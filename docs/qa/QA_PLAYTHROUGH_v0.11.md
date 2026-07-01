# P(Doom) QA Playthrough Session — v0.11+ (Comprehensive)

**Tester:** _______________  **Date:** _______________  **Build / commit:** _______________

> Companion to `QA_CHECKLIST.md`. That file covers the **established** systems (turn loop, hotkeys,
> debug overlay, accessibility, audio, doom, message log, bug reporter, screenshots, save/load) — run
> it for the baseline sweep. **This** file adds what's shipped since, a watch-list of known-suspect
> areas from recent work, a two-playthrough plan, and design-intent notes prompts.

## How to use
1. Sweep `QA_CHECKLIST.md` once (baseline coverage).
2. Do **Playthrough A** (Standard, full run) then **Playthrough B** (Easy or Hard).
3. Capture free-form notes as you go — note-space is throughout, don't wait for the end.
4. Press **F8** in-game to file bugs with state attached; log the meaty ones as GitHub issues after.

---

## ⚠️ SESSION WATCH-LIST (verify these specifically — known-suspect from recent work)

- [ ] **Easy & Hard games START without crashing.** A missing `max_action_points` crashed start-game on Easy/Hard; fixed in #540 — confirm it actually holds in real play.
- [ ] **Does difficulty change AP?** Per **#541**, Easy/Hard set `max_action_points` but `start_turn` ignores it, so AP may be identical across difficulties. Record AP on **turn 1** for each: Easy ___ / Standard ___ / Hard ___  *(expected right now: all 3 — confirm the bug, don't assume it's fixed)*.
- [ ] **Difficulty money modifiers apply.** Easy = +50% starting money, Hard = −25%. Record starting money: Easy ___ / Standard ___ / Hard ___.
- [ ] **Empty-seed "random" new games give different seeds** on rapid restart (#538 fix) — start two quick new games, confirm seeds differ.
- [ ] Full unit suite is green (220/220) — so anything broken here is gameplay/UX, not caught by tests. Trust your eyes over the green checkmark.

Notes: ___________________________________________________________________

---

## RECENTLY SHIPPED — not yet in the base checklist

### Research Quality — Rushed / Standard / Thorough (#500)
- [ ] Selector visible on research actions; defaults to **Standard**; remembers last choice.
- [ ] **Rushed** ≈ faster research; **Standard** = baseline; **Thorough** ≈ slower.
- [ ] **Rushed** raises risk / adds technical debt; **Thorough** lowers doom/risk — verify via the risk pools (F3).
- [ ] Trade-offs (speed vs safety vs debt) communicated clearly in the UI.
Notes: ___________________________________________________________________

### Risk Pool system (press **F3** for the debug overlay)
- [ ] F3 shows the **6 hidden pools**: Capability Overhang, Research Integrity, Regulatory Attention, Public Awareness, Insider Threat, Financial Exposure.
- [ ] Pools move sensibly in response to actions (rushed research → research-integrity / capability-overhang up; delayed publications → financial-exposure up).
- [ ] Crossing a pool threshold triggers an event.
- [ ] Do the pools *feel* like they're driving the doom trend, or are they invisible/inert?
Notes: ___________________________________________________________________

### Pre-Game Setup & Difficulty
- [ ] Player name, lab name, seed entry all work.
- [ ] Difficulty selectable (Easy / Standard / Hard). *(AP & money checks are in the watch-list above.)*
Notes: ___________________________________________________________________

### Scenarios / Mod hooks (#483)
- [ ] Scenario dropdown appears in Custom Game setup.
- [ ] **Bootstrap** ($500k, 200 compute), **Crisis** (2020 start, $150k, 65 doom), **Sandbox** ($10M) each load with the correct starting state.
- [ ] Custom start dates apply (check the in-game date).
Notes: ___________________________________________________________________

### Conferences & Travel (v0.11.0)
- [ ] Travel menu (**T**); attend a conference; submit a paper.
- [ ] The 9 conferences (NeurIPS, ICML, ICLR, AAAI, FAccT, AIES, MATS, ILIAD, Safety Retreat) appear with sensible deadlines.
- [ ] Costs (flights / accommodation / registration) deducted; reputation / paper effects land.
Notes: ___________________________________________________________________

### Scoring & Baseline (#372)
- [ ] End-game score displays + the **"no-action" baseline** comparison ("how much did my decisions matter?").
- [ ] Leaderboard / local high-score records the run.
Notes: ___________________________________________________________________

### What's New modal (#481)
- [ ] Shows automatically on first launch after an update; "What's New" button in the menu; patch notes correct.
Notes: ___________________________________________________________________

---

## PLAYTHROUGH A — Standard difficulty, full run (breadth)
Goal: exercise the whole loop end-to-end — 100 turns, or to a win/loss.

- [ ] **Setup**: new game, Standard, default scenario. Starting state sane.
- [ ] **Early game (turns 1–15)**: hire, first research (try each quality level), first events, doom baseline.
- [ ] **Mid game (15–50)**: upgrades, conferences, funding pressure, rival activity, risk pools climbing.
- [ ] **Late game (50–100)**: doom trend, crisis events, do choices still feel meaningful?
- [ ] **Endgame**: victory or doom-100 loss triggers correctly; score + baseline shown.

Pacing / "is it fun" observations (where did it drag, spike, or click?):
___________________________________________________________________
___________________________________________________________________

## PLAYTHROUGH B — Easy OR Hard (difficulty + watch-list)
Goal: confirm difficulty modifiers + clear the watch-list. A shorter run is fine.

- [ ] Game starts (no crash). AP & money recorded (see watch-list).
- [ ] Difficulty *feels* different (or doesn't — note it).
Notes: ___________________________________________________________________

---

## EXPERIENTIAL / DESIGN-INTENT NOTES (against the canon)
The design docs (`TONE_AND_ART.md`, `TWO_ACT_STRUCTURE.md`, `INTRO_CINEMATIC.md`) are **concept**, mostly
not-yet-built. Note how close the *current* build feels to the intent and what's missing:

- **"Cozy competence under existential dread"** — does the moment-to-moment loop feel warm / competent / low-pressure? Does dread live in the *trend* (doom meter, hidden pools) rather than the moment? Where does it fail?
- **Readability** — are ambient/mood elements distinct from interactive ones? Anything you couldn't tell was clickable?
- **Counterfactual framing** — does the baseline/score make your decisions feel like they mattered, or is it still just "drive doom to 0"?
- **Time / two-act** — any sense of a 2017 start, history, or time-compression? (Mostly unbuilt — note the gap vs the doc.)
- **Tone** — moments that landed the cozy-grimdark dissonance? Moments that broke it?
Notes: ___________________________________________________________________
___________________________________________________________________

---

## BUGS FOUND (file the meaty ones as GitHub issues / F8 in-game)

| # | Severity | Area | Description | Repro |
|---|----------|------|-------------|-------|
| 1 |          |      |             |       |
| 2 |          |      |             |       |
| 3 |          |      |             |       |

**Severity:** Critical / Major / Minor / Cosmetic

## OVERALL
- Most-broken thing: _______________________   Most-promising thing: _______________________
- Ready for the playtester friend?  [ ] Yes  [ ] Needs work
- **Recording captured?** [ ] Yes  (← the "QA video for fun" idea)
