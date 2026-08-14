#!/usr/bin/env python3
"""Render a contact sheet of reviewed assets with their notes as captions.

This is a PROJECTION over pullquotes.jsonl, not a document. It holds no copy
of its own: every caption is the verbatim note from the review log, and every
image path was resolved by extract_pullquotes.py. Change a rating or a
clearance on the atom and re-run this -- nothing here needs editing.

Captions are VERBATIM by default, per Pip's ruling: the notes were typed at
about 2.9 seconds an asset and the typos are evidence of that pace, which is
the thing the post is about. --light uses text_light where a human has
deliberately written one, and falls back to verbatim rather than inventing a
tidied version.

Usage:
    build_cull_sheet.py --verdict discard --limit 6 --out sheet.png
    build_cull_sheet.py --ids artq-024,artq-028,artq-014 --cols 3
    build_cull_sheet.py --platform bluesky --verdict discard
"""

import argparse
import json
import os
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
QUOTES = os.path.join(HERE, "pullquotes.jsonl")

CELL = 420  # thumbnail box, px
CAPTION_H = 150  # caption band under each thumbnail
PAD = 22
BG = (18, 18, 20)
FG = (238, 238, 240)
DIM = (150, 150, 158)
RULE = (60, 60, 66)


def load_font(size, bold=False):
    """Find a usable TTF, or fall back to PIL's bitmap font.

    Falling back is not silent: the caller warns, because a bitmap fallback
    changes the layout enough to be worth knowing about before posting.
    """
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
        "/usr/share/fonts/truetype/liberation/LiberationSans%s.ttf"
        % ("-Bold" if bold else "-Regular"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", help="comma-separated pull-quote ids, in order")
    parser.add_argument("--verdict", help="filter by verdict, e.g. discard")
    parser.add_argument("--category", help="filter by category")
    parser.add_argument(
        "--platform",
        help="only quotes cleared for this platform "
        "(a null clearance is NOT treated as cleared)",
    )
    parser.add_argument("--rating", help="only quotes with this rating")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--cols", type=int, default=3)
    parser.add_argument(
        "--light", action="store_true", help="prefer a deliberately-written text_light caption"
    )
    parser.add_argument(
        "--allow-ambiguous",
        action="store_true",
        help="permit images matched by name only, where the " "version could not be confirmed",
    )
    parser.add_argument("--out", default="cull_sheet.png")
    args = parser.parse_args()

    if not os.path.isfile(QUOTES):
        sys.stderr.write("no pullquotes.jsonl -- run extract_pullquotes.py first\n")
        return 2

    with open(QUOTES, encoding="utf-8") as handle:
        quotes = [json.loads(line) for line in handle if line.strip()]

    if args.ids:
        wanted = [i.strip() for i in args.ids.split(",") if i.strip()]
        index = {q["id"]: q for q in quotes}
        missing = [i for i in wanted if i not in index]
        if missing:
            sys.stderr.write("unknown id(s): %s\n" % ", ".join(missing))
            return 2
        selected = [index[i] for i in wanted]
    else:
        selected = quotes
        if args.verdict:
            selected = [q for q in selected if q["verdict"] == args.verdict]
        if args.category:
            selected = [q for q in selected if q["category"] == args.category]
        if args.rating:
            selected = [q for q in selected if q.get("rating") == args.rating]
        if args.platform:
            # A null clearance means "not yet ruled on", which is not consent.
            selected = [
                q
                for q in selected
                if isinstance(q.get("cleared_for"), list) and args.platform in q["cleared_for"]
            ]
        selected = [q for q in selected if q["image"]]
        selected = selected[: args.limit]

    if not selected:
        sys.stderr.write(
            "nothing selected. If you used --platform, note that "
            "a null cleared_for is not treated as cleared.\n"
        )
        return 1

    without_image = [q["id"] for q in selected if not q["image"]]
    if without_image:
        sys.stderr.write("no image resolved for: %s\n" % ", ".join(without_image))
        return 1

    # An image matched by name alone may be a DIFFERENT VERSION of the asset
    # than the one Pip judged, because the older sets carry no version in the
    # filename. Publishing a note next to the wrong picture is exactly the
    # kind of quiet, plausible error nobody catches downstream, so it fails
    # here unless someone says otherwise on purpose.
    ambiguous = [q["id"] for q in selected if q.get("image_match") == "name-only"]
    if ambiguous and not args.allow_ambiguous:
        sys.stderr.write(
            "REFUSING: %s matched an image by NAME ONLY, so the picture may be "
            "a different version than the one judged.\n"
            "  Pass --allow-ambiguous if you have checked them by eye.\n" % ", ".join(ambiguous)
        )
        return 1

    body = load_font(19)
    tag = load_font(15, bold=True)
    if body is None:
        sys.stderr.write(
            "WARNING: no TrueType font found; falling back to a "
            "bitmap font and the layout will differ.\n"
        )
        body = tag = ImageFont.load_default()

    cols = max(1, min(args.cols, len(selected)))
    rows = (len(selected) + cols - 1) // cols
    width = cols * CELL + (cols + 1) * PAD
    height = rows * (CELL + CAPTION_H) + (rows + 1) * PAD

    sheet = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(sheet)

    for position, quote in enumerate(selected):
        col, row = position % cols, position // cols
        x = PAD + col * (CELL + PAD)
        y = PAD + row * (CELL + CAPTION_H + PAD)

        path = os.path.join(REPO, quote["image"])
        try:
            art = Image.open(path).convert("RGBA")
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write("could not open %s: %s\n" % (quote["image"], exc))
            return 1
        art.thumbnail((CELL, CELL), Image.LANCZOS)
        tile = Image.new("RGB", (CELL, CELL), (28, 28, 32))
        tile.paste(art, ((CELL - art.width) // 2, (CELL - art.height) // 2), art)
        sheet.paste(tile, (x, y))

        draw.line([(x, y + CELL + 9), (x + CELL, y + CELL + 9)], fill=RULE, width=1)

        label = "%s  %s" % (quote["verdict"].upper(), quote["id"])
        draw.text((x, y + CELL + 20), label, font=tag, fill=DIM)

        caption = quote["text_verbatim"]
        if args.light and quote.get("text_light"):
            caption = quote["text_light"]
        wrapped = textwrap.wrap(caption, width=46)[:5]
        for line_no, line in enumerate(wrapped):
            draw.text((x, y + CELL + 46 + line_no * 22), line, font=body, fill=FG)

    out_path = args.out if os.path.isabs(args.out) else os.path.join(os.getcwd(), args.out)
    sheet.save(out_path)
    print("wrote %s  (%dx%d, %d assets)" % (out_path, width, height, len(selected)))
    print(
        "captions are %s"
        % ("text_light where written, else verbatim" if args.light else "VERBATIM")
    )
    for quote in selected:
        print("  %s  %s  %s" % (quote["id"], quote["verdict"], quote["asset"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
