"""Unit tests for Phases 2-6: Read-Only Guardrail, SID Suppression, SCC Cycles, ABAP Flagging."""

import pytest
from api.config import Settings
from api.sap.odata_client import SAPODataClient, SAPReadOnlyViolationError
from generators.base_generator import BaseCSNGenerator
from generators.t6_transformation import TransformationTranslator
from graph.t1_dependency_builder import DependencyGraphBuilder
from repository.db_manager import RepositoryManager


@pytest.fixture
def repo(tmp_path):
    mgr = RepositoryManager(db_path=str(tmp_path / "test_p2_6.db"), use_duckdb=False)
    yield mgr
    mgr.close()


def test_odata_client_blocks_mutating_verbs():
    settings = Settings()
    client = SAPODataClient(settings)
    for verb in ("POST", "PUT", "PATCH", "DELETE"):
        with pytest.raises(SAPReadOnlyViolationError):
            client.request(verb, "/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/")


def test_sid_suppression_in_base_generator():
    assert BaseCSNGenerator.is_sid_field("/BI0/S0CUSTOMER") is True
    assert BaseCSNGenerator.is_sid_field("/BIC/XMYCHAR") is True
    assert BaseCSNGenerator.is_sid_field("CUSTOMER_SID") is True
    assert BaseCSNGenerator.is_sid_field("0CUSTOMER") is False


def test_t1_tarjan_scc_cycle_isolation(repo):
    repo.insert_object("0A", "INFOOBJECT", migration_path="Path 2")
    repo.insert_object("0B", "INFOOBJECT", migration_path="Path 2")
    repo.insert_dependency("0A", "0B", "ATTRIBUTE_OF")
    repo.insert_dependency("0B", "0A", "ATTRIBUTE_OF")

    builder = DependencyGraphBuilder(repo)
    cycles = builder.detect_cycles()
    assert len(cycles) == 1
    waves = builder.get_topological_waves()
    assert len(waves) >= 1
    assert len(builder.severed_edges) == 1


def test_t6_complex_abap_sets_warning_in_db(repo):
    repo.insert_object("TR_COMPLEX", "TRANSFORMATION", migration_path="Path 3")
    repo.insert_transformation(
        tran_id="TR_COMPLEX",
        source_obj="DS_1",
        target_obj="ADSO_1",
        rule_type="ROUTINE",
        field_mappings=[{"source": "A", "target": "A", "rule": "DIRECT"}],
        routines_abap=[{"routine_type": "END_ROUTINE", "abap_code": "SELECT SINGLE * FROM ZTAB INTO ls_z."}],
    )
    translator = TransformationTranslator(repo)
    res = translator.translate_transformation("TR_COMPLEX")
    assert len(res["warnings"]) == 1
    assert "MANUAL REWORK REQUIRED" in res["sql"]
    obj = repo.get_object("TR_COMPLEX")
    assert obj["warning_code"] == "COMPLEX_ABAP_ROUTINE"


def test_reserved_sap_namespace_rejected():
    with pytest.raises(ValueError, match="reserved by SAP"):
        BaseCSNGenerator(space_name="SAP_BW_MIGRATION")


def test_transformation_csn_has_elements_and_unprefixed_query(repo):
    repo.insert_object("TR_CLEAN", "TRANSFORMATION", migration_path="Path 3")
    repo.insert_transformation(
        tran_id="TR_CLEAN",
        source_obj="DS_SRC",
        target_obj="ADSO_TGT",
        rule_type="DIRECT",
        field_mappings=[{"source": "KUNNR", "target": "0CUSTOMER", "rule": "DIRECT"}],
        routines_abap=[],
    )
    res = TransformationTranslator(repo).translate_transformation("TR_CLEAN")
    defs = res["csn"]["definitions"]
    assert "V_DS_SRC_TO_ADSO_TGT" in defs
    view_def = defs["V_DS_SRC_TO_ADSO_TGT"]
    assert "elements" in view_def
    assert "0CUSTOMER" in view_def["elements"]
    assert 'FROM "DS_SRC"' in view_def["query"]
    assert "SAP_BW_MIGRATION" not in str(res["csn"])


def test_unified_lineage_assess_validate_deliver():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    objs = client.get("/api/v1/repository/objects?limit=5").json()["items"]
    if objs:
        tech = objs[0]["tech_name"]
        lin = client.get(f"/api/v1/graph/lineage/{tech}")
        assert lin.status_code == 200
        assert "upstream" in lin.json() and "downstream" in lin.json()

        ass = client.get(f"/api/v1/classify/assess/{tech}")
        assert ass.status_code == 200
        assert ass.json()["compatible"] is True

    val = client.post("/api/v1/generate/validate", json={
        "tech_name": "ZTEST_OBJ",
        "csn": {
            "$schema": "https://sap.com/csn/v1",
            "definitions": {
                "ZTEST_OBJ": {
                    "kind": "entity",
                    "@Analytics.dataCategory": "#DIMENSION",
                    "elements": {"ID": {"key": True, "type": "cds.String", "length": 10}},
                }
            },
        },
        "sql": 'SELECT "ID" FROM "SRC"',
    })
    assert val.status_code == 200
    assert val.json()["valid"] is True
