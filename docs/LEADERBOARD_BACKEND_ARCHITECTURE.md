# Leaderboard Backend Architecture

**Date**: 2025-11-19
**Status**: Planning
**Priority**: HIGH - Main blocker for launch alongside Steam integration

---

## Executive Summary

This document outlines the phased approach to evolving P(Doom)'s leaderboard system from local-only storage to a connected backend service. The goal is to enable competitive play across players while maintaining the existing robust local system as a fallback.

---

## Current State Analysis

### Existing Infrastructure (Fully Functional)

**Game (Godot):**
- `godot/scripts/leaderboard.gd` - Local JSON persistence
- `ScoreEntry` class with UUID, metadata, timestamps
- Seed-specific leaderboard segregation
- UI in `leaderboard_screen.gd` with pagination, filtering

**Game (Python/Pygame - Legacy):**
- `src/scores/enhanced_leaderboard.py` - EnhancedLeaderboardManager
- GameSession tracking with economic model metrics
- `scripts/export_leaderboards.py` - Web export CLI

**Website (pdoom1-website):**
- Static JSON files in `public/leaderboard/data/`
- GitHub workflow for syncing (`sync-leaderboards.yml`)
- Integration spec at `docs/03-integrations/leaderboard-integration-spec.md`
- Already has seed filtering and display components

**Data Repo (pdoom-data):**
- Historical event data architecture
- Separate from game data

### Current Data Flow

```
+-------------------+     Manual Export      +--------------------+
|   Godot Game    | --------------------- ->  |   pdoom1-website |
| (Local JSON)    |    or git commit       | (Static JSON)    |
`-------------------`                        `--------------------`
        v                                              v 
  user://leaderboards/              public/leaderboard/data/
  leaderboard_{seed}.json           seed_leaderboard_*.json
```

### Gaps Blocking Launch

1. **No real-time submission** - Players must manually export scores
2. **No player authentication** - Can't verify identity across devices
3. **No anti-cheat** - Scores not validated
4. **No Steam integration** - Missing platform identity and achievements

---

## Phased Implementation Plan

### Phase 0: Foundation (Current Sprint)

**Goal**: Ensure Godot leaderboard matches website format

**Tasks**:
- [ ] Verify Godot ScoreEntry fields match website JSON schema
- [ ] Add export functionality to Godot version (like Python has)
- [ ] Test manual export  ->  website workflow with Godot
- [ ] Document data flow for alpha testers

**Deliverables**:
- Godot leaderboard exporter script
- Verified data format compatibility
- Alpha tester documentation

**Effort**: 2-4 hours

---

### Phase 1: Semi-Automated Sync

**Goal**: Reduce manual effort for leaderboard updates

**Architecture**:
```
+---------------+    Local Save    +---------------+
|   Godot     | --------------- ->  |  Local JSON |
|   Game      |                  |   Files     |
`---------------`                  `-------+-------`
                                        |
                                  Export Script
                                        |
                                         v 
+---------------------------------------------------+
|               GitHub Repository                  |
|  (pdoom1-website/public/leaderboard/data/)      |
`---------------------------------------------------`
                         |
                    GitHub Actions
                    (on push)
                         |
                          v 
              +--------------------+
              |    Website       |
              | (Static Hosting) |
              `--------------------`
```

**Options**:
1. **GitHub CLI integration** - `gh` commands from game
2. **Git hooks** - Auto-commit on game over
3. **Desktop sync app** - Background service

**Tasks**:
- [ ] Add GitHub CLI detection to game
- [ ] Create `submit_to_github.gd` script
- [ ] Implement rate limiting (max 1 submission per game)
- [ ] Add user confirmation before submission
- [ ] Create GitHub Action to validate and merge

**Effort**: 1-2 days

---

### Phase 2: Simple REST Backend

**Goal**: Real-time score submission without GitHub

**Architecture**:
```
+---------------+   HTTPS POST    +-------------------+
|   Godot     | --------------- -> |  Backend API    |
|   Game      |                 | (Cloudflare/    |
`---------------`                 |  Vercel/Fly)    |
                                `---------+---------`
                                         |
                                    PostgreSQL
                                    or JSON files
                                         |
                                          v 
                                +--------------------+
                                |    Website       |
                                | (Fetches API)    |
                                `--------------------`
```

**Backend Requirements**:
```
Endpoints:
  POST /api/v1/scores              # Submit score
  GET  /api/v1/leaderboards/{seed} # Get leaderboard
  GET  /api/v1/leaderboards        # List all seeds

Score Submission Schema:
{
  "player_id": "device-uuid or steam-id",
  "lab_name": "AI Safety Lab",
  "score": 85,
  "seed": "weekly-2025-W47",
  "final_doom": 15.3,
  "final_money": 2500000,
  "game_version": "v0.10.1",
  "economic_model": "Bootstrap_v0.4.1",
  "duration_seconds": 1245.5,
  "timestamp": "2025-11-19T14:30:00Z"
}
```

**Hosting Options**:
- **Cloudflare Workers** - Free tier, edge computing
- **Vercel Serverless** - Easy deployment from website repo
- **Fly.io** - Good for game backends
- **Railway/Render** - Simple PostgreSQL hosting

**Tasks**:
- [ ] Design API schema
- [ ] Choose hosting platform
- [ ] Implement backend (Node/Python/Go)
- [ ] Add HTTPRequest to Godot
- [ ] Create BackendAPI autoload singleton
- [ ] Implement retry logic and offline queue
- [ ] Fallback to local storage if offline

**Effort**: 3-5 days

---

### Phase 3: Player Authentication

**Goal**: Identify players across devices

**Options**:

#### Option A: Anonymous Device ID
- Generate UUID on first launch
- Store in user preferences
- Simple, no account needed
- Can't transfer between devices

#### Option B: Steam Authentication
- Use Steam ID as player identifier
- Requires Steamworks SDK integration
- Enables Steam achievements
- Players must own game on Steam

#### Option C: Simple Account System
- Email + password
- OAuth (Google, GitHub, Discord)
- More complex to implement
- Better for cross-platform

**Recommended Path**:
1. Start with **Device ID** (Phase 3a)
2. Add **Steam Auth** when integrating achievements (Phase 3b)
3. Consider **OAuth** for web leaderboard later (Phase 3c)

**Tasks**:
- [ ] Implement device ID generation
- [ ] Add device ID to score submissions
- [ ] Backend: player registration endpoint
- [ ] Handle player name changes
- [ ] (Later) Steam SDK integration
- [ ] (Later) OAuth providers

**Effort**: 2-4 days

---

### Phase 4: Steam Integration

**Goal**: Full Steamworks integration

**Features**:
- Steam ID authentication
- Steam achievements
- Steam leaderboards (optional)
- Steam Cloud saves
- Rich presence

**Architecture**:
```
+---------------+     GDExtension     +-------------------+
|   Godot     |  <- ----------------- ->  |  Steamworks SDK |
|   Game      |                     |  (via GodotSteam)|
`-------+-------`                     `-------------------`
       |
       | Steam ID + Auth Token
        v 
+-------------------+     Verify Token    +----------------+
|  Backend API    |  <- ----------------- ->  |  Steam Web   |
|                 |                     |  API         |
`-------------------`                     `----------------`
```

**Tasks**:
- [ ] Register on Steamworks
- [ ] Integrate GodotSteam plugin
- [ ] Implement Steam authentication
- [ ] Add achievement definitions
- [ ] Backend: Steam token verification
- [ ] Steam leaderboard sync (optional)
- [ ] Steam Cloud save integration

**Dependencies**:
- Steam developer account
- Steam App ID
- Steamworks SDK
- GodotSteam GDExtension

**Effort**: 1-2 weeks

---

### Phase 5: Anti-Cheat & Validation

**Goal**: Prevent cheating and invalid scores

**Strategies**:

1. **Client-Side Validation**
   - Hash game state at game over
   - Include in submission
   - Backend verifies hash matches expected

2. **Statistical Analysis**
   - Flag anomalous scores
   - Check score vs game duration
   - Detect impossible resource combinations

3. **Rate Limiting**
   - Max submissions per hour/day
   - IP-based limits
   - Player-based limits

4. **Replay Validation** (Advanced)
   - Record game inputs
   - Server re-simulates
   - Compare final state

**Tasks**:
- [ ] Design hash verification scheme
- [ ] Implement client-side hash generation
- [ ] Backend: hash validation
- [ ] Add statistical anomaly detection
- [ ] Create admin tools for manual review
- [ ] (Optional) Replay recording

**Effort**: 3-7 days

---

## Technology Recommendations

### Backend Stack Options

**Option 1: Serverless (Recommended for MVP)**
```
Cloudflare Workers + KV Storage
- Free tier: 100K requests/day
- Low latency globally
- Simple deployment
- KV for score storage (10M reads/day free)
```

**Option 2: Traditional Backend**
```
Node.js/Express + PostgreSQL on Railway
- $5/month for hobby tier
- Full SQL capabilities
- Better for complex queries
- Easier analytics
```

**Option 3: Managed Game Backend**
```
PlayFab (Microsoft) or GameSparks
- Purpose-built for games
- Built-in leaderboards
- Authentication included
- More expensive at scale
```

### Godot HTTP Implementation

```gdscript
# autoload/backend_api.gd
extends Node

const API_BASE = "https://api.pdoom.game/v1"
var http_request: HTTPRequest

func _ready():
    http_request = HTTPRequest.new()
    add_child(http_request)
    http_request.request_completed.connect(_on_request_completed)

func submit_score(score_entry: Dictionary) -> void:
    var json = JSON.stringify(score_entry)
    var headers = ["Content-Type: application/json"]
    http_request.request(API_BASE + "/scores", headers, HTTPClient.METHOD_POST, json)

func fetch_leaderboard(seed: String, callback: Callable) -> void:
    # Implementation with callback
    pass
```

---

## Migration Considerations

### Backward Compatibility
- Keep local JSON storage working
- Backend is enhancement, not requirement
- Graceful degradation if backend unavailable

### Data Migration
- Import existing local scores on first connection
- Deduplicate by entry_uuid
- Preserve historical data

### Privacy
- Opt-in for cloud submission
- Anonymous options
- GDPR compliance for EU players

---

## Timeline Estimate

| Phase | Description | Effort | Dependencies |
|-------|-------------|--------|--------------|
| 0 | Foundation | 2-4 hrs | None |
| 1 | Semi-Automated Sync | 1-2 days | Phase 0 |
| 2 | REST Backend | 3-5 days | Phase 0 |
| 3 | Authentication | 2-4 days | Phase 2 |
| 4 | Steam Integration | 1-2 weeks | Steam account |
| 5 | Anti-Cheat | 3-7 days | Phase 2-3 |

**Critical Path to Launch**:
- Minimum: Phase 0 + Phase 1 (semi-automated)
- Recommended: Phase 0 + Phase 2 + Phase 3a (device ID)
- Full: All phases including Steam

---

## Decision Points

### Immediate Decisions Needed

1. **Hosting platform**: Cloudflare vs Railway vs other?
2. **Phase 1 approach**: GitHub CLI vs Git hooks vs skip to Phase 2?
3. **Auth strategy**: Device ID first vs Steam first?
4. **Budget**: What's acceptable monthly cost?

### Future Decisions

1. **Steam vs itch.io vs both**: Distribution platform affects auth
2. **Cross-platform**: Web browser play in future?
3. **Competitive features**: Tournaments, seasons, rankings?

---

## Related Documentation

- [LEADERBOARD_WEBSITE_INTEGRATION.md](./LEADERBOARD_WEBSITE_INTEGRATION.md) - Export workflow
- [pdoom1-website: leaderboard-integration-spec.md](https://github.com/PipFoweraker/pdoom1-website/blob/main/docs/03-integrations/leaderboard-integration-spec.md) - Website integration
- [pdoom-data: DATA_ARCHITECTURE.md](https://github.com/PipFoweraker/pdoom-data/blob/main/DATA_ARCHITECTURE.md) - Data separation principles

---

## Next Steps

1. **Review this plan** and confirm phase priorities
2. **Decide on Phase 1 vs jump to Phase 2**
3. **Choose hosting platform** for backend
4. **Create issues** for each phase in GitHub

---

**Document Status**: Draft - Awaiting review
**Last Updated**: 2025-11-19
