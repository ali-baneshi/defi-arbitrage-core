# 扩展指南

## 添加 Provider

实现 `MarketDataProvider.load_snapshot()` 并返回已验证的 `MarketSnapshot`。Provider 是不可信输入边界；它们应规范化外部数据、拒绝不支持的字段，并保留显式 `network` 标识，以便系统安全分析多条链。

## 添加 Reporter

实现 `Reporter.render(opportunities) -> str`。Reporter 不应输出 secret、credential 或敏感运维元数据。

## 添加 Policy 逻辑

保持 policy 显式且独立。优先使用单独的包装层过滤 `Opportunity`，而不是把规则隐藏在 provider 中。为边界条件和负例补充测试。

## 添加合约模板

1. 将 Solidity 文件放到 `contracts/solidity/`，或将 Vyper 文件放到 `contracts/vyper/`。
2. 在文件中包含 `ARBCORE_CONTRACT_TEMPLATE` 与 `NOT AUDITED`。
3. 避免真实地址、RPC URL、部署脚本和危险原语。
4. 将 artifact 加入 `contracts/contract-manifest.json`。
5. 运行 `PYTHONPATH=src python scripts/validate_contracts.py`。
6. 如果有用户可见变化，同时更新测试和文档。

## 添加另一种语言

将 JSON snapshot 和 validation report 视为跨语言契约。在公开发布之前，补齐 manifest language 值、扩展规则、validator 规则、示例、schema、文档和测试。

## 添加另一条网络

核心不需要为每条链重新实现 engine。要专业地扩展到新网络：

1. 用稳定的 `network` 标签生成 snapshot，例如 `ethereum`、`arbitrum`、`optimism`、`base`、`avalanche` 或 `bnb-chain`。
2. 在同一网络内保持 asset 符号、venue 标签以及 fee/liquidity 语义一致。
3. 如果外围 tooling 引入新的 failure mode，就补充确定性示例和负例测试。
4. 将 RPC、bridge、gas、sequencer 和 execution 相关问题留在本 package 之外。

## Rust 加速边界

Rust 扩展必须保持本地 JSON 输入/输出契约，并且始终是可选组件。故障必须被隔离，这样在 Rust 不可用时 Python 仍能继续工作。
