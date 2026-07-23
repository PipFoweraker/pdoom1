#!/usr/bin/env python3
"""Stamp the canonical game version into every place that cannot self-read it.

``version.txt`` at the repo root is THE single source of truth for the game
version (Pip's decision). Runtime GDScript reads it through
``GameConfig.CURRENT_VERSION``, but several build/config/scene files hold a
*copy* of the version that Godot cannot resolve at run time (export paths,
Windows/macOS metadata, the welcome-screen fallback label, the project config).
This script is the "metadata overrides hard values" mechanism: bump
``version.txt``, run ``python tools/sync_version.py``, and every derived copy
follows.

Targets stamped from ``version.txt``:
  * ``godot/autoload/game_config.gd``  -- ``const CURRENT_VERSION``
  * ``godot/project.godot``            -- ``config/version`` (inserted if absent)
  * ``godot/export_presets.cfg``       -- the three ``export_path`` ``/vX/``
                                          segments plus ``application/version``,
                                          ``application/short_version`` and the
                                          four-part ``file_version`` /
                                          ``product_version`` (``X.0``)
  * ``godot/scenes/welcome.tscn``      -- the ``Version`` label static fallback

Second SSOT (build-vs-ladder split, docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md):
``ladder_version.txt`` at the repo root holds the ladder EPOCH -- a bare integer
that bumps ONLY on gameplay/scoring/seed/RNG rule changes. It is stamped into
``godot/autoload/game_config.gd`` ``const LADDER_VERSION`` exactly like
``CURRENT_VERSION``. The leaderboard board-key now derives from the LADDER value
(``GameConfig.get_board_version()``), not the build version, so cosmetic build
bumps no longer fork score boards.

Usage::

    python tools/sync_version.py           # stamp everything (idempotent)
    python tools/sync_version.py --check    # exit 1 if anything is out of sync

The ``--check`` mode writes nothing and is safe to gate CI on: it fails loudly
if any derived copy has drifted from ``version.txt`` / ``ladder_version.txt`` so
they can never silently disagree (the leaderboard board-key derives from the
ladder version, so a silent drift would fork score boards).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_ROOT / "version.txt"
LADDER_FILE = REPO_ROOT / "ladder_version.txt"

GAME_CONFIG = REPO_ROOT / "godot" / "autoload" / "game_config.gd"
PROJECT_GODOT = REPO_ROOT / "godot" / "project.godot"
EXPORT_PRESETS = REPO_ROOT / "godot" / "export_presets.cfg"
WELCOME_SCENE = REPO_ROOT / "godot" / "scenes" / "welcome.tscn"

# Accept MAJOR.MINOR.PATCH with an optional pre-release/build suffix (e.g.
# 0.11.0 or 0.11.0-alpha). The numeric core is what the four-part Windows
# metadata needs.
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+")


def read_version() -> str:
    """Return the canonical version string (trimmed) from version.txt."""
    ver = VERSION_FILE.read_text(encoding="ascii").strip()
    if not ver:
        raise SystemExit(f"[sync_version] {VERSION_FILE} is empty")
    if not _SEMVER_RE.match(ver):
        raise SystemExit(f"[sync_version] {VERSION_FILE} value {ver!r} is not MAJOR.MINOR.PATCH")
    return ver


def read_ladder_version() -> str:
    """Return the canonical ladder epoch (a bare positive integer, as a string).

    ``ladder_version.txt`` is the SSOT for the leaderboard epoch (build-vs-ladder
    split). It bumps only on gameplay/scoring/seed/RNG rule changes -- see the
    spec's Section 3 checklist and ``tools/check_ladder_bump.py``.
    """
    ladder = LADDER_FILE.read_text(encoding="ascii").strip()
    if not ladder:
        raise SystemExit(f"[sync_version] {LADDER_FILE} is empty")
    if not re.fullmatch(r"[1-9]\d*", ladder):
        raise SystemExit(
            f"[sync_version] {LADDER_FILE} value {ladder!r} is not a bare positive integer"
        )
    return ladder


def _numeric_core(ver: str) -> str:
    """Just the leading MAJOR.MINOR.PATCH, dropping any pre-release suffix."""
    return _SEMVER_RE.match(ver).group(0)


def _four_part(ver: str) -> str:
    """Windows file/product version wants a four-part numeric quad."""
    return _numeric_core(ver) + ".0"


def _stamp_game_config(text: str, ver: str, ladder: str) -> str:
    text = re.sub(
        r'(const CURRENT_VERSION: String = ")[^"]*(")',
        lambda m: m.group(1) + ver + m.group(2),
        text,
    )
    # Build-vs-ladder split: stamp the ladder epoch const the same way. The const
    # holds the bare integer from ladder_version.txt; GameConfig.get_board_version()
    # renders it as "L<n>" for board keys.
    return re.sub(
        r'(const LADDER_VERSION: String = ")[^"]*(")',
        lambda m: m.group(1) + ladder + m.group(2),
        text,
    )


def _stamp_project_godot(text: str, ver: str, _ladder: str) -> str:
    if re.search(r'(?m)^config/version="', text):
        return re.sub(
            r'(?m)^(config/version=")[^"]*(")',
            lambda m: m.group(1) + ver + m.group(2),
            text,
        )
    # Not present yet: insert it as the first key under [application].
    return re.sub(
        r"(?m)^(\[application\]\n)",
        lambda m: m.group(1) + f'config/version="{ver}"\n',
        text,
        count=1,
    )


def _stamp_export_presets(text: str, ver: str, _ladder: str) -> str:
    quad = _four_part(ver)
    # export_path="../builds/<os>/vX/..." -- replace only the /vX/ segment.
    text = re.sub(
        r'(export_path="[^"]*?/v)[0-9][^/"]*(/)',
        lambda m: m.group(1) + ver + m.group(2),
        text,
    )
    text = re.sub(
        r'(?m)^(application/short_version=")[^"]*(")',
        lambda m: m.group(1) + ver + m.group(2),
        text,
    )
    text = re.sub(
        r'(?m)^(application/version=")[^"]*(")',
        lambda m: m.group(1) + ver + m.group(2),
        text,
    )
    text = re.sub(
        r'(?m)^(application/file_version=")[^"]*(")',
        lambda m: m.group(1) + quad + m.group(2),
        text,
    )
    text = re.sub(
        r'(?m)^(application/product_version=")[^"]*(")',
        lambda m: m.group(1) + quad + m.group(2),
        text,
    )
    return text


def _stamp_welcome_scene(text: str, ver: str, _ladder: str) -> str:
    # The "Version" label static fallback text = "vX.Y.Z". welcome_screen.gd
    # also sets this at run time from GameConfig.CURRENT_VERSION; stamping keeps
    # the committed scene honest for anyone reading it statically.
    return re.sub(
        r'(text = "v)\d+\.\d+\.\d+[^"]*(")',
        lambda m: m.group(1) + ver + m.group(2),
        text,
    )


# (path, stamper) pairs. Each stamper is pure: (text, ver, ladder) -> new_text.
TARGETS = [
    (GAME_CONFIG, _stamp_game_config),
    (PROJECT_GODOT, _stamp_project_godot),
    (EXPORT_PRESETS, _stamp_export_presets),
    (WELCOME_SCENE, _stamp_welcome_scene),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="write nothing; exit 1 if any derived copy is out of sync",
    )
    args = parser.parse_args()

    ver = read_version()
    ladder = read_ladder_version()
    out_of_sync: list[Path] = []
    written: list[Path] = []

    for path, stamper in TARGETS:
        if not path.exists():
            print(f"[sync_version] MISSING target {path}")
            out_of_sync.append(path)
            continue
        current = path.read_text(encoding="utf-8")
        updated = stamper(current, ver, ladder)
        if updated == current:
            continue
        if args.check:
            out_of_sync.append(path)
        else:
            path.write_text(updated, encoding="utf-8", newline="\n")
            written.append(path)

    def rel(p: Path) -> str:
        return p.relative_to(REPO_ROOT).as_posix()

    if args.check:
        if out_of_sync:
            print(
                f"[sync_version] OUT OF SYNC with version.txt={ver} / ladder_version.txt={ladder}:"
            )
            for p in out_of_sync:
                print(f"  - {rel(p)}")
            print("[sync_version] run: python tools/sync_version.py")
            return 1
        print(
            f"[sync_version] all targets in sync with version.txt={ver}, ladder_version.txt={ladder}"
        )
        return 0

    if written:
        print(f"[sync_version] stamped version.txt={ver} + ladder_version.txt={ladder} into:")
        for p in written:
            print(f"  - {rel(p)}")
    else:
        print(f"[sync_version] already in sync with version.txt={ver}, ladder_version.txt={ladder}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
