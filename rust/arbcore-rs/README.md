# defi-arbitrage-core-rs

Optional Rust analyzer for defi-arbitrage-core.

This binary is a process-boundary acceleration service. It reads the same local snapshot JSON contract as Python and emits the same opportunity JSON contract. It does not use private keys, network access, RPC endpoints, or transaction signing.

## Build

```bash
cargo build --manifest-path rust/arbcore-rs/Cargo.toml
```

## Run

```bash
./rust/arbcore-rs/target/debug/defi-arbitrage-core-rs examples/market_snapshot.json --min-profit-bps 1
```

## Python Fallback

Python can use the Rust binary opportunistically:

```bash
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json --engine auto --rust-binary rust/arbcore-rs/target/debug/defi-arbitrage-core-rs
```

If the binary is missing or fails, the Python adapter falls back to the Python engine.
