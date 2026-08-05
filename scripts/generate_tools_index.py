#!/usr/bin/env python3
"""Generate docs/TOOLS.md -- the index of the dev tooling in scripts/ and tools/.

Layer: GENERATE

WHY THIS EXISTS. Roughly 110 Python tools live in scripts/ and tools/ and until
now NOTHING enumerated them. The consequence is measured, not hypothetical: the
2026-08-04 dead-code sweep (PR #1118) deleted 38 files including THREE redundant
test runners that had sat there for months -- each invoked GUT with no --import
pass and no min-test floor, i.e. three dormant copies of the issue #640
silent-green disaster, invisible because no index listed the tools. You cannot
maintain a suite you cannot see.

Same anti-rot pattern as generate_dq_index.py and generate_adr_index.py: the
index is DERIVED from the tool files themselves, --check gates pre-commit, and
hand edits are therefore impossible to sustain.

The "invoked by" column is DISCOVERED by scanning .pre-commit-config.yaml,
.github/workflows/*.yml, the Makefile, tests/ and the other tools -- it is
never taken from a self-declaration. The gap between what a tool claims and
what actually calls it is the finding; it is exactly what would have surfaced
those hollow runners while they were still alive.

Declaration convention (optional; parsed tolerantly from the module docstring):
a ``Layer:`` line whose value is one of GENERATE / PROVE / OBSERVE / SWEEP
(anything after a `` -- `` on the line is a free comment), and optionally an
``Invoked by:`` line for tools with no automated caller. Undeclared tools are
REPORTED, never failed on. A tool with no declaration, no usage hint in its
docstring, and no discoverable caller lands in the UNKNOWN section -- that list
is the point of the whole exercise.

Usage:
    python scripts/generate_tools_index.py          # (re)write docs/TOOLS.md
    python scripts/generate_tools_index.py --check  # exit 1 if the index is stale
"""

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_REL = Path("docs") / "TOOLS.md"

TOOL_DIRS = ("scripts", "tools")
ARCHIVE_PREFIX = "scripts/archive/"

LAYERS = ("GENERATE", "PROVE", "OBSERVE", "SWEEP")
LAYER_BLURBS = {
    "GENERATE": "derive an artifact from source; offer --check; gate in pre-commit",
    "PROVE": "assert a property and fail loudly",
    "OBSERVE": "report; never gate",
    "SWEEP": "find rot; never delete",
}

# The emitted file must be ASCII (enforce-standards + no-emoji hooks). Keys are
# built with chr() DELIBERATELY -- literal characters would make this file
# non-ASCII, and backslash-u escapes get un-escaped back to literals by black
# on the next commit (observed 2026-08-03 on generate_adr_index.py).
ASCII_MAP = {
    chr(0x00B7): "-",  # middle dot
    chr(0x2013): "--",  # en dash
    chr(0x2014): "--",  # em dash
    chr(0x2018): "'",  # left single quote
    chr(0x2019): "'",  # right single quote
    chr(0x201C): '"',  # left double quote
    chr(0x201D): '"',  # right double quote
    chr(0x2026): "...",  # ellipsis
    chr(0x2192): "->",  # right arrow
    chr(0x00A0): " ",  # nbsp
}

LAYER_RE = re.compile(r"^\s*Layer:\s*([A-Za-z_-]+)\s*(?:--.*)?$", re.M)
INVOKED_RE = re.compile(r"^\s*Invoked by:\s*(.+?)\s*$", re.M)
IMPORT_STEM_TMPL = r"^\s*(?:import|from)\s+{stem}\b"
PURPOSE_WIDTH = 96


def to_ascii(text: str) -> str:
    for src, dst in ASCII_MAP.items():
        text = text.replace(src, dst)
    return "".join(c if ord(c) < 128 else "?" for c in text)


def iter_tool_files(root: Path) -> tuple[list[Path], list[Path]]:
    """Return (active tool files, archived tool files), each sorted by relpath."""
    active: list[Path] = []
    archived: list[Path] = []
    for d in TOOL_DIRS:
        base = root / d
        if not base.is_dir():
            continue
        for p in base.rglob("*.py"):
            if p.name == "__init__.py":
                continue
            rel = p.relative_to(root).as_posix()
            (archived if rel.startswith(ARCHIVE_PREFIX) else active).append(p)
    key = lambda p: p.relative_to(root).as_posix()  # noqa: E731
    return sorted(active, key=key), sorted(archived, key=key)


def parse_tool(path: Path, root: Path) -> dict:
    """Extract relpath, purpose, declared layer/invokers, usage hint, claims.

    Tolerant by design: a missing docstring or an unparseable file is RECORDED,
    never fatal -- the index's job is to show the state of the bay, not to gate
    tool authorship.
    """
    rel = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    doc = None
    parse_error = False
    doc_span: tuple[int, int] | None = None  # (lineno, end_lineno) of the docstring stmt
    try:
        tree = ast.parse(text)
        doc = ast.get_docstring(tree)
        if doc is not None and tree.body:
            node = tree.body[0]
            doc_span = (node.lineno, node.end_lineno or node.lineno)
    except SyntaxError:
        parse_error = True

    purpose = ""
    layer = None
    layer_raw = None
    declared_invokers = None
    usage_hint = False
    claims: set[str] = set()
    if doc:
        for line in doc.splitlines():
            if line.strip():
                purpose = to_ascii(line.strip()).replace("|", "/")
                break
        m = LAYER_RE.search(doc)
        if m:
            layer_raw = m.group(1).upper()
            layer = layer_raw if layer_raw in LAYERS else None
        m = INVOKED_RE.search(doc)
        if m:
            declared_invokers = to_ascii(m.group(1)).replace("|", "/")
        low = doc.lower()
        usage_hint = "usage:" in low or ("python " + rel) in doc or ("python -m" in doc)
        if "pre-commit" in low:
            claims.add("pre-commit")
        if re.search(r"\bCI\b", doc):
            claims.add("ci")
    if len(purpose) > PURPOSE_WIDTH:
        purpose = purpose[: PURPOSE_WIDTH - 3].rstrip() + "..."
    if parse_error:
        purpose = "(FILE DOES NOT PARSE on the baseline interpreter)"

    # For caller discovery, strip the module docstring: prose there routinely
    # NAMES sibling tools without calling them, which would fabricate callers.
    scan_text = text
    if doc_span is not None:
        lines = text.splitlines(keepends=True)
        scan_text = "".join(lines[: doc_span[0] - 1] + lines[doc_span[1] :])

    return {
        "path": path,
        "rel": rel,
        "name": path.name,
        "stem": path.stem,
        "dir": str(Path(rel).parent.as_posix()),
        "purpose": purpose,
        "layer": layer,
        "layer_raw": layer_raw,
        "declared_invokers": declared_invokers,
        "usage_hint": usage_hint,
        "claims": claims,
        "parse_error": parse_error,
        "scan_text": scan_text,
        "callers": [],
    }


def caller_sources(root: Path) -> list[tuple[str, str, bool]]:
    """Return (label, text, fuzzy) for every non-tool file scanned for invocations.

    fuzzy=True (tests) also matches on bare filename / import stem, because tests
    load tool modules via sys.path hacks and spec_from_file_location, where the
    full posix relpath never appears as one string.
    """
    sources: list[tuple[str, str, bool]] = []
    for label, relpath in (("pre-commit", ".pre-commit-config.yaml"), ("make", "Makefile")):
        p = root / relpath
        if p.exists():
            sources.append((label, p.read_text(encoding="utf-8", errors="replace"), False))
    wf = root / ".github" / "workflows"
    if wf.is_dir():
        for y in sorted(list(wf.glob("*.yml")) + list(wf.glob("*.yaml")), key=lambda p: p.name):
            sources.append(("ci:" + y.name, y.read_text(encoding="utf-8", errors="replace"), False))
    tests = root / "tests"
    if tests.is_dir():
        for t in sorted(tests.rglob("test_*.py"), key=lambda p: p.name):
            sources.append(
                ("test:" + t.name, t.read_text(encoding="utf-8", errors="replace"), True)
            )
    return sources


def discover_callers(records: list[dict], sources: list[tuple[str, str, bool]]) -> None:
    """Fill each record's "callers" by scanning sources and the OTHER tools.

    Matching is deliberately dumb (substring on the posix relpath; same-directory
    filename or import-stem) -- this is discovery, not proof. A false "referenced
    by" is cheap; a silently missed caller is the failure mode being hunted.
    """
    for rec in records:
        callers = []
        import_re = re.compile(IMPORT_STEM_TMPL.format(stem=re.escape(rec["stem"])), re.M)
        for label, text, fuzzy in sources:
            if rec["rel"] in text or (fuzzy and (rec["name"] in text or import_re.search(text))):
                callers.append(label)
        for other in records:
            if other is rec:
                continue
            text = other["scan_text"]
            hit = rec["rel"] in text
            if not hit and other["dir"] == rec["dir"]:
                hit = rec["name"] in text or bool(import_re.search(text))
            if hit:
                callers.append("tool:" + other["name"])
        rec["callers"] = callers


def is_unknown(rec: dict) -> bool:
    """UNKNOWN = nothing anywhere says how (or whether) this tool is invoked."""
    return not (
        rec["layer"]
        or rec["layer_raw"]
        or rec["declared_invokers"]
        or rec["usage_hint"]
        or rec["callers"]
    )


def invoked_cell(rec: dict) -> str:
    if rec["callers"]:
        return "; ".join(rec["callers"])
    if rec["declared_invokers"]:
        return rec["declared_invokers"] + " (declared)"
    if rec["usage_hint"]:
        return "human (docstring usage)"
    return "NONE FOUND"


def claim_gaps(records: list[dict]) -> list[tuple[str, str]]:
    """Tools whose docstring invokes the words pre-commit/CI without a matching caller.

    This is the hollow-runner detector: a tool that SAYS it is a gate while
    nothing wires it into one is exactly the #640-successor shape that PR #1118
    deleted three of.
    """
    gaps = []
    for rec in records:
        has_pc = any(c == "pre-commit" for c in rec["callers"])
        has_ci = any(c.startswith("ci:") for c in rec["callers"])
        if "pre-commit" in rec["claims"] and not has_pc:
            gaps.append((rec["rel"], "docstring mentions pre-commit; no pre-commit hook calls it"))
        if "ci" in rec["claims"] and not has_ci:
            gaps.append((rec["rel"], "docstring mentions CI; no workflow calls it"))
    return gaps


def collect(root: Path) -> tuple[list[dict], list[Path]]:
    active, archived = iter_tool_files(root)
    records = [parse_tool(p, root) for p in active]
    discover_callers(records, caller_sources(root))
    return records, archived


def render(root: Path) -> str:
    records, archived = collect(root)
    html_tools = sorted(p.relative_to(root).as_posix() for p in (root / "tools").rglob("*.html"))

    lines = [
        "# Dev tools index (GENERATED -- do not hand-edit)",
        "",
        "> Derived from the tool files in `scripts/` and `tools/` by",
        "> `scripts/generate_tools_index.py`. Regenerate with:",
        "> `python scripts/generate_tools_index.py`. A pre-commit check fails",
        "> commits that change the tooling without regenerating this file.",
        ">",
        "> Why generated: PR #1118 deleted three redundant GUT runners that had",
        "> quietly carried the issue #640 silent-green bug for months -- invisible",
        "> because nothing enumerated the tools. An index that is derived cannot",
        "> rot the way the hand-kept `decisions/README.md` did.",
        "",
        "The `Invoked by` column is DISCOVERED (by scanning `.pre-commit-config.yaml`,",
        "`.github/workflows/*.yml`, `Makefile`, `tests/` and the other tools), never",
        "copied from a tool's self-description. `tool:x.py` means another tool",
        "references it; `test:x.py` means a Python test exercises it.",
        "",
        "## Layers",
        "",
        "Declared with a `Layer:` line in a tool's module docstring; `--` = undeclared.",
        "",
    ]
    for name in LAYERS:
        lines.append("- **%s** -- %s" % (name, LAYER_BLURBS[name]))
    lines.append("")

    by_dir: dict[str, list[dict]] = {}
    for rec in records:
        by_dir.setdefault(rec["dir"], []).append(rec)
    for d in sorted(by_dir):
        lines += [
            "## `%s/`" % d,
            "",
            "| Tool | Layer | Purpose | Invoked by |",
            "|---|---|---|---|",
        ]
        for rec in by_dir[d]:
            layer = rec["layer"] or (
                "%s (unrecognised)" % rec["layer_raw"] if rec["layer_raw"] else "--"
            )
            lines.append(
                "| %s | %s | %s | %s |"
                % (rec["name"], layer, rec["purpose"] or "(no docstring)", invoked_cell(rec))
            )
        lines.append("")

    unknown = [rec for rec in records if is_unknown(rec)]
    lines += [
        "## UNKNOWN -- no declaration, no usage hint, no discoverable caller",
        "",
    ]
    if unknown:
        lines.append(
            "%d tool(s) that nothing declares, documents, or calls. Each one is either"
            % len(unknown)
        )
        lines.append(
            "a rot candidate or an undocumented dependency -- find out which "
            "(`tools/find_dead_code.py` lane)."
        )
        lines.append("")
        for rec in unknown:
            note = " (does not parse)" if rec["parse_error"] else ""
            lines.append("- `%s`%s" % (rec["rel"], note))
    else:
        lines.append("Empty -- checked every tool for a `Layer:`/`Invoked by:` declaration, a")
        lines.append("docstring usage hint, and a caller in pre-commit / workflows / Makefile /")
        lines.append("the other tools. An empty list here is a claim, not an absence of looking.")
    lines.append("")

    gaps = claim_gaps(records)
    lines += ["## Claim-vs-reality gaps", ""]
    if gaps:
        lines.append("The tool's own docstring names an automated caller category that the scan")
        lines.append("could not corroborate. Some are prose false-positives (a docstring merely")
        lines.append("DISCUSSING CI); the rest are the hollow-runner shape -- read them.")
        lines.append("")
        for rel, msg in gaps:
            lines.append("- `%s` -- %s" % (rel, msg))
    else:
        lines.append("None: every docstring mention of pre-commit/CI matched a real caller.")
    lines.append("")

    if archived:
        lines += [
            "## Archived (`scripts/archive/` -- indexed by name only, excluded from caller scan)",
            "",
        ]
        for p in archived:
            lines.append("- `%s`" % p.relative_to(root).as_posix())
        lines.append("")

    if html_tools:
        lines += [
            "## Not indexed: HTML tools",
            "",
            "%d `.html` tool(s) under `tools/` (browser-opened, no docstring to parse): %s."
            % (len(html_tools), ", ".join("`%s`" % h for h in html_tools)),
            "",
        ]

    by_layer: dict[str, int] = {}
    for rec in records:
        key = rec["layer"] or "undeclared"
        by_layer[key] = by_layer.get(key, 0) + 1
    tally = ", ".join("%d %s" % (n, k) for k, n in sorted(by_layer.items()))
    lines.append(
        "Total: %d active tools (%s); %d in UNKNOWN; %d archived."
        % (len(records), tally, len(unknown), len(archived))
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    out = ROOT / OUT_REL
    content = render(ROOT)
    if "--check" in sys.argv:
        if not out.exists() or out.read_text(encoding="utf-8") != content:
            print("docs/TOOLS.md is stale. Run: python scripts/generate_tools_index.py")
            return 1
        return 0
    out.write_text(content, encoding="utf-8", newline="\n")
    print("Wrote %s" % out.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
