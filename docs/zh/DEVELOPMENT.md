# 开发

英文文档是 canonical source，本页提供面向 contributor 的简明 best-effort 指南。

## 推荐开发流程

1. 保持改动小而易于 review
2. 始终维护离线分析边界
3. 为新行为补充 test 与 validation
4. 如果 CLI、schema 或公共契约变化，同时更新文档

## 主要命令

```bash
PYTHONPATH=src python scripts/validate_all.py
PYTHONPATH=src python scripts/validate_all.py --include-rust
python -m pytest -q
python -m ruff check .
```

## 变更标准

- 不要把 live execution、wallet、signing 或 RPC 逻辑引入核心
- 保持公共接口清晰而稳定
- 如果翻译文档滞后，请同步更新 `docs/TRANSLATION_STATUS.md`
