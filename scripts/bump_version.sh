#!/bin/bash
# Bump version across all files and create release tag

set -e

if [ $# -ne 1 ]; then
    echo "Usage: bash scripts/bump_version.sh <version>"
    echo "Example: bash scripts/bump_version.sh 0.10.2"
    exit 1
fi

NEW_VERSION="$1"
echo "======================================"
echo "Version Bump Script"
echo "======================================"
echo ""
echo "New version: v$NEW_VERSION"
echo ""

# Confirm with user
read -p "This will update version numbers in multiple files. Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "🔧 Updating version numbers..."

# Update project.godot
echo "  → godot/project.godot"
sed -i "s/config\/version=\".*\"/config\/version=\"$NEW_VERSION\"/" godot/project.godot

# Update release scripts
echo "  → package_release.sh"
sed -i "s/PACKAGE_NAME=\"PDoom-v.*-Windows\"/PACKAGE_NAME=\"PDoom-v$NEW_VERSION-Windows\"/" package_release.sh

echo "  → create_github_release.sh"
sed -i "s/VERSION=\"v.*\"/VERSION=\"v$NEW_VERSION\"/" create_github_release.sh

# Check if CHANGELOG has a placeholder for this version
if ! grep -q "## \[Unreleased\]" CHANGELOG.md && ! grep -q "## \[$NEW_VERSION\]" CHANGELOG.md; then
    echo ""
    echo "⚠️  WARNING: CHANGELOG.md does not have an [Unreleased] or [$NEW_VERSION] section"
    echo "   Please update CHANGELOG.md manually before committing!"
fi

echo ""
echo "✅ Version numbers updated!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Review changes:"
echo "   git diff"
echo ""
echo "2. Update CHANGELOG.md:"
echo "   - Change [Unreleased] to [$NEW_VERSION] - $(date +%Y-%m-%d)"
echo "   - Document all changes in this version"
echo ""
echo "3. Commit changes:"
echo "   git add ."
echo "   git commit -m \"chore: Bump version to v$NEW_VERSION\""
echo ""
echo "4. Create and push tag:"
echo "   git tag v$NEW_VERSION"
echo "   git push origin main"
echo "   git push origin v$NEW_VERSION"
echo ""
echo "5. Export from Godot to builds/windows/v$NEW_VERSION/"
echo ""
echo "6. Run release process:"
echo "   bash package_release.sh"
echo "   bash create_github_release.sh"
echo ""
