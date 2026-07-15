# docs/archive/ — historical / superseded documentation

**Do not treat anything under this directory as current.** These docs are preserved for
git-history and provenance reasons only — they document the pre-workshop-1 (before
2026-07-04) and pre-Godot-migration (Python/pygame era, before the migration completed
per `docs/adr/0003-godot-migration.md`) state of the project: old planning docs, session
handoffs, bug investigations, hotfix summaries, and superseded game-design analysis.

Nothing here was deleted — everything was moved with `git mv`, so full history is
preserved and `git log --follow` still works on every file.

## Why this exists

Pip (project lead) wanted the pre-workshop-1 documentation corpus swept for two reasons:
1. **Hygiene** — stop new work accidentally cross-pollinating with stale Python-era
   mechanics, numbers, or plans that no longer describe the shipping Godot game.
2. **Confidence the good ideas were kept** — every doc in this sweep was read and its
   ideas cross-checked against current canon (`docs/game-design/DESIGN_PHILOSOPHY.md`,
   the ADR series, `docs/game-design/WORKSHOP_2_BACKLOG.md`, `docs/game-design/WORLD_AND_LORE.md`,
   `docs/balance/*`) before being archived. See `SALVAGE_REPORT.md` in this directory for
   the full record of that check, including every idea that was NOT already captured.

## Current canon lives elsewhere

For "what is this game and why," start at:
- `docs/game-design/DESIGN_PHILOSOPHY.md`
- `docs/game-design/decisions/` (ADR-0001..0016)
- `docs/game-design/WORKSHOP_2_BACKLOG.md` (the open-design-question register)
- `docs/game-design/WORLD_AND_LORE.md`
- `docs/game-design/WORKSHOP_2_BUILD_LANES.md`
- `docs/balance/*`

## Directory structure

- `game-design-pre-workshop1/` — pygame-era game-design analysis/tuning docs, and the two
  EXECUTED Fable workshop kickoff transcripts (#1, #2), superseded by the ADRs and
  `DESIGN_PHILOSOPHY.md` those workshops produced. Also `GAME_DESIGN_CANON.md`, which
  predates workshop #1 by four days and is now superseded/contradicted by ADR-0002
  (see `SALVAGE_REPORT.md`).
- `dev-sessions-pre-workshop1/` — session handoffs, completion reports, and
  project-management planning docs from the Python/pygame era.
- `issues-and-investigations-legacy/` — closed bug investigations and archived/completed
  issue write-ups from the pygame era.
- `technical-pygame-era/` — technical docs describing pygame-era systems (`src/*.py`,
  `ui.py`, `main.py`) that no longer exist post-migration.
- `architecture-pygame-era/` — pygame-era architecture/refactoring planning docs.
- `monolith-refactoring-2025-09/`, `root-docs-cleanup-2025-09-15/`,
  `session-handoffs-2025-09/`, `ui-fixes-and-improvements/` — pre-existing archive
  subtrees from an earlier (2025-09) cleanup pass; left as-is, not re-organized by this
  sweep.

There is also a much larger, older `archive/` directory (and `legacy/`) at the **repo
root** (not under `docs/`) containing the full legacy pygame codebase, scripts, and
~140 archived GitHub-issue stubs from an earlier migration effort. That directory is
intentionally out of scope for this sweep — it's mostly code, not docs, and was already
isolated by a prior cleanup. See `SALVAGE_REPORT.md` for the (light) salvage pass done
over its doc subset.
