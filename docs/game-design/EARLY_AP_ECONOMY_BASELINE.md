# Early-Game Attention / AP Economy -- BASELINE (BEFORE picture)

Read-only analysis of the CURRENT early-game founder-action economy, to inform how much
new time-consuming content (the hiring chain + onboarding + mentoring + conferences of
issues #789 and #803) the opening can absorb without overwhelming a slow / new player,
while preserving intended "suffer-hardness".

IMPORTANT SCOPE: this is the CURRENT baseline. The #789 / #803 sinks are NOT built yet.
Nothing here measures those sinks; it measures the economy they would be dropped into.
Sources are code as of branch `fable/music-session-1` (commit aaccc6a).

---

## 0. Headline

- The live founder currency is **Attention = 20 per plan-month** (`attention.per_month`,
  ADR-0011). Each action's legacy `action_points` cost is now re-read as its ATTENTION
  cost (game_manager.gd:163-165). The per-turn AP pool (3/turn) is VESTIGIAL on the
  player path.
- The action MENU is WIDE (~35 distinct action ids across 7 submenus) but the early
  BUDGET is loose: most actions cost 1-3 Attention, so 20/month funds roughly 7-20
  action-slots. A deliberate player is NOT Attention-starved early.
- The binding early constraints are MONEY (~4 hires before you must fundraise) and
  RESEARCH / PAPER prerequisites (research actions are dead until you have staff), NOT
  Attention.
- Verdict: **menu-wide but Attention-sparse**. There is real headroom, but it is
  concentrated exactly where #789/#803 want to add load (the hire -> onboard -> mentor
  cluster is already the single heaviest Attention sink).

---

## 1. The two-currency architecture (READ THIS FIRST)

There are two parallel action economies in the tree. Conflating them is the main trap.

| | Legacy AP pool | Attention (LIVE for player) |
|---|---|---|
| Where | `state.action_points` | `state.month_plan` (MonthPlan) |
| Grant | 3/turn (Standard) + 0.5/staff, per DAY-turn | 20 per PLAN-MONTH (`attention.per_month`) |
| Cadence | every workday-turn | once per calendar month; unspent reserve evaporates |
| Ruling | ADR-0011 says DELETE the global AP pool | ADR-0009/0011 founder currency |
| Status | vestigial on player path; still used by the raw turn loop | what the player actually spends |

game_manager.gd (the shipped play loop) routes every queued action through
`month_plan`: `attention_cost = action.costs.action_points`, gated against
`month_plan.available()`, then `attention_spent += attention_cost`. The `action_points`
key is stripped before the legacy affordability check. So in the shipped game, an action
labelled "1 AP" costs **1 Attention out of 20/month**, NOT 1 of 3 per turn.

A plan-month is ~21.7 day-turns (Clock: 260 workdays / 12; `financing.ticks_per_month`
= 22). So the same "1 AP" action, priced on the OLD per-turn pool, would have cost 1 of
~66 AP/month (3 x 22). The migration to Attention therefore TIGHTENED the founder action
budget by roughly 3x (66 -> 20) for identically-priced actions. This matters for every
number below and for the sim caveat in section 5.

Reactive decisions are a SEPARATE budget: `events.window_demand_budget` = 3 windows/month
(6 in endgame). Section 6 keeps proactive (Attention) and reactive (windows) load apart.

---

## 2. Starting position (turn 0, Standard difficulty)

From `balance/defaults.json starting_resources` and GameState.reset():

- money $245,000; compute 100; research 0; papers 0; reputation 50; doom 20;
  stationery 100; governance 50.
- **Staff = 0.** `safety_researchers = 0`, `capability_researchers = 0`
  (game_state.gd:254-255). The turn-0 founding seed creates EXACTLY 4 starter
  CANDIDATES in the hiring pool (each with a guaranteed hidden quirk), not employees
  (`_populate_initial_candidates`). You must hire before you have a research engine.
- Attention this month = 20.

Consequence: at turn 0 the research actions (safety/capability/publish) are inert (0
research, and research is produced by hired staff), so the genuine turn-1 decision space
is HIRING + FUNDING + upkeep, not the full menu.

(The `bootstrap` scenario is the tutorial: $500k, doom 40, still 0 staff. Easier money,
same Attention budget and same 0-staff opening.)

---

## 3. Enumerated early actions and Attention costs

Attention cost = the action's `action_points` value. "Free (0 att)" means the action has
no `action_points` key, so it costs money/resources but no Attention. Gates are unlock
conditions; "prereq" is a resource the action spends that you lack at turn 0.

### Reachable at turn 0 (no unlock, or unlock already met)

| Action | Attention | Other cost | Early prereq / note |
|---|---|---|---|
| Purchase Compute (`buy_compute`) | 0 | $50,000 | Attention-FREE compute top-up |
| Hire (instant, per spec) x7 | 1 each | $50k-$80k | safety/cap/interp/align/compute/manager/ethicist |
| Advertise a Role (`advertise`) | 3 | $8,000 | SOURCE step; candidates trickle over ~3 months |
| Work Connections (`use_connections`) | 2 | 6 reputation | SOURCE; one fast pre-vetted lead |
| Interview a Candidate (`interview_next`) | 2 | -- | resolves after ~3 ticks |
| Make an Offer (`hire_best`) | 1 | -- | resolves after ~2 ticks |
| Onboard New Hires (`onboard_next`) | 1-2/step | laptop $3k, visa $5k | laptop 1 + mentoring 2 (+visa 2 if foreign) |
| Modest Funding Round (`fundraise_small`) | 1 | 2 reputation | $30k-$60k |
| Major Funding Round (`fundraise_big`) | 2 | 8 reputation | $80k-$150k |
| Business Loan / Take Loan (`take_loan`) | 1 | -- | +$50-75k now, compounding ledger bill |
| Research Grant (`apply_grant`) | 1 | 1 paper | prereq: needs a published paper |
| Networking (`network`) | 1 | -- | +3 reputation |
| Media Campaign (`media_campaign`) | 2 | $30,000 | +reputation |
| Lobby Government (`lobby_government`) | 2 | $80k, -10 rep | political pressure |
| Public Warning (`release_warning`) | 2 | 15 reputation | risky |
| Open Source Tools (`open_source_release`) | 1 | 3 papers | prereq: needs papers |
| Order Office Supplies (`order_supplies`) | 1 | $2,000 | stationery upkeep |
| Office Maintenance (`office_maintenance`) | 1 | $5,000 | morale |
| Funding w/ Strings (`funding_strings`) | 1 | -- | +$40k, governance obligation |
| Desperation Lever (`desperation_lever`) | 1 | -- | secret compounding liability |
| Contractor (`staff_rider`) | 1 | $15,000 | +2 AP (legacy), governance rider |
| Seek / Accept Financing (`seek_financing` / `accept_financing_offer`) | 1 | -- | ADR-0013 offers |
| Pay the Bill (`pay_bills`) | 1 | cash | retire a balloon early |
| Submit Paper (`submit_paper`) | 1 | 15 research | prereq: needs research |
| Attend Conference (`attend_conference`) | 2 | travel $ | Issue #468 |
| Safety Research (`safety_research`) | 1 | 10 research | prereq: needs research (staff) |
| Capability Research (`capability_research`) | 1 | 10 research | prereq: needs research (staff) |
| Publish Safety Paper (`publish_paper`) | 1 | 20 research | prereq: needs research (staff) |

### Gated (open a few turns / conditions in)

| Action | Attention | Unlock |
|---|---|---|
| Team Building (`team_building`) | 1 | staff_min 2 |
| Safety Audit (`audit_safety`) | 2 | turn_min 5 |
| Acquire Startup (`acquire_startup`) | 2 | strategic submenu: turn_min 10 AND reputation_min 30 |
| Corporate Espionage (`sabotage_competitor`) | 3 | strategic submenu (as above) |
| Emergency Pivot (`emergency_pivot`) | 2 | strategic submenu (as above) |
| Grant Proposal (`grant_proposal`) | 1 | strategic submenu (as above) |

Submenu openers (`hire_staff`, `fundraise`, `publicity`, `operations`, `travel`,
`financing`, `strategic`) cost 0 Attention -- they only open a dialog.

### The hiring pipeline as one compound sink

A single hire via the full pipeline (not the instant $60k path) spends Attention across
FOUR steps, spread over multiple months by durations:
advertise 3 (or connections 2) -> interview 2 -> offer 1 -> onboard (laptop 1 + mentoring
2, +visa 2 if the candidate is foreign; `hiring.onboarding`). That is **~8-10 Attention
for one hire = 40-50% of a month's budget**, and it is the single densest existing sink.
This is exactly the machinery #789/#803 want to extend.

---

## 4. Decision-density verdict: menu-WIDE, Attention-SPARSE

Evidence:

- **Breadth:** ~35 distinct action ids; ~29 reachable at or near turn 0. Wide surface.
- **Budget vs cost:** 20 Attention/month against mostly 1-Attention actions => 7-20
  action-slots per month. Even a Attention-heavy month (one full pipeline hire ~8 + a
  conference 3 + upkeep 2) sits near 13/20, leaving slack.
- **The real early gates are elsewhere:** money ($245k => ~4 hires before a forced
  fundraise) and resource prerequisites (research/papers). The research half of the menu
  is inert until staff exist, so the turn-1 player faces a NARROW live choice (hire, fund,
  upkeep), not the full 29. Density RAMPS as staff and research come online.

So the opening is not a dense, every-Attention-contested puzzle. For a slow, deliberate
player it currently reads as "wide menu, comfortable budget, money is the pinch". That is
headroom -- but see the concentration warning below.

---

## 5. Headless sim (exploit / balance sweep) -- ran cleanly, with a caveat

`godot/tests/manual/test_exploit_sweep.gd` exists and is the balance instrument (20 seeds
x 5 bot policies x up to 300 day-turns, deterministic). It ran clean in ~1 min after an
`--import` pass.

CAVEAT (load-bearing): the sweep drives the RAW turn loop (`TurnManager.start_turn /
execute_turn`) reading `state.action_points` (the 3/turn vestigial pool), NOT the
MonthController/Attention path the player uses. So the bots have ~3x the founder action
budget of a live player and the sweep does NOT measure the live early-Attention economy.
Its doom-trajectory / survival signal is economy-agnostic and still useful; its
"how much can you do" signal is not transferable to the Attention question.

Survival by policy (day-turns; median):

| Policy | Outcome | Median turns | Notes |
|---|---|---|---|
| passive (do nothing) | immortal (300) 20/20 | 300 | doom drifts to ~47-50 and stabilizes; never dies |
| safety_lean | immortal (300) 20/20 | 300 | doom suppressed to ~10-46 |
| capability_rush | doom_loss 19/20 | ~150 | fastest death turn 46; doom hits 100 |
| desperation_spam | ledger_death ~20/20 | ~45 | ledger mortality bites early (turn 33-66) |
| loan_hoard | doom_loss 20/20 | ~49 | doom, root-cause ledger; dies turn 27-145 |

Reading, for the early window (first ~100 Attention = ~5 months = ~108 day-turns):
- Careful play (passive/safety) does NOT die early -- passive is immortal in this harness,
  which the sweep itself flags as a concern (no non-ledger mortality floor).
- Only aggressive capability or debt play dies inside the early window, and only in some
  seeds. The opening is forgiving for the target archetype (slow, deliberate).
- "Suffer-hardness" today comes from the LEDGER (debt policies die ~turn 45) and from
  capability-driven doom, NOT from an Attention crunch. The Attention budget is not
  currently a source of early pressure.

---

## 6. Headroom for #789 / #803 new sinks

Framing as a RANGE, not false precision. Two separate load knobs; keep them apart.

Proactive load (Attention, 20/month) -- where #789/#803 land:

- Slack today: a deliberate early month typically spends ~10-14 of 20 Attention, so there
  is roughly **4-8 Attention of unused budget per month** for a careful player, MORE for a
  passive one.
- But that slack is thin exactly where the new content targets. One full pipeline hire is
  already ~8-10 Attention; a hire + onboard + one conference is ~13-16. Stacking a longer
  chain + explicit mentoring + more conference structure onto that cluster is the fast
  path to overwhelm, because it competes with itself within one month's budget.

Estimated absorptive headroom WITHOUT changing `attention.per_month`:

- **Comfortable (deliberate depth, target archetype happy):** about **+2 to +4 new
  recurring Attention-decisions per month**, i.e. roughly **+3 to +6 Attention of added
  recurring cost**, PROVIDED the new steps largely REPLACE or absorb existing hiring/
  onboarding steps rather than pure-stack on top of them.
- **Tipping toward overwhelm (the Rick failure):** beyond roughly **+6 to +8 Attention of
  new recurring monthly cost**, or any change that pushes a single hire past ~12-14
  Attention (>60-70% of the month), a slow/new player in the first ~5 months is forced
  into hard trade-offs every month -- experienced as "too much", not "considered depth".

Reactive load (windows, `window_demand_budget` = 3/month early): if any #789/#803 step
surfaces as a response WINDOW rather than a planned Attention spend, it competes against
this budget of 3, which is much tighter. Prefer routing new hiring/mentoring/conference
steps through PLANNED Attention spend, not windows, or the overwhelm threshold arrives
far sooner (2-3 items, not 6-8).

The clean lever: `attention.per_month` is a single Balance number and the pipeline
step-costs are Balance keys (`hiring.*`). If the new content is genuinely additive, lift
`per_month` (e.g. 20 -> 24-28) in the SAME change, and the headroom scales with it. The
design ruling #789/#803 actually needs is: are these steps NEW load, or a re-shaping of
the load already in the pipeline? If re-shaping, headroom is ample; if net-new and
window-delivered, it is small.

---

## 7. Dev-tool improvement insights (the harness got better by being used)

Pip's prediction held: running the exploit-finder in anger surfaced more about the TOOL
than about the balance. The single most useful output of this run may be the punch-list
below. Framed for a future reader / blog: the balance instrument is real and deterministic
and fast, but it is currently pointed at the wrong economy and reports only the epilogue,
not the story.

What was awkward, slow, or blind this run:

1. **It measures the wrong economy (the big one).** The sweep drives the raw turn loop and
   spends `state.action_points` (the vestigial 3/turn AP pool). The shipped game spends
   Attention (20/month) via MonthController. So the instrument we reach for to answer "can
   the opening absorb more Attention load?" literally cannot see Attention. It would
   green-light pacing it never tested. FIX: a bot policy (and a run mode) that drives
   `GameManager.end_month` / MonthController, spending `month_plan`, so the sweep exercises
   the same code path the player does. This is the highest-value tooling change and a
   prerequisite for using the sweep to validate #789/#803.

2. **It reports the epilogue, not the trajectory.** Output is one row per run:
   turns, outcome, final doom, root cause. There is no per-turn or early-window telemetry,
   so you cannot see WHEN doom moves, how fast money drains, how many decisions/month were
   actually taken, or what the first 5 months looked like -- exactly the window this
   analysis needed. I had to infer the opening from static costs because the sim would not
   show it. FIX: emit a per-run time series (or at least turn-N snapshots at 5/10/25/50) of
   doom, money, staff, Attention-spent, decisions-taken. A "first 100 Attention" slice
   would have answered the density question directly.

3. **No decision-density metric at all.** The sweep counts turns survived and outcome, but
   never "how many actions did the bot actually take per month" or "how much budget went
   unspent". Density is the whole question for #789/#803, and the tool is silent on it.
   FIX: log actions-queued-per-month and Attention-utilization (%) per policy.

4. **Passive-is-immortal is stated but not quantified as pressure.** The harness tells us
   passive survives 300 turns, but not how CLOSE it came, or its doom velocity, or a
   "turns until first real pressure" number. A doom-velocity / margin-to-death metric would
   turn "immortal" into a gradient. FIX: report doom slope and min-margin, not just the
   binary survive/die.

5. **Invocation friction.** It lives in `tests/manual`, so the standard runner and CI skip
   it; you must hand-run a long `gut_cmdln` incantation AND remember the cold-class-cache
   `--import` pass first (a fresh call quits(0) silently otherwise -- the documented GUT
   trap). There is no `make sweep` / no wrapper. FIX: a one-line make target that does the
   import pass then the sweep, and prints the report path.

6. **Stale, overwriting report path.** `REPORT_PATH` is hardcoded to
   `docs/qa/EXPLOIT_SWEEP_2026-07-05.md` -- a date baked into the filename that no longer
   matches when it runs, and it overwrites in place (no history, no diff across balance
   changes). FIX: stamp the real run date / commit, and keep prior reports so balance
   drift is diff-able (the sweep's own comment asks for exactly this).

7. **Bots are hardcoded GDScript priority lists.** Adding a policy (e.g. an Attention-aware
   "deliberate slow player" that mirrors the target archetype) means editing the harness.
   There is no data-driven bot spec and, notably, no bot that models the SLOW player whose
   overwhelm we care about. FIX: a data-driven policy descriptor, and specifically a
   "deliberate" archetype bot to test the #789/#803 overwhelm hypothesis directly.

Net: this run's most durable product is a better instrument. Before #789/#803 pacing is
tuned, item 1 (drive the Attention path) and item 2 (early-window telemetry) are worth
building first -- otherwise the balance instrument is validating an economy the player
never plays.

---

## 8. Flags / caveats for the design decision

1. The exploit-finder (the balance instrument) does NOT currently exercise the live
   Attention economy -- it runs the vestigial 3/turn AP loop. Before it can validate
   #789/#803 pacing, it needs a bot policy that drives MonthController / month_plan. Right
   now it would green-light Attention load it never actually tested.
2. Passive play is immortal in the sweep; the early game has no non-ledger mortality floor.
   Adding time-consuming content does not, by itself, add difficulty -- "suffer-hardness"
   lives in the ledger and doom systems, not the action budget. Do not expect new
   Attention sinks to make the opening harder; they make it BUSIER. Those are different.
3. Much of what #789/#803 describe (source -> interview -> offer -> onboard; laptop / visa
   / mentoring; submit_paper / attend_conference) ALREADY EXISTS as Attention-costed hooks
   (`hiring.json`, `travel.json`, `hiring.onboarding`). Confirm whether the issues want to
   DEEPEN these or ADD parallel systems -- headroom differs sharply between the two.
4. Money, not Attention, is the early binding constraint (~4 hires before a forced raise).
   New sinks with money costs will bite the cash economy before they bite Attention.
