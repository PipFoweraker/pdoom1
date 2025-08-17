# Repository Refactor and Tidy Plan

Status: Draft (actively updated as we proceed)
Target Integration Branch: `refactor/tidy-structure`
Owners: @PipFoweraker (review), @copilot (implementation support)
Spelling: UK (organisation, behaviour, modularisation, initialise)
Scope: Structure, organisation, configuration wiring, and incremental modularisation with high test confidence and minimal regressions.

## Goals

- Establish a clean, conventional repository layout to improve maintainability, discoverability, and onboarding.
- Split monolithic modules (ui.py, game_state.py) into cohesive, testable submodules with clear responsibilities.
- Stabilise data models (e.g., Action, Upgrade, Event, EmployeeSubtype) via typed dataclasses to reduce dict-shape bugs.
- Centralise runtime config and feature flags (e.g., enhanced events, onboarding/tutorial toggles) in config_manager.
- Normalise runtime file locations (high scores, onboarding progress) to a user data directory and remove them from VCS.
- Consolidate logging/error tracking through a single service (game_logger), retiring unused/duplicate trackers.

## Non-Goals

- No feature redesign or gameplay rebalancing.
- No major UI redesign (visuals remain functionally identical).
- No change to save file formats beyond path location unless necessary (adapter layers if required).
- No immediate performance optimisation beyond obvious wins from modularisation.

## Guardrails and Risk Mitigation

- Drive-by refactors are discouraged; each PR must be small, scoped, and reversible.
- Maintain backwards-compatible facades during splits (e.g., GameState facade delegates to subsystems).
- Feature flags for new pathways (e.g., enhanced events) default to current behaviour until validated by tests.
- Runtime paths: introduce a compatibility layer to read old paths if present; migrate data quietly once.
- Mandatory test plan in every PR; smoke test checklists for UI and core gameplay.
- CI gates: linting, type checks (incremental), and coverage to ensure no blind spots are added.

## Proposed Target Structure (incremental)

- pdoom1/
  - core/
    - game_state/ (facade + subsystems: economy.py, staff.py, research.py, events.py, upgrades.py, persistence.py)
    - actions.py
    - action_rules.py
    - opponents.py
    - end_game_scenarios.py
    - productive_actions.py
    - employee_subtypes.py
  - ui/
    - overlay_manager.py
    - components/ (common primitives)
    - screens/ (main_menu.py, in_game_hud.py, overlays.py, loading.py, audio_menu.py)
  - services/
    - config_manager.py
    - sound_manager.py
    - game_logger.py
    - bug_reporter.py
    - error_tracker.py (temporary; target: consolidate or remove)
    - keyboard_shortcuts.py
    - version.py
  - features/
    - onboarding.py
    - visual_feedback.py
  - assets/
    - images/
    - schemas/
    - data/ (fixtures only; no runtime state)
  - cli.py (or __main__.py for `python -m pdoom1` entry)
- tests/ (aligned with new module boundaries)
- docs/ (this file and any developer notes)
- .github/
  - PULL_REQUEST_TEMPLATE/refactor.md
- pyproject.toml (fmt/lint/type/test config)
- .gitignore (exclude runtime data and caches)

## Phased Plan (each phase = 1–3 small PRs)

0) Prep and Baselines
- Add/refine .gitignore to exclude runtime artefacts (e.g., local_highscore.json, onboarding_progress.json, saves/, cache/).
- Establish coverage baseline; document smoke test steps.
- Add pre-commit hooks for ruff/black/isort (non-blocking initially) and mypy in "permissive" mode on new modules only.

1) Assets and Runtime Paths
- Move static assets to assets/images/, schemas to assets/schemas/.
- Introduce a runtime data directory using platform app dirs (e.g., ~/.pdoom1/ or OS-specific) for high scores and onboarding progress.
- Implement a persistence adapter that:
  - reads old paths if present (compat shim),
  - writes to new runtime directory,
  - warns once if migration occurred.

2) Config Wiring and Feature Flags
- Centralise toggles in config_manager (enhanced events, tutorial visibility, audio defaults, fullscreen).
- Ensure the "enhanced events" system is wired and gated correctly (flag default remains current behaviour until dedicated tests exist).
- Add a developer-facing README section documenting flags and defaults.

3) UI Split — Part 1 (Low Risk)
- Extract overlay_manager.py into pdoom1/ui/.
- Introduce ui/components/ with minimal primitives used by existing UI.
- Update imports with a compatibility shim to avoid broad ripple changes.

4) UI Split — Part 2 (Screens)
- Introduce ui/screens/ modules for main menu, HUD, overlays, loading, audio menu.
- Move associated rendering and handlers from the monolithic ui.py into dedicated screen modules.
- Keep the top-level UI facade to route rendering and events to the screen modules.

5) GameState Decomposition — Part 1 (Subsystems)
- Create pdoom1/core/game_state/ package.
- Move coherent subsets into modules: economy.py, staff.py, research.py, events.py, upgrades.py, persistence.py.
- Provide GameState facade that delegates to subsystems without changing external interface.

6) Data Models
- Introduce dataclasses for Action, Upgrade, Event, EmployeeSubtype.
- Provide adapters to/from legacy dicts so existing code continues to work during transition.
- Incrementally update call sites starting with lowest-risk modules (tests first).

7) Logging and Error Tracking
- Standardise on game_logger for structured logs.
- If error_tracker is unused, deprecate and remove; otherwise adapt it under services and unify pipeline.
- Ensure bug_reporter integration remains intact and covered by tests.

8) Cleanup and Dead Code
- Remove or relocate: demo_onboarding.py (to examples or delete), orphaned schemas/data, redundant screenshots.
- Explicitly ignore/save user data outside VCS.
- Confirm no modules are orphaned via static analysis (vulture/pyflakes).

9) Packaging and Entry Point
- Add __init__.py where needed; switch to absolute imports.
- Provide python -m pdoom1 entry point or cli.py script.
- Update README/Player Guide to reflect new structure paths where relevant.

## Testing and Validation

- Expand/adjust tests to follow new structure; keep existing tests green at each step.
- Coverage should not regress; subsystems and adapters get unit tests.
- Manual smoke tests per PR:
  - Start game, toggle audio, change fullscreen, play basic loop.
  - Trigger events, test hiring dialog, verify popups (enhanced events off by default).
  - Save/load paths work; legacy files auto-detected.

## Rollback and Backout

- Each PR must be revertible without impacting unrelated systems.
- Facades/adapters remain in place until the end of Phase 6 to ensure compatibility.
- If a split introduces instability, back out the split PR and file a follow-up to address blockers.

## Risks and Mitigations

- Import churn and circular dependencies → phased splits with facades; prefer absolute imports.
- Path migration bugs → read-old/write-new adapter; add log + one-time user message; tests cover both locations.
- UI regressions from splits → screen-level smoke tests; small PRs; keep UI facade stable.
- Hidden dead code relied upon in edge cases → runtime telemetry/log review; enable vulture static scan to check suspected unused.

## Naming and Conventions

- Branches: `refactor/*`, `chore/*`, `docs/*`
- Commits: Conventional prefix (docs:, chore:, refactor:, feat: only if no behaviour change risk)
- Imports: absolute within package (pdoom1.*)
- Types: dataclasses for structured data; use TypedDict only as temporary adapters.

## Success Metrics

- Reduced mean time to locate module by responsibility.
- Fewer regressions associated with UI and GameState changes (tracked across releases).
- Improved coverage in pdoom1/core/game_state and pdoom1/ui.
- Faster code reviews due to smaller PRs with clear scope.

## Proposed PR Sequence (high-level)

1) docs: add refactor plan and PR template
2) chore: gitignore runtime artefacts; add coverage baseline notes
3) chore: introduce runtime data dir + persistence adapter (read old, write new)
4) refactor(ui): extract overlay_manager + ui/components
5) refactor(ui): introduce ui/screens and move main menu + HUD
6) refactor(core): create game_state package and move economy + staff
7) refactor(core): move events + upgrades + persistence
8) feat(types): add dataclasses for Action/Upgrade/Event/EmployeeSubtype + adapters
9) chore(logging): consolidate on game_logger; deprecate/remove error_tracker (if unused)
10) chore: remove dead code and relocate examples/assets
11) build: add entry point and absolute imports; update docs

Notes
- Runtime data location preference: use OS-specific app directories by default; allow override via PDOOM1_DATA_DIR for development.
- Enhanced events default: OFF until we add dedicated tests; when those tests land, we may default ON in a separate PR.