# مرزهای پروژه

- ورودی و خروجی فقط محلی است؛ snapshotها untrusted هستند.
- Python در `src/arbcore/` مرجع validation، orchestration و API است.
- Rust فقط analyzer اختیاری process-boundary است.
- network فقط metadata declarative است و chain identity را verify نمی‌کند.
- پروژه RPC، wallet، key، signing، execution، deployment یا production funds ندارد.
- قراردادهای Solidity و Vyper template هستند؛ compile، audit، deploy و execute نمی‌شوند.
- local validation readiness با public یا production readiness یکی نیست.
