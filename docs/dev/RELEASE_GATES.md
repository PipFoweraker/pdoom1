# The release / league gates -- a plain-language guide

**Who this is for:** anyone (including Pip, back after months away) who needs to
know what the six league-week gates are, why they exist, and how their order
was decided. It explains; it does not legislate.

**Where the authority lives -- this page never overrides it:**

| Question | Authoritative source |
|---|---|
| The exact checks, commands and incantation for each gate | `docs/rituals/gate_1_last_pour.md` ... `gate_6_board_opens.md` |
| The ceremony's narrative and the week shape (v0) | `docs/game-design/LEAGUE_WEEK_PLAYBOOK.md` |
| What an epoch, seed, ladder and board key ARE | `docs/RELEASE_NOMENCLATURE.md` (CANONICAL) |
| Branches, tags and hotpatch criteria | `RELEASING.md` |
| Epoch-cut runbook and measured cutover timings | `docs/RELEASE_AND_LEAGUE_CYCLE.html`, `docs/design/LEAGUE_CUTOVER_PLAYBOOK.md` |
| The league board model, end to end | `docs/league/LEAGUE_CYCLE_HANDBOOK.md` |
| A worked record of gates actually performed | `docs/rituals/records/GATE_RECORD_2026-08-24_v0.14.3.md` |

If this page and a ritual sheet disagree, the sheet is right and this page is
stale -- fix this page.

---

## 1. The idea in one box

```
+--------------------------------------------------------------------------+
|  A league is a promise to players: "every score on this board was earned |
|  on the same puzzle (seed), under the same rules (ladder epoch), with a   |
|  build somebody actually played."                                         |
|                                                                           |
|  The gates are six checkpoints that each protect ONE part of that        |
|  promise. Each gate = entry criteria -> literal commands -> a sentence    |
|  spoken out loud. A gate PASSES only when every clause of the sentence    |
|  is backed by a check that was run. Saying a line you have not verified   |
|  is the cardinal sin of the ceremony.                                     |
+--------------------------------------------------------------------------+
```

The spoken sentence (the "incantation") is not decoration: it is a checklist you
can say out loud, and every clause in it maps to a command in the ritual sheet.

## 2. Who does what

```
+-------------------+     +-------------------+     +-------------------+
|  THE BUREAU       |     |  THE CLERK        |     |  THE COMMISSIONER |
|  (agent lanes)    | --> |  (Fable)          | --> |  (Pip)            |
|                   |     |                   |     |                   |
|  builds, pushes,  |     |  prepares tables, |     |  the ONLY one who |
|  never blesses    |     |  evidence, papers;|     |  blesses. Speaks  |
|                   |     |  may say READY,   |     |  the incantation; |
|                   |     |  never PASSED     |     |  a gate is PASSED |
|                   |     |                   |     |  when he says so  |
+-------------------+     +-------------------+     +-------------------+
```

Roles are defined in `docs/rituals/README.md`, section "Authority".

## 3. The six gates at a glance

Gates are written name-first with their number (`[Gate 5: PROVEN BUILD]`), per
Pip's 2026-07-29 ruling. Since 2026-10-26 (#1025) they run in the order
**decide, lock, prove, open**; the names are unchanged and the numbers follow
the new order. Records dated before 2026-10-26 use the old numbers -- the
mapping table is in `docs/rituals/README.md`.

```
 DECIDE (main still open)
+----------------------+   +----------------------+   +----------------------+
| [Gate 1] LAST POUR   |   | [Gate 2] PACK BLESSED|   | [Gate 3] SEED        |
| Wed ~1200            |-->| Wed EOD / Thu AM     |-->| BLESSING             |
| last mechanics PR    |   | league content pack  |   | seed spoken; the     |
| enters review; every |   | read + clean of      |   | seed const is MERGED |
| open PR is MERGE or  |   | printed doom -- or   |   | on the line about to |
| PARK                 |   | "there is no pack"   |   | be cut; key (seed,L) |
+----------------------+   +----------------------+   +----------------------+
                                                                  |
          +-------------------------------------------------------+
          v
 LOCK                       PROVE                      OPEN
+----------------------+   +----------------------+   +----------------------+
| [Gate 4] THE FREEZE  |   | [Gate 5] PROVEN BUILD|   | [Gate 6] BOARD OPENS |
| cut release/v0.X at  |-->| built from the branch|-->| Fri ~1700            |
| a SHA; ladder final; |   | head, proven fresh,  |   | tag + workflow green;|
| branch carries the   |   | carries the blessed  |   | downloads answer;    |
| blessed seed; tests  |   | seed, PLAYED by a    |   | board attested empty;|
| counted; a run STARTS|   | human, clean machine |   | one real run arrives |
| (windowed boot)      |   |                      |   |                      |
+----------------------+   +----------------------+   +----------------------+
                                                                  |
                                                                  v
                                                       Sat AM: hotpatch watch
                                                       window; retro slot
```

The weekday labels come from the v0 playbook, written for a weekly league, and
the slots for Gates 3-5 were not re-ruled with the reorder. In practice the
gates have been run at RELEASE time rather than on a fixed Wednesday-Friday:
the v0.14.3 record shows SEED BLESSING and BOARD OPENS performed on Monday
2026-08-24. Read the days as an ordering, not a calendar.

## 4. Gate by gate: what it checks, who, and what it protects against

| Gate | What it checks (summary; commands live in the sheet) | Who | Protects against |
|---|---|---|---|
| **1 LAST POUR** | Open-PR list snapshotted to a timestamped file; every PR marked MERGE or PARK; none unaccounted; nothing parked is labelled league-critical | Clerk prepares table, Commissioner rules each row | Work sneaking into the month without a decision; "what was open at the pour?" becoming a memory instead of a fact |
| **2 PACK BLESSED** | Branch A (no pack): prove the schedule is structurally empty. Branch B (pack): loader validates, zero printed-doom deltas, ladder bumped on `main` before the freeze, every card read by Pip | Commissioner reads every card | Unread or doom-printing content shipping; a gate being silently skipped when its subject does not exist |
| **3 SEED BLESSING** | Ladder value read aloud; `FEATURED_SEED_OVERRIDE` matches the seed spoken AND is merged on the line the freeze will cut from; board key derives from `get_board_version()`; no non-Standard config can reach the board | Commissioner speaks | Blessed seed and posted seed diverging; the key re-coupling to the build string; Easy/Sandbox runs landing on the ranked board (#1058, #1060) |
| **4 THE FREEZE** | `release/v0.X` cut and pushed, SHA recorded; `sync_version.py --check` exits 0; fast gate green above the 300-test floor; ladder declared final and equal to the one blessed; the branch carries the blessed seed; `check_ladder_bump.py` findings read; **class-cache pre-flight, then a windowed launch where a run actually starts** | Commissioner only | Rules changing after the league's ruleset is fixed; version/ladder drift forking the board key; a "green" CI that ran zero tests (#640); a freeze spoken over a build that does not start (#1023) |
| **5 PROVEN BUILD** | Built from the release-branch head; `build_release.py` proves its freshness marker is in the `.pck`; version agrees; changelog heading; cut number + base SHA recorded; **the seed inside the cut is the blessed seed**; machine reset to a clean player state; **a human plays the built artifact** | Commissioner plays; Bureau must not touch the working tree | Shipping "the thing we meant" instead of "the thing we ship": stale export caches, presentation bugs no headless test can see (#1039 found four), a playtest of the wrong config (the Crisis-Mode scare), a cut that does not carry the blessed seed |
| **6 BOARD OPENS** | Tag pushed and release workflow green; every advertised download URL answers 200; release feed's "latest" is this release; release body teaches no dead keybind; website board attested empty by a named person; one real run travels client -> backend -> board; announcement posted | Commissioner; website state is someone else's attestation | A league whose download 404s; a feed calling an old build "latest" (#1008); an empty board that is really a broken chain; opening on a board proving runs already dirtied |

Three rules from `docs/rituals/README.md` explain most of the design:

```
+--------------------------------------------------------------------------+
| 1. Every clause maps to a check.   No check -> cut it, or label it as a   |
|                                    stated judgement.                      |
| 2. A check must be runnable at the moment the line is spoken.             |
|    (That is why release-URL checking moved from PROVEN BUILD to BOARD    |
|    OPENS -- no tag exists at the build -- and why "the seed is inside    |
|    the cut" moved from SEED BLESSING to PROVEN BUILD in the reorder.)    |
| 3. A FALSE line has a named next step. Each sheet has a "When a line is  |
|    FALSE" section.                                                        |
+--------------------------------------------------------------------------+
```

## 5. The re-cut loop (the part that surprises people)

A build is not patched; it is re-cut. Anything league-critical that lands after
the freeze (on `main` first, then cherry-picked to `release/v0.X`) kills every
earlier cut and sends you back through Gate 5 -- including the human playtest,
at least over the surface the change touched.

```
          +-------------------------------+
          | [Gate 4] FREEZE: release/v0.X |
          | cut at SHA-1                  |
          +---------------+---------------+
                          |
                          v
          +-------------------------------+
   +----->| [Gate 5] cut k from SHA-n     |
   |      | (release branch head)         |
   |      | build, prove, PLAY            |
   |      +---------------+---------------+
   |                      |
   |            playtest finds a bug?
   |              /               \
   |           yes                 no
   |            |                   |
   |            v                   v
   |     league-critical?     +-------------------+
   |       /        \         | [Gate 6] BOARD    |
   |     yes         no ----->| OPENS on cut k    |
   |      |    (file it as    +-------------------+
   |      |    hotpatch-48h /
   |      |    next-release, continue)
   |      v
   |  fix lands on main, cherry-picked to
   |  release/v0.X (legal past the freeze);
   |  record new SHA-n; cut k+1 kills cut k
   +------+
```

Why so strict: two builds reporting the same ladder epoch while playing
differently is a lie nothing downstream can detect (#1039).

## 6. Issue #1025 -- the gate order (RULED 2026-10-26)

**Status: RULED.** Pip chose the order *decide, lock, prove, open*. The
ruling text, verbatim (2026-10-26):

> gates reorder to decide, lock, prove, open: Last Pour,
> Pack Blessed, Seed Blessing, then The Freeze (= the release-branch cut, plus
> a windowed check that a run actually starts), then Proven Build, then Board
> Opens; gate names stay, numbers follow the new order

Source: `docs/rulings/DECISIONS_2026-10-26_return.md`, item 6 (PR #1350). The
ritual sheets in `docs/rituals/` were amended to match; each moved sheet lists
the checks that moved with it.

### What went wrong under the old order

```
 2026-07-29                                                  2026-07-30
 --------------------------------------------------------------------------->
      ~22:13                 22:28                           Thursday
        |                      |                                 |
  a launch shows a full   THE FREEZE (then                 PROVEN BUILD
  UI with NO game state   Gate 2) declared.                (then Gate 4): the
  (#1023, the "boot       Every check passed               first time anyone
  ghost")                 -- because no check              is REQUIRED to have
                          asks "does it run?"              launched the thing
```

The freeze checked the ladder, the version and the tests. None of those asked
whether the game starts, so content could be frozen that no human had ever
launched. Separately, the seed was blessed AFTER the proven build, so changing
the seed const meant a re-merge and a re-cut (it happened on 2026-07-30).

### The old order and the new one

```
 BEFORE (2026-07-29 .. 2026-10-25)
 +-------+   +--------+   +-------+   +--------+   +-------+   +-------+
 | 1     |-->| 2      |-->| 3     |-->| 4      |-->| 5     |-->| 6     |
 | POUR  |   | FREEZE |   | PACK  |   | PROVEN |   | SEED  |   | BOARD |
 +-------+   +--------+   +-------+   +--------+   +-------+   +-------+

 NOW (from 2026-10-26): decide, lock, prove, open
 +-------+   +-------+   +-------+   +----------+   +--------+   +-------+
 | 1     |-->| 2     |-->| 3     |-->| 4 FREEZE |-->| 5      |-->| 6     |
 | POUR  |   | PACK  |   | SEED  |   | = branch |   | PROVEN |   | BOARD |
 |       |   |       |   |       |   | cut + a  |   |        |   |       |
 |       |   |       |   |       |   | run      |   |        |   |       |
 |       |   |       |   |       |   | starts   |   |        |   |       |
 +-------+   +-------+   +-------+   +----------+   +--------+   +-------+
  \_________ decide ________/          lock          prove        open
```

What the new order buys:

1. **The seed is decided before anything is built.** A wrong seed const is a
   one-line PR, not a re-cut, and the release branch is cut with the blessed
   seed already in it.
2. **The freeze is the release-branch cut** (`RELEASING.md`): `main` keeps
   moving; `release/v0.X` takes only hotpatch-criteria cherry-picks.
3. **The freeze includes a boot check.** The clause *"...and the thing
   launches: a run exists, not a screen that resembles one"*, drafted in the
   old freeze sheet's PENDING VOTE box, is adopted. It runs after the
   class-cache pre-flight (`python3 tools/check_class_cache.py --repair`, per
   `CLAUDE.md` -- a stale cache produces the same "UI but no game" picture)
   and it must be a WINDOWED launch: #1023's suspected mechanism was a
   windowed-only `_ready()` abort that headless runs cannot see.

What it costs, recorded so nobody rediscovers it:

- **Checks that were no longer runnable at their new position moved** (rule 2
  above). From SEED BLESSING: "the seed is inside the cut" -> PROVEN BUILD
  (with a branch-level repeat at THE FREEZE); "tag pushed, release workflow
  green" and the named website-board attestation -> BOARD OPENS.
- **Proving runs now play the league seed.** A proving run submitted globally
  lands on the league board before it opens; the PROVEN BUILD sheet says to
  keep global submission off on the proving machine, and BOARD OPENS checks
  the board is empty before its own test run.

**Wanted later, not yet scheduled:** a playtest window for testers other than
Pip between the release-branch cut and the tag -- a release candidate friends
play for some days. Tracked in #1355.

---

## 7. Quick reference

```
+----------------------------+---------------------------------------------+
| I need to...               | Read / run                                  |
+----------------------------+---------------------------------------------+
| perform a gate             | docs/rituals/gate_<n>_*.md (read FROM it)   |
| know the current ladder    | cat ladder_version.txt                      |
| know the seed players post | grep -n FEATURED_SEED_OVERRIDE              |
|                            |   godot/autoload/game_config.gd             |
| know if a bump is owed     | python3 tools/check_ladder_bump.py --owed   |
| check version agreement    | python3 tools/sync_version.py --check       |
| run the fast gate          | python3 scripts/run_godot_tests.py --quick  |
|                            |   --ci-mode --min-tests 300                 |
| cut a release build        | python3 tools/build_release.py (never a raw |
|                            |   godot --export)                           |
| see a past gate record     | docs/rituals/records/                       |
+----------------------------+---------------------------------------------+
```
