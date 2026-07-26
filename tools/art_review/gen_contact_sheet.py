#!/usr/bin/env python3
"""Generate a self-contained pixellab contact-sheet / triage HTML. Local review tool."""

import collections
import json
import os
import sys

# shared verdict vocabulary -- review_style.py is the SSOT (same dir as this script,
# which sys.path[0] covers when run as a script)
from review_style import VERDICT_COLORS, VERDICTS

# Repo-relative: this script lives at <repo>/tools/art_review/ , so the repo
# root is three levels up. Override art_source with argv[1] if given.
_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))

ART_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "art_source")
OUT = os.path.join(ART_DIR, "pixellab_contact_sheet.html")
EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def categorize(rel_parts):
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
    n = fname.lower()
    if "cat" in n:
        return "cats"
    if "tileset" in n or "floor_" in n or "wall_" in n:
        return "tilesets"
    if "hat" in n or "silhouette" in n:
        return "cosmetics"
    return "characters"


CATS = ["characters", "cats", "props", "tilesets", "cosmetics", "other"]

records = []
cat_counts = collections.Counter()
run_counts = collections.Counter()
run_cat_counts = collections.defaultdict(collections.Counter)

runs = sorted(
    d
    for d in os.listdir(ART_DIR)
    if d.startswith("pixellab_") and os.path.isdir(os.path.join(ART_DIR, d))
)

for run in runs:
    run_root = os.path.join(ART_DIR, run)
    for dirpath, dirnames, filenames in os.walk(run_root):
        dirnames.sort()
        for fn in sorted(filenames):
            if not fn.lower().endswith(EXTS):
                continue
            abs_path = os.path.join(dirpath, fn)
            rel = os.path.relpath(abs_path, ART_DIR).replace("\\", "/")
            sub = os.path.relpath(dirpath, run_root).replace("\\", "/")
            dir_segs = [] if sub == "." else sub.split("/")
            cat = categorize(dir_segs) if dir_segs else None
            if cat is None:
                cat = categorize_by_name(fn)
            if cat not in CATS:
                cat = "other"
            subfolder = "/".join(dir_segs) if dir_segs else "(root)"
            records.append({"rel": rel, "run": run, "cat": cat, "sub": subfolder, "fn": fn})
            cat_counts[cat] += 1
            run_counts[run] += 1
            run_cat_counts[run][cat] += 1

total = len(records)

print("TOTAL:", total)
print("BY CATEGORY:")
for c in CATS:
    if cat_counts[c]:
        print(f"  {cat_counts[c]:5d}  {c}")
print("BY RUN:")
for r in runs:
    print(f"  {run_counts[r]:5d}  {r}")
    for c in CATS:
        if run_cat_counts[r][c]:
            print(f"          {run_cat_counts[r][c]:4d}  {c}")

CAT_COLORS = {
    "characters": "#e0a34a",
    "cats": "#c98b3f",
    "props": "#8fae6b",
    "tilesets": "#6ba3b0",
    "cosmetics": "#b57fb0",
    "other": "#8a8375",
}
# VERDICTS / VERDICT_COLORS imported from review_style (shared vocabulary)

data = [
    {"r": rec["rel"], "u": rec["run"], "c": rec["cat"], "s": rec["sub"], "f": rec["fn"]}
    for rec in records
]
data_json = json.dumps(data, separators=(",", ":"))

chips = "".join(
    f'<button class="chip" data-cat="{c}">{c} <span class="chip-n">{cat_counts[c]}</span></button>'
    for c in CATS
    if cat_counts[c]
)
vchips = "".join(
    f'<button class="vchip" data-v="{v}" style="--vc:{VERDICT_COLORS[v]}">{v} '
    f'<span class="chip-n" id="vcount-{v}">0</span></button>'
    for v in VERDICTS
)

css = """
:root{--bg:#141210;--bg2:#1c1916;--bg3:#252019;--fg:#e8e0d2;--dim:#9a9081;
--amber:#e0a34a;--amber2:#ffcf7a;--line:#3a332a;
--like:#6fae5a;--dislike:#cc5a4a;--favour:#e0a34a;--disfavour:#7a7268;--promote:#5a8fc0;}
*{box-sizing:border-box;}
html,body{margin:0;padding:0;background:var(--bg);color:var(--fg);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;overflow-x:hidden;}
.mono,h1,h2{font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;}
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
input[type=search]{background:var(--bg3);border:1px solid var(--line);color:var(--fg);
padding:6px 10px;border-radius:6px;font-size:13px;min-width:200px;flex:0 1 300px;font-family:monospace;}
input[type=search]:focus{outline:none;border-color:var(--amber);}
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
main{padding:6px 18px 90px;}
.run-sec{margin-top:16px;}
.run-head,.cat-head{cursor:pointer;user-select:none;display:flex;align-items:center;gap:8px;flex-wrap:wrap;}
.run-head{font-size:15px;color:var(--amber2);border-bottom:1px solid var(--line);padding:8px 0 6px;margin-top:8px;}
.cat-head{font-size:12px;color:var(--dim);padding:8px 0 4px;margin-left:4px;text-transform:uppercase;letter-spacing:1px;}
.caret{display:inline-block;width:12px;color:var(--amber);transition:transform .12s;}
.collapsed .caret{transform:rotate(-90deg);}
.collapsed > .body{display:none;}
.count-tag{color:var(--dim);font-size:11px;font-family:monospace;}
.selall{font-size:10px;color:var(--dim);background:var(--bg3);border:1px solid var(--line);
border-radius:5px;padding:2px 7px;cursor:pointer;font-family:monospace;}
.selall:hover{border-color:var(--amber);color:var(--fg);}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(132px,1fr));gap:10px;margin:6px 0 14px;}
.tile{background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:8px 8px 7px;
position:relative;display:flex;flex-direction:column;transition:border-color .12s;}
.tile:hover{border-color:#5a5040;}
.tile.sel{border-color:var(--amber2);box-shadow:0 0 0 1px var(--amber2) inset;}
.thumb-wrap{background:repeating-conic-gradient(#201c17 0% 25%,#2a251e 0% 50%) 50%/16px 16px;
border-radius:5px;aspect-ratio:1;display:flex;align-items:center;justify-content:center;overflow:hidden;cursor:zoom-in;}
.thumb-wrap img{max-width:100%;max-height:100%;image-rendering:pixelated;image-rendering:crisp-edges;}
.selbox{position:absolute;top:6px;left:6px;width:20px;height:20px;cursor:pointer;z-index:2;
accent-color:var(--amber);margin:0;}
.fn{font-family:monospace;font-size:10px;color:var(--fg);margin-top:6px;word-break:break-all;line-height:1.3;}
.meta{font-size:9px;color:var(--dim);margin-top:2px;font-family:monospace;}
.cat-pill{display:inline-block;font-size:8px;padding:1px 5px;border-radius:6px;color:#15110b;
font-weight:700;text-transform:uppercase;letter-spacing:.5px;}
.vtags{display:flex;flex-wrap:wrap;gap:3px;margin-top:6px;}
.vtag{font-size:8px;font-family:monospace;padding:2px 5px;border-radius:5px;cursor:pointer;
border:1px solid var(--line);background:transparent;color:var(--dim);text-transform:uppercase;
letter-spacing:.3px;line-height:1;transition:all .1s;}
.vtag:hover{color:var(--fg);border-color:var(--vc);}
.vtag.on{background:var(--vc);color:#12100c;border-color:var(--vc);font-weight:700;}
.empty{color:var(--dim);font-style:italic;padding:20px;text-align:center;}
footer{color:var(--dim);font-size:11px;padding:20px 18px;border-top:1px solid var(--line);font-family:monospace;line-height:1.6;}
.bulkbar{position:fixed;left:0;right:0;bottom:0;z-index:30;background:linear-gradient(0deg,#221d16,#1a1611);
border-top:1px solid #5a4a2a;padding:10px 18px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;
box-shadow:0 -3px 14px #000a;transform:translateY(110%);transition:transform .18s;}
.bulkbar.on{transform:translateY(0);}
.bulkbar .selcount{color:var(--amber2);font-family:monospace;font-size:13px;font-weight:600;}
.bulkbar .sep{color:var(--line);}
.bulk-add,.bulk-del{border-radius:6px;font-size:11px;padding:5px 9px;border:1px solid var(--line);
background:var(--bg3);color:var(--dim);cursor:pointer;font-family:monospace;}
.bulk-add{--vc:#888;}
.bulk-add:hover{background:var(--vc);color:#12100c;border-color:var(--vc);}
.bulk-del:hover{background:#3a2020;border-color:#cc5a4a;color:#e8b0a8;}
.lightbox{position:fixed;inset:0;background:#000d;z-index:100;display:none;align-items:center;
justify-content:center;flex-direction:column;gap:12px;cursor:zoom-out;}
.lightbox.on{display:flex;}
.lightbox img{max-width:80vw;max-height:72vh;image-rendering:pixelated;
background:repeating-conic-gradient(#201c17 0% 25%,#2a251e 0% 50%) 50%/24px 24px;border:1px solid var(--line);}
.lightbox .lbcap{color:var(--fg);font-family:monospace;font-size:13px;text-align:center;padding:0 20px;}
#toast{position:fixed;bottom:70px;left:50%;transform:translateX(-50%);background:#2a2419;
border:1px solid var(--amber);color:var(--amber2);padding:8px 16px;border-radius:8px;
font-family:monospace;font-size:12px;z-index:200;opacity:0;transition:opacity .2s;pointer-events:none;}
#toast.on{opacity:1;}
"""

js = r"""
const DATA=__DATA__;
const CATCOLORS=__CATCOLORS__;
const VERDICTS=__VERDICTS__;
const VCOLORS=__VCOLORS__;
const KV='pcs:verdicts';   // {rel:[tags]}
let V={};                  // in-memory verdict map
let storageOK=false;
function loadV(){try{const s=localStorage.getItem(KV);V=s?JSON.parse(s):{};storageOK=true;}
  catch(e){V={};storageOK=false;}}
function saveV(){if(!storageOK)return;try{localStorage.setItem(KV,JSON.stringify(V));}catch(e){storageOK=false;}}
function tagsOf(r){return V[r]||[];}
function hasTag(r,t){return tagsOf(r).indexOf(t)>=0;}
function setTag(r,t,on){let a=V[r]?V[r].slice():[];const i=a.indexOf(t);
  if(on&&i<0)a.push(t);else if(!on&&i>=0)a.splice(i,1);
  if(a.length)V[r]=a;else delete V[r];}

let activeCats=new Set(), activeVerdicts=new Set(), query='';
const selected=new Set();
let lastClickedIdx=null;
const tileByRel={}; let orderedRels=[];

function build(){
  const runs={};
  for(const d of DATA){(runs[d.u]=runs[d.u]||{});(runs[d.u][d.c]=runs[d.u][d.c]||[]).push(d);}
  const main=document.getElementById('main');
  for(const run of Object.keys(runs).sort()){
    const sec=document.createElement('section');sec.className='run-sec';
    const rc=Object.values(runs[run]).reduce((a,b)=>a+b.length,0);
    const rh=document.createElement('div');rh.className='run-head';
    rh.innerHTML=`<span class="caret">v</span><span class="mono">${run}</span> <span class="count-tag">${rc}</span>`;
    const selBtn=document.createElement('span');selBtn.className='selall';selBtn.textContent='select group';
    rh.appendChild(selBtn);
    const rbody=document.createElement('div');rbody.className='body';
    rh.addEventListener('click',e=>{if(e.target===selBtn)return;sec.classList.toggle('collapsed');});
    const groupRels=[];
    sec.appendChild(rh);sec.appendChild(rbody);
    for(const cat of Object.keys(runs[run]).sort()){
      const cwrap=document.createElement('div');cwrap.className='cat-sec';cwrap.dataset.cat=cat;
      const ch=document.createElement('div');ch.className='cat-head';
      ch.innerHTML=`<span class="caret">v</span>${cat} <span class="count-tag">${runs[run][cat].length}</span>`;
      const cSel=document.createElement('span');cSel.className='selall';cSel.textContent='select';
      ch.appendChild(cSel);
      const cbody=document.createElement('div');cbody.className='body grid';
      ch.addEventListener('click',e=>{if(e.target===cSel)return;cwrap.classList.toggle('collapsed');});
      const catRels=[];
      for(const d of runs[run][cat]){const t=tile(d);cbody.appendChild(t);catRels.push(d.r);groupRels.push(d.r);}
      cSel.onclick=e=>{e.stopPropagation();selectRels(catRels);};
      cwrap.appendChild(ch);cwrap.appendChild(cbody);rbody.appendChild(cwrap);
    }
    selBtn.onclick=e=>{e.stopPropagation();selectRels(groupRels);};
    main.appendChild(sec);
  }
}

function tile(d){
  const t=document.createElement('div');t.className='tile';t.dataset.rel=d.r;
  t.dataset.fn=d.f.toLowerCase();t.dataset.cat=d.c;t.dataset.sub=d.s.toLowerCase();
  const col=CATCOLORS[d.c]||'#888';
  t.innerHTML=`
    <input type="checkbox" class="selbox" title="select">
    <div class="thumb-wrap"><img loading="lazy" src="${enc(d.r)}" alt="${esc(d.f)}"></div>
    <div class="fn">${esc(d.f)}</div>
    <div class="meta"><span class="cat-pill" style="background:${col}">${d.c}</span> ${esc(d.s)}</div>
    <div class="vtags"></div>`;
  const vt=t.querySelector('.vtags');
  for(const v of VERDICTS){
    const b=document.createElement('button');b.className='vtag';b.dataset.v=v;b.textContent=v;
    b.style.setProperty('--vc',VCOLORS[v]);
    if(hasTag(d.r,v))b.classList.add('on');
    b.onclick=e=>{e.stopPropagation();const on=!hasTag(d.r,v);setTag(d.r,v,on);
      b.classList.toggle('on',on);saveV();refreshCounts();if(activeVerdicts.size)applyFilter();};
    vt.appendChild(b);
  }
  const cb=t.querySelector('.selbox');
  cb.addEventListener('click',e=>{e.stopPropagation();onSelClick(d.r,e.shiftKey,cb.checked);});
  t.querySelector('img').onclick=e=>{e.stopPropagation();openLB(d);};
  tileByRel[d.r]=t;
  return t;
}

function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function enc(s){return s.split('/').map(encodeURIComponent).join('/');}

// ---- selection ----
function onSelClick(rel,shift,checked){
  const idx=orderedRels.indexOf(rel);
  if(shift&&lastClickedIdx!==null){
    const [a,b]=[Math.min(lastClickedIdx,idx),Math.max(lastClickedIdx,idx)];
    for(let i=a;i<=b;i++){const r=orderedRels[i];const tt=tileByRel[r];
      if(tt.style.display==='none')continue; setSel(r,checked);}
  }else{setSel(rel,checked);}
  lastClickedIdx=idx;updateSelUI();
}
function setSel(rel,on){const t=tileByRel[rel];if(!t)return;
  if(on){selected.add(rel);t.classList.add('sel');}else{selected.delete(rel);t.classList.remove('sel');}
  const cb=t.querySelector('.selbox');if(cb)cb.checked=on;}
function selectRels(rels){const vis=rels.filter(r=>tileByRel[r].style.display!=='none');
  const allSel=vis.every(r=>selected.has(r));
  for(const r of vis)setSel(r,!allSel);updateSelUI();}
function selectAllVisible(){const vis=orderedRels.filter(r=>tileByRel[r].style.display!=='none');
  const allSel=vis.length&&vis.every(r=>selected.has(r));
  for(const r of vis)setSel(r,!allSel);updateSelUI();}
function clearSel(){for(const r of[...selected])setSel(r,false);updateSelUI();}
function updateSelUI(){const n=selected.size;
  document.getElementById('selcount').textContent=n;
  document.getElementById('bulkbar').classList.toggle('on',n>0);}

// ---- bulk verdict ----
function bulkApply(v,on){for(const r of selected){setTag(r,v,on);
  const t=tileByRel[r];const b=t.querySelector(`.vtag[data-v="${v}"]`);if(b)b.classList.toggle('on',on);}
  saveV();refreshCounts();if(activeVerdicts.size)applyFilter();
  toast(`${on?'Set':'Removed'} ${v} on ${selected.size} sprite(s)`);}

// ---- filtering ----
function applyFilter(){
  let shown=0;
  for(const r of orderedRels){
    const t=tileByRel[r];let ok=true;
    if(activeCats.size&&!activeCats.has(t.dataset.cat))ok=false;
    if(ok&&query){const hay=t.dataset.fn+' '+t.dataset.cat+' '+t.dataset.sub;if(!hay.includes(query))ok=false;}
    if(ok&&activeVerdicts.size){const tags=tagsOf(r);
      let m=false;for(const v of activeVerdicts)if(tags.indexOf(v)>=0){m=true;break;}if(!m)ok=false;}
    t.style.display=ok?'':'none';if(ok)shown++;
  }
  for(const cs of document.querySelectorAll('.cat-sec')){
    const any=[...cs.querySelectorAll('.tile')].some(x=>x.style.display!=='none');cs.style.display=any?'':'none';}
  for(const rs of document.querySelectorAll('.run-sec')){
    const any=[...rs.querySelectorAll('.cat-sec')].some(c=>c.style.display!=='none');rs.style.display=any?'':'none';}
  document.getElementById('shown').textContent=shown;
}
function refreshCounts(){
  const c={};for(const v of VERDICTS)c[v]=0;let any=0;
  for(const r in V){for(const t of V[r])if(c[t]!==undefined)c[t]++;any++;}
  for(const v of VERDICTS)document.getElementById('vcount-'+v).textContent=c[v];
  document.getElementById('taggedn').textContent=any;
}

// ---- export / import ----
function download(name,text,type){const blob=new Blob([text],{type:type||'text/plain'});
  const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;
  document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function exportJSON(){download('pixellab_verdicts.json',JSON.stringify(V,null,2),'application/json');
  toast('Exported JSON');}
function exportCSV(){let rows=['relative_path,tags'];
  for(const r of orderedRels){const tg=tagsOf(r);if(tg.length)rows.push(`"${r}","${tg.join(';')}"`);}
  download('pixellab_verdicts.csv',rows.join('\n'),'text/csv');toast('Exported CSV');}
function copyList(v){const rels=orderedRels.filter(r=>hasTag(r,v));
  const text=rels.join('\n');
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(()=>toast(`Copied ${rels.length} ${v} path(s)`),
      ()=>fallbackCopy(text,rels.length,v));
  }else fallbackCopy(text,rels.length,v);}
function fallbackCopy(text,n,v){const ta=document.createElement('textarea');ta.value=text;
  ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();
  let ok=false;try{ok=document.execCommand('copy');}catch(e){}ta.remove();
  toast(ok?`Copied ${n} ${v} path(s)`:`Copy blocked -- see console`);if(!ok)console.log(text);}
function importJSON(file){const rd=new FileReader();
  rd.onload=()=>{try{const obj=JSON.parse(rd.result);
    if(typeof obj!=='object'||Array.isArray(obj))throw 0;
    V=obj;saveV();
    for(const r of orderedRels){const t=tileByRel[r];
      for(const b of t.querySelectorAll('.vtag'))b.classList.toggle('on',hasTag(r,b.dataset.v));}
    refreshCounts();applyFilter();toast('Imported verdicts');
  }catch(e){toast('Import failed -- not a valid verdicts JSON');}};
  rd.readAsText(file);}

// ---- misc ----
function openLB(d){const lb=document.getElementById('lb');lb.querySelector('img').src=enc(d.r);
  lb.querySelector('.lbcap').textContent=`${d.f}  --  ${d.u}/${d.s}`;lb.classList.add('on');}
let toastT=null;
function toast(msg){const el=document.getElementById('toast');el.textContent=msg;el.classList.add('on');
  clearTimeout(toastT);toastT=setTimeout(()=>el.classList.remove('on'),1800);}

window.addEventListener('DOMContentLoaded',()=>{
  loadV();orderedRels=DATA.map(d=>d.r);build();
  document.getElementById('total').textContent=DATA.length;
  refreshCounts();applyFilter();
  document.getElementById('q').addEventListener('input',e=>{query=e.target.value.trim().toLowerCase();applyFilter();});
  for(const chip of document.querySelectorAll('.chip')){chip.onclick=()=>{const c=chip.dataset.cat;
    if(activeCats.has(c)){activeCats.delete(c);chip.classList.remove('on');}
    else{activeCats.add(c);chip.classList.add('on');}applyFilter();};}
  for(const vc of document.querySelectorAll('.vchip')){vc.onclick=()=>{const v=vc.dataset.v;
    if(activeVerdicts.has(v)){activeVerdicts.delete(v);vc.classList.remove('on');}
    else{activeVerdicts.add(v);vc.classList.add('on');}applyFilter();};}
  document.getElementById('selallvis').onclick=selectAllVisible;
  // bulk bar buttons
  const addWrap=document.getElementById('bulkadd'),delWrap=document.getElementById('bulkdel');
  for(const v of VERDICTS){
    const a=document.createElement('button');a.className='bulk-add';a.textContent='+'+v;
    a.style.setProperty('--vc',VCOLORS[v]);a.onclick=()=>bulkApply(v,true);addWrap.appendChild(a);
    const d=document.createElement('button');d.className='bulk-del';d.textContent='-'+v;
    d.onclick=()=>bulkApply(v,false);delWrap.appendChild(d);
  }
  document.getElementById('clearsel').onclick=clearSel;
  document.getElementById('expjson').onclick=exportJSON;
  document.getElementById('expcsv').onclick=exportCSV;
  document.getElementById('copypromote').onclick=()=>copyList('promote');
  document.getElementById('copyfavour').onclick=()=>copyList('favour');
  document.getElementById('impbtn').onclick=()=>document.getElementById('impfile').click();
  document.getElementById('impfile').addEventListener('change',e=>{if(e.target.files[0])importJSON(e.target.files[0]);e.target.value='';});
  const lb=document.getElementById('lb');lb.onclick=()=>lb.classList.remove('on');
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){lb.classList.remove('on');}});
  if(!storageOK)document.getElementById('storewarn').style.display='inline';
});
"""

js = (
    js.replace("__DATA__", data_json)
    .replace("__CATCOLORS__", json.dumps(CAT_COLORS))
    .replace("__VERDICTS__", json.dumps(VERDICTS))
    .replace("__VCOLORS__", json.dumps(VERDICT_COLORS))
)

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>P(Doom)1 -- pixellab triage</title>
<style>{css}</style>
</head>
<body>
<header>
  <div class="title-row">
    <h1>P(Doom)1 pixellab library <span class="sub">// triage sheet</span></h1>
    <span class="badge"><span id="shown">{total}</span> / <span id="total">{total}</span> shown</span>
    <span class="badge">tagged <span id="taggedn">0</span></span>
    <span class="badge" id="storewarn" style="display:none;color:#d88">localStorage off -- verdicts wont persist (use Export)</span>
  </div>
  <div class="controls">
    <input id="q" type="search" placeholder="filter by filename / category / folder...">
    <span class="row-label">cat</span>{chips}
  </div>
  <div class="controls">
    <span class="row-label">verdict</span>{vchips}
    <span class="sep"> </span>
    <button class="btn" id="selallvis">select all visible</button>
    <button class="btn" id="expjson">export JSON</button>
    <button class="btn" id="expcsv">export CSV</button>
    <button class="btn" id="copypromote">copy PROMOTE</button>
    <button class="btn" id="copyfavour">copy FAVOUR</button>
    <button class="btn primary" id="impbtn">import JSON</button>
    <input type="file" id="impfile" accept="application/json,.json" style="display:none">
  </div>
</header>
<main id="main"></main>
<footer>
  Local triage tool -- untracked, not committed. Thumbnail = enlarge (Esc/click closes).
  Per-sprite verdict tags (like/dislike/favour/disfavour/promote) + batch select (checkbox,
  shift-click ranges, select-group / select-all-visible) + bulk apply/remove bar.
  Verdicts persist to this browser's localStorage; Export JSON/CSV to make them portable/actionable.
  {total} sprites across {len([r for r in runs if run_counts[r]])} runs.
</footer>
<div class="bulkbar" id="bulkbar">
  <span class="selcount"><span id="selcount">0</span> selected</span>
  <span class="sep">|</span>
  <span class="row-label">apply</span><span id="bulkadd" style="display:flex;gap:5px;flex-wrap:wrap"></span>
  <span class="sep">|</span>
  <span class="row-label">remove</span><span id="bulkdel" style="display:flex;gap:5px;flex-wrap:wrap"></span>
  <span class="sep">|</span>
  <button class="btn" id="clearsel">clear selection</button>
</div>
<div class="lightbox" id="lb"><img src="" alt=""><div class="lbcap"></div></div>
<div id="toast"></div>
<script>{js}</script>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(doc)
print("WROTE:", OUT, "bytes:", len(doc.encode("utf-8")))
