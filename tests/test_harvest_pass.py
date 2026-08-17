#!/usr/bin/env python3
"""Unit tests for the harvest second pass (tools/art_review/serve_review.py).

WHAT IS BEING PROTECTED

The harvest axis went unused for months -- 2 tags across 7,944 judged assets --
because the tool asked for the tag in the same form as the verdict, so harvesting
competed with sweeping and lost. The second pass is the fix. Two properties make
it work, and both are easy to break by accident:

1. ADDITIVE TAGS. Batch-tagging 40 discards `flaw:blurry` must not wipe the
   `element:corner` someone put on one of them last week. `tags` REPLACES (right
   for a single-asset edit); `add_tags` UNIONS. If someone "simplifies" the two
   into one path, the batch case silently destroys prior harvest work -- the
   damage is invisible because the result is still a valid tag list.

2. THE VERDICT IS NEVER TOUCHED. Harvest decides what survives a fate, not the
   fate. A patch that carries only tags must leave the verdict, note and
   shelf_reason exactly as they were.

Also pinned: every harvest pass declares a QUESTION. That is not decoration --
from the 2026-08-14 session audio, the reviewer's own reason for wanting a second
pass was "without instructions, I'm not sure where my limited attention is going
to be best spent". A pass whose question went missing would technically function
and would reproduce the problem it was built to solve.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "art_review"))

import serve_review as sr  # noqa: E402


class HarvestTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self._saved = (sr.STATE_PATH, sr.LOG_PATH)
        sr.STATE_PATH = root / "review_state.json"
        sr.LOG_PATH = root / "review_log.jsonl"

    def tearDown(self):
        sr.STATE_PATH, sr.LOG_PATH = self._saved
        self.tmp.cleanup()

    def state(self):
        if not sr.STATE_PATH.exists():
            return {}
        return json.loads(sr.STATE_PATH.read_text(encoding="utf-8"))

    def entry(self, asset_id):
        return self.state().get(asset_id, {})

    def events(self):
        if not sr.LOG_PATH.exists():
            return []
        return [
            json.loads(x) for x in sr.LOG_PATH.read_text(encoding="utf-8").splitlines() if x.strip()
        ]


class TestAdditiveTags(HarvestTestBase):
    def test_add_tags_unions_and_preserves_existing(self):
        sr.apply_patch({"asset_id": "a", "verdict": "discard", "tags": ["element:corner"]})
        sr.apply_patch({"asset_id": "a", "add_tags": ["flaw:blurry"]})
        self.assertEqual(self.entry("a")["tags"], ["element:corner", "flaw:blurry"])

    def test_add_tags_is_idempotent(self):
        sr.apply_patch({"asset_id": "a", "verdict": "discard", "add_tags": ["flaw:blurry"]})
        sr.apply_patch({"asset_id": "a", "add_tags": ["flaw:blurry"]})
        sr.apply_patch({"asset_id": "a", "add_tags": ["flaw:blurry", "flaw:scale"]})
        self.assertEqual(self.entry("a")["tags"], ["flaw:blurry", "flaw:scale"])

    def test_remove_tags_drops_only_named(self):
        sr.apply_patch(
            {
                "asset_id": "a",
                "verdict": "keep",
                "tags": ["element:corner", "flaw:scale", "palette"],
            }
        )
        sr.apply_patch({"asset_id": "a", "remove_tags": ["flaw:scale"]})
        self.assertEqual(self.entry("a")["tags"], ["element:corner", "palette"])

    def test_remove_tags_ignores_absent(self):
        sr.apply_patch({"asset_id": "a", "verdict": "keep", "tags": ["palette"]})
        sr.apply_patch({"asset_id": "a", "remove_tags": ["flaw:nope"]})
        self.assertEqual(self.entry("a")["tags"], ["palette"])

    def test_tags_still_REPLACES_for_single_asset_edits(self):
        """The old behaviour must survive -- the note field on a cell depends on it."""
        sr.apply_patch({"asset_id": "a", "verdict": "keep", "tags": ["element:lamp"]})
        sr.apply_patch({"asset_id": "a", "tags": ["flaw:shiny"]})
        self.assertEqual(self.entry("a")["tags"], ["flaw:shiny"])

    def test_add_tags_normalises_whitespace_and_blanks(self):
        sr.apply_patch({"asset_id": "a", "verdict": "discard", "add_tags": ["  flaw:grain  ", ""]})
        self.assertEqual(self.entry("a")["tags"], ["flaw:grain"])

    def test_add_tags_accepts_a_comma_string(self):
        sr.apply_patch({"asset_id": "a", "verdict": "discard", "add_tags": "flaw:a, flaw:b"})
        self.assertEqual(self.entry("a")["tags"], ["flaw:a", "flaw:b"])


class TestHarvestNeverTouchesTheVerdict(HarvestTestBase):
    def test_tagging_leaves_verdict_note_and_reason_intact(self):
        sr.apply_patch(
            {
                "asset_id": "a",
                "verdict": "shelf",
                "shelf_reason": "when a night-scene brief exists",
                "note": "keep the lamp",
            }
        )
        before = dict(self.entry("a"))
        sr.apply_patch({"asset_id": "a", "add_tags": ["element:lamp"]})
        after = self.entry("a")
        self.assertEqual(after["verdict"], before["verdict"])
        self.assertEqual(after["note"], before["note"])
        self.assertEqual(after["shelf_reason"], before["shelf_reason"])
        self.assertIn("element:lamp", after["tags"])

    def test_tag_only_patch_on_an_undecided_asset_creates_no_verdict(self):
        sr.apply_patch({"asset_id": "a", "add_tags": ["seed:new-scene"]})
        self.assertIsNone(self.entry("a").get("verdict"))
        self.assertEqual(self.entry("a")["tags"], ["seed:new-scene"])

    def test_a_tag_alone_is_enough_signal_to_keep_the_entry(self):
        """A harvest tag on a discarded-then-cleared asset must not vanish."""
        sr.apply_patch({"asset_id": "a", "add_tags": ["element:corner"]})
        self.assertIn("a", self.state())


class TestHarvestIsLogged(HarvestTestBase):
    def test_each_tag_application_appends_one_event(self):
        sr.apply_patch({"asset_id": "a", "verdict": "discard"})
        n = len(self.events())
        sr.apply_patch({"asset_id": "a", "add_tags": ["flaw:blurry"]})
        self.assertEqual(len(self.events()), n + 1)
        last = self.events()[-1]
        self.assertEqual(last["next"]["tags"], ["flaw:blurry"])
        self.assertEqual(last["prev"]["tags"], [])
        self.assertEqual(last["next"]["verdict"], "discard")

    def test_a_no_op_add_logs_nothing(self):
        sr.apply_patch({"asset_id": "a", "verdict": "discard", "add_tags": ["flaw:blurry"]})
        n = len(self.events())
        sr.apply_patch({"asset_id": "a", "add_tags": ["flaw:blurry"]})
        self.assertEqual(len(self.events()), n, "re-applying the same tag must not log")


class TestTagsInUse(HarvestTestBase):
    def test_counts_tags_across_assets(self):
        sr.apply_patch({"asset_id": "a", "verdict": "discard", "add_tags": ["flaw:blurry"]})
        sr.apply_patch({"asset_id": "b", "verdict": "discard", "add_tags": ["flaw:blurry"]})
        sr.apply_patch({"asset_id": "c", "verdict": "keep", "add_tags": ["element:corner"]})
        counts = sr.harvest_tags_in_use(self.state())
        self.assertEqual(counts["flaw:blurry"], 2)
        self.assertEqual(counts["element:corner"], 1)

    def test_empty_state_is_empty_not_an_error(self):
        self.assertEqual(sr.harvest_tags_in_use({}), {})


class TestPassDefinitions(unittest.TestCase):
    """The passes are the feature. A pass without a question is the old failure."""

    def test_every_pass_states_a_question_and_an_instruction(self):
        self.assertTrue(sr.HARVEST_PASSES, "there must be at least one pass")
        for p in sr.HARVEST_PASSES:
            self.assertTrue(p.get("question", "").strip(), f"{p['key']} has no question")
            self.assertTrue(p.get("instruction", "").strip(), f"{p['key']} has no instruction")
            self.assertTrue(p["question"].strip().endswith("?"), f"{p['key']} is not a question")

    def test_every_pass_has_a_filter_and_a_non_empty_palette(self):
        for p in sr.HARVEST_PASSES:
            self.assertIn(p.get("filter"), {"discard", "keep", "remix", "shelf", "decided"})
            self.assertTrue(p.get("palette"), f"{p['key']} has an empty palette")

    def test_pass_keys_are_unique(self):
        keys = [p["key"] for p in sr.HARVEST_PASSES]
        self.assertEqual(len(keys), len(set(keys)))

    def test_prefixed_palettes_are_bare_terms(self):
        """Palette entries get the prefix applied in the UI; pre-prefixing double-stacks."""
        for p in sr.HARVEST_PASSES:
            if not p["prefix"]:
                continue
            for term in p["palette"]:
                self.assertNotIn(":", term, f"{p['key']}: {term!r} must not carry a prefix")

    def test_the_discard_passes_exist(self):
        """A discard is where harvest MATTERS -- the image dies, the lesson should not."""
        filters = {p["filter"] for p in sr.HARVEST_PASSES}
        self.assertIn("discard", filters)

    def test_flaw_and_element_are_both_reachable(self):
        prefixes = {p["prefix"] for p in sr.HARVEST_PASSES}
        self.assertIn("flaw:", prefixes)
        self.assertIn("element:", prefixes)

    def test_plain_pass_offers_the_unqualified_vocabulary(self):
        plain = [p for p in sr.HARVEST_PASSES if p["prefix"] == ""]
        self.assertTrue(plain, "composition/palette take no qualifier and need a home")
        terms = set(plain[0]["palette"])
        self.assertTrue({"composition", "palette"} <= terms)


class TestTemplateWiring(unittest.TestCase):
    """The page must actually carry the UI; a syntax-valid page that lacks it is worse."""

    def test_template_declares_the_harvest_placeholders(self):
        self.assertIn("{{PASSES}}", sr._TEMPLATE)
        self.assertIn("{{TAGSINUSE}}", sr._TEMPLATE)

    def test_template_has_the_harvest_controls(self):
        for token in ('id="harvestbtn"', 'id="hvbar"', 'id="hvq"', 'id="hvpal"', 'id="hvinstr"'):
            self.assertIn(token, sr._TEMPLATE, f"missing {token}")

    def test_client_uses_add_tags_not_tags(self):
        """If the client ever POSTs `tags` from the palette, batch tagging clobbers."""
        self.assertIn("add_tags:[tag]", sr._TEMPLATE.replace(" ", ""))


if __name__ == "__main__":
    unittest.main(verbosity=2)
