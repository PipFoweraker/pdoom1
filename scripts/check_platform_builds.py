# !/usr/bin/env python3
"""Detect, per platform, whether a release's build artefacts actually EXIST.

Layer: VERIFY

Why this exists (v0.14.3, 2026-08-24)
-------------------------------------
v0.14.3 published with no macOS asset. The upload step in
`.github/workflows/enhanced-release.yml` carries `if-no-files-found: warn`,
which is deliberate and correct (issue #1071: the GodotSteam .framework loses
its Versions/Current symlink on a non-mac checkout, so the macOS export can
fail through no fault of the tagged source, and Windows + Linux publishing is
worth more than an all-or-nothing gate). The defect is that the warning warns
INTO THE VOID: the job stays green, nothing is filed, and the release feed
then advertises a macOS URL that 404s. Every release from v0.13.1 to v0.14.2
shipped a mac asset, so v0.14.3 was the first instance.

What this checks is NOT "did the upload step run" -- an `if-no-files-found`
verdict is a property of the step, evaluated once, discarded, and unavailable
to anything downstream. This walks the DOWNLOADED artefact tree and asks of
each expected zip: is the file there, and is it big enough to be a real build?
A zero-byte or truncated zip is a missing build for a player's purposes.

Output is `build-status.json` (schema `pdoom.build_status/1.0`), which is the
machine-readable contract the website consumes to render "build coming" with a
link to the tracking issue, instead of either lying about availability or
pointing people at an old release. `scripts/report_missing_build_issue.py`
fills in the `tracking_issue` field afterwards.

Exit codes
----------
0  every REQUIRED platform (Windows, Linux) is present. Best-effort platforms
   may be missing -- that is reported LOUDLY (GitHub warning annotation, job
   summary, build-status.json, tracking issue) but is deliberately NOT an
   error, because a missing macOS build must not withhold Windows and Linux
   from players.
1  a REQUIRED platform is missing, or the artefacts directory is unusable.

Deliberately does no network I/O and imports nothing outside the stdlib, so
the detection half is unit-testable without touching the GitHub API.

Usage:
    python scripts/check_platform_builds.py \
        --artifacts-dir build-artifacts \
        --version v0.14.3 \
        --run-url https://github.com/owner/repo/actions/runs/123 \
        --output build-status.json
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

SCHEMA = "pdoom.build_status/1.0"

# A real Godot build zip is tens of MB. Anything under this is a truncated or
# placeholder file, which is a missing build as far as a player is concerned --
# the point of this script is to check the FILE, not the step that made it.
MIN_ASSET_BYTES = 1_000_000

# The expected assets per platform. These names are the ones
# scripts/build_all_platforms.py actually writes and enhanced-release.yml
# actually uploads; the unversioned alias is REQUIRED, not a nicety (issue
# #1068: the website's download buttons are fixed strings against
# releases/latest/download/<name>).
#
# `required` mirrors MultiPlatformBuilder.REQUIRED_PLATFORMS: Windows and Linux
# fail the build job; macOS is best-effort (issue #1071).
PLATFORMS = (
    {
        "key": "windows",
        "label": "Windows",
        "artifact": "build-windows",
        "required": True,
        "assets": ("PDoom-Windows-{version}.zip", "PDoom-Windows.zip"),
    },
    {
        "key": "linux",
        "label": "Linux",
        "artifact": "build-linux",
        "required": True,
        "assets": ("PDoom-Linux-{version}.zip", "PDoom-Linux.zip"),
    },
    {
        "key": "macos",
        "label": "macOS",
        "artifact": "build-mac",
        "required": False,
        "assets": ("PDoom-macOS-{version}.zip", "PDoom.app.zip"),
    },
)


def _find_asset(artifacts_dir: Path, name: str) -> Optional[Path]:
    """Locate an asset by exact filename anywhere under artifacts_dir.

    Layout-agnostic on purpose: actions/download-artifact nests each artifact
    in its own directory when downloading by pattern, but merges them when
    `merge-multiple` is set. The asset filenames are unique per platform, so
    searching by name survives either layout -- and survives a future change to
    it, which a hardcoded `build-artifacts/build-mac/<version>/` path would not.
    """
    for path in sorted(artifacts_dir.rglob(name)):
        if path.is_file():
            return path
    return None


def scan_platform(artifacts_dir: Path, version: str, spec: Dict) -> Dict:
    """Check one platform's expected assets on disk.

    A platform counts as available only if EVERY expected asset exists and
    clears MIN_ASSET_BYTES. Half a platform (versioned zip present, alias
    missing) is what caused #1068 and must not read as available.
    """
    assets: List[Dict] = []
    for template in spec["assets"]:
        name = template.format(version=version)
        found = _find_asset(artifacts_dir, name)
        size = found.stat().st_size if found is not None else 0
        assets.append(
            {
                "name": name,
                "present": found is not None and size >= MIN_ASSET_BYTES,
                "bytes": size,
                "path": found.as_posix() if found is not None else None,
            }
        )

    missing = [a["name"] for a in assets if not a["present"]]
    available = not missing
    return {
        "label": spec["label"],
        "artifact": spec["artifact"],
        "required": spec["required"],
        "available": available,
        "status": "available" if available else "unavailable",
        "assets": assets,
        "missing_assets": missing,
        # Filled in by scripts/report_missing_build_issue.py. Present as an
        # explicit null so the website can read the key unconditionally.
        "tracking_issue": None,
        "user_message": _user_message(spec["label"], version, available),
    }


def _user_message(label: str, version: str, available: bool) -> str:
    """The sentence the website may render verbatim next to the platform."""
    if available:
        return f"{label} build for {version} is available."
    return (
        f"The {label} build for {version} did not complete, so there is no "
        f"{label} download for this release. Earlier releases are unaffected. "
        "Follow the tracking issue for progress."
    )


def build_status(
    artifacts_dir: Path,
    version: str,
    run_url: str = "",
    now: Optional[datetime.datetime] = None,
) -> Dict:
    """Assemble the full build-status document."""
    stamp = now or datetime.datetime.now(datetime.timezone.utc)
    platforms = {spec["key"]: scan_platform(artifacts_dir, version, spec) for spec in PLATFORMS}
    missing = sorted(k for k, v in platforms.items() if not v["available"])
    return {
        "schema": SCHEMA,
        "version": version,
        "generated_at": stamp.isoformat(),
        "run_url": run_url,
        "all_present": not missing,
        "missing_platforms": missing,
        "missing_required": sorted(k for k in missing if platforms[k]["required"]),
        "platforms": platforms,
    }


def render_summary(status: Dict) -> str:
    """Markdown for the GitHub job summary -- the human half of 'loud'."""
    lines = [f"## Platform build status -- {status['version']}", ""]
    lines.append("| Platform | Tier | Result | Missing assets |")
    lines.append("| --- | --- | --- | --- |")
    for key, info in status["platforms"].items():
        tier = "required" if info["required"] else "best-effort"
        result = "present" if info["available"] else "**MISSING**"
        missing = ", ".join(info["missing_assets"]) or "-"
        lines.append(f"| {info['label']} ({key}) | {tier} | {result} | {missing} |")
    lines.append("")
    if status["all_present"]:
        lines.append("All platform artefacts present. Nothing filed.")
    else:
        lines.append(
            "A missing platform does NOT block this release: Windows and Linux "
            "publish regardless (issue #1071). It is tracked instead -- see the "
            "rolling tracking issue linked from `build-status.json`."
        )
    return "\n".join(lines) + "\n"


def emit_annotations(status: Dict, stream=sys.stdout) -> None:
    """GitHub Actions annotations: visible on the run page even at exit 0."""
    for key, info in status["platforms"].items():
        if info["available"]:
            continue
        tier = "required" if info["required"] else "best-effort"
        level = "error" if info["required"] else "warning"
        print(
            f"::{level}::{info['label']} build artefacts are MISSING for "
            f"{status['version']} ({tier}): "
            f"{', '.join(info['missing_assets'])}. "
            "The release will publish without this platform; a tracking issue "
            "is filed so the website can say 'build coming' rather than 404.",
            file=stream,
        )


def write_job_summary(text: str) -> None:
    """Append to $GITHUB_STEP_SUMMARY when running under Actions.

    Written from inside Python rather than by piping the script's stdout in
    the workflow. RULING 2026-08-24 (flavour ci-gates) says a command's exit
    status must never be read through a pipe -- the cheapest way to obey that
    is to have no pipe at all, so this script owns its own summary file.
    """
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(text)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        required=True,
        help="Directory the build-* artifacts were downloaded into.",
    )
    parser.add_argument("--version", required=True, help="Release tag, e.g. v0.14.3")
    parser.add_argument("--run-url", default="", help="URL of the workflow run.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build-status.json"),
        help="Where to write the build-status JSON document.",
    )
    args = parser.parse_args(argv)

    if not args.artifacts_dir.exists():
        # Loud and fatal: an absent artefacts directory means the download step
        # broke, which is a DIFFERENT failure from a missing platform build and
        # must not be reported as "every platform is missing".
        print(
            f"::error::Artifacts directory not found: {args.artifacts_dir}. "
            "This is a pipeline defect, not a missing platform build.",
            file=sys.stderr,
        )
        return 1

    status = build_status(args.artifacts_dir, args.version, args.run_url)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(status, indent=2) + "\n", encoding="ascii")
    print(f"[*] Wrote {args.output}")

    for key, info in status["platforms"].items():
        mark = "[OK]" if info["available"] else "[MISSING]"
        tier = "required" if info["required"] else "best-effort"
        print(f"  {mark} {info['label']} ({tier})")
        for asset in info["assets"]:
            state = "present" if asset["present"] else "MISSING"
            print(f"        {asset['name']}: {state} ({asset['bytes']} bytes)")

    emit_annotations(status)
    write_job_summary(render_summary(status))

    if status["missing_required"]:
        print("[ERROR] Required platform(s) missing: " f"{', '.join(status['missing_required'])}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
