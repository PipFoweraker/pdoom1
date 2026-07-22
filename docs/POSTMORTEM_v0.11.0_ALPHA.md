# P(Doom)1 -- Postmortem / Running Lessons-Learned

> **Status: running lessons-learned log.** One entry per ship. This is entry #1
> (the v0.11.0 friends-and-family alpha, 2026-07-17..20). Future ships append their
> own dated entry below; do **not** rewrite past entries -- they are the record.
> Like `DESIGN_PHILOSOPHY.md` and `VISION_ACCUMULATION_AND_EVOLUTION.md`, this
> preserves the concrete facts (PR numbers, error strings, measured timings) before
> abstracting them into a lesson, so the evidence chain survives.

The game's own thesis is that a thing which "keeps building and building itself" should
**articulate the story of its own development** (`VISION_ACCUMULATION_AND_EVOLUTION.md`
section 2.4: the dev-facing accumulation is the *same shape* of story as the player-facing
one -- simple principles branching into increasingly articulated philosophies). A
postmortem log is that motif applied to the process, not just the design: the repo
recording its own developmental lessons is part of the accumulation thesis, in
process-space rather than strategy-space. So this file is not overhead -- it is the game
being what it says it is.

Voice note: honest over triumphalist. The most valuable content here is the
**mis-diagnoses**. A postmortem that only lists wins teaches nothing next time.

---

## Entry #1 -- v0.11.0 friends-and-family Windows alpha (2026-07-17..20)

Ship status as of 2026-07-20: **core loop verified end-to-end; final texture-crash fix
merged (#728) but not yet re-tested on a fresh release build; publish pending Pip's
re-test.**

### 1. What we set out to ship

A friends-and-family, direct-download **Windows** alpha (v0.11.0). The core payoff is not
a feature -- it is the **loop closing on itself**, the LOOP + META-LOOP:

> download -> play -> lose -> your score posts -> it lands on a live global leaderboard
> your friends can see (and see themselves on).

That is why the leaderboard was the release-blocking surface: if the score does not make
the round trip, the whole point of *this* build evaporates. Everything else in the build
(hiring pipeline, PLAN/WATCH views, honest defeat screens, the arxiv-flood feed filter)
is in service of producing a run worth posting.

The backend that makes the meta-loop real: a live **PHP score API** deployed on the
DreamCompute VM (`api.pdoom1.com`, nginx + php-fpm), writing per-`(seed, game_version)`
boards. The HTTP + scoring contract is **frozen** (ADR-0002: turns-survived, flows-only,
lexicographic tiebreak on the doom integral; `BACKEND_AND_DATA_ARCHITECTURE.md`: one PHP
host, versioned-never-silent contract). Deploy + round-trip landed across PRs #679
(architecture), #680 (remote client), #698 (nginx), #701 (go live).

### 2. The leaderboard-crash hunt (the headline lesson) -- FIVE passes to root cause

The live build "quit weirdly" when you opened or reached the end of the game near the
leaderboard. Root-causing it took **five passes**. Each pass found a *real* bug and fixed
it; the first four were real-but-not-the-crash (or not the *whole* crash). Told honestly,
because the honest telling is the lesson:

**Pass 1 -- the endgame freeze + lost score (PR #705, #694).** First report: "quit weirdly
at end-game," and -- worse -- *no score reached the server* (confirmed: the server data dir
held only the deploy-test board after a full playthrough). Found: `game_over_screen.gd`
ran a **multi-second synchronous baseline simulation on the main thread** (measured
~4.0s) and fired the score POST *after* it. The window went "Not Responding," the player
force-quit during the freeze, and the async POST -- the last scoring step -- never
dispatched. Fixed properly: non-blocking baseline at defeat, **score-first** (persist +
dispatch before rendering), a re-entrancy guard, and a **durable outbox**
(`user://pending_scores.json`, retried at next launch) so a slow/dead endpoint or a
mid-post exit can no longer lose a score. Real fix. **Not the crash.**

**Pass 2 -- the memory leak (PR #713).** Re-test still died -- a segfault right after
"Transitioning to leaderboard" on a large accumulated population (the dev had ~400 pages).
Found a genuine leak: `leaderboard.gd extends Node`, so each `Leaderboard` instance is
**not refcounted**; `_load_all_leaderboards()` created one board Node per file and
**retained it forever** in `all_leaderboards`. Every re-open leaked a Node plus its whole
`entries` array -> unbounded growth -> segfault. Fixed: parse each board transiently, copy
the `RefCounted` entries out, `free()` the Node; page-bounded row instantiation; drop
refs on `_exit_tree`. Real fix (and it too was a genuine release-build segfault). **Still
not the whole crash.**

**Pass 3 -- the load-perf issue (PR #716).** Still crashing. Found the leaderboard parsed
**every seed file on every open** and sorted the full population each time. Headless
timing on an accumulated 383 boards / 3083 entries: full all-seeds scan+sort = **~1004ms
every open**; a cheap dir-listing discover = **16ms**, parse one board = **3ms**. Fixed:
`_ready` does a no-parse `_discover_boards()` and opens only the current board (~19ms);
the cross-seed aggregate parses lazily on demand. (~1s -> ~19ms.) Real fix. **Not the
crash.**

**Pass 4 -- ruling out the renderer.** Launched with `--rendering-driver opengl3`. It
**still crashed on OpenGL** -- so the fault is **renderer-independent**. That single test
ruled out the GPU / Vulkan driver as the cause and pointed at *content*, not the graphics
backend. A negative result, but a load-bearing one: it redirected the hunt.

**Pass 5 -- `--verbose` names the culprit (PR #728).** Ran with `--verbose`. The **last
resource logged before "Segmentation fault"** was the imported `.ctex` for
`tex_cyan_ispf_512` (and its sibling `tex_oxidized_copper_512`) -- the two background
textures used **only** by `leaderboard_screen.tscn`. The crash lives in the **CPU-side
texture decode**, *before* the GPU is involved (consistent with pass 4: renderer-
independent). Headless never hit it because **headless does not fully decode textures**.
Fixed by swapping the two decorative `TextureRect` backgrounds for `ColorRect` palette
solids (menu-chrome off-black indigo `#170A1C`), which removes the trigger.

**Honesty caveat on pass 5 (from the PR, do not overclaim):** static analysis did **not**
confirm a "malformed PNG." All 20 textures in those folders are structurally identical
(512x512, 8-bit RGBA, no ICC profile, valid IEND) and **all decode cleanly through
libpng/PIL**; the two crashers are indistinguishable from their 18 siblings. So the true
cause is one of: (a) a Godot-internal codec edge-case on the specific pixel payload of
those two files, or (b) the `.ctex` line was merely the *last flushed log event* before an
unrelated crash. The ColorRect swap removes the trigger either way, but the mechanism is
**not fully pinned** -- flagged so a later ship does not cite "malformed texture" as
settled fact. Batch risk noted in #728: the same bg+overlay texture pattern is in
`welcome.tscn`, `settings_menu.tscn`, `pregame_setup.tscn` -- they reportedly do not crash
(which argues payload-specific over systematic), but they warrant a targeted release-build
re-test.

Why five passes and not one: the same scene (`leaderboard_screen`) genuinely stacked
**multiple independent release-affecting faults** -- a lost-score bug, a real memory leak
that segfaulted, a real perf cliff, and a texture-decode segfault. Each pass found a true
bug whose fix was worth shipping, which is *exactly* what made each one look like the root
cause. Plausibility was the trap.

### 3. Lessons (the reusable core)

**L1 -- Headless GUT cannot catch GUI render / texture-decode crashes.** Headless
"instanced OK" the whole way through; the fatal fault lived in the CPU texture-decode
layer that headless *structurally does not exercise* (it does not fully decode textures).
Automated green != the GUI runs. The **human release-build playtest was the only gate that
surfaced it** -- and also surfaced the ledger dead-end and several text traps. Concrete
rule: **a required human play-through to the affected screen, on the RELEASE build (not
debug, not headless), before declaring anything render / asset / scene-transition
shipped.**

**L2 -- How to diagnose a native segfault (the toolkit that worked here):**
- `--verbose`: the **last resource logged before the fault** names the likely culprit
  (here, `tex_cyan_ispf_512.ctex`). Necessary caveat: "last logged" can be "last flushed
  before an unrelated crash" -- strong signal, not proof.
- `--rendering-driver opengl3`: **renderer vs content triage.** Crash persists on OpenGL
  => renderer-independent => it is the content/CPU path, not the GPU/Vulkan driver.
- **Debug builds can MASK release-only crashes.** The memory-leak segfault (#713) only
  killed the *release* build; debug strained but survived. A passing debug run is **not**
  proof the release build is safe.

**L3 -- Do not declare "fixed" without the real repro passing.** The crash was mis-called
fixed *twice* by conflating it with adjacent real bugs (the freeze, then the leak). Each
adjacent bug was real and worth fixing -- but fixing a real bug is not the same as fixing
*the* bug. Follow the evidence (the actual repro still failing), never the plausible
hunch, no matter how satisfying the hunch. The MAIN discipline applies literally here:
"Do we know provenance of {the fix}?" -- provenance is the repro passing, not the patch
merging.

**L4 -- Process / tooling landmines (brief; from `CLAUDE.md` + this ship):**
- **Background commits + parallel tool activity roll back.** The session harness rewrites
  `.claude/settings.local.json` on any tool call; pre-commit stashes that file, sees it
  change mid-hook, reports "Stashed changes conflicted with hook auto-fixes... Rolling
  back," aborts -- **and the rollback discards working-tree edits made during the run.**
  Commit in the FOREGROUND, zero tool calls while hooks run (cost 4 attempts 2026-07-19).
- **`git checkout -- godot/` discards unstaged real edits.** It is the sanctioned way to
  drop the ~1200-file `.import`/`.uid` churn from an `--import` pass, but it does not
  distinguish churn from your genuine unstaged work. Never run it with real unstaged edits
  present; stage your files first (`git add <path>`), never `git add -A`.
- **Machine sleep stalls overnight background agents.** A sleeping dev machine froze
  long-running background agents to ~15h wall-clock -- they do not run while the host
  sleeps. Do not assume an overnight background job made progress.

### 4. What went right

Recorded plainly (the wins are real; they are just not the point of a postmortem):
- **Live backend, round-trip verified.** api.pdoom1.com deployed (nginx + php-fpm) and a
  real score made the download -> play -> lose -> post -> board trip (#679, #680, #698,
  #701).
- **Real gameplay + robustness fixes shipped**, each with the repro that proved it:
  promise-currency early-loss fix (#685: promises cost domain obligations, not a
  reputation rep-bomb); the P0 batch (#691: quit-to-menu, honest defeat title, event-feed
  filter); the endgame freeze + durable outbox (#705); the memory leak (#713); the
  load-perf cliff (#716); the ledger dead-end (#711); player-facing text traps (#715).
- **Tests that resist hollowness.** Anti-hollow strategy + property-based invariants
  (ADR-0017, #687, #699), and an **auto-discovering** no-UI-dead-end escape-contract test
  (#711) that walks openable panels rather than a hardcoded list -- so a *future* trapping
  panel is caught without anyone remembering to add it. (Note the boundary these tests
  could not reach: none of them touch the GUI decode path -- see L1.)
- **The accumulation/evolution vision captured** (`VISION_ACCUMULATION_AND_EVOLUTION.md`,
  #712): run telemetry as the game's self-building substrate, contract-safe.
- **A working art pipeline**: generate -> local review app with persistent verdicts (#706)
  -> `apply_review.py` promote/reroll (#709), fed by a volume batch (#708).
- **The process feature, stated as a feature, not a failure:** the human playtest caught
  what the automated tests structurally could not. That is the gate working as designed
  (L1), not the tests failing.

### 5. Actions carried forward

Short and factual -- the open work this ship spawned:
- **#715** (PR, open) -- player-facing copy audit: traps fixed, hardcoded -> variable.
- **#717** (PR, open) -- directional menu-consistency pass (palette/texture alignment);
  the ColorRect ship-fix in #728 was aligned to this direction. Related issues: **#707**
  (UI consistency sweep after asset promotion), **#602** (navigation/ESC-back audit),
  **#565** (Travel/Conferences only reachable by hotkey).
- **#714** (issue, open) -- turn-1 / early-days processing feels slow: the baseline-sim
  perf theme from pass 1/pass 3, now a standing watch-item.
- **#712** (PR, open) -- the accumulation/evolution vision doc.
- **#703** (issue, open) -- v0.11.0 playtest: defeat-pacing drag + hiring pipeline feels
  gappy.
- **#700** (issue, open) -- local `Leaderboard.add_score` does not dedupe by `entry_uuid`
  (remote PHP does).
- **#718** (PR, open) -- success premortem + four-lens review pack (2026-07-20).
- **Follow-up owed on #728:** re-test `welcome` / `settings_menu` / `pregame_setup` on the
  release build (same bg-texture pattern; batch risk), and -- if worthwhile -- pin whether
  the decode fault is a Godot codec edge-case or a misleading last-log-line (L2 caveat).

### 6. RESOLUTION (2026-07-21) -- pass 5 was ALSO a mis-diagnosis; the real root cause

Recorded here rather than by editing the passes above (the passes stay as the honest
record of the hunt). **Pass 5's texture-decode conclusion was wrong too.** On a genuinely
fresh release build, the crash **survived** the ColorRect swap (#728) -- and survived a
build with the two suspect textures *physically removed from the pack*. The `.ctex` line
was exactly the "last flushed log event before an unrelated crash" that L2 warned about.
Two more wrong hypotheses followed (an orphaned baseline thread -- but the weekly-league
seed used a precomputed baseline, so no thread ever started; and a dangling GUI
`key_focus` -- disproven by a `gui_release_focus()` build that still crashed).

**The actual root cause (pass 7, confirmed):** `game_over_screen.gd` called
`change_scene_to_file()` **synchronously from inside its `_input()` handler** (ENTER key).
That runs a full scene load + instantiate mid input-dispatch, which segfaulted the
optimized engine deterministically (`0xc0000005`, faulting module `PDoom.exe`, offset
`0x142be24`, before `_ready`). **Fix: `call_deferred("_continue_to_leaderboard")`** -- move
the nav onto a clean idle frame. A verified-fresh release build reproduced the crash; the
deferred build reached the leaderboard cleanly. Full write-up + the reusable method:
`docs/LEADERBOARD_CRASH_DIAGNOSIS.md`.

New lessons this resolution adds:

**L5 -- Windows Event Viewer is the free backtrace substitute.** When Godot's crash handler
prints nothing (hard `0xc0000005` outruns the logger) and no debugger is installed, the
Windows Application log (Event ID 1000, `Get-WinEvent`) already holds the exception code +
faulting module + offset for every crash produced -- no rerun. A **constant offset across
independent builds** proves a deterministic native deref (engine), not a GDScript error.

**L6 -- "last resource in `--verbose`" frames the WRONG layer when the fault is an ACTION,
not an asset.** For four days the last-logged leaderboard `.scn`/`.gdc` load framed this as
a leaderboard-scene bug. The load was innocent; the *act of loading from within input
dispatch* was the fault. When a stub/minimal target crashes identically, stop blaming the
target.

**L7 -- Systemic, not a one-off.** The same "scene change from inside `_input`" pattern is
latent in `config_confirmation`, `leaderboard_screen`, `settings_menu`, `welcome_screen`
and others (see LEADERBOARD_CRASH_DIAGNOSIS.md section 6). Game-over just detonated first.
Carried-forward action: defer all input-initiated navigation (or route it through a
`SceneRouter` + a lint that bans direct `change_scene_to_file` from input handlers).

**L8 -- `build_release.py` earned its keep.** Passes 5-7 were only trustworthy because each
build was proven fresh (marker file in the `.pck`). The earlier stale-`.godot/exported`
cache had silently packed old scenes and burned ~12 cycles; anchoring freshness on a
resource FILENAME (GDScript packs as binary `.gdc`, so string literals do not survive as
grep-able text) is what made "the fix is really in this build" checkable.

---

<!-- Future ships: add "## Entry #2 -- <version> (<dates>)" below this line. Keep the
same shape: what we set out to ship / the headline hunt told honestly / reusable lessons
/ what went right / actions carried forward. Never edit a prior entry. -->
