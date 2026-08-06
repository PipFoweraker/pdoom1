# Claim audit -- pdoom1's own output, 2026-08-06

**What this is.** In `coordination#31` Phase 3, at 10:55Z today, the pdoom1 seat
adopted a rule about its own writing:

> A claim in a title, a summary line, a table cell or a bolded sentence must be
> reducible to a command another party can run. If it is not, it moves into the
> body with its hedge attached, or it does not ship.

The rule was adopted because the seat had just been caught by it: `pdoom1-website`
wrote 2,197, pdoom1 repeated 2,197 back in its own chair note without checking, and
the correct figure was 2,194. A rule adopted in response to being caught, and then
never applied backwards, is a rule that cost nothing.

This document applies it retroactively to everything the seat published today.

**Method.** Extract every quantitative or factual claim occupying a HEADLINE
POSITION -- a title, a bolded sentence, a summary line, a table cell, a section
heading. Not body prose. For each, determine whether it reduces to a command; run
the command; record it and its output. Where no command exists, say what would have
to exist.

**Bases.** Verification ran against `origin/main` at `9358c120` in a clean worktree
at `.claude/worktrees/claim-audit`, plus `78be0370` (the base the workshop comments
declare) via `git show`, plus the live art store and `pdoom1-website` working copies
in Pip's checkout, which are not in git here.

**Scope actually found, versus the scope commissioned.** Three documents named in
the brief do not exist where the brief places them. `docs/ISSUE_TRIAGE_2026-08-06.md`
is in unmerged PR `#1144`; `docs/design/ASSET_PAYLOAD_ANALYSIS_2026-08-06.md` is
untracked in Pip's working copy only; `docs/design/WORKSHOP_TRI_REPO_PREP_2026-08-06.md`
is in unmerged PR `#1156`. `docs/ACTION_TAXONOMY.md` is at `docs/`, not
`docs/design/`. Recorded because a claim audit that silently accepts a wrong file
list is the same defect it is auditing.

---

## Counts

| Verdict | Rows |
|---|---|
| CONFIRMED -- command run, output matches | **49** |
| WRONG -- command run, output does not match | **6** |
| UNCHECKABLE -- no command exists | **7** |
| STALE -- true when written, not now | **6** |
| **Total headline claims examined** | **68** |

The known-wrong instance (2,197) is row W1 and the method rediscovered it
independently -- see "Did the method rediscover 2,197?" below.

---

## WRONG (6)

### W1. "2,197 pages" -- the known instance, rediscovered and sharpened

**Where:** `coordination#30`, pdoom1's chair/evidence comment (09:53:20Z), OWES
section: *"the website badges, facets and sorts on it across 2,197 pages and cannot
vote."* And `coordination#31`, pdoom1's Phase 1 (09:53:18Z), chair's note: *"a
public surface with five petition buttons on 2,197 pages."* Both bolded-context
summary lines.

**Command** (run in `G:\Documents\Organising_Life\Code\pdoom1-website`, branch
`fix/suggest-link-routing`):

```
ls public/events | wc -l                                  -> 2197
grep -rl "issues/new?labels=metadata" public/events/ | wc -l -> 2194
grep -rl "rarity" public/events/ | wc -l                    -> 2196
```

**Verdict: WRONG, under either reading.** The petition-button reading is 2,194 --
the figure `pdoom1-website` published as its own correction at 10:07Z. The
rarity-badge reading, which is what pdoom1's `#30` sentence actually asserts
("badges, facets and sorts on it"), is **2,196**, and nobody has stated that figure
anywhere. 2,197 is the raw file count of the directory and is the one number that
describes neither claim.

**Who is holding a wrong number.** `coordination` (both comments are on
coordination issues, and the recorder minutes from them); `pdoom1-website` (whose
own correction fixes only the 2,194 reading and leaves 2,196 unstated); and open PR
`#1156`, whose body carries `2,197 pages` forward into the pdoom1 repo.

**Aggravating detail.** `pdoom1-website` is cloned at
`G:\Documents\Organising_Life\Code\pdoom1-website` on the same machine. The command
above took under a second. The claim was not unavailable to the seat; it was
unrun.

### W2. PR #1155 (MERGED): the panel-box table cell

**Where:** merged PR body, the type-scale table, bolded final row:

| **Panel box** | **640 x 600** | **800 x 740** | **+25% w, +23% h** |

**Command:**

```
git show 9358c120 -- godot/scenes/pause_menu.tscn | grep offset_
  -offset_top = -300.0   +offset_top = -396.0
  -offset_bottom = 300.0 +offset_bottom = 396.0
  -offset_left = -320.0  +offset_left = -400.0
  -offset_right = 320.0  +offset_right = 400.0
```

**Verdict: WRONG.** 600 -> **792**, not 740. Height grew **+32%**, not +23%. Width
(640 -> 800, +25%) is correct.

The correction exists, in the PR's own merged test file, as a REBASE NOTE:
`godot/tests/unit/test_music_player_controls.gd:352` -- *"#1120 landed a sixth
button in this panel ... so the contents grew 707 -> 769 and the authored box 740
-> 792."* The hedge stayed in a code comment. The table travelled.

**Who is holding a wrong number:** anyone reading the merged `#1155` body -- which
is the artifact Pip reviews and the changelog derives from.

### W3. PR #1155 (MERGED): the seven-row resolution table

**Where:** merged PR body, *"Resolutions -- measured, not assumed"*, seven rows each
asserting `panel rect (560,170) 800x740` or `(560,230)` / `(560,350)`.

**Command:** as W2. Authored box is 800x792, so a centred panel in a 1920x1080
viewport sits at `(560,144)`, not `(560,170)`.

**Verdict: WRONG -- all seven rows.** The `fits: yes` column is almost certainly
still true (792 < 1080, and the PR's `aspect="expand"` argument is sound and
independent of the height). The measured cells are not.

This is the sharpest illustration of the rule's own target: a table of
seven measurements, every one reducible to a command, none re-run after the rebase
that invalidated them.

### W4. PR #1155 (MERGED): the central bolded argument

**Where:** *"**A flat +30% (780px) with these contents leaves 73px of empty panel
under the Quit button**"* -- and the framing sentence *"The panel is +23% tall, not
+30%, and that difference is the whole point."*

**Command:** as W2. Shipped height **792**.

**Verdict: WRONG.** The shipped panel is 12px **taller** than the flat +30% the PR
explicitly rejects. The argument is recoverable -- the contents also grew to 769, so
the slack is 23px, inside the PR's own 40px budget, and the merged guard passes for
that reason -- but the recovery appears nowhere in the body. As written, the PR
argues against a number it then exceeded.

### W5. `coordination#31` Phase 3: a citation declared re-measured that was not

**Where:** Phase 3 (10:55:41Z), A1 bit 3, discharging `pdoom-data`'s block: *"It is
nine lines, `godot/autoload/event_service.gd:404-410`"*, closing with the italic
summary line *"Every number in this comment was measured against that tree
[`9358c120`] for this comment, not carried forward from Phase 1."*

**Command:**

```
git show 78be0370:godot/autoload/event_service.gd | grep -n "func _is_flavour_event"  -> 404
git show 9358c120:godot/autoload/event_service.gd | grep -n "func _is_flavour_event"  -> 406
```

**Verdict: WRONG.** `404-410` is the Phase 1 base. At `9358c120` it is **406-412**;
`#1137` shifted the file by two lines. The number was carried forward, and the
closing sentence asserting otherwise is the false claim.

**Who is holding a wrong number:** `pdoom-data`, which was handed those line numbers
as the unblocking artefact for its `salience_tier` correlation work.

### W6. `coordination#31` Phase 3: a published command that cannot fail

**Where:** Phase 3, B2: *"Measured on `main` just now:
`grep -ci 'snapshot|corpus_sha|generated_at|record_count'` against that file returns
**0**."*

**Command, and its control:**

```
grep -ci 'snapshot|corpus_sha|generated_at|record_count' \
  godot/data/events/overrides/promotion_pass_2026_08.json   -> 0
printf 'snapshot\ncorpus_sha\n' > /tmp/ctl.txt
grep -ci 'snapshot|corpus_sha|generated_at|record_count' /tmp/ctl.txt  -> 0   <-- control
grep -ciE 'snapshot|corpus_sha|generated_at|record_count' /tmp/ctl.txt -> 2
```

**Verdict: WRONG as a measurement.** Basic `grep` treats `|` as a literal, so the
published command searches for one 44-character literal string and returns 0 against
a file that contains all four words. It cannot fail. The underlying claim happens to
be TRUE -- `grep -ciE` also returns 0 against the pass file -- but the seat did not
establish it, and reported that it had.

This is `#640`'s shape (a check that reports success while testing nothing),
committed inside the comment that adopts a rule about commands. It also violates
`coordination#10`, whose whole subject is shell metacharacters eating meaning.

---

## UNCHECKABLE (7)

### U1. "52 of 2,247 game images are hero-shaped"

**Where:** `coordination#31` Phase 1 (A2 bit 4 failure mode, bolded) and Phase 3
(*"The measurement that decides it, still unmade: `#249` found only **52 of
2,247**"*), and PR `#1156`. Attributed to `pdoom1-website#249`, but it is a fact
about **pdoom1's own assets**.

**Nothing in pdoom1 counts 2,247:**

```
find godot/assets -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.webp' -o -iname '*.svg' \) | wc -l  -> 502
find art_generated -type f -iname '*.png' -o -iname '*.jpg' -o -iname '*.webp' | wc -l                          -> 5048
git ls-files art_source | grep -icE '\.(png|jpg|jpeg|webp)$'                                                    -> 4466
python -c "...review_state.json non-discard verdicts..."                                                        -> 2244
```

**What would have to exist:** a definition of "game image" (packed? Library?
reviewed?) and of "hero-shaped" (aspect ratio threshold? minimum long edge?), plus
the script that produced 52. None is published.

**Note, stated as an observation and not a conclusion:** the nearest measured figure,
2,244 non-discard verdicts, sits 3 below 2,247 -- numerically the same shape as 2,194
sitting 3 below 2,197. That may be coincidence. It is exactly the kind of coincidence
this seat should not resolve by pattern-matching, and it is the sister seat's number
to check.

**This is the same species as W1**, repeated twice in bolded sentences, in the same
comment that adopts the rule, ~50 lines above it.

### U2. "`rarity` correlates `r = -0.0065`"

**Where:** `coordination#30` OWES section (bolded), Phase 1 A1 bit 1, Phase 3 A1
bit 3. **Against what?** No second variable is named anywhere -- "with anything
pdoom1 uses it for", "against anything visible". A correlation coefficient with one
named variable is not reducible to any command.

**What would have to exist:** the two vectors and the script. Four significant
figures on an unnamed pairing is precisely the kind of precision that buys
credibility it has not earned.

### U3. PR #1145 (MERGED): "10 phase-critical state variables / 34 mutation sites"

**Where:** the merged PR body's headline table, both bolded. These are enumerations,
not derivations -- the only way to check them is to hand-recount the audit document
that produced them. `grep` over the one variable I could isolate finds 9 mutation
sites for `pending_events`, which neither confirms nor contradicts a 34 spanning ten
variables.

**What would have to exist:** the scanner already shipped in that PR
(`test_phase_critical_state_guard.gd`) emitting its counts, or a generator in
`scripts/`. This is the repo's own generated-index pattern, not applied to its own
audit.

### U4. PR #1154 (OPEN): the slot-picker measurement table

**Where:** the PR body's "Measured, on the live store" table -- 1,206 promotable
assets / 200.4 MB, 600 pool-exempt files, 15 frame roles / 41 files / 10.4 MB, 136
contested clusters / 398 files / 116.7 MB.

`tools/art_review/slot_model.py` is on the unmerged branch and `art_generated/` is
gitignored, so no third party -- including a reviewer in a fresh worktree, including
CI -- can run any of it. The PR's own tests say so: they *"skip where the gitignored
art library is absent."* Only `2,713 verdicts` is checkable from the tracked tree
(and is CONFIRMED, row C45).

**Not a defect in the PR** -- the store genuinely is gitignored by policy. It is a
statement that these numbers are one machine's word, and the PR body does not say so.

### U5. `coordination#28`: "75 per cent of their feedback"

**Where:** section 5, quoted back approvingly by the coordination seat and now
carried into a Manifund draft. Two playtesters, one hour, no recording, no
transcript, no instrument named. There is no command.

**What would have to exist:** the feedback log. It is the single most-travelled
sentence pdoom1 published this week and it is the least checkable thing in this
audit.

### U6. PR #1153 (MERGED): "the game ships 1,194 records naming real people and organisations"

1,194 is the total corpus size (CONFIRMED, row C1). It is not a count of records
naming real people; no command distinguishes them, and the sentence asserts a
property of all 1,194. The load-bearing point (the guardrail is untracked) is
CONFIRMED separately at row C28.

### U7. ASSET_PAYLOAD_ANALYSIS: "200.4 MB -> 46.5 MB at 1x display size"

The document's headline saving. `du` on the live store confirms the baseline halves
that are tracked (`godot/assets` = 47 MB, row C49), but the 1,206-file promotable
set and its 200.4 MB come from the same gitignored store as U4, and the resizing
model is not published as a runnable script.

---

## STALE (6)

| # | Claim | Where | Measured now |
|---|---|---|---|
| S1 | "201 open issues" | `#28` title + body; PR `#1144` table total | **206**. `gh issue list --state open --limit 400 --json number -q 'length'`. `#1153` itself filed six (`#1147`-`#1152`), all OPEN and confirmed to exist |
| S2 | "baseline `origin/main` @ `78be0370` = **1146 tests / 112 files**" | PR bodies `#1137` `#1139` `#1143` `#1144` `#1145` `#1146` | main at `9358c120` = **1205 tests / 118 files, 0 failures** (`python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300`) |
| S3 | "1089 tests / 104 files before, 1113 / 106 after" | PR `#1120` merged body, bolded | A branch point older than `78be0370`. `docs/SEAT_VOICE.md` names *"a '1089 green' report made from local runs while main sat red in CI"* as one of the week's defects; the figure is still the verification baseline in a merged PR body |
| S4 | Line citations `event_service.gd:335-342`, `:366`, `:378`, `:404-410` | PR `#1156` (OPEN) and `WORKSHOP_TRI_REPO_PREP_2026-08-06.md` | Exact at `78be0370` (verified). Off by +2 on today's main. They go stale for every reader the moment `#1156` merges |
| S5 | "`#1137` is **OPEN, not merged**" | Phase 1 (09:53Z), bolded, load-bearing for B2 | Merged 09:53:46Z, within a minute of the comment. Phase 3 corrects it unprompted and reports that it cuts against the seat -- **credit where due; this is the process working** |
| S6 | "~50 closeable with no code" | `#28` title and body | Arithmetic still internally sound (8+15+19+8 = 50, row C31). Zero have been closed; the set drifts daily and nothing regenerates it |

**Note on S2.** The individual deltas are honest and I can prove it: 1146 + 24
(`#1120`) + 6 (`#1137`) + 0 (`#1139`) + 4 (`#1143`) + 7 (`#1145`) + 17 (`#1146`) +
1 (`#1155`) = **1205**, and 112 + 2 + 1 + 1 + 1 + 1 = **118**. Both land exactly on
the measured post-merge tree. Seven lanes measuring independently from a shared base
summed correctly. What none of them measured is the tree that shipped.

---

## CONFIRMED (41)

Commands were run in the audit worktree unless noted. Grouped by source.

### The event-corpus numbers (`coordination#30` evidence, `#31` Phase 1, PR `#1156`)

One `python` pass over `godot/data/historical_events.json` reproduces all of these:

| # | Claim | Output |
|---|---|---|
| C1 | 1,194 records | 1194 |
| C2 | `rare` 1,076 / `common` 77 / `legendary` 41 | exact |
| C3 | 48 `rare` records dated 2016 | 48 |
| C4 | 1,028 `rare` reach the pool | 1028 |
| C5 | 1,073 = `rare` AND flavour-gated ("nearest measured figure to 1,072") | 1073 |
| C6 | 1,025 of 1,028 demoted to the feed tier | 1025 |
| C7 | Exactly three survive the flavour gate as `rare` | `ftx_future_fund_collapse_2022`, `openai_board_crisis_2023`, `international_coordination_breakdown_2025` -- named correctly |
| C8 | 53 in-pool records dated 2017 | 53 |
| C9 | Delta table: no change **975**, +9 turns later **101**, earlier **0** | 1076-101 = 975; 48+53 = 101; and the direction follows from `rare_spread == window/2` |
| C10 | Identical under `(52,13,26)` and `(12,3,6)` | Both collapse the rare expression to `base_turn`; `common` floors at 10; only years with `base_turn < 10` move, in both |
| C11 | 1,174 of 1,194 feed-demoted; decision surface of 20 | 1174 / 20 |
| C12 | `pdoom_impact` null in 1,187 of 1,194 | 1187 |
| C13 | `sources` present on all 1,194 | 1194 |
| C14 | `impacts[].condition` -- 3,636 entries, all null | 3636 / 3636 |

The reproduction command is in `docs/design/WORKSHOP_TRI_REPO_PREP_2026-08-06.md`'s
appendix (PR `#1156`) -- **which is why these rows are checkable at all.** That
appendix is the rule working before it was written down.

### Code and config citations

| # | Claim | Command / output |
|---|---|---|
| C15 | `rarity_curves.json` leaves `common.min_turn: 10`, `common.base_probability: 0.12`, `rare.min_turn: 20`, `rare.base_probability: 0.06` untouched | all four present with those values |
| C16 | The dial ships `month_per_turn` 12/6/3/6 and `week_per_turn` 52/26/13/26 | exact |
| C17 | `promotion_pass_2026_08.json` is 214 lines | `wc -l` -> 214 |
| C18 | 24 override entries | 28 top-level keys, 4 `_`-prefixed metadata -> 24 |
| C19 | No corpus sha / record count / generated-at anywhere in the pass | `grep -ciE` -> 0 (the claim is true; the **published** command is not -- see W6) |
| C20 | `events.gd:111-113` is the start-year filter; `:185` is `rng.randf()` | exact on both `78be0370` and `9358c120` |
| C21 | `event_service.gd:335-342` / `:366` / `:378` / `:404-410` / `:446` | exact **at `78be0370`**, the base Phase 1 declares (see S4, W5) |
| C22 | Zero `tr()` calls in `godot/scripts/`, no `locale/`, no `.translation`/`.po`, no `internationalization` block | 0 / none / none / 0 |
| C23 | `docs/copy/README.md` header is `**Status:** ACTIVE POLICY (2026-07-25)` | exact string |
| C24 | Six pull targets; the player guide is not among them | six bullets, "These six are the seam"; `player_guide` absent |
| C25 | The push clause is on **line 6** of `ROLE_CREATIVE_DIRECTOR.md`, under `PROPOSED PERMANENT HOME`, in a file headed `Status: DRAFT for Pip review, 2026-07-26. Not committed anywhere yet.` | line 6 exactly; header exact |
| C26 | `variable_mapping.json` maps `vibey_doom` / `stress` / `burnout_risk` onto a literal `doom` | all three -> `"doom"` |
| C27 | `palette.json` carries no version, no generated-at, no source | bare 24-element array of `hex`/`rgb`/`role_guess`/`weight_pct` |
| C28 | The real-people guardrail (`#1150`) appears nowhere in `docs/` | `grep -rlni "never imply wrongdoing" docs/` -> only `ISSUE_MINING_2026-08-06.md` itself |
| C29 | `#1152`: `ROADMAP.md:47` and `RELEASE_NOMENCLATURE.md:89` both map `v0.14 -> L3` | both lines exact, both carry L3 |
| C30 | `#802`: no skip, no next, no mute anywhere in `godot/scripts` or `godot/scenes` | empty, **on today's main, after `#1146` merged a track picker** |
| C31 | `#1153`'s buckets sum: 32 + 7 + 11 = 50; and 8 + 15 + 19 + 8 = 50 | both |
| C32 | `#1144`'s triage sums: 8+15+19+8+8+27+116 = 201 | 201 |

### `UI_ARCHITECTURE` -- the `#1153` correction (a headline claim of absence)

| # | Claim | Output |
|---|---|---|
| C33 | `UI_ARCHITECTURE_2026-08-06.md` contains **zero** occurrences of `#622`, `#577`, `#936`, `#828`, `#830`, `#954`, "monolith", "decompose", "LET-DIE" | 0 for all nine |
| C34 | Mouse-over jiggle is at line 335 | line 335 exactly |

A claim of absence is the hardest thing to check and the easiest thing to assert.
This one holds, nine times.

### PR `#1139` -- action taxonomy

Command: `python scripts/generate_action_taxonomy.py --check`.

| # | Claim | Output |
|---|---|---|
| C35 | 62 entries, 61 distinct ids, 1 error, 6 warnings | `62 entries, 61 distinct ids, 1 errors, 6 warnings.` |
| C36 | 12 files scanned, 11 carrying actions, 9 doors, 9 loose tiles, 3 hidden; `risk_contributions.json` holds zero | all six exact |
| C37 | The five namespace-category doors are `operations`, `travel`, `financing`, `office`, `scouting` | named exactly, in that order |
| C38 | The `$75k`/`$90k` figure propagated into `SEED_FUNDING_MODES.md` | line 26: `` | `take_loan` | Business Loan | 1 AP -> $75k now, $90k debt. | `` |

`#1139` is the strongest-scoring artifact in this audit: every headline count in it
is produced by a committed generator, so every one is reducible to one command by
construction. That is the rule satisfied structurally rather than by discipline.

### PRs `#1120`, `#1143`, `#1145`, `#1146`

| # | Claim | Command / output |
|---|---|---|
| C39 | `#1145`: `turn_manager.gd:895` is `result["can_select_actions"] = ...` and is read by nothing shipped | line 895 exact; only consumers are tests and one comment |
| C40 | `#1145`: `state.can_end_turn` -- 9 writers, 0 readers | 9 writers exactly. **Caveat:** 3 sites read the value (save serialize, two result dicts); zero read it to branch. The table cell's own "why not done" column names the save schema, so the cell is internally coherent -- but "0 readers" is true only in the gating sense |
| C41 | `#1145`: `_step_check_events:541` whole-array replace; `seed_schedule.gd:56` append | both lines exact |
| C42 | `#1143`: no dev/debug surface mutates `pending_events` | `grep` over `godot/scripts/debug/` -> reads and tombstone comments only |
| C43 | `#1146`: **zero lines added to `main_ui.gd`** | `git show --stat 5731dd2e -- godot/scripts/ui/main_ui.gd` -> empty |
| C44 | `#1120`: P7 clean -- no raw `change_scene_*` outside the autoload | only comments referencing the rule |

### Cross-repo and store

| # | Claim | Command / output |
|---|---|---|
| C45 | 2,713 verdicts, untouched | `review_state.json` -> 2713 (keep 1958 / discard 469 / maybe 130 / reroll 84 / iterate 63 / blank 9) |
| C46 | "a migration across **5,267 Library files**" | `git ls-files art_source \| wc -l` -> **5267** exactly. **Caveat:** 801 of the 5,267 are not images (4,466 are), and the masters archive per `ART_MASTERS_POLICY` is excluded, so this counts the in-git half of what ADR-0019:46 defines as the Library. The number reproduces; the label is loose |
| C47 | `#28`: every other seat has checked in -- `#2` `#4` `#6` `#17` `#23` `#25` | all six exist, correct repo, correct seat, titles match |
| C48 | `#28`: "~40 merged PRs" in the week | 40 merged since 2026-07-31; 46 since 07-30 |
| C49 | `godot/assets` = 47 MB | `du -sm` -> 47 |

Rows C1-C49, of which C19, C21, C40 and C46 carry caveats stated in place. Several
of the same claims appear in two or three places (the corpus figures are in
`coordination#30`, `coordination#31` and PR `#1156` alike); each is counted once,
against the command that settles it.

---

## Did the method rediscover 2,197 independently?

**Yes, and it sharpened it.**

The extraction pass pulled *"across 2,197 pages"* out of `coordination#30` purely on
position -- a bolded summary line carrying a number -- before I had read
`pdoom1-website`'s 10:07Z correction, and flagged it under the rule's own test: a
claim about another repo's directory, with no command attached. Checking whether a
command existed turned up `pdoom1-website` cloned on the same machine, so the answer
was "yes, and nobody ran it."

Running it produced three numbers, not two: 2,197 files, 2,194 with suggest links,
**2,196 rendering rarity**. The published correction fixes only the second. pdoom1's
`#30` sentence asserts the third -- "badges, facets and sorts on it" -- so the
correction on the table does not actually correct pdoom1's sentence. That is new,
and the method found it because it demanded a command for the exact claim as worded
rather than accepting the neighbouring correction.

So the method works. Which means the rest of the results can be trusted to roughly
the degree this one instance was.

---

## Verdict on the rule

**Keep it.** But the audit found three distinct failure modes, only one of which the
rule as adopted catches, so keeping it unamended would be keeping a rule that scored
worse than this document implies.

**1. The rule works, and it earns its keep.** 6 wrong claims in 68 headline
positions -- 9 per cent. Two of the six (W2, W3, W4 are one defect with three
faces) sat in a **merged** PR body and would have gone into the changelog. One (W1)
had already reached two other repos. One (W5) was handed to `pdoom-data` as an
unblocking artefact. The rule is what surfaced every one of them, because in every
case the question "what command produces this?" was answerable and nobody had asked
it.

**2. It has a hole the audit walked straight into: a runnable command is not a run
command.** `#1155`'s table cells were *perfectly* reducible to
`grep offset_ godot/scenes/pause_menu.tscn`. That is why W2/W3/W4 are three of the
six -- the rule as worded was satisfied at the moment of writing and the tree moved
underneath it. **Amendment: the command must be re-run against the tree that
merges, not the tree that was current when the sentence was drafted.** A PR body
rebased onto new content is a stale document by default. The repo already knows
this shape -- it is why `sync_version.py --check` and `generate_dq_index.py --check`
are pre-commit gates and not instructions.

**3. It has a second hole, and this one is worse, because it is the `#640` defect
wearing the rule's own uniform.** W6 is a published command that returns 0 against
a file containing all four search terms. A rule that says "attach a command" and
nothing more will produce commands that cannot fail, which is strictly worse than
attaching nothing -- a bare claim invites scepticism; a claim with a command
attached buys credibility the command has not earned. **Amendment: a command
published in support of a headline claim must be shown capable of returning the
other answer**, exactly as this repo already requires of a test guard. One control
line. `grep -ci ... /tmp/ctl.txt -> 0` would have taken five seconds and caught it.

**4. What it does not catch at all, and should not be asked to.** Seven of the 68
claims are UNCHECKABLE, and the rule's remedy -- "move it into the body with its
hedge" -- was applied to **none** of them. `52 of 2,247` and `r = -0.0065` are still
in bolded sentences in the comment that adopts the rule. `75 per cent of their
feedback` is the seat's most-quoted sentence of the week and is now in a Manifund
draft. The rule was adopted at 10:55Z and violated above its own adoption in the
same comment. **That is the honest headline of this audit** and it is a stronger
finding than any individual wrong number: the seat wrote the rule down and did not
re-read the document it was writing it in.

**5. The counter-case, stated fairly.** 41 CONFIRMED is not a gentle result; it is a
real property of today's output, and two artifacts scored structurally rather than
by luck. `#1139` derives every headline count from a committed generator, so its
numbers cannot rot without a pre-commit failure. `#1156`'s appendix publishes the
reproduction formula, which is the only reason fourteen corpus figures were
checkable at all. **Both of those predate the rule.** So the honest reading is not
"the rule fixed something" -- it is "the repo already had the good pattern in two
places, and the rule is an attempt to state it as policy." The rule's marginal value
is what it does in the places that were not already generated.

**6. Recommendation.** Keep the rule with the two amendments above (re-run at merge;
show the command can fail). Do **not** trust it to fix the UNCHECKABLE class, which
is the larger and more contagious problem -- an unfalsifiable number in a bolded
sentence travels further than a wrong one, because nothing can catch it. For that
class the only remedy is the one `#1139` already demonstrates: derive the number
from a committed script, or do not put it in a table.

**And the falsifier, so this document meets its own standard.** If a re-run of this
audit against pdoom1's output for the week of 2026-08-13 finds a WRONG rate at or
above today's 9 per cent, the rule did not take and should be replaced with the
generator requirement rather than patched again.

---

*Audit performed against `origin/main` `9358c120`, 2026-08-06. Every command in this
document was run, not recalled. Where a claim could not be checked from this repo,
this document says so rather than inferring. Nothing found here was fixed -- fixing
widens the blast radius and this is an audit.*
