# SOP: F1 Foundation Layer (Discovery, Graph Analysis & Wave Planning)

## 1. Scope & Objective
This Standard Operating Procedure governs the execution of **Foundation Layer (F1)** tools:
* **Tool T0: BW Inventory Scanner & In-Scope Extractor**
* **Shared Metadata Repository (DuckDB / SQLite)**
* **Tool T1: Graph Analysis & Cycle Resolution Engine**
* **Tool T2: Automated Scoring & Object Classifier**
* **Tool T3: Traffic Controller & Wave Handover Engine**

Applies to both modern **SAP BW/4HANA** (ADSOs, CompositeProviders) and legacy **SAP BW 7.x / BW on HANA** (InfoCubes, MultiProviders, classic DSOs, DataSources 3.x/7.x).

---

## 2. Tool T0: BW Inventory Scanner & Extraction

### 2.1 Extraction Prerequisites
1. **Connectivity:** Active RFC destination configured in `config/settings.yaml` (or SAP Cloud Connector reverse-proxy tunnel).
2. **Authorizations in SAP BW:**
   * Authorization object `S_TABU_DIS` with activity `03` (Display) for table authorization group `&NC&` and table clusters `RS*`.
   * Authorization object `S_RFC` for function modules: `RFC_READ_TABLE`, `BAPI_MDPROVIDER_*`.

### 2.2 Table-by-Table Extraction Catalog

#### For SAP BW/4HANA:
* **InfoObjects:** Query `RSDIOBJ`, `RSDCHABAS`, `RSDATTR`, `RSDIOBJT`.
* **ADSOs:** Query `RSOADSO`, `RSDDSO`, `RSDODSOIOBJ`.
* **Transformations & Rules:** Query `RSTRAN`, `RSTRANRULE`, `RSTRANROUT`.
* **CompositeProviders:** Query `RSDHCPR`, `RSDHCPRCOMP`, `RSDHCPRLNK`.
* **Analytic Queries:** Query `RSZELTDIR`, `RSZCALC`, `RSZCOMPDIR`.

#### For Legacy SAP BW 7.x / BW on HANA:
* **Classic DSOs:** Query `RSDODSO` (extract active `/BIC/A*00` or `/BI0/A*00` table layouts).
* **InfoCubes:** Query `RSDCUBE`, `RSDCUBET`, `RSDCUBEIOBJ` (E-fact `/BIC/E*` and F-fact `/BIC/F*` tables).
* **MultiProviders:** Query `RSDMULTIIOBJ`, `RSDPART` (extract underlying part providers and identification mapping).
* **DataSources (ODP & 3.x/7.x):** Query `ROOSOURCE`, `ROOSATTR`, `ROOSFIELD`.

### 2.3 Step-by-Step Execution
1. Verify database initialization:
   ```bash
   python -c "from repository.db_manager import RepositoryManager; repo = RepositoryManager(); print('DB Ready')"
   ```
2. Execute the inventory scanner:
   ```bash
   python main.py --mode scan
   ```
3. Verify object count output. Verify that the table `objects` in `metadata_repo.db` contains expected records with status `PENDING`.

---

## 3. Shared Metadata Repository Specifications

The metadata repository is stored in `metadata_repo.db` (DuckDB or SQLite format):

### 3.1 DDL Schema Reference
```sql
-- Objects Master Table
CREATE TABLE IF NOT EXISTS objects (
    tech_name VARCHAR(100) PRIMARY KEY,
    object_type VARCHAR(50) NOT NULL, -- INFOOBJECT, ADSO, INFOCUBE, COMPOSITE_PROVIDER, MULTIPROVIDER, BEX_QUERY, TRANSFORMATION, DTP, PROCESS_CHAIN, SOURCE_SYSTEM
    description VARCHAR(255),
    complexity_score INT DEFAULT 1,
    migration_path VARCHAR(20),        -- Path 1 to Path 7
    status VARCHAR(50) DEFAULT 'PENDING',
    raw_metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lineage & Dependency Table
CREATE TABLE IF NOT EXISTS dependencies (
    id VARCHAR(100) PRIMARY KEY,
    source_obj VARCHAR(100) NOT NULL,
    target_obj VARCHAR(100) NOT NULL,
    dependency_type VARCHAR(50),       -- DATA_FLOW, USES_MASTER_DATA, QUERIES_PROVIDER, ATTRIBUTE_OF, COMPOUNDED_WITH
    FOREIGN KEY (source_obj) REFERENCES objects(tech_name),
    FOREIGN KEY (target_obj) REFERENCES objects(tech_name)
);

-- Transformation Details Table
CREATE TABLE IF NOT EXISTS transformations (
    tran_id VARCHAR(100) PRIMARY KEY,
    source_obj VARCHAR(100) NOT NULL,
    target_obj VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50),             -- DIRECT, CONSTANT, FORMULA, ROUTINE
    field_mappings JSON,
    routines_abap JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wave Schedule Table
CREATE TABLE IF NOT EXISTS wave_schedule (
    wave_id INT PRIMARY KEY,
    wave_name VARCHAR(100),
    objects_count INT,
    status VARCHAR(50) DEFAULT 'PLANNED'
);
```

---

## 4. Tool T1: Graph Analysis & Cycle Resolution Engine

### 4.1 Dependency Mapping Logic
* **InfoObject Attributes:** Source attribute `0COUNTRY` $\rightarrow$ Target InfoObject `0CUSTOMER` (`type: ATTRIBUTE_OF`).
* **Transformations:** Source `DS_SALES_HEADER` $\rightarrow$ Transformation `TR_01` $\rightarrow$ Target `ADSO_SALES_STG` (`type: DATA_FLOW`).
* **CompositeProviders / MultiProviders:** Part provider `ADSO_SALES_CUBE` $\rightarrow$ Target `HCPR_SALES_ANALYSIS` (`type: PROVIDES_DATA_TO`).
* **Queries:** CompositeProvider `HCPR_SALES_ANALYSIS` $\rightarrow$ Query `REP_SALES_Q001` (`type: QUERIED_BY`).

### 4.2 Cycle Resolution Algorithm
In legacy BW systems, circular dependencies frequently occur (e.g. InfoObject A has navigational attribute B, which compounded with A; or master data lookup routines creating dual flows).
1. Construct directed graph using `networkx.DiGraph`.
2. Execute Tarjan’s strongly connected components algorithm:
   ```python
   cycles = list(nx.simple_cycles(graph))
   ```
3. If cycles exist:
   * Isolate the cyclic sub-graph.
   * Identify non-fatal back-edges (e.g., text-lookup associations or optional display attributes).
   * Sever the back-edge temporarily for wave generation, recording the association to be restored during post-wave semantic link generation.
4. Execute `nx.topological_generations(dag)` to produce topological wave groupings.

---

## 5. Tool T2: Automated Scoring & Object Classifier

### 5.1 Complexity Rating Heuristics (Scale 1 to 5)

| Object Type | Heuristic Evaluation Criteria | Complexity Score |
| :--- | :--- | :--- |
| **InfoObject** | Base characteristic or key figure without attributes or compounding | **1** |
| | InfoObject with 1–4 simple display attributes | **2** |
| | InfoObject with compounding keys or navigational attributes | **3** |
| | InfoObject with multiple compounding keys and temporal hierarchies | **4** |
| | Complex InfoObject with external HANA views and custom authorization exits | **5** |
| **ADSO / DSO** | Staging ADSO (Inbound queue only, write-optimized) | **2** |
| | Standard ADSO (<15 fields, single active table) | **3** |
| | Complex ADSO (>15 fields, non-cumulative inventory, or active + changelog) | **4** |
| **InfoCube (BW 7.x)** | Standard Multi-dimensional InfoCube with E and F fact tables | **4** (mapped to Path 4 ADSO/Fact) |
| **Transformation** | 100% Direct field mappings or constant rules | **1** |
| | Formula expressions (simple arithmetic, string concatenation) | **2** |
| | 1–2 ABAP Start/End routines without database lookups | **4** |
| | Complex ABAP routines with custom SQL queries, internal tables, or expert routine | **5** |
| **CompositeProvider** | 1–2 Part Providers joined on primary keys | **2** |
| | MultiProvider / CompositeProvider with 3+ providers, union and left outer joins | **3** to **4** |
| **BEx Query** | Simple tabular query with basic filters | **1** |
| | Query with Restricted Key Figures (RKF) and Calculated Key Figures (CKF) | **2** |
| | Query with customer-exit variables, condition thresholds, and structural components | **3** to **4** |

### 5.2 Taxonomy Path Mapping
* **Path 1:** Source Systems & DataSources (`SOURCE_SYSTEM`, `DATASOURCE`)
* **Path 2:** Master Data & Dimensions (`INFOOBJECT`)
* **Path 3:** Logic & Transformations (`TRANSFORMATION`)
* **Path 4:** Data Persistence Layer (`ADSO`, legacy `DSO`, legacy `INFOCUBE`)
* **Path 5:** Semantic Models (`COMPOSITE_PROVIDER`, legacy `MULTIPROVIDER`)
* **Path 6:** Analytical Consumption (`BEX_QUERY`)
* **Path 7:** Process Orchestration & Security (`PROCESS_CHAIN`, `ANALYSIS_AUTH`)

---

## 6. Tool T3: Traffic Controller & Wave Handover Engine

### 6.1 Handover Mechanism
1. Tool T3 queries `wave_schedule` and retrieves objects for the active wave index.
2. Evaluates prerequisite locking: Wave $N$ cannot trigger until Wave $N-1$ objects achieve status `GENERATED` (or `DEPLOYED`).
3. Dispatches wave objects in parallel batches to F2 generator tools:
   * Path 1 objects $\rightarrow$ **Tool T4**
   * Path 2 objects $\rightarrow$ **Tool T5**
   * Path 3 objects $\rightarrow$ **Tool T6**
   * Path 4 objects $\rightarrow$ **Tool T7**
   * Path 5 objects $\rightarrow$ **Tool T8**
   * Path 6 objects $\rightarrow$ **Tool T9**
   * Path 7 objects $\rightarrow$ **Tool T10**
4. Updates object status in `metadata_repo.db` from `PENDING` $\rightarrow$ `IN_PROGRESS`.
