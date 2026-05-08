# 配置

设置可以通过 CLI 参数或环境变量控制。任何设置都不应包含 private key、token、seed phrase、wallet secret 或 RPC credential。

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `ARBCORE_PROVIDER_FILE` | `examples/market_snapshot.json` | 本地快照路径 |
| `ARBCORE_DEFAULT_NETWORK` | `polygon` | 供 diagnostics 与外围 tooling 使用的默认网络标签 |
| `ARBCORE_MIN_PROFIT_BPS` | `5` | fee 后的最小利润 |
| `ARBCORE_MAX_HOPS` | `4` | 最大循环长度 |
| `ARBCORE_MIN_LIQUIDITY` | `0` | 最小 liquidity |
| `ARBCORE_MAX_NOTIONAL` | `10000` | 估算 capacity 的上限 |
| `ARBCORE_MAX_RESULTS` | `25` | 返回结果上限 |

CLI 参数会在单次运行中覆盖环境变量。

## 多网络快照契约

`MarketSnapshot` 现在包含显式 `network` 字段，因此同一个核心可以用于 Polygon、Ethereum、Arbitrum、Optimism、Base、Avalanche、BNB Chain 等环境。

- 快照生产方应尽量总是写入 `network`
- opportunity 输出会保留同一个 `network`
- 这个字段只是 label，不是 RPC endpoint，也不是 chain registry
- 支持哪些网络，应由更高层系统决定，而不是由这个 package 写死

## Fail-Closed 边界

为避免意外资源消耗，`RiskPolicy` 会拒绝 `max_hops > 8` 与 `max_results > 1000`。validation 也会拒绝非法 metadata、非法 timestamp、空 source、空 network，以及超过 `10000` 条 edge 的快照。
