#!/usr/bin/env python3
"""Undo one batch action, restoring exactly what each asset was before it.

Layer: PROVE (dry-run by default; only --apply writes)

WHY THIS CAN EXIST AT ALL
-------------------------
Because the decision log is append-only and every event carries its `prev`. A
state file alone could not support this: the previous verdict would already be
overwritten. This is the payoff of the log design, collected.

THE INCIDENT IT WAS WRITTEN FOR (2026-08-19)
--------------------------------------------
A guest reviewer meant to tag a handful of flame frames "flame good". A large
selection from earlier in the session was still active, so one click wrote
`keep` + that note to 1,694 assets at 22:14:58 -- the last minute of the session.

1,691 of them had NO prior verdict, so restoring them loses nothing. Three had
real prior calls, and the log still holds them. Without the log, the only honest
options would have been to keep 1,694 opinions she never gave, or to delete work
she did give.

A REVERT IS ITSELF AN EVENT
---------------------------
This does not rewrite the log. It appends new events restoring the prior values,
so "she swept 1,694 by accident and it was undone" stays visible. Erasing the
mistake would be a second, worse falsification.

Usage:
  # what would change (default -- writes nothing)
  python tools/art_review/revert_action.py --reviewer wanasai --at 2026-08-19T12:14:58

  # do it
  python tools/art_review/revert_action.py --reviewer wanasai --at 2026-08-19T12:14:58 --apply

  # list the big actions if you do not know the timestamp
  python tools/art_review/revert_action.py --reviewer wanasai --list
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import serve_review as sr  # noqa: E402


def load_log(reviewer: str) -> list:
    sr.set_reviewer(reviewer)
    if not sr.LOG_PATH.exists():
        sys.exit(f"no log for {reviewer!r} at {sr.LOG_PATH}")
    out = []
    for line in sr.LOG_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("ts"):
            e["_t"] = dt.datetime.fromisoformat(e["ts"]).replace(tzinfo=None)
            out.append(e)
    out.sort(key=lambda e: e["_t"])
    return out


def cluster(log: list, burst: float) -> list:
    if not log:
        return []
    cl = [[log[0]]]
    for prev, cur in zip(log, log[1:]):
        if (cur["_t"] - prev["_t"]).total_seconds() <= burst:
            cl[-1].append(cur)
        else:
            cl.append([cur])
    return cl


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--reviewer", default="pip")
    ap.add_argument("--at", help="ISO timestamp (UTC) of any event in the action")
    ap.add_argument("--window", type=float, default=5.0, help="seconds around --at to match")
    ap.add_argument("--burst", type=float, default=1.5, help="seconds between events in one action")
    ap.add_argument("--list", action="store_true", help="show the largest actions and exit")
    ap.add_argument("--min-size", type=int, default=25, help="with --list, only actions this big")
    ap.add_argument("--apply", action="store_true", help="actually write (default is dry run)")
    args = ap.parse_args()

    log = load_log(args.reviewer)
    clusters = cluster(log, args.burst)

    if args.list or not args.at:
        big = [c for c in clusters if len(c) >= args.min_size]
        big.sort(key=len, reverse=True)
        print(f"{args.reviewer}: {len(log)} events in {len(clusters)} actions")
        print(f"actions of >= {args.min_size} assets:\n")
        for c in big[:20]:
            note = ((c[0].get("next") or {}).get("note") or "").strip()
            verd = (c[0].get("next") or {}).get("verdict")
            print(
                f"  {c[0]['ts'][:19]}Z  {len(c):5} assets  verdict={verd}"
                + (f"  note={note[:48]!r}" if note else "")
            )
        if not args.at:
            print("\n(pass --at <timestamp> to target one)")
        return 0

    target = dt.datetime.fromisoformat(args.at).replace(tzinfo=None)
    hit = None
    for c in clusters:
        if any(abs((e["_t"] - target).total_seconds()) <= args.window for e in c):
            hit = c
            break
    if not hit:
        sys.exit(f"no action found within {args.window}s of {args.at}")

    # Last write per asset in the action is what the state currently reflects;
    # its `prev` is what to restore.
    restore = {}
    for e in hit:
        restore[e["asset"]] = e.get("prev") or {}

    print(f"action: {hit[0]['ts'][:19]}Z, {len(hit)} events over {len(restore)} assets")
    wrote = collections.Counter(
        json.dumps((e.get("next") or {}), sort_keys=True) for e in hit
    ).most_common(1)
    if wrote:
        print(f"  it wrote: {wrote[0][0][:110]}  (x{wrote[0][1]})")
    back = collections.Counter(v.get("verdict") for v in restore.values())
    print(f"  restoring to: {dict(back)}")
    keep_prior = [a for a, v in restore.items() if v.get("verdict")]
    print(f"  assets that had a REAL prior verdict: {len(keep_prior)}")
    for a in keep_prior[:12]:
        v = restore[a]
        print(f"    {a}  -> {v.get('verdict')}  {(v.get('note') or '')[:44]!r}")

    if not args.apply:
        print("\nDRY RUN -- nothing written. Re-run with --apply to restore.")
        return 0

    ok = 0
    for asset, prev in restore.items():
        patch = {
            "asset_id": asset,
            "verdict": prev.get("verdict"),
            "note": prev.get("note", ""),
            "tags": prev.get("tags", []),
        }
        if prev.get("shelf_reason"):
            patch["shelf_reason"] = prev["shelf_reason"]
        code, _resp = sr.apply_patch(patch)
        if code == 200:
            ok += 1
    print(f"\nrestored {ok}/{len(restore)} assets.")
    print("The revert is itself logged -- the accident stays visible in the history.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
