"""F2 CSN Generators Router (Paths 2, 3, 4) + Custom Editable CSN/SQL Compiler."""

import json
import os
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.dependencies import get_db
from generators.base_generator import BaseCSNGenerator
from generators.t5_master_data import MasterDataMigrator
from generators.t6_transformation import TransformationTranslator
from generators.t7_adso import ADSODataMigrator
from repository.db_manager import RepositoryManager

router = APIRouter(prefix="/generate", tags=["T5-T7: CSN Generators"])


class EditableColumn(BaseModel):
    include: bool = True
    source_field: str
    target_column: str
    csn_type: str = "cds.String"
    length: int = 30
    scale: int = 0
    is_key: bool = False
    label: str = ""


class CompileCustomRequest(BaseModel):
    space_name: str = ""
    target_name: str
    source_name: str = ""
    description: str = ""
    analytics_category: str = "#DIMENSION"
    include_text_entity: bool = False
    include_changelog_entity: bool = False
    sql_where: str = ""
    columns: List[EditableColumn]


def _save_csn_output(filename: str, payload: Any) -> str:
    os.makedirs("output", exist_ok=True)
    path = os.path.join("output", filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path


@router.get("/path2")
def generate_path2_infoobjects(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Generate CSN v1.0 document for all Path 2 (InfoObject) objects."""
    db.set_phase_status("T5", "RUNNING")
    try:
        migrator = MasterDataMigrator(db)
        csn = migrator.convert_all_path2_objects()
        out_path = _save_csn_output("path2_infoobjects_csn.json", csn)
        summary = {"entities_count": len(csn.get("definitions", {})), "output_file": out_path}
        db.set_phase_status("T5", "COMPLETED", summary=summary)
        return {"phase": "T5", "status": "completed", **summary, "csn": csn}
    except Exception as exc:
        db.set_phase_status("T5", "ERROR", summary={"error": str(exc)})
        raise


@router.get("/path3")
def generate_path3_transformations(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Transpile all Path 3 Transformations and ABAP routines to Datasphere SQL Views."""
    db.set_phase_status("T6", "RUNNING")
    try:
        translator = TransformationTranslator(db)
        tr_objs = db.get_objects_by_path("Path 3")
        results: List[Dict[str, Any]] = []
        warnings_total = 0
        for tr in tr_objs:
            res = translator.translate_transformation(tr["tech_name"])
            warnings_total += len(res["warnings"])
            results.append({"tran_id": tr["tech_name"], **res})

        out_path = _save_csn_output("path3_transformations_csn.json", [r["csn"] for r in results])
        summary = {
            "transformations_count": len(results),
            "warnings_count": warnings_total,
            "output_file": out_path,
        }
        db.set_phase_status("T6", "COMPLETED", summary=summary)
        return {"phase": "T6", "status": "completed", **summary, "results": results}
    except Exception as exc:
        db.set_phase_status("T6", "ERROR", summary={"error": str(exc)})
        raise


@router.get("/path4")
def generate_path4_adsos(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Generate CSN Local Table definitions for all Path 4 (ADSO) objects."""
    db.set_phase_status("T7", "RUNNING")
    try:
        migrator = ADSODataMigrator(db)
        adso_objs = db.get_objects_by_path("Path 4")
        csns = [migrator.convert_adso(a["tech_name"]) for a in adso_objs]
        out_path = _save_csn_output("path4_adsos_csn.json", csns)
        summary = {"adsos_count": len(csns), "output_file": out_path}
        db.set_phase_status("T7", "COMPLETED", summary=summary)
        return {"phase": "T7", "status": "completed", **summary, "csns": csns}
    except Exception as exc:
        db.set_phase_status("T7", "ERROR", summary={"error": str(exc)})
        raise


@router.get("/object/{tech_name}")
def generate_single_object(
    tech_name: str,
    db: RepositoryManager = Depends(get_db),
) -> Dict[str, Any]:
    """Generate CSN / SQL / Task Chain artifact for any BW object (Paths 1-7)."""
    obj = db.get_object(tech_name)
    if not obj:
        raise HTTPException(status_code=404, detail=f"Object '{tech_name}' not found")

    path = obj.get("migration_path")
    meta = obj.get("raw_metadata", {})
    base = BaseCSNGenerator(space_name="")

    if path == "Path 2":
        return {"tech_name": tech_name, "csn": MasterDataMigrator(db).convert_infoobject(tech_name)}
    if path == "Path 3":
        return {"tech_name": tech_name, **TransformationTranslator(db).translate_transformation(tech_name)}
    if path == "Path 4":
        return {"tech_name": tech_name, "csn": ADSODataMigrator(db).convert_adso(tech_name)}

    if path == "Path 1":
        elements = {
            f.get("name", "ID"): {
                **base.map_bw_datatype_to_csn(f.get("type", "CHAR"), f.get("length", 30)),
                **({"key": True} if f.get("is_key") else {}),
            }
            for f in meta.get("fields", [{"name": "OBJECT_ID", "type": "CHAR", "length": 20, "is_key": True}])
        }
        csn = base.create_csn_document({
            tech_name: {
                "kind": "entity",
                "@cds.external": True,
                "@EndUserText.label": obj.get("description", tech_name),
                "elements": elements,
            }
        })
        db.update_status(tech_name, "GENERATED")
        return {"tech_name": tech_name, "csn": csn}

    if path == "Path 5":
        sources = meta.get("sources", ["ADSO_SOURCE"])
        sql = f'SELECT *\nFROM "{sources[0]}"'
        csn = base.create_csn_document({
            tech_name: {
                "kind": "entity",
                "@EndUserText.label": obj.get("description", tech_name),
                "@Analytics.dataCategory": "#CUBE",
                "elements": {"OBJECT_ID": {"key": True, "type": "cds.String", "length": 30}},
                "query": sql,
            }
        })
        db.update_status(tech_name, "GENERATED")
        return {"tech_name": tech_name, "csn": csn, "sql": sql}

    if path == "Path 6":
        provider = meta.get("infoprovider", "HCPR_SOURCE")
        csn = base.create_csn_document({
            tech_name: {
                "kind": "entity",
                "@EndUserText.label": obj.get("description", tech_name),
                "@Analytics.dataCategory": "#CUBE",
                "query": f'SELECT *\nFROM "{provider}"',
            }
        })
        db.update_status(tech_name, "GENERATED")
        return {"tech_name": tech_name, "csn": csn}

    if path == "Path 7":
        task_chain = {
            "name": tech_name,
            "description": obj.get("description", tech_name),
            "tasks": meta.get("steps", [{"step_id": 1, "task_type": "DATA_FLOW", "task_name": f"RUN_{tech_name}"}]),
        }
        db.update_status(tech_name, "GENERATED")
        return {"tech_name": tech_name, "csn": task_chain}

    raise HTTPException(status_code=400, detail=f"Unsupported migration path '{path}' for {tech_name}")


class ValidateArtifactRequest(BaseModel):
    tech_name: str
    csn: Dict[str, Any]
    sql: str = ""


class DeliverArtifactRequest(BaseModel):
    tech_name: str
    target_name: str
    csn: Dict[str, Any]
    sql: str = ""


@router.post("/validate")
def validate_generated_artifact(req: ValidateArtifactRequest) -> Dict[str, Any]:
    """Validate CSN v1.0 schema, namespace safety, SID suppression, primary keys, and SQL readiness."""
    checks: List[Dict[str, Any]] = []
    csn = req.csn or {}
    defs = csn.get("definitions", {})

    has_schema = csn.get("$schema") == "https://sap.com/csn/v1"
    checks.append({
        "name": "SAP CSN v1.0 Envelope",
        "passed": has_schema and bool(defs),
        "message": "Valid $schema and non-empty definitions." if (has_schema and defs) else "Missing $schema or definitions.",
    })

    sap_ns_bad = [k for k in defs.keys() if k.upper().startswith("SAP_")]
    checks.append({
        "name": "No Reserved SAP_* Namespace",
        "passed": len(sap_ns_bad) == 0,
        "message": "Clean Active Space naming." if not sap_ns_bad else f"Blocked reserved namespace: {sap_ns_bad}",
    })

    sid_hits: List[str] = []
    missing_pk: List[str] = []
    for ent_name, ent in defs.items():
        elems = ent.get("elements", {})
        for fname in elems.keys():
            if BaseCSNGenerator.is_sid_field(fname):
                sid_hits.append(f"{ent_name}.{fname}")
        cat = ent.get("@Analytics.dataCategory", "")
        if cat in ("#DIMENSION", "#FACT") and elems:
            if not any(isinstance(v, dict) and v.get("key") is True for v in elems.values()):
                missing_pk.append(ent_name)

    checks.append({
        "name": "Zero Surrogate SID Propagation",
        "passed": len(sid_hits) == 0,
        "message": "Natural business keys only." if not sid_hits else f"SID fields found: {sid_hits}",
    })
    checks.append({
        "name": "Primary Key Integrity",
        "passed": len(missing_pk) == 0,
        "message": "All Dimension/Fact entities define primary keys." if not missing_pk else f"Missing key in: {missing_pk}",
    })

    manual_rework = "MANUAL REWORK REQUIRED" in (req.sql or "")
    checks.append({
        "name": "SQL & ABAP Readiness",
        "passed": not manual_rework,
        "message": "Clean Pure SQL View." if not manual_rework else "Contains /* MANUAL REWORK REQUIRED */ block needing review.",
    })

    all_passed = all(c["passed"] for c in checks)
    return {"valid": all_passed, "checks": checks}


@router.post("/deliver")
def deliver_generated_artifact(
    req: DeliverArtifactRequest,
    db: RepositoryManager = Depends(get_db),
) -> Dict[str, Any]:
    """Save validated CSN & SQL artifacts to output/ and mark object VALIDATED in repository."""
    csn_file = _save_csn_output(f"{req.target_name}.csn.json", req.csn)
    sql_file = ""
    if req.sql.strip():
        os.makedirs("output", exist_ok=True)
        sql_file = os.path.join("output", f"{req.target_name}.sql")
        with open(sql_file, "w", encoding="utf-8") as f:
            f.write(req.sql)

    if db.get_object(req.tech_name):
        db.update_status(req.tech_name, "VALIDATED")

    return {
        "status": "delivered",
        "tech_name": req.tech_name,
        "repo_status": "VALIDATED",
        "csn_file": csn_file,
        "sql_file": sql_file,
    }


@router.post("/compile")
def compile_custom_csn(req: CompileCustomRequest) -> Dict[str, Any]:
    """Compile user-edited columns, naming, and SQL into SAP CSN v1.0 JSON + Pure SQL View."""
    try:
        base = BaseCSNGenerator(space_name=req.space_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    elements: Dict[str, Any] = {}
    select_cols: List[str] = []
    sid_warnings: List[str] = []

    for col in req.columns:
        if not col.include or not col.target_column.strip():
            continue
        tgt = col.target_column.strip()
        src = col.source_field.strip() or tgt
        if base.is_sid_field(tgt) or base.is_sid_field(src):
            sid_warnings.append(f"Suppressed BW surrogate SID field '{src}' per Datasphere natural-key policy.")
            continue

        elem_def: Dict[str, Any] = {"type": col.csn_type}
        if col.is_key:
            elem_def["key"] = True
        if col.csn_type == "cds.String":
            elem_def["length"] = col.length if col.length > 0 else 30
        elif col.csn_type == "cds.Decimal":
            elem_def["precision"] = col.length if col.length > 0 else 17
            elem_def["scale"] = col.scale
        elem_def["@EndUserText.label"] = col.label or tgt

        elements[tgt] = elem_def
        if src == tgt:
            select_cols.append(f'    "{src}"')
        else:
            select_cols.append(f'    "{src}" AS "{tgt}"')

    entity_fqn = base.qualify_name(req.target_name)
    definitions: Dict[str, Any] = {
        entity_fqn: {
            "kind": "entity",
            "@EndUserText.label": req.description or req.target_name,
            "@Analytics.dataCategory": req.analytics_category,
            "elements": elements,
        }
    }

    if req.include_text_entity:
        definitions[base.qualify_name(f"{req.target_name}_TEXT")] = {
            "kind": "entity",
            "@EndUserText.label": f"Text for {req.description or req.target_name}",
            "@Analytics.dataCategory": "#TEXT",
            "elements": {
                req.target_name: {"key": True, "type": "cds.String", "length": 30},
                "LANGUAGE_CODE": {"key": True, "type": "cds.String", "length": 2},
                "TXTSH": {"type": "cds.String", "length": 20},
                "TXTMD": {"type": "cds.String", "length": 60},
                "TXTLG": {"type": "cds.String", "length": 100},
            },
        }

    if req.include_changelog_entity:
        cl_elems = dict(elements)
        cl_elems["RECORDMODE"] = {"type": "cds.String", "length": 1, "@EndUserText.label": "BW Delta Record Mode"}
        definitions[base.qualify_name(f"{req.target_name}_CHANGELOG")] = {
            "kind": "entity",
            "@EndUserText.label": f"Change Log Audit for {req.description or req.target_name}",
            "elements": cl_elems,
        }

    source_ref = req.source_name.strip() or req.target_name
    from_target = f'"{base.space_name}"."{source_ref}"' if base.space_name else f'"{source_ref}"'
    sql_lines = ["SELECT", ",\n".join(select_cols) if select_cols else "    *", f"FROM {from_target}"]
    if req.sql_where.strip():
        where_clause = req.sql_where.strip()
        if not where_clause.upper().startswith("WHERE"):
            where_clause = f"WHERE {where_clause}"
        sql_lines.append(where_clause)
    pure_sql = "\n".join(sql_lines)

    if req.analytics_category == "#CUBE":
        definitions[entity_fqn]["query"] = pure_sql

    csn_doc = base.create_csn_document(definitions)
    return {
        "status": "valid",
        "csn": csn_doc,
        "sql": pure_sql,
        "warnings": sid_warnings,
    }


@router.get("/status")
def get_generator_status(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Return persisted T5, T6, T7 generator phase statuses."""
    return {
        "T5": db.get_phase_status("T5"),
        "T6": db.get_phase_status("T6"),
        "T7": db.get_phase_status("T7"),
    }
