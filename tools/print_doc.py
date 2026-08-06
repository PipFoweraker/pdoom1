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
table { border-collapse: collapse; width: 100%%; margin: 2.5mm 0 4mm; }
th, td { border: 1px solid #444; padding: 2.2mm 2.6mm; text-align: left; vertical-align: top; }
th { background: #e8e8e8; font-weight: 700; }
code, pre { font-family: Consolas, "Courier New", monospace; font-size: %(mono)spt; }
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


def send_to_printer(pdf: Path, printer: str | None) -> None:
    sumatra = find_silent_printer()
    if sumatra:
        # -silent: no window, no dialog, no focus change. Exactly what we want.
        cmd = [str(sumatra), "-silent"]
        cmd += ["-print-to", printer] if printer else ["-print-to-default"]
        cmd.append(str(pdf.resolve()))
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode != 0:
            raise SystemExit(
                "SumatraPDF print failed (exit %d):\n%s" % (res.returncode, res.stderr[-1200:])
            )
        return

    print("[warn] SumatraPDF not found -- falling back to the shell print verb.")
    print("       That opens whatever owns .pdf (often Acrobat) and WILL steal focus.")
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

    send_to_printer(pdf_path, args.printer)
    print("[OK] sent to %s" % (args.printer or "the default printer"))
    print("     If nothing comes out, check the queue -- Windows fails printing silently.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
