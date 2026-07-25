#!/usr/bin/env python3
"""Generate art_generated/hero_gallery.html -- triage gallery for gpt-image-1 hero/banner/icon outputs."""
import glob
import json
import os
import re

import yaml

# Repo-relative: this script lives at <repo>/tools/art_review/ , so the repo
# root is three levels up. The HTML template sits next to this script.
_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
GEN = os.path.join(ROOT, "art_generated")
PROMPTS = os.path.join(ROOT, "art_prompts")
OUT = os.path.join(GEN, "hero_gallery.html")
TEMPLATE = os.path.join(_HERE, "hero_gallery_template.html")

IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")

# ---- transliterate common non-ascii so displayed text is clean ASCII ----
TRANS = {
    "\u2014": "--",
    "\u2013": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2026": "...",
    "\u2192": "->",
    "\u00a0": " ",
    "\u00b0": "deg",
    "\u00d7": "x",
    "\u2212": "-",
    "\u2011": "-",
    "\u00ad": "",
    "\u2022": "*",
}


def ascii_clean(s):
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    for k, v in TRANS.items():
        s = s.replace(k, v)
    # drop anything still non-ascii
    return s.encode("ascii", "ignore").decode("ascii")


# ---------------------------------------------------------------- prompts
def resolve_style(data, theme_name):
    """Return resolved style-context string for a theme (style_overrides + color_bias)."""
    parts = []
    styles = data.get("styles") or {}
    themes = data.get("themes") or {}
    th = themes.get(theme_name) or {}
    for ov in th.get("style_overrides") or []:
        txt = styles.get(ov)
        if txt:
            parts.append(ascii_clean(txt))
    cb = th.get("color_bias")
    if cb:
        parts.append(ascii_clean(cb))
    return "  ".join(parts)


# by_asset[(subdir, id)] = dict(prompt_tail, full_prompt, display_name, category, versions{ver:params})
by_asset = {}
prompt_yaml_files = []

for path in sorted(glob.glob(os.path.join(PROMPTS, "*.yaml"))) + sorted(
    glob.glob(os.path.join(PROMPTS, "*.json"))
):
    try:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except Exception as e:
        print("SKIP (parse fail):", path, e)
        continue
    if not isinstance(data, dict):
        continue
    subdir = data.get("asset_type")
    items = data.get("assets") or data.get("icons") or []
    if not subdir:
        # ui_icons.json has no asset_type -> icons list, subdir = ui_icons
        subdir = "ui_icons"
    global_icon = ascii_clean(data.get("global_style_icon") or "")
    prompt_yaml_files.append((os.path.basename(path), subdir, len(items)))
    for it in items:
        if not isinstance(it, dict):
            continue
        aid = it.get("id")
        if not aid:
            continue
        pt = ascii_clean(it.get("prompt_tail") or it.get("prompt") or "")
        theme = it.get("theme")
        style_ctx = resolve_style(data, theme) if theme else global_icon
        full = ("  ".join([p for p in [style_ctx, pt] if p])).strip()
        versions = {}
        for gh in it.get("generation_history") or []:
            ver = str(gh.get("version") or "")
            versions[ver] = {
                "md": ascii_clean(gh.get("model") or ""),
                "cs": gh.get("cost_usd"),
                "hs": ascii_clean(gh.get("full_prompt_hash") or ""),
                "ga": ascii_clean(gh.get("generated_at") or ""),
            }
        key = (subdir, aid.lower())
        # prefer entry that actually carries prompt text / history
        prev = by_asset.get(key)
        rec = {
            "pt": pt,
            "fp": full,
            "dn": ascii_clean(it.get("display_name") or aid),
            "cat": ascii_clean(it.get("category") or subdir),
            "versions": versions,
            "reroll_of": ascii_clean(it.get("reroll_of") or ""),
            "reroll_note": ascii_clean(it.get("reroll_note") or ""),
        }
        if prev is None or (not prev["pt"] and pt):
            by_asset[key] = rec

# ---------------------------------------------------------------- generation logs (ground-truth prompts)
# log lines: "... DEBUG | GENERATE: <id>_v<n>" then "... DEBUG | PROMPT: <full prompt>"
log_prompt = {}  # (id_lower, ver) -> {"fp":prompt, "md":model}
log_prompt_any = {}  # id_lower -> {"fp":prompt,"md":model}  (first seen)
gen_re = re.compile(r"GENERATE:\s*(?P<vid>\S+)")
info_gen_re = re.compile(r"Generating\s+(?P<vid>\S+)\s*\((?P<size>[0-9x]+),\s*(?P<model>[^)]+)\)")
ver_strip = re.compile(r"_v(\d+)$")
LOGDIR = os.path.join(GEN, "logs")
for lp in sorted(glob.glob(os.path.join(LOGDIR, "*.log"))):
    cur_vid = None
    cur_model = ""
    try:
        with open(lp, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                mi = info_gen_re.search(line)
                if mi:
                    cur_model = ascii_clean(mi.group("model").strip())
                mg = gen_re.search(line)
                if mg:
                    cur_vid = mg.group("vid")
                    continue
                idx = line.find("PROMPT:")
                if idx >= 0 and cur_vid:
                    prompt = ascii_clean(line[idx + 7 :].strip())
                    m = ver_strip.search(cur_vid)
                    if m:
                        vid_id = cur_vid[: m.start()].lower()
                        ver = "v" + m.group(1)
                    else:
                        vid_id = cur_vid.lower()
                        ver = ""
                    rec = {"fp": prompt, "md": cur_model or "openai gpt-image"}
                    log_prompt[(vid_id, ver)] = rec
                    log_prompt_any.setdefault(vid_id, rec)
                    cur_vid = None
    except Exception as e:
        print("log skip", lp, e)
print("log prompt entries:", len(log_prompt))

# global id fallback index (yaml) -- catches cross-subdir dupes (e.g. ui_* icons copied into game_icons/)
by_id_global = {}
for (sd, aid), rec in by_asset.items():
    by_id_global.setdefault(aid, rec)

# ---------------------------------------------------------------- images
fn_re = re.compile(r"^(?P<id>.+?)(?:_v(?P<ver>\d+))?(?:_(?P<size>\d+))?$")


def parse_name(stem):
    m = fn_re.match(stem)
    if not m:
        return stem, "", None
    gid = m.group("id")
    ver = m.group("ver")
    size = m.group("size")
    return gid, ("v" + ver if ver else ""), (int(size) if size else None)


# collect all image files
groups = {}  # (subdir, id, ver) -> {files:[(size,rel)], subdir,id,ver}
subdir_asset_ids = {}  # subdir -> sorted list of asset ids (for prefix fallback)
for sd, aid in by_asset:
    subdir_asset_ids.setdefault(sd, []).append(aid)
for sd in subdir_asset_ids:
    subdir_asset_ids[sd].sort(key=len, reverse=True)  # longest first

n_files = 0
for dirpath, _dirs, files in os.walk(GEN):
    for fn in files:
        if not fn.lower().endswith(IMG_EXT):
            continue
        n_files += 1
        rel = os.path.relpath(os.path.join(dirpath, fn), GEN).replace("\\", "/")
        subdir = rel.split("/")[0]
        stem = os.path.splitext(fn)[0]
        gid, ver, size = parse_name(stem)
        key = (subdir, gid, ver)
        g = groups.setdefault(key, {"subdir": subdir, "id": gid, "ver": ver, "files": []})
        g["files"].append((size if size is not None else 0, rel))


# ---------------------------------------------------------------- build entries
def match_prompt(subdir, gid):
    """Return (asset_id, pinfo) from yaml. pinfo carries prompt_tail + metadata."""
    gl = gid.lower()
    key = (subdir, gl)
    if key in by_asset:
        return gl, by_asset[key]
    # prefix fallback within same subdir
    for aid in subdir_asset_ids.get(subdir, []):
        if gl == aid or gl.startswith(aid + "_"):
            return aid, by_asset[(subdir, aid)]
    # global-id fallback (cross-subdir dupes)
    if gl in by_id_global:
        return gl, by_id_global[gl]
    return None, None


CAT_PALETTE = [
    "#e0a34a",
    "#8fae6b",
    "#6ba3b0",
    "#b57fb0",
    "#c98b3f",
    "#7f9fb5",
    "#b0906b",
    "#9a8fb0",
    "#6fae5a",
    "#c07f7f",
]

entries = []
matched = 0
cat_seen = {}
for key, g in groups.items():
    files = sorted(g["files"], key=lambda t: -t[0])  # largest first
    rep = files[0][1]
    aid, pinfo = match_prompt(g["subdir"], g["id"])
    gl = g["id"].lower()
    # log-based ground-truth prompt (per version, else any version of this id)
    log_rec = log_prompt.get((gl, g["ver"])) or log_prompt_any.get(gl)

    pt = pinfo["pt"] if pinfo else ""
    fp = pinfo["fp"] if pinfo else ""
    dn = pinfo["dn"] if pinfo else g["id"]
    rr = pinfo["reroll_note"] if pinfo else ""
    params = {}
    if pinfo and pinfo.get("versions"):
        params = pinfo["versions"].get(g["ver"], {}) or next(iter(pinfo["versions"].values()))
    md = ascii_clean(params.get("md") or "")
    cs = params.get("cs")
    hs = ascii_clean(params.get("hs") or "")
    ga = ascii_clean(params.get("ga") or "")

    # fill from log when yaml gave no prompt text
    if not fp and log_rec:
        fp = log_rec["fp"]
        if not pt:
            pt = log_rec["fp"]
        if not md:
            md = log_rec["md"] + " (from gen log)"

    has_prompt = bool(fp or pt)
    if has_prompt:
        matched += 1
    cat = (pinfo["cat"] if pinfo else g["subdir"]) or g["subdir"]
    cat_seen[cat] = cat_seen.get(cat, 0) + 1
    entries.append(
        {
            "r": rep,
            "u": g["subdir"],
            "c": cat,
            "f": os.path.basename(rep),
            "id": g["id"],
            "v": g["ver"],
            "dn": dn,
            "pt": pt,
            "fp": fp,
            "rr": rr,
            "md": md,
            "cs": cs,
            "hs": hs,
            "ga": ga,
            "w": has_prompt,
            "sz": [[s, r] for (s, r) in files],
        }
    )

# order: by run then category then id then version
entries.sort(key=lambda e: (e["u"], e["c"], e["id"], e["v"]))

cat_colors = {c: CAT_PALETTE[i % len(CAT_PALETTE)] for i, c in enumerate(sorted(cat_seen))}

total_imgs = n_files
n_entries = len(entries)
match_rate = f"{matched}/{n_entries}"
print(f"image files walked: {total_imgs}")
print(f"deduped entries (subdir,id,version @maxsize): {n_entries}")
print(f"matched to prompt: {matched} ({100*matched/max(1,n_entries):.1f}%)")
print("runs:", sorted(set(e["u"] for e in entries)))

DATA_JSON = json.dumps(entries, ensure_ascii=True, separators=(",", ":"))
CATCOL_JSON = json.dumps(cat_colors, ensure_ascii=True)

with open(TEMPLATE, encoding="utf-8") as fh:
    HTML_TEMPLATE = fh.read()

HTML = (
    HTML_TEMPLATE.replace("__DATA__", DATA_JSON)
    .replace("__CATCOLORS__", CATCOL_JSON)
    .replace("__NENTRIES__", str(n_entries))
    .replace("__NIMGS__", str(total_imgs))
    .replace("__MATCHED__", str(matched))
    .replace("__NRUNS__", str(len(set(e["u"] for e in entries))))
)

# guard: ensure ASCII only
bad = [c for c in HTML if ord(c) > 127]
if bad:
    print("WARNING non-ascii remaining:", set(bad))
with open(OUT, "w", encoding="ascii", newline="\n") as fh:
    fh.write(HTML)
print("wrote:", OUT, "bytes:", os.path.getsize(OUT))
