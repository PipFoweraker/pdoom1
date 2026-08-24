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
time as **Patches** without forking -- but a mid-month change that DOES alter
gameplay cuts a new Epoch on the spot, so epochs outnumber minor versions and
the epoch number cannot be predicted from a release date. Occasionally a **Big Milestone** (public
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
| **Monthly Theme** | monthly (1st Fri) | THE evolution unit: one named theme (new mechanic + QoL + balance). Always a forking cut. | **Yes, by definition** | minor +1 (`0.13->0.14`) AND ladder +1 |
| **Epoch** | whenever gameplay forks | one value of `ladder_version` -- cut by every Theme AND by any mid-version gameplay change | it IS the fork | ladder +1, version moves or not |
| **Patch** | any time | cosmetic / honesty hotpatch, no rules change | No | patch +1 (`0.14.0->0.14.1`) |
| **Big Milestone** | occasional, multi-month | a large capability spanning several monthly Themes (e.g. "First Contact", "Rivals & News"). Completes when done, not date-locked. | n/a (a container) | (a range of minors) |

A Theme forks *by definition* -- it changes how the game plays. A pure-QoL month
with no gameplay change is just Patches, not an Epoch (ladder holds).

## The two version numbers

| Number | SSOT | Bumps when | Forks the board? |
|---|---|---|---|
| **minor** (`0.X`) | `version.txt` | each MONTHLY Theme / Epoch | **Yes** (with the ladder) |
| **patch** (`0.X.Y`) | `version.txt` | cosmetic within-month hotpatch | No |
| **ladder** (`LN`) | `ladder_version.txt` | each forking monthly Epoch, AND any mid-version gameplay fork | it IS the fork counter |

**The coupling runs one way only** (ruling of 2026-08-24; the declaration lives
next to its mechanism, in `tools/generate_release_horizon.py`, and is indexed in
`docs/rulings/RULINGS.md` under flavour `release-cadence`). A minor version bump
ALWAYS cuts the ladder. The ladder MAY ALSO cut mid-version, whenever gameplay
forks -- and does: three of the first six epochs were mid-version cuts, two of
them inside v0.14.x. So **ladder epochs >= minor versions, always, and the
ladder epoch is never forecastable from a version number.** A patch bump does
not by itself touch the ladder, but a patch release that changes gameplay cuts
it (v0.14.2 did). Board key = `(seed, ladder_version)`. `sync_version.py --check`
gates the two `version.txt` fields from drifting.

What a player can be told, because it is a ceiling rather than a schedule: **a
score set today stays comparable until the next MINOR version at the latest, and
possibly sooner.**

## The fork rule (the only question that matters at ship time)

> **"Could two identical runs, played the same way, produce a different score,
> trajectory, or RNG stream across this change?"**
>
> - **YES** -> it forks. It is an Epoch: bump the **ladder**, always. Bump the
>   **minor** too if this is the monthly Theme cut; mid-month, the ladder moves
>   on its own and the version takes a patch bump.
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

## Dated calendar

Epoch = first Friday of the month; Seed = every Friday. Confirm operational
details against `RELEASE_AND_LEAGUE_CYCLE.html`.

### What actually happened (measured from `ladder_version.txt` history)

| Date | Beat | Unit | Ver / Ladder | Forks? |
|---|---|---|---|---|
| Jul 23 | ladder counter created | -- | 0.12.0 / **L1** | n/a |
| Jul 24 | Build **0.13.0** shipped | Epoch | 0.13.0 / **L2** | shipped |
| Jul 25 | **0.13.1** hotpatch (quirks, subtitle, office, READMEs) | Patch | 0.13.1 / L2 | **No** |
| Jul 27 | early-game lease + scouting build | mid-version fork | 0.13.1 / **L3** | **Yes** |
| Aug 7 | **Theme `v0.14` "Per-tick & People"** | Epoch+Seed | 0.14.0 / **L4** | **Yes** |
| Aug 21 | v0.14.2 | mid-version fork | 0.14.2 / **L5** | **Yes** |
| Aug 23 | epoch cut, four bump declarations came due | mid-version fork | 0.14.3 / **L6** | **Yes** |

Read that column, not the one this table used to carry: **six epochs, four minor
versions, and three of the six were mid-version forks.** The old forward rows
said `v0.14 -> L3` and `v0.15 -> L4`; the shipped truth was L4 and, by the time
v0.15 was still three weeks away, L6.

### What is coming (generated -- do not hand-edit this block)

<!-- BEGIN GENERATED: release-horizon -- tools/generate_release_horizon.py -- do not hand-edit -->
**Forward view (tier 1, SCHEDULED -- generated).** Dates are the monthly
train's first Friday; seeds name the ISO week the league opens in. Weekly
seeds for the Fridays in between are in
[`releases/RELEASE_HORIZON.md`](releases/RELEASE_HORIZON.md).

| Version | Ships | Unit | Featured seed at open |
|---|---|---|---|
| **v0.15** | Fri 4 Sep 2026 | Epoch+Seed | `weekly-2026-w36` |
| **v0.16** | Fri 2 Oct 2026 | Epoch+Seed | `weekly-2026-w40` |
| **v0.17** | Fri 6 Nov 2026 | Epoch+Seed | `weekly-2026-w45` |
| **v0.18** | Fri 4 Dec 2026 | Epoch+Seed | `weekly-2026-w49` |
| **v0.19** | Fri 1 Jan 2027 (New Year's Day) | Epoch+Seed | `weekly-2026-w53` |
| **v0.20** | Fri 5 Feb 2027 | Epoch+Seed | `weekly-2027-w05` |

**No ladder column, on purpose (tier 3, NOT FORECASTABLE).** Floor today:
**`>= L6`**, ratcheting. A minor bump always cuts the ladder, and the ladder
may also cut mid-version whenever gameplay forks -- so epochs >= minors and
the next epoch number cannot be read off the next version number. What can
be said, and is what a player needs: **A score set today stays comparable until the next MINOR version at the latest, and possibly sooner.**
<!-- END GENERATED: release-horizon -->

Big Milestones sit outside this table: **"First Contact"** targets end Q3 2026
(spanning v0.13-v0.15) and **"Rivals & News"** end Q4 2026. They complete when
done, not on a first Friday.

## `L<n>` means two unrelated things -- check the namespace

**A bare `L3` is ambiguous in this project and both meanings get spoken in
league week.** In this document and anywhere near a board key, `L<n>` is a
**ladder epoch** (`ladder_version.txt`, the fork counter). In
`docs/GLOSSARY.md` and `docs/design/UPDATER_DESIGN.md` the same notation names
the **L0-L3 distribution update ladder** (L0 raw zip, L1 installer, L2 in-game
update notice, L3 auto-patcher) -- a different axis entirely, with its own L3
that has nothing to do with any leaderboard. Build/art lanes have also been
numbered `L0..L10`. Write "epoch L3" or "update-ladder L3" when the surrounding
sentence does not already settle it.

## Open reconciliation flag (owe Pip)

- **CLOSED.** The `ROADMAP.md` quarterly-pins table was re-cast into the Monthly
  Themes table; the quarterly pins are gone. Theme names for `v0.15`+ are still
  Pip's to name and are marked `(unnamed)` / `(prov.)` there rather than invented.
- **OPEN: v0.19 is scheduled for Friday 1 January 2027** by the first-Friday
  rule -- New Year's Day. Hold it to Fri 8 Jan 2027 (ISO week 01 of 2027, seed
  `weekly-2027-w01`), or accept the date? Note the two are not adjacent week
  numbers: 1 Jan is `weekly-2026-w53`, 8 Jan is `weekly-2027-w01`, because the
  ISO year turns over between them. The generator flags the collision and
  does not move it; only a ruling moves it.
