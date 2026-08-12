# Commitments -- the declaration convention, and the ones this repo has made

This file is HAND-EDITED. It holds three things:

1. the convention a human writes so a parser can read a date exactly,
2. the horizon the prose scan works from,
3. the declarations whose natural home is outside this repo (another repo's
   issue, a cadence Pip stated out loud) and therefore have nowhere else to live.

Declarations may live in **any** tracked text file. Prefer putting one next to
the fact it is about -- `docs/art/PIXELLAB_OPERATIONS.md` declares its own spend
policy expiry, three lines under the policy -- because a declaration that lives
beside its fact gets corrected when the fact does.

Generated from this file and the rest of the written record:

- `docs/calendar/pdoom1-commitments.ics` -- the calendar
- `docs/calendar/COMMITMENTS_INDEX.md` -- the human-readable index

Regenerate: `python scripts/generate_commitment_calendar.py`

CALENDAR-HORIZON: 2026-08-09

---

## 1. The convention

One line. No file to open, no schema, no ID to allocate, no YAML block:

```
COMMITMENT: <YYYY-MM-DD> -- <what> -- owner: <who> [-- kind: <kind>] [-- lead: <Nd,Nd>] [-- covers: <path,path>] [-- note: <text>]
COMMITMENT: every <DAY>[,<DAY>] -- <what> -- owner: <who> -- kind: cadence -- from: <YYYY-MM-DD> [-- until: <YYYY-MM-DD>]
```

### Why this form and not another

**Why a one-line marker rather than a YAML front-matter block or a dedicated
registry file.** The measured failure mode here is not that people record dates
badly -- eleven were recorded correctly and none fired. It is that recording
costs more than the moment of noticing. A convention that needs a file opened,
a schema recalled or an ID allocated will lose to typing the date in prose,
every time, and then we are back to a scraper guessing. This one is cheap enough
to write mid-sentence in a handover, an issue body, a `.gd` comment or a commit
message, and it reads correctly to somebody who has never seen the convention.

**Why only the DATE is positional.** House ASCII style (issue #744) makes ` -- `
the em-dash, so ` -- ` appears constantly inside ordinary titles. A parser that
split positionally on ` -- ` would corrupt every second declaration. So: the date
is matched first and exactly; `owner:` `kind:` `lead:` `covers:` `from:` `until:`
`note:` are keyword-extracted from anywhere after it; anything left over is the
title, rejoined with ` -- `. A title containing dashes survives intact.

**Why `owner:` is mandatory and the parse FAILS without it.** The week's
measurement found the load-bearing column was not the date but the who: an
obligation another repo is publicly waiting on behaves nothing like an intention
somebody expressed once. An unowned commitment is a wish. The generator reports
a missing owner as MALFORMED in the index rather than defaulting it, because a
default owner is how everything ends up assigned to Pip.

**Why a payload containing `<` is skipped.** That is how this section can
document the grammar inside a file the scanner reads. It costs one character of
discipline and removes the need for an exclusion list.

**Known weakness, stated rather than discovered later:** the parser will happily
accept a date that is wrong. It checks form, not truth. A declaration typed as
`<2027>-08-13` for something due next week parses green and fires a year late. Nothing
here detects that, and the index's Source column is the only defence -- which is
why every event carries its file and line.

### Kinds, and the reminder lead times each gets

A lodgement deadline and a recurring dev day want different warnings. Uniform
reminders are how a calendar gets muted.

| Kind | Days' warning | Reasoning |
|---|---|---|
| `deadline` | 14, 7, 2, 0 | External, missable, irrecoverable. Manifund does not accept late. Long lead because the work is upstream of the date |
| `expiry` | 7, 1, 0 | A fact stops being true whether or not anyone acts. Nothing to prepare, so no 14-day warning -- but you want it before, not after, so you do not act on an expired policy |
| `review` | 14, 3, 0 | A scheduled re-decision. The 14-day lead is the one that matters: a review with no prepared position becomes a rubber stamp |
| `handoff` | 3, 1, 0 | Another party is waiting and can see whether you delivered. Short lead, because the cost of missing it is social and immediate |
| `release` | 7, 1, 0 | The monthly train. A week is the observed cut-to-ship time |
| `falsifier` | 1, 0 | A check to RUN on a date, usually a one-line command. Warning early is useless -- you cannot run it before the date |
| `task` | 2, 0 | Default. Something to do |
| `cadence` | 0 | Day-of only, 08:00. **Deliberately minimal**: a reminder for a thing you already do every Thursday is the single fastest way to teach yourself to swipe the whole calendar away unread |
| `unparsed` | 0 | Not a commitment. A prompt to classify one |

Override with `lead: 21d,7d` when a specific item disagrees.

### What does NOT belong in this calendar

A calendar of everything is ignored, which costs more than having none. The bar
is all three:

1. **It has a date.** `ship:next-release` (28 issues) and `ship:hotpatch-48h`
   (9 issues) are *tiers*, not dates. `hotpatch-48h` looks like a deadline but
   the 48 hours run from label application, and GitHub does not record when a
   label was applied in any field this generator can read offline. So they are
   out, and that is a gap worth naming rather than a date worth inventing.
2. **Something changes on that date whether or not anyone acts, or somebody
   outside this seat is waiting.** The spend policy expires on 08-15 with nobody
   touching it. `coordination#32` has pdoom1 named in public as the blocking
   party. Both qualify. "I would like to do X soon" does not.
3. **Missing it costs more than reading it.** This is the one that excludes the
   long tail.

Explicitly excluded, with reasons:

- **GitHub milestones.** Four exist; the nearest due date is 2026-09-29 and one
  is 8 months overdue. Importing decorative due dates teaches the calendar is
  fiction, and one fictional entry discredits the true ones beside it.
- **Every open issue without a date.** 211 open issues is a backlog. A backlog in
  a calendar is a backlog you now also cannot use as a calendar.
- **PR review queues.** They are urgent and they are not dated; a date invented
  for them would be the defect this repo measured itself at 8.8% for.
- **Past dates.** A calendar of the past is a log. `CHANGELOG.md` is excluded
  from the scan for the same reason.

### How an item LEAVES the calendar -- and the part that is not solvable here

When an issue closes or a commitment is met, delete or amend the declaration and
regenerate. The event disappears from the `.ics`. That is the whole mechanism,
and whether it reaches Pip depends entirely on how he took the file:

- **Subscribed** (calendar app polls a URL): the feed is replaced wholesale on
  each poll, so a removed event genuinely disappears. This is the only route that
  retracts.
- **Imported** (one-shot file open): **it cannot be retracted.** The events are
  copies in his calendar's own database now; regenerating this file does not
  reach them. Stable UIDs mean a *re-import* will update the events that still
  exist, but an event that has been deleted from the source is simply not in the
  new file, so nothing tells the calendar to remove it. It sits there forever.

**That is not a limitation this script can engineer around, and pretending
otherwise would be worse than saying it.** The half-measure available -- keeping
cancelled events in the file with `STATUS:CANCELLED` for a grace period -- needs
the generator to remember what it emitted last time, which means state, which
means the state can drift from the sources and be silently wrong. Given what this
repo spent the weekend cataloguing, a known limitation beats a stateful mechanism
that might lie.

**So: subscribe rather than import.** The route is in section 4.

---

## 2. Declarations

Kept here only where the fact's home is another repo, or where the fact is a
cadence with no document of its own. Everything else is declared beside its fact
and appears in the generated index with its own file and line.

### The coming week

COMMITMENT: 2026-08-10 -- IP / trademark: take the five-point brief to Australian lawyers -- owner: pip -- kind: deadline -- note: pdoom1#1061. Already slipped once, 2026-08-03 to 2026-08-10. The issue wrote its own escalation rule for a second slip and that rule has no executor.

COMMITMENT: 2026-08-10 -- Read the Workshop 2 minute (ten rulings R1-R10) -- owner: pip -- kind: task -- note: coordination#47, closed 11:35 AEST 2026-08-09. Pip was absent by design.

COMMITMENT: 2026-08-10 -- Book the half-day audit-mechanics workshop, target window opens -- owner: pip -- kind: task -- note: pdoom1#984, ruled 2026-07-27 18:11. Scheduled to precede the 2026-08-31 formal review, which is the only reason it lands this week.

COMMITMENT: 2026-08-13 -- Answer coordination#32: can asset provenance be captured retroactively -- owner: pdoom1-seat -- kind: handoff -- covers: docs/design/ASSET_PROVENANCE_SCOPE_2026-08-06.md, docs/design/ART_RUN_2026-08-07.md -- note: pdoom1 named ITSELF the blocking party in public and pdoom1-website is waiting. One of only two open coordination issues carrying a return date.

COMMITMENT: 2026-08-16 -- Workshop 2 C5: four cross-repo bets scored, pdoom1 owes three RED run IDs -- owner: pdoom1-seat -- kind: handoff -- note: coordination#47 chair ruling R6 adopted pdoom1's red-run rule as the standard all four bets are scored against. Falsifier at docs/workshop-2/position.md:545-552 -- fewer than three run IDs means the bet was named and not operated.

### Cadence

Recorded 2026-08-06 (`docs/HANDOVER_2026-08-06_EVENING.md:163`): *"Thursday dev,
Friday push. Friday is an ordinary patch day."* Expanded to concrete dates rather
than emitted as an RRULE, so each occurrence stays individually traceable in the
index and the widest set of clients can read the file. Bounded at 8 weeks, not a
year, because a cadence stated once in a handover is not a commitment to 52 of
them -- re-declare it when it is still true.

COMMITMENT: every TH -- Thursday dev (the working half of the cadence) -- owner: pip -- kind: cadence -- from: 2026-08-13 -- until: 2026-10-08 -- note: docs/HANDOVER_2026-08-06_EVENING.md:163

COMMITMENT: every FR -- Friday push -- an ordinary patch day, epoch-breaking changes only if player experience demands it -- owner: pip -- kind: cadence -- from: 2026-08-14 -- until: 2026-10-09 -- note: docs/HANDOVER_2026-08-06_EVENING.md:163

COMMITMENT: every FR -- Rektango 17:30 -- the weekly anchor, a hard stop -- owner: pip -- kind: cadence -- from: 2026-08-14 -- until: 2026-10-09 -- note: docs/game-design/WORKSHOP_3_PREP.md:32. Listed because it bounds Friday, not because Pip needs reminding of it.

### Further out

COMMITMENT: 2026-08-24 -- Reflective review: release / league cycle -- owner: pip -- kind: review -- note: pdoom1#808 and #811 both name this date.

COMMITMENT: 2026-08-31 -- Formal 4-way founder-hours review -- owner: pip -- kind: review -- covers: docs/design/MONTH_REVIEW_OPTIONS.md, docs/game-design/ADR_DQ_AUDIT_2026-08-03.md, docs/game-design/WS3A_DAYLOG_2026-07-27.md, docs/game-design/decisions/ADR-0011-effort-economy.md -- note: ADR-0011 effort-economy amendment (c) sets this as a formal review timer. pdoom1#984's workshop is scheduled to precede it.

COMMITMENT: 2026-08-31 -- Exploit-finder review-by -- owner: pdoom1-seat -- kind: review -- covers: docs/ARCHITECTURE.md

COMMITMENT: 2026-09-09 -- Manifund deadline -- owner: pip -- kind: deadline -- covers: docs/copy/MANIFUND_SUBMITTED_2026-07-29.md, docs/LAUNCH_SCHEDULE_MODELS.md, docs/design/WORKSHOP_TRI_REPO_PREP_2026-08-06.md -- note: cited by pdoom1#1015, pdoom1#1061 and pdoom1-website#194. The asset-provenance obligation hangs off this.

COMMITMENT: 2026-10-23 -- gpt-image-1 retires; the art pipeline's default model needs migrating -- owner: pdoom1-seat -- kind: expiry -- covers: docs/art/ASSET_PIPELINE.md, docs/art/PROMPT_RECIPES_2026-07-29.md, docs/art/VISUAL_ASSET_OPTIONS_2026-07-16.md, docs/design/ART_RUN_2026-08-07.md, docs/design/ASSET_PROVENANCE_SCOPE_2026-08-06.md -- note: a dormant pipeline that stops working on a date nobody is watching is the same shape as #1070.

COMMITMENT: 2027-07-27 -- ADR-0018 render-only office doctrine: standing review -- owner: pdoom1-seat -- kind: review -- covers: docs/game-design/decisions/ADR-0018-render-only-office-doctrine.md, docs/game-design/ADR_DQ_AUDIT_2026-08-03.md, docs/game-design/WS3A_DAYLOG_2026-07-27.md -- note: the ADR states office gameplay foreclosed by default must CLEAR this review rather than tack on. Eleven months out, which is exactly the horizon a person cannot hold.

---

## 3. What the generator does not cover

- **It cannot read Pip's calendar, phone alarms or paper diary.** Every gap this
  reports means "nothing in the repo will remind him", not "nothing anywhere
  will".
- **It does not run.** A file cannot ring. Until this `.ics` is subscribed to by
  something that notifies, the finding it was built to fix is unchanged. Section
  4 is therefore the load-bearing part of this document, not section 2.
- **It scrapes prose and will miss things.** That is why UNPARSED exists and why
  there is no silent ignore list: a scraper that reports success is the failure
  class this repo already paid for twice.
- **`ship:hotpatch-48h` produces no event.** See section 1's inclusion bar.

---

## 4. Getting it into an actual calendar

**Subscribe, do not import** -- see section 1 on retraction.

The repo is public, so the raw file has a stable URL that a calendar app can poll:

```
https://raw.githubusercontent.com/PipFoweraker/pdoom1/main/docs/calendar/pdoom1-commitments.ics
```

- **Google Calendar:** Other calendars -> `+` -> *From URL* -> paste -> Add.
  Polls on its own schedule (commonly 8-24 h), so a same-day change may not show
  until the next poll. That lag is the price of retraction working at all.
- **Apple Calendar:** File -> New Calendar Subscription -> paste -> set
  auto-refresh to Every day.
- **Outlook / Microsoft 365:** Add calendar -> Subscribe from web -> paste.
- **Thunderbird / anything CalDAV-adjacent:** New Calendar -> On the Network ->
  iCalendar (ICS) -> paste.

The local copy, for a one-shot import or to inspect before subscribing:

```
G:\Documents\Organising_Life\Code\pdoom1\docs\calendar\pdoom1-commitments.ics
```
