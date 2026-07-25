#!/usr/bin/env python3
"""Sync the local art-masters cache to off-site object storage (DreamObjects).

Masters are a regenerable convenience cache (see docs/art/ART_MASTERS_POLICY.md),
kept OUT of git. This pushes the local staging folder to a DreamObjects
(S3-compatible) bucket so the only copy is not the dev machine's disk.

Prereqs (one-time):
  1. Install rclone: https://rclone.org/install/
  2. Configure a remote named 'dreamobjects' (S3-compatible):
       rclone config
       - type: s3, provider: Other / S3-compatible
       - endpoint: objects-us-east-1.dream.io (or your region's endpoint)
       - access_key_id / secret_access_key from the DreamHost panel
  3. Create the bucket once:
       rclone mkdir dreamobjects:pdoom1-art-masters

Usage:
  python tools/archive_masters.py            # dry-run (shows what WOULD sync)
  python tools/archive_masters.py --push     # actually sync
  python tools/archive_masters.py --push --local G:/tmp/pdoom1-art-masters
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

DEFAULT_LOCAL = "G:/tmp/pdoom1-art-masters"
REMOTE = "dreamobjects:pdoom1-art-masters"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync art masters to DreamObjects.")
    parser.add_argument("--local", default=DEFAULT_LOCAL, help="local masters folder")
    parser.add_argument("--push", action="store_true", help="sync (default: dry-run)")
    args = parser.parse_args()

    if shutil.which("rclone") is None:
        print("ERROR: rclone not found. Install: https://rclone.org/install/")
        return 1

    cmd = ["rclone", "sync", args.local, REMOTE, "--progress"]
    if not args.push:
        cmd.append("--dry-run")
        print("DRY RUN (no changes). Re-run with --push to sync.")

    print("Running:", " ".join(cmd))
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
