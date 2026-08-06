# Handover -- Thursday 2026-08-06, evening

Written at high context so nothing is lost. This is the state of play, the open
threads, and what the next session needs to know that is not recoverable from git.

---

## 1. Where main is

`main` carries everything merged today. The fast gate is green (~1128 tests).
**Merged 2026-08-06:** action visibility (#1130), dev-gate split + music player
(#1129), identity prompt + lab-name generator (#1133), tools index (#1123),
dead-code scanner (#1124), leaderboard toggle honesty (#1127), percent-rounding
fix (main was RED in CI for a day before this).

**Open PRs:**
- **#1120** -- keyboard/navigation, four issues (#567 #575 #565 #602). PIP IS
  HOLDING THIS. He flagged "issues in the morning" on 08-05 and has not returned
  to it. The UI architecture doc assumes its seven navigation principles P1-P7,
  so it wants resolving before Phase 1 of the architecture work.
- Whatever the two live lanes below produce.

**Live agent lanes at handover:** the event retime (`feat/event-retime-and-
promotions`) and the copy-truth lane (`fix/copy-teaches-the-real-game`).

---

## 2. The three documents produced today, all printed, none acted on

- `docs/design/UI_ARCHITECTURE_2026-08-06.md` -- the taxonomy rule and 9 doors
- `docs/design/FRESH_EYES_TEARDOWN_2026-08-06.md` -- 11 ranked findings, 7 new
- `docs/design/JAM_SESSION_2026-08-05.md` + the print sheets

These are the substance of the day. **Everything below is downstream of them.**

---

## 3. The parked intro work Pip was trying to remember

**It is issue #1112: "Pip's rulings on intro + poster art, 2026-08-04 11:34 --
B1/B2 approved, dev-vs-alpha tool split, and a prior story beat."**

He ruled on it Tuesday and it was never built. B1 and B2 refer to the proposals in
`docs/design/INTRO_AND_POSTER_ART.md`:

- **B1 "Portal Stitch"** -- uses `godot/assets/shaders/time_portal.gdshader`, a
  procedural rotating vortex with 14 dials, 3 palettes, a tweened reveal, a live
  tuning harness and a deterministic capture tool. **It ships in the pack today and
  is referenced by ZERO player-facing code.** Costs 0 assets, 0 MB.
- **B2 "Held Frame"** -- one poster, ~0.4 MB.

Also parked and adjacent:
- **#1029** -- no way to replay the cold-open intro (reset `last_seen_intro_version`)
- **#1017** -- ship a FIRST-RUN.txt in the zip; macOS instructions currently reach
  nobody who downloaded
- `docs/design/ONBOARDING_STORY_DESIGN.md` exists in the tree

**The through-line:** the intro has been designed twice, ruled on once, and built
zero times. The cold open still ends on a string that calls itself "expository
filler (for now)".

---

## 4. Cold-open replacement lines -- Pip asked for "a few simple scripts"

Current, `cold_open_sequence.gd:56`:

> "Hello past me! I am expository filler (for now). You know nothing yet -- go and
> find out. Read, show up somewhere, or be loud online. Scouting. -- MHS"

Constraints the replacement must honour: it is a message from MHS to past-self, it
must point at scouting, and per ADR-0001 a reveal must OPEN A DECISION rather than
just inform. Register is dry gallows humour, not portentous.

Options, all keeping the function:

**A. The terse one.**
> "Hello past me. You know nothing yet, and that is the only advantage you have
> left. Go and find out -- read, show up, be loud. Scouting. -- MHS"

**B. The one that admits the shape of the game.**
> "Hello past me. I would tell you how this ends, but you would not believe me and
> it would not help. Find out what everyone else is building. Scouting. -- MHS"

**C. The one that sets the clock.**
> "Hello past me. It is 2017 and you have more time than you will ever have again.
> Spend some of it looking. Scouting. -- MHS"

**D. The driest.**
> "Hello past me. Nobody is coming. Start by finding out who else is working on
> this. Scouting. -- MHS"

Pip picks; the copy-truth lane can take whichever he names, or he writes his own.

---

## 5. The issue sweep he asked for -- what the teardown and architecture imply

**Issues these two documents SUPERSEDE or absorb (candidates to close or relabel):**
- **#798** (Buy Compute under an operations submenu) -- ABSORBED by the architecture
  doc, which argues nesting compute under housekeeping "repeats the fundraise-
  below-the-fold mistake one level deeper" and makes Compute its own door instead.
- **#1043** (Plan screen wastes its middle) -- partially absorbed; its layout half
  is Phase 1, its workshop questions remain open.
- **#1037 / #1073** (stale AP vocabulary) -- largely landed via #1116; the teardown
  found the Player Guide still teaches retired controls, which the copy lane is
  fixing. Worth re-checking then closing.

**Issues the teardown CONFIRMS are still live:** #1088 (rivals never introduced),
#1031 (placeholders, incl. the retired "Week 1 | Day 1/5" time model -- note this
is now doubly wrong post-#1125), #1035, #1086, #1064, #1063, #1062.

**Issues the teardown reports as FIXED (verify then close):** five 07-20 findings
are genuinely dead -- empty-queue hard-error, dark death-attribution, stale AP
tooltip, month-review auto-jump, dead-end leaderboard.

**New, unfiled findings from the teardown that need issues:**
1. Player Guide teaches a false win condition and dead controls (copy lane owns it)
2. Three surfaces disagree about whether you can win (copy lane owns it)
3. "Plan (Enter)" is a second commit button named after the mode it exits, and
   silently reserves all remaining Attention
4. Cold open self-identifies as unfinished (copy lane owns it)
5. **No help exists inside a run after turn 3** -- hint and pulse self-retire, the
   overlay and cold open are show-once, the pause menu has no guide entry
6. Unconfirmed one-click resign that then mislabels the death as "The AI Destroyed
   Humanity"
7. Hidden-feed rejections

---

## 6. Open bugs that are not cosmetic

- **#1134 -- F3 permalock. CONFIRMED REACHABLE BY ANY PLAYER.** The overlay is
  instanced unconditionally in `main.tscn:415`, `_ready` binds the keybind with no
  build check, and `_trigger_event` appends to `state.pending_events` with NO PHASE
  GUARD. Inject in a phase that never drains the queue and the run is dead. Alpha
  Tools protects the BOARD, not the RUN -- a distinct risk that #1129's reasoning
  did not cover and did not need to.
- **`take_loan` is defined TWICE** -- `fundraising.json` and `financing.json`.
  Silent last-loader-wins. Found by counting during the architecture pass. The
  Phase 0 taxonomy checker goes red on it immediately, which is why it is the
  recommended first build.
- **#1085** -- minimising the window does not minimise. Not diagnosed.

---

## 7. Rulings made today, so they are not re-litigated

- **Music player is NOT an Alpha Tool.** Cosmetic-only, cannot affect scores. Pip:
  "if people want to listen to their favourite tracks, they can do so and if they
  miss out on doom indicators etc, so be it, that's their choice." **Owed:** a
  player-facing note that the music is presently loosely tied to the game and will
  become more so -- destination is the website's static pages.
- **Research safety/capability needs a workshop, not a lane.** Pip: "I am mostly
  getting to develop the research safety / capabilities things in a bit more detail
  because this element of the game is a little unsubtle for now." He agrees with the
  architecture doc's #1090 inference -- the Research door opens an ALLOCATION PANEL,
  not a verb list. Layout can proceed on 8 doors while Research waits.
- **Lab-name content pass deferred** to a future epoch as #1135, incl. backfilled
  bacronyms.
- **Turn = one month** (#1125, ruled 08-05). This invalidates the event pack's
  26-or-52 premise, which is what the retime lane is fixing.
- **Thursday dev, Friday push.** Friday is an ordinary patch day; epoch-breaking
  changes only if player experience demands it.

---

## 8. Still unruled, and one has a clock

- **The league seed still reads `weekly-2026-w31` and the ISO week is now W32.**
  Under a weekly reading the roll is overdue; under monthly the NAME is misleading.
  Unresolved since Monday.
- **ADR-0010's rung pick** -- the code implements the alternative the ADR rejected.
  The ADR/DQ audit called this the single most-unblocking decision available.
- **Which ADR-0002 is true** (#809) -- two colliding series give opposite answers on
  whether the game has a victory condition. The copy lane was told explicitly NOT
  to resolve this, only to make surfaces match the design-series ADR.
- **Art promotion is at 200.4 MB**, from the 58 MB Pip agreed to. It has grown three
  times, each time because a fix revealed cost a bug was hiding. Worth re-ruling
  rather than assuming the old answer holds.

---

## 9. Process notes worth keeping

- **`git checkout -- godot/` has now discarded an agent's tracked edits TWICE.**
  Both recovered by reapplying from context and re-running the gate. Worth a
  `CLAUDE.md` line.
- **A local gate pass is not a CI pass.** `main` sat red in `Godot Tests` for a day
  while I reported green from local runs, because I checked the two neighbouring
  jobs. Coordination #20 states the general rule: "a seat may cache state, but may
  not assert from cache about the present."
- **Guards must be proven to fail before they are trusted.** Four lanes did this
  today; two of them found real bugs while doing it.
- **The single most valuable thing this week was an external player.** Two friends
  found in one hour what every internal playtest missed, because everyone internal
  has a working network, a populated board, and knows where fundraising is.
