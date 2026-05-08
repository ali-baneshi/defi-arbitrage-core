# راهنمای انتشار عمومی

## متن پیشنهادی GitHub About

هسته قطعی و چندشبکه‌ای تحلیل دیفای برای snapshotهای محلی بازار. validation-first، contract-driven و به‌صورت پیش‌فرض آفلاین.

## توضیح کوتاه پیشنهادی

یک هسته reusable برای تحلیل آفلاین آربیتراژ دیفای با validation صریح، پشتیبانی چندشبکه‌ای، قراردادهای JSON پایدار و شتاب‌دهی اختیاری Rust.

## topicهای پیشنهادی

- `defi`
- `arbitrage`
- `market-analysis`
- `quant-research`
- `graph-algorithms`
- `json-schema`
- `python`
- `rust`
- `developer-tools`
- `infrastructure`

## جایگاه اولین انتشار عمومی

اولین انتشار عمومی باید به‌عنوان alpha offline MVP معرفی شود. حرفه‌ای‌ترین روایت این نیست که repository یک trading bot است؛ بلکه این است که یک هسته تحلیل دیفایِ قطعی، validation-first و دارای trust boundaryهای روشن و extension pointهای شفاف است.

## ساختار پیشنهادی release note

### عنوان

`defi-arbitrage-core v0.1.0-alpha`

### افتتاحیه

این اولین انتشار عمومی `defi-arbitrage-core` را معرفی می‌کند؛ یک هسته reusable برای تحلیل آفلاین snapshotهای محلی بازار دیفای. تمرکز پروژه روی validation قطعی، تحلیل چرخه محدود، portability چندشبکه‌ای، قراردادهای JSON پایدار و جداسازی روشن بین analysis و execution است.

### نکات برجسته

- branding عمومی `defi-arbitrage-core` و entrypoint خط فرمان جدید
- پشتیبانی صریح از snapshotهای چندشبکه‌ای با فیلد `network`
- validation fail-closed در سطح schema و runtime
- خروجی JSON ساخت‌یافته، diagnostics و گزارش release-readiness
- analyzer اختیاری Rust پشت process boundary امن با fallback به Python
- validation برای templateهای Solidity و Vyper در workflow سطح repository
- مستندات انگلیسی، فارسی و چینی برای onboarding عمومی

### بیانیه scope

این release یک انتشار زیرساختی در سطح alpha است. شامل wallet، signing، ingest زنده RPC، trade execution، deployment قرارداد یا ادعای production-readiness نیست.

### شواهدی که باید حفظ شوند

یک کپی از این موارد نگه دارید:

- `PYTHONPATH=src python scripts/validate_all.py --include-rust`
- `PYTHONPATH=src python scripts/release_readiness.py --json`
- نتیجه history scan مستقل
- attestation نگه‌دارنده برای credential rotation و حذف history قدیمی از مسیر انتشار

## قبل از public کردن repository

این موارد را در عمل تأیید کنید، نه فقط در متن:

- credentialهای تاریخی rotate شده‌اند
- backupهای قدیمی `.git` قابل انتشار تصادفی نیستند
- release evidence ثبت و بایگانی شده است
- description و topicهای repository با scope واقعی آن هماهنگ‌اند
- هیچ docای ادعای live trading یا production safety نمی‌کند
