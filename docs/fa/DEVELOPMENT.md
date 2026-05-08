# توسعه

نسخه انگلیسی canonical است و این صفحه یک خلاصه best-effort برای contributorها است.

## مسیر توسعه پیشنهادی

1. تغییر را کوچک و قابل review نگه دارید.
2. قبل از هر چیز boundaryهای تحلیل آفلاین را حفظ کنید.
3. برای behaviorهای جدید test و validation اضافه کنید.
4. اگر contract عمومی یا CLI تغییر می‌کند، docs و schemaها را هم به‌روزرسانی کنید.

## commandهای اصلی

```bash
PYTHONPATH=src python scripts/validate_all.py
PYTHONPATH=src python scripts/validate_all.py --include-rust
python -m pytest -q
python -m ruff check .
```

## استانداردهای تغییر

- execution logic زنده، wallet، signing و RPC را وارد هسته نکنید.
- interfaceهای پایدار را صریح نگه دارید.
- اگر translationها عقب می‌مانند، `docs/TRANSLATION_STATUS.md` را به‌روزرسانی کنید.
