#!/usr/bin/env python3
"""
Run Godot GUT (Godot Unit Test) tests from command line.

This runner is the real CI gate (issues #629 / #590). It does three things the
old runner did NOT, each of which is why CI was green while running zero tests:

  1. Runs `godot --headless --import` FIRST. On a fresh checkout GUT's own
     class_names are not in the class cache, so GUT calls quit(0) BEFORE parsing
     args or running a single test (version_conversion.error_if_not_all_classes_imported).
     Without an import pass the whole suite is skipped and exit code is 0.
  2. Does NOT trust GUT's bare exit code. GUT exits 0 whenever fail_count == 0 --
     including when it ran nothing, quit early, or silently dropped a test file
     that failed to parse / used the wrong base class. Instead we PARSE the JUnit
     XML and require: file exists, tests > 0 (and >= --min-tests), failures == 0.
  3. Manifest check (closes #590): every `test_*.gd` on disk in a test dir MUST
     appear as a collected <testsuite> in the JUnit results. A file GUT silently
     skips (parse error, or `extends Node` instead of GutTest) => count mismatch
     => hard failure naming the offending files. Silence is failure.

Usage:
    python scripts/run_godot_tests.py                 # unit (fast) + simulation + integration
    python scripts/run_godot_tests.py --quick         # fast unit gate only (tests/unit, non-recursive)
    python scripts/run_godot_tests.py --simulation    # slow simulation suite only (tests/unit/simulation)
    python scripts/run_godot_tests.py --integration-only
    python scripts/run_godot_tests.py --smoke-only
    python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300
"""

import argparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
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

# Mode -> (res:// dir, human name). Fast unit gate is tests/unit NON-recursive;
# the slow, run-simulating suites live in tests/unit/simulation (a separate,
# visible CI job) so they don't bloat the required fast gate.
MODE_DIRS = {
    "quick": "res://tests/unit",
    "simulation": "res://tests/unit/simulation",
    "integration": "res://tests/integration",
    "smoke": "res://tests/smoke",
}


def find_godot():
    """Find Godot executable on system."""
    for path in GODOT_PATHS:
        try:
            result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                print(f"[INFO] Found Godot: {path}")
                print(f"[INFO] Version: {result.stdout.strip()}")
                return path
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            continue

    print("[ERROR] Could not find Godot executable!")
    print("[INFO] Tried paths:", GODOT_PATHS)
    return None


def run_import(godot_path):
    """Populate the class cache so GUT does not quit(0) before running tests.

    This is THE fix for the zero-test false-green (#629): a fresh checkout has no
    .godot/global_script_class_cache, so GUT's error_if_not_all_classes_imported()
    is true and it quits immediately.
    """
    print("\n[IMPORT] Running headless import pass (populates class cache)...")
    cmd = [godot_path, "--headless", "--path", str(GODOT_PROJECT), "--import"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        # --import can exit non-zero on benign asset warnings; only treat a hard
        # failure (no cache produced) as fatal. The cache file confirms success.
        cache = GODOT_PROJECT / ".godot" / "global_script_class_cache.cfg"
        if cache.exists():
            print("[IMPORT] Class cache present -- import OK.")
            return True
        print("[IMPORT][WARN] class cache missing after import; exit", result.returncode)
        print(result.stdout[-2000:])
        print(result.stderr[-2000:])
        return False
    except subprocess.TimeoutExpired:
        print("[IMPORT][ERROR] Import pass timed out after 10 minutes!")
        return False
    except Exception as e:
        print(f"[IMPORT][ERROR] Import pass failed: {e}")
        return False


def check_syntax(godot_path):
    """Check GDScript syntax by attempting to load the project."""
    print("\n[CHECK] Checking GDScript syntax...")

    cmd = [godot_path, "--headless", "--path", str(GODOT_PROJECT), "--quit"]

    # Godot emits benign ERROR lines on headless shutdown (ObjectDB leaks,
    # resources still in use) and for missing imported assets. Only match
    # markers that indicate genuinely broken GDScript source. Patterns broadened
    # under #629: the old set missed Godot's actual "Parse error" /
    # "Failed to load script" strings, so real parse failures passed the gate.
    REAL_ERROR_MARKERS = [
        "Cannot load source code",
        "GDScript error",
        "Parse error",
        "Failed to load script",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        output = result.stdout + result.stderr
        found_errors = [m for m in REAL_ERROR_MARKERS if m in output]

        if found_errors:
            print("[FAIL] GDScript syntax errors found (markers: %s):" % found_errors)
            print(output)
            return False
        else:
            print("[PASS] GDScript syntax check passed! CHECKED")
            return True

    except Exception as e:
        print(f"[ERROR] Syntax check failed: {e}")
        return False


def _disk_test_files(test_dir):
    """Non-recursive glob of test_*.gd basenames in a res:// test dir."""
    dir_path = GODOT_PROJECT / test_dir.replace("res://", "")
    if not dir_path.exists():
        return None  # signal: directory missing
    return sorted(p.name for p in dir_path.glob("test_*.gd"))


def _parse_junit(junit_path):
    """Parse a GUT JUnit XML file.

    Returns dict {tests, failures, suites:set(basenames)} or None if unparseable.
    """
    if not junit_path.exists():
        return None
    try:
        root = ET.parse(junit_path).getroot()  # <testsuites tests= failures= >
        tests = int(root.get("tests", "0"))
        failures = int(root.get("failures", "0"))
        suites = set()
        for suite in root.findall("testsuite"):
            name = suite.get("name", "")  # e.g. "tests/unit/test_foo.gd"
            suites.add(Path(name).name)
        return {"tests": tests, "failures": failures, "suites": suites}
    except ET.ParseError as e:
        print(f"[PARSE][ERROR] JUnit XML at {junit_path} is malformed: {e}")
        return None


def run_gut_tests(godot_path, mode, test_dir, log_level, min_tests):
    """Run one test directory and hard-gate on the JUnit results.

    Returns (ok: bool, tests: int, failures: int).
    """
    disk_files = _disk_test_files(test_dir)
    if disk_files is None:
        # A requested-but-missing dir is a FAILURE, not a silent skip. The old
        # runner skipped missing dirs, which is exactly how the smoke gate
        # "passed" while pointing at a nonexistent tests/smoke (#629).
        print(f"\n[FAIL] Test directory {test_dir} does not exist -- cannot run '{mode}'.")
        return (False, 0, 0)

    if not disk_files:
        print(f"\n[FAIL] No test_*.gd files found in {test_dir} for '{mode}'.")
        return (False, 0, 0)

    junit_fs = GODOT_PROJECT / f"test-results-{mode}.xml"
    junit_res = f"res://test-results-{mode}.xml"
    if junit_fs.exists():
        junit_fs.unlink()

    cmd = [
        godot_path,
        "--headless",
        "--path",
        str(GODOT_PROJECT),
        "-s",
        "res://addons/gut/gut_cmdln.gd",
        "-gdir=" + test_dir,
        f"-glog={log_level}",
        "-gexit",
        f"-gjunit_xml_file={junit_res}",  # NOTE: underscores. GUT 9.5 rejects -gjunitxml_file.
    ]

    print(f"\n[TEST] Running '{mode}' tests in {test_dir} ({len(disk_files)} files on disk)")
    print(f"[CMD] {' '.join(cmd)}\n")

    exit_code = None
    try:
        result = subprocess.run(
            cmd, cwd=GODOT_PROJECT, capture_output=False, text=True, timeout=900
        )
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        print("\n[FAIL] Tests timed out after 15 minutes!")
        return (False, 0, 0)
    except Exception as e:
        print(f"\n[FAIL] Failed to run tests: {e}")
        return (False, 0, 0)

    # --- The gate: trust the JUnit file, not the exit code. ---
    parsed = _parse_junit(junit_fs)
    if parsed is None:
        print(
            f"\n[FAIL] '{mode}': no parseable JUnit results at {junit_fs}. "
            "GUT ran nothing or quit early (missing import pass? bad args?)."
        )
        return (False, 0, 0)

    tests = parsed["tests"]
    failures = parsed["failures"]
    collected = parsed["suites"]

    ok = True

    # (a) zero-tests / floor: silence is failure
    if tests <= 0:
        print(f"\n[FAIL] '{mode}': JUnit reports {tests} tests collected -- ZERO tests ran.")
        ok = False
    elif tests < min_tests:
        print(
            f"\n[FAIL] '{mode}': only {tests} tests ran, below floor of {min_tests}. "
            "Tests likely silently dropped."
        )
        ok = False

    # (b) real failures
    if failures > 0:
        print(f"\n[FAIL] '{mode}': {failures} test failure(s) reported.")
        ok = False

    # (c) manifest: every on-disk test file must be collected (#590 parse-hiding)
    missing = [f for f in disk_files if f not in collected]
    if missing:
        print(
            f"\n[FAIL] '{mode}': {len(missing)} test file(s) on disk were NOT collected by GUT "
            "(parse error or wrong base class -- must `extends GutTest`):"
        )
        for f in missing:
            print(f"          - {f}")
        ok = False

    # (d) sanity: GUT's own exit code should corroborate. Log a mismatch.
    if exit_code not in (0, None) and ok:
        print(f"\n[WARN] '{mode}': JUnit looked clean but GUT exit code was {exit_code}.")

    status = "PASS" if ok else "FAIL"
    print(
        f"\n[{status}] '{mode}': {tests} tests, {failures} failures, "
        f"{len(collected)}/{len(disk_files)} files collected."
    )
    return (ok, tests, failures)


def _write_step_summary(rows):
    """Append a counts table to GITHUB_STEP_SUMMARY so a human sees 'N tests ran'."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    lines = [
        "",
        "### Godot test results",
        "",
        "| Suite | Tests | Failures | Result |",
        "|---|---:|---:|---|",
    ]
    for name, tests, failures, ok in rows:
        lines.append(f"| {name} | {tests} | {failures} | {'PASS' if ok else 'FAIL'} |")
    lines.append("")
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception as e:
        print(f"[WARN] Could not write step summary: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Run Godot GUT tests (real gate: import pass + JUnit floor + manifest).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--quick", action="store_true", help="Fast unit gate only (tests/unit, non-recursive)"
    )
    parser.add_argument(
        "--simulation",
        action="store_true",
        help="Slow simulation suite only (tests/unit/simulation)",
    )
    parser.add_argument(
        "--integration-only",
        action="store_true",
        dest="integration_only",
        help="Integration tests only",
    )
    parser.add_argument(
        "--smoke-only", action="store_true", dest="smoke_only", help="Smoke tests only"
    )
    parser.add_argument(
        "--ci-mode",
        action="store_true",
        dest="ci_mode",
        help="CI mode (kept for compatibility; JUnit is always produced now)",
    )
    parser.add_argument(
        "--min-tests",
        type=int,
        default=1,
        dest="min_tests",
        help="Fail if fewer than N tests run (floor tripwire). Default 1 (i.e. >0).",
    )
    parser.add_argument(
        "--no-syntax-check",
        action="store_true",
        dest="no_syntax_check",
        help="Skip GDScript syntax check",
    )
    parser.add_argument(
        "--no-import",
        action="store_true",
        dest="no_import",
        help="Skip the headless import pass (only if the class cache is already warm)",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose GUT output (log level 3)")

    args = parser.parse_args()

    godot_path = find_godot()
    if not godot_path:
        sys.exit(1)

    # Import pass FIRST -- without it GUT quits(0) before running anything.
    if not args.no_import:
        if not run_import(godot_path):
            print("\n[ERROR] Import pass failed; aborting (GUT would run zero tests).")
            sys.exit(1)

    if not args.no_syntax_check:
        if not check_syntax(godot_path):
            print("\n[ERROR] Syntax check failed! Fix errors before running tests.")
            sys.exit(1)

    log_level = 3 if args.verbose else 2

    # Determine modes to run
    if args.smoke_only:
        modes = ["smoke"]
    elif args.integration_only:
        modes = ["integration"]
    elif args.simulation:
        modes = ["simulation"]
    elif args.quick:
        modes = ["quick"]
    else:
        modes = ["quick", "simulation", "integration"]

    all_passed = True
    summary_rows = []
    for mode in modes:
        ok, tests, failures = run_gut_tests(
            godot_path, mode, MODE_DIRS[mode], log_level, args.min_tests
        )
        summary_rows.append((mode, tests, failures, ok))
        all_passed = all_passed and ok

    _write_step_summary(summary_rows)

    print("\n" + "=" * 60)
    print(
        "[TOTALS] "
        + " | ".join(
            f"{m}: {t} tests, {fl} fail ({'ok' if o else 'FAIL'})" for (m, t, fl, o) in summary_rows
        )
    )
    if all_passed:
        print("[SUCCESS] All requested suites passed the gate! CHECKED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("[FAILURE] Gate failed (see above).")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
