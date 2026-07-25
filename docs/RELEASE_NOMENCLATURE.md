# Release & League Nomenclature

**Status:** CANONICAL (2026-07-25, Pip). The precise definitions of every clock,
counter, and name the project uses to schedule and ship. If another doc
disagrees with this one, this one wins; fix the other. Runbook (the operational
how-to) lives in `docs/RELEASE_AND_LEAGUE_CYCLE.html`.

---

## The one-paragraph version

The game evolves on a **monthly rhythm**: each month is a named **Theme** -- one
new mechanical direction plus QoL and balance -- shipped as a **minor-version
bump that forks the leaderboard** (a new Epoch). Within each month, a fresh
weekly **Seed** gives a new board on unchanged rules. Cosmetic fixes ship any
time as **Patches** without forking. Occasionally a **Big Milestone** (public
alpha, rivals-go-live) spans several monthly Themes -- those complete when done,
not on a fixed date, and are the only "quarter-ish" objects.

**Design intent (Pip, 2026-07-25):** small monthly increments along a theme, with
QoL touch-ups and balance, is the healthy sustainable shape while in development
(~one decent feature a week is the current pace). Quarterly/big-block planning
actually *slows* this down. Players see what's coming, and choose when to patch
and re-join.

---

## The rhythm (fast to slow)

| Unit | Cadence | What it is | Forks? | Version move |
|---|---|---|---|---|
| **Seed** | weekly (every Fri) | a fresh board on UNCHANGED rules (new `seed`, same `ladder_version`) | No | none |
| **Epoch = Monthly Theme** | monthly (1st Fri) | THE evolution unit: one named theme (new mechanic + QoL + balance). The forking cut. | **Yes, by definition** | minor +1 (`0.13->0.14`) AND ladder +1 (`L2->L3`) |
| **Patch** | any time | cosmetic / honesty hotpatch, no rules change | No | patch +1 (`0.14.0->0.14.1`) |
| **Big Milestone** | occasional, multi-month | a large capability spanning several monthly Themes (e.g. "First Contact", "Rivals & News"). Completes when done, not date-locked. | n/a (a container) | (a range of minors) |

A Theme forks *by definition* -- it changes how the game plays. A pure-QoL month
with no gameplay change is just Patches, not an Epoch (ladder holds).

## The two version numbers

| Number | SSOT | Bumps when | Forks the board? |
|---|---|---|---|
| **minor** (`0.X`) | `version.txt` | each MONTHLY Theme / Epoch | **Yes** (with the ladder) |
| **patch** (`0.X.Y`) | `version.txt` | cosmetic within-month hotpatch | No |
| **ladder** (`LN`) | `ladder_version.txt` | each forking monthly Epoch (+ any rare mid-month fork) | it IS the fork counter |

Minor and ladder move **together**, monthly. Patch **never** touches the ladder.
Board key = `(seed, ladder_version)`. `sync_version.py --check` gates the two
`version.txt` fields from drifting.

## The fork rule (the only question that matters at ship time)

> **"Could two identical runs, played the same way, produce a different score,
> trajectory, or RNG stream across this change?"**
>
> - **YES** -> it forks. It's an Epoch. Bump **minor + ladder** (monthly).
> - **NO** -> it doesn't. Bump only **patch**. Ship any time.

Not breaking the ladder is a **discipline, not a hard rule** (Pip, 2026-07-23): a
strictly-dominated change (e.g. removing a do-nothing money sink) may ship as a
Patch even though it technically touches the action space, because no scoring run
is affected. Judgement, declared, not pretended away.

## Naming decision

- **Monthly Themes get a minor version + a short name** (e.g. `v0.14 "Per-tick &
  People"`). This is the primary unit.
- **Big Milestones get a NAME only** (First Contact, Rivals & News) and span
  several monthly Themes. Tracked as GitHub milestones.
- **Nothing is quarterly-locked.** The old "one minor version per quarter" pin
  was a planning artifact from before the current build pace; it is retired.
  Versions move on the monthly Theme clock.

---

## Dated calendar (2026 H2)

Epoch = first Friday of the month; Seed = every Friday. Today = Sat 2026-07-25
(AEST). Theme names for v0.14+ are provisional -- Pip names them. Confirm
operational details against `RELEASE_AND_LEAGUE_CYCLE.html`.

| Date | Day | Beat | Unit | Ver / Ladder | Forks? |
|---|---|---|---|---|---|
| Jul 24 | Fri | Build **0.13.0** shipped | Epoch | 0.13 / **L2** | shipped |
| ~Jul 27-28 | Mon-Tue | **0.13.1** hotpatch (quirks, subtitle, office, READMEs) | Patch | 0.13.1 / L2 | **No** |
| **Jul 29** | **Wed** | **Workshop 3** (mechanics) -- #811 | design | -- | -- |
| Jul 31 | Fri | Weekly Seed | Seed | -- / L2 | No |
| **Aug 7** | **Fri** | **Theme `v0.14` "Per-tick & People" (prov.)** -- per-tick resolution + people&money + WS-3 builds | Epoch+Seed | 0.14 / **L3** | **Yes** |
| Aug 14/21/28 | Fri | Weekly Seeds | Seed | -- / L3 | No |
| **Sep 4** | **Fri** | **Theme `v0.15` (prov.)** | Epoch+Seed | 0.15 / **L4** | **Yes** |
| Sep 11/18/25 | Fri | Weekly Seeds | Seed | -- / L4 | No |
| **Sep 29** | Tue | Big Milestone **"First Contact"** target (spans v0.13-v0.15) | Milestone | -- | -- |
| **Oct 2** | **Fri** | **Theme `v0.16` (prov.)** | Epoch+Seed | 0.16 / **L5** | Yes |
| ...monthly... | | Themes `v0.17`, `v0.18` through Q4 | Epoch | -- | -- |
| **Dec 30** | Wed | Big Milestone **"Rivals & News"** target | Milestone | -- | -- |

## Open reconciliation flag (owe Pip)

- **`ROADMAP.md` quarterly-pins table** still maps one-minor-version-per-quarter.
  Under this model that recasts to **monthly Themes** (a named minor each month),
  with only the two Big Milestones (First Contact, Rivals & News) surviving as
  coarse multi-month groupings. Pip to re-cast the table and name the upcoming
  Themes (`v0.14`+). Left for Pip; not rewritten unilaterally.
