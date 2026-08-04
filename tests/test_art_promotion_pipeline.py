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
import json
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

    def test_second_pass_prefix_overrides(self):
        """The 2026-08-04 recurrence batches: every prefix added in the
        second-pass fix routes where it was ruled to route."""
        cat = apply_review._px_category
        self.assertEqual(
            cat("pixellab_2026-07-26_doom_overlays/arc/branching/idle"), "doom_overlays"
        )
        self.assertEqual(
            cat("pixellab_2026-07-26_prop_grain_vanguard/native/door_scummy_native_r1"),
            "px_probes",
        )
        self.assertEqual(cat("pixellab_2026-07-26_size_probe/whatever_probe_r1"), "px_probes")
        self.assertEqual(cat("pixellab_2026-07-26_worker_rebase/worker_a/east"), "characters")
        self.assertEqual(cat("pixellab_2026-07-27_t6_worker_diagonals/w/ne"), "characters")
        self.assertEqual(
            cat("pixellab_2026-07-27_worker_round2/worker_grey_black_f/animations/e/frame_000"),
            "characters",
        )
        self.assertEqual(cat("dump_october_31_2025/hero-bg-2400w.webp"), "legacy_dump")

    def test_vignette_batch_beats_cat_fallback(self):
        """01_cat-in-the-alley contains 'cat': without the batch override the
        loose fallback filed a 1536x1024 hero vignette under cats/generated
        (latent wrong-destination, found 2026-08-04)."""
        cat = apply_review._px_category
        self.assertEqual(cat("vignettes_2026-07-28/01_cat-in-the-alley.png"), "vignettes")
        self.assertEqual(cat("vignettes_2026-07-28/05_taxi-window-rain.png"), "vignettes")

    def test_large_source_token_is_masters_hold(self):
        """prop_rebase mixes promotable native/ art with 2x large_source
        provenance in ONE batch: the token must split them."""
        cat = apply_review._px_category
        self.assertEqual(
            cat("pixellab_2026-07-27_prop_rebase/large_source/desk_decent_r1.png"), "px_masters"
        )
        self.assertEqual(cat("pixellab_2026-07-27_prop_rebase/native/door_decent_r1.png"), "props")
        self.assertIsInstance(apply_review.PX_DEST["px_masters"], apply_review.Hold)


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

    IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

    def _has_images(self, d):
        return any(f.suffix.lower() in self.IMAGE_EXTS for f in d.rglob("*") if f.is_file())

    def test_every_art_generated_batch_on_disk_is_mapped(self):
        """LIVE-TREE INVARIANT: a new art_generated/<category> dir with no
        GEN_DEST entry fails here -- the gap surfaces at commit time.

        KNOWN LIMIT (the 2026-08-04 recurrence): most of art_generated/ is
        machine-local (untracked), so on CI this test only sees the tracked
        legacy dirs and passes vacuously. The CI-real coverage lives in
        test_every_review_state_id_is_mappable below; THIS test is the local
        early-warning on the machine where new batches actually appear.
        Dirs with no image files (logs/, velocity/, ...) cannot strand a
        review and are exempt."""
        gen_root = REPO_ROOT / "art_generated"
        self.assertTrue(gen_root.is_dir(), "art_generated/ missing from repo")
        for d in sorted(p for p in gen_root.iterdir() if p.is_dir()):
            if not self._has_images(d):
                continue
            self.assertIn(
                d.name,
                apply_review.GEN_DEST,
                f"art_generated/{d.name} has no GEN_DEST mapping: add a destination "
                "or an explicit Hold(reason) in tools/art_review/apply_review.py",
            )

    def test_every_art_source_image_on_disk_is_mappable(self):
        """LIVE-TREE INVARIANT, px side (new, 2026-08-04): EVERY image file
        under art_source/ must derive a category that PX_DEST maps (str or
        Hold). Same CI limit as above -- untracked batches only exist on the
        review machine, which is exactly where this needs to fire before the
        gallery indexes them."""
        src_root = REPO_ROOT / "art_source"
        self.assertTrue(src_root.is_dir(), "art_source/ missing from repo")
        bad = {}
        for f in src_root.rglob("*"):
            if not (f.is_file() and f.suffix.lower() in self.IMAGE_EXTS):
                continue
            rel = f.relative_to(src_root).as_posix()
            if apply_review.dest_rule_for_id(f"px:{rel}") is None:
                bad.setdefault(rel.split("/")[0], []).append(rel)
        self.assertEqual(
            bad,
            {},
            "art_source batches with unmappable images (add PX_PREFIX_CATEGORY "
            "+ PX_DEST destination or Hold(reason)): "
            + "; ".join(f"{k} x{len(v)} e.g. {v[0]}" for k, v in sorted(bad.items())),
        )

    def test_every_review_state_id_is_mappable(self):
        """THE CI-VISIBLE INVARIANT (2026-08-04 structural fix): every asset
        id in the TRACKED verdict store must map to a destination or an
        explicit Hold, disk-free. art_generated/ and most of art_source/ only
        exist on Pip's machine, so the on-disk sweeps above pass vacuously on
        CI -- but review_state.json is in git, so the commit that lands a
        review pass FAILS here until the map rules on every category it
        touched. A review pass can no longer strand its own results on main."""
        state_path = REPO_ROOT / "tools" / "art_review" / "review_state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        bad = sorted(
            aid
            for aid, val in state.items()
            if isinstance(val, dict) and apply_review.dest_rule_for_id(aid) is None
        )
        self.assertEqual(
            bad,
            [],
            f"{len(bad)} review_state ids have no destination mapping "
            f"(first few: {bad[:5]}) -- add a destination or Hold(reason) in "
            "tools/art_review/apply_review.py",
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

    def test_endgame_study_series_is_held(self):
        """The eight 2026-08 endgame direction-study categories are concept
        material, not game-ready derivatives (ADR-0019): all Hold."""
        for cat in (
            "endgame_concepts",
            "endgame_concepts_gen2",
            "crisp_sweep",
            "treatment_sweep",
            "new_subjects",
            "wanasai_calls",
            "doomfield_ladder",
            "people_policy",
        ):
            self.assertIsInstance(
                apply_review._gen_dest_rel(cat, "anything"), apply_review.Hold, cat
            )

    def test_audiodump_is_held(self):
        self.assertIsInstance(apply_review.GEN_DEST["audiodump"], apply_review.Hold)

    def test_scene_art_wave2_event_files_join_shipped_event_art(self):
        """event_* must land in images/events beside the already-shipped
        event_crisis_v1.webp etc. -- images/scenes would DUPLICATE those
        bytes in the pack."""
        f = apply_review._gen_dest_rel
        self.assertEqual(f("scene_art_wave2", "event_crisis_v1"), "godot/assets/images/events")
        self.assertEqual(f("scene_art_wave2", "office_wide_day"), "godot/assets/images/scenes")
        self.assertEqual(f("scene_art_wave2", "records_vault"), "godot/assets/images/scenes")


class TestDestRuleForId(unittest.TestCase):
    """dest_rule_for_id: the disk-free mapping predicate shared by the report
    gate, the gallery preflight and the review_state sweep."""

    def test_gen_id(self):
        self.assertEqual(
            apply_review.dest_rule_for_id("gen:ui_icons:icon_x:v1"),
            "godot/assets/icons/generated",
        )

    def test_px_id_with_and_without_art_source_prefix(self):
        for aid in (
            "px:pixellab_2026-07-19/characters/worker_x/rotations/east",
            "px:art_source/pixellab_2026-07-19/characters/worker_x/rotations/east",
        ):
            self.assertEqual(
                apply_review.dest_rule_for_id(aid),
                "godot/assets/office_floor/characters",
                aid,
            )

    def test_file_id_gen_side_routes_by_category_and_stem(self):
        self.assertEqual(
            apply_review.dest_rule_for_id(
                "file:art_generated/scene_art_wave2/v1/event_board_v1.webp"
            ),
            "godot/assets/images/events",
        )
        self.assertEqual(
            apply_review.dest_rule_for_id(
                "file:art_generated/iconset_round2/v1/gen_cat_doom_8bit_v1_48.png"
            ),
            "godot/assets/icons/generated",
        )

    def test_file_id_px_side_uses_px_derivation(self):
        self.assertEqual(
            apply_review.dest_rule_for_id("file:art_source/cats_incoming/office_cat_base.png"),
            "godot/assets/cats/generated",
        )

    def test_unmapped_and_malformed_are_none(self):
        self.assertIsNone(apply_review.dest_rule_for_id("gen:no_such_category:x:v1"))
        self.assertIsNone(apply_review.dest_rule_for_id("file:art_generated/no_such_cat/v1/x.png"))
        self.assertIsNone(apply_review.dest_rule_for_id("px:mystery_batch/loose_file"))
        self.assertIsNone(apply_review.dest_rule_for_id("gen:short"))
        self.assertIsNone(apply_review.dest_rule_for_id("weird:thing"))


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


class TestFileResolver(_TmpArtRoot):
    """file:<relpath> -- the gallery's additive third id scheme, taught to
    apply_review 2026-08-04 (the 30 'unresolved-source' keeps were all this:
    webp scene art and 48/32px icons outside the gallery's gen: grammar)."""

    def test_resolves_single_file_and_keeps_name_verbatim(self):
        p = self._write("art_generated/scene_art_wave2/v1/event_crisis_v1.webp")
        a = _make_asset("file:art_generated/scene_art_wave2/v1/event_crisis_v1.webp", self.root)
        self.assertIsNone(a.error)
        self.assertEqual(a.sources, [p])
        self.assertEqual(a.promotion_status(), ("promotable", "godot/assets/images/events"))
        # verbatim: v1/v2/v4 of one base are distinct kept assets; no
        # variant-stripping collision is possible.
        self.assertEqual(a.dest_name(p), "event_crisis_v1.webp")

    def test_off_grid_size_stem_icon(self):
        p = self._write("art_generated/iconset_round2/v1/gen_seal_dod_wax_v1_32.png")
        a = _make_asset(
            "file:art_generated/iconset_round2/v1/gen_seal_dod_wax_v1_32.png", self.root
        )
        self.assertIsNone(a.error)
        self.assertEqual(a.promotion_status(), ("promotable", "godot/assets/icons/generated"))
        self.assertEqual(a.dest_name(p), "gen_seal_dod_wax_v1_32.png")

    def test_missing_file_is_blocked_unresolved(self):
        a = _make_asset("file:art_generated/scene_art_wave2/v1/ghost.webp", self.root)
        self.assertEqual(a.promotion_status()[0], "blocked-unresolved")
        self.assertIn("ghost.webp", a.error)

    def test_over_cap_file_is_blocked_size(self):
        cap = apply_review.MAX_PROMOTE_BYTES
        self._write("art_generated/scene_art_wave2/v1/office_huge.webp", size=cap + 1)
        a = _make_asset("file:art_generated/scene_art_wave2/v1/office_huge.webp", self.root)
        self.assertEqual(a.promotion_status()[0], "blocked-size")

    def test_held_category_file_is_held(self):
        self._write("art_generated/endgame_concepts/v1/study_x_v1.webp")
        a = _make_asset("file:art_generated/endgame_concepts/v1/study_x_v1.webp", self.root)
        self.assertEqual(a.promotion_status()[0], "held")

    def test_unmapped_file_names_the_batch_dir(self):
        self._write("art_generated/new_sweep_2099/v1/thing.webp")
        a = _make_asset("file:art_generated/new_sweep_2099/v1/thing.webp", self.root)
        status, detail = a.promotion_status()
        self.assertEqual(status, "blocked-unmapped")
        self.assertIn("art_generated/new_sweep_2099", detail)
        self.assertIn("GEN_DEST", detail)


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

    def test_both_variants_kept_ship_at_distinct_paths(self):
        """Pip ruled 2026-08-03: "Keep both, you pick naming variant."

        The guarantee under test is UNCHANGED from when this asserted a contested
        failure -- NO SILENT OVERWRITE. What changed is the resolution: instead of
        refusing, the highest variant claims the plain name and earlier ones carry
        their marker, so both ship at distinct paths.
        """
        self._write("art_generated/ui_icons/v1/icon_z_v1_512.png")
        self._write("art_generated/ui_icons/v1/icon_z_v2_512.png")
        a1 = _make_asset("gen:ui_icons:icon_z:v1", self.root)
        a2 = _make_asset("gen:ui_icons:icon_z:v2", self.root)
        buckets, n_blocked, contested = apply_review._promotion_gate([a1, a2])
        self.assertEqual(contested, {}, "variant collision must resolve, not block")
        self.assertEqual(len(buckets["promotable"]), 2, "both variants ship")
        self.assertEqual(len(buckets["contested"]), 0)

        dests = set()
        for a in (a1, a2):
            for src in a.promote_sources():
                dests.add(a.dest_dir() / a.dest_name(src, a.keep_variant_in_name))
        self.assertEqual(len(dests), 2, "distinct destinations -- nothing overwrites")
        names = sorted(d.name for d in dests)
        # HIGHEST variant takes the plain name the game already references.
        self.assertEqual(names, ["icon_z_512.png", "icon_z_v1_512.png"])

    def test_implicit_v1_gets_its_marker_inserted(self):
        """v1 files carry NO _v1_ marker (icon_y_512.png), so "keep the marker" is
        a no-op for them and the collision would survive. The loser must have the
        marker INSERTED before the size token. This is the bug that made the first
        implementation of Pip's ruling silently ineffective."""
        self._write("art_generated/ui_icons/v1/icon_y_512.png")  # v1, no marker
        self._write("art_generated/ui_icons/v1/icon_y_v2_512.png")
        a1 = _make_asset("gen:ui_icons:icon_y:v1", self.root)
        a2 = _make_asset("gen:ui_icons:icon_y:v2", self.root)
        buckets, _n, contested = apply_review._promotion_gate([a1, a2])
        self.assertEqual(contested, {})
        names = sorted(
            a.dest_name(src, a.keep_variant_in_name)
            for a in (a1, a2)
            for src in a.promote_sources()
        )
        self.assertEqual(names, ["icon_y_512.png", "icon_y_v1_512.png"])

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
