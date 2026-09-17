# Trust Boundaries

ورودی‌های untrusted شامل snapshot JSON، providerها، contract templateها و خروجی Rust هستند.
همه این موارد باید قبل از مصرف downstream validation شوند.

اجزای trusted محلی شامل Python canonical، schemaها و validation scriptها هستند؛
این اعتماد به معنی audit امنیتی یا تضمین production نیست.

private key، wallet، signing، broadcast، live trading، deployment، gas analysis و
formal verification خارج از boundary هستند.
