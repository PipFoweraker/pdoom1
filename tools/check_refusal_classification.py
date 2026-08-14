#!/usr/bin/env python3
"""check_refusal_classification.py -- every NEW player-facing refusal must say whether it
is a rule or a stub.

Layer: PROVE

WHY (playtest 2026-08-14, Pip):
    Onboarding a hire costs 3 Attention. With a full queue on screen, the card's "pull from
    planned work" option refused with "insufficient capacity to handle by cannibalising".
    Pip: "which, like, isn't strictly true? ... if its because we haven't built it, we
    should also say [ALPHA: This behaviour is a stub, harass the developers to extend it!]"

    He was right. MonthPlan.pay_by_cannibalizing() can only free Attention by cancelling
    MonthPlan.queued_strategic entries, and nothing in the shipped game ever writes that
    array -- GameManager.queue_strategic_action() has zero callers. The option could not do
    the thing it named, and the refusal explained a budget instead of an absence.

THE INVARIANT THIS ENFORCES:
    A stub that refuses in the voice of a rule teaches the player a rule that does not
    exist. "You cannot do that" and "we have not built that yet" are different statements:
    the first is worldbuilding, the second is an apology. So every refusal constructed in
    the Godot tree must be CLASSIFIED -- as a real constraint (RULE) or as an unbuilt
    behaviour (STUB, which carries Refusal.ALPHA_STUB_MARKER so the player can tell).

    See godot/scripts/core/refusal.gd for the contract and the two constructors.

HOW A SITE COUNTS AS CLASSIFIED (any one of these):
    * built through the API:   return Refusal.rule("...")  /  Refusal.stub("...")
    * marked in place:         result["message"] = Refusal.mark_stub("...")
    * self-declaring:          {"success": false, ..., "refusal": Refusal.CLASS_STUB}
    * annotated on the site or the line above:   # refusal: rule -- <why>
                                                 # refusal: stub -- <what is missing>
                                                 # refusal: n/a  -- <not player copy>
    The annotation exists for dict literals that carry extra keys the constructors do not
    build. It deliberately requires you to type one of the three tokens, so the
    classification is a CHOICE and never a default. "n/a" is only for a `"success": false`
    that says nothing to a player -- a result TEMPLATE filled in per branch, or a
    programmer/data-error path -- and, like "# scene-nav-allow", it wants a reason after it.

WHY A BASELINE, AND WHY IT CAN ONLY SHRINK:
    There were 93 pre-existing refusal sites when this landed. Annotating all 93 in the
    same change would be a large, low-attention diff -- and, worse, a gate that is RED ON
    ARRIVAL gets --no-verify-ed and then ignored forever (the lesson recorded in
    docs/UI_PLACEHOLDER_AUDIT_2026-07-30.md rec. 3 and the action-taxonomy-index-check
    comment in .pre-commit-config.yaml). So the pre-existing sites are recorded in
    tools/refusal_baseline.txt and this gate is GREEN ON ARRIVAL.

    The ratchet: a site is a violation unless it is classified OR present in the baseline.
    Adding a refusal therefore forces a classification, and CHANGING a baselined refusal's
    wording knocks it out of the baseline -- so touching an old lie makes you classify it
    too. The baseline is regenerated with --write-baseline, which can only be honestly run
    after the count has gone DOWN; --check refuses to write a baseline that grew.

WHAT THIS DOES NOT CATCH (stated so nobody trusts it further than it goes):
    Only the `{"success": false, ...}` Dictionary shape is detected -- that is the one
    unambiguous, machine-findable refusal form in this codebase. Bare rejection strings
    (`error_occurred.emit("Cannot afford ...")`, UI label text, disabled-button tooltips)
    are NOT covered; they are audited by hand. Extending detection to those means teaching
    the scanner which emits are refusals, which is a judgement call, not a regex.

USAGE:
    python tools/check_refusal_classification.py            # scan godot/ (CI mode)
    python tools/check_refusal_classification.py <files...> # pre-commit passes these
    python tools/check_refusal_classification.py --write-baseline
    python tools/check_refusal_classification.py --self-test

    Exit 0 = clean. Exit 1 = at least one unclassified, un-baselined refusal.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT_ROOT = REPO_ROOT / "godot"
BASELINE_PATH = Path(__file__).resolve().parent / "refusal_baseline.txt"

# Directories whose refusals never reach a player: the dev overlays, and the tests that
# assert on refusals rather than emitting them.
EXCLUDED_PARTS = ("addons", "tests", "debug", "dev")

# A refusal site: a Dictionary literal that declares failure. Godot style permits either
# quoting and any spacing.
REFUSAL_RE = re.compile(r"""["']success["']\s*:\s*false""")

# The message string literal on that site, used as the stable baseline key (line numbers
# rot on the first unrelated edit; the sentence does not).
MESSAGE_RE = re.compile(r"""["']message["']\s*:\s*"((?:[^"\\]|\\.)*)\"""")

# Built through the API, or marked in place.
CLASSIFIED_CALL_RE = re.compile(r"\bRefusal\.(rule|stub|mark_stub)\s*\(")

# A Dictionary that names its own kind inline. This is how Refusal's own constructors, and
# any hand-built result that sets result["refusal"], declare themselves.
SELF_DECLARED_RE = re.compile(r"""["']refusal["']\s*:""")

# Inline escape hatch, on the site or the line above it. "n/a" is for a `"success": false`
# that carries no player-facing copy at all -- a result TEMPLATE later filled in per branch,
# or a programmer/data-error path. It still forces you to type a token and a reason, so it
# shows up in review exactly like "# scene-nav-allow" does.
ANNOTATION_RE = re.compile(r"#\s*refusal:\s*(rule|stub|n/a)\b")


def _key(rel: str, message: str) -> str:
    """Baseline key: file plus the refusal's own sentence. Stable across line moves,
    deliberately NOT stable across rewording -- editing a refusal should make you classify
    it.

    The message is JSON-quoted, and that is load-bearing rather than decorative: a plain
    tab-separated key was silently corrupted by pre-commit's trailing-whitespace hook,
    which ate the trailing tab of every empty message and the trailing space of every
    message like "Unknown action: ". Quoting puts the whitespace inside delimiters where no
    whitespace fixer can reach it."""
    return "%s :: %s" % (rel, json.dumps(message))


def scan_text(text: str, rel: str) -> list[tuple[int, str, str]]:
    """Yield (lineno, key, snippet) for every unclassified refusal site in `text`."""
    out: list[tuple[int, str, str]] = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue  # prose about refusals is not a refusal
        if not REFUSAL_RE.search(line):
            continue
        if (
            CLASSIFIED_CALL_RE.search(line)
            or SELF_DECLARED_RE.search(line)
            or ANNOTATION_RE.search(line)
        ):
            continue
        # Look back a few lines: an annotation often sits above a multi-line comment
        # explaining itself, and the explanation is the point.
        if any(ANNOTATION_RE.search(lines[j]) for j in range(max(0, i - 3), i)):
            continue
        m = MESSAGE_RE.search(line)
        message = m.group(1) if m else ""
        out.append((i + 1, _key(rel, message), stripped[:110]))
    return out


def relpath(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def iter_targets(argv: list[str]) -> list[Path]:
    if argv:
        paths = [Path(a) for a in argv if a.endswith(".gd")]
    else:
        paths = sorted(GODOT_ROOT.rglob("*.gd"))
    keep = []
    for p in paths:
        if not p.exists():
            continue  # pre-commit can hand us a deleted file
        parts = set(p.resolve().parts)
        if parts & set(EXCLUDED_PARTS):
            continue
        keep.append(p)
    return keep


def collect(argv: list[str]) -> list[tuple[Path, int, str, str]]:
    found: list[tuple[Path, int, str, str]] = []
    for path in iter_targets(argv):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, key, snippet in scan_text(text, relpath(path)):
            found.append((path, lineno, key, snippet))
    return found


def load_baseline() -> set[str]:
    if not BASELINE_PATH.exists():
        return set()
    keys = set()
    for line in BASELINE_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            keys.add(line)
    return keys


def write_baseline(keys: set[str]) -> int:
    previous = load_baseline()
    if len(keys) > len(previous) and previous:
        print("REFUSED: the baseline may only SHRINK.")
        print("  current unclassified sites: %d, baselined: %d" % (len(keys), len(previous)))
        print("  Classify the new refusals instead of re-baselining them.")
        return 1
    header = (
        "# Pre-existing UNCLASSIFIED refusal sites (tools/check_refusal_classification.py).\n"
        '# Format: <path> :: "<message literal>". This list may only SHRINK: classify a\n'
        "# site with Refusal.rule()/Refusal.stub() or a '# refusal: rule -- why' annotation\n"
        "# and regenerate. See godot/scripts/core/refusal.gd for the contract.\n"
    )
    BASELINE_PATH.write_text(header + "\n".join(sorted(keys)) + "\n", encoding="utf-8")
    print("Wrote %s (%d entries, was %d)." % (relpath(BASELINE_PATH), len(keys), len(previous)))
    return 0


SELF_TEST_CLEAN = """
static func a() -> Dictionary:
	return Refusal.rule("No desk. Get a bigger office.")

static func b() -> Dictionary:
	return Refusal.stub("Delegation is not wired up.")

static func c() -> Dictionary:
	# refusal: rule -- the office cap is a real hard cap (#791)
	return {"success": false, "message": "No desk.", "code": 3}

static func d() -> Dictionary:
	return {"success": false, "message": "Already onboarded.", "x": 1}  # refusal: rule -- idempotence

static func e() -> Dictionary:
	return {"success": false, "message": "No WIP to eat.", "refusal": Refusal.CLASS_STUB}

static func f() -> Dictionary:
	# refusal: n/a -- result template; every failure branch below sets its own kind
	var out := {"success": false, "message": ""}
	return out
"""

SELF_TEST_DIRTY = """
static func e() -> Dictionary:
	return {"success": false, "message": "Insufficient capacity to handle by cannibalizing"}
"""


def self_test() -> int:
    """Prove the checker can return BOTH answers (CLAUDE.md: a published command must be
    shown capable of returning the other answer)."""
    ok = True

    clean = scan_text(SELF_TEST_CLEAN, "self_test.gd")
    if clean:
        ok = False
        print("SELF-TEST FAIL: classified refusals were flagged: %r" % (clean,))
    else:
        print("  [ok] all six classification forms pass clean")
        print("       (rule / stub / annotation above / annotation inline / self-declared / n/a)")

    dirty = scan_text(SELF_TEST_DIRTY, "self_test.gd")
    if len(dirty) != 1:
        ok = False
        print("SELF-TEST FAIL: expected 1 unclassified refusal, got %d" % len(dirty))
    else:
        if dirty[0][1] != _key("self_test.gd", "Insufficient capacity to handle by cannibalizing"):
            ok = False
            print("SELF-TEST FAIL: wrong baseline key: %r" % (dirty[0][1],))
        else:
            print("  [ok] an unclassified refusal is caught, keyed by its own sentence")

    prose = scan_text('# a comment mentioning {"success": false, "message": "x"}\n', "self_test.gd")
    if prose:
        ok = False
        print("SELF-TEST FAIL: a comment about refusals was treated as one")
    else:
        print("  [ok] prose about refusals is not mistaken for a refusal")

    print("SELF-TEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()

    if "--write-baseline" in argv:
        argv = [a for a in argv if a != "--write-baseline"]
        return write_baseline({key for _, _, key, _ in collect(argv)})

    baseline = load_baseline()
    found = collect(argv)
    violations = [(p, ln, key, snip) for p, ln, key, snip in found if key not in baseline]

    if not violations:
        print(
            "[refusal-class] OK: %d refusal site(s) scanned, %d classified or baselined."
            % (len(found), len(found))
        )
        return 0

    print("ERROR: unclassified player-facing refusal(s).")
    print("       A stub that refuses in the voice of a rule teaches the player a rule that")
    print("       does not exist. Say which one this is.")
    print()
    for path, lineno, _key_, snippet in violations:
        print("  %s:%d: %s" % (relpath(path), lineno, snippet))
    print()
    print("%d violation(s). Fix by one of:" % len(violations))
    print('  return Refusal.rule("...")        -- a real constraint, ships unmarked')
    print('  return Refusal.stub("...")        -- unbuilt; carries the [ALPHA: ...] marker')
    print("  # refusal: rule -- <why>          -- annotate the line (or the line above)")
    print("See godot/scripts/core/refusal.gd. Do NOT re-baseline: the baseline only shrinks.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
