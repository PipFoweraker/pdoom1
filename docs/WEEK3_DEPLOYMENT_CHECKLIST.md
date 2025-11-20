# Week 3 Deployment Checklist - Global Leaderboards Launch

**Goal**: Launch global leaderboards with verification in 7 days
**Date Started**: November 20, 2024
**Target Launch**: November 27, 2024

---

## Day 1: Verification Testing & Scoring Implementation

### Morning: Test Verification System ✅

**Run Quick Test**:
```bash
# Open Godot
# Load scene: godot/tests/manual/test_verification_quick.tscn
# Press F6 to run

# Expected output:
# ✅ PASS: Hashes match! System is deterministic.
# ✅ PASS: Different actions produce different hash
```

**If Tests Pass**: ✅ System is working, proceed to scoring
**If Tests Fail**: 🔧 Debug RNG tracking, check for non-deterministic code

### Afternoon: Implement Scoring Formula

**1. Add to GameState or GameManager** (`godot/scripts/core/game_state.gd` or `godot/scripts/game_manager.gd`):

```gdscript
func calculate_final_score() -> int:
	"""
	Calculate final score from current game state.

	Formula:
	- Safety:    (100 - doom) * 1000
	- Research:  papers * 5000
	- Team:      researchers * 2000
	- Survival:  turn * 500
	- Financial: money * 0.1
	- Victory:   +50000 if doom < 20%
	"""
	var score = 0

	# Safety Achievement (40-50% of score)
	score += (100 - doom) * 1000

	# Research Output (20-30% of score)
	score += papers * 5000

	# Team Excellence (10-15% of score)
	score += researchers.size() * 2000

	# Survival Duration (10-15% of score)
	score += turn * 500

	# Financial Success (5-10% of score)
	score += money * 0.1

	# Victory Bonus
	if doom < 20.0:
		score += 50000

	return int(score)
```

**2. Update Game Over Flow** (`godot/scripts/game_controller.gd` or similar):

```gdscript
func handle_game_over():
	# Calculate final score (NEW)
	var final_score = game_state.calculate_final_score()

	# Create score entry with new score
	var score_entry = LeaderboardClass.ScoreEntry.new(
		final_score,  # Use calculated score instead of turns
		lab_name,
		game_state["turn"],
		"v0.10.2",
		duration
	)

	# ... rest of existing code
```

**3. Update Python to Match** (`pdoom1-website/scripts/verification_logic.py`):

```python
@staticmethod
def calculate_score(final_state: Dict[str, Any]) -> int:
	"""CRITICAL: Must match Godot exactly!"""
	doom = final_state.get('doom', 0)
	papers = final_state.get('papers', 0)
	researchers = final_state.get('researchers', 0)
	turn = final_state.get('turn', 0)
	money = final_state.get('money', 0)

	score = 0
	score += (100 - doom) * 1000
	score += papers * 5000
	score += researchers * 2000
	score += turn * 500
	score += money * 0.1

	if doom < 20.0:
		score += 50000

	return int(score)
```

**4. Test Scoring Consistency**:

Play a game, note the final state, calculate score manually:
```python
# Example:
state = {
	"doom": 45.5, "papers": 5, "researchers": 6,
	"turn": 50, "money": 125000
}

# Godot should show: X points
# Python should calculate: X points (same!)
```

**Checklist**:
- [ ] Scoring function added to Godot
- [ ] Game over flow updated to use new score
- [ ] Python formula updated to match
- [ ] Manual test: Godot and Python produce same score
- [ ] Commit changes to git

---

## Day 2: Database Migration & API Integration

### Morning: Database Setup

**1. Backup Production Database** (if applicable):
```bash
pg_dump $DATABASE_URL > backup_before_verification_$(date +%Y%m%d).sql
```

**2. Run Migration**:
```bash
cd pdoom1-website/scripts

# Test migration on local/staging first
psql $STAGING_DATABASE_URL -f db_migrations/003_add_verification_hashes.sql

# Verify tables created
psql $STAGING_DATABASE_URL -c "
SELECT table_name FROM information_schema.tables
WHERE table_name IN ('verification_hashes', 'hash_duplicates');
"

# Expected output:
# verification_hashes
# hash_duplicates
```

**3. Run on Production** (if ready):
```bash
psql $DATABASE_URL -f db_migrations/003_add_verification_hashes.sql
```

### Afternoon: API Server Integration

**1. Update api-server-v2.py**:

Add imports at top:
```python
from verification_logic import (
	HashVerificationHandler,
	PlausibilityChecker,
	ScoreCalculator,
	VerificationError
)
```

Replace `_handle_score_submission()`:
```python
def _handle_score_submission(self, user_data: Dict):
	"""Handle score submission with cumulative hash verification."""
	try:
		content_length = int(self.headers.get('Content-Length', 0))
		if content_length == 0:
			self._send_error(400, "No data provided")
			return

		post_data = self.rfile.read(content_length)
		score_data = json.loads(post_data.decode('utf-8'))

		# Validate basic submission format
		if not self._validate_score_submission(score_data):
			self._send_error(400, "Invalid score submission")
			return

		user_id = user_data['sub']

		# Use verification handler
		verification_handler = HashVerificationHandler(self.db_manager)

		try:
			response = verification_handler.process_submission(user_id, score_data)

			self._send_json_response(200, {
				"status": response["status"],
				"data": response["data"],
				"message": response["data"].get("message", "Score submitted successfully"),
				"timestamp": datetime.now().isoformat() + "Z"
			})

		except VerificationError as e:
			self._send_error(400, f"Verification failed: {str(e)}")

	except json.JSONDecodeError:
		self._send_error(400, "Invalid JSON data")
	except Exception as e:
		print(f"Score submission error: {e}")
		import traceback
		traceback.print_exc()
		self._send_error(500, f"Score submission failed: {str(e)}")
```

Update `_validate_score_submission()`:
```python
def _validate_score_submission(self, score_data: Dict[str, Any]) -> bool:
	"""Validate score submission data."""
	required_fields = ['seed', 'score', 'verification_hash', 'timestamp', 'final_state']

	for field in required_fields:
		if field not in score_data:
			print(f"Missing required field: {field}")
			return False

	if not isinstance(score_data['score'], int) or score_data['score'] < 0:
		return False

	if len(score_data['verification_hash']) != 64:
		return False

	if not isinstance(score_data['final_state'], dict):
		return False

	return True
```

**Checklist**:
- [ ] Database migration run successfully
- [ ] Tables verified in database
- [ ] API server code updated
- [ ] verification_logic.py module available
- [ ] Server restarts without errors
- [ ] Commit changes to git

---

## Day 3: Manual Testing

### Test Cases

**Test 1: Submit Original Score**
```bash
# Register user
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"pseudonym": "TestPlayer1", "opt_in_leaderboard": true}'

# Login
TOKEN=$(curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"pseudonym": "TestPlayer1"}' | jq -r '.data.token')

# Submit score
curl -X POST http://localhost:8080/api/scores/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "seed": "test-seed-001",
    "score": 125000,
    "verification_hash": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
    "game_version": "0.10.2",
    "timestamp": 1732118400,
    "final_state": {
      "turn": 50,
      "money": 125000,
      "doom": 45.5,
      "papers": 5,
      "research": 120,
      "compute": 350,
      "researchers": 6
    },
    "duration_seconds": 1800
  }'

# Expected: "hash_status": "original"
```

**Test 2: Submit Duplicate (Different Player)**
```bash
# Create second player
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"pseudonym": "TestPlayer2", "opt_in_leaderboard": true}'

TOKEN2=$(curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"pseudonym": "TestPlayer2"}' | jq -r '.data.token')

# Submit SAME hash
curl -X POST http://localhost:8080/api/scores/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN2" \
  -d '{
    "seed": "test-seed-001",
    "score": 125000,
    "verification_hash": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
    ...
  }'

# Expected: "hash_status": "duplicate"
```

**Test 3: Invalid State (Plausibility Check)**
```bash
# Submit impossible doom
curl -X POST http://localhost:8080/api/scores/submit \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "final_state": {
      "doom": 150.0  # IMPOSSIBLE
    },
    ...
  }'

# Expected: 400 error "Implausible game state"
```

**Checklist**:
- [ ] Test 1 passes (original submission)
- [ ] Test 2 passes (duplicate detection)
- [ ] Test 3 passes (plausibility rejection)
- [ ] Leaderboard displays correctly
- [ ] Scores calculated correctly
- [ ] No errors in server logs

---

## Day 4: Game Integration Testing

### In-Game Flow

**1. Play Full Game**:
- Start new game
- Play through several turns
- Reach game over (win or lose)
- Check console output for hash

**2. Verify Hash Export**:
```
Expected console output:
[GameManager] Verification tracking enabled (debug mode: ON)
[VerificationTracker] Started tracking
  Seed: quantum-2024-11-20
  Version: 0.10.2
  Initial hash: 7a3f2e1b...
[VerificationTracker] Action: buy_compute → 9b2c4d5e...
[VerificationTracker] Turn 1 end → 3c5e7f9a...
...
[GameOverScreen] Game ended - Verification hash: 8a0b2c4d...
[GameOverScreen] Full verification data ready for submission
```

**3. Extract Verification Data**:

Check that `verification_data` contains:
```gdscript
{
	"verification_hash": "8a0b2c4d...",  # 64 characters
	"seed": "quantum-2024-11-20",
	"game_version": "0.10.2",
	"final_state": {
		"turn": X,
		"money": X,
		"doom": X,
		"papers": X,
		"researchers": X
	},
	"timestamp": X
}
```

**4. Manual Submission** (if no UI yet):

Copy data and submit via curl:
```bash
curl -X POST http://localhost:8080/api/scores/submit \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{ ... paste verification_data here ... }'
```

**Checklist**:
- [ ] Hash generated successfully
- [ ] Verification data exported correctly
- [ ] Final state includes all required fields
- [ ] Score calculated matches expected
- [ ] Manual submission succeeds
- [ ] Entry appears in leaderboard

---

## Day 5: Deployment Preparation

### Code Review & Cleanup

**1. Remove Debug Output** (if desired):
```gdscript
# In game_manager.gd, change:
VerificationTracker.enable_debug()  # Remove or comment out

# Or leave for beta testing
```

**2. Version Tagging**:
```bash
cd pdoom1
git add .
git commit -m "feat: Add cumulative hash verification for global leaderboards

- Implement VerificationTracker autoload with full RNG tracking
- Add comprehensive scoring system (safety + research + team + survival)
- Track 15+ RNG types for complete determinism
- Export 64-byte hash + game state for verification

Ready for Week 3 deployment.

Refs: #439 (CI/CD), docs/VERIFICATION_COMPLETE_SUMMARY.md"

git tag v0.11.0-beta-leaderboards
git push origin feature/ui-texture-integration
git push --tags
```

**3. Build Game Executables**:
```bash
# Export builds with verification enabled
# Windows, Linux, Mac builds
# Test each platform produces same hash for same seed
```

### Server Deployment

**1. Deploy to DreamCompute**:
```bash
# SSH to server
ssh your-server

# Pull latest code
cd pdoom1-website
git pull origin main

# Run migration
psql $DATABASE_URL -f scripts/db_migrations/003_add_verification_hashes.sql

# Restart API server
systemctl restart pdoom-api  # Or your process manager
```

**2. Verify API Running**:
```bash
curl http://your-api-domain/api/health

# Expected: {"status": "ok"}
```

**Checklist**:
- [ ] Code committed and tagged
- [ ] Game builds created
- [ ] Server code deployed
- [ ] Database migration run
- [ ] API server restarted
- [ ] Health check passes

---

## Day 6: Beta Testing

### Invite Beta Testers

**1. Create Beta Announcement**:
```markdown
# PDoom Global Leaderboards - Beta Test

We're launching global leaderboards with a unique verification system!

**What's New**:
- Global leaderboards (per seed)
- Fair play verification (no cheating possible)
- Strategy sharing encouraged (duplicates tracked, first discoverer credited)
- New scoring system (rewards safety, research, team building)

**How to Test**:
1. Download beta build: [link]
2. Play a game
3. Check your score on leaderboards: [link]
4. Report any issues: [Discord/Forum]

**Looking For**:
- Score balance feedback (too easy/hard to get high scores?)
- Verification system working correctly
- Any bugs or crashes
- Leaderboard display issues
```

**2. Monitor Submissions**:
```sql
-- Check submissions coming in
SELECT
	u.pseudonym,
	le.score,
	le.submitted_at,
	le.is_original_hash
FROM leaderboard_entries le
JOIN users u ON le.user_id = u.user_id
ORDER BY le.submitted_at DESC
LIMIT 20;

-- Check for any flagged hashes
SELECT * FROM verification_hashes
WHERE rapid_duplicate_flag = TRUE;
```

**3. Gather Feedback**:
- Discord reactions
- Forum posts
- Bug reports
- Score distribution analysis

**Checklist**:
- [ ] Beta announcement posted
- [ ] 5+ beta testers playing
- [ ] Submissions appearing in database
- [ ] No critical bugs reported
- [ ] Scores seem balanced
- [ ] Feedback collected

---

## Day 7: Launch Day!

### Morning: Final Checks

**1. Database Health**:
```sql
-- Check entry counts
SELECT COUNT(*) FROM leaderboard_entries;
SELECT COUNT(*) FROM verification_hashes;

-- Check for errors
SELECT * FROM verification_hashes WHERE rapid_duplicate_flag = TRUE;

-- Top scores look reasonable?
SELECT * FROM v_leaderboard_with_discoveries
WHERE seed = 'quantum-2024-11-20'
LIMIT 10;
```

**2. API Health**:
```bash
curl http://your-api/api/health
curl http://your-api/api/leaderboards/current?limit=10

# Check response times
time curl http://your-api/api/scores/submit ...
# Should be < 500ms
```

**3. Game Builds**:
- [ ] Windows build tested
- [ ] Linux build tested
- [ ] Mac build tested (if available)
- [ ] All produce consistent hashes

### Afternoon: Public Launch

**1. Launch Announcement**:

```markdown
# 🎉 PDoom Global Leaderboards - NOW LIVE!

After weeks of development, we're excited to launch global leaderboards!

**What Makes This Special**:

✅ **Fair Play Verification**: Our unique hash-based system prevents cheating
   without requiring invasive anti-cheat or storing your gameplay

✅ **Strategy Sharing**: Share your strategies! First to discover gets credit,
   others can reproduce for verification

✅ **Multiple Leaderboards**: Global, weekly challenges, per-seed competition

✅ **Balanced Scoring**: Rewards safety focus, research output, and survival
   (not just "turns survived")

**How It Works**:

Your game generates a unique "fingerprint" (hash) that proves you played
fairly. Same seed + same decisions = same hash. First to submit wins!

**Get Started**:
1. Download latest build: [link]
2. Play a game
3. View leaderboards: [link]

**Privacy First**:
- Anonymous by default
- Opt-in leaderboard display
- No tracking, no telemetry
- You own your data

Join the competition! 🏆

---

Technical Deep Dive: [link to docs]
Report Issues: [GitHub/Discord]
```

**2. Post to**:
- [ ] Game website
- [ ] Reddit (r/gamedev, r/incremental_games, r/aisafety)
- [ ] Discord server
- [ ] Twitter/social media
- [ ] IndieDB/itch.io

**3. Monitor Launch**:
```bash
# Watch logs
tail -f /var/log/pdoom-api.log

# Monitor database
watch "psql $DATABASE_URL -c 'SELECT COUNT(*) FROM leaderboard_entries'"

# Check for issues
psql $DATABASE_URL -c "
SELECT * FROM verification_hashes
WHERE rapid_duplicate_flag = TRUE
ORDER BY flagged_at DESC
LIMIT 5"
```

### Evening: Post-Launch

**Celebrate!** 🎉

Then:
- [ ] Respond to feedback
- [ ] Fix any critical bugs (hotfix if needed)
- [ ] Thank beta testers
- [ ] Plan Week 4 improvements

---

## Success Criteria

**Technical**:
- ✅ 99%+ submission success rate
- ✅ < 500ms API response time
- ✅ Zero hash collisions
- ✅ No critical bugs

**Community**:
- ✅ 50+ scores submitted in first 24h
- ✅ Positive feedback ratio > 80%
- ✅ No cheating reports
- ✅ Strategy sharing happening

**Business**:
- ✅ Leaderboards drive engagement
- ✅ Players return to compete
- ✅ Community grows

---

## Rollback Plan

If critical issues occur:

**1. Quick Fix** (if possible):
```bash
# Deploy hotfix
git checkout -b hotfix/leaderboard-issue
# ... make fix ...
git commit -m "hotfix: Fix critical leaderboard issue"
git push
# Deploy immediately
```

**2. Full Rollback**:
```bash
# Revert API changes
git revert [commit-hash]
systemctl restart pdoom-api

# Disable leaderboard submissions in game
# (emergency config flag or new build)
```

**3. Communicate**:
```markdown
We've temporarily disabled leaderboard submissions while we investigate
an issue. Your local scores are safe. We'll have this resolved within [timeframe].
```

---

## Week 4 Planning

**Post-Launch Improvements**:
- [ ] Add "Hall of Fame" (opt-in discoverer attribution)
- [ ] Weekly challenge seeds
- [ ] Leaderboard filters (by week, by mode)
- [ ] Score visualization
- [ ] Strategy guides section
- [ ] Achievement system

**Analytics to Track**:
- Score distribution
- Popular strategies (most duplicated hashes)
- Rare strategies (unique hashes)
- Player retention
- Average game length

---

**Ready to launch!** 🚀

Follow this checklist day by day and you'll have global leaderboards live by November 27th.
