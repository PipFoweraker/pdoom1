#!/usr/bin/env python3
"""
Bug Report Processing Tool for P(Doom)

This tool processes locally saved bug reports from the in-game bug reporter
and creates GitHub issues via the GitHub API.

Usage:
    python tools/process_bug_reports.py [options]

Options:
    --dry-run       Preview issues without creating them
    --archive       Archive processed reports after successful creation
    --limit N       Process only N reports (default: all)
    --help          Show this help message

Requirements:
    - GitHub CLI (gh) installed and authenticated
    - Bug reports in user data directory (handled by Godot game)

Privacy:
    This tool respects user privacy - only uploads data from reports
    where users have explicitly opted in to submission.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class BugReportProcessor:
    """Process bug reports and create GitHub issues."""

    def __init__(self, dry_run: bool = False, archive: bool = False):
        self.dry_run = dry_run
        self.archive = archive
        self.reports_processed = 0
        self.reports_failed = 0

    def find_bug_reports_directory(self) -> Optional[Path]:
        """
        Find the Godot user data directory containing bug reports.

        Godot stores user:// data in platform-specific locations:
        - Windows: %APPDATA%/Godot/app_userdata/[project_name]/
        - Linux: ~/.local/share/godot/app_userdata/[project_name]/
        - macOS: ~/Library/Application Support/Godot/app_userdata/[project_name]/
        """
        project_name = "pdoom1"  # Update if project name differs

        if sys.platform == "win32":
            base = Path(os.environ.get("APPDATA", "")) / "Godot" / "app_userdata" / project_name
        elif sys.platform == "darwin":
            base = (
                Path.home()
                / "Library"
                / "Application Support"
                / "Godot"
                / "app_userdata"
                / project_name
            )
        else:  # Linux and others
            base = Path.home() / ".local" / "share" / "godot" / "app_userdata" / project_name

        reports_dir = base / "bug_reports"

        if reports_dir.exists():
            return reports_dir

        return None

    def load_bug_report(self, filepath: Path) -> Optional[Dict]:
        """Load and validate a bug report JSON file."""
        try:
            with open(filepath, encoding="utf-8") as f:
                report = json.load(f)

            # Validate required fields
            required_fields = ["report_type", "title", "description", "system_info", "created_at"]
            for field in required_fields:
                if field not in report:
                    print(f"  ⚠ Warning: Missing required field '{field}' in {filepath.name}")
                    return None

            return report

        except json.JSONDecodeError as e:
            print(f"  ✗ Error: Invalid JSON in {filepath.name}: {e}")
            return None
        except Exception as e:
            print(f"  ✗ Error reading {filepath.name}: {e}")
            return None

    def format_github_issue(self, report: Dict) -> Dict[str, str]:
        """Format bug report for GitHub issue creation."""
        # Create title
        issue_type = report["report_type"].replace("_", " ").title()
        title = f"[{issue_type}] {report['title']}"

        # Create body
        body_parts = []

        # Header
        body_parts.append(f"**Type:** {issue_type}")
        body_parts.append("")

        # Description
        body_parts.append("**Description:**")
        body_parts.append(report["description"])
        body_parts.append("")

        # Optional sections
        if "steps_to_reproduce" in report and report["steps_to_reproduce"]:
            body_parts.append("**Steps to Reproduce:**")
            body_parts.append(report["steps_to_reproduce"])
            body_parts.append("")

        if "expected_behavior" in report and report["expected_behavior"]:
            body_parts.append("**Expected Behavior:**")
            body_parts.append(report["expected_behavior"])
            body_parts.append("")

        if "actual_behavior" in report and report["actual_behavior"]:
            body_parts.append("**Actual Behavior:**")
            body_parts.append(report["actual_behavior"])
            body_parts.append("")

        # System information
        body_parts.append("**System Information:**")
        system_info = report["system_info"]
        body_parts.append(f"- OS: {system_info.get('os_type', 'Unknown')}")
        body_parts.append(f"- Godot: {system_info.get('godot_version', 'Unknown')}")
        body_parts.append(f"- Game Version: {system_info.get('game_version', 'Unknown')}")
        body_parts.append(f"- Reported: {system_info.get('timestamp', 'Unknown')}")
        body_parts.append("")

        # Attribution (for contributor recognition)
        if report.get("attribution") and report["attribution"]:
            attribution = report["attribution"]
            body_parts.append(f"**Reported by:** {attribution['name']}")
            if attribution.get("contact"):
                body_parts.append(f"**Contact:** {attribution['contact']}")
        else:
            body_parts.append("**Reported by:** Anonymous")

        # Attachments note
        attachments = report.get("attachments", {})
        if attachments.get("screenshot_included") or attachments.get("save_file_included"):
            body_parts.append("")
            body_parts.append("**Attachments:**")
            if attachments.get("screenshot_included"):
                body_parts.append("- Screenshot: Available in local bug report")
            if attachments.get("save_file_included"):
                body_parts.append("- Save file: Available in local bug report")

        # Footer
        body_parts.append("")
        body_parts.append("---")
        body_parts.append("*Submitted via in-game bug reporter*")

        return {"title": title, "body": "\n".join(body_parts)}

    def create_github_issue(self, report: Dict, issue_data: Dict[str, str]) -> bool:
        """Create a GitHub issue using gh CLI."""
        try:
            # Determine labels based on report type
            labels = ["community-submission"]
            if report["report_type"] == "bug":
                labels.append("bug")
            elif report["report_type"] == "feature_request":
                labels.append("enhancement")
            elif report["report_type"] == "feedback":
                labels.append("feedback")

            # Build gh command
            cmd = [
                "gh",
                "issue",
                "create",
                "--title",
                issue_data["title"],
                "--body",
                issue_data["body"],
                "--label",
                ",".join(labels),
            ]

            if self.dry_run:
                print("\n  [DRY RUN] Would create issue:")
                print(f"  Title: {issue_data['title']}")
                print(f"  Labels: {', '.join(labels)}")
                print(f"  Body preview: {issue_data['body'][:200]}...")
                return True

            # Execute gh command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Extract issue URL from output
            issue_url = result.stdout.strip()
            print(f"  ✓ Created: {issue_url}")

            return True

        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to create issue: {e.stderr}")
            return False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False

    def archive_report(self, filepath: Path) -> bool:
        """Move processed report to archive directory."""
        try:
            archive_dir = filepath.parent / "archive"
            archive_dir.mkdir(exist_ok=True)

            # Add timestamp to archived filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = archive_dir / f"{filepath.stem}_archived_{timestamp}{filepath.suffix}"

            filepath.rename(archive_path)
            print(f"  → Archived to: {archive_path.name}")

            # Also move associated files (screenshots, save files)
            base_name = filepath.stem
            for ext in [".png", ".sav"]:
                assoc_file = filepath.parent / f"{base_name}{ext}"
                if assoc_file.exists():
                    assoc_archive = archive_dir / f"{base_name}_archived_{timestamp}{ext}"
                    assoc_file.rename(assoc_archive)

            return True

        except Exception as e:
            print(f"  ✗ Failed to archive: {e}")
            return False

    def process_reports(self, reports_dir: Path, limit: Optional[int] = None) -> None:
        """Process all bug reports in directory."""
        # Find all bug report JSON files
        report_files = sorted(reports_dir.glob("bug_report_*.json"))

        if not report_files:
            print("No bug reports found.")
            return

        if limit:
            report_files = report_files[:limit]

        print(f"\nFound {len(report_files)} bug report(s) to process\n")

        for filepath in report_files:
            print(f"Processing: {filepath.name}")

            # Load report
            report = self.load_bug_report(filepath)
            if not report:
                self.reports_failed += 1
                continue

            # Format for GitHub
            issue_data = self.format_github_issue(report)

            # Create GitHub issue
            success = self.create_github_issue(report, issue_data)

            if success:
                self.reports_processed += 1

                # Archive if requested and not dry run
                if self.archive and not self.dry_run:
                    self.archive_report(filepath)
            else:
                self.reports_failed += 1

            print()  # Blank line between reports

        # Summary
        print("\n" + "=" * 60)
        print("Summary:")
        print(f"  Processed: {self.reports_processed}")
        print(f"  Failed: {self.reports_failed}")
        print(f"  Total: {len(report_files)}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Process P(Doom) bug reports and create GitHub issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Preview issues without creating them"
    )

    parser.add_argument(
        "--archive", action="store_true", help="Archive processed reports after successful creation"
    )

    parser.add_argument(
        "--limit", type=int, metavar="N", help="Process only N reports (default: all)"
    )

    parser.add_argument(
        "--reports-dir",
        type=Path,
        metavar="PATH",
        help="Path to bug reports directory (default: auto-detect)",
    )

    args = parser.parse_args()

    # Initialize processor
    processor = BugReportProcessor(dry_run=args.dry_run, archive=args.archive)

    # Find or use provided reports directory
    if args.reports_dir:
        reports_dir = args.reports_dir
        if not reports_dir.exists():
            print(f"Error: Directory not found: {reports_dir}")
            sys.exit(1)
    else:
        print("Auto-detecting bug reports directory...")
        reports_dir = processor.find_bug_reports_directory()
        if not reports_dir:
            print("Error: Could not find bug reports directory")
            print("Please specify path with --reports-dir")
            sys.exit(1)

    print(f"Using reports directory: {reports_dir}")

    # Check for gh CLI
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\nError: GitHub CLI (gh) not found or not authenticated")
        print("Please install: https://cli.github.com/")
        print("And authenticate: gh auth login")
        sys.exit(1)

    # Process reports
    processor.process_reports(reports_dir, limit=args.limit)


if __name__ == "__main__":
    main()
