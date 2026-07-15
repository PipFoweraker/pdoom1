# Desperation-Lever Solver (EE-9 / DQ-25) — does the lever ever pay?

> **Base:** dials-1-4 calibration (`L1_CALIBRATION_2026-07-14.md`) — doom starts 20, ledger
> teeth live (Finding A fix), per-bill caps + slow-bleed rollover. **CAVEAT:** still pre
> nine-stream migration (DQ-21); re-run post-migration before the DQ-25 beat locks anything in.

EE-9 solver-bot: baseline `fundraise_first` vs the same policy + ONE injected rule 'pull `desperation_lever` when doom >= threshold' (plus an every-month and a double-dose variant). 12 seeds each, shared month driver. The survival delta is attributable to the lever alone.

| Variant | median months | mean | min | max | delta median vs baseline | doom-root deaths | ledger-root deaths | survived-to-cap(60) |
|---|---|---|---|---|---|---|---|---|
| baseline (no lever) | 14.0 | 17.2 | 11 | 55 | +0.0 | 11 | 1 | 0 |
| lever@always | 11.5 | 11.9 | 9 | 16 | -2.5 | 0 | 12 | 0 |
| lever@40 | 12.0 | 15.0 | 10 | 50 | -2.0 | 2 | 10 | 0 |
| lever@60 | 13.0 | 16.7 | 12 | 53 | -1.0 | 1 | 11 | 0 |
| lever@80 | 14.0 | 17.5 | 12 | 56 | +0.0 | 10 | 2 | 0 |
| lever@2x60 | 13.0 | 16.3 | 11 | 55 | -1.0 | 1 | 11 | 0 |

## Verdict — does the lever pay?

- **The lever is NEUTRAL at the median** (best variant `lever@80`, +0.0 months). Check the min/max and death-cause columns for distribution effects the median hides — a lever that trades tail risk for mode survival can be worth shipping even at zero median delta.
- **Threshold reachability** — doom starts 20 and climbs ~4-6/month on a passive line, so plan-phase thresholds 40/60/80 now genuinely fire mid-run (unlike the pre-calibration world, where runs died sub-month and no plan-phase doom trigger was ever reached). Residual DQ-25 flavour question: a 'desperation' verb might belong at window speed, not plan speed.

_Regenerate: `"$GODOT" --headless -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual -gselect=test_desperation_solver.gd -gexit` (from `godot/`)._
