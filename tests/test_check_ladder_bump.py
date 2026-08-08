#!/usr/bin/env python3
"""Unit tests for tools/check_ladder_bump.py -- the board-key bump guard (issue #1178).

What these lock down:

- **The guard can actually fail.** Until 2026-08-09 this check ran in CI as
  ``python tools/check_ladder_bump.py --base ... || true`` AND with its own
  default of exit-0-on-warning, so it was disarmed twice over. These tests
  assert the exit codes directly, so a future re-disarming shows up as a red
  test rather than as a green CI job that checks nothing.
- Ack parsing: a ``ladder-ack:`` line with a substantive reason turns a strict
  failure green; a token-length reason does not.
- The gameplay-surface allowlist, including the ``.md`` exclusion added because
  the real #1137 run named ``godot/data/events/overrides/README.md`` as
  gameplay surface (prose in the .pck cannot move a score).
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import check_ladder_bump as clb  # noqa: E402


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class FakeRepo:
    """A throwaway git repo with a base commit, so changed_files() has real input."""

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "config", "user.email", "test@example.invalid")
        git(self.root, "config", "user.name", "test")
        write(self.root, "README.md", "base\n")
        write(self.root, "ladder_version.txt", "4\n")
        git(self.root, "add", "README.md", "ladder_version.txt")
        git(self.root, "commit", "-qm", "base")
        self.base = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def commit(self, files: dict, message: str = "change") -> None:
        for rel, text in files.items():
            write(self.root, rel, text)
        git(self.root, "add", *files.keys())
        git(self.root, "commit", "-qm", message)

    def close(self) -> None:
        self._tmp.cleanup()


class LadderBumpGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = FakeRepo()
        patcher = mock.patch.object(clb, "REPO_ROOT", self.repo.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.repo.close)

    def run_main(self, *argv: str, env: dict | None = None) -> int:
        with mock.patch.object(
            sys, "argv", ["check_ladder_bump.py", "--base", self.repo.base, *argv]
        ):
            with mock.patch.dict("os.environ", env or {}, clear=False):
                return clb.main()

    # -- the case the guard exists for: gameplay change, no bump ------------

    def test_gameplay_without_bump_is_advisory_green_without_strict(self):
        """Documents the pre-#1178 behaviour: warning, exit 0. Not a bug -- a default."""
        self.repo.commit({"godot/data/events/balancing/rarity_curves.json": "{}\n"})
        self.assertEqual(self.run_main(), 0)

    def test_gameplay_without_bump_fails_under_strict(self):
        """The load-bearing assertion: this guard CAN go red."""
        self.repo.commit({"godot/data/events/balancing/rarity_curves.json": "{}\n"})
        self.assertEqual(self.run_main("--strict", env={"LADDER_ACK": ""}), 1)

    def test_core_script_change_without_bump_fails_under_strict(self):
        self.repo.commit({"godot/scripts/core/doom_system.gd": "extends Node\n"})
        self.assertEqual(self.run_main("--strict", env={"LADDER_ACK": ""}), 1)

    # -- the reverse direction: bump with nothing to justify it -------------

    def test_bump_without_gameplay_change_fails_under_strict(self):
        self.repo.commit({"ladder_version.txt": "5\n"})
        self.assertEqual(self.run_main("--strict", env={"LADDER_ACK": ""}), 1)

    # -- the legitimate quiet cases: must stay green ------------------------

    def test_consistent_bump_passes(self):
        self.repo.commit(
            {
                "godot/scripts/core/doom_system.gd": "extends Node\n",
                "ladder_version.txt": "5\n",
            }
        )
        self.assertEqual(self.run_main("--strict", env={"LADDER_ACK": ""}), 0)

    def test_cosmetic_only_diff_passes(self):
        self.repo.commit({"godot/scripts/ui/main_ui.gd": "extends Control\n"})
        self.assertEqual(self.run_main("--strict", env={"LADDER_ACK": ""}), 0)

    def test_tests_and_godot_metadata_are_not_gameplay_surface(self):
        self.repo.commit(
            {
                "godot/tests/unit/test_thing.gd": "extends GutTest\n",
                "godot/data/events/thing.json.uid": "uid://abc\n",
            }
        )
        self.assertEqual(self.run_main("--strict", env={"LADDER_ACK": ""}), 0)

    def test_markdown_under_data_is_not_gameplay_surface(self):
        """The real #1137 false positive: a README under godot/data/ flagged as gameplay."""
        self.assertFalse(clb.is_gameplay_surface("godot/data/events/overrides/README.md"))
        self.repo.commit({"godot/data/events/overrides/README.md": "docs\n"})
        self.assertEqual(self.run_main("--strict", env={"LADDER_ACK": ""}), 0)

    def test_patch_notes_are_not_gameplay_surface(self):
        """Release copy under godot/data/ changes every release; it cannot move a score."""
        self.assertFalse(clb.is_gameplay_surface("godot/data/patch_notes.json"))
        self.repo.commit({"godot/data/patch_notes.json": '{"versions": []}\n'})
        self.assertEqual(self.run_main("--strict", env={"LADDER_ACK": ""}), 0)

    # -- the ack escape hatch ----------------------------------------------

    def test_written_ack_turns_a_strict_failure_green(self):
        self.repo.commit({"godot/data/events/balancing/rarity_curves.json": "{}\n"})
        ack = "please explain\n\nladder-ack: comment-only retune, no score can move\n"
        self.assertEqual(self.run_main("--strict", env={"LADDER_ACK": ack}), 0)

    def test_token_ack_reason_is_not_an_ack(self):
        self.repo.commit({"godot/data/events/balancing/rarity_curves.json": "{}\n"})
        self.assertEqual(self.run_main("--strict", env={"LADDER_ACK": "ladder-ack: y"}), 1)

    def test_ack_env_name_is_configurable(self):
        self.repo.commit({"godot/data/events/balancing/rarity_curves.json": "{}\n"})
        env = {"LADDER_ACK": "", "OTHER_ACK": "ladder-ack: reviewed against 3.3 checklist"}
        self.assertEqual(self.run_main("--strict", "--ack-env", "OTHER_ACK", env=env), 0)

    def test_find_ack_parsing(self):
        self.assertIsNone(clb.find_ack(""))
        self.assertIsNone(clb.find_ack("no ack here at all"))
        self.assertIsNone(clb.find_ack("ladder-ack:"))
        self.assertIsNone(clb.find_ack("this mentions ladder-ack: inline but ends"))
        self.assertEqual(clb.find_ack("LADDER-ACK: cosmetic only"), "cosmetic only")
        self.assertEqual(clb.find_ack("  ladder-ack:  spaced reason  "), "spaced reason")


if __name__ == "__main__":
    unittest.main()
