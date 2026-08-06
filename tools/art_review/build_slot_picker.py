#!/usr/bin/env python3
"""build_slot_picker.py -- the SLOT PICKER page.

Generates art_generated/slot_picker.html: a local, offline, one-file page for
the single taste pass docs/design/ASSET_PAYLOAD_ANALYSIS_2026-08-06.md leaves
to Pip (its sequencing steps 4 and half of 5). Everything else in the payload
reduction is mechanical.

Two sections, two DIFFERENT decision shapes -- deliberately not mixed:

  1. FRAME ROLES (15).  "Keep the painted texture, or replace it with
     geometry?"  These are 512px PICTURES of a 12px corner. Verdicts on them
     were never wrong; the wrong bit was assuming keep implies ship-as-is.
     Answer per role: StyleBoxFlat / 9-slice extract / ship whole / drop.

  2. SLOT CLUSTERS (contested roles).  "Which ONE of these competing Library
     assets does this slot pin?"  Shown AT THE SIZE THE GAME DRAWS THEM
     (action-bar tiles are 70x70; hero art is 408 wide) as well as full size,
     because "which looks best at 512" is the wrong question for a 512px
     master behind a 70px tile.

What this tool does NOT do
--------------------------
It records decisions. It never promotes, moves, copies, deletes or edits a
single art file, and it never touches review_state.json -- your 2,713 verdicts
are read-only input here. A pick is a property of the (asset, SLOT) PAIRING,
so it is written as a manifest-shaped selection entry, NOT as a new verdict
value on the asset (ADR-0019 / the analysis's rejected option (a)).

Round trip -- the same shape as the full gallery you already use
---------------------------------------------------------------
  1. python tools/art_review/build_slot_picker.py --open
  2. pick in the browser; state lives in localStorage as you go
  3. press E -> downloads slot_picks_export_<stamp>.json
  4. python tools/art_review/apply_slot_picks.py <that file>
     -> merges into tools/assets/demand/slot_picks.json, which is TRACKED IN
        GIT. `git diff` on it IS the manifest diff.

Usage:
    python tools/art_review/build_slot_picker.py [--open] [--out PATH]
                                                 [--state PATH]
"""

import argparse
import html
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import review_style  # noqa: E402
import slot_model  # noqa: E402

REPO = slot_model.REPO
ART_GEN = REPO / "art_generated"
ART_SRC = REPO / "art_source"
DEFAULT_OUT = ART_GEN / "slot_picker.html"

try:
    from PIL import Image
except ImportError:  # dimensions are a nicety, not a dependency
    Image = None


def href_of(p: Path):
    """Path relative to the output file, which lives in art_generated/ --
    identical scheme to build_full_gallery.href_of so the page works offline
    from file:// with no copying and no data: URIs."""
    try:
        return html.escape(p.relative_to(ART_GEN).as_posix(), quote=True)
    except ValueError:
        return html.escape("../art_source/" + p.relative_to(ART_SRC).as_posix(), quote=True)


def dims(p: Path):
    if Image is None:
        return None
    try:
        with Image.open(p) as im:
            return list(im.size)
    except Exception:
        return None


def cand_payload(c):
    return {
        "rel": c.rel,
        "href": href_of(c.src),
        "name": c.name,
        "variant": c.variant,
        "kb": round(c.bytes / 1024),
        "px": dims(c.src),
        "note": c.note,
        "asset_id": c.asset_id,
    }


def build_data(clusters, frame_roles, stats):
    return {
        "built": time.strftime("%Y-%m-%d %H:%M"),
        "stats": stats,
        "frames": [
            {
                "id": f.role_id,
                "kb": round(f.bytes / 1024),
                "cands": [cand_payload(c) for c in f.candidates],
            }
            for f in frame_roles
        ],
        "clusters": [
            {
                "id": cl.slot_id,
                "dest": cl.dest,
                "stem": cl.stem,
                "draw": cl.draw_px,
                "why": cl.draw_why,
                "kb": round(cl.bytes / 1024),
                "default": cl.default_pick(),
                "cands": [cand_payload(c) for c in cl.candidates],
            }
            for cl in clusters
        ],
    }


PAGE = r"""<meta charset="utf-8">
<title>slot picker -- one winner per contested slot</title>
<style>
/* Colours come from review_style.PALETTE (the house "warm cozy-grim CRT"
   vocabulary). The picker adopts the PALETTE and the checkerboard-under-alpha
   ground; it deliberately does NOT adopt review_style's verdict machinery --
   that machinery exports {rel: [tags]} into the VERDICT store, and a pick is
   not a verdict. Same reason serve_review.py sits at "adopt BASE_CSS only" in
   the migration table. */
:root { color-scheme: dark; __VARS__ }
body { background:var(--bg); color:var(--fg); font:13px/1.45 "Segoe UI",system-ui,sans-serif;
       margin:0; padding:0 0 240px; }
header { position:sticky; top:0; z-index:40; background:var(--bg); padding:10px 16px;
         border-bottom:1px solid var(--line); }
h1 { font-size:15px; margin:0 0 6px; letter-spacing:.4px; color:var(--amber2); }
h2 { font-size:14px; margin:28px 16px 8px; padding-top:10px; letter-spacing:.4px;
     border-top:1px solid var(--line); color:var(--amber); }
.sub { color:var(--dim); font-size:12px; }
.bar { display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin-top:6px; }
select, input[type=text] { background:var(--bg3); color:var(--fg); border:1px solid var(--line);
       border-radius:3px; padding:3px 6px; font:12px inherit; }
button { background:var(--bg3); color:var(--fg); border:1px solid var(--line); border-radius:3px;
       padding:3px 9px; font:12px inherit; cursor:pointer; }
button:hover { border-color:var(--amber); }
button.on { background:var(--green); border-color:var(--green); color:#0f1a0c; }
.warn { background:var(--bg2); border:1px solid var(--amber); color:var(--amber2); padding:7px 10px;
        margin:10px 16px; border-radius:3px; font-size:12px; }
.note-in { background:var(--bg); border:1px solid var(--line); color:var(--fg); width:100%;
        font:12px inherit; padding:4px 6px; border-radius:3px; }
.row { border:1px solid var(--line); border-left:3px solid var(--line); background:var(--bg2);
       margin:8px 16px; border-radius:4px; }
.row.focus { border-left-color:var(--amber2); box-shadow:0 0 0 1px var(--amber) inset; }
.row.done { border-left-color:var(--green); }
.row.defer { border-left-color:var(--amber); }
.rhead { display:flex; gap:10px; align-items:baseline; padding:7px 10px; flex-wrap:wrap; }
.rid { font-family:Consolas,monospace; font-size:12.5px; color:var(--fg); }
.rmeta { color:var(--dim); font-size:11.5px; }
.badge { font-size:10.5px; padding:1px 6px; border-radius:8px; border:1px solid var(--line);
         color:var(--dim); }
.badge.draw { border-color:var(--amber); color:var(--amber2); }
.cards { display:flex; gap:10px; flex-wrap:wrap; padding:0 10px 9px; }
.card { border:1px solid var(--line); border-radius:4px; background:var(--bg); padding:6px;
        width:186px; cursor:pointer; }
.card:hover { border-color:var(--amber); }
.card.win { border-color:var(--green); box-shadow:0 0 0 1px var(--green) inset; }
/* The gamebox is a FLAT DARK tile on purpose -- it stands in for the ground the
   action bar actually draws these on. No checkerboard here; checkerboard is for
   judging alpha, which is the full-size preview's job. */
.gamebox { background:#0b0a09; border:1px dashed var(--line); display:flex; align-items:center;
        justify-content:center; padding:8px; margin-bottom:5px; min-height:86px; }
.gamebox img { display:block; image-rendering:auto; }
.full { display:block; width:100%; background:__CHECKER__; border:1px solid var(--line); }
.cmeta { font-family:Consolas,monospace; font-size:10.5px; color:var(--dim); margin-top:4px;
         word-break:break-all; }
.cvar { color:var(--fg); font-weight:600; }
.cnote { color:var(--amber); font-size:11px; margin-top:3px; }
.pickno { float:right; color:var(--dim); }
.frow .cards .card { width:150px; }
.tbtn { margin-right:5px; }
#help { position:fixed; right:0; bottom:0; left:0; background:var(--bg); padding:8px 16px;
        border-top:1px solid var(--line); font-size:11.5px; color:var(--dim); z-index:50; }
kbd { background:var(--bg3); border:1px solid var(--line); border-radius:3px; padding:0 4px;
      font-family:Consolas,monospace; color:var(--fg); }
#modal { position:fixed; inset:0; background:#000d; z-index:90; display:none;
         align-items:center; justify-content:center; }
#modal img { max-width:96vw; max-height:92vh; background:__CHECKER__; }
#toast { position:fixed; top:8px; right:12px; background:var(--green); color:#0f1a0c;
         padding:6px 12px; border-radius:3px; z-index:99; display:none; }
</style>

<header>
  <h1>SLOT PICKER &mdash; one winner per contested slot</h1>
  <div class="sub" id="counts"></div>
  <div class="bar">
    <button id="f-open">Undecided</button>
    <button id="f-done">Decided</button>
    <button id="f-all">All</button>
    <span class="sub">|</span>
    <select id="dest"></select>
    <select id="ncand"></select>
    <input type="text" id="q" placeholder="filter by name..." size="18">
    <span class="sub">|</span>
    <span class="sub">game-size zoom</span>
    <button id="z1">1x</button><button id="z2">2x</button><button id="z4">4x</button>
    <span class="sub">|</span>
    <span class="sub">batch:</span>
    <button class="bapply" data-v="1">all v1</button>
    <button class="bapply" data-v="2">all v2</button>
    <button class="bapply" data-v="3">all v3</button>
    <button class="bapply" data-v="4">all v4</button>
    <button class="bapply" data-v="hi">all highest</button>
    <span class="sub">(applies to the VISIBLE undecided clusters only)</span>
    <span class="sub">|</span>
    <button id="exp">E &mdash; export</button>
  </div>
</header>

<div class="warn">
  Picks live in THIS browser's localStorage until you press <kbd>E</kbd>. That downloads
  <b>slot_picks_export_&lt;stamp&gt;.json</b>; fold it into the repo with<br>
  <b>python tools/art_review/apply_slot_picks.py &lt;download&gt;</b> &mdash; which writes
  <b>tools/assets/demand/slot_picks.json</b>, tracked in git.
  Notes typed here travel with the pick. Nothing here edits review_state.json or moves any file.
  <span id="lastexp"></span>
</div>

<h2>1 &mdash; FRAME ROLES <span class="sub">(UI source material: keep the painted
  texture, or replace it with geometry?)</span></h2>
<div class="sub" style="margin:0 16px 6px">
  512px pictures of a 12px corner. Per role: <b>StyleBoxFlat</b> (geometric, zero texture bytes,
  resolution-independent) / <b>9-slice</b> (the painted texture is the point &mdash; crop
  corner+edge regions into one small atlas) / <b>ship whole</b> (it really is a full-screen
  image) / <b>drop</b>. Click a variant to nominate WHICH master the 9-slice or whole ship uses.
</div>
<div id="frames"></div>

<h2>2 &mdash; CONTESTED SLOTS <span class="sub">(one winner per slot; the losers stay
  Library assets no manifest entry names &mdash; nothing is done TO them)</span></h2>
<div id="clusters"></div>

<div id="modal"><img id="modalimg" src=""></div>
<div id="toast"></div>
<div id="help">
  <kbd>j</kbd>/<kbd>k</kbd> next/prev &nbsp; <kbd>1</kbd>..<kbd>9</kbd> pick that candidate &nbsp;
  <kbd>n</kbd> note &nbsp; <kbd>x</kbd> defer (decide later) &nbsp; <kbd>u</kbd> reopen (clear
  pick) &nbsp; <kbd>s</kbd>/<kbd>9</kbd>/<kbd>w</kbd> frame treatment &nbsp;
  <kbd>f</kbd> full size &nbsp; <kbd>E</kbd> export &nbsp;
  <span class="sub">reopening is expected &mdash; taste sessions are not one-shot.</span>
</div>

<script>
var DATA = __DATA__;
var LS = "pdoom1_slot_picks_v1", LSE = "pdoom1_slot_picks_exported";
// Storage shim. Some browsers refuse localStorage on file:// (opaque origin)
// and THROW rather than return null. Unguarded, that kills the page on load
// and the failure looks like "the tool is broken". Degrade to in-memory --
// picks still work for the session, and E still exports them; the banner says
// so. Silent data loss is the thing to avoid, not the storage itself.
var MEM = {}, STORE_OK = true;
function sget(k) { try { return localStorage.getItem(k); }
                   catch (e) { STORE_OK = false; return MEM[k] === undefined ? null : MEM[k]; } }
function sset(k, v) { try { localStorage.setItem(k, v); }
                      catch (e) { STORE_OK = false; MEM[k] = v; } }
var picks = {};
try { picks = JSON.parse(sget(LS) || "{}") || {}; } catch (e) { picks = {}; }
var filter = "open", zoom = 1, focus = 0, order = [];

function save() { sset(LS, JSON.stringify(picks)); }
function now() { return new Date().toISOString(); }
function esc(s) { return String(s).replace(/[&<>"]/g, function (c) {
  return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]; }); }
function toast(m) { var t = document.getElementById("toast"); t.textContent = m;
  t.style.display = "block"; clearTimeout(t._h); t._h = setTimeout(function () {
  t.style.display = "none"; }, 1400); }

// ---- render helpers -------------------------------------------------------
function gameImg(c, draw) {
  // draw==0 means "the game draws this at native size" -- there is nothing to
  // shrink, so cap the preview for layout instead of inventing a game size.
  var w = draw ? draw * zoom : 0;
  if (w) return '<img loading="lazy" src="' + c.href + '" style="width:' + w +
                'px;height:' + w + 'px">';
  return '<img loading="lazy" src="' + c.href + '" style="max-width:160px;max-height:110px">';
}
function cardHtml(c, i, chosen, draw) {
  return '<div class="card' + (chosen ? ' win' : '') + '" data-rel="' + esc(c.rel) + '">' +
    '<div class="gamebox">' + gameImg(c, draw) + '</div>' +
    '<img class="full" loading="lazy" src="' + c.href + '">' +
    '<div class="cmeta"><span class="pickno">' + (i + 1) + '</span>' +
    '<span class="cvar">' + esc(c.variant) + '</span> &middot; ' + c.kb + ' KB' +
    (c.px ? ' &middot; ' + c.px[0] + 'x' + c.px[1] : '') + '<br>' + esc(c.name) + '</div>' +
    (c.note ? '<div class="cnote">review note: ' + esc(c.note) + '</div>' : '') +
    '</div>';
}
function noteBox(id) {
  var p = picks[id] || {};
  return '<div style="padding:0 10px 8px"><input class="note-in" data-note="' + esc(id) +
    '" placeholder="note (travels with the pick into slot_picks.json)" value="' +
    esc(p.note || "") + '"></div>';
}
function stateOf(id) { var p = picks[id]; if (!p) return ""; return p.status || ""; }

function clusterHtml(cl, idx) {
  var p = picks["slot:" + cl.id] || {}, st = p.status || "";
  var cls = "row" + (st === "chosen" ? " done" : st === "deferred" ? " defer" : "") +
            (idx === focus ? " focus" : "");
  var h = '<div class="' + cls + '" id="row_slot:' + esc(cl.id) + '" data-id="slot:' +
    esc(cl.id) + '" data-idx="' + idx + '">';
  h += '<div class="rhead"><span class="rid">' + esc(cl.stem) + '</span>' +
    '<span class="rmeta">' + esc(cl.dest) + '</span>' +
    '<span class="badge draw">' + (cl.draw ? 'game draws ' + cl.draw + 'px' : 'native size') +
    '</span><span class="badge">' + esc(cl.why) + '</span>' +
    '<span class="badge">' + cl.cands.length + ' candidates, ' + cl.kb + ' KB</span>' +
    (st ? '<span class="badge">' + st.toUpperCase() + '</span>' : '') + '</div>';
  h += '<div class="cards">';
  for (var i = 0; i < cl.cands.length; i++)
    h += cardHtml(cl.cands[i], i, p.src === cl.cands[i].rel, cl.draw);
  h += '</div>' + noteBox("slot:" + cl.id) + '</div>';
  return h;
}

var TREAT = [["styleboxflat", "S: StyleBoxFlat"], ["nineslice", "9: 9-slice atlas"],
             ["whole", "W: ship whole"], ["drop", "D: drop"]];
function frameHtml(fr, idx) {
  var id = "frame:" + fr.id, p = picks[id] || {}, st = p.status || "";
  var cls = "row frow" + (st === "chosen" ? " done" : st === "deferred" ? " defer" : "") +
            (idx === focus ? " focus" : "");
  var h = '<div class="' + cls + '" id="row_' + esc(id) + '" data-id="' + esc(id) +
    '" data-idx="' + idx + '">';
  h += '<div class="rhead"><span class="rid">' + esc(fr.id) + '</span>' +
    '<span class="badge">' + fr.cands.length + ' files, ' + fr.kb + ' KB</span>';
  for (var t = 0; t < TREAT.length; t++)
    h += '<button class="tbtn' + (p.treatment === TREAT[t][0] ? ' on' : '') +
      '" data-treat="' + TREAT[t][0] + '" data-fid="' + esc(id) + '">' +
      TREAT[t][1] + '</button>';
  h += '</div><div class="cards">';
  for (var i = 0; i < fr.cands.length; i++)
    h += cardHtml(fr.cands[i], i, p.src === fr.cands[i].rel, 0);
  h += '</div>' + noteBox(id) + '</div>';
  return h;
}

// ---- filtering ------------------------------------------------------------
function visibleClusters() {
  var d = document.getElementById("dest").value, n = document.getElementById("ncand").value;
  var q = document.getElementById("q").value.toLowerCase();
  return DATA.clusters.filter(function (cl) {
    var st = stateOf("slot:" + cl.id);
    if (filter === "open" && st === "chosen") return false;
    if (filter === "done" && st !== "chosen") return false;
    if (d && cl.dest !== d) return false;
    if (n && String(cl.cands.length) !== n) return false;
    if (q && cl.stem.toLowerCase().indexOf(q) < 0) return false;
    return true;
  });
}
function visibleFrames() {
  return DATA.frames.filter(function (fr) {
    var st = stateOf("frame:" + fr.id);
    if (filter === "open" && st === "chosen") return false;
    if (filter === "done" && st !== "chosen") return false;
    return true;
  });
}

function render() {
  var fr = visibleFrames(), cl = visibleClusters();
  order = fr.map(function (f) { return "frame:" + f.id; })
            .concat(cl.map(function (c) { return "slot:" + c.id; }));
  if (focus >= order.length) focus = Math.max(0, order.length - 1);
  var fh = "", i;
  for (i = 0; i < fr.length; i++) fh += frameHtml(fr[i], i);
  document.getElementById("frames").innerHTML = fh ||
    '<div class="sub" style="margin:0 16px">all frame roles decided.</div>';
  var ch = "";
  for (i = 0; i < cl.length; i++) ch += clusterHtml(cl[i], fr.length + i);
  document.getElementById("clusters").innerHTML = ch ||
    '<div class="sub" style="margin:0 16px">nothing left in this view.</div>';
  var nd = 0, nf = 0;
  DATA.clusters.forEach(function (c) { if (stateOf("slot:" + c.id) === "chosen") nd++; });
  DATA.frames.forEach(function (f) { if (stateOf("frame:" + f.id) === "chosen") nf++; });
  document.getElementById("counts").innerHTML =
    "slots " + nd + "/" + DATA.clusters.length + " decided &middot; frame roles " + nf + "/" +
    DATA.frames.length + " decided &middot; showing " + order.length +
    " &middot; source: " + DATA.stats.state_entries + " verdicts (READ-ONLY), " +
    DATA.stats.promotable_files + " promotable files &middot; built " + DATA.built;
}

function scrollFocus() {
  var el = document.getElementById("row_" + order[focus]);
  if (el) el.scrollIntoView({ block: "center" });
}

// ---- mutations ------------------------------------------------------------
function setPick(id, rel) {
  var p = picks[id] || {};
  p.src = rel; p.updated_at = now();
  // A frame role is only DECIDED once a treatment is chosen -- nominating a
  // source master is half the answer. Marking it chosen here would export an
  // entry apply_slot_picks.py must reject, which is a footgun, so don't.
  p.status = (id.indexOf("frame:") === 0 && !p.treatment) ? "" : "chosen";
  picks[id] = p; save();
}
function setTreat(id, t) {
  var p = picks[id] || {};
  p.treatment = t; p.status = "chosen"; p.updated_at = now();
  picks[id] = p; save();
}
function defer(id) {
  var p = picks[id] || {}; p.status = "deferred"; p.updated_at = now(); picks[id] = p; save();
}
function reopen(id) {
  var p = picks[id]; if (!p) return;
  delete p.src; delete p.treatment; p.status = ""; p.updated_at = now();
  if (!p.note) delete picks[id]; save();
}

document.addEventListener("click", function (ev) {
  var b = ev.target.closest("button[data-treat]");
  if (b) { setTreat(b.dataset.fid, b.dataset.treat); render(); return; }
  var c = ev.target.closest(".card");
  if (c) {
    var row = c.closest(".row");
    if (ev.shiftKey) {  // shift-click = inspect at natural size
      document.getElementById("modalimg").src = c.querySelector("img.full").src;
      document.getElementById("modal").style.display = "flex"; return;
    }
    focus = parseInt(row.dataset.idx, 10);
    setPick(row.dataset.id, c.dataset.rel); render(); return;
  }
  if (ev.target.id === "modal" || ev.target.id === "modalimg") {
    document.getElementById("modal").style.display = "none";
  }
});
document.addEventListener("input", function (ev) {
  var n = ev.target.dataset && ev.target.dataset.note;
  if (!n) return;
  var p = picks[n] || {}; p.note = ev.target.value; p.updated_at = now();
  if (!p.status) p.status = "";
  picks[n] = p; save();
});

document.addEventListener("keydown", function (ev) {
  if (ev.target.tagName === "INPUT" || ev.target.tagName === "SELECT") {
    if (ev.key === "Escape") ev.target.blur();
    return;
  }
  var id = order[focus], k = ev.key;
  if (k === "j") { focus = Math.min(order.length - 1, focus + 1); render(); scrollFocus(); }
  else if (k === "k") { focus = Math.max(0, focus - 1); render(); scrollFocus(); }
  else if (k >= "1" && k <= "9" && id && id.indexOf("slot:") === 0) {
    var cl = DATA.clusters.filter(function (c) { return "slot:" + c.id === id; })[0];
    var i = parseInt(k, 10) - 1;
    if (cl && cl.cands[i]) { setPick(id, cl.cands[i].rel); render(); }
  } else if (id && id.indexOf("frame:") === 0 &&
             (k === "s" || k === "9" || k === "w" || k === "d")) {
    setTreat(id, { s: "styleboxflat", "9": "nineslice", w: "whole", d: "drop" }[k]);
    render();
  } else if (k === "n") {
    ev.preventDefault();
    var el = document.querySelector('#row_' + CSS.escape(id) + ' .note-in');
    if (el) el.focus();
  } else if (k === "x") { defer(id); render(); }
  else if (k === "u") { reopen(id); render(); }
  else if (k === "f") {
    var im = document.querySelector('#row_' + CSS.escape(id) + ' img.full');
    if (im) { document.getElementById("modalimg").src = im.src;
              document.getElementById("modal").style.display = "flex"; }
  } else if (k === "E" || (k === "e" && !ev.ctrlKey)) { doExport(); }
  else if (k === "Escape") { document.getElementById("modal").style.display = "none"; }
});

// ---- batch apply ----------------------------------------------------------
// Pip's walk-cycle-frames complaint: when the variants are near-identical,
// picking them one at a time is toil, not taste. Scope is always the VISIBLE
// UNDECIDED set so the blast radius is whatever the filters say it is, and the
// count is confirmed before anything is written.
function batchApply(v) {
  var cl = visibleClusters().filter(function (c) {
    return stateOf("slot:" + c.id) !== "chosen"; });
  var hits = [];
  cl.forEach(function (c) {
    var pick = null;
    if (v === "hi") pick = c.cands[c.cands.length - 1];
    // "v1*" is the implicit-v1 label (v1 files carry no _v1_ marker at all in
    // this naming convention), so match on the number, not the label.
    else c.cands.forEach(function (x) {
      if (x.variant.replace("*", "") === "v" + v) pick = x; });
    if (pick) hits.push([c, pick]);
  });
  if (!hits.length) { toast("no visible undecided cluster has that variant"); return; }
  var label = v === "hi" ? "the highest variant" : "v" + v;
  if (!confirm("Pin " + label + " for " + hits.length + " visible undecided slot(s)?\n" +
               "(" + (cl.length - hits.length) + " visible cluster(s) have no " + label +
               " and are left alone. Reversible: press u on any row.)")) return;
  hits.forEach(function (h) { setPick("slot:" + h[0].id, h[1].rel); });
  render(); toast("pinned " + hits.length);
}

// ---- export ---------------------------------------------------------------
function doExport() {
  var out = {};
  Object.keys(picks).forEach(function (k) {
    var p = picks[k];
    if (!p) return;
    if (!p.src && !p.treatment && !p.note && !p.status) return;
    out[k] = { src: p.src || "", treatment: p.treatment || "",
               status: p.status || "", note: p.note || "",
               updated_at: p.updated_at || now() };
  });
  var n = Object.keys(out).length;
  if (!n) { toast("nothing to export yet"); return; }
  var blob = new Blob([JSON.stringify(out, null, 2)], { type: "application/json" });
  var a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "slot_picks_export_" + new Date().toISOString().replace(/[:.]/g, "-") + ".json";
  document.body.appendChild(a); a.click(); a.remove();
  sset(LSE, new Date().toISOString());
  showLastExport();
  toast("exported " + n + " decision(s)");
}
function showLastExport() {
  var t = sget(LSE);
  document.getElementById("lastexp").innerHTML =
    (STORE_OK ? "" : "<br><b>[!] this browser refuses localStorage here -- picks are held " +
                     "IN MEMORY ONLY. Do not close the tab before pressing E.</b>") +
    (t ? "<br>last export: <b>" + esc(t) + "</b>"
       : "<br><b>never exported from this browser yet.</b>");
}

// ---- wiring ---------------------------------------------------------------
(function () {
  var dests = {}, ns = {};
  DATA.clusters.forEach(function (c) { dests[c.dest] = 1; ns[c.cands.length] = 1; });
  var d = document.getElementById("dest");
  d.innerHTML = '<option value="">all destinations</option>' +
    Object.keys(dests).sort().map(function (x) {
      return '<option value="' + esc(x) + '">' + esc(x) + '</option>'; }).join("");
  var n = document.getElementById("ncand");
  n.innerHTML = '<option value="">any count</option>' +
    Object.keys(ns).sort().map(function (x) {
      return '<option value="' + x + '">' + x + ' candidates</option>'; }).join("");
  ["dest", "ncand", "q"].forEach(function (i) {
    document.getElementById(i).addEventListener("input", function () { focus = 0; render(); }); });
  function fbtn(id, val) {
    document.getElementById(id).addEventListener("click", function () {
      filter = val; focus = 0;
      ["f-open", "f-done", "f-all"].forEach(function (x) {
        document.getElementById(x).classList.remove("on"); });
      document.getElementById(id).classList.add("on"); render(); });
  }
  fbtn("f-open", "open"); fbtn("f-done", "done"); fbtn("f-all", "all");
  document.getElementById("f-open").classList.add("on");
  [["z1", 1], ["z2", 2], ["z4", 4]].forEach(function (z) {
    document.getElementById(z[0]).addEventListener("click", function () {
      zoom = z[1];
      ["z1", "z2", "z4"].forEach(function (x) {
        document.getElementById(x).classList.remove("on"); });
      document.getElementById(z[0]).classList.add("on"); render(); }); });
  document.getElementById("z1").classList.add("on");
  Array.prototype.forEach.call(document.querySelectorAll(".bapply"), function (b) {
    b.addEventListener("click", function () { batchApply(b.dataset.v); }); });
  document.getElementById("exp").addEventListener("click", doExport);
  showLastExport();
  render();
})();
</script>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--state", default=None, help="review_state.json (read-only)")
    ap.add_argument("--open", action="store_true", help="open the page when done")
    args = ap.parse_args(argv)

    t0 = time.time()
    clusters, frames, stats = slot_model.build_model(state_path=args.state)
    data = build_data(clusters, frames, stats)
    css_vars = " ".join("--%s:%s;" % (k, v) for k, v in sorted(review_style.PALETTE.items()))
    page = PAGE.replace("__VARS__", css_vars)
    page = page.replace("__CHECKER__", review_style.CHECKER)
    page = page.replace("__DATA__", json.dumps(data, ensure_ascii=True))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8", newline="\n")

    print("== slot picker ==")
    print(
        "read {state_entries} verdicts (READ-ONLY) -> {promotable_assets} promotable assets, "
        "{promotable_files} files, {mb} MB".format(
            mb=round(stats["promotable_bytes"] / 1e6, 1), **stats
        )
    )
    print(
        "  pool destinations exempt (no single winner): {pool_files_exempt} files".format(**stats)
    )
    print(
        "  frame roles:        {frame_roles} roles, {frame_files} files, {fmb} MB".format(
            fmb=round(stats["frame_bytes"] / 1e6, 1), **stats
        )
    )
    print(
        "  slot-competing:     {slot_files} files -> {slot_roles} roles "
        "({alternates} alternates)".format(**stats)
    )
    print(
        "  CONTESTED CLUSTERS: {contested_clusters} (the working set), "
        "{contested_files} candidate files, {cmb} MB".format(
            cmb=round(stats["contested_bytes"] / 1e6, 1), **stats
        )
    )
    print("wrote %s (%.1f KB) in %.1fs" % (out, out.stat().st_size / 1024, time.time() - t0))
    print("open:  %s" % out.resolve())
    print("then:  python tools/art_review/apply_slot_picks.py <downloaded export>")
    if args.open:
        try:
            subprocess.Popen(["cmd", "/c", "start", "", str(out.resolve())], shell=False)
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
