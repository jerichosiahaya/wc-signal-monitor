from rich.table import Table
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header, Static

from wcprob.consensus import build_consensus
from wcprob.models import SourceHealth
from wcprob.storage import Storage


def format_probability(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_source_health(health: list[SourceHealth]) -> str:
    if not health:
        return "Sources: none"

    statuses = []
    for row in health:
        if row.ok:
            statuses.append(f"{row.source} ok")
        else:
            statuses.append(f"{row.source} failed: {row.message}")
    return f"Sources: {'; '.join(statuses)}"


class ProbabilityApp(App):
    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, storage: Storage, refresh_seconds: int = 900):
        super().__init__()
        self.storage = storage
        self.refresh_seconds = refresh_seconds

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="rankings")
        yield Static(id="source-health")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#rankings", DataTable)
        table.add_columns("Rank", "Country", "Consensus", "Sources")
        self.refresh_table()
        if self.refresh_seconds > 0:
            self.set_interval(self.refresh_seconds, self.refresh_table)

    def action_refresh(self) -> None:
        self.refresh_table()

    def refresh_table(self) -> None:
        table = self.query_one("#rankings", DataTable)
        table.clear()
        consensus = build_consensus(self.storage.latest_observations())
        for index, row in enumerate(consensus[:12], start=1):
            table.add_row(
                str(index),
                row.country,
                format_probability(row.probability),
                str(row.source_count),
            )
        self.query_one("#source-health", Static).update(
            format_source_health(self.storage.latest_health())
        )


def build_rich_table(storage: Storage) -> Table:
    table = Table(title="World Cup 2026 Win Probability")
    table.add_column("Rank")
    table.add_column("Country")
    table.add_column("Consensus")
    table.add_column("Sources")

    consensus = build_consensus(storage.latest_observations())
    for index, row in enumerate(consensus[:12], start=1):
        table.add_row(
            str(index),
            row.country,
            format_probability(row.probability),
            str(row.source_count),
        )

    return table


def run_tui(storage: Storage, refresh_seconds: int = 900) -> None:
    ProbabilityApp(storage, refresh_seconds=refresh_seconds).run()
