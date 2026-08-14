#!/usr/bin/env python3
"""check_class_cache.py -- catch a STALE global script class cache before it eats a playtest.

Layer: PROVE -- and deliberately NOT a CI gate. See "WHY CI CANNOT CATCH THIS".

WHY (2026-08-13, cost a first-time playtester's session):
    #1211 added `godot/scripts/core/capacity.gd` declaring `class_name Capacity`.
    Godot resolves every `class_name` through `godot/.godot/global_script_class_cache.cfg`,
    which is GENERATED, GITIGNORED and PER-CHECKOUT. The agent that wrote #1211 worked in a
    separate worktree, which built its own fresh cache; 1313 tests passed there. The shared
    checkout's cache predated the new file, so after pulling `main` every script that
    referenced `Capacity` died with:

        Parse Error: Identifier "Capacity" not declared in the current scope.
        Compile Error: Failed to compile depended scripts

    cascading through the autoloads.

    THE SYMPTOM WAS NOT AN ERROR. No crash, no dialog, no red text. The window opened, the
    background art drew, the doom readout said 58.5%, the phase label said "starting up", and
    the research-quality selector (rushed / standard / thorough) still worked. Dead: every
    action icon, every upgrade, commit-month, the music, and game initialisation itself --
    the phase never advanced past "starting up". Pip, at the machine, narrating
    (capture 2026-08-13_214820__db1ee7a2):

        "all my icons have disappeared. And all my upgrades have disappeared, and I can't
         commit the month, and the music track seems not to be working, and also, there's no
         active game, so I don't think the game's actually initialized"

    It looks exactly like a game that has not finished loading. Anyone would wait. Diagnosis
    took a headless run to surface the parse errors that the windowed run swallowed.

    Fix was `godot --headless --path godot --import`. Mechanical, unambiguous, ~seconds.

WHY CI CANNOT CATCH THIS:
    CI clones fresh every run, so it ALWAYS generates a correct cache. Only a long-lived
    working copy can hold a stale one. Every check that starts clean is structurally blind to
    this class of failure -- which is most of them. That is why this tool is wired into the
    LAUNCH path (`make run`), not into a workflow. What CI can and does prove is that this
    checker itself still works: tests/test_check_class_cache.py.

    Note the difference from the already-known COLD-cache trap in CLAUDE.md ("GUT quits(0) if
    the class cache is cold"). Cold = absent, and it fails loudly and immediately. STALE =
    present, plausible, mostly correct, and it fails silently. Stale is the worse half.

WHAT IT CHECKS (pure Python, no Godot launch, ~50ms):
    The set of `class_name X` declarations in godot/**/*.gd must match, name AND path, the
    entries in godot/.godot/global_script_class_cache.cfg. Three ways that breaks:

      MISSING  -- declared in source, absent from cache. A new class the cache never saw.
                  This is the #1211 shape and the one that kills a playtest.
      MOVED    -- in both, but the cache points at a different path (a rename or a move).
      ORPHANED -- in the cache, no longer declared anywhere in source (a delete or a rename's
                  other half). Godot tolerates this better, but it means the same thing:
                  the cache does not describe this checkout.

USAGE:
    python tools/check_class_cache.py             # report; exit 0 clean, 1 stale
    python tools/check_class_cache.py --repair    # if stale, run --import and re-check
    python tools/check_class_cache.py --quiet     # print only on failure (for wrappers)

    --repair is the recommended mode for anything that launches the game. The repair is
    mechanical and there is no judgement call to make, so refusing to launch would just be
    a slower way of arriving at the same command. Auto-repair converts a silent, mystifying
    failure into a named, self-healing one -- which is the whole value here, because the
    failure mode is a screen that looks like it is still loading.

EXIT CODES:
    0  cache agrees with source (or --repair made it agree)
    1  cache is stale (or --repair could not fix it)
    2  could not run the check at all (no godot/ tree, Godot binary missing for --repair)
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT_ROOT = REPO_ROOT / "godot"
CACHE_REL = Path(".godot") / "global_script_class_cache.cfg"

REPAIR_ARGS = ["--headless", "--path", "godot", "--import"]
REPAIR_HINT = "godot --headless --path godot --import"

# `class_name Foo` / `class_name Foo extends Bar`, at the start of a line. GDScript only
# permits it at top level, but leading whitespace is tolerated here so a stray indent shows up
# as a finding rather than vanishing from the scan.
CLASS_NAME_RE = re.compile(r"^[ \t]*class_name[ \t]+([A-Za-z_][A-Za-z0-9_]*)")

# One cache record: "class": &"Foo", ... "path": "res://a/b.gd". Key order is stable in
# Godot's writer (alphabetical), so class always precedes path within a record, but the regex
# is anchored on the pair rather than on record boundaries to survive a reordering.
CACHE_ENTRY_RE = re.compile(
    r'"class"\s*:\s*&?"([^"]+)".*?"path"\s*:\s*&?"([^"]+)"',
    re.DOTALL,
)

TRIPLE_QUOTES = ('"""', "'''")


def _code_part(line: str) -> str:
    """Strip a trailing '#' comment so a commented-out declaration is not counted."""
    hashpos = line.find("#")
    return line if hashpos == -1 else line[:hashpos]


def res_path(path: Path, godot_root: Path) -> str:
    """godot/scripts/core/capacity.gd -> res://scripts/core/capacity.gd"""
    return "res://" + path.resolve().relative_to(godot_root.resolve()).as_posix()


def scan_source(godot_root: Path | None = None) -> dict[str, str]:
    """Map every `class_name` declared under godot/**/*.gd to its res:// path.

    Skips docstring blocks so prose that quotes a declaration is not mistaken for one.

    The root is resolved at CALL time, not bound as a default, so tests can point the
    scanner at a synthetic tree.
    """
    godot_root = GODOT_ROOT if godot_root is None else godot_root
    declared: dict[str, str] = {}
    for gd in sorted(godot_root.rglob("*.gd")):
        # .godot/ is the generated dir itself; anything in there is not source.
        if ".godot" in gd.parts:
            continue
        try:
            text = gd.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "class_name" not in text:
            continue
        in_docstring = False
        for raw in text.splitlines():
            delims = sum(raw.count(q) for q in TRIPLE_QUOTES)
            was_in_docstring = in_docstring
            if delims % 2 == 1:
                in_docstring = not in_docstring
            if was_in_docstring:
                continue
            match = CLASS_NAME_RE.match(_code_part(raw))
            if match:
                declared[match.group(1)] = res_path(gd, godot_root)
                break  # one class_name per file; the rest of the file cannot add another
    return declared


def parse_cache(cache_path: Path) -> dict[str, str] | None:
    """Map class name -> res:// path from the cache. None if the cache does not exist."""
    if not cache_path.exists():
        return None
    text = cache_path.read_text(encoding="utf-8", errors="replace")
    return {name: path for name, path in CACHE_ENTRY_RE.findall(text)}


def compare(declared: dict[str, str], cached: dict[str, str]) -> dict[str, list]:
    """Findings, by kind. Empty lists everywhere = the cache describes this checkout."""
    missing = sorted((n, p) for n, p in declared.items() if n not in cached)
    orphaned = sorted((n, p) for n, p in cached.items() if n not in declared)
    moved = sorted(
        (n, declared[n], cached[n]) for n in declared if n in cached and declared[n] != cached[n]
    )
    return {"missing": missing, "orphaned": orphaned, "moved": moved}


def is_stale(findings: dict[str, list]) -> bool:
    return any(findings.values())


def report(findings: dict[str, list], cache_path: Path) -> None:
    print("STALE CLASS CACHE -- this checkout will run the WRONG code, silently.")
    print(f"  cache: {cache_path}")
    print()
    if findings["missing"]:
        print(
            f"  {len(findings['missing'])} class_name(s) declared in source but NOT in the cache."
        )
        print("  Every script referencing one of these will fail to parse, and the failure")
        print("  will look like a game that is still loading -- no crash, no dialog.")
        for name, path in findings["missing"]:
            print(f"    MISSING   {name:<32} {path}")
        print()
    if findings["moved"]:
        print(f"  {len(findings['moved'])} class(es) the cache points at the wrong file:")
        for name, src, cache in findings["moved"]:
            print(f"    MOVED     {name:<32} source={src}")
            print(f"    {'':<42}cache ={cache}")
        print()
    if findings["orphaned"]:
        print(f"  {len(findings['orphaned'])} cache entry(ies) with no declaration left in source:")
        for name, path in findings["orphaned"]:
            print(f"    ORPHANED  {name:<32} {path}")
        print()
    print(f"  FIX:  {REPAIR_HINT}")
    print("        (or re-run this with --repair, which does exactly that)")


def find_godot() -> str | None:
    return os.environ.get("GODOT_BIN") or shutil.which("godot")


def run_import(godot_bin: str, quiet: bool) -> int:
    """Rebuild the cache. Godot's first import pass floods stderr with the very
    class-cache SCRIPT ERRORs we are repairing -- expected noise, not a failure
    (CLAUDE.md, "Fresh worktree gotcha")."""
    if not quiet:
        print(f"  repairing: {godot_bin} {' '.join(REPAIR_ARGS)}")
        print("  (SCRIPT ERROR class-cache lines during this pass are expected noise)")
    proc = subprocess.run(
        [godot_bin, *REPAIR_ARGS],
        cwd=REPO_ROOT,
        capture_output=quiet,
        text=True,
    )
    return proc.returncode


def check(godot_root: Path | None = None) -> tuple[dict[str, list], dict[str, str]]:
    godot_root = GODOT_ROOT if godot_root is None else godot_root
    declared = scan_source(godot_root)
    cached = parse_cache(godot_root / CACHE_REL)
    if cached is None:
        # A cold cache (no .godot at all) is the loud, already-known failure; report it as
        # every class missing so the same --repair path fixes it.
        cached = {}
    return compare(declared, cached), declared


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--repair",
        action="store_true",
        help="if stale, run the Godot --import pass and re-check",
    )
    ap.add_argument("--quiet", action="store_true", help="print nothing unless something is wrong")
    args = ap.parse_args(argv)

    if not GODOT_ROOT.is_dir():
        print(f"ERROR: no godot/ tree at {GODOT_ROOT}", file=sys.stderr)
        return 2

    cache_path = GODOT_ROOT / CACHE_REL
    findings, declared = check()

    if not is_stale(findings):
        if not args.quiet:
            print(f"class cache OK -- {len(declared)} class_name declaration(s) all resolve.")
        return 0

    report(findings, cache_path)

    if not args.repair:
        return 1

    godot_bin = find_godot()
    if not godot_bin:
        print()
        print("ERROR: --repair asked for, but no Godot binary found on PATH or in $GODOT_BIN.")
        print(f"       Run this yourself, from {REPO_ROOT}:  {REPAIR_HINT}")
        return 2

    print()
    rc = run_import(godot_bin, args.quiet)

    findings, declared = check()
    if is_stale(findings):
        print()
        print(f"REPAIR FAILED -- cache still stale after --import (godot exit {rc}).")
        report(findings, cache_path)
        return 1

    print()
    print(f"repaired -- {len(declared)} class_name declaration(s) now resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
