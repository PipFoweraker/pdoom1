#!/usr/bin/env python3
"""gen_size_probe_sheet -- character size vanguard probe sheet (2026-07-26).

Feeds Pip's sprite-scale vs accessory-richness decision: the SAME worker
character (beanie + glasses + lanyard/ID badge as the richness test) generated
at pixellab size 32 / 48 / 64, shown on a 64px-tile floor strip at the display
multiples that land the subject at ~1.5-2.25 tiles tall:

    size-48 @ 2x -> 96px subject  -> 1.50 tiles   (current house standard)
    size-48 @ 3x -> 144px subject -> 2.25 tiles
    size-64 @ 2x -> 128px subject -> 2.00 tiles
    size-32 @ 4x -> 128px subject -> 2.00 tiles   (ladder bottom rung upscaled)

"tiles tall" = subject px * multiple / 64 (the tile art stays at face value;
only the sprite multiple varies -- the framing Pip asked to compare at).

Images are embedded as base64 data URIs so the single HTML file survives being
copied to the main checkout before the art itself lands there. Builds on
tools/art_review/review_style.py (house style). Stdlib only; ASCII only.

Usage:  python tools/art_review/gen_size_probe_sheet.py
Input:  art_source/pixellab_2026-07-26_size_probe/size_{32,48,64}/rotations/*.png
Output: art_generated/size_probe_sheet.html
"""

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import review_style as rs  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "art_source" / "pixellab_2026-07-26_size_probe"
OUT = ROOT / "art_generated" / "size_probe_sheet.html"

DIRS = [
    "south",
    "south-east",
    "east",
    "north-east",
    "north",
    "north-west",
    "west",
    "south-west",
]

TILE = 64  # px, floor tile face value

# (subject_px, canvas_px, display_multiple) rows, in Pip's comparison order.
ROWS = [
    (48, 68, 2, "current house standard at its floor multiple"),
    (48, 68, 3, "house standard pushed one multiple up"),
    (64, 92, 2, "bigger canvas candidate -- more accessory pixels"),
    (32, 48, 4, "ladder bottom rung, heavily upscaled"),
]


def data_uri(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def tile_strip(subject: int, canvas: int, mult: int, note: str) -> str:
    """One floor strip: 64px-tile grid ground, 8 directions bottom-aligned."""
    rot_dir = SRC / f"size_{subject}" / "rotations"
    tiles = subject * mult / TILE
    disp_canvas = canvas * mult
    disp_subject = subject * mult
    imgs = []
    for d in DIRS:
        p = rot_dir / f"{d}.png"
        if not p.exists():
            imgs.append(
                f'<div class="probe-missing" style="width:{disp_canvas}px;'
                f'height:{disp_canvas}px">missing<br>{rs.esc(d)}</div>'
            )
            continue
        imgs.append(
            f'<img src="{data_uri(p)}" width="{disp_canvas}" height="{disp_canvas}" '
            f'alt="{rs.esc(d)}" title="{rs.esc(d)}">'
        )
    label = (
        f"{subject}px subject / {mult}x display / {tiles:.2f} tiles tall "
        f"({disp_subject}px on 64px tiles)"
    )
    return (
        f'<div class="probe-row">'
        f'<div class="probe-label mono">{rs.esc(label)}'
        f'<span class="probe-note"> -- {rs.esc(note)}; canvas {canvas}px shown at '
        f"{disp_canvas}px</span></div>"
        f'<div class="probe-strip" style="height:{max(disp_canvas + 24, TILE * 3)}px">'
        + "".join(imgs)
        + "</div></div>"
    )


EXTRA_CSS = """
.probe-row{margin:16px 0 22px;}
.probe-label{color:var(--amber2);font-size:13px;margin-bottom:6px;}
.probe-note{color:var(--dim);font-size:11px;}
.probe-strip{display:flex;align-items:flex-end;gap:12px;padding:0 12px;
overflow-x:auto;border:1px solid var(--line);border-radius:6px;
background:
 repeating-linear-gradient(0deg,transparent 0 63px,#3a332a 63px 64px),
 repeating-linear-gradient(90deg,transparent 0 63px,#3a332a 63px 64px),
 repeating-conic-gradient(#241f18 0% 25%,#2b251c 0% 50%) 0 0/128px 128px;}
.probe-strip img{image-rendering:pixelated;display:block;}
.probe-missing{display:flex;align-items:center;justify-content:center;
color:#e0a0a0;border:1px dashed #cc5a4a;font-family:monospace;font-size:10px;
text-align:center;}
"""


def main() -> int:
    rows_html = "".join(tile_strip(*row) for row in ROWS)
    body = rs.section(
        "size ladder on a 64px-tile floor strip",
        rows_html,
        count=f"{len(ROWS)} configurations x 8 directions",
    )
    intro = (
        "Same worker description at every size (beanie + glasses + lanyard/ID "
        "badge = the accessory-richness test); pixellab standard mode, low "
        "top-down, 8-dir stills. Only the generation size and display multiple "
        'change. "tiles tall" = subject px * multiple / 64. Grid lines are the '
        "64px tile faces. Source art: art_source/pixellab_2026-07-26_size_probe/ "
        "(MANIFEST.md has ids + gen cost)."
    )
    html_text = rs.page(
        "size probe",
        "sprite scale vs accessory richness -- 2026-07-26",
        body,
        badges=[("sizes", "32/48/64"), ("mode", "standard 8-dir stills")],
        intro_html=intro,
        extra_css=EXTRA_CSS,
        footer_note="Data-only probe: nothing is wired into godot/.",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rs.write_ascii(OUT, html_text)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
