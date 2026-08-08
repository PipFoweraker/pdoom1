"""Cross-check CHANGELOG.md claims against real GitHub issue state.

Layer: PROVE (with a GENERATE mode, --refresh, for the cached manifest)

Why this exists
---------------
`sync-game-version.yml` slices a version section out of CHANGELOG.md and
publishes it to pdoom1-website as release notes, so a wrong line in this file
reaches players with no human in between. Issue #1165 recorded the v0.13.2
release body announcing #500 ("Research Quality System") as delivered while
#500 was -- and is -- open, plus six competing `## [Unreleased]` headings that
let any "take the newest section" slicer assemble years of unrelated text.

Two failure classes, two checks:

  STRUCTURE  exactly one `## [Unreleased]` heading and it must be first;
             modern version headings must be `[x.y.z] - YYYY-MM-DD` with
             non-increasing dates.
  CLAIMS     an issue number cited inside a *released* section must not be
             OPEN. A shipped section citing an open issue is a claim that
             something landed when it did not.

Ground truth
------------
GitHub is the authority, but a pre-commit hook cannot depend on the network.
So state is cached in a committed manifest (`scripts/changelog_issue_state.json`)
that is regenerated with `--refresh` and read offline by every other mode.
This is the same anti-rot shape as `scripts/generate_dq_index.py`: a generated
artefact plus a `--check` that blocks stale commits.

Degradation, deliberately NOT silent
------------------------------------
If CHANGELOG.md cites a number the manifest has never seen, the check FAILS
with an instruction to run `--refresh`; it does not shrug and pass. A check
that passes when it could not verify is the exact failure class this file
exists to stop. `--refresh` needs `gh` authenticated; nothing else does.

Usage
-----
    python scripts/check_changelog_claims.py            # verify (offline)
    python scripts/check_changelog_claims.py --refresh  # re-fetch state (needs gh)
    python scripts/check_changelog_claims.py --report   # print the ground-truth table
"""

import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
MANIFEST = Path(__file__).resolve().parent / "changelog_issue_state.json"
REPO = "PipFoweraker/pdoom1"

HEADING = re.compile(r"^## \[([^\]]+)\](.*)$")
ISSUE_REF = re.compile(r"#(\d+)\b(?:\s*\[(open|ref)\])?")
SEMVER_DATE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
DATE_IN_HEADING = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

# Everything at or above this heading is held to the strict structural rules.
# Below it sits the pre-0.9 pygame-era history, which was written before this
# project had a release discipline: duplicate 0.7.4 headings, a `[Previous]`
# label, `[0.1.0] - TBD`, out-of-order dates. Rewriting that archive would
# destroy history to satisfy a linter. The `[Unreleased]` rule still applies
# to the whole file, because that is the collision that actually shipped.
STRICT_FLOOR = "0.9.0"

# A released section MAY cite a still-open number, but only with the inline
# marker `#NNNN [open]`, which the reader sees too:
#
#     - **Pick the music from the pause menu** (#802 [open], #1146)
#
# meaning "this release advanced #802; #802 itself is not finished". The marker
# is checked in BOTH directions -- an `[open]` marker on a number that has since
# closed also fails, so the annotation cannot rot into decoration.
#
# `#NNNN [ref]` is the other escape hatch: the number is cited as provenance for
# an editorial change ("relabelled 2026-08-09 (#1165 [ref])"), not as a claim
# that anything shipped, so its state is irrelevant and is not checked. It has to
# be typed deliberately and it reads as a reference to a human, which is the
# point; `[open]` is the one you want for real work.
OPEN_MARKER = "[open]"


# Keyed by codepoint rather than by literal so this source file is itself pure
# ASCII (issue #744). Issue titles routinely carry smart quotes and en-dashes.
ASCII_FOLD = {
    0x2013: "--",  # en dash
    0x2014: "--",  # em dash
    0x2018: "'",  # left single quote
    0x2019: "'",  # right single quote
    0x201C: '"',  # left double quote
    0x201D: '"',  # right double quote
    0x2026: "...",  # ellipsis
    0x2192: "->",  # rightwards arrow
}


def ascii_fold(text: str) -> str:
    text = text.translate(ASCII_FOLD)
    return text.encode("ascii", "replace").decode("ascii")


class Section:
    def __init__(self, label: str, rest: str, lineno: int):
        self.label = label
        self.rest = rest
        self.lineno = lineno
        self.body: list[str] = []

    @property
    def is_unreleased(self) -> bool:
        return self.label.strip().lower() == "unreleased"

    @property
    def version(self) -> tuple[int, int, int] | None:
        m = SEMVER_DATE.match(self.label.strip())
        return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None

    @property
    def heading_date(self) -> date | None:
        m = DATE_IN_HEADING.search(self.rest)
        if not m:
            return None
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None

    def issue_refs(self) -> list[tuple[int, int, str]]:
        """[(issue_number, line number, marker)] for every citation.

        `marker` is "open", "ref", or "" when the number is cited bare.
        """
        found: list[tuple[int, int, str]] = []
        for offset, line in enumerate(self.body):
            for m in ISSUE_REF.finditer(line):
                found.append((int(m.group(1)), self.lineno + 1 + offset, m.group(2) or ""))
        return found

    def numbers(self) -> set[int]:
        return {n for n, _, _ in self.issue_refs()}


def parse_sections() -> list[Section]:
    sections: list[Section] = []
    for lineno, line in enumerate(CHANGELOG.read_text(encoding="utf-8").splitlines(), 1):
        m = HEADING.match(line)
        if m:
            sections.append(Section(m.group(1), m.group(2), lineno))
        elif line.startswith("## "):
            # A non-bracket H2 (e.g. "## Release Process") ends the current
            # section without starting a new one.
            sections.append(Section("__prose__", "", lineno))
        elif sections:
            sections[-1].body.append(line)
    return [s for s in sections if s.label != "__prose__"]


def load_manifest() -> dict:
    if not MANIFEST.exists():
        return {"generated": None, "issues": {}}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def fetch_state(numbers: list[int]) -> dict:
    """Ask GitHub for the real state of each number. Needs gh, authenticated."""
    issues: dict[str, dict] = {}
    for n in sorted(numbers):
        proc = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{REPO}/issues/{n}",
                "--jq",
                "{state: .state, title: .title, pr: (.pull_request != null)}",
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
        if proc.returncode != 0:
            if "Not Found" in proc.stderr or "404" in proc.stderr:
                issues[str(n)] = {"state": "missing", "title": "", "kind": "none"}
                print(f"  #{n}: DOES NOT EXIST")
                continue
            raise SystemExit(
                f"gh failed for #{n} (exit {proc.returncode}): {proc.stderr.strip()}\n"
                "Refresh needs `gh auth status` to be clean."
            )
        data = json.loads(proc.stdout)
        issues[str(n)] = {
            "state": data["state"],
            "title": ascii_fold(data["title"])[:120],
            "kind": "pr" if data["pr"] else "issue",
        }
        print(f"  #{n}: {issues[str(n)]['kind']} {data['state']}")
    return issues


def refresh() -> int:
    cited = sorted({n for s in parse_sections() for n in s.numbers()})
    print(f"Fetching real state for {len(cited)} numbers cited in CHANGELOG.md ...")
    issues = fetch_state(cited)
    payload = {
        "_comment": (
            "GENERATED by scripts/check_changelog_claims.py --refresh. Cached "
            "GitHub state for every number cited in CHANGELOG.md, so the "
            "pre-commit guard can verify claims without a network call. Do not "
            "hand-edit; re-run the refresh."
        ),
        "repo": REPO,
        "refreshed": date.today().isoformat(),
        "issues": issues,
    }
    MANIFEST.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Wrote {MANIFEST.relative_to(ROOT)} ({len(issues)} numbers)")
    return 0


def report() -> int:
    manifest = load_manifest()["issues"]
    sections = parse_sections()
    print("| number | kind | state | cited in | title |")
    print("|---|---|---|---|---|")
    seen: dict[int, list[str]] = {}
    for s in sections:
        for n in sorted(s.numbers()):
            seen.setdefault(n, []).append(s.label)
    for n in sorted(seen):
        rec = manifest.get(str(n), {"kind": "?", "state": "UNKNOWN", "title": ""})
        where = ", ".join(dict.fromkeys(seen[n]))
        print(f"| #{n} | {rec['kind']} | {rec['state']} | {where} | {rec['title']} |")
    return 0


def check() -> int:
    manifest = load_manifest()
    issues = manifest["issues"]
    sections = parse_sections()
    failures: list[str] = []

    # --- STRUCTURE -------------------------------------------------------
    unreleased = [s for s in sections if s.is_unreleased]
    if len(unreleased) != 1:
        where = ", ".join(f"line {s.lineno}" for s in unreleased)
        failures.append(
            f"CHANGELOG.md has {len(unreleased)} '## [Unreleased]' headings "
            f"({where or 'none'}); exactly one is allowed. Any tool that greps "
            "for the newest section can splice unrelated years together."
        )
    elif sections and sections[0] is not unreleased[0]:
        failures.append(
            f"'## [Unreleased]' is at line {unreleased[0].lineno} but must be "
            f"the first section (currently '[{sections[0].label}]' at line "
            f"{sections[0].lineno})."
        )

    floor = tuple(int(p) for p in STRICT_FLOOR.split("."))
    strict: list[Section] = []
    for s in sections:
        if s.is_unreleased:
            continue
        v = s.version
        if v is None or v < floor:
            continue
        strict.append(s)
    prev_date: date | None = None
    for s in strict:
        d = s.heading_date
        if d is None:
            failures.append(
                f"line {s.lineno}: '[{s.label}]' has no YYYY-MM-DD date in its "
                "heading; released sections must be dated."
            )
            continue
        if prev_date is not None and d > prev_date:
            failures.append(
                f"line {s.lineno}: '[{s.label}]' is dated {d}, later than the "
                f"section above it ({prev_date}). Newest goes on top."
            )
        prev_date = d

    # --- CLAIMS ----------------------------------------------------------
    unknown: list[str] = []
    for s in sections:
        if s.is_unreleased:
            continue  # [Unreleased] does not claim anything shipped
        for n, line, marker in sorted(s.issue_refs(), key=lambda r: (r[1], r[0])):
            if marker == "ref":
                continue  # provenance for an edit, not a claim about shipping
            marked = marker == "open"
            rec = issues.get(str(n))
            if rec is None:
                unknown.append(f"#{n} (line {line}, section '[{s.label}]')")
                continue
            if rec["state"] == "missing":
                failures.append(
                    f"line {line}: section '[{s.label}]' cites #{n}, which does "
                    "not exist in this repo."
                )
            elif rec["state"] == "open" and not marked:
                failures.append(
                    f"line {line}: section '[{s.label}]' is a SHIPPED section "
                    f"but cites #{n}, which is still OPEN "
                    f"({rec['kind']}: {rec['title']}). A released section citing "
                    "an open number announces work that did not land. Either "
                    f"correct the entry, or write `#{n} {OPEN_MARKER}` if the "
                    "release genuinely advanced an issue that is not finished."
                )
            elif rec["state"] == "closed" and marked:
                failures.append(
                    f"line {line}: #{n} carries the `{OPEN_MARKER}` marker but "
                    f"is CLOSED ({rec['kind']}: {rec['title']}). Drop the "
                    "marker -- a stale 'still open' warning is its own false "
                    "claim."
                )

    if unknown:
        shown = "; ".join(unknown[:10])
        if len(unknown) > 10:
            shown += f"; ... and {len(unknown) - 10} more"
        where = (
            f"{MANIFEST.name} does not exist"
            if not MANIFEST.exists()
            else f"absent from {MANIFEST.name}"
        )
        failures.append(
            f"{len(unknown)} citation(s) could NOT be verified ({where}): {shown}. "
            "Run `python scripts/check_changelog_claims.py --refresh` while "
            "online, then commit the manifest. This check refuses to pass on "
            "unverified claims -- passing-when-unsure is the bug it exists to "
            "catch."
        )

    if failures:
        print("CHANGELOG claim check FAILED:\n")
        for f in failures:
            print(f"  [FAIL] {f}\n")
        return 1

    marked = sorted(
        {n for s in sections if not s.is_unreleased for n, _, m in s.issue_refs() if m == "open"}
    )
    print(
        f"CHANGELOG claim check OK -- {len(sections)} sections, "
        f"{len(issues)} numbers verified against {MANIFEST.name} "
        f"(refreshed {manifest.get('refreshed')})."
    )
    if marked:
        print(
            f"  {len(marked)} citation(s) carry the `{OPEN_MARKER}` marker and "
            "were confirmed still open: " + ", ".join(f"#{n}" for n in marked)
        )
    return 0


def main() -> int:
    if "--refresh" in sys.argv:
        return refresh()
    if "--report" in sys.argv:
        return report()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
