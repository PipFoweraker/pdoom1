# Review sheet -- font-size SSOT (#1224 parts 3 + 4)

**Merged:** `71d2fa76` on 2026-08-19. **Recording:** full session.
**What you are reviewing:** body text went **16 -> 19px** game-wide, and **86
size overrides were deleted** across 15 scenes. Nothing about this was checked
by eye before it merged. The suite is green (1371 tests) but **no test measures
whether a button still fits its box**, which is exactly the failure to hunt.

Launch:

    make run

---

## The one thing to say out loud first

Before touching anything: **is the game more readable or less?** One sentence,
on tape, before the detail hunt biases it. The whole change exists to answer
that and nothing below matters if the answer is "less".

---

## What counts as a DEFECT (report these)

- **Text clipped or overflowing its box** -- a button label cut off, a word
  running past a panel edge, a row taller than its container.
- **A heading now SMALLER than the prose under it.** This is the specific
  inversion the change was supposed to remove; if any survives, it was missed.
- **Something that used to fit on one line and now wraps to two** in a place
  where that breaks the layout.
- **Text that overlaps other text.**

## What is NOT a defect (expected, already decided -- do not file)

- **Dense panels still tiny.** Sizes <=15px were deliberately left alone. The
  hiring panel still renders its decision data at 9px. That is the NEXT pass,
  not a regression from this one.
- **Big display text unchanged.** Sizes >=20px were left alone too.
- Anything about **hotkey badges, the "press 1-9" hint, or the dead `3` key** --
  those are parts 1 and 2 of #1224, still open and untouched here.

---

## The route, ordered by how much each screen changed

Highest risk first. The number is how many overrides were deleted from that
scene -- more deletions means more text moved.

| # | Screen | How to reach it | Removed | Look hardest at |
|---|---|---|---|---|
| 1 | **Settings** | main menu -> SETTINGS | **28** | The three-column board. Every button label. Does the ACCESS column still line up? |
| 2 | **Config confirmation** | change a setting, confirm | **11** | The confirm/cancel buttons and the body copy |
| 3 | **Leaderboard** | main menu -> LEADERBOARD | **10** | Column headers vs rows. Do 50 entries still fit, or does the table now scroll where it did not? |
| 4 | **Player guide** | main menu -> PLAYER GUIDE | 9 (+8) | **The part-4 fix.** See its own section below |
| 5 | **Pre-game setup** | NEW GAME | **8** | Seed field, difficulty and scenario pickers, the labels beside them |
| 6 | **Pause menu** | in game, `ESC` | 6 | Every entry; this is the one #1155 already called cramped |
| 7 | **Main game screen** | in game | 5 | The phase banner, top resource bar, action tiles |
| 8 | What's new modal | first launch after version bump | 3 | Body copy and the dismiss button |
| 9 | Welcome overlay | first launch | 3 | Same |
| 10 | Employee screen | in game -> staff | 3 | Row text |
| 11 | Credits | main menu -> CREDITS | 3 | Names should not wrap oddly |
| 12 | Staff perks panel | in game -> staff -> perks | 2 | |
| 13 | Plan screen | in game -> plan | 1 | |
| 14 | Keybind screen | Settings -> Keybindings | 1 | Key column alignment |
| 15 | Debug overlay | dev mode | 1 | |

Screens 1-7 are the ones worth slowing down on. 8-15 are a quick look each.

---

## Player guide -- the specific claim to falsify

Reported twice (#1141, then #1224) and never fixed. Four sections each had their
own internal scrollbar inside the outer one -- you said "triple", it was five.

**Scroll from the very top to the very bottom in one continuous motion.**

- It should be **one scroll**. No section should stop scrolling while the page
  keeps going, and no section should scroll while the page is still.
- No text should be cut off at the bottom of a section.
- If any section still has its own bar, the fix did not take. Say so on tape.

---

## The menu buttons -- the sneakiest risk

`menu_theme.tres` used to pin every menu button at 16px. That line is gone, so
**every button on all nine menu screens is now 19px inside a box someone sized
for 16px text.** If anything is going to overflow, it is a button label.

Worth a deliberate pass: main menu, settings, leaderboard, credits, keybinds,
pre-game, pause, config confirmation, player guide. Just read the buttons.

---

## Verdict, for the tape

Say each of these out loud at the end so the transcript carries them:

1. More readable, less readable, or no real difference?
2. Is 19px **right**, or does it want to be 20-21? (It is one number:
   `godot/theme/base_theme.tres`, `default_font_size`.)
3. Anything actually broken -- clipped, overlapping, wrapped badly?
4. Which screen should the NEXT pass take? (The measured worst is the hiring
   panel: 30 overrides, decision data at 9px, in a 580x640 box that never
   grows. You named it in #1041 and again in #1224.)

---

## After the recording

    python tools/ingest_recordings.py                 # pull today's OBS files in
    python tools/transcribe.py <file>                 # offline, timestamped
    python tools/playtest_report.py                   # evidenced bug list

Anything you rule during the session gets written down as one line, wherever it
belongs:

    RULING: <YYYY-MM-DD> -- <the ruling> -- flavour: ui-legibility

or `python tools/rule.py "<ruling>" --flavour ui-legibility`, which shows you
every prior ruling in that flavour first.
