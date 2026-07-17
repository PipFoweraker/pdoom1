#!/usr/bin/env python3
"""Build the P(Doom)1 style-review tool: a self-contained, single-file HTML page
from manifest.json + sweep_prompts.json + the committed PNGs.

The viewer is a keyboard-driven asset browser with two orthogonal controls:

  * GROUP BY: Style | Category. Style is the PRIMARY axis (Pip re-runs stable
    prompts under evolving styles/models over time, so style is the thing he
    iterates and compares along). Tabs are the style variants when grouped by
    Style (warm-grime / heavy-outline / ...), or the asset categories when
    grouped by Category. Runs that don't encode a style facet collapse to a
    single "(unstyled)" tab. If the whole dataset has only one style value, the
    toggle auto-defaults to Category (so single-style runs are still usefully
    tabbed).
  * STATUS FILTER: All | Pending | Keep | Maybe | Re-roll -- orthogonal, applies
    within whichever grouping/tab is active.

Only the ACTIVE tab's cells are rendered to the DOM (lazy render on tab switch),
so the page stays responsive as sweeps grow. Images are referenced by RELATIVE
path (not base64-inlined) so the HTML stays tiny and scales.

Verdicts + notes + winner-picks persist to a SINGLE localStorage store (shared
across all tabs -- one HTML file, so file:// origin does not fragment it) and are
seeded from verdicts.json so they survive across sessions/machines.

Keyboard: arrows move the focus ring across the rendered cells; K/M/R stamp
keep/maybe/re-roll; N/Enter edits the note; Export dumps a markdown paste-back.

Cell-id scheme (matches docs/art/reviews + verdicts.json):
  matrix cell : "<batch.id>:<style.key>__<subject.key>"
  ladder step : "<batch.id>:<step.key>"
  gallery item: "<batch.id>:<item.key>"
  sweep roll  : "sweep:<category>:<key>:<roll>"
  reroll roll : "reroll:<category>:<key>:<roll>"

Image files (relative to <repo>/<image_root>/<batch.dir>/):
  matrix "<style.key>__<subject.key>.png"; ladder/gallery "<key>.png".
Sweep images: <image_root>/sweep/<category>/<key>_<roll>.png (roll=1..N).
Re-roll images: art_source/pixellab_2026-07-17/reroll/<category>/<key>_<roll>.png.
Missing files render as a 'pending' placeholder (regenerate + re-run to fill).

Usage:  python tools/art_review/build.py   ->  writes tools/art_review/style_review.html
"""
import json
import os
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
MANIFEST = HERE / "manifest.json"
SWEEP = HERE / "sweep_prompts.json"
REROLL = REPO / "art_source/pixellab_2026-07-17/reroll"
_ROT = re.compile(r"_(north|south|east|west|north-east|north-west|south-east|south-west)$")
OUT = HERE / "style_review.html"
UNSTYLED = "(unstyled)"

# Category keys in sweep_prompts.json carry tool hints in their name
# (e.g. cats_body_type_quadruped_template_cat, ui_filler_map_object). Once one of
# these marker tokens appears, the rest of the key is a tool hint, not a label.
TOOL_HINT_MARKERS = {
    "use",
    "create",
    "map",
    "object",
    "body",
    "type",
    "template",
    "quadruped",
    "character",
    "overlays",
}


def relimg(path):
    """Relative POSIX path from the HTML file to an image, or None if missing."""
    if not path.is_file():
        return None
    return os.path.relpath(path, HERE).replace("\\", "/")


def sweep_label(cat_key):
    """Clean display label from a tool-hinted category key."""
    words = []
    for w in cat_key.split("_"):
        if w in TOOL_HINT_MARKERS:
            break
        words.append(w)
    if not words:
        words = [cat_key]
    return " ".join(words).title().replace("Ui", "UI")


def rec(cells, *, id, label, img, cat, style, key, roll, row, cap, batch, tag):
    """Append one flat cell record. The client renders these lazily per tab."""
    cells.append(
        {
            "id": id,
            "label": label,
            "img": img,
            "cat": cat,
            "style": style,
            "key": key,
            "roll": roll,
            "row": row,
            "cap": cap,
            "batch": batch,
            "tag": tag,
        }
    )


def build_matrix(cells, b, root):
    """Style matrix: style IS the facet. Under Style grouping each style is a tab
    (rows = subjects); under Category grouping each subject is a tab (a row of the
    competing styles side by side)."""
    for st in b["styles"]:
        for s in b["subjects"]:
            key = f'{st["key"]}__{s["key"]}'
            rec(
                cells,
                id=f'{b["id"]}:{key}',
                label=f'{st["label"]} / {s["label"]}',
                img=relimg(root / f"{key}.png"),
                cat=s["label"],
                style=st["key"],
                key=s["key"],
                roll=0,
                row=s["label"],
                cap=st["label"],
                batch=b["id"],
                tag="style matrix",
            )


def build_ladder(cells, b, root):
    for st in b["steps"]:
        rec(
            cells,
            id=f'{b["id"]}:{st["key"]}',
            label=st["label"],
            img=relimg(root / f'{st["key"]}.png'),
            cat="Era ladder",
            style=UNSTYLED,
            key=st["key"],
            roll=0,
            row=st["label"],
            cap=st.get("note", ""),
            batch=b["id"],
            tag="era ladder",
        )


def build_gallery(cells, b, root):
    for it in b["items"]:
        rec(
            cells,
            id=f'{b["id"]}:{it["key"]}',
            label=it["label"],
            img=relimg(root / f'{it["key"]}.png'),
            cat="Office library",
            style=UNSTYLED,
            key=it["key"],
            roll=0,
            row=it["label"],
            cap="",
            batch=b["id"],
            tag="office library",
        )


def build_sweep(cells, root_img):
    if not SWEEP.is_file():
        return
    sw = json.loads(SWEEP.read_text(encoding="utf-8"))
    default_rolls = int(sw.get("default_rolls", 3))
    for cat, entries in sw.items():
        if not isinstance(entries, list):
            continue  # skip _comment / style_suffix / default_rolls / view
        label = sweep_label(cat)
        subdir = root_img / "sweep" / cat
        for e in entries:
            key = e["key"]
            n = int(e.get("rolls", default_rolls))
            for r in range(1, n + 1):
                rec(
                    cells,
                    id=f"sweep:{cat}:{key}:{r}",
                    label=f"{key} roll {r}",
                    img=relimg(subdir / f"{key}_{r}.png"),
                    cat=label,
                    style=UNSTYLED,
                    key=key,
                    roll=r,
                    row=key,
                    cap=f"#{r}",
                    batch=f"sweep:{cat}",
                    tag="sweep",
                )


def build_reroll(cells):
    """Render the 2026-07-17 re-roll batch from the filesystem (no manifest):
    one row per asset key, rolls side by side. Single-file tilesets (no trailing
    _<n>) collapse to roll 1."""
    if not REROLL.is_dir():
        return
    for catdir in sorted(p for p in REROLL.iterdir() if p.is_dir()):
        cat = catdir.name
        label = cat.title()
        groups = {}
        for f in sorted(catdir.glob("*.png")):
            stem = f.stem
            if _ROT.search(stem):
                continue  # rotation sheet, not a review image
            m = re.match(r"^(.*)_(\d+)$", stem)
            key, roll = (m.group(1), int(m.group(2))) if m else (stem, 1)
            groups.setdefault(key, {})[roll] = f
        for key in sorted(groups):
            for r in sorted(groups[key]):
                rec(
                    cells,
                    id=f"reroll:{cat}:{key}:{r}",
                    label=f"{key} roll {r}",
                    img=relimg(groups[key][r]),
                    cat=label,
                    style=UNSTYLED,
                    key=key,
                    roll=r,
                    row=key,
                    cap=f"#{r}",
                    batch=f"reroll:{cat}",
                    tag="reroll",
                )


def ordered_unique(values):
    """First-appearance-ordered unique list, but always float UNSTYLED to the end."""
    seen = []
    for v in values:
        if v not in seen:
            seen.append(v)
    if UNSTYLED in seen:
        seen = [v for v in seen if v != UNSTYLED] + [UNSTYLED]
    return seen


def main():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    img_root = REPO / m["image_root"]
    cells = []
    for b in m["batches"]:
        root = img_root / b["dir"]
        if b["kind"] == "matrix":
            build_matrix(cells, b, root)
        elif b["kind"] == "ladder":
            build_ladder(cells, b, root)
        elif b["kind"] == "gallery":
            build_gallery(cells, b, root)
    build_sweep(cells, img_root)
    build_reroll(cells)

    styles = ordered_unique(c["style"] for c in cells)
    cats = ordered_unique(c["cat"] for c in cells)
    # Auto-fallback: single style value -> default to grouping by category.
    default_group = "category" if len(styles) <= 1 else "style"

    data = {
        "cells": cells,
        "styles": styles,
        "cats": cats,
        "defaultGroup": default_group,
    }

    vpath = HERE / "verdicts.json"
    verdicts = json.loads(vpath.read_text(encoding="utf-8")) if vpath.is_file() else {}
    verdicts.setdefault("picks", {})
    verdicts.setdefault("notes", {})
    verdicts.setdefault("verdicts", {})
    verdicts.setdefault("styledir", "")

    html = (
        TEMPLATE.replace("{{TITLE}}", esc(m["title"]))
        .replace("{{SUBTITLE}}", esc(m["subtitle"]))
        .replace("{{VERDICTS}}", json.dumps(verdicts))
        .replace("{{DATA}}", json.dumps(data, separators=(",", ":")))
    )
    OUT.write_text(html, encoding="utf-8")
    missing = sum(1 for c in cells if not c["img"])
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    print(f"  cells={len(cells)}  missing_img={missing}")
    print(f"  styles={styles}")
    print(f"  cats={cats}")
    print(f"  defaultGroup={default_group}")


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


TEMPLATE = r"""<title>{{TITLE}}</title>
<style>
  :root{
    --ground:#17120e;--panel:#211a14;--panel-2:#2b221a;--ink:#ece0cf;--ink-dim:#a9977f;--ink-faint:#6f6250;
    --amber:#e8a33d;--amber-deep:#c07a1f;--win:#6fae86;--line:#3a2e22;--checker-a:#201811;--checker-b:#180f09;
    --field:#120d09;--shadow:rgba(0,0,0,.45);
  }
  @media (prefers-color-scheme:light){:root{
    --ground:#efe6d6;--panel:#f7efe0;--panel-2:#fbf5e9;--ink:#2b2116;--ink-dim:#6b5b45;--ink-faint:#9a876c;
    --amber:#b9741a;--amber-deep:#8f5710;--win:#3f8a5c;--line:#ddccb0;--checker-a:#e6dac4;--checker-b:#ded1b8;
    --field:#fffaf0;--shadow:rgba(80,55,20,.18);}}
  :root[data-theme="dark"]{--ground:#17120e;--panel:#211a14;--panel-2:#2b221a;--ink:#ece0cf;--ink-dim:#a9977f;--ink-faint:#6f6250;--amber:#e8a33d;--amber-deep:#c07a1f;--win:#6fae86;--line:#3a2e22;--checker-a:#201811;--checker-b:#180f09;--field:#120d09;--shadow:rgba(0,0,0,.45);}
  :root[data-theme="light"]{--ground:#efe6d6;--panel:#f7efe0;--panel-2:#fbf5e9;--ink:#2b2116;--ink-dim:#6b5b45;--ink-faint:#9a876c;--amber:#b9741a;--amber-deep:#8f5710;--win:#3f8a5c;--line:#ddccb0;--checker-a:#e6dac4;--checker-b:#ded1b8;--field:#fffaf0;--shadow:rgba(80,55,20,.18);}
  /* verdict colours -- var(--win)/(--amber) are late-bound so they track theme */
  :root{--keep:var(--win);--maybe:var(--amber);--reroll:#d8695a}
  @media (prefers-color-scheme:light){:root{--reroll:#c14a3a}}
  :root[data-theme="dark"]{--reroll:#d8695a}
  :root[data-theme="light"]{--reroll:#c14a3a}
  *{box-sizing:border-box}
  body{margin:0;background:var(--ground);color:var(--ink);font-family:ui-sans-serif,system-ui,"Segoe UI",Helvetica,Arial,sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased}
  img{image-rendering:pixelated;image-rendering:crisp-edges;max-width:100%;height:auto;display:block}
  .wrap{max-width:1180px;margin:0 auto;padding:3rem 1.4rem 6rem}
  .eyebrow{font-family:ui-monospace,Consolas,monospace;font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;color:var(--amber);margin:0 0 .8rem}
  h1{font-family:ui-monospace,"Cascadia Code",Consolas,monospace;font-weight:700;font-size:clamp(1.8rem,4vw,2.7rem);line-height:1.05;margin:0 0 .6rem;text-wrap:balance}
  .lede{max-width:70ch;color:var(--ink-dim);font-size:1.02rem;margin:0}
  .direction{background:var(--panel-2);border:1px solid var(--line);border-radius:12px;padding:1.2rem 1.3rem;margin-top:1.5rem}
  .direction h2{margin:0 0 .3rem;font-size:.9rem;font-family:ui-monospace,Consolas,monospace;letter-spacing:.06em}
  .direction p{margin:0 0 .7rem;color:var(--ink-dim);font-size:.85rem}
  .direction textarea{width:100%;min-height:64px;resize:vertical;background:var(--field);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:.6rem .7rem;font-family:ui-monospace,Consolas,monospace;font-size:.83rem;line-height:1.5}
  /* control deck: group toggle + status filter + tabs */
  .deck{position:sticky;top:0;z-index:40;margin:1.6rem 0 1.4rem;padding:.8rem 0 .5rem;background:color-mix(in srgb,var(--ground) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
  .deck-row{display:flex;align-items:center;gap:.9rem;flex-wrap:wrap;margin-bottom:.6rem}
  .seg{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}
  .seg button{font-family:ui-monospace,Consolas,monospace;font-size:.72rem;text-transform:uppercase;letter-spacing:.04em;padding:.34rem .7rem;border:0;background:var(--field);color:var(--ink-dim);cursor:pointer}
  .seg button+button{border-left:1px solid var(--line)}
  .seg button.on{background:var(--amber);color:#20140a;font-weight:700}
  .seg button:focus-visible{outline:2px solid var(--amber);outline-offset:-2px}
  .deck-label{font-family:ui-monospace,Consolas,monospace;font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-faint)}
  .tabbar{display:flex;gap:.35rem;overflow-x:auto;padding-bottom:.3rem;scrollbar-width:thin}
  .tab{white-space:nowrap;font-family:ui-monospace,Consolas,monospace;font-size:.76rem;padding:.4rem .75rem;border-radius:8px 8px 0 0;border:1px solid var(--line);border-bottom:0;background:var(--panel);color:var(--ink-dim);cursor:pointer}
  .tab .cnt{font-size:.62rem;color:var(--ink-faint);margin-left:.35rem}
  .tab.on{background:var(--panel-2);color:var(--ink);box-shadow:inset 0 -3px 0 var(--amber)}
  .tab:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
  #board{min-height:40vh}
  .empty{color:var(--ink-faint);font-family:ui-monospace,Consolas,monospace;font-size:.85rem;padding:2rem 0}
  .cell{display:flex;flex-direction:column;gap:.4rem;border-radius:8px;scroll-margin:120px}
  .cell.v-keep{box-shadow:0 0 0 2px var(--keep)}
  .cell.v-maybe{box-shadow:0 0 0 2px var(--maybe)}
  .cell.v-reroll{box-shadow:0 0 0 2px var(--reroll)}
  .cell.focused{outline:2px solid var(--amber);outline-offset:2px}
  .stage{background-color:var(--checker-a);background-image:linear-gradient(45deg,var(--checker-b) 25%,transparent 25%),linear-gradient(-45deg,var(--checker-b) 25%,transparent 25%),linear-gradient(45deg,transparent 75%,var(--checker-b) 75%),linear-gradient(-45deg,transparent 75%,var(--checker-b) 75%);background-size:14px 14px;background-position:0 0,0 7px,7px -7px,-7px 0;border:1px solid var(--line);border-radius:8px;padding:.7rem;display:grid;place-items:center;min-height:130px}
  .stage img{width:auto;max-height:150px}
  .stage.pending{color:var(--ink-faint);font-family:ui-monospace,Consolas,monospace;font-size:.7rem;text-align:center}
  .note{width:100%;background:var(--field);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:.35rem .5rem;font-size:.76rem;font-family:ui-sans-serif,system-ui,sans-serif}
  .note:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
  .verdict{display:flex;gap:.25rem}
  .vbtn{flex:1;font-family:ui-monospace,Consolas,monospace;font-size:.62rem;text-transform:uppercase;letter-spacing:.03em;padding:.28rem .1rem;border-radius:5px;border:1px solid var(--line);background:var(--field);color:var(--ink-dim);cursor:pointer;transition:.1s}
  .vbtn:hover{color:var(--ink);border-color:var(--ink-faint)}
  .vbtn:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
  .vbtn.on[data-v="keep"]{background:var(--keep);border-color:var(--keep);color:#12251a}
  .vbtn.on[data-v="maybe"]{background:var(--maybe);border-color:var(--maybe);color:#2a1e08}
  .vbtn.on[data-v="reroll"]{background:var(--reroll);border-color:var(--reroll);color:#2a1210}
  /* rows: one asset, its rolls/styles side by side */
  .board-rows{display:flex;flex-direction:column;gap:1rem}
  .row{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:.9rem;display:grid;grid-template-columns:180px 1fr;gap:.9rem;align-items:start}
  .rowhead h4{margin:0 0 .25rem;font-size:.9rem;font-family:ui-monospace,Consolas,monospace;word-break:break-word}
  .rowhead p{margin:0;font-size:.72rem;color:var(--ink-faint);font-family:ui-monospace,Consolas,monospace}
  .rolls{display:grid;grid-template-columns:repeat(var(--cols),minmax(130px,1fr));gap:.7rem}
  .rollcell{position:relative;background:var(--panel-2);border:1px solid var(--line);padding:.6rem;border-radius:8px}
  .cap{position:absolute;top:.45rem;left:.5rem;z-index:1;max-width:calc(100% - 1rem);font-family:ui-monospace,Consolas,monospace;font-size:.62rem;color:var(--amber);background:var(--ground);border:1px solid var(--line);border-radius:4px;padding:0 .3rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  /* keyboard legend */
  .kbd-legend{position:fixed;top:10px;right:10px;z-index:50;display:flex;flex-direction:column;gap:.28rem;background:color-mix(in srgb,var(--panel) 92%,transparent);border:1px solid var(--line);border-radius:9px;padding:.55rem .65rem;font-family:ui-monospace,Consolas,monospace;font-size:.66rem;color:var(--ink-dim);pointer-events:none;box-shadow:0 2px 12px var(--shadow);backdrop-filter:blur(4px)}
  .kbd-legend b{color:var(--amber);font-weight:400}
  .kbd-legend kbd{display:inline-block;min-width:1.1em;text-align:center;padding:.05rem .32rem;margin-right:.12rem;border:1px solid var(--line);border-bottom-width:2px;border-radius:4px;background:var(--field);color:var(--ink);font-size:.62rem}
  /* export bar */
  .exportbar{position:sticky;bottom:0;margin:2.5rem -1.4rem -6rem;padding:1rem 1.4rem;background:color-mix(in srgb,var(--ground) 88%,transparent);backdrop-filter:blur(8px);border-top:1px solid var(--line);display:flex;align-items:center;gap:1rem;flex-wrap:wrap}
  .tally{font-family:ui-monospace,Consolas,monospace;font-size:.78rem;color:var(--ink-dim)}
  .tally b{color:var(--win)}
  .spacer{flex:1}
  .btn{font-family:ui-monospace,Consolas,monospace;font-size:.8rem;padding:.5rem .9rem;border-radius:7px;border:1px solid var(--amber);background:var(--amber);color:#20140a;font-weight:700;cursor:pointer}
  .btn:hover{background:var(--amber-deep);border-color:var(--amber-deep)}
  .btn:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
  .btn.ghost{background:transparent;color:var(--ink-dim);border-color:var(--line);font-weight:400}
  .btn.ghost:hover{color:var(--ink);border-color:var(--ink-faint)}
  dialog{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:12px;padding:0;max-width:min(760px,92vw);width:100%}
  dialog::backdrop{background:rgba(0,0,0,.55)}
  .modal-head{display:flex;align-items:center;justify-content:space-between;padding:1rem 1.2rem;border-bottom:1px solid var(--line)}
  .modal-head h3{margin:0;font-size:1rem;font-family:ui-monospace,Consolas,monospace}
  .modal-body{padding:1.1rem 1.2rem}
  .modal-body p{margin:0 0 .7rem;color:var(--ink-dim);font-size:.85rem}
  #exporttext{width:100%;min-height:320px;resize:vertical;background:var(--field);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:.8rem;font-family:ui-monospace,Consolas,monospace;font-size:.76rem;line-height:1.5;white-space:pre}
  footer{margin-top:3rem;padding-top:1.4rem;border-top:1px solid var(--line);color:var(--ink-faint);font-size:.78rem;font-family:ui-monospace,Consolas,monospace}
  @media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
  @media (max-width:760px){.row{grid-template-columns:1fr}.rolls{--cols:2!important}}
  @media (max-width:640px){.kbd-legend{display:none}}
</style>

<div class="kbd-legend" aria-hidden="true">
  <span><kbd>&larr;</kbd><kbd>&rarr;</kbd> move focus</span>
  <span><b>K</b> keep &middot; <b>M</b> maybe &middot; <b>R</b> re-roll</span>
  <span><kbd>N</kbd>/<kbd>&crarr;</kbd> note &middot; <kbd>Esc</kbd> back</span>
</div>

<div class="wrap">
  <p class="eyebrow">P(Doom)1 &middot; art direction &middot; repo tool</p>
  <h1>{{TITLE}}</h1>
  <p class="lede">{{SUBTITLE}} Rebuild after each generation round: <code>python tools/art_review/build.py</code>.</p>

  <div class="direction">
    <h2>// style-direction notes</h2>
    <p>Global dials to push next round (e.g. "10% more futurepunk on the decent tier", "heavier 1px black outline"). Exported with your picks.</p>
    <textarea id="styledir" placeholder="jot the dials you want to push..."></textarea>
  </div>

  <div class="deck">
    <div class="deck-row">
      <span class="deck-label">group by</span>
      <div class="seg" id="groupseg" role="group" aria-label="Group by">
        <button type="button" data-g="style">Style</button>
        <button type="button" data-g="category">Category</button>
      </div>
      <span class="deck-label">status</span>
      <div class="seg" id="filterseg" role="group" aria-label="Status filter">
        <button type="button" data-f="all">All</button>
        <button type="button" data-f="pending">Pending</button>
        <button type="button" data-f="keep">Keep</button>
        <button type="button" data-f="maybe">Maybe</button>
        <button type="button" data-f="reroll">Re-roll</button>
      </div>
    </div>
    <div class="tabbar" id="tabbar" role="tablist"></div>
  </div>

  <div id="board"></div>

  <div class="exportbar">
    <div class="tally" id="tally">picks: <b id="ct">0</b></div>
    <div class="tally" id="vct"></div>
    <div class="spacer"></div>
    <button type="button" class="btn ghost" id="clearbtn">reset</button>
    <button type="button" class="btn" id="exportbtn">Export my picks &rarr;</button>
  </div>
  <footer>Verdicts saved in your browser (localStorage) + seeded from verdicts.json. Export to hand them back for the next round.</footer>
</div>

<dialog id="exportdlg">
  <div class="modal-head"><h3>// your picks</h3><button type="button" class="btn ghost" id="copybtn">copy</button></div>
  <div class="modal-body"><p>Copy and paste this back into the chat.</p><textarea id="exporttext" readonly></textarea></div>
</dialog>

<script>
(function(){
  "use strict";
  var KEY="pdoom_style_review_v1",DKEY="pdoom_style_dir_global_v1",UKEY="pdoom_style_review_ui_v1";
  var SEEDED={{VERDICTS}};
  var DATA={{DATA}};
  var CELLDATA=DATA.cells;
  var LABELS={};CELLDATA.forEach(function(c){LABELS[c.id]=c.label;});

  var st={
    picks:Object.assign({},SEEDED.picks||{}),
    notes:Object.assign({},SEEDED.notes||{}),
    verdicts:Object.assign({},SEEDED.verdicts||{})
  };
  try{var ls=JSON.parse(localStorage.getItem(KEY)||"{}");
    if(ls.picks)st.picks=Object.assign(st.picks,ls.picks);
    if(ls.notes)st.notes=Object.assign(st.notes,ls.notes);
    if(ls.verdicts)st.verdicts=Object.assign(st.verdicts,ls.verdicts);
  }catch(e){}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(st));}catch(e){}}
  function reduceMotion(){return window.matchMedia&&matchMedia('(prefers-reduced-motion:reduce)').matches;}
  function esc(s){return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}

  // ---- UI state (grouping / active tab / status filter) ----
  var ui={group:DATA.defaultGroup,tab:null,filter:"all"};
  try{var us=JSON.parse(localStorage.getItem(UKEY)||"{}");
    if(us.group==="style"||us.group==="category")ui.group=us.group;
    if(typeof us.tab==="string")ui.tab=us.tab;
    if(us.filter)ui.filter=us.filter;
  }catch(e){}
  function saveUI(){try{localStorage.setItem(UKEY,JSON.stringify(ui));}catch(e){}}
  function tabsFor(group){return group==="style"?DATA.styles:DATA.cats;}
  function facetOf(c){return ui.group==="style"?c.style:c.cat;}
  // validate persisted tab against current grouping
  if(tabsFor(ui.group).indexOf(ui.tab)<0)ui.tab=tabsFor(ui.group)[0]||null;

  var board=document.getElementById('board');
  var tabbar=document.getElementById('tabbar');

  // ---- verdicts ----
  function applyVerdict(c,v){
    c.classList.remove('v-keep','v-maybe','v-reroll');
    if(v)c.classList.add('v-'+v);
    c.querySelectorAll('.vbtn').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-v')===v);});
  }
  function setVerdict(c,v){
    var id=c.getAttribute('data-item');
    if(st.verdicts[id]===v){delete st.verdicts[id];v=null;}
    else{st.verdicts[id]=v;}
    applyVerdict(c,v);save();tally();
    // if a status filter is active, a changed verdict may drop the cell from view
    if(ui.filter!=="all")render();
  }

  // ---- keyboard nav over currently-rendered cells ----
  var CELLS=[],cur=-1;
  function setFocus(i,scroll){
    if(i<0||i>=CELLS.length)return;
    if(cur>=0&&CELLS[cur])CELLS[cur].classList.remove('focused');
    cur=i;var c=CELLS[cur];c.classList.add('focused');
    if(scroll)c.scrollIntoView({behavior:reduceMotion()?'auto':'smooth',block:'nearest',inline:'nearest'});
  }
  function move(d){
    var i=cur<0?0:cur+d;
    if(i<0)i=0;if(i>=CELLS.length)i=CELLS.length-1;
    setFocus(i,true);
  }
  function focusNote(){
    if(cur<0)setFocus(0,true);
    var c=CELLS[cur],n=c&&c.querySelector('.note');
    if(n){n.focus();if(n.select)n.select();}
  }

  // ---- rendering ----
  function cellHTML(c){
    var stg=c.img
      ? '<div class="stage"><img loading="lazy" src="'+esc(c.img)+'" alt="'+esc(c.label)+'"></div>'
      : '<div class="stage pending"><span>pending<br>regen &amp; rebuild</span></div>';
    return '<div class="cell rollcell" data-item="'+esc(c.id)+'" data-label="'+esc(c.label)+'">'
      +(c.cap?'<div class="cap" title="'+esc(c.cap)+'">'+esc(c.cap)+'</div>':'')
      +stg
      +'<div class="verdict" role="group" aria-label="Verdict for '+esc(c.label)+'">'
      +'<button type="button" class="vbtn" data-v="keep" title="Keep (K)">keep</button>'
      +'<button type="button" class="vbtn" data-v="maybe" title="Maybe (M)">maybe</button>'
      +'<button type="button" class="vbtn" data-v="reroll" title="Re-roll (R)">re-roll</button></div>'
      +'<input type="text" class="note" placeholder="note..." aria-label="Note for '+esc(c.label)+'">'
      +'</div>';
  }
  function passesFilter(c){
    if(ui.filter==="all")return true;
    var v=st.verdicts[c.id]||null;
    if(ui.filter==="pending")return !v;
    return v===ui.filter;
  }
  function activeCells(){
    return CELLDATA.filter(function(c){return facetOf(c)===ui.tab&&passesFilter(c);});
  }
  function buildTabs(){
    var tabs=tabsFor(ui.group);
    // per-tab totals (ignore status filter, so counts are stable)
    var totals={};
    CELLDATA.forEach(function(c){var f=facetOf(c);totals[f]=(totals[f]||0)+1;});
    tabbar.innerHTML=tabs.map(function(t){
      var on=t===ui.tab?' on':'';
      return '<button type="button" class="tab'+on+'" role="tab" data-tab="'+esc(t)+'" aria-selected="'+(t===ui.tab)+'">'
        +esc(t)+'<span class="cnt">'+(totals[t]||0)+'</span></button>';
    }).join('');
    tabbar.querySelectorAll('.tab').forEach(function(btn){
      btn.addEventListener('click',function(){ui.tab=btn.getAttribute('data-tab');saveUI();render();});
    });
  }
  function render(){
    buildTabs();
    var cells=activeCells();
    var order=[],groups={};
    cells.forEach(function(c){
      var g=c.batch+'|'+c.key;
      if(!groups[g]){groups[g]=[];order.push(g);}
      groups[g].push(c);
    });
    var html;
    if(!order.length){
      html='<p class="empty">no cells match this tab + filter.</p>';
    }else{
      html='<div class="board-rows">'+order.map(function(g){
        var rows=groups[g],first=rows[0];
        return '<div class="row"><div class="rowhead"><h4>'+esc(first.row)+'</h4>'
          +'<p>'+esc(first.tag||"")+'</p></div>'
          +'<div class="rolls" style="--cols:'+Math.max(rows.length,1)+'">'
          +rows.map(cellHTML).join('')+'</div></div>';
      }).join('')+'</div>';
    }
    board.innerHTML=html;
    wireCells();
  }
  function wireCells(){
    CELLS=[].slice.call(board.querySelectorAll('.cell'));cur=-1;
    CELLS.forEach(function(c,idx){
      var id=c.getAttribute('data-item');
      var inp=c.querySelector('.note');
      if(inp){
        if(st.notes[id])inp.value=st.notes[id];
        inp.addEventListener('input',function(e){st.notes[id]=e.target.value;if(!e.target.value)delete st.notes[id];save();});
      }
      applyVerdict(c,st.verdicts[id]||null);
      c.querySelectorAll('.vbtn').forEach(function(btn){
        btn.addEventListener('click',function(){setFocus(idx,false);setVerdict(c,btn.getAttribute('data-v'));});
      });
      c.addEventListener('mousedown',function(){setFocus(idx,false);});
    });
  }

  // group toggle
  document.querySelectorAll('#groupseg button').forEach(function(btn){
    btn.classList.toggle('on',btn.getAttribute('data-g')===ui.group);
    btn.addEventListener('click',function(){
      ui.group=btn.getAttribute('data-g');
      document.querySelectorAll('#groupseg button').forEach(function(b){b.classList.toggle('on',b===btn);});
      if(tabsFor(ui.group).indexOf(ui.tab)<0)ui.tab=tabsFor(ui.group)[0]||null;
      saveUI();render();
    });
  });
  // status filter
  document.querySelectorAll('#filterseg button').forEach(function(btn){
    btn.classList.toggle('on',btn.getAttribute('data-f')===ui.filter);
    btn.addEventListener('click',function(){
      ui.filter=btn.getAttribute('data-f');
      document.querySelectorAll('#filterseg button').forEach(function(b){b.classList.toggle('on',b===btn);});
      saveUI();render();
    });
  });

  document.addEventListener('keydown',function(e){
    var t=e.target,tag=(t.tagName||'').toLowerCase();
    var typing=tag==='input'||tag==='textarea'||t.isContentEditable;
    if(typing){ if(e.key==='Escape'){t.blur();e.preventDefault();} return; }
    if(e.ctrlKey||e.metaKey||e.altKey)return;
    var k=e.key;
    if(k==='ArrowRight'||k==='ArrowDown'){move(1);e.preventDefault();}
    else if(k==='ArrowLeft'||k==='ArrowUp'){move(-1);e.preventDefault();}
    else if(k==='k'||k==='K'){if(cur>=0){setVerdict(CELLS[cur],'keep');e.preventDefault();}}
    else if(k==='m'||k==='M'){if(cur>=0){setVerdict(CELLS[cur],'maybe');e.preventDefault();}}
    else if(k==='r'||k==='R'){if(cur>=0){setVerdict(CELLS[cur],'reroll');e.preventDefault();}}
    else if(k==='n'||k==='N'||k==='Enter'){focusNote();e.preventDefault();}
    else if(k==='Escape'){if(cur>=0){CELLS[cur].classList.remove('focused');cur=-1;}}
  });

  var dir=document.getElementById('styledir');
  try{dir.value=localStorage.getItem(DKEY)||SEEDED.styledir||"";}catch(e){dir.value=SEEDED.styledir||"";}
  dir.addEventListener('input',function(e){try{localStorage.setItem(DKEY,e.target.value);}catch(x){}});

  function tally(){
    document.getElementById('ct').textContent=Object.keys(st.picks).length;
    var k=0,m=0,r=0;
    for(var id in st.verdicts){var v=st.verdicts[id];if(v==='keep')k++;else if(v==='maybe')m++;else if(v==='reroll')r++;}
    var el=document.getElementById('vct');
    if(el)el.innerHTML='keep <b>'+k+'</b> / maybe <b>'+m+'</b> / re-roll <b>'+r+'</b>';
  }

  function labelFor(id){return LABELS[id]||id;}
  function buildExport(){
    var L=["# P(Doom)1 style review -- Pip's picks",""];
    var sd=(dir.value||"").trim();
    if(sd){L.push("## Style direction",sd,"");}
    L.push("## Winning styles");
    var pk=Object.keys(st.picks);
    L.push(pk.length?pk.map(function(b){return "- "+b+": **"+st.picks[b]+"**";}).join("\n"):"_(none picked)_");
    L.push("");
    var groups={keep:[],maybe:[],reroll:[]};
    Object.keys(st.verdicts).forEach(function(id){
      var v=st.verdicts[id];if(!groups[v])return;
      var note=st.notes[id]?(" -- "+st.notes[id]):"";
      groups[v].push("- "+labelFor(id)+" ("+id+")"+note);
    });
    var titles={keep:"Keep",maybe:"Maybe",reroll:"Re-roll"};
    ["keep","maybe","reroll"].forEach(function(g){
      if(groups[g].length){L.push("## "+titles[g],groups[g].join("\n"),"");}
    });
    var extra=Object.keys(st.notes).filter(function(id){return !st.verdicts[id];});
    if(extra.length){L.push("## Other notes");
      extra.forEach(function(id){L.push("- "+labelFor(id)+" ("+id+"): "+st.notes[id]);});
      L.push("");
    }
    return L.join("\n");
  }
  var dlg=document.getElementById('exportdlg'),txt=document.getElementById('exporttext');
  document.getElementById('exportbtn').addEventListener('click',function(){
    txt.value=buildExport();
    if(typeof dlg.showModal==='function')dlg.showModal();else alert(txt.value);
    txt.focus();txt.select();
  });
  document.getElementById('copybtn').addEventListener('click',function(){
    txt.select();var ok=false;try{ok=document.execCommand('copy');}catch(e){}
    if(navigator.clipboard)navigator.clipboard.writeText(txt.value).catch(function(){});
    this.textContent=ok?"copied":"select+copy";var b=this;setTimeout(function(){b.textContent="copy";},1500);
  });
  document.getElementById('clearbtn').addEventListener('click',function(){
    if(!confirm("Clear all picks, verdicts and notes?"))return;
    st={picks:{},notes:{},verdicts:{}};save();
    render();tally();
  });

  render();
  tally();
})();
</script>
"""

if __name__ == "__main__":
    main()
