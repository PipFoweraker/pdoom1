#!/usr/bin/env python3
"""
Generate release metadata for website integration.

This script creates JSON and RSS feeds for game releases that can be
consumed by the pdoom.net website. It extracts version information,
changelog entries, and download links to make releases easily discoverable.

Usage:
    python scripts/generate_release_metadata.py --version v0.10.1
    python scripts/generate_release_metadata.py --latest
"""

import argparse
import datetime
import json
import subprocess
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from typing import Dict, List, Optional
from xml.dom import minidom


class ReleaseMetadataGenerator:
    """Generates metadata files for game releases."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.output_dir = repo_root / "public" / "releases"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_git_tag_info(self, tag: str) -> Optional[Dict]:
        """Extract information from a git tag."""
        try:
            # Get tag date
            result = subprocess.run(
                ["git", "log", "-1", "--format=%aI", tag],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            date = result.stdout.strip()

            # Get commit hash
            result = subprocess.run(
                ["git", "rev-parse", tag],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            commit_hash = result.stdout.strip()

            # Get tag message if it's an annotated tag
            result = subprocess.run(
                ["git", "tag", "-l", "--format=%(contents)", tag],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            message = result.stdout.strip()

            return {"tag": tag, "date": date, "commit": commit_hash, "message": message}
        except subprocess.CalledProcessError:
            return None

    def extract_changelog_for_version(self, version: str) -> str:
        """Extract changelog section for a specific version."""
        changelog_file = self.repo_root / "CHANGELOG.md"

        if not changelog_file.exists():
            return f"Release {version}\n\nNo changelog available."

        with open(changelog_file, encoding="utf-8") as f:
            content = f.read()

        # Look for version section (remove 'v' prefix if present)
        version_num = version.lstrip("v")

        lines = content.split("\n")
        in_version_section = False
        changelog_lines = []

        for line in lines:
            # Check if we hit the version header
            if line.startswith(f"## [{version_num}]") or line.startswith(f"## {version_num}"):
                in_version_section = True
                continue

            # Stop at next version header
            if in_version_section and line.startswith("## "):
                break

            # Collect lines in the version section
            if in_version_section:
                changelog_lines.append(line)

        changelog_text = "\n".join(changelog_lines).strip()

        if not changelog_text:
            return f"Release {version}\n\nSee CHANGELOG.md for details."

        return changelog_text

    def generate_release_json(self, version: str, tag_info: Dict) -> Dict:
        """Generate JSON metadata for a single release."""
        version_num = version.lstrip("v")

        # Extract changelog
        changelog = self.extract_changelog_for_version(version)

        # Determine if it's a prerelease
        is_prerelease = "-" in version or "alpha" in version.lower() or "beta" in version.lower()

        # Generate download URLs (GitHub releases pattern)
        github_repo = "PipFoweraker/pdoom1"
        base_url = f"https://github.com/{github_repo}/releases/download/{version}"

        release_data = {
            "version": version,
            "version_number": version_num,
            "release_date": tag_info["date"],
            "commit_hash": tag_info["commit"],
            "is_prerelease": is_prerelease,
            "changelog": changelog,
            "downloads": {
                "windows": f"{base_url}/PDoom.exe",
                "linux": f"{base_url}/PDoom.x86_64",
                "mac": f"{base_url}/PDoom.app.zip",
                "source_zip": f"{base_url}/pdoom-{version_num}-source.zip",
                "source_tar": f"{base_url}/pdoom-{version_num}-source.tar.gz",
            },
            "metadata": {
                "engine": "Godot 4.5.1",
                "platforms": ["Windows", "Linux", "macOS"],
                "tag_message": tag_info.get("message", ""),
            },
        }

        return release_data

    def get_all_release_tags(self) -> List[str]:
        """Get all version tags from git."""
        try:
            result = subprocess.run(
                ["git", "tag", "-l", "v*.*.*"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            tags = [line.strip() for line in result.stdout.split("\n") if line.strip()]
            # Sort by version (newest first)
            tags.sort(reverse=True)
            return tags
        except subprocess.CalledProcessError:
            return []

    def generate_releases_index(self, releases: List[Dict]) -> Dict:
        """Generate index of all releases."""
        return {
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "latest_version": releases[0]["version"] if releases else None,
            "latest_stable": next((r["version"] for r in releases if not r["is_prerelease"]), None),
            "releases": releases,
            "total_releases": len(releases),
        }

    def generate_rss_feed(self, releases: List[Dict]) -> str:
        """Generate RSS feed for releases."""
        # Create RSS feed
        rss = ElementTree.Element("rss", version="2.0")
        rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")

        channel = ElementTree.SubElement(rss, "channel")

        # Channel metadata
        ElementTree.SubElement(channel, "title").text = "P(Doom) Game Releases"
        ElementTree.SubElement(channel, "link").text = "https://pdoom.net"
        ElementTree.SubElement(channel, "description").text = (
            "Latest releases of P(Doom) - AI Safety Strategy Game"
        )
        ElementTree.SubElement(channel, "language").text = "en-us"
        ElementTree.SubElement(channel, "lastBuildDate").text = datetime.datetime.now(
            datetime.timezone.utc
        ).strftime("%a, %d %b %Y %H:%M:%S %z")

        # Self-reference
        atom_link = ElementTree.SubElement(channel, "atom:link")
        atom_link.set("href", "https://pdoom.net/releases/releases.rss")
        atom_link.set("rel", "self")
        atom_link.set("type", "application/rss+xml")

        # Add items for each release
        for release in releases[:10]:  # Last 10 releases
            item = ElementTree.SubElement(channel, "item")

            title_text = f"P(Doom) {release['version']}"
            if release["is_prerelease"]:
                title_text += " (Pre-release)"

            ElementTree.SubElement(item, "title").text = title_text
            ElementTree.SubElement(item, "link").text = (
                f"https://github.com/PipFoweraker/pdoom1/releases/tag/{release['version']}"
            )
            ElementTree.SubElement(item, "description").text = (
                release["changelog"][:500] + "..."
                if len(release["changelog"]) > 500
                else release["changelog"]
            )
            ElementTree.SubElement(item, "pubDate").text = datetime.datetime.fromisoformat(
                release["release_date"]
            ).strftime("%a, %d %b %Y %H:%M:%S %z")
            ElementTree.SubElement(item, "guid", isPermaLink="false").text = (
                f"pdoom-release-{release['version']}"
            )

        # Pretty print XML
        xml_string = ElementTree.tostring(rss, encoding="unicode")
        dom = minidom.parseString(xml_string)
        return dom.toprettyxml(indent="  ")

    def generate_all_metadata(self, specific_version: Optional[str] = None):
        """Generate all metadata files."""
        print("[*] Generating release metadata for P(Doom)...")

        # Get all release tags
        if specific_version:
            tags = [specific_version]
        else:
            tags = self.get_all_release_tags()

        if not tags:
            print("[!] No release tags found!")
            return

        print(f"[*] Found {len(tags)} release(s)")

        # Generate metadata for each release
        releases = []
        for tag in tags:
            print(f"  Processing {tag}...")
            tag_info = self.get_git_tag_info(tag)

            if tag_info:
                release_data = self.generate_release_json(tag, tag_info)
                releases.append(release_data)

                # Save individual release file
                release_file = self.output_dir / f"{tag}.json"
                with open(release_file, "w", encoding="utf-8") as f:
                    json.dump(release_data, f, indent=2, ensure_ascii=False)
                print(f"    [+] Generated {release_file.name}")

        # Generate releases index
        index_data = self.generate_releases_index(releases)
        index_file = self.output_dir / "releases.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        print(f"[+] Generated releases index: {index_file}")

        # Generate RSS feed
        rss_content = self.generate_rss_feed(releases)
        rss_file = self.output_dir / "releases.rss"
        with open(rss_file, "w", encoding="utf-8") as f:
            f.write(rss_content)
        print(f"[+] Generated RSS feed: {rss_file}")

        print(f"\n[SUCCESS] Generated metadata for {len(releases)} release(s)")
        print(f"[*] Output directory: {self.output_dir}")
        print(f"[*] Latest version: {index_data['latest_version']}")
        print(f"[*] Latest stable: {index_data['latest_stable']}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate release metadata for website integration"
    )
    parser.add_argument(
        "--version", type=str, help="Specific version to generate metadata for (e.g., v0.10.1)"
    )
    parser.add_argument(
        "--latest", action="store_true", help="Only generate metadata for the latest release"
    )

    args = parser.parse_args()

    # Find repository root
    repo_root = Path(__file__).parent.parent

    generator = ReleaseMetadataGenerator(repo_root)

    if args.latest and not args.version:
        # Get latest tag
        tags = generator.get_all_release_tags()
        if tags:
            generator.generate_all_metadata(specific_version=tags[0])
        else:
            print("⚠️  No release tags found!")
    else:
        generator.generate_all_metadata(specific_version=args.version)


if __name__ == "__main__":
    main()
