# Public Release 计划

本计划针对已经公开的当前 repository。不会创建替代 repository、新版本或新 tag。

目标是发布可审查、可复现的 alpha offline MVP，而不是 trading bot。

主要工作：

1. 清理并扫描完整 history 与 unreachable objects。
2. 轮换历史 credential，并将旧备份排除在 publication path 之外。
3. 保持当前 `0.1.0a1` version，并统一 URL 与 release evidence。
4. 完整刷新 Persian 与 Chinese 文档镜像。
5. 执行 tests、Rust parity、dependency scan、secret scan、Docker 与 clean-clone verification。

在所有 gate satisfied 之前，`public_release_ready` 必须保持 false；repository
公开并不等于 release 已经准备完成。
