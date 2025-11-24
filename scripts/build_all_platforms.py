#!/usr/bin/env python3
"""
Build P(Doom) for all platforms (Windows, Linux, macOS).

This script automates Godot exports for all configured platforms,
making it easy to create releases for distribution.

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

    def export_platform(self, preset_name: str, platform_name: str) -> bool:
        """Export for a specific platform."""
        print(f"\n[*] Building {platform_name}...")

        cmd = [
            str(self.godot_exe),
            "--headless",
            "--export-release",
            preset_name,
            "--path",
            str(self.godot_dir),
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                print(f"[SUCCESS] {platform_name} build completed successfully")
                return True
            else:
                print(f"[ERROR] {platform_name} build failed:")
                print(f"  stdout: {result.stdout}")
                print(f"  stderr: {result.stderr}")
                return False
        except Exception as e:
            print(f"[ERROR] Exception during {platform_name} build: {e}")
            return False

    def build_all(self) -> bool:
        """Build for all platforms."""
        print("\n" + "=" * 60)
        print("P(Doom) Multi-Platform Build")
        print("=" * 60)

        # Update export paths first
        self._update_export_paths()

        # Create build directories
        for platform in ["windows", "linux", "mac"]:
            build_dir = self.repo_root / "builds" / platform / self.version
            build_dir.mkdir(parents=True, exist_ok=True)
            print(f"[+] Created build directory: {build_dir}")

        platforms = [
            ("Windows Desktop", "Windows"),
            ("Linux/X11", "Linux"),
            ("macOS", "macOS"),
        ]

        results = {}
        for preset_name, platform_name in platforms:
            results[platform_name] = self.export_platform(preset_name, platform_name)

        # Print summary
        print("\n" + "=" * 60)
        print("Build Summary")
        print("=" * 60)

        all_success = True
        for platform, success in results.items():
            status = "[SUCCESS]" if success else "[FAILED]"
            print(f"  {status} {platform}")
            if not success:
                all_success = False

        if all_success:
            print(f"\n[SUCCESS] All platforms built successfully for {self.version}")

            # Create distribution ZIPs
            zip_success = self.zip_builds()
            if not zip_success:
                print("\n[WARNING] Some ZIP packaging failed")

            print(f"\nBuilds location: {self.repo_root / 'builds'}")
        else:
            print("\n[WARNING] Some builds failed. Check errors above.")

        return all_success

    def zip_builds(self) -> bool:
        """Create distribution ZIPs for each platform."""
        print("\n" + "=" * 60)
        print("Creating Distribution Packages")
        print("=" * 60)

        success = True

        # Windows: ZIP the .exe and .pck together
        windows_dir = self.repo_root / "builds" / "windows" / self.version
        if windows_dir.exists():
            zip_path_versioned = windows_dir / f"PDoom-Windows-{self.version}.zip"
            zip_path_simple = windows_dir / "PDoom-Windows.zip"
            try:
                # Create versioned zip
                with zipfile.ZipFile(zip_path_versioned, "w", zipfile.ZIP_DEFLATED) as zf:
                    exe_file = windows_dir / "PDoom.exe"
                    pck_file = windows_dir / "PDoom.pck"

                    if exe_file.exists():
                        zf.write(exe_file, "PDoom.exe")
                    if pck_file.exists():
                        zf.write(pck_file, "PDoom.pck")

                size_mb = zip_path_versioned.stat().st_size / (1024 * 1024)
                print(f"[SUCCESS] Created {zip_path_versioned.name} ({size_mb:.1f} MB)")

                # Also create simple-named zip for website compatibility
                shutil.copy2(zip_path_versioned, zip_path_simple)
                print(f"[SUCCESS] Created {zip_path_simple.name} (copy for website)")
            except Exception as e:
                print(f"[ERROR] Failed to create Windows ZIP: {e}")
                success = False

        # Linux: ZIP the executable and .pck
        linux_dir = self.repo_root / "builds" / "linux" / self.version
        if linux_dir.exists():
            zip_path = linux_dir / f"PDoom-Linux-{self.version}.zip"
            try:
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    exe_file = linux_dir / "PDoom.x86_64"
                    pck_file = linux_dir / "PDoom.pck"

                    if exe_file.exists():
                        zf.write(exe_file, "PDoom.x86_64")
                    if pck_file.exists():
                        zf.write(pck_file, "PDoom.pck")

                size_mb = zip_path.stat().st_size / (1024 * 1024)
                print(f"[SUCCESS] Created {zip_path.name} ({size_mb:.1f} MB)")
            except Exception as e:
                print(f"[ERROR] Failed to create Linux ZIP: {e}")
                success = False

        # macOS: Rename existing .zip for consistency
        mac_dir = self.repo_root / "builds" / "mac" / self.version
        old_mac_zip = mac_dir / "PDoom.app.zip"
        new_mac_zip = mac_dir / f"PDoom-macOS-{self.version}.zip"
        if old_mac_zip.exists() and not new_mac_zip.exists():
            try:
                shutil.copy2(old_mac_zip, new_mac_zip)
                size_mb = new_mac_zip.stat().st_size / (1024 * 1024)
                print(f"[SUCCESS] Created {new_mac_zip.name} ({size_mb:.1f} MB)")
            except Exception as e:
                print(f"[ERROR] Failed to rename macOS ZIP: {e}")
                success = False
        elif new_mac_zip.exists():
            size_mb = new_mac_zip.stat().st_size / (1024 * 1024)
            print(f"[INFO] macOS package ready: {new_mac_zip.name} ({size_mb:.1f} MB)")

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
