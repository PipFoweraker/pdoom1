#!/usr/bin/env python3
"""
Rebuild tools/assets/review_generated.html from whatever PNGs are on disk under
art_generated/. Standalone output: inline CSS, relative image paths, ASCII only,
no external asset refs. Open the HTML directly in a browser.

Ordering: featured (newest) manifests first as their own sections, then the
remaining prior-run assets grouped by art_generated/<asset_type>/v1/ directory.
Each asset collapses its output sizes into one representative thumbnail; the
caption lists every size present. Alpha shows against the CSS checkered backdrop.

Usage:
  python tools/assets/build_review_gallery.py

The featured manifests are listed in FEATURED below; add a manifest there to give
its assets a dedicated top section. Everything else is auto-discovered.
"""

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ART = REPO / "art_generated"
OUT = REPO / "tools" / "assets" / "review_generated.html"

# Featured manifests, newest first. Each becomes a dedicated top section using
# the manifest's own asset order + display names. (path, section title, subtitle,
# representative-width target, big-card?)
FEATURED = [
    (
        "tools/assets/manifests/hero_banners.json",
        "hero_banners -- key-art OPTIONS (NEW this run)",
        "6 deliberately different hero/key-art directions for the website + itch page, "
        "gpt-image-1.5 @ 1536x1024, background=opaque. Pick a direction. "
        "Grounded in docs/art/PALETTE_AND_DOOM_INTENSITY.md.",
        768,
        True,
    ),
    (
        "tools/assets/manifests/icons_v2.json",
        "icons_v2 -- expanded action + resource icons (NEW this run)",
        "Action-menu and resource icons beyond the original 6, gpt-image-1.5 with "
        "background=transparent (checkered backdrop shows real alpha). Same brand "
        "style as icons_v1. Ids grounded in godot/data/actions/*.json + game_state.gd.",
        256,
        True,
    ),
    (
        "tools/assets/manifests/icons_v1.json",
        "icons_v1 -- palette-grounded resource icons",
        "The original 6 resource icons (doom/compute/money/reputation/papers/governance), "
        "gpt-image-1.5 with background=transparent. Grounded in docs/art/palette.json.",
        256,
        True,
    ),
]

SIZE_RE = re.compile(r"^(?P<base>.+)_(?P<w>\d+)\.png$")


def scan_dir(v1_dir):
    """Group PNGs in a dir by base id -> sorted list of widths present."""
    assets = {}
    if not v1_dir.is_dir():
        return assets
    for p in v1_dir.glob("*.png"):
        m = SIZE_RE.match(p.name)
        if not m:
            continue
        base = m.group("base")
        assets.setdefault(base, []).append(int(m.group("w")))
    for base in assets:
        assets[base] = sorted(set(assets[base]))
    return assets


def pick_width(widths, target):
    """Width closest to target that exists (ties -> smaller)."""
    return min(widths, key=lambda w: (abs(w - target), w))


def rel(path):
    """Relative path from tools/assets/ to an art_generated file, forward slashes."""
    return "../../" + str(path.relative_to(REPO)).replace("\\", "/")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(v1_dir, base, widths, target, big, label=None):
    show_w = pick_width(widths, target)
    img = v1_dir / f"{base}_{show_w}.png"
    if not img.exists():
        return ""
    sizes = ",".join(str(w) for w in widths)
    cls = "card big" if big else "card"
    name = esc(label) if label else esc(base)
    return (
        f'<figure class="{cls}"><div class="thumb"><img loading="lazy" '
        f'src="{rel(img)}" alt="{esc(base)}"></div><figcaption>'
        f'<span class="id">{name}</span>'
        f'<span class="meta">shown@{show_w} &middot; sizes {sizes}</span>'
        f"</figcaption></figure>"
    )


def main():
    sections = []  # (anchor_label, html)
    featured_bases = {}  # asset_type -> set(base ids) already shown up top

    # ---- Featured sections (newest first) ----
    for rel_path, title, sub, target, big in FEATURED:
        mpath = REPO / rel_path
        if not mpath.exists():
            continue
        data = json.loads(mpath.read_text(encoding="utf-8"))
        atype = data.get("asset_type", "unknown")
        v1_dir = ART / atype / "v1"
        disk = scan_dir(v1_dir)
        cards = []
        shown = 0
        for a in data.get("assets", []):
            base = a.get("id")
            if base in disk:
                cards.append(card(v1_dir, base, disk[base], target, big, a.get("display_name")))
                featured_bases.setdefault(atype, set()).add(base)
                shown += 1
        grid_cls = "grid hero"
        body = (
            f'<h2>{esc(title)}</h2><p class="sub">{esc(sub)}</p>\n'
            f'<div class="{grid_cls}">\n' + "\n".join(c for c in cards if c) + "\n</div>"
        )
        if shown == 0:
            body = (
                f'<h2>{esc(title)}</h2><p class="sub">{esc(sub)}</p>\n'
                f'<p class="empty">No PNGs on disk yet (manifest not generated).</p>'
            )
        sections.append((f"{title.split(' ')[0]} ({shown})", body))

    # ---- Prior-run sections: every art_generated/<type>/v1 dir ----
    if ART.is_dir():
        for type_dir in sorted(p for p in ART.iterdir() if p.is_dir()):
            atype = type_dir.name
            if atype == "logs":
                continue
            v1_dir = type_dir / "v1"
            disk = scan_dir(v1_dir)
            exclude = featured_bases.get(atype, set())
            bases = sorted(b for b in disk if b not in exclude)
            if not bases:
                continue
            # representative target: icons small, textures/backgrounds larger
            target = 256 if "icon" in atype else 512
            cards = [card(v1_dir, b, disk[b], target, False) for b in bases]
            cards = [c for c in cards if c]
            body = (
                f"<h2>{esc(atype)} (prior runs)</h2>"
                f'<p class="sub">{len(cards)} asset(s) on disk</p>\n'
                f'<div class="grid">\n' + "\n".join(cards) + "\n</div>"
            )
            sections.append((f"{atype} ({len(cards)})", body))

    # ---- Assemble ----
    nav = "".join(f'<a href="#sec{i}">{esc(lbl)}</a>' for i, (lbl, _) in enumerate(sections))
    secs = "\n".join(
        f'<section id="sec{i}">{html}</section>' for i, (_, html) in enumerate(sections)
    )
    total = sum(html.count("<figure") for _, html in sections)

    page = f"""<!-- pdoom1 generated-art review gallery. Standalone, inline CSS,
relative image paths, ASCII only. Regenerated by tools/assets/build_review_gallery.py.
Open directly in a browser (double-click). Images load from art_generated/ (gitignored, on disk). -->
<title>P(Doom)1 -- generated-art review</title>
<style>
:root{{color-scheme:light dark;--bg:#14121a;--panel:#1e1b28;--ink:#ece0cf;
--muted:#9a90a6;--line:#332c40;--accent:#b07bd6;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif}}
header{{padding:22px 26px;border-bottom:1px solid var(--line);position:sticky;top:0;
background:linear-gradient(180deg,#1b1826,#14121a);z-index:5}}
header h1{{margin:0 0 4px;font-size:20px;letter-spacing:.3px}}
header p{{margin:0;color:var(--muted);font-size:13px}}
nav{{padding:10px 26px;border-bottom:1px solid var(--line);position:sticky;top:64px;
background:var(--bg);z-index:4;display:flex;flex-wrap:wrap;gap:8px}}
nav a{{color:var(--accent);text-decoration:none;font-size:12px;padding:3px 9px;
border:1px solid var(--line);border-radius:20px}}
nav a:hover{{border-color:var(--accent)}}
section{{padding:20px 26px;border-bottom:1px solid var(--line)}}
section h2{{font-size:16px;margin:0 0 3px}}
section .sub{{color:var(--muted);font-size:12px;margin:0 0 16px}}
.grid{{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}}
.grid.hero{{grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:10px;
overflow:hidden;display:flex;flex-direction:column}}
.thumb{{display:flex;align-items:center;justify-content:center;padding:10px;
min-height:150px;
background-image:linear-gradient(45deg,#2a2733 25%,transparent 25%),
linear-gradient(-45deg,#2a2733 25%,transparent 25%),
linear-gradient(45deg,transparent 75%,#2a2733 75%),
linear-gradient(-45deg,transparent 75%,#2a2733 75%);
background-size:20px 20px;background-position:0 0,0 10px,10px -10px,-10px 0}}
.card.big .thumb{{min-height:230px}}
.thumb img{{max-width:100%;max-height:210px;image-rendering:auto}}
.card.big .thumb img{{max-height:300px}}
figcaption{{padding:8px 10px;border-top:1px solid var(--line);display:flex;
flex-direction:column;gap:2px}}
.id{{font-size:12px;word-break:break-all}}
.meta{{font-size:10px;color:var(--muted)}}
.empty{{color:var(--muted);font-style:italic;font-size:13px}}
</style>

<header><h1>P(Doom)1 &mdash; generated-art review</h1><p>{total} asset thumbnails, newest sets first. One representative size shown per asset; all output sizes listed in each caption. Images load from <code>art_generated/</code> (gitignored, on disk). Checkered backdrop reveals real alpha.</p></header>
<nav>{nav}</nav>
{secs}
"""
    OUT.write_text(page, encoding="ascii", errors="strict")
    print(f"Wrote {OUT} -- {total} figures across {len(sections)} sections.")


if __name__ == "__main__":
    main()
