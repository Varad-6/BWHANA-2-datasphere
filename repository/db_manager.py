import sqlite3
import json
import os
import threading

class RepositoryManager:
    def __init__(self, db_path="metadata_repo.db", use_duckdb=True):
        self.db_path = db_path
        self.use_duckdb = use_duckdb
        self.local = threading.local()
        self.is_duck = False
        self._create_tables()

    def get_connection(self):
        """Returns a thread-safe connection dedicated to the calling thread."""
        if not hasattr(self.local, 'conn') or self.local.conn is None:
            if self.use_duckdb:
                try:
                    import duckdb
                    self.local.conn = duckdb.connect(self.db_path)
                    self.is_duck = True
                except Exception:
                    self.local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
                    self.is_duck = False
            else:
                self.local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
                self.is_duck = False
        return self.local.conn

    def _create_tables(self):
        schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")
        if os.path.exists(schema_file):
            with open(schema_file, "r", encoding="utf-8") as f:
                schema_sql = f.read()

            if not self.is_duck:
                schema_sql = schema_sql.replace("JSON", "TEXT").replace("DOUBLE", "REAL").replace("TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "DATETIME DEFAULT CURRENT_TIMESTAMP")

            statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]
            for stmt in statements:
                self.execute(stmt)

    def execute(self, query, params=None):
        if params is None:
            params = []
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        if not self.is_duck:
            conn.commit()
        return cursor

    def query_all(self, query, params=None):
        if params is None:
            params = []
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def insert_object(self, tech_name, object_type, description="", complexity_score=1, migration_path=None, raw_metadata=None):
        raw_json = json.dumps(raw_metadata) if raw_metadata else "{}"
        query = """
        INSERT OR REPLACE INTO objects (tech_name, object_type, description, complexity_score, migration_path, status, raw_metadata)
        VALUES (?, ?, ?, ?, ?, 'PENDING', ?)
        """
        self.execute(query, [tech_name, object_type, description, complexity_score, migration_path, raw_json])

    def insert_dependency(self, source_obj, target_obj, dependency_type="DATA_FLOW"):
        dep_id = f"{source_obj}->{target_obj}"
        query = "INSERT OR REPLACE INTO dependencies (id, source_obj, target_obj, dependency_type) VALUES (?, ?, ?, ?)"
        self.execute(query, [dep_id, source_obj, target_obj, dependency_type])

    def insert_transformation(self, tran_id, source_obj, target_obj, rule_type="DIRECT", field_mappings=None, routines_abap=None):
        field_json = json.dumps(field_mappings) if field_mappings else "[]"
        routines_json = json.dumps(routines_abap) if routines_abap else "[]"
        query = """
        INSERT OR REPLACE INTO transformations (tran_id, source_obj, target_obj, rule_type, field_mappings, routines_abap)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.execute(query, [tran_id, source_obj, target_obj, rule_type, field_json, routines_json])

    def get_all_objects(self):
        query = "SELECT tech_name, object_type, description, complexity_score, migration_path, status, raw_metadata FROM objects"
        rows = self.query_all(query)
        result = []
        for r in rows:
            result.append({
                "tech_name": r[0],
                "object_type": r[1],
                "description": r[2],
                "complexity_score": r[3],
                "migration_path": r[4],
                "status": r[5],
                "raw_metadata": json.loads(r[6]) if isinstance(r[6], str) else r[6]
            })
        return result

    def get_all_dependencies(self):
        query = "SELECT source_obj, target_obj, dependency_type FROM dependencies"
        return self.query_all(query)

    def close(self):
        if hasattr(self.local, 'conn') and self.local.conn:
            self.local.conn.close()
            self.local.conn = None
