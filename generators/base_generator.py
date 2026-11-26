"""
Base Generator for SAP Datasphere Core Schema Notation (CSN / JSON)
Provides standard JSON metadata builder compliant with SAP CSN v1.0 Specification.
"""

from typing import Any, Dict


class BaseCSNGenerator:
    """Base CSN v1.0 builder and SAP BW-to-CDS type mapper."""

    SID_PREFIXES = ("/BI0/S", "/BI0/X", "/BI0/Y", "/BIC/S", "/BIC/X", "/BIC/Y")

    def __init__(self, space_name: str = "") -> None:
        self.space_name = self.validate_namespace(space_name)

    @staticmethod
    def validate_namespace(space_name: str) -> str:
        """Reject SAP-reserved namespaces (SAP_*) that fail Datasphere Space import."""
        cleaned = (space_name or "").strip()
        if cleaned.upper().startswith("SAP_"):
            raise ValueError(
                f"Namespace '{cleaned}' is reserved by SAP. Leave namespace empty for Active Space import or use a custom non-SAP_ prefix."
            )
        return cleaned

    def qualify_name(self, object_name: str) -> str:
        """Return namespace-qualified name if custom namespace is set, else unprefixed object name."""
        return f"{self.space_name}.{object_name}" if self.space_name else object_name

    @classmethod
    def is_sid_field(cls, field_name: str) -> bool:
        """Return True if field_name is a BW integer surrogate key (SID) that must be suppressed."""
        upper = field_name.upper().strip()
        if any(upper.startswith(p) for p in cls.SID_PREFIXES):
            return True
        if upper == "SID" or upper.endswith("_SID"):
            return True
        return False

    def create_csn_document(self, definitions: Dict[str, Any]) -> Dict[str, Any]:
        """Wrap definitions dictionary into valid SAP CSN v1.0 document format."""
        return {
            "$schema": "https://sap.com/csn/v1",
            "meta": {
                "creator": "BW4HANA-Datasphere-Migration-Accelerator",
                "version": "1.0.0",
            },
            "definitions": definitions,
        }

    def map_bw_datatype_to_csn(self, bw_type: str, length: int = 0, decimals: int = 0) -> Dict[str, Any]:
        """Map SAP BW Data Types to CSN Data Types."""
        bw_type = bw_type.upper().strip()
        if bw_type in ["CHAR", "UNIT", "CUKY"]:
            return {"type": "cds.String", "length": length if length > 0 else 100}
        if bw_type == "NUMC":
            return {"type": "cds.String", "length": length if length > 0 else 10}
        if bw_type == "DATS":
            return {"type": "cds.Date"}
        if bw_type == "TIMS":
            return {"type": "cds.Time"}
        if bw_type in ["DEC", "CURR", "QUAN"]:
            return {"type": "cds.Decimal", "precision": length if length > 0 else 17, "scale": decimals}
        if bw_type in ["INT4", "INT2", "INT8"]:
            return {"type": "cds.Integer"}
        if bw_type in ["FLTP"]:
            return {"type": "cds.Double"}
        if bw_type in ["RAW", "RAWSTRING"]:
            return {"type": "cds.Binary"}
        if bw_type in ["LCHR", "STRG", "STRING"]:
            return {"type": "cds.LargeString"}
        return {"type": "cds.String", "length": 255}
