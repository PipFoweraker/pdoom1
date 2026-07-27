#!/usr/bin/env python3
"""
UI evolution capture collector for P(Doom).

Sweeps the in-game UI evolution capture rail's output -- the F7 hotkey wired in
godot/scripts/debug/ui_evolution_recorder.gd, which drops screenshot +
manifest.jsonl entries under user://ui_evolution/<version>/ -- plus, optionally,
Windows' manual Win+PrtScn rail (Pictures\\Screenshots), and copies everything
into a dated, OUTSIDE-the-repo staging directory with normalized names, next to
an ASCII index.md timeline. See docs/content/UI_EVOLUTION_CAPTURE.md for the
full convention (when to capture, where things land, how the timeline gets
mined later).

Usage:
    python tools/collect_ui_evolution.py                       # today's captures
    python tools/collect_ui_evolution.py --since 2026-07-20 --until 2026-07-27
    python tools/collect_ui_evolution.py --no-manual           # skip Pictures\\Screenshots
    python tools/collect_ui_evolution.py --dest G:/tmp/custom  # override staging dir
    python tools/collect_ui_evolution.py --dry-run             # list what would copy

Output (default G:/tmp/pdoom1-ui-evolution/<date>/ -- repo-external, per
docs/art/ART_MASTERS_POLICY.md; big/accumulating binaries never go in git):
    <version>_<index>_<scene>.png   -- from the in-game F7 rail
    manual_<timestamp>.png          -- from Win+PrtScn, unless --no-manual
    index.md                        -- ASCII timeline table
"""

import argparse
import json
import os
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

# The Godot project's actual app_userdata folder name, i.e. project.godot's
# config/name ("P(Doom)"), NOT the repo/package name "pdoom1". Verified
# empirically 2026-07-27 against %APPDATA%/Godot/app_userdata/P(Doom)/ --
# tools/process_bug_reports.py assumes "pdoom1" and is stale; do not copy that
# assumption here.
PROJECT_NAME = "P(Doom)"

UI_EVOLUTION_SUBDIR = "ui_evolution"


def resolve_user_dir() -> Path:
    """Resolve Godot's user:// root for this project, platform-aware."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", "")) / "Godot" / "app_userdata" / PROJECT_NAME
    elif sys.platform == "darwin":
        base = (
            Path.home()
            / "Library"
            / "Application Support"
            / "Godot"
            / "app_userdata"
            / PROJECT_NAME
        )
    else:
        base = Path.home() / ".local" / "share" / "godot" / "app_userdata" / PROJECT_NAME
    return base


def default_dest_root() -> Path:
    """G:/tmp is Pip's convention (docs/art/ART_MASTERS_POLICY.md masters
    staging); fall back to a home-relative dir on a machine without a G: drive."""
    g_tmp = Path("G:/tmp/pdoom1-ui-evolution")
    if g_tmp.drive and Path(g_tmp.drive + "\\").exists():
        return g_tmp
    return Path.home() / "pdoom1-ui-evolution"


def default_screenshots_dir() -> Path:
    return Path.home() / "Pictures" / "Screenshots"


def parse_date(text: str) -> date:
    return datetime.strptime(text, "%Y-%m-%d").date()


def entry_date(timestamp: str) -> date:
    # manifest timestamps are "YYYY-MM-DD HH:MM:SS" (UIEvolutionRecorder.iso_timestamp).
    return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").date()


def sweep_manifests(user_dir: Path, since: date, until: date):
    """Yield (version, entry_dict, screenshot_path) for manifest entries whose
    timestamp falls within [since, until] and whose screenshot file exists."""
    root = user_dir / UI_EVOLUTION_SUBDIR
    if not root.exists():
        return
    for version_dir in sorted(root.iterdir()):
        if not version_dir.is_dir():
            continue
        manifest_path = version_dir / "manifest.jsonl"
        if not manifest_path.exists():
            continue
        with open(manifest_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    print(f"  [!] Skipping malformed manifest line in {manifest_path}")
                    continue
                ts = entry.get("timestamp", "")
                try:
                    d = entry_date(ts)
                except ValueError:
                    print(f"  [!] Skipping entry with unparseable timestamp: {ts!r}")
                    continue
                if not (since <= d <= until):
                    continue
                shot_path = version_dir / str(entry.get("screenshot", ""))
                if not shot_path.exists():
                    print(f"  [!] Manifest references missing screenshot: {shot_path}")
                    continue
                yield version_dir.name, entry, shot_path


def sweep_manual_screenshots(screenshots_dir: Path, since: date, until: date):
    """Yield Path for any file in Pictures\\Screenshots whose mtime date falls
    within [since, until]. Windows' Win+PrtScn rail has no metadata beyond the
    filesystem timestamp, so mtime is the only signal available."""
    if not screenshots_dir.exists():
        return
    for path in sorted(screenshots_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            continue
        mtime = datetime.fromtimestamp(path.stat().st_mtime).date()
        if since <= mtime <= until:
            yield path


def safe_name(text: str) -> str:
    keep = "".join(c if (c.isalnum() or c in "-_") else "_" for c in text)
    return keep or "unknown"


def collect(
    since: date,
    until: date,
    dest_root: Path,
    include_manual: bool,
    screenshots_dir: Path,
    dry_run: bool,
) -> Path:
    user_dir = resolve_user_dir()
    print(f"[collect_ui_evolution] Godot user:// root: {user_dir}")

    label = since.isoformat() if since == until else f"{since.isoformat()}_to_{until.isoformat()}"
    dest = dest_root / label
    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)

    rows = []  # (version, timestamp, scene, turn, source, relative_path)

    for version, entry, shot_path in sweep_manifests(user_dir, since, until):
        index = entry.get("index", 0)
        scene = safe_name(str(entry.get("scene", "unknown")))
        dest_name = f"{safe_name(version)}_{int(index):04d}_{scene}.png"
        dest_path = dest / dest_name
        print(f"  [rail] {shot_path} -> {dest_name}")
        if not dry_run:
            shutil.copy2(shot_path, dest_path)
        rows.append(
            (
                version,
                entry.get("timestamp", ""),
                entry.get("scene", "unknown"),
                entry.get("turn", -1),
                "f7-rail",
                dest_name,
            )
        )

    if include_manual:
        for shot_path in sweep_manual_screenshots(screenshots_dir, since, until):
            mtime = datetime.fromtimestamp(shot_path.stat().st_mtime)
            dest_name = f"manual_{mtime.strftime('%Y%m%d_%H%M%S')}_{safe_name(shot_path.stem)}{shot_path.suffix}"
            dest_path = dest / dest_name
            print(f"  [manual] {shot_path} -> {dest_name}")
            if not dry_run:
                shutil.copy2(shot_path, dest_path)
            rows.append(
                (
                    "-",
                    mtime.strftime("%Y-%m-%d %H:%M:%S"),
                    "(manual capture)",
                    "-",
                    "win+prtscn",
                    dest_name,
                )
            )

    rows.sort(key=lambda r: r[1])  # chronological by timestamp

    if not rows:
        print("[collect_ui_evolution] Nothing found in the requested date range.")
        return dest

    index_lines = [
        "# UI evolution capture index",
        "",
        f"Range: {since.isoformat()} to {until.isoformat()}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "| Version | Timestamp | Scene | Turn | Source | File |",
        "|---|---|---|---|---|---|",
    ]
    for version, ts, scene, turn, source, dest_name in rows:
        index_lines.append(f"| {version} | {ts} | {scene} | {turn} | {source} | {dest_name} |")
    index_lines.append("")

    index_path = dest / "index.md"
    if not dry_run:
        index_path.write_text("\n".join(index_lines), encoding="utf-8")
    print(f"[collect_ui_evolution] {len(rows)} capture(s) -> {dest}")
    if not dry_run:
        print(f"[collect_ui_evolution] Index: {index_path}")
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--since", type=parse_date, default=None, help="Start date YYYY-MM-DD (default: today)"
    )
    parser.add_argument(
        "--until",
        type=parse_date,
        default=None,
        help="End date YYYY-MM-DD (default: --since, or today)",
    )
    parser.add_argument(
        "--dest", type=Path, default=None, help="Staging root (default: G:/tmp/pdoom1-ui-evolution)"
    )
    parser.add_argument(
        "--no-manual", action="store_true", help="Skip the Pictures\\Screenshots (Win+PrtScn) sweep"
    )
    parser.add_argument(
        "--screenshots-dir",
        type=Path,
        default=None,
        help="Override the manual screenshots directory",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print what would be copied without touching disk"
    )
    args = parser.parse_args()

    today = date.today()
    since = args.since or today
    until = args.until or since
    if until < since:
        parser.error("--until must not be before --since")

    dest_root = args.dest or default_dest_root()
    screenshots_dir = args.screenshots_dir or default_screenshots_dir()

    collect(since, until, dest_root, not args.no_manual, screenshots_dir, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
