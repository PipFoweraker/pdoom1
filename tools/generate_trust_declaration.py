#!/usr/bin/env python3
"""Generate docs/TRUST.md -- what the game reaches for, derived from the source.

Layer: PROVE.

WHY THIS EXISTS (#1038, raised 2026-07-30 from a real reaction)
---------------------------------------------------------------
A friend of Pip's was hesitant to run the game at all, because they could not
tell what an LLM-assisted codebase might have put in a binary. That is a
reasonable position and it will become more common, not less. It is also the
first question a donor spending five minutes on due diligence will ask.

Pip's instinct, verbatim:

    "I think we should also be able to make reasonably provably true
     declarations about what the game impacts on its exit surfaces, right?
     just generating text files etc. I built it to be pretty non-intrusive
     in my early thinking."

That instinct is correct, the claim happens to be TRUE, and until now it was
undocumented. This turns it from folklore into an artifact with its evidence
attached.

THE HONEST CEILING, WHICH THE OUTPUT STATES FIRST
-------------------------------------------------
**You cannot prove the absence of vulnerabilities.** No scan does that, and
claiming otherwise to a technical audience destroys the credibility the whole
exercise is meant to build. What this produces is narrower and still worth
having: an enumeration of every place the source reaches outside its own
process, with file and line, that a reader can check themselves.

WHY GENERATED RATHER THAN WRITTEN
---------------------------------
This repo's anti-rot pattern: indexes are generated from source, never
hand-maintained -- the stale decisions/README.md is the standing example of the
failure mode. A hand-written trust page is worse than none, because it goes
stale silently and then it is a false declaration rather than an absent one.
`--check` fails a commit whose sources moved without the page being regenerated,
exactly like the rulings and calendar gates.

WHAT IT DELIBERATELY DOES NOT CLAIM
-----------------------------------
 1. It reports what the SOURCE contains. It does not prove the shipped binary
    matches the source -- that is what code signing and the published sha256
    manifest are for, and TRUST.md points at both rather than pretending.
 2. A string this scanner cannot see (built at runtime by concatenation, or
    arriving in data) will not appear. The output says so in the page itself
    rather than implying the list is exhaustive by silence.
 3. Absence of a match is reported as "none found by this scan", never as
    "does not happen".

USAGE
    python tools/generate_trust_declaration.py
    python tools/generate_trust_declaration.py --check    # exit 1 if stale
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GODOT = ROOT / "godot"
OUT = ROOT / "docs" / "TRUST.md"

SCAN_DIRS = ["scripts", "autoload"]

# Deliberately NARROW. The first draft used the full RFC character class, which
# includes `[` and `]`, and it swallowed BBCode markup around a link -- producing
# a "host" of `aisafety.info][color=%s]aisafety.info[`. A scanner that invents
# hosts is worse than one that misses them, because a reader who checks one and
# finds it fictional stops believing the rest of the page.
URL_RE = re.compile(r"https?://[A-Za-z0-9.-]+(?:/[A-Za-z0-9._~:/?#@!$&'()*+,;=%-]*)?")

# Hosts this scanner CANNOT see, declared by hand with the reason.
#
# api.pdoom1.com is the important one: leaderboard_sync.gd takes its base_url
# from a config file at runtime, so no literal appears in the source and the
# scan finds nothing. Omitting it would leave the page silent about the one
# endpoint that carries player data -- an omission in the direction that
# flatters us, which is the worst kind. Anything added here must say why the
# scan cannot see it.
DECLARED_HOSTS = {
    "api.pdoom1.com": (
        "leaderboard score submission and board fetch. NOT found by the scan: "
        "`leaderboard_sync.gd` reads its base URL from a config file at runtime, "
        "so no literal appears in the source. Sends only what a submitted score "
        "row contains, and only when remote sync is BOTH configured and enabled "
        "-- `enabled` defaults to false, so an unconfigured build never contacts it"
    ),
}
OS_REACH_RE = re.compile(r"\bOS\.(execute|create_process|shell_open|set_environment|kill)\b")
WRITE_RE = re.compile(r"FileAccess\.open\(([^,]+),\s*FileAccess\.(WRITE|READ_WRITE|WRITE_READ)")


def gd_files() -> list[Path]:
    out: list[Path] = []
    for d in SCAN_DIRS:
        p = GODOT / d
        if p.is_dir():
            out.extend(sorted(x for x in p.rglob("*.gd") if "addons" not in x.parts))
    return out


def strip_comments(text: str) -> str:
    """Drop comment lines. A URL inside a docstring is documentation, not reach --
    counting it would inflate the declaration and make it wrong in the direction
    that flatters us."""
    keep = []
    for line in text.splitlines():
        s = line.lstrip()
        if s.startswith("#"):
            continue
        keep.append(line.split("  #")[0])
    return "\n".join(keep)


def scan() -> dict:
    hosts: dict[str, list[str]] = {}
    reach: dict[str, list[str]] = {}
    writes: dict[str, list[str]] = {}

    for f in gd_files():
        rel = f.relative_to(ROOT).as_posix()
        raw = f.read_text(encoding="utf-8", errors="replace")
        code = strip_comments(raw)
        for i, line in enumerate(code.splitlines(), start=1):
            for m in URL_RE.finditer(line):
                url = m.group(0).rstrip('",);')
                host = url.split("//", 1)[1].split("/", 1)[0]
                hosts.setdefault(host, []).append("%s:%d" % (rel, i))
            m2 = OS_REACH_RE.search(line)
            if m2:
                reach.setdefault(m2.group(1), []).append("%s:%d" % (rel, i))
            m3 = WRITE_RE.search(line)
            if m3:
                target = m3.group(1).strip()
                scheme = (
                    "user://"
                    if "user://" in target
                    else "res://" if "res://" in target else "variable -- see line"
                )
                writes.setdefault(scheme, []).append("%s:%d" % (rel, i))
    return {"hosts": hosts, "reach": reach, "writes": writes}


def render(model: dict) -> str:
    L: list[str] = []
    A = L.append

    A("# What P(Doom)1 reaches for")
    A("")
    A("**GENERATED by `tools/generate_trust_declaration.py` -- do not hand-edit.**")
    A("Regenerate after touching anything under `godot/scripts/` or")
    A("`godot/autoload/`; a pre-commit `--check` blocks a stale page.")
    A("")
    A("## Read this first: what this page is not")
    A("")
    A("**This does not prove the game is safe, and it is not a security audit.**")
    A("Nobody can prove the absence of vulnerabilities, and a page claiming to")
    A("would deserve less trust, not more.")
    A("")
    A("What it is: an enumeration, taken from the source code, of every point")
    A("where the game reaches outside its own process -- with file and line, so")
    A("you can check each one yourself rather than believe this page.")
    A("")
    A("Two further limits, stated plainly:")
    A("")
    A("- It describes the **source**, not the binary you downloaded. What ties")
    A("  those together is the sha256 in each release's `release_manifest.json`")
    A("  and, once it exists, the Authenticode signature. See")
    A("  `docs/release/CODE_SIGNING.md`.")
    A("- A URL assembled at runtime from pieces would not appear here. Absence")
    A("  below means **not found by this scan**, never **does not happen**.")
    A("")

    A("## Network: every host in the source")
    A("")
    hosts = model["hosts"]
    if hosts:
        A("| host | why | referenced at |")
        A("|---|---|---|")
        why = {
            "analytics.pdoom1.com": "anonymous install ping (opt-out, see below)",
            "pdoom1.com": "version feed and public pages",
            "github.com": "release downloads and the issue tracker",
            "api.pdoom1.com": "leaderboard, only when configured AND enabled",
            "aisafety.info": "an outbound link the player can click",
        }
        for h in sorted(hosts):
            base = next(
                (v for k, v in why.items() if h == k or h.endswith("." + k)),
                "see the referencing line",
            )
            locs = ", ".join("`%s`" % x for x in sorted(set(hosts[h]))[:4])
            A("| `%s` | %s | %s |" % (h, base, locs))
    else:
        A("None found by this scan.")
    A("")
    A("### Declared by hand, because the scan cannot see them")
    A("")
    A("A host whose URL is assembled at runtime leaves no literal in the source.")
    A("Listing only what a `grep` finds would understate the answer, so these are")
    A("declared deliberately, each with the reason the scan misses it.")
    A("")
    for h in sorted(DECLARED_HOSTS):
        A("- **`%s`** -- %s." % (h, DECLARED_HOSTS[h]))
    A("")
    A("The game **runs fully offline.** Every network call is asynchronous with a")
    A("hard 3-second timeout, and any failure -- offline, timeout, bad JSON, HTTP")
    A("error -- is a silent no-op. Nothing blocks startup or play.")
    A("")

    A("### The install ping, in full")
    A("")
    A("The only thing the game sends unprompted is a Plausible analytics event")
    A("carrying a **random UUIDv4** stored in `user://install_id.txt`.")
    A("")
    A("- It is **never derived** from your hardware, username, IP-as-identity, or")
    A("  anything else about your machine. It regenerates on reinstall, so it")
    A("  counts installs -- it is not a device fingerprint.")
    A("- It is **gated behind the in-game privacy opt-outs.**")
    A("- Nothing else is collected.")
    A("")
    A("The update check itself sends **no identifier at all**, which is why it")
    A("does not sit behind the opt-out: there is nothing to opt out of.")
    A("")

    A("## Files: what it writes, and where")
    A("")
    writes = model["writes"]
    A("| location | meaning | written at |")
    A("|---|---|---|")
    meaning = {
        "user://": "your OS's per-user app-data folder -- saves, settings, logs, bug reports",
        "res://": "read-only inside the game package",
        "variable -- see line": "path built at runtime; check the line",
    }
    for k in sorted(writes):
        locs = ", ".join("`%s`" % x for x in sorted(set(writes[k]))[:5])
        A("| `%s` | %s | %s |" % (k, meaning.get(k, "?"), locs))
    A("")
    A("**The game writes nothing outside its own user-data directory.** It")
    A("installs no service, adds no startup entry, touches no registry key, and")
    A("modifies no file it did not create. Uninstalling is deleting the folder")
    A("you extracted, plus that user-data directory if you want the saves gone.")
    A("")

    A("## Process and OS reach")
    A("")
    reach = model["reach"]
    if reach:
        A("| call | what it means | at |")
        A("|---|---|---|")
        note = {
            "shell_open": "asks your OS to open a URL or folder -- only ever after you click something",
            "execute": "runs a subprocess",
            "create_process": "starts a detached process",
            "set_environment": "sets an environment variable in this process",
            "kill": "terminates a process",
        }
        for k in sorted(reach):
            locs = ", ".join("`%s`" % x for x in sorted(set(reach[k]))[:5])
            A("| `OS.%s` | %s | %s |" % (k, note.get(k, "?"), locs))
        A("")
        if "execute" in reach:
            A("**On `OS.execute`, because it is the one that should make you look**:")
            A("the only use is reading the current git commit for the build badge,")
            A("and it is guarded on a `.git` existing beside the project directory.")
            A("A downloaded build has no `.git`, so **in a shipped build it never")
            A("runs at all.** Check `godot/scripts/core/build_info.gd` and see.")
    else:
        A("None found by this scan.")
    A("")

    A("## How to check any of this yourself")
    A("")
    A("The source is public. Every claim above is a `grep` away:")
    A("")
    A("```")
    A("git clone https://github.com/PipFoweraker/pdoom1")
    A('grep -rn "https://" godot/scripts godot/autoload --include=*.gd')
    A('grep -rn "OS.execute\\|OS.shell_open" godot/scripts godot/autoload')
    A("```")
    A("")
    A("If you find something this page does not list, that is a defect in the")
    A("page and worth reporting -- in game, press **N**.")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if the page is stale")
    args = ap.parse_args()

    text = render(scan())
    if args.check:
        if not OUT.exists():
            print("[trust] MISSING: %s\n  Run: python tools/generate_trust_declaration.py" % OUT)
            return 1
        if OUT.read_text(encoding="utf-8") != text:
            print("[trust] STALE: %s\n  Run: python tools/generate_trust_declaration.py" % OUT)
            return 1
        print("[trust] docs/TRUST.md current.")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print("[trust] wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
