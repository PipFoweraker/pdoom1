# UI + features stack (Pip playtest 2026-07-17)

> Living backlog from Pip's #664 alpha playtest. Loved the patch overall ("mechanically it feels
> amazing"; "sense of time progressing is fantastic"). This captures every note, the design
> heuristics behind them, and the insight Pip wanted recorded. Priority: P0 ship-relevant / P1 soon
> / P2 polish. Items marked IN-FLIGHT are already being built.

## Design heuristics / principles (Pip's -- treat as rules-of-thumb)
- **No early loss:** a new player should NOT normally be able to lose within the first ~6 turns.
- **Easy information transition once earned (pain/payoff):** the player can fight for or "buy"
  information; once earned it should flow easily across sub-menus (offer page etc.) with static
  bits staying put. Don't administratively hurt the player with clicks/attention the game can't
  also make easier -- every friction should have a payoff the game helps them realize.
- **Rage-quit friction:** slow down rage-quitting -- quit-to-menu by default, offer reload, make
  "wait" moments (loading screens) fun rather than punishing.
- **Time model:** a TURN is a planning period (count it); DAYS are the baseline tick; the game
  starts at the start of a period on a date. Show the turn count AND the date, cleanly.
- **Channel discipline:** don't flood the event feed, especially at low situational awareness --
  down-tune volume or give obvious filtering.

## Insight to note (Pip credited this, well-received)
- The **hiring mini-tab flavour + grouped status fields** (grouping the candidate's fields by
  category) was a good call and reads well. Keep this grouping pattern for other info-dense panels.

## IN-FLIGHT (building now, this session)
- **Promise cost fix (B):** appetite-promises cost future domain obligations (paper slot / compute
  / mission constraint), not raw reputation -- kills the turn-14 rep-collapse instant-death; +a
  test that promises can't cause a loss in <=6 turns; +cost shown before commit. (fix/promise-currency)
- **Manual PLAN<->WATCH toggle** (switch views at will). (feat/ui-quick-wins)
- **Turn/date display tidy** (Turn N + human date, clean-slated). (feat/ui-quick-wins)
- **In-flight hiring steps in the action queue** with progress (interview 2/3 ticks, etc.). (feat/ui-quick-wins)

## P0 -- ship-relevant polish (do around the alpha)
- **Quit -> Main Menu by default** (not quit-to-desktop) to slow rage-quits.
- **Defeat title/cause mismatch:** the screen showed "The AI Destroyed Humanity" while the cause
  was reputation collapse. Title the defeat by its ACTUAL death-attribution (rep collapse ->
  "lost all credibility"). `death_attribution.gd`.
- **Event-feed flooding:** the feed is drowning in `technical_research_breakthrough` / arxiv FEED
  lines. Either down-tune visible-event volume (scale to situational awareness) OR add obvious
  filtering -- MMORPG-style channels (global / local / org / party-equivalent) the player toggles.
  Start with the cheapest: a verbosity toggle + collapse the arxiv-flavour spam.
  CONFIRMED SEVERITY (turn-229 dump): the ENTIRE `hist_arxiv` deck fires -- 200+ entries in
  `event_cooldowns` -- so the feed is flooded by design, not a fluke. The flavour-arxiv stream
  needs its own channel/severity so it never crowds out real, actionable events.

## Playtest data (2026-07-17, seed weekly-2026-w0)
- Two rep-collapse deaths: turn 14 (bill -54) and turn 229 (one `mission_charter` promise, bill
  -80) -- both from the promise-as-reputation-debt bug (promise principal 2183 vs start rep 50).
  Fixed by the promise-currency (B) lane.
- Baseline (do-nothing) survives 588 turns / score 28413; the played runs died at 14 and 229 --
  inaction still outlives action, so promises + rep-collapse are the dominant early-loss vector.
- Burnout is climbing correctly (Gray/Ellis at 81 after ~162 turns) -- the slow-burn works.
- Defeat title said "The AI Destroyed Humanity" at doom 50 while the actual cause was rep-collapse
  -> the title/cause mismatch above.

## P1 -- soon (onboarding legibility + info flow + consequences)
- **Onboarding-pending highlight on the main screen:** make pending onboarding read louder.
  Integrate the office visuals -- e.g. a hollow, glowing green DASHED outline of the absent item
  (laptop/desk), transparency for easy parsing. Fun + legible.
- **Draw each step's result to easy-dismiss attention** (a light toast/blip per hiring-step
  resolution; dismissible, not modal).
- **Warn before penalty:** surface a heads-up right around when the game is about to start
  penalising the player for inaction-to-date (the "you should probably act now" nudge).
- **Offer page = earned-info transition:** scouted/revealed candidate info shows easily on the
  offer page; as you move through sub-menus, earned info persists/transmutes, static bits stay.
  (Direct application of the pain/payoff principle.)
- **Reload from an earlier era** on defeat (once autosave lands) -- "make better decisions."
- **Dev tools / debug reinstatement + upgrade:** better dev/debug tooling may have been lost /
  re-hotkeyed / combined during the UI work -- audit, restore, and upgrade. Add a processing-time
  / perf readout in debug modes.

## P2 -- flavour + polish
- **Early-game idle / "browse the internet" / shitpost actions:** low-stakes flavour actions that
  fill the calm early turns and reinforce the sense of time passing.
- **CoD-style AI-safety quote collection** on defeat ("whoops, defeat" -- a rotating set of real
  AI-safety quotes; light rage-bait; extends the existing aisafety.info link).
- **Loading screens / screen transitions** if runtime creeps (the baseline sim can hang a beat);
  make them a fun rage-bait moment. Tie to the debug processing-time work.
- **Full Gantt / progress lane** for the two-view split (the wireframe's progress-bar idea, fuller
  version once the in-queue progress lands).

## Art to generate (a few hundred generations spare)
- Onboarding "absent item" glowing-green dashed outlines (or do as a shader -- likely cheaper).
- UI elements / panel frames / status blips (the earlier UI-filler batch was weak; pair with the
  palette + likely the gpt-image-1 pipeline for icons).
- Loading-screen art.

## Cross-refs
`BUILD_BRIEF_PLAN_WATCH_UI.md` (two-view), `PALETTE_AND_DOOM_INTENSITY.md` (glow colours for the
green dashed outline = the "ok/computers-working" green), `docs/art/reviews/` (prop art for the office).
