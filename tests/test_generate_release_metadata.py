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
"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_release_metadata as grm  # noqa: E402

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


if __name__ == "__main__":
    unittest.main()
