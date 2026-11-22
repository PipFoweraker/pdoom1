# Claim audit -- pdoom1's own output, week of 2026-08-13

**Why this exists.** `docs/POSTMORTEM_2026-08-07_CAPTURE.md` Section 6, proposal
P3, with a falsifier and a date:

> P3 -- Every published measurement command ships a control line proving it can
> return the other answer. **Falsifier:** Re-run the claim audit on the week of
> **2026-08-13**. A WRONG rate at or above today's 9 per cent means the rule did
> not take and should be replaced with the generator requirement, not patched
> again.

Declared in the commitment calendar as a `falsifier` dated 2026-08-20, owner
`pdoom1-seat` (the declaration itself lives in the postmortem). It was **one day
overdue** when this ran (2026-08-21, ~10:15-11:00 AEST).

Baseline to beat: `docs/CLAIM_AUDIT_2026-08-06.md` found **6 WRONG of 68
headline claims = 8.8 per cent**.

---

## Method, and where it differs from the 2026-08-06 run

Same rule being tested:

> A claim in a title, a summary line, a table cell or a bolded sentence must be
> reducible to a command another party can run.

**Corpus.** The 58 commits merged to `origin/main` between 2026-08-13 and
2026-08-21. Commit subjects are the headline surface this repo actually
publishes -- they are titles, they are quoted in PR bodies and release notes,
and in this repo they are unusually claim-dense ("148 of 322 json files did not
parse", "7,944 assets carry a verdict").

**Selection.** Subjects carrying a checkable quantitative claim. This is a
NARROWER frame than 2026-08-06, which examined 68 claims across titles, bolded
sentences, table cells and section headings in prose documents.

**Sample size is the main limitation and is stated up front: n=7.** Against a
baseline of n=68. See "What this run cannot decide".

**Bases.** Every command run against `origin/main` in the working checkout at
`D:\Local_Code\pdoom1`, HEAD `01d40168`, with historical states recovered via
`git show <sha>:<path>`. No external repos involved.

---

## Counts

| Verdict | Rows |
|---|---|
| CONFIRMED -- command run, output matches | **5** |
| WRONG -- command run, output does not match | **2** |
| **Total headline claims examined** | **7** |

**WRONG rate: 2/7 = 28.6 per cent.** The P3 threshold is 9 per cent.

---

## CONFIRMED (5)

### K1. "148 of 322 json files did not parse" -- `2c6f923a`

```
git ls-tree -r -z --name-only 2c6f923a~1   # -z is load-bearing, see F1
  -> 322 files ending .json
  -> 148 fail json.loads()
```

**Exact on both numerator and denominator.**

### K2. "7,944 assets carry a verdict" -- `0ed871ce`

```
git show 0ed871ce:tools/art_review/review_state.json | count entries
  -> 7944 entries, 7944 with a non-empty verdict
```

**Exact.** Note the store is tracked, so the claim stayed checkable after the
fact. An untracked store would have made this UNCHECKABLE forever.

### K3. "28 new events" -- `56d46c40`

```
core_events.json  25 -> 35   (+10)
risk_events.json  30 -> 48   (+18)   # nested under pools.<pool>.<severity>
                              = 28
```

**Exact.**

### K4. "every risk pool/severity cell filled" -- `56d46c40`

```
6 pools x 4 severities = 24 cells; 0 empty
```

**Exact.**

### K5. "60 curated hireable people" -- `9af8b175`

```
len(json.load(godot/data/researchers/personas.json)["personas"]) -> 60
```

**Exact.**

---

## WRONG (2)

### W1. "regenerate the **four** indexes" -- `bb144c7d`

**Where:** commit subject, and restated in the body: *"all four generated
indexes derive from those."*

**Command:**

```
git show --stat --format='' bb144c7d
  -> docs/TOOLS.md
     docs/calendar/COMMITMENTS_INDEX.md
     docs/calendar/pdoom1-commitments.ics
     docs/rulings/RULINGS.md
     docs/rulings/rulings.json
```

**Verdict: WRONG under either reading.** Five FILES. Three index SYSTEMS
(tools; calendar, which emits two files; rulings, which emits two files).
Neither count is four. The repo has more than four generated indexes in total
(the pre-commit run lists DQ, ADR, dev-tools, action-taxonomy, credits,
commitment-calendar and rulings), so "the four" does not name a stable set
either.

**Severity: low.** Nobody is misled about the world; the tree state is correct.
It is in scope because the rule is about headline numerals, and this is one.

### W2. "redact **12** live contact addresses from bundled events" -- `5ccfa6e1`

**Where:** commit subject (#1212).

**Two independent commands, both disagreeing with 12:**

```
placeholder count "[email address redacted]"   75 -> 88   = 13 added
"@" character count in the same file           14 -> 1    = 13 removed
```

**Verdict: WRONG. The number is 13.** Both proxies agree, and they fail
differently, so they are not one mistake counted twice.

**The defensible reading, stated because it exists.** One removed string is
`{gilmer,muelly,goodfellow,mrtz,beenkim}@google.com` -- a brace-group holding
five addresses behind one `@`. Any counting rule that treats that as one item
gives 13; any rule that expands it gives 17. To reach 12 requires excluding
exactly one item on a ground the commit does not state. The word "live" may be
doing that work, but a reader cannot run it.

**Severity: low-moderate.** This is a privacy commit. The count is the evidence
that the sweep was complete, so being unable to reproduce it weakens the one
thing the commit is claiming.

---

## The finding that matters more than the rate

Sorting the seven by **where the number came from**:

| Origin of the number | CONFIRMED | WRONG |
|---|---|---|
| Output of a tool or a script | **5** | 0 |
| Counted by hand while writing prose | 0 | **2** |

Five for five when a command produced the number. Zero for two when a human or
an agent typed a small integer from memory while writing the commit message.

Both failures are small-integer miscounts (4 vs 3-or-5; 12 vs 13), not
fabrications and not misdescriptions of the world. That pattern points exactly
where P3 itself pointed:

> ...should be replaced with the generator requirement, not patched again.

**Recommendation.** The control-line rule DID take wherever a command already
existed. It has no purchase on a number typed into prose, because there is
nothing to attach a control line to. So:

> A headline integer must be the output of a command, or the sentence must be
> written without a number.

"Regenerate the generated indexes" and "redact the contact addresses found by
the scan" are both true, checkable, and cost nothing. Neither needs a numeral.

---

## What this run cannot decide

**The falsifier is crossed but not settled.** 2/7 = 28.6 per cent is above the
9 per cent threshold, but n=7. The 95 per cent interval on 2 of 7 runs roughly
4 to 71 per cent and straddles the threshold in both directions. **This run does
not establish that the rule failed**, and saying otherwise would be the exact
defect being audited.

What would settle it: extend the corpus from commit subjects to the week's
prose documents and PR bodies, reaching n comparable to 68. Estimated at two to
three hours. Until then, treat the origin-of-the-number table above as the
result and the percentage as indicative.

---

## F. Two false WRONGs this audit produced against ITSELF

Recorded because an audit that cannot audit itself is the thing it is auditing.
Both were about to be published as findings.

### F1. "148 of 322" was first scored WRONG at 159

`git ls-tree -r --name-only | .split()` splits on whitespace, so tracked
filenames CONTAINING spaces were shredded into fragments -- `Houses.json`,
`Knee55.json`, `(safe).json`, `maxima.json`, `sandbagging.json` and six more,
each counted as its own unparseable file. Exactly 11 spurious entries against an
11-unit discrepancy.

**What caught it:** the denominator matched the claim EXACTLY (322) while the
numerator did not. Identical denominators imply an identical file set, so the
gap had to be mine. Fixed with `-z` and NUL splitting; the recount is 148.

### F2. The redaction was first scored as "0 addresses removed"

A conventional email regex found zero addresses on both sides of the diff. The
addresses are OCR extractions from PDFs and are mangled -- `thilo.hagendorff@uni
-tuebingen.de` has a space inside the domain, `{gilmer,muelly,...}@google.com`
has braces and commas in the local part. Neither matches `[A-Za-z0-9._%+-]+@`.

**What caught it:** "0 before AND 0 after" is not a plausible state for a commit
whose diff visibly removes email addresses. A result of zero on both sides of a
change is a smell, not a measurement.

**The lesson, and it is P3's own rule turned inward:** a published measurement
command must ship a control line proving it can return the other answer. Neither
F1 nor F2 had one. `git ls-tree | split()` was never shown capable of returning
148, and the regex was never shown capable of finding a single address in that
file. Both would have shipped.

---

## Provenance

Run 2026-08-21 ~10:15-11:00 AEST by the pdoom1 seat (Claude Opus 5) at Pip's
direction, in `D:\Local_Code\pdoom1` at HEAD `01d40168`, branch
`release/v0.14.2-L5`. Every command above was executed, not composed. Where a
command's first result was wrong it is recorded in Section F rather than
silently corrected.

COMMITMENT: 2026-09-18 -- Extend this claim audit to prose documents and PR bodies to reach n comparable to 68, or retire the percentage and keep only the origin-of-the-number test -- owner: pdoom1-seat -- kind: falsifier -- note: the 2026-08-21 run was n=7 and could not decide P3 either way.

That declaration is one physical line on purpose. The first draft of this file
hard-wrapped it across four lines and the calendar generator reported it as
MALFORMED, because the scanner reads a declaration line-wise and the wrapped
remainder lost its trailing fields. Reported, not silently dropped -- which is
the behaviour the convention promises. Same lesson as the rest of this document:
the tool was right and the prose was wrong.
