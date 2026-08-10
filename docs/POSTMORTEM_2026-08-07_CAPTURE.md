# SUNDAY -- postmortem capture, 2026-08-06/07

**Tagged SUNDAY on purpose.** Nothing in this document needs to be read on
Friday night or Saturday. It is the unflattering half of the week, written down
while it is still checkable.

Companion to `docs/POSTMORTEM_2026-07-31_LEAGUE_DAY.md`, whose shape this
matches, and whose findings section 3 checks for recurrence.

**Method.** Every number below is either the output of a command run against
`origin/main` at `abd6c7d0` on 2026-08-07, or a quotation from a tracked file
or a merged commit message. Where a claim in the commissioning brief did not
reproduce, this document says so and gives the measurement instead -- three of
them did not reproduce as worded, and those corrections are in place, not
footnoted away.

**Bases.** `origin/main` @ `abd6c7d0`; tag `v0.13.2` @ `868c784e`; GitHub API
for issue/PR/CI state; `builds/playtest-2026-08-07/PDoom.pck` on disk.

---

## The one-sentence version

Forty-eight pull requests merged in seven days and **nothing shipped to a
player**: version frozen at `0.13.2` since 07-29, ladder frozen at L3 since
07-27, zero changelog entries, and the open-issue count moved **201 -> 208**
while the week's two triage lanes closed nothing they identified.

---

## 1. What changed this cycle

| Measurement | Command | Value |
|---|---|---|
| Commits on `main`, 08-05..08-07 | `git log --oneline --since=2026-08-05 origin/main \| wc -l` | **24** |
| Commits since tag `v0.13.2` | `git rev-list --count v0.13.2..origin/main` | **68** |
| PRs merged since 07-31 | `gh pr list --state merged` | **48** (16 on 08-06 alone) |
| PRs merged 08-05..08-07 | same | **24** |
| Open PRs now | `gh pr list --state open` | **2** (#1164, #1166) |
| Open issues now | `gh issue list --state open -q length` | **208** |
| Issues opened since 08-05 / closed | same | **19 opened, 5 closed** |
| Latest `Godot Tests` on main | `gh run list --workflow "Godot Tests"` | 1212 tests, 0 failures, 119 files, at `553f0b7c` |
| `version.txt` / `ladder_version.txt` | `cat` | **0.13.2** (last bumped 07-29) / **3** (last bumped 07-27) |
| Art night spend | run ledger, PR #1158 / #1164 | 652 + 306 images, **USD 46.75** of a 75.50 ceiling |

Three commits landed as **direct pushes to main**, not through a PR:
`abd6c7d0`, `c743710b`, `15902301`. One of those matters (F6 below).

What the cycle actually produced, by volume: nine documentation and audit
commits, eleven touching game code, seven touching the art pipeline, ten new
guard test files. The single largest output of the two days was **written
analysis**, not shipped software. Section 5 asks what that bought.

---

## 2. Failures, ranked by cost

Ranking is by cost if undetected, not by embarrassment.

### F1. Main carries a ladder-forking change on an unbumped ladder, and every automated guard passes

**What happened.** `8791ba47` (#1137, merged 2026-08-06 09:53) retimed the
historical deck and changed event probabilities. `docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md`
section 3.1 names as explicit bump triggers *"anything that changes which
events fire on a given seed"* and *"event probabilities"*. `ladder_version.txt`
was last modified in `9abe20a7`, which `git merge-base --is-ancestor` confirms
is an ancestor of `v0.13.2`. So none of the 68 post-tag commits touched it.

A run from current main is not comparable to the six scores already on the L3
board, and would be submitted under L3 anyway.

**Why every guard passed.** Three separate instruments were in the path and
none of them could have objected:

- Pre-commit (`.pre-commit-config.yaml:142-145`) checks that `version.txt` and
  `ladder_version.txt` are **synced to their derived copies**. Internal
  consistency, not whether a bump was owed.
- CI's check is named, in the YAML, `Ladder Bump Heuristic (advisory)` and ends
  `python tools/check_ladder_bump.py --base "origin/$BASE_REF" || true`
  (`.github/workflows/quality-checks.yml:69-79`). The `|| true` makes it
  structurally incapable of failing a build.
- `tools/check_ladder_bump.py:42-45` scopes itself to
  `GAMEPLAY_PREFIXES = ("godot/scripts/core/", "godot/data/")`. `#1137`'s
  central change is in `godot/autoload/event_service.gd`, which is not in that
  set. Even blocking, it would have missed this.

**Introduced vs discovered.** Introduced 2026-08-06 09:53. Discovered
2026-08-07 ~16:45, by a person sitting down to write a decision card, roughly
31 hours later. No instrument reported it in that window; none could have.

**Cost.** Contained, because nothing was published. A `.pck` exists at
`G:\Documents\Organising_Life\Code\pdoom1\builds\playtest-2026-08-07\PDoom.pck`
(16:20 today) built on the unbumped ladder -- but the same decision card calls
it *"explicitly not shippable, entirely fine for looking at"*, and no tag or
release exists past `v0.13.2`.

> **Correction to the brief.** The brief says a `.pck` *shipped* on a ladder
> that should have been bumped. Measured: a `.pck` was **built and handed to
> Pip for playtest**; nothing was published. "Shipped" is stronger than the
> evidence supports and this document will not use it.

**What would have caught it earlier.** Removing `|| true`, and adding
`godot/autoload/` to `GAMEPLAY_PREFIXES`. Both are one-line changes to files
that already exist.

### F2. The art gallery's entire script block failed to parse for three days, and the page looked fine

**What happened.** `build_full_gallery.py` held its page in a **non-raw** Python
triple-quoted template. A `\n\n` written into a JavaScript `confirm()` string
was compiled by Python into two real newlines, landing inside the JS string
literal:

```
  if (!confirm("Set " + label + " on " + targets.length +
               " UNREVIEWED asset(s) in this batch?

" +
               "Already-judged assets are left alone.")) return;
```

Chromium threw `SyntaxError: Invalid or unexpected token` at parse time, so the
whole `<script>` never executed. From the fix commit `51ca568c`:

> *"Not one key, not one click handler, not one verdict badge.
> `typeof cards === "undefined"`. ... Nothing looked wrong. The file was 4 MB,
> all 11,524 images resolved, every section rendered."*

**Introduced vs discovered.** Introduced `f239af06`, 2026-08-04 11:59.
Fixed `51ca568c`, 2026-08-07 14:48. **3.1 days.** It was discovered because Pip
opened it and said the keyboard did not work -- *"None of the keyboard inputs
are working - the little cards around the images don't seem to have things or
onmouseovers quite right?"* No test, no gate, no lane.

**Cost.** Three days in which the primary art-review surface silently did
nothing it advertised. Every verdict badge, note and colour was unpainted for
the whole window.

**What would have caught it earlier.** Exactly what the fix installed: the build
now runs `node --check` (or a built-in scanner) on its own emitted script and
**fails rather than writing a page whose keyboard is dead**. Also worth stating
plainly: `CLAUDE.md` already records this escape-mangling class -- a `\b` in a
non-raw Python string compiled to a literal backspace and made a PII check
report clean while ten records still carried email addresses. The rule was
written for heredocs; the same bug walked in through a template string.

### F3. `--picks` read 5,794 verdicts as non-favourable and said nothing

**What happened.** `run_art_night.py:559-562`:

```python
    if isinstance(raw, dict):
        candidates = [
            k for k, tags in raw.items() if set(t.lower() for t in tags) & FAVOURABLE_TAGS
        ]
```

`tags` is the per-id **record dict**, not a tag list. Iterating it yields the
field names `verdict` / `tags` / `note` / `updated_at`, which are disjoint from
`FAVOURABLE_TAGS` for every one of the 5,794 entries in `review_state.json`
(measured: 4,644 keep / 809 discard / 130 maybe / 126 iterate / 84 reroll).
No exception. `candidates` is empty, `unparsed` is empty because there was
nothing to report, `picks == []`.

The only output is `[ABORT] L2 needs picks and none parsed` -- which names the
symptom and would read identically against an empty file. The repo's own words,
in `export_picks.py:22-24`: *"Note the failure mode: not a crash, a shrug."*

A second, independent mismatch sat behind it: `iterate` -- the verdict L2 exists
to consume -- is not in `FAVOURABLE_TAGS` at all.

**Cost.** The L2 wave was blocked until diagnosed. Recoverable, but see F4.

### F4. `picks_target` would have discarded 15 of Pip's verdicts silently, and underspent the brief while doing it

`run_art_night.py` truncated with `picks = picks[:limit]` and printed nothing.
The spec's `picks_target` was 36; the review produced **51** parseable `iterate`
cells. From `manifests/art_night_2026-08-07.json:225-226`:

> *"36 would have made `load_picks` drop 15 of Pip's verdicts, and it drops them
> without printing anything."*

The money coupling is the part that makes this more than tidiness: at 36 picks
the run lands at USD 66.25, **below its own 68.00 underspend floor** -- and
underspending was Pip's explicitly stated failure condition for the night. A
silent data loss would have produced a silent brief failure.

Fixed in the same PR: the truncation now prints, with the comment *"a silently
dropped pick is the same class of wrongness as a silently dropped tag -- the
wave still looks like it ran correctly."*

### F5. Six of 68 headline claims the seat published in one day were wrong

`docs/CLAIM_AUDIT_2026-08-06.md`: **49 CONFIRMED / 6 WRONG / 7 UNCHECKABLE /
6 STALE**. A 9 per cent wrong rate in title, table-cell and bolded-sentence
positions. The blast radius, not the rate, is the finding:

| Row | The wrong claim | Where it travelled |
|---|---|---|
| W1 | "2,197 pages" | Two coordination issues, a sister repo's correction that fixes only one of two readings, and open PR #1156. The correct figure for what the sentence asserts is **2,196** and nobody has stated it |
| W2/W3/W4 | Panel box `800x740`, `+23%`, and seven measured resolution rows | **Merged** PR #1155's body -- the artifact Pip reviews. Shipped height is 792; the panel is 12px taller than the flat +30% the PR argues against |
| W5 | `event_service.gd:404-410`, declared re-measured | Handed to `pdoom-data` as its unblocking artefact. It is 406-412 on that tree |
| W6 | A published `grep` command returning 0 | A command that **cannot** return anything else -- see M1 |

**What makes this the seat's worst class rather than its most numerous.**
The audit's own verdict, quoted because paraphrase would soften it:

> *"The rule was adopted at 10:55Z and violated above its own adoption in the
> same comment. That is the honest headline of this audit."*

Two claims of the seven UNCHECKABLE -- `52 of 2,247` and `r = -0.0065` -- sit in
bolded sentences roughly fifty lines above the rule that forbids them. A third,
*"75 per cent of their feedback"* (two playtesters, one hour, no recording, no
instrument), is the seat's most-travelled sentence of the week and is now in a
Manifund draft.

### F6. A guarded data file changed on main and its guard did not run

Measured tonight, not previously recorded anywhere.

`abd6c7d0` (**a direct push to main**, no PR) edited `godot/data/credits.json`.
`godot/tests/unit/test_credits_data.gd` asserts against exactly that file
(`:61` *"credits.json carries no credit sections at all"*, `:66` the
eight-cats cross-check, `:111` an unresolved-marker scan).

`.github/workflows/godot-tests.yml` filters pushes to
`godot/**/*.gd`, `godot/**/*.tscn`, `godot/project.godot`, the workflow, and
the runner. **`godot/data/**` is not in that list.** The `pull_request` trigger
carries no path filter and would have caught it -- but this went in as a direct
push, so that path did not apply either.

Consequence: `gh run list --workflow "Godot Tests" --branch main` last shows
`553f0b7c`, 2026-08-06 23:23Z. Five commits have landed since, one of them
editing a file a test guards. Main's Godot suite is **green as of 553f0b7c**,
which is not the same sentence as "main is green", and this document will not
write the second one.

**Cost this time: zero** -- the edit was a one-line credit attribution. The cost
is the precedent: a data-driven game whose data directory is outside the push
test filter.

### F7. The phase guard was hollow on its first run

From `godot/tests/unit/test_phase_critical_state_guard.gd:121-126`, in the
shipped file, kept as a comment:

> *"an earlier draft excluded [a preceding '.'] and silently matched nothing in
> the two files that carried the live #1134 defect -- a hollow guard that passed
> for the wrong reason."*

The audit's own framing (`PHASE_GUARD_AUDIT_2026-08-06.md` section 6): *"First
draft compiled, ran, and reported 1 failure -- looking, at a glance, like a
working guard. It was not."*

This is in the failures list and not the wins list because the near-miss is the
finding: the guard would have shipped green, been counted as coverage, and been
cited later as evidence that the class was handled. It was caught only because
the lane was under a standing instruction to prove the guard red first.

The same audit records the boundary honestly: `turn_manager.gd` is allowlisted,
and D1 -- `_step_check_events:541` doing a whole-array replace of
`state.pending_events`, destroying `SeedSchedule.inject_event` appends -- is a
real, live, silent content-loss bug **inside an allowlisted file**. *"The
scanner is green on a live bug."* D1 is still unfixed, deliberately, because
fixing it forks replays.

### F8. The seat destroyed in-flight work in the main checkout twice in 24 hours

Both provable from `git reflog` in the main checkout:

| When | Reflog entry | What it discarded | Recovery |
|---|---|---|---|
| 2026-08-06 16:17:01 | `reset: moving to HEAD~1` | `98cc8068` -- the slot picker, 1,592 lines including `tools/assets/demand/slot_picks.json`, committed 15 minutes earlier | Re-landed as `624433cb` (PR #1154) |
| 2026-08-06 22:22:40 | `reset: moving to origin/main` | `df6f5f53` -- `docs/SEAT_VOICE.md`, the voice grant, committed 22:20:42 | Branch `recover-seat-voice`, then `cherry-pick` at 2026-08-07 09:20 |

> **Correction to the brief.** Git's reflog records `reset: moving to <target>`
> and **does not record the mode**. Nothing in this repo can distinguish
> `--hard` from `--mixed`. What is provable is that two resets in the main
> checkout discarded commits that then had to be recovered, one of them
> carrying the slot-pick file. The `--hard` flag itself is asserted, not
> measured, and is recorded here as such.

Adjacent, same destructive class, already recorded in
`docs/HANDOVER_2026-08-06_EVENING.md:186-188`:

> *"`git checkout -- godot/` has now discarded an agent's tracked edits TWICE.
> Both recovered by reapplying from context and re-running the gate."*

So: four destructive events in the shared checkout inside the cycle, all
recovered, none caught by anything but a person noticing the file was gone.

**This is the failure that does not fit the through-line**, and section 4 says
why that matters.

### F9. `[Unreleased]` has accumulated across five releases, and the changelog announces open issues as shipped

Measured on `CHANGELOG.md` (1,576 lines, not edited by this lane):

- **Six `## [Unreleased]` headings**, at lines 7, 468, 546, 807, 1174, 1344.
  Five are stranded mid-file behind released versions. The largest is 141 lines
  -- the single largest section in the file. Plus a `## [Previous]` at line 484.
- The top `[Unreleased]` at line 7 is **empty**, and `CHANGELOG.md` has not been
  touched since `c7951b8f` on 2026-07-29. **Zero of the 48 PRs merged since
  07-31 produced a changelog entry.**
- **`0.12.0` and `0.13.0` have no changelog section at all.** The file jumps
  `[v0.13.1] - 2026-07-25` straight to `[v0.11.0] - 2025-12-08`. Two shipped
  releases are undocumented.
- The `[0.13.2]` section's body is headed `### 2026-07-27 build day (rides the
  next version bump)` -- content authored for a future version, filed under a
  released one.
- `CHANGELOG.md` announces **#791** and **#811** as delivered.
  `gh issue view` reports both **OPEN** today.

**And the version that is public.** The published GitHub release body for
`v0.13.2` -- which pdoom1.com renders at `/game-changelog/` -- says at its line
71:

> *"**Research Quality System** (#500): Rushed / Standard / Thorough quality
> toggle for research"*

`#500` is **OPEN**, and the 08-06 triage records it as superseded by #1090
because the ruling moved quality to research-project level, i.e. the
global-toggle world it describes is not the world that shipped. The
`pdoom1-website` seat stated the limit of this evidence better than I can, so
its sentence stands:

> *"An open issue is not proof a feature is absent. What the table proves is
> narrower and still serious: **the release body is not derived from what
> shipped in that release.**"*

Filed during the cycle as **#1165**, and ruled in `coordination#35` where
pdoom1 named the general form: *"`[Unreleased]` is an accumulator with no
expiry and no owner ... a release-notes pipeline that can announce a
still-open issue is **not a documentation problem; it is a correctness problem
wearing documentation's clothes**."* The ticket is one of nineteen opened
against five closed.

> **Partial correction to the brief.** For #791 and #811 the mechanism is
> milder than "announced work that did not happen" -- both are open largely
> because squash-merge does not fire closes-keywords here. For #500 it is not
> milder: that entry is live on the public site describing a toggle the design
> ruling replaced.

### F10. The cost model reads its own constant back out of a log and the doc still calls it MEASURED

`estimate_cost_per_image()` returns a hardcoded table lookup
(`tools/assets/generate_images.py:65-77`). That value becomes `unit_cost`
(`:487`), is returned verbatim (`:353`), accumulated (`:654`), written into the
JSON record (`:672`) and into the log's `SUMMARY: ... cost=$...` line (`:706`).

`docs/art/SEED_ART_COST_MODEL.md` then reads those logs and tags the numbers
**MEASURED** -- lines 31, 33, 52 and 53, under a stated contract at lines 6-7
that "from logs" counts as a measured source.

The arithmetic proof, from `ART_RUN_2026-08-07.md`: the 2026-07-29 run logged
`cost=$1.08` for 12 images; `$0.09` is the literal table entry for `1536x1024`;
12 x 0.09 = 1.08 exactly. *"Nothing was measured."*

**Status: documented, not fixed.** `SEED_ART_COST_MODEL.md`'s last commit is
`a3962fe7`, well before this cycle. **The MEASURED tags are live in the tree
tonight.** A comment block was added above the constant in `1795cd12` warning
the next reader; the wrong document was not touched.

Adjacent finding from the same read, and the more expensive one: `quality` was
never passed to the Images API, so `auto` applied and was free to bill the high
tier -- **USD 0.20 against medium's 0.05 at 1536x1024, a silent 4x**. Consistent
with the 48-72 second render times in the 07-29 log. Every call now passes
`quality` explicitly. Without that single line, a projected USD 31 wave could
have billed USD 125.

### F11. Smaller, recorded so they are not rediscovered

- **`FEATURED_SEED_OVERRIDE` reads `weekly-2026-w31`; today is ISO 2026-W32.**
  Unresolved since Monday per the 08-06 handover.
- **The playtest build was cut from `merge/1158-main`, not from main.** Measured
  by grepping the emitted `.pck`: `commit=357173f3 date=2026-08-07
  branch=merge/1158-main`. It is correctly stamped and correctly labelled
  not-shippable; recorded because "the build he played" and "main" are again two
  different things.
- **`docs/ROADMAP.md:47` and `docs/RELEASE_NOMENCLATURE.md:89` both map
  `v0.14 -> L3`**, and L3 is already spent. Every row below is off by one.
  Filed as #1152; still open.
- **#1061, IP/trademark, was due Monday 2026-08-03.** Open. Pip asked to be
  forced on this one.
- **The seat raised a false consent alarm against itself.** The eight
  contributor cat photos were filed in `coordination#32` as an undischarged
  consent obligation. They were contributed with their owners' permission,
  confirmed by Pip on 08-06. Retracted -- *"That was wrong"* -- inside a day.
  Recorded because a false alarm from the auditing seat costs the same
  attention as a real one, and because the retraction is the part that worked.
- **Nine unattributed images are live on pdoom1.com right now**, and six of the
  nine are variants Pip **rejected**, published indistinguishably from the
  three he chose. They arrived as a side effect of an events-system commit --
  *"There is no commit where anyone decided to publish art."* The sync script
  that supposedly manages them, `sync-game-icons.py`, writes to a directory
  that does not exist and has apparently never successfully run.

---

## 3. Recurrences from the 2026-07-31 postmortem

This is the section that should be uncomfortable. Seven days elapsed.

### R1 (worst). "A check that cannot fail" recurred three times, once inside the guard for the thing that went wrong

07-31 FINDING 9 established the shape precisely: every step of the sync
workflow was `continue-on-error: true`, so *"the job could not reach a failed
state"*, and the runs reporting **success** contained the identical error. That
finding is nine days old at the time of writing.

This cycle, the same shape, three fresh instances:

| Instance | The mechanism | Caught by |
|---|---|---|
| `check_ladder_bump.py` in CI | `\|\| true` on the invocation -- structurally cannot fail a build. This is the guard for **F1**, the cycle's highest-cost defect | Nothing. Found by reading the YAML while writing this |
| W6, the published `grep` | Basic `grep` treats `\|` as a literal, so the command searches one 44-character string and returns 0 against a file containing all four words | The claim audit, by running a control line |
| The phase-guard regex | Excluded a preceding `.`, so `gm.state.pending_events.append(...)` -- the actual #1134 defect line -- matched nothing, and the suite went green | The lane, because it was required to prove the guard red first |

**A fourth instance, in a sister repo, in the same week.** `coordination#29`
reports that `certes`' `check-language.sh` split each rule line on its **first**
pipe, silently truncating three of seven regex-alternation rules to their first
alternative. `retreat.*hosting` -- *"one of the two violations this guard was
built after"* -- **was never being checked, for six months**. The tell was
printing in the output the whole time as garbled advice text; *"Nobody read
it."* Once fixed, a tracked file went red in one second.

That is the same defect as W6 (a shell metacharacter eating the rule) and the
same outcome as the ladder heuristic (green because the rule never ran). Four
instances, three repos, seven days.

**Why this is the sharpest thing in the pack.** The 07-31 postmortem named the
mechanism, in writing, in this repo. One week later the mechanism appears in the
guard covering the ladder -- the exact axis whose corruption 07-31's FINDING 5
was about. Naming a failure mode in a document demonstrably did not stop it
recurring; the two instances that *were* caught were caught by a **practice**
(prove it red, run a control), not by the document.

### R2. "The provenance display is the thing least able to be trusted about provenance" (07-31 F11) recurred, on money

07-31: `build_stamp.txt` inside the published v0.13.2 build read
`commit=fd60eb6 / date=2026-07-11 / branch=feat/dev-build-overlay-ledger` --
*"It does not fail; it confidently reports a plausible commit on a plausible
date."*

This cycle: the cost model (F10) reports a constant as MEASURED, and
`ASSET_PROVENANCE_SCOPE_2026-08-06.md` reaches the same conclusion from a third
direction -- *"Provenance is not missing information. It is discarded
information"* -- with PIL confirming that no `tEXt` chunk, no EXIF, nothing a
generator wrote, survives into a shipped PNG.

**The counter-case, and it is real.** The build stamp itself is fixed. Grepping
tonight's `.pck` returns `commit=357173f3 / date=2026-08-07`. #1067's fix took.
One of 07-31's eleven findings is closed and stayed closed.

### R3. "The instance-versus-class problem is the expensive one" (07-31 lesson 1) -- adopted at the audit layer, not at the fix layer

07-31: #1058 locked difficulty at 11:14; the identical hole in scenario, one
control away on the same screen, survived until 16:15.

This cycle the practice **was** operated: `PHASE_GUARD_AUDIT_2026-08-06.md`
exists precisely to hunt the class behind #1134, enumerated 10 phase-critical
variables and 34 mutation sites, and reported a near-null (0 confirmed reachable
permalocks). That is the 07-31 candidate practice working.

But the fix that shipped (#1143) was the instance -- delete the debug trigger --
and the class fix, *"a single guarded entry point"* for `pending_events`, was
filed as **#1148 and is open**. So: the class is now *enumerated* before the fix
lands, and still not *closed* by it. Half a recurrence.

### R4. "Every failure was in the gap between a proxy and the thing itself" -- four new rows for 07-31's table

| Proxy that was checked | The thing that mattered |
|---|---|
| the review page rendered | the review page's script parsed |
| `sync_version.py --check` reports no drift | the ladder should have moved |
| CI is green | CI ran on **this** commit |
| the cost is in the run log | the cost was billed |

07-31's table had six rows and its own summary was *"nothing was watching the
join."* Nothing has been built to watch a join since.

### R5. "Confidence-shaped output is a failure mode in its own right" (07-31 F6) recurred as the claim audit's own headline

07-31: the orchestrator presented a three-way Mac/Linux decision resting on a
premise that collapsed when Pip asked *"Why can't we build mac and linux assets
tonight? Just time?"* -- *"a decision matrix with tradeoffs and a
recommendation, resting on an unchecked assumption."*

This cycle: the seat adopted a rule requiring every headline claim to reduce to
a runnable command, and published two unfalsifiable bolded numbers fifty lines
above it in the same comment. The format signalled diligence the content did not
contain -- same sentence, different week.

### R6. 07-31's own open-items list

07-31 closed with thirteen items, five of them marked **"needs an issue"**. Of
those, three now have numbers (#1071 macOS, #1067 -> #1114 the release path,
#1072 -> #1099 the hardcoded exe name, all landed). That is a genuine
improvement over the 07-20 teardown, whose items mostly evaporated.

Against it: **#1061 (IP/trademark, due 2026-08-03) is four days overdue**, and
the 08-06 mining lane independently rediscovered the general rule -- *"Documenting
debt is not scheduling debt"* -- as a finding, without noticing it was
describing the pack it was written in.

---

## 4. Mechanisms -- the through-line, tested

The commissioning brief proposed one: *"a plausible output from a process that
did not do the work."* Tested against the eleven failures above, **it does not
hold as a mechanism.** It holds as a description of the *outcome* -- nothing
complained -- which is the property already recorded in this project's notes as
"silent wrongness". Naming the outcome is not naming the generator, and the
difference is operational: the four generators below have four different
remedies, and no single remedy catches more than one of them.

**Four mechanisms, plus one that is not a defect mechanism at all.**

### M1 -- The vacuous check

*An instrument exists, is wired in, and the bad answer is unreachable.*

Instances: `|| true` on the ladder heuristic; the `grep` whose `|` is a literal;
the phase-guard regex excluding a preceding `.`; historically,
`continue-on-error` on every sync step (07-31 F9) and the CI gate that ran zero
tests (#640).

Distinguishing property: **removing the instrument entirely would leave the
world no worse, and the reader better informed.** A bare claim invites
scepticism; a claim with a green check attached buys credibility the check has
not earned.

Remedy: an instrument must be shown returning the other answer. One control
line, one red run.

### M2 -- The absorbing empty state

*A consumer reads a producer in the wrong shape, and the wrong shape maps
cleanly onto a legitimate "nothing matched".*

Instances: `--picks` over 5,794 records (F3); `picks_target` truncating 15 (F4);
`apply_review.py` reporting 807 confident keeps of which 75 per cent could not
move; the website's `sync_icons()` reporting success on every scheduled run for
about eight months while doing nothing.

Distinguishing property: **no instrument is involved.** There is nothing to
harden. The data path itself has a state that is indistinguishable from success.

Remedy: zero is an error until proven. A tool that reads a store and finds no
usable records exits non-zero and names the store and the count it read.

### M3 -- The self-referential measurement

*A number is derived from a record of itself, then labelled as independently
observed.*

Instances: cost constant -> run log -> `SEED_ART_COST_MODEL.md` "MEASURED"
(F10); `event_service.gd:404-410` declared re-measured against a tree it was not
re-measured against (W5); "2,197" repeated from a sister repo without running a
one-second command on a clone sitting on the same disk (W1).

Distinguishing property: **the number is real and traceable.** Only its
provenance claim is false, which is why it survives inspection -- following the
citation leads somewhere.

Remedy: derive from a committed generator, or carry an explicit provenance flag.
The repo now does the second (`cost_is_billed_truth: false` in every sidecar)
and already did the first in two places (`generate_action_taxonomy.py`,
`DQ_INDEX.md`).

### M4 -- Escape mangling in a generated artefact

*The defect is invisible in the source and invisible in the output's
appearance. Only a parser sees it.*

Instances: the gallery's `\n\n` (F2); the `\b` in a non-raw string that made a
PII check report clean over ten records still carrying email addresses; the `|`
eaten by basic `grep` (which is M1 and M4 at once).

Distinguishing property: **looking harder does not help.** The 4 MB page
rendered, all 11,524 images resolved, every section drew.

Remedy: parse the emitted artefact before writing it. Installed for the gallery
in `51ca568c`; not yet installed for `build_slot_picker.py`.

### M5 -- Destructive operation in a shared checkout

*Not a plausible-output failure at all.* Two resets and two `checkout --`
invocations destroyed in-flight work (F8). Nothing about it looked fine; the
work was simply gone, and a person noticed.

It is listed because it cost real time, and because **its existence is the
cleanest disproof of the single-mechanism reading**. A cycle's defects are not
all one thing.

### What the four share, and what they do not

They share an outcome and a discovery channel: in every case the defect was
found by a human or an agent going and looking, and in no case by an automated
report. That is 07-31's one-sentence version, unchanged, which is itself a
result.

They do not share a fix. M1 wants a control line. M2 wants a non-zero exit. M3
wants a generator. M4 wants a parser. M5 wants a worktree. **A single remedy
would have caught at most one of the eleven failures above**, and a postmortem
that proposed one would be committing M1 in prose.

---

## 5. What the instruments actually bought

Honest accounting. Cost is agent-hours and Pip-attention; benefit is defects
found that nothing else would have found.

### The tri-repo workshop -- close to a null in the room, real value in the prep

`WORKSHOP_TRI_REPO_PREP_2026-08-06.md` is 1,012 lines. What the **prep** bought
is not in doubt: it demolished three of the agenda's four premises with
measurements (the 1,072-event cost figure does not reproduce -- nearest measured
is 1,073, and the direction is inverted: 975 records unchanged, 101 arriving
**nine turns later**, zero sooner), and it found two live code defects on the
way (`eligibility_end` written and read by nothing, so a `rare` event rolls
6 per cent per turn forever; and #1137 widening the `_get_rarity_settings`
poison-key trap from 4 keys to 7).

What the **room** bought is much less clear, and the seat said so in advance.
Its own disclosure: *"pdoom1 is the repo Pip works in every day. Its seat is
structurally the least independent of the three"*, and on the push-vs-pull
question, *"two of three seats are compromised on A2 bit 1 in the same
direction. Coordination should say so in the post-mortem rather than reading 3-0
as three independent derivations."* A ballot on which the seats had already seen
the same six public Pip rulings is not six independent votes.

**The null is on the record from two directions, and neither is mine.**
`pdoom-data`, in Phase 3: *"**Two of the six items did not need this
instrument.** A1 bit 1 and A3 came back four-way unanimous from four different
arguments. Unanimity is what an issue thread produces cheaply. **The workshop's
cost was not repaid there.**"* pdoom1's own accounting went further: *"**The
workshop was not necessary for four of six rulings.**"* The selection rule that
fell out is the keeper: **run a workshop when seats hold different evidence;
file an issue when they hold the same evidence and disagree about it.**

**The seal had a hole, and pdoom1 found it in its own protocol.** The sealed
file is gitignored in a repo no seat holds, so *"the verification the protocol
rests on is available to exactly one party -- the one whose honesty it was
built to make unnecessary."* The recorder agreed and fixed it, conceding the
sharper form: *"a commitment you cannot cleanly re-hash is not a commitment."*
That is M1 again, wearing a cryptographic hash instead of a green tick.

**Verdict: keep the prep, keep the seals, cut the agenda.** The recommendation
already on the record -- *"if this runs again, run it on two items, not six"* --
is the right one. Six items bought two contested rulings and four expensive
confirmations of things an issue thread would have produced free.

### The claim-audit rule -- keep it, but its marginal value is narrow

Found: 6 wrong in 68, two of them in a merged PR body, one already propagated to
two repos, one handed to another repo as an unblocking artefact. That is a real
catch and cheap.

Against it, from the audit's own section 5: the two artifacts that scored
structurally rather than by discipline -- #1139's committed generator and
#1156's published reproduction formula -- **both predate the rule**. So the
honest reading is not "the rule fixed something" but "the repo already had the
good pattern twice, and the rule is an attempt to state it as policy." Its
marginal value is confined to the places that were not already generated.

And it produced M1 in its own body (W6). A rule that says "attach a command"
and stops there manufactures commands that cannot fail.

**Verdict: keep, with the two amendments the audit names -- re-run at merge, and
show the command can return the other answer.** Do not expect it to touch the
UNCHECKABLE class, which is larger and travels further.

### The phase-guard audit -- earned its cost on the hollow-guard catch alone

A near-null by design (0 confirmed reachable permalocks outside what #1143
already deletes). It earned itself twice over anyway: it caught its own hollow
regex before shipping, and it found D1, a live silent content-loss bug. It also
states its own boundary rather than claiming coverage: *"The scanner is green on
a live bug."* And it declined to install a runtime invariant check that
false-fired in normal play, on the grounds that *"a guard that false-fires in
normal play trains people to ignore it, which is worse than no guard."*

**Verdict: the best-designed instrument of the cycle.** Six items handed back
undone, all named.

### The taste profile -- the only instrument with a same-day cash payoff

Its headline signals are modest and it says so: contrast 74.3 per cent
(n=136, p<0.0001) but *"35 of 136 slots went the other way. This is a tendency,
not a law"*, and the whole thing may be *"a profile of what survives a fast
glance"* given a **1.7-second median gap between decisions**.

Its **nulls** are what paid. Iterating a prompt bought nothing measurable
(highest-vN chosen 40 times against a random expectation of 47.3, p=0.34;
per-variant hit rates 33/43/25/32 per cent against a 34 per cent base rate).
That result reshaped the art run the same day: `l1_depth` -- 264 images and USD
13.20 of re-rolls -- became `l1_family`, 22 subjects x 12 coherent directions at
identical cost. And it killed the 2026-08-03 "highest variant wins" convention,
which had no support in Pip's actual behaviour.

It also flagged its own money risk: the hue result does not survive Bonferroni
correction, and *"a careless reading of this document could actively cost money
by narrowing the palette."*

**Verdict: the clearest earn in the pack.** A measured null redirected spend
within hours.

### Issue triage and mining -- the pair earned it, the triage alone would have done harm

The triage bucketed 201 issues and asserted six were absorbed by the UI
architecture doc. The mining lane checked the doc and found it contains **zero**
occurrences of `#622`, `#577`, `#936`, `#828`, `#830`, `#954`, "monolith",
"decompose" or "LET-DIE". Two of those (#622, #577) would have closed silently
and stayed closed, one of them carrying Pip's standing ruling that monolith
decomposition is deferred until release.

The mining lane's own calibration number is the one to keep: **32 of 50 issues
yielded nothing.** It reports the nothing.

**Verdict on the pair: earned.** **Verdict on the outcome: nothing happened.**
Zero of the ~50 closeable issues were closed. The open count went 201 -> 208.
An instrument whose output nobody actions is a cost with a report attached.

### The guard-first practice -- cheapest instrument, highest hit rate

From the 08-06 handover: *"Guards must be proven to fail before they are
trusted. Four lanes did this today; two of them found real bugs while doing
it."* Two of the three R1 instances above were caught this way.

**Verdict: keep, and make it the default rather than a lane-level habit.**

### What is ceremony

- **Printing documents nobody acts on.** The 08-06 handover's own heading:
  *"The three documents produced today, all printed, none acted on."* This pack
  is a fourth. Its falsifier is in section 6.
- **Bucketing issues without closing them.** See above.
- **A sealed convergence process among seats that share a source of truth.**
  Convergence measured after the seal is only evidence if independence was real,
  and two of three seats declared it was not.
- **`[Unreleased]` as a section.** Six headings, five stranded, nothing written
  into the live one for 48 PRs. A section nobody writes to is not a process.

---

## 6. Proposals for next week, each with a falsifier and a date

| # | Proposal | Falsifier | Date |
|---|---|---|---|
| P1 | Remove `\|\| true` from the ladder-bump check and add `godot/autoload/` to `GAMEPLAY_PREFIXES` | If by **2026-08-21** it has fired zero times **and** no ladder-owed change merged unbumped, it is dead weight -- delete it rather than keep a green ornament | 2026-08-21 |
| P2 | Add `godot/data/**` and `godot/**/*.json` to the `Godot Tests` push path filter | If no push-triggered run between now and **2026-08-21** touches only those paths, the filter change bought nothing and should be reverted rather than left as coverage theatre | 2026-08-21 |
| P3 | Every published measurement command ships a control line proving it can return the other answer | Re-run the claim audit on the week of **2026-08-13**. A WRONG rate at or above today's 9 per cent means the rule did not take and should be replaced with the generator requirement, not patched again | 2026-08-20 |
| P4 | Zero-result reads are errors. Any tool consuming a store and finding no usable records exits non-zero, naming the store and the count read | If this produces more than two false alarms by **2026-08-21**, it is mis-tuned and should be narrowed to the art tooling only | 2026-08-21 |
| P5 | Generated HTML/JS artefacts are parsed before they are written. Extend `51ca568c`'s gate to `build_slot_picker.py` | If the gate rejects nothing by **2026-09-01**, the raw-string fix was sufficient alone and the gate is cost without benefit | 2026-09-01 |
| P6 | No agent operates in the main checkout; lanes get worktrees | Read `git reflog` in the main checkout on **2026-08-21**. Any agent-attributable `reset` or `checkout --` means the rule was written and not operated -- the same failure as 07-31's unrecorded freeze exemption | 2026-08-21 |
| P7 | A ten-minute close-what-merged sweep, weekly | Open issue count on **2026-08-14**. If it is still at or above 208, the sweep did not happen and the triage lane should not be re-run until it does | 2026-08-14 |
| P8 | Correct the four MEASURED tags in `SEED_ART_COST_MODEL.md`, or delete the doc | `grep -n MEASURED docs/art/SEED_ART_COST_MODEL.md` on **2026-08-14**. Any survivor beside a log-derived cost means the finding was documented and not fixed, which is F10 repeating one week on | 2026-08-14 |

**And this pack's own falsifier.** If, on **2026-08-14**, none of P1-P8 has been
started and no issue references this document, then it is the fourth printed
document nobody acted on, and the correct response is to stop producing them --
not to produce a better one.

### These nine dates, declared so something other than a person can hold them

Section 6's dates were correct, written down, and reachable by
nobody on the day -- which is the same defect as F-series, one level up. The
lines below are the machine-readable form (`docs/calendar/COMMITMENTS.md`); they
restate the table above rather than replacing it, and the table stays the
argument.

COMMITMENT: 2026-08-14 -- P7 falsifier: open-issue count. At or above 208 means the weekly close-sweep did not happen and the triage lane must not re-run -- owner: pdoom1-seat -- kind: falsifier -- note: measured 211 on 2026-08-09, so this is already failing unless 4+ close first.

COMMITMENT: 2026-08-14 -- P8 falsifier: grep -n MEASURED docs/art/SEED_ART_COST_MODEL.md. Any survivor beside a log-derived cost is F10 repeating one week on -- owner: pdoom1-seat -- kind: falsifier

COMMITMENT: 2026-08-14 -- P9, the pack's OWN falsifier: if none of P1-P8 started and no issue cites this document, stop producing printed packs -- owner: pdoom1-seat -- kind: falsifier -- note: the only item on the list whose subject is the planning apparatus itself.

COMMITMENT: 2026-08-20 -- P3 falsifier: re-run the claim audit. A WRONG rate at or above 9 per cent means the control-line rule did not take -- owner: pdoom1-seat -- kind: falsifier -- covers: docs/CLAIM_AUDIT_2026-08-06.md -- note: section 6's P3 row carries TWO dates, 2026-08-13 in the falsifier prose and 2026-08-20 in the Date column. The Date column wins here; that ambiguity is exactly what a declaration removes.

COMMITMENT: 2026-08-21 -- P1 falsifier: if the ladder-bump check has fired zero times and no ladder-owed change merged unbumped, delete it rather than keep a green ornament -- owner: pdoom1-seat -- kind: falsifier

COMMITMENT: 2026-08-21 -- P2 falsifier: if no push-triggered run touched only godot/data or godot JSON paths, the path-filter change bought nothing -- owner: pdoom1-seat -- kind: falsifier

COMMITMENT: 2026-08-21 -- P4 falsifier: more than two false alarms from zero-result-reads-are-errors means it is mis-tuned and narrows to art tooling -- owner: pdoom1-seat -- kind: falsifier

COMMITMENT: 2026-08-21 -- P6 falsifier: read git reflog in the main checkout. Any agent-attributable reset or checkout -- means the worktree rule was written and not operated -- owner: pdoom1-seat -- kind: falsifier

COMMITMENT: 2026-09-01 -- P5 falsifier: if the parse-before-write gate has rejected nothing, the raw-string fix was sufficient alone and the gate is cost without benefit -- owner: pdoom1-seat -- kind: falsifier

---

## 7. Open questions for Pip

1. **The ladder.** L3 -> L4 or hold? The board has six entries from five
   players, which is thin enough that forking costs little. On the card you
   already have; repeated here because it is the highest-cost open item.
2. **The seed name.** `weekly-2026-w31` while the ISO week is W32. Under a
   weekly reading the roll is overdue; under monthly the name is misleading.
   Unresolved since Monday.
3. **The art payload.** 200.4 MB of promotable assets against the 58 MB you
   agreed to. It has grown three times, each time because a fix revealed cost a
   bug was hiding. Re-rule rather than assume the old answer holds.
4. **Is the workshop room worth repeating?** Convergence among seats that share
   your public rulings is not independent convergence, and two of three seats
   declared themselves compromised on the same question in the same direction.
   The prep clearly paid. The room is the part in question.
5. **#1061, IP/trademark.** Four days past due. You asked to be forced.
6. **`SEED_ART_COST_MODEL.md`.** Correct the MEASURED tags, or delete the
   document? It is currently a tracked file asserting a measurement that was
   never taken, and the cheapest honest option may be deletion.
7. **Does anything actually close issues?** Two lanes spent a day identifying
   ~50 closeable issues and closed none. Either someone owns the sweep, or the
   count is not a signal and we should stop treating it as one.

---

## What went right

After the failures, and without inflation.

- **The guard-first practice caught two real bugs**, including the phase guard's
  own hollow regex, before either shipped.
- **The build stamp is genuinely fixed.** 07-31's FINDING 11 is closed:
  tonight's `.pck` carries `commit=357173f3 / date=2026-08-07`.
- **A measured null changed spend the same day.** The iteration result
  redirected USD 13.20 of re-rolls into breadth before a single image fired.
- **The mining lane's 11 DO-NOT-CLOSE corrections** stopped two issues closing
  wrongly, one of them carrying a standing ruling of yours.
- **The gallery fix installed a gate, not just a patch** -- the build now proves
  its own script parses before writing the page, and the defect was
  demonstrated rejected by both gates.
- **The art night stayed inside its ceiling.** USD 46.75 of 75.50, 958 images,
  zero failures, and a hard module-constant ceiling that `--ceiling-usd` can
  only lower.
- **Two friends found in one hour what every internal playtest missed.** The
  08-06 handover's own read: *"because everyone internal has a working network,
  a populated board, and knows where fundraising is."* That is the cheapest
  instrument available and it is not on any schedule.

---

*Written 2026-08-07 for reading on Sunday 2026-08-09. Every command in this
document was run against `origin/main` at `abd6c7d0`, not recalled. Three
claims in the commissioning brief did not reproduce as worded and the
corrections are in place, not appended. Nothing found here was fixed -- fixing
widens the blast radius and this is a capture.*
