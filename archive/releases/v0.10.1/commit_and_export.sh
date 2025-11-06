#!/bin/bash
# Commit documentation changes and prepare for Godot export

echo "=== Committing documentation changes ==="
git add -A
git commit -m "Prepare for v0.10.1 release: Fix docs, organize structure

- Fix README: pdoom1.com URL, remove Python player instructions
- Update CHANGELOG: Add v0.10.1 entry
- Organize docs: Move 20 files into logical structure
- Fix player guides: Remove Python, focus on Godot
- Create Godot dev tools with clean exit modes
- Create release checklist for Godot export

This prepares the repository for the first official Godot 4.x release.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo "=== Creating build directory structure ==="
mkdir -p builds/windows/v0.10.1

echo ""
echo "=== Documentation committed! ==="
echo "Next: Opening Godot to configure export..."
echo ""
echo "Run this in PowerShell to open Godot:"
echo '  cd godot'
echo '  & "C:\Program Files\Godot\Godot_v4.5.1-stable_win64.exe" --path .'
echo ""
echo "Then: Project → Export... → Add... → Windows Desktop"
echo "Export to: builds/windows/v0.10.1/PDoom.exe"
