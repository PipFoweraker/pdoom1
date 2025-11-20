# Verification System - Quick Reference

**TL;DR**: Every game generates a unique 64-byte hash that proves you played fairly. Same seed + same actions = same hash. Different actions = different hash. Leaderboards use this to prevent cheating while allowing strategy sharing.

---

## For Developers

### How It Works

```gdscript
# Game starts
VerificationTracker.start_tracking("seed-123", "v0.10.2")

# Every action
VerificationTracker.record_action("buy_compute", game_state)

# Every RNG outcome
VerificationTracker.record_rng_outcome("candidate_spec", 0.342, turn)

# Every event
VerificationTracker.record_event("funding_crisis", "random", turn)
VerificationTracker.record_event_response("funding_crisis", "accept", turn)

# Turn end
VerificationTracker.record_turn_end(turn, game_state)

# Game end
var hash = VerificationTracker.get_final_hash()
var data = VerificationTracker.export_for_submission(final_state)
```

### Key Files

| File | Purpose |
|------|---------|
| `godot/autoload/verification_tracker.gd` | Core tracking system |
| `godot/scripts/game_manager.gd` | Initialization |
| `godot/scripts/core/turn_manager.gd` | Action/event tracking |
| `godot/scripts/core/events.gd` | Event RNG tracking |
| `godot/scripts/core/actions.gd` | Action RNG tracking |
| `godot/scripts/ui/game_over_screen.gd` | Hash export |
| `godot/tests/unit/test_verification_determinism.gd` | Tests |

### Adding New RNG Sources

If you add new RNG calls that affect gameplay:

```gdscript
# BEFORE
var random_value = state.rng.randf()

# AFTER
var random_value = state.rng.randf()
VerificationTracker.record_rng_outcome("my_new_rng_type", random_value, state.turn)
```

**Critical**: Track BEFORE using the value, and use descriptive type names.

### Debug Mode

```gdscript
# Enable verbose logging
VerificationTracker.enable_debug()

# Disable verbose logging
VerificationTracker.disable_debug()
```

Output shows every hash update:
```
[VerificationTracker] Action: buy_compute → 7a3f2e1b...
[VerificationTracker] RNG: candidate_spec=0.342156 → 9b2c4d5e...
```

---

## For Players (Future Documentation)

### What Is Verification?

When you play PDoom, the game creates a unique "fingerprint" (hash) of your entire playthrough. This fingerprint:

- **Proves you played fairly** (no cheating)
- **Allows strategy sharing** (others can reproduce your strategy)
- **Protects your privacy** (doesn't reveal specific actions)
- **Enables fair leaderboards** (first to discover gets credit)

### How Leaderboards Work

1. **You play a game** → Game generates verification hash
2. **You submit your score** → Hash + score sent to server
3. **Server checks**:
   - Is this hash valid? (plausibility check)
   - Has anyone submitted this before? (timestamp priority)
4. **Leaderboard updated**:
   - First to submit hash = "Original" (⭐)
   - Later submissions = "Duplicate" (🔁)

### Why Duplicates Are OK

If someone else submits the same hash as you:
- They played the same seed with identical decisions
- This is **legitimate** and proves strategies are reproducible
- First submission gets "Original" credit
- Later submissions are tracked but not penalized
- Think speedrun culture: first to discover route gets credit, sharing makes everyone better

### Privacy

What we collect:
- ✅ Verification hash (64 characters, no personal info)
- ✅ Final game state (score, resources, turn count)
- ✅ Timestamp

What we DON'T collect:
- ❌ Your specific gameplay actions
- ❌ IP addresses (not logged)
- ❌ Personal information
- ❌ Telemetry/analytics (unless opted in)

---

## For Server Developers

### API Endpoint Enhancement

**POST** `/api/scores/submit`

**Request**:
```json
{
  "verification_hash": "8a0b2c4d6e8f0a1b...",
  "seed": "quantum-2024-11-20",
  "game_version": "0.10.2",
  "final_state": {
    "turn": 50,
    "money": 125000,
    "doom": 45.5,
    "papers": 5,
    "research": 120,
    "compute": 350,
    "researchers": 8
  },
  "score": 234567,
  "timestamp": 1732118400
}
```

**Server Logic**:
1. Check if hash exists in `verification_hashes` table
2. If new:
   - Create hash record (first_submitted_by, first_submitted_at)
   - Create leaderboard entry (is_original_hash = TRUE)
   - Response: "Original discovery!"
3. If duplicate from same player:
   - Log but ignore
   - Response: "You already submitted this"
4. If duplicate from different player:
   - Increment duplicate_count
   - Create leaderboard entry (is_duplicate_hash = TRUE)
   - Create hash_duplicates record
   - Response: "Discovered X hours ago by another player"
5. Plausibility checks:
   - Doom in [0, 100]
   - Resources not negative (except money can be negative)
   - Turn count reasonable
   - Recalculated score matches submitted score

**Database Tables** (see `docs/HASH_VERIFICATION_POLICY.md`):
- `verification_hashes` (unique hashes, first submission tracking)
- `hash_duplicates` (all duplicate submissions)
- `leaderboard_entries` (scores with original/duplicate flags)

---

## Testing

### Run Determinism Tests

```bash
# From godot directory
godot --headless --script tests/unit/test_verification_determinism.gd
```

### Manual Testing

```gdscript
# In game console or test script
VerificationTracker.enable_debug()

# Play game, then check:
print(VerificationTracker.get_tracking_summary())
# Output:
# {
#   "tracking_enabled": true,
#   "game_seed": "test-seed-001",
#   "game_version": "0.10.2",
#   "current_hash": "7a3f2e1b9c8d4a5f...",
#   "hash_prefix": "7a3f2e1b9c8d4a5f"
# }
```

---

## Troubleshooting

### Hash Mismatch Between Replays

**Symptom**: Same seed + same actions → different hash

**Common Causes**:
1. **New RNG call not tracked** → Add `record_rng_outcome()`
2. **Float precision issue** → Ensure using `snappedf()` for rounding
3. **Action order different** → Check action execution order
4. **Event RNG not tracked** → Check event trigger tracking
5. **Platform difference** → Test cross-platform consistency

**Fix**: Enable debug mode, compare hash update logs side-by-side

### Hash Not Updating

**Symptom**: Hash stays same after actions

**Causes**:
1. Tracking not started → Check `start_tracking()` called
2. Tracking disabled → Check `tracking_enabled` flag
3. Silent failure → Check debug logs

**Fix**:
```gdscript
if not VerificationTracker.is_tracking():
    print("ERROR: Tracking not enabled!")
```

### Export Fails

**Symptom**: `export_for_submission()` returns empty/invalid data

**Causes**:
1. Called before `stop_tracking()`
2. Invalid final_state dictionary
3. Missing required fields

**Fix**: Check final_state has all required keys before export

---

## Performance

### Overhead

- **Hash update**: < 0.1ms per operation
- **Memory**: ~1KB tracking overhead
- **Network**: < 1KB submission payload

### Optimization Tips

1. Don't call `record_rng_outcome()` for visual-only RNG (UI animations, etc.)
2. Only track gameplay-affecting outcomes
3. Use debug mode sparingly (impacts performance)
4. Disable tracking in non-competitive modes (if needed)

---

## Security Notes

### What's Protected

- ✅ Score inflation (can't fake without valid state)
- ✅ State tampering (breaks hash chain)
- ✅ Replay attacks (timestamp priority)
- ✅ Action reordering (turn sequence matters)

### What's NOT Protected

- ⚠️ Memory hacking (but plausibility checks catch extremes)
- ⚠️ RNG manipulation (but that's strategy optimization!)
- ⚠️ Perfect play bots (welcomed, not blocked)

### Philosophy

This is **90% security with 10% complexity**. It's not bulletproof, but it:
- Deters casual cheating
- Allows legitimate strategy sharing
- Maintains player privacy
- Enables community collaboration

---

## References

**Full Documentation**:
- Complete Implementation: `docs/VERIFICATION_INTEGRATION_COMPLETE.md`
- Technical Spec: `docs/CUMULATIVE_HASH_VERIFICATION.md`
- Policy Decisions: `docs/POLICY_FINALIZED.md`
- Implementation Log: `docs/IMPLEMENTATION_LOG_VERIFICATION.md`

**Code References**:
- Core System: `godot/autoload/verification_tracker.gd`
- Tests: `godot/tests/unit/test_verification_determinism.gd`

---

**Last Updated**: November 20, 2024
**Status**: ✅ Client-side complete
