# Reviewer 指南

canonical 来源：

- Python：`src/arbcore/`
- JSON contracts：`schemas/`
- validation：`scripts/validate_*.py`
- readiness：`scripts/release_readiness.py`
- evidence：`release/release-evidence.json`

快速 review 路径：

```bash
PYTHONPATH=src python scripts/validate_all.py --include-rust
PYTHONPATH=src python scripts/release_readiness.py --json
PYTHONPATH=src python scripts/validate_release_evidence.py --example
cargo test --manifest-path rust/arbcore-rs/Cargo.toml
```

不得从本 repository 推断 production trading、contract audit 或 on-chain execution 能力。
