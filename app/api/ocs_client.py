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

        return category.strip()

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
        data = payload.get("ocs", {}).get("data")
        if data is None:
            data = payload.get("data", payload)

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

    @staticmethod
    def _pagination(payload: dict[str, Any], page: int, page_size: int) -> dict[str, int | bool]:
        total_items = Theme._as_int(
            payload.get("totalitems")
            or payload.get("ocs", {}).get("meta", {}).get("totalitems"),
            0,
        )
        items_per_page = Theme._as_int(
            payload.get("itemsperpage")
            or payload.get("ocs", {}).get("meta", {}).get("itemsperpage"),
            page_size,
        )
        return {
            "page": page,
            "page_size": items_per_page or page_size,
            "total_items": total_items,
            "has_more": total_items > page * (items_per_page or page_size),
        }

    @staticmethod
    def _parse_categories(payload: dict[str, Any]) -> list[dict[str, str]]:
        items = OCSClient._parse_content(payload)
        categories: list[dict[str, str]] = []
        for item in items:
            category_id = str(item.get("id", "")).strip()
            name = str(item.get("display_name") or item.get("name") or "").strip()
            if not category_id or not name:
                continue
            categories.append(
                {
                    "id": category_id,
                    "name": name,
                    "parent_id": str(item.get("parent_id", "")).strip(),
                    "xdg_type": str(item.get("xdg_type", "")).strip(),
                }
            )
        return categories

    def _list(
        self,
        *,
        sort: str | None = None,
        query: str | None = None,
        category: str | None = None,
        page: int = 1,
        page_size: int = 24,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"page": page, "pagesize": page_size}
        if sort:
            params["sort"] = sort
        if query:
            params["search"] = query

        normalized_category = self._normalize_category(category)
        if normalized_category:
            params["categories"] = normalized_category

        payload = self._get("/content/data", params)
        content = self._parse_content(payload)
        themes = [Theme.from_ocs(item) for item in content]
        return {
            "items": themes,
            "pagination": self._pagination(payload, page, page_size),
            "raw_count": len(content),
        }

    def search(
        self,
        query: str,
        category: str | None = None,
        page: int = 1,
        page_size: int = 24,
    ) -> list[Theme]:
        result = self._list(
            query=query,
            category=category,
            page=page,
            page_size=page_size,
        )
        themes = result["items"]
        print(
            f"[themectl][OCSClient.search] raw={result['raw_count']} parsed={len(themes)} query={query!r}"
        )
        return themes

    def search_page(
        self,
        query: str,
        category: str | None = None,
        page: int = 1,
        page_size: int = 24,
    ) -> dict[str, Any]:
        result = self._list(
            query=query,
            category=category,
            page=page,
            page_size=page_size,
        )
        print(
            f"[themectl][OCSClient.search] raw={result['raw_count']} parsed={len(result['items'])} query={query!r}"
        )
        return result

    def top(
        self,
        category: str | None = None,
        page: int = 1,
        page_size: int = 24,
    ) -> list[Theme]:
        result = self.top_page(category=category, page=page, page_size=page_size)
        themes = result["items"]
        return themes

    def top_page(
        self,
        category: str | None = None,
        page: int = 1,
        page_size: int = 24,
    ) -> dict[str, Any]:
        result = self._list(
            sort="rating",
            category=category,
            page=page,
            page_size=page_size,
        )
        print(f"[themectl][OCSClient.top] raw={result['raw_count']} parsed={len(result['items'])}")
        return result

    def trending(
        self,
        category: str | None = None,
        page: int = 1,
        page_size: int = 24,
    ) -> list[Theme]:
        result = self.trending_page(category=category, page=page, page_size=page_size)
        themes = result["items"]
        return themes

    def trending_page(
        self,
        category: str | None = None,
        page: int = 1,
        page_size: int = 24,
    ) -> dict[str, Any]:
        result = self._list(
            sort="new",
            category=category,
            page=page,
            page_size=page_size,
        )
        print(
            f"[themectl][OCSClient.trending] raw={result['raw_count']} parsed={len(result['items'])}"
        )
        return result

    def details(self, content_id: str) -> Theme | None:
        content = self._parse_content(self._get(f"/content/data/{content_id}", {}))
        return Theme.from_ocs(content[0]) if content else None

    def categories(self) -> list[dict[str, str]]:
        payload = self._get("/content/categories", {})
        categories = self._parse_categories(payload)
        print(f"[themectl][OCSClient.categories] parsed={len(categories)}")
        return categories
