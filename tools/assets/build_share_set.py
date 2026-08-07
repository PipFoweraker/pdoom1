#!/usr/bin/env python3
"""Derive the ART SHARE SET from verdicts already applied -- no new review pass.

WHAT A SHARE SET IS
-------------------
A tracked declaration of which Library art assets pdoom1 is willing to HAND OVER
for public use, with the provenance needed to substantiate what they are.

It is NOT a publication decision. ``coordination#31`` ruled that
``pdoom1-website`` owns the ``publishable`` gate; this seat does not want that
gate and should not be given it. What this file does is close the gap on the
other side: before it existed, an asset that no GAME SLOT demanded had no route
to any public surface at all, because ADR-0019 only routes art that a demand
entry pulls into ``godot/assets/``. Assets Pip likes but the game does not need
were simply stranded.

So: pdoom1 publishes a candidate set with evidence. The website decides what,
if anything, goes up. One-way, per ``docs/copy/README.md``.

WHY ``keep`` IS NOT THE SAME AS "CLEARED"
-----------------------------------------
``tools/art_review/serve_review.py`` defines the verdicts as taste, nothing
else: ``keep`` = "accept it", ``iterate`` = "on-brief but not final; regenerate
to compare/hone -- the DEFAULT 'slight reject'", ``discard`` = "OFF-brief". ADR-0019
says the same from the other end: "Verdicts still gate Library admission
(taste)... none of them implies packing."

This tool therefore treats ``keep`` as a NECESSARY condition and adds the ones a
taste verdict cannot express:

- **``iterate`` is excluded.** Not because a rule says so but because Pip's own
  ``iterate`` notes on this run are reservations in plain words -- "slightly too
  washed out, composition feels odd", "this composition feels weird", "slightyl
  too crisp". Every note he left on an ``iterate`` is a complaint and every note
  he left on a ``keep`` is praise. Publishing an ``iterate`` would publish an
  image he has already said is wrong.
- **Text leakage is excluded.** Measured, see ``TIER_QUARANTINE_TEXT`` below.
- **Assets without per-file provenance are excluded** -- structurally: the
  builder cannot emit an entry without a ledger record and a sidecar, so an
  unattributable asset cannot silently enter. That is the mechanism, not a
  policy anyone has to remember.

TIERS
-----
The website is not a game looking for functional assets; it wants images that
exist to be looked at. A ``keep`` on a 1024x1024 colour swatch sheet and a
``keep`` on a 1536x1024 lit interior are the same verdict and wildly different
publication candidates, so the manifest ranks them:

``hero``               keep + scene + Pip left an approving note. The strongest
                       signal in the store -- he typed words rather than clicking.
``feature``            keep + scene, text-clean, no note either way.
``reference``          keep + swatch sheet. INTERNAL palette evidence. Interesting
                       to us, meaningless to a reader. Labelled rather than
                       omitted so the website seat is not left guessing what a
                       grid of colour rectangles is doing in a hero list.
``quarantine_text``    keep, but OCR found lettering. Listed WITH the detected
                       strings so the exclusion is auditable instead of invisible.

SURFACES
--------
Recorded per entry as ``surfaces``, derived from pixel size, not asserted:
1536x1024 and 1024x1024 masters are comfortable for web and social at any normal
display size. **Neither supports print at poster size.** 1536px long edge is
about 5.1 inches at 300dpi and this pipeline has no upscale path, so anything
claiming print needs a regenerated source, not a resample.

USAGE
-----
    python tools/assets/build_share_set.py
    python tools/assets/build_share_set.py --check      # CI-style staleness gate
    python tools/assets/build_share_set.py --html       # local contact sheet
    python tools/assets/build_share_set.py --stage DIR  # copy masters + sidecars

Writes ``docs/copy/art_share_set.json`` (the manifest the website pulls) and
``docs/copy/art_share_set_prompts.json`` (sha256 -> full prompt text, kept
separate so the manifest stays diffable). Never writes into ``godot/``, never
moves or deletes an art file.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN_ID = "art_night_2026-08-07"
BATCH_PREFIX = "an0807"
SCHEMA_VERSION = "1.0"

MANIFEST_REL = "docs/copy/art_share_set.json"
PROMPTS_REL = "docs/copy/art_share_set_prompts.json"
TEXT_SCAN_REL = "tools/art_review/text_scan_%s.json" % RUN_ID
HTML_REL = "art_generated/share_set.html"

TIER_HERO = "hero"
TIER_FEATURE = "feature"
TIER_REFERENCE = "reference"
TIER_QUARANTINE_TEXT = "quarantine_text"

PUBLICATION_TIERS = (TIER_HERO, TIER_FEATURE)

# Blocks whose output is a design-reference artefact rather than a picture of
# anything. Kept in the manifest, never a publication candidate.
REFERENCE_BLOCKS = {"%s_l0_sheets" % BATCH_PREFIX}

# OCR confidence at or above which a detection is treated as probable lettering.
# Kept in sync with tools/art_review/scan_text_leak.py:CONF_STRONG.
CONF_STRONG = 0.60


def surfaces_for(size):
    """What a master of this pixel size actually supports. Derived, not claimed."""
    try:
        wide, high = (int(x) for x in size.lower().split("x"))
    except (ValueError, AttributeError):
        return {
            "web": False,
            "social": False,
            "print_poster": False,
            "note": "unparsed size %r" % size,
        }
    long_edge = max(wide, high)
    return {
        "web": long_edge >= 1024,
        "social": long_edge >= 1024,
        "print_poster": False,
        "note": (
            "long edge %dpx = about %.1f inches at 300dpi. No upscale path exists "
            "in this pipeline, so print at poster size needs a REGENERATED source, "
            "not a resample of this file." % (long_edge, long_edge / 300.0)
        ),
    }


def load_ledger(repo_root):
    path = os.path.join(repo_root, "art_generated", RUN_ID, "ledger.jsonl")
    if not os.path.exists(path):
        return None
    ledger = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rec = json.loads(line)
                ledger[rec["job_id"]] = rec
    return ledger


def job_id_for(asset_id):
    """gen:an0807_l1_family:s10_f10:v1  ->  L1|l1_family|s10_f10|v1"""
    _, block, cell, variant = asset_id.split(":")
    level = "L0" if "_l0_" in block else "L1"
    short = block.split("_", 1)[1]
    return "%s|%s|%s|%s" % (level, short, cell, variant), block


def build(repo_root, require_text_scan=True):
    """Return (manifest_dict, prompts_dict). Raises on missing inputs."""
    with open(
        os.path.join(repo_root, "tools/art_review/review_state.json"), encoding="utf-8"
    ) as fh:
        state = json.load(fh)

    ledger = load_ledger(repo_root)
    if ledger is None:
        raise SystemExit(
            "ERROR: %s/ledger.jsonl not found.\n"
            "art_generated/ is gitignored -- run this on the machine that holds the run." % RUN_ID
        )

    text_scan = {}
    scan_path = os.path.join(repo_root, TEXT_SCAN_REL)
    scan_meta = None
    if os.path.exists(scan_path):
        with open(scan_path, encoding="utf-8") as fh:
            blob = json.load(fh)
        text_scan = blob.get("assets", {})
        scan_meta = {k: v for k, v in blob.items() if k != "assets"}
    elif require_text_scan:
        # Found the hard way on 2026-08-07: without this the builder silently
        # emitted a manifest with NO text gate and 9 extra "candidates", and
        # said nothing. A share set that is quietly ungated is worse than no
        # share set, because it looks identical to a gated one.
        raise SystemExit(
            "ERROR: %s not found, so the text-leak gate cannot run.\n"
            "  Generate it:  python tools/art_review/scan_text_leak.py\n"
            "  Or accept an UNGATED manifest explicitly:  --no-text-scan" % TEXT_SCAN_REL
        )

    reviewed = {k: v for k, v in state.items() if k.startswith("gen:%s" % BATCH_PREFIX)}
    keeps = {k: v for k, v in reviewed.items() if v.get("verdict") == "keep"}

    entries = []
    prompts = {}
    skipped_no_provenance = []

    for asset_id in sorted(keeps):
        val = keeps[asset_id]
        job_id, block = job_id_for(asset_id)
        rec = ledger.get(job_id)
        if rec is None:
            skipped_no_provenance.append({"asset_id": asset_id, "reason": "no ledger record"})
            continue
        rel_master = rec["master_path"].replace("\\", "/")
        abs_master = os.path.join(repo_root, rel_master)
        sidecar = os.path.splitext(abs_master)[0] + ".meta.json"
        if not os.path.exists(sidecar):
            skipped_no_provenance.append({"asset_id": asset_id, "reason": "no .meta.json sidecar"})
            continue
        with open(sidecar, encoding="utf-8") as fh:
            meta = json.load(fh)

        scan = text_scan.get(asset_id)
        hits = (scan or {}).get("hits", [])
        strong = [h for h in hits if h["conf"] >= CONF_STRONG]

        note = (val.get("note") or "").strip()
        is_reference = block in REFERENCE_BLOCKS

        # ANY detection quarantines, not just a confident one. The costs are
        # asymmetric: a false quarantine loses one image out of ~130, while a
        # false pass puts a garbled half-word on a picture chosen precisely
        # because it is prominent. The confidence travels with the entry so the
        # website seat can overrule a borderline call with the evidence in hand.
        if hits:
            tier = TIER_QUARANTINE_TEXT
        elif is_reference:
            tier = TIER_REFERENCE
        elif note:
            # Every note Pip left on a keep in this run is praise; every note he
            # left on an iterate is a reservation. The note text ships with the
            # entry so a reader can check that claim rather than take it.
            tier = TIER_HERO
        else:
            tier = TIER_FEATURE

        prompts[meta["prompt_sha256"]] = meta["prompt"]

        entries.append(
            {
                "asset_id": asset_id,
                "tier": tier,
                "publishable_candidate": tier in PUBLICATION_TIERS,
                "master_path": rel_master,
                "master_bytes": meta.get("master_bytes"),
                "size": rec["size"],
                "surfaces": surfaces_for(rec["size"]),
                "verdict": "keep",
                "verdict_note": note,
                "verdict_updated_at": val.get("updated_at"),
                "text_scan": {
                    "scanned": scan is not None,
                    "detections": hits,
                    "strong_detections": len(strong),
                },
                "provenance": {
                    # Vocabulary from docs/design/ASSET_PROVENANCE_SCOPE_2026-08-06.md.
                    # The sidecar's own value is the coarser "generated".
                    "origin": "generated_model",
                    "origin_detail": "%s via %s, run %s, job %s"
                    % (meta.get("model"), meta.get("backend"), meta.get("run_id"), job_id),
                    "evidence": "run ledger line + per-file .meta.json sidecar, both written at generation time",
                    "confidence": "high",
                    "model": meta.get("model"),
                    "backend": meta.get("backend"),
                    "run_id": meta.get("run_id"),
                    "job_id": job_id,
                    "prompt_sha256": meta.get("prompt_sha256"),
                    "generated_at_utc": meta.get("generated_at_utc") or rec.get("recorded_at_utc"),
                    "quality": meta.get("quality"),
                    "cost_usd_tariff": meta.get("cost_usd_tariff", rec.get("cost_usd")),
                    "cost_is_billed_truth": meta.get("cost_is_billed_truth", False),
                    "seed": None,
                    "seed_note": meta.get("seed_note")
                    or (
                        "The OpenAI Images API exposes no seed parameter. This record "
                        "establishes what was ASKED FOR; it does not make the exact "
                        "output reproducible."
                    ),
                    "revised_prompt": meta.get("revised_prompt"),
                },
            }
        )

    counts = {}
    for e in entries:
        counts[e["tier"]] = counts.get(e["tier"], 0) + 1

    verdict_counts = {}
    for v in reviewed.values():
        verdict_counts[v.get("verdict")] = verdict_counts.get(v.get("verdict"), 0) + 1

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "kind": "art_share_set",
        "source_repo": "pdoom1",
        "consumer": "pdoom1-website (owns the `publishable` gate, coordination#31 A2 bit 3)",
        "run_id": RUN_ID,
        "what_this_is": (
            "Library art pdoom1 offers for public use, derived from verdicts Pip "
            "already applied. Entry here is a HANDOVER, not a publication decision. "
            "pdoom1 does not hold the `publishable` gate and is not asking for it."
        ),
        "how_to_consume": (
            "Filter on publishable_candidate == true, then sort by tier (hero "
            "before feature). Read entry.surfaces before choosing a placement. "
            "Any public provenance claim must be backed by entry.provenance plus "
            "the prompt text in art_share_set_prompts.json, keyed by prompt_sha256."
        ),
        "bytes_are_not_here": (
            "This manifest carries PATHS, not pixels. The masters total ~408MB and "
            "docs/art/ART_MASTERS_POLICY.md forbids art over 1MB in git; the masters "
            "archive bucket is deliberately non-public and auth-only, so it is not a "
            "web path either. Getting bytes to the website is a separate, deliberate "
            "handover -- see docs/copy/ART_SHARE_SET.md."
        ),
        "limits": [
            "Coverage is one run only. Older Library assets are NOT here: "
            "docs/design/ASSET_PROVENANCE_SCOPE_2026-08-06.md records 31.6% of packed "
            "assets whose only origin evidence is a gitignored single-copy directory, "
            "and 6 that are unattributable outright. Evidence that weak cannot back a "
            "public claim, so the builder cannot emit those entries at all.",
            "Text-leak measurement is a LOWER BOUND -- OCR misses small, stylised or "
            "low-contrast lettering.",
            "No entry supports print at poster size. See entry.surfaces.",
            "Cost figures are tariff arithmetic, not billed truth "
            "(cost_is_billed_truth is false throughout).",
        ],
        "tier_meanings": {
            TIER_HERO: "keep + Pip left an approving note. Strongest signal available.",
            TIER_FEATURE: "keep, text-clean scene, no note either way.",
            TIER_REFERENCE: "keep, but a design-reference swatch sheet. NOT a publication candidate.",
            TIER_QUARANTINE_TEXT: "keep, but OCR found lettering at ANY confidence. "
            "Excluded; every detection is listed with its confidence "
            "so a borderline call can be overruled on the evidence.",
        },
        "counts": {
            "reviewed_in_run": len(reviewed),
            "by_verdict": verdict_counts,
            "in_share_set": len(entries),
            "by_tier": counts,
            "publishable_candidates": sum(1 for e in entries if e["publishable_candidate"]),
            "skipped_no_provenance": len(skipped_no_provenance),
        },
        "excluded": {
            "iterate": "Pip's own iterate notes on this run are reservations in plain words. "
            "iterate is defined as 'on-brief but not final'; publishing one would "
            "publish an image he has already said is wrong.",
            "discard": "off-brief by his verdict.",
            "unjudged": (
                "%d of 652 images in the run carry no verdict, including the entire "
                "l1_grid (220) and l0_anchors (54) blocks. Unjudged is not a quiet yes."
                % (652 - len(reviewed))
            ),
        },
        "text_scan_source": scan_meta,
        "text_gate": "applied" if scan_meta else "NOT APPLIED -- built with --no-text-scan",
        "skipped_no_provenance": skipped_no_provenance,
        "assets": entries,
    }
    return manifest, prompts


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="ascii", newline="\n") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, ensure_ascii=True)
        fh.write("\n")


def render_html(manifest, repo_root):
    """A local contact sheet. Derived output -- art_generated/ is gitignored."""
    order = {TIER_HERO: 0, TIER_FEATURE: 1, TIER_REFERENCE: 2, TIER_QUARANTINE_TEXT: 3}
    assets = sorted(manifest["assets"], key=lambda e: (order.get(e["tier"], 9), e["asset_id"]))
    parts = [
        "<!doctype html><meta charset='utf-8'>",
        "<title>P(Doom)1 art share set -- %s</title>" % manifest["run_id"],
        "<style>",
        "body{background:#0e0614;color:#e8e2ea;font:14px/1.5 ui-monospace,Consolas,monospace;margin:0;padding:24px}",
        "h1{color:#e8a33d;font-size:20px} h2{color:#e8a33d;border-top:1px solid #3a2c44;padding-top:14px;margin-top:34px}",
        ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}",
        ".card{background:#170a1c;border:1px solid #3a2c44;padding:8px;border-radius:4px}",
        ".card img{width:100%;display:block;border-radius:2px;background:#000}",
        ".id{color:#9a8fa6;font-size:11px;word-break:break-all;margin-top:6px}",
        ".note{color:#7fd67f;font-size:12px;margin-top:4px}",
        ".warn{color:#ff8a6a;font-size:12px;margin-top:4px}",
        "p{max-width:80ch;color:#b8aec2}",
        "</style>",
        "<h1>P(Doom)1 art share set</h1>",
        "<p>%s</p>" % manifest["what_this_is"],
        "<p><b>%d</b> entries, <b>%d</b> publication candidates. Tiers: %s</p>"
        % (
            manifest["counts"]["in_share_set"],
            manifest["counts"]["publishable_candidates"],
            ", ".join("%s=%d" % (k, v) for k, v in sorted(manifest["counts"]["by_tier"].items())),
        ),
        "<p>No entry supports print at poster size -- 1536px long edge is about "
        "5.1 inches at 300dpi and there is no upscale path.</p>",
    ]
    current = None
    for e in assets:
        if e["tier"] != current:
            if current is not None:
                parts.append("</div>")
            current = e["tier"]
            parts.append("<h2>%s -- %s</h2>" % (current, manifest["tier_meanings"][current]))
            parts.append("<div class='grid'>")
        # Prefer the 1024 derivative for page weight; fall back to the master.
        src = e["master_path"]
        alt = src.replace("_1536.png", "_1024.png")
        if os.path.exists(os.path.join(repo_root, alt)):
            src = alt
        rel = os.path.relpath(
            os.path.join(repo_root, src), os.path.dirname(os.path.join(repo_root, HTML_REL))
        )
        parts.append("<div class='card'><img loading='lazy' src='%s'>" % rel.replace("\\", "/"))
        parts.append(
            "<div class='id'>%s<br>%s %s</div>"
            % (e["asset_id"], e["size"], e["provenance"]["model"])
        )
        if e["verdict_note"]:
            parts.append("<div class='note'>Pip: %s</div>" % e["verdict_note"])
        if e["text_scan"]["strong_detections"]:
            found = ", ".join(
                repr(h["text"]) for h in e["text_scan"]["detections"] if h["conf"] >= CONF_STRONG
            )
            parts.append("<div class='warn'>[!] text detected: %s</div>" % found)
        parts.append("</div>")
    if current is not None:
        parts.append("</div>")
    return "\n".join(parts) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo-root", default=REPO_ROOT)
    ap.add_argument(
        "--check",
        action="store_true",
        help="fail if the tracked manifest differs from a fresh build",
    )
    ap.add_argument("--html", action="store_true", help="also write the local contact sheet")
    ap.add_argument(
        "--stage",
        metavar="DIR",
        help="copy publication-candidate masters + sidecars into DIR "
        "(off-git staging, per docs/art/ART_MASTERS_POLICY.md)",
    )
    ap.add_argument(
        "--no-text-scan",
        action="store_true",
        help="build WITHOUT the text-leak gate. The manifest records "
        "that it is ungated. Do not publish from such a manifest.",
    )
    args = ap.parse_args(argv)

    root = args.repo_root
    manifest, prompts = build(root, require_text_scan=not args.no_text_scan)
    manifest_path = os.path.join(root, MANIFEST_REL)
    prompts_path = os.path.join(root, PROMPTS_REL)

    if args.check:
        stale = []
        for path, obj in ((manifest_path, manifest), (prompts_path, prompts)):
            if not os.path.exists(path):
                stale.append("%s is missing" % path)
                continue
            with open(path, encoding="ascii") as fh:
                if json.load(fh) != obj:
                    stale.append("%s is stale" % path)
        if stale:
            for s in stale:
                print("FAIL:", s, file=sys.stderr)
            print("Regenerate: python tools/assets/build_share_set.py", file=sys.stderr)
            return 1
        print("OK: share set is current (%d entries)" % manifest["counts"]["in_share_set"])
        return 0

    write_json(manifest_path, manifest)
    write_json(prompts_path, prompts)
    print(
        "wrote %s  (%d entries, %d publication candidates)"
        % (
            MANIFEST_REL,
            manifest["counts"]["in_share_set"],
            manifest["counts"]["publishable_candidates"],
        )
    )
    print("wrote %s  (%d unique prompts)" % (PROMPTS_REL, len(prompts)))
    for tier, n in sorted(manifest["counts"]["by_tier"].items()):
        print("   %-18s %d" % (tier, n))

    if args.html:
        html_path = os.path.join(root, HTML_REL)
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        with open(html_path, "w", encoding="ascii", errors="backslashreplace", newline="\n") as fh:
            fh.write(render_html(manifest, root))
        print("wrote %s" % os.path.abspath(html_path))

    if args.stage:
        os.makedirs(args.stage, exist_ok=True)
        # Cell ids are NOT unique across blocks -- l1_palette and l1_probe both
        # use sNN_rNN_pNN, and s01_r01_p01 exists in both from DIFFERENT models
        # (gpt-image-1.5 vs gpt-image-2). Staging on basename alone silently
        # overwrote one with the other. The block goes in the name, and the
        # result is asserted unique rather than assumed.
        planned = {}
        for e in manifest["assets"]:
            if not e["publishable_candidate"]:
                continue
            block = e["asset_id"].split(":")[1]
            stem = "%s__%s__%s" % (e["tier"], block, os.path.basename(e["master_path"]))
            if stem in planned:
                raise SystemExit(
                    "ERROR: staged filename collision on %r (%s vs %s)"
                    % (stem, planned[stem], e["asset_id"])
                )
            planned[stem] = e["asset_id"]

        n = 0
        for e in manifest["assets"]:
            if not e["publishable_candidate"]:
                continue
            src = os.path.join(root, e["master_path"])
            side = os.path.splitext(src)[0] + ".meta.json"
            block = e["asset_id"].split(":")[1]
            stem = "%s__%s__%s" % (e["tier"], block, os.path.basename(src))
            shutil.copy2(src, os.path.join(args.stage, stem))
            if os.path.exists(side):
                shutil.copy2(
                    side, os.path.join(args.stage, os.path.splitext(stem)[0] + ".meta.json")
                )
            n += 1
        shutil.copy2(manifest_path, os.path.join(args.stage, "art_share_set.json"))
        shutil.copy2(prompts_path, os.path.join(args.stage, "art_share_set_prompts.json"))
        print("staged %d masters + sidecars into %s" % (n, os.path.abspath(args.stage)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
