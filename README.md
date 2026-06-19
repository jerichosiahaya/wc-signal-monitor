# WC Signal Monitor

Automated Python TUI for tracking FIFA World Cup 2026 winner probabilities over time.

The monitor stores immutable probability snapshots in SQLite, computes a consensus ranking, and displays current favorites, source counts, and source health in the terminal.

## Commands

```bash
wcprob init-db
wcprob collect-once
wcprob tui
```

## Data Sources

API sources should be preferred for probabilities. Scrapers are used for annotations and fallback health signals because public page layouts change often.

## Environment Variables

- `WCPROB_DATABASE`: SQLite database path. Defaults to `wcprob.sqlite`.
- `WCPROB_REFRESH_SECONDS`: TUI refresh cadence. Defaults to `900`.
- `WCPROB_ODDS_API_URL`: Odds API endpoint for outright winner markets.
- `WCPROB_MARKET_URL`: Prediction-market endpoint returning country probabilities.
