"""Centralized configuration for BW Morph API loaded from .env."""

from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings sourced from environment variables / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # SAP Inbound (S21)
    sap_ashost: str = "192.168.1.55"
    sap_sysnr: str = "00"
    sap_sid: str = "S21"
    sap_client: str = "200"
    sap_user: str = "INT_SAMARTH"
    sap_password: str = ""
    sap_rfc_port: int = 3300
    sap_http_port: int = 8000
    sap_https_port: int = 44300
    sap_read_only: bool = True

    # Repository
    repository_type: str = "sqlite"
    repository_db_path: str = "metadata_repo.db"

    # Reconciliation
    reconciliation_tolerance: float = 0.01
    reconciliation_sample_rows: int = 10000

    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8001

    @field_validator("sap_read_only")
    @classmethod
    def enforce_sap_read_only(cls, v: bool) -> bool:
        """Hard stop if SAP_READ_ONLY is disabled."""
        if not v:
            raise ValueError("SAP_READ_ONLY must remain True for system safety.")
        return v


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()
