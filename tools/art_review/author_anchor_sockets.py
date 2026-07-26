"""Author godot/data/office/anchor_sockets.json -- Anchor Sockets V2 (#894 #900 #913).

Measures per-clip-direction STATIC anchor points (eyes / butt / spine_mid) for
the PROMOTED cat walk clips (art_source/pixellab_verdicts.json clip-level
entries, triaged by Pip 2026-07-26) so effects can attach to sprite PARTS
instead of sprite centres.

Method (python PIL, deterministic):
  * alpha bbox per frame, averaged across the clip -> subject_px + feet_px
    (feet = bottom-centre of the average bbox; the props_manifest anchor_px
    convention from #906/#915).
  * side-view eyes: hue/saturation blob search inside the head region (front
    40% of the subject, upper half) -- tabby has green eyes, black amber,
    purple orange-red; centroid averaged across frames.
  * rear-view (north) eyes: NOT visible -- anchored at the head centroid
    (top-of-subject centre), flagged "review": true.
  * front-view (south) eyes: dark-dot search on the pale face, flagged
    "review": true (muzzle/nose confusable).
  * butt: rear views + butt-flash only (ruled set) -- rump centre estimated
    from the subject bbox (centre x, ~78% down), flagged "review": true.
  * spine_mid: reserve anchor at the subject centre-back (bbox centre x,
    ~35% down), always flagged "review": true (pure geometry, no detection).
  * footfall_frames: paw-strike pulse hook (Pip ruling 2026-07-26) -- frames
    that are local maxima of ground-row foot spread (stride extremes ~=
    contact frames), flagged "review": true.

Sockets are stored as OFFSETS FROM feet_px in source px (+x right, +y down;
eyes have negative y), mirroring props_manifest approach_px. Canvas position
of a socket = feet_px + px.

V2 = per-direction static offsets only. V3 (documented future) adds per-frame
tracks: "tracks": {"eyes": [[x,y] per frame]} alongside the static px.

Usage:  python tools/art_review/author_anchor_sockets.py
Writes: godot/data/office/anchor_sockets.json (tracked SSOT)
        art_generated/anchor_debug_sheet.png (gitignored marker proof sheet)
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SW = "art_source/pixellab_2026-07-26_cat_sweep"
OUT_JSON = ROOT / "godot" / "data" / "office" / "anchor_sockets.json"
OUT_SHEET = ROOT / "art_generated" / "anchor_debug_sheet.png"

# Promoted clips (pixellab_verdicts.json clip-level "promote" entries,
# 2026-07-26) -> runtime sprite-set/clip ids the sandbox builds.
# view: side_e / side_w (eyes by colour blob), rear (lowtd north-ish),
# front (lowtd south). eye_hue: (hue_lo_deg, hue_hi_deg, sat_min, val_min).
GREEN_EYES = (60, 170, 0.25, 0.25)
AMBER_EYES = (10, 50, 0.55, 0.55)
CLIPS = {
    "cat_tabby_v1": {
        "walk_east": {
            "dir": f"{SW}/cat_b2_tabby_side_heft/animations/walk_side_diag_probe/east",
            "view": "side_e",
            "eye_hue": GREEN_EYES,
        },
        "walk_west": {
            "dir": f"{SW}/cat_b2_tabby_side_heft/animations/walk_side_diag_probe/west",
            "view": "side_w",
            "eye_hue": GREEN_EYES,
        },
        "walk_north": {
            "dir": f"{SW}/cat_b2_tabby_lowtd_heft/animations/walk_ns_lowtd/north",
            "view": "rear",
        },
        "walk_south": {
            "dir": f"{SW}/cat_b2_tabby_lowtd_heft/animations/walk_ns_lowtd/south",
            "view": "front",
        },
        # butt-flash splice (issue #913): frames 2..8 of the 9-frame clip are
        # what the renderer plays as walk_north_alt (frame_000 = idle ref).
        "walk_north_alt": {
            "dir": f"{SW}/cat_b2_tabby_lowtd_heft/animations/butt_flash_north/north",
            "view": "rear",
            "frames": [2, 8],
        },
    },
    "cat_black_v1": {
        "walk_east": {
            "dir": f"{SW}/cat_sweep_black_side_heft/animations/walk_ew/east",
            "view": "side_e",
            "eye_hue": AMBER_EYES,
        },
        "walk_west": {
            "dir": f"{SW}/cat_sweep_black_side_heft/animations/walk_ew/west",
            "view": "side_w",
            "eye_hue": AMBER_EYES,
        },
    },
    "cat_purple_v1": {
        "walk_east": {
            "dir": f"{SW}/cat_sweep_purple_side_heft/animations/walking/east",
            "view": "side_e",
            "eye_hue": AMBER_EYES,
        },
        "walk_west": {
            "dir": f"{SW}/cat_sweep_purple_side_heft/animations/walking/west",
            "view": "side_w",
            "eye_hue": AMBER_EYES,
        },
    },
}

SCHEMA = {
    "sprites": (
        "sprite-set id -> {canvas_px, clips}. Ids match the SpriteFrames sets the "
        "office sandbox builds from the promoted cat sweep clips "
        "(art_source/pixellab_verdicts.json 'promote' entries, Pip 2026-07-26)."
    ),
    "canvas_px": "[w, h] full frame canvas in pixels (all clips of a set share it).",
    "clips": (
        "clip name (runtime AnimatedSprite2D animation name, e.g. walk_east; "
        "walk_north_alt = the #913 butt-flash splice) -> per-clip anchor data."
    ),
    "source_dir": "repo-root-relative dir holding the clip's frame_NNN.png files.",
    "frames": (
        "OPTIONAL [first, last] inclusive frame-index range used from source_dir "
        "(butt-flash splices 2..8 per the sweep MANIFEST); absent = all frames."
    ),
    "subject_px": "[w, h] opaque-subject bbox averaged across the clip's frames (rounded).",
    "feet_px": (
        "[x, y] feet anchor in CANVAS coords: bottom-centre of the average alpha "
        "bbox (same convention as props_manifest anchor_px, #906/#915). The "
        "sprite origin sockets are measured from."
    ),
    "footfall_frames": (
        "clip-local frame indices (0-based) where a paw strikes the floor -- the "
        "deterministic hook for footfall-anchored overlay pulses (Pip ruling "
        "2026-07-26). Measured as stride-extreme frames; review flags apply."
    ),
    "sockets": (
        "list of {name, px, layer} -- the UNIFIED socket convention shared with "
        "props_manifest.json sockets. px = [x, y] OFFSET FROM feet_px in source "
        "px (+x right, +y down; eyes are negative y). layer: 'front'|'behind' "
        "draw order relative to the host sprite. Optional review/notes. Ruled "
        "anchor set for cats: eyes (every direction), butt (rear-facing + "
        "butt-flash only), spine_mid (reserve)."
    ),
    "review": "optional bool: true = anchor needs Pip's judgement (see notes).",
    "notes": "optional free-text provenance / uncertainty notes.",
    "v3_future": (
        "V2 stores per-direction STATIC offsets only. V3 adds OPTIONAL per-frame "
        "tracks alongside px: 'tracks': {socket_name: [[x, y] per clip frame]}; "
        "consumers prefer tracks when present and fall back to px. The layering "
        "lab's click-to-adjust flow is the intended authoring path."
    ),
}


def hsv(px):
    r, g, b = (c / 255.0 for c in px[:3])
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0:
        h = 0.0
    elif mx == r:
        h = 60 * (((g - b) / d) % 6)
    elif mx == g:
        h = 60 * ((b - r) / d + 2)
    else:
        h = 60 * ((r - g) / d + 4)
    s = 0.0 if mx == 0 else d / mx
    return h, s, mx


def load_frames(spec):
    d = ROOT / spec["dir"]
    paths = sorted(d.glob("frame_*.png"))
    if not paths:
        raise FileNotFoundError(d)
    if "frames" in spec:
        a, b = spec["frames"]
        paths = paths[a : b + 1]
    return [Image.open(p).convert("RGBA") for p in paths]


def bbox_of(im):
    bb = im.split()[3].getbbox()  # (l, t, r_excl, b_excl)
    if bb is None:
        raise ValueError("empty frame")
    return bb


def avg(vals):
    return sum(vals) / len(vals)


def detect_eyes_side(frames, spec, bboxes):
    """Colour-blob centroid inside the head region of a side view."""
    h_lo, h_hi, s_min, v_min = spec["eye_hue"]
    east = spec["view"] == "side_e"
    pts = []
    for im, (bl, bt, br, bb) in zip(frames, bboxes):
        w, hgt = br - bl, bb - bt
        # head = front 40% of the subject, upper 55% (above the collar line)
        x0 = bl + int(w * 0.60) if east else bl
        x1 = br if east else bl + int(w * 0.40)
        y1 = bt + int(hgt * 0.55)
        hits = []
        for y in range(bt, y1):
            for x in range(x0, x1):
                px = im.getpixel((x, y))
                if px[3] < 200:
                    continue
                h, s, v = hsv(px)
                if h_lo <= h <= h_hi and s >= s_min and v >= v_min:
                    hits.append((x, y))
        if hits:
            pts.append((avg([p[0] for p in hits]), avg([p[1] for p in hits])))
    if not pts:
        return None
    return (avg([p[0] for p in pts]), avg([p[1] for p in pts]))


def detect_eyes_front(frames, bboxes):
    """Darkest-dot centroid on the face (front/lowtd south view). Confusable
    with the muzzle -> caller flags review."""
    pts = []
    for im, (bl, bt, br, bb) in zip(frames, bboxes):
        w, hgt = br - bl, bb - bt
        x0, x1 = bl + int(w * 0.25), br - int(w * 0.25)
        y0, y1 = bt + int(hgt * 0.18), bt + int(hgt * 0.48)
        hits = []
        for y in range(y0, y1):
            for x in range(x0, x1):
                px = im.getpixel((x, y))
                if px[3] < 200:
                    continue
                _, _, v = hsv(px)
                if v < 0.30:  # dark dots on a pale face
                    hits.append((x, y))
        if hits:
            pts.append((avg([p[0] for p in hits]), avg([p[1] for p in hits])))
    if not pts:
        return None
    return (avg([p[0] for p in pts]), avg([p[1] for p in pts]))


def detect_footfalls(frames, bboxes):
    """Stride-extreme frames ~= paw-strike frames: local maxima of the opaque
    x-spread over the bottom 3 rows of each frame's bbox."""
    spreads = []
    for im, (bl, bt, br, bb) in zip(frames, bboxes):
        xs = [
            x
            for y in range(max(bt, bb - 3), bb)
            for x in range(bl, br)
            if im.getpixel((x, y))[3] >= 200
        ]
        spreads.append((max(xs) - min(xs)) if xs else 0)
    n = len(spreads)
    hits = [
        i
        for i in range(n)
        if spreads[i] >= spreads[(i - 1) % n] and spreads[i] >= spreads[(i + 1) % n]
    ]
    # collapse adjacent plateau indices; keep at most 2 per 8-frame cycle
    kept = []
    for i in hits:
        if not kept or (i - kept[-1]) % n > 1:
            kept.append(i)
    return kept[:2] if kept else [0]


def author_clip(sprite, clip, spec):
    frames = load_frames(spec)
    bboxes = [bbox_of(im) for im in frames]
    sub_w = round(avg([br - bl for bl, bt, br, bb in bboxes]))
    sub_h = round(avg([bb - bt for bl, bt, br, bb in bboxes]))
    feet_x = round(avg([(bl + br) / 2 for bl, bt, br, bb in bboxes]) * 2) / 2
    feet_y = round(avg([bb for bl, bt, br, bb in bboxes]))
    top_y = round(avg([bt for bl, bt, br, bb in bboxes]))
    l_av = avg([bl for bl, bt, br, bb in bboxes])
    r_av = avg([br for bl, bt, br, bb in bboxes])

    def off(cx, cy):
        return [round(cx - feet_x), round(cy - feet_y)]

    sockets = []
    view = spec["view"]
    if view in ("side_e", "side_w"):
        eye = detect_eyes_side(frames, spec, bboxes)
        if eye is not None:
            sockets.append(
                {
                    "name": "eyes",
                    "px": off(*eye),
                    "layer": "front",
                    "notes": "colour-blob centroid of the iris pixels, avg across frames",
                }
            )
        else:
            # geometric fallback: front-top of the head
            ex = r_av - sub_w * 0.12 if view == "side_e" else l_av + sub_w * 0.12
            sockets.append(
                {
                    "name": "eyes",
                    "px": off(ex, top_y + sub_h * 0.30),
                    "layer": "front",
                    "review": True,
                    "notes": "eye colour-blob detection found nothing; geometric head-front guess",
                }
            )
    elif view == "front":
        eye = detect_eyes_front(frames, bboxes)
        if eye is not None:
            sockets.append(
                {
                    "name": "eyes",
                    "px": off(*eye),
                    "layer": "front",
                    "review": True,
                    "notes": "dark-dot centroid on the face; muzzle/nose confusable -- Pip to nudge in the lab",
                }
            )
        else:
            sockets.append(
                {
                    "name": "eyes",
                    "px": off((l_av + r_av) / 2, top_y + sub_h * 0.30),
                    "layer": "front",
                    "review": True,
                    "notes": "no dark-dot hit; geometric face-centre guess",
                }
            )
    else:  # rear
        sockets.append(
            {
                "name": "eyes",
                "px": off((l_av + r_av) / 2, top_y + sub_h * 0.14),
                "layer": "behind",
                "review": True,
                "notes": (
                    "eyes NOT visible from the rear -- anchored at the head "
                    "centroid so a glow halos the head; layer behind"
                ),
            }
        )
        sockets.append(
            {
                "name": "butt",
                "px": off((l_av + r_av) / 2, top_y + sub_h * 0.78),
                "layer": "front",
                "review": True,
                "notes": "rump centre from bbox geometry (~78% down the subject) -- Pip to nudge in the lab",
            }
        )
    sockets.append(
        {
            "name": "spine_mid",
            "px": off((l_av + r_av) / 2, top_y + sub_h * 0.35),
            "layer": "front",
            "review": True,
            "notes": "reserve anchor, pure bbox geometry (centre x, 35% down)",
        }
    )
    entry = {
        "source_dir": spec["dir"],
        "subject_px": [sub_w, sub_h],
        "feet_px": [feet_x, feet_y],
        "footfall_frames": detect_footfalls(frames, bboxes),
        "footfall_review": True,
        "sockets": sockets,
    }
    if "frames" in spec:
        entry["frames"] = spec["frames"]
    return entry, frames


def debug_sheet(rows):
    """rows: list of (label, frame_img, entry) -- draw markers, 6x upscale."""
    s = 6
    cell_h = 68 * s + 22
    sheet = Image.new("RGBA", (68 * s * 3 + 40, cell_h * len(rows)), (28, 28, 32, 255))
    dr = ImageDraw.Draw(sheet)
    colors = {"eyes": (0, 255, 90), "butt": (255, 80, 200), "spine_mid": (80, 170, 255)}
    for i, (label, im, entry) in enumerate(rows):
        y0 = i * cell_h
        big = im.resize((68 * s, 68 * s), Image.NEAREST)
        sheet.alpha_composite(big, (0, y0))
        fx, fy = entry["feet_px"]
        dr.line([(0, y0 + fy * s), (68 * s, y0 + fy * s)], fill=(255, 255, 0, 140), width=1)
        dr.ellipse(
            [fx * s - 4, y0 + fy * s - 4, fx * s + 4, y0 + fy * s + 4],
            outline=(255, 255, 0),
            width=2,
        )
        for sk in entry["sockets"]:
            cx = (fx + sk["px"][0]) * s
            cy = y0 + (fy + sk["px"][1]) * s
            col = colors.get(sk["name"], (255, 255, 255))
            dr.line([(cx - 7, cy), (cx + 7, cy)], fill=col, width=2)
            dr.line([(cx, cy - 7), (cx, cy + 7)], fill=col, width=2)
            if sk.get("review"):
                dr.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], outline=col, width=1)
        dr.text(
            (68 * s + 10, y0 + 10),
            label
            + "\nfeet %s  footfalls %s" % (entry["feet_px"], entry["footfall_frames"])
            + "".join(
                "\n%s %s%s" % (sk["name"], sk["px"], " [review]" if sk.get("review") else "")
                for sk in entry["sockets"]
            ),
            fill=(230, 230, 210),
        )
        dr.text((4, y0 + 68 * s + 4), label, fill=(255, 255, 160))
    return sheet


def main():
    sprites = {}
    rows = []
    n_review = 0
    for sprite, clips in CLIPS.items():
        canvas = None
        centry = {}
        for clip, spec in clips.items():
            entry, frames = author_clip(sprite, clip, spec)
            centry[clip] = entry
            canvas = list(frames[0].size)
            mid = frames[len(frames) // 2]
            rows.append(("%s / %s" % (sprite, clip), mid, entry))
            n_review += sum(1 for sk in entry["sockets"] if sk.get("review"))
        sprites[sprite] = {"canvas_px": canvas, "clips": centry}
    doc = {
        "_meta": {
            "version": "2.0",
            "description": (
                "Anchor Sockets V2 -- per-clip-direction named anchor points on "
                "animated sprites, so effects attach to PARTS (eyes, butt, "
                "spine_mid) instead of sprite centres. Covers the PROMOTED cat "
                "sweep clips (Pip triage 2026-07-26). Consumed by "
                "scripts/ui/office_floor/anchored_overlay.gd; authored by "
                "tools/art_review/author_anchor_sockets.py; adjusted via the "
                "layering lab click-to-adjust flow. See docs/art/PROP_MANIFEST.md "
                "(Anchor sockets section)."
            ),
            "measured_with": "tools/art_review/author_anchor_sockets.py (python PIL), 2026-07-26",
        },
        "_schema": SCHEMA,
        "sprites": sprites,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(doc, indent=2) + "\n", encoding="ascii", newline="\n")
    print("wrote %s (%d sprite sets)" % (OUT_JSON, len(sprites)))
    print("review-flagged sockets: %d" % n_review)
    OUT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    debug_sheet(rows).save(OUT_SHEET)
    print("wrote %s" % OUT_SHEET)
    return 0


if __name__ == "__main__":
    sys.exit(main())
