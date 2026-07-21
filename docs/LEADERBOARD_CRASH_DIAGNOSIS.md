# Leaderboard crash -- diagnostic builds + ordered kill protocol

Release-blocking bug: the game **segfaults while LOADING the leaderboard scene** on the
game-over -> leaderboard transition. RELEASE-ONLY. The crash happens **before**
`leaderboard_screen.gd::_ready` runs (trace prints never fired). Main-menu-from-game-over
works, so it is leaderboard-scene-specific, not a teardown fault. #728 already swapped the
leaderboard bg textures for ColorRects and the crash persisted in a verified-fresh build.

This doc is COMMITTED on purpose (must survive compaction). It lists three verified-fresh
diagnostic builds and the exact ordered protocol to run them. The builds were each
produced with `tools/build_release.py`, which nukes `godot/.godot`, injects a unique
marker file, exports, and PROVES the marker is in the `.pck` before emitting the build --
so each pack below is confirmed built from the current source (NOT a stale cache).

---

## The three diagnostic builds (each verified-fresh at build time)

> Paths are the STABLE copies under the main repo `builds/` tree (gitignored). They are
> also present in the agent worktree under `builds_diag/` but that worktree may be cleaned
> up; prefer the stable paths.

| # | Build | Mode | What it changes | Absolute path (PDoom.exe / .console.exe next to PDoom.pck) |
|---|---|---|---|---|
| 1 | DEBUG | `--export-debug` | current source + `[LBTRACE-n]` probes in `_ready` | `G:\Documents\Organising_Life\Code\pdoom1\builds\leaderboard-diag\debug01\PDoom.exe` |
| 2 | THEME-STRIPPED | `--export-release` | `tex_cyan_ispf_512` + `tex_oxidized_copper_512` **removed from theme_manager AND absent from the pack** (source files stashed so no `.ctex` is generated -- verified 0 occurrences in the pack) | `G:\Documents\Organising_Life\Code\pdoom1\builds\leaderboard-diag\strip01\PDoom.exe` |
| 3 | MINIMAL SCENE | `--export-release` | `leaderboard_screen.tscn` at its real path reduced to Control + ColorRect + Label + EntriesContainer stub + Back button, with a dependency-free stub script (`leaderboard_screen_min_stub.gd`) | `G:\Documents\Organising_Life\Code\pdoom1\builds\leaderboard-diag\min01\PDoom.exe` |

Capturing the log (IMPORTANT -- differs by build):
- **Build 1 (DEBUG)** ships a **`PDoom.console.exe`** wrapper next to `PDoom.exe`. Run the
  console one so stdout/stderr are visible.
- **Builds 2 and 3 (RELEASE)** do NOT ship a console wrapper (Godot only emits it for
  debug exports). Two reliable ways to get the log:
  1. From a terminal, redirect the GUI exe -- inherited handles are captured even though
     the window is GUI-subsystem: `PDoom.exe --verbose > run_buildNN.log 2>&1`.
  2. Or read Godot's own user log afterwards:
     `%APPDATA%\Godot\app_userdata\P(Doom)\logs\godot.log` (newest entry).

---

## Ordered protocol -- run in this order, stop when a step is conclusive

For every run: launch with `--verbose` capturing the log (see "Capturing the log" above --
console wrapper for the debug build, redirection or the user log for the release builds),
then play -> lose -> press ENTER for leaderboard, and inspect the tail of the log:

```
# Build 1 (debug):    "C:\...\debug01\PDoom.console.exe" --verbose > run_build1.log 2>&1
# Builds 2/3 (release): "C:\...\strip01\PDoom.exe"       --verbose > run_build2.log 2>&1
```

### STEP 1 -- Build 1 (DEBUG): get the deepest trace
The earlier "debug didn't crash" was very likely itself a STALE build. Build 1 is a
verified-fresh debug export; a debug build installs a crash handler that prints a
**symbolized backtrace** on segfault -- the single most valuable signal.

Look for, in `run_build1.log`:
- `[LBDIAG-TRACE-DEBUG-01] ... _ready ENTERED` and the `[LBTRACE-1..6]` lines.
- A crash dump ("Dumping the backtrace" + stack frames).

Interpretation:
- **No `[LBTRACE]` lines + a backtrace** -> crash is genuinely pre-`_ready`. The backtrace
  names the native call (scene/resource loader, text server, or renderer). This is the
  deepest lever -- read the top non-Godot-internal frame. GO no further until you've read
  this trace; it may name the cause outright.
- **Some `[LBTRACE-n]` lines then crash** -> the crash is actually INSIDE `_ready` at step
  `n+1` (the pre-`_ready` claim was a stale-build artifact). Jump to the named call.
- **Build 1 does NOT crash at all** -> confirmed release-only (optimizer/renderer). Go to
  STEP 2/3 (release builds) to isolate.

### STEP 2 -- Build 2 (RELEASE, textures ABSENT): exonerate or convict the textures
The two suspect textures are **not in this pack at all** (verified: 0 occurrences).

- **Still crashes** -> textures are **fully EXONERATED**. This is the expected outcome
  given the code reading (nothing ever `load()`s them; they were dead string paths). Go to
  STEP 3.
- **No crash** -> textures WERE implicated despite never being loaded by game code (would
  implicate the `all_resources` packing / a pack-time decode path). Fix = keep them
  excluded/deleted; done.

### STEP 3 -- Build 3 (RELEASE, MINIMAL scene): structure vs content
Build 3 puts a bare scene at the real `res://scenes/leaderboard_screen.tscn` path.

- **Minimal LOADS fine (reaches the minimal board, `[LBMIN-TRACE]` prints)** -> the crash
  is in the REAL scene's structure/content, not the transition. Binary-search it back:
  copy the real scene, delete ~half its nodes, rebuild with `tools/build_release.py`,
  retest; halve until the offending node/sub-resource is isolated. Prime suspects, in
  order: the `OptionButton` (SeedDropdown -- instantiates an internal PopupMenu; unique to
  this scene, absent from welcome/game-over), then the `Panel` + `ScrollContainer` nesting,
  then the emoji Labels (though welcome.tscn also has an emoji Label and loads fine).
- **Minimal ALSO crashes** -> the fault is more fundamental than scene content: the
  game-over -> leaderboard scene-CHANGE path itself, or a renderer/text-server interaction
  triggered by ANY scene at this path in a release build. Diff against the welcome.tscn
  transition (which works) for the differentiator.

---

## Rebuilding any variant (for the STEP 3 binary search)

Always rebuild through the verify-the-pack tool -- never a raw `--export`:

```
python tools/build_release.py --mode release --output builds/leaderboard-diag/probeNN
```

It refuses to emit a build whose pack does not contain its injected marker, so you can
never again waste a cycle testing a stale pack.

## Reproducing the minimal build (Build 3) from scratch
1. `cp godot/scenes/leaderboard_screen_minimal.tscn godot/scenes/leaderboard_screen.tscn`
   then fix the uid line back to `uid://c8jkm2s8cdp4t` (keeps other refs stable).
2. `python tools/build_release.py --mode release --output builds/leaderboard-diag/min01`
3. `git checkout -- godot/scenes/leaderboard_screen.tscn` to restore the real scene.

---

## Best current hypothesis (from reading the scene + theme code)

Reading the code (not yet confirmed by a live trace -- headless cannot reproduce this):

1. **Textures are almost certainly NOT the cause.** `tex_cyan_ispf` / `tex_oxidized_copper`
   are referenced ONLY as dead string paths in `theme_manager.gd`; nothing ever
   `preload`/`load`s them. Meanwhile `welcome.tscn` loads REAL textures (as `TextureRect`
   ext_resources) and is the boot scene -- it loads fine. So "textured scene" is not the
   discriminator; the leaderboard scene is now textureless yet crashes. Build 2 is the
   falsification test.
2. **The script preload chain is clean.** `leaderboard_screen.gd` member-preloads
   `scripts/leaderboard.gd`, which has no resource dependencies, and `game_over_screen.gd`
   already uses the `Leaderboard` class successfully -- so that dependency is resolved
   before the transition and is not the fault.
3. **Leading suspect: the `OptionButton` (SeedDropdown).** It is the one node type unique
   to this scene (absent from welcome and game-over). `OptionButton` builds an internal
   `PopupMenu`/`Window` sub-resource at instantiation; a Window/Popup created during a
   scene-change, in a release renderer, is a plausible pre-`_ready` native-crash site.
   Build 3 (which has NO OptionButton) is the direct test: if Build 3 loads and the real
   scene does not, the OptionButton is the prime candidate to bisect to first.

Ranked: (a) OptionButton/PopupMenu instantiation in the release renderer ~45%; (b) some
other scene sub-resource/structure interaction ~30%; (c) the scene-change machinery itself
on this specific transition ~15%; (d) textures ~5%; (e) something else ~5%. Build 3's
result splits (a)+(b) from (c), and Build 1's backtrace should name the native frame
directly.
