"""Application configuration values and path helpers."""

from pathlib import Path


class Settings:
    """Runtime settings for themectl."""

    APP_NAME = "themectl"
    APP_VERSION = "2.0.0"

    OCS_BASE_URL = "https://api.opendesktop.org/ocs/v1"
    OCS_FALLBACK_BASE_URL = "https://api.pling.com/ocs/v1"
    GTK_CATEGORIES = "135,167,136"

    HOST = "127.0.0.1"
    PORT = 8000

    THEMES_DIR = Path.home() / ".themes"
    CACHE_DIR = Path.home() / ".cache" / APP_NAME
    DOWNLOAD_DIR = CACHE_DIR / "downloads"
    CACHE_EXPIRY_SECONDS = 1800
    INSTALLED_DB = CACHE_DIR / "installed_themes.json"

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist."""
        cls.THEMES_DIR.mkdir(parents=True, exist_ok=True)
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
