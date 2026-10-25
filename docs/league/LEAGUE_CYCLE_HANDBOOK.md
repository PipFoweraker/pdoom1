# League cycle handbook

**This is the MASTER copy.** Ruled by Pip on 2026-10-26 (#1266, #1267; recorded
in `docs/rulings/DECISIONS_2026-10-26_return.md`): pdoom1 owns the league-cycle
handbook; the website receives published versions according to protocol and
never holds the master copy. Section 10 says how a version reaches the website.

**Lineage and credit.** This handbook is carried over from
`pdoom1-website/docs/LEAGUE_CYCLE_HANDBOOK.md` (written 2026-07-31, website commit
`f5158133`, PR #211), whose explanations of the board key, bless-versus-roll and
the website's place in the gate rail are still the clearest in the estate and are
reused here nearly verbatim where they remain true. What changed, and why, is in
section 11.

**How to read it.** This handbook tries hard NOT to state volatile values (the
current epoch, the current seed) as facts, because a handbook that says "currently
L3" goes stale the day the ladder moves -- which is exactly what happened to the
website copy. Where a value matters, the handbook gives the command that reads it
from its source of truth. The one dated snapshot (section 1) is labelled as such.

**Authority.** `docs/RELEASE_NOMENCLATURE.md` is CANONICAL on epochs, seeds,
ladders and board keys; if this handbook disagrees with it, this handbook is
wrong. The gate procedures are `docs/rituals/`; a plain-language guide to them is
`docs/dev/RELEASE_GATES.md`.

Claims marked **NOT VERIFIED** could not be checked from a source by the author
on 2026-10-26; treat them as hearsay until someone does.

---

## 1. Where things stand -- read it, do not trust this paragraph

```
+----------------------------+--------------------------------------------------+
| Value                      | Read it with                                     |
+----------------------------+--------------------------------------------------+
| Ladder epoch (rules)       | cat ladder_version.txt                           |
| Build version              | cat version.txt                                  |
| Seed the shipped client    | grep -n FEATURED_SEED_OVERRIDE                   |
|   posts to (on main)       |   godot/autoload/game_config.gd                  |
| What a PUBLISHED build     | gh release download v<X.Y.Z>                     |
|   actually carries         |   -p release_manifest.json  (fields              |
|                            |   ladder_version, league_seed, commit_hash)      |
| Bump declared but unpaid?  | python3 tools/check_ladder_bump.py --owed        |
| Ledger of blessed boards   | pdoom1-website docs/LEAGUE_SEED_LEDGER.md        |
|                            |   (website-owned record; see section 9)          |
+----------------------------+--------------------------------------------------+
```

**Snapshot, read 2026-10-26 (will rot -- re-run the commands):**

- `ladder_version.txt` = `6`; `version.txt` = `0.14.4`.
- `FEATURED_SEED_OVERRIDE` = `weekly-2026-w35` on main.
- Latest published release is v0.14.4; its `release_manifest.json` carries
  `ladder_version: "6"`, `league_seed: "weekly-2026-w35"`.
- So the live board key is `(weekly-2026-w35, L6)`, blessed and opened
  2026-08-24 (gate record: `docs/rituals/records/GATE_RECORD_2026-08-24_v0.14.3.md`).
  The seed has not rotated since; the league has been effectively dormant during
  Pip's absence.
- `check_ladder_bump.py --owed` reports ONE unpaid bump: `397e4936` (#1280,
  hiring ad campaign reporting).
- Ruled 2026-10-26 (`ladder-epochs`): v0.14.5 ships on L6 with no bump; a fresh
  L7 board is cut at the start of the November 2026 release campaign, which also
  pays #1280's bump.

---

## 2. The board key, in one page

*(Carried over from the website handbook, examples updated.)*

A **board** is one leaderboard table. Every score the game submits carries a key
saying which table it belongs on. The key has two halves:

```
 ( seed ,              ladder_epoch )
    |                       |
    |                       +-- which RULES the score was earned under, e.g. "L6".
    |                           Ticks only when the rules change.
    +-------------------------- which SCENARIO everyone competes on,
                                e.g. "weekly-2026-w35".
```

**Two scores are comparable only if both halves match.** Same puzzle, same rules.

**The build version is NOT part of the key.** `v0.14.4` is not `L6`. A cosmetic
patch must never fork a board -- that is the whole point of the build-versus-
ladder split. One board legitimately spans several builds: the v0.14.3 and
v0.14.4 release manifests both carry the key `(weekly-2026-w35, L6)`, so clients
of both builds post to one board, and that is the split working.

Where the key comes from in code:

- `GameConfig.get_board_version()` returns `"L" + LADDER_VERSION`
  (`godot/autoload/game_config.gd`). `LADDER_VERSION` is stamped from
  `ladder_version.txt` by `tools/sync_version.py`; `--check` fails on drift.
- The seed is `GameConfig.get_weekly_seed()`, which returns
  `FEATURED_SEED_OVERRIDE` whenever it is non-empty (it is).
- The local board file is `user://leaderboards/leaderboard_<seed>__<L-version>.json`
  (`godot/scripts/leaderboard.gd`).
- Rebuilding the key from `CURRENT_VERSION` (the build string) anywhere is a
  fork bug; [Gate 3: SEED BLESSING] check 4 exists to catch it.

**Why this matters more than it sounds.** The score API answers a request for a
board that has never existed with `ok: true` and an empty list -- no error. That
is visible in source: `server/leaderboard/score_api.php` (in THIS repo) returns
`[]` from `load_board()` when the board file does not exist. So a wrong key is
**indistinguishable from nobody playing**, from the player's side and from ours.
It has happened: 27 real submissions from 6 players were stranded this way and
nobody noticed for a week (website handbook; **NOT VERIFIED** here -- the numbers
come from the website copy, not re-measured). They sit in the website's permanent
anomaly archive and must never be re-stamped.

One thing has improved since the website copy: a board file that EXISTS but cannot
be read now fails with HTTP 500 (`board unreadable; refusing to report it as
empty`) instead of also reading as empty. The never-existed case still reads as
empty, by design.

---

## 3. When each half of the key moves

```
+-----------------------------+      +-----------------------------+
|  SEED moves when...         |      |  LADDER EPOCH moves when... |
+-----------------------------+      +-----------------------------+
| a new league opens on the   |      | gameplay forks: "could two  |
| same rules (planned weekly  |      | identical runs, played the  |
| per RELEASE_NOMENCLATURE;   |      | same way, produce a         |
| in practice, per release),  |      | different score, trajectory |
| OR a board must open empty  |      | or RNG stream?"  YES -> L+1 |
| (a "roll", section 4)       |      | Every minor version cuts    |
|                             |      | one; mid-version forks can  |
| Name = ISO week the league  |      | cut more. Never forecast    |
| OPENS in (ruled 2026-08-24) |      | from a version number.      |
+-----------------------------+      +-----------------------------+
```

**The seed.** Ruled 2026-08-24 (`league-seeds`, declared at
`godot/autoload/game_config.gd`): the featured seed names the ISO week the league
opens in, so a league that slips is renamed to the week it actually runs and the
slip is recorded, never hidden in the label. A seed rolled in the repository that
never reaches a published build is skipped, not reused (`weekly-2026-w34` was
never published; see the v0.14.3 gate record).

Changing the seed is a **code change** (`FEATURED_SEED_OVERRIDE`), so it must be
merged BEFORE [Gate 3: SEED BLESSING], which since the 2026-10-26 reorder (#1025)
comes before the release-branch cut, so the cut carries it. After
[Gate 4: THE FREEZE] it means a cherry-pick to `release/v0.X`, a re-blessing and a
re-cut.

**When the epoch moves, does the seed move too?** Both precedents exist and both
were legitimate:

- **Held** (L4 -> L5, v0.14.2): the epoch half moved, so the key forked anyway;
  rolling the seed as well bought nothing.
- **Rolled** (L5 -> L6, v0.14.3): both halves moved together.

Either way the new board opens empty, because the key is new. The choice is about
naming, not fairness.

**The epoch.** `tools/check_ladder_bump.py` is a BLOCKING CI gate (armed in #1178):
a change under `godot/` outside UI/scenes/assets/theme/tests/docs needs either a
ladder bump or a `Ladder-Impact: none -- <reason>` line. Ruled 2026-08-23
(`ladder-epochs`): ladder debt is DECLARED when incurred (`Ladder-Impact: bump`)
and PAID at the release that ships it; deferring is legal, forgetting is not.
`check_ladder_bump.py --owed`, run at cut time, lists the unpaid declarations.

---

## 4. Bless vs roll -- the decision that keeps coming up

*(Carried over from the website handbook; still true.)*

Both words are about the **seed** half of the key. Neither touches the epoch.

| | **Bless in place** | **Roll** |
|---|---|---|
| What happens | Keep the seed the client already sends; record it as canonical | Change the client's seed const, then bless the new one |
| Board opens | With whatever is already on it | Empty |
| Cost | None -- no re-cut | A const change and a re-cut |
| Use when | Everything on the board is legitimate competition | Something on the board should not be in the competition |

**The deciding question: is everything currently on that board something you are
happy for players to compete against?** Yes -> bless in place. No -> roll.

There is no third option, because **nobody filters a live board.** Removing
entries is editing standings, and a board that can be edited is no longer a record
of what happened (*"filtering standings is editing them"* -- quoted in
`docs/rituals/gate_6_board_opens.md`). If something must not be on the opening
board, the league opens on a different key -- and since the epoch only moves for
rules, "get those runs off the board" and "roll the seed" are the same sentence.

Worked example (2026-07-31, old numbering): Gate 4 (PROVEN BUILD) proving runs sat on `(weekly-2026-w30, L3)`;
Pip ruled they should not open the league; rules unchanged so L3 stayed; the seed
rolled to `weekly-2026-w31`.

### Verify from the artifact, never by posting

After a roll you cannot verify by submitting a score -- that puts a run on the
board you just ruled must open empty. And **never verify by "the GET returned
ok: true"**: every wrong key returns that too.

Verify from the published artifact instead. That is now easier than when the
website copy was written: every release since v0.14.1 (#1175) ships a
`release_manifest.json` asset carrying `ladder_version` and `league_seed`
(written by `scripts/generate_release_manifest.py` in
`.github/workflows/enhanced-release.yml`). The v0.14.3 gate record also read the
seed from the build stamp inside the `.pck`.

---

## 5. One live board at a time: the hard cutover

Ruled 2026-10-26 (`league-seeds`, #823): **leagues use a hard cutover, not layered
overlapping lifespans.** The layered model floated in #823 (several staggered
leagues active at once) is not the plan.

```
   epoch L6 board                     epoch L7 board
 ===========================|        |=============================>
  (weekly-2026-w35, L6)     |        |  (<new seed>, L7)
  open, taking scores       |        |  opens EMPTY at the cut
                            v        |
                     CUTOVER INSTANT-+
                            |
                            +--> L6 board: closed, preserved read-only.
                                 Scores never migrate: different rules
                                 produced them.
```

What this implies, and what is **NOT VERIFIED / not yet specified**:

- Implied: at most one board is "the league" at any moment; the website shows it.
- Implied: a closed board's scores are history and are never merged forward.
- **Not specified anywhere I could find:** whether an old client that keeps
  posting to the closed key after the cutover is refused, ignored, or silently
  accepted onto a board nobody displays. From `score_api.php` the server appears
  to accept any key (it creates boards on first POST), so the closed board would
  keep accepting scores unless something else stops it. **NOT VERIFIED** against
  the deployed server. This deserves a decision before the L7 cut.

`docs/design/LEAGUE_CUTOVER_PLAYBOOK.md` has the measured timings and the
pre-stage / at-cutover split for an epoch cut.

---

## 6. What may reach a ranked board

A board key being stable and a board being comparable are different claims.
[Gate 3: SEED BLESSING] check 8 covers the second.

```
 +-------------------------+     +---------------------------+
 | difficulty              | --> | LOCKED to Standard        |
 |                         |     | (LEAGUE_DIFFICULTY_LOCK)  |
 +-------------------------+     +---------------------------+
 | scenario (Crisis,       | --> | is_ranked_run() == false  |
 | Sandbox, ...)           |     | -> never posted           |
 +-------------------------+     +---------------------------+
 | Alpha Tools used        | --> | is_ranked_run() == false  |
 |                         |     | (sticky, one-way flag)    |
 +-------------------------+     +---------------------------+
 | dev-assisted run        | --> | RULED: MARKED on the      |
 |                         |     | score, never excluded --  |
 |                         |     | NOT BUILT YET (#1012 open)|
 +-------------------------+     +---------------------------+
```

- Difficulty: `LEAGUE_DIFFICULTY_LOCK := true`, Standard, in
  `godot/autoload/game_config.gd` (#1058).
- Scenario and Alpha Tools: `GameConfig.is_ranked_run()` returns false if Alpha
  Tools were used or a scenario is set (#1060).
- Dev-assisted runs: ruled 2026-10-26 (`league-integrity`) that they are MARKED on
  submitted scores, never excluded. #1012 is still open: no dev-mode field reaches
  a submitted score today, so the ruling has no mechanism yet.

---

## 7. Where the website sits in the gate rail

*(Rewritten: the website copy predates the 2026-07-31 ritual sheets. Order and
numbers as reordered 2026-10-26, #1025.)*

| Gate | Website involvement |
|---|---|
| 1 LAST POUR | none |
| 2 PACK BLESSED | none |
| 3 SEED BLESSING | none -- the seed is blessed from this repository alone; the board attestation moved to Gate 6 in the reorder |
| 4 THE FREEZE | none |
| 5 PROVEN BUILD | none (release-URL checks were moved OFF this gate). Proving runs now play the league seed, so a proving run submitted globally lands on the league board early. |
| **6 BOARD OPENS** | **Check 7: the website serves a board for `(seed, L<N>)` and it is empty**, taken before check 4. Spoken as an ATTESTATION with a name and time attached, not as a fact -- the old clause "the board-key forks clean" was cut because the person saying it could not verify it. Check 4: one real run travels client -> backend -> board. Checks 1-2 verify the published download URLs and release feed. The website then publishes the board. |

What the website side must be able to attest at Gate 6 (from the website copy,
still the right list):

1. The API accepts the epoch key.
2. The site publishes whatever board the client posts to.
3. Earlier epochs stay preserved and read-only, never merged forward.

### Why the website needs no code change on ceremony day

Per the website copy (**NOT VERIFIED** against the current script, which lives in
the website repo): `pdoom1-website/scripts/publish-live-board.py` OBSERVES the
board key rather than being told it -- it finds whichever board on the current
epoch has the most recent activity and publishes that. Draw the seed, the client
posts to it, the next probe publishes it. Corollary from the same source: never
hardcode a seed in the website's `scripts/` or `public/data/`;
`test-weekly-league-boundary.py` enforces it. (Both scripts were confirmed to
EXIST on website `main` on 2026-10-26; their behaviour was not re-read.)

---

## 8. The one remaining human channel -- and it can now be retired

The website copy (section 5) said the current ladder epoch reaches the website by
a person typing it into `public/leaderboard/data/board-probe-targets.json`,
because pdoom1 published no machine-readable epoch artifact.

**The second half of that is no longer true.** Since v0.14.1 every release ships
`release_manifest.json` with `ladder_version` and `league_seed` (verified
2026-10-26 on the v0.14.4 asset). `docs/LEDGER_ROW_PROTOCOL_2026-08-21.md` noted
this on 2026-08-21.

**The first half still is.** On website `main` as read 2026-10-26,
`board-probe-targets.json` `current_ladder_epoch` = `L6`, `declared_on`
2026-08-24, still hand-declared. Its own `supersede_when` condition ("pdoom1
publishes the ladder epoch as a fetchable artifact") is met.

**So, at the L7 cut:** either a human updates that file (the current, fragile
step), or -- better, and website-side work -- the website reads the epoch from the
latest release's `release_manifest.json`. Until that lands, an epoch fork with no
update to that file is a silent wrong-board bug.

---

## 9. Records, and who owns which

| Record | Owner | Notes |
|---|---|---|
| This handbook | pdoom1 (master) | Website gets published copies (section 10) |
| `ladder_version.txt`, `FEATURED_SEED_OVERRIDE` | pdoom1 | The sources of truth for the key |
| Gate records (`docs/rituals/records/`) | pdoom1 | What was spoken, with check results |
| `LEAGUE_SEED_LEDGER.md` (blessings log) | pdoom1-website | Not moved by the 2026-10-26 ruling, which covers the handbook only. Whether the ledger should also move is an open question for Pip. |
| Anomaly archive, `public/leaderboard/data/preserved/` | pdoom1-website | Immutable. Never edit, never re-stamp. |
| `board-probe-targets.json` | pdoom1-website | See section 8 |

Release branches and tags: from 2026-10-26 the release-branch model in
`RELEASING.md` is adopted for real (`release/v0.X` per epoch; tags only from
release branches), and only Pip creates release tags (GitHub ruleset on `v*`).
Agents must never push a `v*` tag. Read `RELEASING.md` for the procedure; this
handbook does not restate it.

---

## 10. Publishing protocol -- how a version reaches the website

**Status: PROPOSED. None of the publishing machinery below exists yet.** What
exists today is listed separately so the two are never confused.

### What exists today

- The website already renders pdoom1 docs by a GENERATED path:
  `pdoom1-website/.github/workflows/sync-design-notes.yml` runs
  `scripts/sync/sync-design-notes.py` twice daily and on `repository_dispatch`
  (`pdoom1_release`, `pdoom1_docs_update`). It reads an ALLOWLIST (only
  `docs/game-design/decisions/ADR-*.md` from pdoom1), scrubs internal markers,
  renders HTML into `public/design-notes/`, and writes a `manifest.json`.
- The older raw-docs mirror (`sync-pdoom1-docs.yml`) is PARKED because it
  rsynced the whole docs tree, internal material included. Its own comment says:
  allowlist, never denylist.
- The website's hand-written `docs/LEAGUE_CYCLE_HANDBOOK.md` is the copy this
  file supersedes. Nothing keeps it in sync.

### What is proposed

```
 pdoom1 (master)                                pdoom1-website (published)
+-------------------------------+              +--------------------------------+
| docs/league/                  |   sync job   | public/<league-handbook page>  |
|   LEAGUE_CYCLE_HANDBOOK.md    | -----------> |  rendered HTML, carrying:      |
|                               |  (website    |   source: pdoom1@<commit SHA>  |
| edited ONLY here, via PR      |   side,      |   source path                  |
|                               |   allowlist  |   rendered-at timestamp        |
+-------------------------------+   entry)     |   "do not edit -- generated"   |
                                               +--------------------------------+
                                                              |
                                               staleness check (website CI):
                                               rendered SHA's copy of the file
                                               == file at pdoom1 main / latest
                                               release?  NO -> fail loudly
```

1. **One allowlist entry, not a new pipeline.** Extend the existing design-notes
   sync (or a sibling script built the same way) with this file's path. The
   website never hand-edits the output.
2. **Source header on every published copy.** pdoom1 commit SHA, source path,
   render time, and a "generated -- edit in pdoom1" line, so a reader can always
   find the master.
3. **Which ref publishes.** Recommend: the latest release tag for player-facing
   pages, falling back to `main` (the design-notes job already resolves refs this
   way). A handbook change that matters on league night should therefore ship
   with -- or be followed by -- a docs dispatch.
4. **Staleness check, website side.** A CI step that compares the published
   copy's source SHA against the current file at the chosen ref, and fails (or
   files an issue) when they differ for longer than one sync cycle.
5. **Retire the old copy.** Replace the body of
   `pdoom1-website/docs/LEAGUE_CYCLE_HANDBOOK.md` with a pointer to this file.
   That is a website-repo change; it is not made by this PR.
6. **Scrub before publish.** This handbook is written to be publishable, but the
   sync's existing scrub (HTML comments, session attributions, TODOs) should run
   over it like any other allowlisted file.

The broader plan for putting dev notes and tools on the website is
`docs/dev/WEBSITE_DEV_NOTES_PLAN.md`.

---

## 11. What changed from the website copy (2026-07-31 -> 2026-10-26)

| Website copy said | Now |
|---|---|
| Examples at `L3`, seed `weekly-2026-w31` | Ladder is at L6; examples updated; volatile values replaced by commands (section 1) |
| Gate 5's website line is "board-key fork verified clean" | That clause was cut from the ritual sheet the same day and became a named attestation; since the 2026-10-26 reorder it is [Gate 6: BOARD OPENS] check 7, and SEED BLESSING is Gate 3 (section 7) |
| Gate 6 website involvement: "display points at the live board" | Gate 6 now owns URL checks, the empty-board attestation and the end-to-end real-run check |
| pdoom1 publishes no machine-readable epoch artifact | False since v0.14.1: `release_manifest.json` carries `ladder_version` and `league_seed` (section 8) |
| (silent) | Seed naming rule (ISO week of opening), held-vs-rolled precedents, ladder-debt rule, blocking `check_ladder_bump.py` (section 3) |
| (silent) | Hard-cutover ruling (#823), what may reach a ranked board, dev-assisted runs marked not excluded (sections 5, 6) |
| (silent) | The score API is in this repo (`server/leaderboard/score_api.php`); unreadable boards now 500 instead of reading empty (section 2) |
| Lives on the website | Master lives here; website gets generated copies (section 10) |

Still true and carried over: the two-halves board key, build-is-not-key,
"wrong key looks like nobody played", bless-vs-roll and its deciding question, no
filtering a live board, verify from the artifact, scores never migrate across a
fork, the anomaly archive is immutable, and "if the board looks wrong, suspect the
key before suspecting the players" (`python scripts/check-board-liveness.py` in
the website repo prints every board it can find and whether each is DEPLOYED,
archived or a NEW ORPHAN -- per the website copy, **NOT VERIFIED** here).

---

## 12. NOT VERIFIED -- for Pip or a website-side check

1. The "27 submissions from 6 players stranded" figure (section 2) -- from the
   website copy only.
2. Whether the deployed score server keeps accepting posts to a closed epoch's
   board after a hard cutover (section 5). Source suggests yes; not tested.
3. `publish-live-board.py` still observes the key rather than being told it, and
   `check-board-liveness.py` output categories (sections 7, 11) -- existence
   confirmed, behaviour not re-read.
4. Whether the seed is still meant to rotate WEEKLY (`RELEASE_NOMENCLATURE.md`
   says every Friday) or per release (what has actually happened since August).
   This handbook describes both and asserts neither as policy.
