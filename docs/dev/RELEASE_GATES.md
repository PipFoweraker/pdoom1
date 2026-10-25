# The release / league gates -- a plain-language guide

**Who this is for:** anyone (including Pip, back after months away) who needs to
know what the six league-week gates are, why they exist, and what is still
undecided about them. It explains; it does not legislate.

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

Gates are written name-first with their number (`[Gate 4: PROVEN BUILD]`), per
Pip's 2026-07-29 ruling. The old playbook numbered them G0-G5; Gate N = G(N-1).

```
 WEDNESDAY                  WED PM -> THU AM            THURSDAY (re-cut Fri)
+----------------------+   +----------------------+   +----------------------+
| [Gate 1] LAST POUR   |   | [Gate 2] THE FREEZE  |   | [Gate 3] PACK BLESSED|
| ~1200                |-->| Wed PM               |-->| Wed EOD / Thu AM     |
| last mechanics PR    |   | main frozen at a SHA;|   | league content pack  |
| enters review; every |   | ladder value final;  |   | read + clean of      |
| open PR is MERGE or  |   | tests counted        |   | printed doom -- or   |
| PARK                 |   |                      |   | "there is no pack"   |
+----------------------+   +----------------------+   +----------------------+
                                                                  |
          +-------------------------------------------------------+
          v
+----------------------+   +----------------------+   +----------------------+
| [Gate 4] PROVEN BUILD|   | [Gate 5] SEED        |   | [Gate 6] BOARD OPENS |
| Thu (re-cut Fri)     |-->| BLESSING  Fri ~1645  |-->| Fri ~1700            |
| release artifact     |   | seed spoken; the     |   | downloads answer;    |
| built, proven fresh, |   | client's seed const  |   | feed names this      |
| PLAYED by a human on |   | matches it; board    |   | build; one real run  |
| a clean machine      |   | key = (seed, L<N>)   |   | reaches the board    |
+----------------------+   +----------------------+   +----------------------+
                                                                  |
                                                                  v
                                                       Sat AM: hotpatch watch
                                                       window; retro slot
```

The weekday labels come from the v0 playbook, written for a weekly league.
In practice the gates have been run at RELEASE time rather than on a fixed
Wednesday-Friday: the v0.14.3 record shows Gates 5 and 6 performed on Monday
2026-08-24. Read the days as an ordering, not a calendar.

## 4. Gate by gate: what it checks, who, and what it protects against

| Gate | What it checks (summary; commands live in the sheet) | Who | Protects against |
|---|---|---|---|
| **1 LAST POUR** | Open-PR list snapshotted to a timestamped file; every PR marked MERGE or PARK; none unaccounted; nothing parked is labelled league-critical | Clerk prepares table, Commissioner rules each row | Work sneaking into the month without a decision; "what was open at the pour?" becoming a memory instead of a fact |
| **2 THE FREEZE** | Frozen commit SHA recorded; `sync_version.py --check` exits 0; fast gate green above the 300-test floor; `ladder_version.txt` declared final; `check_ladder_bump.py` findings read | Commissioner only | Rules changing after the league's ruleset is fixed; version/ladder drift forking the board key; a "green" CI that ran zero tests (#640) |
| **3 PACK BLESSED** | Branch A (no pack): prove the schedule is structurally empty. Branch B (pack): loader validates, zero printed-doom deltas, ladder bumped, every card read by Pip | Commissioner reads every card | Unread or doom-printing content shipping; a gate being silently skipped when its subject does not exist |
| **4 PROVEN BUILD** | `build_release.py` proves its freshness marker is in the `.pck`; version agrees; changelog heading; cut number + base SHA recorded; machine reset to a clean player state; **a human plays the built artifact** | Commissioner plays; Bureau must not touch the working tree | Shipping "the thing we meant" instead of "the thing we ship": stale export caches, presentation bugs no headless test can see (#1039 found four), a playtest of the wrong config (the Crisis-Mode scare) |
| **5 SEED BLESSING** | Ladder value read aloud; `FEATURED_SEED_OVERRIDE` matches the seed spoken AND is inside the cut; board key derives from `get_board_version()`; no non-Standard config can reach the board; website board attested by a named person | Commissioner speaks; website state is someone else's attestation | Blessed seed and posted seed diverging; the key re-coupling to the build string; Easy/Sandbox runs landing on the ranked board (#1058, #1060) |
| **6 BOARD OPENS** | Every advertised download URL answers 200; release feed's "latest" is this release; release body teaches no dead keybind; one real run travels client -> backend -> board; announcement posted | Commissioner | A league whose download 404s; a feed calling an old build "latest" (#1008); an empty board that is really a broken chain |

Three rules from `docs/rituals/README.md` explain most of the design:

```
+--------------------------------------------------------------------------+
| 1. Every clause maps to a check.   No check -> cut it, or label it as a   |
|                                    stated judgement.                      |
| 2. A check must be runnable at the moment the line is spoken.             |
|    (That is why release-URL checking moved from Gate 4 to Gate 6: the    |
|    tag does not exist yet at Gate 4.)                                     |
| 3. A FALSE line has a named next step. Each sheet has a "When a line is  |
|    FALSE" section.                                                        |
+--------------------------------------------------------------------------+
```

## 5. The re-cut loop (the part that surprises people)

A build is not patched; it is re-cut. Anything league-critical that merges after
the freeze kills every earlier cut and sends you back through Gate 4 -- including
the human playtest, at least over the surface the change touched.

```
          +---------------------------+
          | [Gate 2] FREEZE at SHA-1  |
          +-------------+-------------+
                        |
                        v
          +---------------------------+
   +----->| [Gate 4] cut k from SHA-n |
   |      | build, prove, PLAY        |
   |      +-------------+-------------+
   |                    |
   |          playtest finds a bug?
   |            /               \
   |         yes                 no
   |          |                   |
   |          v                   v
   |   league-critical?     +-------------------+
   |     /        \         | [Gate 5] SEED     |
   |   yes         no ----->| BLESSING on cut k |
   |    |    (file it as    +-------------------+
   |    |    hotpatch-48h /
   |    |    next-release, continue)
   |    v
   |  fix merges past the freeze (legal);
   |  record new SHA-n; cut k+1 kills cut k
   +----+
```

Why so strict: two builds reporting the same ladder epoch while playing
differently is a lie nothing downstream can detect (#1039).

## 6. The open question: issue #1025 -- should the freeze come before a launch?

**Status: PENDING a decision by Pip.** Nothing on this page changes the gate
order. Per `docs/rituals/README.md`, gate wording, checks and ordering change
only by a Council of Elders vote, recorded under #1025.

### What went wrong

```
 2026-07-29                                                  2026-07-30
 --------------------------------------------------------------------------->
      ~22:13                 22:28                           Thursday
        |                      |                                 |
  a launch shows a full   [Gate 2] FREEZE                  [Gate 4] PROVEN
  UI with NO game state   declared. Every                  BUILD: the first
  (#1023, the "boot       check passed --                  time anyone is
  ghost")                 because no check                 REQUIRED to have
                          asks "does it run?"              launched the thing
```

The freeze checks the ladder, the version and the tests. None of those ask
whether the game starts. So content can be frozen that no human has ever
launched. Nothing said at the freeze was untrue -- the gate did its job; the
question is whether its job is the right one.

It is mild, not urgent: Gate 4 still catches a broken build before any board
opens, and league-critical fixes are explicitly allowed past the freeze. The cost
is rework and a freeze spoken over a corpse, not a wrong league.

### The four options from the issue

```
 OPTION 1: LEAVE IT
 +--------+   +--------+   +--------+   +----------------+   +--------+   +--------+
 | Gate 1 |-->| Gate 2 |-->| Gate 3 |-->| Gate 4 (build  |-->| Gate 5 |-->| Gate 6 |
 |        |   | (law)  |   |        |   | + play)        |   |        |   |        |
 +--------+   +--------+   +--------+   +----------------+   +--------+   +--------+

 OPTION 2: ADD A SMOKE CHECK TO GATE 2  (one clause, run from source, no build)
 +--------+   +----------------+   +--------+   +--------+   +--------+   +--------+
 | Gate 1 |-->| Gate 2 (law +  |-->| Gate 3 |-->| Gate 4 |-->| Gate 5 |-->| Gate 6 |
 |        |   | "a run exists")|   |        |   |        |   |        |   |        |
 +--------+   +----------------+   +--------+   +--------+   +--------+   +--------+

 OPTION 3: REORDER  (proven build before the freeze)
 +--------+   +----------------+   +--------+   +--------+   +--------+   +--------+
 | Gate 1 |-->| PROVEN BUILD   |-->| FREEZE |-->| Gate 3 |-->| Gate 5 |-->| Gate 6 |
 |        |   | (moved earlier)|   |        |   |        |   |        |   |        |
 +--------+   +----------------+   +--------+   +--------+   +--------+   +--------+

 OPTION 4: SPLIT GATE 4  (cheap boots-check early, full playtest where it is)
 +--------+   +--------+   +-------+   +--------+   +----------------+   +--------+
 | Gate 1 |-->| Gate 2 |-->| BOOTS |-->| Gate 3 |-->| Gate 4 (full   |-->| 5 / 6  |
 |        |   |        |   | check |   |        |   | build + play)  |   |        |
 +--------+   +--------+   +-------+   +--------+   +----------------+   +--------+
```

| Option | Cost | Benefit | Risk |
|---|---|---|---|
| 1. Leave it | Zero | Keeps Gate 2 purely about law | A freeze can keep being spoken over a build that does not start |
| 2. Smoke check in Gate 2 | One clause, a few minutes: launch from source, start a run, see turn 1 live | Catches the #1023 class before the freeze; no build day needed | The check must be worded tightly or it passes on a corpse (see below) |
| 3. Reorder | Build work moves earlier, likely onto the day the playbook keeps clear | Cleanest in principle | Every post-freeze league-critical fix re-cuts anyway, so the early build is often wasted |
| 4. Split Gate 4 | Adds a seventh checkpoint, disturbs the numbering ruled on 2026-07-29 | Same catch as option 2 | More ceremony for the same check; renumbering confuses records and sheets |

### Recommendation (for Pip to accept or reject)

**Option 2.** It is the smallest change that removes the specific surprise, it
needs no build, and options 2 and 4 put the *same* check at the *same* moment --
option 4 just pays for it with a new gate and a renumbering. Option 3 buys little,
because the re-cut loop in section 5 means a build made before the freeze is
routinely thrown away.

If option 2 carries, the candidate clause is already drafted in
`gate_2_the_freeze.md` (PENDING VOTE box). Two details matter:

1. **The wording.** *"...and the thing launches: a run exists, not a screen that
   resembles one."* `main.tscn` once shipped placeholder text (`Phase: Not
   Started`, `Turn 1`) that made a dead UI and a live game look identical, so
   "the game looks fine" would have passed on the corpse.
2. **Run the class-cache pre-flight first** (`python3 tools/check_class_cache.py
   --repair`, then `godot --path godot`), per `CLAUDE.md`. A stale class cache in
   the checkout produces exactly the same "UI but no game" picture (2026-08-13);
   without the pre-flight, the smoke check can fail for a reason that has nothing
   to do with what is being frozen. And it must be a windowed launch: #1023's
   suspected mechanism was a windowed-only `_ready()` abort that headless runs
   cannot see.

**One thing to weigh alongside it.** On 2026-10-26 Pip ruled that the
release-branch model in `RELEASING.md` is adopted for real (`release/v0.X` per
epoch, tags only from release branches); guards for it are being built separately
under #1269. Under that model the natural "freeze" is the release-branch cut. That
does not change the recommendation -- the smoke check would simply run on the
release branch head -- but the Council may want to decide #1025 and the
freeze-equals-branch-cut question together, so the Gate 2 sheet is amended once.

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
