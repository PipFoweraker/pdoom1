# !/usr/bin/env python3
"""
Style Guide Enforcement Check

This script checks if UI-related files have been modified without updating
the UI_STYLE_GUIDE.md. It's designed to remind developers to keep the
style guide in sync with code changes.

Usage:
    python scripts/check_style_guide.py [--strict]

Options:
    --strict    Exit with error code 1 on violations (blocks commit)
                Without this flag, only warnings are shown

Skip this check:
    - Use --no-verify flag: git commit --no-verify
    - Or set environment variable: SKIP_STYLE_GUIDE_CHECK=1
"""

import os
import subprocess
import sys
from pathlib import Path

# Files/patterns that should trigger style guide update reminders
STYLE_SENSITIVE_PATTERNS = [
    # Theme and styling
    "godot/autoload/theme_manager.gd",
    "godot/theme/",

    # UI scenes with styling
    "godot/scenes/welcome.tscn",
    "godot/scenes/settings_menu.tscn",
    "godot/scenes/pregame_setup.tscn",
    "godot/scenes/leaderboard_screen.tscn",
    "godot/scenes/end_game_screen.tscn",
    "godot/scenes/main.tscn",

    # Asset additions
    "godot/assets/textures/",
    "godot/assets/ui/",

    # Color/style definitions in GDScript
    "Color(",  # When new colors are added
]

STYLE_GUIDE_PATH = "godot/UI_STYLE_GUIDE.md"


def get_staged_files():
    """Get list of files staged for commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []


def check_for_color_additions(files):
    """Check if any GDScript files have new Color() definitions."""
    for file in files:
        if file.endswith('.gd'):
            try:
                result = subprocess.run(
                    ["git", "diff", "--cached", file],
                    capture_output=True,
                    text=True,
                    check=True
                )
                # Check for added lines with Color(
                for line in result.stdout.split('\n'):
                    if line.startswith('+') and 'Color(' in line and not line.startswith('+++'):
                        return True
            except subprocess.CalledProcessError:
                pass
    return False


def check_style_guide_update(files):
    """
    Check if style-sensitive files were modified without updating the style guide.

    Returns:
        tuple: (needs_update: bool, affected_files: list)
    """
    affected_files = []
    style_guide_updated = STYLE_GUIDE_PATH in files

    for file in files:
        # Skip the style guide itself
        if file == STYLE_GUIDE_PATH:
            continue

        # Check against patterns
        for pattern in STYLE_SENSITIVE_PATTERNS:
            if pattern in file:
                affected_files.append(file)
                break

    # Also check for Color() additions
    if check_for_color_additions(files):
        affected_files.append("(new Color definitions detected)")

    # Remove duplicates
    affected_files = list(set(affected_files))

    # Only flag if we have affected files but no style guide update
    if affected_files and not style_guide_updated:
        return True, affected_files

    return False, []


def main():
    # Check for skip environment variable
    if os.environ.get('SKIP_STYLE_GUIDE_CHECK', '').lower() in ('1', 'true', 'yes'):
        print("[STYLE GUIDE] Check skipped via SKIP_STYLE_GUIDE_CHECK environment variable")
        return 0

    strict_mode = '--strict' in sys.argv

    files = get_staged_files()
    if not files:
        return 0

    needs_update, affected_files = check_style_guide_update(files)

    if needs_update:
        print("\n" + "=" * 60)
        print("[STYLE GUIDE REMINDER]")
        print("=" * 60)
        print("\nThe following UI/style-related files were modified:")
        for f in affected_files:
            print(f"  - {f}")
        print(f"\nBut {STYLE_GUIDE_PATH} was not updated.")
        print("\nPlease consider updating the style guide if:")
        print("  - New colors were added")
        print("  - New textures/assets were integrated")
        print("  - UI layout patterns changed")
        print("  - Typography or spacing was modified")
        print("\nTo skip this check:")
        print("  git commit --no-verify")
        print("  or: SKIP_STYLE_GUIDE_CHECK=1 git commit")
        print("\n" + "=" * 60 + "\n")

        if strict_mode:
            print("[ERROR] Style guide check failed (strict mode)")
            return 1
        else:
            print("[WARNING] Proceeding with commit (warning only)")
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
