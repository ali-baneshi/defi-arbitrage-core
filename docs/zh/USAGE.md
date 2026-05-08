# 使用

本页只描述离线、本地分析的用法。它并不意味着支持 live execution、wallet handling 或可部署的智能合约。

## CLI

```bash
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json --json
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/base_market_snapshot.json --json
PYTHONPATH=src python -m defi_arbitrage_core.cli --show-policy
PYTHONPATH=src python -m defi_arbitrage_core.cli --diagnostics
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json --validate-only
```

常用 flag：

- `--json`：机器可读输出
- `--error-json`：机器可读失败输出
- `--diagnostics`：检查 capability 与 environment
- `--engine auto`：优先使用 Rust，失败时安全 fallback 到 Python

## 多网络快照模式

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

这个仓库不做 cross-chain bridge 或 routing。推荐的方式是：每个网络生成自己的本地 snapshot，然后复用同一个分析核心。

## Python API

```python
from defi_arbitrage_core import AnalysisEngine, JsonFileProvider, RiskPolicy

snapshot = JsonFileProvider("examples/base_market_snapshot.json").load_snapshot()
policy = RiskPolicy(min_profit_bps=5, max_hops=4, max_notional=1000)
opportunities = AnalysisEngine(policy).analyze(snapshot)
```

## 完整验证

```bash
PYTHONPATH=src python scripts/validate_all.py
PYTHONPATH=src python scripts/validate_all.py --include-rust
```
