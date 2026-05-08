# راهنمای توسعه‌پذیری

## افزودن provider

متد `MarketDataProvider.load_snapshot()` را پیاده‌سازی کنید و یک `MarketSnapshot` معتبر برگردانید. providerها مرز ورودی غیرقابل‌اعتماد هستند؛ بنابراین باید داده بیرونی را نرمال‌سازی کنند، فیلدهای پشتیبانی‌نشده را رد کنند و مقدار `network` را به‌صورت صریح حفظ کنند تا تحلیل چندشبکه‌ای ایمن بماند.

## افزودن reporter

متد `Reporter.render(opportunities) -> str` را پیاده‌سازی کنید. reporter نباید secret، credential یا metadata عملیاتی حساس را چاپ کند.

## افزودن policy

policy را شفاف و جدا از provider نگه دارید. بهتر است یک لایه جدا `Opportunity`ها را فیلتر کند تا اینکه ruleها داخل منبع داده پنهان شوند. برای مرزها و caseهای منفی test اضافه کنید.

## افزودن template قرارداد

1. فایل Solidity را زیر `contracts/solidity/` یا فایل Vyper را زیر `contracts/vyper/` قرار دهید.
2. عبارت‌های `ARBCORE_CONTRACT_TEMPLATE` و `NOT AUDITED` را داخل فایل بگذارید.
3. از آدرس واقعی، RPC URL، script استقرار و primitiveهای خطرناک استفاده نکنید.
4. artifact را به `contracts/contract-manifest.json` اضافه کنید.
5. دستور `PYTHONPATH=src python scripts/validate_contracts.py` را اجرا کنید.
6. اگر تغییر user-facing است، test و doc را هم به‌روزرسانی کنید.

## افزودن زبان دیگر

snapshotهای JSON و reportهای validation را به‌عنوان contract مستقل از زبان نگه دارید. قبل از انتشار عمومی، مقدار language در manifest، ruleهای extension، validatorها، exampleها، schemaها، docs و testها را کامل کنید.

## افزودن شبکه دیگر

برای هر شبکه جدید لازم نیست engine جدید بنویسید. برای توسعه حرفه‌ای به شبکه‌های دیگر:

1. snapshotها را با برچسب پایدار `network` مثل `ethereum`، `arbitrum`، `optimism`، `base`، `avalanche` یا `bnb-chain` تولید کنید.
2. نام assetها، venueها و معناشناسی fee/liquidity را داخل همان شبکه سازگار نگه دارید.
3. اگر tooling پیرامونی failure mode جدیدی ایجاد می‌کند، example قطعی و test منفی اضافه کنید.
4. concernهای RPC، bridge، gas، sequencer و execution را بیرون از این package نگه دارید.

## مرز شتاب‌دهی Rust

افزونه‌های Rust باید همان contract محلی JSON ورودی/خروجی را حفظ کنند و اختیاری بمانند. خطاها باید ایزوله شوند تا در نبود Rust، Python بتواند ادامه دهد.
