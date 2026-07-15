# Shutdown-Hygiene & Silent-Error Audit — 2026-07-16

Lane: shutdown-hygiene & silent internal Godot errors. Godot 4.5.1 stable, headless.
Branch `qa/shutdown-hygiene`. Investigate-and-report: unambiguous low-risk issues fixed with
proof; everything needing judgment documented, not guessed.

## How this was reproduced

- **Clean shutdown leak dump:** `godot --headless --verbose --quit-after N` boots the real main
  scene (`welcome.tscn` + all autoloads) and quits cleanly after N frames, so Godot's end-of-run
  `ObjectDB` / `RID` / resource leak checks actually fire (a killed/timed-out process does NOT
  run them). `N=120` (~2 s) lands mid-boot-crossfade; `N=400` lands after it settles.
- **Gameplay-path silent errors:** the L1 month sweep (`tests/manual/test_l1_month_sweep.gd`,
  72 runs driving plan→commit→day-tick playback→windows→boundary→death) plus the full
  `tests/unit` GUT suite, both with stderr captured and grepped for
  `push_error`/`SCRIPT ERROR`/`Nonexistent`/`Invalid`/`leaked`/`Orphan`.

## Findings (ordered by severity)

| # | Symptom | Owning file:line | Root cause | Severity | Status |
|---|---------|------------------|------------|----------|--------|
| 1 | 4 orphan Nodes leak per game instance (`game_state.gd`, `doom_system.gd`, `risk_pool.gd`, `turn_manager.gd`) — GUT orphan monitor prints "8 Orphans" after two games | `scripts/game_manager.gd:43` (`start_new_game`) and `:630` (`load_saved_game`) | `GameState`/`DoomSystem`/`RiskPool`/`TurnManager` all `extends Node` but are **never added to the scene tree**, so reassigning `state`/`turn_manager` orphans them. `start_new_game` freed nothing; `load_saved_game` freed only `state`, leaving its `doom_system`/`risk_system` and the old `turn_manager`. GameManager is an autoload persisting the whole process, so every restart / "play again" / load accumulates 4 leaked Nodes for the rest of the session. | **real-bug** (mid-session, accumulating) | **FIXED** + regression test |
| 2 | `ObjectDB instances leaked at exit` + `2 resources still in use at exit`: a running `Tween`, `AudioStreamPlaybackMP3`, and the two MENU `AudioStream`s | `autoload/music_manager.gd` `_crossfade_to_track` (`await tween.finished`) | Autoload had no shutdown cleanup. If quit lands during the ~2 s boot crossfade, the coroutine suspended at `await tween.finished` keeps the `Tween` + the `new_stream` local alive; the players still hold their playbacks. | **cosmetic** (at-exit only; OS reclaims; does NOT accumulate mid-run — each crossfade completes and releases normally) | **PARTIALLY FIXED** — see note |
| 3 | `stop_music()` fails to stop an in-flight crossfade | `autoload/music_manager.gd` `stop_music()` (was `get_tree().create_tween().kill()`) | Created a *fresh* tween and killed that instead of the real crossfade tween (which wasn't stored) — a no-op. Disabling music mid-crossfade left the crossfade running. | hygiene (minor, mid-run) | **FIXED** |
| 4 | Headless GUT floods stderr with `SCRIPT ERROR: Parse Error: Identifier "FinanceEngine" not declared` (86×), `"FlightRecorder" not declared`, and `Nonexistent function 'get_all_actions'/'get_action_by_id'/'execute_action' in base 'GDScript'` — including a real backtrace at `turn_manager.gd:534` | environmental (Godot global class cache), not a code defect | Every one of those identifiers **is** declared (`finance_engine.gd:1`, `flight_recorder.gd:2`, `actions.gd:142/146/212`). The running game boots clean (only Finding #2 appears) and the sweep produces coherent evolving state, i.e. the statics resolve fine at runtime. This is the known "fresh-worktree headless GUT class-cache" gotcha: `--import` does not warm `global_script_class_cache.cfg` the way opening the editor once does, so GUT's dynamic per-script loads intermittently fail to resolve `class_name` references. | environmental / needs-verification | **Documented** (see recommendation) |
| 5 | GUT reports "3 / 4 / 8 Orphans" on various tests | test scripts (e.g. `test_replay_verification.gd`) | Tests instantiate `GameState`+subsystems and don't free them (the same 4-Node shape as Finding #1 — the manual sweep already works around it by calling `.free()` explicitly). Test-code hygiene, not shipped code. | test hygiene | Documented |

## Fixes applied

### Finding #1 — GameManager leaks the previous game's Node subsystems (REAL, the headline)

`scripts/game_manager.gd`: added `_release_game_objects()` which `queue_free()`s the old
`state`, its orphaned `doom_system` + `risk_system`, and the old `turn_manager`, each guarded by
`is_instance_valid`. Called at the top of `start_new_game` (after stopping month playback) and in
`load_saved_game` in place of the old partial `state.queue_free()`.

Safety verified before writing: every external reader reaches these subsystems through
`state.doom_system` / `st.doom_system` (re-fetched from the current state, never cached across a
reset — confirmed by grepping `ui/`, `debug/`, `core/`), so no live reference survives the swap.
`Ledger` and `MonthController` are `RefCounted` and free themselves. `queue_free()` (deferred) is
safe on these off-tree nodes and avoids invalidating an in-flight month-playback tick mid-frame.

**Proof** (`tests/unit/test_game_lifecycle_hygiene.gd`): two consecutive `start_new_game` calls,
asserting the global orphan-node count does not grow across the second call.
- Fix disabled: `orphan delta=4` → **FAIL** (exactly state+doom+risk+turn_manager).
- Fix enabled: `delta <= 0` → **PASS** (`1/1 passed`).

### Finding #3 — stop_music no-op (FIXED)

Now stores the crossfade tween in `_crossfade_tween` and `stop_music()` kills the real one.

### Finding #2 — MusicManager shutdown leak (PARTIALLY FIXED)

Added `_exit_tree()` that kills `_crossfade_tween` and clears both players' streams, and tracks
the crossfade tween. **Verified:** quitting while music is settled (`--quit-after 400`, after the
boot crossfade completes) now produces **zero** leaked instances / resources — previously it
leaked regardless of timing.

**Residual (left for Pip — judgment call):** if quit lands *inside* the ~2 s boot crossfade
(`--quit-after 120`), the leak persists. Root cause is structural: `_crossfade_to_track` suspends
on `await tween.finished`; a killed tween never emits `finished`, so the coroutine stays suspended
holding the `Tween` and `new_stream`. `_exit_tree` cannot resume a coroutine. Fully closing it
means restructuring the crossfade to a one-shot `tween.finished.connect(...)` callback (no
suspended coroutine) — a refactor of audio behaviour I did not ship unreviewed under a hygiene PR,
since it is cosmetic (at-exit, OS-reclaimed, non-accumulating) and headless can't verify the audio
still sounds right. **Recommendation:** de-coroutine the crossfade, or add an explicit
"is this crossfade still valid" guard after the await.

Secondary observation feeding #2: `welcome_screen.gd` calls `MusicManager.play_context(MENU)`
**twice** (lines 29 and 77), which forces an unnecessary crossfade at boot — the exact window that
produces the reported "mid-crossfade teardown" leak. Collapsing that to one call would also shrink
the leak window. Left for Pip (UI-flow judgment).

## Recommendations (not fixed — need judgment / are environmental)

- **Finding #4 / issue #629 (hollow CI):** the headless GUT run emits ~150 `SCRIPT ERROR` lines
  from class-cache resolution that are *not* real defects but *do* bury any genuine error and make
  a green/red read unreliable. Recommend: warm `global_script_class_cache.cfg` (open the project in
  the editor once, or add a cache-priming step) before the headless GUT run in CI, then treat
  residual `SCRIPT ERROR`/`push_error` as failures. This is a prerequisite for trusting the suite.
- **Finding #5:** give the sim tests a teardown that frees `GameState` + `doom_system` +
  `risk_system` + `turn_manager` (mirror the manual sweep's explicit `.free()`), removing the
  orphan noise.

## The single most important finding

**Finding #1.** It is the only *accumulating mid-run/mid-session* leak: 4 Nodes per game, unbounded
across a session of restarts/loads (a real bite for the now-many-minute calibrated sessions and
"play again" loops), and it explains the "resources left running at the end" impression far better
than the music leak. The MusicManager leak (Finding #2), by contrast, is a single at-exit snapshot
that the OS reclaims and never accumulates during play.

## Verification status

- `test_game_lifecycle_hygiene.gd`: 1/1 pass (and demonstrably fails without the fix).
- `--quit-after 400` after fix: zero leaks/resources-in-use.
- No `.import` files are included in this change (worktree import churn excluded from the commit).
