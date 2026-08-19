#!/usr/bin/env python3
"""Diff two reviewers' verdicts, honestly.

Layer: OBSERVE

WHY THIS EXISTS
---------------
On 2026-08-19 a second reviewer (Wanasai) judged art for the first time. Two
palates over the same assets is the only way to find out which calls are TASTE
and which are CRAFT -- a single reviewer cannot tell the difference from the
inside, because everything they believe looks like craft to them.

THE TRAP THIS TOOL EXISTS TO AVOID
-----------------------------------
The naive comparison is worthless and looks authoritative. Measured on the first
session: raw keep rate 94% (her) vs 79% (his), 73% "agreement" over 1,646 shared
assets. Every one of those numbers is an artefact.

1,694 of her 1,888 assets carry ONE batch note applied in a SINGLE action. Her
1,888 "judgements" are ~126 actions, one of which covered 1,694 assets. Counting
batch members as independent opinions inflates whoever swept hardest and turns a
sweep into a mandate.

So this tool separates DELIBERATE calls from BULK ones before comparing anything,
and reports both numbers with the bulk share visible. A comparison that hides its
denominator is worse than no comparison.

WHAT COUNTS AS BULK
-------------------
An action -- a cluster of log events within `--burst` seconds -- larger than
`--bulk-min` assets. Detected from the LOG, not guessed from the state, because
the log is the only place the grouping survives. Assets touched only by bulk
actions are excluded from the taste comparison and counted separately.

Usage:
  python tools/art_review/compare_reviewers.py                    # pip vs wanasai
  python tools/art_review/compare_reviewers.py --a pip --b wanasai
  python tools/art_review/compare_reviewers.py --md report.md
  python tools/art_review/compare_reviewers.py --json diff.json
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_REVIEWER = "pip"


def paths_for(name: str) -> tuple[pathlib.Path, pathlib.Path]:
    if name == DEFAULT_REVIEWER:
        return HERE / "review_state.json", HERE / "review_log.jsonl"
    return HERE / f"review_state.{name}.json", HERE / f"review_log.{name}.jsonl"


def load(name: str) -> tuple[dict, list]:
    state_p, log_p = paths_for(name)
    if not state_p.exists():
        sys.exit(f"no state for reviewer {name!r} at {state_p}")
    state = json.loads(state_p.read_text(encoding="utf-8"))
    log = []
    if log_p.exists():
        for line in log_p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                log.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return state, log


def bulk_assets(log: list, burst: float, bulk_min: int) -> tuple[set, list]:
    """Assets touched only inside LARGE actions, plus every action's size.

    An action is a run of events within `burst` seconds of each other. This is the
    same clustering used for throughput reporting, so the two analyses cannot
    disagree about what a decision was.
    """
    rows = []
    for e in log:
        ts = e.get("ts")
        if not ts:
            continue
        rows.append((dt.datetime.fromisoformat(ts).replace(tzinfo=None), e))
    rows.sort(key=lambda r: r[0])
    if not rows:
        return set(), []
    clusters = [[rows[0]]]
    for prev, cur in zip(rows, rows[1:]):
        if (cur[0] - prev[0]).total_seconds() <= burst:
            clusters[-1].append(cur)
        else:
            clusters.append([cur])
    sizes = [len(c) for c in clusters]
    in_bulk, in_small = set(), set()
    for c in clusters:
        target = in_bulk if len(c) >= bulk_min else in_small
        for _t, e in c:
            target.add(e.get("asset"))
    # an asset also touched deliberately is NOT bulk -- the considered call wins
    return in_bulk - in_small, sizes


def verdict(state: dict, key: str):
    return (state.get(key) or {}).get("verdict")


def note(state: dict, key: str) -> str:
    return ((state.get(key) or {}).get("note") or "").strip()


def compare(a_name: str, b_name: str, burst: float, bulk_min: int) -> dict:
    a_state, a_log = load(a_name)
    b_state, b_log = load(b_name)
    a_bulk, a_sizes = bulk_assets(a_log, burst, bulk_min)
    b_bulk, b_sizes = bulk_assets(b_log, burst, bulk_min)

    shared = sorted(set(a_state) & set(b_state))
    deliberate = [k for k in shared if k not in a_bulk and k not in b_bulk]

    def tally(state, keys):
        return dict(collections.Counter(verdict(state, k) for k in keys))

    def keep_rate(state, keys):
        if not keys:
            return None
        n = sum(1 for k in keys if verdict(state, k) == "keep")
        return round(n / len(keys) * 100)

    matrix = collections.Counter((verdict(a_state, k), verdict(b_state, k)) for k in deliberate)
    agree = sum(n for (x, y), n in matrix.items() if x == y)

    def flips(x, y):
        return [
            {
                "asset": k,
                "family": k.split(":")[1] if k.count(":") > 1 else "",
                "a_note": note(a_state, k),
                "b_note": note(b_state, k),
            }
            for k in deliberate
            if verdict(a_state, k) == x and verdict(b_state, k) == y
        ]

    return {
        "a": a_name,
        "b": b_name,
        "params": {"burst_seconds": burst, "bulk_min_assets": bulk_min},
        "counts": {
            "a_total": len(a_state),
            "b_total": len(b_state),
            "shared": len(shared),
            "a_bulk_assets": len(a_bulk),
            "b_bulk_assets": len(b_bulk),
            "deliberate_shared": len(deliberate),
            "a_actions": len(a_sizes),
            "b_actions": len(b_sizes),
            "a_largest_action": max(a_sizes) if a_sizes else 0,
            "b_largest_action": max(b_sizes) if b_sizes else 0,
        },
        "keep_rate_all": {a_name: keep_rate(a_state, shared), b_name: keep_rate(b_state, shared)},
        "keep_rate_deliberate": {
            a_name: keep_rate(a_state, deliberate),
            b_name: keep_rate(b_state, deliberate),
        },
        "verdicts_deliberate": {
            a_name: tally(a_state, deliberate),
            b_name: tally(b_state, deliberate),
        },
        "agreement_deliberate": {
            "agreed": agree,
            "of": len(deliberate),
            "pct": round(agree / len(deliberate) * 100) if deliberate else None,
        },
        "matrix": [
            {"a": x, "b": y, "n": n} for (x, y), n in sorted(matrix.items(), key=lambda kv: -kv[1])
        ],
        "b_rejects_a_keep": flips("keep", "discard"),
        "b_keeps_a_discard": flips("discard", "keep"),
    }


def render_md(d: dict) -> str:
    a, b = d["a"], d["b"]
    c = d["counts"]
    out = [
        f"# Reviewer diff -- {a} vs {b}",
        "",
        "> GENERATED by `tools/art_review/compare_reviewers.py`. Bulk actions are",
        "> separated from deliberate ones BEFORE any comparison; see the tool's",
        "> docstring for why the naive numbers are worthless.",
        "",
        "## Denominators first",
        "",
        "| | " + a + " | " + b + " |",
        "|---|---:|---:|",
        f"| assets judged | {c['a_total']} | {c['b_total']} |",
        f"| distinct actions | {c['a_actions']} | {c['b_actions']} |",
        f"| largest single action | {c['a_largest_action']} | {c['b_largest_action']} |",
        f"| assets touched ONLY in bulk | {c['a_bulk_assets']} | {c['b_bulk_assets']} |",
        "",
        f"Shared assets: **{c['shared']}**. After removing bulk-only ones, "
        f"**{c['deliberate_shared']}** carry a deliberate call from both.",
        "",
        "## Keep rate",
        "",
        "| basis | " + a + " | " + b + " |",
        "|---|---:|---:|",
        f"| all shared (MISLEADING) | {d['keep_rate_all'][a]}% | {d['keep_rate_all'][b]}% |",
        f"| deliberate only | **{d['keep_rate_deliberate'][a]}%** | "
        f"**{d['keep_rate_deliberate'][b]}%** |",
        "",
    ]
    ag = d["agreement_deliberate"]
    out += [
        "## Agreement, on deliberate calls only",
        "",
        f"**{ag['agreed']} of {ag['of']} = {ag['pct']}%**",
        "",
        f"| {a} | {b} | n |",
        "|---|---|---:|",
    ]
    for row in d["matrix"]:
        mark = " (agree)" if row["a"] == row["b"] else ""
        out.append(f"| {row['a']} | {row['b']}{mark} | {row['n']} |")
    out.append("")

    def section(title, rows, why):
        out.append(f"## {title} -- {len(rows)}")
        out.append("")
        out.append(why)
        out.append("")
        if not rows:
            out.append("None.")
            out.append("")
            return
        out.append(f"| asset | family | {b}'s reason |")
        out.append("|---|---|---|")
        for r in rows[:60]:
            out.append(f"| `{r['asset']}` | {r['family']} | {r['b_note'] or '--'} |")
        if len(rows) > 60:
            out.append(f"| ... | | {len(rows) - 60} more |")
        out.append("")

    section(
        f"{b} rejected what {a} kept",
        d["b_rejects_a_keep"],
        "The highest-value disagreement. A fresh eye rejecting approved work is the "
        "check a single reviewer cannot perform on themselves.",
    )
    section(
        f"{b} kept what {a} discarded",
        d["b_keeps_a_discard"],
        "Read with care. `discard` means OFF-BRIEF, not ugly -- a reviewer who has "
        "not seen the brief cannot apply it, so these may be a vocabulary mismatch "
        "rather than a taste difference.",
    )
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--a", default="pip", help="first reviewer (default: pip)")
    ap.add_argument("--b", default="wanasai", help="second reviewer")
    ap.add_argument("--burst", type=float, default=1.5, help="seconds between events in one action")
    ap.add_argument(
        "--bulk-min", type=int, default=25, help="an action >= this many assets is bulk"
    )
    ap.add_argument("--md", type=pathlib.Path, help="write the markdown report here")
    ap.add_argument("--json", type=pathlib.Path, help="write the raw diff here")
    args = ap.parse_args()

    d = compare(args.a, args.b, args.burst, args.bulk_min)
    md = render_md(d)
    if args.md:
        args.md.write_text(md, encoding="utf-8", newline="")
        print(f"wrote {args.md}")
    if args.json:
        args.json.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8", newline="")
        print(f"wrote {args.json}")
    if not args.md and not args.json:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
