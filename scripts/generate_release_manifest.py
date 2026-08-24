# !/usr/bin/env python3
"""Generate release_manifest.json -- the machine-readable release descriptor.

Layer: GENERATE

WHY THIS SCRIPT EXISTS (issue context: self-updater workstream; see
docs/design/UPDATER_DESIGN.md):

- The manifest used to be a YAML heredoc inside
  .github/workflows/enhanced-release.yml -- untestable, unable to hash the
  built assets (a heredoc cannot read the artifact zips), and silently
  fragile (a quoting slip ships malformed JSON that nothing checks).
- The manifest IS the game's update-check endpoint. `update_check.gd`
  fetches `releases/latest/download/release_manifest.json` at launch, so
  every field here is a contract with shipped clients. NEVER remove or
  rename a field; add only.
- The per-asset sha256 list is the integrity anchor for the future pck
  patcher (L3): a downloaded blob is trusted only if its hash matches the
  manifest fetched over HTTPS. Publishing hashes NOW means every release
  from here on is verifiable, before any auto-download code exists.

Field contract (superset of the old heredoc -- old consumers keep working):

  version           "v0.13.2" (the git tag)
  build_date        ISO-8601 UTC
  commit_hash       full SHA the tag points at
  commit_short      first 8 chars
  ladder_version    NEW -- board epoch from ladder_version.txt ("3"). The
                    client compares this to its own LADDER_VERSION and warns
                    the player when an update forks the board
                    (docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md).
  league_seed       NEW -- the featured league seed this build ships with,
                    read from GameConfig.FEATURED_SEED_OVERRIDE (the SSOT the
                    game itself uses). The website MUST read this rather than
                    derive it: a website-derived seed stranded 23 submissions
                    in July (coordination#40). Sourced, never hand-typed -- a
                    second literal is exactly the drift that forks a board key.
  highlights        NEW -- ASCII-safe CHANGELOG excerpt for this version,
                    truncated; the in-game notice tooltip shows it.
  download_page     NEW -- the release tag page URL (human download surface).
  assets            NEW -- [{name, size, sha256}] for every built zip.
  data_batch_hash, schema_versions, engine, platforms, validation_passed,
  build_pipeline, workflow_run, provenance -- unchanged from the heredoc.

Run locally (loud failure is the point -- a bad manifest must fail the
release, not ship):

  python scripts/generate_release_manifest.py --version v0.13.2 \
      --commit <sha> --assets-dir builds/ --output release_manifest.json
"""

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

# Sibling import: this file lives in scripts/, next to the metadata generator
# whose changelog extraction we reuse rather than duplicate.
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from generate_release_metadata import (  # noqa: E402
    _ABSENT_MARKER,
    ReleaseMetadataGenerator,
    _ascii_safe,
)

_VERSION_RE = re.compile(r"^v?\d+\.\d+\.\d+([.-][0-9A-Za-z.-]+)?$")

# Matches the featured-league seed const in godot/autoload/game_config.gd. Kept
# anchored to line start so a mention inside a comment or a doc string cannot be
# mistaken for the declaration.
_SEED_CONST_RE = re.compile(
    r'^const\s+FEATURED_SEED_OVERRIDE\s*:\s*String\s*=\s*"([^"]*)"', re.MULTILINE
)

# Cap the changelog excerpt embedded in the manifest. The client shows this in
# a tooltip; the release page carries the full notes.
HIGHLIGHTS_MAX_CHARS = 1200
TRUNCATION_MARK = "\n[...] full notes on the release page"


def validate_version(version: str) -> str:
    """Tag-shaped version or die loudly. Returns the input unchanged."""
    if not _VERSION_RE.match(version.strip()):
        raise SystemExit("[manifest] FATAL: version %r is not tag-shaped (vX.Y.Z)" % version)
    return version.strip()


def read_ladder_version(repo_root: Path) -> str:
    """Board epoch from ladder_version.txt -- SSOT, digits only, loud on rot.

    A manifest without a ladder epoch would make the client unable to warn
    players that an update forks their board (the (seed, ladder_epoch) key),
    so a missing/garbled file FAILS the release rather than shipping silence.
    """
    path = repo_root / "ladder_version.txt"
    if not path.exists():
        raise SystemExit("[manifest] FATAL: ladder_version.txt missing at %s" % path)
    value = path.read_text(encoding="ascii").strip()
    if not value.isdigit():
        raise SystemExit(
            "[manifest] FATAL: ladder_version.txt content %r is not a bare integer" % value
        )
    return value


def read_featured_seed(repo_root: Path) -> str:
    """Featured league seed from GameConfig -- the SAME const the game reads.

    `GameConfig.get_weekly_seed()` returns FEATURED_SEED_OVERRIDE whenever it is
    non-empty, which is the pinned-league mode the project runs in. Parsing that
    const is the only way to publish the seed WITHOUT introducing a second copy
    of it, and a second copy is the failure this field exists to end.

    Fails loudly rather than falling back to the calendar-week branch of
    get_weekly_seed(): that branch derives from wall-clock time at RUN time, so
    there is no stable value a build could honestly publish. If the override is
    empty at release time, the release should stop and ask for a pin.
    """
    path = repo_root / "godot" / "autoload" / "game_config.gd"
    if not path.exists():
        raise SystemExit("[manifest] FATAL: game_config.gd missing at %s" % path)
    match = _SEED_CONST_RE.search(path.read_text(encoding="utf-8"))
    if match is None:
        raise SystemExit(
            '[manifest] FATAL: no `const FEATURED_SEED_OVERRIDE: String = "..."` in %s '
            "-- the seed SSOT moved or was renamed; fix this parser, do NOT hand-type a seed" % path
        )
    seed = match.group(1).strip()
    if not seed:
        raise SystemExit(
            "[manifest] FATAL: FEATURED_SEED_OVERRIDE is empty, so the featured seed would be "
            "derived from wall-clock time at run time and no stable value can be published. "
            "Pin the seed in game_config.gd before cutting a release."
        )
    return seed


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_assets(assets_dir: Path) -> list:
    """Hash every built zip under assets_dir (recursive), sorted by name.

    Returns [] when the dir is absent -- callers running without artifacts
    (local dry runs) still get a valid manifest, just without hashes; the
    release workflow always passes the real artifact dir.
    """
    if assets_dir is None or not assets_dir.exists():
        return []
    entries = []
    for path in sorted(assets_dir.rglob("*.zip"), key=lambda p: p.name):
        entries.append(
            {
                "name": path.name,
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return entries


def extract_highlights(repo_root: Path, version: str, max_chars: int = HIGHLIGHTS_MAX_CHARS) -> str:
    """ASCII-safe CHANGELOG excerpt for this version, hard-capped in length.

    A missing section yields an explicit ABSENCE marker, never a stand-in note.
    This was the THIRD copy of the same defect (2026-08-24): the excerpt reached a
    client tooltip, and when extract_changelog_for_version() had no section it
    returned "Release vX.Y.Z / See CHANGELOG.md for details.", which reads as a real
    if terse release note. The extractor now returns None for "I could not find one",
    and this states that rather than papering over it.
    """
    generator = ReleaseMetadataGenerator(repo_root)
    raw = generator.extract_changelog_for_version(version)
    if raw is None:
        return _ABSENT_MARKER.format(version=version)
    text = _ascii_safe(raw).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + TRUNCATION_MARK
    return text


def build_manifest(
    version: str,
    commit: str,
    ladder_version: str,
    league_seed: str,
    highlights: str,
    assets: list,
    repository: str,
    data_hash: str = "",
    workflow_run: str = "",
    ref: str = "",
    actor: str = "",
    event: str = "",
    validation_passed: bool = True,
    build_date: str = "",
) -> dict:
    """Pure assembly -- everything already read/validated by the caller."""
    if not build_date:
        build_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "version": version,
        "build_date": build_date,
        "commit_hash": commit,
        "commit_short": commit[:8],
        "ladder_version": ladder_version,
        "league_seed": league_seed,
        "highlights": highlights,
        "download_page": "https://github.com/%s/releases/tag/%s" % (repository, version),
        "assets": assets,
        "data_batch_hash": data_hash,
        "schema_versions": {
            "events": "1.0",
            "organizations": "1.0",
            "researchers": "1.0",
        },
        "engine": {"name": "Godot", "version": "4.5.1"},
        "platforms": ["windows", "linux", "macos"],
        "validation_passed": validation_passed,
        "build_pipeline": "github-actions",
        "workflow_run": workflow_run,
        "provenance": {
            "repository": repository,
            "ref": ref,
            "actor": actor,
            "event": event,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", required=True, help="release tag, e.g. v0.13.2")
    parser.add_argument("--commit", required=True, help="full commit SHA")
    parser.add_argument("--repository", default="PipFoweraker/pdoom1")
    parser.add_argument("--data-hash", default="")
    parser.add_argument("--workflow-run", default="")
    parser.add_argument("--ref", default="")
    parser.add_argument("--actor", default="")
    parser.add_argument("--event", default="")
    parser.add_argument(
        "--validation-passed",
        default="true",
        choices=["true", "false"],
        help="pass the ACTUAL validation outcome; 'false' records an override release honestly",
    )
    parser.add_argument("--assets-dir", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, default=Path("release_manifest.json"))
    args = parser.parse_args()

    version = validate_version(args.version)
    ladder = read_ladder_version(args.repo_root)
    league_seed = read_featured_seed(args.repo_root)
    highlights = extract_highlights(args.repo_root, version)
    assets = collect_assets(args.assets_dir)

    manifest = build_manifest(
        version=version,
        commit=args.commit,
        ladder_version=ladder,
        league_seed=league_seed,
        highlights=highlights,
        assets=assets,
        repository=args.repository,
        data_hash=args.data_hash,
        workflow_run=args.workflow_run,
        ref=args.ref,
        actor=args.actor,
        event=args.event,
        validation_passed=(args.validation_passed == "true"),
    )

    body = json.dumps(manifest, indent=2, sort_keys=False)
    body.encode("ascii")  # loud non-ASCII gate; _ascii_safe should guarantee this
    args.output.write_text(body + "\n", encoding="ascii")

    print("[manifest] wrote %s" % args.output)
    print(
        "[manifest] version=%s ladder=L%s seed=%s assets=%d"
        % (version, ladder, league_seed, len(assets))
    )
    for entry in assets:
        print(
            "[manifest]   %s  %d bytes  sha256=%s" % (entry["name"], entry["size"], entry["sha256"])
        )
    if not assets:
        print(
            "[manifest] WARNING: no assets hashed (no --assets-dir?); manifest carries no integrity anchors"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
