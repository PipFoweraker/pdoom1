# External Repositories Implementation Plan

**Issues:** #432, #433, #437
**Created:** 2025-12-24
**Status:** Planning

This document outlines the implementation plan for the three external repository issues that support the P(Doom) game ecosystem.

---

## Issue #432: Create pdoom-data Repository

### Overview
Create a new repository `pdoom-data` to serve as the centralized data landing and transformation zone for historical AI safety/capabilities events.

### Repository Structure

```
pdoom-data/
├── README.md                      # Repository overview
├── LICENSE                        # MIT or similar
├── CONTRIBUTING.md                # Contribution guidelines
├── CHANGELOG.md                   # Data version history
│
├── raw/                           # Raw source data (untransformed)
│   ├── alignment_research/        # Alignment Research Dataset extracts
│   ├── arxiv/                     # arXiv paper metadata
│   ├── news/                      # News article archives
│   └── organizations/             # Organization founding dates, etc.
│
├── transformed/                   # Game-ready event data
│   ├── timeline_events/           # Year-by-year event files
│   │   ├── 2000-2009.json
│   │   ├── 2010-2016.json
│   │   ├── 2017.json
│   │   ├── 2018.json
│   │   ├── 2019.json
│   │   ├── 2020.json
│   │   ├── 2021.json
│   │   ├── 2022.json
│   │   ├── 2023.json
│   │   └── 2024.json
│   └── organizations/             # AI safety org data
│       ├── labs.json
│       ├── research_orgs.json
│       └── conferences.json
│
├── schemas/                       # JSON schemas for validation
│   ├── event.schema.json
│   ├── organization.schema.json
│   └── timeline.schema.json
│
├── scripts/                       # Data processing scripts
│   ├── validate.py                # Schema validation
│   ├── transform.py               # Raw -> transformed conversion
│   ├── sync_to_pdoom1.sh          # Sync to game repo
│   ├── blog_manager.sh            # Blog post automation
│   └── extract_alignment_data.py  # Alignment Research Dataset extractor
│
├── docs/                          # Documentation
│   ├── DATA_SOURCES.md            # Source attribution
│   ├── TRANSFORMATION_RULES.md    # How raw -> transformed
│   ├── API_SPEC.md                # Future API documentation
│   └── PUBLISHING_STRATEGY.md     # Release cadence
│
├── blog/                          # Dev blog entries
│   └── entries/                   # Individual blog posts
│
├── .github/
│   └── workflows/
│       ├── validate.yml           # PR validation
│       ├── sync-to-game.yml       # Auto-sync to pdoom1
│       └── publish-api.yml        # Future: Deploy API
│
└── tests/
    ├── test_schemas.py
    ├── test_transforms.py
    └── test_data_integrity.py
```

### Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "date", "title", "category"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[a-z0-9_]+$",
      "description": "Unique identifier (snake_case)"
    },
    "date": {
      "type": "string",
      "format": "date",
      "description": "ISO 8601 date (YYYY-MM-DD)"
    },
    "title": {
      "type": "string",
      "maxLength": 100,
      "description": "Event title for display"
    },
    "description": {
      "type": "string",
      "maxLength": 500,
      "description": "Detailed event description"
    },
    "category": {
      "type": "string",
      "enum": ["organization", "research", "paper", "policy", "regulation", "capability", "incident", "funding", "conference"],
      "description": "Event category for transformation"
    },
    "significance": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10,
      "description": "Impact scale (1=minor, 10=paradigm-shifting)"
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Searchable tags"
    },
    "sources": {
      "type": "array",
      "items": {"type": "string", "format": "uri"},
      "description": "Source URLs for verification"
    }
  }
}
```

### Implementation Steps

1. **Create Repository**
   - Initialize pdoom-data on GitHub
   - Set up branch protection (main requires PR)
   - Add MIT license and README

2. **Set Up Structure**
   - Create directory structure as above
   - Add JSON schemas for validation
   - Create initial CONTRIBUTING.md

3. **Seed Initial Data**
   - Migrate `historical_events.json` from pdoom1
   - Split into year files (2000-2024)
   - Add source attribution

4. **Add Validation**
   - Python script for schema validation
   - Pre-commit hooks
   - GitHub Actions workflow

5. **Set Up Sync Pipeline**
   - Script to sync transformed data to pdoom1
   - GitHub Action to trigger on merge to main
   - PR automation in pdoom1

---

## Issue #433: Extract 2018-2019 Timeline

### Overview
Extract historical AI safety/capabilities events for 2018-2019 from the Alignment Research Dataset and other sources.

### Target Event Counts
- **2018:** 25-30 events
- **2019:** 30-35 events

### Data Sources

1. **Alignment Research Dataset**
   - URL: https://github.com/moirage/alignment-research-dataset
   - Contains: Papers, blog posts, forum discussions
   - Extract: Publication dates, titles, abstracts

2. **AI Alignment Forum Archive**
   - URL: https://www.alignmentforum.org
   - Contains: Research posts, discussions
   - Extract: Major posts with high karma

3. **Organization Announcements**
   - OpenAI blog, Anthropic announcements, DeepMind publications
   - Major funding rounds, leadership changes
   - Policy statements, safety commitments

4. **News Archives**
   - Major AI capability announcements
   - Policy/regulatory developments
   - Public discourse moments

### 2018 Key Events to Include

| Month | Event | Category | Significance |
|-------|-------|----------|--------------|
| Jan | MIRI 2017 Review | organization | 6 |
| Feb | OpenAI Five announced | capability | 7 |
| Mar | Cambridge Analytica scandal | incident | 8 |
| Apr | EU GDPR takes effect | regulation | 8 |
| Jun | Google AI Principles published | policy | 7 |
| Jul | OpenAI Dota 2 benchmark | capability | 6 |
| Aug | BAIR founded | organization | 6 |
| Oct | GPT-1 released | capability | 7 |
| Nov | AlphaFold announced | capability | 8 |
| Dec | AI Alignment Forum launched | organization | 7 |

### 2019 Key Events to Include

| Month | Event | Category | Significance |
|-------|-------|----------|--------------|
| Feb | OpenAI LP formed | organization | 8 |
| Feb | GPT-2 (staged release) | capability | 9 |
| Mar | Musk leaves OpenAI board | organization | 6 |
| Apr | CHAI established at Berkeley | organization | 7 |
| May | AI Now Institute report | policy | 6 |
| Jun | OpenAI accepts $1B from Microsoft | funding | 9 |
| Jul | DeepMind AlphaStar | capability | 7 |
| Sep | AI Safety Camp | organization | 5 |
| Oct | CSET founded at Georgetown | organization | 7 |
| Nov | OpenAI full GPT-2 release | capability | 8 |
| Dec | 80K Hours AI Safety profile | organization | 6 |

### Extraction Process

1. **Clone Alignment Research Dataset**
   ```bash
   git clone https://github.com/moirage/alignment-research-dataset
   ```

2. **Run Extraction Script**
   ```python
   # scripts/extract_alignment_data.py
   import json
   from datetime import datetime

   def extract_events(year: int) -> list:
       """Extract events for a given year from dataset"""
       events = []
       # Parse dataset, filter by date, categorize
       return events
   ```

3. **Manual Curation**
   - Review extracted events
   - Add missing major events
   - Verify dates and significance ratings
   - Add source URLs

4. **Validation**
   - Run schema validation
   - Check for duplicates
   - Verify category distribution

### Output Format

```json
{
  "year": 2018,
  "event_count": 28,
  "last_updated": "2025-12-24",
  "events": [
    {
      "id": "gpt1_released",
      "date": "2018-10-11",
      "title": "GPT-1 Released",
      "description": "OpenAI releases the first Generative Pre-trained Transformer, demonstrating the power of unsupervised pre-training for NLP tasks.",
      "category": "capability",
      "significance": 7,
      "tags": ["openai", "language-model", "transformer", "gpt"],
      "sources": ["https://openai.com/blog/language-unsupervised/"]
    }
  ]
}
```

---

## Issue #437: Automated Blog Publishing

### Overview
Automate blog content creation from commit metadata, dataset refresh logs, delta event updates, and pipeline release notes.

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   pdoom-data    │     │     pdoom1      │     │ pdoom1-website  │
│                 │     │                 │     │                 │
│  Timeline data  │────▶│  Game events    │     │   Blog posts    │
│  Blog entries   │     │  Integration    │────▶│   Release notes │
│  Release notes  │     │                 │     │   Dev updates   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                         GitHub Actions
                         (Automated Sync)
```

### Blog Entry Types

1. **Data Updates**
   - New historical events added
   - Source corrections
   - Significance adjustments

2. **Game Releases**
   - Version changelogs
   - New features
   - Bug fixes

3. **Pipeline Updates**
   - Infrastructure changes
   - New automation
   - Process improvements

4. **Community Updates**
   - Contributor acknowledgments
   - Roadmap updates
   - Milestone celebrations

### Blog Entry Schema

```json
{
  "id": "2025-12-24-historical-events-update",
  "title": "20 New Historical Events Added",
  "date": "2025-12-24",
  "author": "Pipeline Bot",
  "type": "data_update",
  "summary": "Added 20 curated AI safety timeline events from 2000-2024.",
  "content_markdown": "...",
  "metadata": {
    "source_repo": "pdoom-data",
    "source_commit": "abc123",
    "events_added": 20,
    "events_modified": 0,
    "events_removed": 0
  },
  "tags": ["data", "timeline", "events"],
  "published": true
}
```

### Automation Pipeline

```yaml
# .github/workflows/publish-blog.yml
name: Publish Blog Updates

on:
  push:
    branches: [main]
    paths:
      - 'transformed/timeline_events/**'
      - 'CHANGELOG.md'
  workflow_dispatch:
    inputs:
      blog_type:
        description: 'Blog entry type'
        required: true
        type: choice
        options:
          - data_update
          - release
          - pipeline
          - community

jobs:
  generate-blog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Detect changes
        id: changes
        run: |
          # Count new/modified events
          echo "events_added=$(git diff HEAD~1 --numstat transformed/ | wc -l)" >> $GITHUB_OUTPUT

      - name: Generate blog entry
        run: |
          python scripts/generate_blog.py \
            --type ${{ github.event.inputs.blog_type || 'data_update' }} \
            --commit ${{ github.sha }}

      - name: Publish to website repo
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.WEBSITE_REPO_TOKEN }}
          repository: PipFoweraker/pdoom1-website
          path: _posts/
          title: "Blog: ${{ steps.generate.outputs.title }}"
          body: "Automated blog post from pdoom-data"
```

### Blog Generation Script

```python
# scripts/generate_blog.py
import argparse
import json
from datetime import datetime
from pathlib import Path

def generate_blog_entry(blog_type: str, commit_sha: str) -> dict:
    """Generate a blog entry based on type and recent changes."""

    entry = {
        "id": f"{datetime.now().strftime('%Y-%m-%d')}-{blog_type}",
        "date": datetime.now().isoformat(),
        "type": blog_type,
        "metadata": {
            "source_commit": commit_sha,
            "generated_at": datetime.now().isoformat()
        }
    }

    if blog_type == "data_update":
        # Analyze recent data changes
        events_added = count_new_events()
        entry["title"] = f"{events_added} New Historical Events Added"
        entry["content"] = generate_data_update_content(events_added)

    elif blog_type == "release":
        # Parse CHANGELOG for release notes
        version, notes = parse_latest_release()
        entry["title"] = f"P(Doom) {version} Released"
        entry["content"] = notes

    return entry

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()

    entry = generate_blog_entry(args.type, args.commit)

    # Save to blog/entries/
    output_path = Path(f"blog/entries/{entry['id']}.json")
    output_path.write_text(json.dumps(entry, indent=2))

    print(f"Generated blog entry: {entry['id']}")

if __name__ == "__main__":
    main()
```

### Success Criteria

- [ ] 100% blog posts generated with complete provenance and metadata
- [ ] Automated integration with game, website, and data pipelines
- [ ] Zero manual copy-paste required for publishing
- [ ] Traceable links to source commits and events
- [ ] Validated against schema before publishing

---

## Implementation Order

### Phase 1: Foundation (Week 1)
1. Create pdoom-data repository (#432)
2. Set up directory structure and schemas
3. Migrate existing historical_events.json
4. Add validation scripts and CI

### Phase 2: Data Extraction (Week 2)
1. Extract 2018 timeline events (#433)
2. Extract 2019 timeline events
3. Validate and curate events
4. Set up sync pipeline to pdoom1

### Phase 3: Blog Automation (Week 3)
1. Implement blog generation scripts (#437)
2. Set up GitHub Actions workflows
3. Integrate with pdoom1-website
4. Test end-to-end publishing

### Phase 4: Polish (Week 4)
1. Documentation updates
2. Contributor guidelines
3. API documentation (future)
4. Performance optimization

---

## Dependencies

- pdoom1 EventService (completed in #442)
- GitHub repository access
- GitHub Actions secrets for cross-repo triggers
- pdoom1-website repository (if not exists, create)

---

*Document version: 1.0 | Last updated: 2025-12-24*
