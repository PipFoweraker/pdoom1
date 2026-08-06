#!/usr/bin/env python3
"""Unit tests for scripts/generate_action_taxonomy.py (the action-taxonomy checker).

What these lock down:

- Duplicate id detection across files -- the live `take_loan` defect, asserted
  against a synthetic fixture AND against the real tree, so a future dedup makes
  the real-tree assertion fail loudly rather than the tool going quietly green on
  a bug nobody re-read.
- Missing / unknown `category`.
- The two-tier category-disagreement rule: ERROR when the members' category is one
  the action bar renders (the #1130 `fundraise` defect, replayed as a fixture),
  WARNING when it is a submenu-only namespace with no render group.
- Depth (no door inside a door), unbuildable doors, orphan domains, stale hides,
  the door cap.
- The GDScript readers really parse the two real files (category_order,
  HIDDEN_FROM_ACTION_BAR_IDS, GRID_CONFIG keys) rather than silently falling back.
- The guard can actually fail: analyse() over a tree with an injected duplicate
  goes red naming BOTH files, and green when the injection is removed. Two guards
  shipped in this repo could not fail; this asserts ours can.

Run: python -m unittest tests.test_generate_action_taxonomy -v
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_action_taxonomy as gat  # noqa: E402

RENDER_CATEGORIES = ["funding", "hiring", "research", "management", "other"]


def rec(action_id, domain, category, is_submenu=False, index=0, name="X", **extra):
    raw = {"id": action_id, "name": name, "category": category}
    if is_submenu:
        raw["is_submenu"] = True
    raw.update(extra)
    return {
        "id": action_id,
        "name": name,
        "domain": domain,
        "file": "%s.json" % domain,
        "category": category,
        "is_submenu": is_submenu,
        "index": index,
        "raw": raw,
    }


def run(records, hidden=None, grid=None, render=None):
    return gat.analyse(
        records,
        render if render is not None else RENDER_CATEGORIES,
        hidden or [],
        grid if grid is not None else ["fundraise"],
    )


def joined(messages):
    return "\n".join(messages)


class DuplicateIds(unittest.TestCase):
    def test_duplicate_across_files_is_an_error_naming_both(self):
        result = run(
            [
                rec("fundraise", "core", "funding", is_submenu=True),
                rec("take_loan", "fundraising", "funding"),
                rec("take_loan", "financing", "financing"),
                rec("financing", "core", "financing", is_submenu=True, index=1),
            ],
            grid=["fundraise", "financing"],
        )
        errors = joined(result["errors"])
        self.assertIn("DUPLICATE ID 'take_loan'", errors)
        self.assertIn("fundraising.json", errors)
        self.assertIn("financing.json", errors)
        self.assertEqual(result["unique_ids"], 3)

    def test_duplicate_error_names_the_fields_the_records_disagree_on(self):
        """ "Duplicate" understates it: the real pair promise different money."""
        result = run(
            [
                rec("fundraise", "core", "funding", is_submenu=True),
                rec("take_loan", "fundraising", "funding", gains={"money": 75000}),
                rec("take_loan", "financing", "financing"),
                rec("financing", "core", "financing", is_submenu=True, index=1),
            ],
            grid=["fundraise", "financing"],
        )
        errors = joined(result["errors"])
        self.assertIn("They DISAGREE on:", errors)
        self.assertIn("gains", errors)
        self.assertIn("category", errors)

    def test_identical_duplicates_still_error_and_say_they_are_identical(self):
        a = rec("clone", "fundraising", "funding")
        b = rec("clone", "financing", "funding")
        result = run(
            [
                rec("fundraise", "core", "funding", is_submenu=True),
                rec("financing", "core", "funding", is_submenu=True, index=1),
                a,
                b,
            ],
            grid=["fundraise", "financing"],
        )
        errors = joined(result["errors"])
        self.assertIn("DUPLICATE ID 'clone'", errors)
        self.assertIn("the records are identical", errors)

    def test_no_duplicate_when_ids_are_unique(self):
        result = run(
            [
                rec("fundraise", "core", "funding", is_submenu=True),
                rec("take_loan", "fundraising", "funding"),
            ]
        )
        self.assertNotIn("DUPLICATE", joined(result["errors"]))


class Categories(unittest.TestCase):
    def test_missing_category_is_an_error(self):
        result = run(
            [
                rec("fundraise", "core", "funding", is_submenu=True),
                rec("take_loan", "fundraising", None),
            ]
        )
        self.assertIn("MISSING CATEGORY on 'take_loan'", joined(result["errors"]))

    def test_unknown_category_is_an_error(self):
        result = run(
            [
                rec("fundraise", "core", "funding", is_submenu=True),
                rec("take_loan", "fundraising", "funding"),
                rec("stray", "core", "wibble"),
            ]
        )
        self.assertIn("UNKNOWN CATEGORY 'wibble'", joined(result["errors"]))

    def test_namespace_categories_are_known(self):
        """`travel`/`office`/... are absent from category_order but legitimate."""
        result = run(
            [
                rec("travel", "core", "research", is_submenu=True),
                rec("submit_paper", "travel", "travel"),
            ],
            grid=["travel"],
        )
        self.assertNotIn("UNKNOWN CATEGORY", joined(result["errors"]))


class CategoryDisagreement(unittest.TestCase):
    def test_the_fundraise_defect_is_an_error(self):
        """#1130 replayed: door tagged `management`, members `funding`.

        `funding` IS a render category, so the door sorted into a group unrelated
        to what it opens -- the tile rendered tenth and fell below the fold.
        """
        result = run(
            [
                rec("fundraise", "core", "management", is_submenu=True),
                rec("fundraise_small", "fundraising", "funding"),
                rec("fundraise_big", "fundraising", "funding"),
            ]
        )
        errors = joined(result["errors"])
        self.assertIn("CATEGORY DISAGREEMENT", errors)
        self.assertIn("door 'fundraise' is category 'management'", errors)
        self.assertIn("funding", errors)

    def test_agreement_is_silent(self):
        result = run(
            [
                rec("fundraise", "core", "funding", is_submenu=True),
                rec("fundraise_small", "fundraising", "funding"),
            ]
        )
        self.assertNotIn("CATEGORY DISAGREEMENT", joined(result["errors"]))

    def test_namespace_mismatch_is_only_a_warning(self):
        """A door CANNOT carry `travel`: the action bar has no group for it."""
        result = run(
            [
                rec("travel", "core", "research", is_submenu=True),
                rec("submit_paper", "travel", "travel"),
            ],
            grid=["travel"],
        )
        self.assertNotIn("CATEGORY DISAGREEMENT", joined(result["errors"]))
        self.assertIn("NAMESPACE CATEGORY", joined(result["warnings"]))

    def test_partial_agreement_counts_as_agreement(self):
        result = run(
            [
                rec("fundraise", "core", "funding", is_submenu=True),
                rec("a", "fundraising", "funding"),
                rec("b", "fundraising", "management"),
            ]
        )
        self.assertNotIn("CATEGORY DISAGREEMENT", joined(result["errors"]))


class Structure(unittest.TestCase):
    def test_door_inside_a_door_is_a_depth_violation(self):
        result = run(
            [
                rec("fundraise", "core", "funding", is_submenu=True),
                rec("financing", "fundraising", "funding", is_submenu=True),
            ],
            grid=["fundraise", "financing"],
        )
        self.assertIn("DEPTH VIOLATION", joined(result["errors"]))

    def test_door_without_a_builder_is_an_error(self):
        result = run(
            [
                rec("fundraise", "core", "funding", is_submenu=True),
                rec("fundraise_small", "fundraising", "funding"),
            ],
            grid=[],
        )
        self.assertIn("NO BUILDER for door 'fundraise'", joined(result["errors"]))

    def test_bespoke_builders_satisfy_the_builder_check(self):
        result = run(
            [
                rec("hire_staff", "core", "hiring", is_submenu=True),
                rec("hire_manager", "hiring", "hiring"),
            ],
            grid=[],
        )
        self.assertNotIn("NO BUILDER", joined(result["errors"]))

    def test_grid_panel_with_no_door_is_a_warning(self):
        result = run(
            [
                rec("fundraise", "core", "funding", is_submenu=True),
                rec("fundraise_small", "fundraising", "funding"),
            ],
            grid=["fundraise", "ghost_panel"],
        )
        self.assertIn("ORPHAN BUILDER", joined(result["warnings"]))

    def test_unmapped_door_is_an_error(self):
        result = run([rec("mystery_door", "core", "funding", is_submenu=True)], grid=[])
        self.assertIn("UNMAPPED DOOR 'mystery_door'", joined(result["errors"]))

    def test_stale_hide_is_an_error(self):
        result = run(
            [
                rec("fundraise", "core", "funding", is_submenu=True),
                rec("fundraise_small", "fundraising", "funding"),
            ],
            hidden=["ghost_action"],
        )
        self.assertIn("STALE HIDE", joined(result["errors"]))

    def test_hidden_actions_are_not_counted_as_loose_tiles(self):
        result = run(
            [
                rec("fundraise", "core", "funding", is_submenu=True),
                rec("fundraise_small", "fundraising", "funding"),
                rec("interview_next", "core", "hiring"),
            ],
            hidden=["interview_next"],
        )
        self.assertEqual(result["loose"], [])

    def test_door_cap_fires_above_the_limit(self):
        records = []
        for n, (door, domain) in enumerate(gat.DOOR_DOMAIN.items()):
            records.append(rec(door, "core", "funding", is_submenu=True, index=n))
            records.append(rec("%s_member" % domain, domain, "funding", index=n))
        result = run(records, grid=list(gat.DOOR_DOMAIN))
        self.assertNotIn("DOOR CAP", joined(result["errors"]))
        self.assertLessEqual(len(result["doors"]), gat.MAX_DOORS)


class GdscriptReaders(unittest.TestCase):
    """The readers must really parse the real files; a silent fallback is the bug."""

    def test_category_order_is_read_from_the_renderer(self):
        cats = gat.read_render_categories(gat.RENDERER.read_text(encoding="utf-8"))
        self.assertIn("funding", cats)
        self.assertIn("hiring", cats)
        self.assertGreaterEqual(len(cats), 5)

    def test_hidden_ids_are_read_from_the_renderer(self):
        hidden = gat.read_hidden_ids(gat.RENDERER.read_text(encoding="utf-8"))
        self.assertIn("interview_next", hidden)

    def test_grid_config_keys_exclude_nested_entry_keys(self):
        grid = gat.read_grid_config_ids(gat.SUBMENU_CONTROLLER.read_text(encoding="utf-8"))
        self.assertIn("fundraise", grid)
        self.assertIn("operations", grid)
        # Nested per-entry keys must NOT leak in as if they were panels.
        for leak in ("panel_size", "summary", "key_labels", "log_label"):
            self.assertNotIn(leak, grid)


class RealTree(unittest.TestCase):
    """Assertions about the tree as it stands. These are meant to change with it."""

    def setUp(self):
        self.records, self.notes = gat.load_actions()
        renderer = gat.RENDERER.read_text(encoding="utf-8")
        self.result = gat.analyse(
            self.records,
            gat.read_render_categories(renderer),
            gat.read_hidden_ids(renderer),
            gat.read_grid_config_ids(gat.SUBMENU_CONTROLLER.read_text(encoding="utf-8")),
        )

    def test_inventory_is_62_entries_in_11_action_files(self):
        """The commission said 64; risk_contributions.json holds ZERO actions."""
        self.assertEqual(len(self.records), 62)
        self.assertEqual(len({r["file"] for r in self.records}), 11)
        self.assertEqual(len(list(gat.ACTIONS_DIR.glob("*.json"))), 12)
        self.assertTrue(any("risk_contributions.json" in n for n in self.notes))

    def test_take_loan_is_still_duplicated_and_the_checker_says_so(self):
        """Delete this assertion WHEN take_loan is deduped -- and only then.

        Failing here means the defect was fixed, which is the moment to flip the
        checker from report-only to a blocking pre-commit gate.
        """
        self.assertEqual(len(self.records) - self.result["unique_ids"], 1)
        self.assertIn("DUPLICATE ID 'take_loan'", joined(self.result["errors"]))

    def test_take_loan_is_the_only_error_left(self):
        self.assertEqual(len(self.result["errors"]), 1, joined(self.result["errors"]))

    def test_nine_doors_under_the_cap(self):
        self.assertEqual(len(self.result["doors"]), 9)
        self.assertLessEqual(len(self.result["doors"]), gat.MAX_DOORS)


class GuardCanFail(unittest.TestCase):
    """Red-first: inject a duplicate, watch it name both files, remove it, green."""

    def test_injecting_a_duplicate_into_the_real_records_goes_red(self):
        records, _ = gat.load_actions()
        renderer = gat.RENDERER.read_text(encoding="utf-8")
        args = (
            gat.read_render_categories(renderer),
            gat.read_hidden_ids(renderer),
            gat.read_grid_config_ids(gat.SUBMENU_CONTROLLER.read_text(encoding="utf-8")),
        )

        clone = dict(records[-1])
        clone["domain"] = "publicity"
        clone["file"] = "publicity.json"
        injected = gat.analyse(records + [clone], *args)
        message = joined(injected["errors"])
        self.assertIn("DUPLICATE ID '%s'" % clone["id"], message)
        self.assertIn("publicity.json", message)
        self.assertIn(records[-1]["file"], message)

        baseline = gat.analyse(records, *args)
        self.assertNotIn("DUPLICATE ID '%s'" % clone["id"], joined(baseline["errors"]))
        self.assertEqual(len(injected["errors"]), len(baseline["errors"]) + 1)


if __name__ == "__main__":
    unittest.main()
