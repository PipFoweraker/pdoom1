# ADR-0009 — Turn structure: plan-months, two decision speeds, day as resolution tick

- **Status:** ACCEPTED
- **Date:** 2026-07-12
- **Session:** Fable workshop #2, beat 1 (issue #604)

## Context

Workshop #1's intent was a week-based planning loop; the build drifted to day-turns with
the week surviving only as display (`game_state.gd` `TURNS_PER_WEEK`, "Day 3/5" HUD).
The drift's real shape: **decisions attached to the resolution tick.** Evidence forcing
the ruling: exploit-finder sweep (loan terms absurd at day cadence; only safety-spam
beats passive), and Pip's playtest notes (repetitive event loop, weirdly slow pacing,
*instantaneous* rewards from fundraising breaking time-feel, salary cadence off).

Pip fixed the fiction anchors this session: **2017 start; ~2027 early-competent loss,
2033 decent, 2037 hard, 2040 ≈ the 1% run.** Wall-clock ruling: a decent run is a
Civ/X-com-campaign 6–8 hours (Pip: "60% 6–8 hours, 30% evening, 10% other").
Grain arithmetic against those anchors: week ≈ 500+ turns to an early loss (dead);
month ≈ 114 / 186 / 234 / 270 turns; quarter ≈ 38 / 62 / 78 / 90.

## Decision

1. **The turn is a month.** Fixed grain, v1. Plan phase: allocate staff and founder
   hours, queue strategic actions, explicitly set reserve (slack).
2. **The day is demoted to resolution tick** — sim substrate, calendar, animation,
   score resolution. **Guard rule: no mechanic may hang a routine decision on the day
   tick.** Days are for physics and comedy.
3. **Two decision speeds** (MtG taxonomy, none of its machinery):
   - *Plan speed* ("sorcery") — only castable at the month boundary.
   - *Response windows* ("instant") — an event fires mid-month and, if a window opens,
     offers a costed menu: **HANDLE from reserve** (painless — what insurance was for) ·
     **HANDLE by cannibalizing** (delay/kill planned WIP) · **DEFER** (mints a Liability
     Ledger entry with named terms) · **IGNORE** (stated immediate consequence at list
     price). Defer/ignore pricing is the ledger beat's to detail (ADR-0010, this
     workshop).
4. **Reserve is crisp.** Unspent slack evaporates at month end. No banking ever (Pip:
   *"I don't think we can let players bank time"*). Overcommitting is a legal gamble.
5. **Strategic actions have durations.** Nothing strategic resolves instantaneously;
   effects land mid-period or at the month review (fundraising is a campaign, hiring is
   a search → offer-interrupt → onboarding drag).
6. **The badge is the date.** Public score = the exact calendar day the run died
   ("I made it to March 2034"); internals unchanged — lexicographic (days survived,
   doom-integral) per ADR-0002. Ladder texture Pip named: players overtake each other
   *by days* while decisions lock in *months* — coarse hands, fine scoreboard.

## Beacons served / violated

- **Rams #10 (as little design as possible):** one cadence ruling folds the loan-term
  absurdity, salary cadence, event pacing, and banking (deleted) — and the response menu
  reuses the ledger as its payment rail instead of adding a system.
- **Rams #6 (honest):** durations match fiction; a muted channel's events resolve
  honestly at list price; the insane 25%/turn loan becomes a *nameable* desperation tier
  at month denomination instead of a bug.
- **MaRo Interaction:** the reserve gamble makes the plan and the event stream interlock.
  (Does *not* by itself fix the dominant-line finding — that's payoffs, beat 2.)

## Interaction contract

Reads/writes ≥2 existing systems: **calendar/game_state** (month boundary, day tick),
**Liability Ledger** (DEFER intake — the flagship gains an intake valve every run hits),
**SA channels** (window gating: SA buys response windows, ADR-0004 cashed out; muting a
channel = auto-resolve without a window, priced), **replay artifact** (response records),
**exploit-finder** (policies become plan-policy × response-policy), **payroll/loans**
(re-denominated monthly).

## Rejected alternatives

- **Week (the original intent):** dead against the fiction window — ~500 turns to an
  early loss can't carry fast replays or badge legibility.
- **Quarter:** strong candidate (evening-length runs; native quarterly-report/runway
  fiction; turn numbers matching the old badge intuitions). Lost to Pip's wall-clock
  preference (6–8 hr campaigns) and early-game texture. **Revisit trigger:** month-grain
  playtests showing decent runs well over ~8 hr, or empty/repetitive mid-run months.
- **Variable/coarsening cadence** (month → quarter as the org scales): honest fit to the
  delegation fantasy (*"They can't go to all these weekly stand-ups, after all!"*) —
  parked until fixed grain demonstrably fails in playtest (Rams #10 discipline).
- **Soft reserve fallback** (idle time does low-efficiency generic work): rejected v1 —
  crisp evaporation keeps the commitment-loss legible.

## Consequences / open questions

- **Re-denomination pass:** salaries → monthly payroll; loans → %/month with cost-of-debt
  as a function (org type / hype / reputation — merges with the DEFER pricing engine,
  agenda 3+4); event density per month; `review_period_weeks` conversion.
- **Replay schema bump:** record `(event_id, window, choice, payment_source)` per
  response (ADR-0001/ADR-0006 artifact versioning; adjacent to DQ-6).
- **Exploit-finder rework:** bots need plan-level and response-level policies — real
  work, and it upgrades the instrument (next sweep question: which *response* policy
  dominates?).
- **UI:** day-tick playback needs speed control + auto-pause-on-window; the month review
  screen is the natural home for world-state progression display (Pip's playtest note:
  progression feel is weak).
- **Risk (~40%):** late-game dead air if interrupt density doesn't scale with era —
  expect a per-era density tuning pass.
- **Partially closes ADR-0008's deliberately-open wall-clock item:** decent run 6–8 hr;
  consistent with its fixed constraints (deep-run tail "several hundred turns" ≈ 270
  months to 2040; a noob death ~2 fiction-years ≈ 24 turns still costs well under an
  hour).
- **Save/fork/divergence:** Pip is open ("I don't see strong reasons why we shouldn't");
  legal under ADR-0006's verification law (a legal replay is a legal run however
  produced). Parked to backlog — it's ladder *norms*, not rules.
