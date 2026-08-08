#!/usr/bin/env python3
"""
Run Godot GUT (Godot Unit Test) tests from command line.

Layer: PROVE

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

Three outcomes, not two (#1181 / #1168): PASS / FAIL / NO RESULT. Point 2 above
says a number that did not come from tests executing must not be trusted; the
timeout path used to break that rule in the runner's own reporting. A run killed
by the wall-clock cap produced no JUnit file, so no test count exists for it --
yet it rendered as `simulation: 0 tests, 0 fail (FAIL)`, character-identical in
shape to a measured result, and as `| simulation | 0 | 0 | FAIL |` in the CI
summary table. Now a killed run reports NO RESULT, prints `-` where the counts
would go, and exits 2 (distinct from 1 = measured failure, 0 = measured pass).
The cap itself is `--timeout` / `PDOOM1_TEST_TIMEOUT`, default 900s -- the same
900 that was hardcoded before, so CI's contract is unchanged.

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
    python scripts/run_godot_tests.py --simulation --timeout 3600  # slow box (#1181)
    python scripts/run_godot_tests.py --simulation --timeout 0     # no cap at all

Exit codes: 0 = measured pass, 1 = measured failure, 2 = NO RESULT (the run did
not complete, so no measurement exists -- do not report a suite result from it).
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
GODOT_PROJECT = PROJECT_ROOT / "godot"


def _isolated_env():
    """Environment for every Godot invocation, with `user://` pointed AWAY from the
    developer's real profile.

    MEASURED DAMAGE, not a precaution. Godot derives the user data dir from
    `config/name` in project.godot ("P(Doom)"), NOT from the checkout path, so every
    worktree on a machine shares ONE profile:
    `%APPDATA%/Godot/app_userdata/P(Doom)/`. These subprocesses previously inherited
    the developer's APPDATA, so a headless test run wrote into live player data --
    on 2026-08-07 a test run took Pip's 2026-07-31 league board from 50 entries to 0,
    and rewrote his config.cfg / keybinds.cfg / theme.cfg. `test_leaderboard_sync.gd`
    writes the outbox, `test_default_identity_prompt.gd` calls GameConfig.save_config(),
    and `test_leaderboard_properties.gd` creates a board file per property iteration.

    Only APPDATA works on Windows. XDG_DATA_HOME was tried and has NO effect there
    (proven by execution, 2026-08-07); on Linux/macOS the XDG/HOME vars are what bite,
    so all three are redirected.

    REJECTED: setting `use_custom_user_dir` in project.godot. That ships to players and
    would relocate every real player's saves.

    The sandbox is keyed by a hash of the checkout path so concurrent worktrees do not
    collide with each other either.
    """
    key = hashlib.sha1(str(PROJECT_ROOT.resolve()).encode("utf-8")).hexdigest()[:12]
    sandbox = Path(tempfile.gettempdir()) / "pdoom1-godot-userdata" / key
    sandbox.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["APPDATA"] = str(sandbox)  # Windows: the only var that moves user://
    env["XDG_DATA_HOME"] = str(sandbox)  # Linux (CI)
    env["HOME"] = str(sandbox)  # macOS / Linux fallback
    env["PDOOM1_USERDATA_SANDBOX"] = str(sandbox)  # read by the in-engine guard test
    return env


ISOLATED_ENV = _isolated_env()

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


# --- Outcomes (#1181) -------------------------------------------------------
# Three states, deliberately not two. FAILED means "we measured, and it was
# bad". NO_RESULT means "we did not measure": there is no count, no verdict, and
# it must never be renderable in the shape of the former.
PASSED = "PASS"
FAILED = "FAIL"
NO_RESULT = "NO RESULT"

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_NO_RESULT = 2

# The wall-clock cap for one GUT invocation. 900 is the value that was hardcoded
# at scripts/run_godot_tests.py:375 before #1181; it is kept as the default so
# CI's behaviour is byte-identical unless someone opts out. It is now a
# parameter because there is no single number right for every machine: the
# Ubuntu CI runner completes the simulation tier in 460-550s, while Pip's
# Windows box (concurrent agent lanes, art generation, several Godot instances)
# was still emitting live GUT progress at 27m10s. A cap that cannot be raised
# means that machine can never obtain a result from that tier at all.
DEFAULT_TIMEOUT = 900
TIMEOUT_ENV_VAR = "PDOOM1_TEST_TIMEOUT"


def resolve_timeout(cli_timeout):
    """Resolve the per-run wall-clock cap.

    Precedence: --timeout, then $PDOOM1_TEST_TIMEOUT, then DEFAULT_TIMEOUT.
    Returns (seconds_or_None, provenance_string); None means no cap at all
    (`--timeout 0`). The provenance is printed, because an implicit cap that
    silently destroys a measurement is the defect being fixed here -- the reader
    should never have to guess which number was in force.
    """
    seconds = DEFAULT_TIMEOUT
    source = "default"
    if cli_timeout is not None:
        seconds, source = cli_timeout, "--timeout"
    else:
        raw = os.environ.get(TIMEOUT_ENV_VAR, "").strip()
        if raw:
            try:
                seconds, source = int(raw), f"${TIMEOUT_ENV_VAR}"
            except ValueError:
                print(
                    f"[WARN] {TIMEOUT_ENV_VAR}={raw!r} is not an integer; "
                    f"falling back to the {DEFAULT_TIMEOUT}s default."
                )
    if seconds <= 0:
        return None, f"{source} (cap DISABLED)"
    return seconds, source


def _no_result(mode, detail):
    """Build a result row for a run that produced no measurement."""
    return {
        "mode": mode,
        "outcome": NO_RESULT,
        "tests": None,
        "failures": None,
        "failing_tests": [],
        "detail": detail,
    }


def find_godot():
    """Find Godot executable on system."""
    for path in GODOT_PATHS:
        try:
            result = subprocess.run(
                [path, "--version"], capture_output=True, text=True, timeout=15, env=ISOLATED_ENV
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


def run_import(godot_path):
    """Populate the class cache so GUT does not quit(0) before running tests.

    This is THE fix for the zero-test false-green (#629): a fresh checkout has no
    .godot/global_script_class_cache, so GUT's error_if_not_all_classes_imported()
    is true and it quits immediately.
    """
    print("\n[IMPORT] Running headless import pass (populates class cache)...")
    cmd = [godot_path, "--headless", "--path", str(GODOT_PROJECT), "--import"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=ISOLATED_ENV)
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
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=ISOLATED_ENV)
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


def _fail_row(mode, tests=0, failures=0, failing_tests=None):
    return {
        "mode": mode,
        "outcome": FAILED,
        "tests": tests,
        "failures": failures,
        "failing_tests": failing_tests or [],
        "detail": "",
    }


def run_gut_tests(godot_path, mode, test_dir, log_level, min_tests, timeout=DEFAULT_TIMEOUT):
    """Run one test directory and hard-gate on the JUnit results.

    Returns a result dict: {mode, outcome, tests, failures, failing_tests,
    detail}. `outcome` is PASSED / FAILED / NO_RESULT. When outcome is
    NO_RESULT, `tests` and `failures` are None -- there is deliberately no
    number to print, because no number was measured.
    """
    disk_files = _disk_test_files(test_dir)
    if disk_files is None:
        # A requested-but-missing dir is a FAILURE, not a silent skip. The old
        # runner skipped missing dirs, which is exactly how the smoke gate
        # "passed" while pointing at a nonexistent tests/smoke (#629).
        print(f"\n[FAIL] Test directory {test_dir} does not exist -- cannot run '{mode}'.")
        return _fail_row(mode)

    if not disk_files:
        print(f"\n[FAIL] No test_*.gd files found in {test_dir} for '{mode}'.")
        return _fail_row(mode)

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
    started = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            cwd=GODOT_PROJECT,
            capture_output=False,
            text=True,
            timeout=timeout,
            env=ISOLATED_ENV,
        )
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - started
        detail = (
            f"killed by the {timeout}s wall-clock cap after {elapsed:.0f}s, before "
            "GUT wrote any results. Raise the cap with --timeout N (or "
            f"{TIMEOUT_ENV_VAR}=N), or --timeout 0 to remove it."
        )
        print("\n" + "!" * 68)
        print(f"[NO RESULT] '{mode}': TIMED OUT after {elapsed:.0f}s (cap {timeout}s).")
        print("[NO RESULT] No JUnit file was written, so there is NO test count for")
        print("[NO RESULT] this run: nothing passed and nothing failed. This is NOT a")
        print("[NO RESULT] green run and NOT a measured failure -- it is an absence of")
        print("[NO RESULT] measurement. Do not report a suite result from it.")
        print(f"[NO RESULT] Fix: --timeout N / {TIMEOUT_ENV_VAR}=N (0 removes the cap).")
        print("!" * 68)
        return _no_result(mode, detail)
    except Exception as e:
        detail = f"the Godot process could not be run to completion: {e}"
        print(f"\n[NO RESULT] '{mode}': failed to run tests -- {e}")
        print("[NO RESULT] No measurement exists for this run (not a pass, not a failure).")
        return _no_result(mode, detail)

    # --- The gate: trust the JUnit file, not the exit code. ---
    parsed = _parse_junit(junit_fs)
    if parsed is None:
        print(
            f"\n[FAIL] '{mode}': no parseable JUnit results at {junit_fs}. "
            "GUT ran nothing or quit early (missing import pass? bad args?)."
        )
        return _fail_row(mode)

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

    status = PASSED if ok else FAILED
    print(
        f"\n[{status}] '{mode}': {tests} tests, {failures} failures, "
        f"{len(collected)}/{len(disk_files)} files collected."
    )
    return {
        "mode": mode,
        "outcome": status,
        "tests": tests,
        "failures": failures,
        "failing_tests": failing_tests,
        "detail": "",
    }


# Modes considered "non-blocking" tiers in CI: a failure here does not fail the
# required gate, so it needs its own loud banner or nobody will ever see it
# (issue #964 -- the simulation tier was red on 5 straight main runs, silently,
# because the only visible signal was a job that stayed green via
# continue-on-error). Keyed by MODE_DIRS name.
NON_BLOCKING_MODES = {"simulation"}


def format_totals_line(rows):
    """The one-line [TOTALS] verdict.

    A NO_RESULT row prints no counts at all. Before #1181 it printed
    `0 tests, 0 fail (FAIL)` -- literally true and completely misleading, since
    "0 fail" describes a run that never happened.
    """
    parts = []
    for r in rows:
        if r["outcome"] == NO_RESULT:
            parts.append(f"{r['mode']}: NO RESULT -- run did not complete, no test count exists")
        else:
            parts.append(
                f"{r['mode']}: {r['tests']} tests, {r['failures']} fail "
                f"({'ok' if r['outcome'] == PASSED else 'FAIL'})"
            )
    return "[TOTALS] " + " | ".join(parts)


def decide_exit(rows):
    """0 measured pass / 1 measured failure / 2 no measurement.

    NO_RESULT outranks FAILED: if any tier did not run, the most important thing
    to tell the caller is that the run cannot be reported on, not that some
    other tier was red.
    """
    if any(r["outcome"] == NO_RESULT for r in rows):
        return EXIT_NO_RESULT
    if any(r["outcome"] == FAILED for r in rows):
        return EXIT_FAILED
    return EXIT_OK


def format_summary_markdown(rows):
    """Build one markdown report shared by GITHUB_STEP_SUMMARY, --summary, and
    the PR-comment step (issue #964). `rows` is a list of result dicts from
    run_gut_tests().

    Non-blocking tiers (currently: simulation) get an unmissable
    '[!] <MODE> TIER RED' banner plus a per-test failure table when they fail,
    since a plain PASS/FAIL row in a wall of green is exactly what went
    unnoticed for 5 main-branch runs before this was added.

    A tier that did NOT COMPLETE gets its own banner and renders its counts as
    `-`, never as 0 (#1181): the simulation tier is non-blocking in CI, so a
    timeout there would otherwise appear as a quiet `| simulation | 0 | 0 |`
    row that a reader would have to already know how to distrust.
    """
    lines = []

    for r in rows:
        if r["outcome"] != NO_RESULT:
            continue
        lines.append("")
        lines.append(f"## [!] {r['mode'].upper()} DID NOT COMPLETE -- NO RESULT")
        lines.append("")
        lines.append(
            f"`{r['mode']}` was {r['detail']} No test count exists for this run: it "
            "is neither a pass nor a failure. Treat this tier as UNMEASURED and do "
            "not quote a suite result from it."
        )
        lines.append("")

    for r in rows:
        if r["outcome"] == FAILED and r["failing_tests"] and r["mode"] in NON_BLOCKING_MODES:
            lines.append("")
            lines.append(f"## [!] {r['mode'].upper()} TIER RED (non-blocking, but real)")
            lines.append("")
            lines.append(
                f"`{r['mode']}` tier: {r['failures']}/{r['tests']} test failures. This "
                "tier does NOT block merges -- it is surfaced here so it is not "
                "silently red. See docs/ARCHITECTURE.md / the sim-tier test files "
                "for context."
            )
            lines.append("")
            lines.append("| Suite | Test | Failure |")
            lines.append("|---|---|---|")
            for ft in r["failing_tests"]:
                lines.append(f"| {ft['suite']} | {ft['test']} | {ft['message']} |")
            lines.append("")

    lines.append("")
    lines.append("### Godot test results")
    lines.append("")
    lines.append("| Suite | Tests | Failures | Result |")
    lines.append("|---|---:|---:|---|")
    for r in rows:
        tier_note = " (non-blocking)" if r["mode"] in NON_BLOCKING_MODES else ""
        if r["outcome"] == NO_RESULT:
            lines.append(f"| {r['mode']}{tier_note} | - | - | **NO RESULT (did not run)** |")
        else:
            lines.append(
                f"| {r['mode']}{tier_note} | {r['tests']} | {r['failures']} | {r['outcome']} |"
            )
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
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help=(
            "Wall-clock cap in seconds for EACH GUT run. Default "
            f"{DEFAULT_TIMEOUT} -- the same value that was hardcoded before "
            "#1181, so CI behaviour is unchanged. 0 removes the cap entirely. "
            f"Env fallback: {TIMEOUT_ENV_VAR}. Exceeding the cap is reported as "
            "NO RESULT (exit 2), never as a test failure."
        ),
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

    timeout, provenance = resolve_timeout(args.timeout)
    print(
        "\n[TIMEOUT] Per-run wall-clock cap: "
        + (f"{timeout}s" if timeout else "DISABLED")
        + f" (from {provenance})."
    )

    summary_rows = []
    for mode in modes:
        summary_rows.append(
            run_gut_tests(godot_path, mode, MODE_DIRS[mode], log_level, args.min_tests, timeout)
        )

    _write_step_summary(summary_rows)
    if args.summary_file:
        _write_summary_file(summary_rows, Path(args.summary_file))
    if args.summary:
        print("\n" + format_summary_markdown(summary_rows))

    print("\n" + "=" * 60)
    print(format_totals_line(summary_rows))

    incomplete = [r for r in summary_rows if r["outcome"] == NO_RESULT]
    if incomplete:
        print(
            "[NO RESULT] "
            + ", ".join(r["mode"] for r in incomplete)
            + " did not run to completion. This is NOT a pass and NOT a test "
            "failure -- no measurement exists. Do not report a suite result "
            "from this run."
        )
        for r in incomplete:
            print(f"            {r['mode']}: {r['detail']}")
    elif any(r["outcome"] == FAILED for r in summary_rows):
        print("[FAILURE] Gate failed (see above).")
    else:
        print("[SUCCESS] All requested suites passed the gate! CHECKED")
    print("=" * 60)
    sys.exit(decide_exit(summary_rows))


if __name__ == "__main__":
    main()
