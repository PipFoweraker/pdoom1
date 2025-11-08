---
**Title**: Tracking: Refactor/tidy-structure integration and phased refactor (UK spelling)  
**Assignees**: PipFoweraker  
**Body**:  
### Tracking: refactor/tidy-structure integration and phased refactor (UK spelling)  
  
Track the incremental refactor and tidy effort landing into the integration branch refactor/tidy-structure via small, reviewable PRs, with UK spelling, conservative defaults, and strong test discipline.  
  
---  
  
### Branch and references  
- **Integration branch:** refactor/tidy-structure  
- **Plan document:** docs/refactor-plan.md (introduced in PR #153)  
- **Preferences:**  
  - **Spelling:** UK (organisation, behaviour, modularisation, initialise)  
  - **Runtime data location:** OS-specific app directories by default; override via PDOOM1_DATA_DIR for development  
  - **Enhanced events:** default OFF until dedicated tests are added; any default flip will be in a dedicated PR  
  
---  
  
### Milestones and task list  
- [ ] PR 1: docs - add refactor plan and PR template (UK spelling) (PR #153)  
- [ ] PR 2: chore - update .gitignore to exclude runtime artefacts; document coverage baseline and smoke tests  
- [ ] PR 3: chore - introduce runtime data directory + persistence adapter (read old paths, write new; one-time migration notice)  
- [ ] PR 4: refactor(ui) - extract overlay_manager to pdoom1/ui and add ui/components/ primitives  
- [ ] PR 5: refactor(ui) - add ui/screens/ (main menu, HUD, overlays, loading, audio menu) and route via a UI facade  
- [ ] PR 6: refactor(core) - create pdoom1/core/game_state/ and move economy + staff subsystems; keep GameState facade stable  
- [ ] PR 7: refactor(core) - move events + upgrades + persistence subsystems  
- [ ] PR 8: feat(types) - introduce dataclasses for Action, Upgrade, Event, EmployeeSubtype + legacy adapters  
- [ ] PR 9: chore(logging) - consolidate on game_logger; deprecate/remove error_tracker if unused  
- [ ] PR 10: chore - remove dead code; relocate examples/assets; ensure runtime files are ignored  
- [ ] PR 11: build - add package entry point (python -m pdoom1) and absolute imports; update docs  
  
---  
  
### Guardrails and validation  
- Small, reversible PRs with clear scope and test plans  
- Facades/adapters maintain current behaviour during splits  
- Coverage must not regress; add subsystem tests as they are introduced  
- Manual smoke tests per PR (audio, fullscreen/window, basic loop, events/popups, save/load with legacy path recognition)  
  
---  
  
### Definition of done  
- New structure in place (core/ui/services/features/assets) with absolute imports  
- GameState and UI split into coherent modules with stable facades  
- Runtime data stored outside VCS in app dirs; legacy paths supported/migrated  
- Logging consolidated; dead code removed  
- Plan and README updated  
  
---  
  
### Links  
- PR 1: https://github.com/PipFoweraker/pdoom1/pull/153