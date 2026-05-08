# 高级基础设施指南

## 设计理念

该项目以基础设施优先为原则。它的价值来自体量小、行为确定、在 review 下仍然清晰。每个主要边界都在回答一个实际问题：什么可以信任，什么必须 validation，什么必须留在包外。

因此，它比那些把分析、execution、wallet、合约、deployment 与运维混在一起的单体套利仓库，更容易审计、扩展和嵌入。

## 系统边界

核心接收本地 snapshot，输出本地 report。这是有意的边界。

在这个边界内部，repository 关注确定性 contract、graph 分析、policy 过滤和稳定输出语义。在这个边界之外，采用者可以在自己的控制下构建 collector、pricing service、decision engine、transaction system 或 deployment workflow。

这使得该 repository 既可以作为公司内部共享基础设施，也可以作为其他开源工具的公共底座。

## 信任模型

Provider 和可选 accelerator 都被视为不可信边界。Provider 可能读取损坏文件或不一致的市场数据，accelerator 也可能失败、发生偏差或暂时不可用。因此系统会显式 validation 输入，并保留 Python 路径，以便在 Rust 不可用时仍维持 authoritative 行为。

这种信任模型适合那些需要可预测 failure mode，而不是乐观假设的组织。

## 可扩展模型

系统被设计为可供个人、创业团队、内部平台团队和大型公司扩展。

常见的扩展方式包括：

- 保持 snapshot contract 稳定
- 为公共或专有数据集增加新的 provider
- 为新网络增加确定性示例和负例测试
- 为内部 dashboard、queue 或 notebook 增加自定义 reporter 或 wrapper
- 将 execution、custody 和 production networking 保持在独立服务中

这种模式让多个团队可以共享同一个 analysis kernel，而不必共享同一套运维架构。

## 适合的组织级用例

对于个人 researcher，它比零散脚本提供更干净的基础。

对于 trading 或 market-structure 团队，它可以作为更大机会审查 pipeline 中的确定性分析阶段。

对于 protocol 或 infrastructure 公司，它可以作为内部服务、simulation 环境或合作方 tooling 的可复用 validation 与 route-analysis 层。

对于 engineering manager 或 reviewer，清晰的 artifact、schema 和 boundary 能显著提升评估效率。

## 面向公开仓库的质量标准

一个公开的基础设施仓库，首先应该容易理解，其次才是令人印象深刻。这意味着一致的命名、现实的示例、稳定的 machine-readable 输出、诚实的成熟度描述，以及明确的发布阻塞项。

这个 repository 试图通过以下方面达到这个标准：

- contract-driven 接口
- 确定性 validation
- 多网络复用
- 有界且可测试的行为
- 清晰的 readiness evidence

## 健康的采用方式

健康的采用方式不会把这个 repository 当成神奇 bot，而是把它当成 kernel。

团队应先理解 contract、validation 自己的 snapshot、审查 failure mode，然后再构建真正需要的外围系统。以这种方式使用时，它会成为 research platform、analytics product、内部开发者工具和受控 execution pipeline 的坚实基础。

## 深入：基础设施边界

### 输入边界

系统接收符合文档化 schema 的本地 JSON snapshot。这个边界是显式且经过 validation 的：

- **Schema Validation**：每个 snapshot 在处理前都会与 `schemas/market_snapshot.schema.json` 进行检查
- **Business Rule Validation**：强制执行 network 身份、edge 合理性、liquidity 边界和 fee 合理性
- **Fail-Closed Semantics**：无效输入会被提前拒绝并返回结构化错误消息，绝不会被静默忽略
- **No Network Assumptions**：系统从不 fetch 数据，从不假设 RPC 可用，从不要求 API key

这种设计意味着你可以用 fixture 文件、版本控制的 snapshot 或合成生成的市场条件来测试整个分析 pipeline，无需外部依赖。

### 处理边界

在边界内部，系统专注于确定性 graph 分析：

- **Cycle Detection**：基于 Bellman-Ford 的有界循环枚举，具有可配置的深度限制
- **Rate Composition**：乘法 rate 计算，在每个 hop 显式扣除 fee
- **Liquidity Constraints**：基于每条路径中的限制性 liquidity 进行容量估算
- **Policy Filtering**：可配置的最低利润阈值、最大路径长度和网络特定规则

Engine 被设计为对相同输入产生相同输出，无论执行环境、时间戳或系统状态如何。这种确定性对于可重现研究、回归测试和多环境部署至关重要。

### 输出边界

系统以两种格式输出结构化、稳定的输出：

- **Human-Readable Text**：格式化表格，包含 network、path、venues、profit basis points 和 capacity
- **Machine-Readable JSON**：符合 `schemas/opportunity_report.schema.json` 的结构化 opportunity 对象

输出稳定性通过以下方式强制执行：

- **Schema Contracts**：JSON 输出形状已文档化并在 CI 中 validation
- **Deterministic Ordering**：Opportunity 按利润降序排序，然后按路径长度排序
- **Stable Field Names**：输出结构的 breaking 变更需要 major version bump
- **Diagnostics Separation**：错误、警告和 metadata 输出到 stderr 或单独的 diagnostic 通道

这使得系统可以安全地嵌入到自动化 pipeline、dashboard 和下游决策系统中。

### 扩展边界

系统设计为无需修改即可扩展：

- **Provider Protocol**：实现 `SnapshotProvider` 以规范化专有数据源
- **Reporter Protocol**：实现 `OpportunityReporter` 以输出自定义格式（CSV、Parquet、数据库写入）
- **Policy Protocol**：实现 `OpportunityPolicy` 以添加特定领域的过滤逻辑
- **Service Protocol**：实现 `AnalysisService` 以集成替代分析引擎（Rust、C++、GPU 加速）

扩展被隔离在稳定接口之后，允许团队在不 fork 核心 engine 的情况下自定义行为。

## 深入：信任模型

### 不可信输入

所有外部数据都被视为不可信：

- **File Providers**：可能读取损坏的 JSON、无效的 UTF-8 或包含嵌入式攻击 payload 的文件
- **Custom Providers**：可能返回不一致的数据、违反 schema contract 或注入恶意 edge 定义
- **Environment Variables**：可能包含意外值、注入尝试或错误配置的路径

Validation 层是信任边界。没有任何东西可以在不通过 schema validation、business rule 检查和合理性边界的情况下进入 engine。

### 不可信加速器

可选的 Rust 分析被视为不可信加速器：

- **Process Isolation**：Rust 二进制文件在单独的进程中运行，没有共享内存
- **Timeout Protection**：长时间运行的 Rust 进程在可配置的超时后被 kill
- **Fallback Semantics**：如果 Rust 失败、发散或不可用，Python 分析保持权威性
- **Parity Validation**：测试套件验证 Rust 和 Python 在参考 snapshot 上产生相同结果

这种设计允许团队受益于 Rust 性能，而不会创建硬依赖或单点故障。

### 可信核心

`src/arbcore/` 下的 Python 实现是可信核心：

- **Canonical Semantics**：Python 定义 validation、分析和输出的权威行为
- **Minimal Dependencies**：核心分析仅需要 Python 标准库
- **Auditable Size**：核心 engine 不到 2000 行 Python，专为人工审查设计
- **Deterministic Behavior**：无随机性，输出中无时间戳，无环境依赖逻辑

这种信任模型使系统适合安全敏感环境，在这些环境中外部依赖和非确定性行为是不可接受的。

## 深入：多网络架构

### Network 作为一等概念

`network` 字段在每个 snapshot 中都是强制且显式的：

```json
{
  "network": "base",
  "timestamp": "2026-05-07T00:00:00Z",
  "edges": [...]
}
```

这种设计有几个好处：

- **No Implicit Assumptions**：Engine 从不猜测 snapshot 代表哪个网络
- **Multi-Network Pipelines**：单个 analysis service 可以处理来自 Ethereum、Base、Arbitrum、Polygon 等的 snapshot
- **Network-Specific Policies**：不同网络可以有不同的利润阈值、gas 假设或 liquidity 过滤器
- **Audit Trail**：每个 opportunity report 都包含源网络，使分析可追溯

### 网络无关 Engine

核心 engine 故意与网络无关：

- **No Hardcoded Chains**：没有针对 Ethereum vs. Base vs. Arbitrum 的特殊情况
- **No RPC Assumptions**：不了解 block time、gas price 或共识机制
- **No Token Registries**：没有硬编码的 token 地址或 symbol 映射
- **No Venue Catalogs**：不假设哪些 DEX 存在于哪些网络上

这使得 engine 可在以下场景中重用：

- **Public Mainnets**：Ethereum、Base、Arbitrum、Optimism、Polygon、Avalanche、BNB Chain
- **Public Testnets**：Sepolia、Goerli、Base Sepolia、Arbitrum Sepolia
- **Private Networks**：内部 testnet、forked 环境、simulation 网络
- **Future Networks**：任何 EVM 兼容链，无需代码更改

### 网络特定扩展

团队可以通过扩展点添加网络特定逻辑：

- **Custom Providers**：规范化网络特定数据源（Ethereum 上的 Uniswap V3，Base 上的 Aerodrome）
- **Custom Policies**：应用网络特定过滤器（昂贵网络上的更高利润阈值）
- **Custom Reporters**：输出网络特定 metadata（gas 估算、block 确认）

这种分离保持核心清洁，同时允许实际定制。

## 深入：Validation 作为基础设施

### 为什么 Validation 重要

在生产系统中，静默失败比响亮失败更危险。这个 repository 将 validation 视为一等功能：

- **Early Detection**：无效输入在分析开始前被拒绝，而不是在部分处理后
- **Structured Errors**：Validation 失败产生 machine-readable 错误对象，包含字段路径和违规描述
- **Fail-Closed**：系统拒绝处理模糊或不安全的输入，从不回退到"最佳猜测"行为
- **Audit Trail**：Validation 结果被记录，可以持久化以供合规审查

### Schema 级 Validation

`schemas/` 下的 JSON schema 记录公共 contract：

- **market_snapshot.schema.json**：定义输入 snapshot 的形状
- **opportunity_report.schema.json**：定义输出 opportunity 的形状
- **diagnostics.schema.json**：定义系统 diagnostics 的形状
- **error_response.schema.json**：定义结构化错误的形状

这些 schema 有多个目的：

- **Documentation**：开发者可以阅读 schema 以了解预期的输入/输出
- **Validation**：Runtime 检查强制执行 schema 合规性
- **Code Generation**：团队可以从 schema 生成客户端库
- **Contract Testing**：CI 验证实际输出是否符合 schema contract

### Runtime Validation

除了 schema validation，系统还强制执行业务规则：

- **Network Identity**：`network` 字段必须存在且非空
- **Edge Sanity**：Rate 必须为正，fee 必须非负，liquidity 必须为正
- **Symbol Consistency**：Edge 必须形成有效路径（edge N 的 target 必须匹配 edge N+1 的 source）
- **Bounded Complexity**：Snapshot 不能超过最大 edge 数量（防止通过巨大 graph 进行 DoS）

这些检查防止：

- **Data Quality Issues**：损坏的 snapshot、陈旧数据、不一致的规范化
- **Attack Vectors**：旨在导致崩溃、无限循环或资源耗尽的恶意 snapshot
- **Integration Bugs**：由于代码更改而违反 contract 的上游系统

### 负面案例 Validation

Repository 包含显式负面测试案例：

- **Missing Required Fields**：没有 `network` 或 `edges` 的 snapshot 必须被拒绝
- **Invalid Data Types**：字符串 rate、负 liquidity、非数组 edge 必须被拒绝
- **Business Rule Violations**：零 rate edge、self-loop、disconnected graph 必须被拒绝

这些测试证明系统在收到错误输入时会安全且可预测地失败。

## 结论：基础设施，而非产品

这个 repository 是基础设施，不是产品。它是 kernel，不是完整系统。它是基础，不是完工建筑。

成功采用它的团队理解这种区别。他们将其用作他们控制的更大系统内部的干净、可审计、确定性分析层。他们添加自己的数据收集、自己的风险管理、自己的执行逻辑和自己的运维实践。

与之斗争的团队将其视为应该开箱即用的神奇 bot。他们期望它收集数据、管理钱包、执行交易并在没有额外工程的情况下产生利润。

Repository 是为第一组设计的。如果你在第二组，这不是适合你的工具。

如果你在第一组，欢迎。阅读 contract，validation 你的 snapshot，审查 failure mode，并在这个基础上构建伟大的东西。
