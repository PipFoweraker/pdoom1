#!/usr/bin/env python3
"""Local art-review app for P(Doom)1 -- ONE place to review ALL the art.

It serves both art tracks in a single gallery:
  * pixellab sprites/office-sim under  art_source/**            (committed)
  * gpt-image icons/banners/bg/textures under art_generated/**  (gitignored, ~1.1 GB)

Per asset you get a clickable keep / iterate / discard verdict, a free-text NOTE
field and optional comma-separated TAGS. Every edit AUTO-PERSISTS to a real file
on disk -- tools/art_review/review_state.json -- via a POST endpoint, so a review
survives across sittings, can be revised over many sessions, and is a clean input
for promote/regenerate tooling. (No browser localStorage: too fragile for multi-session.)

Verdict model (v2):
  * keep    -- accept it (green).
  * iterate -- on-brief but not final; regenerate to compare/hone. The DEFAULT
               "slight reject". (amber)
  * discard -- OFF-brief / wrong direction; note is prompted-for. NOT regenerated
               -- it signals the brief itself needs reconsidering. (red)
"Decided" = keep OR discard (moves to the Decisions archive). iterate stays live
(it expects a fresh variant). Old "maybe" and "reroll" verdicts migrate to
"iterate" transparently on load.

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
        "verdict": "keep" | "iterate" | "discard" | null,
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

VALID_VERDICTS = {"keep", "iterate", "discard"}
# old verdicts -> new; applied on every state load so pre-v2 files just work.
_VERDICT_MIGRATE = {"maybe": "iterate", "reroll": "iterate"}


def migrate_verdict(v):
    """Map a stored verdict onto the v2 model. keep/iterate/discard pass through;
    legacy maybe/reroll fold into iterate; anything else -> None."""
    if v in VALID_VERDICTS:
        return v
    return _VERDICT_MIGRATE.get(v)


# ordered generated categories (label); any other dirs found are appended
_GEN_CATS = [
    ("game_icons", "Game icons"),
    ("ui_icons", "UI icons"),
    ("hero_banners", "Hero banners"),
    ("screen_backgrounds", "Screen backgrounds"),
    ("terminal_textures", "Terminal textures"),
]

# where each generated category shows up in-game -- batch-level context so the
# reviewer knows what they are approving FOR and where it will appear.
_GEN_HOME = {
    "game_icons": "Action / resource icons on the PLAN buttons + the resource bar",
    "ui_icons": "UI controls -- buttons, toggles, window chrome",
    "hero_banners": "Wide hero banners behind menu / screen titles",
    "screen_backgrounds": "Full-screen backdrops -- menus, office floor, records room",
    "terminal_textures": "CRT / terminal surface textures + frame overlays",
}


def _px_home(rel):
    r = rel.lower()
    if "tileset" in r or "tiles" in r:
        return "Office-sim floor / wall tilesets"
    if "portrait" in r:
        return "Researcher / staff portraits"
    if "style_matrix" in r or "baseline" in r:
        return "Style exploration -- direction-finding, not a shipped asset"
    return "Pixellab office-sim sprites / props"


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
                    "base": base_id,
                }
            )
        sections.append(
            {
                "id": "gen-" + slug(cat),
                "group": GROUP_GEN,
                "title": title,
                "home": _GEN_HOME.get(cat, ""),
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
                    "base": stem,
                }
            )
        parts = rel_under_src.split("/")
        title = " / ".join(parts[-2:]) if len(parts) > 1 else rel_under_src
        sections.append(
            {
                "id": "px-" + slug(rel_under_src),
                "group": GROUP_PX,
                "title": title,
                "home": _px_home(rel_under_src),
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
            state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return {}
        return _migrate_state(state)
    return {}


def _migrate_state(state):
    """In-memory migration of legacy verdicts (maybe/reroll -> iterate). Lossless
    for the reviewer's intent: keep stays keep, everything soft folds to iterate,
    discard is new. Persisted opportunistically the next time an entry is saved."""
    if not isinstance(state, dict):
        return {}
    for entry in state.values():
        if isinstance(entry, dict) and "verdict" in entry:
            entry["verdict"] = migrate_verdict(entry.get("verdict"))
    return state


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
def render_cell(c, in_set=False):
    aid = esc(c["asset_id"])
    src = "/img?p=" + quote(c["img"], safe="/")
    meta = f'<span class="meta">{esc(c["meta"])}</span>' if c["meta"] else ""
    # winner button only appears for cells that are part of a comparison set:
    # pick this variant -> it becomes keep, the rest of the set -> discard.
    win = (
        '<button type="button" class="winbtn" title="Pick this variant as the set '
        'winner (this -> keep, others -> discard)">[*] winner</button>'
        if in_set
        else ""
    )
    return f"""
      <div class="cell" data-asset="{aid}" data-base="{esc(c.get('base',''))}">
        <div class="stage"><img loading="lazy" src="{esc(src)}" alt="{esc(c['label'])}"></div>
        <div class="cap"><span class="lbl">{esc(c['label'])}</span>{meta}</div>
        <div class="idline">{aid}</div>
        {win}
        <div class="verdict" role="group" aria-label="Verdict">
          <button type="button" class="vbtn" data-v="keep" title="Keep (K)">keep</button>
          <button type="button" class="vbtn" data-v="iterate" title="Iterate (I)">iterate</button>
          <button type="button" class="vbtn" data-v="discard" title="Discard (D)">discard</button>
        </div>
        <textarea class="note" rows="2" placeholder="note... (N)" aria-label="Note"></textarea>
        <input type="text" class="tags" placeholder="tags, comma, separated" aria-label="Tags">
      </div>"""


def _group_cells(cells):
    """Split a section's cells into runs of the same base_id, preserving order.
    A run with >1 cell is a comparison set (one base, several variants)."""
    groups = []
    for c in cells:
        b = c.get("base", "")
        if b and groups and groups[-1][0] == b:
            groups[-1][1].append(c)
        else:
            groups.append((b, [c]))
    return groups


def render_section(s):
    parts = []
    for base, members in _group_cells(s["cells"]):
        if len(members) > 1:
            inner = "".join(render_cell(c, in_set=True) for c in members)
            ids = ",".join(m["asset_id"] for m in members)
            parts.append(
                f'<div class="setframe" data-set-base="{esc(base)}" '
                f'data-set-ids="{esc(ids)}">'
                f'<div class="setbar"><span class="setlbl">SET // {esc(base)} '
                f"<b>{len(members)}</b> variants</span>"
                f'<span class="setspacer"></span>'
                f'<button type="button" class="setbtn" data-set="iterate" '
                f'title="Iterate the whole set">iterate set</button>'
                f'<button type="button" class="setbtn" data-set="discard" '
                f'title="Discard the whole set">discard set</button>'
                f'<span class="sethint">pick a winner below, or decide the set</span>'
                f"</div>"
                f'<div class="grid setgrid">{inner}</div></div>'
            )
        else:
            parts.append(render_cell(members[0]))
    body = "".join(parts)
    home = f'<p class="sechome">{esc(s.get("home", ""))}</p>' if s.get("home") else ""
    return f"""
    <section id="{esc(s['id'])}" class="sec" data-section="{esc(s['id'])}">
      <h2>{esc(s['title'])} <span class="seccount">{len(s['cells'])}</span> <span class="secprog"></span></h2>
      {home}
      <div class="grid">{body}</div>
    </section>"""


def render_nav(sections):
    out = []
    last_group = None
    for s in sections:
        if s["group"] != last_group:
            out.append(f'<span class="navtitle">{esc(s["group"])}</span>')
            last_group = s["group"]
        out.append(
            f'<a class="chip" data-navfor="{esc(s["id"])}" href="#{esc(s["id"])}">{esc(s["title"])}'
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
    --field:#120d09;--shadow:rgba(0,0,0,.45);--keep:#6fae86;--iterate:#e8a33d;--discard:#d8695a;
  }
  @media (prefers-color-scheme:light){:root{
    --ground:#efe6d6;--panel:#f7efe0;--panel-2:#fbf5e9;--ink:#2b2116;--ink-dim:#6b5b45;--ink-faint:#9a876c;
    --amber:#b9741a;--amber-deep:#8f5710;--win:#3f8a5c;--line:#ddccb0;--checker-a:#e6dac4;--checker-b:#ded1b8;
    --field:#fffaf0;--shadow:rgba(80,55,20,.18);--keep:#3f8a5c;--iterate:#b9741a;--discard:#c14a3a;}}
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
    backdrop-filter:blur(8px);border-bottom:1px solid var(--line);max-height:24vh;overflow-y:auto}
  .navtitle{font-family:ui-monospace,Consolas,monospace;font-size:.64rem;letter-spacing:.14em;text-transform:uppercase;
    color:var(--ink-faint);margin:0 .3rem 0 .5rem;flex-basis:100%}
  .navtitle:first-child{margin-top:0}
  .chip{font-family:ui-monospace,Consolas,monospace;font-size:.72rem;text-decoration:none;color:var(--ink-dim);
    border:1px solid var(--line);border-radius:20px;padding:.22rem .6rem;display:inline-flex;gap:.35rem;align-items:center;white-space:nowrap}
  .chip:hover{color:var(--ink);border-color:var(--ink-faint)}
  .chip b{color:var(--amber);font-weight:600}
  .chip.done{opacity:.35;text-decoration:line-through}
  .sechome{margin:-.5rem 0 1rem;font-size:.73rem;color:var(--ink-dim);font-family:ui-monospace,Consolas,monospace}
  .sechome::before{content:"-> shows up: ";color:var(--amber);font-size:.62rem;letter-spacing:.08em}
  .secprog{font-size:.66rem;color:var(--ink-faint);font-family:ui-monospace,Consolas,monospace;margin-left:auto;font-weight:400}
  /* set comparison frame -- one bordered block spanning the outer grid */
  .setframe{grid-column:1/-1;border:1px solid var(--amber-deep);border-radius:12px;
    padding:.6rem;background:color-mix(in srgb,var(--panel-2) 60%,transparent)}
  .setbar{display:flex;align-items:center;gap:.5rem;flex-wrap:wrap;margin:0 .1rem .55rem}
  .setlbl{font-family:ui-monospace,Consolas,monospace;font-size:.72rem;color:var(--amber);letter-spacing:.03em}
  .setlbl b{color:var(--ink)}
  .setspacer{flex:1}
  .sethint{font-family:ui-monospace,Consolas,monospace;font-size:.62rem;color:var(--ink-faint);flex-basis:100%;text-align:right}
  .setbtn{font-family:ui-monospace,Consolas,monospace;font-size:.66rem;text-transform:uppercase;letter-spacing:.03em;
    padding:.28rem .55rem;border-radius:6px;border:1px solid var(--line);background:var(--field);color:var(--ink-dim);cursor:pointer}
  .setbtn:hover{color:var(--ink);border-color:var(--ink-faint)}
  .setbtn[data-set="iterate"]:hover{border-color:var(--iterate);color:var(--iterate)}
  .setbtn[data-set="discard"]:hover{border-color:var(--discard);color:var(--discard)}
  .setgrid{grid-template-columns:repeat(auto-fill,minmax(190px,1fr))}
  .winbtn{font-family:ui-monospace,Consolas,monospace;font-size:.64rem;text-transform:uppercase;letter-spacing:.03em;
    padding:.28rem .1rem;border-radius:5px;border:1px dashed var(--amber-deep);background:transparent;color:var(--amber);cursor:pointer}
  .winbtn:hover{background:var(--amber);border-style:solid;color:#20140a}
  .cell.iswinner .winbtn{background:var(--keep);border-color:var(--keep);border-style:solid;color:#12251a}
  .sec{margin:2.2rem 0;scroll-margin-top:70px}
  .sec h2{font-family:ui-monospace,Consolas,monospace;font-size:1rem;letter-spacing:.02em;margin:0 0 .9rem;
    display:flex;align-items:center;gap:.7rem;padding-bottom:.4rem;border-bottom:1px solid var(--line)}
  .seccount{font-size:.72rem;color:var(--ink-faint);border:1px solid var(--line);border-radius:10px;padding:0 .5rem}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:.9rem}
  .cell{display:flex;flex-direction:column;gap:.4rem;background:var(--panel);border:1px solid var(--line);
    border-radius:12px;padding:.7rem;scroll-margin:80px}
  .cell.v-keep{border-color:var(--keep);box-shadow:0 0 0 1px var(--keep)}
  .cell.v-iterate{border-color:var(--iterate);box-shadow:0 0 0 1px var(--iterate)}
  .cell.v-discard{border-color:var(--discard);box-shadow:0 0 0 1px var(--discard)}
  .cell.focused{outline:2px solid var(--amber);outline-offset:2px}
  /* decided (keep/discard) cells are physically MOVED into #archive; a section or
     set frame left with no live cells collapses out of the live flow */
  .sec.empty{display:none}
  .setframe.empty{display:none}
  .stage img{cursor:zoom-in}
  /* decisions archive panel */
  #archive{margin:2.5rem 0;border:1px solid var(--line);border-radius:12px;background:var(--panel)}
  #archive>summary{cursor:pointer;list-style:none;padding:.85rem 1.1rem;font-family:ui-monospace,Consolas,monospace;
    font-size:.85rem;color:var(--ink-dim);display:flex;align-items:center;gap:.6rem}
  #archive>summary::-webkit-details-marker{display:none}
  #archive>summary::before{content:"[+]";color:var(--amber)}
  #archive[open]>summary::before{content:"[-]"}
  #archive>summary b{color:var(--ink)}
  #archive .archwrap{padding:0 1.1rem 1.1rem}
  #archive .archnote{font-family:ui-monospace,Consolas,monospace;font-size:.68rem;color:var(--ink-faint);margin:0 0 .8rem}
  #archive .grid{margin-top:.4rem}
  /* image lightbox */
  #lightbox{position:fixed;inset:0;z-index:80;display:none;place-items:center;padding:3vmin;
    background:rgba(0,0,0,.82);backdrop-filter:blur(3px);cursor:zoom-out}
  #lightbox.open{display:grid}
  #lightbox img{image-rendering:pixelated;max-width:94vw;max-height:88vh;width:auto;height:auto;
    border:1px solid var(--line);border-radius:8px;box-shadow:0 8px 40px rgba(0,0,0,.6);background:var(--checker-a)}
  #lightbox .lbcap{position:fixed;bottom:2vmin;left:0;right:0;text-align:center;color:var(--ink-dim);
    font-family:ui-monospace,Consolas,monospace;font-size:.78rem;pointer-events:none}
  #lightbox .lbclose{position:fixed;top:2vmin;right:2.4vmin;color:var(--ink);font-family:ui-monospace,Consolas,monospace;
    font-size:.9rem;border:1px solid var(--line);border-radius:6px;padding:.3rem .6rem;background:var(--panel)}
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
  .vbtn.on[data-v="iterate"]{background:var(--iterate);border-color:var(--iterate);color:#2a1e08}
  .vbtn.on[data-v="discard"]{background:var(--discard);border-color:var(--discard);color:#2a1210}
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
  .tally .k{color:var(--keep)}.tally .m{color:var(--iterate)}.tally .r{color:var(--discard)}
  .save{font-family:ui-monospace,Consolas,monospace;font-size:.72rem;color:var(--ink-faint)}
  .save.ok{color:var(--keep)}.save.err{color:var(--discard)}
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
  <span><b>K</b> keep &middot; <b>I</b> iterate &middot; <b>D</b> discard</span>
  <span><kbd>N</kbd> note &middot; <kbd>Esc</kbd> back</span>
</div>
<div class="wrap">
  <p class="eyebrow">P(Doom)1 &middot; art direction &middot; local review app</p>
  <h1>Art review -- all tracks, one place</h1>
  <p class="lede">{{SUBTITLE}}</p>
  <nav class="nav">{{NAV}}</nav>
  {{BODY}}
  <details id="archive">
    <summary>Decisions archive <b class="archcount">0</b> decided <span class="archbreak"></span></summary>
    <div class="archwrap">
      <p class="archnote">Kept + discarded assets live here, out of the live queue. Change a verdict back to
      iterate (or clear it) to send an item back up to the live flow.</p>
      <div class="grid" id="archivegrid"></div>
    </div>
  </details>
  <div class="bar">
    <div class="tally" id="tally"></div>
    <div class="save" id="save">state file: tools/art_review/review_state.json</div>
    <div class="spacer"></div>
    <button type="button" class="btn ghost" id="archivebtn">Decisions archive (<b>0</b>)</button>
    <button type="button" class="btn ghost" id="exportbtn">View state JSON</button>
  </div>
  <footer>Every verdict / note / tag POSTs to the local server and is written to
  <b>review_state.json</b> on disk -- reload any time, across sessions, and your review is still here.</footer>
</div>
<div id="lightbox" aria-hidden="true">
  <span class="lbclose">[ESC] close</span>
  <img alt="">
  <div class="lbcap"></div>
</div>
<dialog id="exportdlg">
  <div class="modal-head"><h3>// review_state.json</h3><button type="button" class="btn ghost" id="copybtn">copy</button></div>
  <div class="modal-body"><textarea id="exporttext" readonly></textarea></div>
</dialog>
<script>
(function(){
  "use strict";
  var SEED={{SEED}};
  var VERDICTS=['keep','iterate','discard'];
  var CELLS=[].slice.call(document.querySelectorAll('.cell'));
  var cellById={};CELLS.forEach(function(c){cellById[c.getAttribute('data-asset')]=c;});
  var archGrid=document.getElementById('archivegrid');
  var timers={},focusCell=null;

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

  // -- verdict state on a cell --
  function applyVerdict(cell,v){
    cell.classList.remove('v-keep','v-iterate','v-discard');
    if(v)cell.classList.add('v-'+v);
    if(v!=='keep')cell.classList.remove('iswinner');
    cell.classList.toggle('decided',v==='keep'||v==='discard');
    cell.querySelectorAll('.vbtn').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-v')===v);});
  }
  function curVerdict(cell){
    if(cell.classList.contains('v-keep'))return 'keep';
    if(cell.classList.contains('v-iterate'))return 'iterate';
    if(cell.classList.contains('v-discard'))return 'discard';
    return null;
  }
  function isDecided(cell){var v=curVerdict(cell);return v==='keep'||v==='discard';}
  function getNote(cell){var n=cell.querySelector('.note');return n?n.value.trim():'';}
  function setNoteField(cell,val){var n=cell.querySelector('.note');if(n)n.value=val;}

  // commit a verdict (and optionally a note) to a cell + server, then re-place it
  function commitVerdict(cell,v,note){
    var id=cell.getAttribute('data-asset');
    applyVerdict(cell,v);
    var patch={verdict:v};
    if(note!=null){setNoteField(cell,note);patch.note=note;}
    persist(id,patch);
    placeCell(cell);
    refreshLayout();
  }
  // interactive verdict from a button/key: toggles off, prompts a discard note
  function setVerdict(cell,v){
    if(curVerdict(cell)===v)v=null;               // toggle off -> undecided
    if(v==='discard'&&!getNote(cell)){
      var r=window.prompt('Discard note -- why is this OFF-brief / wrong direction?\n(a discard says the BRIEF needs a rethink, not a re-roll. Blank = skip.)','');
      if(r===null)return;                         // cancelled -> leave as-is
      commitVerdict(cell,'discard',r.trim());
      advanceFrom(cell);return;
    }
    commitVerdict(cell,v,null);
    if(isDecided(cell))advanceFrom(cell);
  }
  function parseTags(str){return (str||'').split(',').map(function(t){return t.trim();}).filter(Boolean);}

  // -- archive placement: decided cells physically move into #archivegrid; an
  // anchor comment marks each cell's live home so it restores in place --
  function placeCell(cell){
    var dec=isDecided(cell),inArch=cell.parentNode===archGrid;
    if(dec&&!inArch){archGrid.appendChild(cell);}
    else if(!dec&&inArch){cell._anchor.parentNode.insertBefore(cell,cell._anchor);}
  }

  // -- lightbox --
  var lb=document.getElementById('lightbox'),lbImg=lb.querySelector('img'),lbCap=lb.querySelector('.lbcap');
  function openLightbox(src,cap){lbImg.src=src;lbCap.textContent=cap||'';lb.classList.add('open');lb.setAttribute('aria-hidden','false');}
  function closeLightbox(){lb.classList.remove('open');lb.setAttribute('aria-hidden','true');lbImg.removeAttribute('src');}
  lb.addEventListener('click',closeLightbox);

  // hydrate every cell + wire it up
  CELLS.forEach(function(cell){
    var id=cell.getAttribute('data-asset'), s=SEED[id]||{};
    // anchor marks the live slot so a de-archived cell returns to its exact place
    var anchor=document.createComment('a:'+id);
    cell.parentNode.insertBefore(anchor,cell.nextSibling);
    cell._anchor=anchor;
    applyVerdict(cell,s.verdict||null);
    var note=cell.querySelector('.note'); if(note)note.value=s.note||'';
    var tags=cell.querySelector('.tags'); if(tags)tags.value=(s.tags||[]).join(', ');
    cell.querySelectorAll('.vbtn').forEach(function(btn){
      btn.addEventListener('click',function(){focusOn(cell,false);setVerdict(cell,btn.getAttribute('data-v'));});
    });
    var win=cell.querySelector('.winbtn');
    if(win)win.addEventListener('click',function(){focusOn(cell,false);pickWinner(cell);});
    var img=cell.querySelector('.stage img');
    if(img)img.addEventListener('click',function(){openLightbox(img.src,cell.getAttribute('data-asset'));});
    if(note)note.addEventListener('input',function(e){debounce(id,{note:e.target.value});});
    if(tags)tags.addEventListener('input',function(e){debounce(id,{tags:parseTags(e.target.value)});});
    cell.addEventListener('mousedown',function(){focusOn(cell,false);});
  });

  // -- comparison sets (server-marked) for one-decision handling --
  var SETS=[];
  [].slice.call(document.querySelectorAll('.setframe')).forEach(function(frame){
    var ids=(frame.getAttribute('data-set-ids')||'').split(',').filter(Boolean);
    var cells=ids.map(function(i){return cellById[i];}).filter(Boolean);
    if(!cells.length)return;
    var set={base:frame.getAttribute('data-set-base'),cells:cells,frame:frame};
    cells.forEach(function(c){c._set=set;});
    SETS.push(set);
    frame.querySelectorAll('.setbtn').forEach(function(btn){
      btn.addEventListener('click',function(){setDecision(set,btn.getAttribute('data-set'));});
    });
  });
  function pickWinner(cell){
    var set=cell._set; if(!set)return;
    cell.classList.add('iswinner');
    set.cells.forEach(function(c){
      if(c===cell){commitVerdict(c,'keep',null);}
      else{c.classList.remove('iswinner');
        var note=getNote(c)||('not chosen -- set winner: '+set.base);
        commitVerdict(c,'discard',note);}
    });
  }
  function setDecision(set,kind){
    if(kind==='iterate'){set.cells.forEach(function(c){c.classList.remove('iswinner');commitVerdict(c,'iterate',null);});return;}
    if(kind==='discard'){
      var r=window.prompt('Discard the WHOLE set -- why is this direction OFF-brief?\n(blank = skip; applied to variants without their own note)','');
      if(r===null)return; var msg=r.trim();
      set.cells.forEach(function(c){c.classList.remove('iswinner');
        var note=getNote(c)||msg; commitVerdict(c,'discard',note);});
    }
  }

  // -- focus + keyboard nav over the LIVE queue (archived cells excluded) --
  function liveCells(){return CELLS.filter(function(c){return c.parentNode!==archGrid;});}
  function focusOn(cell,scroll){
    if(focusCell&&focusCell!==cell)focusCell.classList.remove('focused');
    focusCell=cell;
    if(cell){cell.classList.add('focused');if(scroll)cell.scrollIntoView({block:'nearest',inline:'nearest'});}
  }
  function move(d){
    var list=liveCells(); if(!list.length)return;
    var i=focusCell?list.indexOf(focusCell):-1;
    if(i<0){i=d>0?0:list.length-1;}else{i+=d;}
    if(i<0)i=0; if(i>=list.length)i=list.length-1;
    focusOn(list[i],true);
  }
  function advanceFrom(cell){ // after a decide archives `cell`, land focus on the next live one
    var list=liveCells();
    if(!list.length){focusCell=null;return;}
    focusOn(list[0],true);
  }
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'&&lb.classList.contains('open')){closeLightbox();e.preventDefault();return;}
    var t=e.target,tag=(t.tagName||'').toLowerCase();
    if(tag==='input'||tag==='textarea'||t.isContentEditable){if(e.key==='Escape')t.blur();return;}
    if(e.ctrlKey||e.metaKey||e.altKey)return;
    var k=e.key;
    if(k==='ArrowRight'||k==='ArrowDown'){move(1);e.preventDefault();}
    else if(k==='ArrowLeft'||k==='ArrowUp'){move(-1);e.preventDefault();}
    else if(k==='k'||k==='K'){if(focusCell){setVerdict(focusCell,'keep');e.preventDefault();}}
    else if(k==='i'||k==='I'){if(focusCell){setVerdict(focusCell,'iterate');e.preventDefault();}}
    else if(k==='d'||k==='D'){if(focusCell){setVerdict(focusCell,'discard');e.preventDefault();}}
    else if(k==='n'||k==='N'||k==='Enter'){if(!focusCell)move(1);if(focusCell){var n=focusCell.querySelector('.note');if(n)n.focus();}e.preventDefault();}
    else if(k==='Escape'){if(focusCell){focusCell.classList.remove('focused');focusCell=null;}}
  });

  function tally(){
    var k=0,m=0,r=0,notes=0;
    for(var id in SEED){var s=SEED[id]||{};if(s.verdict==='keep')k++;else if(s.verdict==='iterate')m++;else if(s.verdict==='discard')r++;
      if(s.note&&s.note.trim())notes++;}
    document.getElementById('tally').innerHTML='<span class="k">keep '+k+'</span> &middot; '+
      '<span class="m">iterate '+m+'</span> &middot; <span class="r">discard '+r+'</span> &middot; '+
      '<b>'+notes+'</b> notes';
  }

  // capture each section's ORIGINAL cell list up front (before archive moves it)
  var SECS=[].slice.call(document.querySelectorAll('.sec')).map(function(sec){
    return {el:sec,id:sec.getAttribute('data-section'),cells:[].slice.call(sec.querySelectorAll('.cell'))};
  });
  function refreshLayout(){
    // hide set frames + sections that have no live cells left
    [].slice.call(document.querySelectorAll('.setframe')).forEach(function(f){
      f.classList.toggle('empty',!f.querySelector('.grid > .cell'));
    });
    SECS.forEach(function(sec){
      var n=sec.cells.length,dec=0;
      sec.cells.forEach(function(c){if(isDecided(c))dec++;});
      var live=n-dec;
      sec.el.classList.toggle('empty',live===0);
      var prog=sec.el.querySelector('.secprog');if(prog)prog.textContent=dec+' / '+n+' decided';
      var chip=document.querySelector('.chip[data-navfor="'+sec.id+'"]');
      if(chip)chip.classList.toggle('done',live===0&&n>0);
    });
    var decided=archGrid.querySelectorAll('.cell').length;
    var ac=document.querySelector('#archive .archcount');if(ac)ac.textContent=decided;
    var ab=document.querySelector('#archivebtn b');if(ab)ab.textContent=decided;
  }

  // move already-decided cells into the archive on first paint
  CELLS.forEach(placeCell);
  tally();
  refreshLayout();

  document.getElementById('archivebtn').addEventListener('click',function(){
    var d=document.getElementById('archive');d.open=!d.open;
    if(d.open)d.scrollIntoView({block:'start'});
  });

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
