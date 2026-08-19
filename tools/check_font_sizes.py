#!/usr/bin/env python3
"""check_font_sizes.py -- count what the font-size SSOT still cannot reach.

Layer: PROVE

    python tools/check_font_sizes.py            # census + ratchet (CI / pre-commit)
    python tools/check_font_sizes.py --report    # census only, never fails
    python tools/check_font_sizes.py --by-file   # where the remaining sites are

WHY THIS FILE EXISTS AT ALL.

Pip, after the 2026-08-14 playtest: "the text can just all universally go up 2
to 4 points apart from maybe the player guide." That was a 378-site mechanical
edit, because nothing in the project was central enough to turn.

RULING: 2026-08-17 -- the game has ONE font-size lever (theme/base_theme.tres default_font_size, registered as the project theme) and a raw size override is a deviation that has to earn its line -- flavour: ui-legibility -- mechanism: tools/check_font_sizes.py

MEASURED 2026-08-17, before the change:

    215  theme_override_font_sizes/* declarations across godot/scenes/
    163  add_theme_font_size_override() calls across scripts/ and autoload/
     19  distinct values, from 8 to 72
      1  central scale (ThemeManager.ThemeData.fonts) -- with ONE caller
      0  times that scale had ever changed a rendered glyph

The last two lines are the whole story. `notification_manager.gd:167` asked
`get_font_size("body")` while the dictionary key was `"body_size"`, so it took
the silent `, 16` fallback on every call since it was written. A scale with one
caller, and that caller wired to a fallback, is indistinguishable from no scale.
Roughly 52% of all runtime-set text in the game was 12px or smaller.

WHAT CHANGED, AND WHAT DID NOT.

`godot/theme/base_theme.tres` now carries `default_font_size` and is registered
as `gui/theme/custom`, the bottom of Godot's theme lookup chain. That reaches
every UNOVERRIDDEN Control in the game, including `main.tscn` (which declares no
theme) and the panels built in code with no `.tscn` at all. Proved, not assumed,
by `godot/tests/unit/test_font_size_ssot.gd`, which measures through
`get_theme_font_size()` on real Controls rather than reading the resource file.

AN EXPLICIT OVERRIDE STILL WINS. That is Godot's rule and this tool does not
change it -- it counts the overrides so the number is measurable rather than
remembered. 86 scene overrides in the 16..19 band were deleted in the first
pass: 16 merely restated Godot's old built-in default, and 17-19 sat at or below
the new body size, so leaving them would have inverted the hierarchy -- headings
smaller than the prose beneath them.

WHAT IS DELIBERATELY LEFT. Sizes <= 15 are a real "smaller than body" signal on
dense panels; blanket-deleting them would jump a 9px stat line straight to body
size inside a fixed-size box that does not grow. Sizes >= 20 are deliberately
larger and still are. Both need the size-token pass and a visual review, which
is different work from building the lever.

THE RATCHET. CEILING is not a target, it is a one-way valve: the count may fall
freely and may not rise. A new raw override is not forbidden -- it is forbidden
to add one WITHOUT lowering the ceiling to match, which is the moment someone
has to look at whether the deviation earns its line.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT_ROOT = REPO_ROOT / "godot"

SSOT_TRES = GODOT_ROOT / "theme" / "base_theme.tres"
PROJECT_GODOT = GODOT_ROOT / "project.godot"

SCENE_RE = re.compile(r"^theme_override_font_sizes/([A-Za-z_]+) *= *(\d+)", re.M)
RUNTIME_RE = re.compile(r"add_theme_font_size_override\(\s*\"([a-z_]+)\"\s*,\s*(\d+)\s*\)")
# Every call, literal size or not. A call whose size is an EXPRESSION (e.g. one
# routed through ThemeManager.get_font_size()) is not a raw override at all -- it
# is a use of the scale -- so the derived count is this total minus the literal
# matches above, rather than a second pattern that would have to stay in step
# with the first.
RUNTIME_ANY_RE = re.compile(r"add_theme_font_size_override\(")

# The one-way valve. Lower these when the count falls; never raise them.
CEILING_SCENE = 125
CEILING_RUNTIME_LITERAL = 155


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def ssot_value() -> int | None:
    """The one number, read from the resource rather than restated here."""
    if not SSOT_TRES.exists():
        return None
    m = re.search(r"^default_font_size *= *(\d+)", read(SSOT_TRES), re.M)
    return int(m.group(1)) if m else None


def ssot_is_wired() -> bool:
    if not PROJECT_GODOT.exists():
        return False
    return "theme/custom=" in read(PROJECT_GODOT) and "base_theme.tres" in read(PROJECT_GODOT)


def census() -> dict:
    scene_sites: list[tuple[str, int, int]] = []
    for path in sorted(GODOT_ROOT.joinpath("scenes").rglob("*.tscn")):
        text = read(path)
        rel = str(path.relative_to(REPO_ROOT))
        for m in SCENE_RE.finditer(text):
            line = text[: m.start()].count("\n") + 1
            scene_sites.append((rel, line, int(m.group(2))))

    runtime_sites: list[tuple[str, int, int]] = []
    total_calls = 0
    for sub in ("scripts", "autoload"):
        for path in sorted(GODOT_ROOT.joinpath(sub).rglob("*.gd")):
            if "addons" in path.parts:
                continue
            text = read(path)
            rel = str(path.relative_to(REPO_ROOT))
            for m in RUNTIME_RE.finditer(text):
                line = text[: m.start()].count("\n") + 1
                runtime_sites.append((rel, line, int(m.group(2))))
            total_calls += len(RUNTIME_ANY_RE.findall(text))

    return {
        "scene": scene_sites,
        "runtime": runtime_sites,
        "derived": total_calls - len(runtime_sites),
    }


def histogram(sites: list[tuple[str, int, int]]) -> str:
    counts = Counter(size for _, _, size in sites)
    return "  ".join("%dpx x%d" % (size, n) for size, n in sorted(counts.items()))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", action="store_true", help="census only; never fails")
    ap.add_argument("--by-file", action="store_true", help="list counts per file")
    ap.add_argument("files", nargs="*", help="ignored; pre-commit passes changed files")
    args = ap.parse_args(argv)

    base = ssot_value()
    if base is None:
        print("ERROR: no default_font_size in %s." % SSOT_TRES.relative_to(REPO_ROOT))
        print("       That file IS the lever. Without it there is nothing to turn.")
        return 1
    if not ssot_is_wired():
        print("ERROR: godot/project.godot does not register the SSOT as gui/theme/custom.")
        print("       The resource exists but sits outside Godot's lookup chain, so it")
        print('       reaches nothing. Expected: theme/custom="res://theme/base_theme.tres"')
        return 1

    data = census()
    n_scene = len(data["scene"])
    n_runtime = len(data["runtime"])

    print("Font-size SSOT: %dpx (godot/theme/base_theme.tres, wired as the project theme)" % base)
    print()
    print("Raw overrides the SSOT cannot reach:")
    print("  scenes   %4d  (ceiling %d)   %s" % (n_scene, CEILING_SCENE, histogram(data["scene"])))
    print(
        "  runtime  %4d  (ceiling %d)   %s"
        % (n_runtime, CEILING_RUNTIME_LITERAL, histogram(data["runtime"]))
    )
    print("  total    %4d" % (n_scene + n_runtime))
    print()
    print(
        "  %d runtime call(s) already take their size from an expression rather" % data["derived"]
    )
    print("  than a literal. Driving the numbers above down means turning raw")
    print("  literals into those, or deleting them so the SSOT reaches through.")

    if args.by_file:
        print()
        per = Counter(rel for rel, _, _ in data["scene"] + data["runtime"])
        for rel, n in per.most_common():
            print("  %4d  %s" % (n, rel))

    if args.report:
        return 0

    problems = []
    if n_scene > CEILING_SCENE:
        problems.append(
            "scene overrides rose to %d against a ceiling of %d" % (n_scene, CEILING_SCENE)
        )
    if n_runtime > CEILING_RUNTIME_LITERAL:
        problems.append(
            "runtime overrides rose to %d against a ceiling of %d"
            % (n_runtime, CEILING_RUNTIME_LITERAL)
        )

    if problems:
        print()
        for p in problems:
            print("ERROR: %s" % p)
        print()
        print("The ceiling is a one-way valve, not a quota. A new raw font size is not")
        print("forbidden -- adding one without lowering the ceiling is, because that is")
        print("the moment someone has to say why this text deviates from the one lever.")
        print("Either route it through ThemeManager.get_font_size(), delete it so the")
        print("SSOT reaches through, or lower the ceiling in this file and say why.")
        return 1

    if n_scene < CEILING_SCENE or n_runtime < CEILING_RUNTIME_LITERAL:
        print()
        print("NOTE: the count has fallen below the ceiling. Lower CEILING_SCENE to %d" % n_scene)
        print("      and CEILING_RUNTIME_LITERAL to %d in this file so the" % n_runtime)
        print("      ground gained cannot be given back silently.")

    print()
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
