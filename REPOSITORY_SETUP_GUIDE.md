# Repository Setup Guide

This guide explains how to create a new private repository copy of this project for your initial MVP release.

## Prerequisites

1. **Git**: Ensure git is installed and configured
2. **rsync**: For efficient file copying (usually pre-installed on Linux/macOS)
3. **GitHub CLI (optional)**: Install `gh` for automated GitHub repository creation
   - Install: `brew install gh` (macOS) or see https://cli.github.com/
   - Login: `gh auth login`

## Quick Start

Run the automated script from the project root:

```bash
bash scripts/create_new_repo.sh
```

This will:
1. Create a new directory at `~/Documents/Google-antigravity/defi-arbitrage-core-mvp-v1`
2. Copy all project files (excluding .git, build artifacts, and temporary files)
3. Initialize a fresh git repository with clean history
4. Create an initial commit with comprehensive release notes
5. Create a private GitHub repository (if `gh` CLI is available)
6. Add repository topics for discoverability
7. Create a v1.0.0 release tag

## Manual Steps (if gh CLI is not available)

If you don't have GitHub CLI installed, follow these steps after running the script:

### 1. Create Repository on GitHub

Go to https://github.com/new and create a new **private** repository:
- Repository name: `defi-arbitrage-core-mvp-v1`
- Description: `DeFi arbitrage analysis infrastructure - MVP v1.0.0`
- Visibility: **Private**
- Do NOT initialize with README, .gitignore, or license (we already have these)

### 2. Push to GitHub

```bash
cd ~/Documents/Google-antigravity/defi-arbitrage-core-mvp-v1
git remote add origin https://github.com/ali-baneshi/defi-arbitrage-core-mvp-v1.git
git branch -M main
git push -u origin main
git push origin v1.0.0
```

### 3. Configure Repository Settings

On GitHub, go to repository Settings:

**Topics**: Add these topics for better discoverability:
- `defi`
- `arbitrage`
- `market-analysis`
- `quant-research`
- `graph-algorithms`
- `json-schema`
- `rust`
- `python`
- `developer-tools`
- `infrastructure`

**About**: Add description:
```
A boundary-driven DeFi arbitrage analysis core focused on deterministic validation, multi-network market modeling, and reproducible off-chain opportunity evaluation.
```

## Verification Steps

After repository creation, verify everything is correct:

### 1. Check Repository Structure

```bash
cd ~/Documents/Google-antigravity/defi-arbitrage-core-mvp-v1
ls -la
```

You should see:
- All source files and documentation
- No `.git` directory from the original repo (fresh history)
- No build artifacts or temporary files

### 2. Verify Git History

```bash
git log --oneline
```

Should show only one commit: "Initial MVP release v1.0.0"

### 3. Verify Git Tags

```bash
git tag -l
```

Should show: `v1.0.0`

### 4. Run Validation Suite

```bash
PYTHONPATH=src python scripts/validate_all.py
```

All checks should pass (except the BLOCKED items which are expected).

### 5. Check Remote Configuration

```bash
git remote -v
```

Should show your new repository URL.

## Making the Repository Public

**IMPORTANT**: Only make the repository public after:
1. Reviewing all files for sensitive information
2. Confirming no credentials or API keys are present
3. Verifying documentation is complete and accurate
4. Running the full validation suite

To make public:

```bash
cd ~/Documents/Google-antigravity/defi-arbitrage-core-mvp-v1
gh repo edit --visibility public
```

Or manually on GitHub: Settings → Danger Zone → Change repository visibility → Make public

## Customization

To customize the script for your needs, edit `scripts/create_new_repo.sh`:

```bash
# Change repository name
NEW_REPO_NAME="your-custom-name"

# Change target path
NEW_REPO_PATH="/your/custom/path/${NEW_REPO_NAME}"

# Change GitHub username
GITHUB_USERNAME="your-github-username"
```

## Troubleshooting

### Error: Target directory already exists

If you see this error, either:
1. Remove the existing directory: `rm -rf ~/Documents/Google-antigravity/defi-arbitrage-core-mvp-v1`
2. Or change `NEW_REPO_NAME` in the script

### Error: gh command not found

Install GitHub CLI:
- macOS: `brew install gh`
- Linux: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md
- Or follow manual steps above

### Error: rsync command not found

Install rsync:
- macOS: Pre-installed
- Linux: `sudo apt-get install rsync` or `sudo yum install rsync`

### Permission denied when running script

Make the script executable:
```bash
chmod +x scripts/create_new_repo.sh
```

## What Gets Excluded

The script automatically excludes:
- `.git/` - Original git history
- `.venv/` - Python virtual environments
- `__pycache__/` - Python bytecode cache
- `*.pyc` - Compiled Python files
- `.pytest_cache/` - Pytest cache
- `.ruff_cache/` - Ruff linter cache
- `target/` - Rust build artifacts
- `Cargo.lock` - Rust dependency lock (regenerated on build)
- `.DS_Store` - macOS metadata
- `*.swp`, `*.swo` - Vim swap files
- `.env` - Environment variables (should use .env.example)
- `node_modules/` - Node.js dependencies

## Post-Creation Checklist

After creating the new repository:

- [ ] Verify all files are present
- [ ] Check git history is clean (only one commit)
- [ ] Run validation suite
- [ ] Review README.md
- [ ] Review all documentation
- [ ] Test example commands
- [ ] Verify no sensitive data is present
- [ ] Push to GitHub
- [ ] Add repository topics
- [ ] Configure repository settings
- [ ] Create GitHub release from v1.0.0 tag
- [ ] Update repository description
- [ ] Consider making public (when ready)

## Creating a GitHub Release

After pushing the tag, create a release on GitHub:

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Choose tag: `v1.0.0`
4. Release title: `MVP Release v1.0.0`
5. Description: Use the content from the tag message
6. Mark as "pre-release" if still in alpha
7. Publish release

## Next Steps

After repository creation:

1. **Review Documentation**: Ensure all docs are accurate and complete
2. **Test Installation**: Try installing in a fresh environment
3. **Run Examples**: Verify all example commands work
4. **Update Links**: If you changed the repository name, update any hardcoded links
5. **Invite Collaborators**: Add team members if this is a team project
6. **Set Up CI/CD**: Configure GitHub Actions for automated testing
7. **Monitor Issues**: Watch for issues and questions from users

## Support

For questions or issues with this setup process:
1. Check the troubleshooting section above
2. Review the main README.md
3. Check docs/en/INSTALLATION.md
4. Open an issue in the original repository

## License

This repository is released under the MIT License. See LICENSE file for details.
