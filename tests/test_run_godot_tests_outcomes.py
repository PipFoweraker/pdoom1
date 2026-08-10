# !/usr/bin/env python3
"""Unit tests for the three-outcome reporting in scripts/run_godot_tests.py (#1181).

What these lock down, and why each one exists:

- **A timeout must not be renderable as a test result.** Cutting v0.14.1 the
  simulation tier timed out and the runner printed
  `simulation: 0 tests, 0 fail (FAIL)` -- two numbers and a verdict, none of
  which came from a test executing. A human had to read a process list to work
  out that it was not a real failure. `test_timeout_totals_line_*` asserts the
  exact old string can no longer be produced from a timed-out run.
- **The kill paths are exercised for real, not mocked.** A guard that has never
  been shown to fire is not evidence (#640), so
  `test_real_subprocess_wall_clock_timeout` and `test_real_subprocess_stall`
  launch actual sleeping processes and prove the runner kills them and labels
  the two cases differently.
- **Counts that were never measured render as `-`, never `0`.** `_count(None)`
  and the markdown table are asserted directly; `0` would be a measurement.
- **Incompleteness outranks failure in the exit code.** If any suite did not
  finish, we do not know the state of the run, so exit 2 beats exit 1.
"""

import io
import sys
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import run_godot_tests as rgt  # noqa: E402


def _row(mode, outcome, tests=None, failures=None, failing_tests=None, detail="", elapsed=0.0):
    return rgt._result(mode, outcome, tests, failures, failing_tests, detail, elapsed)


class TestOutcomeRendering(unittest.TestCase):
    """The reporting layer. This is where #1181 actually bit."""

    def test_count_of_unmeasured_is_a_dash_not_zero(self):
        self.assertEqual(rgt._count(None), "-")
        self.assertEqual(rgt._count(0), "0")

    def test_timeout_totals_line_has_no_counts_and_no_fail_verdict(self):
        rows = [_row("simulation", rgt.NO_RESULT, detail="timed out after 900s", elapsed=901)]
        line = rgt.format_totals_line(rows)
        # The exact string the old runner emitted, which is what made a timeout
        # indistinguishable from a failing suite:
        self.assertNotIn("0 tests, 0 fail", line)
        self.assertNotIn("(FAIL)", line)
        self.assertIn("DID NOT COMPLETE", line)
        self.assertIn("NO RESULT", line)

    def test_totals_line_still_reports_measured_pass_and_fail(self):
        rows = [
            _row("quick", rgt.PASSED, 412, 0),
            _row("integration", rgt.FAILED, 30, 2),
        ]
        line = rgt.format_totals_line(rows)
        self.assertIn("quick: 412 tests, 0 fail (ok)", line)
        self.assertIn("integration: 30 tests, 2 fail (FAIL)", line)

    def test_three_outcomes_are_three_distinct_renderings(self):
        rows = [
            _row("quick", rgt.PASSED, 412, 0),
            _row("integration", rgt.FAILED, 30, 2),
            _row("simulation", rgt.NO_RESULT, detail="timed out after 900s", elapsed=901),
        ]
        md = rgt.format_summary_markdown(rows)
        self.assertIn("| quick | 412 | 0 | PASS |", md)
        self.assertIn("| integration | 30 | 2 | FAIL |", md)
        self.assertIn("| simulation (non-blocking) | - | - | NO RESULT (not measured) |", md)
        # And the no-result tier gets its own banner, distinct from TIER RED.
        self.assertIn("NO RESULT (not run to completion)", md)
        self.assertNotIn("SIMULATION TIER RED", md)

    def test_failing_sim_tier_still_gets_the_red_banner(self):
        """#964's banner must survive the #1181 refactor."""
        rows = [
            _row(
                "simulation",
                rgt.FAILED,
                80,
                1,
                failing_tests=[{"suite": "test_x.gd", "test": "test_y", "message": "boom"}],
            )
        ]
        md = rgt.format_summary_markdown(rows)
        self.assertIn("[!] SIMULATION TIER RED", md)
        self.assertIn("| test_x.gd | test_y | boom |", md)


class TestExitCodes(unittest.TestCase):
    def test_distinct_codes(self):
        self.assertEqual(rgt.decide_exit([_row("quick", rgt.PASSED, 1, 0)]), 0)
        self.assertEqual(rgt.decide_exit([_row("quick", rgt.FAILED, 1, 1)]), 1)
        self.assertEqual(rgt.decide_exit([_row("quick", rgt.NO_RESULT)]), 2)

    def test_incompleteness_outranks_failure(self):
        rows = [_row("quick", rgt.FAILED, 1, 1), _row("simulation", rgt.NO_RESULT)]
        self.assertEqual(rgt.decide_exit(rows), 2)


class TestTimeoutResolution(unittest.TestCase):
    def setUp(self):
        self._saved = {k: __import__("os").environ.get(k) for k in ("CI", "PDOOM1_TEST_TIMEOUT")}
        for k in self._saved:
            __import__("os").environ.pop(k, None)

    def tearDown(self):
        import os

        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_cli_flag_wins(self):
        self.assertEqual(rgt.resolve_timeout("simulation", 12345)[0], 12345)

    def test_env_var_beats_default(self):
        import os

        os.environ["PDOOM1_TEST_TIMEOUT"] = "77"
        secs, why = rgt.resolve_timeout("simulation", None)
        self.assertEqual(secs, 77)
        self.assertIn("PDOOM1_TEST_TIMEOUT", why)

    def test_ci_default_is_unchanged_at_900(self):
        """CI's contract must not move: it completes the sim tier in 460-550s."""
        import os

        os.environ["CI"] = "true"
        self.assertEqual(rgt.resolve_timeout("simulation", None)[0], 900)
        self.assertEqual(rgt.resolve_timeout("quick", None)[0], 900)

    def test_local_sim_default_is_generous(self):
        secs, why = rgt.resolve_timeout("simulation", None)
        self.assertGreater(
            secs, 1630, "must clear the worst local sim run seen in #1181 (27m10s, still going)"
        )
        self.assertIn("local", why)
        # Only the slow tier gets the generous cap.
        self.assertEqual(rgt.resolve_timeout("quick", None)[0], 900)


class TestStreamProcessRealKills(unittest.TestCase):
    """Real subprocesses. Mocking the kill would prove only that the mock works."""

    def test_real_subprocess_wall_clock_timeout(self):
        cmd = [sys.executable, "-c", "import time; time.sleep(120)"]
        start = time.monotonic()
        buf = io.StringIO()
        with redirect_stdout(buf):
            status, rc, elapsed, _out = rgt._stream_process(
                cmd, cwd=None, env=None, timeout=3, stall_timeout=0, heartbeat=1, label="fake"
            )
        self.assertEqual(status, "timeout")
        self.assertIsNone(rc)
        self.assertLess(time.monotonic() - start, 60, "the process was not actually killed")
        self.assertGreaterEqual(elapsed, 3)

    def test_real_subprocess_stall_is_labelled_differently_from_timeout(self):
        """A silent process is HUNG; a chatty slow one is not. Same kill, different word."""
        cmd = [sys.executable, "-c", "import time; time.sleep(120)"]
        buf = io.StringIO()
        with redirect_stdout(buf):
            status, _rc, _elapsed, _out = rgt._stream_process(
                cmd, cwd=None, env=None, timeout=0, stall_timeout=3, heartbeat=1, label="fake"
            )
        self.assertEqual(status, "stall")

    def test_chatty_process_is_not_killed_by_the_stall_detector(self):
        """The distinction that cost the most time on 2026-08-08: slow != hung."""
        cmd = [
            sys.executable,
            "-u",
            "-c",
            "import time\nfor i in range(10):\n    print('tick', i, flush=True)\n    time.sleep(0.5)\n",
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            status, rc, _elapsed, out = rgt._stream_process(
                cmd, cwd=None, env=None, timeout=60, stall_timeout=2, heartbeat=1, label="chatty"
            )
        self.assertEqual(status, "completed")
        self.assertEqual(rc, 0)
        self.assertIn("tick 9", out)

    def test_progress_heartbeat_is_emitted_during_a_slow_run(self):
        """Without this a human cannot tell slow from hung without Task Manager."""
        cmd = [sys.executable, "-u", "-c", "import time; time.sleep(4)"]
        buf = io.StringIO()
        with redirect_stdout(buf):
            rgt._stream_process(
                cmd, cwd=None, env=None, timeout=20, stall_timeout=0, heartbeat=1, label="slowly"
            )
        printed = buf.getvalue()
        self.assertIn("[PROGRESS] slowly:", printed)
        self.assertIn("elapsed", printed)

    def test_unlaunchable_command_is_no_result_not_failure(self):
        status, _rc, _elapsed, out = rgt._stream_process(
            ["definitely-not-a-real-binary-1181"],
            cwd=None,
            env=None,
            timeout=5,
            stall_timeout=0,
            heartbeat=0,
            label="nope",
        )
        self.assertEqual(status, "error")
        self.assertIn("failed to launch", out)


class TestRunGutTestsTimeoutPath(unittest.TestCase):
    """End of the chain: a timed-out suite must come back with NO counts."""

    def setUp(self):
        self._real = rgt._stream_process

    def tearDown(self):
        rgt._stream_process = self._real

    def _fake(self, status, elapsed=901.0):
        def _f(*_a, **_k):
            return (status, None, elapsed, "")

        return _f

    def test_timeout_returns_no_result_with_no_counts(self):
        rgt._stream_process = self._fake("timeout")
        buf = io.StringIO()
        with redirect_stdout(buf):
            r = rgt.run_gut_tests(
                "godot", "simulation", rgt.MODE_DIRS["simulation"], 2, 80, 900, 300, 30
            )
        self.assertEqual(r["outcome"], rgt.NO_RESULT)
        self.assertIsNone(r["tests"], "an unmeasured count must be None, never 0")
        self.assertIsNone(r["failures"])
        self.assertIn("--timeout", r["detail"], "the report must say how to get a measurement")
        self.assertIn("NO RESULT", buf.getvalue())
        self.assertNotIn("[FAIL]", buf.getvalue())

    def test_stall_returns_no_result_and_says_hung(self):
        rgt._stream_process = self._fake("stall")
        with redirect_stdout(io.StringIO()):
            r = rgt.run_gut_tests(
                "godot", "simulation", rgt.MODE_DIRS["simulation"], 2, 80, 0, 300, 30
            )
        self.assertEqual(r["outcome"], rgt.NO_RESULT)
        self.assertIn("hung", r["detail"])

    def test_missing_test_dir_is_still_a_measured_failure(self):
        """Regression guard: NOT everything becomes NO_RESULT. A directory that
        does not exist is a fact we observed (#629), so it stays FAILED."""
        with redirect_stdout(io.StringIO()):
            r = rgt.run_gut_tests(
                "godot", "smoke", "res://tests/does_not_exist", 2, 1, 900, 300, 30
            )
        self.assertEqual(r["outcome"], rgt.FAILED)


if __name__ == "__main__":
    unittest.main()
