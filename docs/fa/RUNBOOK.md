# Runbook

پیش‌نیاز baseline، Python 3.10+ و نبودن network dependency است.

```bash
PYTHONPATH=src python scripts/validate_all.py --include-rust
PYTHONPATH=src python scripts/validate_golden_fixtures.py
PYTHONPATH=src python scripts/release_readiness.py --json
PYTHONPATH=src python scripts/audit_public_remote.py
```

اگر gateی blocked است، tag یا public release ایجاد نکنید. release evidence باید
non-secret باشد و rotation credential، history scan، حذف backupهای قدیمی و refresh
مستندات را با شواهد خارجی ثابت کند.

پس از commit تغییرات hardening، `PYTHONPATH=src python scripts/verify_public_snapshot.py`
snapshot عمومی فعلی را بررسی می‌کند و هیچ tag، push یا rewriteای انجام نمی‌دهد.
