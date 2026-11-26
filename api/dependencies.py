"""FastAPI dependency injection providers."""

from functools import lru_cache
from fastapi import Depends
from api.config import Settings, get_settings
from repository.db_manager import RepositoryManager


@lru_cache()
def _get_repo_singleton(db_path: str, use_duckdb: bool) -> RepositoryManager:
    """Create and cache the shared RepositoryManager instance."""
    return RepositoryManager(db_path=db_path, use_duckdb=use_duckdb)


def get_db(settings: Settings = Depends(get_settings)) -> RepositoryManager:
    """Provide the shared thread-safe RepositoryManager instance."""
    use_duck = settings.repository_type.lower() == "duckdb"
    return _get_repo_singleton(settings.repository_db_path, use_duck)
