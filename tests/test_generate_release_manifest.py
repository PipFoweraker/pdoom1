# !/usr/bin/env python3
"""Unit tests for scripts/generate_release_manifest.py (self-updater workstream).

What these lock down:

- The manifest field CONTRACT: `update_check.gd` parses "version" /
  "ladder_version" / "highlights" / "download_page" by exact name, and older
  consumers read the legacy heredoc fields. Removing or renaming any of them
  breaks shipped clients, so the superset is asserted key-by-key.
- Integrity anchors: the per-asset sha256 entries must be the REAL digest of
  the file bytes -- a wrong hash would make the future pck verifier reject
  good downloads (annoying) or, far worse, a lenient one accept bad ones.
- Loud failure: bad version strings and a missing/garbled ladder_version.txt
  must FAIL manifest generation (SystemExit), never ship silence.
"""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_release_manifest as grm  # noqa: E402


class TestValidateVersion(unittest.TestCase):
    def test_accepts_tag_shapes(self):
        self.assertEqual(grm.validate_version("v0.13.2"), "v0.13.2")
        self.assertEqual(grm.validate_version("0.13.2"), "0.13.2")
        self.assertEqual(grm.validate_version("v1.0.0-rc.1"), "v1.0.0-rc.1")

    def test_rejects_garbage_loudly(self):
        for bad in ("", "latest", "v0.13", "vX.Y.Z", "0..1", "v0.13.2; rm -rf"):
            with self.assertRaises(SystemExit, msg=bad):
                grm.validate_version(bad)


class TestReadLadderVersion(unittest.TestCase):
    def test_reads_real_repo_ladder(self):
        # The actual SSOT file must parse -- this doubles as a repo-state check.
        value = grm.read_ladder_version(REPO_ROOT)
        self.assertTrue(value.isdigit(), "ladder_version.txt must be a bare integer")

    def test_missing_file_fails_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                grm.read_ladder_version(Path(tmp))

    def test_garbled_content_fails_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "ladder_version.txt").write_text("L3\n", encoding="ascii")
            with self.assertRaises(SystemExit):
                grm.read_ladder_version(Path(tmp))


class TestCollectAssets(unittest.TestCase):
    def test_hashes_are_real_sha256_and_sorted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Nested layout mirrors download-artifact: build-*/<ver>/<zip>
            (root / "build-windows").mkdir()
            win = root / "build-windows" / "PDoom-Windows.zip"
            win.write_bytes(b"windows-bytes")
            (root / "build-linux").mkdir()
            lin = root / "build-linux" / "PDoom-Linux.zip"
            lin.write_bytes(b"linux-bytes")
            # A non-zip must NOT be hashed into the asset list.
            (root / "build-windows" / "notes.txt").write_text("x", encoding="ascii")

            assets = grm.collect_assets(root)
            self.assertEqual([a["name"] for a in assets], ["PDoom-Linux.zip", "PDoom-Windows.zip"])
            self.assertEqual(assets[1]["sha256"], hashlib.sha256(b"windows-bytes").hexdigest())
            self.assertEqual(assets[0]["sha256"], hashlib.sha256(b"linux-bytes").hexdigest())
            self.assertEqual(assets[1]["size"], len(b"windows-bytes"))

    def test_absent_dir_yields_empty_list(self):
        self.assertEqual(grm.collect_assets(Path("no/such/dir")), [])
        self.assertEqual(grm.collect_assets(None), [])


class TestExtractHighlights(unittest.TestCase):
    def _fake_repo(self, tmp: str, section_body: str) -> Path:
        root = Path(tmp)
        (root / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [9.9.9] - 2099-01-01\n\n%s\n\n## [0.0.1] - 2020-01-01\nold\n"
            % section_body,
            encoding="utf-8",
        )
        return root

    def test_extracts_this_versions_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fake_repo(tmp, "### Added\n- a thing players see")
            text = grm.extract_highlights(root, "v9.9.9")
            self.assertIn("a thing players see", text)
            self.assertNotIn("old", text)

    def test_truncation_cap_holds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fake_repo(tmp, "x" * 5000)
            text = grm.extract_highlights(root, "v9.9.9", max_chars=200)
            self.assertLessEqual(len(text), 200 + len(grm.TRUNCATION_MARK))
            self.assertTrue(text.endswith(grm.TRUNCATION_MARK))

    def test_output_is_ascii(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Escapes keep this SOURCE file ASCII (house rule #744) while the
            # changelog content under test is genuinely non-ASCII.
            root = self._fake_repo(tmp, "- em\u2014dash and caf\u00e9")
            text = grm.extract_highlights(root, "v9.9.9")
            text.encode("ascii")  # raises on failure


class TestBuildManifest(unittest.TestCase):
    def _manifest(self):
        return grm.build_manifest(
            version="v0.13.3",
            commit="abcdef0123456789",
            ladder_version="3",
            highlights="### Fixed\n- a bug",
            assets=[{"name": "PDoom-Windows.zip", "size": 1, "sha256": "aa"}],
            repository="PipFoweraker/pdoom1",
            data_hash="dh",
            workflow_run="wr",
            ref="refs/tags/v0.13.3",
            actor="ci",
            event="push",
        )

    def test_legacy_heredoc_fields_all_survive(self):
        # CONTRACT: the script replaced a YAML heredoc; every field the heredoc
        # published must still exist under the same name (add-only manifest).
        m = self._manifest()
        for key in (
            "version",
            "build_date",
            "commit_hash",
            "commit_short",
            "data_batch_hash",
            "schema_versions",
            "engine",
            "platforms",
            "validation_passed",
            "build_pipeline",
            "workflow_run",
            "provenance",
        ):
            self.assertIn(key, m, "legacy manifest field %r must not be dropped" % key)
        self.assertEqual(m["commit_short"], "abcdef01")
        self.assertEqual(m["engine"], {"name": "Godot", "version": "4.5.1"})

    def test_updater_fields_match_gdscript_contract(self):
        # These names are parsed verbatim by update_check.gd
        # parse_release_manifest(); renaming either side breaks the check.
        m = self._manifest()
        self.assertEqual(m["version"], "v0.13.3")
        self.assertEqual(m["ladder_version"], "3")
        self.assertEqual(m["highlights"], "### Fixed\n- a bug")
        self.assertEqual(
            m["download_page"],
            "https://github.com/PipFoweraker/pdoom1/releases/tag/v0.13.3",
        )
        self.assertEqual(m["assets"][0]["sha256"], "aa")

    def test_download_page_is_trusted_prefix(self):
        # update_check.gd only shell-opens pages under this prefix; a manifest
        # that drifts off it silently loses its download link in-game.
        m = self._manifest()
        self.assertTrue(m["download_page"].startswith("https://github.com/PipFoweraker/pdoom1/"))

    def test_manifest_serializes_to_ascii_json(self):
        body = json.dumps(self._manifest(), indent=2)
        body.encode("ascii")


if __name__ == "__main__":
    unittest.main()
