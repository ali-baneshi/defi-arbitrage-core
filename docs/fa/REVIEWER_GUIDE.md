# راهنمای Reviewer

منابع canonical:

- Python: `src/arbcore/`
- قراردادهای JSON: `schemas/`
- validation: `scripts/validate_*.py`
- readiness: `scripts/release_readiness.py`
- evidence: `release/release-evidence.json`

مسیر سریع review:

```bash
PYTHONPATH=src python scripts/validate_all.py --include-rust
PYTHONPATH=src python scripts/release_readiness.py --json
PYTHONPATH=src python scripts/validate_release_evidence.py --example
cargo test --manifest-path rust/arbcore-rs/Cargo.toml
```

از این repository نباید production trading، contract audit یا on-chain execution نتیجه‌گیری شود.
