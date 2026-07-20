# Postmortem -- v0.11.0 friends-and-family alpha

Status: living document. This file is created on branch
`fix/leaderboard-crash-deep-diagnosis`; if PR #730 (the earlier postmortem/lessons
doc) lands first, fold these sections in rather than duplicating.

The release was blocked for an extended period by a single release-only segfault
(game-over -> leaderboard). The engineering cost was dominated NOT by the bug itself
but by a diagnostic-tooling trap that made every test cycle lie. The lessons below are
ordered by how much time they cost.

---

## Lesson 1 (most expensive): Godot's `.godot/exported/` cache silently ships STALE scenes

### What happened
Every export run from the release-build worktree packed an OLD, converted copy of the
leaderboard scene. Fixes (the #728 texture->ColorRect swap) and diagnostic `printerr`
traces were written, committed, and exported -- and were simply NOT in the build that
was tested. ~12 test cycles were burned "reproducing" a bug that the current source may
already have changed, because nobody could prove which source a given `.pck` was built
from. `--import` did NOT clear the stale artifact; deleting `.godot/exported/` alone did
not reliably clear it either.

### Root cause
Godot caches converted/imported artifacts under `godot/.godot/` (including
`.godot/exported/`). Under some worktree/cache states the exporter reuses a stale
converted scene instead of reconverting from the `.tscn` source.

### The discipline (now enforced in code)
1. **Before ANY export: `rm -rf godot/.godot`** to force a genuine from-scratch build.
2. **Prove the pack is fresh** before trusting it (next lesson).
`tools/build_release.py` does both and refuses to emit an unverified build.

---

## Lesson 2: "grep the pack for a string you added" does NOT work here -- anchor on a FILENAME

The natural freshness check -- add a unique `printerr("TAG")` to a script, then grep the
`.pck` for `TAG` -- is UNRELIABLE in this project's export config, and quietly so.

### Why (verified 2026-07-21)
This project exports GDScript as **binary-tokenized `.gdc`** (the pack lists
`res://scripts/ui/leaderboard_screen.gdc` + a `.gd.remap`). String LITERALS inside
scripts do **not** survive as grep-able UTF-8 (nor UTF-16, nor UTF-32) in the pack.
Grepping the pack for an existing script string such as `"Leaderboard screen opened"`
returns **nothing**.

What DOES survive, reliably, is **resource PATHS / filenames** in the pack's file table:
grepping for `res://scripts/leaderboard.gd` or the substring `leaderboard_screen` hits.

### The reliable anchor
Drop a **uniquely-named marker file** into the project immediately before export (e.g.
`buildstamp<uuidhex>.gd`), then grep the pack for that unique token. Its `res://` path
lands in the file table, so a hit proves the pack was built from the current working
tree. This is what `tools/build_release.py` injects and verifies; a miss aborts the
build non-zero.

Corollary correction to earlier notes (SESSION_STATUS_2026-07-21): the advice to "grep
the pack for a SCRIPT string you added (e.g. an added printerr tag)" should be replaced
with "grep the pack for a unique marker FILENAME you added."

---

## Lesson 3: `export_filter="all_resources"` packs textures regardless of code references

The leaderboard segfault was suspected to involve two background textures
(`tex_cyan_ispf_512`, `tex_oxidized_copper_512`) that were referenced only as **dead
string paths** in `theme_manager.gd` (stored, never `preload`/`load`-ed). A natural fix
-- "remove the strings so the textures are not packed" -- does NOT unpack them: the
Windows preset uses `export_filter="all_resources"`, which packs every resource in the
project irrespective of references.

Consequences for diagnosis:
- Removing the `theme_manager.gd` strings is still worth doing (kills a dead reference)
  but changes nothing about what is packed.
- To PROVE a texture is not the cause, the source asset (and its import sidecar) must be
  **absent** so no imported `.ctex` artifact is generated. Excluding only the source
  `*.png` via `exclude_filter` leaves the imported `.ctex` (hashed name still contains
  the source stem) in the pack -- partial, not conclusive.

---

## Lesson 4: the render-gate limitation -- what headless CANNOT catch

Headless Godot (tests, `--import`, `--script` probes, even a verified-fresh pack) uses a
dummy rendering/audio driver. It does **not** GPU-decode textures, allocate real VRAM,
or run the platform's release-mode renderer. Therefore:
- A crash that only manifests in a **release export on a real GPU** will not reproduce in
  any headless check. The v0.11.0 leaderboard segfault is exactly this class (it did not
  reproduce headless; the existing smoke test already instantiate()s the scene cleanly).
- Headless gates (`test_smoke_load_all.gd`, the new `test_ui_scene_ready_smoke.gd`,
  `validate_assets.py`) are **necessary but not sufficient**. The final ship gate is a
  **human playing a release build** through the exact transition (play -> lose ->
  leaderboard) on real hardware.

---

## Defenses added on `fix/leaderboard-crash-deep-diagnosis`

| Defense | File | Catches |
|---|---|---|
| From-clean export + pack-freshness verify (marker filename) | `tools/build_release.py` | stale-cache builds (Lessons 1-2) |
| UI-scene add-to-tree + `_ready` smoke | `godot/tests/unit/test_ui_scene_ready_smoke.gd` | `_ready`-time faults the instantiate-only smoke missed |
| Asset-import validation gate | `tools/validate_assets.py` + `godot/tools/validate_assets_probe.gd` | a corrupt/undecodable asset before it ships |
| Ordered crash-diagnosis protocol + diagnostic builds | `docs/LEADERBOARD_CRASH_DIAGNOSIS.md` | reproducing + isolating THIS crash |

All three defenses are honest about the render-gate limit (Lesson 4): they harden the
whole class of load-time faults, but the human release-build playtest remains the gate
that would have caught this specific segfault fastest.
