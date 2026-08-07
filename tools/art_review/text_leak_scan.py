#!/usr/bin/env python3
"""text_leak_scan.py -- measure how often generated art leaks legible text.

Layer: MEASURE (read-only; generates nothing, promotes nothing, casts no verdict)

WHY THIS EXISTS
---------------
The prompts ban text in the strongest terms available ("ABSOLUTELY NO TEXT
ANYWHERE IN THE IMAGE"), and text still gets through -- 17 of 244 an0807 images
(7.0%), and 11 of the 12 images of subject s07 alone (91.7%), because s07 is
literally "stacked application forms in labelled trays ... a date stamp". A ban
does not beat a subject that is made of printing.

The 2026-08-07 L2 lane produced exactly this measurement and wrote only its
OUTPUT (text_scan_art_night_2026-08-07.json) into the repo, not the code that
made it. So the number could be quoted but never re-run, on the next batch or
on any other -- which makes it an anecdote rather than an instrument. This file
is that scanner, committed, so the rate is re-measurable.

The reading is OCR, so it is a PROXY with two failure directions worth naming:
  * FALSE POSITIVES -- OCR hallucinates words out of texture, grain and the
    edges of props. The low-confidence hits in particular ("De Bg aat") are
    noise, which is why `strong_hits` (alphabetic, >=3 chars, conf >= 0.65) is
    reported separately and is the number worth acting on.
  * FALSE NEGATIVES -- text too small, too warped or too stylised to OCR is
    still text a human will see. A rate from this tool is a FLOOR, never a
    ceiling.

Usage:
    python tools/art_review/text_leak_scan.py --glob "art_generated/an0807_l3_*/v1/*_1536.png"
    python tools/art_review/text_leak_scan.py --glob "..." --out scan.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

STRONG_MIN_CONF = 0.65
STRONG_MIN_ALPHA = 3


def is_strong(text, conf):
    """A hit worth acting on: confident, and actually word-shaped.

    Deliberately stricter than "OCR returned something". A two-character blob
    at confidence 0.5 is the tool seeing letters in grain; 'APPROVED' at 0.86
    is a legend that really is printed in the picture.
    """
    letters = re.sub(r"[^A-Za-z]", "", text)
    return conf >= STRONG_MIN_CONF and len(letters) >= STRONG_MIN_ALPHA


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--glob",
        required=True,
        action="append",
        help="glob relative to the repo root; repeatable. Repeat it rather than "
        "running the tool twice: a rate is only comparable to another rate "
        "measured by the SAME instrument, and two runs invite two thresholds.",
    )
    ap.add_argument("--out", default=None, help="write JSON here (default: stdout summary only)")
    ap.add_argument("--min-conf", type=float, default=0.30, help="floor for recording a hit at all")
    args = ap.parse_args()

    paths = sorted({p for g in args.glob for p in REPO.glob(g)})
    if not paths:
        print(f"[ABORT] no files matched {args.glob!r} under {REPO}")
        return 2
    print(f"scanning {len(paths)} images ...")

    import easyocr

    reader = easyocr.Reader(["en"], gpu=False, verbose=False)

    assets, any_hit, strong_any = {}, 0, 0
    for i, p in enumerate(paths, 1):
        hits = []
        for _box, text, conf in reader.readtext(str(p)):
            text = text.strip()
            if not text or conf < args.min_conf:
                continue
            hits.append({"conf": round(float(conf), 4), "text": text})
        strong = sum(1 for h in hits if is_strong(h["text"], h["conf"]))
        assets[str(p.relative_to(REPO)).replace("\\", "/")] = {
            "hits": hits,
            "strong_hits": strong,
        }
        if hits:
            any_hit += 1
        if strong:
            strong_any += 1
        if i % 20 == 0 or i == len(paths):
            print(f"  [{i}/{len(paths)}] any={any_hit} strong={strong_any}")

    n = len(paths)
    out = {
        "glob": args.glob,
        "n_images": n,
        "any_hit_count": any_hit,
        "any_hit_rate": round(any_hit / n, 4),
        "strong_hit_count": strong_any,
        "strong_hit_rate": round(strong_any / n, 4),
        "strong_rule": f"conf >= {STRONG_MIN_CONF} and >= {STRONG_MIN_ALPHA} letters",
        "caveat": "OCR proxy. Hallucinates on texture (false positives, mostly "
        "low-confidence) and misses small/warped/stylised text (false "
        "negatives). Treat the rate as a floor, not a ceiling.",
        "assets": assets,
    }
    print("")
    print(f"images        : {n}")
    print(f"any OCR hit   : {any_hit}  ({any_hit / n:.1%})")
    print(f"STRONG hits   : {strong_any}  ({strong_any / n:.1%})   <- the number worth acting on")
    if args.out:
        Path(args.out).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
