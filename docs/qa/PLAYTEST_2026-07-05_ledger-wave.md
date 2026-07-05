# Playtest — Ledger Wave (2026-07-05)

**Tester:** _______  **Date:** _______  **Build/commit:** `a48ab65`+ (`main`)

> First play since the "Big Pause" **plus** five new mechanic lanes (scoring rewire,
> determinism, replay, seed schedules, the Liability Ledger + its player-facing UI).
>
> **Division of labour:**
> - **This doc** = the *new* mechanics + a boot smoke pass + *feel*. Work it top-to-bottom.
> - **`QA_PLAYTHROUGH_v0.11.md`** = the general regression sweep (research quality, risk
>   pools/F3, difficulty, scenarios, conferences/T, events, accessibility, debug). Run it
>   after §1–2 here.
> - **The automated exploit sweep** (`docs/qa/EXPLOIT_SWEEP_2026-07-05.md`, landing
>   separately) measures *balance/dominant strategies* with bots — so here, judge **feel**,
>   not numbers. If something feels overpowered, note it; the bots will have quantified it.
>
> Capture as you go (don't wait for the end). **F8** files a bug with state attached.

---

## §0 · Boot smoke — DO FIRST (BL-1's click paths weren't verified in CI)
- [ ] Game launches to the welcome screen, no console errors.
- [ ] Start a **Standard** game → loads to the main UI, no errors.
- [ ] The **compact ledger summary** shows under the doom trend (`Ledger: $X owed | due Nt | Y secret`).
- [ ] A **Financing** action is present in the action list.
- [ ] **Financing → "View Ledger"** opens the ledger screen *(this is the specific
      unverified click path)*; closes via **[X]** / **ESC**.

If any of §0 fails, stop and note it — that's a BL-1 bug, not a design issue.
Notes: _______________________________________________________________

---

## §1 · The Liability Ledger loop (the new flagship — WS-1 + BL-1)

### Take on liabilities (Financing submenu)
- [ ] **Take Loan** — +$50k now; a payable entry appears, due in ~4 turns.
- [ ] **Funding-with-Strings** — +$40k; a governance-obligation entry appears.
- [ ] **Desperation Lever** — doom drops now; a **secret**, compounding governance liability appears (you can see your *own* secrets).
- [ ] **Contractor** — +2 AP; a small governance rider entry appears.

### The ledger screen reads clearly
- [ ] Each entry shows source, currency, principal, **due Nt**, interest, secret flag, side (payable/receivable).
- [ ] Outstanding totals shown; compact summary **reddens** as secrets mount.

### Fuses, interest, billing (advance several turns)
- [ ] A loan's fuse counts down and, when due, **bills** (money leaves).
- [ ] Interest **compounds** on carried entries turn-over-turn.
- [ ] An **unpayable** bill escalates into **doom** — and the post-mortem later **attributes** it to that entry.

### Exposure & blackmail (BL-2 — the teeth)
- [ ] Over turns, a **secret** liability gets **EXPOSED** → reputation/governance damage. *Confirm it actually fires.*
- [ ] Exposure can present a **blackmail** offer (a new, worse entry) — the chain continues.

### Death by ledger
- [ ] Lean into desperation levers/loans → you eventually die, and the **death is attributed to specific ledger entries** in the post-mortem.

### FEEL — the real question this wave exists to answer
- Is the ledger **legible**? Do you always know what you owe and when it bites?
- Is the tension **fun** — does "spend now, the bill compounds toward death" create good decisions, or is it opaque/fiddly bookkeeping?
- Does the **desperation lever** feel like a real *catch-up-when-behind* lever, or a no-brainer / a trap?
- Does the game now feel **more tense and rich** than the thin pre-wave version? *(This wave's whole reason for being.)*
Notes: _______________________________________________________________
_______________________________________________________________

---

## §2 · New scoring display (WS-A — changed since you last played)
- [ ] End-game shows **`Turn N · <integral>`** (turns survived · doom-integral) — **not** the old composite points total.
- [ ] **No victory bonus**; score is turns-survived-dominant, doom-integral only as tiebreak.
- [ ] **Post-mortem reveal only** — no live score ticker during play.
- [ ] Leaderboard records the run (keyed by seed + version).
- Feel: does "how many turns did you survive" read as the score you'd brag about? (The ADR-0002 thesis.)
Notes: _______________________________________________________________

---

## §3 · Regression since the Big Pause
- [ ] Run **`QA_PLAYTHROUGH_v0.11.md`** end-to-end (the general sweep).
- [ ] Anything that broke since you last played? Five lanes touched core (determinism,
      replay, seed schedules, ledger, scoring) — watch for regressions in events, doom,
      turn flow, save/load.
Notes: _______________________________________________________________

---

## §4 · Capture — tag every finding

| # | Tag | Area | Description | Repro / turn |
|---|-----|------|-------------|--------------|
| 1 |     |      |             |              |
| 2 |     |      |             |              |
| 3 |     |      |             |              |

**Tags:** `BUG` (→ GitHub issue / F8) · `BALANCE` (→ workshop #2; the sweep quantifies) · `FEEL` (→ workshop #2)

## Overall
- Does the ledger make the game **more tense / richer**? [ ] clearly [ ] somewhat [ ] not yet
- Most-broken thing: ______________  Most-promising thing: ______________
- Ready to show the playtester friend? [ ] Yes [ ] Needs work
