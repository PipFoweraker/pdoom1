# Leaderboard crash -- RESOLVED (2026-07-21)

> The worst bug of the v0.11.0 cycle: a release-only, no-backtrace segfault on the
> game-over -> leaderboard transition. Root-caused and fixed 2026-07-21 after ~4 days
> and (honestly) SEVEN distinct hypotheses, five of which were wrong. This is the full
> record -- kept because the mis-diagnoses are the lesson, and because the root cause is
> a systemic pattern still latent elsewhere in the codebase (see section 6).

---

## 1. TL;DR

**Symptom.** In RELEASE builds only, pressing ENTER on the game-over (DEFEAT) screen to
go to the leaderboard segfaulted the process (`0xc0000005`, access violation) while the
leaderboard scene was loading, BEFORE its `_ready` ran. No GDScript error, no Godot crash
backtrace in stdout or `godot.log` (a hard access violation that outran the logger).

**Root cause.** `game_over_screen.gd` called `get_tree().change_scene_to_file(...)`
**synchronously from inside its `_input()` handler** (on the ENTER key).
`change_scene_to_file()` synchronously loads + instantiates the target scene; doing that
work from *inside* input dispatch drove the engine into a deterministic native deref.

**Fix (one line, at the call site).** Defer the navigation out of the input callstack:

```gdscript
# game_over_screen.gd _input(), on KEY_ENTER / KEY_SPACE:
get_viewport().set_input_as_handled()
call_deferred("_continue_to_leaderboard")   # was: _continue_to_leaderboard()
```

**Confirmed** by a verified-fresh release build (`build_release.py`, marker-in-pack
proven) reproducing the crash, and the deferred build reaching the leaderboard cleanly --
a live repro AND a live non-repro isolating the exact cause.

---

## 2. Why it was so hard

Every property of this bug defeated a standard tool:

- **Release-only.** Debug builds never crashed (different heap/timing masks the deref). So
  the editor, `--export-debug`, and every headless test were all blind to it.
- **No backtrace.** Godot's crash handler produced nothing in the release template; the
  access violation killed the process before any log flush. `godot.log` ended mid-gameplay.
- **Headless can't reach it.** It is a GUI/scene-transition fault; the test tiers never
  perform a real windowed scene change, so green CI meant nothing here.
- **Content-independent.** A bare `Control + ColorRect + Label + Button` stub scene at the
  leaderboard path crashed identically -- so "fix the scene" attempts (textures, dropdown)
  all failed, because the scene was never the cause.
- **The last log line was a red herring.** `--verbose` showed the last resource as the
  leaderboard `.scn`/`.gdc` load, which framed it as a leaderboard-scene bug for days. The
  real fault was the *act of loading from within input dispatch*, not the thing loaded.

---

## 3. The forensic timeline -- seven hypotheses, honestly

Each row is a hypothesis, the evidence that raised it, and the evidence that KILLED it.
Passes 1-3 were adjacent real bugs (worth fixing, not the crash); 4-7 were about this crash.

| # | Hypothesis | Killed by |
|---|---|---|
| 1 | Endgame freeze / lost score (blocking baseline sim on main thread) | Fixed (#705, real bug) -- crash persisted |
| 2 | Memory leak (`leaderboard.gd extends Node`, boards never freed) | Fixed (#713, real bug) -- crash persisted |
| 3 | Load-perf cliff (parse every seed file every open, ~1s) | Fixed (#716, real bug) -- crash persisted |
| 4 | Renderer / GPU (Vulkan) | `--rendering-driver opengl3` still crashed -> renderer-independent |
| 5 | Texture decode (`tex_cyan_ispf_512.ctex` last in `--verbose`) | #728 swapped to ColorRect; **strip build with the textures physically absent still crashed** -> textures fully exonerated |
| 6 | Leaderboard scene content (e.g. the `OptionButton`/SeedDropdown building a popup) | **Minimal stub scene (no dropdown, no real content) crashed identically, before `_ready`** -> content exonerated |
| 6b | Orphaned baseline worker thread racing scene teardown | Log showed `Using precomputed baseline` -- **no thread was ever started** on this seed. Dead. |
| 6c | Dangling GUI keyboard focus (`Viewport.gui.key_focus`) | Added `gui_release_focus()` before the change -> **still crashed** -> not focus |
| 7 | **change_scene_to_file() called from inside `_input()`** | `call_deferred` the nav -> **crash gone.** CONFIRMED. |

The isolation table that cracked it (all on the SAME verified-fresh release build):

| Path | Trigger | Result |
|---|---|---|
| main menu -> leaderboard | mouse (Button `pressed`) | works |
| game-over -> main menu | mouse (Button `pressed`) | works |
| game-over -> leaderboard | **keyboard (ENTER in `_input`)** | **crash** |

Same destination scene works from a mouse click and crashes from a keyboard `_input`
handler. The destination was never the variable -- the **input callstack** was.

---

## 4. The smoking gun: Windows Error Reporting

With no Godot backtrace and no debugger installed, the break came from **Windows Event
Viewer** (Application log, "Application Error", Event ID 1000), which had silently recorded
every crash:

```
Faulting application: PDoom.exe, version 0.11.0.0
Faulting module:      PDoom.exe            <- the engine binary, not our GDScript
Exception code:       0xc0000005           <- access violation (dereference of bad ptr)
Fault offset:         0x142be24            <- SAME offset across two different builds / two days
```

Read: it is a **deterministic native pointer deref inside the engine**, not GDScript
erroring (that would be caught and printed). Pull it with PowerShell, no rerun needed:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Application'; Id=1000} -MaxEvents 40 |
  Where-Object { $_.Message -match 'PDoom' } | Select-Object -First 5 |
  ForEach-Object { $_.TimeCreated; $_.Message }
```

This is now the go-to for any release-only native crash here: **the exception code + faulting
module + offset are in the Windows event log already, for free.**

---

## 5. Root cause mechanism

`change_scene_to_file()` is not a lightweight enqueue. It synchronously
`ResourceLoader.load()`s the target `PackedScene` (and its script dependency -- the last
`--verbose` line) and instantiates it. Calling it from inside `_input()` runs that entire
load+instantiate WHILE the engine is mid input-dispatch on the current viewport. That
re-entrancy is what the engine could not survive in the optimized release build -- a
deterministic deref at template offset `0x142be24`, before the new scene's `_ready`.

We did not symbolize the exact engine frame (the release template is stripped and the debug
template does not reproduce). But the cause-and-fix is proven empirically: moving the same
call onto a clean idle frame (`call_deferred`) removes the crash 100% of the time. The
mechanistic class -- **mutating the scene tree / loading a scene from within input
processing** -- is a known Godot hazard; the fix is the standard "defer structural changes
out of input/signal callbacks."

---

## 6. Systemic finding -- this pattern is latent elsewhere (ACTION)

The grep for scene changes reachable from input handlers found the SAME shape in several
screens. Game-over is simply the one that detonated (tearing down the heavy in-game scene
is the likely tipping factor). Each of these calls `change_scene_to_file()` synchronously
from within an `_input`/`_unhandled_input` key handler and should be deferred the same way:

- `game_over_screen.gd` -- ENTER -> leaderboard. **FIXED.**
- `config_confirmation.gd:91` -- ESC -> welcome, ENTER -> main.
- `leaderboard_screen.gd:640` -- ESC -> welcome.
- `settings_menu.gd:198` -- ESC -> welcome.
- `welcome_screen.gd:84` -- ENTER emits a Button `pressed` from *inside* `_input` (same
  re-entrancy, just one hop removed).
- Verify too: `pregame_setup.gd:195`, `player_guide.gd:12`, `main_ui.gd` (`_input` /
  `_unhandled_input` -> quit-to-menu), `keybind_screen.gd`.

**Recommended systemic fix (not yet applied -- Pip to greenlight).** Two options:

1. **Minimal:** wrap every input-initiated scene change in `call_deferred(...)`. Cheap,
   local, low-risk. Apply to the list above.
2. **Structural (preferred long-term):** a tiny `SceneRouter` autoload with
   `go_to(path)` that always `call_deferred`s `change_scene_to_file`, route ALL navigation
   through it, and add a cheap lint/test that fails if any `.gd` calls
   `change_scene_to_file` directly from within an `_input*`/`_gui_input` function body.
   That converts "remember to defer" into an enforced invariant -- the anti-rot pattern
   this repo already uses for generated indexes (`generate_dq_index.py`) and the
   no-dead-end escape test (#711).

---

## 7. The reusable diagnostic method (what actually worked)

For a release-only, no-backtrace native crash here, in order:

1. **Windows Event Viewer / `Get-WinEvent` Id 1000** -> exception code + faulting module +
   offset, for free, from crashes already produced. `0xc0000005` in the engine binary = a
   native deref, not GDScript.
2. **`build_release.py`** -> never test a stale pack again; it nukes `.godot`, injects a
   unique marker FILE (GDScript packs as binary-tokenized `.gdc`, so string literals do
   NOT survive as grep-able text -- anchor freshness on a resource filename), exports, and
   proves the marker is in the `.pck` before emitting the build.
3. **Isolation by construction** -> vary ONE thing at a time (destination scene; source
   scene; input vs mouse trigger) on the same verified build. The table in section 3 is
   what localized it to the input callstack.
4. **Bisect with a stub** -> a dependency-free stub scene at the target path exonerates
   "scene content" in one build.
5. **The human release-build playtest is the final gate.** Headless/CI cannot reach GUI /
   scene-transition / decode faults; only playing the release build to the affected screen
   surfaces them. Never declare a render/scene/asset bug fixed without that repro passing.

## 8. Upstream

Candidate Godot report drafted at `docs/upstream/godot-changescene-from-input-crash.md`:
"`change_scene_to_file()` called from `_input()` causes a release-only segfault
(0xc0000005) before `_ready`" -- with the minimal repro and the WER signature. File it so
the engine either guards the re-entrancy or documents the constraint.
