# P(Doom) Branching Strategy

## Overview
This document outlines the Git branching strategy for P(Doom) to enable graceful hotfix management and organized development.

## Branch Structure

### Main Branches

#### `main`
- **Purpose**: Production-ready code
- **Protection**: Should always be stable and deployable
- **Updates**: Only receives merges from `release/staging` and `hotfix/*` branches
- **Versioning**: Each merge should correspond to a version tag (e.g., v0.2.12)

#### `develop`
- **Purpose**: Integration branch for ongoing development
- **Usage**: Day-to-day development work
- **Features**: New features branch from here and merge back here
- **Updates**: Receives merges from `feature/*` branches
- **Testing**: Run full test suite before merging to `release/staging`

#### `release/staging`
- **Purpose**: Pre-release testing and final polish
- **Usage**: Created from `develop` when ready for release
- **Activities**: Bug fixes, documentation updates, version bumps
- **Merging**: Merges to both `main` and `develop` when ready

#### `stable-alpha` (NEW)
- **Purpose**: Alpha testing candidates from develop
- **Usage**: Created from `develop` for early testing
- **Audience**: Internal testing, developers
- **Updates**: Receives selected merges from `develop`

#### `stable-beta` (NEW)
- **Purpose**: Beta testing candidates, more stable than alpha
- **Usage**: Promoted from `stable-alpha` when ready
- **Audience**: Beta testers, broader audience
- **Updates**: Receives merges from `stable-alpha`

### Supporting Branches

#### `hotfix/*` (e.g., `hotfix/ui-button-shrink`)
- **Purpose**: Critical fixes for production issues
- **Source**: Branches from `main`
- **Naming**: `hotfix/brief-description` or `hotfix/issue-number`
- **Merging**: Merges to both `main` and `develop`
- **Lifecycle**: Delete after successful merge

#### `feature/*` (e.g., `feature/new-ai-opponent`)
- **Purpose**: New features and enhancements
- **Source**: Branches from `develop`
- **Naming**: `feature/brief-description` or `feature/issue-number`
- **Merging**: Merges to `develop` only
- **Lifecycle**: Delete after successful merge

#### `experimental/playground`
- **Purpose**: Risky experiments and proof-of-concepts
- **Usage**: Testing major architectural changes
- **Safety**: Never merges directly to main branches
- **Flow**: Cherry-pick successful experiments to feature branches

#### `experimental/*` (NEW)
- **Purpose**: Experimental features and side quests
- **Examples**: `experimental/longtermist-dates` - 5-digit year format
- **Usage**: Isolated feature experiments
- **Safety**: No impact on main development workflow
- **Flow**: Merge to `develop` when ready, or abandon safely

## Workflow Examples

### Regular Development
```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/improve-ai-strategy

# Work on feature...
# When complete:
git checkout develop
git merge feature/improve-ai-strategy
git branch -d feature/improve-ai-strategy
```

### Hotfix Workflow
```bash
# Critical bug found in production
git checkout main
git pull origin main
git checkout -b hotfix/fix-crash-on-startup

# Fix the bug...
# Test thoroughly...

# Deploy hotfix
git checkout main
git merge hotfix/fix-crash-on-startup
git tag v0.2.13

# Update develop with the fix
git checkout develop
git merge hotfix/fix-crash-on-startup
git branch -d hotfix/fix-crash-on-startup
```

### Release Workflow
```bash
# Prepare for release
git checkout develop
git checkout -b release/v0.3.0

# Final testing, version bump, documentation...
# When ready:
git checkout main
git merge release/v0.3.0
git tag v0.3.0

git checkout develop
git merge release/v0.3.0
git branch -d release/v0.3.0
```

## Branch Protection Rules (GitHub)

### For `main`:
- Require pull request reviews
- Require status checks (CI tests)
- Require up-to-date branches
- Restrict pushes to specific roles

### For `develop`:
- Require status checks (CI tests)
- Allow force pushes (for rebasing)

## Quick Commands Reference

### Create and Switch Branches
```bash
# New feature
git checkout -b feature/feature-name develop

# New hotfix
git checkout -b hotfix/fix-description main

# New experimental work
git checkout -b experimental/experiment-name experimental/playground
```

### Cleanup Commands
```bash
# List merged branches
git branch --merged develop

# Delete merged feature branches
git branch --merged develop | grep 'feature/' | xargs -n 1 git branch -d

# Clean up remote tracking branches
git remote prune origin
```

### Current Branch Status
```bash
# Show all branches with last commit
git branch -v

# Show branch tracking info
git branch -vv

# Show branch relationships
git log --oneline --graph --all
```

## Best Practices

### Naming Conventions
- **Features**: `feature/brief-kebab-case-description`
- **Hotfixes**: `hotfix/brief-kebab-case-description`
- **Releases**: `release/v0.0.0` or `release/staging`
- **Experiments**: `experimental/brief-description`

### Commit Messages
- Use conventional commit format: `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore
- Examples:
  - `feat(ui): add new settings panel`
  - `fix(game): resolve turn sequence bug`
  - `hotfix(crash): fix startup initialization error`

### Testing Requirements
- All feature branches: Run unit tests (`python -m unittest discover tests -v`)
- Before merging to `develop`: Full test suite + type checking
- Before merging to `main`: Full test suite + manual validation
- Hotfixes: Targeted tests + smoke testing

### Version Management
- `main` branch version should always be a released version
- `develop` branch version can include `-dev` suffix
- Release branches bump version and remove `-dev` suffix
- Hotfixes increment patch version

## Emergency Procedures

### Critical Production Bug
1. Create hotfix branch from `main`
2. Fix bug with minimal changes
3. Test fix thoroughly
4. Merge to `main` and tag immediately
5. Merge to `develop` to prevent regression
6. Deploy hotfix quickly

### Rollback Strategy
1. Identify last known good commit on `main`
2. Create hotfix branch from that commit
3. Revert problematic changes
4. Follow standard hotfix workflow

This branching strategy provides structure while remaining flexible for solo development and collaboration.
