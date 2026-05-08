# معماری

## مرز اصلی

مرز پروژه ورودی محلی، validation قطعی، تحلیل قطعی و خروجی محلی است. هر چیزی که به private key، RPC زنده، signing، wallet، deployment یا production funds مربوط باشد، بیرون از این package قرار می‌گیرد.

## دیاگرام سطح بالا

```text
snapshot/provider محلی
        |
        v
validation در سطح schema و runtime
        |
        v
engine تحلیلی deterministic
        |
        +--> reporterهای text/json
        |
        +--> مسیر اختیاری Rust
        |
        +--> سیستم‌های بزرگ‌تر پژوهشی یا اجرایی
```

## ماژول‌ها

- `arbcore.models`: مدل‌های immutable مانند `Edge`، `MarketSnapshot`، `RiskPolicy` و `Opportunity`
- `arbcore.validation`: validation بدون وابستگی خارجی و helperهای serialization
- `arbcore.providers`: protocolها و providerهای ورودی
- `arbcore.engine`: جست‌وجوی cycleهای محدود
- `arbcore.reporters`: خروجی text و JSON
- `arbcore.service`: مرز process-boundary برای analyzer اختیاری Rust
- `arbcore.contracts`: manifest و validation برای contract templateها

## جریان داده بازار

1. provider یک `MarketSnapshot` محلی را بارگذاری می‌کند.
2. snapshot و edgeها normalize و validate می‌شوند.
3. فیلد صریح `network` حفظ می‌شود.
4. `AnalysisEngine` گراف جهت‌دار می‌سازد.
5. engine cycleها را تا حد `max_hops` جست‌وجو می‌کند.
6. سود بعد از fee محاسبه می‌شود.
7. opportunityها با همان `network` خروجی داده می‌شوند.

## مرز چندشبکه‌ای

هسته اکنون network-aware است اما عمداً network-agnostic باقی می‌ماند:

- هسته فقط label شبکه را حمل می‌کند.
- logic مخصوص chain، gas، bridge، RPC یا execution داخل آن نیست.
- سیستم‌های بزرگ‌تر می‌توانند همین هسته را برای Polygon، Ethereum، Arbitrum، Optimism، Base، Avalanche یا BNB Chain reuse کنند.

## مرز اعتماد

- provider و snapshot ورودی untrusted هستند.
- خروجی Rust تا زمانی که parse و validate نشود trusted نیست.
- contract templateها untrusted هستند و validation آن‌ها audit محسوب نمی‌شود.
