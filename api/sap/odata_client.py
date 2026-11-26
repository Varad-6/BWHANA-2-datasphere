"""Thread-safe SAP OData HTTP Client with Strict Read-Only Enforcement."""

import logging
import time
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from api.config import Settings

logger = logging.getLogger("bw_morph.sap.odata")


class SAPReadOnlyViolationError(RuntimeError):
    """Raised when a mutating HTTP method is attempted against SAP."""


class SAPODataClient:
    """Thread-safe HTTP client for SAP S21 OData/ICF endpoints (GET/HEAD only)."""

    ALLOWED_METHODS = frozenset({"GET", "HEAD"})

    def __init__(self, settings: Settings) -> None:
        if not settings.sap_read_only:
            raise SAPReadOnlyViolationError("SAP_READ_ONLY must be True.")
        self.settings = settings
        self.base_url = f"http://{settings.sap_ashost}:{settings.sap_http_port}"
        self.session = requests.Session()
        self.session.auth = (settings.sap_user, settings.sap_password)
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "BW-Morph-Migration-Accelerator/1.0",
        })
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[502, 503, 504],
            allowed_methods=["GET", "HEAD"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _assert_read_only(self, method: str) -> None:
        """Enforce strict read-only policy before any network call."""
        upper = method.upper().strip()
        if upper not in self.ALLOWED_METHODS or not self.settings.sap_read_only:
            raise SAPReadOnlyViolationError(
                f"SAP_READ_ONLY: Mutating HTTP method '{upper}' is strictly blocked on {self.settings.sap_sid}."
            )

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 15,
    ) -> requests.Response:
        """Execute a strictly read-only HTTP GET request against SAP S21."""
        self._assert_read_only("GET")
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        query_params = dict(params or {})
        query_params.setdefault("sap-client", self.settings.sap_client)

        start = time.monotonic()
        resp = self.session.get(url, params=query_params, headers=headers, timeout=timeout)
        elapsed_ms = (time.monotonic() - start) * 1000.0
        logger.info("SAP GET %s -> %s (%.1f ms)", path, resp.status_code, elapsed_ms)
        return resp

    def get_json(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 15,
    ) -> Dict[str, Any]:
        """Execute GET with $format=json and return parsed JSON."""
        query_params = dict(params or {})
        query_params.setdefault("$format", "json")
        resp = self.get(path, params=query_params, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        """Override generic request to block all non-GET/HEAD verbs."""
        self._assert_read_only(method)
        if method.upper() == "HEAD":
            url = path if path.startswith("http") else f"{self.base_url}{path}"
            return self.session.head(url, **kwargs)
        return self.get(path, **kwargs)
