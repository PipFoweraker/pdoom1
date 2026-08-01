#!/usr/bin/env python3
"""Reconstruct how much TIME a git history actually cost -- six ways, side by side.

WHY THIS EXISTS. Pip, 2026-08-01: the roadmap projections are "not actually based on
anything right now other than a momentum I built by kinda sacrificing time and attention
at my CEO job, which I can't sustainably do." A roadmap needs a velocity; a velocity
needs hours; nobody recorded hours. The raw material to reconstruct them is in the git
history and will never be more recoverable than now.

THE PROBLEM WITH ONE ESTIMATOR. Any single method embeds an assumption you cannot check
-- "a session ends after 30 idle minutes", "an active day is 4 hours". Pick one and you
get a number with false precision. So this emits SIX, labelled A-F, over the same data.
Pip's instruction: "give me lots of reconstruction options so I can narrow based on
experiencing them... let me A B C test them."

The spread between estimators IS the finding. If A says 20h and E says 60h, the honest
answer is "somewhere in there, and here is why they disagree" -- which is far more useful
than a confident 34.5.

ANTI-GOODHART NOTE, and it is Pip's own ruling (2026-08-02): these numbers are for
"satisfaction and storytelling and mood-adding things, NOT goodharting ourselves". A
velocity used to PREDICT is a measurement. A velocity used as a TARGET stops measuring
the moment anyone optimises for it. Commits are especially easy to game and easy to
inflate accidentally (an agent lane pushing per-step looks like ten times the work).
Treat every number here as a lower-confidence input to a judgement, never as a score.

    python tools/velocity_report.py
    python tools/velocity_report.py --out art_generated/velocity/report.html
    python tools/velocity_report.py --repo ../pdoom1-website
"""

from __future__ import annotations

import argparse
import html
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# Windows we report over. Name -> (days back, or None for all history).
WINDOWS = [
    ("League week (Mon 27 Jul -> Sun 2 Aug)", 7),
    ("Last 14 days", 14),
    ("Last 30 days", 30),
    ("June baseline (31-60 days back)", None),  # handled specially
    ("All history", None),
]

BOT_MARKERS = ("bot]", "[bot", "copilot", "github-actions")


def git(repo: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if out.returncode != 0:
        raise SystemExit("git failed: %s\n%s" % (" ".join(args), out.stderr[-800:]))
    return out.stdout


def load_commits(repo: Path) -> list[dict]:
    """Every commit as {when, author, is_bot, files, ins, del}. Newest first."""
    raw = git(
        repo,
        "log",
        "--all",
        "--no-merges",
        "--date=iso-strict",
        "--pretty=format:@@@%H|%ad|%an",
        "--numstat",
    )
    commits: list[dict] = []
    cur: dict | None = None
    for line in raw.splitlines():
        if line.startswith("@@@"):
            if cur:
                commits.append(cur)
            sha, when, author = line[3:].split("|", 2)
            cur = {
                "sha": sha,
                "when": datetime.fromisoformat(when),
                "author": author,
                "is_bot": any(m in author.lower() for m in BOT_MARKERS),
                "files": 0,
                "ins": 0,
                "dels": 0,
            }
        elif line.strip() and cur is not None:
            parts = line.split("\t")
            if len(parts) == 3:
                cur["files"] += 1
                for idx, key in ((0, "ins"), (1, "dels")):
                    if parts[idx].isdigit():
                        cur[key] += int(parts[idx])
    if cur:
        commits.append(cur)
    return commits


def sessions(times: list[datetime], gap_min: int, lead_in_min: int) -> tuple[float, int]:
    """Cluster timestamps into work sessions. Returns (hours, session_count).

    A session is a run of commits each within gap_min of the previous. Its duration is
    first-to-last PLUS lead_in_min, because the work before the first commit of a session
    is invisible to git and is emphatically not zero. A lone commit counts as lead_in_min.
    """
    if not times:
        return 0.0, 0
    ts = sorted(times)
    total = 0.0
    count = 1
    start = prev = ts[0]
    for t in ts[1:]:
        if (t - prev).total_seconds() / 60.0 > gap_min:
            total += (prev - start).total_seconds() / 3600.0 + lead_in_min / 60.0
            count += 1
            start = t
        prev = t
    total += (prev - start).total_seconds() / 3600.0 + lead_in_min / 60.0
    return total, count


def active_days(times: list[datetime]) -> int:
    return len({t.date() for t in times})


def daily_span_hours(times: list[datetime]) -> float:
    """Sum of first-commit-to-last-commit per day. Generous: counts lunch as work."""
    by_day: dict = defaultdict(list)
    for t in times:
        by_day[t.date()].append(t)
    total = 0.0
    for day_times in by_day.values():
        if len(day_times) > 1:
            total += (max(day_times) - min(day_times)).total_seconds() / 3600.0
        else:
            total += 0.5
    return total


def estimators(times: list[datetime], n_commits: int) -> list[tuple]:
    """(label, name, hours, the assumption you are buying)."""
    a, a_n = sessions(times, 30, 20)
    b, b_n = sessions(times, 60, 30)
    c, c_n = sessions(times, 15, 10)
    d_days = active_days(times)
    d = d_days * 4.0
    e = daily_span_hours(times)
    f = n_commits * 12.0 / 60.0
    return [
        (
            "A",
            "Sessions, 30 min gap, +20 min lead-in",
            a,
            "a pause over 30 min ends a session; 20 min of unlogged thinking precedes each",
            "%d sessions" % a_n,
        ),
        (
            "B",
            "Sessions, 60 min gap, +30 min lead-in",
            b,
            "long pauses are still one session; more unlogged setup per session",
            "%d sessions" % b_n,
        ),
        (
            "C",
            "Sessions, 15 min gap, +10 min lead-in",
            c,
            "tight bursts only; the most conservative reading",
            "%d sessions" % c_n,
        ),
        (
            "D",
            "Active days x 4 h",
            d,
            "any day with a commit was a half-day of work",
            "%d active days" % d_days,
        ),
        (
            "E",
            "First-to-last commit span per day",
            e,
            "everything between the day's first and last commit was work (counts lunch)",
            "upper bound",
        ),
        (
            "F",
            "Commits x 12 min",
            f,
            "every commit cost a flat 12 minutes, regardless of size",
            "crudest",
        ),
    ]


def window_times(
    commits: list[dict], days: int | None, offset: int = 0, include_bots: bool = False
) -> list[dict]:
    sel = commits if include_bots else [c for c in commits if not c["is_bot"]]
    if days is None:
        return sel
    now = max(c["when"] for c in commits)
    hi = now - timedelta(days=offset)
    lo = hi - timedelta(days=days)
    return [c for c in sel if lo < c["when"] <= hi]


def bar(value: float, peak: float, width_mm: int = 60) -> str:
    w = 0 if peak <= 0 else max(0.4, value / peak * width_mm)
    return (
        '<span style="display:inline-block;height:3.6mm;background:#1a1a1a;'
        'width:%.2fmm;vertical-align:-0.6mm"></span>' % w
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Reconstruct effort from git history, six ways.")
    ap.add_argument("--repo", default=".", help="repo to analyse")
    ap.add_argument("--out", default="art_generated/velocity/VELOCITY_REPORT.html")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    commits = load_commits(repo)
    if not commits:
        raise SystemExit("no commits found")

    human = [c for c in commits if not c["is_bot"]]
    bots = [c for c in commits if c["is_bot"]]
    first, last = min(c["when"] for c in commits), max(c["when"] for c in commits)

    P: list[str] = []
    P.append("<title>Velocity reconstruction -- %s</title>" % html.escape(repo.name))
    P.append(
        """<style>
@page { size: A4 portrait; margin: 13mm 12mm; }
html { font-size: 12.5pt; }
body { font-family: "Segoe UI", Calibri, Arial, sans-serif; line-height:1.4; color:#000;
       background:#fff; max-width:190mm; margin:0 auto; }
h1 { font-size:18pt; margin:0 0 2mm; }
h2 { font-size:14.5pt; margin:6mm 0 2mm; padding:1.7mm 2.5mm; background:#1a1a1a;
     color:#fff; page-break-after:avoid; }
h3 { font-size:13pt; margin:4mm 0 1.5mm; page-break-after:avoid; }
p,li,td,th { font-size:12.5pt; }
table { border-collapse:collapse; width:100%; margin:2.5mm 0 4mm; }
th,td { border:1px solid #444; padding:2mm 2.4mm; text-align:left; vertical-align:top; }
th { background:#e8e8e8; font-weight:700; }
td.num { text-align:right; white-space:nowrap; font-weight:700; }
td.lab { white-space:nowrap; font-weight:700; width:8mm; text-align:center; }
.box { border:2.2pt solid #000; padding:3mm 3.5mm; margin:4mm 0; page-break-inside:avoid; }
.box.hi { border-width:3pt; background:#f2f2f2; }
.note { font-size:11.5pt; color:#222; }
.chk { display:inline-block; width:5mm; height:5mm; border:1.7pt solid #000;
       margin-right:2.4mm; vertical-align:-0.8mm; }
code { font-family:Consolas,"Courier New",monospace; font-size:11.5pt; background:#eee; }
.pb { page-break-before:always; }
.foot { font-size:11.5pt; color:#333; border-top:1.2pt solid #999; margin-top:5mm;
        padding-top:2mm; }
@media (prefers-color-scheme: dark) { html,body { background:#fff; color:#000; } }
</style>"""
    )

    P.append("<h1>Velocity reconstruction -- %s</h1>" % html.escape(repo.name))
    P.append(
        '<p class="note">%s commits (%s human, %s bot/agent) from %s to %s. '
        "Generated %s.</p>"
        % (
            len(commits),
            len(human),
            len(bots),
            first.date(),
            last.date(),
            last.strftime("%Y-%m-%d %H:%M"),
        )
    )

    P.append(
        '<div class="box hi"><h3 style="margin-top:0">How to use this</h3>'
        "<p>Six estimators, <b>A</b> to <b>F</b>, over the same commits. They disagree "
        "because each buys a different assumption, stated in its row. "
        "<b>The spread is the finding.</b> Read the assumptions, decide which one "
        "describes how you actually worked, and use that column. Do not average them -- "
        "an average of six assumptions is an assumption nobody holds.</p>"
        "<p style='margin-bottom:0'><b>Anti-Goodhart, your own ruling:</b> these are for "
        "storytelling and for sizing a roadmap you can keep. The moment a number becomes "
        "a target it stops measuring. Commits are trivially gameable and inflate by "
        "accident -- an agent lane pushing per-step looks like ten times the work.</p>"
        "</div>"
    )

    win_defs = [
        ("League week (last 7 days)", 7, 0),
        ("Last 14 days", 14, 0),
        ("Last 30 days", 30, 0),
        ("Baseline: 31-60 days back", 30, 30),
        ("Baseline: 61-90 days back", 30, 60),
        ("All history", None, 0),
    ]

    for title, days, offset in win_defs:
        sel = window_times(commits, days, offset)
        times = [c["when"] for c in sel]
        ins = sum(c["ins"] for c in sel)
        dels = sum(c["dels"] for c in sel)
        P.append("<h2>%s</h2>" % html.escape(title))
        if not times:
            P.append("<p><i>No human commits in this window.</i></p>")
            continue
        rows = estimators(times, len(times))
        peak = max(r[2] for r in rows) or 1.0
        P.append(
            '<p class="note">%d human commits &middot; +%s / -%s lines &middot; '
            "%d active days</p>" % (len(times), f"{ins:,}", f"{dels:,}", active_days(times))
        )
        P.append(
            "<table><tr><th>&nbsp;</th><th>Estimator</th><th>Hours</th>"
            "<th>&nbsp;</th><th>The assumption you are buying</th></tr>"
        )
        for lab, name, hours, assumption, extra in rows:
            P.append(
                "<tr><td class='lab'>%s</td><td>%s<br><span class='note'>%s</span></td>"
                "<td class='num'>%.1f</td><td>%s</td><td class='note'>%s</td></tr>"
                % (
                    lab,
                    html.escape(name),
                    html.escape(extra),
                    hours,
                    bar(hours, peak),
                    html.escape(assumption),
                )
            )
        P.append("</table>")
        lo = min(r[2] for r in rows)
        hi = max(r[2] for r in rows)
        P.append(
            '<p class="note"><b>Spread: %.1f h to %.1f h</b> (%.1fx). '
            "Widest disagreement is between the tightest session model and the "
            "daily-span upper bound -- i.e. how much of the gap between commits was "
            "work.</p>" % (lo, hi, (hi / lo) if lo else 0)
        )

    # ---- weekly series -------------------------------------------------------------
    P.append('<h2 class="pb">Weekly shape -- the burst, and what preceded it</h2>')
    by_week: Counter = Counter()
    for c in human:
        iso = c["when"].isocalendar()
        by_week["%d-W%02d" % (iso[0], iso[1])] += 1
    weeks = sorted(by_week)[-20:]
    peak = max((by_week[w] for w in weeks), default=1)
    P.append("<table><tr><th>ISO week</th><th>Human commits</th><th>&nbsp;</th></tr>")
    for w in weeks:
        P.append(
            "<tr><td>%s</td><td class='num'>%d</td><td>%s</td></tr>"
            % (w, by_week[w], bar(by_week[w], peak, 90))
        )
    P.append("</table>")

    P.append(
        '<div class="box hi"><h3 style="margin-top:0">The number that matters most</h3>'
        "<p style='margin-bottom:0'>The recent weeks are not a velocity, they are a "
        "<b>burst</b>. Compare the league weeks against the baseline windows above. A "
        "roadmap built on the burst assumes a person who does not exist on an ordinary "
        "week, and missing it will read as personal failure rather than as a bad "
        "baseline. <b>The sustainable number is the quiet weeks, possibly plus a "
        "little.</b></p></div>"
    )

    # ---- when do you work ----------------------------------------------------------
    P.append("<h2>When the work happened</h2>")
    hours_c: Counter = Counter(c["when"].hour for c in human)
    peak = max(hours_c.values()) if hours_c else 1
    P.append(
        "<h3>By hour of day</h3><table><tr><th>Hour</th><th>Commits</th>" "<th>&nbsp;</th></tr>"
    )
    for h in range(24):
        band = "core work hours" if 9 <= h < 18 else ("night" if h < 6 or h >= 22 else "")
        P.append(
            "<tr><td>%02d:00 <span class='note'>%s</span></td><td class='num'>%d</td>"
            "<td>%s</td></tr>" % (h, band, hours_c.get(h, 0), bar(hours_c.get(h, 0), peak, 80))
        )
    P.append("</table>")
    office = sum(v for h, v in hours_c.items() if 9 <= h < 18)
    total = sum(hours_c.values()) or 1
    P.append(
        '<p class="note"><b>%.0f%% of commits land between 09:00 and 18:00</b> -- the '
        "hours a CEO job also wants. That share is the clearest available proxy for "
        "how much of this was funded by displacing the day job, and it is the number "
        "to watch if sustainability is the goal.</p>" % (office / total * 100)
    )

    dow_c: Counter = Counter(c["when"].strftime("%a") for c in human)
    order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    peak = max(dow_c.values()) if dow_c else 1
    P.append(
        "<h3>By day of week</h3><table><tr><th>Day</th><th>Commits</th>" "<th>&nbsp;</th></tr>"
    )
    for d in order:
        P.append(
            "<tr><td>%s</td><td class='num'>%d</td><td>%s</td></tr>"
            % (d, dow_c.get(d, 0), bar(dow_c.get(d, 0), peak, 80))
        )
    P.append("</table>")
    wknd = dow_c.get("Sat", 0) + dow_c.get("Sun", 0)
    P.append('<p class="note">Weekend share: <b>%.0f%%</b>.</p>' % (wknd / total * 100))

    # ---- decision ------------------------------------------------------------------
    P.append("<h2>Pick one</h2>")
    P.append(
        "<table><tr><th>&nbsp;</th><th>Choose the estimator that matches how you "
        "actually worked</th></tr>"
    )
    for lab, name, _h, assumption, _e in estimators([c["when"] for c in human], len(human)):
        P.append(
            "<tr><td class='lab'><span class='chk'></span></td><td><b>%s</b> -- %s"
            "<br><span class='note'>Buying: %s</span></td></tr>"
            % (lab, html.escape(name), html.escape(assumption))
        )
    P.append("</table>")
    P.append(
        '<p class="note">Then: sustainable weekly hours x (commits per hour from your '
        "chosen estimator) = a roadmap you can keep. Both terms are guesses; stating "
        "them makes the guess auditable instead of invisible.</p>"
    )

    P.append(
        '<p class="foot">tools/velocity_report.py &middot; %s &middot; bots excluded '
        "from all estimates (%d bot commits) &middot; not a score</p>"
        % (last.strftime("%Y-%m-%d %H:%M"), len(bots))
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(P), encoding="utf-8")
    print("[OK] wrote %s" % out)
    print(
        "     %d commits (%d human, %d bot), %s -> %s"
        % (len(commits), len(human), len(bots), first.date(), last.date())
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
