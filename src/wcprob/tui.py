from rich.table import Table
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header

from wcprob.consensus import build_consensus
from wcprob.storage import Storage


def format_probability(value: float) -> str:
    return f"{value * 100:.1f}%"


class ProbabilityApp(App):
    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="rankings")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#rankings", DataTable)
        table.add_columns("Rank", "Country", "Consensus", "Sources")
        self.refresh_table()

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


def run_tui(storage: Storage) -> None:
    ProbabilityApp(storage).run()
