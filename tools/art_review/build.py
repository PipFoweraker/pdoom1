#!/usr/bin/env python3
"""Build the P(Doom)1 style-review tool: a self-contained HTML page from
manifest.json + the committed PNGs. Rows = style directions, columns = subjects,
so a whole style reads across many subjects at once. Plus an era-ladder strip.
Pick a winner per matrix, note per cell, jot global style dials, and Export the
verdicts to paste back for the next generation round.

Convention for image files (relative to <repo>/<image_root>/<batch.dir>/):
  matrix cell : "<style.key>__<subject.key>.png"
  ladder step : "<step.key>.png"
Missing files render as a 'pending' placeholder (regenerate + re-run to fill).

Usage:  python tools/art_review/build.py   ->  writes tools/art_review/style_review.html
"""
import base64
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
MANIFEST = HERE / "manifest.json"
OUT = HERE / "style_review.html"


def datauri(path: pathlib.Path):
    if not path.is_file():
        return None
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def cell(item_id, label, uri):
    if uri:
        img = f'<div class="stage"><img src="{uri}" alt="{esc(label)}"></div>'
    else:
        img = '<div class="stage pending"><span>pending<br>regen &amp; rebuild</span></div>'
    return f"""
      <div class="cell" data-item="{item_id}" data-label="{esc(label)}">
        {img}
        <input type="text" class="note" placeholder="note..." aria-label="Note for {esc(label)}">
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
        img = (
            f'<div class="stage"><img src="{uri}" alt="{esc(st["label"])}"></div>'
            if uri
            else '<div class="stage pending"><span>pending</span></div>'
        )
        steps.append(
            f"""
        <div class="cell ladder-step" data-item="{b['id']}:{st['key']}" data-label="{esc(st['label'])}">
          <div class="era-idx">{i+1}</div>
          {img}
          <h4>{esc(st['label'])}</h4><p class="era-note">{esc(st['note'])}</p>
          <input type="text" class="note" placeholder="note..." aria-label="Note for {esc(st['label'])}">
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
        img = (
            f'<div class="stage"><img src="{uri}" alt="{esc(it["label"])}"></div>'
            if uri
            else '<div class="stage pending"><span>pending</span></div>'
        )
        cells.append(
            f"""
      <div class="cell" data-item="{b['id']}:{it['key']}" data-label="{esc(it['label'])}">
        {img}
        <h4>{esc(it['label'])}</h4>
        <input type="text" class="note" placeholder="note..." aria-label="Note for {esc(it['label'])}">
      </div>"""
        )
    return f"""
    <section class="batch" data-batch="{b['id']}">
      <div class="section-label">{esc(b['title'])}</div>
      <p class="batch-note">{esc(b['note'])}</p>
      <div class="gallery">{''.join(cells)}</div>
    </section>"""


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
    body = "\n".join(sections)

    html = (
        TEMPLATE.replace("{{TITLE}}", esc(m["title"]))
        .replace("{{SUBTITLE}}", esc(m["subtitle"]))
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
  .cell{display:flex;flex-direction:column;gap:.4rem}
  .stage{background-color:var(--checker-a);background-image:linear-gradient(45deg,var(--checker-b) 25%,transparent 25%),linear-gradient(-45deg,var(--checker-b) 25%,transparent 25%),linear-gradient(45deg,transparent 75%,var(--checker-b) 75%),linear-gradient(-45deg,transparent 75%,var(--checker-b) 75%);background-size:14px 14px;background-position:0 0,0 7px,7px -7px,-7px 0;border:1px solid var(--line);border-radius:8px;padding:.7rem;display:grid;place-items:center;min-height:130px}
  .stage img{width:auto;max-height:150px}
  .stage.pending{color:var(--ink-faint);font-family:ui-monospace,Consolas,monospace;font-size:.7rem;text-align:center}
  .note{width:100%;background:var(--field);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:.35rem .5rem;font-size:.76rem;font-family:ui-sans-serif,system-ui,sans-serif}
  .note:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
  /* ladder */
  .ladder-scroll{overflow-x:auto}
  .ladder{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(190px,1fr);gap:.9rem;min-width:min-content}
  .ladder-step{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:1rem;position:relative}
  .era-idx{position:absolute;top:.6rem;left:.7rem;font-family:ui-monospace,Consolas,monospace;font-size:.7rem;color:var(--amber);border:1px solid var(--line);border-radius:50%;width:1.4rem;height:1.4rem;display:grid;place-items:center;background:var(--ground)}
  .ladder-step h4{margin:.5rem 0 .1rem;font-size:.95rem}
  .era-note{margin:0 0 .5rem;font-size:.76rem;color:var(--ink-dim)}
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
  @media (prefers-reduced-motion:reduce){*{transition:none!important}}
  @media (max-width:760px){.mx-headrow,.mx-row{grid-template-columns:1fr}.mx-headrow .mx-corner,.mx-headrow .mx-col{display:none}.mx-cells{--cols:2!important}}
</style>

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
  var st={picks:{},notes:{}};
  try{st=Object.assign({picks:{},notes:{}},JSON.parse(localStorage.getItem(KEY)||"{}"));}catch(e){}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(st));}catch(e){}}

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
  // restore + wire notes
  document.querySelectorAll('.cell').forEach(function(c){
    var id=c.getAttribute('data-item'),inp=c.querySelector('.note');
    if(!inp)return;
    if(st.notes[id])inp.value=st.notes[id];
    inp.addEventListener('input',function(e){st.notes[id]=e.target.value;if(!e.target.value)delete st.notes[id];save();});
  });
  var dir=document.getElementById('styledir');
  try{dir.value=localStorage.getItem(DKEY)||"";}catch(e){}
  dir.addEventListener('input',function(e){try{localStorage.setItem(DKEY,e.target.value);}catch(x){}});

  function tally(){document.getElementById('ct').textContent=Object.keys(st.picks).length;}
  tally();

  function buildExport(){
    var L=["# P(Doom)1 style review -- Pip's picks",""];
    var sd=(dir.value||"").trim();
    if(sd){L.push("## Style direction",sd,"");}
    L.push("## Winning styles");
    var pk=Object.keys(st.picks);
    L.push(pk.length?pk.map(function(b){return "- "+b+": **"+st.picks[b]+"**";}).join("\n"):"_(none picked)_");
    L.push("");
    var ns=Object.keys(st.notes);
    if(ns.length){L.push("## Notes");ns.forEach(function(id){
      var c=document.querySelector('.cell[data-item="'+id.replace(/"/g,'')+'"]');
      var label=c?c.getAttribute('data-label'):id;
      L.push("- "+label+" ("+id+"): "+st.notes[id]);
    });L.push("");}
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
    if(!confirm("Clear all picks and notes?"))return;
    st={picks:{},notes:{}};save();
    document.querySelectorAll('.mx-row').forEach(function(r){r.classList.remove('won');var rr=r.querySelector('input[type=radio]');if(rr)rr.checked=false;});
    document.querySelectorAll('.note').forEach(function(n){n.value="";});
    tally();
  });
})();
</script>
"""

if __name__ == "__main__":
    main()
