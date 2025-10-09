# Multi-Repository Development Workflow: P(Doom) Ecosystem

## Repository Status Assessment

Based on the existing GitHub Actions workflows, your P(Doom) ecosystem appears to have:

### [EMOJI] **Confirmed Existing Repositories**
- **`PipFoweraker/pdoom1`** - Main game repository (current workspace)
- **`PipFoweraker/pdoom1-website`** - Website repository (referenced in sync workflows)
- **`PipFoweraker/pdoom1-data`** - Data repository (status unknown - needs verification)

### [SEARCH] **Repository Verification Commands**

Run these commands to verify which repositories exist and their access status:

```bash
# Check website repository
git ls-remote https://github.com/PipFoweraker/pdoom1-website.git

# Check data repository  
git ls-remote https://github.com/PipFoweraker/pdoom1-data.git

# List all your repositories
gh repo list PipFoweraker --limit 50
```

## VS Code Multi-Repository Setup

### Option 1: VS Code Workspace File (Recommended)

Create a workspace file to manage all repositories together:

**File: `pdoom1-ecosystem.code-workspace`**
```json
{
    "folders": [
        {
            "name": "Game (pdoom1)",
            "path": "./pdoom1"
        },
        {
            "name": "Website",
            "path": "./pdoom1-website"
        },
        {
            "name": "Data & API",
            "path": "./pdoom1-data"
        }
    ],
    "settings": {
        "files.exclude": {
            "**/node_modules": true,
            "**/__pycache__": true,
            "**/venv": true,
            "**/.pytest_cache": true
        },
        "search.exclude": {
            "**/node_modules": true,
            "**/__pycache__": true,
            "**/venv": true
        },
        "git.enableSmartCommit": true,
        "git.autofetch": true,
        "python.defaultInterpreterPath": "./pdoom1/venv/bin/python"
    },
    "extensions": {
        "recommendations": [
            "ms-python.python",
            "ms-vscode.vscode-json",
            "redhat.vscode-yaml",
            "ms-vscode.vscode-typescript-next",
            "GitHub.vscode-pull-request-github",
            "eamodio.gitlens"
        ]
    }
}
```

### Option 2: Directory Structure Setup

Organize your local development with this structure:

```
pdoom1-ecosystem/
[EMOJI][EMOJI][EMOJI] pdoom1/                    # Main game (current location)
[EMOJI][EMOJI][EMOJI] pdoom1-website/           # Website repository  
[EMOJI][EMOJI][EMOJI] pdoom1-data/              # Data/API repository
[EMOJI][EMOJI][EMOJI] docs/                     # Shared documentation
[EMOJI][EMOJI][EMOJI] scripts/                  # Cross-repo scripts
[EMOJI][EMOJI][EMOJI] pdoom1-ecosystem.code-workspace
```

### Setup Commands

```bash
# Navigate to parent directory
cd "$(dirname "$(pwd)")"

# Create ecosystem directory structure
mkdir -p pdoom1-ecosystem/{docs,scripts}

# Move current game repo (if needed)
mv "Pdoom1Folder/pdoom1" pdoom1-ecosystem/

# Clone other repositories
cd pdoom1-ecosystem
git clone https://github.com/PipFoweraker/pdoom1-website.git
git clone https://github.com/PipFoweraker/pdoom1-data.git  # If it exists

# Create workspace file
cat > pdoom1-ecosystem.code-workspace << 'EOF'
[workspace file content from above]
EOF
```

## Cross-Repository Documentation System

### Central Documentation Index

Create a central documentation hub that references all repositories:

**File: `docs/ECOSYSTEM_OVERVIEW.md`**
```markdown
# P(Doom) Ecosystem Documentation Hub

## Repository Navigation

| Repository | Purpose | Key Documentation |
|------------|---------|------------------|
| [pdoom1](../pdoom1/) | Game Logic & Core | [Developer Guide](../pdoom1/docs/DEVELOPERGUIDE.md) |
| [pdoom1-website](../pdoom1-website/) | Website & Community | [Website README](../pdoom1-website/README.md) |
| [pdoom1-data](../pdoom1-data/) | API & Database | [API Documentation](../pdoom1-data/docs/API.md) |

## Integration Points

- **Game -> Website**: Dev blog sync, release announcements
- **Game -> Data**: Score submission, leaderboards
- **Data -> Website**: Dynamic content, leaderboards
- **Website -> Data**: User registration, community features

## Quick Links

- [Multi-Repository Integration Plan](../pdoom1/docs/MULTI_REPOSITORY_INTEGRATION_PLAN.md)
- [Website Pipeline Strategy](../pdoom1/docs/WEBSITE_PIPELINE_STRATEGY.md)
- [Cross-Repo Sync Status](./SYNC_STATUS.md)
```

### Documentation Sync Script

**File: `scripts/sync-docs.py`**
```python
# !/usr/bin/env python3
"""
Sync important documentation between repositories
"""
import os
import shutil
from pathlib import Path

def sync_documentation():
    """Sync key documentation files across repositories"""
    base_dir = Path(__file__).parent.parent
    
    # Documentation sync map
    sync_map = {
        # Source -> Destinations
        "pdoom1/docs/MULTI_REPOSITORY_INTEGRATION_PLAN.md": [
            "pdoom1-website/docs/",
            "pdoom1-data/docs/"
        ],
        "pdoom1/docs/WEBSITE_PIPELINE_STRATEGY.md": [
            "pdoom1-website/docs/"
        ],
        "pdoom1/CHANGELOG.md": [
            "pdoom1-website/docs/",
            "docs/"
        ]
    }
    
    for source, destinations in sync_map.items():
        source_path = base_dir / source
        if source_path.exists():
            for dest_dir in destinations:
                dest_path = base_dir / dest_dir
                if dest_path.exists():
                    dest_file = dest_path / source_path.name
                    print(f"Syncing {source} -> {dest_file}")
                    shutil.copy2(source_path, dest_file)
                else:
                    print(f"[WARNING][EMOJI]  Destination not found: {dest_path}")
        else:
            print(f"[WARNING][EMOJI]  Source not found: {source_path}")

if __name__ == "__main__":
    sync_documentation()
```

## Git Workflow for Multi-Repository Development

### Git Submodules Approach (Advanced)

If you want tight integration, consider using submodules:

```bash
# In main pdoom1 repository
git submodule add https://github.com/PipFoweraker/pdoom1-website.git website
git submodule add https://github.com/PipFoweraker/pdoom1-data.git data

# Initialize submodules
git submodule init
git submodule update

# Add to .gitmodules for team consistency
```

### Cross-Repository Scripts

**File: `scripts/status-all.sh`**
```bash
# !/bin/bash
# Check status of all repositories

echo "=== P(Doom) Ecosystem Status ==="
echo

repos=("pdoom1" "pdoom1-website" "pdoom1-data")

for repo in "${repos[@]}"; do
    if [ -d "$repo" ]; then
        echo "[EMOJI] $repo:"
        cd "$repo"
        
        # Git status
        echo "   Branch: $(git branch --show-current)"
        echo "   Status: $(git status --porcelain | wc -l) files changed"
        echo "   Remote: $(git rev-list --count HEAD..origin/$(git branch --show-current) 2>/dev/null || echo '0') commits behind"
        
        cd ..
        echo
    else
        echo "[EMOJI] $repo: Not found"
        echo
    fi
done
```

**File: `scripts/pull-all.sh`**
```bash
# !/bin/bash
# Pull latest changes from all repositories

repos=("pdoom1" "pdoom1-website" "pdoom1-data")

for repo in "${repos[@]}"; do
    if [ -d "$repo" ]; then
        echo "[EMOJI] Updating $repo..."
        cd "$repo"
        git pull origin $(git branch --show-current)
        cd ..
        echo
    fi
done
```

## VS Code Extensions for Multi-Repository Work

Install these extensions for better multi-repo development:

```json
{
    "recommendations": [
        "eamodio.gitlens",           // Advanced Git integration
        "GitHub.vscode-pull-request-github", // GitHub PR management
        "ms-vscode.vscode-json",     // JSON editing
        "redhat.vscode-yaml",        // YAML editing  
        "ms-python.python",          // Python support
        "ms-vscode.vscode-typescript-next", // TypeScript support
        "streetsidesoftware.code-spell-checker", // Spell checking
        "yzhang.markdown-all-in-one" // Markdown editing
    ]
}
```

## Repository Status Dashboard

Create a simple status dashboard you can run:

**File: `scripts/dashboard.py`**
```python
# !/usr/bin/env python3
"""
Simple repository status dashboard
"""
import subprocess
import json
from pathlib import Path

def get_repo_info(repo_path):
    """Get information about a repository"""
    if not repo_path.exists():
        return {"status": "missing", "path": str(repo_path)}
    
    try:
        # Get current branch
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"], 
            cwd=repo_path,
            text=True
        ).strip()
        
        # Get status
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], 
            cwd=repo_path,
            text=True
        ).strip()
        
        # Get last commit
        last_commit = subprocess.check_output(
            ["git", "log", "-1", "--pretty=format:%h %s"], 
            cwd=repo_path,
            text=True
        ).strip()
        
        return {
            "status": "active",
            "branch": branch,
            "uncommitted_changes": len(status.split('\n')) if status else 0,
            "last_commit": last_commit,
            "path": str(repo_path)
        }
    except subprocess.CalledProcessError:
        return {"status": "error", "path": str(repo_path)}

def main():
    base_dir = Path(__file__).parent.parent
    
    repos = {
        "Game": base_dir / "pdoom1",
        "Website": base_dir / "pdoom1-website", 
        "Data": base_dir / "pdoom1-data"
    }
    
    print("[EMOJI] P(Doom) Ecosystem Status")
    print("=" * 50)
    
    for name, path in repos.items():
        info = get_repo_info(path)
        print(f"\n[EMOJI] {name}:")
        
        if info["status"] == "missing":
            print("   [EMOJI] Repository not found")
        elif info["status"] == "error":
            print("   [WARNING][EMOJI]  Git error")
        else:
            print(f"   [EMOJI] Branch: {info['branch']}")
            print(f"   [NOTE] Changes: {info['uncommitted_changes']}")
            print(f"   [DIZZY] Last: {info['last_commit']}")

if __name__ == "__main__":
    main()
```

## Quick Verification Steps

Run these commands to check your current multi-repo setup:

```bash
# 1. Check if website repo exists and is accessible
curl -s https://api.github.com/repos/PipFoweraker/pdoom1-website | jq '.name'

# 2. Check if data repo exists and is accessible  
curl -s https://api.github.com/repos/PipFoweraker/pdoom1-data | jq '.name'

# 3. Check GitHub Actions status
gh run list --repo PipFoweraker/pdoom1 --limit 5

# 4. Check current sync tokens
gh secret list --repo PipFoweraker/pdoom1
```

## Next Steps

1. **Verify Repository Status**: Run the verification commands above
2. **Set Up Workspace**: Create the VS Code workspace file
3. **Clone Missing Repos**: Clone any missing repositories  
4. **Configure Scripts**: Set up the cross-repo management scripts
5. **Update Integration Plan**: Revise the integration plan based on actual repository status

This approach will give you full visibility across all P(Doom) repositories while maintaining clean separation of concerns.
