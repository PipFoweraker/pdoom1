#!/usr/bin/env python
"""Find closed issues whose own acceptance criteria may never have been checked.

Layer: PROVE

WHY THIS EXISTS
---------------
Pip, 2026-08-22, on discovering that #775 was closed COMPLETED with one of its
three acceptance criteria unmet and no comment recording it: "How do we scan for
anything else closed with zero comments that might have partially completed
work? ew. shadow tech debt is gross."

An issue closed with NO comments is an issue where nobody wrote down what was
actually done. That is not automatically bad -- most such closes are genuinely
trivial. It becomes interesting only when the issue stated criteria that a
reader could have tested and nobody recorded testing them.

WHAT THIS TOOL WILL NOT DO
--------------------------
It does not tell you whether the work was done. It CANNOT: the criteria are
prose, and checking them means reading the tree. It produces a SHORTLIST for a
human, and the shortlist is only useful because it is short.

The first run, 2026-08-22, measured on 426 closed issues:

    closed total                    426
    closed with zero comments       159   (37% -- far too coarse to act on)
      ...with unticked checkboxes    18
      ...with prose acceptance       28

Five were then checked by hand against the tree. FOUR were satisfied (#488,
#481, #531, #720); one had a real gap (#775, filed as #1269). So the base rate
of genuine shadow debt is low, and the scan's value is in making that
measurable rather than assumed.

THE NEGATIVE RESULT THAT MATTERS
--------------------------------
Across all 18 issues carrying unticked checkboxes, the number of TICKED boxes
was ZERO. Not low -- zero. Checkboxes have never been used as live state in this
repository; they are spec text. So "unticked box in a closed issue" carries no
information here, and this tool reports that population separately and says so
rather than letting it inflate the shortlist.

That is worth re-measuring rather than trusting forever: if someone starts
ticking boxes, the signal becomes real and `--boxes` becomes worth reading.

USAGE
    python tools/scan_closed_issue_debt.py              # the shortlist
    python tools/scan_closed_issue_debt.py --boxes      # the checkbox population
    python tools/scan_closed_issue_debt.py --since 700  # only issues above N
    python tools/scan_closed_issue_debt.py --json       # machine-readable

Needs `gh` authenticated. Read-only: it never writes to GitHub.
"""

import argparse
import json
import re
import subprocess
import sys

UNTICKED = re.compile(r"^\s*[-*]\s*\[ \]\s*(.+)$", re.M)
TICKED = re.compile(r"^\s*[-*]\s*\[[xX]\]", re.M)
CRITERIA = re.compile(r"(?im)^.*\b(acceptance|definition of done|done when|success criteria)\b.*$")


def fetch(limit=1000):
    """Every closed issue with its body and comment count."""
    cmd = [
        "gh",
        "issue",
        "list",
        "--state",
        "closed",
        "--limit",
        str(limit),
        "--json",
        "number,title,body,comments,closedAt",
    ]
    try:
        # encoding= is load-bearing on Windows: text=True alone decodes with the
        # ANSI codepage (cp1252 here) and issue bodies are not cp1252. Measured
        # 2026-08-22 -- it raised UnicodeDecodeError on byte 0x8f mid-fetch, which
        # is the good failure. Without errors= a single stray byte would take the
        # whole scan down; with it, one mangled character costs one grep match.
        out = subprocess.run(
            cmd, capture_output=True, timeout=180, encoding="utf-8", errors="replace"
        )
    except (OSError, subprocess.SubprocessError) as e:
        print("[scan] could not run gh: %s" % e, file=sys.stderr)
        return None
    if out.returncode != 0:
        print("[scan] gh failed: %s" % (out.stderr or "").strip()[:300], file=sys.stderr)
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError as e:
        print("[scan] gh returned unparseable JSON: %s" % e, file=sys.stderr)
        return None


def analyse(issues, since=0):
    zero, boxes, prose = [], [], []
    for i in issues:
        if int(i.get("number", 0)) < since:
            continue
        if len(i.get("comments") or []) != 0:
            continue
        zero.append(i)
        body = i.get("body") or ""
        un = UNTICKED.findall(body)
        if un:
            i["_unticked"] = un
            i["_ticked"] = len(TICKED.findall(body))
            boxes.append(i)
            continue  # a checkbox issue is reported in the checkbox population only
        m = CRITERIA.search(body)
        if m:
            i["_criteria"] = m.group(0).strip()
            prose.append(i)
    return zero, boxes, prose


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--boxes",
        action="store_true",
        help="show the checkbox population (see the module docstring: "
        "historically uninformative in this repo)",
    )
    ap.add_argument(
        "--since",
        type=int,
        default=0,
        help="only issues numbered >= N (older ones predate the Godot port)",
    )
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    issues = fetch()
    if issues is None:
        return 2  # DID NOT COMPLETE -- distinct from "found nothing"
    zero, boxes, prose = analyse(issues, args.since)

    if args.json:
        print(
            json.dumps(
                {
                    "closed_total": len(issues),
                    "zero_comment": len(zero),
                    "checkbox_population": [i["number"] for i in boxes],
                    "shortlist": [
                        {
                            "number": i["number"],
                            "title": i["title"],
                            "criteria": i.get("_criteria", ""),
                        }
                        for i in prose
                    ],
                },
                indent=2,
            )
        )
        return 0

    print("closed issues scanned          : %d" % len(issues))
    print("closed with ZERO comments      : %d" % len(zero))
    print("  carrying checkboxes          : %d  (--boxes to list)" % len(boxes))
    print("  carrying prose criteria      : %d  <- the shortlist" % len(prose))

    if args.boxes:
        ticked_total = sum(i.get("_ticked", 0) for i in boxes)
        print("\n--- checkbox population ---")
        print("TICKED boxes across all of them: %d" % ticked_total)
        if ticked_total == 0:
            print("Zero. Checkboxes are spec text in this repo, not state, so an")
            print("unticked box in a closed issue means nothing on its own. Re-measure")
            print("this line before trusting the population either way.")
        for i in sorted(boxes, key=lambda x: -len(x["_unticked"])):
            print("  #%-5d %-58s %d unticked" % (i["number"], i["title"][:58], len(i["_unticked"])))
        return 0

    print("\n--- shortlist: closed, uncommented, and stated criteria a reader could test ---")
    print("This is a list to READ, not a list of defects. Check each against the tree.")
    for i in sorted(prose, key=lambda x: -int(x["number"])):
        print("\n  #%-5d %s" % (i["number"], i["title"][:66]))
        print("         %s" % i["_criteria"][:96])
    print("\nConfirmed shadow debt from the 2026-08-22 run: #775 only (now #1269).")
    print("Four others checked by hand were satisfied. Expect a low hit rate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
