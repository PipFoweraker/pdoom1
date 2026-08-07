#!/usr/bin/env python3
"""Measure text leakage in a generated art batch, with OCR, and record the result.

WHY THIS EXISTS
---------------
The 2026-08-07 art night put a global no-text instruction in every prompt
(``docs/design/ART_RUN_2026-08-07.md``: "Text, lettering or logos. Banned in
every prompt."). The instruction is not a guarantee -- the model prints words on
props anyway. One leak was found by eye
(``an0807_l1_family/v1/s17_f01_v1_1536.png``, the word "DESICCANT" on a packet)
and the extent was unmeasured.

An image bound for a public surface is exactly where a garbled half-word is most
expensive, so the share set (``docs/copy/art_share_set.json``) refuses to promote
anything this scan flags. This script produces the evidence that gate reads.

WHAT IT MEASURES, AND WHAT IT DOES NOT
--------------------------------------
It runs RapidOCR (ONNX, CPU, no network) over each master and records every
detection verbatim with its confidence. That is a LOWER BOUND on leakage:

- OCR misses small, low-contrast, heavily stylised or partially occluded
  lettering. A clean scan is evidence of absence, not proof of it.
- OCR also FALSE-POSITIVES on texture. Grime, cable bundles and grain get read
  as letters at low confidence. That is why every hit is recorded with its text
  and confidence rather than collapsed to a boolean -- a reader can judge.

Validation performed 2026-08-07: fires on the known positive
``s17_f01_v1_1536.png`` with text "DESICCANT" at confidence 0.89, and returns
no detections on two known-clean images (``s01_f01_v1_1536.png``, a scene, and
``p01_v1_1024.png``, a swatch sheet).

DEPENDENCY
----------
``rapidocr-onnxruntime`` (pip, ~15MB, CPU-only, no torch). It is NOT a repo
dependency and NOT required by anything in CI -- this script is run by hand and
its OUTPUT is what gets committed. ``build_share_set.py`` reads the output file
and never imports OCR.

USAGE
-----
    python tools/art_review/scan_text_leak.py
    python tools/art_review/scan_text_leak.py --run-id art_night_2026-08-07

Writes ``tools/art_review/text_scan_<run_id>.json``, ASCII-only (any non-ASCII
codepoint OCR returns is backslash-escaped, per the repo ASCII rule).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_RUN = "art_night_2026-08-07"

# A hit at or above this confidence is treated as probable real lettering.
# Below it, the detection is recorded but classed as suspected texture noise.
CONF_STRONG = 0.60


def ascii_safe(text):
    """Return text with every non-ASCII codepoint backslash-escaped.

    The repo forbids non-ASCII in .json (see CLAUDE.md). OCR happily returns
    CJK and punctuation glyphs when it hallucinates on texture, so escaping is
    mandatory rather than defensive.
    """
    return text.encode("ascii", "backslashreplace").decode("ascii")


def load_targets(repo_root, run_id):
    """Every reviewed asset from the run, as (asset_id, verdict, master_path)."""
    state_path = os.path.join(repo_root, "tools", "art_review", "review_state.json")
    with open(state_path, encoding="utf-8") as fh:
        state = json.load(fh)

    ledger_path = os.path.join(repo_root, "art_generated", run_id, "ledger.jsonl")
    ledger = {}
    with open(ledger_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            ledger[rec["job_id"]] = rec

    # review_state keys are gen:<block>:<cell>:<variant>; ledger job_ids are
    # <LEVEL>|<block-without-batch-prefix>|<cell>|<variant>. The batch prefix
    # (an0807) is a review-side naming convention, not a ledger one.
    targets = []
    for key, val in state.items():
        if not key.startswith("gen:"):
            continue
        parts = key.split(":")
        if len(parts) != 4:
            continue
        _, block, cell, variant = parts
        if "_l0_" not in block and "_l1_" not in block:
            continue
        level = "L0" if "_l0_" in block else "L1"
        short = block.split("_", 1)[1] if "_" in block else block
        job_id = "%s|%s|%s|%s" % (level, short, cell, variant)
        rec = ledger.get(job_id)
        if rec is None:
            continue
        path = os.path.join(repo_root, rec["master_path"].replace("\\", "/"))
        targets.append((key, val.get("verdict"), path))
    return sorted(targets)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run-id", default=DEFAULT_RUN)
    ap.add_argument("--repo-root", default=REPO_ROOT)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        print("ERROR: rapidocr-onnxruntime is not installed.", file=sys.stderr)
        print("  python -m pip install rapidocr-onnxruntime", file=sys.stderr)
        return 2

    targets = load_targets(args.repo_root, args.run_id)
    if not targets:
        print("ERROR: no reviewed assets found for run %s" % args.run_id, file=sys.stderr)
        return 2

    missing = [p for _, _, p in targets if not os.path.exists(p)]
    if missing:
        print("WARNING: %d master(s) absent, skipped" % len(missing), file=sys.stderr)

    ocr = RapidOCR()
    scanned = {}
    start = time.time()
    for i, (asset_id, verdict, path) in enumerate(targets):
        if not os.path.exists(path):
            continue
        res, _ = ocr(path)
        hits = []
        for item in res or []:
            hits.append({"text": ascii_safe(str(item[1])), "conf": round(float(item[2]), 4)})
        scanned[asset_id] = {
            "verdict": verdict,
            "hits": hits,
            "strong_hits": sum(1 for h in hits if h["conf"] >= CONF_STRONG),
        }
        if (i + 1) % 50 == 0:
            print("  %d/%d  %.0fs" % (i + 1, len(targets), time.time() - start), flush=True)

    flagged = [k for k, v in scanned.items() if v["hits"]]
    strong = [k for k, v in scanned.items() if v["strong_hits"]]

    out_path = args.out or os.path.join(
        args.repo_root, "tools", "art_review", "text_scan_%s.json" % args.run_id
    )
    payload = {
        "schema_version": "1.0",
        "run_id": args.run_id,
        "engine": "rapidocr-onnxruntime",
        "conf_strong": CONF_STRONG,
        "scanned_count": len(scanned),
        "any_hit_count": len(flagged),
        "strong_hit_count": len(strong),
        "limits": (
            "OCR is a LOWER BOUND on leakage -- small, low-contrast or stylised "
            "lettering is missed, and texture false-positives at low confidence. "
            "A clean scan is evidence of absence, not proof of it."
        ),
        "assets": scanned,
    }
    with open(out_path, "w", encoding="ascii", newline="\n") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True, ensure_ascii=True)
        fh.write("\n")

    print(
        "scanned %d, %d with any detection, %d with a detection at conf >= %.2f"
        % (len(scanned), len(flagged), len(strong), CONF_STRONG)
    )
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
