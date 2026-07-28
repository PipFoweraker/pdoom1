#!/usr/bin/env python3
"""build_cat_west_walk_picks -- 2026-07-27 cat_sweep_black_side_heft WEST walk pick sheet.

Queue item C of the 2026-07-27 background art run (issues #900 #913): the
cat_sweep_black_side_heft west-facing walk had problems on the 2026-07-26
sweep, so this generates fresh WEST-direction variants for a side-by-side
pick. All variants animate the SAME character/rotation
(cat_sweep_black_side_heft, id 55bf4986), so they are directly comparable --
only the animation job differs:

  * walk_ew (baseline)     -- the ORIGINAL 2026-07-26 walk-8-frames template
                               west clip (the one flagged as having problems)
  * walk_west_cleanfix     -- a pre-existing 2026-07-26 v3 custom "clean fix"
                               attempt (kept for comparison, not new spend)
  * west_walk_v3_template6 -- NEW: walk-6-frames template (different frame
                               count template -- distinct generation)
  * west_walk_v4_v3custom  -- NEW: v3 custom, "thick barrel body swaying"
  * west_walk_v5_v3custom  -- NEW: v3 custom, "slow deliberate pace, firm
                               planting steps"

Built on tools/art_review/review_style.py. ASCII only.

Usage:  python tools/art_review/build_cat_west_walk_picks.py
Output: art_generated/cat_west_walk_picks.html
"""

import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_style as rs  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "art_source" / "pixellab_2026-07-27_cat_west_variants" / "cat_sweep_black_side_heft"
OUT = ROOT / "art_generated" / "cat_west_walk_picks.html"
RELROOT = "art_source/pixellab_2026-07-27_cat_west_variants/cat_sweep_black_side_heft"

VARIANTS = [
    ("walk_ew", "BASELINE (2026-07-26): walk-8-frames template, the flagged-problem clip"),
    ("walk_west_cleanfix", "prior attempt (2026-07-26): v3 custom clean fix"),
    ("west_walk_v3_template6", "NEW: walk-6-frames template (6f, different template)"),
    ("west_walk_v4_v3custom", "NEW: v3 custom -- thick barrel body swaying, weighty steps"),
    ("west_walk_v5_v3custom", "NEW: v3 custom -- slow deliberate pace, firm planting steps"),
]

SCALE = 3  # 68px char -> 204px display


def data_uri(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def variant_cell(anim: str, blurb: str) -> str:
    ddir = SRC / "animations" / anim / "west"
    if not ddir.is_dir():
        return f'<div class="pk-missing">missing<br>{rs.esc(anim)}</div>'
    frames = sorted(ddir.glob("*.png"), key=lambda p: p.name)
    uris = [data_uri(p) for p in frames]
    pid = f"pick-{anim}".replace("_", "-")
    rel = f"{RELROOT}/animations/{anim}/west"
    strip = "".join(
        f'<div class="wr-fcell"><img src="{u}" width="68" height="68" alt="f{i}">'
        f'<span class="mono">f{i}</span></div>'
        for i, u in enumerate(uris)
    )
    return (
        f'<div class="pk-cell rs-cell" data-rel="{rs.esc(rel)}">'
        f'<div class="wr-player"><img id="{pid}" src="{uris[0]}" width="{68*SCALE}" '
        f'height="{68*SCALE}" alt="west"></div>'
        f'<div class="rs-label mono">{rs.esc(anim)}</div>'
        f'<div class="rs-blurb">{rs.esc(blurb)}</div>'
        f'<div class="pk-fcount mono">{len(frames)} frames</div>'
        f'<div class="prompt-toggle" onclick="var b=this.nextElementSibling;'
        f"var on=b.classList.toggle('on');"
        f"this.textContent=on?'frames [-]':'frames [+]'\">frames [+]</div>"
        f'<div class="prompt-body wr-filmstrip">{strip}</div>'
        f'<div class="rs-vtags"></div>{rs.NOTE_HTML}'
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
.pk-row{display:flex;flex-wrap:wrap;gap:16px;padding:6px 0;}
.pk-cell{width:240px;}
.pk-missing{width:204px;height:204px;display:flex;align-items:center;justify-content:center;
color:#e0a0a0;border:1px dashed #cc5a4a;font-family:monospace;font-size:11px;text-align:center;}
.wr-player{background:"""
    + rs.CHECKER
    + """;border-radius:5px;display:flex;align-items:center;justify-content:center;
align-self:center;}
.wr-player img,.wr-fcell img{image-rendering:pixelated;display:block;}
.wr-filmstrip{display:flex;flex-wrap:wrap;gap:4px;max-height:220px;}
.wr-fcell{display:flex;flex-direction:column;align-items:center;font-size:8px;color:var(--dim);}
.pk-fcount{font-size:9px;color:var(--dim);margin-top:2px;}
"""
)


def main() -> int:
    cells = [variant_cell(anim, blurb) for anim, blurb in VARIANTS]
    body = f'<div class="pk-row">{"".join(cells)}</div>'
    sections = rs.section(
        "cat_sweep_black_side_heft -- WEST walk, 5 variants",
        body,
        count=f"{len(VARIANTS)} variants",
        accent="#e0a34a",
    )
    intro = (
        "2026-07-27 background art run, queue C (issues #900 #913): "
        "cat_sweep_black_side_heft's WEST-direction walk had problems on the "
        "2026-07-26 cat sweep. Five variants of the SAME character/rotation "
        "animated west, for a direct side-by-side pick -- pick one (or none, "
        "keep baseline) via the promote/favour verdict chips. Baseline + "
        "cleanfix are the pre-existing 2026-07-26 clips (not re-spent); the "
        "3 template6/v3custom variants are new generations from this run. "
        "Source: art_source/pixellab_2026-07-27_cat_west_variants/MANIFEST.md."
    )
    html_text = rs.page(
        "cat west walk -- pick sheet",
        "cat_sweep_black_side_heft WEST walk variants -- 2026-07-27",
        sections,
        badges=[("variants", str(len(VARIANTS))), ("direction", "west"), ("canvas", "68x68")],
        intro_html=intro,
        extra_css=EXTRA_CSS,
        extra_js=ANIM_JS,
        verdict_key="cat_west_walk_picks_20260727:verdicts",
        export_name="cat_west_walk_picks_verdicts.json",
        footer_note="Animated players cycle at ~7 fps; expand [frames] for the filmstrip.",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rs.write_ascii(OUT, html_text)
    print(f"[OK] wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size/1e3:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
