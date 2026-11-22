#!/usr/bin/env python3
"""Generate the rulings index + the cross-repo rulings.json from RULING: declarations.

Layer: GENERATE

Why this exists
---------------
Measured 2026-08-15: more than forty rulings already live in this tree as prose
(`ruled by Pip`, `Pip ruled`, `ruled 2026-..`) scattered across .py docstrings,
.gd comments, .json data, docs and tests. Capture was never the problem. What was
missing:

  1. a home for a ruling with no code yet ("the epoch counter starts at 1"),
  2. recall by FLAVOUR -- Pip, 2026-08-15: "these will show up again in similar
     flavours" -- so a new question can be answered by precedent,
  3. supersession: nothing marked which of two conflicting rulings is current.

The convention and the argued reasoning live in
`docs/rulings/RULINGS_CONVENTION.md`. This file is the machine half.

Design is copied deliberately from `scripts/generate_commitment_calendar.py`,
which solved the same shape for dates. Same one-line declaration writable
anywhere, same generated index, same --check gate, and above all the same
never-drop doctrine:

    "A calendar that silently omits is worse than no calendar, because it looks
     complete."

So a prose ruling with no declaration is emitted as UNDECLARED in both outputs
rather than quietly missing.

Determinism
-----------
Output is a pure function of tracked files. Nothing reads the clock. A
clock-reading generator goes stale overnight and trains people to ignore the
gate, which is worse than having no gate.

Usage
-----
    python scripts/generate_rulings.py            # (re)write both outputs
    python scripts/generate_rulings.py --check    # exit 1 if stale (pre-commit)
    python scripts/generate_rulings.py --report   # stdout summary, never fails
    python scripts/generate_rulings.py --flavour <slug>   # precedent lookup
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "docs" / "rulings" / "RULINGS.md"
OUT_JSON = ROOT / "docs" / "rulings" / "rulings.json"
LEDGER = ROOT / "docs" / "rulings" / "LEDGER.md"
CONVENTION = "docs/rulings/RULINGS_CONVENTION.md"
SCHEMA = "pdoom.rulings/0.1"

# Text files worth scanning. Binary and generated trees are excluded; the
# generated outputs themselves are excluded or the scan would echo its own text
# back as declarations and the --check gate would never converge.
SCAN_SUFFIXES = {".md", ".py", ".gd", ".json", ".yaml", ".yml", ".txt", ".cfg", ".toml"}
SCAN_EXCLUDE = (
    "docs/rulings/RULINGS.md",
    "docs/rulings/rulings.json",
    # The convention doc contains EXAMPLE declarations. Scanning it would turn
    # documentation into data -- three worked examples showed up as real rulings
    # on the first run. Examples must never become facts.
    "docs/rulings/RULINGS_CONVENTION.md",
    "godot/.godot/",
    ".claude/",
)

DECL = re.compile(r"RULING:\s*(\d{4}-\d{2}-\d{2})\s*--\s*(.+)")

# The informal patterns already in the tree. Heuristic on purpose: a false
# positive costs one glance, a false negative loses a decision.
PROSE = re.compile(r"\bruled by \w+\b|\b\w+ ruled\b|\bruled (?:on )?\d{4}-\d{2}-\d{2}\b", re.I)


def repo_name() -> str:
    """Derive the repo name from the git remote, so the script is copy-portable."""
    try:
        url = subprocess.run(
            ["git", "-C", str(ROOT), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return url.rstrip("/").rsplit("/", 1)[-1].removesuffix(".git") or ROOT.name
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ROOT.name


def tracked_files() -> list[Path]:
    try:
        # --others --exclude-standard includes files that are NEW but not
        # gitignored. Without it a freshly written ruling is invisible until it
        # is committed, so you would have to commit a ruling before the index
        # could show it -- and --check would go stale the moment you added one.
        out = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    keep = []
    for rel in out:
        if any(rel.startswith(x) for x in SCAN_EXCLUDE):
            continue
        if Path(rel).suffix.lower() not in SCAN_SUFFIXES:
            continue
        keep.append(ROOT / rel)
    return keep


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


# Keys are CODEPOINTS, not literals: this file is itself subject to the ASCII
# gate (issue #744), so spelling the characters out here would fail the very
# check this map exists to serve. str.translate takes an ordinal-keyed dict.
_ASCII_MAP = {
    0x2014: "--",  # em dash
    0x2013: "-",  # en dash
    0x2018: "'",  # left single quote
    0x2019: "'",  # right single quote / apostrophe
    0x201C: '"',  # left double quote
    0x201D: '"',  # right double quote
    0x2026: "...",  # ellipsis
    0x00A0: " ",  # non-breaking space
    0x2192: "->",  # right arrow
    0x2022: "*",  # bullet
}


def to_ascii(text: str) -> str:
    """Fold known punctuation, then hard-replace anything else non-ASCII."""
    return text.translate(_ASCII_MAP).encode("ascii", "replace").decode("ascii")


def parse_fields(tail: str) -> tuple[str, dict]:
    """Split '<ruling> -- flavour: x -- mechanism: y' into (ruling, fields)."""
    parts = [p.strip() for p in tail.split(" -- ")]
    ruling = parts[0].strip()
    fields = {}
    for part in parts[1:]:
        if ":" not in part:
            continue
        key, _, value = part.partition(":")
        fields[key.strip().lower()] = value.strip()
    return ruling, fields


# ---------------------------------------------------------------- other stores
# CONSOLIDATION, ruled by Pip 2026-08-21.
#
# An audit on 2026-08-21 found FIVE places rulings were being recorded, four of
# which predated this file. The instruction was to consolidate them into one.
#
# What is NOT done here, and why: the five are not competing stores, they are
# GENRES, and merging the files would destroy what each genre carries.
#   * an ADR is a full argument -- Context, Decision, Consequences. Nineteen of
#     them, each several pages. Flattening one into a single line deletes the
#     reasoning that makes it re-checkable later, which is the entire point of an
#     ADR.
#   * SPOKEN_RULINGS_* are TRANSCRIPTS. They are evidence of what was said, with
#     a "not yet re-read by him" caveat on them. Rewriting evidence into a
#     summary is the exact error `check_provenance.py` refuses to make about
#     asset origins.
#   * decision-cards are the INPUT a ruling was made from, not the ruling.
#
# So the record is consolidated and the sources are not: ONE index, five
# sources, each ruling carrying the `kind` of thing it came from and a path back
# to the full text. Nothing is moved, nothing is rewritten, and every ruling in
# the estate becomes findable in one place for the first time.
ADR_DIR = ROOT / "docs" / "game-design" / "decisions"
ADR_TITLE = re.compile(r"^#\s*(ADR-\d+)\s*--\s*(.+?)\s*$", re.M)
# Status and Summary WRAP in the source markdown -- a continuation line is
# indented and does not start a new `- **Field:**`. Capturing only the first line
# truncated ADR-0001's status mid-word ("... lead-time"), which is precisely the
# half-right parse this file refuses to make of transcripts. Consume until the
# next field or a blank line, then collapse the whitespace.
ADR_FIELD = {
    "status": re.compile(r"^-\s*\*\*Status:\*\*\s*(.+?)(?=\n-\s*\*\*|\n\n)", re.M | re.S),
    "date": re.compile(r"^-\s*\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})", re.M),
    "summary": re.compile(r"^-\s*\*\*Summary:\*\*\s*(.+?)(?=\n-\s*\*\*|\n\n)", re.M | re.S),
}


def unwrap(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


# Documents whose PURPOSE is recording rulings. Listed as sources rather than
# parsed line-by-line: their internal structure varies per session, and a
# half-right parse of a transcript is worse than an honest pointer to it.
RULING_DOC_GLOBS = [
    "docs/SPOKEN_RULINGS_*.md",
    "docs/SPOKEN_COMMENTS_*.md",
    "docs/game-design/*RULINGS*.md",
    "docs/decision-cards/*",
]
DOC_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def collect_adrs(repo: str) -> tuple[list[dict], list[str]]:
    """Each ADR is one ruling, summarised, pointing at its own full argument."""
    out, errors = [], []
    if not ADR_DIR.is_dir():
        return out, errors
    for path in sorted(ADR_DIR.glob("ADR-0*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        title = ADR_TITLE.search(text)
        fields = {k: rx.search(text) for k, rx in ADR_FIELD.items()}
        if not title or not all(fields.values()):
            missing = [k for k, v in fields.items() if not v] + ([] if title else ["title"])
            errors.append(f"{rel(path)}: ADR header incomplete, missing {missing}")
            continue
        adr_id, headline = title.group(1), title.group(2)
        date = fields["date"].group(1)
        status = unwrap(fields["status"].group(1))
        summary = to_ascii(unwrap(fields["summary"].group(1)))
        digest = hashlib.sha256(f"{adr_id}{summary}".encode("utf-8")).hexdigest()[:8]
        out.append(
            {
                "id": f"{repo}:{date}:{digest}",
                "date": date,
                "ruling": to_ascii(f"{adr_id} -- {headline}"),
                "summary": summary,
                "flavour": "architecture",
                "kind": "adr",
                "status": to_ascii(status),
                "by": "Pip",
                "mechanism": None,
                "supersedes": None,
                "superseded_by": None,
                "source": f"{rel(path)}:1",
            }
        )
    return out, errors


def collect_ruling_docs(repo: str) -> list[dict]:
    """Ruling-purposed documents, pointed AT rather than parsed."""
    out = []
    seen = set()
    for pattern in RULING_DOC_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            r = rel(path)
            if r in seen or any(r.startswith(x) for x in SCAN_EXCLUDE):
                continue
            seen.add(r)
            m = DOC_DATE.search(path.name)
            date = m.group(1) if m else "0000-00-00"
            kind = "card" if "/decision-cards/" in r else "session"
            digest = hashlib.sha256(r.encode("utf-8")).hexdigest()[:8]
            out.append(
                {
                    "id": f"{repo}:{date}:{digest}",
                    "date": date,
                    "ruling": to_ascii(path.stem.replace("_", " ")),
                    "summary": (
                        "Ruling-purposed document. Read it in full; it is not "
                        "summarised here because a half-right parse of a "
                        "transcript is worse than a pointer to it."
                    ),
                    "flavour": "session-record",
                    "kind": kind,
                    "status": "",
                    "by": "Pip",
                    "mechanism": None,
                    "supersedes": None,
                    "superseded_by": None,
                    "source": f"{r}:1",
                }
            )
    return out


def collect() -> tuple[list[dict], list[dict], list[str]]:
    """Return (rulings, undeclared, errors). Deterministic: sorted by source."""
    rulings: list[dict] = []
    undeclared: list[dict] = []
    errors: list[str] = []
    repo = repo_name()

    for path in sorted(tracked_files(), key=rel):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            errors.append(f"{rel(path)}: unreadable ({exc})")
            continue
        lines = text.splitlines()
        # Skip GENERATED artifacts. They quote prose from their own sources, so
        # scanning them double-counts, and worse: the commitment calendar's
        # generated index contains ruling-shaped prose, so the two generators
        # ping-ponged -- regenerating either made the other stale, and --check
        # could never be satisfied. Detected by the repo's own "GENERATED"
        # header convention rather than a hardcoded list, so a new generated
        # file is excluded the day it appears.
        if any("GENERATED" in ln for ln in lines[:6]):
            continue
        for lineno, line in enumerate(lines, 1):
            m = DECL.search(line)
            if m:
                date, tail = m.group(1), m.group(2)
                ruling, fields = parse_fields(tail)
                if not ruling:
                    errors.append(f"{rel(path)}:{lineno}: RULING: with no text")
                    continue
                if "flavour" not in fields:
                    errors.append(
                        f"{rel(path)}:{lineno}: RULING: has no 'flavour:' field "
                        f"-- it cannot be recalled by flavour, which is the point"
                    )
                digest = hashlib.sha256(ruling.encode("utf-8")).hexdigest()[:8]
                rulings.append(
                    {
                        "id": f"{repo}:{date}:{digest}",
                        "date": date,
                        "ruling": to_ascii(ruling),
                        "summary": "",
                        "flavour": fields.get("flavour", "UNFILED"),
                        "kind": "declaration",
                        "status": "",
                        "by": fields.get("by", "Pip"),
                        "mechanism": fields.get("mechanism") or None,
                        "supersedes": fields.get("supersedes") or None,
                        "superseded_by": None,
                        "source": f"{rel(path)}:{lineno}",
                    }
                )
            elif PROSE.search(line):
                undeclared.append(
                    {
                        "source": f"{rel(path)}:{lineno}",
                        # rstrip AFTER truncating: a 200-char cut can land
                        # mid-line and leave a trailing space, which the
                        # trailing-whitespace hook then strips mid-commit --
                        # changing a file this generator just wrote and aborting
                        # the commit.
                        "text": to_ascii(line.strip()[:200]).rstrip(),
                    }
                )

    # The other four stores. Added last so a hand-written declaration always
    # wins a digest collision with a derived record.
    adrs, adr_errors = collect_adrs(repo)
    rulings.extend(adrs)
    errors.extend(adr_errors)
    rulings.extend(collect_ruling_docs(repo))

    # Resolve supersession both ways so a consumer never has to join it itself.
    by_id = {r["id"]: r for r in rulings}
    for r in rulings:
        target = r["supersedes"]
        if target and target in by_id:
            by_id[target]["superseded_by"] = r["id"]
        elif target:
            errors.append(f"{r['source']}: supersedes unknown id {target!r}")

    rulings.sort(key=lambda r: (r["date"], r["source"]))
    undeclared.sort(key=lambda u: u["source"])
    return rulings, undeclared, errors


def render_md(rulings: list[dict], undeclared: list[dict], errors: list[str]) -> str:
    by_flavour: dict[str, list[dict]] = defaultdict(list)
    for r in rulings:
        by_flavour[r["flavour"]].append(r)
    no_mech = [r for r in rulings if not r["mechanism"] and not r["superseded_by"]]

    out = [
        "# Rulings index (GENERATED -- do not hand-edit)",
        "",
        "> Derived from `RULING:` declarations in tracked files by",
        "> `scripts/generate_rulings.py`. Regenerate with",
        "> `python scripts/generate_rulings.py`. The convention, and why it looks",
        f"> like this, is argued in `{CONVENTION}`.",
        "",
        f"**{len(rulings)} ruling(s)** across **{len(by_flavour)} flavour(s)**. "
        f"**{len(undeclared)}** prose ruling(s) not yet declared.",
        "",
        "## One index, five sources",
        "",
        "Consolidated 2026-08-21. The estate had five places rulings were recorded;",
        "they are GENRES, not rivals, so the record is unified here while the sources",
        "keep their form. An ADR is a full argument and a transcript is evidence --",
        "flattening either into one line would delete what makes it worth having.",
        "",
        "| kind | n | what it is | where |",
        "|---|---:|---|---|",
    ]
    kind_desc = {
        "declaration": ("a `RULING:` line written next to what it governs", "anywhere"),
        "adr": ("a full architecture argument, summarised here", "`docs/game-design/decisions/`"),
        "session": (
            "a transcript or workshop ruling set, pointed at",
            "`docs/SPOKEN_*`, `*RULINGS*`",
        ),
        "card": ("the input a ruling was made from", "`docs/decision-cards/`"),
    }
    by_kind: dict[str, list[dict]] = defaultdict(list)
    for r in rulings:
        by_kind[r.get("kind", "declaration")].append(r)
    for kind in ("declaration", "adr", "session", "card"):
        if kind not in by_kind:
            continue
        what, where = kind_desc[kind]
        out.append(f"| `{kind}` | {len(by_kind[kind])} | {what} | {where} |")
    out += [
        "",
        "## By flavour",
        "",
        "Recall by flavour is the point: before ruling on something, look for the",
        "flavour it belongs to and read what was already decided there.",
        "",
    ]

    for flavour in sorted(by_flavour):
        group = by_flavour[flavour]
        singleton = " (only one so far)" if len(group) == 1 else ""
        out += [
            f"### `{flavour}`{singleton}",
            "",
            "| date | ruling | mechanism | source |",
            "|---|---|---|---|",
        ]
        for r in group:
            mech = f"`{r['mechanism']}`" if r["mechanism"] else "-- none --"
            text = r["ruling"]
            if r["superseded_by"]:
                text = f"~~{text}~~ (superseded by `{r['superseded_by']}`)"
            out.append(f"| {r['date']} | {text} | {mech} | `{r['source']}` |")
        out.append("")

    out += [
        "## Nothing will re-ask these",
        "",
        "Rulings with no `mechanism:`. Pip's doctrine (2026-08-11): what forces a",
        "question to be resolved later is a MECHANISM, not a document. This section",
        "reports, it does not block -- naming a mechanism is optional by design, and",
        "an empty list here is not a goal.",
        "",
    ]
    if no_mech:
        for r in no_mech:
            out.append(f"- `{r['id']}` -- {r['ruling']} (`{r['source']}`)")
    else:
        out.append("None -- every active ruling names something that will re-ask it.")
    out.append("")

    out += [
        "## UNDECLARED -- prose that reads like a ruling",
        "",
        "Found by heuristic scan. These are a WORK LIST, not rulings: each needs a",
        "`RULING:` line, or is a false positive to ignore. They are listed rather",
        "than dropped because an index that silently omits looks complete when it",
        "is not.",
        "",
    ]
    if undeclared:
        for u in undeclared:
            out.append(f"- `{u['source']}` -- {u['text']}")
    else:
        out.append("None.")
    out.append("")

    if errors:
        out += ["## Errors", ""]
        out += [f"- {e}" for e in errors]
        out.append("")

    return "\n".join(out)


def render_json(rulings: list[dict], undeclared: list[dict]) -> str:
    doc = {
        "schema": SCHEMA,
        "repo": repo_name(),
        "generated_from": "tracked files at HEAD",
        "convention": CONVENTION,
        "count": len(rulings),
        "rulings": rulings,
        "undeclared": undeclared,
    }
    return json.dumps(doc, indent=2, ensure_ascii=True) + "\n"


def build() -> tuple[str, str, list[dict], list[dict], list[str]]:
    rulings, undeclared, errors = collect()
    return (
        render_md(rulings, undeclared, errors),
        render_json(rulings, undeclared),
        (rulings),
        undeclared,
        errors,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the outputs are stale")
    ap.add_argument("--report", action="store_true", help="stdout summary; never fails")
    ap.add_argument("--flavour", help="print prior rulings in this flavour (precedent lookup)")
    args = ap.parse_args()

    md, js, rulings, undeclared, errors = build()

    if args.flavour:
        hits = [r for r in rulings if r["flavour"] == args.flavour]
        if not hits:
            flavours = sorted({r["flavour"] for r in rulings})
            print(f"no prior rulings in flavour {args.flavour!r}.")
            print("known flavours: " + (", ".join(flavours) if flavours else "(none yet)"))
            return 0
        print(f"{len(hits)} prior ruling(s) in flavour {args.flavour!r}:\n")
        for r in hits:
            mark = " [SUPERSEDED]" if r["superseded_by"] else ""
            print(f"  {r['date']}{mark}  {r['ruling']}")
            print(f"     mechanism: {r['mechanism'] or '-- none --'}")
            print(f"     source:    {r['source']}\n")
        return 0

    if args.report:
        print(f"rulings:    {len(rulings)}")
        print(f"flavours:   {len(set(r['flavour'] for r in rulings))}")
        print(f"no mechanism: {sum(1 for r in rulings if not r['mechanism'])}")
        print(f"undeclared: {len(undeclared)}")
        for e in errors:
            print(f"  error: {e}")
        return 0

    if args.check:
        stale = []
        for path, want in ((OUT_MD, md), (OUT_JSON, js)):
            have = path.read_text(encoding="utf-8") if path.exists() else None
            if have != want:
                stale.append(rel(path))
        if stale:
            print("STALE: " + ", ".join(stale))
            print("Run: python scripts/generate_rulings.py")
            return 1
        print(f"[OK] rulings index current ({len(rulings)} ruling(s)).")
        return 0

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    # newline="" forces LF. On Windows the default translates \n to \r\n, the
    # mixed-line-ending hook then rewrites the file back to LF mid-commit, and
    # --check fails against a file it just generated. .gitattributes already
    # mandates LF repo-wide; write it that way in the first place.
    OUT_MD.write_text(md, encoding="utf-8", newline="")
    OUT_JSON.write_text(js, encoding="utf-8", newline="")
    print(f"wrote {rel(OUT_MD)} and {rel(OUT_JSON)} ({len(rulings)} ruling(s), ", end="")
    print(f"{len(undeclared)} undeclared)")
    for e in errors:
        print(f"  error: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
