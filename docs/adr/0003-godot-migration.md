<!--
status: accepted
date: 2026-06-30
deciders: Pip
-->

# ADR-0003: Runtime — migrate from pygame/Python to Godot 4.5.1 / GDScript

- **Status:** Accepted (record of a migration completed earlier; formalised here)
- **Date:** 2026-06-30 (migration code-complete ~November 2025; pygame debris archived June 2026)
- **Deciders:** Pip

## Context

P(Doom) began as a Python application using **pygame** for its GUI, with code under `src/`, an entry
point `main.py`, and UI in `ui.py`. The project migrated to the **Godot** engine. The new game lives
entirely under `godot/` (GDScript, JSON data, GUT tests). The legacy pygame/Python tree was archived
to `archive/legacy-pygame/` and `archive/legacy-python-src/` (`a84ec29`, with stragglers in `a1734a0`,
June 2026); it is no longer imported by live code.

Because the migration's *cleanup* lagged the *code* by months, many docs and CI steps continued to
describe the pygame runtime long after it was dead — the single largest source of documentation drift
in the repo.

## Decision

**Godot 4.5.1 (standard build) + GDScript is the sole game runtime.** JSON drives game content; GUT is
the test framework. **Python is retained only for tooling and CI scripts**, with a **3.11 baseline**
(`pyproject.toml`). References to `src/`, `main.py`, `ui.py`, `pip install pygame`,
`python -m unittest`, or `src/services/version.py` describe the retired build and are wrong for the
current game.

Authoritative current sources: `CONTRIBUTING.md` (setup/workflow) and
`docs/developer/ARCHITECTURE.md` (architecture).

## Consequences

- Many docs needed de-pygaming. Done so far (`#539`): `.github/copilot-instructions.md` (full rewrite)
  and `docs/DEVELOPERGUIDE.md` (setup section + under-revision banner). Remaining pygame-era
  `docs/game-design/*` analysis docs are slated for archival, superseded by code + GAME_DESIGN_CANON.
- The `archive/legacy-pygame/**` tree is kept for history only and must not be revived or maintained.
- A pre-commit hook ("Ensure pygame/ directory is not added") guards against reintroducing the old tree.
- Tooling scripts must stay Python-3.11-compatible (enforced by the CI syntax gate).
