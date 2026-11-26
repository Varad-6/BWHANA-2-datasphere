# Project BW Morph — Change Log

All notable changes, architectural milestones, and fixes for Project BW Morph are documented in this file.

---

## [2026-11-26] BW Morph Home Launchpad -> S21 Sync -> Clean Single-Row 8-Stage Studio
- **Problem:** Duplicate 8-stage stepper bars, an empty white HTML wrapper div above the Object Selector, and missing Launchpad Home -> S21 Connection & Sync acceptance flow.
- **Changed:**
  - `dashboard/app.py`: Added BW Morph Home Launchpad with SAP S21 Connection & Live Sync Acceptance card (`✓ Accept Details & Sync Live S21`) and Fiori Launchpad Box (`Open BW Migration Studio`); replaced raw HTML wrapper divs with native `st.container(border=True)` and removed the duplicate HTML stage bar so only 1 clean row of 8 stage buttons renders.
  - `clean_code/playwright/test_phase7_dashboard.spec.ts`: Verified full Home -> Accept & Sync -> Open Studio Box -> Single-row 8-stage stepper (`count() == 1`) -> Stage 1..8 E2E flow.
- **Tests added:** Playwright `test_phase7_dashboard.spec.ts` (`1/1 passed` in `14.7s`).
- **SAP/CSN impact:** None — SAP S21 remains 100% strict read-only `GET`/`HEAD`.
- **UX impact:** Clean Launchpad Box entry, persisted sync confirmation banner, zero duplicate bars, zero empty divs.
- **Known risk/follow-up:** None.

---

## [2026-11-26] Unified 8-Stage BW Migration Studio (Single Centralized Page)
- **Problem:** Users previously had to switch between separate Launchpad studio pages for different BW object types, and lacked per-object lineage, assessment, validation, and delivery stages inside a single workflow.
- **Changed:**
  - `api/routers/graph.py`: Added `GET /api/v1/graph/lineage/{tech_name}` for upstream/downstream dependencies, wave assignment, and cycle status.
  - `api/routers/classify.py`: Added `GET /api/v1/classify/assess/{tech_name}` for compatibility, risk flags, and recommended Datasphere target pattern.
  - `api/routers/generate.py`: Expanded `GET /api/v1/generate/object/{tech_name}` to support all 7 Paths (1–7), and added `POST /api/v1/generate/validate` and `POST /api/v1/generate/deliver`.
  - `dashboard/app.py`: Consolidated into a single unified **SAP Fiori Horizon** BW Migration Studio with centralized object selector (all BW object types) and integrated 8-stage workflow (`1. Discover` -> `2. Analyze` -> `3. Explore Lineage` -> `4. Assess` -> `5. Map` -> `6. Transform` -> `7. Validate` -> `8. Deliver`).
  - `tests/test_phases_2_to_6.py` & `clean_code/playwright/test_phase7_dashboard.spec.ts`: Added unit tests and full 8-stage unified E2E Playwright test.
- **Tests added:** `pytest` (`13/13 passed`) and Playwright headless (`8/8 passed` in `16.6s`).
- **SAP/CSN impact:** Full Path 1–7 coverage; SAP S21 remains 100% strict read-only `GET`/`HEAD`.
- **UX impact:** Single centralized page — zero studio/page switching required.
- **Known risk/follow-up:** None.

---

## [2026-11-26] Remove Reserved SAP_* Namespace & Fix Transformation CSN Import
- **Problem:** SAP Datasphere rejected CSN import (`You do not have permission to create, update or delete objects in the "SAP_BW_MIGRATION" namespace`) because `SAP_*` namespaces are reserved, and Transformation `#CUBE` CSN views lacked explicit `elements` alongside `query`.
- **Changed:**
  - `generators/base_generator.py`: Changed default `space_name` to `""` (unprefixed active Space import), added `validate_namespace()` rejecting `SAP_*` prefixes, and added `qualify_name()`.
  - `generators/t5_master_data.py`, `generators/t7_adso.py`: Defaulted `space_name=""` and used `qualify_name()` for all entity keys and associations.
  - `generators/t6_transformation.py`: Defaulted `space_name=""`, emitted unprefixed `FROM "<source>"` SQL queries, and included explicit `elements` dictionary alongside `query` in `#CUBE` view definitions.
  - `api/routers/generate.py` & `dashboard/app.py`: Defaulted namespace to `""` (Active Space), returned HTTP 400 on `SAP_*` namespaces, and updated UI hints.
  - `tests/test_phases_2_to_6.py`: Added `test_reserved_sap_namespace_rejected` and `test_transformation_csn_has_elements_and_unprefixed_query`.
- **Tests added:** `pytest` (12/12 passed) and Playwright headless (`8/8 passed`).
- **SAP/CSN impact:** CSN artifacts now import directly into any customer Datasphere Space without `SAP_*` namespace permission errors.
- **UX impact:** Step 4 and Cockpit default to blank (Active Space) namespace.
- **Known risk/follow-up:** None.

---

## [2026-11-26] SAP Fiori Horizon Cockpit & 5-Step Editable Studio Frontend
- **Problem:** Initial wizard frontend lacked SAP Fiori Horizon polish, launchpad studio tiles, and inline editable schema/naming controls. Also resolved `pyarrow`/`numpy 1.26.4` runtime ImportError in `st.dataframe`.
- **Changed:**
  - `.agents/rules/bw-morph-frontend-prompt.md`: Added comprehensive SAP Fiori Horizon (`sap_horizon`) frontend architecture & UX specification.
  - `api/routers/generate.py` & `api/main.py`: Added `POST /api/v1/generate/compile` local endpoint to compile user-edited columns, types, keys, naming, and SQL filters into SAP CSN v1.0 JSON + Pure SQL View.
  - `dashboard/app.py`: Rebuilt frontend to match SAP Fiori Horizon (`#F5F6F7` canvas, `#FFFFFF` `16px` launchpad tiles, `#0070F2` primary buttons, `72` font stack), 5 studio tiles, and 5-step editable studio (`Select -> Artifacts -> Editable Columns Grid -> Editable Object Naming -> Live CSN & SQL Downloads`).
  - `clean_code/playwright/test_phase7_dashboard.spec.ts`: Expanded E2E test verifying launchpad tiles, 5-step navigation, and live edit propagation (`Z_EDITED_E2E_ADSO`) into Step 5 CSN output.
- **Tests added:** `pytest` (10/10 passed) and Playwright headless (`8/8 passed` across Phases 1–7).
- **SAP/CSN impact:** Local-only CSN compilation endpoint added; SAP S21 remains 100% strict read-only `GET`/`HEAD`.
- **UX impact:** Full SAP Fiori Horizon cockpit with editable `st.data_editor` column grid, editable naming/SQL inputs, and live downloadable `.csn.json`/`.sql` artifacts.
- **Known risk/follow-up:** None.

---

## [2026-11-26] Phases 2–7 — Live S21 OData Extractor, Repository, Graph, Classifier, CSN Generators & Streamlit Wizard
- **Problem:** Needed end-to-end live SAP S21 OData extraction, production repository persistence, Tarjan's SCC dependency planning, 7-path classification, CSN v1.0 generators (with SID suppression & ABAP rework flagging), and a decoupled Design Thinking Streamlit Wizard UI.
- **Changed:**
  - `api/sap/odata_client.py` & `api/sap/catalog_extractor.py`: Thread-safe OData HTTP client (GET/HEAD-only enforced via `SAPReadOnlyViolationError`) and live Gateway Catalog + EDMX `$metadata` extractor.
  - `extractors/t0_bw_scanner.py` & `api/routers/scan.py`: Live S21 OData inventory scanner (`scan_live_s21`) and `/api/v1/scan/*` endpoints.
  - `repository/schema.sql`, `repository/db_manager.py`, `api/routers/repository.py`: Idempotent column migrations, `phase_status` persistence table, `save_wave_schedule`, and `/api/v1/repository/*` endpoints.
  - `graph/t1_dependency_builder.py` & `api/routers/graph.py`: Tarjan's SCC cycle detection (`detect_cycles`), non-fatal back-edge severing, topological waves, and `/api/v1/graph/*` endpoints.
  - `graph/t2_classifier.py` & `api/routers/classify.py`: 7-Path heuristic scorer (1–5) covering `INFOCUBE`, `MULTIPROVIDER`, `ANALYSIS_AUTH`, and `/api/v1/classify/*` endpoints.
  - `generators/base_generator.py`, `t5_master_data.py`, `t6_transformation.py`, `t7_adso.py`, `api/routers/generate.py`: SID suppression, compounding composite keys, time-dependent attributes, `CONCATENATE`/`DATE_DIFF` transpilation, `COMPLEX_ABAP_ROUTINE` DB flagging, `*1`/`*2`/`*3` ADSO partitions, and `/api/v1/generate/*` endpoints.
  - `dashboard/app.py`: Decoupled Streamlit Wizard UI (zero direct engine imports; FastAPI-only via HTTP GET) with progressive disclosure, status-gated `→ Next Step` buttons, and CSN syntax-highlighted viewer + download.
  - `tests/test_phases_2_to_6.py` & `clean_code/playwright/test_phase2..7*.spec.ts`: Full pytest and headless Playwright E2E test suites.
- **Tests added:** `pytest` (10/10 passed) and Playwright headless (`8/8 passed` across Phases 1–7).
- **SAP/CSN impact:** Live S21 OData extraction (strictly read-only GET) generating valid CSN v1.0 artifacts in `output/`.
- **UX impact:** Full 6-step guided wizard UI with persisted DB progress and disabled-until-complete navigation gates.
- **Known risk/follow-up:** None for F1/F2/T12; ready for interactive use or F3 Task Chain / DAC / Reconciliation extensions.

---

## [2026-11-26] Phase 1 — API Foundation & Infrastructure
- **Problem:** Needed a decoupled FastAPI REST backend on port 8001 with typed `.env` configuration, strict `SAP_READ_ONLY` enforcement, shared DB dependency injection, and health verification against SQLite and live SAP S21.
- **Changed:**
  - `requirements.txt`: Added locked dependency manifest.
  - `api/__init__.py`, `api/routers/__init__.py`: Initialized API package structure.
  - `api/config.py`: Added pydantic-settings `Settings` with validator enforcing `sap_read_only=True`.
  - `api/dependencies.py`: Added cached `RepositoryManager` singleton dependency provider.
  - `api/routers/health.py`: Added `GET /api/v1/health` checking DB (`SELECT 1`) and SAP S21 TCP reachability (`192.168.1.55:8000`).
  - `api/main.py`: Configured FastAPI app, localhost CORS, global structured JSON exception handler, and Uvicorn runner.
  - `tests/test_api_phase1.py`: Added unit/integration tests for settings safety validator and `/api/v1/health`.
  - `clean_code/playwright/playwright.config.ts`, `clean_code/playwright/package.json`, `clean_code/playwright/test_phase1_api.spec.ts`: Added Playwright API test suite.
- **Tests added:** `pytest` (6/6 passed) and Playwright headless (`2/2 passed` against live Uvicorn on `127.0.0.1:8001`).
- **SAP/CSN impact:** No — read-only TCP reachability check only.
- **UX impact:** No — backend foundation for upcoming Streamlit wizard integration.
- **Known risk/follow-up:** Ready to proceed to Phase 2 (SAP S21 Live OData Extractor).

---

## [2026-11-26] Foundation Table Mapping Excel Workbook & Live SAP S21 Read-Only Verification
- **Problem:** Need for an authoritative technical mapping workbook bridging demo video actions to F1/F2/F3 SOP layers, listing all source SAP metadata tables, retrieval rationale, extraction protocols, downstream lineage, and Datasphere CSN / OData endpoints. Also required live connection verification against SAP system S21 under strict read-only safety guardrails.
- **Changed:**
  - `docs/BW_Morph_Foundation_Table_Mapping.xlsx`: Comprehensive 4-tab enterprise Excel workbook containing Architecture Alignment (Tab 1), Foundation Table Mapping (Tab 2: RSD*, RSO*, RSTRAN*, /BIC/A* physical tables to CSN categories), OData & Ingestion API Catalog (Tab 3: RFC, ADT, Gateway, and Datasphere REST/CLI endpoints), and S21 Live Verification Checklist (Tab 4).
  - `.env`: Configured local environment variables for SAP system S21 (`192.168.1.55`, SID `S21`, Client `200`, User `INT_SAMARTH`, ports 3200/3300/8000) with mandatory `SAP_READ_ONLY=TRUE` enforcement.
  - `clean_code/build_mapping_excel.py`: OpenPyXL script generating the formatted, styled 4-tab Excel workbook.
  - `extractors/s21_live_verifier.py`: Strictly read-only Python verifier probing SAP ICF, ADT, and OData Gateway Catalog service (`/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/`), successfully returning HTTP 200 OK.
- **Tests added:** Executed `clean_code/build_mapping_excel.py` to compile the 4-tab Excel workbook; executed `extractors/s21_live_verifier.py` against live SAP host `192.168.1.55:8000`, confirming authentication and read-only access.
- **SAP/CSN impact:** Maps all 7 migration paths to CSN v1.0 data categories (`#DIMENSION`, `#FACT`, `#STAGING`, `#CUBE`, `#TEXT`), Task Chains, and Data Access Controls (DAC).
- **Known risk/follow-up:** System user `INT_SAMARTH` has full administrative authorization (`SAP_ALL`) on S21; strict read-only policy must remain permanently enabled across all extractor tools.

---

## [2026-11-26] Baseline Solution Architecture, Enterprise Diagrams & SOP Suite
- **Problem:** Need for an authoritative architectural blueprint, standard operating procedures (SOPs) across tiers F1, F2, and F3, an enterprise horizontal pipeline diagram with multi-format exports, and a senior developer rule hook for team collaboration and agent governance.
- **Changed:**
  - `clean_code/BW_Morph_Architecture_Horizontal.drawio`: Complete 5-swimlane horizontal architecture diagram (Source, F1, F2, F3, Target) with right-hand notes panel and legend on a 1920×1080 canvas.
  - `clean_code/BW_Morph_Architecture_Horizontal.svg`: High-resolution vector export with crisp typography (Segoe UI/Inter).
  - `clean_code/BW_Morph_Architecture_Horizontal.png`: 2x scale (3840×2160) ultra-high-definition rendered PNG via Chrome headless.
  - `docs/SOP_OVERVIEW.md`: Master SOP governance, roles, architectural hierarchy, and phase-gating exit criteria.
  - `docs/F1_FOUNDATION_LAYER_SOP.md`: Detailed SOP for T0 scanner, DuckDB metadata repository, T1 graph analysis, T2 complexity heuristics, and T3 wave traffic control (covering both BW/4HANA and BW 7.x).
  - `docs/F2_GENERATOR_TRANSLATOR_SOP.md`: Detailed SOP for T4 source systems, T5 InfoObjects (attributes, texts, surrogate SIDs, compounding), T6 transformations & ABAP AST transpiler, T7 ADSOs (inbound, active, change log), T8 CompositeProviders, and T9 BEx queries.
  - `docs/F3_GOVERNANCE_CONTROL_SOP.md`: Detailed SOP for T10 process/task chains & DAC, T11 reconciliation engine (row counts & SHA-256 metric sums), T12 Streamlit dashboard, and `@sap/datasphere-cli` deployment.
  - `.agents/rules/bw-morph-senior-dev-prompt.md`: Senior Migration Architect Hook & System Prompt modeled on the Transporter Portal rule, enforcing no unapproved Git pushes, plan-approval-execute-log discipline, and CSN v1.0 validation.
  - `TEMP_FILES.md`: Initialized scratch manifest tracking clean code and temporary files.
- **Tests added:** Validated diagram generation and Playwright headless 2x screenshot rendering; verified Markdown cross-links across all SOPs.
- **SAP/CSN impact:** Full architectural mapping established for Paths 1 through 7, covering SAP BW dictionary extraction to Datasphere CSN JSON models.
- **Known risk/follow-up:** Live SAP RFC connectivity tests to be conducted once on-premise connection parameters are provisioned.
