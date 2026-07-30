#!/usr/bin/env python3
"""Pull fresh OBS recordings into the repo's working area.

OBS writes everything to one flat folder that only grows (4.2 GB as of
2026-07-30). This copies across only what is NEW, so the repo side stays a
working set rather than a second copy of the archive.

Defaults to TODAY only, because the common case is "I just recorded something,
go get it". Skips anything already present at the destination with the same
size, so re-running is free and safe.

Copies rather than moves by default: OBS's folder stays the source of truth
until you have deliberately decided what to keep. Pass --move once a retention
policy exists.

Usage:
    python tools/ingest_recordings.py                    # today's, copy, report
    python tools/ingest_recordings.py --dry-run          # show what it would do
    python tools/ingest_recordings.py --days 3           # last 3 days
    python tools/ingest_recordings.py --since 2026-07-28
    python tools/ingest_recordings.py --process          # then build playtest reports
"""

import argparse
import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path("G:/012 OBS Outputs")
DEFAULT_DEST = REPO / "art_generated" / "audiodump"
VIDEO_SUFFIXES = {".mp4", ".mkv", ".mov", ".flv", ".m4a", ".mp3", ".wav", ".flac"}


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} GB"


def cutoff_from_args(args) -> dt.datetime:
    if args.all:
        return dt.datetime.min
    if args.since:
        return dt.datetime.strptime(args.since, "%Y-%m-%d")
    if args.days is not None:
        return dt.datetime.now() - dt.timedelta(days=args.days)
    midnight = dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    ap.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    ap.add_argument("--since", help="YYYY-MM-DD; files modified on or after this date")
    ap.add_argument("--days", type=int, help="files modified in the last N days")
    ap.add_argument("--all", action="store_true", help="ignore dates entirely")
    ap.add_argument("--move", action="store_true", help="move instead of copy")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--process",
        action="store_true",
        help="run tools/playtest_report.py on each newly ingested file",
    )
    args = ap.parse_args()

    if not args.source.is_dir():
        sys.exit(f"[!] source folder not found: {args.source}")
    args.dest.mkdir(parents=True, exist_ok=True)

    cutoff = cutoff_from_args(args)
    print(f"[*] source {args.source}")
    print(f"[*] dest   {args.dest}")
    print(
        f"[*] taking files modified on/after {cutoff:%Y-%m-%d %H:%M}"
        if cutoff != dt.datetime.min
        else "[*] taking ALL files"
    )

    candidates, skipped_old = [], 0
    for path in sorted(args.source.iterdir()):
        if not path.is_file() or path.suffix.lower() not in VIDEO_SUFFIXES:
            continue
        if dt.datetime.fromtimestamp(path.stat().st_mtime) < cutoff:
            skipped_old += 1
            continue
        candidates.append(path)

    if not candidates:
        print(f"[*] nothing new ({skipped_old} older files left alone)")
        return 0

    ingested, already, total = [], 0, 0
    for src in candidates:
        dst = args.dest / src.name
        if dst.exists() and dst.stat().st_size == src.stat().st_size:
            already += 1
            print(f"    = {src.name:34s} {human(src.stat().st_size):>9s}  already here")
            continue
        size = src.stat().st_size
        verb = "move" if args.move else "copy"
        print(f"    {'~' if args.dry_run else '+'} {src.name:34s} {human(size):>9s}  {verb}")
        if not args.dry_run:
            if args.move:
                shutil.move(str(src), str(dst))
            else:
                shutil.copy2(src, dst)
            ingested.append(dst)
        total += size

    print(
        f"[*] {len(ingested)} ingested ({human(total)}), {already} already present, "
        f"{skipped_old} older skipped"
    )

    if args.process and ingested:
        script = REPO / "tools" / "playtest_report.py"
        for path in ingested:
            print(f"\n=== playtest_report: {path.name}")
            subprocess.run([sys.executable, str(script), str(path)], check=False)

    if args.dry_run:
        print("[*] dry run -- nothing was written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
