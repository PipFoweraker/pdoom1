#!/usr/bin/env python3
"""gen_prop_grain_sheet -- prop NATIVE-GRAIN vanguard comparison sheet (issue #900/#925).

Question the sheet answers: should office props be re-generated at native pixel
grain (small canvases, chunky 2x pixels matching the 32px-art floor) instead of
reusing the current larger-canvas art (fine grain; smooth mush when downscaled
to realistic proportions)?

For each vanguard prop the sheet shows, on a real floor-tile strip with the
in-game 2-tile (128 screen px) worker silhouette for scale:

  (a) CURRENT art at manifest scale (height_tiles x 64 screen px -- how the
      game renders it today; the trio is 3.25-3.5 tiles tall vs a 2-tile human);
  (a2) CURRENT art naively downscaled to realistic proportion (the zero-cost
      alternative to a re-base -- shows the smooth grain-mush this produces);
  (b) NATIVE-GRAIN candidates generated at true-proportion art sizes, shown at
      the world's 2x (1 art px = 2 screen px, same grain as the floor);
  (c) a combined side-by-side strip -- current vs native vs worker, unmissable.

Inputs (repo-relative; run from anywhere):
  godot/data/office/props_manifest.json
  godot/assets/office_floor/props/*.png                (current in-game art)
  godot/assets/office_floor/tilesets/floor_concrete.png (base tile @ 64,32,32,32)
  godot/assets/office_floor/artloop_char/idle_0.png    (worker -> silhouette)
  art_source/pixellab_2026-07-26_prop_grain_vanguard/{native,manifest_scale,dial}/*.png

Output: art_generated/prop_grain_vanguard_sheet.html (self-contained, data URIs).
Requires Pillow. ASCII only (issue #744).
"""

import base64
import io
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_style as rs  # noqa: E402  (needs the sys.path insert above)

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "art_source" / "pixellab_2026-07-26_prop_grain_vanguard"
OUT = ROOT / "art_generated" / "prop_grain_vanguard_sheet.html"

TILE_SCREEN = 64  # one floor tile on screen (32px art x2)
WORKER_SCREEN_H = 128  # CHAR_TARGET_H in employee_sprite.gd (2 tiles)
BASELINE_PAD = 34  # floor px left below the feet line in strips

# Vanguard set. true_tiles = realistic height relative to the 2-tile (~1.8m)
# worker; the proposed re-base proportion (Pip to rule -- manifest heights are
# all flagged review:true).
PROPS = [
    {
        "id": "water_cooler",
        "label": "water cooler",
        "true_tiles": 1.3,
        "real_world": "~1.2m incl bottle",
    },
    {
        "id": "filing_cabinet",
        "label": "filing cabinet",
        "true_tiles": 1.45,
        "real_world": "~1.3m four-drawer",
    },
    {
        "id": "server_cluster",
        "label": "server cluster",
        "true_tiles": 2.2,
        "real_world": "~2.0m racks",
    },
    {
        "id": "desk",
        "label": "desk (gap-fill)",
        "true_tiles": 1.35,
        "real_world": "~0.75m desk + monitor",
    },
    {
        "id": "door",
        "label": "door (gap-fill)",
        "true_tiles": 2.25,
        "real_world": "~2.0m door + frame",
    },
]

PROMPTS = {
    "water_cooler": "office water cooler, blue water bottle on top, dispenser taps, "
    "heavy black outline, deep shadow beneath, straight-on centered symmetrical "
    "view-locked, warm-grime lived-in office, muted teal-olive-slate palette, "
    "warm amber accent only",
    "filing_cabinet": "tall metal office filing cabinet, four drawers with label plates "
    "and handles, [house style suffix as above]",
    "server_cluster": "row of three dark server racks, glowing amber status lights, "
    "cable bundles, powered screens glowing, [house style suffix]",
    "desk": "office desk with glowing computer monitor, keyboard, tidy paper tray, "
    "[house style suffix]",
    "door": "closed office door in door frame, small rectangular window pane, metal "
    "handle, [house style suffix]",
}


def data_uri(im):
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def subject_bbox(im):
    return im.getchannel("A").getbbox()


def crop_subject(im):
    return im.crop(subject_bbox(im))


def load_floor_tile():
    atlas = Image.open(
        ROOT / "godot" / "assets" / "office_floor" / "tilesets" / "floor_concrete.png"
    ).convert("RGBA")
    tile = atlas.crop((64, 32, 96, 64))  # FLOOR_BASE_REGION in office_floor.gd
    return tile.resize((TILE_SCREEN, TILE_SCREEN), Image.NEAREST)


def load_worker_silhouette():
    """In-game worker (artloop idle_0) as a dark silhouette at its real render
    height: 128 screen px (CHAR_TARGET_H). Subject is ~122 art px, i.e. the
    worker renders near 1:1 -- honest context for the grain comparison."""
    src = Image.open(
        ROOT / "godot" / "assets" / "office_floor" / "artloop_char" / "idle_0.png"
    ).convert("RGBA")
    sub = crop_subject(src)
    s = WORKER_SCREEN_H / sub.height
    sub = sub.resize((max(1, round(sub.width * s)), WORKER_SCREEN_H), Image.LANCZOS)
    sil = Image.new("RGBA", sub.size, (0, 0, 0, 0))
    px = sub.load()
    sp = sil.load()
    for y in range(sub.height):
        for x in range(sub.width):
            a = px[x, y][3]
            if a:
                sp[x, y] = (30, 34, 40, min(230, a))
    return sil


def scaled(im, s, smooth=False):
    sub = crop_subject(im)
    w = max(1, round(sub.width * s))
    h = max(1, round(sub.height * s))
    return sub.resize((w, h), Image.LANCZOS if smooth else Image.NEAREST)


def build_strip(items, floor_tile, min_h=None):
    """items: list of (screen-scale RGBA image, short caption tag). Feet-anchored
    on a tiled floor; the tag is drawn centred under the feet line and the cell
    is widened to fit it, so tags never collide (long prose goes in the HTML
    legend, not here)."""
    pad = 16
    label_h = 14
    top_pad = 16
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    cells = []
    for im, caption in items:
        tw = int(probe.textlength(caption)) if caption else 0
        cells.append((im, caption, max(im.width, tw)))
    tallest = max(im.height for im, _, _ in cells)
    H = max(min_h or 0, tallest + top_pad + BASELINE_PAD + label_h)
    W = pad + sum(cw + pad for _, _, cw in cells)
    strip = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    for ty in range(0, H, TILE_SCREEN):
        for tx in range(0, W, TILE_SCREEN):
            strip.alpha_composite(floor_tile, (tx, ty))
    # dim the floor toward the in-game FLOOR_DIM tint so sprites read over it
    dim = Image.new("RGBA", (W, H), (20, 18, 16, 96))
    strip = Image.alpha_composite(strip, dim)
    draw = ImageDraw.Draw(strip)
    baseline = H - BASELINE_PAD - label_h
    x = pad
    for im, caption, cw in cells:
        strip.alpha_composite(im, (x + (cw - im.width) // 2, baseline - im.height))
        if caption:
            tw = int(probe.textlength(caption))
            draw.text((x + (cw - tw) // 2, baseline + 6), caption, fill=(255, 207, 122, 255))
        x += cw + pad
    return strip


def strip_html(strip, alt):
    return (
        '<div style="overflow-x:auto;margin:8px 0">'
        f'<img src="{data_uri(strip)}" width="{strip.width}" height="{strip.height}" '
        f'alt="{rs.esc(alt)}" style="image-rendering:pixelated;border:1px solid #3a332a;'
        'border-radius:6px"></div>'
    )


def cand_cell(png_path, label, blurb, prompt, grain_note):
    """Candidate cell: 2x pixelated thumb + verdict chips (rel = repo path)."""
    im = Image.open(png_path).convert("RGBA")
    rel = png_path.relative_to(ROOT).as_posix()
    sub = crop_subject(im)
    return (
        f'<div class="rs-cell" data-rel="{rs.esc(rel)}">'
        f'<div class="rs-thumb pix" style="padding:6px">'
        f'<img src="{data_uri(im)}" width="{im.width * 2}" height="{im.height * 2}" '
        f'alt="{rs.esc(label)}"></div>'
        f'<div class="rs-label">{rs.esc(label)}</div>'
        f'<code class="rs-sub">{rs.esc(rel.split("/")[-1])} -- '
        f"{im.width}x{im.height}px canvas, subject {sub.width}x{sub.height}px</code>"
        f'<p class="rs-blurb">{rs.esc(blurb)} {rs.esc(grain_note)}</p>'
        '<div class="prompt-toggle" onclick="var b=this.nextElementSibling;'
        "var on=b.classList.toggle('on');"
        "this.textContent=on?'prompt [-]':'prompt [+]'\">prompt [+]</div>"
        f'<div class="prompt-body">{rs.esc(prompt)}</div>'
        '<div class="rs-vtags"></div></div>'
    )


def main():
    manifest = json.loads((ROOT / "godot" / "data" / "office" / "props_manifest.json").read_text())[
        "props"
    ]
    floor_tile = load_floor_tile()
    worker = load_worker_silhouette()

    sections = []
    total_cells = 0
    for spec in PROPS:
        pid = spec["id"]
        true_h_screen = spec["true_tiles"] * TILE_SCREEN
        entry = manifest.get(pid)
        current = None
        if entry:
            cur_path = ROOT / "godot" / entry["art"].replace("res://", "")
            current = Image.open(cur_path).convert("RGBA")

        # ---- gather candidate PNGs
        native = sorted((BATCH / "native").glob(f"{pid}_*native*.png"))
        controls = sorted((BATCH / "manifest_scale").glob(f"{pid}_*.png"))
        dials = sorted((BATCH / "dial").glob(f"{pid}_*.png"))

        # ---- pick the lane's native pick: first decent roll (Pip re-picks via verdicts)
        pick = None
        for p in native:
            if "_decent_" in p.name or (pid in ("server_cluster",) and "native" in p.name):
                pick = p
                break
        if pick is None and native:
            pick = native[0]

        # ---- combined strip (c): short tags on the strip, prose in the legend
        items = []
        legend = []
        if current is not None:
            sub_h = subject_bbox(current)
            cur_sub_h = sub_h[3] - sub_h[1]
            mscale = entry["height_tiles"] * TILE_SCREEN / cur_sub_h
            items.append((scaled(current, mscale), "(a) current"))
            legend.append(
                f"(a) CURRENT art at manifest scale, {entry['height_tiles']} tiles "
                f"tall -- 1 art px = {mscale:.2f} screen px."
            )
            tscale = true_h_screen / cur_sub_h
            items.append((scaled(current, tscale, smooth=True), "(a2) shrunk"))
            legend.append(
                f"(a2) the same CURRENT art naively downscaled to the realistic "
                f"{spec['true_tiles']} tiles ({tscale:.2f}x, smooth) -- the "
                f"zero-cost alternative to a re-base: sub-pixel mush."
            )
        else:
            items.append((Image.new("RGBA", (8, 8), (0, 0, 0, 0)), "(a) no art"))
            legend.append("(a) NO CURRENT ART -- this prop is the drawn-circle gap.")
        if pick is not None:
            pim = Image.open(pick).convert("RGBA")
            items.append((scaled(pim, 2.0), "(b) native 2x"))
            legend.append(
                "(b) NATIVE-GRAIN lane pick shown at the world 2x -- 1 art px = "
                "2 screen px, exactly the floor tile grain "
                f"(lane pick: {pick.name}; re-pick via verdict chips below)."
            )
        items.append((worker, "worker"))
        legend.append("worker = in-game render, 128 screen px / 2 tiles (silhouetted).")
        combined = build_strip(items, floor_tile)

        body = ['<p class="rs-blurb" style="text-align:left;font-size:12px">']
        if entry:
            body.append(
                rs.esc(
                    f"Manifest today: height_tiles {entry['height_tiles']} "
                    f"(review:true), subject "
                    f"{entry['subject_px'][0]}x{entry['subject_px'][1]}px. "
                    f"Real-world: {spec['real_world']} -> proposed "
                    f"{spec['true_tiles']} tiles."
                )
            )
        else:
            body.append(
                rs.esc(
                    f"No manifest entry / no current art (gap Pip flagged). "
                    f"Real-world: {spec['real_world']} -> proposed "
                    f"{spec['true_tiles']} tiles."
                )
            )
        body.append("</p>")
        body.append(strip_html(combined, f"{pid} combined comparison strip"))
        body.append(
            '<p class="rs-blurb" style="text-align:left;max-width:70em">'
            + " ".join(rs.esc(x) for x in legend)
            + "</p>"
        )

        # ---- candidate grids
        def grid(paths, tag, blurb):
            nonlocal total_cells
            if not paths:
                return ""
            cells = []
            for p in paths:
                im = Image.open(p).convert("RGBA")
                sb = subject_bbox(im)
                sh = sb[3] - sb[1]
                if tag == "native" or tag == "dial":
                    note = (
                        f"@2x on floor: {sh * 2} screen px tall "
                        f"= {sh * 2 / TILE_SCREEN:.2f} tiles."
                    )
                else:
                    ig = (entry["height_tiles"] * TILE_SCREEN / sh) if entry else 2.0
                    note = f"at manifest scale 1 art px = {ig:.2f} screen px."
                cells.append(cand_cell(p, p.stem.replace(f"{pid}_", ""), blurb, PROMPTS[pid], note))
                total_cells += 1
            return f'<div class="rs-grid">{"".join(cells)}</div>'

        native_grid = grid(
            native,
            "native",
            "True-proportion native gen; thumb shown at the world 2x.",
        )
        if native_grid:
            body.append(
                '<div class="rs-sec-head" style="font-size:12px;border:none">'
                "(b) native-grain candidates -- verdict-tag your picks</div>"
            )
            body.append(native_grid)
        ctrl_grid = grid(
            controls,
            "control",
            "CONTROL: native gen at the CURRENT oversized manifest canvas.",
        )
        if ctrl_grid:
            body.append(
                '<div class="rs-sec-head" style="font-size:12px;border:none">'
                "control -- native gen at manifest (oversized) scale</div>"
            )
            body.append(ctrl_grid)
        dial_grid = grid(dials, "dial", "DIAL: medium detail / medium shading variant.")
        if dial_grid:
            body.append(
                '<div class="rs-sec-head" style="font-size:12px;border:none">'
                "dial -- medium detail / medium shading</div>"
            )
            body.append(dial_grid)

        sections.append(
            rs.section(
                f"{spec['label']}",
                "".join(body),
                count=f"{len(native)} native / {len(controls)} control / {len(dials)} dial",
                accent="#e0a34a",
            )
        )

    intro = (
        "Vanguard gating the ~500-gen prop re-base (#900, #925). Each section: "
        "(a) CURRENT art at manifest scale (the trio renders 3.25-3.5 tiles tall "
        "next to a 2-tile human -- oversized), (a2) the zero-cost alternative "
        "(shrink current art to realistic proportion -- smooth sub-pixel mush), "
        "(b) NATIVE-GRAIN candidates authored small and shown at the world 2x "
        "(1 art px = 2 screen px, exactly the floor tile grain), plus controls at "
        "the old oversized canvas and a medium-detail dial. Worker silhouette = "
        "the real in-game render (128 screen px from ~122 art px, i.e. the worker "
        "itself is near-1:1 fine grain -- the floor is the 2x anchor). Strips are "
        "1:1 screen pixels on the real concrete floor tile. "
        "<span class='warn'>Verdict-tag winners (promote = re-base this way); "
        "export JSON when done.</span>"
    )
    html = rs.page(
        "prop grain vanguard",
        "native-grain re-base decision sheet",
        "".join(sections),
        badges=[("props", len(PROPS)), ("cells", total_cells)],
        intro_html=intro,
        verdict_key="propgrain:verdicts",
        export_name="prop_grain_verdicts.json",
        footer_note="Generator: tools/art_review/gen_prop_grain_sheet.py; art: "
        "art_source/pixellab_2026-07-26_prop_grain_vanguard/.",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rs.write_ascii(OUT, html)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB, {total_cells} candidate cells)")


if __name__ == "__main__":
    main()
