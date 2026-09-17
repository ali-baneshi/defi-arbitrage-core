# Validation 指南

无依赖 baseline：

```bash
PYTHONPATH=src python scripts/validate_all.py
PYTHONPATH=src python scripts/validate_all.py --include-rust
```

重要 workflow：

```bash
PYTHONPATH=src python scripts/validate_output_contracts.py
PYTHONPATH=src python scripts/validate_release_evidence.py --example
PYTHONPATH=src python scripts/release_readiness.py --json
```

只有在存在经过外部验证的 non-secret `release/release-evidence.json` 时，
`release_readiness.py` 才会将 public release gate 视为 satisfied。example
文件故意保持 blocked，不能作为发布许可。

本项目只执行 nominal 分析，不保证利润或 on-chain 可执行性。英文文档仍是 canonical source。
