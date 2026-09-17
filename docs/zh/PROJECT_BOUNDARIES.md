# 项目边界

- 输入和输出均为本地数据；snapshot 属于不受信输入。
- `src/arbcore/` 中的 Python 是 validation、orchestration 和 API 的 canonical 实现。
- Rust 只是可选的 process-boundary analyzer。
- network 只是 declarative metadata，不验证真实 chain identity。
- 项目不包含 RPC、wallet、key、signing、execution、deployment 或 production funds。
- Solidity 与 Vyper 文件只是 template，不会被 compile、audit、deploy 或 execute。
- local validation readiness 不等于 public 或 production readiness。
