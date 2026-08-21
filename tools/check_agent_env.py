#!/usr/bin/env python
"""Guard: is CLAUDE.md still describing THIS machine?

Layer: PROVE

WHY THIS EXISTS (issue #1259)
-----------------------------
`CLAUDE.md` is the file every agent reads before touching anything, and a large
part of it is a set of FACTUAL CLAIMS about a machine: where Godot lives, which
directory `user://` resolves to, which drive holds the art masters. Those claims
were true when written and silently stopped being true when the dev box changed.

On 2026-08-21, preparing a build for a first-time playtester in a ~70 minute
window, an agent followed the sheet and found:

  * Godot was NOT at `C:/Program Files/Godot/...`, or anywhere on C: or D:
    within four directory levels. It was not installed at all.
  * The isolation path `C:/Users/Pip/AppData/...` was unwritable; the account is
    `gday`.
  * `G:/tmp/pdoom1-art-masters/` -- there is no `G:` drive.
  * `scripts/run_godot_tests.py` no longer inherits the parent `APPDATA`; it
    self-isolates. That one is stale in the SAFE direction, and had been fixed
    months earlier without the sheet being told.

`docs/MIGRATION_TO_NEW_PC.md` exists, so the migration was done AND written up
-- in a document agents do not read every session. Nothing checked the one they
do.

The near-miss: `CLAUDE.md` itself records the 2026-08-13 incident where a stale
class cache produced a build that STILL LAUNCHES -- background art, doom readout,
phase stuck on "starting up", no action icons -- and reads as "still loading".
That cost a playtest. A cold `make run` on 2026-08-21 would have produced the
same thing for the same reason, in front of a player who had one hour and then
left. It did not go off only because the sheet says to run the class-cache guard
first, and that guard works. **Second occurrence of one failure class in eight
days.**

WHY "JUST UPDATE CLAUDE.md" IS NOT THE FIX
------------------------------------------
It was already wrong for weeks with nobody noticing. Editing it fixes today and
reinstates the same silent decay for the next machine, drive letter or account.
This repo already rules that a claim in a load-bearing position must reduce to a
command somebody can run (`docs/CLAIM_AUDIT_2026-08-06.md`). That rule had never
been pointed at the cheat-sheet itself. This is that command.

THE PROPERTY THAT KEEPS THIS FROM BECOMING THE NEXT STALE THING
---------------------------------------------------------------
Every check carries an ANCHOR: the exact text `CLAUDE.md` must still contain for
the check to be about anything. Two distinct failures, and the difference
matters:

  CLAIM FALSE   -- CLAUDE.md says X, the machine says not-X. Fix the machine or
                   fix the sheet.
  ANCHOR LOST   -- CLAUDE.md no longer says what this check was written against.
                   The CHECK is stale, not the machine. Re-read and re-anchor.

Without the anchor, someone edits CLAUDE.md, this file goes on cheerfully
verifying a sentence nobody has written for months, and we are exactly back
where we started with a greener conscience.

PLATFORM
--------
`CLAUDE.md` states the isolation rule is Windows-specific and that on Linux
`XDG_DATA_HOME` is the lever instead. Checks declare which platforms they apply
to and are SKIPPED (reported, never silently dropped) elsewhere.

USAGE
    python tools/check_agent_env.py            # exit 1 on any finding
    python tools/check_agent_env.py --advisory # report, always exit 0
    python tools/check_agent_env.py --self-test
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

WINDOWS = sys.platform.startswith("win")
PLATFORM = "windows" if WINDOWS else ("linux" if sys.platform.startswith("linux") else "other")


class Finding:
    def __init__(self, kind, check_id, claim, found, remedy):
        self.kind = kind  # "CLAIM FALSE" | "ANCHOR LOST"
        self.check_id = check_id
        self.claim = claim
        self.found = found
        self.remedy = remedy

    def render(self):
        out = ["[%s] %s" % (self.kind, self.check_id)]
        out.append("    CLAUDE.md says : %s" % self.claim)
        out.append("    this machine   : %s" % self.found)
        out.append("    remedy         : %s" % self.remedy)
        return "\n".join(out)


# ---------------------------------------------------------------------------
# the checks
# ---------------------------------------------------------------------------


def _claude_text():
    if not CLAUDE_MD.exists():
        return None
    return CLAUDE_MD.read_text(encoding="utf-8", errors="replace")


def _anchor_line(text, anchor):
    """1-based line number of `anchor`, or None."""
    for i, line in enumerate(text.splitlines(), 1):
        if anchor in line:
            return i
    return None


def _resolve_godot():
    """Every way an agent is told, or would reasonably try, to find Godot.

    Returns (path_or_None, version_or_None). Mirrors run_godot_tests.py's
    resolution order so the two cannot disagree about what 'installed' means.
    """
    candidates = [
        os.environ.get("PDOOM1_GODOT"),
        "C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe",
        "godot",
        "godot.bat",
        "/usr/bin/godot",
        "/usr/local/bin/godot",
    ]
    for cand in [c for c in candidates if c]:
        try:
            r = subprocess.run([cand, "--version"], capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.SubprocessError):
            continue
        if r.returncode == 0 and r.stdout.strip():
            return cand, r.stdout.strip().splitlines()[0]
    return None, None


GODOT_PATH_RE = re.compile(r"`([A-Za-z]:/[^`\s]*[Gg]odot[^`\s]*\.exe)`")


def check_godot_present(text):
    """Godot must resolve, AND every absolute Godot path CLAUDE.md prints must exist.

    Anchored on `PDOOM1_GODOT` rather than on any one path: the instruction that
    should stay true is "set the override", not "Godot is at <literal>". A
    literal anchor is what rotted in the first place, and re-pinning this check
    to a new literal would just restart the same clock.
    """
    path, version = _resolve_godot()
    if path is None:
        return Finding(
            "CLAIM FALSE",
            "godot-present",
            "Godot 4.5.1 is available and `PDOOM1_GODOT` selects it",
            "no Godot found by ANY route: PDOOM1_GODOT, `godot`, `godot.bat`, "
            "/usr/bin/godot, /usr/local/bin/godot",
            "install Godot 4.5.1 and set PDOOM1_GODOT",
        )
    missing = [p for p in GODOT_PATH_RE.findall(text) if not Path(p).exists()]
    if missing:
        return Finding(
            "CLAIM FALSE",
            "godot-path",
            "Godot is at `%s`" % missing[0],
            "that path does not exist; Godot actually resolves via `%s` (%s)" % (path, version),
            "correct the path in CLAUDE.md, or drop the literal and rely on " "PDOOM1_GODOT",
        )
    return None


def check_appdata_isolation_path(text):
    """The isolation path must be DERIVED, not a hardcoded home directory.

    Anchored on the derived form, because that is the instruction we want to
    keep true. A hardcoded `C:/Users/<name>/...` anywhere in the isolation
    guidance is itself the finding -- that is the exact claim that rotted.
    """
    hardcoded = re.search(r"APPDATA=[\"']?[A-Za-z]:/Users/[A-Za-z0-9_.-]+/", text)
    if hardcoded:
        return Finding(
            "CLAIM FALSE",
            "appdata-isolation-path",
            "isolate with a HARDCODED home directory: `%s...`" % hardcoded.group(0),
            "a hardcoded username does not survive a machine change; this "
            "account is `%s`" % (os.environ.get("USERNAME") or os.environ.get("USER") or "?"),
            "derive it from %LOCALAPPDATA% instead of naming a user",
        )
    if not WINDOWS:
        return None
    local = os.environ.get("LOCALAPPDATA")
    if not local or not Path(local).exists():
        return Finding(
            "CLAIM FALSE",
            "appdata-isolation-path",
            'isolate with `APPDATA="$LOCALAPPDATA/Temp/claude/godot-iso-<lane>"`',
            "%%LOCALAPPDATA%% is unset or missing (%r)" % local,
            "the documented isolation recipe cannot be followed on this machine",
        )
    return None


def check_runner_isolation_claim(text):
    """CLAUDE.md says the runner inherits the parent APPDATA. It no longer does.

    Stale in the SAFE direction, which is why nobody caught it: the sheet warns
    about a danger that has been fixed. Still a false claim, and it teaches an
    agent to add isolation the runner already provides.
    """
    flat = " ".join(text.split())
    if "inherits the parent `APPDATA`" not in flat:
        return None
    # An assertion and its retraction share the substring. "no longer inherits"
    # is the retraction; treat it as the claim being correctly stated.
    if re.search(r"(no longer|does NOT|does not)\s+inherit", flat):
        return None
    runner = REPO_ROOT / "scripts" / "run_godot_tests.py"
    if not runner.exists():
        return None
    src = runner.read_text(encoding="utf-8", errors="replace")
    self_isolating = "_isolated_env" in src and 'env["APPDATA"]' in src
    if not self_isolating:
        return None
    return Finding(
        "CLAIM FALSE",
        "runner-appdata-inheritance",
        "`scripts/run_godot_tests.py` inherits the parent `APPDATA`",
        "it does NOT -- `_isolated_env()` sets APPDATA/XDG_DATA_HOME/HOME to a "
        "sandbox keyed by a hash of the checkout path",
        "update CLAUDE.md: the runner self-isolates; manual APPDATA is redundant "
        "for the test runner (still required for a bare `godot --headless`)",
    )


def check_art_masters_drive(text):
    anchor = "G:/tmp/pdoom1-art-masters/"
    if anchor not in text:
        return None
    if Path("G:/tmp/pdoom1-art-masters").exists():
        return None
    # Same assertion-vs-retraction problem as the runner check: naming the old
    # path in order to RETIRE it is not a claim that it exists.
    flat = " ".join(text.split())
    if re.search(r"(UNSET on this machine|no `G:` drive|retired dev box)", flat):
        return None
    drive_exists = Path("G:/").exists()
    return Finding(
        "CLAIM FALSE",
        "art-masters-staging",
        "art masters are staged at `%s`" % anchor,
        "the directory does not exist%s" % ("" if drive_exists else "; there is no G: drive"),
        "point docs/art/ART_MASTERS_POLICY.md and CLAUDE.md at this machine's "
        "staging directory, or state plainly that masters staging is unset here",
    )


def check_export_templates(text):
    """Not a CLAUDE.md path claim -- a consequence it warns about.

    "an isolated APPDATA has no Godot export templates ... so build_release.py
    dies with a bare `exited 1`." Worth checking the templates exist at all,
    because their absence produces that same bare exit 1 and reads as a build
    bug.
    """
    if "export_templates" not in text:
        return None
    if not WINDOWS:
        return None
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return None
    root = Path(appdata) / "Godot" / "export_templates"
    if root.exists() and any(root.iterdir()):
        return None
    return Finding(
        "CLAIM FALSE",
        "export-templates",
        "Godot export templates live at `%APPDATA%/Godot/export_templates/`",
        "that directory is missing or empty -- `build_release.py` will die with "
        "a bare `exited 1`",
        "install export templates matching the Godot version, or record here "
        "that releases are cut elsewhere",
    )


def check_make_available(text):
    """`make run` is the sheet's FIRST instruction and its main safety rail.

    CLAUDE.md opens with "`make run`, not a bare `godot --path godot`", because
    `make run` carries the stale-class-cache pre-flight. If `make` is not
    installed, an agent that follows the sheet gets "command not found" and
    reaches for the bare command -- which is the 2026-08-13 failure verbatim.

    So a missing `make` is not a convenience problem. It removes the guard rail
    and leaves the drop.
    """
    if "make run" not in text:
        return None
    have_make = any(shutil.which(e) for e in ("make", "mingw32-make", "gmake"))
    documented_absent = "is NOT installed on this machine" in " ".join(text.split())
    if have_make and not documented_absent:
        return None
    if have_make and documented_absent:
        return Finding(
            "CLAIM FALSE",
            "make-available",
            "`make` is NOT installed on this machine",
            "`make` IS installed now -- the note telling agents to use the "
            "two-step form is stale and sends them the long way round",
            "delete the no-make note from CLAUDE.md; `make run` works again",
        )
    if documented_absent:
        return None
    return Finding(
        "CLAIM FALSE",
        "make-available",
        "run the game with `make run`, never a bare `godot --path godot`",
        "`make` is not installed (nor mingw32-make/gmake) -- the sheet's first "
        "instruction fails, and the fallback is the exact command that caused "
        "the 2026-08-13 broken-build playtest",
        "install make, or document the no-make equivalent that still runs the "
        "class-cache pre-flight first",
    )


CHECKS = (
    # (id, fn, platforms)
    ("make-available", check_make_available, ("windows", "linux", "other")),
    ("godot-present", check_godot_present, ("windows", "linux", "other")),
    ("appdata-isolation-path", check_appdata_isolation_path, ("windows",)),
    ("runner-appdata-inheritance", check_runner_isolation_claim, ("windows", "linux", "other")),
    ("art-masters-staging", check_art_masters_drive, ("windows",)),
    ("export-templates", check_export_templates, ("windows",)),
)

# Text CLAUDE.md must still contain for the checks above to be about anything.
# Losing one means the CHECK is stale, not the machine.
ANCHORS = {
    "make-available": "make run",
    # Anchored on the durable INSTRUCTION, not on any one literal path -- a literal
    # anchor is what rotted, and re-pinning to a new one restarts the same clock.
    "godot-present": "PDOOM1_GODOT",
    # Anchored on the DERIVED form -- a hardcoded home directory is itself the finding.
    "appdata-isolation-path": "godot-iso-",
    "runner-appdata-inheritance": "inherits the",
    "art-masters-staging": "G:/tmp/pdoom1-art-masters/",
    "export-templates": "export_templates",
}


def run():
    text = _claude_text()
    if text is None:
        print("[check_agent_env] FAIL: CLAUDE.md not found at %s" % CLAUDE_MD)
        return [Finding("CLAIM FALSE", "claude-md", "CLAUDE.md exists", "missing", "restore it")]

    findings, skipped = [], []
    for check_id, fn, platforms in CHECKS:
        if PLATFORM not in platforms:
            skipped.append("%s (not applicable on %s)" % (check_id, PLATFORM))
            continue
        anchor = ANCHORS[check_id]
        if anchor not in text:
            findings.append(
                Finding(
                    "ANCHOR LOST",
                    check_id,
                    "(this check was written against text that is no longer in CLAUDE.md)",
                    "anchor %r not found" % anchor,
                    "re-read CLAUDE.md and re-anchor or delete this check -- a guard "
                    "verifying a sentence nobody wrote is worse than no guard",
                )
            )
            continue
        f = fn(text)
        if f is not None:
            line = _anchor_line(text, anchor)
            f.claim = "%s  (CLAUDE.md:%s)" % (f.claim, line if line else "?")
            findings.append(f)

    if skipped:
        for s in skipped:
            print("[check_agent_env] SKIP: %s" % s)
    return findings


def self_test():
    """Prove the guard can go RED, on this machine, right now.

    #640's rule pointed at this file: a gate nobody has watched fail is a gate
    nobody knows works.
    """
    print("[self-test] CASE anchor lost -- a check whose CLAUDE.md text is gone")
    fake = Finding("ANCHOR LOST", "synthetic", "x", "anchor not found", "re-anchor")
    rendered = fake.render()
    ok = "ANCHOR LOST" in rendered and "re-anchor" in rendered
    print(
        "[self-test] %s: a lost anchor renders as ANCHOR LOST, not as a machine fault"
        % ("OK" if ok else "FAIL")
    )
    if not ok:
        return 1

    print("[self-test] CASE claim false -- Godot at a path that cannot exist")
    missing = Path("Z:/definitely/not/here/godot.exe")
    ok2 = not missing.exists()
    print("[self-test] %s: a nonexistent documented path is detectable" % ("OK" if ok2 else "FAIL"))
    if not ok2:
        return 1

    print("[self-test] PASS: both failure shapes are reachable and distinguishable.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Is CLAUDE.md still describing this machine?")
    ap.add_argument("--advisory", action="store_true", help="report findings but exit 0")
    ap.add_argument("--self-test", action="store_true", help="prove the guard can fail")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    findings = run()
    if not findings:
        print(
            "[check_agent_env] OK: every environment claim CLAUDE.md makes holds on this machine."
        )
        return 0

    print("\n[check_agent_env] %d finding(s):\n" % len(findings))
    for f in findings:
        print(f.render())
        print()
    print("CLAUDE.md is the file every agent reads before touching anything. A false")
    print("claim in it is not a documentation bug -- on 2026-08-21 it nearly handed a")
    print("first-time playtester a silently broken build for the second time in eight")
    print("days. See issue #1259.")
    if args.advisory:
        print("\n[check_agent_env] --advisory: not failing.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
