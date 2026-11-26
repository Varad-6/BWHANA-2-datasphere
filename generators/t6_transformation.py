"""
T6: Transformation Translator (Path 3)
Converts BW Transformations (Direct, Constant, Formula rules) to Datasphere SQL Views / Data Flows,
and analyzes/transpiles ABAP Start, End, and Field routines into equivalent SQL expressions.
"""

import re
import json
from generators.base_generator import BaseCSNGenerator

class TransformationTranslator(BaseCSNGenerator):
    def __init__(self, repo_manager, space_name="SAP_BW_MIGRATION"):
        super().__init__(space_name)
        self.repo = repo_manager

    def transpile_abap_to_sql(self, abap_code, routine_type="START_ROUTINE"):
        """Analyzes and transpiles common ABAP routine patterns to SQL expressions."""
        sql_clauses = []
        warnings = []

        if not abap_code:
            return {"sql": "", "warnings": []}

        clean_abap = abap_code.strip()

        # 1. Parse DELETE SOURCE_PACKAGE WHERE ...
        delete_match = re.search(r"DELETE\s+SOURCE_PACKAGE\s+WHERE\s+(.*?)\.", clean_abap, re.IGNORECASE)
        if delete_match:
            abap_cond = delete_match.group(1).strip()
            # Convert IS INITIAL -> IS NULL OR ''
            sql_cond = re.sub(r"(\w+)\s+IS\s+INITIAL", r"(\1 IS NULL OR \1 = '')", abap_cond, flags=re.IGNORECASE)
            sql_clauses.append(f"WHERE NOT ({sql_cond})")

        # 2. Parse RESULT = SOURCE_FIELDS-...
        result_match = re.search(r"RESULT\s*=\s*SOURCE_FIELDS-(\w+)\s*(.*?)\.", clean_abap, re.IGNORECASE)
        if result_match:
            field = result_match.group(1)
            expr = result_match.group(2).strip()
            sql_clauses.append(f"CALCULATION: {field} {expr}")

        if not sql_clauses:
            warnings.append(f"Complex ABAP in {routine_type} requiring human review: {clean_abap[:80]}...")
            sql_clauses.append(f"/* MANUAL REWORK REQUIRED: {clean_abap} */")

        return {
            "sql": "\n".join(sql_clauses),
            "warnings": warnings
        }

    def convert_formula_to_sql(self, formula_expr):
        """Transpiles BW Formula expressions into SQL dialect expressions."""
        if not formula_expr:
            return ""

        # Convert IF(cond, val1, val2) -> CASE WHEN cond THEN val1 ELSE val2 END
        if_match = re.search(r"IF\s*\((.*?),(.*?),(.*?)\)", formula_expr, re.IGNORECASE)
        if if_match:
            cond, v1, v2 = if_match.group(1).strip(), if_match.group(2).strip(), if_match.group(3).strip()
            return f"CASE WHEN {cond} THEN {v1} ELSE {v2} END"

        return formula_expr

    def translate_transformation(self, tran_id):
        """Converts BW Transformation object into Datasphere SQL View CSN model."""
        query = "SELECT tran_id, source_obj, target_obj, rule_type, field_mappings, routines_abap FROM transformations WHERE tran_id = ?"
        rows = self.repo.query_all(query, [tran_id])

        if not rows:
            raise ValueError(f"Transformation {tran_id} not found")

        row = rows[0]
        source_obj = row[1]
        target_obj = row[2]
        rule_type = row[3]
        mappings = json.loads(row[4]) if isinstance(row[4], str) else row[4]
        routines = json.loads(row[5]) if isinstance(row[5], str) else row[5]

        select_cols = []
        all_warnings = []

        # 1. Process Field Mappings
        for m in mappings:
            src = m.get("source")
            tgt = m.get("target")
            rule = m.get("rule", "DIRECT")

            if rule == "DIRECT":
                select_cols.append(f'    "{src}" AS "{tgt}"')
            elif rule == "CONSTANT":
                const_val = m.get("constant_val", "")
                select_cols.append(f'    \'{const_val}\' AS "{tgt}"')
            elif rule == "FORMULA":
                formula_sql = self.convert_formula_to_sql(m.get("formula_expr", ""))
                select_cols.append(f'    {formula_sql} AS "{tgt}"')

        # 2. Process ABAP Routines
        where_clause = ""
        for r in routines:
            t_res = self.transpile_abap_to_sql(r.get("abap_code", ""), r.get("routine_type", "ROUTINE"))
            all_warnings.extend(t_res["warnings"])
            if "WHERE" in t_res["sql"]:
                where_clause = t_res["sql"]

        # Build SQL Statement
        source_entity = f'"{self.space_name}"."{source_obj}"'
        sql_query = f"SELECT\n" + ",\n".join(select_cols) + f"\nFROM {source_entity}"
        if where_clause:
            sql_query += f"\n{where_clause}"

        view_name = f"{self.space_name}.V_{source_obj}_TO_{target_obj}"
        definitions = {
            view_name: {
                "kind": "entity",
                "@EndUserText.label": f"View for {tran_id} ({source_obj} -> {target_obj})",
                "@Analytics.dataCategory": "#CUBE",
                "query": sql_query,
                "migration_metadata": {
                    "tran_id": tran_id,
                    "rule_type": rule_type,
                    "warnings": all_warnings
                }
            }
        }

        return {
            "csn": self.create_csn_document(definitions),
            "sql": sql_query,
            "warnings": all_warnings
        }
