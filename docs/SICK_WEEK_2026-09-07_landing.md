# Sick week, 2026-09-07 -- the landing document

**Read this first when you are back. Everything else this week feeds into it.**

Pip is ill from 2026-09-07 for several days. He approved autonomous running across
four seats (pdoom1, pdoom1-website, pdoom-data, coordination) with printing held.
This file is the single entry point on return, so that the first hour back is spent
deciding rather than rediscovering.

RULING: 2026-09-07 -- while Pip is ill, autonomous lanes are restricted to work with a machine-checkable success criterion and reversible output; anything requiring his judgement is drafted as a decision card and parked, never guessed -- flavour: autonomy -- mechanism: this file, read on return

**The one sentence to take from this week, if you take nothing else: the thing that
proves a claim is produced locally, and pushing it is a separate act nobody is prompted
to perform.** Two seats held load-bearing artefacts on single disks in the same week --
`fix/identity-truncation`, which is the only fix for a live bug and exists on exactly one
machine (section (d.0)), and the website seat's measurement commit that settled a
disputed claim, which sat local and unpushed. Neither was carelessness. Both are the same
missing mechanism, and it is a prompt rather than a sweep. Section (d.0) is the one with
a possible deadline attached.

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
**Bluesky and all social posting are RED for the week** -- Pip's own explicit call,
relayed via the coordination seat, not an inference drawn by any agent.

## (d.0) The one item where work can still be LOST, not merely delayed

Everything else in this week's batch is reversible. This is not.

`fix/identity-truncation` (`50d918be`) exists on **exactly one disk**: the debian-laptop
checkout at `/home/pip/Repos/pdoom1`. Confirmed two ways -- `SEAT_2026-08-30_pdoom1-branches.md`
opens "Sun 30 August 2026, executed on debian-laptop", and `git cat-file -t 50d918be` in
this checkout returns *"Not a valid object name"*, so the commit is **absent from this
repository's object store**, not merely unbranched. It is not on origin.

Its bug is **still live on today's main**: `godot/scripts/leaderboard.gd:26` still
hardcodes `BOARD_NAME_MAX_BYTES := 40`, and `game_over_screen.gd` still has no
`max_length` on its identity `LineEdit`s.

**NOT MEASURED, and it decides whether this is a decision or a deadline: whether the
debian laptop is the machine leaving around 15 September.** Nobody has established it. Do
not read this as safe because it is written calmly. If that laptop is the one leaving,
someone should push that branch to origin before it goes, and no seat on this machine can
do it -- the object does not exist here to push.

Mitigating: `SEAT_2026-08-30_pdoom1-branches.md` section 4 already carries a worked plan
(cherry-pick in three tiers; the `score_api.php` third must be re-done, not taken). The
risk is purely custodial, not analytical.

### The pattern underneath it

Two seats held load-bearing work on single machines in the same week: this branch, and
the website seat's `a693a666` -- the measurement that settled the quotation-marks
question -- which sat local and unpushed. That is not coincidence. It is what happens when
the artefact that proves a claim is produced locally and pushing is a separate act nobody
is prompted to perform. It wants a mechanism, not a reminder.

## (d.1) The estate-level decision batch lives elsewhere -- read it with this file

`coordination/DECISIONS-NEEDED_2026-09-07.md` is the SINGLE batch across all four
seats, one question per entry, each stating the default already taken and what being
wrong costs. pdoom1's five entries are numbers 6 to 10 there: Manifund, the slipped
v0.15 train, whether #1341 warrants a hotpatch, whether PR #1339 should have been
merged unattended, and the standing instruction not to close #1071.

**The single highest-value five minutes available to a human this week** is in that
batch as entry 10: launch the v0.14.4 macOS zip and find out whether it runs. No agent
can establish it. Staff are expected **Monday 8 and Tuesday 9**, which is the only
human-verification window before Pip is back.

Correction adopted from the website seat, worth carrying because it inverts an
intuition: the site is currently **under**-claiming on macOS, not over-claiming. Its
download button is derived at runtime from the release assets and is therefore honest
by its declared standard ("an asset is attached"), while hardcoded FAQ prose still says
there is no Mac build. The page contradicts itself. Separately, that weak standard is
not the same proposition as #1071's "has ever been verified to run", which is why
entry 10 exists.

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
