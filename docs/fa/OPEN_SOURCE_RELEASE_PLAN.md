# برنامه Public Release

هدف، انتشار یک alpha offline MVP قابل بررسی و قابل بازتولید است؛ نه انتشار trading bot.

کارهای اصلی:

1. پاک‌سازی و scan کامل history و objectهای unreachable.
2. rotation credentialهای تاریخی و خارج‌کردن backupهای قدیمی از publication path.
3. هماهنگ‌کردن version `0.1.0-alpha`، URLها و release evidence.
4. refresh کامل mirrorهای فارسی و چینی.
5. اجرای test، Rust parity، dependency scan، secret scan، Docker و clean-clone verification.

تا زمان satisfiedشدن همه gateها، `public_release_ready` باید false بماند.
