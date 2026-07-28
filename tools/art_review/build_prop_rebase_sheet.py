#!/usr/bin/env python3
"""build_prop_rebase_sheet -- prop re-base bulk batch + facing pilot (2026-07-27).

Review sheet for art_source/pixellab_2026-07-27_prop_rebase/ (queue items D+E
of the 2026-07-27 background art run, issues #900 #925): the full prop
catalog (water_cooler, filing_cabinet, server_cluster, desk, door) at
native-grain canvases, generated at 2x and downscaled with PIL LANCZOS (Pip's
"generate large then downscale" ruling), medium detail / medium shading (the
dial probe's winning detail level folded in as the default), plus the desk
facing-pilot (front-facing vs side-profile, scummy+decent).

Each cell shows the downscaled NATIVE render (the kept artifact) with the 2x
LARGE source expandable underneath for provenance / comparison.

Builds on tools/art_review/review_style.py (house style). ASCII only.

Usage:  python tools/art_review/build_prop_rebase_sheet.py
Output: art_generated/prop_rebase_sheet.html
"""

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_style as rs  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "art_source" / "pixellab_2026-07-27_prop_rebase"
NATIVE = SRC / "native"
LARGE = SRC / "large_source"
OUT = ROOT / "art_generated" / "prop_rebase_sheet.html"
RELROOT = "art_source/pixellab_2026-07-27_prop_rebase"

# section title -> list of file stems (without .png), in display order
SECTIONS = [
    ("D: water_cooler -- scummy", ["water_cooler_scummy_r1", "water_cooler_scummy_r2"]),
    ("D: water_cooler -- decent", ["water_cooler_decent_r1", "water_cooler_decent_r2"]),
    ("D: filing_cabinet -- scummy", ["filing_cabinet_scummy_r1", "filing_cabinet_scummy_r2"]),
    ("D: filing_cabinet -- decent", ["filing_cabinet_decent_r1", "filing_cabinet_decent_r2"]),
    ("D: server_cluster (single tier)", ["server_cluster_r1", "server_cluster_r2"]),
    (
        "D: desk -- scummy (RE-PROMPTED, desk surface must read)",
        ["desk_scummy_r1", "desk_scummy_r2"],
    ),
    ("D: desk -- decent", ["desk_decent_r1", "desk_decent_r2"]),
    ("D: door -- scummy", ["door_scummy_r1"]),
    ("D: door -- decent", ["door_decent_r1"]),
    (
        "E: desk facing pilot -- front-facing",
        ["desk_front_scummy_r1", "desk_front_decent_r1"],
    ),
    (
        "E: desk facing pilot -- side-profile",
        ["desk_side_scummy_r1", "desk_side_decent_r1"],
    ),
]


def data_uri(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode("ascii")


EXTRA_CSS = (
    """
/* .pr-cell is also .rs-cell (house verdict chrome), but rs-cell's fixed
   width was clipping wide props at x4 display (e.g. the 72x48 desk ->
   288x192) and overlapping the next card. Size the card to its content
   instead -- width:auto + max-width so a runaway image still wraps rather
   than overflowing. */
.pr-cell.rs-cell{width:auto;max-width:360px;}
.pr-cell{background:"""
    + rs.CHECKER
    + """;border-radius:5px;padding:8px;display:flex;flex-direction:column;
align-items:center;gap:4px;}
.pr-cell img{image-rendering:pixelated;display:block;max-width:100%;height:auto;}
.pr-native{border:2px solid var(--amber);border-radius:4px;padding:4px;background:#0000;
max-width:100%;box-sizing:border-box;}
.pr-native img{max-width:100%;height:auto;}
.pr-dims{font-size:9px;color:var(--dim);font-family:monospace;}
.pr-missing{color:#e0a0a0;font-family:monospace;font-size:11px;padding:20px;text-align:center;
border:1px dashed #cc5a4a;width:160px;}
.pr-ab{display:flex;gap:10px;align-items:flex-start;}
.pr-ab .pr-cell.rs-cell{width:auto;max-width:220px;}
.pr-ab-label{font-size:10px;color:var(--amber2);font-family:monospace;text-align:center;
margin-bottom:2px;text-transform:uppercase;letter-spacing:.5px;}
"""
)


def _downscale_variant(stem: str, suffix: str, native_p, label: str, method_note: str) -> str:
    """One downscale-method candidate card (own data-rel -> own verdict + note)."""
    from PIL import Image

    rel = f"{RELROOT}/native/{native_p.name}"
    nw, nh = Image.open(native_p).size
    scale = 4
    large_p = LARGE / f"{stem}.png"
    large_toggle = ""
    if large_p.exists():
        lw, lh = Image.open(large_p).size
        large_toggle = (
            '<div class="prompt-toggle" onclick="var b=this.nextElementSibling;'
            "var on=b.classList.toggle('on');"
            "this.textContent=on?'2x source [-]':'2x source [+]'\">2x source [+]</div>"
            f'<div class="prompt-body"><img src="{data_uri(large_p)}" '
            f'width="{lw}" height="{lh}" style="image-rendering:pixelated" '
            f'alt="{rs.esc(stem)} large"><div class="pr-dims">gen {lw}x{lh} -> '
            f"{method_note} -> {nw}x{nh}</div></div>"
        )
    return (
        f'<div class="pr-cell rs-cell" data-rel="{rs.esc(rel)}">'
        f'<div class="pr-ab-label">{rs.esc(label)}</div>'
        f'<div class="pr-native"><img src="{data_uri(native_p)}" '
        f'width="{nw*scale}" height="{nh*scale}" alt="{rs.esc(stem)} {label}"></div>'
        f'<div class="pr-dims">native {nw}x{nh} (x{scale} display)</div>'
        f'<div class="rs-label mono">{rs.esc(stem)}</div>'
        f"{large_toggle}"
        f'<div class="rs-vtags"></div>{rs.NOTE_HTML}</div>'
    )


def cell(stem: str) -> str:
    native_p = NATIVE / f"{stem}.png"
    nearest_p = NATIVE / f"{stem}_nearest.png"
    rel = f"{RELROOT}/native/{stem}.png"
    if not native_p.exists():
        return (
            f'<div class="pr-missing rs-cell" data-rel="{rs.esc(rel)}">'
            f'missing<br>{rs.esc(stem)}<div class="rs-vtags"></div></div>'
        )
    lanczos = _downscale_variant(
        stem, "lanczos", native_p, "lanczos (kept native)", "PIL LANCZOS downscale"
    )
    if nearest_p.exists():
        nearest = _downscale_variant(stem, "nearest", nearest_p, "nearest", "PIL NEAREST downscale")
    else:
        nearest = '<div class="pr-missing rs-cell">no nearest variant' f"<br>{rs.esc(stem)}</div>"
    return f'<div class="pr-ab">{lanczos}{nearest}</div>'


def main() -> int:
    sections = []
    total = 0
    for title, stems in SECTIONS:
        cells = [cell(s) for s in stems]
        total += len(stems)
        sections.append(
            section(
                title,
                '<div class="wr-anims" style="display:flex;flex-wrap:wrap;gap:12px">'
                + "".join(cells)
                + "</div>",
                count=f"{len(stems)} rolls",
                accent="#e0a34a",
            )
        )
    intro = (
        "2026-07-27 prop re-base (queue D) + desk facing pilot (queue E), issues "
        "#900 #925. All via create_map_object, view high top-down, outline single "
        "color outline, medium detail / medium shading (the 2026-07-26 dial probe's "
        "winning detail level, folded in as this run's default). GENERATE LARGE "
        "THEN DOWNSCALE per Pip's ruling: every prop is generated at 2x its native "
        "canvas then downscaled -- amber-bordered image is native-res; expand "
        "[2x source] to compare against the pre-downscale render. LANCZOS vs "
        "NEAREST A/B (2026-07-28 follow-up): the LANCZOS downscale reads muddy/soft "
        "next to the crisp native worker batch, so each roll now also shows a "
        "NEAREST-downscaled candidate from the same 2x source, side by side, each "
        "with its own verdict buttons -- rule which downscale method wins per prop. "
        "desk_scummy was RE-PROMPTED (not re-rolled verbatim) after the "
        "2026-07-26 vanguard flagged it as reading like a lone CRT with the desk "
        "surface lost -- the new prompt explicitly demands a wide visible desk "
        "surface on all sides of the monitor. Prop catalog is deliberately the 5 "
        "props that exist (water_cooler, filing_cabinet, server_cluster, desk, "
        "door -- 3 in props_manifest.json + desk/door net-new from the vanguard); "
        "breadth covers the whole catalog well inside the 450-gen cap -- see "
        "MANIFEST.md for the budget accounting."
    )
    html_text = rs.page(
        "prop re-base + facing pilot",
        "office prop catalog at native grain, 2x-gen + downscale -- 2026-07-27",
        "".join(sections),
        badges=[("rolls", str(total)), ("props", "5"), ("method", "2x + LANCZOS/NEAREST A/B")],
        intro_html=intro,
        extra_css=EXTRA_CSS,
        verdict_key="prop_rebase_20260727:verdicts",
        export_name="prop_rebase_verdicts.json",
        footer_note=(
            "Each roll shows a lanczos/nearest A/B pair (own data-rel, own verdict + "
            "note) so a per-prop downscale-method call is possible. Expand [2x source] "
            "per card for provenance."
        ),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rs.write_ascii(OUT, html_text)
    print(f"[OK] wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size/1e6:.2f} MB)")
    return 0


section = rs.section

if __name__ == "__main__":
    raise SystemExit(main())
