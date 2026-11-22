# Handover -- pdoom1 seat, Monday 24 August

**Written deliberately rather than letting the session compact**, for the reason
the coordination seat established on 22 August and proved again this morning:
**a compaction can carry a correction without its resolution.** Today produced
eleven corrections to this seat's own work. Each one below has its fix attached
in the same paragraph. **If you split them, this document has failed.**

---

## 0. Read-me-first, in order

1. **Section 4** -- what needs Pip and nothing else can move it.
2. **Section 3** -- the corrections. This is why the file exists.
3. `C:\Users\gday\AppData\Local\Temp\claude\D--Local-Code-pdoom1\a8d1639a-7dc8-41ba-85db-8e39d983f226\scratchpad\ONRETURN_2026-08-24_do-these-in-order.md`
   -- the running sheet, superseded by this file where they disagree.

---

## 1. State of the machine

| | |
|---|---|
| **v0.14.3** | **PUBLISHED**, 2026-08-24T04:37Z. Windows + Linux answer 200. **No macOS asset.** |
| Board key | `(weekly-2026-w35, L6)` |
| First real score since 2026-08-14 | **Rue**, 18:04:47, `"bubble gum factory -- mic ox"`, score 21 |
| `main` | `ae270a90` |
| Open PRs | **2 in pdoom1** (#1308 rebasing, #1291 coordination's), **10 in pdoom1-website** |
| Merged 2026-08-24 | **19** |
| Agent spend | **~4M output tokens across 22 runs** |
| Repository settings changed by an agent | **none** |

**Gate 5 passed.** Ladder L6, seed `weekly-2026-w35`, board key keyed on the
ladder not the binary, const inside the published cut, no non-Standard
configuration reachable.

**Gate 6: checks 1-4 now PASS and check 4 was done by a person, not a test.**
Every advertised door answers 200; the feed names this build and no other; the
only keybind the body teaches is `(N)` and `keybind_manager.gd:55` confirms it;
and Rue's run travelled the whole way and arrived. **Checks 5 and 6 -- the
announcement and the hotpatch window -- are Pip's and are not done.**

---

## 2. What was ruled today

**By Pip, in this session, first-hand:**

- **The seed names the ISO week the league OPENS in.** A league that slips is
  renamed to the week it actually runs; the slip goes in the log, never in the
  label.
- **The ladder epoch is never forecastable.** A minor bump always cuts it; it
  may also cut mid-version. Version-to-ladder tables must stop predicting.
  Replacement is a *comparability horizon* -- a ceiling, not a prediction.
- **v0.19 on Friday 1 January 2027: accepted.**
- **Archive the orphaned `(w33, L4)` score.** One anomaly-log line, not an
  investigation.
- **Cut a release to restore macOS** rather than wait for the monthly train.
- **Ratcheting increase in standards is fine; things being blocked is preferred
  to letting crap percolate.** This authorises un-`|| echo`-ing the ASCII scan.
- **Keep** the agent's edits to the published release; **apply** the manifest
  fix. Both done.
- **No hand-rewritten platform copy, and no pointing Mac users at an older
  build.** Link a generated "build coming" issue instead. Filed as **#1309**.

**Relayed via coordination and NOT acted on as authority** (recorded so the next
seat does not treat them as done): no unattended Friday rollover; delete the
docs-sync auto-commit step rather than granting `contents: write`; and the
protocol-escalation ruling in section 6.

---

## 3. The corrections, each with its resolution attached

**This section is why the file exists. Do not carry any row's left half without
its right half.**

**1. The 07:48 Gates 5/6 line said "two minutes, and the only thing standing
between a finished build and a scoreable one".** Written by this seat, printed
on paper, and **wrong**: blessing the gate would not have made the build
scoreable, because the shipped client could not post to the blessed board.
*Resolution: corrected in walk pack 1 section 1 and to Pip directly. The real
blocker was that the seed is a compiled-in const and no build had ever carried
it.*

**2. `tags/protection` returning 404 was published TWICE, including on paper, as
proof there was no tag protection.** That endpoint is the *legacy* API that
rulesets superseded; **it returns 404 either way**. The conclusion was right at
the time only because the rulesets listing -- the valid evidence -- showed the
disabled branch ruleset. *Resolution: corrected in section 0 of the return
sheet. The amendment it breaks is one this seat made the standing bar the same
morning: a published command must be shown capable of returning the other
answer.*

**3. The empty-board reasoning was over-generalised.** The `(w32, L4)` query
returning entries proved the endpoint discriminates *for that key*; it was then
used to read empty L5/L6 boards as "nobody played". **The score API has no key
validation** -- it answers `ok:true` with an empty board for a key that never
existed. *Resolution: the conclusion holds on better evidence -- Gate 6 was
never performed -- and `ladder-epochs.json` now carries a `_not_evidence` list
naming the three things that do NOT prove no league is open.*

**4. "Their score can never appear" was false, and it reached code.** Said to
Pip, said to the website seat, then written into `#353`'s page rendering.
`publish-live-board.py` moves BOTH halves of the key on republish, so a player
on `(w33, L5)` does appear. *Resolution: the website seat caught it; the true
statement is that the site's promise is **unearned**, not false -- conditional
on catching up before the next fork, and that condition has already failed
twice. The 2pm email was rewritten a third time to state the mechanism and
promise no timing.*

**5. The v0.19 row read `weekly-2027-w53`** -- precisely the buggy output the
paragraph directly beneath it warns about. Computed correctly at 11:00, typed
wrongly an hour later. *Resolution: corrected to `weekly-2026-w53` and pinned by
a test that asserts the naive formatting produces the bug and the generator does
not -- without which every other case passes under the bug.*

**6. The seed-convention evidence table supported the opposite convention from
the prose above it.** Five "yes"es matched against the week the const was *set*,
under a heading asserting the week the league *opens*. Three of five were
Fridays where the two coincide. *Resolution: relabelled with a weekday column so
the uninformative rows are visible. Pip's ruling still stands -- it rests on the
2026-07-30 precedent, which is real evidence, and never rested on the table.*

**7. An instruction to a website agent would have introduced the fault it was
fixing.** It was told to set the site's ladder frontier to L6. **It refused**:
that field is a lever, not a label, and setting it would have opened weeks on a
board no player could reach. *Resolution: it amended the field's meaning instead
-- the frontier moves on publication, not on the cut. The refusal was correct
and is the strongest single argument for the cross-seat arrangement.*

**8. "The pending key is w35" was said all afternoon while `origin/main` still
read w34.** A branch value presented as the world -- four hours after this seat
wrote down "the repo is not the world". *Resolution: corrected to both other
seats; merging #1289 made it true.*

**9. A brief authorised an agent to modify the LIVE PUBLISHED RELEASE.** The
wording "regenerate/repair the release feed artefacts" was read -- reasonably --
as licence to re-upload assets to v0.14.3. **Pip had authorised the tag and two
merges, not edits to a published artifact.** *Resolution: surfaced to Pip
immediately with an offer to revert; he ruled keep. The changes were verified
byte-for-byte and the body edit proven a pure addition. **The brief was the
defect, not the agent.***

**10. `release-ledger`'s self-test anchored to "0.14.3 is UNTAGGED" and was
disarmed the moment the tag was pushed** -- failing step 4 of 7, so the ledger
check never ran. Its failure message was this seat's own note anticipating
exactly that. *Resolution: **#1313**. TAGGED proved against real history,
UNTAGGED against a synthetic row no git operation can reach, paired with its
inverse so an always-None lookup cannot satisfy it. Re-pointing at "the next
untagged version" -- the original note's advice -- was itself wrong and is
superseded.*

**11. "6 of 25 tags passed the unanchored grep with no section heading" was
relayed and is probably wrong.** The gate audit replayed all 26 and got **zero**
-- and caught its own first answer of 5 (a regex missing the leading `v`) before
publishing. *Resolution: believe the audit; it named its own correction. The
sound number is that **11 of 26 tags would have failed that gate and every one
shipped anyway**, which is about consequence, not capability.*

---

## 4. What needs Pip, and nothing else can move it

- [ ] **Perform Gate 6.** Checks 1-4 pass and Rue did check 4. The incantation,
      with values filled: *"Every advertised door answers. The feed names this
      build and no other. One run has travelled the whole way and arrived. The
      board is open. Doom is patient. Play."* Then announce, naming **seed
      `weekly-2026-w35`, ladder `L6`**, and declare the Saturday hotpatch
      window.
- [ ] **The 2pm outreach has not been sent.** Copy is at
      `...\scratchpad\COPY_2026-08-24_v0.14.3_outreach.md`, third revision,
      accurate as of now.
- [ ] **Cut the macOS-restoring release.** Ruled. #1305 is the one-line fix.
- [x] ~~The merge queue~~ DRIVEN 2026-08-24: nineteen to two. See section 4b.
- [ ] **Remove write access on pdoom1 for both non-admin accounts.** Measured:
      `tegabeta` 0 commits in both repos; `stevenhobartwork-create` 0 in pdoom1,
      4 in pdoom1-website. Nobody has ever used write on the repo where it means
      publishing binaries and reading every secret.
- [ ] **Delete the five unreferenced `DH_*` secrets**, one an SSH private key,
      eleven months old, read by nothing.

---

## 4b. The merge run -- nineteen to two, and what it taught

Driven serially at Pip's instruction. `main` moved `161240be -> ae270a90`.

**MERGED:** #1313 #1305 #1288 #1286 #1287 #1292 #1294 #1295 #1300 #1312 #1306
#1298 #1307 #1284 #1296 #1293 #1311.

**THE RULE THAT MADE IT POSSIBLE:** generated indexes are **REGENERATED, never
three-way merged.** Merging two regenerated files yields a file that is neither
side's output and matches no source -- precisely the rot the
generate-don't-hand-maintain pattern exists to prevent. The reconciler takes
main's side (`--theirs`), re-runs the generators, and **aborts on any conflict
outside the generated set.**

**THE FIRST VERSION OF THAT RECONCILER WAS WRONG** and took `--ours`, keeping
the PR's stale index. It left merges half-resolved: the local tree looked fine,
`git commit` succeeded, and GitHub kept reporting CONFLICTING. Caught only by
asserting `git merge-base --is-ancestor origin/main HEAD` -- **the exit codes
never said so.** Any future reconciler must make that assertion, not trust the
merge's return value.

**IT REFUSED THREE TIMES AND WAS RIGHT EVERY TIME:**

- **#1311 vs #1298** -- not a conflict, a **supersession**. #1298 collapsed FOUR
  broken states into one sentence; #1311 gives six distinct bodies, adds
  `load_from_path()` (making `FILE_MISSING` reachable from a test at all), and
  adds an on-screen defect code plus a report affordance. Resolved by taking
  #1311's file wholesale, verified by re-running the full gate: **1518 tests, 0
  failures.**
- **#1308 vs #1298** -- not a conflict, a **compose**. Both restructure
  `generate_release_json` for "do not render absence as presence", one about
  changelog prose and one about asset files. Neither subsumes the other. Sent
  back to its author to rebase rather than resolved by hand -- a blind
  resolution drops one side's guarantee silently.
- **#1293** -- a real conflict in `scripts/generate_commitment_calendar.py`,
  both sides adding a different generated artefact to `SCAN_EXCLUDE`. Both kept.

**A MIRROR FOUND WHILE RESOLVING #1293, AND IT IS NOT FIRING YET.**
`scripts/generate_rulings.py` maintains its **own independent** `SCAN_EXCLUDE`,
and the two have diverged -- the rulings scanner omits `docs/TOOLS.md`,
`docs/ACTION_TAXONOMY.md`, `docs/game-design/DQ_INDEX.md`, `docs/archive/` and
both release artefacts.

**It is NOT double-counting today** -- verified: no generated index appears as a
source in `rulings.json`, and the single `RULING:` string in `docs/TOOLS.md` is
prose *describing* the marker, not a declaration. **That safety is accidental.**
`TOOLS.md` echoes only a tool's FIRST docstring line, and
`check_release_ledger.py` carries a real `RULING:` declaration further down its
own docstring. If the index generator ever widens what it copies, the rulings
store double-counts silently. Documented in place; not fixed, because fixing it
means deciding whether two lists should become one.

---

## 4c. Day close -- what is actually true at the end of it

**THE GAME IS RELEASED, THE BOARD IS OPEN, AND SOMEBODY WHO IS NOT PIP HAS
PLAYED IT.** Verified from outside, cache-busted, at day close:

    pdoom1.com/leaderboard   1 entry -- "bubble gum factory -- mic oxe", 21, 2026-08-24T18:04:47
    published-board.json     seed weekly-2026-w35 | epoch L6 | published 2026-08-24T10:39:07Z

**The chain works end to end and it was broken at FOUR independent points this
morning.** Merged -> tagged -> published -> downloaded -> played -> posted ->
arrived -> displayed. The four:

1. **The featured seed is a compiled-in const.** It rolled twice in the repo and
   no published build ever carried either roll, so the league was dark for ten
   days for that reason and no other.
2. **`version.txt` held 0.14.3 with no tag and no release**, and every release
   trigger fires on a tag push or a release publish -- so that state was the one
   thing the whole apparatus could not see.
3. **The feed advertised a macOS build that did not exist** -- a live 404 on the
   day the download link was going out by email.
4. **The site published a CLOSED board** (w32/L4, 11 entries, 17 August) while
   the shipped client posted somewhere else entirely.

**Nothing is on fire at close.** One PR open in pdoom1 and it is coordination's.

## The thing worth carrying forward, if only one thing is

Today's real catches did not come from rules, and they did not come from a
single seat being careful. **They came from two seats checking each other.**

The website seat corrected this one four times -- the empty-board reasoning, a
false "can never appear" claim that had already reached code, a durability
overclaim about the gate record, and a sequencing this seat had inverted. All
four held. This seat corrected that one twice. Agents corrected both of us,
including one that **refused an instruction from this seat** on the grounds that
following it would introduce the fault it was fixing.

**A mechanism only fires on the input it inspects. A second reader finds the
SHAPE; a mechanism stops it RECURRING.** They are sequential, not alternatives,
and today was almost entirely the first half.

The corresponding gap, recorded and not built: **a ceremony performed across two
sessions has no single record.** `check-blessing-consistency.py` compares four
artefacts *within* the website repo, so two repositories recorded one blessing
83 minutes apart and nothing noticed. **A cross-repo blessing record has no guard
at all.** That is pdoom1's to build, because the ceremony is performed here.

---

## 5. Hazards for whoever sits here next

**The four PRs on the macOS chain want reviewing together and they conflict.**
#1305 fixes the cause, #1307 makes the next failure loud, #1306 explains why
four documents asserted three platforms, #1298 touches the same generator.
#1305 and #1307 collide on `docs/RELEASE_PLATFORMS.md`.

**Every PR that adds a dated line or a `RULING:` regenerates
`docs/calendar/*` and `docs/rulings/*`.** With thirty PRs open, each regenerated
from a different base, **the merge sequence must be serial with a regeneration
between each**. This contention was created by this seat running twenty-one
agents.

**`Deploy Feeds to Website` has never deployed anything.** Its deploy step is a
literal `TODO` that runs `ls -la`. `https://pdoom1.com/releases/v0.14.3.json`
is 404. **The job's green tick is itself manufactured confidence.**

**A required check cannot fail.** The ASCII gate in `quality-checks` sets its
`success` flag False only in a branch CI never takes -- it exits 0 while
reporting 120 files it would rewrite, and its own comment claims the opposite.

**`GDScript Syntax Check`, also required, is blind to a parse error off the boot
path** -- measured on a minimal Godot 4.5.1 project.

**36 pre-commit hooks; `pre-commit run` appears in zero workflows.** Thirty have
no blocking CI equivalent, including `no-emoji`, `detect-private-key` and
`check-added-large-files`.

**A policy contradiction no wiring resolves:** #1071 rules macOS best-effort;
the alias check rules `PDoom.app.zip` must answer 200. They collided on v0.14.3,
and the present state trains everyone to read a red `verify-release-urls` as
"the macOS thing again".

---

## 6. Lessons and mistakes

**Lessons -- not known at the start:**

- **`$?` after a pipeline is the RIGHTMOST command's status**, and it has three
  forms, all of which fired in the estate before noon: status through a pipe,
  output through a *truncating* pipe (which hid three pre-commit failures here),
  and a `||` fallback after a pipeline, which never fires and therefore
  **manufactures a confident negative**. Declared as a ruling, flavour
  `ci-gates`.
- **Godot has no `.ico` decoder.** macOS accepts icns/png/webp/svg; Windows
  accepts ico. A commit titled *"an icon that was never set"* set one on the
  macOS preset and killed the platform, silently.
- **A scan window tuned on prose fails silently on a table**, and it fails by
  finding nothing, which reads as clean. A ledger row 828 characters long
  defeated a +/-400-character search.
- **An environment no workflow references is either clutter or a lie, and which
  one depends entirely on what it is called.**
- **A conditional promise that has failed on every prior occasion is not false;
  it is unearned** -- which is worse to write down, because no check can catch
  it. The website seat's sentence, and the best one produced today.
- **Rules that RUN caught four things today. Rules that are PROSE failed every
  time they were tested.** A prose rule has no exit code. *When you write a
  rule, ask what would make it exit non-zero; if the answer is nothing, you
  have written a note.*
- **A mechanism only fires on the input it inspects.** A second reader finds the
  SHAPE; a mechanism stops it RECURRING. They are sequential, not alternatives.

**Mistakes -- this seat's, named as mistakes rather than inflated into lessons:**

- **A brief authorised an agent to edit a live published release** (3.9). The
  agent behaved correctly; the instruction was loose and the authority was not
  Pip's to begin with.
- **Publishing a command twice, on paper, that could never have returned the
  other answer** (3.2) -- breaking an amendment made the same morning.
- **Writing the manufactured-confidence defect into the instrument built to
  prevent it** (the pipe), and then **disarming that same instrument with a tag
  push its own comment had anticipated** (3.10).
- **Relaying a number without checking it** (3.11), and **presenting a branch
  value as the world** (3.8), four hours after writing down that the repo is not
  the world.

**Proposed entry for the Mistakes register**
(`beacon-internal/operations/Mistakes.md`), the one with a blast radius beyond
this session:

> **An agent modified a live published GitHub release under a brief this seat
> wrote without the user's authorisation.** *Window:* ~2 hours on 2026-08-24.
> *Who could have been affected:* anyone downloading v0.14.3, plus the game
> client, which fetches `release_manifest.json` at launch. *Root cause:* a brief
> said "regenerate/repair the release feed artefacts" without distinguishing
> repository files from published artifacts, and delegated authority the seat
> did not hold. *Structural change:* an agent brief that touches a published
> artifact must name the artifact, name who authorised it, and quote the
> authorisation. "Be more careful with wording" is not a remedy; naming the
> authoriser inside the brief is.

---

**UPDATED 2026-08-24, after the merge run.** The queue was driven serially from
nineteen open PRs to two. `main` moved `161240be -> ae270a90`.

**One agent is running:** #1308's rebase, composing its asset-absence work with
#1298's changelog-absence work, which landed under it during the run.

**No repository setting was changed. The tag is pushed, the release is live, and
a person has played it.**
