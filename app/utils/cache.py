"""Simple JSON file cache with TTL support."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from app.utils.config import Settings


class JsonCache:
    """A filesystem-backed cache for API payloads."""

    def __init__(self, ttl_seconds: int | None = None) -> None:
        self.ttl_seconds = ttl_seconds or Settings.CACHE_EXPIRY_SECONDS

    def _cache_path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return Settings.CACHE_DIR / f"api_{digest}.json"

    def get(self, key: str) -> Any | None:
        """Return cached payload when still valid."""
        path = self._cache_path(key)
        if not path.exists():
            return None

        age = time.time() - path.stat().st_mtime
        if age > self.ttl_seconds:
            return None

        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def set(self, key: str, value: Any) -> None:
        """Persist payload to cache."""
        path = self._cache_path(key)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(value, handle)
