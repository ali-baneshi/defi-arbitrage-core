# Security

## Scope

The repository is an offline analysis core. It excludes private-key handling, signing, transaction broadcast, live RPC integrations, contract deployment, and trade execution.

## Git History Status

The active tree is sanitized, but previous local history contained sensitive material. Treat any historical credentials as compromised, rotate them, and do not publish old `.git` backups.

## Safe Defaults

- Local file provider only.
- No network calls.
- No wallet or signing APIs.
- Explicit exceptions with non-secret-bearing messages.
- Contract templates are inert and marked `NOT AUDITED`.

## Contract Security Model

`contracts/` contains Solidity and Vyper templates only. `scripts/validate_contracts.py` rejects obvious secret patterns, hard-coded addresses, RPC URLs, missing safety notices, and dangerous primitives. This validation is not compilation and not an audit. Do not deploy these templates without independent review.

## Local Checks

```bash
PYTHONPATH=src python scripts/validate_all.py
./scripts/secret_scan.sh
```

The secret scan is lightweight active-tree scanning and does not replace independent history scanning such as gitleaks.

## Reporting Vulnerabilities

Report suspected vulnerabilities privately to Ali Baneshi at baneshi712@gmail.com. Include affected files, reproduction steps, expected impact, and whether any secret exposure is involved.
