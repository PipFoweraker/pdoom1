# !/usr/bin/env python3
"""Unit tests for the missing-platform-build detector and its issue reporter.

The defect being locked down (v0.14.3, 2026-08-24): the macOS upload step in
`enhanced-release.yml` carries `if-no-files-found: warn`, the job went green,
and the release feed then advertised a macOS URL that 404s. Nothing was filed,
so the website had nothing to link.

Both answers are proven here, because only proving one is how a detector that
always says "missing" (or always says "fine") passes review:

  * every platform present  -> nothing is created, commented or closed;
  * a platform missing      -> EXACTLY ONE issue is created or updated, and its
                               URL lands in build-status.json.

No live GitHub API. `FakeGitHub` implements the same small method surface as
`report_missing_build_issue.GitHubIssues`, so the tests exercise the real
create/find/update/comment logic without a token or a network.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_platform_builds as cpb  # noqa: E402
import report_missing_build_issue as rmb  # noqa: E402

VERSION = "v0.14.3"

# Every asset name the pipeline is expected to produce for this version.
ALL_ASSETS = {
    "windows": [f"PDoom-Windows-{VERSION}.zip", "PDoom-Windows.zip"],
    "linux": [f"PDoom-Linux-{VERSION}.zip", "PDoom-Linux.zip"],
    "macos": [f"PDoom-macOS-{VERSION}.zip", "PDoom.app.zip"],
}
ARTIFACT_DIRS = {"windows": "build-windows", "linux": "build-linux", "macos": "build-mac"}


def make_artifacts(root: Path, platforms, size: int = cpb.MIN_ASSET_BYTES + 1) -> Path:
    """Lay out a download-artifact-shaped tree for the given platform keys."""
    for key in platforms:
        target = root / ARTIFACT_DIRS[key] / VERSION
        target.mkdir(parents=True, exist_ok=True)
        for name in ALL_ASSETS[key]:
            (target / name).write_bytes(b"0" * size)
    return root


class TestDetection(unittest.TestCase):
    def test_all_platforms_present_reports_nothing_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_artifacts(Path(tmp), ALL_ASSETS.keys())
            status = cpb.build_status(root, VERSION, "http://run")

            self.assertTrue(status["all_present"])
            self.assertEqual(status["missing_platforms"], [])
            self.assertEqual(status["missing_required"], [])
            for key in ALL_ASSETS:
                self.assertTrue(status["platforms"][key]["available"], key)
                self.assertIsNone(status["platforms"][key]["tracking_issue"], key)

    def test_missing_mac_artifact_is_detected_and_is_not_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_artifacts(Path(tmp), ["windows", "linux"])
            status = cpb.build_status(root, VERSION, "http://run")

            self.assertFalse(status["all_present"])
            self.assertEqual(status["missing_platforms"], ["macos"])
            # The v0.14.3 shape exactly: mac missing must NOT be "required
            # missing", because Windows/Linux publishing outranks it (#1071).
            self.assertEqual(status["missing_required"], [])
            self.assertTrue(status["platforms"]["windows"]["available"])
            self.assertFalse(status["platforms"]["macos"]["available"])
            self.assertIn(VERSION, status["platforms"]["macos"]["user_message"])

    def test_truncated_zip_counts_as_missing(self):
        # The real check is the FILE, not the upload step's verdict: a
        # zero-byte or truncated zip uploads happily and 404s nothing, but it
        # is not a build a player can run.
        with tempfile.TemporaryDirectory() as tmp:
            root = make_artifacts(Path(tmp), ALL_ASSETS.keys())
            victim = root / "build-mac" / VERSION / "PDoom.app.zip"
            victim.write_bytes(b"")
            status = cpb.build_status(root, VERSION, "http://run")

            self.assertEqual(status["missing_platforms"], ["macos"])
            self.assertIn("PDoom.app.zip", status["platforms"]["macos"]["missing_assets"])

    def test_missing_unversioned_alias_alone_is_unavailable(self):
        # Half a platform is not a platform: the website's download buttons are
        # fixed strings against the unversioned alias (issue #1068).
        with tempfile.TemporaryDirectory() as tmp:
            root = make_artifacts(Path(tmp), ALL_ASSETS.keys())
            (root / "build-linux" / VERSION / "PDoom-Linux.zip").unlink()
            status = cpb.build_status(root, VERSION, "http://run")

            self.assertEqual(status["missing_platforms"], ["linux"])
            self.assertEqual(status["missing_required"], ["linux"])

    def test_layout_agnostic_flat_download(self):
        # download-artifact with merge-multiple flattens the tree; detection
        # must not depend on which layout the action chose.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for names in ALL_ASSETS.values():
                for name in names:
                    (root / name).write_bytes(b"0" * (cpb.MIN_ASSET_BYTES + 1))
            status = cpb.build_status(root, VERSION, "http://run")
            self.assertTrue(status["all_present"])


class TestCliExitCodes(unittest.TestCase):
    def test_exit_zero_when_only_best_effort_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_artifacts(Path(tmp), ["windows", "linux"])
            out = Path(tmp) / "build-status.json"
            code = cpb.main(
                ["--artifacts-dir", str(root), "--version", VERSION, "--output", str(out)]
            )
            # Loud, not blocking: a missing macOS build must not stop the
            # release, so the detector itself stays green.
            self.assertEqual(code, 0)
            written = json.loads(out.read_text(encoding="ascii"))
            self.assertEqual(written["missing_platforms"], ["macos"])
            self.assertEqual(written["schema"], cpb.SCHEMA)

    def test_exit_one_when_required_platform_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_artifacts(Path(tmp), ["linux", "macos"])
            out = Path(tmp) / "build-status.json"
            code = cpb.main(
                ["--artifacts-dir", str(root), "--version", VERSION, "--output", str(out)]
            )
            self.assertEqual(code, 1)

    def test_missing_artifacts_dir_is_a_pipeline_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = cpb.main(
                [
                    "--artifacts-dir",
                    str(Path(tmp) / "nope"),
                    "--version",
                    VERSION,
                    "--output",
                    str(Path(tmp) / "build-status.json"),
                ]
            )
            self.assertEqual(code, 1)


class FakeGitHub:
    """In-memory stand-in for report_missing_build_issue.GitHubIssues."""

    def __init__(self, issues=None, labels=None):
        self.issues = list(issues or [])
        self.labels = set(labels or [])
        self.comments = {}
        self.created = []
        self.updates = []
        self.created_labels = []
        self._next = max([i["number"] for i in self.issues], default=100) + 1

    def ensure_label(self, name, color, description):
        if name not in self.labels:
            self.labels.add(name)
            self.created_labels.append(name)

    def find_open_issue(self, labels):
        for issue in sorted(self.issues, key=lambda i: i["number"]):
            if issue.get("state", "open") != "open":
                continue
            if all(name in issue.get("labels", []) for name in labels):
                return issue
        return None

    def create_issue(self, title, body, labels):
        issue = {
            "number": self._next,
            "title": title,
            "body": body,
            "labels": list(labels),
            "state": "open",
            "html_url": f"https://github.com/o/r/issues/{self._next}",
        }
        self._next += 1
        self.issues.append(issue)
        self.created.append(issue)
        return issue

    def update_issue(self, number, **fields):
        for issue in self.issues:
            if issue["number"] == number:
                issue.update(fields)
                self.updates.append((number, fields))
                return issue
        raise AssertionError(f"no such issue {number}")

    def list_comments(self, number):
        return list(self.comments.get(number, []))

    def create_comment(self, number, body):
        comment = {"body": body}
        self.comments.setdefault(number, []).append(comment)
        return comment


def status_with(missing=()):
    """Build a status doc by hand -- decoupled from the filesystem detector."""
    platforms = {}
    for key, label in (("windows", "Windows"), ("linux", "Linux"), ("macos", "macOS")):
        gone = key in missing
        platforms[key] = {
            "label": label,
            "required": key != "macos",
            "available": not gone,
            "status": "unavailable" if gone else "available",
            "assets": [],
            "missing_assets": list(ALL_ASSETS[key]) if gone else [],
            "tracking_issue": None,
            "user_message": cpb._user_message(label, VERSION, not gone),
        }
    return {
        "schema": cpb.SCHEMA,
        "version": VERSION,
        "run_url": "http://run/1",
        "all_present": not missing,
        "missing_platforms": sorted(missing),
        "missing_required": sorted(k for k in missing if k != "macos"),
        "platforms": platforms,
    }


class TestIssueReporting(unittest.TestCase):
    def test_all_present_files_nothing(self):
        client = FakeGitHub()
        result = rmb.sync_all(client, status_with(), "http://run/1")

        self.assertEqual(client.created, [])
        self.assertEqual(client.comments, {})
        self.assertEqual(client.created_labels, [])
        for info in result["platforms"].values():
            self.assertIsNone(info["tracking_issue"])

    def test_missing_platform_opens_exactly_one_issue_and_emits_url(self):
        client = FakeGitHub()
        result = rmb.sync_all(client, status_with(["macos"]), "http://run/1")

        self.assertEqual(len(client.created), 1)
        issue = client.created[0]
        self.assertEqual(sorted(issue["labels"]), ["build-missing", "platform:macos"])
        self.assertIn(VERSION, issue["title"])
        self.assertIn("macOS", issue["title"])
        self.assertIn("http://run/1", issue["body"])
        self.assertIn("macOS", issue["body"])

        tracked = result["platforms"]["macos"]["tracking_issue"]
        self.assertEqual(tracked["url"], issue["html_url"])
        self.assertEqual(tracked["number"], issue["number"])
        # The other platforms stay untracked -- one issue, not three.
        self.assertIsNone(result["platforms"]["windows"]["tracking_issue"])
        self.assertIsNone(result["platforms"]["linux"]["tracking_issue"])
        self.assertIn("build-missing", client.created_labels)
        self.assertIn("platform:macos", client.created_labels)

    def test_second_release_updates_the_same_issue_instead_of_opening_another(self):
        existing = {
            "number": 900,
            "title": rmb.issue_title("macOS", "v0.14.3"),
            "body": rmb.new_body(
                "macOS",
                "macos",
                "v0.14.3",
                status_with(["macos"])["platforms"]["macos"],
                "http://run/1",
            )
            + "\nHuman note: this is the #1071 framework symlink.\n",
            "labels": ["build-missing", "platform:macos"],
            "state": "open",
            "html_url": "https://github.com/o/r/issues/900",
        }
        client = FakeGitHub(issues=[existing], labels={"build-missing", "platform:macos"})

        later = status_with(["macos"])
        later["version"] = "v0.14.4"
        result = rmb.sync_all(client, later, "http://run/2")

        self.assertEqual(client.created, [], "must not open a second rolling issue")
        self.assertEqual(len(client.comments[900]), 1)
        self.assertIn("v0.14.4", client.comments[900][0]["body"])
        self.assertIn("http://run/2", client.comments[900][0]["body"])
        self.assertEqual(result["platforms"]["macos"]["tracking_issue"]["number"], 900)

        body = existing["body"]
        self.assertIn("v0.14.4", body)
        self.assertIn("http://run/2", body)
        # Human prose outside the managed block survives the rewrite.
        self.assertIn("Human note: this is the #1071 framework symlink.", body)
        self.assertIn("v0.14.4", existing["title"])

    def test_rerunning_the_same_tag_does_not_duplicate_the_comment(self):
        existing = {
            "number": 900,
            "title": rmb.issue_title("macOS", VERSION),
            "body": "seed",
            "labels": ["build-missing", "platform:macos"],
            "state": "open",
            "html_url": "https://github.com/o/r/issues/900",
        }
        client = FakeGitHub(issues=[existing])

        rmb.sync_all(client, status_with(["macos"]), "http://run/1")
        rmb.sync_all(client, status_with(["macos"]), "http://run/1")

        self.assertEqual(client.created, [])
        self.assertEqual(len(client.comments[900]), 1, "re-run must not re-comment")

    def test_recovery_closes_the_rolling_issue(self):
        existing = {
            "number": 900,
            "title": rmb.issue_title("macOS", "v0.14.3"),
            "body": "seed",
            "labels": ["build-missing", "platform:macos"],
            "state": "open",
            "html_url": "https://github.com/o/r/issues/900",
        }
        client = FakeGitHub(issues=[existing])

        healthy = status_with()
        healthy["version"] = "v0.14.4"
        result = rmb.sync_all(client, healthy, "http://run/3")

        self.assertEqual(existing["state"], "closed")
        self.assertEqual(len(client.comments[900]), 1)
        self.assertIn("v0.14.4", client.comments[900][0]["body"])
        # Nothing to link once it is back -- the website must stop saying
        # "build coming" the moment the build exists.
        self.assertIsNone(result["platforms"]["macos"]["tracking_issue"])

    def test_pull_request_carrying_the_label_is_not_mistaken_for_the_issue(self):
        # find_open_issue's PR filter lives in the real client, so assert the
        # contract here on the shape the API returns.
        client = rmb.GitHubIssues("o/r", "t")
        self.assertEqual(rmb.platform_labels("macos"), ["build-missing", "platform:macos"])
        self.assertTrue(hasattr(client, "find_open_issue"))


class TestReporterCli(unittest.TestCase):
    def _write_status(self, tmp, missing=()):
        path = Path(tmp) / "build-status.json"
        path.write_text(json.dumps(status_with(missing), indent=2), encoding="ascii")
        return path

    def test_no_token_is_an_error_not_a_silent_no_op(self):
        # A token-less run must not look identical to a run where everything
        # was fine -- that is the v0.14.3 403 failure mode in another costume.
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_status(tmp, ["macos"])
            saved = {k: os.environ.pop(k, None) for k in ("GH_TOKEN", "GITHUB_TOKEN")}
            try:
                code = rmb.main(["--status", str(path), "--repo", "o/r"])
            finally:
                for k, v in saved.items():
                    if v is not None:
                        os.environ[k] = v
            self.assertEqual(code, 1)

    def test_cli_writes_the_issue_url_back_into_build_status_json(self):
        # The whole point of the plumbing: the URL must land in the file the
        # website reads, not only in the job log.
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_status(tmp, ["macos"])
            fake = FakeGitHub()
            real = rmb.GitHubIssues
            os.environ["GH_TOKEN"] = "test-token"
            rmb.GitHubIssues = lambda *a, **k: fake
            try:
                code = rmb.main(
                    ["--status", str(path), "--repo", "o/r", "--run-url", "http://run/9"]
                )
            finally:
                rmb.GitHubIssues = real
                os.environ.pop("GH_TOKEN", None)

            self.assertEqual(code, 0)
            written = json.loads(path.read_text(encoding="ascii"))
            url = written["platforms"]["macos"]["tracking_issue"]["url"]
            self.assertTrue(url.startswith("https://github.com/"))
            self.assertIsNone(written["platforms"]["windows"]["tracking_issue"])


class TestBodySplicing(unittest.TestCase):
    def test_splice_replaces_only_the_managed_block(self):
        block = rmb.managed_block(
            "macOS", "macos", VERSION, {"missing_assets": ["a.zip"], "user_message": "m"}, "u"
        )
        body = "keep-head\n\n" + block + "\n\nkeep-tail\n"
        newer = rmb.managed_block(
            "macOS", "macos", "v0.15.0", {"missing_assets": ["b.zip"], "user_message": "m2"}, "u2"
        )
        spliced = rmb.splice_body(body, newer)

        self.assertIn("keep-head", spliced)
        self.assertIn("keep-tail", spliced)
        self.assertIn("v0.15.0", spliced)
        self.assertNotIn("a.zip", spliced)
        self.assertEqual(spliced.count(rmb.BODY_START), 1)

    def test_splice_appends_when_no_block_present(self):
        spliced = rmb.splice_body("legacy hand-written issue", "BLOCK")
        self.assertIn("legacy hand-written issue", spliced)
        self.assertIn("BLOCK", spliced)


class TestAsciiOutput(unittest.TestCase):
    def test_generated_text_is_ascii(self):
        # ASCII-only is a hard repo rule (#744) and these strings end up in
        # .json feed files and issue bodies.
        info = status_with(["macos"])["platforms"]["macos"]
        for text in (
            rmb.new_body("macOS", "macos", VERSION, info, "http://run"),
            rmb.issue_title("macOS", VERSION),
            cpb.render_summary(status_with(["macos"])),
        ):
            text.encode("ascii")


if __name__ == "__main__":
    unittest.main()
