# 迁移与重构说明

## 旧系统

最初的 repository 是一个大型 Polygon 套利研究与执行栈，包含 Python、Rust、Solidity、AI 模型、实时配置、日志、数据库、RPC 端点文件和生成产物。

## 新核心

现在的 repository 已收敛为一个 Python 离线分析核心。保留下来的本质是基于 graph 的机会发现，以及显式 policy gate 和扩展协议。

## 已移除内容

- live trading 入口
- private key 与 wallet 代码
- 智能合约和 deployment 脚本
- Rust runtime 实验
- AI 模型与 training 脚本
- 日志、cache、database 和生成状态
- 私有 RPC endpoint 与不安全 env 文件

## 重构原因

一个公开、可复用的基础设施应当是安全、精简、可讲解、可扩展的，而不应继承实时交易系统的运维风险。
