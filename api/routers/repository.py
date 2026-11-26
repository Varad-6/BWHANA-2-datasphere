"""Shared Metadata Repository Read API Router."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_db
from repository.db_manager import RepositoryManager

router = APIRouter(prefix="/repository", tags=["Repository"])


@router.get("/objects")
def get_repository_objects(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    migration_path: Optional[str] = None,
    object_type: Optional[str] = None,
    status: Optional[str] = None,
    db: RepositoryManager = Depends(get_db),
) -> Dict[str, Any]:
    """Return filtered and paginated objects from metadata_repo.db."""
    objs = db.get_all_objects()
    if migration_path:
        objs = [o for o in objs if o["migration_path"] == migration_path]
    if object_type:
        objs = [o for o in objs if o["object_type"] == object_type.upper()]
    if status:
        objs = [o for o in objs if o["status"] == status.upper()]

    total = len(objs)
    start = (page - 1) * limit
    items: List[Dict[str, Any]] = objs[start : start + limit]
    return {"total": total, "page": page, "limit": limit, "items": items}


@router.get("/stats")
def get_repository_stats(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Return aggregated repository counts and complexity stats."""
    return db.get_stats()


@router.get("/object/{tech_name}")
def get_repository_object(
    tech_name: str,
    db: RepositoryManager = Depends(get_db),
) -> Dict[str, Any]:
    """Return full metadata for a single technical object."""
    obj = db.get_object(tech_name)
    if not obj:
        raise HTTPException(status_code=404, detail=f"Object '{tech_name}' not found")
    return obj


@router.get("/phases")
def get_all_phases(db: RepositoryManager = Depends(get_db)) -> Dict[str, Any]:
    """Return completion state for all wizard phases (T0, T2, T1, T5-T7)."""
    statuses = db.get_all_phase_statuses()
    ordered_ids = ["T0", "T2", "T1", "T5", "T6", "T7"]
    phases = []
    for pid in ordered_ids:
        entry = statuses.get(pid, {"phase_id": pid, "status": "PENDING", "summary": {}, "updated_at": None})
        phases.append(entry)
    return {"phases": phases}
