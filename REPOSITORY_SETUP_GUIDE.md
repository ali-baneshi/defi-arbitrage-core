# Repository Setup Guide

The current repository is already the public snapshot being prepared. Keep this
repository, its `main` branch, and package identity `0.1.0a1`. This guide does
not authorize a replacement repository, a history rewrite, a force-push, or a
new release tag.

## Current Workflow

Run these commands from this repository:

```bash
PYTHONPATH=src python scripts/audit_public_remote.py
PYTHONPATH=src python scripts/validate_all.py --include-rust
PYTHONPATH=src python scripts/release_readiness.py --json
```

The first command scans the refs currently advertised by the configured public
remote in a temporary mirror. It cannot prove that server-side unreachable
objects are gone, so an independent full-history scan and maintainer attestations
remain required. The readiness report intentionally stays false until the
external gates are evidenced in `release/release-evidence.json`.

After the hardening change is committed and the working tree is clean, use:

```bash
PYTHONPATH=src python scripts/verify_public_snapshot.py
```

This is a non-mutating guard for the same public snapshot. It checks the package
identity and validation state; it never creates a tag, pushes, or rewrites Git
history.

## Current Version and Git Policy

- Package version: `0.1.0a1` (human-facing alpha label: `0.1.0-alpha`).
- Existing historical tags remain untouched.
- Work lands as an ordinary commit on `main` when the maintainer is ready.
- Do not create or move a tag for this preparation task.

## External Gates Still Owned by the Maintainer

- Rotate any credential that may have appeared in older local history.
- Confirm old repositories, `.git` backups, and archive paths are outside every
  publication path.
- Run an independent full-history scanner and retain its report checksum.
- Review Persian and Chinese docs, or explicitly scope English as canonical in
  release notes.
- Create the real non-secret `release/release-evidence.json` only from verified
  facts; never copy the blocked example as if it were an attestation.

## Legacy Clean-Copy Utility

The commands below are retained only for a separately authorized archival copy.
They are not part of preparing this public repository. Do not run them with the
current repository as the destination:

```bash
ALLOW_LEGACY_REPO_COPY=1 bash scripts/create_new_repo.sh
```

That utility creates a fresh repository and is intentionally outside the current
workflow. Its historical instructions are preserved below for reference only.

## Prerequisites

1. **Git**: Ensure git is installed and configured
2. **rsync**: For efficient file copying (usually pre-installed on Linux/macOS)
3. **GitHub CLI (optional)**: Install `gh` for automated GitHub repository creation
   - Install: `brew install gh` (macOS) or see https://cli.github.com/
   - Login: `gh auth login`

## Legacy Quick Start (Reference Only)

Run the automated script only when a separate clean copy has been explicitly
requested:

```bash
ALLOW_LEGACY_REPO_COPY=1 bash scripts/create_new_repo.sh
```

If used for a separate legacy copy, this will:
1. Create a new directory at a separately configured destination
2. Copy all project files (excluding .git, build artifacts, and temporary files)
3. Initialize a fresh git repository with clean history
4. Create an initial commit with comprehensive release notes
5. Create a private GitHub repository (if `gh` CLI is available)
6. Add repository topics for discoverability
7. Run validation for that separate copy

## Legacy Manual Steps (Reference Only)

If you don't have GitHub CLI installed, follow these steps after running the script:

### 1. Create Repository on GitHub

Go to https://github.com/new and create a separate **private** repository only
if you intentionally need a legacy copy:
- Repository name: choose a distinct name; do not reuse the current public repository
- Description: `DeFi arbitrage analysis infrastructure - legacy copy`
- Visibility: **Private**
- Do NOT initialize with README, .gitignore, or license (we already have these)

### 2. Push to GitHub

```bash
cd ~/Documents/Google-antigravity/defi-arbitrage-core
git remote add origin https://github.com/ali-baneshi/defi-arbitrage-core.git
git branch -M main
git push -u origin main
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
cd ~/Documents/Google-antigravity/defi-arbitrage-core
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

Should show the clean alpha release commit.

### 3. Verify Git Tags

```bash
git tag -l
```

Do not expect a new tag from this workflow; the current public snapshot is
validated through `scripts/verify_public_snapshot.py`.

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
1. Choose a different `NEW_REPO_PATH` or remove the existing target directory after verifying it is disposable.
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

## Legacy Post-Creation Checklist

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
- [ ] Archive the completed current-snapshot evidence
- [ ] Update repository description
- [ ] Keep the current repository public; do not create a new release tag as part of this workflow

## Legacy GitHub Release Reference

The current-snapshot workflow does not create or push a new tag. If a separate
legacy copy is intentionally maintained, manage its release independently:

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Do not apply these steps to the current public repository
4. Do not apply these steps to the current public repository; complete its
   external evidence gates instead
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
