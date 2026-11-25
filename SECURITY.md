# Security policy

## Scope

This is an offline analysis tool. It intentionally excludes private keys,
wallets, RPC endpoints, transaction signing, contract deployment, and trade
execution.

## Input handling

- A snapshot is a local file the caller explicitly names.
- Files larger than 50 MiB are rejected before reading.
- Files must be UTF-8 JSON; shape and domain validation run before analysis.
- Unknown keys, explicit nulls, self-loops, non-finite numbers, and invalid
  fees are rejected.
- The number of edges, node degree, and search expansions are bounded.
- The process does not open network connections, read environment
  configuration, or spawn a second engine.

## Reporting a vulnerability

Report suspected vulnerabilities privately to Ali Baneshi at
baneshi712@gmail.com. Include affected files, reproduction steps, and expected
impact. Do not include real secrets in a report.

## Secret hygiene

Do not commit `.env` files, private keys, API tokens, wallet data, logs,
databases, or generated build metadata. This repository has no secrets and
requires none.

## History warning

If you republish an old clone or backup, independently scan its full Git
history and do not publish old `.git` directories. The current tree is not a
claim about every historical object in every copy.
