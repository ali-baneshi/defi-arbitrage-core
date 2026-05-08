# History Cleanup Record

The repository was rebuilt from a cleaned working tree and reinitialized with a fresh Git history.

## What Was Done

- The old `.git` directory was moved out of this repository path.
- A new Git repository was initialized on branch `main`.
- The cleaned MVP files were committed as a new root commit.
- Active-tree secret scans were run before and after reinitialization.

## Important Remaining Security Action

Any credentials that appeared in the previous local history must be considered compromised and rotated. Do not publish or copy the old `.git` backup into any public location.

## Recommended Verification

```bash
git log --oneline --all
./scripts/secret_scan.sh
PYTHONPATH=src python scripts/validate_examples.py
```

Use an independent tool such as `gitleaks` before publishing.
