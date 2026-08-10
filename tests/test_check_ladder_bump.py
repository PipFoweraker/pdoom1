#!/usr/bin/env python3
"""Unit tests for tools/check_ladder_bump.py -- the board-key bump guard (issue #1178).

ADOPTED FROM PR #1185, which lost the adjudication on its classification rules
but was right about this: the guard needs a hermetic test suite that runs on a
synthetic repo, not only the `--self-test` replay of real history. `--self-test`
is the stronger evidence (it proves the gate red against the commits it actually
missed), but it needs full git history and SKIPS on a shallow clone. These tests
pin the classification rules unconditionally, so a shallow CI checkout cannot
silently reduce this gate's coverage to nothing.

What they lock down:

- **The guard can actually fail.** Until 2026-08-09 CI ran this check as
  ``python tools/check_ladder_bump.py --base ... || true``, so it was structurally
  incapable of failing a build. These tests assert the findings directly, so a
  future re-disarming shows up as a red test rather than a green job that checks
  nothing (#640).
- **The polarity is denylist, not allowlist.** ``godot/autoload/event_service.gd``
  MUST be gameplay surface. The old allowlist covered only ``godot/scripts/core/``
  and ``godot/data/``, so it called a real event-scheduling change clean
  (``d7b47a1a``, #1101). PR #1185 kept that allowlist; this is the test that
  distinguishes the two designs.
- **The known false positives stay green:** ``patch_notes.json`` (release copy,
  changes every patch) and ``.md`` prose under ``godot/data/``.
- Declaration parsing, including #1185's rule that a token reason is not a
  reason.
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


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class FakeRepo:
    """A throwaway git repo, so the gate runs against real `git diff` output."""

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
        self.base = git(self.root, "rev-parse", "HEAD")

    def commit(self, files: dict, message: str = "change") -> None:
        for rel, text in files.items():
            write(self.root, rel, text)
        git(self.root, "add", *files.keys())
        git(self.root, "commit", "-qm", message)

    def close(self) -> None:
        self._tmp.cleanup()


class ClassificationTest(unittest.TestCase):
    """Path polarity. No repo needed -- these are pure functions."""

    def test_autoload_is_gameplay_surface(self):
        """The #1101 miss (d7b47a1a). The old allowlist -- and #1185's -- said False."""
        self.assertFalse(clb.is_cosmetic_path("godot/autoload/event_service.gd"))
        self.assertFalse(clb.is_cosmetic_path("godot/autoload/balance.gd"))

    def test_an_unforeseen_gameplay_directory_fails_safe(self):
        """The point of the denylist: a system that MOVES is still covered."""
        self.assertFalse(clb.is_cosmetic_path("godot/systems/brand_new_thing.gd"))

    def test_core_and_data_remain_gameplay_surface(self):
        self.assertFalse(clb.is_cosmetic_path("godot/scripts/core/doom_system.gd"))
        self.assertFalse(clb.is_cosmetic_path("godot/data/events/balancing/rarity_curves.json"))

    def test_presentation_paths_are_cosmetic(self):
        for path in (
            "godot/scripts/ui/main_ui.gd",
            "godot/scenes/menu.tscn",
            "godot/assets/icon.png",
            "godot/theme/colors.tres",
            "godot/tests/unit/test_thing.gd",
            "godot/addons/gut/gut.gd",
        ):
            self.assertTrue(clb.is_cosmetic_path(path), path)

    def test_patch_notes_are_not_gameplay_surface(self):
        """Release copy under godot/data/ changes every patch; it cannot move a score.

        This was the v0.14.1 false positive (0dc8adb9): the old gate cried wolf
        on a correct patch cut.
        """
        self.assertTrue(clb.is_cosmetic_path("godot/data/patch_notes.json"))

    def test_markdown_and_godot_metadata_are_not_gameplay_surface(self):
        """The #1137 run named an events README as gameplay surface."""
        self.assertTrue(clb.is_cosmetic_path("godot/data/events/overrides/README.md"))
        self.assertTrue(clb.is_cosmetic_path("godot/data/events/thing.json.uid"))
        self.assertTrue(clb.is_cosmetic_path("godot/assets/art.png.import"))

    def test_outside_the_game_root_is_cosmetic(self):
        self.assertTrue(clb.is_cosmetic_path("tools/check_ladder_bump.py"))
        self.assertTrue(clb.is_cosmetic_path("docs/ROADMAP.md"))


class DeclarationParsingTest(unittest.TestCase):
    """#1185's minimum-reason rule: a verdict without a reason is not a record."""

    def test_no_declaration(self):
        self.assertIsNone(clb.find_declaration(""))
        self.assertIsNone(clb.find_declaration("nothing to see here"))

    def test_bare_verdict_is_not_a_declaration(self):
        self.assertIsNone(clb.find_declaration("Ladder-Impact: none"))
        self.assertIsNone(clb.find_declaration("Ladder-Impact: none -- x"))

    def test_substantive_reason_is_accepted(self):
        self.assertIsNotNone(clb.find_declaration("Ladder-Impact: none -- comment-only edit"))
        self.assertIsNotNone(clb.find_declaration("ladder-impact: bump -- new event deck"))

    def test_declaration_is_found_among_other_prose(self):
        body = "Fixes a thing.\n\nLadder-Impact: none -- refactor, no reachable behaviour\n\nCheers"
        self.assertIsNotNone(clb.find_declaration(body))


class GateBehaviourTest(unittest.TestCase):
    """End-to-end over a real (synthetic) repo."""

    def setUp(self) -> None:
        self.repo = FakeRepo()
        patcher = mock.patch.object(clb, "REPO_ROOT", self.repo.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.repo.close)
        env = mock.patch.dict("os.environ", {"LADDER_DECLARATION_TEXT": ""}, clear=False)
        env.start()
        self.addCleanup(env.stop)

    def findings(self):
        return clb.run(self.repo.base, "HEAD")

    # -- the case the guard exists for --------------------------------------

    def test_gameplay_without_bump_or_declaration_is_a_finding(self):
        """The load-bearing assertion: this guard CAN go red."""
        self.repo.commit({"godot/data/events/balancing/rarity_curves.json": "{}\n"})
        self.assertTrue(self.findings())

    def test_autoload_change_without_bump_is_a_finding(self):
        """d7b47a1a in miniature -- the case an allowlist calls clean."""
        self.repo.commit({"godot/autoload/event_service.gd": "extends Node\n"})
        self.assertTrue(self.findings())

    # -- the legitimate quiet cases: must stay green ------------------------

    def test_consistent_bump_passes(self):
        self.repo.commit(
            {"godot/scripts/core/doom_system.gd": "extends Node\n", "ladder_version.txt": "5\n"}
        )
        self.assertEqual(self.findings(), [])

    def test_cosmetic_only_diff_passes(self):
        self.repo.commit({"godot/scripts/ui/main_ui.gd": "extends Control\n"})
        self.assertEqual(self.findings(), [])

    def test_patch_notes_only_diff_passes(self):
        self.repo.commit({"godot/data/patch_notes.json": '{"versions": []}\n'})
        self.assertEqual(self.findings(), [])

    # -- the declaration escape hatch ---------------------------------------

    def test_declaration_in_a_commit_message_clears_the_finding(self):
        self.repo.commit(
            {"godot/scripts/core/doom_system.gd": "extends Node\n"},
            message="refactor\n\nLadder-Impact: none -- rename only, no behaviour change\n",
        )
        self.assertEqual(self.findings(), [])

    def test_declaration_supplied_by_ci_clears_the_finding(self):
        self.repo.commit({"godot/scripts/core/doom_system.gd": "extends Node\n"})
        with mock.patch.dict(
            "os.environ",
            {"LADDER_DECLARATION_TEXT": "Ladder-Impact: none -- comment-only, verified by replay"},
        ):
            self.assertEqual(self.findings(), [])

    def test_token_reason_does_not_clear_the_finding(self):
        self.repo.commit({"godot/scripts/core/doom_system.gd": "extends Node\n"})
        with mock.patch.dict("os.environ", {"LADDER_DECLARATION_TEXT": "Ladder-Impact: none -- y"}):
            self.assertTrue(self.findings())


if __name__ == "__main__":
    unittest.main()
