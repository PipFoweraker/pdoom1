# P(Doom)1 developer glossary

Project-specific vocabulary, defined once so humans and LLM agents resolve the
same term the same way. These words are load-bearing: using the wrong mental
model for `epoch`, `fork`, or `re-cut` can scatter a public leaderboard league
across incompatible boards.

**Every entry is grounded in a repo source**, cited as `path:LINE`. Definitions
here are read out of the sources, not inferred. Terms that exist in
conversation but have no repo source are marked
`[ungrounded -- needs Pip ruling]` rather than guessed at.

**Future editors:** cite a source for every entry you add, or mark it
ungrounded. An honestly-empty entry beats a confabulated one. When a source
moves, fix the citation; a glossary with stale line numbers rots the same way
`decisions/README.md` did (see **DQ index** for the anti-rot pattern).

Related canonical docs: `docs/RELEASE_NOMENCLATURE.md` (wins on any clock /
counter / naming disagreement), `docs/ARCHITECTURE.md` (systems map),
`docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md` (the version split spec).

---

## Versioning and leaderboards

### build version (`version.txt`, `CURRENT_VERSION`)
The full semver string identifying the binary/pck; `version.txt` at the repo
root is the SSOT, stamped into `game_config.gd`, `project.godot`,
`export_presets.cfg` and `welcome.tscn` by `tools/sync_version.py`. It bumps
every release and every patch. It is the runtime const
`GameConfig.CURRENT_VERSION`, kept compiled-in (not a runtime file read)
because `version.txt` lives outside `res://`.

Why it bites: build version is NOT the board scope any more -- see **ladder
version**. Build version is the *provenance* answer ("which binary did the
player run"), used by the share line, bug report, and the replay artifact's
build tag.

Source: `godot/autoload/game_config.gd:138-146`,
`docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md:26-27,41-47`

### ladder version (`ladder_version.txt`, `LADDER_VERSION`, `L<n>`)
A separate, slow-moving integer -- the ruleset/epoch counter -- whose SSOT is
`ladder_version.txt` at the repo root, stamped into
`GameConfig.LADDER_VERSION` by `sync_version.py` exactly like the build
version. It bumps ONLY when gameplay/scoring/seed/RNG rules change. Rendered
as `"L<n>"` (e.g. `L3`) so it is unambiguous next to a `v0.13.1` build
string; `GameConfig.get_board_version()` returns `"L" + LADDER_VERSION`.

Why it bites: a cosmetic patch that bumps the ladder splits testers across
incompatible boards; a gameplay patch that does NOT bump the ladder puts
scores earned under different rules on the same board -- a lie about what the
scores mean. See **fork**, **epoch**, **board key**.

Source: `godot/autoload/game_config.gd:153-161,557-569`,
`docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md:138-153,180-197`,
`docs/RELEASE_NOMENCLATURE.md:41-51`

### epoch
One value of `ladder_version`. All scores sharing the same
`(seed, ladder_version)` are directly comparable; scores across different
ladder values are NOT (different rules produced them). Crossing an epoch
boundary is a one-way rotation -- scores never migrate forward, because that
would misrepresent the rules they were earned under. Operationally, each
monthly Theme is an epoch (see **Theme**).

Why it bites: treating "epoch" as a synonym for "release" is the classic
error -- a cosmetic patch release is a new build and the SAME epoch.

Source: `docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md:352-358`,
`docs/RELEASE_NOMENCLATURE.md:30-39`

### board key
The `(seed, ladder_version)` pair that scopes a leaderboard. Locally it is
the board filename `leaderboard_<seed>__<version>.json`; remotely it is the
`version` field/query param the PHP score API buckets on. ADR-0002 item #5 is
the deciding rule ("Boards are keyed by `(seed, game_version)`"), narrowed by
the version split so the version component is the ladder epoch, not the
build.

Why it bites: rebuilding the key from `CURRENT_VERSION` at any call site
re-couples the board to the build string and re-introduces the bug the split
fixed. Every board-key site must route through
`GameConfig.get_board_version()`.

Source: `godot/autoload/game_config.gd:557-569`,
`docs/game-design/decisions/ADR-0002-scoring-turns-survived.md:33-36`,
`docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md:59-99`,
`docs/RELEASE_NOMENCLATURE.md:50`

### fork (as in "forks the board")
A change that moves players onto a NEW board key, i.e. bumps the ladder. The
fork rule, stated as the only question that matters at ship time: *"Could two
identical runs, played the same way, produce a different score, trajectory, or
RNG stream across this change?"* YES -> it forks (bump minor + ladder); NO ->
it does not (bump patch only).

Why it bites: an unintended fork scatters testers across incompatible ladders
and empties the live board mid-league -- exactly what happened when EVERY
build bump fed the board key (a music-only patch forked every board). An
omitted fork is the mirror failure: incomparable scores sharing one board.
Not-breaking-the-ladder is a declared discipline, not a hard rule -- a
strictly-dominated change may ship as a patch by judgement, stated openly.

Source: `docs/RELEASE_NOMENCLATURE.md:52-63`,
`docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md:110-123,225-278`

### Theme / Big Milestone
A **Theme** is a named monthly release (first Friday) = a minor-version bump =
a forking epoch, e.g. `v0.14 "Per-tick & People"`. A **Big Milestone** is a
named multi-month arc (First Contact; Rivals & News) tracked as a GitHub
milestone; it is a container, not a release cadence, and completes when done
rather than on a date. Nothing is quarterly-locked -- quarterly planning was
retired 2026-07-25.

Source: `docs/RELEASE_NOMENCLATURE.md:30-35,64-73`,
`docs/ROADMAP.md:39-61`

### seed / seed schedule
A **seed** is not just an RNG seed: ADR-0005 defines `seed = RNG seed + event
schedule`. The schedule is an ordered list of authored *causes* (rival funding
wave, injected event id) that may touch sim INPUTS only -- never the doom
variable or any outcome directly ("author causes, never outcomes"). A fresh
weekly seed gives a new board on unchanged rules, so it does NOT fork. Pip is
a seed *curator*, not a wave author: candidate seeds are run headless through
`baseline_simulator.gd` and rejected if their doom trajectory falls outside a
playability envelope.

Why it bites: because the schedule is part of the seed, changing schedule
content changes what happens on a fixed seed -- that is a ladder bump (fork),
not a content refresh.

Source: `godot/scripts/core/seed_schedule.gd:2-14`,
`docs/game-design/decisions/ADR-0005-emergent-waves-seed-schedules.md`
(lines 18-53),
`docs/RELEASE_NOMENCLATURE.md:32`

### the featured / weekly seed
The default league seed the game presents. `GameConfig.FEATURED_SEED_OVERRIDE`
PINS it manually ("manual for now"); when empty, `get_weekly_seed()` derives
`weekly-<year>-w<week>` from the wall-clock date. Rotating the league today
means editing that const.

Source: `godot/autoload/game_config.gd:458-478`

---

## Build and release

### pack (noun)
Two distinct nouns share this word -- disambiguate before acting:

1. **The `.pck`** -- the Godot resource pack shipped next to `PDoom.exe`
   (~60MB), containing all GDScript, data and art. Changes every patch. See
   **pck**.
2. **The league / world-update pack** -- ADR-0016 content: a month's curated
   real-world events authored as ADR-0005 schedule entries, plus league notes.
   The playbook's [Gate 3: PACK BLESSED] is "the 0016 league pack is authored, schema-valid,
   and born clean of printed doom".

Source (1): `docs/game-design/DISTRIBUTION_AND_PATCHING.md:9-13,29-43`
Source (2): `docs/game-design/decisions/ADR-0016-league-metabolism.md:22-27`,
`docs/game-design/LEAGUE_WEEK_PLAYBOOK.md:61-67`

### pack (verb)
To author the month's league pack content (the Wednesday "FREEZE + pack"
beat), gated by [Gate 3: PACK BLESSED]. Note it does NOT mean "run the exporter" -- that is
**cut** / `build_release.py`.

Source: `docs/game-design/LEAGUE_WEEK_PLAYBOOK.md:22-23,61-67,99`

### freeze
The [Gate 2: THE FREEZE] stage gate (Wednesday PM): main freezes for mechanics. After the
freeze, only pack content, art, docs, and bugfixes labelled league-critical
may merge. `ladder_version.txt` is final for the league at this line.
Incantation: *"No new law crosses this line. What is merged is the month.
What is parked is the next."*

Why it bites: merging a mechanics PR past the freeze changes the ruleset the
league is about to open on, after the ladder value was declared final.

Source: `docs/game-design/LEAGUE_WEEK_PLAYBOOK.md:54-61`

### cut / the proven build
Producing the release artifact via `python tools/build_release.py` -- never a
raw `godot --export`. The tool nukes `godot/.godot` first, plants a
uniquely-named marker file, exports, and PROVES that marker is present in the
`.pck` before emitting; a missing marker exits non-zero and loud. This exists
because Godot's `exported/` cache can silently pack a STALE scene while
reporting success (~12 test cycles burned on v0.11.0). [Gate 4: PROVEN BUILD] pairs the proven
build with `sync_version.py --check` green and a human playtest of the built
artifact, not the editor.

Source: `tools/build_release.py:3-31`,
`docs/game-design/LEAGUE_WEEK_PLAYBOOK.md:69-77`

### re-cut
**Newly coined 2026-07-29 in conversation; no repo source yet.** Re-building
the release pack from scratch after ANY gameplay-affecting change, rather than
patching the existing pack.

Why it bites: two builds can honestly report the same ladder epoch while
playing differently -- and the ladder-version guard CANNOT catch that, because
both report the same `L` value truthfully. The guard checks that
`LADDER_VERSION` matches `ladder_version.txt`, not that the shipped bits match
the ruleset the epoch claims. Re-cutting is the only mechanical answer.

Source: `[ungrounded -- needs Pip ruling]`. The guard limitation it addresses
is grounded: `--check` catches file-to-const drift only
(`docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md:286-300`, which states
outright that "A pure `--check` cannot catch" a human forgetting the bump),
and the freshness proof is a build-time marker check, not a semantic one
(`tools/build_release.py:14-20`).

### pck
A Godot resource pack. `ProjectSettings.load_resource_pack("patch.pck")`
mounts a SECOND pck whose files OVERRIDE the base pck's, so a 3-file patch
becomes a few-KB pck. Roughly 95% of patches are pck-only; the ~94MB exe does
not move. Security caveat: mounting a downloaded pck executes its GDScript --
a remote-code-execution path by construction, so hash verification and a
trusted backend are mandatory before mounting anything downloaded.

Source: `docs/game-design/DISTRIBUTION_AND_PATCHING.md:29-60`

### the L0-L3 update ladder
The distribution options ladder, cheapest first. NOTE: this `L<n>` is a
DIFFERENT namespace from the ladder-version `L<n>` -- context disambiguates,
but do not read "L3" as an epoch here.

- **L0** raw zip + manual extract (the run-from-inside-zip trap).
- **L1** Inno Setup installer (ruled: adopt).
- **L2** in-game update NOTICE -- SHIPPED 2026-07 (#799);
  `godot/autoload/update_check.gd` GETs `pdoom1.com/data/version.json`,
  compares to `CURRENT_VERSION`, shows a dismissible banner. No auto-download.
- **L3** in-game auto pck-swap patcher -- UNBUILT, and per the Steam
  re-prioritization probably will not be built (Steam depots delta-patch
  natively).

Source: `docs/game-design/DISTRIBUTION_AND_PATCHING.md:62-83,176-183`

### hotpatch
A within-month patch-version bump that does NOT fork the ladder: cosmetic or
honesty fixes shipped any time (`0.14.0 -> 0.14.1`). The league week arms a
Saturday-morning hotpatch watch window.

Why it bites: "urgent" and "non-forking" are independent axes. A forking
change is not a hotpatch no matter how urgent -- issue #789 carrying both
`league:v0.13` and `ship:hotpatch-48h` was flagged as a contradiction to
resolve, not a valid combination.

Source: `docs/RELEASE_NOMENCLATURE.md:34,48`,
`docs/game-design/LEAGUE_WEEK_PLAYBOOK.md:25`,
`docs/game-design/TENSION_AUDIT_2026-07-23.md:333-336`

### `ship:` label tiers
Release-urgency labels on GitHub issues: `ship:tonight`,
`ship:hotpatch-48h`, `ship:next-release`. Unlabeled = backlog. They are
ORTHOGONAL to the `league:*` / `patch:*` tier labels, which describe what a
change touches; the audit's relabel list treats mixing the two axes as the
recurring mistake.

Source: `CLAUDE.md:84-86`,
`docs/game-design/TENSION_AUDIT_2026-07-23.md:333-359`

### stage gates
The league week's ceremony: six gates, each entry criteria -> mechanical
checks -> incantation. A gate is PASSED only when the Commissioner (Pip) says
its incantation with every line true. The Clerk may declare a gate READY,
never PASSED. Saying a line you have not verified is named the cardinal sin
of the ceremony.

Naming (ruled 2026-07-29, Pip): gates are written name-first with a 1-6
sequence number, in ASCII chrome, e.g. `[Gate 4: PROVEN BUILD]`. The playbook
still uses the older zero-indexed G0-G5 letters, so the mapping is:

| Written from 2026-07-29 | Legacy in the playbook |
|---|---|
| [Gate 1: LAST POUR] -- last mechanics merge enters review | G0 |
| [Gate 2: THE FREEZE] | G1 |
| [Gate 3: PACK BLESSED] | G2 |
| [Gate 4: PROVEN BUILD] | G3 |
| [Gate 5: SEED BLESSING] -- seed drawn, ladder stamped, board-key fork verified clean | G4 |
| [Gate 6: BOARD OPENS] | G5 |

Why it bites: the legacy scheme is zero-indexed, so a bare "Gate 1" is
ambiguous between the FIRST gate (G0 LAST POUR) and G1 (THE FREEZE). The
sequence numbers above are ceremony order, and the name is always carried
alongside so the number can never be the only disambiguator.

Three checks are explicitly NOT allowed to slip: [Gate 3: PACK BLESSED]'s
clean-of-printed-doom, [Gate 4: PROVEN BUILD]'s proven build, and
[Gate 5: SEED BLESSING]'s board-key check.

Source: `docs/game-design/LEAGUE_WEEK_PLAYBOOK.md:28-45,117-124`;
naming ruling is conversational (2026-07-29), not yet reflected in the playbook

---

## Testing

### fast gate
The blocking test tier you run for any scoped change:
`python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300`
(`godot/tests/unit`, non-recursive). The runner does the `--import` pass
itself. In CI it is the `unit-tests` job, ~36 files, min-test floor 300,
blocking.

Source: `CLAUDE.md:19-22`, `docs/ARCHITECTURE.md:274-277`

### simulation tier
The slow suite (`--simulation`, `godot/tests/unit/simulation`, ~3 min):
full-run / replay / determinism. **Non-blocking** in CI
(`continue-on-error`, min 80). Run it only when you touched
simulation/economy/replay code; do NOT wait on it for a scoped change.

Why it bites: conflating the tiers either wastes three minutes per scoped
change, or ships an RNG-stream change unverified. ADR-0006-style replay
determinism is exactly the property that decides whether a change forks the
ladder -- the spec proposes a golden-replay test here as the strongest
backstop against a forgotten ladder bump.

Source: `CLAUDE.md:23-26`, `docs/ARCHITECTURE.md:274-279`,
`docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md:313-319`

### hollow test / the honest gate
A "hollow" test passes without exercising the thing it claims to protect.
Two 2026-07-17 failures named it: CI reporting GREEN while running ZERO tests
(a cold Godot class cache made GUT `quit(0)` before parsing anything), and a
one-line parse error in `main_ui.gd` that broke the game while 436 unit tests
passed (the fast tier never loads UI scripts). Fixed by #640: the runner
IGNORES GUT's exit code, parses the JUnit XML, and hard-fails on zero tests,
a below-floor count, any failure, or a manifest cross-check miss. CI green
can be trusted again.

Source: `docs/game-design/decisions/ADR-0017-anti-hollow-test-strategy.md:7-32`,
`docs/ARCHITECTURE.md:267-285`, `CLAUDE.md:126-131`

### fresh worktree gotcha
In a cold checkout, `godot/.godot/global_script_class_cache` is absent, so
GUT/headless `quit(0)`s before running anything and emits misleading
`class_name` parse errors. Run `godot --headless --path godot --import`
first; `run_godot_tests.py` does this for you.

Source: `docs/ARCHITECTURE.md:259-262`, `CLAUDE.md:23-28`

---

## Player-facing vocabulary

### Attention (NOT "Action Points" / "AP")
The founder's ONLY currency: a grant of roughly N decisions per PLAN MONTH,
typed into PLANNING and OPERATING hours. Staff never add to it -- they work
their own per-person lanes. Unspent Attention evaporates at month end (no
banking).

**"Action Points" / "AP" is dead vocabulary.** The per-turn AP pool was killed
as a design concept on 2026-07-27 (ADR-0011 amendment (a): *"AP confirmed dead
(RIP AP, dead 1h03m. Long live A!)"*) and deleted in code by the T2 migration.
`game_state.gd` states it in terms: *"There is no `action_points` field, no
per-turn grant, no AP in any cost dict."* Any player-facing "AP" string is a
defect, not a mechanic -- and a stale AP string is worse than a stale word,
because #1073's worst case taught a FORMULA ("Base 3 + 0.5 per staff") for a
mechanic that does not exist.

Guarded by `godot/tests/unit/test_no_stale_ap_vocabulary.gd`, which asserts the
ABSENCE of the vocabulary across scenes/data/UI scripts. #1050 tried to close
this by enumerating nine strings and missed at least six; enumeration is the
failure mode.

Source: `docs/game-design/decisions/ADR-0011-*.md` (Decision point 1,
Amendment 2026-07-27 (a)), `godot/scripts/core/game_state.gd:76-80`

### number format policy
One convention for every player-facing number: money in whole grouped dollars
(never cents), resource scalars in whole grouped units, percentages to one
decimal (the deliberate exception -- p(Doom)'s fraction is load-bearing), and
deltas always signed. **A raw float must never reach the player.** All of it
lives in `GameConfig`; nothing else may format a number for a player.

Source: `docs/NUMBER_FORMATS.md`, `godot/autoload/game_config.gd` (the
"NUMBER FORMAT POLICY" block), `godot/tests/unit/test_number_format_policy.gd`

---

## Process and docs

### ADR
Architecture Decision Record -- one file per decision in
`docs/game-design/decisions/`, currently ADR-0001 through ADR-0018. Fixed
sections: Status / Date / Session, Context, Decision, Beacons served or
violated, Interaction contract (must read+write >= 2 existing systems),
Rejected alternatives, Consequences.

Why it bites: `decisions/README.md` is STALE (it lists only ADR-0001 as
PROPOSED). Trust the ADR files themselves, never the index.

Source: `docs/game-design/decisions/ADR-TEMPLATE.md:1-22`,
`docs/ARCHITECTURE.md:31-33`, `CLAUDE.md:100-102`

### DQ / DQ index
A **DQ** is a numbered design question in
`docs/game-design/WORKSHOP_2_BACKLOG.md` (the SSOT). `DQ_INDEX.md` is a
GENERATED status table -- never hand-edit it. Regenerate with
`python scripts/generate_dq_index.py`; a pre-commit `--check` blocks commits
that change the backlog without regenerating.

This is the project's **anti-rot pattern**: indexes are derived from source
files, not hand-maintained. The generator's own docstring names the stale
`decisions/README.md` as the failure mode it avoids.

Source: `scripts/generate_dq_index.py:1-20`,
`docs/game-design/DQ_INDEX.md:1-6`, `CLAUDE.md:107-114`

### W-block (W0, W1, ... ) / workshop numbering
Two different numbers, routinely confused:

- **WS-<n> / Workshop <n>** -- a whole design workshop session (WS-1, workshop
  #2, WS-3). Multi-day, produces ADRs. Sub-sessions get letters: the runsheet
  runs `W-3a` Monday and `W-3b` Wednesday of Workshop 3.
- **W<n> block** -- a TIMEBOXED AGENDA BLOCK inside one workshop day. On
  Wednesday 2026-07-29: `W0` = review Tuesday's builds (merge/park per PR),
  `W1` = colour architecture, `W2` = decorating math, `W3` = league/content
  cadence + Friday league prep, `W4` = next-epoch planning. Each block has
  named inputs and a named output artifact.

Why it bites: `W0` is not "workshop zero" -- it is the first block of the
day, the PR review block, and it is on the not-allowed-to-slip list because
unreviewed builds rot fastest.

Source: `docs/game-design/RUNSHEET_2026-07-27_to_29.md:1,204-241,247-263`

### the runsheet vs the playbook
The **playbook** (`LEAGUE_WEEK_PLAYBOOK.md`) holds the evergreen ceremony
(roles, gates, incantations). The **runsheet**
(`RUNSHEET_2026-07-27_to_29.md`) is SSOT for volatile dated detail. Anti-rot
rule: the playbook never copies what the runsheet owns, it links.

Source: `docs/game-design/LEAGUE_WEEK_PLAYBOOK.md:5-9`

### Commissioner / Clerk / the Bureau
League-week roles. **Commissioner** (Pip): the only one who blesses -- rules
on packs, waves the doom wand, speaks the seed. **Clerk of the League**
(Fable): prepares packs, tables, verification evidence, gate paperwork; may
declare a gate READY, never PASSED. **The Bureau** (agent lanes): builds,
never blesses, pushes per step so nothing is lost by stopping a lane.

Source: `docs/game-design/LEAGUE_WEEK_PLAYBOOK.md:28-38`

### park / in-flight
A lane not green by the day's hard stop PARKS: it becomes the next block's
review input, not evening work. A parked lane at a hard stop is "an agenda
line, not a failure". Anything not in review by [Gate 1: LAST POUR] does not ship this
league,
by construction.

Source: `docs/game-design/LEAGUE_WEEK_PLAYBOOK.md:26,47-52,119`,
`docs/game-design/RUNSHEET_2026-07-27_to_29.md:150-151,199`

### printed doom (ADR-0015 / "born clean")
No action or event may write doom directly -- they write intermediaries
(lab frontier capability, safety absorption) and doom is recomputed from
streams. Pack content is checked "born clean of printed doom" at [Gate 3: PACK BLESSED]
by grep;
that check is on the not-allowed-to-slip list.

Source: `docs/ARCHITECTURE.md:85-102`,
`docs/game-design/LEAGUE_WEEK_PLAYBOOK.md:61-67,120-124`

---

## Observed inconsistency (flagged, not ruled)

`ladder_version.txt` currently reads `3` and
`GameConfig.LADDER_VERSION` is `"3"`, so `get_board_version()` returns `L3`,
while `version.txt` reads `0.13.1`. But `ROADMAP.md`'s Monthly Themes table
maps `v0.13 -> L2` and `v0.14 (Aug 7) -> L3`, and the comment block above
`LADDER_VERSION` still says "Epoch L1 == the current ruleset" and predicts a
bump "to 2 at the v0.13 epoch cut". At least the comment is stale; whether the
live `L3` on a `0.13.1` build is intended (an early mid-month fork) or a drift
is a Pip ruling, not a glossary call.

Source: `ladder_version.txt:1`, `version.txt:1`,
`godot/autoload/game_config.gd:153-161`, `docs/ROADMAP.md:44-48`
