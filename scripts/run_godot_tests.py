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

Three outcomes, not two (#1181): PASSED / FAILED / DID-NOT-COMPLETE. A run that
was killed by the timeout never produced a test count, so the runner refuses to
print one -- the counts render as `-`, the word FAIL never appears, and the exit
code is 2 (distinct from 1 = measured failure, 0 = measured pass). This is the
#640 rule pointed at the runner itself: a number that did not come from tests
executing must not be shown in the shape of one. Cutting v0.14.1 a timeout
rendered as `simulation: 0 tests, 0 fail (FAIL)`, which a human had to
disambiguate from a real failure by reading a process list.

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
    python scripts/run_godot_tests.py --simulation --timeout 3600   # slow box (#1181)
    python scripts/run_godot_tests.py --simulation --timeout 0      # no cap at all

Exit codes: 0 = measured pass, 1 = measured failure, 2 = DID NOT COMPLETE
(timeout / stall / could not launch -- no measurement exists).
"""

import argparse
import collections
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import threading
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
#
# PDOOM1_GODOT wins when set, because the hardcoded list below is a guess about
# one machine and it went stale: after the PC migration Godot lived at
# D:/Local_Code/_tools/Godot/, not in Program Files, and this runner reported
# "Could not find Godot executable" with no way to tell it otherwise.
#
# The bare "godot" entry is NOT a working fallback on Windows. subprocess calls
# CreateProcess, which does not apply PATHEXT, so an extensionless shim on PATH
# raises FileNotFoundError -- measured 2026-08-21: 'godot' -> WinError 2 while
# 'godot.bat' -> 0. It stays only because it does work on Linux/macOS.
GODOT_PATHS = [
    p
    for p in (
        os.environ.get("PDOOM1_GODOT"),
        "C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe",
        "godot",  # System PATH (POSIX only -- see note above)
        "godot.bat",  # Windows PATH shim
        "/usr/bin/godot",
        "/usr/local/bin/godot",
    )
    if p
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
# bad". NO_RESULT means "we did not measure" -- no count, no verdict, and it
# must never be renderable as the former.
PASSED = "PASSED"
FAILED = "FAILED"
NO_RESULT = "DID-NOT-COMPLETE"

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_NO_RESULT = 2

# --- Timeout defaults (#1181) -----------------------------------------------
# The cap exists to bound a HUNG process, not to enforce a performance budget,
# and the two ways of being wrong are wildly asymmetric:
#   too low  -> destroys a measurement that was about to succeed, costs a full
#               re-run, and (before this change) reported the destruction as a
#               test failure;
#   too high -> costs wall clock ONLY when something is genuinely stuck, and
#               the stall detector below now catches that case in minutes.
# So the total cap should sit well above the slowest observed HEALTHY run on
# the slowest machine we care about, and the real hang detector should be
# "no output for N seconds" -- hung means no progress, slow means progress.
#
# Measured while fixing #1181, on Pip's Windows box, through the streaming path
# below (5 runs, 107 tests and 0 failures every time):
#     5731dd2e  pre-#1137 ....... 434s, 412s   (mean 423s)
#     8791ba47  the #1137 merge . 584s
#     1ddb033d  main ............ 586s, 619s   (mean 602s)
# So the local sim tier is ~7-10 min, comparable to CI's 460-550s -- NOT the
# ">1630s and still going" that motivated this issue. What made it unrunnable
# was never the platform, the machine load, or the #1137 retiming: it was the
# runner handing Godot an inherited stdout (see _stream_process for the table).
#
# So why keep a parameter at all, if local and CI now agree? Because a cap is
# insurance against the case we have not measured, and the cost of setting it
# too low is the whole of this issue. 2700s locally is ~4.4x the slowest healthy
# run observed here; CI stays at 900s so its contract is unchanged. Both are
# defaults, not budgets -- override freely.
DEFAULT_TIMEOUT_CI = 900
DEFAULT_TIMEOUT_LOCAL = {"simulation": 2700}
DEFAULT_TIMEOUT_LOCAL_OTHER = 900
DEFAULT_STALL_TIMEOUT = 300
DEFAULT_HEARTBEAT = 30


def _in_ci():
    return os.environ.get("CI", "").lower() in ("1", "true", "yes")


def resolve_timeout(mode, cli_timeout):
    """Return (seconds, human-readable provenance). 0/negative == no cap."""
    if cli_timeout is not None:
        return cli_timeout, "--timeout"
    env = os.environ.get("PDOOM1_TEST_TIMEOUT")
    if env:
        try:
            return int(env), "PDOOM1_TEST_TIMEOUT env"
        except ValueError:
            print(f"[WARN] PDOOM1_TEST_TIMEOUT={env!r} is not an integer; ignoring.")
    if _in_ci():
        return DEFAULT_TIMEOUT_CI, "default (CI)"
    return (
        DEFAULT_TIMEOUT_LOCAL.get(mode, DEFAULT_TIMEOUT_LOCAL_OTHER),
        "default (local, no CI env var)",
    )


def _stream_process(cmd, cwd, env, timeout, stall_timeout, heartbeat, label, echo=True):
    """Run a subprocess, streaming its output, with a heartbeat and a stall detector.

    Returns (status, exit_code, elapsed_seconds, output_text) where status is one
    of "completed" / "timeout" / "stall" / "error".

    Why streaming rather than subprocess.run(): with capture_output the caller
    sees nothing until the end, and with capture_output=False the caller sees
    text but the RUNNER sees nothing -- so it cannot tell a slow run from a hung
    one. On 2026-08-08 that distinction cost the most time of anything in the
    incident behind #1181; it was settled by checking process RSS in `tasklist`.
    Reading the pipe ourselves gives us both: the human still sees GUT's output
    live, and we get a last-output timestamp to hang the stall detector on.

    Owning the pipe is ALSO what makes the sim tier runnable locally at all, and
    that was the surprise in #1181. `capture_output=False` handed Godot whatever
    stdout the parent happened to have, and Godot's per-line write cost depends
    enormously on what that is. Measured on one Windows box, 200,000 identical
    print() calls from the same headless build:

        native Win32 pipe, drained by this reader ....  2.42s  (82,600/s)
        Git Bash `> file` redirect .................. 432.3s  (   463/s)
        Git Bash `| cat` (MSYS pipe) ................ ~2900s  (    68/s)
        redirected to NUL ...........................  1.25s

    The sim tier emits ~4-5M lines per run, so a 100x per-line penalty is the
    difference between 8 minutes and most of a day. Which is why the echo below
    is BATCHED: writing 5M lines one at a time to a Windows console would
    reintroduce the exact pathology on the runner's own side of the pipe.
    """
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            errors="replace",
        )
    except Exception as e:
        return ("error", None, 0.0, f"failed to launch: {e}")

    # Keep only a tail in memory: the sim tier emits tens of thousands of RNG
    # trace lines and we only ever print the tail on failure.
    buf = collections.deque(maxlen=4000)
    state = {"lines": 0, "last_at": time.monotonic(), "last_line": ""}
    lock = threading.Lock()

    def _reader():
        pending = []
        last_flush = time.monotonic()

        def _flush():
            if pending:
                sys.stdout.write("".join(pending))
                sys.stdout.flush()
                pending.clear()

        try:
            for line in proc.stdout:
                with lock:
                    state["lines"] += 1
                    state["last_at"] = time.monotonic()
                    stripped = line.rstrip()
                    if stripped:
                        state["last_line"] = stripped
                buf.append(line)
                if echo:
                    pending.append(line)
                    now = time.monotonic()
                    # Batch: one write per 500 lines or per 0.25s, whichever
                    # comes first. Keeps output feeling live without paying a
                    # syscall per line on a slow sink (see the table above).
                    if len(pending) >= 500 or (now - last_flush) >= 0.25:
                        _flush()
                        last_flush = now
            if echo:
                _flush()
        except Exception:
            pass
        finally:
            try:
                proc.stdout.close()
            except Exception:
                pass

    reader = threading.Thread(target=_reader, daemon=True)
    reader.start()

    start = time.monotonic()
    last_beat = start
    status = "completed"
    while True:
        rc = proc.poll()
        if rc is not None:
            break
        now = time.monotonic()
        with lock:
            lines = state["lines"]
            quiet_for = now - state["last_at"]
            last_line = state["last_line"]
        if timeout and (now - start) > timeout:
            status = "timeout"
            break
        if stall_timeout and quiet_for > stall_timeout:
            status = "stall"
            break
        if now - last_beat >= heartbeat:
            last_beat = now
            print(
                f"[PROGRESS] {label}: {int(now - start)}s elapsed, {lines} output lines, "
                f"{int(quiet_for)}s since last output | {last_line[:100]}",
                flush=True,
            )
        time.sleep(0.5)

    elapsed = time.monotonic() - start
    if status != "completed":
        print(
            f"\n[KILL] {label}: {status} -- terminating process after {int(elapsed)}s.", flush=True
        )
        try:
            proc.kill()
            proc.wait(timeout=30)
        except Exception:
            pass
        rc = None
    reader.join(timeout=10)
    return (status, rc, elapsed, "".join(buf))


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


def run_import(godot_path, heartbeat=DEFAULT_HEARTBEAT):
    """Populate the class cache so GUT does not quit(0) before running tests.

    This is THE fix for the zero-test false-green (#629): a fresh checkout has no
    .godot/global_script_class_cache, so GUT's error_if_not_all_classes_imported()
    is true and it quits immediately.
    """
    print("\n[IMPORT] Running headless import pass (populates class cache)...")
    cmd = [godot_path, "--headless", "--path", str(GODOT_PROJECT), "--import"]
    status, exit_code, elapsed, tail = _stream_process(
        cmd,
        cwd=None,
        env=ISOLATED_ENV,
        timeout=600,
        stall_timeout=None,  # the import pass is legitimately silent for long stretches
        heartbeat=heartbeat,
        label="import",
        echo=False,  # ~1200 asset lines; only the tail is useful, and only on failure
    )
    if status != "completed":
        print(f"[IMPORT][NO RESULT] Import pass did not complete ({status}) after {int(elapsed)}s.")
        print(tail[-2000:])
        return NO_RESULT
    # --import can exit non-zero on benign asset warnings; only treat a hard
    # failure (no cache produced) as fatal. The cache file confirms success.
    cache = GODOT_PROJECT / ".godot" / "global_script_class_cache.cfg"
    if cache.exists():
        print(f"[IMPORT] Class cache present -- import OK ({int(elapsed)}s).")
        return PASSED
    print("[IMPORT][WARN] class cache missing after import; exit", exit_code)
    print(tail[-2000:])
    return FAILED


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


def check_syntax(godot_path, heartbeat=DEFAULT_HEARTBEAT):
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

    status, _exit_code, elapsed, output = _stream_process(
        cmd,
        cwd=None,
        env=ISOLATED_ENV,
        timeout=600,
        stall_timeout=None,
        heartbeat=heartbeat,
        label="syntax",
        echo=False,
    )
    if status != "completed":
        # Not "syntax is broken" -- we never got to find out (#1181).
        print(f"[NO RESULT] Syntax walker did not complete ({status}) after {int(elapsed)}s.")
        print(output[-2000:])
        return NO_RESULT

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
        return FAILED

    # (b) manifest: walker count must equal what is on disk
    walked = int(marker.group(1))
    on_disk = len(_disk_gd_files())
    if walked != on_disk:
        print(
            f"[FAIL] Syntax walker compiled {walked} scripts but {on_disk} .gd files "
            "are on disk (excluding addons/). Walker and gate disagree about "
            "coverage -- fix the mismatch, do not trust this run."
        )
        return FAILED

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
        return FAILED

    print(f"[PASS] GDScript syntax check passed! Compiled {walked}/{on_disk} scripts. CHECKED")
    return PASSED


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


def _result(mode, outcome, tests=None, failures=None, failing_tests=None, detail="", elapsed=0.0):
    """One suite's outcome. tests/failures are None whenever they were never
    measured -- the whole point of #1181 is that an unmeasured count must not be
    representable as 0."""
    return {
        "mode": mode,
        "outcome": outcome,
        "tests": tests,
        "failures": failures,
        "failing_tests": failing_tests or [],
        "detail": detail,
        "elapsed": elapsed,
    }


def run_gut_tests(
    godot_path, mode, test_dir, log_level, min_tests, timeout, stall_timeout, heartbeat
):
    """Run one test directory and hard-gate on the JUnit results.

    Returns a result dict (see _result). Outcome is PASSED, FAILED, or
    NO_RESULT; NO_RESULT is reserved for "the process did not finish", i.e. we
    have no measurement at all. A process that DID finish and produced nothing
    parseable is a FAILED -- we watched it run and produce nothing, which is the
    #629/#590 silence-is-failure case and a genuine measurement.
    """
    disk_files = _disk_test_files(test_dir)
    if disk_files is None:
        # A requested-but-missing dir is a FAILURE, not a silent skip. The old
        # runner skipped missing dirs, which is exactly how the smoke gate
        # "passed" while pointing at a nonexistent tests/smoke (#629).
        print(f"\n[FAIL] Test directory {test_dir} does not exist -- cannot run '{mode}'.")
        return _result(mode, FAILED, 0, 0, detail=f"test directory {test_dir} does not exist")

    if not disk_files:
        print(f"\n[FAIL] No test_*.gd files found in {test_dir} for '{mode}'.")
        return _result(mode, FAILED, 0, 0, detail=f"no test_*.gd files in {test_dir}")

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

    status, exit_code, elapsed, tail = _stream_process(
        cmd,
        cwd=GODOT_PROJECT,
        env=ISOLATED_ENV,
        timeout=timeout,
        stall_timeout=stall_timeout,
        heartbeat=heartbeat,
        label=mode,
    )

    if status != "completed":
        # NOT a test result. No count is known, so none is reported.
        if status == "timeout":
            detail = (
                f"timed out after {int(elapsed)}s (cap {timeout}s) -- the run was killed, "
                "so NO test count exists. Raise the cap with --timeout SECONDS "
                "(or PDOOM1_TEST_TIMEOUT) and re-run; this is not a test failure."
            )
        elif status == "stall":
            detail = (
                f"produced no output for {stall_timeout}s and was killed at {int(elapsed)}s "
                "-- looks genuinely hung rather than slow. NO test count exists."
            )
        else:
            detail = f"could not be launched/run: {tail[-300:]}"
        print(f"\n[NO RESULT] '{mode}': {detail}")
        print("[NO RESULT] This is the ABSENCE of a measurement, not a failing measurement.")
        return _result(mode, NO_RESULT, None, None, detail=detail, elapsed=elapsed)

    # --- The gate: trust the JUnit file, not the exit code. ---
    parsed = _parse_junit(junit_fs)
    if parsed is None:
        print(
            f"\n[FAIL] '{mode}': no parseable JUnit results at {junit_fs}. "
            "GUT ran nothing or quit early (missing import pass? bad args?)."
        )
        return _result(
            mode,
            FAILED,
            0,
            0,
            detail="no parseable JUnit results (GUT quit early)",
            elapsed=elapsed,
        )

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

    label = "PASS" if ok else "FAIL"
    print(
        f"\n[{label}] '{mode}': {tests} tests, {failures} failures, "
        f"{len(collected)}/{len(disk_files)} files collected, {int(elapsed)}s."
    )
    return _result(
        mode,
        PASSED if ok else FAILED,
        tests,
        failures,
        failing_tests,
        detail="",
        elapsed=elapsed,
    )


# Modes considered "non-blocking" tiers in CI: a failure here does not fail the
# required gate, so it needs its own loud banner or nobody will ever see it
# (issue #964 -- the simulation tier was red on 5 straight main runs, silently,
# because the only visible signal was a job that stayed green via
# continue-on-error). Keyed by MODE_DIRS name.
NON_BLOCKING_MODES = {"simulation"}


def _count(v):
    """Render a count that may never have been measured. '-' is deliberate: a
    dash cannot be mistaken for a measured zero (#1181)."""
    return "-" if v is None else str(v)


def format_summary_markdown(rows):
    """Build one markdown report shared by GITHUB_STEP_SUMMARY, --summary, and
    the PR-comment step (issue #964). `rows` is a list of result dicts
    (see _result).

    Non-blocking tiers (currently: simulation) get an unmissable
    '[!] <MODE> TIER RED' banner plus a per-test failure table when they fail,
    since a plain PASS/FAIL row in a wall of green is exactly what went
    unnoticed for 5 main-branch runs before this was added.

    A DID-NOT-COMPLETE tier gets its OWN banner, distinct from RED, because it
    is a different claim: RED says the tier is broken, NO RESULT says we do not
    know (#1181).
    """
    lines = []

    for r in rows:
        mode = r["mode"]
        if r["outcome"] == NO_RESULT:
            lines.append("")
            lines.append(f"## [?] {mode.upper()} TIER: NO RESULT (not run to completion)")
            lines.append("")
            lines.append(
                f"`{mode}` did not finish, so there is no pass/fail verdict and no test "
                f"count for it. Reason: {r['detail']}"
            )
            lines.append("")
            lines.append(
                "Do NOT read this as a failure and do NOT read it as a pass. "
                "Nothing was measured."
            )
            lines.append("")
        elif r["outcome"] == FAILED and r["failing_tests"] and mode in NON_BLOCKING_MODES:
            lines.append("")
            lines.append(f"## [!] {mode.upper()} TIER RED (non-blocking, but real)")
            lines.append("")
            lines.append(
                f"`{mode}` tier: {r['failures']}/{r['tests']} test failures. This tier does "
                "NOT block merges -- it is surfaced here so it is not silently red. "
                "See docs/ARCHITECTURE.md / the sim-tier test files for context."
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
        verdict = {PASSED: "PASS", FAILED: "FAIL", NO_RESULT: "NO RESULT (not measured)"}[
            r["outcome"]
        ]
        lines.append(
            f"| {r['mode']}{tier_note} | {_count(r['tests'])} | "
            f"{_count(r['failures'])} | {verdict} |"
        )
    lines.append("")

    return "\n".join(lines)


def format_totals_line(rows):
    """The one-line TOTALS report.

    This single line is the whole of #1181: under the old runner a timed-out
    simulation tier rendered here as `simulation: 0 tests, 0 fail (FAIL)` --
    two invented numbers and a verdict, none of which came from a test running.
    A suite that did not complete now gets NO numbers and no verdict.
    """
    parts = []
    for r in rows:
        if r["outcome"] == NO_RESULT:
            parts.append(f"{r['mode']}: DID NOT COMPLETE after {int(r['elapsed'])}s -- NO RESULT")
        else:
            parts.append(
                f"{r['mode']}: {r['tests']} tests, {r['failures']} fail "
                f"({'ok' if r['outcome'] == PASSED else 'FAIL'})"
            )
    return "[TOTALS] " + " | ".join(parts)


def decide_exit(rows):
    """Exit code from outcomes. Incompleteness OUTRANKS failure: if any suite
    did not finish we cannot claim to know the state of the run, so 2 (no
    result) is more honest than 1 (measured failure)."""
    if any(r["outcome"] == NO_RESULT for r in rows):
        return EXIT_NO_RESULT
    if any(r["outcome"] == FAILED for r in rows):
        return EXIT_FAILED
    return EXIT_OK


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
        "--timeout",
        type=int,
        default=None,
        help=(
            "Wall-clock cap in seconds per suite. 0 = no cap. Overrides "
            "PDOOM1_TEST_TIMEOUT. Default: 900 in CI; locally 2700 for the "
            "simulation tier and 900 elsewhere (#1181). Hitting the cap is "
            "reported as DID-NOT-COMPLETE, never as a test failure."
        ),
    )
    parser.add_argument(
        "--stall-timeout",
        type=int,
        default=DEFAULT_STALL_TIMEOUT,
        dest="stall_timeout",
        help=(
            "Kill a suite that has produced NO output for this many seconds "
            f"(default {DEFAULT_STALL_TIMEOUT}; 0 disables). This -- not the "
            "wall-clock cap -- is the hang detector: hung means no progress, "
            "slow means progress."
        ),
    )
    parser.add_argument(
        "--heartbeat",
        type=int,
        default=DEFAULT_HEARTBEAT,
        help=(
            f"Seconds between [PROGRESS] lines (default {DEFAULT_HEARTBEAT}; 0 "
            "disables). Makes 'slow' visibly different from 'hung' without "
            "opening Task Manager."
        ),
    )
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
        outcome = run_import(godot_path, heartbeat=args.heartbeat)
        if outcome == NO_RESULT:
            print("\n[NO RESULT] Import pass did not complete; nothing was measured.")
            sys.exit(EXIT_NO_RESULT)
        if outcome != PASSED:
            print("\n[ERROR] Import pass failed; aborting (GUT would run zero tests).")
            sys.exit(EXIT_FAILED)

    if not args.no_syntax_check:
        outcome = check_syntax(godot_path, heartbeat=args.heartbeat)
        if outcome == NO_RESULT:
            print("\n[NO RESULT] Syntax check did not complete; nothing was measured.")
            sys.exit(EXIT_NO_RESULT)
        if outcome != PASSED:
            print("\n[ERROR] Syntax check failed! Fix errors before running tests.")
            sys.exit(EXIT_FAILED)

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

    summary_rows = []
    for mode in modes:
        timeout, provenance = resolve_timeout(mode, args.timeout)
        print(
            f"\n[TIMEOUT] '{mode}': wall-clock cap "
            + (f"{timeout}s" if timeout else "DISABLED")
            + f" (from {provenance}); stall detector "
            + (f"{args.stall_timeout}s" if args.stall_timeout else "DISABLED")
            + f"; heartbeat every {args.heartbeat}s."
        )
        summary_rows.append(
            run_gut_tests(
                godot_path,
                mode,
                MODE_DIRS[mode],
                log_level,
                args.min_tests,
                timeout,
                args.stall_timeout,
                args.heartbeat,
            )
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
            + " did not run to completion. This is NOT a test failure and NOT a "
            "pass -- no measurement exists. Do not report a suite result from this run."
        )
        for r in incomplete:
            print(f"           {r['mode']}: {r['detail']}")
    elif any(r["outcome"] == FAILED for r in summary_rows):
        print("[FAILURE] Gate failed (see above).")
    else:
        print("[SUCCESS] All requested suites passed the gate! CHECKED")
    print("=" * 60)
    sys.exit(decide_exit(summary_rows))


if __name__ == "__main__":
    main()
