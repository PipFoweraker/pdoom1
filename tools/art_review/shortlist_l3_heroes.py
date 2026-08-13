#!/usr/bin/env python3
"""shortlist_l3_heroes.py -- turn 140 flat hero candidates into an ordered shortlist.

Layer: REVIEW (read-only over art, verdicts and the OCR scan; writes a report
and an HTML sheet, and NOTHING else). It does not pick. Pip picks.

WHY THIS EXISTS, AND WHY IT IS NOT rank_l3_picks.py
---------------------------------------------------
``rank_l3_picks.py`` ranks L1 *keeps* to decide WHICH GET HERO MONEY -- it is the
thing that produced these 140 images. It ranks inputs. This ranks outputs, which
is a different job and had no tool.

The 140 L3 heroes have ZERO verdicts (measured 2026-08-13). Presented flat they
are 140 equal-looking thumbnails; the point of this file is to impose enough
structure that a human eye starts somewhere useful, WITHOUT asserting a winner.

THE RANKING, AND WHERE IT IS WEAK
---------------------------------
1. HARD EXCLUSIONS FIRST, because no score should outvote these:
   * subject s07 entirely -- "stacked application forms in labelled trays ... a
     date stamp". 11 of its 12 L1 images leaked legible text (91.7% against 7.0%
     for the night). A prompt clause does not beat a subject made of printing.
   * any image the OCR scan flagged at conf >= 0.60. A hero with legible
     lettering on it is the single most expensive mistake available here.
2. Ranked on the only two axes ``docs/design/TASTE_PROFILE_2026-08-06.md``
   measured as significant -- contrast and detail density -- computed by
   importing ``measure_taste.measure`` itself, so the two files cannot drift.
   Composition and saturation are measured NULLS there and are NOT ranked on.
3. Standardised WITHIN palette, not globally. Scored globally, the same proxy
   put 22 of 28 picks in one palette because a light ground with dark ink
   mechanically maximises both luminance spread and gradient magnitude -- it was
   measuring PALETTE, not quality. This is that lesson, inherited.
4. Caps (3 per subject, 5 per palette) stop the shortlist collapsing to one look.

FOUR HONEST WEAKNESSES
----------------------
  * The taste profile measured those axes PAIRED WITHIN ICON SLOTS at 128x128.
    Applying them to full-bleed 1536px posters is an EXTRAPOLATION, not a
    replication. It has never been validated at this size.
  * Contrast and detail density are proxies for "reads well", not measures of
    it. Nothing here can see composition, subject legibility, or whether the
    reserved title space actually works -- which is most of what a hero is for.
  * OCR is a LOWER BOUND on text leakage. A clean scan is evidence of absence,
    not proof. Small, stylised or occluded lettering is missed.
  * The score has never been checked against a human ranking of these images,
    because no human ranking of these images exists yet. Until it does, treat
    the ORDER as a reading order and not as a quality claim.

USAGE
-----
    python tools/art_review/shortlist_l3_heroes.py
    python tools/art_review/shortlist_l3_heroes.py --top 20

Writes docs/art/audit_2026-08-13/L3_HERO_SHORTLIST.md and, beside it,
l3_hero_shortlist.html -- open the HTML, it shows the images.
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
LEDGER = os.path.join(REPO, "art_generated", "art_night_2026-08-07", "ledger.jsonl")
STATE = os.path.join(HERE, "review_state.json")
SCAN = os.path.join(HERE, "text_scan_ALL_2026-08-13.json")
OUTDIR = os.path.join(REPO, "docs", "art", "audit_2026-08-13")

# s07 is excluded wholesale, not scored. See module docstring.
BANNED_SUBJECTS = {"s07"}
CONF_STRONG = 0.60
CAP_PER_SUBJECT = 3
CAP_PER_PALETTE = 5
CELL_RE = re.compile(r"^(s\d+)_(r\d+)_(p\d+)$")


def load_measure():
    """Import measure_taste.measure by path, so the axis definitions are shared
    rather than copied. A copy is how two files start disagreeing."""
    spec = importlib.util.spec_from_file_location(
        "measure_taste", os.path.join(HERE, "measure_taste.py")
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["measure_taste"] = mod
    spec.loader.exec_module(mod)
    return mod.measure


def load_heroes():
    """Every L3 master in the ledger, one row per (cell, variant)."""
    rows, seen = [], set()
    with open(LEDGER, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            parts = str(rec.get("job_id", "")).split("|")
            if len(parts) != 4 or parts[0] != "L3":
                continue
            level, block, cell, variant = parts
            master = str(rec.get("master_path") or "").strip().replace("\\", "/")
            if not master:
                # FAILED attempt, no image. This skip MUST precede the `seen`
                # bookkeeping: the ledger logs a failure BEFORE the retry that
                # succeeds, so registering it first evicts its own successful
                # master. 116 of the 140 L3 heroes were retried after a
                # credit-limit error, so getting this wrong drops 114 of them
                # and silently ranks 20 images as though they were the set.
                # Third occurrence of this trap in one day -- see
                # scan_text_leak.load_targets_from_ledger for the other two.
                continue
            key = (block, cell, variant)
            if key in seen:
                continue
            seen.add(key)
            m = CELL_RE.match(cell)
            rows.append(
                {
                    "asset_id": "gen:an0807_%s:%s:%s" % (block, cell, variant),
                    "block": block,
                    "cell": cell,
                    "variant": variant,
                    "subject": m.group(1) if m else None,
                    "rendering": m.group(2) if m else None,
                    "palette": m.group(3) if m else None,
                    "relpath": master,
                    "size": rec.get("size"),
                }
            )
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--top", type=int, default=15, help="shortlist length per orientation")
    args = ap.parse_args(argv)

    measure = load_measure()
    rows = load_heroes()
    print("L3 masters in ledger: %d" % len(rows), flush=True)

    state = {}
    if os.path.exists(STATE):
        with open(STATE, encoding="utf-8") as fh:
            state = json.load(fh)

    # The report claims these heroes are unjudged. Measure it rather than assert
    # it -- if a review session has happened since, the claim must change itself.
    judged = sum(1 for r in rows if (state.get(r["asset_id"]) or {}).get("verdict"))
    print("heroes carrying a verdict: %d of %d" % (judged, len(rows)))

    flagged, scan_present = set(), os.path.exists(SCAN)
    if scan_present:
        with open(SCAN, encoding="utf-8") as fh:
            scan = json.load(fh)
        for aid, v in scan.get("assets", {}).items():
            if v.get("strong_hits"):
                flagged.add(aid)
        print("OCR scan loaded: %d assets with a strong hit" % len(flagged))
    else:
        print("WARNING: no OCR scan at %s -- text exclusions NOT applied" % SCAN)

    kept, excluded = [], []
    for r in rows:
        if not os.path.isfile(os.path.join(REPO, r["relpath"])):
            excluded.append((r, "master absent on disk"))
            continue
        if r["subject"] in BANNED_SUBJECTS:
            excluded.append((r, "subject %s banned (91.7%% L1 text leak)" % r["subject"]))
            continue
        if r["asset_id"] in flagged:
            excluded.append((r, "OCR strong hit"))
            continue
        try:
            r["m"] = measure(r["relpath"])
        except Exception as exc:  # noqa: BLE001 -- report, do not crash the run
            excluded.append((r, "measure failed: %s" % exc))
            continue
        kept.append(r)

    # contrast and detail density, standardised WITHIN palette -- see docstring
    by_pal = collections.defaultdict(list)
    for r in kept:
        by_pal[r["palette"]].append(r)

    def z(vals, x):
        if len(vals) < 2:
            return 0.0
        sd = statistics.pstdev(vals)
        return 0.0 if sd < 1e-9 else (x - statistics.fmean(vals)) / sd

    for pal, group in by_pal.items():
        contrast = [g["m"]["p95_p05"] for g in group]
        detail = [g["m"]["edge"] for g in group]
        for g in group:
            zc = z(contrast, g["m"]["p95_p05"])
            zd = z(detail, g["m"]["edge"])
            g["z_contrast"], g["z_detail"] = zc, zd
            g["score"] = zc + zd

    lines = []
    for block in ("l3_hero_land", "l3_hero_port"):
        pool = sorted([r for r in kept if r["block"] == block], key=lambda r: -r["score"])
        picked, ns, np_ = [], collections.Counter(), collections.Counter()
        for r in pool:
            if ns[r["subject"]] >= CAP_PER_SUBJECT or np_[r["palette"]] >= CAP_PER_PALETTE:
                continue
            picked.append(r)
            ns[r["subject"]] += 1
            np_[r["palette"]] += 1
            if len(picked) >= args.top:
                break
        r_block = {"block": block, "pool": pool, "picked": picked}
        lines.append(r_block)

    os.makedirs(OUTDIR, exist_ok=True)
    _write_md(lines, kept, excluded, rows, scan_present, flagged, args, judged)
    _write_html(lines, args)
    return 0


def _write_md(blocks, kept, excluded, rows, scan_present, flagged, args, judged):
    out = os.path.join(OUTDIR, "L3_HERO_SHORTLIST.md")
    L = [
        "# L3 hero shortlist -- a reading order, not a winner",
        "",
        "**GENERATED** by `tools/art_review/shortlist_l3_heroes.py`, 2026-08-13.",
        "Regenerate: `python tools/art_review/shortlist_l3_heroes.py`",
        "",
        "**This file does not pick a hero.** It orders 140 flat candidates so a",
        "human eye starts somewhere useful. The order is a proxy for contrast and",
        "detail density, which are two things a hero needs and not the main thing.",
        "",
        "## Scope",
        "",
        "| | |",
        "|---|---|",
        "| L3 masters in ledger | %d |" % len(rows),
        "| Measured and ranked | %d |" % len(kept),
        "| Excluded | %d |" % len(excluded),
        "| OCR scan applied | %s |" % ("yes" if scan_present else "**NO -- run it**"),
        "| Images with an OCR strong hit (whole run) | %d |" % len(flagged),
        "",
        "**%d of these %d carry a review verdict** -- measured at generation time,"
        % (judged, len(rows)),
        "not asserted. The rest have never been judged by a human.",
        "",
        "## Exclusions, itemised",
        "",
    ]
    if excluded:
        why = collections.Counter(w for _, w in excluded)
        L += ["| reason | count |", "|---|---|"]
        L += ["| %s | %d |" % (w, c) for w, c in why.most_common()]
        L += ["", "Excluded assets:", ""]
        L += [
            "- `%s` -- %s" % (r["asset_id"], w)
            for r, w in sorted(excluded, key=lambda t: t[0]["asset_id"])
        ]
    else:
        L.append("None.")
    L.append("")

    for b in blocks:
        L += [
            "## %s -- top %d of %d" % (b["block"], len(b["picked"]), len(b["pool"])),
            "",
            "| # | cell | var | subject | rendering | palette | z(contrast) | z(detail) | score |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for i, r in enumerate(b["picked"], 1):
            L.append(
                "| %d | `%s` | %s | %s | %s | %s | %+.2f | %+.2f | **%+.2f** |"
                % (
                    i,
                    r["cell"],
                    r["variant"],
                    r["subject"],
                    r["rendering"],
                    r["palette"],
                    r["z_contrast"],
                    r["z_detail"],
                    r["score"],
                )
            )
        L.append("")

    L += [
        "## How to read this, and how not to",
        "",
        "**Do** use it as a reading order -- open the HTML sheet beside this file",
        "and work down. **Do not** read rank 1 as the best hero.",
        "",
        "Four weaknesses, stated so they can be argued with:",
        "",
        "1. The taste profile measured these axes **paired within icon slots at",
        "   128x128**. Applying them to full-bleed 1536px posters is an",
        "   extrapolation that has never been validated at this size.",
        "2. Contrast and detail density are proxies for *reads well*, not measures",
        "   of it. Nothing here sees composition, subject legibility, or whether",
        "   the reserved title space works -- which is most of what a hero is for.",
        "3. OCR is a **lower bound**. A clean scan is evidence of absence, not",
        "   proof; stylised or occluded lettering is missed.",
        "4. The score has never been checked against a human ranking of these",
        "   images, because none exists. The first review session is what tests it.",
        "",
        "**Scoring is standardised WITHIN palette, deliberately.** Scored globally,",
        "this same proxy once put 22 of 28 picks in a single palette, because a",
        "light ground with dark ink mechanically maximises both luminance spread",
        "and gradient magnitude. It was measuring palette, not quality.",
        "",
        "## Reminder about size",
        "",
        "`l3_hero_land` masters are **1536x1024**; `l3_hero_port` are **1024x1536**.",
        "The website hero slot is **2400px** wide. Nothing in this shortlist can",
        "fill it without an upscale step that does not exist in this pipeline.",
        "",
    ]
    with open(out, "w", encoding="ascii", errors="backslashreplace", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote", out)


def _write_html(blocks, args):
    out = os.path.join(OUTDIR, "l3_hero_shortlist.html")
    parts = [
        "<title>L3 hero shortlist -- 2026-08-13</title>",
        "<style>",
        "body{background:#141210;color:#e8dfd0;font-family:ui-monospace,Consolas,monospace;margin:0;padding:2rem}",
        "h1{font-size:1.3rem}h2{font-size:1rem;color:#d08a2c;border-bottom:1px solid #3a332b;padding-bottom:.4rem;margin-top:2.5rem}",
        ".note{color:#9a8b76;max-width:80ch;font-size:.85rem;line-height:1.6}",
        ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(520px,1fr));gap:1.4rem;margin-top:1rem}",
        ".c{background:#1d1a16;border:1px solid #3a332b;border-radius:10px;padding:.7rem}",
        ".c img{width:100%;height:auto;display:block;border-radius:6px}",
        ".m{font-size:.72rem;color:#9a8b76;margin-top:.5rem;display:flex;gap:.8rem;flex-wrap:wrap}",
        ".r{color:#d08a2c;font-weight:700}",
        "</style>",
        "<h1>L3 hero shortlist -- a reading order, not a winner</h1>",
        "<p class='note'>Generated 2026-08-13. Ordered by contrast + detail density,",
        "standardised within palette, s07 and OCR-flagged images excluded. <b>These",
        "have zero review verdicts.</b> Rank 1 is not the best hero -- it is where to",
        "start looking. Verdicts belong in the review app, not here.</p>",
    ]
    for b in blocks:
        parts.append("<h2>%s -- top %d</h2><div class='grid'>" % (b["block"], len(b["picked"])))
        for i, r in enumerate(b["picked"], 1):
            rel = "../../../" + r["relpath"]
            parts.append(
                "<div class='c'><img loading='lazy' src='%s' alt='%s'>"
                "<div class='m'><span class='r'>#%d</span><span>%s v%s</span>"
                "<span>%s / %s / %s</span><span>score %+.2f</span></div></div>"
                % (
                    rel,
                    r["cell"],
                    i,
                    r["cell"],
                    r["variant"],
                    r["subject"],
                    r["rendering"],
                    r["palette"],
                    r["score"],
                )
            )
        parts.append("</div>")
    with open(out, "w", encoding="ascii", errors="backslashreplace", newline="\n") as fh:
        fh.write("\n".join(parts) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    raise SystemExit(main())
