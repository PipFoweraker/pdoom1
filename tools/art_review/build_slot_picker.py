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
                "crop": list(f.crop),
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
                "square": cl.draw_square,
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
/* overflow:hidden is a BACKSTOP, not the fix. The fix is that every card is
   sized to its own game-size render (cardHtml sets an inline width). Without
   both, a 408px hero render inside a 186px card spilled ~111px out of each
   side of a centring flexbox -- three of them overlapping read as a "hover
   overlay" covering the header and running off the left edge of the page.
   Reported by Pip 2026-08-06; the bug had nothing to do with hover. */
.card { border:1px solid var(--line); border-radius:4px; background:var(--bg); padding:6px;
        width:186px; cursor:pointer; overflow:hidden; }
.card:hover { border-color:var(--amber); }
.card.win { border-color:var(--green); box-shadow:0 0 0 1px var(--green) inset; }
/* The gamebox is a FLAT DARK tile on purpose -- it stands in for the ground the
   action bar actually draws these on. No checkerboard here; checkerboard is for
   judging alpha, which is the full-size preview's job. */
.gamebox { background:#0b0a09; border:1px dashed var(--line); display:flex; align-items:center;
        justify-content:center; padding:8px; margin-bottom:5px; min-height:86px;
        overflow:hidden; }
.gamebox img { display:block; image-rendering:auto; max-width:100%; }
.boxcap { color:var(--dim); font-size:10px; text-align:center; margin:-3px 0 5px; }
/* Frame roles: the decision is about a 12px corner bracket, so show the CORNER,
   cropped and magnified, not the 512px picture it sits in. */
.crop { background-repeat:no-repeat; background-color:#0b0a09;
        border:1px dashed var(--line); }
.cropmini { background-repeat:no-repeat; background-color:#0b0a09;
        border:1px solid var(--line); }
.croprow { display:flex; gap:8px; align-items:flex-end; margin-bottom:4px; }
/* Two-step frame decision. Step 2 is ABSENT, not disabled, when step 1 makes
   it meaningless -- see frameHtml. */
.step { padding:7px 10px 3px; font-size:12px; color:var(--fg); }
.stepn { font-family:Consolas,monospace; font-size:10.5px; color:var(--bg);
         background:var(--amber); border-radius:3px; padding:1px 6px; margin-right:7px; }
.ok { color:var(--green); }
.need { color:var(--amber2); }
.treats { display:flex; gap:8px; flex-wrap:wrap; padding:0 10px 4px; }
.tbtn { text-align:left; padding:5px 9px; max-width:260px; }
.gloss { display:block; color:var(--dim); font-size:10.5px; font-weight:400; margin-top:2px; }
button.on .gloss { color:#12200e; }
.noscnd { padding:2px 10px 9px; color:var(--dim); font-size:11.5px; }
.cards.dimmed { opacity:.35; filter:saturate(.4); }
.cards.dimmed .card { cursor:default; }
.link { background:none; border:none; color:var(--amber); text-decoration:underline;
        padding:0 2px; cursor:pointer; font-size:11.5px; }
.explain { background:var(--bg2); border:1px solid var(--line); border-radius:4px;
        margin:6px 16px 10px; padding:9px 12px; font-size:12px; color:var(--fg); }
.explain h3 { font-size:12px; margin:0 0 5px; color:var(--amber); }
.explain pre { font-family:Consolas,monospace; font-size:11px; color:var(--dim);
        margin:6px 0; line-height:1.25; }
.explain dt { color:var(--amber2); font-weight:600; margin-top:6px; }
.explain dd { margin:1px 0 0 0; color:var(--dim); }
.qline { margin:0 16px 8px; padding:6px 10px; border-left:3px solid var(--amber);
        background:var(--bg2); font-size:12.5px; }
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
/* ---- lightbox: the MAGNIFIER surface ----------------------------------
   Deliberately a different surface from the inline "as-drawn size" control.
   Inline zoom answers "what does this look like at the size the game draws
   it" -- growing it past that would answer a different question AND re-break
   the card-overflow bug. Magnification for judging lives here, where a fixed
   full-screen overlay cannot overlap anything. */
#lb { position:fixed; inset:0; background:#000e; z-index:90; display:none;
      flex-direction:column; }
#lbbar { display:flex; gap:10px; align-items:center; flex-wrap:wrap;
         padding:8px 12px; background:var(--bg); border-bottom:1px solid var(--line);
         font-size:12px; }
#lbstage { flex:1; overflow:auto; background:__CHECKER__; position:relative;
           cursor:grab; }
#lbstage.drag { cursor:grabbing; }
#lbwrap { min-width:100%; min-height:100%; display:flex; align-items:center;
          justify-content:center; }
#lbimg { display:block; image-rendering:auto; }
#lbimg.fit { max-width:98%; max-height:98%; }
.lbname { font-family:Consolas,monospace; color:var(--fg); }
.lbdim { color:var(--dim); }
#lb .on { background:var(--green); border-color:var(--green); color:#0f1a0c; }
.zbtn { position:absolute; top:4px; right:4px; z-index:5; padding:1px 6px;
        font-size:11px; opacity:.55; }
.zbtn:hover { opacity:1; }
.gwrap { position:relative; }
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
    <span class="sub">| filters (SECTION 2 only):</span>
    <select id="dest"></select>
    <select id="ncand"></select>
    <input type="text" id="q" placeholder="filter by name..." size="18">
    <span class="sub">| as-drawn size (section 2; not a magnifier):</span>
    <button id="z1">1x</button><button id="z2">2x</button><button id="z4">4x</button>
    <span class="sub">| batch-pin the clusters currently visible:</span>
    <button class="bapply" data-v="1">all v1</button>
    <button class="bapply" data-v="2">all v2</button>
    <button class="bapply" data-v="3">all v3</button>
    <button class="bapply" data-v="4">all v4</button>
    <button class="bapply" data-v="hi">all highest</button>
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

<h2>1 &mdash; FRAME ROLES (15)</h2>
<div class="qline"><b>The question here:</b> HOW should this thing be drawn at all &mdash;
  in code, or from a piece of this painted art? <span class="sub">Nothing is being compared
  for beauty. These 15 roles are UI source material: 512x512 pictures of a bracket that ends
  up about 12px on screen. All four answers are legitimate.</span></div>

<div class="explain">
  <h3>What the four answers actually mean</h3>
  <p style="margin:0 0 4px">You already have a feel for StyleBoxFlat, so the others are
  described against it.</p>
  <dl style="margin:0">
    <dt>draw it in code (StyleBoxFlat) &mdash; ships 0 bytes</dt>
    <dd>The theme says "1px amber border, 3px corner radius" and the engine draws it at any
      size, on any screen, forever. It CANNOT have grain, brush texture, ornament or a painted
      gradient. Right answer for a plain panel or a plain button.</dd>
    <dt>crop the corners out (9-slice) &mdash; ships kilobytes, keeps the painted look</dt>
    <dd>We cut NINE regions out of the master &mdash; 4 corners, 4 edges, 1 middle &mdash; into
      one small shared atlas. The engine then draws the corners at fixed size and STRETCHES the
      edge strips to whatever length the box needs, so one small image frames a box of any
      shape. That is why only the corner and a sliver of edge are worth keeping: the middle of
      the master is never drawn.
      <pre>+-----+---------+-----+
|  1  |    2    |  3  |   1 3 7 9  corners, drawn at fixed size, never stretched
+-----+---------+-----+   2 8      top/bottom edge, STRETCHED horizontally
|  4  |    5    |  6  |   4 6      left/right edge, STRETCHED vertically
+-----+---------+-----+   5        middle -- usually transparent or a flat fill
|  7  |    8    |  9  |
+-----+---------+-----+   all 15 roles together: well under 0.3 MB</pre>
      Concretely: <b>frame_panel_ornate</b> has painted ornament in its corners &mdash; that is
      exactly what 9-slice preserves and StyleBoxFlat cannot. <b>frame_panel_plain</b> probably
      has nothing a border colour could not reproduce, so 9-slice would be paying bytes for
      nothing.</dd>
    <dt>ship the whole image &mdash; ships the full 512px picture</dt>
    <dd>Only right when the whole picture IS the thing on screen. The three CRT bezels are
      genuine full-screen overlays, so they qualify. For a corner bracket this means shipping
      ~250 KB to draw 12 px.</dd>
    <dt>don't use it &mdash; ships nothing, changes nothing on disk</dt>
    <dd>The role goes away. The masters stay in Library; no manifest entry names them. Nothing
      is deleted.</dd>
  </dl>
</div>
<div id="frames"></div>

<h2>2 &mdash; CONTESTED SLOTS (136)</h2>
<div class="qline"><b>The question here:</b> WHICH of these variants ships in this slot?
  <span class="sub">Different question from section 1. Every candidate is already approved
  art; the game just has one slot and several of them. Pick one. The losers stay Library
  assets that no manifest entry names &mdash; nothing is done TO them, no file moves, and
  you can change your mind (<kbd>u</kbd>) at any time.</span></div>
<div id="clusters"></div>

<div id="lb">
  <div id="lbbar">
    <button id="lbclose">[ESC] close</button>
    <button id="lbprev">&lt; prev</button>
    <span class="lbname" id="lblabel"></span>
    <button id="lbnext">next &gt;</button>
    <span class="sub">|</span>
    <button class="lbz" data-s="fit">fit</button>
    <button class="lbz" data-s="1">100%</button>
    <button class="lbz" data-s="2">200%</button>
    <button class="lbz" data-s="4">400%</button>
    <span class="lbdim" id="lbdims"></span>
    <span class="sub">|</span>
    <button id="lbpin">[ENTER] pin this one</button>
    <span class="lbdim">wheel = zoom &middot; drag = pan &middot;
      <kbd>[</kbd>/<kbd>]</kbd> step candidates</span>
  </div>
  <div id="lbstage"><div id="lbwrap"><img id="lbimg" class="fit" src=""></div></div>
</div>
<div id="toast"></div>
<div id="help"><span id="helptxt"></span></div>

<script>
var DATA = __DATA__;
// v2: the key was bumped on 2026-08-06 so the first session's picks (made
// against a page whose frame section was misleading) are discarded rather than
// silently carried forward. Pip's ruling: "none of that work meant anything
// because I was clicking wrong. Full discard, rebuild tool."
var LS = "pdoom1_slot_picks_v2", LSE = "pdoom1_slot_picks_exported";
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
var filter = "open", zoom = 1, focus = 0, order = [], showMasters = {};

function save() { sset(LS, JSON.stringify(picks)); }
function now() { return new Date().toISOString(); }
function esc(s) { return String(s).replace(/[&<>"]/g, function (c) {
  return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]; }); }
function toast(m) { var t = document.getElementById("toast"); t.textContent = m;
  t.style.display = "block"; clearTimeout(t._h); t._h = setTimeout(function () {
  t.style.display = "none"; }, 1400); }

// ---- render helpers -------------------------------------------------------
var CARD_MIN = 186, RENDER_MAX = 760;   // never let a card outgrow the page

function renderWidth(cl) {
  // The width the game-size preview will actually occupy. Everything that
  // sizes a card derives from THIS, so a card can never be narrower than its
  // own contents. draw==0 means "drawn at native size" -- there is nothing to
  // shrink, so cap for layout instead of inventing a game size.
  if (!cl || !cl.draw) return 160;
  return Math.min(cl.draw * zoom, RENDER_MAX);
}
function gameImg(c, cl) {
  var w = renderWidth(cl);
  if (!cl || !cl.draw) {
    return '<img loading="lazy" src="' + c.href + '" style="max-width:160px;max-height:110px">';
  }
  // square: the consumer pins BOTH dimensions (a 70x70 tile).
  // otherwise: it pins WIDTH and lets height run proportional, so forcing a
  // square here would squash 768x512 hero art and lie about what ships.
  var st = cl.square ? 'width:' + w + 'px;height:' + w + 'px'
                     : 'width:' + w + 'px;height:auto';
  return '<img loading="lazy" src="' + c.href + '" style="' + st + '">';
}
function cardWidth(cl) {
  return Math.max(CARD_MIN, renderWidth(cl) + 16);
}
function cardHtml(c, i, chosen, cl) {
  var w = cardWidth(cl);
  var capped = cl && cl.draw && (cl.draw * zoom > RENDER_MAX);
  return '<div class="card' + (chosen ? ' win' : '') + '" data-rel="' + esc(c.rel) +
    '" style="width:' + w + 'px">' +
    '<div class="gwrap"><div class="gamebox">' + gameImg(c, cl) + '</div>' +
    '<button class="zbtn" data-zoom="' + esc(c.rel) + '" title="magnify this candidate ' +
    '(full screen, pan and zoom)">[+] zoom</button></div>' +
    (cl && cl.draw
      ? '<div class="boxcap">as the game draws it (' + cl.draw + 'px' +
        (zoom > 1 ? ' at ' + zoom + 'x' : '') + ')' +
        (capped ? ' &mdash; capped; use [+] zoom' : '') + '</div>'
      : '<div class="boxcap">drawn at native size &mdash; use [+] zoom to judge it</div>') +
    '<img class="full" loading="lazy" src="' + c.href + '">' +
    '<div class="cmeta"><span class="pickno">' + (i + 1) + '</span>' +
    '<span class="cvar">' + esc(c.variant) + '</span> &middot; ' + c.kb + ' KB' +
    (c.px ? ' &middot; ' + c.px[0] + 'x' + c.px[1] : '') + '<br>' + esc(c.name) + '</div>' +
    (c.note ? '<div class="cnote">review note: ' + esc(c.note) + '</div>' : '') +
    '</div>';
}

// ---- frame cards: show the REGION being decided, not the picture around it --
function cropStyle(c, crop, boxW, boxH) {
  // CSS background crop. background-size scales the master so the crop fills
  // the box; background-position's percentage is relative to (image - box),
  // hence x/(1-w).
  var x = crop[0], y = crop[1], w = crop[2], h = crop[3];
  var px = w >= 1 ? 0 : (x / (1 - w)) * 100;
  var py = h >= 1 ? 0 : (y / (1 - h)) * 100;
  return "background-image:url('" + c.href + "');" +
    "background-size:" + (100 / w) + "% " + (100 / h) + "%;" +
    "background-position:" + px.toFixed(2) + "% " + py.toFixed(2) + "%;" +
    "width:" + Math.round(boxW) + "px;height:" + Math.round(boxH) + "px;";
}
function frameCardHtml(c, i, chosen, crop, inert) {
  var w = crop[2], h = crop[3];
  var big = 168, bw = w >= h ? big : big * (w / h), bh = h >= w ? big : big * (h / w);
  var mini = 16, mw = w >= h ? mini : mini * (w / h), mh = h >= w ? mini : mini * (h / w);
  var whole = (w >= 1 && h >= 1);
  return '<div class="card' + (chosen ? ' win' : '') + (inert ? ' inert' : '') +
    '" data-rel="' + esc(c.rel) + '"' + (inert ? ' data-inert="1"' : '') +
    ' style="width:' + Math.max(CARD_MIN, bw + 16) + 'px">' +
    '<div class="croprow">' +
      '<div class="gwrap"><div class="crop" style="' + cropStyle(c, crop, bw, bh) + '"></div>' +
      '<button class="zbtn" data-zoom="' + esc(c.rel) + '" title="magnify the whole master">' +
      '[+] zoom</button>' +
      '<div class="boxcap">' + (whole ? 'whole overlay' : 'the region in question, magnified') +
      '</div></div>' +
      (whole ? '' :
        '<div><div class="cropmini" style="' + cropStyle(c, crop, mw, mh) + '"></div>' +
        '<div class="boxcap">~16px</div></div>') +
    '</div>' +
    '<img class="full" loading="lazy" src="' + c.href + '">' +
    '<div class="boxcap">the whole master (mostly not the subject)</div>' +
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
    h += cardHtml(cl.cands[i], i, p.src === cl.cands[i].rel, cl);
  h += '</div>' + noteBox("slot:" + cl.id) + '</div>';
  return h;
}

// Plain language at the point of decision. Pip clicked 11 of these before the
// paragraph above the section told him what they meant -- so the paragraph is
// not where the explanation belongs.
// Keys are LETTERS, not digits: the old "9 = 9-slice" collided with 1..9
// source selection on the very same row, which is the two-controls-one-key
// version of the bug this section was rebuilt to remove.
var TREAT = [
  ["styleboxflat", "[S] draw it in code", "StyleBoxFlat border. Ships 0 bytes. No texture."],
  ["nineslice", "[C] crop the corners out", "9-slice atlas. Keeps the paint. Ships KB, not MB."],
  ["whole", "[W] ship the whole image", "the full 512px picture. Only for full-screen art."],
  ["drop", "[D] don't use it", "nothing ships; masters stay in Library, untouched."]];
var TREAT_KEY = { s: "styleboxflat", c: "nineslice", w: "whole", d: "drop" };
function frameHtml(fr, idx) {
  var id = "frame:" + fr.id, p = picks[id] || {}, st = p.status || "";
  var cls = "row frow" + (st === "chosen" ? " done" : st === "deferred" ? " defer" : "") +
            (idx === focus ? " focus" : "");
  var h = '<div class="' + cls + '" id="row_' + esc(id) + '" data-id="' + esc(id) +
    '" data-idx="' + idx + '">';
  h += '<div class="rhead"><span class="rid">' + esc(fr.id) + '</span>' +
    '<span class="badge">' + fr.cands.length + ' files, ' + fr.kb + ' KB</span>' +
    (st ? '<span class="badge">' + st.toUpperCase() + '</span>' : '') + '</div>';

  // STEP 1 -- always live. One question, four answers.
  h += '<div class="step"><span class="stepn">STEP 1</span> how should this be drawn?</div>';
  h += '<div class="treats">';
  for (var t = 0; t < TREAT.length; t++)
    h += '<button class="tbtn' + (p.treatment === TREAT[t][0] ? ' on' : '') +
      '" data-treat="' + TREAT[t][0] + '" data-fid="' + esc(id) + '">' +
      '<b>' + TREAT[t][1] + '</b><span class="gloss">' + TREAT[t][2] + '</span></button>';
  h += '</div>';

  // STEP 2 -- EXISTS ONLY when the answer to step 1 makes a source matter.
  // Not greyed, not disabled: absent. A control that accepts a click and
  // discards it is the silent-wrongness pattern wearing a UI (Pip, 2026-08-06:
  // "I don't understand how you want me to combine those s 9 w d things with
  // clicking on the pictures?").
  var needsSrc = (p.treatment === "nineslice" || p.treatment === "whole");
  if (needsSrc) {
    h += '<div class="step"><span class="stepn">STEP 2</span> ' +
      (p.treatment === "nineslice" ? 'which master do we crop the atlas from?'
                                   : 'which master ships?') +
      (p.src ? ' <span class="ok">[OK] chosen</span>'
             : ' <span class="need">[!] needed -- click one</span>') + '</div>';
    h += '<div class="cards">';
    for (var i = 0; i < fr.cands.length; i++)
      h += frameCardHtml(fr.cands[i], i, p.src === fr.cands[i].rel, fr.crop);
    h += '</div>';
  } else if (p.treatment) {
    h += '<div class="noscnd">' + (p.treatment === "styleboxflat"
      ? 'No source image is used -- the border is authored in the theme as a StyleBoxFlat, ' +
        'so there is nothing to pick and these masters ship no bytes.'
      : 'Nothing ships for this role. The masters stay in Library; no manifest entry names them.'
      ) + ' <button class="link" data-show="' + esc(id) + '">show the masters anyway</button>' +
      '</div>';
    if (showMasters[id]) {
      h += '<div class="cards dimmed">';
      for (var j = 0; j < fr.cands.length; j++)
        h += frameCardHtml(fr.cands[j], j, false, fr.crop, true);
      h += '</div>';
    }
  } else {
    h += '<div class="noscnd">Answer step 1 and the rest of the question appears.</div>';
    h += '<div class="cards dimmed">';
    for (var k = 0; k < fr.cands.length; k++)
      h += frameCardHtml(fr.cands[k], k, false, fr.crop, true);
    h += '</div>';
  }
  h += noteBox(id) + '</div>';
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
  syncConditionalControls();
  syncHelp();
}

function scrollFocus() {
  var el = document.getElementById("row_" + order[focus]);
  if (el && el.scrollIntoView) el.scrollIntoView({ block: "center" });
}

// ---- the magnifier ---------------------------------------------------------
// Measured 2026-08-06, before this existed: inline zoom took a hero from 408px
// to 760px and then stopped (2x and 4x identical, because of the anti-overlap
// clamp), and for the 16 NATIVE-SIZE clusters -- 1024px texture masters,
// 1536px event art -- it did nothing at all at any level, because those have
// no measured draw size to multiply. So "cannot zoom the big ones" was only
// partly the clamp; mostly it was that the biggest art was pinned at a 160px
// preview by design. Magnification is now its own surface.
var lb = { list: [], i: 0, scale: "fit", rowId: "", open: false };

function lbCandsFor(rowId) {
  if (rowId.indexOf("slot:") === 0) {
    var cl = DATA.clusters.filter(function (c) { return "slot:" + c.id === rowId; })[0];
    return cl ? cl.cands : [];
  }
  var fr = DATA.frames.filter(function (f) { return "frame:" + f.id === rowId; })[0];
  return fr ? fr.cands : [];
}
function lbOpen(rowId, rel) {
  var list = lbCandsFor(rowId);
  if (!list.length) return;
  var i = 0;
  for (var n = 0; n < list.length; n++) if (list[n].rel === rel) i = n;
  lb = { list: list, i: i, scale: "fit", rowId: rowId, open: true };
  document.getElementById("lb").style.display = "flex";
  lbPaint();
}
function lbClose() {
  lb.open = false;
  document.getElementById("lb").style.display = "none";
}
function lbPaint() {
  var c = lb.list[lb.i];
  if (!c) return;
  var img = document.getElementById("lbimg");
  img.src = c.href;
  if (lb.scale === "fit") { img.className = "fit"; img.style.width = ""; }
  else {
    img.className = "";
    // Scale relative to the master's own pixels, so 100% means one image pixel
    // per screen pixel and 400% is a real magnification of a 512px icon.
    img.style.width = c.px ? (c.px[0] * lb.scale) + "px" : (512 * lb.scale) + "px";
  }
  var picked = (picks[lb.rowId] || {}).src === c.rel;
  document.getElementById("lblabel").innerHTML =
    esc(c.variant) + " &mdash; " + esc(c.name) + "  (" + (lb.i + 1) + "/" + lb.list.length + ")" +
    (picked ? ' <span class="ok">[OK] pinned</span>' : "");
  document.getElementById("lbdims").textContent =
    (c.px ? c.px[0] + "x" + c.px[1] + " master" : "") + " " + c.kb + " KB";
  Array.prototype.forEach.call(document.querySelectorAll(".lbz"), function (b) {
    b.classList.toggle("on", String(lb.scale) === b.dataset.s);
  });
  // A frame role under a treatment that consumes no source has nothing to pin,
  // so the button says so instead of silently doing nothing.
  var p = picks[lb.rowId] || {}, isFrame = lb.rowId.indexOf("frame:") === 0;
  var canPin = !isFrame || p.treatment === "nineslice" || p.treatment === "whole";
  var pin = document.getElementById("lbpin");
  pin.disabled = !canPin;
  pin.style.opacity = canPin ? "1" : ".35";
  pin.title = canPin ? "" : "this frame treatment uses no source image";
}
function lbStep(d) {
  if (!lb.open || !lb.list.length) return;
  lb.i = (lb.i + d + lb.list.length) % lb.list.length;
  lbPaint();
}
function lbSetScale(s) {
  lb.scale = (s === "fit") ? "fit" : parseFloat(s);
  lbPaint();
}
function lbWire() {
  var stage = document.getElementById("lbstage");
  stage.addEventListener("wheel", function (ev) {
    if (!lb.open) return;
    ev.preventDefault();
    var cur = (lb.scale === "fit") ? 1 : lb.scale;
    lbSetScale(ev.deltaY < 0 ? Math.min(8, cur * 1.25) : Math.max(0.25, cur / 1.25));
  }, { passive: false });
  var down = false, sx = 0, sy = 0, ol = 0, ot = 0;
  stage.addEventListener("mousedown", function (ev) {
    down = true; sx = ev.clientX; sy = ev.clientY;
    ol = stage.scrollLeft; ot = stage.scrollTop;
    stage.classList.add("drag"); ev.preventDefault();
  });
  document.addEventListener("mousemove", function (ev) {
    if (!down) return;
    stage.scrollLeft = ol - (ev.clientX - sx);
    stage.scrollTop = ot - (ev.clientY - sy);
  });
  document.addEventListener("mouseup", function () {
    down = false; stage.classList.remove("drag");
  });
}
function lbPin() {
  var c = lb.list[lb.i];
  if (!c) return;
  var p = picks[lb.rowId] || {}, isFrame = lb.rowId.indexOf("frame:") === 0;
  if (isFrame && p.treatment !== "nineslice" && p.treatment !== "whole") {
    toast("this frame treatment uses no source image"); return;
  }
  setPick(lb.rowId, c.rel);
  lbPaint(); render();
  toast("pinned " + c.variant);
}

// ---- conditional controls, made visible -----------------------------------
// Same test the frame section had to pass, applied to the toolbar: no control
// may accept a click and quietly do nothing. Each batch button carries its own
// live hit count and disables itself at zero, so "all v4" cannot look
// available while matching no visible cluster.
function batchTargets(v) {
  return visibleClusters()
    .filter(function (c) { return stateOf("slot:" + c.id) !== "chosen"; })
    .map(function (c) {
      var pick = null;
      if (v === "hi") pick = c.cands[c.cands.length - 1];
      else c.cands.forEach(function (x) {
        if (x.variant.replace("*", "") === "v" + v) pick = x; });
      return pick ? [c, pick] : null;
    })
    .filter(Boolean);
}
function syncConditionalControls() {
  Array.prototype.forEach.call(document.querySelectorAll(".bapply"), function (b) {
    var n = batchTargets(b.dataset.v).length;
    b.textContent = (b.dataset.v === "hi" ? "all highest" : "all v" + b.dataset.v) + " (" + n + ")";
    b.disabled = (n === 0);
    b.style.opacity = n ? "1" : ".35";
    b.title = n ? ("pins " + n + " of the " + visibleClusters().length + " visible cluster(s)")
                : "no visible undecided cluster has that variant";
  });
  // The as-drawn control is NOT a magnifier and must not pretend to be one.
  // It only moves for clusters with a measured draw size, and it stops at
  // RENDER_MAX (the anti-overlap clamp). Both limits are stated on the control
  // itself, and both point at the magnifier instead of leaving a dead button.
  var vis = visibleClusters();
  var anyDraw = vis.some(function (c) { return !!c.draw; });
  [["z1", 1], ["z2", 2], ["z4", 4]].forEach(function (pair) {
    var e = document.getElementById(pair[0]);
    var capped = anyDraw && vis.every(function (c) {
      return !c.draw || c.draw * pair[1] > RENDER_MAX; });
    e.style.opacity = anyDraw ? "1" : ".35";
    e.textContent = pair[1] + "x" + (capped ? "*" : "");
    e.title = !anyDraw
      ? "nothing visible has a measured draw size -- use [+] zoom on a card to magnify"
      : capped
        ? "capped at " + RENDER_MAX + "px so cards cannot overlap -- use [+] zoom to magnify"
        : "show the art at the size the game draws it";
  });
}
function syncHelp() {
  var id = order[focus] || "", frame = id.indexOf("frame:") === 0;
  document.getElementById("helptxt").innerHTML =
    (frame
      ? '<b>frame role focused:</b> <kbd>s</kbd> draw in code &nbsp; <kbd>c</kbd> crop ' +
        'corners (9-slice) &nbsp; <kbd>w</kbd> ship whole &nbsp; <kbd>d</kbd> don\'t use ' +
        '&nbsp; <span class="sub">(then, and only then, <kbd>1</kbd>..<kbd>9</kbd> ' +
        'picks the source master &mdash; s and d need none)</span>'
      : '<b>slot focused:</b> <kbd>1</kbd>..<kbd>9</kbd> pin that candidate &nbsp; ' +
        '<span class="sub">(s/9/w/d do nothing here -- they are frame-role answers)</span>') +
    ' &nbsp;|&nbsp; <kbd>j</kbd>/<kbd>k</kbd> next/prev &nbsp; <kbd>n</kbd> note &nbsp; ' +
    '<kbd>x</kbd> defer &nbsp; <kbd>u</kbd> reopen &nbsp; <kbd>E</kbd> export' +
    ' &nbsp;|&nbsp; <b>MAGNIFY:</b> <kbd>f</kbd> or the <b>[+] zoom</b> button on any card ' +
    '&nbsp; <span class="sub">(then <kbd>[</kbd>/<kbd>]</kbd> to A/B the candidates full ' +
    'screen, wheel to zoom, drag to pan, <kbd>Enter</kbd> to pin the one you are looking ' +
    'at). The 1x/2x/4x control is as-drawn size, not a magnifier.</span>';
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
  p.treatment = t; p.updated_at = now();
  // "chosen" means the whole question is answered. 9-slice and ship-whole are
  // only half-answered until step 2 names a source, and a source picked under
  // a PREVIOUS treatment must not survive a switch to one that ignores it --
  // otherwise the record carries a source nobody chose for the treatment that
  // shipped. Clearing it is the honest move.
  if (t === "styleboxflat" || t === "drop") { delete p.src; p.status = "chosen"; }
  else { p.status = p.src ? "chosen" : ""; }
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
  var sh = ev.target.closest("button[data-show]");
  if (sh) { showMasters[sh.dataset.show] = !showMasters[sh.dataset.show]; render(); return; }
  var z = ev.target.closest("button[data-zoom]");
  if (z) { lbOpen(z.closest(".row").dataset.id, z.dataset.zoom); return; }
  var c = ev.target.closest(".card");
  if (c) {
    var row = c.closest(".row");
    if (ev.shiftKey) { lbOpen(row.dataset.id, c.dataset.rel); return; }
    // A card rendered as reference-only cannot be picked. It is shown dimmed
    // and it says why; accepting the click and dropping it would be exactly
    // the failure this restructure exists to remove.
    if (c.dataset.inert) { toast("this treatment uses no source image"); return; }
    focus = parseInt(row.dataset.idx, 10);
    setPick(row.dataset.id, c.dataset.rel); render(); return;
  }
  if (ev.target.id === "lbclose" || ev.target.id === "lbstage" || ev.target.id === "lbwrap") {
    lbClose(); return;
  }
  if (ev.target.id === "lbprev") { lbStep(-1); return; }
  if (ev.target.id === "lbnext") { lbStep(1); return; }
  if (ev.target.id === "lbpin") { lbPin(); return; }
  var lz = ev.target.closest(".lbz");
  if (lz) { lbSetScale(lz.dataset.s); return; }
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
  // The lightbox owns the keyboard while it is open. Letting the page's keys
  // fire underneath it would mean pressing "3" magnifies one candidate and
  // silently pins a different one.
  if (lb.open) {
    ev.preventDefault();
    if (k === "Escape" || k === "f") lbClose();
    else if (k === "[" || k === "ArrowLeft") lbStep(-1);
    else if (k === "]" || k === "ArrowRight") lbStep(1);
    else if (k === "0") lbSetScale("fit");
    else if (k === "+" || k === "=") lbSetScale(lb.scale === "fit" ? 1 :
                                                Math.min(8, lb.scale * 2));
    else if (k === "-") lbSetScale(lb.scale === "fit" ? 1 : Math.max(0.25, lb.scale / 2));
    else if (k === "Enter") lbPin();
    else if (k >= "1" && k <= "9") {
      var n = parseInt(k, 10) - 1;
      if (lb.list[n]) { lb.i = n; lbPaint(); }
    }
    return;
  }
  if (k === "j") { focus = Math.min(order.length - 1, focus + 1); render(); scrollFocus(); }
  else if (k === "k") { focus = Math.max(0, focus - 1); render(); scrollFocus(); }
  else if (k >= "1" && k <= "9" && id && id.indexOf("slot:") === 0) {
    var cl = DATA.clusters.filter(function (c) { return "slot:" + c.id === id; })[0];
    var i = parseInt(k, 10) - 1;
    if (cl && cl.cands[i]) { setPick(id, cl.cands[i].rel); render(); }
  } else if (k >= "1" && k <= "9" && id && id.indexOf("frame:") === 0) {
    // Digits select a SOURCE, and only exist as an answer once step 1 has made
    // a source relevant. Otherwise say so instead of silently ignoring it.
    var p = picks[id] || {};
    if (p.treatment !== "nineslice" && p.treatment !== "whole") {
      toast(p.treatment ? "this treatment uses no source image"
                        : "answer step 1 first (s / c / w / d)");
    } else {
      var fr = DATA.frames.filter(function (f) { return "frame:" + f.id === id; })[0];
      var j = parseInt(k, 10) - 1;
      if (fr && fr.cands[j]) { setPick(id, fr.cands[j].rel); render(); }
    }
  } else if (id && id.indexOf("frame:") === 0 && TREAT_KEY[k]) {
    setTreat(id, TREAT_KEY[k]);
    render();
  } else if (id && id.indexOf("slot:") === 0 && TREAT_KEY[k]) {
    toast("s / c / w / d are frame-role answers -- this is a slot; use 1..9");
  } else if (k === "n") {
    ev.preventDefault();
    var el = document.querySelector('#row_' + CSS.escape(id) + ' .note-in');
    if (el) el.focus();
  } else if (k === "x") { defer(id); render(); }
  else if (k === "u") { reopen(id); render(); }
  else if (k === "f") {
    // Open the candidate being judged -- the pinned one if there is one, else
    // the first. The old version always grabbed the row's FIRST full image, so
    // there was no way to full-size candidate 2, 3 or 4 from the keyboard.
    if (id) lbOpen(id, (picks[id] || {}).src || "");
  } else if (k === "E" || (k === "e" && !ev.ctrlKey)) { doExport(); }
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
  lbWire();
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
