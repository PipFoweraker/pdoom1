#!/usr/bin/env python3
"""Side-by-side comparison of two generations of the same concept batch.

Built 2026-07-29 so a morning review can answer the question that actually
matters after a feedback round: *did the notes work?* Verdicts on single images
cannot answer that. Seeing generation 1 and generation 2 of the same concept in
one row can.

Layout per concept: gen1 v1 + v2 on the left, gen2 v1 + v2 on the right, with a
visible divider. Each image takes a verdict; each concept takes a note AND a
"which generation won" pick -- that pick is the data point that decides whether
the provisional rules A1-A10 survive (see
docs/art/ENDGAME_CONCEPT_REVIEW_2026-07-29.md).

Both generations' prompts are included, collapsed, so a surprising result can be
traced to what actually changed in the text.

Everything persists to localStorage as you go and exports as JSON.

Usage:
    python tools/art_review/build_generation_compare.py
    python tools/art_review/build_generation_compare.py --open
"""

import argparse
import html
import json
import webbrowser
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ART = REPO / "art_generated"
MANIFESTS = REPO / "tools" / "assets" / "manifests"
GEN1_MANIFEST = MANIFESTS / "endgame_concepts.json"
GEN2_MANIFEST = MANIFESTS / "endgame_concepts_gen2.json"
OUT = ART / "generation_compare.html"

VERDICTS = [("promote", "Promote"), ("like", "Like"), ("meh", "Meh"), ("dislike", "Dislike")]
PICKS = [("gen1", "Gen 1 wins"), ("gen2", "Gen 2 wins"), ("neither", "Neither")]


def load(path: Path) -> dict:
    """Read a manifest, falling back to origin/main if it is not on disk.

    Pip syncs his own main, so a manifest committed earlier today can be absent
    from his working tree while present on the remote. That is a stale checkout,
    NOT a lost file -- so look in git before giving up.
    """
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    import subprocess

    rel = path.relative_to(REPO).as_posix()
    result = subprocess.run(
        ["git", "show", f"origin/main:{rel}"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        print(f"[*] {rel} not on disk; read from origin/main (local main is behind)")
        return json.loads(result.stdout)
    return {}


def find_image_dir(manifest: dict, fallback: str) -> Path:
    """Locate the directory the generator wrote to for this manifest.

    The pipeline writes to art_generated/<asset_type>/v1, but a second batch may
    use a different asset_type, so resolve it rather than assuming.
    """
    asset_type = manifest.get("asset_type") or fallback
    candidate = ART / asset_type / "v1"
    if candidate.is_dir():
        return candidate
    # Fall back to any directory that actually contains matching PNGs.
    for path in sorted(ART.glob(f"{asset_type}*/**/")):
        if any(path.glob("*.png")):
            return path
    return candidate


def pick_image(directory: Path, asset_id: str, variant: str) -> str:
    """Prefer a mid-size render; fall back through the sizes the pipeline emits."""
    for size in ("1024", "768", "512", "1536"):
        name = f"{asset_id}_{variant}_{size}.png"
        if (directory / name).exists():
            return name
    return ""


def figure(rel_root: str, directory: Path, asset_id: str, variant: str, gen: str) -> str:
    name = pick_image(directory, asset_id, variant)
    if not name:
        return f'<figure class="var missing"><div class="none">no {gen} {variant}</div></figure>'
    key = f"{gen}/{asset_id}/{variant}"
    full = f"{asset_id}_{variant}_1536.png"
    full_path = directory / full
    href = f"{rel_root}/{full if full_path.exists() else name}"
    buttons = "".join(
        f'<button class="v" data-k="{key}" data-v="{code}">{label}</button>'
        for code, label in VERDICTS
    )
    return (
        f'<figure class="var" data-key="{key}">'
        f'<a href="{href}" target="_blank">'
        f'<img loading="lazy" src="{rel_root}/{name}" alt="{asset_id} {gen} {variant}"></a>'
        f"<figcaption>{gen} &middot; {variant}</figcaption>"
        f'<div class="btns">{buttons}</div>'
        f"</figure>"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--open", action="store_true", help="open in the default browser when built"
    )
    args = parser.parse_args()

    gen1 = load(GEN1_MANIFEST)
    gen2 = load(GEN2_MANIFEST)
    if not gen1:
        raise SystemExit(f"[!] generation-1 manifest not found: {GEN1_MANIFEST}")
    if not gen2:
        print(f"[!] generation-2 manifest not found: {GEN2_MANIFEST}")
        print("    Building a gen1-only page; re-run once generation 2 exists.")

    dir1 = find_image_dir(gen1, "endgame_concepts")
    dir2 = find_image_dir(gen2, "endgame_concepts_gen2") if gen2 else None
    rel1 = dir1.relative_to(ART).as_posix()
    rel2 = dir2.relative_to(ART).as_posix() if dir2 and dir2.exists() else ""

    prompts2 = {a.get("id"): a.get("prompt_tail", "") for a in gen2.get("assets", [])}
    names2 = {a.get("id"): a.get("display_name", "") for a in gen2.get("assets", [])}

    ordered = list(gen1.get("assets", []))
    known = {a.get("id") for a in ordered}
    for asset in gen2.get("assets", []):
        if asset.get("id") not in known:
            ordered.append(asset)  # concepts new in gen2 (e.g. runaway_delivery_loop)

    cards = []
    for asset in ordered:
        asset_id = asset.get("id", "")
        title = html.escape(asset.get("display_name") or names2.get(asset_id) or asset_id)
        is_new = asset_id not in {a.get("id") for a in gen1.get("assets", [])}
        badge = ' <span class="new">NEW IN GEN 2</span>' if is_new else ""

        left = (
            figure(rel1, dir1, asset_id, "v1", "gen1") + figure(rel1, dir1, asset_id, "v2", "gen1")
            if not is_new
            else '<figure class="var missing"><div class="none">not in gen 1</div></figure>'
        )
        right = (
            figure(rel2, dir2, asset_id, "v1", "gen2") + figure(rel2, dir2, asset_id, "v2", "gen2")
            if dir2
            else '<figure class="var missing"><div class="none">gen 2 pending</div></figure>'
        )

        picks = "".join(
            f'<button class="p" data-k="{asset_id}" data-p="{code}">{label}</button>'
            for code, label in PICKS
        )
        p1 = html.escape((asset.get("prompt_tail", "") or "")[:1200])
        p2 = html.escape((prompts2.get(asset_id, "") or "")[:1200])

        cards.append(
            f'<section class="card" id="{html.escape(asset_id)}">'
            f"<h2>{title}{badge}</h2>"
            f'<div class="rows">'
            f'<div class="gen gen1"><div class="glabel">generation 1</div>{left}</div>'
            f'<div class="gen gen2"><div class="glabel">generation 2</div>{right}</div>'
            f"</div>"
            f'<div class="pickrow" data-pick="{html.escape(asset_id)}">'
            f'<span class="plabel">Which generation won?</span>{picks}</div>'
            f'<textarea class="note" data-k="{html.escape(asset_id)}" rows="2" '
            f'placeholder="note on {html.escape(asset_id)} -- what changed, what still needs work"></textarea>'
            f"<details><summary>prompts</summary>"
            f'<p class="prompt"><b>gen1:</b> {p1}</p>'
            f'<p class="prompt"><b>gen2:</b> {p2}</p></details>'
            f"</section>"
        )

    page = TEMPLATE.replace("__CARDS__", "\n".join(cards))
    OUT.write_text(page, encoding="utf-8", newline="\n")
    print(f"[+] wrote {OUT}")
    print(f"[*] {len(cards)} concepts   gen1={rel1 or 'missing'}   gen2={rel2 or 'PENDING'}")
    if args.open:
        webbrowser.open(OUT.as_uri())
    return 0


TEMPLATE = """<!doctype html>
<meta charset="utf-8">
<title>Endgame concepts -- generation 1 vs 2</title>
<style>
  :root{--bg:#15151a;--fg:#e9e7e2;--dim:#96938c;--line:#33323b;--card:#1d1d24;
        --ok:#7fc08d;--warn:#d9bd6a;--no:#e2807c;--acc:#d9955c;--g2:#6f8fd6}
  @media(prefers-color-scheme:light){:root{--bg:#f6f5f2;--fg:#1a1a18;--dim:#63615c;
        --line:#d9d6ce;--card:#fff;--ok:#2f6b3a;--warn:#8a6a10;--no:#9c2b2b;--acc:#7a3b12;--g2:#31509b}}
  *{box-sizing:border-box}
  body{background:var(--bg);color:var(--fg);margin:0;padding:16px 18px 130px;
       font:14px/1.5 ui-monospace,Consolas,monospace}
  header{position:sticky;top:0;z-index:9;background:var(--bg);border-bottom:1px solid var(--line);
         padding:10px 0;margin-bottom:14px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
  h1{font-size:16px;margin:0}
  .card{border:1px solid var(--line);background:var(--card);border-radius:5px;padding:12px 14px;margin:0 0 18px}
  h2{font-size:14px;margin:0 0 10px}
  .new{color:var(--g2);border:1px solid var(--g2);border-radius:3px;padding:1px 6px;font-size:10px}
  .rows{display:grid;grid-template-columns:1fr 1fr;gap:18px}
  @media(max-width:1100px){.rows{grid-template-columns:1fr}}
  .gen{border:1px solid var(--line);border-radius:4px;padding:9px;display:grid;
       grid-template-columns:1fr 1fr;gap:9px}
  .gen2{border-color:var(--g2)}
  .glabel{grid-column:1/-1;color:var(--dim);font-size:11px;letter-spacing:.08em;text-transform:uppercase}
  .gen2 .glabel{color:var(--g2)}
  figure{margin:0}
  img{width:100%;height:auto;display:block;border:1px solid var(--line);border-radius:3px}
  figcaption{color:var(--dim);font-size:11px;margin:4px 0}
  .missing .none{display:flex;align-items:center;justify-content:center;height:120px;
                 color:var(--dim);border:1px dashed var(--line);border-radius:3px;font-size:12px}
  .btns{display:flex;gap:4px;margin:5px 0}
  button.v,button.p{padding:6px 4px;font:600 11px ui-monospace,monospace;cursor:pointer;
        background:transparent;color:var(--dim);border:1px solid var(--line);border-radius:3px}
  button.v{flex:1}
  button.p{padding:6px 12px}
  button.v:hover,button.p:hover{color:var(--fg)}
  .var[data-verdict="promote"] button.v[data-v="promote"]{background:var(--ok);color:#08120a;border-color:var(--ok)}
  .var[data-verdict="like"] button.v[data-v="like"]{background:var(--acc);color:#120a04;border-color:var(--acc)}
  .var[data-verdict="meh"] button.v[data-v="meh"]{background:var(--warn);color:#120e02;border-color:var(--warn)}
  .var[data-verdict="dislike"] button.v[data-v="dislike"]{background:var(--no);color:#170606;border-color:var(--no)}
  .var[data-verdict="dislike"] img{opacity:.4}
  .pickrow{display:flex;gap:7px;align-items:center;margin:11px 0 7px;flex-wrap:wrap}
  .plabel{color:var(--dim);font-size:12px}
  .pickrow[data-picked="gen1"] button.p[data-p="gen1"]{background:var(--acc);color:#120a04;border-color:var(--acc)}
  .pickrow[data-picked="gen2"] button.p[data-p="gen2"]{background:var(--g2);color:#fff;border-color:var(--g2)}
  .pickrow[data-picked="neither"] button.p[data-p="neither"]{background:var(--no);color:#170606;border-color:var(--no)}
  textarea.note{width:100%;background:var(--bg);color:var(--fg);border:1px solid var(--line);
                border-radius:3px;padding:6px;font:12px ui-monospace,monospace;resize:vertical}
  details{margin-top:9px}
  summary{color:var(--dim);cursor:pointer;font-size:12px}
  .prompt{color:var(--dim);font-size:11px;white-space:pre-wrap}
  #bar{position:fixed;left:0;right:0;bottom:0;background:var(--card);border-top:1px solid var(--line);
       padding:9px 16px;display:flex;gap:12px;align-items:center;font-size:12px;flex-wrap:wrap}
  #bar button{padding:7px 13px;font:600 12px ui-monospace,monospace;cursor:pointer;
              background:var(--acc);color:#120a04;border:0;border-radius:3px}
  #bar button.ghost{background:transparent;color:var(--dim);border:1px solid var(--line)}
  #out{width:100%;height:150px;display:none;margin-top:8px;background:var(--bg);color:var(--fg);
       border:1px solid var(--line);font:11px ui-monospace,monospace}
  .hint{color:var(--dim)}
</style>

<header>
  <h1>Endgame concepts -- generation 1 vs generation 2</h1>
  <span class="hint">The question that matters: did the notes work? Pick a winner per concept.</span>
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
const KEY = "endgame_gencompare_v1";
let state = JSON.parse(localStorage.getItem(KEY) || '{"verdicts":{},"picks":{},"notes":{}}');

function paint(){
  document.querySelectorAll(".var[data-key]").forEach(f=>{
    const v = state.verdicts[f.dataset.key];
    if(v) f.setAttribute("data-verdict", v); else f.removeAttribute("data-verdict");
  });
  document.querySelectorAll(".pickrow").forEach(r=>{
    const p = state.picks[r.dataset.pick];
    if(p) r.setAttribute("data-picked", p); else r.removeAttribute("data-picked");
  });
  document.querySelectorAll("textarea.note").forEach(t=>{
    if(state.notes[t.dataset.k] !== undefined && t.value === "") t.value = state.notes[t.dataset.k];
  });
  const picked = Object.keys(state.picks).length;
  const total = document.querySelectorAll(".pickrow").length;
  const g2 = Object.values(state.picks).filter(v=>v==="gen2").length;
  document.getElementById("prog").textContent =
    picked + " / " + total + " concepts picked  --  gen2 winning " + g2;
}
function save(){ localStorage.setItem(KEY, JSON.stringify(state)); paint(); }

document.querySelectorAll("button.v").forEach(b=>b.addEventListener("click", ()=>{
  const k = b.dataset.k;
  if(state.verdicts[k] === b.dataset.v) delete state.verdicts[k]; else state.verdicts[k] = b.dataset.v;
  save();
}));
document.querySelectorAll("button.p").forEach(b=>b.addEventListener("click", ()=>{
  const k = b.dataset.k;
  if(state.picks[k] === b.dataset.p) delete state.picks[k]; else state.picks[k] = b.dataset.p;
  save();
}));
document.querySelectorAll("textarea.note").forEach(t=>t.addEventListener("input", ()=>{
  if(t.value.trim()) state.notes[t.dataset.k] = t.value.trim(); else delete state.notes[t.dataset.k];
  localStorage.setItem(KEY, JSON.stringify(state));
}));

function payload(){
  return JSON.stringify({
    batch: "endgame_concepts gen1 vs gen2",
    generation_winner: state.picks,
    verdicts: state.verdicts,
    notes: state.notes
  }, null, 1);
}
document.getElementById("exp").addEventListener("click", ()=>{
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([payload()], {type:"application/json"}));
  a.download = "endgame_generation_compare.json"; a.click();
  document.getElementById("msg").textContent = "downloaded";
});
document.getElementById("copy").addEventListener("click", async ()=>{
  const out = document.getElementById("out");
  out.style.display = "block"; out.value = payload(); out.select();
  try { await navigator.clipboard.writeText(out.value); document.getElementById("msg").textContent = "copied"; }
  catch(e){ document.getElementById("msg").textContent = "select the box and copy"; }
});
document.getElementById("clr").addEventListener("click", ()=>{
  if(!confirm("Clear every verdict, pick and note?")) return;
  state = {verdicts:{},picks:{},notes:{}}; save();
  document.querySelectorAll("textarea.note").forEach(t=>t.value="");
});
paint();
</script>
"""


if __name__ == "__main__":
    raise SystemExit(main())
