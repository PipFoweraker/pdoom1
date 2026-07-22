# Deprecated: single-slot save / load (v0.11.0)

> Status: HIDDEN (dormant), not deleted. Decided 2026-07-21 (Pip). Re-enable is a
> deliberate design act, not a bug-fix -- see "Open design question" below.

## What was deprecated

The pre-v0.11.0 quicksave feature (L7, issue #618):
- **Save:** pause menu "Save Game" button -> one overwrite-only quicksave file
  (`SaveLoad.QUICKSAVE_PATH`).
- **Load:** welcome-screen "Load Game" button -> set a one-shot `GameConfig.pending_load_path`
  flag, navigate to `main.tscn`, and `main_ui._boot_game()` loads the save instead of a fresh
  run (falls back to a new game if the load fails).

Both buttons are now `visible = false` in `_ready()` (welcome_screen.gd, pause_menu.gd). The
handlers (`_on_load_game_pressed`, `_on_save_pressed`) and the boot-time consume path in
`main_ui._boot_game()` are left intact and dormant -- flip the two `visible` flags to restore.

## Why hide it now

1. **Half-built.** One slot, no save picker, and Load drops you straight into mid-run state
   with zero context (no "here is the run you are resuming"). It reads as unfinished to a
   tester.
2. **Points against the game's own thesis (unresolved).** The meta-loop is a live, seeded
   leaderboard with a per-run verification hash chain (ADR-0002, VerificationTracker).
   Mid-run save/resume enables save-scumming a competitive board, and a faithful resume would
   have to restore the verification chain intact or the submitted score's provenance breaks
   (untested).
3. **De-risking before a friends-and-family tester build.** Fewer half-built surfaces.

Trivial to bring back; hidden rather than removed for exactly that reason.

## Open design question (the reason this is a DESIGN decision, not a fix)

Pip, 2026-07-21: save-scumming might become an INTENTIONAL mechanic rather than a leak --
an "Orb of Regret" / time-travel-branching affordance that fits the game's theming, letting
players explore branches of a run.

The tension to resolve before re-adding:
- **For a branch/rewind mechanic:** thematically rich; turns "save-scum" from an exploit into
  a designed, costed action; supports experimentation.
- **Against (the case for one uninterruptible run per seed):** unlimited rewind lets players
  explore the decision tree too fast, which flattens discovery and cheapens the per-seed
  leaderboard. A single start-to-finish run keeps the discovery base honest and unhurried,
  and keeps every submitted score a clean, un-rewound line.

Either resolution is legitimate; the point is that re-enabling save/load must pick one
deliberately (and, if resume stays leaderboard-eligible, solve the verification-chain
restore). Until then: hidden.

## To re-enable (checklist for the future)

- [ ] Decide the design question above (branch-mechanic vs one-run discipline).
- [ ] If leaderboard-eligible: verification-chain-safe resume, or mark resumed runs
      practice-only (not board-eligible).
- [ ] A real save picker (multiple slots / named saves), not the single overwrite slot.
- [ ] A "welcome back" context screen on load (seed, month, doom, score-so-far).
- [ ] Un-hide the two buttons (welcome_screen.gd, pause_menu.gd `visible = true`).
