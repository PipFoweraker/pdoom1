# DOOM_STREAMS_v1 — ADR-0015 nine-stream doom coefficients + rationale

**Lane:** doom-migration (ADR-0015 flagship) · **Branch:** `adr-0015-doom-streams` (base `l1-balance-calibration` @ `edb2e3a`) · **Date:** 2026-07-15
**Function:** `godot/scripts/core/doom_system.gd` · **Pricing:** `godot/data/balance/defaults.json → doom.streams.*` · **Harness:** `godot/tests/manual/test_l1_month_sweep.gd` (72 runs)

> **What this is.** ADR-0015 makes doom an ACCUMULATING RATE computed each day tick from a
> sum of NAMED STREAMS, each fed by a DQ-21 world-state intermediary. No action/event writes
> doom directly. This memo prices the streams so the calibration headline (`L1_CALIBRATION_2026-07-14.md`)
> reproduces within tolerance. **The function is structure; these numbers are the freely-tuned layer.**

## 1. The streams (what each is, which intermediary feeds it)

`doom_rate = Σ streams` (superposition — MAY be negative). `doom_level += doom_rate` each tick.

| Stream | Intermediary (DQ-21) | Meaning | Sign |
|---|---|---|---|
| `baseline` | `ambient_risk` | year-keyed background floor (2017 low, climbs) | + |
| `overhang` | `frontier_capability` − `safety_absorption` | ACUTE hazard: frontier not matched by absorption; `max` over actors | + (clamped ≥0 v1) |
| `diffusion` | `general_capability` | chronic commoditized floor (ratchet) | + |
| `compute` | `dedicated_ai_compute` | the controllable fleet (v1: inert, `W_compute=0`) | + |
| `panic` | `global_panic` | social accelerant (reckless rival/player moves, risk shocks) | + |
| `alarm` | `global_alarm` | small standing RELIEF (productive concern) + damper gate | − |
| `ledger` | (routed input) | ADR-0003 bill teeth, routed via `add_stream_input` | + |
| `technical_debt` | `technical_debt` | GameState coupling (migrated from a direct write) | + |
| `pulse:*` | `doom_pulses` | ADR-0005 scheduled envelopes (v1: none wired) | ± |
| `momentum` | — | gated trend modifier on the sum (`doom.momentum_enabled/weight`) | ± |

`political_pressure` and `global_compute` are **gate/derivation-only** — no stream of their own
(DQ-21 R2-Q2 / Q-SEM-COMPUTE). Typed dampers subtract from a specific stream (clamped ≥0 v1).

## 2. Stream coefficients (`doom.streams.*`) — the v1 prices

| Key | Value | What it does / why this size |
|---|---|---|
| `W_frontier` | **0.000039** | overhang weight on `max(frontier)−absorption`. Set so **do_nothing (rival-frontier only) lands at median 14**; larger → do_nothing dies faster. |
| `cap_frontier_gain` | **60.0** | player frontier gained per productive capability researcher / tick. Set so **greedy_overcommit dies ~7** off its own frontier while do_nothing is unaffected. |
| `safety_absorb_gain` | **8.0** | safety_absorption gained per productive safety researcher / tick. Offsets rival frontier in the overhang gap; set so **safety/reserve outlast passive but still die** (rivals eventually outpace absorption). |
| `alarm_gain` | **0.05** | global_alarm per productive safety researcher / tick. Small (DQ-21 §1.7 "alarm small by design"); large values drive a sustained-negative rate (trips the trend invariant). |
| `W_alarm` | **0.02** | alarm stream = −0.02·global_alarm — the natively-NEGATIVE relief component. |
| `W_panic` | **0.02** | panic stream weight; with `panic_decay` sets the steady rival-pressure floor. |
| `panic_per_capability_action` | **0.05** (`rivals.*`) | global_panic per reckless rival capability move → the steady early rival pressure floor (replaces the retired per-action doom literals). |
| `panic_decay` | **0.97** | habituation on panic (steady-state ≈ input/0.03). |
| `alarm_decay` | **0.985** | habituation on alarm. |
| `W_general` | **0.0005** | diffusion weight (small growing floor). |
| `diffusion_gain` | **0.00006** | general_capability per tick from Σ rival frontier (slow ratchet). |
| `W_compute` | **0.0** | compute stream inert in v1 (the ocean has no own doom term, DQ-21 Q-SEM-COMPUTE). |
| `leak_panic_scale` | **0.02** | researcher-leak / stationery-failure incidents → global_panic. |
| `action_*` (founder-action → intermediary scales) | **0.0** unless noted | founder safety/audit/paper actions priced at 0 in v1 (their influence already flows via the researcher advance; a follow-up prices them). Non-sweep levers (lobby/warning/acquire/sabotage/opensource/conference/cat) carry real nonzero scales. |

## 3. Intermediary dynamics (flow → stock)

Each tick, `DoomSystem._advance_intermediaries()`:
- **player frontier** += `cap_frontier_gain` × (productive capability researchers)
- **safety_absorption** += `safety_absorb_gain` × (productive safety researchers); **global_alarm** += `alarm_gain` × same
- **rival frontier** = each rival's `capability_progress` (already accumulates in `rivals.gd`); the overhang scalar is `max` over all actors
- **general_capability** += `diffusion_gain` × Σ rival frontier (ratchet)
- **ambient_risk** = `doom.base_per_turn` (0.06); **alarm/panic** decay by their `*_decay`

"Productive" = managed AND compute-fed, mirroring `_step_researcher_productivity`.

## 4. Regression — calibrated vs migrated (72-run sweep, same seeds/policies)

Both measured on this machine. Calibrated = `l1-balance-calibration` baseline; migrated = this branch @ locked coefficients.

| Policy | Calibrated median (range) | Migrated median (range) | death-cause (migrated) | contract |
|---|---|---|---|---|
| `do_nothing` | 14.0 (13–15) | **14.0 (14–15)** | 10/0/0 doom | [x] median 14 |
| `safety_lean` | 16.5 (13–21) | 18.0 (17–26) | 8/0/0 doom | [O] +1.5 (in n=8 variance; ordering held) |
| `reserve_heavy` | 19.0 (15–45) | **19.5 (17–21)** | 8/0/0 doom | [x] |
| `random_walk` | 8.0 (4–13) | 6.0 (4–13) | 0/0/30 ledger | [O] −2 (still ledger-rooted) |
| `greedy_overcommit` | 7.0 (6–13) | **7.5 (7–14)** | 8/0/0 doom | [x] T4 + T9 (min 7) |
| `loan_desperation` | 7.0 (6–8) | **7.0 (6–7)** | 0/0/8 ledger | [x] T5 + T9 (min 6) |

`MORTALITY_CHECK: max_months=26, immortal_runs=0 → PASS` (calibrated max was 45; both « 400).

**Contract status:** do_nothing median 14 [x] · T9 floor ≥6 for all standard policies [x] (greedy 7,
loan 6; random_walk min 4 is the fuzzer, matching the calibrated baseline) · mortality 0 immortal,
max 26 [x] · loan_desperation ledger-rooted (8/8) [x] · ordering `greedy≈loan≈random < do_nothing <
safety < reserve` [x].

**Deviations (precise):**
1. `safety_lean` 18.0 vs 16.5 (+1.5 months). Within the memo's stated n=8 variance (±2–3). Ordering
   (safety > do_nothing) intact. Bringing it down further trades against the sustained-negative-rate
   trend-invariant flag (over-suppression). Left slightly high rather than over-tuned.
2. `random_walk` 6.0 vs 8.0 (−2 months). Still 30/30 ledger-rooted — it dies of its ~40% reckless
   ledger moves, not of engaging. The stock-based overhang makes reckless capability moves bite a
   touch faster than the old flow model; consistent with the calibration's own "below-band, above the
   reckless cluster" reading, just lower.

## 5. What is NOT priced here (v1 hooks, follow-up lanes)

- **Scheduled pulses** (`pulse:*`) — envelope schema wired, no content (DQ-21 R2-Q5/Q6).
- **Typed dampers** — engine + gate wired (`doom_dampers`, alarm/political_pressure), no content grants yet (R2-Q4 damper pricing deferred).
- **Founder safety-action intermediary influence** — priced at 0 (their effect flows via the researcher advance; a follow-up prices the founder actions).
- **Event-content doom (data/events/*.json)** — the un-migrated clobber remainder (Legacy #15 / memo §7.1); inert no-ops today, re-authored to intermediaries by a follow-up content lane.
- **R2-Q9 stream clamp** — hazard streams clamp ≥0 in v1; the natively-negative alarm stream is exempt. LOUD REVISIT MARKER in `_compute_streams`.
