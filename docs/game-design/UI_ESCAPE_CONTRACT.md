# UI escape contract -- no dead-ends

- **Status:** ACCEPTED
- **Date:** 2026-07-19
- **Branch:** fix/ui-no-dead-ends
- **Enforced by:** `godot/tests/unit/test_ui_no_dead_ends.gd`

## The failure class

A *UI dead-end* is a panel that opens with no working way out: no visible close /
back control, and `ui_cancel` (Esc) does nothing. The player is trapped and can only
force-quit. The reported instance was the Liability Ledger (`ledger_screen.gd`):
`build_screen()` returned a bare `Panel` whose exit was ENTIRELY host-provided
(`MainUI._decorate_active_submenu` for the `[X]`, `MainUI._input` for Esc). A panel
whose only exit lives in a caller is one wiring-regression away from trapping the
player -- and it is invisible to isolation tests.

## The contract

**Every openable overlay panel MUST provide its OWN working exit.** Concretely, once
the panel is instanced and shown, at least one of these must close it (free it, hide
it, or emit a zero-arg close/closed/cancel signal for its parent):

1. **`ui_cancel` (Esc).** An `_input` / `_unhandled_input` / `_shortcut_input` handler
   that closes the panel when `event.is_action_pressed("ui_cancel")`. This is the
   preferred, primary path -- Esc closes the topmost panel, everywhere.
2. **A visible close / back affordance.** A discoverable `Button` (a `[X]`, "Close",
   "Back", "Continue", ...) whose `pressed` handler hides / frees the panel.

Both SHOULD be present. "Intrinsic" is the key word: the exit must not depend on a
host input router being wired, because that wiring can be absent (isolation, reuse) or
regress.

### How the shared frame delivers it

`SubmenuChrome.add_close_affordance(dialog, on_close)` (the shared submenu frame) now
attaches BOTH: the clickable `[X]` + "[ESC] close" hint AND an `EscToClose` helper
node (`scripts/ui/esc_to_close.gd`) that calls `on_close` on `ui_cancel`. Any panel
routed through the chrome inherits the full contract for free. Procedural panels
(e.g. the ledger) call it from their own `build_screen()`; in the running game
`MainUI._input` still consumes Esc first, so the helper never double-fires -- it is
the intrinsic fallback.

## Naming / discovery conventions (so the test finds future panels automatically)

`test_ui_no_dead_ends.gd` auto-discovers panels -- there is no hand-maintained list.
For it to cover a NEW panel, follow one of these conventions:

- **Scene overlays:** name the `.tscn` under `res://scenes/ui/` with a `_panel` or
  `_modal` suffix (e.g. `foo_panel.tscn`).
- **Procedural overlays:** expose a `build_screen(data, viewport_size) -> Control`
  builder on the script (as `ledger_screen.gd` does). The test instances it with
  `build_screen(null, <size>)` and checks the returned node.

Transient toasts (`_popup`, e.g. `fanfare_popup`) auto-dismiss (backdrop click /
Continue / Esc) and are a separate class; they are not in the test's scope but still
honor `ui_cancel`.

## Why a functional (not structural) test

Per ADR-0017 (anti-hollow tests), the guard must exercise the thing it protects. The
test does not grep for an Esc handler; it INSTANCES each panel in the live tree, shows
it, dispatches a real `ui_cancel` `InputEvent` (then, failing that, presses the close
button), and asserts the panel ends up freed / hidden / signalled-closed. It was
watched fail red-first against the unfixed ledger before this contract was accepted.
