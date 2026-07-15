# Desperation-Lever Solver (EE-9 / DQ-25) — does the lever ever pay?

> **Base:** dials-1-4 calibration on **nine-stream doom** (ADR-0015 / #643) — ledger teeth live,
> per-bill caps + slow-bleed rollover. **CAVEAT:** dial-5 Attention pass pending + a stream
> re-calibration owed; re-run before the DQ-25 beat. The trap finding survived the migration.

EE-9 solver-bot: baseline `fundraise_first` vs the same policy + ONE injected rule 'pull `desperation_lever` when doom >= threshold' (plus an every-month and a double-dose variant). 12 seeds each, shared month driver. The survival delta is attributable to the lever alone.

| Variant | median months | mean | min | max | delta median vs baseline | doom-root deaths | ledger-root deaths | survived-to-cap(60) |
|---|---|---|---|---|---|---|---|---|
| baseline (no lever) | 15.0 | 14.0 | 9 | 16 | +0.0 | 10 | 2 | 0 |
| lever@always | 10.0 | 10.1 | 8 | 12 | -5.0 | 0 | 12 | 0 |
| lever@40 | 11.5 | 11.2 | 9 | 12 | -3.5 | 0 | 12 | 0 |
| lever@60 | 13.0 | 13.2 | 9 | 17 | -2.0 | 1 | 11 | 0 |
| lever@80 | 15.0 | 14.0 | 9 | 16 | +0.0 | 10 | 2 | 0 |
| lever@2x60 | 13.0 | 12.8 | 9 | 17 | -2.0 | 1 | 11 | 0 |

## Verdict — does the lever pay?

- **The lever is NEUTRAL at the median** (best variant `lever@80`, +0.0 months). Check the min/max and death-cause columns for distribution effects the median hides — a lever that trades tail risk for mode survival can be worth shipping even at zero median delta.
- **Dose-response (the DQ-25 answer):** firing the lever earlier/more is monotonically WORSE — `lever@80` (fires late, rarely) is neutral (+0.0, 2 ledger-root deaths) while `lever@always` (every month) is the worst (-5.0, 12/12 deaths ledger-root). The mechanic reliably CONVERTS doom deaths into delayed ledger deaths (baseline 1 ledger-root -> lever@always 12), and the conversion costs survival. Under calibrated constants the desperation lever is a **trap that reads as help**: the -10 doom is real and visible, its compounding secret governance liability is neither. That legibility gap is the DQ-25 design question — intended cost you can see coming, or a mispriced sucker-lever?
- **Survived the nine-stream migration — and got STEEPER.** On stream-based doom (ADR-0015 / #643) the trap is more punishing than on the pre-stream calibration: `lever@always` now costs ~5 median months (was ~2.5), and the doom->ledger death conversion is total (baseline 2 ledger-root -> lever@always 12/12). The qualitative finding is migration-robust: systematic lever use monotonically shortens survival and swaps the death cause from doom to ledger.
- **Don't misread the opening-book's near-neutral lever signal.** `OPENING_BOOK_v0.md` shows `desperation_lever` as roughly neutral in a random opening (a lone lever buried among ~6 random early picks washes out — its effect is swamped by whatever else the prefix bought). That is NOT a contradiction: this solver ISOLATES the lever against a disciplined baseline and sweeps its dosage, so it is the instrument that sees the mechanic cleanly. Systematic use = trap (here); incidental single use in noise = undetectable (there). Trust the solver for the mechanic's verdict.
- **Threshold reachability** — doom starts 20 and climbs ~4-6/month on a passive line, so plan-phase thresholds 40/60/80 genuinely fire mid-run (unlike the pre-calibration world, where runs died sub-month and no plan-phase doom trigger was ever reached). Residual DQ-25 flavour question: a 'desperation' verb might belong at window speed, not plan speed.

_Regenerate: `"$GODOT" --headless -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual -gselect=test_desperation_solver.gd -gexit` (from `godot/`)._
