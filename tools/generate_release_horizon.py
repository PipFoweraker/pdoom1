#!/usr/bin/env python3
"""Generate the release horizon: which version ships when, on which seed, and
what stays comparable -- with the ladder epoch rendered as a FLOOR, never a
forecast.

Layer: GENERATE (with a --check gate, same anti-rot pattern as the DQ index,
the rulings index and the commitment calendar).

THE DEFECT THIS TOOL WAS WRITTEN TO FIX (#1152)
-----------------------------------------------
Two published documents mapped version -> ladder epoch by hand:

    docs/ROADMAP.md               "| v0.15 | Sep 4 | L5 | ..."
    docs/RELEASE_NOMENCLATURE.md  "| Sep 4 | Fri | ... | 0.15 / L4 | Yes |"

#1152 filed those cells as "off by one from v0.14 down". They are not off by
one. The MODEL behind them is wrong, and correcting the numbers would only
re-stale them: both tables encode ONE ladder epoch per minor version, and the
codebase has never behaved that way. Derivable from git history in this repo
(and replayed by --self-test below): six epochs across four minor versions, two
of them inside v0.14.x alone.

  L1  2026-07-23  e0963ca9  (no version move -- the counter was created)
  L2  2026-07-24  f8c36edf  v0.13.0   <- minor bump, ladder cut
  L3  2026-07-27  9abe20a7  (no version move)
  L4  2026-08-07  7368e237  v0.14.0   <- minor bump, ladder cut
  L5  2026-08-21  38528c22  v0.14.2   <- PATCH bump, ladder cut
  L6  2026-08-23  38c5951e  (no version move)

The two axes are independent by construction. The minor version is a property
of RELEASE CADENCE (a monthly train, first Friday). The ladder epoch is a
property of GAMEPLAY CHANGE -- BUILD_VS_LADDER_VERSION_SPLIT.md 3.1: "two
identical inputs could produce a different score, trajectory or RNG stream than
the previous epoch". Any table with one row per minor version and one ladder
cell in it asserts a coupling the code does not have.

RULING: 2026-08-24 -- a minor version bump ALWAYS cuts the ladder, and the ladder MAY ALSO cut mid-version whenever gameplay forks; therefore ladder epochs >= minor versions, always, and the ladder epoch is NEVER forecastable -- flavour: release-cadence -- mechanism: tools/generate_release_horizon.py

THREE TIERS, KEPT VISUALLY APART
--------------------------------
The reason the previous tables rotted is that they rendered three different
kinds of certainty in one typeface:

  1. SCHEDULED       mechanically derivable, no judgement (the monthly train,
                     first Friday, and the ISO-week seed each date implies).
                     GENERATED here.
  2. FORECAST        a plan, revisable, owned by Pip (theme names, headlines).
                     NOT generated -- it stays hand-maintained in ROADMAP.md,
                     labelled as a forecast.
  3. NOT FORECASTABLE  the ladder epoch. Emitted as a FLOOR that ratchets
                     (">= L6"), read from ladder_version.txt. Never a number
                     with a version next to it.

A reader who cannot tell tier 1 from tier 3 will plan the wrong board, which is
exactly what #1152 reported.

THE ISO-WEEK TRAP (live, and it fires on a league night)
--------------------------------------------------------
The featured seed names the ISO week the league opens in (ruling of 2026-08-24,
pinned on the game side by godot/tests/unit/test_iso_week_seed.gd). Formatting
it as f"weekly-{d.year}-w{d.isocalendar()[1]}" is wrong twice over:

  * Friday 1 January 2027 is in ISO week 53 OF 2026. A naive `.year` emits
    `weekly-2027-w53`, a week that does not exist. Use `.isocalendar()[0]`.
  * `w1` and `w01` are DIFFERENT board keys, and a board cannot be tidied
    afterwards. Zero-pad to two digits.

v0.19 is scheduled for Friday 2027-01-01, so this is not a hypothetical. The
Python equivalents of the GDScript boundary cases are pinned in
tests/test_generate_release_horizon.py.

ATOM STORE, AND WHO RULES IT
----------------------------
This tool generates docs/releases/release_horizon.json (schema
`pdoom.release-horizon/0.1`). Under the atomise protocol clause 3 (2026-08-24:
do not build an atom store unless a named party will rule it), the named ruler
for this store is **Pip Foweraker, interim**, stated here at build time as the
protocol requires. Intended eventual owner is the Orchestrator role, which does
not exist yet. Same shape as tools/check_release_ledger.py.

DETERMINISM
-----------
Output is a pure function of tracked files: version.txt, ladder_version.txt and
the ANCHOR pin below. NOTHING READS THE CLOCK. A clock-reading generator goes
stale overnight and trains people to ignore the gate, which is worse than
having no gate. Git history is read only by --self-test, which is why --check
works in a shallow clone. --self-test needs full history and FAILS loudly when
it cannot reach it, rather than reporting a pass it did not measure.

USAGE
-----
    python tools/generate_release_horizon.py             # (re)write outputs
    python tools/generate_release_horizon.py --check     # exit 1 if stale
    python tools/generate_release_horizon.py --report    # stdout, never fails
    python tools/generate_release_horizon.py --self-test # replay real history

EXIT CODES
----------
    0  outputs written, or up to date, or the self-test reproduced history
    1  stale under --check, or the self-test found a mismatch
    2  could not measure (a required input file is missing, or a managed
       generated region has lost its markers) -- NOT a pass
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "version.txt"
LADDER_FILE = ROOT / "ladder_version.txt"

OUT_MD = ROOT / "docs" / "releases" / "RELEASE_HORIZON.md"
OUT_JSON = ROOT / "docs" / "releases" / "release_horizon.json"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
NOMENCLATURE = ROOT / "docs" / "RELEASE_NOMENCLATURE.md"

SCHEMA = "pdoom.release-horizon/0.1"
RULER = "Pip Foweraker, interim"
GENERATOR = "tools/generate_release_horizon.py"

# The pin. ANCHOR_MINOR ships in ANCHOR_YEAR/ANCHOR_MONTH; every later minor
# takes the next month, first Friday. Taken from the ROADMAP Monthly Themes
# table as it stood on 2026-08-24 (v0.15 -> Sep 2026) and from the monthly-train
# ruling of 2026-07-25. One pin, not a table of dates, so there is nothing here
# to drift out of step with itself.
ANCHOR_MINOR = 15
ANCHOR_YEAR = 2026
ANCHOR_MONTH = 9
FINAL_MINOR = 20  # the horizon this document was asked for: out to v0.20

# Fixed-date public holidays worth flagging when the train lands on one. This is
# a FLAG, not a ruling: the tool never moves a date, it says "a human owes a
# decision here". AEST/Australian set, because that is where the cut is made.
FIXED_HOLIDAYS = {
    (1, 1): "New Year's Day",
    (1, 26): "Australia Day",
    (4, 25): "ANZAC Day",
    (12, 25): "Christmas Day",
    (12, 26): "Boxing Day",
}

BEGIN = "<!-- BEGIN GENERATED: release-horizon -- %s -- do not hand-edit -->" % GENERATOR
END = "<!-- END GENERATED: release-horizon -->"

COMPARABILITY = (
    "A score set today stays comparable until the next MINOR version at the "
    "latest, and possibly sooner."
)

UNMEASURED = 2


# --------------------------------------------------------------------------
# the two derivations that must not be got wrong
# --------------------------------------------------------------------------


def iso_week_seed(when: date) -> str:
    """The featured seed for a league opening on `when`.

    `isocalendar()[0]` is the ISO year, which is NOT `when.year` in the last
    days of December or the first days of January. `%02d` because `w1` and `w01`
    are different board keys.
    """
    iso_year, iso_week, _ = when.isocalendar()
    return "weekly-%04d-w%02d" % (iso_year, iso_week)


def first_friday(year: int, month: int) -> date:
    """The release train's ship date for a month (ROADMAP: first Friday)."""
    first = date(year, month, 1)
    return first + timedelta(days=(4 - first.weekday()) % 7)


def fridays_between(start: date, end_exclusive: date) -> list[date]:
    """Every Friday in [start, end_exclusive) -- the weekly seed rolls."""
    out, cur = [], start
    while cur < end_exclusive:
        if cur.weekday() == 4:
            out.append(cur)
        cur += timedelta(days=1)
    return out


def easter_sunday(year: int) -> date:
    """Anonymous Gregorian algorithm (Meeus/Jones/Butcher)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    lam = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * lam) // 451
    month, day = divmod(h + lam - 7 * m + 114, 31)
    return date(year, month, day + 1)


def holiday_name(when: date) -> str | None:
    """Named public holiday on `when`, or None.

    Good Friday is included because it is ALWAYS a Friday, so it is the one
    holiday guaranteed to be able to collide with a first-Friday train -- and it
    does: Friday 2026-04-03 was both.
    """
    fixed = FIXED_HOLIDAYS.get((when.month, when.day))
    if fixed:
        return fixed
    if when == easter_sunday(when.year) - timedelta(days=2):
        return "Good Friday"
    return None


# --------------------------------------------------------------------------
# inputs
# --------------------------------------------------------------------------


def read_text(path: Path) -> str:
    if not path.exists():
        raise SystemExit("FATAL: missing input %s -- cannot measure." % path.name)
    return path.read_text(encoding="utf-8").strip()


def current_version() -> tuple[int, int, int]:
    raw = read_text(VERSION_FILE)
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", raw)
    if not m:
        raise SystemExit("FATAL: version.txt is %r, not major.minor.patch." % raw)
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def ladder_floor() -> int:
    raw = read_text(LADDER_FILE)
    if not raw.isdigit():
        raise SystemExit("FATAL: ladder_version.txt is %r, not an integer." % raw)
    return int(raw)


def scheduled_rows() -> list[dict]:
    """The SCHEDULED tier: one row per remaining minor version out to v0.20.

    The starting row comes from version.txt (the next minor after the one that
    shipped), the month comes from the ANCHOR pin. So when v0.15 ships, the v0.15
    row leaves the table on its own and v0.16 keeps its October date -- no
    second place to edit, and no way for the table to advertise a date in the
    past.
    """
    major, minor, _ = current_version()
    rows: list[dict] = []
    for target in range(minor + 1, FINAL_MINOR + 1):
        offset = target - ANCHOR_MINOR
        month_index = (ANCHOR_YEAR * 12 + (ANCHOR_MONTH - 1)) + offset
        year, month0 = divmod(month_index, 12)
        ships = first_friday(year, month0 + 1)
        # The cycle runs to the NEXT month's first Friday, which is computed even
        # for the last row -- the weekly seeds keep rolling after v0.20 ships.
        next_year, next_month0 = divmod(month_index + 1, 12)
        cycle = fridays_between(ships, first_friday(next_year, next_month0 + 1))
        rows.append(
            {
                "version": "%d.%d" % (major, target),
                "ships": ships.isoformat(),
                "iso_year": ships.isocalendar()[0],
                "iso_week": ships.isocalendar()[1],
                "featured_seed": iso_week_seed(ships),
                "cycle_seeds": [iso_week_seed(f) for f in cycle],
                "holiday": holiday_name(ships),
            }
        )
    return rows


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------


def human_date(iso: str) -> str:
    """`Fri 4 Sep 2026`. Deliberately NOT ISO in the injected doc regions: the
    commitment calendar's prose scan treats every future ISO date in docs/*.md
    as an undeclared commitment, and a generated forecast is not a promise."""
    when = date.fromisoformat(iso)
    return "%s %d %s %d" % (
        when.strftime("%a"),
        when.day,
        when.strftime("%b"),
        when.year,
    )


def floor_phrase(floor: int) -> str:
    return ">= L%d" % floor


def render_markdown(rows: list[dict], floor: int, version: str) -> str:
    lines = [
        "# Release horizon -- versions, dates, seeds, and what stays comparable",
        "",
        "**GENERATED by `%s` -- do not hand-edit.** Regenerate after bumping" % GENERATOR,
        "`version.txt` or `ladder_version.txt`; `--check` blocks a stale commit.",
        "",
        "Three kinds of certainty live in this document and are kept apart on",
        "purpose. Mixing them in one table is what rotted the tables this file",
        "replaces (issue #1152).",
        "",
        "| Tier | Kind of claim | Who owns it | Generated? |",
        "|---|---|---|---|",
        "| 1. SCHEDULED | mechanically derivable from a rule | the calendar | yes, below |",
        "| 2. FORECAST | a plan, revisable | Pip | no -- `../ROADMAP.md` |",
        "| 3. NOT FORECASTABLE | a consequence of gameplay change | nobody, in advance | floor only |",
        "",
        "Current inputs: `version.txt` = **%s**, `ladder_version.txt` = **L%d**."
        % (version, floor),
        "",
        "---",
        "",
        "## Tier 1 -- SCHEDULED",
        "",
        "Monthly release train, first Friday of the month (`../ROADMAP.md` cadence",
        "ruling, 2026-07-25). The featured seed names the ISO week the league opens",
        "in (ruling 2026-08-24; pinned by `godot/tests/unit/test_iso_week_seed.gd`",
        "and, in Python, by `tests/test_generate_release_horizon.py`).",
        "",
        "Nothing here is a judgement call: change the rule or the pin, and every",
        "cell moves with it.",
        "",
        "| Version | Ships | ISO week | Featured seed at open | Weekly seeds in cycle |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        marker = " **(!)**" if row["holiday"] else ""
        weeks = ", ".join(s.rsplit("-", 1)[-1] for s in row["cycle_seeds"])
        lines.append(
            "| v%s | %s%s | %d-w%02d | `%s` | %s |"
            % (
                row["version"],
                row["ships"],
                marker,
                row["iso_year"],
                row["iso_week"],
                row["featured_seed"],
                weeks,
            )
        )
    lines.append("")
    flagged = [r for r in rows if r["holiday"]]
    if flagged:
        lines.append("**(!) The train lands on a public holiday.** The rule is applied as")
        lines.append("written rather than quietly adjusted; a date is only moved by a ruling.")
        lines.append("")
        for row in flagged:
            lines.append(
                "- **v%s ships %s -- %s.** Hold, or accept? Ruling owed."
                % (row["version"], row["ships"], row["holiday"])
            )
        lines.append("")
    lines += [
        "Read the seed column carefully at the year boundary: the ISO year is not",
        "the calendar year. Friday 2027-01-01 is in ISO **week 53 of 2026**, so",
        "v0.19 opens on `weekly-2026-w53`. `weekly-2027-w53` is a week that does",
        "not exist, and it is what a generator formatting `date.year` emits.",
        "",
        "---",
        "",
        "## Tier 2 -- FORECAST",
        "",
        "Theme names and headlines are a PLAN, and Pip names them",
        "(`../RELEASE_NOMENCLATURE.md`). They are deliberately NOT generated and",
        "are not restated here -- one hand-maintained copy, in the Monthly Themes",
        "table of `../ROADMAP.md`, labelled as a forecast.",
        "",
        "---",
        "",
        "## Tier 3 -- NOT FORECASTABLE: the ladder epoch",
        "",
        "> **Floor: `%s`.** Every future epoch is at or above this number." % floor_phrase(floor),
        "> The floor ratchets: it may rise, never fall. There is no row in this",
        "> file that predicts a specific epoch for a specific version, because no",
        "> such prediction can be made.",
        "",
        "A minor version bump ALWAYS cuts the ladder. The ladder MAY ALSO cut",
        "mid-version, as often as gameplay forks require, and has done so more",
        "often than not. So ladder epochs >= minor versions, always, and the next",
        "epoch number is not derivable from the next version number. The counts are",
        "deliberately not written here: `--self-test` measures them from git on",
        "demand, and a number typed into a document is a number that goes stale.",
        "",
        "**Comparability horizon (the useful thing a player can be told).**",
        "%s" % COMPARABILITY,
        "It is a CEILING, not a schedule: the next minor version is the last date a",
        "current score can survive to, not the date it is guaranteed to survive to.",
        "",
        "`--self-test` replays the real epoch history and proves the coupling test",
        "returns BOTH answers on it -- a check that can only return one answer",
        "proves nothing.",
        "",
        "## Two different `L<n>` namespaces",
        "",
        "`L<n>` here is a LADDER EPOCH (`ladder_version.txt`). It is a different",
        "namespace from the `L0-L3` distribution update ladder in",
        "`../GLOSSARY.md` and `../design/UPDATER_DESIGN.md`, and from the `L0..L10`",
        "build/art lane numbering. Same notation, unrelated meanings, all spoken in",
        "league week.",
        "",
    ]
    # rstrip then one newline: pre-commit's end-of-file-fixer rewrites a file
    # that ends in a blank line, which would make --check red on the very commit
    # that generated it.
    return "\n".join(lines).rstrip("\n") + "\n"


def render_json(rows: list[dict], floor: int, version: str) -> str:
    payload = {
        "schema": SCHEMA,
        "generated_by": GENERATOR,
        "ruler": RULER,
        "current_version": version,
        "ladder_floor": floor,
        "ladder_floor_label": floor_phrase(floor),
        "ladder_forecastable": False,
        "comparability_horizon": COMPARABILITY,
        "anchor": {
            "version": "0.%d" % ANCHOR_MINOR,
            "year": ANCHOR_YEAR,
            "month": ANCHOR_MONTH,
            "rule": "monthly release train, first Friday",
        },
        "scheduled": rows,
    }
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def render_roadmap_block(rows: list[dict], floor: int) -> str:
    lines = [
        "**SCHEDULED (tier 1 -- mechanical, not a plan).** Monthly train, first",
        "Friday. Generated from `version.txt` plus the cadence rule; the full table",
        "with weekly seeds is [`releases/RELEASE_HORIZON.md`](releases/RELEASE_HORIZON.md).",
        "",
        "| Version | Ships | Featured seed at open |",
        "|---|---|---|",
    ]
    for row in rows:
        flag = " (%s)" % row["holiday"] if row["holiday"] else ""
        lines.append(
            "| v%s | %s%s | `%s` |"
            % (row["version"], human_date(row["ships"]), flag, row["featured_seed"])
        )
    lines += [
        "",
        "**NOT FORECASTABLE (tier 3) -- the ladder epoch.** Floor today: **`%s`**."
        % floor_phrase(floor),
        "A minor bump always cuts the ladder; the ladder may also cut mid-version",
        "whenever gameplay forks, and most cuts so far were exactly that. No version",
        "in the table above carries a predicted epoch, because none can be predicted",
        "(`python tools/generate_release_horizon.py --self-test` measures the",
        "history rather than restating it).",
        "",
        "**Comparability horizon.** %s" % COMPARABILITY,
    ]
    return "\n".join(lines)


def render_nomenclature_block(rows: list[dict], floor: int) -> str:
    lines = [
        "**Forward view (tier 1, SCHEDULED -- generated).** Dates are the monthly",
        "train's first Friday; seeds name the ISO week the league opens in. Weekly",
        "seeds for the Fridays in between are in",
        "[`releases/RELEASE_HORIZON.md`](releases/RELEASE_HORIZON.md).",
        "",
        "| Version | Ships | Unit | Featured seed at open |",
        "|---|---|---|---|",
    ]
    for row in rows:
        flag = " (%s)" % row["holiday"] if row["holiday"] else ""
        lines.append(
            "| **v%s** | %s%s | Epoch+Seed | `%s` |"
            % (row["version"], human_date(row["ships"]), flag, row["featured_seed"])
        )
    lines += [
        "",
        "**No ladder column, on purpose (tier 3, NOT FORECASTABLE).** Floor today:",
        "**`%s`**, ratcheting. A minor bump always cuts the ladder, and the ladder"
        % floor_phrase(floor),
        "may also cut mid-version whenever gameplay forks -- so epochs >= minors and",
        "the next epoch number cannot be read off the next version number. What can",
        "be said, and is what a player needs: **%s**" % COMPARABILITY,
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# managed regions
# --------------------------------------------------------------------------


def splice(path: Path, block: str) -> str:
    """Return `path`'s text with the managed region replaced by `block`."""
    text = path.read_text(encoding="utf-8")
    start = text.find(BEGIN)
    end = text.find(END)
    if start < 0 or end < 0 or end < start:
        raise SystemExit(
            "FATAL: %s has lost its generated-region markers. Restore both lines:\n"
            "  %s\n  %s" % (path.name, BEGIN, END)
        )
    return text[:start] + BEGIN + "\n" + block + "\n" + text[end:]


def targets() -> list[tuple[Path, str]]:
    rows = scheduled_rows()
    floor = ladder_floor()
    version = read_text(VERSION_FILE)
    return [
        (OUT_MD, render_markdown(rows, floor, version)),
        (OUT_JSON, render_json(rows, floor, version)),
        (ROADMAP, splice(ROADMAP, render_roadmap_block(rows, floor))),
        (NOMENCLATURE, splice(NOMENCLATURE, render_nomenclature_block(rows, floor))),
    ]


def write_all() -> list[Path]:
    written = []
    for path, content in targets():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        # newline="\n" explicitly: Path.write_text() uses the platform default,
        # which produces CRLF on Windows and LF on CI, so a byte-correct file
        # authored on Windows reports STALE under --check on Ubuntu. Measured
        # 2026-08-24, on this very generator.
        path.write_text(content, encoding="utf-8", newline="\n")
        written.append(path)
    return written


def stale() -> list[Path]:
    out = []
    for path, content in targets():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            out.append(path)
    return out


# --------------------------------------------------------------------------
# self-test: the coupling classifier, replayed against real history
# --------------------------------------------------------------------------


def git(*args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(ROOT), *args], capture_output=True, text=True, timeout=60
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def value_at(commit: str, path: str) -> str | None:
    out = git("show", "%s:%s" % (commit, path))
    return out.strip() if out is not None else None


def minor_of(raw: str | None) -> tuple[int, int] | None:
    if not raw:
        return None
    m = re.match(r"^(\d+)\.(\d+)", raw)
    return (int(m.group(1)), int(m.group(2))) if m else None


def cut_with_minor_bump(commit: str) -> bool | None:
    """THE CLASSIFIER. For a commit that cut the ladder: did the same commit
    also bump the MINOR version?

    True  -> that epoch is explained by the release train.
    False -> that epoch is a mid-version gameplay fork, and no version-keyed
             table could ever have predicted it.
    None  -> could not measure (history unreachable). Never silently False.
    """
    parent = git("rev-parse", "%s^" % commit)
    if parent is None:
        return None
    before, after = minor_of(value_at(parent, "version.txt")), minor_of(
        value_at(commit, "version.txt")
    )
    if after is None:
        return None
    return before is not None and after != before


def epoch_cut_commits() -> list[tuple[str, str, str]]:
    """Every commit that changed ladder_version.txt, oldest first."""
    log = git("log", "--reverse", "--format=%H%x1f%cs", "--", "ladder_version.txt")
    if not log:
        return []
    rows = []
    for line in log.splitlines():
        if "\x1f" not in line:
            continue
        sha, when = line.split("\x1f", 1)
        rows.append((sha, when, value_at(sha, "ladder_version.txt") or "?"))
    return rows


def self_test() -> int:
    print("[self-test] replaying the real epoch history from git\n")
    cuts = epoch_cut_commits()
    if not cuts:
        print("[self-test] FAIL: no ladder_version.txt history reachable, so nothing")
        print("            was proven. Needs a full clone (fetch-depth: 0).")
        return 1

    answers: dict[bool, list[str]] = {True: [], False: []}
    unknown = []
    created = cuts[0][0]  # the commit that created the counter forks nothing
    print("  epoch  date        commit    version at cut  minor bump?")
    for sha, when, epoch in cuts:
        if sha == created:
            print("  L%-4s  %s  %s  %-14s  %s" % (epoch, when, sha[:8], "--", "counter created"))
            continue
        verdict = cut_with_minor_bump(sha)
        ver = value_at(sha, "version.txt") or "?"
        label = {True: "YES", False: "no", None: "UNKNOWN"}[verdict]
        print("  L%-4s  %s  %s  %-14s  %s" % (epoch, when, sha[:8], ver, label))
        if verdict is None:
            unknown.append(sha)
        else:
            answers[verdict].append(sha)

    print()
    failed = False
    if not answers[True]:
        print("[self-test] FAIL: the classifier never returned YES on real history.")
        failed = True
    if not answers[False]:
        print("[self-test] FAIL: the classifier never returned NO on real history.")
        failed = True
    if unknown:
        print("[self-test] FAIL: %d cut(s) unmeasurable -- shallow clone?" % len(unknown))
        failed = True

    # The claim the generated documents rest on, checked rather than asserted.
    epochs = len(cuts)
    minors = len(answers[True])
    if not failed and epochs <= minors:
        print("[self-test] FAIL: history shows %d epochs and %d minor-coupled" % (epochs, minors))
        print("            cuts; the 'epochs >= minors' claim needs re-deriving.")
        failed = True

    # The ISO-week trap, proven live rather than described.
    trap = date(2027, 1, 1)
    naive = "weekly-%04d-w%02d" % (trap.year, trap.isocalendar()[1])
    if iso_week_seed(trap) == naive:
        print("[self-test] FAIL: the ISO-year guard is not live -- 2027-01-01 emitted %s" % naive)
        failed = True

    if failed:
        return 1
    print(
        "[self-test] PASS: %d epoch cut(s) = 1 counter creation + %d explained by a"
        % (epochs, minors)
    )
    print("            minor bump + %d mid-version gameplay fork(s)." % len(answers[False]))
    print("            Both answers occur in real history, so the classifier is")
    print("            capable of either, and a version-keyed ladder forecast is")
    print("            falsified by %d case(s)." % len(answers[False]))
    print(
        "            ISO-year guard live: 2027-01-01 -> %s (naive: %s)."
        % (iso_week_seed(trap), naive)
    )
    return 0


# --------------------------------------------------------------------------


def report() -> int:
    rows = scheduled_rows()
    floor = ladder_floor()
    print(
        "Release horizon (version.txt %s, ladder %s)"
        % (read_text(VERSION_FILE), floor_phrase(floor))
    )
    for row in rows:
        flag = "  (!) %s" % row["holiday"] if row["holiday"] else ""
        print("  v%-5s %s  %s%s" % (row["version"], row["ships"], row["featured_seed"], flag))
    print("  ladder epoch: %s -- NOT FORECASTABLE" % floor_phrase(floor))
    print("  %s" % COMPARABILITY)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if any output is stale")
    ap.add_argument("--report", action="store_true", help="print the horizon; never fails")
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="replay the real epoch history and prove the classifier returns both answers",
    )
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.report:
        return report()

    if args.check:
        bad = stale()
        if bad:
            print("STALE release horizon. Run: python %s" % GENERATOR)
            for path in bad:
                print("  - %s" % path.relative_to(ROOT).as_posix())
            return 1
        print(
            "Release horizon up to date (%s, ladder %s)."
            % (read_text(VERSION_FILE), floor_phrase(ladder_floor()))
        )
        return 0

    written = write_all()
    if not written:
        print("Release horizon already up to date.")
    for path in written:
        print("wrote %s" % path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit as exc:  # keep the "could not measure" exit distinct from "stale"
        if isinstance(exc.code, str):
            print(exc.code)
            sys.exit(UNMEASURED)
        raise
