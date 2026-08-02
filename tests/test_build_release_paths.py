# !/usr/bin/env python3
"""Unit tests for tools/build_release.py output-name derivation (issue #1072).

The defect these lock down: build_release.py used to compute
`exe_path = out_dir / "PDoom.exe"` regardless of --preset, so Linux and macOS
exports landed named PDoom.exe and three presets sharing one --output directory
would silently overwrite each other -- in a tool whose whole purpose is proving
which source produced which binary.

The fix reads the filename from the preset's own export_path, so this file also
checks against the REAL godot/export_presets.cfg, which is what makes the
derivation unable to drift from a manual export.
"""

import io
import sys
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_release  # noqa: E402  (deliberate late import; sys.path just set)

# Trimmed but structurally faithful sample: quoted values, an [preset.N.options]
# sub-section between presets (which must NOT be read as preset keys), and a
# multi-line unindented dict value of the kind the real macOS preset carries
# (this is why configparser cannot be used here).
SAMPLE_CFG = """[preset.0]

name="Windows Desktop"
platform="Windows Desktop"
runnable=true
export_path="../builds/windows/v0.13.2/PDoom.exe"

[preset.0.options]

binary_format/embed_pck=false
export_path="../builds/decoy/NOT_THIS.exe"

[preset.1]

name="Linux/X11"
platform="Linux/X11"
runnable=true
export_path="../builds/linux/v0.13.2/PDoom.x86_64"

[preset.1.options]

binary_format/architecture="x86_64"

[preset.2]

name="macOS"
platform="macOS"
runnable=true
export_path="../builds/mac/v0.13.2/PDoom.app.zip"

[preset.2.options]

application/copyright_localized={
"en": "Copyright P(Doom)"
}
"""


class TestParseExportPresets(unittest.TestCase):
    def test_finds_all_top_level_presets_in_order(self):
        presets = build_release.parse_export_presets(SAMPLE_CFG)
        self.assertEqual([p["name"] for p in presets], ["Windows Desktop", "Linux/X11", "macOS"])

    def test_ignores_options_subsections(self):
        # A stray export_path inside [preset.0.options] must not leak into the
        # preset -- otherwise a Godot config detail silently redirects the build.
        presets = build_release.parse_export_presets(SAMPLE_CFG)
        self.assertEqual(presets[0]["export_path"], "../builds/windows/v0.13.2/PDoom.exe")

    def test_multiline_dict_value_does_not_break_parsing(self):
        # configparser raises on the unindented continuation lines of
        # application/copyright_localized; the line-wise scanner must not.
        presets = build_release.parse_export_presets(SAMPLE_CFG)
        self.assertEqual(presets[2]["export_path"], "../builds/mac/v0.13.2/PDoom.app.zip")

    def test_empty_config_yields_no_presets(self):
        self.assertEqual(build_release.parse_export_presets(""), [])


class TestOutputNameForPreset(unittest.TestCase):
    def test_each_platform_gets_its_own_filename(self):
        for preset, expected in [
            ("Windows Desktop", "PDoom.exe"),
            ("Linux/X11", "PDoom.x86_64"),
            ("macOS", "PDoom.app.zip"),
        ]:
            with self.subTest(preset=preset):
                self.assertEqual(build_release.output_name_for_preset(SAMPLE_CFG, preset), expected)

    def test_the_three_names_are_distinct(self):
        # This is the actual bug: identical names meant a shared --output dir
        # silently overwrote artifacts.
        names = {
            build_release.output_name_for_preset(SAMPLE_CFG, n)
            for n in ("Windows Desktop", "Linux/X11", "macOS")
        }
        self.assertEqual(len(names), 3)

    def test_windows_style_backslashes_in_export_path(self):
        cfg = '[preset.0]\nname="Win"\nexport_path="..\\\\builds\\\\win\\\\PDoom.exe"\n'
        self.assertEqual(build_release.output_name_for_preset(cfg, "Win"), "PDoom.exe")

    def test_bare_filename_export_path(self):
        cfg = '[preset.0]\nname="Win"\nexport_path="PDoom.exe"\n'
        self.assertEqual(build_release.output_name_for_preset(cfg, "Win"), "PDoom.exe")

    def test_unknown_preset_raises_and_lists_available(self):
        with self.assertRaises(ValueError) as ctx:
            build_release.output_name_for_preset(SAMPLE_CFG, "Nintendo Switch")
        self.assertIn("Nintendo Switch", str(ctx.exception))
        self.assertIn("Linux/X11", str(ctx.exception))

    def test_empty_export_path_raises_rather_than_guessing(self):
        cfg = '[preset.0]\nname="Web"\nexport_path=""\n'
        with self.assertRaises(ValueError):
            build_release.output_name_for_preset(cfg, "Web")

    def test_missing_export_path_key_raises(self):
        cfg = '[preset.0]\nname="Web"\nplatform="Web"\n'
        with self.assertRaises(ValueError):
            build_release.output_name_for_preset(cfg, "Web")


class TestAgainstRealExportPresets(unittest.TestCase):
    """The anti-drift half: derive from the config the build actually uses."""

    def setUp(self):
        cfg = REPO_ROOT / "godot" / "export_presets.cfg"
        if not cfg.exists():
            self.skipTest(f"no export_presets.cfg at {cfg}")
        self.text = cfg.read_text(encoding="utf-8")

    def test_real_presets_resolve_to_the_shipped_asset_names(self):
        self.assertEqual(
            build_release.output_name_for_preset(self.text, "Windows Desktop"), "PDoom.exe"
        )
        self.assertEqual(
            build_release.output_name_for_preset(self.text, "Linux/X11"), "PDoom.x86_64"
        )
        self.assertEqual(build_release.output_name_for_preset(self.text, "macOS"), "PDoom.app.zip")

    def test_no_two_real_presets_share_an_output_filename(self):
        presets = build_release.parse_export_presets(self.text)
        names = [
            build_release.output_name_for_preset(self.text, p["name"])
            for p in presets
            if p.get("name") and p.get("export_path")
        ]
        self.assertEqual(len(names), len(set(names)), f"colliding output filenames: {names}")


class TestFindMarker(unittest.TestCase):
    """The zipped-bundle half (issue #1072): a macOS .app.zip hides the marker
    filename inside a compressed entry, so a raw byte scan false-FAILS."""

    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.token = b"buildstampdeadbeefcafe"

    def test_plain_file_containing_marker(self):
        p = self.tmp / "PDoom.pck"
        p.write_bytes(b"\x00" * 100 + self.token + b"\x00" * 100)
        self.assertIsNotNone(build_release.find_marker(p, self.token))

    def test_plain_file_without_marker(self):
        p = self.tmp / "PDoom.pck"
        p.write_bytes(b"\x00" * 4096)
        self.assertIsNone(build_release.find_marker(p, self.token))

    def test_marker_straddling_a_chunk_boundary(self):
        # The chunked scanner must carry a tail; a match split across two reads
        # would otherwise be missed and reported as a stale build.
        p = self.tmp / "PDoom.pck"
        chunk = build_release._SCAN_CHUNK
        head = b"\x00" * (chunk - len(self.token) // 2)
        p.write_bytes(head + self.token + b"\x00" * 64)
        self.assertIsNotNone(build_release.find_marker(p, self.token))

    def test_zip_with_marker_only_inside_a_compressed_entry(self):
        # The macOS shape: the marker's res:// filename lives in the bundled
        # .pck, which is DEFLATEd, so it is absent from the zip's raw bytes.
        inner = io.BytesIO()
        inner.write(b"\x00" * 2048 + self.token + b"\x00" * 2048)
        zip_path = self.tmp / "PDoom.app.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("PDoom.app/Contents/Resources/PDoom.pck", inner.getvalue())
        self.assertNotIn(self.token, zip_path.read_bytes(), "test setup: token must be hidden")
        found = build_release.find_marker(zip_path, self.token)
        self.assertIsNotNone(found)
        self.assertIn("PDoom.pck", found)

    def test_zip_with_marker_as_an_entry_name(self):
        zip_path = self.tmp / "PDoom.app.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"PDoom.app/{self.token.decode()}.gd", "extends Node\n")
        found = build_release.find_marker(zip_path, self.token)
        self.assertIsNotNone(found)
        self.assertIn("zip entry name", found)

    def test_zip_without_marker_still_reports_absent(self):
        # The guarantee must not be weakened into always-passing.
        zip_path = self.tmp / "PDoom.app.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("PDoom.app/Contents/Resources/PDoom.pck", b"\x00" * 4096)
        self.assertIsNone(build_release.find_marker(zip_path, self.token))


if __name__ == "__main__":
    unittest.main()
