# !/usr/bin/env python3
"""Unit tests for scripts/build_all_platforms.py orchestration (issue #1069).

The defect these lock down: the CI release path used to run a raw
`godot --export-release` with none of tools/build_release.py's discipline
(cache nuke, freshness marker, marker-in-pack proof), so the binary a
developer proved locally was never the binary players downloaded. The fix
delegates every per-platform export to build_release.py; these tests pin:

- the delegation command actually routes through tools/build_release.py
- Windows/Linux are REQUIRED, macOS is best-effort (issue #1071 ruling)
- a failed platform's output dir is cleared, so a stale or unverified
  artifact can never be packaged or uploaded
- a required-platform failure aborts before any packaging; a macOS-only
  failure does not block Windows/Linux
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_all_platforms  # noqa: E402  (deliberate late import; sys.path just set)


def make_builder(repo_root: Path, version: str = "v9.9.9"):
    """Builder instance without __init__ (which requires a real Godot exe)."""
    b = build_all_platforms.MultiPlatformBuilder.__new__(build_all_platforms.MultiPlatformBuilder)
    b.version = version
    b.version_num = version.lstrip("v")
    b.repo_root = repo_root
    b.godot_dir = repo_root / "godot"
    b.godot_exe = repo_root / "godot_exe"
    return b


class TestRequiredPlatforms(unittest.TestCase):
    def test_windows_and_linux_are_required(self):
        self.assertIn("Windows", build_all_platforms.MultiPlatformBuilder.REQUIRED_PLATFORMS)
        self.assertIn("Linux", build_all_platforms.MultiPlatformBuilder.REQUIRED_PLATFORMS)

    def test_macos_is_best_effort(self):
        # The #1069 ruling: macOS (issue #1071) must not block Windows/Linux
        # from publishing. If macOS ever becomes required, change this test
        # deliberately, not by accident.
        self.assertNotIn("macOS", build_all_platforms.MultiPlatformBuilder.REQUIRED_PLATFORMS)


class TestBuildReleaseCmd(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        self.builder = make_builder(self.repo)

    def test_command_routes_through_build_release(self):
        cmd = self.builder._build_release_cmd("Windows Desktop", self.repo / "out")
        self.assertEqual(cmd[0], sys.executable)
        self.assertEqual(Path(cmd[1]).name, "build_release.py")
        self.assertEqual(Path(cmd[1]).parent.name, "tools")

    def test_command_carries_preset_output_godot_and_project(self):
        out_dir = self.repo / "builds" / "linux" / "v9.9.9"
        cmd = self.builder._build_release_cmd("Linux/X11", out_dir)
        for flag, value in [
            ("--preset", "Linux/X11"),
            ("--output", str(out_dir)),
            ("--godot-path", str(self.builder.godot_exe)),
            ("--project", str(self.builder.godot_dir)),
        ]:
            with self.subTest(flag=flag):
                self.assertIn(flag, cmd)
                self.assertEqual(cmd[cmd.index(flag) + 1], value)

    def test_command_never_weakens_the_discipline(self):
        # --no-clean would skip the cache nuke; --keep-marker litters the
        # project. Neither has any business in the release path.
        cmd = self.builder._build_release_cmd("macOS", self.repo / "out")
        self.assertNotIn("--no-clean", cmd)
        self.assertNotIn("--keep-marker", cmd)


class TestExportPlatform(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        self.builder = make_builder(self.repo)
        self.build_dir = self.repo / "builds" / "windows" / "v9.9.9"
        self.build_dir.mkdir(parents=True)

    def test_success_returns_true_and_keeps_outputs(self):
        artifact = self.build_dir / "PDoom.exe"
        artifact.write_bytes(b"exe")
        with mock.patch.object(
            build_all_platforms.subprocess,
            "run",
            return_value=subprocess.CompletedProcess([], 0),
        ):
            ok = self.builder.export_platform("Windows Desktop", "Windows", self.build_dir)
        self.assertTrue(ok)
        self.assertTrue(artifact.exists())

    def test_failure_clears_the_output_dir(self):
        # A build_release.py failure can happen AFTER the export wrote files
        # (freshness miss). Nothing left behind may be packaged or uploaded.
        stale = self.build_dir / "PDoom.app.zip"
        stale.write_bytes(b"stale unverified export")
        with mock.patch.object(
            build_all_platforms.subprocess,
            "run",
            return_value=subprocess.CompletedProcess([], 1),
        ):
            ok = self.builder.export_platform("macOS", "macOS", self.build_dir)
        self.assertFalse(ok)
        self.assertFalse(stale.exists())
        self.assertTrue(self.build_dir.exists())
        self.assertEqual(list(self.build_dir.iterdir()), [])


class TestBuildAllFailurePolicy(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        self.builder = make_builder(self.repo)
        self.builder._stamp_build = mock.Mock(return_value=True)
        self.builder._update_export_paths = mock.Mock()
        self.builder.zip_builds = mock.Mock(return_value=True)

    def _fake_exports(self, outcomes):
        def fake(preset_name, platform_name, build_dir):
            return outcomes[platform_name]

        self.builder.export_platform = mock.Mock(side_effect=fake)

    def test_macos_failure_does_not_block_the_release(self):
        self._fake_exports({"Windows": True, "Linux": True, "macOS": False})
        self.assertTrue(self.builder.build_all())
        self.builder.zip_builds.assert_called_once()

    def test_required_platform_failure_packages_nothing(self):
        # A half-built release is worse than none: no zips, exit non-zero.
        self._fake_exports({"Windows": True, "Linux": False, "macOS": True})
        self.assertFalse(self.builder.build_all())
        self.builder.zip_builds.assert_not_called()

    def test_all_green_still_green(self):
        self._fake_exports({"Windows": True, "Linux": True, "macOS": True})
        self.assertTrue(self.builder.build_all())
        self.builder.zip_builds.assert_called_once()

    def test_zip_failure_fails_the_build(self):
        self._fake_exports({"Windows": True, "Linux": True, "macOS": True})
        self.builder.zip_builds = mock.Mock(return_value=False)
        self.assertFalse(self.builder.build_all())


if __name__ == "__main__":
    unittest.main()
