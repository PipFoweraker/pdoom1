#!/usr/bin/env python3
"""build_full_gallery.py -- ONE stateful gallery over ALL art on disk, in three
task-shaped modes: TRIAGE, STUDY, COMPARE.

Layer: OBSERVE
Invoked by: human

Why a sibling and not an extension of build_morning_index.py: the morning index
is a hand-curated map of eight named batches and is deliberately verdict-free
("the map, not the workbench"). This tool is the opposite: it WALKS THE DISK so
nothing can be invisible (the 3-percent-coverage failure), and it captures
verdicts. Different generator, different lifecycle; both stay.

THREE MODES, SPLIT BY TASK NOT BY LAYOUT (2026-08-07)
-----------------------------------------------------
The first version of this page was built for one job: narrow 600 images fast.
It did that job well -- 136 decisions in 10.4 minutes, 1.7s median gap. Then Pip
opened it on the 652-image art_night_2026-08-07 run and the job changed: "These
are so gorgeous I want to be able to enjoy the fine detail and start giving
specific comments." Studying is not triaging. A dense keyboard-first grid is the
wrong surface for saying something specific about one picture, and a big single
picture is the wrong surface for narrowing 600.

So the modes are split by what the reviewer is DOING, and each keeps the
affordances that job needs:

  TRIAGE  (default, key 1) -- the original dense grid. One keystroke per
      decision, reviewed items can leave the working set, batch sweeps. This is
      how 600 becomes 60. Deliberately unchanged.
  STUDY   (key 2) -- one image large, left/right steps through the working set
      ("a gallery-rotate rather than scroll"), zoom/pan on the same magnifier
      surface the slot picker uses, a MULTI-LINE note box always on screen, and
      the generation record (direction, palette, subject, model) beside the
      picture so a note can name what it is reacting to.
  COMPARE (key 3) -- one facet group tiled at judging size. The l1_family block
      is 12 style DIRECTIONS x 22 subjects: it was generated so a direction can
      be accepted or rejected as a direction. Adjudicating that one image at a
      time throws away the reason it was generated that way.

Rejected: a fourth "lightbox-only" mode, and a separate study PAGE. The
magnifier is a control, not a task -- it belongs inside triage and study rather
than being a mode of its own; and a second page would fork the verdict store,
which is the failure this repo has already paid for twice.

THE MAGNIFIER IS PORTED, NOT REINVENTED
---------------------------------------
The zoom/pan surface here is the one from build_slot_picker.py (fit/100/200/400,
wheel to zoom, drag to pan, keyboard ownership while open so number keys do not
leak to the grid underneath). That component shipped 2026-08-06, was used in
anger, and was called "the funnest art picking". Growing a second magnifier here
would guarantee the two drift.

FACETS COME FROM THE .meta.json SIDECARS
----------------------------------------
art_night_2026-08-07 writes a sidecar per image carrying block, cell, model,
quality, cost and the full prompt. The named style direction lives inside the
prompt ("COHERENT DIRECTION -- MUNICIPAL RECORD:"), as do the RENDERING, PALETTE
and SUBJECT clauses. Those are parsed out and interned into a small string table
so the page can group by DIRECTION rather than by the opaque cell code `f07`.
Full prompts are NOT embedded -- they are ~5 KB each and would add ~13 MB to the
page for text nobody reads in a grid. The sidecar path is embedded instead, and
the record panel shows the parsed clauses.

Coverage: every image file (png/jpg/jpeg/webp) under art_generated/ and
art_source/, grouped into batches by top-level directory, newest batch first.
Read-only on assets -- this script writes exactly one file, the HTML output.
review_state.json is read, never written.

Statefulness (the honest file:// story):
  - The page keeps verdicts/notes in browser localStorage, so they survive
    closing the tab.
  - Baseline verdicts from tools/art_review/review_state.json are baked into
    the page at build time, so already-judged assets show their verdict.
  - "E" in the page downloads a JSON export; merge it back with
        python tools/art_review/merge_gallery_export.py <downloaded.json>
    which folds it into review_state.json (the single verdict store that
    apply_review.py consumes). No second verdict store is invented, and NOTES
    ride the same path -- review_state.json is tracked in git, so a note is
    diffable the moment it is merged, and
        python tools/art_review/notes_brief.py
    renders them into docs/art/NOTES_BRIEF.md, the brief the next generation
    round reads.

asset_id compatibility with apply_review.py / review_state.json:
  gen:<category>:<base_id>:<variant>  for art_generated/<category>/v1 files
      matching <base>_<vN>_<size>.png or <base>_<size>.png (implicit v1).
  px:<relpath>                        for art_source files. Existing state uses
      extension-less relpaths; where a state key already exists it is reused
      verbatim (no duplicate keys). New px assets get the relpath WITH
      extension, which apply_review.py can actually resolve.
  file:<relpath-from-repo-root>       ADDITIVE extension, only for files no
      existing scheme can express (e.g. webp scene art, off-grid size stems,
      loose files outside a v1/ dir). apply_review.py resolves these since
      2026-08-04: single file, category derived from the path, destination
      filename kept verbatim.

Usage:
    python tools/art_review/build_full_gallery.py [--open] [--art-root DIR]
Output:
    <art-root>/art_generated/full_gallery.html   (gitignored; open via file://)
"""

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import webbrowser
from pathlib import Path

# Sibling module (this script runs from tools/art_review/, which is
# sys.path[0] when invoked as a script). Supplies dest_rule_for_id -- the ONE
# mapping-coverage predicate shared with the report gate and the tests.
import apply_review

REPO = Path(__file__).resolve().parents[2]
# ART_GEN / ART_SRC / OUT are rebound by main() when --art-root is given. Agents
# work in git worktrees, and art_generated/ is gitignored, so a worktree sees
# ~500 legacy tracked PNGs and none of tonight's 652 -- the file-locality trap
# this repo has already lost a day to. --art-root points the walk at the one
# checkout that actually holds the art. STATE stays with the CODE, because the
# verdict store is tracked and belongs to the branch you are on.
ART_GEN = REPO / "art_generated"
ART_SRC = REPO / "art_source"
STATE = REPO / "tools" / "art_review" / "review_state.json"
OUT = ART_GEN / "full_gallery.html"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
KNOWN_SIZES = {64, 128, 256, 512, 768, 1024, 1536, 2048}
# preferred display size, best first (roughly "big enough to judge, small
# enough to load 9k of")
THUMB_PREF = [512, 768, 1024, 256, 1536, 128, 2048, 64]
GEN_STEM = re.compile(r"^(?P<base>.+?)(?:_(?P<var>v\d+))?_(?P<size>\d+)$")
VERDICT_MIGRATE = {"maybe": "remix", "reroll": "remix", "iterate": "remix"}
VERDICTS = ("keep", "remix", "shelf", "discard")


def load_state():
    if not STATE.is_file():
        return {}
    try:
        raw = json.loads(STATE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return raw if isinstance(raw, dict) else {}


def migrate(v):
    v = (v or "").strip().lower()
    if v in VERDICTS:
        return v
    return VERDICT_MIGRATE.get(v, "")


# Directories that hold IMAGES but are not ART CANDIDATES. audiodump/ holds OBS
# playtest recordings and the frames extracted from them for timestamp analysis --
# 535 files across 5 frames_* dirs. Pip hit them in the 2026-08-04 review pass:
# "For some reason all these frames from my video grab of our audio review came in
# ... We do not want those showing up." A review tool that shows non-reviewable
# items spends the reviewer's attention on nothing, which is the scarcest thing
# in this loop.
SKIP_DIR_NAMES = {"audiodump", "logs", "velocity", "ceremony_2026-07-31"}
SKIP_DIR_PREFIXES = ("frames_",)


def _is_skipped(rel_parts):
    for seg in rel_parts:
        if seg in SKIP_DIR_NAMES or seg.startswith(SKIP_DIR_PREFIXES):
            return True
    return False


def iter_images(root):
    if not root.is_dir():
        return
    for p in sorted(root.rglob("*")):
        if not (p.is_file() and p.suffix.lower() in IMAGE_EXTS):
            continue
        if _is_skipped(p.relative_to(root).parts[:-1]):
            continue
        yield p


# --------------------------------------------------------------------------
# Facets -- parsed from the .meta.json sidecars written by the art_night runner
# --------------------------------------------------------------------------
# Grouping by `f07` tells the reviewer nothing. Grouping by "MUNICIPAL RECORD"
# tells them exactly what they are accepting or rejecting. The named direction
# is not a JSON field -- it is a clause inside the prompt -- so it is parsed
# here rather than being invented as a hand-maintained side-map of cell -> name
# (that map would rot the first time a block is regenerated).
DIRECTION_RE = re.compile(r"COHERENT DIRECTION\s*--\s*([A-Z][A-Z0-9 '/&-]{2,40}?)\s*:")
CLAUSE_RE = {
    "rendering": re.compile(r"(?:^|,\s)RENDERING:\s*(.+?)(?=,\s(?:PALETTE|SUBJECT|COHERENT)\b|$)"),
    "palette": re.compile(r"(?:^|,\s)PALETTE:\s*(.+?)(?=,\s(?:RENDERING|SUBJECT|COHERENT)\b|$)"),
    "subject": re.compile(r"(?:^|,\s)SUBJECT:\s*(.+?)$"),
}


def _short(text, words=9, chars=64):
    """First clause of a long prompt segment, trimmed to a chip-sized label."""
    text = re.sub(r"\s+", " ", (text or "")).strip()
    # the first comma/semicolon usually ends the naming part of the clause
    head = re.split(r"[;,]", text)[0].strip()
    if not head:
        return ""
    parts = head.split(" ")
    if len(parts) > words:
        head = " ".join(parts[:words])
    if len(head) > chars:
        head = head[: chars - 3].rstrip() + "..."
    return head


def facets_from_meta(meta):
    """Return {facet_name: label} for one sidecar dict. Empty labels dropped."""
    out = {}
    prompt = meta.get("prompt") or ""
    if prompt:
        m = DIRECTION_RE.search(prompt)
        if m:
            out["direction"] = m.group(1).strip().title()
        for name, rx in CLAUSE_RE.items():
            cm = rx.search(prompt)
            if cm:
                lbl = _short(cm.group(1))
                if lbl:
                    out[name] = lbl
        # when no NAMED direction exists (the palette/grid blocks), the rendering
        # clause IS the direction the reviewer is judging
        if "direction" not in out and out.get("rendering"):
            out["direction"] = out["rendering"]
    q = meta.get("quality")
    if q:
        out["quality"] = str(q)
    mdl = meta.get("model")
    if mdl:
        out["model"] = str(mdl)
    return {k: v for k, v in out.items() if v}


def read_meta_for(paths, cache):
    """Find and parse the sidecar for an asset group. One read per cell.

    Sidecars are per-FILE (s01_f01_v1_1536.meta.json) but every size of one cell
    carries the same prompt, so the parse is cached on the sidecar path.
    """
    for p in paths:
        side = p.with_name(p.stem + ".meta.json")
        if not side.is_file():
            continue
        key = str(side)
        if key in cache:
            return cache[key]
        try:
            meta = json.loads(side.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            cache[key] = ({}, "")
            return cache[key]
        try:
            rel = side.relative_to(REPO).as_posix()
        except ValueError:
            rel = side.name
        rec = (facets_from_meta(meta), rel)
        cache[key] = rec
        return rec
    return ({}, "")


class AssetGroup:
    __slots__ = ("id", "name", "files", "thumb", "full", "facets", "meta_rel")

    def __init__(self, asset_id, name):
        self.id = asset_id
        self.name = name
        self.files = []  # (path, size_or_None)
        self.thumb = None
        self.full = None
        self.facets = {}
        self.meta_rel = ""


def scan(state):
    """Return list of batches: {title, mtime, assets:[AssetGroup]}."""
    batches = []

    def batch_for(files, title):
        if not files:
            return None
        mtime = max(p.stat().st_mtime for p, _ in files)
        return {"title": title, "mtime": mtime, "files": files}

    # ---- art_generated: batch per top-level dir ----
    gen_top = {}
    for p in iter_images(ART_GEN):
        rel = p.relative_to(ART_GEN)
        top = rel.parts[0] if len(rel.parts) > 1 else "(root)"
        gen_top.setdefault(top, []).append((p, "gen"))
    for top, files in gen_top.items():
        b = batch_for(files, f"art_generated/{top}")
        if b:
            batches.append(b)

    # ---- art_source: batch per top-level dir ----
    src_top = {}
    for p in iter_images(ART_SRC):
        rel = p.relative_to(ART_SRC)
        top = rel.parts[0] if len(rel.parts) > 1 else "(root)"
        src_top.setdefault(top, []).append((p, "px"))
    for top, files in src_top.items():
        b = batch_for(files, f"art_source/{top}")
        if b:
            batches.append(b)

    batches.sort(key=lambda b: b["mtime"], reverse=True)

    # ---- group each batch's files into assets with canonical ids ----
    meta_cache = {}
    for b in batches:
        groups = {}
        order = []
        for p, kind in b["files"]:
            asset_id, name, size = classify(p, kind, state)
            if asset_id not in groups:
                groups[asset_id] = AssetGroup(asset_id, name)
                order.append(asset_id)
            groups[asset_id].files.append((p, size))
        assets = []
        for aid in order:
            g = groups[aid]
            sized = [(p, s) for p, s in g.files if s is not None]
            if sized:
                by_pref = {s: p for p, s in sized}
                g.thumb = next((by_pref[s] for s in THUMB_PREF if s in by_pref), sized[0][0])
                g.full = max(sized, key=lambda t: t[1])[0]
            else:
                g.thumb = g.files[0][0]
                g.full = g.files[-1][0]
            g.facets, g.meta_rel = read_meta_for([p for p, _ in g.files], meta_cache)
            assets.append(g)
        b["assets"] = assets
        del b["files"]
    return batches


def classify(p, kind, state):
    """Return (canonical asset_id, display name, size_or_None) for one file."""
    if kind == "gen":
        rel = p.relative_to(ART_GEN)
        # canonical gen id only for <category>/v1/<file>.png with a size stem
        if len(rel.parts) == 3 and rel.parts[1] == "v1" and p.suffix.lower() == ".png":
            m = GEN_STEM.match(p.stem)
            if m and int(m.group("size")) in KNOWN_SIZES:
                cat = rel.parts[0]
                base = m.group("base")
                var = m.group("var") or "v1"
                return (
                    f"gen:{cat}:{base}:{var}",
                    f"{base} {var}" if m.group("var") else base,
                    int(m.group("size")),
                )
        return (f"file:art_generated/{rel.as_posix()}", p.name, None)

    # px: reuse the existing state key spelling if one exists (600 legacy keys
    # are extension-less); otherwise use the resolvable with-extension form.
    rel = p.relative_to(ART_SRC).as_posix()
    sans = rel[: -len(p.suffix)]
    for candidate in (f"px:{sans}", f"px:{rel}"):
        if candidate in state:
            return (candidate, p.name, None)
    return (f"px:{rel}", p.name, None)


# Facet order is the order the filter bar shows them, coarsest first.
FACET_ORDER = ["direction", "palette", "subject", "rendering", "quality", "model"]


class Interner:
    """String table so 6000 cards carry a few small ints, not long strings."""

    def __init__(self):
        self.strings = []
        self._idx = {}

    def __call__(self, s):
        if s not in self._idx:
            self._idx[s] = len(self.strings)
            self.strings.append(s)
        return self._idx[s]


def build_page(batches, state):
    baseline = {}
    sections = []
    batch_index = []
    total_assets = 0
    total_files = 0
    matched = 0
    intern = Interner()
    facet_values = {f: {} for f in FACET_ORDER}  # facet -> {label_index: count}
    card_meta = {}  # asset_id -> small record shown in the STUDY side panel

    for bi, b in enumerate(batches):
        cards = []
        for g in b["assets"]:
            total_assets += 1
            total_files += len(g.files)
            entry = state.get(g.id)
            if entry and isinstance(entry, dict):
                v = migrate(entry.get("verdict"))
                n = entry.get("note") or ""
                if v or n:
                    baseline[g.id] = {"v": v, "n": n}
                    if v:
                        matched += 1
            thumb_href = href_of(g.thumb)
            full_href = href_of(g.full)
            fdata = {}
            for f in FACET_ORDER:
                lbl = g.facets.get(f)
                if not lbl:
                    continue
                li = intern(lbl)
                fdata[f] = li
                facet_values[f][li] = facet_values[f].get(li, 0) + 1
            card_meta[g.id] = {
                "batch": b["title"],
                "meta": g.meta_rel,
                "n": len(g.files),
            }
            nfiles = f'<span class="nf">x{len(g.files)}</span>' if len(g.files) > 1 else ""
            fattr = "".join(f' data-f-{f}="{fdata[f]}"' for f in FACET_ORDER if f in fdata)
            chip = ""
            if "direction" in g.facets:
                chip = f'<span class="chip">{html.escape(g.facets["direction"])}</span>'
            cards.append(
                f'<div class="card" data-id="{html.escape(g.id, quote=True)}" '
                f'data-b="{bi}"{fattr}>'
                f'<a href="{full_href}" target="_blank" tabindex="-1">'
                f'<img loading="lazy" decoding="async" src="{thumb_href}" '
                f'alt="{html.escape(g.name, quote=True)}"></a>'
                f'<div class="meta"><span class="nm" title="{html.escape(g.id, quote=True)}">'
                f"{html.escape(g.name)}</span>{nfiles}</div>"
                f"{chip}"
                f'<div class="vrow"><span class="badge"></span><span class="notetxt"></span></div>'
                f"</div>"
            )
        day = time.strftime("%Y-%m-%d", time.localtime(b["mtime"]))
        sections.append(
            f'<section class="batch" id="b{bi}" data-b="{bi}">'
            f'<h2>{html.escape(b["title"])}'
            f'<span class="bstat" id="bs{bi}"></span>'
            f'<span class="bdate">{day}</span></h2>'
            f'<div class="grid">{"".join(cards)}</div></section>'
        )
        batch_index.append(
            f'<a href="#b{bi}" data-b="{bi}">{html.escape(b["title"])} '
            f'<span class="bs" id="bi{bi}">{len(b["assets"])}</span></a>'
        )

    # filter bar: only offer a facet that actually discriminates (>1 value)
    facet_opts = {}
    for f in FACET_ORDER:
        vals = facet_values[f]
        if len(vals) < 2:
            continue
        facet_opts[f] = sorted(
            ([li, intern.strings[li], n] for li, n in vals.items()),
            key=lambda t: (-t[2], t[1]),
        )

    page = TEMPLATE
    page = page.replace("__SECTIONS__", "\n".join(sections))
    page = page.replace("__BATCHINDEX__", "\n".join(batch_index))
    page = page.replace("__BASELINE__", json.dumps(baseline, ensure_ascii=True))
    page = page.replace("__STRINGS__", json.dumps(intern.strings, ensure_ascii=True))
    page = page.replace("__FACETOPTS__", json.dumps(facet_opts, ensure_ascii=True))
    page = page.replace("__FACETORDER__", json.dumps(FACET_ORDER, ensure_ascii=True))
    page = page.replace("__CARDMETA__", json.dumps(card_meta, ensure_ascii=True))
    page = page.replace("__NBATCH__", str(len(batches)))
    page = page.replace("__BUILT__", time.strftime("%Y-%m-%d %H:%M"))
    return page, total_assets, total_files, matched


def href_of(p):
    """Path relative to the output file (which lives in art_generated/)."""
    try:
        rel = p.relative_to(ART_GEN)
        return html.escape(rel.as_posix(), quote=True)
    except ValueError:
        rel = p.relative_to(ART_SRC)
        return html.escape("../art_source/" + rel.as_posix(), quote=True)


def preflight_mapping(batches):
    """Batches whose asset ids cannot map to a destination or explicit Hold.

    Returns {batch_title: [unmappable asset ids]}. This is the pre-review
    gate for the #1093/#1107 recurrence (2026-08-04): a batch indexed without
    a mapping lets a whole review pass strand its own keeps -- the verdicts
    land, then apply_review's promotion gate fails AFTER the reviewing was
    spent. Failing HERE means the one-line map entry (destination or
    Hold(reason)) exists BEFORE any verdict is cast."""
    unmapped = {}
    for b in batches:
        bad = [g.id for g in b["assets"] if apply_review.dest_rule_for_id(g.id) is None]
        if bad:
            unmapped[b["title"]] = bad
    return unmapped


# --------------------------------------------------------------------------
# The JS syntax gate -- the reason this whole rebuild happened
# --------------------------------------------------------------------------
# 2026-08-04..08-07: this page shipped with an UNTERMINATED STRING LITERAL. A
# `\n\n` written into the non-raw TEMPLATE was compiled by Python into two real
# newlines INSIDE a JavaScript string, so the browser threw "Invalid or
# unexpected token" at parse time and the ENTIRE <script> block never ran. Every
# key was dead, no badge was painted, no card was selectable. Nothing in the
# build said a word: the file was 4 MB, every <img> resolved, every section was
# present. This is exactly the repo's silent-wrongness pattern -- the artefact
# LOOKED right, and only the behaviour was gone.
#
# Two fixes, because the second one is the only one that survives the next edit:
#   1. TEMPLATE is now a RAW string, so a JS `\n` stays a JS `\n`.
#   2. The build PARSES the emitted script before writing the file. `node
#      --check` when node exists; a narrower raw-newline-in-string-literal
#      scanner when it does not. A build that cannot prove its own script
#      parses fails loudly rather than writing a page whose keyboard is dead.
SCRIPT_RE = re.compile(r"<script>(.*?)</script>", re.S)


def extract_script(page):
    m = SCRIPT_RE.search(page)
    return m.group(1) if m else ""


# A `/` starts a REGEX literal only where a value is expected. The standard
# cheap heuristic: look at the previous significant character. After a name, a
# number, `)` or `]` a slash is division; after an operator, `(`, `,`, `=`, `:`
# or a statement start it opens a regex.
_REGEX_OK_AFTER = set("(,=:[!&|?{};+-*%~^<>")


def fallback_js_scan(js):
    """Detect a raw newline inside a single- or double-quoted JS string.

    Deliberately narrow: it looks for the ONE defect class that killed this page
    rather than pretending to be a parser. Template literals (backticks) legally
    span lines and are skipped; this codebase does not use them.

    It MUST also understand comments and regex literals, because both can hold a
    lone quote character. The first version of this scanner did not, and flagged
    the perfectly good line

        .replace(/>/g, "&gt;").replace(/"/g, "&quot;");

    as an unterminated string -- a gate that blocks every build is worse than
    the bug it was added to catch. See _scanner_self_test.
    """
    problems = []
    quote = None
    esc = False
    line = 1
    start_line = 0
    prev_sig = ""  # previous significant char, for the regex/division call
    i = 0
    n = len(js)
    while i < n:
        ch = js[i]
        if quote:
            if ch == "\n":
                problems.append(
                    f"line {start_line}: unterminated {quote}-quoted string "
                    f"(raw newline inside a JS string literal)"
                )
                quote = None
                line += 1
                esc = False
            elif esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch == "\n":
            line += 1
            i += 1
            continue
        if ch == "/" and i + 1 < n:
            nxt = js[i + 1]
            if nxt == "/":  # line comment
                while i < n and js[i] != "\n":
                    i += 1
                continue
            if nxt == "*":  # block comment
                j = js.find("*/", i + 2)
                if j < 0:
                    j = n
                line += js.count("\n", i, j)
                i = j + 2
                continue
            if prev_sig == "" or prev_sig in _REGEX_OK_AFTER:  # regex literal
                i += 1
                resc = False
                cls = False
                while i < n:
                    c = js[i]
                    if resc:
                        resc = False
                    elif c == "\\":
                        resc = True
                    elif c == "[":
                        cls = True
                    elif c == "]":
                        cls = False
                    elif c == "/" and not cls:
                        i += 1
                        break
                    elif c == "\n":
                        break
                    i += 1
                prev_sig = "/"
                continue
        if ch in "\"'":
            quote = ch
            start_line = line
            i += 1
            continue
        if not ch.isspace():
            prev_sig = ch
        i += 1
    return problems


# Two fixtures the scanner must get right. If it fails them, the build STOPS
# TRUSTING IT rather than blocking on a verdict it cannot justify.
_SELF_TEST_GOOD = 'var re = /"/g;\nvar s = "ok"; // don\'t\nvar d = a / b;\n'
_SELF_TEST_BAD = 'var s = "oops\nstill";\n'


def _scanner_self_test():
    return not fallback_js_scan(_SELF_TEST_GOOD) and bool(fallback_js_scan(_SELF_TEST_BAD))


def check_js(page):
    """Return (ok, method, problems)."""
    js = extract_script(page)
    if not js.strip():
        return False, "none", ["no <script> block found in the emitted page"]
    node = shutil.which("node")
    if node:
        tmp = Path(tempfile.gettempdir()) / f"pdoom1_gallery_jscheck_{os.getpid()}.js"
        tmp.write_text(js, encoding="utf-8", newline="\n")
        try:
            r = subprocess.run(
                [node, "--check", str(tmp)], capture_output=True, text=True, timeout=60
            )
            if r.returncode == 0:
                return True, "node --check", []
            msg = (r.stderr or r.stdout or "").strip().splitlines()
            return False, "node --check", msg[:12]
        except (OSError, subprocess.SubprocessError) as e:
            return True, f"node unavailable ({e.__class__.__name__}); skipped", []
        finally:
            try:
                tmp.unlink()
            except OSError:
                pass
    if not _scanner_self_test():
        return (
            True,
            "NOT CHECKED -- node not found and the built-in scanner failed its "
            "own fixtures, so its verdict is not trustworthy. Install node and "
            "rebuild before relying on this page's keyboard.",
            [],
        )
    problems = fallback_js_scan(js)
    return (not problems), "built-in scanner (node not found)", problems


def main():
    global ART_GEN, ART_SRC, OUT

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--open", action="store_true")
    ap.add_argument(
        "--art-root",
        default=None,
        help="checkout holding art_generated/ and art_source/ (default: this "
        "script's repo). Set it when running from a git WORKTREE -- "
        "art_generated/ is gitignored, so a worktree sees only the legacy "
        "tracked art and none of the current batch.",
    )
    ap.add_argument(
        "--no-js-check",
        action="store_true",
        help="skip the emitted-script syntax gate (do not: a script that does "
        "not parse produces a page with a completely dead keyboard and no "
        "other visible symptom -- that shipped once already)",
    )
    ap.add_argument(
        "--allow-unmapped",
        action="store_true",
        help="index batches that have no destination mapping anyway (their "
        "keep verdicts WILL be stranded until the map rules on them; the "
        "default is to refuse so the map gets its one-line entry first).",
    )
    args = ap.parse_args()

    if args.art_root:
        root = Path(args.art_root).resolve()
        if not root.is_dir():
            sys.exit(f"error: --art-root {root} is not a directory")
        ART_GEN = root / "art_generated"
        ART_SRC = root / "art_source"
        OUT = ART_GEN / "full_gallery.html"
        print(f"[*] art root: {root}")

    t0 = time.time()
    state = load_state()
    batches = scan(state)

    unmapped = preflight_mapping(batches)
    if unmapped:
        print(
            "[!] {} batch(es) have assets with NO destination mapping -- a "
            "review pass over them would strand its own keeps:".format(len(unmapped))
        )
        for title, ids in sorted(unmapped.items()):
            print(f"    {title}  ({len(ids)} unmappable; e.g. {ids[0]})")
        print(
            "    Fix: add a godot/assets/... destination or an explicit "
            "Hold(reason) per batch in tools/art_review/apply_review.py "
            "(GEN_DEST / PX_DEST / PX_PREFIX_CATEGORY). A Hold is a "
            "first-class outcome for concept/reference/master material."
        )
        if not args.allow_unmapped:
            print("    Refusing to build (override: --allow-unmapped).")
            sys.exit(2)
        print("    --allow-unmapped given: building anyway.")

    page, n_assets, n_files, n_matched = build_page(batches, state)

    if not args.no_js_check:
        ok, method, problems = check_js(page)
        print(f"[*] script syntax gate: {method}")
        if not ok:
            print("[!] the emitted <script> DOES NOT PARSE. Refusing to write.")
            for p in problems:
                print("    " + p)
            print(
                "    A page with a broken script still renders every image and "
                "looks correct -- but no key works and no verdict is painted. "
                "That exact defect shipped 2026-08-04 and was live for 3 days."
            )
            return 3

    OUT.write_text(page, encoding="utf-8", newline="\n")
    dt = time.time() - t0

    # coverage cross-check: state keys whose asset never appeared on disk
    seen = set()
    for b in batches:
        for g in b["assets"]:
            seen.add(g.id)
    orphans = [k for k in state if k not in seen]

    print(f"[+] wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)")
    print(
        f"[*] {len(batches)} batches, {n_assets} assets ({n_files} image files), "
        f"{n_matched} with an existing verdict, built in {dt:.1f}s"
    )
    if orphans:
        print(
            f"[!] {len(orphans)} review_state keys matched no file on disk "
            f"(deleted/renamed assets); first few: {orphans[:5]}"
        )
    if args.open:
        webbrowser.open(OUT.as_uri())
    return 0


# NOTE: RAW string. A JS backslash escape inside this template must reach the
# browser verbatim -- see the syntax-gate comment above for what happens when it
# does not. Do not remove the r prefix.
TEMPLATE = r"""<!doctype html>
<meta charset="utf-8">
<title>P(Doom)1 full art gallery -- triage, study, compare</title>
<style>
  :root{--bg:#15151a;--fg:#e9e7e2;--dim:#96938c;--line:#33323b;--card:#1d1d24;
        --acc:#d9955c;--keep:#5fae6e;--iter:#d9b95c;--disc:#c96a5f;--sel:#7aa2d9}
  @media(prefers-color-scheme:light){:root{--bg:#f6f5f2;--fg:#1a1a18;--dim:#63615c;
        --line:#d9d6ce;--card:#fff;--acc:#7a3b12;--sel:#2c5c9c}}
  *{box-sizing:border-box}
  body{background:var(--bg);color:var(--fg);margin:0;padding:0 16px 120px;
       font:13px/1.5 ui-monospace,Consolas,monospace}
  #top{position:sticky;top:0;z-index:10;background:var(--bg);
       border-bottom:1px solid var(--line);padding:8px 0;margin:0 -16px 10px;
       padding-left:16px;padding-right:16px}
  #top h1{font-size:14px;margin:0 0 4px;display:inline}
  #prog{color:var(--dim);margin-left:12px}
  #curb{color:var(--acc)}
  #bar{height:4px;background:var(--line);border-radius:2px;margin-top:6px}
  #barfill{height:100%;background:var(--keep);border-radius:2px;width:0}
  #statewarn{color:var(--dim);font-size:11px;margin-top:4px}
  #statewarn b{color:var(--iter)}
  #bindings{color:var(--dim);font-size:11px;margin-top:2px}
  #bindings b{color:var(--fg)}
  #bindex{columns:3;font-size:11px;margin:0 0 14px;border:1px solid var(--line);
          border-radius:4px;padding:8px 12px}
  #bindex a{display:block;color:var(--dim);text-decoration:none;padding:1px 0}
  #bindex a:hover{color:var(--acc)}
  #bindex .bs{color:var(--acc)}
  /* ---- mode switch + filters ------------------------------------------- */
  #modes{display:flex;gap:6px;align-items:center;margin-top:6px;flex-wrap:wrap}
  #modes button,#filters button{background:var(--card);color:var(--fg);
        border:1px solid var(--line);border-radius:3px;padding:2px 9px;
        font:11px ui-monospace,Consolas,monospace;cursor:pointer}
  #modes button.on{background:var(--acc);border-color:var(--acc);color:#15151a;
        font-weight:700}
  #filters{display:flex;gap:6px;align-items:center;margin-top:5px;flex-wrap:wrap;
        font-size:11px;color:var(--dim)}
  #filters select,#filters input{background:var(--card);color:var(--fg);
        border:1px solid var(--line);border-radius:3px;padding:2px 5px;
        font:11px ui-monospace,Consolas,monospace;max-width:230px}
  #fcount{color:var(--acc)}
  .batch{border-top:1px solid var(--line);padding-top:10px;margin-bottom:22px;
         content-visibility:auto;contain-intrinsic-size:auto 600px}
  h2{font-size:13px;margin:0 0 8px;color:var(--acc)}
  .bstat{color:var(--dim);font-weight:400;font-size:11px;margin-left:10px}
  .bdate{float:right;color:var(--dim);font-weight:400;font-size:11px}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:4px;
        padding:6px;content-visibility:auto;contain-intrinsic-size:auto 210px}
  .card.sel{outline:2px solid var(--sel);outline-offset:1px}
  .card img{width:100%;height:150px;object-fit:contain;display:block;
            background:#0008;border-radius:3px}
  .meta{display:flex;justify-content:space-between;gap:6px;margin-top:4px}
  .nm{font-size:10px;color:var(--dim);overflow:hidden;text-overflow:ellipsis;
      white-space:nowrap}
  .nf{font-size:10px;color:var(--dim)}
  .chip{display:block;font-size:9px;color:var(--acc);overflow:hidden;
        text-overflow:ellipsis;white-space:nowrap;letter-spacing:.04em}
  .vrow{min-height:14px;margin-top:2px;display:flex;gap:6px;align-items:baseline}
  .badge{font-size:10px;font-weight:700;letter-spacing:.05em}
  .badge.keep{color:var(--keep)} .badge.iterate{color:var(--iter)}
  .badge.discard{color:var(--disc)}
  .notetxt{font-size:10px;color:var(--dim);overflow:hidden;text-overflow:ellipsis;
           white-space:nowrap}
  .card.keep{border-color:var(--keep)} .card.iterate{border-color:var(--iter)}
  .card.discard{border-color:var(--disc)}
  .card.hasnote{box-shadow:inset 3px 0 0 var(--sel)}
  body.hiderev .card.rev{display:none}
  .card.filtered{display:none}
  section.batch.empty{display:none}
  /* COMPARE mode: bigger tiles, one facet group at a time. A style DIRECTION is
     judged as a direction, so the tiles have to be big enough to see the
     direction and numerous enough to see it repeat. */
  body.mode-compare .grid{grid-template-columns:repeat(auto-fill,minmax(360px,1fr));
        gap:14px}
  /* height:auto, not a fixed box. A fixed 260px box around a 3:2 picture spends
     a third of every tile on empty letterbox bands -- visible as grey slabs in
     the 08-07 screenshot -- which is exactly the space a compare view cannot
     afford. Same-aspect sets (which is what you compare) still line up. */
  body.mode-compare .card img{height:auto;max-height:420px;background:none}
  body.mode-compare #bindex{display:none}
  /* STUDY mode: the page becomes one picture. */
  body.mode-study #bindex,body.mode-study .batch{display:none}
  #study{display:none}
  body.mode-study #study{display:flex;gap:12px;height:calc(100vh - 210px);
        min-height:420px}
  #stage{flex:1;overflow:auto;background:var(--card);border:1px solid var(--line);
        border-radius:4px;position:relative;cursor:grab;display:flex;
        align-items:center;justify-content:center}
  #stage.drag{cursor:grabbing}
  #stageimg{display:block;image-rendering:auto}
  #stageimg.fit{max-width:98%;max-height:98%}
  /* #side must NOT scroll as a whole. It did, and focusing the note box
     scrolled the zoom and verdict controls off the top -- the reviewer typed a
     note and the L/I/X buttons vanished. Only the record panel scrolls. */
  #side{width:330px;flex:0 0 330px;display:flex;flex-direction:column;gap:8px;
        overflow:hidden}
  #side h3{font-size:11px;margin:0;color:var(--acc);letter-spacing:.06em}
  #srec{font-size:11px;color:var(--dim);border:1px solid var(--line);
        border-radius:4px;padding:8px;line-height:1.55;overflow:auto;flex:1;
        min-height:60px}
  #srec b{color:var(--fg);font-weight:400}
  #srec .k{color:var(--acc);display:inline-block;min-width:74px}
  #snote{width:100%;height:150px;resize:vertical;background:var(--card);
        color:var(--fg);border:1px solid var(--acc);border-radius:4px;padding:8px;
        font:12px/1.5 ui-monospace,Consolas,monospace}
  #snotehint{font-size:10px;color:var(--dim)}
  #sverd{display:flex;gap:6px}
  #sverd button{flex:1;background:var(--card);color:var(--fg);
        border:1px solid var(--line);border-radius:3px;padding:5px 0;
        font:11px ui-monospace,Consolas,monospace;cursor:pointer}
  #sverd button.on.keep{background:var(--keep);border-color:var(--keep);color:#0d1a0c}
  #sverd button.on.iterate{background:var(--iter);border-color:var(--iter);color:#1a160c}
  #sverd button.on.discard{background:var(--disc);border-color:var(--disc);color:#1a0c0c}
  .zrow{display:flex;gap:4px;align-items:center;font-size:11px;color:var(--dim);
        flex-wrap:wrap}
  .zrow button{background:var(--card);color:var(--fg);border:1px solid var(--line);
        border-radius:3px;padding:1px 7px;font:11px ui-monospace,Consolas,monospace;
        cursor:pointer}
  .zrow button.on{background:var(--acc);border-color:var(--acc);color:#15151a}
  /* ---- the MAGNIFIER, ported from build_slot_picker.py --------------------
     Same component, same keys, same wheel/drag behaviour, and it owns the
     keyboard while open so number keys cannot leak to the grid underneath. */
  #lb{position:fixed;inset:0;background:#000e;z-index:90;display:none;
      flex-direction:column}
  #lbbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:8px 12px;
      background:var(--bg);border-bottom:1px solid var(--line);font-size:12px}
  #lbbar button{background:var(--card);color:var(--fg);border:1px solid var(--line);
      border-radius:3px;padding:1px 7px;font:11px ui-monospace,Consolas,monospace;
      cursor:pointer}
  #lbbar button.on{background:var(--acc);border-color:var(--acc);color:#15151a}
  #lbstage{flex:1;overflow:auto;position:relative;cursor:grab;display:flex;
      align-items:center;justify-content:center}
  #lbstage.drag{cursor:grabbing}
  #lbimg{display:block}
  #lbimg.fit{max-width:98%;max-height:98%}
  #lblabel{color:var(--fg)} #lbdims{color:var(--dim)}
  #notebox{position:fixed;left:50%;bottom:60px;transform:translateX(-50%);
           width:min(640px,90vw);display:none;z-index:20}
  #notebox input{width:100%;padding:8px 10px;font:13px ui-monospace,Consolas,monospace;
           background:var(--card);color:var(--fg);border:1px solid var(--acc);
           border-radius:4px}
  #foot{position:fixed;left:0;right:0;bottom:0;background:var(--bg);
        border-top:1px solid var(--line);padding:6px 16px;font-size:11px;
        color:var(--dim);z-index:10}
  #foot b{color:var(--fg)}
  #help{position:fixed;inset:0;background:#000a;z-index:95;display:none;
        overflow:auto}
  #help .in{background:var(--card);border:1px solid var(--line);border-radius:6px;
        max-width:680px;margin:6vh auto;padding:20px 26px;font-size:12px;line-height:1.7}
  #help h3{margin:14px 0 6px;color:var(--acc)}
  #help h3:first-child{margin-top:0}
  #help kbd{background:var(--bg);border:1px solid var(--line);border-radius:3px;
        padding:0 5px;font-family:inherit}
  #unsaved{color:var(--iter);font-weight:700}
  #toast{position:fixed;top:10px;right:14px;background:var(--keep);color:#0d1a0c;
        padding:6px 12px;border-radius:3px;z-index:99;display:none;font-size:12px}
</style>

<div id="top">
  <h1>Full art gallery</h1>
  <span id="prog"></span> <span id="curb"></span>
  <div id="bar"><div id="barfill"></div></div>
  <div id="modes">
    <span style="color:var(--dim);font-size:11px">mode:</span>
    <button id="m1" data-mode="triage">1 TRIAGE</button>
    <button id="m2" data-mode="study">2 STUDY</button>
    <button id="m3" data-mode="compare">3 COMPARE</button>
    <span id="modehint" style="color:var(--dim);font-size:11px"></span>
  </div>
  <div id="filters">
    <span>filter:</span>
    <select id="f-batch"><option value="">all batches</option></select>
    <span id="facetsel"></span>
    <input type="text" id="f-q" placeholder="name contains..." size="16">
    <select id="f-rev">
      <option value="">any verdict</option>
      <option value="none">unreviewed only</option>
      <option value="keep">keep</option>
      <option value="iterate">iterate</option>
      <option value="discard">discard</option>
      <option value="noted">has a note</option>
    </select>
    <button id="f-clear">clear</button>
    <span id="fcount"></span>
  </div>
  <div id="statewarn"><b>State lives in THIS browser's localStorage</b> (plus the
    baked-in baseline from review_state.json, built __BUILT__). A browser data
    clear loses unexported verdicts -- press <b>E</b> to export, then run
    <b>python tools/art_review/merge_gallery_export.py &lt;download&gt;</b> to fold
    them into review_state.json. Unexported changes: <span id="unsaved">0</span></div>
  <div id="bindings"><b>1/2/3</b> mode | <b>J/K</b> or arrows move |
    <b>L</b> keep | <b>I</b> iterate | <b>X</b> discard | <b>U</b> clear |
    <b>N</b> note | <b>F</b> magnify | <b>B</b>/<b>Shift+B</b> batch jump |
    <b>H</b> hide reviewed | <b>Shift+L/I/X</b> whole batch (or compare group) |
    <b>Enter/O</b> open full | <b>E</b> export | <b>?</b> help</div>
</div>

<nav id="bindex">__BATCHINDEX__</nav>

<div id="study">
  <div id="stage"><img id="stageimg" class="fit" alt=""></div>
  <div id="side">
    <div class="zrow"><span>zoom:</span>
      <button class="sz on" data-s="fit">fit</button>
      <button class="sz" data-s="1">100%</button>
      <button class="sz" data-s="2">200%</button>
      <button class="sz" data-s="4">400%</button>
      <span>wheel = zoom, drag = pan</span></div>
    <div id="sverd">
      <button data-v="keep" class="keep">L keep</button>
      <button data-v="iterate" class="iterate">I iterate</button>
      <button data-v="discard" class="discard">X discard</button>
    </div>
    <h3>NOTE -- a brief for the next round</h3>
    <textarea id="snote" placeholder="What is right or wrong about THIS picture? Notes are read back as the brief for the next generation round, so name the thing: the value structure, the palette, the prop vocabulary, the light."></textarea>
    <div id="snotehint">saves as you type (localStorage) -- press <b>E</b> to
      export, then merge into review_state.json</div>
    <h3>GENERATION RECORD</h3>
    <div id="srec"></div>
  </div>
</div>

__SECTIONS__

<div id="notebox"><input id="notein" placeholder="note -- Enter saves, Esc cancels"></div>
<div id="foot">Selected: <b id="selname">(none -- press J)</b>
  <span id="selverdict"></span></div>

<div id="lb">
  <div id="lbbar">
    <button id="lbclose">[ESC] close</button>
    <span id="lblabel"></span><span id="lbdims"></span>
    <span>zoom:</span>
    <button class="lbz on" data-s="fit">fit</button>
    <button class="lbz" data-s="1">100%</button>
    <button class="lbz" data-s="2">200%</button>
    <button class="lbz" data-s="4">400%</button>
    <span style="color:var(--dim)">wheel = zoom &middot; drag = pan &middot;
      [ and ] step &middot; L/I/X still judge</span>
  </div>
  <div id="lbstage"><img id="lbimg" class="fit" alt=""></div>
</div>

<div id="toast"></div>

<div id="help"><div class="in">
  <h3>Three modes, split by what you are doing</h3>
  <kbd>1</kbd> <b>TRIAGE</b> -- dense grid, one keystroke per decision. How 600
  images become 60.<br>
  <kbd>2</kbd> <b>STUDY</b> -- one image large, arrows rotate through the working
  set, multi-line note beside it, generation record underneath. For saying
  something specific.<br>
  <kbd>3</kbd> <b>COMPARE</b> -- big tiles. Filter to one direction or one
  subject and judge the whole family as a family.<br><br>
  The <b>filter bar</b> sets the working set for ALL THREE modes: what you filter
  to in triage is what study rotates through and what compare tiles.
  <h3>Keys</h3>
  <kbd>J</kbd>/<kbd>K</kbd> or arrow keys: next / previous asset<br>
  <kbd>L</kbd> keep (promotable) | <kbd>I</kbd> iterate (remix/regenerate) |
  <kbd>X</kbd> discard (off-brief) | <kbd>U</kbd> clear verdict<br>
  <kbd>N</kbd> note on selected asset (in STUDY the note box is always there) |
  <kbd>F</kbd> magnify full-screen | <kbd>Enter</kbd>/<kbd>O</kbd> open full-size
  in a new tab | <kbd>B</kbd>/<kbd>Shift+B</kbd> next/prev batch |
  <kbd>H</kbd> hide reviewed | <kbd>E</kbd> export JSON | <kbd>/</kbd> jump to
  the name filter<br>
  Verdicts auto-advance to the next visible asset. Click a card to select it.
  <h3>The magnifier</h3>
  <kbd>F</kbd> opens the full-screen magnifier -- the same component the slot
  picker uses. fit / 100% / 200% / 400%, wheel to zoom, drag to pan,
  <kbd>[</kbd> and <kbd>]</kbd> to step through the working set without leaving
  it. It owns the keyboard while open, so nothing leaks to the grid underneath.
  <kbd>L</kbd>/<kbd>I</kbd>/<kbd>X</kbd> still judge from inside it.
  <h3>Bulk verdicts</h3>
  <kbd>Shift+L</kbd> / <kbd>Shift+I</kbd> / <kbd>Shift+X</kbd> apply keep /
  iterate / discard to <b>every UNREVIEWED asset</b> in the current batch (TRIAGE
  and STUDY) or in the whole visible working set (COMPARE), after a confirm
  showing the count. For rotation sets and walk cycles, where eight files are one
  artistic decision -- and in COMPARE, for a style direction you have decided
  about as a direction.<br>
  <b>Assets you have already judged are never overwritten</b> -- a sweep only
  fills gaps, so it can follow a careful pass without undoing it.
  <h3>Where state lives</h3>
  Verdicts and notes persist in this browser's localStorage immediately.
  They are NOT in the repo until you press <kbd>E</kbd> (downloads
  gallery_verdicts_*.json) and run<br>
  <b>python tools/art_review/merge_gallery_export.py path/to/download.json</b><br>
  which merges into tools/art_review/review_state.json -- which IS tracked in
  git, so your notes become diffable history the moment you merge them.
  <b>python tools/art_review/notes_brief.py</b> then rewrites
  docs/art/NOTES_BRIEF.md, the generated brief the next generation round reads.
  Press <kbd>?</kbd> or <kbd>Esc</kbd> to close.
</div></div>

<script>
"use strict";
var BASELINE = __BASELINE__;
var STRINGS = __STRINGS__;
var FACETOPTS = __FACETOPTS__;
var FACETORDER = __FACETORDER__;
var CARDMETA = __CARDMETA__;
var NBATCH = __NBATCH__;
var LS_KEY = "pdoom1_full_gallery_v1";
var LS_EXP = "pdoom1_full_gallery_last_export";

var local = {};
try { local = JSON.parse(localStorage.getItem(LS_KEY) || "{}") || {}; }
catch (e) { local = {}; }

function eff(id) {
  if (Object.prototype.hasOwnProperty.call(local, id)) {
    return { v: local[id].verdict || "", n: local[id].note || "" };
  }
  var b = BASELINE[id];
  return b ? { v: b.v || "", n: b.n || "" } : { v: "", n: "" };
}
function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
                  .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
var sections = Array.prototype.slice.call(document.querySelectorAll("section.batch"));
var batchIds = [];   // per batch: array of unique ids
var idBatch = {};    // id -> batch number (first seen)
for (var i = 0; i < NBATCH; i++) batchIds.push([]);
cards.forEach(function (c) {
  var id = c.dataset.id, b = +c.dataset.b;
  if (!(id in idBatch)) { idBatch[id] = b; batchIds[b].push(id); }
});
var totalAssets = Object.keys(idBatch).length;

function cardsFor(id) {
  return cards.filter(function (c) { return c.dataset.id === id; });
}
function paintCard(c) {
  var e = eff(c.dataset.id);
  var badge = c.querySelector(".badge"), note = c.querySelector(".notetxt");
  badge.textContent = e.v ? e.v.toUpperCase() : "";
  badge.className = "badge " + e.v;
  note.textContent = e.n;
  note.title = e.n;
  c.classList.remove("keep", "iterate", "discard", "rev", "hasnote");
  if (e.v) { c.classList.add(e.v, "rev"); }
  if (e.n) { c.classList.add("hasnote"); }
}
function paintAll() { cards.forEach(paintCard); refreshCounts(); }

function refreshCounts() {
  var done = 0;
  for (var b = 0; b < NBATCH; b++) {
    var d = 0;
    batchIds[b].forEach(function (id) { if (eff(id).v) d++; });
    done += d;
    var bs = document.getElementById("bs" + b);
    if (bs) bs.textContent = d + " / " + batchIds[b].length + " reviewed";
    var bi = document.getElementById("bi" + b);
    if (bi) bi.textContent = d + "/" + batchIds[b].length;
  }
  document.getElementById("prog").textContent =
    done + " of " + totalAssets + " assets reviewed (" +
    (totalAssets ? Math.round(100 * done / totalAssets) : 0) + " percent)";
  document.getElementById("barfill").style.width =
    (totalAssets ? 100 * done / totalAssets : 0) + "%";
  refreshUnsaved();
}
function refreshUnsaved() {
  var last = localStorage.getItem(LS_EXP) || "";
  var n = 0;
  for (var id in local) {
    if ((local[id].updated_at || "") > last) n++;
  }
  document.getElementById("unsaved").textContent = n;
  window.__unsaved = n;
}

// ---- filtering: ONE working set, shared by all three modes ----------------
// The reason grouping and the modes are the same feature: "show me every
// MUNICIPAL RECORD image" is useless if it only holds in one layout. Filter in
// triage, switch to compare, and you are looking at the same 22 pictures.
var FILT = { batch: "", facets: {}, q: "", rev: "" };

function facetAttr(f) {
  return "f" + f.charAt(0).toUpperCase() + f.slice(1);
}

function buildFacetSelects() {
  var host = document.getElementById("facetsel");
  var out = [];
  FACETORDER.forEach(function (f) {
    var opts = FACETOPTS[f];
    if (!opts || !opts.length) return;
    var h = '<select class="ffac" data-f="' + f + '"><option value="">all ' +
            esc(f) + 's</option>';
    opts.forEach(function (o) {
      h += '<option value="' + o[0] + '">' + esc(STRINGS[o[0]]) +
           " (" + o[2] + ")</option>";
    });
    out.push(h + "</select>");
  });
  host.innerHTML = out.join(" ");
  Array.prototype.forEach.call(host.querySelectorAll(".ffac"), function (s) {
    s.addEventListener("change", function () {
      var v = s.value;
      if (v === "") delete FILT.facets[s.dataset.f];
      else FILT.facets[s.dataset.f] = v;
      applyFilter();
    });
  });
  var bsel = document.getElementById("f-batch");
  for (var b = 0; b < NBATCH; b++) {
    var h2 = sections[b] ? sections[b].querySelector("h2") : null;
    var title = h2 ? h2.childNodes[0].nodeValue : "batch " + (b + 1);
    var o = document.createElement("option");
    o.value = String(b);
    o.textContent = title + " (" + batchIds[b].length + ")";
    bsel.appendChild(o);
  }
}

function cardPasses(c) {
  if (FILT.batch !== "" && c.dataset.b !== FILT.batch) return false;
  for (var f in FILT.facets) {
    if (c.dataset[facetAttr(f)] !== FILT.facets[f]) return false;
  }
  if (FILT.q) {
    var chip = c.querySelector(".chip");
    var hay = c.dataset.id + " " + (c.querySelector(".nm").textContent || "") +
              " " + (chip ? chip.textContent : "");
    if (hay.toLowerCase().indexOf(FILT.q) < 0) return false;
  }
  if (FILT.rev) {
    var e = eff(c.dataset.id);
    if (FILT.rev === "none" && e.v) return false;
    if (FILT.rev === "noted" && !e.n) return false;
    if (FILT.rev !== "none" && FILT.rev !== "noted" && e.v !== FILT.rev) return false;
  }
  return true;
}
function applyFilter(keepSel) {
  var n = 0;
  cards.forEach(function (c) {
    var ok = cardPasses(c);
    c.classList.toggle("filtered", !ok);
    if (ok) n++;
  });
  // hide a section that has nothing left, so the page is not a field of headers
  sections.forEach(function (s) {
    s.classList.toggle("empty", !s.querySelector(".card:not(.filtered)"));
  });
  document.getElementById("fcount").textContent =
    n === cards.length ? "" : (n + " of " + cards.length + " shown");
  if (!keepSel && (sel < 0 || !visible(cards[sel]))) { sel = -1; move(1); }
  syncStudy();
}

// ---- selection ----
var sel = -1;
// "In the working set" is a PROPERTY OF THE DATA, not of the layout.
//
// This used to be `c.offsetParent !== null`, and a real browser found two ways
// that is wrong (2026-08-07, Edge/Chromium):
//   1. `.batch` carries `content-visibility:auto`. Chromium SKIPS the contents
//      of an off-screen section, and a skipped subtree's children report
//      offsetParent === null. So J/K silently refused to walk into any batch
//      that was not already scrolled near -- traversal depended on where the
//      page happened to be scrolled.
//   2. STUDY mode hides the whole grid by design, which made EVERY card
//      "invisible" and froze the arrow keys completely.
// Both vanish once membership is asked of the classes that actually define it.
// It is also cheaper: offsetParent forces a layout flush per card, 6205 times.
function visible(c) {
  if (!c) return false;
  if (c.classList.contains("filtered")) return false;
  if (document.body.classList.contains("hiderev") && c.classList.contains("rev"))
    return false;
  return true;
}
function workingSet() {
  return cards.filter(visible);
}
function select(i, scroll) {
  if (i < 0 || i >= cards.length) return;
  // Clear by QUERY, not by remembered index. applyFilter resets `sel` to -1 to
  // force a re-pick, which stranded the outline on the old card -- two cards
  // showed as selected at once (seen by eye in a browser screenshot, 08-07).
  Array.prototype.forEach.call(document.querySelectorAll(".card.sel"),
    function (c) { c.classList.remove("sel"); });
  sel = i;
  var c = cards[sel];
  c.classList.add("sel");
  if (scroll !== false && MODE !== "study") c.scrollIntoView({ block: "center" });
  var e = eff(c.dataset.id);
  var b = +c.dataset.b;
  document.getElementById("selname").textContent = c.dataset.id;
  document.getElementById("selverdict").textContent =
    (e.v ? " [" + e.v + "]" : "") + (e.n ? " note: " + e.n.split("\n")[0] : "");
  document.getElementById("curb").textContent =
    "| batch " + (b + 1) + " of " + NBATCH;
  syncStudy();
}
function move(step) {
  var i = sel;
  do { i += step; } while (i >= 0 && i < cards.length && !visible(cards[i]));
  if (i >= 0 && i < cards.length) select(i);
  else if (sel < 0 && cards.length) {
    for (var j = 0; j < cards.length; j++) if (visible(cards[j])) { select(j); break; }
  }
}
function jumpBatch(dir) {
  var cur = sel >= 0 ? +cards[sel].dataset.b : -1;
  var target = cur + dir;
  if (target < 0 || target >= NBATCH) return;
  for (var i = 0; i < cards.length; i++) {
    if (+cards[i].dataset.b === target && visible(cards[i])) { select(i); return; }
  }
  // batch fully hidden: keep going
  if (target >= 0 && target < NBATCH) {
    cur = target;
    while (cur + dir >= 0 && cur + dir < NBATCH) {
      cur += dir;
      for (var k = 0; k < cards.length; k++) {
        if (+cards[k].dataset.b === cur && visible(cards[k])) { select(k); return; }
      }
    }
  }
}
cards.forEach(function (c, i) {
  c.addEventListener("click", function (ev) {
    if (ev.target.tagName !== "IMG" && ev.target.tagName !== "A") select(i, false);
  });
});

// ---- verdict + note writes ----
function save() { localStorage.setItem(LS_KEY, JSON.stringify(local)); }
function writeEntry(id, verdict, note) {
  local[id] = { verdict: verdict, note: note, tags: [],
                updated_at: new Date().toISOString() };
  save();
  cardsFor(id).forEach(paintCard);
  refreshCounts();
}
function setVerdict(v) {
  if (sel < 0) return;
  var id = cards[sel].dataset.id;
  writeEntry(id, v, eff(id).n);
  select(sel, false);
  if (v) move(1);
}
// ---- BATCH / GROUP verdicts ----------------------------------------------
// Pip, 2026-08-04: "I don't like the idea of having to manually review all the
// frames of a walking animation, or if I do, there should be a batch selection
// option." A rotation set is ONE artistic decision spread over 8 files; making
// the reviewer press a key 8 times does not make the judgement any better, it
// just makes the pile look bigger than it is.
//
// In COMPARE the unit is the visible working set instead of the batch, because
// that is the whole point of compare: you filtered to one style direction and
// you are deciding about the DIRECTION.
//
// Applies only to cards with NO existing verdict, so a considered per-asset call
// is never overwritten by a sweep. Confirms with a count first -- a bulk action
// that fires silently is how you lose an hour of judgement to one keystroke.
function setBatchVerdict(v) {
  if (sel < 0) return;
  var groupIsWorkingSet = (MODE === "compare");
  var b = cards[sel].dataset.b;
  var targets = [];
  var seen = {};
  var pool = groupIsWorkingSet ? workingSet() : cards;
  for (var i = 0; i < pool.length; i++) {
    if (!groupIsWorkingSet && pool[i].dataset.b !== b) continue;
    var id = pool[i].dataset.id;
    if (seen[id]) continue;
    if (eff(id).v) continue;            // never stomp an existing verdict
    seen[id] = 1;
    targets.push(id);
  }
  if (!targets.length) {
    alert("Nothing unreviewed left in " +
          (groupIsWorkingSet ? "the visible group." : "this batch."));
    return;
  }
  var label = v ? v.toUpperCase() : "CLEAR";
  var scope = groupIsWorkingSet ? "the VISIBLE GROUP" : "this batch";
  if (!confirm("Set " + label + " on " + targets.length +
               " UNREVIEWED asset(s) in " + scope + "?\n\n" +
               "Already-judged assets are left alone.")) return;
  var now = new Date().toISOString();
  targets.forEach(function (id) {
    local[id] = { verdict: v, note: eff(id).n, tags: [], updated_at: now };
  });
  save();
  targets.forEach(function (id) { cardsFor(id).forEach(paintCard); });
  refreshCounts();
  select(sel, false);
  if (!visible(cards[sel])) move(1);
}
var notebox = document.getElementById("notebox");
var notein = document.getElementById("notein");
function openNote() {
  if (sel < 0) return;
  if (MODE === "study") { document.getElementById("snote").focus(); return; }
  notein.value = eff(cards[sel].dataset.id).n;
  notebox.style.display = "block";
  notein.focus();
}
notein.addEventListener("keydown", function (ev) {
  ev.stopPropagation();
  if (ev.key === "Enter") {
    var id = cards[sel].dataset.id;
    writeEntry(id, eff(id).v, notein.value);
    select(sel, false);
    notebox.style.display = "none";
  } else if (ev.key === "Escape") {
    notebox.style.display = "none";
  }
});

// ---- STUDY mode -----------------------------------------------------------
// "maybe an in-house preview frame so I'm not popping open new windows... a kind
// of gallery-rotate rather than scroll?" -- Pip, 2026-08-07. Rotate, not scroll:
// the picture stays put and the CONTENT changes under it, so the eye never has
// to re-find the frame between two images. That is also what makes A-vs-B
// comparison possible at all in a single-image view: flicking left and right
// between two images in the same rectangle shows differences that side-by-side
// at different screen positions hides.
var MODE = "triage";
var stageScale = "fit";
var stageImg = document.getElementById("stageimg");
var snote = document.getElementById("snote");

function setMode(m) {
  MODE = m;
  document.body.classList.remove("mode-triage", "mode-study", "mode-compare");
  document.body.classList.add("mode-" + m);
  ["m1", "m2", "m3"].forEach(function (bid) {
    var el = document.getElementById(bid);
    el.classList.toggle("on", el.dataset.mode === m);
  });
  document.getElementById("modehint").textContent =
    m === "triage" ? "dense grid, one keystroke per decision" :
    m === "study" ? "arrows rotate through the working set; note box is live" :
    "big tiles -- filter to one direction and judge the family";
  if (sel < 0 || !visible(cards[sel])) move(1);
  syncStudy();
  if (m !== "study") window.scrollTo(0, 0);
}
function syncStudy() {
  if (MODE !== "study") return;
  if (sel < 0 || !cards[sel]) { stageImg.removeAttribute("src"); return; }
  var id = cards[sel].dataset.id;
  var cm = CARDMETA[id] || {};
  var a = cards[sel].querySelector("a");
  var want = a ? a.getAttribute("href") : "";
  // Guard the assignment: syncStudy runs on every note keystroke, and
  // re-assigning .src restarts decode and flashes the picture the reviewer is
  // in the middle of describing.
  if (stageImg.getAttribute("src") !== want) { stageImg.src = want; }
  applyStageScale();
  var e = eff(id);
  if (snote.value !== e.n) snote.value = e.n;
  Array.prototype.forEach.call(document.querySelectorAll("#sverd button"),
    function (b) { b.classList.toggle("on", b.dataset.v === e.v); });
  var ws = workingSet();
  var pos = ws.indexOf(cards[sel]) + 1;
  var rows = [
    ["asset", id],
    ["batch", cm.batch || ""],
    ["files", (cm.n || 1) + " size(s)"],
    ["position", pos + " of " + ws.length + " in the working set"]
  ];
  // Blocks with no NAMED direction fall back to the rendering clause, which
  // then prints the same long sentence twice. Show each distinct value once.
  var shownVals = {};
  FACETORDER.forEach(function (f) {
    var v = cards[sel].dataset[facetAttr(f)];
    if (v === undefined || shownVals[v]) return;
    shownVals[v] = 1;
    rows.push([f, STRINGS[+v]]);
  });
  if (cm.meta) rows.push(["record", cm.meta]);
  rows.push(["origin", "MACHINE-GENERATED (see the sidecar record)"]);
  document.getElementById("srec").innerHTML = rows.map(function (r) {
    return '<div><span class="k">' + esc(r[0]) + "</span> <b>" + esc(r[1]) + "</b></div>";
  }).join("");
}
function applyStageScale() {
  if (stageScale === "fit") { stageImg.className = "fit"; stageImg.style.width = ""; }
  else {
    stageImg.className = "";
    stageImg.style.width = ((stageImg.naturalWidth || 1024) * stageScale) + "px";
  }
  Array.prototype.forEach.call(document.querySelectorAll(".sz"), function (b) {
    b.classList.toggle("on", String(stageScale) === b.dataset.s);
  });
}
function setStageScale(s) {
  stageScale = (s === "fit") ? "fit" : parseFloat(s);
  applyStageScale();
}
// The note box writes on every keystroke. A note the reviewer typed and lost
// because they pressed the arrow key before some explicit save is exactly the
// kind of loss this tool exists to prevent.
snote.addEventListener("input", function () {
  if (sel < 0) return;
  var id = cards[sel].dataset.id;
  writeEntry(id, eff(id).v, snote.value);
  select(sel, false);
});
snote.addEventListener("keydown", function (ev) {
  ev.stopPropagation();
  if (ev.key === "Escape") { snote.blur(); }
});
Array.prototype.forEach.call(document.querySelectorAll("#sverd button"),
  function (b) { b.addEventListener("click", function () { setVerdict(b.dataset.v); }); });
Array.prototype.forEach.call(document.querySelectorAll(".sz"),
  function (b) { b.addEventListener("click", function () { setStageScale(b.dataset.s); }); });

// ---- the MAGNIFIER (ported from build_slot_picker.py) ---------------------
var lb = { open: false, scale: "fit" };
var lbimg = document.getElementById("lbimg");
function lbOpen() {
  if (sel < 0) return;
  lb.open = true; lb.scale = "fit";
  document.getElementById("lb").style.display = "flex";
  lbPaint();
}
function lbClose() {
  lb.open = false;
  document.getElementById("lb").style.display = "none";
}
function lbPaint() {
  if (!lb.open || sel < 0) return;
  var c = cards[sel];
  var a = c.querySelector("a");
  var want = a ? a.getAttribute("href") : "";
  if (lbimg.getAttribute("src") !== want) { lbimg.src = want; }
  if (lb.scale === "fit") { lbimg.className = "fit"; lbimg.style.width = ""; }
  else {
    lbimg.className = "";
    lbimg.style.width = ((lbimg.naturalWidth || 1024) * lb.scale) + "px";
  }
  var e = eff(c.dataset.id);
  var ws = workingSet();
  document.getElementById("lblabel").textContent =
    c.dataset.id + "  (" + (ws.indexOf(c) + 1) + "/" + ws.length + ")" +
    (e.v ? "  [" + e.v.toUpperCase() + "]" : "");
  var cm = CARDMETA[c.dataset.id] || {};
  document.getElementById("lbdims").textContent =
    "  " + (cm.batch || "") + "  " + (lbimg.naturalWidth || "?") + "x" +
    (lbimg.naturalHeight || "?");
  Array.prototype.forEach.call(document.querySelectorAll(".lbz"), function (b) {
    b.classList.toggle("on", String(lb.scale) === b.dataset.s);
  });
}
function lbSetScale(s) {
  lb.scale = (s === "fit") ? "fit" : parseFloat(s);
  lbPaint();
}
lbimg.addEventListener("load", function () { if (lb.open) lbPaint(); });
stageImg.addEventListener("load", function () { applyStageScale(); });
Array.prototype.forEach.call(document.querySelectorAll(".lbz"),
  function (b) { b.addEventListener("click", function () { lbSetScale(b.dataset.s); }); });
document.getElementById("lbclose").addEventListener("click", lbClose);

function wirePanZoom(stageId, getScale, setScale) {
  var stage = document.getElementById(stageId);
  stage.addEventListener("wheel", function (ev) {
    ev.preventDefault();
    var cur = getScale();
    cur = (cur === "fit") ? 1 : cur;
    setScale(ev.deltaY < 0 ? Math.min(8, cur * 1.25) : Math.max(0.25, cur / 1.25));
  }, { passive: false });
  var down = false, sx = 0, sy = 0, ol = 0, ot = 0;
  stage.addEventListener("mousedown", function (ev) {
    down = true; sx = ev.clientX; sy = ev.clientY;
    ol = stage.scrollLeft; ot = stage.scrollTop;
    stage.classList.add("drag"); ev.preventDefault();
  });
  document.addEventListener("mousemove", function (ev) {
    if (!down) return;
    stage.scrollLeft = ol - (ev.clientX - sx);
    stage.scrollTop = ot - (ev.clientY - sy);
  });
  document.addEventListener("mouseup", function () {
    down = false; stage.classList.remove("drag");
  });
}
wirePanZoom("lbstage", function () { return lb.scale; }, lbSetScale);
wirePanZoom("stage", function () { return stageScale; }, setStageScale);

// ---- export ----
var toastEl = document.getElementById("toast"), toastT = 0;
function toast(msg) {
  toastEl.textContent = msg;
  toastEl.style.display = "block";
  clearTimeout(toastT);
  toastT = setTimeout(function () { toastEl.style.display = "none"; }, 2600);
}
function doExport() {
  var blob = new Blob([JSON.stringify(local, null, 2)],
                      { type: "application/json" });
  var a = document.createElement("a");
  var ts = new Date().toISOString().slice(0, 16).replace(/[:T]/g, "-");
  a.href = URL.createObjectURL(blob);
  a.download = "gallery_verdicts_" + ts + ".json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  localStorage.setItem(LS_EXP, new Date().toISOString());
  refreshUnsaved();
  toast("exported -- now run merge_gallery_export.py");
}
window.addEventListener("beforeunload", function (ev) {
  if (window.__unsaved > 0) { ev.preventDefault(); ev.returnValue = ""; }
});

// ---- keys ----
// The guard is on the ELEMENT KIND, not on one known input. The filter bar added
// a text box and six <select>s; a handler that only knew about #notein would
// have let every keystroke typed into a filter also fire a verdict.
function isTyping(t) {
  if (!t) return false;
  var tag = t.tagName;
  return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" ||
         t.isContentEditable;
}
document.addEventListener("keydown", function (ev) {
  if (isTyping(ev.target)) return;
  if (ev.ctrlKey || ev.metaKey || ev.altKey) return;
  var k = ev.key;
  var handled = true;
  var helpEl = document.getElementById("help");

  // The magnifier OWNS the keyboard while it is open. Letting the page's keys
  // fire underneath it is how "3" both magnifies and switches mode.
  if (lb.open) {
    if (k === "Escape" || k === "f" || k === "F") lbClose();
    else if (k === "[" || k === "k" || k === "K" || k === "ArrowLeft") { move(-1); lbPaint(); }
    else if (k === "]" || k === "j" || k === "J" || k === "ArrowRight") { move(1); lbPaint(); }
    else if (k === "l" || k === "L") { setVerdict("keep"); lbPaint(); }
    else if (k === "i" || k === "I") { setVerdict("iterate"); lbPaint(); }
    else if (k === "x" || k === "X") { setVerdict("discard"); lbPaint(); }
    else if (k === "u" || k === "U") { setVerdict(""); lbPaint(); }
    else if (k === "1") lbSetScale("fit");
    else if (k === "2") lbSetScale(1);
    else if (k === "3") lbSetScale(2);
    else if (k === "4") lbSetScale(4);
    else handled = false;
    if (handled) ev.preventDefault();
    return;
  }
  if (helpEl.style.display === "block" && (k === "Escape" || k === "?")) {
    helpEl.style.display = "none";
    ev.preventDefault();
    return;
  }

  if (k === "j" || k === "J" || k === "ArrowRight" || k === "ArrowDown") move(1);
  else if (k === "k" || k === "K" || k === "ArrowLeft" || k === "ArrowUp") move(-1);
  else if (k === "l") setVerdict("keep");
  else if (k === "i") setVerdict("iterate");
  else if (k === "x") setVerdict("discard");
  else if (k === "u" || k === "U" || k === "0") setVerdict("");
  else if (k === "n" || k === "N") openNote();
  else if (k === "f" || k === "F") lbOpen();
  else if (k === "1") setMode("triage");
  else if (k === "2") setMode("study");
  else if (k === "3") setMode("compare");
  else if (k === "b") jumpBatch(1);
  else if (k === "B") jumpBatch(-1);
  else if (k === "L") setBatchVerdict("keep");
  else if (k === "I") setBatchVerdict("iterate");
  else if (k === "X") setBatchVerdict("discard");
  else if (k === "/") { document.getElementById("f-q").focus(); }
  else if (k === "h" || k === "H") {
    document.body.classList.toggle("hiderev");
    if (sel >= 0 && !visible(cards[sel])) move(1);
    syncStudy();
  }
  else if (k === "e" || k === "E") doExport();
  else if (k === "Enter" || k === "o" || k === "O") {
    if (sel >= 0) window.open(cards[sel].querySelector("a").href, "_blank");
  }
  else if (k === "?") {
    helpEl.style.display = helpEl.style.display === "block" ? "none" : "block";
  }
  else handled = false;
  if (handled) ev.preventDefault();
});
document.getElementById("help").addEventListener("click", function (ev) {
  if (ev.target === this) this.style.display = "none";
});
["m1", "m2", "m3"].forEach(function (bid) {
  document.getElementById(bid).addEventListener("click", function () {
    setMode(this.dataset.mode);
  });
});
document.getElementById("f-batch").addEventListener("change", function () {
  FILT.batch = this.value; applyFilter();
});
document.getElementById("f-q").addEventListener("input", function () {
  FILT.q = this.value.trim().toLowerCase(); applyFilter();
});
document.getElementById("f-q").addEventListener("keydown", function (ev) {
  ev.stopPropagation();
  if (ev.key === "Escape" || ev.key === "Enter") this.blur();
});
document.getElementById("f-rev").addEventListener("change", function () {
  FILT.rev = this.value; applyFilter();
});
document.getElementById("f-clear").addEventListener("click", function () {
  FILT = { batch: "", facets: {}, q: "", rev: "" };
  document.getElementById("f-batch").value = "";
  document.getElementById("f-q").value = "";
  document.getElementById("f-rev").value = "";
  Array.prototype.forEach.call(document.querySelectorAll(".ffac"),
    function (s) { s.value = ""; });
  applyFilter();
});

buildFacetSelects();
paintAll();
setMode("triage");
applyFilter(true);
</script>
"""


if __name__ == "__main__":
    raise SystemExit(main())
