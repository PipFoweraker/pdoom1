#!/usr/bin/env python3
"""Guard: shipped images must not silently lose their C2PA content credential.

Layer: PROVE

WHAT A CREDENTIAL IS, AND WHY THIS GUARD EXISTS
-----------------------------------------------
The OpenAI Images API returns PNGs carrying a signed C2PA manifest in a `caBX`
ancillary chunk. Measured 2026-08-15 on a live `gpt-image-1` call: 29,030 bytes
asserting IPTC `digitalSourceType=trainedAlgorithmicMedia`, claim generator
"OpenAI Media Service API", chained to SSL.com C2PA ICA R1 with an RFC3161
timestamp.

That is a far stronger disclosure than any caption this project could write: a
stranger can verify it without trusting us. It is also fragile in a specific,
silent way -- PIL drops unknown ancillary chunks on re-encode, so a single
`Image.open(...).save(...)` deletes it and leaves a byte-for-byte plausible
image behind. `generate_images.py` and `run_art_night.py` did exactly that for
roughly 1,600 masters before 2026-08-15. Those cannot be retro-signed: the
signature covers pixels that no longer have a witness.

So the loss mode is: invisible, irreversible, and produced by a one-line change
anyone might make while tidying. That is precisely the shape this estate has
already been burned by (issue #640, the stale class cache, the hollow CI gate).
It gets a detector.

WHY A RATCHET ON THE *CREDENTIALED* SET, NOT THE UNCREDENTIALED ONE
--------------------------------------------------------------------
The obvious guard -- "fail while any image lacks a credential" -- would sit
permanently red over ~4,900 legacy files, and this estate has ruled on what
that is worth:

    "A guard always red and a guard always green fail identically -- neither
     carries information."   -- SUBMISSION_2026-08-09_four-patterns.md

So the pin records the images that DO carry a credential, and the guard fails
when that set changes in either direction:

  * a pinned image LOSES its credential   -> a regression, loudly. This is the
    fix being undone by a well-meaning re-encode somewhere downstream.
  * an unpinned image GAINS one           -> the pin is stale, update it.

The second direction is not an error in spirit -- it is the programme WORKING.
Each `--update-pin` commit is a dated record of the shipped set becoming more
honest, which is the thing the Manifund copy commitment will eventually need
someone to be able to point at. It exits 1 anyway, because a silent success is
still a silent change to a disclosure claim.

SCOPE: SHIPPED ASSETS ONLY
--------------------------
The pin covers `godot/assets/` -- what players and the website actually get.
`art_source/` is a working area that churns by the hundred per art night;
pinning it would make the guard a nuisance and nuisances get bypassed. It is
still REPORTED, never gated, so the numbers stay visible.

Usage:
  python tools/assets/check_credentials.py              # audit, exit 1 on drift
  python tools/assets/check_credentials.py --update-pin # accept current state
  python tools/assets/check_credentials.py --self-test  # prove the detector works
  python tools/assets/check_credentials.py --report     # observe only, never fails
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SHIPPED = REPO / "godot" / "assets"
WORKING = REPO / "art_source"
PIN = Path(__file__).resolve().parent / "credentialed_pin.json"

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
C2PA_CHUNK = b"caBX"

# IPTC Digital Source Type terms we expect to see inside a credential. Kept here
# so the vocabulary is greppable from the guard rather than only in prose.
# See docs/art/MOTIF_AND_WATERMARK_PROTOCOL.md and cv.iptc.org/newscodes/digitalsourcetype.
IPTC_PREFIX = b"cv.iptc.org/newscodes/digitalsourcetype/"

# The closed vocabulary, verified against cv.iptc.org/newscodes/digitalsourcetype
# on 2026-08-15. Matched longest-first: the credential is CBOR, so the term is not
# delimited by anything we can rely on, and scraping "letters until they stop" runs
# straight past the term into the next key. An unrecognised term is reported AS
# unrecognised rather than guessed at -- a wrong-but-plausible source type is worse
# than none, because it would be quoted as a disclosure.
IPTC_TERMS = (
    "compositeWithTrainedAlgorithmicMedia",
    "trainedAlgorithmicMedia",
    "algorithmicallyEnhanced",
    "compositeSynthetic",
    "computationalCapture",
    "dataDrivenMedia",
    "virtualRecording",
    "compositeCapture",
    "digitalCreation",
    "algorithmicMedia",
    "digitalCapture",
    "screenCapture",
    "negativeFilm",
    "positiveFilm",
    "humanEdits",
    "composite",
    "print",
)


def read_c2pa_box(data: bytes) -> bytes | None:
    """Return the raw `caBX` chunk payload, or None if the PNG carries no credential.

    Walks the chunk table rather than searching for the marker, so a `caBX`
    byte-sequence that happens to occur inside compressed image data cannot
    produce a false positive.
    """
    if data[:8] != PNG_MAGIC:
        return None
    i = 8
    while i + 8 <= len(data):
        (length,) = struct.unpack(">I", data[i : i + 4])
        ctype = data[i + 4 : i + 8]
        if ctype == C2PA_CHUNK:
            return data[i + 8 : i + 8 + length]
        if ctype == b"IEND":
            return None
        i += 12 + length
    return None


def read_c2pa_box_streaming(path: Path) -> bytes | None:
    """Same answer as read_c2pa_box, without loading the file.

    Walks the chunk table by reading 8-byte headers and SEEKING past payloads,
    so cost is O(number of chunks), not O(file size). The naive version read
    every byte of every PNG: over `art_source` that is ~4 GB of reads per run
    and it blew a 120-second timeout on the first real invocation. A guard slow
    enough to time out is a guard that gets removed from pre-commit.

    `caBX` sits immediately after IHDR in practice, so the loop almost always
    exits after two headers.
    """
    try:
        with path.open("rb") as fh:
            if fh.read(8) != PNG_MAGIC:
                return None
            while True:
                header = fh.read(8)
                if len(header) < 8:
                    return None
                (length,) = struct.unpack(">I", header[:4])
                ctype = header[4:8]
                if ctype == C2PA_CHUNK:
                    return fh.read(length)
                if ctype == b"IEND":
                    return None
                fh.seek(length + 4, 1)  # payload + CRC
    except OSError:
        return None


def credential_of(path: Path) -> dict | None:
    """Describe the credential on `path`, or None. Never raises on bad files."""
    box = read_c2pa_box_streaming(path)
    if box is None:
        return None
    source_type = ""
    idx = box.find(IPTC_PREFIX)
    if idx != -1:
        tail = box[idx + len(IPTC_PREFIX) :]
        # Longest-first is REQUIRED, not cosmetic: "composite" is a prefix of
        # "compositeSynthetic", "compositeCapture" and
        # "compositeWithTrainedAlgorithmicMedia". Sorted here rather than trusted
        # to the literal's order, which drifts the moment someone adds a term.
        for term in sorted(IPTC_TERMS, key=len, reverse=True):
            if tail.startswith(term.encode("ascii")):
                source_type = term
                break
        else:
            source_type = "UNRECOGNISED"
    return {
        "bytes": len(box),
        "sha256": hashlib.sha256(box).hexdigest(),
        "digital_source_type": source_type,
    }


def scan(root: Path) -> dict[str, dict]:
    """Map repo-relative posix path -> credential, for every credentialed PNG under root."""
    found = {}
    if not root.exists():
        return found
    for path in sorted(root.rglob("*.png")):
        cred = credential_of(path)
        if cred is not None:
            found[path.relative_to(REPO).as_posix()] = cred
    return found


def load_pin() -> dict[str, dict]:
    if not PIN.exists():
        return {}
    return json.loads(PIN.read_text(encoding="utf-8")).get("credentialed", {})


def write_pin(found: dict[str, dict]) -> None:
    doc = {
        "_why": (
            "Pinned set of shipped images carrying a signed C2PA content credential. "
            "The guard fails when this set changes in either direction: a loss is a "
            "regression, a gain is a stale pin. See tools/assets/check_credentials.py."
        ),
        "_fails_when": (
            "a pinned image loses its credential, or an unpinned shipped image gains one"
        ),
        "_regenerate": "python tools/assets/check_credentials.py --update-pin",
        "count": len(found),
        "credentialed": found,
    }
    # newline="" forces LF -- see the note in scripts/generate_rulings.py: the
    # Windows default writes CRLF, the mixed-line-ending hook rewrites it, and a
    # --check comparison fails against a file it just generated.
    PIN.write_text(
        json.dumps(doc, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline=""
    )


def report(found: dict[str, dict]) -> None:
    total = len(list(SHIPPED.rglob("*.png"))) if SHIPPED.exists() else 0
    working_total = len(list(WORKING.rglob("*.png"))) if WORKING.exists() else 0
    working_cred = len(scan(WORKING))
    print(f"shipped  {SHIPPED.relative_to(REPO).as_posix()}: {len(found)}/{total} credentialed")
    print(
        f"working  {WORKING.relative_to(REPO).as_posix()}: "
        f"{working_cred}/{working_total} credentialed (reported, never gated)"
    )
    for rel, cred in sorted(found.items()):
        dst = cred["digital_source_type"] or "(no IPTC term found)"
        print(f"  {rel}  {cred['bytes']}B  {dst}")


def audit() -> int:
    pinned = load_pin()
    found = scan(SHIPPED)

    lost = {r: pinned[r] for r in pinned if r not in found}
    gained = {r: found[r] for r in found if r not in pinned}
    changed = {
        r: (pinned[r]["sha256"], found[r]["sha256"])
        for r in pinned
        if r in found and pinned[r]["sha256"] != found[r]["sha256"]
    }

    report(found)
    print()

    if not PIN.exists():
        print("[!] no pin file yet. Establish one with --update-pin.")
        return 1

    if not (lost or gained or changed):
        print(f"[OK] {len(found)} credentialed shipped image(s), all pinned, none lost.")
        return 0

    if lost:
        print("[FAIL] credential LOST -- something re-encoded a signed image:")
        for rel in sorted(lost):
            print(f"  - {rel}")
        print("       This is irreversible. The image cannot be retro-signed.")
        print("       Find the re-encode (usually a PIL Image.save) before updating the pin.")
    if gained:
        print("[FAIL] credential GAINED -- the pin is stale. This is good news:")
        for rel in sorted(gained):
            print(f"  + {rel}  {gained[rel]['digital_source_type']}")
        print("       Accept with: python tools/assets/check_credentials.py --update-pin")
    if changed:
        print("[FAIL] credential REPLACED -- same path, different manifest:")
        for rel in sorted(changed):
            print(f"  ~ {rel}")
        print("       Expected if the asset was regenerated. Accept with --update-pin.")
    return 1


def self_test() -> int:
    """Prove the detector can return BOTH answers, on synthetic bytes.

    A guard nobody has watched fail is not known to work (issue #640). This
    builds a minimal PNG, asserts no credential is seen; injects a `caBX`
    chunk, asserts one IS seen; then round-trips it the way the old pipeline
    did and asserts the credential is gone again.
    """
    import zlib
    from io import BytesIO

    def chunk(ctype: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + ctype
            + payload
            + struct.pack(">I", zlib.crc32(ctype + payload) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    idat = zlib.compress(b"\x00\x00\x00\x00\x00")
    plain = PNG_MAGIC + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")

    fake_box = b"jumbc2pa" + IPTC_PREFIX + b"trainedAlgorithmicMedia" + b"\x00" * 32
    signed = (
        PNG_MAGIC
        + chunk(b"IHDR", ihdr)
        + chunk(C2PA_CHUNK, fake_box)
        + chunk(b"IDAT", idat)
        + chunk(b"IEND", b"")
    )

    failures = []

    if read_c2pa_box(plain) is not None:
        failures.append("FALSE POSITIVE: found a credential in a plain PNG")
    box = read_c2pa_box(signed)
    if box is None:
        failures.append("FALSE NEGATIVE: missed a credential that is present")
    elif box != fake_box:
        failures.append("payload mismatch: extracted the wrong bytes")

    # A `caBX` byte-run inside image data must NOT be mistaken for a chunk.
    # Level 0 (stored) keeps the literal bytes in the file; default compression
    # would encode them away and leave this case testing nothing. The fixture is
    # asserted, not assumed -- a decoy test with no decoy in it is worse than no
    # test, because it reads as coverage.
    decoy_idat = zlib.compress(b"\x00" + C2PA_CHUNK, 0)
    decoy = PNG_MAGIC + chunk(b"IHDR", ihdr) + chunk(b"IDAT", decoy_idat) + chunk(b"IEND", b"")
    if C2PA_CHUNK not in decoy:
        failures.append("BROKEN FIXTURE: the decoy does not contain the decoy bytes")
    elif read_c2pa_box(decoy) is not None:
        failures.append("FALSE POSITIVE: matched a caBX byte-run inside IDAT")

    # The original loss, reproduced: PIL re-encode must destroy it.
    try:
        from PIL import Image

        buf = BytesIO()
        Image.open(BytesIO(signed)).convert("RGBA").save(buf, format="PNG")
        if read_c2pa_box(buf.getvalue()) is not None:
            failures.append(
                "CONTROL DID NOT REPRODUCE THE BUG: PIL kept the chunk, so this "
                "guard proves nothing about the failure it was written for"
            )
    except ImportError:
        print("[self-test] SKIP  PIL control (Pillow not installed)")

    if failures:
        print("[self-test] FAIL:")
        for f in failures:
            print("  -", f)
        return 1
    print("[self-test] PASS: blind to plain PNGs, sees real chunks, ignores decoy byte-runs,")
    print("            and reproduces the PIL re-encode loss it exists to catch.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--update-pin", action="store_true", help="accept the current set")
    ap.add_argument("--self-test", action="store_true", help="prove the detector works")
    ap.add_argument("--report", action="store_true", help="observe only, always exits 0")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.report:
        report(scan(SHIPPED))
        return 0
    if args.update_pin:
        found = scan(SHIPPED)
        write_pin(found)
        print(f"pinned {len(found)} credentialed shipped image(s) -> {PIN.name}")
        return 0
    return audit()


if __name__ == "__main__":
    sys.exit(main())
