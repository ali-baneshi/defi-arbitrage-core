#!/usr/bin/env sh
set -eu

# Scan repository-controlled text files for common high-risk secret markers.
# Local environments, build outputs, caches, dependency trees, and VCS internals
# are intentionally excluded to avoid false positives from third-party packages.
#
# Generic labels such as api_key/private_key/client_secret are only flagged when
# they look like assignments to non-trivial values. This avoids flagging scanner
# code, documentation prose, and validation error names.

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

HIGH_CONFIDENCE_PATTERN='(AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{36,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----)'

ASSIGNMENT_PATTERN='(private[_-]?key|client[_-]?secret|api[_-]?key|access[_-]?token|secret[_-]?key)[[:space:]]*[:=][[:space:]]*["'\'']?[A-Za-z0-9_./+=:-]{16,}'

EXCLUDE_PATTERN='(^|/)(\.git|\.venv|venv|env|\.mypy_cache|\.ruff_cache|\.pytest_cache|__pycache__|target|dist|build|node_modules|site-packages)(/|$)|^scripts/secret_scan\.sh$'

scan_files() {
    xargs -0 -r grep -nEI "$HIGH_CONFIDENCE_PATTERN|$ASSIGNMENT_PATTERN" -- 2>/dev/null
}

if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    # Tracked files + untracked non-ignored files. This respects .gitignore and
    # avoids scanning .venv, target, caches, and other local-only artifacts.
    if git ls-files -co --exclude-standard -z |
        grep -zEv "$EXCLUDE_PATTERN" |
        scan_files
    then
        echo "Potential secret found" >&2
        exit 1
    fi
else
    if find . \
        \( -path './.git' -o -path './.venv' -o -path './venv' -o -path './env' \
           -o -path './.mypy_cache' -o -path './.ruff_cache' -o -path './.pytest_cache' \
           -o -path './target' -o -path './dist' -o -path './build' \
           -o -path './node_modules' -o -path '*/__pycache__/*' -o -path '*/site-packages/*' \) -prune \
        -o -type f ! -path './scripts/secret_scan.sh' -print0 |
        scan_files
    then
        echo "Potential secret found" >&2
        exit 1
    fi
fi

echo "No potential secrets found"
