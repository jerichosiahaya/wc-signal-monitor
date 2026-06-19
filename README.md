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

The app can collect from The Odds API, Polymarket Gamma, and Kalshi market data.
Polymarket is enabled by default using its public World Cup Winner event.
The Odds API requires an API key. Kalshi requires a specific market-data URL because broad search results can include unrelated multi-leg sports markets.

## Environment Variables

- `WCPROB_DATABASE`: SQLite database path. Defaults to `wcprob.sqlite`.
- `WCPROB_REFRESH_SECONDS`: TUI refresh cadence. Defaults to `900`.
- `WCPROB_ODDS_API_KEY`: The Odds API key. Enables the built-in World Cup outrights endpoint.
- `WCPROB_ODDS_API_REGIONS`: The Odds API bookmaker region list. Defaults to `us`.
- `WCPROB_POLYMARKET_ENABLED`: Set to `false` to disable Polymarket. Defaults to `true`.
- `WCPROB_POLYMARKET_URL`: Polymarket Gamma URL. Defaults to the World Cup Winner event slug.
- `WCPROB_KALSHI_ENABLED`: Set to `true` to enable Kalshi. Defaults to `false`.
- `WCPROB_KALSHI_URL`: Specific Kalshi market-data URL for World Cup winner markets.
- `WCPROB_ODDS_API_URL`: Advanced override for a complete odds endpoint URL.
- `WCPROB_MARKET_URL`: Advanced override for a normalized prediction-market endpoint returning `country` and `probability`.

## Example

```bash
export WCPROB_ODDS_API_KEY="your-the-odds-api-key"
wcprob init-db
wcprob collect-once
wcprob tui
```

You can also start from `.env.example`, but the app reads environment variables from your shell.
