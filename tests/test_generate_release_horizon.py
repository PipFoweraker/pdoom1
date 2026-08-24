#!/usr/bin/env python3
"""Unit tests for tools/generate_release_horizon.py (issue #1152).

These are the PYTHON HALF of a property already pinned on the game side by
`godot/tests/unit/test_iso_week_seed.gd`. Two implementations of the same rule
now exist -- GDScript computes the seed the game posts under, Python computes
the seed the documents promise -- and a board key is an exact string, so the two
must not be allowed to drift. The boundary cases below are deliberately the SAME
cases the GDScript test pins, for exactly that reason.

Why the boundaries and not just a happy path: the naive formatting
`f"weekly-{d.year}-w{d.isocalendar()[1]}"` agrees with the correct answer on
every date the project has used so far, and then diverges permanently on Friday
2027-01-01 -- which is a scheduled release date. A test suite that only checked
2026 dates would be green and worthless.

`--self-test` covers the other half (the ladder-coupling classifier against real
git history). It needs a full clone; these tests do not, so a shallow CI
checkout cannot silently reduce this file's coverage to nothing.
"""

import json
import sys
import unittest
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import generate_release_horizon as grh  # noqa: E402


class TestIsoWeekSeed(unittest.TestCase):
    """Mirrors godot/tests/unit/test_iso_week_seed.gd, case for case."""

    def test_blessed_seeds_round_trip(self):
        # Every seed actually blessed to date, at the date it was set.
        self.assertEqual(grh.iso_week_seed(date(2026, 7, 24)), "weekly-2026-w30")
        self.assertEqual(grh.iso_week_seed(date(2026, 7, 31)), "weekly-2026-w31")
        self.assertEqual(grh.iso_week_seed(date(2026, 8, 7)), "weekly-2026-w32")
        self.assertEqual(grh.iso_week_seed(date(2026, 8, 13)), "weekly-2026-w33")
        self.assertEqual(grh.iso_week_seed(date(2026, 8, 23)), "weekly-2026-w34")

    def test_the_january_boundary_belongs_to_the_previous_iso_year(self):
        # ISO-8601: a week belongs to the year containing its Thursday.
        # 2027-01-01 is a Friday whose Thursday fell on 2026-12-31, so the whole
        # week is week 53 OF 2026.
        self.assertEqual(grh.iso_week_seed(date(2026, 12, 31)), "weekly-2026-w53")
        self.assertEqual(grh.iso_week_seed(date(2027, 1, 1)), "weekly-2026-w53")
        self.assertEqual(grh.iso_week_seed(date(2027, 1, 3)), "weekly-2026-w53")
        # The Monday after starts ISO 2027.
        self.assertEqual(grh.iso_week_seed(date(2027, 1, 4)), "weekly-2027-w01")

    def test_single_digit_weeks_are_zero_padded(self):
        # w1 and w01 are different board keys.
        self.assertEqual(grh.iso_week_seed(date(2027, 1, 8)), "weekly-2027-w01")
        self.assertEqual(grh.iso_week_seed(date(2027, 2, 5)), "weekly-2027-w05")
        self.assertTrue(grh.iso_week_seed(date(2027, 2, 5)).endswith("w05"))

    def test_leap_year_and_year_end_edges(self):
        self.assertEqual(grh.iso_week_seed(date(2028, 3, 1)), "weekly-2028-w09")
        # 2024-12-30 is a Monday in ISO week 1 of 2025 -- the mirror of the 2027
        # case, where a December date belongs to the NEXT ISO year.
        self.assertEqual(grh.iso_week_seed(date(2024, 12, 30)), "weekly-2025-w01")

    def test_weeks_advance_by_exactly_one_across_a_week_boundary(self):
        self.assertEqual(grh.iso_week_seed(date(2026, 8, 28)), "weekly-2026-w35")
        self.assertEqual(grh.iso_week_seed(date(2026, 9, 4)), "weekly-2026-w36")

    def test_the_naive_year_formatting_is_actually_wrong_here(self):
        """The bug this guard exists for, stated as a falsifiable difference.

        Without this assertion the tests above would still pass under a naive
        implementation for every 2026 date, which is how the bug survived.
        """
        trap = date(2027, 1, 1)
        naive = "weekly-%04d-w%02d" % (trap.year, trap.isocalendar()[1])
        self.assertEqual(naive, "weekly-2027-w53")  # what .year emits
        self.assertNotEqual(grh.iso_week_seed(trap), naive)
        self.assertEqual(grh.iso_week_seed(trap), "weekly-2026-w53")


class TestReleaseTrain(unittest.TestCase):
    def test_first_friday(self):
        self.assertEqual(grh.first_friday(2026, 9), date(2026, 9, 4))
        self.assertEqual(grh.first_friday(2026, 10), date(2026, 10, 2))
        self.assertEqual(grh.first_friday(2027, 1), date(2027, 1, 1))
        # A month starting ON a Friday returns the 1st, not the 8th.
        self.assertEqual(grh.first_friday(2026, 5), date(2026, 5, 1))
        # A month starting on Saturday pushes to the 7th.
        self.assertEqual(grh.first_friday(2026, 8), date(2026, 8, 7))

    def test_fridays_between_is_half_open(self):
        fridays = grh.fridays_between(date(2026, 9, 4), date(2026, 10, 2))
        self.assertEqual(
            fridays,
            [date(2026, 9, 4), date(2026, 9, 11), date(2026, 9, 18), date(2026, 9, 25)],
        )

    def test_holidays_that_can_land_on_the_train(self):
        # v0.19's scheduled date. Flagged, never silently moved.
        self.assertEqual(grh.holiday_name(date(2027, 1, 1)), "New Year's Day")
        # Good Friday is always a Friday, so it is the one movable holiday that
        # can BE a first Friday -- and in April 2026 it was.
        self.assertEqual(grh.first_friday(2026, 4), date(2026, 4, 3))
        self.assertEqual(grh.holiday_name(date(2026, 4, 3)), "Good Friday")
        self.assertIsNone(grh.holiday_name(date(2026, 9, 4)))

    def test_scheduled_rows_start_after_the_shipped_version(self):
        rows = grh.scheduled_rows()
        major, minor, _ = grh.current_version()
        self.assertTrue(rows, "the horizon must not be empty before v0.20 ships")
        self.assertEqual(rows[0]["version"], "%d.%d" % (major, minor + 1))
        self.assertEqual(rows[-1]["version"], "%d.%d" % (major, grh.FINAL_MINOR))
        for row in rows:
            self.assertEqual(date.fromisoformat(row["ships"]).weekday(), 4, row)

    def test_v019_seed_is_the_previous_iso_year(self):
        """The one row where the whole ISO-year question is load-bearing."""
        rows = {r["version"]: r for r in grh.scheduled_rows()}
        if "0.19" in rows:
            self.assertEqual(rows["0.19"]["ships"], "2027-01-01")
            self.assertEqual(rows["0.19"]["featured_seed"], "weekly-2026-w53")
            self.assertEqual(rows["0.19"]["holiday"], "New Year's Day")


class TestNoForecastLeaks(unittest.TestCase):
    """The point of #1152: nothing may pair a version with a predicted epoch."""

    def test_generated_outputs_are_current(self):
        self.assertEqual(grh.stale(), [], "run: python tools/generate_release_horizon.py")

    def test_atom_store_names_its_ruler(self):
        # Atomise protocol clause 3: no atom store without a named ruler.
        payload = json.loads(grh.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], grh.SCHEMA)
        self.assertTrue(payload["ruler"].strip())
        self.assertFalse(payload["ladder_forecastable"])
        self.assertEqual(payload["ladder_floor"], grh.ladder_floor())

    def test_the_ladder_is_only_ever_a_floor_in_generated_text(self):
        rows = grh.scheduled_rows()
        floor = grh.ladder_floor()
        blocks = [
            grh.render_markdown(rows, floor, "0.0.0"),
            grh.render_roadmap_block(rows, floor),
            grh.render_nomenclature_block(rows, floor),
        ]
        for block in blocks:
            for row in rows:
                for epoch in range(1, floor + 12):
                    forbidden = "v%s | " % row["version"]
                    line = next(
                        (ln for ln in block.splitlines() if ln.startswith("| " + forbidden)), ""
                    )
                    self.assertNotIn(
                        "L%d" % epoch,
                        line,
                        "a version row must never carry an epoch number: %r" % line,
                    )

    def test_the_published_docs_carry_no_version_to_epoch_mapping(self):
        for doc in (grh.ROADMAP, grh.NOMENCLATURE):
            text = doc.read_text(encoding="utf-8")
            start = text.find(grh.BEGIN)
            end = text.find(grh.END)
            self.assertGreater(start, -1, "%s lost its BEGIN marker" % doc.name)
            self.assertGreater(end, start, "%s lost its END marker" % doc.name)
            block = text[start:end]
            self.assertIn(grh.floor_phrase(grh.ladder_floor()), block)
            self.assertIn("NOT FORECASTABLE", block)


if __name__ == "__main__":
    unittest.main()
