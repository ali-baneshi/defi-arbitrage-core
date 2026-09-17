# امنیت

نسخه انگلیسی canonical است و این صفحه خلاصه‌ای برای درک سریع است.

## scope

این repository یک هسته تحلیل آفلاین است و عمداً این موارد را شامل نمی‌شود:

- private key handling
- signing
- live RPC
- deployment
- trade execution

## گزارش آسیب‌پذیری

آسیب‌پذیری‌ها را به‌صورت خصوصی به maintainer گزارش کنید و reproduction step، impact و محدوده فایل‌های درگیر را ذکر کنید.

## hygiene

- secret، token، wallet data یا credential را commit نکنید.
- شاخه عمومی برای محدوده alpha پاک‌سازی شده است، اما clone محلی ممکن است objectهای unreachable تاریخی داشته باشد.
- قبل از انتشار عمومی، history scan مستقل انجام دهید.
- برای scan سطح refs عمومی از `PYTHONPATH=src python scripts/audit_public_remote.py` استفاده کنید؛ این جای scan مستقل را نمی‌گیرد.
- از `PYTHONPATH=src python scripts/release_readiness.py --json` به‌عنوان gate نهایی استفاده کنید.
