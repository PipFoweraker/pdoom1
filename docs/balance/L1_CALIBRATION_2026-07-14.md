# L1 Balance Recalibration — dials 1-4 applied + iteration log

**Lane:** L1 balance-calibration · **Branch:** `l1-balance-calibration` (base `main`, was `l1-month-turn-engine` / PR #636 — squash-merged) · **Date:** 2026-07-14
**Harness:** `godot/tests/manual/test_l1_month_sweep.gd` (72 runs, same seeds/policies as #637) · **Raw data:** `docs/balance/L1_sweep_runs.csv`
**Baseline:** the overnight sweep memo `docs/balance/L1_SWEEP_2026-07-13.md` (PR #637) — under pre-rebalance constants **no policy survived even one plan-month**.

> **Headline.** After 5 measured iterations (then merged onto `main`), do_nothing lands at **14 months** (target 12-18 ✓), greedy dies fastest-but-not-instantly (✓), the ledger now bites *legibly over months* instead of as a one-tick guillotine (✓), and **every policy still dies** (max 45 months, 0 immortal — ADR-0002 ✓). **Two targets miss, both for a reason outside dials 1-4:** the safety-beats-passive *margin* — **1.43× (safety_lean 20 mo) / 1.36× (reserve_heavy 19 mo)**, a near-miss on the 1.5-2.5× band — is bounded by the bot policy's monthly-overhiring **bankruptcy** (a money/salary effect: bumping the safety coefficient +25% did *not* lift the median), and random_walk (6 mo) sits below the do_nothing↔safety band because it takes genuinely self-harming ledger/capability actions ~40% of the time. Neither is the out-of-scope Attention dial — see §Scope + §6. **Note:** the final numbers are measured on the merge with `main` (which brought #631/#633/#635 event-outcome fixes + the window-pop guard); those merged changes lifted safety from the pre-merge 1.1× to ~1.4×.

---

## ⚠️ Read this first — two load-bearing findings + a scope confession

**FINDING A — the ledger's doom teeth were INERT (probe-confirmed).** The #637 memo dramatised DEFER as a "+99…+143 doom one-click death button." **That doom never actually landed.** The turn loop overwrites `state.doom = doom_system.current_doom` every tick (`turn_manager._step_resolve_doom`), and that authority never reads `state.doom` — so the ledger's `state.doom += doom_hit` was silently **clobbered** the same tick. loan_desperation's "8/8 ledger deaths" in #637 were ordinary *rival-doom* deaths that `DeathAttribution` merely **labelled** ledger (a ledger default sat in the cause log). Probe: a governance bill computing `doom: 104.8` moved actual doom by ~0 (rivals only). **To make dial 3's target real ("DEFER's doom cost lands over subsequent months"), the ledger doom must actually land** — so this calibration routes ledger doom through `doom_system.add_event_doom` (surgical, ledger-only; event/action direct-doom writes are still clobbered — out of scope). This is a behaviour change; **Pip veto-first.**

**FINDING B — safety's advantage is bankruptcy/variance-bound, not doom-bound.** safety_lean/reserve_heavy crush doom to 0 for months, then the bot (which queues `hire_safety_researcher` *every* month) goes **bankrupt** (`funding_starvation`), its researchers go unproductive, and overhang-accelerated doom climbs to death. On the merged tree the median lands at **1.43× / 1.36×** (a near-miss), but the *median* is not coefficient-sensitive: strengthening the safety coefficient (-0.18 → -0.28 pre-merge = **0.0 months**; -0.28 → -0.35 post-merge = median **20 → 18.5**, only the lucky-tail max grew) does not lift it. The 1.5-2.5× margin is therefore **not reliably reachable via dials 1-4** (or their re-denomination): it demands the money/hiring economy (cheaper hires, or the bot not overhiring, or a salary re-denomination), which is neither a doom/ledger/momentum/start dial nor the Attention dial. What DID lift it from 1.1× to ~1.4× was merging `main`'s event-outcome fixes — an economy change, consistent with this finding.

**SCOPE CONFESSION (do not skip).** The #637 memo's dial table named only *rivals + base* (dial 1) and *DEFER→payroll* (dial 3). Measurement proved the per-tick→per-month re-denomination artifact **pervades three more surfaces that the memo did not list**, and the targets are unreachable without completing them. I extended dials 1 & 3 to cover them rather than quietly widen scope — **each is flagged in the checklist (§3) as a "re-denomination completion" for you to veto independently:**
- **(dial 1 completion)** player **researcher / legacy / unproductive doom** coefficients — sized for the strategic turn, billed ~22×/month. Without this, safety researchers at -3.5/tick pin doom to 0 (immortal-ish) and mortality collapses onto bankruptcy artifacts (the §I1 inversion).
- **(dial 3 completion)** ledger **fuses + interest + exposure/blackmail cadence** — fuses of 3-8 *ticks* meant loans billed within the same fiction-month; "priced as a loan over months" is impossible until fuses are month-scale.

I did **not** touch dial 5 (Attention/window scarcity): `attention.per_month = 20` and window `attention_cost` are unchanged, so these results isolate dials 1-4.

---

## 1. Targets used — *Fable's interim targets, veto these first*

These are the **coordinator's** interim targets, derived from ADR anchors (ADR-0009 fiction: 2017 start; ~2027 early loss ≈114 mo; noob death ~24 mo; ADR-0002 mortality) + Pip's dial rulings. **They are mine, not Pip's — veto before trusting a single number below.**

| # | Target | Status |
|---|---|---|
| T1 | do_nothing median **12-18 months** | ✅ HIT (14.0) |
| T2 | safety_lean & reserve_heavy **1.5-2.5× do_nothing** | 🟠 NEAR-MISS (1.43× / 1.36×) — bankruptcy/variance-bound (Finding B) |
| T3 | random_walk **between do_nothing and safety_lean** | ❌ MISS (6.0, below) — ordinally middling (§I5) |
| T4 | greedy_overcommit **faster than do_nothing, not sub-month** | ✅ HIT (5.0) |
| T5 | loan_desperation **mid-range, predominantly ledger-rooted** | 🟡 PARTIAL (4.0, 8/8 ledger — ledger ✓, pace low-mid) |
| T6 | a single **DEFER survivable**, doom over months, never >~15/tick | ✅ HIT (loan default caps at 15, rolls forward) |
| T7 | start doom **meaningfully below 50 (15-25)** | ✅ set to **20** |
| T8 | **HARD (ADR-0002):** every policy dies; no run >400 months | ✅ HIT (max 45 mo, 0 immortal) |

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
| **MERGE** | merge `main` (#631/#633/#635 event fixes + window-pop guard; **no dial change**) | 14 | **20** | **19** | 6 | 5 | 4 | PASS (max 45) | main's event economy lifts safety 1.1×→~1.4×; do_nothing/greedy/loan stable. **This is the final state.** |
| I7 *(reverted)* | safety_base -0.28→-0.35 (post-merge probe) | 14 | 18.5 | 19 | 6 | 5 | 4 | PASS (max 49) | median **not** coefficient-sensitive (only tail max grew) → reverted; confirms Finding B |

---

## 3. Final proposed constants — yes/no checklist for Pip

All in `godot/data/balance/defaults.json` unless noted. **☐ = please rule yes/no.** Grouped by dial; re-denomination completions marked ⚑.

### Dial 1 — rival + per-tick doom re-denomination
- ☐ `rivals.per_tick_doom_scale` — **NEW → 0.02** (multiplies summed rival per-action+overhang doom in `turn_manager`; 1.0 = pre-L1)
- ☐ `rivals.capability_overhang_doom_per_progress` — 0.025 → **0.002**
- ☐ `doom.base_per_turn` — 1.0 → **0.06**
- ⚑ ☐ `doom.researcher.safety_base` — -3.5 → **-0.28**  *(completion)*
- ⚑ ☐ `doom.researcher.capabilities_base` — 3.0 → **0.15**  *(completion)*
- ⚑ ☐ `doom.researcher.interpretability_base` — -3.0 → **-0.24**  *(completion)*
- ⚑ ☐ `doom.researcher.alignment_base` — -3.2 → **-0.25**  *(completion)*
- ⚑ ☐ `doom.legacy_capability_per_researcher` — 3.0 → **0.15**  *(completion)*
- ⚑ ☐ `doom.legacy_safety_per_researcher` — 3.5 → **0.18**  *(completion)*
- ⚑ ☐ `doom.unproductive_per_staff` — 0.5 → **0.025**  *(completion; this one killed the I1 inversion)*

### Dial 2 — lower start doom
- ☐ `starting_resources.doom` — 50.0 → **20.0** *(scenarios still override on top for late-league spawns)*

### Dial 3 — DEFER/ledger priced as a loan, not a one-click death
- ☐ `ledger.max_doom_per_bill` — **NEW → 15.0** *(code: cap + month-spread rollover in `ledger.gd`)*
- ☐ `ledger.max_rep_per_bill` — **NEW → 15.0** *(code: caps the rep-collapse guillotine on money-defaults)*
- ☐ `ledger.doom_per_unpaid_1000` — 3.5 → **1.5**
- ☐ `ledger.desperation_payroll.severity_base` — 8000 → **1200**
- ☐ `ledger.desperation_payroll.severity_spread` — 6000 → **800**
- ⚑ ☐ `ledger.desperation_payroll.fuse_turns` — 3 → **33**  *(completion)*
- ⚑ ☐ `ledger.desperation_payroll.interest_rate` — 0.35 → **0.012**  *(completion)*
- ⚑ ☐ `ledger.loan.fuse_turns` — 4 → **44**  *(completion)*
- ⚑ ☐ `ledger.loan.interest_rate` — 0.25 → **0.012**  *(completion)*
- ⚑ ☐ `ledger.funding_strings.fuse_turns` — 6 → **66**  *(completion)*
- ⚑ ☐ `ledger.funding_strings.interest_rate` — 0.05 → **0.0025**  *(completion)*
- ⚑ ☐ `ledger.staff_rider.fuse_turns` — 8 → **88**  *(completion)*
- ⚑ ☐ `ledger.staff_rider.interest_rate` — 0.02 → **0.001**  *(completion)*
- ⚑ ☐ `ledger.exposure_chance_per_turn` — 0.15 → **0.007**  *(completion; per-tick secret-exposure was near-instant)*
- ⚑ ☐ `ledger.blackmail.fuse_turns` — 2 → **22**  *(completion)*
- ⚑ ☐ `ledger.blackmail.interest_rate` — 0.5 → **0.02**  *(completion)*

### Dial 4 — momentum re-tune
- ☐ `doom.momentum_accumulation_rate` — 0.15 → **0.05**
- ☐ `doom.momentum_cap` — 8.0 → **2.0**

### Code changes (behaviour, not just numbers) — veto explicitly
- ☐ `turn_manager.gd` `_step_process_rival_turns` — multiply summed rival doom by `rivals.per_tick_doom_scale`.
- ☐ **`ledger.gd` — route ledger doom through `doom_system.add_event_doom` (Finding A fix), cap per bill at `max_doom_per_bill`, roll the residual forward as a fuse-1 doom entry** (full teeth, delivered over months). Rep money-default hit capped at `max_rep_per_bill` (no rollover — doom carries mortality).
- ☐ `test_l1_month_sweep.gd` harness — `MAX_MONTHS` 60→420 (ADR-0002 detection), m1-m6 CSV/slope columns, `MORTALITY_CHECK` line.
- ☐ `test_ledger_actions.gd` — `soonest_fuse` assertion now reads the Balance fuse (was hardcoded `3`).

**NOT changed (dial 5, out of scope):** `attention.per_month` (20), window `attention_cost` (1), `window_demand_budget` (3).

---

## 4. Final results vs #637 baseline

72 runs, identical seeds/policies, **on the merge with `main`**. `MORTALITY_CHECK: max_months=45, immortal_runs=0 → PASS`.

| Policy | #637 median (mo / death-tick) | **Final median (mo / death-tick)** | range (mo) | death-cause (doom/rep/ledger) | month-1→6 doom slope | target verdict |
|---|---|---|---|---|---|---|
| `do_nothing` | 0 / 6 | **14.0 / 308** | 13-15 | 10 / 0 / 0 | +3.7,3.5,4.0,5.1,5.4,4.4 | ✅ T1 |
| `safety_lean` | 0 / 8 | **20.0 / 444** | 13-24 | 7 / 1 / 0 | −6.0,−13.2,0.6,2.7,5.2,4.9 | 🟠 T2 (1.43×) |
| `reserve_heavy` | 0 / 9 | **19.0 / 424** | 15-45 | 8 / 0 / 0 | −7.7,−11.6,0.5,2.6,3.8,6.0 | 🟠 T2 (1.36×) |
| `random_walk` | 0 / 6 | **6.0 / 138** | 2-13 | 2 / 0 / 28 | +3.3,1.7,1.8,4.1,8.3,15.8 | ❌ T3 (below) |
| `greedy_overcommit` | 0 / 4 | **5.0 / 119** | 4-7 | 8 / 0 / 0 | +9.0,12.3,16.6,16.7,15.2,11.4 | ✅ T4 |
| `loan_desperation` | 0 / 6 | **4.0 / 91** | 4-5 | 0 / 0 / 8 | +3.2,8.1,7.2,21.2,29.1,— | 🟡 T5 (ledger ✓) |

**Ordinal spread (final):** reckless cluster `loan_desperation 4 < greedy 5 < random_walk 6` clearly below careful cluster `do_nothing 14 < reserve_heavy 19 < safety_lean 20`. The #637 "only-safety-or-nothing shame finding" is **broken in direction** — active safety play now beats passive by ~1.4×, capability-rushing dies fastest — the unmet piece is only that safety's edge is a *near-miss* on the 1.5-2.5× band (T2).

---

## 5. Three lived-experience narratives — re-narrated at final constants

Grounded in logged runs from the final sweep (per-tick doom curve + death chain).

### 5.1 The cautious reserve-keeper — `reserve_heavy`, seed `l1sweep-reserve_heavy-00` (21 months, April 2019)
> **What the player sees.** June 2017, doom a low **20**. She banks half her Attention and pours the rest into safety — hire a researcher, run safety work, hold the reserve. It *works*: doom slides down a step or two every day, and by August it touches **0** and sits there. She handles a *lot* of interruptions cleanly — 105 windows across the run, 65 from reserve, 40 by cannibalising, none deferred into ledger trouble. Then, deep in, the story gets interesting: around **month 13 doom has crept back to 73** (the payroll bit, staff idled) — but an income beat lets her re-staff, and doom **falls again, 73 → 54 → 39**, a genuine second wind. It can't last; the treasury is bleeding (`funding_starvation` fired back at tick 48, money ends at **−$192k**) and each recovery is shallower than the last. Doom grinds up the final stretch to 100 in **April 2019 — month 21.** She dies careful, wildly respected (rep **159**), and deeply broke, of pure background pressure (`rivals 0.5, momentum 0.2`). **The lesson: safety works while you can pay for it — and paying for it is the whole game.**

### 5.2 The greedy overcommitter — `greedy_overcommit`, seed `l1sweep-greedy_overcommit-03` (5 months, Dec 2017)
> **What the player sees.** He floors it — all 20 Attention into strategic work (reserve 0), buy compute, hire capability researchers, spam capability research. Doom climbs from the first day and never stops: his own capability work stacks on rival pressure, and the windows he can't afford to handle from an empty reserve get **cannibalised** (the `events +2.0` spikes on the per-tick curve — a jolt every few days). He's bankrupt by **tick 40** (`funding_starvation`, cash $10) but it barely matters; the doom curve `[20 → 29 → 48 → 65 → 85 → 97]` was already a ramp. **Dead December 2017, month 5 — the fastest cohort, exactly as a capability-rush should be.** He never gets the slow grind the careful players earn; aggression buys a short, bright, doomed run (rep **32** at the end).

### 5.3 The unlucky random walker — `random_walk`, seed `l1sweep-random_walk-04` (6 months, Jan 2018)
> **What the player sees.** A scattershot plan, dice for a reserve, windows answered any which way (2 reserve, 9 cannibalise, 1 defer, 9 ignore). Doom climbs a steady middling line — `[20 → 30 → 40 → 54 → 65 → 78]` — neither the careful players' dive nor the greedy ramp. Under the surface the ledger is quietly filling: a `funding_starvation` payroll at tick 53, a governance deficit from an exposed payroll coinflip (+4.3 doom), a contractor's rider (+2.0). She keeps her nose above water until **month 6**, when a big payroll bill she can't cover (`funding_starvation`, bills $102k vs $65k cash) tips into a **loan default — capped at +15 doom, −15 rep** (no single guillotine, exactly the new rail). **Dead January 2018, month 6, root cause ledger** even though the treasury was near-flush moments earlier. The chip the game should show her: *the deferred bills came home together.*

---

## 6. Open questions the calibration surfaced

1. **Ledger-doom clobber (Finding A) — is the surgical fix the right one?** I routed *only* the ledger's doom through `doom_system` so its bills land. **Event and action direct-doom writes (`add_resources({"doom":…})`, e.g. `desperation_lever`'s own −10 "benefit") are STILL clobbered.** So `desperation_lever` is currently pure downside (its −10 evaporates, its ledger cost lands). Do you want the global overwrite fixed (all direct doom writes land), or is the ledger-only fix the intended seam? This is arguably a bug worth its own issue.
2. **Safety's 1.5-2.5× margin (T2) needs the money economy, not a doom dial.** The bot's monthly-overhiring bankruptcy caps safety's *median* at ~1.4× (a near-miss) — and it's already demonstrated to respond to the economy, not the doom dial: merging `main`'s event-outcome fixes lifted it 1.1×→1.4×, while a +25% safety-coefficient bump did nothing to the median. Levers that would close the last ~0.1-0.6×: (a) a smarter safety policy that doesn't re-hire every month (harness change — but breaks #637 comparability), (b) cheaper hires / a salary re-denomination (ADR-0009 flagged "salaries → monthly payroll" as pending), (c) making rivals/overhang a *real* fight vs. safety rather than a floor-at-0 (needs stronger, later-ramping overhang). Which do you want the next lane to pull?
3. **random_walk (T3) below the band by construction.** It takes self-harming ledger/capability actions ~40% of the time, so it structurally can't match passive-optimal do_nothing without gutting the ledger (which would break T5). Is "reckless-cluster, clearly below careful-cluster" an acceptable re-reading of T3, or do you want the random policy's action pool reweighted?
4. **`DeathAttribution` over-attributes to ledger.** Any death with a single ledger default in the cause log roots as "ledger," even when rival doom was the proximate killer (random_walk reads 29/30 ledger partly for this reason). Worth a classifier review (EE-8) so the split is trustworthy.
5. **loan_desperation at 4 months is low-mid.** It's cleanly 8/8 ledger-rooted and spread-over-months now, but "mid-range" might want ~6-9. Softening `desperation_payroll` severity further, or the exposure rep rate, would lift it — held back this pass to avoid weakening the ledger's bite past the "must keep biting" line.
6. **Momentum is now a whisper (cap 2, accum 0.05).** On the re-denominated slope it barely registers as flavour. If the design wants a legible "doom spiral / safety flywheel" feel, momentum may need re-strengthening *relative to the new baseline* — a deliberate re-tune once the raw slope is locked.
7. **Re-check window pacing.** #637 couldn't observe a full month's window economy (nothing survived). do_nothing now sees **63 windows over 14 months** (~4.5/month, all ignored) — worth confirming the 2-3/month spawn feel holds now that months complete. Dial 5 (Attention/reserve) tuning was explicitly deferred and should follow.

---

## 7. Repro

```
"/c/Program Files/Godot/Godot_v4.5.1-stable_win64_console.exe" --headless --path godot --import
"/c/Program Files/Godot/Godot_v4.5.1-stable_win64_console.exe" --headless --path godot \
  -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual -gselect=test_l1_month_sweep.gd -glog=1 -gexit
```
Determinism unchanged from #637: each run fixed by `(game seed, policy)`; bot choices from a separate RNG seeded `hash("<seed>|<policy>")`. Runtime ~10 s. CI is hollow (#629) — this is a manual instrument; run it locally.
