"""Build art_generated/cat_refinement_sheet.html -- the cat refinement batch.

2026-07-26 execution of Pip's cat-sweep review rulings (issues #900 #912 #913
#923; verdicts folded in PR #935):

  1. cat_purple RETIRED (noted, nothing regenerated);
  2. white-flash fix re-rolls (v3, clean-alpha language) for the clips that
     showed pale flashes under the cats -- old vs new side by side, with
     scan_white_flash.py numbers in the blurbs;
  3. tabby lowtd north tail-spaz re-roll;
  4. tabby lowtd south calmer-gait / slightly-taller re-roll;
  5. sitting + licking REDONE at 16 frames (v3 motion-arc prompts) for
     tabby / black / eldritch + the new roster;
  6. butt punctuation: prompt-language attempt + deterministic PIL dot
     stamp (butt_dot_stamp.py) -- both shown;
  7. new roster on the locked recipe: stripey brown, kambu_placeholder
     (superseded later by the real Kambu spec, issue #923), fat marmalade
     chonker.

Built on the shared review_style module (verdict chips, hide-on-verdict,
collapsed sections + completeness pills). All images embedded as base64 data
URIs -- fully self-contained.

Usage:  python tools/art_review/build_cat_refinement_sheet.py
Output: art_generated/cat_refinement_sheet.html (gitignored derived output)
"""

import base64
import io
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_style import esc, page, section, write_ascii  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
NEW = ROOT / "art_source" / "pixellab_2026-07-26_cat_refinement"
OLD = ROOT / "art_source" / "pixellab_2026-07-26_cat_sweep"
FLOOR_ATLAS = ROOT / "godot" / "assets" / "office_floor" / "tilesets" / "floor_concrete.png"
OUT = ROOT / "art_generated" / "cat_refinement_sheet.html"

NEW_REL = "art_source/pixellab_2026-07-26_cat_refinement"
OLD_REL = "art_source/pixellab_2026-07-26_cat_sweep"

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

# ---- fix ledger: (label, old char/anim/dir, new char/anim/dir, note) --------
WHITE_FLASH_FIXES = [
    (
        "black side west",
        ("cat_sweep_black_side_heft", "walk_ew", "west"),
        ("cat_sweep_black_side_heft", "walk_west_cleanfix", "west"),
        "old: pale shadow ellipse appears frames 1/4/7 (96 flash-px)",
    ),
    (
        "black lowtd NE",
        ("cat_black", "walking", "north-east"),
        ("cat_black", "walk_diag_cleanfix", "north-east"),
        "old scan found NO in-sprite white (flash was leg-gap flicker); re-rolled per ruling",
    ),
    (
        "black lowtd SE",
        ("cat_black", "walking", "south-east"),
        ("cat_black", "walk_diag_cleanfix", "south-east"),
        "",
    ),
    (
        "black lowtd SW",
        ("cat_black", "walking", "south-west"),
        ("cat_black", "walk_diag_cleanfix", "south-west"),
        "",
    ),
    (
        "black lowtd NW",
        ("cat_black", "walking", "north-west"),
        ("cat_black", "walk_diag_cleanfix", "north-west"),
        "",
    ),
    (
        "eldritch east",
        ("cat_eldritch_r2", "walk_8dir_lowtd", "east"),
        ("cat_eldritch_r2", "walk_ew_cleanfix", "east"),
        "old: stuck bright fleck at (41,36)",
    ),
    (
        "eldritch east ALT (cleanfix2)",
        ("cat_eldritch_r2", "walk_8dir_lowtd", "east"),
        ("cat_eldritch_r2", "walk_east_cleanfix2", "east"),
        "second roll -- collar-stability language; pick between this and cleanfix v1",
    ),
    (
        "eldritch west",
        ("cat_eldritch_r2", "walk_8dir_lowtd", "west"),
        ("cat_eldritch_r2", "walk_ew_cleanfix", "west"),
        "old: intermittent fleck at (25,37)",
    ),
    (
        "tabby lowtd east",
        ("cat_b2_tabby_lowtd_heft", "walk_ns_lowtd", "east"),
        ("cat_b2_tabby_lowtd_heft", "walk_ew_cleanfix", "east"),
        "old: cream belly-line flicker (145 flash-px)",
    ),
    (
        "tabby lowtd west",
        ("cat_b2_tabby_lowtd_heft", "walk_ns_lowtd", "west"),
        ("cat_b2_tabby_lowtd_heft", "walk_ew_cleanfix", "west"),
        "old: cream belly-line flicker (145 flash-px)",
    ),
]

GAIT_FIXES = [
    (
        "tabby north -- tail-spaz fix",
        ("cat_b2_tabby_lowtd_heft", "walk_ns_lowtd", "north"),
        ("cat_b2_tabby_lowtd_heft", "walk_north_tailfix", "north"),
        "old: tail position jumps between frames; new: one continuous relaxed curve",
    ),
    (
        "tabby south -- calmer + taller",
        ("cat_b2_tabby_lowtd_heft", "walk_ns_lowtd", "south"),
        ("cat_b2_tabby_lowtd_heft", "walk_south_calmtall", "south"),
        "old: 'sashaying a little hard'; new: minimal hip sway, body carried slightly taller",
    ),
]

# sitting/licking v2 -- existing cats: old 8/10-frame template vs new 16-frame v3
FLOURISH_CATS_EXISTING = ["cat_b2_tabby_lowtd_heft", "cat_black", "cat_eldritch_r2"]

NEW_CATS = {
    "stripey": {
        "side": "cat_ref_stripey_side_heft",
        "lowtd": "cat_ref_stripey_lowtd",
        "blurb": "stripey brown -- tabby-adjacent but distinct brown striping",
    },
    "kambu_placeholder": {
        "side": "cat_ref_kambu_placeholder_side_heft",
        "lowtd": "cat_ref_kambu_placeholder_lowtd",
        "blurb": "white blotches/patches placeholder -- superseded by the real Kambu spec (issue #923)",
    },
    "marmalade": {
        "side": "cat_ref_marmalade_side_heft",
        "lowtd": "cat_ref_marmalade_lowtd",
        "blurb": "fat marmalade chonker, big whiskers -- the Scarface Claw archetype",
    },
}

# ------------------------------------------------------------------ plumbing

ANIMS: dict[str, list[str]] = {}
PLAYER_BINDINGS: list[tuple[str, str]] = []
FLOOR = ""


def b64(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def frames_of(base: Path, char: str, anim: str, direction: str) -> list[str]:
    folder = base / char / "animations" / anim / direction
    paths = sorted(folder.glob("*.png"))
    if not paths:
        raise FileNotFoundError(f"no frames under {folder}")
    return [b64(p) for p in paths]


def load_anim(key: str, base: Path, char: str, anim: str, direction: str) -> str | None:
    try:
        ANIMS[key] = frames_of(base, char, anim, direction)
        return key
    except FileNotFoundError:
        return None


def floor_tile_b64() -> str:
    atlas = Image.open(FLOOR_ATLAS)
    tile = atlas.crop((32, 32, 64, 64))
    buf = io.BytesIO()
    tile.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def player_cell(key: str, label: str, rel: str, scale: int = 2, blurb: str = "") -> str:
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


def filmstrip(key: str, label: str | None = None) -> str:
    cells = "".join(
        f'<div class="stillcell"><img src="{u}" width="68" height="68">'
        f'<div class="slbl">{i}</div></div>'
        for i, u in enumerate(ANIMS[key])
    )
    return (
        f'<h4 class="fs-head">{esc(label or key)} ({len(ANIMS[key])} frames, 1x)</h4>'
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
.retire-note{font-family:monospace;color:#c98b3f;border:1px dashed #6a5333;
border-radius:5px;padding:8px 12px;margin:6px 0;}
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
    missing = [p for p in (NEW, OLD, FLOOR_ATLAS) if not p.exists()]
    if missing:
        print("missing inputs: " + ", ".join(str(m) for m in missing))
        return 1
    FLOOR = floor_tile_b64()

    # ---- section 0: dispositions ------------------------------------------
    sec0 = section(
        "0. Dispositions from the 2026-07-26 review",
        '<div class="retire-note">cat_purple (cat_purple_r2b + '
        "cat_sweep_purple_side_heft): RETIRED -- 'the large purple cat with "
        "white collary thing can go'. No regeneration; sprites remain in the "
        "sweep folder for the archive. The eldritch cat stays (doom comes from "
        "overlays; its glow accents predate the regular-looks ruling).</div>",
        count="1 retirement",
        accent="#b0553a",
    )

    # ---- section 1: white-flash fixes -------------------------------------
    s1 = [
        '<p class="intro">Each disliked clip re-rolled via v3 with explicit '
        "clean-alpha language. OLD on the left (sweep clip Pip disliked), NEW "
        "on the right. Scan numbers from tools/art_review/scan_white_flash.py "
        "(temporal flash-px; moving cream paws legitimately score ~70, the "
        "known-bad clips scored 96-145).</p>"
    ]
    for label, old_ref, new_ref, note in WHITE_FLASH_FIXES:
        ochar, oanim, odir = old_ref
        nchar, nanim, ndir = new_ref
        okey = load_anim(f"old_{label}", OLD, ochar, oanim, odir)
        nkey = load_anim(f"new_{label}", NEW, nchar, nanim, ndir)
        if not nkey:
            continue
        s1.append(f'<div class="cat-row-label">{esc(label)}</div><div class="rs-grid">')
        if okey:
            s1.append(
                player_cell(
                    okey,
                    "OLD (disliked)",
                    f"{OLD_REL}/{ochar}/animations/{oanim}/{odir}",
                    blurb=note,
                )
            )
        s1.append(
            player_cell(
                nkey,
                "NEW (cleanfix)",
                f"{NEW_REL}/{nchar}/animations/{nanim}/{ndir}",
            )
        )
        s1.append("</div>")
    sec1 = section(
        "1. White-flash fix re-rolls -- old vs new (2x, animated)",
        "".join(s1),
        count=f"{len(WHITE_FLASH_FIXES)} clips",
        accent="#6fae5a",
    )

    # ---- section 2: gait fixes --------------------------------------------
    s2 = []
    for label, old_ref, new_ref, note in GAIT_FIXES:
        ochar, oanim, odir = old_ref
        nchar, nanim, ndir = new_ref
        okey = load_anim(f"old_{label}", OLD, ochar, oanim, odir)
        nkey = load_anim(f"new_{label}", NEW, nchar, nanim, ndir)
        if not nkey:
            continue
        s2.append(f'<div class="cat-row-label">{esc(label)}</div><div class="rs-grid">')
        if okey:
            s2.append(
                player_cell(okey, "OLD", f"{OLD_REL}/{ochar}/animations/{oanim}/{odir}", blurb=note)
            )
        s2.append(player_cell(nkey, "NEW", f"{NEW_REL}/{nchar}/animations/{nanim}/{ndir}"))
        s2.append("</div>")
    sec2 = section(
        "2. Gait fixes -- tabby north tail-spaz + south calm/tall (2x, animated)",
        "".join(s2),
        count=f"{len(GAIT_FIXES)} clips",
        accent="#6ba3b0",
    )

    # ---- section 3: sitting / licking v2 ----------------------------------
    s3 = [
        '<p class="intro">All old sitting/licking clips were disliked -- too '
        "little range of motion. v2 clips are 16-frame v3 customs with "
        "explicit motion arcs (sitting: stand -&gt; haunches lower -&gt; settle "
        "-&gt; weight shift -&gt; tail wrap; licking: head dip -&gt; three tongue "
        "strokes -&gt; pause -&gt; resume). Old 8/10-frame template clip beside "
        "each for contrast; play slower in your head -- same 8 fps here.</p>"
    ]
    old_flourish_anim = {"sitting": "sitting", "licking": "licking"}
    for char in FLOURISH_CATS_EXISTING + [c["lowtd"] for c in NEW_CATS.values()]:
        row = []
        for flourish in ("sitting", "licking"):
            okey = load_anim(
                f"old_{char}_{flourish}", OLD, char, old_flourish_anim[flourish], "south"
            )
            nkey = load_anim(f"new_{char}_{flourish}", NEW, char, f"{flourish}_v2", "south")
            if okey:
                row.append(
                    player_cell(
                        okey,
                        f"OLD {flourish}",
                        f"{OLD_REL}/{char}/animations/{flourish}/south",
                        blurb="disliked: cramped motion",
                    )
                )
            if nkey:
                row.append(
                    player_cell(
                        nkey,
                        f"NEW {flourish} v2 (16f)",
                        f"{NEW_REL}/{char}/animations/{flourish}_v2/south",
                    )
                )
        if row:
            s3.append(f'<div class="cat-row-label">{esc(char)}</div><div class="rs-grid">')
            s3.extend(row)
            s3.append("</div>")
    sec3 = section(
        "3. Sitting / licking v2 -- 16-frame motion arcs (2x, animated)",
        "".join(s3),
        count="6 cats x 2 clips",
        accent="#8fae6b",
    )

    # ---- section 4: butt punctuation --------------------------------------
    s4 = [
        '<p class="intro">Issue #913 follow-up: the flash frames lacked the '
        "anatomical dot. Two paths shown: (a) prompt-language attempt "
        "(butt_flash_dotted, v3 re-roll); (b) deterministic PIL stamp on the "
        "liked sweep clips (butt_dot_stamp.py -- 1-2px dark dot under the "
        "raised tail on the flash frames only). Filmstrips below the players "
        "for pixel-level judgement.</p>"
    ]
    dot_keys = []
    prompt_key = load_anim(
        "tabby_butt_dotted_prompt",
        NEW,
        "cat_b2_tabby_lowtd_heft",
        "butt_flash_dotted",
        "north",
    )
    s4.append('<div class="cat-row-label">prompt-language attempt (tabby)</div>')
    s4.append('<div class="rs-grid">')
    okey = load_anim("tabby_butt_old", OLD, "cat_b2_tabby_lowtd_heft", "butt_flash_north", "north")
    if okey:
        s4.append(
            player_cell(
                okey,
                "OLD butt-flash (liked, dotless)",
                f"{OLD_REL}/cat_b2_tabby_lowtd_heft/animations/butt_flash_north/north",
            )
        )
    if prompt_key:
        s4.append(
            player_cell(
                prompt_key,
                "prompt-language re-roll",
                f"{NEW_REL}/cat_b2_tabby_lowtd_heft/animations/butt_flash_dotted/north",
            )
        )
        dot_keys.append(("tabby prompt attempt", prompt_key))
    s4.append("</div>")
    # PIL-stamped variants land under {char}/animations/butt_flash_stamped/north
    s4.append('<div class="cat-row-label">deterministic PIL stamp</div><div class="rs-grid">')
    for char in ["cat_b2_tabby_lowtd_heft", "cat_black", "cat_eldritch_r2"] + [
        c["lowtd"] for c in NEW_CATS.values()
    ]:
        skey = load_anim(f"{char}_butt_stamped", NEW, char, "butt_flash_stamped", "north")
        if skey:
            s4.append(
                player_cell(
                    skey,
                    f"{char} stamped",
                    f"{NEW_REL}/{char}/animations/butt_flash_stamped/north",
                )
            )
            dot_keys.append((f"{char} stamped", skey))
    s4.append("</div>")
    for lbl, k in dot_keys:
        s4.append(filmstrip(k, lbl))
    sec4 = section(
        "4. Butt punctuation (issue #913) -- prompt vs PIL stamp (2x, animated)",
        "".join(s4),
        count=f"{len(dot_keys)} clips",
        accent="#c98b3f",
    )

    # ---- section 5: new roster --------------------------------------------
    s5 = [
        '<p class="intro">Three new cats on the locked recipe (side-heft E/W + '
        "lowtd N/S + full 8-dir lowtd baseline + butt-flash loop + 16-frame "
        "flourishes). REGULAR looks -- no spooky features, doom comes from "
        "overlays; standard eyes. Body-range ruling: cats may span 'skinny "
        "lankers and hefty chonkers' -- the marmalade should read emphatically "
        "chonky.</p>"
    ]
    for cat, spec in NEW_CATS.items():
        side, lowtd = spec["side"], spec["lowtd"]
        s5.append(f'<div class="cat-row-label">{esc(cat)} -- {esc(spec["blurb"])}</div>')
        rot_side = NEW / side / "rotations"
        rot_lowtd = NEW / lowtd / "rotations"
        if rot_side.exists():
            s5.append(still_strip([(d, b64(rot_side / f"{d}.png")) for d in DIRS8]))
        if rot_lowtd.exists():
            s5.append(still_strip([(d, b64(rot_lowtd / f"{d}.png")) for d in DIRS8]))
        s5.append('<div class="rs-grid">')
        for d in ("east", "west"):
            k = load_anim(f"{cat}_side_{d}", NEW, side, "walk_ew", d)
            if k:
                s5.append(player_cell(k, f"side {d}", f"{NEW_REL}/{side}/animations/walk_ew/{d}"))
        for d in DIRS8:
            k = load_anim(f"{cat}_lowtd_{d}", NEW, lowtd, "walk_8dir_lowtd", d)
            if k:
                s5.append(
                    player_cell(
                        k, f"lowtd {d}", f"{NEW_REL}/{lowtd}/animations/walk_8dir_lowtd/{d}"
                    )
                )
        bkey = load_anim(f"{cat}_butt", NEW, lowtd, "butt_flash_dotted", "north")
        if bkey:
            s5.append(
                player_cell(
                    bkey,
                    "butt-flash north",
                    f"{NEW_REL}/{lowtd}/animations/butt_flash_dotted/north",
                    blurb="splice frames ~2-8",
                )
            )
        s5.append("</div>")
    sec5 = section(
        "5. New roster -- stripey / kambu_placeholder / marmalade (2x, animated)",
        "".join(s5),
        count="3 cats x (2 views + walks + butt-flash)",
        accent="#e0a34a",
    )

    # ---- page -------------------------------------------------------------
    n_clips = len(ANIMS)
    intro = (
        "Cat refinement batch executing Pip's 2026-07-26 cat-sweep review: "
        "purple retired; white-flash re-rolls (verified with "
        "scan_white_flash.py); tabby tail-spaz + sashay fixes; 16-frame "
        "sitting/licking motion arcs; butt punctuation via prompt AND "
        "deterministic PIL stamp; three new roster cats on the locked recipe. "
        "Players at 8 fps on the office floor tile. Source: "
        "art_source/pixellab_2026-07-26_cat_refinement/ (MANIFEST.md)."
    )
    body = sec0 + sec1 + sec2 + sec3 + sec4 + sec5
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
        "cat refinement",
        "cat-sweep review fixes + new roster (issues #900 #912 #913 #923)",
        body,
        badges=(("cats", "6 live + 3 new"), ("clips", str(n_clips)), ("fps", "8")),
        intro_html=intro,
        extra_css=EXTRA_CSS,
        extra_js=anim_js,
        verdict_key="cat_refinement:verdicts",
        export_name="cat_refinement_verdicts.json",
        footer_note=(
            "Recipe: NEVER ship side-view N/S (bipedal horror, issue #912). "
            "cat_purple retired per the 2026-07-26 review. kambu_placeholder "
            "will be superseded by the real Kambu spec (issue #923). "
            "No godot/ changes ride with this sheet."
        ),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    write_ascii(OUT, html)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB, {n_clips} clips)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
