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

WHY IT HASHES THE GIT BLOB AND NOT THE FILE ON DISK (2026-08-19)
-----------------------------------------------------------------
It used to hash the working tree. Run on New-Bort at `71d2fa76` it reported six
files as "changed content but kept their provenance record" -- all six were
false. `.gitattributes` gained `*.svg text eol=lf` after those working copies
were checked out, and git does not renormalise a file it has no reason to
touch, so `cats/default/happy.svg` is 837 bytes with CRLF on disk and 818 bytes
in the blob. The blob's sha256 matches the manifest exactly.

So the working tree answers a per-checkout question and the manifest asks a
per-content one. Hashing the blob makes this guard give the same answer on
Windows, on the Debian laptop and in CI, which is the only version of it worth
wiring into anything -- and a guard that cries wolf on every text asset is one
this estate has already ruled carries no information.

`--self-test` proves both directions on a synthetic repo built for the purpose,
so the fix cannot decay into a comparator that always agrees.

RULING: 2026-08-19 -- the provenance guard compares against the git blob, not the working tree, and runs in pre-commit and CI; a guard wired to nothing is a document -- flavour: art-provenance -- mechanism: .pre-commit-config.yaml provenance-check + quality-checks.yml, both running --self-test first

Usage:
  python tools/assets/check_provenance.py          # audit, exit 1 on drift
  python tools/assets/check_provenance.py --self-test
  python tools/assets/check_provenance.py --update-pin
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
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

CREDIT_SOURCE = "CREDITS.md"
PHOTO_ASSET_DIR = "cats/simple/"


def credit_forms(repo: Path) -> dict[str, str]:
    """pack-relative asset path -> the credit form CREDITS.md says to use.

    Deliberately a small independent reader rather than an import of
    backfill_provenance.credit_forms(): a checker that shares its parser with the
    writer it checks cannot catch a parser bug, only a data bug. Clause 2 of the
    check rule (#1075) -- do not derive what to look for from the system under
    test.

    Cells still carrying a [Pip to fill] / [Pip to confirm] placeholder mean no
    credit form has been chosen, and are omitted so they read as unattributed --
    matching what generate_credits.py does with the same markers.
    """
    out: dict[str, str] = {}
    src = repo / CREDIT_SOURCE
    if not src.is_file():
        return out
    in_cats = False
    for line in src.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_cats = line.strip().lower() == "## cats"
            continue
        if not in_cats or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[2].lower() in ("asset", "---"):
            continue
        if set(cells[0]) <= set("-: "):
            continue
        who, asset = cells[1], cells[2]
        if "[Pip to" in who or not asset:
            continue
        out[PHOTO_ASSET_DIR + asset] = who
    return out


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        while chunk := fh.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def git_contents(repo: Path, paths: list[str]) -> dict[str, bytes]:
    """Bytes for each repo-relative path AS GIT STORES THEM: index first.

    Returns only the paths git could resolve. A path absent from the result is
    untracked and unstaged -- a brand new asset -- and the caller falls back to
    the working tree for it, which is the right answer there because no blob
    exists yet to disagree with.

    One `git cat-file --batch` process, not one per file: the pack is 510 files
    and process spawn on Windows is the expensive part.
    """
    if not paths:
        return {}
    payload = ("\n".join(f":{p}" for p in paths) + "\n").encode("utf-8")
    proc = subprocess.run(
        ["git", "cat-file", "--batch"],
        input=payload,
        capture_output=True,
        cwd=str(repo),
    )
    out = proc.stdout
    if not out:
        return {}

    # --batch emits, per input line, either
    #   <sha1> SP <type> SP <size> LF <contents> LF
    # or
    #   <spec> SP missing LF
    # so the reply is positional and has to be walked, not split.
    found: dict[str, bytes] = {}
    pos = 0
    for rel in paths:
        nl = out.find(b"\n", pos)
        if nl < 0:
            break
        header = out[pos:nl].decode("utf-8", "replace").split(" ")
        if header[-1] in ("missing", "ambiguous"):
            pos = nl + 1
            continue
        try:
            size = int(header[2])
        except (IndexError, ValueError):
            break
        start = nl + 1
        found[rel] = out[start : start + size]
        pos = start + size + 1  # the LF git adds after the payload
    return found


def packed() -> dict[str, Path]:
    return {
        p.relative_to(PACK).as_posix(): p
        for p in PACK.rglob("*")
        if p.is_file() and p.suffix.lower() in MEDIA_EXT
    }


def self_test() -> int:
    """Prove `git_contents` gives BOTH answers, on a repo built to force them.

    Replays the 2026-08-19 false positive exactly: a blob committed with LF, a
    working copy carrying CRLF, and a manifest hash taken from the blob. The old
    working-tree comparison called that drift. This must not -- AND must still
    call a genuine byte change drift, or the fix is just a comparator that
    always agrees, which is the failure mode #640 is named for.
    """
    failures = []
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        run = lambda *a: subprocess.run(  # noqa: E731 -- local, three uses
            ["git", *a], cwd=str(repo), capture_output=True, check=True
        )
        run("init", "-q")
        run("config", "user.email", "selftest@example.invalid")
        run("config", "user.name", "selftest")

        lf = b"<svg>\n<rect/>\n</svg>\n"
        (repo / "eol.svg").write_bytes(lf)
        (repo / "same.bin").write_bytes(b"\x00\x01\x02")
        (repo / "changed.bin").write_bytes(b"original")
        run("add", "-A")
        run("commit", "-qm", "selftest")

        # The trap: renormalisation never happened on this checkout.
        (repo / "eol.svg").write_bytes(lf.replace(b"\n", b"\r\n"))
        # And a real edit, STAGED, which must still be caught. Staged is the
        # honest representation of "the asset changed": an unstaged working-tree
        # edit is invisible to this guard by design, because nothing unstaged
        # can be committed and CI clones a tree where the two agree anyway.
        (repo / "changed.bin").write_bytes(b"tampered")
        run("add", "changed.bin")

        paths = ["eol.svg", "same.bin", "changed.bin"]
        blobs = git_contents(repo, paths)

        # The manifest records the hash of what was committed.
        recorded = {
            rel: hashlib.sha256(b).hexdigest()
            for rel, b in (
                ("eol.svg", lf),
                ("same.bin", b"\x00\x01\x02"),
                ("changed.bin", b"original"),
            )
        }

        def drifts(rel: str) -> bool:
            blob = blobs.get(rel)
            digest = hashlib.sha256(blob).hexdigest() if blob is not None else sha256(repo / rel)
            return digest != recorded[rel]

        if (repo / "eol.svg").read_bytes() == lf:
            failures.append(
                "eol.svg: the working copy was not CRLF, so this self-test did "
                "not reproduce the condition it exists to pin"
            )
        eol_ok = not drifts("eol.svg")
        same_ok = not drifts("same.bin")
        changed_caught = drifts("changed.bin")

        # An untracked file has no blob and must be reported as absent, not as
        # empty bytes -- empty would hash to a constant and read as drift.
        (repo / "new.bin").write_bytes(b"arrived")
        untracked_absent = "new.bin" not in git_contents(repo, ["new.bin"])

        if not eol_ok:
            failures.append("eol.svg: CRLF working copy still reported as drift")
        if not same_ok:
            failures.append("same.bin: unchanged binary reported as drift")
        if not changed_caught:
            failures.append(
                "changed.bin: a real byte change was NOT caught -- the "
                "comparator has decayed into one that always agrees"
            )
        if not untracked_absent:
            failures.append("new.bin: untracked file resolved to a blob")

        # --- the credit-withdrawal case, pinned so it cannot decay ---------
        # The point of the credit check is that removing someone from CREDITS.md
        # removes them everywhere. Prove the reader sees a withdrawal, and that
        # a placeholder reads as unattributed rather than as a name.
        credits_md = repo / "CREDITS.md"
        credits_md.write_text(
            "# c\n\n## Cats\n\n| Cat | Photo by | Asset |\n|---|---|---|\n"
            "| A | Alex | a.jpg |\n| B | [Pip to confirm -- withdrew] | b.jpg |\n",
            encoding="utf-8",
        )
        forms = credit_forms(repo)
        credited_ok = forms.get("cats/simple/a.jpg") == "Alex"
        withdrawn_ok = "cats/simple/b.jpg" not in forms
        if not credited_ok:
            failures.append("credit reader did not read a plain credited row")
        if not withdrawn_ok:
            failures.append(
                "a withdrawn/placeholder credit was read as a name -- the "
                "manifest would keep shipping someone who asked to be removed"
            )

        verdicts = [
            ("CRLF working copy vs LF blob", eol_ok, "no drift"),
            ("credited row read from CREDITS.md", credited_ok, "name"),
            ("withdrawn credit (placeholder)", withdrawn_ok, "unattributed"),
            ("unchanged binary", same_ok, "no drift"),
            ("genuinely edited file", changed_caught, "drift"),
            ("untracked file", untracked_absent, "no blob, falls back to disk"),
        ]

    print("self-test: git_contents reads the index, not the working tree")
    for label, ok, expected in verdicts:
        print(f"  {label:<30} -> {expected if ok else 'WRONG ANSWER'}")
    if failures:
        print("\nSELF-TEST FAILED:")
        for f in failures:
            print(f"  {f}")
        return 1
    print("\nself-test OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--update-pin",
        action="store_true",
        help="rewrite the unknown-set pin to match the manifest",
    )
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="prove the blob comparison still gives both answers",
    )
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if not MANIFEST.is_file():
        print("RED: no provenance manifest at " f"{MANIFEST.relative_to(REPO)}", file=sys.stderr)
        print("     run: python tools/assets/backfill_provenance.py --write", file=sys.stderr)
        print("     NOTE: run it on a machine holding a COMPLETE art_generated/.", file=sys.stderr)
        print("     A fresh clone yields ~69% attribution and would record 150+", file=sys.stderr)
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
    # Against the BLOB, not the working tree -- see the module docstring. An
    # untracked file has no blob, so it falls back to disk; that is a new asset
    # arriving, and disk is the only copy there is.
    shared = sorted(set(assets) & set(on_disk))
    blobs = git_contents(REPO, [f"godot/assets/{rel}" for rel in shared])
    drifted, untracked = [], []
    for rel in shared:
        rec = assets[rel]
        if not rec.get("sha256"):
            continue
        blob = blobs.get(f"godot/assets/{rel}")
        if blob is None:
            untracked.append(rel)
            digest = sha256(on_disk[rel])
        else:
            digest = hashlib.sha256(blob).hexdigest()
        if digest != rec["sha256"]:
            drifted.append(rel)
    if drifted:
        problems += 1
        print(
            f"\nFAIL: {len(drifted)} file(s) changed content but kept their " "provenance record."
        )
        for d in drifted[:20]:
            print(f"        {d}")
        if untracked:
            print(
                f"      ({len(untracked)} of the files compared are untracked "
                "and were read from disk.)"
            )

    # --- credit drift: the manifest must agree with the credits SSOT -------
    # CREDITS.md is the source of truth for who is credited; this manifest only
    # mirrors it. The mirror existed for one day and was already wrong -- it
    # carried "Office (default/mascot)" for web-doom-cat.jpg, a value CREDITS.md
    # had resolved to "Pip" eight days earlier.
    #
    # This is the check that makes WITHDRAWAL reliable. Consent can be taken
    # back, and if it is, one edit to CREDITS.md has to be enough. Without this,
    # removing someone from the credits leaves their name sitting in a manifest
    # that ships inside the .pck -- "we removed you" that is not true, which is
    # worse than never having credited them.
    credits = credit_forms(REPO)
    credit_drift = []
    for rel, rec in assets.items():
        want = credits.get(rel, "unattributed")
        got = rec.get("author", "unattributed")
        if got != want:
            credit_drift.append((rel, got, want))
    if credit_drift:
        problems += 1
        print(
            f"\nFAIL: {len(credit_drift)} asset(s) disagree with {CREDIT_SOURCE} "
            "about who is credited."
        )
        print("      CREDITS.md is the SSOT. Re-run:")
        print("        python tools/assets/backfill_provenance.py --apply-authors --write")
        for rel, got, want in credit_drift[:20]:
            print(f"        {rel}\n          manifest {got!r} != credits {want!r}")

    # --- the ratchet: the unknown set must be exactly what was pinned ------
    unknown = {rel: rec["sha256"] for rel, rec in assets.items() if rec.get("origin") == "unknown"}

    if args.update_pin:
        PIN.write_text(
            json.dumps(
                {
                    "_why": "Pinned unknown set. Ruled by Pip 2026-08-11: keep the "
                    "unattributable assets, record them honestly, and let a "
                    "mechanism force the question later rather than a document.",
                    "_fails_when": "an asset becomes unknown, or a pinned one is resolved "
                    "or removed. Both directions are worth interrupting for.",
                    "unknown": unknown,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"pinned {len(unknown)} unknown asset(s) -> {PIN.relative_to(REPO)}")
        return 0

    if not PIN.is_file():
        print(
            f"\nRED: no pin at {PIN.relative_to(REPO)}. "
            "Create it with --update-pin once the manifest is trusted."
        )
        return 1

    pinned = json.loads(PIN.read_text(encoding="utf-8")).get("unknown", {})
    appeared = sorted(set(unknown) - set(pinned))
    resolved = sorted(set(pinned) - set(unknown))

    if appeared:
        problems += 1
        print(f"\nFAIL: {len(appeared)} NEW unattributable asset(s). The estate " "got worse.")
        for a in appeared:
            print(f"        {a}")
        print("      Do not pin these away. Find the record, or find out why " "there isn't one.")
    if resolved:
        problems += 1
        print(
            f"\nFAIL: {len(resolved)} pinned unknown(s) no longer unknown " "(resolved or removed)."
        )
        for r in resolved:
            print(f"        {r}")
        print("      Good news, stale pin. Re-run with --update-pin.")

    # --- the Manifund trigger ---------------------------------------------
    human = sorted(
        rel
        for rel, rec in assets.items()
        if rec.get("origin") in NON_MODEL
        and Path(rel).suffix.lower() in ART_EXT
        and not rel.startswith("cats/simple/")  # contributor photos, always were
        and not rel.startswith("cats/default/")  # placeholder markup, always was
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
    print(
        f"OK: {len(assets)} provenanced, {len(unknown)} pinned unknown, " "pack and manifest agree."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
