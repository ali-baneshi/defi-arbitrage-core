# 架构

## 核心边界

项目边界是本地输入、确定性 validation、确定性分析与本地输出。凡是涉及 private key、实时 RPC、signing、wallet、deployment 或 production funds 的能力，都属于本 package 之外。

## 高层结构图

```text
本地 snapshot/provider
        |
        v
schema + runtime validation
        |
        v
deterministic 分析引擎
        |
        +--> text/json reporter
        |
        +--> 可选 Rust 路径
        |
        +--> 更大的研究或执行系统
```

## 模块

- `arbcore.models`：`Edge`、`MarketSnapshot`、`RiskPolicy`、`Opportunity`
- `arbcore.validation`：无额外依赖的 validation 与 serialization helper
- `arbcore.providers`：输入 provider 协议与实现
- `arbcore.engine`：有界 cycle 搜索
- `arbcore.reporters`：text / JSON 输出
- `arbcore.service`：Rust analyzer 的 process-boundary 适配层
- `arbcore.contracts`：contract template manifest 与 validation

## 市场数据流

1. provider 加载本地 `MarketSnapshot`
2. snapshot 与 edge 会被 normalize 和 validate
3. 显式 `network` 字段会被保留
4. `AnalysisEngine` 构建有向图
5. engine 在 `max_hops` 范围内搜索 cycle
6. profit 按 fee 后结果计算
7. 输出的 opportunity 会保留原始 `network`

## 多网络边界

核心现在是 network-aware，但仍然故意保持 network-agnostic：

- 核心只携带网络标签
- 不内置 chain-specific 的 gas、bridge、RPC 或 execution logic
- 更大的系统可以在 Polygon、Ethereum、Arbitrum、Optimism、Base、Avalanche 或 BNB Chain 上复用同一核心

## 信任边界

- provider 与 snapshot 输入是不可信的
- Rust 输出在 parse/validate 前不可信
- contract template 在通过 validation 前不可信；validation 不是审计
