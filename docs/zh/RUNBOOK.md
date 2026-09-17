# Runbook

baseline 需要 Python 3.10+，并且不依赖网络。

```bash
PYTHONPATH=src python scripts/validate_all.py --include-rust
PYTHONPATH=src python scripts/validate_golden_fixtures.py
PYTHONPATH=src python scripts/release_readiness.py --json
```

只要有 gate 处于 blocked，就不要创建 tag 或进行 public release。release evidence
必须是 non-secret，并用外部证据证明 credential rotation、history scan、旧备份排除和文档刷新。
