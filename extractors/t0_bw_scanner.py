"""
T0: BW Object Inventory Scanner
Connects to BW/4HANA (or loads mock inventory) and populates the shared metadata repository.
"""

import json
from extractors.sample_data import SAMPLE_BW_METADATA

class BWInventoryScanner:
    def __init__(self, repo_manager):
        self.repo = repo_manager

    def scan_sample_metadata(self):
        """Scans the sample system metadata dictionary and loads into repository."""
        data = SAMPLE_BW_METADATA
        counts = {}

        # 1. Source Systems
        for ss in data.get("source_systems", []):
            self.repo.insert_object(
                tech_name=ss["tech_name"],
                object_type="SOURCE_SYSTEM",
                description=ss["description"],
                complexity_score=1,
                migration_path="Path 1",
                raw_metadata=ss
            )
        counts["SOURCE_SYSTEM"] = len(data.get("source_systems", []))

        # 2. DataSources
        for ds in data.get("datasources", []):
            self.repo.insert_object(
                tech_name=ds["tech_name"],
                object_type="DATASOURCE",
                description=ds["description"],
                complexity_score=1,
                migration_path="Path 1",
                raw_metadata=ds
            )
            # Add dependency to source system
            self.repo.insert_dependency(ds["source_system"], ds["tech_name"], "EXTRACTS_FROM")
        counts["DATASOURCE"] = len(data.get("datasources", []))

        # 3. InfoObjects
        for io in data.get("infoobjects", []):
            comp_count = len(io.get("compounding", []))
            attr_count = len(io.get("attributes", []))
            complexity = 1 + comp_count + (1 if attr_count > 0 else 0)
            self.repo.insert_object(
                tech_name=io["tech_name"],
                object_type="INFOOBJECT",
                description=io["description"],
                complexity_score=complexity,
                migration_path="Path 2",
                raw_metadata=io
            )
            # Register attribute dependencies
            for attr in io.get("attributes", []):
                self.repo.insert_dependency(attr, io["tech_name"], "ATTRIBUTE_OF")
        counts["INFOOBJECT"] = len(data.get("infoobjects", []))

        # 4. ADSOs
        for adso in data.get("adsos", []):
            complexity = 2 if adso["adso_type"] == "STAGING" else 3
            self.repo.insert_object(
                tech_name=adso["tech_name"],
                object_type="ADSO",
                description=adso["description"],
                complexity_score=complexity,
                migration_path="Path 4",
                raw_metadata=adso
            )
        counts["ADSO"] = len(data.get("adsos", []))

        # 5. CompositeProviders
        for hcpr in data.get("composite_providers", []):
            self.repo.insert_object(
                tech_name=hcpr["tech_name"],
                object_type="COMPOSITE_PROVIDER",
                description=hcpr["description"],
                complexity_score=3,
                migration_path="Path 5",
                raw_metadata=hcpr
            )
            for src in hcpr.get("sources", []):
                self.repo.insert_dependency(src, hcpr["tech_name"], "PROVIDES_DATA_TO")
        counts["COMPOSITE_PROVIDER"] = len(data.get("composite_providers", []))

        # 6. BEx Queries
        for q in data.get("queries", []):
            self.repo.insert_object(
                tech_name=q["tech_name"],
                object_type="BEX_QUERY",
                description=q["description"],
                complexity_score=2,
                migration_path="Path 6",
                raw_metadata=q
            )
            self.repo.insert_dependency(q["infoprovider"], q["tech_name"], "QUERIED_BY")
        counts["BEX_QUERY"] = len(data.get("queries", []))

        # 7. Transformations
        for tr in data.get("transformations", []):
            has_routines = len(tr.get("routines_abap", [])) > 0
            complexity = 4 if has_routines else 2
            self.repo.insert_object(
                tech_name=tr["tran_id"],
                object_type="TRANSFORMATION",
                description=f"Tran {tr['source_obj']} -> {tr['target_obj']}",
                complexity_score=complexity,
                migration_path="Path 3",
                raw_metadata=tr
            )
            self.repo.insert_transformation(
                tran_id=tr["tran_id"],
                source_obj=tr["source_obj"],
                target_obj=tr["target_obj"],
                rule_type=tr["rule_type"],
                field_mappings=tr.get("field_mappings", []),
                routines_abap=tr.get("routines_abap", [])
            )
            self.repo.insert_dependency(tr["source_obj"], tr["tran_id"], "TRANSFORMED_BY")
            self.repo.insert_dependency(tr["tran_id"], tr["target_obj"], "LOADS_INTO")
        counts["TRANSFORMATION"] = len(data.get("transformations", []))

        # 8. Process Chains
        for pc in data.get("process_chains", []):
            self.repo.insert_object(
                tech_name=pc["tech_name"],
                object_type="PROCESS_CHAIN",
                description=pc["description"],
                complexity_score=2,
                migration_path="Path 7",
                raw_metadata=pc
            )
        counts["PROCESS_CHAIN"] = len(data.get("process_chains", []))

        return counts
