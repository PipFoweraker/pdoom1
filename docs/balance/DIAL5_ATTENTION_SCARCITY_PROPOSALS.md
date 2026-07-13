# Dial 5 — Attention / Reserve Scarcity: a menu of adjustments

**Lane:** design-proposals (dial 5) · **For:** Pip to yes/no · **Date:** 2026-07-14
**Source of the problem:** `docs/balance/L1_SWEEP_2026-07-13.md` §2 Q5 ("reserve is inert") + §4 dial 6.
**Nothing here is applied.** These are directions to argue with; every number is first-pass.

---

## The finding, stated as an equation

From the sweep (§2 Q5, §4 dial 6): supply is `attention.per_month = 20`; demand is `WindowResolver.DEFAULT_ATTENTION_COST = 1` × `window_demand_budget = 3` ≈ **3 Attention of window demand against 20 supply**. That is ~6.7× oversupply. Consequence the sweep proved directly: *"Even `greedy_overcommit` (reserve 0) handled all 3 windows by cannibalizing with zero failures."* The crisp-reserve gamble ADR-0009 built (HANDLE-from-reserve = "painless — what insurance was for") has **no teeth**, because the insurance never has to pay out. Reserve-heavy's apparent survival edge is a confound — those runs also queue safety actions; the reserve itself buys nothing.

So the dial has exactly two screws, per §4 dial 6: **cut supply** (fewer Attention) or **raise demand** (windows/plan actions cost more, or an overhead eats the float). Everything below is a way of turning one or both, plus how reserve becomes genuine insurance once the gap closes.

**One caveat that governs all of it (sweep §4 sequencing note):** dial 6 must be tuned *last*, "once a month actually completes and the window economy is observable." Right now no run survives a month (doom wall), so these are all *directional commitments you can ratify now* and *numbers you calibrate after the doom rebalance lands*. Ratify the shape; defer the decimals.

---

## Proposal A — Supply cut (20 → 10–12/month)

**Mechanism.** Lower `attention.per_month` from 20 to ~10–12. Leave window cost at 1 and the spawn window budget at 3. The gap closes from 20-vs-3 to 12-vs-3 (≈4×) or 10-vs-3 (≈3.3×) — still loose, so A alone is a *partial* screw.

**What it makes the player feel.** "I don't have enough hours." Directly renders the founder line ADR-0011 canonizes — founder hours are "sacred, roughly fixed." Fewer, heavier decisions.

**Interactions.** Cleanest possible change (one constant). But it **collides with a ruled grain**: WORKSHOP_2_BACKLOG "L1 spec inputs" fixes the founder unit at *"decisions, ~20/month"*, and DESIGN_PHILOSOPHY "On the hero and the office" derives it as *"~1 meaningful decision/day ≈ 5/week ≈ 20-and-a-bit/month."* Cutting supply to 12 says the founder makes 12 decisions/month — contradicting the canon 20 unless you also say each decision costs >1 Attention (which is really Proposal B wearing A's clothes). Plays fine with the plan screen (just a smaller number on it) and with era scaling (C can raise it back later).

**Cost of being wrong.** If cut too far, you re-create the sweep's headline failure at the Attention layer — the player runs out before the plan is expressible, and the "20 decisions" feel dies. Low-effort to try, low-effort to revert, but it fights a decision Pip already made.

**Recommend if you want X** = the blunt, one-line screw and you're willing to renegotiate the "~20/month" canon down to ~12.

---

## Proposal B — Demand rise: price plan actions + an admin-overhead tax

**Mechanism.** Keep nominal supply at 20 (preserves the "~20 decisions/month" canon). Make the 20 *spoken-for* instead of free:
1. **Price the plan-phase actions** ADR-0011 §2 already names — *doors, approvals, audits* — in Attention. Sketch: door (stakeholder face-time) ~2–3, approval (a hire, a direction ruling) ~1–2, audit (skip-level ground-truthing) ~2. Currently only "reserve" (windows) draws Attention; doors/approvals/audits price *nothing*, which is exactly why 17 of the 20 sits idle.
2. **Add a flat admin-overhead tax**, ~4/month at spawn, deducted before the player allocates anything. This is Pip's explicit ask (*"Admin is painful in this game, I want that to be part of the overhead"*). Crucially it **shrinks as ops/admin staff are hired** — ADR-0011 §6: *"Ops/admin staff reduce the founder-price of routine actions and automate whole classes over time."* Sketch: −1 to −2 Attention of admin bought back per ops hire, floor ~1, endpoint the 2037 "payroll is automated" vignette.
3. **Raise window face cost** 1 → ~2–3, so the three spawn windows demand ~6–9, not 3.

Arithmetic against the 20-vs-3 baseline: admin ~4 + three windows at ~2.5 (~7.5) already claims ~11.5 of 20 before a single door/audit. Add a realistic plan (a door + an audit + an approval ≈ 6–7) and total *addressable* demand exceeds 20 — the player must now **prioritise and hold reserve deliberately**. Reserve stops being the leftover 17 and becomes a chosen bet.

**What it makes the player feel.** Every month starts already half-spent (admin), and doing the strategic things you want (doors compound social capital — DESIGN_PHILOSOPHY "successes plus schmoozing... buys doors, and doors compound") trades directly against the reserve that answers surprises. This is the slack-as-insurance gamble made real: *"they will get away by being greedy and overcommitting... but maybe."*

**Interactions.** This is the proposal that makes ADR-0011's closing line true — *"founder-hour prices for doors/audits/approvals... set the whole game's attention economy."* Feeds straight into the plan-screen redesign (ADR-0011 consequence): the priced actions and the admin line are what that screen displays. The ops-staff buyback is the mechanical form of *"staff buy back founder time"* (DESIGN_PHILOSOPHY "On work and delegation"). Composes with reserve gamble (makes it bite) and with era scaling (C raises these prices over the run). No new currency, no new panel — pure read/writes on existing Attention (satisfies the restraint rule).

**Cost of being wrong.** Two failure modes: (i) plan prices too high → plan-phase paralysis, the player can afford almost nothing and the month feels like pure tax; (ii) admin tax too high or not visibly reducible → "painful overhead" tips into un-fun grind with no agency. Mitigate by making the buyback legible early (first ops hire visibly cuts admin) so the tax reads as a *problem staff solve*, not a flat penalty. Medium effort (needs the plan actions to actually charge Attention, which the plan screen doesn't exist for yet — so partly gated on that UI).

**Recommend if you want X** = to keep the "~20 decisions" canon intact, make ADR-0011's four founder-hour categories finally *price something*, and get the admin-overhead flavour Pip explicitly asked for — the most canon-consistent screw.

---

## Proposal C — Era scaling: demand and window cost rise toward endgame

**Mechanism.** Already half-ruled: window demand budget rises **2–3/month at spawn → 5–6 in true endgame** (WORKSHOP_2_BACKLOG "L1 spec inputs"; ADR-0009 §Consequences flags the per-era density pass). Add the second axis: **late-game window Attention cost rises** too (spawn ~2 → endgame ~4). Late demand then ≈ 6 windows × 4 ≈ 24 against a 20 supply — *structurally uncoverable by the founder alone*. Scarcity is not present at spawn; it **emerges over the run**.

**What it makes the player feel.** The early game is survivable solo; the late game is not — you must have built the office. The only way to cover 24 demand on 20 supply is managers absorbing window classes (ADR-0011 §5: *"managers are interrupt shields... they absorb their team's class of response windows"*) and ops staff buying back admin (§6). This is *"we don't power up the player, we power up the office"* (DESIGN_PHILOSOPHY "On the hero and the office") expressed as an Attention curve. It also arms the midgame trigger — DQ-22's *"the world starts shooting back"* — with a resource correlate: rising window pressure is what the growing office is racing.

**Interactions.** Composes with everything — it's a time-axis multiplier on B's prices and A's supply. Ties to ADR-0009's *"Risk (~40%): late-game dead air if interrupt density doesn't scale with era."* Home for the display is the month review screen (ADR-0009 consequence; DQ-14 world-state progression). **Hard dependency on the sweep caveat:** you cannot tune the endgame numbers until a month — then a run — actually completes; today every run dies in month 0, so C is *shape-now, number-later* more than any other.

**Cost of being wrong.** If the ramp is too steep, the endgame is unplayable regardless of office quality (founder drowns before delegation can catch up); too shallow and scarcity never arrives, leaving the same inert-reserve problem in the late game. Because it can't be measured yet, the risk of mis-set numbers is highest here — but the *direction* is already ruled, so ratifying costs nothing.

**Recommend if you want X** = scarcity to be something the growing office out-builds rather than a wall at spawn, and to give the "power up the office" fantasy a concrete resource it's racing.

---

## Proposal D — Uninsured-handling premium (reserve as genuine insurance discount)

**Mechanism.** Make **HANDLE-by-cannibalizing cost meaningfully more Attention than HANDLE-from-reserve.** Sketch: reserve-handle pays the window's face price (say 2.5); cannibalize pays face × ~1.5 (≈3.75), the surcharge representing the disruption of tearing into committed WIP. Reserve becomes a *discount you pre-paid for* — the mechanical form of "insurance."

**What it makes the player feel.** Holding reserve visibly pays: the same crisis costs less if you saw it coming and kept slack. Overcommitting is still legal (ADR-0009 point 4) but now *marginal* — you can bull through on cannibalize, you just bleed extra. Directly instantiates the slack-as-insurance quote (DESIGN_PHILOSOPHY "On the turn").

**Interactions.** This is the proposal that most literally answers §2 Q5's "for the reserve to become insurance." **But it has a load-bearing dependency: D does nothing at 6× oversupply** — if you can cannibalize freely (as today, where the sweep notes *"strategic WIP has no effect in v1 anyway"*), a premium on a free action is still ~free. D requires A or B to have closed the gap first. Also a **double-charge risk**: ADR-0009 already defines cannibalize's real cost as *"delay/kill planned WIP"* — once L2 gives WIP gameplay effect, the lost work *is* the cost, and an Attention surcharge on top double-bills. So D is best framed as a **v1 bridge**: the Attention premium stands in for WIP-loss until L2 makes WIP bite, then softens.

**Cost of being wrong.** If the premium is too large, nobody ever cannibalizes and D collapses into a hard "you must hold reserve" rule (removing the legal gamble ADR-0009 wants). If too small, reserve still doesn't visibly pay. And if it ships without A/B, it's inert. Low effort mechanically (one pricing branch in the resolver), but useless standalone.

**Recommend if you want X** = the reserve gamble to *visibly* reward foresight this version, before L2's WIP system exists to do that job properly.

---

## Proposal E — Cramming penalty: soft cap via degraded decision quality (Pip's own flag)

**Mechanism.** Instead of a hard 20-Attention wall, the **last N Attention each month (say the final ~4–5) are spent at degraded decision quality** — a soft cap. Overcommitting past your comfortable budget stays *legal* but each crammed decision resolves worse (weaker outcome roll, higher chance of a bad branch). Renders Pip's flagged speculation verbatim (DESIGN_PHILOSOPHY "On the hero and the office"): *"Decisions imply draining something like mana or willpower, and this implies poor decisions if you're cramming, although this is speculation."*

**What it makes the player feel.** Fatigue. You *can* keep clicking, but you feel yourself getting sloppy — the 18th decision of the month lands worse than the 3rd. A texture no other proposal gives: the cost of overcommitment is *quality*, not a locked button.

**Interactions.** Softens A's bluntness — a soft cap is gentler than a hard supply cut and keeps the "~20 decisions" canon (you *can* make 20+, they just degrade). Feeds delta chips (L6/EE-7) as the legibility surface — the player must *see* the quality hit or it's invisible punishment. **Restraint-rule risk:** "decision quality" is arguably a new hidden variable (the restraint rule: *"a mechanic that needs a new player-facing currency or panel has to prove it can't be a read/write on existing ones first"*). It survives the rule *only if* the degradation is expressed as a modifier on existing outcome rolls surfaced through existing chips — not a new "willpower" meter. If it needs its own gauge, it fails restraint.

**Cost of being wrong.** Highest legibility risk of the five: if the degradation is opaque, it violates the honesty line (DESIGN_PHILOSOPHY "the game must explain your death before it kills you") — the player loses to bad rolls they didn't know they were buying. It's also the most speculative (Pip flagged it himself) and the most likely to sprawl into a subsystem. Medium-high effort and the one most likely to need a second design pass.

**Recommend if you want X** = the fatigue/cramming *texture* specifically, and you're willing to invest in making the quality-degradation legible so it doesn't become hidden punishment.

---

## What composes vs what conflicts

- **B + D + C compose cleanly and reinforce.** B closes the supply–demand gap (so D's insurance premium has something to insure against), D makes the held reserve visibly pay, C makes the whole thing tighten over the run and hands the late game to the office. This is a single coherent arc: *spawn = live gamble → endgame = uncoverable-solo, out-built by delegation.*
- **D depends on A-or-B.** D is inert at 6× oversupply. Never ship D alone.
- **A and B are two doses of the same medicine** (close the gap). Running *both* hard over-squeezes — 12 supply *and* priced plan actions *and* admin tax *and* costlier windows could re-wall the month. Pick one primary. B is the more canon-consistent (keeps 20); A is the blunter fallback. They don't hard-conflict, but stacking both at full strength does.
- **A conflicts with the "~20 decisions/month" canon** unless you also renegotiate that grain. B does not (it keeps 20 nominal, spends it down).
- **E substitutes for the hard edge of A** (soft cap vs hard cut) — you'd run E *instead of* A's harshness, not both. E composes fine with B/C/D as a texture layer, but carries the restraint + legibility risk the others don't.
- **C is orthogonal** — a time multiplier that rides on top of whatever supply/demand shape you pick. Nearly free to ratify (direction already ruled), most gated on "wait for a month to complete" for numbers.

---

## Recommended package

**B (demand rise: priced plan actions + shrinking admin tax) + D (uninsured-handling premium) + C (era scaling).**

**One-sentence rationale:** Keep the ruled ~20-decisions/month canon intact but make roughly half of it spoken-for (admin overhead + priced doors/approvals/audits), so the reserve you hold back becomes a real bet; price the uninsured-handling premium so that bet is genuine insurance this version; and let both window demand and window cost climb with the era so scarcity is something the growing office must out-build rather than a wall at spawn.

**Deliberately excluded:** A (fights the 20-decisions canon; B does A's job without the conflict) and E (highest legibility/restraint risk and Pip-flagged-speculative — hold it as a *texture* to add later if the priced-overhead version still feels too binary). Both remain live if you disagree.

**Sequencing:** ratify shapes now; set all decimals *after* the doom rebalance (sweep dials #1–#4) lets a month complete, per the sweep's own "tune dial 6 last" note.

---

## Checklist for Pip (yes / no / one word)

1. **Cut nominal supply below 20?** (Proposal A) — yes / no
`Pip:`

2. **Keep 20 nominal but price plan actions (doors/approvals/audits) in Attention?** (B) — yes / no
`Pip:`

3. **Add an admin-overhead tax (~4/mo) that ops staff buy back down?** (B) — yes / no
`Pip:`

4. **Raise window face cost from 1 → ~2–3?** (B) — yes / no
`Pip:`

5. **Make cannibalize cost more Attention than reserve-handle (insurance discount)?** (D) — yes / no
`Pip:`

6. **Ratify the era-scaling direction (demand 3→6 + rising window cost) now, numbers later?** (C) — yes / no
`Pip:`

7. **Build the cramming soft-cap / degraded-quality texture?** (E) — yes / no / later
`Pip:`

8. **Endorse the recommended package B+D+C as the spine?** — yes / no
`Pip:`

9. **Any number here you want to overrule on sight?** — one word / figure
`Pip:`
