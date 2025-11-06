# Release Scripts

This directory contains scripts for managing P(Doom) releases.

## Quick Start

For a new release (e.g., v0.10.2):

```bash
# 1. Bump version across all files
bash scripts/bump_version.sh 0.10.2

# 2. Review and update CHANGELOG.md manually

# 3. Commit changes
git add .
git commit -m "chore: Bump version to v0.10.2"
git push origin main

# 4. Create and push tag
git tag v0.10.2
git push origin v0.10.2

# 5. Export from Godot to builds/windows/v0.10.2/

# 6. Package and release
bash package_release.sh v0.10.2
bash create_github_release.sh v0.10.2
```

## Scripts

### `bump_version.sh`
Updates version numbers across:
- `godot/project.godot`
- Release scripts
- Reminds you to update CHANGELOG.md

**Usage:**
```bash
bash scripts/bump_version.sh <version>
# Example: bash scripts/bump_version.sh 0.10.2
```

### `package_release.sh` (root)
Creates distributable .zip package with:
- Game executable (.exe)
- Game data (.pck)
- README.txt
- CHANGELOG.txt
- Optional debug console .exe

**Usage:**
```bash
bash package_release.sh [version]
# Example: bash package_release.sh v0.10.2
# Default: v0.10.1
```

### `create_github_release.sh` (root)
Creates GitHub release and uploads package.

**Usage:**
```bash
bash create_github_release.sh [version]
# Example: bash create_github_release.sh v0.10.2
# Default: v0.10.1
```

## Automation

### GitHub Actions

**Pre-Release Checks** (`.github/workflows/pre-release-checks.yml`)
- Triggered on version tag push
- Validates CHANGELOG updated
- Checks version consistency
- Runs tests
- Creates issue if validation fails

**Release Reminder** (`.github/workflows/release-reminder.yml`)
- Triggered on version tag push
- Creates issue with release checklist
- Posts reminder for post-release tasks

### Release Checklist

See `.github/RELEASE_CHECKLIST.md` for comprehensive release checklist covering:
- Pre-release validation
- Export & packaging
- Testing
- GitHub release
- Post-release tasks

## Archive

Completed releases are archived in `archive/releases/<version>/` including:
- Release notes
- Version-specific scripts
- Issue resolutions
- Quick reference guides

## Tips

1. **Always test locally first**: Extract the .zip and test on a clean Windows machine
2. **Version format**: Use `v0.10.1` format (with 'v' prefix) for tags
3. **CHANGELOG**: Keep `[Unreleased]` section for ongoing work
4. **Rollback**: If issues found, delete release (not tag), fix, and re-release

## Future Improvements

- [ ] Automate Godot export in CI/CD
- [ ] Add Mac/Linux build support
- [ ] Steam/itch.io upload automation
- [ ] Automatic tweet/announcement posting
