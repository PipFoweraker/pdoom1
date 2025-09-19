# Cross-Repository Documentation Strategy: P(Doom) Ecosystem

## The Problem: Documentation Drift

In multi-repository architectures, documentation quickly becomes inconsistent across repositories. Common issues include:
- **Version Drift**: Updates in one repo aren't reflected in others
- **Source of Truth Confusion**: Which repository has the authoritative documentation?
- **Maintenance Overhead**: Manual synchronization is error-prone and time-consuming
- **Inconsistent Information**: Different repositories showing conflicting information

## Solution: Documentation as Code with Single Source of Truth

We'll implement a **hub-and-spoke documentation model** with automated synchronization.

## Architecture: Documentation Hub Pattern

### Primary Pattern: Central Documentation Repository

```
Documentation Flow Architecture

[EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI]    [EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI]    [EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI]
[EMOJI]     pdoom1      [EMOJI]    [EMOJI]  pdoom1-website [EMOJI]    [EMOJI]   pdoom-data    [EMOJI]
[EMOJI]   (Game Repo)   [EMOJI]    [EMOJI] (Website Repo)  [EMOJI]    [EMOJI] (Data Service)  [EMOJI]
[EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI]    [EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI]    [EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI]
[EMOJI] * Game Docs     [EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI] * Public Docs   [EMOJI]    [EMOJI] * API Docs      [EMOJI]
[EMOJI] * Dev Guides    [EMOJI]   [EMOJI][EMOJI] * User Guides   [EMOJI]    [EMOJI] * Data Schemas  [EMOJI]
[EMOJI] * Changelogs    [EMOJI]   [EMOJI][EMOJI] * Tutorials     [EMOJI]    [EMOJI] * Integration   [EMOJI]
[EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI]   [EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI]    [EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI]
         [EMOJI]             [EMOJI]         [EMOJI]                        [EMOJI]
         [EMOJI]             [EMOJI]         [EMOJI]                        [EMOJI]
         [EMOJI]             [EMOJI]         [EMOJI]                        [EMOJI]
    [EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI]
    [EMOJI]               [EMOJI] DOCUMENTATION HUB                          [EMOJI]
    [EMOJI]                (pdoom1/docs/ directory)                     [EMOJI]
    [EMOJI]  [EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI]  [EMOJI]
    [EMOJI]  [EMOJI]   Shared    [EMOJI]  Website    [EMOJI]    API      [EMOJI] Integration [EMOJI]  [EMOJI]
    [EMOJI]  [EMOJI]    Docs     [EMOJI]    Docs     [EMOJI]    Docs     [EMOJI]    Docs     [EMOJI]  [EMOJI]
    [EMOJI]  [EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI]  [EMOJI]
    [EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI][EMOJI]
                                   [EMOJI]
                             Automated Sync
                          (GitHub Actions + Scripts)
```

## Implementation Strategy

### 1. Establish Documentation Taxonomy

```
docs/
[EMOJI][EMOJI][EMOJI] shared/                           # Cross-repository documentation
[EMOJI]   [EMOJI][EMOJI][EMOJI] ECOSYSTEM_OVERVIEW.md        # High-level architecture
[EMOJI]   [EMOJI][EMOJI][EMOJI] INTEGRATION_PLAN.md          # Master integration document
[EMOJI]   [EMOJI][EMOJI][EMOJI] API_REFERENCE.md             # API documentation
[EMOJI]   [EMOJI][EMOJI][EMOJI] DATABASE_SCHEMA.md           # Database design
[EMOJI]   [EMOJI][EMOJI][EMOJI] DEPLOYMENT_GUIDE.md          # Deployment procedures
[EMOJI][EMOJI][EMOJI] game/                            # Game-specific documentation
[EMOJI]   [EMOJI][EMOJI][EMOJI] DEVELOPER_GUIDE.md           # Game development
[EMOJI]   [EMOJI][EMOJI][EMOJI] FEATURES.md                  # Game features
[EMOJI]   [EMOJI][EMOJI][EMOJI] CONFIGURATION.md             # Game configuration
[EMOJI][EMOJI][EMOJI] website/                         # Website-specific documentation
[EMOJI]   [EMOJI][EMOJI][EMOJI] CONTENT_MANAGEMENT.md       # Content workflow
[EMOJI]   [EMOJI][EMOJI][EMOJI] DEPLOYMENT.md               # Website deployment
[EMOJI]   [EMOJI][EMOJI][EMOJI] STYLING_GUIDE.md            # Design system
[EMOJI][EMOJI][EMOJI] data/                           # Data service documentation
[EMOJI]   [EMOJI][EMOJI][EMOJI] API_ENDPOINTS.md            # API specification
[EMOJI]   [EMOJI][EMOJI][EMOJI] SECURITY.md                 # Security implementation
[EMOJI]   [EMOJI][EMOJI][EMOJI] MONITORING.md               # Monitoring setup
[EMOJI][EMOJI][EMOJI] templates/                      # Documentation templates
    [EMOJI][EMOJI][EMOJI] README.template.md          # Standard README format
    [EMOJI][EMOJI][EMOJI] CHANGELOG.template.md       # Changelog format
    [EMOJI][EMOJI][EMOJI] API_DOC.template.md         # API documentation format
```

### 2. Documentation Synchronization Strategies

#### Option A: Hub-and-Spoke (Recommended)

**Source of Truth**: `pdoom1/docs/` (main game repository)
**Sync Direction**: pdoom1 -> other repositories

**Advantages**:
- Single source of truth
- Centralized maintenance
- Consistent versioning with game releases
- Simple conflict resolution

**Implementation**:
```yaml
# .github/workflows/sync-documentation.yml
name: Sync Documentation Across Repositories

on:
  push:
    paths:
      - 'docs/shared/**'
      - 'docs/website/**'
      - 'docs/data/**'
    branches: [main]
  workflow_dispatch:

jobs:
  sync-docs:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        target:
          - repo: pdoom1-website
            docs: ['shared/', 'website/']
            destination: 'docs/'
          - repo: pdoom-data
            docs: ['shared/', 'data/']
            destination: 'docs/'
    
    steps:
      - name: Checkout source
        uses: actions/checkout@v4
        
      - name: Checkout target
        uses: actions/checkout@v4
        with:
          repository: PipFoweraker/${{ matrix.target.repo }}
          token: ${{ secrets.CROSS_REPO_TOKEN }}
          path: target-repo
          
      - name: Sync documentation
        run: |
          for doc_dir in ${{ join(matrix.target.docs, ' ') }}; do
            echo "Syncing docs/$doc_dir to ${{ matrix.target.repo }}"
            rsync -av --delete \
              "docs/$doc_dir" \
              "target-repo/${{ matrix.target.destination }}"
          done
          
      - name: Commit and push changes
        working-directory: target-repo
        run: |
          git config user.email "docs-sync@pdoom.net"
          git config user.name "Documentation Sync Bot"
          
          if [[ -n $(git status --porcelain) ]]; then
            git add .
            git commit -m "docs: sync from pdoom1@$(echo $GITHUB_SHA | head -c 7)"
            git push
          else
            echo "No documentation changes to sync"
          fi
```

#### Option B: Distributed with Validation

**Source of Truth**: Each repository owns its domain-specific docs
**Sync Direction**: Bidirectional with validation

**Advantages**:
- Domain expertise in appropriate repositories
- Parallel development possible
- Specialized tooling per repository type

**Implementation**:
```yaml
# Cross-repository documentation validation
name: Validate Cross-Repo Documentation

on:
  pull_request:
    paths: ['docs/**']

jobs:
  validate-consistency:
    runs-on: ubuntu-latest
    steps:
      - name: Check documentation consistency
        run: |
          # Fetch documentation from all repositories
          # Validate cross-references
          # Check for conflicts
          # Generate consistency report
```

### 3. Documentation Automation Tools

#### A. Documentation Sync Script

**File: `scripts/sync-docs.py`**
```python
#!/usr/bin/env python3
"""
Cross-repository documentation synchronization tool
"""
import subprocess
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple

class DocSyncer:
    def __init__(self, config_file: str = "docs/sync-config.yml"):
        self.config = self._load_config(config_file)
        self.base_path = Path(".")
        
    def _load_config(self, config_file: str) -> Dict:
        """Load synchronization configuration"""
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def sync_to_repository(self, target_repo: str) -> bool:
        """Sync documentation to target repository"""
        config = self.config['repositories'][target_repo]
        
        # Clone or update target repository
        repo_path = self._ensure_repo(target_repo, config['url'])
        
        # Copy documentation files
        for source_path, dest_path in config['mappings'].items():
            self._copy_docs(source_path, repo_path / dest_path)
        
        # Commit and push changes
        return self._commit_changes(repo_path, target_repo)
    
    def _ensure_repo(self, repo_name: str, repo_url: str) -> Path:
        """Ensure repository is available locally"""
        repo_path = Path(f"temp/{repo_name}")
        
        if repo_path.exists():
            # Pull latest changes
            subprocess.run(["git", "pull"], cwd=repo_path)
        else:
            # Clone repository
            repo_path.parent.mkdir(exist_ok=True)
            subprocess.run(["git", "clone", repo_url, str(repo_path)])
        
        return repo_path
    
    def _copy_docs(self, source: str, destination: Path):
        """Copy documentation files with preprocessing"""
        source_path = self.base_path / "docs" / source
        
        if source_path.is_file():
            # Process single file
            content = self._process_file(source_path, destination.parent.name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content)
        elif source_path.is_dir():
            # Process directory
            for file_path in source_path.rglob("*.md"):
                rel_path = file_path.relative_to(source_path)
                dest_file = destination / rel_path
                content = self._process_file(file_path, destination.name)
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_text(content)
    
    def _process_file(self, file_path: Path, target_repo: str) -> str:
        """Process documentation file for target repository"""
        content = file_path.read_text()
        
        # Apply repository-specific transformations
        transformations = self.config.get('transformations', {})
        repo_transforms = transformations.get(target_repo, {})
        
        for pattern, replacement in repo_transforms.items():
            content = content.replace(pattern, replacement)
        
        # Add sync metadata
        sync_header = f"""<!-- 
This file is automatically synced from pdoom1/docs/{file_path.relative_to(self.base_path / 'docs')}
Last synced: {datetime.now().isoformat()}
DO NOT EDIT DIRECTLY - Changes will be overwritten
-->

"""
        return sync_header + content
    
    def _commit_changes(self, repo_path: Path, repo_name: str) -> bool:
        """Commit and push documentation changes"""
        try:
            # Check for changes
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                cwd=repo_path, 
                capture_output=True, 
                text=True
            )
            
            if not result.stdout.strip():
                print(f"No documentation changes for {repo_name}")
                return True
            
            # Commit changes
            subprocess.run(["git", "add", "."], cwd=repo_path)
            subprocess.run([
                "git", "commit", "-m", 
                f"docs: sync from pdoom1 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
            ], cwd=repo_path)
            
            # Push changes
            subprocess.run(["git", "push"], cwd=repo_path)
            print(f"Successfully synced documentation to {repo_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to sync documentation to {repo_name}: {e}")
            return False

if __name__ == "__main__":
    syncer = DocSyncer()
    
    # Sync to all configured repositories
    for repo in syncer.config['repositories']:
        syncer.sync_to_repository(repo)
```

#### B. Documentation Configuration

**File: `docs/sync-config.yml`**
```yaml
# Documentation synchronization configuration
repositories:
  pdoom1-website:
    url: "https://github.com/PipFoweraker/pdoom1-website.git"
    mappings:
      "shared/ECOSYSTEM_OVERVIEW.md": "docs/ECOSYSTEM_OVERVIEW.md"
      "shared/INTEGRATION_PLAN.md": "docs/INTEGRATION_PLAN.md"
      "website/": "docs/website/"
      "templates/README.template.md": "docs/templates/README.template.md"
    
  pdoom-data:
    url: "https://github.com/PipFoweraker/pdoom-data.git"
    mappings:
      "shared/ECOSYSTEM_OVERVIEW.md": "docs/ECOSYSTEM_OVERVIEW.md"
      "shared/API_REFERENCE.md": "docs/API_REFERENCE.md"
      "data/": "docs/"
      "templates/": "docs/templates/"

# Repository-specific content transformations
transformations:
  pdoom1-website:
    "pdoom-data": "pdoom-data"
    "../pdoom1/": "../"
  
  pdoom-data:
    "pdoom1/docs/": "docs/"
    "game repository": "pdoom1 repository"

# Documentation validation rules
validation:
  cross_references:
    - pattern: '\[.*\]\(\.\.\/.*\.md\)'
      check: "relative_links"
  
  consistency:
    - files: ["shared/ECOSYSTEM_OVERVIEW.md"]
      check: "repository_list"
    - files: ["shared/API_REFERENCE.md"] 
      check: "endpoint_consistency"
```

### 4. Advanced Documentation Patterns

#### A. Documentation Versioning

```yaml
# docs/versions.yml
documentation_versions:
  current: "v0.4.1"
  
  versions:
    "v0.4.1":
      pdoom1: "main"
      pdoom1-website: "main"
      pdoom-data: "main"
    
    "v0.4.0":
      pdoom1: "v0.4.0"
      pdoom1-website: "v0.4.0-website"
      pdoom-data: "v0.4.0-data"

sync_strategy:
  production: "tag_based"    # Sync on version tags
  development: "branch_based" # Sync on main branch updates
```

#### B. Documentation Templates with Variables

**Template: `templates/API_ENDPOINT.template.md`**
```markdown
# {{ENDPOINT_NAME}} API

## Endpoint Information
- **URL**: `{{BASE_URL}}/{{ENDPOINT_PATH}}`
- **Method**: `{{HTTP_METHOD}}`
- **Authentication**: {{AUTH_TYPE}}

## Repository Context
This endpoint is part of the {{REPO_NAME}} service in the P(Doom) ecosystem.

<!-- AUTO-GENERATED: Do not edit below this line -->
{{GENERATED_CONTENT}}
```

#### C. Cross-Repository Link Validation

**File: `scripts/validate-links.py`**
```python
#!/usr/bin/env python3
"""
Validate cross-repository documentation links
"""
import re
import requests
from pathlib import Path
from typing import List, Tuple

class LinkValidator:
    def __init__(self):
        self.repositories = {
            'pdoom1': 'https://github.com/PipFoweraker/pdoom1',
            'pdoom1-website': 'https://github.com/PipFoweraker/pdoom1-website',
            'pdoom-data': 'https://github.com/PipFoweraker/pdoom-data'
        }
    
    def validate_all_links(self) -> List[Tuple[str, str, bool]]:
        """Validate all cross-repository links"""
        results = []
        
        for md_file in Path("docs").rglob("*.md"):
            results.extend(self._validate_file_links(md_file))
        
        return results
    
    def _validate_file_links(self, file_path: Path) -> List[Tuple[str, str, bool]]:
        """Validate links in a single file"""
        content = file_path.read_text()
        results = []
        
        # Find all markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
        for link_text, link_url in links:
            if self._is_cross_repo_link(link_url):
                valid = self._validate_cross_repo_link(link_url)
                results.append((str(file_path), link_url, valid))
        
        return results
    
    def _is_cross_repo_link(self, url: str) -> bool:
        """Check if link is a cross-repository reference"""
        return any(repo in url for repo in self.repositories.keys())
    
    def _validate_cross_repo_link(self, url: str) -> bool:
        """Validate a cross-repository link"""
        # Convert relative paths to absolute GitHub URLs
        github_url = self._convert_to_github_url(url)
        
        try:
            response = requests.head(github_url, timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def _convert_to_github_url(self, relative_url: str) -> str:
        """Convert relative repository path to GitHub URL"""
        # Implementation to convert ../pdoom1-website/docs/file.md
        # to https://github.com/PipFoweraker/pdoom1-website/blob/main/docs/file.md
        pass

if __name__ == "__main__":
    validator = LinkValidator()
    results = validator.validate_all_links()
    
    # Report results
    broken_links = [r for r in results if not r[2]]
    if broken_links:
        print("[EMOJI] Broken cross-repository links found:")
        for file_path, link, _ in broken_links:
            print(f"  {file_path}: {link}")
        exit(1)
    else:
        print("[EMOJI] All cross-repository links are valid")
```

## Implementation Roadmap

### Phase 1: Setup (Week 1)
1. **Documentation Taxonomy**: Organize existing docs into the new structure
2. **Sync Configuration**: Create `sync-config.yml` with repository mappings
3. **Basic Sync Script**: Implement simple documentation synchronization
4. **GitHub Actions**: Set up automated sync workflows

### Phase 2: Automation (Week 2)
1. **Advanced Sync**: Add preprocessing and transformation capabilities
2. **Link Validation**: Implement cross-repository link checking
3. **Version Management**: Add documentation versioning support
4. **Monitoring**: Set up sync status monitoring

### Phase 3: Enhancement (Week 3)
1. **Templates**: Create standardized documentation templates
2. **Validation Rules**: Add consistency checking across repositories
3. **Dashboard**: Create documentation status dashboard
4. **Integration**: Integrate with existing dev workflows

## Quick Start Commands

```bash
# Initialize documentation structure
python scripts/init-docs.py

# Sync documentation to all repositories
python scripts/sync-docs.py --all

# Validate cross-repository links
python scripts/validate-links.py

# Check sync status
python scripts/doc-status.py
```

This approach gives you:
- **Single Source of Truth**: Clear ownership and authority
- **Automated Consistency**: No manual synchronization needed  
- **Version Control**: Full history of documentation changes
- **Validation**: Automated checking for broken links and inconsistencies
- **Scalability**: Easily add new repositories to the ecosystem

Would you like me to implement any specific part of this system first?
