# Phase-guard audit -- the CLASS behind #1134

Date: 2026-08-06. Branch: `audit/phase-guard-class`. Baseline: `origin/main` @ `78be0370`.

Commissioned by Pip after the #1134 release-build permalock:

> "removing the feature is correct but I think the phase guard thing is very good and we
> should think about if anything else in the game needs it?"

This is **not** about #1134. PR #1143 (retire the feature) is the ruled fix for the
instance. This document asks whether the same species of defect lives anywhere else.

**Headline answer:** the enumeration found **10** pieces of phase-critical state and **34**
mutation sites. Outside the three sites PR #1143 already deletes, there are **0** confirmed
reachable silent permalocks, **1** confirmed non-permalock defect (silent content loss in
the sim, reported not fixed), and **3** theoretical-but-unreached hazards. The count is
deliberately low; the reachability arguments that shrank it are written out below so they
can be attacked.

---

## 1. The mechanism, re-derived from source

Pip's brief named `turn_manager.gd:895` (`can_select_actions = pending_events.size() == 0`).
That line is real but it is **not** the lock -- it is a field in a returned Dictionary that
no shipped code reads (`grep can_select_actions` finds writers in `turn_manager.gd` and two
assertions in `tests/unit/test_turn_manager.gd`, and nothing else). The live lock is a
three-part interlock, all of which must hold:

1. **`GameManager.select_action` hard-refuses** while events are pending
   (`game_manager.gd:185`, `if state.pending_events.size() > 0: ... return false`), and
   again if `current_phase != ACTION_SELECTION` (`:195`).
2. **The drain path refuses too.** `TurnManager.resolve_event` returns
   `{"success": false, "error": "Cannot resolve events in phase %s"}` unless
   `current_phase == TurnPhase.TURN_START` (`turn_manager.gd:862`). The month-loop's
   alternative drain (`GameManager.resolve_event:1064`) only engages when
   `month_controller.is_paused()`.
3. **The modal cannot be dismissed.** `event_triggered` is presented by `EventDialog` at
   `ModalStack.PRIORITY_MUST_ANSWER` with a `MOUSE_FILTER_STOP` blocker; ESC deliberately
   refuses to close it (#452); and since the 2026-07-24 "direction-b" playtest change the
   dialog closes **only on a successful resolve** (`main_ui.gd:2057-2068`).

So the actual invariant is sharper than "do not write `pending_events`":

> **INVARIANT E.** `GameManager.event_triggered` may only be emitted when a resolution path
> can succeed -- that is, when `month_controller.is_paused()` **or**
> `state.current_phase == TurnPhase.TURN_START` **or** the event is the synthetic
> `MONTH_REVIEW_EVENT_ID` (which `resolve_event` short-circuits at `:1054`).
>
> **INVARIANT P.** `state.pending_events` may only be non-empty in a phase whose drain is
> live -- same two conditions.

Violate P alone and the player gets a mute run with no modal (annoying, sometimes
recoverable via COMMIT PLAN). Violate E and P together and the run is **dead**: the
unanswerable modal blocks the very button that would have recovered it. #1134 violated both
at once, which is why it read as a hard lock rather than a stuck button.

Worth recording, because it is the non-obvious half: **the escape hatch exists and is
covered up.** `_on_commit_plan_button_pressed` -> `plan_controller.commit_month()` ->
`GameManager.end_month()` appends `PASS_ACTION_ID` on an empty queue (`:696-701`), which
runs `advance_tick` -> `start_turn` -> `_step_begin_turn` -> `state.pending_events.clear()`.
A player who could click that button would have unlocked their own run. The modal blocker is
what makes the defect terminal.

---

## 2. Enumerated phase-critical state (the deliverable)

"Phase-critical" = the value gates a phase transition, or gates the player's ability to act.

| # | Variable | Owner | What it gates | Mutation sites |
|---|---|---|---|---|
| 1 | `state.pending_events` | `GameState:239` | `select_action` refusal; `resolve_event` drain; `can_select_actions` | 13 |
| 2 | `state.current_phase` | `GameState:238` | `select_action` refusal; `resolve_event` refusal; `end_turn` warning | 9 |
| 3 | `state.can_end_turn` | `GameState:240` | **nothing** -- see D3 | 9 |
| 4 | `state.queued_actions` | `GameState:251` | `end_turn` refusal; `end_month` pass-fallback; `execute_turn` input | 13 |
| 5 | `MonthController.status` | `month_controller.gd:32` | `advance_tick` early-return; `resolve_current_window*`; `GameManager.resolve_event` routing | internal only |
| 6 | `MonthController.window_queue` | `:27` | drives (5) via `is_paused()`; mirrored into (1) by `_sync_pending` | internal + `conference_trip` reads |
| 7 | `MonthController.month_open_pending` | `:42` | whether the boundary tick holds open as the plan phase | internal + `conference_trip` reads |
| 8 | `GameManager.month_playback_active` | `game_manager.gd:20` | `end_month` re-entry guard; playback loop condition | internal only |
| 9 | `state.game_over` | `GameState:196` | playback loop exit; every control disabled at `main_ui.gd:1229` | 4, all in `game_state.gd` |
| 10 | `PlanController.queued_actions` (UI mirror) | `plan_controller.gd:30` | `end_turn_button.disabled`, `undo`/`clear` enablement | 7, all in `plan_controller.gd` |

Two derived observations that fell out of the enumeration and matter more than any
individual writer:

- **(5)-(8) have no writers outside their owning file.** `MonthController` and
  `GameManager` keep their phase state private by convention already. That is why the
  audit's confirmed count is low: the newer L1 month machine was built with this discipline;
  the older `GameState`-public fields (1)-(4) were not.
- **(10) is a mirror of (4) with no enforced coupling.** `needs_pass_fallback()`
  (`plan_controller.gd:122`) exists precisely because they can diverge ("phantom UI tiles").
  A divergence where the mirror is empty and the backend is not disables COMMIT THE MONTH
  (`main_ui.gd:1359, 2033`) -- a soft-lock with a different generator from #1134. It is
  netted today, but the net is a patch on a missing invariant, not the invariant.

---

## 3. Writers, classified, with the reachability call

### 3.1 CONFIRMED reachable, silent permalock -- 3 sites, all already being deleted

| Site | Class | Guard | Reachable in a bad phase? |
|---|---|---|---|
| `debug_overlay.gd:445` `gm.state.pending_events.append(event)` | dev/debug surface | null-check only | **YES.** Overlay instanced unconditionally in `main.tscn`, F3 keybind unconditional in `_ready`. Fires from the plan phase where `current_phase == ACTION_SELECTION`. |
| `debug_overlay.gd:449` `gm.emit_signal("event_triggered", event)` | dev/debug surface | none | **YES.** Violates INVARIANT E -- this is the line that makes it terminal rather than merely stuck. |
| `dev_mode_overlay.gd:485` `gm.state.pending_events.append({...})` | dev/debug surface | null-check only | **YES.** Reachable in release via `BuildInfo.are_alpha_tools_available()` (deliberate, #1079/#1104). |

All three are removed by **PR #1143**, which is the ruled fix. Nothing here duplicates that
work; they are listed because the guard in section 5 is proven red against exactly these
lines.

**Confirmed-reachable permalocks introduced by anything OTHER than #1143's three sites: 0.**

### 3.2 CONFIRMED defect, not a permalock -- 1 site. REPORT ONLY (simulation).

**D1 -- `TurnManager._step_check_events:541` silently discards scheduled event injections.**

```
state.pending_events = triggered_events   # whole-array REPLACE, not append
```

`start_turn` runs `_step_begin_turn` (clears `pending_events`), then
`_step_apply_scheduled_causes` -> `SeedSchedule._apply_cause` -> `inject_event` **appends**
`{"id": target, "scheduled": true}` (`seed_schedule.gd:56`), then `_step_check_events`
**overwrites the whole array**. So a scenario-authored `inject_event` cause is destroyed
whenever a random event happens to fire the same turn, and survives only when none does.

Severity: silent content loss, not a lock. The authored beat simply never happens and
nothing says so. This is squarely the repo's documented failure mode ("silent wrongness").

**Not fixed here.** Changing it alters which events fire on a given seed, which forks every
recorded replay and moves league outcomes. That is Pip's call, per the brief. The one-line
shape of the fix (`append_array` instead of `=`, plus deciding ordering) is deliberately not
applied.

Second-order note on the same site: even when the injection survives, in the month path it
is drained at `month_controller.gd:99-100` and routed through `_dispatch` -> `EventTiers.partition`.
A bare `{"id": ..., "scheduled": true}` dict carries no `delivery_tier`, so it will not
partition as a window. Whether it resolves at all is worth a separate look; also sim-touching,
also not fixed.

### 3.3 THEORETICAL -- 3 hazards, no production route found

**T1 -- save/load can in principle rehydrate into the #1134 state.**
`GameState.from_dict` restores both `current_phase` (`:1549`) and `pending_events`
(`:1554-1557`). `MonthController.rehydrate_from_state` (`:378-387`) then rebuilds
`window_queue` from `pending_events` but **filters on `EventTiers.is_window(ev)`** and never
clears the non-window remainder. A save carrying a non-window pending event plus
`current_phase == ACTION_SELECTION` would load into: `status = READY` (so `resolve_event`
routes to `TurnManager`), `pending_events` non-empty (so `select_action` refuses), and
`game_manager.gd:1030-1034` emitting `event_triggered` for it -- an unanswerable modal.
Identical outcome to #1134, via the load path.

Why it is theoretical, not confirmed: the only writer of `pending_events` in a savable
moment is `_sync_pending`, which writes **windows only**; the month loop clears
`pending_events` every tick at `:100`; and the modal blocks saving while a legacy TURN_START
event is open. Post-#1143 I found no route that produces such a save from a current build.
It remains reachable from **an old save file or a hand-edited one**, and it is one defensive
line from impossible (on load, if `pending_events` is non-empty and `window_queue` came back
empty, force `current_phase = TURN_START` so the drain works). Not applied: it changes
loaded-run behaviour and belongs with a decision about save-version compatibility.

**T2 -- `plan_controller.append_reserve_all:146` writes the backend queue with the
validation bypass stated in its own comment** ("bypass select_action validation"). It is a
UI file mutating phase-critical state (4) with no phase check. It is **not** a defect, and
the reason is the useful generalisation: *direction matters.* Writers that **add** to
`pending_events` lock the run; writers that **add** to `queued_actions` unlock it (they make
`end_month` viable). `append_reserve_all` can only ever move the run toward being playable.
Allowlisted with that argument attached, not with a shrug.

**T3 -- `state.can_end_turn` is a dead gate.** Written at 9 sites across three core files,
read by **zero** consumers: `turn_manager.gd:50` and `:896` put it in returned Dictionaries
nobody inspects; `game_state.gd:1450/1550` serialise it. The End Turn button consults
`plan_controller.is_queue_empty()` instead. Today that is harmless. The hazard is that it
*looks* authoritative: the next person to write `if state.can_end_turn:` will be reading a
value that is correct only by accident, and it has been out of the execution path long
enough that nothing would notice if it drifted. Cheapest honest fixes, in preference order:
delete it, or add a test asserting it agrees with the real gate. Neither applied here --
deletion touches the save schema.

### 3.4 Writers cleared with an argument

- **`SeedSchedule._apply_cause:56`** (core sim) -- only ever called from
  `_step_apply_scheduled_causes`, which is step 2 of `start_turn`, which the month loop drains
  at `:100` in the same call. Phase-safe by construction.
- **`ConferenceTrip:253` (`queued_actions`) and its window drain at `:305`** -- drives the
  controller through its own API (`skip_current_window`, `is_paused`) and deliberately
  **cuts the trip short** on an unignorable window rather than force-resolving it
  (`_drain_windows_while_away`). This is the only non-`GameManager` caller of the month
  machine and it is the best-behaved writer in the audit; it is the model the mechanism in
  section 5 should be measured against.
- **`baseline_simulator.gd:254`, `replay_simulator.gd:84-89`** -- headless simulators that
  own their own loop and drain `pending_events` themselves before advancing. No UI, no modal,
  no phase to be wrong about.
- **`GameManager.end_turn()` (`:513`)** -- carries a phase check that only *warns* (`:536`).
  Cleared because it is **dead in the shipped path**: `grep '\.end_turn()'` across
  `scripts/` and `autoload/` returns nothing outside tests. The button routes to
  `end_month()`. Comment at `:624` says so explicitly. Worth deleting eventually; not a
  defect.
- **`state.game_over` and `GameManager.is_initialized`** -- no writers outside their owning
  file. Nothing to audit.

---

## 4. Severity ranking, by what the player experiences

1. **Silent permalock** (no error, run dead, leaderboard entry lost): the 3 sites in 3.1.
   Being removed by #1143. Nothing else in the tree reaches this tier today.
2. **Silent content loss** (authored beat never fires, nothing says so): D1. Real, live,
   sim-touching, reported not fixed.
3. **Soft-lock via mirror divergence** (COMMIT THE MONTH disabled while the backend queue is
   non-empty): netted by `needs_pass_fallback()`; the net is the only thing standing between
   state (4) and state (10).
4. **Latent wrongness** (a gate that reads authoritative and is not): T3.
5. **Load-path hazard**: T1, no current production route.

---

## 5. The mechanism: what to install, and what each choice MISSES

Four candidates were weighed. Judged on: does it catch a *new* writer written by someone who
has not read this document?

| Option | Catches | Misses | Cost |
|---|---|---|---|
| **A. Shared assertion helper** callers must call (`PhaseGuard.assert_can_queue_event(state)`) | Mistakes by callers who remember to call it | Everything written by someone who does not call it -- which is exactly the population that caused #1134. Opt-in guards guard the already-careful. | low |
| **B. Phase-aware setter, raw field made private** (`state.queue_event(ev)` gating on phase) | All writes, structurally -- the strongest option on paper | GDScript has no `private`; enforcement collapses back to a source scan. Also: ~34 call sites to migrate, several in `turn_manager`/`replay_simulator` whose write ORDER is the deterministic RNG stream (`start_turn` docstring: "STEP ORDER IS LOAD-BEARING"). High replay-fork risk for a refactor whose enforcement is still a scan. | high |
| **C. Test-time scanner over an audited allowlist** (the #1143 shape, generalised) | Any NEW file that starts writing phase-critical state, or emits `event_triggered` -- fails in CI with a pointer to the reachability argument | Cannot prove an *allowlisted* file is phase-safe. Cannot see runtime reachability at all. Blind to a violation routed through an alias (`var s = state; s.pending_events.append(...)`) or through `set()`. | low |
| **D. Documented invariant only** | Nothing, mechanically | Everything. Documentation is what already existed -- `game_manager.gd:171` says "FIX #418: Block if events pending" and #1134 still shipped. | ~0 |

**Recommendation: C, installed now (done -- see section 6), with B recorded as the real fix
and explicitly deferred.**

The argument for C over B is not that C is better. B is better. C is what can be installed
today without touching the deterministic step order, and its failure mode is *loud and in
CI* rather than *silent and in a release build*. The argument against A is the sharper one
and generalises past this repo: **an opt-in guard is guarded by the discipline it is meant to
replace.** `debug_overlay.gd:435` already had a guard -- `if not gm or not gm.state: return`.
The author was guarding. They guarded the wrong variable. A helper they must remember to
call would have been skipped by the same reasoning that produced the null-check.

**What C misses, stated plainly so it is not mistaken for coverage:**

- It cannot tell a *safe* write from an *unsafe* one inside an allowlisted file. `turn_manager.gd`
  is allowlisted, and D1 (section 3.2) is a real defect inside it. **The scanner is green on
  a live bug.** That is the honest boundary of this mechanism.
- It is a static scan: an alias, a `call()`, a `set("pending_events", ...)`, or a write from
  a `.tscn`-embedded script all pass through it.
- The allowlist is a *permissive superset*. It does not assert that an allowlisted file still
  writes, so it will not notice a #1143-style removal regressing. (#1143 ships its own guard
  for that; the two are complementary, not redundant.)
- It is only as good as the reachability arguments in section 3, which are my reading of the
  code, not proofs.

A **runtime** invariant check (`push_error` when `pending_events` is non-empty while
`current_phase == ACTION_SELECTION` and the controller is not paused) was prototyped and
**rejected**: that exact combination occurs legitimately inside `advance_tick`, between
`start_turn` returning with a `SeedSchedule` injection and `:100` clearing it. A guard that
false-fires in normal play trains people to ignore it, which is worse than no guard. Making
it correct means threading a "settled state" concept through the tick, which is option B's
work by another name.

---

## 6. What was installed, with red/green proof

`godot/tests/unit/test_phase_critical_state_guard.gd` -- 7 tests:

1. `test_scan_actually_reads_the_source_tree` -- backstop: >100 `.gd` files found, and the
   two files that own the gates are among them. The #640 lesson: a scan that scans nothing
   passes vacuously.
2. `test_scanner_finds_the_known_core_writers` -- the regex still matches real code.
3. `test_scanner_finds_the_known_offender_shape` -- literal must-catch / must-ignore lines,
   including `gm.state.pending_events.append(event)` verbatim. **This test exists because the
   first draft of the guard was hollow** (below).
4. `test_only_audited_files_mutate_phase_critical_state` -- the allowlists from section 3.
5. `test_event_triggered_is_emitted_only_from_audited_files` -- INVARIANT E.
6. `test_resolve_event_still_refuses_outside_turn_start` -- fails if the drain-path refusal
   that this whole audit rests on is ever relaxed, so the allowlists cannot quietly end up
   guarding a rule that no longer holds.
7. `test_select_action_still_refuses_on_pending_events` -- same, for the `select_action` gate.

### The guard was hollow on its first run, and that is the useful part

First draft compiled, ran, and reported **1 failure** -- looking, at a glance, like a working
guard. It was not. The receiver regex excluded a preceding `.`, so
`gm.state.pending_events.append(event)` -- *the actual #1134 line* -- matched **nothing**.
The allowlist test passed green with the offenders removed from the allowlist. Only the
`event_triggered` check (a different regex) fired, which is what made the discrepancy
visible. Fixed, and test 3 above now pins the shape so it cannot recur. A guard that has
never been proven against the live defect is not evidence -- this one nearly proved the point
against itself.

### Measured runs

All via `python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300`.

**Baseline, before any change** (`origin/main` @ `78be0370`):

```
[PASS] 'quick': 1146 tests, 0 failures, 112/112 files collected.
```

**RED** -- guard present with the two `PENDING_REMOVAL_1143` allowlist entries and the
`debug_overlay` emitter entry temporarily removed, i.e. run against the live #1134 defect:

```
[FAIL] 'quick': 1153 tests, 2 failures, 113/113 files collected.
```

```
test_only_audited_files_mutate_phase_critical_state
  res://scripts/debug/debug_overlay.gd:445 mutates state.pending_events -- gm.state.pending_events.append(event)
  res://scripts/debug/dev_mode_overlay.gd:485 mutates state.pending_events -- gm.state.pending_events.append({"id": event_id, "scheduled": true})

test_event_triggered_is_emitted_only_from_audited_files
  res://scripts/debug/debug_overlay.gd:449 -- gm.emit_signal("event_triggered", event)
```

All three #1134 sites named unprompted, from an enumeration built before the offenders were
looked at.

**GREEN** -- tombstone entries restored (they are legitimate on this base; #1143 deletes the
code, and the allowlist is permissive so that merge stays green):

```
[PASS] 'quick': 1153 tests, 0 failures, 113/113 files collected.
```

1146 -> 1153 = +7, matching the 7 new tests. 112 -> 113 files = +1, matching the one new file.

---

## 7. Follow-ups this audit did not do

| Item | Why not | Whose call |
|---|---|---|
| D1: `_step_check_events` clobbering scheduled injections | Changes which events fire on a seed -> forks replays, moves league results | Pip |
| T1: force `TURN_START` on load when pending events survive rehydrate | Changes loaded-run behaviour; belongs with save-version policy | Pip |
| T3: delete `state.can_end_turn` | Touches the save schema | Pip |
| Delete dead `GameManager.end_turn()` | Unreferenced outside tests; simulation-tier tests exercise it | Pip |
| Remove the two `PENDING_REMOVAL_1143` allowlist entries | Only after PR #1143 merges | whoever merges #1143 |
| Option B (phase-aware setters) | ~34 sites, load-bearing step order, replay-fork risk | Pip |
