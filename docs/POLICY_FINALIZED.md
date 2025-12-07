# Hash Verification Policy - Finalized Decisions

**Date**: November 20, 2024
**Status**: SUCCESS Approved for implementation

---

## Core Decisions

### 1. Leaderboard Display SUCCESS

**Main leaderboard shows ORIGINALS ONLY**

```
Rank | Player      | Score  | Duplicates
-----|-------------|--------|------------
1    | Alice       | 95,000 | 12 others ⬆ Click to view
2    | Bob         | 92,000 | 5 others  ⬆ Click to view
3    | Dana        | 90,000 | 2 others  ⬆ Click to view
```

**Why**: Saves screen real estate, emphasizes unique strategies

**Details view** (click score):
- Shows verification hash
- Shows all duplicates with timestamps
- Shows first discoverer (if opted in)

**Alternative view**: Toggle to show ALL submissions (originals + duplicates)

### 2. Hall of Fame Attribution SUCCESS

**Three-tier system**:

1. **Anonymous (default)**: "First discovered 3 days ago"
2. **Pseudonym opt-in**: "First discovered by **Alice** on 2024-11-20"
3. **Future - Verified account**: "First discovered by **Alice** 🔗 (Steam/Forum)"

**Database fields**:
```sql
ALTER TABLE users ADD COLUMN display_discoveries BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN verified_external_account TEXT;  -- Future
```

**Name squatting approach**:
- First-come-first-served for pseudonyms
- Can optionally link Steam/Forum for verification badge
- Pseudonym != real identity (privacy preserved)
- If squatting becomes issue: iterate based on community feedback
- TBD: character limits, account linking requirements, etc.

**Philosophy**: Privacy by default, recognition by choice, verification without doxxing

### 3. Rapid Duplicate Detection SUCCESS

**Threshold**: 10+ duplicates of same hash within 1 hour

**Action**:
- Flag for admin review (don't auto-ban)
- Log to admin dashboard: hash, times, players, seed
- Possible causes:
  - Bot farms
  - Popular strategy guide
  - Community coordinated testing
  - Speedrun TAS development

**Response**:
- Observe and monitor
- Don't assume malicious intent
- May need to **encourage** bots (TAS culture)
- Future: dedicated "TAS/Bot" leaderboard category?

**Database tracking**:
```sql
-- Flag in verification_hashes table
ALTER TABLE verification_hashes ADD COLUMN rapid_duplicate_flag BOOLEAN DEFAULT FALSE;
ALTER TABLE verification_hashes ADD COLUMN flag_reason TEXT;
ALTER TABLE verification_hashes ADD COLUMN flagged_at TIMESTAMP;
```

**Philosophy**: "Guilty until proven innocent" is wrong. Observe first, ban never (unless proven malicious).

### 4. Self-Duplicate Behavior SUCCESS

**Scenario**: Player submits same hash multiple times

**Causes**:
- Accidentally clicks "Submit" twice
- Replays same seed with identical strategy
- Testing/debugging

**Behavior**:
- First submission: Creates leaderboard entry
- Subsequent self-duplicates: Logged but ignored
- Response: "You already submitted this strategy on [date]"
- NOT flagged as suspicious (same player = practice/accident)
- Hash already contains game state, so no new information

**Implementation**:
```python
if str(first_player) == user_id:
    # Same player resubmitting
    return {
        "status": "accepted",
        "message": "You already submitted this strategy",
        "original_submission": first_timestamp.isoformat(),
        "leaderboard_entry": "unchanged"
    }
```

**Philosophy**: Hash is deterministic - same player + same actions = same hash. This is expected, not suspicious.

---

## Implementation Checklist

### Database Schema Changes

```sql
-- Hash tracking
CREATE TABLE verification_hashes (
    hash_id SERIAL PRIMARY KEY,
    verification_hash TEXT UNIQUE NOT NULL,
    first_submission_id UUID REFERENCES game_sessions(session_id),
    first_submitted_by UUID REFERENCES users(user_id),
    first_submitted_at TIMESTAMP NOT NULL,
    duplicate_count INTEGER DEFAULT 0,
    seed TEXT NOT NULL,

    -- Rapid duplicate detection
    rapid_duplicate_flag BOOLEAN DEFAULT FALSE,
    flag_reason TEXT,
    flagged_at TIMESTAMP,

    INDEX idx_verification_hash (verification_hash),
    INDEX idx_seed (seed),
    INDEX idx_flagged (rapid_duplicate_flag)
);

-- Duplicate tracking
CREATE TABLE hash_duplicates (
    duplicate_id SERIAL PRIMARY KEY,
    hash_id INTEGER REFERENCES verification_hashes(hash_id),
    session_id UUID REFERENCES game_sessions(session_id),
    user_id UUID REFERENCES users(user_id),
    submitted_at TIMESTAMP NOT NULL,
    time_delta_seconds INTEGER,
    is_self_duplicate BOOLEAN DEFAULT FALSE,

    INDEX idx_hash_id (hash_id),
    INDEX idx_user_id (user_id),
    INDEX idx_submitted_at (submitted_at)
);

-- User attribution preferences
ALTER TABLE users ADD COLUMN display_discoveries BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN verified_external_account TEXT;

-- Leaderboard entry flags
ALTER TABLE leaderboard_entries ADD COLUMN is_original_hash BOOLEAN DEFAULT FALSE;
ALTER TABLE leaderboard_entries ADD COLUMN is_duplicate_hash BOOLEAN DEFAULT FALSE;
```

### API Endpoints to Implement

1. **Score submission with hash tracking** SUCCESS (enhance existing)
   - `POST /api/scores/submit`
   - Check for existing hash
   - Timestamp priority logic
   - Self-duplicate detection
   - Rapid duplicate flagging

2. **Score detail view** (new)
   - `GET /api/scores/{entry_id}/details`
   - Returns: hash, duplicates, timestamps, discoverer

3. **User preference updates** (new)
   - `PATCH /api/users/profile`
   - Update `display_discoveries` boolean
   - Update `verified_external_account` (future)

4. **Admin dashboard** (future)
   - `GET /api/admin/flagged-hashes`
   - Returns: rapid duplicates, suspicious patterns

### Client-Side Changes

1. **VerificationTracker autoload** (new)
   - Initialize hash from seed
   - Update after every action/event/RNG
   - Provide final hash on game end

2. **Score submission integration** (modify existing)
   - Include `verification_hash` in submission
   - Handle response messages (original/duplicate/self-duplicate)

3. **Leaderboard UI** (enhance existing)
   - Show "X others found this" count
   - Click to expand: duplicate list
   - Toggle: Originals only / All submissions

4. **Settings menu** (add option)
   - Checkbox: "Display my pseudonym for discoveries"
   - Future: "Link Steam account"

---

## Testing Plan

### Week 1: Hash Generation

- [ ] Same seed + same actions = same hash (determinism)
- [ ] Different actions = different hash (sensitivity)
- [ ] RNG variations detected
- [ ] Float rounding doesn't break hashes
- [ ] Turn order matters (anti-reordering)

### Week 2: Server Logic

- [ ] First submission gets "original" flag
- [ ] Duplicate detection works
- [ ] Self-duplicate detection works
- [ ] Rapid duplicate flagging (10+ in 1 hour)
- [ ] Timestamp priority correct
- [ ] Plausibility checks catch impossible states
- [ ] Score recalculation matches game formula

### Week 3: End-to-End

- [ ] Game  ->  API  ->  Database flow
- [ ] Leaderboard displays correctly
- [ ] Score detail view works
- [ ] User preferences save
- [ ] Multiple players, multiple seeds
- [ ] Concurrent submissions (race conditions)

### Week 4: Load & Security

- [ ] 100+ concurrent submissions
- [ ] Hash collision testing (should be impossible with SHA-256)
- [ ] SQL injection attempts (should be blocked by parameterization)
- [ ] Invalid hash format rejection
- [ ] Implausible state rejection

---

## Success Metrics

**Week 1**: Hash generation working, deterministic
**Week 2**: Server accepts and tracks hashes correctly
**Week 3**: End-to-end leaderboard flow working
**Week 4**: Production deployment, community launch

**Post-launch**:
- Verification success rate > 95%
- False positive rate < 1%
- Average submission latency < 500ms
- Zero data leaks (privacy maintained)
- Community feedback positive

---

## Blog/Reddit Talking Points

### The Hook
"We're launching global leaderboards with a twist: first to discover a strategy gets credit, but anyone can reproduce it for verification."

### The Innovation
- Cumulative hash verification (lightweight, fast, secure)
- Timestamp priority system (rewards innovation, allows sharing)
- Privacy-first (anonymous by default, opt-in attribution)

### The Benefits
- ACHIEVEMENT First discoverer gets recognition
- REPEAT Strategy sharing encouraged
- 🛡 Cheat-resistant (can't fake scores)
- METRICS See which strategies are popular
- 🎓 Educational (learn from duplicates)

### The Philosophy
"Think speedrun culture: first to find the route gets credit, but sharing makes everyone better."

### Community Impact
- Casual players: Fair competition, learn from others
- Competitive players: Innovation rewarded
- Strategy crafters: Publish guides without losing credit
- Bot developers: Welcomed (TAS culture), not banned

---

**Status**: SUCCESS Policy finalized, ready for implementation
**Next**: Implement VerificationTracker autoload in Godot
