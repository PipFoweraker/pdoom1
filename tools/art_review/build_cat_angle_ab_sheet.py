"""Build art_generated/cat_angle_ab.html -- the 2026-07-26 cat angle A/B sheet.

Vanguard experiment for issue #900 (per-entity angle cheat: cats one graduation
more side-on). Puts old low-top-down cat frames beside new side-view frames at
1x and 2x on a tiled office-floor strip, with animated walk players.

Ported onto the shared review_style module (tools/art_review/README.md) -- house
header/footer/CRT chrome; the floor-strip comparison layout stays sheet-local.

All images are embedded as base64 data URIs, so the emitted HTML is fully
self-contained and can be opened from any checkout.

Usage:  python tools/art_review/build_cat_angle_ab_sheet.py [--source-root DIR]
        --source-root: checkout whose art_source/ holds the cat frames (default:
        this repo root; useful when the A/B art lives in another worktree).
Output: art_generated/cat_angle_ab.html (gitignored derived output)
"""

import argparse
import base64
import io
import sys
from pathlib import Path

import review_style as rs
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FLOOR_ATLAS = ROOT / "godot" / "assets" / "office_floor" / "tilesets" / "floor_concrete.png"
OUT = ROOT / "art_generated" / "cat_angle_ab.html"

CARDINALS = ["south", "east", "north", "west"]
DIAGONALS = ["south-east", "north-east", "north-west", "south-west"]

SHEET_CSS = """
h4{margin:10px 0 4px;font-weight:normal;color:#9aa;font-size:13px;}
.strip{display:inline-flex;align-items:flex-end;gap:6px;
padding:8px 12px;border:1px solid var(--line);margin:2px 0 10px;border-radius:4px;}
.strip img{image-rendering:pixelated;vertical-align:bottom;}
.cell{text-align:center;}
.cell .lbl{font-size:10px;color:#ccc;font-family:monospace;text-shadow:0 1px 2px #000;}
.pair{display:flex;gap:32px;flex-wrap:wrap;}
"""


def b64(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def floor_tile_b64() -> str:
    """Crop the interior 32x32 tile from the 128x128 Wang atlas."""
    atlas = Image.open(FLOOR_ATLAS)
    tile = atlas.crop((32, 32, 64, 64))
    buf = io.BytesIO()
    tile.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def strip(images: list[tuple[str, str]], scale: int, floor: str, sprite_px: int = 68) -> str:
    """A floor-tiled strip of (label, datauri) sprites at the given scale."""
    tile_px = 32 * scale
    h = sprite_px * scale + 16
    cells = []
    for label, uri in images:
        w = sprite_px * scale
        cells.append(
            f'<div class="cell"><img src="{uri}" width="{w}" height="{sprite_px * scale}" '
            f'alt="{label}"><div class="lbl">{label}</div></div>'
        )
    return (
        f'<div class="strip" style="background-image:url({floor});'
        f'background-size:{tile_px}px {tile_px}px;min-height:{h}px">' + "".join(cells) + "</div>"
    )


def list_js(uris: list[str]) -> str:
    return "[" + ",".join(f'"{u}"' for u in uris) + "]"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", default=str(ROOT), help="checkout root holding art_source/")
    args = ap.parse_args()
    src_root = Path(args.source_root)

    new = src_root / "art_source" / "pixellab_2026-07-26_cat_angle_ab"
    old16 = src_root / "art_source" / "pixellab_2026-07-16"
    old19 = src_root / "art_source" / "pixellab_2026-07-19"

    missing = [p for p in (new, old16, old19, FLOOR_ATLAS) if not p.exists()]
    if missing:
        print("missing inputs: " + ", ".join(str(m) for m in missing))
        return 1

    floor = floor_tile_b64()

    old_cat1 = [(d, b64(old16 / f"15-Cat1-singed-tabby_{d}.png")) for d in CARDINALS]
    new_cat1 = [(d, b64(new / "cat1_tabby_side" / "rotations" / f"{d}.png")) for d in CARDINALS]
    new_cat1_diag = [
        (d, b64(new / "cat1_tabby_side" / "rotations" / f"{d}.png")) for d in DIAGONALS
    ]

    old_black = [
        (d, b64(old19 / "characters" / "cat_black" / "rotations" / f"{d}.png")) for d in CARDINALS
    ]
    new_black = [(d, b64(new / "cat_black_side" / "rotations" / f"{d}.png")) for d in CARDINALS]

    old_walk = {
        d: [b64(old16 / "cat_walk_cat1" / f"walk_{d}_{i}.png") for i in range(9)] for d in CARDINALS
    }
    new_walk = {
        d: [b64(new / "cat1_tabby_side" / "walk" / f"walk_{d}_{i}.png") for i in range(8)]
        for d in CARDINALS
    }

    def walk_player(pid: str, frames: list[str], scale: int) -> str:
        return (
            f'<img id="{pid}" class="player" src="{frames[0]}" width="{68 * scale}" '
            f'height="{68 * scale}">'
        )

    js_frames = []
    players = []
    for d in ["east", "south"]:
        js_frames.append(f'anims["old_{d}"] = {list_js(old_walk[d])};')
        js_frames.append(f'anims["new_{d}"] = {list_js(new_walk[d])};')
        players.append((d, f"old_{d}", f"new_{d}"))

    walk_rows = []
    for d, old_id, new_id in players:
        walk_rows.append(
            f'<div class="pair"><div><h4>old: low top-down ({d})</h4>'
            f'<div class="strip" style="background-image:url({floor});'
            f'background-size:64px 64px;min-height:152px">{walk_player(old_id, old_walk[d], 2)}'
            f"</div></div>"
            f"<div><h4>new: side ({d})</h4>"
            f'<div class="strip" style="background-image:url({floor});'
            f'background-size:64px 64px;min-height:152px">{walk_player(new_id, new_walk[d], 2)}'
            f"</div></div></div>"
        )

    filmstrips = []
    for d in CARDINALS:
        filmstrips.append(f"<h4>old walk {d} (9 frames)</h4>")
        filmstrips.append(strip([(str(i), u) for i, u in enumerate(old_walk[d])], 1, floor))
        filmstrips.append(f"<h4>new walk {d} (8 frames)</h4>")
        filmstrips.append(strip([(str(i), u) for i, u in enumerate(new_walk[d])], 1, floor))

    sec1 = rs.section(
        '1. Cat 1 "singed tabby" rotations -- clean A/B (both 68x68, angle only)',
        f"<h4>old: low top-down (2026-07-16 promoted lineage) -- 1x</h4>{strip(old_cat1, 1, floor)}"
        f"<h4>new: side -- 1x</h4>{strip(new_cat1, 1, floor)}"
        f"<h4>old: low top-down -- 2x</h4>{strip(old_cat1, 2, floor)}"
        f"<h4>new: side -- 2x</h4>{strip(new_cat1, 2, floor)}"
        f"<h4>new: side, diagonals -- 2x</h4>{strip(new_cat1_diag, 2, floor)}",
    )
    sec2 = rs.section(
        "2. Walk cycle -- animated (2x, 8 fps)",
        "".join(walk_rows) + "<h4>Filmstrips (1x)</h4>" + "".join(filmstrips),
    )
    sec3 = rs.section(
        "3. Cat black rotations",
        '<p class="intro warn">NOT one-dial: old still is 92x92 (size-64 batch, 2026-07-19); '
        "new is 68x68 (size 48, walker standard). Judge silhouette and face read, not "
        "on-screen size.</p>"
        f"<h4>old: low top-down (92x92) -- 1x</h4>{strip(old_black, 1, floor, sprite_px=92)}"
        f"<h4>new: side (68x68) -- 1x</h4>{strip(new_black, 1, floor)}"
        f"<h4>old: low top-down -- 2x</h4>{strip(old_black, 2, floor, sprite_px=92)}"
        f"<h4>new: side -- 2x</h4>{strip(new_black, 2, floor)}",
    )

    anim_js = "\n".join(js_frames)
    extra_js = (
        "var anims = {};\n" + anim_js + "\nvar t = 0;\n"
        "setInterval(function () {\n"
        "  t += 1;\n"
        "  for (var id in anims) {\n"
        "    var el = document.getElementById(id);\n"
        "    if (el) el.src = anims[id][t % anims[id].length];\n"
        "  }\n"
        "}, 125);\n"
    )

    intro = (
        "Pip's ruling: cats get main-character fidelity via the per-entity angle cheat -- "
        "one graduation more side-on while humans/scene hold low top-down. API view enum "
        "offers only: high top-down (~35deg), low top-down (~20deg), side (eye-level), "
        "oblique (BETA, broken for characters per 2026-07-16 V6). No intermediate 3/4-side "
        'exists, so "one graduation down" == <b>side</b>. Both new cats: standard mode, '
        "quadruped/cat template, 8 dir, size 48 (68x68 canvas -- matches the promoted "
        "walkers), single color black outline, high detail. 6 generations total. "
        "Floor: interior tile of floor_concrete.png."
    )

    html = rs.page(
        tool_name="cat angle A/B",
        subtitle="low top-down vs side -- issue #900",
        body_html=sec1 + sec2 + sec3,
        badges=[("generations", "6"), ("date", "2026-07-26")],
        intro_html=intro,
        extra_css=SHEET_CSS,
        extra_js=extra_js,
        date="2026-07-26",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    rs.write_ascii(OUT, html)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
