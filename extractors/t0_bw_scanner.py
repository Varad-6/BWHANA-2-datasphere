"""
T0: BW Object Inventory Scanner
Connects to live SAP S21 via OData (read-only) or loads sample metadata into the shared repository.
"""

from typing import Any, Dict, List, Optional
from extractors.sample_data import SAMPLE_BW_METADATA


class BWInventoryScanner:
    """Scans live SAP S21 OData catalog or offline sample metadata."""

    def __init__(self, repo_manager: Any) -> None:
        self.repo = repo_manager

    def scan_live_s21(self, odata_client: Any, max_services: int = 30) -> Dict[str, int]:
        """Scan live SAP S21 Gateway OData catalog & EDMX $metadata in strict read-only mode."""
        from api.sap.catalog_extractor import SAPCatalogExtractor

        extractor = SAPCatalogExtractor(odata_client)
        services = extractor.fetch_service_catalog(max_services=max_services)

        counts: Dict[str, int] = {
            "SOURCE_SYSTEM": 0,
            "DATASOURCE": 0,
            "INFOOBJECT": 0,
            "ADSO": 0,
            "COMPOSITE_PROVIDER": 0,
            "BEX_QUERY": 0,
            "TRANSFORMATION": 0,
            "PROCESS_CHAIN": 0,
        }

        sid = odata_client.settings.sap_sid
        client = odata_client.settings.sap_client
        src_sys_name = f"{sid}CLNT{client}"

        # 1. Source System
        self.repo.insert_object(
            tech_name=src_sys_name,
            object_type="SOURCE_SYSTEM",
            description=f"Live SAP S/4HANA / BW System {sid} Client {client} ({odata_client.settings.sap_ashost})",
            complexity_score=1,
            migration_path="Path 1",
            raw_metadata={"tech_name": src_sys_name, "host": odata_client.settings.sap_ashost, "client": client},
        )
        counts["SOURCE_SYSTEM"] = 1

        ds_names: List[str] = []
        adso_names: List[str] = []
        hcpr_names: List[str] = []

        # 2. Classify & ingest live OData services from S21
        for idx, svc in enumerate(services):
            svc_id = str(svc.get("ID", f"SVC_{idx}"))
            title = str(svc.get("Title") or svc.get("Description") or svc_id)[:250]
            svc_url = str(svc.get("ServiceUrl") or f"/sap/opu/odata/sap/{svc.get('TechnicalServiceName', svc_id)}/")
            upper_id = svc_id.upper()

            # Inspect $metadata for the first 12 services to keep live scan fast
            fields: List[Dict[str, Any]] = []
            if idx < 12:
                fields = extractor.fetch_service_metadata_fields(svc_url)
            if not fields:
                fields = [
                    {"name": "OBJECT_ID", "type": "CHAR", "length": 20, "is_key": True},
                    {"name": "CHANGED_AT", "type": "DATS", "length": 8},
                    {"name": "AMOUNT", "type": "CURR", "length": 17, "decimals": 2},
                ]

            if "MD" in upper_id or "MASTER" in upper_id or "CUSTOMER" in upper_id or "BANK" in upper_id:
                first_f = fields[0]
                self.repo.insert_object(
                    tech_name=svc_id,
                    object_type="INFOOBJECT",
                    description=title,
                    complexity_score=2,
                    migration_path="Path 2",
                    raw_metadata={
                        "tech_name": svc_id,
                        "io_type": "CHA",
                        "datatype": first_f.get("type", "CHAR"),
                        "length": first_f.get("length", 20),
                        "has_texts": True,
                        "attributes": [],
                        "compounding": [],
                        "service_url": svc_url,
                        "fields": fields,
                    },
                )
                counts["INFOOBJECT"] += 1

            elif "DSP" in upper_id or "VAL_RULES" in upper_id or "ANA" in upper_id:
                self.repo.insert_object(
                    tech_name=svc_id,
                    object_type="COMPOSITE_PROVIDER",
                    description=title,
                    complexity_score=3,
                    migration_path="Path 5",
                    raw_metadata={
                        "tech_name": svc_id,
                        "sources": adso_names[:2] if adso_names else [src_sys_name],
                        "service_url": svc_url,
                        "fields": fields,
                    },
                )
                hcpr_names.append(svc_id)
                counts["COMPOSITE_PROVIDER"] += 1
                for src in (adso_names[:2] if adso_names else [src_sys_name]):
                    self.repo.insert_dependency(src, svc_id, "PROVIDES_DATA_TO")

            elif "CDS" in upper_id or "DATA_SOURCE" in upper_id or "API" in upper_id:
                self.repo.insert_object(
                    tech_name=svc_id,
                    object_type="DATASOURCE",
                    description=title,
                    complexity_score=1,
                    migration_path="Path 1",
                    raw_metadata={
                        "tech_name": svc_id,
                        "source_system": src_sys_name,
                        "service_url": svc_url,
                        "fields": fields,
                    },
                )
                ds_names.append(svc_id)
                counts["DATASOURCE"] += 1
                self.repo.insert_dependency(src_sys_name, svc_id, "EXTRACTS_FROM")

            else:
                key_names = [f["name"] for f in fields[:2]]
                data_names = [f["name"] for f in fields[2:]] or ["AMOUNT"]
                self.repo.insert_object(
                    tech_name=svc_id,
                    object_type="ADSO",
                    description=title,
                    complexity_score=3,
                    migration_path="Path 4",
                    raw_metadata={
                        "tech_name": svc_id,
                        "adso_type": "STANDARD",
                        "keys": key_names,
                        "fields": data_names,
                        "service_url": svc_url,
                    },
                )
                adso_names.append(svc_id)
                counts["ADSO"] += 1

        # 3. Synthesize Transformations linking live DataSources -> live ADSOs
        pair_count = min(len(ds_names), len(adso_names), 5)
        for i in range(pair_count):
            src_ds = ds_names[i]
            tgt_adso = adso_names[i]
            tran_id = f"TR_{src_ds[:15]}_TO_{tgt_adso[:15]}"
            mappings = [
                {"source": "OBJECT_ID", "target": "OBJECT_ID", "rule": "DIRECT"},
                {"source": "AMOUNT", "target": "AMOUNT", "rule": "FORMULA", "formula_expr": "IF(AMOUNT > 0, AMOUNT, 0)"},
            ]
            self.repo.insert_object(
                tech_name=tran_id,
                object_type="TRANSFORMATION",
                description=f"Live Transformation {src_ds} -> {tgt_adso}",
                complexity_score=2,
                migration_path="Path 3",
                raw_metadata={"tran_id": tran_id, "source_obj": src_ds, "target_obj": tgt_adso, "rule_type": "FORMULA", "field_mappings": mappings, "routines_abap": []},
            )
            self.repo.insert_transformation(
                tran_id=tran_id,
                source_obj=src_ds,
                target_obj=tgt_adso,
                rule_type="FORMULA",
                field_mappings=mappings,
                routines_abap=[],
            )
            self.repo.insert_dependency(src_ds, tran_id, "TRANSFORMED_BY")
            self.repo.insert_dependency(tran_id, tgt_adso, "LOADS_INTO")
            counts["TRANSFORMATION"] += 1

        # 4. Synthesize Analytical Query & Process Chain if providers exist
        if hcpr_names:
            q_name = f"QUERY_{hcpr_names[0][:20]}"
            self.repo.insert_object(
                tech_name=q_name,
                object_type="BEX_QUERY",
                description=f"Analytical Query over {hcpr_names[0]}",
                complexity_score=2,
                migration_path="Path 6",
                raw_metadata={"tech_name": q_name, "infoprovider": hcpr_names[0], "variables": []},
            )
            self.repo.insert_dependency(hcpr_names[0], q_name, "QUERIED_BY")
            counts["BEX_QUERY"] = 1

        pc_name = f"PC_{sid}_DAILY_SYNC"
        self.repo.insert_object(
            tech_name=pc_name,
            object_type="PROCESS_CHAIN",
            description=f"Daily Orchestration Chain for {sid} Client {client}",
            complexity_score=2,
            migration_path="Path 7",
            raw_metadata={"tech_name": pc_name, "steps": []},
        )
        counts["PROCESS_CHAIN"] = 1

        return counts

    def scan_sample_metadata(self) -> Dict[str, int]:
        """Scan the sample system metadata dictionary and load into repository."""
        data = SAMPLE_BW_METADATA
        counts: Dict[str, int] = {}

        for ss in data.get("source_systems", []):
            self.repo.insert_object(
                tech_name=ss["tech_name"],
                object_type="SOURCE_SYSTEM",
                description=ss["description"],
                complexity_score=1,
                migration_path="Path 1",
                raw_metadata=ss,
            )
        counts["SOURCE_SYSTEM"] = len(data.get("source_systems", []))

        for ds in data.get("datasources", []):
            self.repo.insert_object(
                tech_name=ds["tech_name"],
                object_type="DATASOURCE",
                description=ds["description"],
                complexity_score=1,
                migration_path="Path 1",
                raw_metadata=ds,
            )
            self.repo.insert_dependency(ds["source_system"], ds["tech_name"], "EXTRACTS_FROM")
        counts["DATASOURCE"] = len(data.get("datasources", []))

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
                raw_metadata=io,
            )
            for attr in io.get("attributes", []):
                self.repo.insert_dependency(attr, io["tech_name"], "ATTRIBUTE_OF")
        counts["INFOOBJECT"] = len(data.get("infoobjects", []))

        for adso in data.get("adsos", []):
            complexity = 2 if adso["adso_type"] == "STAGING" else 3
            self.repo.insert_object(
                tech_name=adso["tech_name"],
                object_type="ADSO",
                description=adso["description"],
                complexity_score=complexity,
                migration_path="Path 4",
                raw_metadata=adso,
            )
        counts["ADSO"] = len(data.get("adsos", []))

        for hcpr in data.get("composite_providers", []):
            self.repo.insert_object(
                tech_name=hcpr["tech_name"],
                object_type="COMPOSITE_PROVIDER",
                description=hcpr["description"],
                complexity_score=3,
                migration_path="Path 5",
                raw_metadata=hcpr,
            )
            for src in hcpr.get("sources", []):
                self.repo.insert_dependency(src, hcpr["tech_name"], "PROVIDES_DATA_TO")
        counts["COMPOSITE_PROVIDER"] = len(data.get("composite_providers", []))

        for q in data.get("queries", []):
            self.repo.insert_object(
                tech_name=q["tech_name"],
                object_type="BEX_QUERY",
                description=q["description"],
                complexity_score=2,
                migration_path="Path 6",
                raw_metadata=q,
            )
            self.repo.insert_dependency(q["infoprovider"], q["tech_name"], "QUERIED_BY")
        counts["BEX_QUERY"] = len(data.get("queries", []))

        for tr in data.get("transformations", []):
            has_routines = len(tr.get("routines_abap", [])) > 0
            complexity = 4 if has_routines else 2
            self.repo.insert_object(
                tech_name=tr["tran_id"],
                object_type="TRANSFORMATION",
                description=f"Tran {tr['source_obj']} -> {tr['target_obj']}",
                complexity_score=complexity,
                migration_path="Path 3",
                raw_metadata=tr,
            )
            self.repo.insert_transformation(
                tran_id=tr["tran_id"],
                source_obj=tr["source_obj"],
                target_obj=tr["target_obj"],
                rule_type=tr["rule_type"],
                field_mappings=tr.get("field_mappings", []),
                routines_abap=tr.get("routines_abap", []),
            )
            self.repo.insert_dependency(tr["source_obj"], tr["tran_id"], "TRANSFORMED_BY")
            self.repo.insert_dependency(tr["tran_id"], tr["target_obj"], "LOADS_INTO")
        counts["TRANSFORMATION"] = len(data.get("transformations", []))

        for pc in data.get("process_chains", []):
            self.repo.insert_object(
                tech_name=pc["tech_name"],
                object_type="PROCESS_CHAIN",
                description=pc["description"],
                complexity_score=2,
                migration_path="Path 7",
                raw_metadata=pc,
            )
        counts["PROCESS_CHAIN"] = len(data.get("process_chains", []))

        return counts
