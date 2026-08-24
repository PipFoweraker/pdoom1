# !/usr/bin/env python3
"""Unit tests for scripts/generate_release_metadata.py -- platform asset presence.

THE BUG THESE LOCK DOWN (v0.14.3, 2026-08-24):

The generator built its `downloads` block from a naming convention. macOS is a
deliberately best-effort platform (issue #1071): its export failed, no
PDoom-macOS-v0.14.3.zip was ever uploaded, and Windows/Linux published as
designed. The feed advertised the macOS zip anyway. It answered 404, in a
public feed, on the day the download link was going out by email.

This is the #963 shape by name -- "a URL that never existed, that looked like a
working link" -- with the twist that the convention was CORRECT and the asset
was simply absent. So a test that only checks URL SPELLING cannot catch it; the
tests below check URL EXISTENCE against observed assets.

The pair that matters is `test_all_three_platforms_*` vs
`test_missing_macos_*`: same generator, same version, same convention, and the
two produce different feeds. A check that cannot return the other answer proves
nothing, so both answers are demanded here.
"""

import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_release_metadata as grm  # noqa: E402
import verify_release_urls as vru  # noqa: E402

VERSION = "v0.14.3"

WINDOWS_ASSET = f"PDoom-Windows-{VERSION}.zip"
LINUX_ASSET = f"PDoom-Linux-{VERSION}.zip"
MAC_ASSET = f"PDoom-macOS-{VERSION}.zip"

TAG_INFO = {
    "tag": VERSION,
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


def make_generator(tmp: Path) -> grm.ReleaseMetadataGenerator:
    """A generator rooted in a throwaway tree, so no test writes public/releases/."""
    return grm.ReleaseMetadataGenerator(tmp)


def build_entry(tmp: Path, asset_names, source="test") -> dict:
    evidence = grm.AssetEvidence(asset_names, source)
    return make_generator(tmp).generate_release_json(VERSION, TAG_INFO, evidence)


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
        dead_url = f"releases/download/{VERSION}/{MAC_ASSET}"
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
        entry = make_generator(Path(self.tmp.name)).generate_release_json(VERSION, TAG_INFO)
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


class TestEvidenceFromDirectory(unittest.TestCase):
    def test_finds_assets_nested_under_artifact_directories(self):
        # CI's layout: build-artifacts/build-windows/<version>/<zip>
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for artifact, name in (
                ("build-windows", WINDOWS_ASSET),
                ("build-linux", LINUX_ASSET),
            ):
                target = root / artifact / VERSION
                target.mkdir(parents=True)
                (target / name).write_bytes(b"zip")
            evidence = grm.evidence_from_directory(root)
            self.assertTrue(evidence.resolved)
            self.assertEqual(evidence.status_for(WINDOWS_ASSET), grm.STATUS_AVAILABLE)
            self.assertEqual(evidence.status_for(LINUX_ASSET), grm.STATUS_AVAILABLE)
            self.assertEqual(evidence.status_for(MAC_ASSET), grm.STATUS_NOT_BUILT)

    def test_missing_directory_is_unresolved_not_empty(self):
        # "the artifact download step is misconfigured" must not render as
        # "no platform was built" -- that would silently unpublish everything.
        evidence = grm.evidence_from_directory(Path("no") / "such" / "dir")
        self.assertFalse(evidence.resolved)
        self.assertEqual(evidence.status_for(WINDOWS_ASSET), grm.STATUS_UNKNOWN)

    def test_empty_directory_is_a_real_observation(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = grm.evidence_from_directory(Path(tmp))
            self.assertTrue(evidence.resolved)
            self.assertEqual(evidence.status_for(WINDOWS_ASSET), grm.STATUS_NOT_BUILT)


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
            evidence = grm.evidence_from_github(VERSION)
        self.assertTrue(evidence.resolved)
        self.assertEqual(evidence.status_for(LINUX_ASSET), grm.STATUS_AVAILABLE)
        self.assertEqual(evidence.status_for(MAC_ASSET), grm.STATUS_NOT_BUILT)

    def test_rate_limit_is_unknown_not_nothing_was_built(self):
        error = urllib.error.HTTPError("url", 403, "rate limited", {}, None)
        with mock.patch.object(grm.urllib.request, "urlopen", side_effect=error):
            evidence = grm.evidence_from_github(VERSION)
        self.assertFalse(evidence.resolved)
        self.assertEqual(evidence.status_for(WINDOWS_ASSET), grm.STATUS_UNKNOWN)

    def test_offline_is_unknown(self):
        error = urllib.error.URLError("no route to host")
        with mock.patch.object(grm.urllib.request, "urlopen", side_effect=error):
            evidence = grm.evidence_from_github(VERSION)
        self.assertFalse(evidence.resolved)

    def test_garbled_payload_is_unknown(self):
        with self._urlopen_returning({"message": "Not Found"}):
            evidence = grm.evidence_from_github(VERSION)
        self.assertFalse(evidence.resolved)


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
        ] = f"https://github.com/{grm.GITHUB_REPO}/releases/download/{VERSION}/{MAC_ASSET}"
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

    def test_legacy_feed_without_status_block_is_reported_not_passed(self):
        entry = build_entry(Path(self.tmp.name), [WINDOWS_ASSET])
        del entry["platform_status"]
        problems = grm.audit_advertised_platforms([entry])
        self.assertTrue(problems)
        self.assertIn("platform_status", problems[0])


class TestVerifyReleaseUrlsCrossCheck(unittest.TestCase):
    """The blocking CI gate's offline half -- both answers demanded again."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_two_platform_feed_is_consistent(self):
        entry = build_entry(Path(self.tmp.name), [WINDOWS_ASSET, LINUX_ASSET])
        self.assertEqual(vru.verify_platform_status(entry, VERSION), [])

    def test_advertised_missing_macos_fails(self):
        entry = build_entry(Path(self.tmp.name), [WINDOWS_ASSET, LINUX_ASSET])
        entry["downloads"]["mac"] = "https://example.invalid/PDoom-macOS.zip"
        problems = vru.verify_platform_status(entry, VERSION)
        self.assertTrue(problems)

    def test_missing_status_block_fails(self):
        self.assertTrue(vru.verify_platform_status({"downloads": {}}, VERSION))


class TestPlatformContractMatchesTheBuilder(unittest.TestCase):
    """Guard the convention half: the names must stay the ones CI produces."""

    def test_asset_templates_match_build_all_platforms(self):
        builder = (REPO_ROOT / "scripts" / "build_all_platforms.py").read_text(encoding="utf-8")
        for _key, _label, template in grm.PLATFORMS:
            # The builder writes these with an f-string on self.version.
            stem = template.format(version="{self.version}")
            self.assertIn(
                stem,
                builder,
                f"{template} is not a name scripts/build_all_platforms.py produces",
            )


if __name__ == "__main__":
    unittest.main()
