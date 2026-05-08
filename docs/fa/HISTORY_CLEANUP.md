# سابقه پاک‌سازی تاریخچه

repository از یک working tree پاک‌سازی‌شده بازسازی شد و با Git history تازه دوباره initialize شد.

## چه کارهایی انجام شد

- پوشه قدیمی `.git` از مسیر این repository خارج شد.
- یک Git repository جدید روی branch `main` ساخته شد.
- فایل‌های MVP پاک‌سازی‌شده به‌عنوان root commit جدید ثبت شدند.
- قبل و بعد از بازسازی، secret scan روی active tree اجرا شد.

## اقدام امنیتی باقیمانده

هر credentialی که در history قبلی وجود داشته باید compromise‌شده فرض شود و rotate شود. از انتشار یا کپی backup قدیمی `.git` در هر فضای عمومی خودداری کنید.

## بررسی پیشنهادی

```bash
git log --oneline --all
./scripts/secret_scan.sh
PYTHONPATH=src python scripts/validate_examples.py
```

پیش از انتشار عمومی، یک ابزار مستقل مثل `gitleaks` هم اجرا کنید.
