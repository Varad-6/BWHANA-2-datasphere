"""
Automated Integration & Unit Tests for BW/4HANA to Datasphere Migration Accelerator
"""

import pytest
import os
import json
from repository.db_manager import RepositoryManager
from extractors.t0_bw_scanner import BWInventoryScanner
from graph.t1_dependency_builder import DependencyGraphBuilder
from graph.t2_classifier import ObjectClassifier
from generators.t5_master_data import MasterDataMigrator
from generators.t6_transformation import TransformationTranslator
from generators.t7_adso import ADSODataMigrator

@pytest.fixture
def repo(tmp_path):
    db_file = str(tmp_path / "test_repo.db")
    mgr = RepositoryManager(db_path=db_file, use_duckdb=False)
    yield mgr
    mgr.close()

def test_t0_scanner_and_classifier(repo):
    scanner = BWInventoryScanner(repo)
    counts = scanner.scan_sample_metadata()

    assert counts["INFOOBJECT"] > 0
    assert counts["TRANSFORMATION"] > 0

    classifier = ObjectClassifier(repo)
    summary = classifier.classify_and_score()

    assert summary["Path 2"] >= 5
    assert summary["Path 3"] >= 2

def test_t1_dependency_graph(repo):
    scanner = BWInventoryScanner(repo)
    scanner.scan_sample_metadata()

    builder = DependencyGraphBuilder(repo)
    graph = builder.build_graph()

    assert len(graph.nodes) > 0
    waves = builder.get_topological_waves()
    assert len(waves) >= 1

def test_t5_infoobject_csn_generator(repo):
    scanner = BWInventoryScanner(repo)
    scanner.scan_sample_metadata()

    migrator = MasterDataMigrator(repo, space_name="TEST_SPACE")
    csn_doc = migrator.convert_infoobject("0CUSTOMER")

    assert "$schema" in csn_doc
    definitions = csn_doc["definitions"]
    assert "TEST_SPACE.0CUSTOMER" in definitions
    assert "TEST_SPACE.0CUSTOMER_TEXT" in definitions

    elem = definitions["TEST_SPACE.0CUSTOMER"]["elements"]
    assert "0CUSTOMER" in elem
    assert "0COUNTRY" in elem

def test_t6_transformation_transpiler(repo):
    scanner = BWInventoryScanner(repo)
    scanner.scan_sample_metadata()

    translator = TransformationTranslator(repo, space_name="TEST_SPACE")
    res = translator.translate_transformation("TR_STG_TO_CUBE")

    assert "sql" in res
    assert "SELECT" in res["sql"]
    assert "0CUSTOMER" in res["sql"]
    assert res["warnings"] is not None
