#!/usr/bin/env python3
"""Derive the pull-quote atoms from review_log.jsonl.

Why this exists
---------------
The first art-cull post was written as prose: one hand-authored blob per
platform, each quoting the same notes independently. That makes PROSE the
atom, and it has three failures the rest of this estate already knows about.

  * Nothing composes. A line that works cannot be reused anywhere without a
    copy-paste, and a copy becomes a variant the moment either side changes
    (coordination#15).
  * A judgement cannot percolate. If Pip decides one note is the best thing
    in the log, there is nowhere to record that once; he has to edit every
    platform blob that quotes it, and the ones he forgets silently disagree.
  * Nothing is checkable at the granularity that matters. A guard can assert
    "the counts are right" but not "this quote is still verbatim", because
    the quote only exists inside a paragraph.

So the NOTE is the atom. Each note Pip typed during a review becomes one
record carrying its verbatim text, the asset it judged, the verdict, a
resolved image path, and the per-platform clearance. Posts become
PROJECTIONS over a selection of those records -- the same relationship the
serveable zone has to curated data in pdoom-data.

The practical payoff: rate a quote once, and every post that draws on it
follows. Clear a quote for Bluesky but not LinkedIn, once, and no post can
get it wrong.

Verbatim is the default and the stored text is never edited. Pip ruled this
directly: the typos were typed at about 2.9 seconds an asset and are evidence
of the pace the post is about. `text_light` exists as an OPTIONAL sibling
field for venues where a typo would misread as carelessness, and is null
unless someone deliberately writes one. Nothing here silently tidies a human's
words.

Usage:
    extract_pullquotes.py            rewrite pullquotes.jsonl from the log
    extract_pullquotes.py --check    assert the committed file matches a
                                     fresh derivation; exit 1 if not
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
LOG = os.path.join(HERE, "review_log.jsonl")
OUT = os.path.join(HERE, "pullquotes.jsonl")
ART_ROOT = os.path.join(REPO, "art_generated")

# Notes the review tool wrote for itself. These are bookkeeping, not voice,
# and must never reach a post as though Pip had typed them.
TOOL_NOTE_PREFIXES = ("not chosen", "set winner", "set-winner", "server ")

# Categories are a reading aid for whoever assembles a post, not a taxonomy
# anyone should defend. Keyword-assigned, and deliberately coarse: the point
# is that a post can ask for "one from each" rather than "three in a row about
# colour", which is the failure that makes a quote list read as a list.
CATEGORY_RULES = [
    ("representation", ("male", "androgynous", "operator", "silhouette", "gender")),
    (
        "symbolism",
        ("symbol", "nuclear", "lock", "mtg", "ouroborous", "ouroboros", "abstract", "represent"),
    ),
    (
        "bewilderment",
        ("no idea", "not sure", "i think this is just", "distressing", "wildly incorrect"),
    ),
    ("praise", ("amazing", "strong positive", "interesting", "very funny")),
    (
        "craft",
        (
            "colour",
            "color",
            "contrast",
            "brighten",
            "grain",
            "dark",
            "lighting",
            "tone",
            "definition",
            "delineation",
        ),
    ),
]


def categorise(text):
    low = text.lower()
    for name, keywords in CATEGORY_RULES:
        if any(k in low for k in keywords):
            return name
    return "direction"


def parse_asset(asset_id):
    """gen:<set>:<name>:<version> -> (set, name, version). None if unparseable."""
    parts = asset_id.split(":")
    if len(parts) != 4 or parts[0] != "gen":
        return None
    return parts[1], parts[2], parts[3]


def resolve_image(asset_id):
    """Find the largest committed PNG for an asset, or None.

    Layout is art_generated/<set>/<version>/<name>_<version>_<size>.png.
    Returns a repo-relative path so nothing here depends on where the repo
    is checked out -- an absolute path in a committed artefact is a machine
    detail leaking into shared data.
    """
    parsed = parse_asset(asset_id)
    if not parsed:
        return None, None
    art_set, name, version = parsed

    candidates = []
    match_kind = None

    # Preferred layout: art_generated/<set>/<version>/<name>_<version>_<size>.png
    # The version is IN the filename, so this identifies the exact asset judged.
    directory = os.path.join(ART_ROOT, art_set, version)
    if os.path.isdir(directory):
        prefix = "%s_%s_" % (name, version)
        for filename in os.listdir(directory):
            if filename.startswith(prefix) and filename.endswith(".png"):
                candidates.append(os.path.join(directory, filename))
        if candidates:
            match_kind = "versioned"

    # Fallback: several sets predate that layout and live under art_source/
    # or godot/assets/ with no version in the filename. Search by exact stem
    # so a name cannot match a longer, different asset -- 'grant_proposal'
    # must not pull in 'grant_proposal_r3'.
    #
    # This fallback CANNOT distinguish versions. doom_meter_frame:v2 and :v3
    # are different assets that Pip judged differently, and both resolve to
    # the same file, so the image may not be the version he saw. That is
    # recorded as match_kind "name-only" rather than papered over, and
    # build_cull_sheet refuses to publish one without --allow-ambiguous.
    if not candidates:
        match_kind = "name-only"
        for root in (os.path.join(REPO, "art_source"), os.path.join(REPO, "godot", "assets")):
            if not os.path.isdir(root):
                continue
            for dirpath, _dirs, files in os.walk(root):
                if ".godot" in dirpath or "imported" in dirpath:
                    continue
                for filename in files:
                    if not filename.endswith(".png"):
                        continue
                    stem = re.sub(r"_(\d+)\.png$", "", filename)
                    if stem == name:
                        candidates.append(os.path.join(dirpath, filename))

    if not candidates:
        return None, None

    def size_of(path):
        match = re.search(r"_(\d+)\.png$", os.path.basename(path))
        return int(match.group(1)) if match else 0

    # Largest available, then shortest path, so the choice is deterministic
    # across machines -- os.walk order is not.
    best = sorted(candidates, key=lambda p: (-size_of(p), len(p), p))[0]
    return os.path.relpath(best, REPO).replace(os.sep, "/"), match_kind


def derive():
    if not os.path.isfile(LOG):
        sys.stderr.write("no review log at %s\n" % LOG)
        return None

    with open(LOG, encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]

    # The log is append-only, so an asset may appear several times. The last
    # row carrying a note is the one Pip left standing; earlier ones are the
    # mind-changes the log exists to preserve, and are counted, not quoted.
    latest = {}
    revisions = {}
    for row in rows:
        nxt = row.get("next") or {}
        note = (nxt.get("note") or "").strip()
        asset = row.get("asset")
        if nxt.get("verdict"):
            revisions.setdefault(asset, []).append(nxt["verdict"])
        if not note or note.lower().startswith(TOOL_NOTE_PREFIXES):
            continue
        latest[asset] = {
            "asset": asset,
            "text_verbatim": note,
            "verdict": nxt.get("verdict"),
            "ts": row.get("ts"),
        }

    quotes = []
    for index, asset in enumerate(sorted(latest), start=1):
        record = latest[asset]
        chain = revisions.get(asset, [])
        image_path, image_match = resolve_image(asset)
        quotes.append(
            {
                "id": "artq-%03d" % index,
                # Verbatim, always. Never rewritten by this script.
                "text_verbatim": record["text_verbatim"],
                # A deliberately-written cleaned variant, for venues where a typo
                # would misread as carelessness. Null unless a human writes one.
                "text_light": None,
                "asset": asset,
                "verdict": record["verdict"],
                "verdict_chain": chain if len(set(chain)) > 1 else None,
                "image": image_path,
                # "versioned": the filename carries the version, so this IS the
                # asset judged. "name-only": resolved by name across older sets
                # that carry no version, so it MAY be a different version.
                "image_match": image_match,
                "category": categorise(record["text_verbatim"]),
                # Pip's own tier. Null until he rates it. This is the field that
                # makes a judgement percolate: set it once, and every projection
                # that selects on rating follows without any post being edited.
                "rating": None,
                # Per-platform clearance. null means "not yet ruled on"; a list
                # means exactly those platforms. Set from Pip's rulings only.
                "cleared_for": None,
                "reviewed_at": record["ts"],
            }
        )
    return quotes


def write(quotes):
    with open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        for quote in quotes:
            handle.write(json.dumps(quote, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="assert the committed file matches a fresh derivation"
    )
    args = parser.parse_args()

    quotes = derive()
    if quotes is None:
        return 2

    fresh = "".join(json.dumps(q, ensure_ascii=False, sort_keys=True) + "\n" for q in quotes)

    if args.check:
        if not os.path.isfile(OUT):
            print("CHECK FAILED: %s does not exist" % os.path.basename(OUT))
            return 1
        with open(OUT, encoding="utf-8") as handle:
            committed = handle.read()
        # Human fields are intentionally editable; only the derived half must
        # match. Compare on the fields this script owns.
        owned = (
            "id",
            "text_verbatim",
            "asset",
            "verdict",
            "verdict_chain",
            "image",
            "image_match",
            "reviewed_at",
        )

        def project(blob):
            out = []
            for line in blob.splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                out.append({k: row.get(k) for k in owned})
            return out

        if project(committed) != project(fresh):
            print("CHECK FAILED: committed pullquotes disagree with the log " "on a derived field")
            return 1
        print("CHECK OK: %d pull-quotes, derived fields match review_log.jsonl" % len(quotes))
        return 0

    write(quotes)
    with_image = sum(1 for q in quotes if q["image"])
    ambiguous = sum(1 for q in quotes if q.get("image_match") == "name-only")
    changed = sum(1 for q in quotes if q["verdict_chain"])
    print("wrote %s" % os.path.relpath(OUT, REPO))
    print(
        "  %d pull-quotes, %d with a resolved image, %d whose verdict changed"
        % (len(quotes), with_image, changed)
    )
    if ambiguous:
        print(
            "  %d image(s) matched by NAME ONLY -- the version could not be "
            "distinguished, so the picture may not be the one judged. "
            "build_cull_sheet refuses these without --allow-ambiguous." % ambiguous
        )
    counts = {}
    for quote in quotes:
        counts[quote["category"]] = counts.get(quote["category"], 0) + 1
    print("  categories: %s" % ", ".join("%s %d" % kv for kv in sorted(counts.items())))
    print(
        "  rating and cleared_for are null on every row -- they are Pip's "
        "to set, and nothing may infer them."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
