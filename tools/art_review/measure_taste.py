#!/usr/bin/env python3
"""measure_taste.py -- what the slot picks say about taste, measured.

READ-ONLY. Writes nothing, moves nothing, generates no art. It opens the
chosen file and its rejected siblings for each contested slot, measures both,
and reports the paired comparison.

    python tools/art_review/measure_taste.py

Why paired: a chosen image on its own tells you almost nothing (an icon is
dark because icons are dark). A chosen image NEXT TO the two near-identical
siblings it beat isolates the difference that decided it. Every statistic
below is therefore "chosen minus the mean of the rejected, within one slot",
counted across slots -- a sign test, n = number of contested slots.

Method notes that limit what the numbers mean:

  * Candidates are resampled to a COMMON 128x128 canvas before measuring.
    Without that, a 32px source and a 512px source in the same cluster get
    measured at different resolutions and the downscaling itself changes
    contrast and gradient magnitude. `--native` reproduces the uncontrolled
    version for comparison.
  * "Detail density" is the mean luminance-gradient magnitude on that canvas.
    It is a PROXY. It rises with texture, grain, and edge count alike, and it
    cannot tell "richly rendered" from "noisy". PNG bytes-per-pixel is
    reported as a second, independent proxy precisely because it fails
    differently (it also rises with dithering and falls with flat alpha).
  * Clustering is copied from the retired slot_model.role_stem heuristic and
    carries its warning: a cluster means "these definitely compete", never
    "nothing else competes".
  * Alpha: metrics are taken over opaque pixels where an alpha channel is
    meaningfully used, over all pixels otherwise. A cutout icon on
    transparency would otherwise read as very dark and very high contrast.

Source of truth for the picks: tools/assets/demand/slot_picks.json (or the
dated session copy). This script never writes to it.
"""

import argparse
import json
import math
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

PICK_CANDIDATES = (
    "tools/assets/demand/slot_picks.json",
    "tools/assets/demand/slot_picks.json.pips-session-2026-08-06",
)

CANVAS = 128

_SIZE_TOK = re.compile(r"_(\d{2,4})$")
_VAR_TOK = re.compile(r"_v\d+")
_DATE_TOK = re.compile(r"_\d{8}$")


def role_stem(filename):
    """Collapse a filename to its ROLE. Copied from the slot_model heuristic."""
    stem = Path(filename).stem
    stem = _DATE_TOK.sub("", stem)
    stem = _SIZE_TOK.sub("", stem)
    stem = _VAR_TOK.sub("", stem)
    return _SIZE_TOK.sub("", stem)


def variant_num(filename):
    vm = re.findall(r"_v(\d+)", Path(filename).stem)
    return int(vm[-1]) if vm else 1


def load_picks(path=None):
    if path:
        return json.loads(Path(path).read_text())
    for rel in PICK_CANDIDATES:
        p = REPO / rel
        if p.exists():
            print("picks: %s" % rel)
            return json.loads(p.read_text())
    sys.exit("error: no slot_picks.json found (looked in %s)" % ", ".join(PICK_CANDIDATES))


# Pools read DIRECTORIES as variety pools, so they have no single winner and
# never enter the picker (ADR-0019 pt 3). Copied from the retired slot_model.
POOL_DEST_PREFIXES = (
    "godot/assets/office_floor/",
    "godot/assets/cats/",
    "godot/assets/effects/doom_overlays",
    "godot/assets/portraits/",
)

FRAME_ROLE_STEMS = (
    "ui_frame_corner_tl",
    "ui_frame_corner_tr",
    "ui_frame_corner_bl",
    "ui_frame_corner_br",
    "ui_frame_top",
    "ui_frame_bottom",
    "ui_frame_left",
    "ui_frame_right",
    "doom_meter_frame",
    "frame_button",
    "frame_panel_plain",
    "frame_panel_ornate",
    "crt_frame_bezel_heavy",
    "crt_frame_curved_glass",
    "crt_frame_vignette_light",
)


def build_clusters(picks):
    """Re-derive the contested slots the picker showed.

    Uses apply_review's OWN promotable set, so the candidate list is
    byte-identical to what the promotion gate reports -- the same move
    slot_model.py made before it was retired. The clustering rules
    (role_stem, pool exemption, frame-role split) are inlined copies of
    slot_model's, which is why this script re-derives 136 slots rather than
    trusting the picks file's own count.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import apply_review

    state = apply_review.load_state(REPO / apply_review.DEFAULT_STATE)
    assets = apply_review.parse_assets(state, REPO)
    keeps = [a for a in assets if a.verdict == "keep"]
    buckets, _blocked, _contested = apply_review._promotion_gate(keeps)

    roles = defaultdict(list)
    for a in buckets["promotable"]:
        dest = a.dest_rule()
        if any(dest.startswith(p) for p in POOL_DEST_PREFIXES):
            continue
        for src in a.promote_sources():
            rel = src.relative_to(REPO).as_posix()
            stem = role_stem(src.name)
            if stem in FRAME_ROLE_STEMS:
                continue
            roles[(dest, stem)].append(rel)

    clusters = {}
    for (dest, stem), cands in roles.items():
        if len(cands) < 2:
            continue
        slot = "%s/%s" % (dest, stem)
        pick = picks["slots"].get(slot)
        if not pick:
            print("  warn: no pick recorded for contested slot %s" % slot)
            continue
        clusters[slot] = (pick["source_file"], sorted(cands), dest)
    return clusters


def measure(relpath, native=False):
    import numpy as np
    from PIL import Image

    p = REPO / relpath
    im = Image.open(p).convert("RGBA")
    w, h = im.size
    if native:
        im.thumbnail((256, 256), Image.LANCZOS)
    else:
        im = im.resize((CANVAS, CANVAS), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255.0
    alpha, rgb = a[..., 3], a[..., :3]
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    opaque = alpha > 0.5
    fo = float(opaque.mean())
    m = opaque if fo > 0.02 else np.ones_like(opaque)
    L = lum * (alpha if fo > 0.02 else 1.0)
    gy, gx = np.gradient(L)
    grad = np.hypot(gx, gy)
    W = np.abs(L - np.median(L))
    tot = W.sum()
    H, Wd = L.shape
    ys, xs = np.mgrid[0:H, 0:Wd]
    cx = float((W * xs).sum() / tot) / max(Wd - 1, 1) if tot > 1e-6 else 0.5
    cy = float((W * ys).sum() / tot) / max(H - 1, 1) if tot > 1e-6 else 0.5
    return {
        "src_w": w,
        "vnum": variant_num(p.name),
        "lum": float(lum[m].mean()),
        "lum_sd": float(lum[m].std()),
        "p95_p05": float(np.percentile(lum[m], 95) - np.percentile(lum[m], 5)),
        "sat": float(sat[m].mean()),
        "edge": float(grad.mean()),
        "bpp": p.stat().st_size / float(w * h),
        "offcentre": math.hypot(cx - 0.5, cy - 0.5),
    }


def binom_p(k, n):
    if n == 0:
        return 1.0
    pmf = [math.comb(n, i) * 0.5**n for i in range(n + 1)]
    return min(1.0, sum(x for x in pmf if x <= pmf[k] + 1e-12))


METRICS = [
    ("lum_sd", "contrast (luminance sd)"),
    ("p95_p05", "contrast (p95 - p05)"),
    ("edge", "detail density (grad)"),
    ("lum", "luminance"),
    ("sat", "saturation"),
    ("bpp", "PNG bytes/pixel"),
    ("offcentre", "off-centre distance"),
]


def sign_test(groups, metric):
    up = dn = 0
    deltas = []
    for chosen_m, rejected_m in groups:
        d = chosen_m[metric] - sum(r[metric] for r in rejected_m) / len(rejected_m)
        deltas.append(d)
        if d > 1e-12:
            up += 1
        elif d < -1e-12:
            dn += 1
    return up, dn, (sum(deltas) / len(deltas) if deltas else 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--picks")
    ap.add_argument(
        "--native", action="store_true", help="measure at source resolution (uncontrolled)"
    )
    ap.add_argument(
        "--perm", type=int, default=1000, help="permutation-null iterations (0 to skip)"
    )
    args = ap.parse_args()

    picks = load_picks(args.picks)
    clusters = build_clusters(picks)
    print(
        "contested slots reconstructed: %d (picks file records %d)"
        % (len(clusters), len(picks["slots"]))
    )

    cache = {}
    groups = []
    ladder = []
    meta = []
    for slot, (chosen, cands, dest) in sorted(clusters.items()):
        ms = {}
        for rel in cands:
            if rel not in cache:
                cache[rel] = measure(rel, args.native)
            ms[rel] = cache[rel]
        rej = [ms[r] for r in cands if r != chosen]
        if not rej:
            continue
        groups.append((ms[chosen], rej))
        meta.append((slot, dest, chosen, cands, ms))
        ladder.append(len(set(m["src_w"] for m in ms.values())) > 1)

    print("\n=== paired sign test: chosen vs mean(rejected), per slot ===")
    print(
        "canvas: %s"
        % ("source resolution (uncontrolled)" if args.native else "common %dx%d" % (CANVAS, CANVAS))
    )
    print("%-26s %5s %6s %7s %11s %8s" % ("metric", "n", "up", "up%", "mean delta", "p"))
    for m, label in METRICS:
        up, dn, md = sign_test(groups, m)
        n = up + dn
        print(
            "%-26s %5d %6d %6.1f%% %+11.4f %8.4f"
            % (label, n, up, 100.0 * up / n, md, binom_p(up, n))
        )

    sub = [g for g, is_ladder in zip(groups, ladder) if not is_ladder]
    print("\n--- excluding the %d size-ladder slots (same art at many px) ---" % sum(ladder))
    for m, label in METRICS:
        up, dn, md = sign_test(sub, m)
        n = up + dn
        print(
            "%-26s %5d %6d %6.1f%% %+11.4f %8.4f"
            % (label, n, up, 100.0 * up / n, md, binom_p(up, n))
        )

    if args.perm:
        print("\n=== permutation null: %d draws of a random winner per slot ===" % args.perm)
        random.seed(7)
        allsets = [[ms[r] for r in cands] for _, _, _, cands, ms in meta]
        for m, label in METRICS:
            up, dn, _ = sign_test(groups, m)
            obs = up / max(up + dn, 1)
            dist = []
            for _ in range(args.perm):
                gg = []
                for s in allsets:
                    w = random.choice(s)
                    gg.append((w, [x for x in s if x is not w]))
                u, d, _ = sign_test(gg, m)
                dist.append(u / max(u + d, 1))
            mu = sum(dist) / len(dist)
            sd = (sum((x - mu) ** 2 for x in dist) / len(dist)) ** 0.5
            pp = (sum(1 for x in dist if abs(x - mu) >= abs(obs - mu)) + 1) / (len(dist) + 1)
            print("%-26s observed %.3f  null %.3f +/- %.3f  perm p=%.4f" % (label, obs, mu, sd, pp))

    print("\n=== lineage: did the variant number decide anything? ===")
    hi = lo = mid = flat = 0
    exp_hi = exp_lo = 0.0
    for slot, dest, chosen, cands, ms in meta:
        vs = [ms[r]["vnum"] for r in cands]
        if len(set(vs)) == 1:
            flat += 1
            continue
        cv = ms[chosen]["vnum"]
        exp_hi += vs.count(max(vs)) / len(vs)
        exp_lo += vs.count(min(vs)) / len(vs)
        if cv == max(vs):
            hi += 1
        elif cv == min(vs):
            lo += 1
        else:
            mid += 1
    n = hi + lo + mid
    print("slots where variant numbers differ: %d (uniform-variant slots: %d)" % (n, flat))
    print("  chose highest vN: %3d   (random expectation %.1f)" % (hi, exp_hi))
    print("  chose lowest  vN: %3d   (random expectation %.1f)" % (lo, exp_lo))
    print("  chose middle  vN: %3d" % mid)
    print("  binomial p, highest vs lowest: %.4f" % binom_p(hi, hi + lo))


if __name__ == "__main__":
    main()
