"""Domain models for OCS themes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Theme:
    """Normalized theme object consumed by services and UI."""

    id: str
    name: str
    author: str
    summary: str
    score: float
    downloads: int
    version: str
    updated_at: str
    preview_urls: list[str] = field(default_factory=list)
    download_url: str | None = None
    download_name: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def _as_int(value: Any, default: int = 0) -> int:
        try:
            if value in (None, ""):
                return default
            return int(float(value))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _as_float(value: Any, default: float = 0.0) -> float:
        try:
            if value in (None, ""):
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _is_preview_url(value: Any) -> bool:
        if not isinstance(value, str) or not value:
            return False
        return "images.pling.com" in value or "opendesktop.org/img/" in value

    @classmethod
    def from_ocs(cls, payload: dict[str, Any]) -> "Theme":
        """Build Theme from a raw OCS response item."""
        previews = [
            payload.get("previewpic1"),
            payload.get("previewpic2"),
            payload.get("previewpic3"),
            payload.get("previewpic4"),
        ]
        preview_urls = [url for url in previews if cls._is_preview_url(url)]

        if not preview_urls:
            fallback_previews = [
                payload.get("preview1"),
                payload.get("preview2"),
                payload.get("preview3"),
                payload.get("preview4"),
            ]
            preview_urls = [url for url in fallback_previews if cls._is_preview_url(url)]

        return cls(
            id=str(payload.get("id", "")),
            name=str(payload.get("name", "Unknown")),
            author=str(payload.get("personid") or payload.get("username") or "Unknown"),
            summary=str(payload.get("summary") or "No summary available."),
            score=cls._as_float(payload.get("score"), 0.0),
            downloads=cls._as_int(
                payload.get("downloads", payload.get("download_count")),
                0,
            ),
            version=str(payload.get("version") or payload.get("changed") or "unknown"),
            updated_at=str(payload.get("changed") or payload.get("created") or ""),
            preview_urls=preview_urls,
            download_url=payload.get("downloadlink1") or payload.get("download_link1"),
            download_name=payload.get("downloadname1") or payload.get("download_name1"),
            raw=payload,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the normalized model for API responses."""
        preview1 = self.preview_urls[0] if len(self.preview_urls) > 0 else ""
        preview2 = self.preview_urls[1] if len(self.preview_urls) > 1 else ""
        preview3 = self.preview_urls[2] if len(self.preview_urls) > 2 else ""
        preview4 = self.preview_urls[3] if len(self.preview_urls) > 3 else ""

        return {
            "id": self.id,
            "name": self.name,
            "author": self.author,
            "summary": self.summary,
            "score": self.score,
            "downloads": self.downloads,
            "version": self.version,
            "updated_at": self.updated_at,
            "preview": preview1,
            "previewpic1": preview1,
            "previewpic2": preview2,
            "previewpic3": preview3,
            "previewpic4": preview4,
            "preview_urls": self.preview_urls,
            "download_link": self.download_url or "",
            "downloadlink1": self.download_url or "",
            "download_name": self.download_name or "",
            "downloadname1": self.download_name or "",
        }
