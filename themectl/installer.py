import os
import shutil
import zipfile
import tarfile
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from .utils import Config, format_size
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn

class ThemeInstaller:
    """Handles the installation and management of themes."""
    
    def __init__(self):
        Config.ensure_dirs()

    def install(self, content_id: str, download_url: str, filename: str):
        """Download and install a theme."""
        temp_dir = Config.CACHE_DIR / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        dest_path = temp_dir / filename
        
        # Download with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
        ) as progress:
            task = progress.add_task(f"Downloading {filename}...", total=None)
            
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            progress.update(task, total=total_size)
            
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))

        # Extract
        extract_path = temp_dir / f"extracted_{content_id}"
        extract_path.mkdir(exist_ok=True)
        
        if filename.endswith(".zip"):
            with zipfile.ZipFile(dest_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
        elif filename.endswith((".tar.gz", ".tgz", ".tar.xz", ".tar.bz2")):
            with tarfile.open(dest_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_path)
        else:
            # If it's not an archive, just move it
            shutil.move(dest_path, Config.THEMES_DIR / filename)
            return

        # Move to ~/.themes
        # Often themes are inside a subfolder in the archive
        for item in extract_path.iterdir():
            if item.is_dir():
                target = Config.THEMES_DIR / item.name
                if target.exists():
                    shutil.rmtree(target)
                shutil.move(str(item), str(target))
        
        # Cleanup
        shutil.rmtree(temp_dir)

    def remove(self, theme_name: str):
        """Remove an installed theme."""
        theme_path = Config.THEMES_DIR / theme_name
        if theme_path.exists():
            if theme_path.is_dir():
                shutil.rmtree(theme_path)
            else:
                theme_path.unlink()
            return True
        return False

    def list_installed(self) -> List[str]:
        """List all installed themes in ~/.themes."""
        if not Config.THEMES_DIR.exists():
            return []
        return [item.name for item in Config.THEMES_DIR.iterdir() if item.is_dir()]

    def update(self):
        """Placeholder for update logic (requires tracking versions)."""
        # In a real app, we'd store a local DB of installed theme IDs and versions
        pass
