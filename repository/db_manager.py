"""Shared Metadata Repository Manager (SQLite / DuckDB) with idempotent migrations."""

import json
import os
import sqlite3
import threading
from typing import Any, Dict, List, Optional, Tuple


class RepositoryManager:
    """Thread-safe metadata repository for BW Morph tools T0-T12."""

    def __init__(self, db_path: str = "metadata_repo.db", use_duckdb: bool = True) -> None:
        self.db_path = db_path
        self.use_duckdb = use_duckdb
        self.local = threading.local()
        self.is_duck = False
        self._create_tables()

    def get_connection(self) -> Any:
        """Return a thread-safe connection dedicated to the calling thread."""
        if not hasattr(self.local, "conn") or self.local.conn is None:
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

    def _create_tables(self) -> None:
        """Create tables from schema.sql and run idempotent column migrations."""
        schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")
        if os.path.exists(schema_file):
            with open(schema_file, "r", encoding="utf-8") as f:
                schema_sql = f.read()

            if not self.is_duck:
                schema_sql = (
                    schema_sql.replace("JSON", "TEXT")
                    .replace("DOUBLE", "REAL")
                    .replace("TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "DATETIME DEFAULT CURRENT_TIMESTAMP")
                )

            statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]
            for stmt in statements:
                self.execute(stmt)

        self._run_idempotent_migrations()

    def _run_idempotent_migrations(self) -> None:
        """Safely add new columns to existing objects tables without data loss."""
        if not self.is_duck:
            rows = self.query_all("PRAGMA table_info(objects)")
            existing_cols = {r[1] for r in rows}
            if "warning_code" not in existing_cols:
                self.execute("ALTER TABLE objects ADD COLUMN warning_code VARCHAR(100)")
            if "wave_id" not in existing_cols:
                self.execute("ALTER TABLE objects ADD COLUMN wave_id INT")
            if "updated_at" not in existing_cols:
                self.execute("ALTER TABLE objects ADD COLUMN updated_at DATETIME")

    def execute(self, query: str, params: Optional[List[Any]] = None) -> Any:
        if params is None:
            params = []
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        if not self.is_duck:
            conn.commit()
        return cursor

    def query_all(self, query: str, params: Optional[List[Any]] = None) -> List[Tuple[Any, ...]]:
        if params is None:
            params = []
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def insert_object(
        self,
        tech_name: str,
        object_type: str,
        description: str = "",
        complexity_score: int = 1,
        migration_path: Optional[str] = None,
        raw_metadata: Optional[Dict[str, Any]] = None,
        status: str = "PENDING",
        warning_code: Optional[str] = None,
        wave_id: Optional[int] = None,
    ) -> None:
        raw_json = json.dumps(raw_metadata) if raw_metadata else "{}"
        query = """
        INSERT OR REPLACE INTO objects
            (tech_name, object_type, description, complexity_score, migration_path, status, warning_code, wave_id, raw_metadata, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        self.execute(
            query,
            [tech_name, object_type, description, complexity_score, migration_path, status, warning_code, wave_id, raw_json],
        )

    def insert_dependency(self, source_obj: str, target_obj: str, dependency_type: str = "DATA_FLOW") -> None:
        dep_id = f"{source_obj}->{target_obj}"
        query = "INSERT OR REPLACE INTO dependencies (id, source_obj, target_obj, dependency_type) VALUES (?, ?, ?, ?)"
        self.execute(query, [dep_id, source_obj, target_obj, dependency_type])

    def insert_transformation(
        self,
        tran_id: str,
        source_obj: str,
        target_obj: str,
        rule_type: str = "DIRECT",
        field_mappings: Optional[List[Dict[str, Any]]] = None,
        routines_abap: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        field_json = json.dumps(field_mappings) if field_mappings else "[]"
        routines_json = json.dumps(routines_abap) if routines_abap else "[]"
        query = """
        INSERT OR REPLACE INTO transformations (tran_id, source_obj, target_obj, rule_type, field_mappings, routines_abap)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.execute(query, [tran_id, source_obj, target_obj, rule_type, field_json, routines_json])

    def _row_to_object(self, r: Tuple[Any, ...]) -> Dict[str, Any]:
        return {
            "tech_name": r[0],
            "object_type": r[1],
            "description": r[2],
            "complexity_score": r[3],
            "migration_path": r[4],
            "status": r[5],
            "warning_code": r[6],
            "wave_id": r[7],
            "raw_metadata": json.loads(r[8]) if isinstance(r[8], str) else (r[8] or {}),
        }

    def get_all_objects(self) -> List[Dict[str, Any]]:
        query = """
        SELECT tech_name, object_type, description, complexity_score, migration_path,
               status, warning_code, wave_id, raw_metadata
        FROM objects
        """
        return [self._row_to_object(r) for r in self.query_all(query)]

    def get_object(self, tech_name: str) -> Optional[Dict[str, Any]]:
        query = """
        SELECT tech_name, object_type, description, complexity_score, migration_path,
               status, warning_code, wave_id, raw_metadata
        FROM objects WHERE tech_name = ?
        """
        rows = self.query_all(query, [tech_name])
        return self._row_to_object(rows[0]) if rows else None

    def get_objects_by_path(self, migration_path: str) -> List[Dict[str, Any]]:
        query = """
        SELECT tech_name, object_type, description, complexity_score, migration_path,
               status, warning_code, wave_id, raw_metadata
        FROM objects WHERE migration_path = ?
        """
        return [self._row_to_object(r) for r in self.query_all(query, [migration_path])]

    def get_objects_by_status(self, status: str) -> List[Dict[str, Any]]:
        query = """
        SELECT tech_name, object_type, description, complexity_score, migration_path,
               status, warning_code, wave_id, raw_metadata
        FROM objects WHERE status = ?
        """
        return [self._row_to_object(r) for r in self.query_all(query, [status])]

    def update_status(
        self,
        tech_name: str,
        status: str,
        warning_code: Optional[str] = None,
        wave_id: Optional[int] = None,
    ) -> None:
        if warning_code is not None and wave_id is not None:
            self.execute(
                "UPDATE objects SET status = ?, warning_code = ?, wave_id = ?, updated_at = CURRENT_TIMESTAMP WHERE tech_name = ?",
                [status, warning_code, wave_id, tech_name],
            )
        elif warning_code is not None:
            self.execute(
                "UPDATE objects SET status = ?, warning_code = ?, updated_at = CURRENT_TIMESTAMP WHERE tech_name = ?",
                [status, warning_code, tech_name],
            )
        elif wave_id is not None:
            self.execute(
                "UPDATE objects SET status = ?, wave_id = ?, updated_at = CURRENT_TIMESTAMP WHERE tech_name = ?",
                [status, wave_id, tech_name],
            )
        else:
            self.execute(
                "UPDATE objects SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE tech_name = ?",
                [status, tech_name],
            )

    def get_stats(self) -> Dict[str, Any]:
        total = self.query_all("SELECT COUNT(*) FROM objects")[0][0]
        by_type = dict(self.query_all("SELECT object_type, COUNT(*) FROM objects GROUP BY object_type"))
        by_path = dict(self.query_all("SELECT COALESCE(migration_path, 'UNASSIGNED'), COUNT(*) FROM objects GROUP BY migration_path"))
        by_status = dict(self.query_all("SELECT status, COUNT(*) FROM objects GROUP BY status"))
        avg_row = self.query_all("SELECT AVG(complexity_score) FROM objects")[0][0]
        deps_count = self.query_all("SELECT COUNT(*) FROM dependencies")[0][0]
        warnings_count = self.query_all("SELECT COUNT(*) FROM objects WHERE warning_code IS NOT NULL")[0][0]
        return {
            "total_objects": total,
            "total_dependencies": deps_count,
            "avg_complexity": round(float(avg_row), 2) if avg_row is not None else 0.0,
            "warnings_count": warnings_count,
            "by_type": by_type,
            "by_path": by_path,
            "by_status": by_status,
        }

    def save_wave_schedule(self, waves: List[Dict[str, Any]]) -> None:
        self.execute("DELETE FROM wave_schedule")
        for w in waves:
            self.execute(
                "INSERT INTO wave_schedule (wave_id, wave_name, objects_count, status) VALUES (?, ?, ?, ?)",
                [w["wave_id"], w["wave_name"], len(w["objects"]), "PLANNED"],
            )
            for obj_name in w["objects"]:
                self.execute("UPDATE objects SET wave_id = ? WHERE tech_name = ?", [w["wave_id"], obj_name])

    def set_phase_status(self, phase_id: str, status: str, summary: Optional[Dict[str, Any]] = None) -> None:
        summary_json = json.dumps(summary or {})
        self.execute(
            "INSERT OR REPLACE INTO phase_status (phase_id, status, summary, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            [phase_id, status, summary_json],
        )

    def get_phase_status(self, phase_id: str) -> Dict[str, Any]:
        rows = self.query_all("SELECT phase_id, status, summary, updated_at FROM phase_status WHERE phase_id = ?", [phase_id])
        if not rows:
            return {"phase_id": phase_id, "status": "PENDING", "summary": {}, "updated_at": None}
        r = rows[0]
        return {
            "phase_id": r[0],
            "status": r[1],
            "summary": json.loads(r[2]) if isinstance(r[2], str) else (r[2] or {}),
            "updated_at": str(r[3]) if r[3] else None,
        }

    def get_all_phase_statuses(self) -> Dict[str, Dict[str, Any]]:
        rows = self.query_all("SELECT phase_id, status, summary, updated_at FROM phase_status")
        return {
            r[0]: {
                "phase_id": r[0],
                "status": r[1],
                "summary": json.loads(r[2]) if isinstance(r[2], str) else (r[2] or {}),
                "updated_at": str(r[3]) if r[3] else None,
            }
            for r in rows
        }

    def get_all_dependencies(self) -> List[Tuple[Any, ...]]:
        return self.query_all("SELECT source_obj, target_obj, dependency_type FROM dependencies")

    def close(self) -> None:
        if hasattr(self.local, "conn") and self.local.conn:
            self.local.conn.close()
            self.local.conn = None
