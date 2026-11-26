"""Unit and integration tests for Phase 1 FastAPI Health & Config."""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.config import Settings


def test_settings_enforces_read_only():
    with pytest.raises(ValueError, match="SAP_READ_ONLY"):
        Settings(sap_read_only=False)


def test_health_endpoint():
    client = TestClient(app)
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["db_connected"] is True
    assert data["sap_read_only"] is True
    assert data["sap_sid"] == "S21"
    assert data["sap_host"] == "192.168.1.55"
