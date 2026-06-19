# Agent Instructions

## Project

`wc-signal-monitor` is a Python terminal app for tracking World Cup 2026 winner signals from odds, prediction markets, and news.

## Commands

Use the project virtualenv unless the user explicitly asks to change tooling:

```bash
.venv/bin/ruff check .
.venv/bin/python -m pytest -v
.venv/bin/wcprob init-db
.venv/bin/wcprob collect-once
.venv/bin/wcprob tui
```

Do not introduce `uv`, Poetry, or another package manager unless the user asks for it. A stray `uv.lock` may exist locally; do not commit it unless adding uv support is the task.

## Architecture

- `src/wcprob/models.py`: Pydantic data models and source kinds.
- `src/wcprob/storage.py`: SQLite schema, immutable observation writes, latest snapshot queries, and history queries.
- `src/wcprob/sources/`: source adapters. Keep provider-specific parsing here.
- `src/wcprob/collector.py`: runs sources and records source health.
- `src/wcprob/consensus.py`: combines observations into ranked probabilities.
- `src/wcprob/tui.py`: Textual/Rich terminal UI.
- `src/wcprob/cli.py`: CLI wiring and source construction.

Keep provider logic out of the TUI and keep storage logic out of source adapters.

## Data Source Rules

- Treat external feeds as unreliable. Bad or empty payloads should raise clear errors inside the source adapter so collector health records the failure.
- Do not let a source silently return `[]` unless an empty result is semantically valid and tested.
- Preserve raw source values in `raw_value`.
- For probabilities, keep values in the `0..1` range.
- News signals are weak signals. Do not treat them as equal to market odds without an explicit weighting feature.
- Kalshi is opt-in because broad search can return unrelated multi-leg markets. Do not enable it by default without reliable winner-market discovery.

## Testing

Use TDD for behavior changes:

1. Add or update a focused failing test.
2. Run the targeted test and confirm the expected failure.
3. Implement the smallest change.
4. Run targeted tests.
5. Run full lint and tests.

Prefer mocked HTTP tests with `respx`; do not make live network calls in automated tests.

## Git Hygiene

- Do not commit runtime artifacts: `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `*.sqlite`, `*.db`, `__pycache__/`, or egg-info.
- Keep commits scoped to one behavior.
- Before finishing, run:

```bash
.venv/bin/ruff check .
.venv/bin/python -m pytest -v
git status --short
```

## Public Repo Safety

This repository is public. Never commit API keys, tokens, private market URLs, or local secrets. Use environment variables and `.env.example` only.
