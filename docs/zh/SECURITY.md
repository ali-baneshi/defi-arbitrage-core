# 安全

英文文档是 canonical source，本页提供快速摘要。

## scope

这个 repository 是离线分析核心，故意不包含：

- private key handling
- signing
- live RPC
- deployment
- trade execution

## 漏洞报告

请私下向 maintainer 报告漏洞，并附上 reproduction step、impact 以及受影响文件范围。

## hygiene

- 不要提交 secret、token、wallet data 或 credential
- 公开发布前请执行独立的 history scan
- 使用 `PYTHONPATH=src python scripts/release_readiness.py --json` 作为最终 gate
