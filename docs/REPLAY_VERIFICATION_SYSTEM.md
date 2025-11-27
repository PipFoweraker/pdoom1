# PDoom Replay Verification System

## Overview

A **replay-based anti-cheat system** that verifies scores by recording player inputs and deterministically replaying the game server-side. No shared secrets needed - verification is the game logic itself.

## Why This Works

PDoom's architecture is ideal for replay verification:

1. **Deterministic RNG**: `RandomNumberGenerator` seeded from `game_seed_str` produces identical results
2. **Turn-based**: Clear input  ->  output structure
3. **Action queue**: All player choices recorded as action IDs
4. **Pure functions**: Game state mutations are deterministic given inputs

## Core Concept

```
Player plays game with seed "quantum-2024"
   v 
Records: [hire_safety_researcher, buy_compute, safety_research, ...]
   v 
Submits: {seed: "quantum-2024", actions: [...], final_score: 85000}
   v 
Server replays: same seed + same actions = verifies score matches
```

## Data Structure

### Replay File Format

```gdscript
# Replay data structure (JSON serializable)
{
  "version": "0.10.2",           # Game version for compatibility
  "seed": "quantum-2024",         # Game seed (deterministic RNG)
  "start_timestamp": 1732109234,  # Unix timestamp
  "end_timestamp": 1732112834,    # Unix timestamp (60min game)
  "player_id": "device_uuid",     # Anonymous player identifier

  "actions": [
    {
      "turn": 1,
      "actions": ["hire_safety_researcher_0", "buy_compute"]
    },
    {
      "turn": 2,
      "actions": ["safety_research", "publish_paper"]
    },
    {
      "turn": 3,
      "event_response": "invest_in_interpretability",  # Event choices
      "actions": ["buy_compute"]
    }
    # ... continues for all turns
  ],

  "final_state": {
    "turn": 42,
    "score": 85000,
    "money": 120000,
    "doom": 35.2,
    "papers": 12,
    "researchers": 8,
    "game_over": false,
    "victory": true
  },

  "checksum": "sha256_hash_of_replay_data"  # Tamper detection
}
```

### Action Encoding

Actions are stored as ID strings that uniquely identify the choice:

```gdscript
# Simple actions
"buy_compute"
"safety_research"
"publish_paper"

# Hiring actions (includes candidate index from pool)
"hire_safety_researcher_0"   # Hire first candidate in pool
"hire_capabilities_researcher_2"  # Hire third candidate

# Event responses
"event_response:invest_in_interpretability"
"event_response:decline_funding"

# Submenu actions
"fundraise:conservative"
"fundraise:aggressive"
"publicity:academic_conference"
```

**Key insight**: Candidate pool is deterministic (generated from `state.rng`), so candidate index is sufficient.

## Implementation

### Phase 1: Replay Recording (Client-Side)

Create `godot/autoload/replay_recorder.gd`:

```gdscript
extends Node
## Records all player actions for replay verification

var recording: bool = false
var replay_data: Dictionary = {}
var current_turn_actions: Array[String] = []

func start_recording(seed: String, player_id: String):
	"""Begin recording a new game session"""
	recording = true
	replay_data = {
		"version": GameManager.get_version(),
		"seed": seed,
		"start_timestamp": Time.get_unix_time_from_system(),
		"player_id": player_id,
		"actions": []
	}

func record_action(action_id: String):
	"""Record a player action for current turn"""
	if not recording:
		return

	current_turn_actions.append(action_id)

func record_event_response(event_id: String, response_id: String):
	"""Record player's response to an event"""
	if not recording:
		return

	var event_action = "event_response:%s:%s" % [event_id, response_id]
	current_turn_actions.append(event_action)

func end_turn(turn_number: int):
	"""Commit actions for completed turn"""
	if not recording or current_turn_actions.size() == 0:
		return

	replay_data["actions"].append({
		"turn": turn_number,
		"actions": current_turn_actions.duplicate()
	})

	current_turn_actions.clear()

func finish_recording(final_state: Dictionary) -> Dictionary:
	"""Complete recording and return replay data"""
	if not recording:
		return {}

	recording = false

	replay_data["end_timestamp"] = Time.get_unix_time_from_system()
	replay_data["final_state"] = final_state

	# Generate checksum (tamper detection)
	var replay_json = JSON.stringify(replay_data)
	replay_data["checksum"] = replay_json.sha256_text()

	return replay_data

func export_to_file(filepath: String):
	"""Save replay to local file (for debugging/sharing)"""
	var file = FileAccess.open(filepath, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(replay_data, "\t"))
		file.close()
```

### Phase 2: Game Integration

Modify game flow to record actions:

```gdscript
# In game_manager.gd or main_ui.gd

func start_new_game(seed: String):
	# Existing game start logic...

	# Start replay recording
	var player_id = PrivacyManager.get_device_id()
	ReplayRecorder.start_recording(seed, player_id)

func queue_action(action_id: String):
	# Existing action queue logic...

	# Record for replay
	ReplayRecorder.record_action(action_id)

func handle_event_response(event_id: String, response_id: String):
	# Existing event handling...

	# Record for replay
	ReplayRecorder.record_event_response(event_id, response_id)

func end_turn():
	# Process turn...
	TurnManager.process_turn()

	# Record turn completion
	ReplayRecorder.end_turn(state.turn)

func end_game():
	# Game over logic...

	# Finish replay recording
	var final_state = {
		"turn": state.turn,
		"score": calculate_score(),
		"money": state.money,
		"doom": state.doom,
		"papers": state.papers,
		"researchers": state.researchers.size(),
		"game_over": state.game_over,
		"victory": state.victory
	}

	var replay = ReplayRecorder.finish_recording(final_state)

	# Submit to backend for verification
	await BackendAPI.submit_score_with_replay(replay)
```

### Phase 3: Server-Side Replay Engine

Create lightweight headless replay engine (Python or GDScript):

#### Option A: Python Replay Engine

Reimplement core game logic in Python (minimal, deterministic subset):

```python
# backend/replay_engine/game_replay.py

import json
import hashlib
import random

class ReplayEngine:
    """Lightweight game engine for replay verification"""

    def __init__(self, seed: str):
        self.seed = seed
        self.rng = random.Random(hash(seed))  # Match Godot's seed hashing

        # Initialize game state (mirrors GameState.gd)
        self.money = 245000.0
        self.compute = 100.0
        self.research = 0.0
        self.papers = 0.0
        self.doom = 50.0
        self.action_points = 3

        self.turn = 0
        self.researchers = []
        self.candidate_pool = []

    def verify_replay(self, replay_data: dict) -> dict:
        """
        Replay the game and verify final state matches

        Returns:
            {
                "valid": bool,
                "expected_score": int,
                "submitted_score": int,
                "state_diff": dict  # Differences if invalid
            }
        """
        # Validate checksum
        checksum_valid = self._validate_checksum(replay_data)
        if not checksum_valid:
            return {"valid": False, "error": "Checksum mismatch - replay tampered"}

        # Replay each turn
        for turn_data in replay_data["actions"]:
            self.turn = turn_data["turn"]
            self._process_turn_start()

            for action_id in turn_data["actions"]:
                self._execute_action(action_id)

            self._process_turn_end()

        # Calculate final score
        expected_score = self._calculate_score()
        submitted_score = replay_data["final_state"]["score"]

        # Verify state matches
        state_match = self._verify_final_state(replay_data["final_state"])

        return {
            "valid": (expected_score == submitted_score and state_match),
            "expected_score": expected_score,
            "submitted_score": submitted_score,
            "final_doom": self.doom,
            "final_papers": self.papers
        }

    def _validate_checksum(self, replay_data: dict) -> bool:
        """Verify replay hasn't been tampered with"""
        submitted_checksum = replay_data.get("checksum", "")

        # Recompute checksum (exclude checksum field itself)
        data_copy = replay_data.copy()
        data_copy.pop("checksum", None)

        replay_json = json.dumps(data_copy, sort_keys=True)
        expected_checksum = hashlib.sha256(replay_json.encode()).hexdigest()

        return submitted_checksum == expected_checksum

    def _process_turn_start(self):
        """Mirror TurnManager.start_turn()"""
        # Staff salaries
        staff_count = len(self.researchers)
        salaries = staff_count * 5000
        self.money -= salaries

        # Populate candidate pool (deterministic)
        self._populate_candidates()

        # Reset action points
        self.action_points = 3 + int(staff_count * 0.5)

    def _populate_candidates(self):
        """Generate candidates (deterministic from RNG)"""
        empty_slots = 6 - len(self.candidate_pool)
        chance = 0.30 + (empty_slots * 0.10)

        if self.rng.random() < chance and empty_slots > 0:
            candidate = self._generate_candidate()
            self.candidate_pool.append(candidate)

    def _generate_candidate(self) -> dict:
        """Generate random candidate (matches TurnManager logic)"""
        specs = ["safety", "capabilities", "interpretability", "alignment"]
        weights = [0.35, 0.25, 0.20, 0.20]

        spec = self.rng.choices(specs, weights=weights)[0]

        return {
            "specialization": spec,
            "productivity": self.rng.uniform(0.7, 1.3),
            "salary": self.rng.randint(60000, 120000)
        }

    def _execute_action(self, action_id: str):
        """Execute a single action (mirrors game logic)"""
        if action_id == "buy_compute":
            if self.money >= 50000:
                self.money -= 50000
                self.compute += 50
                self.action_points -= 1

        elif action_id == "safety_research":
            if self.research >= 10:
                self.research -= 10
                self.doom -= 2.0
                self.action_points -= 1

        elif action_id == "publish_paper":
            if self.research >= 20:
                self.research -= 20
                self.papers += 1
                self.doom -= 3.0
                self.action_points -= 1

        elif action_id.startswith("hire_"):
            # Parse: "hire_safety_researcher_0" -> index 0
            parts = action_id.split("_")
            candidate_index = int(parts[-1])

            if candidate_index < len(self.candidate_pool):
                candidate = self.candidate_pool.pop(candidate_index)
                self.researchers.append(candidate)
                self.money -= 20000  # Hiring cost

        # Add more actions as needed...

    def _process_turn_end(self):
        """End of turn processing"""
        # Researchers generate research
        for researcher in self.researchers:
            if self.rng.random() < 0.30 * researcher["productivity"]:
                self.research += self.rng.randint(1, 3)

        # Doom increases slightly each turn
        self.doom += 0.5

    def _calculate_score(self) -> int:
        """Calculate final score (mirrors game scoring)"""
        score = 0
        score += self.money * 0.1
        score += self.papers * 5000
        score += (100 - self.doom) * 1000
        score += len(self.researchers) * 2000
        return int(score)

    def _verify_final_state(self, submitted_state: dict) -> bool:
        """Check if final state matches replay"""
        tolerance = 0.01  # Allow tiny floating point differences

        return (
            abs(self.doom - submitted_state["doom"]) < tolerance and
            abs(self.papers - submitted_state["papers"]) < tolerance and
            len(self.researchers) == submitted_state["researchers"]
        )
```

#### Option B: Godot Headless Replay Engine

Export Godot as headless server binary:

```bash
# Export headless Linux binary for server
godot --headless --export-release "Linux/X11" replay_engine_linux

# Run replays server-side
./replay_engine_linux --replay verify_replay.json
```

**Pros**: Exact same game logic, no reimplementation
**Cons**: Heavier (full Godot runtime), slower startup

**Recommendation**: Start with Option B (Godot headless) for exact parity, migrate to Option A (Python) once stable.

### Phase 4: API Integration

Add verification endpoint to API server:

```python
# In pdoom1-website/scripts/api-server-v2.py

from replay_engine.game_replay import ReplayEngine

@app.post("/api/v1/scores/submit_with_replay")
async def submit_score_with_replay(
    replay_data: dict,
    auth_token: str = Header(...)
):
    """
    Submit score with replay for verification

    Steps:
    1. Validate authentication
    2. Verify replay checksum (tamper detection)
    3. Replay game to verify score
    4. If valid, add to leaderboard
    5. Store replay for later analysis
    """

    # Authenticate player
    player = await authenticate_token(auth_token)
    if not player:
        raise HTTPException(401, "Invalid authentication")

    # Verify player opted in
    if not player.opted_in:
        raise HTTPException(403, "Player not opted into leaderboards")

    # Rate limiting (prevent spam)
    if exceeded_rate_limit(player.id):
        raise HTTPException(429, "Too many submissions")

    # Verify replay
    engine = ReplayEngine(replay_data["seed"])
    verification = engine.verify_replay(replay_data)

    if not verification["valid"]:
        # Log suspicious activity
        log_failed_verification(player.id, replay_data, verification)

        raise HTTPException(400, {
            "error": "Replay verification failed",
            "details": verification
        })

    # Replay is valid - store score
    score_entry = {
        "player_id": player.id,
        "seed": replay_data["seed"],
        "score": verification["expected_score"],
        "game_version": replay_data["version"],
        "verified": True,
        "submitted_at": datetime.utcnow()
    }

    db.insert_score(score_entry)

    # Store replay for analysis (compress to save space)
    replay_storage.save_replay(
        player_id=player.id,
        replay_data=replay_data,
        compress=True
    )

    # Calculate rank
    rank = db.get_player_rank(replay_data["seed"], verification["expected_score"])

    return {
        "status": "verified",
        "score": verification["expected_score"],
        "rank": rank,
        "seed": replay_data["seed"]
    }
```

## Security Benefits

### vs Shared Secrets (HMAC)

| Feature | HMAC | Replay Verification |
|---------|------|---------------------|
| Client-side tampering | WARNING Vulnerable (if secret leaked) | SUCCESS Impossible (must provide valid inputs) |
| Score inflation | WARNING Easy if secret known | SUCCESS Impossible (replay proves legitimacy) |
| Transparency | ERROR Opaque | SUCCESS Replays can be shared publicly |
| Implementation | SUCCESS Simple | WARNING Complex (game logic reimplementation) |
| Future features | ERROR Limited | SUCCESS Enables spectating, tutorials, analysis |

### Attack Resistance

**Attack 1: Submit fake score without playing**
- ERROR **Blocked**: No valid action sequence can produce fake score

**Attack 2: Modify replay JSON to inflate score**
- ERROR **Blocked**: Checksum detects tampering
- ERROR **Blocked**: Even if checksum bypassed, replay won't produce inflated score

**Attack 3: Find lucky RNG seed, submit multiple times**
- SUCCESS **Allowed**: Legitimate strategy (like speedrun seed hunting)
- WARNING **Mitigation**: Leaderboard shows "per seed" and "best overall"

**Attack 4: Reverse engineer game logic, craft perfect inputs**
- SUCCESS **Allowed**: This is just being very good at the game!
- SUCCESS **Benefit**: Encourages strategic depth

**Attack 5: Memory hacking during gameplay**
- WARNING **Partial**: Can modify client state, but replay will fail verification
- SUCCESS **Detection**: Server sees impossible action sequences

## Privacy Considerations

### Replay Data Privacy

**What replays reveal:**
- SUCCESS Game strategy and decision-making
- SUCCESS Reaction to events
- SUCCESS Playstyle (aggressive vs conservative)

**What replays DON'T reveal:**
- ERROR No personal information
- ERROR No IP addresses (if stored anonymously)
- ERROR No gameplay outside this specific run

**Privacy Controls:**

```gdscript
# In PrivacyManager.gd

var share_replays: bool = false  # Opt-in for public replay sharing

func should_submit_replay() -> bool:
	"""Only submit replay if player opted in"""
	return opted_in  # Uses existing leaderboard opt-in

func can_share_replay_publicly() -> bool:
	"""Separate opt-in for public replay database"""
	return share_replays
```

### Replay Storage

**Server-side storage strategy:**

1. **Verified scores**: Keep replay for 30 days (anti-cheat auditing)
2. **Top 100 scores**: Keep permanently (leaderboard verification)
3. **Suspicious scores**: Keep permanently (ban appeals)
4. **Public replays**: Only if player opted in to sharing

**Compression**: Replays are small (~5-20KB), compress to ~1-2KB with gzip

## Rollout Plan

### Phase 1: Local Replay Recording (Week 1)
- [ ] Implement `ReplayRecorder` autoload
- [ ] Integrate with game flow (record actions)
- [ ] Export replays to local files
- [ ] Test: Play game, verify replay records correctly

### Phase 2: Replay Playback (Week 2)
- [ ] Implement local replay player (watch recorded games)
- [ ] Add UI: "Watch Replay" button on leaderboard
- [ ] Test: Verify playback produces identical results

### Phase 3: Server-Side Verification (Week 3)
- [ ] Build Python replay engine (minimal game logic)
- [ ] Add verification unit tests
- [ ] Deploy to backend server
- [ ] Test: Submit replays, verify server validation works

### Phase 4: API Integration (Week 4)
- [ ] Add `/api/v1/scores/submit_with_replay` endpoint
- [ ] Implement rate limiting
- [ ] Add suspicious replay logging
- [ ] Test: End-to-end submission + verification

### Phase 5: Production Deployment (Week 5)
- [ ] Enable replay submission in game client
- [ ] Monitor verification success rate
- [ ] Tune replay engine for accuracy
- [ ] Add admin tools to review flagged replays

## Implementation Estimate

**Total effort**: 3-4 weeks

**Breakdown**:
- Week 1: Replay recording (Client-side) - 2-3 days
- Week 2: Replay playback (Client-side) - 2-3 days
- Week 3: Verification engine (Server-side) - 4-5 days
- Week 4: API integration - 2 days
- Week 5: Testing + deployment - 3 days

**vs HMAC approach**: 2-3 days

**Trade-off**: 10x more implementation time, but **infinitely more robust** and enables future features.

## Future Enhancements

Once replay system is working:

### 1. Replay Sharing
- Players can share replays of impressive runs
- "Featured Replay of the Week" on website
- Replay browser with filters (high scores, specific strategies)

### 2. Spectator Mode
- Watch top players' strategies in real-time
- Learn optimal decision-making

### 3. Tournament Mode
- Weekly challenge: specific seed
- Leaderboard shows top replays
- Community votes on best strategies

### 4. AI Analysis
- Train ML model on top replays
- Suggest optimal moves to players
- Identify new strategies

### 5. Replay Compression
- Delta encoding (only store state changes)
- Reduce 20KB replay to 1-2KB

### 6. Replay Versioning
- Handle game updates gracefully
- Store game version in replay
- Maintain compatibility across versions

## Conclusion

Replay-based verification is the **gold standard** for competitive game anti-cheat:

SUCCESS **Cheat-proof**: Impossible to fake without playing legitimately
SUCCESS **Transparent**: Replays can be shared and analyzed
SUCCESS **Future-proof**: Enables spectating, tutorials, tournaments
SUCCESS **No secrets**: No shared keys to leak or manage
SUCCESS **Privacy-preserving**: Only game actions recorded, no personal data

**Recommendation**: Implement this system. It's more work upfront, but makes your leaderboards bulletproof and unlocks exciting community features.

---

## Decision Point

Ready to proceed with replay verification instead of HMAC?

**Next step**: Start Phase 1 (Replay Recording) - I can help you implement `ReplayRecorder` autoload and integrate it into your game flow.
