#!/usr/bin/env python3
"""
Extract a brand palette from an image (default: the P(Doom)1 hero background).

Part of the no-spend asset-generation pipeline: the palette it emits grounds the
generation manifests (icons/textures) so a whole set reads as one colour system,
and the swatch page lets Pip eyeball + rename the roles.

Method: PIL adaptive quantise (median-cut) over the actual pixels of a downscaled
copy of the image, then sort the resulting palette by pixel frequency and label
each colour with a best-guess role from its HSV coordinates. Nothing here calls a
network or an image API -- it only reads local pixels.

Usage:
    python tools/assets/extract_palette.py <image> [--n 24]
    python tools/assets/extract_palette.py godot/assets/dump_october_31_2025/hero-bg-2400w.webp --n 24

Outputs (relative to repo root, override with flags):
    docs/art/palette.json                  -- [{hex, rgb, role_guess, weight_pct}, ...]
    tools/art_review/palette_swatches.html -- standalone swatch page (no external assets)
"""

import argparse
import colorsys
import json
import sys
from pathlib import Path

# Repo root is two levels up from tools/assets/extract_palette.py
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSON = REPO_ROOT / "docs" / "art" / "palette.json"
DEFAULT_HTML = REPO_ROOT / "tools" / "art_review" / "palette_swatches.html"

# Downscale the longest edge to this before quantising -- keeps it fast while
# preserving the colour distribution (quantise samples pixels, not detail).
SAMPLE_MAX_EDGE = 400


def guarded_pillow():
    """Import Pillow, or print the install line and exit non-zero (no crash)."""
    try:
        from PIL import Image  # noqa: F401

        return Image
    except ImportError:
        print("Pillow (PIL) is required for palette extraction.", file=sys.stderr)
        print("Install it with:  pip install pillow", file=sys.stderr)
        sys.exit(1)


def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def role_guess(r, g, b):
    """Best-effort semantic role from HSV. These are hints for Pip to rename, not
    ground truth -- value/saturation gate first, then hue buckets."""
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hue = h * 360.0

    # Achromatic / value extremes first.
    if v < 0.16:
        return "ink"
    if s < 0.12:
        if v > 0.82:
            return "paper-bone"
        if v > 0.5:
            return "ash-grey"
        return "shadow-grey"

    # Chromatic buckets (hue in degrees).
    if hue < 20 or hue >= 345:
        return "alert-red"
    if hue < 45:
        return "ground-warm" if v < 0.6 else "accent-amber"
    if hue < 70:
        return "brass-yellow"
    if hue < 160:
        return "signal-green"
    if hue < 200:
        return "screen-cyan"
    if hue < 255:
        return "screen-blue"
    if hue < 290:
        return "doom-indigo"
    return "doom-purple"


def extract_palette(image_path, n, Image):
    """Return a list of {hex, rgb, role_guess, weight_pct} sorted by frequency."""
    img = Image.open(image_path).convert("RGB")

    # Downscale for speed; the colour histogram is preserved well enough.
    img.thumbnail((SAMPLE_MAX_EDGE, SAMPLE_MAX_EDGE), Image.LANCZOS)

    # Adaptive (median-cut) quantise over the actual pixels.
    quant = img.quantize(colors=n, method=Image.Quantize.MEDIANCUT)

    palette = quant.getpalette()  # flat [r,g,b, r,g,b, ...]
    counts = quant.getcolors(maxcolors=n * n) or []  # [(count, index), ...]
    total = sum(c for c, _ in counts) or 1

    entries = []
    for count, index in counts:
        base = index * 3
        r, g, b = palette[base], palette[base + 1], palette[base + 2]
        entries.append(
            {
                "hex": rgb_to_hex(r, g, b),
                "rgb": [r, g, b],
                "role_guess": role_guess(r, g, b),
                "weight_pct": round(100.0 * count / total, 2),
            }
        )

    entries.sort(key=lambda e: e["weight_pct"], reverse=True)
    return entries


def write_swatches_html(entries, out_path, source_name):
    """Standalone swatch page -- inline styles only, no external assets."""
    cells = []
    for e in entries:
        r, g, b = e["rgb"]
        # Pick a legible text colour against the swatch (perceived luminance).
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        text = "#111" if lum > 140 else "#f4f4f4"
        cells.append(
            """    <figure class="sw" style="background:{hexv};color:{text}">
      <figcaption>
        <span class="hex">{hexv}</span>
        <span class="role">{role}</span>
        <span class="meta">rgb({r},{g},{b}) &middot; {wt}%</span>
      </figcaption>
    </figure>""".format(
                hexv=e["hex"],
                text=text,
                role=e["role_guess"],
                r=r,
                g=g,
                b=b,
                wt=e["weight_pct"],
            )
        )

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>P(Doom)1 brand palette -- {n} swatches</title>
<style>
  body{{margin:0;font-family:ui-monospace,Consolas,monospace;background:#181410;color:#ece0cf;padding:2rem}}
  h1{{font-size:1.1rem;letter-spacing:.04em;margin:0 0 .3rem}}
  p.sub{{color:#a9977f;font-size:.8rem;margin:0 0 1.6rem}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:.7rem}}
  .sw{{margin:0;border-radius:10px;min-height:120px;display:flex;align-items:flex-end;
       padding:.6rem;border:1px solid rgba(255,255,255,.08)}}
  figcaption{{display:flex;flex-direction:column;gap:.1rem;font-size:.72rem;line-height:1.35}}
  .hex{{font-weight:700;letter-spacing:.06em}}
  .role{{opacity:.92}}
  .meta{{opacity:.75;font-size:.66rem}}
</style>
</head>
<body>
  <h1>P(Doom)1 brand palette</h1>
  <p class="sub">{n} swatches extracted from <code>{src}</code> (adaptive median-cut quantise, sorted by pixel frequency). Roles are guesses -- rename freely.</p>
  <div class="grid">
{cells}
  </div>
</body>
</html>
""".format(
        n=len(entries), src=source_name, cells="\n".join(cells)
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Extract a brand palette from an image.")
    parser.add_argument("image", help="Path to the source image (webp/png/jpg).")
    parser.add_argument("--n", type=int, default=24, help="Number of swatches (default: 24).")
    parser.add_argument("--out-json", default=str(DEFAULT_JSON), help="Palette JSON output path.")
    parser.add_argument("--out-html", default=str(DEFAULT_HTML), help="Swatch HTML output path.")
    args = parser.parse_args()

    Image = guarded_pillow()

    image_path = Path(args.image)
    if not image_path.exists():
        print("Image not found: {}".format(image_path), file=sys.stderr)
        sys.exit(2)

    entries = extract_palette(image_path, args.n, Image)

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")

    out_html = Path(args.out_html)
    write_swatches_html(entries, out_html, image_path.name)

    print("Extracted {} colours from {}".format(len(entries), image_path.name))
    print("  palette JSON -> {}".format(out_json))
    print("  swatch HTML  -> {}".format(out_html))
    roles = ", ".join("{} {}".format(e["hex"], e["role_guess"]) for e in entries[:4])
    print("  top roles: {}".format(roles))
    return 0


if __name__ == "__main__":
    sys.exit(main())
