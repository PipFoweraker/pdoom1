#!/usr/bin/env python3
"""Census the Balance surface in BOTH directions, because nothing else does.

Layer: PROVE -- direction 1 FAILS the build. Direction 2 ratchets.

WHY THIS EXISTS, 2026-08-23
---------------------------
`Balance.num(key, fallback)` returns the fallback for a key that does not
exist. That is deliberate and it is why unconfigured builds never crash. It is
also sighting #1 in docs/design/SILENT_FAILURE_REGISTER.md -- the generator
behind at least four of the fifteen confirmed silent failures in this estate:

  #2  doom.streams.upgrade_cat_alarm  read at upgrades.gd:143, never defined.
      The cat's alarm effect silently uses a hardcoded 5.0. All THIRTY sibling
      keys under doom.streams are defined; this one is not, so anyone reading
      defaults.json to understand the doom model concludes the cat has no
      mechanical effect at all.
  #3  13 of 273 leaf keys defined and never read, including a doom.legacy_*
      model anyone tuning doom would assume is live.
  #4  Two keys INVENTED during review and never noticed, because the feature
      "worked" -- it worked on fallbacks (#1276).

Every existing guard in this repo points at code. The balance surface is the
one place with no gate in either direction, and it is therefore the surface
this defect class has colonised.

THE COUNTER IS CENSUS, NOT VIGILANCE
------------------------------------
The register argues this at length and it decides the design here: if each
failure is individually sub-threshold, per-instance detection cannot work by
construction. There is no event to notice. What works is enumerating the whole
surface and diffing the two directions -- which takes about a second and found
sightings #2 and #3 after a weekend of nobody seeing them.

TWO DIRECTIONS, DELIBERATELY ASYMMETRIC
---------------------------------------
**READ BUT NOT DEFINED -> FAIL.** A live silent fallback. There is no benign
version: either the key should exist, or the call should not. This blocks.

**DEFINED BUT NOT READ -> RATCHET.** Genuinely ambiguous. It may be staged
config for an unlanded feature, or a scenario override, or dead weight from a
superseded model. Deleting it automatically would be worse than leaving it. So
the count may FALL and never RISE, exactly like tools/check_font_sizes.py.
A ratchet converts an unbounded mess into a bounded one without requiring
anybody to adjudicate 13 keys today.

THE FALSE-POSITIVE PROBLEM, WHICH IS THE WHOLE DIFFICULTY
---------------------------------------------------------
A naive scan reports eight missing keys and six are noise:

    Balance.num("financing." + key, ...)          -> literal "financing."
    Balance.num("ledger.promise.%s.fuse_turns")   -> a format string

A checker that cries wolf on its first run is a checker somebody disables in
week two, and then the surface is unguarded AND believed guarded -- which is
strictly worse than today. So composed keys are excluded structurally (a
trailing dot, or a `%` placeholder) rather than by an allowlist that would rot.

DYNAMIC_PREFIXES below is for the residue: prefixes whose leaves are assembled
at runtime from values this scanner cannot enumerate. Each entry states why.
Adding one is a claim, and the claim is visible in review.

EXIT CODES -- THREE, NOT TWO
    0  measured pass.
    1  measured failure (a live silent fallback, or the ratchet rose).
    2  COULD NOT MEASURE -- defaults.json is missing, so there is no census. This is
       not a pass and it is not a finding; anything that reports it as either is
       asserting a result from a run that established nothing.

USAGE
    python tools/check_balance_keys.py             # census, human-readable
    python tools/check_balance_keys.py --check     # gate: exit 1 on direction 1
    python tools/check_balance_keys.py --json      # machine-readable
    python tools/check_balance_keys.py --self-test # prove BOTH directions still work

WHY --self-test EXISTS (added 2026-08-24, issue #1265)
    The first draft of this file listed "doom.streams." in DYNAMIC_PREFIXES and thereby
    reported "no live silent fallbacks" while doom.streams.upgrade_cat_alarm -- the
    sighting the tool was built for -- sat undefined three lines away. That failure mode
    is invisible from the outside: a suppressed gate and a satisfied gate print the same
    line. The self-test pins it directly: direction 1 must still catch a key that sits
    under a DYNAMIC_PREFIXES entry. If someone "fixes a false positive" by widening that
    list, this goes red instead of going quiet.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = ROOT / "godot" / "data" / "balance" / "defaults.json"
GODOT = ROOT / "godot"
RATCHET_FILE = ROOT / "tools" / "balance_unread_ratchet.txt"

# Prefixes whose LEAVES are composed at runtime, so a definition under them is
# reachable even though no literal names it.
#
# THIS LIST SUPPRESSES DIRECTION 2 ONLY. It is never consulted for direction 1 --
# see the comment there for the bug that taught us why. Each entry MUST carry a
# reason, because this is the list that decides what the census cannot see, and
# an unexplained entry is an unexamined hole.
#
# Note what is NOT here: "doom.streams." The first draft listed it and thereby
# hid the very sighting the tool was built for.
DYNAMIC_PREFIXES = {
    "financing.instruments.": "keyed by instrument id from defaults.json itself",
    "financing.org_factors.": "keyed by org type at runtime (finance_engine.gd:111)",
    "financing.counterparty_factors.": "keyed by counterparty at runtime (:112, :230)",
    "ledger.promise.": "keyed by promise id via a %s format string (ledger.gd:156-167)",
}

CALL = re.compile(r'Balance\.(?:num|inum|table|get|has)\(\s*"([^"]+)"')


def leaves(d: dict, pre: str = "") -> set[str]:
    """Leaf paths only. `_description` keys are documentation, not tunables."""
    out: set[str] = set()
    for k, v in d.items():
        if k.startswith("_"):
            continue
        key = f"{pre}{k}"
        if isinstance(v, dict):
            out |= leaves(v, key + ".")
        else:
            out.add(key)
    return out


def all_paths(d: dict, pre: str = "") -> set[str]:
    """Every path including intermediate dicts -- Balance.table() reads those."""
    out: set[str] = set()
    for k, v in d.items():
        if k.startswith("_"):
            continue
        key = f"{pre}{k}"
        out.add(key)
        if isinstance(v, dict):
            out |= all_paths(v, key + ".")
    return out


def gd_sources() -> list[Path]:
    return [f for f in GODOT.rglob("*.gd") if "addons" not in f.parts and "tests" not in f.parts]


def is_composed(key: str) -> bool:
    """Structural exclusion, not an allowlist -- these cannot rot."""
    return key.endswith(".") or "%" in key or key == ""


def scan_reads() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for f in gd_sources():
        rel = f.relative_to(ROOT).as_posix()
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            for m in CALL.finditer(line):
                found.setdefault(m.group(1), []).append(f"{rel}:{i}")
    return found


def under_dynamic_prefix(key: str, prefixes=None) -> str | None:
    for p in DYNAMIC_PREFIXES if prefixes is None else prefixes:
        if key.startswith(p) and key != p:
            return p
    return None


def adjudicate(data: dict, reads: dict, src: str, prefixes=None):
    """The whole decision, with nothing read from disk.

    Split out of main() so --self-test can drive it with synthetic inputs. Returns
    (defined_leaves, missing, unread). `prefixes` overrides DYNAMIC_PREFIXES and
    exists ONLY so the self-test can prove direction 1 ignores it.
    """
    defined_leaves = leaves(data)
    defined_all = all_paths(data)

    # --- direction 1: read but not defined -------------------------------
    #
    # DYNAMIC_PREFIXES is deliberately NOT consulted here, and the first draft of
    # this file got that wrong in the most instructive way possible: it listed
    # "doom.streams." as dynamic, which suppressed the entire namespace and made
    # the checker report "no live silent fallbacks" while
    # doom.streams.upgrade_cat_alarm -- the sighting that motivated the tool --
    # sat undefined three lines away. A gate with a hole in it is worse than no
    # gate, because the surface is then unguarded AND believed guarded.
    #
    # The exclusion direction 1 needs is STRUCTURAL and already applied:
    # is_composed() catches the literal a concatenation leaves behind (a trailing
    # dot) and format strings (a % placeholder). A key with a real leaf name is
    # always a real lookup, whatever namespace it sits in.
    missing: dict[str, list[str]] = {}
    for key, locs in reads.items():
        if is_composed(key) or key in defined_all:
            continue
        missing[key] = locs

    # --- direction 2: defined but never read -----------------------------
    unread: list[str] = []
    for key in sorted(defined_leaves):
        if key in reads:
            continue
        if under_dynamic_prefix(key, prefixes):
            continue
        leaf = key.rsplit(".", 1)[-1]
        # A leaf name appearing anywhere in source counts as reachable: it may be
        # composed. Conservative ON PURPOSE -- direction 2 ratchets, so a false
        # "reachable" costs a missed cleanup, while a false "unread" would put
        # noise in a gate and gates with noise get switched off.
        if f'"{leaf}"' in src or f".{leaf}" in src:
            continue
        unread.append(key)

    return defined_leaves, missing, unread


def self_test() -> int:
    """Prove the census can return BOTH answers in BOTH directions."""
    ok = True

    def check(label, cond, detail=""):
        nonlocal ok
        if cond:
            print("  [ok] %s" % label)
        else:
            ok = False
            print("SELF-TEST FAIL: %s %s" % (label, detail))

    # Shaped like defaults.json around the real sighting: a doom.streams namespace
    # with siblings defined, and one key that is read and never defined.
    data = {
        "_description": "documentation, not a tunable",
        "doom": {
            "streams": {"baseline": 1.0, "compute_pressure": 2.0},
            "legacy_curve": 0.5,
        },
        "financing": {"instruments": {"seed": {"cap": 10}}},
        "ledger": {"promise": {"grant_a": {"fuse_turns": 3}}},
    }
    src_clean = 'Balance.num("doom.streams.baseline", 1.0)\n'

    # SIGHTING #2, verbatim: read at upgrades.gd:143, defined nowhere.
    reads = {
        "doom.streams.baseline": ["godot/scripts/core/doom_system.gd:10"],
        "doom.streams.upgrade_cat_alarm": ["godot/scripts/core/upgrades.gd:143"],
        # The two false-positive shapes that must NEVER be reported: a literal
        # left behind by concatenation, and a format string.
        "financing.": ["godot/scripts/core/finance_engine.gd:111"],
        "ledger.promise.%s.fuse_turns": ["godot/scripts/core/ledger.gd:156"],
    }

    _, missing, _ = adjudicate(data, reads, src_clean)
    check(
        "direction 1 catches sighting #2 (doom.streams.upgrade_cat_alarm) and only it",
        list(missing) == ["doom.streams.upgrade_cat_alarm"],
        repr(sorted(missing)),
    )
    check(
        'the composed shapes ("financing." and a %s format string) are NOT reported',
        "financing." not in missing and "ledger.promise.%s.fuse_turns" not in missing,
    )

    # THE REGRESSION THAT MATTERS. Suppressing the whole namespace must not
    # suppress direction 1 -- that is exactly the bug the first draft shipped.
    _, missing_sup, _ = adjudicate(
        data, reads, src_clean, prefixes={"doom.streams.": "pretend this is dynamic"}
    )
    check(
        "direction 1 STILL catches it when doom.streams. is declared dynamic",
        list(missing_sup) == ["doom.streams.upgrade_cat_alarm"],
        repr(sorted(missing_sup)),
    )

    # The other answer: a defaults file that defines what is read reports nothing.
    data_fixed = json.loads(json.dumps(data))
    data_fixed["doom"]["streams"]["upgrade_cat_alarm"] = 5.0
    _, missing_none, _ = adjudicate(data_fixed, reads, src_clean)
    check("direction 1 goes GREEN once the key is defined", missing_none == {}, repr(missing_none))

    # Direction 2, both answers.
    _, _, unread = adjudicate(data, reads, src_clean)
    check(
        "direction 2 reports doom.legacy_curve (sighting #3's shape) as unread",
        "doom.legacy_curve" in unread,
        repr(unread),
    )
    check(
        "direction 2 does NOT report keys under a declared dynamic prefix",
        not any(k.startswith("financing.instruments.") for k in unread)
        and not any(k.startswith("ledger.promise.") for k in unread),
        repr(unread),
    )
    _, _, unread_seen = adjudicate(data, reads, src_clean + '"legacy_curve"\n')
    check(
        "a leaf name appearing in source is treated as reachable (composed reads)",
        "doom.legacy_curve" not in unread_seen,
        repr(unread_seen),
    )
    check("_description keys are documentation, never tunables", "_description" not in str(unread))

    # The regex is the other half of direction 1: a key nobody parses is a key
    # nobody can miss.
    hits = CALL.findall(
        'Balance.num("a.b", 1.0) Balance.inum("c.d", 2) Balance.table("e") Balance.has("f")'
    )
    check(
        "the call regex sees num/inum/table/has",
        hits == ["a.b", "c.d", "e", "f"],
        repr(hits),
    )

    print("SELF-TEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def load_ratchet() -> int:
    if RATCHET_FILE.is_file():
        try:
            return int(RATCHET_FILE.read_text(encoding="utf-8").split("#")[0].strip())
        except ValueError:
            pass
    return 10**6


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--check", action="store_true", help="gate mode: exit 1 on a live silent fallback"
    )
    ap.add_argument("--json", dest="as_json", action="store_true")
    ap.add_argument(
        "--write-ratchet",
        action="store_true",
        help="record the current unread count as the new ceiling",
    )
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="prove the census can still return BOTH answers in BOTH directions",
    )
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if not DEFAULTS.is_file():
        # Exit 2, NOT 1: there is no census, so there is no finding. Callers must
        # keep these apart -- reporting 2 as 1 asserts a result from a run that
        # measured nothing.
        print("[balance] CANNOT RUN: %s missing" % DEFAULTS, file=sys.stderr)
        return 2

    data = json.loads(DEFAULTS.read_text(encoding="utf-8"))
    reads = scan_reads()
    src = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in gd_sources())
    defined_leaves, missing, unread = adjudicate(data, reads, src)

    ceiling = load_ratchet()

    if args.as_json:
        print(
            json.dumps(
                {
                    "defined_leaves": len(defined_leaves),
                    "reads": len(reads),
                    "read_but_undefined": missing,
                    "defined_but_unread": unread,
                    "ratchet_ceiling": ceiling,
                },
                indent=2,
            )
        )
    else:
        print("[balance] census of %s" % DEFAULTS.relative_to(ROOT))
        print("  leaf keys defined : %d" % len(defined_leaves))
        print("  distinct lookups  : %d" % len(reads))
        print()
        if missing:
            print("  READ BUT NOT DEFINED -- %d live silent fallback(s):" % len(missing))
            for k in sorted(missing):
                print("    %s" % k)
                for loc in missing[k][:3]:
                    print("        %s" % loc)
            print()
            print("  Each of these silently returns its hardcoded fallback. The value")
            print("  cannot be tuned from data, and a reader of defaults.json would")
            print("  conclude the mechanic does not exist.")
        else:
            print("  READ BUT NOT DEFINED : none. No live silent fallbacks.")
        print()
        print("  DEFINED BUT NEVER READ : %d (ceiling %s)" % (len(unread), ceiling))
        for k in unread[:20]:
            print("    %s" % k)
        if len(unread) > 20:
            print("    ... and %d more" % (len(unread) - 20))
        print()
        print("  Direction 2 RATCHETS: the count may fall, never rise. These are")
        print("  ambiguous by nature -- staged config, scenario overrides, or a")
        print("  superseded model -- so this reports rather than adjudicates.")

    if args.write_ratchet:
        RATCHET_FILE.write_text(
            "%d  # defined-but-unread balance keys. May FALL, never RISE.\n"
            "# Lower it when you delete dead config; never raise it to make a\n"
            "# commit pass. See tools/check_balance_keys.py and\n"
            "# docs/design/SILENT_FAILURE_REGISTER.md sighting #3.\n" % len(unread),
            encoding="utf-8",
            newline="\n",
        )
        print("\n[balance] ratchet set to %d" % len(unread))
        return 0

    if args.check:
        rc = 0
        if missing:
            print(
                "\n[balance] FAIL: %d key(s) read but never defined." % len(missing),
                file=sys.stderr,
            )
            print("  Define them in defaults.json, or stop reading them.", file=sys.stderr)
            rc = 1
        if len(unread) > ceiling:
            print(
                "\n[balance] FAIL: defined-but-unread rose %d -> %d." % (ceiling, len(unread)),
                file=sys.stderr,
            )
            print("  The ratchet only falls. Read the key, or do not add it.", file=sys.stderr)
            rc = 1
        if rc == 0:
            print(
                "\n[balance] OK: no live silent fallbacks; unread %d <= %d."
                % (len(unread), ceiling)
            )
        return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
