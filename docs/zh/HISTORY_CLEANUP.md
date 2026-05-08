# 历史清理记录

该 repository 基于清理后的 working tree 重建，并使用全新的 Git 历史重新初始化。

## 已完成的操作

- 旧的 `.git` 目录已从当前 repository 路径移出。
- 在 `main` 分支上初始化了新的 Git repository。
- 清理后的 MVP 文件作为新的 root commit 提交。
- 在重建前后都对 active tree 运行了 secret scan。

## 仍需完成的安全动作

凡是出现在旧历史中的 credential，都必须视为已泄露并立即轮换。不要把旧 `.git` 备份发布到任何公共位置，也不要再次复制进公共仓库。

## 建议验证

```bash
git log --oneline --all
./scripts/secret_scan.sh
PYTHONPATH=src python scripts/validate_examples.py
```

公开发布前，再额外运行独立工具，例如 `gitleaks`。
