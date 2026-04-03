"""OpenDesktop OCS API integration."""

from __future__ import annotations

import json
from typing import Any

import requests

from app.models.theme import Theme
from app.utils.cache import JsonCache
from app.utils.config import Settings


class OCSClient:
    """HTTP client for OpenDesktop OCS content API."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "OCS-APIREQUEST": "true",
                "User-Agent": f"{Settings.APP_NAME}/{Settings.APP_VERSION}",
            }
        )
        self.cache = JsonCache()

    def _cache_key(self, endpoint: str, params: dict[str, Any]) -> str:
        return f"{endpoint}:{json.dumps(params, sort_keys=True)}"

    @staticmethod
    def _normalize_category(category: str | None) -> str | None:
        """Normalize category input for OCS queries."""
        if not category:
            return None

        normalized = category.strip().lower()
        if normalized in {"all", "*"}:
            return None

        # Historical default for GTK in themectl.
        if normalized == "gtk":
            return Settings.GTK_CATEGORIES

        return category

    def _get(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        params = {**params, "format": "json"}
        key = self._cache_key(endpoint, params)
        cached = self.cache.get(key)
        if cached:
            return cached

        payload: dict[str, Any] = {}
        for base_url in (Settings.OCS_BASE_URL, Settings.OCS_FALLBACK_BASE_URL):
            response = self.session.get(
                f"{base_url}{endpoint}", params=params, timeout=20
            )
            response.raise_for_status()
            payload = response.json()
            if self._parse_content(payload):
                break

        self.cache.set(key, payload)
        return payload

    @staticmethod
    def _parse_content(payload: dict[str, Any]) -> list[dict[str, Any]]:
        data = payload.get("ocs", {}).get("data", [])

        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]

        if not isinstance(data, dict):
            return []

        content = data.get("content", data)
        if isinstance(content, dict):
            return [content]
        if isinstance(content, list):
            return [item for item in content if isinstance(item, dict)]
        return []

    def search(
        self,
        query: str,
        category: str = "gtk",
        page: int = 1,
        page_size: int = 24,
    ) -> list[Theme]:
        params: dict[str, Any] = {"search": query, "page": page, "pagesize": page_size}
        normalized_category = self._normalize_category(category)
        if normalized_category:
            params["categories"] = normalized_category
        content = self._parse_content(self._get("/content/data", params))
        themes = [Theme.from_ocs(item) for item in content]
        print(
            f"[themectl][OCSClient.search] raw={len(content)} parsed={len(themes)} query={query!r}"
        )
        return themes

    def top(
        self,
        category: str = "all",
        page: int = 1,
        page_size: int = 24,
    ) -> list[Theme]:
        params: dict[str, Any] = {"sort": "rating", "page": page, "pagesize": page_size}
        normalized_category = self._normalize_category(category)
        if normalized_category:
            params["categories"] = normalized_category
        content = self._parse_content(self._get("/content/data", params))
        themes = [Theme.from_ocs(item) for item in content]
        print(f"[themectl][OCSClient.top] raw={len(content)} parsed={len(themes)}")
        return themes

    def trending(
        self,
        category: str = "all",
        page: int = 1,
        page_size: int = 24,
    ) -> list[Theme]:
        params: dict[str, Any] = {"sort": "new", "page": page, "pagesize": page_size}
        normalized_category = self._normalize_category(category)
        if normalized_category:
            params["categories"] = normalized_category
        content = self._parse_content(self._get("/content/data", params))
        themes = [Theme.from_ocs(item) for item in content]
        print(f"[themectl][OCSClient.trending] raw={len(content)} parsed={len(themes)}")
        return themes

    def details(self, content_id: str) -> Theme | None:
        content = self._parse_content(self._get(f"/content/data/{content_id}", {}))
        return Theme.from_ocs(content[0]) if content else None
