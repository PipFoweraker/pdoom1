#!/usr/bin/env python3
"""Unit tests for tools/check_release_branch.py -- the release-branch guard (#1269).

House standard: a guard must be shown capable of returning BOTH answers. These
tests run the guard against a real (throwaway) git repository, so every verdict
comes from real `git merge-base` / `git show` output, and they cover green, red,
and the third answer -- COULD NOT MEASURE (exit 2) -- which must never be folded
into either of the other two.

Run: python3 -m unittest tests.test_check_release_branch -v
"""

import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import check_release_branch as crb  # noqa: E402


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


class FixtureTest(unittest.TestCase):
    """Shares the self-test's fixture: see crb.build_fixture for the shape."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.sha = crb.build_fixture(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def codes(self, tag: str, commit: str, require_tag: bool = True) -> list:
        return crb.codes(crb.check(self.root, tag, commit, require_tag=require_tag))

    def cli(self, *argv: str) -> int:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = crb.main(["--repo", str(self.root), *argv])
        self.output = buf.getvalue()
        return code


class ParseTagTest(unittest.TestCase):
    def test_release_tags_map_to_their_branch(self):
        self.assertEqual(crb.parse_tag("v0.14.5"), ("release/v0.14", "0.14.5"))
        self.assertEqual(crb.parse_tag("v1.0.0"), ("release/v1.0", "1.0.0"))
        self.assertEqual(crb.parse_tag("v0.15.0-rc1"), ("release/v0.15", "0.15.0-rc1"))

    def test_non_release_names_are_rejected(self):
        for bad in ["0.14.5", "v0.14", "v0.14.5.1", "release/v0.14", "v0.014.5", "v0.14.5-", ""]:
            self.assertIsNone(crb.parse_tag(bad), bad)


class GreenTest(FixtureTest):
    def test_tag_on_release_branch_with_matching_version_passes(self):
        self.assertEqual(self.codes("v0.14.5", self.sha["C"]), [])

    def test_epoch_baseline_reachable_from_branch_passes(self):
        # release/v0.14 is cut FROM the v0.14.4 commit, so v0.14.4 is on it.
        self.assertEqual(self.codes("v0.14.4", self.sha["A"]), [])

    def test_dry_run_before_tag_exists_passes(self):
        self.assertEqual(self.codes("v0.14.7", self.sha["D"], require_tag=False), [])

    def test_cli_exit_0(self):
        self.assertEqual(
            self.cli("--tag", "v0.14.5", "--commit", self.sha["C"], "--require-tag"), 0
        )
        self.assertIn("OK v0.14.5 is on release/v0.14", self.output)


class RedTest(FixtureTest):
    def test_rb001_bad_tag_name(self):
        self.assertEqual(self.codes("0.14.5", self.sha["C"]), ["RB001"])

    def test_rb002_version_txt_mismatch(self):
        self.assertEqual(self.codes("v0.14.6", self.sha["C"]), ["RB002"])

    def test_rb003_branch_missing_on_remote(self):
        self.assertEqual(self.codes("v0.15.0", self.sha["B"]), ["RB003"])

    def test_rb003_local_branch_does_not_count(self):
        # A release branch that exists only on Pip's laptop is not a release branch.
        git(self.root, "branch", "release/v0.15", self.sha["B"])
        self.assertEqual(self.codes("v0.15.0", self.sha["B"]), ["RB003"])

    def test_rb003_custom_prefix_finds_local_branch(self):
        git(self.root, "branch", "release/v0.15", self.sha["B"])
        findings = crb.check(
            self.root, "v0.15.0", self.sha["B"], remote_prefix="refs/heads/", require_tag=True
        )
        self.assertEqual(findings, [])

    def test_rb004_main_commit_not_on_release_branch(self):
        # Tag v0.14.9 at a main-only commit whose version.txt says 0.14.9: the
        # only thing wrong is WHERE it was cut. This is the v0.14.1-v0.14.4 shape.
        git(self.root, "checkout", "-q", "main")
        (self.root / "version.txt").write_text("0.14.9\n", encoding="utf-8")
        git(self.root, "commit", "-qam", "tagged from main")
        sha = git(self.root, "rev-parse", "HEAD")
        git(self.root, "tag", "v0.14.9", sha)
        self.assertEqual(self.codes("v0.14.9", sha), ["RB004"])

    def test_rb005_tag_points_elsewhere(self):
        # Dispatch from main labelled as an existing tag.
        self.assertIn("RB005", self.codes("v0.14.5", self.sha["B"]))

    def test_rb005_publish_requires_existing_tag(self):
        self.assertEqual(self.codes("v0.14.7", self.sha["D"], require_tag=True), ["RB005"])

    def test_cli_exit_1_and_annotation(self):
        self.assertEqual(self.cli("--tag", "v0.14.6", "--commit", self.sha["C"], "--github"), 1)
        self.assertIn("::error title=Release-branch guard::RB002", self.output)
        self.assertIn("The release is refused", self.output)


class CouldNotMeasureTest(FixtureTest):
    def test_shallow_clone_is_exit_2_not_a_finding(self):
        shallow = self.root / "shallow"
        git(
            self.root,
            "clone",
            "-q",
            "--depth",
            "1",
            "--no-local",
            "file://" + str(self.root),
            str(shallow),
        )
        with self.assertRaises(crb.Unmeasurable):
            crb.check(shallow, "v0.14.5", "HEAD")
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = crb.main(["--repo", str(shallow), "--tag", "v0.14.5"])
        self.assertEqual(code, 2)
        self.assertIn("COULD NOT MEASURE", buf.getvalue())
        self.assertNotIn("FAIL", buf.getvalue())

    def test_unresolvable_commit_is_exit_2(self):
        self.assertEqual(self.cli("--tag", "v0.14.5", "--commit", "deadbeef" * 5), 2)

    def test_not_a_repo_is_exit_2(self):
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = crb.main(["--repo", td, "--tag", "v0.14.5"])
            self.assertEqual(code, 2)


class SelfTestTest(unittest.TestCase):
    def test_self_test_passes_and_exercises_both_answers(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = crb.self_test()
        self.assertEqual(code, 0, buf.getvalue())
        greens = [c for c in crb.SELF_TEST_CASES if not c[4]]
        reds = [c for c in crb.SELF_TEST_CASES if c[4]]
        self.assertTrue(greens and reds)


class WorkflowWiringTest(unittest.TestCase):
    """The guard is only a gate if the release workflow runs it BEFORE building."""

    WORKFLOW = REPO_ROOT / ".github" / "workflows" / "enhanced-release.yml"

    def setUp(self) -> None:
        import yaml  # requirements.txt; only this class needs it

        self.wf = yaml.safe_load(self.WORKFLOW.read_text(encoding="utf-8"))
        self.jobs = self.wf["jobs"]

    def _needs(self, job: str) -> list:
        n = self.jobs[job].get("needs", [])
        return [n] if isinstance(n, str) else list(n)

    def test_preflight_runs_the_guard(self):
        steps = " ".join(s.get("run", "") for s in self.jobs["preflight"]["steps"])
        self.assertIn("tools/check_release_branch.py --self-test", steps)
        self.assertIn("tools/check_release_branch.py", steps)
        self.assertIn('grep -q "^## \\[$TAG_VERSION\\]" CHANGELOG.md', steps)
        self.assertIn("check_release_notes.py --changelog-structure", steps)

    def test_preflight_has_full_history(self):
        checkout = self.jobs["preflight"]["steps"][0]
        self.assertEqual(checkout["with"]["fetch-depth"], 0)

    def test_build_and_publish_need_preflight(self):
        for job in ["validate-data", "build-godot", "create-github-release"]:
            self.assertIn("preflight", self._needs(job), job)

    def test_preflight_cannot_be_skipped_by_skip_validation(self):
        pre = self.jobs["preflight"]
        self.assertNotIn("skip_validation", str(pre.get("if", "")))
        for step in pre["steps"]:
            self.assertNotIn("continue-on-error", step, step.get("name"))


if __name__ == "__main__":
    unittest.main()
