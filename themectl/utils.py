"""Utility functions and classes for themectl."""

import json
import time
import hashlib
from pathlib import Path
from typing import Any, Optional


class Config:
    """Handles configuration and paths for themectl."""

    THEMES_DIR = Path.home() / ".themes"
    CACHE_DIR = Path.home() / ".cache" / "themectl"
    CACHE_EXPIRY = 3600  # 1 hour

    @classmethod
    def ensure_dirs(cls):
        """Ensure necessary directories exist."""
        cls.THEMES_DIR.mkdir(parents=True, exist_ok=True)
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)


class Cache:
    """Simple file-based cache for API responses."""

    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Retrieve cached data if valid."""
        cache_file = Config.CACHE_DIR / f"{key}.json"
        if cache_file.exists():
            if time.time() - cache_file.stat().st_mtime < Config.CACHE_EXPIRY:
                with open(cache_file, "r") as f:
                    return json.load(f)
        return None

    @staticmethod
    def set(key: str, data: Any):
        """Cache data to a file."""
        cache_file = Config.CACHE_DIR / f"{key}.json"
        with open(cache_file, "w") as f:
            json.dump(data, f)


def format_size(size_bytes: float) -> str:
    """Format bytes into human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def json_hash(data: Any) -> str:
    """Simple hash for cache keys."""
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
