# What "paused" means in P(Doom)1

The written statement #1343 asked for. Scope and history: `docs/PAUSE_SEMANTICS_SWEEP.md`
(the measurement that opened the sweep) and #1341 (the bug that shipped). This file is
the rule; the sweep doc is how we got here.

Status: written by the pdoom1 seat for #1343; accepted by Pip on 2026-10-30 ("1360 seems
good to go"). The diagnostic-controls row stays undecided (#1028 option B).

RULING: 2026-10-30 -- "paused" means the player has stepped out of the game: simulation, gameplay input, animations and on-screen messages stop; only the pause menu, what it controls, music, scene transitions and capture/diagnostic tools keep running -- flavour: pause-semantics -- mechanism: tools/check_pause_timers.py

## Two different pauses -- do not confuse them

1. **The game-level pause.** A `window`-tier event stops month playback and asks for a
   decision (ARCHITECTURE.md section 2). That is game logic, inside the simulation, and
   is NOT what this document is about.
2. **The tree pause.** `SceneTree.paused = true`. Set in exactly one place --
   `pause_menu.gd` `show_pause_menu()`, reached by ESC in a live run -- and cleared on
   every way out of that menu. This document is about this one.

## The definition

> **Paused means the player has stepped out of the game. Nothing the player would
> otherwise have to watch, read or react to may move. Only the pause menu itself, the
> things the pause menu controls, and the tools for reporting what is on screen keep
> running.**

Expanded, by layer:

| Layer | While paused | Why |
|---|---|---|
| **Simulation / game clock** -- day ticks, turn advance, anything that mutates `GameState` | **STOPS** | The whole point. #1341: six day-ticks and a month boundary ran behind the menu on a shipped build. |
| **Gameplay input** -- MainUI shortcuts, action/plan clicks, dialog keys, in-game ESC-to-close | **STOPS** | The menu is modal. Gameplay surfaces are pausable, so the engine already drops their input. |
| **Presentation beats** -- in-run tweens, pulses, fanfare reveals | **FREEZE** | A frozen picture is the honest picture of a frozen game. Nothing awaits them across a pause, so freezing cannot deadlock. |
| **Messages meant to be read** -- toasts, error flashes, "report saved" lines | **FREEZE, lifetime included** | A message must not spend its lifetime behind the menu. The old default counted the clock but froze the slide, so a toast came back from the menu already dead. |
| **The pause menu** and what it controls -- volume, the music picker | **RUNS** | It is the thing being used. `pause_menu.tscn` is `PROCESS_MODE_ALWAYS`. |
| **Music** | **RUNS** | Pip opened the menu *to change the volume* (#1341). Music is a view-layer side effect with no state to freeze (ADR-0006); a crossfade must not freeze half-done. `MusicManager` is `ALWAYS`. |
| **Navigation** -- `SceneTransition` | **RUNS** | Infrastructure, not game. A fade awaited while paused must finish or ALL navigation dies for the session (#1034). And **a pause never survives a scene change**: the router unpauses before swapping, because no other scene hosts a pause menu that could unpause it. |
| **Diagnostics and capture** -- screenshot, log export, F3 readout toggle, flight recorder (F6), UI-evolution shot (F7) | **RUNS** | The pause menu is where you go when something looks wrong; it must not be the one state you cannot capture (#1028). |
| **Diagnostic controls that WRITE state** -- dev-overlay pokes, debug-overlay "add money"/"commit plan" | **undecided -- left paused** | They are gameplay writes wearing a diagnostic badge. Letting them run while paused is a conscious call, not a side effect; parked on #1028 (its option B). |
| **Network** -- leaderboard sync, update check | **RUNS** | Already `ALWAYS`; a request in flight should not stall because a menu is open. |

### The mechanical rules that follow

- **Nodes inherit `PROCESS_MODE_PAUSABLE`. That is the right default -- leave it.** A
  node that must keep running sets `process_mode = Node.PROCESS_MODE_ALWAYS` in
  `_ready()` *with a comment saying which row of the table above it belongs to*.
- **Tweens inherit the process mode of the node that created them.** Correct by
  construction for every row above, PROVIDED the node is in the right row. The one
  trap is an `ALWAYS` context awaiting a tween created on a pausable node (that is
  #1034's shape). No per-tween `set_pause_mode` is needed today.
- **`SceneTree.create_timer()` is the exception: its default points the WRONG way.**
  `create_timer(time_sec, process_always = true)` ignores the pause unless told
  otherwise. So every call passes the second argument explicitly: `false` (the house
  default -- stops while paused) or `true` with a comment saying which row justifies
  it. **Enforced by `tools/check_pause_timers.py`** (pre-commit + `guards.yml`, with a
  self-test that returns both answers).
- **`Timer` nodes** follow their node's process mode, like tweens. Not guarded.

## The inventory, re-measured on `origin/main` 20e41e12 (2026-10-29)

Commands, so the numbers can be re-run rather than trusted (from the repo root;
addons and tests excluded):

    grep -rn "create_timer(" godot --include=*.gd | grep -v addons/ | grep -v /tests/
    grep -rn "create_tween()" godot --include=*.gd | grep -v addons/ | grep -v /tests/
    grep -rnE "func _(input|unhandled_input|gui_input|unhandled_key_input|shortcut_input)\(" godot --include=*.gd | grep -v addons/ | grep -v /tests/
    grep -rn "mouse_filter" godot --include=*.gd --include=*.tscn | grep -v addons/ | grep -v /tests/ | wc -l
    grep -rn "process_mode" godot --include=*.gd --include=*.tscn | grep -v addons/ | grep -v /tests/

| Surface | #1343 said (2026-08-30) | Measured 2026-10-29 | Note |
|---|---|---|---|
| `create_timer` with no explicit 2nd arg | 9 | **11** | The issue's grep covered `godot/scripts/` only; `autoload/` adds `music_manager.gd` and `notification_manager.gd`. Plus 2 already explicit (#1341's fix). |
| `Timer` nodes | -- | **1** | `settings_menu.gd` save debounce. |
| `create_tween()` sites | 18 | **25** | Same reason: `autoload/` adds 8 (`scene_transition` x3, `notification_manager` x3, `music_manager` x2); 0 set a pause mode. |
| Input handler functions | -- | **27** in 24 files | `_input` 19, `_unhandled_input` 6, `_gui_input` 1, `_unhandled_key_input` 1. Button `pressed` signals are not counted: they arrive through the engine's own `_gui_input`, which a paused Control does not receive. |
| `mouse_filter` sites | 47 | **67** (50 `.gd`, 17 `.tscn`) | Not classified one by one -- see "Left for later". |
| explicit `process_mode` | -- | **4** | `pause_menu.tscn`, `music_manager`, `leaderboard_sync`, `update_check` -- all `ALWAYS`. |

### Which scenes can be paused at all

The tree is paused ONLY by `pause_menu.gd`, and `pause_menu.tscn` is instanced ONLY in
`main.tscn`. Every exit from the menu unpauses before navigating, and `SceneTransition`
now unpauses on any swap as well. So every node living in another scene -- welcome,
cold open, conference vignette, settings, keybinds, pregame, config confirmation,
credits, leaderboard, player guide, office sandbox, dev captures -- **cannot observe a
pause**. Those sites are classified *irrelevant*; their timers still state `false`
because the guard wants an explicit answer and `false` is the house default (identical
behaviour on an unpaused tree).

### Classification

Legend: **stop** = must stop while paused; **run** = must keep running; **n/a** = can
never observe a pause (see above). "Fixed" = changed in this PR.

**Timers**

| Site | Paces | Class | Before | Now |
|---|---|---|---|---|
| `game_manager.gd:590` | turn advance | stop | `false` (#1341) | unchanged |
| `game_manager.gd:773` | day ticks | stop | `false` (#1341) | unchanged |
| `notification_manager.gd` toast lifetime | toast expiry | stop (message) | default (ignored pause) | **fixed**, `false`, tested |
| `plan_screen.gd` error flash | 4s auto-hide | stop (message) | default | **fixed**, `false` |
| `bug_report_panel.gd` show_error | 5s auto-hide | stop (message) | default | **fixed**, `false` |
| `music_manager.gd` conductor nudge | picker "switching..." line | run (pause menu control) | default | explicit `true` |
| `portal_capture.gd` self-quit | dev capture exit | run (tooling) | default | explicit `true` |
| `welcome_screen.gd` x2 | overlay delay | n/a | default | explicit `false` |
| `cold_open_sequence.gd` x2 | intro beats | n/a | default | explicit `false` |
| `conference_vignette.gd` x2 | vignette beats | n/a (own scene via SceneTransition) | default | explicit `false` |
| `settings_menu.gd` `Timer` node | save debounce | n/a | inherits | unchanged |

**Process modes (nodes)**

| Node | Class | Before | Now |
|---|---|---|---|
| `PauseMenu` | run | `ALWAYS` | unchanged |
| `MusicManager` | run | `ALWAYS` | unchanged |
| `LeaderboardSync`, `UpdateCheck` | run (network) | `ALWAYS` | unchanged |
| `SceneTransition` | run (navigation) | inherited PAUSABLE -- **#1034 latent deadlock** | **fixed**, `ALWAYS` + unpause-on-swap, tested |
| `KeybindManager` | run (diagnostic dispatch only -- no gameplay bind lives there) | inherited PAUSABLE -- **#1028** | **fixed**, `ALWAYS`, tested |
| `FlightRecorder` (child of MainUI) | run (capture; its note popup is a LineEdit) | inherited | **fixed**, `ALWAYS` |
| `GameManager`, `MainUI` and the rest of `main.tscn` | stop | inherited | unchanged (correct) |
| `NotificationManager` | stop (messages freeze) | inherited | unchanged (correct) |
| `DebugOverlay`, `DevModeOverlay` | **undecided** (carry state-writing controls) | inherited | unchanged -- see "Left for later" |

**Tweens** (all inherit their node; none needed a per-tween change)

| Site | Class | Verdict |
|---|---|---|
| `scene_transition.gd` x3 (fade out / in / quick blip) | run | correct now that the node is `ALWAYS` (#1034) |
| `music_manager.gd` x2 (crossfade, fade-out) | run | correct (`ALWAYS` since the music-picker fix) |
| `notification_manager.gd` x3 (slide in / out / reposition) | stop (message) | correct; lifetime timer now agrees with them |
| `fanfare_popup.gd` x2 (reveal / dismiss) | stop (presentation) | correct; see the input caveat below |
| `main_ui.gd` first-lever pulse (looping) | stop (presentation) | correct |
| `debug_overlay.gd` x2 (error/warning flash) | follows the overlay decision | parked with #1028 |
| `cold_open_sequence.gd` x9, `conference_vignette.gd` x1 | n/a | correct |
| `portal_shader_demo.gd` x1, `portal_capture.gd` x1 | n/a (dev) | correct |

**Input handlers**

| Handler | Class | Verdict |
|---|---|---|
| `pause_menu.gd` `_input` (ESC closes) | run | correct (`ALWAYS`) |
| `keybind_manager.gd` `_input` (diagnostic binds) | run | **fixed** (#1028) |
| `flight_recorder.gd` `_input` (ESC skips note) | run | **fixed** with its node |
| `main_ui.gd` `_input`, `_unhandled_key_input`, `_unhandled_input` | stop | correct (pausable) |
| `tab_manager.gd` `_input` | stop | correct |
| `esc_to_close.gd` `_unhandled_input` (in-game dialogs) | stop | correct -- the pause menu owns ESC while open |
| `staff_perks_panel.gd` `_unhandled_input`, `doom_trend_graph.gd` `_gui_input` | stop | correct |
| `fanfare_popup.gd` `_unhandled_input` | stop | correct in itself; see caveat |
| `bug_report_panel.gd` `_input` | stop | correct (opened only from gameplay input) |
| `game_over_screen.gd` `_input` (in `main.tscn`) | stop | correct by inheritance; NOT verified that ESC cannot open the pause menu over it |
| `welcome_screen`, `welcome_overlay`, `whats_new_modal`, `player_guide`, `settings_menu`, `keybind_screen`, `pregame_setup`, `config_confirmation`, `credits_screen`, `leaderboard_screen`, `cold_open_sequence` (x2), `conference_vignette`, `office_sandbox` | n/a | separate scenes, cannot be paused |

## What is pinned

- `godot/tests/unit/test_pause_stops_month_playback.gd` (#1341) -- sim stops, and resumes.
- `godot/tests/unit/test_pause_semantics.gd` (#1343) -- each in both directions:
  SceneTransition's fade finishes while paused (control: a pausable tween does not);
  navigation releases a pause; KeybindManager dispatches F3 while paused (control: an
  ordinary node cannot process); a toast does not expire behind the menu, and does
  expire after it. Run against the code with the three fixes reverted, those three
  tests failed (4 assertions); `_release_pause()` is new code and has no "before".
- `tools/check_pause_timers.py` -- no new `create_timer` can take the default silently.

## Left for later (not done here)

1. **Overlay input ownership -- the `mouse_filter` half (67 sites).** The second half
   of what Pip hit: which overlay owns input when two are up. One concrete shape,
   INFERRED from source and not run: ESC while a `FanfarePopup` (CanvasLayer 128) is up
   reaches `MainUI._input` first and opens the pause menu UNDER the fanfare; the fanfare
   is then frozen but its `MOUSE_FILTER_STOP` backdrop still sits over the menu. ESC
   still closes the menu, so it is not a trap, but the menu cannot be clicked. Same
   family as #603. Fix shape: MainUI declines to open the pause menu while a fanfare is
   up (or the fanfare joins `ModalStack`). Needs a run to confirm Godot's hit-testing of
   a paused STOP control before changing anything.
2. **`DebugOverlay` / `DevModeOverlay` while paused (#1028 option B).** Hotkeys now
   reach them, so F3 toggles a readout that shows a correct snapshot (the game is
   frozen, so the snapshot is current) but its buttons are inert and it does not
   live-refresh. Making them `ALWAYS` lets state-writing dev pokes run while paused --
   a call for Pip, not a side effect of this sweep.
3. **The 67 `mouse_filter` sites** are not classified one by one here. Most
   are `IGNORE` on decorative children; the question that matters is item 1.
