# SOP: F2 Generator & Translator Layer (CSN Synthesis & Code Transpilation)

## 1. Scope & Objective
This Standard Operating Procedure details the execution of **Generator & Translator Layer (F2)** tools:
* **Tool T4: Source System Converter (Path 1)**
* **Tool T5: InfoObjects Migrator (Path 2)**
* **Tool T6: SQL & ABAP Transpiler (Path 3)**
* **Tool T7: ADSO / DSO Table Converter (Path 4)**
* **Tool T8: CompositeProvider / MultiProvider Converter (Path 5)**
* **Tool T9: BEx Query Converter (Path 6)**
* **CSN Compilation & Schema Validation Engine**

All tools output valid **SAP Core Schema Notation (CSN) JSON** compliant with SAP Datasphere standards.

---

## 2. Tool T4: Source System Converter (Path 1)

### 2.1 Technical Transformation Rules
* On-premise SAP S/4HANA, ECC, or BW source connections are translated into **Datasphere Space Connections**:
  * Connection Type: `SAP HANA`, `SAP S/4HANA On-Premise`, or `Cloud Connector`.
  * Remote Table definition: Generates CSN schema headers with `@cds.external: true` and `@EndUserText.label`.
* Flat file DataSources are translated into **Datasphere CSV Ingestion Stubs** or Local Staging Tables.

---

## 3. Tool T5: InfoObjects Migrator (Path 2)

### 3.1 Characteristic (`CHA`) to Dimension Conversion
BW characteristics are converted into Datasphere Local Tables with semantic category `#DIMENSION`:
```json
{
  "SAP_BW_MIGRATION.0CUSTOMER": {
    "kind": "entity",
    "@EndUserText.label": "Customer Master",
    "@Analytics.dataCategory": "#DIMENSION",
    "elements": {
      "0CUSTOMER": {
        "key": true,
        "type": "cds.String",
        "length": 10,
        "@EndUserText.label": "Customer ID"
      }
    }
  }
}
```

### 3.2 Master Data Attributes & Live Associations
* **Time-Independent Attributes (`/BI0/P*`):** Added as direct elements in the dimension entity.
* **Semantic Associations (`cds.Association`):** If `0CUSTOMER` has attribute `0COUNTRY`, a 1:1 association is declared in CSN:
```json
"to_0COUNTRY": {
  "type": "cds.Association",
  "target": "SAP_BW_MIGRATION.0COUNTRY",
  "on": [
    { "ref": ["0COUNTRY"] },
    "=",
    { "ref": ["to_0COUNTRY", "0COUNTRY"] }
  ]
}
```
* **Time-Dependent Attributes (`/BI0/Q*`):** Created with temporal keys `DATE_FROM` and `DATE_TO` with `@Semantics.businessDate.from: true`.

### 3.3 Master Data Texts (`/BI0/T*`)
* Generated as a dedicated text entity named `<IOBJ>_TEXT` with semantic category `#TEXT`:
* Compound Key: Natural business key (`0CUSTOMER`) + `LANGUAGE_CODE` (`cds.String`, length 2).
* Description Fields: `TXTSH` (Short, 20), `TXTMD` (Medium, 40), `TXTLG` (Long, 60).

### 3.4 Surrogate IDs (SIDs) Resolution
* **Problem:** In SAP BW, tables `/BI0/S*`, `/BI0/X*`, and `/BI0/Y*` store integer surrogate keys (SIDs) for internal joins.
* **Resolution Standard:** In SAP Datasphere, natural alphanumeric business keys are used. Tool T5 replaces all internal SID lookups with the parent InfoObject characteristic key.

### 3.5 Compounding Key Handling
* When an InfoObject is compounded (e.g. `0COSTCENTER` compounded with `0CONTROLLING_AREA`):
  * In Datasphere CSN, **both fields are declared as compound primary keys** (`"key": true`).
  * The natural hierarchy is enforced through composite key associations.

---

## 4. Tool T6: SQL & ABAP Transpiler (Path 3)

### 4.1 Transformation Rule Conversion
1. **Direct Rules:** Translated into projected `SELECT` expressions (`"SRC_FIELD" AS "TGT_FIELD"`).
2. **Constants:** Converted to SQL string/numeric literals (`'ACTIVE' AS "STATUS"`).
3. **Formulas:** Transpiled via regex syntax trees:
   * `IF(A > 0, B, C)` $\rightarrow$ `CASE WHEN A > 0 THEN B ELSE C END`
   * `CONCATENATE(A, B)` $\rightarrow$ `CONCAT(A, B)` or `A || B`
   * `DATE_DIFF(D1, D2)` $\rightarrow$ `DAYS_BETWEEN(D2, D1)`

### 4.2 ABAP Routine Transpilation Strategy (Dual-Track)

#### Track A: Automatic AST Transpilation to SQL Views
* **DELETE SOURCE_PACKAGE WHERE condition:**
  * Regex parses the condition, converts `IS INITIAL` to `(FIELD IS NULL OR FIELD = '')`, and outputs a negative SQL `WHERE` filter:
    ```sql
    WHERE NOT (DOC_STATUS IS NULL OR DOC_STATUS = '')
    ```
* **Field Computations:**
  * `RESULT = SOURCE_FIELDS-NET_PRICE * SOURCE_FIELDS-QUANTITY.`
  * Converted to: `("NET_PRICE" * "QUANTITY") AS "TOTAL_AMOUNT"`

#### Track B: Complex Routine Fallback (Datasphere Data Flow)
* **Trigger:** Complex ABAP routines containing database lookups (`SELECT SINGLE ... FROM ... INTO ...`), internal tables (`LOOP AT ...`), or function calls.
* **Procedure:**
  1. Tool T6 inserts an explicit manual review comment into the CSN SQL View:
     ```sql
     /* MANUAL REWORK REQUIRED: Complex ABAP routine in TR_01 */
     ```
  2. The object is flagged in `metadata_repo.db` with a warning code `COMPLEX_ABAP_ROUTINE`.
  3. The engineer routes the logic into a **Datasphere Data Flow** using a Python or SQL Script operator:
     * In the Data Flow Python operator, read source dataset, perform vectorized pandas transformation, and output to target table.

---

## 5. Tool T7: ADSO / DSO Table Converter (Path 4)

### 5.1 ADSO Architectural Mapping

| BW ADSO Physical Table | Table Purpose | Target SAP Datasphere Entity | CSN Definition Category |
| :--- | :--- | :--- | :--- |
| **Inbound Queue (`/BIC/A*1`)** | Staging / unactivated incoming data | Inbound Staging Local Table | `"@Analytics.dataCategory": "#STAGING"` |
| **Active Data Table (`/BIC/A*2`)** | Core activated transactional records | Primary Analytical Fact Local Table | `"@Analytics.dataCategory": "#FACT"` |
| **Change Log Table (`/BIC/A*3`)** | Historical delta changes (`RECORDMODE`) | Change Log Audit Relational View | Regular relational entity |

### 5.2 Legacy BW 7.x DSO & InfoCube Mapping
* **Classic Standard DSO:** Active table (`/BIC/A<DSO>00`) is mapped directly to a Fact Local Table. Change log table (`/BIC/B<DSO>00`) is mapped to an audit history view.
* **Standard InfoCube:**
  * The compressed E-fact table (`/BIC/E<CUBE>`) and uncompressed F-fact table (`/BIC/F<CUBE>`) are unified into a single Datasphere Fact Local Table.
  * Dimension tables (Dim ID $\rightarrow$ SID $\rightarrow$ Key) are collapsed into a clean star schema with direct dimension associations.

---

## 6. Tool T8: CompositeProvider Converter (Path 5)

### 6.1 CompositeProvider & MultiProvider Translation
* **Input:** Union and join tree metadata from `RSDHCPR` and `RSDHCPRCOMP` (or legacy `RSDMULTIIOBJ`).
* **Logic:**
  1. Creates a Datasphere **Analytical View** combining underlying Part Providers (ADSOs from T7).
  2. Union nodes: Converted to SQL `UNION ALL` with empty column padding for non-overlapping attributes.
  3. Join nodes: Converted to SQL `LEFT OUTER JOIN` or `INNER JOIN` based on join cardinality.
  4. Dimensions: Joins Dimension Local Tables (from T5) to Fact views on primary business keys.
* **Output:** Valid CSN Analytical View with star schema annotations.

---

## 7. Tool T9: BEx Query Converter (Path 6)

### 7.1 Multi-Dimensional Semantic Mapping
1. **Restricted Key Figures (RKF):**
   * Transpiled to **Datasphere Restricted Measures** filtered by specific dimension values (e.g., `Net Amount WHERE FiscalYear = '2026'`).
2. **Calculated Key Figures (CKF):**
   * Transpiled to **Datasphere Calculated Measures** (e.g., `(Actual Revenue - Budget Revenue) / Budget Revenue * 100`).
3. **Query Variables:**
   * Converted to **Analytic Model Input Parameters** (prompts for single values, ranges, or multiple selections).
4. **Output Perspectives:**
   * Generates SAP Datasphere **Analytic Models** natively consumable by **SAP Analytics Cloud (SAC)** and Microsoft Power BI via the Direct Data Connection.

---

## 8. CSN Schema Compilation & Validation

1. All definitions generated across T5, T6, T7, T8, and T9 are bundled into the standard CSN envelope:
   ```json
   {
     "$schema": "https://sap.com/csn/v1",
     "meta": {
       "creator": "BW-Morph-Migration-Accelerator",
       "version": "1.0.0"
     },
     "definitions": { ... }
   }
   ```
2. The compilation engine writes the JSON documents to `output/`:
   * `path2_infoobjects_csn.json`
   * `path3_transformations_csn.json`
   * `path4_adsos_csn.json`
3. Tool validates JSON syntax and schema compliance against the official SAP CSN v1.0 standard prior to handing over to F3 deployment tools.
