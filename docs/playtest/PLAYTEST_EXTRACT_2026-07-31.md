# Playtest extract -- 0.13.2 dev build, 2026-07-31 10:24 (14:08, solo, spoken)

- **Source:** `art_generated/audiodump/2026-07-31_10-24-00.transcript.md`, whisper-1,
  no diarization. Every claim below carries the timestamp it came from -- open the
  transcript at that mark to hear the original wording.
- **Status:** EXTRACTED BY CLAUDE 2026-07-31, **not yet ruled on by Pip.** The
  categories below are my reading of an unstructured spoken pass. Move items between
  BLOCKER / FAST-FOLLOW / BACKLOG freely -- that re-categorisation is the point of
  reading this.
- **Privacy:** this extract contains no personal data. The raw transcript lives in
  `art_generated/` (gitignored) and should stay there.

> ## THE VERDICT ALREADY GIVEN
>
> **[14:02]** *"So I say **don't ship**, but when we've solved these things I'm happy
> to ship."*
>
> That was said at ~10:38 today. [Gate 4: PROVEN BUILD] cannot honestly be spoken
> over it as it stands. The re-cut window is ~1500, and [Gate 5: SEED BLESSING] is
> 1645 -- so the list below is a **decision queue with a four-hour fuse**, not a
> backlog.

---

## 1. What the run PROVED works (do not re-test, do not re-open)

Worth stating first, because it retires the week's biggest fear.

- **The v0.11.0 segfault family did not reproduce.** The run went game-over ->
  leaderboard **twice** (**[11:14]**, **[12:33]**) -- the exact transition that
  killed v0.11.0 in a release build. Clean both times.
- **Score submission works end to end** -- submit -> local board -> global board ->
  score screen -> play again (**[12:33]**, **[13:03]**, **[13:10]**).
- **Board key is correct:** `weekly2026w31`, epoch `L3` (**[3:31]**, **[13:10]**).
  This is the string the backend was told about in website #151.
- **Bug-report key is `N`, not `F8`** -- checked deliberately (**[3:10]**-**[3:18]**).
- **Doom-linked audio works:** *"extra creepiness in the music... because I started
  at 65% doom. That's fantastic"* (**[7:32]**-**[7:47]**).
- **Attention/queue substrate holds:** 13 fundraising actions queued, *"they are
  stacking the tiles correctly"* (**[9:19]**).
- **Crisis mode + for-profit + hard research integrity launched without breaking**
  (**[7:02]**-**[7:23]**).

## 2. SHIP-BLOCKERS -- the things behind "don't ship"

### B1. You cannot tell which run on the leaderboard is yours

The dominant finding of the session; he returns to it three times.

- **[12:38]** *"you have to change the lab name in order for it to differentiate
  yourself from every other player on the planet, this is a **close to critical
  ladder bug**"*
- **[13:40]** *"it's **critical** that we put the player name and the lab name in
  there, it's critical that we let people update... on the first screen"*
- **[13:53]** *"the failure mode here is someone just like runs the game and then
  they can't tell who they are on the leaderboard and that sucks"*

Two halves, and they may be separable: **(a)** the board shows `player` but no lab
name (**[5:14]**; he believes a patch may already be queued -- *verify before
fixing*), and **(b)** name + lab name are not editable on the first screen you reach
from Launch Lab (**[6:17]**-**[6:44]**). Pre-generated lab names collide, so (a)
without (b) still leaves duplicates.

**Ruling needed:** is (a) alone enough to ship on, with (b) as Saturday hotpatch?

### B2. Test seeds may be visible in the public seed filter

- **[13:19]** *"there's a huge amount of test things showing up in the filter by
  seed, that might be a local problem for me, it might be a global thing, if it's a
  global thing **it's hideous and we need to fix it**"*

This is a **10-minute verification, not a fix** -- check the seed filter against the
live API from a clean profile. If global, it is league-facing on the day the board
opens. Cheapest item on this page with the worst tail.

### B3. Version badge text runs off the right edge

- **[0:37]** *"the dev guide build text goes off the right hand side of the screen
  now, bug"*
- **[2:14]** *"it says 0.13.2 doc slash recording guide level, and then it blanks off
  the screen"*

First thing seen, on every screenshot and every stream frame. May be dev-build-only
chrome -- **confirm whether it appears in the release artifact** before spending
re-cut budget on it.

### B4. No intro, and an empty feed on the first screen

- **[7:47]** *"I am not getting the... I didn't get the intro to the game"*
- **[7:54]** *"the feed's first line, I noticed that there is no feed. There's nothing
  in the feed on the first screen that I get to"*
- **[8:14]** watch screen reads *"initializing game, keyboard 1-9 for action, space,
  enter to commit, initializing game, and then Jan 7 2020 turn phase action
  selection"* -> **[8:29]** *"That's a placeholder."*

**Cross-reference:** this is the same family as LIVE BUG #1 in
`docs/UI_PLACEHOLDER_AUDIT_2026-07-30.md` -- `watch_screen.tscn:25` ships a scene
literal that no boot path ever clears, because the feed writer at
`main_ui.gd:1359` is `+=` only. The audit predicted a player would read scene
literals as real state; **this transcript is that prediction coming true in a live
run.** The audit's one-line fix (an unconditional `=` on the boot path) plausibly
closes part of B4.

The missing cold open is separate and is live design question #814 -- **do not
improvise it four hours before a board opens.**

## 3. FAST-FOLLOW -- his own words, not shipping blockers

- Plan-screen action buttons still need scrolling to see all of them -- *"that's
  still a fast follow"* (**[8:41]**)
- Upgrades still mispositioned bottom-left; *"pretty sure that's queued, so maybe
  we'll just check the queue"* (**[8:51]**)
- "Reserve attention" button is legible only on hunting for it -- *"very, very
  difficult to see"* (**[9:40]**)
- **Play Again is offered when there is no game to play again from** -- *"that logic
  seems weird"* (**[5:44]**)
- Back / Play Again buttons too small, text hard against the edges; *"could be like
  double or triple the size"* (**[5:55]**)
- Leaderboard **Duration column is wall-clock and therefore meaningless** -- 9m32s
  for a run; wants days-survived or similar (**[4:49]**, **[11:34]**)
- `vsbase` column blank because no baseline exists yet (**[4:35]**)
- Leaderboard readability: vertical column rules + alternating row shading, *"like in
  Excel"* (**[5:05]**)
- Copy: lowercase `(you are on build v0.13.2)` should be capital Y (**[3:53]**)
- Naming: *"we're calling it turns rather than days... this is not critical but this
  is a significant problem that we haven't solved"* (**[12:51]**)

## 4. COPY / CONTENT asks (cheap, high leverage, mostly text)

- **Patch-cadence notice, currently bottom-right, wants promoting** (**[2:20]**-**[2:44]**):
  move to **top-middle**, **4-5x larger**, plus one or two sentences covering *what
  the most recent patch was*, *when the next one lands*, *a warning that the ladder
  may break*, and *an explicit ask to file bug reports and suggestions.* This is the
  single highest-value text change on the list for a board-opening weekend -- it
  converts confused players into bug reporters.
- **Leaderboard explainer needs a schedule line** (**[4:18]**-**[4:30]**): a new seed
  is blessed Friday evening AEST; link out to the website if easy URLs allow.
- **Pop-ups must say they cost attention** (**[10:35]**-**[10:44]**): *"it needs to be
  explicit about it costing attention because it's not obvious right now from the
  text"*
- **Settings screen wastes its top third** -- "Laboratory settings" negative space,
  then a small scrolling window (**[2:52]**-**[3:00]**)

## 5. DESIGN, not this week

- **Attention trade-offs when maxed:** *"allow people to have trade-offs so they can
  kill something that's in their stack... that's like clearly where the next bit of
  attention in the game needs to arrive"* (**[10:51]**-**[11:06]**)
- **The phase-tip area wants rethinking entirely** -- currently *"tip higher safety
  researchers to reduce p(Doom)"* sitting under a glowing green phase banner;
  *"we might want to revisit that area of the UI just entirely"* (**[9:53]**-**[10:04]**)
- Player-facing feedback loop: *"I will prompt people who are looking at the game to
  say what they like and don't like and are confused by"* (**[10:04]**) -- this pairs
  with the patch-notice ask above.

---

## What I would decide first, if it were mine to decide

1. **B2 verification** (~10 min, no code). Cheapest, and it is the only item that
   could embarrass the board publicly today.
2. **B1(a)** -- check the queue first. He suspects lab-name-on-board is already
   patched; if so this collapses from a blocker to a merge.
3. **B4 partial** via the audit's one-liner. Small, understood, already diagnosed.
4. **B3** -- confirm dev-only, then ignore until Saturday if it is.
5. Everything in section 3 and 4 -> **Saturday hotpatch window**, per the playbook's
   own rule: after the freeze, gameplay-shaped change means **re-cut, not patch**.

The honest reading of **[14:02]** is that "don't ship" was scoped to *"these
things"* -- and most of "these things" are section 3, not section 2. Worth deciding
explicitly whether the verdict binds the whole list or only the blockers, because
those are very different Fridays.

## Still unextracted

Two more transcripts from this window have never been turned into anything:

- `2026-07-30_16-36-55` (5:13) -- *"I've built the 0.13.2... Going to launch lab"*
- `2026-07-30_09-19-38` (3:48)

If either contains a bug not listed above, it is currently invisible to the release
process.
