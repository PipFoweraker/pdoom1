# Build Brief — Plan/Watch UI + Employee Sprites

> Consolidates the 2026-07-16 plan/watch screen workshop (WORKSHOP_2_BACKLOG "Plan/Watch
> screen workshop" beats 1–4) into a build plan. Steering artifact for the build lanes.
> Aesthetic + feel rationale lives in the workshop captures; this is the *what to build*.

## The model (ruled)

**Two screens, a mode switch between them** (more modes possible later — Civ/XCOM precedent).
- **PLAN** = strategy. Verb: *"deal the cards from the hand you've got"* / lay your army out
  before battle (pre-commit the month). Calm, spatial, board-like.
- **WATCH** = tactics. The operator swivels to observing the office floor via live feeds while
  the month plays out in day-ticks. Ambient, temporal, reactive. The silhouetted operator +
  office scene live HERE.
- **COMMIT THE MONTH** transitions PLAN → WATCH; month-end review returns to PLAN.

**Aesthetic:** terminal / mainframe pastiche, lightly modernized (amber/green CRT, scanline,
boxes+rules), NOT literal retro. The ASCII mockups in the workshop ARE close to target.

**Phase-scaling (important):** UI complexity graduates with the 5-phase spine (WORLD_AND_LORE
"The five phases"). Startup = a small hand + a couple of people, panels-dominant, heads-down
terminal. Entity+ = the team panel unfolds into a swimlane/assignment board. Titan = division
abstraction + scene-dominant spectacle. **Build the Startup/Incubator version first**; leave
seams for the later unfold. Do NOT impose management-board complexity early.

---

## PLAN screen (build target: Startup/Incubator)

Reference mockup: workshop beat 1. Elements:
1. **Header:** Turn N · planning <Month Year> · **Attention budget** as depleting pips
   (allocated ●●● vs reserved ○○○ — the reserve/allocation gauge; ADR-0011 ~20/mo, data-driven).
2. **The committed queue ("The month ahead"):** the plays you've committed, each with a
   **gantt-style duration bar + ETA** ("lands ~M18") — the fishing-line made visual.
   **Queue ORDER = execution priority** (see mechanic below) — the list is reorderable.
3. **Reserve:** explicit held-Attention amount, part of the gauge.
4. **The hand:** action cards along the bottom, card-game register. **Baseline cards** (Research,
   Read, Scout, Shitpost — always playable) + **situational cards** that appear only when
   relevant (Interview when applicants exist, Respond-to-offer when offered). Each shows its
   Attention cost. **Show MORE cards than 20 Attention can play** (the honest scarcity — you
   leave things undone). Greyed = unaffordable this month.
5. **Team panel (small, early game):** founder row + a few hires, each showing assignment
   ("Sage → Interp research", "Riley → ⚠ drifting"). This is the SEED that unfolds into the
   swimlane board at Entity — build it collapsible/extensible.
6. **COMMIT THE MONTH** button → WATCH.

### Mechanic: queue order = execution priority (NEW — build this)
The committed queue's order is the **day-by-day execution priority**, resolved in order, locked
to ticks. Deterministic → resolves the intra-day sequencing question. Interacts with external
actors (a rival's mid-month move interleaves against your order; low-priority plays get bumped
under pressure). The player can reorder the queue at plan time — it's a real decision.

---

## WATCH screen (build target: Startup/Incubator)

Reference mockup: workshop beat 2. Elements:
1. **Header:** WATCH · <Month> · day NN/31 · **playback controls (play/pause/speed)** ·
   **reserve remaining** (the slack available to spend on response windows).
2. **The feed:** dated entries (the #655 in-game-date fix), **rival actions shown inline**
   (makes the rival narratively present — DQ-12).
3. **P(DOOM) two-instrument display:** **rate** as a live sparkline (wiggles) + **level** as a
   grinding bar (climbs slowly) + names its own current driver. (The "rate wiggles, level
   grinds" ruling made visual; DESIGN_PHILOSOPHY.)
4. **In-flight queue:** the committed plays executing **in your committed order** (1→2→3), with
   progress bars and completion ticks.
5. **Across-your-desk:** response windows arrive as inbox slips — handle (reserve cost) / defer /
   ignore. Auto-pause on arrival (existing MonthController machinery).
6. **The office floor** = the employee-sprite component (below). Operator silhouette + office
   scene occupy the center-right; environmental reactions to events.

---

## Employee sprites (BUILD Tier 0 + Tier 1; PLAN Tier 2)

Build as a **standalone, reusable `OfficeFloor` scene/component** (testable on its own; embed
into WATCH later — do NOT couple it to a main_ui rebuild). Art and code are independent: code
works against placeholder blobs; **real sprite art + animation frames come from pixellab.ai**
(pixel-sprite / animation-protocol path, asset options #649) and drop in later.

**ARCHITECTURAL RULE — the OfficeFloor is a PURE VIEW (read-only).** It READS the roster/employee
state and never WRITES game state. This makes it **determinism-safe by construction** (replay
replays inputs→state; a cosmetic view can't affect the verified run — ADR-0006). Sprite wander
randomness therefore doesn't even need the seeded RNG. Corollary: sprite behavior must NEVER feed
back into game state (no "employees who chatted get a bonus" — that would require determinism and
break the clean separation).

- **Tier 0 (do):** placeholder representation — colored shapes + a hat, random drift. OG-pdoom1
  parity floor ("blobs with hats milling like molecule clusters").
- **Tier 1 (do — the MVP sweet spot):** `AnimatedSprite2D` characters + a lightweight FSM:
  states `idle / walking / working-at-desk / stressed`, optional `NavigationAgent2D` to path to
  a workstation. **KEY: the sprite's animation state is a cheap READOUT of the employee's real
  mechanical state** — working=at desk, unmanaged/drifting=wandering aimlessly, stressed/burnout=
  head-in-hands, unfed-appetite=pacing by the coffee machine. So the fishbowl IS the office-as-
  dashboard: you read who's a problem off the floor without opening a panel. Drive states from
  the real staff/researcher state (game_state roster), degrade gracefully if fields are absent.
- **Tier 2 (plan, do NOT build): first-round approach** — navmesh around a real office layout;
  contextual pair behaviors (two employees chat, gather at a whiteboard); event reactions
  (everyone glances up on a doom spike); more animation variety. Mostly ART cost, moderate code.
  First-round approach when it's built: (a) hand-authored `NavigationRegion2D` office layout with
  named work-zones (desks, coffee, whiteboard); (b) a small utility/blackboard layer picking
  contextual actions from employee state + proximity; (c) an event-reaction hook (global signal →
  sprites play a reaction anim). All Tier-2 behavior stays a pure view (read-only, per the rule).
- **Tier 3 (LLM-driven generative agents / Smallville): OUT — not even a stretch goal.** Two
  reasons: (1) an LLM in the behavior loop **breaks replay determinism** (ADR-0006 — verified runs
  must reproduce); (2) over-engineered for fishbowl flavor. Pixellab is for *animation frames*, not
  a behavior brain — the behavior is the deterministic (or pure-view) Tier-1 FSM.

---

## Deferred to later waves (captured, NOT this build)
- **Costume/hat cosmetics** (presentation-rep lever; impostor-syndrome satire) — future content.
- **Office-as-moral-mirror** (office aesthetic reflects upgrades + moral path + doom) — future
  art/logic; leave a `office_tier` / `moral_skew` seam in OfficeFloor if cheap, else defer.
- **Swimlane assignment board** (Entity-phase unfold of the team panel) — leave the seam.
- **Operator representation** (anonymous silhouette; customizable trappings not face) — OPEN fork.

## Build phasing / lanes
- **Lane 1 — Plan/Watch scaffold (Phase A):** the two-screen structure + mode switch + COMMIT
  transition + migrate existing functionality into the right screen + first terminal-styling
  pass. Reviewable first cut (do NOT one-shot full polish; keep the game playable). Pip-review.
- **Lane 2 — Employee sprites Tier 0/1:** the standalone OfficeFloor component. Pip-review.
- **Follow-ups (after Lane 1 lands + Pip reacts):** Plan-screen polish (card-hand, duration bars,
  reserve gauge, reorderable queue-order); Watch-screen polish (two-instrument doom, desk-slips);
  OfficeFloor integration into WATCH.
