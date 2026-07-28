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
                           localStorage persistence, filter-by-verdict, and a
                           three-state completeness control (ALL / HIDE DECIDED /
                           ONLY UNREVIEWED): any verdict tag moves a cell off
                           unreviewed-neutral, so decided cells leave the live
                           queue and you can clear hundreds without getting
                           tired. Export / import JSON round-trips the flat
                           {rel: [tags]} schema used by analyze_verdicts.py.
  * bulk-select         -- ported from gen_contact_sheet.py (issue #900/#912
                           follow-up): a checkbox per cell, shift-click range
                           select (keyed off data-rel, respects the current
                           show-filter -- hidden cells never enter a shift
                           range or select-all-visible), a "select all visible"
                           button in the verdict toolbar, and a fixed bulk
                           apply/remove bar (one +tag/-tag button pair per
                           verdict). Automatic whenever a sheet passes
                           verdict_key to page() -- no per-sheet wiring needed.
  * completeness UX     -- COMPLETENESS_JS / COMPLETENESS_CSS /
                           completeness_controls(): sections render COLLAPSED by
                           default (expand state persists per-section in
                           localStorage; expand-all / collapse-all in the
                           header), every section header carries a live
                           "unreviewed N / M" rollup (parents aggregate their
                           sub-sections via DOM containment), and ONLY-UNREVIEWED
                           mode force-expands sections and hides any section with
                           0 unreviewed -- the completeness pass. The count
                           rollup has a pure-Python mirror, rollup_counts()
                           (run `python review_style.py --selftest`).

Compare-mode hook (issue #745): every cell carries data-rel; a future compare
mode can collect cells marked via a "compare" pin into a side-by-side tray.
See README "compare-and-contrast mode" note. Stdlib only; ASCII only.
"""

import datetime
import html as _html
import re as _re
import sys as _sys

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
padding:10px 10px 8px;width:240px;display:flex;flex-direction:column;position:relative;
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
/* per-item free-text notes (issue #900 follow-up): generous, always-visible,
   autosaves into the same localStorage record as the verdict tags. */
.rs-note{width:100%;box-sizing:border-box;margin-top:7px;background:var(--bg3);
color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px 7px;
font-family:monospace;font-size:11px;line-height:1.4;resize:vertical;min-height:56px;}
.rs-note:focus{outline:none;border-color:var(--amber);}
.rs-note::placeholder{color:var(--dim);}
/* verdict chips on a cell -- deliberately BIG tap targets (Pip: rapid-fire
   triage, screen real-estate greed explicitly approved, 2026-07-28). */
.rs-vtags{display:flex;flex-wrap:wrap;gap:7px;margin-top:9px;justify-content:center;}
.vtag{font-size:13px;font-family:monospace;padding:9px 16px;border-radius:8px;cursor:pointer;
border:2px solid var(--line);background:transparent;color:var(--dim);text-transform:uppercase;
letter-spacing:.4px;line-height:1;transition:all .1s;font-weight:600;}
.vtag:hover{color:var(--fg);border-color:var(--vc);}
.vtag.on{background:var(--vc);color:#12100c;border-color:var(--vc);font-weight:800;}
footer{color:var(--dim);font-size:11px;padding:20px 18px;border-top:1px solid var(--line);
font-family:monospace;line-height:1.6;}
#toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#2a2419;
border:1px solid var(--amber);color:var(--amber2);padding:8px 16px;border-radius:8px;
font-family:monospace;font-size:12px;z-index:1200;opacity:0;transition:opacity .2s;
pointer-events:none;}
#toast.on{opacity:1;}
"""
)

# completeness-pass chrome, shared verbatim by the contact sheet and the hero
# gallery template (both consume this constant -- keep it selector-generic):
# live "unreviewed N / M" pill per section head; ONLY-UNREVIEWED mode hides
# sections with 0 unreviewed (data-unrev kept current by COMPLETENESS_JS).
COMPLETENESS_CSS = """
.rs-cc{color:var(--dim);font-size:10px;font-family:monospace;border:1px solid var(--line);
border-radius:9px;padding:1px 7px;white-space:nowrap;}
.rs-cc.has-unrev{color:var(--amber2);border-color:#5a4a2a;}
body.rs-only [data-unrev="0"]{display:none;}
body.rs-only .caret{opacity:.35;}
"""

# bulk-select chrome (ported from gen_contact_sheet.py, issue #900/#912
# follow-up): per-cell checkbox, .sel highlight, and the fixed bulk apply/
# remove bar. Shared by every sheet that passes verdict_key to page().
BULK_CSS = """
main{padding-bottom:76px;}
.rs-selbox{position:absolute;top:6px;left:6px;width:16px;height:16px;cursor:pointer;
z-index:3;accent-color:var(--amber);margin:0;}
.rs-cell.sel{border-color:var(--amber2);box-shadow:0 0 0 1px var(--amber2) inset;}
.rs-bulkbar{position:fixed;left:0;right:0;bottom:0;z-index:40;
background:linear-gradient(0deg,#221d16,#1a1611);border-top:1px solid #5a4a2a;
padding:10px 18px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;
box-shadow:0 -3px 14px #000a;transform:translateY(110%);transition:transform .18s;}
.rs-bulkbar.on{transform:translateY(0);}
.rs-bulkbar .rs-selcount{color:var(--amber2);font-family:monospace;font-size:13px;font-weight:600;}
.rs-bulkbar .sep{color:var(--line);}
.rs-bulk-add,.rs-bulk-del{border-radius:6px;font-size:11px;padding:5px 9px;border:1px solid var(--line);
background:var(--bg3);color:var(--dim);cursor:pointer;font-family:monospace;}
.rs-bulk-add:hover{background:var(--vc);color:#12100c;border-color:var(--vc);}
.rs-bulk-del:hover{background:#3a2020;border-color:#cc5a4a;color:#e8b0a8;}
"""

BASE_CSS += COMPLETENESS_CSS
BASE_CSS += BULK_CSS

# ---------------------------------------------------------------- completeness JS

# Shared engine: collapsed-by-default sections with per-section localStorage
# expand state + expand/collapse-all, the ALL / HIDE DECIDED / ONLY UNREVIEWED
# three-state, and the live unreviewed/total rollup (parents aggregate children
# because querySelectorAll on a parent section sees descendant cells).
# Consumers: VERDICT_JS below, gen_contact_sheet.py, hero_gallery_template.html
# (injected by gen_hero_gallery.py). Pure-Python mirror: rollup_counts().
COMPLETENESS_JS = r"""
window.rsCompleteness=(function(){
  const cfg={key:null,sectionSel:'.rs-section',cellSel:'.rs-cell[data-rel]',
    tagsOf:function(){return [];},onFilter:null};
  let exp={};      // secid -> 1 == user expanded (sections default COLLAPSED)
  let mode='all';  // 'all' | 'hide' (hide decided) | 'only' (only unreviewed)
  let inited=false;
  function skey(){return (cfg.key||('rsui:'+document.title))+':expanded';}
  function load(){try{exp=JSON.parse(localStorage.getItem(skey()))||{};}catch(e){exp={};}}
  function save(){try{localStorage.setItem(skey(),JSON.stringify(exp));}catch(e){}}
  function sections(){return Array.from(document.querySelectorAll(cfg.sectionSel));}
  function secId(s,i){return s.dataset.secid||('sec'+i);}
  function applyCollapse(){const force=(mode==='only'); // completeness pass opens everything
    sections().forEach((s,i)=>{s.classList.toggle('collapsed',!force&&!exp[secId(s,i)]);});}
  function toggle(sec){const i=sections().indexOf(sec);const id=secId(sec,i);
    const col=sec.classList.toggle('collapsed');
    if(col)delete exp[id];else exp[id]=1;save();}
  function setAll(open){exp={};if(open)sections().forEach((s,i)=>{exp[secId(s,i)]=1;});
    save();applyCollapse();}
  function markMode(){document.body.classList.toggle('rs-only',mode==='only');
    for(const b of document.querySelectorAll('[data-rsmode]'))
      b.classList.toggle('on',b.dataset.rsmode===mode);}
  function setMode(m){mode=m;markMode();applyCollapse();updateCounts();
    if(cfg.onFilter)cfg.onFilter();}
  function cellPass(tags){return mode==='all'||!(tags&&tags.length);}
  function updateCounts(){for(const s of sections()){
    let un=0,tot=0;
    for(const c of s.querySelectorAll(cfg.cellSel)){tot++;
      const t=cfg.tagsOf(c.dataset.rel);if(!(t&&t.length))un++;}
    s.dataset.unrev=un;
    const el=s.querySelector('.rs-cc');
    if(el){el.textContent=tot?('unreviewed '+un+' / '+tot):'';
      el.classList.toggle('has-unrev',un>0);}}}
  function init(c){Object.assign(cfg,c||{});load();applyCollapse();markMode();updateCounts();
    if(!inited){inited=true;
      const ea=document.getElementById('rs-expandall');if(ea)ea.onclick=()=>setAll(true);
      const ca=document.getElementById('rs-collapseall');if(ca)ca.onclick=()=>setAll(false);
      for(const b of document.querySelectorAll('[data-rsmode]'))
        b.onclick=()=>setMode(b.dataset.rsmode);}
  }
  window.addEventListener('DOMContentLoaded',()=>{if(!inited)init({});});
  return {init:init,toggle:toggle,setAll:setAll,setMode:setMode,
    cellPass:cellPass,updateCounts:updateCounts,mode:()=>mode};
})();
window.rsSecToggle=function(sec){window.rsCompleteness.toggle(sec);};
"""


def completeness_controls(default_mode="all"):
    """Header controls for the completeness pass: the ALL / HIDE DECIDED /
    ONLY UNREVIEWED three-state plus expand-all / collapse-all. Buttons are
    wired by COMPLETENESS_JS (data-rsmode / rs-expandall / rs-collapseall)."""

    def b(m, label):
        on = " on" if m == default_mode else ""
        return f'<button class="toggle{on}" data-rsmode="{m}">{label}</button>'

    return (
        '<span class="row-label">show</span>'
        + b("all", "all")
        + b("hide", "hide decided")
        + b("only", "only unreviewed")
        + '<span class="row-label">sections</span>'
        '<button class="btn" id="rs-expandall">expand all</button>'
        '<button class="btn" id="rs-collapseall">collapse all</button>'
    )


# ---------------------------------------------------------------- verdict JS

VERDICT_JS = r"""
(function(){
const VERDICTS=__RS_VERDICTS__;
const VCOLORS=__RS_VCOLORS__;
const KEY='__RS_KEY__';
const EXPORT_NAME='__RS_EXPORT__';
let V={},storageOK=false;
// Per-item record is {tags:[...], note:"..."}. Legacy exports/localStorage
// (pre-notes) stored a bare array of tags per rel -- normalize() upgrades
// those on load/import so old in-progress verdicts survive a sheet rebuild.
// The localStorage KEY itself never changes (Pip has in-progress verdicts).
function normalize(raw){
  const out={};
  if(!raw||typeof raw!=='object')return out;
  for(const k in raw){
    const v=raw[k];
    if(Array.isArray(v))out[k]={tags:v.slice(),note:''};
    else if(v&&typeof v==='object')
      out[k]={tags:Array.isArray(v.tags)?v.tags.slice():[],note:typeof v.note==='string'?v.note:''};
  }
  return out;
}
function loadV(){try{const s=localStorage.getItem(KEY);V=normalize(s?JSON.parse(s):{});storageOK=true;}
  catch(e){V={};storageOK=false;}}
function saveV(){if(!storageOK)return;try{localStorage.setItem(KEY,JSON.stringify(V));}catch(e){storageOK=false;}}
function tagsOf(r){return (V[r]&&V[r].tags)||[];}
function noteOf(r){return (V[r]&&V[r].note)||'';}
function hasTag(r,t){return tagsOf(r).indexOf(t)>=0;}
function setTag(r,t,on){const cur=V[r]||{tags:[],note:''};
  const a=cur.tags.slice();const i=a.indexOf(t);
  if(on&&i<0)a.push(t);else if(!on&&i>=0)a.splice(i,1);
  const note=cur.note||'';
  if(a.length||note.trim())V[r]={tags:a,note:note};else delete V[r];}
function setNote(r,text){const cur=V[r]||{tags:[],note:''};
  const tags=cur.tags||[];
  if(tags.length||text.trim())V[r]={tags:tags,note:text};else delete V[r];}
let activeVerdicts=new Set();
const cells=Array.from(document.querySelectorAll('.rs-cell[data-rel]'));
function applyFilter(){
  let shown=0,hidden=0;
  for(const c of cells){
    const r=c.dataset.rel,tags=tagsOf(r);let ok=true;
    if(!rsCompleteness.cellPass(tags))ok=false;
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
  for(const r in V){const tags=tagsOf(r);for(const t of tags)if(c[t]!==undefined)c[t]++;
    if(tags.length)any++;}
  for(const v of VERDICTS){const el=document.getElementById('rs-vcount-'+v);
    if(el)el.textContent=c[v];}
  const tg=document.getElementById('rs-taggedn');if(tg)tg.textContent=any;
}
function syncCell(c){const r=c.dataset.rel;
  for(const b of c.querySelectorAll('.vtag'))b.classList.toggle('on',hasTag(r,b.dataset.v));
  const nt=c.querySelector('.rs-note');if(nt)nt.value=noteOf(r);}
// ---- bulk-select (ported from gen_contact_sheet.py, issue #900/#912 follow-up) ----
// data-rel is the stable handle (README compare-mode note); shift-click range
// select walks DOM order and skips cells hidden by the current show-filter.
const cellByRel={};for(const c of cells)cellByRel[c.dataset.rel]=c;
const selected=new Set();
let lastClickedIdx=null;
function setSel(rel,on){const c=cellByRel[rel];if(!c)return;
  if(on){selected.add(rel);c.classList.add('sel');}else{selected.delete(rel);c.classList.remove('sel');}
  const cb=c.querySelector('.rs-selbox');if(cb)cb.checked=on;}
function onSelClick(rel,shift,checked){
  const idx=cells.indexOf(cellByRel[rel]);
  if(shift&&lastClickedIdx!==null){
    const [a,b]=[Math.min(lastClickedIdx,idx),Math.max(lastClickedIdx,idx)];
    for(let i=a;i<=b;i++){const c=cells[i];
      if(c.style.display==='none')continue; // never silently pull in filtered-out cells
      setSel(c.dataset.rel,checked);}
  }else{setSel(rel,checked);}
  lastClickedIdx=idx;updateSelUI();
}
function selectAllVisible(){const vis=cells.filter(c=>c.style.display!=='none').map(c=>c.dataset.rel);
  const allSel=vis.length&&vis.every(r=>selected.has(r));
  for(const r of vis)setSel(r,!allSel);updateSelUI();}
function clearSel(){for(const r of[...selected])setSel(r,false);updateSelUI();}
function updateSelUI(){const n=selected.size;
  const sc=document.getElementById('rs-selcountn');if(sc)sc.textContent=n;
  const bar=document.getElementById('rs-bulkbar');if(bar)bar.classList.toggle('on',n>0);}
function bulkApply(v,on){for(const r of selected){setTag(r,v,on);
  const c=cellByRel[r];if(!c)continue;const b=c.querySelector(`.vtag[data-v="${v}"]`);
  if(b)b.classList.toggle('on',on);}
  saveV();refreshCounts();rsCompleteness.updateCounts();
  if(rsCompleteness.mode()!=='all'||activeVerdicts.size)applyFilter();
  toast(`${on?'Set':'Removed'} ${v} on ${selected.size} item(s)`);}
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
        b.classList.toggle('on',on);saveV();refreshCounts();rsCompleteness.updateCounts();
        if(rsCompleteness.mode()!=='all'||activeVerdicts.size)applyFilter();};
      vt.appendChild(b);
    }
    const cb=document.createElement('input');cb.type='checkbox';cb.className='rs-selbox';
    cb.title='select';
    cb.addEventListener('click',e=>{e.stopPropagation();onSelClick(r,e.shiftKey,cb.checked);});
    c.insertBefore(cb,c.firstChild);
    const nt=c.querySelector('.rs-note');
    if(nt){nt.value=noteOf(r);let noteT=null;
      const commit=()=>{setNote(r,nt.value);saveV();};
      nt.addEventListener('input',()=>{clearTimeout(noteT);noteT=setTimeout(commit,400);});
      nt.addEventListener('blur',()=>{clearTimeout(noteT);commit();});
      nt.addEventListener('click',e=>e.stopPropagation());
    }
  }
  for(const vc of document.querySelectorAll('.vchip[data-v]')){
    vc.onclick=()=>{const v=vc.dataset.v;
      if(activeVerdicts.has(v)){activeVerdicts.delete(v);vc.classList.remove('on');}
      else{activeVerdicts.add(v);vc.classList.add('on');}applyFilter();};}
  const sav=document.getElementById('rs-selallvis');if(sav)sav.onclick=selectAllVisible;
  const addWrap=document.getElementById('rs-bulkadd'),delWrap=document.getElementById('rs-bulkdel');
  if(addWrap&&delWrap){
    for(const v of VERDICTS){
      const a=document.createElement('button');a.className='rs-bulk-add';a.textContent='+'+v;
      a.style.setProperty('--vc',VCOLORS[v]);a.onclick=()=>bulkApply(v,true);addWrap.appendChild(a);
      const d=document.createElement('button');d.className='rs-bulk-del';d.textContent='-'+v;
      d.onclick=()=>bulkApply(v,false);delWrap.appendChild(d);
    }
  }
  const cs=document.getElementById('rs-clearsel');if(cs)cs.onclick=clearSel;
  rsCompleteness.init({key:KEY,sectionSel:'.rs-section',cellSel:'.rs-cell[data-rel]',
    tagsOf:tagsOf,onFilter:applyFilter});
  const ex=document.getElementById('rs-export');
  if(ex)ex.onclick=()=>{download(EXPORT_NAME,JSON.stringify(V,null,2),'application/json');
    toast('Exported '+EXPORT_NAME);};
  const ib=document.getElementById('rs-import'),inf=document.getElementById('rs-importfile');
  if(ib&&inf){ib.onclick=()=>inf.click();
    inf.addEventListener('change',e=>{const f=e.target.files[0];if(!f)return;
      const rd=new FileReader();
      rd.onload=()=>{try{const obj=JSON.parse(rd.result);
        if(typeof obj!=='object'||Array.isArray(obj))throw 0;
        V=normalize(obj);saveV();for(const c of cells)syncCell(c);
        refreshCounts();rsCompleteness.updateCounts();applyFilter();toast('Imported verdicts');
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
        '<span class="row-label">verdict</span>'
        + vchips
        + " "
        + completeness_controls()
        + '<span class="count-tag"><span id="rs-hiddenn">0</span> hidden</span> '
        '<button class="btn" id="rs-selallvis">select all visible</button>'
        '<button class="btn" id="rs-export">export JSON</button>'
        '<button class="btn primary" id="rs-import">import JSON</button>'
        '<input type="file" id="rs-importfile" accept="application/json,.json" style="display:none">'
        "</div>"
    )


def _bulk_bar():
    """Fixed bulk apply/remove bar (ported from gen_contact_sheet.py). Buttons
    for +tag/-tag per verdict are populated by VERDICT_JS; only rendered when
    the sheet has a verdict toolbar (verdict_key set)."""
    return (
        '<div class="rs-bulkbar" id="rs-bulkbar">'
        '<span class="rs-selcount"><span id="rs-selcountn">0</span> selected</span>'
        '<span class="sep">|</span>'
        '<span class="row-label">apply</span>'
        '<span id="rs-bulkadd" style="display:flex;gap:5px;flex-wrap:wrap"></span>'
        '<span class="sep">|</span>'
        '<span class="row-label">remove</span>'
        '<span id="rs-bulkdel" style="display:flex;gap:5px;flex-wrap:wrap"></span>'
        '<span class="sep">|</span>'
        '<button class="btn" id="rs-clearsel">clear selection</button>'
        "</div>"
    )


# ---------------------------------------------------------------- components

# Per-item notes textarea (issue #900 follow-up). image_cell() emits this
# automatically when rel is set; sheets that hand-roll their own cell markup
# (most of them -- image_cell() is the exception, not the rule) should append
# this literally after their own '<div class="rs-vtags"></div>' so every
# reviewable card gets the same notes box, wired by VERDICT_JS's per-cell
# '.rs-note' lookup (no per-sheet JS needed).
NOTE_HTML = '<textarea class="rs-note" rows="3" placeholder="notes..."></textarea>'


def esc(s):
    """HTML-escape (accepts None)."""
    return _html.escape("" if s is None else str(s), quote=True)


def section(title, body_html, count=None, accent=None, head_extra=""):
    """Collapsible titled section. accent = CSS colour for the heading rule.

    Renders COLLAPSED by default (completeness UX): COMPLETENESS_JS restores
    per-section expand state from localStorage, keyed by a slug of the title,
    and keeps the head's "unreviewed N / M" pill (.rs-cc) live.
    """
    style = f' style="--accent:{accent}"' if accent else ""
    cls = "rs-sec-head accent" if accent else "rs-sec-head"
    count_tag = f' <span class="count-tag">{count}</span>' if count is not None else ""
    secid = _re.sub(r"[^a-z0-9]+", "-", str(title).lower()).strip("-") or "section"
    return (
        f'<section class="rs-section collapsed" data-secid="{esc(secid)}"{style}>'
        f'<div class="{cls}" onclick="rsSecToggle(this.parentNode)">'
        f'<span class="caret">v</span>{esc(title)}{count_tag}'
        f'<span class="rs-cc"></span>{head_extra}</div>'
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
        parts.append('<textarea class="rs-note" rows="3" placeholder="notes..."></textarea>')
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
    bulk_bar = ""
    if verdict_key:
        verdict_bar = _verdict_toolbar()
        bulk_bar = _bulk_bar()
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
            f'"{verdict_key}"; sections open collapsed (expand state remembered); '
            "show: all / hide decided / only unreviewed -- only-unreviewed is the "
            "completeness pass (any verdict tag = decided; sections with 0 "
            "unreviewed disappear); export JSON to make decisions durable. "
            "Batch-select: checkbox + shift-click range per cell, select all "
            "visible (respects the current show-filter), bulk apply/remove bar."
        )
    if footer_note:
        footer_bits.append(footer_note)
    scripts = f"<script>{COMPLETENESS_JS}</script>"
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
{bulk_bar}
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


# ---------------------------------------------------------------- rollup (pure)


def rollup_counts(section_tree, verdicts):
    """Pure mirror of COMPLETENESS_JS's updateCounts() rollup.

    section_tree -- {"id": str, "cells": [rel, ...], "children": [tree, ...]}
    verdicts     -- {rel: [tags]} (the flat verdict schema); a missing rel or an
                    empty tag list means UNREVIEWED (any tag = decided).

    Returns {section_id: (unreviewed, total)} where a parent's counts include
    every descendant's cells -- in the JS this aggregation falls out of
    querySelectorAll on the parent element seeing descendant cells.
    """
    out = {}

    def walk(sec):
        un = tot = 0
        for rel in sec.get("cells", ()):
            tot += 1
            if not verdicts.get(rel):
                un += 1
        for child in sec.get("children", ()):
            cu, ct = walk(child)
            un += cu
            tot += ct
        out[sec["id"]] = (un, tot)
        return un, tot

    walk(section_tree)
    return out


def _selftest():
    """Check the count-rollup logic (python mirror of the JS)."""
    tree = {
        "id": "batch",
        "cells": ["root_a"],
        "children": [
            {"id": "batch/chars", "cells": ["b", "c"], "children": []},
            {"id": "batch/props", "cells": ["d", "e", "f"], "children": []},
        ],
    }
    verdicts = {
        "b": ["like"],  # decided
        "e": ["dislike", "favour"],  # decided (multi-tag still one item)
        "f": [],  # empty list == unreviewed (schema drops empty keys)
        "ghost": ["promote"],  # verdict for a cell not on the sheet: ignored
    }
    got = rollup_counts(tree, verdicts)
    assert got["batch/chars"] == (1, 2), got
    assert got["batch/props"] == (2, 3), got
    # parent = own cells + sum of children: (1,1) + (1,2) + (2,3)
    assert got["batch"] == (4, 6), got
    # all-decided section -> 0 unreviewed (ONLY-UNREVIEWED mode hides it)
    solo = rollup_counts({"id": "s", "cells": ["x"], "children": []}, {"x": ["promote"]})
    assert solo["s"] == (0, 1), solo
    # no verdicts at all -> everything unreviewed
    fresh = rollup_counts(tree, {})
    assert fresh["batch"] == (6, 6), fresh
    # sanity: the JS engine string carries the same vocabulary + hooks
    for needle in ("cellPass", "updateCounts", "data-rsmode", "rs-expandall", "rs-cc"):
        assert needle in COMPLETENESS_JS, needle
    assert 'body.rs-only [data-unrev="0"]' in COMPLETENESS_CSS
    print("review_style selftest OK (rollup + completeness hooks)")


if __name__ == "__main__":
    if "--selftest" in _sys.argv:
        _selftest()
    else:
        print("usage: python review_style.py --selftest")
