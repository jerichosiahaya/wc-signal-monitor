# WC Signal Monitor Roadmap

This roadmap keeps the project focused on one job: tracking World Cup 2026 winner signals over time from market, odds, and news sources.

## Current MVP

- CLI commands: `init-db`, `collect-once`, `tui`
- SQLite storage for immutable observations and source health
- Consensus ranking from latest source-country observations
- TUI table with probability, source count, source health, and sparklines
- Built-in source support:
  - The Odds API, enabled with `WCPROB_ODDS_API_KEY`
  - Polymarket Gamma, enabled by default
  - Kalshi, opt-in with a specific `WCPROB_KALSHI_URL`
  - RSS news signal, enabled by default

## Near Term

- Add provider-specific validation for real The Odds API outright payloads after testing with a live key.
- Add a reliable Kalshi World Cup winner discovery path instead of requiring a specific URL.
- Add a `sources` CLI command that prints enabled sources, URLs, and latest health.
- Add a `snapshot` CLI command that prints the current top 12 without opening the TUI.
- Add configurable source weights so news signals contribute less than markets and sportsbook odds.
- Add migration/version metadata to SQLite schema setup.

## TUI Improvements

- Add a country detail view with per-source probabilities and recent history.
- Add a movers view for 24-hour and 7-day probability changes.
- Add explicit source-health panel with last success time and failure message.
- Add empty-state messaging when no probability snapshots exist yet.
- Add direct keyboard shortcuts for refresh, source health, movers, and country drill-down.

## Signal Quality

- Normalize country names across sources, including aliases like `USA` and `United States`.
- Separate market odds, sportsbook odds, and news signals in consensus output.
- Add recency decay for stale observations.
- Add outlier detection when one provider diverges sharply from the rest.
- Store raw payload samples for failed parses in a debug-only mode.

## Operations

- Add `uv` support if the project standardizes on it.
- Add `systemd` timer or cron examples for scheduled collection.
- Add GitHub Actions for lint and tests.
- Add release packaging instructions.
- Add sample screenshots or terminal recordings for the README.

## Not Planned Yet

- Automated trading.
- Account-authenticated Kalshi or Polymarket trading APIs.
- Match-level predictions.
- Model-generated winner probabilities beyond source aggregation.
