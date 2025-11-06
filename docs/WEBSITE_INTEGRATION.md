# Website Integration Plan

**Repository**: [pdoom1-website](https://github.com/PipFoweraker/pdoom1-website)
**Strategy**: Static content sync from this repo to website

## Architecture

### Content Sources

This repo (`pdoom1`) serves as the **source of truth** for:
1. Game documentation
2. Leaderboard data exports
3. Release notes
4. Feature announcements

Website repo (`pdoom1-website`) **pulls** content from here.

### Sync Strategy

**Option A: Manual Sync** (Current)
- Copy markdown files to website repo as needed
- Website repo has own directory structure
- Allows website-specific formatting/styling

**Option B: Automated Sync** (Recommended)
- Script in this repo exports to `_website_export/`
- Website repo pulls from this export folder
- Git submodules or sync workflow

**Option C: Direct Links** (Simplest)
- Website links directly to GitHub docs
- No duplication, always up-to-date
- Less control over presentation

## Recommended: Option B (Automated Sync)

### Implementation

**In this repo** (`pdoom1`):
```
scripts/
└── sync_website_docs.py  # Export script

_website_export/           # Git-ignored working directory
└── docs/                  # Processed markdown for website
    ├── getting-started.md
    ├── gameplay.md
    ├── contributing.md
    └── ...

.github/workflows/
└── export_website_docs.yml  # Auto-export on release
```

**In website repo** (`pdoom1-website`):
```
content/
└── game/                  # Pulled from pdoom1/_website_export
    ├── getting-started.md
    ├── gameplay.md
    └── ...

scripts/
└── pull_game_docs.sh     # Sync script
```

### Sync Script Features

**`scripts/sync_website_docs.py`** should:
1. **Select** docs marked for website export
2. **Transform** GitHub-specific markdown → website markdown:
   - Convert relative links
   - Add front-matter for static site generators
   - Process images
3. **Export** to `_website_export/docs/`
4. **Validate** markdown syntax
5. **Generate** index/manifest

**Example front-matter transformation**:
```markdown
<!-- Source: docs/user-guide/GAMEPLAY.md -->

<!-- Becomes: -->
---
title: "How to Play"
slug: "gameplay"
category: "guides"
updated: "2025-10-31"
---
```

### Content Mapping

| pdoom1 Source | Website Location | Notes |
|---------------|------------------|-------|
| `README.md` | `content/game/index.md` | Overview only |
| `docs/user-guide/*.md` | `content/game/guides/` | Player docs |
| `docs/developer/*.md` | `content/game/dev/` | Dev docs |
| `docs/PRIVACY.md` | `content/game/privacy.md` | Privacy page |
| `CHANGELOG.md` | `content/game/releases.md` | Release history |
| Leaderboard exports | `static/data/leaderboards/` | JSON data |

## Leaderboard Data Sync

### Export Format

**Command**:
```bash
python -m src.leaderboard export --format web --output _website_export/leaderboards/
```

**Output Structure**:
```
_website_export/
└── leaderboards/
    ├── manifest.json          # List of all leaderboards
    ├── weekly-2025-w44.json   # Seed-specific leaderboard
    ├── daily-2025-10-31.json
    └── default.json
```

**Manifest Format**:
```json
{
  "version": "1.0",
  "updated": "2025-10-31T14:30:00Z",
  "leaderboards": [
    {
      "seed": "weekly-2025-w44",
      "entries": 52,
      "top_score": 25,
      "file": "weekly-2025-w44.json"
    }
  ]
}
```

### Website Integration

Website can:
1. **Fetch** `manifest.json` to list available leaderboards
2. **Load** specific leaderboard JSON files
3. **Display** top scores, rankings, statistics
4. **Filter** by seed, date range, player

## Automated Workflows

### GitHub Actions (pdoom1 repo)

**`.github/workflows/export_website_docs.yml`**:
```yaml
name: Export Website Docs

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  export:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Export docs
        run: python scripts/sync_website_docs.py

      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: website-docs
          path: _website_export/
```

### GitHub Actions (website repo)

**`.github/workflows/sync_game_docs.yml`**:
```yaml
name: Sync Game Docs

on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Download latest export
        run: ./scripts/pull_game_docs.sh

      - name: Commit changes
        run: |
          git config user.name "Bot"
          git config user.email "bot@pdoom.org"
          git add content/game/
          git commit -m "Sync game docs" || echo "No changes"
          git push
```

## Manual Sync Process

Until automation is set up:

1. **In pdoom1 repo**:
   ```bash
   # Export docs
   python scripts/sync_website_docs.py

   # Copy to website repo
   cp -r _website_export/docs/ ../pdoom1-website/content/game/
   ```

2. **In pdoom1-website repo**:
   ```bash
   git add content/game/
   git commit -m "Update game docs from pdoom1"
   git push
   ```

## Content Responsibilities

### pdoom1 Repo Owns
- Game mechanics documentation
- Developer guides
- Installation instructions
- Changelog/release notes
- Leaderboard data

### Website Repo Owns
- Site structure and navigation
- Styling and themes
- Landing pages and marketing
- Blog posts
- Community pages

## Next Steps

**To implement this**:

1. **Create `scripts/sync_website_docs.py`** (this repo)
   - Scan `docs/` for markdown files
   - Transform and export to `_website_export/`

2. **Create `.website_manifest.yml`** (this repo)
   - Mark which docs to export
   - Define transformations

3. **Add to .gitignore**:
   ```
   _website_export/
   ```

4. **In website repo**:
   - Create `scripts/pull_game_docs.sh`
   - Set up content structure
   - Add GitHub Action for auto-sync

5. **Test**:
   - Run manual sync
   - Verify content on website
   - Set up automated workflows

## URLs

Once live:
- **Website**: https://pdoom.org
- **Game Docs**: https://pdoom.org/game/
- **Guides**: https://pdoom.org/game/guides/
- **Leaderboards**: https://pdoom.org/leaderboards/
- **GitHub**: https://github.com/PipFoweraker/pdoom1

---

**Status**: Documentation complete, awaiting implementation in both repos.
**Next**: Create `sync_website_docs.py` script in this repo.
