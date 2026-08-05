#!/usr/bin/env python3
"""build_full_gallery.py -- ONE stateful drive-by gallery over ALL art on disk.

Layer: OBSERVE
Invoked by: human

Why a sibling and not an extension of build_morning_index.py: the morning index
is a hand-curated map of eight named batches and is deliberately verdict-free
("the map, not the workbench"). This tool is the opposite: it WALKS THE DISK so
nothing can be invisible (the 3-percent-coverage failure), and it captures
verdicts. Different generator, different lifecycle; both stay.

Coverage: every image file (png/jpg/jpeg/webp) under art_generated/ and
art_source/, grouped into batches by top-level directory, newest batch first.
Read-only on assets -- this script writes exactly one file, the HTML output.

Statefulness (the honest file:// story):
  - The page keeps verdicts/notes in browser localStorage, so they survive
    closing the tab.
  - Baseline verdicts from tools/art_review/review_state.json are baked into
    the page at build time, so already-judged assets show their verdict.
  - "E" in the page downloads a JSON export; merge it back with
        python tools/art_review/merge_gallery_export.py <downloaded.json>
    which folds it into review_state.json (the single verdict store that
    apply_review.py consumes). No second verdict store is invented.

asset_id compatibility with apply_review.py / review_state.json:
  gen:<category>:<base_id>:<variant>  for art_generated/<category>/v1 files
      matching <base>_<vN>_<size>.png or <base>_<size>.png (implicit v1).
  px:<relpath>                        for art_source files. Existing state uses
      extension-less relpaths; where a state key already exists it is reused
      verbatim (no duplicate keys). New px assets get the relpath WITH
      extension, which apply_review.py can actually resolve.
  file:<relpath-from-repo-root>       ADDITIVE extension, only for files no
      existing scheme can express (e.g. webp scene art, off-grid size stems,
      loose files outside a v1/ dir). apply_review.py resolves these since
      2026-08-04: single file, category derived from the path, destination
      filename kept verbatim.

Usage:
    python tools/art_review/build_full_gallery.py [--open]
Output:
    art_generated/full_gallery.html   (gitignored; open via file://)
"""

import argparse
import html
import json
import re
import sys
import time
import webbrowser
from pathlib import Path

# Sibling module (this script runs from tools/art_review/, which is
# sys.path[0] when invoked as a script). Supplies dest_rule_for_id -- the ONE
# mapping-coverage predicate shared with the report gate and the tests.
import apply_review

REPO = Path(__file__).resolve().parents[2]
ART_GEN = REPO / "art_generated"
ART_SRC = REPO / "art_source"
STATE = REPO / "tools" / "art_review" / "review_state.json"
OUT = ART_GEN / "full_gallery.html"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
KNOWN_SIZES = {64, 128, 256, 512, 768, 1024, 1536, 2048}
# preferred display size, best first (roughly "big enough to judge, small
# enough to load 9k of")
THUMB_PREF = [512, 768, 1024, 256, 1536, 128, 2048, 64]
GEN_STEM = re.compile(r"^(?P<base>.+?)(?:_(?P<var>v\d+))?_(?P<size>\d+)$")
VERDICT_MIGRATE = {"maybe": "iterate", "reroll": "iterate"}
VERDICTS = ("keep", "iterate", "discard")


def load_state():
    if not STATE.is_file():
        return {}
    try:
        raw = json.loads(STATE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return raw if isinstance(raw, dict) else {}


def migrate(v):
    v = (v or "").strip().lower()
    if v in VERDICTS:
        return v
    return VERDICT_MIGRATE.get(v, "")


# Directories that hold IMAGES but are not ART CANDIDATES. audiodump/ holds OBS
# playtest recordings and the frames extracted from them for timestamp analysis --
# 535 files across 5 frames_* dirs. Pip hit them in the 2026-08-04 review pass:
# "For some reason all these frames from my video grab of our audio review came in
# ... We do not want those showing up." A review tool that shows non-reviewable
# items spends the reviewer's attention on nothing, which is the scarcest thing
# in this loop.
SKIP_DIR_NAMES = {"audiodump", "logs", "velocity", "ceremony_2026-07-31"}
SKIP_DIR_PREFIXES = ("frames_",)


def _is_skipped(rel_parts):
    for seg in rel_parts:
        if seg in SKIP_DIR_NAMES or seg.startswith(SKIP_DIR_PREFIXES):
            return True
    return False


def iter_images(root):
    for p in sorted(root.rglob("*")):
        if not (p.is_file() and p.suffix.lower() in IMAGE_EXTS):
            continue
        if _is_skipped(p.relative_to(root).parts[:-1]):
            continue
        yield p


class AssetGroup:
    __slots__ = ("id", "name", "files", "thumb", "full")

    def __init__(self, asset_id, name):
        self.id = asset_id
        self.name = name
        self.files = []  # (path, size_or_None)
        self.thumb = None
        self.full = None


def scan(state):
    """Return list of batches: {title, mtime, assets:[AssetGroup]}."""
    batches = []

    def batch_for(files, title):
        if not files:
            return None
        mtime = max(p.stat().st_mtime for p, _ in files)
        return {"title": title, "mtime": mtime, "files": files}

    # ---- art_generated: batch per top-level dir ----
    gen_top = {}
    for p in iter_images(ART_GEN):
        rel = p.relative_to(ART_GEN)
        top = rel.parts[0] if len(rel.parts) > 1 else "(root)"
        gen_top.setdefault(top, []).append((p, "gen"))
    for top, files in gen_top.items():
        b = batch_for(files, f"art_generated/{top}")
        if b:
            batches.append(b)

    # ---- art_source: batch per top-level dir ----
    src_top = {}
    for p in iter_images(ART_SRC):
        rel = p.relative_to(ART_SRC)
        top = rel.parts[0] if len(rel.parts) > 1 else "(root)"
        src_top.setdefault(top, []).append((p, "px"))
    for top, files in src_top.items():
        b = batch_for(files, f"art_source/{top}")
        if b:
            batches.append(b)

    batches.sort(key=lambda b: b["mtime"], reverse=True)

    # ---- group each batch's files into assets with canonical ids ----
    for b in batches:
        groups = {}
        order = []
        for p, kind in b["files"]:
            asset_id, name, size = classify(p, kind, state)
            if asset_id not in groups:
                groups[asset_id] = AssetGroup(asset_id, name)
                order.append(asset_id)
            groups[asset_id].files.append((p, size))
        assets = []
        for aid in order:
            g = groups[aid]
            sized = [(p, s) for p, s in g.files if s is not None]
            if sized:
                by_pref = {s: p for p, s in sized}
                g.thumb = next((by_pref[s] for s in THUMB_PREF if s in by_pref), sized[0][0])
                g.full = max(sized, key=lambda t: t[1])[0]
            else:
                g.thumb = g.files[0][0]
                g.full = g.files[-1][0]
            assets.append(g)
        b["assets"] = assets
        del b["files"]
    return batches


def classify(p, kind, state):
    """Return (canonical asset_id, display name, size_or_None) for one file."""
    if kind == "gen":
        rel = p.relative_to(ART_GEN)
        # canonical gen id only for <category>/v1/<file>.png with a size stem
        if len(rel.parts) == 3 and rel.parts[1] == "v1" and p.suffix.lower() == ".png":
            m = GEN_STEM.match(p.stem)
            if m and int(m.group("size")) in KNOWN_SIZES:
                cat = rel.parts[0]
                base = m.group("base")
                var = m.group("var") or "v1"
                return (
                    f"gen:{cat}:{base}:{var}",
                    f"{base} {var}" if m.group("var") else base,
                    int(m.group("size")),
                )
        return (f"file:art_generated/{rel.as_posix()}", p.name, None)

    # px: reuse the existing state key spelling if one exists (600 legacy keys
    # are extension-less); otherwise use the resolvable with-extension form.
    rel = p.relative_to(ART_SRC).as_posix()
    sans = rel[: -len(p.suffix)]
    for candidate in (f"px:{sans}", f"px:{rel}"):
        if candidate in state:
            return (candidate, p.name, None)
    return (f"px:{rel}", p.name, None)


def build_page(batches, state):
    baseline = {}
    sections = []
    batch_index = []
    total_assets = 0
    total_files = 0
    matched = 0

    for bi, b in enumerate(batches):
        cards = []
        for g in b["assets"]:
            total_assets += 1
            total_files += len(g.files)
            entry = state.get(g.id)
            if entry and isinstance(entry, dict):
                v = migrate(entry.get("verdict"))
                n = entry.get("note") or ""
                if v or n:
                    baseline[g.id] = {"v": v, "n": n}
                    if v:
                        matched += 1
            thumb_href = href_of(g.thumb)
            full_href = href_of(g.full)
            nfiles = f'<span class="nf">x{len(g.files)}</span>' if len(g.files) > 1 else ""
            cards.append(
                f'<div class="card" data-id="{html.escape(g.id, quote=True)}" data-b="{bi}">'
                f'<a href="{full_href}" target="_blank" tabindex="-1">'
                f'<img loading="lazy" decoding="async" src="{thumb_href}" '
                f'alt="{html.escape(g.name, quote=True)}"></a>'
                f'<div class="meta"><span class="nm" title="{html.escape(g.id, quote=True)}">'
                f"{html.escape(g.name)}</span>{nfiles}</div>"
                f'<div class="vrow"><span class="badge"></span><span class="notetxt"></span></div>'
                f"</div>"
            )
        day = time.strftime("%Y-%m-%d", time.localtime(b["mtime"]))
        sections.append(
            f'<section class="batch" id="b{bi}" data-b="{bi}">'
            f'<h2>{html.escape(b["title"])}'
            f'<span class="bstat" id="bs{bi}"></span>'
            f'<span class="bdate">{day}</span></h2>'
            f'<div class="grid">{"".join(cards)}</div></section>'
        )
        batch_index.append(
            f'<a href="#b{bi}" data-b="{bi}">{html.escape(b["title"])} '
            f'<span class="bs" id="bi{bi}">{len(b["assets"])}</span></a>'
        )

    page = TEMPLATE
    page = page.replace("__SECTIONS__", "\n".join(sections))
    page = page.replace("__BATCHINDEX__", "\n".join(batch_index))
    page = page.replace("__BASELINE__", json.dumps(baseline, ensure_ascii=True))
    page = page.replace("__NBATCH__", str(len(batches)))
    page = page.replace("__BUILT__", time.strftime("%Y-%m-%d %H:%M"))
    return page, total_assets, total_files, matched


def href_of(p):
    """Path relative to the output file (which lives in art_generated/)."""
    try:
        rel = p.relative_to(ART_GEN)
        return html.escape(rel.as_posix(), quote=True)
    except ValueError:
        rel = p.relative_to(ART_SRC)
        return html.escape("../art_source/" + rel.as_posix(), quote=True)


def preflight_mapping(batches):
    """Batches whose asset ids cannot map to a destination or explicit Hold.

    Returns {batch_title: [unmappable asset ids]}. This is the pre-review
    gate for the #1093/#1107 recurrence (2026-08-04): a batch indexed without
    a mapping lets a whole review pass strand its own keeps -- the verdicts
    land, then apply_review's promotion gate fails AFTER the reviewing was
    spent. Failing HERE means the one-line map entry (destination or
    Hold(reason)) exists BEFORE any verdict is cast."""
    unmapped = {}
    for b in batches:
        bad = [g.id for g in b["assets"] if apply_review.dest_rule_for_id(g.id) is None]
        if bad:
            unmapped[b["title"]] = bad
    return unmapped


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--open", action="store_true")
    ap.add_argument(
        "--allow-unmapped",
        action="store_true",
        help="index batches that have no destination mapping anyway (their "
        "keep verdicts WILL be stranded until the map rules on them; the "
        "default is to refuse so the map gets its one-line entry first).",
    )
    args = ap.parse_args()

    t0 = time.time()
    state = load_state()
    batches = scan(state)

    unmapped = preflight_mapping(batches)
    if unmapped:
        print(
            "[!] {} batch(es) have assets with NO destination mapping -- a "
            "review pass over them would strand its own keeps:".format(len(unmapped))
        )
        for title, ids in sorted(unmapped.items()):
            print(f"    {title}  ({len(ids)} unmappable; e.g. {ids[0]})")
        print(
            "    Fix: add a godot/assets/... destination or an explicit "
            "Hold(reason) per batch in tools/art_review/apply_review.py "
            "(GEN_DEST / PX_DEST / PX_PREFIX_CATEGORY). A Hold is a "
            "first-class outcome for concept/reference/master material."
        )
        if not args.allow_unmapped:
            print("    Refusing to build (override: --allow-unmapped).")
            sys.exit(2)
        print("    --allow-unmapped given: building anyway.")

    page, n_assets, n_files, n_matched = build_page(batches, state)
    OUT.write_text(page, encoding="utf-8", newline="\n")
    dt = time.time() - t0

    # coverage cross-check: state keys whose asset never appeared on disk
    seen = set()
    for b in batches:
        for g in b["assets"]:
            seen.add(g.id)
    orphans = [k for k in state if k not in seen]

    print(f"[+] wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)")
    print(
        f"[*] {len(batches)} batches, {n_assets} assets ({n_files} image files), "
        f"{n_matched} with an existing verdict, built in {dt:.1f}s"
    )
    if orphans:
        print(
            f"[!] {len(orphans)} review_state keys matched no file on disk "
            f"(deleted/renamed assets); first few: {orphans[:5]}"
        )
    if args.open:
        webbrowser.open(OUT.as_uri())
    return 0


TEMPLATE = """<!doctype html>
<meta charset="utf-8">
<title>P(Doom)1 full art gallery -- stateful drive-by review</title>
<style>
  :root{--bg:#15151a;--fg:#e9e7e2;--dim:#96938c;--line:#33323b;--card:#1d1d24;
        --acc:#d9955c;--keep:#5fae6e;--iter:#d9b95c;--disc:#c96a5f;--sel:#7aa2d9}
  @media(prefers-color-scheme:light){:root{--bg:#f6f5f2;--fg:#1a1a18;--dim:#63615c;
        --line:#d9d6ce;--card:#fff;--acc:#7a3b12;--sel:#2c5c9c}}
  *{box-sizing:border-box}
  body{background:var(--bg);color:var(--fg);margin:0;padding:0 16px 120px;
       font:13px/1.5 ui-monospace,Consolas,monospace}
  #top{position:sticky;top:0;z-index:10;background:var(--bg);
       border-bottom:1px solid var(--line);padding:8px 0;margin:0 -16px 10px;
       padding-left:16px;padding-right:16px}
  #top h1{font-size:14px;margin:0 0 4px;display:inline}
  #prog{color:var(--dim);margin-left:12px}
  #curb{color:var(--acc)}
  #bar{height:4px;background:var(--line);border-radius:2px;margin-top:6px}
  #barfill{height:100%;background:var(--keep);border-radius:2px;width:0}
  #statewarn{color:var(--dim);font-size:11px;margin-top:4px}
  #statewarn b{color:var(--iter)}
  #bindings{color:var(--dim);font-size:11px;margin-top:2px}
  #bindings b{color:var(--fg)}
  #bindex{columns:3;font-size:11px;margin:0 0 14px;border:1px solid var(--line);
          border-radius:4px;padding:8px 12px}
  #bindex a{display:block;color:var(--dim);text-decoration:none;padding:1px 0}
  #bindex a:hover{color:var(--acc)}
  #bindex .bs{color:var(--acc)}
  .batch{border-top:1px solid var(--line);padding-top:10px;margin-bottom:22px;
         content-visibility:auto;contain-intrinsic-size:auto 600px}
  h2{font-size:13px;margin:0 0 8px;color:var(--acc)}
  .bstat{color:var(--dim);font-weight:400;font-size:11px;margin-left:10px}
  .bdate{float:right;color:var(--dim);font-weight:400;font-size:11px}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:4px;
        padding:6px;content-visibility:auto;contain-intrinsic-size:auto 210px}
  .card.sel{outline:2px solid var(--sel);outline-offset:1px}
  .card img{width:100%;height:150px;object-fit:contain;display:block;
            background:#0008;border-radius:3px}
  .meta{display:flex;justify-content:space-between;gap:6px;margin-top:4px}
  .nm{font-size:10px;color:var(--dim);overflow:hidden;text-overflow:ellipsis;
      white-space:nowrap}
  .nf{font-size:10px;color:var(--dim)}
  .vrow{min-height:14px;margin-top:2px;display:flex;gap:6px;align-items:baseline}
  .badge{font-size:10px;font-weight:700;letter-spacing:.05em}
  .badge.keep{color:var(--keep)} .badge.iterate{color:var(--iter)}
  .badge.discard{color:var(--disc)}
  .notetxt{font-size:10px;color:var(--dim);overflow:hidden;text-overflow:ellipsis;
           white-space:nowrap}
  .card.keep{border-color:var(--keep)} .card.iterate{border-color:var(--iter)}
  .card.discard{border-color:var(--disc)}
  body.hiderev .card.rev{display:none}
  #notebox{position:fixed;left:50%;bottom:60px;transform:translateX(-50%);
           width:min(640px,90vw);display:none;z-index:20}
  #notebox input{width:100%;padding:8px 10px;font:13px ui-monospace,Consolas,monospace;
           background:var(--card);color:var(--fg);border:1px solid var(--acc);
           border-radius:4px}
  #foot{position:fixed;left:0;right:0;bottom:0;background:var(--bg);
        border-top:1px solid var(--line);padding:6px 16px;font-size:11px;
        color:var(--dim);z-index:10}
  #foot b{color:var(--fg)}
  #help{position:fixed;inset:0;background:#000a;z-index:30;display:none}
  #help .in{background:var(--card);border:1px solid var(--line);border-radius:6px;
        max-width:640px;margin:8vh auto;padding:20px 26px;font-size:12px;line-height:1.7}
  #help h3{margin:0 0 8px;color:var(--acc)}
  #help kbd{background:var(--bg);border:1px solid var(--line);border-radius:3px;
        padding:0 5px;font-family:inherit}
  #unsaved{color:var(--iter);font-weight:700}
</style>

<div id="top">
  <h1>Full art gallery</h1>
  <span id="prog"></span> <span id="curb"></span>
  <div id="bar"><div id="barfill"></div></div>
  <div id="statewarn"><b>State lives in THIS browser's localStorage</b> (plus the
    baked-in baseline from review_state.json, built __BUILT__). A browser data
    clear loses unexported verdicts -- press <b>E</b> to export, then run
    <b>python tools/art_review/merge_gallery_export.py &lt;download&gt;</b> to fold
    them into review_state.json. Unexported changes: <span id="unsaved">0</span></div>
  <div id="bindings"><b>J/K</b> or arrows move | <b>L</b> like/keep |
    <b>I</b> iterate/remix | <b>X</b> discard | <b>U</b> clear | <b>N</b> note |
    <b>B</b>/<b>Shift+B</b> batch jump | <b>H</b> hide reviewed |
    <b>Shift+L/I/X</b> WHOLE BATCH (unreviewed only) |
    <b>Enter/O</b> open full | <b>E</b> export | <b>?</b> help</div>
</div>

<nav id="bindex">__BATCHINDEX__</nav>

__SECTIONS__

<div id="notebox"><input id="notein" placeholder="note -- Enter saves, Esc cancels"></div>
<div id="foot">Selected: <b id="selname">(none -- press J)</b>
  <span id="selverdict"></span></div>

<div id="help"><div class="in">
  <h3>Drive-by review -- keys</h3>
  <kbd>J</kbd>/<kbd>K</kbd> or arrow keys: next / previous asset<br>
  <kbd>L</kbd> like -> verdict <b>keep</b> (promotable) |
  <kbd>I</kbd> -> <b>iterate</b> (remix/regenerate) |
  <kbd>X</kbd> -> <b>discard</b> (off-brief) | <kbd>U</kbd> clear verdict<br>
  <kbd>N</kbd> note on selected asset | <kbd>Enter</kbd>/<kbd>O</kbd> open
  full-size | <kbd>B</kbd>/<kbd>Shift+B</kbd> next/prev batch |
  <kbd>H</kbd> hide reviewed | <kbd>E</kbd> export JSON<br>
  Verdicts auto-advance to the next visible asset. Click a card to select it.<br><br>
  <h3>Whole-batch verdicts</h3>
  <kbd>Shift+L</kbd> / <kbd>Shift+I</kbd> / <kbd>Shift+X</kbd> apply keep /
  iterate / discard to <b>every UNREVIEWED asset in the current batch</b>, after a
  confirm showing the count. For rotation sets and walk cycles, where eight files
  are one artistic decision.<br>
  <b>Assets you have already judged are never overwritten</b> -- a sweep only fills
  gaps, so it can follow a careful pass without undoing it.<br><br>
  <h3>Where state lives</h3>
  Verdicts persist in this browser's localStorage immediately on keypress.
  They are NOT in the repo until you press <kbd>E</kbd> (downloads
  gallery_verdicts_*.json) and run<br>
  <b>python tools/art_review/merge_gallery_export.py path/to/download.json</b><br>
  which merges into tools/art_review/review_state.json (newer timestamp wins,
  backup written). apply_review.py report / promote / reroll then work as usual.
  Press <kbd>?</kbd> to close.
</div></div>

<script>
"use strict";
var BASELINE = __BASELINE__;
var NBATCH = __NBATCH__;
var LS_KEY = "pdoom1_full_gallery_v1";
var LS_EXP = "pdoom1_full_gallery_last_export";

var local = {};
try { local = JSON.parse(localStorage.getItem(LS_KEY) || "{}") || {}; }
catch (e) { local = {}; }

function eff(id) {
  if (Object.prototype.hasOwnProperty.call(local, id)) {
    return { v: local[id].verdict || "", n: local[id].note || "" };
  }
  var b = BASELINE[id];
  return b ? { v: b.v || "", n: b.n || "" } : { v: "", n: "" };
}

var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
var batchIds = [];   // per batch: array of unique ids
var idBatch = {};    // id -> batch number (first seen)
for (var i = 0; i < NBATCH; i++) batchIds.push([]);
cards.forEach(function (c) {
  var id = c.dataset.id, b = +c.dataset.b;
  if (!(id in idBatch)) { idBatch[id] = b; batchIds[b].push(id); }
});
var totalAssets = Object.keys(idBatch).length;

function cardsFor(id) {
  return cards.filter(function (c) { return c.dataset.id === id; });
}
function paintCard(c) {
  var e = eff(c.dataset.id);
  var badge = c.querySelector(".badge"), note = c.querySelector(".notetxt");
  badge.textContent = e.v ? e.v.toUpperCase() : "";
  badge.className = "badge " + e.v;
  note.textContent = e.n;
  note.title = e.n;
  c.classList.remove("keep", "iterate", "discard", "rev");
  if (e.v) { c.classList.add(e.v, "rev"); }
}
function paintAll() { cards.forEach(paintCard); refreshCounts(); }

function refreshCounts() {
  var done = 0;
  for (var b = 0; b < NBATCH; b++) {
    var d = 0;
    batchIds[b].forEach(function (id) { if (eff(id).v) d++; });
    done += d;
    var bs = document.getElementById("bs" + b);
    if (bs) bs.textContent = d + " / " + batchIds[b].length + " reviewed";
    var bi = document.getElementById("bi" + b);
    if (bi) bi.textContent = d + "/" + batchIds[b].length;
  }
  document.getElementById("prog").textContent =
    done + " of " + totalAssets + " assets reviewed (" +
    (totalAssets ? Math.round(100 * done / totalAssets) : 0) + " percent)";
  document.getElementById("barfill").style.width =
    (totalAssets ? 100 * done / totalAssets : 0) + "%";
  refreshUnsaved();
}
function refreshUnsaved() {
  var last = localStorage.getItem(LS_EXP) || "";
  var n = 0;
  for (var id in local) {
    if ((local[id].updated_at || "") > last) n++;
  }
  document.getElementById("unsaved").textContent = n;
  window.__unsaved = n;
}

// ---- selection ----
var sel = -1;
function visible(c) { return c.offsetParent !== null; }
function select(i, scroll) {
  if (i < 0 || i >= cards.length) return;
  if (sel >= 0) cards[sel].classList.remove("sel");
  sel = i;
  var c = cards[sel];
  c.classList.add("sel");
  if (scroll !== false) c.scrollIntoView({ block: "center" });
  var e = eff(c.dataset.id);
  var b = +c.dataset.b;
  document.getElementById("selname").textContent = c.dataset.id;
  document.getElementById("selverdict").textContent =
    (e.v ? " [" + e.v + "]" : "") + (e.n ? " note: " + e.n : "");
  document.getElementById("curb").textContent =
    "| batch " + (b + 1) + " of " + NBATCH;
}
function move(step) {
  var i = sel;
  do { i += step; } while (i >= 0 && i < cards.length && !visible(cards[i]));
  if (i >= 0 && i < cards.length) select(i);
  else if (sel < 0 && cards.length) {
    for (var j = 0; j < cards.length; j++) if (visible(cards[j])) { select(j); break; }
  }
}
function jumpBatch(dir) {
  var cur = sel >= 0 ? +cards[sel].dataset.b : -1;
  var target = cur + dir;
  if (target < 0 || target >= NBATCH) return;
  for (var i = 0; i < cards.length; i++) {
    if (+cards[i].dataset.b === target && visible(cards[i])) { select(i); return; }
  }
  // batch fully hidden: keep going
  if (target >= 0 && target < NBATCH) {
    cur = target;
    while (cur + dir >= 0 && cur + dir < NBATCH) {
      cur += dir;
      for (var k = 0; k < cards.length; k++) {
        if (+cards[k].dataset.b === cur && visible(cards[k])) { select(k); return; }
      }
    }
  }
}
cards.forEach(function (c, i) {
  c.addEventListener("click", function (ev) {
    if (ev.target.tagName !== "IMG" && ev.target.tagName !== "A") select(i, false);
  });
});

// ---- verdict + note writes ----
function save() { localStorage.setItem(LS_KEY, JSON.stringify(local)); }
function setVerdict(v) {
  if (sel < 0) return;
  var id = cards[sel].dataset.id;
  var cur = eff(id);
  local[id] = { verdict: v, note: cur.n, tags: [],
                updated_at: new Date().toISOString() };
  save();
  cardsFor(id).forEach(paintCard);
  refreshCounts();
  select(sel, false);
  if (v) move(1);
}
// ---- BATCH verdicts -------------------------------------------------------
// Pip, 2026-08-04: "I don't like the idea of having to manually review all the
// frames of a walking animation, or if I do, there should be a batch selection
// option." A rotation set is ONE artistic decision spread over 8 files; making
// the reviewer press a key 8 times does not make the judgement any better, it
// just makes the pile look bigger than it is.
//
// Applies only to cards with NO existing verdict, so a considered per-asset call
// is never overwritten by a sweep. Confirms with a count first -- a bulk action
// that fires silently is how you lose an hour of judgement to one keystroke.
function setBatchVerdict(v) {
  if (sel < 0) return;
  var b = cards[sel].dataset.b;
  var targets = [];
  var seen = {};
  for (var i = 0; i < cards.length; i++) {
    if (cards[i].dataset.b !== b) continue;
    var id = cards[i].dataset.id;
    if (seen[id]) continue;
    if (eff(id).v) continue;            // never stomp an existing verdict
    seen[id] = 1;
    targets.push(id);
  }
  if (!targets.length) {
    alert("Nothing unreviewed left in this batch.");
    return;
  }
  var label = v ? v.toUpperCase() : "CLEAR";
  if (!confirm("Set " + label + " on " + targets.length +
               " UNREVIEWED asset(s) in this batch?

" +
               "Already-judged assets are left alone.")) return;
  var now = new Date().toISOString();
  targets.forEach(function (id) {
    local[id] = { verdict: v, note: eff(id).n, tags: [], updated_at: now };
  });
  save();
  targets.forEach(function (id) { cardsFor(id).forEach(paintCard); });
  refreshCounts();
  select(sel, false);
  if (!visible(cards[sel])) move(1);
}
var notebox = document.getElementById("notebox");
var notein = document.getElementById("notein");
function openNote() {
  if (sel < 0) return;
  notein.value = eff(cards[sel].dataset.id).n;
  notebox.style.display = "block";
  notein.focus();
}
notein.addEventListener("keydown", function (ev) {
  ev.stopPropagation();
  if (ev.key === "Enter") {
    var id = cards[sel].dataset.id;
    var cur = eff(id);
    local[id] = { verdict: cur.v, note: notein.value, tags: [],
                  updated_at: new Date().toISOString() };
    save();
    cardsFor(id).forEach(paintCard);
    refreshCounts();
    select(sel, false);
    notebox.style.display = "none";
  } else if (ev.key === "Escape") {
    notebox.style.display = "none";
  }
});

// ---- export ----
function doExport() {
  var blob = new Blob([JSON.stringify(local, null, 2)],
                      { type: "application/json" });
  var a = document.createElement("a");
  var ts = new Date().toISOString().slice(0, 16).replace(/[:T]/g, "-");
  a.href = URL.createObjectURL(blob);
  a.download = "gallery_verdicts_" + ts + ".json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  localStorage.setItem(LS_EXP, new Date().toISOString());
  refreshUnsaved();
}
window.addEventListener("beforeunload", function (ev) {
  if (window.__unsaved > 0) { ev.preventDefault(); ev.returnValue = ""; }
});

// ---- keys ----
document.addEventListener("keydown", function (ev) {
  if (ev.target === notein) return;
  if (ev.ctrlKey || ev.metaKey || ev.altKey) return;
  var k = ev.key;
  var handled = true;
  if (k === "j" || k === "J" || k === "ArrowRight" || k === "ArrowDown") move(1);
  else if (k === "k" || k === "K" || k === "ArrowLeft" || k === "ArrowUp") move(-1);
  else if (k === "l" || k === "1") setVerdict("keep");
  else if (k === "i" || k === "2") setVerdict("iterate");
  else if (k === "x" || k === "3") setVerdict("discard");
  else if (k === "u" || k === "U" || k === "0") setVerdict("");
  else if (k === "n" || k === "N") openNote();
  else if (k === "b") jumpBatch(1);
  else if (k === "B") jumpBatch(-1);
  else if (k === "L") setBatchVerdict("keep");
  else if (k === "I") setBatchVerdict("iterate");
  else if (k === "X") setBatchVerdict("discard");
  else if (k === "h" || k === "H") {
    document.body.classList.toggle("hiderev");
    if (sel >= 0 && !visible(cards[sel])) move(1);
  }
  else if (k === "e" || k === "E") doExport();
  else if (k === "Enter" || k === "o" || k === "O") {
    if (sel >= 0) window.open(cards[sel].querySelector("a").href, "_blank");
  }
  else if (k === "?") {
    var h = document.getElementById("help");
    h.style.display = h.style.display === "block" ? "none" : "block";
  }
  else handled = false;
  if (handled) ev.preventDefault();
});
document.getElementById("help").addEventListener("click", function () {
  this.style.display = "none";
});

paintAll();
</script>
"""


if __name__ == "__main__":
    raise SystemExit(main())
