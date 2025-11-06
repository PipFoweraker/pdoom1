# Release Checklist Template

Use this checklist for every release to ensure nothing is forgotten.

## Pre-Release (Before Export)

- [ ] All target issues/features merged to main
- [ ] CHANGELOG.md updated with version and changes
- [ ] Version number updated in:
  - [ ] `godot/project.godot` (application/config/version)
  - [ ] All release scripts
- [ ] All tests passing (`pytest`)
- [ ] No GDScript warnings in Godot editor
- [ ] Game tested manually (smoke test)
- [ ] Git status clean (all changes committed)

## Export & Package

- [ ] Open Godot 4.5.1+
- [ ] Project → Export → Windows Desktop
- [ ] Export to: `builds/windows/vX.Y.Z/PDoom.exe`
- [ ] Verify both .exe and .pck files created
- [ ] Run `bash package_release.sh`
- [ ] Verify package created successfully

## Test Package

- [ ] Extract zip to clean directory
- [ ] Run PDoom.exe
- [ ] Test core gameplay:
  - [ ] Queue actions (AP tracking works)
  - [ ] Clear queue (C key works)
  - [ ] Remove individual items (✕ buttons work)
  - [ ] Commit turn (Space works)
  - [ ] Events display correctly
  - [ ] Save/load works
- [ ] Check for console errors

## GitHub Release

- [ ] Run `bash create_github_release.sh`
- [ ] Verify release created on GitHub
- [ ] Test download link works
- [ ] Release notes are correct

## Post-Release

- [ ] Update README.md with download link
- [ ] Close related issues with release note
- [ ] Commit post-release changes:
  ```bash
  git add README.md [other files]
  git commit -m "chore: Post-release updates for vX.Y.Z"
  git push origin main
  ```
- [ ] Update pdoom1.com website
- [ ] Announce on social media (if applicable)
- [ ] Create milestone for next version
- [ ] Move open issues to next milestone

## Rollback Plan (If Issues Found)

1. Delete GitHub release (DO NOT delete tag yet)
2. Fix issues locally
3. Re-export and re-package
4. Re-create GitHub release with same tag
5. Update download links if changed

## Version Number Guidelines

- **Patch (X.Y.Z)**: Bug fixes, minor tweaks
- **Minor (X.Y.0)**: New features, non-breaking changes
- **Major (X.0.0)**: Breaking changes, major overhauls

## Notes

- Keep this checklist updated as release process evolves
- Add platform-specific steps as Mac/Linux builds are added
- Consider automating more steps with GitHub Actions
