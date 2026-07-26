#!/usr/bin/env python3
"""qc_sprite_frames -- PIL QC gate for pixellab character batches.

Checks (per docs/art/PIXELLAB_OPERATIONS.md house rules, ruled 2026-07-26):

1. CLEAN ALPHA under feet: no near-white OPAQUE pixels in the lower third of
   the canvas (the white-flash matting failure). Threshold: min(R,G,B) >= 235
   and alpha >= 128, count > allowed (default 4) -> FAIL for that frame.
2. CANVAS consistency: every PNG under one variant folder must share one
   canvas size.
3. FRAME CONTINUITY (animations): between adjacent frames of one direction,
   the alpha-silhouette centroid must not jump more than --max-jump px
   (default 10) and the silhouette IoU must stay >= --min-iou (default 0.55).
   Violations are flagged as limb-teleport SUSPECTS for the review sheet,
   not hard failures (walk strides legitimately move limbs).

Usage:
    python tools/art_review/qc_sprite_frames.py art_source/<batch_dir>
    python tools/art_review/qc_sprite_frames.py art_source/<batch_dir> --json out.json

Exit code 1 if any HARD failure (alpha or canvas); continuity suspects only
warn. Stdlib + Pillow. ASCII only.
"""

import argparse
import json
import os
import re
import sys

from PIL import Image

WHITE_MIN = 235  # min(R,G,B) at/above this counts as near-white
ALPHA_MIN = 128  # opaque enough to matter


def frame_stats(path):
    """Return (size, near_white_lower_third, centroid, mask_set)."""
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    lower_start = h - h // 3
    near_white = 0
    sx = sy = n = 0
    mask = set()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a >= ALPHA_MIN:
                mask.add((x, y))
                sx += x
                sy += y
                n += 1
                if y >= lower_start and min(r, g, b) >= WHITE_MIN:
                    near_white += 1
    centroid = (sx / n, sy / n) if n else (w / 2.0, h / 2.0)
    return (w, h), near_white, centroid, mask


def natural_key(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def qc_batch(root, allowed_white=4, max_jump=10.0, min_iou=0.55):
    report = {"root": root, "variants": {}, "hard_failures": 0, "suspects": 0}
    for variant in sorted(os.listdir(root)):
        vdir = os.path.join(root, variant)
        if not os.path.isdir(vdir):
            continue
        vrep = {
            "canvas": None,
            "canvas_ok": True,
            "alpha_failures": [],
            "continuity_suspects": [],
            "frames": 0,
        }
        sizes = {}
        # collect every PNG, grouped by directory (rotations vs anim dirs)
        groups = {}
        for dirpath, _dirnames, filenames in os.walk(vdir):
            pngs = sorted((f for f in filenames if f.endswith(".png")), key=natural_key)
            if pngs:
                groups[os.path.relpath(dirpath, vdir)] = [os.path.join(dirpath, f) for f in pngs]
        cache = {}
        for rel, paths in sorted(groups.items()):
            for p in paths:
                size, nw, cen, mask = frame_stats(p)
                cache[p] = (size, cen, mask)
                vrep["frames"] += 1
                sizes.setdefault(size, 0)
                sizes[size] += 1
                if nw > allowed_white:
                    vrep["alpha_failures"].append(
                        {
                            "frame": os.path.relpath(p, root).replace(os.sep, "/"),
                            "near_white_px": nw,
                        }
                    )
            # continuity only inside animation frame runs (frame_*.png sequences)
            run = [p for p in paths if os.path.basename(p).startswith("frame_")]
            for a, b in zip(run, run[1:]):
                (_, ca, ma), (_, cb, mb) = cache[a], cache[b]
                jump = ((ca[0] - cb[0]) ** 2 + (ca[1] - cb[1]) ** 2) ** 0.5
                inter = len(ma & mb)
                union = len(ma | mb) or 1
                iou = inter / union
                if jump > max_jump or iou < min_iou:
                    vrep["continuity_suspects"].append(
                        {
                            "pair": [
                                os.path.relpath(a, root).replace(os.sep, "/"),
                                os.path.relpath(b, root).replace(os.sep, "/"),
                            ],
                            "centroid_jump_px": round(jump, 2),
                            "silhouette_iou": round(iou, 3),
                        }
                    )
        if sizes:
            vrep["canvas"] = max(sizes, key=sizes.get)
            vrep["canvas_ok"] = len(sizes) == 1
            if not vrep["canvas_ok"]:
                vrep["canvas_sizes_seen"] = {str(k): v for k, v in sizes.items()}
        report["hard_failures"] += len(vrep["alpha_failures"]) + (0 if vrep["canvas_ok"] else 1)
        report["suspects"] += len(vrep["continuity_suspects"])
        report["variants"][variant] = vrep
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("batch_dir")
    ap.add_argument("--json", help="write full report JSON here")
    ap.add_argument("--allowed-white", type=int, default=4)
    ap.add_argument("--max-jump", type=float, default=10.0)
    ap.add_argument("--min-iou", type=float, default=0.55)
    args = ap.parse_args()
    rep = qc_batch(args.batch_dir, args.allowed_white, args.max_jump, args.min_iou)
    for name, v in rep["variants"].items():
        status = "OK"
        if v["alpha_failures"] or not v["canvas_ok"]:
            status = "FAIL"
        elif v["continuity_suspects"]:
            status = "SUSPECT"
        print(
            f"[{status}] {name}: {v['frames']} frames, canvas {v['canvas']}, "
            f"{len(v['alpha_failures'])} alpha fails, "
            f"{len(v['continuity_suspects'])} continuity suspects"
        )
        for f in v["alpha_failures"]:
            print(f"    ALPHA {f['frame']} near_white_px={f['near_white_px']}")
        for s in v["continuity_suspects"]:
            print(
                f"    CONT  {s['pair'][1]} jump={s['centroid_jump_px']}px "
                f"iou={s['silhouette_iou']}"
            )
    if args.json:
        with open(args.json, "w", encoding="ascii", newline="\n") as fh:
            json.dump(rep, fh, indent=1, sort_keys=True)
        print(f"report -> {args.json}")
    print(f"hard failures: {rep['hard_failures']}, continuity suspects: {rep['suspects']}")
    return 1 if rep["hard_failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
