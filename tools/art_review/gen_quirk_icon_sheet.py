#!/usr/bin/env python3
"""Generate art_generated/quirk_icons_sheet.html -- quirk icon review sheet (issue #903).

Recreates the #909 lane's one-off inline sheet as a proper generator on the
shared review_style module (see tools/art_review/README.md). Inventory is the
SHIPPED 64px set under godot/assets/icons/quirks/<id>_64.png; metadata (display
name, valence theme, prompt) comes from art_prompts/quirk_icons.yaml and the
flavour blurbs from godot/data/researchers/quirks.json.

Cards are grouped by valence with the theme_manager.gd colour language:
positive=green, negative=crimson, double_edged=violet, state glyphs=grey-teal.
Each card: 128px display (2x upsample of the shipped 64), a 64/32/16 readability
row, the resolved generating prompt, and verdict chips (hide-on-verdict, export
JSON -> quirk_verdicts.json keyed by repo-relative path).

All images embed as base64 data URIs -- the emitted HTML is self-contained.

Usage:  python tools/art_review/gen_quirk_icon_sheet.py
Output: art_generated/quirk_icons_sheet.html   (regenerable, gitignored)
"""

import base64
import json
import os
import sys

import review_style as rs
import yaml

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
ICON_DIR = os.path.join(ROOT, "godot", "assets", "icons", "quirks")
YAML_PATH = os.path.join(ROOT, "art_prompts", "quirk_icons.yaml")
QUIRKS_JSON = os.path.join(ROOT, "godot", "data", "researchers", "quirks.json")
OUT = os.path.join(ROOT, "art_generated", "quirk_icons_sheet.html")

VALENCE_ORDER = ["positive", "double_edged", "negative", "neutral"]
VALENCE_COLORS = {
    "positive": "#33CC4D",  # theme "success"
    "double_edged": "#B380E6",  # theme "category_research" violet
    "negative": "#E64D33",  # theme "error"
    "neutral": "#7A9494",  # desaturated grey-teal (state glyphs)
}
THEME_TO_VALENCE = {
    "valence_positive": "positive",
    "valence_negative": "negative",
    "valence_double_edged": "double_edged",
    "valence_neutral": "neutral",
}


def b64(path):
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")


def resolve_full_prompt(data, asset):
    """style_overrides + color_bias + prompt_tail, same shape gen_hero_gallery uses."""
    styles = data.get("styles") or {}
    themes = data.get("themes") or {}
    th = themes.get(asset.get("theme") or "") or {}
    parts = [styles.get(ov, "") for ov in th.get("style_overrides") or []]
    if th.get("color_bias"):
        parts.append(th["color_bias"])
    parts.append(asset.get("prompt_tail") or "")
    return "  ".join(p.strip() for p in parts if p and p.strip())


def main():
    missing_inputs = [p for p in (ICON_DIR, YAML_PATH, QUIRKS_JSON) if not os.path.exists(p)]
    if missing_inputs:
        print("missing inputs: " + ", ".join(missing_inputs))
        return 1

    with open(YAML_PATH, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    with open(QUIRKS_JSON, encoding="utf-8") as fh:
        quirks_meta = json.load(fh).get("quirks", {})

    by_valence = {v: [] for v in VALENCE_ORDER}
    n_missing = 0
    for asset in data.get("assets") or []:
        aid = asset.get("id")
        if not aid:
            continue
        valence = THEME_TO_VALENCE.get(asset.get("theme") or "", "neutral")
        png = os.path.join(ICON_DIR, f"{aid}_64.png")
        exists = os.path.exists(png)
        if not exists:
            n_missing += 1
        qmeta = quirks_meta.get(aid) or {}
        blurb = qmeta.get("flavour") or (
            "??? -- hidden until revealed in play" if aid == "quirk_unrevealed" else ""
        )
        by_valence[valence].append(
            {
                "id": aid,
                "name": asset.get("display_name") or aid,
                "blurb": blurb,
                "prompt": resolve_full_prompt(data, asset),
                "uri": b64(png) if exists else "",
                "missing": not exists,
            }
        )

    sections = []
    total = 0
    for valence in VALENCE_ORDER:
        cards = by_valence[valence]
        if not cards:
            continue
        total += len(cards)
        accent = VALENCE_COLORS[valence]
        cells = []
        for c in cards:
            rel = f"godot/assets/icons/quirks/{c['id']}_64.png"
            cells.append(
                rs.image_cell(
                    src=c["uri"],
                    label=c["name"],
                    sublabel=c["id"],
                    size_row=[(64, c["uri"]), (32, c["uri"]), (16, c["uri"])] if c["uri"] else (),
                    blurb=c["blurb"] if not c["missing"] else "[!] 64px file missing on disk",
                    prompt=c["prompt"],
                    rel=rel,
                    accent=accent,
                    img_px=128,
                    missing=c["missing"],
                )
            )
        sections.append(
            rs.section(
                valence,
                f'<div class="rs-grid">{"".join(cells)}</div>',
                count=len(cards),
                accent=accent,
            )
        )

    intro = (
        "Valence colour language from theme_manager.gd: positive=green (success), "
        "negative=crimson (error), double_edged=violet purple (category_research), "
        "state glyphs=neutral grey-teal. Main image is a 2x upsample of the SHIPPED "
        "64px file; the 64/32/16 row is the real readability ladder. 1024px masters "
        "live in the generation archive (see docs/art/ART_MASTERS_POLICY.md), not in git."
    )
    html_text = rs.page(
        tool_name="quirk icon sheet",
        subtitle="14 quirks + 2 state glyphs -- issue #903",
        body_html="".join(sections),
        badges=[("icons", str(total)), ("model", "gpt-image-1.5")],
        intro_html=intro,
        verdict_key="quirk:verdicts",
        export_name="quirk_verdicts.json",
        footer_note=(
            "Exported paths are repo-relative (godot/assets/icons/quirks/...). "
            "Round-trip: export JSON -> PR comment -> fold into verdicts tracking."
        ),
    )

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rs.write_ascii(OUT, html_text)
    print(f"wrote {OUT} ({os.path.getsize(OUT) // 1024} KB, {total} icons, {n_missing} missing)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
