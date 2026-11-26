# Standard Operating Procedure (SOP) — Project BW Morph

## 1. Document Overview & Purpose
**Project Name:** BW Morph  
**Purpose:** Standard Operating Procedure for migrating SAP BW / BW on HANA / BW/4HANA systems into SAP Datasphere using the modular T0–T12 automated accelerator.  
**Target Audience:** Solution Architects, SAP BW Leads, Datasphere Cloud Engineers, Data Engineers, and Autonomous Migration Agents.  
**Strict Mandate:** No changes or commits to Git may be pushed without explicit human architect approval.

---

## 2. Architectural Hierarchy (F1, F2, F3)

The BW Morph accelerator organizes the entire modernization lifecycle into three sequential, highly coordinated tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   SAP BW / BW4HANA (Source System)                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (RFC / OData Extraction)
┌───────────────────────────────────▼────────────────────────────────────┐
│ F1: FOUNDATION LAYER (T0 - T3)                                         │
│ • T0: BW Inventory Scanner                                             │
│ • Shared Metadata Repository (DuckDB / SQLite: metadata_repo.db)        │
│ • T1: Graph Analysis & Wave Planner (NetworkX DAG / Tarjan's SCC)      │
│ • T2: Automated Scoring & Object Classifier (1–5 scale, Paths 1–7)     │
│ • T3: Traffic Controller & Wave Handover Engine                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Wave Batches + Path Tags)
┌───────────────────────────────────▼────────────────────────────────────┐
│ F2: GENERATOR & TRANSLATOR LAYER (T4 - T9)                             │
│ • T4: Source System Converter (Path 1) -> Space Connections            │
│ • T5: InfoObjects Migrator (Path 2) -> Dimensions, Texts & Attributes  │
│ • T6: SQL & ABAP Transpiler (Path 3) -> SQL Views & AST Transpilation  │
│ • T7: ADSO Converter (Path 4) -> Local Tables & Fact Views             │
│ • T8: CompositeProvider Converter (Path 5) -> Analytical Relational    │
│ • T9: BEx Query Converter (Path 6) -> Analytic Models & SAC Perspectives│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Compiled CSN JSON Bundle)
┌───────────────────────────────────▼────────────────────────────────────┐
│ F3: CROSS-CUTTING & GOVERNANCE LAYER (T10 - T12)                       │
│ • T10: Process Chain & Security Converter (Path 7) -> Task Chains, DAC │
│ • T11: Data Quality & Reconciliation Engine -> Row-counts & SHA-256    │
│ • T12: Web Command Center (Streamlit Dashboard & Control Plane)        │
│ • Deployment Agent (@sap/datasphere-cli & REST Ingestion APIs)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Ingestion / Deployment)
┌───────────────────────────────────▼────────────────────────────────────┐
│                 SAP DATASPHERE (Target Business Cloud)                 │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Team Roles & Operating Responsibilities

| Role | Responsibilities | Assigned Tools |
| :--- | :--- | :--- |
| **Enterprise Solution Architect** | Defines target space, reviews wave schedules, signs off on complexity scores, reviews unparsed ABAP fallbacks, approves Git releases. | T1, T2, T3, T12 |
| **SAP BW Specialist** | Validates source dictionary extracts, verifies SID-to-business-key mappings, inspects active ADSO tables and transformation routines. | T0, T5, T6, T7 |
| **Datasphere Engineer** | Manages target space quotas, oversees CSN deployment via `@sap/datasphere-cli`, configures Data Provisioning Agent (DP Agent). | T4, T8, T9, T10 |
| **QA / Data Governance Lead** | Monitors reconciliation tolerance (0.01% drift threshold), validates row counts and numerical hash checksums between BW and DSP. | T11, T12 |

---

## 4. Phase-Gating Prerequisites & Quality Thresholds

Before any wave is promoted from one tier to the next, it must satisfy strict exit criteria:

1. **F1 Gate (Discovery to Generation):**
   * All in-scope objects cataloged in `metadata_repo.db` with valid technical names and raw JSON metadata.
   * Directed dependency graph built with 0 unresolved cyclic deadlocks.
   * Every object scored (1–5) and assigned an explicit migration path (`Path 1` to `Path 7`).
   * Wave sequence matrix compiled and locked in `wave_schedule`.

2. **F2 Gate (Generation to Deployment):**
   * Output JSON files validated against the **SAP Core Schema Notation (CSN) v1.0 specification**.
   * All referenced dimension entities exist prior to deploying dependent fact views or CompositeProviders.
   * Zero untranspiled syntax errors: all complex ABAP routines unparsed by AST regex must be cleanly wrapped in `/* MANUAL REWORK REQUIRED */` warning blocks without crashing the CSN compiler.

3. **F3 Gate (Cutover & Sign-Off):**
   * Target Space Local Tables and Views deployed successfully with HTTP 200/201 response.
   * Reconciliation check: variance percentage between BW source and Datasphere target must be $\le 0.01\%$.
   * Audit trail logged with deployment timestamps, operator ID, and Git commit hash.

---

## 5. Detailed SOP Reference Directory

* **[F1 Foundation Layer SOP](file:///C:/Users/Varad/Documents/GitHub/BWHANA-2-datasphere/docs/F1_FOUNDATION_LAYER_SOP.md):** Scanning, DuckDB repository schema, cycle-breaking graph analysis, complexity heuristics, and traffic batching.
* **[F2 Generator & Translator Layer SOP](file:///C:/Users/Varad/Documents/GitHub/BWHANA-2-datasphere/docs/F2_GENERATOR_TRANSLATOR_SOP.md):** InfoObjects, ADSOs (Inbound/Active/Change-Log), Transformations & ABAP AST transpilation, CompositeProviders, and BEx query translation into CSN JSON.
* **[F3 Governance & Deployment Layer SOP](file:///C:/Users/Varad/Documents/GitHub/BWHANA-2-datasphere/docs/F3_GOVERNANCE_CONTROL_SOP.md):** Process chains to task chains, security analysis authorizations to DAC, reconciliation validation, and Streamlit deployment operations.
