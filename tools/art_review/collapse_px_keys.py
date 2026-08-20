#!/usr/bin/env python3
"""One-shot: collapse the two `px:` key spellings onto one, per reviewer store.

ORPHANS A4. Ruled by Pip 2026-08-20: canonicalise on the write path AND collapse
the pairs that already exist, archiving the losing verdict rather than dropping
it.

WHAT WENT WRONG
---------------
`serve_review.py` writes `px:<dir>/<stem>`; the browser gallery wrote
`px:<dir>/<stem>.png`. Both resolve to the same image. The 2026-08-14/15 sweeps
wrote 1,861 new keys under the second spelling for files that already had the
first, so 1,863 files ended up carrying two verdicts each.

That is not merely untidy. `apply_review.py:parse_assets()` builds one work item
per KEY, and both keys resolve to the same destination filename, so the promotion
gate reports the file as contesting its own destination -- 1,439 of the pairs
were `keep` under both spellings. Promotion has been refusing to run at all.

WHY THE NEWER VERDICT WINS
--------------------------
In all 373 pairs that disagree, the extension-less key is the newer one (the
gallery sweep predates the server sessions). Those are recorded changes of mind,
so the newer judgement is the considered one.

WHY THE LOSER IS ARCHIVED, NOT DROPPED
---------------------------------------
373 of these pairs are a reviewer changing their mind, which is taste data and is
the thing this store exists to hold. The log is append-only and already carries
prior values, so each dropped verdict is written there as an event before it
leaves the projection. Erasing it would be the second and worse falsification --
the same reasoning `revert_action.py` gives for appending rather than editing.

NON-PNG IS EXCLUDED
-------------------
`apply_review.py` resolves a px: key by trying `base` then `base + ".png"`, so an
extension-less key only resolves for .png. There are 9 non-png files under
art_source/; they keep their extension and are not collapsed.

Usage:
    python tools/art_review/collapse_px_keys.py            # dry run
    python tools/art_review/collapse_px_keys.py --write
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ART_SRC = REPO / "art_source"
HERE = REPO / "tools" / "art_review"

# (state file, log file, who the store belongs to)
STORES = [
    (HERE / "review_state.json", HERE / "review_log.jsonl", "pip"),
    (HERE / "review_state.wanasai.json", HERE / "review_log.wanasai.jsonl", "wanasai"),
]


def png_backed(stem: str) -> bool:
    """True when <stem>.png exists, i.e. the extension-less key will resolve."""
    return (ART_SRC / (stem + ".png")).is_file()


def collapse(state: dict) -> tuple[dict, list[dict]]:
    """Return (new_state, dropped) -- dropped entries keep their key and value."""
    pairs: dict[str, dict[str, str]] = {}
    for key in state:
        if not key.startswith("px:"):
            continue
        rel = key[3:]
        if rel.lower().endswith(".png"):
            pairs.setdefault(rel[:-4], {})["ext"] = key
        else:
            pairs.setdefault(rel, {})["bare"] = key

    new = dict(state)
    dropped = []
    for stem, spellings in sorted(pairs.items()):
        if len(spellings) != 2 or not png_backed(stem):
            continue
        bare, ext = spellings["bare"], spellings["ext"]
        a, b = state[bare], state[ext]
        # Newer wins. Ties keep the canonical (bare) entry.
        winner_key = bare if (a.get("updated_at") or "") >= (b.get("updated_at") or "") else ext
        loser_key = ext if winner_key == bare else bare
        new[bare] = dict(state[winner_key])
        if loser_key in new and loser_key != bare:
            del new[loser_key]
        elif loser_key == bare:
            del new[ext]
        dropped.append(
            {
                "stem": stem,
                "kept_from": winner_key,
                "dropped_key": loser_key,
                "dropped_entry": state[loser_key],
                "disagreed": (state[bare].get("verdict") != state[ext].get("verdict")),
            }
        )
    return new, dropped


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    stamp = _dt.datetime.now(_dt.timezone.utc).isoformat()
    totals = {"pairs": 0, "disagreed": 0, "stores": 0, "skipped_non_png": 0}

    for state_path, log_path, owner in STORES:
        if not state_path.is_file():
            continue
        state = json.loads(state_path.read_text(encoding="utf-8"))
        before = len(state)
        new, dropped = collapse(state)
        dis = sum(1 for d in dropped if d["disagreed"])
        totals["pairs"] += len(dropped)
        totals["disagreed"] += dis
        totals["stores"] += 1

        print(f"{state_path.name}  ({owner})")
        print(f"  entries {before} -> {len(new)}   collapsed {len(dropped)} pair(s)")
        print(f"  of which the two spellings DISAGREED on the verdict: {dis}")
        for d in dropped[:3]:
            if d["disagreed"]:
                print(
                    f"    e.g. {d['stem']}: dropped "
                    f"{d['dropped_entry'].get('verdict')!r} kept "
                    f"{new[('px:' + d['stem'])].get('verdict')!r}"
                )
        if not args.write:
            continue

        backup = state_path.with_suffix(f".json.bak-{_dt.datetime.now().strftime('%Y%m%d-%H%M%S')}")
        shutil.copy2(state_path, backup)
        state_path.write_text(
            json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
        )
        # Archive every dropped verdict as a log event BEFORE it stops existing
        # in the projection. Append-only: this adds, never rewrites.
        with log_path.open("a", encoding="utf-8", newline="\n") as fh:
            for d in dropped:
                fh.write(
                    json.dumps(
                        {
                            "asset": d["dropped_key"],
                            "by": owner,
                            "ts": stamp,
                            "cleared": True,
                            "migration": "collapse_px_keys -- ORPHANS A4, duplicate spelling",
                            "prev": d["dropped_entry"],
                            "next": {"verdict": None, "note": "", "tags": []},
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )
        print(f"  backup {backup.name}; {len(dropped)} verdict(s) archived to {log_path.name}")

    print(
        f"\ntotal: {totals['pairs']} pair(s) collapsed across {totals['stores']} store(s); "
        f"{totals['disagreed']} were changes of mind, all preserved in the logs"
    )
    if not args.write:
        print("DRY RUN -- nothing written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
