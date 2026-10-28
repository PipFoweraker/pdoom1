#!/usr/bin/env python3
"""Guard: a release tag must be cut from its release branch, at the version it names.

Layer: PROVE -- this gate FAILS the release workflow, before any build.

WHY THIS EXISTS (issue #1269)
----------------------------
``RELEASING.md`` said "ship from the release branch, never from churny main"
from 2026-07-25 onwards. Every release after that -- v0.13.x through v0.14.4 --
was tagged from ``main``, no ``release/*`` branch ever existed on origin, and
nothing in CI could tell the difference. A protocol that only prose enforces is
a protocol nobody has to follow. The ruling: adopt the release-branch model for
real, enforced by mechanical guards rather than prose.

The ruling itself is declared once, in docs/rulings/DECISIONS_2026-10-26_return.md
(PR #1350); this file is its mechanism and does not restate it.

WHAT IT CHECKS
--------------
RB001  the tag name is a release version: ``v<major>.<minor>.<patch>`` with an
       optional ``-<prerelease>`` suffix.                          FAIL.
RB002  ``version.txt`` at the commit being released equals the tag minus its
       leading ``v`` (``v0.14.5`` -> ``0.14.5``; ``v0.14.5-rc1`` -> ``0.14.5-rc1``).
                                                                   FAIL.
RB003  the release branch ``release/v<major>.<minor>`` exists on the remote
       (as a remote-tracking ref, default ``refs/remotes/origin/``).  FAIL.
RB004  the commit being released is reachable from that branch.   FAIL.
RB005  if the tag already exists, it points at the commit being released --
       so a manual dispatch cannot build a branch head and label it with an
       existing tag. With ``--require-tag`` the tag MUST exist.  FAIL.

THREE OUTCOMES, NOT TWO
-----------------------
  exit 0  measured pass
  exit 1  measured failure (one or more RB findings)
  exit 2  COULD NOT MEASURE -- not a git repository, the commit cannot be
          resolved, or the clone is shallow. A shallow clone can make an
          ancestor look unreachable, so a "not reachable" verdict from one would
          be a manufactured finding. The release workflow checks out with
          ``fetch-depth: 0`` for exactly this reason.

USAGE
-----
  # what CI runs on a tag push (HEAD is the tagged commit)
  python tools/check_release_branch.py --tag v0.14.5 --require-tag

  # dry-run BEFORE tagging, from a checkout of release/v0.14 (fetch first)
  git fetch origin
  python tools/check_release_branch.py --tag v0.14.5

  # prove the guard can still return every answer (hermetic, no network)
  python tools/check_release_branch.py --self-test
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TAG_RE = re.compile(
    r"^v(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?P<pre>-[0-9A-Za-z.-]+)?$"
)
DEFAULT_REMOTE_PREFIX = "refs/remotes/origin/"

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_UNMEASURED = 2


class Unmeasurable(Exception):
    """The question could not be asked. Never reported as a finding."""


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=False)


def parse_tag(tag: str) -> tuple[str, str] | None:
    """Return (release_branch, expected_version_txt) for a valid tag, else None."""
    m = TAG_RE.match(tag)
    if not m:
        return None
    branch = "release/v{}.{}".format(m.group("major"), m.group("minor"))
    return branch, tag[1:]


def _resolve_commit(repo: Path, rev: str) -> str | None:
    res = _git(repo, "rev-parse", "--verify", "--quiet", rev + "^{commit}")
    return res.stdout.strip() if res.returncode == 0 else None


def check(
    repo: Path,
    tag: str,
    commit: str = "HEAD",
    remote_prefix: str = DEFAULT_REMOTE_PREFIX,
    require_tag: bool = False,
) -> list[str]:
    """Return a list of findings (empty = pass). Raises Unmeasurable."""
    if _git(repo, "rev-parse", "--git-dir").returncode != 0:
        raise Unmeasurable(f"{repo} is not a git repository")
    shallow = _git(repo, "rev-parse", "--is-shallow-repository")
    if shallow.stdout.strip() == "true":
        raise Unmeasurable(
            "shallow clone: reachability cannot be decided (check out with fetch-depth: 0)"
        )
    sha = _resolve_commit(repo, commit)
    if sha is None:
        raise Unmeasurable(f"cannot resolve commit {commit!r}")

    parsed = parse_tag(tag)
    if parsed is None:
        return [
            (
                f"RB001 {tag!r} is not a release tag; expected v<major>.<minor>.<patch>"
                "[-prerelease], e.g. v0.14.5"
            )
        ]
    branch, expected_version = parsed
    findings: list[str] = []

    shown = _git(repo, "show", f"{sha}:version.txt")
    if shown.returncode != 0:
        findings.append(f"RB002 version.txt does not exist at {sha[:12]}")
    else:
        actual = shown.stdout.strip()
        if actual != expected_version:
            findings.append(
                f"RB002 version.txt at {sha[:12]} reads {actual!r}, but the tag {tag} needs {expected_version!r}. "
                f"Bump version.txt (python tools/sync_version.py) on {branch} before tagging."
            )

    branch_ref = remote_prefix + branch
    branch_sha = _resolve_commit(repo, branch_ref)
    if branch_sha is None:
        findings.append(
            f"RB003 {branch} does not exist ({branch_ref} not found). Every release tag must be cut "
            f"from its release branch; push it first: git push origin {branch}"
        )
    else:
        anc = _git(repo, "merge-base", "--is-ancestor", sha, branch_sha)
        if anc.returncode == 1:
            findings.append(
                f"RB004 {sha[:12]} is not reachable from {branch} ({branch_sha[:12]}). Tags come off the release "
                f"branch, never off main: cherry-pick onto {branch} and tag there."
            )
        elif anc.returncode != 0:
            raise Unmeasurable(f"git merge-base failed: {anc.stderr.strip()}")

    tag_sha = _resolve_commit(repo, "refs/tags/" + tag)
    if tag_sha is None:
        if require_tag:
            findings.append(
                f"RB005 tag {tag} does not exist, and this run publishes. Only Pip pushes "
                f"release tags; dispatch a publish with --ref {tag}."
            )
    elif tag_sha != sha:
        findings.append(
            f"RB005 tag {tag} points at {tag_sha[:12]}, but the commit being released is {sha[:12]}. "
            "The build must be the tagged commit."
        )
    return findings


def run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    try:
        findings = check(repo, args.tag, args.commit, args.remote_prefix, args.require_tag)
    except Unmeasurable as exc:
        print(f"[release-branch] COULD NOT MEASURE: {exc} -- no result, not a finding.")
        return EXIT_UNMEASURED
    parsed = parse_tag(args.tag)
    if findings:
        for f in findings:
            print(f"[release-branch] FAIL {f}")
            if args.github:
                print(f"::error title=Release-branch guard::{f}")
        print(f"[release-branch] {len(findings)} finding(s). The release is refused.")
        return EXIT_FAIL
    print(f"[release-branch] OK {args.tag} is on {parsed[0]} and version.txt reads {parsed[1]}.")
    return EXIT_PASS


# --- self-test ---------------------------------------------------------------
# Hermetic: builds a throwaway repo with a fake "origin" remote-tracking layout
# and proves every answer is reachable. Shares no fixture with the unit tests on
# purpose -- this is what CI runs at release time to prove the detector is alive.


def _sh(repo: Path, *args: str) -> str:
    res = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)
    return res.stdout.strip()


def build_fixture(root: Path) -> dict:
    """main: A(0.14.4, tag v0.14.4) -> B(main-only, 0.15.0-dev)
    release/v0.14 (pushed as origin/release/v0.14): A -> C(0.14.5, tag v0.14.5) -> D(0.14.7, untagged)
    Plus tag v0.14.6 on C (wrong version) and v0.15.0 on B (no release/v0.15)."""
    _sh(root, "init", "-q", "-b", "main")
    _sh(root, "config", "user.email", "test@example.invalid")
    _sh(root, "config", "user.name", "test")
    _sh(root, "config", "commit.gpgsign", "false")
    _sh(root, "config", "tag.gpgsign", "false")

    def commit(version: str, msg: str) -> str:
        (root / "version.txt").write_text(version + "\n", encoding="utf-8")
        _sh(root, "add", "version.txt")
        _sh(root, "commit", "-qm", msg)
        return _sh(root, "rev-parse", "HEAD")

    a = commit("0.14.4", "release 0.14.4")
    _sh(root, "tag", "v0.14.4", a)
    b = commit("0.15.0", "main moves on")
    _sh(root, "tag", "v0.15.0", b)
    _sh(root, "checkout", "-q", "-b", "release/v0.14", a)
    c = commit("0.14.5", "release 0.14.5")
    _sh(root, "tag", "v0.14.5", c)
    _sh(root, "tag", "v0.14.6", c)
    d = commit("0.14.7", "bump to 0.14.7, not yet tagged")
    # Simulate what actions/checkout fetch-depth: 0 produces for a pushed branch.
    _sh(root, "update-ref", DEFAULT_REMOTE_PREFIX + "release/v0.14", d)
    _sh(root, "update-ref", DEFAULT_REMOTE_PREFIX + "main", b)
    _sh(root, "checkout", "-q", "main")
    return {"A": a, "B": b, "C": c, "D": d}


# (name, tag, commit-key, require_tag, expected RB codes -- empty means pass)
SELF_TEST_CASES = [
    ("green: v0.14.5 on release/v0.14, version matches", "v0.14.5", "C", True, []),
    (
        "green: epoch baseline v0.14.4 is reachable from the branch it seeded",
        "v0.14.4",
        "A",
        True,
        [],
    ),
    ("green: dry run before the tag exists", "v0.14.7", "D", False, []),
    ("red: tag name is not a release version", "0.14.5", "C", True, ["RB001"]),
    ("red: version.txt disagrees with the tag", "v0.14.6", "C", True, ["RB002"]),
    ("red: release branch does not exist", "v0.15.0", "B", True, ["RB003"]),
    (
        "red: v0.14.5 built from main, not the release branch",
        "v0.14.5",
        "B",
        True,
        ["RB002", "RB004", "RB005"],
    ),
    ("red: publish requested but the tag was never pushed", "v0.14.7", "D", True, ["RB005"]),
]


def codes(findings: list[str]) -> list[str]:
    return sorted(f.split(" ", 1)[0] for f in findings)


def self_test() -> int:
    failed = 0
    green = red = 0
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        shas = build_fixture(root)
        for name, tag, key, require, expected in SELF_TEST_CASES:
            got = codes(check(root, tag, shas[key], require_tag=require))
            ok = got == sorted(expected)
            if not got:
                green += 1
            else:
                red += 1
            print(
                "[self-test] {} {}: expected {} got {}".format(
                    "ok  " if ok else "FAIL", name, sorted(expected) or "pass", got or "pass"
                )
            )
            failed += 0 if ok else 1
        # The third answer: a shallow clone must be COULD NOT MEASURE, never a finding.
        shallow = root / "shallow"
        _sh(root, "clone", "-q", "--depth", "1", "--no-local", "file://" + str(root), str(shallow))
        try:
            check(shallow, "v0.14.5", "HEAD")
            print("[self-test] FAIL shallow clone: expected COULD NOT MEASURE, got a verdict")
            failed += 1
        except Unmeasurable:
            print("[self-test] ok   shallow clone reports COULD NOT MEASURE")
    if green == 0 or red == 0:
        print(f"[self-test] FAIL: both answers were not exercised ({green} green, {red} red).")
        return EXIT_FAIL
    if failed:
        print(f"[self-test] FAIL: {failed} case(s) did not return the expected answer.")
        return EXIT_FAIL
    print(f"[self-test] PASS: {green} green, {red} red, and shallow -> exit 2, all as expected.")
    return EXIT_PASS


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tag", help="the release tag, e.g. v0.14.5")
    ap.add_argument("--commit", default="HEAD", help="commit being released (default HEAD)")
    ap.add_argument("--repo", default=".", help="repository path (default .)")
    ap.add_argument(
        "--remote-prefix",
        default=DEFAULT_REMOTE_PREFIX,
        help="where release branches are looked up (default %(default)s)",
    )
    ap.add_argument(
        "--require-tag", action="store_true", help="the tag must already exist (publishing runs)"
    )
    ap.add_argument("--github", action="store_true", help="also emit ::error:: annotations")
    ap.add_argument("--self-test", action="store_true", help="prove every answer is reachable")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.tag:
        ap.error("--tag is required (or --self-test)")
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
