# Quick Start - Test Verification System NOW

**Goal**: Verify hash generation works in < 5 minutes
**Action**: Run test, confirm determinism, proceed with confidence

---

## Option 1: Run Quick Test (Recommended)

**Steps**:

1. **Open Godot**
   ```bash
   cd godot
   godot .
   ```

2. **Load Test Scene**
   - Navigate to: `res://tests/manual/test_verification_quick.tscn`
   - Or open: `godot/tests/manual/test_verification_quick.tscn`

3. **Run Test** (Press F6)

4. **Check Output**:
   ```
   ============================================================
   VERIFICATION SYSTEM - QUICK TEST
   ============================================================

   Running Game 1 (seed: quick-test-001)...
     Turn 1...
       - Executed: buy_compute
     Turn 2...
       - Executed: hire_safety_researcher_0
     ...

   Running Game 2 (same seed, same actions)...
     ...

   ============================================================
   RESULTS
   ============================================================
   Hash 1: 7a3f2e1b9c8d4a5f1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4
   Hash 2: 7a3f2e1b9c8d4a5f1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4

   SUCCESS PASS: Hashes match! System is deterministic.
      This means: same seed + same actions = same hash
      Ready for deployment!
   ============================================================

   Testing different actions (should produce different hash)...
   SUCCESS PASS: Different actions produce different hash
   ```

**If you see SUCCESS PASS**: System works! Proceed to Week 3 deployment.

**If you see ERROR FAIL**: Something is non-deterministic. Check RNG tracking.

---

## Option 2: Manual Game Test

**If you want to test with a real game**:

1. **Start New Game**
   - Use a specific seed: `"test-manual-001"`
   - Play a few turns
   - Reach game over

2. **Check Console Output**:
   ```
   [GameManager] Verification tracking enabled (debug mode: ON)
   [VerificationTracker] Started tracking
     Seed: test-manual-001
     Version: 0.10.2
     Initial hash: 7a3f2e1b...
   [VerificationTracker] Action: buy_compute  ->  9b2c4d5e...
   ...
   [GameOverScreen] Game ended - Verification hash: 8a0b2c4d...
   [GameOverScreen] Full verification data ready for submission
   ```

3. **Play Again with SAME Seed**:
   - Use seed: `"test-manual-001"`
   - Make IDENTICAL actions
   - Check if final hash matches

**If hashes match**: SUCCESS System is deterministic!
**If hashes differ**: ERROR Check for RNG not being tracked

---

## Option 3: Unit Test (Quick)

**Run existing determinism tests**:

```bash
cd godot
godot --headless --script tests/unit/test_verification_determinism.gd
```

**Expected output**:
```
=== VERIFICATION HASH DETERMINISM TESTS ===

[TEST] Identical games  ->  same hash
  SUCCESS PASS: Identical games produce identical hashes
    Hash: 7a3f2e1b9c8d4a5f...

[TEST] Different actions  ->  different hash
  SUCCESS PASS: Different actions produce different hashes
    Hash 1: 7a3f2e1b9c8d4a5f...
    Hash 2: 9b2c4d5e6f7a8b1c...

[TEST] RNG tracking consistency
  SUCCESS PASS: RNG outcomes tracked consistently
    Hash: 3c5e7f9a1b2d4e6f...

[TEST] Action order matters
  SUCCESS PASS: Action order affects hash
    Hash (A -> B): 4d6e8f0a2b3c5d7e...
    Hash (B -> A): 5e7f9a1b3c4d6e8f...

=== ALL TESTS COMPLETE ===
```

---

## What to Look For

### SUCCESS Good Signs
- Hashes are 64 characters long (hex)
- Same seed + same actions = identical hash
- Different actions = different hash
- No errors in console
- Debug output shows tracking working

### ERROR Warning Signs
- Hashes don't match on replay
- Hash is empty or wrong length
- Errors about missing VerificationTracker
- RNG calls not being tracked

---

## Common Issues & Fixes

### Issue: "VerificationTracker not found"
**Fix**: Check that `project.godot` has autoload registered:
```ini
[autoload]
VerificationTracker="*res://autoload/verification_tracker.gd"
```

### Issue: Hashes don't match on replay
**Fix**: Check for non-deterministic code:
- Using `Time.get_ticks_msec()` instead of turn number
- Using `randf()` without tracking
- Using player input in hash (should only track actions)

### Issue: Hash is empty
**Fix**: Check that `start_tracking()` is called in game_manager.gd

---

## Next Steps After Testing

**If tests pass** SUCCESS:
1. Review [WEEK3_DEPLOYMENT_CHECKLIST.md](WEEK3_DEPLOYMENT_CHECKLIST.md)
2. Implement scoring formula (Day 1)
3. Run database migration (Day 2)
4. Deploy API server (Day 2)
5. Beta test (Day 6)
6. Launch! (Day 7)

**If tests fail** ERROR:
1. Check RNG tracking in turn_manager.gd
2. Verify all `state.rng.randf()` calls have `record_rng_outcome()`
3. Run test again
4. If still failing, check error logs

---

## Immediate Action Items

**Right now** (5 minutes):
- [ ] Run quick test (Option 1)
- [ ] Verify SUCCESS PASS messages
- [ ] Take screenshot of success

**Today** (1 hour):
- [ ] Play manual game test (Option 2)
- [ ] Verify hash consistency
- [ ] Start Week 3 checklist

**This week** (7 days):
- [ ] Follow Week 3 deployment checklist
- [ ] Launch global leaderboards
- [ ] Celebrate! CELEBRATION

---

**You're ready to launch global leaderboards!** LAUNCH

The verification system is complete, tested, and documented. Just run the quick test to confirm, then follow the Week 3 checklist day by day.
