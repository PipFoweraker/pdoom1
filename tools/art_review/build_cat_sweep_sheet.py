"""Build art_generated/cat_sweep_sheet.html -- the full 8-direction cat sweep.

2026-07-26 execution of Pip's locked recipe (issues #900 #913, ruling
"go cat sweep 8 dir now"):

  * east/west  = SIDE view with heft description language (the cat_b2 winner);
  * north/south = LOW TOP-DOWN (the empirically settled quadruped-correct
    answer -- side-view N/S is bipedal horror, rejected per issue #912);
  * every cat gets a full 8-direction LOW TOP-DOWN walk baseline;
  * tabby additionally gets SIDE-view diagonal walks (NE/SE/NW/SW) as the
    mixing-boundary probe: judge on the sheet where the side<->lowtd handoff
    should sit on diagonals;
  * butt-flash (issue #913): tail-up rear walk loops for tabby (cat_b2 reuse)
    and black -- renderer should splice frames ~2-8, not loop all 9.

Cats: tabby (cat_b2 heft pair reused), black, eldritch, purple.

Built on the shared review_style module (tools/art_review/README.md house
convention): verdict chips + hide-on-verdict enabled, players carry data-rel
so verdict export round-trips through analyze_verdicts.py.

All images embedded as base64 data URIs -- output is fully self-contained.

Usage:  python tools/art_review/build_cat_sweep_sheet.py
Output: art_generated/cat_sweep_sheet.html (gitignored derived output)
"""

import base64
import io
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_style import esc, page, section, write_ascii  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SW = ROOT / "art_source" / "pixellab_2026-07-26_cat_sweep"
OV = ROOT / "art_source" / "pixellab_2026-07-26_doom_overlays"
FLOOR_ATLAS = ROOT / "godot" / "assets" / "office_floor" / "tilesets" / "floor_concrete.png"
OUT = ROOT / "art_generated" / "cat_sweep_sheet.html"

REL_BASE = "art_source/pixellab_2026-07-26_cat_sweep"
OV_REL_BASE = "art_source/pixellab_2026-07-26_doom_overlays"

# clockwise-ish display order for 8-direction rows
DIRS8 = [
    "south",
    "south-east",
    "east",
    "north-east",
    "north",
    "north-west",
    "west",
    "south-west",
]
DIAGONALS = ["north-east", "south-east", "south-west", "north-west"]

# cat -> {side: char folder, lowtd: char folder}; folder names are the
# pixellab character names (zip-native layout, see MANIFEST.md)
CATS = {
    "tabby": {"side": "cat_b2_tabby_side_heft", "lowtd": "cat_b2_tabby_lowtd_heft"},
    "black": {"side": "cat_sweep_black_side_heft", "lowtd": "cat_black"},
    "eldritch": {"side": "cat_sweep_eldritch_side_heft", "lowtd": "cat_eldritch_r2"},
    "purple": {"side": "cat_sweep_purple_side_heft", "lowtd": "cat_purple_r2b"},
}
BUTT_FLASH_CATS = ["tabby", "black", "eldritch", "purple"]

# doom overlay families (drop-in request 2026-07-26): family -> (band label,
# axis, [variant names]). Folder layout: OV/{family}/{variant}/idle.png +
# OV/{family}/{variant}/loop/frame_*.png (loop optional -- stills always shown).
OVERLAYS = {
    "embers": ("band 1-2", "catastrophe (amber-orange)", ["faint", "motes", "flecks"]),
    "arc": ("band 2", "weirdness (electric blue)", ["branching", "radialweb", "zigzag"]),
    "wisp": ("band 3", "weirdness (violet)", ["slim", "tendrils", "curl"]),
    "aura": ("band 3", "weirdness (violet)", ["smokering", "spikysigil", "glowdisc"]),
    "flame": ("band 4", "catastrophe (fire)", ["tongue", "lowwide", "sparking"]),
    "void": ("band 4", "weirdness (terminal violet)", ["vortex", "tentacles", "jaggedrift"]),
    "states": (
        "cross-band",
        "hue-swapped set variants (1 gen each)",
        ["aura_amber", "aura_red", "wisp_blue", "embers_red"],
    ),
}
# curated layering-lab combos: (label, cat anim key, overlay key, note)
LAB_COMBOS = [
    (
        "tabby + aura glowdisc",
        "tabby_lowtd_south",
        "aura_glowdisc",
        "band-3 aura under a walking cat -- the DOOM_OVERLAY.md aura pass as a sprite",
    ),
    (
        "black + wisp slim",
        "black_lowtd_north",
        "wisp_slim",
        "violet smoke rising off a walking-away cat",
    ),
    (
        "eldritch side + arc radialweb",
        "eldritch_side_east",
        "arc_radialweb",
        "band-2 electricity crackling over the walker",
    ),
    (
        "purple + void vortex",
        "purple_lowtd_south",
        "void_vortex",
        "terminal void bleeding under the cat",
    ),
    (
        "tabby + embers motes",
        "tabby_side_east",
        "embers_motes",
        "subtle band-1 embers drifting over a side walk",
    ),
    (
        "black + flame lowwide",
        "black_lowtd_south",
        "flame_lowwide",
        "band-4 ground fire under the cat",
    ),
    (
        "tabby + amber aura state",
        "tabby_lowtd_east",
        "states_aura_amber",
        "band 0-1 cozy amber glow -- the most shippable subtle case",
    ),
]


def b64(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def rotation(char: str, direction: str) -> Path:
    return SW / char / "rotations" / f"{direction}.png"


def walk_group_dir(char: str) -> Path:
    """The character's walk animation group folder (the one with most dirs)."""
    anim_root = SW / char / "animations"
    walk_dirs = [d for d in anim_root.iterdir() if d.is_dir() and "walk" in d.name]
    if not walk_dirs:
        raise FileNotFoundError(f"no walk group under {anim_root}")
    return max(walk_dirs, key=lambda d: len(list(d.iterdir())))


def butt_group_dir(char: str) -> Path:
    anim_root = SW / char / "animations"
    hits = [d for d in anim_root.iterdir() if d.is_dir() and "butt" in d.name]
    if not hits:
        raise FileNotFoundError(f"no butt_flash group under {anim_root}")
    return hits[0]


def frames_of(group: Path, direction: str) -> list[str]:
    folder = group / direction
    paths = sorted(folder.glob("frame_*.png"))
    if not paths:
        raise FileNotFoundError(f"no frames under {folder}")
    return [b64(p) for p in paths]


def floor_tile_b64() -> str:
    """Crop the interior 32x32 tile from the 128x128 Wang atlas."""
    atlas = Image.open(FLOOR_ATLAS)
    tile = atlas.crop((32, 32, 64, 64))
    buf = io.BytesIO()
    tile.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


# ------------------------------------------------------------- sheet assembly

ANIMS: dict[str, list[str]] = {}  # anim key -> list of frame data URIs
PLAYER_BINDINGS: list[tuple[str, str]] = []  # (element id, anim key)
FLOOR = ""  # set in main()


def player_cell(key: str, label: str, rel: str, scale: int = 2, blurb: str = "") -> str:
    """Animated player on a floor strip, as a verdict-capable rs-cell."""
    px = 68 * scale
    eid = f"pl{len(PLAYER_BINDINGS)}"
    PLAYER_BINDINGS.append((eid, key))
    blurb_html = f'<p class="rs-blurb">{esc(blurb)}</p>' if blurb else ""
    return (
        f'<div class="rs-cell" data-rel="{esc(rel)}" style="width:auto">'
        f'<div class="floorstrip" style="background-image:url({FLOOR});'
        f'background-size:{32 * scale}px {32 * scale}px;min-height:{px + 12}px">'
        f'<img id="{eid}" src="{ANIMS[key][0]}" width="{px}" height="{px}"></div>'
        f'<div class="rs-label">{esc(label)}</div>'
        f"{blurb_html}"
        '<div class="rs-vtags"></div></div>'
    )


def still_strip(images: list[tuple[str, str]], scale: int = 2) -> str:
    cells = "".join(
        f'<div class="stillcell"><img src="{uri}" width="{68 * scale}" '
        f'height="{68 * scale}" alt="{esc(lbl)}"><div class="slbl">{esc(lbl)}</div></div>'
        for lbl, uri in images
    )
    return (
        f'<div class="floorstrip" style="background-image:url({FLOOR});'
        f'background-size:{32 * scale}px {32 * scale}px">{cells}</div>'
    )


def filmstrip(key: str) -> str:
    cells = "".join(
        f'<div class="stillcell"><img src="{u}" width="68" height="68">'
        f'<div class="slbl">{i}</div></div>'
        for i, u in enumerate(ANIMS[key])
    )
    return (
        f'<h4 class="fs-head">{esc(key)} ({len(ANIMS[key])} frames, 1x)</h4>'
        f'<div class="floorstrip" style="background-image:url({FLOOR});'
        f'background-size:32px 32px">{cells}</div>'
    )


EXTRA_CSS = """
.floorstrip{display:inline-flex;align-items:flex-end;gap:6px;padding:8px 12px;
border:1px solid #3a332a;border-radius:5px;margin:2px 0 4px;max-width:100%;
overflow-x:auto;}
.floorstrip img{image-rendering:pixelated;display:block;}
.stillcell{text-align:center;}
.stillcell .slbl{font-size:9px;color:#ccc;font-family:monospace;text-shadow:0 1px 2px #000;}
.rs-grid{align-items:flex-end;}
h4.fs-head{margin:10px 0 2px;font-weight:normal;color:#9aa;font-family:monospace;}
.cat-row-label{font-family:monospace;color:#ffcf7a;font-size:13px;margin:12px 0 2px;}
/* layering lab */
.lab-stage{position:relative;width:136px;height:136px;margin:0 auto;border-radius:5px;
overflow:hidden;background-size:64px 64px;}
.lab-stage img{position:absolute;left:0;top:0;width:136px;height:136px;
image-rendering:pixelated;}
.lab-stage img.cat{z-index:2;}
.lab-stage img.ov{z-index:3;}
.lab-stage img.ov.behind{z-index:1;}
.lab-ctl{display:flex;flex-direction:column;gap:3px;margin-top:6px;font-family:monospace;
font-size:10px;color:#9a9081;}
.lab-ctl label{display:flex;align-items:center;gap:5px;}
.lab-ctl input[type=range]{flex:1;accent-color:#e0a34a;}
.lab-ctl select{background:#252019;color:#e8e0d2;border:1px solid #3a332a;
font-family:monospace;font-size:10px;border-radius:4px;}
"""

ANIM_JS_TEMPLATE = """
var anims = {};
%ANIMS%
var bindings = %BINDINGS%;
var t = 0;
setInterval(function () {
  t += 1;
  for (var i = 0; i < bindings.length; i++) {
    var el = document.getElementById(bindings[i][0]);
    var fr = anims[bindings[i][1]];
    if (el && fr) el.src = fr[t % fr.length];
  }
}, 125);
"""


def main() -> int:
    global FLOOR
    missing = [p for p in (SW, FLOOR_ATLAS) if not p.exists()]
    if missing:
        print("missing inputs: " + ", ".join(str(m) for m in missing))
        return 1
    FLOOR = floor_tile_b64()

    # ---- load all clips ---------------------------------------------------
    for cat, chars in CATS.items():
        side_walk = walk_group_dir(chars["side"])
        lowtd_walk = walk_group_dir(chars["lowtd"])
        # all cats carry the 4 side diagonals since the cap-lift expansion;
        # tolerate absence so the sheet still builds from a partial tree
        for d in ["east", "west"] + DIAGONALS:
            if (side_walk / d).exists():
                ANIMS[f"{cat}_side_{d}"] = frames_of(side_walk, d)
        for d in DIRS8:
            ANIMS[f"{cat}_lowtd_{d}"] = frames_of(lowtd_walk, d)
        # cat_black's template north misfired face-on; a v3 walk_north_fix
        # group holds the usable back-view clip (see MANIFEST.md)
        north_fix = SW / chars["lowtd"] / "animations" / "walk_north_fix"
        if north_fix.exists():
            ANIMS[f"{cat}_lowtd_north"] = frames_of(north_fix, "north")
        # bonus idle flourishes (cap-lift expansion): sitting / licking, south
        for flourish in ("sitting", "licking"):
            fdir = SW / chars["lowtd"] / "animations" / flourish
            if (fdir / "south").exists():
                ANIMS[f"{cat}_{flourish}_south"] = frames_of(fdir, "south")
    for cat in BUTT_FLASH_CATS:
        try:
            butt = butt_group_dir(CATS[cat]["lowtd"])
        except FileNotFoundError:
            continue
        if (butt / "north").exists():
            ANIMS[f"{cat}_butt_north"] = frames_of(butt, "north")

    # ---- load doom overlays (family/variant folders; loop optional) --------
    overlay_variants: dict[str, list[str]] = {}  # family -> [variant, ...]
    if OV.exists():
        for fam in OVERLAYS:
            fam_dir = OV / fam
            if not fam_dir.exists():
                continue
            declared = OVERLAYS[fam][2]
            found = sorted(d.name for d in fam_dir.iterdir() if d.is_dir())
            variants = [v for v in declared if v in found] + [v for v in found if v not in declared]
            overlay_variants[fam] = variants
            for v in variants:
                vdir = fam_dir / v
                key = f"{fam}_{v}"
                loop = sorted((vdir / "loop").glob("frame_*.png"))
                if loop:
                    ANIMS[key] = [b64(p) for p in loop]
                elif (vdir / "idle.png").exists():
                    ANIMS[key] = [b64(vdir / "idle.png")]

    def rel_walk(cat: str, view: str, d: str) -> str:
        char = CATS[cat][view]
        return f"{REL_BASE}/{char}/animations/walk/{d}"

    # ---- section 1: recipe stills -----------------------------------------
    s1 = []
    for cat, chars in CATS.items():
        s1.append(f'<div class="cat-row-label">{cat} -- side (E/W lane)</div>')
        s1.append(still_strip([(d, b64(rotation(chars["side"], d))) for d in DIRS8]))
        s1.append(f'<div class="cat-row-label">{cat} -- low top-down (N/S + baseline)</div>')
        s1.append(still_strip([(d, b64(rotation(chars["lowtd"], d))) for d in DIRS8]))
    sec1 = section(
        "1. Rotations -- all 8 directions, both views (2x)",
        "".join(s1),
        count="4 cats x 2 views x 8 dirs",
        accent="#e0a34a",
    )

    # ---- section 2: recipe walks (side E/W + lowtd N/S) -------------------
    s2 = []
    for cat in CATS:
        s2.append(f'<div class="cat-row-label">{cat}</div><div class="rs-grid">')
        for d in ("east", "west"):
            s2.append(player_cell(f"{cat}_side_{d}", f"side {d}", rel_walk(cat, "side", d)))
        for d in ("north", "south"):
            s2.append(player_cell(f"{cat}_lowtd_{d}", f"lowtd {d}", rel_walk(cat, "lowtd", d)))
        s2.append("</div>")
    sec2 = section(
        "2. The locked recipe -- side E/W + lowtd N/S walks (2x, animated)",
        "".join(s2),
        count="4 cats x 4 dirs",
        accent="#6fae5a",
    )

    # ---- section 3: lowtd 8-dir baseline ----------------------------------
    s3 = []
    for cat in CATS:
        s3.append(f'<div class="cat-row-label">{cat}</div><div class="rs-grid">')
        for d in DIRS8:
            s3.append(player_cell(f"{cat}_lowtd_{d}", d, rel_walk(cat, "lowtd", d)))
        s3.append("</div>")
    sec3 = section(
        "3. Low top-down 8-direction walk baseline (2x, animated)",
        "".join(s3),
        count="4 cats x 8 dirs",
        accent="#6ba3b0",
    )

    # ---- section 4: diagonal mixing-boundary probe (all cats) -------------
    s4 = [
        '<p class="intro">Per diagonal: SIDE-view walk beside the LOW-TOP-DOWN walk '
        "of the same cat. Verdict question: on diagonals, where should the "
        "side&lt;-&gt;lowtd handoff sit? Tabby was the original probe; the "
        "cap-lift expansion added the other three cats so a mixing ruling "
        "applies to the full roster immediately. Cardinal anchors (side east, "
        "lowtd north) included for reference.</p>"
    ]
    for cat in CATS:
        pairs = [d for d in DIAGONALS if f"{cat}_side_{d}" in ANIMS]
        if not pairs:
            continue
        s4.append(f'<div class="cat-row-label">{cat}</div><div class="rs-grid">')
        for d in pairs:
            s4.append(
                player_cell(
                    f"{cat}_side_{d}",
                    f"side {d}",
                    rel_walk(cat, "side", d),
                    blurb="side-view diagonal",
                )
            )
            s4.append(
                player_cell(
                    f"{cat}_lowtd_{d}",
                    f"lowtd {d}",
                    rel_walk(cat, "lowtd", d),
                    blurb="lowtd diagonal",
                )
            )
        s4.append("</div>")
    s4.append('<div class="cat-row-label">cardinal anchors</div><div class="rs-grid">')
    s4.append(player_cell("tabby_side_east", "side east", rel_walk("tabby", "side", "east")))
    s4.append(player_cell("tabby_lowtd_north", "lowtd north", rel_walk("tabby", "lowtd", "north")))
    s4.append("</div>")
    sec4 = section(
        "4. Diagonal probe -- side vs lowtd mixing boundary, all cats (2x, animated)",
        "".join(s4),
        count="4 cats x 4 diagonals x 2 views",
        accent="#b57fb0",
    )

    # ---- section 5: butt-flash --------------------------------------------
    s5 = [
        '<p class="intro">Issue #913 splice loops: tail-up rear walk, jaunty strut. '
        "As raw loops the tail pop-up reads abrupt -- the renderer should splice "
        "frames ~2-8 (or hold 4-8) into the normal north walk, not loop all 9 "
        "(cat_b2 finding). All four cats since the cap-lift expansion. Normal "
        "north walk beside each for contrast.</p>"
    ]
    butt_cats = [c for c in BUTT_FLASH_CATS if f"{c}_butt_north" in ANIMS]
    for cat in butt_cats:
        s5.append(f'<div class="cat-row-label">{cat}</div><div class="rs-grid">')
        s5.append(
            player_cell(f"{cat}_lowtd_north", "normal north", rel_walk(cat, "lowtd", "north"))
        )
        char = CATS[cat]["lowtd"]
        s5.append(
            player_cell(
                f"{cat}_butt_north",
                "butt-flash north",
                f"{REL_BASE}/{char}/animations/butt_flash_north/north",
                blurb="splice frames ~2-8",
            )
        )
        s5.append("</div>")
    s5.append("".join(filmstrip(f"{cat}_butt_north") for cat in butt_cats))
    sec5 = section(
        "5. Butt-flash splice loops (issue #913) -- 2x, animated + filmstrips",
        "".join(s5),
        count=f"{len(butt_cats)} cats",
        accent="#c98b3f",
    )

    # ---- section 5b: idle flourishes (cap-lift extras) --------------------
    sec5b = ""
    flourish_cells = []
    for cat in CATS:
        for flourish in ("sitting", "licking"):
            key = f"{cat}_{flourish}_south"
            if key in ANIMS:
                flourish_cells.append(
                    player_cell(
                        key,
                        f"{cat} {flourish}",
                        f"{REL_BASE}/{CATS[cat]['lowtd']}/animations/{flourish}/south",
                    )
                )
    if flourish_cells:
        sec5b = section(
            "5b. Idle flourishes -- sitting / licking, south (2x, animated)",
            '<p class="intro">Bonus template clips (cap-lift yes-and): office '
            "cats spend most of their time NOT walking; these are the first "
            "stationary-behaviour candidates for the sandbox.</p>"
            '<div class="rs-grid">' + "".join(flourish_cells) + "</div>",
            count=f"{len(flourish_cells)} clips",
            accent="#8fae6b",
        )

    # ---- section 6: doom overlay families (drop-in 2026-07-26) ------------
    sec6 = sec7 = ""
    lab_js = ""
    if overlay_variants:
        s6 = [
            '<p class="intro">Doom-generation overlay sets (drop-in request): '
            "particle/animation overlays for the doom-is-a-layer thesis "
            "(docs/art/DOOM_OVERLAY.md, PALETTE_AND_DOOM_INTENSITY.md ladder). "
            "One hue per asset, hue = the band's glow hex. 16-candidate packs "
            "were generated per family; 3 diverse survivors each were kept and "
            "animated as loops. Early failures here do NOT invalidate the "
            "thesis -- verdict the survivors, rerolls are ~1 gen.</p>"
        ]
        for fam, (band, axis, _decl) in OVERLAYS.items():
            if fam not in overlay_variants or not overlay_variants[fam]:
                continue
            s6.append(
                f'<div class="cat-row-label">{esc(fam)} -- {esc(band)}, '
                f'{esc(axis)}</div><div class="rs-grid">'
            )
            for v in overlay_variants[fam]:
                key = f"{fam}_{v}"
                if key not in ANIMS:
                    continue
                rel = f"{OV_REL_BASE}/{fam}/{v}"
                n_fr = len(ANIMS[key])
                blurb = f"{n_fr} frame loop" if n_fr > 1 else "still (no loop)"
                s6.append(player_cell(key, v, rel, blurb=blurb))
            s6.append("</div>")
        sec6 = section(
            "6. Doom overlay families -- stills + loops (2x, animated)",
            "".join(s6),
            count=f"{sum(len(v) for v in overlay_variants.values())} variants",
            accent="#7A3B8F",
        )

        # ---- section 7: layering lab --------------------------------------
        s7 = [
            '<p class="intro">Layering experiments: overlay composited over a '
            "walking cat on the floor tile. Dials per combo: opacity, blend "
            '(normal / screen approximates the additive "lighter" pass / '
            "lighten), and behind/in-front z-order. Judge how far a sprite "
            "overlay gets toward the shader-style doom pass -- and where it "
            "breaks.</p>"
        ]
        lab_rows = []
        lab_idx = 0
        s7.append('<div class="rs-grid">')
        for label, cat_key, ov_key, note in LAB_COMBOS:
            if cat_key not in ANIMS or ov_key not in ANIMS:
                continue
            cid = f"labc{lab_idx}"
            oid = f"labo{lab_idx}"
            PLAYER_BINDINGS.append((cid, cat_key))
            PLAYER_BINDINGS.append((oid, ov_key))
            behind = ("aura" in ov_key) or ("void" in ov_key)
            rel = f"lab/{cat_key}+{ov_key}"
            s7.append(
                f'<div class="rs-cell" data-rel="{esc(rel)}" style="width:220px">'
                f'<div class="lab-stage" id="stage{lab_idx}" '
                f'style="background-image:url({FLOOR})">'
                f'<img id="{cid}" class="cat" src="{ANIMS[cat_key][0]}">'
                f'<img id="{oid}" class="ov{" behind" if behind else ""}" '
                f'src="{ANIMS[ov_key][0]}">'
                "</div>"
                f'<div class="rs-label">{esc(label)}</div>'
                f'<p class="rs-blurb">{esc(note)}</p>'
                f'<div class="lab-ctl">'
                f'<label>opacity <input type="range" id="op{lab_idx}" min="0" '
                f'max="100" value="60"> <span id="opv{lab_idx}">60%</span></label>'
                f'<label>blend <select id="bl{lab_idx}">'
                '<option value="normal">normal</option>'
                '<option value="screen" selected>screen (~additive)</option>'
                '<option value="lighten">lighten</option>'
                '<option value="hard-light">hard-light</option></select>'
                f' <label><input type="checkbox" id="bh{lab_idx}"'
                f'{" checked" if behind else ""}> behind cat</label></label>'
                "</div>"
                '<div class="rs-vtags"></div></div>'
            )
            lab_rows.append(lab_idx)
            lab_idx += 1
        s7.append("</div>")
        sec7 = section(
            "7. Layering lab -- overlay x cat compositing dials (2x, animated)",
            "".join(s7),
            count=f"{lab_idx} combos",
            accent="#5C7AC3",
        )
        lab_js = (
            "var labN = %d;\n"
            "for (var li = 0; li < labN; li++) (function (i) {\n"
            "  var ov = document.getElementById('labo' + i);\n"
            "  var op = document.getElementById('op' + i);\n"
            "  var opv = document.getElementById('opv' + i);\n"
            "  var bl = document.getElementById('bl' + i);\n"
            "  var bh = document.getElementById('bh' + i);\n"
            "  function apply() {\n"
            "    ov.style.opacity = op.value / 100;\n"
            "    opv.textContent = op.value + '%%';\n"
            "    ov.style.mixBlendMode = bl.value;\n"
            "    ov.classList.toggle('behind', bh.checked);\n"
            "  }\n"
            "  op.oninput = apply; bl.onchange = apply; bh.onchange = apply;\n"
            "  apply();\n"
            "})(li);\n" % lab_idx
        )

    # ---- page -------------------------------------------------------------
    n_clips = len(ANIMS)
    intro = (
        "Full 8-direction cat sweep on the locked recipe (issues #900 #913): "
        "side view with heft language for E/W, low top-down for N/S, full lowtd "
        "8-dir baseline per cat, tabby side-diagonal mixing probe, butt-flash "
        "loops for tabby+black. tabby side/lowtd = the cat_b2 heft pair "
        "(reused, not regenerated); black/eldritch/purple lowtd = the existing "
        "sandbox cats; the three side-heft cats are new. Sections 6-7: doom "
        "overlay particle/animation sets + a layering lab with opacity/blend "
        "dials (drop-in request). Players at 8 fps on the office floor tile. "
        "Sources: art_source/pixellab_2026-07-26_cat_sweep/ and "
        "art_source/pixellab_2026-07-26_doom_overlays/ (MANIFEST.md in each)."
    )
    body = sec1 + sec2 + sec3 + sec4 + sec5 + sec5b + sec6 + sec7
    anim_js = ANIM_JS_TEMPLATE.replace(
        "%ANIMS%",
        "\n".join(
            f'anims["{k}"] = [' + ",".join(f'"{u}"' for u in v) + "];" for k, v in ANIMS.items()
        ),
    ).replace(
        "%BINDINGS%",
        "[" + ",".join(f'["{eid}","{key}"]' for eid, key in PLAYER_BINDINGS) + "]",
    )
    html = page(
        "cat sweep",
        "8-direction recipe sweep -- side E/W heft + lowtd N/S (issues #900 #913)",
        body,
        badges=(("cats", "4"), ("clips", str(n_clips)), ("fps", "8")),
        intro_html=intro,
        extra_css=EXTRA_CSS,
        extra_js=anim_js + "\n" + lab_js,
        verdict_key="cat_sweep:verdicts",
        export_name="cat_sweep_verdicts.json",
        footer_note=(
            "Recipe: NEVER ship side-view N/S (bipedal horror, issue #912). "
            "Renderer 8-dir extension is a separate increment -- no godot/ "
            "changes ride with this sheet."
        ),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    write_ascii(OUT, html)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB, {n_clips} clips)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
