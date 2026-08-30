# Pause semantics -- the sweep this repo owes itself

Opened 2026-08-30, the day #1341 was found on a shipped build. Scoped and
measured here; the work itself is due by Friday for the league patch.

COMMITMENT: 2026-09-04 -- Sweep the pause-semantics family: every create_timer, tween and input-capture site that silently opts out of SceneTree.paused, plus a written statement of what pausing this game MEANS and a guard that stops a new one landing -- owner: pip -- kind: deadline -- note: scoped in this file after #1341 shipped to players in v0.14.4; Friday at the latest because the league patch goes out then.

## The one-sentence problem

**Nothing in this repository states what "paused" means, so every site that could
observe `SceneTree.paused` decided for itself -- usually by inheriting an engine
default that says "ignore it".**

## How it surfaced

Pip opened the pause menu on the shipped v0.14.4 build to change the music
volume. Six day-ticks and a month boundary ran while it was open, and the Month
Review dialog then appeared over a still-open, still-click-eating, **invisible**
pause menu. `begin planning next month` would not take a click.

`pause_menu.gd` was never at fault. It sets `get_tree().paused = true` correctly.
The month-playback loop simply never observed it, because
`SceneTree.create_timer(time_sec, process_always = true, ...)` **defaults
`process_always` to true** -- the engine's default is to ignore the pause.

Fixed in #1341 at the two gameplay-advancing sites, with a regression test that
was proven to fail without the fix (`turn 1 -> 7 over 0.6s`, six ticks, the same
magnitude Pip saw). That fix is deliberately narrow. This document is the part
that is not narrow.

## The measured surface, 2026-08-30

### 1. Timers that ignore pause -- 9 remaining sites

    grep -rn "create_timer(" godot/scripts/ --include=*.gd | grep -v ", *false" | grep -v ", *true"

| file | what it paces | pause-correct? |
|---|---|---|
| `ui/welcome_screen.gd:248,253` | welcome beats | probably fine, nothing to pause into |
| `ui/cold_open_sequence.gd:188,662` | cold-open beats | probably fine, same reason |
| `ui/conference_vignette.gd:45,182` | vignette beats | **unclear** -- this is mid-run, and ESC during it is reachable |
| `ui/plan_screen.gd:58` | 4s error-toast auto-hide | **wrong, mildly** -- a toast can expire while you are reading the menu |
| `ui/bug_report_panel.gd:300` | 5s "thanks" dismiss | same shape as above |
| `dev/captures/portal_capture.gd:88` | capture self-quit | correct as-is, capture must not pause |

None of the nine advances game state, which is why #1341's fix stops at two. But
"does not advance state" is not the same as "is correct", and nobody has decided
which of these SHOULD stop.

### 2. Tweens -- 18 sites, none of which say anything about pause

    grep -rc "create_tween()" godot/scripts/ --include=*.gd     ->  18 sites
    grep -rc "set_pause_mode\|TWEEN_PAUSE" godot/scripts/       ->   0

Every tween inherits its pause behaviour from the node that created it, and no
site has examined that. **This family already has a known latent member:** #1034
records that the fade transition awaits a pausable tween and *"would deadlock ALL
navigation if called while paused"*. That one has never fired only because
nothing has yet called it from a paused state.

### 3. Input capture by things you cannot see -- 47 `mouse_filter` sites

This is the second half of what Pip hit: the pause menu was open, drawn
underneath the Month Review dialog, and still eating clicks. Fixing the timer
removes the common path into that state, but it does not answer the general
question of which overlay owns input when two are up.

Related and pre-existing: #603 (events leak under the fanfare popup, no dimming
backdrop), #1028 (ESC/pause disables ALL diagnostic surfaces -- root cause is
`process_mode`, not input priority).

## What the sweep should produce

1. **A written statement of what pausing means**, in one place, covering: the
   simulation, presentation beats, audio, input, and navigation. Probably an ADR,
   because the answer is a design decision and not a bug fix.
2. **Each of the sites above conformed to it**, or explicitly excepted with a
   reason next to the code.
3. **A guard so the next one cannot land silently.** The cheapest honest version:
   a check that flags `get_tree().create_timer(` with no explicit second argument
   under `godot/scripts/`, requiring the author to state the intent either way.
   That is greppable, gateable, and in the same family as the repo's existing
   `check_scene_nav.py`. It should ship with a self-test and be wired into
   `guards.yml`, per the doctrine already established there.

## Why it is worth doing rather than filing

This class does not announce itself. Every member is a default that was never
chosen, and each one is invisible until a player does something ordinary -- open
a menu, change the volume, press ESC at the wrong moment. #1341 sat in a shipped
build; #1034 is sitting in this one right now, waiting for the first navigation
call from a paused state.

The fix per site is usually one argument. The expensive part is knowing which
sites, which is what this sweep buys.
