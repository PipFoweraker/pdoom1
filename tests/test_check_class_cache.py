#!/usr/bin/env python3
"""Unit tests for tools/check_class_cache.py -- the stale-class-cache guard.

WHY THESE EXIST AT ALL, given that the bug they guard is invisible to CI:

    The guard's subject -- a stale `godot/.godot/global_script_class_cache.cfg` -- cannot
    occur in CI, because CI clones fresh and therefore always generates a correct cache.
    So CI cannot test the CONDITION. What it can and must test is the DETECTOR: that
    check_class_cache.py still goes red on a cache that does not describe its checkout.

    This is the #640 lesson applied to a new gate: a check nobody has watched fail is not
    known to work. The real RED run happened on the incident's own shape (Capacity removed
    from a real generated cache, 30 parse errors reproduced). These tests pin that shape as
    a fixture so the detector cannot silently degrade to a function that always returns 0.

The fixtures are byte-shaped like Godot's own writer output (see the real file: a single
`list=[{...}, {...}]` with `&"..."` StringName markers), so a change to that format breaks
these tests loudly instead of turning the guard into a no-op.
"""

import sys
import textwrap
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import check_class_cache as ccc  # noqa: E402


def cache_text(entries: list[tuple[str, str]]) -> str:
    """Render entries as Godot writes them: one list=[...] of dicts, StringName-marked."""
    records = []
    for name, path in entries:
        records.append(
            textwrap.dedent(
                f"""\
                {{
                "base": &"RefCounted",
                "class": &"{name}",
                "icon": "",
                "is_abstract": false,
                "is_tool": false,
                "language": &"GDScript",
                "path": "{path}"
                }}"""
            )
        )
    return "list=[" + ", ".join(records) + "]\n"


class FakeTree:
    """A minimal godot/ tree: .gd sources plus an optional .godot cache."""

    def __init__(self, root: Path):
        self.root = root
        (root / "scripts" / "core").mkdir(parents=True, exist_ok=True)

    def add_script(self, rel: str, body: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")

    def write_cache(self, entries: list[tuple[str, str]]) -> None:
        cache = self.root / ccc.CACHE_REL
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(cache_text(entries), encoding="utf-8")


class ScanSourceTests(unittest.TestCase):
    def setUp(self):
        self._dir = Path(__file__).resolve().parent / "_tmp_ccc_scan"
        self._cleanup()
        self._dir.mkdir(parents=True)
        self.tree = FakeTree(self._dir)
        self.patch = mock.patch.object(ccc, "GODOT_ROOT", self._dir)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self._cleanup()

    def _cleanup(self):
        import shutil

        if self._dir.exists():
            shutil.rmtree(self._dir)

    def test_finds_declaration_and_maps_to_res_path(self):
        self.tree.add_script(
            "scripts/core/capacity.gd", "extends RefCounted\nclass_name Capacity\n\nvar x = 1\n"
        )
        found = ccc.scan_source(self._dir)
        self.assertEqual(found, {"Capacity": "res://scripts/core/capacity.gd"})

    def test_class_name_with_inline_extends(self):
        self.tree.add_script("scripts/core/a.gd", "class_name Alpha extends Node\n")
        self.assertEqual(ccc.scan_source(self._dir), {"Alpha": "res://scripts/core/a.gd"})

    def test_commented_out_declaration_is_not_a_declaration(self):
        self.tree.add_script("scripts/core/b.gd", "# class_name Ghost\nextends Node\n")
        self.assertEqual(ccc.scan_source(self._dir), {})

    def test_declaration_quoted_in_a_docstring_is_not_a_declaration(self):
        self.tree.add_script(
            "scripts/core/c.gd",
            '"""\nDo not write class_name Ghost here.\n"""\nextends Node\n',
        )
        self.assertEqual(ccc.scan_source(self._dir), {})

    def test_inner_class_keyword_is_not_class_name(self):
        self.tree.add_script("scripts/core/d.gd", "extends Node\n\nclass Inner:\n\tvar y = 2\n")
        self.assertEqual(ccc.scan_source(self._dir), {})

    def test_generated_godot_dir_is_not_source(self):
        gen = self._dir / ".godot" / "junk.gd"
        gen.parent.mkdir(parents=True, exist_ok=True)
        gen.write_text("class_name Generated\n", encoding="utf-8")
        self.assertEqual(ccc.scan_source(self._dir), {})


class ParseCacheTests(unittest.TestCase):
    def setUp(self):
        self._dir = Path(__file__).resolve().parent / "_tmp_ccc_cache"
        self._cleanup()
        self._dir.mkdir(parents=True)
        self.tree = FakeTree(self._dir)

    def tearDown(self):
        self._cleanup()

    def _cleanup(self):
        import shutil

        if self._dir.exists():
            shutil.rmtree(self._dir)

    def test_parses_godot_writer_format(self):
        self.tree.write_cache(
            [
                ("ActionBarRenderer", "res://scripts/ui/action_bar_renderer.gd"),
                ("Capacity", "res://scripts/core/capacity.gd"),
            ]
        )
        parsed = ccc.parse_cache(self._dir / ccc.CACHE_REL)
        self.assertEqual(
            parsed,
            {
                "ActionBarRenderer": "res://scripts/ui/action_bar_renderer.gd",
                "Capacity": "res://scripts/core/capacity.gd",
            },
        )

    def test_absent_cache_is_none_not_empty(self):
        # None (cold, never generated) and {} (generated but empty) are different worlds;
        # conflating them would hide a truncated cache.
        self.assertIsNone(ccc.parse_cache(self._dir / ccc.CACHE_REL))

    def test_real_cache_in_this_checkout_parses(self):
        # Format-drift canary against the actual engine output, when it is present.
        real = ccc.GODOT_ROOT / ccc.CACHE_REL
        if not real.exists():
            self.skipTest("no generated cache in this checkout (fresh clone)")
        parsed = ccc.parse_cache(real)
        self.assertGreater(len(parsed), 50, "real cache parsed to implausibly few entries")
        for name, path in parsed.items():
            self.assertTrue(path.startswith("res://"), f"{name} -> {path}")


class CompareTests(unittest.TestCase):
    """The classification rules. These are what the guard's verdict reduces to."""

    def test_agreement_is_not_stale(self):
        both = {"Capacity": "res://scripts/core/capacity.gd"}
        findings = ccc.compare(both, dict(both))
        self.assertFalse(ccc.is_stale(findings))

    def test_missing_is_the_1211_shape(self):
        # Declared in source, absent from cache: the cache predates the file.
        declared = {
            "Capacity": "res://scripts/core/capacity.gd",
            "TurnManager": "res://scripts/core/turn_manager.gd",
        }
        cached = {"TurnManager": "res://scripts/core/turn_manager.gd"}
        findings = ccc.compare(declared, cached)
        self.assertTrue(ccc.is_stale(findings))
        self.assertEqual(findings["missing"], [("Capacity", "res://scripts/core/capacity.gd")])
        self.assertEqual(findings["moved"], [])
        self.assertEqual(findings["orphaned"], [])

    def test_moved_detects_a_rename_the_cache_did_not_see(self):
        declared = {"Capacity": "res://scripts/core/capacity.gd"}
        cached = {"Capacity": "res://scripts/core/old_capacity.gd"}
        findings = ccc.compare(declared, cached)
        self.assertTrue(ccc.is_stale(findings))
        self.assertEqual(
            findings["moved"],
            [("Capacity", "res://scripts/core/capacity.gd", "res://scripts/core/old_capacity.gd")],
        )

    def test_orphaned_detects_a_deletion_the_cache_did_not_see(self):
        findings = ccc.compare({}, {"Deleted": "res://scripts/core/gone.gd"})
        self.assertTrue(ccc.is_stale(findings))
        self.assertEqual(findings["orphaned"], [("Deleted", "res://scripts/core/gone.gd")])

    def test_cold_cache_reports_every_class_missing(self):
        declared = {"A": "res://a.gd", "B": "res://b.gd"}
        findings = ccc.compare(declared, {})
        self.assertEqual(len(findings["missing"]), 2)


class EndToEndTests(unittest.TestCase):
    """The guard must be capable of returning BOTH answers against a real-shaped tree.

    CLAUDE.md's relay rule: "a published command must be shown capable of returning the
    other answer." These two tests are that demonstration, in CI, forever.
    """

    def setUp(self):
        self._dir = Path(__file__).resolve().parent / "_tmp_ccc_e2e"
        self._cleanup()
        self._dir.mkdir(parents=True)
        self.tree = FakeTree(self._dir)
        self.tree.add_script(
            "scripts/core/capacity.gd", "extends RefCounted\nclass_name Capacity\n"
        )
        self.tree.add_script(
            "scripts/core/turn_manager.gd", "extends RefCounted\nclass_name TurnManager\n"
        )
        self.patch = mock.patch.object(ccc, "GODOT_ROOT", self._dir)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self._cleanup()

    def _cleanup(self):
        import shutil

        if self._dir.exists():
            shutil.rmtree(self._dir)

    def test_green_when_cache_agrees(self):
        self.tree.write_cache(
            [
                ("Capacity", "res://scripts/core/capacity.gd"),
                ("TurnManager", "res://scripts/core/turn_manager.gd"),
            ]
        )
        self.assertEqual(ccc.main(["--quiet"]), 0)

    def test_red_on_the_incident_shape(self):
        # The 2026-08-13 cache: correct about everything except the file #1211 added.
        self.tree.write_cache([("TurnManager", "res://scripts/core/turn_manager.gd")])
        self.assertEqual(ccc.main([]), 1)

    def test_repair_without_a_godot_binary_exits_2_not_0(self):
        # A missing engine must never be reported as a clean cache.
        self.tree.write_cache([("TurnManager", "res://scripts/core/turn_manager.gd")])
        with mock.patch.object(ccc, "find_godot", return_value=None):
            self.assertEqual(ccc.main(["--repair"]), 2)

    def test_repair_reports_failure_when_import_does_not_fix_it(self):
        self.tree.write_cache([("TurnManager", "res://scripts/core/turn_manager.gd")])
        with (
            mock.patch.object(ccc, "find_godot", return_value="/fake/godot"),
            mock.patch.object(ccc, "run_import", return_value=0) as fake_import,
        ):
            self.assertEqual(ccc.main(["--repair"]), 1)
        fake_import.assert_called_once()


if __name__ == "__main__":
    unittest.main()
