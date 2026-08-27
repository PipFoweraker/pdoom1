#!/usr/bin/env python3
"""Guard: the client and the server must agree on the board-name budget.

Layer: PROVE -- this gate FAILS the commit.

WHY THIS EXISTS. The leaderboard's name budget lived in two files that had no
way to notice each other:

  * ``server/leaderboard/score_api.php`` cut ``player_name`` at 40 bytes with a
    byte-wise ``substr``;
  * ``godot/scripts/leaderboard.gd`` carried its own ``BOARD_NAME_MAX_BYTES``,
    copied from a MEASUREMENT of the deployed server rather than from the file
    two directories away -- its comment even asserted, wrongly, that
    ``score_api.php`` "lives on the server and is in no repo here".

Because the client believed the number was external it never questioned it, and
because nothing compared the two, the number could drift in either direction
without a sound. What it produced on the live weekly-2026-w33 board was
``"Bureau of Catastrophe... -- Pip"`` -- a player's lab name shortened, with the
literal ``...`` stored as data, discovered by reading the public board.

The two numbers disagreeing IS the defect class. This compares them.

WHAT IT CHECKS
1. ``$MAX_NAME_BYTES`` in the PHP equals ``BOARD_NAME_MAX_BYTES`` in the
   GDScript. Client > server means the server silently amputates again; client
   < server means the client silently truncates names the server would have
   accepted. Both are the same bug wearing different hats, so this is ``==``.
2. ``BOARD_NAME_MAX_BYTES`` is still DERIVED from the two input-field caps and
   not re-frozen into a literal. A hand-picked budget is what let 40 masquerade
   as a law of nature; if the derivation is edited away, the guarantee that a
   typed name is never altered goes with it.

The field caps themselves, and the generator that has to fit inside them, are
pinned on the Godot side by
``godot/tests/unit/test_leaderboard_identity_fields.gd``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GD_PATH = REPO_ROOT / "godot" / "scripts" / "leaderboard.gd"
PHP_PATH = REPO_ROOT / "server" / "leaderboard" / "score_api.php"


def _gd_int_const(src: str, name: str) -> int:
    """Read `const NAME := <int>` out of the GDScript."""
    m = re.search(rf"^const\s+{re.escape(name)}\s*:=\s*(\d+)\s*$", src, re.M)
    if m is None:
        raise LookupError(f"could not find `const {name} := <int>` in {GD_PATH}")
    return int(m.group(1))


def main() -> int:
    problems: list[str] = []

    for path in (GD_PATH, PHP_PATH):
        if not path.is_file():
            print(f"[board-budget] missing file: {path}", file=sys.stderr)
            return 1

    gd = GD_PATH.read_text(encoding="utf-8")
    php = PHP_PATH.read_text(encoding="utf-8")

    try:
        lab = _gd_int_const(gd, "LAB_NAME_MAX_CHARS")
        operator = _gd_int_const(gd, "OPERATOR_NAME_MAX_CHARS")
        per_char = _gd_int_const(gd, "MAX_UTF8_BYTES_PER_CHAR")
        sep_bytes = _gd_int_const(gd, "BOARD_NAME_SEPARATOR_BYTES")
    except LookupError as exc:
        print(f"[board-budget] {exc}", file=sys.stderr)
        return 1

    derived = (lab + operator) * per_char + sep_bytes

    # Check 2: the budget must still be an expression over those constants, not
    # a literal someone "simplified" back into place.
    budget_decl = re.search(
        r"^const\s+BOARD_NAME_MAX_BYTES\s*:=\s*(.+?)^\s*$",
        gd,
        re.M | re.S,
    )
    if budget_decl is None:
        problems.append(
            "could not find `const BOARD_NAME_MAX_BYTES :=` in " f"{GD_PATH.relative_to(REPO_ROOT)}"
        )
    else:
        expr = budget_decl.group(1)
        for required in (
            "LAB_NAME_MAX_CHARS",
            "OPERATOR_NAME_MAX_CHARS",
            "MAX_UTF8_BYTES_PER_CHAR",
            "BOARD_NAME_SEPARATOR_BYTES",
        ):
            if required not in expr:
                problems.append(
                    "BOARD_NAME_MAX_BYTES must stay DERIVED from the input-field "
                    f"caps -- `{required}` is no longer part of its expression. "
                    "A literal budget is how a self-imposed 40 came to be treated "
                    "as an external law."
                )

    # Check 1: the PHP number.
    m = re.search(r"^\$MAX_NAME_BYTES\s*=\s*(\d+)\s*;", php, re.M)
    if m is None:
        problems.append(
            "could not find `$MAX_NAME_BYTES = <int>;` in " f"{PHP_PATH.relative_to(REPO_ROOT)}"
        )
    else:
        php_budget = int(m.group(1))
        if php_budget != derived:
            problems.append(
                f"budget drift: score_api.php stores {php_budget} bytes but the "
                f"client derives {derived} "
                f"(({lab} lab + {operator} operator) * {per_char} + {sep_bytes} "
                "separator).\n"
                f"    client > server -> the server amputates names again;\n"
                f"    client < server -> the client truncates names the server "
                "would have kept.\n"
                "    Move BOTH, and remember score_api.php is deployed by hand "
                "(server/leaderboard/README.md) -- the upload must land BEFORE a "
                "client that sends longer names."
            )

    if problems:
        print("[board-budget] FAIL", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print(
        f"[board-budget] OK: client and server agree on {derived} bytes "
        f"(({lab} + {operator}) * {per_char} + {sep_bytes})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
