#!/bin/bash
# Master release script for v0.10.1

set -e  # Exit on error

echo "============================================"
echo " P(Doom) v0.10.1 - Master Release Script"
echo "============================================"
echo ""
echo "This script will guide you through:"
echo "  1. Committing all changes"
echo "  2. Packaging the release"
echo "  3. Creating GitHub release"
echo "  4. Post-release updates"
echo ""
echo "Prerequisites:"
echo "  ✓ Game tested in Godot and works"
echo "  ✓ Exported to builds/windows/v0.10.1/"
echo "  ✓ All features verified"
echo ""
read -p "Ready to proceed? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Release cancelled"
    exit 0
fi

echo ""
echo "=== STEP 1: Committing All Changes ==="
echo ""

if [ -n "$(git status --porcelain)" ]; then
    echo "Uncommitted changes found. Committing..."

    # Run commit scripts
    if [ -f "commit_ap_tracking_fix.sh" ]; then
        echo "Running: commit_ap_tracking_fix.sh"
        bash commit_ap_tracking_fix.sh
    fi

    if [ -f "commit_gdscript_warnings.sh" ]; then
        echo "Running: commit_gdscript_warnings.sh"
        bash commit_gdscript_warnings.sh
    fi

    if [ -f "commit_tier2_features.sh" ]; then
        echo "Running: commit_tier2_features.sh"
        bash commit_tier2_features.sh
    fi

    # Commit CHANGELOG update
    if [ -n "$(git status --porcelain CHANGELOG.md)" ]; then
        echo "Committing CHANGELOG updates..."
        git add CHANGELOG.md
        git commit -m "docs: Update CHANGELOG for v0.10.1 complete release notes"
    fi
else
    echo "✓ No uncommitted changes"
fi

echo ""
echo "=== STEP 2: Pushing to GitHub ==="
echo ""
git push origin main
echo "✓ Pushed to main"

echo ""
echo "=== STEP 3: Packaging Release ==="
echo ""
bash package_release.sh

echo ""
echo "=== STEP 4: Creating GitHub Release ==="
echo ""
bash create_github_release.sh

echo ""
echo "============================================"
echo " 🎉 RELEASE PROCESS COMPLETE!"
echo "============================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Update README.md:"
echo "   - Replace 'Windows builds coming soon' with download link"
echo "   - Commit and push"
echo ""
echo "2. Close GitHub issues:"
echo "   gh issue close 435 -c 'Fixed in v0.10.1'"
echo "   gh issue close 431 -c 'Fixed in v0.10.1'"
echo "   gh issue close 389 -c 'Resolved by design - see issue_389_resolution.md'"
echo ""
echo "3. Update website (pdoom1-website repo)"
echo ""
echo "4. Announce release (optional)"
echo ""
echo "🔗 Release URL:"
echo "   https://github.com/PipFoweraker/pdoom1/releases/tag/v0.10.1"
echo ""
