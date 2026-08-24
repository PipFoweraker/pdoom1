#!/usr/bin/env python3
"""Unit tests for tools/check_patch_notes.py.

WHAT THIS GUARDS, and the honest scope of the claim:

    godot/tests/unit/test_patch_notes.gd ALREADY asserts that patch_notes.json has an
    entry for the shipped version. The tool under test is not a new assertion -- it is
    the same assertion moved into a tier that pre-commit can run, because the GUT tier
    needs a Godot binary and an import pass and therefore never fires on a commit.

    The failure it exists to catch: a release bump touches version.txt and forgets
    godot/data/patch_notes.json, so whats_new_modal.gd finds no entry and shows every
    player its fallback. Nothing errors; the player is simply told the release had
    nothing to say. That is a value meaning "I could not tell" rendered as a value
    meaning "fine" (Pip's ruling, 2026-08-23).

    These tests drive the tool through fixtures rather than the real repo, so they
    prove the detector goes RED. The one test that reads the real tree asserts the
    shipped state is currently clean -- which is latent, not guaranteed, and is exactly
    why the gate exists.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import check_patch_notes as cpn  # noqa: E402


def write_case(root: Path, version: str, notes_obj) -> tuple:
    """Write a version.txt + patch_notes.json pair; return the two paths."""
    version_file = root / "version.txt"
    version_file.write_text(version + "\n", encoding="utf-8")
    notes_file = root / "patch_notes.json"
    if notes_obj is not None:
        if isinstance(notes_obj, str):
            notes_file.write_text(notes_obj, encoding="utf-8")
        else:
            notes_file.write_text(json.dumps(notes_obj), encoding="utf-8")
    return version_file, notes_file


GOOD_ENTRY = {
    "version": "1.2.3",
    "title": "A Real Release",
    "date": "2026-01-01",
    "highlights": ["something happened"],
    "sections": {"added": [], "fixed": [], "changed": []},
}


class CheckPatchNotesTests(unittest.TestCase):
    def _check(self, version, notes_obj):
        with tempfile.TemporaryDirectory() as td:
            vf, nf = write_case(Path(td), version, notes_obj)
            return cpn.check(vf, nf)

    def test_matching_entry_is_clean(self):
        """The gate must be capable of returning the OTHER answer."""
        problems = self._check("1.2.3", {"versions": [GOOD_ENTRY]})
        self.assertEqual(problems, [], "a well-formed entry should produce no problems")

    def test_missing_entry_for_shipped_version_fails(self):
        problems = self._check("9.9.9", {"versions": [GOOD_ENTRY]})
        self.assertTrue(problems)
        self.assertIn("no entry for the shipped version 9.9.9", problems[0])

    def test_version_mismatch_is_exact_string_matching(self):
        """The modal matches the EXACT string, so 'v1.2.3' is not '1.2.3'."""
        entry = dict(GOOD_ENTRY, version="v1.2.3")
        problems = self._check("1.2.3", {"versions": [entry]})
        self.assertTrue(problems, "a 'v' prefix is the same failure as no entry at all")

    def test_missing_notes_file_fails(self):
        problems = self._check("1.2.3", None)
        self.assertTrue(problems)
        self.assertIn("MISSING", problems[0])

    def test_unparseable_json_fails(self):
        problems = self._check("1.2.3", "{not json at all")
        self.assertTrue(problems)
        self.assertIn("UNREADABLE", problems[0])

    def test_valid_json_of_the_wrong_shape_fails(self):
        """Mirrors whats_new_modal.gd's shape guard: a bare array parses fine."""
        problems = self._check("1.2.3", [GOOD_ENTRY])
        self.assertTrue(problems)
        self.assertIn("not an object with a 'versions' array", problems[0])

    def test_versions_not_a_list_fails(self):
        problems = self._check("1.2.3", {"versions": "nope"})
        self.assertTrue(problems)
        self.assertIn("not an object with a 'versions' array", problems[0])

    def test_entry_with_no_title_fails(self):
        entry = dict(GOOD_ENTRY, title="")
        problems = self._check("1.2.3", {"versions": [entry]})
        self.assertTrue(any("no title" in p for p in problems))

    def test_empty_entry_fails_because_it_renders_a_blank_modal(self):
        """An entry with no lines is the fallback message with extra steps."""
        entry = {
            "version": "1.2.3",
            "title": "Titled But Empty",
            "highlights": [],
            "sections": {"added": [], "fixed": [], "changed": []},
        }
        problems = self._check("1.2.3", {"versions": [entry]})
        self.assertTrue(any("blank modal" in p for p in problems))

    def test_section_lines_count_as_body(self):
        entry = {
            "version": "1.2.3",
            "title": "Fixes Only",
            "highlights": [],
            "sections": {"added": [], "fixed": ["fixed a thing"], "changed": []},
        }
        self.assertEqual(self._check("1.2.3", {"versions": [entry]}), [])

    def test_empty_version_file_fails(self):
        problems = self._check("", {"versions": [GOOD_ENTRY]})
        self.assertTrue(problems)
        self.assertIn("EMPTY", problems[0])


class ShippedTreeTests(unittest.TestCase):
    def test_the_real_repo_is_currently_clean(self):
        """Latent, not guaranteed -- which is the reason the gate was added.

        version.txt was 0.14.3 and patch_notes.json had a 0.14.3 entry when this was
        written. If this fails, the shipped build shows its fallback to every player.
        """
        problems = cpn.check()
        self.assertEqual(
            problems,
            [],
            "patch_notes.json no longer covers version.txt: {}".format(problems),
        )

    def test_tool_exits_zero_on_the_real_repo(self):
        self.assertEqual(cpn.main(["--quiet"]), 0)


if __name__ == "__main__":
    unittest.main()
