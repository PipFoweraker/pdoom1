#!/usr/bin/env python3
"""Unit tests for scripts/generate_release_metadata.py -- the release feed generator.

WHAT THESE PIN, and why it matters more than usual:

    This generator writes public/releases/<tag>.json and public/releases/releases.rss.
    Both are DEPLOYED and player-visible -- pdoom.net consumes them, and the RSS
    <description> is the release note a subscriber reads.

    Until 2026-08-24 a missing CHANGELOG section produced
    "Release vX.Y.Z\\n\\nSee CHANGELOG.md for details." and a missing CHANGELOG.md
    produced "...No changelog available.". Neither is distinguishable, to a reader,
    from a real but terse release note. So "the generator could not find anything"
    rendered as "this release had nothing to say" -- a value meaning "I could not
    tell" displayed as a value meaning "fine" (Pip's ruling, 2026-08-23).

    Measured on the tree that carried the defect: `grep -c "0\\.14\\.2" CHANGELOG.md`
    returned 0, 14 of the 23 entries in the tracked index carried the placeholder, and
    the live releases.rss served "<description>Release v0.13.1".

    These tests prove the detector goes RED, not merely that it can go green. The
    fatal-path test is the one that matters: a gate never watched to fail is not known
    to work (the #640 lesson).

THE SECOND HALF OF THIS FILE covers the OTHER absence the same generator can render
as presence: a platform whose ASSET was never built.

    v0.14.3 (2026-08-24) published with no macOS zip -- the export died on a Windows
    .ico that Godot has no decoder for (fixed in #1305). build_all_platforms.py
    dropped the macOS assets exactly as designed and Windows/Linux published exactly
    as designed. The feed advertised PDoom-macOS-v0.14.3.zip regardless, and it
    404'd, in a public feed, on the day the download link was going out by email.

    Same ruling, different dimension. The changelog tests above are about absent
    PROSE; these are about absent FILES. Neither subsumes the other -- a release can
    be missing notes, a platform, both, or neither -- and the generator now refuses
    to paper over either.
"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_platform_builds as cpb  # noqa: E402
import generate_release_metadata as grm  # noqa: E402
import verify_release_urls as vru  # noqa: E402

CHANGELOG_WITH_SECTION = """\
# Changelog

## [Unreleased]
- nothing yet

## [1.2.3] - 2026-01-01
### Added
- a real feature

## [1.2.2] - 2025-12-01
### Fixed
- an old bug
"""


class ExtractChangelogTests(unittest.TestCase):
    """extract_changelog_for_version must return a SENTINEL, never invented prose."""

    def _generator(self, tmp: Path, changelog: str = None) -> grm.ReleaseMetadataGenerator:
        if changelog is not None:
            (tmp / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
        return grm.ReleaseMetadataGenerator(tmp)

    def test_present_section_is_returned(self):
        with tempfile.TemporaryDirectory() as td:
            gen = self._generator(Path(td), CHANGELOG_WITH_SECTION)
            text = gen.extract_changelog_for_version("v1.2.3")
            self.assertIsNotNone(text)
            self.assertIn("a real feature", text)
            # Must stop at the next heading, not swallow the following release.
            self.assertNotIn("an old bug", text)

    def test_absent_section_returns_none_not_prose(self):
        with tempfile.TemporaryDirectory() as td:
            gen = self._generator(Path(td), CHANGELOG_WITH_SECTION)
            self.assertIsNone(gen.extract_changelog_for_version("v9.9.9"))

    def test_missing_changelog_file_returns_none_not_prose(self):
        with tempfile.TemporaryDirectory() as td:
            gen = self._generator(Path(td))  # no CHANGELOG.md written at all
            self.assertIsNone(gen.extract_changelog_for_version("v1.2.3"))

    def test_retired_placeholders_are_never_emitted(self):
        """The exact strings that shipped. If either comes back, this fails."""
        with tempfile.TemporaryDirectory() as td:
            gen = self._generator(Path(td), CHANGELOG_WITH_SECTION)
            for version in ("v9.9.9", "v1.2.3"):
                text = gen.extract_changelog_for_version(version) or ""
                self.assertNotIn("See CHANGELOG.md for details.", text)
                self.assertNotIn("No changelog available.", text)


class ReleaseJsonTests(unittest.TestCase):
    """The player-visible fields must say "missing", not fake a note."""

    def _gen(self, td: str) -> grm.ReleaseMetadataGenerator:
        (Path(td) / "CHANGELOG.md").write_text(CHANGELOG_WITH_SECTION, encoding="utf-8")
        return grm.ReleaseMetadataGenerator(Path(td))

    TAG_INFO = {"date": "2026-01-01T00:00:00+00:00", "commit": "abc123", "message": "msg"}

    def test_missing_changelog_becomes_null_and_status_missing(self):
        with tempfile.TemporaryDirectory() as td:
            data = self._gen(td).generate_release_json("v9.9.9", self.TAG_INFO)
            self.assertIsNone(data["changelog"])
            self.assertEqual(data["changelog_status"], "missing")

    def test_present_changelog_sets_status_present(self):
        with tempfile.TemporaryDirectory() as td:
            data = self._gen(td).generate_release_json("v1.2.3", self.TAG_INFO)
            self.assertIn("a real feature", data["changelog"])
            self.assertEqual(data["changelog_status"], "present")

    def test_rss_description_states_the_absence(self):
        """The most player-visible surface. Must not read like a release note."""
        with tempfile.TemporaryDirectory() as td:
            gen = self._gen(td)
            releases = [
                gen.generate_release_json("v9.9.9", self.TAG_INFO),
                gen.generate_release_json("v1.2.3", self.TAG_INFO),
            ]
            rss = gen.generate_rss_feed(releases)
            self.assertIn("[no CHANGELOG.md section for v9.9.9", rss)
            self.assertNotIn("See CHANGELOG.md for details.", rss)
            # The real one still renders normally.
            self.assertIn("a real feature", rss)


class GapPinTests(unittest.TestCase):
    """The pin is a ratchet, and it must be capable of returning the other answer."""

    def test_repo_pin_parses_and_lists_only_real_tags(self):
        pinned = grm.load_gap_pin(REPO_ROOT)
        self.assertGreater(len(pinned), 0, "the shipped pin should not be empty")
        for tag in pinned:
            self.assertRegex(tag, r"^v\d+\.\d+\.\d+", "pin entries are version tags")

    def test_current_release_is_not_pinned(self):
        """v0.14.2 is deliberately UNPINNED so the generator stays loud about it.

        If someone silences it by adding the line, this fails and says why.
        """
        self.assertNotIn(
            "v0.14.2",
            grm.load_gap_pin(REPO_ROOT),
            "v0.14.2 has no CHANGELOG section; the fix is to write the section, "
            "not to pin it. The pin is for releases that predate the convention.",
        )

    def test_missing_pin_file_makes_every_gap_fatal(self):
        """A deleted pin must make the gate STRICTER, never quieter."""
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(grm.load_gap_pin(Path(td)), [])

    def test_comments_and_blank_lines_are_ignored(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "scripts").mkdir()
            (root / grm._CHANGELOG_GAP_PIN).write_text(
                "# a comment\n\nv1.0.0  # trailing note\n", encoding="utf-8"
            )
            self.assertEqual(grm.load_gap_pin(root), ["v1.0.0"])


class PlaceholderDetectionTests(unittest.TestCase):
    def test_recognises_both_retired_strings(self):
        self.assertTrue(
            grm.is_placeholder_changelog("Release v0.13.1\n\nSee CHANGELOG.md for details.")
        )
        self.assertTrue(grm.is_placeholder_changelog("Release v0.9.0\n\nNo changelog available."))

    def test_does_not_flag_a_real_note(self):
        self.assertFalse(grm.is_placeholder_changelog("### Added\n- a real feature"))

    def test_none_and_empty_are_not_placeholders(self):
        # They are a DIFFERENT problem (absence), reported separately by --check.
        self.assertFalse(grm.is_placeholder_changelog(None))
        self.assertFalse(grm.is_placeholder_changelog(""))


class CheckInspectsChangelogTests(unittest.TestCase):
    """--check used to compare only tags and latest_version.

    An index could therefore be "fresh" by every assertion it made while every entry
    in it said "See CHANGELOG.md for details.". These prove it now looks at the field
    a player actually reads.
    """

    def _run_check_on(self, td: str, releases: list, pin: str = "") -> tuple:
        root = Path(td)
        (root / "public" / "releases").mkdir(parents=True)
        (root / "scripts").mkdir(exist_ok=True)
        (root / grm._CHANGELOG_GAP_PIN).write_text(pin, encoding="utf-8")
        index = {
            "latest_version": releases[0]["version"] if releases else None,
            "releases": releases,
        }
        (root / "public" / "releases" / "releases.json").write_text(
            json.dumps(index), encoding="utf-8"
        )
        gen = grm.ReleaseMetadataGenerator(root)
        tags = [r["version"] for r in releases]
        with mock.patch.object(gen, "get_all_release_tags", return_value=tags):
            import io
            from contextlib import redirect_stdout

            buf = io.StringIO()
            with redirect_stdout(buf):
                code = grm._run_check(gen, root)
        return code, buf.getvalue()

    def test_placeholder_changelog_fails_the_check(self):
        with tempfile.TemporaryDirectory() as td:
            code, out = self._run_check_on(
                td,
                [
                    {
                        "version": "v1.0.0",
                        "changelog": "Release v1.0.0\n\nSee CHANGELOG.md for details.",
                        "changelog_status": "present",
                    }
                ],
            )
            self.assertEqual(code, 1)
            self.assertIn("retired placeholder", out)

    def test_null_changelog_fails_unless_pinned(self):
        with tempfile.TemporaryDirectory() as td:
            code, out = self._run_check_on(
                td,
                [{"version": "v1.0.0", "changelog": None, "changelog_status": "missing"}],
            )
            self.assertEqual(code, 1)
            self.assertIn("no changelog", out)

    def test_null_changelog_passes_when_pinned(self):
        with tempfile.TemporaryDirectory() as td:
            code, out = self._run_check_on(
                td,
                [{"version": "v1.0.0", "changelog": None, "changelog_status": "missing"}],
                pin="v1.0.0\n",
            )
            self.assertEqual(code, 0, out)

    def test_a_good_index_passes(self):
        """The gate must be capable of returning the OTHER answer."""
        with tempfile.TemporaryDirectory() as td:
            code, out = self._run_check_on(
                td,
                [
                    {
                        "version": "v1.0.0",
                        "changelog": "### Added\n- a real feature",
                        "changelog_status": "present",
                    }
                ],
            )
            self.assertEqual(code, 0, out)


class ManifestCallerTests(unittest.TestCase):
    """generate_release_manifest.py is the THIRD surface the placeholder reached.

    extract_highlights() feeds a client tooltip. It used to call
    _ascii_safe(extract_changelog_for_version(v)).strip() directly, so it inherited
    "Release vX.Y.Z / See CHANGELOG.md for details." verbatim -- and, once the
    extractor started returning None, would have raised AttributeError on .strip().
    """

    def _highlights(self, version: str) -> str:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import generate_release_manifest as grman

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "CHANGELOG.md").write_text(CHANGELOG_WITH_SECTION, encoding="utf-8")
            return grman.extract_highlights(Path(td), version)

    def test_present_section_is_excerpted(self):
        self.assertIn("a real feature", self._highlights("v1.2.3"))

    def test_missing_section_states_absence_and_does_not_raise(self):
        text = self._highlights("v9.9.9")
        self.assertIn("[no CHANGELOG.md section for v9.9.9", text)
        self.assertNotIn("See CHANGELOG.md for details.", text)


class WorkflowGateAgreementTests(unittest.TestCase):
    """pre-release-checks.yml must ask the SAME question as the extractor.

    It used to run `grep -q "$TAG_VERSION" CHANGELOG.md` -- unanchored and
    unbracketed, so any mention of the bare string anywhere in CHANGELOG.md's 1800+
    lines satisfied it. Measured against the repo's own 25 tags, 6 of them (v0.9.0,
    v0.10.1, v0.10.2, v0.10.3, v0.11.0, v0.13.1) PASSED that gate while having no
    section heading at all -- and those are precisely the releases whose feed entries
    carried the placeholder.
    """

    WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pre-release-checks.yml"

    def test_changelog_gate_is_anchored(self):
        text = self.WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            'grep -q "^## \\[$TAG_VERSION\\]" CHANGELOG.md',
            text,
            "the CHANGELOG gate must anchor on the section heading",
        )

    def test_unanchored_form_is_gone(self):
        text = self.WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn(
            'grep -q "$TAG_VERSION" CHANGELOG.md',
            text,
            "the unanchored grep passed for 6 real tags that had no section",
        )

    def test_anchor_matches_what_the_extractor_finds(self):
        """The workflow's regex and extract_changelog_for_version must agree.

        Two gates testing different things is how the loose one ends up owning the
        reassuring message. This runs both over the real CHANGELOG.md for every real
        tag and asserts they never disagree.
        """
        changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        tags = subprocess.run(
            ["git", "tag", "-l", "v*.*.*"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
            gen = grm.ReleaseMetadataGenerator(Path(td))
            for tag in tags:
                version = tag.lstrip("v")
                workflow_hit = bool(re.search(r"(?m)^## \[%s\]" % re.escape(version), changelog))
                extractor_hit = gen.extract_changelog_for_version(tag) is not None
                self.assertEqual(
                    workflow_hit,
                    extractor_hit,
                    "gates disagree for {}: workflow={}, extractor={}".format(
                        tag, workflow_hit, extractor_hit
                    ),
                )


# ---------------------------------------------------------------------------
# ASSET PRESENCE -- the other absence (v0.14.3, 2026-08-24)
# ---------------------------------------------------------------------------

ASSET_VERSION = "v0.14.3"
WINDOWS_ASSET = f"PDoom-Windows-{ASSET_VERSION}.zip"
LINUX_ASSET = f"PDoom-Linux-{ASSET_VERSION}.zip"
MAC_ASSET = f"PDoom-macOS-{ASSET_VERSION}.zip"

ASSET_TAG_INFO = {
    "tag": ASSET_VERSION,
    "date": "2026-08-24T04:30:00+00:00",
    "commit": "0" * 40,
    "message": "release cut",
}


def _all_strings(node):
    """Every string value anywhere in a nested JSON-ish structure."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _all_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _all_strings(value)


def make_generator(tmp: Path) -> "grm.ReleaseMetadataGenerator":
    """A generator rooted in a throwaway tree, so no test writes public/releases/."""
    return grm.ReleaseMetadataGenerator(tmp)


def build_entry(tmp: Path, asset_names, source="test") -> dict:
    evidence = grm.AssetEvidence(asset_names, source)
    return make_generator(tmp).generate_release_json(ASSET_VERSION, ASSET_TAG_INFO, evidence)


class TestAllThreePlatformsPresent(unittest.TestCase):
    """The positive answer: everything built, everything advertised."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.entry = build_entry(Path(self.tmp.name), [WINDOWS_ASSET, LINUX_ASSET, MAC_ASSET])
        self.addCleanup(self.tmp.cleanup)

    def test_three_platform_downloads(self):
        downloads = self.entry["downloads"]
        self.assertIn("windows", downloads)
        self.assertIn("linux", downloads)
        self.assertIn("mac", downloads)

    def test_all_statuses_available(self):
        for platform in ("windows", "linux", "mac"):
            self.assertEqual(
                self.entry["platform_status"][platform]["status"], grm.STATUS_AVAILABLE
            )

    def test_urls_point_at_the_observed_asset_names(self):
        self.assertTrue(self.entry["downloads"]["mac"].endswith("/" + MAC_ASSET))
        self.assertTrue(self.entry["downloads"]["windows"].endswith("/" + WINDOWS_ASSET))
        self.assertTrue(self.entry["downloads"]["linux"].endswith("/" + LINUX_ASSET))

    def test_metadata_platforms_lists_all_three(self):
        self.assertEqual(self.entry["metadata"]["platforms"], ["Windows", "Linux", "macOS"])

    def test_source_archives_still_present(self):
        # Codeload archives exist for any tag, so they are NOT gated on assets.
        self.assertIn("source_zip", self.entry["downloads"])
        self.assertIn("source_tar", self.entry["downloads"])


class TestMissingMacOS(unittest.TestCase):
    """The v0.14.3 answer: two platforms, and macOS explicitly marked not built."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.entry = build_entry(Path(self.tmp.name), [WINDOWS_ASSET, LINUX_ASSET])
        self.addCleanup(self.tmp.cleanup)

    def test_two_platform_downloads(self):
        downloads = self.entry["downloads"]
        self.assertIn("windows", downloads)
        self.assertIn("linux", downloads)
        self.assertNotIn("mac", downloads)

    def test_macos_marked_not_built_not_merely_absent(self):
        mac = self.entry["platform_status"]["mac"]
        self.assertEqual(mac["status"], grm.STATUS_NOT_BUILT)
        # The consumer is told WHICH asset was looked for and WHERE that was
        # checked -- "not built" has to be a statement, not a silence.
        self.assertEqual(mac["asset"], MAC_ASSET)
        self.assertEqual(mac["evidence"], "test")
        self.assertNotIn("url", mac)

    def test_not_built_is_distinguishable_from_not_checked(self):
        self.assertNotEqual(self.entry["platform_status"]["mac"]["status"], grm.STATUS_UNKNOWN)

    def test_no_macos_url_anywhere_in_the_serialised_feed(self):
        # The load-bearing assertion. Not "mac is missing from downloads" but
        # "the string that 404'd does not appear in the published bytes at all".
        #
        # Note the asset NAME does still appear, inside platform_status -- that
        # is the evidence trail ("this is what was looked for and not found"),
        # and it is not a link. What must never appear is the downloadable URL.
        serialised = json.dumps(self.entry)
        dead_url = f"releases/download/{ASSET_VERSION}/{MAC_ASSET}"
        self.assertNotIn(dead_url, serialised)
        for value in _all_strings(self.entry):
            if value.startswith("http"):
                self.assertNotIn("PDoom-macOS", value, f"advertised a macOS URL: {value}")

    def test_metadata_platforms_does_not_claim_macos(self):
        self.assertEqual(self.entry["metadata"]["platforms"], ["Windows", "Linux"])
        self.assertNotIn("macOS", self.entry["metadata"]["platforms"])

    def test_windows_and_linux_are_untouched_by_the_macos_failure(self):
        # The failure policy (issue #1069) is that a macOS miss must not cost
        # the required platforms anything. Assert that, not just the omission.
        self.assertTrue(self.entry["downloads"]["windows"].endswith("/" + WINDOWS_ASSET))
        self.assertTrue(self.entry["downloads"]["linux"].endswith("/" + LINUX_ASSET))

    def test_the_changelog_half_still_works_alongside(self):
        # The compose itself: #1298's field and this lane's field coexist in one
        # entry. If either restructure had clobbered the other, this fails.
        self.assertIn("changelog_status", self.entry)
        self.assertIn("platform_status", self.entry)


class TestUnknownIsNotAPass(unittest.TestCase):
    """RULING 2026-08-23 (manufactured confidence): could-not-tell is not fine."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_no_evidence_yields_unknown_for_every_platform(self):
        entry = build_entry(Path(self.tmp.name), None, source="none")
        for platform in ("windows", "linux", "mac"):
            self.assertEqual(entry["platform_status"][platform]["status"], grm.STATUS_UNKNOWN)

    def test_unknown_emits_no_download_urls(self):
        entry = build_entry(Path(self.tmp.name), None, source="none")
        for platform in ("windows", "linux", "mac"):
            self.assertNotIn(platform, entry["downloads"])
        self.assertEqual(entry["metadata"]["platforms"], [])

    def test_omitting_evidence_entirely_defaults_to_unknown_not_to_advertising(self):
        # A caller that forgets the argument must under-advertise, never invent.
        entry = make_generator(Path(self.tmp.name)).generate_release_json(
            ASSET_VERSION, ASSET_TAG_INFO
        )
        self.assertEqual(entry["platform_status"]["windows"]["status"], grm.STATUS_UNKNOWN)
        self.assertNotIn("windows", entry["downloads"])
        self.assertFalse(entry["asset_evidence"]["resolved"])

    def test_empty_observation_is_not_unknown(self):
        # A release that genuinely carries no assets is a real observation.
        # Collapsing it into "unknown" would lose the difference the ruling is
        # about, in the opposite direction.
        entry = build_entry(Path(self.tmp.name), [], source="github-api")
        for platform in ("windows", "linux", "mac"):
            self.assertEqual(entry["platform_status"][platform]["status"], grm.STATUS_NOT_BUILT)
        self.assertTrue(entry["asset_evidence"]["resolved"])


class TestEvidenceFromBuildStatus(unittest.TestCase):
    """#1307's scanner is authoritative; this adopts its verdict, never re-derives."""

    def _write(self, tmp: Path, platforms: dict) -> Path:
        path = tmp / "build-status.json"
        path.write_text(
            json.dumps({"schema": cpb.SCHEMA, "version": ASSET_VERSION, "platforms": platforms}),
            encoding="utf-8",
        )
        return path

    def test_adopts_the_scanners_verdict_including_the_macos_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp),
                {
                    "windows": {"available": True},
                    "linux": {"available": True},
                    "macos": {"available": False},
                },
            )
            evidence = grm.evidence_from_build_status(path)
            self.assertTrue(evidence.resolved)
            entry = make_generator(Path(tmp)).generate_release_json(
                ASSET_VERSION, ASSET_TAG_INFO, evidence
            )
        self.assertEqual(
            sorted(k for k in entry["downloads"] if not k.startswith("source")),
            ["linux", "windows"],
        )
        self.assertEqual(entry["platform_status"]["mac"]["status"], grm.STATUS_NOT_BUILT)
        self.assertEqual(entry["platform_status"]["mac"]["evidence"], "build-status")

    def test_a_stricter_verdict_wins_over_a_bare_filename_match(self):
        # The whole reason for preferring #1307: it fails a truncated zip that a
        # name lookup would happily call present. If this generator re-derived
        # availability from names it would DISAGREE with the build report.
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), {"windows": {"available": False}})
            evidence = grm.evidence_from_build_status(path)
            # The file is on disk under the same name, yet the verdict is False.
            (Path(tmp) / WINDOWS_ASSET).write_bytes(b"truncated")
            self.assertEqual(evidence.status_for("windows", WINDOWS_ASSET), grm.STATUS_NOT_BUILT)

    def test_missing_file_is_unknown_not_nothing_was_built(self):
        evidence = grm.evidence_from_build_status(Path("no") / "such" / "build-status.json")
        self.assertFalse(evidence.resolved)
        self.assertEqual(evidence.status_for("windows", WINDOWS_ASSET), grm.STATUS_UNKNOWN)

    def test_garbled_file_is_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "build-status.json"
            path.write_text("{not json", encoding="utf-8")
            self.assertFalse(grm.evidence_from_build_status(path).resolved)

    def test_platform_absent_from_the_report_is_unknown_not_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), {"windows": {"available": True}})
            evidence = grm.evidence_from_build_status(path)
            self.assertEqual(evidence.status_for("mac", MAC_ASSET), grm.STATUS_UNKNOWN)


class TestEvidenceFromDirectory(unittest.TestCase):
    def test_finds_assets_nested_under_artifact_directories(self):
        # CI's layout: build-artifacts/build-windows/<version>/<zip>
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for artifact, name in (
                ("build-windows", WINDOWS_ASSET),
                ("build-linux", LINUX_ASSET),
            ):
                target = root / artifact / ASSET_VERSION
                target.mkdir(parents=True)
                (target / name).write_bytes(b"zip")
            evidence = grm.evidence_from_directory(root)
            self.assertTrue(evidence.resolved)
            self.assertEqual(evidence.status_for("windows", WINDOWS_ASSET), grm.STATUS_AVAILABLE)
            self.assertEqual(evidence.status_for("linux", LINUX_ASSET), grm.STATUS_AVAILABLE)
            self.assertEqual(evidence.status_for("mac", MAC_ASSET), grm.STATUS_NOT_BUILT)

    def test_missing_directory_is_unresolved_not_empty(self):
        # "the artifact download step is misconfigured" must not render as
        # "no platform was built" -- that would silently unpublish everything.
        evidence = grm.evidence_from_directory(Path("no") / "such" / "dir")
        self.assertFalse(evidence.resolved)
        self.assertEqual(evidence.status_for("windows", WINDOWS_ASSET), grm.STATUS_UNKNOWN)

    def test_empty_directory_is_a_real_observation(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = grm.evidence_from_directory(Path(tmp))
            self.assertTrue(evidence.resolved)
            self.assertEqual(evidence.status_for("windows", WINDOWS_ASSET), grm.STATUS_NOT_BUILT)


class TestEvidenceFromGitHub(unittest.TestCase):
    """Every API failure path must degrade to UNKNOWN, never to an empty list."""

    def _urlopen_returning(self, payload: dict):
        response = mock.MagicMock()
        response.read.return_value = json.dumps(payload).encode("utf-8")
        response.__enter__.return_value = response
        response.__exit__.return_value = False
        return mock.patch.object(grm.urllib.request, "urlopen", return_value=response)

    def test_parses_asset_names(self):
        payload = {"assets": [{"name": WINDOWS_ASSET}, {"name": LINUX_ASSET}]}
        with self._urlopen_returning(payload):
            evidence = grm.evidence_from_github(ASSET_VERSION)
        self.assertTrue(evidence.resolved)
        self.assertEqual(evidence.status_for("linux", LINUX_ASSET), grm.STATUS_AVAILABLE)
        self.assertEqual(evidence.status_for("mac", MAC_ASSET), grm.STATUS_NOT_BUILT)

    def test_rate_limit_is_unknown_not_nothing_was_built(self):
        error = urllib.error.HTTPError("url", 403, "rate limited", {}, None)
        with mock.patch.object(grm.urllib.request, "urlopen", side_effect=error):
            evidence = grm.evidence_from_github(ASSET_VERSION)
        self.assertFalse(evidence.resolved)
        self.assertEqual(evidence.status_for("windows", WINDOWS_ASSET), grm.STATUS_UNKNOWN)

    def test_offline_is_unknown(self):
        error = urllib.error.URLError("no route to host")
        with mock.patch.object(grm.urllib.request, "urlopen", side_effect=error):
            self.assertFalse(grm.evidence_from_github(ASSET_VERSION).resolved)

    def test_garbled_payload_is_unknown(self):
        with self._urlopen_returning({"message": "Not Found"}):
            self.assertFalse(grm.evidence_from_github(ASSET_VERSION).resolved)


class TestAuditAdvertisedPlatforms(unittest.TestCase):
    """The offline gate, proven able to return BOTH answers."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_clean_feed_passes(self):
        entry = build_entry(Path(self.tmp.name), [WINDOWS_ASSET, LINUX_ASSET])
        self.assertEqual(grm.audit_advertised_platforms([entry]), [])

    def test_the_exact_v0143_defect_is_caught(self):
        # Reconstruct what actually shipped: a not_built macOS with a URL.
        entry = build_entry(Path(self.tmp.name), [WINDOWS_ASSET, LINUX_ASSET])
        entry["downloads"][
            "mac"
        ] = f"https://github.com/{grm.GITHUB_REPO}/releases/download/{ASSET_VERSION}/{MAC_ASSET}"
        problems = grm.audit_advertised_platforms([entry])
        self.assertTrue(problems)
        self.assertTrue(any("mac" in p for p in problems), problems)

    def test_unknown_with_a_url_is_also_caught(self):
        entry = build_entry(Path(self.tmp.name), None)
        entry["downloads"]["windows"] = "https://example.invalid/whatever.zip"
        self.assertTrue(grm.audit_advertised_platforms([entry]))

    def test_available_without_a_url_is_caught(self):
        entry = build_entry(Path(self.tmp.name), [WINDOWS_ASSET, LINUX_ASSET])
        del entry["downloads"]["windows"]
        self.assertTrue(grm.audit_advertised_platforms([entry]))

    def test_legacy_entry_advertising_a_platform_is_still_caught(self):
        # No platform_status AND a platform URL -- the exact shape the published
        # v0.14.3 feed had. Leniency about the missing block must not reach this.
        entry = build_entry(Path(self.tmp.name), [WINDOWS_ASSET])
        del entry["platform_status"]
        problems = grm.audit_advertised_platforms([entry])
        self.assertTrue(problems)
        self.assertIn("platform_status", problems[0])

    def test_legacy_entry_advertising_nothing_is_left_alone(self):
        # Following #1298's measured call one loop above: a finding that fires
        # on every legacy entry buries the one that matters. An entry with no
        # platform downloads at all claims nothing, so there is nothing to catch.
        self.assertEqual(grm.audit_advertised_platforms([{"version": "v1.0.0"}]), [])

    def test_the_real_published_v0143_shape_is_caught(self):
        # Reconstructed from the artifact that actually shipped: mac advertised,
        # no platform_status block anywhere.
        legacy = {
            "version": ASSET_VERSION,
            "downloads": {
                "windows": "https://example.invalid/w.zip",
                "linux": "https://example.invalid/l.zip",
                "mac": "https://example.invalid/PDoom-macOS-v0.14.3.zip",
            },
        }
        self.assertTrue(grm.audit_advertised_platforms([legacy]))


class TestVerifyReleaseUrlsCrossCheck(unittest.TestCase):
    """The blocking CI gate's offline half -- both answers demanded again."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_two_platform_feed_is_consistent(self):
        entry = build_entry(Path(self.tmp.name), [WINDOWS_ASSET, LINUX_ASSET])
        self.assertEqual(vru.verify_platform_status(entry, ASSET_VERSION), [])

    def test_advertised_missing_macos_fails(self):
        entry = build_entry(Path(self.tmp.name), [WINDOWS_ASSET, LINUX_ASSET])
        entry["downloads"]["mac"] = "https://example.invalid/PDoom-macOS.zip"
        self.assertTrue(vru.verify_platform_status(entry, ASSET_VERSION))

    def test_missing_status_block_fails(self):
        self.assertTrue(vru.verify_platform_status({"downloads": {}}, ASSET_VERSION))


class TestOneAssetNameTableNotTwo(unittest.TestCase):
    """The feed must not grow a second opinion about what an asset is called.

    #1307 landed check_platform_builds.PLATFORMS while this lane was in flight.
    Two tables of the same names is the drift that lets a build report and a
    release feed disagree about one release, so this generator DERIVES from that
    table rather than restating it. These tests pin the derivation's assumptions.
    """

    def test_every_feed_platform_maps_to_a_real_scanner_platform(self):
        scanner_keys = {spec["key"] for spec in cpb.PLATFORMS}
        for build_key in grm._FEED_TO_BUILD_KEY.values():
            self.assertIn(build_key, scanner_keys)

    def test_versioned_template_comes_first_and_the_alias_second(self):
        # The derivation indexes assets[0]/assets[1] by position. If that order
        # ever flipped, the feed would advertise the unversioned alias as the
        # versioned download -- silently, and only on the next release.
        for spec in cpb.PLATFORMS:
            versioned, alias = spec["assets"][0], spec["assets"][1]
            self.assertIn("{version}", versioned, spec["key"])
            self.assertNotIn("{version}", alias, spec["key"])

    def test_asset_templates_match_build_all_platforms(self):
        builder = (REPO_ROOT / "scripts" / "build_all_platforms.py").read_text(encoding="utf-8")
        for _key, _label, template in grm.PLATFORMS:
            stem = template.format(version="{self.version}")
            self.assertIn(
                stem, builder, f"{template} is not a name build_all_platforms.py produces"
            )

    def test_platform_assets_for_lists_versioned_then_alias(self):
        names = grm.platform_assets_for(ASSET_VERSION)
        self.assertEqual(names["mac"], [MAC_ASSET, "PDoom.app.zip"])
        self.assertEqual(names["windows"], [WINDOWS_ASSET, "PDoom-Windows.zip"])


if __name__ == "__main__":
    unittest.main()
