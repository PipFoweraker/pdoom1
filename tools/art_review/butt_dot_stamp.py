"""Stamp the anatomical dot onto butt-flash frames (issue #913 follow-up).

Pip's 2026-07-26 review: the butt-flash rear frames "added a butt element
without the little starfish... that should punctuate it". Generation cannot
reliably hit 1-2px precision, so this is the deterministic fallback: a PIL
post-process stamping a small dark dot on the rump of the tail-up frames of
a north-facing butt-flash clip.

Geometry (from the tabby clip forensics): north = walking away, head at the
TOP of the sprite, rump at the BOTTOM; on flash frames the raised tail runs
UP OVER the back, so "beneath the raised tail" = the bottom-centre of the
rump mass, just above the outline edge, between the hind legs.

Anchor algorithm (per stamped frame):
- body mask = alpha > 128;
- scanning rows bottom-up, compute runs of consecutive opaque pixels; the
  first row whose longest single run >= RUMP_MIN_RUN is the rump bottom
  (leg rows below it split into two short runs and are skipped);
- dot = DOT_W x DOT_H at (run centre, rump_bottom - DOT_UP), drawn only
  over already-opaque pixels so it can never halo.

The flash window (which frames show the raised tail) differs per clip, so it
is passed explicitly after eyeballing the filmstrip -- deliberate: a human
picks WHICH frames get punctuated, the stamp itself is deterministic.

Usage:
  python tools/art_review/butt_dot_stamp.py SRC_DIR DST_DIR FRAMES
      SRC_DIR: direction folder of butt-flash frames
      DST_DIR: output folder (created; all frames copied, FRAMES stamped)
      FRAMES:  comma list / ranges of frame indices, e.g. "4-8" or "2,4-8"
Prints per-frame decisions.
"""

import sys
from pathlib import Path

from PIL import Image

RUMP_MIN_RUN = 12
DOT_W = 2
DOT_H = 1
DOT_UP = 2  # rows above the rump-bottom outline row
DOT_RGBA = (43, 26, 23, 255)  # dark warm brown -- default for light/mid coats
DOT_RGBA_DARKCOAT = (98, 62, 58, 255)  # muted pink-brown -- reads on black fur
DARKCOAT_LUMA = 60  # local body brightness below this = dark coat
ALPHA_MIN = 128


def parse_frames(spec: str) -> set[int]:
    out: set[int] = set()
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return out


def runs_of(row: list[bool]) -> list[tuple[int, int]]:
    """[(start, length), ...] of True runs."""
    out = []
    start = None
    for i, v in enumerate(row + [False]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            out.append((start, i - start))
            start = None
    return out


def stamp_frame(src: Path, dst: Path) -> str:
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    px = im.load()
    for y in range(h - 1, -1, -1):
        row = [px[x, y][3] > ALPHA_MIN for x in range(w)]
        rr = runs_of(row)
        if not rr:
            continue
        start, length = max(rr, key=lambda t: t[1])
        if length >= RUMP_MIN_RUN:
            cx = start + length // 2
            oy = y - DOT_UP
            # contrast-aware shade: sample the 5x5 body neighbourhood; a dark
            # coat (black cat) gets the lighter pink-brown so the dot reads
            samples = [
                min(px[cx + dx, oy + dy][:3])
                for dx in range(-2, 3)
                for dy in range(-2, 3)
                if 0 <= cx + dx < w and 0 <= oy + dy < h and px[cx + dx, oy + dy][3] > ALPHA_MIN
            ]
            local = sum(samples) // len(samples) if samples else 255
            colour = DOT_RGBA_DARKCOAT if local < DARKCOAT_LUMA else DOT_RGBA
            stamped = 0
            for dy in range(DOT_H):
                for dx in range(DOT_W):
                    x0 = cx - DOT_W // 2 + dx
                    y0 = oy + dy
                    if 0 <= x0 < w and 0 <= y0 < h and px[x0, y0][3] > ALPHA_MIN:
                        px[x0, y0] = colour
                        stamped += 1
            im.save(dst)
            return f"stamped {stamped}px at ({cx},{oy})"
    im.save(dst)
    return "skipped: no rump run found"


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    src_dir, dst_dir, frame_spec = Path(argv[0]), Path(argv[1]), argv[2]
    frames = parse_frames(frame_spec)
    dst_dir.mkdir(parents=True, exist_ok=True)
    for i, f in enumerate(sorted(src_dir.glob("*.png"))):
        if i in frames:
            verdict = stamp_frame(f, dst_dir / f.name)
        else:
            Image.open(f).save(dst_dir / f.name)
            verdict = "copied (outside flash window)"
        print(f"{f.name}: {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
