# themectl

A modern command-line client for browsing, installing, and managing Linux desktop themes from the [OpenDesktop / Pling OCS API](https://www.opendesktop.org/).

## Features

- **Search**: Find themes by name or category.
- **Top Rated**: Browse the highest-rated themes.
- **Trending**: See what's currently popular.
- **Preview**: View theme details and screenshots in your terminal.
- **Install**: One-click installation to `~/.themes/`.
- **Interactive Mode**: A terminal UI for a better browsing experience.

## Installation

### Prerequisites

- Python 3.11 or higher.

### From Source

```bash
git clone https://github.com/yourusername/themectl.git
cd themectl
pip install .
```

### Using pipx (Recommended)

```bash
pipx install .
```

## Usage

### Commands

- **Search themes**:
  ```bash
  themectl search gtk catppuccin
  ```

- **Show top rated themes**:
  ```bash
  themectl top
  ```

- **Show trending themes**:
  ```bash
  themectl trending
  ```

- **Preview a theme**:
  ```bash
  themectl preview <id>
  ```

- **Install a theme**:
  ```bash
  themectl install <id>
  ```

- **List installed themes**:
  ```bash
  themectl list
  ```

- **Remove a theme**:
  ```bash
  themectl remove <theme_name>
  ```

- **Interactive Browser**:
  ```bash
  themectl browse
  ```

## Architecture

`themectl` is built with a modular architecture:

- `api.py`: Handles all communication with the OCS API.
- `installer.py`: Manages downloading, extracting, and installing themes.
- `preview.py`: Formats and displays theme information using `rich`.
- `cli.py`: Defines the command-line interface using `typer`.
- `tui.py`: Provides the interactive terminal UI using `textual`.
- `utils.py`: Contains shared utilities for caching and configuration.

## License

MIT
