"""T2 Object Classifier & Complexity Scorer Router."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends

from api.dependencies import get_db
from graph.t2_classifier import ObjectClassifier
from repository.db_manager import RepositoryManager

router = APIRouter(prefix="/classify", tags=["T2: Classifier"])


@router.get("/run")
def run_classification(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Run T2 heuristic classifier and complexity scorer across all repository objects."""
    db.set_phase_status("T2", "RUNNING")
    try:
        classifier = ObjectClassifier(db)
        path_summary = classifier.classify_and_score()
        stats = db.get_stats()
        summary = {
            "path_summary": path_summary,
            "avg_complexity": stats["avg_complexity"],
            "total_classified": stats["total_objects"],
        }
        db.set_phase_status("T2", "COMPLETED", summary=summary)
        return {"phase": "T2", "status": "completed", **summary}
    except Exception as exc:
        db.set_phase_status("T2", "ERROR", summary={"error": str(exc)})
        raise


@router.get("/summary")
def get_classification_summary(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Return current path breakdown and complexity stats."""
    stats = db.get_stats()
    return {
        "total_objects": stats["total_objects"],
        "avg_complexity": stats["avg_complexity"],
        "by_path": stats["by_path"],
        "by_type": stats["by_type"],
    }


@router.get("/by-path/{path_id}")
def get_objects_by_path(
    path_id: int,
    db: RepositoryManager = Depends(get_db),
) -> Dict[str, Any]:
    """Return all objects tagged with 'Path <path_id>'."""
    path_label = f"Path {path_id}"
    objs: List[Dict[str, Any]] = db.get_objects_by_path(path_label)
    return {"migration_path": path_label, "count": len(objs), "items": objs}


@router.get("/status")
def get_classify_status(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Return persisted T2 phase status."""
    phase = db.get_phase_status("T2")
    return {"phase": "T2", "status": phase["status"].lower(), "summary": phase["summary"], "updated_at": phase["updated_at"]}


@router.get("/assess/{tech_name}")
def assess_object_compatibility(
    tech_name: str,
    db: RepositoryManager = Depends(get_db),
) -> Dict[str, Any]:
    """Assess SAP Datasphere compatibility, risks, and recommended migration approach for an object."""
    from fastapi import HTTPException

    obj = db.get_object(tech_name)
    if not obj:
        raise HTTPException(status_code=404, detail=f"Object '{tech_name}' not found")

    obj_type = obj["object_type"]
    path = obj.get("migration_path") or "Path 1"
    score = obj.get("complexity_score") or 1
    meta = obj.get("raw_metadata", {})

    approach_map = {
        "Path 1": ("Datasphere Space Connection / @cds.external Remote Table", "Replicate or federate via Cloud Connector / OData"),
        "Path 2": ("Datasphere Local Table (#DIMENSION + #TEXT)", "Map natural business keys, composite compounding keys & associations"),
        "Path 3": ("Datasphere Pure SQL View (#CUBE) / Data Flow", "Transpile Direct/Formula/Simple ABAP to SELECT; route complex ABAP to Data Flow"),
        "Path 4": ("Datasphere Local Table (#FACT / #STAGING + _CHANGELOG)", "Map Active (*2) to #FACT, Inbound (*1) to #STAGING"),
        "Path 5": ("Datasphere Analytical View / Relational Join Model", "Convert Union/Join tree to SQL UNION ALL / LEFT OUTER JOIN"),
        "Path 6": ("Datasphere Analytic Model + Input Parameters", "Convert RKF/CKF to Restricted/Calculated Measures"),
        "Path 7": ("Datasphere Task Chain / Data Access Control (DAC)", "Convert Process Chain steps to Task Chain dependsOn sequence"),
    }
    recommended_target, migration_approach = approach_map.get(path, ("Datasphere Local Table", "Standard CSN conversion"))

    risks: List[str] = []
    if meta.get("compounding"):
        risks.append(f"Compounding keys detected ({', '.join(meta['compounding'])}) — must enforce composite primary key.")
    if meta.get("routines_abap"):
        risks.append(f"{len(meta['routines_abap'])} ABAP routine(s) detected — verify SQL transpilation or Data Flow fallback.")
    if obj.get("warning_code"):
        risks.append(f"Flagged warning: {obj['warning_code']}")
    if len(meta.get("fields", [])) >= 15:
        risks.append("Wide schema (>=15 fields) — verify column types and lengths in Map stage.")

    return {
        "tech_name": tech_name,
        "object_type": obj_type,
        "migration_path": path,
        "complexity_score": score,
        "compatible": True,
        "recommended_target": recommended_target,
        "migration_approach": migration_approach,
        "risks": risks,
    }
