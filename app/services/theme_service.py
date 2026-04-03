"""High-level theme use-cases for UI/API routes."""

from __future__ import annotations

from app.api.ocs_client import OCSClient
from app.services.installer_service import InstallerService


class ThemeService:
    """Facade combining API and local installation operations."""

    def __init__(self) -> None:
        self.client = OCSClient()
        self.installer = InstallerService()

    def browse(
        self,
        sort: str = "top",
        page: int = 1,
        page_size: int = 24,
        category: str | None = None,
    ):
        if sort == "trending":
            result = self.client.trending_page(
                page=page,
                page_size=page_size,
                category=category,
            )
        else:
            result = self.client.top_page(
                page=page,
                page_size=page_size,
                category=category,
            )
        print(
            f"[themectl][ThemeService.browse] sort={sort} page={page} page_size={page_size} category={category!r} parsed={len(result['items'])}"
        )
        return result

    def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 24,
        category: str | None = None,
    ):
        result = self.client.search_page(
            query,
            page=page,
            page_size=page_size,
            category=category,
        )
        print(
            f"[themectl][ThemeService.search] query={query!r} page={page} page_size={page_size} category={category!r} parsed={len(result['items'])}"
        )
        return result

    def categories(self):
        categories = self.client.categories()
        print(f"[themectl][ThemeService.categories] parsed={len(categories)}")
        return categories

    def details(self, content_id: str):
        return self.client.details(content_id)

    def install(self, content_id: str):
        theme = self.client.details(content_id)
        if not theme:
            raise ValueError("Theme not found")
        return self.installer.install(theme)

    def remove(self, content_id: str):
        return self.installer.remove(content_id)

    def installed(self):
        return self.installer.list_installed()

    def updates(self):
        updates = []
        for installed in self.installer.list_installed():
            content_id = installed.get("id", "")
            remote = self.client.details(content_id)
            if not remote:
                continue
            if str(remote.version) != str(installed.get("version", "")):
                updates.append(
                    {
                        "id": remote.id,
                        "name": remote.name,
                        "installed_version": installed.get("version", "unknown"),
                        "latest_version": remote.version,
                    }
                )
        return updates
