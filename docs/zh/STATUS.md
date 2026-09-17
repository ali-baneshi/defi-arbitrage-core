# 项目状态

- 成熟度：alpha offline MVP
- 支持本地 snapshot 分析与确定性 validation。
- Rust analyzer 是可选组件，Python 仍是 canonical 实现。
- 不支持 live RPC、wallet、signing、broadcast、execution 或 deployment。
- `local_validation_ready` 不代表 public 或 production readiness。
- `production_ready` 必须始终为 `false`。

使用以下命令查看 release 状态：

```bash
PYTHONPATH=src python scripts/release_readiness.py --json
```

release-critical 决策应以 `docs/en/` 英文文档为 canonical source。
