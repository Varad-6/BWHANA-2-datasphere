# SOP: F3 Governance, Reconciliation & Deployment Layer

## 1. Scope & Objective
This Standard Operating Procedure governs the execution of **Governance, Reconciliation & Deployment Layer (F3)** tools:
* **Tool T10: Process Chain & Security Converter (Path 7)**
* **Tool T11: Data Quality & Reconciliation Engine**
* **Tool T12: Web Orchestration Dashboard (Streamlit Control Center)**
* **Deployment Agent & CLI Ingestion Runner**
* **Audit Trail & Cutover Logging**

---

## 2. Tool T10: Process Chain & Security Converter (Path 7)

### 2.1 Process Chain to Task Chain Conversion
1. **Extraction:** Tool T10 extracts chain structure from `RSPCPROCESS` and `RSPCLOGCHAIN`.
2. **Node Mapping:**
   * DTP execution nodes $\rightarrow$ Datasphere **Data Flow Run Nodes** or **Replication Flow Trigger Nodes**.
   * ADSO activation nodes $\rightarrow$ Datasphere **View Persistence Run Nodes**.
   * Rollup / index build nodes $\rightarrow$ Omitted (handled natively by in-memory SAP HANA Cloud engine).
3. **Sequence & Parallelism:**
   * Sequential dependencies are mapped as `dependsOn` arrays in the Datasphere Task Chain JSON.
   * Parallel execution branches are preserved.
4. **Target Deployment Payload:** Generates standard Task Chain JSON deployed via REST API endpoint:
   `POST https://<tenant>.datasphere.cloud/api/v1/spaces/{spaceId}/taskchains`

### 2.2 Analysis Authorizations to Data Access Controls (DAC)
1. **Extraction:** Queries `RSECVAL` and `RSECBIOBJ` (authorization criteria by InfoObject).
2. **Criteria Mapping:**
   * InfoObject authorization criteria (e.g., `0PLANT = '1000' OR '2000'`) are mapped to Datasphere **Data Access Control (DAC)** criteria.
   * Value operator mapping: `EQ` $\rightarrow$ `=`, `CP` $\rightarrow$ `LIKE`, `BT` $\rightarrow$ `BETWEEN`.
3. **Binding:** Generates DAC policy linked to the corresponding Dimension Local Table or Analytical View:
   `POST https://<tenant>.datasphere.cloud/api/v1/spaces/{spaceId}/dataaccesscontrols`

---

## 3. Tool T11: Data Quality & Reconciliation Engine

### 3.1 Verification Methodology
Reconciliation operates continuously to guarantee zero data loss between the source BW tables and migrated Datasphere entities:

```
┌─────────────────────────────────┐           ┌─────────────────────────────────┐
│     SAP BW Source Persistent    │           │     SAP Datasphere Target       │
│  Tables (/BIC/A*2, /BI0/P*, ..) │           │   Local Tables & Fact Views     │
└────────────────┬────────────────┘           └────────────────┬────────────────┘
                 │                                             │
                 │ Record Count & Metric Sums                  │ Record Count & Metric Sums
                 ▼                                             ▼
       ┌─────────────────────────────────────────────────────────────┐
       │         Tool T11: Automated Reconciliation Engine           │
       │  • Absolute row-count comparison                            │
       │  • SHA-256 control hash on numerical metrics (AMOUNT, QTY)  │
       │  • Variance percentage evaluation: Tolerance <= 0.01%       │
       └─────────────────────────────┬───────────────────────────────┘
                                     │
                     ┌───────────────┴───────────────┐
                     ▼                               ▼
            PASS (Variance <= 0.01%)       FAIL (Variance > 0.01%)
            Wave Promotion Allowed          Alert Logged & Wave Halted
```

### 3.2 Reconciliation Algorithms
1. **Row Count Variance:**
   $$\text{Variance \%} = \frac{|\text{Source Rows} - \text{Target Rows}|}{\text{Source Rows}} \times 100$$
2. **Metric Sum Hash (SHA-256 Checksum):**
   * Aggregates primary numerical measure columns (e.g., `SUM(NETWR)`, `SUM(KWMENG)`).
   * Rounds to 2 decimal places, formats as canonical string, and hashes using SHA-256.
   * Compares source hash against target hash.

### 3.3 Status Codes in `reconciliation_results` Table
* `PASS`: Variance is $0.00\%$ or strictly within configured tolerance ($\le 0.01\%$).
* `WARNING`: Non-critical master data text variance (e.g. missing optional language descriptions).
* `FAIL`: Row-count mismatch or measure variance $> 0.01\%$. The wave is halted immediately for architectural review.

---

## 4. Tool T12: Web Orchestration Dashboard (Streamlit)

### 4.1 Launching the Control Center
Run from the root directory:
```bash
streamlit run dashboard/app.py
```

### 4.2 Operating Modules
* **Executive Overview:** Real-time KPI cards displaying in-scope objects, path breakdown, average complexity score, and wave completion status.
* **Dependency Graph & Waves:** Interactive visualization of topological waves derived from NetworkX; inspect individual wave object lists and view Graphviz DOT syntax.
* **CSN Code Inspector & Live Generator:** Select any InfoObject, ADSO, or Transformation to generate and preview its native CSN JSON on the fly with live SQL diffs.
* **Reconciliation Cockpit:** Review source vs. target row-count tables and pass/fail indicators.

---

## 5. Deployment Agent & CLI Ingestion Procedures

### 5.1 Deployment via `@sap/datasphere-cli`
1. Ensure the CLI is installed and configured:
   ```bash
   npm install -g @sap/datasphere-cli
   datasphere login --host <tenant-subdomain>.eu10.datasphere.cloud
   ```
2. Deploy compiled CSN documents into the target space:
   ```bash
   datasphere objects import --space DEV_SPACE_01 --file output/path2_infoobjects_csn.json
   datasphere objects import --space DEV_SPACE_01 --file output/path4_adsos_csn.json
   datasphere objects import --space DEV_SPACE_01 --file output/path3_transformations_csn.json
   ```

### 5.2 Deployment via REST API
* Endpoint: `POST https://<tenant>.datasphere.cloud/api/v1/spaces/{spaceId}/definitions`
* Headers:
  * `Authorization: Bearer <OAuth_Token>`
  * `Content-Type: application/json`
* Payload: The compiled CSN document generated by F2 tools.

---

## 6. Audit Trail & Cutover Logging Standards

Every deployed object must be recorded with full audit traceability:
* Record timestamp in UTC.
* Source commit SHA from Git.
* Executing engineer or subagent identifier.
* Validation test results and reconciliation report link.
* Status update in `metadata_repo.db` updated to `DEPLOYED` and `VALIDATED`.
