#!/usr/bin/env python3
"""
Pre-Build Validation Script - Comprehensive Godot Project Testing

Runs before any build or deployment to catch errors early.
Inspired by Python unittest/pytest philosophy but for Godot projects.

Usage:
    python scripts/pre_build_validation.py
    python scripts/pre_build_validation.py --quick    # Fast checks only
    python scripts/pre_build_validation.py --full     # Include slow tests
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class ValidationResult:
    def __init__(self, name: str, passed: bool, message: str = "", duration: float = 0.0):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = duration

class PreBuildValidator:
    def __init__(self, project_root: Path, godot_exe: Path):
        self.project_root = project_root
        self.godot_path = project_root / "godot"
        self.godot_exe = godot_exe
        self.results: List[ValidationResult] = []

    def print_header(self, text: str):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

    def print_result(self, result: ValidationResult):
        status = f"{Colors.GREEN}[PASS]{Colors.END}" if result.passed else f"{Colors.RED}[FAIL]{Colors.END}"
        print(f"{status} {result.name}")
        if result.message:
            print(f"      {result.message}")

    def run_godot_command(self, args: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """Run Godot with arguments and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                [str(self.godot_exe)] + args,
                cwd=str(self.godot_path),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)

    # ==================== FAST CHECKS ====================

    def check_godot_parse_errors(self) -> ValidationResult:
        """Check for GDScript parse errors across all scripts"""
        returncode, stdout, stderr = self.run_godot_command(
            ["--headless", "--quit-after", "1", "project.godot"],
            timeout=15
        )

        output = stdout + stderr
        error_count = output.count("Parse Error")

        if error_count == 0:
            return ValidationResult("GDScript Parse Errors", True, "No parse errors found")
        else:
            errors = [line for line in output.split('\n') if 'Parse Error' in line]
            return ValidationResult(
                "GDScript Parse Errors",
                False,
                f"Found {error_count} parse errors:\n      " + "\n      ".join(errors[:5])
            )

    def check_scene_file_validity(self) -> ValidationResult:
        """Check all .tscn files for structural validity"""
        invalid_scenes = []

        for scene_file in self.godot_path.glob("**/*.tscn"):
            try:
                content = scene_file.read_text(encoding='utf-8')
                lines = content.split('\n')

                # Check ordering: ext_resource -> sub_resource -> node
                found_node = False
                found_sub_after_node = False

                for line in lines:
                    if line.startswith('[node '):
                        found_node = True
                    if found_node and line.startswith('[sub_resource '):
                        found_sub_after_node = True
                        invalid_scenes.append(f"{scene_file.name}: sub_resource after node")
                        break

            except Exception as e:
                invalid_scenes.append(f"{scene_file.name}: {str(e)}")

        if not invalid_scenes:
            return ValidationResult("Scene File Structure", True, "All scene files valid")
        else:
            return ValidationResult(
                "Scene File Structure",
                False,
                f"Found {len(invalid_scenes)} invalid scenes:\n      " + "\n      ".join(invalid_scenes[:5])
            )

    def check_missing_resources(self) -> ValidationResult:
        """Check for missing external resources referenced in scenes"""
        returncode, stdout, stderr = self.run_godot_command(
            ["--headless", "--quit-after", "1", "project.godot"],
            timeout=15
        )

        output = stdout + stderr
        missing_count = output.count("Failed loading resource")

        if missing_count == 0:
            return ValidationResult("Missing Resources", True, "No missing resources")
        else:
            errors = [line for line in output.split('\n') if 'Failed loading resource' in line]
            return ValidationResult(
                "Missing Resources",
                False,
                f"Found {missing_count} missing resources:\n      " + "\n      ".join(errors[:5])
            )

    def check_autoload_scripts(self) -> ValidationResult:
        """Verify all autoload scripts can be loaded"""
        returncode, stdout, stderr = self.run_godot_command(
            ["--headless", "--quit-after", "1", "project.godot"],
            timeout=15
        )

        output = stdout + stderr
        autoload_failures = output.count("Failed to create an autoload")

        if autoload_failures == 0:
            return ValidationResult("Autoload Scripts", True, "All autoloads loaded successfully")
        else:
            errors = [line for line in output.split('\n') if 'autoload' in line.lower() and 'error' in line.lower()]
            return ValidationResult(
                "Autoload Scripts",
                False,
                f"Found {autoload_failures} autoload failures:\n      " + "\n      ".join(errors[:5])
            )

    # ==================== MEDIUM CHECKS ====================

    def run_godot_unit_tests(self) -> ValidationResult:
        """Run all Godot unit tests in tests/ directory"""
        test_dir = self.godot_path / "tests"

        if not test_dir.exists():
            return ValidationResult("Godot Unit Tests", True, "No test directory found (skipped)")

        # Run GUT (Godot Unit Test) if available
        returncode, stdout, stderr = self.run_godot_command(
            ["--headless", "-s", "addons/gut/gut_cmdln.gd"],
            timeout=60
        )

        output = stdout + stderr

        # Parse GUT results
        if "All tests passed" in output or returncode == 0:
            passed_count = output.count("PASSED")
            return ValidationResult("Godot Unit Tests", True, f"{passed_count} tests passed")
        else:
            failed_count = output.count("FAILED")
            return ValidationResult(
                "Godot Unit Tests",
                False,
                f"{failed_count} tests failed"
            )

    def check_exports_configuration(self) -> ValidationResult:
        """Verify export presets are configured correctly"""
        export_presets = self.godot_path / "export_presets.cfg"

        if not export_presets.exists():
            return ValidationResult("Export Configuration", False, "export_presets.cfg not found")

        content = export_presets.read_text()

        # Check for required export presets
        required_presets = ["Windows Desktop", "Linux", "macOS"]
        missing = [p for p in required_presets if p not in content]

        if not missing:
            return ValidationResult("Export Configuration", True, "All export presets configured")
        else:
            return ValidationResult(
                "Export Configuration",
                False,
                f"Missing export presets: {', '.join(missing)}"
            )

    # ==================== SLOW CHECKS ====================

    def test_game_initialization(self) -> ValidationResult:
        """Test that the game can initialize and reach welcome screen"""
        returncode, stdout, stderr = self.run_godot_command(
            ["--headless", "--quit-after", "5", "scenes/welcome.tscn"],
            timeout=15
        )

        output = stdout + stderr

        # Look for successful initialization messages
        if "[GameConfig]" in output and "ERROR" not in output:
            return ValidationResult("Game Initialization", True, "Game initialized successfully")
        else:
            errors = [line for line in output.split('\n') if 'ERROR' in line]
            return ValidationResult(
                "Game Initialization",
                False,
                f"Initialization failed:\n      " + "\n      ".join(errors[:3])
            )

    def test_scene_transitions(self) -> ValidationResult:
        """Test that key scenes can load without errors"""
        test_scenes = [
            "scenes/welcome.tscn",
            "scenes/pregame_setup.tscn",
            "scenes/config_confirmation.tscn",
        ]

        failed_scenes = []

        for scene in test_scenes:
            returncode, stdout, stderr = self.run_godot_command(
                ["--headless", "--check-only", scene],
                timeout=10
            )

            if returncode != 0 or "ERROR" in (stdout + stderr):
                failed_scenes.append(scene)

        if not failed_scenes:
            return ValidationResult("Scene Transitions", True, f"All {len(test_scenes)} scenes loadable")
        else:
            return ValidationResult(
                "Scene Transitions",
                False,
                f"Failed scenes: {', '.join(failed_scenes)}"
            )

    # ==================== RUNNER ====================

    def run_fast_checks(self):
        """Run fast validation checks (< 30 seconds total)"""
        self.print_header("FAST CHECKS (Parse Errors, Structure, Resources)")

        checks = [
            self.check_godot_parse_errors,
            self.check_scene_file_validity,
            self.check_missing_resources,
            self.check_autoload_scripts,
        ]

        for check in checks:
            result = check()
            self.results.append(result)
            self.print_result(result)

    def run_medium_checks(self):
        """Run medium validation checks (< 2 minutes total)"""
        self.print_header("MEDIUM CHECKS (Unit Tests, Export Config)")

        checks = [
            self.run_godot_unit_tests,
            self.check_exports_configuration,
        ]

        for check in checks:
            result = check()
            self.results.append(result)
            self.print_result(result)

    def run_slow_checks(self):
        """Run slow validation checks (< 5 minutes total)"""
        self.print_header("SLOW CHECKS (Game Initialization, Scene Loading)")

        checks = [
            self.test_game_initialization,
            self.test_scene_transitions,
        ]

        for check in checks:
            result = check()
            self.results.append(result)
            self.print_result(result)

    def print_summary(self):
        """Print final summary of all results"""
        self.print_header("VALIDATION SUMMARY")

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)

        if failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}ALL CHECKS PASSED ({passed}/{total}){Colors.END}")
            print(f"{Colors.GREEN}[OK] Build is ready for deployment{Colors.END}")
            return 0
        else:
            print(f"{Colors.RED}{Colors.BOLD}CHECKS FAILED ({passed}/{total} passed, {failed} failed){Colors.END}")
            print(f"{Colors.RED}[FAIL] Build is NOT ready for deployment{Colors.END}")
            print(f"\n{Colors.YELLOW}Fix the failed checks before proceeding.{Colors.END}")
            return 1

def main():
    parser = argparse.ArgumentParser(description="Pre-Build Validation for Godot Project")
    parser.add_argument("--quick", action="store_true", help="Run only fast checks")
    parser.add_argument("--full", action="store_true", help="Run all checks including slow ones")
    parser.add_argument("--godot", type=Path, help="Path to Godot executable")

    args = parser.parse_args()

    # Determine project root and Godot path
    project_root = Path(__file__).parent.parent

    if args.godot:
        godot_exe = args.godot
    else:
        # Try common Godot locations
        godot_exe = Path("C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe")
        if not godot_exe.exists():
            print(f"{Colors.RED}Error: Godot executable not found{Colors.END}")
            print("Please specify with --godot flag")
            return 1

    validator = PreBuildValidator(project_root, godot_exe)

    # Run checks based on mode
    validator.run_fast_checks()

    if not args.quick:
        validator.run_medium_checks()

    if args.full:
        validator.run_slow_checks()

    return validator.print_summary()

if __name__ == "__main__":
    sys.exit(main())
