# Month Review Options -- proposals from the 2026-08-01 recorded playtest

Decision card for Pip. Source: recorded playtest 2026-08-01, timestamps [3:18]-[5:03].
Ten proposals for the month review screen (Part A), five for the "Begin planning" button
(Part B), then a cheapest-three / highest-impact-three split. Design document only --
no code was changed.

## What the screen actually is (read this first, it reframes everything)

The "month review screen" is not a screen. It is a generic event popup:
`game_manager.gd:_finish_month_playback()` (lines 763-781) builds a plain event
Dictionary (one format string, `type: "popup"`, one option) and emits it through
`event_dialog.gd` -- the SAME presenter that shows crisis windows. So the player gets:

- a full-screen click blocker at 60% black (`event_dialog.gd:104-111`),
- a 600x450 forest-green panel, hardcoded colors predating the theme lane (#743),
- the review text as one Label,
- one dark-gray 500x45 choice button reading `[Q] Begin planning August 2017 (Free)`.

Three load-bearing code facts found while verifying his complaints:

**Fact 1 -- the data he wants is destroyed one call before the review renders.**
`MonthController.advance_tick()` calls `_open_plan_month()` -> `MonthPlan.begin_month()`
(month_plan.gd:121-143), which RESETS `attention_spent`, `attention_reserved`,
`reserve_used`, `hours_spent`, and `kind_spent` -- and only THEN does
`_finish_month_playback()` build the review. The review's "Attention: 20" is
`month_plan.available()` on the already-reset plan, i.e. the fresh grant. His [3:24]
"I don't see what my unspent reserve here WAS" is not a layout gap; the number no
longer exists at render time. Any planned-vs-actual proposal requires a pre-reset
snapshot (cheap: capture `month_plan.to_dict()` before `begin_month()`).

**Fact 2 -- the trade-off story he asked for at [3:35] is already recorded, just never
shown.** `WindowResolver.resolve()` returns `payment_source`
(reserve/cannibalize/defer/ignore) and `cancelled_wip` (the named strategic actions
sacrificed), and records each response into the replay artifact
(`VerificationTracker.record_window_response`, window_resolver.gd:135-138). "You made
this many trade-offs, this many sacrifices" is an aggregation of data the engine
already emits -- nothing new needs simulating.

**Fact 3 -- the "(Free)" suffix.** `EventDialog.format_cost_summary({})` returns
`" (Free)"` for a costless option (event_dialog.gd:65-83, a deliberate 2026-07-24
cost-display fix FOR EVENT CHOICES). Applied to a navigation button it produces
"Begin planning August 2017 (Free)" -- a door with a price tag saying the door costs
nothing.

### Is the review describing a retired mechanic? (his [4:18] "pre-W3" remark)

Split verdict, checked against ADR-0011 amendments (a)/(d) and `game_state.gd:76`:

- The review's own copy ("fresh decisions this month... unspent reserve evaporated --
  no banking") describes the CURRENT Attention model: monthly grant (ADR-0011
  amendment (d)), crisp evaporation (ADR-0009 S4). Not retired.
- BUT it narrates a mechanic the player has never been shown: the v1 reserve is
  IMPLICIT -- `game_manager.end_month()` (lines 701-709) silently sets reserve =
  everything unspent after execution. The player never set a reserve, so "your unspent
  reserve evaporated" reads as bookkeeping about an invisible object. That is the real
  source of the [3:42] "whatever, this is just kind of, eh".
- AND it is blind to everything W3 added: typed founder hours (planning/operating),
  the 4-way kind ledger (doors/approvals/audits/reserve, `kind_spent`), the window
  demand budget, cannibalized WIP. The review predates the economy it summarizes.
- Meanwhile the genuinely retired mechanic DOES survive on the same screen-stack:
  the top-bar tooltip `main.tscn:176` still says "Action Points. Limits actions per
  turn. Base 3 + 0.5 per staff." -- the AP pool deleted by T2 (issue #1073 family).
  The review popup sits on top of a HUD that lies about the currency the review is
  reporting.

### The rivals situation (his [3:58]-[4:10], the hardest call-out)

Verified in `rivals.gd:155-174`: three rival labs are seeded per run, two visible
(KNOWN) from turn 1, one hidden (RUMORED, discovery-gated on reputation). Visible
rivals DO emit deadpan one-line headlines into the WATCH feed on the "rivals" channel
(`turn_manager.gd:636-661`), and discovery emits an `[INTEL]` line. So strictly the
review is not the first appearance -- but the feed lines are gray one-liners scrolling
in a terminal feed with a "Hide rival intel" toggle, no framing, no introduction beat,
no persistent surface. Nothing ever tells the player THAT rivals exist as a concept,
WHY they matter (their capability feeds the overhang -> doom, post-ADR-0015), or WHERE
to look. The month review is the first place rivals appear FRAMED, which to a player is
the first appearance. He is right that this is not a layout problem, and right that the
fix mostly does not live on this screen (proposals A7/A8).

---

## Part A -- ten proposals for the month review

### A1. Cut the state, keep the change (delete the Funds line)

- **Answers:** [3:45] "funds is good, but I CAN SEE THAT UP HERE, so this is NOT
  FRESH INFORMATION"
- **Change:** delete `Funds: ... | Doom: ... | Staff: ...` from the review string, or
  keep a stat only when it CHANGED band/sign this month. Funds are in the top bar;
  doom is in the doom meter; staff is in the roster instrument.

```
BEFORE                                    AFTER
Attention: 20 fresh decisions...          August 2017 begins.
Funds: $84,200 | Doom: 31.2% | Staff: 3   (state lines gone -- the HUD owns state;
Rivals this month: ...                     the review owns what HAPPENED)
```

- **Trade-off:** the review gets thinner before A2/A3 give it new content; for one
  build the screen may feel empty. Ship with A2 if possible.
- **Effort:** 0.5h (one format string in `_finish_month_playback`).

### A2. The plan-vs-reality line (pre-reset snapshot)

- **Answers:** [3:24] "I don't see what my unspent reserve here WAS" and [3:30] "at
  the start of the month you planned to spend like 17 out of 20 attention"
- **Change:** capture `month_plan.to_dict()` in `_open_plan_month()` BEFORE
  `begin_month()` wipes it (Fact 1); render last month as planned vs actual:

```
  JULY IN REVIEW
  You committed 17 of 20 Attention to the plan.
  3 were held back -- 2 went to firefighting, 1 evaporated unused.
```

- **Trade-off:** small new state on GameManager (a `last_month_report` Dictionary);
  save/load should carry it or degrade gracefully (empty on load = skip the block).
  Display-only, so determinism/replay untouched.
- **Effort:** 3-4h including a unit test on the snapshot ordering.

### A3. The trade-off ledger ("what you gave up")

- **Answers:** [3:35] "things came up requiring this much attention, you made this
  many trade-offs, you made this many sacrifices"
- **Change:** accumulate window resolutions per month (the data already exists per
  Fact 2 -- `payment_source` + `cancelled_wip` per resolution) into a month log, then:

```
  CRISES: 3 windows opened.
    1 handled from reserve (painless -- that is what the reserve was for)
    1 handled by cannibalizing -- SACRIFICED: "Hire senior researcher"
    1 deferred -- a Liability Ledger entry now compounds against you
```

  Naming the sacrificed action by id/title is the emotional payload -- "you gave up
  the hire" lands where "2 trade-offs" does not.
- **Trade-off:** requires a per-month accumulator (GameManager or MonthController
  member, reset in `_open_plan_month`); the review grows taller, which pushes toward
  A5's scrollable panel. Also feeds the ADR-0009 consequence note that the review is
  "the natural home for world-state progression display".
- **Effort:** 4-6h.

### A4. Deltas, not levels

- **Answers:** [3:45] (redundant state) and the general diagnosis "shows state,
  not CHANGE"
- **Change:** every retained stat renders as month-start -> month-end movement using
  the existing EE-7 delta-chip convention (`delta_good`/`delta_bad`,
  UI_STYLE_GUIDE.md section 2): `Funds $102k -> $84k (-$18k: payroll, rent)`.
  Doom renders as BAND movement ("ELEVATED, unchanged" / "crossed into HIGH"), not a
  per-cause number -- ADR-0015 forbids printed doom deltas per SOURCE; a start/end
  level comparison is world-state display and legal, but per-cause attribution stays
  in the paid doom-breakdown instrument (ADR-0001 spending-buys-sight).
- **Trade-off:** needs month-start snapshots of money/doom/staff (trivial to capture
  in `_open_plan_month`); the rent/payroll attribution on the funds delta needs the
  ledger lines, or ship v1 with just the raw delta.
- **Effort:** 3h raw deltas; +2-3h for the "why" annotations.

### A5. Un-block the screen: review as a dockable panel, not a modal

- **Answers:** [3:49] "it's actually just kind of POPPING UP AND BLOCKING THE SCREEN"
- **Change:** stop routing the review through `event_dialog`. Two sub-options:
  - **A5a (panel):** reuse the "WHILE YOU WERE AWAY" idiom (`main_ui.gd:755+`) --
    one dismissible, scrollable, non-auto-advancing panel. Already the house answer
    to the #877 modal-stacking failure and the FRESH_EYES item-9 complaint about
    auto-jumping month-review modals; the review is the last holdout.
  - **A5b (docked, structural):** the review renders INTO the plan screen as a
    "LAST MONTH" card in a side column, so the player reads it WHILE planning --
    the review informs the exact decisions it should inform, and needs no dismissal.

```
  A5b sketch (plan screen):
  +---------------------------+--------------------------------+
  | LAST MONTH (July)         |  PLAN AUGUST 2017              |
  |  17/20 committed          |  Attention: 20                 |
  |  1 sacrifice: sr. hire    |  [ action queue ............ ] |
  |  Rivals: see INTEL        |  [ COMMIT PLAN (Space) ]       |
  +---------------------------+--------------------------------+
```

- **Trade-off:** A5b is the real fix but touches plan-screen layout (screen_mode /
  plan_screen lanes) and removes the "beat" between months -- some players like a
  curtain between acts. A5a keeps the beat, kills the blocking. Killing the modal
  also kills the current button entirely (see B5).
- **Effort:** A5a 4-6h; A5b 8-12h.

### A6. The month as a headline (narrative beat)

- **Answers:** [3:42] "whatever, this is just kind of, eh" -- the review has no
  voice; also ADR-0009's own consequence note: "progression feel is weak".
- **Change:** lead the review with ONE generated sentence naming the month's biggest
  event -- picked by simple precedence (doom band crossed > sacrifice made > rival
  reveal > biggest fund swing > quiet month), deadpan register per house style:

```
  JULY 2017: the month you gave up the senior hire to keep the lights on.
  ---
  (stat block below, per A2-A4)
```

- **Trade-off:** a template-picker, not AI text -- but even 6-8 templates need
  writing in the game's register, and a wrong-feeling headline is worse than none.
  Falls back to plain "August begins." when nothing clears the bar.
- **Effort:** 6-8h (mostly the precedence rules and copy).

### A7. Introduce rivals BEFORE reporting them (the fix that is not on this screen)

- **Answers:** [3:58] "I've NEVER SEEN THESE RIVALS BEFORE" / [4:02] "HOW DO I KNOW
  THAT I HAVE RIVALS?" / [4:10] "How has the game INTRODUCED THIS CONCEPT?"
- **Change:** a one-time introduction beat, fired the first time a rival is visible
  (for the two turn-1 KNOWN labs that means early in month 1, well before any review):
  a single framed INTEL card -- who they are, what they want, why you care ("their
  capability feeds the overhang; you cannot stop them, only outlast them"), where to
  watch them from now on. Candidate homes, in order of preference: (1) a first-month
  feed event promoted to a window-tier one-off; (2) a cold-open / pregame line ("you
  are not the only lab that got funded this year"); (3) the onboarding hint system
  (issue #720 surfaces, `show_hints`). The month review then only ever RECAPS a
  concept the game already taught.
- **Trade-off:** consumes one of the early window-demand-budget slots (2-3 early,
  month_controller.gd:51-56) if done as a window -- or bypass the budget like the
  hiring prompts do (player-owned, not external demand). Discovery of the hidden
  third lab already emits an [INTEL] feed line, so only the CONCEPT introduction is
  missing, not the reveal machinery.
- **Effort:** 4-8h depending on home; the copy is the hard part.

### A8. A persistent rivals surface (so the review can point instead of dump)

- **Answers:** [3:58]-[4:10] again -- the deeper half: rivals have NO home. The
  review is carrying a whole subsystem's UI on three text lines.
- **Change:** an INTEL card in the shared instrument panel (visible in both PLAN and
  WATCH modes, like doom/roster): visible rivals, focus, qualitative drift tag --
  the exact fields `_build_rivals_review_section()` already formats
  (game_manager.gd:784-802), rendered persistently instead of once a month. The
  review's rivals block shrinks to one line: "Rivals: CapabiliCorp accelerating --
  see INTEL." Qualitative drift labels only -- no capability numbers -- consistent
  with ADR-0001 (sight is bought) and ADR-0015 (no printed doom math).
- **Trade-off:** instrument-panel real estate is contested; `_rival_cap_snapshot`
  (the per-review drift baseline) needs an owner that updates monthly, not per-frame.
  A8 without A7 still fails his question -- a panel does not introduce a concept.
  Pair them.
- **Effort:** 6-10h.

### A9. Report the W3 economy the player actually lives in (typed-hours readout)

- **Answers:** [4:18] "This summary was probably done pre-W3, and so this needs a
  rework" -- the review is blind to typed hours, kinds, and the demand budget.
- **Change:** replace the "fresh decisions / no banking" bookkeeping-speak with a
  where-your-month-went readout from `kind_spent` + `hours_spent` (already tracked,
  month_plan.gd:105-109):

```
  WHERE JULY WENT (17 of 20 hours)
    approvals  #######      7   (queued strategy, hires)
    doors      #####        5   (stakeholder face-time)
    audits     ##           2   (ground-truthing reports)
    reserve    ###          3   (firefighting: 2 used, 1 evaporated)
```

  Move the "no banking" TEACHING where it belongs: a plan-screen tooltip on the
  Attention counter, shown while the player can still act on it.
- **Trade-off:** depends on A2's pre-reset snapshot (same wipe destroys kind_spent).
  The 4-way kind layer has a 2026-08-31 review date (ADR-0011 amendment (c)) and may
  collapse to 2-way -- render from a families-first template so a collapse only
  deletes rows. ASCII bars fit the terminal register for free.
- **Effort:** 3-5h on top of A2.

### A10. Reviews are re-readable (kill the read-now-or-lose-it pressure)

- **Answers:** [3:49] -- half of why blocking feels bad is that dismissing the modal
  DESTROYS the information; the popup is the only copy.
- **Change:** every month review also lands in the WATCH feed as a compact block
  (the feed is already the persistent record -- `feed_log`, message_log), so closing
  the review costs nothing and a player can scroll back to compare months. Cheap v1
  of a review history; a later "R = review archive" key can grow from it.
- **Trade-off:** feed noise -- one multi-line block per month is acceptable at
  ~114-270 months per run only if it collapses to a single expandable line under the
  existing feed-filter pattern. Without A5, this is a palliative, not the fix.
- **Effort:** 2h.

---

## Part B -- the "Begin planning August 2017" button

### Diagnosis: WHY the button sucks (before proposing)

The button is a generic event-choice button wearing a crisis costume, because the
review is a generic event. Five concrete faults, all verified in code:

1. **It renders as `[Q] Begin planning August 2017 (Free)`.** The `(Free)` suffix is
   `format_cost_summary({})` (Fact 3) -- cost chrome designed for crisis options,
   nonsensical on a door. The `[Q]` is `dialog_key_labels[0]` (event_dialog.gd:203)
   -- an arbitrary event-menu letter, not a considered binding.
2. **It is a one-option menu.** The presenter exists to offer CHOICES with costs,
   affordability graying, and tooltips; with one free option all that machinery
   communicates "this is a decision" when there is no decision. Navigation styled as
   deliberation.
3. **Wrong visual weight.** Dark gray 500x45, #333-family (event_dialog.gd:220-231),
   identical to any event option -- while the loop's OTHER primary action, END TURN
   (Space), is teal, 16px, and full-width in the bottom bar. The two doors of the
   month loop do not look like siblings.
4. **The obvious keys are dead.** MainUI._input (lines 551-558) deliberately blocks
   SPACE and ENTER while any dialog is active (to protect against accidental
   end-turn -- a GOOD rule). But no exception exists for a single-free-option
   navigation dialog, so the two keys every player tries first do nothing, and the
   working key (Q) is only discoverable by reading the button text. Pip found Q by
   accident at [4:55].
5. **The label is calendar-speak, not pull.** "Begin planning August 2017" names the
   destination but carries no reason to go -- the fresh grant (the one genuinely new
   number the review has) is not on the door.

His [4:55]-[5:03] ruling fits fault 4 exactly: Space yes, Enter no ("if enter is
going to be the commit turn thing, we don't want people doing that accidentally").
Enter = commit plan is already the live binding (main_ui.gd:594-597), so keeping
Enter dead in dialogs is correct and should stay.

### B1. Space advances the review (Enter stays dead)

Tag the review event (it already has a stable id, `MONTH_REVIEW_EVENT_ID`) so the
dialog-active branch of `MainUI._input` maps KEY_SPACE to button 0 ONLY for a
single-free-option review dialog. Enter remains blocked per Pip's own ruling and the
existing accidental-commit protection. Space is also semantically consistent:
outside dialogs Space already means "advance the loop". Effort: 1-2h incl. test.

### B2. Strip the crisis chrome from navigation buttons

Suppress ` (Free)` and the `[Q]` letter-menu prefix when a popup has exactly one
costless option; hint the real key instead, house style: `Begin planning August 2017
[SPACE]` (pairs with B1; `[ESC] close`-style chrome per UI_STYLE_GUIDE). Effort: 1h.

### B3. Primary-action styling

Style the single forward option as the sibling of END TURN: action_teal, larger
font, full-width at the panel base -- forward-motion looks different from
deliberation everywhere in the game. Also removes the affordability-gray ambiguity
(a dark-gray button reads half-disabled). Effort: 1-2h, theme-manager colors, no
layout surgery.

### B4. Put the pull on the door

Label carries the one fresh number the review owns: `Plan August -- 20 Attention
waiting [SPACE]`. The button becomes the bridge from "what happened" to "what will
you do", which is the review's actual job. Effort: 1h (string already has
`attention_now` in scope).

### B5. Delete the button (structural, rides A5b)

If the review docks into the plan screen (A5b), there is nothing to dismiss and the
existing bottom bar IS the forward door. The button's five faults all evaporate
because the button stops existing. Effort: folded into A5b; zero standalone.

---

## Cheapest three / highest-impact three

**Cheapest three (same afternoon, low risk):**
1. **A1** -- delete the redundant state lines (0.5h)
2. **B2** -- strip `(Free)` + `[Q]` chrome, hint the real key (1h)
3. **B1** -- Space advances the review, Enter stays dead (1-2h)

**Highest-impact three (each answers a diagnosis at the root):**
1. **A2 + A3** -- pre-reset snapshot + trade-off ledger: the review finally tells
   the planned-17-of-20, here-is-what-you-gave-up story. Fixes "state, not CHANGE"
   at the data layer every other proposal renders from. (7-10h combined)
2. **A5** -- review as panel (a) or docked into the plan screen (b): fixes
   "blocks rather than informs" structurally; b also deletes the button (B5).
   (4-12h by sub-option)
3. **A7 + A8** -- introduce rivals before reporting them + give them a home: the
   only pair that answers "how has the game INTRODUCED THIS CONCEPT to me?", and
   the fix Pip correctly suspected does not live on this screen. (10-18h combined)

Sequencing note: A2's snapshot is the substrate for A3, A4, and A9 -- if only one
structural thing lands this cycle, land the snapshot. And whatever else is decided,
fix the `main.tscn:176` AP tooltip alongside (issue #1073 family): the review popup
currently opens on top of a HUD describing a currency deleted in T2.
