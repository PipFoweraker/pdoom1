#!/usr/bin/env python3
"""
Verify release-feed download URLs actually resolve.

Anti-rot guard for public/releases/*.json (issue #963 follow-up). The
release-metadata generator has drifted from the real build/upload pipeline
before: PDoom.exe / PDoom.x86_64 / pdoom-*-source.* were hardcoded into
every generated release JSON and were 404s against every real release
since the versioned-zip build pipeline landed, and nothing caught it until
a human noticed. This script closes that gap by actually resolving the
URLs it is asked to check, instead of trusting the generator's output.

Two modes:

  --file PATH   Blocking check. HEADs every URL in a single release JSON's
                "downloads" block. Exits nonzero on any non-200. This is
                meant to run in CI right after a release's assets are
                uploaded, so a future generator/pipeline mismatch fails the
                workflow instead of silently shipping 404s.
                It ALSO cross-checks the "platform_status" block offline: a
                404 sweep can only see URLs that are listed, so an omitted
                platform would be invisible to it. See verify_platform_status.

  --sweep PATH  Report-only sweep (unless --strict). Walks every entry in a
                releases.json index, checks whether a matching GitHub
                Release still exists (via the Releases API, NOT the tag
                page -- a bare git tag with no Release object still 200s
                the tag page, which is exactly how the v0.9.0 feed-rot went
                unnoticed), and checks its download URLs too. Old entries
                that have rotted (e.g. a release that was later deleted)
                are reported but do not fail the run by default -- pass
                --strict to make sweep failures blocking as well.

Usage:
    python scripts/verify_release_urls.py --file public/releases/v0.13.1.json
    python scripts/verify_release_urls.py --sweep public/releases/releases.json
    python scripts/verify_release_urls.py --sweep public/releases/releases.json --strict
    python scripts/verify_release_urls.py --file public/releases/v0.13.1.json --sweep public/releases/releases.json
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

GITHUB_REPO = "PipFoweraker/pdoom1"
USER_AGENT = "pdoom1-release-url-verifier"
TIMEOUT_SECONDS = 15.0


def check_url(url: str) -> Tuple[int, str]:
    """HEAD a URL, following redirects. Returns (status_code, error_str).

    status_code is 0 on a network-level failure (no response at all), in
    which case error_str carries the reason.
    """
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            return resp.status, ""
    except urllib.error.HTTPError as e:
        return e.code, str(e.reason)
    except urllib.error.URLError as e:
        return 0, str(e.reason)


def verify_downloads(downloads: Dict[str, str], label: str) -> List[str]:
    """Check every URL in a `downloads` dict. Prints a line per URL, returns
    a list of human-readable failure descriptions (empty if all resolved)."""
    failures = []
    if not downloads:
        msg = f"{label}: no 'downloads' block found"
        print(f"  [!] {msg}")
        return [msg]

    for platform, url in downloads.items():
        status, err = check_url(url)
        ok = status == 200
        marker = "[OK]" if ok else "[!]"
        detail = str(status) if status else "ERR"
        if err:
            detail = f"{detail} ({err})"
        print(f"  {marker} {label}.{platform:12s} {detail:24s} {url}")
        if not ok:
            failures.append(f"{label}.{platform} -> {detail} :: {url}")
    return failures


def release_exists(version: str) -> bool:
    """True iff a GitHub Release object exists for this tag.

    Deliberately uses the Releases API, not the tag page: a git tag can
    exist with no Release attached (e.g. a deleted/never-published
    release) and https://github.com/{repo}/releases/tag/{tag} still
    returns 200 in that case -- checked against v0.9.0, which is exactly
    the rot this sweep mode exists to catch.
    """
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{version}"
    status, _ = check_url(api_url)
    return status == 200


def verify_platform_status(data: Dict, label: str) -> List[str]:
    """Offline cross-check between `platform_status` and `downloads`.

    The URL checks above can only fail on a URL that IS listed. That is exactly
    how the v0.14.3 macOS 404 could have been shipped quietly under a slightly
    different generator bug: an omitted platform is invisible to a 404 sweep.
    So this asserts the other direction too -- an `available` status must have a
    URL, and a `not_built`/`unknown` status must NOT have one.

    A feed with no `platform_status` block at all is reported (not silently
    passed): it was written by a generator that could not distinguish "not
    built" from "not checked".
    """
    problems: List[str] = []
    status_block = data.get("platform_status")
    if status_block is None:
        print(f"  [!] {label}: no platform_status block (pre-#963-followup generator)")
        return [f"{label}: no platform_status block -- cannot audit omitted platforms"]

    downloads = data.get("downloads", {}) or {}
    for platform, entry in sorted(status_block.items()):
        status = entry.get("status")
        has_url = platform in downloads
        marker = {"available": "[OK]", "not_built": "[--]", "unknown": "[??]"}.get(status, "[!]")
        print(f"  {marker} {label}.{platform:12s} status={status!s:10s} url_listed={has_url}")
        if has_url and status != "available":
            problems.append(
                f"{label}.{platform}: URL advertised while status is {status!r} "
                f"-- a missing asset must never render as a URL"
            )
        if not has_url and status == "available":
            problems.append(f"{label}.{platform}: status 'available' but no download URL listed")
        if status not in ("available", "not_built", "unknown"):
            problems.append(f"{label}.{platform}: unrecognised status {status!r}")
    return problems


def cmd_file(path: Path) -> int:
    """Blocking: verify one release JSON's download URLs."""
    data = json.loads(path.read_text(encoding="utf-8"))
    version = data.get("version", path.stem)
    print(f"[*] Verifying download URLs for {version} ({path})")

    failures = verify_downloads(data.get("downloads", {}), version)
    failures += verify_platform_status(data, version)
    if failures:
        print(f"\n[!] {len(failures)} problem(s) in {path}:")
        for f in failures:
            print(f"  [!] {f}")
        return 1

    print(f"[OK] All download URLs for {version} resolve, and match their platform_status")
    return 0


def cmd_sweep(path: Path, strict: bool) -> int:
    """Report-only (unless --strict): sweep a releases.json index for rot."""
    data = json.loads(path.read_text(encoding="utf-8"))
    releases = data.get("releases", [])
    plural = "y" if len(releases) == 1 else "ies"
    print(f"[*] Sweeping {len(releases)} feed entr{plural} in {path}")

    rotten = []
    for entry in releases:
        version = entry.get("version", "?")
        if not release_exists(version):
            print(f"  [!] {version}: no matching GitHub release (feed rot -- release is gone)")
            rotten.append(version)
            continue
        print(f"  [*] {version}: release exists, checking downloads...")
        if verify_downloads(entry.get("downloads", {}), version):
            rotten.append(version)

    if rotten:
        are = "is" if len(rotten) == 1 else "are"
        print(
            f"\n[!] {len(rotten)} feed entr{'y' if are == 'is' else 'ies'} {are} rotten: "
            f"{', '.join(rotten)}"
        )
        if strict:
            return 1
        print("[*] --strict not set: old-entry rot is report-only, exiting 0")
        return 0

    print("[OK] No rot found in feed index")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify release-feed download URLs actually resolve (issue #963)"
    )
    parser.add_argument(
        "--file", type=Path, help="A single release JSON to verify (blocking on any 404)"
    )
    parser.add_argument(
        "--sweep",
        type=Path,
        help="A releases.json index to sweep for rotted entries (report-only unless --strict)",
    )
    parser.add_argument(
        "--strict", action="store_true", help="Make --sweep rot findings exit nonzero too"
    )
    args = parser.parse_args()

    if not args.file and not args.sweep:
        parser.error("pass --file and/or --sweep")

    exit_code = 0
    if args.file:
        exit_code = max(exit_code, cmd_file(args.file))
    if args.sweep:
        exit_code = max(exit_code, cmd_sweep(args.sweep, args.strict))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
