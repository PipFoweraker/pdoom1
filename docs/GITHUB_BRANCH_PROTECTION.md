# GitHub Branch Protection Setup Guide

## Overview
This guide provides step-by-step instructions for setting up branch protection rules that enforce the P(Doom) branching strategy.

## Branch Protection Rules

### 1. Protect `main` Branch (Critical)

**Purpose**: Ensure production branch stability and enforce code review process.

**Settings to Enable:**
- ✅ **Require a pull request before merging**
  - Require approvals: 1 (can be yourself for solo development)
  - Dismiss stale reviews when new commits are pushed
  - Require review from code owners (optional)

- ✅ **Require status checks to pass before merging**
  - Require branches to be up to date before merging
  - Required status checks:
    - `build` (if you have GitHub Actions)
    - `test` (if you have automated testing)

- ✅ **Require conversation resolution before merging**

- ✅ **Restrict pushes that create files larger than 100MB**

- ✅ **Allow force pushes**: ❌ (Disabled)
- ✅ **Allow deletions**: ❌ (Disabled)

**GitHub Settings Path:**
```
Settings > Branches > Add rule
Branch name pattern: main
```

### 2. Protect `develop` Branch (Moderate)

**Purpose**: Maintain development branch stability while allowing flexibility.

**Settings to Enable:**
- ✅ **Require status checks to pass before merging**
  - Required status checks:
    - `test` (ensure tests pass)
  - Do NOT require "up to date" (allows faster merging)

- ✅ **Allow force pushes**: ✅ (Enabled for rebasing)
- ✅ **Allow deletions**: ❌ (Disabled)

**GitHub Settings Path:**
```
Settings > Branches > Add rule
Branch name pattern: develop
```

### 3. Protect Release Branches (Moderate)

**Purpose**: Ensure release candidates are properly tested.

**Settings to Enable:**
- ✅ **Require a pull request before merging**
  - Require approvals: 1

- ✅ **Require status checks to pass before merging**
  - Require branches to be up to date before merging

**GitHub Settings Path:**
```
Settings > Branches > Add rule
Branch name pattern: release/*
```

### 4. Auto-Delete Feature Branches

**Purpose**: Keep repository clean by automatically deleting merged branches.

**Settings to Enable:**
- ✅ **Automatically delete head branches** (in repository settings)

**GitHub Settings Path:**
```
Settings > General > Pull Requests
☑ Automatically delete head branches
```

## GitHub Actions Integration

### Recommended Workflow File
Create `.github/workflows/branch-protection.yml`:

```yaml
name: Branch Protection
on:
  pull_request:
    branches: [ main, develop, release/* ]
  push:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m unittest discover tests -v
    - name: Type checking
      run: |
        python -m pip install mypy
        python -m mypy src/ --ignore-missing-imports
      continue-on-error: true  # Don't fail on type errors yet

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install flake8
    - name: Lint with flake8
      run: |
        flake8 src/ tests/ --max-line-length=120 --ignore=E501,W503
      continue-on-error: true  # Don't fail on lint errors yet
```

## Team Collaboration Rules

### Naming Conventions (Enforced by Branch Protection)

**Feature Branches:**
- Pattern: `feature/*`
- Example: `feature/improve-ai-strategy`
- Source: `develop`
- Target: `develop`

**Hotfix Branches:**
- Pattern: `hotfix/*`
- Example: `hotfix/fix-crash-on-startup`
- Source: `main`
- Target: `main` AND `develop`

**Release Branches:**
- Pattern: `release/*`
- Example: `release/v0.3.0`
- Source: `develop`
- Target: `main`

**Experimental Branches:**
- Pattern: `experimental/*`
- Example: `experimental/new-ui-framework`
- Source: `experimental/playground`
- Target: `experimental/playground` (or cherry-pick to feature branches)

## Setup Instructions

### Step 1: Access GitHub Settings
1. Go to your repository on GitHub
2. Click "Settings" tab
3. Click "Branches" in left sidebar

### Step 2: Create Branch Protection Rules
1. Click "Add rule"
2. Enter branch name pattern (e.g., `main`)
3. Configure protection settings as outlined above
4. Click "Create"

### Step 3: Verify Protection Rules
Test the rules by:
1. Creating a test branch
2. Making a change
3. Opening a pull request
4. Verify protection rules are enforced

### Step 4: Configure Auto-Delete
1. Go to Settings > General
2. Scroll to "Pull Requests" section
3. Check "Automatically delete head branches"

## Enforcement Commands

### Check Protection Status
```bash
# List protected branches
gh api repos/:owner/:repo/branches --jq '.[] | select(.protected == true) | .name'

# Check specific branch protection
gh api repos/:owner/:repo/branches/main/protection
```

### Override Protection (Emergency Only)
```bash
# Temporarily disable protection for emergency hotfix
gh api -X DELETE repos/:owner/:repo/branches/main/protection

# Re-enable protection after emergency
gh api -X PUT repos/:owner/:repo/branches/main/protection \
  --input protection-config.json
```

## Monitoring and Maintenance

### Weekly Checklist
- [ ] Review unmerged branches older than 2 weeks
- [ ] Clean up stale feature branches
- [ ] Verify protection rules are working
- [ ] Check for any protection bypasses in audit log

### Monthly Checklist
- [ ] Review and update required status checks
- [ ] Audit branch protection settings
- [ ] Clean up old release branches
- [ ] Update documentation if rules change

## Benefits of This Setup

1. **Quality Assurance**: Automated testing prevents broken code from reaching main
2. **Code Review**: All changes to main go through review process
3. **Clean History**: Protection rules maintain linear history
4. **Emergency Response**: Hotfix workflow allows rapid fixes when needed
5. **Collaboration**: Clear rules for team development

## Troubleshooting

### Common Issues

**Q: Can't push to main branch**
A: This is correct! Use feature branches and pull requests.

**Q: Status checks failing**
A: Check GitHub Actions logs for test failures or setup issues.

**Q: Need to bypass protection for emergency**
A: Use admin override, but document the reason and restore protection immediately.

**Q: Too many required reviews**
A: Adjust approval count in protection settings (can be 0 for solo development).

This setup provides robust protection while maintaining development velocity!
