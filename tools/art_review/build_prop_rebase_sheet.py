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
.pr-cell{background:"""
    + rs.CHECKER
    + """;border-radius:5px;padding:8px;display:flex;flex-direction:column;
align-items:center;gap:4px;}
.pr-cell img{image-rendering:pixelated;display:block;}
.pr-native{border:2px solid var(--amber);border-radius:4px;padding:4px;background:#0000;}
.pr-dims{font-size:9px;color:var(--dim);font-family:monospace;}
.pr-missing{color:#e0a0a0;font-family:monospace;font-size:11px;padding:20px;text-align:center;
border:1px dashed #cc5a4a;width:160px;}
"""
)


def cell(stem: str) -> str:
    native_p = NATIVE / f"{stem}.png"
    large_p = LARGE / f"{stem}.png"
    rel = f"{RELROOT}/native/{stem}.png"
    if not native_p.exists():
        return (
            f'<div class="pr-missing rs-cell" data-rel="{rs.esc(rel)}">'
            f'missing<br>{rs.esc(stem)}<div class="rs-vtags"></div></div>'
        )
    from PIL import Image

    nw, nh = Image.open(native_p).size
    scale = 4
    native_img = (
        f'<div class="pr-native"><img src="{data_uri(native_p)}" '
        f'width="{nw*scale}" height="{nh*scale}" alt="{rs.esc(stem)}"></div>'
        f'<div class="pr-dims">native {nw}x{nh} (x{scale} display)</div>'
    )
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
            f"LANCZOS downscale -> {nw}x{nh}</div></div>"
        )
    return (
        f'<div class="pr-cell rs-cell" data-rel="{rs.esc(rel)}">'
        f"{native_img}"
        f'<div class="rs-label mono">{rs.esc(stem)}</div>'
        f"{large_toggle}"
        f'<div class="rs-vtags"></div></div>'
    )


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
        "canvas then downscaled with PIL LANCZOS -- amber-bordered image is the kept "
        "native artifact; expand [2x source] to compare against the pre-downscale "
        "render. desk_scummy was RE-PROMPTED (not re-rolled verbatim) after the "
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
        badges=[("rolls", str(total)), ("props", "5"), ("method", "2x + LANCZOS")],
        intro_html=intro,
        extra_css=EXTRA_CSS,
        verdict_key="prop_rebase_20260727:verdicts",
        export_name="prop_rebase_verdicts.json",
        footer_note="Amber border = kept native artifact. Expand [2x source] per cell for provenance.",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rs.write_ascii(OUT, html_text)
    print(f"[OK] wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size/1e6:.2f} MB)")
    return 0


section = rs.section

if __name__ == "__main__":
    raise SystemExit(main())
