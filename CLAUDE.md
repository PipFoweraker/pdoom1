# CLAUDE.md -- P(Doom)1 agent cheat-sheet

Operational notes for Claude/LLM agents. Keep it short; update in place when a
convention changes. For the systems map read **`docs/ARCHITECTURE.md` FIRST**.

## What this is
Turn-based AI-safety strategy game. **Godot 4.5.1, pure GDScript** (no Python
runtime -- the old Python bridge is gone). Python exists only for CI/tooling in
`scripts/` and `tools/`. Windows dev machine; CI is Ubuntu.

## Run the game
- **`make run`, not a bare `godot --path godot`.** Same launch, plus the
  stale-class-cache pre-flight (~30ms; see the Tests section). The bare command
  is what was typed on 2026-08-13 and it launched a silently broken build in
  front of a first-time playtester. On Pip's machine Godot is
  `C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe`.

## Tests -- two tiers, don't conflate them
- **Fast gate (this is what you run for scoped changes):**
  `python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300`
  (`tests/unit`, non-recursive). The runner does the `--import` pass itself.
- **Slow simulation tier:** `--simulation` (`tests/unit/simulation`, full-run /
  replay / determinism). **Non-blocking** in CI -- do NOT wait on it for a
  scoped change. Run it only when you touched simulation/economy/replay code.
  Budget **~7-10 min**: 460-550s on CI, and 412-619s measured locally on
  Windows across 5 runs (#1181). It is NOT an hour-long tier; if it behaves
  like one, read the next bullet.
- **If the sim tier ever crawls locally, suspect stdout, not the tests.** The
  tier emits ~4-5M `print()` lines, and Godot's per-line write cost depends
  wildly on what stdout is attached to -- 200k prints measured at 2.4s through
  a native pipe, 432s through a Git Bash `> file` redirect, ~2900s through
  `| cat`. The runner now owns the pipe itself, so run it directly; do NOT wrap
  it in shell redirection you can avoid (#1181).
- **Three outcomes, not two (#1181).** The runner exits `0` = measured pass,
  `1` = measured failure, `2` = **DID NOT COMPLETE**. A timeout prints
  `DID NOT COMPLETE ... NO RESULT` with counts as `-`; it NEVER prints a test
  count, because none exists. If you see exit 2, you have no measurement --
  do not report a suite result from that run. Cap it yourself with
  `--timeout SECONDS` (`0` = none) or `PDOOM1_TEST_TIMEOUT`; defaults are 900s
  in CI and, locally, 2700s for `--simulation` / 900s elsewhere. `[PROGRESS]`
  heartbeats every 30s tell slow from hung without opening Task Manager.
- **Fresh worktree gotcha:** GUT quits(0) before running anything if the class
  cache is cold. The runner's import pass fixes this; if you invoke Godot/GUT
  directly, run `godot --headless --path godot --import` first. Running headless
  Godot also floods stderr with SCRIPT ERROR class-cache lines on the first pass --
  expected noise, not a real failure.
- **STALE cache is the worse half of that trap (2026-08-13, cost a playtest).**
  Cold = absent, and it fails loudly. **Stale = present, plausible, and wrong
  about exactly the file someone just added.** `godot/.godot/` is generated,
  gitignored and PER-CHECKOUT, so a worktree that authors a new `class_name`
  builds a correct cache and passes 1313 tests while the shared checkout, which
  only pulled, keeps a cache that predates the file. Every dependent script then
  hits `Parse Error: Identifier "X" not declared`. **The game still launches** --
  background art, doom readout, phase stuck on "starting up", no action icons,
  no upgrades, no commit-month, no music. It reads as "still loading".
  **CI is structurally blind to this** (it always clones fresh).
  Guard: `python tools/check_class_cache.py [--repair]`, ~30ms, no Godot launch;
  `make run` and `make lint` now depend on it. Note `godot --headless --quit`
  exits **0** through the whole cascade, so "it did not crash" proves nothing.
- `make test` = fast gate; `make run` = game.

## `.import` / `.uid` files -- the staging trap
- Both are **tracked on purpose** (Godot 4 convention: `.import` = import
  metadata, `.uid` = stable resource IDs). `godot/.godot/` and `godot/.import/`
  are correctly gitignored; the per-asset `*.import` / `*.uid` files are not.
- Running `--import` **rewrites/touches ~1200 `.import` files** and may emit new
  `.uid` files. **Do NOT stage that churn.** Never `git add -A` / `git add .`.
  Stage only the files you changed (`git add <path>`), or discard the churn with
  `git checkout -- godot/` before committing.

## Commit hooks & line endings
- Pre-commit runs `mixed-line-ending --fix=lf`, `enforce-standards` (ASCII-only,
  scans the whole tree -- slowish), black/isort/ruff (Python only).
- **`.gitattributes` now forces `eol=lf`** repo-wide, so the old CRLF<->LF fight
  (every doc commit failing once on the line-ending hook under
  `core.autocrlf=true`) is fixed. If a NEW file was authored with CRLF the hook
  still rewrites it once -- re-`git add` and re-commit is normal for that one file.
- **ASCII-only (hard rule, issue #744):** no non-ASCII chars in
  `.py/.md/.json/.yaml/.txt/.cfg/.sh` (no smart quotes, em-dashes as `--`,
  arrows as `->`, ellipsis as `...`). **Emoji are NEVER allowed anywhere** --
  not in Godot source, not in player-facing UI strings, not in docs. The house
  style is ASCII-flavoured chrome: `[M]`, `>>`, `[ESC] close`, `[OK]`, `[!]`.
- **Blocking no-emoji gate:** `scripts/check_no_emoji.py` (pre-commit hook
  `no-emoji`) fails the commit if `godot/**/*.gd` (non-addon) or
  `godot/data/**/*.json` contain ANY codepoint above U+007F, or if
  `godot/**/*.tscn` contain emoji. This is BLOCKING (the older
  `enforce-standards` Unicode check was non-blocking and let a coffee emoji
  ship). A few menu `.tscn` files are temporarily excluded pending the theme
  lane (issue #743); remove those exclusions when #743 lands.
- **Agents: commit in the FOREGROUND and make zero tool calls while hooks
  run.** The session harness rewrites `.claude/settings.local.json` on tool
  activity; pre-commit has that file stashed during the run, sees a tracked
  file change mid-hook, reports "Stashed changes conflicted with hook
  auto-fixes... Rolling back", and aborts -- and the rollback also DISCARDS
  any working-tree edits made during the run. Background commits + parallel
  work = repeated mystery failures (cost 4 attempts on 2026-07-19).

## Talking to Pip
- **ALWAYS give the ABSOLUTE path when he has to open something himself** -- an
  HTML tool, a built `.exe`, a generated report, a launch command. Full
  `G:\Documents\Organising_Life\Code\...` every time, even if you named it three
  messages ago, even if it is "obvious" from the repo root. He should never have
  to scroll back or keep a bookmark. Standing request 2026-08-04, in force at
  least until the tooling settles. Repeat the path in the SAME message as the
  instruction to open it, not in a separate one.
- **Compose file content with the file-writing tools, NOT shell heredocs.**
  Ruled in `coordination#9`/`#10` and adopted here. A heredoc silently compiled a
  `\b` in a non-raw Python string to a literal BACKSPACE, so a PII residue check
  reported clean while ten records still carried email addresses -- invisible in
  terminal output, and below U+007F so every ASCII gate passed it. Same class hit
  this repo repeatedly (mangled `\d`/`\s`/`\u` escapes, `gh issue create` bodies
  dying on quoting). Write the file, then act on it.

## Godot writes to Pip's REAL player profile -- isolate it (2026-08-08, cost a board)
- **Every `godot --headless` run on this machine writes into
  `C:/Users/Pip/AppData/Roaming/Godot/app_userdata/P(Doom)/`.** The user data dir
  derives from `config/name` in `project.godot`, NOT from the worktree path, so
  all worktrees share ONE profile. `scripts/run_godot_tests.py` inherits the
  parent `APPDATA`.
- **What it cost:** a test run wrote **1,330 files** into that profile,
  **destroyed the 50-entry 2026-07-31 league board** (recovered from a backup),
  mutated `config.cfg`/`keybinds.cfg`/`theme.cfg`, and injected 23 synthetic rows
  into the LIVE `(weekly-2026-w32, L4)` board during a release playtest -- which
  then corrupted the evidence being used to diagnose a separate ship blocker.
  Filed as **#1070 on 2026-07-31 and left open for seven days** before it went off.
- **Do this, every Godot invocation:**
  `APPDATA=C:/Users/Pip/AppData/Local/Temp/claude/godot-iso-<lane> godot --headless ...`
  (PowerShell: set `$env:APPDATA` first.) **`XDG_DATA_HOME` does NOT work on
  Windows** -- proven, no effect. Verify by printing `OS.get_user_data_dir()` once
  and confirming it is not under `AppData/Roaming`.
- **Consequence nobody expects:** an isolated `APPDATA` has no Godot **export
  templates** (`%APPDATA%/Godot/export_templates/`), so `build_release.py` dies
  with a bare `exited 1`. Copy the templates into the sandbox, or build unisolated
  (builds do not write boards).
- Do NOT set `use_custom_user_dir` in `project.godot` -- that ships to players and
  would move every real player's save directory.
- **This rule is WINDOWS-SPECIFIC. On Linux it is backwards:** `APPDATA` means
  nothing and `XDG_DATA_HOME` is the lever that works. An agent following the
  paragraph above on the Debian laptop runs UNISOLATED. Linux incantation and
  its first-run confirmation step: `docs/LAPTOP_DEBIAN_SETUP.md` section 4.

## Relay only what you verified (2026-08-06..09, measured)
- A claim audit over one cycle's output found **6 of 68 headline claims wrong
  (8.8%)** -- two already merged, one already propagated to two other repos
  (`docs/CLAIM_AUDIT_2026-08-06.md`). Every one was an assertion made from a
  summary, a memory, or another agent's report rather than from a source.
- **Adopted rule:** a claim in a title, summary line, table cell or bolded
  sentence must be reducible to a command another party can run, or it moves into
  the body with its hedge. Two amendments learned since: **a runnable command is
  not a run command** (re-run it against the tree that merges), and **a published
  command must be shown capable of returning the other answer.**
- **The specific trap:** relaying a sibling agent's characterisation. A lane was
  told to adopt two things from a rival PR "because they were better"; both were
  **backwards** when checked against the code. Read the diff, not the description.

## Agent gotchas (hard-won 2026-07-20..22)
- **Pushes hang on Git Credential Manager** (interactive prompt, no GUI):
  prefix `GIT_TERMINAL_PROMPT=0` on `git push` -- pushes instantly via gh's
  helper.
- **enforce-standards whole-tree churn is FIXED (#773, PR #849).** The
  pre-commit CHECK runs `enforce_standards.py --incremental` on only the
  files pre-commit passes (read-only, changed-files-only, since a274a09d),
  and `intelligent_ascii_converter.py` is now report-only DRY RUN by default
  -- it rewrites files ONLY with an explicit `--apply` (00adece3). A bare or
  accidental run no longer sprays transliterated churn across the tree. Still
  NEVER `git add -A` (the `.import`/`.uid` staging trap remains); if a worktree
  ever looks mass-modified, suspect that, not enforce-standards.
- **Squash-merge does NOT fire closes-keywords here** -- after merging,
  verify the linked issues closed; close stale ones manually.
- **Verify your Edit paths land in YOUR worktree** -- three lanes in one
  week initially edited the wrong checkout. Absolute paths from prompts go
  stale after worktree switches.
- **Art over 1MB never goes in git** (no --no-verify, no cap raises):
  docs/art/ART_MASTERS_POLICY.md. Masters staging: G:/tmp/pdoom1-art-masters/.
- **Release tiers**: issues carry ship:tonight / ship:hotpatch-48h /
  ship:next-release labels; unlabeled = backlog. Monthly release train
  (docs/ROADMAP.md); release-branch model in issue #775.
- **Pip visual passes**: make a preview worktree at the branch, run
  `godot --headless --path godot --import` (background, minutes), then give
  him the launch command. Never repurpose his main checkout.

## Git workflow
- Branch from **freshly-fetched** `origin/main`, not a stale local ref:
  `git fetch origin main && git checkout -b <branch> origin/main`.
- **Never stage `.claude/settings.local.json`** (always shows modified; it's local).
- Merge to main via admin-merge (Pip reviews first for agent PRs). PR body ends
  with the Claude Code footer; commit trailer `Co-Authored-By: Claude ...`.

## Where things live
- `docs/ARCHITECTURE.md` -- systems->code->ADR map. **READ FIRST.**
- `docs/game-design/` -- `DESIGN_PHILOSOPHY.md` (the "why"), `decisions/`
  (ADR-0001...0016 -- trust the files, the `decisions/README.md` index is stale),
  `WORKSHOP_2_BACKLOG.md`, `BUILD_BRIEF_*` build briefs.
- `docs/ROADMAP.md` -- thin roadmap SSOT: GitHub milestones are the live "Now";
  quarterly pins to v0.15; league/content cadence is MONTHLY (ruled 2026-07-21).
  Keep it thin -- link volatile things, never copy them.
- `docs/game-design/DQ_INDEX.md` -- **GENERATED, never hand-edit.** Regenerate
  with `python scripts/generate_dq_index.py` after touching
  `WORKSHOP_2_BACKLOG.md` (pre-commit `--check` blocks stale commits). This is
  the anti-rot pattern: indexes are generated from source files, not
  hand-maintained (the stale `decisions/README.md` is the failure mode).
- `docs/calendar/` -- the commitment calendar. **Every gate in this repo fires on
  a COMMIT; this is the only thing that fires on a DATE.** Writing a dated promise
  ANYWHERE (doc, issue body, `.gd` comment) means writing one line:
  `COMMITMENT: <YYYY-MM-DD> -- <what> -- owner: <who> -- kind: <kind>`. The
  convention, the kinds and their reminder lead times are argued in
  `docs/calendar/COMMITMENTS.md`; `.ics` + index are GENERATED by
  `python scripts/generate_commitment_calendar.py` (pre-commit `--check` blocks
  stale commits; `--refresh-github` is the only networked path). A future date
  with no declaration is reported as `UNPARSED`, never dropped.
- `docs/rulings/` -- **where a decision goes so it stops evaporating.** Same shape
  as the calendar above, for rulings instead of dates. Pip rules constantly and
  the same questions recur "in similar flavours"; 190+ rulings were already
  scattered through this tree as prose before anything gathered them. Writing a
  ruling ANYWHERE (docstring, `.gd` comment, doc, issue) means one line:
  `RULING: <YYYY-MM-DD> -- <the ruling> -- flavour: <slug>` (optional
  ` -- mechanism: <what re-asks it>`, ` -- supersedes: <id>`). Prefer writing it
  next to the thing it governs; if it has no home yet, use
  `python tools/rule.py "<ruling>" --flavour <slug>`, which **shows you every
  prior ruling in that flavour first**. `RULINGS.md` + `rulings.json` are
  GENERATED by `python scripts/generate_rulings.py` (pre-commit `--check` blocks
  stale commits). Ruling-shaped prose with no declaration is reported as
  `UNDECLARED`, never dropped. **Cross-repo by design** (ruled 2026-08-15):
  each repo emits `rulings.json` (schema `pdoom.rulings/0.1`) and an aggregator
  reads them; nothing writes back. Convention argued in
  `docs/rulings/RULINGS_CONVENTION.md`.
- `godot/scripts/core/` -- game logic (game_state, turn_manager, actions,
  doom_system, finance_engine, events, ...). Deterministic, testable.
- `godot/scripts/ui/` -- screens/panels (`main_ui.gd` is the 3k-line monolith).
- `godot/autoload/` -- singletons (event_service, game_config, theme_manager, ...).
- `godot/data/` -- data-driven balance/events/actions/scenarios (JSON). Prefer
  editing data over hardcoding.
- `godot/tests/` -- `unit/` (fast), `unit/simulation/` (slow), `integration/`.

## Scene navigation -- ALWAYS through SceneTransition (MUST)
Change scenes ONLY via the `SceneTransition` autoload:
`SceneTransition.go_to("res://scenes/X.tscn")` / `SceneTransition.reload()`.
NEVER call `get_tree().change_scene_to_file()` / `change_scene_to_packed()` /
`reload_current_scene()` directly. Why: calling `change_scene_to_file()` from inside an
`_input()`/`_gui_input()` handler segfaulted the RELEASE build (0xc0000005, before
`_ready`) -- the v0.11.0 leaderboard crash. `SceneTransition` ALWAYS defers the swap, so it
is safe from any context (input handlers, signals). Enforced by
`tools/check_scene_nav.py` (pre-commit on changed `.gd`; CI full-tree scan); annotate a
genuine one-off exception `# scene-nav-allow`. Full story: `docs/LEADERBOARD_CRASH_DIAGNOSIS.md`.

## Version + builds
- `version.txt` (root) is the version SSOT. After bumping, run
  `python tools/sync_version.py` (stamps `game_config.gd` / `project.godot` /
  `export_presets.cfg` / `welcome.tscn`). `sync_version.py --check` gates pre-commit + CI
  (a silent drift forks the leaderboard board-key -- fatal).
- `ladder_version.txt` (root) is the LADDER epoch SSOT and the leaderboard board
  key. **`tools/check_ladder_bump.py` now FAILS the build** (armed in #1178,
  advisory before that): touching anything under `godot/` outside
  UI/scenes/assets/theme/tests/docs requires either a ladder bump or a line
  `Ladder-Impact: none -- <reason>` in a commit message or the PR body. It is
  proven against real history on every CI run via `--self-test`.
- Cut Windows builds with `python tools/build_release.py` -- it nukes `godot/.godot`
  (defeats the stale-export-cache trap), auto-stamps the build via `write_build_stamp.py`
  (no more "unstamped"), exports, and PROVES a unique freshness marker is in the `.pck`
  before emitting. NEVER hand-run a raw `godot --export` (stale-cache risk; burned ~12
  cycles in v0.11.0).
- **Godot packs the ENTIRE `godot/` tree into the `.pck` (referenced or not).**
  Keep retired/source assets OUTSIDE `godot/` (`art_source/` for <=1MB art kept
  in git; masters archive `G:/tmp/pdoom1-art-masters/` for >1MB per
  `docs/art/ART_MASTERS_POLICY.md`). Before moving/removing ANY asset,
  `grep -rn` its `uid://` AND `res://` path across `godot/` -- scenes/resources
  reference by UID, not path, so a blind move silently breaks refs (issue #787:
  ~488MB of unreferenced hi-res icon variants were bloating the `.pck`).

## CI is honest now (#640)
Green CI means tests actually ran. Earlier the gate reported green while running
ZERO tests (cold class cache -> GUT quit(0)); `run_godot_tests.py` now parses the
JUnit XML, enforces a min-test floor, and fails if any `test_*.gd` was silently
dropped. Trust green.
