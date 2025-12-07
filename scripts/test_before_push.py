# !/usr/bin/env python3
"""
Test Before Push - Local Development Workflow

Run this before pushing to main to catch issues early.
This is your "git pre-push hook" script.

Usage:
    python scripts/test_before_push.py              # Standard checks
    python scripts/test_before_push.py --full       # Full test suite
    python scripts/test_before_push.py --fix        # Auto-fix issues where possible
"""

import argparse
import subprocess
import sys
from pathlib import Path

def run_command(cmd: list, description: str) -> bool:
    """Run command and return success status"""
    print(f"\n[RUN] {description}...")
    try:
        result = subprocess.run(cmd, check=True)
        print(f"[OK] {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] {description} failed with exit code {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Before Push - Local Dev Workflow")
    parser.add_argument("--full", action="store_true", help="Run full test suite (slower)")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues where possible")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    results = []

    print("=" * 60)
    print("TEST BEFORE PUSH - Pre-Deployment Validation")
    print("=" * 60)

    # 1. Run pre-build validation
    print("\n[STEP 1/4] Running Godot validation checks...")
    if args.full:
        results.append(run_command(
            [sys.executable, "scripts/pre_build_validation.py", "--full"],
            "Godot Validation (Full)"
        ))
    else:
        results.append(run_command(
            [sys.executable, "scripts/pre_build_validation.py", "--quick"],
            "Godot Validation (Quick)"
        ))

    # 2. Check for uncommitted changes
    print("\n[STEP 2/4] Checking git status...")
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )

        if result.stdout.strip():
            print("[WARN] You have uncommitted changes:")
            print(result.stdout)
            print("[INFO] Consider committing or stashing before pushing")
            # Don't fail on uncommitted changes, just warn
        else:
            print("[OK] Working tree is clean")

        results.append(True)  # Don't fail on this
    except Exception as e:
        print(f"[FAIL] Git status check failed: {e}")
        results.append(False)

    # 3. Run Python tests if they exist
    print("\n[STEP 3/4] Running Python tests...")
    test_dir = project_root / "tests"
    if test_dir.exists() and list(test_dir.glob("test_*.py")):
        results.append(run_command(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            "Python Unit Tests"
        ))
    else:
        print("[SKIP] No Python tests found")
        results.append(True)

    # 4. Check for common issues
    print("\n[STEP 4/4] Checking for common issues...")
    issues_found = []

    # Check for debug prints in GDScript
    for gd_file in project_root.glob("godot/**/*.gd"):
        content = gd_file.read_text(encoding='utf-8')
        if "print_debug" in content or "breakpoint" in content:
            issues_found.append(f"{gd_file.name}: Contains debug statements")

    if issues_found:
        print(f"[WARN] Found {len(issues_found)} potential issues:")
        for issue in issues_found[:5]:
            print(f"  - {issue}")
        # Don't fail on warnings
    else:
        print("[OK] No common issues found")

    results.append(True)  # Don't fail on warnings

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r)
    total = len(results)

    if all(results):
        print(f"[OK] ALL CHECKS PASSED ({passed}/{total})")
        print("[OK] Ready to push!")
        return 0
    else:
        print(f"[FAIL] SOME CHECKS FAILED ({passed}/{total} passed)")
        print("[FAIL] Fix issues before pushing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
