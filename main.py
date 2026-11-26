"""
BW/4HANA to SAP Datasphere Migration Accelerator
Main CLI Orchestrator (T0 - T12 Pipeline Runner)
"""

import os
import json
import argparse
from repository.db_manager import RepositoryManager
from extractors.t0_bw_scanner import BWInventoryScanner
from graph.t1_dependency_builder import DependencyGraphBuilder
from graph.t2_classifier import ObjectClassifier
from generators.t5_master_data import MasterDataMigrator
from generators.t6_transformation import TransformationTranslator
from generators.t7_adso import ADSODataMigrator

def main():
    parser = argparse.ArgumentParser(description="SAP BW/4HANA to SAP Datasphere Migration Accelerator")
    parser.add_argument("--mode", choices=["all", "scan", "classify", "generate"], default="all", help="Execution mode")
    parser.add_argument("--output-dir", default="output", help="Directory to save generated CSN JSON artifacts")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    print("=" * 65)
    print(" SAP BW/4HANA to SAP Datasphere Migration Accelerator ")
    print("=" * 65)

    # 1. Initialize Shared Metadata Repository
    db_path = "metadata_repo.db"
    print(f"\n[1/5] Initializing Shared Metadata Repository ({db_path})...")
    repo = RepositoryManager(db_path=db_path, use_duckdb=False)

    # 2. T0: Scan Inventory
    print("[2/5] Running Tool T0: BW Object Inventory Scanner...")
    scanner = BWInventoryScanner(repo)
    counts = scanner.scan_sample_metadata()
    print("      Scanned Object Summary:")
    for obj_type, cnt in counts.items():
        print(f"        - {obj_type:<20}: {cnt}")

    # 3. T2: Classifier & Complexity Scorer
    print("\n[3/5] Running Tool T2: Object Classifier & Complexity Scorer...")
    classifier = ObjectClassifier(repo)
    path_summary = classifier.classify_and_score()
    print("      Taxonomy Path Classification:")
    for path_name, cnt in path_summary.items():
        print(f"        - {path_name:<10}: {cnt} objects")

    # 4. T1: Dependency Graph Builder & Wave Planner
    print("\n[4/5] Running Tool T1: Dependency Graph Builder & Wave Sequence...")
    graph_builder = DependencyGraphBuilder(repo)
    waves = graph_builder.get_topological_waves()
    for wave in waves:
        print(f"      Wave {wave['wave_id']} ({len(wave['objects'])} objects): {', '.join(wave['objects'])}")

    # 5. T5 & T6 Generators (Paths 2 & 3 Focus)
    print("\n[5/5] Executing CSN Artifact Generators (Path 2 InfoObjects & Path 3 Transformations)...")

    # Path 2 Generation
    master_migrator = MasterDataMigrator(repo)
    path2_csn = master_migrator.convert_all_path2_objects()
    path2_file = os.path.join(args.output_dir, "path2_infoobjects_csn.json")
    with open(path2_file, "w", encoding="utf-8") as f:
        json.dump(path2_csn, f, indent=2)
    print(f"      [Path 2] Master Data CSN saved to: {path2_file}")

    # Path 3 Generation
    tran_translator = TransformationTranslator(repo)
    tr_objs = [o for o in repo.get_all_objects() if o["migration_path"] == "Path 3"]
    path3_results = []
    for tr in tr_objs:
        res = tran_translator.translate_transformation(tr["tech_name"])
        path3_results.append(res)
        print(f"      [Path 3] Transpiled Transformation '{tr['tech_name']}' -> SQL View with {len(res['warnings'])} warnings")

    path3_file = os.path.join(args.output_dir, "path3_transformations_csn.json")
    with open(path3_file, "w", encoding="utf-8") as f:
        json.dump([r["csn"] for r in path3_results], f, indent=2)
    print(f"      [Path 3] Transformations CSN saved to: {path3_file}")

    # Path 4 Generation (ADSOs)
    adso_migrator = ADSODataMigrator(repo)
    adso_objs = [o for o in repo.get_all_objects() if o["migration_path"] == "Path 4"]
    adso_csns = []
    for adso in adso_objs:
        csn = adso_migrator.convert_adso(adso["tech_name"])
        adso_csns.append(csn)
    path4_file = os.path.join(args.output_dir, "path4_adsos_csn.json")
    with open(path4_file, "w", encoding="utf-8") as f:
        json.dump(adso_csns, f, indent=2)
    print(f"      [Path 4] ADSO CSN saved to: {path4_file}")

    print("\n" + "=" * 65)
    print(" SUCCESS: Accelerator Run Complete! All artifacts generated in 'output/'.")
    print(" To launch the Streamlit Dashboard (T12), run:")
    print("   streamlit run dashboard/app.py")
    print("=" * 65)

    repo.close()

if __name__ == "__main__":
    main()
