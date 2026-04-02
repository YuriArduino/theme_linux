"""API client for themectl to interact with Open Collaboration Services (OCS)."""

from typing import List, Dict, Any, Optional
import requests
from .utils import Cache, json_hash


class OCSClient:
    """Client for the Open Collaboration Services (OCS) API."""

    BASE_URL = "https://www.opendesktop.org/ocs/v1"

    # GTK Categories (GTK 3, GTK 4, GTK 2)
    GTK_CATEGORIES = "135,167,136"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": "application/json", "User-Agent": "themectl/1.0.0"}
        )

    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Internal GET request handler with caching."""
        cache_key = f"{endpoint}_{json_hash(params)}" if params else endpoint
        cached = Cache.get(cache_key)
        if cached:
            return cached

        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        params["format"] = "json"

        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        Cache.set(cache_key, data)
        return data

    def search(self, query: str, category: str = "gtk") -> List[Dict[str, Any]]:
        """Search for content."""
        params = {
            "search": query,
            "categories": self.GTK_CATEGORIES if category == "gtk" else category,
        }
        data = self._get("/content/data", params)
        return self._parse_content_list(data)

    def get_top(self, category: str = "gtk") -> List[Dict[str, Any]]:
        """Get top rated content."""
        params = {
            "sort": "rating",
            "categories": self.GTK_CATEGORIES if category == "gtk" else category,
        }
        data = self._get("/content/data", params)
        return self._parse_content_list(data)

    def get_trending(self, category: str = "gtk") -> List[Dict[str, Any]]:
        """Get recently trending content."""
        params = {
            "sort": "new",
            "categories": self.GTK_CATEGORIES if category == "gtk" else category,
        }
        data = self._get("/content/data", params)
        return self._parse_content_list(data)

    def get_details(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific content ID."""
        data = self._get(f"/content/data/{content_id}")
        items = self._parse_content_list(data)
        return items[0] if items else None

    def _parse_content_list(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse OCS JSON response into a clean list of items."""
        try:
            # OCS JSON structure is often nested under ocs.data.content
            content = data.get("ocs", {}).get("data", {}).get("content", [])
            if isinstance(content, dict):
                return [content]
            return content
        except ValueError:
            return []
