# Summary

Explain what this PR changes at a high level. Keep it focused and scoped.

# Scope

- What modules/files are affected?
- What is intentionally out of scope (non-goals)?

# Rationale

Why is this change needed? Reference the refactor plan and the specific phase/step.

# Risk Assessment

- Potential regressions and why
- Mitigations in this PR (facades, adapters, feature flags, tests)

# Test Plan

- Unit tests added/updated
- Manual smoke steps:
  - [ ] Launch game
  - [ ] Toggle audio settings
  - [ ] Toggle fullscreen/windowed
  - [ ] Play basic loop (earn/spend)
  - [ ] Trigger a popup/event (enhanced events flag remains OFF unless explicitly tested)
  - [ ] Save/load works; legacy paths still recognised (if relevant)

# Rollout / Backout

- Rollout plan (flags/defaults if any)
- Backout plan (revert strategy, compatibility notes)

# Checklist

- [ ] Small, focused PR
- [ ] Imports are absolute (pdoom1.*)
- [ ] Public interfaces unchanged or have compatibility adapters
- [ ] No runtime artefacts committed
- [ ] Lints/formatting pass
- [ ] Tests green
- [ ] Updated docs/notes if needed