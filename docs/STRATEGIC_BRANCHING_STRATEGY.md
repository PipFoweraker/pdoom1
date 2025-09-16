# Strategic Branching Strategy for v1.0.0 Development
*Created: September 16, 2025*

## Overview

This document outlines the focused branching strategy designed to systematically address critical issues, implement quick wins, and prepare for v1.0.0 release while maintaining development organization and preventing scope creep.

## Strategic Phases

### Phase 1: STABILITY FOUNDATION (Week 1)
**Priority: Kill bugs and stop failures**

#### Critical Fix Branches
| Branch | Purpose | Effort | Priority |
|--------|---------|---------|----------|
| `fix/test-suite-segfault` | Fix segmentation fault blocking test validation | 1-2 days | CRITICAL |
| `fix/sound-system-integration` | Fix sound manager default state and integration | 4-6 hours | HIGH |
| `fix/menu-system-integration` | Restore New Player Experience menu, research actions | 4-6 hours | HIGH |
| `fix/configuration-consistency` | Reconcile starting cash values and config consistency | 2-4 hours | HIGH |

### Phase 2: QUICK WINS IMPLEMENTATION (Week 2)
**Priority: Alpha-blocking features with existing infrastructure**

#### Feature Activation Branches
| Branch | Purpose | Effort | Priority |
|--------|---------|---------|----------|
| `feature/leaderboard-activation` | Replace placeholder UI with LocalLeaderboard system | 2-4 hours | HIGH |
| `feature/player-run-logging` | Enable comprehensive logging for dev builds | 1-2 days | HIGH |
| `chore/branch-consolidation` | Merge stable work, close dead branches | 4-8 hours | MEDIUM |

### Phase 3: ARCHITECTURE & v1.0.0 PREP (Weeks 3-4)
**Priority: Backend infrastructure for stable release**

#### Refactoring Branches
| Branch | Purpose | Effort | Priority |
|--------|---------|---------|----------|
| `refactor/complete-type-annotations` | Complete remaining game_state.py type annotations | 1-2 days | MEDIUM |
| `refactor/ui-architecture-prep` | Continue UI monolith breakdown for post-1.0.0 | 3-5 days | LOW |
| `planning/post-1.0.0-roadmap` | Document post-1.0.0 features and scope reduction | 1-2 days | LOW |

## Branch Management Principles

### Naming Convention
- `fix/` - Bug fixes and critical stability issues
- `feature/` - New feature implementation or activation
- `refactor/` - Code structure improvements and architecture
- `chore/` - Development workflow and maintenance tasks
- `planning/` - Documentation and strategic planning

### Workflow Rules
1. **All branches based on `main`** - Ensures clean merge conflicts
2. **Single focus per branch** - One issue/feature per branch for clean merges
3. **Phase-based priority** - Complete Phase 1 before Phase 2, etc.
4. **Regular integration** - Merge completed branches back to main frequently
5. **Documentation requirement** - Each branch requires issue documentation

### Merge Strategy
1. **Phase 1** - Direct merge to main after testing (critical fixes)
2. **Phase 2** - PR review for feature changes (quick wins)
3. **Phase 3** - Extended review for architectural changes

## Legacy Branch Status

### Active Legacy Branches
- `fix/seed-selection-keyboard-navigation` - Complete and merge if stable
- `refactor/monolith-breakdown` - Assess and potentially merge into Phase 3
- `type-annotation-*` - Consolidate into `refactor/complete-type-annotations`

### Deprecated Branches (Target for Consolidation)
- `bug-sweep-critical-stability` - Merge scope into Phase 1 fixes
- `dead-code-analysis` - Defer to post-1.0.0
- `experimental/playground` - Archive or delete
- `hotfix/v0.4.1-*` - Assess for critical fixes, otherwise archive

## Success Metrics

### Phase 1 Success Criteria
- [ ] Test suite runs without segmentation fault
- [ ] Sound system integration tests pass
- [ ] Menu system displays correct items
- [ ] Configuration values are consistent across files

### Phase 2 Success Criteria
- [ ] Leaderboard UI functional and activated
- [ ] Comprehensive logging enabled for dev builds
- [ ] Legacy branches consolidated or archived
- [ ] Active branch count reduced to <10

### Phase 3 Success Criteria
- [ ] Type annotation coverage >90%
- [ ] UI architecture prepared for post-1.0.0 features
- [ ] Clear post-1.0.0 roadmap documented
- [ ] v1.0.0 scope finalized and stable

## Post-1.0.0 Scope Reduction

### Deferred to Post-1.0.0
- Multi-turn action delegation system (complex, 1-2 week effort)
- Advanced developer tools enhancement
- Deterministic RNG system overhaul
- Complex UI refactoring beyond critical fixes
- Website integration and automated deployment

### Maintained for 1.0.0
- Critical bug fixes and stability improvements
- Existing system activation (leaderboards, logging)
- Essential configuration and integration fixes
- Type annotation completion for core systems
- Basic UI fixes for menu and sound systems

## Branch Lifecycle Management

### Daily Workflow
1. Start day on appropriate phase branch
2. Focus on single issue until completion
3. Commit with descriptive messages referencing issues
4. Test changes using appropriate test subset
5. Document progress in commit messages

### Weekly Integration
1. Review completed branches for main merge
2. Update this strategy document with progress
3. Assess phase completion and next priorities
4. Archive or delete obsolete branches
5. Create new branches for emerging critical issues

### Risk Management
- **Critical blocker identified**: Create immediate `fix/` branch
- **Scope creep detected**: Document in `planning/post-1.0.0-roadmap`
- **Merge conflicts**: Rebase branch on latest main before merge
- **Test failures**: Block merge until tests pass on affected branches

This strategic branching approach ensures systematic progress toward v1.0.0 while maintaining code quality and preventing feature creep.
