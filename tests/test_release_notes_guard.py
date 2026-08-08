"""Tests for scripts/check_release_notes.py (issue #1165).

These are OFFLINE. Issue states are stubbed so the suite does not depend on
GitHub -- but the stub values are the real ones, read from the live API on
2026-08-09: #500 OPEN, #483 CLOSED, #1173/#1175/#1179 CLOSED.

The load-bearing test is `test_red_against_the_real_v0132_defect`: the guard
must go RED on the exact text that reached players. A guard that has never been
shown to fail is not evidence.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import check_release_notes as guard  # noqa: E402

# Verbatim from the published v0.13.2 release body (`gh release view v0.13.2`).
# Trimmed to the lines that matter; wording untouched.
V0132_EXCERPT = """\
#### Dev / data (no visible gameplay change yet)
- ~500 art files (worker round 2, cat west-walk variants, prop re-base, tier-6
  diagonals) made durable from the day's generation runs (#965, #966).

#### Added
- **Research Quality System** (#500): Rushed / Standard / Thorough quality toggle for research
- **Scenario/Mod Hook System** (#483): Custom scenarios without code changes
    - **Bootstrap Mode**: Extra resources for learning ($500k, 200 compute)
"""

# Verbatim from the published v0.14.1 release body, hand-checked and clean.
V0141_EXCERPT = """\
### Fixed
- **The leaderboard screen opened on LOCAL** and only fetched the global board if
  you pressed a toggle (#1173). It opens on global now.

### Added
- **In-game patch notes cover 0.12.0 onwards** (#1175), ending three releases
  where the What's New screen said nothing about what changed.
"""

# Verbatim from CHANGELOG.md [0.12.0], written by hand on 2026-08-08. Cites an
# OPEN issue and discloses it, so it must pass.
DISCLOSED_EXCERPT = """\
### Added
- Research quality: a Rushed / Standard / Thorough toggle that trades speed
  against risk, feeding the hidden risk pool (#500). Wired into the plan screen
  via `main_ui.gd`, with `research_quality_selector.gd` as the control. **#500 is
  still OPEN** -- this describes what the shipped code does, not a finished
  feature.
"""

REAL_STATES = {
    500: "OPEN",
    483: "CLOSED",
    791: "OPEN",
    811: "OPEN",
    965: "CLOSED",
    966: "CLOSED",
    1173: "CLOSED",
    1175: "CLOSED",
    1179: "CLOSED",
}


@pytest.fixture(autouse=True)
def stub_github(monkeypatch):
    monkeypatch.setattr(
        guard, "resolve_states", lambda numbers: {n: REAL_STATES.get(n, "CLOSED") for n in numbers}
    )


def codes(findings):
    return sorted(f.code for f in findings if f.fatal)


def test_red_against_the_real_v0132_defect():
    findings, numbers = guard.check_body_citations(V0132_EXCERPT, "v0.13.2")
    fatal = [f for f in findings if f.fatal]
    assert fatal, "guard must go RED on the body that actually reached players"
    assert all("#500" in f.message for f in fatal)
    assert 500 in numbers


def test_green_against_hand_checked_v0141():
    findings, numbers = guard.check_body_citations(V0141_EXCERPT, "v0.14.1")
    assert [f for f in findings if f.fatal] == []
    assert set(numbers) == {1173, 1175}


def test_prose_numbers_are_not_citations():
    """`~500 art files` and `$500k` sit next to the real #500 in the same body.

    If the citation regex caught either, the guard would cry wolf on every
    release and get switched off.
    """
    numbers = [n for n, _, _ in guard.citations_in(V0132_EXCERPT)]
    assert numbers.count(500) == 1


def test_markdown_headings_are_not_citations():
    assert guard.citations_in("#### Added\n### Fixed\n## [0.14.1]") == []


def test_disclosed_open_issue_passes():
    findings, _ = guard.check_body_citations(DISCLOSED_EXCERPT, "[0.12.0]")
    assert [f for f in findings if f.fatal] == []


def test_disclosure_does_not_launder_a_neighbouring_bullet():
    body = DISCLOSED_EXCERPT + "- Something else entirely (#500).\n"
    findings, _ = guard.check_body_citations(body, "mixed")
    assert len([f for f in findings if f.fatal]) == 1


def test_code_fences_are_ignored():
    body = "```\ngh issue view #500\n```\n"
    findings, numbers = guard.check_body_citations(body, "fenced")
    assert numbers == []
    assert findings == []


def test_unknown_state_is_not_a_pass(monkeypatch):
    monkeypatch.setattr(guard, "resolve_states", lambda numbers: {n: "UNKNOWN" for n in numbers})
    findings, _ = guard.check_body_citations(V0141_EXCERPT, "unknown")
    assert findings, "an unresolvable citation must be reported, not silently passed"


def test_rn001_catches_multiple_unreleased_headings():
    text = "# Changelog\n\n## [Unreleased]\n\n- a\n\n## [Unreleased] - 2025-09-17\n\n- b\n"
    findings = guard.check_changelog_structure(text)
    assert "RN001" in codes(findings)


def test_rn001_passes_on_a_single_unreleased_heading():
    text = "# Changelog\n\n## [Unreleased]\n\n## [0.14.1] - 2026-08-08\n\n- a\n"
    assert codes(guard.check_changelog_structure(text)) == []


def test_rn002_duplicate_version_is_warn_only():
    text = "## [0.7.4] - x\n- a\n## [0.7.4] - y\n- b\n"
    findings = guard.check_changelog_structure(text)
    assert codes(findings) == []
    assert any(f.code == "RN002" for f in findings)


def test_extraction_stops_at_the_next_version_heading():
    text = "## [0.14.1]\n- in\n\n## [0.14.0]\n- out\n"
    section = guard.extract_changelog_section("0.14.1", text)
    assert "- in" in section and "- out" not in section


def test_the_real_changelog_has_exactly_one_unreleased_heading():
    """Regression pin for the six-heading corruption (#1165)."""
    findings = guard.check_changelog_structure(guard.CHANGELOG.read_text(encoding="utf-8"))
    assert "RN001" not in codes(findings)
