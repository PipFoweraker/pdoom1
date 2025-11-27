# Leaderboard Backend - GitHub Issues

These issues form a sequential dependency chain. When all are completed, P(Doom) will have a robust global leaderboard accessible via Steam, web, and direct API (for AI agents).

---

## Issue 1: Godot Leaderboard Export Function

**Title**: `feat: Add leaderboard export to Godot version`

**Labels**: `enhancement`, `leaderboard`, `phase-0`

**Description**:
Add export functionality to Godot's leaderboard system matching the Python version's `export_leaderboards.py`.

**Tasks**:
- [ ] Create `scripts/tools/export_leaderboard.gd`
- [ ] Export to `web_export/` directory in website-compatible JSON format
- [ ] Match schema from `LEADERBOARD_WEBSITE_INTEGRATION.md`
- [ ] Add CLI invocation via `--export-leaderboard` flag
- [ ] Test export  ->  website workflow

**Acceptance Criteria**:
- Running export produces valid JSON files
- Files work when copied to `pdoom1-website/public/leaderboard/data/`
- Format matches existing website display code

**Dependencies**: None

**Effort**: 2-4 hours

---

## Issue 2: Backend API Design & Hosting Setup

**Title**: `feat: Design and deploy leaderboard REST API`

**Labels**: `enhancement`, `backend`, `infrastructure`, `phase-2`

**Description**:
Create the backend API service for real-time leaderboard operations.

**Tasks**:
- [ ] Finalize API schema (OpenAPI/Swagger spec)
- [ ] Choose hosting platform (Cloudflare Workers recommended)
- [ ] Implement endpoints:
  - `POST /api/v1/scores` - Submit score
  - `GET /api/v1/leaderboards/{seed}` - Get seed leaderboard
  - `GET /api/v1/leaderboards` - List all seeds
  - `GET /api/v1/stats` - Global statistics
- [ ] Set up data storage (KV for Cloudflare, or PostgreSQL)
- [ ] Implement rate limiting
- [ ] Deploy to production URL
- [ ] Document API for third-party use (AI agents)

**API Schema**:
```yaml
Score Submission:
  player_id: string (device UUID or Steam ID)
  lab_name: string
  score: integer
  seed: string
  final_doom: float
  final_money: integer
  game_version: string
  duration_seconds: float
  timestamp: ISO8601
```

**Acceptance Criteria**:
- API deployed and accessible at `https://api.pdoom.game/v1/` (or similar)
- Can submit score via curl and see it in response
- Rate limiting prevents abuse
- API documentation published

**Dependencies**: Issue #1 (for data format reference)

**Effort**: 3-5 days

---

## Issue 3: Godot Backend Integration

**Title**: `feat: Connect Godot game to leaderboard backend`

**Labels**: `enhancement`, `leaderboard`, `networking`, `phase-2`

**Description**:
Add HTTPRequest-based backend communication to Godot game.

**Tasks**:
- [ ] Create `autoload/backend_api.gd` singleton
- [ ] Implement score submission on game over
- [ ] Implement leaderboard fetching for display
- [ ] Add offline queue for failed submissions
- [ ] Graceful fallback to local storage
- [ ] User preference for cloud submission opt-in
- [ ] Retry logic with exponential backoff

**Code Structure**:
```gdscript
# autoload/backend_api.gd
signal score_submitted(success, rank)
signal leaderboard_fetched(entries)

func submit_score(score_entry: Dictionary) -> void
func fetch_leaderboard(seed: String) -> void
func is_online() -> bool
```

**Acceptance Criteria**:
- Scores appear on backend within seconds of game over
- Leaderboard screen shows live data from backend
- Game works normally when offline (uses local storage)
- Queued scores sync when connection restored

**Dependencies**: Issue #2 (API must exist)

**Effort**: 2-3 days

---

## Issue 4: Device ID Authentication

**Title**: `feat: Implement device-based player identification`

**Labels**: `enhancement`, `authentication`, `phase-3`

**Description**:
Generate and persist unique device IDs for player tracking across sessions.

**Tasks**:
- [ ] Generate UUID on first launch
- [ ] Store in user preferences (persistent across reinstalls if possible)
- [ ] Include device_id in all API requests
- [ ] Backend: register new devices automatically
- [ ] Backend: track player history by device_id
- [ ] Allow player to reset/regenerate ID (privacy)
- [ ] Handle device_id conflicts gracefully

**Acceptance Criteria**:
- Same device_id used across game sessions
- Backend can show player's score history
- Players can opt to reset their ID
- No PII collected (anonymous by default)

**Dependencies**: Issue #3 (needs backend integration)

**Effort**: 1-2 days

---

## Issue 5: Steam Authentication

**Title**: `feat: Integrate Steamworks SDK for authentication`

**Labels**: `enhancement`, `steam`, `authentication`, `phase-4`

**Description**:
Add GodotSteam plugin and implement Steam-based player authentication.

**Tasks**:
- [ ] Register on Steamworks, obtain App ID
- [ ] Integrate GodotSteam GDExtension
- [ ] Implement Steam initialization
- [ ] Get Steam ID for authenticated players
- [ ] Get Steam display name
- [ ] Generate auth ticket for backend verification
- [ ] Backend: verify Steam auth tickets via Web API
- [ ] Link Steam ID to existing device_id (optional)
- [ ] Fallback to device_id for non-Steam players

**Acceptance Criteria**:
- Steam overlay works in-game
- Player's Steam name appears on leaderboard
- Backend verifies player is legitimate Steam user
- Non-Steam builds still work with device_id

**Dependencies**: Issue #4, Steamworks developer account

**Effort**: 1 week

---

## Issue 6: Steam Achievements

**Title**: `feat: Implement Steam achievements`

**Labels**: `enhancement`, `steam`, `achievements`, `phase-4`

**Description**:
Define and implement Steam achievements for P(Doom).

**Tasks**:
- [ ] Design achievement list (15-30 achievements)
- [ ] Configure achievements in Steamworks
- [ ] Implement achievement triggers in game code
- [ ] Track achievement progress
- [ ] Handle offline achievement unlocks
- [ ] Test achievement unlocks

**Achievement Ideas**:
- First Game Completed
- Survive 50 Turns
- Survive 100 Turns
- Keep P(Doom) under 20%
- Publish 10 Research Papers
- Hire 50 Staff
- Win on Hard Difficulty
- Weekly League Top 10

**Acceptance Criteria**:
- Achievements unlock and appear in Steam overlay
- Progress tracked correctly
- Achievements sync when coming back online

**Dependencies**: Issue #5 (Steam SDK)

**Effort**: 2-3 days

---

## Issue 7: Anti-Cheat Score Validation

**Title**: `feat: Implement score validation and anti-cheat`

**Labels**: `enhancement`, `security`, `backend`, `phase-5`

**Description**:
Prevent cheating and validate submitted scores.

**Tasks**:
- [ ] Design game state hash algorithm
- [ ] Client: generate hash at game over
- [ ] Backend: validate hash matches expected
- [ ] Statistical anomaly detection
  - Score vs duration check
  - Impossible resource combinations
  - Suspicious patterns
- [ ] Rate limiting per player
- [ ] Flag suspicious scores for manual review
- [ ] Admin tools for score moderation
- [ ] (Optional) Replay recording for disputes

**Acceptance Criteria**:
- Modified game clients produce invalid hashes
- Statistically impossible scores flagged
- Admin can review and remove cheated scores
- Legitimate scores unaffected

**Dependencies**: Issue #4 (needs player identification)

**Effort**: 3-5 days

---

## Issue 8: Public API Documentation

**Title**: `docs: Publish leaderboard API for AI agents and third parties`

**Labels**: `documentation`, `api`, `accessibility`

**Description**:
Create public documentation for the leaderboard API so AI agents and third-party tools can interact with leaderboards.

**Tasks**:
- [ ] Write OpenAPI/Swagger specification
- [ ] Generate interactive API docs (Swagger UI or Redoc)
- [ ] Document authentication methods
- [ ] Provide example requests (curl, Python, JavaScript)
- [ ] Document rate limits and quotas
- [ ] Create "AI Agent Integration Guide"
- [ ] Host docs at `https://api.pdoom.game/docs`

**Example Use Cases**:
- AI agent plays game and submits scores
- Third-party leaderboard widgets
- Analytics and research tools
- Tournament management systems

**Acceptance Criteria**:
- API docs accessible at public URL
- Examples work when copy-pasted
- AI can successfully submit score using documented API

**Dependencies**: Issue #2 (API must be stable)

**Effort**: 1-2 days

---

## Issue 9: Website Live Leaderboard

**Title**: `feat: Connect website to live backend API`

**Labels**: `enhancement`, `website`, `frontend`

**Description**:
Update pdoom1-website to fetch leaderboards from backend API instead of static JSON.

**Tasks**:
- [ ] Replace static JSON fetching with API calls
- [ ] Add loading states
- [ ] Implement auto-refresh (every 60s or on focus)
- [ ] Cache responses for performance
- [ ] Show "Live" indicator when connected
- [ ] Graceful fallback to cached data
- [ ] Update seed selector to use API

**Acceptance Criteria**:
- Website shows scores within seconds of submission
- "Live" indicator visible
- Works on mobile
- Fast initial load (< 2s)

**Dependencies**: Issue #2 (API endpoint)

**Effort**: 1-2 days

---

## Issue 10: Steam Leaderboard Sync (Optional)

**Title**: `feat: Sync scores to Steam Leaderboards`

**Labels**: `enhancement`, `steam`, `optional`

**Description**:
Optionally sync scores to Steam's built-in leaderboard system for Steam-native features.

**Tasks**:
- [ ] Configure Steam leaderboards in Steamworks
- [ ] Submit scores to both backend and Steam
- [ ] Display Steam leaderboard in-game (optional)
- [ ] Handle Steam leaderboard limits (per seed or global?)

**Acceptance Criteria**:
- Scores appear in Steam leaderboards
- Steam friends can compare scores
- Steam leaderboard achievements possible

**Dependencies**: Issue #5 (Steam SDK), Issue #3 (backend)

**Effort**: 1-2 days

---

## Dependency Graph

```
Issue #1 (Export)
     v 
Issue #2 (API) ------------------ ->  Issue #8 (API Docs)
     v                                      v 
Issue #3 (Godot Integration) ---- ->  Issue #9 (Website Live)
     v 
Issue #4 (Device ID)
     v 
Issue #5 (Steam Auth) ----------- ->  Issue #10 (Steam Leaderboards)
     v 
Issue #6 (Achievements)

Issue #4 + #5  ->  Issue #7 (Anti-Cheat)
```

---

## Milestones

### Milestone: Alpha Leaderboard
**Issues**: #1, #2, #3, #4
**Outcome**: Working global leaderboard with device ID auth

### Milestone: Steam Ready
**Issues**: #5, #6, #10
**Outcome**: Full Steam integration with achievements

### Milestone: Production Hardened
**Issues**: #7, #8, #9
**Outcome**: Anti-cheat, public API, live website

---

## Creating These Issues

To create these issues in GitHub:

```bash
cd "g:/Documents/Organising Life/Code/pdoom1"

# Create issues using gh CLI
gh issue create --title "feat: Add leaderboard export to Godot version" \
  --body "$(cat docs/issues/leaderboard-backend-issues.md | sed -n '/## Issue 1/,/## Issue 2/p')" \
  --label "enhancement,leaderboard,phase-0"

# Or create them manually in GitHub UI using the content above
```

---

## Total Effort Estimate

| Phase | Issues | Effort |
|-------|--------|--------|
| Foundation | #1 | 2-4 hrs |
| Backend | #2, #3 | 5-8 days |
| Auth | #4 | 1-2 days |
| Steam | #5, #6, #10 | 1.5 weeks |
| Hardening | #7, #8, #9 | 5-8 days |

**Total**: ~4-5 weeks for complete implementation

**Minimum for launch**: Issues #1-4 (~1-2 weeks)
