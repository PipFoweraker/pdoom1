# Per-tick action resolution -- design + prototype (L3 / WS-3 groundwork)

Status: SPIKE ESCALATED TO DEV LANE. Branch `spike-resolve-time-spend`. NOT for
today's L2 floor+outs ship. Pip is the architect; this doc lays out options +
a recommendation per open question and a working prototype. Pip makes the calls.

Builds on commit `c65ae2d6` (the committed-vs-spent Attention accounting split).

## The problem Pip named

> "A flaw in the simulator's logic running into conflict with philosophy, and
> philosophy wants to win here."

The philosophy (ADR-0009): the MONTH is the plan cadence; the day-turn is the
resolution tick beneath it. Queued cards are meant to RESOLVE over the month's
day-ticks (~1/day, in order), interleaved with events and response windows, so
that a mid-month opportunity can DIVERT a not-yet-resolved card's still-unspent
Attention.

The flaw (traced in the spike): **queued cards do NOT resolve over ticks.** They
all execute at once in a single `TurnManager.execute_turn()` at `end_month`,
BEFORE day-tick playout begins. The day-tick loop then plays out only events and
windows. The duration machinery that WOULD spread cards over ticks
(`MonthPlan.queue_strategic` / `take_due_strategic`,
`MonthController.last_released_strategic`, the `_run_month_playback` `released`
hook) is DORMANT: nothing in the production path populates it, and the `released`
hook is ignored. `turn_manager.execute_turn` even carries the comment "L1
(ADR-0009) will redistribute these consequence steps across day ticks" -- future
tense, never done.

Consequence: mid-month diversion is impossible today (there is no window in which
a card sits queued-but-unresolved during playout), and `pay_by_cannibalizing` has
nothing to cancel (`queued_strategic` is always empty in production).

## What this lane does

Wire the dormant seam into the real action path so queued cards resolve on
day-ticks, interleaved with events/windows, debiting Attention as each resolves.
This unlocks: mid-month diversion (#824 F6, #825 event OUTS interplay), the teeth,
and the Attention-as-a-clock feel the philosophy wants.

## Architecture chosen (prototype)

Key realisation that de-risks replay: the replay simulator (`replay_simulator.gd`)
and the replay/determinism TESTS use a FLAT per-turn harness -- `start_turn ->
resolve pending_events -> queue actions_by_turn[t] -> execute_turn` -- that does
NOT model the MonthController/plan/window loop at all (it even ignores `k:"w"`
window records). So as long as each action still RESOLVES through a single
`execute_turn` call at its resolve turn (and `record_action` fires there), the
flat replay reproduces it by re-queuing actions at their recorded turn. This means
we do NOT route effects through the `last_released_strategic` hook (which would
force the replay simulator to model the whole month loop). Instead:

1. At `end_month` commit: convert each `queued_actions` entry into a
   `MonthPlan.queued_strategic` WIP card with a resolve tick (sequential, one per
   working day, in queue order). Do NOT resolve anything at commit. The plan-turn
   `execute_turn` now runs only the consequence steps (doom/rivals/papers), with
   an empty action queue.
2. During playout, `MonthController.advance_tick` pops the cards due this tick
   (`take_due_strategic`) and pushes their `action_id`s into `state.queued_actions`
   so the tick's `_complete_tick -> execute_turn -> _step_execute_queued_actions`
   resolves them: records into the replay log, debits committed Attention
   (`resolve_committed`), applies effects -- exactly the existing path, just fired
   at the resolve tick instead of at commit.
3. Attention: committed at queue time (`commit_attention`, from c65ae2d6), debited
   as each card resolves (`resolve_committed`). Cancelling an unresolved card
   releases the commitment (`pay_by_cannibalizing`, now WIP-aware).

Deterministic resolution order: cards resolve in (resolve_tick asc, queue order)
-- `queued_strategic` is insertion-ordered (= queue order) and `take_due_strategic`
scans it in order. Within a tick, events fire first (in `start_turn`), then any
window pauses/resolves, then due actions resolve in `_complete_tick`.

## Open questions for Pip (the calls to make)

### Q1. Action -> tick mapping (duration model)

Actions have NO duration field in data today. Options:

- **(1) Sequential one-per-day, queue order** [PROTOTYPE USES THIS]. The i-th
  queued card resolves on `commit_turn + 1 + i`. Matches Pip's "~1/day, in order".
  Simple, predictable, deterministic. Ignores intrinsic action length (hiring a
  researcher resolves as fast as buying compute).
- **(2) Per-action intrinsic duration from data.** Add `duration_days` to action
  JSON; card resolves that many days after commit. Richer (hiring = weeks, compute
  = a day); several can resolve the same day. Needs authoring ~40 actions + a
  default. Ordering within a tick = queue order.
- **(3) Hybrid: sequential dispatch + intrinsic duration.** One card is "started"
  per day in queue order, then takes its intrinsic duration to land. Most
  realistic, most complex.

RECOMMENDATION: ship (1) for the first playable, add (2) as a data pass once the
loop is proven. **Q for Pip: do intrinsic durations matter for the v1 feel, or is
"one decision resolves per day, in order" the intended texture?**

### Q2. The state-read question (the core balance call)

Today every queued action resolves at commit against commit-time state (they DO
see each other's mutations -- they run sequentially -- but NOT any intervening
events or daily consequence steps). Spreading resolution across ticks means a
later card reads state AFTER intervening events, doom accrual, rival progress, and
earlier cards. Options:

- **(A) Live reads -- plan meets reality** [PROTOTYPE USES THIS]. A card resolves
  against whatever state exists on its tick. Thematic ("your plan hits a changed
  world"), emergent, least code. Cost: a card can now FAIL at resolve if an
  intervening event drained the money/compute it needed (`execute_action` already
  returns `success:false` when `can_afford` fails at resolve). Higher variance;
  harder to balance.
- **(B) Escrow non-Attention costs at queue time.** Lock money/compute when the
  card is queued so later events cannot starve it; only effects are computed live.
  Preserves affordability guarantees; more accounting (per-resource escrow +
  refund on divert).
- **(C) Snapshot everything at queue (pure plan).** Precompute the full delta at
  queue, apply on the tick. Maximally predictable but kills the collision-with-
  reality -- mid-month events can't influence outcomes, defeating much of the point.

RECOMMENDATION: (A), because it is what makes the mechanic alive and matches
"philosophy wants to win". It forces a sub-decision:

  **Q2a. When a card cannot afford its non-Attention cost at resolve time, does it
  (a) fizzle + refund its committed Attention, (b) fizzle + consume the Attention
  (you spent attention planning a bet that reality spoiled), or (c) partial?**
  Prototype does (a)-ish: `resolve_committed` still fires (Attention debited) but
  the effect fails -- i.e. currently closer to (b). This needs Pip's ruling; it is
  a real feel/fairness call.

### Q3. Interleaving order with events/windows

Within a tick the prototype orders: (i) `start_turn` fires events (RNG), (ii) a
window may pause and be answered (may divert cards via cannibalize), (iii)
`_complete_tick` resolves the cards due this tick + runs consequence steps. So a
same-tick event/window sees cards from EARLIER ticks resolved but not this tick's
card (it resolves after). Alternative: resolve due cards BEFORE dispatching events
so a same-tick event sees today's action. RECOMMENDATION: events-before-actions
(matches the existing `start_turn`-then-`execute_turn` structure; reads as "morning
news, then you act"). **Q for Pip: confirm the within-tick order.**

### Q4. Mid-month diversion -- how the player sacrifices a card

`pay_by_cannibalizing` cancels queued WIP LIFO to free Attention for a window
HANDLE. Now that cards live in `queued_strategic`, this works. Open call:

- LIFO auto-selection [PROTOTYPE] vs letting the player PICK which queued card to
  sacrifice. LIFO is what the code does and is the least UI; explicit pick is a
  better decision surface but needs a diversion picker in the window dialog.
- A card due THIS tick is already committed to resolving (removed from
  `queued_strategic` before the window resolves) -- it cannot be diverted. Only
  not-yet-due cards can. This seems right (you cannot un-ring today's bell) but is
  a design consequence worth confirming.

RECOMMENDATION: LIFO for v1; explicit-pick as a WS-3 UI enhancement. **Q for Pip:
is LIFO acceptable for the first playable, and should diverting surface as its own
verb or stay folded into HANDLE-by-cannibalize?**

### Q5. The hiring-pipeline / implicit-reserve interaction (a genuine wrinkle)

The implicit reserve is set at commit to `total - committed` (all uncommitted
Attention guards windows), driving `available()` to 0 during playout. But
self-charging actions (the hiring pipeline spends Attention via
`spend_attention`, which checks `available()`) used to resolve AT COMMIT, before
the reserve was set, so `available() > 0`. Under per-tick resolution they resolve
DURING playout with `available() == 0` -- so a hiring card's internal self-charge
can be starved. This is the implicit-reserve design colliding with per-tick
resolution. Options: (a) exclude hiring-pipeline actions from per-tick conversion
(they already own a duration pipeline) -- prototype's fallback if tests break;
(b) make self-charge draw against committed-being-resolved; (c) redesign the
implicit reserve so it does not pre-claim all slack. **Q for Pip: this needs a
ruling at WS-3; it is the messiest seam.**

### Q6. Determinism / replay (forks the ladder -- intended for an L3 epoch)

Spreading action RNG (fundraise amounts, sabotage rolls, etc.) across ticks
interleaves it with per-tick event RNG differently than the batch model, so the
verification HASH changes -- a NEW ladder epoch, which is fine (L3). Requirements:
the new order must be strictly deterministic (it is -- see resolution order above),
and replays within the new epoch must verify. Because actions still resolve via
`execute_turn` at their recorded turn, the flat replay simulator reproduces the
new order WITHOUT modification. KNOWN PRE-EXISTING GAP (not introduced here): the
replay simulator does not model the window/plan loop and ignores `k:"w"` records,
so real runs with RNG-consuming window resolutions are not byte-faithfully
replayable today. That is orthogonal and should be its own WS-3 task (make the
replay simulator drive the real MonthController).

### Q7. Balance implications to re-sweep

- Pacing: outcomes now depend on WHEN in the month a card lands and what happened
  first -- variance up. The `deliberate`/Attention-aware policy in the sweep should
  be re-run against the new epoch.
- Affordability: under Q2(A), late cards can fizzle -- the sweep should measure
  fizzle rates and whether they punish reasonable plans.
- Diversion: the sweep's response-policy axis should gain a "divert a queued card"
  option to value mid-month opportunities against planned WIP.

## Prototype state

Implemented on this branch (see the commit after `c65ae2d6`):
- `month_plan.gd`: `queue_strategic` unified onto the committed model;
  `enqueue_committed_card` (schedule an already-committed card);
  `pay_by_cannibalizing` releases COMMITTED (WIP-aware diversion).
- `game_manager.gd` `end_month`: converts `queued_actions` to scheduled
  `queued_strategic` cards (sequential durations) instead of batch-resolving.
- `month_controller.gd` `advance_tick`: feeds cards due this tick into
  `queued_actions` so the tick's `execute_turn` resolves + records them.

Test results and the exact determinism deltas are recorded in the lane report.

## Sizing

Prototype (this doc + the wiring above, green on both gates): a few hours.
Production-ready WS-3: multi-session. The long poles are Q2 (state-read policy +
fizzle rules + escrow if chosen), Q5 (hiring/reserve seam), and the orthogonal
replay-simulator-models-the-month-loop task under Q6 -- each is its own designed
change with balance re-sweeps, not a same-day ship.
