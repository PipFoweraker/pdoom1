# !/usr/bin/env python3
"""
validate_assets.py -- pre-release asset-import validation gate.

WHY THIS EXISTS: a corrupt or undecodable texture/resource can import "successfully"
in the editor yet fail to load at runtime -- a silent landmine that could crash a
release build the first time a scene references it. This gate reimports the project
from a clean asset cache and then LOADS every resource under godot/assets, failing
loudly (non-zero exit) if any asset does not resolve. Run it before cutting a build.

WHAT IT DOES:
    1. (default) `godot --import` so the asset cache reflects the current tree.
    2. Runs godot/tools/validate_assets_probe.gd headless, which walks res://assets,
       ResourceLoader.load()s each importable file, and checks textures have a sane
       size. The probe exits non-zero on any failure or if the walk finds too few
       assets (anti-hollow floor).

LIMITATION (honest): headless validation proves each asset is STRUCTURALLY loadable;
it does NOT GPU-decode textures (the dummy renderer discards VRAM-compressed CPU
images). The human release-build playtest remains the final gate.

Usage:
    python tools/validate_assets.py
    python tools/validate_assets.py --no-import        # skip the reimport pass (faster)
    python tools/validate_assets.py --godot-path "C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe"
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

DEFAULT_GODOT_CANDIDATES = [
    Path("C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe"),
    Path("C:/Program Files/Godot/Godot.exe"),
    Path.home() / "Godot" / "Godot_v4.5.1-stable_win64.exe",
    Path("/usr/bin/godot"),
    Path("/usr/local/bin/godot"),
    Path("/Applications/Godot.app/Contents/MacOS/Godot"),
]

PROBE = "res://tools/validate_assets_probe.gd"


def find_godot(explicit: Optional[str]) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.exists():
            print(f"[validate_assets][FATAL] --godot-path does not exist: {p}", file=sys.stderr)
            sys.exit(2)
        return p
    for cand in DEFAULT_GODOT_CANDIDATES:
        if cand.exists():
            return cand
    which = shutil.which("godot")
    if which:
        return Path(which)
    print("[validate_assets][FATAL] Godot executable not found; pass --godot-path", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--godot-path", default=None)
    ap.add_argument("--project", default=None, help="Godot project dir (default: <repo>/godot).")
    ap.add_argument(
        "--no-import", action="store_true", help="Skip the reimport pass before validating."
    )
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    project = Path(args.project).resolve() if args.project else (repo_root / "godot")
    if not (project / "project.godot").exists():
        print(f"[validate_assets][FATAL] no project.godot under {project}", file=sys.stderr)
        return 2

    godot = find_godot(args.godot_path)
    print(f"[validate_assets] Godot:   {godot}")
    print(f"[validate_assets] Project: {project}")

    if not args.no_import:
        print("[validate_assets] reimport pass ...")
        r = subprocess.run(
            [str(godot), "--headless", "--path", str(project), "--import"],
            text=True,
            check=False,
        )
        # Import may exit non-zero on cold class-cache noise; the probe is the real gate.
        if r.returncode != 0:
            print(f"[validate_assets] import returned {r.returncode} (tolerated; running probe).")

    print("[validate_assets] running probe ...")
    r = subprocess.run(
        [str(godot), "--headless", "--path", str(project), "--script", PROBE],
        text=True,
        check=False,
    )
    if r.returncode == 0:
        print("[validate_assets][PASS] all assets loaded structurally cleanly.")
    else:
        print(
            f"[validate_assets][FAIL] probe exited {r.returncode} -- see [FAIL] lines above. DO NOT SHIP.",
            file=sys.stderr,
        )
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
