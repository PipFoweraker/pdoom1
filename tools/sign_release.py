#!/usr/bin/env python3
"""Authenticode-sign a built Windows binary, or say clearly that it did not.

Layer: PROVE.

WHY THIS EXISTS, 2026-08-23
---------------------------
Pip is about to tell ten people today, forty tomorrow, and email a hundred the
day after. Every one of them, on Windows, currently meets:

    Windows protected your PC
    Microsoft Defender SmartScreen prevented an unrecognised app from starting.

That is the first thing a donor doing five minutes of due diligence sees, and
issue #1038 records a friend who declined to run the game at all for exactly
this reason: they could not tell what an LLM-assisted codebase had put in a
binary. That is a reasonable position and it is becoming more common.

THE MEASUREMENT THAT DECIDES THE DESIGN
---------------------------------------
Microsoft's SmartScreen reputation works on TWO objects, and only one of them
survives a rebuild:

  * FILE-HASH reputation attaches to one exact binary. It grows as people
    download and run that file without incident, and it DIES the moment a new
    build ships, because a new build is a new hash.
  * CERTIFICATE reputation accumulates across every file the certificate signs.
    New builds signed with an established certificate INHERIT that trust.

This project bumps builds constantly -- twenty-three commits past the last tag
on the day this was written. Unsigned, that cadence is not merely unhelpful, it
is self-defeating: every release resets the only reputation it has to zero, so
the warning can never stop appearing no matter how many people download it.

Signing is the one purchase whose value COMPOUNDS with build frequency instead
of being destroyed by it.

Note, because it is a common and expensive misconception: since March 2024 an
EV certificate NO LONGER grants instant SmartScreen trust. EV and OV now build
reputation the same way. Buy on validation speed and price, not on a bypass
that no longer exists.

WHAT THIS TOOL WILL NOT DO
--------------------------
It will not pretend. Three estate rules apply and each kills a specific silent
failure:

 1. UNSIGNED IS REPORTED, NEVER ASSUMED-FINE. If no credentials are configured
    this exits 0 with an explicit NOT SIGNED verdict, because an unsigned dev
    build is a legitimate state. It never prints anything that could be read as
    "signed" when it is not. `--require` inverts this for release builds: no
    credentials becomes a hard failure, so a release cannot quietly ship
    unsigned the way v0.13.1's gdextension binaries quietly shipped missing.

 2. A SIGNATURE IS VERIFIED AFTER SIGNING, FROM OUTSIDE THE SIGNING TOOL.
    signtool can exit 0 having produced a signature that does not verify. The
    check therefore re-reads the file with `signtool verify /pa` rather than
    trusting the sign command's own exit code. Observation comes from a
    different invocation than the action.

 3. TIMESTAMPING IS MANDATORY, NOT OPTIONAL. Without an RFC-3161 timestamp
    every signature this project has ever made stops validating the day the
    certificate expires -- which, under the CA/Browser Forum change effective
    2026-02-23, is at most 459 days after issuance. Builds handed to donors and
    playtesters would silently become "unknown publisher" again on a date
    nobody has written down. If timestamping fails, signing fails.

CONFIGURATION -- deliberately the same shape as leaderboard_sync.gd
-------------------------------------------------------------------
Credentials come from the environment, never from a file in the repo:

    PDOOM1_SIGN_METHOD    "signtool" (default) or "azure"
    PDOOM1_SIGN_SHA1      certificate thumbprint in the Windows cert store
    PDOOM1_SIGN_PFX       path to a .pfx  (alternative to the thumbprint)
    PDOOM1_SIGN_PFX_PASS  password for that .pfx
    PDOOM1_SIGN_TS_URL    RFC-3161 timestamp URL (a working default is used)

Nothing secret is ever written to disk or echoed. The .pfx password is passed
to signtool and never logged; `--dry-run` prints the command with the password
replaced by a placeholder so the invocation can be reviewed safely.

USAGE
-----
    python tools/sign_release.py builds/windows_desktop/PDoom.exe
    python tools/sign_release.py --require builds/windows_desktop/PDoom.exe
    python tools/sign_release.py --dry-run builds/windows_desktop/PDoom.exe
    python tools/sign_release.py --status

EXIT CODES
    0  signed and verified, OR unsigned-and-said-so without --require
    1  signing was attempted and failed, or --require with no credentials
    2  the tool could not run at all (no signtool on PATH, file missing)
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# A default RFC-3161 timestamp authority. DigiCert's is free, does not require an
# account, and is not tied to who issued the certificate.
DEFAULT_TS_URL = "http://timestamp.digicert.com"

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_CANNOT_RUN = 2

PLACEHOLDER = "<password-not-shown>"


def info(msg: str) -> None:
    print("[sign_release] %s" % msg)


def creds_present() -> bool:
    return bool(os.environ.get("PDOOM1_SIGN_SHA1") or os.environ.get("PDOOM1_SIGN_PFX"))


def find_signtool() -> Path | None:
    """signtool.exe, from an explicit override, PATH, or a known install.

    NOT installed by the full Windows SDK on this machine, deliberately. winget
    only carries 2018-era SDK packages (10.0.17134 / 10.0.18362), which are old
    enough to predate signing algorithms we want. Microsoft also ships signtool
    inside the `Microsoft.Windows.SDK.BuildTools` NuGet package -- a ~22MB
    download, no administrator rights, and no multi-gigabyte SDK for one binary.
    That is what is deployed here (2026-08-23, version 10.0.28000.2526).

    Note it is extracted WITH its sibling DLLs rather than as a lone exe:
    signtool loads wintrust/appx helpers from its own directory and fails
    obscurely if they are missing.
    """
    explicit = os.environ.get("PDOOM1_SIGNTOOL")
    if explicit and Path(explicit).is_file():
        return Path(explicit)
    which = shutil.which("signtool")
    if which:
        return Path(which)
    # The NuGet BuildTools drop, then the full-SDK locations.
    nuget_drop = Path.home() / "bin" / "windows-sdk-buildtools" / "signtool.exe"
    if nuget_drop.is_file():
        return nuget_drop
    roots = [
        Path("C:/Program Files (x86)/Windows Kits/10/bin"),
        Path("C:/Program Files/Windows Kits/10/bin"),
    ]
    found: list[Path] = []
    for root in roots:
        if root.is_dir():
            found.extend(root.glob("*/x64/signtool.exe"))
    if not found:
        return None
    # Highest SDK version wins; older signtool builds predate some /fd algorithms.
    return sorted(found)[-1]


def build_command(tool: Path, target: Path) -> tuple[list[str], list[str]]:
    """(real command, redacted command). Redacted is what is safe to print."""
    ts = os.environ.get("PDOOM1_SIGN_TS_URL", DEFAULT_TS_URL)
    cmd = [str(tool), "sign", "/fd", "sha256", "/td", "sha256", "/tr", ts, "/v"]
    sha1 = os.environ.get("PDOOM1_SIGN_SHA1")
    pfx = os.environ.get("PDOOM1_SIGN_PFX")
    if sha1:
        cmd += ["/sha1", sha1]
        redacted = list(cmd)
    elif pfx:
        cmd += ["/f", pfx]
        redacted = list(cmd)
        pw = os.environ.get("PDOOM1_SIGN_PFX_PASS")
        if pw:
            cmd += ["/p", pw]
            redacted += ["/p", PLACEHOLDER]
    else:
        raise RuntimeError("no credentials")
    cmd.append(str(target))
    redacted.append(str(target))
    return cmd, redacted


def verify(tool: Path, target: Path) -> tuple[bool, str]:
    """Rule 2: re-read the file rather than trusting the sign command's exit code."""
    r = subprocess.run(
        [str(tool), "verify", "/pa", "/v", str(target)], capture_output=True, text=True
    )
    return r.returncode == 0, (r.stdout or "") + (r.stderr or "")


def status() -> int:
    tool = find_signtool()
    info("signtool: %s" % (tool if tool else "NOT FOUND"))
    info("method:   %s" % os.environ.get("PDOOM1_SIGN_METHOD", "signtool"))
    info(
        "cert:     %s"
        % (
            "thumbprint in cert store"
            if os.environ.get("PDOOM1_SIGN_SHA1")
            else ".pfx file" if os.environ.get("PDOOM1_SIGN_PFX") else "NONE CONFIGURED"
        )
    )
    info("timestamp:%s" % os.environ.get("PDOOM1_SIGN_TS_URL", DEFAULT_TS_URL))
    if not creds_present():
        info("")
        info("No signing credentials. Builds will be UNSIGNED and every Windows")
        info("downloader will see the SmartScreen 'unrecognised app' wall. See")
        info("docs/release/CODE_SIGNING.md for what to buy and what it costs.")
    return EXIT_OK


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("target", nargs="?", help="binary to sign")
    ap.add_argument(
        "--require",
        action="store_true",
        help="fail if no credentials are configured (use for releases)",
    )
    ap.add_argument(
        "--dry-run", action="store_true", help="print the redacted command without running it"
    )
    ap.add_argument("--status", action="store_true", help="report what is configured and exit")
    args = ap.parse_args()

    if args.status:
        return status()
    if not args.target:
        ap.error("a target binary is required (or pass --status)")

    target = Path(args.target)
    if not target.is_file():
        info("CANNOT RUN: %s does not exist." % target)
        return EXIT_CANNOT_RUN

    if not creds_present():
        # Rule 1: an unsigned dev build is legitimate; a SILENT one is not.
        info("NOT SIGNED -- no credentials configured (PDOOM1_SIGN_SHA1 / _PFX).")
        info("            %s will show SmartScreen 'unrecognised app'." % target.name)
        if args.require:
            info("FAILING because --require was passed: a release must not ship unsigned")
            info("        without somebody deciding that on purpose.")
            return EXIT_FAILED
        return EXIT_OK

    tool = find_signtool()
    if tool is None:
        info("CANNOT RUN: signtool.exe not found (install the Windows SDK).")
        return EXIT_CANNOT_RUN

    cmd, redacted = build_command(tool, target)
    if args.dry_run:
        info("would run: %s" % " ".join(redacted))
        return EXIT_OK

    info("signing %s" % target)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        info("SIGNING FAILED (signtool exit %d)." % r.returncode)
        # Never echo the real command -- it may carry the .pfx password.
        print((r.stdout or "") + (r.stderr or ""), file=sys.stderr)
        return EXIT_FAILED

    ok, out = verify(tool, target)
    if not ok:
        # Rule 2 earning its place: signtool exited 0 and the result does not verify.
        info("SIGNED BUT VERIFICATION FAILED -- do not ship this binary.")
        print(out, file=sys.stderr)
        return EXIT_FAILED

    # Rule 3: a signature without a timestamp expires with the certificate.
    if "Timestamp" not in out and "timestamp" not in out:
        info("SIGNED BUT NOT TIMESTAMPED -- refusing to call this good.")
        info("        Without an RFC-3161 timestamp this signature stops validating")
        info("        when the certificate expires (<=459 days under the CA/B change")
        info("        effective 2026-02-23), and every build already handed out")
        info("        silently becomes 'unknown publisher' on a date nobody wrote down.")
        return EXIT_FAILED

    info("SIGNED and VERIFIED, with timestamp: %s" % target)
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
