#!/usr/bin/env python3
"""Build a verdict-capturing review page for the endgame concept batch.

Why this exists rather than a plain contact sheet: a review with someone
looking over your shoulder is fast, and anything not captured in the moment is
lost. This page captures a verdict AND a free-text note per image, persists to
localStorage so a refresh cannot destroy the session, and exports JSON in the
shape art_source/hero_verdicts.json already uses (path -> list of tags) so the
result feeds the existing hero-art tooling instead of stranding in a new format.

Notes are exported alongside under a separate "notes" key, because
hero_verdicts.json values are tag arrays with nowhere to put prose.

Usage:
    python tools/art_review/build_endgame_review.py
    -> writes art_generated/endgame_concepts/review.html
"""

import html
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
IMG_DIR = REPO / "art_generated" / "endgame_concepts" / "v1"
OUT = REPO / "art_generated" / "endgame_concepts" / "review.html"
MANIFEST_CANDIDATES = [
    REPO / "tools" / "assets" / "manifests" / "endgame_concepts.json",
    REPO / "endgame_manifest_tmp.json",
]

VERDICTS = [
    ("promote", "Promote", "1"),
    ("like", "Like", "2"),
    ("meh", "Meh", "3"),
    ("dislike", "Dislike", "4"),
]


def load_manifest() -> dict:
    for path in MANIFEST_CANDIDATES:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise SystemExit("endgame_concepts.json not found in any known location")


def main() -> int:
    manifest = load_manifest()
    assets = manifest.get("assets", [])

    cards = []
    for asset in assets:
        asset_id = asset.get("id", "")
        title = html.escape(asset.get("display_name", asset_id))
        theme = html.escape(asset.get("theme", ""))
        prompt = html.escape((asset.get("prompt_tail", "") or "")[:900])

        variants = []
        for variant in ("v1", "v2"):
            name = f"{asset_id}_{variant}_1024.png"
            if not (IMG_DIR / name).exists():
                name = f"{asset_id}_{variant}_512.png"
            if not (IMG_DIR / name).exists():
                continue
            key = f"endgame_concepts/v1/{name}"
            full = f"{asset_id}_{variant}_1536.png"
            buttons = "".join(
                f'<button class="v" data-k="{html.escape(key)}" data-v="{code}">'
                f"{label}</button>"
                for code, label, _ in VERDICTS
            )
            variants.append(
                f'<figure class="var" data-key="{html.escape(key)}">'
                f'<a href="v1/{html.escape(full)}" target="_blank">'
                f'<img loading="lazy" src="v1/{html.escape(name)}" alt="{title} {variant}"></a>'
                f"<figcaption>{variant}</figcaption>"
                f'<div class="btns">{buttons}</div>'
                f'<textarea class="note" data-k="{html.escape(key)}" rows="2" '
                f'placeholder="note ({variant}) -- what works, what does not"></textarea>'
                f"</figure>"
            )

        if not variants:
            continue
        cards.append(
            f'<section class="card" id="{html.escape(asset_id)}">'
            f'<h2>{title} <span class="theme">{theme}</span></h2>'
            f'<div class="vars">{"".join(variants)}</div>'
            f'<details><summary>prompt</summary><p class="prompt">{prompt}</p></details>'
            f"</section>"
        )

    page = TEMPLATE.replace("__CARDS__", "\n".join(cards)).replace(
        "__COUNT__", str(sum(1 for _ in assets))
    )
    OUT.write_text(page, encoding="utf-8", newline="\n")
    print(f"[+] wrote {OUT}")
    print(f"[*] {len(cards)} concepts, open it in a browser")
    return 0


TEMPLATE = """<!doctype html>
<meta charset="utf-8">
<title>Endgame concepts -- review</title>
<style>
  :root{--bg:#15151a;--fg:#e9e7e2;--dim:#96938c;--line:#33323b;--card:#1d1d24;
        --ok:#7fc08d;--warn:#d9bd6a;--no:#e2807c;--acc:#d9955c}
  @media(prefers-color-scheme:light){:root{--bg:#f6f5f2;--fg:#1a1a18;--dim:#63615c;
        --line:#d9d6ce;--card:#fff;--ok:#2f6b3a;--warn:#8a6a10;--no:#9c2b2b;--acc:#7a3b12}}
  *{box-sizing:border-box}
  body{background:var(--bg);color:var(--fg);margin:0;padding:16px 18px 120px;
       font:14px/1.5 ui-monospace,Consolas,monospace}
  header{position:sticky;top:0;z-index:9;background:var(--bg);border-bottom:1px solid var(--line);
         padding:10px 0;margin-bottom:14px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
  h1{font-size:16px;margin:0}
  .card{border:1px solid var(--line);background:var(--card);border-radius:5px;
        padding:12px 14px;margin:0 0 16px}
  h2{font-size:14px;margin:0 0 10px;font-weight:600}
  .theme{color:var(--dim);font-weight:400;font-size:12px}
  .vars{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
  figure{margin:0}
  img{width:100%;height:auto;display:block;border:1px solid var(--line);border-radius:3px}
  figcaption{color:var(--dim);font-size:11px;margin:4px 0}
  .btns{display:flex;gap:5px;margin:6px 0}
  button.v{flex:1;padding:7px 4px;font:600 11px ui-monospace,monospace;cursor:pointer;
           background:transparent;color:var(--dim);border:1px solid var(--line);border-radius:3px}
  button.v:hover{color:var(--fg)}
  .var[data-verdict="promote"] button.v[data-v="promote"]{background:var(--ok);color:#08120a;border-color:var(--ok)}
  .var[data-verdict="like"] button.v[data-v="like"]{background:var(--acc);color:#120a04;border-color:var(--acc)}
  .var[data-verdict="meh"] button.v[data-v="meh"]{background:var(--warn);color:#120e02;border-color:var(--warn)}
  .var[data-verdict="dislike"] button.v[data-v="dislike"]{background:var(--no);color:#170606;border-color:var(--no)}
  .var[data-verdict="dislike"] img{opacity:.42}
  textarea.note{width:100%;background:var(--bg);color:var(--fg);border:1px solid var(--line);
                border-radius:3px;padding:6px;font:12px ui-monospace,monospace;resize:vertical}
  details{margin-top:10px}
  summary{color:var(--dim);cursor:pointer;font-size:12px}
  .prompt{color:var(--dim);font-size:12px;white-space:pre-wrap}
  #bar{position:fixed;left:0;right:0;bottom:0;background:var(--card);
       border-top:1px solid var(--line);padding:9px 16px;display:flex;gap:12px;
       align-items:center;font-size:12px;flex-wrap:wrap}
  #bar button{padding:7px 13px;font:600 12px ui-monospace,monospace;cursor:pointer;
              background:var(--acc);color:#120a04;border:0;border-radius:3px}
  #bar button.ghost{background:transparent;color:var(--dim);border:1px solid var(--line)}
  #out{width:100%;height:150px;display:none;margin-top:8px;background:var(--bg);
       color:var(--fg);border:1px solid var(--line);font:11px ui-monospace,monospace}
  .hint{color:var(--dim)}
</style>

<header>
  <h1>Endgame concepts -- review</h1>
  <span class="hint">click a verdict, type a note. Saved locally as you go.</span>
  <span id="prog" class="hint"></span>
</header>

__CARDS__

<div id="bar">
  <button id="exp">Export JSON</button>
  <button id="copy" class="ghost">Copy to clipboard</button>
  <button id="clr" class="ghost">Clear all</button>
  <span id="msg" class="hint"></span>
  <textarea id="out" readonly></textarea>
</div>

<script>
const KEY = "endgame_review_v1";
let state = JSON.parse(localStorage.getItem(KEY) || '{"verdicts":{},"notes":{}}');

function save(){ localStorage.setItem(KEY, JSON.stringify(state)); paint(); }

function paint(){
  document.querySelectorAll(".var").forEach(f=>{
    const v = state.verdicts[f.dataset.key];
    if(v) f.setAttribute("data-verdict", v); else f.removeAttribute("data-verdict");
  });
  document.querySelectorAll("textarea.note").forEach(t=>{
    if(state.notes[t.dataset.k] !== undefined && t.value === "") t.value = state.notes[t.dataset.k];
  });
  const done = Object.keys(state.verdicts).length;
  const total = document.querySelectorAll(".var").length;
  document.getElementById("prog").textContent = done + " / " + total + " judged";
}

document.querySelectorAll("button.v").forEach(b=>{
  b.addEventListener("click", ()=>{
    const k = b.dataset.k;
    if(state.verdicts[k] === b.dataset.v) delete state.verdicts[k];
    else state.verdicts[k] = b.dataset.v;
    save();
  });
});

document.querySelectorAll("textarea.note").forEach(t=>{
  t.addEventListener("input", ()=>{
    if(t.value.trim()) state.notes[t.dataset.k] = t.value.trim();
    else delete state.notes[t.dataset.k];
    localStorage.setItem(KEY, JSON.stringify(state));
  });
});

function payload(){
  // hero_verdicts.json shape: path -> [tags]. Notes ride alongside, since that
  // schema has nowhere to put prose.
  const verdicts = {};
  for(const [k,v] of Object.entries(state.verdicts)) verdicts[k] = [v];
  return JSON.stringify({batch:"endgame_concepts/v1", verdicts, notes: state.notes}, null, 1);
}

document.getElementById("exp").addEventListener("click", ()=>{
  const blob = new Blob([payload()], {type:"application/json"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "endgame_review.json";
  a.click();
  document.getElementById("msg").textContent = "downloaded endgame_review.json";
});

document.getElementById("copy").addEventListener("click", async ()=>{
  const out = document.getElementById("out");
  out.style.display = "block";
  out.value = payload();
  out.select();
  try { await navigator.clipboard.writeText(out.value);
        document.getElementById("msg").textContent = "copied"; }
  catch(e){ document.getElementById("msg").textContent = "select the box and copy"; }
});

document.getElementById("clr").addEventListener("click", ()=>{
  if(!confirm("Clear every verdict and note?")) return;
  state = {verdicts:{},notes:{}}; save();
  document.querySelectorAll("textarea.note").forEach(t=>t.value="");
});

paint();
</script>
"""


if __name__ == "__main__":
    raise SystemExit(main())
