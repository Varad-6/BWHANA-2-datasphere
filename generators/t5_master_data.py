"""
T5: Master Data Migrator (Path 2)
Converts BW InfoObjects (Characteristics, Key Figures, Attributes, Texts, Compounding)
into SAP Datasphere Local Tables, Dimensions, and Semantic Association metadata.
"""

import json
from generators.base_generator import BaseCSNGenerator

class MasterDataMigrator(BaseCSNGenerator):
    def __init__(self, repo_manager, space_name="SAP_BW_MIGRATION"):
        super().__init__(space_name)
        self.repo = repo_manager

    def convert_infoobject(self, io_tech_name):
        """Converts single InfoObject into native Datasphere CSN entity structure."""
        objects = self.repo.get_all_objects()
        io_obj = next((o for o in objects if o["tech_name"] == io_tech_name), None)

        if not io_obj:
            raise ValueError(f"InfoObject {io_tech_name} not found in metadata repository")

        meta = io_obj.get("raw_metadata", {})
        io_type = meta.get("io_type", "CHA")
        desc = io_obj.get("description", io_tech_name)

        definitions = {}
        entity_name = f"{self.space_name}.{io_tech_name}"

        # Key elements dictionary
        elements = {}

        # Primary Key (InfoObject ID itself)
        elements[io_tech_name] = {
            "key": True,
            **self.map_bw_datatype_to_csn(meta.get("datatype", "CHAR"), meta.get("length", 10)),
            "@EndUserText.label": desc
        }

        # Compounding Keys
        for comp_io in meta.get("compounding", []):
            elements[comp_io] = {
                "key": True,
                "type": "cds.String",
                "length": 10,
                "@EndUserText.label": f"Compounded {comp_io}"
            }

        # Attributes
        associations = {}
        for attr_io in meta.get("attributes", []):
            elements[attr_io] = {
                "type": "cds.String",
                "length": 10,
                "@EndUserText.label": f"Attribute {attr_io}"
            }
            # Add CSN association link
            target_entity = f"{self.space_name}.{attr_io}"
            associations[f"to_{attr_io}"] = {
                "type": "cds.Association",
                "target": target_entity,
                "on": [
                    {"ref": [attr_io]},
                    "=",
                    {"ref": [f"to_{attr_io}", attr_io]}
                ]
            }

        # Combine elements and associations
        elements.update(associations)

        # Build Main Entity
        definitions[entity_name] = {
            "kind": "entity",
            "@EndUserText.label": desc,
            "@Analytics.dataCategory": "#DIMENSION" if io_type == "CHA" else "#MEASURE",
            "elements": elements
        }

        # Generate Text Entity if InfoObject has texts
        if meta.get("has_texts", False):
            text_entity_name = f"{self.space_name}.{io_tech_name}_TEXT"
            text_elements = {
                io_tech_name: {
                    "key": True,
                    **self.map_bw_datatype_to_csn(meta.get("datatype", "CHAR"), meta.get("length", 10)),
                    "@EndUserText.label": desc
                },
                "LANGUAGE_CODE": {
                    "key": True,
                    "type": "cds.String",
                    "length": 2,
                    "@EndUserText.label": "Language"
                },
                "TXTMD": {
                    "type": "cds.String",
                    "length": 60,
                    "@EndUserText.label": "Medium Description"
                },
                "TXTLG": {
                    "type": "cds.String",
                    "length": 100,
                    "@EndUserText.label": "Long Description"
                }
            }

            definitions[text_entity_name] = {
                "kind": "entity",
                "@EndUserText.label": f"Text for {desc}",
                "@Analytics.dataCategory": "#TEXT",
                "elements": text_elements
            }

        return self.create_csn_document(definitions)

    def convert_all_path2_objects(self):
        """Converts all Path 2 (InfoObjects) in repository to CSN definitions."""
        objects = self.repo.get_all_objects()
        path2_objs = [o for o in objects if o.get("migration_path") == "Path 2"]

        combined_definitions = {}
        for o in path2_objs:
            csn_doc = self.convert_infoobject(o["tech_name"])
            combined_definitions.update(csn_doc["definitions"])

        return self.create_csn_document(combined_definitions)
