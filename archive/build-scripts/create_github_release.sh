#!/bin/bash
# Create GitHub release

set -e  # Exit on error

# Accept version as parameter or use default
VERSION="${1:-v0.10.1}"

echo "==================================="
echo "P(Doom) $VERSION GitHub Release"
echo "==================================="
echo ""

PACKAGE="PDoom-${VERSION}-Windows.zip"
RELEASE_NOTES="archive/releases/${VERSION}/RELEASE_NOTES_${VERSION}.md"

# Fallback to CHANGELOG if no specific release notes
if [ ! -f "$RELEASE_NOTES" ]; then
    echo "ℹ️  No release notes file found, will use CHANGELOG.md excerpt"
    RELEASE_NOTES=""
fi

# Check if package exists
if [ ! -f "$PACKAGE" ]; then
    echo "❌ ERROR: Package not found: $PACKAGE"
    echo "Please run: bash package_release.sh"
    exit 1
fi

# Skip release notes check if using CHANGELOG fallback
if [ -n "$RELEASE_NOTES" ] && [ ! -f "$RELEASE_NOTES" ]; then
    echo "❌ ERROR: Release notes not found: $RELEASE_NOTES"
    exit 1
fi

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ ERROR: GitHub CLI (gh) not installed"
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ ERROR: Not authenticated with GitHub"
    echo "Run: gh auth login"
    exit 1
fi

echo "✅ Pre-flight checks passed"
echo ""

# Confirm with user
echo "About to create release:"
echo "  Version: $VERSION"
echo "  Package: $PACKAGE ($(du -h $PACKAGE | cut -f1))"
if [ -n "$RELEASE_NOTES" ]; then
    echo "  Notes: $RELEASE_NOTES"
else
    echo "  Notes: Will prompt for release notes"
fi
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Release cancelled"
    exit 1
fi

# Create the release
echo ""
echo "🚀 Creating GitHub release..."
echo ""

if [ -n "$RELEASE_NOTES" ]; then
    # Use provided release notes file
    gh release create "$VERSION" \
        --notes-file "$RELEASE_NOTES" \
        "$PACKAGE"
else
    # Use CHANGELOG excerpt (gh will extract from CHANGELOG.md if formatted properly)
    gh release create "$VERSION" \
        --generate-notes \
        "$PACKAGE"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "==================================="
    echo "✅ RELEASE CREATED SUCCESSFULLY!"
    echo "==================================="
    echo ""
    echo "🎉 Release published: $VERSION"
    echo "🔗 View at: https://github.com/PipFoweraker/pdoom1/releases/tag/$VERSION"
    echo ""
    echo "Next steps:"
    echo "1. Test download link from GitHub"
    echo "2. Update README.md with release link"
    echo "3. Close related issues (#435, #431, #389)"
    echo "4. Update website (pdoom1.com)"
    echo ""
else
    echo ""
    echo "❌ ERROR: Failed to create release"
    echo "Check error messages above"
    exit 1
fi
