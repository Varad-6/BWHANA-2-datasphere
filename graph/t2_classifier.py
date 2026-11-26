"""
T2: Object Classifier & Complexity Scorer
Evaluates object complexity (1-5 scale) and tags objects with their target migration path (Paths 1-7).
"""

class ObjectClassifier:
    def __init__(self, repo_manager):
        self.repo = repo_manager

    def classify_and_score(self):
        """Scores objects in repository and updates migration path tags."""
        objects = self.repo.get_all_objects()
        summary = {"Path 1": 0, "Path 2": 0, "Path 3": 0, "Path 4": 0, "Path 5": 0, "Path 6": 0, "Path 7": 0}

        for obj in objects:
            tech_name = obj["tech_name"]
            obj_type = obj["object_type"]
            meta = obj.get("raw_metadata", {})

            path = "Path 1"
            score = 1

            if obj_type in ["SOURCE_SYSTEM", "DATASOURCE"]:
                path = "Path 1"
                score = 1
            elif obj_type == "INFOOBJECT":
                path = "Path 2"
                num_attrs = len(meta.get("attributes", []))
                num_comp = len(meta.get("compounding", []))
                has_hier = meta.get("has_hierarchies", False)
                score = 1 + (1 if num_attrs > 0 else 0) + (1 if num_comp > 0 else 0) + (2 if has_hier else 0)
                score = min(score, 5)
            elif obj_type == "TRANSFORMATION":
                path = "Path 3"
                num_routines = len(meta.get("routines_abap", []))
                rule_type = meta.get("rule_type", "DIRECT")
                if num_routines > 0:
                    score = 4 if num_routines <= 2 else 5
                elif rule_type == "FORMULA":
                    score = 2
                else:
                    score = 1
            elif obj_type == "ADSO":
                path = "Path 4"
                adso_type = meta.get("adso_type", "STANDARD")
                num_fields = len(meta.get("fields", []))
                score = 2 if adso_type == "STAGING" else (3 if num_fields < 15 else 4)
            elif obj_type == "COMPOSITE_PROVIDER":
                path = "Path 5"
                num_sources = len(meta.get("sources", []))
                score = 2 if num_sources <= 1 else 3
            elif obj_type == "BEX_QUERY":
                path = "Path 6"
                num_vars = len(meta.get("variables", []))
                score = 2 if num_vars <= 2 else 3
            elif obj_type in ["PROCESS_CHAIN", "ANALYSIS_AUTH"]:
                path = "Path 7"
                score = 2

            summary[path] = summary.get(path, 0) + 1

            # Update repository
            self.repo.insert_object(
                tech_name=tech_name,
                object_type=obj_type,
                description=obj["description"],
                complexity_score=score,
                migration_path=path,
                raw_metadata=meta
            )

        return summary
