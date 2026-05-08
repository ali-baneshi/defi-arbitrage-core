# 项目概览

defi-arbitrage-core 是一个面向本地市场快照的离线分析核心。这个仓库刻意不是“交易机器人”：不处理钱包、不保存私钥、不调用实时 RPC、不监听 mempool，也不执行交易。

`docs/en/` 中的英文文档是 canonical source。中文文档用于辅助阅读，但涉及 release-critical 判断时应以英文文档为准。

## 推荐入口

- 先看 `README.md`，了解仓库承诺与快速命令。
- 再看 `docs/en/STATUS.md`，了解当前成熟度和 blocker。
- 阅读 `docs/en/PROJECT_BOUNDARIES.md`，避免推断出仓库并不具备的能力。
- 若你是 reviewer，请先读 `docs/en/REVIEWER_GUIDE.md`。
- 对 validation 与发布证据，请看 `docs/en/VALIDATION.md` 和 `docs/en/RELEASE_EVIDENCE.md`。

## 目标

这个核心面向 research、simulation、education，以及更大系统的基础设施层。重点是本地输入、显式 validation、稳定的数据契约，以及易于扩展的接口。

## 当前能力

- 本地市场快照的离线分析
- text 与 JSON 输出
- 带显式 `network` 字段的多网络快照
- Solidity / Vyper 模板验证
- 可选 Rust analyzer，并在失败时安全 fallback 到 Python

## 不包含的能力

- live trading
- wallet 或 secret 管理
- 合约部署或审计
- cross-chain bridge 或 routing

## 建议阅读顺序

1. `docs/en/STATUS.md`
2. `docs/en/PROJECT_BOUNDARIES.md`
3. `docs/en/ARCHITECTURE.md`
4. `docs/en/VALIDATION.md`
5. `docs/en/RELEASE_EVIDENCE.md`

## 延伸阅读

- `docs/zh/README_DETAILS.md` 解释目标用户、采用模式与实际适配场景。
- `docs/zh/ADVANCED_README.md` 更深入说明边界、信任模型与扩展方式。
