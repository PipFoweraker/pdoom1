# Release Scripts

This directory contains scripts for managing P(Doom) releases.

> **Version single-source-of-truth (v0.11.0+):** `version.txt` (repo root) is the
> authoritative game version. After changing it, run `python tools/sync_version.py`
> to stamp the derived copies (`game_config.gd` `CURRENT_VERSION`, `project.godot`,
> `export_presets.cfg`, `welcome.tscn`). `python tools/sync_version.py --check`
> gates pre-commit AND CI and exits 1 on drift -- a silent mismatch forks the
> leaderboard board-key. Cut Windows builds with `python tools/build_release.py`
> (stamps the build and defeats the stale-export-cache trap); never hand-run a raw
> `godot --export`. See [`../tools/README.md`](../tools/README.md) for those tools.

## Quick Start

For a new release:

```bash
# 1. Bump version (version.txt is the SSOT), then stamp the derived copies
#    -- edit version.txt, then:
python tools/sync_version.py
python tools/sync_version.py --check   # must exit 0

# 2. Review and update CHANGELOG.md manually

# 3. Commit changes (stage only what you changed -- never `git add -A`)
git commit -m "chore: bump version to <version>"
git push origin main

# 4. Tag
git tag v<version>
git push origin v<version>

# 5. Build (this replaces every step 5/6 the old README described)
python tools/build_release.py
```

## Scripts

> **[!] Three release scripts documented here until 2026-08-04 did not exist or
> could not run.** Removed from this README on that date:
>
> - `bump_version.sh` -- DELETED 2026-08-04. It ran `set -e` and then
>   `sed -i ... package_release.sh`, so it hard-failed on a file that is not in
>   the repo. Superseded by `version.txt` + `tools/sync_version.py`, which this
>   README's own banner already described.
> - `package_release.sh` (root) -- never existed in this repo. Superseded by
>   `python tools/build_release.py`.
> - `create_github_release.sh` (root) -- never existed in this repo. Use
>   `gh release create`.
>
> A README documenting three commands that cannot run is the failure this sweep
> exists to stop. If you add a script here, this file is where its deadness must
> also be recorded when it goes.

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

## Logging System

Scripts use a centralized logging system (`logging_system.py`) for structured output and debugging.

### Quick Start

```python
from logging_system import get_logger, LogCategory, TimedOperation

logger = get_logger('my_script', LogCategory.BUILD)
logger.info('Starting process')

with TimedOperation(logger, 'expensive_operation'):
    # Timed code here
    pass
```

### Log Categories

| Category | Description | Directory |
|----------|-------------|-----------|
| `QUALITY` | Pre-commit hooks, linting | `logs/quality/` |
| `BUILD` | Compilation, exports | `logs/release/` |
| `VERSION` | Version bumps, changelog | `logs/release/` |
| `TESTS` | Test runs, validation | `logs/testing/` |
| `DOCS` | Documentation generation | `logs/docs/` |
| `GENERAL` | Miscellaneous | `logs/dev/` |

### Key Files

- `scripts/logging_system.py` - Core PDoomLogger class
- `logs/README.md` - Log directory structure documentation

See `logs/README.md` for log file naming conventions and retention policies.

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
