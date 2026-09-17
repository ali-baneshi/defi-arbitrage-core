# Release Evidence

canonical evidence 文件为 `release/release-evidence.json`，并必须符合
`schemas/release_evidence.schema.json`。仓库只发布 example 文件；该文件会
故意保持 blocked 状态。

所需证据包括：

- 轮换所有历史 credential；
- 确认旧 `.git` 备份不在任何发布路径；
- 对全部 history（包括 unreachable objects）执行独立扫描；
- 完整刷新 Persian 与 Chinese 文档镜像。

证据文件不得包含 secret、token、private key 或本地私有路径。英文文档是 release 的 canonical source。

GitHub 仓库目前已经是 public；但 `public_release_ready` 只表示 signed alpha
release 已经通过 gate，不表示仓库 visibility。证据必须绑定到明确的 release
commit，并保存独立扫描报告的 checksum。
