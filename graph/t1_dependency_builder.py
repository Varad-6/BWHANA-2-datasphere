"""
T1: Dependency Graph Builder
Parses repository metadata into a NetworkX directed graph, detects strongly connected
components (Tarjan's SCC), severs non-fatal back-edges, and derives topological migration waves.
"""

from typing import Any, Dict, List, Tuple
import networkx as nx


class DependencyGraphBuilder:
    """Directed dependency graph and topological wave planner."""

    NON_FATAL_EDGE_TYPES = {"ATTRIBUTE_OF", "COMPOUNDED_WITH"}

    def __init__(self, repo_manager: Any) -> None:
        self.repo = repo_manager
        self.graph = nx.DiGraph()
        self.severed_edges: List[Tuple[str, str, str]] = []

    def build_graph(self) -> nx.DiGraph:
        """Construct directed graph from repository objects and dependencies."""
        self.graph.clear()
        self.severed_edges = []

        for obj in self.repo.get_all_objects():
            self.graph.add_node(
                obj["tech_name"],
                object_type=obj["object_type"],
                migration_path=obj["migration_path"],
                complexity=obj["complexity_score"],
            )

        for src, tgt, dep_type in self.repo.get_all_dependencies():
            if not self.graph.has_node(src):
                self.graph.add_node(src, object_type="EXTERNAL", migration_path="Path 1", complexity=1)
            if not self.graph.has_node(tgt):
                self.graph.add_node(tgt, object_type="EXTERNAL", migration_path="Path 1", complexity=1)
            self.graph.add_edge(src, tgt, type=dep_type)

        return self.graph

    def detect_cycles(self) -> List[List[str]]:
        """Detect Strongly Connected Components with >1 node (Tarjan's SCC) and self-loops."""
        if not self.graph.nodes:
            self.build_graph()
        sccs = [sorted(list(c)) for c in nx.strongly_connected_components(self.graph) if len(c) > 1]
        for node in nx.nodes_with_selfloops(self.graph):
            sccs.append([node])
        return sccs

    def get_topological_waves(self) -> List[Dict[str, Any]]:
        """Generate execution waves based on topological sorting with cycle isolation."""
        if not self.graph.nodes:
            self.build_graph()

        dag = self.graph.copy()
        self.severed_edges = []

        # Break any cycles by severing non-fatal attribute/compounding edges first
        cycles = list(nx.simple_cycles(dag))
        for cycle in cycles:
            if len(cycle) == 1:
                u = cycle[0]
                if dag.has_edge(u, u):
                    etype = dag[u][u].get("type", "UNKNOWN")
                    dag.remove_edge(u, u)
                    self.severed_edges.append((u, u, etype))
                continue

            removed = False
            for i in range(len(cycle)):
                u = cycle[i]
                v = cycle[(i + 1) % len(cycle)]
                if dag.has_edge(u, v) and dag[u][v].get("type") in self.NON_FATAL_EDGE_TYPES:
                    etype = dag[u][v].get("type", "ATTRIBUTE_OF")
                    dag.remove_edge(u, v)
                    self.severed_edges.append((u, v, etype))
                    removed = True
                    break

            if not removed and dag.has_edge(cycle[0], cycle[1]):
                etype = dag[cycle[0]][cycle[1]].get("type", "DATA_FLOW")
                dag.remove_edge(cycle[0], cycle[1])
                self.severed_edges.append((cycle[0], cycle[1], etype))

        try:
            layers = list(nx.topological_generations(dag))
            waves = [
                {
                    "wave_id": idx,
                    "wave_name": f"Wave {idx}",
                    "objects": sorted(layer),
                }
                for idx, layer in enumerate(layers, start=1)
            ]
        except Exception:
            waves = [
                {
                    "wave_id": 1,
                    "wave_name": "Wave 1 (Fallback)",
                    "objects": sorted(list(self.graph.nodes)),
                }
            ]

        if hasattr(self.repo, "save_wave_schedule") and waves:
            self.repo.save_wave_schedule(waves)

        return waves

    def generate_dot_string(self) -> str:
        """Generate Graphviz DOT format representation."""
        if not self.graph.nodes:
            self.build_graph()
        lines = [
            "digraph BW_Migration_Graph {",
            "  rankdir=LR;",
            '  node [shape=box, style=filled, fillcolor="#DDEBF7", fontname="Segoe UI"];',
        ]
        for node, data in self.graph.nodes(data=True):
            path = data.get("migration_path", "")
            lines.append(f'  "{node}" [label="{node}\\n({path})"];')
        for src, tgt, edata in self.graph.edges(data=True):
            etype = edata.get("type", "")
            lines.append(f'  "{src}" -> "{tgt}" [label="{etype}"];')
        lines.append("}")
        return "\n".join(lines)
