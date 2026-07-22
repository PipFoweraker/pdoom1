# !/usr/bin/env python3
"""
build_release.py -- export a P(Doom) build FROM A VERIFIED-CLEAN STATE.

WHY THIS EXISTS (the hard-won lesson behind v0.11.0-alpha):
    Godot's `godot/.godot/exported/` cache can silently pack a STALE converted scene.
    Running `--import` does NOT clear it. The result: an export command reports SUCCESS
    while packing OLD scenes/scripts -- so a fix (or a diagnostic trace) you KNOW you
    wrote is simply not in the build you test. ~12 test cycles were burned re-running an
    already-fixed bug because nobody could prove which source a given .pck was built from.

THE DISCIPLINE THIS TOOL ENFORCES (no build ships unverified):
    1. `rm -rf godot/.godot` BEFORE the export -- forces a genuine from-scratch build.
    2. Drop a UNIQUELY-NAMED marker script into the project so its res:// path lands in
       the exported pack's file table.
    3. Export, then VERIFY the marker's unique token is present in the .pck (or the exe,
       if the pack is embedded). If it is missing, the export was served stale -> this
       tool exits NON-ZERO and LOUD. A green build here means the pack provably reflects
       the current working tree.

FRESHNESS-ANCHOR NOTE (why a marker FILE, not a grepped string):
    In this project's export config, GDScript is packed as binary-tokenized `.gdc`, so
    string LITERALS inside scripts do NOT survive as grep-able text -- the old
    "grep the pack for a printerr tag" advice is UNRELIABLE here. Resource PATHS/filenames
    DO survive in the pack file table. So we anchor on a unique FILENAME, which is a
    reliable, encoding-independent freshness proof.

RENDER-GATE LIMITATION:
    A clean, verified pack proves the RIGHT BITS shipped. It does NOT prove the game runs
    on a real GPU -- headless tooling never GPU-decodes textures or runs the release
    renderer. The human release-build playtest remains the final ship gate.

Usage:
    python tools/build_release.py                       # release, Windows, default paths
    python tools/build_release.py --mode debug          # debug build (symbolized crash backtrace)
    python tools/build_release.py --preset "Windows Desktop" --output builds/win
    python tools/build_release.py --godot-path "C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe"
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import uuid
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


def find_godot(explicit: Optional[str]) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.exists():
            fail(f"--godot-path does not exist: {p}")
        return p
    for cand in DEFAULT_GODOT_CANDIDATES:
        if cand.exists():
            return cand
    which = shutil.which("godot")
    if which:
        return Path(which)
    fail("Godot executable not found; pass --godot-path")
    raise SystemExit(2)  # unreachable; keeps type-checkers happy


def fail(msg: str) -> None:
    print(f"\n[BUILD-VERIFY][FATAL] {msg}", file=sys.stderr)
    sys.exit(1)


def info(msg: str) -> None:
    print(f"[build_release] {msg}")


def run(cmd: list[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    info("run: " + " ".join(str(c) for c in cmd))
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, check=False)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--godot-path", default=None, help="Path to the Godot 4.5.1 executable.")
    ap.add_argument("--preset", default="Windows Desktop", help="export_presets.cfg preset name.")
    ap.add_argument("--mode", choices=["release", "debug"], default="release", help="Export mode.")
    ap.add_argument(
        "--output", default=None, help="Output directory (default: builds/<preset-slug>)."
    )
    ap.add_argument("--project", default=None, help="Godot project dir (default: <repo>/godot).")
    ap.add_argument(
        "--no-clean",
        action="store_true",
        help="Skip the rm -rf .godot from-scratch step (NOT recommended).",
    )
    ap.add_argument(
        "--keep-marker",
        action="store_true",
        help="Leave the freshness marker file in the project tree.",
    )
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    project = Path(args.project).resolve() if args.project else (repo_root / "godot")
    if not (project / "project.godot").exists():
        fail(f"no project.godot under {project}")

    godot = find_godot(args.godot_path)
    info(f"Godot: {godot}")
    info(f"Project: {project}")
    info(f"Mode: {args.mode}   Preset: {args.preset}")

    out_dir = (
        Path(args.output).resolve()
        if args.output
        else (repo_root / "builds" / args.preset.replace(" ", "_").lower())
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    exe_path = out_dir / "PDoom.exe"

    dot_godot = project / ".godot"

    # ---- STEP 1: from-scratch state (the anti-stale-cache core) -----------------
    if not args.no_clean:
        if dot_godot.exists():
            info(
                f"rm -rf {dot_godot}  (forcing a from-scratch build; clears .godot/exported cache)"
            )
            shutil.rmtree(dot_godot, ignore_errors=True)
        else:
            info(".godot absent already (clean).")
    else:
        info("--no-clean set: NOT clearing .godot (stale-cache risk accepted by caller).")

    # ---- STEP 2: unique freshness marker ----------------------------------------
    token = "buildstamp" + uuid.uuid4().hex  # e.g. buildstamp3f9a...  (alnum, grep-safe)
    marker_path = project / f"{token}.gd"
    marker_path.write_text(
        "extends Node\n"
        "# Auto-generated build-freshness marker (tools/build_release.py). Safe to delete.\n"
        f'const MARKER := "{token}"\n',
        encoding="utf-8",
    )
    info(f"wrote freshness marker: {marker_path.name}")

    # ---- STEP 2.5: stamp the build BEFORE import (fixes the in-game "unstamped") -
    # write_build_stamp.py -> godot/build_stamp.txt (commit/date/branch), read by
    # build_info.gd at startup; without it the DEV BUILD overlay reads "unstamped".
    # sync_version.py --check surfaces (non-fatally) any drift between version.txt and
    # the derived copies (game_config.gd / project.godot / export_presets.cfg /
    # welcome.tscn) -- the FATAL version gate lives in CI/pre-release, so a diagnostic
    # build is never blocked, only warned.
    stamp_tool = repo_root / "tools" / "write_build_stamp.py"
    if stamp_tool.exists():
        r = run([sys.executable, str(stamp_tool)])
        if r.returncode != 0:
            fail(f"write_build_stamp.py exited {r.returncode}; the build would be 'unstamped'.")
    else:
        info("write_build_stamp.py not found; build may show 'unstamped'.")

    sync_tool = repo_root / "tools" / "sync_version.py"
    if sync_tool.exists():
        r = run([sys.executable, str(sync_tool), "--check"])
        if r.returncode != 0:
            info(
                "WARNING: sync_version --check reports version drift (see above). Run "
                "`python tools/sync_version.py` and commit before a real release cut."
            )

    try:
        # ---- STEP 3: import (populates a fresh .godot incl. the marker) ----------
        r = run([str(godot), "--headless", "--path", str(project), "--import"])
        # Import can exit non-zero on benign class-cache noise in a cold tree; do not
        # gate on it. The export below is the real gate.
        if r.returncode != 0:
            info(f"import returned {r.returncode} (tolerated; cold-cache noise is expected).")

        # ---- STEP 4: export -----------------------------------------------------
        export_flag = "--export-release" if args.mode == "release" else "--export-debug"
        r = run(
            [
                str(godot),
                "--headless",
                "--path",
                str(project),
                export_flag,
                args.preset,
                str(exe_path),
            ]
        )
        if r.returncode != 0:
            fail(f"godot {export_flag} exited {r.returncode} (see output above).")
        if not exe_path.exists():
            fail(f"export reported success but {exe_path} does not exist.")

        # ---- STEP 5: VERIFY the pack is fresh -----------------------------------
        pck_path = exe_path.with_suffix(".pck")
        search_targets = [p for p in (pck_path, exe_path) if p.exists()]
        needle = token.encode("ascii")
        found_in = None
        for tgt in search_targets:
            data = tgt.read_bytes()
            if needle in data:
                found_in = tgt
                break
        if found_in is None:
            fail(
                "FRESHNESS CHECK FAILED: marker '%s' NOT found in %s.\n"
                "  The exported pack does NOT reflect the current working tree -- it was\n"
                "  almost certainly served from a STALE .godot/exported cache. DO NOT SHIP.\n"
                "  Re-run WITHOUT --no-clean." % (token, [str(t) for t in search_targets])
            )

        # ---- success ------------------------------------------------------------
        size_mb = (pck_path.stat().st_size if pck_path.exists() else exe_path.stat().st_size) / (
            1024 * 1024
        )
        print("\n" + "=" * 68)
        print("[BUILD-VERIFY][PASS] pack is provably fresh.")
        print(f"  marker token : {token}")
        print(f"  found in     : {found_in}")
        print(f"  exe          : {exe_path}")
        if pck_path.exists():
            print(f"  pck          : {pck_path}  ({size_mb:.1f} MB)")
        print(f"  mode         : {args.mode}")
        print("=" * 68)
        print("REMINDER: a fresh, verified pack proves the RIGHT BITS shipped. It does NOT")
        print("prove the game runs on a real GPU. The human release-build playtest")
        print("(play -> lose -> leaderboard on a real machine) is the final ship gate.")
        return 0
    finally:
        if not args.keep_marker and marker_path.exists():
            marker_path.unlink()
            info(f"removed freshness marker: {marker_path.name}")


if __name__ == "__main__":
    sys.exit(main())
