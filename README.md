# themectl

`themectl` is a modern Linux theme manager for browsing, previewing, installing, and managing themes from the OpenDesktop / Pling OCS API.

> API endpoint: `https://api.opendesktop.org/ocs/v1/content/data`

## What's new in v2

- Migrated from terminal-first UX to a local web application (FastAPI + TailwindCSS).
- Introduced modular architecture designed for long-term maintainability.
- Added API response caching to reduce duplicate network calls.
- Added install-state tracking for installed themes and update checks.

## Architecture

```text
app/
  api/        # OCS API client and response parsing
  services/   # Theme workflows (browse/search/install/remove/update checks)
  models/     # Domain model(s) used across layers
  ui/         # FastAPI routes, templates, static assets
  utils/      # Shared config and caching utilities
main.py       # Local launcher: python main.py
```

### Module responsibilities

- `app/api/ocs_client.py`: Handles all HTTP communication with OpenDesktop OCS endpoints.
- `app/services/theme_service.py`: Orchestrates browse/search/details/install/remove/update operations.
- `app/services/installer_service.py`: Downloads archives, extracts theme folders to `~/.themes`, persists install metadata.
- `app/models/theme.py`: Normalizes OCS payloads into a stable `Theme` model.
- `app/ui/routes.py`: REST API + HTML route for local browser UI.
- `app/ui/templates/index.html`: Tailwind-based desktop-style layout.
- `app/ui/static/app.js`: Client-side interactions for navigation, search, detail modal, install/remove/update actions.
- `app/utils/cache.py`: File cache with TTL to avoid repeated API calls.
- `app/utils/config.py`: Central app settings and filesystem paths.

## Installation

### Prerequisites

- Python 3.11+

### Install dependencies

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Open in your browser:

```text
http://localhost:8000
```

## UI features

- Sidebar navigation (Browse / Trending / Installed / Updates)
- Search bar and search results grid
- Theme cards with preview image, rating, and download count
- Theme details modal
- Install and remove actions
- Installed themes section
- Update detection for installed themes

## Notes on caching and performance

- API responses are cached in `~/.cache/themectl` with TTL-based expiration.
- Cache keys are deterministic and parameter-based to prevent redundant requests.
- Repeated browse/search/detail requests within TTL avoid remote calls.

## Development tips

- Keep domain logic in `services/` and `api/`; keep route handlers thin.
- Avoid business logic in templates or JavaScript when possible.
- Keep model normalization in `models/` to shield UI from API shape changes.
