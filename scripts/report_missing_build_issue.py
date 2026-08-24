# !/usr/bin/env python3
"""File / update ONE ROLLING tracking issue per platform whose build is missing.

Layer: REPORT

Reads the `build-status.json` written by `scripts/check_platform_builds.py`,
and for each platform whose artefacts are absent:

  * ensures the labels exist (`build-missing`, `platform:<key>`);
  * finds the EXISTING open issue carrying BOTH labels -- one rolling issue per
    platform, never a fresh issue every release;
  * creates it if there is none, otherwise refreshes its managed body block and
    its title so the latest affected version is on the front of it;
  * adds one comment per newly-affected version (deduplicated by an HTML
    marker, so a re-run of the same tag does not re-comment);
  * writes the issue URL back into build-status.json, which is what the website
    reads to render "build coming -- see <issue>" instead of advertising a
    download URL that 404s, or quietly pointing people at an older release.

And when a platform RECOVERS, the open issue is commented and CLOSED, so the
website stops linking a stale "coming soon" the moment the build is back.

Loud but not blocking, and the split matters
--------------------------------------------
A missing best-effort build is NOT an error here: it is data, an annotation, a
labelled issue and a JSON field. What IS an error is this reporter failing --
if the issue cannot be filed the failure becomes invisible, which is exactly
what happened on the v0.14.3 tag when `pre-release-checks.yml` 403'd with
"Resource not accessible by integration" and filed nothing. So a reporting
failure exits non-zero (red job) while a missing platform build does not.
The workflow keeps that red off the publication path with `if: always()` on the
downstream jobs.

No third-party dependencies: urllib only, so the GitHub call surface is one
small injectable class and the unit tests never touch the live API.

Usage:
    python scripts/report_missing_build_issue.py \
        --status build-status.json \
        --repo PipFoweraker/pdoom1 \
        --run-url https://github.com/PipFoweraker/pdoom1/actions/runs/123
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

API_ROOT = "https://api.github.com"

TRACKING_LABEL = "build-missing"
LABEL_COLOR = "b60205"
LABEL_DESCRIPTION = "A platform build artefact was missing from a release"

# The body between these markers is regenerated on every run. Anything a human
# writes OUTSIDE them survives -- a rolling issue accumulates human diagnosis
# (this is the #1071 symlink problem, here is the workaround), and a robot that
# stomps that is a robot people stop reading.
BODY_START = "<!-- BUILD-STATUS-START -- managed by scripts/report_missing_build_issue.py -->"
BODY_END = "<!-- BUILD-STATUS-END -->"


def platform_labels(key: str) -> List[str]:
    """Both labels the rolling issue is found by. Order is stable for tests."""
    return [TRACKING_LABEL, f"platform:{key}"]


class GitHubIssues:
    """The whole GitHub surface this script needs, in one injectable object."""

    def __init__(self, repo: str, token: str, api_root: str = API_ROOT):
        self.repo = repo
        self.token = token
        self.api_root = api_root.rstrip("/")

    def _request(self, method: str, path: str, payload: Optional[Dict] = None):
        url = f"{self.api_root}{path}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("X-GitHub-Api-Version", "2022-11-28")
        request.add_header("Authorization", f"Bearer {self.token}")
        request.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
        return json.loads(body) if body else None

    def ensure_label(self, name: str, color: str, description: str) -> None:
        try:
            self._request(
                "POST",
                f"/repos/{self.repo}/labels",
                {"name": name, "color": color, "description": description},
            )
        except urllib.error.HTTPError as exc:
            # 422 = already exists. Anything else (notably 403 "Resource not
            # accessible by integration") must NOT be swallowed -- a silently
            # unprivileged reporter is the defect this whole file exists to
            # stop repeating.
            if exc.code != 422:
                raise

    def find_open_issue(self, labels: List[str]) -> Optional[Dict]:
        query = urllib.parse.urlencode(
            {"labels": ",".join(labels), "state": "open", "per_page": "100"}
        )
        issues = self._request("GET", f"/repos/{self.repo}/issues?{query}") or []
        # /issues returns pull requests too; a PR carrying the label must never
        # be mistaken for the tracking issue.
        issues = [i for i in issues if "pull_request" not in i]
        if not issues:
            return None
        return sorted(issues, key=lambda i: i["number"])[0]

    def create_issue(self, title: str, body: str, labels: List[str]) -> Dict:
        return self._request(
            "POST",
            f"/repos/{self.repo}/issues",
            {"title": title, "body": body, "labels": labels},
        )

    def update_issue(self, number: int, **fields) -> Dict:
        return self._request("PATCH", f"/repos/{self.repo}/issues/{number}", fields)

    def list_comments(self, number: int) -> List[Dict]:
        return (
            self._request("GET", f"/repos/{self.repo}/issues/{number}/comments?per_page=100") or []
        )

    def create_comment(self, number: int, body: str) -> Dict:
        return self._request("POST", f"/repos/{self.repo}/issues/{number}/comments", {"body": body})


def occurrence_marker(key: str, version: str) -> str:
    """Idempotency token: one comment per (platform, version), not per run."""
    return f"<!-- pdoom-build-missing: {key} {version} -->"


TITLE_PREFIX = "[build-missing]"


def issue_title(label: str, version: str) -> str:
    return f"{TITLE_PREFIX} {label} build unavailable (latest: {version})"


def owns_title(existing_title: str) -> bool:
    """Whether this script wrote the title, and may therefore rewrite it.

    Found by a real example: issue #1309 was filed BY HAND for the v0.14.3
    macOS gap, carrying the right label pair and the title "macOS build is
    missing from v0.14.3 -- broken by an .ico icon Godot cannot decode". That
    title says strictly more than the generated one. Adopting the issue (which
    the label match does correctly) while overwriting that title with
    "[build-missing] macOS build unavailable (latest: v0.14.3)" would be the
    same defect the managed-block markers already guard against in the BODY: a
    robot stomping a human's better text is a robot people stop reading.

    So only a title this script generated gets refreshed. A human title stays,
    and may therefore name an older version than the managed block does -- the
    block, the comments and build-status.json all carry the current version, so
    nothing that a consumer reads goes stale.
    """
    return existing_title.startswith(TITLE_PREFIX)


def managed_block(label: str, key: str, version: str, info: Dict, run_url: str) -> str:
    missing = ", ".join(info.get("missing_assets") or []) or "(none recorded)"
    return "\n".join(
        [
            BODY_START,
            f"- **Platform:** {label} (`{key}`)",
            f"- **Latest affected release:** `{version}`",
            f"- **Workflow run:** {run_url or '(not recorded)'}",
            f"- **Missing assets:** {missing}",
            "",
            "**What a user should expect**",
            "",
            info.get("user_message", ""),
            "",
            "The rest of the release published normally -- the other platforms are "
            "unaffected, and previous releases still carry their own "
            f"{label} download. The website reads `build-status.json` from the "
            "release feed and links THIS issue instead of advertising a download "
            "URL that would 404.",
            "",
            "This issue is ROLLING: it is reused and updated for every affected "
            "release, and is closed automatically when the build comes back.",
            BODY_END,
        ]
    )


def splice_body(existing: str, block: str) -> str:
    """Replace the managed block in an existing body, preserving human text."""
    if BODY_START in existing and BODY_END in existing:
        head = existing.split(BODY_START)[0]
        tail = existing.split(BODY_END, 1)[1]
        return head + block + tail
    return existing.rstrip() + "\n\n" + block + "\n"


def new_body(label: str, key: str, version: str, info: Dict, run_url: str) -> str:
    return (
        f"Automated tracking issue: the **{label}** build artefacts were absent "
        "from a published release.\n\n"
        "Opened by `scripts/report_missing_build_issue.py` from "
        "`.github/workflows/enhanced-release.yml`. Notes added below the managed "
        "block are preserved across updates.\n\n"
        + managed_block(label, key, version, info, run_url)
        + "\n"
    )


def sync_platform(
    client: GitHubIssues,
    key: str,
    info: Dict,
    version: str,
    run_url: str,
) -> Optional[Dict]:
    """Create/update/close the rolling issue for one platform.

    Returns the tracking-issue record to embed in build-status.json, or None
    when the platform is available and nothing is being tracked.
    """
    label = info.get("label", key)
    labels = platform_labels(key)
    existing = client.find_open_issue(labels)

    if info.get("available"):
        if existing is None:
            return None
        client.create_comment(
            existing["number"],
            f"The {label} build is present again as of `{version}`. "
            f"Closing this rolling tracker.\n\nRun: {run_url or '(not recorded)'}",
        )
        client.update_issue(existing["number"], state="closed")
        print(f"[*] {label}: recovered -- closed #{existing['number']}")
        return None

    for name in labels:
        client.ensure_label(name, LABEL_COLOR, LABEL_DESCRIPTION)

    if existing is None:
        issue = client.create_issue(
            issue_title(label, version),
            new_body(label, key, version, info, run_url),
            labels,
        )
        print(f"[*] {label}: opened tracking issue #{issue['number']}")
    else:
        number = existing["number"]
        fields = {
            "body": splice_body(
                existing.get("body") or "",
                managed_block(label, key, version, info, run_url),
            )
        }
        if owns_title(existing.get("title") or ""):
            fields["title"] = issue_title(label, version)
        else:
            print(f"[*] {label}: #{number} has a hand-written title; leaving it alone")
        client.update_issue(number, **fields)
        marker = occurrence_marker(key, version)
        seen = any(marker in (c.get("body") or "") for c in client.list_comments(number))
        if seen:
            print(f"[*] {label}: #{number} already records {version}; no new comment")
        else:
            client.create_comment(
                number,
                f"{marker}\n"
                f"`{version}` also published without a {label} build.\n\n"
                f"- Missing assets: {', '.join(info.get('missing_assets') or []) or '(none recorded)'}\n"
                f"- Run: {run_url or '(not recorded)'}",
            )
            print(f"[*] {label}: commented {version} on #{number}")
        issue = {"number": number, "html_url": existing["html_url"]}

    return {
        "number": issue["number"],
        "url": issue["html_url"],
        "labels": labels,
        "state": "open",
    }


def sync_all(client: GitHubIssues, status: Dict, run_url: str) -> Dict:
    """Walk every platform in the status document; mutate and return it."""
    version = status["version"]
    for key, info in status["platforms"].items():
        info["tracking_issue"] = sync_platform(client, key, info, version, run_url)
    return status


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--status", type=Path, required=True, help="build-status.json")
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--run-url", default="", help="URL of the workflow run.")
    parser.add_argument("--api-root", default=API_ROOT, help="GitHub API root (tests / GHES).")
    args = parser.parse_args(argv)

    status = json.loads(args.status.read_text(encoding="utf-8"))
    run_url = args.run_url or status.get("run_url", "")

    if status.get("all_present"):
        print("[*] Every platform artefact is present.")

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    if not token:
        # Never a silent no-op: a token-less run would look identical to a run
        # where everything was fine.
        print(
            "::error::No GH_TOKEN/GITHUB_TOKEN in the environment -- cannot file "
            "or update the platform build tracking issue.",
            file=sys.stderr,
        )
        return 1

    client = GitHubIssues(args.repo, token, args.api_root)
    try:
        sync_all(client, status, run_url)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        print(
            f"::error::GitHub API {exc.code} while filing the platform build "
            f"tracking issue: {detail}. A missing build that files nothing is "
            "invisible -- fix the workflow's `issues: write` permission.",
            file=sys.stderr,
        )
        return 1

    args.status.write_text(json.dumps(status, indent=2) + "\n", encoding="ascii")
    print(f"[*] Updated {args.status} with tracking issue URLs")
    for key, info in status["platforms"].items():
        issue = info.get("tracking_issue")
        if issue:
            print(f"  {key}: {issue['url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
