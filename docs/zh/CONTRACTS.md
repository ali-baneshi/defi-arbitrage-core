# 合约

`contracts/` 中的 Solidity 与 Vyper 文件只是 template。本 repository 不会对其
进行 compile、deploy、audit 或 execute。每个 template 必须包含
`ARBCORE_CONTRACT_TEMPLATE` 与 `NOT AUDITED` marker。

validator 只检查 manifest、path、hash、语言、safety marker、明显 secret、hard-coded
address、RPC URL 与危险 primitive。它不能替代 compiler、formal verification 或 professional audit。

```bash
PYTHONPATH=src python scripts/validate_contracts.py --json
```
