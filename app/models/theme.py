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

    @classmethod
    def from_ocs(cls, payload: dict[str, Any]) -> "Theme":
        """Build Theme from a raw OCS response item."""
        previews = [
            payload.get("preview1"),
            payload.get("preview2"),
            payload.get("preview3"),
            payload.get("preview4"),
        ]
        preview_urls = [url for url in previews if isinstance(url, str) and url]

        return cls(
            id=str(payload.get("id", "")),
            name=str(payload.get("name", "Unknown")),
            author=str(payload.get("personid") or payload.get("username") or "Unknown"),
            summary=str(payload.get("summary") or "No summary available."),
            score=float(payload.get("score") or 0),
            downloads=int(payload.get("download_count") or 0),
            version=str(payload.get("version") or payload.get("changed") or "unknown"),
            updated_at=str(payload.get("changed") or payload.get("created") or ""),
            preview_urls=preview_urls,
            download_url=payload.get("downloadlink1") or payload.get("download_link1"),
            download_name=payload.get("downloadname1") or payload.get("download_name1"),
            raw=payload,
        )
