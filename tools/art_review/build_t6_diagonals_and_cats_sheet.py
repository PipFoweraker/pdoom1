#!/usr/bin/env python3
"""build_t6_diagonals_and_cats_sheet -- lane T6 review sheet, 2026-07-27.

Covers two batches from the T6 art-generation lane:

  1. worker diagonal fill -- worker_wheelchair_f (roll) and worker_crutch_m
     (walk) gain the 4 missing diagonal directions (NE/NW/SE/SW), completing
     the 8-dir cycle the 2026-07-26 worker rebase scoped down to cardinals.
     art_source/pixellab_2026-07-27_t6_worker_diagonals/MANIFEST.md
  2. cat round -- tabby's side-heft diagonal MIXING PROBE gets a v3 refresh
     (paired against the original template probe for comparison), and
     eldritch gets a brand-new non-heft SIDE-VIEW character (the heft trio's
     eldritch member was universally disfavoured 2026-07-26).
     art_source/pixellab_2026-07-27_t6_cats/MANIFEST.md

Images embed as base64 data URIs so the sheet survives being copied to the
main checkout. Builds on tools/art_review/review_style.py. ASCII only.

Usage:  python tools/art_review/build_t6_diagonals_and_cats_sheet.py
Output: art_generated/t6_diagonals_and_cats_sheet.html
"""

import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_style as rs  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
WORKER_SRC = ROOT / "art_source" / "pixellab_2026-07-27_t6_worker_diagonals"
CAT_SRC = ROOT / "art_source" / "pixellab_2026-07-27_t6_cats"
OLD_CAT_SRC = ROOT / "art_source" / "pixellab_2026-07-26_cat_sweep"
OUT = ROOT / "art_generated" / "t6_diagonals_and_cats_sheet.html"

DIRS_8 = [
    "south",
    "south-east",
    "east",
    "north-east",
    "north",
    "north-west",
    "west",
    "south-west",
]
DIAG_4 = ["north-east", "south-east", "south-west", "north-west"]
NEW_DIAGS = {"north-east", "north-west", "south-east", "south-west"}


def data_uri(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def rotations_row(rot_dir: Path, px: int, scale: int):
    imgs = []
    for d in DIRS_8:
        p = rot_dir / f"{d}.png"
        if not p.exists():
            imgs.append(f'<div class="wr-missing">missing<br>{rs.esc(d)}</div>')
            continue
        imgs.append(
            f'<div class="wr-frame"><img src="{data_uri(p)}" width="{px*scale}" '
            f'height="{px*scale}" alt="{rs.esc(d)}" title="{rs.esc(d)}">'
            f'<span class="wr-dir mono">{rs.esc(d)}</span></div>'
        )
    return '<div class="wr-strip">' + "".join(imgs) + "</div>"


def anim_player(rel_root, char, anim, direction, frames, px, scale, is_new=False):
    uris = [data_uri(p) for p in frames]
    pid = f"{char}-{anim}-{direction}".replace("_", "-")
    strip = "".join(
        f'<div class="wr-fcell"><img src="{u}" width="{px}" height="{px}" '
        f'alt="f{i}"><span class="mono">f{i}</span></div>'
        for i, u in enumerate(uris)
    )
    rel_dir = f"{rel_root}/{char}/animations/{anim}/{direction}"
    new_chip = '<span class="t6-new mono">[NEW]</span>' if is_new else ""
    return (
        f'<div class="wr-anim rs-cell" data-rel="{rs.esc(rel_dir)}">'
        f'<div class="wr-player"><img id="{pid}" src="{uris[0]}" width="{px*scale}" '
        f'height="{px*scale}" alt="{rs.esc(direction)}"></div>'
        f'<div class="rs-label mono">{rs.esc(direction)} ({len(frames)}f){new_chip}</div>'
        f'<div class="prompt-toggle" onclick="var b=this.nextElementSibling;'
        f"var on=b.classList.toggle('on');"
        f"this.textContent=on?'frames [-]':'frames [+]'\">frames [+]</div>"
        f'<div class="prompt-body wr-filmstrip">{strip}</div>'
        f'<div class="rs-vtags"></div>'
        f'<script>(window.rsAnimQueue=window.rsAnimQueue||[]).push(["{pid}",{json.dumps(uris)}]);</script>'
        f"</div>"
    )


def worker_section(char: str, anim: str, blurb: str) -> str:
    cdir = WORKER_SRC / char
    body = [rotations_row(cdir / "rotations", 92, 2)]
    body.append(
        '<div class="rs-label mono" style="text-align:left;margin-top:12px">'
        f"animation: {rs.esc(anim)} (8/8 directions -- 4 NEW this lane)</div>"
    )
    cells = []
    for d in DIRS_8:
        ddir = cdir / "animations" / anim / d
        if not ddir.is_dir():
            continue
        frames = sorted(ddir.glob("*.png"), key=lambda p: p.name)
        if frames:
            cells.append(
                anim_player(
                    "art_source/pixellab_2026-07-27_t6_worker_diagonals",
                    char,
                    anim,
                    d,
                    frames,
                    92,
                    2,
                    is_new=(d in NEW_DIAGS),
                )
            )
    body.append(f'<div class="wr-anims">{"".join(cells)}</div>')
    return rs.section(char, "".join(body), count=blurb, accent="#e0a34a")


def tabby_probe_section() -> str:
    """Pair each diagonal: OLD template probe vs NEW v3 refresh."""
    old_dir = OLD_CAT_SRC / "cat_b2_tabby_side_heft" / "animations" / "walk_side_diag_probe"
    new_dir = CAT_SRC / "cat_b2_tabby_side_heft" / "animations" / "walk_side_diag_v3refresh"
    rows = []
    for d in DIAG_4:
        pair_cells = []
        od = old_dir / d
        if od.is_dir():
            frames = sorted(od.glob("*.png"), key=lambda p: p.name)
            pair_cells.append(
                anim_player(
                    "art_source/pixellab_2026-07-26_cat_sweep",
                    "cat_b2_tabby_side_heft",
                    "walk_side_diag_probe",
                    d,
                    frames,
                    68,
                    3,
                )
            )
        nd = new_dir / d
        if nd.is_dir():
            frames = sorted(nd.glob("*.png"), key=lambda p: p.name)
            pair_cells.append(
                anim_player(
                    "art_source/pixellab_2026-07-27_t6_cats",
                    "cat_b2_tabby_side_heft",
                    "walk_side_diag_v3refresh",
                    d,
                    frames,
                    68,
                    3,
                    is_new=True,
                )
            )
        rows.append(
            f'<div class="t6-pairrow"><div class="t6-pairhead mono">{rs.esc(d)}'
            f" -- template probe (2026-07-26) vs v3 refresh (NEW)</div>"
            f'<div class="wr-anims">{"".join(pair_cells)}</div></div>'
        )
    body = "".join(rows)
    return rs.section(
        "cat_b2_tabby_side_heft -- diagonal mixing-boundary probe refresh",
        body,
        count="4 directions paired: original template probe vs v3 refresh",
        accent="#c98b3f",
    )


def eldritch_section() -> str:
    cdir = CAT_SRC / "cat_eldritch_side_original"
    body = [rotations_row(cdir / "rotations", 68, 3)]
    body.append(
        '<div class="rs-label mono" style="text-align:left;margin-top:12px">'
        "animation: walk_ew_diag (E/W + 4 diagonals, N/S deliberately skipped"
        " -- side-view N/S is the never-ship bipedal-horror rule, issue #912)</div>"
    )
    cells = []
    for d in ["east", "west", "north-east", "south-east", "south-west", "north-west"]:
        ddir = cdir / "animations" / "walk_ew_diag" / d
        if ddir.is_dir():
            frames = sorted(ddir.glob("*.png"), key=lambda p: p.name)
            cells.append(
                anim_player(
                    "art_source/pixellab_2026-07-27_t6_cats",
                    "cat_eldritch_side_original",
                    "walk_ew_diag",
                    d,
                    frames,
                    68,
                    3,
                    is_new=True,
                )
            )
    body.append(f'<div class="wr-anims">{"".join(cells)}</div>')
    bf_dir = cdir / "animations" / "butt_flash_north" / "north"
    if bf_dir.is_dir():
        frames = sorted(bf_dir.glob("*.png"), key=lambda p: p.name)
        body.append(
            '<div class="rs-label mono" style="text-align:left;margin-top:12px">'
            "animation: butt_flash_north (new identity -> gets one per locked rule,"
            " issue #913; splice frames ~2-8, dont loop all 9)</div>"
        )
        body.append(
            '<div class="wr-anims">'
            + anim_player(
                "art_source/pixellab_2026-07-27_t6_cats",
                "cat_eldritch_side_original",
                "butt_flash_north",
                "north",
                frames,
                68,
                3,
                is_new=True,
            )
            + "</div>"
        )
    return rs.section(
        "cat_eldritch_side_original -- NEW non-heft side-view character",
        "".join(body),
        count="8 rotations + 6-dir walk + butt-flash, all NEW",
        accent="#5a8fc0",
    )


ANIM_JS = r"""
window.rsAnimQueue=window.rsAnimQueue||[];
window.addEventListener('DOMContentLoaded',function(){
  for(const [id,frames] of window.rsAnimQueue){
    const el=document.getElementById(id);if(!el||frames.length<2)continue;
    let i=0;setInterval(()=>{i=(i+1)%frames.length;el.src=frames[i];},140);
  }
});
"""

EXTRA_CSS = (
    """
.wr-strip{display:flex;flex-wrap:wrap;gap:10px;padding:10px;border:1px solid var(--line);
border-radius:6px;background:"""
    + rs.CHECKER
    + """;}
.wr-strip img,.wr-player img,.wr-fcell img{image-rendering:pixelated;display:block;}
.wr-frame{display:flex;flex-direction:column;align-items:center;gap:2px;}
.wr-dir{font-size:9px;color:var(--dim);}
.wr-missing{display:flex;align-items:center;justify-content:center;width:184px;height:184px;
color:#e0a0a0;border:1px dashed #cc5a4a;font-family:monospace;font-size:10px;text-align:center;}
.wr-anims{display:flex;flex-wrap:wrap;gap:12px;margin-top:10px;}
.wr-anim{width:220px;}
.wr-player{background:"""
    + rs.CHECKER
    + """;border-radius:5px;display:flex;
align-items:center;justify-content:center;align-self:center;}
.wr-filmstrip{display:flex;flex-wrap:wrap;gap:4px;max-height:260px;}
.wr-fcell{display:flex;flex-direction:column;align-items:center;font-size:8px;color:var(--dim);}
.t6-new{color:#6fae5a;margin-left:4px;}
.t6-pairrow{margin-top:14px;border-top:1px dashed var(--line);padding-top:8px;}
.t6-pairhead{font-size:11px;color:var(--amber2);margin-bottom:4px;}
"""
)


def main() -> int:
    sections = [
        worker_section(
            "worker_wheelchair_f",
            "roll",
            "manual wheelchair roll -- 4 diagonals appended to the 2026-07-26 v3 group",
        ),
        worker_section(
            "worker_crutch_m",
            "walk",
            "forearm crutch walk -- 4 diagonals appended to the 2026-07-26 v3 group",
        ),
        tabby_probe_section(),
        eldritch_section(),
    ]
    intro = (
        "Lane T6, 2026-07-27 -- two batches. (1) Worker diagonal fill: "
        "worker_wheelchair_f (roll) and worker_crutch_m (walk) complete their "
        "8-direction cycles -- the 2026-07-26 rebase scoped v3 customs down to "
        "4 cardinals; this lane appends the 4 diagonals to the SAME animation "
        "groups at the same v3 profile (9f, 92x92). NEW chip marks the 4 "
        "appended directions per character; cardinals are unchanged. "
        "(2) Cat round per the locked next-round rules (heft everywhere "
        "EXCEPT eldritch; no licking/sitting; butt-flash for new identities): "
        "tabby's side-heft diagonal MIXING-BOUNDARY PROBE gets a v3 refresh, "
        "paired against the original template probe per direction; eldritch "
        "gets a brand-new NON-HEFT side-view character (the heft trio's "
        "eldritch member was disfavoured across every direction on "
        "2026-07-26) with a 6-direction walk (N/S skipped -- side-view N/S is "
        "the never-ship bipedal-horror rule) plus butt_flash_north. "
        "Sources: art_source/pixellab_2026-07-27_t6_worker_diagonals/MANIFEST.md, "
        "art_source/pixellab_2026-07-27_t6_cats/MANIFEST.md."
    )
    html_text = rs.page(
        "T6 diagonals + cats",
        "worker diagonal fill + tabby refresh + eldritch non-heft side -- 2026-07-27",
        "".join(sections),
        badges=[
            ("worker gens", "16"),
            ("cat gens", "12"),
            ("total gens", "28"),
        ],
        intro_html=intro,
        extra_css=EXTRA_CSS,
        extra_js=ANIM_JS,
        verdict_key="t6_diagonals_and_cats_20260727:verdicts",
        export_name="t6_diagonals_and_cats_verdicts.json",
        footer_note="Animated players cycle at ~7 fps; expand [frames] for the filmstrip. "
        "[NEW] chips mark content generated in this lane.",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rs.write_ascii(OUT, html_text)
    print(f"[OK] wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
