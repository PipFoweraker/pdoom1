#!/usr/bin/env python3
"""Analyze a pixellab contact-sheet triage export (verdicts JSON).

Reads the verdict tags a reviewer saved from the contact sheet
(art_source/pixellab_contact_sheet.html -> "export JSON") and cross-references
them against the full sprite inventory on disk. Produces:

  1. A verdict summary (totals + PROMOTE/FAVOUR broken down by category and by
     the finer subtype), so an imbalance like "props/coat_rack 40, props/bin 2"
     is obvious.
  2. Imbalance + coverage gaps: over-represented promoted subtypes per category,
     under-/zero-promote subtypes that DO exist in the inventory, stale verdict
     paths (tagged but no longer on disk), and never-triaged sprites per category.
  3. Three actionable path lists under art_source/ (promote / favour /
     disfavour+dislike) grouped by "# category/subtype".

Classification logic is copied from the contact-sheet generator
(G:/tmp/gen_contact_sheet.py) so categories match the sheet exactly. If that
file is gone the equivalent folder-based rules are re-implemented here (see
categorize / categorize_by_name below) -- this script is self-contained and does
not import it.

stdlib only, Python 3.11, ASCII only. Local review tool -- not committed.

Usage:
  python tools/art_review/analyze_verdicts.py            # real run
  python tools/art_review/analyze_verdicts.py --selftest # synthetic self-check
"""
import collections
import json
import os
import sys

# --- paths -----------------------------------------------------------------
# Repo-relative: this script lives at <repo>/tools/art_review/, so art_source/
# is two levels up. Override with a single CLI arg pointing at an art_source dir.
_HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_ART_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "art_source"))
ART_DIR = (
    os.path.abspath(sys.argv[1])
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-")
    else _DEFAULT_ART_DIR
)
VERDICTS_PATH = os.path.join(ART_DIR, "pixellab_verdicts.json")
PROMOTE_OUT = os.path.join(ART_DIR, "promote_list.txt")
FAVOUR_OUT = os.path.join(ART_DIR, "favour_list.txt")
PRUNE_OUT = os.path.join(ART_DIR, "disfavour_dislike_list.txt")

EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp")
VERDICTS = ["like", "dislike", "favour", "disfavour", "promote"]
CATS = ["characters", "cats", "props", "tilesets", "cosmetics", "other"]
TOP_N = 8  # how many over-represented subtypes to list per category

# tokens stripped from the tail of a filename stem to reach the "item" identity
_DIRS = {
    "east",
    "west",
    "north",
    "south",
    "up",
    "down",
    "north-east",
    "north-west",
    "south-east",
    "south-west",
    "ne",
    "nw",
    "se",
    "sw",
}
_UNWRAP = {"reroll", "sweep"}  # container run-subfolders to skip
_STRIP_LEAF = {"rotations"}  # trailing folder segs that aren't identity


# --- classification (copied from gen_contact_sheet.py) ---------------------
def categorize(rel_parts):
    """Category from the folder segments (all segments below the run root)."""
    segs = [s.lower() for s in rel_parts]

    def has(*names):
        return any(any(n in s for n in names) for s in segs)

    if has("tileset"):
        return "tilesets"
    if has("cat"):
        return "cats"
    if has("cosmetic", "overlay"):
        return "cosmetics"
    if has(
        "window",
        "prop",
        "object",
        "kitchen",
        "chair",
        "library",
        "environment",
        "ui_filler",
        "ui-filler",
        "icon",
    ):
        return "props"
    if has(
        "character",
        "founder",
        "era_ladder",
        "era-ladder",
        "style_matrix",
        "style-matrix",
        "researcher",
        "worker",
        "genius",
    ):
        return "characters"
    return None


def categorize_by_name(fname):
    """Fallback category for loose root sprites, from the filename."""
    n = fname.lower()
    if "cat" in n:
        return "cats"
    if "tileset" in n or "floor_" in n or "wall_" in n:
        return "tilesets"
    if "hat" in n or "silhouette" in n:
        return "cosmetics"
    return "characters"


# --- subtype derivation ----------------------------------------------------
def file_item(fname):
    """Object identity from a filename: strip extension, then strip trailing
    direction tokens (east/north-west/...) and pure-number variant tokens
    (_1, _2). 'chair_decent_1_east.png' -> 'chair_decent';
    'east.png' -> '' (rotation frame, identity lives in the folder)."""
    stem = os.path.splitext(fname)[0].lower()
    toks = stem.split("_")
    while toks and (toks[-1] in _DIRS or toks[-1].isdigit()):
        toks.pop()
    return "_".join(toks)


def unwrap_segs(dir_segs):
    """Drop reroll/sweep container prefixes and a trailing 'rotations' seg."""
    segs = [s for s in dir_segs if s.lower() not in _UNWRAP]
    while segs and segs[-1].lower() in _STRIP_LEAF:
        segs.pop()
    return segs


def subtype_of(cat, dir_segs, fname):
    """Finer subtype label 'category/<item>'. Prefer the filename-derived item
    (so props/objects splits into desk_decent, coat_rack, bin, ...); fall back
    to the immediate folder leaf when the filename is direction-only (character
    and cat rotation frames, whose identity is the folder name)."""
    item = file_item(fname)
    if not item:
        segs = unwrap_segs(dir_segs)
        item = segs[-1].lower() if segs else "misc"
    return "{}/{}".format(cat, item)


def classify_record(dir_segs, fname):
    """Return (category, subtype) for one sprite. dir_segs are the folder
    segments below the run root ([] for a loose root sprite)."""
    cat = categorize(dir_segs) if dir_segs else None
    if cat is None:
        cat = categorize_by_name(fname)
    if cat not in CATS:
        cat = "other"
    return cat, subtype_of(cat, dir_segs, fname)


# --- inventory scan --------------------------------------------------------
def build_inventory(art_dir):
    """Scan art_source/pixellab_* for images. Returns list of record dicts:
    {rel, run, cat, subtype, fn}. rel is POSIX-style, relative to art_dir
    (matching the verdict-JSON key form)."""
    records = []
    if not os.path.isdir(art_dir):
        return records
    runs = sorted(
        d
        for d in os.listdir(art_dir)
        if d.startswith("pixellab_") and os.path.isdir(os.path.join(art_dir, d))
    )
    for run in runs:
        run_root = os.path.join(art_dir, run)
        for dirpath, dirnames, filenames in os.walk(run_root):
            dirnames.sort()
            for fn in sorted(filenames):
                if not fn.lower().endswith(EXTS):
                    continue
                abs_path = os.path.join(dirpath, fn)
                rel = os.path.relpath(abs_path, art_dir).replace("\\", "/")
                sub = os.path.relpath(dirpath, run_root).replace("\\", "/")
                dir_segs = [] if sub == "." else sub.split("/")
                cat, subtype = classify_record(dir_segs, fn)
                records.append(
                    {
                        "rel": rel,
                        "run": run,
                        "cat": cat,
                        "subtype": subtype,
                        "fn": fn,
                    }
                )
    return records


def load_verdicts(path):
    """Return {rel: [tags]} with POSIX keys and known tags only, or None if the
    file is missing. Raises ValueError on a malformed (non-object) file."""
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        raise ValueError("verdicts JSON must be an object {path: [tags]}")
    out = {}
    for k, v in obj.items():
        key = str(k).replace("\\", "/")
        if isinstance(v, str):
            v = [v]
        tags = [t for t in (v or []) if t in VERDICTS]
        if tags:
            out[key] = tags
    return out


# --- aggregation (pure; unit-tested by --selftest) -------------------------
def summarize(verdicts, records):
    """Cross-reference verdicts against the inventory.

    verdicts: {rel: [tags]}          records: list of inventory record dicts
    Returns a dict of aggregates (see keys assembled at the end)."""
    inv_by_rel = {r["rel"]: r for r in records}

    verdict_counts = collections.Counter()
    # per-verdict breakdowns, only for on-disk sprites
    by_cat = {v: collections.Counter() for v in VERDICTS}
    by_sub = {v: collections.Counter() for v in VERDICTS}
    # actionable path lists keyed (cat, subtype) -> [rel...]
    lists = {v: collections.defaultdict(list) for v in VERDICTS}
    stale = collections.Counter()  # rel -> tags present but not on disk
    stale_paths = {}

    tagged_rels = set()
    for rel, tags in verdicts.items():
        tagged_rels.add(rel)
        rec = inv_by_rel.get(rel)
        for t in tags:
            verdict_counts[t] += 1
        if rec is None:
            stale_paths[rel] = tags
            for t in tags:
                stale[t] += 1
            continue
        for t in tags:
            by_cat[t][rec["cat"]] += 1
            by_sub[t][rec["subtype"]] += 1
            lists[t][(rec["cat"], rec["subtype"])].append(rel)

    # inventory-side coverage: every subtype that exists, per category, plus its
    # promote count (0 if never promoted).
    inv_subtypes = collections.defaultdict(set)  # cat -> {subtype}
    inv_sub_count = collections.Counter()  # subtype -> inventory size
    for r in records:
        inv_subtypes[r["cat"]].add(r["subtype"])
        inv_sub_count[r["subtype"]] += 1

    promote_by_sub = by_sub["promote"]
    # per category: over-represented (top N promoted) and under/zero-promote
    over = {}  # cat -> [(subtype, promote_count)] desc
    under = {}  # cat -> [(subtype, promote_count, inv_count)] promote<=1
    for cat in sorted(inv_subtypes):
        subs = inv_subtypes[cat]
        ranked = sorted(
            ((s, promote_by_sub.get(s, 0)) for s in subs),
            key=lambda x: (-x[1], x[0]),
        )
        over[cat] = [t for t in ranked if t[1] > 0][:TOP_N]
        under[cat] = sorted(
            (
                (s, promote_by_sub.get(s, 0), inv_sub_count[s])
                for s in subs
                if promote_by_sub.get(s, 0) <= 1
            ),
            key=lambda x: (x[1], -x[2], x[0]),
        )

    # never-triaged sprites (on disk, no verdict at all), by category
    untouched_by_cat = collections.Counter()
    untouched_total = 0
    for r in records:
        if r["rel"] not in tagged_rels:
            untouched_by_cat[r["cat"]] += 1
            untouched_total += 1

    return {
        "total_tagged": len(tagged_rels),
        "verdict_counts": verdict_counts,
        "by_cat": by_cat,
        "by_sub": by_sub,
        "lists": lists,
        "stale": stale,
        "stale_paths": stale_paths,
        "over": over,
        "under": under,
        "untouched_by_cat": untouched_by_cat,
        "untouched_total": untouched_total,
        "inv_total": len(records),
    }


# --- reporting -------------------------------------------------------------
def _fmt_counter(counter, indent="    "):
    lines = []
    for name, n in sorted(counter.items(), key=lambda x: (-x[1], x[0])):
        lines.append("{}{:5d}  {}".format(indent, n, name))
    return lines or ["{}(none)".format(indent)]


def render_report(agg, inv_total):
    L = []
    p = L.append
    p("=" * 70)
    p("PIXELLAB VERDICT ANALYSIS")
    p("=" * 70)
    p("inventory on disk : {} sprites".format(inv_total))
    p("tagged (triaged)  : {}".format(agg["total_tagged"]))
    p("never triaged     : {}".format(agg["untouched_total"]))
    p("")
    p("-- 1. VERDICT SUMMARY " + "-" * 48)
    p("verdict tag counts:")
    vc = agg["verdict_counts"]
    for v in VERDICTS:
        p("    {:5d}  {}".format(vc.get(v, 0), v))
    stale = agg["stale"]
    if sum(stale.values()):
        p("  (of which STALE -- tag on a path not on disk:)")
        for v in VERDICTS:
            if stale.get(v):
                p("    {:5d}  {} (stale)".format(stale[v], v))

    for v in ("promote", "favour"):
        p("")
        p("  {} by CATEGORY:".format(v.upper()))
        L.extend(_fmt_counter(agg["by_cat"][v], "      "))
        p("  {} by SUBTYPE (desc):".format(v.upper()))
        L.extend(_fmt_counter(agg["by_sub"][v], "      "))

    p("")
    p("-- 2. IMBALANCE + COVERAGE GAPS " + "-" * 38)
    for cat in sorted(agg["over"]):
        over = agg["over"][cat]
        under = agg["under"][cat]
        if not over and not under:
            continue
        p("  [{}]".format(cat))
        p("    over-represented promoted subtypes (top {}):".format(TOP_N))
        if over:
            for s, n in over:
                p("      {:5d}  {}".format(n, s))
        else:
            p("      (nothing promoted in this category)")
        p("    under-/zero-promote subtypes present in inventory:")
        zero = [(s, n, inv) for (s, n, inv) in under if n == 0]
        one = [(s, n, inv) for (s, n, inv) in under if n == 1]
        if zero:
            p("      ZERO promotes ({} asset types):".format(len(zero)))
            for s, n, inv in zero:
                p("        {}  (inventory x{})".format(s, inv))
        if one:
            p("      only 1 promote:")
            for s, n, inv in one:
                p("        {}  (inventory x{})".format(s, inv))
        if not zero and not one:
            p("      (every subtype here has >=2 promotes)")

    stale_paths = agg["stale_paths"]
    p("")
    p("  STALE verdict paths (tagged but not on disk): {}".format(len(stale_paths)))
    for rel in sorted(stale_paths)[:40]:
        p("      {}  {}".format(",".join(stale_paths[rel]), rel))
    if len(stale_paths) > 40:
        p("      ... and {} more".format(len(stale_paths) - 40))

    p("")
    p("  NEVER-TRIAGED sprites by category:")
    L.extend(_fmt_counter(agg["untouched_by_cat"], "      "))
    return "\n".join(L)


def write_list_file(path, list_map, header):
    """list_map: {(cat, subtype): [rel...]}. Writes paths grouped under a
    '# category/subtype' header per group (subtype already contains category)."""
    groups = sorted(list_map.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    total = 0
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# {}\n".format(header))
        f.write("# generated by tools/art_review/analyze_verdicts.py\n\n")
        for (cat, subtype), rels in groups:
            f.write("# {}\n".format(subtype))
            for rel in sorted(rels):
                f.write(rel + "\n")
                total += 1
            f.write("\n")
    return total


def write_outputs(agg):
    lists = agg["lists"]
    n_prom = write_list_file(
        PROMOTE_OUT, lists["promote"], "PROMOTE -- office sandbox + generation queue"
    )
    n_fav = write_list_file(FAVOUR_OUT, lists["favour"], "FAVOUR -- shortlist")
    # prune list: disfavour + dislike merged, keyed the same way
    prune_map = collections.defaultdict(list)
    for v in ("disfavour", "dislike"):
        for key, rels in lists[v].items():
            prune_map[key].extend(rels)
    for key in prune_map:
        prune_map[key] = sorted(set(prune_map[key]))
    n_prune = write_list_file(PRUNE_OUT, prune_map, "DISFAVOUR + DISLIKE -- prune / ignore")
    return {PROMOTE_OUT: n_prom, FAVOUR_OUT: n_fav, PRUNE_OUT: n_prune}


# --- selftest --------------------------------------------------------------
def selftest():
    # classification checks against real folder shapes
    assert classify_record(["reroll", "objects"], "chair_decent_1.png") == (
        "props",
        "props/chair_decent",
    ), classify_record(["reroll", "objects"], "chair_decent_1.png")
    assert classify_record(["characters", "worker_hoodie_m", "rotations"], "east.png") == (
        "characters",
        "characters/worker_hoodie_m",
    )
    assert classify_record(["characters", "cat_black", "rotations"], "north-east.png") == (
        "cats",
        "cats/cat_black",
    )
    assert classify_record(["reroll", "cats"], "cat_eldritch_1_south-west.png") == (
        "cats",
        "cats/cat_eldritch",
    )
    assert classify_record(["tilesets"], "floor_carpet_1.png") == (
        "tilesets",
        "tilesets/floor_carpet",
    )
    assert classify_record(["cosmetics"], "hat_medium_1.png") == (
        "cosmetics",
        "cosmetics/hat_medium",
    )
    assert classify_record([], "cat_ginger_east.png") == ("cats", "cats/cat_ginger")

    # synthetic inventory + verdicts exercising every aggregate
    records = []

    def add(rel, cat, subtype, fn):
        records.append({"rel": rel, "run": "pixellab_x", "cat": cat, "subtype": subtype, "fn": fn})

    # props: coat_rack promoted 3x (over), bin exists but never promoted (zero gap)
    add("pixellab_x/objects/coat_rack_1.png", "props", "props/coat_rack", "coat_rack_1.png")
    add("pixellab_x/objects/coat_rack_2.png", "props", "props/coat_rack", "coat_rack_2.png")
    add("pixellab_x/objects/coat_rack_3.png", "props", "props/coat_rack", "coat_rack_3.png")
    add(
        "pixellab_x/objects/bin_1.png", "props", "props/bin", "bin_1.png"
    )  # untouched + zero-promote
    add("pixellab_x/objects/desk_1.png", "props", "props/desk", "desk_1.png")  # 1 promote (under)
    add("pixellab_x/cats/cat_black_1.png", "cats", "cats/cat_black", "cat_black_1.png")
    verdicts = {
        "pixellab_x/objects/coat_rack_1.png": ["promote", "favour"],
        "pixellab_x/objects/coat_rack_2.png": ["promote"],
        "pixellab_x/objects/coat_rack_3.png": ["promote", "like"],
        "pixellab_x/objects/desk_1.png": ["promote"],
        "pixellab_x/cats/cat_black_1.png": ["favour", "like"],
        "pixellab_x/GONE/ghost_1.png": ["promote", "favour"],  # stale (not on disk)
        "pixellab_x/objects/bad_1.png": ["dislike"],  # stale dislike
    }
    # bad_1 is stale too (not in inventory) -> that's fine, still counted
    agg = summarize(verdicts, records)

    assert agg["total_tagged"] == 7, agg["total_tagged"]
    assert agg["verdict_counts"]["promote"] == 5, agg["verdict_counts"]
    assert agg["verdict_counts"]["favour"] == 3, agg["verdict_counts"]
    # promote by subtype: coat_rack 3, desk 1 (ghost is stale, excluded from by_sub)
    assert agg["by_sub"]["promote"]["props/coat_rack"] == 3, agg["by_sub"]["promote"]
    assert agg["by_sub"]["promote"]["props/desk"] == 1
    assert agg["by_cat"]["promote"]["props"] == 4, agg["by_cat"]["promote"]
    # stale: ghost has promote+favour, bad has dislike
    assert (
        agg["stale"]["promote"] == 1
        and agg["stale"]["favour"] == 1
        and agg["stale"]["dislike"] == 1
    )
    assert len(agg["stale_paths"]) == 2
    # over-represented props: coat_rack first
    over_props = agg["over"]["props"]
    assert over_props and over_props[0] == ("props/coat_rack", 3), over_props
    # zero-promote gap: bin present with 0 promotes
    under_props = dict((s, n) for (s, n, inv) in agg["under"]["props"])
    assert under_props.get("props/bin") == 0, under_props
    assert under_props.get("props/desk") == 1
    assert "props/coat_rack" not in under_props  # 3 promotes -> not under
    # untouched: bin_1 (never tagged) + cat_black is tagged; coat_racks tagged; desk tagged
    assert agg["untouched_by_cat"]["props"] == 1, agg["untouched_by_cat"]
    assert agg["untouched_total"] == 1

    # grouping/list assembly
    lists = agg["lists"]
    assert set(lists["promote"].keys()) == {("props", "props/coat_rack"), ("props", "props/desk")}
    assert sorted(lists["promote"][("props", "props/coat_rack")]) == [
        "pixellab_x/objects/coat_rack_1.png",
        "pixellab_x/objects/coat_rack_2.png",
        "pixellab_x/objects/coat_rack_3.png",
    ]
    # render must not throw and must mention the imbalance
    rep = render_report(agg, len(records))
    assert "props/coat_rack" in rep and "STALE" in rep and "ZERO promotes" in rep
    print("selftest OK: classification, aggregation, gaps, stale, grouping all pass")
    return 0


# --- main ------------------------------------------------------------------
def main(argv):
    if "--selftest" in argv:
        return selftest()

    try:
        verdicts = load_verdicts(VERDICTS_PATH)
    except (ValueError, json.JSONDecodeError) as e:
        print("ERROR: could not parse {}\n  {}".format(VERDICTS_PATH, e))
        print('Expected a flat object: { "relative/path.png": ["promote", ...] }')
        return 1

    if verdicts is None:
        print("No verdicts file found at:")
        print("  {}".format(VERDICTS_PATH))
        print("")
        print("Open the contact sheet (art_source/pixellab_contact_sheet.html),")
        print("tag sprites, click 'export JSON', and SAVE the downloaded")
        print("pixellab_verdicts.json to the path above. Then re-run:")
        print("  python tools/art_review/analyze_verdicts.py")
        return 0

    records = build_inventory(ART_DIR)
    if not records:
        print(
            "WARNING: no sprites found under {}/pixellab_* -- report will be empty.".format(ART_DIR)
        )
    agg = summarize(verdicts, records)

    print(render_report(agg, len(records)))

    print("")
    print("-- 3. ACTIONABLE FILES " + "-" * 46)
    written = write_outputs(agg)
    for path, n in written.items():
        print("    wrote {:4d} paths -> {}".format(n, path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
