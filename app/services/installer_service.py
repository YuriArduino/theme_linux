"""Theme installation/removal/update routines."""

from __future__ import annotations

import json
import shutil
import tarfile
import zipfile
from pathlib import Path

import requests

from app.models.theme import Theme
from app.utils.config import Settings


class InstallerService:
    """Manage local theme files and installation state."""

    def __init__(self) -> None:
        Settings.ensure_directories()

    def _read_installed_db(self) -> dict[str, dict[str, str]]:
        if not Settings.INSTALLED_DB.exists():
            return {}
        with Settings.INSTALLED_DB.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write_installed_db(self, data: dict[str, dict[str, str]]) -> None:
        with Settings.INSTALLED_DB.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def _download(self, url: str, filename: str) -> Path:
        target = Settings.DOWNLOAD_DIR / filename
        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with target.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        handle.write(chunk)
        return target

    def _extract_or_copy(self, archive_path: Path, content_id: str) -> list[str]:
        extract_dir = Settings.DOWNLOAD_DIR / f"extract_{content_id}"
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)

        filename = archive_path.name.lower()
        if filename.endswith(".zip"):
            with zipfile.ZipFile(archive_path, "r") as archive:
                archive.extractall(extract_dir)
        elif filename.endswith((".tar.gz", ".tgz", ".tar.xz", ".tar.bz2", ".tar")):
            with tarfile.open(archive_path, "r:*") as archive:
                archive.extractall(extract_dir)
        else:
            target = Settings.THEMES_DIR / archive_path.name
            shutil.copy2(archive_path, target)
            return [target.name]

        installed_names: list[str] = []
        for item in extract_dir.iterdir():
            target = Settings.THEMES_DIR / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.move(str(item), str(target))
            installed_names.append(target.name)

        shutil.rmtree(extract_dir)
        archive_path.unlink(missing_ok=True)
        return installed_names

    def install(self, theme: Theme) -> dict[str, str | list[str]]:
        """Install a theme and persist install metadata."""
        if not theme.download_url:
            raise ValueError("Theme has no downloadable file.")

        filename = theme.download_name or f"{theme.id}.zip"
        archive = self._download(theme.download_url, filename)
        installed_folders = self._extract_or_copy(archive, theme.id)

        db = self._read_installed_db()
        db[theme.id] = {
            "id": theme.id,
            "name": theme.name,
            "version": theme.version,
            "updated_at": theme.updated_at,
            "folders": "|".join(installed_folders),
        }
        self._write_installed_db(db)

        return {"id": theme.id, "name": theme.name, "folders": installed_folders}

    def remove(self, theme_id: str) -> bool:
        db = self._read_installed_db()
        record = db.get(theme_id)
        if not record:
            return False

        folders = record.get("folders", "").split("|")
        for folder in [f for f in folders if f]:
            target = Settings.THEMES_DIR / folder
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()

        db.pop(theme_id, None)
        self._write_installed_db(db)
        return True

    def list_installed(self) -> list[dict[str, str]]:
        db = self._read_installed_db()
        return list(db.values())
