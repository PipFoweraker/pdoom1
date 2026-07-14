# L1 Balance Recalibration — dials 1-4 applied + iteration log

**Lane:** L1 balance-calibration · **Branch:** `l1-balance-calibration` (base `main`, was `l1-month-turn-engine` / PR #636 — squash-merged) · **Date:** 2026-07-14
**Harness:** `godot/tests/manual/test_l1_month_sweep.gd` (72 runs, same seeds/policies as #637) · **Raw data:** `docs/balance/L1_sweep_runs.csv`
**Baseline:** the overnight sweep memo `docs/balance/L1_SWEEP_2026-07-13.md` (PR #637) — under pre-rebalance constants **no policy survived even one plan-month**.

> **Headline (post-review round).** After the original 5 measured iterations, Pip's #638 review rulings, and a second calibration round for the new **T9 floor** ("no standard run finishes in less than 6 months"), the final state is: do_nothing **14 months** (T1 ✓, byte-identical through the whole T9 round), **every standard policy survives ≥6 full months** (loan_desperation 6-7, greedy_overcommit 6-13 — T9 ✓), the ledger bites *legibly over months* with per-bill caps and a slow-bleed rollover (T6 ✓), and **every policy still dies** (max 45 months, 0 immortal — ADR-0002/T8 ✓). **Two targets still miss, both for a reason outside dials 1-4:** the safety-beats-passive *margin* (~1.2-1.4×, wanted 1.5-2.5×) is bounded by the bot policy's monthly-overhiring **bankruptcy** (a money/salary effect: safety-coefficient bumps do not move the median), and random_walk sits below the do_nothing↔safety band because it takes genuinely self-harming actions ~40% of the time. Neither is the out-of-scope Attention dial — see §Scope + §7. Final numbers measured on the merge with `main` through #640.

---

## ⚠️ Read this first — two load-bearing findings + a scope confession

**FINDING A — the ledger's doom teeth were INERT (probe-confirmed).** The #637 memo dramatised DEFER as a "+99…+143 doom one-click death button." **That doom never actually landed.** The turn loop overwrites `state.doom = doom_system.current_doom` every tick (`turn_manager._step_resolve_doom`), and that authority never reads `state.doom` — so the ledger's `state.doom += doom_hit` was silently **clobbered** the same tick. loan_desperation's "8/8 ledger deaths" in #637 were ordinary *rival-doom* deaths that `DeathAttribution` merely **labelled** ledger (a ledger default sat in the cause log). Probe: a governance bill computing `doom: 104.8` moved actual doom by ~0 (rivals only). **To make dial 3's target real ("DEFER's doom cost lands over subsequent months"), the ledger doom must actually land** — so this calibration routes ledger doom through `doom_system.add_event_doom`. **APPROVED (#638 review, coordinator ruling on Pip's deferral), with this rationale: the fix aligns with ADR-0005/ADR-0015 — one authority for doom writes, no parallel pipes.** `doom_system` is the single doom authority; the pre-fix ledger write was a parallel pipe that the authority (correctly, by its own contract) overwrote. Routing the ledger through the authority's event channel is the ADR-0015-shaped fix, not a workaround — and it makes ledger doom visible in the doom-source breakdown (loss legibility) for free. Event/action *direct* doom writes (`add_resources({"doom": …})`) are still clobbered — that is the remainder of the same bug class, logged as open question §7.1 for the ADR-0015 migration lane.

**FINDING B — safety's advantage is bankruptcy/variance-bound, not doom-bound.** safety_lean/reserve_heavy crush doom to 0 for months, then the bot (which queues `hire_safety_researcher` *every* month) goes **bankrupt** (`funding_starvation`), its researchers go unproductive, and overhang-accelerated doom climbs to death. The final medians land at **1.18× / 1.36×** (safety_lean 16.5 / reserve_heavy 19 vs do_nothing 14), and the *median* is not coefficient-sensitive: strengthening the safety coefficient (-0.18 → -0.28 = **0.0 months**; -0.28 → -0.35 probe = median moved *down* 20→18.5 while only the lucky-tail max grew) does not lift it. At n=8 the medians are variance-dominated (±2-3 months across rng streams — safety_lean read 20 before the T9 round's rng-stream shift and 16.5 after, same constants). The 1.5-2.5× margin is therefore **not reliably reachable via dials 1-4** (or their re-denomination): it demands the money/hiring economy (cheaper hires, the bot not overhiring, or the salary re-denomination ADR-0009 already owes), which is neither a doom/ledger/momentum/start dial nor the Attention dial. What DID move it (1.1× → ~1.2-1.4×) was merging `main`'s event-outcome fixes — an economy change, consistent with this finding.

**SCOPE CONFESSION (do not skip).** The #637 memo's dial table named only *rivals + base* (dial 1) and *DEFER→payroll* (dial 3). Measurement proved the per-tick→per-month re-denomination artifact **pervades three more surfaces that the memo did not list**, and the targets are unreachable without completing them. I extended dials 1 & 3 to cover them rather than quietly widen scope — **each is flagged in the checklist (§3) as a "re-denomination completion" for you to veto independently:**
- **(dial 1 completion)** player **researcher / legacy / unproductive doom** coefficients — sized for the strategic turn, billed ~22×/month. Without this, safety researchers at -3.5/tick pin doom to 0 (immortal-ish) and mortality collapses onto bankruptcy artifacts (the §I1 inversion).
- **(dial 3 completion)** ledger **fuses + interest + exposure/blackmail cadence** — fuses of 3-8 *ticks* meant loans billed within the same fiction-month; "priced as a loan over months" is impossible until fuses are month-scale.

I did **not** touch dial 5 (Attention/window scarcity): `attention.per_month = 20` and window `attention_cost` are unchanged, so these results isolate dials 1-4.

---

## 1. Targets used — statuses + the reasoning behind each number

T1-T8 are the **coordinator's** interim targets, derived from ADR anchors (ADR-0009 fiction: 2017 start; ~2027 early loss ≈114 mo; noob death ~24 mo; ADR-0002 mortality) + Pip's dial rulings; T9 is **Pip's own ruling** from the #638 review. Per that review, each target now carries its reasoning — why this number, and what breaks if it drifts — so future-us can re-derive instead of cargo-culting.

| # | Target | Status (final) |
|---|---|---|
| T1 | do_nothing median **12-18 months** | ✅ HIT (14.0) |
| T2 | safety_lean & reserve_heavy **1.5-2.5× do_nothing** | ❌ MISS (1.18× / 1.36×) — bankruptcy/variance-bound (Finding B) |
| T3 | random_walk **between do_nothing and safety_lean** | ❌ MISS (8.0, below band) — but now clearly above the reckless cluster |
| T4 | greedy_overcommit **faster than do_nothing, not sub-month** | ✅ HIT (7.0 < 14, min 6) |
| T5 | loan_desperation **mid-range, predominantly ledger-rooted** | ✅ HIT (7.0, 8/8 ledger-rooted) |
| T6 | a single **DEFER survivable**, doom over months, capped per tick | ✅ HIT (per-bill cap 10, slow-bleed rollover — see explainer below) |
| T7 | start doom **meaningfully below 50 (15-25)** | ✅ set to **20** |
| T8 | **HARD (ADR-0002):** every policy dies; no run >400 months | ✅ HIT (max 45 mo, 0 immortal) |
| T9 | **Pip (#638): no standard run finishes in < 6 months** | ✅ HIT (min months: greedy 6, loan_desperation 6) |

**T1 — why 12-18 months.** ADR-0009 pins a noob death at ~2 fiction-years (~24 months) and an early-competent loss at ~2027 (~114 months). Passive non-play must be *worse than* a noob actually playing (else engagement is punished — the #637 shame finding) but not so fast the world reads as arbitrary; 12-18 puts do_nothing at roughly half the noob anchor. Drift down → month cadence stops mattering (too few plan screens to learn from); drift up past ~24 → passivity outperforms noobs and the shame finding returns.

**T2 — why 1.5-2.5×.** Sensible active play must *visibly* beat passivity (below ~1.5× the difference reads as noise against run variance at n=8, σ≈2-3 months) but must not beat it so hard that safety-spam becomes the only line (above ~2.5× we re-create #637's "only-safety-or-nothing" dominance in inverted form). What breaks if ignored: player learning — the game can't teach "your choices matter" if the best and worst sensible plays land within variance of each other.

**T3 — why "between".** random_walk is the fuzzer: half its actions are sensible, half self-harming, so its expected value should land between pure-passive and pure-sensible. If it lands *below do_nothing*, random engagement is punished versus abstention — the exact pathology #637 flagged. (Final: 8.0 vs do_nothing 14 — still below, but the reading changed: random_walk's deaths are 28/30 ledger-rooted, i.e. it dies of the ~40% of its actions that are genuinely reckless ledger/capability moves, not of engaging per se. Whether that satisfies the *spirit* is Pip's call — §7.3.)

**T4 — why "faster, not sub-month".** Capability-rushing is the fiction's cautionary tale — it must be a *bad gamble*, so faster than passive; but a sub-month death means the player never experiences a single plan cycle, converting "bad gamble" into "undiagnosable instant loss." Breaks legibility if ignored (the punishment must arrive where the player can see the cause).

**T5 — why mid-range + ledger-rooted.** The Liability Ledger is the flagship mechanic (ADR-0003); the policy built to abuse it must die *of it* (root-cause attribution says "ledger", not "doom") or the flagship has no teeth. Mid-range because debt abuse should out-die sensible play but not instantly (that's T9's floor). Breaks if ignored: either the ledger is cosmetic (deaths not ledger-rooted) or it's a trap-door (instant deaths — T9 violation).

**T6 — why capped-per-tick (plain-language explainer, per Pip's request).** *What DEFER minted before:* deferring certain windows created a `desperation_payroll` ledger entry — a SECRET governance debt of $8,000-14,000 compounding at **35% per day-tick** with a 3-tick fuse. Three days later it billed ~$19k-34k against a governance stock of **50**; the deficit converted to doom at 3.5/1000 → **+99…+143 doom in one tick**, from a 100-point gauge. *Why that was an accounting collision, not a design:* those magnitudes were sized for the pre-L1 strategic turn (35%/turn was "35% per strategic beat", not per day) — AND the doom never actually landed anyway, because of the clobber bug (Finding A): the killing number existed only in the cause log while the run actually died of rival doom. So the "one-click death button" was two stacked accounting errors, not a mechanic anyone chose. *What the cap + roll-over means in play:* a defaulted bill now costs at most **10 doom (and 10 rep) on the tick it lands**; any remainder is not forgiven but rolls forward as a fresh ledger entry that re-bills (capped again) every ~9 ticks — a **bleed, not a guillotine**. A single DEFER stings, a debt spiral still kills, but it kills over weeks-months with every hit named in the death chain. *Why ~10-15:* the cap must be large enough that a default outweighs a month of ambient pressure (~+4-6 doom/month for do_nothing — a cap below ~8 would make defaults ignorable) and small enough that doom-20 starts survive one mistake (a cap above ~25 recreates the guillotine from low doom). 15 was the opening value; the T9 round settled on **10** so a monthly *pair* of maturing loans (+20) stays under a lethal single-tick spike.

**T7 — why 15-25.** Pip's ruling verbatim: "the default doom level for a 2017 spawn should be lower... the steady build is the early stage grind." Mechanically the start level is the player's error budget: at 50, half the gauge is spent before turn 1 and any +15 event is a quarter of remaining life; at 20, the early game reads as low-and-grinding-up and survives T6-scale hits. Below ~15 the doom gauge stops signalling at all in year one.

**T8 — why 400 months hard.** ADR-0002's mortality guarantee (no immortal runs) with ADR-0009's outer fiction anchor: 2040 ≈ the 1% run ≈ 270 months. 400 ≈ 1.5× that anchor — any run past it means a policy has *escaped* the mortality curve, which breaks the ladder (ADR-0002 scoring assumes every run terminates).

**T9 — why a 6-month floor (Pip, #638 review).** "We should be surprised if ANY standard run finishes in less than 6 months" — the early game must be nearly unlosable *with respect to compounding debt*: a player can **set up** ruin early (bad loans, deferred bills, secret liabilities) but cannot **complete** it early. Mechanically: every debt instrument's path from mint to lethal must span months (fuses ~3-4 fiction-months, capped bills, slow-bleed rollover, monthly-not-daily risk triggers). What breaks if ignored: the new-player experience — a first-session death inside the first few plan screens is undiagnosable and reads as arbitrary, exactly the #637 pathology one level up. Aggressive-but-legal play (greedy_overcommit, loan_desperation) counts as "standard" for this floor.

---

## 2. Per-iteration log

Each iteration = adjust constants → run the full 72-run sweep → table vs targets → verdict. Median **months** survived per policy (death-cause split in parens: doom/ledger).

| Iter | Key changes | do_nothing | safety_lean | reserve_heavy | random_walk | greedy | loan_desp | Mortality | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **#637 base** | *(none)* | 0 | 0 | 0 | 0 | 0 | 0 | all die tick 4-9 | nothing survives month 0 |
| **I1** | rival scale 0.03, overhang 0.003, base 0.1, momentum accum 0.05/cap 2, **start doom 20**, doom-cap+rollover+**doom-routing fix** (max_doom_per_bill 15), payroll sev 2500/1500 | 9 | **5** | **5.5** | 2 | 0 | 1 | PASS | doom re-denom works but **INVERSION**: safety dies *faster* than passive (bankruptcy→`unproductive`(0.5)×momentum explodes doom); greedy sub-month |
| **I2** | **researcher/legacy/unproductive doom ÷~20** (safety -0.18, cap +0.15, unproductive 0.025); **ledger fuses ×~11-15 + interest ÷~20** (loan 44/0.012, payroll 33, etc.); rival scale 0.02, overhang 0.002, base 0.06 | **14 ✓** | 15.5 | 15.5 | 4.5 | 5 | 1 | PASS | inversion fixed, do_nothing in band; safety only **1.1×**; ledger still fast |
| **I3** | safety -0.18→**-0.28** (interp -0.24, align -0.25); payroll sev **1200/800**; **rep cap 15** (max_rep_per_bill) | 14 | 15.5 | 16 | 6 | 5 | 2 | PASS | safety strengthen = **0.0 effect** (bankruptcy-bound, Finding B); rep-cap lifts random/loan a little |
| **I4** | `doom_per_unpaid_1000` 3.5→**1.5** | 14 | 15.5 | 15.5 | 6 | 5 | 2 | PASS | ledger *doom* isn't the binding killer for random/loan → near-zero move |
| **I5** | **exposure_chance 0.15→0.007**, blackmail fuse 2→22/interest 0.5→0.02 | 14 | 15.5 | 16 | 6 | 5 | **4** | PASS | loan_desperation exposed as **rep-collapse via secret-exposure** (per-tick chance); re-denom → 8/8 ledger, tighter (4-5 mo) |
| I6 *(reverted)* | rep_per_unpaid 2→1, expose rep 4→2 | 14 | 15.5 | 16 | 6 | 5 | 4 | PASS | **no target benefit** → reverted (brief: "don't calibrate teeth away") |
| **MERGE** | merge `main` (#631/#633/#635 event fixes + window-pop guard; **no dial change**) | 14 | **20** | **19** | 6 | 5 | 4 | PASS (max 45) | main's event economy lifts safety 1.1×→~1.4×; do_nothing/greedy/loan stable |
| I7 *(reverted)* | safety_base -0.28→-0.35 (post-merge probe) | 14 | 18.5 | 19 | 6 | 5 | 4 | PASS (max 49) | median **not** coefficient-sensitive (only tail max grew) → reverted; confirms Finding B |

### T9 round (post-review: Pip's 6-month floor; levers = dial-3 pricing + per-tick cadence artifacts only; ambient doom untouched — do_nothing stayed byte-identical at 14 throughout)

| Iter | Key changes | do_nothing | safety_lean | reserve_heavy | random_walk | greedy | loan_desp (min) | Mortality | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **T9-A** | **`risk.trigger_scale_per_tick` NEW 0.045** (risk-pool triggers were pool/100 per DAY-TICK — greedy's hidden +2-doom drip); loan fuse 44→66, desperation 33→44, both interest 0.012→0.009 | 14 | 16.5 | 19 | 7 | **7** | 6.0 (5) | PASS | greedy clears the floor; loan_desp median 6 but min 5. safety_lean 20→16.5 is rng-stream jitter (risk draws shift every later roll; n=8) |
| T9-B *(kept, null)* | loan fuse 66→77, desperation 44→55 | 14 | 16.5 | 19 | 6 | 7 | 6.0 (5) | PASS | **no effect** — fuse timing no longer the binding constraint |
| T9-C | `doom_per_unpaid_1000` 1.1→0.9; `funding_strings` ×0.15→×0.10 | 14 | 16.5 | 19 | 6.5 | 7 | 6.0 (5) | PASS | drip −30% yet death turns barely move — distinct capped bills dominate |
| T9-D *(kept, null)* | `rollover_fuse_ticks` NEW 3, then 8 | 14 | 16.5 | 19 | 7 | 7 | 6.0 (5) | PASS | loan_desp byte-identical → rollover lands at/after death for this bot; kept anyway (it sets the bleed cadence for a HUMAN's single mega-default) |
| **T9-G** | **`max_doom_per_bill` 15→10** | 14 | 16.5 | 19 | 7 | 7 | 6.0 (5) | PASS | doom-path deaths clear to 6-7 mo; the one sub-6 run left is a REP collapse |
| **T9-H** | **`max_rep_per_bill` 15→10; `expose.rep_per_1000` 4.0→2.5** | 14 | 16.5 | 19 | 7 | 7 | **6.0 (6)** | PASS | **T9 floor cleared** — min 6 everywhere |
| **T9-FINAL** | interest 0.009→**0.008** + whole-unit principal rounding (JSON float round-trip determinism — see §7.2); merge #639/#640 | **14** | **16.5** | **19** | **8** | **7 (6-13)** | **7.0 (6-8)** | **PASS (max 45)** | final state; loan_desp lifts to 7 as smaller compounding keeps the Ponzi carousel solvent longer |

**Why the doom-conversion dead-ends (T9-B/C/D null results) matter:** they localise the death engine. loan_desperation's finisher is not fuse timing, not the drip rate, not the rollover — it is the **monthly PAIR of maturing $60k+ loans, each a capped bill, landing the same tick** once the borrow-to-pay carousel goes insolvent (~month 4.5). Only the per-bill caps (T9-G/H) touch that. This is the measured shape of "set up early, complete late": setup = the carousel, completion = the maturity train, and the caps set the train's speed.

---

## 3. Final constants — status after the #638 review round

All in `godot/data/balance/defaults.json` unless noted. Review status: **✔A = approved as-is by Pip's #638 review** (dials 1, 2, 3, both code caps, all ⚑ re-denomination completions, and the doom-routing fix); **◐I = accepted as interim** (dial 4 momentum); **☐N = NEW this round (T9) — awaiting Pip's ruling**. ⚑ marks re-denomination completions (all blessed: "if we discovered more environments where the game is interacting with a different per-tick speed than makes sense to a human… that's awesome").

### Dial 1 — rival + per-tick doom re-denomination *(✔A approved)*
- ✔A `rivals.per_tick_doom_scale` — **NEW → 0.02** (multiplies summed rival per-action+overhang doom in `turn_manager`; 1.0 = pre-L1)
- ✔A `rivals.capability_overhang_doom_per_progress` — 0.025 → **0.002**
- ✔A `doom.base_per_turn` — 1.0 → **0.06**
- ✔A ⚑ `doom.researcher.safety_base` — -3.5 → **-0.28**
- ✔A ⚑ `doom.researcher.capabilities_base` — 3.0 → **0.15**
- ✔A ⚑ `doom.researcher.interpretability_base` — -3.0 → **-0.24**
- ✔A ⚑ `doom.researcher.alignment_base` — -3.2 → **-0.25**
- ✔A ⚑ `doom.legacy_capability_per_researcher` — 3.0 → **0.15**
- ✔A ⚑ `doom.legacy_safety_per_researcher` — 3.5 → **0.18**
- ✔A ⚑ `doom.unproductive_per_staff` — 0.5 → **0.025** *(this one killed the I1 inversion)*

### Dial 2 — lower start doom *(✔A approved)*
- ✔A `starting_resources.doom` — 50.0 → **20.0** *(scenarios still override on top for late-league spawns)*

### Dial 3 — DEFER/ledger priced as a loan, not a one-click death *(✔A approved at #638 values; ☐N rows moved further for T9)*
- ✔A→☐N `ledger.max_doom_per_bill` — NEW 15.0 at review → **10.0 after T9** *(T9-G: the monthly maturity PAIR must stay under a lethal single-tick spike)*
- ✔A→☐N `ledger.max_rep_per_bill` — NEW 15.0 at review → **10.0 after T9** *(T9-H: symmetric — the last sub-6-month death was a rep collapse)*
- ✔A→☐N `ledger.doom_per_unpaid_1000` — 3.5 → 1.5 at review → **0.9 after T9**
- ✔A `ledger.desperation_payroll.severity_base` — 8000 → **1200**
- ✔A `ledger.desperation_payroll.severity_spread` — 6000 → **800**
- ✔A→☐N ⚑ `ledger.desperation_payroll.fuse_turns` — 3 → 33 at review → **55 after T9** *(~2.5 fiction-months to first bill)*
- ✔A→☐N ⚑ `ledger.desperation_payroll.interest_rate` — 0.35 → 0.012 at review → **0.008 after T9** *(+ float round-trip constraint, §7.2)*
- ✔A→☐N ⚑ `ledger.loan.fuse_turns` — 4 → 44 at review → **77 after T9** *(~3.5 fiction-months)*
- ✔A→☐N ⚑ `ledger.loan.interest_rate` — 0.25 → 0.012 at review → **0.008 after T9** *(≈ ~19%/fiction-month compounding)*
- ✔A→☐N ⚑ `ledger.funding_strings.fuse_turns` — 6 → 66 at review → **88 after T9** *(~4 fiction-months)*
- ✔A→☐N `ledger.funding_strings.principal_multiplier` — 0.15 → **0.10 after T9** *(governance strings bill ~5k, ~4.5 doom — drip, not spike)*
- ✔A ⚑ `ledger.funding_strings.interest_rate` — 0.05 → **0.0025**
- ✔A ⚑ `ledger.staff_rider.fuse_turns` — 8 → **88**
- ✔A ⚑ `ledger.staff_rider.interest_rate` — 0.02 → **0.001**
- ✔A ⚑ `ledger.exposure_chance_per_turn` — 0.15 → **0.007** *(per-tick secret-exposure was near-instant; now ~14%/month per secret)*
- ✔A ⚑ `ledger.blackmail.fuse_turns` — 2 → **22**
- ✔A ⚑ `ledger.blackmail.interest_rate` — 0.5 → **0.02**
- ☐N `ledger.expose.rep_per_1000` — 4.0 → **2.5** *(T9-H: exposure rep was finishing runs at month 5)*
- ☐N `ledger.rollover_fuse_ticks` — **NEW → 8** *(bleed cadence of a capped bill's residual: one capped hit every ~9 ticks; null-effect on the bots but sets how fast a HUMAN's single mega-default completes)*

### Dial 4 — momentum re-tune *(◐I accepted as INTERIM; now a switch per the ruling)*
- ◐I `doom.momentum_accumulation_rate` — 0.15 → **0.05**
- ◐I `doom.momentum_cap` — 8.0 → **2.0**
- ☐N `doom.momentum_enabled` — **NEW → 1.0** *(the ruled kill-switch: 0 = momentum contributes nothing)*
- ☐N `doom.momentum_weight` — **NEW → 1.0** *(scales the contribution without touching the accumulator shape)*

> **Momentum explainer (refresher owed to Pip — what this mechanic even is).**
> *What it does:* every tick, the doom system sums its raw sources (base + rivals + researchers + events…), then feeds a fraction of that raw change into an accumulator: `momentum += raw_change × accumulation_rate`, clamped to ±`cap`, decayed by ×`decay_rate` (0.92) each tick. The accumulator's current value is then **added on top of** the raw change. So momentum is a *trend amplifier*: sustained rising doom makes doom rise faster ("doom spiral"), sustained falling doom makes it fall faster ("safety flywheel"). It is symmetric and self-decaying — stop the trend and the bonus fades ~8%/tick.
> *Why it existed:* Phase-1 doom design (pre-workshop-1, `doom_system.gd` "Path of Exile style" scaffold) wanted runs to feel like they had inertia — a run going badly should *feel* like it's snowballing rather than random-walking.
> *What the retune did and why:* the old values (rate 0.15, cap 8) were sized for per-strategic-turn doom changes of ±5-15. Under L1 the same accumulator runs per day-tick on the same big per-tick swings, so it saturated to its cap almost immediately and added a near-constant +8/tick — a third of the #637 wall was just momentum echoing the rival over-billing. At the re-denominated slope (±0.1-0.5/tick) the old cap would be 16-80× the underlying signal. New values (rate 0.05, cap 2) make it a *flavour* on the new slope: worst case ~+2/tick during a sustained spiral, typically ±0.1-0.3.
> *Worked example (final constants):* do_nothing's steady state is ~+0.2 raw doom/tick. Each tick momentum gains 0.2×0.05 = +0.01 and decays ×0.92, converging to ≈ 0.01/(1−0.92) ≈ **+0.12/tick** — i.e. momentum adds ~60% on top of a sustained slow burn (visible over a month: ~+2.6 of do_nothing's ~+4-6/month), but a single bad tick (say a +10 capped bill) only seeds 10×0.05 = +0.5 that halves within ~8 ticks. One-off shocks fade; sustained trends compound. Flip `momentum_enabled` to 0 and do_nothing's month-slope drops ~35-40% — that is the size of the switch you'd be throwing.
> *Switch semantics:* while disabled, the accumulator still ticks (velocity/trend readouts stay live, and re-enabling mid-run behaves sanely); only the doom *contribution* is zeroed.

### Code changes (behaviour, not just numbers)
- ✔A `turn_manager.gd` `_step_process_rival_turns` — multiply summed rival doom by `rivals.per_tick_doom_scale`.
- ✔A **`ledger.gd` — route ledger doom through `doom_system.add_event_doom` (Finding A fix)**, per-bill caps, residual rollover. **Approved with the ADR-0005/ADR-0015 rationale: one authority for doom writes, no parallel pipes** (see Finding A).
- ☐N `risk_pool.gd` — probabilistic trigger scaled by `risk.trigger_scale_per_tick` (**NEW → 0.045**): pool/100 was per day-tick, i.e. a pool of 40 fired ~9 events/month; now pool N ≈ N%/month. Threshold crossings (50/75/100) remain guaranteed one-shots. *(T9 lever: this was greedy_overcommit's hidden drip.)*
- ☐N `ledger.gd` — **whole-unit principal rounding** at mint + each compound step. Determinism guard, not flavour: Godot's JSON float parse is not correctly-rounded, so full-precision principals came back from a save 1 ulp off, breaking save/load deep-equality (§7.2).
- ☐N `doom_system.gd` — momentum switch (`momentum_enabled`/`momentum_weight`, see explainer).
- ✔A `test_l1_month_sweep.gd` harness — `MAX_MONTHS` 60→420 (ADR-0002 detection), m1-m6 CSV/slope columns, `MORTALITY_CHECK` line.
- ✔A `test_ledger_actions.gd` — `soonest_fuse` assertion reads the Balance fuse. Plus this round: `test_game_state.gd` (start-doom + clamp assertions read Balance), `test_death_attribution.gd` (exposure magnitudes updated to re-priced rates).

**NOT changed (dial 5, out of scope):** `attention.per_month` (20), window `attention_cost` (1), `window_demand_budget` (3).

---

## 4. Final results vs #637 baseline

72 runs, identical seeds/policies, on the merge with `main` through #640. `MORTALITY_CHECK: max_months=45, immortal_runs=0 → PASS`. All three CI gates (quick 333, integration 14, simulation 93) pass at these constants.

| Policy | #637 median (mo / death-tick) | **Final median (mo / death-tick)** | range (mo) | death-cause (doom/rep/ledger) | month-1→6 mean doom slope | target verdict |
|---|---|---|---|---|---|---|
| `do_nothing` | 0 / 6 | **14.0 / 308** | 13-15 | 10 / 0 / 0 | +3.7,3.5,4.0,5.1,5.4,4.4 | ✅ T1 |
| `safety_lean` | 0 / 8 | **16.5 / 361** | 13-21 | 8 / 0 / 0 | −6.0,−13.2,0.6,2.1,6.0,2.7 | ❌ T2 (1.18×) |
| `reserve_heavy` | 0 / 9 | **19.0 / 424** | 15-45 | 8 / 0 / 0 | −7.7,−11.6,0.5,2.6,3.8,6.0 | 🟠 T2 (1.36×) |
| `random_walk` | 0 / 6 | **8.0 / 179** | 4-13 | 2 / 0 / 28 | +3.1,1.0,1.4,4.4,8.5,9.0 | ❌ T3 (below band, above reckless) |
| `greedy_overcommit` | 0 / 4 | **7.0 / 168** | **6**-13 | 8 / 0 / 0 | +9.1,9.3,9.3,10.2,10.3,10.5 | ✅ T4 + T9 |
| `loan_desperation` | 0 / 6 | **7.0 / 160** | **6**-8 | 0 / 0 / 8 | +3.0,3.4,6.3,6.5,11.4,12.9 | ✅ T5 + T9 |

**Ordinal spread (final):** aggressive cluster `greedy 7 ≈ loan_desperation 7 < random_walk 8` clearly below careful cluster `do_nothing 14 < safety_lean 16.5 < reserve_heavy 19`, and **nothing dies before month 6** among the standard policies (T9). The #637 "only-safety-or-nothing shame finding" is **broken in direction** — active safety play beats passive, capability-rushing and debt-abuse die fastest but legibly — the unmet piece is the *magnitude* of safety's edge (T2, Finding B). Note on T2's apparent regression vs the pre-T9 snapshot (safety_lean 20 → 16.5): the risk-trigger re-denomination shifts every subsequent rng draw, and at n=8 the median jitters ±2-3 months across rng streams (range 13-21 overlapping throughout); the honest claim is "safety ≈ 1.2-1.4× passive, variance-dominated," not any single decimal.

---

## 5. Three lived-experience narratives — re-narrated at final constants

Grounded in logged runs from the final sweep (per-tick doom curve + death chain).

### 5.1 The cautious reserve-keeper — `reserve_heavy`, seed `l1sweep-reserve_heavy-00` (21 months, April 2019)
> **What the player sees.** June 2017, doom a low **20**. She banks half her Attention and pours the rest into safety — hire a researcher, run safety work, hold the reserve. It *works*: doom slides down a step or two every day, and by August it touches **0** and sits there. She handles a *lot* of interruptions cleanly — 105 windows across the run, 65 from reserve, 40 by cannibalising, none deferred into ledger trouble. Then, deep in, the story gets interesting: around **month 13 doom has crept back to 73** (the payroll bit, staff idled) — but an income beat lets her re-staff, and doom **falls again, 73 → 54 → 39**, a genuine second wind. It can't last; the treasury is bleeding (`funding_starvation` fired back at tick 48, money ends at **−$192k**) and each recovery is shallower than the last. Doom grinds up the final stretch to 100 in **April 2019 — month 21.** She dies careful, wildly respected (rep **159**), and deeply broke, of pure background pressure (`rivals 0.5, momentum 0.2`). **The lesson: safety works while you can pay for it — and paying for it is the whole game.**

### 5.2 The greedy overcommitter — `greedy_overcommit`, seed `l1sweep-greedy_overcommit-04` (7 months, Feb 2018)
> **What the player sees.** He floors it — all 20 Attention into strategic work (reserve 0), buy compute, hire capability researchers, spam capability research. Doom climbs from the first month and never once dips: `[20 → 31 → 41 → 54 → 63 → 73 → 82 → 94]` — a steady ~+10 a month, his own capability work stacking on rival pressure, with the occasional risk-event jolt (`events +3.0` on the death tick — the overhang pool coming due, now ~monthly instead of the old every-few-days barrage). He's insolvent by **tick 60** (`funding_starvation`, cash $149) but the ramp was already set. Along the way he answers 24 windows, 17 of them by **cannibalising his own plans**. **Dead February 2018, month 7 — tied-fastest cohort, exactly as a capability-rush should be: a bad gamble you get to WATCH go bad for seven months, not an ambush.** Rep 57 at the end — the world never even disliked him; it just ended.

### 5.3 The unlucky random walker — `random_walk`, seed `l1sweep-random_walk-15` (8 months, Mar 2018)
> **What the player sees.** A scattershot plan, dice for a reserve, windows answered any which way (4 reserve, 8 cannibalise, **7 deferred**, 8 ignored). Her doom line *wanders* — `[20 → 24 → 35 → 37 → 31 → 30 → 35 → 44 → 72]` — actually **falling** through months 3-5 when the dice happen to queue safety work; at month 5 she's at 30 doom and looks fine. She is not fine: seven DEFERs and a payroll insolvency (tick 119, bills $950 vs $90 cash) have quietly stacked **13 ledger entries**. Months 7-8 are the maturity train: two loan defaults land on the same tick at t165 (**+10 doom, −10 rep each** — capped, named, survivable individually), then their rolled-over residuals keep billing **+10 every nine days** (t174 ×2, t183 ×2) with a funding-strings governance deficit (+4.5) in between. Doom 44 → 72 → 100 across five weeks of visible, itemised bills. **Dead March 2018, month 8, root cause ledger — with the death chain reading like a bank statement.** The chip the game should show her: *every one of those seven DEFER clicks was a loan, and they all matured together.*

---

## 6. Legacy variables — the ADR-0015 migration lane's shopping list

Per Pip's #638 review: every constant this calibration touched or read that is marked (or behaves) Legacy / pre-workshop-1, with a one-line verdict on whether it survives the ADR-0015 migration or should die there. "Survives" = keeps a job after intermediaries own doom; "dies" = delete or absorb.

| # | Constant / surface | Where | Verdict for ADR-0015 |
|---|---|---|---|
| 1 | `doom.legacy_capability_per_researcher` / `doom.legacy_safety_per_researcher` | defaults.json → `doom_system._calculate_capability_doom`/`_calculate_safety_doom` fallback path | **Dies.** Only fires when `state.researchers` is empty (the pre-researcher-object counts). L2 deletes the legacy staff counts; the fallback path and both keys go with it. Re-denominated here only so pre-L2 sweeps aren't lying. |
| 2 | `state.capability_researchers` / `safety_researchers` / `compute_engineers` legacy count fields | game_state.gd | **Dies** (same L2 deletion). The sweep bots still hire through them. |
| 3 | `doom.base_per_turn` | defaults.json → doom_system | **Survives renamed** — but as an *intermediary input* ("background risk"), not a direct doom write; rename to per-month denomination or it will be re-mis-read. |
| 4 | `doom.status_cutoffs` | defaults.json | **Dead key already** — doom_system now reads ThemeManager's band labels (L6 unification); the Balance key is an orphan. Delete. |
| 5 | `doom.velocity_carry` / `velocity_gain` | defaults.json → `_calculate_momentum` | **Survives if momentum survives** — they only feed the trend readout. If momentum is switched off permanently, the velocity pair should move to the display layer or die. |
| 6 | `starting_resources.action_points`, `action_points.per_staff`, `difficulty.*.max_action_points` | defaults.json | **Dies with the AP pool** (L2: Attention replaces founder AP; staff get per-person actions). The sweep still budgets plans in AP — the harness will need the same migration. |
| 7 | Rival per-action doom literals (`+2/+5/+3/-0.5/-2/-3`) | `rivals.gd` `process_rival_turn` | **Migrates into data.** Flagged "remain in code (follow-up batch)" since L9. Under ADR-0015 these become intermediary contributions; my `per_tick_doom_scale` is an admitted **shim multiplying code literals** — the honest end-state is per-month rival pressure values in data, and the shim dies. |
| 8 | `salaries.*` + the `/260` workday divisor in code | defaults.json + turn_manager | **Survives re-denominated** — ADR-0009 already owes "salaries → monthly payroll." The bankruptcies capping T2 (Finding B) live here; this is the next balance lane's main lever. |
| 9 | `papers.max_decisions_per_turn` | defaults.json | **Dies** — self-documented as a #630 stopgap "superseded by ADR-0009/0012/0014 response windows." |
| 10 | `events.first_event_turn` / `max_new_events_per_turn` | defaults.json | **Survives demoted** — explicitly "the pre-L1 day-tick throttle kept for the resolution tick." Fine as tick plumbing; must never gate a decision (ADR-0009 guard rule). |
| 11 | `Ledger.DOOM_PER_UNPAID_1000` / `REP_PER_UNPAID_1000` consts | ledger.gd | **Dies** — call-site fallbacks duplicating Balance keys; keep the Balance keys only (fallback literals now stale vs tuned values, a footgun). |
| 12 | `RivalLabs.CAPABILITY_OVERHANG_DOOM_PER_PROGRESS` const | rivals.gd | **Dies** — same duplicate-fallback pattern as #11 (stale 0.025 vs tuned 0.002). |
| 13 | `GameState.TECH_DEBT_DOOM_MULTIPLIER` (0.05, threshold 20) | game_state.gd | **Migrates** — a direct doom-source write from state code; exactly the parallel-pipe class ADR-0015 exists to kill. Never re-denominated (tech debt rarely reached 20 in sweeps) — flag for the migration, don't tune blind. |
| 14 | `ReplaySimulator.MAX_TURNS` / `BaselineSimulator.MAX_TURNS` (were 200) | replay_simulator.gd / baseline_simulator.gd | **Fixed this round** (200 day-ticks ≈ 9 fiction-months — the verifier would have rejected every honest long run). Survives at 10000; consider deriving from the ADR-0002 400-month cap instead of a literal. |
| 15 | Event/action direct doom writes (`add_resources({"doom": …})`) | actions.gd, events content | **Migrates wholesale** — the un-fixed remainder of the clobber bug class (Finding A / §7.1). Every one of these is currently a silent no-op. |

**Count: 15 items** (6 die outright, 4 migrate into intermediaries/data, 5 survive with renames/re-denomination).

---

## 7. Open questions the calibration surfaced

1. **Ledger-doom clobber (Finding A) — the un-fixed remainder.** The ledger route is fixed and approved (one-authority rationale, ADR-0005/ADR-0015), but **event and action direct-doom writes (`add_resources({"doom":…})`) are STILL clobbered** — e.g. `desperation_lever`'s −10 doom "benefit" silently evaporates while its ledger cost lands, making the lever pure downside. Feeds DQ-25 (desperation-lever revisit) and Legacy item #15: the migration lane should route ALL doom writes through the authority.
2. **NEW — Godot JSON float parse is not correctly-rounded (save/load determinism hazard).** Discovered via CI: full-precision floats can come back from a save **1 ulp off** (probe: `0.009`, `0.015`, `0.045`, `0.06` corrupt; `0.008`, `0.0025`, `0.25` survive). Two guards shipped: interest rates chosen from round-trip-safe decimals, and ledger principals quantized to whole units (self-healing). **The hazard is generic** — any arbitrary-precision float in the save envelope (salaries, doom, money after multiplications) can in principle drift 1 ulp on load, which would break post-load replay verification. Worth a dedicated issue: either a round-trip-verified float serializer or systematic quantization policy.
3. **random_walk (T3) below the band by construction.** It takes self-harming ledger/capability actions ~40% of the time, so it can't match passive-optimal do_nothing without gutting the ledger (breaking T5). Final reading: 8 months, above the aggressive cluster, 28/30 ledger-rooted — it dies of its reckless moves, not of engaging. Is that an acceptable re-reading of T3, or should the random pool be reweighted?
4. **Safety's 1.5-2.5× margin (T2) needs the money economy, not a doom dial** (Finding B). Demonstrated twice: coefficient bumps do nothing to the median; main's event-economy fixes moved it. Levers for the next lane: salary re-denomination (Legacy #8, ADR-0009 owes it), cheaper/slower hiring, or a bot that doesn't overhire (breaks #637 comparability). Also note the medians are variance-dominated at n=8 (±2-3 months across rng streams) — consider n=16+ for T2-sensitive comparisons.
5. **`DeathAttribution` over-attributes to ledger.** Any death with material recent ledger damage roots as "ledger" even when ambient doom was co-proximate (random_walk 28/30 partly for this reason). Worth an EE-8 classifier review before the next tuning pass leans on the split.
6. **Momentum is now a whisper — and a switch.** At final constants it adds ~+0.1/tick steady-state (see explainer, §3). If the design wants a *legible* "doom spiral" feel, retune `momentum_weight` upward relative to the new baseline; the switch makes A/B trivial (`momentum_enabled: 0` sweep vs 1). DQ-25's solver-bot data (EE-9) could measure whether players can even perceive it.
7. **Window pacing at month grain.** do_nothing sees 63 windows over 14 months (~4.5/month, all ignorable). The 2-3/month *demand* budget holds (surplus downgrades to feed), but 4.5 offered/month may still be chatty. Re-check with dial 5 (Attention/reserve), which remains explicitly out of scope here.
8. **T9's floor is enforced by pricing, not by structure.** Nothing *prevents* a future content lane from minting a short-fuse/high-severity entry that completes ruin in month 2. Consider a structural guard (e.g. a Balance-level floor on fuse_turns, or a lint in the exploit sweep) so T9 survives content growth.

---

## 8. Repro

```
"/c/Program Files/Godot/Godot_v4.5.1-stable_win64_console.exe" --headless --path godot --import
"/c/Program Files/Godot/Godot_v4.5.1-stable_win64_console.exe" --headless --path godot \
  -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual -gselect=test_l1_month_sweep.gd -glog=1 -gexit
```
Determinism unchanged from #637: each run fixed by `(game seed, policy)`; bot choices from a separate RNG seeded `hash("<seed>|<policy>")`. Runtime ~30 s (runs last ~10-45 fiction-months now). CI is no longer hollow (#640): the quick/integration/simulation gates run GUT for real — all three pass at these constants. The sweep itself stays a manual instrument in `tests/manual` (excluded from the gates).
