"""Ui preview for themectl using Rich."""

import re
from typing import List, Dict, Any
from .utils import format_size
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns


class ThemePreview:
    """Formats and displays theme information using Rich."""

    def __init__(self):
        self.console = Console()

    def show_list(self, themes: List[Dict[str, Any]], title: str = "Themes"):
        """Display a list of themes in a table."""
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=10)
        table.add_column("Name", style="bold cyan")
        table.add_column("Author", style="green")
        table.add_column("Score", justify="right")
        table.add_column("Downloads", justify="right")

        for theme in themes:
            table.add_row(
                str(theme.get("id", "N/A")),
                theme.get("name", "Unknown"),
                theme.get("personid", "Unknown"),
                str(theme.get("score", "0")),
                str(theme.get("download_count", "0")),
            )

        self.console.print(table)

    def show_details(self, theme: Dict[str, Any]):
        """Display detailed information for a single theme."""
        name = theme.get("name", "Unknown")
        author = theme.get("personid", "Unknown")
        score = theme.get("score", "0")
        summary = theme.get("summary", "No summary available.")
        preview_url = theme.get("preview1", "No preview image.")

        # Clean up summary (it might contain HTML)

        clean_summary = re.sub("<[^<]+?>", "", summary)

        panel_content = Text.assemble(
            ("Author: ", "bold"),
            (f"{author}\n", "green"),
            ("Score: ", "bold"),
            (f"{score}/100\n", "yellow"),
            ("\nSummary:\n", "bold"),
            (f"{clean_summary}\n", "white"),
            ("\nPreview Image: ", "bold"),
            (f"{preview_url}", "blue underline"),
        )

        self.console.print(
            Panel(panel_content, title=f"[bold cyan]{name}[/bold cyan]", expand=False)
        )
