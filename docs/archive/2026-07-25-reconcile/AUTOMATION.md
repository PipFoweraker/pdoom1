# Automation Infrastructure Guide

**Last Updated**: 2025-01-06
**Status**: Production Ready
**Philosophy**: "Stay programmatic, add human flavor deliberately"

---

## Overview

This project includes a comprehensive automation toolkit designed to maintain code quality, manage technical debt, and streamline development workflows. All tools support dry-run modes for safety and generate detailed reports.

---

## Quick Reference

```bash
# Daily maintenance
python scripts/cleanup_project.py --clean-pyc --clean-cache

# Weekly devblog update
python scripts/devblog_automation.py --weekly-summary

# Find technical debt
python scripts/todo_tracker.py --scan --report

# Detect duplicates
python scripts/find_duplicates.py --scan --suggest

# Test before committing (automatic with pre-commit hooks)
pre-commit run --all-files
```

---

## 1. Project Cleanup (`cleanup_project.py`)

**Purpose**: Automated project hygiene and maintenance

### Features

- **Cache Cleaning**: Removes `.pyc` files and `__pycache__` directories
- **Session Archiving**: Archives session notes older than 180 days
- **Orphan Detection**: Finds files that don't fit project structure
- **Duplicate Detection**: Identifies duplicate files by content hash
- **Safety**: Dry-run mode prevents accidental deletions

### Usage

```bash
# Dry-run (recommended first)
python scripts/cleanup_project.py --dry-run --clean-pyc --clean-cache

# Execute cleanup
python scripts/cleanup_project.py --clean-pyc --clean-cache

# Archive old session notes
python scripts/cleanup_project.py --archive-old

# Full cleanup
python scripts/cleanup_project.py --all

# Find orphaned files and duplicates
python scripts/cleanup_project.py --find-orphans --find-duplicates
```

### Options

- `--dry-run`: Preview changes without executing
- `--clean-pyc`: Remove .pyc files
- `--clean-cache`: Remove cache directories (__pycache__, .pytest_cache, etc.)
- `--archive-old`: Archive old session notes (>180 days)
- `--find-orphans`: Detect files outside standard structure
- `--find-duplicates`: Scan for duplicate files
- `--all`: Run all cleanup tasks

### Output

```
Project Cleanup Report
======================

Cache Cleanup:
  .pyc files removed: 15
  __pycache__ dirs removed: 8
  Space freed: 245 KB

Session Archiving:
  Sessions archived: 3
  Target: docs/archive/sessions/

Orphaned Files: 2 detected
  - scripts/old_debug.py (no references)
  - tests/abandoned_test.gd (no imports)

Recommendations:
  - Review orphaned files for removal
  - Run duplicate detection monthly
```

---

## 2. Dev Blog Automation (`devblog_automation.py`)

**Purpose**: Programmatic development blog with structured metadata

### Features

- **Commit Extraction**: Parses git history for changes
- **Auto-Categorization**: Classifies commits (feature, bugfix, ui-ux, docs, test, refactor, chore, perf)
- **Issue Tracking**: Extracts GitHub issue references (#123)
- **Contributor Attribution**: Tracks all contributors
- **Structured Output**: YAML frontmatter + Markdown content
- **Searchable Index**: JSON index for filtering and search
- **Weekly Summaries**: Automated week-in-review generation
- **Publishing Export**: Clean format for blog publishing

### Usage

```bash
# Generate entry from recent commits
python scripts/devblog_automation.py --from-commits HEAD~10..HEAD

# Generate weekly summary
python scripts/devblog_automation.py --weekly-summary

# Manually add entry (opens editor)
python scripts/devblog_automation.py --add-entry

# Export for publishing
python scripts/devblog_automation.py --export
```

### Options

- `--from-commits RANGE`: Generate entry from commit range (e.g., HEAD~5..HEAD)
- `--add-entry`: Manually add entry (opens editor)
- `--weekly-summary`: Generate weekly summary
- `--export`: Export all entries for publishing

### Output Format

```markdown
---
title: "Development Update - Week of 2025-01-06"
date: 2025-01-06
categories: ["feature", "ui-ux", "chore"]
issues: [434, 436]
contributors: ["Claude", "User"]
---

## Summary

This week focused on UI enhancements and project automation...

## Changes

### Features
- Implemented upgrades system (#434)
- Added player feedback improvements (#436)

### Automation
- Created comprehensive cleanup toolkit
- Deployed devblog automation system

## Stats
- Commits: 8
- Files Changed: 350
- Lines Added: 1,500
- Lines Removed: 100,000
```

### JSON Index

```json
{
  "entries": [
    {
      "date": "2025-01-06",
      "title": "Development Update - Week of 2025-01-06",
      "categories": ["feature", "ui-ux", "chore"],
      "issues": [434, 436],
      "contributors": ["Claude", "User"],
      "file": "docs/devblog/2025-01-06-weekly.md"
    }
  ]
}
```

---

## 3. TODO Tracker (`todo_tracker.py`)

**Purpose**: Scan codebase for action items and technical debt

### Features

- **Multi-Format**: Detects TODO, FIXME, HACK, NOTE, XXX, BUG comments
- **Priority Detection**: Auto-prioritizes by keywords
  - High: critical, urgent, asap, security, bug
  - Low: nice, maybe, consider, optional
  - Medium: everything else
- **Context Tracking**: Identifies function/class containing the comment
- **File Hotspots**: Shows files with most TODOs
- **Export Formats**: JSON and Markdown outputs

### Usage

```bash
# Scan and display report
python scripts/todo_tracker.py --scan --report

# Export as JSON for CI/CD
python scripts/todo_tracker.py --scan --export-json todos.json

# Export as Markdown for docs
python scripts/todo_tracker.py --scan --export-md docs/TODOS.md

# Scan specific extensions
python scripts/todo_tracker.py --scan --extensions .py .gd .md
```

### Options

- `--scan`: Scan codebase for TODO comments
- `--report`: Generate formatted console report
- `--export-json FILE`: Export as JSON
- `--export-md FILE`: Export as Markdown
- `--extensions EXT...`: File extensions to scan (default: .py .gd .gdscript .md)

### Output

```
TODO Tracker Report
===================

Total: 47 items
  High Priority: 8
  Medium Priority: 32
  Low Priority: 7

By Type:
  TODO: 35
  FIXME: 8
  HACK: 3
  NOTE: 1

HIGH PRIORITY ITEMS
-------------------

[FIXME] godot/scripts/core/game_state.gd:245
  Context: calculate_doom
  Security: Input validation missing for user-provided doom values

[TODO] godot/scripts/ui/main_ui.gd:567
  Context: _on_action_selected
  Critical: Add error handling for invalid action IDs

FILES WITH MOST TODOs
---------------------

  12 - godot/scripts/ui/main_ui.gd
   8 - godot/scripts/core/turn_manager.gd
   6 - godot/scripts/core/actions.gd
```

### Markdown Export

```markdown
# TODO Tracker Report

Generated: 2025-01-06

Total: 47 items

## HIGH Priority (8 items)

### [FIXME] `godot/scripts/core/game_state.gd:245`

**Context:** `calculate_doom`

Security: Input validation missing for user-provided doom values

---
```

---

## 4. Duplicate File Detector (`find_duplicates.py`)

**Purpose**: Identify and consolidate duplicate files

### Features

- **Content Hashing**: MD5 hashing for accurate duplicate detection
- **Size Filtering**: Minimum file size threshold (default: 1KB)
- **Smart Ignoring**: Skips build artifacts, caches, virtual environments
- **Consolidation Suggestions**: Recommends which file to keep
- **Canonical Locations**: Prefers `src/`, `godot/scripts/`, `shared/`
- **Wasted Space Calculation**: Shows potential space savings

### Usage

```bash
# Scan for duplicates
python scripts/find_duplicates.py --scan --report

# Get consolidation suggestions
python scripts/find_duplicates.py --scan --suggest

# Export as JSON for batch processing
python scripts/find_duplicates.py --export-json duplicates.json

# Use custom ignore list
python scripts/find_duplicates.py --scan --ignore-list known_duplicates.txt

# Change minimum file size (bytes)
python scripts/find_duplicates.py --scan --min-size 2048
```

### Options

- `--scan`: Scan directory for duplicates
- `--report`: Generate duplicate report
- `--suggest`: Suggest consolidation actions
- `--export-json FILE`: Export as JSON
- `--ignore-list FILE`: File with paths to ignore
- `--min-size BYTES`: Minimum file size to check (default: 1024)

### Output

```
Duplicate Files Report
======================

Found 5 groups of duplicates
Total duplicate files: 8
Total wasted space: 1,245,678 bytes (1.19 MB)

DUPLICATE GROUPS
----------------

Group 1: 3 copies (45,678 bytes each, 91,356 bytes wasted)
  Hash: a1b2c3d4e5f6...
    - godot/scripts/utils/helper.gd
    - archived/old_scripts/helper.gd
    - tests/fixtures/helper.gd

CONSOLIDATION SUGGESTIONS
--------------------------

[ACTION] Keep: godot/scripts/utils/helper.gd
  Remove:
    - archived/old_scripts/helper.gd
    - tests/fixtures/helper.gd
```

### Ignore List Format

```
# known_duplicates.txt
# Intentional duplicates - don't report
tests/fixtures/sample_data.json
docs/examples/tutorial_code.gd
```

---

## 5. Editor Configuration (`.editorconfig`)

**Purpose**: Cross-editor consistency for all contributors

### Configuration

```ini
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4
max_line_length = 100

[*.gd]
indent_style = tab
indent_size = 4

[*.{yaml,yml,json}]
indent_style = space
indent_size = 2
```

### Supported Editors

- VS Code (native support)
- PyCharm/IntelliJ IDEA (native support)
- Sublime Text (via EditorConfig plugin)
- Vim/Neovim (via editorconfig-vim)
- Emacs (via editorconfig-emacs)

---

## 6. Pre-Commit Hooks (`.pre-commit-config.yaml`)

**Purpose**: Automated quality checks before commits

### Configured Hooks

1. **black** - Python code formatting
2. **isort** - Import sorting
3. **ruff** - Fast Python linting
4. **trailing-whitespace** - Remove trailing whitespace
5. **end-of-file-fixer** - Ensure newline at EOF
6. **check-yaml** - YAML syntax validation
7. **check-json** - JSON syntax validation
8. **mixed-line-ending** - Enforce LF line endings

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Usage

```bash
# Automatic (runs on git commit)
git commit -m "Your message"
# Hooks run automatically, commit fails if checks fail

# Manual execution
pre-commit run --all-files

# Update hooks
pre-commit autoupdate

# Skip hooks (emergency only)
git commit --no-verify -m "Emergency fix"
```

### Custom Hooks

Add project-specific hooks in `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: no-legacy-code-changes
      name: Prevent archive/ directory changes
      entry: scripts/hooks/check_archive.sh
      language: script
      pass_filenames: false
      # Prevents accidental modification of archived legacy code
```

---

## Integration with Development Workflow

### Daily Development

```bash
# Morning: Clean up overnight cache files
python scripts/cleanup_project.py --clean-pyc --clean-cache

# During work: Pre-commit hooks run automatically
git commit -m "feat: Add new feature"

# End of day: Check for TODOs added
python scripts/todo_tracker.py --scan --report
```

### Weekly Maintenance

```bash
# Monday: Generate weekly devblog
python scripts/devblog_automation.py --weekly-summary

# Wednesday: Check for duplicates
python scripts/find_duplicates.py --scan --suggest

# Friday: Archive old sessions
python scripts/cleanup_project.py --archive-old
```

### Monthly Cleanup

```bash
# Full project cleanup
python scripts/cleanup_project.py --all

# Export devblog for publishing
python scripts/devblog_automation.py --export
```

### CI/CD Integration

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install pre-commit

      - name: Run pre-commit
        run: pre-commit run --all-files

      - name: Check for high-priority TODOs
        run: |
          python scripts/todo_tracker.py --scan --export-json todos.json
          # Fail if >10 high-priority TODOs
          python -c "import json; todos = json.load(open('todos.json')); high = [t for t in todos['todos'] if t['priority'] == 'high']; exit(1 if len(high) > 10 else 0)"

      - name: Detect duplicates
        run: python scripts/find_duplicates.py --scan --export-json dupes.json
```

---

## Troubleshooting

### Pre-commit hooks failing

```bash
# Update hooks to latest versions
pre-commit autoupdate

# Clear cache and reinstall
pre-commit clean
pre-commit install

# Run specific hook
pre-commit run black --all-files
```

### Cleanup script removing important files

```bash
# Always use dry-run first
python scripts/cleanup_project.py --dry-run --clean-pyc --clean-cache

# Check what would be archived
python scripts/cleanup_project.py --dry-run --archive-old

# Restore from archive if needed
cp docs/archive/sessions/SESSION_X.md docs/sessions/2024-2025/
```

### Devblog not finding commits

```bash
# Check git log
git log --oneline --since="7 days ago"

# Verify commit range
python scripts/devblog_automation.py --from-commits HEAD~10..HEAD

# Export devblog
python scripts/devblog_automation.py --export
```

### TODO tracker missing comments

```bash
# Verify extensions
python scripts/todo_tracker.py --scan --extensions .py .gd .gdscript .md

# Check regex pattern (in script)
# Pattern: r'#\s*(TODO|FIXME|HACK|NOTE|XXX|BUG)[:,\s]+(.*)'
```

---

## Best Practices

### 1. Always Use Dry-Run First

```bash
# Good
python scripts/cleanup_project.py --dry-run --clean
# Review output, then run without --dry-run

# Risky
python scripts/cleanup_project.py --clean
```

### 2. Keep Ignore Lists Updated

```bash
# Create ignore list for intentional duplicates
echo "tests/fixtures/sample.gd" >> duplicates_ignore.txt
python scripts/find_duplicates.py --scan --ignore-list duplicates_ignore.txt
```

### 3. Review Automation Output

```bash
# Generate reports, review, then act
python scripts/todo_tracker.py --scan --export-md TODOS.md
# Review TODOS.md
# Address high-priority items
```

### 4. Commit Automation Changes Separately

```bash
# Good
git add scripts/cleanup_project.py
git commit -m "chore: Add cleanup automation"

# Then run cleanup
python scripts/cleanup_project.py --clean
git commit -m "chore: Run automated cleanup"
```

### 5. Test Pre-Commit Hooks Before Enabling

```bash
# Install but don't enable
pip install pre-commit

# Test manually
pre-commit run --all-files

# If all pass, enable
pre-commit install
```

---

## Development Philosophy

### Programmatic First, Human Flavor Second

All automation tools follow the principle: **"Stay programmatic, add human flavor deliberately"**

- **Structured Data**: YAML frontmatter, JSON exports, consistent formats
- **Machine-Readable**: Tools output structured data for further processing
- **Human-Readable**: Reports formatted for human review
- **Extensible**: JSON/YAML outputs can be piped to other tools
- **Auditable**: All operations logged and traceable

### Example Workflow

```bash
# 1. Automation generates structured data
python scripts/devblog_automation.py --weekly --output devblog.md

# 2. Human reviews and adds flavor
# Edit devblog.md, add personality, context, jokes

# 3. Automation handles publishing
python scripts/devblog_automation.py --export --publish

# Result: Structured + Personality
```

---

## Future Enhancements

### Planned Features

- **Performance Monitoring**: Track automation execution times
- **Notification System**: Slack/Discord webhooks for reports
- **AI-Assisted Prioritization**: LLM-based TODO priority adjustment
- **Dependency Tracking**: Detect and report outdated dependencies
- **Test Coverage Integration**: Link TODOs to test coverage gaps
- **Automated Changelog**: Generate CHANGELOG.md from commits

### Contributing

To add new automation:

1. Create script in `scripts/`
2. Follow naming convention: `verb_noun.py`
3. Include `--dry-run` mode
4. Add comprehensive `--help` text
5. Document in this file
6. Add tests in `tests/automation/`
7. Update pre-commit hooks if needed

---

## Support

For issues or questions:

1. Check [GitHub Issues](https://github.com/yourusername/pdoom1/issues)
2. Review automation logs in `logs/automation/`
3. Run with `--verbose` flag for debugging
4. Check this documentation for troubleshooting

---

**Last Updated**: 2025-01-06
**Version**: 1.0.0
**Maintainer**: P(Doom) Development Team
