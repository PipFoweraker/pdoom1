# Contributor System - Technical Documentation

## Architecture Overview

The PDoom contributor recognition system is a multi-repository, privacy-first architecture for recognizing community contributions through the "Office Cat" feature.

## System Components

### 1. PDoom1 Game Repository (This Repo)

**Components:**
- `godot/scripts/data/contributor_manager.gd` - Loads and manages contributor data
- `godot/scripts/ui/office_cat.gd` - Displays contributor cats with doom variants
- `godot/scenes/ui/office_cat.tscn` - Office cat UI scene
- `godot/data/contributors.json` - Contributor data (synced from pdoom-data)
- `godot/assets/cats/` - Cat image assets
- `godot/scripts/core/bug_reporter.gd` - In-game bug reporting system
- `godot/scenes/ui/bug_report_panel.tscn` - Bug reporter UI
- `tools/process_bug_reports.py` - Local bug report  ->  GitHub issue processor

**Responsibilities:**
- Display office cats in-game
- Collect bug reports/feedback locally
- Load contributor data from JSON
- Provide bug reporting UI (F8 key)

### 2. PDoom1-Website Repository

**Purpose:** Web-facing contributor management

**Components (See [Issue #70](https://github.com/PipFoweraker/pdoom1-website/issues/70)):**
- Airtable CRM system for tracking contributors
- Anonymous bug/feedback submission web form
- Web form  ->  GitHub API  ->  Airtable pipeline
- Forum integration for displaying GitHub issues
- Contributor dashboard (future)

**Responsibilities:**
- Accept anonymous bug reports via web form
- Create GitHub issues from submissions
- Track contributors in Airtable CRM
- Manage contributor approval workflow

### 3. PDoom-Data Repository

**Purpose:** Centralized contributor data and cat assets

**Components (See [Issue #22](https://github.com/PipFoweraker/pdoom-data/issues/22)):**
- `contributors.json` - Master contributor database
- `cats/{contributor_uuid}/` - Cat image assets (5 doom variants each)
- Cat image processing pipeline
- Validation schemas

**Responsibilities:**
- Store approved contributor data
- Host cat image assets
- Validate contributor data integrity
- Sync data to pdoom1 repository

## Data Flow

### Bug Report Submission Flow

```
Player submits bug (F8 in-game)
     v 
Local save to user://bug_reports/
     v 
Admin runs tools/process_bug_reports.py
     v 
GitHub issue created (label: community-submission)
     v 
Webhook  ->  Airtable CRM (future)
     v 
Admin reviews and approves
```

### Contributor Recognition Flow

```
Contribution approved in Airtable CRM
     v 
Admin requests cat photo from contributor
     v 
Photo processed  ->  5 doom variants
     v 
Upload to pdoom-data repo: cats/{uuid}/
     v 
Add entry to pdoom-data: contributors.json
     v 
CI/CD syncs pdoom-data  ->  pdoom1
     v 
Next game release includes contributor cat
```

## Data Schemas

### contributors.json

Location: `godot/data/contributors.json` (synced from pdoom-data)

```json
{
  "version": "1.0",
  "last_updated": "2025-01-10T12:00:00Z",
  "contributors": [
    {
      "id": "uuid-v4",
      "name": "Contributor Display Name",
      "cat_name": "Office Cat Name",
      "cat_image_base": "contributor_uuid",
      "contribution_types": ["bug_report", "feature_request", "playtesting"],
      "date_added": "2025-01-10",
      "total_contributions": 5
    }
  ]
}
```

### Bug Report JSON

Location: `user://bug_reports/bug_report_TIMESTAMP.json`

```json
{
  "report_type": "bug|feature_request|feedback",
  "title": "Brief summary",
  "description": "Detailed description",
  "system_info": {
    "os_type": "Windows|Linux|macOS",
    "godot_version": "4.x.x",
    "game_version": "0.11.0",
    "timestamp": "2025-01-10T12:00:00Z"
  },
  "attribution": {
    "name": "Contributor Name (optional)",
    "contact": "email@example.com (optional)"
  },
  "attachments": {
    "screenshot_included": true,
    "save_file_included": false
  },
  "created_at": "2025-01-10T12:00:00Z"
}
```

## Cat Image Processing

### Directory Structure

```
godot/assets/cats/
|--- default/
|   |--- happy.png
|   |--- concerned.png
|   |--- worried.png
|   |--- distressed.png
|   `--- corrupted.png
`--- {contributor_uuid}/
    |--- happy.png
    |--- concerned.png
    |--- worried.png
    |--- distressed.png
    `--- corrupted.png
```

### Image Specifications

- **Format**: PNG with transparency
- **Size**: 256x256 pixels
- **Doom Progression**: 5 variants representing increasing corruption
- **Style**: Consistent with game art aesthetic

### Processing Pipeline (Future)

The cat image processing will be automated via `pdoom-data` repository:

1. Contributor uploads original photo
2. Script extracts subject, removes background
3. AI processing generates 5 doom-level variants
4. Manual review and approval
5. Upload to pdoom-data repository
6. Sync to pdoom1 via CI/CD

**Current Implementation:** Manual processing using image editing tools or GPT Vision.

## Privacy & Security

### Privacy-First Design

- **Local-first**: Bug reports saved locally by default
- **Opt-in attribution**: Contributors choose whether to be recognized
- **Anonymous submissions**: No personal data required
- **Clear consent**: Explicit opt-in for cat photo submission
- **Data ownership**: Contributors can request removal at any time

### Data Handling

- **Minimal collection**: Only essential info for debugging/recognition
- **No tracking**: No analytics on who reports bugs (unless opted-in)
- **Secure storage**: Airtable CRM with access controls
- **Public data**: Only approved, consensual data published

See [PRIVACY.md](PRIVACY.md) for full privacy policy.

## API Integration Points

### Future: PDoom1-Website API

When the web form is live, the bug reporter can POST directly:

```gdscript
# Future implementation in bug_reporter.gd
func submit_to_api(report: Dictionary) -> bool:
    var http = HTTPRequest.new()
    add_child(http)

    var url = "https://pdoom.net/api/bug_reports"
    var headers = ["Content-Type: application/json"]
    var body = JSON.stringify(report)

    http.request(url, headers, HTTPClient.METHOD_POST, body)
    # Handle response...
```

### Contributor Data Sync (Future)

Automated sync from pdoom-data to pdoom1:

```yaml
# .github/workflows/sync-contributors.yml
name: Sync Contributor Data

on:
  repository_dispatch:
    types: [contributors-updated]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Download contributors.json from pdoom-data
      - name: Copy to godot/data/contributors.json
      - name: Download cat images from pdoom-data
      - name: Copy to godot/assets/cats/
      - name: Commit and push changes
```

## Developer Guide

### Adding a Contributor Manually

1. Generate UUID: `uuidgen` or [online tool](https://www.uuidgenerator.net/)
2. Process cat image into 5 doom variants
3. Add to `pdoom-data` repository:
   ```bash
   # Add cat images
   mkdir -p cats/{uuid}
   cp happy.png cats/{uuid}/happy.png
   # ... (repeat for all 5 variants)

   # Update contributors.json
   # Add contributor entry with matching UUID
   ```
4. Contributor data will sync to pdoom1 on next release

### Testing Office Cat System

```gdscript
# In main UI or test scene
var contributor_manager = ContributorManager.new()
add_child(contributor_manager)

# Load contributors
contributor_manager.load_contributors()

# Get random contributor
var contributor = contributor_manager.get_random_contributor()
print("Contributor: %s" % contributor.get("name", "Unknown"))

# Get cat image for doom level
var doom_level = 0.75  # 75% doom
var cat_image = contributor_manager.get_cat_image_for_doom_level(doom_level)
print("Cat image: %s" % cat_image)
```

### Processing Local Bug Reports

```bash
# Run bug report processor
python tools/process_bug_reports.py --dry-run

# Process and create GitHub issues
python tools/process_bug_reports.py --archive

# Process only first 5 reports
python tools/process_bug_reports.py --limit 5
```

## Roadmap

### Phase 1: Foundation SUCCESS (v0.11.0)
- [x] Contributor manager (GDScript)
- [x] Bug reporter (GDScript + UI)
- [x] Office cat UI component
- [x] Local bug report processing tool
- [x] Documentation

### Phase 2: Web Integration (v0.12.0)
- [ ] pdoom1-website Airtable CRM (Issue #70)
- [ ] Anonymous web form for bug submissions
- [ ] Web form  ->  GitHub API pipeline
- [ ] Forum integration (Issue #71)

### Phase 3: Automation (v0.13.0)
- [ ] pdoom-data contributor sync pipeline (Issue #22)
- [ ] Automated cat image processing
- [ ] CI/CD contributor data sync
- [ ] Webhook integration (Airtable  ->  GitHub  ->  pdoom-data)

### Phase 4: Enhancements (Future)
- [ ] In-game contributor gallery
- [ ] Contributor dashboard on website
- [ ] Achievement system for contributions
- [ ] Seasonal cat variants

## Related Documentation

- [CONTRIBUTOR_REWARDS.md](CONTRIBUTOR_REWARDS.md) - User-facing contributor program info
- [PRIVACY.md](PRIVACY.md) - Privacy policy
- [CONTROLS.md](CONTROLS.md) - Keyboard shortcuts (including F8 for bug reporter)

## External Links

- [pdoom1-website Issue #70](https://github.com/PipFoweraker/pdoom1-website/issues/70) - Airtable CRM
- [pdoom1-website Issue #71](https://github.com/PipFoweraker/pdoom1-website/issues/71) - Forum integration
- [pdoom-data Issue #22](https://github.com/PipFoweraker/pdoom-data/issues/22) - Data sync pipeline

---

*This document reflects the current implementation as of v0.11.0. The contributor system is under active development.*

*Last Updated: 2025-01-10*
