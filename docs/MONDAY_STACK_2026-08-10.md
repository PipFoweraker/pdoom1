# Monday stack -- 2026-08-10

**From the `pdoom1` seat, assembled Sunday 2026-08-09 evening**, on Pip's
instruction:

> "I will defer these decisions, summarised, losslessly, until my Monday print
> stack triggers. Insert things into that via the most updated protocols and
> after fully satisfying yourself that the coordination is done working for the
> day and ready to receive and manage the print queue."

Eleven cards. **Each is self-contained** -- context, precise ask, source links --
per the standing decision-card ruling. None assumes you remember the weekend.

---

## Two things about the handover itself, before the cards

### The print protocol: I do not know it, and I said so rather than inventing one

`coordination#50` (opened 09:04Z today, by the `pdoom1-website` seat) asks
`coordination` whether a print stack/queue exists at all, and **had zero comments
when this was written.** The canonical reference,
`PRINT_AND_PROCESS_REFERENCE.md`, is **v2 dated 2026-08-02**, and `#49` reports it
was updated at **18:51 today** -- so the version this seat reasoned from may
already be stale. Its **2026-08-07 carve-out** puts the pdoom trio's printing
with the **G-seat**, meaning this stack is coordination's to emit, not mine.

`pdoom1` holds only `tools/print_doc.py` -- render and print, no queue, no ledger,
no supersession. **So this pack was printed directly, which is the no-mechanism
fallback, not a preference.** Posted as a comment on `coordination#50`
(`#issuecomment-5231059147`) asking for the protocol, with the standing
commitment that `pdoom1` follows whatever that thread says over its own plan.

`pdoom-data` made the same move an hour earlier as `coordination#49`.

### The eleven dated commitments are NOT reprinted here. Deliberately.

They are **already on paper**, as section 2 of
`tools/runsheet/week-2026-08-10-plan.html` (the 8-page week plan on the printer),
as a full table: P1-P11, each with date, who committed it, source citation, and
what would remind you. **Nine of the eleven are marked `NOTHING`.**

Reprinting them would be exactly the waste `coordination#50` measured today --
you re-reading superseded pages -- and exactly what that same plan warns against
in its own "Explicitly NOT suggested" section: *"A new tracking document. P9
fires Friday if nothing acts on the last one. A twelfth artefact this week would
be the finding, not the fix."*

**Where a card below IS one of those eleven, it says so and gives the P-number**,
so the two sheets join up rather than compete.

**The calendar generator: it does not exist.** I was briefed that a lane owns
`scripts/generate_commitment_calendar.py` and to stay out of it. **The file is
absent from the repo.** The only trace anywhere is a permission entry in
`.claude/settings.local.json` -- somebody was authorised to run it and it was
never created. **So nothing has been built to fix the reminder gap.** The week
plan's own S1 argues the fix should not be a file at all: *"The medium matters
far less than that it is not a markdown file: a scheduled agent, eleven phone
alarms, or one sheet on the desk."*

---

# ORDERING

**Cards M1-M3 have a Monday date. M4-M6 unblock another seat. M7-M11 do not.**

---

# M1. IP / trademark to the Australian lawyers -- DUE TODAY

**This is P1 on the week plan. It is the only card with a hard Monday date.**

**Issue:** [`#1061`](https://github.com/PipFoweraker/pdoom1/issues/1061) --
"IP / trademark follow-up -- Australian lawyers, DUE Monday 2026-08-03".
Labelled `priority:high`. Also tracked as `beacon-internal#15`.

## Context you should not have to reconstruct

**The title still says 2026-08-03.** It slipped to 08-10 on 2026-08-06. **The
stated reason for the slip was the funding block, and that reason has now
expired** -- the weekend money arrived. So the thing that justified deferring it
once cannot justify deferring it again.

**You asked to be forced on this one.** The premortem trigger was: *the point at
which the project has money attached is the point at which unregistered
name/mark exposure stops being theoretical.* That trigger has fired.

## The five-point brief, verbatim from the issue

- Trade mark position for **P(Doom)** / **P(Doom)1** -- searchable? registrable?
  already conflicted?
- Which class(es) -- software/games is the obvious one; check whether the
  education/AI-safety framing needs a second
- Relationship between the **Beacon** entity and the game IP -- who owns what,
  and is an assignment needed
- Whether the public launch + live leaderboard changes the position (prior use,
  disclosure timing)
- Cost and timeline for filing

## Facts the lawyers will ask for

- Public site live at **pdoom1.com**; public builds shipping since **v0.11.0**
- First public league night: **Fri 2026-07-31**
- Manifund application live, **deadline 2026-09-09** (`pdoom1-website#194`) --
  funding and IP questions touch each other

## Close condition (the issue's own, not "asked the lawyers")

> **a written position on whether to file, in which classes, and by when.**

## THE ASK

- [ ] Contacted the lawyers today
- [ ] Deferred again -- **new date: ____________** and **the reason, which
      cannot be the funding block: ______________________________________**

---

# M2. Read the Workshop 2 minute -- and its C5 bet scores Sunday 08-16

**This is P2 and P11 on the week plan.**

## What happened while you were out

**Workshop 2 ran and closed without you, by design.** `pdoom-data` chaired.
All four phases ran. **The chair's words: you "were absent throughout and were
not needed once."** Closed **11:35 AEST**; minute due 12:00 from the
`coordination` recorder. Thread:
[`coordination#47`](https://github.com/PipFoweraker/coordination/issues/47).

**The minute had not been verified as published when this was written.** Last
activity on the thread was 06:30Z -- a post-close correction, not the minute.

## The rulings that touch pdoom1 (read the minute for all ten)

- **R2** -- `coordination`'s falsifier was met twice, by two seats, on its own
  stated test.
- **R3** -- the merged taxonomy is **eight classes**: disarmed; unverified
  assertion; mis-aimed referent; wrong property of the right object; knowing
  allowlist; expired premise; composite premise; absent. **Class 5, the knowing
  allowlist, defeats every remedy proposed by any seat** -- a check that prints
  three divergences and exits 0 by design, and has for about eight months.
- **R4** -- **action outranks detection**, with pdoom1's line adopted verbatim,
  supported independently by three seats who had read nothing of each other.
- **R6 -- pdoom1's red-run rule is ADOPTED as the standard all four C5 bets are
  scored against.**

## The C5 bet, verbatim -- pdoom1 set the bar the other three are measured on

> "No guard counts as installed until a RED run of it has been observed and its
> run ID recorded. On 2026-08-16, ask for three run IDs -- one per guard -- each
> showing the guard in its FAILING state. **If fewer than three exist, the bet
> was named and not operated.**"
> -- `docs/workshop-2/position.md:545-552`

**The unflattering part: the three PRs that ARE that bet are all unmerged.**
`#1189` (the `force_alarm` drill for the freshness check, whose alarm had never
once fired), `#1184` and `#1185` (arm the ladder guards, "and prove it can
fail"). **`#1189` is instalment one and it has sat since 08-08.** If they are
still unmerged on 08-16, pdoom1 loses its own bet in another repo's public
ledger, having written the rule everyone else is scored by.

**Nobody owns the 08-16 scoring.** `coordination#47` is closed and no seat
claimed it.

## Two chair asks that need one word each

1. **`pdoom-data`'s `main` push trigger is dead. One empty commit settles it.**
   A chair ruling stands that a seat may not write to `main` unattended, which
   is why it is an ask at all. **Yes / No: ____________**
2. **Class 8 needs an owner** -- one check across all three repos that a `main`
   tip carries a completed run. **Owner: ____________**

## THE ASK

- [ ] Minute read
- [ ] Someone owns the 08-16 C5 scoring: ____________
- [ ] The three bet PRs merged before 08-16 -- **Yes / No**

---

# M3. The next design workshop has no name, no number and no date

**This is P3 on the week plan (week of 08-10), and it is undated inside its own
target window.**

## The naming problem, measured

**W5 and W6 do not exist.** `docs/GLOSSARY.md:414-430` distinguishes two numbers
that get routinely confused:

- **`WS-<n>` / Workshop `<n>`** -- a whole design workshop session. Multi-day,
  produces ADRs. Sub-sessions get letters (`W-3a` Monday, `W-3b` Wednesday).
- **`W<n>` block** -- a **timeboxed agenda block inside one workshop day.**

**`W4` was an agenda block on Wednesday 2026-07-29** -- "next-epoch planning" --
alongside `W0` (review Tuesday's builds), `W1` (colour architecture), `W2`
(decorating math), `W3` (league/content cadence + Friday league prep).
**It was not a workshop.** The glossary lists blocks only up to W4, and there is
no W5 or W6 anywhere in the repo.

So **the next design workshop has no name, no number and no date**, and the
naming collision is the reason it is easy to believe otherwise.

## What is waiting for it -- three things, and they may be one thing

**1. `#984`, your own ruling, 2026-07-27 18:11.** Half-day audit-mechanics
workshop -- "something amazing under the smell". Target window **"week of
2026-08-10, before the 2026-08-31 formal review"**. Scheduled against
ADR-0011's review question: *did optimistic self-reporting + audits earn its
complexity, or does 4-way collapse to 2-way + manager-era audits?*
**Undated inside its window.**

**2. The research/safety unsubtlety.** Your words, `HANDOVER_2026-08-06_EVENING.md:153-157`:

> "I am mostly getting to develop the research safety / capabilities things in a
> bit more detail because this element of the game is a little unsubtle for now."

Ruled: **a workshop, not a lane.** The Research door opens an ALLOCATION PANEL,
not a verb list. Layout can proceed on 8 doors while Research waits.
`#1090` sits on the boundary -- Research Quality is still a global Plan-screen
toggle when your ruling moved it to project level.

**3. The proposal already on the week plan (S3):** fold the research/safety
unsubtlety into `#984` rather than opening a second workshop, because **audits
and research integrity are the same distortion surface from two ends.**
Its falsifier: *if the two need separate ADRs they were separate workshops and
merging them cost a week.*

## THE ASK

- [ ] Day and time booked: ____________
- [ ] One session or two -- **fold / separate**
- [ ] Name and number for it: ____________

---

# M4. Merge `#1190` -- a citation of mine points at a file that is not on main

**This unblocks `pdoom1-website`. It is also a defect on my side and it is the
class of defect the whole weekend was about.**

## What is wrong

[`coordination#48`](https://github.com/PipFoweraker/coordination/issues/48) is a
timing contract `pdoom1` filed **to** `pdoom1-website`, so they can pre-announce
league cutovers. It says:

> Full measured record: `pdoom1` PR #1190,
> `docs/design/LEAGUE_CUTOVER_PLAYBOOK.md`.

**That file exists only in unmerged PR `#1190`.** A reader following the link
today gets nothing. The measured numbers in the issue body are correct and
self-contained; **the citation is not.**

**This is Workshop 2's class 3, mis-aimed referent, committed by the seat that
argued the taxonomy.** Recorded, not apologised for.

## The measured content (so the decision does not need the file)

| Phase | v0.14.0 | v0.14.1 | Predictable? |
|---|---|---|---|
| Tag pushed -> release published on GitHub | **5m 18s** | **5m 28s** | **YES** -- two samples ten seconds apart, includes the full cross-platform build |
| Release published -> pdoom1.com serves it | 1h 10m 58s | **18m 00s** | **No** |
| ...unattended | never observed | never observed | **UNMEASURED** |

**pdoom1 can publish in 5m30s and cannot tell you when pdoom1.com will agree.**
That is the whole reason a pre-announcement schedule cannot be promised yet.

## A second dangling citation, found while checking this one

`tools/runsheet/week-2026-08-10-plan.html:359` cites
`docs/design/WEEK_2026-08-10_PLAN.md` as "full working with every citation".
**That file does not exist either.** Same class, different sheet, and it is on
the page already on your printer.

## THE ASK

- [ ] Merge `#1190` -- **Yes / No**  (fixes the `coordination#48` link)
- [ ] If no: **`coordination#48` needs its citation corrected instead** -- who: ______

---

# M5. Asset provenance -- `pdoom1` is the blocking party, return Thursday 08-13

**This is P4 on the week plan. Another repo is waiting on you and there is no
automated reminder.**

**Issue:**
[`coordination#32`](https://github.com/PipFoweraker/coordination/issues/32) --
"Asset provenance is UNMET, not at-risk: the Manifund obligation has no capture
mechanism in pdoom1 -- blocking party pdoom1, return date 2026-08-13".

## The finding, measured not assumed

The question is whether a published asset carries `origin`
(`generated` / `human` / `photo`), and whether the website is **required** to be
able to say which. It is a **Manifund commitment** -- a truth obligation on the
website created by an art decision.

**Measured in `pdoom1`: provenance is not recorded anywhere. The obligation is
UNMET, not at risk.**

- No `origin` field in `ADR-0019-pull-from-demand-asset-pipeline.md`, which
  defines the three asset states
- No manifest of any kind in `godot/assets/`
- Nothing `pdoom1` emits carries provenance
- What exists is batch-level metadata as **prose** in
  `art_source/pixellab_*/MANIFEST.md`, and **it is stripped before a file reaches
  the pack**
- `pdoom1#900` still lists provenance logging as an open prerequisite

**No amount of website-side work can fix this: the information does not survive
the pipeline.** `pdoom1` has not advanced it since filing.

**Of 27 open coordination issues, exactly two carry a return date: `#32`
(08-13, live) and `#19` (08-05, four days past).**

## THE ASK -- one word, and it sizes everything downstream

- [ ] **Retroactive** (backfill provenance for already-shipped assets) or
      **prospective only** (record it from here forward)? ____________

---

# M6. `pdoom1-website#289` -- awaiting their decision, plus one thing they must not assume

**Nothing is owed by `pdoom1` here.** Flagged so it is not waiting on a seat
that has gone dark.

[`pdoom1-website#289`](https://github.com/PipFoweraker/pdoom1-website/issues/289)
is a proposal from the `pdoom1` seat implementing **their** issue `#285` rather
than redesigning it -- taking their second option verbatim: add
`repository_dispatch` and keep the 6-hourly cron as a **backstop, not the
mechanism**. Not pushed, not merged, `#285` not closed. **Theirs to accept,
amend or reject.**

## The correction they need before deciding

`#1194` measured that **`sync-game-version.yml` has been writing four artefacts
into `pdoom1-website` that nothing reads:**

| written artefact | reader |
|---|---|
| `content/game-versions/v*/release-notes.md` | **none** -- outside `public/`, rsync deploys `public/` only. Written every release since v0.13.0, served to nobody |
| `data/versions/v*.json` | **none** -- zero references anywhere in that repo |
| `data/version-history.json` | **none** -- the write always evaporated. **The file has never existed in that repo** |
| `data/current-game-version.json` | **one, and it was ours** -- reading a repo-root file the site never deploys |
| `repository_dispatch game_version_sync` | **none yet** -- `total_count: 0`. No such run has ever executed there |

**Every step printed `SUCCESS` while the answer was no.** The summary step
literally echoed `SUCCESS Website Repository: Updated with release content` on
every run.

**So they should not assume any of those writes has been arriving.** Also
relevant to `coordination#40`.

## THE ASK

- [ ] Nothing required from you. Chase only if `#289` is still silent by
      Thursday -- **chase / leave**

---

# M7. `gh release edit v0.14.0` -- 14 open issues are publicly announced as delivered

**Merge `#1194` FIRST. The ordering is not cosmetic; see below.**

## What is wrong, right now, in public

The published body of
[`v0.14.0`](https://github.com/PipFoweraker/pdoom1/releases/tag/v0.14.0)
(published 2026-08-07T12:52:51Z) announces **14 open issues as delivered**.
**That page is where pdoom1.com's download button sends people.**

Counted independently rather than inherited, by one batched GraphQL query over
all 68 numbers cited in the section: **68 cited. 54 closed. 14 OPEN.**

Verified, not assumed, that the section IS the published body:
`diff <(sed -n '69,142p' CHANGELOG.md) <(gh release view v0.14.0 --json body)`
reports the first 74 lines byte-identical.

| # | what the section implied | what is actually unfinished |
|---|---|---|
| #802 | music controller shipped | mute/skip and the doom-triggered rotation |
| #957 | own row highlighted on the board | not implemented |
| #1063 | name set on the first screen | prompt appears at upload instead |
| #1111 | ruling delivered | deferred items remain in the ruling |
| #1125 | ruling delivered | deferred items remain in the ruling |
| #793 | office floor fixed | all staff still render as one character |
| #1067 | build stamp fixed | CI still never runs `write_build_stamp.py` |
| #1126 | toggle fixed | un-press behaviour unverified in a shipped build |
| #1068 | Linux download fixed | not confirmed against a shipped build |
| #1072 | preset-derived filename fixed | not confirmed against a shipped build |
| #1117 | dead-path sweep done | sweep unfinished; #1124 is the instrument |
| #798 | action grouping done | #1139 is the checker that measures it |
| #1115 | pdoom-data re-sync retired | capability deleted, not replaced |
| #1093 | art review done | backlog not cleared |

**Nothing was deleted.** Every one of the 14 has a real merged commit in
`v0.13.2..v0.14.0`. Each now discloses in the ruled form and says **what** is
unfinished -- the part a player can act on.

## Why `#1194` must merge first

`#1194` does two things. It carries the corrected body **and** it repairs
`sync-game-version.yml`. **If you run the edit before merging, the release-edit
event re-fires a changelog extraction into `pdoom1-website`** -- into the
dead-end write paths in card M6, which nothing reads and which report SUCCESS
regardless.

## The command -- prepared, verified, NOT run

The corrected body is `docs/release-body-v0.14.0-CORRECTED.md` (on `#1194`'s
branch): the corrected section plus the release workflow's
download/SmartScreen/Build-Information tail, verbatim. It passes
`check_release_notes.py --body ... --tag v0.14.0`, satisfying `#1183`'s own RN004
rule ("every bullet ties to a commit in range").

```
gh release edit v0.14.0 --notes-file docs/release-body-v0.14.0-CORRECTED.md
```

**Not run. Applying it edits outward-facing text under your name, so it stays
yours.**

## One thing `#1183`'s guard does not handle, found by using it

`split_bullets()` treats any line whose stripped form starts with `#` as a new
claim unit -- including a continuation line beginning with a **wrapped
citation**, e.g. `  #1081).`. That orphans a bullet's disclosure from its
citation and reports a FAIL that is not real. **Fail-safe direction only** (it
can never manufacture a false pass). Worked around by reflowing one bullet.
**Not fixed.**

## THE ASK

- [ ] Merge `#1194` -- **Yes / No**
- [ ] Then run the `gh release edit` -- **you / delegate to the seat**
- [ ] The ruled disclosure syntax is prose (`#500 is still OPEN`), not
      `#500 [open]`, because these sections render to players. **Confirm / change**

---

# M8. Eleven open PRs, none draft, all awaiting you

**The week plan already lists these. This card adds what it does not: which need
judgement, which are rubber stamps, and one collision it names but does not
size.**

| PR | What it does | Judgement or stamp |
|---|---|---|
| **`#1166`** | **A share set -- 126 candidates, 6.3% text-leak measured. The entire route from your 262 art verdicts to a public surface.** +33,261/-6,148, 9 files. **Sat since 08-07.** | **JUDGEMENT** -- and it is the natural-traffic lane you asked for |
| `#1164` | Art L2 wave -- 306 images, USD 15.30, already generated | **JUDGEMENT** (spend already incurred; policy expires 08-15) |
| `#1194` | Repairs the 14 public false claims + stops the dead-end writes | **JUDGEMENT** -- see card M7 |
| `#1190` | League cutover playbook | **JUDGEMENT** -- see card M4, unblocks another seat |
| `#1189` | `force_alarm` drill for the freshness check, whose alarm had never once fired | **STAMP** -- and it is C5 bet instalment 1 |
| `#1191` | pdoom1's Workshop 2 Phase 1 sealed position, 1 file, docs only | **STAMP** -- the artefact behind the 08-16 bet |
| `#1176` | Operator name -- see card M9 | **PARKED ON YOUR RULING** |
| `#1192` / `#1186` | **PAIR. Both close `#1181`** ("a timeout is not a test result"). | **PICK ONE** |
| `#1185` / `#1184` | **PAIR. Both close `#1178`** (arm the ladder guard). | **PICK ONE** |

## The pairs, sized -- because "duplicate" undersells it

**`#1192` and `#1186` both rewrite `scripts/run_godot_tests.py`** and both add a
test file for it (`test_run_godot_tests_outcomes.py` vs
`test_run_godot_tests_timeout.py`), and both edit `docs/TOOLS.md`. **They will
conflict on merge.** `#1192` is larger (+774/-92) and also touches `CLAUDE.md`;
`#1186` also touches `docs/TESTING_QUALITY_GATES.md`.

**`#1184` and `#1185` both modify `tools/check_ladder_bump.py` and
`.github/workflows/quality-checks.yml`.** The week plan calls them a duplicate
pair. **I am less sure they are duplicates than it is** -- `#1184` arms
`check_ladder_bump.py` and proves it can fail; `#1185` arms the *board-key*
guard by dropping a `|| true`. Those read as two guards in one file, i.e.
**stacked, not duplicated.** **Worth one look before either is closed as
redundant** -- closing the wrong one silently loses a guard, which is this
estate's defining failure shape.

## THE ASK

- [ ] `#1166` -- **merge / changes / park**  (this is the traffic route)
- [ ] `#1181` pair: keep **`#1192` / `#1186`**
- [ ] `#1178` pair: **duplicates, keep ____ / actually two guards, merge both**
- [ ] Stamps `#1189` + `#1191` -- **merge / hold**

---

# M9. The board cleanup -- and two of the three numbers I was given are wrong

**Nothing here has been run. No Godot process was running when this was
checked.**

## What happened

From `CLAUDE.md:81-102` and `docs/POSTMORTEM_SATURDAY_ITEMS_2026-08-08.md`:

> Tonight the test suite wrote **1,330 files** into Pip's live player profile,
> **destroyed his 2026-07-31 league board** (50 entries -> 0), mutated
> `config.cfg`, `keybinds.cfg` and `theme.cfg`, and injected 23 synthetic rows
> into the live `(weekly-2026-w32, L4)` board during a release playtest.

Cause: **every `godot --headless` run on this machine writes into
`C:/Users/Pip/AppData/Roaming/Godot/app_userdata/P(Doom)/`.** The user-data dir
derives from `config/name` in `project.godot`, **not** from the worktree path,
so all worktrees share ONE profile. **Filed as `#1070` on 2026-07-31 and left
open for seven days before it went off.**

## Measured state, read-only, tonight

| Path | State |
|---|---|
| `...\P(Doom)\leaderboards\` | **1,333 files** |
| `...\leaderboard_weekly-2026-w31__L3.json` | **0 entries** -- the destroyed July league board |
| `...\leaderboard_weekly-2026-w32__L3.json` | empty |
| `...\leaderboard_weekly-2026-w32__L4.json` | **32 entries** |
| `...\*__test.json` | **exactly 1,330** -- matches the documented figure |

## Correction 1: the right backup is the 08-01 one, not the 07-31 one

Two backups exist, both made by `tools/reset_player_state.py`:

| Backup | `weekly-2026-w31__L3.json` |
|---|---|
| `_backup_20260731_160443` | 50 entries, newest row **10:36 that morning** -- taken at 16:04, **before league night** |
| `_backup_20260801_095039` | 50 entries, includes the **18:11 `Notkilleveryone Inc / 47`** run |

**Both hold 50 entries, so a count check cannot tell them apart.** The 07-31
backup predates the league. **Restore from 08-01.**

## Correction 2: `reset_player_state.py --restore` will NOT do this

Its `restore()` takes `backups[-1]` (newest) and **skips any child already
present** -- `SKIP <x> (already present -- not overwriting)`. The current
`leaderboards/` directory exists, so a bare `--restore` **skips it entirely and
silently succeeds.** The tool cannot perform this restore as written.

## Correction 3: "4 genuine rows" on L4 is not sourceable

The local L4 board has **32** entries, not 27. `turns_survived`, `timestamp` and
`final_doom` are **`null` in every row**; the only usable discriminator is
`duration_seconds`. That yields **23 rows between 2.5s and 10.7s** (the
synthetic block, matching the documented 23 exactly) and **9 rows above 30s**,
not 4.

**I did not filter to 4 on a number I cannot source.** The "4" most likely
refers to the **server-side** board at pdoom1.com, not this local file --
and `docs/workshop-2/position.md:577-591` warns explicitly that a board query
returning rows is not evidence any of them is human. **Separately, you have
since confirmed both named players on that board, `GRIM` and `gronklabs`, are
you** -- which is why row counts there are not player counts.

## The commands -- reconstructed, because none are documented anywhere

```powershell
# 0. PRECONDITION -- must return nothing. A running editor, game or headless
#    test shares the one profile and will re-serialise over anything restored.
Get-Process | Where-Object { $_.ProcessName -like "*odot*" -or $_.ProcessName -like "*PDoom*" }

$LB = "C:\Users\Pip\AppData\Roaming\Godot\app_userdata\P(Doom)\leaderboards"
$BK = "C:\Users\Pip\AppData\Roaming\Godot\app_userdata\P(Doom)\_backup_20260801_095039\leaderboards"

# 1. Restore the 50-entry July league board. COPY, not move -- keep the backup intact.
Copy-Item "$BK\leaderboard_weekly-2026-w31__L3.json" "$LB\leaderboard_weekly-2026-w31__L3.json" -Force

# 2. Clear the 1,330 test files. Leaves exactly 3 files.
Get-ChildItem "$LB" -Filter "*__test.json" | Remove-Item -Confirm:$false

# 3. Filter L4 -- NO SAFE CANNED COMMAND. See Correction 3.
```

## THE ASK

- [ ] Steps 1 and 2 -- **run / hold**
- [ ] Step 3: the L4 target is **the local file (9 plausible rows) / the server
      board / neither** ____________
- [ ] Should `reset_player_state.py` gain a `--restore --force` that overwrites?
      **Yes / No**

---

# M10. The copy review pack -- three findings you have not seen

**The pack was printed 08-09, 20 pages, and is on your desk awaiting your pen.**
Path: `G:\Documents\Organising_Life\Code\pdoom1\tools\runsheet\copy-review-2026-08-09.html`.
It quotes every player-facing string; nothing in it was edited, only quoted.
**These three are called out here because they are defects rather than taste
calls, and you have not seen any of them.**

## Finding 1 -- "Global leaderboard: leaderboard ..."

Two files produce one doubled word. **The word "leaderboard" appears twice in
four of the six sync messages.**

- Prefix: `godot/scripts/ui/game_over_screen.gd:632`
  `sync_status_label.text = "Global leaderboard: %s" % message`
- Bodies: `godot/autoload/leaderboard_sync.gd:270-276`, e.g.
  `"leaderboard busy (HTTP 429) -- score saved locally, will retry next launch"`

**What a player reads:**
`Global leaderboard: leaderboard busy (HTTP 429) -- score saved locally, will retry next launch`

## Finding 2 -- Operator vs "player name", same person, two words

The one-time claim-a-name dialog labels the field **`Operator:`** (the `#957`
nomenclature ruling). The upload-consent dialog at game over says:

```
This shares publicly, for this and future runs:
  player name: [name]
  lab name:    [lab]
  your score
```

**Same field, same person, two different words, two dialogs a player sees
minutes apart.** This is the same inconsistency `#1176` exists to fix -- see
card M11.

## Finding 3 -- `CREDITS.md` ships "(adjust name form as preferred)" to players

`CREDITS.md:18`:

```
- **Design, direction, and development:** Pip Foweraker  *(adjust name form as preferred)*
```

**The credits generator drops any entry carrying `[Pip to fill]` or
`[Pip to confirm]`.** This parenthetical is **not** one of those markers, so it
is not dropped -- **it ships.** An unanswered question addressed to you is
currently rendering on a public credits screen, under your name, alongside the
named artists.

## THE ASK

- [ ] Name form: ____________________  (then delete the parenthetical)
- [ ] Fix findings 1 and 2 -- **now / with `#1176` / park**
- [ ] Should the generator's placeholder-drop also catch bare parentheticals?
      **Yes / No**

---

# M11. `#1176` -- operator names for 0.14.2, parked on your both-names ruling

**Parked deliberately. It is not stalled; it is waiting on you.**

**PR:** [`#1176`](https://github.com/PipFoweraker/pdoom1/pull/1176) --
"the Operator name was collected and never carried anywhere -- two identity
fields, and a truncation that stops amputating". 22 files, +1,249/-42, open
since **2026-08-07**.

## Context

The Operator name **was collected from the player and then went nowhere.** The
PR introduces **two identity fields** rather than one -- which is your both-names
ruling made concrete -- and fixes a truncation that was amputating names rather
than eliding them.

**This is the same surface as card M10's finding 2**: the copy says "Operator"
in one dialog and "player name" in the next, because there genuinely are two
concepts and the UI had one word. **Deciding `#1176` decides the copy.**

**It is 22 files across the identity path, so it is not a rubber stamp**, and it
targets 0.14.2 rather than a patch.

## THE ASK

- [ ] Both names carried, per your ruling -- **confirm / amend**
- [ ] Ship in **0.14.2 / later**
- [ ] The player-facing word is **Operator / player name / both, in defined
      places**: ____________

---

# M12. The art payload is unruled, and it has grown three times

**Not on the week plan. No date. Nobody is chasing it.**

From `docs/HANDOVER_2026-08-06_EVENING.md:178-180`, under "Still unruled":

> **Art promotion is at 200.4 MB**, from the 58 MB Pip agreed to. It has grown
> three times, **each time because a fix revealed cost a bug was hiding.**
> Worth re-ruling rather than assuming the old answer holds.

Repeated as open question 3 in `docs/POSTMORTEM_2026-08-07_CAPTURE.md:776-778`.

## The numbers, with their own caveat attached

From `docs/design/ASSET_PAYLOAD_ANALYSIS_2026-08-06.md`:

- `promotable payload: 1,206 files, 200.4 MB`
- `200.4 MB -> 46.5 MB at 1x display size, 71.2 MB at 2x. Saves 129 to 154 MB`

**Contested by `docs/CLAIM_AUDIT_2026-08-06.md:282-286`** (entry U7): the set and
its 200.4 MB figure come from a **gitignored store**, so the number is not
independently checkable from the repo. **Reported because it is unflattering to
the claim, not despite it.**

**Why it matters beyond disk:** Godot packs the **entire** `godot/` tree into the
`.pck`, referenced or not. A payload ruling is a download-size ruling.

## Adjacent and expiring

**Your generation spend policy -- "$100 AUD/day unconstrained until
2026-08-15" -- expires Saturday** (P10 on the week plan). `coordination#33` has
USD 44 headroom; `#1164` is already generated and unmerged. **The policy does not
alarm when it expires; it just stops being true, silently.**

## THE ASK

- [ ] Re-rule the payload ceiling: **58 MB stands / new figure: ______ MB /
      downscale to 1x (46.5 MB) / downscale to 2x (71.2 MB)**
- [ ] Spend policy after 08-15: **lapse / extend to ______ / new daily cap ______**

---

# M13. "The rewrite thing" -- your words, carried verbatim and not interpreted

**Recorded exactly as said, because it is a half-formed thought and paraphrasing
it would lose it.**

> **"The rewrite thing falls into a pattern of rules that I think is now just
> mere hours away from me adopting, so I will defer these decisions."**
>
> -- Pip, 2026-08-09, quoted by the `pdoom-data` seat in
> [`coordination#49`](https://github.com/PipFoweraker/coordination/issues/49)

**No interpretation is offered and none should be inferred from the placement of
this card.**

## The concrete instance it was said about, so the rule has something to be sized against

**It belongs to the `pdoom-data` seat, not `pdoom1`.** `pdoom-data#72` redacts
email addresses of named academics at HEAD. **The addresses remain in git
history, in every existing clone, and in every fork.** Removing them requires a
history rewrite -- disruptive and irreversible.

**Scope, so the rule can be sized against a real number: 405 unique addresses
across 13 files**, one of them a 196 MB untracked local dump. Published history
is the tracked subset only.

`pdoom-data`'s own framing, which this seat endorses and repeats rather than
restates:

> **Do not treat this as an open question needing an answer Monday.** Pip has
> deferred it deliberately because he judges it an instance of a general rule he
> is close to adopting, and deciding it case-by-case first would pre-empt the
> rule. **The ask on Monday is whether the rule has landed, not what to do about
> these addresses.**

## THE ASK

- [ ] Has the rule landed? **Yes -- state it: ______________________________ /
      No, still forming**
- [ ] If yes, does it settle `pdoom-data#72`'s history rewrite? **Yes / No /
      needs its own pass**

---

## What is NOT in this pack, and where it is instead

Cut deliberately rather than dropped, because a stack you will not finish is not
lossless in the way that matters.

| Cut | Where it is |
|---|---|
| **The eleven dated commitments, in full** | Section 2, `tools/runsheet/week-2026-08-10-plan.html` -- on the printer, as a table with sources and reminder status |
| **The three ranked suggestions (S1-S3)** | Section 5 of the same plan |
| **Every player-facing string** | `tools/runsheet/copy-review-2026-08-09.html`, 20 pages, on your desk |
| **Workshop 2's full ruling ledger R1-R10** | `coordination#47`, and the recorder's minute |
| **The full 8-class taxonomy with evidence** | The Workshop 2 minute |
| **PR-by-PR diffs** | GitHub |

**Nothing above was summarised away.** Each lives in a document that is already
printed or already published, and each card that touches one names it.

-- `pdoom1` seat, 2026-08-09.
