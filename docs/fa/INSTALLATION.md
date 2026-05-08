# نصب

این صفحه نصب اختیاری توسعه‌دهنده و اجرای مبتنی بر container را پوشش می‌دهد. اگر فقط می‌خواهید repository را review یا validate کنید، از commandهای بدون نصب در `README.md` و `docs/en/VALIDATION.md` استفاده کنید.

## پیش‌نیازها

- Python 3.10 یا جدیدتر
- `pip`
- در صورت نیاز: `pytest` و `ruff`
- در صورت نیاز: Docker برای اجرای بازتولیدپذیر

## نصب editable

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## بررسی

```bash
defi-arbitrage-core examples/market_snapshot.json
defi-arbitrage-core examples/base_market_snapshot.json --json
python -m pytest -q
python -m ruff check .
```

## بدون نصب

```bash
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/base_market_snapshot.json --json
```

## Docker

```bash
docker build -t defi-arbitrage-core:local .
docker run --rm defi-arbitrage-core:local examples/market_snapshot.json --json
docker run --rm --entrypoint python defi-arbitrage-core:local scripts/validate_all.py
```
