"""Mine GitHub timestamps for a release tag into a stage-gate timing table.

Maps naturally-occurring release artifacts (tag push, workflow runs, release
assets, sync-workflow runs, PR merges) onto the G..N release timing model
documented in docs/process/RELEASE_TIMING_MODEL.md. Prints an ASCII timing
table and an append-friendly CSV row for docs/process/release_timings.csv.

Usage:
    python tools/release_timeline.py            # latest release
    python tools/release_timeline.py v0.13.1    # specific tag
    python tools/release_timeline.py v0.13.1 --append   # also append CSV row

Requires: gh CLI authenticated for the repo. Stdlib only otherwise.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_REPO = "PipFoweraker/pdoom1"
SYNC_WORKFLOW = "sync-game-version.yml"
# Assets created more than this long after publish are treated as late
# (i.e. uploaded via the local fallback path, not the CI path).
LATE_ASSET_GRACE = timedelta(minutes=15)
# How long after publish we still attribute manual sync dispatches to this
# release.
SYNC_DISPATCH_WINDOW = timedelta(hours=24)

CSV_COLUMNS = [
    "tag",
    "last_pr_merged_utc",
    "tag_pushed_utc",
    "ci_run_start_utc",
    "ci_run_end_utc",
    "ci_minutes",
    "release_published_utc",
    "initial_asset_count",
    "late_asset_count",
    "last_late_asset_utc",
    "sync_fail_count",
    "sync_green_utc",
    "l_minutes_after_publish",
    "m_utc",
    "n_utc",
]


def gh_api(repo: str, path: str) -> dict | list:
    """Call `gh api` and return parsed JSON. Raises on gh failure."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh api {path} failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def fmt_ts(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%SZ") if value else "n/a"


def fmt_iso(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ") if value else ""


def fmt_dur(start: datetime | None, end: datetime | None) -> str:
    if not start or not end:
        return "n/a"
    seconds = int((end - start).total_seconds())
    sign = "-" if seconds < 0 else ""
    seconds = abs(seconds)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{sign}{hours}h{minutes:02d}m"
    if minutes:
        return f"{sign}{minutes}m{secs:02d}s"
    return f"{sign}{secs}s"


def gather(repo: str, tag: str | None) -> dict:
    """Collect every timestamped artifact for the tag from the GitHub API."""
    if tag:
        release = gh_api(repo, f"releases/tags/{tag}")
    else:
        release = gh_api(repo, "releases/latest")
        tag = release["tag_name"]

    published = parse_ts(release.get("published_at"))

    # Resolve the tag to its commit SHA. Never use target_commitish: it is a
    # branch name whose HEAD keeps moving after the tag (learned on v0.13.1,
    # where it attributed a post-tag PR to the release).
    ref = gh_api(repo, f"git/ref/tags/{tag}")
    obj = ref["object"]
    if obj["type"] == "tag":  # annotated tag: dereference once
        obj = gh_api(repo, f"git/tags/{obj['sha']}")["object"]
    sha = obj["sha"]

    # PRs whose merge produced the tagged commit -- proxy for gate I.
    prs = gh_api(repo, f"commits/{sha}/pulls")
    if not isinstance(prs, list):
        prs = []
    merged_prs = sorted(
        (
            p
            for p in prs
            if p.get("merged_at") and (not published or parse_ts(p["merged_at"]) <= published)
        ),
        key=lambda p: p["merged_at"],
    )
    last_pr = merged_prs[-1] if merged_prs else None

    # Workflow runs triggered by pushing the tag. The release workflow's
    # created_at is the best available proxy for the tag-push instant.
    # Match on workflow path first; a bare name match on "release" grabs the
    # wrong run (Pre-Release Checks) -- also learned on v0.13.1.
    runs = gh_api(repo, f"actions/runs?head_branch={tag}&event=push&per_page=100")
    push_runs = runs.get("workflow_runs", [])
    ci_run = next(
        (r for r in push_runs if r.get("path", "").endswith("enhanced-release.yml")),
        None,
    )
    if ci_run is None:
        ci_run = next(
            (
                r
                for r in push_runs
                if "release" in r["name"].lower() and "pre-release" not in r["name"].lower()
            ),
            None,
        )

    # Sync-workflow runs: release-event runs for this tag, plus manual
    # dispatches shortly after publish (the recovery path).
    sync = gh_api(repo, f"actions/workflows/{SYNC_WORKFLOW}/runs?per_page=100")
    sync_runs = []
    for run in sync.get("workflow_runs", []):
        started = parse_ts(run["run_started_at"])
        if run["head_branch"] == tag:
            sync_runs.append(run)
        elif (
            run["event"] == "workflow_dispatch"
            and published
            and started
            and published <= started <= published + SYNC_DISPATCH_WINDOW
        ):
            sync_runs.append(run)
    sync_runs.sort(key=lambda r: r["run_started_at"])

    assets = sorted(release.get("assets", []), key=lambda a: a["created_at"])
    initial, late = [], []
    for asset in assets:
        created = parse_ts(asset["created_at"])
        if published and created and created > published + LATE_ASSET_GRACE:
            late.append(asset)
        else:
            initial.append(asset)

    return {
        "tag": tag,
        "release": release,
        "published": published,
        "last_pr": last_pr,
        "ci_run": ci_run,
        "sync_runs": sync_runs,
        "initial_assets": initial,
        "late_assets": late,
    }


def build_rows(data: dict) -> list[tuple[str, str, str, str, str]]:
    """Stage rows: (stage, start, end, duration, notes)."""
    rows: list[tuple[str, str, str, str, str]] = []
    published = data["published"]

    rows.append(("G last B-quality submission", "n/a", "n/a", "n/a", "unmeasured"))
    rows.append(("H last A-quality submission", "n/a", "n/a", "n/a", "unmeasured"))

    last_pr = data["last_pr"]
    ci_run = data["ci_run"]
    tag_pushed = parse_ts(ci_run["created_at"]) if ci_run else None
    if last_pr:
        merged = parse_ts(last_pr["merged_at"])
        rows.append(
            (
                "I gate (proxy: last PR merge)",
                fmt_ts(merged),
                fmt_ts(tag_pushed),
                fmt_dur(merged, tag_pushed),
                f"PR #{last_pr['number']} -> tag push",
            )
        )
    else:
        rows.append(("I gate (proxy: last PR merge)", "n/a", "n/a", "n/a", "no PR found"))

    if ci_run:
        start = parse_ts(ci_run["run_started_at"])
        end = parse_ts(ci_run["updated_at"])
        rows.append(
            (
                "J+K CI build+upload",
                fmt_ts(start),
                fmt_ts(end),
                fmt_dur(start, end),
                f"{ci_run['name']}: {ci_run['conclusion']}",
            )
        )
    else:
        rows.append(("J+K CI build+upload", "n/a", "n/a", "n/a", "no release run found"))

    initial = data["initial_assets"]
    if initial:
        first = parse_ts(initial[0]["created_at"])
        last = parse_ts(initial[-1]["created_at"])
        rows.append(
            (
                "K assets (CI batch)",
                fmt_ts(first),
                fmt_ts(last),
                fmt_dur(published, last),
                f"{len(initial)} assets within grace of publish",
            )
        )
    for asset in data["late_assets"]:
        created = parse_ts(asset["created_at"])
        size_mb = asset["size"] / (1024 * 1024)
        rows.append(
            (
                "K late asset (local fallback)",
                fmt_ts(published),
                fmt_ts(created),
                fmt_dur(published, created),
                f"{asset['name']} ({size_mb:.1f} MB) after publish",
            )
        )

    sync_runs = data["sync_runs"]
    fails = [r for r in sync_runs if r["conclusion"] != "success"]
    green = next((r for r in sync_runs if r["conclusion"] == "success"), None)
    if sync_runs:
        first = parse_ts(sync_runs[0]["run_started_at"])
        green_ts = parse_ts(green["run_started_at"]) if green else None
        note = f"{len(fails)} failed run(s) before green"
        if green and green["event"] == "workflow_dispatch":
            note += "; green was a MANUAL dispatch"
        rows.append(
            (
                "L cross-repo sync",
                fmt_ts(first),
                fmt_ts(green_ts),
                fmt_dur(published, green_ts),
                note,
            )
        )
    else:
        rows.append(("L cross-repo sync", "n/a", "n/a", "n/a", "no sync runs found"))

    rows.append(("M deploy + social process", "n/a", "n/a", "n/a", "unmeasured"))
    rows.append(("N league observed working", "n/a", "n/a", "n/a", "unmeasured"))
    return rows


def print_table(tag: str, published: datetime | None, rows: list) -> None:
    headers = ("Stage", "Start (UTC)", "End (UTC)", "Duration", "Notes")
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def line(cells: tuple) -> str:
        return "| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths)) + " |"

    sep = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    print(f"Release timeline for {tag} (published {fmt_ts(published)})")
    print(line(headers))
    print(sep)
    for row in rows:
        print(line(row))


def csv_row(data: dict) -> dict[str, str]:
    published = data["published"]
    ci_run = data["ci_run"]
    ci_start = parse_ts(ci_run["run_started_at"]) if ci_run else None
    ci_end = parse_ts(ci_run["updated_at"]) if ci_run else None
    last_pr = data["last_pr"]
    late = data["late_assets"]
    sync_runs = data["sync_runs"]
    fails = [r for r in sync_runs if r["conclusion"] != "success"]
    green = next((r for r in sync_runs if r["conclusion"] == "success"), None)
    green_ts = parse_ts(green["run_started_at"]) if green else None
    ci_minutes = f"{(ci_end - ci_start).total_seconds() / 60:.1f}" if ci_start and ci_end else ""
    l_minutes = (
        f"{(green_ts - published).total_seconds() / 60:.1f}" if green_ts and published else ""
    )
    return {
        "tag": data["tag"],
        "last_pr_merged_utc": fmt_iso(parse_ts(last_pr["merged_at"]) if last_pr else None),
        "tag_pushed_utc": fmt_iso(parse_ts(ci_run["created_at"]) if ci_run else None),
        "ci_run_start_utc": fmt_iso(ci_start),
        "ci_run_end_utc": fmt_iso(ci_end),
        "ci_minutes": ci_minutes,
        "release_published_utc": fmt_iso(published),
        "initial_asset_count": str(len(data["initial_assets"])),
        "late_asset_count": str(len(late)),
        "last_late_asset_utc": fmt_iso(parse_ts(late[-1]["created_at"]) if late else None),
        "sync_fail_count": str(len(fails)),
        "sync_green_utc": fmt_iso(green_ts),
        "l_minutes_after_publish": l_minutes,
        "m_utc": "",
        "n_utc": "",
    }


def append_csv(path: Path, row: dict[str, str]) -> str:
    """Append the row unless the tag is already recorded. Returns a status."""
    exists = path.exists()
    if exists:
        with path.open(newline="", encoding="ascii") as handle:
            if any(r.get("tag") == row["tag"] for r in csv.DictReader(handle)):
                return f"skip: {row['tag']} already in {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="ascii") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, lineterminator="\n")
        if not exists:
            writer.writeheader()
        writer.writerow(row)
    return f"appended {row['tag']} to {path}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tag", nargs="?", help="release tag (default: latest release)")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="owner/name")
    parser.add_argument(
        "--append",
        action="store_true",
        help="append the CSV row to docs/process/release_timings.csv",
    )
    parser.add_argument(
        "--csv-path",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "docs" / "process" / "release_timings.csv",
        help="CSV file to append to (with --append)",
    )
    args = parser.parse_args()

    try:
        data = gather(args.repo, args.tag)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    rows = build_rows(data)
    print_table(data["tag"], data["published"], rows)

    row = csv_row(data)
    print()
    print("CSV row (" + ",".join(CSV_COLUMNS) + "):")
    print(",".join(row[c] for c in CSV_COLUMNS))
    if args.append:
        print(append_csv(args.csv_path, row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
