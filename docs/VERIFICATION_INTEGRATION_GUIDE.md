# Verification Tracker Integration Guide

**Status**: ✅ VerificationTracker autoload implemented
**Next**: Integrate into game flow

---

## Implementation Checklist

### ✅ Phase 1: Core Infrastructure (COMPLETE)

- [x] Create `verification_tracker.gd` autoload
- [x] Register in `project.godot`
- [x] Implement hash chaining logic
- [x] Implement state snapshot creation
- [x] Add debug logging

### 🔄 Phase 2: Game Start Integration (NEXT)

**File**: `godot/scripts/game_manager.gd` or equivalent

**Location**: Where new game is initialized

**Code to add**:
```gdscript
func start_new_game(seed: String):
	# ... existing game initialization ...

	# Start verification tracking
	var version = GameConfig.get_version() # Or hardcode version string
	VerificationTracker.start_tracking(seed, version)

	print("[Game] Verification tracking started for seed: %s" % seed)
```

**Test**:
- Start new game
- Check console for "[VerificationTracker] Started tracking"
- Verify initial hash is set

---

### 🔄 Phase 3: Action Execution Integration

**File**: Wherever actions are executed (likely `game_manager.gd` or `main_ui.gd`)

**Location**: After action is executed and game state updated

**Code to add**:
```gdscript
func execute_action(action_id: String):
	# ... existing action execution logic ...
	# (e.g., spend resources, update state, etc.)

	# Record action in verification hash
	VerificationTracker.record_action(action_id, game_state)
```

**Special case - Hiring actions**:
```gdscript
func hire_researcher(candidate_index: int):
	# ... existing hiring logic ...

	# Record with specific candidate index
	var action_id = "hire_researcher_%d" % candidate_index
	VerificationTracker.record_action(action_id, game_state)
```

**Test**:
- Execute various actions
- Check console for "[VerificationTracker] Action: ..."
- Verify hash changes after each action

---

### 🔄 Phase 4: Event System Integration

**File**: `godot/scripts/core/events.gd` or event handler

#### When Event Triggers

**Location**: Where random events are triggered

**Code to add**:
```gdscript
func trigger_event(event: Dictionary):
	# ... existing event trigger logic ...

	# Record event in verification hash
	VerificationTracker.record_event(
		event["id"],
		event["type"],
		game_state.turn
	)
```

#### When Player Responds to Event

**Location**: Where player's event response is processed

**Code to add**:
```gdscript
func handle_event_response(event_id: String, response_id: String):
	# ... existing response handling ...

	# Record response in verification hash
	VerificationTracker.record_event_response(
		event_id,
		response_id,
		game_state.turn
	)
```

**Test**:
- Trigger events
- Choose responses
- Verify hash updates for both trigger and response

---

### 🔄 Phase 5: RNG Outcome Tracking

**File**: `godot/scripts/core/turn_manager.gd`

**Critical RNG calls to track**:

#### Candidate Generation
```gdscript
func _generate_random_candidate() -> Researcher:
	# ... existing candidate generation ...

	# Record RNG outcome for specialization
	var spec_roll = state.rng.randf()
	VerificationTracker.record_rng_outcome("candidate_spec", spec_roll, state.turn)

	# Determine specialization from roll
	var cumulative = 0.0
	var spec = "safety"
	for i in range(specializations.size()):
		cumulative += weights[i]
		if spec_roll < cumulative:
			spec = specializations[i]
			break

	# ... rest of candidate generation ...
```

#### Event Probability Rolls
```gdscript
func check_event_trigger() -> bool:
	var roll = state.rng.randf()
	VerificationTracker.record_rng_outcome("event_trigger", roll, state.turn)

	return roll < event_probability
```

#### Research Breakthroughs
```gdscript
func check_research_breakthrough() -> bool:
	var roll = state.rng.randf()
	VerificationTracker.record_rng_outcome("research_breakthrough", roll, state.turn)

	return roll < breakthrough_chance
```

**Philosophy**: Record RNG outcomes that **affect gameplay**, not cosmetic things

**Test**:
- Play same seed twice
- Verify identical RNG outcomes produce identical hashes

---

### 🔄 Phase 6: Turn End Integration

**File**: `godot/scripts/core/turn_manager.gd`

**Location**: At end of `process_turn()` or equivalent

**Code to add**:
```gdscript
func process_turn():
	# ... existing turn processing ...

	# Record turn end
	VerificationTracker.record_turn_end(state.turn, state)

	print("[Turn] Turn %d complete, hash updated" % state.turn)
```

**Test**:
- Complete full turns
- Verify hash updates at turn boundaries

---

### 🔄 Phase 7: Game End & Submission

**File**: `godot/scripts/end_game_screen.gd` or wherever game end is handled

**Location**: When game ends (victory/defeat)

**Code to add**:
```gdscript
func on_game_end():
	# ... existing game end logic ...

	# Get final verification hash
	var final_hash = VerificationTracker.get_final_hash()

	# Prepare final state for submission
	var final_state = {
		"turn": game_state.turn,
		"money": game_state.money,
		"doom": game_state.doom,
		"papers": game_state.papers,
		"research": game_state.research,
		"compute": game_state.compute,
		"researchers": game_state.researchers.size(),
		"game_over": game_state.game_over,
		"victory": game_state.victory
	}

	# Export for submission
	var submission_data = VerificationTracker.export_for_submission(final_state)

	print("[Game] Final verification hash: %s" % final_hash)
	print("[Game] Ready for leaderboard submission")

	# TODO: Submit to BackendAPI (Phase 8)
	# await BackendAPI.submit_score(submission_data)
```

**Test**:
- Complete full game
- Verify final hash is generated
- Verify submission data format is correct

---

### 🔄 Phase 8: Backend API Integration (FUTURE)

**File**: New file `godot/autoload/backend_api.gd`

**Not implemented yet** - Requires:
- HTTP client setup
- JWT authentication
- Score submission endpoint

**Placeholder**:
```gdscript
# backend_api.gd (future)
extends Node

func submit_score(verification_data: Dictionary) -> Dictionary:
	# TODO: Implement HTTP request to /api/scores/submit
	# TODO: Handle authentication (JWT token)
	# TODO: Return response (rank, status, duplicate info)

	print("[API] Score submission not yet implemented")
	return {"status": "pending"}
```

---

## Testing Strategy

### Test 1: Determinism (CRITICAL)

**Goal**: Same seed + same actions = same hash

**Steps**:
1. Start game with seed "test-seed-123"
2. Execute specific sequence of actions:
   - hire_researcher_0
   - buy_compute
   - safety_research
   - publish_paper
3. Record final hash
4. Restart game with same seed
5. Execute EXACT same actions
6. Verify final hash is identical

**Expected**: Both games produce hash `abc123def456...` (identical)

**If fails**: Check for:
- Floating-point rounding issues
- Non-deterministic RNG calls
- State snapshot order changes
- Missing hash updates

### Test 2: Sensitivity

**Goal**: Different actions = different hash

**Steps**:
1. Play seed "test-seed-123"
2. Execute: hire_researcher_0, buy_compute
3. Record hash after buy_compute
4. Restart with same seed
5. Execute: hire_researcher_1, buy_compute (different candidate!)
6. Record hash after buy_compute

**Expected**: Hashes are different

**If fails**: Hash updates not sensitive enough

### Test 3: RNG Tracking

**Goal**: RNG outcomes affect hash

**Steps**:
1. Enable debug mode: `VerificationTracker.enable_debug()`
2. Play game and trigger candidate generation
3. Check console for RNG outcome logs
4. Verify hash changes after RNG calls

**Expected**: See "[VerificationTracker] RNG: candidate_spec=0.342156 →..."

### Test 4: Turn Boundary

**Goal**: Hash updates at turn end

**Steps**:
1. Play one full turn
2. Verify hash changes at turn end
3. Check that turn-end hash includes turn number

**Expected**: Hash changes predictably at turn boundaries

---

## Debug Tools

### Enable Verbose Logging

```gdscript
# In _ready() or settings menu
VerificationTracker.enable_debug()
```

**Output**:
```
[VerificationTracker] Started tracking
  Seed: quantum-2024
  Version: 0.10.2
  Initial hash: abc123def456...
[VerificationTracker] Action: buy_compute → def456789abc...
[VerificationTracker] RNG: candidate_spec=0.342156 → 789abcdef123...
[VerificationTracker] Turn 1 end → 123def456789...
```

### Get Current Hash

```gdscript
# At any point during game
var current_hash = VerificationTracker.get_final_hash()
print("Current hash: %s" % current_hash)

# Or get summary
var summary = VerificationTracker.get_tracking_summary()
print(summary)
```

### Manual Hash Comparison

Save hashes to file for comparison:

```gdscript
# At game end
var hash = VerificationTracker.get_final_hash()
var file = FileAccess.open("user://hash_log.txt", FileAccess.WRITE)
file.store_line("Seed: %s" % game_seed)
file.store_line("Hash: %s" % hash)
file.close()
```

---

## Common Issues & Solutions

### Issue 1: Non-Deterministic Hashes

**Symptom**: Same seed + same actions = different hashes

**Causes**:
- Float precision differences across runs
- Non-deterministic RNG calls
- State snapshot includes non-deterministic data
- Action order not preserved

**Solutions**:
- Use `snappedf()` to round floats consistently
- Only use `state.rng` (seeded RNG), never `randf()` (global)
- Verify state snapshot fields are deterministic
- Record actions in execution order, not UI interaction order

### Issue 2: Hash Too Sensitive

**Symptom**: Tiny state differences cause different hashes (expected, but check if problematic)

**Example**: `money = 99999.999` vs `money = 100000.001` → different hashes

**Solution**: This is correct behavior - hash should be sensitive!

**But if problematic**: Increase rounding precision in `snappedf(value, 0.01)` → `snappedf(value, 0.1)`

### Issue 3: Missing Hash Updates

**Symptom**: Identical hashes for games that should differ

**Causes**:
- Action executed but not recorded
- Event triggered but not tracked
- RNG call not logged

**Solution**: Add verification tracker calls to all gameplay-affecting code paths

### Issue 4: Performance Impact

**Symptom**: Game feels slower after adding verification

**Unlikely**: SHA-256 hashing is fast (< 1ms per call)

**If real issue**:
- Profile to confirm hash updates are the bottleneck
- Consider batching hash updates (less secure)
- Don't hash on every frame, only on meaningful game events

---

## Integration Sequence

**Recommended order**:

1. ✅ Create VerificationTracker autoload (DONE)
2. ✅ Register in project.godot (DONE)
3. 🔄 Add to game start (test: hash initializes)
4. 🔄 Add to action execution (test: hash changes)
5. 🔄 Add to turn end (test: turn boundaries)
6. 🔄 Test determinism (same seed twice)
7. 🔄 Add event tracking
8. 🔄 Add RNG tracking
9. 🔄 Test full game playthrough
10. 🔄 Add game end export
11. ⏳ Backend API integration (future)

**Timeline**: ~2-3 days for full integration

---

## Documentation for Players (Future)

Once system is live, explain to players:

**What is verification?**
- "Your score is cryptographically verified"
- "Can't fake a score without actually playing"
- "First to discover a strategy gets credit"

**What is the hash?**
- "Unique fingerprint of your game"
- "Same strategy = same hash (proof of reproducibility)"
- "Share your hash to prove your strategy works"

**Privacy?**
- "Hash doesn't reveal your actions"
- "Only proves you played legitimately"
- "Anonymous by default"

---

## Next Steps

1. **Start Integration**: Begin with Phase 2 (game start)
2. **Test Incrementally**: After each phase, test that hash updates
3. **Verify Determinism**: Critical test before deployment
4. **Document Findings**: Update this guide with issues/solutions
5. **Prepare for Launch**: Blog post, Reddit announcement

**Status**: Ready to integrate into game flow!
