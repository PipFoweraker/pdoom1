#!/usr/bin/env python3
"""
Run Godot GUT (Godot Unit Test) tests from command line.

Usage:
    python scripts/run_godot_tests.py                    # Run all tests
    python scripts/run_godot_tests.py --quick            # Run unit tests only
    python scripts/run_godot_tests.py --smoke-only       # Run smoke tests only
    python scripts/run_godot_tests.py --ci-mode          # CI mode with JUnit output
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
GODOT_PROJECT = PROJECT_ROOT / "godot"

# Godot executable paths (try to find Godot)
GODOT_PATHS = [
    "C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe",
    "godot",  # System PATH
    "/usr/bin/godot",
    "/usr/local/bin/godot",
]


def find_godot():
    """Find Godot executable on system."""
    for path in GODOT_PATHS:
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"[INFO] Found Godot: {path}")
                print(f"[INFO] Version: {result.stdout.strip()}")
                return path
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            continue

    print("[ERROR] Could not find Godot executable!")
    print("[INFO] Tried paths:", GODOT_PATHS)
    return None


def run_gut_tests(godot_path, test_dir, log_level=2, junit_output=None):
    """
    Run GUT tests using Godot headless mode.

    Args:
        godot_path: Path to Godot executable
        test_dir: Test directory relative to project (e.g. "res://tests/unit")
        log_level: GUT log level (0=quiet, 1=normal, 2=verbose, 3=debug)
        junit_output: Path to JUnit XML output file (optional)

    Returns:
        True if tests passed, False otherwise
    """
    cmd = [
        godot_path,
        "--headless",
        "--path", str(GODOT_PROJECT),
        "-s", "res://addons/gut/gut_cmdln.gd",
        "-gdir=" + test_dir,
        f"-glog={log_level}",
        "-gexit"
    ]

    if junit_output:
        cmd.append(f"-gjunitxml_file={junit_output}")

    print(f"\n[TEST] Running tests in {test_dir}")
    print(f"[CMD] {' '.join(cmd)}\n")

    try:
        result = subprocess.run(
            cmd,
            cwd=GODOT_PROJECT,
            capture_output=False,
            text=True,
            timeout=300  # 5 minute timeout
        )

        # GUT exits with 0 on success, non-zero on failure
        if result.returncode == 0:
            print(f"\n[PASS] Tests in {test_dir} passed! ✓")
            return True
        else:
            print(f"\n[FAIL] Tests in {test_dir} failed! ✗")
            return False

    except subprocess.TimeoutExpired:
        print(f"\n[ERROR] Tests timed out after 5 minutes!")
        return False
    except Exception as e:
        print(f"\n[ERROR] Failed to run tests: {e}")
        return False


def check_syntax(godot_path):
    """Check GDScript syntax by attempting to load the project."""
    print("\n[CHECK] Checking GDScript syntax...")

    cmd = [
        godot_path,
        "--headless",
        "--path", str(GODOT_PROJECT),
        "--quit"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Check for errors in output
        output = result.stdout + result.stderr
        if "ERROR" in output or "Parse Error" in output:
            print("[FAIL] GDScript syntax errors found:")
            print(output)
            return False
        else:
            print("[PASS] GDScript syntax check passed! ✓")
            return True

    except Exception as e:
        print(f"[ERROR] Syntax check failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run Godot GUT tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_godot_tests.py                    # Run all tests
  python scripts/run_godot_tests.py --quick            # Unit tests only
  python scripts/run_godot_tests.py --smoke-only       # Smoke tests only
  python scripts/run_godot_tests.py --ci-mode          # CI mode with JUnit
        """
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only unit tests (fast)"
    )

    parser.add_argument(
        "--smoke-only",
        action="store_true",
        help="Run only smoke tests"
    )

    parser.add_argument(
        "--ci-mode",
        action="store_true",
        help="CI mode: generate JUnit XML output"
    )

    parser.add_argument(
        "--no-syntax-check",
        action="store_true",
        help="Skip GDScript syntax check"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output (GUT log level 3)"
    )

    args = parser.parse_args()

    # Find Godot
    godot_path = find_godot()
    if not godot_path:
        sys.exit(1)

    # Check syntax first (unless skipped)
    if not args.no_syntax_check:
        if not check_syntax(godot_path):
            print("\n[ERROR] Syntax check failed! Fix errors before running tests.")
            sys.exit(1)

    # Determine log level
    log_level = 3 if args.verbose else 2

    # Track results
    all_passed = True

    # Run tests based on mode
    if args.smoke_only:
        # Smoke tests only
        test_dirs = ["res://tests/smoke"]
    elif args.quick:
        # Unit tests only
        test_dirs = ["res://tests/unit"]
    else:
        # Full test suite
        test_dirs = [
            "res://tests/unit",
            "res://tests/integration",
            "res://tests/smoke"
        ]

    # Run each test directory
    for test_dir in test_dirs:
        # Check if directory exists
        dir_path = GODOT_PROJECT / test_dir.replace("res://", "")
        if not dir_path.exists():
            print(f"[SKIP] {test_dir} does not exist, skipping...")
            continue

        junit_file = None
        if args.ci_mode:
            test_name = test_dir.split("/")[-1]
            junit_file = str(PROJECT_ROOT / f"test-results-{test_name}.xml")

        passed = run_gut_tests(godot_path, test_dir, log_level, junit_file)
        all_passed = all_passed and passed

    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("[SUCCESS] All tests passed! ✓")
        print("="*60)
        sys.exit(0)
    else:
        print("[FAILURE] Some tests failed! ✗")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
