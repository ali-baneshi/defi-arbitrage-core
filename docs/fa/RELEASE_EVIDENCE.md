# شواهد Release

فایل canonical شواهد `release/release-evidence.json` است و باید با
`schemas/release_evidence.schema.json` سازگار باشد. repository فقط فایل
example را منتشر می‌کند؛ این فایل عمداً gateها را blocked نگه می‌دارد.

شواهد لازم:

- rotation همه credentialهای تاریخی؛
- حذف یا خارج‌بودن backupهای قدیمی `.git` از مسیر انتشار؛
- scan مستقل کل history، شامل objectهای unreachable؛
- refresh کامل مستندات فارسی و چینی.

فایل شواهد نباید secret، token، private key یا مسیر خصوصی سیستم را شامل شود.
نسخه انگلیسی منبع canonical برای release است.
