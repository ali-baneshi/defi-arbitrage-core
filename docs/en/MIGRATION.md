# Migration and Refactor Notes

## Previous System

The original repository was a large Polygon arbitrage research and execution stack with Python, Rust, Solidity, AI models, live configuration, logs, databases, RPC endpoint files, and generated artifacts.

## New Core

The repository is now a Python-only offline analysis core. The retained essence is graph-based opportunity discovery with explicit policy gates and extension protocols.

## Removed

- Live trading entrypoints.
- Private-key and wallet code.
- Smart contracts and deployment scripts.
- Rust runtime experiments.
- AI models and training scripts.
- Logs, caches, databases, and generated state.
- Private RPC endpoints and unsafe env files.

## Reason

A public open-source foundation must be secure, small, teachable, and extensible without inheriting operational risk from a live trading system.
