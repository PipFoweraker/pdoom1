#!/usr/bin/env python3
"""merge_gallery_export.py -- fold a full_gallery.html export back into
tools/art_review/review_state.json (the ONE verdict store apply_review.py
reads). No second store; the browser export is a transport, not a home.

The gallery's "E" key downloads gallery_verdicts_*.json shaped exactly like
review_state.json entries: {asset_id: {verdict, note, tags, updated_at}}.
An empty verdict ("") means "cleared in the gallery" and is written through
(apply_review.py filters empty verdicts out, so a clear sticks).

Merge rule: per asset_id, the NEWER updated_at wins; ties keep the incoming
value. px: keys are canonicalised against the existing state so the legacy
extension-less spelling and the new with-extension spelling never coexist for
the same file.

Usage:
    python tools/art_review/merge_gallery_export.py DOWNLOAD.json [--dry-run]
                                                    [--state PATH]
A timestamped backup of the state file is written before any change.
"""

import argparse
import datetime as _dt
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_STATE = REPO / "tools" / "art_review" / "review_state.json"


def canonical_key(key, state):
    """Map an incoming px: key onto an existing state key for the same file."""
    if key in state or not key.startswith("px:"):
        return key
    rel = key[3:]
    if rel.lower().endswith(".png"):
        sans = "px:" + rel[: -len(".png")]
        if sans in state:
            return sans
    else:
        withext = "px:" + rel + ".png"
        if withext in state:
            return withext
    return key


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("export", help="gallery_verdicts_*.json downloaded from the page")
    ap.add_argument("--state", default=str(DEFAULT_STATE))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    export_path = Path(args.export)
    state_path = Path(args.state)
    if not export_path.is_file():
        sys.exit(f"error: {export_path} not found")
    try:
        incoming = json.loads(export_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"error: {export_path} is not valid JSON: {e}")
    if not isinstance(incoming, dict):
        sys.exit("error: export must be an object of asset_id -> entry")

    state = {}
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            sys.exit(f"error: {state_path} is not an object")

    added = updated = skipped_older = unchanged = bad = 0
    for key, entry in sorted(incoming.items()):
        if not isinstance(entry, dict):
            bad += 1
            continue
        tgt = canonical_key(key, state)
        new = {
            "verdict": (entry.get("verdict") or "").strip().lower(),
            "note": entry.get("note") or "",
            "tags": entry.get("tags") or [],
            "updated_at": entry.get("updated_at") or "",
        }
        old = state.get(tgt)
        if old is None:
            state[tgt] = new
            added += 1
            print(f"ADD  {tgt} -> {new['verdict'] or '(cleared)'}")
        else:
            old_ts = old.get("updated_at") or ""
            if old_ts > new["updated_at"]:
                skipped_older += 1
                print(f"SKIP {tgt} (state is newer: {old_ts})")
            elif old.get("verdict") == new["verdict"] and (old.get("note") or "") == new["note"]:
                unchanged += 1
            else:
                state[tgt] = new
                updated += 1
                print(
                    f"UPD  {tgt}: {old.get('verdict')!r} -> " f"{new['verdict'] or '(cleared)'!r}"
                )

    print(
        f"\nadded={added} updated={updated} unchanged={unchanged} "
        f"skipped-older={skipped_older} bad-entries={bad}"
    )
    if args.dry_run:
        print("dry-run: state file untouched.")
        return 0
    if added or updated:
        if state_path.is_file():
            stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = state_path.with_suffix(f".json.bak-{stamp}")
            shutil.copy2(state_path, backup)
            print(f"backup: {backup}")
        state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote {state_path} ({len(state)} entries)")
    else:
        print("nothing to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
