# Playtest & QA Guide — post-workshop-2 consolidation lanes (2026-07-13)

> Covers everything merged since your last session: workshop-#2 docs (#611) + six
> build lanes L0/L7/L9/L10/L8/L6 (PRs #624/#623/#627/#628/#626/#625). **These lanes were
> deliberately behavior-preserving** (pre-rewrite consolidation) with **one intentional
> gameplay change** (doom-band colours) and **two genuinely new player-facing features**
> (save/load, achievements). The big mechanics rewrite (ADR-0009 month-turns etc.) is
> NOT in this build — that's L1 onward, still ahead.
>
> You're "feeling things out" — that's the point. Sections 1–2 are quick checks so a
> regression doesn't waste your QA; Section 4 is the real deliverable: subjective notes
> to feed the Fable QA round.

## 0. Get on the build
See the pull instructions in the session chat (fetch → pull --ff-only → `--import` pass).
**The `--import` pass is not optional** — skip it and the game/tests throw misleading
"class_name not declared" errors on a fresh sync.

## 1. NEW — exercise these (the actual additions)

- [ ] **Save / Load (L7).** Save from the pause menu mid-run; quit; Load from the
  welcome screen. Confirm the loaded game is *exactly* where you left it — money, doom,
  reputation, staff (with their traits), ledger entries (incl. any secret/exposed ones),
  a paper in flight, the current date/turn. Then play one more turn in the loaded game
  and sanity-check it behaves normally. *(This is the highest-value new thing to break.)*
- [ ] **Achievements (L8).** Watch for unlock toasts / log lines during play. Try to
  trip: first hire, first paper published, first loan taken, first staff departure,
  surviving a turn with doom > 90 ("White Knuckles"), and the year marks (survive into
  2022 / 2027 / 2032 / 2037). Check the game-over screen lists what you unlocked this run.
  They should feel like deadpan recognition, never a reward that changes the run.
- [ ] **Loss-legibility delta chips (L6).** Near each resource (money/doom/rep/compute)
  there should now be a per-turn change indicator (last turn's delta, red/green). Confirm
  it matches what actually happened. The event log should also state resource deltas.
- [ ] **Defeat screen attribution (L6).** When you die, the "why" should be more honest
  than before — a debt-driven collapse now reads as a *ledger* death even though doom or
  cash delivered the final blow. See Section 3 for why this matters.

## 2. REGRESSION SWEEP — should feel IDENTICAL (refactored surfaces)
These were moved/restructured but not meant to change. A 5-minute pass:
- [ ] Boot to menu, start a new game (no crashes, single clean load).
- [ ] End-turn / turn advance loop; "Do Nothing" / pass still works.
- [ ] **Event dialogs** pop and resolve, choices apply (extracted to `event_dialog.gd`).
- [ ] **Ledger screen** opens and reads correctly (extracted to `ledger_screen.gd`).
- [ ] **Employee roster / staff cards** render (extracted to `employee_panel.gd`).
- [ ] Every **submenu** (hiring, fundraising, financing, publicity, strategic, travel,
  operations) opens and aligns (shared `submenu_chrome.gd`).
- [ ] Hiring a specific candidate hires *that* candidate (the hire path was rewired
  through the engine — confirm no wrong-candidate or double-hire).
- [ ] Game-over screen shows correct totals.

## 3. KNOWN CHANGES / GOTCHAS (expected, not bugs)

- [ ] **You are no longer always on "test-seed".** Previously the game booted every run
  with a hardcoded `"test-seed"` regardless of what you entered — so your prior playtests
  may all have been the *same timeline*. That debt is fixed: the game now uses the
  configured/entered seed. If runs feel different from memory, this is likely why. (Set a
  known seed deliberately when you want to compare against a past run.)
- [ ] **Doom colours shifted (the one intentional gameplay change).** Doom status now
  routes through a single source (ThemeManager) with bands at **25 / 50 / 70 / 90**.
  Previously three different parts of the UI disagreed (30/60/80 vs 25/50/70/90 vs
  70/80). The meter/warnings/status will now agree with each other — but may look
  slightly different from your memory. Expected.
- [ ] **Don't trust a green CI check on GitHub.** Separately discovered this session: the
  Godot CI test gate has been reporting green while running zero tests (issue #629,
  shelved until post-QA). The real verification is running the game and the local suite.
  Your own eyes are the gate right now.

## 4. What to FEEL / capture (the Fable QA round deliverable)
Sections 1–3 are pass/fail. This is the subjective harvest — jot rough notes, no structure
needed; I'll interrogate them with you afterward:
- Does **save/load** preserve the *story* of a run, or does reloading feel like it breaks
  the fiction / momentum?
- Do **achievements** land emotionally (dark-comedy recognition) or read as noise/spam?
  Right ones? Missing an obvious one? Wrong tone on any?
- Do the **delta chips** actually help you understand what's killing you, or add clutter?
- Anything that *feels* off in pacing, difficulty, or legibility — even if you can't name
  it. Especially: does the game still punish engagement (the workshop's core complaint)?
- Screenshots of anything surprising → `docs/devblog/playtest-images/` (existing convention).

## 5. Optional 60-second determinism self-check
Play the same seed twice for ~5 turns making the same choices; the resource numbers should
track identically. If they diverge, that's a real determinism regression worth flagging
(the suites say they don't, but you're the ground truth this round).
