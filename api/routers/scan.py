"""T0 Live Scan Router (SAP S21 Read-Only Extraction)."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query

from api.config import Settings, get_settings
from api.dependencies import get_db
from api.sap.odata_client import SAPODataClient
from extractors.t0_bw_scanner import BWInventoryScanner
from repository.db_manager import RepositoryManager

router = APIRouter(prefix="/scan", tags=["T0: Scanner"])


@router.get("/start")
def start_scan(
    mode: str = Query("live", pattern="^(live|sample)$"),
    limit: int = Query(30, ge=5, le=200),
    settings: Settings = Depends(get_settings),
    db: RepositoryManager = Depends(get_db),
) -> Dict[str, Any]:
    """Run T0 inventory scan (live SAP S21 OData by default) and persist phase state."""
    db.set_phase_status("T0", "RUNNING")
    scanner = BWInventoryScanner(db)
    try:
        if mode == "live":
            client = SAPODataClient(settings)
            counts = scanner.scan_live_s21(client, max_services=limit)
        else:
            counts = scanner.scan_sample_metadata()

        summary = {
            "mode": mode,
            "counts": counts,
            "total_scanned": sum(counts.values()),
            "sap_sid": settings.sap_sid,
        }
        db.set_phase_status("T0", "COMPLETED", summary=summary)
        return {"phase": "T0", "status": "completed", **summary}
    except Exception as exc:
        db.set_phase_status("T0", "ERROR", summary={"error": str(exc)})
        raise


@router.get("/status")
def get_scan_status(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Return persisted T0 scan status and summary."""
    phase = db.get_phase_status("T0")
    stats = db.get_stats()
    return {
        "phase": "T0",
        "status": phase["status"].lower(),
        "summary": phase["summary"],
        "total_objects": stats["total_objects"],
        "updated_at": phase["updated_at"],
    }


@router.get("/objects")
def list_scanned_objects(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    object_type: Optional[str] = None,
    db: RepositoryManager = Depends(get_db),
) -> Dict[str, Any]:
    """Return paginated list of scanned objects."""
    all_objs = db.get_all_objects()
    if object_type:
        all_objs = [o for o in all_objs if o["object_type"] == object_type.upper()]

    total = len(all_objs)
    start = (page - 1) * limit
    items: List[Dict[str, Any]] = all_objs[start : start + limit]
    return {"total": total, "page": page, "limit": limit, "items": items}
