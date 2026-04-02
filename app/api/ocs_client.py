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
                "User-Agent": f"{Settings.APP_NAME}/{Settings.APP_VERSION}",
            }
        )
        self.cache = JsonCache()

    def _cache_key(self, endpoint: str, params: dict[str, Any]) -> str:
        return f"{endpoint}:{json.dumps(params, sort_keys=True)}"

    def _get(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        params = {**params, "format": "json"}
        key = self._cache_key(endpoint, params)
        cached = self.cache.get(key)
        if cached:
            return cached

        response = self.session.get(f"{Settings.OCS_BASE_URL}{endpoint}", params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
        self.cache.set(key, payload)
        return payload

    @staticmethod
    def _parse_content(payload: dict[str, Any]) -> list[dict[str, Any]]:
        content = payload.get("ocs", {}).get("data", {}).get("content", [])
        if isinstance(content, dict):
            return [content]
        if isinstance(content, list):
            return content
        return []

    def search(self, query: str, category: str = "gtk") -> list[Theme]:
        params = {
            "search": query,
            "categories": Settings.GTK_CATEGORIES if category == "gtk" else category,
        }
        content = self._parse_content(self._get("/content/data", params))
        return [Theme.from_ocs(item) for item in content]

    def top(self, category: str = "gtk") -> list[Theme]:
        params = {
            "sort": "rating",
            "categories": Settings.GTK_CATEGORIES if category == "gtk" else category,
        }
        content = self._parse_content(self._get("/content/data", params))
        return [Theme.from_ocs(item) for item in content]

    def trending(self, category: str = "gtk") -> list[Theme]:
        params = {
            "sort": "new",
            "categories": Settings.GTK_CATEGORIES if category == "gtk" else category,
        }
        content = self._parse_content(self._get("/content/data", params))
        return [Theme.from_ocs(item) for item in content]

    def details(self, content_id: str) -> Theme | None:
        content = self._parse_content(self._get(f"/content/data/{content_id}", {}))
        return Theme.from_ocs(content[0]) if content else None
