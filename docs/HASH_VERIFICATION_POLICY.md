# Hash Verification Policy - Timestamp Priority System

## Core Principle

**Duplicate hashes are allowed** - Multiple players can submit the same verification hash if they:
- Use the same seed
- Make identical decisions
- Experience identical RNG outcomes (deterministic)

This is **legitimate** and actually proves a strategy is reproducible.

## Timestamp Priority System

### Rule: First Submission Wins

When multiple players submit identical verification hashes:

1. **First submission** (earliest `submitted_at` timestamp) gets **full credit**
2. **Later submissions** are accepted but **flagged as duplicate**
3. Leaderboard shows **first player to discover** that hash/strategy

### Database Schema Changes

```sql
-- Add hash tracking table
CREATE TABLE IF NOT EXISTS verification_hashes (
    hash_id SERIAL PRIMARY KEY,
    verification_hash TEXT UNIQUE NOT NULL,
    first_submission_id UUID REFERENCES game_sessions(session_id),
    first_submitted_by UUID REFERENCES users(user_id),
    first_submitted_at TIMESTAMP NOT NULL,
    duplicate_count INTEGER DEFAULT 0,
    seed TEXT NOT NULL,

    INDEX idx_verification_hash (verification_hash),
    INDEX idx_seed (seed)
);

-- Track duplicate submissions
CREATE TABLE IF NOT EXISTS hash_duplicates (
    duplicate_id SERIAL PRIMARY KEY,
    hash_id INTEGER REFERENCES verification_hashes(hash_id),
    session_id UUID REFERENCES game_sessions(session_id),
    user_id UUID REFERENCES users(user_id),
    submitted_at TIMESTAMP NOT NULL,
    time_delta_seconds INTEGER,  -- Seconds after first submission

    INDEX idx_hash_id (hash_id),
    INDEX idx_user_id (user_id)
);
```

### Submission Flow

```python
def _handle_score_submission(self, user_data: Dict):
    """Enhanced score submission with hash tracking."""

    # ... existing validation ...

    user_id = user_data['sub']
    verification_hash = score_data['verification_hash']
    seed = score_data['seed']
    submitted_at = datetime.utcnow()

    # Check if hash already exists
    hash_check_query = """
        SELECT
            hash_id,
            first_submitted_by,
            first_submitted_at,
            duplicate_count
        FROM verification_hashes
        WHERE verification_hash = %s
    """

    hash_result = self.db_manager.execute_query(
        hash_check_query,
        (verification_hash,)
    )

    is_first_submission = (hash_result is None or len(hash_result) == 0)

    # Create game session (always)
    session_id = self._create_game_session(user_id, score_data)

    if is_first_submission:
        # FIRST TIME this hash has been seen

        # Record as original discoverer
        insert_hash_query = """
            INSERT INTO verification_hashes (
                verification_hash,
                first_submission_id,
                first_submitted_by,
                first_submitted_at,
                duplicate_count,
                seed
            )
            VALUES (%s, %s, %s, %s, 0, %s)
            RETURNING hash_id
        """

        hash_record = self.db_manager.execute_insert(
            insert_hash_query,
            (verification_hash, session_id, user_id, submitted_at, seed)
        )

        # Create leaderboard entry (marked as original)
        leaderboard_query = """
            INSERT INTO leaderboard_entries (
                session_id, user_id, seed, score,
                verified, is_original_hash
            )
            VALUES (%s, %s, %s, %s, TRUE, TRUE)
            RETURNING entry_id
        """

        leaderboard_result = self.db_manager.execute_insert(
            leaderboard_query,
            (session_id, user_id, seed, score_data['score'])
        )

        response = {
            "status": "success",
            "data": {
                "session_id": session_id,
                "entry_id": str(leaderboard_result['entry_id']),
                "rank": self._calculate_rank(seed, score_data['score']),
                "score": score_data['score'],
                "hash_status": "original",
                "message": "First player to achieve this strategy!"
            }
        }

    else:
        # DUPLICATE HASH - someone already submitted this

        hash_record = hash_result[0]
        first_player = hash_record['first_submitted_by']
        first_timestamp = hash_record['first_submitted_at']

        # Check if this is the SAME player resubmitting
        if str(first_player) == user_id:
            # Same player submitting again (e.g., replay for practice)
            # Accept but don't add to leaderboard again

            response = {
                "status": "accepted",
                "data": {
                    "session_id": session_id,
                    "score": score_data['score'],
                    "hash_status": "self_duplicate",
                    "message": "You already submitted this strategy",
                    "original_submission": first_timestamp.isoformat()
                }
            }

            # Don't create leaderboard entry (already have one)

        else:
            # DIFFERENT player found same strategy

            time_delta = int((submitted_at - first_timestamp).total_seconds())

            # Record duplicate
            duplicate_query = """
                INSERT INTO hash_duplicates (
                    hash_id, session_id, user_id,
                    submitted_at, time_delta_seconds
                )
                VALUES (%s, %s, %s, %s, %s)
            """

            self.db_manager.execute_query(
                duplicate_query,
                (hash_record['hash_id'], session_id, user_id, submitted_at, time_delta),
                fetch=False
            )

            # Increment duplicate count
            update_count_query = """
                UPDATE verification_hashes
                SET duplicate_count = duplicate_count + 1
                WHERE hash_id = %s
            """

            self.db_manager.execute_query(
                update_count_query,
                (hash_record['hash_id'],),
                fetch=False
            )

            # Create leaderboard entry BUT mark as duplicate
            leaderboard_query = """
                INSERT INTO leaderboard_entries (
                    session_id, user_id, seed, score,
                    verified, is_original_hash, is_duplicate_hash
                )
                VALUES (%s, %s, %s, %s, TRUE, FALSE, TRUE)
                RETURNING entry_id
            """

            leaderboard_result = self.db_manager.execute_insert(
                leaderboard_query,
                (session_id, user_id, seed, score_data['score'])
            )

            # Format time delta nicely
            if time_delta < 60:
                delta_str = f"{time_delta} seconds"
            elif time_delta < 3600:
                delta_str = f"{time_delta // 60} minutes"
            elif time_delta < 86400:
                delta_str = f"{time_delta // 3600} hours"
            else:
                delta_str = f"{time_delta // 86400} days"

            response = {
                "status": "success",
                "data": {
                    "session_id": session_id,
                    "entry_id": str(leaderboard_result['entry_id']),
                    "rank": self._calculate_rank(seed, score_data['score']),
                    "score": score_data['score'],
                    "hash_status": "duplicate",
                    "message": f"Strategy already discovered {delta_str} ago by another player",
                    "duplicate_count": hash_record['duplicate_count'] + 1,
                    "first_discovered_by": "Anonymous",  # Privacy - don't reveal who
                    "first_discovered_at": first_timestamp.isoformat()
                }
            }

    self._send_json_response(200, response)
```

## Leaderboard Display

### Main Leaderboard (Default) - **ORIGINALS ONLY**

Filter: `WHERE is_original_hash = TRUE`

Shows only **first discovery** of each unique strategy:

```
Rank | Player      | Score  | Duplicates
-----|-------------|--------|------------
1    | Alice       | 95,000 | 12 others ⬆ Click to view
2    | Bob         | 92,000 | 5 others  ⬆ Click to view
3    | Dana        | 90,000 | 2 others  ⬆ Click to view
```

**Saves screen real estate** by only showing unique strategies.

### Score Detail View (Click to Expand)

When clicking on a score, show duplicates:

```
Strategy: abc123def456... (verification hash)
First discovered by: Alice on 2024-11-20 14:32 UTC
Score: 95,000

Duplicates (12):
- Bob (3 hours later)
- Charlie (5 hours later)
- [10 more...]
```

### Alternative: "All Submissions" View

Optional filter to show **every** submission including duplicates:

```
Rank | Player      | Score  | Status
-----|-------------|--------|------------------
1    | Alice       | 95,000 | ⭐ Original
2    | Bob         | 92,000 | ⭐ Original
3    | Charlie     | 95,000 | REPEAT Duplicate
4    | Dana        | 90,000 | ⭐ Original
```

## Why This Design?

### Advantages

SUCCESS **Rewards innovation**: First player to find strategy gets credit
SUCCESS **Allows sharing**: Players can share strategies without "stealing" credit
SUCCESS **Prevents accidental rejections**: Legitimate duplicate play isn't penalized
SUCCESS **Encourages community**: "X others found this strategy" shows popularity
SUCCESS **Speedrun-friendly**: Like speedrunning, first to discover route gets recognition
SUCCESS **Educational**: Duplicate count shows which strategies are common vs rare

### Use Cases

**Use Case 1: Strategy Guide**
- Player publishes "optimal seed quantum-2024 strategy"
- Guide followers get duplicate hash
- Original discoverer still credited as first
- Duplicates prove guide works

**Use Case 2: Convergent Play**
- Two skilled players independently find optimal strategy
- First to submit gets "original" badge
- Second player sees "discovered X hours ago"
- Both scores count for leaderboard

**Use Case 3: Practice/Replay (Self-Duplicates)**
- Player accidentally clicks "Submit" on same game multiple times
- OR player replays same seed with identical strategy
- First submission counts for leaderboard
- Later self-submissions logged but ignored
- Player sees "You already submitted this strategy on [date]"
- Hash prevents accidental double-submissions
- Not flagged as suspicious (same player, same hash = practice/accident)

**Use Case 4: Suspicious Activity (Rapid Duplicates)**
- **Threshold**: 10+ duplicate submissions of same hash within 1 hour
- Server flags: "Rapid duplicate activity detected"
- Admin dashboard shows: hash, submission times, players involved
- Possible explanations:
  - Bot farm testing same strategy
  - Shared optimal strategy from guide/video
  - Coordinated testing by community
  - Legitimate convergent discovery (unlikely at this speed)
- **Action**: Flag for review, don't auto-ban (could be legitimate)
- **Future**: May need to encourage/manage bots (speedrun TAS culture)
- **Philosophy**: Observe first, ban later if needed

## Privacy Considerations

### What We Show

SUCCESS "Strategy discovered X hours/days ago"
SUCCESS "Y other players found this strategy"
SUCCESS Your own previous submissions

### What We DON'T Show

ERROR Identity of first discoverer (unless they opt-in to "Featured Discoveries")
ERROR Identities of duplicate submitters
ERROR Specific gameplay details from hash

### Hall of Fame - Pseudonymous Attribution

Players can **opt-in** to having their discoveries attributed using their chosen pseudonym:

```sql
-- Add to users table
ALTER TABLE users ADD COLUMN display_discoveries BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN verified_external_account TEXT;  -- Future: Steam/Forum/etc
```

**Attribution modes**:

1. **Anonymous (default)**: "First discovered **3 days ago**"
2. **Pseudonym opt-in**: "First discovered by **Alice** on 2024-11-20"
3. **Future - Verified account**: "First discovered by **Alice** 🔗 (Steam)"

**Name squatting prevention** (future):
- Pseudonyms are first-come-first-served
- Can link to Steam/Forum account for verification badge
- Pseudonym != Steam name (privacy preserved)
- If name squatting becomes issue: require account linking OR character limits
- Privacy-respecting solution TBD based on community feedback

**Philosophy**:
- Default to privacy (anonymous)
- Allow recognition (pseudonym)
- Support verification (account linking) without requiring real identity

## Statistical Analysis

### Interesting Metrics

```sql
-- Most reproduced strategies (popular/obvious)
SELECT
    vh.seed,
    vh.verification_hash,
    vh.duplicate_count,
    u.pseudonym as discoverer
FROM verification_hashes vh
JOIN users u ON vh.first_submitted_by = u.user_id
ORDER BY vh.duplicate_count DESC
LIMIT 10;

-- Rarest strategies (creative/difficult)
SELECT seed, verification_hash, duplicate_count
FROM verification_hashes
WHERE duplicate_count = 0
ORDER BY first_submitted_at DESC;

-- Average time to duplicate (how fast strategies spread)
SELECT
    AVG(time_delta_seconds) as avg_seconds,
    AVG(time_delta_seconds) / 3600.0 as avg_hours
FROM hash_duplicates;
```

## Migration for Existing Data

```sql
-- Backfill verification_hashes table from existing leaderboard_entries
INSERT INTO verification_hashes (
    verification_hash,
    first_submission_id,
    first_submitted_by,
    first_submitted_at,
    duplicate_count,
    seed
)
SELECT DISTINCT ON (gs.checksum)
    gs.checksum as verification_hash,
    gs.session_id as first_submission_id,
    gs.user_id as first_submitted_by,
    le.submitted_at as first_submitted_at,
    0 as duplicate_count,
    le.seed
FROM game_sessions gs
JOIN leaderboard_entries le ON gs.session_id = le.session_id
WHERE gs.checksum IS NOT NULL
ORDER BY gs.checksum, le.submitted_at ASC;

-- Find and mark duplicates
UPDATE leaderboard_entries le
SET is_duplicate_hash = TRUE,
    is_original_hash = FALSE
WHERE EXISTS (
    SELECT 1 FROM verification_hashes vh
    JOIN game_sessions gs ON le.session_id = gs.session_id
    WHERE vh.verification_hash = gs.checksum
    AND vh.first_submission_id != le.session_id
);
```

## Summary

**Timestamp priority system**:
- SUCCESS Accepts all valid submissions
- ⭐ Credits first discoverer
- REPEAT Tracks duplicates transparently
- METRICS Enables rich analytics
- ACHIEVEMENT Rewards innovation while allowing shared strategies
- 🛡 Maintains privacy by default

This is the **best of both worlds**: strict verification (hash must be valid) + flexible credit (duplicates allowed, first wins).

Ready to implement?
