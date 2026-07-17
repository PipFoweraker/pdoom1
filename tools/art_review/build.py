#!/usr/bin/env python3
"""Build the P(Doom)1 style-review tool: a self-contained HTML page from
manifest.json + the committed PNGs. Rows = style directions, columns = subjects,
so a whole style reads across many subjects at once. Plus an era-ladder strip,
an office gallery, and (when present) the overnight generation sweep.

It's a keyboard-driven asset browser: arrow keys move a focus ring between
review cells, K/M/R stamp a keep/maybe/re-roll verdict, N/Enter edits the note.
Verdicts + notes + picks persist to localStorage and are seeded from
verdicts.json so they survive across sessions/machines.

Convention for image files (relative to <repo>/<image_root>/<batch.dir>/):
  matrix cell : "<style.key>__<subject.key>.png"
  ladder step : "<step.key>.png"
  gallery item: "<item.key>.png"
Sweep images live at <image_root>/sweep/<category>/<key>_<roll>.png (roll=1..N).
Missing files render as a 'pending' placeholder (regenerate + re-run to fill).

Usage:  python tools/art_review/build.py   ->  writes tools/art_review/style_review.html
"""
import base64
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
MANIFEST = HERE / "manifest.json"
SWEEP = HERE / "sweep_prompts.json"
REROLL = REPO / "art_source/pixellab_2026-07-17/reroll"
_ROT = re.compile(r"_(north|south|east|west|north-east|north-west|south-east|south-west)$")
OUT = HERE / "style_review.html"

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


def datauri(path: pathlib.Path):
    if not path.is_file():
        return None
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def controls(label):
    """Verdict tri-state (keep / maybe / re-roll) + note input for a review cell."""
    return f"""<div class="verdict" role="group" aria-label="Verdict for {esc(label)}">
          <button type="button" class="vbtn" data-v="keep" title="Keep (K)">keep</button>
          <button type="button" class="vbtn" data-v="maybe" title="Maybe (M)">maybe</button>
          <button type="button" class="vbtn" data-v="reroll" title="Re-roll (R)">re-roll</button>
        </div>
        <input type="text" class="note" placeholder="note..." aria-label="Note for {esc(label)}">"""


def stage(label, uri, pending="pending<br>regen &amp; rebuild"):
    if uri:
        return f'<div class="stage"><img src="{uri}" alt="{esc(label)}"></div>'
    return f'<div class="stage pending"><span>{pending}</span></div>'


def cell(item_id, label, uri):
    return f"""
      <div class="cell" data-item="{item_id}" data-label="{esc(label)}">
        {stage(label, uri)}
        {controls(label)}
      </div>"""


def build_matrix(b, root):
    subs = b["subjects"]
    head = '<div class="mx-corner"></div>' + "".join(
        f'<div class="mx-col">{esc(s["label"])}</div>' for s in subs
    )
    rows = []
    for st in b["styles"]:
        cells = []
        for s in subs:
            key = f'{st["key"]}__{s["key"]}'
            uri = datauri(root / f"{key}.png")
            cells.append(cell(f'{b["id"]}:{key}', f'{st["label"]} / {s["label"]}', uri))
        rows.append(
            f"""
      <div class="mx-row" data-style="{b['id']}:{st['key']}">
        <div class="mx-rowhead">
          <label class="pick"><input type="radio" name="win-{b['id']}" value="{st['key']}"><span class="pick-dot"></span></label>
          <div class="rowmeta"><h3>{esc(st['label'])}</h3><p>{esc(st['note'])}</p></div>
        </div>
        <div class="mx-cells" style="--cols:{len(subs)}">{''.join(cells)}</div>
      </div>"""
        )
    return f"""
    <section class="batch" data-batch="{b['id']}">
      <div class="section-label">{esc(b['title'])}</div>
      <p class="batch-note">{esc(b['note'])}</p>
      <div class="matrix">
        <div class="mx-headrow" style="--cols:{len(subs)}">{head}</div>
        {''.join(rows)}
      </div>
    </section>"""


def build_ladder(b, root):
    steps = []
    for i, st in enumerate(b["steps"]):
        uri = datauri(root / f'{st["key"]}.png')
        steps.append(
            f"""
        <div class="cell ladder-step" data-item="{b['id']}:{st['key']}" data-label="{esc(st['label'])}">
          <div class="era-idx">{i+1}</div>
          {stage(st['label'], uri, 'pending')}
          <h4>{esc(st['label'])}</h4><p class="era-note">{esc(st['note'])}</p>
          {controls(st['label'])}
        </div>"""
        )
    return f"""
    <section class="batch" data-batch="{b['id']}">
      <div class="section-label">{esc(b['title'])}</div>
      <p class="batch-note">{esc(b['note'])}</p>
      <div class="ladder-scroll"><div class="ladder">{''.join(steps)}</div></div>
    </section>"""


def build_gallery(b, root):
    cells = []
    for it in b["items"]:
        uri = datauri(root / f'{it["key"]}.png')
        cells.append(
            f"""
      <div class="cell" data-item="{b['id']}:{it['key']}" data-label="{esc(it['label'])}">
        {stage(it['label'], uri, 'pending')}
        <h4>{esc(it['label'])}</h4>
        {controls(it['label'])}
      </div>"""
        )
    return f"""
    <section class="batch" data-batch="{b['id']}">
      <div class="section-label">{esc(b['title'])}</div>
      <p class="batch-note">{esc(b['note'])}</p>
      <div class="gallery">{''.join(cells)}</div>
    </section>"""


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


def build_sweep(root_img):
    """Render the overnight sweep: one section per category, one row per asset,
    that asset's rolls side by side as review cells. root_img is <image_root>."""
    if not SWEEP.is_file():
        return ""
    sw = json.loads(SWEEP.read_text(encoding="utf-8"))
    default_rolls = int(sw.get("default_rolls", 3))
    sections = []
    for cat, entries in sw.items():
        if not isinstance(entries, list):
            continue  # skip _comment / style_suffix / default_rolls / view
        subdir = root_img / "sweep" / cat
        rows = []
        for e in entries:
            key = e["key"]
            n = int(e.get("rolls", default_rolls))
            rolls = []
            for r in range(1, n + 1):
                uri = datauri(subdir / f"{key}_{r}.png")
                item_id = f"sweep:{cat}:{key}:{r}"
                label = f"{key} roll {r}"
                rolls.append(
                    f"""
          <div class="cell sweep-cell" data-item="{item_id}" data-label="{esc(label)}">
            <div class="roll-idx">#{r}</div>
            {stage(label, uri, 'pending')}
            {controls(label)}
          </div>"""
                )
            desc = esc(e.get("desc", ""))
            rows.append(
                f"""
      <div class="sweep-row">
        <div class="sweep-rowhead"><h4>{esc(key)}</h4><p>{desc}</p></div>
        <div class="sweep-rolls" style="--cols:{n}">{''.join(rolls)}</div>
      </div>"""
            )
        sections.append(
            f"""
    <section class="batch" data-batch="sweep:{cat}">
      <div class="section-label">Sweep &middot; {esc(sweep_label(cat))}</div>
      <p class="batch-note">One row per asset; rolls side by side -- keep the best roll, re-roll the rest.</p>
      <div class="sweep">{''.join(rows)}</div>
    </section>"""
        )
    if not sections:
        return ""
    return '\n    <div class="section-label big">// overnight sweep</div>\n' + "\n".join(sections)


def build_reroll():
    """Render the 2026-07-17 re-roll batch from the filesystem (no manifest):
    one section per category dir, one row per asset key, rolls side by side."""
    if not REROLL.is_dir():
        return ""
    sections = []
    for catdir in sorted(p for p in REROLL.iterdir() if p.is_dir()):
        cat = catdir.name
        groups = {}
        for f in sorted(catdir.glob("*.png")):
            stem = f.stem
            if _ROT.search(stem):
                continue  # rotation sheet, not a review image
            m = re.match(r"^(.*)_(\d+)$", stem)
            key, roll = (m.group(1), int(m.group(2))) if m else (stem, 1)
            groups.setdefault(key, {})[roll] = f
        if not groups:
            continue
        rows = []
        for key in sorted(groups):
            rolls_html = []
            for r in sorted(groups[key]):
                uri = datauri(groups[key][r])
                item_id = f"reroll:{cat}:{key}:{r}"
                label = f"{key} roll {r}"
                rolls_html.append(
                    f"""
          <div class="cell sweep-cell" data-item="{item_id}" data-label="{esc(label)}">
            <div class="roll-idx">#{r}</div>
            {stage(label, uri, 'pending')}
            {controls(label)}
          </div>"""
                )
            rows.append(
                f"""
      <div class="sweep-row">
        <div class="sweep-rowhead"><h4>{esc(key)}</h4><p></p></div>
        <div class="sweep-rolls" style="--cols:{len(groups[key])}">{''.join(rolls_html)}</div>
      </div>"""
            )
        sections.append(
            f"""
    <section class="batch" data-batch="reroll:{cat}">
      <div class="section-label">Re-roll &middot; {esc(cat.title())}</div>
      <p class="batch-note">2026-07-17 re-roll batch -- keep the best roll, re-roll the rest.</p>
      <div class="sweep">{''.join(rows)}</div>
    </section>"""
        )
    if not sections:
        return ""
    return '\n    <div class="section-label big">// re-roll batch (2026-07-17)</div>\n' + "\n".join(
        sections
    )


def main():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    img_root = REPO / m["image_root"]
    sections = []
    for b in m["batches"]:
        root = img_root / b["dir"]
        if b["kind"] == "matrix":
            sections.append(build_matrix(b, root))
        elif b["kind"] == "ladder":
            sections.append(build_ladder(b, root))
        elif b["kind"] == "gallery":
            sections.append(build_gallery(b, root))
    sections.append(build_sweep(img_root))
    sections.append(build_reroll())
    body = "\n".join(s for s in sections if s)

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
        .replace("{{BODY}}", body)
    )
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


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
  .section-label{font-family:ui-monospace,Consolas,monospace;font-size:.74rem;letter-spacing:.2em;text-transform:uppercase;color:var(--ink-faint);margin:2.6rem 0 .6rem;display:flex;align-items:center;gap:1rem}
  .section-label::after{content:"";flex:1;height:1px;background:var(--line)}
  .section-label.big{color:var(--amber);font-size:.82rem;margin-top:3.4rem}
  .batch-note{max-width:78ch;color:var(--ink-dim);font-size:.9rem;margin:0 0 1.3rem}
  .gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:.9rem}
  .gallery .cell{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:.9rem}
  .gallery .cell h4{margin:.5rem 0 .3rem;font-size:.88rem;text-align:center}
  /* matrix */
  .matrix{display:flex;flex-direction:column;gap:.7rem}
  .mx-headrow{display:grid;grid-template-columns:200px repeat(var(--cols),1fr);gap:.7rem;align-items:end}
  .mx-col{font-family:ui-monospace,Consolas,monospace;font-size:.8rem;color:var(--ink-dim);text-align:center;padding-bottom:.2rem;letter-spacing:.04em}
  .mx-row{display:grid;grid-template-columns:200px 1fr;gap:.7rem;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:.8rem;align-items:stretch}
  .mx-row.won{border-color:var(--win);box-shadow:0 0 0 1px var(--win)}
  .mx-rowhead{display:flex;gap:.6rem;align-items:flex-start}
  .rowmeta h3{margin:0;font-size:1rem}
  .rowmeta p{margin:.15rem 0 0;font-size:.78rem;color:var(--ink-dim)}
  .pick{position:relative;cursor:pointer;padding-top:.15rem}
  .pick input{position:absolute;opacity:0;width:1px;height:1px}
  .pick-dot{display:block;width:18px;height:18px;border:2px solid var(--ink-faint);border-radius:50%;transition:.12s}
  .pick input:checked+.pick-dot{border-color:var(--win);background:var(--win);box-shadow:inset 0 0 0 3px var(--panel)}
  .pick input:focus-visible+.pick-dot{outline:2px solid var(--amber);outline-offset:2px}
  .mx-cells{display:grid;grid-template-columns:repeat(var(--cols),1fr);gap:.7rem}
  .cell{display:flex;flex-direction:column;gap:.4rem;border-radius:8px;scroll-margin:80px}
  /* verdict border ring (box-shadow needs no pre-existing border on matrix cells) */
  .cell.v-keep{box-shadow:0 0 0 2px var(--keep)}
  .cell.v-maybe{box-shadow:0 0 0 2px var(--maybe)}
  .cell.v-reroll{box-shadow:0 0 0 2px var(--reroll)}
  .cell.focused{outline:2px solid var(--amber);outline-offset:2px}
  .stage{background-color:var(--checker-a);background-image:linear-gradient(45deg,var(--checker-b) 25%,transparent 25%),linear-gradient(-45deg,var(--checker-b) 25%,transparent 25%),linear-gradient(45deg,transparent 75%,var(--checker-b) 75%),linear-gradient(-45deg,transparent 75%,var(--checker-b) 75%);background-size:14px 14px;background-position:0 0,0 7px,7px -7px,-7px 0;border:1px solid var(--line);border-radius:8px;padding:.7rem;display:grid;place-items:center;min-height:130px}
  .stage img{width:auto;max-height:150px}
  .stage.pending{color:var(--ink-faint);font-family:ui-monospace,Consolas,monospace;font-size:.7rem;text-align:center}
  .note{width:100%;background:var(--field);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:.35rem .5rem;font-size:.76rem;font-family:ui-sans-serif,system-ui,sans-serif}
  .note:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
  /* verdict buttons */
  .verdict{display:flex;gap:.25rem}
  .vbtn{flex:1;font-family:ui-monospace,Consolas,monospace;font-size:.62rem;text-transform:uppercase;letter-spacing:.03em;padding:.28rem .1rem;border-radius:5px;border:1px solid var(--line);background:var(--field);color:var(--ink-dim);cursor:pointer;transition:.1s}
  .vbtn:hover{color:var(--ink);border-color:var(--ink-faint)}
  .vbtn:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
  .vbtn.on[data-v="keep"]{background:var(--keep);border-color:var(--keep);color:#12251a}
  .vbtn.on[data-v="maybe"]{background:var(--maybe);border-color:var(--maybe);color:#2a1e08}
  .vbtn.on[data-v="reroll"]{background:var(--reroll);border-color:var(--reroll);color:#2a1210}
  /* ladder */
  .ladder-scroll{overflow-x:auto}
  .ladder{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(190px,1fr);gap:.9rem;min-width:min-content}
  .ladder-step{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:1rem;position:relative}
  .era-idx{position:absolute;top:.6rem;left:.7rem;font-family:ui-monospace,Consolas,monospace;font-size:.7rem;color:var(--amber);border:1px solid var(--line);border-radius:50%;width:1.4rem;height:1.4rem;display:grid;place-items:center;background:var(--ground)}
  .ladder-step h4{margin:.5rem 0 .1rem;font-size:.95rem}
  .era-note{margin:0 0 .5rem;font-size:.76rem;color:var(--ink-dim)}
  /* sweep */
  .sweep{display:flex;flex-direction:column;gap:1rem}
  .sweep-row{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:.9rem;display:grid;grid-template-columns:180px 1fr;gap:.9rem;align-items:start}
  .sweep-rowhead h4{margin:0 0 .25rem;font-size:.9rem;font-family:ui-monospace,Consolas,monospace;word-break:break-word}
  .sweep-rowhead p{margin:0;font-size:.75rem;color:var(--ink-dim)}
  .sweep-rolls{display:grid;grid-template-columns:repeat(var(--cols),minmax(130px,1fr));gap:.7rem}
  .sweep-cell{position:relative;background:var(--panel-2);border:1px solid var(--line);padding:.6rem}
  .roll-idx{position:absolute;top:.45rem;left:.5rem;z-index:1;font-family:ui-monospace,Consolas,monospace;font-size:.62rem;color:var(--amber);background:var(--ground);border:1px solid var(--line);border-radius:4px;padding:0 .3rem}
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
  @media (max-width:760px){.mx-headrow,.mx-row{grid-template-columns:1fr}.mx-headrow .mx-corner,.mx-headrow .mx-col{display:none}.mx-cells{--cols:2!important}.sweep-row{grid-template-columns:1fr}}
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

  {{BODY}}

  <div class="exportbar">
    <div class="tally" id="tally">picks: <b id="ct">0</b></div>
    <div class="tally" id="vct"></div>
    <div class="spacer"></div>
    <button type="button" class="btn ghost" id="clearbtn">reset</button>
    <button type="button" class="btn" id="exportbtn">Export my picks &rarr;</button>
  </div>
  <footer>Verdicts saved in your browser (localStorage). Export to hand them back for the next round.</footer>
</div>

<dialog id="exportdlg">
  <div class="modal-head"><h3>// your picks</h3><button type="button" class="btn ghost" id="copybtn">copy</button></div>
  <div class="modal-body"><p>Copy and paste this back into the chat.</p><textarea id="exporttext" readonly></textarea></div>
</dialog>

<script>
(function(){
  "use strict";
  var KEY="pdoom_style_review_v1",DKEY="pdoom_style_dir_global_v1";
  var SEEDED={{VERDICTS}};
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

  // ---- verdicts (keep / maybe / re-roll) ----
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
  }

  // ---- keyboard navigation ----
  var CELLS=[].slice.call(document.querySelectorAll('.cell'));
  var cur=-1;
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

  // restore + wire winner radios
  document.querySelectorAll('.mx-row').forEach(function(row){
    var sid=row.getAttribute('data-style'), batch=sid.split(':')[0], key=sid.split(':')[1];
    var radio=row.querySelector('input[type=radio]');
    if(st.picks[batch]===key){radio.checked=true;row.classList.add('won');}
    radio.addEventListener('change',function(){
      st.picks[batch]=key;save();
      document.querySelectorAll('.mx-row[data-style^="'+batch+':"]').forEach(function(r){
        r.classList.toggle('won', r.getAttribute('data-style')===sid);
      });
      tally();
    });
  });

  // restore + wire notes, verdicts, click-to-focus on every review cell
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

  document.addEventListener('keydown',function(e){
    var t=e.target,tag=(t.tagName||'').toLowerCase();
    var typing=tag==='input'||tag==='textarea'||t.isContentEditable;
    if(typing){ if(e.key==='Escape'){t.blur();e.preventDefault();} return; }  // never fire shortcuts while typing
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
  tally();

  function labelFor(id){
    var c=document.querySelector('.cell[data-item="'+id.replace(/"/g,'')+'"]');
    return c?c.getAttribute('data-label'):id;
  }
  function buildExport(){
    var L=["# P(Doom)1 style review -- Pip's picks",""];
    var sd=(dir.value||"").trim();
    if(sd){L.push("## Style direction",sd,"");}
    L.push("## Winning styles");
    var pk=Object.keys(st.picks);
    L.push(pk.length?pk.map(function(b){return "- "+b+": **"+st.picks[b]+"**";}).join("\n"):"_(none picked)_");
    L.push("");
    // verdicts grouped keep / maybe / re-roll (with notes inline)
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
    // any remaining notes not attached to a verdict
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
    document.querySelectorAll('.mx-row').forEach(function(r){r.classList.remove('won');var rr=r.querySelector('input[type=radio]');if(rr)rr.checked=false;});
    document.querySelectorAll('.note').forEach(function(n){n.value="";});
    CELLS.forEach(function(c){applyVerdict(c,null);});
    tally();
  });
})();
</script>
"""

if __name__ == "__main__":
    main()
