"""
T1: Dependency Graph Builder
Parses repository metadata into a NetworkX directed graph to derive optimal migration sequence.
"""

import networkx as nx

class DependencyGraphBuilder:
    def __init__(self, repo_manager):
        self.repo = repo_manager
        self.graph = nx.DiGraph()

    def build_graph(self):
        """Constructs directed graph from repo dependencies and objects."""
        self.graph.clear()
        objects = self.repo.get_all_objects()
        for obj in objects:
            self.graph.add_node(
                obj["tech_name"],
                object_type=obj["object_type"],
                migration_path=obj["migration_path"],
                complexity=obj["complexity_score"]
            )

        deps = self.repo.get_all_dependencies()
        for src, tgt, dep_type in deps:
            self.graph.add_edge(src, tgt, type=dep_type)

        return self.graph

    def get_topological_waves(self):
        """Generates execution waves based on topological sorting."""
        if not self.graph.nodes:
            self.build_graph()

        try:
            # Check for cycles
            cycles = list(nx.simple_cycles(self.graph))
            if cycles:
                print(f"[Warning] Cycles detected in graph: {cycles}")
                # Return nodes grouped by layer ignoring back-edges
                dag = self.graph.copy()
                for c in cycles:
                    dag.remove_edge(c[0], c[1])
                layers = list(nx.topological_generations(dag))
            else:
                layers = list(nx.topological_generations(self.graph))

            waves = []
            for idx, layer in enumerate(layers, start=1):
                waves.append({
                    "wave_id": idx,
                    "wave_name": f"Wave {idx}",
                    "objects": layer
                })
            return waves
        except Exception as e:
            print(f"[Error] Topological sort failed: {e}")
            return [{"wave_id": 1, "wave_name": "Wave 1 (Fallback)", "objects": list(self.graph.nodes)}]

    def generate_dot_string(self):
        """Generates Graphviz DOT format representation."""
        lines = ["digraph BW_Migration_Graph {", "  rankdir=LR;", "  node [shape=box, style=filled, fillcolor=lightgray];"]
        for node, data in self.graph.nodes(data=True):
            path = data.get("migration_path", "")
            lines.append(f'  "{node}" [label="{node}\\n({path})"];')
        for src, tgt in self.graph.edges():
            lines.append(f'  "{src}" -> "{tgt}";')
        lines.append("}")
        return "\n".join(lines)
