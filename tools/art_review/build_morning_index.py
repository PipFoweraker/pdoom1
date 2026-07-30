#!/usr/bin/env python3
"""One index page over every generated art batch on disk.

Built 2026-07-30. Overnight produced eight batches across six directories; an
index beats remembering eight paths. Each batch gets a section with its own
thumbnails, its manifest's display names, and a link to the full-size master.

Deliberately read-only -- verdict capture lives in the dedicated tools
(build_generation_compare.py for gen1-vs-gen2, build_endgame_review.py for the
gen1 batch). This is the map, not the workbench.

Usage:
    python tools/art_review/build_morning_index.py [--open]
"""

import argparse
import html
import json
import subprocess
import webbrowser
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ART = REPO / "art_generated"
MANIFESTS = REPO / "tools" / "assets" / "manifests"
OUT = ART / "morning_index.html"

# (asset_type, manifest stem, section title, what question it answers)
BATCHES = [
    (
        "endgame_concepts",
        "endgame_concepts",
        "Generation 1 -- the original batch",
        "Reviewed aloud with Wanasai. Half kept, half rejected.",
    ),
    (
        "endgame_concepts_gen2",
        "endgame_concepts_gen2",
        "Generation 2 -- feedback applied",
        "Same ids as gen 1, rewritten under rules A1-A10 plus the per-concept notes.",
    ),
    (
        "doomfield_ladder",
        "doomfield_ladder",
        "The doom-field ladder",
        "One fixed street corner at six escalating levels. The endgame idea made visible.",
    ),
    (
        "wanasai_calls",
        "wanasai_calls",
        "Wanasai's calls, executed",
        "The atrium face argument settled by comparison, and the hero properly obscured.",
    ),
    (
        "treatment_sweep",
        "treatment_sweep",
        "Treatment sweep",
        "One subject, six renderings. Settles how this art should be made.",
    ),
    (
        "people_policy",
        "people_policy",
        "The A2 test",
        "No people vs silhouettes vs a varied group. Tests the most contested rule.",
    ),
    (
        "crisp_sweep",
        "crisp_sweep",
        "Crispness sweep",
        "Four liked subjects x soft / crisp / graphic, composition held constant.",
    ),
    (
        "new_subjects",
        "new_subjects",
        "New subjects",
        "Includes the office at low / mid / high doom -- the colour-architecture study.",
    ),
]


def load_manifest(stem: str) -> dict:
    path = MANIFESTS / f"{stem}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    result = subprocess.run(
        ["git", "show", f"origin/main:tools/assets/manifests/{stem}.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        return json.loads(result.stdout)
    return {}


def thumb(rel_root: str, directory: Path, asset_id: str, variant: str) -> str:
    for size in ("768", "1024", "512"):
        name = f"{asset_id}_{variant}_{size}.png"
        if (directory / name).exists():
            full = f"{asset_id}_{variant}_1536.png"
            href = f"{rel_root}/{full if (directory / full).exists() else name}"
            return (
                f'<figure><a href="{href}" target="_blank">'
                f'<img loading="lazy" src="{rel_root}/{name}" alt="{html.escape(asset_id)} {variant}">'
                f"</a><figcaption>{variant}</figcaption></figure>"
            )
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()

    sections, totals = [], []
    for asset_type, stem, title, blurb in BATCHES:
        directory = ART / asset_type / "v1"
        if not directory.is_dir():
            continue
        manifest = load_manifest(stem)
        assets = manifest.get("assets", [])
        rel_root = f"{asset_type}/v1"

        if not assets:  # manifest missing: fall back to whatever is on disk
            ids = sorted({p.name.rsplit("_v", 1)[0] for p in directory.glob("*_1024.png")})
            assets = [{"id": i, "display_name": i} for i in ids]

        cards, count = [], 0
        for asset in assets:
            asset_id = asset.get("id", "")
            figures = "".join(thumb(rel_root, directory, asset_id, v) for v in ("v1", "v2"))
            if not figures:
                continue
            count += figures.count("<figure>")
            cards.append(
                f'<div class="concept"><h3>{html.escape(asset.get("display_name") or asset_id)}'
                f'<span class="cid">{html.escape(asset_id)}</span></h3>'
                f'<div class="pair">{figures}</div></div>'
            )
        if not cards:
            continue
        totals.append((title, count))
        sections.append(
            f'<section class="batch"><h2>{html.escape(title)}'
            f'<span class="n">{count} images</span></h2>'
            f'<p class="blurb">{html.escape(blurb)}</p>'
            f'<div class="grid">{"".join(cards)}</div></section>'
        )

    summary = "".join(f"<li>{html.escape(t)} <b>{n}</b></li>" for t, n in totals)
    grand = sum(n for _, n in totals)
    page = TEMPLATE.replace("__SECTIONS__", "\n".join(sections))
    page = page.replace("__SUMMARY__", summary).replace("__GRAND__", str(grand))
    OUT.write_text(page, encoding="utf-8", newline="\n")
    print(f"[+] wrote {OUT}")
    print(f"[*] {len(sections)} batches, {grand} images")
    if args.open:
        webbrowser.open(OUT.as_uri())
    return 0


TEMPLATE = """<!doctype html>
<meta charset="utf-8">
<title>Art batches -- morning index</title>
<style>
  :root{--bg:#15151a;--fg:#e9e7e2;--dim:#96938c;--line:#33323b;--card:#1d1d24;--acc:#d9955c}
  @media(prefers-color-scheme:light){:root{--bg:#f6f5f2;--fg:#1a1a18;--dim:#63615c;
        --line:#d9d6ce;--card:#fff;--acc:#7a3b12}}
  *{box-sizing:border-box}
  body{background:var(--bg);color:var(--fg);margin:0;padding:18px 20px 80px;
       font:14px/1.55 ui-monospace,Consolas,monospace}
  h1{font-size:17px;margin:0 0 6px}
  .lead{color:var(--dim);margin:0 0 18px}
  .lead a{color:var(--acc)}
  ul.sum{color:var(--dim);font-size:12px;columns:2;margin:0 0 22px;padding-left:18px}
  .batch{border-top:1px solid var(--line);padding-top:14px;margin-bottom:26px}
  h2{font-size:14px;margin:0 0 4px;color:var(--acc);letter-spacing:.03em}
  .n{color:var(--dim);font-weight:400;font-size:11px;margin-left:9px}
  .blurb{color:var(--dim);font-size:12px;margin:0 0 12px}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(430px,1fr));gap:16px}
  .concept{background:var(--card);border:1px solid var(--line);border-radius:4px;padding:10px}
  h3{font-size:12px;margin:0 0 8px;font-weight:600}
  .cid{color:var(--dim);font-weight:400;margin-left:8px;font-size:11px}
  .pair{display:grid;grid-template-columns:1fr 1fr;gap:8px}
  figure{margin:0}
  img{width:100%;height:auto;display:block;border:1px solid var(--line);border-radius:3px}
  figcaption{color:var(--dim);font-size:10px;margin-top:3px}
</style>

<h1>Art batches -- morning index</h1>
<p class="lead">
  __GRAND__ images across eight batches, generated overnight 2026-07-29/30.
  Verdict capture lives elsewhere: <b>generation_compare.html</b> for gen1 vs gen2
  (buttons, notes, and a which-generation-won pick), and <b>endgame_concepts/review.html</b>
  for the original batch. Prompt language is written up in
  <b>docs/art/PROMPT_RECIPES_2026-07-29.md</b>.
</p>
<ul class="sum">__SUMMARY__</ul>

__SECTIONS__
"""


if __name__ == "__main__":
    raise SystemExit(main())
