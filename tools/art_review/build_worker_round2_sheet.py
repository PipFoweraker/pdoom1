#!/usr/bin/env python3
"""build_worker_round2_sheet -- 2026-07-27 worker reroll + fresh worker (A+B).

Review sheet for art_source/pixellab_2026-07-27_worker_round2/:
  A. worker_headphones_m_r2 -- reroll of worker_headphones_m, hardened prompt
     so the large over-ear headphones are visible in every rotation (Pip's
     dislike on the 2026-07-26 round was invisible headphones).
  B. worker_grey_black_f -- fresh worker pool addition: older Black woman,
     short grey hair, office worker.

Same house params as the 2026-07-26 worker rebase (issue #900 #793):
create_character standard mode, humanoid, size 64 (92x92 canvas), low
top-down, 8 directions, single color black outline, high detail, basic
shading, template walk (8-dir, 6 frames/direction).

Built on tools/art_review/review_style.py; images embed as data URIs so the
sheet survives being copied elsewhere. ASCII only.

Usage:  python tools/art_review/build_worker_round2_sheet.py
Output: art_generated/worker_round2_sheet.html
"""

import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_style as rs  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "art_source" / "pixellab_2026-07-27_worker_round2"
OUT = ROOT / "art_generated" / "worker_round2_sheet.html"
RELROOT = "art_source/pixellab_2026-07-27_worker_round2"

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

VARIANTS = [
    (
        "worker_headphones_m_r2",
        "REROLL (A): headphones hardened -- large over-ear cups + visible band, "
        "must read in every rotation (2026-07-26 dislike: sometimes invisible)",
    ),
    (
        "worker_grey_black_f",
        "FRESH (B): older Black woman, short natural grey hair, cardigan, "
        "reading glasses -- worker pool addition",
    ),
]

SCALE = 2  # display multiple (92 -> 184)


def data_uri(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def rotations_row(variant: str):
    vdir = SRC / variant / "rotations"
    imgs = []
    for d in DIRS:
        p = vdir / f"{d}.png"
        if not p.exists():
            imgs.append(f'<div class="wr-missing">missing<br>{rs.esc(d)}</div>')
            continue
        imgs.append(
            f'<div class="wr-frame"><img src="{data_uri(p)}" width="{92*SCALE}" '
            f'height="{92*SCALE}" alt="{rs.esc(d)}" title="{rs.esc(d)}">'
            f'<span class="wr-dir mono">{rs.esc(d)}</span></div>'
        )
    return '<div class="wr-strip">' + "".join(imgs) + "</div>"


def anim_player(variant: str, anim: str, direction: str, frames):
    uris = [data_uri(p) for p in frames]
    pid = f"{variant}-{anim}-{direction}".replace("_", "-")
    strip = "".join(
        f'<div class="wr-fcell"><img src="{uris[i]}" width="92" height="92" '
        f'alt="f{i}"><span class="mono">f{i}</span></div>'
        for i in range(len(frames))
    )
    rel_dir = f"{RELROOT}/{variant}/animations/{anim}/{direction}"
    return (
        f'<div class="wr-anim rs-cell" data-rel="{rs.esc(rel_dir)}">'
        f'<div class="wr-player"><img id="{pid}" src="{uris[0]}" width="{92*SCALE}" '
        f'height="{92*SCALE}" alt="{rs.esc(direction)}"></div>'
        f'<div class="rs-label mono">{rs.esc(direction)} ({len(frames)}f)</div>'
        f'<div class="prompt-toggle" onclick="var b=this.nextElementSibling;'
        f"var on=b.classList.toggle('on');"
        f"this.textContent=on?'frames [-]':'frames [+]'\">frames [+]</div>"
        f'<div class="prompt-body wr-filmstrip">{strip}</div>'
        f'<div class="rs-vtags"></div>'
        f'<script>(window.rsAnimQueue=window.rsAnimQueue||[]).push(["{pid}",{json.dumps(uris)}]);</script>'
        f"</div>"
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
"""
)


def main() -> int:
    sections = []
    total_frames = 0
    for variant, blurb in VARIANTS:
        vdir = SRC / variant
        if not vdir.is_dir():
            sections.append(rs.section(variant, '<p class="warn">folder missing</p>'))
            continue
        body = []
        rel = f"{RELROOT}/{variant}/rotations"
        body.append(
            f'<div class="rs-cell" style="width:auto" data-rel="{rs.esc(rel)}">'
            + rotations_row(variant)
            + '<div class="rs-label">rotations (8-dir stills)</div><div class="rs-vtags"></div></div>'
        )
        anim_root = vdir / "animations"
        if anim_root.is_dir():
            for anim in sorted(p.name for p in anim_root.iterdir() if p.is_dir()):
                cells = []
                for d in DIRS:
                    ddir = anim_root / anim / d
                    if not ddir.is_dir():
                        continue
                    frames = sorted(ddir.glob("*.png"), key=lambda p: p.name)
                    if frames:
                        total_frames += len(frames)
                        cells.append(anim_player(variant, anim, d, frames))
                if cells:
                    body.append(
                        f'<div class="rs-label mono" style="text-align:left;margin-top:12px">'
                        f"animation: {rs.esc(anim)}</div>"
                        f'<div class="wr-anims">{"".join(cells)}</div>'
                    )
        sections.append(rs.section(variant, "".join(body), count=blurb, accent="#e0a34a"))
    intro = (
        "2026-07-27 background art run, queue A+B: worker_headphones_m REROLL "
        "(hardened prompt for headphone visibility) and worker_grey_black_f FRESH "
        "worker-pool addition. Same 64px standard as the 2026-07-26 rebase (92x92 "
        "canvas), 8-dir template walk. Nothing wired into godot/ -- variant-pool "
        "registry consumes after Pip's triage. Source + params: "
        "art_source/pixellab_2026-07-27_worker_round2/MANIFEST.md."
    )
    html_text = rs.page(
        "worker round 2 -- headphones reroll + grey_black_f",
        "2026-07-27 background art run, queue A+B",
        "".join(sections),
        badges=[
            ("variants", str(len(VARIANTS))),
            ("frames", str(total_frames)),
            ("canvas", "92x92"),
        ],
        intro_html=intro,
        extra_css=EXTRA_CSS,
        extra_js=ANIM_JS,
        verdict_key="worker_round2_20260727:verdicts",
        export_name="worker_round2_verdicts.json",
        footer_note="Animated players cycle at ~7 fps; expand [frames] for the filmstrip.",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rs.write_ascii(OUT, html_text)
    print(f"[OK] wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
