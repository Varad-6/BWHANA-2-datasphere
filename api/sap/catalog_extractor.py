"""SAP S21 Gateway OData Catalog & Metadata Extractor (Read-Only)."""

import xml.etree.ElementTree as ET
from typing import Any, Dict, List
from api.sap.odata_client import SAPODataClient


class SAPCatalogExtractor:
    """Extracts live OData services and EDMX $metadata schemas from SAP S21."""

    CATALOG_PATH = "/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection"

    def __init__(self, client: SAPODataClient) -> None:
        self.client = client

    def fetch_service_catalog(self, max_services: int = 50) -> List[Dict[str, Any]]:
        """Fetch activated OData services from SAP S21 Gateway Catalog."""
        data = self.client.get_json(self.CATALOG_PATH, params={"$top": max_services})
        results = data.get("d", {}).get("results", [])
        return results

    def fetch_service_metadata_fields(self, service_url: str) -> List[Dict[str, Any]]:
        """Fetch $metadata EDMX for a service and extract EntityType properties."""
        if not service_url:
            return []
        meta_path = service_url.rstrip("/") + "/$metadata"
        try:
            resp = self.client.get(
                meta_path,
                headers={"Accept": "application/xml"},
                timeout=10,
            )
            if resp.status_code != 200:
                return []
            root = ET.fromstring(resp.text)
            fields: List[Dict[str, Any]] = []
            for elem in root.iter():
                if elem.tag.endswith("Property"):
                    name = elem.attrib.get("Name", "")
                    edm_type = elem.attrib.get("Type", "Edm.String")
                    max_len = elem.attrib.get("MaxLength", "30")
                    if name and len(fields) < 15:
                        bw_type = self._edm_to_bw_type(edm_type)
                        fields.append({
                            "name": name,
                            "type": bw_type,
                            "length": int(max_len) if str(max_len).isdigit() else 30,
                            "edm_type": edm_type,
                        })
            return fields
        except Exception:
            return []

    @staticmethod
    def _edm_to_bw_type(edm_type: str) -> str:
        """Map OData Edm types to SAP BW dictionary types."""
        mapping = {
            "Edm.String": "CHAR",
            "Edm.DateTime": "DATS",
            "Edm.DateTimeOffset": "DATS",
            "Edm.Time": "TIMS",
            "Edm.Decimal": "CURR",
            "Edm.Int32": "INT4",
            "Edm.Int16": "INT2",
            "Edm.Double": "FLTP",
            "Edm.Binary": "RAW",
        }
        return mapping.get(edm_type, "CHAR")
