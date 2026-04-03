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

    def _cache_key(self, endpoint: str, query: dict[str, Any]) -> str:
        """Generate deterministic cache key."""
        return f"{endpoint}:{json.dumps(query, sort_keys=True)}"

    def _get(self, endpoint: str, query: dict[str, Any]) -> dict[str, Any]:
        """Perform HTTP GET with caching."""
        query = {**query, "format": "json"}

        cache_key = self._cache_key(endpoint, query)
        cached = self.cache.get(cache_key)

        if cached:
            return cached

        response = self.session.get(
            f"{Settings.OCS_BASE_URL}{endpoint}",
            params=query,
            timeout=20,
        )

        response.raise_for_status()

        payload = response.json()

        self.cache.set(cache_key, payload)

        return payload

    @staticmethod
    def _parse_content(payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract 'content' list from OCS response."""
        content = payload.get("ocs", {}).get("data", {}).get("content", [])

        if isinstance(content, dict):
            return [content]

        if isinstance(content, list):
            return content

        return []

    def search(self, query: str, category: str = "gtk") -> list[Theme]:
        """Search themes."""
        query_params = {
            "search": query,
            "sortmode": "rating",
            "page": 1,
            "pagesize": 20,
            "categories": Settings.GTK_CATEGORIES if category == "gtk" else category,
        }

        content = self._parse_content(self._get("/content/data", query_params))

        return [Theme.from_ocs(item) for item in content]

    def top(self, category: str = "gtk") -> list[Theme]:
        """Fetch top rated themes."""
        query_params = {
            "sortmode": "rating",
            "page": 1,
            "pagesize": 20,
            "categories": Settings.GTK_CATEGORIES if category == "gtk" else category,
        }

        content = self._parse_content(self._get("/content/data", query_params))

        return [Theme.from_ocs(item) for item in content]

    def trending(self, category: str = "gtk") -> list[Theme]:
        """Fetch newest/trending themes."""
        query_params = {
            "sortmode": "new",
            "page": 1,
            "pagesize": 20,
            "categories": Settings.GTK_CATEGORIES if category == "gtk" else category,
        }

        content = self._parse_content(self._get("/content/data", query_params))

        return [Theme.from_ocs(item) for item in content]

    def details(self, content_id: str) -> Theme | None:
        """Fetch details for a specific theme."""
        content = self._parse_content(self._get(f"/content/data/{content_id}", {}))

        if not content:
            return None

        return Theme.from_ocs(content[0])
