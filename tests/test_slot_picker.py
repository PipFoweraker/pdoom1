"""Tests for the slot picker (tools/art_review/slot_model.py + apply_slot_picks.py).

The picker RECORDS decisions; a later mechanical lane applies them. So the
invariants worth guarding are not "did the right file move" but:

  1. the cluster model is stable and derived from ONE definition (a pick
     recorded against cluster X must not silently land on cluster Y after a
     regeneration -- hence build + merge share slot_model);
  2. selection never becomes a verdict (review_state.json is read-only input,
     and no new verdict value is ever invented -- the analysis's rejected
     option (a));
  3. a pick that no longer resolves is REPORTED, not written (the
     silent-wrongness family: every failure in review week looked right).
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLDIR = REPO_ROOT / "tools" / "art_review"
if str(TOOLDIR) not in sys.path:
    sys.path.insert(0, str(TOOLDIR))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLDIR / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


slot_model = _load("slot_model")
apply_slot_picks = _load("apply_slot_picks")

# art_generated/ and the >1MB masters are gitignored, so the art exists in
# Pip's main checkout and in NOTHING else -- not a fresh worktree, not CI. The
# live-tree classes below resolve real files, so they SKIP where the art is
# absent rather than reporting a red that only means "you are in a worktree".
# The pure-logic classes always run. (Worktree file-locality trap, 2026-07-25.)
#
# The probe is "do all 15 frame roles resolve", not "does the directory
# exist". art_source/ IS tracked, so a worktree resolves ~670 pixellab files
# and would pass any looser check while every gpt-generated cluster and all 15
# frame roles are missing -- a red that only means "you are in a worktree".
try:
    _MODEL = slot_model.build_model()
except SystemExit:  # no review_state.json at all
    _MODEL = None
HAS_ART = bool(_MODEL) and len(_MODEL[1]) == len(slot_model.FRAME_ROLE_STEMS)
NEEDS_ART = unittest.skipUnless(
    HAS_ART, "full art library not present (art_generated/ is gitignored; CI/worktree)"
)


class TestRoleStem(unittest.TestCase):
    """The clustering heuristic, pinned so a refactor cannot quietly re-group
    slots under existing picks."""

    def test_strips_variant_and_size(self):
        self.assertEqual(slot_model.role_stem("icon_audit_safety_v3_512.png"), "icon_audit_safety")
        self.assertEqual(slot_model.role_stem("icon_audit_safety_512.png"), "icon_audit_safety")

    def test_strips_batch_date(self):
        self.assertEqual(slot_model.role_stem("walk_east_0_20260719.png"), "walk_east_0")

    def test_v12_beats_v2(self):
        self.assertGreater(
            slot_model.variant_rank("x_v12_512.png"), slot_model.variant_rank("x_v2_512.png")
        )

    def test_every_frame_role_has_a_crop(self):
        # A missing entry silently falls back to the whole 512px picture -- which
        # is exactly the "you showed me the glowing arrow, not the corner" bug.
        for stem in slot_model.FRAME_ROLE_STEMS:
            self.assertIn(stem, slot_model.FRAME_CROPS, stem)

    def test_crops_are_inside_the_image(self):
        for stem, (x, y, w, h) in slot_model.FRAME_CROPS.items():
            self.assertGreater(w, 0, stem)
            self.assertGreater(h, 0, stem)
            self.assertLessEqual(x + w, 1.0001, stem)
            self.assertLessEqual(y + h, 1.0001, stem)

    def test_only_the_bezels_claim_the_whole_image(self):
        whole = {s for s, c in slot_model.FRAME_CROPS.items() if c[2] >= 1 and c[3] >= 1}
        self.assertEqual(whole, {s for s in slot_model.FRAME_ROLE_STEMS if s.startswith("crt_")})

    def test_implicit_v1_label(self):
        # v1 files carry no _v1_ marker at all in this naming convention; the
        # batch shortcut has to know that or "all v1" silently matches nothing.
        self.assertEqual(slot_model.variant_label("button_hire_hover_512.png"), "v1*")
        self.assertEqual(slot_model.variant_label("button_hire_hover_v3_512.png"), "v3")


@NEEDS_ART
class TestModel(unittest.TestCase):
    """Live-tree invariants. These read the real review_state.json, read-only."""

    @classmethod
    def setUpClass(cls):
        cls.clusters, cls.frames, cls.stats = _MODEL

    def test_frame_roles_are_the_fifteen(self):
        self.assertEqual(len(self.frames), len(slot_model.FRAME_ROLE_STEMS))
        self.assertEqual({f.stem for f in self.frames}, set(slot_model.FRAME_ROLE_STEMS))

    def test_every_cluster_is_actually_contested(self):
        for cl in self.clusters:
            self.assertGreater(len(cl.candidates), 1, cl.slot_id)

    def test_pools_never_enter_the_picker(self):
        # A pool has no single winner (ADR-0019 pt 3), so it has no slot to pick.
        for cl in self.clusters:
            self.assertFalse(slot_model.is_pool(cl.dest), cl.slot_id)

    def test_slot_ids_are_unique(self):
        ids = [cl.slot_id for cl in self.clusters]
        self.assertEqual(len(ids), len(set(ids)))

    def test_draw_size_is_cited_not_guessed(self):
        for cl in self.clusters:
            self.assertTrue(cl.draw_why, cl.slot_id)

    def test_square_only_where_the_consumer_pins_both_dimensions(self):
        # Getting this wrong squashes 768x512 hero art into a square preview,
        # which makes the preview lie about what the game draws.
        for cl in self.clusters:
            if cl.dest == "godot/assets/icons/generated":
                self.assertTrue(cl.draw_square, cl.slot_id)
            else:
                self.assertFalse(cl.draw_square, cl.slot_id)

    def test_nothing_shrinks_below_native_claim(self):
        # draw_px 0 means "already at or below the drawn size"; any positive
        # number must come from DRAW_RULES, never from a default.
        for cl in self.clusters:
            if cl.draw_px:
                self.assertIn(cl.dest, slot_model.DRAW_RULES)


@NEEDS_ART
class TestValidation(unittest.TestCase):
    """A pick that no longer resolves must be loud."""

    @classmethod
    def setUpClass(cls):
        cls.idx, cls.stats = apply_slot_picks.index_model()
        cls.slot_key = next(k for k in cls.idx if k.startswith("slot:"))
        cls.frame_key = next(k for k in cls.idx if k.startswith("frame:"))

    def test_good_pick_validates(self):
        rel = next(iter(self.idx[self.slot_key]["cands"]))
        ok, why = apply_slot_picks.validate(
            self.slot_key, {"src": rel, "status": "chosen"}, self.idx
        )
        self.assertTrue(ok, why)

    def test_unknown_slot_rejected(self):
        ok, _ = apply_slot_picks.validate(
            "slot:godot/assets/icons/generated/nope", {"src": "", "status": "chosen"}, self.idx
        )
        self.assertFalse(ok)

    def test_file_from_another_slot_rejected(self):
        other = next(k for k in self.idx if k.startswith("slot:") and k != self.slot_key)
        rel = next(iter(self.idx[other]["cands"]))
        ok, _ = apply_slot_picks.validate(self.slot_key, {"src": rel, "status": "chosen"}, self.idx)
        self.assertFalse(ok)

    def test_chosen_slot_without_source_rejected(self):
        ok, _ = apply_slot_picks.validate(self.slot_key, {"src": "", "status": "chosen"}, self.idx)
        self.assertFalse(ok)

    def test_frame_needs_a_known_treatment(self):
        ok, _ = apply_slot_picks.validate(
            self.frame_key, {"src": "", "status": "chosen", "treatment": "vibes"}, self.idx
        )
        self.assertFalse(ok)

    def test_nineslice_needs_a_source_master(self):
        ok, _ = apply_slot_picks.validate(
            self.frame_key, {"src": "", "status": "chosen", "treatment": "nineslice"}, self.idx
        )
        self.assertFalse(ok)

    def test_styleboxflat_needs_no_source(self):
        # Geometry replaces the texture entirely, so there is no master to name.
        ok, why = apply_slot_picks.validate(
            self.frame_key, {"src": "", "status": "chosen", "treatment": "styleboxflat"}, self.idx
        )
        self.assertTrue(ok, why)


@NEEDS_ART
class TestMerge(unittest.TestCase):
    def setUp(self):
        self.idx, self.stats = apply_slot_picks.index_model()
        self.key = next(k for k in self.idx if k.startswith("slot:"))
        self.rel = next(iter(self.idx[self.key]["cands"]))
        self.data = {"slots": {}, "frame_roles": {}}

    def _entry(self, **kw):
        base = {
            "src": self.rel,
            "status": "chosen",
            "note": "",
            "updated_at": "2026-08-06T00:00:00Z",
        }
        base.update(kw)
        return base

    def test_note_survives_the_round_trip(self):
        # Pip's question, verbatim: "if I add notes with n and then keep it, do
        # you get the notes?" The answer must be yes.
        apply_slot_picks.merge({self.key: self._entry(note="the warm one")}, self.data, self.idx)
        rid = self.key.split(":", 1)[1]
        self.assertEqual(self.data["slots"][rid]["note"], "the warm one")

    def test_pick_records_the_pairing_not_a_verdict(self):
        apply_slot_picks.merge({self.key: self._entry()}, self.data, self.idx)
        rec = self.data["slots"][self.key.split(":", 1)[1]]
        self.assertNotIn("verdict", rec)
        self.assertTrue(rec["source_asset"])
        self.assertTrue(rec["destination"])

    def test_clearing_a_pick_removes_the_entry(self):
        # "good but not chosen" is the ABSENCE of a record, never a stored
        # label -- and reopening a decision must be possible.
        apply_slot_picks.merge({self.key: self._entry()}, self.data, self.idx)
        apply_slot_picks.merge(
            {self.key: self._entry(src="", status="", updated_at="2026-08-06T01:00:00Z")},
            self.data,
            self.idx,
        )
        self.assertEqual(self.data["slots"], {})

    def test_older_export_does_not_clobber(self):
        apply_slot_picks.merge(
            {self.key: self._entry(note="new", updated_at="2026-08-06T02:00:00Z")},
            self.data,
            self.idx,
        )
        apply_slot_picks.merge(
            {self.key: self._entry(note="stale", updated_at="2026-08-05T00:00:00Z")},
            self.data,
            self.idx,
        )
        self.assertEqual(self.data["slots"][self.key.split(":", 1)[1]]["note"], "new")

    def test_rejected_pick_is_not_written(self):
        _a, _u, _un, _o, rejected, _c = apply_slot_picks.merge(
            {"slot:godot/assets/icons/generated/nope": self._entry(src="")}, self.data, self.idx
        )
        self.assertEqual(rejected, 1)
        self.assertEqual(self.data["slots"], {})


@NEEDS_ART
class TestReviewStateUntouched(unittest.TestCase):
    def test_state_file_is_never_written(self):
        """The 2,713 verdicts are read-only input. Byte-compare before/after a
        full model build + merge."""
        state = REPO_ROOT / "tools" / "art_review" / "review_state.json"
        before = state.read_bytes()
        idx, _stats = apply_slot_picks.index_model()
        key = next(k for k in idx if k.startswith("slot:"))
        rel = next(iter(idx[key]["cands"]))
        data = {"slots": {}, "frame_roles": {}}
        apply_slot_picks.merge(
            {
                key: {
                    "src": rel,
                    "status": "chosen",
                    "note": "x",
                    "updated_at": "2026-08-06T00:00:00Z",
                }
            },
            data,
            idx,
        )
        self.assertEqual(state.read_bytes(), before)


class TestRecordFileIsTracked(unittest.TestCase):
    def test_record_is_valid_json_with_both_buckets(self):
        rec = REPO_ROOT / "tools" / "assets" / "demand" / "slot_picks.json"
        self.assertTrue(rec.is_file(), "the selection record must exist and be tracked in git")
        data = json.loads(rec.read_text(encoding="utf-8"))
        self.assertIn("slots", data)
        self.assertIn("frame_roles", data)

    def test_record_is_ascii(self):
        rec = REPO_ROOT / "tools" / "assets" / "demand" / "slot_picks.json"
        rec.read_text(encoding="utf-8").encode("ascii")


if __name__ == "__main__":
    unittest.main()
