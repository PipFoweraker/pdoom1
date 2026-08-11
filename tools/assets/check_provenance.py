#!/usr/bin/env python3
"""Guard: the provenance manifest and the pack must agree, and `unknown` must not grow.

Ruled by Pip 2026-08-11: the six unattributable assets are KEPT and recorded as
`unknown`, and the thing that forces them to be resolved later is a MECHANISM,
not a document. This is the mechanism.

WHY A RATCHET AND NOT A RED LIGHT
---------------------------------
The obvious guard -- "fail while any asset is unknown" -- would sit permanently
red, and this estate has already ruled on what that is worth:

    "A guard always red and a guard always green fail identically -- neither
     carries information."   -- SUBMISSION_2026-08-09_four-patterns.md

So this guard pins the unknown set by CONTENT HASH instead. It fails when the
set CHANGES in either direction:

  * a NEW unattributable asset appears  -> the estate got worse, loudly
  * a known one is resolved or removed  -> the pin is stale, update it

Both are events worth interrupting someone for. Steady state is green and means
something.

THE THIRD DIRECTION
-------------------
ADR-0019 defines a two-direction audit (packed-but-undemanded,
demanded-but-unpacked). Provenance needs a third: PACKED-BUT-UNPROVENANCED. A
file hand-copied or merge-accidented into godot/assets/ gets no manifest entry,
and nothing else would ever notice. Report, never delete -- same doctrine.

THE MANIFUND TRIGGER, which is the part nobody was watching
-----------------------------------------------------------
The commitment is one sentence: "Human artists to replace current AI-generated
assets." The pdoom1-website seat established it is a COPY constraint, not a
per-asset attribution requirement -- so "we cannot attribute the pre-existing
set" is already compliant, because the application's own blanket statement that
current assets are AI-generated IS the attribution.

That blanket claim is true ONLY WHILE THE SET IS HOMOGENEOUS. The moment one
human-made asset ships, the set is mixed, the blanket statement goes false, and
per-asset origin becomes load-bearing for the first time.

Nothing tracked that trigger. This does. It is not an error -- it is the
milestone the grant is FOR -- so it exits 0 and shouts.

Usage:
  python tools/assets/check_provenance.py          # audit, exit 1 on drift
  python tools/assets/check_provenance.py --update-pin
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "godot" / "assets"
MANIFEST = REPO / "godot" / "data" / "asset_provenance.json"
PIN = REPO / "tools" / "assets" / "provenance_unknown_pin.json"

ART_EXT = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".bmp"}
AUDIO_EXT = {".ogg", ".wav", ".mp3"}
MEDIA_EXT = ART_EXT | AUDIO_EXT

# Origins that mean "not produced by an image/audio model". The arrival of one of
# these in the ART set is the Manifund trigger.
NON_MODEL = {"authored_code", "photo", "procedural_render"}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        while chunk := fh.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def packed() -> dict[str, Path]:
    return {
        p.relative_to(PACK).as_posix(): p
        for p in PACK.rglob("*")
        if p.is_file() and p.suffix.lower() in MEDIA_EXT
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--update-pin", action="store_true",
                    help="rewrite the unknown-set pin to match the manifest")
    args = ap.parse_args()

    if not MANIFEST.is_file():
        print("RED: no provenance manifest at "
              f"{MANIFEST.relative_to(REPO)}", file=sys.stderr)
        print("     run: python tools/assets/backfill_provenance.py --write",
              file=sys.stderr)
        print("     NOTE: run it on a machine holding a COMPLETE art_generated/.",
              file=sys.stderr)
        print("     A fresh clone yields ~69% attribution and would record 150+",
              file=sys.stderr)
        print("     files as `unknown` that are in fact attributable.", file=sys.stderr)
        return 1

    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assets = doc.get("assets", {})
    on_disk = packed()
    problems = 0

    # --- third direction: packed but unprovenanced -------------------------
    missing = sorted(set(on_disk) - set(assets))
    if missing:
        problems += 1
        print(f"FAIL: {len(missing)} packed file(s) have no provenance entry.")
        print("      Nothing gates godot/assets/ against a hand-copied file, so")
        print("      this is how that shows up. Report, never delete.")
        for m in missing[:20]:
            print(f"        {m}")
        if len(missing) > 20:
            print(f"        ... and {len(missing) - 20} more")

    stale = sorted(set(assets) - set(on_disk))
    if stale:
        problems += 1
        print(f"\nFAIL: {len(stale)} manifest entr(ies) name a file that is gone.")
        for s in stale[:20]:
            print(f"        {s}")

    # --- content drift: same path, different bytes -------------------------
    drifted = []
    for rel, rec in assets.items():
        p = on_disk.get(rel)
        if p and rec.get("sha256") and sha256(p) != rec["sha256"]:
            drifted.append(rel)
    if drifted:
        problems += 1
        print(f"\nFAIL: {len(drifted)} file(s) changed content but kept their "
              "provenance record.")
        for d in drifted[:20]:
            print(f"        {d}")

    # --- the ratchet: the unknown set must be exactly what was pinned ------
    unknown = {rel: rec["sha256"] for rel, rec in assets.items()
               if rec.get("origin") == "unknown"}

    if args.update_pin:
        PIN.write_text(json.dumps({
            "_why": "Pinned unknown set. Ruled by Pip 2026-08-11: keep the "
                    "unattributable assets, record them honestly, and let a "
                    "mechanism force the question later rather than a document.",
            "_fails_when": "an asset becomes unknown, or a pinned one is resolved "
                           "or removed. Both directions are worth interrupting for.",
            "unknown": unknown,
        }, indent=2) + "\n", encoding="utf-8")
        print(f"pinned {len(unknown)} unknown asset(s) -> {PIN.relative_to(REPO)}")
        return 0

    if not PIN.is_file():
        print(f"\nRED: no pin at {PIN.relative_to(REPO)}. "
              "Create it with --update-pin once the manifest is trusted.")
        return 1

    pinned = json.loads(PIN.read_text(encoding="utf-8")).get("unknown", {})
    appeared = sorted(set(unknown) - set(pinned))
    resolved = sorted(set(pinned) - set(unknown))

    if appeared:
        problems += 1
        print(f"\nFAIL: {len(appeared)} NEW unattributable asset(s). The estate "
              "got worse.")
        for a in appeared:
            print(f"        {a}")
        print("      Do not pin these away. Find the record, or find out why "
              "there isn't one.")
    if resolved:
        problems += 1
        print(f"\nFAIL: {len(resolved)} pinned unknown(s) no longer unknown "
              "(resolved or removed).")
        for r in resolved:
            print(f"        {r}")
        print("      Good news, stale pin. Re-run with --update-pin.")

    # --- the Manifund trigger ---------------------------------------------
    human = sorted(
        rel for rel, rec in assets.items()
        if rec.get("origin") in NON_MODEL
        and Path(rel).suffix.lower() in ART_EXT
        and not rel.startswith("cats/simple/")      # contributor photos, always were
        and not rel.startswith("cats/default/")     # placeholder markup, always was
    )
    if human:
        print("\n" + "=" * 68)
        print("MANIFUND TRIGGER: a non-model-generated ART asset is in the pack.")
        print("=" * 68)
        for h in human:
            print(f"  {h}  ({assets[h]['origin']})")
        print()
        print('  The commitment is "Human artists to replace current AI-generated')
        print('  assets." It is a COPY constraint, and it was satisfied by a blanket')
        print("  statement that current assets are AI-generated.")
        print()
        print("  THAT BLANKET STATEMENT IS NOW FALSE. The set is mixed. Per-asset")
        print("  origin is load-bearing from today, and the website's copy has to")
        print("  say something true about a mixed set.")
        print()
        print("  This is not an error. It is the milestone the grant is for.")

    if problems:
        print(f"\n{problems} problem class(es). See above.")
        return 1
    print(f"OK: {len(assets)} provenanced, {len(unknown)} pinned unknown, "
          "pack and manifest agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
