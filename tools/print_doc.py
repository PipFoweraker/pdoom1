#!/usr/bin/env python3
"""Print a Markdown or HTML doc to paper with PREDICTABLE, LEGIBLE typography.

Layer: OBSERVE
Invoked by: human

WHY THIS EXISTS (Pip's ask, 2026-07-31). `Out-Printer` gives no font control -- it
renders whatever the shell hands it at whatever size Windows picks, which is how you
end up with a 9pt wall of text you cannot read while walking. The standard he asked
for is a 12pt floor and formatting that does not change between documents.

HOW IT WORKS. Chrome/Edge headless renders the HTML to PDF (honouring @page and the
stylesheet below, so the 12pt floor is enforced at render time, not hoped for), then
the PDF goes to the printer. No Word, no browser window, no manual Ctrl-P.

    python tools/print_doc.py docs/NOTES.md                 # print to default printer
    python tools/print_doc.py sheet.html --pdf-only         # render, do not print
    python tools/print_doc.py sheet.html --printer "Brother HL-L2460DW series"
    python tools/print_doc.py docs/NOTES.md --base-size 14  # bigger, for walking
    python tools/print_doc.py RUNSHEET.md --sides simplex   # clipboard: NEVER duplex

    python tools/print_doc.py --list-printers

HTML input is printed as-authored (its own <style> wins), with the house stylesheet
below supplying only the defaults it does not set. Markdown input gets the house
stylesheet outright.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# The print legibility standard. Nothing here may drop below 11pt.
HOUSE_CSS = """
@page { size: A4 portrait; margin: 14mm 13mm; }
html { font-size: %(base)spt; }
body { font-family: "Segoe UI", Calibri, Arial, sans-serif; line-height: 1.42;
       color: #000; background: #fff; max-width: 190mm; margin: 0 auto; }
h1 { font-size: %(h1)spt; margin: 0 0 3mm; line-height: 1.15; }
h2 { font-size: %(h2)spt; margin: 7mm 0 2mm; padding: 1.6mm 2.5mm;
     background: #1a1a1a; color: #fff; page-break-after: avoid; }
h3 { font-size: %(h3)spt; margin: 4.5mm 0 1.5mm; page-break-after: avoid; }
p, li, td, th { font-size: %(base)spt; }
/* table-layout:fixed is LOAD-BEARING, not cosmetic, and it is what enforces the
   11pt floor at render time. Without it a wide table overflows the content box
   and Chromium shrinks the ENTIRE PAGE to fit -- uniformly, so every size scales
   together and the result reads as a deliberate layout rather than a fault.
   MEASURED 2026-08-23 through this tool's own --pdf-only path, default 12.5pt:
       docs/POSTMORTEM_2026-08-07_CAPTURE.md        12.49pt  scale 1.00
       docs/game-design/ADR_DQ_AUDIT_2026-08-03.md  12.34pt  scale 0.99
       docs/game-design/WS3A_DAYLOG_2026-07-27.md   11.62pt  scale 0.93
       godot/docs/qa/SHUTDOWN_HYGIENE_2026-07-16.md  8.33pt  scale 0.67
       docs/TOOLS.md                                 8.37pt  scale 0.67
   The last two are UNDER the 11pt floor main() calls not negotiable -- the floor
   was applied to the HTML and then undone at render time, silently.
   Margins are specified in mm and do NOT shrink with it, so the margin-to-type
   ratio blows out; the paper was never wide, the ink got small.
   Same fix and same reasoning as coordination/tools/walkpack/build_walkpack.py
   at 43cb364. */
table { border-collapse: collapse; width: 100%%; margin: 2.5mm 0 4mm;
        table-layout: fixed; }
th, td { border: 1px solid #444; padding: 2.2mm 2.6mm; text-align: left; vertical-align: top;
         overflow-wrap: anywhere; }
th { background: #e8e8e8; font-weight: 700; }
code, pre { font-family: Consolas, "Courier New", monospace; font-size: %(mono)spt;
            overflow-wrap: anywhere; }
code { background: #eee; padding: 0.3mm 1mm; }
pre { background: #f2f2f2; padding: 2.5mm 3mm; border: 1px solid #ccc;
      white-space: pre-wrap; word-wrap: break-word; }
blockquote { border-left: 4pt solid #000; margin: 2.5mm 0; padding: 1.5mm 0 1.5mm 4mm; }
ul, ol { margin: 1.5mm 0 3mm; padding-left: 7mm; }
li { margin-bottom: 1.3mm; }
hr { border: 0; border-top: 1.2pt solid #999; margin: 5mm 0; }
img { max-width: 100%%; }
"""

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def find_browser() -> str:
    for cand in BROWSERS:
        if Path(cand).exists():
            return cand
    for name in ("msedge", "chrome", "chromium", "google-chrome"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit(
        "No Chrome/Edge found -- needed to render with real typography.\n"
        "Use --pdf-only on a machine that has one, or print the HTML by hand."
    )


def md_to_html(md_text: str, css: str, title: str) -> str:
    try:
        import markdown  # type: ignore

        body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "toc"])
    except ImportError:
        # No hard dependency: fall back to preformatted text, which is still
        # legible at 12pt and still beats Out-Printer. Say so rather than
        # silently producing something worse than expected.
        print("[note] python-markdown not installed -- printing as preformatted text.")
        print("       pip install markdown   for proper headings and tables.")
        escaped = md_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        body = "<pre>%s</pre>" % escaped
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>%s</title><style>%s</style></head><body>%s</body></html>" % (title, css, body)
    )


def render_pdf(browser: str, html_path: Path, pdf_path: Path) -> None:
    url = html_path.resolve().as_uri()
    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-to-pdf=%s" % pdf_path.resolve(),
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if not pdf_path.exists():
        raise SystemExit(
            "PDF render failed (exit %d).\nstderr:\n%s" % (proc.returncode, proc.stderr[-1500:])
        )


def list_printers() -> int:
    ps = "Get-CimInstance Win32_Printer | Select-Object -ExpandProperty Name"
    out = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
        capture_output=True,
        text=True,
    )
    print(out.stdout.strip() or "(none found)")
    return 0


# Silent printers, in preference order. The shell "print" verb is LAST because it
# hands the file to whatever owns .pdf -- on Pip's machine that is Acrobat, which
# pops a window and steals mouse focus. A print helper that interrupts the person
# it is printing for has defeated its own purpose (his note, 2026-07-31).
SILENT_PRINTERS = [
    Path(os.environ.get("LOCALAPPDATA", "")) / "SumatraPDF" / "SumatraPDF.exe",
    Path(os.environ.get("ProgramFiles", "")) / "SumatraPDF" / "SumatraPDF.exe",
    Path(os.environ.get("ProgramFiles(x86)", "")) / "SumatraPDF" / "SumatraPDF.exe",
]


def find_silent_printer() -> Path | None:
    for cand in SILENT_PRINTERS:
        if str(cand) and cand.exists():
            return cand
    found = shutil.which("SumatraPDF")
    return Path(found) if found else None


ACROBATS = [
    Path(r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe"),
    Path(r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"),
    Path(r"C:\Program Files (x86)\Adobe\Acrobat DC\Acrobat\Acrobat.exe"),
]


def find_acrobat() -> Path | None:
    for cand in ACROBATS:
        if cand.exists():
            return cand
    found = shutil.which("AcroRd32")
    return Path(found) if found else None


def default_printer_name() -> str | None:
    """Acrobat's /t REQUIRES a printer name -- there is no print-to-default form."""
    ps = (
        "(Get-CimInstance Win32_Printer -Filter 'Default=True' "
        "| Select-Object -ExpandProperty Name)"
    )
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True,
            text=True,
            timeout=45,
        )
        name = res.stdout.strip().splitlines()
        return name[0].strip() if name else None
    except (OSError, subprocess.SubprocessError):
        return None


def print_settings_for(sides: str, paper: str) -> str:
    """Build the SumatraPDF -print-settings string. Per JOB, never per queue.

    PRINT_AND_PROCESS_REFERENCE.md (coordination, bc7daf8) rules both halves:

      paper=A4   The queue default is per-seat and NOT canonical -- measured
                 `Letter` on the G-seat and `A4` on the D-seat. A script may not
                 assume either, so every job carries the size. Until this
                 existed, this tool sent no settings at all, and the @page rule
                 above declaring A4 was overridden by whatever the driver
                 defaulted to: the document said A4 and the paper came out
                 Letter, silently.

      sides      A CORRECTNESS rule, not a preference.
                   duplex  -- essays, memos, sitreps, postmortems. Read as a
                              booklet, and it halves the paper.
                   simplex -- checklists and runsheets. They live on a
                              clipboard, and a back face you cannot see while
                              the front is clipped HIDES HALF THE CHECKLIST.
                 Default is duplex because that is this tool's usual input.
                 Anything that gets ticked while clipped needs --sides simplex,
                 and NO heuristic here guesses it -- guessing wrong is the exact
                 failure the rule exists to prevent.

    Mirrors print_settings_for() in coordination/tools/walkpack/build_walkpack.py
    minus its page-range argument, which this tool has no --reverse to feed.
    """
    parts = []
    if sides == "simplex":
        parts.append("simplex")
    elif sides == "short":
        parts.append("duplexshort")
    else:
        parts.append("duplexlong")
    if paper:
        parts.append("paper=%s" % paper)
    return ",".join(parts)


def send_to_printer(
    pdf: Path, printer: str | None, sides: str = "duplex", paper: str = "A4"
) -> None:
    settings = print_settings_for(sides, paper)
    sumatra = find_silent_printer()
    if sumatra:
        # -silent: no window, no dialog, no focus change. Exactly what we want.
        cmd = [str(sumatra), "-silent", "-exit-when-done"]
        cmd += ["-print-to", printer] if printer else ["-print-to-default"]
        cmd += ["-print-settings", settings]
        cmd.append(str(pdf.resolve()))
        print("[print] settings: %s" % settings)
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode != 0:
            raise SystemExit(
                "SumatraPDF print failed (exit %d):\n%s" % (res.returncode, res.stderr[-1200:])
            )
        return

    # Acrobat's own /t switch, BEFORE the shell verb. Measured 2026-08-20 on
    # Pip's machine: `Start-Process -Verb Print` on a PDF returns exit 0, raises
    # nothing, and prints NOTHING -- empty queue, JobCountSinceLastReset stays 0.
    # Five documents were reported sent and none existed. The returncode check
    # below cannot catch that, because the failure IS a clean exit.
    #
    # `AcroRd32.exe /n /t <file> <printer>` spools properly and exits. It steals
    # focus briefly, which is why SumatraPDF stays the preferred path.
    acro = find_acrobat()
    if acro:
        target = printer or default_printer_name()
        if target:
            # Acrobat's /t has no per-job duplex or paper control -- it takes
            # the queue default, which is per-seat and not canonical. So this
            # path CANNOT honour the settings above. Say so, rather than let a
            # clipboard checklist come back duplexed without a word.
            print("[warn] Acrobat fallback cannot set %s -- queue default applies." % settings)
            cmd = [str(acro), "/n", "/t", str(pdf.resolve()), target]
            subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            # Acrobat's exit code is not a reliable success signal either, so the
            # honest report is "handed to the spooler" -- verify with
            # Get-PrintJob if it matters.
            print("[print] handed to %s via Acrobat. Verify with:" % target)
            print('        Get-PrintJob -PrinterName "%s"' % target)
            return

    print("[warn] neither SumatraPDF nor Acrobat found -- falling back to the shell verb.")
    print("       It cannot set %s either; the queue default applies." % settings)
    print("       MEASURED UNRELIABLE on Pip's machine: it can exit 0 and print nothing.")
    if printer:
        ps = (
            'Start-Process -FilePath "%s" -Verb PrintTo -ArgumentList "%s" -PassThru | Out-Null'
            % (
                pdf.resolve(),
                printer,
            )
        )
    else:
        ps = 'Start-Process -FilePath "%s" -Verb Print -PassThru | Out-Null' % pdf.resolve()
    res = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        raise SystemExit("Print failed:\n%s" % res.stderr[-1200:])


def main() -> int:
    ap = argparse.ArgumentParser(description="Print a doc with a 12pt+ legibility floor.")
    ap.add_argument("path", nargs="?", help="a .md or .html file")
    ap.add_argument("--printer", help="exact printer name (see --list-printers)")
    ap.add_argument("--pdf-only", action="store_true", help="render the PDF, do not print")
    ap.add_argument("--out", help="where to write the PDF")
    ap.add_argument(
        "--base-size", type=float, default=12.5, help="body point size (floor 11; default 12.5)"
    )
    ap.add_argument(
        "--sides",
        choices=("duplex", "simplex", "short"),
        default="duplex",
        help="duplex (default; essays, memos, sitreps -- read as a booklet) | "
        "simplex (checklists and runsheets: they live on a clipboard, and a back "
        "face you cannot see hides half the checklist) | short (duplexshort)",
    )
    ap.add_argument(
        "--paper",
        default="A4",
        help="paper size sent WITH THE JOB (default A4). The queue default is "
        "per-seat and not canonical -- do not rely on it.",
    )
    ap.add_argument("--list-printers", action="store_true")
    args = ap.parse_args()

    if args.list_printers:
        return list_printers()
    if not args.path:
        ap.error("a file path is required (or --list-printers)")

    src = Path(args.path)
    if not src.exists():
        raise SystemExit("No such file: %s" % src)

    base = max(11.0, args.base_size)  # the floor is not negotiable
    if base != args.base_size:
        print("[note] base size raised to the 11pt floor.")
    css = HOUSE_CSS % {
        "base": base,
        "h1": round(base * 1.6, 1),
        "h2": round(base * 1.2, 1),
        "h3": round(base * 1.04, 1),
        "mono": round(max(11.0, base * 0.92), 1),
    }

    tmpdir = Path(tempfile.mkdtemp(prefix="printdoc_"))
    if src.suffix.lower() in (".html", ".htm"):
        html_text = src.read_text(encoding="utf-8")
        if "<html" not in html_text.lower():
            # A body fragment (the Artifact convention) -- wrap it, and put the
            # house CSS FIRST so the fragment's own <style> still wins.
            html_text = (
                "<!doctype html><html><head><meta charset='utf-8'>"
                "<style>%s</style></head><body>%s</body></html>" % (css, html_text)
            )
        html_path = tmpdir / "doc.html"
        html_path.write_text(html_text, encoding="utf-8")
    else:
        html_path = tmpdir / "doc.html"
        html_path.write_text(
            md_to_html(src.read_text(encoding="utf-8"), css, src.stem), encoding="utf-8"
        )

    pdf_path = Path(args.out) if args.out else tmpdir / (src.stem + ".pdf")
    render_pdf(find_browser(), html_path, pdf_path)
    size_kb = pdf_path.stat().st_size / 1024
    print("[OK] rendered %s (%.0f KB) at %.1fpt body" % (pdf_path, size_kb, base))

    if args.pdf_only:
        print("[OK] --pdf-only: not printed.")
        return 0

    send_to_printer(pdf_path, args.printer, args.sides, args.paper)
    print("[OK] sent to %s" % (args.printer or "the default printer"))
    print("     If nothing comes out, check the queue -- Windows fails printing silently.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
