#!/usr/bin/env python3
"""Render the funding budget from data. Every published form, one source.

    render_budget.py --format manifund   # short update, paste into Manifund
    render_budget.py --format table      # the line items, for a page
    render_budget.py --format html       # the whole public page
    render_budget.py --format html --out ../pdoom1-website/public/funding/index.html
    render_budget.py --check             # arithmetic and constraints only

WHY.

RULING: 2026-08-17 -- published figures live in tooling, not prose: the line item is the atom and every rendering is a projection -- flavour: estate-process -- mechanism: tools/render_budget.py --check

Pip's words for it: "Let's put things in tooling, not prose, and then we can
rebuild either and update them easily." The same move already made for art
pull-quotes and event atoms.

The concrete failure it prevents: a budget written as prose in two places
disagrees the moment one is edited, and nobody finds out until a funder adds
the column up. The $500 gap between the minimum-tier line items and the
published minimum has been sitting in the 2026-07-29 submission since the day
it went out. Here it is RECOMPUTED on every render, and `--check` fails if the
stated size stops matching the arithmetic. A gap that is named cannot rot; a
gap described in a sentence can.

WHAT IT REFUSES TO DO.

It will not emit the raised total or days-remaining. Those move daily and a
stale number is worse than none, so they are not in the data and there is no
field for them. `--format html` additionally re-reads its own finished output
and refuses to write it if a forbidden phrase, a non-ASCII byte or an
identification of the project's first backer got in. That guard reads the
emitted bytes, not the template's intentions, which is the only version of the
check worth having.

WHY THE HTML LIVES IN A DIFFERENT REPOSITORY, AND WHAT THAT COSTS.

The data is here in `pdoom1`. The page is served from `pdoom1-website`, whose
`public/` tree is hand-written `index.html` files with no build step of its
own. That leaves three ways to join them and only one of them is safe:

  1. Vendor a copy of `budget.json` into the website. REJECTED. A copy becomes
     a variant on the next edit of either side, which is the exact failure
     `coordination#15` names and which this whole file exists to prevent. It
     would also put a second producer behind the same numbers.
  2. Have the website fetch a published artefact at runtime. REJECTED for now.
     It buys freshness the content does not need -- these figures change when
     Pip decides something, not on a clock -- and pays for it with a page whose
     dollar figures are absent when a fetch fails, on a funding page, which is
     the worst possible failure direction.
  3. THE RENDERER RUNS FROM HERE AND WRITES ACROSS. Chosen. `--out` writes a
     complete page into the website working tree. The website is a read-only
     consumer of a pdoom1 output, exactly as it already is for the art-review
     figures and the served dataset counts.

The cost of (3), stated rather than hidden: the generated page is a derived
copy living in another repository, so it CAN go stale relative to this data.
Two things keep that honest. The render is deterministic -- no timestamps, no
counters -- so re-running with `--out` and finding `git diff` empty in the
website tree is a real drift check anyone can run in one command. And the page
carries `data-budget-sha256`, the hash of the exact `budget.json` it was
rendered from, so the question "is this page current?" is answerable by
comparing two hashes rather than by reading two documents.

    python tools/render_budget.py --format html \\
        --out ../pdoom1-website/public/funding/index.html
    git -C ../pdoom1-website diff --stat public/funding/     # empty == current
"""

import argparse
import datetime as dt
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "docs", "copy", "budget.json")

MARK = {
    "measured": "measured",
    "own_labour": "own labour, own rate",
    "needs_quote": "NEEDS A QUOTE",
    "needs_definition": "NEEDS A DEFINITION",
}


def load():
    with open(os.path.abspath(DATA), encoding="utf-8") as fh:
        return json.load(fh)


def data_sha256():
    """Hash of the exact bytes the render came from. Stamped into the page so a
    reader in the other repository can answer 'is this current?' by comparing
    two hashes rather than by reading two documents."""
    with open(os.path.abspath(DATA), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def usd(n):
    return "--" if n is None else "$%s" % format(n, ",d")


def totals(b):
    tmin = sum(i["min_usd"] or 0 for i in b["line_items"])
    tgoal = sum(i["goal_usd"] or 0 for i in b["line_items"])
    return tmin, tgoal


def check(b):
    """Arithmetic and constraint problems. Empty list means sound."""
    problems = []
    tmin, tgoal = totals(b)
    pub = b["published"]

    gap = pub["minimum_usd"] - tmin
    stated = next((g for g in b["known_gaps"] if g["id"] == "five-hundred"), None)
    if stated is None:
        problems.append("the min-column gap is not declared in known_gaps")
    elif stated["size_usd"] != gap:
        problems.append(
            "gap DRIFTED: line items now leave %s against a declared %s. "
            "Update the declaration or the items -- do not publish either way."
            % (usd(gap), usd(stated["size_usd"]))
        )

    if tgoal != pub["goal_usd"]:
        problems.append(
            "goal column sums to %s, published goal is %s" % (usd(tgoal), usd(pub["goal_usd"]))
        )

    for item in b["line_items"]:
        if item["provenance"] not in b["provenance_vocabulary"]:
            problems.append("%s: unknown provenance %r" % (item["id"], item["provenance"]))
        if item["provenance"] in ("needs_quote", "needs_definition") and not item.get("settled_by"):
            problems.append(
                "%s: unpriced with no settled_by -- say what would "
                "settle it, or the gap reads as vagueness" % item["id"]
            )

    art = b.get("art_measurement", {})
    if art:
        s = art["discarded"] + art["kept"] + 1  # +1 remix
        if s != art["assets_judged"]:
            problems.append(
                "art measurement does not reconcile: %d discarded + %d kept + "
                "1 remix = %d, but assets_judged is %d"
                % (art["discarded"], art["kept"], s, art["assets_judged"])
            )
        if art["slots_with_survivor"] + art["slots_with_nothing_kept"] != art["distinct_slots"]:
            problems.append("art slots do not reconcile")

        # The naive per-slot figure is PUBLISHED as a number, so it has to be
        # the division it claims to be. Drafts of this note carried the
        # superseded 206-slot count, which rounds to the same $30 and so hid
        # itself; this catches the day it stops rounding to the same answer.
        art_goal = next((i["goal_usd"] for i in b["line_items"] if i["id"] == "art"), None)
        naive = art["division"]["naive_per_slot_usd"]
        if art_goal and art["distinct_slots"]:
            recomputed = int(round(float(art_goal) / art["distinct_slots"]))
            if abs(recomputed - naive) > 1:
                problems.append(
                    "naive per-slot DRIFTED: %s over %d slots is about $%d, "
                    "but naive_per_slot_usd says $%d"
                    % (usd(art_goal), art["distinct_slots"], recomputed, naive)
                )
    return problems


def fmt_table(b):
    out = ["| Line item | Minimum | Goal | How the number is known |", "|---|---|---|---|"]
    for i in b["line_items"]:
        basis = i["basis"]
        if i.get("settled_by"):
            basis += " **Settled by:** " + i["settled_by"]
        if i.get("softest_number"):
            basis += " *Softest number here: " + i["softest_number"] + "*"
        out.append(
            "| %s | %s | %s | **%s.** %s |"
            % (i["label"], usd(i["min_usd"]), usd(i["goal_usd"]), MARK[i["provenance"]], basis)
        )
    tmin, tgoal = totals(b)
    out.append("| **Total** | **%s** | **%s** | |" % (usd(tmin), usd(tgoal)))
    return "\n".join(out)


def fmt_manifund(b):
    """Short-form update. Prose is a template; every figure comes from data."""
    p = b["published"]
    tmin, tgoal = totals(b)
    gap = p["minimum_usd"] - tmin
    art = b["art_measurement"]
    unpriced = [
        i for i in b["line_items"] if i["provenance"] in ("needs_quote", "needs_definition")
    ]

    L = []
    L.append("## What the money is actually for")
    L.append("")
    L.append(
        "An update, because asking for %s without showing the working is a "
        "wish rather than a proposal. Below is the whole budget, including "
        "the parts I cannot price yet." % usd(p["minimum_usd"])
    )
    L.append("")
    L.append(
        "**The two numbers buy different things, and the difference is not "
        "scale -- it is who does the work.**"
    )
    L.append("")
    L.append(
        "At **%s**, the project does not stop: hosting, the generation and "
        "tooling budget, the open dataset kept current, and partial "
        "recovery of one focused day a week. Nobody else is paid. The art "
        "keeps improving the way it improved on 14 August -- generate a "
        "lot, throw most away, write down why." % usd(p["minimum_usd"])
    )
    L.append("")
    L.append(
        "At **%s**, somebody other than me draws it. That is the honest "
        "headline, and it cuts against my own ask: **every dollar of the "
        "human-artist line sits above the minimum.** At %s nothing is "
        "commissioned." % (usd(p["goal_usd"]), usd(p["minimum_usd"]))
    )
    L.append("")
    L.append(fmt_table(b))
    L.append("")
    L.append("**Two gaps I would rather name than close.**")
    L.append("")
    L.append(
        "The minimum column sums to %s against a published minimum of %s. "
        "That %s is rounding from the evening I set the figure, not a "
        "hidden line item, and I would rather flag it than retrofit "
        "something to cover it. I also have not established whether the "
        "platform takes a cut; if it does, the gap is larger, and it is "
        "better that I find that out than that you do."
        % (usd(tmin), usd(p["minimum_usd"]), usd(gap))
    )
    L.append("")
    L.append(
        "**%d of the %d line items carry no quote.** I have not invented "
        "rates to make the table look finished; each says what would "
        "settle it." % (len(unpriced), len(b["line_items"]))
    )
    L.append("")
    L.append(
        "**The art line, measured rather than gestured at.** On 14 August "
        "I judged %d generated assets in about 23 minutes and discarded "
        "%d. But %d discards is not %d things that need drawing -- it was "
        "a selection sweep, and decomposed properly those judgements "
        "resolve to **%d distinct slots**, %d with a surviving pick and %d "
        "with nothing worth keeping. Anyone pricing a human pass should "
        "price %d slots, not %d discards. I would rather publish the "
        "correction that lowers my own number than quote the one that "
        "flatters it."
        % (
            art["assets_judged"],
            art["discarded"],
            art["discarded"],
            art["discarded"],
            art["distinct_slots"],
            art["slots_with_survivor"],
            art["slots_with_nothing_kept"],
            art["distinct_slots"],
            art["discarded"],
        )
    )
    L.append("")
    L.append(
        "And the division, which is what I would want to see in somebody "
        "else's budget: %s across %d slots is about $%d a slot. I do not "
        "believe that is a real rate for commissioned illustration and I "
        "am not going to pretend otherwise. %s"
        % (
            usd(
                next(i["goal_usd"] for i in b["line_items"] if i["id"] == "art"),
            ),
            art["distinct_slots"],
            art["division"]["naive_per_slot_usd"],
            art["division"]["hypothesis"],
        )
    )
    L.append("")
    L.append(
        "Nobody has been hired, commissioned or engaged; every figure "
        "describes what the money would pay for. The game is free and "
        "source-available and stays that way -- a pledge funds the work, "
        "not a licence. And it is not finished, which is rather the point."
    )
    L.append("")
    L.append(
        "Closes %s. It is all-or-nothing: below the minimum every pledge "
        "is returned and nobody is out of pocket." % p["closes"]
    )
    return "\n".join(L)


# ----------------------------------------------------------------------------
# HTML
# ----------------------------------------------------------------------------
#
# House rules this page obeys, from pdoom1-website docs/HTML_PAGE_TEMPLATE.md
# and the shape of public/press/index.html. They are restated here as code
# comments and not as a second copy of that document:
#
#   - hand-written index.html per directory; there is no build step in the site
#   - canonical link, meta description of 150-160 characters (asserted below)
#   - Plausible in <head>, before the <style> block
#   - og:image is /assets/og-card.jpg and nothing else
#   - <header> stays EMPTY; navigation.js injects it, at the end of <body>
#   - no footer
#   - HTML entities, never literal characters
#   - NO UTM parameters on on-site links

CANONICAL = "https://pdoom1.com/funding/"

# 150-160 characters, asserted at render time rather than counted by hand.
META_DESCRIPTION = (
    "Where the money goes if p(Doom)1 is funded: every budget line, how far "
    "each figure can be defended, the ones that still need a quote, and the "
    "gap left open."
)

# Labels for art_measurement.slot_breakdown keys. Display text only -- no
# figure is ever read from here, and an unknown key falls back to itself.
SLOT_LABELS = {
    "interface_and_action_icons": "interface and action icons",
    "hero_banners_key_art_backgrounds": "hero banners, key art and screen backgrounds",
    "researcher_portraits": "researcher portraits",
}

# Phrases the finished bytes are searched for, one per line, each tracking an
# entry in the data's `constraints` array. This is deliberately a check on the
# EMITTED PAGE rather than on the template: a guard that inspects the intention
# passes at exactly the moment the intention stops being met.
FORBIDDEN = [
    (r"\braised\b", "the raised total moves daily; constraint 3"),
    (r"\bdays?\s+(left|remaining|to go)\b", "days-remaining moves daily; " "constraint 3"),
    (r"\bpledged so far\b", "a running total by another name; constraint 3"),
    (
        r"first backer|first person to back|only donor|only backer|first funder",
        "identifies the project's first backer by description; constraint 4",
    ),
    (
        r"\b(launch|1\.0|version one|finished game|complete[d]? game)\b",
        "frames an unfinished game as a launch; constraint 5",
    ),
    (
        r"\b(hired|commissioned|engaged|contracted|quoted)\s+(an?|the)\s",
        "reads as though somebody has been engaged; constraint 1",
    ),
]

# Weaker than the above, and named as weaker: these assert that the sections
# discharging constraints 1, 2 and 5 are still present. A positive check like
# this compares the template against itself, so it cannot catch a section that
# was never right -- only one that was deleted.
REQUIRED = [
    ("has been engaged", "the nobody-has-been-engaged statement"),
    ("source-available", "the game-stays-free statement"),
    ("not finished", "the not-a-launch statement"),
]


def esc(s):
    """HTML-escape, then the entity conversions the house rules require. Data
    strings are ASCII by construction (validated upstream), so this only has to
    turn ASCII conventions into entities, never literal characters into them."""
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    s = s.replace(" -- ", " &mdash; ")
    s = re.sub(r"(?<=[A-Za-z])'(?=[A-Za-z])", "&rsquo;", s)
    return s


def usd_html(n):
    return "&mdash;" if n is None else "$%s" % format(n, ",d")


def comment_safe(s):
    """Text bound for an HTML comment.

    Comments do NOT decode entities, so esc() is wrong here -- it would put a
    literal "&rsquo;" in front of a reader who opens the file. And a comment may
    not contain a double hyphen at all: html5lib rejects it, which is how this
    was caught, after the regeneration command line in the header comment made
    the page fail a strict parse on its own `--format` flag. Removing the double
    hyphen also removes the only way to write a premature `-->`."""
    while "--" in s:
        s = s.replace("--", "-")
    return s


WORDS = [
    "no",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
]


def words(n):
    """Small counts read as words in prose. Falls back to the numeral, so this
    can never be the reason a count fails to appear."""
    return WORDS[n] if 0 <= n < len(WORDS) else format(n, ",d")


def long_date(iso):
    d = dt.datetime.strptime(iso, "%Y-%m-%d").date()
    return "%d %s %d" % (d.day, d.strftime("%B"), d.year)


def session_window(art):
    """(date, seconds) for the review session, parsed rather than typed. Returns
    (None, None) if the string is not in the expected shape -- an unparseable
    window means the duration is simply not mentioned, never guessed."""
    m = re.match(
        r"^(\d{4}-\d{2}-\d{2}),\s*(\d{2}:\d{2}:\d{2})\s*to\s*" r"(\d{2}:\d{2}:\d{2})$",
        art.get("session", ""),
    )
    if not m:
        return None, None
    day = dt.datetime.strptime(m.group(1), "%Y-%m-%d").date()
    t0 = dt.datetime.strptime(m.group(2), "%H:%M:%S")
    t1 = dt.datetime.strptime(m.group(3), "%H:%M:%S")
    return day, int((t1 - t0).total_seconds())


def html_gap_paragraphs(b):
    """Prose for known_gaps, COMPOSED from the arithmetic rather than
    transcribed from the data's own sentences.

    The `what` and `explanation` fields spell their figures out in words --
    "sum to $14,000 against a published minimum of $14,500" -- and those
    literals are not covered by check(), which only reconciles `size_usd`. A
    literal transcribed onto a public page is a number that can rot while the
    check stays green, which is the entire failure this tool exists to stop. So
    each gap is composed here from live values, and an id this function does
    not know how to compose REFUSES rather than being silently dropped: adding
    a gap to the data forces a decision about how to say it.

    `handling` is deliberately not rendered anywhere. It is instruction to
    whoever writes the copy, not copy."""
    tmin, _ = totals(b)
    pub = b["published"]
    gap = pub["minimum_usd"] - tmin
    out, unknown = [], []
    for g in b["known_gaps"]:
        if g["id"] == "five-hundred":
            out.append(
                "The minimum column sums to %s against a published minimum of "
                "%s. That %s is %s, and I would rather flag it than retrofit a "
                "line item to cover it."
                % (
                    usd_html(tmin),
                    usd_html(pub["minimum_usd"]),
                    usd_html(gap),
                    (
                        esc(g["explanation"]).rstrip(".").lower()
                        if g["explanation"]
                        else "unexplained"
                    ),
                )
            )
        elif g["id"] == "platform-cut":
            out.append(
                "%s If there is one, the gap above is larger than %s, and it "
                "is better that I find that out than that you do." % (esc(g["what"]), usd_html(gap))
            )
        else:
            unknown.append(g["id"])
    if unknown:
        return None, (
            "known_gaps carries %s, which this renderer has no prose "
            "for. Say it on the page or take it out of the data -- "
            "do not publish a gap the page does not mention." % ", ".join(repr(u) for u in unknown)
        )
    return out, None


def fmt_html(b):
    """The whole public page. Returns (html, problems).

    Not one dollar figure is typed into this function. Every `$` that reaches
    the reader is either formatted from a numeric field, computed from those
    fields, or carried inside a string that budget.json already holds."""
    p = b["published"]
    tmin, tgoal = totals(b)
    # The gap figure is NOT recomputed here: html_gap_paragraphs() owns it, so
    # there is exactly one place the published $500 can come from.
    art = b["art_measurement"]
    items = b["line_items"]

    min_tier = [i for i in items if i["min_usd"]]
    goal_only = [i for i in items if i["min_usd"] is None]
    unpriced = [i for i in items if i["provenance"] in ("needs_quote", "needs_definition")]
    measured = [i for i in items if i["provenance"] == "measured"]
    own = [i for i in items if i["provenance"] == "own_labour"]
    art_item = next((i for i in items if i["id"] == "art"), None)

    gap_paras, gap_problem = html_gap_paragraphs(b)
    if gap_problem:
        return None, [gap_problem]
    if not (150 <= len(META_DESCRIPTION) <= 160):
        return None, [
            "meta description is %d characters; the house rule is "
            "150-160" % len(META_DESCRIPTION)
        ]

    day, seconds = session_window(art)
    minutes = int(round(seconds / 60.0)) if seconds else None
    per_asset = (
        int(round(float(seconds) / art["assets_judged"]))
        if seconds and art.get("assets_judged")
        else None
    )
    listed_slots = sum(art.get("slot_breakdown", {}).values())
    tail_slots = art["distinct_slots"] - listed_slots

    T = []  # tab-indented, like the site
    w = T.append

    w("<!DOCTYPE html>")
    w('<html lang="en-AU">')
    w("<head>")
    w('\t<meta charset="UTF-8">')
    w('\t<meta name="viewport" content="width=device-width, ' 'initial-scale=1.0">')
    w("\t<title>What the money is for - p(Doom)1</title>")
    w('\t<link rel="canonical" href="%s" />' % CANONICAL)
    w('\t<link rel="sitemap" type="application/xml" href="/sitemap.xml" />')
    w('\t<meta name="description" content="%s" />' % esc(META_DESCRIPTION))
    w('\t<meta name="author" content="p(Doom)1" />')
    w('\t<meta property="og:type" content="website" />')
    w('\t<meta property="og:site_name" content="p(Doom)1" />')
    w('\t<meta property="og:title" content="What the money is for - ' 'p(Doom)1" />')
    w('\t<meta property="og:description" content="%s" />' % esc(META_DESCRIPTION))
    w('\t<meta property="og:url" content="%s" />' % CANONICAL)
    w('\t<meta property="og:image" content="https://pdoom1.com/assets/' 'og-card.jpg" />')
    w('\t<meta name="twitter:card" content="summary_large_image" />')
    w("\t<!-- Plausible Analytics - Privacy-first, self-hosted analytics -->")
    w(
        '\t<script defer data-domain="pdoom1.com" src="https://'
        "analytics.pdoom1.com/js/script.file-downloads.outbound-links."
        'pageview-props.tagged-events.js"></script>'
    )
    w(
        "\t<script>window.plausible = window.plausible || function() { "
        "(window.plausible.q = window.plausible.q || []).push(arguments) }"
        "</script>"
    )
    w("\t<style>")
    w(CSS)
    w("\t</style>")
    w("</head>")
    w('<body data-budget-sha256="%s">' % data_sha256())

    # The constraints travel WITH the artefact. Anyone who opens this file in
    # the website repository sees what the copy is not allowed to say, without
    # having to know that budget.json exists.
    w("\t<!--")
    w("\t     GENERATED FILE. Do not hand-edit: the next render overwrites it.")
    w("\t     Source of truth: pdoom1 docs/copy/budget.json")
    w("\t     Renderer:        pdoom1 tools/render_budget.py")
    w("\t     Regenerate:      from a pdoom1 checkout, run render_budget.py")
    w("\t                      with format html and out set to this path. The")
    w("\t                      exact command line is in that file's docstring")
    w("\t                      and cannot be repeated here, because a double")
    w("\t                      hyphen is not legal inside an HTML comment.")
    w("\t     This page is current when a fresh render leaves")
    w("\t     `git diff public/funding/` empty. The render is deterministic:")
    w("\t     no timestamps, no counters, so any diff is a real difference.")
    w("\t     data-budget-sha256 on the body element is the hash of the exact")
    w("\t     budget.json this was rendered from.")
    w("")
    w("\t     Constraints carried by the data. Not machine-checkable in full;")
    w("\t     the renderer greps the finished bytes for the ones that can be.")
    for c in b["constraints"]:
        w("\t       - %s" % comment_safe(c))
    w("")
    w("\t     NOT DECIDED HERE: this is the first reader-visible mention of")
    w("\t     Manifund on the site. Adding /funding/ to navigation.js and to")
    w("\t     sitemap.xml are separate decisions and have not been made.")
    w("\t-->")
    w("")
    w("\t<header>")
    w("\t\t<!-- Navigation loaded by navigation.js -->")
    w("\t</header>")
    w("")
    w("\t<main>")

    # -- hero ---------------------------------------------------------------
    w('\t\t<section class="hero">')
    w("\t\t\t<h1>What the money is for</h1>")
    w(
        "\t\t\t<p>The whole budget behind the p(Doom)1 funding round, including "
        "the parts I cannot price yet.</p>"
    )
    w("\t\t</section>")
    w("")

    # -- the ask ------------------------------------------------------------
    w('\t\t<section class="panel">')
    w("\t\t\t<h2>The ask</h2>")
    w(
        "\t\t\t<p>p(Doom)1 is asking for a minimum of <strong>%s</strong> on "
        '<a href="%s" target="_blank" rel="noopener">Manifund</a>, with a '
        "goal of <strong>%s</strong>, and the round closes on %s.%s Asking for "
        "%s without showing the working is a wish rather than a proposal, so "
        "this page is the working.</p>"
        % (
            usd_html(p["minimum_usd"]),
            esc(p["url"]),
            usd_html(p["goal_usd"]),
            long_date(p["closes"]),
            (
                " It is all-or-nothing: below the minimum every pledge is returned "
                "and nobody is out of pocket."
                if p.get("all_or_nothing")
                else ""
            ),
            usd_html(p["minimum_usd"]),
        )
    )
    w(
        "\t\t\t<p>The live figures are on the Manifund page and are deliberately "
        "not typed here. They move daily, this page does not, and a stale number "
        "is worse than no number at all.</p>"
    )
    w(
        '\t\t\t<p class="note">Neither figure buys a product. The game is free '
        "and source-available and stays that way &mdash; a pledge funds the work, "
        "not a licence, and not early access. p(Doom)1 is also not finished, "
        "which is rather the point of funding it.</p>"
    )
    w("\t\t</section>")
    w("")

    # -- the two numbers ----------------------------------------------------
    w('\t\t<section class="panel">')
    w("\t\t\t<h2>The two numbers, and what each one changes</h2>")
    w("\t\t\t<p>The difference between them is not scale. It is who does the " "work.</p>")
    w('\t\t\t<div class="tiers">')

    w('\t\t\t\t<div class="tier">')
    w("\t\t\t\t\t<h3>At %s, the project does not stop</h3>" % usd_html(p["minimum_usd"]))
    w("\t\t\t\t\t<ul>")
    for i in min_tier:
        w(
            '\t\t\t\t\t\t<li><span class="amt">%s</span> %s</li>'
            % (usd_html(i["min_usd"]), esc(i["label"]))
        )
    w("\t\t\t\t\t</ul>")
    w(
        "\t\t\t\t\t<p>Nobody else is paid anything. The dataset stays maintained "
        "rather than drifting, and the art keeps improving the way it improved on "
        "%s: generate a great deal of it, throw most of it away, and write down "
        "why. That is a real answer to the art problem, but it is not the answer "
        "people mean when they ask about it.</p>"
        % (("%d %s" % (day.day, day.strftime("%B"))) if day else "review day")
    )
    w("\t\t\t\t</div>")

    w('\t\t\t\t<div class="tier">')
    w("\t\t\t\t\t<h3>At %s, somebody other than me draws it</h3>" % usd_html(p["goal_usd"]))
    w("\t\t\t\t\t<ul>")
    for i in goal_only:
        w(
            '\t\t\t\t\t\t<li><span class="amt">%s</span> %s</li>'
            % (usd_html(i["goal_usd"]), esc(i["label"]))
        )
    w("\t\t\t\t\t</ul>")
    if art_item is not None and art_item["min_usd"] is None:
        # Emitted only because the data says so. If the art line ever gains a
        # minimum-tier figure, this sentence disappears instead of lying.
        w(
            "\t\t\t\t\t<p>Every dollar of the human-artist line sits above the "
            "minimum, and at %s none of it is committed. I could have spread that "
            "line across both columns to make the floor look better. The only "
            "public criticism this project has had is that the art looks too "
            "AI-generated, and answering that with a budget that quietly defers "
            "the answer would be worse than not answering at all.</p>" % usd_html(p["minimum_usd"])
        )
    w("\t\t\t\t</div>")

    w("\t\t\t</div>")
    w("\t\t</section>")
    w("")

    # -- the table ----------------------------------------------------------
    w('\t\t<section class="panel">')
    w("\t\t\t<h2>The line items, and how far each number can be defended</h2>")
    w(
        "\t\t\t<p>There are %s lines. %s %s backed by receipts; %s %s marked as "
        "needing a quote or a definition, with the thing that would settle each "
        "one named; and %s %s my own labour priced at my own rate, which is a "
        "decision I made rather than a price anybody quoted me.</p>"
        % (
            words(len(items)),
            words(len(measured)).capitalize(),
            "is" if len(measured) == 1 else "are",
            words(len(unpriced)),
            "is" if len(unpriced) == 1 else "are",
            words(len(own)),
            "is" if len(own) == 1 else "are",
        )
    )
    w('\t\t\t<div class="scroll">')
    w("\t\t\t<table>")
    w("\t\t\t\t<thead>")
    w(
        '\t\t\t\t\t<tr><th>Line item</th><th class="num">Minimum</th>'
        '<th class="num">Goal</th><th>How the number is known</th></tr>'
    )
    w("\t\t\t\t</thead>")
    w("\t\t\t\t<tbody>")
    for i in items:
        known = [
            '<strong class="mark m-%s">%s.</strong> %s'
            % (
                i["provenance"].replace("_", "-"),
                esc(
                    MARK[i["provenance"]].capitalize()
                    if i["provenance"] != "measured"
                    else "Measured"
                ),
                esc(i["basis"]),
            )
        ]
        if i.get("softest_number"):
            known.append("<em>Softest number here: %s</em>" % esc(i["softest_number"]))
        if i.get("settled_by"):
            known.append("<strong>Settled by:</strong> %s" % esc(i["settled_by"]))
        w(
            '\t\t\t\t\t<tr><td><b>%s</b></td><td class="num">%s</td>'
            '<td class="num">%s</td><td>%s</td></tr>'
            % (esc(i["label"]), usd_html(i["min_usd"]), usd_html(i["goal_usd"]), " ".join(known))
        )
    w("\t\t\t\t</tbody>")
    w("\t\t\t\t<tfoot>")
    w(
        '\t\t\t\t\t<tr><td><b>Total</b></td><td class="num"><b>%s</b></td>'
        '<td class="num"><b>%s</b></td><td></td></tr>' % (usd_html(tmin), usd_html(tgoal))
    )
    w("\t\t\t\t</tfoot>")
    w("\t\t\t</table>")
    w("\t\t\t</div>")
    w("\t\t</section>")
    w("")

    # -- the gaps -----------------------------------------------------------
    w('\t\t<section class="panel">')
    w("\t\t\t<h2>Two gaps I would rather name than close</h2>")
    for para in gap_paras:
        w("\t\t\t<p>%s</p>" % para)
    w(
        '\t\t\t<p class="note">A reader who adds the column up and finds it '
        "short with no acknowledgement concludes the table was reverse-engineered "
        "from the ask. One who finds the gap already flagged concludes the "
        "opposite, and is right.</p>"
    )
    w("\t\t</section>")
    w("")

    # -- the art measurement ------------------------------------------------
    w('\t\t<section class="panel">')
    w("\t\t\t<h2>The size of the art problem, measured rather than gestured " "at</h2>")
    w(
        "\t\t\t<p>On %s I judged %s generated assets in %s and discarded %s.%s "
        "That is the measurement the art line should be priced against, and it "
        "needs one correction first &mdash; a correction that cuts the number "
        "down rather than up.</p>"
        % (
            long_date(day.isoformat()) if day else "the review day",
            format(art["assets_judged"], ",d"),
            ("about %d minutes" % minutes) if minutes else "one sitting",
            format(art["discarded"], ",d"),
            (
                (" That is one decision roughly every %s seconds." % words(per_asset))
                if per_asset
                else ""
            ),
        )
    )
    w(
        "\t\t\t<p><strong>%s discards is not %s things that need drawing.</strong> "
        "The session was a selection sweep: several versions of the same slot "
        "competed and the losers were discarded, which is what the process is for. "
        "Decomposed properly, those judgements resolve to <strong>%s distinct "
        "art slots</strong> &mdash; %s with a surviving pick and %s with nothing "
        "worth keeping at all. Anyone pricing a human pass should price %s slots, "
        "not %s discards, and I would rather publish the correction that lowers "
        "my own number than quote the one that flatters it.</p>"
        % (
            format(art["discarded"], ",d"),
            format(art["discarded"], ",d"),
            format(art["distinct_slots"], ",d"),
            format(art["slots_with_survivor"], ",d"),
            format(art["slots_with_nothing_kept"], ",d"),
            format(art["distinct_slots"], ",d"),
            format(art["discarded"], ",d"),
        )
    )
    if art.get("slot_breakdown"):
        w("\t\t\t<p>The slots break down as:</p>")
        w('\t\t\t<ul class="slots">')
        for k, v in art["slot_breakdown"].items():
            w(
                '\t\t\t\t<li><span class="amt">%s</span> %s</li>'
                % (format(v, ",d"), esc(SLOT_LABELS.get(k, k.replace("_", " "))))
            )
        if tail_slots > 0:
            w(
                '\t\t\t\t<li><span class="amt">%s</span> further slots across '
                "smaller sets</li>" % format(tail_slots, ",d")
            )
        w("\t\t\t</ul>")
    if art.get("hero_candidates_judged"):
        w(
            "\t\t\t<p>The hero surfaces are the ones a stranger sees first, and "
            "they are where the sweep was harshest: %s hero candidates judged, %s "
            "kept.</p>"
            % (format(art["hero_candidates_judged"], ",d"), format(art["hero_kept"], ",d"))
        )
    if art_item is not None:
        w(
            "\t\t\t<p>Now the division, which is the part I would want to see in "
            "somebody else&rsquo;s budget. %s across %s slots is about $%s a "
            "slot. I do not believe that is a real rate for commissioned "
            "illustration and I am not going to pretend otherwise. The shape I "
            "think the money actually buys is narrower and more useful. %s</p>"
            % (
                usd_html(art_item["goal_usd"]),
                format(art["distinct_slots"], ",d"),
                format(art["division"]["naive_per_slot_usd"], ",d"),
                esc(art["division"]["hypothesis"]),
            )
        )
        w('\t\t\t<p class="note">%s</p>' % esc(art["division"]["_hypothesis_status"]))
    w("\t\t</section>")
    w("")

    # -- nobody has been hired ----------------------------------------------
    w('\t\t<section class="panel">')
    w("\t\t\t<h2>Nobody has been hired</h2>")
    w(
        "\t\t\t<p>No artist, illustrator, developer or contractor has been "
        "engaged for this project. No rate has been agreed with anyone, and no "
        "approach has been made. Every figure on this page describes what the "
        "money <em>would</em> pay for if the round closes above the minimum; the "
        "conditional tense throughout is not hedging, it is accuracy.</p>"
    )
    w(
        "\t\t\t<p>If it does not fund, the pledges return, nobody loses anything, "
        "and I keep going at the rate I have been going at. The game does not "
        "stop; it stays a thing done in the gaps, the dataset stays a thing "
        "maintained in the gaps, and somebody other than me does not get to draw "
        "it. That is a real outcome and not a catastrophic one, and I would "
        "rather say so than manufacture an emergency.</p>"
    )
    w("\t\t</section>")
    w("")

    # -- close --------------------------------------------------------------
    w('\t\t<section class="panel cta">')
    w(
        "\t\t\t<p>The round closes %s%s</p>"
        % (
            long_date(p["closes"]),
            (
                (
                    ", all-or-nothing at %s. A pledge costs nothing unless it works."
                    % usd_html(p["minimum_usd"])
                )
                if p.get("all_or_nothing")
                else "."
            ),
        )
    )
    w(
        '\t\t\t<p><a class="btn" href="%s" target="_blank" '
        'rel="noopener">Back it on Manifund</a> <a class="btn ghost" '
        'href="/">Play it, free</a></p>' % esc(p["url"])
    )
    w("\t\t</section>")

    w("\t</main>")
    w("")
    w('\t<script src="/assets/js/navigation.js"></script>')
    w("</body>")
    w("</html>")

    return "\n".join(T) + "\n", []


CSS = """\t\t:root {
\t\t\t--bg-primary: #12100f;
\t\t\t--bg-secondary: #1c1917;
\t\t\t--bg-tertiary: #262220;
\t\t\t--text-primary: #ffffff;
\t\t\t--text-secondary: #cfc7bb;
\t\t\t--text-muted: #a79e92;
\t\t\t--accent-primary: #f6a800;
\t\t\t--accent-secondary: #2fd4c2;
\t\t\t--accent-danger: #ff4444;
\t\t\t--border-color: #3a342e;
\t\t\t--radius-sm: 4px;
\t\t\t--radius-md: 6px;
\t\t\t--radius-lg: 10px;
\t\t\t--duration-base: 300ms;
\t\t\t--easing: cubic-bezier(0.2, 0.8, 0.2, 1);
\t\t}

\t\t* { margin: 0; padding: 0; box-sizing: border-box; }

\t\tbody {
\t\t\tfont-family: 'Courier New', monospace;
\t\t\tbackground: var(--bg-primary);
\t\t\tcolor: var(--text-primary);
\t\t\tline-height: 1.6;
\t\t}

\t\theader {
\t\t\tbackground: var(--bg-secondary);
\t\t\tborder-bottom: 2px solid var(--accent-primary);
\t\t\tpadding: 1rem 0;
\t\t\tposition: sticky;
\t\t\ttop: 0;
\t\t\tz-index: 100;
\t\t}

\t\t/* Nav styling lives in navigation.js, scoped to
\t\t   header[data-nav-injected]. Do not re-add nav rules here. */

\t\tmain { max-width: 1100px; margin: 0 auto; padding: 4rem 2rem; }

\t\t.hero { text-align: center; margin-bottom: 3rem; }

\t\t.hero h1 {
\t\t\tfont-size: 2.6rem;
\t\t\tcolor: var(--accent-primary);
\t\t\ttext-shadow: 0 0 20px var(--accent-primary);
\t\t\tmargin-bottom: 1rem;
\t\t}

\t\t.hero p {
\t\t\tfont-size: 1.1rem;
\t\t\tcolor: var(--text-secondary);
\t\t\tmax-width: 640px;
\t\t\tmargin: 0 auto;
\t\t}

\t\t.panel {
\t\t\tbackground: var(--bg-secondary);
\t\t\tborder: 1px solid var(--border-color);
\t\t\tborder-radius: var(--radius-lg);
\t\t\tpadding: 2rem;
\t\t\tmargin-bottom: 2rem;
\t\t}

\t\t.panel h2 {
\t\t\tcolor: var(--accent-primary);
\t\t\tfont-size: 1.5rem;
\t\t\tmargin-bottom: 1.25rem;
\t\t}

\t\t.panel h3 {
\t\t\tcolor: var(--accent-secondary);
\t\t\tfont-size: 1.05rem;
\t\t\tmargin-bottom: 1rem;
\t\t}

\t\t.panel p { margin-bottom: 1rem; max-width: 72ch; }
\t\t.panel p:last-child { margin-bottom: 0; }
\t\t.panel a { color: var(--accent-secondary); }

\t\t.note {
\t\t\tcolor: var(--text-muted);
\t\t\tfont-size: 0.9rem;
\t\t\tborder-left: 3px solid var(--border-color);
\t\t\tpadding-left: 1rem;
\t\t}

\t\t.tiers {
\t\t\tdisplay: grid;
\t\t\tgrid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
\t\t\tgap: 1.5rem;
\t\t}

\t\t.tier {
\t\t\tbackground: var(--bg-tertiary);
\t\t\tborder: 1px solid var(--border-color);
\t\t\tborder-radius: var(--radius-md);
\t\t\tpadding: 1.5rem;
\t\t}

\t\t.tier ul, ul.slots { list-style: none; margin: 0 0 1rem 0; }

\t\t.tier li, ul.slots li {
\t\t\tpadding: 0.4rem 0;
\t\t\tborder-bottom: 1px solid var(--border-color);
\t\t\tcolor: var(--text-secondary);
\t\t\tfont-size: 0.9rem;
\t\t}

\t\t.tier li:last-child, ul.slots li:last-child { border-bottom: none; }

\t\t.amt {
\t\t\tcolor: var(--accent-primary);
\t\t\tfont-weight: bold;
\t\t\tdisplay: inline-block;
\t\t\tmin-width: 5.5rem;
\t\t}

\t\t.scroll { overflow-x: auto; }

\t\ttable {
\t\t\tborder-collapse: collapse;
\t\t\twidth: 100%;
\t\t\tfont-size: 0.82rem;
\t\t\tmin-width: 720px;
\t\t}

\t\tth {
\t\t\ttext-align: left;
\t\t\tfont-size: 0.68rem;
\t\t\tletter-spacing: 0.12em;
\t\t\ttext-transform: uppercase;
\t\t\tcolor: var(--text-muted);
\t\t\tpadding: 0.4rem 0.6rem 0.5rem;
\t\t\tborder-bottom: 1px solid var(--accent-primary);
\t\t}

\t\ttd {
\t\t\tpadding: 0.7rem 0.6rem;
\t\t\tborder-bottom: 1px solid var(--border-color);
\t\t\tvertical-align: top;
\t\t\tcolor: var(--text-secondary);
\t\t}

\t\ttd b, td.num { color: var(--text-primary); }
\t\tth.num, td.num { text-align: right; white-space: nowrap; }
\t\ttfoot td { border-bottom: none; border-top: 2px solid var(--accent-primary); }

\t\t.mark { display: block; margin-bottom: 0.25rem; }
\t\t.m-measured { color: var(--accent-secondary); }
\t\t.m-own-labour { color: var(--text-primary); }
\t\t.m-needs-quote, .m-needs-definition { color: var(--accent-primary); }

\t\t.cta { text-align: center; }
\t\t.cta p { max-width: none; }

\t\t.btn {
\t\t\tbackground: var(--accent-primary);
\t\t\tcolor: var(--bg-primary);
\t\t\ttext-decoration: none;
\t\t\tpadding: 0.75rem 1.5rem;
\t\t\tborder-radius: var(--radius-md);
\t\t\tfont-weight: bold;
\t\t\tdisplay: inline-block;
\t\t\tmargin-top: 1rem;
\t\t}

\t\t.btn.ghost {
\t\t\tbackground: transparent;
\t\t\tcolor: var(--accent-secondary);
\t\t\tborder: 1px solid var(--accent-secondary);
\t\t}

\t\t@media (max-width: 768px) {
\t\t\t.hero h1 { font-size: 1.8rem; }
\t\t\tmain { padding: 2rem 1rem; }
\t\t\t.panel { padding: 1.25rem; }
\t\t}"""


def guard_html(html):
    """Read the finished bytes back and refuse on anything the constraints
    forbid. This runs on the output, not on the template."""
    problems = []
    for i, ch in enumerate(html):
        if ord(ch) > 127:
            line = html[:i].count("\n") + 1
            problems.append(
                "non-ASCII character %r at line %d -- entities, "
                "not literal characters" % (ch, line)
            )
            break
    # A double hyphen inside a comment is invalid HTML and a strict parser
    # rejects the document. This tool's own flags are spelled with one, so the
    # header comment walked straight into it; comment_safe() is the fix and this
    # is the check that the fix was applied everywhere.
    for c in re.findall(r"<!--(.*?)-->", html, flags=re.S):
        if "--" in c:
            problems.append(
                "HTML comment contains a double hyphen, which is " "invalid: %r" % c.strip()[:70]
            )
            break

    # READER-VISIBLE TEXT ONLY. Comments are excluded because the page carries
    # the constraints verbatim, and a constraint has to quote the words it
    # forbids; style and script are excluded because CSS is full of things like
    # `initial-scale=1.0` that mean nothing to a reader. Getting this wrong in
    # the other direction -- grepping the raw file -- made the guard fire on its
    # own viewport tag, which is a guard nobody would keep.
    body = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    body = re.sub(r"<(style|script)\b.*?</\1>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<[^>]+>", " ", body)
    for pattern, why in FORBIDDEN:
        m = re.search(pattern, body, re.I)
        if m:
            problems.append("emitted %r -- %s" % (m.group(0), why))
    for phrase, what in REQUIRED:
        if phrase not in body:
            problems.append("%s is missing (looked for %r)" % (what, phrase))
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", choices=("manifund", "table", "html"))
    ap.add_argument("--check", action="store_true")
    ap.add_argument(
        "--out",
        metavar="PATH",
        help="write the render to PATH instead of stdout. The "
        "intended target is the website working tree: "
        "../pdoom1-website/public/funding/index.html",
    )
    args = ap.parse_args()

    b = load()
    problems = check(b)

    if args.check or not args.format:
        for p in problems:
            print("FAIL: %s" % p)
        if problems:
            return 1
        tmin, tgoal = totals(b)
        print(
            "CHECK OK: %d line items; min column %s, goal column %s; "
            "declared gap %s reconciles."
            % (
                len(b["line_items"]),
                usd(tmin),
                usd(tgoal),
                usd(b["published"]["minimum_usd"] - tmin),
            )
        )
        print("Constraints carried (not machine-checkable, honour them):")
        for c in b["constraints"]:
            print("  - %s" % c)
        return 0

    if problems:
        sys.stderr.write("REFUSING to render: the data does not reconcile.\n")
        for p in problems:
            sys.stderr.write("  %s\n" % p)
        return 1

    if args.format == "html":
        out, problems = fmt_html(b)
        if out is not None:
            problems = problems + guard_html(out)
        if problems:
            sys.stderr.write("REFUSING to emit the page.\n")
            for p in problems:
                sys.stderr.write("  %s\n" % p)
            return 1
    elif args.format == "manifund":
        out = fmt_manifund(b) + "\n"
    else:
        out = fmt_table(b) + "\n"

    if args.out:
        path = os.path.abspath(args.out)
        parent = os.path.dirname(path)
        if not os.path.isdir(parent):
            sys.stderr.write(
                "REFUSING to write: %s does not exist. Create the "
                "directory deliberately -- this tool writes into "
                "ANOTHER repository and should not invent paths "
                "in it.\n" % parent
            )
            return 1
        # Never open an existing file with a restrictive encoding for writing:
        # Python truncates on open and raises afterwards, destroying the file
        # before the error surfaces. Temp file, then os.replace.
        tmp = path + ".tmp"
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(out)
        os.replace(tmp, path)
        sys.stderr.write("wrote %s (%d bytes)\n" % (path, len(out)))
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
