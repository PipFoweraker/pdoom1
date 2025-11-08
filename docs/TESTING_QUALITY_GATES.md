# Testing & Quality Gate Strategy for P(Doom)

## Overview

This document outlines the comprehensive testing strategy and quality gates for the P(Doom) project, covering both the Godot game engine code and Python tooling.

## Current State Analysis

### ✅ Already Implemented
- **GUT (Godot Unit Test)** framework installed in `godot/addons/gut/`
- **Unit tests** for core systems (game_state, actions, events, turn_manager, etc.)
- **Pre-commit hooks** with Python linting (black, isort, ruff)
- **GitHub Actions CI/CD** with quality checks
- **Pre-release checks** for version consistency and CHANGELOG updates

### ❌ Gaps Identified
1. **No automated Godot test execution** in CI/CD pipeline
2. **No branch protection** requiring tests to pass before merge to main
3. **No integration tests** for UI workflows
4. **Parse errors** currently blocking test execution (duplicate variable issue)
5. **No coverage tracking** for Godot GDScript code
6. **Manual testing** not documented or checklisted

---

## Proposed Testing Strategy

### 1. Test Pyramid Structure

```
                 /\
                /  \
               / E2E\           <- Smoke tests, critical path validation
              /------\
             /        \
            / Integration\      <- Scene transitions, UI workflows, save/load
           /------------\
          /              \
         /   Unit Tests   \    <- Actions, GameState, Events, DoomSystem
        /------------------\
```

### 2. Test Categories

#### A. Unit Tests (GUT Framework)
**Location:** `godot/tests/unit/`

**Coverage:**
- Core game logic (actions, events, game state)
- Resource calculations
- RNG determinism
- Upgrade system
- Researcher system
- Doom momentum
- Rival labs

**Run Command:**
```bash
godot --headless -s godot/addons/gut/gut_cmdln.gd -gdir=res://tests/unit -gexit
```

#### B. Integration Tests
**Location:** `godot/tests/integration/`

**Coverage:**
- Scene loading and transitions
- UI state synchronization
- Save/load game state
- KeybindManager integration
- Configuration flow (welcome → pregame → main)
- Action queue management
- Event handling with user choices

**Examples:**
- Test welcome screen → config confirmation → main game flow
- Test pregame setup with custom seed → confirmation → game start
- Test Clear Queue button integration with KeybindManager

#### C. Smoke Tests
**Location:** `godot/tests/smoke/`

**Coverage:**
- Game launches without crashes
- Main menu loads
- New game starts successfully
- Can complete one full turn
- Can save and load game
- UI renders correctly

#### D. Manual Testing Checklist
**Location:** `docs/MANUAL_TEST_CHECKLIST.md`

**Required for:**
- Visual/aesthetic changes
- New UI screens
- Keybind changes
- Sound/audio features
- Platform-specific builds

---

## Quality Gates

### Gate 1: Local Development (Pre-Commit)

**Automated Checks:**
- ✅ Trailing whitespace removal
- ✅ Line ending normalization (LF)
- ✅ Python linting (black, isort, ruff)
- ✅ Large file detection
- ❌ **NEW: GDScript syntax validation**
- ❌ **NEW: Run unit tests on modified game logic files**

**Hook Enhancement:**
```yaml
# Add to .pre-commit-config.yaml
- repo: local
  hooks:
    - id: godot-syntax-check
      name: GDScript Syntax Check
      entry: python scripts/godot_syntax_check.py
      language: system
      files: \.gd$
      pass_filenames: true

    - id: godot-unit-tests
      name: Run Godot Unit Tests
      entry: python scripts/run_godot_tests.py --quick
      language: system
      files: (scripts/core/|tests/unit/).*\.gd$
      pass_filenames: false
```

**Manual Requirements:**
- Code compiles without errors
- No new GDScript warnings introduced
- Commit message follows convention

---

### Gate 2: Pull Request (Branch → Main)

**Automated CI Checks:**
1. **GDScript Compilation**
   - All .gd files compile without errors
   - No new warnings introduced

2. **Unit Tests**
   - All GUT unit tests pass (100% pass rate required)
   - No regressions in existing tests

3. **Integration Tests**
   - Critical path workflows complete successfully
   - Scene transitions work

4. **Code Quality**
   - Python linting passes
   - ASCII compliance (for web compatibility)
   - No merge conflicts

5. **Documentation**
   - CHANGELOG.md updated if user-facing changes
   - Inline documentation for new systems

6. **Version Consistency**
   - project.godot version matches expected branch version

**Manual Requirements:**
- ✅ **PR description** explains what changed and why
- ✅ **Screenshots/video** for UI changes
- ✅ **Manual testing checklist** completed (if applicable)
- ✅ **Reviewer approval** from maintainer

**GitHub Actions Workflow:**
```yaml
name: PR Quality Gates

on:
  pull_request:
    branches: [main, develop]

jobs:
  godot-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Godot
        uses: chickensoft-games/setup-godot@v1
        with:
          version: 4.5.1

      - name: Run GUT Unit Tests
        run: |
          godot --headless -s godot/addons/gut/gut_cmdln.gd \
                -gdir=res://tests/unit \
                -gexit \
                -glog=2

      - name: Check Test Results
        run: |
          if [ -f .gut_editor_config.json ]; then
            echo "Tests completed"
          else
            echo "Tests failed!"
            exit 1
          fi
```

---

### Gate 3: Release (Main → Production)

**Pre-Release Requirements:**

1. **All Tests Pass**
   - Unit tests: 100% pass
   - Integration tests: 100% pass
   - Smoke tests: 100% pass

2. **Build Validation**
   - Windows .exe builds without errors
   - Web export compiles (if applicable)
   - File size within acceptable limits

3. **Version Management**
   - Version incremented in project.godot
   - CHANGELOG.md updated with release notes
   - Git tag matches version number

4. **Documentation**
   - README.md reflects current features
   - Player guide updated if gameplay changed
   - Known issues documented

5. **Manual Testing**
   - Full playthrough on target platform(s)
   - Critical bugs resolved
   - Performance acceptable

6. **Leaderboard Integration**
   - Weekly seed generation working
   - Score submission tested (if applicable)

**Release Checklist Template:**
```markdown
## Release v0.X.X Checklist

### Code Quality
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] No GDScript errors or warnings
- [ ] Code review completed

### Build & Export
- [ ] Windows build created successfully
- [ ] Export size: ___ MB (< 100MB target)
- [ ] Packaged with package_release.sh

### Documentation
- [ ] CHANGELOG.md updated
- [ ] Version in project.godot: v0.X.X
- [ ] Git tag created: v0.X.X
- [ ] README.md reflects current state

### Manual Testing
- [ ] New game starts correctly
- [ ] Weekly seed loads properly
- [ ] Custom seed works
- [ ] Save/load functional
- [ ] UI renders correctly
- [ ] Keybinds work (default + custom)
- [ ] All major features tested

### Deployment
- [ ] Release notes written
- [ ] Builds uploaded to distribution channels
- [ ] GitHub release created
- [ ] Announcement prepared
```

---

## Implementation Plan

### Phase 1: Fix Current Issues (IMMEDIATE)
1. ✅ **Fix parse errors** in game_state.gd (duplicate `purchased_upgrades`)
2. ✅ **Fix log_exporter.gd** parse error (`state` reference)
3. ✅ **Fix main_ui.gd** missing function references
4. Run existing tests to verify they pass

### Phase 2: Enhanced Pre-Commit (WEEK 1)
1. Add GDScript syntax validation hook
2. Add quick unit test execution for modified files
3. Document hook bypass procedure (for emergencies)

### Phase 3: CI/CD Integration (WEEK 2)
1. Create GitHub Action for Godot test execution
2. Add branch protection rules requiring tests to pass
3. Set up test result reporting
4. Add test coverage tracking (if tooling available)

### Phase 4: Integration Tests (WEEK 3-4)
1. Write integration tests for critical workflows:
   - Game initialization flow
   - Configuration confirmation screen (NEW)
   - Action queue with Clear Queue button (NEW)
   - Save/load system
2. Add integration tests to CI/CD pipeline

### Phase 5: Manual Testing Framework (WEEK 4)
1. Create comprehensive manual testing checklist
2. Document platform-specific testing procedures
3. Create test game save files for various scenarios
4. Train team on testing procedures

---

## Test Execution Commands

### Local Development

**Run all unit tests:**
```bash
godot --headless -s godot/addons/gut/gut_cmdln.gd -gdir=res://tests/unit -gexit
```

**Run specific test:**
```bash
godot --headless -s godot/addons/gut/gut_cmdln.gd \
      -gdir=res://tests/unit \
      -gfile=test_game_state.gd \
      -gexit
```

**Run with verbose output:**
```bash
godot --headless -s godot/addons/gut/gut_cmdln.gd \
      -gdir=res://tests/unit \
      -glog=3 \
      -gexit
```

### CI/CD

**Full test suite (all categories):**
```bash
python scripts/run_all_godot_tests.py --ci-mode
```

**Quick smoke test:**
```bash
python scripts/run_godot_tests.py --smoke-only
```

---

## Coverage Goals

### Target Coverage by Category

- **Core Game Logic:** 80%+ (actions, game_state, events)
- **UI Layer:** 50%+ (main_ui, pregame, confirmation)
- **Utilities:** 70%+ (config, keybinds, themes)
- **Integration Flows:** 100% of critical paths

### Critical Paths Requiring Tests

1. **Game Start Flow:**
   - Welcome → Default path → Confirmation → Main game
   - Welcome → Custom seed → Pregame → Confirmation → Main game

2. **Turn Execution:**
   - Queue actions → End turn → Process results → Next turn

3. **Action Management:**
   - Queue action → Clear queue → Verify AP refunded

4. **Configuration:**
   - Change keybinds → Save → Reload → Verify
   - Change settings → Apply → Restart → Verify

---

## Testing Tools & Resources

### Godot Testing
- **GUT Framework:** `godot/addons/gut/`
- **Documentation:** https://github.com/bitwes/Gut/wiki
- **Assertions:** `assert_eq`, `assert_true`, `assert_null`, etc.

### Python Testing
- **pytest:** Unit testing framework
- **black:** Code formatting
- **ruff:** Fast linting

### CI/CD
- **GitHub Actions:** `.github/workflows/`
- **Pre-commit:** `.pre-commit-config.yaml`

---

## Rollout Strategy

### Week 1: Foundation
- Fix existing parse errors
- Document current test suite
- Create manual testing checklist
- Add basic GDScript syntax checking

### Week 2: Automation
- Set up GitHub Actions for Godot tests
- Add branch protection requiring CI pass
- Document test execution procedures

### Week 3: Expansion
- Write integration tests for new features (#436)
- Add smoke tests for critical paths
- Implement coverage tracking

### Week 4: Refinement
- Train team on testing procedures
- Iterate on quality gates based on feedback
- Optimize test execution speed

---

## Maintenance & Evolution

### Regular Activities

**Daily:**
- Run unit tests before committing
- Check pre-commit hook results

**Per Feature:**
- Write unit tests for new game logic
- Update integration tests if workflows change
- Update manual checklist if UI changes

**Per Release:**
- Complete full manual testing checklist
- Review test coverage reports
- Update testing documentation

**Monthly:**
- Review failed test trends
- Update quality gate thresholds if needed
- Refactor flaky tests

---

## Success Metrics

### Quality Indicators
- **Test Pass Rate:** >95% (target: 100%)
- **Build Success Rate:** >90%
- **Bugs Found in QA vs Production:** 10:1 ratio
- **Time to Detect Regression:** <1 day

### Process Indicators
- **PR Merge Time:** <48 hours (with tests)
- **CI Pipeline Duration:** <10 minutes
- **Test Execution Time:** <5 minutes (unit), <15 minutes (full)

---

## Questions & Next Steps

**Immediate Questions:**
1. Should we block merges to main if tests fail? (Recommendation: YES)
2. Who approves manual testing sign-off? (Recommendation: Project lead)
3. What's acceptable test coverage threshold? (Recommendation: 70% for new code)
4. Should we require tests for bug fixes? (Recommendation: YES)

**Action Items:**
1. [ ] Review this document with team
2. [ ] Fix parse errors blocking tests
3. [ ] Set up basic GitHub Actions test workflow
4. [ ] Create manual testing checklist
5. [ ] Enable branch protection on main
6. [ ] Document test writing guidelines

---

**Document Version:** 1.0
**Last Updated:** 2025-01-07
**Owner:** Project Team
**Next Review:** 2025-02-07
