"""Unit tests for tools/find_dead_code.py reference-detection logic.

All pure: analyzers take an in-memory Corpus (files set + texts dict), so no
checkout, no filesystem walk, no git. The synthetic corpora below encode the
real cases from PR #1118 that earned each detector.

Run: python -m unittest tests.test_find_dead_code
"""

import unittest

from tools.find_dead_code import (
    Corpus,
    analyze_docs,
    analyze_godot,
    analyze_scripts,
    build_uid_map,
    extract_class_decl,
    extract_doc_path_candidates,
    extract_dynamic_prefixes,
    extract_py_imports,
    extract_res_refs,
    extract_script_mentions,
    extract_uid_refs,
    make_ref_regex,
    resolve_local_import,
)


def corpus(texts, extra_files=()):
    files = set(texts) | set(extra_files)
    return Corpus(files=files, texts=dict(texts), root=".")


def by_path(findings):
    return {f.path: f for f in findings}


class TestExtractors(unittest.TestCase):
    def test_res_refs_basic_and_punctuation(self):
        text = 'load("res://scripts/core/foo.gd") # see res://data/x.json.'
        refs = extract_res_refs(text)
        self.assertIn("res://scripts/core/foo.gd", refs)
        self.assertIn("res://data/x.json", refs)  # trailing dot stripped

    def test_res_refs_ignores_bare_scheme(self):
        self.assertEqual(extract_res_refs('globalize_path("res://")'), set())

    def test_uid_refs(self):
        text = '[ext_resource uid="uid://dhdvollqobx6n" path="res://a.gd"]'
        self.assertEqual(extract_uid_refs(text), {"uid://dhdvollqobx6n"})

    def test_class_decl(self):
        self.assertEqual(extract_class_decl("extends Node\nclass_name Foo\n"), "Foo")
        self.assertIsNone(extract_class_decl("extends Node\n"))

    def test_dynamic_prefix_trailing_slash_const(self):
        # event_service.gd / office_cat.gd pattern
        text = 'const DIR = "res://data/events/overrides/"'
        self.assertEqual(extract_dynamic_prefixes(text), {"res://data/events/overrides/"})

    def test_dynamic_prefix_extensionless_dir_const(self):
        # actions.gd pattern: no trailing slash, no extension
        text = 'const ACTIONS_DATA_DIR := "res://data/actions"'
        self.assertEqual(extract_dynamic_prefixes(text), {"res://data/actions/"})

    def test_dynamic_prefix_format_string(self):
        text = 'var p = "res://assets/icons/%s.png" % name'
        self.assertEqual(extract_dynamic_prefixes(text), {"res://assets/icons/"})

    def test_dynamic_prefix_concatenation(self):
        text = 'var p = "res://assets/cats/simple/cat_" + mood + ".svg"'
        self.assertEqual(extract_dynamic_prefixes(text), {"res://assets/cats/simple/"})

    def test_dynamic_prefix_ignores_bare_root_and_plain_files(self):
        self.assertEqual(extract_dynamic_prefixes('var r = "res://"'), set())
        self.assertEqual(extract_dynamic_prefixes('preload("res://scripts/foo.gd")'), set())

    def test_py_imports_absolute_and_relative(self):
        text = (
            "import os\n"
            "from src.core.game_state import GameState\n"
            "from .api_format import WebAPIFormatter\n"
            "import write_build_stamp\n"
        )
        self.assertEqual(
            extract_py_imports(text),
            {"os", "src.core.game_state", ".api_format", "write_build_stamp"},
        )

    def test_resolve_local_import(self):
        files = {
            "scripts/foo.py",
            "tools/pkg/__init__.py",
            "tools/pkg/a.py",
            "tools/build.py",
            "tools/stamp.py",
        }
        dirs = {"scripts", "tools", "tools/pkg"}
        self.assertEqual(
            resolve_local_import("scripts.foo", "x.py", files, dirs), ("ok", "scripts/foo.py")
        )
        self.assertEqual(
            resolve_local_import("src.core.game_state", "tests/t.py", files, dirs),
            ("missing", "src/core/game_state.py"),
        )
        # same-dir bare import (build_release importing write_build_stamp)
        self.assertEqual(
            resolve_local_import("stamp", "tools/build.py", files, dirs), ("ok", "tools/stamp.py")
        )
        # relative import inside a package (the web_export __init__ pattern)
        self.assertEqual(
            resolve_local_import(".a", "tools/pkg/__init__.py", files, dirs),
            ("ok", "tools/pkg/a.py"),
        )
        self.assertEqual(
            resolve_local_import(".gone", "tools/pkg/__init__.py", files, dirs),
            ("missing", "tools/pkg/gone.py"),
        )
        # stdlib / third-party are out of scope
        self.assertEqual(resolve_local_import("os.path", "x.py", files, dirs), ("external", ""))

    def test_script_mentions_token_boundaries(self):
        names, mods = extract_script_mentions(
            "run precommit.py then python tools/commit.py -m x\n"
            "also python -m scripts.run_godot_tests --quick\n"
            "reads configs/default.template.json here"
        )
        self.assertIn("commit.py", names)
        self.assertIn("precommit.py", names)  # its own token, exact
        self.assertNotIn("recommit.py", names)
        self.assertIn("default.template.json", names)
        self.assertIn("scripts.run_godot_tests", mods)

    def test_ref_regex_boundaries(self):
        rex = make_ref_regex("commit.py")
        self.assertTrue(rex.search("tools/commit.py"))
        self.assertFalse(rex.search("precommit.py"))
        self.assertFalse(rex.search("commit.python"))

    def test_doc_path_candidates(self):
        text = (
            "Run `python scripts/foo.py --check` after `godot/scenes/a.tscn`.\n"
            "See `https://example.com/x.py` and `<path>` and `path/to/f.py`.\n"
            "Also `validate_parity.py` and `res://data/x.json` and `v0.11/0.12`.\n"
            "Prose like `input/output` stays out.\n"
        )
        toks = extract_doc_path_candidates(text)
        self.assertIn("scripts/foo.py", toks)
        self.assertIn("godot/scenes/a.tscn", toks)
        self.assertIn("validate_parity.py", toks)  # bare filename, code ext
        self.assertIn("res://data/x.json", toks)
        self.assertNotIn("https://example.com/x.py", toks)
        self.assertNotIn("path/to/f.py", toks)
        self.assertNotIn("input/output", toks)
        for t in toks:
            self.assertNotIn("0.12", t)

    def test_uid_map_sources(self):
        c = corpus(
            {
                "godot/scripts/a.gd.uid": "uid://aaa111\n",
                "godot/scenes/b.tscn": '[gd_scene load_steps=2 format=3 uid="uid://bbb222"]\n',
                "godot/assets/c.png.import": 'uid="uid://ccc333"\nsource_file="res://assets/c.png"\n',
            }
        )
        m = build_uid_map(c)
        self.assertEqual(m["uid://aaa111"], "godot/scripts/a.gd")
        self.assertEqual(m["uid://bbb222"], "godot/scenes/b.tscn")
        self.assertEqual(m["uid://ccc333"], "godot/assets/c.png")


BASE_PROJECT = (
    "config_version=5\n"
    "[application]\n"
    'run/main_scene="res://scenes/main.tscn"\n'
    "[autoload]\n"
    'EventService="*res://autoload/event_service.gd"\n'
)


class TestAnalyzeGodot(unittest.TestCase):
    def make(self, extra_texts=None, extra_files=(), flagged=None):
        texts = {
            "godot/project.godot": BASE_PROJECT,
            "godot/scenes/main.tscn": '[gd_scene format=3 uid="uid://mainscene"]\n'
            '[ext_resource type="Script" path="res://scripts/ui/main_ui.gd"]\n',
            "godot/scripts/ui/main_ui.gd": "extends Control\n",
            "godot/autoload/event_service.gd": 'const OVERRIDES_DIR = "res://data/events/overrides/"\n',
        }
        texts.update(extra_texts or {})
        return analyze_godot(corpus(texts, extra_files), False, flagged or set())

    def test_orphan_gd_confirmed_and_live_gd_not_flagged(self):
        f = by_path(
            self.make(
                {
                    "godot/scripts/ui/orphan_widget.gd": "extends Control\n@onready var x = $Missing/Node\n",
                }
            )
        )
        self.assertIn("godot/scripts/ui/orphan_widget.gd", f)
        self.assertEqual(f["godot/scripts/ui/orphan_widget.gd"].tier, "CONFIRMED")
        self.assertNotIn("godot/scripts/ui/main_ui.gd", f)

    def test_class_name_use_confers_liveness(self):
        f = by_path(
            self.make(
                {
                    "godot/scripts/core/helper.gd": "class_name DoomHelper\nextends RefCounted\n",
                    "godot/scripts/ui/main_ui.gd": "extends Control\nvar h = DoomHelper.new()\n",
                }
            )
        )
        self.assertNotIn("godot/scripts/core/helper.gd", f)

    def test_unreferenced_scene_flagged(self):
        f = by_path(
            self.make(
                {
                    "godot/scenes/old_menu.tscn": "[gd_scene format=3]\n",
                }
            )
        )
        self.assertEqual(f["godot/scenes/old_menu.tscn"].tier, "CONFIRMED")
        self.assertEqual(f["godot/scenes/old_menu.tscn"].category, "scene")

    def test_cycle_of_orphans_is_flagged(self):
        # A preloads B, B preloads A, nothing else references either:
        # naive single-level counting sees both as referenced.
        f = by_path(
            self.make(
                {
                    "godot/scripts/core/cycle_a.gd": 'const B = preload("res://scripts/core/cycle_b.gd")\n',
                    "godot/scripts/core/cycle_b.gd": 'const A = preload("res://scripts/core/cycle_a.gd")\n',
                }
            )
        )
        self.assertIn("godot/scripts/core/cycle_a.gd", f)
        self.assertIn("godot/scripts/core/cycle_b.gd", f)
        self.assertEqual(f["godot/scripts/core/cycle_a.gd"].tier, "LIKELY")

    def test_dynamic_dir_contents_unverifiable_never_confirmed(self):
        # example.json lives under the overrides dir event_service globs;
        # PR #1118 proved it LIVE. The scanner must never call it dead.
        f = by_path(self.make(extra_files=["godot/data/events/overrides/example.json"]))
        found = f["godot/data/events/overrides/example.json"]
        self.assertEqual(found.tier, "UNVERIFIABLE")
        self.assertIn("event_service", found.evidence[0])

    def test_test_declared_prefix_does_not_shield(self):
        # A dir-walking smoke test loads everything; that demands nothing.
        f = by_path(
            self.make(
                {
                    "godot/tests/unit/test_smoke.gd": 'const ROOT = "res://scripts/"\n',
                    "godot/scripts/ui/orphan_widget.gd": "extends Control\n",
                }
            )
        )
        self.assertEqual(f["godot/scripts/ui/orphan_widget.gd"].tier, "CONFIRMED")

    def test_orphan_asset_goes_to_grandfathered_section(self):
        f = by_path(self.make(extra_files=["godot/assets/images/unused.webp"]))
        found = f["godot/assets/images/unused.webp"]
        self.assertEqual(found.section, "grandfathered")
        self.assertTrue(any("ADR-0019" in e for e in found.evidence))

    def test_referenced_asset_not_flagged(self):
        f = by_path(
            self.make(
                {"godot/scripts/ui/main_ui.gd": 'var t = load("res://assets/images/logo.png")\n'},
                extra_files=["godot/assets/images/logo.png"],
            )
        )
        self.assertNotIn("godot/assets/images/logo.png", f)

    def test_test_only_reference_reported_not_deleted(self):
        # candidate_card.gd: only caller is a test -- label, do not delete.
        f = by_path(
            self.make(
                {
                    "godot/scripts/ui/candidate_card.gd": "extends Control\n",
                    "godot/tests/unit/test_hiring.gd": 'const Card = preload("res://scripts/ui/candidate_card.gd")\n',
                }
            )
        )
        found = f["godot/scripts/ui/candidate_card.gd"]
        self.assertEqual(found.section, "test-only")

    def test_allowlist_respected(self):
        f = by_path(
            self.make(
                {
                    "godot/autoload/steam_manager.gd": "extends Node\n",
                }
            )
        )
        self.assertNotIn("godot/autoload/steam_manager.gd", f)

    def test_external_exec_reference_keeps_scene_alive(self):
        # capture_cinematic.py runs a scene: that scene is not dead.
        f = by_path(
            self.make(
                {
                    "tools/capture_cinematic.py": 'SCENE = "res://scenes/dev/captures/portal_capture.tscn"\n',
                    "godot/scenes/dev/captures/portal_capture.tscn": "[gd_scene format=3]\n",
                }
            )
        )
        self.assertNotIn("godot/scenes/dev/captures/portal_capture.tscn", f)

    def test_flagged_script_reference_downgrades_not_revives(self):
        # ...but if the referencing script is itself flagged dead, the scene
        # is LIKELY-dead, not alive.
        f = by_path(
            self.make(
                {
                    "tools/capture_cinematic.py": 'SCENE = "res://scenes/dev/captures/portal_capture.tscn"\n',
                    "godot/scenes/dev/captures/portal_capture.tscn": "[gd_scene format=3]\n",
                },
                flagged={"tools/capture_cinematic.py"},
            )
        )
        found = f["godot/scenes/dev/captures/portal_capture.tscn"]
        self.assertEqual(found.tier, "LIKELY")

    def test_uid_reference_confers_liveness(self):
        f = by_path(
            self.make(
                {
                    "godot/scenes/main.tscn": '[gd_scene format=3 uid="uid://mainscene"]\n'
                    '[ext_resource type="Script" uid="uid://helper1"]\n',
                    "godot/scripts/ui/helper.gd": "extends Node\n",
                    "godot/scripts/ui/helper.gd.uid": "uid://helper1\n",
                }
            )
        )
        self.assertNotIn("godot/scripts/ui/helper.gd", f)


class TestAnalyzeScripts(unittest.TestCase):
    def run_scripts(self, texts, extra_files=()):
        findings, flagged = analyze_scripts(corpus(texts, extra_files), False)
        return by_path(findings), flagged

    def test_unreferenced_python_confirmed(self):
        f, flagged = self.run_scripts({"tools/orphan_tool.py": "print(1)\n"})
        self.assertEqual(f["tools/orphan_tool.py"].tier, "CONFIRMED")
        self.assertIn("tools/orphan_tool.py", flagged)

    def test_workflow_invocation_is_liveness(self):
        f, _ = self.run_scripts(
            {
                "scripts/run_godot_tests.py": "print(1)\n",
                ".github/workflows/tests.yml": "run: python scripts/run_godot_tests.py --quick\n",
            }
        )
        self.assertNotIn("scripts/run_godot_tests.py", f)

    def test_doc_only_mention_is_likely_the_sync_script_class(self):
        # sync_from_pdoom_data.sh: documented everywhere, executed nowhere.
        f, _ = self.run_scripts(
            {
                "scripts/sync_from_pdoom_data.sh": "#!/bin/bash\nrsync x y\n",
                "docs/PIPELINE.md": "Run `scripts/sync_from_pdoom_data.sh` daily.\n",
            }
        )
        found = f["scripts/sync_from_pdoom_data.sh"]
        self.assertEqual(found.tier, "LIKELY")
        self.assertIn("nothing executes it", found.evidence[0])

    def test_archived_mentions_do_not_confer_liveness(self):
        # An archived copy of a script mentioning its own name must not keep
        # the live copy "referenced" (hid setup_godot_migration.py once).
        f, _ = self.run_scripts(
            {
                "tools/setup_godot_migration.py": "print(1)\n",
                "archive/legacy/tools/setup_godot_migration.py": "# usage: python tools/setup_godot_migration.py\n",
                "docs/archive/old_notes.md": "`tools/setup_godot_migration.py`\n",
            }
        )
        found = f["tools/setup_godot_migration.py"]
        self.assertEqual(found.tier, "CONFIRMED")
        self.assertTrue(any("archives" in e for e in found.evidence))

    def test_dead_cluster_fixpoint(self):
        # integration_test imports the package; nothing runs integration_test:
        # the whole web_export cluster is dead (PR #1118).
        f, flagged = self.run_scripts(
            {
                "tools/integration_test.py": "import tools.web_export_mod\n",
                "tools/web_export_mod.py": "X = 1\n",
            }
        )
        self.assertIn("tools/integration_test.py", flagged)
        self.assertIn("tools/web_export_mod.py", flagged)
        self.assertEqual(f["tools/web_export_mod.py"].tier, "LIKELY")

    def test_discovery_collected_but_broken_imports(self):
        # The #1117 pattern: unittest discover runs it, || echo hides the
        # ImportError, CI reports green over zero assertions.
        f, flagged = self.run_scripts(
            {
                "tests/test_pygame_thing.py": "from src.core.game_state import GameState\n",
                ".github/workflows/ci.yml": 'run: python -m unittest discover tests -v || echo "ok"\n',
            }
        )
        found = f["tests/test_pygame_thing.py"]
        self.assertEqual(found.tier, "LIKELY")
        self.assertIn("CANNOT run", found.evidence[0])
        self.assertNotIn("tests/test_pygame_thing.py", flagged)

    def test_shebang_script_without_extension(self):
        # tools/pre-commit-issue-check: a hook never wired into config.
        f, _ = self.run_scripts(
            {
                "tools/pre-commit-issue-check": "#!/bin/bash\nexit 0\n",
            }
        )
        self.assertIn("tools/pre-commit-issue-check", f)

    def test_extensionless_non_script_ignored(self):
        f, _ = self.run_scripts(
            {
                "tools/dev/global_style_icon": "high-res 512x512 square icon\n",
            }
        )
        self.assertNotIn("tools/dev/global_style_icon", f)

    def test_broken_package_init_reported(self):
        # tools/web_export/__init__.py: relative imports of deleted members
        # made `import tools.web_export` raise unconditionally.
        f, flagged = self.run_scripts(
            {
                "tools/web_export/__init__.py": "from .export_leaderboards import LeaderboardWebExporter\n",
            }
        )
        found = f["tools/web_export/__init__.py"]
        self.assertEqual(found.tier, "LIKELY")
        self.assertIn("ALWAYS raises", found.evidence[0])
        self.assertIn("tools/web_export/__init__.py", flagged)

    def test_invalid_orphan_config_json(self):
        # configs/*.json in Python-dict syntax: json.load raised on line 2,
        # so no loader can ever have read them (PR #1118).
        f, _ = self.run_scripts(
            {
                "configs/default.template.json": "{'window_scale': 2}\n",
            }
        )
        found = f["configs/default.template.json"]
        self.assertEqual(found.tier, "CONFIRMED")
        self.assertTrue(any("not even valid JSON" in e for e in found.evidence))

    def test_referenced_config_json_not_flagged(self):
        f, _ = self.run_scripts(
            {
                "configs/live.json": '{"a": 1}\n',
                "scripts/loader.py": 'open("configs/live.json")\n',
            }
        )
        self.assertNotIn("configs/live.json", f)


class TestAnalyzeDocs(unittest.TestCase):
    def run_docs(self, texts, extra_files=()):
        return by_path(analyze_docs(corpus(texts, extra_files), False))

    def test_missing_backticked_path_flagged(self):
        f = self.run_docs(
            {
                "docs/DOC_LIFECYCLE.md": "Run `scripts/check_doc_staleness.py` weekly.\n",
            }
        )
        found = f["docs/DOC_LIFECYCLE.md"]
        self.assertEqual(found.category, "doc-broken-path")
        self.assertIn("scripts/check_doc_staleness.py", found.evidence[0])

    def test_existing_path_not_flagged(self):
        f = self.run_docs(
            {"docs/OK.md": "See `scripts/real.py`.\n"}, extra_files=["scripts/real.py"]
        )
        self.assertNotIn("docs/OK.md", f)

    def test_ancestor_relative_resolution(self):
        # godot/docs/*.md saying `autoload/x.gd` means godot/autoload/x.gd.
        f = self.run_docs(
            {"godot/docs/qa/NOTES.md": "Fixed `autoload/music_manager.gd`.\n"},
            extra_files=["godot/autoload/music_manager.gd"],
        )
        self.assertNotIn("godot/docs/qa/NOTES.md", f)

    def test_bare_filename_missing_everywhere_flagged(self):
        # tools/migration/README.md listed scripts that never existed.
        f = self.run_docs(
            {
                "tools/migration/README.md": "- `validate_parity.py` checks x\n",
            }
        )
        self.assertIn("tools/migration/README.md", f)

    def test_bare_filename_existing_anywhere_ok(self):
        f = self.run_docs(
            {"docs/GUIDE.md": "Uses `export_leaderboards.py` for export.\n"},
            extra_files=["scripts/export_leaderboards.py"],
        )
        self.assertNotIn("docs/GUIDE.md", f)

    def test_res_path_checked_against_godot_tree(self):
        f = self.run_docs(
            {"docs/EVENTS.md": "Add `res://data/events/overrides/promo.json` next.\n"}
        )
        self.assertIn("docs/EVENTS.md", f)

    def test_archived_docs_skipped_by_default(self):
        f = self.run_docs(
            {
                "docs/archive/OLD.md": "See `scripts/gone_forever.py`.\n",
            }
        )
        self.assertNotIn("docs/archive/OLD.md", f)


if __name__ == "__main__":
    unittest.main()
