"""
T7: DSO / ADSO Table Generator (Path 4)
Generates Datasphere Local Table and Audit Change Log View CSN definitions
from ADSO Key/Data field structures, respecting *1 (Inbound), *2 (Active), *3 (Change Log).
"""

from typing import Any, Dict
from generators.base_generator import BaseCSNGenerator


class ADSODataMigrator(BaseCSNGenerator):
    """Converts Path 4 ADSOs into Datasphere CSN Local Tables and Change Log Views."""

    def __init__(self, repo_manager: Any, space_name: str = "") -> None:
        super().__init__(space_name)
        self.repo = repo_manager

    def convert_adso(self, adso_tech_name: str) -> Dict[str, Any]:
        """Convert ADSO definition into Datasphere CSN Local Table + optional Change Log view."""
        adso_obj = self.repo.get_object(adso_tech_name) if hasattr(self.repo, "get_object") else next(
            (o for o in self.repo.get_all_objects() if o["tech_name"] == adso_tech_name), None
        )
        if not adso_obj:
            raise ValueError(f"ADSO {adso_tech_name} not found")

        meta = adso_obj.get("raw_metadata", {})
        keys = meta.get("keys", [])
        fields = meta.get("fields", [])
        desc = adso_obj.get("description", adso_tech_name)
        adso_type = meta.get("adso_type", "STANDARD")

        elements: Dict[str, Any] = {}
        for k in keys:
            if self.is_sid_field(k):
                continue
            elements[k] = {
                "key": True,
                "type": "cds.String",
                "length": 30,
                "@EndUserText.label": f"Key Field {k}",
            }

        for f in fields:
            if self.is_sid_field(f) or f in elements:
                continue
            is_amount = any(tok in f.upper() for tok in ("AMOUNT", "NET", "VAL", "QTY", "QUANT"))
            if is_amount:
                elements[f] = {
                    "type": "cds.Decimal",
                    "precision": 17,
                    "scale": 2,
                    "@EndUserText.label": f"Data Field {f}",
                }
            else:
                elements[f] = {
                    "type": "cds.String",
                    "length": 30,
                    "@EndUserText.label": f"Data Field {f}",
                }

        entity_name = self.qualify_name(adso_tech_name)
        definitions: Dict[str, Any] = {
            entity_name: {
                "kind": "entity",
                "@EndUserText.label": desc,
                "@Analytics.dataCategory": "#FACT" if adso_type == "STANDARD" else "#STAGING",
                "elements": elements,
            }
        }

        if adso_type == "STANDARD":
            cl_elements = dict(elements)
            cl_elements["RECORDMODE"] = {
                "type": "cds.String",
                "length": 1,
                "@EndUserText.label": "BW Delta Record Mode",
            }
            definitions[self.qualify_name(f"{adso_tech_name}_CHANGELOG")] = {
                "kind": "entity",
                "@EndUserText.label": f"Change Log Audit for {desc}",
                "elements": cl_elements,
            }

        if hasattr(self.repo, "update_status"):
            self.repo.update_status(adso_tech_name, "GENERATED")

        return self.create_csn_document(definitions)
