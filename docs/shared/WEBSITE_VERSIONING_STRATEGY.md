# Website Versioning Strategy

## Overview

The pdoom1-website will maintain its own versioning system while tracking and displaying game version information as content. This creates a decoupled but synchronized system where:

1. **Website versions** track the website's own features and content
2. **Game version tracking** displays current and historical game releases
3. **Data batch integration** connects with pdoom-data for analytics and leaderboards

## Website Versioning Structure

### Version Schema
```
Website Version: MAJOR.MINOR.PATCH
- MAJOR: Site architecture changes, breaking API changes
- MINOR: New features, content sections, UI improvements  
- PATCH: Bug fixes, content updates, minor improvements

Examples:
- v1.0.0: Initial website launch
- v1.1.0: Add dev blog integration
- v1.1.1: Fix mobile responsive issues
- v1.2.0: Add game version tracking dashboard
```

### Version Storage
```json
{
  "website": {
    "version": "1.2.0",
    "release_date": "2025-09-15T00:00:00Z",
    "changelog_url": "/changelog",
    "build_info": {
      "commit": "abc123",
      "build_date": "2025-09-15T12:00:00Z",
      "environment": "production"
    }
  },
  "game_tracking": {
    "current_version": "0.6.0",
    "latest_release": {
      "version": "0.6.0",
      "release_date": "2025-09-14T00:00:00Z",
      "changelog_url": "/game/releases/0.6.0",
      "download_url": "https://github.com/PipFoweraker/pdoom1/releases/tag/v0.6.0"
    },
    "supported_versions": ["0.6.0", "0.5.0", "0.4.1"],
    "deprecated_versions": ["0.2.x", "0.1.x"]
  },
  "data_integration": {
    "current_batch": "2025-09-15",
    "data_version": "1.0.0",
    "last_sync": "2025-09-15T12:00:00Z",
    "status": "active"
  }
}
```

## Game Version Content Management

### Version Display System
- **Current Version Badge**: Prominent display of latest game version
- **Release Timeline**: Historical view of all game releases
- **Changelog Integration**: Formatted display of CHANGELOG.md content
- **Download Links**: Direct links to game releases
- **Compatibility Matrix**: Which website features work with which game versions

### Content Structure
```
/content/
[EMOJI][EMOJI][EMOJI] game-versions/
[EMOJI]   [EMOJI][EMOJI][EMOJI] v0.6.0/
[EMOJI]   [EMOJI]   [EMOJI][EMOJI][EMOJI] release-notes.md
[EMOJI]   [EMOJI]   [EMOJI][EMOJI][EMOJI] changelog.md
[EMOJI]   [EMOJI]   [EMOJI][EMOJI][EMOJI] features.json
[EMOJI]   [EMOJI]   [EMOJI][EMOJI][EMOJI] screenshots/
[EMOJI]   [EMOJI][EMOJI][EMOJI] v0.5.0/
[EMOJI]   [EMOJI][EMOJI][EMOJI] v0.4.1/
[EMOJI][EMOJI][EMOJI] version-history.json
[EMOJI][EMOJI][EMOJI] current-version.json
```

## Data Batch Integration (Future)

### Data Version Tracking
```json
{
  "data_batches": {
    "leaderboards": {
      "version": "1.2.0",
      "batch_date": "2025-09-15",
      "records_count": 15420,
      "schema_version": "1.0",
      "compatible_game_versions": ["0.6.0", "0.5.0"]
    },
    "analytics": {
      "version": "1.1.0", 
      "batch_date": "2025-09-15",
      "metrics_count": 8940,
      "schema_version": "1.0",
      "retention_days": 90
    },
    "challenges": {
      "version": "1.0.0",
      "batch_date": "2025-09-15", 
      "active_challenges": 12,
      "schema_version": "1.0",
      "seasonal_event": "autumn_2025"
    }
  }
}
```

### API Integration Points
```
GET /api/versions/website
GET /api/versions/game/current
GET /api/versions/game/history
GET /api/versions/data/current
GET /api/versions/compatibility-matrix
POST /api/versions/sync (webhook from game releases)
```

## Automation Strategy

### Version Sync Workflow
1. **Game Release Trigger**: GitHub webhook on pdoom1 tag creation
2. **Content Extraction**: Pull changelog, version info, release assets
3. **Website Update**: Update version tracking, create content pages
4. **Cache Invalidation**: Clear CDN cache for version-dependent content
5. **Notification**: Update version badges, send notifications

### Data Batch Sync (Future)
1. **Scheduled Sync**: Daily/weekly sync with pdoom-data
2. **Version Alignment**: Ensure data compatibility with game versions
3. **Content Updates**: Update leaderboards, statistics, analytics
4. **Rollback Support**: Version-specific data rollback capability

## Implementation Phases

### Phase 1: Website Versioning (Immediate)
- [ ] Create version.json file
- [ ] Add version display to website header/footer
- [ ] Implement basic changelog system
- [ ] Set up version API endpoints

### Phase 2: Game Version Tracking (Next)
- [ ] Create game version content management
- [ ] Build release timeline display
- [ ] Integrate with GitHub releases API
- [ ] Add automated version sync workflow

### Phase 3: Data Integration (Future)
- [ ] Design data batch API contracts
- [ ] Implement version compatibility checking
- [ ] Build data versioning dashboard
- [ ] Create automated data sync pipeline

## Content Strategy

### Version-Aware Content
- **Feature Documentation**: Tag content with minimum game version
- **Guides & Tutorials**: Version-specific instructions
- **API Documentation**: Compatibility matrices for different versions
- **Community Content**: Version-specific discussions and feedback

### SEO & Discovery
- **Structured Data**: Game version metadata for search engines
- **Canonical URLs**: Version-specific URLs for releases
- **Archive Strategy**: Maintain historical version content
- **Update Notifications**: RSS/Atom feeds for version updates

This strategy creates a robust, scalable system for website versioning while preparing for comprehensive game version tracking and future data integration.
