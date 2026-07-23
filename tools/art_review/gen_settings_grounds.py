#!/usr/bin/env python3
"""
Warm-register settings-screen background candidates for P(Doom)1 (no API).

The current kept settings ground is the sage/green peeling-paint metal panel
(godot/assets/textures/surfaces/tex_painted_metal_panel_512.png, 512x512).
Pip flagged it as the greenest of the kept grounds and asked for 3 alternatives
in the WARMER register of the other kept grounds. These are procedural
worn-panel textures (peeling paint + rust + corner/edge screws + grain) at the
SAME 512x512 so they are drop-in replacements for that TextureRect.

No-key fallback: gpt-image-1 (tools/assets) is the higher-fidelity path but
needs OPENAI_API_KEY, absent in this environment.

Usage:
  python tools/art_review/gen_settings_grounds.py --out art_source/settings_bg_2026-07-21
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT_SIZE = 512
WORK = 1024  # render at 2x then downscale for anti-aliased screws/grain


def noise_field(size, base_cells, octaves, y_squash, seed):
    """Multi-octave value noise in [0,1]. y_squash>1 stretches features
    vertically (paint-drip look)."""
    rng = np.random.default_rng(seed)
    acc = np.zeros((size, size), dtype=float)
    amp, tot, cells = 1.0, 0.0, base_cells
    for _ in range(octaves):
        rows = max(2, int(cells / y_squash))
        g = rng.random((rows, cells))
        im = Image.fromarray((g * 255).astype("uint8")).resize((size, size), Image.BICUBIC)
        acc += amp * (np.asarray(im, dtype=float) / 255.0)
        tot += amp
        amp *= 0.5
        cells *= 2
    return acc / tot


def lerp_rgb(a, b, t):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    t = t[..., None]
    return a * (1 - t) + b * t


def edge_proximity(size):
    ax = np.linspace(0, 1, size)
    gx, gy = np.meshgrid(ax, ax)
    d = np.minimum.reduce([gx, gy, 1 - gx, 1 - gy])  # 0 at edge, 0.5 at center
    return np.clip(1 - d / 0.14, 0, 1)  # ~1 near edges, 0 inside


def build_panel(style):
    p = STYLES[style]
    size = WORK
    peel = noise_field(size, 6, 5, p["y_squash"], p["seed"])
    stain = noise_field(size, 3, 3, 1.0, p["seed"] + 100)
    grain = noise_field(size, 220, 2, 1.0, p["seed"] + 200)
    rustn = noise_field(size, 10, 4, 1.6, p["seed"] + 300)

    t = p["peel_thresh"]
    # topcoat (m=1) vs undercoat (m=0), soft transition
    m = np.clip((peel - (t - 0.05)) / 0.11, 0, 1)
    col = lerp_rgb(p["undercoat"], p["topcoat"], m)
    # deepest peel reveals the dark substrate
    deep = np.clip(((t - 0.16) - peel) / 0.10, 0, 1) * p["deep_amt"]
    col = lerp_rgb(col, p["base"], deep)

    # broad dirt/stain shading
    col *= (0.86 + 0.20 * stain)[..., None]

    # rust: near edges + where rust noise is high (and mostly on peeled metal)
    rust_mask = np.clip(rustn - 0.55, 0, 1) * 2.2
    rust_mask = np.clip(rust_mask * (0.35 + 0.75 * edge_proximity(size)), 0, 1)
    rust_mask *= 1 - 0.5 * m  # more rust where paint has gone
    col = lerp_rgb(col, p["rust"], rust_mask * p["rust_amt"])

    # fine grain
    col += ((grain - 0.5) * p["grain"])[..., None]

    col = np.clip(col, 0, 255).astype("uint8")
    img = Image.fromarray(col, "RGB").convert("RGBA")

    _add_screws(img, p)
    _add_vignette(img)
    return img.resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS).convert("RGB")


def _add_screws(img, p):
    d = ImageDraw.Draw(img)
    s = WORK
    inset = int(s * 0.055)
    positions = [
        (inset, inset),
        (s - inset, inset),
        (inset, s - inset),
        (s - inset, s - inset),
        (s // 2, inset),
        (s // 2, s - inset),
        (inset, s // 2),
        (s - inset, s // 2),
    ]
    r = int(s * 0.026)
    for cx, cy in positions:
        # rust ring
        d.ellipse(
            [cx - r * 1.6, cy - r * 1.6, cx + r * 1.6, cy + r * 1.6],
            fill=tuple(int(v) for v in p["rust"]) + (70,),
        )
        # screw body
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(38, 30, 24, 255))
        # bevel highlight (top-left)
        d.arc(
            [cx - r, cy - r, cx + r, cy + r],
            150,
            300,
            fill=(150, 130, 100, 255),
            width=max(2, r // 5),
        )
        # slot
        d.line(
            [(cx - r * 0.6, cy - r * 0.2), (cx + r * 0.6, cy + r * 0.2)],
            fill=(20, 15, 12, 255),
            width=max(2, r // 4),
        )
    # blur screws slightly so they sit in the surface
    return img


def _add_vignette(img):
    s = WORK
    vig = Image.new("L", (s, s), 0)
    dv = ImageDraw.Draw(vig)
    dv.rectangle([int(s * 0.03)] * 2 + [int(s * 0.97)] * 2, fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(s * 0.06))
    dark = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    dark.putalpha(vig.point(lambda v: 60 - int(v * 60 / 255)))
    img.alpha_composite(dark)


# Warm-register palettes (topcoat / undercoat / dark base / rust), all avoiding
# the sage-green of the current kept panel.
STYLES = {
    "warm_ochre": dict(
        topcoat=(150, 112, 58),
        undercoat=(198, 172, 124),
        base=(78, 50, 30),
        rust=(120, 62, 34),
        peel_thresh=0.52,
        deep_amt=0.75,
        rust_amt=0.85,
        y_squash=3.2,
        grain=16,
        seed=7,
    ),
    "warm_terracotta": dict(
        topcoat=(158, 78, 46),
        undercoat=(196, 150, 98),
        base=(70, 36, 24),
        rust=(132, 58, 30),
        peel_thresh=0.5,
        deep_amt=0.8,
        rust_amt=0.95,
        y_squash=3.0,
        grain=15,
        seed=19,
    ),
    "warm_bakelite": dict(
        topcoat=(96, 64, 42),
        undercoat=(140, 100, 62),
        base=(52, 34, 22),
        rust=(104, 58, 34),
        peel_thresh=0.44,
        deep_amt=0.55,
        rust_amt=0.6,
        y_squash=2.2,
        grain=13,
        seed=31,
    ),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for style in STYLES:
        img = build_panel(style)
        fn = out / f"settings_bg_{style}_512.png"
        img.save(fn)
        print(f"  rendered {fn.name}")
    print(f"Done: {len(STYLES)} settings-background candidates -> {out}")


if __name__ == "__main__":
    main()
