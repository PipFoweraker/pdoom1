# SEED: Conference as a Player-Chosen Rhythm Break -- design seed

> RAW DESIGN SEED, not decided canon. Built from Pip's 2026-07-27 ruling on
> ADR-0014's parked "conference subgame" ambition. [PIP] = verbatim quote;
> [CLAUDE-note] = secretariat synthesis, reword or discard freely.
>
> **Feeds:** Wednesday R3b / W-block (WS-3 conference finish, per
> WS3_FINISH_OR_DROP.md section 3).
>
> **Siblings (2026-07-27 R5 emit batch):** `SEED_VIGNETTE_SPECS.md` (this
> seed's mini-scene beats feed the conference-cycle vignette specs 02-04+29),
> `SEED_GOVERNANCE_BODIES_NAMES.md`, `SEED_GOVERNANCE_NAMES_YESAND.md`. Day
> record: `WS3A_DAYLOG_2026-07-27.md`.

## 0. The ruling [PIP]

> "a really good placeholder conference experience that we can then build on
> later ... fade-out - replace with conference mini-scene - fade-in a few days
> later with a backlog of things that have stacked up, and the middle
> experience can be automatically resolved or very little interaction for
> now - this creates an interesting break in the player's rhythm that they can
> control much like combat in Heroes of Might and Magic compared to the normal
> turn structure."

Supersedes WS3_FINISH_OR_DROP's "downscope, sequence after ADR-0010-v1" on ONE
axis only: the shell (fade/mini-scene/fade/backlog) can build now, decoupled
from the yields it eventually carries. It does not unstick the sequencing
rule on real adoption/contact numbers -- see section 3.

## 1. The tempo mechanic

**Player controls:** departure timing (any turn a conference is on the
schedule, ADR-0014 point 1) and delegate choice (founder vs staff, point 2).
Duration is NOT a v1 dial -- each conference has a fixed length ("a few
days"), so the player chooses WHETHER to attend, not how long (v2 knob,
section 6).

**What freezes vs accrues** is load-bearing: `turn_manager.gd`'s
`start_turn()` step order IS the deterministic RNG stream ("STEP ORDER IS
LOAD-BEARING" per its own docstring). Two candidate models:
- **(A) Skip-turns:** the conference consumes N real turns; `start_turn()`
  keeps running normally for every other system (finance, salaries, events),
  the away-founder/delegate is just flagged unavailable. Backlog = those
  turns' triggered_events. Cheap, deterministic for free (same stream/order),
  but risks feeling like "you lost N turns," not a break FROM the structure.
- **(B) True pocket:** a bounded micro-loop (section 2) that does NOT advance
  `state.turn`; on exit, batch-advance N turns deterministically in one shot
  (the sim-speed "batch-advance" knob, SEED_SPEED_AND_COMPLEXITY.md section
  1, repurposed as a player-facing tempo control), then present the backlog.
  Truer to HoMM's actual pause, but needs batch-advance proven deterministic
  outside dev-mode first.
[CLAUDE-note] Recommend (A) for the placeholder: existing turn loop plus an
availability flag, ships this week, trivially replay-safe -- (B) is the
version worth building once batch-advance graduates from dev-only.

**Return-burst UX -- feed-channel discipline.** DESIGN_PHILOSOPHY's three
intrusiveness tiers (ambient change < readable feed < response window) and
the modal-chokepoint lesson (month-review modals that auto-jump and can't be
inspected are a named FRESH_EYES failure, item 9) push one direction: the
return burst must NOT be a stack of N modals for N missed turns.
- Fade-in lands on the normal plan screen with a SINGLE dismissible/
  scrollable "while you were away" panel (month-review's shape, but
  scrollable, NOT auto-jumping -- FRESH_EYES item 9's ask), summarizing
  accrued feed lines in surfaced-order. The conference's own yields (flavor
  or real, section 3) headline it; routine accrual (salaries, auto-resolved
  events) reads as compressed feed lines underneath, not separate interrupts.
- No response-window items should accrue while away (a response window
  demands presence by definition). An event that WOULD have opened one
  either auto-resolves to a documented default, or defers to the founder's
  first turn back, surfaced at the TOP of the panel, not buried.

## 2. The HoMM analogy, made structural

Normal turns = strategic layer (plan -> act -> review, ADR-0009). HoMM's
battle screen is a bounded tactical pocket the player OPTS into from the
strategic map -- map pauses, pocket resolves, map resumes carrying the
outcome. Conference maps directly: attend = opt-in, mini-scene (section 4) =
pocket, backlog-on-return = outcome carried back.

**Why voluntary tempo change is the interesting part** [CLAUDE-note]: events
(ADR-0004's lethality rule -- the world may shout uninvited about what's
becoming lethal) are tempo breaks the player does NOT choose; their interest
is the interrupt itself. A conference inverts this: the player chooses to
LEAVE the normal rhythm, trading N turns of direct control for an accelerant
(ADR-0014 point 3) and a discovery burst (point 4) -- "is this worth the
blackout window," a legible-cost/fuzzy-payoff call, same shape as HoMM's
"commit my hero to this fight" but on the calendar axis. Worth protecting in
build: if attending is ever STRICTLY dominant (no real opportunity cost while
away), the framing collapses into "free button" and the HoMM comparison
stops holding.

## 3. Shell vs yields -- the buildable seam

- **SHELL (buildable now, no ADR-0010-v1 dependency):** fade-out trigger on
  the attend/send-delegation action (currently `is_stub: true` in
  `data/actions/travel.json:15-31`), the mini-scene, the skip-turns flag
  (1A), the fade-in + single backlog panel. Yields here are FLAVOR-ONLY: a
  feed line, a small reputation nudge, maybe a named contact stub with no
  receivable behavior -- exactly what turns "[Coming Soon]" into a real,
  shippable placeholder without waiting on anything.
- **YIELDS (wired in after ADR-0010-v1 exists):** the real adoption-accelerant
  multiplier and contacts-as-receivables minting into the Ledger's
  counterparty slot (`ledger.gd:16,30` already has the field) stay where
  WS3_FINISH_OR_DROP already sequenced them -- nothing to accelerate yet. The
  shell doesn't care whether its yield hook is a flavor stub or a real
  accelerant call; swap the function body, not the UX. [CLAUDE-note] This
  split lets Wednesday build the placeholder without re-opening the
  sequencing debate WS3_FINISH_OR_DROP already settled.

## 4. Mini-scene sketch options (pick fidelity, not concept)

1. **Text vignette (S, ~1 day).** Single scrollable panel, 1-3 short
   paragraphs (COPY_CORPUS voice), no new art/scene, auto-resolves on
   acknowledge. Fastest, weakest on "interesting break" -- reads as a toast.
2. **Single-screen tableau, office-art style (M, ~2-3 days).** One static
   illustrated backdrop (office-art palette/fidelity) with 2-4 clickable
   hotspots (booth, hallway chat, poster session), any order, rest
   auto-resolves on exit. Sweet spot for "very little interaction for now"
   while reading as a DIFFERENT place -- the visual context-switch IS the
   break.
3. **Light choice beat (M/L, ~3-5 days).** Tableau plus ONE bounded
   deterministic-safe choice (e.g. "hallway track" vs "turn in early" -> a
   small flavor delta via the existing RNG stream). Closest to the "subgame"
   ambition ADR-0014 parked -- this is that wedge's thin edge, not a
   separate thing. [CLAUDE-note] Recommend option 2: option 1 undersells the
   ask, option 3 reopens a parked decision before WS-3 rules on it.

## 5. Risks

- **Pacing dead-spot:** boring auto-resolve turns the "break" into a
  wait-state -- the failure the HoMM comparison is trying to avoid.
  Mitigation: even option 1 needs one line that surprises (a rival
  silhouette glimpsed at the conference, SEED_RIVAL, is a cheap payoff).
- **Save/replay determinism:** both models in section 1 must stay inside the
  deterministic RNG stream (ADR-0006). (A) is safe by construction. (B)'s
  batch-advance needs the same proof SEED_SPEED_AND_COMPLEXITY flags for
  dev-mode, extended to replay-recorded play -- do not ship (B) without it.
- **Backlog overwhelm vs no-early-loss:** an early-turn conference returning
  to a wall of accrued events risks the rage-quit-friction failure the design
  principles flag. Mitigation: early-attendable conferences are already rare
  (majors 9-month-announced, smaller ones invitation-gated) and early-turn
  event density is already low (ambient-floor principle) -- no special-casing
  needed.

## 6. Open questions for Pip

1. Duration fixed-per-conference (v1, this seed's assumption) or a player
   dial later -- confirm v1 stays fixed?
2. Model (A) skip-turns vs (B) true pocket for the placeholder -- ship (A)
   now, or worth the extra build for (B)'s truer "pause" feel?
3. Does a glimpsed-rival beat belong in the flavor yields, or is that
   jumping ahead of WS-3's Developments/Sightings ruling?
4. Founder-away: does the strategic layer fully lock the founder's action
   slot for the trip, or can delegates/staff still act around them?
5. Fidelity pick for Wednesday: option 2 (tableau) recommended -- confirmed,
   or option 1 (text) to ship faster and iterate later?
