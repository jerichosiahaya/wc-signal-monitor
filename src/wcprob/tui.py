from rich.table import Table
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header, Static

from wcprob.consensus import build_consensus
from wcprob.models import SourceHealth, SourceObservation
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


def sparkline(values: list[float]) -> str:
    bars = "▁▂▃▄▅▆▇█"
    if not values:
        return ""
    if len(values) == 1:
        return bars[-1]
    minimum = min(values)
    maximum = max(values)
    if minimum == maximum:
        return bars[0] * len(values)
    scale = len(bars) - 1
    return "".join(
        bars[round((value - minimum) / (maximum - minimum) * scale)]
        for value in values
    )


def country_history(
    observations: list[SourceObservation],
    country: str,
    limit: int = 12,
) -> list[float]:
    values = [
        row.implied_probability
        for row in sorted(observations, key=lambda row: row.captured_at)
        if row.country == country
    ]
    return values[-limit:]


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
        latest = self.storage.latest_observations()
        history = self.storage.observation_history()
        consensus = build_consensus(latest)
        for index, row in enumerate(consensus[:12], start=1):
            table.add_row(
                str(index),
                row.country,
                format_probability(row.probability),
                f"{row.source_count} {sparkline(country_history(history, row.country))}",
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

    latest = storage.latest_observations()
    history = storage.observation_history()
    consensus = build_consensus(latest)
    for index, row in enumerate(consensus[:12], start=1):
        table.add_row(
            str(index),
            row.country,
            format_probability(row.probability),
            f"{row.source_count} {sparkline(country_history(history, row.country))}",
        )

    return table


def run_tui(storage: Storage, refresh_seconds: int = 900) -> None:
    ProbabilityApp(storage, refresh_seconds=refresh_seconds).run()
