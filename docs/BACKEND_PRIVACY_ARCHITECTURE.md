# PDoom Backend Architecture - Privacy-First Design

## Overview

Self-hosted backend on DreamCompute for global leaderboards that:
- Prioritizes player privacy and data ownership
- Works for standalone EXE downloads
- Seamlessly integrates Steam later without architecture changes
- Minimizes security attack surface

## Technology Stack

### Backend Server (DreamCompute)
```
- Python 3.11+ with FastAPI (lightweight, async, easy to secure)
- SQLite database (simple, no external DB needed)
- HTTPS only (Let's Encrypt cert)
- Rate limiting via slowapi
- CORS properly configured
```

**Why FastAPI?**
- Built-in request validation (prevents injection attacks)
- Automatic OpenAPI docs for testing
- Async support for better performance
- Easy to deploy with uvicorn/gunicorn
- Strong typing reduces bugs

### Database Schema (Privacy-Minimal)

```sql
-- Players table (anonymous)
CREATE TABLE players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT UNIQUE,          -- UUID generated client-side
    steam_id TEXT UNIQUE,            -- NULL for non-Steam players
    display_name TEXT,               -- Player chosen, can be "Anonymous"
    opted_in BOOLEAN DEFAULT FALSE,  -- Explicit consent
    created_at TIMESTAMP,
    last_seen TIMESTAMP
);

-- Scores table
CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
    seed TEXT NOT NULL,
    score INTEGER NOT NULL,
    game_duration INTEGER,           -- seconds
    game_version TEXT,               -- e.g. "v0.10.1"
    submitted_at TIMESTAMP,

    -- Anti-cheat metadata (NOT gameplay tracking)
    state_hash TEXT,                 -- Hash of final game state

    INDEX idx_seed_score (seed, score DESC),
    INDEX idx_player_scores (player_id, submitted_at DESC)
);

-- Privacy: NO IP logging, NO session tracking, NO analytics
```

### API Endpoints

```
POST   /api/v1/scores              Submit score (requires opt-in)
GET    /api/v1/leaderboard/{seed}  Get top scores for seed
GET    /api/v1/player/stats        Get personal stats (requires auth)
POST   /api/v1/player/opt-in       Opt into leaderboards
POST   /api/v1/player/opt-out      Opt out + delete all data
DELETE /api/v1/player/delete       Delete all player data (GDPR)
```

## Privacy Controls

### 1. Opt-In Flow (Client-Side)

```gdscript
# godot/autoload/privacy_manager.gd
extends Node

var opted_in: bool = false
var device_id: String = ""

func _ready():
    load_privacy_settings()

func load_privacy_settings():
    var config = ConfigFile.new()
    if config.load("user://privacy.cfg") == OK:
        opted_in = config.get_value("privacy", "leaderboard_opt_in", false)
        device_id = config.get_value("privacy", "device_id", "")

    if device_id == "":
        device_id = _generate_device_id()
        save_privacy_settings()

func _generate_device_id() -> String:
    var uuid = OS.get_unique_id()  # Godot built-in UUID
    return uuid

func opt_in(display_name: String):
    opted_in = true
    # Call backend API to register
    await BackendAPI.opt_in_player(device_id, display_name)
    save_privacy_settings()

func opt_out():
    opted_in = false
    # Call backend API to delete all data
    await BackendAPI.delete_player_data(device_id)
    save_privacy_settings()
```

### 2. Backend Opt-In Verification

```python
# backend/api/scores.py
from fastapi import HTTPException

@app.post("/api/v1/scores")
async def submit_score(score_data: ScoreSubmission):
    # Verify player has opted in
    player = db.get_player_by_device_id(score_data.device_id)

    if not player or not player.opted_in:
        raise HTTPException(
            status_code=403,
            detail="Player has not opted into leaderboards. Please opt-in first."
        )

    # Validate score data
    if not validate_score(score_data):
        raise HTTPException(status_code=400, detail="Invalid score data")

    # Rate limiting: max 10 scores per hour per device
    if exceeded_rate_limit(player.id):
        raise HTTPException(status_code=429, detail="Too many submissions")

    # Insert score
    db.insert_score(player.id, score_data)
    return {"status": "success", "rank": calculate_rank(score_data)}
```

### 3. GDPR Compliance (Right to Erasure)

```python
@app.delete("/api/v1/player/delete")
async def delete_player_data(device_id: str):
    """Permanently delete all player data (GDPR Article 17)"""
    player = db.get_player_by_device_id(device_id)
    if not player:
        return {"status": "no_data"}

    # CASCADE delete removes all scores too
    db.delete_player(player.id)

    return {"status": "deleted", "message": "All data permanently removed"}
```

## Security Measures

### 1. HTTPS Only (Let's Encrypt)
```bash
# On DreamCompute server
sudo certbot --nginx -d leaderboard.pdoom.com
```

### 2. Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/scores")
@limiter.limit("10/hour")  # Max 10 score submissions per hour per IP
async def submit_score(...):
    pass
```

### 3. Input Validation
```python
from pydantic import BaseModel, validator

class ScoreSubmission(BaseModel):
    device_id: str
    seed: str
    score: int
    game_duration: int
    game_version: str

    @validator('score')
    def score_must_be_reasonable(cls, v):
        if v < 0 or v > 1000000:  # Adjust max based on game
            raise ValueError('Score out of valid range')
        return v

    @validator('seed')
    def seed_must_be_valid_format(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid seed format')
        return v
```

### 4. Basic Anti-Cheat (State Hash)

```gdscript
# godot/scripts/game_state.gd
func generate_state_hash() -> String:
    """Generate hash of final game state for verification"""
    var state_data = {
        "money": money,
        "compute": compute,
        "staff": staff_count,
        "papers": papers_published,
        "seed": current_seed,
        "version": game_version
    }

    var json = JSON.stringify(state_data)
    return json.sha256_text()  # Godot built-in SHA256
```

Backend verifies this hash can't be reused (store in DB, reject duplicates).

## Steam Integration (Future-Proof)

### Current Design Supports Both

```python
# backend/models.py
class Player:
    device_id: Optional[str]  # For standalone players
    steam_id: Optional[str]   # For Steam players
    auth_type: str            # "device" or "steam"
```

### Authentication Logic

```python
async def get_or_create_player(auth_data: AuthData):
    if auth_data.steam_id:
        # Steam player - verify Steam token
        if not verify_steam_token(auth_data.steam_token):
            raise HTTPException(401, "Invalid Steam authentication")

        player = db.get_player_by_steam_id(auth_data.steam_id)
        if not player:
            player = db.create_player(steam_id=auth_data.steam_id)
    else:
        # Standalone player - use device ID
        player = db.get_player_by_device_id(auth_data.device_id)
        if not player:
            raise HTTPException(403, "Player not opted in")

    return player
```

### When Steam Launches

1. Add Steam authentication endpoint
2. Allow linking device_id to steam_id (migrate existing players)
3. Dual-post scores: your backend + Steam leaderboards
4. Players choose: "PDoom Leaderboard" or "Steam Leaderboard" or both

## Deployment to DreamCompute

### 1. Server Setup

```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip nginx certbot python3-certbot-nginx

# Clone backend repo
git clone https://github.com/PipFoweraker/pdoom-backend.git
cd pdoom-backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Backend Requirements

```
# backend/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
slowapi==0.1.9      # Rate limiting
python-dotenv==1.0.0
httpx==0.25.1       # For Steam API verification (future)
```

### 3. Systemd Service

```ini
# /etc/systemd/system/pdoom-backend.service
[Unit]
Description=PDoom Leaderboard API
After=network.target

[Service]
User=pdoom
WorkingDirectory=/home/pdoom/pdoom-backend
Environment="PATH=/home/pdoom/pdoom-backend/venv/bin"
ExecStart=/home/pdoom/pdoom-backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/pdoom-leaderboard
server {
    listen 80;
    server_name leaderboard.pdoom.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. HTTPS with Let's Encrypt

```bash
sudo certbot --nginx -d leaderboard.pdoom.com
sudo systemctl enable certbot.timer  # Auto-renewal
```

## Privacy Policy (Required)

Create `docs/PRIVACY_POLICY.md`:

```markdown
# PDoom Privacy Policy

## Data Collection (Opt-In Only)

PDoom collects NO data by default. If you choose to participate in global
leaderboards, we collect:

- Your chosen display name (can be "Anonymous")
- Game scores, seeds, and completion times
- A device identifier (randomly generated on your device)

We DO NOT collect:
- IP addresses (not logged)
- Gameplay sessions or telemetry
- Personal information
- Location data

## Your Rights

- View your data: See all your scores in-game
- Delete your data: Opt-out deletes ALL your data permanently
- Change display name: Update anytime in settings
- Opt-out: One click removes you from leaderboards

## Data Storage

All data is stored on our own servers (DreamCompute). We do not use
third-party analytics or tracking services.

## Contact

Questions about your data: privacy@pdoom.com
```

## Implementation Checklist

### Phase 1: Backend Foundation (Week 1)

- [ ] Set up DreamCompute server with Python 3.11
- [ ] Create FastAPI backend skeleton
- [ ] Implement SQLite database schema
- [ ] Add privacy-first API endpoints (opt-in, submit, query)
- [ ] Deploy with Nginx + Let's Encrypt HTTPS
- [ ] Write privacy policy

### Phase 2: Godot Integration (Week 2)

- [ ] Create `BackendAPI` autoload singleton
- [ ] Create `PrivacyManager` autoload singleton
- [ ] Add opt-in UI to settings menu
- [ ] Implement score submission with HTTPRequest
- [ ] Add "View My Stats" screen
- [ ] Handle offline gracefully (queue scores, retry later)

### Phase 3: Security Hardening (Week 3)

- [ ] Add rate limiting (slowapi)
- [ ] Implement state hash validation
- [ ] Add duplicate score detection
- [ ] Set up backup automation (daily SQLite backups)
- [ ] Add monitoring (simple healthcheck endpoint)

### Phase 4: Steam Prep (Future)

- [ ] Add Steam authentication endpoint
- [ ] Implement device_id  ->  steam_id linking
- [ ] Dual-post to PDoom + Steam leaderboards
- [ ] Add Steam-specific privacy settings

## Cost Estimate

**DreamCompute Server:**
- ~$10-20/month for small VPS
- SQLite = no database hosting costs
- Let's Encrypt = free SSL
- **Total: ~$15/month** for global leaderboards

**Bandwidth:**
- ~1KB per score submission
- 10,000 players x 10 games each = 100KB data
- Negligible bandwidth costs

## Security Considerations

**What we're protecting against:**
1. SUCCESS SQL injection  ->  Pydantic validation + SQLAlchemy ORM
2. SUCCESS DDoS  ->  Rate limiting (10 scores/hour per IP)
3. SUCCESS Privacy leaks  ->  No IP logging, minimal data collection
4. SUCCESS Score cheating  ->  State hash validation, statistical analysis
5. WARNING Advanced exploits  ->  Keep FastAPI/Python updated

**What we're NOT building (yet):**
- Advanced anti-cheat (memory scanning, etc.)
- Replay verification system
- Machine learning anomaly detection

For a small indie game, the above security is sufficient. Can add more later if needed.

## Next Steps

1. **Review this architecture** - Does it meet your privacy/ownership goals?
2. **Set up DreamCompute server** - I can help with deployment scripts
3. **Build backend skeleton** - FastAPI + SQLite foundation
4. **Test locally** - Run backend on localhost, connect Godot client
5. **Deploy to production** - DreamCompute + domain setup
6. **Add opt-in UI to game** - Settings menu integration

Estimated time to working global leaderboards: **2-3 weeks** (working part-time)

Would you like me to start building the backend code, or do you want to adjust the architecture first?
