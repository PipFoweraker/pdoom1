# Release Checklist for P(Doom)

This document provides a comprehensive checklist for releasing new versions of P(Doom): Bureaucracy Strategy Game.

## Pre-Release Preparation

### 1. Version Planning
- [ ] Determine version number using [Semantic Versioning](https://semver.org/)
  - **MAJOR** (X.0.0): Incompatible API changes, major gameplay overhauls
  - **MINOR** (0.X.0): Backwards-compatible functionality additions
  - **PATCH** (0.0.X): Backwards-compatible bug fixes
- [ ] Review planned features and changes for the release
- [ ] Update project roadmap and milestones if needed

### 2. Code Quality & Testing
- [ ] All features implemented and code complete
- [ ] Full test suite passes locally: `python -m unittest discover tests -v`
- [ ] No failing tests in CI/CD pipeline
- [ ] Code review completed for all new changes
- [ ] Performance testing completed (if applicable)
- [ ] Security review completed (if applicable)

### 3. Documentation Updates
- [ ] Update `version.py` with new version number
  - [ ] Update `__version__` constant
  - [ ] Update `VERSION_MAJOR`, `VERSION_MINOR`, `VERSION_PATCH`
  - [ ] Clear or update `VERSION_PRERELEASE` and `VERSION_BUILD` as needed
- [ ] Update `CHANGELOG.md`
  - [ ] Move changes from `[Unreleased]` to new version section
  - [ ] Add version number and release date
  - [ ] Ensure all significant changes are documented
  - [ ] Follow [Keep a Changelog](https://keepachangelog.com/) format
- [ ] Update `README.md` if needed
  - [ ] Version-specific installation instructions
  - [ ] New feature highlights
  - [ ] Updated requirements or dependencies
- [ ] Update `DEVELOPERGUIDE.md` if needed
  - [ ] New architecture changes
  - [ ] Updated contribution guidelines
  - [ ] New testing procedures
- [ ] Update `PLAYERGUIDE.md` if needed
  - [ ] New gameplay features
  - [ ] Updated controls or strategies
  - [ ] Bug fixes that affect gameplay

### 4. Version Consistency Verification
- [ ] Verify version consistency across all files:
  ```bash
  python -c 'from version import get_display_version; print(get_display_version())'
  python -c 'from game_state import GameState; gs = GameState('test'); print(gs.logger.game_version)'
  ```
- [ ] Check that window title shows correct version
- [ ] Verify changelog mentions correct version
- [ ] Ensure all version references are updated

## Release Process

### 5. Pre-Release Testing
- [ ] Run full test suite one final time: `python -m unittest discover tests -v`
- [ ] Manual testing of key features:
  - [ ] Game launches successfully
  - [ ] Main menu functions correctly
  - [ ] Game modes work (weekly seed, custom seed)
  - [ ] Core gameplay mechanics function
  - [ ] Event system works properly
  - [ ] Opponents system functions
  - [ ] Save/load functionality (if applicable)
  - [ ] Bug reporting system works
- [ ] Test on multiple platforms (Windows, macOS, Linux) if possible
- [ ] Verify documentation is accessible and accurate

### 6. Create Release
- [ ] Commit all changes with appropriate commit message
- [ ] Push changes to main branch
- [ ] Ensure CI/CD tests pass on main branch
- [ ] Create and push version tag:
  ```bash
  git tag -a v0.1.0 -m 'Release version 0.1.0'
  git push origin v0.1.0
  ```
- [ ] Verify GitHub Actions release workflow triggers successfully
- [ ] Review automatically generated release assets
- [ ] Update release notes if needed

### 7. Release Verification
- [ ] Download and test release assets
- [ ] Verify checksums match
- [ ] Test installation from release packages
- [ ] Confirm version number displays correctly in released version
- [ ] Check that all documentation links work correctly

## Post-Release Tasks

### 8. Communication & Documentation
- [ ] Update project README with latest release information
- [ ] Update any external documentation or websites
- [ ] Announce release on relevant channels (if applicable)
- [ ] Update project status and roadmap

### 9. Monitoring & Follow-up
- [ ] Monitor for any critical issues or bug reports
- [ ] Plan hotfix release if critical issues discovered
- [ ] Begin planning next release cycle
- [ ] Update issue tracker and project milestones

### 10. Development Preparation
- [ ] Create new `[Unreleased]` section in CHANGELOG.md
- [ ] Update development version number if using development builds
- [ ] Plan and schedule next release
- [ ] Update project roadmap and milestones

## Emergency Hotfix Process

If a critical bug is discovered after release:

1. **Immediate Assessment**
   - [ ] Assess severity and impact
   - [ ] Determine if hotfix is necessary
   - [ ] Identify fix requirements

2. **Hotfix Development**
   - [ ] Create hotfix branch from release tag
   - [ ] Implement minimal fix
   - [ ] Test fix thoroughly
   - [ ] Update version to patch increment (e.g., 0.1.0 -> 0.1.1)

3. **Hotfix Release**
   - [ ] Follow abbreviated release process
   - [ ] Update CHANGELOG.md with hotfix details
   - [ ] Tag and release hotfix version
   - [ ] Merge hotfix back to main branch

## Version Numbering Guidelines

### Semantic Versioning Rules
- **MAJOR** version changes:
  - Incompatible gameplay mechanics changes
  - Save file format changes that break compatibility
  - Major UI/UX overhauls that change core interaction patterns
  
- **MINOR** version changes:
  - New game features (events, actions, upgrades, opponents)
  - New game modes or options
  - Backwards-compatible enhancements
  - New documentation or guides
  
- **PATCH** version changes:
  - Bug fixes that don't change functionality
  - Performance improvements
  - Documentation corrections
  - Security patches

### Pre-release Versions
- **Alpha** (e.g., v0.2.0-alpha.1): Early development, major features incomplete
- **Beta** (e.g., v0.2.0-beta.1): Feature complete, testing and polishing
- **Release Candidate** (e.g., v0.2.0-rc.1): Potentially final, last-minute testing

## Release Schedule Recommendations

- **Patch releases**: As needed for critical bugs (within days/weeks)
- **Minor releases**: Monthly or bi-monthly for new features
- **Major releases**: Quarterly or as needed for significant changes

## Tools and Commands Reference

```bash
# Version verification
python -c 'from version import get_version_info; print(get_version_info())'

# Run all tests
python -m unittest discover tests -v

# Create and push tag
git tag -a v0.1.0 -m 'Release version 0.1.0'
git push origin v0.1.0

# Manual release trigger (if needed)
gh workflow run release.yml -f version=v0.1.0

# Check release workflow status
gh run list --workflow=release.yml
```

---

**Remember**: Always test thoroughly and follow this checklist completely. A good release process prevents issues and maintains user trust.