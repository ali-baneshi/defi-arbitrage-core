# Configuration

Settings are available through CLI flags or environment variables. No setting should contain private keys, tokens, wallet seeds, or RPC credentials.

| Environment Variable | Default | Description |
| --- | --- | --- |
| `ARBCORE_PROVIDER_FILE` | `examples/market_snapshot.json` | Local snapshot path. |
| `ARBCORE_DEFAULT_NETWORK` | `polygon` | Default network label used by local operator diagnostics and surrounding tooling. |
| `ARBCORE_MIN_PROFIT_BPS` | `5` | Minimum cycle profit after fees. |
| `ARBCORE_MAX_HOPS` | `4` | Maximum cycle length. |
| `ARBCORE_MIN_LIQUIDITY` | `0` | Minimum edge liquidity. |
| `ARBCORE_MAX_NOTIONAL` | `10000` | Capacity ceiling used in opportunity estimates. |
| `ARBCORE_MAX_RESULTS` | `25` | Maximum returned opportunities. |

CLI flags override environment values for a single run. Invalid configuration raises `ConfigurationError` or `PolicyError`, and the CLI exits with code `2`.

Contract validation reads repository files under `contracts/` and does not use environment secrets.

## Multi-Network Snapshot Contract

`MarketSnapshot` now carries an explicit `network` field. This keeps local analysis portable across Polygon, Ethereum, Arbitrum, Optimism, Base, Avalanche, BNB Chain, and other environments without changing the analysis engine itself.

- Snapshot producers should always emit `network`.
- Opportunity output preserves the same `network`.
- Network labels are simple normalized strings, not RPC endpoints or chain metadata objects.
- The core intentionally does not hard-code a short allowlist of chains; infrastructure builders can decide their own supported network catalog outside this package.

## Fail-Closed Bounds

To reduce accidental resource exhaustion in public examples and CI, `RiskPolicy` rejects `max_hops` above `8` and `max_results` above `1000`. Snapshot validation rejects non-object metadata, non-string timestamps, empty sources, empty network labels, oversized source/network fields, and snapshots above `10000` edges. These limits are conservative defaults for the offline MVP, not performance claims.
