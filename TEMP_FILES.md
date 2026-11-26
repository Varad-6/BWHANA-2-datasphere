# Manifest of Temporary / Scratch / Clean Code Files

This file tracks all temporary scripts, mock datasets, and clean code generation utilities created in Project BW Morph. Any item listed here can be inspected or purged cleanly without impacting core runtime modules.

---

| File / Folder Path | Purpose & Description | Safe-to-Delete Condition |
| :--- | :--- | :--- |
| `clean_code/generate_diagrams.py` | Python generation script for SVG, Draw.io XML, and headless Chrome rendering wrapper. | Safe to delete or keep as a repeatable diagram build script. |
| `clean_code/build_mapping_excel.py` | OpenPyXL script generating the 4-tab enterprise Foundation Table Mapping Excel workbook. | Safe to delete or retain as a repeatable Excel builder. |
| `extractors/s21_live_verifier.py` | Read-only connection verification script probing SAP S21 HTTP/OData endpoints. | Retain in extractors/ as a pre-flight connectivity verification tool. |
| `clean_code/render_wrapper.html` | Temporary HTML wrapper for 2x scale Playwright screenshot capture of the SVG diagram. | Safe to delete anytime; regenerable on demand. |
| `generate_pdf.py` | Python script using ReportLab to compile the executive solution architecture PDF. | Safe to delete or retain in `clean_code/`. |
| `extractors/sample_data.py` | Mock BW system dictionary dataset used for offline testing of T0–T12 pipeline. | Do NOT delete during demo phase; replace with live RFC extractor in production. |
| `clean_code/playwright/test_phase1_api.spec.ts` | Playwright headless API test suite for Phase 1 health & OpenAPI endpoints. | Keep as permanent Phase 1 regression test suite. |
| `clean_code/playwright/test_phase2_scan.spec.ts` | Playwright headless test for Phase 2 live S21 OData scan. | Keep as permanent Phase 2 regression test suite. |
| `clean_code/playwright/test_phase3_repository.spec.ts` | Playwright headless test for Phase 3 repository endpoints. | Keep as permanent Phase 3 regression test suite. |
| `clean_code/playwright/test_phase4_graph.spec.ts` | Playwright headless test for Phase 4 dependency graph & waves. | Keep as permanent Phase 4 regression test suite. |
| `clean_code/playwright/test_phase5_classify.spec.ts` | Playwright headless test for Phase 5 classifier & complexity scorer. | Keep as permanent Phase 5 regression test suite. |
| `clean_code/playwright/test_phase6_generators.spec.ts` | Playwright headless test for Phase 6 CSN generators (Paths 2–4). | Keep as permanent Phase 6 regression test suite. |
| `clean_code/playwright/test_phase7_dashboard.spec.ts` | Playwright headless E2E browser test for Phase 7 Streamlit Wizard UI. | Keep as permanent Phase 7 regression test suite. |
