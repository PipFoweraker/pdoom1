# Documentation Organization Plan

**Date:** 2025-11-03
**Goal:** Organize remaining 28 markdown files in root directory

## Current State

28 markdown files in root (down from 39 after SESSION_* archival)

## Categorization

### 🟢 Keep in Root (8 files)
These are essential project files that belong in root:

1. `README.md` - Main project README ✓
2. `CHANGELOG.md` - Version history ✓
3. `CHANGELOG_v0.9.0.md` - Specific version changelog (consider merging?)
4. `ARCHIVE_COMPLETION_2025-11-03.md` - Recent archive summary ✓
5. `QOL_IMPROVEMENTS_2025-11-03.md` - Recent QoL summary ✓
6. `SESSION_SUMMARY_CLEANUP_QOL_2025-11-03.md` - Recent session ✓
7. `DEV_TOOLS_PORTING_ANALYSIS.md` - Important reference ✓
8. `README_OLD.md` - Archive or delete (see below)

### 🔵 Move to `godot/docs/` (5 files)
Godot-specific documentation:

1. `GODOT_README.md` → `godot/docs/README.md`
2. `GODOT_QUICKSTART.md` → `godot/docs/QUICKSTART.md`
3. `GODOT_OFFICE_CAT_ENHANCEMENT.md` → `godot/docs/features/OFFICE_CAT_ENHANCEMENT.md`
4. `GODOT_PHASE_4_SUMMARY.md` → `godot/docs/development/PHASE_4_SUMMARY.md`
5. `GODOT_PHASE_5_SUMMARY.md` → `godot/docs/development/PHASE_5_SUMMARY.md`

### 🟡 Move to `docs/summaries/` (7 files)
Historical summaries and completion reports:

1. `COMPREHENSIVE_CLEANUP_REPORT_2025-09-28.md`
2. `CRITICAL_GAMEPLAY_BUGS_FIX_SUMMARY.md`
3. `DEMO_HOTFIX_SUMMARY.md`
4. `DEMO_HOTFIXES_SUMMARY.md` (duplicate?)
5. `LIFT_AND_SHIFT_COMPLETION_SUMMARY.md`
6. `MASTER_CLEANUP_REFERENCE.md`
7. `PHASE_6_SUGGESTIONS.md`

### 🟠 Move to `docs/guides/` (4 files)
Implementation guides and references:

1. `ASSET_INTEGRATION_GUIDE.md`
2. `TERMINAL_MESSAGES_IMPLEMENTATION.md`
3. `PDOOM_DATA_INTEGRATION_PLAN.md`
4. `COPILOT_INSTRUCTIONS_UPDATE_ANALYSIS.md`

### 🔴 Move to `docs/analysis/` (1 file)
Technical analysis documents:

1. `test_failure_analysis.md`

### ⚠️ Special Cases

**`README_OLD.md`**
- Options:
  1. Archive to `archive/docs/`
  2. Delete if content is in current README
  3. Keep for historical reference

**Recommendation:** Archive it

## Proposed Directory Structure

```
pdoom1/
├── README.md                           # Main project README
├── CHANGELOG.md                        # Current changelog
├── CHANGELOG_v0.9.0.md                 # Version-specific (consider merging)
├── ARCHIVE_COMPLETION_2025-11-03.md   # Recent work summaries
├── QOL_IMPROVEMENTS_2025-11-03.md
├── SESSION_SUMMARY_CLEANUP_QOL_2025-11-03.md
├── DEV_TOOLS_PORTING_ANALYSIS.md
│
├── docs/
│   ├── guides/
│   │   ├── ASSET_INTEGRATION_GUIDE.md
│   │   ├── TERMINAL_MESSAGES_IMPLEMENTATION.md
│   │   ├── PDOOM_DATA_INTEGRATION_PLAN.md
│   │   └── COPILOT_INSTRUCTIONS_UPDATE_ANALYSIS.md
│   │
│   ├── summaries/
│   │   ├── COMPREHENSIVE_CLEANUP_REPORT_2025-09-28.md
│   │   ├── CRITICAL_GAMEPLAY_BUGS_FIX_SUMMARY.md
│   │   ├── DEMO_HOTFIX_SUMMARY.md
│   │   ├── DEMO_HOTFIXES_SUMMARY.md
│   │   ├── LIFT_AND_SHIFT_COMPLETION_SUMMARY.md
│   │   ├── MASTER_CLEANUP_REFERENCE.md
│   │   └── PHASE_6_SUGGESTIONS.md
│   │
│   └── analysis/
│       └── test_failure_analysis.md
│
├── godot/
│   └── docs/
│       ├── README.md                   # From GODOT_README.md
│       ├── QUICKSTART.md               # From GODOT_QUICKSTART.md
│       ├── features/
│       │   └── OFFICE_CAT_ENHANCEMENT.md
│       └── development/
│           ├── PHASE_4_SUMMARY.md
│           └── PHASE_5_SUMMARY.md
│
└── archive/
    └── docs/
        └── README_OLD.md
```

## Implementation Steps

### Step 1: Create Directory Structure
```bash
mkdir -p docs/guides
mkdir -p docs/summaries
mkdir -p docs/analysis
mkdir -p godot/docs/features
mkdir -p godot/docs/development
mkdir -p archive/docs
```

### Step 2: Move Godot Documentation (5 files)
```bash
git mv GODOT_README.md godot/docs/README.md
git mv GODOT_QUICKSTART.md godot/docs/QUICKSTART.md
git mv GODOT_OFFICE_CAT_ENHANCEMENT.md godot/docs/features/OFFICE_CAT_ENHANCEMENT.md
git mv GODOT_PHASE_4_SUMMARY.md godot/docs/development/PHASE_4_SUMMARY.md
git mv GODOT_PHASE_5_SUMMARY.md godot/docs/development/PHASE_5_SUMMARY.md
```

### Step 3: Move Summaries (7 files)
```bash
git mv COMPREHENSIVE_CLEANUP_REPORT_2025-09-28.md docs/summaries/
git mv CRITICAL_GAMEPLAY_BUGS_FIX_SUMMARY.md docs/summaries/
git mv DEMO_HOTFIX_SUMMARY.md docs/summaries/
git mv DEMO_HOTFIXES_SUMMARY.md docs/summaries/
git mv LIFT_AND_SHIFT_COMPLETION_SUMMARY.md docs/summaries/
git mv MASTER_CLEANUP_REFERENCE.md docs/summaries/
git mv PHASE_6_SUGGESTIONS.md docs/summaries/
```

### Step 4: Move Guides (4 files)
```bash
git mv ASSET_INTEGRATION_GUIDE.md docs/guides/
git mv TERMINAL_MESSAGES_IMPLEMENTATION.md docs/guides/
git mv PDOOM_DATA_INTEGRATION_PLAN.md docs/guides/
git mv COPILOT_INSTRUCTIONS_UPDATE_ANALYSIS.md docs/guides/
```

### Step 5: Move Analysis (1 file)
```bash
git mv test_failure_analysis.md docs/analysis/
```

### Step 6: Archive README_OLD (1 file)
```bash
git mv README_OLD.md archive/docs/
```

### Step 7: Create Index Files

**`docs/README.md`**
```markdown
# P(Doom) Documentation

## Structure

- `guides/` - Implementation guides and how-tos
- `summaries/` - Historical summaries and completion reports
- `analysis/` - Technical analysis documents

## Guides
- Asset Integration Guide
- Terminal Messages Implementation
- P(Doom) Data Integration Plan
- Copilot Instructions Update Analysis

## Recent Summaries
See `summaries/` directory for historical development summaries.
```

**`godot/docs/README.md`** (from GODOT_README.md)
- Keep existing content, update paths if needed

## Expected Results

### Root Directory After Organization
- 8 markdown files (down from 28)
- Only essential project files remain
- Clear, professional structure

### New Documentation Structure
- `docs/` - General documentation (12 files)
  - `guides/` - 4 files
  - `summaries/` - 7 files
  - `analysis/` - 1 file
- `godot/docs/` - Godot-specific (5 files)
- `archive/docs/` - Archived (1 file)

### Benefits
1. **Clear organization** - Easy to find documentation
2. **Professional appearance** - Root directory clean
3. **Logical grouping** - Related docs together
4. **Preserved history** - All git history maintained
5. **Scalable structure** - Easy to add new docs

## Validation

After organization, verify:

```bash
# Root should have ~8 markdown files
ls *.md | wc -l

# New directories should exist
ls -d docs/guides docs/summaries docs/analysis
ls -d godot/docs godot/docs/features godot/docs/development

# Files moved correctly
git status
```

## Notes

- All moves use `git mv` to preserve history
- No deletions (except README_OLD archived)
- Can always undo with `git reset`
- Consider merging duplicate files (DEMO_HOTFIX_SUMMARY vs DEMO_HOTFIXES_SUMMARY)
