# Sick week, 2026-09-07 -- the landing document

**Read this first when you are back. Everything else this week feeds into it.**

Pip is ill from 2026-09-07 for several days. He approved autonomous running across
four seats (pdoom1, pdoom1-website, pdoom-data, coordination) with printing held.
This file is the single entry point on return, so that the first hour back is spent
deciding rather than rediscovering.

RULING: 2026-09-07 -- while Pip is ill, autonomous lanes are restricted to work with a machine-checkable success criterion and reversible output; anything requiring his judgement is drafted as a decision card and parked, never guessed -- flavour: autonomy -- mechanism: this file, read on return

---

## (a) Decisions he made on the way out, and what actually happened

| Decision | Status |
|---|---|
| Commit the certes strategy documents | **DONE.** Ten documents, 1,117 insertions, pushed to `origin/main` at certes (`3e86cbe`, `0e7037a`). |
| Push coordination's unpushed commits | **NOT NEEDED -- my error, see below.** Coordination was pulled up to `eb4b280` instead. |
| Hold printing | **HELD.** Nothing will be flushed unattended. Reasoning in section (d). |
| Defer Manifund | **DEFERRED.** Consequence stated in section (b). This is the item most likely to be regretted. |

### The correction

I told Pip twice that coordination held **13 unpushed commits at risk**. That was
backwards. `git rev-list --left-right --count origin/main...HEAD` returned `13 0`,
which means 13 commits in `origin/main` that are **not** local -- i.e. 13 **behind**,
zero ahead. Nothing was ever at risk there.

The 2026-08-25 estate triage had already recorded this correctly
(`coordination | REAL WORK at risk: none`) and I read past it. Cost: one wasted
decision from a man about to be ill. Filed here because the generator that produces
these errors is the one this repo already measured -- asserting from a reconstruction
when a cheap check existed.

### The preservation item is closed

The 2026-08-25 triage ranked `certes/docs/strategy/` as **rank 1 of 23 repos**: nine
authored documents, 62,660 bytes, present in no commit on `origin/main`. A tenth
(`utas-hdr-approach.md`) had been written since the triage ran. All ten are now
committed and pushed. `migration-pathways.md` self-describes as the only surviving
copy of its reasoning, so this was the one genuinely irreversible item outstanding.

Scanned for credentials before staging (`sk-`, `ghp_`, `AKIA`, `xox*-`, PRIVATE KEY):
zero matches. Both repos confirmed PRIVATE before anything was pushed.

---

## (b) The thing to look at first, before anything else

**Manifund closed 2026-09-09 and was deferred.**

- The commitment is `docs/calendar/COMMITMENTS_INDEX.md:56`, owner pip.
- PR **#1291** ("budget: his four answers applied, the assumption named, and the
  number they still do not license") is still `CONFLICTING`, unchanged since
  2026-08-24.
- **Deferring means it lapses.** No agent could land it honestly, because the open
  question in its own title is a judgement about what the evidence licenses, not a
  merge conflict.

If there is a late path, a rollover, or a next round, that is the first thing worth
checking on return. NOT VERIFIED: whether Manifund has a later window; nobody checked.

---

## (c) What ran unattended, and where its output landed

Only **one** lane was permitted to commit. Concurrent commits into one checkout is
the pre-commit rollback trap that discards working-tree edits, so every other lane
is report-only. Each committing lane works in its own worktree.

| Lane | Kind | Output |
|---|---|---|
| ASCII breach sweep (#1331) | commits, one PR | see the PR; before/after breach counts stated with the commands that produced them |
| Backlog triage over 213 open issues | report only | `docs/TRIAGE_2026-09-07_backlog.md` |
| Branch and worktree debt census | report only | `docs/BRANCH_DEBT_2026-09-07.md` |

The triage report ends with a **NEEDS A PIP RULING** section, written so the decisions
can be answered in one sitting rather than one at a time. Start there.

The branch census deliberately biases toward CANNOT DETERMINE over SAFE TO DELETE,
because being wrong in the safe-to-delete column is the only failure mode in that job
that actually destroys work.

---

## (d) What is deliberately NOT happening, and why

**Printing is staged, never flushed.** `coordination/FUSE_2026-08-24_print-queue-under-concurrency.md`
opens: *"Three seats wrote into one print queue today and it produced four distinct
failures, none of which raised an error."* Its failure 2 is precisely this week's
configuration: *"a scheduled or unattended flush of an edited item SKIPS rather than
prints, and nothing chases it."* Measured that day: thirteen stacks, 127 pages, four
of them starved flushes, and *"nothing currently reports that number, so it is
invisible unless a human happens to count."*

Combined with the known local trap (`-Verb Print` silently prints nothing; use
`AcroRd32 /n /t` and check the queue) and coordination #82 (walkpack emitting HTML
named `.pdf`; five of six jobs reported as printed had not printed), a week of
unattended printing can report complete and produce no paper. The coordination seat
has been asked to build the missing instrument instead -- report page-count versus
queue-length, so a starved flush becomes loud rather than silent.

**RED list, not touched unattended by any seat:** releases and tags; anything writing
to the real player profile or the live leaderboard; merges of player-facing behaviour;
print flushes; anything outward-facing (emails, posts, third-party comments, spending).

---

## (e) Standing state you will want, measured 2026-09-07

- `main` at `82fa10a1`, 2026-08-30. Version **0.14.4**, ladder epoch **L6**.
- Latest RELEASE is v0.14.4, tagged 2026-08-28. **The v0.15 train was due 2026-09-04
  and slipped.** No new date has been set; that is a decision, not an oversight to fix.
- **#1341 -- the pause menu that did not pause -- is fixed on `main` but is in no
  release.** The current public download still has it. Pip found that one on the
  shipped build himself.
- PR **#1339** is green on all 13 checks and MERGEABLE, idle since 2026-08-30. It stops
  1,194 invented "safety researcher" quotes shipping as player-facing flavour text.
  Cheapest available win.
- 213 open issues. No `ship:tonight` or `ship:hotpatch-48h`. The `ship:next-release`
  label holds items open since July, so treat those labels as evidence, not truth.
- Onboarding, if anyone asks whether the game is ready for an audience: there is **no
  tutorial in the build**. `grep -rln tutorial godot/scripts/` matches one file, and it
  is `bug_reporter.gd`. #722 and #721 have been open and untouched since 2026-07-22.

---

## (f) The failure mode this week was designed around

The risk of running agents for days is not wasted tokens. It is **volume that needs
review, where the reviewer is the person who was ill.** That converts a rest week into
a review-debt week.

So every lane was given the same evidence standard: this repo audited itself and found
**6 of 68 headline claims wrong (8.8%)**, every one asserted from a summary rather than
a source, two already merged, one already propagated to two other repos
(`docs/CLAIM_AUDIT_2026-08-06.md`). Unreviewed, that rate compounds. Lanes were told
that a claim in a heading or a bolded sentence must reduce to a command someone else can
run, and to write NOT MEASURED rather than a plausible number.

Judge the week's output by that standard first. A short report with checked claims is
worth more than a complete one with confident ones.
