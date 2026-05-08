#!/usr/bin/env bash
# Create a new private repository copy for initial MVP release

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Configuration
NEW_REPO_NAME="defi-arbitrage-core-mvp-v1"
NEW_REPO_PATH="${HOME}/Documents/Google-antigravity/${NEW_REPO_NAME}"
GITHUB_USERNAME="ali-baneshi"

echo "=========================================="
echo "Creating New Repository Copy"
echo "=========================================="
echo ""
echo "Source: ${PROJECT_ROOT}"
echo "Target: ${NEW_REPO_PATH}"
echo "GitHub: ${GITHUB_USERNAME}/${NEW_REPO_NAME}"
echo ""

# Check if target directory already exists
if [ -d "${NEW_REPO_PATH}" ]; then
    echo "Error: Target directory already exists: ${NEW_REPO_PATH}"
    echo "Please remove it first or choose a different name."
    exit 1
fi

# Step 1: Create target directory
echo "Step 1: Creating target directory..."
mkdir -p "${NEW_REPO_PATH}"

# Step 2: Copy all files except .git
echo "Step 2: Copying project files..."
cd "${PROJECT_ROOT}"

# Use rsync for efficient copying with exclusions
rsync -av \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='.ruff_cache' \
    --exclude='target' \
    --exclude='Cargo.lock' \
    --exclude='.DS_Store' \
    --exclude='*.swp' \
    --exclude='*.swo' \
    --exclude='.env' \
    --exclude='node_modules' \
    ./ "${NEW_REPO_PATH}/"

echo "Files copied successfully."

# Step 3: Initialize new git repository
echo "Step 3: Initializing new git repository..."
cd "${NEW_REPO_PATH}"
git init
git config user.name "Ali Baneshi"
git config user.email "ali.baneshi@example.com"

# Step 4: Create initial commit
echo "Step 4: Creating initial commit..."
git add .
git commit -m "Initial MVP release v1.0.0

This is the first public-ready version of defi-arbitrage-core.

Features:
- Offline market snapshot analysis
- Multi-network support (Ethereum, Base, Arbitrum, Polygon, etc.)
- Deterministic cycle detection and opportunity analysis
- JSON schema validation and structured output
- Optional Rust acceleration with Python fallback
- Contract template validation (Solidity, Vyper)
- Comprehensive documentation in English, Persian, and Chinese
- Docker support for reproducible environments

This repository contains no credentials, no private keys, and no
proprietary data. It is designed as infrastructure for research,
education, and as a foundation for larger systems."

# Step 5: Create GitHub repository (requires gh CLI)
echo "Step 5: Creating GitHub repository..."
if command -v gh &> /dev/null; then
    echo "Creating private repository on GitHub..."
    gh repo create "${GITHUB_USERNAME}/${NEW_REPO_NAME}" \
        --private \
        --source="${NEW_REPO_PATH}" \
        --description="DeFi arbitrage analysis infrastructure - MVP v1.0.0" \
        --push
    
    echo "Repository created and pushed successfully!"
else
    echo "GitHub CLI (gh) not found. Creating remote manually..."
    echo ""
    echo "Please run these commands manually:"
    echo ""
    echo "  # Create repository on GitHub web interface, then:"
    echo "  cd ${NEW_REPO_PATH}"
    echo "  git remote add origin https://github.com/${GITHUB_USERNAME}/${NEW_REPO_NAME}.git"
    echo "  git branch -M main"
    echo "  git push -u origin main"
    echo ""
fi

# Step 6: Add repository topics and settings
echo "Step 6: Configuring repository settings..."
if command -v gh &> /dev/null; then
    cd "${NEW_REPO_PATH}"
    
    # Add topics
    gh repo edit \
        --add-topic defi \
        --add-topic arbitrage \
        --add-topic market-analysis \
        --add-topic quant-research \
        --add-topic graph-algorithms \
        --add-topic json-schema \
        --add-topic rust \
        --add-topic python \
        --add-topic developer-tools \
        --add-topic infrastructure
    
    echo "Repository topics added."
fi

# Step 7: Create release tag
echo "Step 7: Creating release tag..."
cd "${NEW_REPO_PATH}"
git tag -a v1.0.0 -m "MVP Release v1.0.0

First public-ready release of defi-arbitrage-core infrastructure.

This is an alpha-quality offline analysis kernel suitable for:
- Research and education
- Simulation and backtesting foundations
- Internal tooling and data pipelines
- Protocol analysis and market structure research

Not suitable for:
- Live trading or execution
- Production use without additional infrastructure
- Wallet management or key custody

See README.md and docs/ for detailed documentation."

echo ""
echo "=========================================="
echo "Repository Creation Complete!"
echo "=========================================="
echo ""
echo "New repository location: ${NEW_REPO_PATH}"
echo ""
echo "Next steps:"
echo "1. Review the repository contents"
echo "2. Push the tag: cd ${NEW_REPO_PATH} && git push origin v1.0.0"
echo "3. Make the repository public when ready: gh repo edit --visibility public"
echo ""
