#!/usr/bin/env bash
# One-command repository creation script
# Usage: bash CREATE_NEW_REPO.sh

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  DeFi Arbitrage Core - New Repository Creation                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed"
    exit 1
fi

if ! command -v rsync &> /dev/null; then
    echo "❌ Error: rsync is not installed"
    exit 1
fi

echo "✓ Git found: $(git --version)"
echo "✓ Rsync found: $(rsync --version | head -1)"

if command -v gh &> /dev/null; then
    echo "✓ GitHub CLI found: $(gh --version | head -1)"
    GH_AVAILABLE=true
else
    echo "⚠ GitHub CLI not found (repository will need manual creation)"
    GH_AVAILABLE=false
fi

echo ""
echo "────────────────────────────────────────────────────────────────"
echo ""

# Run the main script
if [ -f "scripts/create_new_repo.sh" ]; then
    echo "Running repository creation script..."
    echo ""
    bash scripts/create_new_repo.sh
else
    echo "❌ Error: scripts/create_new_repo.sh not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Repository Creation Summary                                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

NEW_REPO_PATH="${HOME}/Documents/Google-antigravity/defi-arbitrage-core-mvp-v1"

if [ -d "${NEW_REPO_PATH}" ]; then
    echo "✓ Repository created at: ${NEW_REPO_PATH}"
    
    cd "${NEW_REPO_PATH}"
    
    echo "✓ Git initialized with $(git log --oneline | wc -l) commit(s)"
    echo "✓ Tag created: $(git tag -l)"
    
    if git remote get-url origin &> /dev/null; then
        echo "✓ Remote configured: $(git remote get-url origin)"
    else
        echo "⚠ Remote not configured (manual setup required)"
    fi
    
    echo ""
    echo "────────────────────────────────────────────────────────────────"
    echo ""
    echo "Next Steps:"
    echo ""
    
    if [ "$GH_AVAILABLE" = false ]; then
        echo "1. Create repository on GitHub:"
        echo "   https://github.com/new"
        echo ""
        echo "2. Configure remote and push:"
        echo "   cd ${NEW_REPO_PATH}"
        echo "   git remote add origin https://github.com/ali-baneshi/defi-arbitrage-core-mvp-v1.git"
        echo "   git branch -M main"
        echo "   git push -u origin main"
        echo "   git push origin v1.0.0"
        echo ""
    else
        echo "1. Push the release tag:"
        echo "   cd ${NEW_REPO_PATH}"
        echo "   git push origin v1.0.0"
        echo ""
        echo "2. Create GitHub release:"
        echo "   gh release create v1.0.0 --title 'MVP Release v1.0.0' --notes-file <(git tag -l --format='%(contents)' v1.0.0)"
        echo ""
    fi
    
    echo "3. Verify the repository:"
    echo "   cd ${NEW_REPO_PATH}"
    echo "   PYTHONPATH=src python scripts/validate_all.py"
    echo ""
    
    echo "4. Review documentation:"
    echo "   cat ${NEW_REPO_PATH}/README.md"
    echo "   cat ${NEW_REPO_PATH}/REPOSITORY_SETUP_GUIDE.md"
    echo ""
    
    echo "5. When ready, make repository public:"
    echo "   gh repo edit --visibility public"
    echo ""
    
    echo "────────────────────────────────────────────────────────────────"
    echo ""
    echo "For detailed instructions, see:"
    echo "  ${NEW_REPO_PATH}/REPOSITORY_SETUP_GUIDE.md"
    echo ""
else
    echo "❌ Error: Repository creation failed"
    exit 1
fi

echo "✓ Done!"
echo ""
