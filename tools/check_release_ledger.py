#!/usr/bin/env python3
"""Guard: has every version we bumped to actually been tagged and released?

Layer: PROVE -- this gate FAILS the build once armed.

THE DEFECT THIS TOOL WAS WRITTEN TO FIX
---------------------------------------
On 2026-08-24 the repo held ``version.txt = 0.14.3``, a proven build on disk,
a blessed seed and a fresh ladder epoch -- and **no ``v0.14.3`` tag and no
GitHub release**. Nothing anywhere reported that. It was found by a human
reading a gate sheet, not by a gate.

The reason is structural, and it is the whole point of this file. Every
release-adjacent workflow in this repo is triggered by a TAG PUSH or a RELEASE
PUBLISH:

  * ``enhanced-release.yml``          on: push tags v*.*.*
  * ``release-reminder.yml``          on: push tags v*.*.*
  * ``sync-game-version.yml``         on: release published/edited
  * ``release-sync-monitor.yml``      compares the LATEST PUBLISHED release
  * ``live-site-release-freshness.yml`` compares the LATEST PUBLISHED release

Every one of those is DOWNSTREAM of the human act of tagging. So the single
state "the version was bumped and never tagged" is precisely the state in which
the entire apparatus is silent -- **by construction, not by accident**. The
monitors that look like they cover this do not: they compare the live site
against the latest *published* release, so when the latest published release is
itself stale they agree with each other and both go green.

This is the ruled ``manufactured confidence`` shape (Pip, 2026-08-23 16:42):
a value meaning "I could not tell" rendered as a value meaning "fine". Here it
was worse -- nothing even produced a value.

RULING: 2026-08-24 -- every value version.txt has ever held must have a matching git tag, or a declared exemption; a bump with no tag is a defect the machine reports, not a thing a human is expected to remember -- flavour: release-cadence -- mechanism: tools/check_release_ledger.py

WHAT IS *NOT* BROKEN, AND SAYING SO MATTERS
-------------------------------------------
The release pipeline itself is complete and armed. ``enhanced-release.yml`` on a
``v*.*.*`` tag push runs: validate-data -> build-godot (all three platforms via
``tools/build_release.py``, freshness-proven) -> generate-feeds ->
create-release-manifest -> create-github-release (softprops, with assets) ->
verify-release-urls. Nothing in that chain needed fixing.

**The missing act is one ``git push origin <tag>``.** So the remedy is not more
pipeline; it is a trigger that fires UPSTREAM of the tag, which is what this
tool plus ``.github/workflows/release-ledger.yml`` provide.

UNKNOWN IS A FIRST-CLASS RESULT
-------------------------------
Tag presence is derivable offline from git refs. Release presence is NOT -- it
needs the GitHub API. When that is unreachable this tool prints ``UNKNOWN`` for
the release columns and says so in the summary. It never prints "OK" for a
question it could not ask. That is the 2026-08-23 ruling, applied to the tool
built to enforce it, which is exactly where the last one got it wrong.

ATOM STORE, AND WHO RULES IT
----------------------------
This tool generates ``docs/releases/releases.json`` (schema
``pdoom.releases/0.1``). Under the atomise protocol clause 3 (ruled by Pip,
2026-08-24: *"do not build an atom store unless a named party will rule it"*),
the named ruler for this store is **Pip Foweraker**, stated here at build time
as the protocol requires. Intended eventual owner is the Orchestrator role,
which does not exist yet.

USAGE
-----
    python tools/check_release_ledger.py              # report, human readable
    python tools/check_release_ledger.py --write      # regenerate the ledger
    python tools/check_release_ledger.py --check      # CI/pre-commit: fail if
                                                      # stale or undeclared
    python tools/check_release_ledger.py --offline    # skip the GitHub API
    python tools/check_release_ledger.py --self-test  # prove against history

EXIT CODES
----------
    0  every version.txt value has a tag, or a declaration
    1  at least one version is untagged and undeclared, OR the generated
       ledger is stale under --check
    2  could not measure (git history unreachable) -- NOT a pass
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = REPO_ROOT / "version.txt"
LADDER_FILE = REPO_ROOT / "ladder_version.txt"
GAME_CONFIG = "godot/autoload/game_config.gd"

OUT_DIR = REPO_ROOT / "docs" / "releases"
ATOMS_PATH = OUT_DIR / "releases.json"
LEDGER_PATH = OUT_DIR / "RELEASE_LEDGER.md"
DECLARATIONS_PATH = OUT_DIR / "UNTAGGED.md"

SCHEMA = "pdoom.releases/0.1"
RULER = "Pip Foweraker"

SEED_RE = re.compile(r'FEATURED_SEED_OVERRIDE\s*:\s*String\s*=\s*"([^"]*)"')
DECLARATION_RE = re.compile(r"^UNTAGGED:\s*([0-9][^\s-]*)\s*--\s*(.+?)\s*$")

UNKNOWN = "UNKNOWN"


# --------------------------------------------------------------------------
# git plumbing
# --------------------------------------------------------------------------


def git(*args: str, allow_fail: bool = False) -> str | None:
    """Run a git command in the repo root. Returns None on failure."""
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        if allow_fail:
            return None
        return None
    return out.stdout.strip()


def show_at(commit: str, path: str) -> str | None:
    return git("show", f"{commit}:{path}")


def version_bump_commits() -> list[tuple[str, str, str, str]]:
    """Every commit that changed version.txt, oldest first.

    Returns (sha, iso_date, subject, version_value_at_that_commit).
    """
    log = git(
        "log",
        "--reverse",
        "--format=%H%x1f%cI%x1f%s",
        "--",
        "version.txt",
    )
    if log is None:
        return []
    rows: list[tuple[str, str, str, str]] = []
    for line in log.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f")
        if len(parts) != 3:
            continue
        sha, date, subject = parts
        value = show_at(sha, "version.txt")
        if value is None:
            continue
        rows.append((sha, date, subject, value.strip()))
    return rows


def first_bump_per_version(rows: list[tuple[str, str, str, str]]) -> list[dict]:
    """Collapse to the FIRST commit at which version.txt held each value.

    A version that was set, reverted and set again is recorded once, at its
    earliest appearance -- that is the moment the number entered history.
    """
    seen: dict[str, dict] = {}
    for sha, date, subject, value in rows:
        if value in seen:
            continue
        seen[value] = {
            "version": value,
            "bump_commit": sha,
            "bump_commit_short": sha[:8],
            "bump_date": date,
            "bump_subject": subject,
        }
    return list(seen.values())


def ladder_and_seed_at(commit: str) -> tuple[str, str]:
    ladder_raw = show_at(commit, "ladder_version.txt")
    ladder = ("L" + ladder_raw.strip()) if ladder_raw else UNKNOWN
    cfg = show_at(commit, GAME_CONFIG)
    if cfg is None:
        return ladder, UNKNOWN
    match = SEED_RE.search(cfg)
    return ladder, (match.group(1) if match else UNKNOWN)


def known_tags() -> dict[str, str]:
    """Map tag name -> the COMMIT sha it points at.

    ``%(*objectname)`` is the peeled target and is populated only for annotated
    tags; lightweight tags point straight at the commit via ``%(objectname)``.
    Taking the peeled value first handles both without a subprocess per tag.
    Note ``for-each-ref`` does not support ``%x1f``, so the separator is a
    literal that cannot occur in a ref name or a sha.
    """
    raw = git(
        "for-each-ref",
        "--format=%(refname:short)|%(objectname)|%(*objectname)",
        "refs/tags",
    )
    if raw is None:
        return {}
    out: dict[str, str] = {}
    for line in raw.splitlines():
        parts = line.split("|")
        if len(parts) < 2 or not parts[0]:
            continue
        name = parts[0]
        direct = parts[1].strip()
        peeled = parts[2].strip() if len(parts) > 2 else ""
        out[name] = peeled or direct
    return out


def tag_for_version(version: str, tags: dict[str, str]) -> str | None:
    for candidate in (f"v{version}", version):
        if candidate in tags:
            return candidate
    return None


# --------------------------------------------------------------------------
# GitHub side -- may legitimately be UNKNOWN
# --------------------------------------------------------------------------


def gh_releases() -> dict[str, dict] | None:
    """Map tag name -> {name, published_at, assets}. None means UNREACHABLE."""
    if shutil.which("gh") is None:
        return None
    try:
        out = subprocess.run(
            [
                "gh",
                "release",
                "list",
                "--limit",
                "200",
                "--json",
                "tagName,name,publishedAt,isLatest",
            ],
            capture_output=True,
            text=True,
            timeout=90,
            cwd=str(REPO_ROOT),
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError:
        return None
    return {row["tagName"]: row for row in data if row.get("tagName")}


# --------------------------------------------------------------------------
# declarations
# --------------------------------------------------------------------------


def read_declarations() -> dict[str, str]:
    """Parse ``UNTAGGED: <version> -- <reason>`` lines.

    Same shape as the ruling and commitment declaration conventions already
    used in this repo: a declaration is a line anywhere in the file, so the
    surrounding prose can explain itself without a parser caring. (Those two
    markers are deliberately not spelled out here -- writing one in prose makes
    this docstring a malformed declaration to the scanners that read for them,
    which is how this comment earned its rewrite.)
    """
    if not DECLARATIONS_PATH.exists():
        return {}
    out: dict[str, str] = {}
    for line in DECLARATIONS_PATH.read_text(encoding="utf-8").splitlines():
        match = DECLARATION_RE.match(line.strip())
        if match:
            out[match.group(1)] = match.group(2)
    return out


# --------------------------------------------------------------------------
# the ledger
# --------------------------------------------------------------------------


def build_ledger(offline: bool = False) -> dict:
    rows = version_bump_commits()
    if not rows:
        return {"error": "no version.txt history reachable"}

    versions = first_bump_per_version(rows)
    tags = known_tags()
    releases = None if offline else gh_releases()
    declarations = read_declarations()

    atoms = []
    for entry in versions:
        ladder, seed = ladder_and_seed_at(entry["bump_commit"])
        tag = tag_for_version(entry["version"], tags)

        if releases is None:
            release_state = UNKNOWN
            published_at = UNKNOWN
        elif tag and tag in releases:
            release_state = "PUBLISHED"
            published_at = releases[tag].get("publishedAt") or UNKNOWN
        else:
            release_state = "ABSENT"
            published_at = None

        atoms.append(
            {
                "version": entry["version"],
                "bump_commit": entry["bump_commit"],
                "bump_commit_short": entry["bump_commit_short"],
                "bump_date": entry["bump_date"],
                "bump_subject": entry["bump_subject"],
                "ladder_epoch_at_bump": ladder,
                "featured_seed_at_bump": seed,
                "board_key_at_bump": (
                    f"({seed}, {ladder})" if UNKNOWN not in (seed, ladder) else UNKNOWN
                ),
                "tag": tag,
                "tag_state": "TAGGED" if tag else "UNTAGGED",
                "tag_commit": tags.get(tag) if tag else None,
                "tag_matches_bump_or_later": (None if not tag else tags.get(tag) is not None),
                "release_state": release_state,
                "release_published_at": published_at,
                "declared_untagged": declarations.get(entry["version"]),
            }
        )

    atoms.sort(key=lambda a: a["bump_date"])

    return {
        "schema": SCHEMA,
        "ruler": RULER,
        "generated_by": "tools/check_release_ledger.py",
        "github_reachable": releases is not None,
        "atoms": atoms,
    }


def failures(ledger: dict) -> list[str]:
    problems = []
    for atom in ledger.get("atoms", []):
        if atom["tag_state"] == "UNTAGGED" and not atom["declared_untagged"]:
            problems.append(
                f"{atom['version']} bumped {atom['bump_date'][:10]} "
                f"({atom['bump_commit_short']}) has NO TAG and no declaration"
            )
    return problems


def render_markdown(ledger: dict) -> str:
    lines: list[str] = []
    lines.append("# Release ledger -- GENERATED, do not hand-edit")
    lines.append("")
    lines.append(
        "Regenerate with `python tools/check_release_ledger.py --write`. "
        "`--check` blocks stale commits."
    )
    lines.append("")
    lines.append(
        "One row per value `version.txt` has ever held, with the ladder epoch "
        "and featured seed that were live at the moment it was bumped. The "
        "board key is `(seed, ladder)` -- it is keyed on the ladder, not the "
        "binary, so it does NOT move with a patch version."
    )
    lines.append("")
    lines.append(
        "**The seed column is the seed at the BUMP, which is not always the "
        "seed in the CUT.** v0.14.3 is the worked example: `version.txt` went "
        "to 0.14.3 at 07:47 on 2026-08-23 with the seed still reading "
        "`weekly-2026-w34`'s predecessor, and the roll landed at 13:44 the "
        "same day. Read this column as *what was true when the number was "
        "claimed*, and read the build stamp inside the `.pck` for what "
        "actually shipped."
    )
    lines.append("")
    if not ledger.get("github_reachable"):
        lines.append(
            "**Release columns read UNKNOWN: the GitHub API was not reachable "
            "when this was generated.** That is not a pass and not a failure; "
            "it is an unasked question."
        )
        lines.append("")
    lines.append("| Version | Bumped | Ladder | Seed at bump | Tag | GitHub release |")
    lines.append("|---|---|---|---|---|---|")
    for atom in ledger.get("atoms", []):
        tag_cell = atom["tag"] or "**NONE**"
        if atom["declared_untagged"]:
            tag_cell = f"none -- declared: {atom['declared_untagged']}"
        rel = atom["release_state"]
        rel_cell = {
            "PUBLISHED": (
                atom["release_published_at"][:10]
                if atom["release_published_at"] not in (None, UNKNOWN)
                else "published"
            ),
            "ABSENT": "**ABSENT**",
            UNKNOWN: UNKNOWN,
        }.get(rel, rel)
        lines.append(
            f"| {atom['version']} | {atom['bump_date'][:10]} | "
            f"{atom['ladder_epoch_at_bump']} | {atom['featured_seed_at_bump']} | "
            f"{tag_cell} | {rel_cell} |"
        )
    lines.append("")
    problems = failures(ledger)
    if problems:
        lines.append("## Untagged and undeclared")
        lines.append("")
        for problem in problems:
            lines.append(f"- {problem}")
        lines.append("")
        lines.append(
            "To settle one, either push the tag (which arms "
            "`enhanced-release.yml` and publishes the release with assets), "
            "or add an `UNTAGGED: <version> -- <reason>` line to "
            "`docs/releases/UNTAGGED.md`."
        )
        lines.append("")
    # Exactly ONE trailing newline, and this is load-bearing (2026-08-29).
    #
    # The blocks above end with `lines.append("")` for readability, which made
    # this return "...|\n" + "\n" -- a trailing BLANK line. pre-commit's
    # `end-of-file-fixer` then collapses that to a single newline the moment the
    # file is committed, and `--check` compares the committed bytes against
    # freshly generated bytes and reports STALE. So the generator and the hook
    # disagreed about the last byte of the file, and the gate was UNSATISFIABLE
    # through a normal commit: running --write and committing the result could
    # not produce a state --check accepts.
    #
    # That is not a hypothetical. The Release Ledger workflow failed on every
    # run from 2026-08-24 to 2026-08-29 -- eight consecutive, mostly the 04:23
    # cron. It was permanently red for THIS, which is why its red for a real
    # reason on 2026-08-28 (v0.14.4 bumped, tagged, never published) was
    # indistinguishable from the noise and went unread for a day.
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def print_report(ledger: dict) -> None:
    print("[release_ledger] versions derived from version.txt history:")
    for atom in ledger.get("atoms", []):
        tag = atom["tag"] or "-- NO TAG --"
        rel = atom["release_state"]
        print(
            f"  {atom['version']:<10} {atom['bump_date'][:10]}  "
            f"{atom['ladder_epoch_at_bump']:<4} "
            f"{atom['featured_seed_at_bump']:<16} "
            f"{tag:<12} release={rel}"
        )
    if not ledger.get("github_reachable"):
        print(
            "[release_ledger] release state is UNKNOWN -- the GitHub API was "
            "not reachable. This is not a pass."
        )


def self_test() -> int:
    """Prove the classifier against real history.

    Two anchors, chosen because they are the two answers the tool must be able
    to give. A check that cannot return the other answer proves nothing.
    """
    ledger = build_ledger(offline=True)
    if "error" in ledger:
        print("[release_ledger] SELF-TEST: cannot measure -- " + ledger["error"])
        return 2
    by_version = {a["version"]: a for a in ledger["atoms"]}

    problems = []

    # Anchor 1: a version that IS tagged must classify TAGGED.
    if "0.14.2" in by_version:
        if by_version["0.14.2"]["tag_state"] != "TAGGED":
            problems.append("0.14.2 should classify TAGGED and did not")
        if by_version["0.14.2"]["ladder_epoch_at_bump"] != "L5":
            problems.append(
                "0.14.2 ladder should read L5, got "
                + str(by_version["0.14.2"]["ladder_epoch_at_bump"])
            )
    else:
        problems.append("0.14.2 missing from the ledger")

    # Anchor 2: the UNTAGGED answer, proved SYNTHETICALLY and not against live
    # history.
    #
    # This anchor used to name 0.14.3, which was untagged when this tool was
    # written. On 2026-08-24 the tag was pushed and the self-test began FAILING
    # -- which failed step 4 of 7 in release-ledger.yml, so the ledger check
    # after it never ran. THE INSTRUMENT BUILT TO CATCH AN UNTAGGED VERSION WAS
    # DISARMED BY A VERSION BEING TAGGED.
    #
    # The original anchor even printed "replace this with the next untagged
    # version" on failure. That advice was wrong and this comment supersedes it:
    # re-pointing at the next untagged version just re-arms the same trap for
    # whoever tags THAT one. A self-test that depends on live repository state
    # is not a test -- it is a measurement wearing a test's clothes, and it
    # expires the moment the thing it measures changes.
    #
    # So the TAGGED answer is proved against real history (anchor 1, using the
    # oldest tag, which cannot become untagged), and the UNTAGGED answer is
    # proved against a constructed row that no git operation can reach.
    synthetic = {
        "version": "0.0.0-selftest",
        "bump_commit": "0" * 40,
        "bump_commit_short": "0" * 8,
        "bump_date": "2000-01-01T00:00:00+00:00",
        "bump_subject": "synthetic row, never in history",
    }
    fake_tags: dict[str, str] = {}
    if tag_for_version(synthetic["version"], fake_tags) is not None:
        problems.append(
            "a version with no tag in the tag map resolved to a tag -- "
            "the UNTAGGED classification cannot be reached"
        )

    # And prove the same lookup DOES find a tag when one exists, so the check
    # above is discriminating rather than merely always-None.
    if tag_for_version("9.9.9", {"v9.9.9": "deadbeef"}) != "v9.9.9":
        problems.append(
            "a version WITH a tag failed to resolve -- the classifier cannot "
            "return the TAGGED answer, so the UNTAGGED result proves nothing"
        )

    if problems:
        for problem in problems:
            print("[release_ledger] SELF-TEST FAIL: " + problem)
        return 1
    print(
        "[release_ledger] SELF-TEST OK: classifier returns both answers -- "
        "TAGGED proved against real history (0.14.2), UNTAGGED proved against "
        "a synthetic row no git operation can reach."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Release ledger: every version bump, and whether it was tagged."
    )
    parser.add_argument("--write", action="store_true", help="regenerate the generated artefacts")
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the generated artefacts are stale or a version is undeclared-untagged",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="do not call the GitHub API; release columns read UNKNOWN",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="prove the classifier against real history",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    ledger = build_ledger(offline=args.offline)
    if "error" in ledger:
        print("[release_ledger] DID NOT COMPLETE -- " + ledger["error"])
        return 2

    markdown = render_markdown(ledger)
    atoms_json = json.dumps(ledger, indent=2, sort_keys=False) + "\n"

    if args.write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        # newline="\n" is load-bearing, not tidiness. Path.write_text() uses the
        # platform default, so this wrote CRLF on Windows and LF on CI -- and
        # --check compares generated content against the file on disk, so the
        # gate would have reported STALE on Linux for a ledger that was
        # byte-correct. .gitattributes normalises what git STORES; it does not
        # change what this process writes and then reads back.
        ATOMS_PATH.write_text(atoms_json, encoding="utf-8", newline="\n")
        LEDGER_PATH.write_text(markdown, encoding="utf-8", newline="\n")
        print(f"[release_ledger] wrote {ATOMS_PATH.relative_to(REPO_ROOT)}")
        print(f"[release_ledger] wrote {LEDGER_PATH.relative_to(REPO_ROOT)}")

    problems = failures(ledger)

    if args.check:
        stale = False
        # Staleness is only meaningful when the GitHub half was reachable;
        # otherwise a --check run would rewrite PUBLISHED cells to UNKNOWN.
        if ledger["github_reachable"]:
            if not LEDGER_PATH.exists() or LEDGER_PATH.read_text(encoding="utf-8") != markdown:
                print(
                    "[release_ledger] STALE: docs/releases/RELEASE_LEDGER.md "
                    "does not match generated content. Run --write."
                )
                stale = True
        else:
            print(
                "[release_ledger] staleness NOT CHECKED -- GitHub API "
                "unreachable, so the generated content cannot be compared."
            )
        for problem in problems:
            print("[release_ledger] FAIL: " + problem)
        return 1 if (stale or problems) else 0

    print_report(ledger)
    for problem in problems:
        print("[release_ledger] FAIL: " + problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
