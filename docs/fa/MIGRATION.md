# یادداشت‌های مهاجرت و بازطراحی

## سیستم قبلی

نسخه اولیه repository یک stack بزرگ تحقیق و execution برای آربیتراژ Polygon بود که Python، Rust، Solidity، مدل‌های AI، پیکربندی زنده، log، database، فایل‌های RPC و artifactهای تولیدی را در خود داشت.

## هسته جدید

اکنون repository به یک هسته Python برای تحلیل آفلاین تبدیل شده است. بخش حفظ‌شده، کشف فرصت مبتنی بر graph با gateهای policy صریح و protocolهای توسعه‌پذیری است.

## موارد حذف‌شده

- entrypointهای live trading
- کد private key و wallet
- قراردادهای هوشمند و scriptهای deployment
- آزمایش‌های runtime مبتنی بر Rust
- مدل‌های AI و scriptهای training
- logها، cacheها، databaseها و stateهای تولیدی
- endpointهای خصوصی RPC و env fileهای ناامن

## دلیل این بازطراحی

یک زیرساخت public و reusable باید امن، کوچک، قابل آموزش و قابل توسعه باشد؛ بدون اینکه ریسک عملیاتی یک سیستم معامله زنده را به ارث ببرد.
