# پیکربندی

تنظیمات از طریق CLI flagها یا environment variableها قابل کنترل‌اند. هیچ تنظیمی نباید شامل private key، token، seed phrase، wallet secret یا RPC credential باشد.

| متغیر محیطی | مقدار پیش‌فرض | توضیح |
| --- | --- | --- |
| `ARBCORE_PROVIDER_FILE` | `examples/market_snapshot.json` | مسیر snapshot محلی |
| `ARBCORE_DEFAULT_NETWORK` | `polygon` | برچسب پیش‌فرض شبکه برای diagnostics و tooling اطراف هسته |
| `ARBCORE_MIN_PROFIT_BPS` | `5` | حداقل سود بعد از fee |
| `ARBCORE_MAX_HOPS` | `4` | بیشینه طول cycle |
| `ARBCORE_MIN_LIQUIDITY` | `0` | حداقل liquidity قابل قبول |
| `ARBCORE_MAX_NOTIONAL` | `10000` | سقف capacity تخمینی |
| `ARBCORE_MAX_RESULTS` | `25` | بیشترین تعداد نتیجه |

CLI flagها برای همان اجرا روی environment variableها override می‌شوند.

## قرارداد snapshot چندشبکه‌ای

`MarketSnapshot` اکنون فیلد صریح `network` دارد. این کار باعث می‌شود همان هسته برای Polygon، Ethereum، Arbitrum، Optimism، Base، Avalanche، BNB Chain و محیط‌های دیگر قابل استفاده باشد.

- producerهای snapshot بهتر است همیشه `network` را تنظیم کنند.
- output opportunity همان `network` را حفظ می‌کند.
- این فیلد فقط label است، نه RPC endpoint و نه chain registry.
- تصمیم درباره catalog رسمی شبکه‌های پشتیبانی‌شده باید در لایه بالاتر انجام شود، نه داخل این package.

## حدود fail-closed

برای جلوگیری از مصرف ناخواسته منابع، `RiskPolicy` مقدار `max_hops` بالاتر از `8` و `max_results` بالاتر از `1000` را رد می‌کند. validation همچنین metadata نامعتبر، timestamp نامعتبر، source خالی، network خالی و snapshotهای بزرگ‌تر از `10000` edge را رد می‌کند.
