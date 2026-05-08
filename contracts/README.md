# Smart-Contract Templates

This workspace contains offline smart-contract templates that show how reviewed integrations could be organized around arbcore analysis results.

Supported languages in this repository:

- Solidity: `contracts/solidity/`
- Vyper: `contracts/vyper/`

These files are **NOT AUDITED**, not compiled by this repository, not deployment scripts, and not production trading code. They contain the marker `ARBCORE_CONTRACT_TEMPLATE` so the dependency-free validator can distinguish intentional templates from arbitrary source files.

Validate the workspace with:

```bash
PYTHONPATH=src python scripts/validate_contracts.py
PYTHONPATH=src python scripts/validate_contracts.py --json
```

The validator checks manifest shape, language/path consistency, safety markers, obvious secret patterns, hard-coded addresses, RPC URLs, and dangerous primitives. It is not a compiler and not a security audit.
