#!/usr/bin/env python3
"""Write a build stamp that identifies exactly which commit a build came from.

Produces ``godot/build_stamp.txt`` (a plain res:// text file the in-game DEV BUILD
overlay reads at startup — see ``godot/scripts/core/build_info.gd``). Format is a
few ``key=value`` lines so it stays trivially parseable from GDScript::

    commit=abc1234
    date=2026-07-11
    branch=feat/dev-build-overlay-ledger

Reliability model (we chose reliability over cleverness):
  * ``date`` is always written from the system clock, so the stamp is never empty
    even in a checkout with no git available.
  * ``commit`` is best-effort ``git rev-parse --short HEAD``; if git is missing or
    this is not a repo, it falls back to ``unknown`` and the overlay still shows a
    dated stamp.

Run this before cutting a build / export so the tester can confirm the exact build:

    python tools/write_build_stamp.py

Note: the committed stamp necessarily records the *parent* commit (HEAD before this
change is committed). That is fine for "which build am I on" — it pins the build to
a known point in history. Re-run in CI/packaging to refresh right before export.
"""
from __future__ import annotations

import datetime
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STAMP_PATH = REPO_ROOT / "godot" / "build_stamp.txt"


def _git(*args: str) -> str:
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return ""


def main() -> int:
    commit = _git("rev-parse", "--short", "HEAD") or "unknown"
    branch = _git("rev-parse", "--abbrev-ref", "HEAD") or "unknown"
    date = datetime.date.today().isoformat()

    STAMP_PATH.parent.mkdir(parents=True, exist_ok=True)
    STAMP_PATH.write_text(
        f"commit={commit}\ndate={date}\nbranch={branch}\n",
        encoding="ascii",
    )
    print(f"[write_build_stamp] wrote {STAMP_PATH}")
    print(f"  commit={commit} date={date} branch={branch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
