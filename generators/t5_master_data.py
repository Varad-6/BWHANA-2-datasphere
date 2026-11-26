"""
T5: Master Data Migrator (Path 2)
Converts BW InfoObjects (Characteristics, Key Figures, Attributes, Texts, Compounding)
into SAP Datasphere Local Tables, Dimensions, and Semantic Association metadata.
Enforces SID suppression and composite primary keys for compounded InfoObjects.
"""

from typing import Any, Dict
from generators.base_generator import BaseCSNGenerator


class MasterDataMigrator(BaseCSNGenerator):
    """Converts Path 2 InfoObjects into SAP CSN v1.0 Dimension & Text entities."""

    def __init__(self, repo_manager: Any, space_name: str = "") -> None:
        super().__init__(space_name)
        self.repo = repo_manager

    def convert_infoobject(self, io_tech_name: str) -> Dict[str, Any]:
        """Convert single InfoObject into native Datasphere CSN entity structure."""
        io_obj = self.repo.get_object(io_tech_name) if hasattr(self.repo, "get_object") else next(
            (o for o in self.repo.get_all_objects() if o["tech_name"] == io_tech_name), None
        )
        if not io_obj:
            raise ValueError(f"InfoObject {io_tech_name} not found in metadata repository")

        meta = io_obj.get("raw_metadata", {})
        io_type = meta.get("io_type", "CHA")
        desc = io_obj.get("description", io_tech_name)

        definitions: Dict[str, Any] = {}
        entity_name = self.qualify_name(io_tech_name)
        elements: Dict[str, Any] = {}

        # Primary Key (InfoObject natural business key — never SID)
        elements[io_tech_name] = {
            "key": True,
            **self.map_bw_datatype_to_csn(meta.get("datatype", "CHAR"), meta.get("length", 10)),
            "@EndUserText.label": desc,
        }

        # Compounding Keys -> enforced as composite primary keys
        for comp_io in meta.get("compounding", []):
            if self.is_sid_field(comp_io):
                continue
            elements[comp_io] = {
                "key": True,
                "type": "cds.String",
                "length": 10,
                "@EndUserText.label": f"Compounded {comp_io}",
            }

        # Attributes & Semantic Associations
        associations: Dict[str, Any] = {}
        for attr_io in meta.get("attributes", []):
            if self.is_sid_field(attr_io):
                continue
            elements[attr_io] = {
                "type": "cds.String",
                "length": 10,
                "@EndUserText.label": f"Attribute {attr_io}",
            }
            target_entity = self.qualify_name(attr_io)
            associations[f"to_{attr_io}"] = {
                "type": "cds.Association",
                "target": target_entity,
                "on": [
                    {"ref": [attr_io]},
                    "=",
                    {"ref": [f"to_{attr_io}", attr_io]},
                ],
            }

        # Extra live fields from S21 OData $metadata if present (excluding SIDs)
        for f in meta.get("fields", []):
            fname = f.get("name", "")
            if not fname or fname in elements or self.is_sid_field(fname):
                continue
            elements[fname] = {
                **self.map_bw_datatype_to_csn(f.get("type", "CHAR"), f.get("length", 30), f.get("decimals", 0)),
                "@EndUserText.label": fname,
            }

        elements.update(associations)

        definitions[entity_name] = {
            "kind": "entity",
            "@EndUserText.label": desc,
            "@Analytics.dataCategory": "#DIMENSION" if io_type == "CHA" else "#MEASURE",
            "elements": elements,
        }

        # Time-dependent attribute entity if flagged
        if meta.get("has_time_dependent", False):
            td_name = self.qualify_name(f"{io_tech_name}_ATTR_TD")
            definitions[td_name] = {
                "kind": "entity",
                "@EndUserText.label": f"Time-Dependent Attributes for {desc}",
                "@Analytics.dataCategory": "#DIMENSION",
                "elements": {
                    io_tech_name: {
                        "key": True,
                        **self.map_bw_datatype_to_csn(meta.get("datatype", "CHAR"), meta.get("length", 10)),
                    },
                    "DATE_FROM": {"key": True, "type": "cds.Date", "@Semantics.businessDate.from": True},
                    "DATE_TO": {"key": True, "type": "cds.Date", "@Semantics.businessDate.to": True},
                },
            }

        # Text Entity
        if meta.get("has_texts", False):
            text_entity_name = self.qualify_name(f"{io_tech_name}_TEXT")
            text_elements = {
                io_tech_name: {
                    "key": True,
                    **self.map_bw_datatype_to_csn(meta.get("datatype", "CHAR"), meta.get("length", 10)),
                    "@EndUserText.label": desc,
                },
                "LANGUAGE_CODE": {
                    "key": True,
                    "type": "cds.String",
                    "length": 2,
                    "@EndUserText.label": "Language",
                },
                "TXTSH": {"type": "cds.String", "length": 20, "@EndUserText.label": "Short Description"},
                "TXTMD": {"type": "cds.String", "length": 60, "@EndUserText.label": "Medium Description"},
                "TXTLG": {"type": "cds.String", "length": 100, "@EndUserText.label": "Long Description"},
            }
            definitions[text_entity_name] = {
                "kind": "entity",
                "@EndUserText.label": f"Text for {desc}",
                "@Analytics.dataCategory": "#TEXT",
                "elements": text_elements,
            }

        if hasattr(self.repo, "update_status"):
            self.repo.update_status(io_tech_name, "GENERATED")

        return self.create_csn_document(definitions)

    def convert_all_path2_objects(self) -> Dict[str, Any]:
        """Convert all Path 2 (InfoObjects) in repository to CSN definitions."""
        objects = self.repo.get_all_objects()
        path2_objs = [o for o in objects if o.get("migration_path") == "Path 2"]

        combined_definitions: Dict[str, Any] = {}
        for o in path2_objs:
            csn_doc = self.convert_infoobject(o["tech_name"])
            combined_definitions.update(csn_doc["definitions"])

        return self.create_csn_document(combined_definitions)
