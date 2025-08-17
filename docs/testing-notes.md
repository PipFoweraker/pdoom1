# Testing notes: coverage baseline and smoke checks

Status: Living document (updated as we proceed)
Spelling: UK (organisation, behaviour, modularisation, initialise)
Integration branch: `refactor/tidy-structure`

## Coverage baseline

We are establishing an initial coverage baseline to prevent regressions while refactoring. The aim is steady or improving coverage in newly introduced modules, without blocking on legacy hotspots.

Recommended workflow:

- Run tests locally with coverage enabled:
  - `python -m pytest -q`
  - `coverage run -m pytest`
  - `coverage report -m`
- Treat the current reported percentage as the baseline for the repository.
- New subsystems introduced during the refactor (e.g., core/game_state/*, ui/screens/*) should include targeted unit tests and help nudge the baseline upwards.
- CI will report coverage to make deltas explicit; we will tune thresholds once the new structure stabilises.

Notes:
- Runtime data is stored in OS-specific application directories by default. For development, you may override this with the environment variable `PDOOM1_DATA_DIR`.
- The "enhanced events" feature flag remains OFF by default until dedicated tests are added; any change to the default will be made in a separate PR accompanied by tests.

## Manual smoke-test checklist (per PR)

Use this checklist for quick validation on all platforms. Keep PRs small so smoke testing stays fast.

- [ ] Launch the game
- [ ] Toggle audio settings and verify persistence
- [ ] Toggle fullscreen/windowed
- [ ] Play a short loop (earn/spend) without errors
- [ ] Trigger a popup/event and verify UI behaviour (enhanced events should remain OFF unless explicitly tested)
- [ ] Save and load; legacy save paths are recognised/migrated if present

## Guardrails

- Prefer small, reversible changes with clear scope.
- Maintain backwards-compatible facades and adapters during the split phases.
- Use absolute imports within the package (pdoom1.*).
- Keep runtime artefacts out of version control (see .gitignore).