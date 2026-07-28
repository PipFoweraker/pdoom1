#!/usr/bin/env python3
"""Analyze art triage exports (verdict JSONs) for BOTH art libraries.

Two libraries, one tool:

  * sprites -- the pixellab pixel-art library under art_source/pixellab_* ,
    triaged via art_source/pixellab_contact_sheet.html -> "export JSON" saved
    to art_source/pixellab_verdicts.json .
  * hero    -- the gpt-image-1 hero/banner/icon library under art_generated/ ,
    triaged via art_generated/hero_gallery.html -> "export JSON" saved to
    art_source/hero_verdicts.json . Multi-size exports of one asset
    (foo_v2_64/128/256/512/1024.png) are DEDUPED to a single entry per
    (run-subdir, id, version) -- the same identity the gallery shows -- so a
    verdict on any size resolves to that one entry. Category = the run subdir
    (game_icons, ui_icons, hero_banners, ...). This mirrors the dedup + category
    logic in G:/tmp/gen_hero_gallery.py (re-implemented here, stdlib only).

For EACH library the report prints:
  1. Verdict summary  -- inventory total, tagged, per-tag counts; PROMOTE +
     FAVOUR broken down by category and finer subtype.
  2. Imbalance + gaps  -- over-represented promoted subtypes; zero/under-promoted
     subtypes that DO exist in inventory.
  3. UNTRIAGED report (the headline)  -- inventory assets with NO verdict at all,
     counted by category/subtype and as a % of that category, sorted most-first,
     so the owner can SEE where his judgment has not reached.
  4. Stale verdict paths  -- tagged but no longer on disk.

Per-library actionable path lists are written (grouped by "# category/subtype"):
  sprites -> art_source/{promote,favour,disfavour_dislike}_list.txt
  hero    -> art_source/hero_{promote,favour,disfavour_dislike}_list.txt

A missing verdicts JSON is handled gracefully (prints where to paste the export
and skips that library; the other still runs). stdlib only, Python 3.11, ASCII.

Usage:
  python tools/art_review/analyze_verdicts.py                 # both libraries
  python tools/art_review/analyze_verdicts.py --library hero  # just hero
  python tools/art_review/analyze_verdicts.py --library sprites
  python tools/art_review/analyze_verdicts.py --selftest      # synthetic checks
"""
import collections
import json
import os
import re
import sys

# --- paths -----------------------------------------------------------------
# Repo-relative: this script lives at <repo>/tools/art_review/ , so the repo
# root is three levels up. Works from any cwd.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ART_DIR = os.path.join(ROOT, "art_source")
GEN_DIR = os.path.join(ROOT, "art_generated")

# sprites (pixellab)
VERDICTS_PATH = os.path.join(ART_DIR, "pixellab_verdicts.json")
PROMOTE_OUT = os.path.join(ART_DIR, "promote_list.txt")
FAVOUR_OUT = os.path.join(ART_DIR, "favour_list.txt")
PRUNE_OUT = os.path.join(ART_DIR, "disfavour_dislike_list.txt")

# hero (gpt-image-1)
HERO_VERDICTS_PATH = os.path.join(ART_DIR, "hero_verdicts.json")
HERO_PROMOTE_OUT = os.path.join(ART_DIR, "hero_promote_list.txt")
HERO_FAVOUR_OUT = os.path.join(ART_DIR, "hero_favour_list.txt")
HERO_PRUNE_OUT = os.path.join(ART_DIR, "hero_disfavour_dislike_list.txt")

EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp")
VERDICTS = ["like", "dislike", "favour", "disfavour", "promote"]
CATS = ["characters", "cats", "props", "tilesets", "cosmetics", "other"]
TOP_N = 8  # over-represented subtypes to list per category
TOP_N_UNTRIAGED = 15  # untriaged subtypes to list per category before overflow

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


# --- sprite classification (copied from gen_contact_sheet.py) --------------
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


# --- sprite subtype derivation ---------------------------------------------
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


# --- sprite inventory scan -------------------------------------------------
def build_sprite_inventory(art_dir=ART_DIR):
    """Scan art_source/pixellab_* for images. Returns (records, alias).

    records: list of {rel, run, cat, subtype, fn}; rel is POSIX-style relative
    to art_dir (matching the verdict-JSON key form).
    alias: {} -- sprites have no multi-file dedup, so verdict keys map to
    themselves (identity)."""
    records = []
    if not os.path.isdir(art_dir):
        return records, {}
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
    return records, {}


# --- hero inventory scan (mirrors gen_hero_gallery.py dedup/category) -------
# filename stem -> (id, version, size); version + trailing size are optional.
_HERO_FN_RE = re.compile(r"^(?P<id>.+?)(?:_v(?P<ver>\d+))?(?:_(?P<size>\d+))?$")


def parse_hero_name(stem):
    """Split a hero filename stem into (id, version_label, size).
    'grant_proposal_v2_1024' -> ('grant_proposal', 'v2', 1024).
    'crt_overlay'            -> ('crt_overlay', '', None)."""
    m = _HERO_FN_RE.match(stem)
    if not m:
        return stem, "", None
    gid = m.group("id")
    ver = m.group("ver")
    size = m.group("size")
    return gid, ("v" + ver if ver else ""), (int(size) if size else None)


def build_hero_inventory(gen_dir=GEN_DIR):
    """Walk art_generated/ and dedup multi-size exports to one entry per
    (run-subdir, id, version), exactly as the hero gallery does. Returns
    (records, alias).

    records: list of {rel, run, cat, subtype, fn, members}. rel is the
    REPRESENTATIVE (largest-size) file, POSIX-relative to gen_dir; cat is the
    run subdir; subtype is 'cat/id'; members is every size-variant rel.
    alias: {member_rel: representative_rel} for every file, so a verdict on any
    size (or on the representative) resolves to the one deduped entry."""
    records, alias = [], {}
    if not os.path.isdir(gen_dir):
        return records, alias
    # (subdir, id, ver) -> [(size, rel), ...]
    groups = {}
    for dirpath, dirnames, filenames in os.walk(gen_dir):
        dirnames.sort()
        for fn in sorted(filenames):
            if not fn.lower().endswith(EXTS):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), gen_dir).replace("\\", "/")
            subdir = rel.split("/")[0]
            gid, ver, size = parse_hero_name(os.path.splitext(fn)[0])
            key = (subdir, gid, ver)
            groups.setdefault(key, []).append((size if size is not None else 0, rel))

    for (subdir, gid, ver), files in groups.items():
        # representative = largest size (ties broken by path for determinism)
        files_sorted = sorted(files, key=lambda t: (-t[0], t[1]))
        rep = files_sorted[0][1]
        members = [r for _s, r in files_sorted]
        cat = subdir
        subtype = "{}/{}".format(cat, gid.lower())
        records.append(
            {
                "rel": rep,
                "run": subdir,
                "cat": cat,
                "subtype": subtype,
                "fn": os.path.basename(rep),
                "members": members,
            }
        )
        for r in members:
            alias[r] = rep
    records.sort(key=lambda r: (r["cat"], r["subtype"], r["rel"]))
    return records, alias


def load_verdicts(path):
    """Return {rel: [tags]} with POSIX keys and known tags only, or None if the
    file is missing. Raises ValueError on a malformed (non-object) file.

    Per-item value accepts two shapes: the legacy bare tag array/string, and
    the notes-era {"tags": [...], "note": "..."} object (review_style.py's
    per-item free-text notes, issue #900 follow-up) -- the note is not needed
    for this report so it is simply dropped here."""
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
        elif isinstance(v, dict):
            v = v.get("tags") or []
        tags = [t for t in (v or []) if t in VERDICTS]
        if tags:
            out[key] = tags
    return out


def canonicalize_verdicts(verdicts, alias):
    """Remap verdict keys through alias (member -> representative) so a verdict
    on any size variant lands on the one deduped inventory entry. Keys not in
    alias pass through unchanged (identity for sprites; stale for hero). Tags
    from paths that collapse onto the same entry are merged (order-preserving,
    de-duplicated)."""
    if not alias:
        return dict(verdicts)
    out = {}
    for rel, tags in verdicts.items():
        canon = alias.get(rel, rel)
        acc = out.setdefault(canon, [])
        for t in tags:
            if t not in acc:
                acc.append(t)
    return out


# --- aggregation (pure; unit-tested by --selftest) -------------------------
def summarize(verdicts, records):
    """Cross-reference verdicts against the inventory.

    verdicts: {rel: [tags]} (already canonicalized to representative rels)
    records:  list of inventory record dicts
    Returns a dict of aggregates (see keys assembled at the end)."""
    inv_by_rel = {r["rel"]: r for r in records}

    verdict_counts = collections.Counter()
    # per-verdict breakdowns, only for on-disk assets
    by_cat = {v: collections.Counter() for v in VERDICTS}
    by_sub = {v: collections.Counter() for v in VERDICTS}
    # actionable path lists keyed (cat, subtype) -> [rel...]
    lists = {v: collections.defaultdict(list) for v in VERDICTS}
    stale = collections.Counter()  # tag -> count on paths not on disk
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

    # inventory-side coverage: subtypes per category + inventory sizes.
    inv_subtypes = collections.defaultdict(set)  # cat -> {subtype}
    inv_sub_count = collections.Counter()  # subtype -> inventory size
    inv_by_cat = collections.Counter()  # cat -> inventory size
    sub_to_cat = {}  # subtype -> cat
    for r in records:
        inv_subtypes[r["cat"]].add(r["subtype"])
        inv_sub_count[r["subtype"]] += 1
        inv_by_cat[r["cat"]] += 1
        sub_to_cat[r["subtype"]] = r["cat"]

    promote_by_sub = by_sub["promote"]
    # per category: over-represented (top promoted) and under/zero-promote
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

    # UNTRIAGED: assets on disk with NO verdict at all, by category and subtype.
    untriaged_by_cat = collections.Counter()
    untriaged_by_sub = collections.Counter()
    untriaged_total = 0
    for r in records:
        if r["rel"] not in tagged_rels:
            untriaged_by_cat[r["cat"]] += 1
            untriaged_by_sub[r["subtype"]] += 1
            untriaged_total += 1

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
        # untriaged aggregation (headline)
        "untriaged_by_cat": untriaged_by_cat,
        "untriaged_by_sub": untriaged_by_sub,
        "untriaged_total": untriaged_total,
        # inventory sizing (for % denominators)
        "inv_by_cat": inv_by_cat,
        "inv_sub_count": inv_sub_count,
        "sub_to_cat": sub_to_cat,
        "inv_total": len(records),
        # legacy aliases kept for backward-compat with earlier callers/tests
        "untouched_by_cat": untriaged_by_cat,
        "untouched_total": untriaged_total,
    }


# --- reporting -------------------------------------------------------------
def _pct(num, den):
    return (100.0 * num / den) if den else 0.0


def _fmt_counter(counter, indent="    "):
    lines = []
    for name, n in sorted(counter.items(), key=lambda x: (-x[1], x[0])):
        lines.append("{}{:5d}  {}".format(indent, n, name))
    return lines or ["{}(none)".format(indent)]


def render_report(agg, inv_total, title="ART"):
    L = []
    p = L.append
    p("=" * 70)
    p("{} VERDICT ANALYSIS".format(title))
    p("=" * 70)
    p("inventory on disk : {} assets".format(inv_total))
    p("tagged (triaged)  : {}".format(agg["total_tagged"]))
    p(
        "never triaged     : {}  ({:.1f}% of inventory)".format(
            agg["untriaged_total"], _pct(agg["untriaged_total"], inv_total)
        )
    )
    p("")

    # 1. VERDICT SUMMARY -----------------------------------------------------
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

    # 2. IMBALANCE + GAPS ----------------------------------------------------
    p("")
    p("-- 2. IMBALANCE + COVERAGE GAPS " + "-" * 38)
    any_imbalance = False
    for cat in sorted(agg["over"]):
        over = agg["over"][cat]
        under = agg["under"][cat]
        if not over and not under:
            continue
        any_imbalance = True
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
    if not any_imbalance:
        p("  (no verdicts to weigh yet)")

    # 3. UNTRIAGED (headline) -----------------------------------------------
    p("")
    p("-- 3. UNTRIAGED -- WHERE JUDGMENT HAS NOT REACHED " + "-" * 20)
    p(
        "  total untriaged: {} / {} inventory ({:.1f}%)".format(
            agg["untriaged_total"], inv_total, _pct(agg["untriaged_total"], inv_total)
        )
    )
    p("  by category (most untriaged first):")
    ubc = agg["untriaged_by_cat"]
    ibc = agg["inv_by_cat"]
    ubs = agg["untriaged_by_sub"]
    isc = agg["inv_sub_count"]
    sub_to_cat = agg["sub_to_cat"]
    # subtypes grouped under their category
    subs_of_cat = collections.defaultdict(list)
    for sub, n in ubs.items():
        subs_of_cat[sub_to_cat.get(sub, "?")].append((sub, n))
    if not ubc:
        p("      (nothing untriaged -- full coverage)")
    for cat, n in sorted(ubc.items(), key=lambda x: (-x[1], x[0])):
        cat_inv = ibc.get(cat, 0)
        p(
            "    {}  ({} / {} untriaged, {:.1f}% of category)".format(
                cat, n, cat_inv, _pct(n, cat_inv)
            )
        )
        rows = sorted(subs_of_cat.get(cat, []), key=lambda x: (-x[1], x[0]))
        for sub, sn in rows[:TOP_N_UNTRIAGED]:
            sub_inv = isc.get(sub, 0)
            p(
                "        {:4d} / {:<4d}  {}  ({:.0f}% of subtype)".format(
                    sn, sub_inv, sub, _pct(sn, sub_inv)
                )
            )
        if len(rows) > TOP_N_UNTRIAGED:
            hidden = sum(sn for _s, sn in rows[TOP_N_UNTRIAGED:])
            p(
                "        ... and {} more subtypes ({} untriaged assets)".format(
                    len(rows) - TOP_N_UNTRIAGED, hidden
                )
            )

    # 4. STALE ---------------------------------------------------------------
    stale_paths = agg["stale_paths"]
    p("")
    p("-- 4. STALE VERDICT PATHS (tagged but not on disk): {} ".format(len(stale_paths)) + "-" * 12)
    for rel in sorted(stale_paths)[:40]:
        p("      {}  {}".format(",".join(stale_paths[rel]), rel))
    if len(stale_paths) > 40:
        p("      ... and {} more".format(len(stale_paths) - 40))
    if not stale_paths:
        p("      (none -- every verdict path is on disk)")
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


def write_outputs(agg, promote_out, favour_out, prune_out, label):
    lists = agg["lists"]
    n_prom = write_list_file(
        promote_out,
        lists["promote"],
        "{} PROMOTE -- office sandbox + generation queue".format(label),
    )
    n_fav = write_list_file(favour_out, lists["favour"], "{} FAVOUR -- shortlist".format(label))
    # prune list: disfavour + dislike merged, keyed the same way
    prune_map = collections.defaultdict(list)
    for v in ("disfavour", "dislike"):
        for key, rels in lists[v].items():
            prune_map[key].extend(rels)
    for key in prune_map:
        prune_map[key] = sorted(set(prune_map[key]))
    n_prune = write_list_file(
        prune_out, prune_map, "{} DISFAVOUR + DISLIKE -- prune / ignore".format(label)
    )
    return {promote_out: n_prom, favour_out: n_fav, prune_out: n_prune}


# --- library configuration + driver ----------------------------------------
LIBRARIES = {
    "sprites": {
        "title": "PIXELLAB SPRITE",
        "label": "SPRITES",
        "verdicts": VERDICTS_PATH,
        "builder": build_sprite_inventory,
        "outputs": (PROMOTE_OUT, FAVOUR_OUT, PRUNE_OUT),
        "empty_warn": "no sprites found under art_source/pixellab_*",
        "paste_hint": [
            "Open the contact sheet (art_source/pixellab_contact_sheet.html),",
            "tag sprites, click 'export JSON', and SAVE the download to:",
            "  {}".format(VERDICTS_PATH),
        ],
    },
    "hero": {
        "title": "HERO / BANNER / ICON",
        "label": "HERO",
        "verdicts": HERO_VERDICTS_PATH,
        "builder": build_hero_inventory,
        "outputs": (HERO_PROMOTE_OUT, HERO_FAVOUR_OUT, HERO_PRUNE_OUT),
        "empty_warn": "no images found under art_generated/",
        "paste_hint": [
            "Open the hero gallery (art_generated/hero_gallery.html),",
            "tag assets, click 'export JSON', and SAVE the download to:",
            "  {}".format(HERO_VERDICTS_PATH),
        ],
    },
}


def run_library(key):
    """Analyze one library. Returns True if it ran, False if skipped/missing."""
    cfg = LIBRARIES[key]
    print("")
    print("#" * 70)
    print("# LIBRARY: {}  ({})".format(key, cfg["title"]))
    print("#" * 70)

    try:
        raw = load_verdicts(cfg["verdicts"])
    except (ValueError, json.JSONDecodeError) as e:
        print("ERROR: could not parse {}\n  {}".format(cfg["verdicts"], e))
        print('Expected a flat object: { "relative/path.png": ["promote", ...] }')
        return False

    if raw is None:
        print("No verdicts file found. paste the export to {}".format(cfg["verdicts"]))
        print("")
        for line in cfg["paste_hint"]:
            print("  " + line)
        print("  then re-run: python tools/art_review/analyze_verdicts.py --library {}".format(key))
        return False

    records, alias = cfg["builder"]()
    if not records:
        print("WARNING: {} -- report will be empty.".format(cfg["empty_warn"]))
    verdicts = canonicalize_verdicts(raw, alias)
    agg = summarize(verdicts, records)

    print(render_report(agg, len(records), title=cfg["title"]))

    print("")
    print("-- 5. ACTIONABLE FILES " + "-" * 46)
    promote_out, favour_out, prune_out = cfg["outputs"]
    written = write_outputs(agg, promote_out, favour_out, prune_out, cfg["label"])
    for path, n in written.items():
        print("    wrote {:4d} paths -> {}".format(n, path))
    return True


# --- selftest --------------------------------------------------------------
def selftest():
    # -- sprite classification against real folder shapes -------------------
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

    # -- hero filename parsing + dedup alias --------------------------------
    assert parse_hero_name("grant_proposal_v2_1024") == ("grant_proposal", "v2", 1024)
    assert parse_hero_name("crt_overlay") == ("crt_overlay", "", None)
    assert parse_hero_name("compute_v1") == ("compute", "v1", None)
    # a fake group of two sizes for one (subdir,id,ver) collapses to one entry;
    # the smaller-size verdict must resolve to the representative.
    alias = {
        "game_icons/foo_v1_512.png": "game_icons/foo_v1_1024.png",
        "game_icons/foo_v1_1024.png": "game_icons/foo_v1_1024.png",
    }
    canon = canonicalize_verdicts(
        {"game_icons/foo_v1_512.png": ["promote"], "game_icons/foo_v1_1024.png": ["like"]}, alias
    )
    assert canon == {"game_icons/foo_v1_1024.png": ["promote", "like"]}, canon

    # -- synthetic inventory + verdicts exercising every aggregate ----------
    records = []

    def add(rel, cat, subtype, fn):
        records.append({"rel": rel, "run": "pixellab_x", "cat": cat, "subtype": subtype, "fn": fn})

    # props: coat_rack promoted 3x (over), bin exists but never promoted (zero gap),
    #        desk 1 promote (under), lamp UNTRIAGED x2 (fully untriaged subtype)
    add("pixellab_x/objects/coat_rack_1.png", "props", "props/coat_rack", "coat_rack_1.png")
    add("pixellab_x/objects/coat_rack_2.png", "props", "props/coat_rack", "coat_rack_2.png")
    add("pixellab_x/objects/coat_rack_3.png", "props", "props/coat_rack", "coat_rack_3.png")
    add(
        "pixellab_x/objects/bin_1.png", "props", "props/bin", "bin_1.png"
    )  # untriaged + zero-promote
    add("pixellab_x/objects/desk_1.png", "props", "props/desk", "desk_1.png")  # 1 promote (under)
    add("pixellab_x/objects/lamp_1.png", "props", "props/lamp", "lamp_1.png")  # untriaged
    add("pixellab_x/objects/lamp_2.png", "props", "props/lamp", "lamp_2.png")  # untriaged
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
    agg = summarize(verdicts, records)

    assert agg["total_tagged"] == 7, agg["total_tagged"]
    assert agg["verdict_counts"]["promote"] == 5, agg["verdict_counts"]
    assert agg["verdict_counts"]["favour"] == 3, agg["verdict_counts"]
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
    # zero-promote gap: bin present with 0 promotes; lamp also 0 (untriaged too)
    under_props = dict((s, n) for (s, n, inv) in agg["under"]["props"])
    assert under_props.get("props/bin") == 0, under_props
    assert under_props.get("props/desk") == 1
    assert "props/coat_rack" not in under_props  # 3 promotes -> not under

    # -- UNTRIAGED aggregation (the new headline) ---------------------------
    # untriaged assets: bin_1, lamp_1, lamp_2  (cat_black tagged; coat_racks/desk tagged)
    assert agg["untriaged_total"] == 3, agg["untriaged_total"]
    assert agg["untriaged_by_cat"]["props"] == 3, agg["untriaged_by_cat"]
    assert "cats" not in agg["untriaged_by_cat"], agg["untriaged_by_cat"]
    # by subtype
    assert agg["untriaged_by_sub"]["props/lamp"] == 2, agg["untriaged_by_sub"]
    assert agg["untriaged_by_sub"]["props/bin"] == 1, agg["untriaged_by_sub"]
    assert "props/coat_rack" not in agg["untriaged_by_sub"]  # fully triaged
    # denominators for %: category inventory + subtype inventory
    assert agg["inv_by_cat"]["props"] == 7, agg["inv_by_cat"]
    assert agg["inv_by_cat"]["cats"] == 1
    assert agg["inv_sub_count"]["props/lamp"] == 2
    assert agg["sub_to_cat"]["props/lamp"] == "props"
    # props untriaged % of category = 3/7; lamp = 2/2 = 100% of subtype
    assert (
        abs(_pct(agg["untriaged_by_cat"]["props"], agg["inv_by_cat"]["props"]) - (300.0 / 7)) < 1e-9
    )
    assert (
        abs(_pct(agg["untriaged_by_sub"]["props/lamp"], agg["inv_sub_count"]["props/lamp"]) - 100.0)
        < 1e-9
    )
    # legacy aliases still populated
    assert agg["untouched_total"] == 3 and agg["untouched_by_cat"]["props"] == 3

    # -- grouping/list assembly ---------------------------------------------
    lists = agg["lists"]
    assert set(lists["promote"].keys()) == {("props", "props/coat_rack"), ("props", "props/desk")}
    assert sorted(lists["promote"][("props", "props/coat_rack")]) == [
        "pixellab_x/objects/coat_rack_1.png",
        "pixellab_x/objects/coat_rack_2.png",
        "pixellab_x/objects/coat_rack_3.png",
    ]
    # -- render must not throw and must surface imbalance + untriaged --------
    rep = render_report(agg, len(records), title="SELFTEST")
    assert "props/coat_rack" in rep and "STALE" in rep and "ZERO promotes" in rep
    assert "UNTRIAGED" in rep and "props/lamp" in rep and "% of category" in rep
    print("selftest OK: classification, hero-dedup alias, aggregation, gaps,")
    print("             untriaged (cat+subtype+%), stale, grouping all pass")
    return 0


# --- main ------------------------------------------------------------------
def main(argv):
    if "--selftest" in argv:
        return selftest()

    which = "both"
    if "--library" in argv:
        i = argv.index("--library")
        if i + 1 < len(argv):
            which = argv[i + 1].lower()
    if which not in ("sprites", "hero", "both"):
        print("ERROR: --library must be one of: sprites, hero, both")
        return 2

    keys = ["sprites", "hero"] if which == "both" else [which]
    for k in keys:
        run_library(k)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
