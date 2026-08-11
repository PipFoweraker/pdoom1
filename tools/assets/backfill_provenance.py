#!/usr/bin/env python3
"""Backfill asset provenance for everything already packed into godot/assets/.

Answers `coordination#32`. Implements Option A from
`docs/design/ASSET_PROVENANCE_SCOPE_2026-08-06.md`, authorised by Pip 2026-08-11
to run BEFORE the ADR-0019 pull step exists, on the grounds that 161 files'
evidence currently lives single-copy in a gitignored directory on one machine.

WHY THIS IS AN INTERIM, AND SAYS SO IN ITS OWN OUTPUT
-----------------------------------------------------
The scope doc's recommendation is that the ADR-0019 pull step be the SOLE writer
of the manifest, so provenance is a by-product of the write that already happens.
That step does not exist yet. Until it does, this file is a second write site --
exactly the shape ADR-0019's `is_ranked_run()` comment warns about. The mitigation
is not cleverness, it is honesty: every record carries `written_by` and
`evidence`, and `check_provenance.py` fails when the manifest and the pack
disagree, so drift is loud rather than silent.

THE EVIDENCE TIERS (from the scope doc's measured pass, reproduced here)
------------------------------------------------------------------------
  A  content hash -> art_source/ batch WITH a MANIFEST.md    tool, mode, size, UUIDs
  B  content hash -> art_source/ without a manifest          the contributor cat photos
  C  git add-commit message names the generator              origin class, batch depth
  D  content hash -> art_generated/ only                     class from batch dir; LOCAL-ONLY
  E  resolved by hand inspection                             music renders, authored SVG
  F  unattributable                                          recorded `unknown`, never guessed

Tier D is why this runs today: that evidence is not in git.

ORIGIN VOCABULARY -- five values, ruled by Pip 2026-08-11
----------------------------------------------------------
  generated_model    an image/audio model produced it
  authored_code      a human wrote markup or code that IS the asset
  procedural_render  a deterministic render of human-authored code
  photo              a camera produced it
  unknown            no record anywhere -- NEVER inferred

Three values would force a lie: the 8 music .ogg are captures of hand-authored
WebAudio patches, which is neither "generated" nor "human" in the naive sense.

Usage:
  python tools/assets/backfill_provenance.py --dry-run
  python tools/assets/backfill_provenance.py --write
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "godot" / "assets"
OUT = REPO / "godot" / "data" / "asset_provenance.json"

ART_EXT = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".bmp"}
AUDIO_EXT = {".ogg", ".wav", ".mp3"}
MEDIA_EXT = ART_EXT | AUDIO_EXT

LIBRARY_DIRS = ["art_source", "art_generated"]

# --- Tier E: established by hand inspection in the scope doc, cited not guessed ---
# godot/assets/cats/default/*.svg are hand-written markup, self-labelled in a
# comment. They sit under cats/ and ANY rule keying on the directory sweeps them
# into `photo` with the contributor photographs. That is the specific mistake the
# scope doc warns a backfill writer about, so it is handled before the cat rule.
AUTHORED_CODE_PREFIX = "cats/default/"
# godot/assets/cats/simple/*.jpg are the 8 contributor cat PHOTOGRAPHS, used with
# their owners' explicit permission (confirmed by Pip 2026-08-06).
PHOTO_PREFIX = "cats/simple/"
# godot/assets/audio/music/*.ogg are digital captures of hand-authored WebAudio
# patches (tools/music/patches/*.js via capture_takes.py), not model-generated
# audio.
PROCEDURAL_PREFIX = "audio/music/"

GENERATOR_TOKENS = [
    ("pixellab", "pixellab"),
    ("gpt-image", "gpt-image"),
    ("gpt_image", "gpt-image"),
    ("dall-e", "dall-e"),
    ("AI-powered asset generation", "unnamed-model"),
    ("AI-generated", "unnamed-model"),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        while chunk := fh.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def packed_files() -> list[Path]:
    return sorted(
        p for p in PACK.rglob("*")
        if p.is_file() and p.suffix.lower() in MEDIA_EXT
    )


def build_library_index(extra: list[Path] | None = None) -> dict[str, list[Path]]:
    """content hash -> every library path with that content.

    `extra` exists because `art_generated/` is only partly committed: 534 of the
    5,183 files are tracked, and the rest live on whichever machine ran the
    generation. Tier D depends on them. Running this on a fresh clone without
    them silently records 150+ attributable files as `unknown` -- a manifest that
    validates cleanly and is wrong, which is the failure mode this estate keeps
    catching. Point `--library` at a synced copy instead.
    """
    roots = [REPO / d for d in LIBRARY_DIRS] + list(extra or [])
    index: dict[str, list[Path]] = {}
    for root in roots:
        if not root.is_dir():
            print(f"  NOTE: {root} absent -- tier coverage will be lower")
            continue
        n = 0
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in MEDIA_EXT:
                index.setdefault(sha256(p), []).append(p)
                n += 1
        print(f"  {n:5d} media files in {root}")
    return index


_YAML_IDS: dict[str, dict] | None = None


def yaml_id_lookup() -> dict[str, dict]:
    """asset id -> {file, model} from the committed prompt manifests.

    `art_prompts/*.yaml` is the RULED source of truth per ART_MASTERS_POLICY:
    "the true source is the committed YAML prompt manifests, from which any
    master is regenerable for cents". Masters are a cache; these are the record.

    Parsed with regex rather than PyYAML deliberately -- this tool must run on a
    bare checkout with no third-party packages, the same constraint the rest of
    tools/ works under. Only two shapes are needed: `- id: <x>` and `model: <y>`.
    """
    global _YAML_IDS
    if _YAML_IDS is not None:
        return _YAML_IDS
    out: dict[str, dict] = {}
    root = REPO / "art_prompts"
    if root.is_dir():
        for f in sorted(root.glob("*.yaml")):
            text = f.read_text(encoding="utf-8", errors="replace")
            cur = None
            for line in text.splitlines():
                m = re.match(r"^\s*-\s+id:\s*(\S+)", line)
                if m:
                    cur = m.group(1).strip().strip("'\"")
                    out.setdefault(cur, {"file": f.name, "model": None})
                    continue
                m = re.match(r"^\s*model:\s*(\S+)", line)
                if m and cur and not out[cur]["model"]:
                    out[cur]["model"] = m.group(1).strip().strip("'\"")
    _YAML_IDS = out
    return out


def nearest_manifest(p: Path) -> Path | None:
    for parent in p.parents:
        if parent == REPO:
            break
        for name in ("MANIFEST.md", "INVENTORY.md"):
            cand = parent / name
            if cand.is_file():
                return cand
    return None


def add_commit(rel: Path) -> tuple[str, str] | None:
    """(sha, subject) of the commit that first added this path."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%H%x1f%s%x1f%b",
             "-1", "--", str(rel)],
            cwd=REPO, capture_output=True, text=True, timeout=60,
        ).stdout.strip()
    except Exception:
        return None
    if not out:
        return None
    parts = out.split("\x1f")
    return (parts[0], " ".join(parts[1:]).strip())


def classify(p: Path, lib: dict[str, list[Path]]) -> dict:
    rel_pack = p.relative_to(PACK).as_posix()
    rel_repo = p.relative_to(REPO)
    digest = sha256(p)

    rec = {
        "sha256": digest,
        "bytes": p.stat().st_size,
        "origin": None,
        "origin_detail": None,
        "evidence": None,
        "confidence": None,
    }

    # Tier E first -- these are established, and a directory-keyed rule would
    # misfile them. Order matters: authored_code BEFORE the cats/ photo rule.
    if rel_pack.startswith(AUTHORED_CODE_PREFIX) and p.suffix.lower() == ".svg":
        rec.update(origin="authored_code", confidence="high",
                   origin_detail="hand-written SVG, self-labelled placeholder "
                                 "(tools/generate_cat_placeholders.py)",
                   evidence="E:hand-inspection")
        return rec
    if rel_pack.startswith(PROCEDURAL_PREFIX) and p.suffix.lower() == ".ogg":
        rec.update(origin="procedural_render", confidence="high",
                   origin_detail="digital capture of hand-authored WebAudio patch "
                                 "(tools/music/patches/*.js via capture_takes.py)",
                   evidence="E:hand-inspection")
        return rec
    if rel_pack.startswith(PHOTO_PREFIX):
        rec.update(origin="photo", confidence="high",
                   origin_detail="contributor cat photograph, used with the owner's "
                                 "explicit permission (confirmed by Pip 2026-08-06)",
                   evidence="E:hand-inspection")
        return rec

    # Tiers A/D -- exact content match into the library.
    #
    # "No false positives" was WRONG and this comment used to say so. A byte match
    # proves two committed copies share lineage. It does NOT prove either copy has
    # a generation record behind it.
    #
    # The specimen: godot/assets/ui/buttons/glowcat/cat_icon.svg is byte-identical
    # to art_source/dump_october_31_2025/cat_icon.svg. That folder is a USAGE
    # BUNDLE -- its README.txt explains how to wire the icon into a button and
    # never says where the icon came from. An earlier version of this tool called
    # that attributable; the 2026-08-06 scope doc lists the same file among the six
    # genuinely unattributable ones, and the scope doc is right.
    #
    # So a hash match only establishes origin when the matched location ALSO holds
    # a generation record. Otherwise it falls through and may end at `unknown`.
    hits = lib.get(digest, [])
    if hits:
        hit = hits[0]
        where = hit.relative_to(REPO).as_posix()
        man = nearest_manifest(hit)
        in_generated = "art_generated" in Path(where).parts or "art_generated" in where
        if man:
            rec.update(origin="generated_model", confidence="high",
                       origin_detail=f"content-identical to {where}; batch record "
                                     f"{man.relative_to(REPO).as_posix()}",
                       evidence="A:hash->library+manifest")
            return rec
        if in_generated:
            rec.update(origin="generated_model", confidence="medium",
                       origin_detail=f"content-identical to {where} (the batch "
                                     f"directory names the run)",
                       evidence="D:hash->art_generated")
            return rec
        # matched, but into a location with no generation record. Keep looking.
        rec["origin_detail"] = (f"content-identical to {where}, which carries no "
                                f"generation record (lineage, not origin)")

    # Tier Y -- filename stem matches an asset id in a committed prompt manifest.
    # Recovers assets whose derivative file was pruned (so nothing hashes) and
    # whose add-commit does not name a model. Measured to recover the 20
    # textures/ files that every hash-based pass misses.
    yid = yaml_id_lookup()
    stem = p.stem
    for cand in (stem, re.sub(r"_(\d{2,4})$", "", stem)):
        info = yid.get(cand)
        if info:
            rec.update(origin="generated_model", confidence="medium",
                       origin_detail=f"asset id '{cand}' in {info['file']}"
                                     + (f", model {info['model']}" if info["model"] else ""),
                       evidence="Y:prompt-manifest-id")
            return rec

    # Tier C -- the commit that introduced it names a generator.
    ac = add_commit(rel_repo)
    if ac:
        sha, subject = ac
        low = subject.lower()
        for token, tool in GENERATOR_TOKENS:
            if token.lower() in low:
                rec.update(origin="generated_model", confidence="medium",
                           origin_detail=f"add-commit {sha[:8]} names {tool}",
                           evidence="C:git-commit-message")
                return rec

    # Tier F -- no record. Recorded, never inferred.
    rec.update(origin="unknown", confidence="none",
               origin_detail="no record in art_source/, art_generated/, or the "
                             "add-commit message. NOT inferred from dimensions.",
               evidence="F:none")
    return rec


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="write the manifest")
    ap.add_argument("--dry-run", action="store_true", help="report only (default)")
    ap.add_argument("--library", action="append", type=Path, default=[],
                    metavar="DIR",
                    help="extra library root to hash (repeatable). Use this to point "
                         "at a synced copy of the full art_generated/ from the machine "
                         "that generated it -- tier D depends on files that are NOT in git.")
    args = ap.parse_args()
    if not args.write:
        args.dry_run = True

    if not PACK.is_dir():
        sys.exit(f"no pack directory at {PACK}")

    print("indexing library ...")
    lib = build_library_index([d.expanduser().resolve() for d in args.library])
    print(f"  {len(lib)} distinct library contents\n")

    files = packed_files()
    print(f"classifying {len(files)} packed art/audio files ...")
    assets = {}
    for p in files:
        assets[p.relative_to(PACK).as_posix()] = classify(p, lib)

    origins = Counter(r["origin"] for r in assets.values())
    tiers = Counter(r["evidence"] for r in assets.values())
    unknown = sorted(k for k, r in assets.items() if r["origin"] == "unknown")

    print("\norigin:")
    for k, v in origins.most_common():
        print(f"  {k:<18} {v:4d}  ({v / len(assets) * 100:.1f}%)")
    print("\nevidence tier:")
    for k, v in tiers.most_common():
        print(f"  {k:<28} {v:4d}")
    attributable = len(assets) - origins.get("unknown", 0)
    print(f"\nattributable: {attributable}/{len(assets)} = "
          f"{attributable / len(assets) * 100:.1f}%")
    print(f"unknown ({len(unknown)}):")
    for u in unknown:
        print(f"  {u}")

    doc = {
        "_schema": "asset_provenance/1.0",
        "_answers": "coordination#32",
        "_generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "_written_by": "tools/assets/backfill_provenance.py",
        "_interim": (
            "INTERIM. The ADR-0019 pull step does not exist yet; when it does it "
            "becomes the sole writer and this backfill is retired. Until then this "
            "is a second write site and can drift -- tools/assets/check_provenance.py "
            "fails loudly when it does."
        ),
        "_origin_values": [
            "generated_model", "authored_code", "procedural_render", "photo", "unknown",
        ],
        "_unknown_is_not_a_guess": (
            "`unknown` means no record exists. It is never inferred from image "
            "dimensions. 1024x1024 and 1536x1024 are OpenAI output sizes, which makes "
            "'these are gpt-image' a plausible guess; coordination#32 ruled that an "
            "honest unknown beats an inferred generated."
        ),
        "assets": assets,
    }

    if args.dry_run:
        print(f"\nDRY RUN -- would write {OUT.relative_to(REPO)}")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(REPO)}  ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
