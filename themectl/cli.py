"""Main CLI entry point for themectl."""

import typer
from .api import OCSClient
from .installer import ThemeInstaller
from .preview import ThemePreview
from .utils import Config

app = typer.Typer(help="Manage Linux desktop themes from OpenDesktop.")
client = OCSClient()
installer = ThemeInstaller()
previewer = ThemePreview()


@app.command()
def search(query: str, category: str = "gtk"):
    """Search for themes by query and category."""
    themes = client.search(query, category)
    previewer.show_list(themes, f"Search results for '{query}'")


@app.command()
def top(category: str = "gtk"):
    """Show top rated themes."""
    themes = client.get_top(category)
    previewer.show_list(themes, "Top Rated Themes")


@app.command()
def trending(category: str = "gtk"):
    """Show recently trending themes."""
    themes = client.get_trending(category)
    previewer.show_list(themes, "Trending Themes")


@app.command()
def preview(content_id: str):
    """Show theme details including screenshots."""
    theme = client.get_details(content_id)
    if theme:
        previewer.show_details(theme)
    else:
        typer.echo(f"Theme with ID {content_id} not found.")


@app.command()
def install(content_id: str):
    """Download and install a theme by ID."""
    theme = client.get_details(content_id)
    if not theme:
        typer.echo(f"Theme with ID {content_id} not found.")
        return

    # OCS often has multiple download links
    # We'll try to find the best one
    # For simplicity, we'll pick the first one
    download_url = theme.get("download_link1")
    filename = theme.get("download_name1")

    if not download_url:
        typer.echo("No download link found for this theme.")
        return

    typer.echo(f"Installing {theme.get('name')}...")
    installer.install(content_id, download_url, filename)
    typer.echo(f"Successfully installed {theme.get('name')} to ~/.themes/")


@app.command()
def remove(theme_name: str):
    """Remove an installed theme."""
    if installer.remove(theme_name):
        typer.echo(f"Successfully removed {theme_name}.")
    else:
        typer.echo(f"Theme {theme_name} not found in ~/.themes/.")


@app.command()
def list():
    """List installed themes."""
    themes = installer.list_installed()
    if themes:
        typer.echo("Installed themes:")
        for theme in themes:
            typer.echo(f" - {theme}")
    else:
        typer.echo("No themes installed in ~/.themes/.")


@app.command()
def update():
    """Update installed themes (Not implemented yet)."""
    typer.echo("Update feature is coming soon!")


@app.command()
def browse():
    """Open interactive UI mode."""
    from .tui import ThemeBrowser

    app = ThemeBrowser()
    app.run()


if __name__ == "__main__":
    app()
