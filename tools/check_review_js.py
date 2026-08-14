#!/usr/bin/env python3
"""Syntax-check the JavaScript that serve_review.py serves to the browser.

WHY THIS EXISTS
---------------
On 2026-08-14 the art review gallery was completely dead -- no verdicts, no
lightbox, no keyboard -- for most of a working day, and every check in the repo
said it was fine.

The cause was an unterminated JavaScript string: real newline bytes inside a
single-quoted JS literal, introduced by composing a patch in a shell heredoc
(against this repo's own standing rule) so an intended ``\\n`` collapsed into an
actual newline.

**A JS syntax error means the browser never parses the script block at all**, so
not one event handler binds. And nothing caught it, because every check was at
the wrong layer:

- ``py_compile`` passed -- the Python is fine, the JavaScript is a *string*.
- The server returned HTTP 200 and a 10.9 MB page.
- The page contained all 99 expected text-leak badges.

**Valid Python emitting invalid JavaScript is indistinguishable from success on
the server side.** This script checks the layer that actually failed.

WHAT IT DOES
------------
Imports the module, pulls ``_TEMPLATE``, substitutes the ``{{...}}`` placeholders
with syntactically valid stand-ins, extracts every ``<script>`` block, and runs
``node --check`` over it.

If ``node`` is not installed the check reports SKIPPED and exits 0 -- a missing
tool must not block a commit, but it must also not silently look like a pass.

USAGE
-----
    python tools/check_review_js.py
    python tools/check_review_js.py tools/art_review/serve_review.py
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_TARGETS = ["tools/art_review/serve_review.py"]

# Placeholders substituted with values that are syntactically valid in position.
PLACEHOLDERS = {
    "{{SEED}}": "{}",
    "{{SUBTITLE}}": "",
    "{{NAV}}": "",
    "{{BODY}}": "",
    "{{HELP}}": "",
}


def extract_js(path):
    """Return the concatenated <script> contents of the module's _TEMPLATE."""
    spec = importlib.util.spec_from_file_location("_rv_mod", str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_rv_mod"] = mod
    spec.loader.exec_module(mod)
    tmpl = getattr(mod, "_TEMPLATE", None)
    if tmpl is None:
        return None
    for key, val in PLACEHOLDERS.items():
        tmpl = tmpl.replace(key, val)
    blocks = re.findall(r"<script[^>]*>(.*?)</script>", tmpl, re.S)
    return "\n".join(blocks)


def main(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    targets = argv or DEFAULT_TARGETS

    node = shutil.which("node")
    failures = 0
    for rel in targets:
        path = (REPO / rel) if not pathlib.Path(rel).is_absolute() else pathlib.Path(rel)
        if not path.is_file():
            continue
        try:
            js = extract_js(path)
        except Exception as exc:  # noqa: BLE001 -- import failure is a real result
            print("FAIL %s -- could not import to extract template: %s" % (rel, exc))
            failures += 1
            continue
        if not js:
            print("skip %s -- no _TEMPLATE / no <script> block" % rel)
            continue
        if node is None:
            print(
                "SKIPPED %s -- node not installed, so the served JavaScript was "
                "NOT checked. This is not a pass." % rel
            )
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
            fh.write(js)
            tmp = fh.name
        try:
            res = subprocess.run([node, "--check", tmp], capture_output=True, text=True)
        finally:
            try:
                pathlib.Path(tmp).unlink()
            except OSError:
                pass
        if res.returncode == 0:
            print("ok   %s -- served JavaScript parses (%d bytes)" % (rel, len(js)))
        else:
            print("FAIL %s -- the JavaScript this serves does NOT parse:" % rel)
            print(res.stderr.rstrip())
            print(
                "     A syntax error here means the browser binds NO handlers: "
                "no verdicts, no lightbox, no keys. The page will still return "
                "200 and look complete."
            )
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
