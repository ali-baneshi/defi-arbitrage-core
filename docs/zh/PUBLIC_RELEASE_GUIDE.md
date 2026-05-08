# 公开发布指南

## 推荐的 GitHub About 文本

面向本地市场快照的确定性多网络 DeFi 分析核心。validation-first、contract-driven、默认离线。

## 推荐的简短描述

一个可复用的离线 DeFi 套利分析内核，具备显式 validation、多网络支持、稳定 JSON 契约和可选 Rust 加速。

## 推荐 Topics

- `defi`
- `arbitrage`
- `market-analysis`
- `quant-research`
- `graph-algorithms`
- `json-schema`
- `python`
- `rust`
- `developer-tools`
- `infrastructure`

## 首个公开版本的定位

首个公开版本应被定位为 alpha offline MVP。最专业的叙事不是把它包装成 trading bot，而是把它描述为一个确定性、validation-first、具有明确 trust boundary 和清晰扩展点的 DeFi 分析内核。

## 推荐的 Release Notes 结构

### 标题

`defi-arbitrage-core v0.1.0-alpha`

### 开场说明

这是 `defi-arbitrage-core` 的首个公开版本：一个面向本地 DeFi 市场 snapshot 的可复用离线分析核心。项目重点在于确定性 validation、有界循环分析、多网络可移植性、稳定 JSON 契约，以及分析层与执行层之间的清晰分离。

### 亮点

- 公开 `defi-arbitrage-core` 品牌与 CLI 入口
- 通过 `network` 字段显式支持多网络 snapshot
- fail-closed 的 schema 与 runtime validation
- 结构化 JSON 输出、diagnostics 与 release-readiness 报告
- 通过安全 process boundary 提供可选 Rust analyzer，并保留 Python fallback
- 面向仓库级合约工作流的 Solidity / Vyper 模板 validation
- 用于公开上手的英文、波斯文和中文文档

### 范围声明

这个版本是 alpha 级基础设施版本。不包含 wallet、signing、实时 RPC ingestion、trade execution、合约 deployment，亦不做 production-readiness 声明。

### 需要保留的发布证据

请保存以下内容：

- `PYTHONPATH=src python scripts/validate_all.py --include-rust`
- `PYTHONPATH=src python scripts/release_readiness.py --json`
- 独立 history scan 的结果
- 关于 credential rotation 与旧历史排除的 maintainer 证明

## 在将仓库设为公开之前

请在实践中确认以下事项，而不是只写在文档里：

- 历史 credential 已轮换
- 旧 `.git` 备份不会被意外发布
- release evidence 已被保存和归档
- repository 描述与 topics 符合真实 scope
- 没有文档暗示 live trading 或 production safety
