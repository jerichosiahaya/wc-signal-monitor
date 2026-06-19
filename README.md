# WC Signal Monitor

Automated Python TUI for tracking FIFA World Cup 2026 winner probabilities over time.

The monitor stores immutable probability snapshots in SQLite, computes a consensus ranking, and displays current favorites, movement, and source health in the terminal.

## Commands

```bash
wcprob init-db
wcprob collect-once
wcprob tui
```

## Data Sources

API sources should be preferred for probabilities. Scrapers are used for annotations and fallback health signals because public page layouts change often.
