# 详细概览

## 这套基础设施适合谁

这套基础设施面向那些需要确定性 DeFi 市场分析、但不希望继承实时交易栈运维风险的人和团队。

它尤其适合：

- 希望在本地 snapshot 上验证 path-finding 思路的 researcher
- 需要跨多个 EVM 网络比较市场结构的量化开发者
- 研究流动性拓扑与 route 质量的协议分析师
- 构建 scoring、alerting 或 simulation 系统的 backend 工程师
- 在加入自己的 ingestion、execution、governance 或 compliance 层之前，需要一个干净分析内核的公司

它并不适合寻找一键式交易产品的用户。

## 它解决什么问题

很多团队最初依赖零散 notebook、临时脚本，或夸大能力的 bot 仓库。这样会让一些基础工程问题变得难以回答，例如哪些输入可信、同一个 snapshot 是否总能得到相同输出、validation 失败如何表达、以及如何在不重写 engine 的情况下扩展到新网络。

这个 repository 通过一个可复用、contract-driven 的分析核心，解决了这个更窄但非常重要的问题。

## 现实的采用方式

最现实的方式，是把这个核心放在更大 pipeline 的中间层。

上游系统可以负责收集 quote、规范化 venue、补充 symbol 信息，或进行条件模拟。这个核心随后对 snapshot 做 validation，执行有界循环分析，并产出结构化的 candidate。下游系统再决定如何评分、存储、告警、审查，或在独立控制下执行这些候选。

这种模式适合个人开发者、研究团队、内部工具组和基础设施公司，因为它让核心保持清晰，同时允许外围系统独立演进。

## 为什么多网络设计重要

显式 `network` 字段让 engine 不再受限于单链叙事。只要 snapshot 遵守同一套 contract，团队就可以在 Base、Ethereum、Arbitrum、Optimism、Polygon、Avalanche、BNB Chain、本地模拟或私有环境中复用同一个确定性核心。

这提升了复用性、可审查性和测试覆盖率，也减少了每条链都各自 fork engine 导致行为漂移的风险。

## 为什么 Validation 是核心能力

Validation 是这个 repository 最专业的部分之一。

Schema 级 validation 记录了 snapshot、report 和 diagnostics 的公开结构。Runtime validation 则负责执行业务规则，例如显式网络身份、合理 edge、受限 policy，以及对损坏输入进行 fail-closed 拒绝。二者结合后，系统更适合作为大型工具链中的嵌入式基础设施。

## 团队仍需要补齐什么

这个 repository 故意不是完整产品。采用它的团队仍需要自行决定：

- 数据采集与规范化
- storage 与 retention
- scheduling 与 orchestration
- risk approval 与 execution control
- observability、incident response 与 compliance review
- production secret 与 network access 管理

这种分离是设计优势，不是功能缺失。
