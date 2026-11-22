#!/usr/bin/env python3
"""sample_palette.py -- read UI-skin colour tokens out of a mockup image, with provenance.

WHY: a skin is a handful of colour tokens (see godot/data/ui_skins.json). Eyeballing hex
values from a screenshot drifts; sampling them makes every token traceable to a box in a
named source image, so a designer can say "that panel is wrong" and we can say which
pixels it came from and re-sample.

SPEC (JSON): {"image": "<path>", "tokens": {"<name>": {"box": [x0,y0,x1,y1], "mode": M}}}
  mode "bg"        -- per-channel median of the box. For flat fills: panels, page bg.
  mode "fg"        -- mean of the 10% of pixels most different from the box median.
                      For thin things on a fill: text, hairline rules, pip outlines.
  mode "gradient"  -- `stops` evenly spaced medians down the box (vertical), for a
                      gradient fill. Emits a list of hex stops, top to bottom.

USAGE:
  python tools/ui_skins/sample_palette.py SPEC.json            # print token -> hex
  python tools/ui_skins/sample_palette.py SPEC.json --json     # machine-readable
  python tools/ui_skins/sample_palette.py SPEC.json --swatch out.png
      # writes a swatch sheet: each token's source crop beside its sampled colour,
      # so a wrong box is visible at a glance (the negative control for this tool).

Source mockups are NOT committed (third-party art, >1MB policy); pass their path.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def _hex(rgb) -> str:
    return "#%02x%02x%02x" % tuple(int(round(c)) for c in rgb[:3])


def _pixels(im):
    # Pillow 12 deprecates getdata(); get_flattened_data() replaces it.
    fn = getattr(im, "get_flattened_data", None)
    return list(fn() if fn else im.getdata())


def _median(pixels):
    chans = list(zip(*pixels))
    out = []
    for c in chans[:3]:
        s = sorted(c)
        out.append(s[len(s) // 2])
    return tuple(out)


def _dist(a, b) -> float:
    return sum((x - y) ** 2 for x, y in zip(a[:3], b[:3])) ** 0.5


def resolve_image(name: str, images_dir: Path | None) -> Path:
    p = Path(name)
    return p if p.is_absolute() or images_dir is None else images_dir / p


def sample(img: Image.Image, box, mode: str, stops: int = 2):
    crop = img.crop(tuple(box)).convert("RGB")
    pixels = _pixels(crop)
    if not pixels:
        raise ValueError(f"empty box {box}")
    if mode == "bg":
        return _hex(_median(pixels))
    if mode == "fg":
        med = _median(pixels)
        ranked = sorted(pixels, key=lambda p: _dist(p, med), reverse=True)
        top = ranked[: max(1, len(ranked) // 10)]
        return _hex(tuple(sum(c) / len(top) for c in zip(*top)))
    if mode == "gradient":
        w, h = crop.size
        out = []
        band = max(1, h // (stops * 4))
        for i in range(stops):
            y = int(i * (h - band) / max(1, stops - 1))
            strip = _pixels(crop.crop((0, y, w, y + band)))
            out.append(_hex(_median(strip)))
        return out
    raise ValueError(f"unknown mode {mode!r}")


def swatch(img: Image.Image, tokens: dict, results: dict, out: Path) -> None:
    row_h, crop_w, sw_w = 48, 220, 120
    sheet = Image.new("RGB", (crop_w + sw_w + 420, row_h * len(tokens)), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for i, (name, spec) in enumerate(tokens.items()):
        y = i * row_h
        crop = img.crop(tuple(spec["box"])).convert("RGB")
        crop.thumbnail((crop_w, row_h - 4))
        sheet.paste(crop, (0, y + 2))
        val = results[name]
        cols = val if isinstance(val, list) else [val]
        seg = sw_w // len(cols)
        for j, c in enumerate(cols):
            d.rectangle(
                [crop_w + j * seg, y + 2, crop_w + (j + 1) * seg - 1, y + row_h - 3], fill=c
            )
        d.text(
            (crop_w + sw_w + 10, y + 16),
            f"{name}  {val}  ({spec.get('mode', 'bg')})",
            fill=(230, 230, 230),
        )
    sheet.save(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spec", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--swatch", type=Path)
    ap.add_argument(
        "--images", type=Path, help="directory holding the mockups (spec names a bare filename)"
    )
    args = ap.parse_args(argv)

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    img = Image.open(resolve_image(spec["image"], args.images))
    results = {}
    for name, t in spec["tokens"].items():
        results[name] = sample(img, t["box"], t.get("mode", "bg"), t.get("stops", 2))

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for name, val in results.items():
            print(f"{name:<16} {val}")
    if args.swatch:
        swatch(img, spec["tokens"], results, args.swatch)
        print(f"swatch -> {args.swatch}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
