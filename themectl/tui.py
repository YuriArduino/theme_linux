"""TUI module for themectl - a terminal-based theme browser and installer."""

import re
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static, Button
from textual.containers import Container, Horizontal, Vertical
from .api import OCSClient
from .installer import ThemeInstaller


class ThemeBrowser(App):
    """Interactive TUI for browsing themes."""

    CSS = """
    Screen {
        layout: horizontal;
    }
    #sidebar {
        width: 30%;
        border-right: solid magenta;
    }
    #main {
        width: 70%;
        padding: 1;
    }
    .theme-item {
        padding: 1;
        border-bottom: solid gray;
    }
    #details {
        height: 80%;
        border-bottom: solid gray;
    }
    #actions {
        height: 20%;
        align: center middle;
    }
    """

    def __init__(self):
        super().__init__()
        self.client = OCSClient()
        self.installer = ThemeInstaller()
        self.themes = []
        self.selected_theme = None

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()
        with Container(id="sidebar"):
            yield ListView(id="theme-list")
        with Container(id="main"):
            with Vertical(id="details"):
                yield Label("Select a theme to see details", id="theme-name")
                yield Static("", id="theme-summary")
            with Horizontal(id="actions"):
                yield Button("Install", variant="success", id="install-btn")
        yield Footer()

    async def on_mount(self) -> None:
        """Load themes when the app starts."""
        self.themes = self.client.get_top()
        list_view = self.query_one("#theme-list", ListView)
        for theme in self.themes:
            list_view.append(
                ListItem(
                    Label(theme.get("name", "Unknown")), id=f"theme-{theme.get('id')}"
                )
            )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Update theme details when a theme is selected."""
        theme_id = event.item.id.replace("theme-", "")
        self.selected_theme = next(
            (t for t in self.themes if t.get("id") == theme_id), None
        )
        if self.selected_theme:
            self.query_one("#theme-name", Label).update(
                f"[bold cyan]{self.selected_theme.get('name')}[/bold cyan]"
            )
            summary = re.sub("<[^<]+?>", "", self.selected_theme.get("summary", ""))
            self.query_one("#theme-summary", Static).update(summary)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button function"""
        if event.button.id == "install-btn" and self.selected_theme:
            content_id = self.selected_theme.get("id")
            download_url = self.selected_theme.get("download_link1")
            filename = self.selected_theme.get("download_name1")

            if download_url:
                self.notify(f"Installing {self.selected_theme.get('name')}...")
                # In a real TUI, we'd run this in a worker to avoid blocking
                self.run_worker(self._install_theme(content_id, download_url, filename))
            else:
                self.notify("No download link found.", severity="error")

    async def _install_theme(self, content_id, download_url, filename):
        try:
            self.installer.install(content_id, download_url, filename)
            self.notify("Installation complete!")
        except SystemError as e:
            self.notify(f"Error: {str(e)}", severity="error")
