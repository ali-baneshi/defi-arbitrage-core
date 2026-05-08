# Smart-Contract Support

The contract subsystem lets contributors write, organize, reference, and validate smart-contract templates in two EVM languages: Solidity and Vyper.

## Boundaries

The repository does not compile, deploy, audit, or execute contracts. It provides source organization and deterministic safety checks only.

## Files

- `contracts/contract-manifest.json` declares all supported artifacts.
- `contracts/solidity/FlashArbExecutor.sol` is a Solidity skeleton.
- `contracts/vyper/FlashArbExecutor.vy` is a Vyper skeleton.
- `src/arbcore/contracts/` loads and validates manifests and source files.
- `schemas/contract_manifest.schema.json` documents manifest shape.
- `schemas/contract_validation_report.schema.json` documents report output.

## Validation

```bash
PYTHONPATH=src python scripts/validate_contracts.py
PYTHONPATH=src python scripts/validate_contracts.py --json
```

Validation rejects unsupported languages, unknown manifest keys, incorrect language metadata, paths outside `contracts/`, missing files, source SHA-256 mismatches, manifest entrypoints missing from source, missing safety markers, hard-coded EVM addresses, private-key-like values, RPC URLs, non-local network scope, and dangerous primitives such as `delegatecall`, `selfdestruct`, Solidity inline `assembly`, and Vyper `raw_call`.

## Adding A Contract Template

1. Put Solidity files under `contracts/solidity/` or Vyper files under `contracts/vyper/`.
2. Add `ARBCORE_CONTRACT_TEMPLATE` and `NOT AUDITED` to the source.
3. Avoid real addresses, RPC URLs, deployment scripts, and privileged production logic.
4. Add the artifact to `contracts/contract-manifest.json` with `artifact_type`, `source_sha256`, `networks`, and entrypoint metadata.
5. Run `PYTHONPATH=src python scripts/validate_contracts.py`.
6. Add or update tests when validation behavior changes.

## Safe And Unsafe Changes

Safe template changes are small, reviewed source edits that keep execution disabled, update `source_sha256`, and keep manifest entrypoints synchronized with source functions. Unsafe changes include adding real addresses, RPC URLs, deployment scripts, non-local networks, approval/transfer logic, low-level calls, or claiming audit/production readiness.


## Machine-Checked Manifest Invariants

`contracts/contract-manifest.json` is intentionally narrow:

- `schema_version` must be `1`.
- Languages must be exactly the supported offline set: `solidity` and `vyper`.
- Language validation level must remain `static-template-checks`; local compilers must remain optional.
- Artifact paths must stay below `contracts/` and match the declared language extension.
- Artifact role must be `template`, network scope must be `local`, and tags must include `template` and `non-deployable-without-audit`.
- Source SHA-256 hashes must match the checked-in source files.

These checks protect reviewer workflows from silent expansion into deployment, mainnet, or compiler-dependent behavior. They are not substitutes for compilation, formal verification, integration testing, or professional audits.
