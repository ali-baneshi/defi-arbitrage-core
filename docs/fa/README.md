# نمای کلی پروژه

defi-arbitrage-core یک هسته آفلاین برای تحلیل snapshotهای محلی بازار است. این repository عمداً «ربات معامله‌گر» نیست: wallet، private key، RPC زنده، mempool، امضای تراکنش و اجرای معامله در آن وجود ندارد.

نسخه انگلیسی در `docs/en/` منبع canonical است. نسخه فارسی برای مطالعه و درک سریع مفید است، اما برای release-critical decision باید به انگلیسی رجوع شود.

## مسیرهای شروع پیشنهادی

- برای وعده کلی پروژه و commandهای سریع، `README.md` را بخوانید.
- برای وضعیت فعلی و blockerها، `docs/en/STATUS.md` را ببینید.
- برای مرزهای پروژه و چیزهایی که نباید از آن نتیجه گرفت، `docs/en/PROJECT_BOUNDARIES.md` را بخوانید.
- برای مسیر reviewer، `docs/en/REVIEWER_GUIDE.md` را بخوانید.
- برای validation و release evidence، `docs/en/VALIDATION.md` و `docs/en/RELEASE_EVIDENCE.md` را ببینید.

## هدف

این هسته برای research، simulation، education و ساخت زیرساخت‌های بزرگ‌تر طراحی شده است. تمرکز آن روی ورودی محلی، validation صریح، output قابل ماشین‌خواندن و extension pointهای پایدار است.

## قابلیت‌های فعلی

- تحلیل آفلاین snapshotهای محلی بازار
- خروجی text و JSON
- پشتیبانی از snapshotهای چندشبکه‌ای با فیلد صریح `network`
- contract template validation برای Solidity و Vyper
- analyzer اختیاری Rust با fallback امن به Python

## چیزهایی که شامل نمی‌شود

- live trading
- مدیریت wallet یا secret
- deployment یا audit قرارداد
- bridge، cross-chain routing یا execution چندشبکه‌ای

## ترتیب مطالعه

1. `docs/en/STATUS.md`
2. `docs/en/PROJECT_BOUNDARIES.md`
3. `docs/en/ARCHITECTURE.md`
4. `docs/en/VALIDATION.md`
5. `docs/en/RELEASE_EVIDENCE.md`

## مطالعه تکمیلی

- `docs/fa/README_DETAILS.md` کاربران هدف، الگوهای استفاده و تناسب عملی را توضیح می‌دهد.
- `docs/fa/ADVANCED_README.md` boundaryها، مدل اعتماد و توسعه‌پذیری را عمیق‌تر شرح می‌دهد.
