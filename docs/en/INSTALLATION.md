# Installation

This page covers optional developer installation and container-based execution. If you only need to review or validate the repository, prefer the no-install commands in `README.md` and `docs/en/VALIDATION.md`.

## Prerequisites

- Python 3.10 or newer
- `pip`
- Optional: `pytest` and `ruff` through the `dev` extra
- Optional: Docker for reproducible container runs

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Verify

```bash
defi-arbitrage-core examples/market_snapshot.json
defi-arbitrage-core examples/market_snapshot.json --json
python -m pytest -q
python -m ruff check .
```

Without installation:

```bash
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json
```

## Docker

```bash
docker build -t defi-arbitrage-core:local .
docker run --rm defi-arbitrage-core:local examples/market_snapshot.json --json
docker run --rm --entrypoint python defi-arbitrage-core:local scripts/validate_all.py
```

## Environment Variables

`.env.example` lists optional non-secret settings. The core does not require secrets.
