#!/bin/bash
# Sync historical data from pdoom-data repository to pdoom1
# This script is run FROM pdoom1 repository
# Usage: ./scripts/sync_from_pdoom_data.sh [pdoom_data_repo_path]

set -e  # Exit on error

PDOOM1_REPO="$(pwd)"
PDOOM_DATA_REPO="${1:-../pdoom-data}"

echo "=== pdoom-data → pdoom1 Sync Pipeline ==="
echo "Source: $PDOOM_DATA_REPO"
echo "Target: $PDOOM1_REPO"

# Validate we're in pdoom1 repo
if [ ! -f "README.md" ] || ! grep -q "P(Doom)" README.md; then
    echo "ERROR: This script must be run from pdoom1 repository root"
    exit 1
fi

# Validate pdoom-data repo exists
if [ ! -d "$PDOOM_DATA_REPO" ]; then
    echo "ERROR: pdoom-data repository not found at $PDOOM_DATA_REPO"
    echo "Please clone pdoom-data repository or provide correct path"
    exit 1
fi

# Validate pdoom-data has transformed directory
if [ ! -d "$PDOOM_DATA_REPO/transformed" ]; then
    echo "ERROR: pdoom-data repository missing 'transformed' directory"
    echo "Has the data been processed yet?"
    exit 1
fi

# Create target directories if they don't exist
echo "Creating target directories..."
mkdir -p shared/data/historical_timeline
mkdir -p shared/data/researchers
mkdir -p shared/data/organizations
mkdir -p godot/data/historical_timeline
mkdir -p godot/data/researchers
mkdir -p godot/data/organizations

# Sync timeline events (Python version)
echo "Syncing timeline events (Python)..."
if [ -d "$PDOOM_DATA_REPO/transformed/timeline_events" ]; then
    rsync -av --delete \
      "$PDOOM_DATA_REPO/transformed/timeline_events/" \
      shared/data/historical_timeline/
else
    echo "  Warning: No timeline events found in pdoom-data"
fi

# Sync timeline events (Godot version)
echo "Syncing timeline events (Godot)..."
if [ -d "$PDOOM_DATA_REPO/transformed/timeline_events" ]; then
    rsync -av --delete \
      "$PDOOM_DATA_REPO/transformed/timeline_events/" \
      godot/data/historical_timeline/
else
    echo "  Warning: No timeline events found in pdoom-data"
fi

# Sync researcher profiles (Python version)
echo "Syncing researcher profiles (Python)..."
if [ -d "$PDOOM_DATA_REPO/transformed/researcher_profiles" ]; then
    rsync -av --delete \
      "$PDOOM_DATA_REPO/transformed/researcher_profiles/" \
      shared/data/researchers/
else
    echo "  Warning: No researcher profiles found in pdoom-data"
fi

# Sync researcher profiles (Godot version)
echo "Syncing researcher profiles (Godot)..."
if [ -d "$PDOOM_DATA_REPO/transformed/researcher_profiles" ]; then
    rsync -av --delete \
      "$PDOOM_DATA_REPO/transformed/researcher_profiles/" \
      godot/data/researchers/
else
    echo "  Warning: No researcher profiles found in pdoom-data"
fi

# Sync organizations (Python version)
echo "Syncing organizations (Python)..."
if [ -d "$PDOOM_DATA_REPO/cleaned/organizations" ]; then
    rsync -av --delete \
      "$PDOOM_DATA_REPO/cleaned/organizations/" \
      shared/data/organizations/
else
    echo "  Warning: No organizations found in pdoom-data"
fi

# Sync organizations (Godot version)
echo "Syncing organizations (Godot)..."
if [ -d "$PDOOM_DATA_REPO/cleaned/organizations" ]; then
    rsync -av --delete \
      "$PDOOM_DATA_REPO/cleaned/organizations/" \
      godot/data/organizations/
else
    echo "  Warning: No organizations found in pdoom-data"
fi

# Get pdoom-data commit hash for tracking
PDOOM_DATA_COMMIT=$(git -C "$PDOOM_DATA_REPO" rev-parse HEAD 2>/dev/null || echo "unknown")
PDOOM_DATA_BRANCH=$(git -C "$PDOOM_DATA_REPO" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

# Count synced files
TIMELINE_COUNT=$(find shared/data/historical_timeline -name "*.json" 2>/dev/null | wc -l)
RESEARCHER_COUNT=$(find shared/data/researchers -name "*.json" 2>/dev/null | wc -l)
ORG_COUNT=$(find shared/data/organizations -name "*.json" 2>/dev/null | wc -l)

# Generate sync manifest
echo "Generating sync manifest..."
cat > shared/data/SYNC_MANIFEST.json <<EOF
{
  "sync_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "pdoom_data_commit": "$PDOOM_DATA_COMMIT",
  "pdoom_data_branch": "$PDOOM_DATA_BRANCH",
  "pdoom_data_path": "$PDOOM_DATA_REPO",
  "files_synced": {
    "timeline_events": $TIMELINE_COUNT,
    "researcher_profiles": $RESEARCHER_COUNT,
    "organizations": $ORG_COUNT
  }
}
EOF

echo ""
echo "=== Sync Complete ==="
echo "Files synced:"
echo "  - Timeline events: $TIMELINE_COUNT"
echo "  - Researcher profiles: $RESEARCHER_COUNT"
echo "  - Organizations: $ORG_COUNT"
echo ""
echo "Source: $PDOOM_DATA_REPO @ $PDOOM_DATA_COMMIT"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff shared/data godot/data"
echo "  2. Run validation: python scripts/validate_historical_data.py"
echo "  3. Run tests: python -m pytest tests/"
echo "  4. Commit: git add shared/data godot/data && git commit -m 'chore: sync historical data from pdoom-data'"
echo ""
