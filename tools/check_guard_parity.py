#!/usr/bin/env python3
"""Census every pre-commit hook against the workflows, and fail on a guard CI cannot see.

Layer: PROVE

WHY THIS EXISTS (issue #1265, ruled by Pip 2026-08-20)
-----------------------------------------------------
A pre-commit hook is per-clone and bypassable. It does not exist on a machine that
never ran `pre-commit install`, and `git commit --no-verify` steps over all of them.
So a guard wired ONLY to pre-commit is a guard the project cannot rely on, and --
worse -- one it believes it has.

The worked example that opened the issue: `balance-key-census` ran in
.pre-commit-config.yaml and `grep -rn check_balance_keys .github/workflows/` returned
nothing, so the only gate pointed at the balance surface in either direction could be
skipped by anyone, silently, forever.

This file is the census, run as a command instead of written as a table, because a
hand-maintained table of which guards run where is exactly the artefact this repo keeps
watching rot (see the stale docs/game-design/decisions/README.md).

THE THREE THINGS IT GETS RIGHT THAT A GREP DOES NOT
---------------------------------------------------
1. `pre-commit run --all-files` in a workflow covers EVERY hook at once. A per-tool
   grep would report fifteen gaps that are not gaps. Detected explicitly.
2. A workflow may invoke the tool under its bare basename rather than its repo path.
   Both are searched.
3. **A tool can run in CI in a DIFFERENT MODE.** `scripts/generate_release_metadata.py`
   appears in enhanced-release.yml -- as `--version`, which REGENERATES the feed. The
   pre-commit hook runs `--check`, which GATES it. Grepping the filename says "covered";
   the gate is not covered at all. So the gating flag is matched too, and a tool present
   under a different flag is reported as PARTIAL, not as PASS.

EXIT CODES -- THREE, NOT TWO
    0  measured pass: every gated hook has a CI presence, or a declared waiver.
    1  measured failure: a hook runs in pre-commit and nowhere else, or a waiver is
       stale (the hook it excuses now DOES run in CI).
    2  COULD NOT MEASURE: no .pre-commit-config.yaml, or no .github/workflows/.
       Not a pass and not a finding.

USAGE
    python tools/check_guard_parity.py               # print the census table
    python tools/check_guard_parity.py --check       # gate: exit 1 on an unwaived gap
    python tools/check_guard_parity.py --markdown    # census as a markdown table
    python tools/check_guard_parity.py --self-test   # prove it returns BOTH answers

RULING: 2026-08-24 -- a guard wired only to pre-commit is not installed; every local hook must either run in a workflow or carry a declared waiver naming what covers it instead -- flavour: guard-doctrine -- mechanism: tools/check_guard_parity.py --check in .github/workflows/guards.yml
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover -- pyyaml is in requirements.txt
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / ".pre-commit-config.yaml"
WORKFLOW_DIR = ROOT / ".github" / "workflows"

SCRIPT_RE = re.compile(r"((?:scripts|tools)/[\w/]+\.py)")
FLAG_RE = re.compile(r"(--[\w-]+)")

# Hooks that legitimately have no direct workflow invocation. Each entry MUST say what
# covers the guard instead, because an unexplained waiver is how a gap gets renamed
# rather than closed. A waiver whose hook LATER gains a CI presence is reported as
# stale and fails --check: the list only shrinks.
WAIVERS = {
    "class-cache-check": (
        "CI is structurally blind to the bug. A stale godot/.godot class cache only "
        "exists in a long-lived working copy; CI clones fresh and always builds a "
        "correct one, so the guard would be watching the one place that is never "
        "wrong. It is also a post-merge/post-checkout hook, not a pre-commit one. "
        "What CI proves instead is that the DETECTOR still returns both answers: "
        "quality-checks.yml runs `python -m unittest tests.test_check_class_cache` "
        "blocking. See CLAUDE.md 'STALE cache is the worse half of that trap'."
    ),
    "style-guide-reminder": (
        "Not a gate. scripts/check_style_guide.py reads `git diff --cached`, which is "
        "empty on a CI checkout, and without --strict it only warns -- so in CI it "
        "could report exactly one answer, forever. Wiring it as-is would manufacture "
        "a green light rather than a check. Making it gateable is a separate change."
    ),
}

# SCOPE OF --check: hooks from `repo: local` that invoke a project script. Third-party
# hooks are censused (they appear in the table as "(no project script)") but not gated,
# and that is a deliberate, measured deferral rather than an oversight. The formatter and
# whitespace family (black / isort / ruff / trailing-whitespace / ...) only ever runs on
# the files a commit touches, so the untouched tree has drifted: measured 2026-08-24 over
# 236 Python files with the versions pinned in .pre-commit-config.yaml, black would
# reformat 83, isort reports 78, ruff reports 178 errors. A whole-tree CI gate would
# therefore arrive RED, and a gate that is red on arrival gets disabled inside a week
# (the same reasoning the action-taxonomy hook records for --check-stale). The wireable
# form is changed-files-only, which is a separate change -- tracked in issue #1297 with
# the commands that produced the numbers above.


def load_hooks():
    """[(repo, hook_id, entry, stages)] in config order."""
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    out = []
    for repo in cfg.get("repos", []):
        for hook in repo.get("hooks", []):
            out.append(
                (
                    repo.get("repo", ""),
                    hook.get("id", ""),
                    hook.get("entry", ""),
                    hook.get("stages"),
                )
            )
    return out


def load_workflows(directory: Path):
    """{filename: text} for every workflow file."""
    files = sorted(directory.glob("*.yml")) + sorted(directory.glob("*.yaml"))
    return {f.name: f.read_text(encoding="utf-8", errors="replace") for f in files}


def blanket_precommit_runs(workflows) -> list[str]:
    """Workflows that run the whole hook set at once, covering every hook."""
    return sorted(
        name
        for name, text in workflows.items()
        if re.search(r"pre-commit\s+run\s+(--all-files|-a\b)", text)
    )


def tool_of(entry: str) -> str | None:
    """The repo-relative script an entry invokes, or None for inline/upstream hooks."""
    m = SCRIPT_RE.search(entry or "")
    return m.group(1) if m else None


def gating_flag(entry: str) -> str | None:
    """The flag that turns the tool into a gate, e.g. --check / --check-stale.

    A generator run WITHOUT it rewrites the artefact; run WITH it, it fails on drift.
    Same filename, opposite meaning -- which is why matching the filename alone
    reports coverage that is not there.
    """
    flags = [f for f in FLAG_RE.findall(entry or "") if f not in ("--incremental",)]
    for f in flags:
        if f.startswith("--check") or f in ("--offline",):
            return f if f.startswith("--check") else None
    return None


def presence(tool: str, flag: str | None, workflows):
    """(verdict, [workflow names]) for one tool.

    verdict is one of: "yes" (invoked, and with the gating flag if there is one),
    "partial" (invoked, but never with the gating flag), "no".
    """
    basename = tool.rsplit("/", 1)[-1]
    hits, flag_hits = [], []
    for name, text in workflows.items():
        lines = [ln for ln in text.splitlines() if tool in ln or basename in ln]
        # A mention inside a comment is documentation, not an invocation.
        lines = [ln for ln in lines if not ln.lstrip().startswith("#")]
        if not lines:
            continue
        hits.append(name)
        if flag is None or any(flag in ln for ln in lines):
            flag_hits.append(name)
    if not hits:
        return "no", []
    if flag_hits:
        return "yes", sorted(flag_hits)
    return "partial", sorted(hits)


def census(workflows):
    """[dict] one row per hook, in config order."""
    blanket = blanket_precommit_runs(workflows)
    rows = []
    for repo, hook_id, entry, stages in load_hooks():
        tool = tool_of(entry)
        flag = gating_flag(entry) if tool else None
        if blanket:
            verdict, where = "yes", blanket
        elif tool:
            verdict, where = presence(tool, flag, workflows)
        else:
            verdict, where = "n/a", []
        rows.append(
            {
                "hook": hook_id,
                "local": repo == "local",
                "tool": tool or "(no project script)",
                "flag": flag or "",
                "verdict": verdict,
                "where": where,
                "stages": stages,
                "waiver": WAIVERS.get(hook_id),
            }
        )
    return rows


def gaps(rows):
    """Rows that run in pre-commit and nowhere else, with no waiver."""
    return [
        r
        for r in rows
        if r["local"]
        and r["tool"] != "(no project script)"
        and r["verdict"] == "no"
        and not r["waiver"]
    ]


def stale_waivers(rows):
    return [r for r in rows if r["waiver"] and r["verdict"] in ("yes", "partial")]


def partials(rows):
    """Rows whose tool IS invoked by a workflow, but never with the flag that gates.

    A waived hook is excluded for the same reason it is excluded from gaps(): the
    waiver is the declaration that something else covers it.
    """
    return [r for r in rows if r["local"] and r["verdict"] == "partial" and not r["waiver"]]


def exit_code(rows) -> int:
    """The --check verdict for a census.

    Pure and separate from main() so the self-test can prove each failing
    direction fires, rather than proving only that a passing tree passes. A
    gate whose failing direction has never been exercised is a counter.
    """
    return 1 if (gaps(rows) or stale_waivers(rows) or partials(rows)) else 0


def render(rows, markdown: bool) -> None:
    sym = {"yes": "YES", "partial": "PARTIAL", "no": "NO", "n/a": "-"}
    if markdown:
        print("| hook id | tool invoked | gating flag | in CI? | which workflow |")
        print("| --- | --- | --- | --- | --- |")
        for r in rows:
            where = ", ".join(r["where"]) if r["where"] else ""
            if r["waiver"] and r["verdict"] == "no":
                where = "WAIVED"
            print(
                "| `%s` | `%s` | `%s` | %s | %s |"
                % (r["hook"], r["tool"], r["flag"], sym[r["verdict"]], where)
            )
        return
    print("%-30s %-42s %-9s %s" % ("HOOK", "TOOL", "IN CI?", "WHERE"))
    print("-" * 110)
    for r in rows:
        where = ", ".join(r["where"]) if r["where"] else ""
        if r["waiver"] and r["verdict"] == "no":
            where = "WAIVED -- see WAIVERS in this file"
        print("%-30s %-42s %-9s %s" % (r["hook"], r["tool"], sym[r["verdict"]], where))


# --- self-test -------------------------------------------------------------


def _fake_workflows():
    return {
        "wired.yml": "jobs:\n  a:\n    steps:\n"
        "      - run: python tools/check_wired.py --check\n",
        "wrongmode.yml": "jobs:\n  b:\n    steps:\n"
        "      - run: python scripts/gen_thing.py --version v1\n",
        "commented.yml": "jobs:\n  c:\n    steps:\n"
        "      # python tools/check_lonely.py runs in pre-commit only\n"
        "      - run: echo hi\n",
    }


def self_test() -> int:
    """Prove the parity check returns BOTH answers, including the three ways a naive
    grep gets it wrong."""
    ok = True

    def check(label, cond, detail=""):
        nonlocal ok
        if cond:
            print("  [ok] %s" % label)
        else:
            ok = False
            print("SELF-TEST FAIL: %s %s" % (label, detail))

    wf = _fake_workflows()

    v, where = presence("tools/check_wired.py", "--check", wf)
    check("a tool invoked with its gating flag reads YES", v == "yes" and where == ["wired.yml"])

    v, _ = presence("tools/check_lonely.py", None, wf)
    check("a tool named ONLY in a comment reads NO (a mention is not an invocation)", v == "no")

    # The subtle one. Grepping the filename says "covered"; the GATE is not covered.
    v, where = presence("scripts/gen_thing.py", "--check", wf)
    check(
        "a generator run in CI without its --check flag reads PARTIAL, not YES",
        v == "partial" and where == ["wrongmode.yml"],
        "%s %s" % (v, where),
    )

    v, _ = presence("tools/check_absent.py", "--check", wf)
    check("a tool no workflow mentions reads NO", v == "no")

    # A blanket `pre-commit run --all-files` covers everything at once.
    blanket = blanket_precommit_runs({"all.yml": "      - run: pre-commit run --all-files\n"})
    check(
        "a blanket `pre-commit run --all-files` is detected as covering every hook",
        blanket == ["all.yml"],
    )
    check("and a workflow without it is not", blanket_precommit_runs(wf) == [])

    check(
        "the gating flag is read out of the hook entry",
        gating_flag("python scripts/generate_dq_index.py --check") == "--check"
        and gating_flag("python scripts/generate_action_taxonomy.py --check-stale")
        == "--check-stale"
        and gating_flag("python tools/check_scene_nav.py") is None,
    )
    check(
        "the tool path is read out of the hook entry, and inline hooks yield None",
        tool_of("python tools/assets/check_credentials.py") == "tools/assets/check_credentials.py"
        and tool_of('python -c "import sys; sys.exit(0)"') is None,
    )

    # Real history: the gap the issue was opened about, and the gap it must now deny.
    if not CONFIG.is_file() or not WORKFLOW_DIR.is_dir():
        ok = False
        print("SELF-TEST FAIL: cannot reach the real config/workflows")
    else:
        rows = census(load_workflows(WORKFLOW_DIR))
        by_id = {r["hook"]: r for r in rows}
        check(
            "the real config parses to >= 30 hooks",
            len(rows) >= 30,
            str(len(rows)),
        )
        bkc = by_id.get("balance-key-census")
        check(
            "balance-key-census -- the worked example from #1265 -- now reads YES",
            bkc is not None and bkc["verdict"] == "yes",
            repr(bkc and bkc["verdict"]),
        )
        check(
            "every waiver names a hook that really exists in the config",
            all(w in by_id for w in WAIVERS),
            repr([w for w in WAIVERS if w not in by_id]),
        )
        ric = by_id.get("release-index-check")
        check(
            "release-index-check -- the PARTIAL from #1297 -- now reads YES",
            ric is not None and ric["verdict"] == "yes",
            repr(ric and ric["verdict"]),
        )
        check(
            "and the real tree therefore exits 0",
            exit_code(rows) == 0,
        )

    # THE NEWLY ARMED DIRECTION (2026-08-29). PARTIAL fails --check as of #1297
    # section 2, and a rule armed while nothing violates it is a rule nobody has
    # watched fail. These synthetic rows are the proof, and they are built by hand
    # rather than found in the tree precisely because the tree is clean.
    def _row(verdict, waiver=None):
        return {
            "hook": "synthetic",
            "tool": "scripts/gen_thing.py",
            "flag": "--check",
            "local": True,
            "verdict": verdict,
            "where": ["wrongmode.yml"],
            "waiver": waiver,
        }

    check(
        "a PARTIAL row FAILS --check (this is the direction armed for #1297)",
        exit_code([_row("partial")]) == 1,
    )
    # A waived PARTIAL still fails, but through the OTHER rule, and that is the
    # right answer rather than an accident: stale_waivers() already treats a
    # waiver on a hook CI now invokes as stale, because the waiver's whole claim
    # is that CI cannot see the tool. partials() excludes waived rows only so the
    # same row is not reported twice under two headings.
    check(
        "a WAIVED partial still fails -- as a STALE WAIVER, not as a partial",
        exit_code([_row("partial", waiver="covered elsewhere")]) == 1
        and not partials([_row("partial", waiver="covered elsewhere")])
        and stale_waivers([_row("partial", waiver="covered elsewhere")]),
    )
    check(
        "a YES row passes, so the rule is not simply always-fail",
        exit_code([_row("yes")]) == 0,
    )

    print("SELF-TEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--check", action="store_true", help="gate: exit 1 on an unwaived gap")
    ap.add_argument("--markdown", action="store_true", help="render the census as markdown")
    ap.add_argument("--self-test", action="store_true", help="prove BOTH answers")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    if yaml is None:
        print("[guard-parity] CANNOT RUN: pyyaml not installed", file=sys.stderr)
        return 2
    if not CONFIG.is_file():
        print("[guard-parity] CANNOT RUN: %s missing" % CONFIG, file=sys.stderr)
        return 2
    if not WORKFLOW_DIR.is_dir():
        print("[guard-parity] CANNOT RUN: %s missing" % WORKFLOW_DIR, file=sys.stderr)
        return 2

    workflows = load_workflows(WORKFLOW_DIR)
    if not workflows:
        print("[guard-parity] CANNOT RUN: no workflow files found", file=sys.stderr)
        return 2

    rows = census(workflows)
    render(rows, args.markdown)

    # PARTIAL NOW FAILS --check (armed 2026-08-29, issue #1297 section 2).
    #
    # It used to report and not fail, on purpose: the one live instance,
    # release-index-check, was red on main, and a gate that is red on arrival gets
    # disabled inside a week. That deferral had a stated condition -- "promote
    # PARTIAL to a failure once the feed is regenerated" -- and this is that.
    # The feed was regenerated and release-index-check is wired into guards.yml
    # with `--check`, the flag that gates, so it now reads YES and this list is
    # empty at the moment of arming.
    #
    # Arming it with nothing to catch is the point. PARTIAL is the verdict a
    # filename grep gets wrong: the tool IS in a workflow, under a flag that does
    # not gate. That reads as covered to every cheaper instrument, so the next
    # instance would be invisible in exactly the way this one was for months.
    # A rule armed while the list is empty cannot arrive red.
    missing = gaps(rows)
    stale = stale_waivers(rows)
    partial = partials(rows)
    waived = [r for r in rows if r["waiver"] and r["verdict"] == "no"]

    print()
    print(
        "[guard-parity] %d hook(s); %d gated in CI, %d waived, %d partial, %d with no CI presence."
        % (
            len(rows),
            sum(1 for r in rows if r["verdict"] == "yes"),
            len(waived),
            len(partial),
            len(missing),
        )
    )
    if partial:
        print()
        print("PARTIAL -- the tool runs in CI but never with the flag that makes it a gate.")
        print("This is the shape a filename grep reports as covered:")
        for r in partial:
            print(
                "  %-28s %s %s  (CI: %s)" % (r["hook"], r["tool"], r["flag"], ", ".join(r["where"]))
            )

    if not args.check:
        return 0

    rc = 0
    if missing:
        print()
        print("[guard-parity] FAIL: %d guard(s) run in pre-commit and nowhere else." % len(missing))
        print("  pre-commit is per-clone and --no-verify steps over it, so these are not")
        print("  installed on any machine that has not opted in. Wire them into a workflow")
        print("  (.github/workflows/guards.yml), or add a WAIVER saying what covers them.")
        for r in missing:
            print("    %-28s %s" % (r["hook"], r["tool"]))
        rc = 1
    if stale:
        print()
        print(
            "[guard-parity] FAIL: %d stale waiver(s) -- these hooks DO run in CI now." % len(stale)
        )
        print("  Delete the waiver. The list only shrinks.")
        for r in stale:
            print("    %-28s (CI: %s)" % (r["hook"], ", ".join(r["where"])))
        rc = 1
    if partial:
        print()
        print("[guard-parity] FAIL: %d guard(s) run in CI but never as a gate." % len(partial))
        print("  The tool is invoked by a workflow under a flag that does something else")
        print("  -- generating, printing, reporting -- so a filename grep says covered")
        print("  while nothing can fail. Invoke it with the gating flag in a workflow,")
        print("  or add a WAIVER saying what covers the gate instead.")
        for r in partial:
            print(
                "    %-28s %s %s  (CI: %s)"
                % (r["hook"], r["tool"], r["flag"], ", ".join(r["where"]))
            )
        rc = 1
    if rc == 0:
        print()
        print("[guard-parity] OK: every gated hook runs in CI with the flag that gates it.")
    # Returned from the same pure function the self-test exercises, so what this
    # command reports and what the self-test proves cannot drift apart.
    return exit_code(rows)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
