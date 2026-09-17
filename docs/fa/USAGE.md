# استفاده

این صفحه فقط usage آفلاین و محلی را توضیح می‌دهد. وجود آن به معنی پشتیبانی از live execution، wallet handling یا deployable smart contracts نیست.

## CLI

```bash
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json --json
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/base_market_snapshot.json --json
PYTHONPATH=src python -m defi_arbitrage_core.cli --show-policy
PYTHONPATH=src python -m defi_arbitrage_core.cli --diagnostics
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json --validate-only
```

flagهای مفید:

- `--json` برای خروجی machine-readable
- `--error-json` برای failureهای مورد انتظار
- `--diagnostics` برای بررسی capability و environment
- `--engine auto` برای استفاده از Rust با fallback امن به Python

## الگوی snapshot چندشبکه‌ای

```json
{
  "source": "research-snapshot",
  "network": "arbitrum",
  "timestamp": "2026-05-05T00:00:00Z",
  "edges": [
    {"source": "USDC", "target": "WETH", "rate": 0.00025}
  ]
}
```

این repository cross-chain bridge یا routing انجام نمی‌دهد. ایده این است که برای هر شبکه یک snapshot محلی ساخته شود و همان هسته روی آن اجرا شود.

خروجی شامل `capacity_known`، `snapshot_source` و `snapshot_timestamp` است. `estimated_capacity` بر حسب asset شروع مسیر و با تبدیل خطی محدودیت liquidity هر hop محاسبه می‌شود. `limiting_liquidity` فقط یک مقدار خام diagnostics است و ممکن است واحدهای متفاوت asset را ترکیب کند. نبودن liquidity با `capacity_known: false` مشخص می‌شود. این تحلیل nominal است و slippage، gas، token decimals، latency، MEV یا عمق اجرایی venue را مدل نمی‌کند.

## Python API

```python
from defi_arbitrage_core import AnalysisEngine, JsonFileProvider, RiskPolicy

snapshot = JsonFileProvider("examples/base_market_snapshot.json").load_snapshot()
policy = RiskPolicy(min_profit_bps=5, max_hops=4, max_notional=1000)
opportunities = AnalysisEngine(policy).analyze(snapshot)
```

## Validation کامل

```bash
PYTHONPATH=src python scripts/validate_all.py
PYTHONPATH=src python scripts/validate_all.py --include-rust
```
