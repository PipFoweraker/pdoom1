#!/usr/bin/env python3
"""Local art-review app for P(Doom)1 -- ONE place to review ALL the art.

It serves both art tracks in a single gallery:
  * pixellab sprites/office-sim under  art_source/**            (committed)
  * gpt-image icons/banners/bg/textures under art_generated/**  (gitignored, ~1.1 GB)

Per asset you get a clickable keep / maybe / reroll verdict, a free-text NOTE
field and optional comma-separated TAGS. Every edit AUTO-PERSISTS to a real file
on disk -- tools/art_review/review_state.json -- via a POST endpoint, so a review
survives across sittings, can be revised over many sessions, and is a clean input
for promote/reroll tooling. (No browser localStorage: too fragile for multi-session.)

Nothing is embedded or copied: PNGs stream live from disk through /img?p=<relpath>,
so the big gitignored art_generated/ tree is never duplicated or committed.

Run (stdlib only -- no Flask/deps):
    python tools/art_review/serve_review.py                  # http://127.0.0.1:8777
    python tools/art_review/serve_review.py --port 9000
    python tools/art_review/serve_review.py --art-root <dir> # when the art lives elsewhere
        # e.g. running from a git worktree while art_generated/ is in the main checkout:
        # python tools/art_review/serve_review.py --art-root /path/to/main/checkout

State file shape (the pipeline contract):
    {
      "<asset_id>": {
        "verdict": "keep" | "maybe" | "reroll" | null,
        "note":    "free text",
        "tags":    ["tag", ...],
        "updated_at": "2026-07-19T10:11:12.345678+00:00"
      },
      ...
    }

asset_id conventions (stable + pipeline-friendly):
    gen:<category>:<base_id>:<variant>   e.g. gen:game_icons:icon_doom:v2
    px:<relpath under art_source>        e.g. px:pixellab_2026-07-16/style_matrix/baseline__desk
"""
import argparse
import html
import json
import os
import pathlib
import re
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urlparse

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
STATE_PATH = HERE / "review_state.json"

# generated file names: "<id>[_vN]_<size>.png"; strip _<size>, then optional _vN
_SIZE_RE = re.compile(r"^(.+?)_(\d+)\.png$")
_VAR_RE = re.compile(r"^(.+)_v(\d+)$")
# pixellab rotation sheets (one direction each) are not review images
_ROT_RE = re.compile(r"_(north|south|east|west|north-east|north-west|south-east|south-west)$")
# prefer a mid size to show; fall back to whatever exists
_SIZE_PREF = ["512", "256", "1024", "128", "64"]

VALID_VERDICTS = {"keep", "maybe", "reroll"}

# ordered generated categories (label); any other dirs found are appended
_GEN_CATS = [
    ("game_icons", "Game icons"),
    ("ui_icons", "UI icons"),
    ("hero_banners", "Hero banners"),
    ("screen_backgrounds", "Screen backgrounds"),
    ("terminal_textures", "Terminal textures"),
]

GROUP_GEN = "Generated (gpt-image)"
GROUP_PX = "Pixellab (art_source)"


def esc(s):
    return html.escape(str(s or ""), quote=True)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def pick_size(sizes):
    """sizes: {size_str: filename}. Return the preferred representative size key."""
    for p in _SIZE_PREF:
        if p in sizes:
            return p
    return max(sizes, key=lambda z: int(z))


# ------------------------------------------------------------------ scanning
def scan_generated(art_root):
    """Group art_generated/<cat>/v1/*.png into (base_id, variant) units, one
    representative size each. Returns a list of section dicts."""
    base = art_root / "art_generated"
    if not base.is_dir():
        return []
    cats = list(_GEN_CATS)
    known = {c for c, _ in cats}
    for extra in sorted(
        p.name for p in base.iterdir() if p.is_dir() and p.name not in known and p.name != "logs"
    ):
        cats.append((extra, extra.replace("_", " ").title()))

    sections = []
    for cat, title in cats:
        d = base / cat / "v1"
        if not d.is_dir():
            continue
        units = {}  # (base_id, variant) -> {size: filename}
        for f in sorted(os.listdir(d)):
            if not f.endswith(".png"):
                continue
            m = _SIZE_RE.match(f)
            if not m:
                continue
            stem, size = m.group(1), m.group(2)
            vm = _VAR_RE.match(stem)
            base_id, var = (vm.group(1), "v" + vm.group(2)) if vm else (stem, "v1")
            units.setdefault((base_id, var), {})[size] = f
        if not units:
            continue
        cells = []
        for base_id, var in sorted(units):
            sizes = units[(base_id, var)]
            size = pick_size(sizes)
            rel = f"art_generated/{cat}/v1/{sizes[size]}"
            cells.append(
                {
                    "asset_id": f"gen:{cat}:{base_id}:{var}",
                    "label": f"{base_id}  {var}",
                    "img": rel,
                    "meta": f"{size}px",
                }
            )
        sections.append(
            {
                "id": "gen-" + slug(cat),
                "group": GROUP_GEN,
                "title": title,
                "cells": cells,
            }
        )
    return sections


def scan_pixellab(art_root):
    """Walk art_source/**; every leaf dir holding review PNGs becomes a section."""
    base = art_root / "art_source"
    if not base.is_dir():
        return []
    sections = []
    for dp, _dn, fn in os.walk(base):
        pngs = [f for f in sorted(fn) if f.endswith(".png") and not _ROT_RE.search(f[:-4])]
        if not pngs:
            continue
        dpath = pathlib.Path(dp)
        rel_under_src = dpath.relative_to(base).as_posix()  # e.g. pixellab_2026-07-16/style_matrix
        cells = []
        for f in pngs:
            stem = f[:-4]
            rel = f"art_source/{rel_under_src}/{f}"
            cells.append(
                {
                    "asset_id": f"px:{rel_under_src}/{stem}",
                    "label": stem,
                    "img": rel,
                    "meta": "",
                }
            )
        parts = rel_under_src.split("/")
        title = " / ".join(parts[-2:]) if len(parts) > 1 else rel_under_src
        sections.append(
            {
                "id": "px-" + slug(rel_under_src),
                "group": GROUP_PX,
                "title": title,
                "cells": cells,
            }
        )
    sections.sort(key=lambda s: s["id"])
    return sections


def scan_all(art_root):
    return scan_generated(art_root) + scan_pixellab(art_root)


# ------------------------------------------------------------------ state I/O
_LOCK = threading.Lock()


def load_state():
    if STATE_PATH.is_file():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return {}
    return {}


def save_state(state):
    tmp = STATE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(STATE_PATH)


def normalize_tags(raw):
    if raw is None:
        return None
    if isinstance(raw, str):
        raw = raw.split(",")
    if not isinstance(raw, list):
        return []
    out = []
    for t in raw:
        t = str(t).strip()
        if t and t not in out:
            out.append(t)
    return out


def apply_patch(patch):
    """Merge one {asset_id, verdict?, note?, tags?} patch into the state file.
    Returns (status, response_dict)."""
    asset_id = patch.get("asset_id")
    if not asset_id or not isinstance(asset_id, str):
        return 400, {"ok": False, "error": "missing asset_id"}
    with _LOCK:
        state = load_state()
        entry = state.get(asset_id, {})
        entry.setdefault("verdict", None)
        entry.setdefault("note", "")
        entry.setdefault("tags", [])
        if "verdict" in patch:
            v = patch["verdict"]
            entry["verdict"] = v if v in VALID_VERDICTS else None
        if "note" in patch:
            entry["note"] = "" if patch["note"] is None else str(patch["note"])
        if "tags" in patch:
            entry["tags"] = normalize_tags(patch["tags"]) or []
        entry["updated_at"] = now_iso()
        # drop an entry that carries no signal, to keep the file clean
        if not entry["verdict"] and not entry["note"].strip() and not entry["tags"]:
            state.pop(asset_id, None)
            saved = None
        else:
            state[asset_id] = entry
            saved = entry
        save_state(state)
    return 200, {"ok": True, "asset_id": asset_id, "entry": saved}


# ------------------------------------------------------------------ rendering
def render_cell(c):
    aid = esc(c["asset_id"])
    src = "/img?p=" + quote(c["img"], safe="/")
    meta = f'<span class="meta">{esc(c["meta"])}</span>' if c["meta"] else ""
    return f"""
      <div class="cell" data-asset="{aid}">
        <div class="stage"><img loading="lazy" src="{esc(src)}" alt="{esc(c['label'])}"></div>
        <div class="cap"><span class="lbl">{esc(c['label'])}</span>{meta}</div>
        <div class="idline">{aid}</div>
        <div class="verdict" role="group" aria-label="Verdict">
          <button type="button" class="vbtn" data-v="keep" title="Keep (K)">keep</button>
          <button type="button" class="vbtn" data-v="maybe" title="Maybe (M)">maybe</button>
          <button type="button" class="vbtn" data-v="reroll" title="Re-roll (R)">re-roll</button>
        </div>
        <textarea class="note" rows="2" placeholder="note... (N)" aria-label="Note"></textarea>
        <input type="text" class="tags" placeholder="tags, comma, separated" aria-label="Tags">
      </div>"""


def render_section(s):
    cells = "".join(render_cell(c) for c in s["cells"])
    return f"""
    <section id="{esc(s['id'])}" class="sec">
      <h2>{esc(s['title'])} <span class="seccount">{len(s['cells'])}</span></h2>
      <div class="grid">{cells}</div>
    </section>"""


def render_nav(sections):
    out = []
    last_group = None
    for s in sections:
        if s["group"] != last_group:
            out.append(f'<span class="navtitle">{esc(s["group"])}</span>')
            last_group = s["group"]
        out.append(
            f'<a class="chip" href="#{esc(s["id"])}">{esc(s["title"])}'
            f'<b>{len(s["cells"])}</b></a>'
        )
    return "".join(out)


def render_page(art_root):
    sections = scan_all(art_root)
    total = sum(len(s["cells"]) for s in sections)
    gen_total = sum(len(s["cells"]) for s in sections if s["group"] == GROUP_GEN)
    body = "".join(render_section(s) for s in sections)
    nav = render_nav(sections)
    state = load_state()
    subtitle = (
        f"{total} assets across {len(sections)} sections "
        f"({gen_total} generated + {total - gen_total} pixellab). "
        f"Verdicts, notes and tags auto-save to review_state.json on every edit."
    )
    return (
        _TEMPLATE.replace("{{SUBTITLE}}", esc(subtitle))
        .replace("{{NAV}}", nav)
        .replace("{{BODY}}", body)
        .replace("{{SEED}}", json.dumps(state))
    )


# ------------------------------------------------------------------ HTTP
class ReviewServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, addr, art_root):
        self.art_root = art_root.resolve()
        super().__init__(addr, ReviewHandler)


class ReviewHandler(BaseHTTPRequestHandler):
    server_version = "PdoomArtReview/1.0"

    def log_message(self, fmt, *args):  # quieter console
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            self._send(200, render_page(self.server.art_root), "text/html; charset=utf-8")
        elif u.path == "/img":
            self._serve_img(parse_qs(u.query).get("p", [""])[0])
        elif u.path == "/api/state":
            self._send(200, json.dumps(load_state(), indent=2, sort_keys=True))
        elif u.path == "/favicon.ico":
            self._send(204, b"", "image/x-icon")
        else:
            self._send(404, json.dumps({"ok": False, "error": "not found"}))

    def do_POST(self):
        u = urlparse(self.path)
        if u.path != "/api/state":
            self._send(404, json.dumps({"ok": False, "error": "not found"}))
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            patch = json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, TypeError):
            self._send(400, json.dumps({"ok": False, "error": "bad json"}))
            return
        code, resp = apply_patch(patch)
        self._send(code, json.dumps(resp))

    def _serve_img(self, rel):
        # sandbox: resolve under art_root, must stay inside it, must be a .png
        root = self.server.art_root
        rel = rel.lstrip("/")
        target = (root / rel).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            self._send(403, json.dumps({"ok": False, "error": "forbidden"}))
            return
        if target.suffix.lower() != ".png" or not target.is_file():
            self._send(404, json.dumps({"ok": False, "error": "no image"}))
            return
        self._send(200, target.read_bytes(), "image/png")


# ------------------------------------------------------------------ template
_TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>P(Doom)1 -- Art Review</title>
<style>
  :root{
    --ground:#17120e;--panel:#211a14;--panel-2:#2b221a;--ink:#ece0cf;--ink-dim:#a9977f;--ink-faint:#6f6250;
    --amber:#e8a33d;--amber-deep:#c07a1f;--win:#6fae86;--line:#3a2e22;--checker-a:#201811;--checker-b:#180f09;
    --field:#120d09;--shadow:rgba(0,0,0,.45);--keep:#6fae86;--maybe:#e8a33d;--reroll:#d8695a;
  }
  @media (prefers-color-scheme:light){:root{
    --ground:#efe6d6;--panel:#f7efe0;--panel-2:#fbf5e9;--ink:#2b2116;--ink-dim:#6b5b45;--ink-faint:#9a876c;
    --amber:#b9741a;--amber-deep:#8f5710;--win:#3f8a5c;--line:#ddccb0;--checker-a:#e6dac4;--checker-b:#ded1b8;
    --field:#fffaf0;--shadow:rgba(80,55,20,.18);--keep:#3f8a5c;--maybe:#b9741a;--reroll:#c14a3a;}}
  *{box-sizing:border-box}
  body{margin:0;background:var(--ground);color:var(--ink);font-family:ui-sans-serif,system-ui,"Segoe UI",Helvetica,Arial,sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased}
  img{image-rendering:pixelated;image-rendering:crisp-edges;max-width:100%;height:auto;display:block}
  a{color:inherit}
  .wrap{max-width:1320px;margin:0 auto;padding:1.6rem 1.3rem 6rem}
  .eyebrow{font-family:ui-monospace,Consolas,monospace;font-size:.7rem;letter-spacing:.22em;text-transform:uppercase;color:var(--amber);margin:0 0 .5rem}
  h1{font-family:ui-monospace,"Cascadia Code",Consolas,monospace;font-weight:700;font-size:clamp(1.5rem,3.4vw,2.2rem);line-height:1.05;margin:0 0 .4rem}
  .lede{max-width:80ch;color:var(--ink-dim);font-size:.95rem;margin:0}
  /* sticky section nav */
  .nav{position:sticky;top:0;z-index:40;display:flex;flex-wrap:wrap;align-items:center;gap:.35rem;
    padding:.6rem .3rem;margin:1rem 0 1.4rem;background:color-mix(in srgb,var(--ground) 90%,transparent);
    backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
  .navtitle{font-family:ui-monospace,Consolas,monospace;font-size:.64rem;letter-spacing:.14em;text-transform:uppercase;
    color:var(--ink-faint);margin:0 .3rem 0 .5rem;flex-basis:100%}
  .navtitle:first-child{margin-top:0}
  .chip{font-family:ui-monospace,Consolas,monospace;font-size:.72rem;text-decoration:none;color:var(--ink-dim);
    border:1px solid var(--line);border-radius:20px;padding:.22rem .6rem;display:inline-flex;gap:.35rem;align-items:center;white-space:nowrap}
  .chip:hover{color:var(--ink);border-color:var(--ink-faint)}
  .chip b{color:var(--amber);font-weight:600}
  .sec{margin:2.2rem 0;scroll-margin-top:70px}
  .sec h2{font-family:ui-monospace,Consolas,monospace;font-size:1rem;letter-spacing:.02em;margin:0 0 .9rem;
    display:flex;align-items:center;gap:.7rem;padding-bottom:.4rem;border-bottom:1px solid var(--line)}
  .seccount{font-size:.72rem;color:var(--ink-faint);border:1px solid var(--line);border-radius:10px;padding:0 .5rem}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:.9rem}
  .cell{display:flex;flex-direction:column;gap:.4rem;background:var(--panel);border:1px solid var(--line);
    border-radius:12px;padding:.7rem;scroll-margin:80px}
  .cell.v-keep{border-color:var(--keep);box-shadow:0 0 0 1px var(--keep)}
  .cell.v-maybe{border-color:var(--maybe);box-shadow:0 0 0 1px var(--maybe)}
  .cell.v-reroll{border-color:var(--reroll);box-shadow:0 0 0 1px var(--reroll)}
  .cell.focused{outline:2px solid var(--amber);outline-offset:2px}
  .stage{background-color:var(--checker-a);background-image:linear-gradient(45deg,var(--checker-b) 25%,transparent 25%),linear-gradient(-45deg,var(--checker-b) 25%,transparent 25%),linear-gradient(45deg,transparent 75%,var(--checker-b) 75%),linear-gradient(-45deg,transparent 75%,var(--checker-b) 75%);background-size:14px 14px;background-position:0 0,0 7px,7px -7px,-7px 0;border:1px solid var(--line);border-radius:8px;padding:.6rem;display:grid;place-items:center;min-height:150px}
  .stage img{width:auto;max-height:180px}
  .cap{display:flex;align-items:baseline;justify-content:space-between;gap:.4rem}
  .lbl{font-size:.8rem;font-family:ui-monospace,Consolas,monospace;word-break:break-word;line-height:1.25}
  .meta{font-size:.66rem;color:var(--ink-faint);font-family:ui-monospace,Consolas,monospace;white-space:nowrap}
  .idline{font-size:.6rem;color:var(--ink-faint);font-family:ui-monospace,Consolas,monospace;word-break:break-all;opacity:.7}
  .verdict{display:flex;gap:.25rem}
  .vbtn{flex:1;font-family:ui-monospace,Consolas,monospace;font-size:.63rem;text-transform:uppercase;letter-spacing:.03em;
    padding:.3rem .1rem;border-radius:5px;border:1px solid var(--line);background:var(--field);color:var(--ink-dim);cursor:pointer;transition:.1s}
  .vbtn:hover{color:var(--ink);border-color:var(--ink-faint)}
  .vbtn:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
  .vbtn.on[data-v="keep"]{background:var(--keep);border-color:var(--keep);color:#12251a}
  .vbtn.on[data-v="maybe"]{background:var(--maybe);border-color:var(--maybe);color:#2a1e08}
  .vbtn.on[data-v="reroll"]{background:var(--reroll);border-color:var(--reroll);color:#2a1210}
  .note,.tags{width:100%;background:var(--field);color:var(--ink);border:1px solid var(--line);border-radius:6px;
    padding:.35rem .5rem;font-size:.74rem;font-family:ui-sans-serif,system-ui,sans-serif}
  .note{resize:vertical;min-height:2.2rem;line-height:1.4}
  .tags{font-family:ui-monospace,Consolas,monospace;font-size:.68rem}
  .note:focus-visible,.tags:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
  /* keyboard legend */
  .kbd-legend{position:fixed;top:10px;right:10px;z-index:60;display:flex;flex-direction:column;gap:.28rem;
    background:color-mix(in srgb,var(--panel) 92%,transparent);border:1px solid var(--line);border-radius:9px;
    padding:.5rem .6rem;font-family:ui-monospace,Consolas,monospace;font-size:.64rem;color:var(--ink-dim);
    pointer-events:none;box-shadow:0 2px 12px var(--shadow);backdrop-filter:blur(4px)}
  .kbd-legend b{color:var(--amber);font-weight:400}
  .kbd-legend kbd{display:inline-block;min-width:1.1em;text-align:center;padding:.05rem .3rem;margin-right:.1rem;
    border:1px solid var(--line);border-bottom-width:2px;border-radius:4px;background:var(--field);color:var(--ink);font-size:.6rem}
  /* status/export bar */
  .bar{position:sticky;bottom:0;margin:2.5rem -1.3rem -6rem;padding:.9rem 1.3rem;
    background:color-mix(in srgb,var(--ground) 90%,transparent);backdrop-filter:blur(8px);border-top:1px solid var(--line);
    display:flex;align-items:center;gap:1rem;flex-wrap:wrap}
  .tally{font-family:ui-monospace,Consolas,monospace;font-size:.78rem;color:var(--ink-dim)}
  .tally b{color:var(--ink)}
  .tally .k{color:var(--keep)}.tally .m{color:var(--maybe)}.tally .r{color:var(--reroll)}
  .save{font-family:ui-monospace,Consolas,monospace;font-size:.72rem;color:var(--ink-faint)}
  .save.ok{color:var(--keep)}.save.err{color:var(--reroll)}
  .spacer{flex:1}
  .btn{font-family:ui-monospace,Consolas,monospace;font-size:.78rem;padding:.45rem .85rem;border-radius:7px;
    border:1px solid var(--amber);background:var(--amber);color:#20140a;font-weight:700;cursor:pointer}
  .btn:hover{background:var(--amber-deep);border-color:var(--amber-deep)}
  .btn.ghost{background:transparent;color:var(--ink-dim);border-color:var(--line);font-weight:400}
  .btn.ghost:hover{color:var(--ink);border-color:var(--ink-faint)}
  dialog{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:12px;padding:0;max-width:min(760px,92vw);width:100%}
  dialog::backdrop{background:rgba(0,0,0,.55)}
  .modal-head{display:flex;align-items:center;justify-content:space-between;padding:.9rem 1.1rem;border-bottom:1px solid var(--line)}
  .modal-head h3{margin:0;font-size:1rem;font-family:ui-monospace,Consolas,monospace}
  .modal-body{padding:1rem 1.1rem}
  #exporttext{width:100%;min-height:340px;resize:vertical;background:var(--field);color:var(--ink);border:1px solid var(--line);
    border-radius:8px;padding:.8rem;font-family:ui-monospace,Consolas,monospace;font-size:.74rem;line-height:1.5;white-space:pre}
  footer{margin-top:2.5rem;padding-top:1.2rem;border-top:1px solid var(--line);color:var(--ink-faint);font-size:.76rem;font-family:ui-monospace,Consolas,monospace}
  @media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
  @media (max-width:640px){.kbd-legend{display:none}}
</style></head><body>
<div class="kbd-legend" aria-hidden="true">
  <span><kbd>&larr;</kbd><kbd>&rarr;</kbd> move focus</span>
  <span><b>K</b> keep &middot; <b>M</b> maybe &middot; <b>R</b> re-roll</span>
  <span><kbd>N</kbd> note &middot; <kbd>Esc</kbd> back</span>
</div>
<div class="wrap">
  <p class="eyebrow">P(Doom)1 &middot; art direction &middot; local review app</p>
  <h1>Art review -- all tracks, one place</h1>
  <p class="lede">{{SUBTITLE}}</p>
  <nav class="nav">{{NAV}}</nav>
  {{BODY}}
  <div class="bar">
    <div class="tally" id="tally"></div>
    <div class="save" id="save">state file: tools/art_review/review_state.json</div>
    <div class="spacer"></div>
    <button type="button" class="btn ghost" id="exportbtn">View state JSON</button>
  </div>
  <footer>Every verdict / note / tag POSTs to the local server and is written to
  <b>review_state.json</b> on disk -- reload any time, across sessions, and your review is still here.</footer>
</div>
<dialog id="exportdlg">
  <div class="modal-head"><h3>// review_state.json</h3><button type="button" class="btn ghost" id="copybtn">copy</button></div>
  <div class="modal-body"><textarea id="exporttext" readonly></textarea></div>
</dialog>
<script>
(function(){
  "use strict";
  var SEED={{SEED}};
  var CELLS=[].slice.call(document.querySelectorAll('.cell'));
  var cur=-1, timers={};

  function saveMsg(txt,cls){var s=document.getElementById('save');s.textContent=txt;s.className='save '+(cls||'');}

  function persist(id,patch){
    patch.asset_id=id;
    saveMsg('saving...','');
    fetch('/api/state',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(patch)})
      .then(function(r){return r.json();})
      .then(function(j){
        if(j.ok){SEED[id]=j.entry||{};if(!j.entry)delete SEED[id];
          var t=new Date().toLocaleTimeString();saveMsg('saved '+t,'ok');tally();}
        else{saveMsg('save error: '+(j.error||'?'),'err');}
      })
      .catch(function(){saveMsg('save failed (server down?)','err');});
  }
  function debounce(id,patch){clearTimeout(timers[id]);timers[id]=setTimeout(function(){persist(id,patch);},450);}

  function applyVerdict(cell,v){
    cell.classList.remove('v-keep','v-maybe','v-reroll');
    if(v)cell.classList.add('v-'+v);
    cell.querySelectorAll('.vbtn').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-v')===v);});
  }
  function curVerdict(cell){
    if(cell.classList.contains('v-keep'))return 'keep';
    if(cell.classList.contains('v-maybe'))return 'maybe';
    if(cell.classList.contains('v-reroll'))return 'reroll';
    return null;
  }
  function setVerdict(cell,v){
    var id=cell.getAttribute('data-asset');
    if(curVerdict(cell)===v)v=null;    // toggle off
    applyVerdict(cell,v);
    persist(id,{verdict:v});
  }
  function parseTags(str){return (str||'').split(',').map(function(t){return t.trim();}).filter(Boolean);}

  // hydrate every cell from the on-disk state the server embedded
  CELLS.forEach(function(cell,idx){
    var id=cell.getAttribute('data-asset'), s=SEED[id]||{};
    applyVerdict(cell,s.verdict||null);
    var note=cell.querySelector('.note'); if(note)note.value=s.note||'';
    var tags=cell.querySelector('.tags'); if(tags)tags.value=(s.tags||[]).join(', ');
    cell.querySelectorAll('.vbtn').forEach(function(btn){
      btn.addEventListener('click',function(){setFocus(idx,false);setVerdict(cell,btn.getAttribute('data-v'));});
    });
    if(note)note.addEventListener('input',function(e){debounce(id,{note:e.target.value});});
    if(tags)tags.addEventListener('input',function(e){debounce(id,{tags:parseTags(e.target.value)});});
    cell.addEventListener('mousedown',function(){setFocus(idx,false);});
  });

  // keyboard nav (deferred polish, but cheap + the dev likes it)
  function setFocus(i,scroll){
    if(i<0||i>=CELLS.length)return;
    if(cur>=0&&CELLS[cur])CELLS[cur].classList.remove('focused');
    cur=i;var c=CELLS[cur];c.classList.add('focused');
    if(scroll)c.scrollIntoView({block:'nearest',inline:'nearest'});
  }
  function move(d){var i=cur<0?0:cur+d;if(i<0)i=0;if(i>=CELLS.length)i=CELLS.length-1;setFocus(i,true);}
  document.addEventListener('keydown',function(e){
    var t=e.target,tag=(t.tagName||'').toLowerCase();
    if(tag==='input'||tag==='textarea'||t.isContentEditable){if(e.key==='Escape')t.blur();return;}
    if(e.ctrlKey||e.metaKey||e.altKey)return;
    var k=e.key;
    if(k==='ArrowRight'||k==='ArrowDown'){move(1);e.preventDefault();}
    else if(k==='ArrowLeft'||k==='ArrowUp'){move(-1);e.preventDefault();}
    else if(k==='k'||k==='K'){if(cur>=0){setVerdict(CELLS[cur],'keep');e.preventDefault();}}
    else if(k==='m'||k==='M'){if(cur>=0){setVerdict(CELLS[cur],'maybe');e.preventDefault();}}
    else if(k==='r'||k==='R'){if(cur>=0){setVerdict(CELLS[cur],'reroll');e.preventDefault();}}
    else if(k==='n'||k==='N'||k==='Enter'){if(cur<0)setFocus(0,true);var n=CELLS[cur].querySelector('.note');if(n){n.focus();}e.preventDefault();}
    else if(k==='Escape'){if(cur>=0){CELLS[cur].classList.remove('focused');cur=-1;}}
  });

  function tally(){
    var k=0,m=0,r=0,notes=0;
    for(var id in SEED){var s=SEED[id]||{};if(s.verdict==='keep')k++;else if(s.verdict==='maybe')m++;else if(s.verdict==='reroll')r++;
      if(s.note&&s.note.trim())notes++;}
    document.getElementById('tally').innerHTML='<span class="k">keep '+k+'</span> &middot; '+
      '<span class="m">maybe '+m+'</span> &middot; <span class="r">re-roll '+r+'</span> &middot; '+
      '<b>'+notes+'</b> notes';
  }
  tally();

  var dlg=document.getElementById('exportdlg'),txt=document.getElementById('exporttext');
  document.getElementById('exportbtn').addEventListener('click',function(){
    fetch('/api/state').then(function(r){return r.text();}).then(function(s){
      txt.value=s;if(typeof dlg.showModal==='function')dlg.showModal();else alert(s);txt.focus();txt.select();
    });
  });
  document.getElementById('copybtn').addEventListener('click',function(){
    txt.select();try{document.execCommand('copy');}catch(e){}
    if(navigator.clipboard)navigator.clipboard.writeText(txt.value).catch(function(){});
    var b=this;b.textContent='copied';setTimeout(function(){b.textContent='copy';},1400);
  });
})();
</script>
</body></html>
"""


def main():
    ap = argparse.ArgumentParser(description="Local P(Doom)1 art-review app (stdlib only).")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8777)
    ap.add_argument(
        "--art-root",
        default=str(REPO),
        help="dir containing art_source/ and art_generated/ (default: repo root; "
        "point at the main checkout when running from a worktree).",
    )
    ap.add_argument("--no-browser", action="store_true", help="do not auto-open a browser")
    args = ap.parse_args()

    art_root = pathlib.Path(args.art_root).resolve()
    httpd = ReviewServer((args.host, args.port), art_root)
    url = f"http://{args.host}:{args.port}/"
    sections = scan_all(art_root)
    total = sum(len(s["cells"]) for s in sections)
    gen = sum(len(s["cells"]) for s in sections if s["group"] == GROUP_GEN)
    print(f"art root : {art_root}")
    print(f"state    : {STATE_PATH}")
    print(
        f"assets   : {total} cells in {len(sections)} sections ({gen} generated, {total - gen} pixellab)"
    )
    print(f"serving  : {url}   (Ctrl-C to stop)")
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
