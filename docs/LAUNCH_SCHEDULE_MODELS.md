# Launch Schedule Models -- four models, not a plan

Status: DECISION INSTRUMENT for Pip. Ruling of 2026-08-02 (issue #1097): recast the
launch schedule now that real time-logs exist, "presented as a couple of different
models rather than one plan." Pip picks; nothing here is a commitment until he does.

Companion tool: `tools/velocity_report.py` (regenerate with
`python tools/velocity_report.py`; output at
`art_generated/velocity/VELOCITY_REPORT.html`). All numbers below are from the
2026-08-02 run against this repo's git history (1,361 commits, 1,081 human,
2025-07-30 -> 2026-08-02).

Anti-Goodhart, Pip's own ruling, restated up front: these numbers are for sizing a
roadmap and for storytelling, never for scoring. Commits are trivially gameable and
inflate by accident -- an agent lane pushing per-step looks like ten times the work.
Every model below states its assumptions so the guess is auditable.

---

## The measured inputs

**The weighted hours estimate (Pip's portfolio, elicited method-blind 2026-08-02):**

| Window                          | Weighted hours | Human commits | PR-shaped merges |
|---------------------------------|---------------:|--------------:|-----------------:|
| League week (Mon 27 Jul -> Sun 2 Aug) | **32.7 h** | 121 | 74 |
| Last 14 days                    | **64.8 h**     | 256           | --               |

So the burst ran at roughly **32 h/week**, about **3.7-4.0 commits per hour**, and
about **2.3 PR-sized merges per hour** -- a rate a solo dev only reaches with agent
lanes running in parallel.

**The quiet baseline (Jun 3 -> Jul 3, the 30 days before the burst):** 14 human
commits across 6 active days. The estimators disagree hard here, and the
disagreement matters (see "the tension IS the question" below):

| Estimator | Hours over those 30 days | Implied h/week |
|-----------|-------------------------:|---------------:|
| B (60-min sessions, Pip's top percentage bet) | 7.1 | ~1.7 |
| D (active days x 4h, Pip's other 40% bet)     | 24.0 | ~5.6 |
| Full spread (C to D)                          | 2.2 -> 24.0 | 0.5 -> 5.6 |

**The weekly ramp** (human commits, ISO W25 -> W31 2026, i.e. weeks of Mon 15 Jun
-> Mon 27 Jul): **1, 6, 21, 24, 111, 168, then the league week itself**. This
matches the series Pip confirmed from memory (1, 7, 21, 24, 113, 171) within a
few commits of counting noise.

**The precedent, and it is uncomfortable:** this is the SECOND burst. Sep-Nov 2025
peaked at 152 commits/week (W36-W38: 48, 120, 152) and was followed by roughly six
months of near-silence -- December taper (4, 13, 5, 3), one touch in February (9),
one in late March (2), then nothing until mid-June. One prior observation is thin
evidence, but it is the only base rate this repo has for what follows a burst.

**Day-job displacement proxy:** during the 4-week burst, 63% of human commits
landed between 09:00 and 18:00 -- the hours the CEO job also wants (52% over all
history). Pip's own framing, 2026-08-01: the momentum came from "kinda sacrificing
time and attention at my CEO job, which I can't sustainably do."

---

## Ramp vs leverage -- the question that splits the models

The ramp (1 -> 6 -> 21 -> 24 -> 111 -> 168) is a curve, not a step. Two stories
generate that curve, and they predict opposite futures:

- **HOURS story:** the curve is time poured in, mostly displaced from the day job.
  When the hours are withdrawn, output reverts to the June baseline. The July
  tooling helps a little; the curve was never about tooling.
- **LEVERAGE story:** the curve is compounding capability -- agent lanes, parallel
  worktrees, honest CI, runsheets -- each week's tooling making the next week's
  hour worth more. Withdraw the hours and much of the output rate survives,
  because the human's job became directing and reviewing, not typing.

The measurement cannot fully separate them, and here is the sharp part: **the B/D
tension Pip flagged and refused to smooth IS this question in disguise.** On the
league week B and D nearly agree (32.5 h vs 32.0 h), so his 40/40 split there costs
nothing. They diverge on the QUIET window: if B is right, June was ~1.7 h/week at
~2 commits/hour, so the burst was ~20x hours and only ~2x productivity -- the hours
story. If D is right, June was ~5.6 h/week at ~0.6 commits/hour, so the burst was
~6x hours and ~6x productivity -- the leverage story. Same commits, opposite
conclusion, and the estimators are weakest exactly where it matters (sparse commits
give session models almost nothing to see). Only a logged ordinary week resolves
it. Each model below declares which story it buys.

---

## Model 1: QUIET BASELINE ("June Again")

- **Story bought:** HOURS. The burst was displaced CEO time; leverage mostly
  reverts when attention does. This is what the Sep-2025 precedent predicts.
- **Weekly budget:** 4-6 h = **2 h slack block** + 2-4 h directed work.
- **Rate assumption:** ~2 commits/hour, ~1-2 shipped changes per week.
- **Next 3 months predicts:** 100-200 commits total (against 401 in the last 30
  days alone). One system-sized feature OR a season of polish, not both.
  September and October look like a healthier December 2025.
- **Manifund 2026-09-09 (~5.5 weeks, ~25-33 h total):** no new systems. The
  deliverable is the July build itself -- polish, package, screenshot, and write it
  up well. Under this model, spending any of those hours starting something new
  is the mistake.
- **Monthly league cadence:** survivable only as an automated ritual. Seed roll +
  rebuild + league-day slack block consumes most of league week's entire budget;
  the 2 h slack block IS the league ops window that week.
- **Falsified if:** an ordinary capped August week ships at anywhere near burst
  per-hour rates.

## Model 2: WEIGHTED CRUISE ("Keep the Evenings, Keep the Tooling")

- **Story bought:** MOSTLY LEVERAGE, honestly-priced hours. Built directly on the
  portfolio numbers: burst = 32.4 h/week (last-14 weighted), of which ~60% was
  day-job displacement (the 63% office-hours share). Keep the non-displacing
  ~40%, keep the tooling.
- **Weekly budget:** 12-15 h = **2 h slack block** + ~3 h orchestration overhead
  (agent-lane setup/review has a fixed cost that does not shrink with hours) +
  7-10 h directed work.
- **Rate assumption:** ~3-3.5 commits/hour retained; ~1 PR-sized merge per hour
  after overhead.
- **Next 3 months predicts:** 400-550 commits; 2-4 feature-tier items per month;
  a visible but not explosive changelog.
- **Manifund 2026-09-09 (~65-80 h):** one focused feature arc chosen NOW, run to
  done, plus a packaging/writeup week at the end. Enough room for exactly one
  ambition; two is how this model fails.
- **Monthly league cadence:** league week runs at cruise +50% (a bounded surge to
  ~18-20 h) without touching the day job.
- **Falsified if:** the capped week's per-hour output reverts to June levels --
  then the "leverage survives at low hours" premise is wrong and this collapses
  into Model 1 with extra steps.

## Model 3: BURST CADENCE ("League-Synced Bursts")

- **Story bought:** HOURS, but SCHEDULABLE. The burst rate is real and repeatable
  -- not weekly, but as one deliberate, calendar-blocked burst week per month,
  aligned with league week (which is literally what just happened).
- **Weekly budget:** cruise weeks 6 h (**2 h slack block** + 4 h); one burst week
  per month at ~30 h with the CEO calendar cleared IN ADVANCE. ~48-50 h/month.
- **Rate assumption:** burst weeks at full leverage (~2 PR-merges/hour); cruise
  weeks at ~2 commits/hour.
- **Next 3 months predicts:** three league-day-scale pushes; 350-450 commits;
  progress arrives in visible monthly steps rather than a stream.
- **Manifund 2026-09-09:** contains exactly ONE plannable burst week (late
  August). The Manifund story writes itself around it -- IF the week is booked
  now and protected. Unbooked, this model silently degrades to Model 1.
- **Monthly league cadence:** the cadence is the model. League week = burst week;
  the ritual and the push are the same calendar object.
- **Falsified if:** the August burst week gets cannibalized by the day job -- that
  is the precedent's prediction (bursts here have ended in crashes, not cadence)
  and Pip's own "can't sustainably do" applies to unscheduled displacement.

## Model 4: PURE LEVERAGE ("The Tooling Pays Rent")

- **Story bought:** LEVERAGE, fully. Hours revert to quiet baseline; the July
  stack (agent lanes, parallel worktrees, honest CI, runsheets, this very
  velocity tooling) means each remaining hour directs several lanes of work.
  The human is a reviewer and editor, not a typist.
- **Weekly budget:** 5-6 h = **2 h slack block** (doubles as the review/inspection
  window -- on league day the slack hour paid for eleven findings, which is why
  it doubled) + 3-4 h orchestration.
- **Rate assumption:** 5-8x June's per-hour output, i.e. ~30-40 commits/week from
  ~5 hours. NOTE: the anti-Goodhart warning bites hardest exactly here -- agent
  lanes inflate commit counts precisely when this model looks like it is winning.
  Score this model ONLY in reviewed, player-visible shipped changes.
- **Next 3 months predicts:** 150-250 commits but the honest claim is 1-2 shipped
  player-visible changes per week on near-baseline hours.
- **Manifund 2026-09-09 (~28-32 h):** potentially 2-3 small feature arcs, IF
  review does not bottleneck. The known failure mode is Pip's own: silent
  wrongness -- guardrails catch bad code, not wrong state. Thin review hours are
  where wrong-but-green ships.
- **Monthly league cadence:** cheapest of all four; automation carries the league
  and the slack block inspects it.
- **Falsified if:** unreviewed lane output starts needing rework (rework rate is
  this model's real cost), or the capped week shows per-hour output was hours-
  dependent after all.

---

## Summary table

| Model | Weekly hours (incl. 2 h slack) | Ramp story | 3-month output | Manifund shape |
|-------|-------------------------------:|-----------|----------------|----------------|
| 1 Quiet Baseline | 4-6 | Hours | 100-200 commits | Package July; build nothing new |
| 2 Weighted Cruise | 12-15 | Leverage + honest hours | 400-550 commits | One feature arc + packaging |
| 3 Burst Cadence | 6 cruise / ~30 burst | Schedulable hours | 350-450 commits in steps | One protected burst week |
| 4 Pure Leverage | 5-6 | Leverage | 150-250 commits, review-bound | 2-3 small arcs, review-limited |

---

## The one question that collapses the model set

**When the hours are withdrawn, does the leverage stay?**

Operationalized -- the calibration week: pick the first ordinary week of August (no
league, no deadline), cap it at 6 hours (2 h slack block + 4 h directed), log the
actual hours honestly (the first real time-log this repo will ever have), and count
shipped player-visible changes.

- Per-hour output near league-week rates (~2 merges/hour) -> the leverage story
  holds -> Models 2 and 4 are live; choose by how many hours Pip WANTS to spend.
- Per-hour output reverts toward June (~0.5 merges/hour) -> the hours story holds
  -> Model 1 is the truth, and Model 3 is the only way to buy more than Model 1
  delivers -- at a price Pip has already said he can't pay unscheduled.

This is the same question as the B-vs-D tension in the portfolio, which Pip flagged
and asked to examine rather than smooth. He was right to leave it open: it is not a
calibration wobble, it is the fork in the schedule. One logged week answers it.
