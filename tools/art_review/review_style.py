#!/usr/bin/env python3
"""review_style -- ONE house style for all internal review/dev HTML tools.

The "warm cozy-grim CRT" language, extracted from the de-facto standard set by
gen_contact_sheet.py / gen_hero_gallery.py (hero_gallery_template.html): dark
warm ground, subtle scanlines + vignette, amber/green accents, monospace chrome,
ASCII-only text ([ESC] close, >>, [OK] -- never emoji).

Convention (tools/art_review/README.md): ALL new internal review sheets build on
this module instead of hand-rolling CSS. It provides:

  * PALETTE / VERDICTS / VERDICT_COLORS / CAT_PALETTE -- the shared vocabulary.
  * BASE_CSS            -- root vars + chrome (header, badges, chips, cells,
                           checkerboard-under-alpha thumbs, scanlines, toast).
  * page(...)           -- standard document wrapper: header block (tool name,
                           date, count badges), intro note, footer, optional
                           verdict toolbar.
  * section(...)        -- collapsible titled section with count tag + accent.
  * image_cell(...)     -- standard image cell: checkerboard thumb, size-variant
                           row, name/sublabel, blurb, expandable prompt, verdict
                           chip slot.
  * verdict machinery   -- per-cell like/dislike/favour/disfavour/promote chips,
                           localStorage persistence, filter-by-verdict, and
                           HIDE-ON-VERDICT ("hide decided") as a first-class
                           behaviour: decided cells leave the live queue so you
                           can clear hundreds without getting tired. Export /
                           import JSON round-trips the flat {rel: [tags]} schema
                           used by analyze_verdicts.py.

Compare-mode hook (issue #745): every cell carries data-rel; a future compare
mode can collect cells marked via a "compare" pin into a side-by-side tray.
See README "compare-and-contrast mode" note. Stdlib only; ASCII only.
"""

import datetime
import html as _html

# ---------------------------------------------------------------- vocabulary

PALETTE = {
    "bg": "#141210",  # deep warm ground
    "bg2": "#1c1916",  # card / tile
    "bg3": "#252019",  # control
    "fg": "#e8e0d2",  # warm off-white text
    "dim": "#9a9081",  # secondary text
    "amber": "#e0a34a",  # primary accent
    "amber2": "#ffcf7a",  # bright accent
    "line": "#3a332a",  # hairline borders
    "green": "#6fae5a",  # positive accent
    "red": "#cc5a4a",  # negative accent
}

VERDICTS = ["like", "dislike", "favour", "disfavour", "promote"]
VERDICT_COLORS = {
    "like": "#6fae5a",
    "dislike": "#cc5a4a",
    "favour": "#e0a34a",
    "disfavour": "#7a7268",
    "promote": "#5a8fc0",
}

# rotating category-pill palette (same list gen_hero_gallery.py uses)
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

# checkerboard-under-alpha ground (matches contact sheet / hero gallery)
CHECKER = "repeating-conic-gradient(#201c17 0% 25%,#2a251e 0% 50%) 50%/16px 16px"

# ---------------------------------------------------------------- CSS

BASE_CSS = (
    """
:root{--bg:#141210;--bg2:#1c1916;--bg3:#252019;--fg:#e8e0d2;--dim:#9a9081;
--amber:#e0a34a;--amber2:#ffcf7a;--line:#3a332a;
--like:#6fae5a;--dislike:#cc5a4a;--favour:#e0a34a;--disfavour:#7a7268;--promote:#5a8fc0;}
*{box-sizing:border-box;}
html,body{margin:0;padding:0;background:var(--bg);color:var(--fg);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;overflow-x:hidden;}
.mono,h1,h2,h3,h4,code{font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;}
/* CRT: subtle scanlines + vignette over everything */
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:995;
background:repeating-linear-gradient(0deg,transparent 0 2px,rgba(0,0,0,.05) 2px 3px);}
body::after{content:"";position:fixed;inset:0;pointer-events:none;z-index:994;
background:radial-gradient(ellipse at 50% 38%,transparent 62%,rgba(10,6,2,.32) 100%);}
header{position:sticky;top:0;z-index:20;background:linear-gradient(180deg,#1c1916,#141210);
border-bottom:1px solid var(--line);padding:12px 18px 10px;box-shadow:0 2px 12px #0008;}
.title-row{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;}
h1{font-size:17px;margin:0;color:var(--amber);letter-spacing:.5px;}
h1 .sub{color:var(--dim);font-weight:normal;font-size:12px;}
.badge{background:var(--bg3);border:1px solid var(--line);color:var(--amber2);
padding:3px 9px;border-radius:12px;font-size:12px;font-family:monospace;}
.controls{display:flex;gap:8px;align-items:center;margin-top:9px;flex-wrap:wrap;}
.row-label{font-size:10px;color:var(--dim);font-family:monospace;text-transform:uppercase;
letter-spacing:1px;margin-right:2px;}
.chip,.vchip,.toggle,.btn{background:var(--bg3);border:1px solid var(--line);color:var(--dim);
padding:5px 10px;border-radius:13px;font-size:12px;cursor:pointer;font-family:monospace;
transition:all .12s;white-space:nowrap;}
.chip:hover,.vchip:hover,.toggle:hover,.btn:hover{border-color:var(--amber);color:var(--fg);}
.chip.on{background:var(--amber);color:#1a1510;border-color:var(--amber);font-weight:600;}
.vchip.on{background:var(--vc);color:#12100c;border-color:var(--vc);font-weight:600;}
.chip-n{opacity:.7;font-size:10px;}
.toggle.on{background:#4a3a1a;border-color:var(--amber2);color:var(--amber2);}
.btn{border-radius:6px;}
.btn.primary{color:var(--amber2);border-color:#5a4a2a;}
main{padding:6px 18px 40px;}
.intro{color:#8a8;max-width:76em;font-size:13px;line-height:1.5;}
.intro .warn,.warn{color:#ca5;}
/* sections */
.rs-section{margin-top:18px;}
.rs-sec-head{cursor:pointer;user-select:none;display:flex;align-items:center;gap:8px;flex-wrap:wrap;
font-size:15px;color:var(--amber2);border-bottom:1px solid var(--line);padding:8px 0 6px;
font-family:monospace;}
.rs-sec-head.accent{color:var(--accent,#ffcf7a);border-bottom-color:var(--accent,#3a332a);}
.caret{display:inline-block;width:12px;color:var(--amber);transition:transform .12s;}
.collapsed .caret{transform:rotate(-90deg);}
.collapsed > .body{display:none;}
.count-tag{color:var(--dim);font-size:11px;font-family:monospace;}
/* cell grid */
.rs-grid{display:flex;flex-wrap:wrap;gap:12px;margin:10px 0 14px;}
.rs-cell{background:var(--bg2);border:1px solid var(--accent,var(--line));border-radius:8px;
padding:10px 10px 8px;width:190px;display:flex;flex-direction:column;position:relative;
transition:border-color .12s,opacity .2s;}
.rs-cell:hover{filter:brightness(1.08);}
.rs-thumb{background:"""
    + CHECKER
    + """;
border-radius:5px;display:flex;align-items:center;justify-content:center;overflow:hidden;
align-self:center;}
.rs-thumb img{display:block;}
.rs-thumb.pix img{image-rendering:pixelated;}
.rs-sizes{display:flex;justify-content:center;align-items:flex-end;gap:6px;margin:6px 0 0;}
.rs-sizes .sz{display:flex;flex-direction:column;align-items:center;gap:2px;}
.rs-sizes .sz span{font-size:8px;color:var(--dim);font-family:monospace;}
.rs-label{font-weight:600;font-size:13px;margin-top:6px;text-align:center;}
.rs-sub{display:block;font-size:10px;color:#8aa;text-align:center;word-break:break-all;}
.rs-blurb{font-size:10px;color:#999;margin:4px 0 0;line-height:1.4;text-align:center;}
.rs-missing{border-color:#cc5a4a;}
.rs-missing .rs-label{color:#e0a0a0;}
.prompt-toggle{font-family:monospace;font-size:9px;color:var(--amber);cursor:pointer;
margin-top:5px;user-select:none;text-align:left;}
.prompt-toggle:hover{color:var(--amber2);}
.prompt-body{display:none;font-family:monospace;font-size:9px;color:var(--dim);line-height:1.45;
margin-top:4px;max-height:150px;overflow:auto;border-top:1px dashed var(--line);padding-top:4px;
white-space:pre-wrap;text-align:left;}
.prompt-body.on{display:block;}
/* verdict chips on a cell */
.rs-vtags{display:flex;flex-wrap:wrap;gap:3px;margin-top:7px;justify-content:center;}
.vtag{font-size:8px;font-family:monospace;padding:2px 5px;border-radius:5px;cursor:pointer;
border:1px solid var(--line);background:transparent;color:var(--dim);text-transform:uppercase;
letter-spacing:.3px;line-height:1;transition:all .1s;}
.vtag:hover{color:var(--fg);border-color:var(--vc);}
.vtag.on{background:var(--vc);color:#12100c;border-color:var(--vc);font-weight:700;}
footer{color:var(--dim);font-size:11px;padding:20px 18px;border-top:1px solid var(--line);
font-family:monospace;line-height:1.6;}
#toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#2a2419;
border:1px solid var(--amber);color:var(--amber2);padding:8px 16px;border-radius:8px;
font-family:monospace;font-size:12px;z-index:1200;opacity:0;transition:opacity .2s;
pointer-events:none;}
#toast.on{opacity:1;}
"""
)

# ---------------------------------------------------------------- verdict JS

VERDICT_JS = r"""
(function(){
const VERDICTS=__RS_VERDICTS__;
const VCOLORS=__RS_VCOLORS__;
const KEY='__RS_KEY__';
const EXPORT_NAME='__RS_EXPORT__';
let V={},storageOK=false;
function loadV(){try{const s=localStorage.getItem(KEY);V=s?JSON.parse(s):{};storageOK=true;}
  catch(e){V={};storageOK=false;}}
function saveV(){if(!storageOK)return;try{localStorage.setItem(KEY,JSON.stringify(V));}catch(e){storageOK=false;}}
function tagsOf(r){return V[r]||[];}
function hasTag(r,t){return tagsOf(r).indexOf(t)>=0;}
function setTag(r,t,on){let a=V[r]?V[r].slice():[];const i=a.indexOf(t);
  if(on&&i<0)a.push(t);else if(!on&&i>=0)a.splice(i,1);
  if(a.length)V[r]=a;else delete V[r];}
let activeVerdicts=new Set(),hideDecided=false;
const cells=Array.from(document.querySelectorAll('.rs-cell[data-rel]'));
function applyFilter(){
  let shown=0,hidden=0;
  for(const c of cells){
    const r=c.dataset.rel,tags=tagsOf(r);let ok=true;
    if(hideDecided&&tags.length)ok=false;
    if(ok&&activeVerdicts.size){let m=false;
      for(const v of activeVerdicts)if(tags.indexOf(v)>=0){m=true;break;}
      if(!m)ok=false;}
    c.style.display=ok?'':'none';if(ok)shown++;else hidden++;
  }
  for(const s of document.querySelectorAll('.rs-section')){
    const any=Array.from(s.querySelectorAll('.rs-cell')).some(x=>x.style.display!=='none');
    s.style.display=any?'':'none';}
  const sh=document.getElementById('rs-shown');if(sh)sh.textContent=shown;
  const hd=document.getElementById('rs-hiddenn');if(hd)hd.textContent=hidden;
}
function refreshCounts(){
  const c={};for(const v of VERDICTS)c[v]=0;let any=0;
  for(const r in V){for(const t of V[r])if(c[t]!==undefined)c[t]++;any++;}
  for(const v of VERDICTS){const el=document.getElementById('rs-vcount-'+v);
    if(el)el.textContent=c[v];}
  const tg=document.getElementById('rs-taggedn');if(tg)tg.textContent=any;
}
function syncCell(c){const r=c.dataset.rel;
  for(const b of c.querySelectorAll('.vtag'))b.classList.toggle('on',hasTag(r,b.dataset.v));}
let toastT=null;
function toast(msg){const el=document.getElementById('toast');if(!el)return;
  el.textContent=msg;el.classList.add('on');
  clearTimeout(toastT);toastT=setTimeout(()=>el.classList.remove('on'),1800);}
function download(name,text,type){const blob=new Blob([text],{type:type||'text/plain'});
  const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;
  a.download=name;document.body.appendChild(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);}
window.addEventListener('DOMContentLoaded',()=>{
  loadV();
  for(const c of cells){
    const r=c.dataset.rel;const vt=c.querySelector('.rs-vtags');if(!vt)continue;
    for(const v of VERDICTS){
      const b=document.createElement('button');b.className='vtag';b.dataset.v=v;b.textContent=v;
      b.style.setProperty('--vc',VCOLORS[v]);
      if(hasTag(r,v))b.classList.add('on');
      b.onclick=e=>{e.stopPropagation();const on=!hasTag(r,v);setTag(r,v,on);
        b.classList.toggle('on',on);saveV();refreshCounts();
        if(hideDecided||activeVerdicts.size)applyFilter();};
      vt.appendChild(b);
    }
  }
  for(const vc of document.querySelectorAll('.vchip[data-v]')){
    vc.onclick=()=>{const v=vc.dataset.v;
      if(activeVerdicts.has(v)){activeVerdicts.delete(v);vc.classList.remove('on');}
      else{activeVerdicts.add(v);vc.classList.add('on');}applyFilter();};}
  const hb=document.getElementById('rs-hidedecided');
  if(hb)hb.onclick=()=>{hideDecided=!hideDecided;hb.classList.toggle('on',hideDecided);applyFilter();};
  const ex=document.getElementById('rs-export');
  if(ex)ex.onclick=()=>{download(EXPORT_NAME,JSON.stringify(V,null,2),'application/json');
    toast('Exported '+EXPORT_NAME);};
  const ib=document.getElementById('rs-import'),inf=document.getElementById('rs-importfile');
  if(ib&&inf){ib.onclick=()=>inf.click();
    inf.addEventListener('change',e=>{const f=e.target.files[0];if(!f)return;
      const rd=new FileReader();
      rd.onload=()=>{try{const obj=JSON.parse(rd.result);
        if(typeof obj!=='object'||Array.isArray(obj))throw 0;
        V=obj;saveV();for(const c of cells)syncCell(c);
        refreshCounts();applyFilter();toast('Imported verdicts');
      }catch(err){toast('Import failed -- not a valid verdicts JSON');}};
      rd.readAsText(f);e.target.value='';});}
  const sw=document.getElementById('rs-storewarn');
  if(sw&&!storageOK)sw.style.display='inline';
  refreshCounts();applyFilter();
});
})();
"""


def _verdict_toolbar():
    vchips = "".join(
        f'<button class="vchip" data-v="{v}" style="--vc:{VERDICT_COLORS[v]}">{v} '
        f'<span class="chip-n" id="rs-vcount-{v}">0</span></button>'
        for v in VERDICTS
    )
    return (
        '<div class="controls">'
        '<span class="row-label">verdict</span>' + vchips + " "
        '<button class="toggle" id="rs-hidedecided">hide decided '
        '(<span id="rs-hiddenn">0</span> hidden)</button> '
        '<button class="btn" id="rs-export">export JSON</button>'
        '<button class="btn primary" id="rs-import">import JSON</button>'
        '<input type="file" id="rs-importfile" accept="application/json,.json" style="display:none">'
        "</div>"
    )


# ---------------------------------------------------------------- components


def esc(s):
    """HTML-escape (accepts None)."""
    return _html.escape("" if s is None else str(s), quote=True)


def section(title, body_html, count=None, accent=None, head_extra=""):
    """Collapsible titled section. accent = CSS colour for the heading rule."""
    style = f' style="--accent:{accent}"' if accent else ""
    cls = "rs-sec-head accent" if accent else "rs-sec-head"
    count_tag = f' <span class="count-tag">{count}</span>' if count is not None else ""
    return (
        f'<section class="rs-section"{style}>'
        f'<div class="{cls}" onclick="this.parentNode.classList.toggle(\'collapsed\')">'
        f'<span class="caret">v</span>{esc(title)}{count_tag}{head_extra}</div>'
        f'<div class="body">{body_html}</div></section>'
    )


def image_cell(
    src,
    label,
    sublabel="",
    size_row=(),
    blurb="",
    prompt="",
    rel=None,
    accent=None,
    img_px=128,
    pixelated=False,
    missing=False,
):
    """Standard image cell.

    src       -- main image URL / data URI (checkerboard shows under alpha).
    size_row  -- iterable of (px, src) readability variants, rendered smallest-last.
    prompt    -- expandable generating-prompt text (house pattern).
    rel       -- repo-relative path: verdict-chip slot + data-rel (compare hook #745).
    accent    -- border colour (e.g. valence colour).
    """
    cls = "rs-cell" + (" rs-missing" if missing else "")
    style = f' style="--accent:{accent}"' if accent else ""
    relattr = f' data-rel="{esc(rel)}"' if rel else ""
    pix = " pix" if pixelated else ""
    parts = [f'<div class="{cls}"{style}{relattr}>']
    if src:
        parts.append(
            f'<div class="rs-thumb{pix}"><img src="{src}" width="{img_px}" height="{img_px}" '
            f'alt="{esc(label)}"></div>'
        )
    else:
        parts.append(
            f'<div class="rs-thumb{pix}" style="width:{img_px}px;height:{img_px}px"></div>'
        )
    if size_row:
        szs = "".join(
            f'<div class="sz"><img src="{s}" width="{px}" height="{px}" alt="{px}px">'
            f"<span>{px}</span></div>"
            for px, s in size_row
        )
        parts.append(f'<div class="rs-sizes">{szs}</div>')
    parts.append(f'<div class="rs-label">{esc(label)}</div>')
    if sublabel:
        parts.append(f'<code class="rs-sub">{esc(sublabel)}</code>')
    if blurb:
        parts.append(f'<p class="rs-blurb">{esc(blurb)}</p>')
    if prompt:
        parts.append(
            '<div class="prompt-toggle" onclick="var b=this.nextElementSibling;'
            "var on=b.classList.toggle('on');"
            "this.textContent=on?'prompt [-]':'prompt [+]'\">prompt [+]</div>"
            f'<div class="prompt-body">{esc(prompt)}</div>'
        )
    if rel:
        parts.append('<div class="rs-vtags"></div>')
    parts.append("</div>")
    return "".join(parts)


def page(
    tool_name,
    subtitle,
    body_html,
    badges=(),
    intro_html="",
    extra_css="",
    extra_js="",
    verdict_key=None,
    export_name="verdicts.json",
    footer_note="",
    date=None,
):
    """Full ASCII HTML document in the house style.

    badges      -- iterable of (label, value) shown in the header count row.
    verdict_key -- localStorage key (e.g. "quirk:verdicts"); enables the verdict
                   toolbar + per-cell chips + hide-on-verdict + export/import.
    """
    import json as _json

    date = date or datetime.date.today().isoformat()
    badge_html = "".join(f'<span class="badge">{esc(k)} {esc(v)}</span>' for k, v in badges)
    verdict_bar = ""
    verdict_js = ""
    store_warn = ""
    if verdict_key:
        verdict_bar = _verdict_toolbar()
        store_warn = (
            '<span class="badge" id="rs-storewarn" style="display:none;color:#d88">'
            "localStorage off -- verdicts wont persist (use Export)</span>"
        )
        verdict_js = (
            VERDICT_JS.replace("__RS_VERDICTS__", _json.dumps(VERDICTS))
            .replace("__RS_VCOLORS__", _json.dumps(VERDICT_COLORS))
            .replace("__RS_KEY__", verdict_key)
            .replace("__RS_EXPORT__", export_name)
        )
    intro = f'<p class="intro">{intro_html}</p>' if intro_html else ""
    tagged_badge = (
        '<span class="badge">shown <span id="rs-shown">-</span></span>'
        '<span class="badge">tagged <span id="rs-taggedn">0</span></span>'
        if verdict_key
        else ""
    )
    footer_bits = [
        "Local review sheet -- regenerable artifact, not committed (tools/art_review/README.md)."
    ]
    if verdict_key:
        footer_bits.append(
            "Verdicts persist to this browser's localStorage under key "
            f'"{verdict_key}"; hide decided shrinks the live queue as you triage; '
            "export JSON to make decisions durable."
        )
    if footer_note:
        footer_bits.append(footer_note)
    scripts = ""
    if verdict_js:
        scripts += f"<script>{verdict_js}</script>"
    if extra_js:
        scripts += f"<script>{extra_js}</script>"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>P(Doom)1 -- {esc(tool_name)}</title>
<style>{BASE_CSS}{extra_css}</style>
</head>
<body>
<header>
  <div class="title-row">
    <h1>P(Doom)1 {esc(tool_name)} <span class="sub">// {esc(subtitle)}</span></h1>
    <span class="badge">{esc(date)}</span>
    {badge_html}{tagged_badge}{store_warn}
  </div>
  {verdict_bar}
</header>
<main>
{intro}
{body_html}
</main>
<footer>
  {' '.join(footer_bits)}
</footer>
<div id="toast"></div>
{scripts}
</body>
</html>
"""


def write_ascii(path, html_text):
    """Write the sheet, enforcing the repo ASCII-only rule (issue #744)."""
    bad = sorted({c for c in html_text if ord(c) > 127})
    if bad:
        raise ValueError(f"non-ascii chars in generated HTML: {bad!r}")
    with open(path, "w", encoding="ascii", newline="\n") as fh:
        fh.write(html_text)
