# Testing Guide - P(Doom) Quality Assurance

**Philosophy**: Catch errors before they reach production. Test early, test often.

This guide establishes rigorous testing protocols to prevent issues like v0.10.5's parse error from reaching users.

---

## Quick Reference

```bash
# Before every push to main
python scripts/test_before_push.py

# Before creating a release
python scripts/pre_build_validation.py --full

# Quick sanity check
python scripts/pre_build_validation.py --quick
```

---

## Testing Levels

### Level 1: Fast Checks (< 30 seconds)
**When**: Before every commit
**Command**: `python scripts/pre_build_validation.py --quick`

Checks:
- CHECKED GDScript parse errors
- CHECKED Scene file structure (.tscn format validation)
- CHECKED Missing resources
- CHECKED Autoload script loading

### Level 2: Standard Checks (< 2 minutes)
**When**: Before pushing to main
**Command**: `python scripts/test_before_push.py`

Includes Level 1 +:
- CHECKED Godot unit tests (GUT framework)
- CHECKED Export preset configuration
- CHECKED Uncommitted changes warning
- CHECKED Python unit tests (if any)

### Level 3: Full Validation (< 5 minutes)
**When**: Before creating a release tag
**Command**: `python scripts/pre_build_validation.py --full`

Includes Level 1 & 2 +:
- CHECKED Game initialization test
- CHECKED Scene transition testing
- CHECKED Full integration tests

---

## Local Development Workflow

### 1. Daily Development

```bash
# Make changes to code
# ...

# Test before committing
python scripts/pre_build_validation.py --quick

# If all passes
git add .
git commit -m "Your changes"
```

### 2. Before Pushing to Main

```bash
# Run full local test suite
python scripts/test_before_push.py

# If all passes
git push origin main
```

### 3. Creating a Release

```bash
# Ensure all tests pass
python scripts/pre_build_validation.py --full

# Tag the release
git tag v0.10.7
git push origin v0.10.7

# GitHub Actions will run the same validation automatically
```

---

## CI/CD Integration

### Automatic Checks

Every release build now includes:

1. **Pre-Build Validation** (new!)
   - Runs `scripts/pre_build_validation.py --quick`
   - Blocks build if validation fails
   - Logs are available in GitHub Actions

2. **Historical Data Validation** (existing)
   - Validates JSON data files
   - Creates triage issues on failure

3. **Build Process** (existing)
   - Only runs if validation passes

### GitHub Actions Workflow

```yaml
- name: Run Pre-Build Validation
  run: |
    python scripts/pre_build_validation.py --godot "$(which godot)" --quick
    if [ $? -ne 0 ]; then
      echo "::error::Build validation checks did not pass"
      exit 1
    fi
```

---

## Common Issues and Fixes

### Parse Errors in GDScript

**Symptom**: `Parse Error: ...` in validation output
**Fix**: Open the file in Godot editor, fix syntax error, save
**Prevention**: Run quick checks before committing

### Scene File Corruption

**Symptom**: `sub_resource after node` or `Unknown tag 'sub_resource'`
**Fix**: Open scene in Godot editor, press Ctrl+S to resave
**Prevention**: Never manually edit .tscn files
**Root Cause**: .tscn files have strict ordering:
```
1. [gd_scene] header
2. All [ext_resource]
3. All [sub_resource]
4. All [node]
```

### Missing Resources

**Symptom**: `Failed loading resource: res://...`
**Fix**: Verify file exists or update references
**Prevention**: Use Godot editor for refactoring

### Autoload Failures

**Symptom**: `Failed to create an autoload`
**Fix**: Check script for parse errors, verify path in project.godot
**Prevention**: Test after adding new autoloads

---

## Writing Godot Unit Tests

### Using GUT (Godot Unit Test)

1. **Install GUT**:
   - Download from https://github.com/bitwes/Gut
   - Place in `godot/addons/gut/`

2. **Create Test Script**:
```gdscript
# godot/tests/unit/test_game_manager.gd
extends GutTest

func test_game_initialization():
    var game_manager = GameManager.new()
    assert_not_null(game_manager, "GameManager should initialize")

func test_turn_increment():
    var game_manager = GameManager.new()
    game_manager.advance_turn()
    assert_eq(game_manager.current_turn, 1, "Turn should increment")
```

3. **Run Tests**:
```bash
python scripts/pre_build_validation.py --full
```

---

## Python Unit Tests

For Python scripts (build automation, validation, etc.):

```python
# tests/test_validation.py
import pytest
from scripts.pre_build_validation import PreBuildValidator

def test_validator_initialization():
    validator = PreBuildValidator(Path("."), Path("godot"))
    assert validator is not None

def test_scene_validation():
    # Test scene file structure validation
    pass
```

Run with:
```bash
pytest tests/ -v
```

---

## Emergency Procedures

### If CI/CD Validation Fails

1. **Review the logs** in GitHub Actions
2. **Reproduce locally**: `python scripts/pre_build_validation.py --quick`
3. **Fix the issue**
4. **Test locally**: Ensure validation passes
5. **Push fix**: `git push`
6. **Re-run release** if needed

### If a Bad Build Gets Through

1. **Immediately** delete the GitHub release
2. **Create hotfix branch**
3. **Fix the issue** and test thoroughly
4. **Run full validation**: `python scripts/pre_build_validation.py --full`
5. **Create new patch release** (e.g., v0.10.7)

---

## Best Practices

### DO:
- CHECKED Run quick checks before every commit
- CHECKED Run full checks before pushing to main
- CHECKED Test locally before creating release tags
- CHECKED Use Godot editor for scene editing (never manual)
- CHECKED Write unit tests for critical game logic

### DON'T:
- FAILED Manually edit .tscn files
- FAILED Skip validation to "save time"
- FAILED Push directly to main without testing
- FAILED Use `--no-verify` on commits (unless absolutely necessary)
- FAILED Rely solely on CI/CD to catch errors

---

## Future Improvements

### Planned:
1. **Integration Tests**: Full game playthrough automation
2. **Performance Tests**: Frame rate and memory benchmarks
3. **Visual Regression Tests**: Screenshot comparison
4. **Save/Load Tests**: Game state persistence validation
5. **Pre-commit Git Hook**: Automatic validation on commit

### Wishlist:
- Automated playtesting bot
- Achievement unlock validation
- Balance testing framework
- Multiplayer stress testing

---

## Lessons from v0.10.5 Incident

**What Went Wrong**:
- Merge conflict left duplicate variable declaration
- No automated parse error detection
- No scene file structure validation
- Build succeeded but game was unplayable

**What We Fixed**:
- CHECKED Added comprehensive pre-build validation
- CHECKED Automated GDScript parse error detection
- CHECKED Scene file structure validation
- CHECKED Integration with CI/CD pipeline
- CHECKED Local testing workflow

**Result**: These errors will now be caught in < 30 seconds during local development, not after users download the release.

---

## Contact & Support

Questions about testing?
- Check this guide first
- Review validation output for hints
- Create an issue with the `testing` label
- Ask in #dev channel

Remember: **Testing is not overhead, it's insurance against production failures.**
