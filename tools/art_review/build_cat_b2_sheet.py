"""Build art_generated/cat_b2_sheet.html -- the 2026-07-26 cat experiment B sheet.

Follow-up to the cat angle A/B (issue #900). Pip's verdicts drove four probes:
1. HEFT RETRY: side-view walk won but read too lanky -- same tabby regenerated
   with stocky/heavy-mass description language (walk east+west, template mode).
2. N/S CANDIDATES: side-view north/south walks came back BIPEDAL (issue #912).
   Two competing answers: (a) hybrid -- low top-down version of the same tabby
   for N/S only; (b) side-view v3 retry with aggressively quadruped-grounded
   action descriptions.
3. BUTT-FLASH LOOP: occasional-use "away" walk with tail-up rear visibility
   for the splice mechanic (issue #913 -- art only, renderer is another lane).
4. KAWAII PROBE: baby-schema proportions via description (bigger head/eyes,
   rounder body) -- stills only, A/B against standard proportions.

All images embedded as base64 data URIs -- output is fully self-contained.

Usage: python tools/art_review/build_cat_b2_sheet.py
Output: art_generated/cat_b2_sheet.html (gitignored derived output)
"""

import base64
import io
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
B2 = ROOT / "art_source" / "pixellab_2026-07-26_cat_b2"
AB = ROOT / "art_source" / "pixellab_2026-07-26_cat_angle_ab"
OLD16 = ROOT / "art_source" / "pixellab_2026-07-16"
FLOOR_ATLAS = ROOT / "godot" / "assets" / "office_floor" / "tilesets" / "floor_concrete.png"
OUT = ROOT / "art_generated" / "cat_b2_sheet.html"

CARDINALS = ["south", "east", "north", "west"]


def b64(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def frames(folder: Path, stem: str) -> list[str]:
    """All frames matching stem_N.png in order, as data URIs."""
    paths = sorted(folder.glob(f"{stem}_*.png"), key=lambda p: int(p.stem.rsplit("_", 1)[1]))
    if not paths:
        raise FileNotFoundError(f"no frames {folder}/{stem}_*.png")
    return [b64(p) for p in paths]


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
    missing = [p for p in (B2, AB, OLD16, FLOOR_ATLAS) if not p.exists()]
    if missing:
        print("missing inputs: " + ", ".join(str(m) for m in missing))
        return 1

    floor = floor_tile_b64()

    # --- stills -------------------------------------------------------------
    old16_stills = [(d, b64(OLD16 / f"15-Cat1-singed-tabby_{d}.png")) for d in CARDINALS]
    ab_side = [(d, b64(AB / "cat1_tabby_side" / "rotations" / f"{d}.png")) for d in CARDINALS]
    heft_side = [(d, b64(B2 / "tabby_side_heft" / "rotations" / f"{d}.png")) for d in CARDINALS]
    lowtd_heft = [(d, b64(B2 / "tabby_lowtd_heft" / "rotations" / f"{d}.png")) for d in CARDINALS]
    kawaii = [(d, b64(B2 / "tabby_side_kawaii" / "rotations" / f"{d}.png")) for d in CARDINALS]

    # --- walk cycles --------------------------------------------------------
    anims: dict[str, list[str]] = {}
    # references
    for d in CARDINALS:
        anims[f"old16_{d}"] = frames(OLD16 / "cat_walk_cat1", f"walk_{d}")
        anims[f"ab_side_{d}"] = frames(AB / "cat1_tabby_side" / "walk", f"walk_{d}")
    # new clips
    for d in ("east", "west"):
        anims[f"heft_{d}"] = frames(B2 / "tabby_side_heft" / "walk_ew", f"walk_{d}")
    for d in ("north", "south"):
        anims[f"lowtd_{d}"] = frames(B2 / "tabby_lowtd_heft" / "walk_ns", f"walk_{d}")
        anims[f"side_v3_{d}"] = frames(B2 / "tabby_side_heft" / "walk_ns_v3", f"walk_{d}")
    anims["butt_north"] = frames(B2 / "tabby_lowtd_heft" / "butt_flash", "butt_flash_north")

    player_bindings: list[tuple[str, str]] = []  # (element_id, anim_key)

    def player(key: str, scale: int = 2) -> str:
        px = 68 * scale
        eid = f"p{len(player_bindings)}_{key}"
        player_bindings.append((eid, key))
        return (
            f'<div class="cell"><div class="strip" style="background-image:url({floor});'
            f'background-size:{32 * scale}px {32 * scale}px;min-height:{px + 16}px">'
            f'<img id="{eid}" class="player" src="{anims[key][0]}" width="{px}" '
            f'height="{px}"></div><div class="lbl">{key}</div></div>'
        )

    def player_row(keys: list[str]) -> str:
        return '<div class="pair">' + "".join(player(k) for k in keys) + "</div>"

    def filmstrip(pid: str) -> str:
        cells = [(str(i), u) for i, u in enumerate(anims[pid])]
        return f"<h4>{pid} ({len(cells)} frames, 1x)</h4>" + strip(cells, 1, floor)

    html = HTML_TEMPLATE.format(
        old16_2x=strip(old16_stills, 2, floor),
        ab_side_2x=strip(ab_side, 2, floor),
        heft_side_2x=strip(heft_side, 2, floor),
        lowtd_heft_2x=strip(lowtd_heft, 2, floor),
        kawaii_2x=strip(kawaii, 2, floor),
        kawaii_1x=strip(kawaii, 1, floor),
        heft_side_1x=strip(heft_side, 1, floor),
        ab_side_1x=strip(ab_side, 1, floor),
        heft_walk_row=player_row(["old16_east", "ab_side_east", "heft_east"])
        + player_row(["old16_west", "ab_side_west", "heft_west"]),
        ns_north_row=player_row(["old16_north", "ab_side_north", "lowtd_north", "side_v3_north"]),
        ns_south_row=player_row(["old16_south", "ab_side_south", "lowtd_south", "side_v3_south"]),
        butt_row=player_row(["lowtd_north", "butt_north"]),
        filmstrips="".join(
            filmstrip(p)
            for p in (
                "heft_east",
                "heft_west",
                "lowtd_north",
                "lowtd_south",
                "side_v3_north",
                "side_v3_south",
                "butt_north",
            )
        ),
        anim_js="\n".join(f'anims["{k}"] = {list_js(v)};' for k, v in anims.items())
        + "\nvar bindings = "
        + "["
        + ",".join(f'["{eid}","{key}"]' for eid, key in player_bindings)
        + "];",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")
    return 0


HTML_TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8"><title>Cat experiment B -- 2026-07-26 (issues #900 #912 #913)</title>
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
.pair {{ display: flex; gap: 24px; flex-wrap: wrap; align-items: flex-end; }}
</style></head><body>
<h1>Cat experiment B -- heft retry, N/S answers, butt-flash, kawaii probe</h1>
<p class="note">2026-07-26 follow-up to the angle A/B (issue #900). Verdict inputs:
side E/W won but was too lanky; side N/S was bipedal horror (issue #912);
Pip wants a tail-up "away" splice loop (issue #913); plus a baby-schema
proportion probe. All new cats: standard mode, quadruped/cat template, size 48
(68x68), 8 dir, single color black outline, high detail. Naming: old16 = the
promoted 2026-07-16 low-top-down walker; ab_side = the 2026-07-26 A/B side cat
(lanky); heft = new stocky side cat; lowtd = new stocky low-top-down cat.
Animations at 8 fps; floor is the interior tile of floor_concrete.png.</p>

<h2>1. Heft retry -- side rotations (2x)</h2>
<h4>old16: low top-down promoted stills</h4>
{old16_2x}
<h4>ab_side: first side-view attempt (the "lanky" one)</h4>
{ab_side_2x}
<h4>heft: retry with stocky / solid-body-mass / weighty language</h4>
{heft_side_2x}

<h2>2. Heft retry -- E/W walk players (2x, animated)</h2>
<p class="note">Left to right: original low-top-down walker, lanky A/B side
walker, new heft side walker. Judge body mass through the gait.</p>
{heft_walk_row}

<h2>3. N/S candidates -- the bipedal-horror fix (2x, animated)</h2>
<p class="note">Per direction, left to right: old16 low-top-down reference;
ab_side = the REJECTED bipedal side walk (issue #912, kept for comparison);
lowtd = candidate (a), hybrid per-direction views (new stocky low-top-down cat,
template walk); side_v3 = candidate (b), side view retried once with
aggressively quadruped-grounded v3 descriptions ("all four paws on the
ground... seen from behind at eye level").</p>
<h4>north (away from viewer)</h4>
{ns_north_row}
<h4>south (toward viewer)</h4>
{ns_south_row}

<h2>4. Butt-flash splice loop (issue #913) -- 2x, animated</h2>
<p class="note">Occasional-use alternate "away" loop: tail held high, rear
visible -- to be spliced into the normal north walk by the renderer (not this
lane). Left: normal lowtd north walk. Right: butt-flash variant (v3,
low top-down).</p>
{butt_row}

<h2>5. Kawaii probe -- baby-schema proportions (stills only)</h2>
<p class="note">Same tabby, side view, description-dialed baby schema:
oversized round head, huge eyes, chubby rounded body, stubby legs. Proportion
params are humanoid-only in the API, so the dial is description language.
Compare against the heft cat (adult proportions) and the lanky A/B cat.</p>
<h4>kawaii -- 2x</h4>
{kawaii_2x}
<h4>heft (adult) -- 2x</h4>
{heft_side_2x}
<h4>kawaii vs heft vs ab_side -- 1x (in-game scale)</h4>
{kawaii_1x}
{heft_side_1x}
{ab_side_1x}

<h2>6. Filmstrips (1x)</h2>
{filmstrips}

<script>
var anims = {{}};
{anim_js}
var t = 0;
setInterval(function () {{
  t += 1;
  for (var i = 0; i < bindings.length; i++) {{
    var el = document.getElementById(bindings[i][0]);
    var fr = anims[bindings[i][1]];
    if (el && fr) el.src = fr[t % fr.length];
  }}
}}, 125);
</script>
</body></html>
"""

if __name__ == "__main__":
    sys.exit(main())
