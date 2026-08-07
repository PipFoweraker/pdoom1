#!/usr/bin/env python3
"""rank_l3_picks.py -- choose which 'keep' verdicts get hero money.

Layer: REVIEW (read-only over art and verdicts; writes only a picks file)
Feeds: tools/assets/run_art_night.py --wave l3 --picks <out>

WHY A RANKER AT ALL
-------------------
Pip marked 143 an0807 images 'keep'. They collapse to 132 unique
(subject, rendering, palette) cells, because that triple is all L3 regenerates.
The ceiling pays for 28. Something has to choose the other 104 away, and the
choice should be inspectable rather than a seat's taste asserted once in a
commit message.

THE RANKING, AND WHERE IT IS WEAK
---------------------------------
1. HARD EXCLUSIONS FIRST, because no ranking should be able to outvote these:
   * subject s07 entirely. s07 is "stacked application forms in labelled trays
     ... a date stamp" and 11 of its 12 L1 images leaked legible text (91.7%,
     vs 7.0% over the whole night). A prompt clause does not beat a subject
     made of printing, and hero money must not buy an image with APPROVED
     legible in it.
   * any individual image the OCR scan flagged.
2. Pip's TYPED NOTES are seeded ahead of the score. Every note on a keep is
   praise ("love this", "nice and warm"); his words outrank a pixel proxy.
3. The rest rank on the only two axes docs/design/TASTE_PROFILE_2026-08-06.md
   measured as significant -- contrast (p<0.0001) and detail density
   (p<0.0001) -- computed with measure_taste.py's OWN definitions so the two
   files cannot drift apart. Composition and saturation are measured NULLS and
   are deliberately NOT ranked on.
4. Caps (3/subject, 5/palette) stop the set collapsing into one look.

Three honest weaknesses, because a ranker that hides them is worse than none:

  * The profile measured those axes PAIRED WITHIN ICON SLOTS at 128x128.
    Applying them to full-bleed posters is an extrapolation, not a replication.
  * Scored GLOBALLY, the proxy put 22 of 28 picks in palette p06 -- the
    inverted bright-paper palette -- because a light ground with dark ink
    mechanically maximises both luminance sd and gradient magnitude. It was
    measuring PALETTE, not quality. Hence the within-palette standardisation
    below, which is the nearest available stand-in for the profile's paired
    design.
  * THE PROXY DOES NOT PREDICT PIP'S PRAISE. Of the 5 keeps he typed a note
    on, the scores are +3.38, +2.22, -1.07, -2.07, -2.46 -- averaging almost
    exactly the pool mean. n=5 is far too small to conclude anything, but there
    is no evidence here that this ranker reproduces his eye. It is a way of
    spending a fixed budget defensibly, NOT a model of his taste.
"""
import collections
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[2]

CANVAS = 128
CELL = re.compile(r"^(s\d{2})_(r\d{2})_(p\d{2})")
FAM = re.compile(r"^(s\d{2})_(f\d{2})")

state = json.loads((REPO / "tools/art_review/review_state.json").read_text(encoding="utf-8"))
spec = json.loads(
    (REPO / "tools/assets/manifests/art_night_2026-08-07.json").read_text(encoding="utf-8")
)
fams = {f["id"]: f for f in spec.get("families", [])}
tscan = json.loads(
    (REPO / "tools/art_review/text_scan_art_night_2026-08-07.json").read_text(encoding="utf-8")
)["assets"]

keeps = [
    k
    for k, r in state.items()
    if isinstance(r, dict) and "an0807" in k and str(r.get("verdict", "")).lower() == "keep"
]


def cell_of(gid):
    tail = gid.split(":")[-2]
    m = CELL.match(tail)
    if m:
        return m.groups()
    fm = FAM.match(tail)
    if fm and fm.group(2) in fams:
        f = fams[fm.group(2)]
        return (fm.group(1), f["rendering"], f["palette"])
    return None


def master_of(gid):
    _, block, tail, ver = gid.split(":")
    return REPO / "art_generated" / block / "v1" / f"{tail}_{ver}_1536.png"


def measure(p):
    im = Image.open(p).convert("RGBA").resize((CANVAS, CANVAS), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255.0
    rgb = a[..., :3]
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    gy, gx = np.gradient(lum)
    return {
        "lum_sd": float(lum.std()),
        "p95_p05": float(np.percentile(lum, 95) - np.percentile(lum, 5)),
        "edge": float(np.hypot(gx, gy).mean()),
        "lum": float(lum.mean()),
    }


rows = []
skipped = collections.Counter()
seen_cell = {}
for gid in sorted(keeps):
    c = cell_of(gid)
    if c is None:
        skipped["unparseable (palette swatch sheet, carries no s/r/p triple)"] += 1
        continue
    flagged = bool(tscan.get(gid, {}).get("hits"))
    p = master_of(gid)
    if not p.exists():
        skipped["master missing on disk"] += 1
        continue
    m = measure(p)
    rows.append(dict(gid=gid, cell=c, subject=c[0], flagged=flagged, path=str(p), **m))


# Collapse duplicate cells. A NOTED image wins the tiebreak over a
# higher-contrast sibling: the note is Pip pointing at that specific image, and
# ranking his typed words below a pixel proxy is the wrong way round. (Without
# this, "Nice altar, good stylishness" lost its cell to a sibling and dropped
# out of the hero set entirely.)
def rank_key(r):
    return (1 if state.get(r["gid"], {}).get("note") else 0, r["lum_sd"])


best = {}
for r in rows:
    prev = best.get(r["cell"])
    if prev is None or rank_key(r) > rank_key(prev):
        best[r["cell"]] = r
cands = list(best.values())
print(f"keeps={len(keeps)}  measured={len(rows)}  unique cells={len(cands)}")
for k, v in skipped.items():
    print(f"  skipped: {v}  {k}")

# ---- HARD EXCLUSIONS ------------------------------------------------------
LEAK_SUBJECTS = {"s07"}  # 11 of 12 images leaked legible text (91.7%)
excl_text, excl_subj, pool = [], [], []
for r in cands:
    if r["subject"] in LEAK_SUBJECTS:
        excl_subj.append(r)
    elif r["flagged"]:
        excl_text.append(r)
    else:
        pool.append(r)
print(f"excluded (subject s07, 91.7% measured leak): {len(excl_subj)}")
print(f"excluded (this image text-flagged)        : {len(excl_text)}")
for r in excl_text:
    print(f"    {r['gid']}")
print(f"pool remaining: {len(pool)}")


def z(vals):
    mu = sum(vals) / len(vals)
    sd = (sum((x - mu) ** 2 for x in vals) / len(vals)) ** 0.5 or 1.0
    return mu, sd


# WITHIN-PALETTE z-scores. Scoring globally put 22 of 28 picks in palette p06
# (the inverted bright-paper palette), because a light ground with dark ink
# mechanically maximises BOTH luminance sd and gradient magnitude. That is the
# metric measuring palette, not quality. The taste profile measured these axes
# PAIRED WITHIN A SLOT for exactly this reason; comparing each image only
# against others sharing its palette is the nearest available paired control.
bypal = collections.defaultdict(list)
for r in pool:
    bypal[r["cell"][2]].append(r)
for pal, grp in bypal.items():
    for key in ("lum_sd", "p95_p05", "edge"):
        if len(grp) < 3:  # too few to standardise against; leave at 0
            for r in grp:
                r["z_" + key] = 0.0
            continue
        mu, sd = z([r[key] for r in grp])
        for r in grp:
            r["z_" + key] = (r[key] - mu) / sd
for r in pool:
    # contrast is two definitions of one axis -> average them, so contrast and
    # detail carry equal weight rather than contrast counting twice.
    r["score"] = (r["z_lum_sd"] + r["z_p95_p05"]) / 2.0 + r["z_edge"]

pool.sort(key=lambda r: -r["score"])

# ---- diversity cap --------------------------------------------------------
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 28
CAP = 3  # max hero cells per subject: a hero set must not be one room five times
PAL_CAP = 5  # max per palette: keep the hero set from collapsing into one look
chosen, per_subj, per_pal = [], collections.Counter(), collections.Counter()

# SEED: keeps carrying a typed note. Every note on a keep is praise ("love
# this", "love this one", "nice and warm", "touch of green is nice", "Nice
# altar, good stylishness"), so a note is Pip saying it in words. His words
# outrank a pixel proxy, so these go in first regardless of score -- but they
# are NOT exempt from the text-leak exclusions, which is why this filters `pool`
# rather than the raw keeps.
noted = [r for r in pool if state.get(r["gid"], {}).get("note")]
print(f"\nseeding {len(noted)} noted (praised) keeps ahead of the score:")
for r in noted:
    print(f"    {'_'.join(r['cell']):<16} score {r['score']:>6.2f}  \"{state[r['gid']]['note']}\"")
    chosen.append(r)
    per_subj[r["subject"]] += 1
    per_pal[r["cell"][2]] += 1

for r in pool:
    if r in chosen:
        continue
    if len(chosen) >= TARGET:
        break
    if per_subj[r["subject"]] >= CAP or per_pal[r["cell"][2]] >= PAL_CAP:
        continue
    per_subj[r["subject"]] += 1
    per_pal[r["cell"][2]] += 1
    chosen.append(r)
if len(chosen) < TARGET:
    print(f"[!] caps left only {len(chosen)} of {TARGET}; relaxing to fill.")
    for r in pool:
        if len(chosen) >= TARGET:
            break
        if r not in chosen:
            chosen.append(r)
            per_subj[r["subject"]] += 1
            per_pal[r["cell"][2]] += 1

print(f"\nCHOSEN {len(chosen)} (cap {CAP}/subject, {PAL_CAP}/palette), subjects={len(per_subj)}")
print(f"{'rank':>4} {'cell':<16} {'score':>7} {'lum_sd':>7} {'edge':>7}  gid")
for i, r in enumerate(chosen, 1):
    print(
        f"{i:>4} {'_'.join(r['cell']):<16} {r['score']:>7.2f} "
        f"{r['lum_sd']:>7.3f} {r['edge']:>7.4f}  {r['gid']}"
    )
print("\nper-subject:", dict(per_subj.most_common()))
print("per-palette:", dict(per_pal.most_common()))
print("per-rendering:", dict(collections.Counter(r["cell"][1] for r in chosen).most_common()))

out = REPO / "tools/art_review/picks_l3_an0807_keep.json"
out.write_text(json.dumps([r["gid"] for r in chosen], indent=2) + "\n", encoding="utf-8")
print(f"\nwrote {out}")
