# Release ledger -- GENERATED, do not hand-edit

Regenerate with `python tools/check_release_ledger.py --write`. `--check` blocks stale commits.

One row per value `version.txt` has ever held, with the ladder epoch and featured seed that were live at the moment it was bumped. The board key is `(seed, ladder)` -- it is keyed on the ladder, not the binary, so it does NOT move with a patch version.

**The seed column is the seed at the BUMP, which is not always the seed in the CUT.** v0.14.3 is the worked example: `version.txt` went to 0.14.3 at 07:47 on 2026-08-23 with the seed still reading `weekly-2026-w34`'s predecessor, and the roll landed at 13:44 the same day. Read this column as *what was true when the number was claimed*, and read the build stamp inside the `.pck` for what actually shipped.

| Version | Bumped | Ladder | Seed at bump | Tag | GitHub release |
|---|---|---|---|---|---|
| 0.11.0 | 2025-12-13 | UNKNOWN | UNKNOWN | v0.11.0 | 2025-12-07 |
| 0.12.0 | 2026-07-22 | UNKNOWN | UNKNOWN | v0.12.0 | 2026-07-22 |
| 0.13.0 | 2026-07-24 | L2 | weekly-2026-w30 | v0.13.0 | 2026-07-24 |
| 0.13.1 | 2026-07-25 | L2 | weekly-2026-w30 | v0.13.1 | 2026-07-26 |
| 0.13.2 | 2026-07-29 | L3 | weekly-2026-w30 | v0.13.2 | 2026-07-31 |
| 0.14.0 | 2026-08-07 | L4 | weekly-2026-w32 | v0.14.0 | 2026-08-07 |
| 0.14.1 | 2026-08-08 | L4 | weekly-2026-w32 | v0.14.1 | 2026-08-07 |
| 0.14.2 | 2026-08-21 | L5 | weekly-2026-w33 | v0.14.2 | 2026-08-21 |
| 0.14.3 | 2026-08-23 | L6 | weekly-2026-w33 | v0.14.3 | 2026-08-24 |
| 0.14.4 | 2026-08-29 | L6 | weekly-2026-w35 | v0.14.4 | 2026-08-28 |
