#!/usr/bin/env python3
"""Unit tests for the run_godot_tests.py wall-clock cap and its reporting (#1181).

The defect these lock down: the cap was hardcoded (`timeout=900`) with no flag,
and when it tripped the runner returned `(False, 0, 0, [])`, which the reporting
layer rendered as

    [TOTALS] simulation: 0 tests, 0 fail (FAIL)
    | simulation (non-blocking) | 0 | 0 | FAIL |

Those zeros were fabricated -- no JUnit file was ever written, so nothing ran,
nothing passed and nothing failed. Presenting an unmeasured run in the same
shape as a measured one is the #640 defect (a number that did not come from
tests executing) reappearing in the runner's own output.

So the assertions here are mostly NEGATIVE: the timeout path must not emit a
count, must not emit the word FAIL as its verdict, and must exit 2.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import run_godot_tests as R  # noqa: E402  (deliberate late import; sys.path just set)


class ResolveTimeoutTests(unittest.TestCase):
    def test_default_is_still_900(self):
        """Guard the CI contract: #1181 asked for a flag, NOT a new default.

        If this ever needs to change, it changes CI's behaviour for everyone and
        must be a deliberate, separately-reviewed decision.
        """
        self.assertEqual(R.DEFAULT_TIMEOUT, 900)
        with mock.patch.dict("os.environ", {}, clear=False):
            R.os.environ.pop(R.TIMEOUT_ENV_VAR, None)
            seconds, source = R.resolve_timeout(None)
        self.assertEqual(seconds, 900)
        self.assertEqual(source, "default")

    def test_cli_flag_wins(self):
        with mock.patch.dict("os.environ", {R.TIMEOUT_ENV_VAR: "111"}):
            seconds, source = R.resolve_timeout(3600)
        self.assertEqual(seconds, 3600)
        self.assertEqual(source, "--timeout")

    def test_env_var_used_when_no_flag(self):
        with mock.patch.dict("os.environ", {R.TIMEOUT_ENV_VAR: "2700"}):
            seconds, source = R.resolve_timeout(None)
        self.assertEqual(seconds, 2700)
        self.assertIn(R.TIMEOUT_ENV_VAR, source)

    def test_garbage_env_var_falls_back_to_default(self):
        with mock.patch.dict("os.environ", {R.TIMEOUT_ENV_VAR: "soon"}):
            seconds, _source = R.resolve_timeout(None)
        self.assertEqual(seconds, 900)

    def test_zero_disables_the_cap(self):
        seconds, source = R.resolve_timeout(0)
        self.assertIsNone(seconds)
        self.assertIn("DISABLED", source)


class TimeoutOutcomeTests(unittest.TestCase):
    """Drive the real timeout branch of run_gut_tests()."""

    def _run_with_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "godot"
            test_dir = project / "tests" / "unit"
            test_dir.mkdir(parents=True)
            (test_dir / "test_example.gd").write_text("extends GutTest\n", encoding="ascii")

            def boom(cmd, *args, **kwargs):
                raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout", 5))

            with (
                mock.patch.object(R, "GODOT_PROJECT", project),
                mock.patch.object(R.subprocess, "run", boom),
            ):
                return R.run_gut_tests(
                    "godot-never-launched",
                    "simulation",
                    "res://tests/unit",
                    2,
                    80,
                    timeout=5,
                )

    def test_timeout_is_no_result_not_failure(self):
        row = self._run_with_timeout()
        self.assertEqual(row["outcome"], R.NO_RESULT)
        self.assertNotEqual(row["outcome"], R.FAILED)
        self.assertNotEqual(row["outcome"], R.PASSED)

    def test_timeout_reports_no_counts_at_all(self):
        """The load-bearing assertion: no fabricated zeros."""
        row = self._run_with_timeout()
        self.assertIsNone(row["tests"])
        self.assertIsNone(row["failures"])

    def test_totals_line_never_says_zero_tests(self):
        row = self._run_with_timeout()
        line = R.format_totals_line([row])
        self.assertIn("NO RESULT", line)
        self.assertNotIn("0 tests", line)
        self.assertNotIn("0 fail", line)

    def test_markdown_row_shows_dashes_not_zeros(self):
        row = self._run_with_timeout()
        md = R.format_summary_markdown([row])
        self.assertIn("DID NOT COMPLETE", md)
        self.assertIn("| - | - |", md)
        self.assertNotIn("| 0 | 0 |", md)

    def test_exit_code_is_two(self):
        row = self._run_with_timeout()
        self.assertEqual(R.decide_exit([row]), R.EXIT_NO_RESULT)
        self.assertNotEqual(R.EXIT_NO_RESULT, R.EXIT_OK)


class DecideExitTests(unittest.TestCase):
    @staticmethod
    def _row(outcome):
        return {
            "mode": "quick",
            "outcome": outcome,
            "tests": 0 if outcome == R.NO_RESULT else 10,
            "failures": 0,
            "failing_tests": [],
            "detail": "",
        }

    def test_all_pass_is_zero(self):
        self.assertEqual(R.decide_exit([self._row(R.PASSED)]), 0)

    def test_measured_failure_is_one(self):
        self.assertEqual(R.decide_exit([self._row(R.PASSED), self._row(R.FAILED)]), 1)

    def test_no_result_outranks_failure(self):
        rows = [self._row(R.FAILED), self._row(R.NO_RESULT)]
        self.assertEqual(R.decide_exit(rows), 2)


if __name__ == "__main__":
    unittest.main()
