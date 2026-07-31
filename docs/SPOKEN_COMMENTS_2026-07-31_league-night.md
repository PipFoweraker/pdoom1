# Spoken comments -- league night readiness + gate ceremonies, 2026-07-31

Sources: captures `2026-07-31_141150__3a18e34b` (1:11, League Night Alert
Readiness sheet) and `142318__dd9ff5e2` (0:16, Gate 5/6 ceremony checklists from
a localhost:8080 review page). Transcribed on-device; audio never uploaded.

**Status:** EXTRACTED BY CLAUDE, not yet re-read by Pip.

## League Night Alert Readiness

Pip was unsure whether the sheet belongs to `pdoom1` or `pdoom1-website` --
filed here; move it if the sheet's owner is the website.

- **"What will actually reach you / what will not / notice before you go"** --
  structure approved.
- **Player bug reports** -- OK.
- **Para 2, "the website already has an intake workflow"** -- *"I have a question
  mark, let's check #1057."*
- **Para 3, players who bounce off at download, Gatekeeper, or the menus:**
  > *"plan to make the exits more comparable?"* -- and *"I also think trackable,
  > or find ways to see if we can silently capture those while still being
  > privacy respecting."*

  Two asks in one: make drop-off points comparable to each other, **and**
  instrument them without violating the privacy posture. Worth an explicit
  design note before anything is instrumented.
- **Section 5, "set up before 17:45.2 -- watch both repos":**
  > *"is that actually an action inside GitHub Mobile, and if so can you step by
  > step me through it?"* -- **owed to Pip as instructions, not as a claim.**
- **The three things worth being interrupted for** -- agreed, with one query:
  > *"board liveness goes red -- what is board, what is red?"*

  Terms need defining in the sheet itself. The other two (player reports a crash;
  nothing on board an hour after opening) are accepted as-is.
- *"Everything else I agree."*

## Gate 5 / Gate 6 ceremony checklists

> *"Gate 5 and 6 ceremony checklists look good, but this was printed several
> hours ago and I'd like to do a re-cut to see if anything's changed."*

**Action: regenerate the ceremony checklist from current state before the
ceremony runs.** The printed copy is stale by a working day's worth of merges,
and Gate 5 (SEED BLESSING) is the one that asserts board-key fork verified clean.
