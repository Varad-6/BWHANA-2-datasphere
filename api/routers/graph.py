"""T1 Dependency Graph & Wave Planner Router."""

from typing import Any, Dict
from fastapi import APIRouter, Depends

from api.dependencies import get_db
from graph.t1_dependency_builder import DependencyGraphBuilder
from repository.db_manager import RepositoryManager

router = APIRouter(prefix="/graph", tags=["T1: Dependency Graph"])


@router.get("/build")
def build_dependency_graph(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Build NetworkX DiGraph, isolate cycles, and compute topological waves."""
    db.set_phase_status("T1", "RUNNING")
    try:
        builder = DependencyGraphBuilder(db)
        graph = builder.build_graph()
        cycles = builder.detect_cycles()
        waves = builder.get_topological_waves()

        summary = {
            "nodes_count": graph.number_of_nodes(),
            "edges_count": graph.number_of_edges(),
            "waves_count": len(waves),
            "cycles_detected": len(cycles),
            "severed_edges_count": len(builder.severed_edges),
        }
        db.set_phase_status("T1", "COMPLETED", summary=summary)
        return {
            "phase": "T1",
            "status": "completed",
            **summary,
            "waves": waves,
            "cycles": cycles,
            "severed_edges": [
                {"source": s, "target": t, "type": tp} for s, t, tp in builder.severed_edges
            ],
        }
    except Exception as exc:
        db.set_phase_status("T1", "ERROR", summary={"error": str(exc)})
        raise


@router.get("/waves")
def get_waves(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Return ordered topological wave batches."""
    builder = DependencyGraphBuilder(db)
    builder.build_graph()
    waves = builder.get_topological_waves()
    return {"waves_count": len(waves), "waves": waves}


@router.get("/cycles")
def get_cycles(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Return any strongly connected components / cycles detected."""
    builder = DependencyGraphBuilder(db)
    builder.build_graph()
    cycles = builder.detect_cycles()
    return {"cycles_count": len(cycles), "cycles": cycles}


@router.get("/dot")
def get_dot_graph(db: RepositoryManager = Depends(get_db)) -> Dict[str, str]:
    """Return Graphviz DOT representation of the dependency graph."""
    builder = DependencyGraphBuilder(db)
    builder.build_graph()
    return {"dot": builder.generate_dot_string()}


@router.get("/status")
def get_graph_status(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Return persisted T1 phase status."""
    phase = db.get_phase_status("T1")
    return {"phase": "T1", "status": phase["status"].lower(), "summary": phase["summary"], "updated_at": phase["updated_at"]}


@router.get("/lineage/{tech_name}")
def get_object_lineage(
    tech_name: str,
    db: RepositoryManager = Depends(get_db),
) -> Dict[str, Any]:
    """Return upstream and downstream lineage, wave assignment, and cycle status for an object."""
    builder = DependencyGraphBuilder(db)
    graph = builder.build_graph()
    cycles = builder.detect_cycles()
    waves = builder.get_topological_waves()

    wave_id = None
    for w in waves:
        if tech_name in w["objects"]:
            wave_id = w["wave_id"]
            break

    if not graph.has_node(tech_name):
        return {
            "tech_name": tech_name,
            "wave_id": wave_id,
            "in_cycle": False,
            "upstream": [],
            "downstream": [],
        }

    upstream = [
        {"tech_name": u, "relationship": graph[u][tech_name].get("type", "DATA_FLOW")}
        for u in graph.predecessors(tech_name)
    ]
    downstream = [
        {"tech_name": v, "relationship": graph[tech_name][v].get("type", "DATA_FLOW")}
        for v in graph.successors(tech_name)
    ]
    in_cycle = any(tech_name in c for c in cycles)

    return {
        "tech_name": tech_name,
        "wave_id": wave_id,
        "in_cycle": in_cycle,
        "upstream": upstream,
        "downstream": downstream,
    }
