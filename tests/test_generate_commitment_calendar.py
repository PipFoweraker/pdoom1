"""Tests for scripts/generate_commitment_calendar.py.

The load-bearing ones are the NEGATIVE cases: a declaration that should be
rejected, and a date that must NOT vanish. A generator that only proves it can
emit is the class of guard this repo has been burned by (#640: a CI gate reporting
green while running zero tests).
"""

import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_commitment_calendar as gcc  # noqa: E402

HORIZON = date(2026, 8, 9)


def parse(payload):
    return gcc.parse_declaration(payload, "test.md:1", HORIZON)


def test_minimal_declaration_parses():
    got, err = parse("2026-08-13 -- Do the thing -- owner: pip")
    assert err is None
    assert len(got) == 1
    assert got[0].when == date(2026, 8, 13)
    assert got[0].title == "Do the thing"
    assert got[0].owner == "pip"
    assert got[0].kind == "task"


def test_title_containing_the_field_separator_survives():
    """House ASCII style makes ' -- ' an ordinary word separator. A parser that
    split positionally would corrupt every second declaration."""
    got, err = parse("2026-08-13 -- Ship v1 -- and only v1 -- owner: pip -- kind: deadline")
    assert err is None
    assert got[0].title == "Ship v1 -- and only v1"
    assert got[0].kind == "deadline"


def test_note_containing_the_separator_stays_in_the_note():
    got, err = parse("2026-08-13 -- T -- owner: pip -- note: because A -- and B")
    assert err is None
    assert got[0].note == "because A -- and B"
    assert got[0].title == "T"


def test_missing_owner_is_rejected_not_defaulted():
    got, err = parse("2026-08-13 -- Do the thing")
    assert got == []
    assert "owner" in err


def test_unknown_kind_is_rejected():
    _got, err = parse("2026-08-13 -- T -- owner: pip -- kind: vibes")
    assert "unknown kind" in err


def test_no_date_token_is_rejected():
    _got, err = parse("soonish -- T -- owner: pip")
    assert err is not None


def test_recurrence_expands_and_is_bounded():
    got, err = parse(
        "every TH -- Thursday dev -- owner: pip -- kind: cadence "
        "-- from: 2026-08-13 -- until: 2026-09-03"
    )
    assert err is None
    assert [c.when for c in got] == [
        date(2026, 8, 13),
        date(2026, 8, 20),
        date(2026, 8, 27),
        date(2026, 9, 3),
    ]
    assert all(c.leads == (0,) for c in got)


def test_recurrence_without_from_is_rejected():
    _got, err = parse("every TH -- T -- owner: pip -- kind: cadence")
    assert "from:" in err


def test_lead_times_differ_by_kind():
    """A lodgement deadline and a recurring dev day must not warn alike."""
    deadline, _ = parse("2026-09-09 -- Manifund -- owner: pip -- kind: deadline")
    cadence, _ = parse(
        "every FR -- push -- owner: pip -- kind: cadence -- from: 2026-08-14 "
        "-- until: 2026-08-14"
    )
    assert deadline[0].leads == (14, 7, 2, 0)
    assert cadence[0].leads == (0,)


def test_lead_override():
    got, _ = parse("2026-09-09 -- X -- owner: pip -- kind: task -- lead: 21d,3d")
    assert got[0].leads == (21, 3)


def test_uid_is_stable_across_source_moves():
    """Moving a declaration down a file must not mint a second calendar entry."""
    a, _ = gcc.parse_declaration("2026-08-13 -- X -- owner: pip", "a.md:10", HORIZON)
    b, _ = gcc.parse_declaration("2026-08-13 -- X -- owner: pip", "a.md:99", HORIZON)
    assert a[0].uid == b[0].uid


def test_day_of_alarm_fires_in_the_morning_not_at_midnight():
    assert gcc.trigger_for(0) == "PT8H"
    assert gcc.trigger_for(1) == "-PT16H"
    assert gcc.trigger_for(7) == "-PT160H"


def test_ics_folds_long_lines_to_75_octets():
    c = gcc.Commitment(date(2026, 8, 13), "x" * 400, "pip", "task", "test.md:1")
    out = gcc.render_ics([c], HORIZON)
    assert out.endswith("\r\n")
    for line in out.split("\r\n"):
        assert len(line.encode("utf-8")) <= 75


def test_ics_escapes_separators():
    c = gcc.Commitment(date(2026, 8, 13), "a,b;c", "pip", "task", "s")
    assert "SUMMARY:[TASK] a\\,b\\;c" in gcc.render_ics([c], HORIZON)


def test_committed_outputs_are_not_stale():
    """The pre-commit guard, exercised as a test: if a source moved and nobody
    regenerated, this fails here as well as in the hook."""
    ics, index, _d, _r, _u, errors = gcc.build()
    assert errors == [], errors
    assert gcc.OUT_ICS.read_bytes().decode("utf-8") == ics
    assert gcc.OUT_INDEX.read_text(encoding="utf-8") == index


def test_no_unparsed_date_is_silently_dropped():
    """The whole point. Every future date in a scanned file must appear either as
    a declared commitment or in the UNPARSED table -- never nowhere."""
    horizon = gcc.read_horizon()
    declared, _errors, _claims = gcc.collect_declarations(horizon)
    releases = gcc.collect_roadmap_releases(horizon)
    rows = gcc.collect_unparsed(horizon, declared + releases)
    index = gcc.OUT_INDEX.read_text(encoding="utf-8")
    for when, r, _n, _line in rows:
        assert when.isoformat() in index
        assert r in index


@pytest.mark.parametrize("path", [gcc.OUT_ICS, gcc.OUT_INDEX, gcc.SRC_DECL])
def test_outputs_are_ascii(path):
    """ASCII-only is a hard repo rule (#744) and the .ics extension is outside
    the enforce-standards file list, so it is asserted here instead."""
    path.read_bytes().decode("ascii")
