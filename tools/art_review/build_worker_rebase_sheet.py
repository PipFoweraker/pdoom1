#!/usr/bin/env python3
"""build_worker_rebase_sheet -- worker re-base at the 64px standard (2026-07-26).

Review sheet for art_source/pixellab_2026-07-26_worker_rebase/: the sim-worker
roster regenerated at size 64 (92x92 canvas) after Pip's ruling that 64px made
every other comparison feel irrelevant. Per variant: 8-dir rotation strip,
walk/roll cycles with inline animated players, and the state pilot set.

PIL QC results (tools/art_review/qc_sprite_frames.py) are surfaced on the
sheet: alpha failures and limb-teleport continuity suspects get warn chips on
the affected cells.

Images embed as base64 data URIs so the single HTML survives being copied to
the main checkout. Builds on tools/art_review/review_style.py (house style,
completeness UX + verdict machinery). Pillow for QC; ASCII only.

Usage:  python tools/art_review/build_worker_rebase_sheet.py
Input:  art_source/pixellab_2026-07-26_worker_rebase/<variant>/...
Output: art_generated/worker_rebase_sheet.html
"""

import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import review_style as rs  # noqa: E402
from qc_sprite_frames import qc_batch  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "art_source" / "pixellab_2026-07-26_worker_rebase"
OUT = ROOT / "art_generated" / "worker_rebase_sheet.html"
RELROOT = "art_source/pixellab_2026-07-26_worker_rebase"

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

# display order + blurbs (briefed vs yes-and provenance mirrors MANIFEST.md)
VARIANTS = [
    ("worker_hijab_f", "briefed re-base: young South Asian woman, dark teal hijab"),
    ("worker_black_m", "briefed re-base: Black man, slate shirt, lanyard; state-pilot source"),
    ("worker_wheelchair_f", "briefed re-base: manual wheelchair; yes-and roll cycle"),
    ("worker_crutch_m", "briefed re-base: older East Asian man, forearm crutch (legibility watch)"),
    (
        "worker_crutch_m_v2",
        "yes-and alternate: crutch-in-every-view prompt; south grows a second stick",
    ),
    (
        "worker_glasses_badge_m",
        "briefed extension: glasses + lanyard + ID badge (probe accessory set)",
    ),
    ("worker_grey_f", "briefed extension: older woman, short grey hair"),
    ("worker_headphones_m", "yes-and: young Latino man, headphones around neck"),
    ("worker_black_m_state_working", "state pilot: seated typing"),
    ("worker_black_m_state_idle", "state pilot: standing idle with mug"),
    ("worker_black_m_state_stressed", "state pilot: hunched, hand to forehead"),
]

SCALE = 2  # display multiple (92 -> 184)


def data_uri(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def warn_chip(text):
    return f'<span class="qc-warn mono">[!] {rs.esc(text)}</span>'


def ok_chip(text):
    return f'<span class="qc-ok mono">[OK] {rs.esc(text)}</span>'


def rotations_row(variant: str, qc_alpha_frames):
    vdir = SRC / variant / "rotations"
    imgs = []
    for d in DIRS:
        p = vdir / f"{d}.png"
        if not p.exists():
            imgs.append(f'<div class="wr-missing">missing<br>{rs.esc(d)}</div>')
            continue
        rel = f"{variant}/rotations/{d}.png"
        warn = warn_chip("alpha") if rel in qc_alpha_frames else ""
        imgs.append(
            f'<div class="wr-frame"><img src="{data_uri(p)}" width="{92*SCALE}" '
            f'height="{92*SCALE}" alt="{rs.esc(d)}" title="{rs.esc(d)}">'
            f'<span class="wr-dir mono">{rs.esc(d)}</span>{warn}</div>'
        )
    return '<div class="wr-strip">' + "".join(imgs) + "</div>"


def anim_player(variant: str, anim: str, direction: str, frames, qc_alpha_frames, suspect_pairs):
    """Inline animated player + expandable filmstrip for one direction."""
    uris = [data_uri(p) for p in frames]
    pid = f"{variant}-{anim}-{direction}".replace("_", "-")
    strip = []
    for i, p in enumerate(frames):
        rel = f"{variant}/animations/{anim}/{direction}/{p.name}"
        chips = ""
        if rel in qc_alpha_frames:
            chips += warn_chip("alpha")
        if rel in suspect_pairs:
            chips += warn_chip("teleport?")
        strip.append(
            f'<div class="wr-fcell"><img src="{uris[i]}" width="92" height="92" '
            f'alt="f{i}"><span class="mono">f{i}</span>{chips}</div>'
        )
    rel_dir = f"{RELROOT}/{variant}/animations/{anim}/{direction}"
    any_warn = any(
        f"{variant}/animations/{anim}/{direction}/{p.name}" in suspect_pairs
        or f"{variant}/animations/{anim}/{direction}/{p.name}" in qc_alpha_frames
        for p in frames
    )
    head_warn = warn_chip("QC") if any_warn else ""
    return (
        f'<div class="wr-anim rs-cell" data-rel="{rs.esc(rel_dir)}">'
        f'<div class="wr-player"><img id="{pid}" src="{uris[0]}" width="{92*SCALE}" '
        f'height="{92*SCALE}" alt="{rs.esc(direction)}"></div>'
        f'<div class="rs-label mono">{rs.esc(direction)} ({len(frames)}f){head_warn}</div>'
        f'<div class="prompt-toggle" onclick="var b=this.nextElementSibling;'
        f"var on=b.classList.toggle('on');"
        f"this.textContent=on?'frames [-]':'frames [+]'\">frames [+]</div>"
        f'<div class="prompt-body wr-filmstrip">{"".join(strip)}</div>'
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
.qc-warn{color:#cc5a4a;font-size:9px;margin-left:4px;}
.qc-ok{color:#6fae5a;font-size:9px;margin-left:4px;}
.wr-qcline{font-size:11px;color:var(--dim);font-family:monospace;margin:6px 0;}
"""
)


def main() -> int:
    print("running PIL QC gate...")
    qc = qc_batch(str(SRC))
    sections = []
    total_frames = 0
    for variant, blurb in VARIANTS:
        vdir = SRC / variant
        if not vdir.is_dir():
            sections.append(rs.section(variant, '<p class="warn">folder missing</p>'))
            continue
        vqc = qc["variants"].get(variant, {})
        alpha_frames = {f["frame"] for f in vqc.get("alpha_failures", [])}
        suspect_frames = set()
        for s in vqc.get("continuity_suspects", []):
            suspect_frames.update(s["pair"])
        total_frames += vqc.get("frames", 0)
        qcline = (
            f"QC: {vqc.get('frames', 0)} frames, canvas "
            f"{vqc.get('canvas')}, "
            f"{len(vqc.get('alpha_failures', []))} alpha fails, "
            f"{len(vqc.get('continuity_suspects', []))} continuity suspects"
        )
        qchip = (
            ok_chip("clean")
            if not alpha_frames and not suspect_frames and vqc.get("canvas_ok", True)
            else warn_chip("see chips")
        )
        body = [f'<div class="wr-qcline">{rs.esc(qcline)} {qchip}</div>']
        # rotations as one verdict cell
        rel = f"{RELROOT}/{variant}/rotations"
        body.append(
            f'<div class="rs-cell" style="width:auto" data-rel="{rs.esc(rel)}">'
            + rotations_row(variant, alpha_frames)
            + '<div class="rs-label">rotations (8-dir stills)</div><div class="rs-vtags"></div></div>'
        )
        # animations
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
                        cells.append(
                            anim_player(variant, anim, d, frames, alpha_frames, suspect_frames)
                        )
                if cells:
                    body.append(
                        f'<div class="rs-label mono" style="text-align:left;margin-top:12px">'
                        f"animation: {rs.esc(anim)}</div>"
                        f'<div class="wr-anims">{"".join(cells)}</div>'
                    )
        sections.append(rs.section(variant, "".join(body), count=blurb, accent="#e0a34a"))
    intro = (
        "Worker re-base at the CONFIRMED 64px standard (92x92 canvas) -- Pip "
        "2026-07-26: 64px made all other comparisons feel irrelevant; the "
        "size-48 round-2 workers are superseded probes. Standard mode, low "
        "top-down, 8 directions. Walk cycles are template walks (8-dir); the "
        "crutch walk and wheelchair roll are v3 customs (4 cardinals). State "
        "pilot: working / idle / stressed on worker_black_m. PIL QC gate: "
        "clean alpha under feet + frame-continuity; warn chips mark suspects. "
        "Source + ids: art_source/pixellab_2026-07-26_worker_rebase/MANIFEST.md. "
        "Nothing is wired into godot/ -- variant-pool registry consumes AFTER triage."
    )
    html_text = rs.page(
        "worker re-base 64",
        "sim-worker roster at the 64px standard -- 2026-07-26",
        "".join(sections),
        badges=[
            ("variants", str(len(VARIANTS))),
            ("frames", str(total_frames)),
            ("canvas", "92x92"),
        ],
        intro_html=intro,
        extra_css=EXTRA_CSS,
        extra_js=ANIM_JS,
        verdict_key="worker_rebase_64:verdicts",
        export_name="worker_rebase_verdicts.json",
        footer_note="Animated players cycle at ~7 fps; expand [frames] for the filmstrip.",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rs.write_ascii(OUT, html_text)
    print(f"[OK] wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
