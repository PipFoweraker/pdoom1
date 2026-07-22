#!/usr/bin/env python3
"""
Stopgap app-icon candidate generator for P(Doom)1 (no external API).

Renders clean, supersampled vector-style app-icon candidates in the locked
palette (docs/art/PALETTE_AND_DOOM_INTENSITY.md), covering four concept
directions: office cat, doom gauge/dial, bureaucratic seal/stamp, and a
P(Doom) typographic mark. Every candidate is emitted at multiple sizes down
to 32x32 so small-size readability (SmartScreen / taskbar, issue #732) can be
checked directly.

This is a NO-KEY fallback: the gpt-image-1 pipeline (tools/assets) is the
intended higher-fidelity path but requires OPENAI_API_KEY, which was absent in
this environment. These procedural marks are deliberately "quantity + variety
over polish" stopgaps for Pip's fast pass.

Usage:
  python tools/art_review/gen_icon_candidates.py --out art_source/iconset_2026-07-21
"""

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Locked palette (RGB), from docs/art/PALETTE_AND_DOOM_INTENSITY.md
# ---------------------------------------------------------------------------
VOID = (14, 6, 20)
AUBERGINE = (23, 10, 28)
INK = (20, 4, 12)
WARM_PANEL = (43, 34, 26)
WARM_LINE = (58, 46, 34)
COZY_AMBER = (232, 163, 61)
AMBER = (246, 168, 0)
OFFWHITE = (233, 242, 242)
CHROME = (107, 124, 140)
TEAL = (30, 195, 179)
ORANGE = (233, 117, 46)
REDORANGE = (226, 74, 59)
DEEPRED = (179, 18, 23)

RENDER = 4096  # supersampled master; downscaled to the sizes below
SIZES = [1024, 512, 256, 128, 64, 48, 32]

FONT_DIR = Path("C:/Windows/Fonts")


def font(name, size):
    """Load a Windows TTF with a graceful fallback."""
    for cand in (name, "arialbd.ttf", "arial.ttf"):
        p = FONT_DIR / cand
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except OSError:
                continue
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def doom_color(t):
    """Amber -> orange -> red-orange -> deep red across t in [0,1]."""
    stops = [AMBER, ORANGE, REDORANGE, DEEPRED]
    t = max(0.0, min(1.0, t))
    seg = t * (len(stops) - 1)
    i = min(int(seg), len(stops) - 2)
    return lerp(stops[i], stops[i + 1], seg - i)


# ---------------------------------------------------------------------------
# Icon frame / ground
# ---------------------------------------------------------------------------
def rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m


def vertical_gradient(size, top, bottom):
    grad = Image.new("RGB", (1, size))
    for y in range(size):
        grad.putpixel((0, y), lerp(top, bottom, y / max(1, size - 1)))
    return grad.resize((size, size))


def radial_glow(size, color, cx, cy, radius, strength):
    """A soft additive glow layer (RGBA) centered at (cx, cy)."""
    layer = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=255)
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.55))
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    solid = Image.new("RGBA", (size, size), color + (0,))
    alpha = layer.point(lambda v: int(v * strength))
    solid.putalpha(alpha)
    out.alpha_composite(solid)
    return out


def make_base(ground="warm_dark", glow=AMBER, glow_strength=0.30):
    size = RENDER
    if ground == "amber":
        bg = vertical_gradient(size, COZY_AMBER, AMBER)
    elif ground == "steel":
        bg = vertical_gradient(size, (28, 39, 48), (14, 19, 24))
    else:
        bg = vertical_gradient(size, AUBERGINE, WARM_PANEL)
    img = bg.convert("RGBA")

    if glow is not None and ground != "amber":
        img.alpha_composite(
            radial_glow(size, glow, size // 2, int(size * 0.46), int(size * 0.42), glow_strength)
        )

    # subtle corner vignette
    vig = Image.new("L", (size, size), 0)
    dv = ImageDraw.Draw(vig)
    dv.rounded_rectangle(
        [int(size * 0.06)] * 2 + [int(size * 0.94)] * 2, radius=int(size * 0.18), fill=255
    )
    vig = vig.filter(ImageFilter.GaussianBlur(size * 0.10))
    dark = Image.new("RGBA", (size, size), (0, 0, 0, 90))
    dark.putalpha(vig.point(lambda v: 90 - int(v * 90 / 255)))
    img.alpha_composite(dark)

    draw = ImageDraw.Draw(img)
    # thin warm inner border for icon polish
    border = INK if ground == "amber" else WARM_LINE
    draw.rounded_rectangle(
        [int(size * 0.02)] * 2 + [int(size * 0.98)] * 2,
        radius=int(size * 0.17),
        outline=border,
        width=int(size * 0.010),
    )
    return img, draw


def finalize(img, out_dir, icon_id):
    """Mask to rounded-square and emit all sizes."""
    size = RENDER
    mask = rounded_mask(size, int(size * 0.20))
    img.putalpha(mask)
    for s in SIZES:
        r = img.resize((s, s), Image.LANCZOS)
        r.save(out_dir / f"{icon_id}_{s}.png")
    return icon_id


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def pt(cx, cy, r, deg):
    a = math.radians(deg)  # PIL convention: 0 = 3 o'clock, clockwise (+y down)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def draw_arc_gradient(draw, box, start, end, width, t0=0.0, t1=1.0, step=3):
    n = max(1, int((end - start) / step))
    for i in range(n):
        d0 = start + (end - start) * i / n
        d1 = start + (end - start) * (i + 1) / n
        tt = t0 + (t1 - t0) * (i / max(1, n - 1))
        draw.arc(box, d0, d1 + 1, fill=doom_color(tt), width=width)


def needle(draw, cx, cy, r, deg, color, width, hub=True):
    tip = pt(cx, cy, r, deg)
    tail = pt(cx, cy, -r * 0.22, deg)
    draw.line([tail, tip], fill=color, width=width)
    if hub:
        hr = int(r * 0.10)
        draw.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], fill=color)
        draw.ellipse([cx - hr // 2, cy - hr // 2, cx + hr // 2, cy + hr // 2], fill=INK)


def star(draw, cx, cy, r, color, points=5, inner=0.42, rot=-90):
    pts = []
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * inner
        a = rot + i * 180 / points
        pts.append(pt(cx, cy, rr, a))
    draw.polygon(pts, fill=color)


def text_on_arc(base, text, center, radius, font_obj, fill, center_deg, span_deg, flip=False):
    """Render text along a circular arc. center_deg in PIL degrees (0=3o'clock,
    clockwise). Chars are distributed across span_deg and rotated tangentially.
    flip=True orients text for the bottom of the seal."""
    cx, cy = center
    n = len(text)
    if n == 0:
        return
    for i, ch in enumerate(text):
        frac = 0.5 if n == 1 else i / (n - 1)
        # top arc sweeps left->right; bottom arc sweeps the opposite way so the
        # reading order still runs left->right along the bottom of the seal.
        if flip:
            deg = center_deg + span_deg / 2 - span_deg * frac
            rot = -(deg - 90)
        else:
            deg = center_deg - span_deg / 2 + span_deg * frac
            rot = -(deg + 90)
        # glyph tile
        asc = font_obj.size
        tile = Image.new("RGBA", (asc * 2, asc * 2), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        bb = td.textbbox((0, 0), ch, font=font_obj)
        w = bb[2] - bb[0]
        h = bb[3] - bb[1]
        td.text(
            ((asc * 2 - w) / 2 - bb[0], (asc * 2 - h) / 2 - bb[1]), ch, font=font_obj, fill=fill
        )
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=False)
        px, py = pt(cx, cy, radius, deg)
        base.alpha_composite(tile, (int(px - asc), int(py - asc)))


# ---------------------------------------------------------------------------
# Subject renderers -- CAT
# ---------------------------------------------------------------------------
def cat_face(draw, cx, cy, r, fill, eye, worried=False):
    # ears
    ear = r * 0.95
    draw.polygon(
        [pt(cx, cy, r, -140), (cx - r * 0.15, cy - r * 0.55), pt(cx, cy, ear, -118)], fill=fill
    )
    draw.polygon(
        [pt(cx, cy, r, -40), (cx + r * 0.15, cy - r * 0.55), pt(cx, cy, ear, -62)], fill=fill
    )
    # head
    draw.ellipse([cx - r, cy - r * 0.78, cx + r, cy + r * 0.92], fill=fill)
    # eyes
    ew, eh = r * 0.22, r * 0.30
    for sx in (-1, 1):
        ecx = cx + sx * r * 0.38
        ecy = cy - r * 0.02
        draw.ellipse([ecx - ew, ecy - eh, ecx + ew, ecy + eh], fill=eye)
        # pupil
        draw.ellipse([ecx - ew * 0.35, ecy - eh * 0.7, ecx + ew * 0.35, ecy + eh * 0.7], fill=INK)
    # nose
    draw.polygon(
        [(cx - r * 0.10, cy + r * 0.28), (cx + r * 0.10, cy + r * 0.28), (cx, cy + r * 0.42)],
        fill=INK,
    )
    # whiskers
    for sx in (-1, 1):
        for dy in (-0.05, 0.10):
            draw.line(
                [
                    (cx + sx * r * 0.18, cy + r * 0.32 + r * dy),
                    (cx + sx * r * 0.85, cy + r * 0.20 + r * dy),
                ],
                fill=INK,
                width=int(r * 0.04),
            )
    if worried:
        for sx in (-1, 1):
            draw.line(
                [(cx + sx * r * 0.22, cy - r * 0.42), (cx + sx * r * 0.52, cy - r * 0.30)],
                fill=INK,
                width=int(r * 0.06),
            )


def cat_sitting(draw, cx, cy, r, fill, eye):
    # body (teardrop)
    draw.ellipse([cx - r * 0.75, cy - r * 0.15, cx + r * 0.75, cy + r * 1.15], fill=fill)
    draw.rectangle([cx - r * 0.75, cy + r * 0.5, cx + r * 0.75, cy + r * 1.15], fill=fill)
    # tail curl
    draw.arc(
        [cx + r * 0.2, cy + r * 0.2, cx + r * 1.5, cy + r * 1.3],
        -120,
        90,
        fill=fill,
        width=int(r * 0.26),
    )
    # head
    hr = r * 0.55
    hy = cy - r * 0.45
    draw.ellipse([cx - hr, hy - hr, cx + hr, hy + hr], fill=fill)
    # ears
    draw.polygon(
        [
            (cx - hr * 0.8, hy - hr * 0.6),
            (cx - hr * 0.2, hy - hr * 1.35),
            (cx - hr * 0.05, hy - hr * 0.5),
        ],
        fill=fill,
    )
    draw.polygon(
        [
            (cx + hr * 0.8, hy - hr * 0.6),
            (cx + hr * 0.2, hy - hr * 1.35),
            (cx + hr * 0.05, hy - hr * 0.5),
        ],
        fill=fill,
    )
    # eyes (negative amber)
    for sx in (-1, 1):
        ex = cx + sx * hr * 0.42
        draw.ellipse([ex - hr * 0.16, hy - hr * 0.05, ex + hr * 0.16, hy + hr * 0.30], fill=eye)


# ---------------------------------------------------------------------------
# Candidate builders
# ---------------------------------------------------------------------------
def build_cat_face():
    img, d = make_base(glow=AMBER, glow_strength=0.28)
    c = RENDER // 2
    cat_face(d, c, int(RENDER * 0.52), int(RENDER * 0.30), AMBER, OFFWHITE)
    return img, "icon_cat_face"


def build_cat_face_doom():
    img, d = make_base(glow=REDORANGE, glow_strength=0.42)
    c = RENDER // 2
    cat_face(d, c, int(RENDER * 0.52), int(RENDER * 0.30), COZY_AMBER, AMBER, worried=True)
    return img, "icon_cat_face_doom"


def build_cat_sitting():
    img, d = make_base(glow=AMBER, glow_strength=0.26)
    c = RENDER // 2
    cat_sitting(d, c, int(RENDER * 0.44), int(RENDER * 0.30), AMBER, INK)
    return img, "icon_cat_sitting"


def build_dial_clock():
    img, d = make_base(glow=AMBER, glow_strength=0.26)
    c = RENDER // 2
    r = int(RENDER * 0.34)
    box = [c - r, c - r, c + r, c + r]
    d.ellipse(box, outline=CHROME, width=int(RENDER * 0.018))
    # doom arc across the dial face (amber -> deep red), clockwise over the top
    ar = int(r * 0.80)
    abox = [c - ar, c - ar, c + ar, c + ar]
    draw_arc_gradient(d, abox, -210, 30, int(RENDER * 0.05))
    # ticks
    for k in range(12):
        deg = -90 + k * 30
        p1 = pt(c, c, r * 0.92, deg)
        p2 = pt(c, c, r * 0.70, deg)
        d.line([p1, p2], fill=OFFWHITE, width=int(RENDER * 0.010))
    # needle approaching midnight (12 o'clock = -90)
    needle(d, c, c, r * 0.66, -78, DEEPRED, int(RENDER * 0.018))
    return img, "icon_dial_clock"


def build_dial_half():
    img, d = make_base(glow=ORANGE, glow_strength=0.30)
    c = RENDER // 2
    cy = int(RENDER * 0.60)
    r = int(RENDER * 0.34)
    box = [c - r, cy - r, c + r, cy + r]
    draw_arc_gradient(d, box, 180, 360, int(RENDER * 0.055))
    for k in range(7):
        deg = 180 + k * 30
        d.line(
            [pt(c, cy, r * 1.02, deg), pt(c, cy, r * 0.82, deg)],
            fill=OFFWHITE,
            width=int(RENDER * 0.009),
        )
    needle(d, c, cy, r * 0.86, -52, OFFWHITE, int(RENDER * 0.017))
    return img, "icon_dial_half"


def build_dial_ring():
    img, d = make_base(glow=AMBER, glow_strength=0.30)
    c = RENDER // 2
    r = int(RENDER * 0.33)
    box = [c - r, c - r, c + r, c + r]
    d.arc(box, -90, 200, fill=WARM_LINE, width=int(RENDER * 0.075))
    draw_arc_gradient(d, box, -90, 170, int(RENDER * 0.075))
    f = font("consolab.ttf", int(RENDER * 0.14))
    txt = "P(d)"
    bb = d.textbbox((0, 0), txt, font=f)
    d.text(
        (c - (bb[2] - bb[0]) / 2 - bb[0], c - (bb[3] - bb[1]) / 2 - bb[1]),
        txt,
        font=f,
        fill=OFFWHITE,
    )
    return img, "icon_dial_ring"


def build_dial_radar():
    img, d = make_base(ground="steel", glow=TEAL, glow_strength=0.22)
    c = RENDER // 2
    r = int(RENDER * 0.34)
    for rr in (r, int(r * 0.66), int(r * 0.33)):
        d.ellipse([c - rr, c - rr, c + rr, c + rr], outline=CHROME, width=int(RENDER * 0.008))
    d.line([(c - r, c), (c + r, c)], fill=CHROME, width=int(RENDER * 0.006))
    d.line([(c, c - r), (c, c + r)], fill=CHROME, width=int(RENDER * 0.006))
    needle(d, c, c, r, -60, AMBER, int(RENDER * 0.016))
    # a warning blip
    bx, by = pt(c, c, r * 0.62, -60)
    d.ellipse([bx - r * 0.06, by - r * 0.06, bx + r * 0.06, by + r * 0.06], fill=REDORANGE)
    return img, "icon_dial_radar"


def _seal_rings(d, c, r):
    d.ellipse([c - r, c - r, c + r, c + r], outline=AMBER, width=int(RENDER * 0.014))
    ri = int(r * 0.80)
    d.ellipse([c - ri, c - ri, c + ri, c + ri], outline=AMBER, width=int(RENDER * 0.007))
    return ri


def _distress(img, seed):
    """Multiply a blurred noise mask into the alpha for a worn rubber-stamp look."""
    import numpy as np

    rng = np.random.default_rng(seed)
    n = rng.random((RENDER // 16, RENDER // 16))
    noise = Image.fromarray((n * 255).astype("uint8")).resize((RENDER, RENDER))
    noise = noise.filter(ImageFilter.GaussianBlur(RENDER * 0.004))
    mask = noise.point(lambda v: 255 if v > 70 else int(v * 2.2))
    a = img.getchannel("A")
    from PIL import ImageChops

    img.putalpha(ImageChops.multiply(a, mask))
    return img


def build_seal_star():
    img, d = make_base(glow=AMBER, glow_strength=0.26)
    c = RENDER // 2
    r = int(RENDER * 0.36)
    stamp = Image.new("RGBA", (RENDER, RENDER), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    _seal_rings(sd, c, r)
    star(sd, c, c, int(r * 0.34), AMBER)
    f = font("framd.ttf", int(RENDER * 0.072))
    text_on_arc(stamp, "P(DOOM) LABORATORY", (c, c), int(r * 0.90), f, AMBER, -90, 200)
    text_on_arc(stamp, "EST. NOW", (c, c), int(r * 0.90), f, AMBER, 90, 70, flip=True)
    stamp = _distress(stamp, 11)
    img.alpha_composite(stamp)
    return img, "icon_seal_star"


def build_seal_hourglass():
    img, d = make_base(glow=AMBER, glow_strength=0.26)
    c = RENDER // 2
    r = int(RENDER * 0.36)
    stamp = Image.new("RGBA", (RENDER, RENDER), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    _seal_rings(sd, c, r)
    hr = int(r * 0.30)
    sd.polygon([(c - hr, c - hr), (c + hr, c - hr), (c, c)], fill=AMBER)
    sd.polygon([(c - hr, c + hr), (c + hr, c + hr), (c, c)], fill=AMBER)
    sd.line(
        [(c - hr * 1.15, c - hr), (c + hr * 1.15, c - hr)], fill=AMBER, width=int(RENDER * 0.012)
    )
    sd.line(
        [(c - hr * 1.15, c + hr), (c + hr * 1.15, c + hr)], fill=AMBER, width=int(RENDER * 0.012)
    )
    f = font("framd.ttf", int(RENDER * 0.060))
    text_on_arc(stamp, "PAPERWORK THAT MIGHT", (c, c), int(r * 0.90), f, AMBER, -90, 220)
    text_on_arc(stamp, "SAVE THE WORLD", (c, c), int(r * 0.90), f, AMBER, 90, 120, flip=True)
    stamp = _distress(stamp, 23)
    img.alpha_composite(stamp)
    return img, "icon_seal_hourglass"


def build_seal_check():
    img, d = make_base(glow=TEAL, glow_strength=0.20)
    c = RENDER // 2
    r = int(RENDER * 0.36)
    stamp = Image.new("RGBA", (RENDER, RENDER), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    # scalloped octagon frame
    pts = [pt(c, c, r, -90 + k * 45) for k in range(8)]
    sd.polygon(pts, outline=TEAL, width=int(RENDER * 0.014))
    sd.line(
        [pt(c, c, r * 0.78, -90 + k * 45) for k in range(8)] + [pt(c, c, r * 0.78, -90)],
        fill=TEAL,
        width=int(RENDER * 0.006),
    )
    sd.line(
        [(c - r * 0.30, c + r * 0.02), (c - r * 0.05, c + r * 0.28), (c + r * 0.34, c - r * 0.26)],
        fill=TEAL,
        width=int(RENDER * 0.030),
        joint="curve",
    )
    f = font("framd.ttf", int(RENDER * 0.066))
    text_on_arc(stamp, "DOOM DEPT", (c, c), int(r * 0.88), f, TEAL, -90, 150)
    text_on_arc(stamp, "APPROVED", (c, c), int(r * 0.88), f, TEAL, 90, 120, flip=True)
    stamp = _distress(stamp, 37)
    img.alpha_composite(stamp)
    return img, "icon_seal_check"


def build_seal_red():
    img, d = make_base(glow=REDORANGE, glow_strength=0.30)
    c = RENDER // 2
    r = int(RENDER * 0.36)
    stamp = Image.new("RGBA", (RENDER, RENDER), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    ink = REDORANGE
    sd.ellipse([c - r, c - r, c + r, c + r], outline=ink, width=int(RENDER * 0.016))
    ri = int(r * 0.78)
    sd.ellipse([c - ri, c - ri, c + ri, c + ri], outline=ink, width=int(RENDER * 0.008))
    star(sd, c, c, int(r * 0.32), ink)
    f = font("georgiab.ttf", int(RENDER * 0.070))
    text_on_arc(stamp, "P(DOOM)", (c, c), int(r * 0.88), f, ink, -90, 130)
    text_on_arc(stamp, "OFFICIAL", (c, c), int(r * 0.88), f, ink, 90, 110, flip=True)
    stamp = _distress(stamp, 5)
    img.alpha_composite(stamp)
    return img, "icon_seal_red"


def build_type_wordmark():
    img, d = make_base(glow=AMBER, glow_strength=0.28)
    c = RENDER // 2
    f = font("segoeuib.ttf", int(RENDER * 0.20))
    txt = "P(Doom)"
    bb = d.textbbox((0, 0), txt, font=f)
    d.text(
        (c - (bb[2] - bb[0]) / 2 - bb[0], c - (bb[3] - bb[1]) / 2 - bb[1]), txt, font=f, fill=AMBER
    )
    return img, "icon_type_wordmark"


def build_type_amber():
    img, d = make_base(ground="amber")
    c = RENDER // 2
    f = font("segoeuib.ttf", int(RENDER * 0.20))
    txt = "P(Doom)"
    bb = d.textbbox((0, 0), txt, font=f)
    d.text(
        (c - (bb[2] - bb[0]) / 2 - bb[0], c - (bb[3] - bb[1]) / 2 - bb[1]), txt, font=f, fill=INK
    )
    return img, "icon_type_amber"


def build_type_mono():
    img, d = make_base(glow=AMBER, glow_strength=0.26)
    c = RENDER // 2
    fp = font("impact.ttf", int(RENDER * 0.52))
    d.text((c, int(RENDER * 0.30)), "P", font=fp, fill=AMBER, anchor="mm")
    fd = font("consolab.ttf", int(RENDER * 0.12))
    d.text((c, int(RENDER * 0.70)), "(doom)", font=fd, fill=OFFWHITE, anchor="mm")
    return img, "icon_type_mono"


def build_type_dial_paren():
    """Hybrid mark: 'P(' + a tiny doom gauge + ')' -- type meets dial."""
    img, d = make_base(glow=AMBER, glow_strength=0.30)
    c = RENDER // 2
    f = font("segoeuib.ttf", int(RENDER * 0.34))
    left = "P("
    right = ")"
    lb = d.textbbox((0, 0), left, font=f)
    rb = d.textbbox((0, 0), right, font=f)
    gauge_r = int(RENDER * 0.11)
    total = (lb[2] - lb[0]) + gauge_r * 2 + (rb[2] - rb[0])
    x = c - total / 2
    ty = c - (lb[3] - lb[1]) / 2 - lb[1]
    d.text((x - lb[0], ty), left, font=f, fill=AMBER)
    x += lb[2] - lb[0]
    gx = x + gauge_r
    gbox = [gx - gauge_r, c - gauge_r, gx + gauge_r, c + gauge_r]
    draw_arc_gradient(d, gbox, -210, 30, int(RENDER * 0.028))
    needle(d, gx, c, gauge_r * 0.7, -78, DEEPRED, int(RENDER * 0.012), hub=True)
    x += gauge_r * 2
    d.text((x - rb[0], ty), right, font=f, fill=AMBER)
    return img, "icon_type_dial_paren"


BUILDERS = [
    build_cat_face,
    build_cat_face_doom,
    build_cat_sitting,
    build_dial_clock,
    build_dial_half,
    build_dial_ring,
    build_dial_radar,
    build_seal_star,
    build_seal_hourglass,
    build_seal_check,
    build_seal_red,
    build_type_wordmark,
    build_type_amber,
    build_type_mono,
    build_type_dial_paren,
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    made = []
    for b in BUILDERS:
        img, icon_id = b()
        finalize(img, out, icon_id)
        made.append(icon_id)
        print(f"  rendered {icon_id}")
    print(f"Done: {len(made)} icon candidates -> {out}")


if __name__ == "__main__":
    main()
