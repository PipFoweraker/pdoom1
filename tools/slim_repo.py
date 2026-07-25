#!/usr/bin/env python3
"""Reclaim git + .pck weight -- the slack mapped by the 2026-07-25 archival pass (#861).

SAFE by default: a bare run is a DRY RUN that only reports. Pass --apply to execute.
Each phase is independent and guarded. Run from the repo root.

Phases:
  A  untrack art_generated/   -- gitignored + regenerable; `git rm -r --cached`
     (files stay on your disk). NO prereq -- safe to run today, ~85 MB off git.
  B  offload art_source masters (files > 1 MB) to DreamObjects, then untrack them.
     Requires the 'dreamobjects' rclone remote (see tools/archive_masters.py) so
     nothing is lost. Only >1 MB files move; the <=1 MB canonical art stays in git.
  C  delete proven-dead hi-res portrait variants in godot/ (_512 / _1024).
     Re-verifies uid:// AND res:// are unreferenced FIRST -- the #787 dynamic-path
     trap: the _256 and _64 sets are constructed-path loads and are NEVER touched.

Usage:
  python tools/slim_repo.py                        # dry run: report all phases + MB
  python tools/slim_repo.py --apply                # phases A + C (safe, no bucket needed)
  python tools/slim_repo.py --apply --with-masters # also phase B (needs the rclone remote)

After --apply, review `git status`, then commit ONLY the untracked/deleted paths
(never `git add -A` -- the .import/.uid churn).
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
MB = 1024 * 1024
REMOTE = "dreamobjects:pdoom1-art-masters"


def sh(cmd):
    return subprocess.run(cmd, cwd=REPO, text=True, capture_output=True)


def tracked(pathspec):
    return [line for line in sh(["git", "ls-files", pathspec]).stdout.splitlines() if line]


def grep_godot(token):
    return [
        line
        for line in sh(["git", "grep", "-l", "-F", token, "--", "godot/"]).stdout.splitlines()
        if line
    ]


def phase_a(apply):
    files = tracked("art_generated/")
    size = sum((REPO / f).stat().st_size for f in files if (REPO / f).is_file())
    print(f"\n[A] untrack art_generated/  -- {len(files)} tracked files, {size / MB:.1f} MB")
    if not files:
        print("    already untracked -- nothing to do")
        return 0
    print(
        "    -> git rm -r --cached art_generated  (regenerable; already gitignored; stays on disk)"
    )
    if apply:
        r = sh(["git", "rm", "-r", "--cached", "art_generated"])
        print("    applied." if r.returncode == 0 else f"    FAILED: {r.stderr.strip()}")
    return size


def phase_b(apply):
    src = REPO / "art_source"
    if not src.is_dir():
        print("\n[B] art_source/ not present -- skipping")
        return 0
    big = [p for p in src.rglob("*") if p.is_file() and p.stat().st_size > MB]
    size = sum(p.stat().st_size for p in big)
    print(
        f"\n[B] offload art_source masters (>1 MB) -> DreamObjects  -- {len(big)} files, {size / MB:.1f} MB"
    )
    if not big:
        print("    no >1 MB masters in art_source -- nothing to offload")
        return 0
    if shutil.which("rclone") is None:
        print(
            "    rclone not found -- configure the 'dreamobjects' remote first "
            "(tools/archive_masters.py header). SKIPPED."
        )
        return 0
    print(f"    -> for each master: rclone copy to {REMOTE}, verify, then git rm --cached")
    if apply:
        for p in big:
            rel = p.relative_to(REPO).as_posix()
            dest = f"{REMOTE}/{p.parent.relative_to(REPO).as_posix()}"
            if sh(["rclone", "copy", str(p), dest]).returncode != 0:
                print(f"    SKIP {rel}: rclone copy failed")
                continue
            if sh(["rclone", "lsf", f"{dest}/{p.name}"]).stdout.strip() != p.name:
                print(f"    SKIP {rel}: could not verify upload -- left tracked")
                continue
            sh(["git", "rm", "--cached", rel])
            print(f"    offloaded + untracked {rel}")
    return size


def _uids_in(import_file):
    uids = []
    if import_file.is_file():
        for line in import_file.read_text(errors="ignore").splitlines():
            if line.strip().startswith("uid=") and "uid://" in line:
                uids.append(line.split('"')[1] if '"' in line else line.split("uid=")[-1].strip())
    return uids


def _own_files(png):
    """The asset's OWN files (image + its .import/.uid) -- must not count as refs."""
    out = {png.relative_to(REPO).as_posix()}
    for s in (png.with_suffix(png.suffix + ".import"), png.with_suffix(png.suffix + ".uid")):
        if s.is_file():
            out.add(s.relative_to(REPO).as_posix())
    return out


def phase_c(apply):
    pdir = REPO / "godot" / "assets" / "portraits"
    if not pdir.is_dir():
        print("\n[C] godot/assets/portraits not present -- skipping")
        return 0
    imgs = [
        p
        for p in pdir.rglob("*")
        if p.is_file()
        and (p.stem.endswith("_512") or p.stem.endswith("_1024"))
        and p.suffix.lower() in (".png", ".webp")
    ]
    print(f"\n[C] delete dead hi-res portrait variants (_512/_1024)  -- {len(imgs)} images")
    safe, unsafe = [], []
    for p in imgs:
        own = _own_files(p)  # exclude the asset's OWN metadata sidecars from the ref check
        res = "res://" + p.relative_to(REPO).as_posix().split("godot/", 1)[-1]
        refs = [r for r in grep_godot(res) if r not in own]
        for uid in _uids_in(p.with_suffix(p.suffix + ".import")):
            refs += [r for r in grep_godot(uid) if r not in own]
        (safe if not refs else unsafe).append((p, own, refs))
    dead = sum(
        (REPO / f).stat().st_size for _, own, _r in safe for f in own if (REPO / f).is_file()
    )
    print(
        f"    verified-unreferenced (deletable): {len(safe)} images + sidecars, {dead / MB:.1f} MB"
    )
    if unsafe:
        p, _own, refs = unsafe[0]
        print(f"    STILL REFERENCED -- NOT deleting {len(unsafe)} (e.g. {p.name} <- {refs[:1]})")
    if apply and safe:
        for _, own, _r in safe:
            for f in own:
                sh(["git", "rm", f])
        print("    deleted the verified-unreferenced set (images + sidecars).")
    return dead


def main():
    ap = argparse.ArgumentParser(description="Reclaim git/.pck weight (safe; dry-run by default).")
    ap.add_argument("--apply", action="store_true", help="execute (default: dry-run report only)")
    ap.add_argument(
        "--with-masters", action="store_true", help="also run phase B (needs rclone remote)"
    )
    args = ap.parse_args()
    if not (REPO / ".git").exists():
        print("not a git repo root")
        return 1
    print("=== repo slim ===  " + ("(APPLYING)" if args.apply else "(DRY RUN)"))
    total = phase_a(args.apply)
    if args.with_masters:
        total += phase_b(args.apply)
    else:
        print("\n[B] skipped (pass --with-masters once the DreamObjects rclone remote is set up)")
    total += phase_c(args.apply)
    print(f"\n=== reclaimable in this run: ~{total / MB:.0f} MB ===")
    print(
        "dry run -- re-run with --apply to execute."
        if not args.apply
        else "done -- review `git status`, then commit ONLY these paths (never git add -A)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
