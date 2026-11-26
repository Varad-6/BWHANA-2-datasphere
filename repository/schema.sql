-- Schema definition for BW/4HANA to SAP Datasphere Shared Metadata Repository

CREATE TABLE IF NOT EXISTS objects (
    tech_name VARCHAR(100) PRIMARY KEY,
    object_type VARCHAR(50) NOT NULL, -- INFOOBJECT, ADSO, COMPOSITE_PROVIDER, BEX_QUERY, TRANSFORMATION, DTP, PROCESS_CHAIN, SOURCE_SYSTEM
    description VARCHAR(255),
    complexity_score INT DEFAULT 1,
    migration_path VARCHAR(20), -- Path 1 to Path 7
    status VARCHAR(50) DEFAULT 'PENDING', -- PENDING, IN_PROGRESS, GENERATED, DEPLOYED, VALIDATED, FAILED
    raw_metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dependencies (
    id VARCHAR(100) PRIMARY KEY,
    source_obj VARCHAR(100) NOT NULL,
    target_obj VARCHAR(100) NOT NULL,
    dependency_type VARCHAR(50), -- DATA_FLOW, USES_MASTER_DATA, QUERIES_PROVIDER
    FOREIGN KEY (source_obj) REFERENCES objects(tech_name),
    FOREIGN KEY (target_obj) REFERENCES objects(tech_name)
);

CREATE TABLE IF NOT EXISTS transformations (
    tran_id VARCHAR(100) PRIMARY KEY,
    source_obj VARCHAR(100) NOT NULL,
    target_obj VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50), -- DIRECT, CONSTANT, FORMULA, ROUTINE
    field_mappings JSON,
    routines_abap JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wave_schedule (
    wave_id INT PRIMARY KEY,
    wave_name VARCHAR(100),
    objects_count INT,
    status VARCHAR(50) DEFAULT 'PLANNED'
);

CREATE TABLE IF NOT EXISTS reconciliation_results (
    id VARCHAR(100) PRIMARY KEY,
    tech_name VARCHAR(100),
    source_row_count BIGINT,
    target_row_count BIGINT,
    variance_percentage DOUBLE,
    status VARCHAR(20), -- PASS, FAIL, WARNING
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
