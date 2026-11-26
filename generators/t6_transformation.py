"""
T6: Transformation Translator (Path 3)
Converts BW Transformations (Direct, Constant, Formula rules) to Datasphere SQL Views,
and analyzes/transpiles ABAP Start, End, and Field routines into equivalent SQL expressions.
Flags complex unparsed ABAP routines in metadata_repo.db without silent failure.
"""

import json
import re
from typing import Any, Dict, List
from generators.base_generator import BaseCSNGenerator


class TransformationTranslator(BaseCSNGenerator):
    """Transpiles Path 3 BW Transformations and ABAP routines to Datasphere SQL Views."""

    COMPLEX_ABAP_PATTERNS = ("SELECT ", "LOOP AT ", "READ TABLE ", "CALL FUNCTION ", "CALL METHOD ")

    def __init__(self, repo_manager: Any, space_name: str = "") -> None:
        super().__init__(space_name)
        self.repo = repo_manager

    def transpile_abap_to_sql(self, abap_code: str, routine_type: str = "START_ROUTINE") -> Dict[str, Any]:
        """Analyze and transpile common ABAP routine patterns to SQL expressions."""
        sql_clauses: List[str] = []
        warnings: List[str] = []

        if not abap_code:
            return {"sql": "", "warnings": []}

        clean_abap = abap_code.strip()
        upper_abap = clean_abap.upper()

        if any(pat in upper_abap for pat in self.COMPLEX_ABAP_PATTERNS):
            warnings.append(f"Complex ABAP in {routine_type} requiring human review: {clean_abap[:80]}...")
            return {
                "sql": f"/* MANUAL REWORK REQUIRED: {clean_abap} */",
                "warnings": warnings,
            }

        delete_match = re.search(r"DELETE\s+SOURCE_PACKAGE\s+WHERE\s+(.*?)\.", clean_abap, re.IGNORECASE | re.DOTALL)
        if delete_match:
            abap_cond = delete_match.group(1).strip()
            sql_cond = re.sub(r"(\w+)\s+IS\s+INITIAL", r"(\1 IS NULL OR \1 = '')", abap_cond, flags=re.IGNORECASE)
            sql_clauses.append(f"WHERE NOT ({sql_cond})")

        result_match = re.search(r"RESULT\s*=\s*SOURCE_FIELDS-(\w+)\s*(.*?)\.", clean_abap, re.IGNORECASE)
        if result_match:
            field = result_match.group(1)
            expr = result_match.group(2).strip()
            sql_clauses.append(f'("{field}" {expr})' if expr else f'"{field}"')

        if not sql_clauses:
            warnings.append(f"Complex ABAP in {routine_type} requiring human review: {clean_abap[:80]}...")
            sql_clauses.append(f"/* MANUAL REWORK REQUIRED: {clean_abap} */")

        return {
            "sql": "\n".join(sql_clauses),
            "warnings": warnings,
        }

    def convert_formula_to_sql(self, formula_expr: str) -> str:
        """Transpile BW Formula expressions into SQL dialect expressions."""
        if not formula_expr:
            return ""

        expr = formula_expr.strip()

        if_match = re.search(r"IF\s*\((.*?),(.*?),(.*?)\)", expr, re.IGNORECASE)
        if if_match:
            cond, v1, v2 = if_match.group(1).strip(), if_match.group(2).strip(), if_match.group(3).strip()
            return f"CASE WHEN {cond} THEN {v1} ELSE {v2} END"

        concat_match = re.search(r"CONCATENATE\s*\((.*?),(.*?)\)", expr, re.IGNORECASE)
        if concat_match:
            a, b = concat_match.group(1).strip(), concat_match.group(2).strip()
            return f"CONCAT({a}, {b})"

        diff_match = re.search(r"DATE_DIFF\s*\((.*?),(.*?)\)", expr, re.IGNORECASE)
        if diff_match:
            d1, d2 = diff_match.group(1).strip(), diff_match.group(2).strip()
            return f"DAYS_BETWEEN({d2}, {d1})"

        return expr

    def translate_transformation(self, tran_id: str) -> Dict[str, Any]:
        """Convert BW Transformation object into Datasphere SQL View CSN model."""
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

        select_cols: List[str] = []
        elements: Dict[str, Any] = {}
        all_warnings: List[str] = []

        for m in mappings:
            src = m.get("source", "")
            tgt = m.get("target", "")
            rule = m.get("rule", "DIRECT")
            if self.is_sid_field(src) or self.is_sid_field(tgt):
                continue

            if rule == "DIRECT":
                select_cols.append(f'    "{src}" AS "{tgt}"')
            elif rule == "CONSTANT":
                const_val = str(m.get("constant_val", "")).replace("'", "''")
                select_cols.append(f"    '{const_val}' AS \"{tgt}\"")
            elif rule == "FORMULA":
                formula_sql = self.convert_formula_to_sql(m.get("formula_expr", ""))
                select_cols.append(f'    {formula_sql} AS "{tgt}"')

            is_amount = any(tok in str(tgt).upper() for tok in ("AMOUNT", "NET", "VAL", "QTY"))
            elements[tgt] = (
                {"type": "cds.Decimal", "precision": 17, "scale": 2, "@EndUserText.label": tgt}
                if is_amount
                else {"type": "cds.String", "length": 30, "@EndUserText.label": tgt}
            )

        where_clauses: List[str] = []
        for r in routines:
            t_res = self.transpile_abap_to_sql(r.get("abap_code", ""), r.get("routine_type", "ROUTINE"))
            all_warnings.extend(t_res["warnings"])
            if t_res["sql"].startswith("WHERE"):
                where_clauses.append(t_res["sql"])
            elif "MANUAL REWORK REQUIRED" in t_res["sql"]:
                select_cols.append(f"    {t_res['sql']}")

        source_entity = f'"{self.space_name}"."{source_obj}"' if self.space_name else f'"{source_obj}"'
        sql_query = "SELECT\n" + ",\n".join(select_cols) + f"\nFROM {source_entity}"
        if where_clauses:
            sql_query += "\n" + "\n".join(where_clauses)

        view_name = self.qualify_name(f"V_{source_obj}_TO_{target_obj}")
        definitions = {
            view_name: {
                "kind": "entity",
                "@EndUserText.label": f"View for {tran_id} ({source_obj} -> {target_obj})",
                "@Analytics.dataCategory": "#CUBE",
                "elements": elements,
                "query": sql_query,
                "migration_metadata": {
                    "tran_id": tran_id,
                    "rule_type": rule_type,
                    "warnings": all_warnings,
                },
            }
        }

        if hasattr(self.repo, "update_status"):
            warn_code = "COMPLEX_ABAP_ROUTINE" if all_warnings else None
            self.repo.update_status(tran_id, "GENERATED", warning_code=warn_code)

        return {
            "csn": self.create_csn_document(definitions),
            "sql": sql_query,
            "warnings": all_warnings,
        }
