# Playtest Readiness Check — 2026-07-15

**Branch checked:** `playtest-readiness` (built from `origin/main` @ `74074c8`, the tip after
the merge stack: L1 month engine #636, calibration #638, flight-recorder/burnout #639,
honest CI #640, L5 finance #641, nine-stream doom #643).

**Verdict: GREEN. Nothing blocking tomorrow's human playthroughs.**

## 1. Launch smoke

`godot --headless --path godot --quit` (fresh worktree, after the required `--import` pass).

- All 15 autoloads (ErrorHandler, GameConfig, Balance, SceneTransition, ThemeManager,
  NotificationManager, KeybindManager, ScreenshotManager, LogExporter, IconLoader,
  MusicManager, VerificationTracker, EventService, GameManager, Achievements) resolved
  and initialized cleanly.
- EventService loaded and transformed 1194 bundled events with no errors.
- Main scene (`res://scenes/welcome.tscn`) loaded, WelcomeScreen initialized, music
  context switched with no errors.
- Grepped the log against CI's own failure signature (`Cannot load source code|GDScript
  error|Parse error|Failed to load script|Failed loading resource:.*\.gd`) — zero matches.
- Only noise at shutdown: `WARNING: ObjectDB instances leaked at exit` and `1 resources
  still in use at exit` — both from `--quit` tearing down an in-flight audio crossfade
  (MusicManager was mid-transition). Cosmetic; not a startup/gameplay defect.

## 2. Play-a-month smoke

Ran `tests/unit/test_month_button_path.gd::test_end_month_button_path_plays_a_full_month`
(the exact End Turn -> `game_manager.end_month()` -> `MonthController` playback path a
human clicking End Turn will exercise). Result: **PASS** (0.27s).

Confirmed via the test's own assertions:
- Committing the month plan (pass action) hands control to month playback.
- Day-tick playback runs and reaches the month boundary without the run dying (doom
  held at a survivable level by the test harness so the *wiring*, not balance, is what's
  under test).
- A response window surfaces and resolves round-trip (`event_triggered` ->
  `resolve_event`).
- The month review dialog surfaces at the boundary with the expected title.
- `month_controller.month_open_pending` holds the boundary open for the next plan phase.
- >=15 workday ticks played out (a full calendar month).
- Closing the review (`begin_planning`) returns to `ACTION_SELECTION` phase with
  `can_end_turn` true — the loop closes: plan -> play -> review -> plan.

## 3. Cross-system sanity

Not driven live end-to-end (out of scope per the ask — "does it run without erroring"),
but each system's own direct-API test suite passed, and the call sites were checked by
hand for wiring gaps:

- **Nine-stream doom (#643):** `tests/unit/test_doom_system.gd` (33 tests) and
  `tests/unit/test_doom_breakdown.gd` (8 tests) all pass — baseline/overhang/absorption/
  alarm stream math, momentum clamping, trend classification, breakdown-entry
  sort/label/sign logic, JSON round-trip. All green.
- **Finance offers (#641, `seek_financing`):** `tests/unit/test_finance_engine.gd`
  (23 tests) all pass — offer pricing determinism, reputation/leverage/org-type pricing,
  philanthropy gating, desperation fallback, offer generation menu size/liveness,
  accept/pay/default paths, JSON round-trip. Hand-checked the action handler
  (`godot/scripts/core/actions.gd:384`, `"seek_financing"` case) — it's a thin call-through
  to `FinanceEngine.context_from_state` / `generate_offers`, the exact APIs the unit
  suite exercises directly, so no wiring gap between the tested engine and the action
  a player triggers.
- **Flight recorder (#639, F9):** `tests/unit/test_flight_recorder.gd` (9 tests) all
  pass — F9 keybind registration, `flight_recorder_requested` signal emission, state
  snapshot building (incl. null-state guard) and JSON round-trippability, marker/manifest
  formatting.

## 4. Fast unit gate (CI-equivalent)

Ran exactly what CI runs: `python scripts/run_godot_tests.py --quick --ci-mode
--min-tests 300` (targets `tests/unit`, excludes the slow `tests/simulation` subdir).

```
[PASS] 'quick': 345 tests, 0 failures, 36/36 files collected.
[SUCCESS] All requested suites passed the gate!
```

345 tests / 36 files, 0 failures, 0 files silently dropped by GUT (parse error / wrong
base class) — well above the 300-test floor.

## Blockers for tomorrow

None found. No code changes were needed — this branch is a read-only verification pass.

## What was NOT covered (by design, per scope)

- No literal mouse-driven UI walkthrough (headless only) — visual/layout regressions
  (button overlap, text clipping, theme glitches) are not ruled out by this check.
- Simulation-tests subdir (slow suite, ~3 min, `tests/simulation`) was not run — it's
  non-blocking in CI and out of scope for a fast readiness check.
- Cross-system interactions were checked at the unit-test level, not by driving a live
  scene through `seek_financing` / F9 during an actual running game session.
