# وضعیت پروژه

- بلوغ: alpha offline MVP
- تحلیل snapshot محلی و validation قطعی پشتیبانی می‌شود.
- Rust analyzer اختیاری است و Python مرجع canonical باقی می‌ماند.
- live RPC، wallet، signing، broadcast، execution و deployment پشتیبانی نمی‌شود.
- `local_validation_ready` به معنی آمادگی public یا production نیست.
- `production_ready` باید همیشه `false` باقی بماند.

وضعیت release را با این دستور بررسی کنید:

```bash
PYTHONPATH=src python scripts/release_readiness.py --json
```

برای تصمیم‌های release-critical، نسخه انگلیسی در `docs/en/` canonical است.
