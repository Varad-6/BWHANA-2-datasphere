"""
T7: DSO / ADSO Table Generator (Path 4)
Generates Datasphere Local Table and View CSN definitions from ADSO Key/Data field structures.
"""

from generators.base_generator import BaseCSNGenerator

class ADSODataMigrator(BaseCSNGenerator):
    def __init__(self, repo_manager, space_name="SAP_BW_MIGRATION"):
        super().__init__(space_name)
        self.repo = repo_manager

    def convert_adso(self, adso_tech_name):
        """Converts ADSO definition into Datasphere CSN Local Table."""
        objects = self.repo.get_all_objects()
        adso_obj = next((o for o in objects if o["tech_name"] == adso_tech_name), None)

        if not adso_obj:
            raise ValueError(f"ADSO {adso_tech_name} not found")

        meta = adso_obj.get("raw_metadata", {})
        keys = meta.get("keys", [])
        fields = meta.get("fields", [])
        desc = adso_obj.get("description", adso_tech_name)

        elements = {}
        for k in keys:
            elements[k] = {
                "key": True,
                "type": "cds.String",
                "length": 30,
                "@EndUserText.label": f"Key Field {k}"
            }

        for f in fields:
            elements[f] = {
                "type": "cds.Decimal" if "AMOUNT" in f or "NET" in f else "cds.String",
                "precision": 17 if "AMOUNT" in f or "NET" in f else 0,
                "scale": 2 if "AMOUNT" in f or "NET" in f else 0,
                "length": 30 if "AMOUNT" not in f and "NET" not in f else 0,
                "@EndUserText.label": f"Data Field {f}"
            }

        entity_name = f"{self.space_name}.{adso_tech_name}"
        definitions = {
            entity_name: {
                "kind": "entity",
                "@EndUserText.label": desc,
                "@Analytics.dataCategory": "#FACT" if meta.get("adso_type") == "STANDARD" else "#STAGING",
                "elements": elements
            }
        }

        return self.create_csn_document(definitions)
