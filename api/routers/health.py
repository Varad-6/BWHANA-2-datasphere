"""Health check router for BW Morph API."""

import socket
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.config import Settings, get_settings
from api.dependencies import get_db
from repository.db_manager import RepositoryManager

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Schema for /api/v1/health response."""

    status: str
    service: str
    version: str
    db_connected: bool
    sap_host: str
    sap_sid: str
    sap_read_only: bool
    sap_reachable: bool
    timestamp: str


def _check_tcp_reachable(host: str, port: int, timeout: float = 2.0) -> bool:
    """Non-intrusive TCP port check to verify SAP host reachability."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@router.get("/health", response_model=HealthResponse)
def health_check(
    settings: Settings = Depends(get_settings),
    db: RepositoryManager = Depends(get_db),
) -> HealthResponse:
    """Return API, database, and SAP S21 reachability status."""
    db_ok = False
    try:
        rows = db.query_all("SELECT 1")
        db_ok = bool(rows and rows[0][0] == 1)
    except Exception:
        db_ok = False

    sap_ok = _check_tcp_reachable(settings.sap_ashost, settings.sap_http_port)

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        service="BW Morph Migration Accelerator API",
        version="1.0.0",
        db_connected=db_ok,
        sap_host=settings.sap_ashost,
        sap_sid=settings.sap_sid,
        sap_read_only=settings.sap_read_only,
        sap_reachable=sap_ok,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
