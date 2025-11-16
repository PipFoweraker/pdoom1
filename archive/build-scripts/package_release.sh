#!/bin/bash
# Package release for distribution

set -e  # Exit on error

# Accept version as parameter or use default
VERSION="${1:-v0.10.1}"

echo "==================================="
echo "P(Doom) $VERSION Release Packager"
echo "==================================="
echo ""

BUILD_DIR="builds/windows/$VERSION"
PACKAGE_NAME="PDoom-${VERSION}-Windows"
TEMP_DIR="temp_package"

# Check if build exists
if [ ! -f "$BUILD_DIR/PDoom.exe" ]; then
    echo "❌ ERROR: PDoom.exe not found in $BUILD_DIR"
    echo "Please export from Godot first!"
    exit 1
fi

echo "✅ Found build files"
echo ""

# Create temp directory for packaging
echo "📦 Creating package directory..."
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR/$PACKAGE_NAME"

# Copy game files
echo "📋 Copying game files..."
cp "$BUILD_DIR/PDoom.exe" "$TEMP_DIR/$PACKAGE_NAME/"

# The .pck file uses the project name, not the exe name
if [ -f "$BUILD_DIR/P(Doom)1.pck" ]; then
    cp "$BUILD_DIR/P(Doom)1.pck" "$TEMP_DIR/$PACKAGE_NAME/PDoom.pck"
    echo "  ✓ Copied P(Doom)1.pck → PDoom.pck"
elif [ -f "$BUILD_DIR/PDoom.pck" ]; then
    cp "$BUILD_DIR/PDoom.pck" "$TEMP_DIR/$PACKAGE_NAME/"
    echo "  ✓ Copied PDoom.pck"
else
    echo "❌ ERROR: Could not find .pck file"
    exit 1
fi

# Optional: Include console exe for debugging
if [ -f "$BUILD_DIR/P(Doom)1.console.exe" ]; then
    cp "$BUILD_DIR/P(Doom)1.console.exe" "$TEMP_DIR/$PACKAGE_NAME/PDoom.console.exe"
    echo "  ✓ Included PDoom.console.exe (debug version)"
elif [ -f "$BUILD_DIR/PDoom.console.exe" ]; then
    cp "$BUILD_DIR/PDoom.console.exe" "$TEMP_DIR/$PACKAGE_NAME/"
    echo "  ✓ Included PDoom.console.exe (debug version)"
fi

# Create README.txt for the package
echo "📝 Creating README.txt..."
cat > "$TEMP_DIR/$PACKAGE_NAME/README.txt" << 'EOF'
P(Doom) v0.10.1 - AI Safety Lab Management Game
================================================

QUICK START:
1. Double-click PDoom.exe
2. Follow on-screen instructions
3. Use keyboard shortcuts for faster gameplay

CONTROLS:
- 1-9: Select actions
- C: Clear action queue
- Space/Enter: Commit actions (end turn)
- ESC: Pause menu

SYSTEM REQUIREMENTS:
- Windows 10/11 (64-bit)
- 2GB RAM minimum
- 150MB disk space

RESOURCES:
- Website: https://pdoom1.com
- GitHub: https://github.com/PipFoweraker/pdoom1
- Report bugs: https://github.com/PipFoweraker/pdoom1/issues

TROUBLESHOOTING:
- If game doesn't start: Right-click PDoom.exe → Properties → Unblock
- If you see a Windows warning: Click "More info" → "Run anyway"

Enjoy managing your AI safety lab!
EOF

# Create simplified changelog
echo "📄 Creating CHANGELOG.txt..."
cat > "$TEMP_DIR/$PACKAGE_NAME/CHANGELOG.txt" << 'EOF'
P(Doom) v0.10.1 - UX Improvements & First Public Release
=========================================================

MAJOR CHANGES:
✅ First official Godot 4.x release!
✅ Fixed critical AP overcommitment bug
✅ Added visual queue management (remove buttons)
✅ Added danger warnings before risky turns
✅ Improved button states and keyboard shortcuts
✅ Color-coded AP counter (green/yellow/red)

NEW FEATURES:
- Clear Queue button (C key)
- Remove buttons on individual queue items
- Danger warnings when doom/reputation at risk
- Better error messages

BUG FIXES:
- Can't overcommit AP anymore
- Clear Queue button works correctly
- Commit Actions disabled when queue empty
- AP tracking now accurate

For full details, see:
https://github.com/PipFoweraker/pdoom1/releases/tag/v0.10.1
EOF

# Create the zip file
echo "🗜️  Creating zip archive..."
cd "$TEMP_DIR"

# Check if zip command exists, otherwise use PowerShell
if command -v zip &> /dev/null; then
    zip -r "../$PACKAGE_NAME.zip" "$PACKAGE_NAME"
else
    # Use PowerShell on Windows
    powershell -Command "Compress-Archive -Path '$PACKAGE_NAME' -DestinationPath '../$PACKAGE_NAME.zip' -Force"
fi

cd ..

# Clean up temp directory
echo "🧹 Cleaning up..."
rm -rf "$TEMP_DIR"

# Verify package
if [ -f "$PACKAGE_NAME.zip" ]; then
    SIZE=$(du -h "$PACKAGE_NAME.zip" | cut -f1)
    echo ""
    echo "==================================="
    echo "✅ PACKAGE CREATED SUCCESSFULLY!"
    echo "==================================="
    echo ""
    echo "📦 File: $PACKAGE_NAME.zip"
    echo "📏 Size: $SIZE"
    echo ""
    echo "Contents:"
    echo "  - PDoom.exe (game executable)"
    echo "  - PDoom.pck (game data)"
    echo "  - README.txt (quick start guide)"
    echo "  - CHANGELOG.txt (what's new)"
    echo ""
    echo "Next steps:"
    echo "1. Test the package:"
    echo "   - Extract to a new folder"
    echo "   - Run PDoom.exe"
    echo "   - Verify gameplay works"
    echo ""
    echo "2. Create GitHub release:"
    echo "   bash create_github_release.sh"
    echo ""
else
    echo "❌ ERROR: Failed to create package"
    exit 1
fi
