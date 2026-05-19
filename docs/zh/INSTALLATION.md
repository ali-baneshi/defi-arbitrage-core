# 安装

本页覆盖可选的开发者安装流程以及基于 container 的运行方式。如果你只是想 review 或 validate 仓库，更推荐使用 `README.md` 与 `docs/en/VALIDATION.md` 中的无安装命令。

## 前置条件

- Python 3.10 或更高版本
- `pip`
- 如有需要：`pytest` 与 `ruff`
- 如有需要：Docker 用于可复现的容器执行

## Editable 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]' --no-build-isolation
```

如果公共 Python 索引不可达，请使用可访问的镜像：

```bash
make bootstrap PIP_INDEX_URL=https://<mirror>/simple
```

如需额外回退源：

```bash
make bootstrap PIP_INDEX_URL=https://<primary-mirror>/simple PIP_EXTRA_INDEX_URL=https://<secondary-mirror>/simple
```

## 验证

```bash
defi-arbitrage-core examples/market_snapshot.json
defi-arbitrage-core examples/base_market_snapshot.json --json
python -m pytest -q
python -m ruff check .
```

## 不安装时

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
