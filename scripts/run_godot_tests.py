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

Non-blocking-tier surfacing (#964): the simulation tier is intentionally
non-blocking in CI (slow, run-simulating). A failure there must still be LOUD,
not silently green -- format_summary_markdown() emits a "[!] <MODE> TIER RED"
banner plus a per-test failure table for any non-blocking mode that failed.
This is written to GITHUB_STEP_SUMMARY automatically, and available via
--summary (stdout) / --summary-file PATH for CI steps that need it as a file
(e.g. to attach to a PR comment) so local runs and CI share one formatter.

Usage:
    python scripts/run_godot_tests.py                 # unit (fast) + simulation + integration
    python scripts/run_godot_tests.py --quick         # fast unit gate only (tests/unit, non-recursive)
    python scripts/run_godot_tests.py --simulation    # slow simulation suite only (tests/unit/simulation)
    python scripts/run_godot_tests.py --integration-only
    python scripts/run_godot_tests.py --smoke-only
    python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300
    python scripts/run_godot_tests.py --simulation --summary            # print the RED-banner table locally
    python scripts/run_godot_tests.py --simulation --summary-file out.md
"""

import argparse
import os
import re
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


SYNTAX_WALK_SCENE = "res://tools/syntax_walk.tscn"
SYNTAX_WALK_MARKER = re.compile(r"SYNTAX_WALK_COMPLETE files=(\d+)")


def _disk_gd_files():
    """Every .gd under godot/ that the syntax walker is expected to compile.

    MUST mirror the walk in godot/tools/syntax_walk.gd exactly: skip the
    top-level addons/ dir (third-party) and any dot-directory (.godot etc).
    The counts are compared as a manifest check -- a mismatch means the
    walker and this gate disagree about what "everything" is, which is
    itself a failure (the #590 silence-is-failure pattern).
    """
    files = []
    for p in GODOT_PROJECT.rglob("*.gd"):
        rel_parts = p.relative_to(GODOT_PROJECT).parts
        if rel_parts[0] == "addons":
            continue
        if any(part.startswith(".") for part in rel_parts):
            continue
        files.append(p)
    return sorted(files)


def check_syntax(godot_path):
    """Compile-check EVERY non-addon .gd, not just the ones the boot reaches.

    History (issue #1082): the old check ran `--headless --quit`, which BOOTS
    the project -- only autoloads and whatever they pull in get parsed. A file
    with a hard parse error that nothing reaches sailed through as [PASS].
    Per-file `--check-only` is no fix either: in isolation scripts cannot see
    autoloads, so 186/260 real files "fail" (Identifier not found: Balance).

    The fix: run res://tools/syntax_walk.tscn. Booting a scene boots the
    project NORMALLY (autoloads + class_name cache live), then the walker
    force-load()s every .gd outside addons/, which makes the engine parse and
    compile each one; a broken file emits SCRIPT ERROR / "Failed to load
    script" on stderr. Passing requires ALL of:
      (a) the SYNTAX_WALK_COMPLETE marker is present -- proof the walk
          actually ran (#640: silence is failure, the gate fails CLOSED),
      (b) the walker's file count equals this script's own disk glob
          (manifest check, as in #590),
      (c) none of the parse/compile markers appear in the output.
    """
    print("\n[CHECK] Checking GDScript syntax (compile-all walker)...")

    cmd = [godot_path, "--headless", "--path", str(GODOT_PROJECT), SYNTAX_WALK_SCENE]

    # Godot emits benign ERROR lines on headless shutdown (ObjectDB leaks,
    # resources still in use) and for missing imported assets. Only match
    # markers that indicate genuinely broken GDScript source. Matched
    # case-insensitively: the CLI emits "Parse error" but runtime load()
    # emits "SCRIPT ERROR: Parse Error: ..." (different capitalisation).
    REAL_ERROR_MARKERS = [
        "cannot load source code",
        "gdscript error",
        "parse error",
        "failed to load script",
        "compile error",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print("[ERROR] Syntax walker timed out after 300s.")
        return False
    except Exception as e:
        print(f"[ERROR] Syntax check failed to run: {e}")
        return False

    output = result.stdout + result.stderr
    lower = output.lower()
    found_errors = [m for m in REAL_ERROR_MARKERS if m in lower]

    # (a) proof the walk ran at all
    marker = SYNTAX_WALK_MARKER.search(output)
    if marker is None:
        print(
            "[FAIL] Syntax walker did not report completion "
            f"({SYNTAX_WALK_SCENE} missing/broken, or the project failed to boot). "
            "Refusing to pass on silence."
        )
        print(output[-4000:])
        return False

    # (b) manifest: walker count must equal what is on disk
    walked = int(marker.group(1))
    on_disk = len(_disk_gd_files())
    if walked != on_disk:
        print(
            f"[FAIL] Syntax walker compiled {walked} scripts but {on_disk} .gd files "
            "are on disk (excluding addons/). Walker and gate disagree about "
            "coverage -- fix the mismatch, do not trust this run."
        )
        return False

    # (c) no parse/compile markers
    if found_errors:
        print("[FAIL] GDScript syntax errors found (markers: %s):" % found_errors)
        marker_lines = [
            line
            for line in output.splitlines()
            if any(m in line.lower() for m in REAL_ERROR_MARKERS)
        ]
        for line in marker_lines[:80]:
            print("    " + line)
        return False

    print(f"[PASS] GDScript syntax check passed! Compiled {walked}/{on_disk} scripts. CHECKED")
    return True


def _disk_test_files(test_dir):
    """Non-recursive glob of test_*.gd basenames in a res:// test dir."""
    dir_path = GODOT_PROJECT / test_dir.replace("res://", "")
    if not dir_path.exists():
        return None  # signal: directory missing
    return sorted(p.name for p in dir_path.glob("test_*.gd"))


def _parse_junit(junit_path):
    """Parse a GUT JUnit XML file.

    Returns dict {tests, failures, suites:set(basenames), failing_tests:list}
    or None if unparseable. failing_tests is a list of dicts
    {suite, test, message} -- one per failed <testcase>, message truncated to
    one line so it is safe to drop straight into a markdown table cell.
    """
    if not junit_path.exists():
        return None
    try:
        root = ET.parse(junit_path).getroot()  # <testsuites tests= failures= >
        tests = int(root.get("tests", "0"))
        failures = int(root.get("failures", "0"))
        suites = set()
        failing_tests = []
        for suite in root.findall("testsuite"):
            name = suite.get("name", "")  # e.g. "tests/unit/test_foo.gd"
            suite_basename = Path(name).name
            suites.add(suite_basename)
            for case in suite.findall("testcase"):
                fail_el = case.find("failure")
                if fail_el is None:
                    continue
                msg = (fail_el.get("message") or fail_el.text or "").strip()
                msg = msg.splitlines()[0] if msg else "(no message)"
                # Keep table rows sane-length; full text is still in the XML artifact.
                if len(msg) > 160:
                    msg = msg[:157] + "..."
                # Markdown table cells can't contain a literal pipe.
                msg = msg.replace("|", "\\|")
                failing_tests.append(
                    {
                        "suite": suite_basename,
                        "test": case.get("name", "?"),
                        "message": msg,
                    }
                )
        return {
            "tests": tests,
            "failures": failures,
            "suites": suites,
            "failing_tests": failing_tests,
        }
    except ET.ParseError as e:
        print(f"[PARSE][ERROR] JUnit XML at {junit_path} is malformed: {e}")
        return None


def run_gut_tests(godot_path, mode, test_dir, log_level, min_tests):
    """Run one test directory and hard-gate on the JUnit results.

    Returns (ok: bool, tests: int, failures: int, failing_tests: list).
    """
    disk_files = _disk_test_files(test_dir)
    if disk_files is None:
        # A requested-but-missing dir is a FAILURE, not a silent skip. The old
        # runner skipped missing dirs, which is exactly how the smoke gate
        # "passed" while pointing at a nonexistent tests/smoke (#629).
        print(f"\n[FAIL] Test directory {test_dir} does not exist -- cannot run '{mode}'.")
        return (False, 0, 0, [])

    if not disk_files:
        print(f"\n[FAIL] No test_*.gd files found in {test_dir} for '{mode}'.")
        return (False, 0, 0, [])

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
        return (False, 0, 0, [])
    except Exception as e:
        print(f"\n[FAIL] Failed to run tests: {e}")
        return (False, 0, 0, [])

    # --- The gate: trust the JUnit file, not the exit code. ---
    parsed = _parse_junit(junit_fs)
    if parsed is None:
        print(
            f"\n[FAIL] '{mode}': no parseable JUnit results at {junit_fs}. "
            "GUT ran nothing or quit early (missing import pass? bad args?)."
        )
        return (False, 0, 0, [])

    tests = parsed["tests"]
    failures = parsed["failures"]
    collected = parsed["suites"]
    failing_tests = parsed["failing_tests"]

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
    return (ok, tests, failures, failing_tests)


# Modes considered "non-blocking" tiers in CI: a failure here does not fail the
# required gate, so it needs its own loud banner or nobody will ever see it
# (issue #964 -- the simulation tier was red on 5 straight main runs, silently,
# because the only visible signal was a job that stayed green via
# continue-on-error). Keyed by MODE_DIRS name.
NON_BLOCKING_MODES = {"simulation"}


def format_summary_markdown(rows):
    """Build one markdown report shared by GITHUB_STEP_SUMMARY, --summary, and
    the PR-comment step (issue #964). `rows` is a list of
    (mode, tests, failures, ok, failing_tests) tuples.

    Non-blocking tiers (currently: simulation) get an unmissable
    '[!] <MODE> TIER RED' banner plus a per-test failure table when they fail,
    since a plain PASS/FAIL row in a wall of green is exactly what went
    unnoticed for 5 main-branch runs before this was added.
    """
    lines = []

    for mode, tests, failures, ok, failing_tests in rows:
        if not ok and failing_tests and mode in NON_BLOCKING_MODES:
            lines.append("")
            lines.append(f"## [!] {mode.upper()} TIER RED (non-blocking, but real)")
            lines.append("")
            lines.append(
                f"`{mode}` tier: {failures}/{tests} test failures. This tier does "
                "NOT block merges -- it is surfaced here so it is not silently red. "
                "See docs/ARCHITECTURE.md / the sim-tier test files for context."
            )
            lines.append("")
            lines.append("| Suite | Test | Failure |")
            lines.append("|---|---|---|")
            for ft in failing_tests:
                lines.append(f"| {ft['suite']} | {ft['test']} | {ft['message']} |")
            lines.append("")

    lines.append("")
    lines.append("### Godot test results")
    lines.append("")
    lines.append("| Suite | Tests | Failures | Result |")
    lines.append("|---|---:|---:|---|")
    for mode, tests, failures, ok, _failing_tests in rows:
        tier_note = " (non-blocking)" if mode in NON_BLOCKING_MODES else ""
        lines.append(f"| {mode}{tier_note} | {tests} | {failures} | {'PASS' if ok else 'FAIL'} |")
    lines.append("")

    return "\n".join(lines)


def _write_step_summary(rows):
    """Append the shared markdown report to GITHUB_STEP_SUMMARY so a human sees
    'N tests ran' -- and, for non-blocking tiers, the [!] RED banner -- with one
    click on the GitHub Actions run page.
    """
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(format_summary_markdown(rows))
    except Exception as e:
        print(f"[WARN] Could not write step summary: {e}")


def _write_summary_file(rows, out_path):
    """Write the shared markdown report to a plain file (used by --summary /
    downstream CI steps such as the PR-comment job, which cannot see another
    job's GITHUB_STEP_SUMMARY and needs the content as a build artifact).
    """
    try:
        out_path.write_text(format_summary_markdown(rows), encoding="utf-8")
        print(f"\n[SUMMARY] Wrote markdown summary to {out_path}")
    except Exception as e:
        print(f"[WARN] Could not write summary file {out_path}: {e}")


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
    parser.add_argument(
        "--summary",
        action="store_true",
        help=(
            "Print the shared markdown summary (counts table + [!] RED banner/"
            "failure table for any non-blocking tier that failed) to stdout at "
            "the end of the run. Same formatter CI uses for GITHUB_STEP_SUMMARY "
            "and the PR-comment step (#964), so local runs and CI agree."
        ),
    )
    parser.add_argument(
        "--summary-file",
        dest="summary_file",
        default=None,
        help=(
            "Also write the shared markdown summary to this path (e.g. for a "
            "downstream CI job / artifact to consume, since GITHUB_STEP_SUMMARY "
            "is not visible across jobs)."
        ),
    )

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
        ok, tests, failures, failing_tests = run_gut_tests(
            godot_path, mode, MODE_DIRS[mode], log_level, args.min_tests
        )
        summary_rows.append((mode, tests, failures, ok, failing_tests))
        all_passed = all_passed and ok

    _write_step_summary(summary_rows)
    if args.summary_file:
        _write_summary_file(summary_rows, Path(args.summary_file))
    if args.summary:
        print("\n" + format_summary_markdown(summary_rows))

    print("\n" + "=" * 60)
    print(
        "[TOTALS] "
        + " | ".join(
            f"{m}: {t} tests, {fl} fail ({'ok' if o else 'FAIL'})"
            for (m, t, fl, o, _ft) in summary_rows
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
