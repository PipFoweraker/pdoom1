"""Build art_generated/cat_angle_ab.html -- the 2026-07-26 cat angle A/B sheet.

Vanguard experiment for issue #900 (per-entity angle cheat: cats one graduation
more side-on). Puts old low-top-down cat frames beside new side-view frames at
1x and 2x on a tiled office-floor strip, with animated walk players.

All images are embedded as base64 data URIs, so the emitted HTML is fully
self-contained and can be opened from any checkout.

Usage: python tools/art_review/build_cat_angle_ab_sheet.py
Output: art_generated/cat_angle_ab.html (gitignored derived output)
"""

import base64
import io
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
NEW = ROOT / "art_source" / "pixellab_2026-07-26_cat_angle_ab"
OLD16 = ROOT / "art_source" / "pixellab_2026-07-16"
OLD19 = ROOT / "art_source" / "pixellab_2026-07-19"
FLOOR_ATLAS = ROOT / "godot" / "assets" / "office_floor" / "tilesets" / "floor_concrete.png"
OUT = ROOT / "art_generated" / "cat_angle_ab.html"

CARDINALS = ["south", "east", "north", "west"]
DIAGONALS = ["south-east", "north-east", "north-west", "south-west"]


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


def main() -> int:
    missing = [p for p in (NEW, OLD16, OLD19, FLOOR_ATLAS) if not p.exists()]
    if missing:
        print("missing inputs: " + ", ".join(str(m) for m in missing))
        return 1

    floor = floor_tile_b64()

    old_cat1 = [(d, b64(OLD16 / f"15-Cat1-singed-tabby_{d}.png")) for d in CARDINALS]
    new_cat1 = [(d, b64(NEW / "cat1_tabby_side" / "rotations" / f"{d}.png")) for d in CARDINALS]
    new_cat1_diag = [
        (d, b64(NEW / "cat1_tabby_side" / "rotations" / f"{d}.png")) for d in DIAGONALS
    ]

    old_black = [
        (d, b64(OLD19 / "characters" / "cat_black" / "rotations" / f"{d}.png")) for d in CARDINALS
    ]
    new_black = [(d, b64(NEW / "cat_black_side" / "rotations" / f"{d}.png")) for d in CARDINALS]

    old_walk = {
        d: [b64(OLD16 / "cat_walk_cat1" / f"walk_{d}_{i}.png") for i in range(9)] for d in CARDINALS
    }
    new_walk = {
        d: [b64(NEW / "cat1_tabby_side" / "walk" / f"walk_{d}_{i}.png") for i in range(8)]
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
            '<div class="pair"><div><h4>old: low top-down ({d})</h4>'
            '<div class="strip" style="background-image:url({floor});'
            'background-size:64px 64px;min-height:152px">{old}</div></div>'
            "<div><h4>new: side ({d})</h4>"
            '<div class="strip" style="background-image:url({floor});'
            'background-size:64px 64px;min-height:152px">{new}</div></div></div>'.format(
                d=d,
                floor=floor,
                old=walk_player(old_id, old_walk[d], 2),
                new=walk_player(new_id, new_walk[d], 2),
            )
        )

    filmstrips = []
    for d in CARDINALS:
        filmstrips.append(f"<h4>old walk {d} (9 frames)</h4>")
        filmstrips.append(strip([(str(i), u) for i, u in enumerate(old_walk[d])], 1, floor))
        filmstrips.append(f"<h4>new walk {d} (8 frames)</h4>")
        filmstrips.append(strip([(str(i), u) for i, u in enumerate(new_walk[d])], 1, floor))

    html = HTML_TEMPLATE.format(
        old_cat1_1x=strip(old_cat1, 1, floor),
        new_cat1_1x=strip(new_cat1, 1, floor),
        old_cat1_2x=strip(old_cat1, 2, floor),
        new_cat1_2x=strip(new_cat1, 2, floor),
        new_cat1_diag_2x=strip(new_cat1_diag, 2, floor),
        old_black_1x=strip(old_black, 1, floor, sprite_px=92),
        new_black_1x=strip(new_black, 1, floor),
        old_black_2x=strip(old_black, 2, floor, sprite_px=92),
        new_black_2x=strip(new_black, 2, floor),
        walk_players="".join(walk_rows),
        filmstrips="".join(filmstrips),
        anim_js="\n".join(js_frames),
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")
    return 0


def list_js(uris: list[str]) -> str:
    return "[" + ",".join(f'"{u}"' for u in uris) + "]"


HTML_TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8"><title>Cat angle A/B -- 2026-07-26 (issue #900)</title>
<style>
body {{ background: #1b1d22; color: #d8d4c8; font-family: Consolas, monospace;
       margin: 24px; }}
h1 {{ font-size: 20px; }} h2 {{ font-size: 16px; margin-top: 36px;
     border-bottom: 1px solid #444; padding-bottom: 4px; }}
h4 {{ margin: 10px 0 4px; font-weight: normal; color: #9aa; }}
img {{ image-rendering: pixelated; vertical-align: bottom; }}
.note {{ color: #8a8; max-width: 72em; }}
.warn {{ color: #ca5; }}
.strip {{ display: inline-flex; align-items: flex-end; gap: 6px;
          padding: 8px 12px; border: 1px solid #333; margin: 2px 0 10px; }}
.cell {{ text-align: center; }}
.cell .lbl {{ font-size: 10px; color: #ccc; text-shadow: 0 1px 2px #000; }}
.pair {{ display: flex; gap: 32px; flex-wrap: wrap; }}
</style></head><body>
<h1>Cat angle A/B -- low top-down vs side (2026-07-26, issue #900)</h1>
<p class="note">Pip's ruling: cats get main-character fidelity via the per-entity
angle cheat -- one graduation more side-on while humans/scene hold low top-down.
API view enum offers only: high top-down (~35deg), low top-down (~20deg), side
(eye-level), oblique (BETA, broken for characters per 2026-07-16 V6). No
intermediate 3/4-side exists, so "one graduation down" == <b>side</b>.
Both new cats: standard mode, quadruped/cat template, 8 dir, size 48 (68x68
canvas -- matches the promoted walkers), single color black outline, high
detail. 6 generations total. Floor: interior tile of floor_concrete.png.</p>

<h2>1. Cat 1 "singed tabby" rotations -- clean A/B (both 68x68, angle only)</h2>
<h4>old: low top-down (2026-07-16 promoted lineage) -- 1x</h4>
{old_cat1_1x}
<h4>new: side -- 1x</h4>
{new_cat1_1x}
<h4>old: low top-down -- 2x</h4>
{old_cat1_2x}
<h4>new: side -- 2x</h4>
{new_cat1_2x}
<h4>new: side, diagonals -- 2x</h4>
{new_cat1_diag_2x}

<h2>2. Walk cycle -- animated (2x, 8 fps)</h2>
{walk_players}
<h3>Filmstrips (1x)</h3>
{filmstrips}

<h2>3. Cat black rotations</h2>
<p class="note warn">NOT one-dial: old still is 92x92 (size-64 batch,
2026-07-19); new is 68x68 (size 48, walker standard). Judge silhouette and
face read, not on-screen size.</p>
<h4>old: low top-down (92x92) -- 1x</h4>
{old_black_1x}
<h4>new: side (68x68) -- 1x</h4>
{new_black_1x}
<h4>old: low top-down -- 2x</h4>
{old_black_2x}
<h4>new: side -- 2x</h4>
{new_black_2x}

<script>
var anims = {{}};
{anim_js}
var t = 0;
setInterval(function () {{
  t += 1;
  for (var id in anims) {{
    var el = document.getElementById(id);
    if (el) el.src = anims[id][t % anims[id].length];
  }}
}}, 125);
</script>
</body></html>
"""

if __name__ == "__main__":
    sys.exit(main())
