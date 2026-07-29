# !/usr/bin/env python3
"""
Generate release metadata for website integration.

This script creates JSON and RSS feeds for game releases that can be
consumed by the pdoom.net website. It extracts version information,
changelog entries, and download links to make releases easily discoverable.

Usage:
    python scripts/generate_release_metadata.py --version v0.10.1
    python scripts/generate_release_metadata.py --latest
    python scripts/generate_release_metadata.py --version v0.10.1 --verify

--verify HEADs every generated download URL (via scripts/verify_release_urls.py)
after writing the files and exits nonzero on any non-200. This is the same
check CI runs (blocking) after a release's assets are uploaded -- use it
locally to catch a generator/build-pipeline mismatch before pushing a tag.
"""

import argparse
import datetime
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from typing import Dict, List, Optional
from xml.dom import minidom

# Matches vMAJOR.MINOR.PATCH with an optional suffix, e.g. v0.13.1 or v0.2.12-hotfix.
_TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)(?:[-.](.+))?$")


def _ascii_safe(text: str) -> str:
    """Strip non-ASCII from generated feed text.

    The repo enforces ASCII-only in .json (issue #744) and the feed files are
    tracked, so any non-ASCII the generator copies out of git tag messages or
    CHANGELOG.md blocks the commit. Historical tag messages contain emoji and
    mojibake (U+00F0, U+00EF -- lone leading bytes of UTF-8 emoji sequences),
    which is what made the regenerated index unstageable.

    """
    if not text:
        return text
    # Deliberately a plain strip with no transliteration table: this file is itself
    # under the ASCII-only gate (#744), so a table of smart quotes and em dashes
    # written as literals would fail the very check it exists to satisfy. Feed text
    # is metadata, not prose, so losing the occasional dash costs nothing.
    return "".join(ch for ch in text if ord(ch) < 128)


def _semver_sort_key(tag: str):
    """Sort key ordering version tags by NUMERIC semver, not string order.

    Returns (major, minor, patch, is_final, suffix). `is_final` puts a bare
    vX.Y.Z ahead of vX.Y.Z-something at the same numeric version, so a suffixed
    tag never outranks the release it patches. Unparseable tags sort last rather
    than raising, so a stray tag cannot break a release run.
    """
    match = _TAG_RE.match(tag)
    if not match:
        return (-1, -1, -1, 0, tag)
    major, minor, patch, suffix = match.groups()
    return (int(major), int(minor), int(patch), 0 if suffix else 1, suffix or "")


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
            "changelog": _ascii_safe(changelog),
            # Asset names must match what scripts/build_all_platforms.py actually
            # produces and enhanced-release.yml actually uploads (build-windows/
            # **/*.zip, build-linux/**/*.zip, build-mac/**/*.zip) -- NOT a guessed
            # shape. Verified against the real v0.13.1 release asset list
            # (issue #963: PDoom.exe / PDoom.x86_64 / pdoom-*-source.* were all
            # 404s because no such assets are ever produced).
            "downloads": {
                "windows": f"{base_url}/PDoom-Windows-{version}.zip",
                "linux": f"{base_url}/PDoom-Linux-{version}.zip",
                "mac": f"{base_url}/PDoom-macOS-{version}.zip",
                # GitHub auto-generates these codeload archives for every tag;
                # they are not uploaded release assets, so this URL shape works
                # even though no matching file appears in `gh release view`.
                "source_zip": f"https://github.com/{github_repo}/archive/refs/tags/{version}.zip",
                "source_tar": f"https://github.com/{github_repo}/archive/refs/tags/{version}.tar.gz",
            },
            "metadata": {
                "engine": "Godot 4.5.1",
                "platforms": ["Windows", "Linux", "macOS"],
                "tag_message": _ascii_safe(tag_info.get("message", "")),
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
            # Sort by SEMVER, newest first. A plain string sort is WRONG here and was the
            # live bug: "v0.9.0" > "v0.13.1" lexicographically (9 > 1 at the third char), so
            # the feed reported v0.9.0 as `latest_version` from v0.10.0 onward. The website
            # consumes this index, so the bug was player-visible.
            tags.sort(key=_semver_sort_key, reverse=True)
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

    def generate_all_metadata(self, specific_version: Optional[str] = None) -> List[Path]:
        """Generate all metadata files. Returns the list of individual
        per-release JSON files written (used by --verify)."""
        print("[*] Generating release metadata for P(Doom)...")

        # Get all release tags
        if specific_version:
            tags = [specific_version]
        else:
            tags = self.get_all_release_tags()

        if not tags:
            print("[!] No release tags found!")
            return []

        print(f"[*] Found {len(tags)} release(s)")

        # Generate metadata for each release
        releases = []
        release_files: List[Path] = []
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
                release_files.append(release_file)

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

        return release_files


def _run_check(generator: "ReleaseMetadataGenerator", repo_root: Path) -> int:
    """Compare the TRACKED releases index against the git tags. Write nothing.

    Deliberately compares SEMANTICS (which releases are listed, in what order, and
    which is latest) rather than bytes: the generated files carry a `generated_at`
    timestamp that changes every run, so a byte comparison would fail constantly
    and train everyone to bypass the hook.
    """
    index_path = repo_root / "public" / "releases" / "releases.json"
    if not index_path.exists():
        print(f"[check] MISSING {index_path}")
        print("[check] Run: python scripts/generate_release_metadata.py")
        return 1

    expected = generator.get_all_release_tags()
    try:
        tracked = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[check] UNREADABLE {index_path}: {exc}")
        return 1

    actual = [str(r.get("version", "")) for r in tracked.get("releases", [])]
    problems: List[str] = []

    if actual != expected:
        missing = [t for t in expected if t not in actual]
        extra = [t for t in actual if t not in expected]
        if missing:
            problems.append(f"missing from index: {', '.join(missing)}")
        if extra:
            problems.append(f"in index but not a git tag: {', '.join(extra)}")
        if not missing and not extra:
            problems.append("index is ordered differently from the semver tag order")

    expected_latest = expected[0] if expected else None
    if tracked.get("latest_version") != expected_latest:
        problems.append(
            f"latest_version is {tracked.get('latest_version')!r}, expected {expected_latest!r}"
        )

    if problems:
        print("[check] Release index is stale:")
        for problem in problems:
            print(f"  - {problem}")
        print("[check] Fix: python scripts/generate_release_metadata.py")
        print("[check] (Expected right after tagging a release -- regenerate and commit.)")
        return 1

    print(f"[check] Release index matches {len(expected)} git tags; latest={expected_latest}")
    return 0


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
    parser.add_argument(
        "--verify",
        action="store_true",
        help="After generating, HEAD every download URL and exit nonzero on any non-200 "
        "(see scripts/verify_release_urls.py)",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Write nothing. Exit 1 if the tracked releases index disagrees with the git "
        "tags (missing/extra releases, or a wrong latest_version). Gates pre-commit + CI, "
        "mirroring sync_version.py --check and generate_dq_index.py --check.",
    )

    args = parser.parse_args()

    # Find repository root
    repo_root = Path(__file__).parent.parent

    generator = ReleaseMetadataGenerator(repo_root)

    if args.check:
        sys.exit(_run_check(generator, repo_root))

    generated_files: List[Path] = []
    if args.latest and not args.version:
        # Get latest tag
        tags = generator.get_all_release_tags()
        if tags:
            generated_files = generator.generate_all_metadata(specific_version=tags[0])
        else:
            print("WARNING  No release tags found!")
    else:
        generated_files = generator.generate_all_metadata(specific_version=args.version)

    if args.verify:
        sys.path.insert(0, str(Path(__file__).parent))
        import verify_release_urls  # noqa: E402  (deliberate late import, sys.path just set)

        print("\n[*] --verify: checking generated download URLs resolve...")
        exit_code = 0
        for release_file in generated_files:
            exit_code = max(exit_code, verify_release_urls.cmd_file(release_file))
        if exit_code != 0:
            sys.exit(exit_code)


if __name__ == "__main__":
    main()
