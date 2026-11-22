# !/usr/bin/env python3
"""
Generate release metadata for website integration.

Layer: GENERATE

This script creates JSON and RSS feeds for game releases that can be
consumed by the pdoom.net website. It extracts version information,
changelog entries, and download links to make releases easily discoverable.

TWO KINDS OF ABSENCE ARE REFUSED HERE, and they are independent:

  prose  -- a release with no CHANGELOG section gets `changelog: null` and
            `changelog_status: "missing"`, never a stand-in sentence (#1298).
  files  -- a platform appears in a feed entry ONLY when its asset was
            OBSERVED to exist. Availability comes from build-status.json
            (scripts/check_platform_builds.py, #1307 -- authoritative), or a
            local --assets-dir, or the GitHub Releases API. When none can
            answer, the platform is `unknown` and NO url is emitted.

Usage:
    python scripts/generate_release_metadata.py --version v0.10.1
    python scripts/generate_release_metadata.py --latest
    python scripts/generate_release_metadata.py --version v0.10.1 --verify
    python scripts/generate_release_metadata.py --version v0.14.4 \
        --build-status public/releases/build-status.json
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

sys.path.insert(0, str(Path(__file__).resolve().parent))

# The asset-name contract lives in check_platform_builds.py (issue #1307), which
# is stdlib-only and does no network I/O, so importing it here is cheap and safe.
# Importing rather than restating it is the whole point: two tables of "what a
# platform's zip is called" is exactly the drift that lets a build report and a
# release feed disagree about the same release. That module is AUTHORITATIVE for
# the names, and for the CI availability verdict (see evidence_from_build_status).
import check_platform_builds  # noqa: E402

# Matches vMAJOR.MINOR.PATCH with an optional suffix, e.g. v0.13.1 or v0.2.12-hotfix.
_TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)(?:[-.](.+))?$")

# The two placeholder strings this generator used to emit when it could not find a
# CHANGELOG section. Kept ONLY so --check can recognise them in an index generated
# before 2026-08-24 and call them what they are. Never emitted again.
_RETIRED_PLACEHOLDERS = (
    "See CHANGELOG.md for details.",
    "No changelog available.",
)

# What the feed says INSTEAD of a fabricated release note. Deliberately bracketed and
# machine-obvious: it states the absence rather than papering over it, so a reader of
# the RSS feed can tell "nobody wrote notes" from "this release was quiet".
_ABSENT_MARKER = "[no CHANGELOG.md section for {version} -- release notes were never written]"

# Releases that shipped before the section-per-release convention was enforced, and
# which will therefore never grow a CHANGELOG section retroactively. This is a
# RATCHET in the same spirit as tools/balance_unread_ratchet.txt: entries may be
# REMOVED (by writing the missing section), never added for a new release. A tag that
# is missing a section and is NOT listed here fails the generator and --check.
#
# It is a pin rather than a hard failure because 15 of 25 tags were already missing
# sections when this gate was written -- a gate that is red on arrival gets disabled
# inside a week (the lesson already recorded against action-taxonomy-index-check).
# Pinned gaps are still PRINTED on every run, so they cannot go quiet.
_CHANGELOG_GAP_PIN = "scripts/changelog_gap_pin.txt"

GITHUB_REPO = "PipFoweraker/pdoom1"
_API_TIMEOUT_SECONDS = 15.0

# --- The platform asset contract ---------------------------------------------
# RULING: 2026-08-24 -- a published release artifact states a platform shipped only by enumerating an asset that exists, never by a naming convention or a hardcoded list, and where presence cannot be observed it says UNKNOWN instead of advertising a URL -- flavour: release-artifacts -- mechanism: generate_release_metadata.audit_advertised_platforms and generate_release_manifest.derive_platforms
#
# The feed's own key for macOS is "mac" (it is in the shipped `downloads` block
# and cannot be renamed); check_platform_builds spells it "macos". This map is
# the ONLY place that translation lives.
_FEED_TO_BUILD_KEY = {"windows": "windows", "linux": "linux", "mac": "macos"}


def _platform_contract():
    """(feed_key, label, versioned_template, alias) per platform, from #1307's table.

    Derived, not restated. check_platform_builds.PLATFORMS lists each platform's
    assets as (versioned_template, unversioned_alias) -- the order matters and is
    asserted by a test, because deriving from a tuple whose order silently
    flipped would swap "the URL to advertise" with "the website's button target".
    """
    by_key = {spec["key"]: spec for spec in check_platform_builds.PLATFORMS}
    rows = []
    for feed_key, build_key in _FEED_TO_BUILD_KEY.items():
        spec = by_key[build_key]
        versioned, alias = spec["assets"][0], spec["assets"][1]
        rows.append((feed_key, spec["label"], versioned, alias))
    return tuple(rows)


# (key, human label, versioned asset filename template) -- the shape the rest of
# this module loops over. The load-bearing rule, and the reason this exists at
# all rather than a literal URL builder: a feed entry for a platform is DERIVED
# FROM AN OBSERVED ASSET, never from the naming convention alone.
#
# Issue #963 was the first shape of that bug: PDoom.exe / PDoom.x86_64 were
# hardcoded into every release JSON and 404'd against every real release,
# because no such asset was ever produced.
#
# v0.14.3 (2026-08-24) was the second shape, and the convention was RIGHT this
# time -- the asset simply never arrived. macOS is a deliberately best-effort
# platform, its export failed on a Windows .ico that Godot cannot decode
# (fixed in #1305), build_all_platforms.py dropped the macOS zips exactly as
# designed, Windows/Linux published exactly as designed -- and the feed
# advertised PDoom-macOS-v0.14.3.zip anyway. A live 404 in a public feed, on
# the day the download link was going out by email. The build pipeline knew.
# The feed generator was never told.
PLATFORMS = tuple((key, label, versioned) for key, label, versioned, _alias in _platform_contract())

# The unversioned alias each platform ALSO publishes (issue #1068: the website's
# download buttons are fixed strings against releases/latest/download/<name>).
PLATFORM_ALIASES = {key: alias for key, _label, _versioned, alias in _platform_contract()}


def platform_assets_for(version: str) -> Dict[str, List[str]]:
    """Every filename a platform may ship under, versioned name FIRST.

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

    This is the same principle #1298 applied to CHANGELOG prose in this very
    file -- `changelog: null` + `changelog_status: "missing"` rather than a
    sentence that reads like a release note. Neither subsumes the other: that
    one is about absent PROSE, this one about absent FILES, and a release can
    have either, both, or neither.

    `names is None` means UNRESOLVED -- nothing was observed. An EMPTY SET is a
    real observation (a published release that carries no assets) and is a
    different answer; conflating the two is the bug this class makes
    unrepresentable.
    """

    def __init__(self, names: Optional[Iterable[str]], source: str, detail: str = ""):
        self.names: Optional[Set[str]] = None if names is None else {str(n) for n in names}
        self.source = source
        self.detail = detail
        # Set by evidence_from_build_status: a verdict already reached by the
        # authoritative scanner, which is stricter than a name lookup can be.
        self.verdicts: Optional[Dict[str, bool]] = None

    @property
    def resolved(self) -> bool:
        """True iff an asset list (or a verdict set) was actually observed."""
        return self.names is not None or self.verdicts is not None

    def status_for(self, platform_key: str, asset_name: str) -> str:
        if self.verdicts is not None:
            verdict = self.verdicts.get(platform_key)
            if verdict is None:
                return STATUS_UNKNOWN
            return STATUS_AVAILABLE if verdict else STATUS_NOT_BUILT
        if self.names is None:
            return STATUS_UNKNOWN
        return STATUS_AVAILABLE if asset_name in self.names else STATUS_NOT_BUILT

    def as_dict(self) -> Dict:
        return {"source": self.source, "resolved": self.resolved, "detail": self.detail}


def unresolved_evidence(reason: str) -> AssetEvidence:
    """The honest default: nothing was checked, so nothing is claimed."""
    return AssetEvidence(None, "none", reason)


def evidence_from_build_status(status_path: Path) -> AssetEvidence:
    """Adopt the verdict of scripts/check_platform_builds.py (issue #1307).

    THIS IS THE AUTHORITATIVE SOURCE in CI, and the generator deliberately does
    not form a second opinion. That scanner runs in its own job BEFORE
    generate-feeds, walks the downloaded artefact tree, and is STRICTER than a
    filename lookup can be: it requires BOTH the versioned zip and the
    unversioned alias, and enforces a minimum size, so a truncated or zero-byte
    zip counts as a missing build. Re-deriving availability here from names
    alone would create a second, weaker answer to a question already answered --
    which is precisely the "two tables, one truth" failure this composition
    exists to avoid.

    Any problem reading or parsing the file yields UNRESOLVED, never a verdict.
    """
    if not status_path.is_file():
        return AssetEvidence(None, "build-status", f"no such file: {status_path}")
    try:
        payload = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return AssetEvidence(None, "build-status", f"unreadable {status_path}: {exc}")

    platforms = payload.get("platforms")
    if not isinstance(platforms, dict):
        return AssetEvidence(None, "build-status", "no 'platforms' object in build-status.json")

    verdicts: Dict[str, bool] = {}
    for feed_key, build_key in _FEED_TO_BUILD_KEY.items():
        entry = platforms.get(build_key)
        if isinstance(entry, dict) and isinstance(entry.get("available"), bool):
            verdicts[feed_key] = entry["available"]
    if not verdicts:
        return AssetEvidence(None, "build-status", "no usable per-platform verdicts")

    evidence = AssetEvidence(None, "build-status", str(status_path))
    evidence.verdicts = verdicts
    return evidence


def evidence_from_directory(assets_dir: Path) -> AssetEvidence:
    """Observe asset names from a local build-artifact tree.

    The local/offline fallback for when there is no build-status.json -- a
    developer regenerating feeds by hand against a builds/ directory. CI should
    use --build-status instead, which is stricter.

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

    The source for regenerating ALREADY-PUBLISHED releases, where no
    build-status.json exists and never will (every tag before v0.14.4). Uses
    GH_TOKEN/GITHUB_TOKEN when present purely for rate-limit headroom.

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


def _report_platform_status(tag: str, platform_status: Dict, evidence: AssetEvidence) -> None:
    """Say out loud what each platform resolved to.

    A silent omission is the failure mode being fixed, so the omission itself
    has to be noisy: dropping macOS from the feed prints a line and, on CI, a
    ::warning:: annotation. Nobody should have to diff two feeds to notice a
    platform stopped shipping.
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


def audit_advertised_platforms(releases: List[Dict]) -> List[str]:
    """Offline invariant: every advertised platform URL is backed by a status.

    Checks the one thing that needs no network and that the v0.14.3 feed
    violated: a `downloads` entry for a platform must correspond to a
    `platform_status` of `available`. A URL for a `not_built` or `unknown`
    platform -- or a URL with no status block at all -- is an advertised 404
    waiting to happen, and this returns it as a problem.

    Deliberately parallel to the changelog audit #1298 added to _run_check: same
    function, same gate, one asks "is this prose real" and this asks "is this
    file real".
    """
    problems: List[str] = []
    platform_keys = [key for key, _label, _template in PLATFORMS]
    for release in releases:
        version = release.get("version", "?")
        downloads = release.get("downloads", {}) or {}
        status_block = release.get("platform_status")
        if status_block is None:
            # A MISSING block is not itself the defect, and saying so would fire
            # on every entry of a pre-2026-08-24 index. That is the same call
            # #1298 made one loop above for `changelog_status`, for the same
            # measured reason: a finding that fires on all 23 legacy entries
            # buries the one that matters.
            #
            # What IS still a defect, block or no block, is an ADVERTISED
            # platform URL with nothing backing it. That is precisely the shape
            # the published v0.14.3 feed had -- downloads.mac, no
            # platform_status -- so leniency here must not extend to it.
            advertised = [key for key in platform_keys if key in downloads]
            if advertised:
                problems.append(
                    f"{version}: advertises {', '.join(advertised)} with no platform_status "
                    f"to back it -- regenerate; an unbacked URL is how the v0.14.3 macOS "
                    f"404 shipped"
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


def load_gap_pin(repo_root: Path) -> List[str]:
    """Read the pinned list of tags known to have no CHANGELOG section.

    Absent file = empty pin = every gap is fatal. That is the safe direction: a
    deleted pin makes the gate stricter, never quieter.
    """
    pin_path = repo_root / _CHANGELOG_GAP_PIN
    if not pin_path.exists():
        return []
    pinned = []
    for line in pin_path.read_text(encoding="utf-8").splitlines():
        entry = line.split("#", 1)[0].strip()
        if entry:
            pinned.append(entry)
    return pinned


def is_placeholder_changelog(text: Optional[str]) -> bool:
    """True if `text` is one of the retired manufactured-confidence placeholders.

    Used by --check to name the defect in an index generated before 2026-08-24,
    rather than silently accepting a non-empty string as a real release note.
    """
    if not text:
        return False
    return any(marker in text for marker in _RETIRED_PLACEHOLDERS)


class ReleaseMetadataGenerator:
    """Generates metadata files for game releases."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.output_dir = repo_root / "public" / "releases"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Tags found with no CHANGELOG section and no entry in the gap pin. Populated
        # by generate_all_metadata(); main() exits nonzero on a non-empty list.
        self.unpinned_gaps: List[str] = []

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

            # Get commit hash.
            #
            # `tag^{commit}`, not the bare `tag`, and the suffix is the whole
            # point (2026-08-29). Every release tag in this repo is ANNOTATED,
            # and `git rev-parse <annotated tag>` returns the TAG OBJECT's sha,
            # which is not a commit and does not appear in `git log`. The field
            # it lands in is called `commit_hash` and is published to the
            # website in public/releases/<tag>.json, so the feed has been
            # naming an object that is not the thing the field claims.
            #
            #   git rev-parse v0.14.3            -> 8319ab38  (the tag object)
            #   git rev-parse v0.14.3^{commit}   -> b9f55260  (the commit)
            #   git rev-list -n1 v0.14.3         -> b9f55260
            #
            # `^{commit}` peels a tag object to the commit it points at, and is
            # a no-op on a lightweight tag, so this is correct for both kinds.
            result = subprocess.run(
                ["git", "rev-parse", tag + "^{commit}"],
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

    def extract_changelog_for_version(self, version: str) -> Optional[str]:
        """Return the CHANGELOG section for `version`, or None if there is not one.

        None is a SENTINEL meaning "I could not find a section", and callers MUST
        treat it as fatal (see `generate_all_metadata` and `main`). This function
        deliberately never returns prose.

        WHY (2026-08-24). This used to return
        `f"Release {version}\\n\\nSee CHANGELOG.md for details."` when the section was
        absent, and `"...No changelog available."` when CHANGELOG.md itself was
        missing. Both strings land in the `changelog` field of
        public/releases/<tag>.json AND in the <description> of every item in
        public/releases/releases.rss -- deployed, player-visible files. A reader
        cannot tell that text apart from a real, terse release note, so "the
        generator found nothing" rendered as "this release had nothing to say".
        Measured at the time: `grep -c "0\\.14\\.2" CHANGELOG.md` returned 0, and 14
        of the 23 entries in the tracked index carried the placeholder, including the
        live `<description>Release v0.13.1` in releases.rss.

        A value meaning "I could not tell" must not render as a value meaning "fine".
        The one legitimate use for prose here would be to state the ABSENCE, and that
        belongs in the feed writer (which marks it explicitly), not here.
        """
        changelog_file = self.repo_root / "CHANGELOG.md"

        if not changelog_file.exists():
            return None

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
            return None

        return changelog_text

    def generate_release_json(
        self, version: str, tag_info: Dict, evidence: Optional[AssetEvidence] = None
    ) -> Dict:
        """Generate JSON metadata for a single release.

        TWO INDEPENDENT ABSENCES ARE HANDLED HERE, and they are not the same
        absence. `changelog` / `changelog_status` (2026-08-24, #1298) covers
        release notes that were never WRITTEN. `downloads` / `platform_status`
        (this file, same day) covers a platform whose asset was never BUILT. A
        release can have either, both, or neither; both obey the same rule, that
        a value meaning "I could not tell" must not render as one meaning
        "fine".

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
            status = evidence.status_for(key, asset_name)
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
            # null, not a sentence. A consumer that renders this field gets nothing to
            # render, which is the truth, instead of a sentence that reads like a
            # release note. `changelog_status` is the greppable form of the same fact
            # and is what --check inspects.
            "changelog": _ascii_safe(changelog) if changelog is not None else None,
            "changelog_status": "present" if changelog is not None else "missing",
            "downloads": downloads,
            # The explicit half of the asset answer. `downloads` alone cannot
            # tell a consumer WHY a platform is missing; this block distinguishes
            # "not_built" (we looked, it is not there) from "unknown" (we could
            # not look). Exactly parallel to `changelog_status` above.
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
            # A missing changelog gets an explicit statement of ABSENCE, never a
            # stand-in release note. RSS <description> is the most player-visible
            # surface this generator writes -- the live feed carried
            # "<description>Release v0.13.1" for 14 releases before 2026-08-24.
            changelog = release.get("changelog")
            if changelog is None:
                description = _ABSENT_MARKER.format(version=release["version"])
            elif len(changelog) > 500:
                description = changelog[:500] + "..."
            else:
                description = changelog
            ElementTree.SubElement(item, "description").text = description
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
        self,
        tag: str,
        build_status: Optional[Path],
        assets_dir: Optional[Path],
        probe_github: bool,
    ) -> AssetEvidence:
        """Pick the asset-observation source for one tag, most authoritative first.

        1. build-status.json from check_platform_builds.py (#1307). In CI this
           is the answer: its own job already walked the artefact tree, checked
           both the versioned zip AND the alias, and applied a size floor.
        2. --assets-dir, for a local regeneration against a builds/ tree.
        3. The GitHub Releases API, for regenerating already-published tags
           (which is every tag before v0.14.4 -- they have no build-status.json
           and never will).
        4. Nothing => unknown. Never a guess.
        """
        if build_status is not None:
            evidence = evidence_from_build_status(build_status)
            if evidence.resolved:
                return evidence
            print(f"    [!] build-status gave no verdict: {evidence.detail}")
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
        return unresolved_evidence("--no-probe set and no usable build-status/assets-dir")

    def generate_all_metadata(
        self,
        specific_version: Optional[str] = None,
        build_status: Optional[Path] = None,
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
                evidence = self.resolve_evidence(tag, build_status, assets_dir, probe_github)
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

        # Report the changelog gaps BEFORE the success banner, and never let a gap
        # pass silently. Pinned gaps are printed too: a pin that goes quiet is just a
        # slower way of losing the information.
        pinned = load_gap_pin(self.repo_root)
        gaps = [r["version"] for r in releases if r["changelog_status"] == "missing"]
        self.unpinned_gaps = [tag for tag in gaps if tag not in pinned]
        for tag in gaps:
            state = "pinned" if tag in pinned else "UNPINNED"
            print(f"[!] no CHANGELOG.md section for {tag} ({state})")

        print(f"\n[SUCCESS] Generated metadata for {len(releases)} release(s)")
        print(f"[*] Output directory: {self.output_dir}")
        print(f"[*] Latest version: {index_data['latest_version']}")
        print(f"[*] Latest stable: {index_data['latest_stable']}")

        if self.unpinned_gaps:
            print(
                "\n[FATAL] These releases have no CHANGELOG.md section, so the feed has "
                "no release notes to publish for them:"
            )
            for tag in self.unpinned_gaps:
                print(f"  - {tag}")
            print(
                f"[FATAL] Write a '## [<version>]' section in CHANGELOG.md, or add the tag to "
                f"{_CHANGELOG_GAP_PIN} if it genuinely predates the convention."
            )
            print("[FATAL] The generator will NOT invent release notes to fill the gap.")

        return release_files


def _run_self_test(generator: "ReleaseMetadataGenerator", repo_root: Path) -> int:
    """Prove --check still returns all THREE answers, against the real index.

    Only the TAG LIST is varied between the three cases, so the only difference
    is the thing under test. Added 2026-08-29, the day --check became a CI gate:
    its first run in CI reported a measured failure on a correct feed because the
    checkout had no tags, and nothing existed that would have caught that.
    """
    import contextlib
    import io

    real_tags = generator.get_all_release_tags()
    original = generator.get_all_release_tags
    results = {}
    try:
        for label, tags in (
            ("fresh", real_tags),
            ("no tags visible", []),
            ("tags visible but stale", real_tags[:-1]),
        ):
            generator.get_all_release_tags = lambda t=tags: t
            with contextlib.redirect_stdout(io.StringIO()):
                results[label] = _run_check(generator, repo_root)
    finally:
        generator.get_all_release_tags = original

    expected = {"fresh": 0, "no tags visible": 2, "tags visible but stale": 1}
    ok = True
    print("[self-test] %d release tag(s) visible in this checkout." % len(real_tags))
    if len(real_tags) < 2:
        print("[self-test] DID NOT COMPLETE -- needs at least 2 tags to build the stale case.")
        return 2
    for label, want in expected.items():
        got = results[label]
        if got == want:
            print("  [ok] %-24s -> exit %d" % (label, got))
        else:
            ok = False
            print("SELF-TEST FAIL: %-24s -> exit %d, wanted %d" % (label, got, want))

    if ok:
        print("[self-test] PASSED: fresh=0, could-not-measure=2, stale=1 are all reachable.")
        print("            'no tags visible' is the shallow-clone case. It must NOT be 1:")
        print("            a checkout that cannot see tags has not measured the index.")
    else:
        print("[self-test] FAILED")
    return 0 if ok else 1


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

    # THREE OUTCOMES, NOT TWO (added 2026-08-29, the day this became a CI gate).
    #
    # get_all_release_tags() returns [] both when a repo genuinely has no release
    # tags and when the CHECKOUT CANNOT SEE THEM. A shallow clone fetches no tags,
    # and actions/checkout is shallow by default. Collapsing those two into one
    # answer made this command assert, in its first CI run, that all 27 entries in
    # a correct index were "in index but not a git tag" and that latest_version
    # should be None -- a measured verdict from a run that measured nothing, on a
    # feed that was in fact perfectly fresh.
    #
    # A populated index plus zero visible tags is not evidence the index is wrong.
    # It is evidence the question could not be asked. Exit 2 is this repo's answer
    # for that (scripts/run_godot_tests.py, tools/check_balance_keys.py,
    # tools/check_release_ledger.py), and .github/workflows/guards.yml already
    # renders exit 2 as COULD NOT MEASURE rather than as a finding.
    if not expected and tracked.get("releases"):
        print("[check] DID NOT COMPLETE -- `git tag -l 'v*.*.*'` returned nothing, but")
        print(f"        {index_path.name} lists {len(tracked['releases'])} release(s).")
        print("        A checkout with no tags cannot answer whether the index is stale,")
        print("        and this run establishes nothing either way.")
        print("        In CI: give the checkout step `fetch-tags: true` (or fetch-depth: 0).")
        print("        Locally: `git fetch --tags origin`.")
        return 2

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

    # Inspect the CHANGELOG FIELD, not just the tag list. Until 2026-08-24 this
    # function compared which releases were listed and which was latest, and never
    # looked at the one field a player actually reads. An index could therefore be
    # "fresh" by every assertion here while every entry in it said
    # "Release vX.Y.Z / See CHANGELOG.md for details." -- which is what shipped.
    pinned = load_gap_pin(repo_root)
    for release in tracked.get("releases", []):
        version = str(release.get("version", "?"))
        changelog = release.get("changelog")
        if is_placeholder_changelog(changelog):
            problems.append(
                f"{version}: changelog is a retired placeholder ({changelog!r:.60}...) -- "
                f"regenerate; the generator no longer emits these"
            )
        elif changelog is None or not str(changelog).strip():
            if version not in pinned:
                problems.append(
                    f"{version}: no changelog and not listed in {_CHANGELOG_GAP_PIN} -- "
                    f"write a '## [{version.lstrip('v')}]' section in CHANGELOG.md"
                )
        elif "changelog_status" in release and release["changelog_status"] != "present":
            # Only fires when the field EXISTS and disagrees with the text. An index
            # generated before the field was added simply omits it, and complaining
            # about that on every legacy entry would bury the placeholder findings
            # under 9 lines of noise -- measured, that is exactly what it did.
            problems.append(
                f"{version}: has changelog text but changelog_status is "
                f"{release['changelog_status']!r} -- regenerate"
            )

    # The asset half of the same question the changelog loop above asks. That one
    # catches prose that was never written; this catches a URL for a file that was
    # never built. Both are offline, so both can gate pre-commit.
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
        "--build-status",
        type=Path,
        help="build-status.json emitted by scripts/check_platform_builds.py (#1307). "
        "THE authoritative source of platform availability in CI -- it checked the "
        "artefact tree itself, including the unversioned alias and a size floor. "
        "Preferred over --assets-dir; the generator adopts its verdict rather than "
        "forming a second opinion.",
    )
    parser.add_argument(
        "--assets-dir",
        type=Path,
        help="Directory tree of the release's built assets. Local fallback for when "
        "there is no build-status.json. A platform gets a feed entry ONLY if its "
        "asset file is found here.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Prove --check can still return all THREE of its answers (fresh / could "
        "not measure / stale) against the real index. A gate whose failing "
        "directions have never been exercised is a counter, not a gate.",
    )
    parser.add_argument(
        "--no-probe",
        action="store_true",
        help="Do not ask the GitHub Releases API which assets exist. With no other "
        "evidence this makes every platform UNKNOWN and emits no download URLs at "
        "all -- which is the point: offline means unverified, and unverified must "
        "never render as an advertised link.",
    )

    args = parser.parse_args()

    # Find repository root
    repo_root = Path(__file__).parent.parent

    generator = ReleaseMetadataGenerator(repo_root)

    if args.self_test:
        sys.exit(_run_self_test(generator, repo_root))

    if args.check:
        sys.exit(_run_check(generator, repo_root))

    probe_github = not args.no_probe
    generated_files: List[Path] = []
    if args.latest and not args.version:
        # Get latest tag
        tags = generator.get_all_release_tags()
        if tags:
            generated_files = generator.generate_all_metadata(
                specific_version=tags[0],
                build_status=args.build_status,
                assets_dir=args.assets_dir,
                probe_github=probe_github,
            )
        else:
            print("WARNING  No release tags found!")
    else:
        generated_files = generator.generate_all_metadata(
            specific_version=args.version,
            build_status=args.build_status,
            assets_dir=args.assets_dir,
            probe_github=probe_github,
        )

    # A missing changelog section is FATAL, not a shrug. The files are still written
    # (so the feed stays regenerable and the gap is visible in them), but the exit
    # code refuses to call the run a success.
    if generator.unpinned_gaps:
        sys.exit(1)

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
