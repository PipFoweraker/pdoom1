# UI evolution capture -- the "it went from this... to this..." rail

> Authorized: Pip's UI-evolution capture ask, 2026-07-27 0800. Purpose:
> programmatically capture UI states as visual lanes land, so a later
> devblog/anniversary/grantmaker montage can be assembled from a real timeline
> instead of hunting through Win+PrtScn screenshots by hand.

## The three pieces

1. **In-game hotkey (F7)** -- `godot/scripts/debug/ui_evolution_recorder.gd`,
   wired through `KeybindManager.ui_evolution_shot_requested`. One silent
   press drops a screenshot + a one-line context entry (scene name, version,
   turn) into `user://ui_evolution/<version>/manifest.jsonl`. Dev-build only
   (`BuildInfo.is_dev_build()`), same gate as the flight recorder (F6) and the
   DEV MODE overlay -- zero cost in release builds.
2. **Collector** -- `tools/collect_ui_evolution.py`. Resolves the real Windows
   path for `user://` (`%APPDATA%/Godot/app_userdata/P(Doom)/`), sweeps
   `ui_evolution/` for a date range, optionally also sweeps
   `Pictures\Screenshots` (the existing manual Win+PrtScn rail -- timestamped
   automatically by Windows), and copies everything into
   `G:/tmp/pdoom1-ui-evolution/<date>/` with normalized names plus an ASCII
   `index.md` timeline table.
3. **This doc** -- the convention: when to press F7, where things land, how
   the timeline gets mined later.

## Why F7 is a *silent* capture, unlike the flight recorder (F6)

The flight recorder (F6, `godot/scripts/debug/flight_recorder.gd`) is a deep
playtest tool: screenshot + full `GameState.to_dict()` snapshot + a note popup
that pauses for input. UI evolution capture is a much lighter ask -- "grab
what this screen looks like right now" -- so F7 does not open a popup, does
not dump game state, and does not block input. It reuses the flight
recorder's *shape* (session directory under `user://`, append-only
`manifest.jsonl`, zero-padded sortable filenames) rather than inventing a
third capture layout, but it is deliberately cheaper per press.

## When to capture

- **Before and after every visual-lane merge** (theme changes, panel
  redesigns, new screens, art passes that touch UI chrome). Press F7 once on
  the pre-merge build, once on the post-merge build, same scene/screen if
  possible.
- **On version bumps**, if a lane spans several versions -- one shot per
  `version.txt` bump keeps the timeline resolvable by version even without
  precise dates.
- Ad hoc, whenever something looks worth remembering for a "look how far this
  has come" narrative later. Cheap enough to over-capture; the collector's
  date filtering makes cleanup a non-issue.

## Where things land

- **In-game (per machine, per project):**
  `user://ui_evolution/<version>/` -->
  `%APPDATA%/Godot/app_userdata/P(Doom)/ui_evolution/<version>/` on Windows
  (macOS/Linux equivalents in `tools/collect_ui_evolution.py::resolve_user_dir`).
  Each version directory holds `NNNN_<timestamp>.png` screenshots plus one
  `manifest.jsonl` (one JSON line per shot: `index`, `timestamp`, `version`,
  `scene`, `turn`, `screenshot`).
- **After collection:** `G:/tmp/pdoom1-ui-evolution/<date>/` (or a
  `--dest` override) -- **outside the repo**, same doctrine as
  `docs/art/ART_MASTERS_POLICY.md` masters staging (`G:/tmp/pdoom1-art-masters/`):
  Godot packs the entire `godot/` tree into the `.pck`, and this capture set
  accumulates indefinitely, so it must never live under `godot/` and should
  not be committed to git.

Run the collector after a capture session:

```
python tools/collect_ui_evolution.py                        # today's captures
python tools/collect_ui_evolution.py --since 2026-07-20 --until 2026-07-27
python tools/collect_ui_evolution.py --no-manual             # skip Pictures\Screenshots
python tools/collect_ui_evolution.py --dry-run               # preview only
```

## How the timeline gets mined later

`index.md` in each dated staging directory is the join point: a plain ASCII
table of `Version | Timestamp | Scene | Turn | Source | File`, sorted
chronologically. For a montage/devblog pass:

1. Pick the version/scene pairs that bracket the change being told (e.g.
   "the office floor before/after the sprite re-base").
2. Cross-reference by timestamp against the perf story: `UIEvolutionRecorder`
   calls `PerfLog.mark("ui_evolution", {"index":..., "version":..., "scene":...})`
   on every capture (`godot/autoload/perf_log.gd`, merged in PR #973's
   story-mining hooks). If `PerfLog` is active for that session, the same
   moment shows up as a `MARK ui_evolution` line in the perf trail, so the
   visual story and the performance story can be joined by timestamp without
   a second manual log.
3. Assemble the before/after pairs into whatever the output needs (devblog
   screenshots, anniversary retrospective, grantmaker deck) -- the staged
   files are already normalized and dated, so no further hunting through
   Pictures\Screenshots is needed.

## Gotchas

- F7 does nothing in a release build (`BuildInfo.is_dev_build()` gates it) --
  this is by design, not a bug to fix.
- The collector's `--since`/`--until` filter reads the `timestamp` field
  written by the recorder, not filesystem mtimes, for the F7 rail (mtimes are
  used only for the manual `Pictures\Screenshots` sweep, since Windows
  doesn't tag those with in-game metadata).
- If `user://ui_evolution/` doesn't exist yet, the collector reports "nothing
  found" rather than erroring -- press F7 at least once first.
