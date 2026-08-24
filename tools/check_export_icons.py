#!/usr/bin/env python3
"""Every export preset's application/icon is a format that platform can decode.

WHY THIS EXISTS (v0.14.3, 2026-08-24)
-------------------------------------
The v0.14.3 release published Windows and Linux and NO macOS asset -- the first
release ever to ship without one. Run 32690368004, job "Build Godot Game (All
Platforms)", printed exactly one line about it:

    ERROR: Project export for preset "macOS" failed.
       at: _fs_changed (editor/editor_node.cpp:1275)

No reason. The cause was one line added the day before: the macOS preset's
`application/icon` was pointed at `res://assets/images/pdoom1.ico`. Godot has no
.ico DECODER -- `Image.load()` on that file returns error 15
(ERR_FILE_UNRECOGNIZED), measured on the same Godot 4.5.1 build CI runs. The
Windows exporter consumes .ico natively, which is why Windows built fine and
only macOS died.

The silence is structural, not a fluke. In `platform/macos/export/export_plugin.cpp`
the icon is loaded with the SAME `err` variable the export-template unzip loop
tests:

    Ref<Image> icon = _load_icon_or_splash_image(icon_path, &err);
    ...
    while (ret == UNZ_OK && err == OK)

so a failed icon load silently ends the loop and the export returns that error
with no message of its own. Godot's own property hints are the authority on what
each platform accepts:

    macOS:   PROPERTY_HINT_FILE, "*.icns,*.png,*.webp,*.svg"
    Windows: PROPERTY_HINT_FILE, "*.ico,*.png,*.webp,*.svg"

(both quoted from get_export_options in Godot 4.5-stable.)

WHY A CHECKER AND NOT JUST THE ONE-LINE FIX
-------------------------------------------
Nothing in this repo exercises a macOS export except the release workflow
itself. `grep -l "export-release" .github/workflows/` returns exactly one file:
enhanced-release.yml. So a preset edit that breaks macOS cannot be caught before
a tag is pushed -- the first measurement is the release. This runs in ~10ms with
no Godot launch, on the same pre-commit trigger as the file it guards.

Usage:
    python tools/check_export_icons.py            # check, exit 1 on any problem
    python tools/check_export_icons.py --list     # print what each preset uses
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PRESETS = REPO_ROOT / "godot" / "export_presets.cfg"
GODOT_DIR = REPO_ROOT / "godot"

# Quoted from get_export_options() in Godot 4.5-stable. An extension outside a
# platform's list is not "discouraged" -- it is a format that platform's
# exporter has no decoder for.
ALLOWED_BY_PLATFORM = {
    "macos": {".icns", ".png", ".webp", ".svg"},
    "windows desktop": {".ico", ".png", ".webp", ".svg"},
    "linux/x11": {".png", ".webp", ".svg"},
}

# Presets whose platform we do not have a hint list for are reported, not
# failed -- a new platform should not fail the build on this checker's
# ignorance. It should make someone add its row above.
_SECTION_RE = re.compile(r"^\[preset\.(\d+)\]\s*$")
_KEY_RE = re.compile(r'^([A-Za-z0-9_/]+)="?(.*?)"?\s*$')


def parse_presets(text: str) -> list[dict]:
    """Return one dict per [preset.N] section (options sections merge into it)."""
    presets: dict[str, dict] = {}
    current: dict | None = None
    for raw in text.splitlines():
        line = raw.strip()
        m = _SECTION_RE.match(line)
        if m:
            current = presets.setdefault(m.group(1), {"index": m.group(1)})
            continue
        if line.startswith("[preset.") and line.endswith(".options]"):
            idx = line[len("[preset.") : -len(".options]")]
            current = presets.setdefault(idx, {"index": idx})
            continue
        if line.startswith("["):
            current = None
            continue
        if current is None or not line or line.startswith(";"):
            continue
        km = _KEY_RE.match(line)
        if km:
            current[km.group(1)] = km.group(2)
    return [presets[k] for k in sorted(presets, key=int)]


def resolve(res_path: str) -> Path | None:
    """res://foo -> <repo>/godot/foo. Returns None for anything not res://."""
    if not res_path.startswith("res://"):
        return None
    return GODOT_DIR / res_path[len("res://") :]


def check(verbose: bool = False) -> int:
    if not PRESETS.is_file():
        print(f"[FAIL] not found: {PRESETS}")
        return 1

    presets = parse_presets(PRESETS.read_text(encoding="utf-8"))
    if not presets:
        print(f"[FAIL] no [preset.N] sections parsed out of {PRESETS}")
        return 1

    problems: list[str] = []
    for p in presets:
        name = p.get("name", f"preset.{p['index']}")
        platform = p.get("platform", "")
        icon = p.get("application/icon", "")
        key = platform.strip().lower()
        allowed = ALLOWED_BY_PLATFORM.get(key)

        if verbose:
            print(f"  {name:<16} platform={platform:<16} icon={icon or '(none)'}")

        if not icon:
            # Empty is legal: the exporter falls back to the project icon, and
            # an absent icon has never failed an export here.
            continue

        target = resolve(icon)
        if target is None:
            problems.append(f"{name}: application/icon is not a res:// path: {icon!r}")
            continue
        if not target.is_file():
            problems.append(
                f"{name}: application/icon points at a file that does not "
                f"exist: {icon} (looked for {target})"
            )
            continue

        ext = target.suffix.lower()
        if allowed is None:
            print(
                f"[WARN] {name}: platform {platform!r} has no allowed-extension "
                f"list in this checker; icon {icon} not verified. Add its row "
                f"to ALLOWED_BY_PLATFORM."
            )
            continue
        if ext not in allowed:
            problems.append(
                f"{name}: platform {platform!r} cannot decode {ext} -- "
                f"{icon}. Godot accepts {', '.join(sorted(allowed))} here. "
                f"This is what emptied the macOS asset from v0.14.3: the "
                f"export aborts with no message naming the icon."
            )

    if problems:
        print("[FAIL] export preset icons Godot cannot decode:")
        for problem in problems:
            print(f"  - {problem}")
        print()
        print("Fix the preset in godot/export_presets.cfg, or convert the icon.")
        return 1

    print(
        f"[OK] {len(presets)} export presets: every application/icon exists "
        f"and is a format its platform can decode."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--list",
        action="store_true",
        help="print each preset's platform and icon before the verdict",
    )
    # pre-commit passes the changed filenames; this checker always reads the
    # one file it guards, so they are accepted and ignored.
    ap.add_argument("files", nargs="*", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    return check(verbose=args.list)


if __name__ == "__main__":
    sys.exit(main())
