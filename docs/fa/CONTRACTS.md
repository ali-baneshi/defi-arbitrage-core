# قراردادها

فایل‌های `contracts/` فقط templateهای Solidity و Vyper هستند. این repository آن‌ها را
compile، deploy، audit یا execute نمی‌کند. هر template باید markerهای
`ARBCORE_CONTRACT_TEMPLATE` و `NOT AUDITED` را داشته باشد.

validator فقط manifest، path، hash، زبان، markerهای ایمنی، secretهای آشکار، addressهای
hard-coded، RPC URL و primitiveهای خطرناک را بررسی می‌کند. این بررسی جایگزین compiler،
formal verification یا professional audit نیست.

```bash
PYTHONPATH=src python scripts/validate_contracts.py --json
```
