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
import re
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


def load_targets_from_ledger(repo_root, run_id):
    """EVERY master in the run's ledger, reviewed or not, at every level.

    Why this exists (2026-08-13): load_targets() above walks review_state and
    skips anything not in it, then skips L2/L3 outright. That was correct for the
    share-set gate it was built for -- you can only promote what you reviewed.
    It is exactly wrong for a pre-publication sweep, because the material most
    likely to reach a public surface on Friday is the hero art, which is L3 and
    has ZERO verdicts. The old path could not see a single hero.

    Verdict is looked up where one exists and left None otherwise, so an
    unreviewed leak is still reported rather than dropped for lacking a verdict.
    """
    state_path = os.path.join(repo_root, "tools", "art_review", "review_state.json")
    state = {}
    if os.path.exists(state_path):
        with open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)

    ledger_path = os.path.join(repo_root, "art_generated", run_id, "ledger.jsonl")
    targets = []
    seen = set()
    with open(ledger_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            job_id = rec.get("job_id", "")
            parts = job_id.split("|")
            if len(parts) != 4:
                continue
            level, short, cell, variant = parts
            master = str(rec.get("master_path") or "").strip().replace("\\", "/")
            if not master:
                # A FAILED attempt. Two traps here, both hit on 2026-08-13:
                #  1. A blank master_path joins to the REPO ROOT, which is a real
                #     directory -- os.path.exists() says True and PIL then dies
                #     opening a folder. Hence isfile() below, not exists().
                #  2. This skip MUST come before the `seen` bookkeeping. Failed
                #     attempts are logged BEFORE the retry that succeeds, so
                #     adding them to `seen` first evicts their own successful
                #     master. That silently dropped 116 of 1,098 images -- every
                #     one of the L3 heroes retried after the credit-limit error.
                continue
            # ledger job_ids carry no batch prefix; review_state keys do.
            asset_id = "gen:an0807_%s:%s:%s" % (short, cell, variant)
            if asset_id in seen:
                continue  # same master listed twice; scan it once
            seen.add(asset_id)
            path = os.path.join(repo_root, master)
            verdict = (state.get(asset_id) or {}).get("verdict")
            targets.append((asset_id, verdict, path))
    return sorted(targets)


_RES_SET = {"2048", "1536", "1024", "768", "512", "256", "128", "64", "48", "32"}


def load_targets_from_tree(repo_root, batches=None, tracked_only=False):
    """Every reviewable cell in art_generated/, ledger or no ledger.

    Why (2026-08-13): the ledger path only covers the 2026-08-07 art night. The
    534 files that are TRACKED and already on a public remote predate it, belong
    to batches with no ledger at all, and had never been text-scanned by anything.
    Public and unscanned is the worst combination available, so it needed a path.

    Cell enumeration is delegated to serve_review.scan_generated so the asset_ids
    match review_state exactly and the results can be joined back into the review
    app. Each cell is then upgraded from its display proxy (usually 512px) to the
    LARGEST resolution on disk -- OCR is already a lower bound on leakage, and
    scanning a downscale would loosen that bound for no gain.
    """
    import importlib.util
    import pathlib

    spec = importlib.util.spec_from_file_location(
        "serve_review", os.path.join(os.path.dirname(os.path.abspath(__file__)), "serve_review.py")
    )
    sr = importlib.util.module_from_spec(spec)
    sys.modules["serve_review"] = sr
    spec.loader.exec_module(sr)

    root = pathlib.Path(repo_root).resolve()
    tracked = None
    if tracked_only:
        import subprocess

        out = subprocess.run(
            ["git", "ls-files", "art_generated"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        tracked = {line.strip() for line in out.splitlines() if line.strip()}

    state_path = os.path.join(repo_root, "tools", "art_review", "review_state.json")
    state = {}
    if os.path.exists(state_path):
        with open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)

    targets = []
    for sec in sr.scan_generated(root):
        for cell in sec["cells"]:
            rel = cell["img"]
            if batches and rel.split("/")[1] not in batches:
                continue
            best, best_px = rel, -1
            d = root / os.path.dirname(rel)
            stem = os.path.basename(rel)
            m = re.match(r"^(.*)_(\d+)\.(png|webp|jpg|jpeg)$", stem, re.I)
            if m and d.is_dir():
                prefix, _, ext = m.groups()
                for cand in d.glob("%s_*.%s" % (prefix, ext)):
                    cm = re.match(r"^.*_(\d+)\.[^.]+$", cand.name)
                    # guard on a KNOWN resolution set: a filename ending in a
                    # number is not necessarily a resolution (the .mp4 "_38"
                    # trap). Anything else is left at the display proxy.
                    if not (cm and cm.group(1) in _RES_SET):
                        continue
                    candrel = os.path.relpath(str(cand), str(root)).replace("\\", "/")
                    # In tracked-only mode the question is "what is PUBLIC", so
                    # only tracked files are eligible at all. The public files
                    # are frequently the SMALL ones -- 32/48px icons are tracked
                    # while the 1024 master beside them is gitignored -- so
                    # picking the largest and then filtering drops most of the
                    # actually-exposed set. Measured: 116 cells that way against
                    # the true figure below.
                    if tracked is not None and candrel not in tracked:
                        continue
                    if int(cm.group(1)) > best_px:
                        best_px = int(cm.group(1))
                        best = candrel
            if tracked is not None and best not in tracked:
                continue
            targets.append(
                (
                    cell["asset_id"],
                    (state.get(cell["asset_id"]) or {}).get("verdict"),
                    os.path.join(repo_root, best),
                )
            )
    return sorted(set(targets))


def load_targets_tracked_files(repo_root):
    """EVERY git-tracked image under art_generated/ -- the set that is PUBLIC.

    Deliberately NOT cell-based. Two reasons, both measured 2026-08-13:

    1. Cells collapse a family to one representative, but every tracked
       resolution is separately public. If the 48px icon leaks a word and the
       512px does not, a cell-based scan can miss it depending which it picks.
    2. Some tracked batches produce no ``gen:`` cell at all -- ``scene_art_wave2``
       is 28 tracked files carried in review_state under the ``file:`` namespace.
       A cell walk sees zero of them. Cell-based scanning reported 123 units and
       silently omitted those.

    So: scan every tracked image, once, keyed by the review_state id where one is
    derivable and by ``file:<relpath>`` otherwise. Redundant across resolutions,
    complete, and complete is what a public-exposure question needs.
    """
    import subprocess

    out = subprocess.run(
        ["git", "ls-files", "art_generated"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    state_path = os.path.join(repo_root, "tools", "art_review", "review_state.json")
    state = {}
    if os.path.exists(state_path):
        with open(state_path, encoding="utf-8") as fh:
            state = json.load(fh)

    targets = []
    for rel in sorted(line.strip() for line in out.splitlines() if line.strip()):
        if not rel.lower().endswith((".png", ".webp", ".jpg", ".jpeg")):
            continue
        path = os.path.join(repo_root, rel)
        if not os.path.isfile(path):
            continue
        key = "file:" + rel
        verdict = (state.get(key) or {}).get("verdict")
        targets.append((key, verdict, path))
    return targets


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run-id", default=DEFAULT_RUN)
    ap.add_argument("--repo-root", default=REPO_ROOT)
    ap.add_argument("--out", default=None)
    ap.add_argument(
        "--from-tree",
        action="store_true",
        help="scan every cell in art_generated/ (batches with no ledger too)",
    )
    ap.add_argument(
        "--tracked-files",
        action="store_true",
        help="scan EVERY git-tracked image under art_generated -- the public set",
    )
    ap.add_argument(
        "--batches", default=None, help="comma-separated batch dirs to limit --from-tree"
    )
    ap.add_argument(
        "--tracked-only",
        action="store_true",
        help="with --from-tree, scan ONLY git-tracked files -- the ones already public",
    )
    ap.add_argument(
        "--from-ledger",
        action="store_true",
        help="scan EVERY master in the ledger (all levels, reviewed or not) "
        "instead of only reviewed L0/L1 assets. Use before publishing.",
    )
    args = ap.parse_args(argv)

    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        print("ERROR: rapidocr-onnxruntime is not installed.", file=sys.stderr)
        print("  python -m pip install rapidocr-onnxruntime", file=sys.stderr)
        return 2

    if args.tracked_files:
        targets = load_targets_tracked_files(args.repo_root)
        scope = "every git-tracked image under art_generated (the PUBLIC set)"
    elif args.from_tree:
        batches = set(b.strip() for b in args.batches.split(",")) if args.batches else None
        targets = load_targets_from_tree(args.repo_root, batches, args.tracked_only)
        scope = "art_generated tree walk%s%s" % (
            " (TRACKED/public only)" if args.tracked_only else "",
            " limited to %s" % sorted(batches) if batches else "",
        )
    elif args.from_ledger:
        targets = load_targets_from_ledger(args.repo_root, args.run_id)
        scope = "ALL ledger masters (every level, reviewed or not)"
    else:
        targets = load_targets(args.repo_root, args.run_id)
        scope = "reviewed L0/L1 assets only"
    if not targets:
        print("ERROR: no assets found for run %s" % args.run_id, file=sys.stderr)
        return 2
    print("scope: %s -- %d masters" % (scope, len(targets)), flush=True)

    missing = [p for _, _, p in targets if not os.path.isfile(p)]
    if missing:
        print("WARNING: %d master(s) absent, skipped" % len(missing), file=sys.stderr)

    ocr = RapidOCR()
    scanned = {}
    start = time.time()
    for i, (asset_id, verdict, path) in enumerate(targets):
        if not os.path.isfile(path):
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
        "scope": scope,
        "from_ledger": bool(args.from_ledger),
        "from_tree": bool(args.from_tree),
        "tracked_only": bool(args.tracked_only),
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
