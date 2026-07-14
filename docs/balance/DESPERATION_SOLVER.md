# Desperation-Lever Solver — does the lever ever pay?

> **CAVEAT — regenerate post-migration.** Balance constants predate the nine-stream doom
> migration (DQ-21); with doom currently sub-month-lethal (~4-10 day-ticks to 100), the
> lever's -10 doom buys only a tick or two before its 3-turn governance fuse. The SOLVER is
> the durable deliverable; re-run once doom is retuned. Regenerate: see footer.

EE-9 solver-bot: baseline `fundraise_first` vs the same policy + one injected rule 'pull `desperation_lever` when doom >= threshold'. 12 seeds each. Isolates the lever's effect on survival + death cause.

| Variant | median turns | mean turns | min | max | Δ median vs baseline | doom-surface deaths | ledger-root deaths |
|---|---|---|---|---|---|---|---|
| baseline (no lever) | 7.0 | 7.1 | 4 | 10 | +0.0 | 12 | 0 |
| lever@always | 4.0 | 4.6 | 2 | 8 | -3.0 | 3 | 9 |
| lever@60 | 7.0 | 7.1 | 4 | 10 | +0.0 | 12 | 0 |
| lever@70 | 7.0 | 7.1 | 4 | 10 | +0.0 | 12 | 0 |
| lever@80 | 7.0 | 7.1 | 4 | 10 | +0.0 | 12 | 0 |
| lever@90 | 7.0 | 7.1 | 4 | 10 | +0.0 | 12 | 0 |

## Verdict — does the lever pay?

- **The lever does NOT pay (current constants)** — no variant beats the no-lever baseline on median survival (best delta +0.0 turns). Even pulled pre-emptively at month 0, one -10 doom shave is swamped by how hot doom runs (~7-turn/50-point climb), and it plants the secret governance liability for nothing. Under these constants the lever is a trap. **Expected to change post-migration** — re-run then; the DQ-25 beat should use retuned numbers.
- **Reachability finding (design smell):** the `lever@N` doom-threshold variants are IDENTICAL to baseline because the lever is a PLAN-PHASE (strategic) action, its trigger is only re-checked at a month boundary, and runs die mid-month-0 before doom-at-a-plan-phase ever reaches the threshold. A 'desperation' lever you can only reach when NOT yet desperate (at plan time) is a reachability gap — only `lever@always` (pull at month 0 unconditionally) actually fires. Flag for DQ-25: should the lever be a response-window verb (instant speed) rather than a plan action?
- **Death-cause shift** — where the lever fires (`lever@always`), watch doom-surface deaths convert to ledger-root deaths: that conversion IS the mechanic's signature (buy doom now, pay governance later), legible in the two rightmost columns.

_Regenerate: `"$GODOT" --headless -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual -gselect=test_desperation_solver.gd -gexit` (from `godot/`)._
