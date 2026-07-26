"""Scan walk-clip frames for the "white flash under the cat" artifact.

Pip's 2026-07-26 cat-sweep review flagged walk clips showing "weird little
flashes of white under the cats as they walked". Frame forensics on the
disliked clips (cat refinement batch, 2026-07-26) found the generator is
intermittent pale pixels in the under-body zone, with three concrete shapes:

- a light-grey/white ground-shadow ellipse drawn in SOME frames only
  (cat_sweep_black_side_heft walk west, frames 1/4/7, RGB ~(212,198,196));
- a small stuck near-white fleck present across frames
  (cat_eldritch_r2 walk east, cluster at ~(41,36));
- cream belly-line pixels flickering in and out between frames
  (cat_b2_tabby_lowtd_heft walk east/west).

Counter-finding worth keeping: the disliked cat_black DIAGONAL clips contain
NO bright pixels at all (max in-sprite min(R,G,B) = 44) -- whatever Pip saw
there is not in-sprite white (likely floor showing through flickering leg
gaps). The scan cannot flag those; eyeball the contact strips.

Two detectors, both reported:

1. temporal flash: pixel in the lower third of the body bbox whose
   brightness (min of R,G,B, alpha-gated) reaches BRIGHT_MIN in at least one
   frame but in no more than half the frames -- i.e. it comes and goes;
2. stuck fleck: small (<= MAX_CLUSTER px) near-achromatic bright cluster
   present in MORE than half the frames -- constant matting debris.

Moving cream paws produce some legitimate temporal hits (the liked tabby
south walk scores ~71), so treat counts as a comparative signal against the
known-bad baselines (~96-145), not an absolute gate. Always confirm with an
upscaled contact strip before calling a clip clean or dirty.

Usage:
  python tools/art_review/scan_white_flash.py DIR [DIR ...]
      each DIR is a direction folder of frame PNGs (one clip)
  python tools/art_review/scan_white_flash.py --json DIR ...

Exit code 1 if any clip produced hits (comparative -- see above).
"""

import json
import sys
from pathlib import Path

from PIL import Image

BRIGHT_MIN = 140  # min(R,G,B) reaching this counts as bright
CHROMA_MAX = 30  # for the stuck-fleck achromatic gate
MAX_CLUSTER = 14  # stuck clusters bigger than this are markings, not flecks
ALPHA_MIN = 16


def load_clip(folder: Path):
    files = sorted(folder.glob("*.png"))
    frames = [Image.open(f).convert("RGBA") for f in files]
    return files, [f.load() for f in frames], (frames[0].size if frames else (0, 0))


def scan_clip(folder: Path) -> dict:
    files, pxs, (w, h) = load_clip(folder)
    n = len(pxs)
    result = {
        "clip": str(folder),
        "frames": n,
        "temporal_flash_px": 0,
        "stuck_flecks": [],
        "flash_spots": [],
    }
    if not n:
        return result
    ys = [y for p in pxs for y in range(h) for x in range(w) if p[x, y][3] > ALPHA_MIN]
    if not ys:
        return result
    top, bot = min(ys), max(ys)
    zone = top + (bot - top) * 2 // 3
    stuck_candidates = set()
    for y in range(zone, bot + 1):
        for x in range(w):
            bright_in = []
            achro_in = 0
            for i, p in enumerate(pxs):
                r, g, b, a = p[x, y]
                if a > ALPHA_MIN and min(r, g, b) >= BRIGHT_MIN:
                    bright_in.append(i)
                    if max(r, g, b) - min(r, g, b) <= CHROMA_MAX:
                        achro_in += 1
            if bright_in and len(bright_in) <= n // 2:
                result["temporal_flash_px"] += 1
                if len(result["flash_spots"]) < 12:
                    result["flash_spots"].append([x, y, len(bright_in)])
            if achro_in > n // 2:
                stuck_candidates.add((x, y))
    # cluster the stuck candidates (8-connectivity), keep small clusters
    seen: set[tuple[int, int]] = set()
    for p in stuck_candidates:
        if p in seen:
            continue
        stack, comp = [p], []
        seen.add(p)
        while stack:
            cx, cy = stack.pop()
            comp.append((cx, cy))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (cx + dx, cy + dy)
                    if q in stuck_candidates and q not in seen:
                        seen.add(q)
                        stack.append(q)
        if len(comp) <= MAX_CLUSTER:
            mx = sum(c[0] for c in comp) // len(comp)
            my = sum(c[1] for c in comp) // len(comp)
            result["stuck_flecks"].append([mx, my, len(comp)])
    return result


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    dirs = [Path(a) for a in argv if not a.startswith("--")]
    if not dirs:
        print(__doc__)
        return 2
    any_hit = False
    out = []
    for d in dirs:
        r = scan_clip(d)
        out.append(r)
        hit = r["temporal_flash_px"] > 0 or bool(r["stuck_flecks"])
        any_hit = any_hit or hit
        if not as_json:
            tag = "HITS" if hit else "ok  "
            print(
                f"[{tag}] {d}  frames={r['frames']} "
                f"temporal_flash_px={r['temporal_flash_px']} "
                f"stuck_flecks={r['stuck_flecks'] or '[]'}"
            )
            if r["flash_spots"]:
                spots = ", ".join(f"({x},{y})in{k}fr" for x, y, k in r["flash_spots"])
                print(f"        flash spots: {spots}")
    if as_json:
        print(json.dumps(out, indent=1))
    return 1 if any_hit else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
