# راهنمای Validation

baseline بدون dependency:

```bash
PYTHONPATH=src python scripts/validate_all.py
PYTHONPATH=src python scripts/validate_all.py --include-rust
```

workflowهای مهم:

```bash
PYTHONPATH=src python scripts/validate_output_contracts.py
PYTHONPATH=src python scripts/validate_release_evidence.py --example
PYTHONPATH=src python scripts/release_readiness.py --json
```

`release_readiness.py` فقط وقتی gateهای public release را satisfied می‌داند که
`release/release-evidence.json` با شواهد non-secret و خارجی معتبر وجود داشته باشد.
فایل example عمداً blocked است و مجوز انتشار نیست.

این پروژه فقط تحلیل nominal را انجام می‌دهد و نتیجه آن تضمین سود یا قابلیت اجرای
on-chain نیست. نسخه انگلیسی canonical است.
