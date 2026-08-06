#!/usr/bin/env python3
"""find_dead_code.py -- report-only dead-path scanner for P(Doom)1.

Turns the 2026-08-04 manual sweep (PR #1118, issue #1117) into a repeatable
instrument. Pip's framing: run it regularly, and when you start to smell an
opportunity. Regularity comes from a script, not discipline.

THIS TOOL NEVER DELETES ANYTHING. It reports. The manual pass found four
things that looked dead and were live (steam_manager.gd scaffolding,
candidate_card.gd test-only, godot/data/events/overrides/example.json loaded
by a directory glob, cats/default grandfathered) -- an auto-deleter would have
silently changed the game.

What it detects (each category earned by a real find in PR #1118):
  1. GDScript with no callers (no class_name use, no res://, no uid://,
     nothing in a .tscn) -- the five orphan UI widgets.
  2. Scenes nothing loads.
  3. Python nothing imports and no workflow/hook/Makefile invokes.
  4. Shell scripts nothing invokes -- the sync_from_pdoom_data.sh class:
     documented, referenced in prose, never executably reachable.
  5. Docs whose backticked paths do not resolve -- the ~25-doc long tail.
  6. Assets in godot/ that nothing references. Godot packs the ENTIRE tree
     (issue #787), but eight-ish loaders build res:// paths at runtime, so
     anything under such a directory is UNVERIFIABLE, never "dead".

Confidence tiers (the tiers are the whole value -- a flat list gets ignored):
  CONFIRMED    -- no reference of any kind, by any mechanism this scanner
                  checks. Evidence says exactly which mechanisms were checked.
  LIKELY       -- no executable/static reference, but a mechanism exists that
                  static analysis cannot fully rule out (doc-only mentions,
                  callers that are themselves flagged, basename strings in
                  live code).
  UNVERIFIABLE -- a runtime-constructed load path could reach this file.
                  Static analysis is blind here. NEVER treat as dead.

Deliberately NOT wired into pre-commit or CI. This is a tool you RUN, not a
gate: #1117 records the Python CI lane running `|| echo` and reporting green
over zero assertions. A gate that fails on ambiguous evidence gets disabled.

Usage:
  python tools/find_dead_code.py                 # scan repo root, human output
  python tools/find_dead_code.py --json          # machine-readable
  python tools/find_dead_code.py --since REF     # only files changed since REF
  python tools/find_dead_code.py --root PATH     # scan another checkout
  python tools/find_dead_code.py --include-retained  # also scan archive/ etc.

Exit code is always 0 on a completed scan (report, not gate).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Directories retained by policy (repo cruft/archival policy: delete what is
# irrelevant, archive what has evolutionary value). Skipped by default.
RETAINED_PREFIXES = (
    "archive/",
    "archived/",
    "docs/archive/",
    "art_source/",
    "legacy/",
)

# Third-party code: never a candidate, and not scanned as a reference source
# (nothing in addons/ confers liveness on game files by design).
THIRD_PARTY_PREFIXES = ("godot/addons/",)

# Known-live allowlist. Every entry states WHY so the next reader can
# challenge it. These are files a zero-reference scan WOULD flag but that the
# PR #1118 sweep (or repo policy) established as deliberately alive.
ALLOWLIST = {
    "godot/autoload/steam_manager.gd": (
        "Unfinished Steam scaffolding deliberately KEPT in PR #1118: not in "
        "project.godot [autoload] and nothing references it, but "
        "addons/godotsteam is installed and godot/steam_appid.txt exists. "
        "Scaffolding, not a corpse."
    ),
    "godot/steam_appid.txt": (
        "Companion to steam_manager.gd scaffolding (contains 480, Valve's "
        "Spacewar test appid). Goes when the Steam decision is made."
    ),
    "tools/find_dead_code.py": "This scanner.",
    "tests/test_find_dead_code.py": (
        "Unit tests for this scanner; collected by unittest discovery."
    ),
}

# File extensions read as text into the corpus.
TEXT_EXTS = {
    ".gd",
    ".tscn",
    ".tres",
    ".godot",
    ".cfg",
    ".json",
    ".import",
    ".uid",
    ".py",
    ".sh",
    ".bat",
    ".ps1",
    ".yml",
    ".yaml",
    ".toml",
    ".md",
    ".txt",
    ".html",
    ".mk",
    ".gdshader",
    ".ini",
    ".gitattributes",
    ".gutconfig",
}
TEXT_BASENAMES = {"Makefile", "makefile", ".pre-commit-config.yaml", ".gutconfig.json"}
MAX_TEXT_BYTES = 4 * 1024 * 1024

# Binary/media assets under godot/ -- ADR-0019 grandfather rule applies.
ASSET_EXTS = {
    ".png",
    ".svg",
    ".webp",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".ogg",
    ".wav",
    ".mp3",
    ".ttf",
    ".otf",
}

# Godot-side files whose text confers references (liveness edges).
GODOT_SOURCE_EXTS = {".gd", ".tscn", ".tres", ".godot", ".cfg", ".json", ".gdshader"}

# Script-side executable reference surfaces: a mention here counts as an
# invocation-ish reference. Docs mentions deliberately do NOT count
# (sync_from_pdoom_data.sh was documented everywhere and executably dead).
EXEC_SURFACE_EXTS = {".py", ".sh", ".bat", ".ps1", ".yml", ".yaml", ".toml", ".cfg", ".mk", ".ini"}
DOC_SURFACE_EXTS = {".md", ".txt", ".html"}

# Local python package roots that must resolve inside this repo.
LOCAL_PY_TOPLEVEL = {"src", "scripts", "tools", "shared", "tests"}

# Top-level dirs a backticked doc path may start with (existence-checkable).
# Derived from the repo layout; keeps `input/output`-style prose out.
DOC_PATH_TOP_DIRS = {
    "docs",
    "scripts",
    "tools",
    "godot",
    "tests",
    "shared",
    "configs",
    "public",
    "dev-blog",
    ".github",
    "assets",
    "data",
    "scenes",
    "autoload",
}

TIER_ORDER = ["CONFIRMED", "LIKELY", "UNVERIFIABLE"]

# ---------------------------------------------------------------------------
# Pure extraction helpers (unit-tested in tests/test_find_dead_code.py)
# ---------------------------------------------------------------------------

RES_TOKEN_RE = re.compile(r"res://[A-Za-z0-9_\-./]+")
UID_TOKEN_RE = re.compile(r"uid://[0-9a-z]+")
CLASS_DECL_RE = re.compile(r"^class_name\s+([A-Za-z_]\w*)", re.MULTILINE)
QUOTED_RES_RE = re.compile(r"""["'](res://[^"'\n]*)["']""")
HEADER_UID_RE = re.compile(
    r"^\[gd_(?:scene|resource)\b[^\]\n]*\buid=\"(uid://[0-9a-z]+)\"", re.MULTILINE
)
IMPORT_UID_RE = re.compile(r"^uid=\"(uid://[0-9a-z]+)\"", re.MULTILINE)
IMPORT_SOURCE_RE = re.compile(r"^source_file=\"(res://[^\"\n]+)\"", re.MULTILINE)
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
PY_IMPORT_RE = re.compile(
    r"^\s*(?:from\s+(\.*[A-Za-z_][\w.]*|\.+)\s+import|import\s+([A-Za-z_][\w.]*))",
    re.MULTILINE,
)
DISCOVER_RE = re.compile(r"unittest\s+discover\s+(?:-s\s+)?([\w./-]+)")


def extract_res_refs(text: str) -> set[str]:
    """All res:// path tokens in text, trailing punctuation stripped."""
    out = set()
    for tok in RES_TOKEN_RE.findall(text):
        tok = tok.rstrip(".,")
        if len(tok) > len("res://"):
            out.add(tok)
    return out


def extract_uid_refs(text: str) -> set[str]:
    return set(UID_TOKEN_RE.findall(text))


def extract_class_decl(text: str) -> str | None:
    m = CLASS_DECL_RE.search(text)
    return m.group(1) if m else None


def extract_dynamic_prefixes(text: str) -> set[str]:
    """res:// directory prefixes that GDScript builds paths under at runtime.

    Catches: string literals ending in "/" (the const-dir pattern used by
    event_service.gd / portrait_library.gd / office_cat.gd), format-string
    literals containing % or {, and literals immediately followed by
    concatenation (+, %, .path_join). Bare "res://" is excluded -- treating
    the whole tree as dynamic would make every finding UNVERIFIABLE.
    """
    prefixes: set[str] = set()
    for m in QUOTED_RES_RE.finditer(text):
        s = m.group(1)
        prefix = None
        if s.endswith("/"):
            prefix = s
        elif "%" in s or "{" in s:
            prefix = s.rsplit("/", 1)[0] + "/"
        else:
            rest = text[m.end() : m.end() + 24].lstrip()
            if rest[:1] in ("+", "%") or rest.startswith(".path_join"):
                # Concatenation: the last segment is a filename fragment.
                prefix = s.rsplit("/", 1)[0] + "/"
            elif "." not in s.rsplit("/", 1)[-1]:
                # No extension on the last segment and no concatenation: a
                # directory constant ("res://data/actions" pattern).
                prefix = s + "/"
        if prefix and len(prefix) > len("res://") + 1:
            prefixes.add(prefix)
    return prefixes


def extract_py_imports(text: str) -> set[str]:
    out = set()
    for m in PY_IMPORT_RE.finditer(text):
        mod = m.group(1) or m.group(2)
        if mod:
            out.add(mod)
    return out


def resolve_local_import(
    mod: str, importer: str, files: set[str], dirs: set[str]
) -> tuple[str, str]:
    """Classify an import as ('ok'|'missing'|'external', resolved_path).

    Repo-absolute (scripts.foo, src.core.x) and importer-dir-relative bare
    imports are checked against the file list; everything else is 'external'
    (stdlib or site-packages -- out of scope).
    """
    if mod.startswith("."):
        # Relative import: from .x import / from ..pkg.y import
        n = len(mod) - len(mod.lstrip("."))
        rest = mod.lstrip(".")
        here = os.path.dirname(importer)
        for _ in range(n - 1):
            here = os.path.dirname(here)
        if not rest:
            return ("ok", here + "/")  # `from . import x` -- package itself
        base = (here + "/" if here else "") + rest.replace(".", "/")
        if base + ".py" in files:
            return ("ok", base + ".py")
        if base in dirs:
            return ("ok", base + "/")
        return ("missing", base + ".py")
    parts = mod.split(".")
    if parts[0] in LOCAL_PY_TOPLEVEL:
        base = "/".join(parts)
        if base + ".py" in files:
            return ("ok", base + ".py")
        if base in dirs:
            return ("ok", base + "/")
        return ("missing", base + ".py")
    if len(parts) == 1:
        here = os.path.dirname(importer)
        cand = (here + "/" if here else "") + parts[0] + ".py"
        if cand in files:
            return ("ok", cand)
        if (here + "/" if here else "") + parts[0] in dirs:
            return ("ok", (here + "/" if here else "") + parts[0] + "/")
    return ("external", "")


def extract_doc_path_candidates(text: str) -> set[str]:
    """Repo-path-looking tokens inside backticks in a markdown doc.

    Splits backticked content on whitespace so `python scripts/foo.py --check`
    yields scripts/foo.py. Filters to tokens whose first segment is a known
    top-level dir (or res://), which keeps prose like `input/output` and
    placeholders like `path/to/file.py` out.
    """
    out: set[str] = set()
    for content in BACKTICK_RE.findall(text):
        for tok in content.split():
            tok = tok.strip(",;:()'\"<>")
            if tok.startswith("./"):
                tok = tok[2:]
            if len(tok) < 4:
                continue
            if any(ch in tok for ch in "<>{}*$|\\`=@"):
                continue
            if tok.startswith(("http://", "https://", "user://", "path/")):
                continue
            if "/" not in tok:
                # Bare filename: only worth checking for code extensions
                # (the tools/migration/README.md class -- a README listing
                # three scripts that never existed).
                if re.fullmatch(r"[A-Za-z0-9_\-.]+\.(?:py|sh|gd|bat|ps1|tscn)", tok):
                    out.add(tok)
                continue
            if tok.startswith("res://"):
                out.add(tok)
                continue
            if not re.fullmatch(r"[A-Za-z0-9_\-./]+", tok):
                continue
            first = tok.split("/", 1)[0]
            if first not in DOC_PATH_TOP_DIRS:
                continue
            segs = [s for s in tok.strip("/").split("/") if s]
            if all(re.fullmatch(r"[\d.]+", s) for s in segs):
                continue  # version-number-ish, not a path
            out.add(tok)
    return out


def make_ref_regex(needle: str) -> re.Pattern:
    """Word-ish boundary match: 'commit.py' hits 'tools/commit.py' but not
    'precommit.py' or 'commit.python'."""
    return re.compile(r"(?<!\w)" + re.escape(needle) + r"(?!\w)")


WORD_RE = re.compile(r"[A-Za-z_]\w*")
FILE_TOKEN_RE = re.compile(r"[A-Za-z0-9_.\\/-]+\.(?:py|sh|bat|ps1|json)\b", re.IGNORECASE)
MODULE_TOKEN_RE = re.compile(r"\b(?:scripts|tools|src|shared|tests)(?:\.[A-Za-z_]\w*)+\b")


def extract_words(text: str) -> set[str]:
    return set(WORD_RE.findall(text))


def extract_script_mentions(text: str) -> tuple[set[str], set[str]]:
    """(script basenames, dotted module tokens) mentioned in text.

    Token-based, so 'precommit.py' does not count as a mention of
    'commit.py' -- the token's basename must match exactly.
    """
    basenames = set()
    for tok in FILE_TOKEN_RE.findall(text):
        basenames.add(tok.replace("\\", "/").split("/")[-1].lower())
    return basenames, set(MODULE_TOKEN_RE.findall(text))


# ---------------------------------------------------------------------------
# Corpus
# ---------------------------------------------------------------------------


@dataclass
class Corpus:
    files: set[str]  # all tracked paths (posix, repo-rel)
    texts: dict[str, str]  # path -> content for text files
    root: str = "."

    _dirs: set[str] = field(default_factory=set, repr=False)

    def dirs(self) -> set[str]:
        if not self._dirs:
            for p in self.files:
                parts = p.split("/")
                for i in range(1, len(parts)):
                    self._dirs.add("/".join(parts[:i]))
        return self._dirs


def _is_text_path(path: str) -> bool:
    base = os.path.basename(path)
    if base in TEXT_BASENAMES:
        return True
    ext = os.path.splitext(path)[1].lower()
    if ext == "" and not base.startswith("."):
        return True  # extensionless: may be a shebang script (hook style)
    return ext in TEXT_EXTS


def git_ls_files(root: str) -> list[str]:
    out = subprocess.run(
        ["git", "-C", root, "ls-files", "-z"],
        capture_output=True,
        check=True,
    )
    return [p for p in out.stdout.decode("utf-8", "replace").split("\0") if p]


def load_corpus(root: str) -> Corpus:
    try:
        paths = git_ls_files(root)
    except (subprocess.CalledProcessError, FileNotFoundError):
        paths = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                d for d in dirnames if d not in {".git", ".godot", "__pycache__", ".claude"}
            ]
            for f in filenames:
                rel = os.path.relpath(os.path.join(dirpath, f), root)
                paths.append(rel.replace("\\", "/"))
    files = set(paths)
    texts: dict[str, str] = {}
    for p in paths:
        if not _is_text_path(p):
            continue
        full = os.path.join(root, p)
        try:
            if os.path.getsize(full) > MAX_TEXT_BYTES:
                continue
            with open(full, "r", encoding="utf-8", errors="replace") as fh:
                texts[p] = fh.read()
        except OSError:
            continue
    return Corpus(files=files, texts=texts, root=root)


def load_corpus_from_git(root: str, ref: str) -> Corpus:
    """Build the corpus from git objects at REF -- no checkout required.

    This is how the tool validates itself against history (e.g.
    --ref 6cb6472e^ scans the tree as it stood before the PR #1118 sweep).
    Uses one `git cat-file --batch` process for all file contents.
    """
    out = subprocess.run(
        ["git", "-C", root, "ls-tree", "-r", "--name-only", "-z", ref],
        capture_output=True,
        check=True,
    )
    paths = [p for p in out.stdout.decode("utf-8", "replace").split("\0") if p]
    files = set(paths)
    text_paths = [p for p in paths if _is_text_path(p)]
    request = "".join("%s:%s\n" % (ref, p) for p in text_paths).encode("utf-8")
    proc = subprocess.run(
        ["git", "-C", root, "cat-file", "--batch"],
        input=request,
        capture_output=True,
        check=True,
    )
    buf = proc.stdout
    texts: dict[str, str] = {}
    pos = 0
    for p in text_paths:
        nl = buf.index(b"\n", pos)
        header = buf[pos:nl].decode("utf-8", "replace")
        pos = nl + 1
        if header.endswith(" missing"):
            continue
        size = int(header.rsplit(" ", 1)[1])
        body = buf[pos : pos + size]
        pos = pos + size + 1  # trailing newline after each object
        if size <= MAX_TEXT_BYTES:
            texts[p] = body.decode("utf-8", "replace")
    return Corpus(files=files, texts=texts, root=root)


def is_retained(path: str) -> bool:
    """Policy-retained locations: top-level archives plus any archive/
    archived/ segment (scripts/archive/, docs/archive/, ...)."""
    if path.startswith(RETAINED_PREFIXES):
        return True
    return any(seg in ("archive", "archived") for seg in path.split("/")[:-1])


def is_third_party(path: str) -> bool:
    return path.startswith(THIRD_PARTY_PREFIXES)


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    path: str
    category: str  # gdscript | scene | resource | asset | data | python | shell | doc-broken-path
    tier: str  # CONFIRMED | LIKELY | UNVERIFIABLE
    section: str  # main | grandfathered | test-only | docs
    evidence: list[str]

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "category": self.category,
            "tier": self.tier,
            "section": self.section,
            "evidence": self.evidence,
        }


# ---------------------------------------------------------------------------
# Godot domain: mark-and-sweep over res:// / uid:// / class_name references
# ---------------------------------------------------------------------------


def res_to_path(token: str) -> str:
    return "godot/" + token[len("res://") :]


def path_to_res(path: str) -> str:
    assert path.startswith("godot/")
    return "res://" + path[len("godot/") :]


def build_uid_map(corpus: Corpus) -> dict[str, str]:
    """uid://xxx -> repo path, from .uid companions, .import metadata and
    .tscn/.tres headers."""
    uid_map: dict[str, str] = {}
    for p, text in corpus.texts.items():
        if not p.startswith("godot/"):
            continue
        if p.endswith(".uid"):
            uid = text.strip()
            if uid.startswith("uid://"):
                uid_map[uid] = p[: -len(".uid")]
        elif p.endswith(".import"):
            um = IMPORT_UID_RE.search(text)
            sm = IMPORT_SOURCE_RE.search(text)
            if um and sm:
                uid_map[um.group(1)] = res_to_path(sm.group(1))
        elif p.endswith((".tscn", ".tres")):
            hm = HEADER_UID_RE.search(text)
            if hm:
                uid_map[hm.group(1)] = p
    return uid_map


GODOT_PATH_TOKEN_RE = re.compile(r"godot/[A-Za-z0-9_\-./]+")


def collect_external_godot_refs(
    corpus: Corpus, flagged_scripts: set[str]
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Godot files referenced from executable surfaces OUTSIDE godot/
    (tools/capture_cinematic.py running a capture scene, CI invoking a
    probe script). Returns (refs_from_live_surfaces, refs_from_flagged
    surfaces) as {godot_path: {referencing files}}.
    """
    live_refs: dict[str, set[str]] = {}
    dead_refs: dict[str, set[str]] = {}
    for p, t in corpus.texts.items():
        if p.startswith("godot/") or is_third_party(p) or is_retained(p):
            continue
        base = os.path.basename(p)
        ext = os.path.splitext(p)[1].lower()
        if ext not in EXEC_SURFACE_EXTS and base not in TEXT_BASENAMES:
            continue
        targets: set[str] = set()
        for tok in extract_res_refs(t):
            targets.add(res_to_path(tok.rstrip("/")))
        for tok in GODOT_PATH_TOKEN_RE.findall(t):
            targets.add(tok.rstrip("./,"))
        bucket = dead_refs if p in flagged_scripts else live_refs
        for tgt in targets:
            if tgt in corpus.files:
                bucket.setdefault(tgt, set()).add(p)
    return live_refs, dead_refs


@dataclass
class GodotGraph:
    edges: dict[str, set[str]]  # source path -> referenced paths
    incoming: dict[str, set[str]]  # target path -> sources
    live: set[str]
    roots: dict[str, str]  # root path -> why
    class_decls: dict[str, str]  # class name -> declaring path
    dynamic_prefixes: dict[str, set[str]]  # res:// prefix -> declaring files


def build_godot_graph(corpus: Corpus, extra_roots: dict[str, str] | None = None) -> GodotGraph:
    godot_sources = {
        p: t
        for p, t in corpus.texts.items()
        if p.startswith("godot/")
        and not is_third_party(p)
        and os.path.splitext(p)[1] in GODOT_SOURCE_EXTS
        and not p.endswith(".import")
    }
    uid_map = build_uid_map(corpus)

    class_decls: dict[str, str] = {}
    for p, t in godot_sources.items():
        if p.endswith(".gd"):
            name = extract_class_decl(t)
            if name:
                class_decls[name] = p

    word_sets = {
        p: extract_words(t) for p, t in godot_sources.items() if p.endswith((".gd", ".tscn"))
    }

    edges: dict[str, set[str]] = {}
    for p, t in godot_sources.items():
        targets: set[str] = set()
        for tok in extract_res_refs(t):
            tp = res_to_path(tok.rstrip("/"))
            if tp in corpus.files:
                targets.add(tp)
        for uid in extract_uid_refs(t):
            if uid in uid_map:
                targets.add(uid_map[uid])
        if p in word_sets:
            for name, decl in class_decls.items():
                if decl != p and name in word_sets[p]:
                    targets.add(decl)
        targets.discard(p)
        edges[p] = targets

    incoming: dict[str, set[str]] = {}
    for src, tgts in edges.items():
        for tgt in tgts:
            incoming.setdefault(tgt, set()).add(src)

    roots: dict[str, str] = {}
    project = corpus.texts.get("godot/project.godot", "")
    if "godot/project.godot" in corpus.texts:
        roots["godot/project.godot"] = "engine entry config"
    if "godot/export_presets.cfg" in corpus.texts:
        roots["godot/export_presets.cfg"] = "export configuration"
    m = re.search(r"run/main_scene=\"(res://[^\"]+)\"", project)
    if m:
        roots[res_to_path(m.group(1))] = "project.godot run/main_scene"
    for am in re.finditer(r"^\w+=\"\*?(res://[^\"]+)\"", project, re.MULTILINE):
        p = res_to_path(am.group(1))
        if p in corpus.files:
            roots[p] = "project.godot [autoload]"
    for p in godot_sources:
        if p.startswith("godot/tests/") and p.endswith(".gd"):
            roots[p] = "GUT test tree (discovered, not referenced)"
    for cfg in ("godot/.gutconfig.json", ".gutconfig.json"):
        if cfg in corpus.texts:
            roots[cfg] = "GUT configuration"
    for p, why in (extra_roots or {}).items():
        if p in corpus.files:
            roots.setdefault(p, why)

    live: set[str] = set()
    frontier = [r for r in roots if r in corpus.files]
    while frontier:
        p = frontier.pop()
        if p in live:
            continue
        live.add(p)
        for tgt in edges.get(p, ()):
            if tgt not in live:
                frontier.append(tgt)

    dynamic_prefixes: dict[str, set[str]] = {}
    for p, t in godot_sources.items():
        if not p.endswith(".gd") or p not in live:
            continue
        if p.startswith("godot/tests/"):
            # Dir-walking tests (test_smoke_load_all.gd loads EVERY .gd
            # under res://scripts/) demand nothing in particular; letting
            # them declare dynamic prefixes would shield whole directories
            # from CONFIRMED forever. Explicit res:// references from tests
            # still count as edges above.
            continue
        for prefix in extract_dynamic_prefixes(t):
            dynamic_prefixes.setdefault(prefix, set()).add(p)

    return GodotGraph(
        edges=edges,
        incoming=incoming,
        live=live,
        roots=roots,
        class_decls=class_decls,
        dynamic_prefixes=dynamic_prefixes,
    )


def godot_category(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".gd":
        return "gdscript"
    if ext == ".tscn":
        return "scene"
    if ext in (".tres", ".gdshader"):
        return "resource"
    if ext in ASSET_EXTS:
        return "asset"
    if ext == ".json":
        return "data"
    return "asset"


def analyze_godot(
    corpus: Corpus, include_retained: bool, flagged_scripts: set[str] | None = None
) -> list[Finding]:
    flagged_scripts = flagged_scripts or set()
    ext_live, ext_dead = collect_external_godot_refs(corpus, flagged_scripts)
    extra_roots = {
        p: "referenced from executable surface outside godot/: " + ", ".join(sorted(srcs)[:3])
        for p, srcs in ext_live.items()
    }
    graph = build_godot_graph(corpus, extra_roots)
    findings: list[Finding] = []

    live_gd_words = {
        p: extract_words(t)
        for p, t in corpus.texts.items()
        if p in graph.live and p.endswith(".gd") and not is_third_party(p)
    }

    candidates = []
    for p in sorted(corpus.files):
        if not p.startswith("godot/"):
            continue
        if is_third_party(p):
            continue
        if is_retained(p) and not include_retained:
            continue
        if p in graph.live or p in graph.roots:
            continue
        if p in ALLOWLIST:
            continue
        if p.endswith((".uid", ".import")):
            continue  # metadata companions; reported with their source file
        ext = os.path.splitext(p)[1].lower()
        if ext not in GODOT_SOURCE_EXTS and ext not in ASSET_EXTS:
            continue  # README.md etc. handled by the docs pass
        candidates.append(p)

    for p in candidates:
        cat = godot_category(p)
        res = path_to_res(p)
        evidence: list[str] = []
        tier = "CONFIRMED"

        dyn_hits = [
            (prefix, decls)
            for prefix, decls in graph.dynamic_prefixes.items()
            if res.startswith(prefix)
        ]
        if dyn_hits:
            tier = "UNVERIFIABLE"
            for prefix, decls in dyn_hits:
                evidence.append(
                    "under %s, which %s uses to build paths at runtime -- "
                    "static analysis cannot see which files are demanded"
                    % (prefix, ", ".join(sorted(decls)))
                )
        else:
            dead_referencers = sorted(graph.incoming.get(p, set()) - graph.live)
            if dead_referencers:
                tier = "LIKELY"
                evidence.append(
                    "referenced only by files that are themselves unreachable: "
                    + ", ".join(dead_referencers)
                )
            if p in ext_dead:
                tier = "LIKELY"
                evidence.append(
                    "referenced only from script(s) themselves flagged dead: "
                    + ", ".join(sorted(ext_dead[p])[:3])
                )
            stem = os.path.splitext(os.path.basename(p))[0]
            if tier == "CONFIRMED" and len(stem) >= 5:
                mentions = sorted(
                    q for q, words in live_gd_words.items() if q != p and stem in words
                )
                if mentions:
                    tier = "LIKELY"
                    evidence.append(
                        "bare name '%s' appears in live script(s) %s -- a "
                        "constructed path could reach it" % (stem, ", ".join(mentions[:4]))
                    )
        if tier == "CONFIRMED":
            checked = "no res:// reference, no uid:// reference"
            if p.endswith(".gd"):
                name = extract_class_decl(corpus.texts.get(p, ""))
                if name:
                    checked += ", class_name %s used nowhere" % name
                else:
                    checked += ", no class_name declared"
            evidence.append(
                checked + "; unreachable from main scene, autoloads, tests " "and export config"
            )
        if p + ".uid" in corpus.files:
            evidence.append("companion %s.uid goes with it" % p)
        if p + ".import" in corpus.files:
            evidence.append("companion %s.import goes with it" % p)

        section = "main"
        if cat == "asset" and tier != "UNVERIFIABLE":
            section = "grandfathered"
            evidence.append(
                "ADR-0019 / Pip ruling 2026-08-03: existing packed assets are "
                "grandfathered until the demand-manifest audit. Listed for "
                "visibility, NOT as cruft."
            )
        if cat == "data" and tier == "CONFIRMED":
            tier = "LIKELY"
            evidence.append(
                "capped at LIKELY: godot/data JSON is routinely loaded via "
                "constructed paths (definition_loader pattern)"
            )
        findings.append(Finding(p, cat, tier, section, evidence))

    # Test-only survivors: live, but every incoming edge is from godot/tests.
    for p in sorted(graph.live):
        if p in graph.roots or p.startswith("godot/tests/") or is_third_party(p):
            continue
        inc = graph.incoming.get(p, set()) & graph.live
        if inc and all(q.startswith("godot/tests/") for q in inc):
            findings.append(
                Finding(
                    p,
                    godot_category(p),
                    "LIKELY",
                    "test-only",
                    [
                        "only live referencers are test files: %s -- the "
                        "candidate_card.gd pattern (PR #1118 kept it and labelled "
                        "it TEST-ONLY rather than deleting a passing test)"
                        % ", ".join(sorted(inc)[:4])
                    ],
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Python / shell domain
# ---------------------------------------------------------------------------


def analyze_scripts(corpus: Corpus, include_retained: bool) -> tuple[list[Finding], set[str]]:
    """Returns (findings, flagged script paths). The flagged set feeds the
    godot pass: a scene referenced only by a dead capture script is not
    thereby alive."""
    findings: list[Finding] = []
    dirs = corpus.dirs()

    # Retained/archived text NEVER confers executable liveness: an archived
    # copy of a script mentioning its own name must not keep the live copy
    # "referenced" (this exact case hid tools/setup_godot_migration.py from
    # the first validation run against #1118).
    exec_surfaces: dict[str, str] = {}
    doc_surfaces: dict[str, str] = {}
    archived_surfaces: dict[str, str] = {}
    for p, t in corpus.texts.items():
        if is_third_party(p):
            continue
        base = os.path.basename(p)
        ext = os.path.splitext(p)[1].lower()
        if is_retained(p):
            if ext in EXEC_SURFACE_EXTS or ext in DOC_SURFACE_EXTS:
                archived_surfaces[p] = t
            continue
        if ext in EXEC_SURFACE_EXTS or base in TEXT_BASENAMES:
            exec_surfaces[p] = t
        elif ext in DOC_SURFACE_EXTS:
            doc_surfaces[p] = t

    discovery_dirs: set[str] = set()
    for t in exec_surfaces.values():
        for m in DISCOVER_RE.finditer(t):
            discovery_dirs.add(m.group(1).strip("/"))

    candidates = []
    for p in sorted(corpus.files):
        base = os.path.basename(p)
        ext = os.path.splitext(p)[1].lower()
        is_script = ext in {".py", ".sh", ".bat", ".ps1"}
        # Extensionless shebang scripts (the tools/pre-commit-issue-check
        # class: a hook that was never in .pre-commit-config.yaml).
        if not is_script and ext == "" and not base.startswith("."):
            is_script = corpus.texts.get(p, "").startswith("#!")
        if not is_script:
            continue
        if is_third_party(p) or (is_retained(p) and not include_retained):
            continue
        if p in ALLOWLIST:
            continue
        if base == "__init__.py":
            continue  # package markers; reported below only if broken
        candidates.append(p)

    # Same-dir bare imports create real edges (tools/build_release.py
    # importing write_build_stamp), so collect them as exec references.
    import_edges: dict[str, set[str]] = {}
    for p, t in corpus.texts.items():
        if not p.endswith(".py") or is_third_party(p) or is_retained(p):
            continue
        for mod in extract_py_imports(t):
            status, target = resolve_local_import(mod, p, corpus.files, dirs)
            if status == "ok" and target != p:
                import_edges.setdefault(target.rstrip("/"), set()).add(p)

    exec_mentions = {q: extract_script_mentions(t) for q, t in exec_surfaces.items()}
    doc_mentions = {q: extract_script_mentions(t) for q, t in doc_surfaces.items()}
    archived_mentions = {q: extract_script_mentions(t) for q, t in archived_surfaces.items()}

    info: dict[str, dict] = {}
    for p in candidates:
        base = os.path.basename(p).lower()
        module = p[:-3].replace("/", ".") if p.endswith(".py") else None

        exec_refs: set[str] = set(import_edges.get(p, set()) - {p})
        doc_refs: set[str] = set()
        archived_refs: set[str] = set()
        if "." in base:
            for q, (names, mods) in exec_mentions.items():
                if q == p:
                    continue
                if base in names or (module and module in mods):
                    exec_refs.add(q)
            for q, (names, mods) in doc_mentions.items():
                if base in names or (module and module in mods):
                    doc_refs.add(q)
            for q, (names, mods) in archived_mentions.items():
                if base in names or (module and module in mods):
                    archived_refs.add(q)
        else:
            # Extensionless (shebang) scripts: token extraction keys on
            # extensions, so fall back to a boundary regex search.
            rex = make_ref_regex(os.path.basename(p))
            exec_refs |= {q for q, t in exec_surfaces.items() if q != p and rex.search(t)}
            doc_refs |= {q for q, t in doc_surfaces.items() if rex.search(t)}
            archived_refs |= {q for q, t in archived_surfaces.items() if rex.search(t)}

        under_discovery = base.startswith("test") and any(
            p.startswith(d + "/") for d in discovery_dirs
        )

        broken: list[str] = []
        if p.endswith(".py") and p in corpus.texts:
            for mod in sorted(extract_py_imports(corpus.texts[p])):
                status, target = resolve_local_import(mod, p, corpus.files, dirs)
                if status == "missing":
                    broken.append("%s (-> %s does not exist)" % (mod, target))

        info[p] = {
            "exec_refs": exec_refs,
            "doc_refs": doc_refs,
            "archived_refs": archived_refs,
            "under_discovery": under_discovery,
            "broken": broken,
        }

    # Fixpoint: a script whose every exec reference comes from scripts that
    # are themselves flagged joins the flagged set (the web_export cluster).
    flagged = {p for p, d in info.items() if not d["exec_refs"] and not d["under_discovery"]}
    changed = True
    while changed:
        changed = False
        for p, d in info.items():
            if p in flagged or d["under_discovery"]:
                continue
            if d["exec_refs"] and d["exec_refs"] <= flagged:
                flagged.add(p)
                changed = True

    for p in sorted(info):
        d = info[p]
        cat = "python" if p.endswith(".py") else "shell"
        evidence: list[str] = []
        if p in flagged:
            active_docs = d["doc_refs"]
            archived_docs = d["archived_refs"]
            if d["exec_refs"]:
                tier = "LIKELY"
                evidence.append(
                    "only executable callers are themselves flagged dead: "
                    + ", ".join(sorted(d["exec_refs"])[:5])
                )
            elif active_docs:
                tier = "LIKELY"
                evidence.append(
                    "mentioned only in docs (%s) -- nothing executes it. "
                    "The sync_from_pdoom_data.sh class: documented paths "
                    "that cannot run are the costliest kind" % ", ".join(sorted(active_docs)[:5])
                )
            else:
                tier = "CONFIRMED"
                evidence.append(
                    "no import, no workflow/Makefile/pre-commit/script "
                    "invocation, no mention in any non-archived doc"
                )
                if archived_docs:
                    evidence.append(
                        "historical mentions only, in policy-retained "
                        "archives: " + ", ".join(sorted(archived_docs)[:3])
                    )
            if d["broken"]:
                evidence.append(
                    "supporting evidence -- imports that cannot resolve: "
                    + "; ".join(d["broken"][:4])
                )
            findings.append(Finding(p, cat, tier, "main", evidence))
        elif d["broken"]:
            where = (
                "collected by unittest discovery"
                if d["under_discovery"]
                else "referenced by " + ", ".join(sorted(d["exec_refs"])[:3])
            )
            findings.append(
                Finding(
                    p,
                    cat,
                    "LIKELY",
                    "main",
                    [
                        "%s but CANNOT run: imports missing local modules: %s"
                        % (where, "; ".join(d["broken"][:4])),
                        "the #1117 pattern -- a suite CI pretends to run",
                    ],
                )
            )

    # Package markers that break their whole package: an __init__.py whose
    # imports cannot resolve makes `import package` raise unconditionally
    # (the tools/web_export pattern -- always-ImportError since the members
    # it re-exported were deleted).
    for p in sorted(corpus.texts):
        if os.path.basename(p) != "__init__.py":
            continue
        if is_third_party(p) or (is_retained(p) and not include_retained):
            continue
        broken = []
        for mod in sorted(extract_py_imports(corpus.texts[p])):
            status, target = resolve_local_import(mod, p, corpus.files, dirs)
            if status == "missing":
                broken.append("%s (-> %s does not exist)" % (mod, target))
        if broken:
            findings.append(
                Finding(
                    p,
                    "python",
                    "LIKELY",
                    "main",
                    [
                        "package marker with imports that cannot resolve: %s -- "
                        "importing this package ALWAYS raises, so every member is "
                        "unreachable via the package (tools/web_export pattern, "
                        "PR #1118)" % "; ".join(broken[:4])
                    ],
                )
            )
            flagged.add(p)

    # Orphan config JSON (configs/ and repo root): the PR #1118 sweep found
    # configs/*.json that were not even valid JSON -- their only readers
    # were dead pygame tests opening a filename that never existed.
    for p in sorted(corpus.files):
        if not p.endswith(".json"):
            continue
        if not (p.startswith("configs/") or "/" not in p):
            continue
        if is_retained(p) and not include_retained:
            continue
        if p in ALLOWLIST or os.path.basename(p) in TEXT_BASENAMES:
            continue
        base = os.path.basename(p).lower()
        refs = {q for q, (names, _mods) in exec_mentions.items() if q != p and base in names}
        docs_only = {q for q, (names, _mods) in doc_mentions.items() if base in names}
        if refs:
            continue
        evidence = []
        tier = "CONFIRMED"
        if docs_only:
            tier = "LIKELY"
            evidence.append(
                "mentioned only in docs (%s); no script or "
                "workflow reads it" % ", ".join(sorted(docs_only)[:4])
            )
        else:
            evidence.append("no script, workflow or doc references it")
        text = corpus.texts.get(p)
        if text is not None:
            try:
                json.loads(text)
            except ValueError as exc:
                evidence.append(
                    "not even valid JSON (%s) -- no JSON loader "
                    "can ever have read it successfully" % exc
                )
        findings.append(Finding(p, "config", tier, "main", evidence))
        flagged.add(p)

    return findings, flagged


# ---------------------------------------------------------------------------
# Docs domain: backticked paths that do not resolve
# ---------------------------------------------------------------------------


def analyze_docs(corpus: Corpus, include_retained: bool) -> list[Finding]:
    findings: list[Finding] = []
    dirs = corpus.dirs()
    basenames = {os.path.basename(p) for p in corpus.files}
    for p in sorted(corpus.texts):
        if not p.endswith(".md"):
            continue
        if is_third_party(p) or (is_retained(p) and not include_retained):
            continue
        text = corpus.texts[p]
        # A doc may name paths relative to the repo root OR to any of its
        # own ancestor dirs (godot/docs/*.md says `autoload/x.gd` meaning
        # godot/autoload/x.gd).
        prefixes = [""]
        parts = p.split("/")[:-1]
        for i in range(len(parts), 0, -1):
            prefixes.append("/".join(parts[:i]) + "/")
        missing: list[str] = []
        for tok in sorted(extract_doc_path_candidates(text)):
            if tok.startswith("res://"):
                targets = [res_to_path(tok.rstrip("/"))]
            elif "/" not in tok:
                # Bare filename: satisfied if the basename exists anywhere.
                if tok in basenames:
                    continue
                targets = [pre + tok for pre in prefixes]
            else:
                targets = [pre + tok.rstrip("/") for pre in prefixes]
            if any(t in corpus.files or t in dirs for t in targets):
                continue
            missing.append(tok)
        if missing:
            findings.append(
                Finding(
                    p,
                    "doc-broken-path",
                    "CONFIRMED",
                    "docs",
                    ["backticked path(s) that do not resolve: " + ", ".join(missing)],
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def changed_since(root: str, ref: str) -> set[str]:
    out = subprocess.run(
        ["git", "-C", root, "diff", "--name-only", ref + "..HEAD"],
        capture_output=True,
        check=True,
    )
    return {p for p in out.stdout.decode("utf-8", "replace").splitlines() if p}


def run_scan(
    root: str, include_retained: bool = False, since: str | None = None, ref: str | None = None
) -> dict:
    t0 = time.time()
    corpus = load_corpus_from_git(root, ref) if ref else load_corpus(root)
    script_findings, flagged_scripts = analyze_scripts(corpus, include_retained)
    findings = (
        analyze_godot(corpus, include_retained, flagged_scripts)
        + script_findings
        + analyze_docs(corpus, include_retained)
    )
    if since:
        scope = changed_since(root, since)
        findings = [f for f in findings if f.path in scope]
    elapsed = time.time() - t0
    return {
        "root": os.path.abspath(root),
        "ref": ref,
        "files_scanned": len(corpus.files),
        "text_files_read": len(corpus.texts),
        "elapsed_seconds": round(elapsed, 2),
        "since": since,
        "include_retained": include_retained,
        "allowlist": [{"path": k, "reason": v} for k, v in ALLOWLIST.items()],
        "findings": [f.to_dict() for f in findings],
    }


def print_human(report: dict) -> None:
    findings = [Finding(**f) for f in report["findings"]]
    print("find_dead_code -- report only, deletes nothing")
    print("root: %s" % report["root"])
    print(
        "scanned %d tracked files (%d read as text) in %.1fs"
        % (report["files_scanned"], report["text_files_read"], report["elapsed_seconds"])
    )
    if report.get("ref"):
        print("tree as of ref %s (read from git objects, no checkout)" % report["ref"])
    if report["since"]:
        print("scoped to files changed since %s" % report["since"])
    print()

    def emit(items: list[Finding], header: str) -> None:
        if not items:
            return
        print("=" * 72)
        print(header)
        print("=" * 72)
        by_cat: dict[str, list[Finding]] = {}
        for f in items:
            by_cat.setdefault(f.category, []).append(f)
        for cat in sorted(by_cat):
            print("\n-- %s (%d)" % (cat, len(by_cat[cat])))
            for f in by_cat[cat]:
                print("  %s" % f.path)
                for ev in f.evidence:
                    print("      . %s" % ev)
        print()

    main = [f for f in findings if f.section == "main"]
    for tier in TIER_ORDER:
        tier_items = [f for f in main if f.tier == tier]
        blurb = {
            "CONFIRMED": "no reference by any mechanism checked",
            "LIKELY": "no static/executable reference, but a mechanism "
            "exists this scanner cannot fully rule out",
            "UNVERIFIABLE": "runtime-constructed load paths could reach "
            "these -- NEVER treat as dead",
        }[tier]
        emit(tier_items, "%s -- %s" % (tier, blurb))

    emit(
        [f for f in findings if f.section == "grandfathered"],
        "GRANDFATHERED ASSETS -- packed but undemanded (ADR-0019). "
        "Awaiting the demand-manifest audit; NOT cruft.",
    )
    emit(
        [f for f in findings if f.section == "test-only"],
        "TEST-ONLY -- live, but only tests reach them. Label, don't delete.",
    )
    emit(
        [f for f in findings if f.section == "docs"],
        "DOCS WITH BROKEN PATHS -- backticked paths that do not resolve",
    )

    print("=" * 72)
    print("allowlisted as known-live (challenge these if the reason is stale):")
    for e in report["allowlist"]:
        print("  %s" % e["path"])
        print("      . %s" % e["reason"])
    print()
    counts = {}
    for f in findings:
        counts[f.section] = counts.get(f.section, 0) + 1
    print("totals: %s" % ", ".join("%s=%d" % (k, v) for k, v in sorted(counts.items())))
    print()
    print("what this scanner CANNOT see (by construction):")
    print("  . res:// paths assembled from data values or user input beyond")
    print("    the detected dynamic-dir prefixes")
    print("  . callers outside this repo (website, pdoom-data, other repos'")
    print("    workflows) -- a script may be fetched and run remotely")
    print("  . reflection (get(), call(), Callable-by-name) and editor-only")
    print("    usage")
    print("verify before deleting; every #1118 deletion cited a zero-hit")
    print("search AND a test run with an unchanged pass count.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Report-only dead-path scanner (PR #1118 as spec). "
        "Never deletes. Not a gate."
    )
    ap.add_argument(
        "--root", default=None, help="repo root to scan (default: repo containing this file)"
    )
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument(
        "--since",
        default=None,
        metavar="REF",
        help="only report findings among files changed since REF",
    )
    ap.add_argument(
        "--ref",
        default=None,
        metavar="REF",
        help="scan the tree as of REF straight from git objects "
        "(no checkout) -- e.g. --ref 6cb6472e^ replays the "
        "pre-#1118 tree for validation",
    )
    ap.add_argument(
        "--include-retained",
        action="store_true",
        help="also scan policy-retained dirs (archive/, art_source/, ...)",
    )
    args = ap.parse_args(argv)

    root = args.root
    if root is None:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report = run_scan(root, include_retained=args.include_retained, since=args.since, ref=args.ref)
    if args.json:
        json.dump(report, sys.stdout, indent=2)
        print()
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
