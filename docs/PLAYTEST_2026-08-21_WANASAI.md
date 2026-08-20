# Playtest sheet -- 2026-08-21, Wanasai, first session

**Window:** ~0620-0700, she leaves ~0700. **Capture:** OBS.

**Build: the published v0.14.1 release binary.** NOT current `main`.
Godot is not installed on this machine (see "What went wrong" below), so
running from source was not available in the window. She is playing what a real
player downloads today, which is a defensible playtest target in its own right
-- but it is 81 commits behind `main` and does NOT include the doom-sink fix
(#1233) or the 28 new events (#1230).

Her score will post to **`(weekly-2026-w32, L4)`** -- the seed pinned inside
that build. `main` says `w33`. Neither is the board we are forking to today, so
her run cannot dirty the new board.

---

## LAUNCH -- the absolute path

```
D:\Local_Code\_builds\pdoom1-v0.14.1\PDoom.exe
```

Double-click it. **Windows SmartScreen will warn** ("Windows protected your
PC", unknown publisher) because the build is unsigned. Click **More info** ->
**Run anyway**. Do this yourself BEFORE she sits down so she does not spend her
first 60 seconds on a security dialog -- that is not the confusion we are trying
to measure.

Verified present at that path: `PDoom.exe` (PE32+ x86-64, 96.6 MB),
`PDoom.pck` (61.0 MB), `steam_api64.dll`, `libgodotsteam...dll`. All four must
stay in the same folder.

---

## The one thing this session buys that nothing else can

**She can only be a first-timer once.** Every other question in the backlog can
be answered by Pip, by a test, or by a later session. "Where does a person who
has never seen this game get stuck in the first ten turns" cannot. Issue #1210
is exactly this question and its current evidence base is one prior session.

So the scarce resource is her confusion, and the way to waste it is to explain
things. **Spend the whole session on the first ten turns if that is where she
is.** Do not push her forward to see more content.

---

## Observer rule (the hard one)

**Do not help.** Not a hint, not a "try clicking that", not a raised eyebrow.
When she is stuck, that is the measurement -- say nothing and let the clock run.
Note the wall-clock seconds she spends stuck; the duration is the data.

The only permitted interventions:
- An actual crash or softlock -> stop, note it, restart.
- She asks a direct question -> "what do you think it does?" then silence.
- She wants to stop -> stop.

If Pip cannot stay silent, Pip should not be in the room. Put the mic on her and
watch the recording afterwards.

---

## Setup, in order

1. **OBS**: capture the game window plus microphone. Ask her to think aloud --
   "say what you are looking at and what you expect to happen". **Confirm the
   mic is actually recording before turn 1**; a silent capture of this session
   is a total loss and is unrecoverable.
2. Click through SmartScreen yourself first (above).
3. **In-game `N` writes a bug report to disk and shows the path.** If she hits
   anything broken, press `N` rather than trying to remember it.
4. Note the OBS output path on this sheet before you start, not after.

---

## Timeline

| Time | What |
|---|---|
| 0620 | OBS rolling, mic confirmed, SmartScreen already cleared. Hand over the mouse. |
| 0620-0650 | She plays. Observer silent, taking timestamped notes. |
| 0650-0658 | Debrief (below). Recording still rolling. |
| 0658 | Stop capture. Thank her properly. |

---

## Watch-fors -- observations, NOT questions to ask her

These are open issues. Watch whether they bite; do not raise them. If she never
notices one, that is a finding too.

Caveat: several of these were filed against `main`, and she is on v0.14.1. A
finding here is still real (players are on v0.14.1); an ABSENCE proves nothing
about `main`, and vice versa.

| # | Issue | What to watch for |
|---|---|---|
| 1 | #1210 | The first ten turns. Where is the first pause longer than 15s? What was on screen? |
| 2 | #1223 | Action Queue vs Attention header contradict in one frame. Does she notice? Does she act on the wrong one? |
| 3 | #1224 | Hotkey badges lose to modulate; UI says "press 1-9" when there are 13 tiles. Does she ever use a hotkey unprompted? |
| 4 | #1225 | Hiring: five faces for six candidates, free offer retries, invisible ad campaign, empty counter-offers, onboarding bill only visible after commit. Does the bill surprise her? |
| 5 | #1226 | Firing exists on a screen the player never reaches. Does she try to fire anyone, and can she find it? |
| 6 | #1218 | Attention spent without the UI saying so. Does she run out and not understand why? |
| 7 | #1202 | Early-game legibility, five prior findings. Do any recur? |
| 8 | -- | Does she understand what the doom number means, unprompted? |
| 9 | -- | Does she ever say "ticks"? We use the word and have never defined it. |

**Timestamp every observation** so the recording is seekable. A note without a
timestamp costs an hour of scrubbing later.

---

## Debrief questions (after she stops playing, in this order)

Order matters -- open before leading, so her framing is not contaminated.

1. "Talk me through what you thought the game was about."
2. "What were you trying to do?" (her goal, not the game's)
3. "Was there a moment you felt lost? What was on screen?"
4. "Was there a moment something clicked?"
5. "Anything you expected to be able to do and could not find?"
6. "If you sat down again tomorrow, would you? Honestly -- no is a fine answer."

Do not ask "did you like it". It buys nothing and she will be polite.

---

## After she leaves

- OBS file path: `______________________________`
- File findings as issues the same morning, while the recording is fresh, and
  link each to its timestamp. A finding without a timestamp is an opinion.
- Tag every issue with `found-on: v0.14.1` -- otherwise a fix lands on `main`
  and nobody can tell whether it was already fixed there.
- Repeats from #1202 or #1210 are worth more than novel findings: a repeat means
  the earlier fix did not take.
- She is an art reviewer with 197 verdicts in this repo, so she has seen the
  assets but not the systems. Note where art-familiarity misled her -- that is a
  confound, and also a real player state for anyone who has seen a screenshot.

---

## What went wrong getting here (for the record)

At 0550 the class-cache guard reported every `class_name` MISSING in this
checkout. Repairing it needs Godot, and **Godot is not installed on this
machine** -- not at `C:/Program Files/Godot/` where `CLAUDE.md` says it is, and
nowhere on C: or D: within four directory levels. `godot/.godot/` has never
existed here. `make run` cannot work on this box.

`CLAUDE.md` still carries the old PC's paths throughout (`C:/Program
Files/Godot/...`, `C:/Users/Pip/AppData/...`, `G:/tmp/...`); this machine is
`D:\Local_Code`, user `gday`. `docs/MIGRATION_TO_NEW_PC.md` exists, so the
migration happened and the agent cheat-sheet was never updated to match.

**Consequence beyond this session: `tools/build_release.py` cannot run here
either** (it needs Godot plus export templates), so today's v0.14.2 build is
blocked until Godot 4.5.1 is installed. That is a prerequisite for
[Gate 4: PROVEN BUILD], not a side quest.
