#!/usr/bin/env python3
"""Read-only retention census for art_generated/.

Produces every number quoted in RETENTION_ANALYSIS.md in this directory.
Writes NOTHING to disk. art_generated/ is under MIGRATION-HOLD.

Run from the repo root:
    python docs/art/audit_2026-08-13/retention_census.py

Parsing guard (deliberate, see report section "Parsing guard"):
  a file is a resolution variant ONLY IF
    (a) its extension is one of .png/.webp/.jpg/.jpeg, AND
    (b) its filename stem ends in _<N> where N is in {1536,1024,768,512,256,128,64}.
  Everything else is reported separately as unparseable / non-image, never bucketed.
"""
import collections
import json
import os
import re
import struct
import sys

ROOT = "art_generated"
STATE = "tools/art_review/review_state.json"
RES = {1536, 1024, 768, 512, 256, 128, 64}
IMG = {".png", ".webp", ".jpg", ".jpeg"}
# verdicts were renamed 2026-08-13: valid = keep/remix/shelf/discard
LEGACY = {"iterate": "remix", "maybe": "remix", "reroll": "remix"}


def mb(b):
    return b / 1048576.0


def scan_tree():
    fam = collections.defaultdict(dict)  # famkey -> {res: bytes}
    unparse, nonimg = [], []
    total, nfiles = 0, 0
    for dirpath, _dirs, files in os.walk(ROOT):
        rel = os.path.relpath(dirpath, ROOT).replace(os.sep, "/")
        for name in files:
            path = os.path.join(dirpath, name)
            size = os.path.getsize(path)
            total += size
            nfiles += 1
            stem, ext = os.path.splitext(name)
            ext = ext.lower()
            if ext not in IMG:  # guard (a)
                nonimg.append((rel + "/" + name, size, ext))
                continue
            m = re.match(r"^(.*)_(\d+)$", stem)
            if not (m and int(m.group(2)) in RES):  # guard (b)
                unparse.append((rel + "/" + name, size, ext))
                continue
            fam[rel + "/" + m.group(1)][int(m.group(2))] = size
    return fam, unparse, nonimg, total, nfiles


def load_verdicts():
    state = json.load(open(STATE, encoding="utf-8"))
    gen, raw = {}, collections.Counter()
    for key, val in state.items():
        verdict = (val.get("verdict") or "").strip() if isinstance(val, dict) else ""
        raw[verdict] += 1
        if not verdict or not key.startswith("gen:"):
            continue
        parts = key.split(":")
        if len(parts) == 4:
            gen[(parts[1], parts[2], parts[3])] = LEGACY.get(verdict, verdict)
    return gen, raw


def verdict_for(famkey, gen):
    """famkey = '<block>/<vdir>/<base>'. gen key = gen:<block>:<family>:<variant>."""
    block = famkey.split("/")[0]
    base = famkey.split("/")[-1]
    m = re.match(r"^(.*)_(v\d+[a-z]?)$", base)
    if m and (block, m.group(1), m.group(2)) in gen:
        return gen[(block, m.group(1), m.group(2))]
    # fallback: filename carries no explicit _vN -> the variant is implicit v1
    if (block, base, "v1") in gen:
        return gen[(block, base, "v1")]
    return None


def png_dims(path):
    try:
        head = open(path, "rb").read(33)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", head[16:24])
    except (OSError, struct.error):
        pass
    return None


def game_references():
    """Distinct res:// image paths referenced from godot/ source (excl .godot, addons)."""
    pat = re.compile(r"res://[A-Za-z0-9_./-]+\.(?:png|webp|jpg|jpeg)", re.I)
    uidpat = re.compile(r"uid://[a-z0-9]+")
    src = {".gd", ".tscn", ".tres", ".json", ".cfg", ".godot"}
    refs, uids, uidmap = set(), set(), {}
    for dirpath, _dirs, files in os.walk("godot"):
        parts = dirpath.replace(os.sep, "/").split("/")
        if ".godot" in parts:
            continue
        for name in files:
            path = os.path.join(dirpath, name)
            if name.endswith(".uid"):
                try:
                    uidmap[open(path, encoding="utf-8").read().strip()] = os.path.join(
                        dirpath, name[:-4]
                    ).replace(os.sep, "/")
                except OSError:
                    pass
                continue
            if "addons" in parts or os.path.splitext(name)[1].lower() not in src:
                continue
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            refs.update(m.group(0) for m in pat.finditer(text))
            uids.update(m.group(0) for m in uidpat.finditer(text))
    paths = {"godot/" + r[len("res://") :] for r in refs}
    via_uid = {
        uidmap[u] for u in uids if u in uidmap and os.path.splitext(uidmap[u])[1].lower() in IMG
    }
    return paths | via_uid, len(refs), len(uids), len(via_uid)


def main():
    if not os.path.isdir(ROOT):
        sys.exit("run from the repo root: %s not found" % ROOT)

    fam, unparse, nonimg, total, nfiles = scan_tree()
    gen, raw = load_verdicts()

    groups = collections.defaultdict(list)
    for famkey, files in fam.items():
        groups[verdict_for(famkey, gen)].append((famkey, files))

    fam_bytes = sum(sum(f.values()) for f in fam.values())
    ub = sum(s for _, s, _ in unparse)
    nb = sum(s for _, s, _ in nonimg)

    print("=" * 72)
    print("1. INVENTORY")
    print("=" * 72)
    print("files                  %8d" % nfiles)
    print("bytes                  %14d  (%.1f MB)" % (total, mb(total)))
    print("families               %8d" % len(fam))
    print(
        "parseable variants     %8d  %14d bytes (%.1f MB)"
        % (sum(len(v) for v in fam.values()), fam_bytes, mb(fam_bytes))
    )
    print("unparseable IMAGES     %8d  %14d bytes (%.1f MB)" % (len(unparse), ub, mb(ub)))
    print("non-image files        %8d  %14d bytes (%.1f MB)" % (len(nonimg), nb, mb(nb)))
    print(
        "partition check        %14d == %d  %s"
        % (fam_bytes + ub + nb, total, "OK" if fam_bytes + ub + nb == total else "MISMATCH")
    )

    print("\nunparseable images by top-level block:")
    cnt, cby = collections.Counter(), collections.Counter()
    for p, s, _ in unparse:
        cnt[p.split("/")[0]] += 1
        cby[p.split("/")[0]] += s
    for k, n in cnt.most_common():
        print("  %-28s %5d  %12d bytes (%.1f MB)" % (k, n, cby[k], mb(cby[k])))

    print("\nnon-image files by extension:")
    cnt, cby = collections.Counter(), collections.Counter()
    for p, s, e in nonimg:
        cnt[e] += 1
        cby[e] += s
    for k, n in cnt.most_common():
        print("  %-8s %5d  %12d bytes (%.1f MB)" % (k, n, cby[k], mb(cby[k])))

    print("\n" + "=" * 72)
    print("2. FAMILY CENSUS AND BYTES BY RESOLUTION TIER")
    print("=" * 72)
    dist = collections.Counter(len(v) for v in fam.values())
    for k in sorted(dist):
        print("  %d tier(s): %5d families" % (k, dist[k]))
    print("  tier-sets present:")
    for k, n in collections.Counter(
        tuple(sorted(v, reverse=True)) for v in fam.values()
    ).most_common():
        print("    %-34s %5d families" % (str(k), n))
    tb, tn = collections.Counter(), collections.Counter()
    for files in fam.values():
        for r, s in files.items():
            tb[r] += s
            tn[r] += 1
    print("\n  %6s %8s %16s %12s" % ("tier", "files", "bytes", "MB"))
    for r in sorted(RES, reverse=True):
        print("  %6d %8d %16d %12.1f" % (r, tn[r], tb[r], mb(tb[r])))
    print(
        "  %6s %8d %16d %12.1f"
        % ("TOTAL", sum(tn.values()), sum(tb.values()), mb(sum(tb.values())))
    )

    print("\n" + "=" * 72)
    print("3. VERDICTS")
    print("=" * 72)
    print("raw verdict values in %s:" % STATE)
    for k, n in raw.most_common():
        print("  %-10r %d" % (k, n))
    print("\ngen: keys carrying a verdict: %d" % len(gen))
    print(
        "\n  %-9s %7s %16s %10s %16s %16s"
        % ("verdict", "fams", "bytes", "MB", "largest_only", "freed_by_rule_A")
    )
    for v in ["keep", "remix", "shelf", "discard", None]:
        g = groups.get(v, [])
        t = sum(sum(f.values()) for _, f in g)
        r = sum(f[max(f)] for _, f in g)
        print("  %-9s %7d %16d %10.1f %16d %16d" % (str(v), len(g), t, mb(t), r, t - r))

    print("\n" + "=" * 72)
    print("4. RULE A -- discard families keep HIGHEST resolution only")
    print("=" * 72)
    g = groups.get("discard", [])
    t = sum(sum(f.values()) for _, f in g)
    r = sum(f[max(f)] for _, f in g)
    print(
        "  families %d   current %d bytes   retained %d bytes   FREED %d bytes (%.1f MB)"
        % (len(g), t, r, t - r, mb(t - r))
    )

    print("\n" + "=" * 72)
    print("5. RULE B scaffolding -- keep families capped at a single tier")
    print("=" * 72)
    keeps = [f for _, f in groups.get("keep", [])]
    t = sum(sum(f.values()) for f in keeps)
    print("  keep families %d, current %d bytes (%.1f MB)" % (len(keeps), t, mb(t)))
    print("  %-8s %16s %16s %10s" % ("cap", "retained", "freed", "MB"))
    for cap in [1536, 1024, 768, 512, 256, 128, 64]:
        ret = 0
        for f in keeps:
            below = [x for x in f if x <= cap]
            ret += f[max(below)] if below else f[min(f)]
        print("  %-8d %16d %16d %10.1f" % (cap, ret, t - ret, mb(t - ret)))

    print("\n" + "=" * 72)
    print("6. UNDECIDED FAMILIES BY BLOCK")
    print("=" * 72)
    cnt, cby = collections.Counter(), collections.Counter()
    for famkey, files in groups.get(None, []):
        blk = famkey.split("/")[0]
        cnt[blk] += 1
        cby[blk] += sum(files.values())
    for k, n in cnt.most_common():
        print("  %-28s %5d families %14d bytes (%.1f MB)" % (k, n, cby[k], mb(cby[k])))
    tot_u = sum(cby.values())
    print(
        "  %-28s %5d families %14d bytes (%.1f MB)" % ("TOTAL", sum(cnt.values()), tot_u, mb(tot_u))
    )

    print("\n" + "=" * 72)
    print("7. WHAT THE GAME ACTUALLY REFERENCES")
    print("=" * 72)
    refs, n_res, n_uid, n_uid_img = game_references()
    exist = sorted(p for p in refs if os.path.isfile(p))
    print("  distinct res:// image refs      %d" % n_res)
    print("  distinct uid:// refs (all kinds) %d, resolving to images: %d" % (n_uid, n_uid_img))
    print("  referenced image paths           %d, existing on disk: %d" % (len(refs), len(exist)))
    print(
        "  referenced bytes on disk         %d (%.1f MB)"
        % (sum(os.path.getsize(p) for p in exist), mb(sum(os.path.getsize(p) for p in exist)))
    )
    print("\n  pixel dimensions of referenced images:")
    for k, n in collections.Counter(png_dims(p) for p in exist).most_common():
        print("    %-14s %5d" % (str(k), n))
    print("\n  referenced images at 512px or larger:")
    for p in sorted(exist, key=lambda x: -(max(png_dims(x)) if png_dims(x) else 0)):
        d = png_dims(p)
        if d and max(d) >= 512:
            print("    %-58s %-12s %10d" % (p, str(d), os.path.getsize(p)))


if __name__ == "__main__":
    main()
