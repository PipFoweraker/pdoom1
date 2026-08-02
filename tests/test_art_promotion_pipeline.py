"""Tests for tools/art_review/apply_review.py -- destination map + resolver.

Guards the promotion gate against the silent-wrongness failure family
(issues #1027 / #1075 / #1093): an approved (keep) asset must either be
promotable, or explicitly held, or FAIL LOUDLY -- never silently skipped.

Pure logic: temp-dir fixtures for the resolver, live-tree invariants for the
maps (a new art_generated/<category> batch with no destination mapping fails
here at commit time, not at promote time).
"""

import importlib.util
import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "tools" / "art_review" / "apply_review.py"

_spec = importlib.util.spec_from_file_location("apply_review", MODULE_PATH)
apply_review = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(apply_review)


def _make_asset(asset_id, art_root, verdict="keep"):
    return apply_review.Asset(asset_id, verdict, "", [], Path(art_root))


class TestPxCategory(unittest.TestCase):
    """_px_category: batch-dir overrides beat tokens beat the 'cat' fallback."""

    def test_prefix_overrides(self):
        cat = apply_review._px_category
        self.assertEqual(cat("icon_hires/main_navigation/icon_menu_512"), "icon_hires")
        # gen_cat_doom contains 'cat' but the batch dir pins it to icons.
        self.assertEqual(cat("iconset_2026-07-21/gen_cat_doom_128"), "icons")
        self.assertEqual(cat("settings_bg_2026-07-21/gen_bg_warm_ochre_512"), "backgrounds")
        self.assertEqual(cat("cats_incoming/office_cat_base"), "cats")

    def test_prop_family_tokens(self):
        cat = apply_review._px_category
        for seg in ("props", "objects", "chairs", "kitchen", "windows", "environment"):
            self.assertEqual(cat(f"pixellab_2026-07-21-rerolls/{seg}/thing_1"), "props", seg)

    def test_character_family_tokens(self):
        cat = apply_review._px_category
        self.assertEqual(
            cat("pixellab_2026-07-19/characters/worker_x/rotations/east"), "characters"
        )
        self.assertEqual(cat("pixellab_2026-07-21-rerolls/founder/founder_back_1"), "characters")
        self.assertEqual(cat("pixellab_2026-07-21-rerolls/cosmetics/hat_medium_1"), "characters")

    def test_tilesets_cats_icons(self):
        cat = apply_review._px_category
        self.assertEqual(cat("pixellab_2026-07-19/tilesets/floor_1"), "tilesets")
        self.assertEqual(cat("pixellab_2026-07-21-rerolls/cats/cat_purple_1"), "cats")
        self.assertEqual(cat("pixellab_2026-07-17/reroll/icons/icon_1"), "icons")

    def test_cat_fallback_and_batch_default(self):
        cat = apply_review._px_category
        self.assertEqual(cat("pixellab_2026-07-16/cat_walk_cat1/walk_east_0"), "cats")
        # loose files at the 2026-07-16 batch root are character style probes.
        self.assertEqual(cat("pixellab_2026-07-16/18-Hat-tall"), "characters")

    def test_unknown_is_none(self):
        self.assertIsNone(apply_review._px_category("mystery_batch/loose_file"))


class TestDestMaps(unittest.TestCase):
    """Map invariants -- these are what make regressions loud."""

    def test_every_destination_is_under_godot_assets(self):
        for cat, rule in {**apply_review.GEN_DEST, **apply_review.PX_DEST}.items():
            if isinstance(rule, apply_review.Hold):
                self.assertTrue(rule.reason, f"{cat}: Hold must carry a reason")
                continue
            dests = [rule] if isinstance(rule, str) else [d for _, d in rule]
            for d in dests:
                self.assertTrue(
                    d.startswith("godot/assets/"), f"{cat}: {d} not under godot/assets/"
                )

    def test_every_art_generated_batch_on_disk_is_mapped(self):
        """LIVE-TREE INVARIANT: a new art_generated/<category> dir with no
        GEN_DEST entry fails here -- the gap surfaces at commit time."""
        gen_root = REPO_ROOT / "art_generated"
        self.assertTrue(gen_root.is_dir(), "art_generated/ missing from repo")
        for d in sorted(p for p in gen_root.iterdir() if p.is_dir()):
            self.assertIn(
                d.name,
                apply_review.GEN_DEST,
                f"art_generated/{d.name} has no GEN_DEST mapping: add a destination "
                "or an explicit Hold(reason) in tools/art_review/apply_review.py",
            )

    def test_px_dest_categories_cover_all_tokens(self):
        for token, cat in apply_review.PX_TOKEN_CATEGORY.items():
            self.assertIn(cat, apply_review.PX_DEST, f"token {token} -> unmapped {cat}")
        for prefix, cat in apply_review.PX_PREFIX_CATEGORY.items():
            self.assertIn(cat, apply_review.PX_DEST, f"prefix {prefix} -> unmapped {cat}")
        for batch, cat in apply_review.PX_BATCH_DEFAULT_CATEGORY.items():
            self.assertIn(cat, apply_review.PX_DEST, f"batch {batch} -> unmapped {cat}")

    def test_icon_hires_is_explicitly_held(self):
        """icon_hires is the issue #787 bloat class: promoting it must be an
        explicit ruling, never a default."""
        self.assertIsInstance(apply_review.PX_DEST["icon_hires"], apply_review.Hold)

    def test_tilesets_destination_exists_in_game_tree(self):
        """Guards the office_floor/tiles -> office_floor/tilesets fix: the
        destination must be a dir the game actually uses."""
        rel = apply_review.PX_DEST["tilesets"]
        self.assertEqual(rel, "godot/assets/office_floor/tilesets")
        self.assertTrue((REPO_ROOT / rel).is_dir(), f"{rel} does not exist")


class TestGenDestRel(unittest.TestCase):
    def test_round3_rerolls_split_routing(self):
        f = apply_review._gen_dest_rel
        self.assertEqual(
            f("round3_rerolls", "dossier_fresh_grad_a"), "godot/assets/portraits/generated"
        )
        self.assertEqual(
            f("round3_rerolls", "painterly_fresh_grad_a"), "godot/assets/portraits/generated"
        )
        self.assertEqual(f("round3_rerolls", "acquire_startup_r3"), "godot/assets/icons/generated")

    def test_unknown_category_is_none(self):
        self.assertIsNone(apply_review._gen_dest_rel("no_such_category", "x"))

    def test_plain_categories_pass_through(self):
        self.assertEqual(
            apply_review._gen_dest_rel("ui_icons", "anything"), "godot/assets/icons/generated"
        )


class _TmpArtRoot(unittest.TestCase):
    """Fixture: a throwaway art root with art_source/ + art_generated/."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="art_review_test_"))
        self.addCleanup(shutil.rmtree, self.root, True)

    def _write(self, rel, size=16):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as fh:
            fh.write(b"\x89PNG")
            fh.seek(size - 1)
            fh.write(b"\x00")
        return p


class TestPxResolver(_TmpArtRoot):
    def test_exact_file_relpath(self):
        self._write("art_source/batch/props/desk_1.png")
        a = _make_asset("px:batch/props/desk_1.png", self.root)
        self.assertIsNone(a.error)
        self.assertEqual(len(a.sources), 1)

    def test_extensionless_relpath_resolves_to_png(self):
        """The review app writes single-PNG relpaths WITHOUT .png -- the 550
        'no file/dir at ...' skips of 2026-07/08 were exactly this."""
        self._write("art_source/batch/props/desk_1.png")
        a = _make_asset("px:batch/props/desk_1", self.root)
        self.assertIsNone(a.error)
        self.assertEqual(a.sources[0].name, "desk_1.png")

    def test_rotation_dir_relpath(self):
        self._write("art_source/batch/characters/worker/rotations/east.png")
        self._write("art_source/batch/characters/worker/rotations/west.png")
        a = _make_asset("px:batch/characters/worker/rotations", self.root)
        self.assertIsNone(a.error)
        self.assertEqual([s.name for s in a.sources], ["east.png", "west.png"])

    def test_art_root_relative_form(self):
        self._write("art_source/batch/props/desk_1.png")
        a = _make_asset("px:art_source/batch/props/desk_1", self.root)
        self.assertIsNone(a.error)

    def test_missing_reports_every_candidate(self):
        a = _make_asset("px:batch/props/ghost", self.root)
        self.assertIsNotNone(a.error)
        # precise failure: all four tried paths are named, no guessing.
        self.assertEqual(a.error.count("ghost"), 4)
        self.assertIn("ghost.png", a.error)

    def test_px_dest_name_preserves_identity_subdirs(self):
        """cat1/walk_east_0 and cat2/walk_east_0 are DIFFERENT assets -- the
        destination must keep the distinguishing sub-path."""
        p1 = self._write("art_source/pixellab_2026-07-16/cat_walk_cat1/walk_east_0.png")
        p2 = self._write("art_source/pixellab_2026-07-16/cat_walk_cat2/walk_east_0.png")
        a1 = _make_asset("px:pixellab_2026-07-16/cat_walk_cat1/walk_east_0", self.root)
        a2 = _make_asset("px:pixellab_2026-07-16/cat_walk_cat2/walk_east_0", self.root)
        self.assertEqual(a1.dest_name(p1), "cat_walk_cat1/walk_east_0.png")
        self.assertEqual(a2.dest_name(p2), "cat_walk_cat2/walk_east_0.png")

    def test_px_dest_name_strips_category_token_not_structure(self):
        p = self._write("art_source/pixellab_2026-07-19/characters/worker_x/rotations/east.png")
        a = _make_asset("px:pixellab_2026-07-19/characters/worker_x/rotations/east", self.root)
        # 'characters' (the category token) is dropped; worker identity kept.
        self.assertEqual(a.dest_name(p), "worker_x/rotations/east.png")


class TestGenSizeCap(_TmpArtRoot):
    def test_picks_largest_size_under_the_git_cap(self):
        cap = apply_review.MAX_PROMOTE_BYTES
        self._write("art_generated/ui_icons/v1/icon_x_v1_64.png", size=1024)
        self._write("art_generated/ui_icons/v1/icon_x_v1_512.png", size=2048)
        self._write("art_generated/ui_icons/v1/icon_x_v1_1024.png", size=cap + 1)
        a = _make_asset("gen:ui_icons:icon_x:v1", self.root)
        self.assertIsNone(a.error)
        self.assertEqual(a.promote_file.name, "icon_x_v1_512.png")
        self.assertEqual(a.best_file.name, "icon_x_v1_1024.png")
        self.assertTrue(a.size_capped)
        self.assertEqual(a.promotion_status()[0], "promotable")

    def test_nothing_under_cap_is_blocked_not_silent(self):
        cap = apply_review.MAX_PROMOTE_BYTES
        self._write("art_generated/ui_icons/v1/icon_y_v1_1024.png", size=cap + 1)
        a = _make_asset("gen:ui_icons:icon_y:v1", self.root)
        self.assertEqual(a.promotion_status()[0], "blocked-size")


class TestPromotionGate(_TmpArtRoot):
    def test_unmapped_category_is_blocked_and_report_fails(self):
        self._write("art_generated/new_batch_2099/v1/thing_v1_512.png")
        a = _make_asset("gen:new_batch_2099:thing:v1", self.root)
        self.assertEqual(a.promotion_status()[0], "blocked-unmapped")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = apply_review.action_report([a])
        self.assertEqual(rc, 1, "report must exit nonzero when a keep is blocked")
        self.assertIn("[FAIL]", buf.getvalue())

    def test_unresolved_source_is_blocked(self):
        a = _make_asset("px:batch/props/missing_thing", self.root)
        self.assertEqual(a.promotion_status()[0], "blocked-unresolved")

    def test_held_does_not_fail_the_gate(self):
        self._write("art_source/icon_hires/guide/icon_help_512.png")
        a = _make_asset("px:icon_hires/guide/icon_help_512", self.root)
        self.assertEqual(a.promotion_status()[0], "held")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = apply_review.action_report([a])
        self.assertEqual(rc, 0, "explicit Hold is a legitimate outcome, not a failure")

    def test_both_variants_kept_is_contested_not_overwritten(self):
        """v1 and v2 collapse onto one game filename (variant marker is
        stripped) -- promoting both would let the last copy silently win."""
        self._write("art_generated/ui_icons/v1/icon_z_v1_512.png")
        self._write("art_generated/ui_icons/v1/icon_z_v2_512.png")
        a1 = _make_asset("gen:ui_icons:icon_z:v1", self.root)
        a2 = _make_asset("gen:ui_icons:icon_z:v2", self.root)
        buckets, n_blocked, contested = apply_review._promotion_gate([a1, a2])
        self.assertEqual(len(buckets["contested"]), 2)
        self.assertEqual(len(buckets["promotable"]), 0)
        self.assertEqual(len(contested), 1)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = apply_review.action_report([a1, a2])
        self.assertEqual(rc, 1)

    def test_clean_keep_promotes_and_dry_run_reports_bytes(self):
        self._write("art_generated/ui_icons/v1/icon_ok_v1_512.png", size=4096)
        a = _make_asset("gen:ui_icons:icon_ok:v1", self.root)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = apply_review.action_promote([a], dry_run=True)
        out = buf.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("would copy 1 file(s)", out)
        self.assertIn("icon_ok_512.png", out)  # variant marker stripped
        # dry-run must not create anything.
        self.assertFalse((self.root / "godot").exists())


if __name__ == "__main__":
    unittest.main()
