# !/usr/bin/env python3
"""
Generate release metadata for website integration.

Layer: GENERATE

This script creates JSON and RSS feeds for game releases that can be
consumed by the pdoom.net website. It extracts version information,
changelog entries, and download links to make releases easily discoverable.

A platform appears in a feed entry ONLY when its asset was OBSERVED to exist --
see the PLATFORMS table and AssetEvidence below. Asset presence comes either
from a local build-artifact directory (--assets-dir, what CI has before the
release is published) or from the GitHub Releases API. When neither can answer,
the platform is reported `unknown` and NO url is emitted.

Usage:
    python scripts/generate_release_metadata.py --version v0.10.1
    python scripts/generate_release_metadata.py --latest
    python scripts/generate_release_metadata.py --version v0.10.1 --verify
    python scripts/generate_release_metadata.py --version v0.14.4 --assets-dir build-artifacts
    python scripts/generate_release_metadata.py --no-probe   # offline: all UNKNOWN

--verify HEADs every generated download URL (via scripts/verify_release_urls.py)
after writing the files and exits nonzero on any non-200. This is the same
check CI runs (blocking) after a release's assets are uploaded -- use it
locally to catch a generator/build-pipeline mismatch before pushing a tag.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set
from xml.dom import minidom

# Matches vMAJOR.MINOR.PATCH with an optional suffix, e.g. v0.13.1 or v0.2.12-hotfix.
_TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)(?:[-.](.+))?$")

GITHUB_REPO = "PipFoweraker/pdoom1"
_API_TIMEOUT_SECONDS = 15.0

# --- The platform asset contract ---------------------------------------------
# (key, human label, asset filename template). These are the names
# scripts/build_all_platforms.py actually produces and enhanced-release.yml
# actually uploads -- NOT a guessed shape.
#
# The load-bearing rule, and the reason this table exists separately from the
# URL builder: a feed entry for a platform is DERIVED FROM AN OBSERVED ASSET,
# never from the naming convention alone.
#
# Issue #963 was the first shape of that bug: PDoom.exe / PDoom.x86_64 /
# pdoom-*-source.* were hardcoded into every release JSON and 404'd against
# every real release, because no such asset was ever produced.
#
# RULING: 2026-08-24 -- a published release artifact states a platform shipped only by enumerating an asset that exists, never by a naming convention or a hardcoded list, and where presence cannot be observed it says UNKNOWN instead of advertising a URL -- flavour: release-artifacts -- mechanism: generate_release_metadata.audit_advertised_platforms and generate_release_manifest.derive_platforms
#
# v0.14.3 (2026-08-24) was the second shape, and the convention was RIGHT this
# time -- the asset simply never arrived. macOS is a deliberately best-effort
# platform (issue #1071: the GodotSteam .framework loses its Versions/Current
# symlink on non-mac checkouts), its export failed, build_all_platforms.py
# dropped the macOS zips exactly as designed, Windows/Linux published exactly
# as designed -- and the feed advertised PDoom-macOS-v0.14.3.zip anyway. A live
# 404 in a public feed, on the day the download link was going out by email.
# The build pipeline knew. The feed generator was never told.
PLATFORMS = (
    ("windows", "Windows", "PDoom-Windows-{version}.zip"),
    ("linux", "Linux", "PDoom-Linux-{version}.zip"),
    ("mac", "macOS", "PDoom-macOS-{version}.zip"),
)

# The unversioned alias each platform ALSO publishes. Issue #1068: the website's
# download buttons are fixed strings against releases/latest/download/<name>, a
# second distribution path the versioned feed never covered. Kept beside
# PLATFORMS so exactly ONE place in the repo knows what a platform's assets are
# called -- scripts/generate_release_manifest.py imports it rather than keeping
# a second opinion, which is how the manifest came to declare a macOS build for
# v0.14.3 while its own file list showed only Windows and Linux.
PLATFORM_ALIASES = {
    "windows": "PDoom-Windows.zip",
    "linux": "PDoom-Linux.zip",
    "mac": "PDoom.app.zip",
}


def platform_assets_for(version: str) -> Dict[str, List[str]]:
    """Every filename a platform may ship under, versioned name first.

    Two consumers with different needs read this: the feed advertises the
    versioned name only, while the release manifest must RECOGNISE either the
    versioned name or the unversioned alias when deciding whether a platform
    shipped. Both derive from the same table, so they cannot drift apart.
    """
    return {
        key: [template.format(version=version)]
        + ([PLATFORM_ALIASES[key]] if key in PLATFORM_ALIASES else [])
        for key, _label, template in PLATFORMS
    }


# Per-platform status values carried in the feed. Three, not two, on purpose.
STATUS_AVAILABLE = "available"  # asset OBSERVED -- the only state that emits a URL
STATUS_NOT_BUILT = "not_built"  # asset list observed, this name absent from it
STATUS_UNKNOWN = "unknown"  # no asset list could be obtained at all


class AssetEvidence:
    """What is KNOWN about which assets a release has, and where that came from.

    Three states per platform, and the third state is the entire point.

    RULING 2026-08-23 (Pip, "manufactured confidence"): a value meaning "I could
    not tell" must never be rendered as a value meaning "fine". Applied here:
    when no asset list can be obtained, every platform reports `unknown` and
    emits NO download URL. An unverifiable platform is not an advertised one.

    `names is None` means UNRESOLVED -- nothing was observed. An EMPTY SET is a
    real observation (a published release that carries no assets) and is a
    different answer; conflating the two is the bug this class exists to make
    unrepresentable.
    """

    def __init__(self, names: Optional[Iterable[str]], source: str, detail: str = ""):
        self.names: Optional[Set[str]] = None if names is None else {str(n) for n in names}
        self.source = source
        self.detail = detail

    @property
    def resolved(self) -> bool:
        """True iff an asset list was actually observed."""
        return self.names is not None

    def status_for(self, asset_name: str) -> str:
        if self.names is None:
            return STATUS_UNKNOWN
        return STATUS_AVAILABLE if asset_name in self.names else STATUS_NOT_BUILT

    def as_dict(self) -> Dict:
        return {"source": self.source, "resolved": self.resolved, "detail": self.detail}


def unresolved_evidence(reason: str) -> AssetEvidence:
    """The honest default: nothing was checked, so nothing is claimed."""
    return AssetEvidence(None, "none", reason)


def evidence_from_directory(assets_dir: Path) -> AssetEvidence:
    """Observe asset names from a local build-artifact tree.

    This is what CI has BEFORE the release exists: generate-feeds runs after
    build-godot, so the downloaded build-* artifacts are the ground truth at
    that moment. Mirrors generate_release_manifest.py --assets-dir.

    A missing/unreadable directory yields UNRESOLVED, not an empty observation:
    "the artifact download step is misconfigured" must not render as "no
    platform was built".
    """
    if not assets_dir.is_dir():
        return AssetEvidence(None, "assets-dir", f"not a directory: {assets_dir}")
    try:
        names = {path.name for path in assets_dir.rglob("*") if path.is_file()}
    except OSError as exc:
        return AssetEvidence(None, "assets-dir", f"unreadable: {assets_dir} ({exc})")
    return AssetEvidence(names, "assets-dir", str(assets_dir))


def evidence_from_github(
    version: str, repo: str = GITHUB_REPO, timeout: float = _API_TIMEOUT_SECONDS
) -> AssetEvidence:
    """Observe asset names from the GitHub Releases API.

    Authoritative once a release is published, which is the case for every tag
    this generator regenerates after the fact. Uses GH_TOKEN/GITHUB_TOKEN when
    present purely for rate limit headroom.

    EVERY failure path -- offline, 404 (tag has no Release object), 403 rate
    limit, garbled payload -- returns UNRESOLVED. Never an empty observed set:
    "I could not ask" and "I asked and there are none" must not collapse into
    one answer, or a rate-limited run would quietly unpublish every platform.
    """
    url = f"https://api.github.com/repos/{repo}/releases/tags/{version}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "pdoom1-release-metadata-generator",
            "Accept": "application/vnd.github+json",
        },
    )
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return AssetEvidence(None, "github-api", f"HTTP {exc.code} from {url}")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return AssetEvidence(None, "github-api", f"unreachable: {exc}")
    except (ValueError, UnicodeDecodeError) as exc:
        return AssetEvidence(None, "github-api", f"unparseable response: {exc}")

    assets = payload.get("assets")
    if not isinstance(assets, list):
        return AssetEvidence(None, "github-api", "response carried no 'assets' list")
    names = [a.get("name", "") for a in assets if isinstance(a, dict)]
    return AssetEvidence(names, "github-api", url)


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


def _report_platform_status(tag: str, platform_status: Dict, evidence: AssetEvidence) -> None:
    """Say out loud what each platform resolved to.

    A silent omission is the failure mode being fixed, so the omission itself
    has to be noisy: dropping macOS from the feed prints a line and, on the CI
    log, a ::warning:: annotation. Nobody should have to diff two feeds to
    notice a platform stopped shipping.
    """
    for key, _label, _template in PLATFORMS:
        entry = platform_status.get(key, {})
        status = entry.get("status", STATUS_UNKNOWN)
        marker = {STATUS_AVAILABLE: "[OK]", STATUS_NOT_BUILT: "[--]", STATUS_UNKNOWN: "[??]"}[
            status
        ]
        print(f"    {marker} {key:8s} {status:10s} {entry.get('asset', '?')}")

    dropped = [k for k, v in platform_status.items() if v.get("status") == STATUS_NOT_BUILT]
    unknown = [k for k, v in platform_status.items() if v.get("status") == STATUS_UNKNOWN]
    if dropped:
        message = (
            f"{tag}: no asset for {', '.join(sorted(dropped))} "
            f"(evidence: {evidence.source}) -- omitted from the feed, NOT advertised"
        )
        print(f"    [!] {message}")
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"::warning::{message}")
    if unknown:
        message = (
            f"{tag}: could not determine asset presence for {', '.join(sorted(unknown))} "
            f"({evidence.detail or 'no evidence source'}) -- reported UNKNOWN, no URL emitted"
        )
        print(f"    [??] {message}")
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"::warning::{message}")


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

    def generate_release_json(
        self, version: str, tag_info: Dict, evidence: Optional[AssetEvidence] = None
    ) -> Dict:
        """Generate JSON metadata for a single release.

        `evidence` says which assets were OBSERVED for this release. Omitting it
        means "nothing was checked", which yields `unknown` for every platform
        and NO download URLs -- deliberately the most conservative default, so a
        caller that forgets to supply evidence under-advertises rather than
        inventing links.
        """
        version_num = version.lstrip("v")
        if evidence is None:
            evidence = unresolved_evidence("no asset evidence supplied to generate_release_json")

        # Extract changelog
        changelog = self.extract_changelog_for_version(version)

        # Determine if it's a prerelease
        is_prerelease = "-" in version or "alpha" in version.lower() or "beta" in version.lower()

        # Generate download URLs (GitHub releases pattern)
        base_url = f"https://github.com/{GITHUB_REPO}/releases/download/{version}"

        # A URL is emitted ONLY for a platform whose asset was observed. The
        # asset name still comes from the PLATFORMS contract -- the convention
        # says what to LOOK FOR; the evidence says whether it is there.
        downloads: Dict[str, str] = {}
        platform_status: Dict[str, Dict] = {}
        available_labels: List[str] = []
        for key, label, template in PLATFORMS:
            asset_name = template.format(version=version)
            status = evidence.status_for(asset_name)
            entry: Dict = {
                "status": status,
                "asset": asset_name,
                "evidence": evidence.source,
            }
            if status == STATUS_AVAILABLE:
                entry["url"] = f"{base_url}/{asset_name}"
                downloads[key] = entry["url"]
                available_labels.append(label)
            platform_status[key] = entry

        # GitHub auto-generates these codeload archives for every tag; they are
        # not uploaded release assets, so this URL shape works even though no
        # matching file appears in `gh release view`. They are therefore NOT
        # gated on asset evidence -- their existence follows from the tag.
        downloads["source_zip"] = (
            f"https://github.com/{GITHUB_REPO}/archive/refs/tags/{version}.zip"
        )
        downloads["source_tar"] = (
            f"https://github.com/{GITHUB_REPO}/archive/refs/tags/{version}.tar.gz"
        )

        release_data = {
            "version": version,
            "version_number": version_num,
            "release_date": tag_info["date"],
            "commit_hash": tag_info["commit"],
            "is_prerelease": is_prerelease,
            "changelog": _ascii_safe(changelog),
            "downloads": downloads,
            # The explicit half of the answer. `downloads` alone cannot tell a
            # consumer WHY a platform is missing; this block distinguishes
            # "not_built" (we looked, it is not there) from "unknown" (we could
            # not look). A consumer that renders a download page can therefore
            # say "macOS: not built for this release" instead of silently
            # dropping a button, and can refuse to guess a URL when the status
            # is unknown.
            "platform_status": platform_status,
            "asset_evidence": evidence.as_dict(),
            "metadata": {
                "engine": "Godot 4.5.1",
                # DERIVED, not declared. This was hardcoded to
                # ["Windows", "Linux", "macOS"] and therefore claimed a macOS
                # build on v0.14.3, which did not exist.
                "platforms": available_labels,
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

    def resolve_evidence(
        self, tag: str, assets_dir: Optional[Path], probe_github: bool
    ) -> AssetEvidence:
        """Pick the asset-observation source for one tag, most local first.

        Order matters: a local --assets-dir is what CI has at feed-generation
        time (the release does not exist yet), and it is the SAME artifact set
        that is about to be uploaded, so it is the closest thing to the truth.
        The API is the fallback for regenerating already-published releases.
        Neither available => unknown, never a guess.
        """
        if assets_dir is not None:
            evidence = evidence_from_directory(assets_dir)
            if evidence.resolved:
                return evidence
            print(f"    [!] assets-dir gave no observation: {evidence.detail}")
            # Fall through: a broken --assets-dir must not silently become
            # "nothing was built"; try the API before giving up to unknown.
        if probe_github:
            evidence = evidence_from_github(tag)
            if evidence.resolved:
                return evidence
            print(f"    [!] GitHub asset probe failed: {evidence.detail}")
            return evidence
        return unresolved_evidence("--no-probe set and no usable --assets-dir")

    def generate_all_metadata(
        self,
        specific_version: Optional[str] = None,
        assets_dir: Optional[Path] = None,
        probe_github: bool = True,
    ) -> List[Path]:
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
                evidence = self.resolve_evidence(tag, assets_dir, probe_github)
                release_data = self.generate_release_json(tag, tag_info, evidence)
                releases.append(release_data)
                _report_platform_status(tag, release_data["platform_status"], evidence)

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

        latest = releases[0] if releases else None
        if latest:
            status = latest["platform_status"]
            shipped = [k for k, v in status.items() if v["status"] == STATUS_AVAILABLE]
            print(
                f"[*] {latest['version']} advertises: "
                f"{', '.join(sorted(shipped)) if shipped else 'NO PLATFORMS'}"
            )

        return release_files


def audit_advertised_platforms(releases: List[Dict]) -> List[str]:
    """Offline invariant: every advertised platform URL is backed by a status.

    Checks the one thing that needs no network and that the v0.14.3 feed
    violated: a `downloads` entry for a platform must correspond to a
    `platform_status` of `available`. A URL for a `not_built` or `unknown`
    platform -- or a URL with no status block at all -- is an advertised 404
    waiting to happen, and this returns it as a problem.

    Returns a list of human-readable problems (empty means clean).
    """
    problems: List[str] = []
    platform_keys = [key for key, _label, _template in PLATFORMS]
    for release in releases:
        version = release.get("version", "?")
        downloads = release.get("downloads", {}) or {}
        status_block = release.get("platform_status")
        if status_block is None:
            problems.append(
                f"{version}: no platform_status block -- cannot tell 'not built' from "
                f"'not checked' (regenerate with the current generator)"
            )
            continue
        for key in platform_keys:
            entry = status_block.get(key, {})
            status = entry.get("status")
            has_url = key in downloads
            if has_url and status != STATUS_AVAILABLE:
                problems.append(
                    f"{version}: advertises a {key} download while platform_status says "
                    f"{status!r} -- a missing asset must never render as a URL"
                )
            if not has_url and status == STATUS_AVAILABLE:
                problems.append(
                    f"{version}: platform_status says {key} is available but no download "
                    f"URL is listed"
                )
    return problems


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

    problems.extend(audit_advertised_platforms(tracked.get("releases", [])))

    if problems:
        print("[check] Release index is stale or self-inconsistent:")
        for problem in problems:
            print(f"  - {problem}")
        print("[check] Fix: python scripts/generate_release_metadata.py")
        print("[check] (Expected right after tagging a release -- regenerate and commit.)")
        return 1

    print(f"[check] Release index matches {len(expected)} git tags; latest={expected_latest}")
    print("[check] Every advertised platform URL is backed by an 'available' status")
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

    parser.add_argument(
        "--assets-dir",
        type=Path,
        help="Directory tree of the release's built assets (e.g. CI's downloaded "
        "build-* artifacts). A platform gets a feed entry ONLY if its asset file "
        "is found here. This is the pre-publication source of truth -- use it in "
        "the release workflow, where the GitHub release does not exist yet.",
    )
    parser.add_argument(
        "--no-probe",
        action="store_true",
        help="Do not ask the GitHub Releases API which assets exist. Without an "
        "--assets-dir this makes every platform UNKNOWN and emits no download "
        "URLs at all -- which is the point: offline means unverified, and "
        "unverified must never render as an advertised link.",
    )

    args = parser.parse_args()

    # Find repository root
    repo_root = Path(__file__).parent.parent

    generator = ReleaseMetadataGenerator(repo_root)

    if args.check:
        sys.exit(_run_check(generator, repo_root))

    probe_github = not args.no_probe
    generated_files: List[Path] = []
    if args.latest and not args.version:
        # Get latest tag
        tags = generator.get_all_release_tags()
        if tags:
            generated_files = generator.generate_all_metadata(
                specific_version=tags[0], assets_dir=args.assets_dir, probe_github=probe_github
            )
        else:
            print("WARNING  No release tags found!")
    else:
        generated_files = generator.generate_all_metadata(
            specific_version=args.version, assets_dir=args.assets_dir, probe_github=probe_github
        )

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
