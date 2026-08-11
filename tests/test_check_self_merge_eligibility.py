#!/usr/bin/env python3
"""Unit tests for tools/check_self_merge_eligibility.py -- the R1 self-merge gate.

Shape adopted from ``tests/test_check_ladder_bump.py``, for the same reason: the
gate's ``--self-test`` is the louder evidence (it replays the whole rule table and
prints the failure text a human will read), but a hermetic unittest suite pins the
individual rules so they cannot be quietly weakened one at a time.

What these lock down:

- **The gate can actually fail.** ``class:guard`` with no RED-RUN line in the body
  MUST produce a finding. If someone later makes the declaration optional, this
  test goes red rather than the job going quietly green (#640 is the local
  precedent: CI reported green while running zero tests).
- **It never blocks a normal PR.** No class label -> no findings, whatever the
  diff contains. A gate that fires on PRs making no claim gets switched off.
- **The docs rule knows this repo.** ``ladder_version.txt`` ends in ``.txt`` and is
  the leaderboard epoch SSOT; a suffix-only rule would wave it through as prose.
- **The RED-RUN parse matches check_ladder_bump's contract**: verdict plus a
  substantive reason, case-insensitive, findable among other prose.

No network, no GitHub, no git history: everything here is a pure function over
(labels, changed paths, PR body), so the rule stays provable offline.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import check_self_merge_eligibility as sme  # noqa: E402

RED_URL = "https://github.com/PipFoweraker/pdoom1/actions/runs/1234567890"
GOOD_BODY = f"Adds the gate.\n\nRED-RUN: {RED_URL} -- guard label, no declaration in body\n"


class DocumentationRuleTest(unittest.TestCase):
    """What counts as documentation for the class:docs claim."""

    def test_prose_paths_are_documentation(self):
        for path in (
            "docs/ROADMAP.md",
            "CHANGELOG.md",
            "docs/design/JAM_PRINT_SHEETS_2026-08-05.txt",
            "docs/game-design/decisions/ADR-0016.md",
            "dev-blog/2026-08-01-entry.md",
        ):
            self.assertTrue(sme.is_documentation(path), path)

    def test_code_and_config_are_not_documentation(self):
        for path in (
            "godot/scripts/core/doom_system.gd",
            "godot/data/events/balancing/rarity_curves.json",
            "tools/check_self_merge_eligibility.py",
            ".github/workflows/self-merge-eligibility.yml",
            "godot/project.godot",
        ):
            self.assertFalse(sme.is_documentation(path), path)

    def test_machine_read_txt_files_are_not_documentation(self):
        """The trap a suffix-only rule falls into.

        ladder_version.txt is the leaderboard board key (CLAUDE.md: a silent
        drift forks it). Merging that unreviewed under a docs label is exactly
        the irreversible class R1 keeps with Pip.
        """
        for path in (
            "ladder_version.txt",
            "version.txt",
            "requirements.txt",
            "requirements-dev.txt",
            "godot/build_stamp.txt",
            "godot/steam_appid.txt",
        ):
            self.assertFalse(sme.is_documentation(path), path)

    def test_vendored_prose_is_not_our_documentation(self):
        self.assertFalse(sme.is_documentation("godot/addons/gut/README.md"))

    def test_windows_separators_are_normalised(self):
        self.assertTrue(sme.is_documentation("docs\\ROADMAP.md"))
        self.assertFalse(sme.is_documentation("godot\\scripts\\core\\doom_system.gd"))


class RedRunParsingTest(unittest.TestCase):
    """check_ladder_bump's contract: a verdict is not a record without a reason."""

    def test_no_declaration(self):
        self.assertIsNone(sme.find_red_run(""))
        self.assertIsNone(sme.find_red_run("Adds a check. It works."))

    def test_bare_reference_is_not_a_declaration(self):
        self.assertIsNone(sme.find_red_run("RED-RUN: 1234567890"))
        self.assertIsNone(sme.find_red_run(f"RED-RUN: {RED_URL}"))
        self.assertIsNone(sme.find_red_run("RED-RUN: 1234567890 -- x"))

    def test_url_and_numeric_ids_both_parse(self):
        self.assertIsNotNone(sme.find_red_run(f"RED-RUN: {RED_URL} -- inverted the assertion"))
        self.assertIsNotNone(sme.find_red_run("RED-RUN: 1234567890 -- inverted the assertion"))

    def test_a_short_number_is_not_a_run_id(self):
        self.assertIsNone(sme.find_red_run("RED-RUN: 42 -- inverted the assertion"))

    def test_case_insensitive_and_found_among_prose(self):
        body = "Fixes the gate.\n\nred-run: 1234567890 -- ran with the guard removed\n\nCheers"
        self.assertIsNotNone(sme.find_red_run(body))

    def test_the_documented_format_string_actually_parses_a_real_line(self):
        """The failure message tells people a shape; that shape must work."""
        line = sme.RED_RUN_FORMAT.replace("<run-url-or-run-id>", "1234567890").replace(
            "<what was broken to make it fail>", "removed the assertion"
        )
        self.assertIsNotNone(sme.find_red_run(line))


class LabelParsingTest(unittest.TestCase):
    """Actions can hand us either shape; seeing zero labels would pass everything."""

    def test_json_array_of_names(self):
        self.assertEqual(
            sme.parse_labels('["class:guard", "ship:now"]'), ["class:guard", "ship:now"]
        )

    def test_json_array_of_label_objects(self):
        self.assertEqual(sme.parse_labels('[{"name": "class:docs"}]'), ["class:docs"])

    def test_comma_and_newline_separated(self):
        self.assertEqual(sme.parse_labels("class:guard, needs:pip"), ["class:guard", "needs:pip"])
        self.assertEqual(sme.parse_labels("class:guard\nneeds:pip\n"), ["class:guard", "needs:pip"])

    def test_empty_and_malformed(self):
        self.assertEqual(sme.parse_labels(""), [])
        self.assertEqual(sme.parse_labels("   "), [])
        self.assertEqual(sme.parse_labels("[not json"), [])


class GateBehaviourTest(unittest.TestCase):
    """The five rules, end to end."""

    # -- rule 3: never block a normal PR ------------------------------------

    def test_no_class_label_is_neutral(self):
        self.assertEqual(sme.run([], ["godot/scripts/core/doom_system.gd"], ""), [])
        self.assertEqual(sme.run(["bug", "ship:now"], ["anything.gd"], ""), [])

    def test_needs_pip_alone_is_neutral(self):
        """A hold nobody is trying to skip is not this gate's business."""
        self.assertEqual(sme.run(["needs:pip"], ["godot/scripts/core/doom_system.gd"], ""), [])

    # -- rule 4: docs class --------------------------------------------------

    def test_docs_only_diff_passes(self):
        self.assertEqual(sme.run(["class:docs"], ["docs/ROADMAP.md", "README.md"], ""), [])

    def test_docs_class_with_a_code_file_fails_and_names_it(self):
        findings = sme.run(["class:docs"], ["docs/ROADMAP.md", "godot/autoload/balance.gd"], "")
        self.assertTrue(findings)
        self.assertIn("godot/autoload/balance.gd", findings[0])
        self.assertNotIn("docs/ROADMAP.md", findings[0])

    def test_docs_class_with_no_changed_paths_fails(self):
        """Passing on no evidence is how a broken checkout becomes a green gate."""
        self.assertTrue(sme.run(["class:docs"], [], ""))

    # -- rule 5: guard class -------------------------------------------------

    def test_guard_without_a_red_run_declaration_fails(self):
        """The load-bearing assertion: this gate CAN go red (estate rule 5g)."""
        findings = sme.run(["class:guard"], [".github/workflows/x.yml"], "Adds a check.")
        self.assertTrue(findings)
        self.assertIn("RED-RUN:", findings[0])

    def test_guard_with_a_red_run_declaration_passes(self):
        self.assertEqual(sme.run(["class:guard"], [".github/workflows/x.yml"], GOOD_BODY), [])

    def test_guard_class_does_not_care_what_paths_changed(self):
        """A guard can live anywhere -- a workflow, a script, a hook, a query."""
        self.assertEqual(sme.run(["class:guard"], ["scripts/check_thing.py"], GOOD_BODY), [])

    # -- rules 1 and 2: the vetoes ------------------------------------------

    def test_needs_pip_fails_a_guard_claim_even_with_a_red_run(self):
        self.assertTrue(
            sme.run(["class:guard", "needs:pip"], [".github/workflows/x.yml"], GOOD_BODY)
        )

    def test_needs_pip_fails_a_docs_claim_even_on_a_clean_docs_diff(self):
        self.assertTrue(sme.run(["class:docs", "needs:pip"], ["docs/ROADMAP.md"], ""))

    def test_both_class_labels_fail(self):
        findings = sme.run(["class:guard", "class:docs"], ["docs/ROADMAP.md"], GOOD_BODY)
        self.assertTrue(findings)
        self.assertIn("one class or", findings[0])

    def test_label_matching_is_case_insensitive(self):
        self.assertTrue(sme.run(["Class:Guard"], [".github/workflows/x.yml"], "no declaration"))


class SelfTestTableTest(unittest.TestCase):
    """The script's own --self-test must agree with these tests."""

    def test_self_test_passes(self):
        self.assertEqual(sme.self_test(), 0)

    def test_the_table_contains_both_polarities(self):
        expectations = {case[4] for case in sme.SELF_TEST_CASES}
        self.assertEqual(expectations, {0, 1}, "a table with one polarity proves nothing")


if __name__ == "__main__":
    unittest.main()
