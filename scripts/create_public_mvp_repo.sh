#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST_DIR="${1:-${SRC_DIR%/*}/defi-arbitrage-core-public-mvp}"
REPO_NAME="${2:-$(basename "$DEST_DIR")}"
VISIBILITY="${REPO_VISIBILITY:-private}"
CREATE_REMOTE="${CREATE_REMOTE:-0}"
INIT_COMMIT_MESSAGE="${INIT_COMMIT_MESSAGE:-Initial public MVP snapshot}"

if [[ -e "$DEST_DIR" ]]; then
  echo "Destination already exists: $DEST_DIR" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

rsync -a \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  --exclude '.ruff_cache' \
  --exclude 'target' \
  --exclude 'dist' \
  --exclude 'build' \
  --exclude '*.pyc' \
  --exclude '*.pyo' \
  --exclude '*.log' \
  "$SRC_DIR/" "$DEST_DIR/"

cd "$DEST_DIR"

git init -b main >/dev/null

git add .
git commit -m "$INIT_COMMIT_MESSAGE" >/dev/null

PYTHONPATH=src python scripts/validate_repository.py
PYTHONPATH=src python scripts/validate_documented_commands.py
PYTHONPATH=src python scripts/validate_all.py --include-rust

if [[ "$CREATE_REMOTE" == "1" ]]; then
  if ! command -v gh >/dev/null 2>&1; then
    echo "CREATE_REMOTE=1 was requested but GitHub CLI (gh) is not installed." >&2
    exit 1
  fi
  gh repo create "$REPO_NAME" --"$VISIBILITY" --source . --remote origin --push
fi

echo "Created clean MVP repository at: $DEST_DIR"
if [[ "$CREATE_REMOTE" == "1" ]]; then
  echo "GitHub remote created as a $VISIBILITY repository: $REPO_NAME"
else
  echo "Local git repository initialized. Set CREATE_REMOTE=1 to create and push a GitHub repository with gh."
fi
