"""
Base Generator for SAP Datasphere Core Schema Notation (CSN / JSON)
Provides standard JSON metadata builder compliant with SAP CSN Specification.
"""

import json

class BaseCSNGenerator:
    def __init__(self, space_name="SAP_BW_MIGRATION"):
        self.space_name = space_name

    def create_csn_document(self, definitions):
        """Wraps definitions dictionary into valid SAP CSN document format."""
        return {
            "$schema": "https://sap.com/csn/v1",
            "meta": {
                "creator": "BW4HANA-Datasphere-Migration-Accelerator",
                "version": "1.0.0"
            },
            "definitions": definitions
        }

    def map_bw_datatype_to_csn(self, bw_type, length=0, decimals=0):
        """Maps SAP BW Data Types (CHAR, DATS, NUMC, DEC, CURR, QUAN) to CSN Data Types."""
        bw_type = bw_type.upper()
        if bw_type in ["CHAR", "UNIT", "CUKY"]:
            return {"type": "cds.String", "length": length if length > 0 else 100}
        elif bw_type == "NUMC":
            return {"type": "cds.String", "length": length if length > 0 else 10}
        elif bw_type == "DATS":
            return {"type": "cds.Date"}
        elif bw_type == "TIMS":
            return {"type": "cds.Time"}
        elif bw_type in ["DEC", "CURR", "QUAN"]:
            return {"type": "cds.Decimal", "precision": length if length > 0 else 17, "scale": decimals}
        elif bw_type in ["INT4", "INT2"]:
            return {"type": "cds.Integer"}
        else:
            return {"type": "cds.String", "length": 255}
