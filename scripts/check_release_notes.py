#!/usr/bin/env python3
"""Guard against a release note that announces something we did not ship.

Issue #1165. This already reached players: v0.13.2's published release body
announced the Research Quality System as delivered while `#500` was -- and at
the time of writing still is -- OPEN. pdoom1.com's /game-changelog/ renders
release bodies live from the GitHub releases API, so there is no human between
a wrong sentence and a reader.

WHAT THIS CHECKS (mechanical, no judgement involved)
----------------------------------------------------
RN001  more than one `## [Unreleased]` heading in CHANGELOG.md.  FATAL.
       Unambiguous corruption: at least five past releases failed to clear the
       accumulator and nobody noticed, because the failure is silent and the
       output stays plausible.
RN002  the same version heading appearing twice in CHANGELOG.md.  WARN.
       Warn, not fatal, because the file carries genuine historical duplicates
       (`[0.7.4]` twice, 2025-09-16) that predate this guard.
RN003  an issue or PR number cited in a release body whose issue is still
       OPEN.  FATAL.  This is the one that actually bit.
RN004  an issue or PR number cited in a version's release body that cannot be
       tied to any commit message between that version's tag and the previous
       one.  FATAL when a tag range is supplied.
RN005  a bullet that says `#N is still OPEN` about an issue that has since
       CLOSED.  FATAL.  The disclosure escape is only worth having if it is
       checked in both directions: a stale "still open" tells a player that
       finished work is unfinished, which is the same defect as RN003 pointing
       the other way. Taken from #1187, whose author identified this; the
       `[0.14.0]` correction added fourteen of these markers at once, so the
       rot has somewhere to happen now.

WHAT THIS DOES NOT CHECK (still a human's job -- see docs/RELEASE_NOTES_GUARD.md)
--------------------------------------------------------------------------------
- whether a bullet's PROSE is true. `#1173` being closed and in-range says the
  work happened; it says nothing about whether "it opens on global now" is
  accurate. Only playing the build settles that.
- a bullet that cites no issue number at all. RN003/RN004 have nothing to bind
  to, so an uncited claim passes silently. Cite your issues.
- whether a bullet is filed under the RIGHT version. RN004 is a lower bound,
  not a proof: it was run against v0.13.2 and did NOT catch the misfiled
  `#483`, because an unrelated commit in that range happened to mention `#483`
  in its body. A coincidental mention satisfies the tie.

DISCLOSURE ESCAPE
-----------------
A citation of an OPEN issue is permitted if the same bullet says so in exactly
these words: `#<N> is still OPEN`. That phrasing already exists in the
`[0.12.0]` section, written by hand on 2026-08-08. It is deliberately narrow
and greppable: describing shipped code that belongs to an unfinished feature is
legitimate; announcing that feature as delivered is not.

USAGE
-----
  # offline structural check (pre-commit)
  python scripts/check_release_notes.py --changelog-structure

  # the release gate: check the exact bytes about to become the release body
  python scripts/check_release_notes.py --body release_notes.txt --tag v0.14.1

  # audit an already-published release (read-only; never edits it)
  python scripts/check_release_notes.py --release v0.13.2

  # check what CHANGELOG.md would produce for a version
  python scripts/check_release_notes.py --version 0.14.1
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

# A citation is `#` immediately followed by digits, not preceded by a word
# character or another `#`. The negative lookbehind is what keeps `#### Added`
# out (no digit follows anyway) and, more importantly, what keeps the guard off
# `~500 art files` and `$500k` -- neither carries a `#`, and both sit in the
# v0.13.2 body next to the real `#500` defect.
CITATION_RE = re.compile(r"(?<![\w#])#(\d+)\b")

# Issue numbers below this are pre-history and not reliably resolvable; the
# repo's real numbering starts well above it. Nothing in a modern release body
# should cite one.
MIN_PLAUSIBLE_ISSUE = 1

UNRELEASED_HEADING_RE = re.compile(r"^##\s+\[Unreleased\]", re.MULTILINE)
VERSION_HEADING_RE = re.compile(r"^##\s+\[([^\]]+)\]", re.MULTILINE)
FENCE_RE = re.compile(r"^\s*```")

# Everything the release workflow appends AFTER the changelog excerpt. Those
# sections are machine-generated boilerplate (SmartScreen notice, build hashes)
# and make no delivery claims, so they are excluded from citation checks.
APPENDED_SECTION_RE = re.compile(r"^##\s+Build Information\s*$", re.MULTILINE)


class Finding:
    def __init__(self, code: str, fatal: bool, message: str, detail: str = ""):
        self.code = code
        self.fatal = fatal
        self.message = message
        self.detail = detail

    def render(self) -> str:
        tag = "FAIL" if self.fatal else "WARN"
        out = "[{}] {}: {}".format(tag, self.code, self.message)
        if self.detail:
            out += "\n" + "\n".join("         " + line for line in self.detail.splitlines())
        return out


# --------------------------------------------------------------------------
# text handling
# --------------------------------------------------------------------------


def strip_code_fences(text: str) -> str:
    """Blank out fenced code blocks so a `#123` in a sample never trips RN003."""
    out = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def strip_appended_boilerplate(text: str) -> str:
    match = APPENDED_SECTION_RE.search(text)
    return text[: match.start()] if match else text


def split_bullets(text: str) -> List[Tuple[int, str]]:
    """Group a release body into (line_number, text) claim units.

    A "claim unit" is a top-level `- ` bullet plus its continuation lines, or a
    standalone paragraph. Grouping matters because the disclosure escape
    (`#N is still OPEN`) is scoped to the bullet making the claim, not the whole
    document -- one disclosed bullet must not launder every other citation.
    """
    units: List[Tuple[int, List[str]]] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        starts_unit = stripped.startswith(("- ", "* ", "#")) or (
            stripped and not line.startswith((" ", "\t")) and not units
        )
        if starts_unit or not units:
            units.append((idx, [line]))
        elif not stripped:
            units.append((idx + 1, []))
        else:
            units[-1][1].append(line)
    return [(ln, "\n".join(body)) for ln, body in units if body]


def citations_in(text: str) -> List[Tuple[int, int, str]]:
    """Return (issue_number, line_number, bullet_text) for every citation.

    Deduplicated per (number, bullet): a bullet that cites `#500` and then says
    `#500 is still OPEN` is one claim, not two, and reporting it twice made the
    first draft of this guard emit duplicate findings.
    """
    found = []
    seen = set()
    for line_no, unit in split_bullets(text):
        for match in CITATION_RE.finditer(unit):
            number = int(match.group(1))
            key = (number, line_no)
            if number >= MIN_PLAUSIBLE_ISSUE and key not in seen:
                seen.add(key)
                found.append((number, line_no, unit))
    return found


def is_disclosed(number: int, unit: str) -> bool:
    """Does this bullet declare the issue open, in the agreed words?

    Normalised before matching, because the disclosure that already exists in
    the `[0.12.0]` section is written `**#500 is still\\nOPEN**` -- bold, and
    wrapped across a line by the 80-column house style. A literal substring
    match missed it, which would have failed the one section a human had
    already got right. Markdown emphasis is stripped and whitespace collapsed;
    the wording itself still has to be exact.
    """
    flat = re.sub(r"[*_`]", "", unit)
    flat = re.sub(r"\s+", " ", flat)
    return "#{} is still OPEN".format(number) in flat


# --------------------------------------------------------------------------
# sources of release-body text
# --------------------------------------------------------------------------


def extract_changelog_section(version: str, changelog_text: str) -> str:
    """Mirror the release workflow's extraction, on the tight `## [` anchor.

    Two extractors exist in this repo and they are NOT the same:
      * `generate_release_metadata.extract_changelog_for_version()` anchors on
        `## [<version>]` and breaks at the next `## `.
      * `.github/workflows/enhanced-release.yml` -- the one that actually builds
        the published body -- runs
        `sed -n "/\\[$VERSION_NUM\\]/,/^## /p" | head -n -1`, whose start
        pattern is NOT anchored to a heading, so a mere in-prose mention of
        `[0.13.2]` earlier in the file would start the range in the wrong place.
    This function uses the tight anchor. The workflow gate does not rely on it:
    it checks `release_notes.txt` itself, which is the sed output, so the loose
    pattern is covered by checking the bytes rather than by re-deriving them.
    """
    version_num = version.lstrip("v")
    lines = changelog_text.split("\n")
    inside = False
    collected: List[str] = []
    for line in lines:
        if line.startswith("## [{}]".format(version_num)) or line.startswith(
            "## {}".format(version_num)
        ):
            inside = True
            continue
        if inside and line.startswith("## "):
            break
        if inside:
            collected.append(line)
    return "\n".join(collected).strip()


def fetch_published_body(tag: str) -> str:
    result = subprocess.run(
        ["gh", "release", "view", tag, "--json", "body", "-q", ".body"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(
            "could not read published release {}: {}".format(tag, result.stderr.strip())
        )
    return result.stdout


# --------------------------------------------------------------------------
# github state resolution
# --------------------------------------------------------------------------


def resolve_states(numbers: Sequence[int]) -> Dict[int, str]:
    """Batch-resolve issue/PR states via one GraphQL call per 50 numbers.

    `issueOrPullRequest` is used rather than `gh issue view` because the
    CHANGELOG mixes issue and PR references freely and `gh issue view` on a PR
    number is a silent coincidence, not a lookup. States returned: OPEN,
    CLOSED, MERGED. Anything unresolvable comes back as UNKNOWN and is reported
    as a warning, never as a pass.
    """
    states: Dict[int, str] = {}
    unique = sorted(set(numbers))
    for start in range(0, len(unique), 50):
        chunk = unique[start : start + 50]
        fields = "\n".join(
            "n{n}: issueOrPullRequest(number: {n}) {{ "
            "... on Issue {{ state }} ... on PullRequest {{ state }} }}".format(n=n)
            for n in chunk
        )
        query = 'query {{ repository(owner: "PipFoweraker", name: "pdoom1") {{ {} }} }}'.format(
            fields
        )
        result = subprocess.run(
            ["gh", "api", "graphql", "-f", "query=" + query],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            # A partial GraphQL response still carries data alongside errors.
            try:
                payload = json.loads(result.stdout)
            except (ValueError, TypeError):
                for n in chunk:
                    states[n] = "UNKNOWN"
                continue
        else:
            payload = json.loads(result.stdout)
        repo = (payload.get("data") or {}).get("repository") or {}
        for n in chunk:
            node = repo.get("n{}".format(n))
            states[n] = (node or {}).get("state", "UNKNOWN") if node else "UNKNOWN"
    return states


def commit_referenced_numbers(tag: str, prev_tag: str) -> set:
    """Numbers mentioned anywhere in commit messages in `prev_tag..tag`.

    Full message bodies (`%B`), not subjects: squash-merge subjects carry the PR
    number while the issue number lives in the body's `Closes #N`. Measured on
    v0.13.1..v0.13.2 -- subjects alone tie 20 of the section's 22 citations,
    full bodies tie 21, and the one that stays untied is `#500`, the real
    defect.
    """
    result = subprocess.run(
        ["git", "log", "--format=%B", "{}..{}".format(prev_tag, tag)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(
            "could not read commits {}..{}: {}".format(prev_tag, tag, result.stderr.strip())
        )
    return {int(m.group(1)) for m in CITATION_RE.finditer(result.stdout)}


def previous_tag(tag: str) -> Optional[str]:
    result = subprocess.run(
        ["git", "tag", "--sort=v:refname"], cwd=REPO_ROOT, capture_output=True, text=True
    )
    tags = [t for t in result.stdout.split() if t]
    if tag not in tags:
        return None
    index = tags.index(tag)
    return tags[index - 1] if index > 0 else None


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------


def check_changelog_structure(changelog_text: str) -> List[Finding]:
    findings: List[Finding] = []
    lines = changelog_text.split("\n")

    unreleased_lines = [
        i for i, line in enumerate(lines, start=1) if line.startswith("## [Unreleased]")
    ]
    if len(unreleased_lines) > 1:
        findings.append(
            Finding(
                "RN001",
                True,
                "CHANGELOG.md has {} [Unreleased] headings; exactly one is allowed".format(
                    len(unreleased_lines)
                ),
                "lines: {}\n".format(", ".join(str(n) for n in unreleased_lines))
                + "Each extra heading is a past release that failed to clear the\n"
                + "accumulator. Retitle each historical one to the version that\n"
                + "actually shipped it, or fold it into that version's section.",
            )
        )

    seen: Dict[str, List[int]] = {}
    for i, line in enumerate(lines, start=1):
        match = re.match(r"^##\s+\[([^\]]+)\]", line)
        if match:
            key = match.group(1).lstrip("v")
            if key.lower() in ("unreleased", "previous"):
                continue
            seen.setdefault(key, []).append(i)
    for version, at_lines in sorted(seen.items()):
        if len(at_lines) > 1:
            findings.append(
                Finding(
                    "RN002",
                    False,
                    "version [{}] has {} headings".format(version, len(at_lines)),
                    "lines: {}".format(", ".join(str(n) for n in at_lines)),
                )
            )
    return findings


def check_body_citations(
    body: str, label: str, offline: bool = False
) -> Tuple[List[Finding], List[int]]:
    body = strip_appended_boilerplate(strip_code_fences(body))
    cites = citations_in(body)
    numbers = [n for n, _, _ in cites]
    if offline or not numbers:
        return [], numbers

    states = resolve_states(numbers)
    findings: List[Finding] = []
    for number, line_no, unit in cites:
        state = states.get(number, "UNKNOWN")
        if state == "OPEN":
            if is_disclosed(number, unit):
                continue
            findings.append(
                Finding(
                    "RN003",
                    True,
                    "{}: cites #{} but that issue is OPEN".format(label, number),
                    "line {}: {}\n".format(line_no, unit.strip().splitlines()[0][:100])
                    + "A release body reaches pdoom1.com /game-changelog/ with no\n"
                    + "human in between. Either the work shipped and the issue should\n"
                    + "be closed, or the bullet is wrong. If the bullet describes\n"
                    + "shipped code belonging to an unfinished feature, say so with\n"
                    + 'the exact words "#{} is still OPEN".'.format(number),
                )
            )
        elif state == "UNKNOWN":
            findings.append(
                Finding(
                    "RN003",
                    False,
                    "{}: could not resolve #{} (line {})".format(label, number, line_no),
                    "Treated as unresolved, not as a pass.",
                )
            )
        elif is_disclosed(number, unit):
            findings.append(
                Finding(
                    "RN005",
                    True,
                    "{}: says #{} is still OPEN, but it is {}".format(label, number, state),
                    "line {}: {}\n".format(line_no, unit.strip().splitlines()[0][:100])
                    + 'Drop the "#{} is still OPEN" clause. '.format(number)
                    + "A disclosure that has gone stale is its own false claim,\n"
                    + "in the same file and to the same reader -- it now tells a\n"
                    + "player that finished work is unfinished. RN003 is the only\n"
                    + "reason the disclosure wording exists, so the wording has to\n"
                    + "be checked in BOTH directions or the escape rots into\n"
                    + "decoration. Taken from the non-overlapping half of #1187.",
                )
            )
    return findings, numbers


def check_commit_ties(numbers: Iterable[int], tag: str, prev_tag: str, label: str) -> List[Finding]:
    in_range = commit_referenced_numbers(tag, prev_tag)
    findings = []
    for number in sorted(set(numbers)):
        if number not in in_range:
            findings.append(
                Finding(
                    "RN004",
                    True,
                    "{}: cites #{}, which no commit in {}..{} mentions".format(
                        label, number, prev_tag, tag
                    ),
                    "Either the claim belongs to a different release section, or\n"
                    "the work is not in this build. This is a LOWER BOUND: a\n"
                    "coincidental mention in an unrelated commit body satisfies\n"
                    "the tie, so a clean RN004 is not proof of correct filing.",
                )
            )
    return findings


# --------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--changelog-structure", action="store_true", help="RN001/RN002 only")
    parser.add_argument("--body", help="path to the assembled release body to check")
    parser.add_argument("--release", help="check an already-published release by tag (read-only)")
    parser.add_argument("--version", help="check what CHANGELOG.md yields for this version")
    parser.add_argument("--tag", help="tag this body belongs to, enables RN004")
    parser.add_argument("--prev-tag", help="override the auto-detected previous tag")
    parser.add_argument(
        "--offline", action="store_true", help="skip RN003/RN004 (no gh, no network)"
    )
    parser.add_argument("filenames", nargs="*", help="ignored (pre-commit passes filenames)")
    args = parser.parse_args(argv)

    findings: List[Finding] = []
    checked_something = False

    if args.changelog_structure or not (args.body or args.release or args.version):
        findings.extend(check_changelog_structure(CHANGELOG.read_text(encoding="utf-8")))
        checked_something = True

    body = None
    label = ""
    if args.body:
        body = Path(args.body).read_text(encoding="utf-8")
        label = args.body
    elif args.release:
        body = fetch_published_body(args.release)
        label = "published release {}".format(args.release)
    elif args.version:
        body = extract_changelog_section(args.version, CHANGELOG.read_text(encoding="utf-8"))
        label = "CHANGELOG section [{}]".format(args.version.lstrip("v"))
        if not body:
            findings.append(
                Finding("RN000", True, "no CHANGELOG section found for {}".format(args.version))
            )

    if body:
        checked_something = True
        cite_findings, numbers = check_body_citations(body, label, offline=args.offline)
        findings.extend(cite_findings)

        tag = (
            args.tag or args.release or (("v" + args.version.lstrip("v")) if args.version else None)
        )
        if tag and not args.offline:
            prev = args.prev_tag or previous_tag(tag)
            if prev:
                findings.extend(check_commit_ties(numbers, tag, prev, label))
            else:
                findings.append(
                    Finding(
                        "RN004",
                        False,
                        "no previous tag for {}; commit-tie check skipped".format(tag),
                    )
                )

    fatal = [f for f in findings if f.fatal]
    for finding in findings:
        print(finding.render())

    if not checked_something:
        print("[FAIL] nothing was checked -- refusing to report a pass")
        return 2

    if fatal:
        print("")
        print(
            "RELEASE NOTES CHECK FAILED: {} fatal, {} warning".format(
                len(fatal), len(findings) - len(fatal)
            )
        )
        return 1

    print("[OK] release notes check passed ({} warning(s))".format(len(findings)))
    print("     Mechanical only. Prose accuracy and uncited claims remain manual --")
    print("     see docs/RELEASE_NOTES_GUARD.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
