# !/usr/bin/env python3
"""
Build P(Doom) for all platforms (Windows, Linux, macOS).

This script orchestrates per-platform exports and packages the distribution
zips. Since issue #1069 the EXPORT itself is delegated to
tools/build_release.py, one preset at a time, so CI and local cuts share ONE
build discipline: rm -rf godot/.godot before the export (defeats the stale
.godot/exported cache that burned ~12 cycles in v0.11.0), a unique
freshness-marker file, and post-export PROOF that the marker landed inside the
exported .pck/zip. This script previously ran a raw `godot --export-release`,
which had none of that -- the release path routed around the tool built to
prevent the disaster.

The per-platform builds are SEQUENTIAL BY DESIGN and must stay that way:
every build_release.py invocation deletes godot/.godot, so parallel exports
would destroy each other's import caches mid-flight.

macOS is BEST-EFFORT (issue #1071): the GodotSteam .framework loses its
Versions/Current symlink on non-mac checkouts, so the macOS export can fail
through no fault of the tagged source. A macOS failure is reported LOUDLY and
its outputs are discarded (never package an unproven artifact), but it does
not block Windows and Linux from shipping. Windows or Linux failing fails the
whole build, and nothing is packaged.

Usage:
    python scripts/build_all_platforms.py --version v0.10.1
    python scripts/build_all_platforms.py --version v0.10.1 --godot-path "C:/Program Files/Godot/Godot.exe"
"""

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Optional


class MultiPlatformBuilder:
    """Builds game for Windows, Linux, and macOS using Godot."""

    # GDExtension libraries the Godot export lays down beside the executable
    # (from godot/addons/godotsteam/godotsteam.gdextension: the [libraries]
    # release entry plus the [dependencies] steam_api library). Shipping a zip
    # without them causes GDExtension load errors and dead Steam integration
    # (v0.13.1 forensics, issue #917), so packaging fails loudly if absent.
    EXPECTED_WINDOWS_LIBS = [
        "libgodotsteam.windows.template_release.x86_64.dll",
        "steam_api64.dll",
    ]
    EXPECTED_LINUX_LIBS = [
        "libgodotsteam.linux.template_release.x86_64.so",
        "libsteam_api.so",
    ]

    # Platforms a release MUST ship. macOS is deliberately absent: issue #1071
    # (the GodotSteam .framework's Versions/Current symlink does not survive a
    # non-mac checkout, so the macOS export can fail through no fault of the
    # tagged source). The ruling (issue #1069): a macOS failure must be LOUD
    # and its outputs discarded, but it must not block Windows and Linux from
    # publishing. The release workflow's alias check (PDoom.app.zip must
    # answer 200) then turns the run red AFTER Windows/Linux publish -- a
    # visible failure, not a silent one.
    REQUIRED_PLATFORMS = {"Windows", "Linux"}

    def __init__(
        self, version: str, godot_path: Optional[str] = None, project_path: Optional[Path] = None
    ):
        self.version = version
        self.version_num = version.lstrip("v")
        self.repo_root = Path(__file__).parent.parent
        self.godot_dir = project_path or (self.repo_root / "godot")

        # Auto-detect Godot executable
        if godot_path:
            self.godot_exe = Path(godot_path)
        else:
            self.godot_exe = self._find_godot()

        if not self.godot_exe or not self.godot_exe.exists():
            raise FileNotFoundError(
                "Godot executable not found. Please specify --godot-path or install Godot 4.5.1"
            )

        print(f"[*] Using Godot: {self.godot_exe}")
        print(f"[*] Project directory: {self.godot_dir}")
        print(f"[*] Version: {self.version}")

    def _find_godot(self) -> Optional[Path]:
        """Try to auto-detect Godot executable location."""
        common_paths = [
            Path("C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe"),
            Path("C:/Program Files/Godot/Godot.exe"),
            Path.home() / "Godot" / "Godot_v4.5.1-stable_win64.exe",
            Path("/usr/bin/godot"),
            Path("/usr/local/bin/godot"),
            Path("/Applications/Godot.app/Contents/MacOS/Godot"),
        ]

        for path in common_paths:
            if path.exists():
                return path

        # Try to find in PATH
        try:
            result = subprocess.run(
                ["where" if os.name == "nt" else "which", "godot"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return Path(result.stdout.strip().split("\n")[0])
        except Exception:
            pass

        return None

    def _stamp_build(self) -> bool:
        """Refresh godot/build_stamp.txt so it names the commit actually being built.

        The committed stamp is structurally always stale: it is written BY a build
        and committed AFTER it, so the value at any SHA describes the PREVIOUS
        build. Only re-stamping at export time can make it right. build_release.py
        (local builds) already does this; this method mirrors it for the CI path
        (enhanced-release.yml -> this script), which previously shipped whatever
        stamp happened to be committed -- the public v0.13.2 release displayed
        fd60eb6 / 2026-07-11 from a dead feature branch (issue #1067).

        Runs tools/write_build_stamp.py, which stamps from `git rev-parse HEAD`
        of the checked-out ref. Blocking: a stale provenance display is the very
        defect this exists to prevent, so failure fails the build loudly.
        """
        stamp_tool = self.repo_root / "tools" / "write_build_stamp.py"
        if not stamp_tool.exists():
            print(f"[ERROR] Missing {stamp_tool} -- the build would ship a stale stamp")
            return False
        result = subprocess.run([sys.executable, str(stamp_tool)], check=False)
        if result.returncode != 0:
            print("[ERROR] write_build_stamp.py failed -- refusing to ship a stale-stamped build")
            return False
        return True

    def _update_export_paths(self):
        """Update export_presets.cfg with current version paths."""
        export_presets = self.godot_dir / "export_presets.cfg"

        if not export_presets.exists():
            raise FileNotFoundError(f"Export presets not found: {export_presets}")

        with open(export_presets, encoding="utf-8") as f:
            content = f.read()

        # Update paths for each platform
        replacements = [
            (
                r'export_path="../builds/windows/v[^/]+/PDoom.exe"',
                f'export_path="../builds/windows/{self.version}/PDoom.exe"',
            ),
            (
                r'export_path="../builds/linux/v[^/]+/PDoom.x86_64"',
                f'export_path="../builds/linux/{self.version}/PDoom.x86_64"',
            ),
            (
                r'export_path="../builds/mac/v[^/]+/PDoom.app.zip"',
                f'export_path="../builds/mac/{self.version}/PDoom.app.zip"',
            ),
        ]

        import re

        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)

        with open(export_presets, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[+] Updated export paths to version {self.version}")

    def _build_release_cmd(self, preset_name: str, build_dir: Path) -> list:
        """Command line for one tools/build_release.py invocation."""
        return [
            sys.executable,
            str(self.repo_root / "tools" / "build_release.py"),
            "--preset",
            preset_name,
            "--output",
            str(build_dir),
            "--godot-path",
            str(self.godot_exe),
            "--project",
            str(self.godot_dir),
        ]

    def export_platform(self, preset_name: str, platform_name: str, build_dir: Path) -> bool:
        """Export one platform VIA tools/build_release.py (issue #1069).

        build_release.py is the single build discipline: it nukes godot/.godot
        (stale .godot/exported cache defeat), stamps the build, exports, and
        exits non-zero unless a unique freshness marker is PROVEN present in
        the exported .pck/zip. The output filename comes from the preset's own
        export_path (issue #1072), so --output <dir> is all we pass.
        """
        print(f"\n[*] Building {platform_name} via tools/build_release.py ...")

        cmd = self._build_release_cmd(preset_name, build_dir)
        try:
            # Deliberately NOT capture_output: the [BUILD-VERIFY] marker proof
            # must be readable in the CI log, or the proof proves nothing to
            # anyone auditing the run.
            result = subprocess.run(cmd, check=False)
        except Exception as e:
            print(f"[ERROR] Exception during {platform_name} build: {e}")
            result = None

        if result is not None and result.returncode == 0:
            print(f"[SUCCESS] {platform_name} build completed and freshness-verified")
            return True

        code = result.returncode if result is not None else "exception"
        print(f"[ERROR] {platform_name} build failed (build_release.py exit: {code})")
        # A build_release.py failure can happen AFTER the export wrote files
        # (e.g. the freshness check missed). Clear the output dir so a stale
        # or unverified artifact can never be packaged or uploaded.
        if build_dir.exists():
            shutil.rmtree(build_dir, ignore_errors=True)
            build_dir.mkdir(parents=True, exist_ok=True)
            print(f"[*] Cleared {build_dir} -- no unverified artifact may be packaged")
        return False

    def build_all(self) -> bool:
        """Build all platforms via tools/build_release.py, then package zips.

        Returns True iff every REQUIRED platform (Windows, Linux) exported,
        proved its freshness marker, and packaged. macOS is best-effort: its
        failure is loud but non-blocking (see REQUIRED_PLATFORMS).
        """
        print("\n" + "=" * 60)
        print("P(Doom) Multi-Platform Build (via tools/build_release.py)")
        print("=" * 60)

        # Stamp BEFORE any export so the packed godot/build_stamp.txt names this
        # ref, not whatever a previous build committed (issue #1067).
        # build_release.py re-stamps per invocation (same HEAD, idempotent);
        # this early call also fails fast if the stamp tool is broken.
        if not self._stamp_build():
            return False

        # Update export paths first
        self._update_export_paths()

        platforms = [
            ("Windows Desktop", "Windows", "windows"),
            ("Linux/X11", "Linux", "linux"),
            ("macOS", "macOS", "mac"),
        ]

        results = {}
        # SEQUENTIAL ON PURPOSE: every build_release.py run deletes
        # godot/.godot to defeat the stale-export cache, so parallel exports
        # would destroy each other's import caches mid-flight. Do not
        # "optimize" this loop into concurrent builds.
        for preset_name, platform_name, platform_key in platforms:
            build_dir = self.repo_root / "builds" / platform_key / self.version
            build_dir.mkdir(parents=True, exist_ok=True)
            print(f"[+] Build directory: {build_dir}")
            results[platform_name] = self.export_platform(preset_name, platform_name, build_dir)

        # Print summary
        print("\n" + "=" * 60)
        print("Build Summary")
        print("=" * 60)

        for platform, success in results.items():
            status = "[SUCCESS]" if success else "[FAILED]"
            tier = "" if platform in self.REQUIRED_PLATFORMS else " (best-effort, issue #1071)"
            print(f"  {status} {platform}{tier}")

        required_failed = [
            p for p, ok in results.items() if not ok and p in self.REQUIRED_PLATFORMS
        ]
        best_effort_failed = [
            p for p, ok in results.items() if not ok and p not in self.REQUIRED_PLATFORMS
        ]

        if required_failed:
            print(f"\n[ERROR] Required platform build(s) failed: {', '.join(required_failed)}")
            print(
                "[ERROR] Refusing to package ANYTHING -- a half-built release is worse than none."
            )
            return False

        for p in best_effort_failed:
            print(f"\n[WARNING] Best-effort platform FAILED: {p} (issue #1071).")
            print("          Its assets will be MISSING from this release. The release")
            print("          workflow's alias check (PDoom.app.zip must answer 200) will")
            print("          turn the run red after Windows/Linux publish -- that red is")
            print("          the intended loud signal, not a flake.")
            # GitHub Actions annotation: visible on the run summary page even
            # though this step exits 0. Plain print noise in a local run.
            print(
                f"::warning::{p} build failed (best-effort, issue #1071); "
                "its release assets will be missing and verify-release-urls will fail."
            )

        # Create distribution ZIPs for the platforms that built and verified.
        zip_success = self.zip_builds()
        if not zip_success:
            print("\n[ERROR] ZIP packaging failed -- refusing to ship incomplete zips")
            return False

        print(
            f"\n[SUCCESS] Required platforms built, verified fresh, and packaged for {self.version}"
        )
        print(f"\nBuilds location: {self.repo_root / 'builds'}")
        return True

    def _release_note(self, platform_key: str) -> Optional[Path]:
        """Per-platform HOW-TO-RUN template shipped inside each zip."""
        note = self.repo_root / "tools" / "release_notes" / f"HOW-TO-RUN-{platform_key}.txt"
        if not note.exists():
            print(f"[ERROR] Missing release note template: {note}")
            return None
        return note

    def _zip_native_build(
        self,
        build_dir: Path,
        zip_path: Path,
        exe_name: str,
        lib_glob: str,
        expected_libs: list,
        platform_key: str,
    ) -> bool:
        """Zip a Windows/Linux build dir: exe + pck + GDExtension libs + HOW-TO-RUN.

        Includes every lib matching lib_glob that the export laid down beside the
        executable, and fails if any expected GodotSteam library is absent.
        """
        ok = True
        files = [build_dir / exe_name, build_dir / "PDoom.pck"]
        files.extend(sorted(build_dir.glob(lib_glob)))

        missing = [n for n in expected_libs if not (build_dir / n).exists()]
        if missing:
            print(f"[ERROR] {build_dir} is missing expected GDExtension libraries: {missing}")
            print("        The shipped game would fail to load GodotSteam. Aborting package.")
            ok = False

        note = self._release_note(platform_key)
        if note is None:
            ok = False

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                if f.exists():
                    zf.write(f, f.name)
                    print(f"    + {f.name}")
                else:
                    print(f"[ERROR] Expected build output missing: {f}")
                    ok = False
            if note is not None:
                zf.write(note, "HOW-TO-RUN.txt")
                print("    + HOW-TO-RUN.txt")

        size_mb = zip_path.stat().st_size / (1024 * 1024)
        status = "[SUCCESS]" if ok else "[ERROR]"
        print(f"{status} Created {zip_path.name} ({size_mb:.1f} MB)")
        return ok

    def zip_builds(self) -> bool:
        """Create distribution ZIPs for each platform."""
        print("\n" + "=" * 60)
        print("Creating Distribution Packages")
        print("=" * 60)

        success = True

        # Windows: ZIP exe + pck + GodotSteam DLLs + HOW-TO-RUN
        windows_dir = self.repo_root / "builds" / "windows" / self.version
        if windows_dir.exists():
            zip_path_versioned = windows_dir / f"PDoom-Windows-{self.version}.zip"
            zip_path_simple = windows_dir / "PDoom-Windows.zip"
            try:
                if not self._zip_native_build(
                    windows_dir,
                    zip_path_versioned,
                    "PDoom.exe",
                    "*.dll",
                    self.EXPECTED_WINDOWS_LIBS,
                    "windows",
                ):
                    success = False

                # Also create simple-named zip for website compatibility
                shutil.copy2(zip_path_versioned, zip_path_simple)
                print(f"[SUCCESS] Created {zip_path_simple.name} (copy for website)")
            except Exception as e:
                print(f"[ERROR] Failed to create Windows ZIP: {e}")
                success = False

        # Linux: ZIP executable + pck + GodotSteam .so libs + HOW-TO-RUN
        #
        # The unversioned PDoom-Linux.zip alias is REQUIRED, not a nicety (issue
        # #1068). The website's download buttons are fixed strings against
        # releases/latest/download/<name>, which resolves only if the release
        # flagged Latest carries an asset with exactly that name. Windows has had
        # PDoom-Windows.zip and macOS has had PDoom.app.zip since the versioned-zip
        # pipeline landed; Linux never got one, so the site's Linux button 404'd
        # across every release and nobody noticed (a user who cannot download
        # cannot report it in-game). A convention applied to two of three platforms
        # is not a convention, it is two special cases.
        linux_dir = self.repo_root / "builds" / "linux" / self.version
        if linux_dir.exists():
            zip_path_versioned = linux_dir / f"PDoom-Linux-{self.version}.zip"
            zip_path_simple = linux_dir / "PDoom-Linux.zip"
            try:
                if not self._zip_native_build(
                    linux_dir,
                    zip_path_versioned,
                    "PDoom.x86_64",
                    "*.so",
                    self.EXPECTED_LINUX_LIBS,
                    "linux",
                ):
                    success = False

                # Also create simple-named zip for website compatibility
                shutil.copy2(zip_path_versioned, zip_path_simple)
                print(f"[SUCCESS] Created {zip_path_simple.name} (copy for website)")
            except Exception as e:
                print(f"[ERROR] Failed to create Linux ZIP: {e}")
                success = False

        # macOS: the export emits PDoom.app.zip directly, with the GodotSteam
        # framework + libsteam_api.dylib already embedded in Contents/Frameworks/
        # (verified against the CI-built v0.13.1 asset). Verify that, add
        # HOW-TO-RUN.txt beside the .app inside the zip, then copy to the
        # versioned name.
        #
        # BEST-EFFORT (issues #1069/#1071): a macOS packaging problem must not
        # block Windows/Linux from shipping, but a broken bundle must never
        # ship either -- so on ANY problem the macOS zips are DELETED (loudly)
        # and `success` is left alone. The missing PDoom.app.zip asset then
        # turns the release workflow's alias check red.
        mac_dir = self.repo_root / "builds" / "mac" / self.version
        old_mac_zip = mac_dir / "PDoom.app.zip"
        new_mac_zip = mac_dir / f"PDoom-macOS-{self.version}.zip"
        if old_mac_zip.exists():
            mac_ok = True
            try:
                with zipfile.ZipFile(old_mac_zip, "a", zipfile.ZIP_DEFLATED) as zf:
                    names = zf.namelist()
                    frameworks = [n for n in names if "/Contents/Frameworks/" in n]
                    if not frameworks:
                        print(
                            "[ERROR] macOS .app bundle has no Contents/Frameworks/ -- "
                            "GodotSteam GDExtension was not embedded by the export"
                        )
                        mac_ok = False
                    else:
                        print(f"[INFO] macOS bundle embeds {len(frameworks)} Frameworks/ entries")
                    note = self._release_note("macos")
                    if note is None:
                        mac_ok = False
                    elif "HOW-TO-RUN.txt" not in names:
                        zf.write(note, "HOW-TO-RUN.txt")
                        print("    + HOW-TO-RUN.txt (added beside the .app inside the zip)")

                if mac_ok:
                    # Copy (overwrite) so the versioned zip matches the updated one
                    shutil.copy2(old_mac_zip, new_mac_zip)
                    size_mb = new_mac_zip.stat().st_size / (1024 * 1024)
                    print(f"[SUCCESS] Created {new_mac_zip.name} ({size_mb:.1f} MB)")
            except Exception as e:
                print(f"[ERROR] Failed to package macOS ZIP: {e}")
                mac_ok = False

            if not mac_ok:
                for stale in (old_mac_zip, new_mac_zip):
                    if stale.exists():
                        stale.unlink()
                        print(f"[*] Deleted {stale.name} -- a broken macOS bundle must not ship")
                print("[WARNING] macOS packaging failed (best-effort); its assets are dropped.")
                print(
                    "::warning::macOS packaging failed (best-effort, issue #1071); "
                    "PDoom.app.zip will be missing and verify-release-urls will fail."
                )
        else:
            print(
                "[INFO] No macOS PDoom.app.zip present -- skipping macOS packaging "
                "(best-effort platform; expected when the macOS export failed, issue #1071)"
            )

        return success

    def list_builds(self):
        """List all created builds."""
        builds_dir = self.repo_root / "builds"

        if not builds_dir.exists():
            print("[INFO] No builds directory found")
            return

        print("\n" + "=" * 60)
        print("Available Builds")
        print("=" * 60)

        for platform_dir in builds_dir.iterdir():
            if platform_dir.is_dir():
                print(f"\n{platform_dir.name.upper()}:")
                for version_dir in sorted(platform_dir.iterdir(), reverse=True):
                    if version_dir.is_dir():
                        files = list(version_dir.glob("*"))
                        file_list = ", ".join(f.name for f in files)
                        print(f"  {version_dir.name}: {file_list}")


def main():
    parser = argparse.ArgumentParser(
        description="Build P(Doom) for all platforms (Windows, Linux, macOS)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/build_all_platforms.py --version v0.10.1
  python scripts/build_all_platforms.py --version v0.10.1 --list
  python scripts/build_all_platforms.py --version v0.10.1 --godot-path "C:/Godot/Godot.exe"
        """,
    )

    parser.add_argument(
        "--version", type=str, required=True, help="Version to build (e.g., v0.10.1)"
    )
    parser.add_argument(
        "--godot-path", type=str, help="Path to Godot executable (auto-detected if not provided)"
    )
    parser.add_argument(
        "--project-path", type=Path, help="Path to Godot project directory (default: ./godot)"
    )
    parser.add_argument("--list", action="store_true", help="List available builds and exit")

    args = parser.parse_args()

    try:
        builder = MultiPlatformBuilder(args.version, args.godot_path, args.project_path)

        if args.list:
            builder.list_builds()
            return 0

        success = builder.build_all()
        return 0 if success else 1

    except Exception as e:
        print(f"[ERROR] Build failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
