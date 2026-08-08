#!/usr/bin/env python3
"""Is pdoom1.com advertising the release we actually published?

WHY THIS EXISTS
---------------
`.github/workflows/release-sync-monitor.yml` already compares the latest release
against the website, but it reads
`repos/PipFoweraker/pdoom1-website/contents/data/current-game-version.json`
through the GitHub API -- a file in the website REPO. That is not the same
assertion as "the live site serves it", and pdoom1-website#285 recorded the two
diverging in production on the v0.14.0 cut: the repo held v0.14.0 while
pdoom1.com served v0.13.2, and every check in the estate was green throughout.

This script makes the OTHER assertion: fetch the bytes a visitor's browser
would fetch, through a cache-buster, and compare those to the published
release tag.

TWO DIFFERENT ASSERTIONS, STATED PLAINLY:
  A) the website repo has been updated   -- release-sync-monitor.yml checks this
  B) the live site SERVES the update     -- this script checks this
B can be false while A is true (repo committed, deploy not run, or CDN still
serving the old object). A can be false while B is true only transiently.

EXIT CODES (deliberately mirroring pdoom1-website's board-liveness.yml, which
established this convention in this repo family):
  0  in sync, OR mismatched but still inside the tolerated lag window
  1  MISMATCH beyond tolerance -- a human must act
  2  UNKNOWN -- the site was unreachable or its JSON was unreadable.
     "We cannot tell" is NOT "we are wrong". Callers keep this GREEN.

Read-only. Issues one GET and writes nothing anywhere.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

DEFAULT_URL = "https://pdoom1.com/data/version.json"

# See the workflow comment for the full justification. Summary: the website's
# only automatic path to freshness is a 6-hourly cron
# (pdoom1-website .github/workflows/auto-update-data.yml, `0 */6 * * *`), so any
# lag shorter than that is the system working as designed, not a fault.
DEFAULT_TOLERANCE_MINUTES = 480

EXIT_OK = 0
EXIT_MISMATCH = 1
EXIT_UNKNOWN = 2


def _fetch_live_json(url: str, timeout: int) -> dict:
    """GET the live site's version.json, defeating every cache we can name.

    The cache-buster is not decoration. A plain GET of this URL can be answered
    from a CDN edge object minted before the release existed, which is exactly
    the reading that produced eight hours of confident wrong prose on
    2026-08-07: a single curl taken BEFORE the release was published, then
    treated as evidence about a period after it.
    """
    busted = "{}{}cb={}".format(url, "&" if "?" in url else "?", int(time.time()))
    request = urllib.request.Request(
        busted,
        headers={
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
            "User-Agent": "pdoom1-live-site-freshness-check",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw)


def _parse_iso8601(value: str) -> datetime:
    """Parse a GitHub API timestamp. `Z` is not accepted by fromisoformat < 3.11."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _emit_output(key: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write("{}={}\n".format(key, value))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument(
        "--expected-version",
        required=True,
        help="The release tag that SHOULD be live, e.g. v0.14.1.",
    )
    parser.add_argument(
        "--published-at",
        required=True,
        help="ISO-8601 publish time of that release. Lag is measured from here.",
    )
    parser.add_argument(
        "--tolerance-minutes",
        type=int,
        default=DEFAULT_TOLERANCE_MINUTES,
        help="Lag below this is reported and tolerated, not failed.",
    )
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument(
        "--site-json-file",
        default=None,
        help="Read the site payload from a local file instead of fetching. "
        "For testing the comparison logic offline; never used in CI.",
    )
    args = parser.parse_args(argv)

    # ---- Read the live site. Any failure here is UNKNOWN, never MISMATCH. ----
    try:
        if args.site_json_file:
            with open(args.site_json_file, encoding="utf-8") as handle:
                payload = json.load(handle)
        else:
            payload = _fetch_live_json(args.url, args.timeout)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print("verdict=unknown  reason=unreachable  detail={}".format(exc))
        _emit_output("verdict", "unknown")
        _emit_output("live_version", "")
        return EXIT_UNKNOWN
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print("verdict=unknown  reason=unparseable-json  detail={}".format(exc))
        _emit_output("verdict", "unknown")
        _emit_output("live_version", "")
        return EXIT_UNKNOWN

    live_version = ""
    if isinstance(payload, dict):
        latest = payload.get("latest_release")
        if isinstance(latest, dict):
            live_version = str(latest.get("version") or "")

    if not live_version:
        print("verdict=unknown  reason=no-latest_release.version-field")
        _emit_output("verdict", "unknown")
        _emit_output("live_version", "")
        return EXIT_UNKNOWN

    try:
        published = _parse_iso8601(args.published_at)
    except ValueError as exc:
        print("verdict=unknown  reason=unparseable-published-at  detail={}".format(exc))
        _emit_output("verdict", "unknown")
        _emit_output("live_version", live_version)
        return EXIT_UNKNOWN

    # ---- Compare. Tags are compared verbatim; both sides carry the `v`. ----
    expected = args.expected_version.strip()
    age_minutes = int((datetime.now(timezone.utc) - published).total_seconds() // 60)

    _emit_output("live_version", live_version)
    _emit_output("expected_version", expected)
    _emit_output("age_minutes", str(age_minutes))

    print("live site advertises : {}".format(live_version))
    print("latest release is    : {}".format(expected))
    print("release age          : {} min".format(age_minutes))
    print("tolerance            : {} min".format(args.tolerance_minutes))

    if live_version == expected:
        print("verdict=in-sync")
        _emit_output("verdict", "in-sync")
        return EXIT_OK

    # A release published minutes ago has not propagated yet, and saying so is
    # not a finding. Only a gap the automatic backstop should already have
    # closed is worth anyone's attention.
    if age_minutes <= args.tolerance_minutes:
        print(
            "verdict=lagging  (mismatch, but inside the tolerated window -- "
            "the site's own 6-hourly refresh has not necessarily run yet)"
        )
        _emit_output("verdict", "lagging")
        return EXIT_OK

    print(
        "verdict=stale  pdoom1.com has advertised {} for {} min after {} "
        "was published".format(live_version, age_minutes, expected)
    )
    _emit_output("verdict", "stale")
    return EXIT_MISMATCH


if __name__ == "__main__":
    sys.exit(main())
