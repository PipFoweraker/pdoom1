# Build Brief -- #789 Hiring Stitch (onboarding prompts + reserved-AP chain + scheduled-interview surfacing)

> Steering artifact for a later implementation agent (Pip commits the code). This is an
> IMPLEMENTATION SPEC, not finished code: plan, touchpoints, data shapes, pseudocode,
> decision points. Do not re-litigate ruled design -- cite it.
>
> Issue: #789 "Hiring stitch: onboarding sub-actions as AP-sink prompts on offer-accept +
> interview schedule->happen flow" (label `ship:hotpatch-48h`).
> Design substrate (ruled): ADR-0011 (effort economy), ADR-0010 (adoption routing),
> ADR-0009 (durations / no-instant-strategy / crisp reserve), ADR-0004 (pay-to-see),
> ADR-0003 (ledger promises), ADR-0014 (conferences/presence).
> Prior build brief (Phase A/B, MOSTLY BUILT): `docs/game-design/BUILD_BRIEF_HIRING_PIPELINE.md`.
> Ladder policy: `docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md` (recommends C2).

---

## 0. TL;DR and the single most important finding

**#789 is NOT a greenfield build, and it is NOT "reconcile the art-archive worktree".** The
entire source -> interview -> offer -> onboard pipeline is ALREADY MERGED to `main` (PR #664,
commit `556f74bf` "feat(hiring): Phase B -- source/interview/offer/onboard pipeline"). It lives
in `godot/scripts/core/hiring_pipeline.gd` (662 lines), is wired into `game_state.gd`,
`month_controller.gd`, `actions.gd`, and `main_ui.gd`, is data-driven through
`godot/data/balance/defaults.json` `"hiring"` block, and is covered by
`test_hiring_data_model.gd` + `test_hiring_pipeline.gd`.

So #789 is a **STITCH on top of built mechanics**: it wires three player-experience seams that
the merged pipeline resolves *silently and automatically* today:

1. **Onboarding sub-actions surfaced as PROMPTS on offer-accept** (they exist as costed
   actions -- `HiringPipeline.onboard_step` -- but nothing prompts the player when a hire lands
   mid-turn).
2. **A reserved-AP chained follow-up** so the player can spend *reserved* Attention on those
   onboarding steps inside the turn cycle (today onboarding draws from the AVAILABLE pool only).
3. **Scheduled-interview -> it-happens notification** (the schedule->resolve mechanic already
   exists; the resolution is silent -- no pop-up/notification fires when the interview lands).

Everything hard (data model, determinism, duration jobs, negotiation floor, attrition) is done.
#789 is mostly control-flow + UI + one small `MonthPlan` capability. Estimated ~60% UI/feed,
~30% control-flow (pause-on-accept), ~10% data/balance.

### 0.1 The worktree correction (do not chase it)

The coordinator flagged unmerged hiring work in `.claude/worktrees/art-archive`
(branch `feat/art-review-tool`). Verified state:

- That branch is **28 commits BEHIND `origin/main` and 3 ahead**. Its 3 "ahead" commits are
  `d3ddbdbb feat(hiring): Phase B`, `eb726215 fix(hiring): execute plan turn before setting
  implicit Attention reserve (#664)`, `40c49f8d feat(hiring): sourcing redesign -- no free
  refill, 4 guaranteed-rider starters, ad-response feed`.
- `git merge-base --is-ancestor` reports all three as NOT ancestors of `origin/main` -- but that
  is because the branch was rebased/re-authored, not because the work is missing. **The
  content is already on main**: `git diff origin/main..HEAD -- hiring_pipeline.gd` from the
  worktree is EMPTY (byte-identical), and main's `test_hiring_data_model.gd:160-184` already
  asserts the "exactly four starters" + "each starter carries a hidden rider" behavior from the
  `40c49f8d` sourcing-redesign commit.
- The worktree's large diff vs main (e.g. `leaderboard_sync.gd` -326, `music_manager.gd` -276,
  `quirks.json` -119) is the branch MISSING later main work, not new hiring work.

**Conclusion: treat the worktree as superseded. Do NOT merge or rebase it for #789.** Build
#789 against `origin/main`. (If Pip wants the art-review tool from that branch, that is a
separate cherry-pick, out of scope here.)

---

## 1. What #789 is -- the stitch

The pipeline turns hiring into a chained, gated process (the "fishing-line"): source ->
interview (scheduled -> happens on its date) -> offer -> onboard. The MECHANICS of every stage
are built. What is missing is the **turn-cycle choreography** that makes the chain *feel* like a
chain to the player:

### Player-experience problem (Pip, 2026-07-22, A/B build)

- **The AP "ticks down weirdly."** Pip anticipates "a chain of things when hiring someone" but
  there is "no way inside the turn cycle for the next action, presently, to sprint to attention
  and let me use some of the reserved AP." Concretely: when a candidate accepts an offer during
  day-tick playback, the onboarding follow-ups (laptop, mentoring, visa) exist as actions but
  (a) do not announce themselves and (b) can only be paid from the AVAILABLE Attention pool at
  the next plan phase -- there is no way to spend the crisp RESERVE on the immediate follow-up.
- **Interviewing does not read as schedule-then-happen.** The interview is queued with a
  resolve-on-turn and lands silently a few ticks later; the player never gets the "this is
  happening now" beat.

### The two deliverables (verbatim from the issue)

1. **Onboarding sub-actions as prompts + predictable AP sinks.** Laptop-provisioning + mentoring
   for a new hire should surface as PROMPTS when a candidate ACCEPTS an offer during the turn,
   and act as predictable AP sinks you can plan for *when you make the offer*.
2. **Interview = schedule -> happen.** Interviewing should read like SCHEDULING an interview,
   then it taking place later. When the interview happens, fire a pop-up/notification (pairs
   with the newness-glow sibling issue).

The gameplay change (AP economy + timing) forks the ladder -- see Section 8.

---

## 2. Mapping onto ADR-0011's ruled substrate

The stitch must not invent economy. It rides the ruled effort economy:

- **Founder hours = Attention, sacred and monthly** (ADR-0011 decision 1-2; "spent on ...
  approvals (hires, direction rulings)"). In code this is `MonthPlan.attention_total`
  (`month_plan.gd:24`), granted `Balance.inum("attention.per_month", 20)`
  (`game_state.gd:230`). A hire IS an approval -- so onboarding sub-actions spending Attention is
  exactly the ruled model, not a new sink.
- **No global AP pool** (ADR-0011 decision 1). Do NOT resurrect the legacy AP pool. `MonthPlan`
  is the only founder currency; `hiring_pipeline.gd` already spends through
  `state.month_plan.spend_attention(...)` (e.g. `hiring_pipeline.gd:91,115,183,257,412`).
- **The crisp reserve** (ADR-0009 S3, surfaced in ADR-0011 decision 2 "reserve -- instant-speed
  firefighting"). `MonthPlan` already models it: `attention_reserved`, `reserve_used`,
  `set_reserve()`, `pay_from_reserve()` (`month_plan.gd:26-27,61-71,125-131`). Today ONLY
  `window_resolver.gd` draws from it (`window_resolver.gd:78-82` `handle_reserve`). #789's
  chained follow-up is the SECOND consumer of the reserve.

**Ruled vs added by #789:**

| Concern | Ruled (cite) | Added by #789 |
| --- | --- | --- |
| Onboarding items are costed Attention actions | Built: `hiring_pipeline.gd:352-413` | Surface them as prompts on accept |
| Crisp reserve exists + evaporates monthly | ADR-0009 S3/S4; `month_plan.gd:39-49,125-131` | Let onboarding pay FROM reserve (new draw path) |
| Hires are approvals costing founder hours | ADR-0011 decision 2 | Reserve-at-offer-time so the approval chain is affordable |
| Interview reveals, never fabricates | ADR-0004; `hiring_pipeline.gd:170-192,448-454` | Fire a notification when it resolves |

Nothing here adds a currency or a new mechanic class -- Rams #10 (ADR-0011 "no new
player-facing currency"). If the reserve-draw for onboarding needs a design justification, it is
ADR-0009's reserve being used for exactly its stated purpose: instant-speed follow-through the
player pre-funded.

---

## 3. The reserved-AP chain mechanic (design + options + recommendation)

This is the mechanically novel part. The problem: an offer resolves during day-tick playback
(`month_controller.gd:88-89` -> `HiringPipeline.on_tick` -> `_resolve_job` KIND_OFFER ->
`_resolve_offer` -> `_accept_offer`, `hiring_pipeline.gd:445-470,273-323`). Acceptance currently
completes silently and the hire is left un-onboarded (`_accept_offer` sets `onboarded=false`,
`hiring_pipeline.gd:302-307`). The player only discovers the onboarding backlog next time they
open the hiring submenu. Pip wants the moment of acceptance to (a) interrupt and prompt, and
(b) let him pay from reserve.

### The affordance we are modeling

"When I make the offer, I want to earmark Attention so that when they accept, I can immediately
kit them out without waiting for next month." That is a **plan-time reserve decision** feeding an
**instant-speed follow-up** -- structurally identical to a response window (ADR-0009 S3). So the
cleanest design reuses the window machinery rather than inventing a parallel one.

### Option A -- Reuse the response-window pipeline (RECOMMENDED)

Model offer-acceptance as an auto-generated response window ("Onboard <name>?") that pauses the
turn exactly like an event window does today (`month_controller.gd:95-108` already pauses on
`window_queue`). Its HANDLE options are the onboarding sub-actions, each payable via
`handle_reserve` (draws `pay_from_reserve`) or `handle_cannibalize` (eats available / kills WIP)
-- both already implemented in `window_resolver.gd:60-127`.

- Pros: zero new pause/resume control flow; reserve-draw path already exists and is tested
  (`test_window_resolver.gd`); "sprint to attention" is literally what a window is; the crisp
  reserve gets its second consumer with no new accounting.
- Cons: onboarding is multi-step (laptop, then maybe visa, then optional mentoring) and windows
  are one-decision -- so either the window offers "do the whole checklist for N reserve" as one
  HANDLE, or it re-queues itself per step. A one-shot "onboard fully from reserve" HANDLE is the
  simplest and matches "predictable AP sink you can plan for."
- Recommendation: **one HANDLE = "Provision + onboard <name> now"** priced at the sum of the
  hard-checklist Attention (`laptop_attention` + `visa_attention` if `needs_visa`), payable
  from reserve or by cannibalizing; a second option "Defer (onboard later from the hiring
  screen)" = the current silent behavior; mentoring stays a separate, optional, later choice
  (its skimped/attrition tension, ADR-0011, is preserved).

### Option B -- A bespoke "hiring follow-up" prompt (not the window pipeline)

A new lightweight modal specific to onboarding, with its own reserve-draw call to
`MonthPlan.pay_from_reserve`.

- Pros: full control over multi-step UX (show laptop/visa/mentoring as a checklist with per-item
  reserve spend); does not overload the event-window semantics (rep penalty on ignore, tier
  classes) onto a hiring action.
- Cons: duplicates pause/resume; a second place that can desync `pending_events` on save/load
  (`month_controller.gd:97-99` `_sync_pending` exists precisely to avoid that); more test
  surface.

### Option C -- No pause; a persistent "needs onboarding" tray + earmark-at-offer

Do not interrupt the turn at all. At offer time, let the player earmark reserve
(`MonthPlan.set_reserve`) tagged for this hire; surface accepted-but-un-onboarded hires in a
persistent tray (the in-flight hiring box already exists: `main_ui.gd:62,212-220,781-783`), and
let onboarding steps there spend the earmarked reserve.

- Pros: no pause (respects Pip's design principle against rage-quit friction / interruption
  fatigue); "earmark when you make the offer" is exactly the issue's "predictable AP sinks you
  can plan for when you make the offer."
- Cons: reserve is a single undifferentiated pool (`month_plan.gd:26`) -- "tagged" reserve needs
  either a real per-hire earmark field (new state) or is only notional; less of a "sprint to
  attention" beat.

### Recommendation

**Ship Option A for the pause-and-pay beat, borrowing Option C's earmark-at-offer framing as
the UI copy.** Reasoning: Option A reuses tested pause + reserve-draw plumbing (lowest risk for a
`ship:hotpatch-48h` item), and the issue explicitly wants a PROMPT on accept (A gives it) plus
"plan for it when you make the offer" (surface the projected onboarding Attention cost in the
offer confirmation, and nudge the player to raise their reserve then). Keep mentoring OUT of the
forced prompt so the slack-as-insurance tension survives.

Open sub-decision for Pip (Section 9): does the accept-prompt HARD-PAUSE the turn (window
semantics) or is it a non-blocking toast with a "onboard now" button (respects
interruption-fatigue principle)? Pip's own design note "rage-quit friction" argues for the
softer version; the issue's word "PROMPTS" argues for the harder one.

---

## 4. Scheduling -- interview-date -> interview-happens; conference attendance alignment

### 4.1 Interview schedule -> happen (mostly built; add the surfacing)

Already implemented: `launch_interview` appends a job with
`resolves_on_turn = state.turn + Balance.inum("hiring.interview.duration_ticks", 3)`
(`hiring_pipeline.gd:185-191`). `on_tick` pops due jobs and, for KIND_INTERVIEW, calls
`reveal_more` and appends a `{"kind": "interview_done", ...}` entry to `last_events`
(`hiring_pipeline.gd:428-454`). `month_controller` calls `on_tick` every resolution tick
(`month_controller.gd:88-89`).

**The gap: `last_events` is a transient readout that nothing surfaces as a notification.** The
comment at `hiring_pipeline.gd:33-35` says it is "for the turn feed + tests. NOT serialized."
Grep confirms no caller pipes `state.hiring.last_events` into `NotificationManager` or the feed
on tick.

Data shape already present (no change needed):
```
# hiring_pipeline job (hiring_pipeline.gd:185-191)
{ job_id:String, kind:"interview", candidate_id:String, resolves_on_turn:int, params:{} }
# on resolve, last_events gets (hiring_pipeline.gd:453):
{ kind:"interview_done", candidate:String, reveal_level:int, was:int }
```

Trigger/timestep design: hook where `on_tick` is already called
(`month_controller.gd:88-89`). After `state.hiring.on_tick(state)`, drain `last_events` and
route each to (a) `NotificationManager` toast and (b) the turn feed. This is a pure-view side
effect on an already-deterministic resolution -- NO RNG, NO sim change (see Section 8 for why
this alone does not require careful determinism review, but the reserve-draw does).

Pseudocode (see Section 7 for the full version):
```
# month_controller, right after on_tick:
if state.hiring != null:
    state.hiring.on_tick(state)
    for ev in state.hiring.last_events:
        _surface_hiring_event(ev)   # -> NotificationManager + feed line
```

### 4.2 Conference / workshop attendance alignment (lead author must attend)

This is the second, LARGER scheduling ambition in the task framing. Grounding:

- Conferences already exist as scheduled world objects with a `month` field
  (`conferences.gd:26-60`, e.g. NeurIPS month 12, ICML month 7) and a rich schema (tier,
  location_tier, deadlines, prestige). ADR-0014 decision 1 rules conferences are "scheduled
  world events on the seed timeline (ADR-0005 schedule entries)" announced ~9 months ahead.
- Papers already track authorship: `paper_submissions.gd:46-47` has `lead_researcher_name` and
  `co_author_names`.
- ADR-0014 decision 2 rules "Founder attendance >> delegate attendance" and delegates cost "a
  staff-month + travel cash."
- The seed schedule (`seed_schedule.gd`) can inject events but currently only handles
  `rival_funding_wave` / `rival_aggression_shift` / `inject_event` (`seed_schedule.gd:18`) --
  conferences are NOT yet on the injected timeline; they are a static catalogue queried by month
  (`conferences.gd:277-283`).

**Assessment: full "lead author must attend the conference on its date" is a NEW subsystem that
ADR-0014 explicitly PARKED ("conference attendance subgame ... Subgame parked; v1 is attendance
+ yields", ADR-0014 context + rejected-alternatives).** It is out of scope for a
`ship:hotpatch-48h` stitch and should be a separate issue in the ADR-0010/0014 socialization
wave. For #789, recommend the MINIMAL alignment hook only:

- Add a data field on the paper/submission linking it to a target conference id + its month
  (`conferences.gd` already has month), and a soft check "if `lead_researcher_name` is on staff
  and the conference is this month, presence yields the full ADR-0014 bonus; otherwise a
  delegate/absent penalty." Implement as a check at the existing conference-resolution point, not
  a new scheduled-interrupt.
- Defer the "must attend or the paper is not presented" hard gate + the travel-planning
  allocation to the ADR-0014 subgame issue.

Flag this split explicitly to Pip (Section 9, Decision 4): #789 ships interview-surfacing +
onboarding-prompt-chain; conference-attendance alignment is scoped down to a soft
presence-yield hook or deferred entirely.

---

## 5. Data model + state changes (extend the EXISTING model)

The existing model is complete for the pipeline; #789 adds only small surfacing/earmark state.

### 5.1 Already present (DO NOT re-add) -- cite so the agent reuses them

- `Researcher` onboarding fields (`researcher.gd:41-47`): `candidate_id`, `needs_visa`,
  `onboarded` (default true), `laptop_done`, `visa_done`, `mentoring_done`, `mentoring_skipped`.
  All round-trip through `to_dict`/`from_dict` (`researcher.gd:624-631,667-675`).
- `Researcher.HireState` enum + guarded transitions (`researcher.gd:62,509-528`).
- Reveal ladder + `get_card_data()` (`researcher.gd:71-88,545-567`).
- `MonthPlan` reserve accounting: `attention_reserved`, `reserve_used`, `set_reserve()`,
  `pay_from_reserve()`, `reserve_remaining()` (`month_plan.gd:26-27,56-71,125-131`).
- `HiringPipeline` jobs + `on_tick` / `on_month_boundary` (`hiring_pipeline.gd:428-481`), all
  serialized (`hiring_pipeline.gd:631-661`), wired into `game_state.gd:66-69,229-231,926-927,
  1127-1132`.
- Balance keys: `godot/data/balance/defaults.json` `"hiring"` block
  (`defaults.json:51-58`) -- advertise/connections/interview/offer/onboarding costs already
  externalized.

### 5.2 New state #789 introduces (minimal)

Option A (recommended) needs almost no new durable state, because the window pipeline carries the
prompt transiently. If Pip picks the earmark-at-offer framing (Section 3 Option C flavor), add:

- On the offer job params (already a free-form dict, `hiring_pipeline.gd:268`): optional
  `earmark_onboarding_attention: int` recorded at offer time. Serialized already (params
  round-trips, `hiring_pipeline.gd:657-660`), but add an explicit `int()` cast in `from_dict`
  next to the existing `cash` cast (`hiring_pipeline.gd:658-659`).
- OPTIONAL new balance key `hiring.onboarding.provision_bundle_attention` if you want the
  one-shot "provision now" HANDLE priced independently of the sum of item costs. Otherwise
  compute it as `laptop_attention + (visa_attention if needs_visa)`.

New data for the accept-prompt window (transient, not durable) -- an event dict shaped for
`window_resolver`:
```
{
  "id": "hiring_onboard_<candidate_id>",
  "kind": "hiring_onboard_prompt",
  "title": "%s starts Monday -- provision them?" % name,
  "window": {
      "attention_cost": <hard_checklist_attention>,
      "handle_option": "provision_now",
      "ignore_option": "defer",
      "unignorable": false          # deferring is legal (silent-onboard-later path)
  },
  "candidate_id": <candidate_id>
}
```
This mirrors the window schema `window_resolver.window_config` reads (`window_resolver.gd:25-48`).

### 5.3 Determinism note on data

Adding notifications: pure view, no draws. Adding the accept-prompt window: it PAUSES resolution
after the offer already rolled its accept/reject (`_resolve_offer`, `hiring_pipeline.gd:273-290`
consumes `state.rng` BEFORE the prompt), so the RNG stream is untouched by the prompt. The
onboarding steps themselves already consume no RNG (`onboard_step`, `hiring_pipeline.gd:352-388`
is pure). So the ledger of RNG draws is unchanged -- see Section 8.

---

## 6. UI touchpoints

- **`godot/scripts/ui/candidate_card.gd`** (`candidate_card.gd:1-46`): pure view over
  `get_card_data()`. #789 adds an onboarding-progress strip (laptop/visa/mentoring checkboxes +
  per-item Attention cost) for EMPLOYED-but-not-onboarded researchers. Read `onboarding_status`
  (`hiring_pipeline.gd:339-349`). Keep it a pure view -- buttons route through the action
  delegates, do not mutate the model here (the card's contract, `candidate_card.gd:6-8`).
- **`godot/scripts/ui/main_ui.gd`**:
  - The in-flight hiring tracker already exists (`main_ui.gd:62,212-220`, populated by
    `_update_inflight_hiring_display`, `main_ui.gd:781-783`). Extend it to show onboarding
    hires with their remaining checklist + a "provision now" affordance.
  - The hiring submenu (`main_ui.gd:1554-1656`) already lists candidates + an ONBOARDING
    section (`main_ui.gd:1650-1656`). Add the reserve-spend button here for the non-paused path.
  - The accept-prompt window (Option A) renders through whatever renders event windows today
    (find the `PAUSED_ON_WINDOW` consumer of `month_controller` result; `main_ui.gd` handles the
    `paused_on_window` status). Confirm the window renderer can display a hiring-flavored window.
- **`godot/autoload/notification_manager.gd`** (`notification_manager.gd:23,186-199`): call
  `NotificationManager.info(...)` / `.success(...)` for "Interview with <name> happened -- new
  info revealed" and "<name> accepted -- provision them". Note toasts auto-dismiss in 3s
  (`notification_manager.gd:12`); pair the interview toast with the newness-glow sibling issue so
  the revealed card is discoverable after the toast fades.
- **Onboarding advisor nudge (#801)**: `getting_started_hint` is visible while `turn < 3`
  (`main_ui.gd:866-867`, node from `plan_screen.getting_started_hint`, `main_ui.gd:31`). #801
  wants a diegetic advisor saying "Doom is rising. Start by hiring a researcher." #789 should
  make that nudge POINT AT the now-legible pipeline: when `state.researchers` is near-empty and
  the pool has candidates, the hint text should say "Interview a candidate to start hiring" and
  (stretch) highlight the hiring submenu button. Keep the wiring loose -- #801 owns the advisor
  persona; #789 only ensures the hiring entry point is the thing the nudge can point to. Do not
  duplicate #720's welcome overlay.

---

## 7. Implementation plan (ordered, with touchpoints + pseudocode)

Build in this order; each step keeps the fast gate green and the game playable.

### Step 1 -- Surface interview resolution as a notification + feed line (smallest, safe)

Files: `godot/scripts/core/month_controller.gd` (the `on_tick` call site, `:88-89`); a new tiny
helper; `godot/autoload/notification_manager.gd` (reuse).

```
# month_controller.gd, replace lines 88-89:
if state.hiring != null:
    state.hiring.on_tick(state)
    for ev in state.hiring.last_events:
        _surface_hiring_event(state, ev)

func _surface_hiring_event(state, ev: Dictionary) -> void:
    match String(ev.get("kind", "")):
        "interview_done":
            var msg := "Interview with %s happened -- %s" % [
                ev.get("candidate",""), _reveal_blurb(int(ev.get("reveal_level",0)))]
            NotificationManager.info(msg)          # toast
            state.append_feed_line(msg)            # feed channel (find the existing feed API)
        "connection_hit": ...
        "advertise_hit": ...
        "offer_accepted", "offer_resentful_accept": pass   # handled in Step 3
```
Note: `month_controller` is core/deterministic; calling the `NotificationManager` autoload from
it may be undesirable for headless/sim runs. Prefer emitting a signal or returning the events up
to `main_ui.gd` (which already consumes the tick result dict, `month_controller.gd:102-108`) and
firing the toast THERE. Decide with Pip (keep core UI-free -- recommended: bubble events up in
the result dict and let `main_ui.gd` toast them).

### Step 2 -- Onboarding progress on the candidate card + reserve-spend button (non-paused path)

Files: `candidate_card.gd`, `main_ui.gd` (submenu + in-flight tracker), `actions.gd`
(`onboard_next` already exists, `:305-306`; add per-item + pay-from-reserve variants).

```
# new HiringPipeline method (mirrors onboard_step but draws reserve first):
func onboard_step_from_reserve(state, candidate_id, item) -> Dictionary:
    var cand := find_employed(state, candidate_id)
    ...
    var att := _item_attention(item)      # laptop/visa/mentoring cost from Balance
    # try reserve first (the crisp reserve, ADR-0009 S3), else available:
    if state.month_plan.reserve_remaining() >= att:
        state.month_plan.pay_from_reserve(att)
    elif state.month_plan.available() >= att:
        state.month_plan.spend_attention(att)
    else:
        return {"success": false, "message": "Not enough Attention (reserve or available)."}
    # money cost + flag flip identical to onboard_step (refactor the shared body)
    ...
```
Refactor `onboard_step` (`hiring_pipeline.gd:352-388`) so the money+flag logic is shared and only
the Attention SOURCE differs -- avoid a copy that can desync.

### Step 3 -- The accept-prompt (the reserved-AP chain beat)

Files: `hiring_pipeline.gd` (`_accept_offer`, `:293-323`), `month_controller.gd` (window queue),
window renderer in `main_ui.gd`.

Design: when `_accept_offer` employs the hire, instead of silently leaving them un-onboarded,
emit an event into the pipeline's `last_events` tagged `offer_accepted` carrying the candidate id
and the projected hard-checklist Attention. `month_controller` (or `main_ui` per Step 1's
decision) converts that into a response-window pushed onto `window_queue`, which already pauses
the turn (`month_controller.gd:95-108`).

```
# _accept_offer tail (hiring_pipeline.gd ~:323), add to last_events:
last_events.append({
    "kind": "offer_accepted",
    "candidate_id": cand.candidate_id,
    "candidate": cand.researcher_name,
    "onboard_attention": _hard_checklist_attention(cand),  # laptop + visa-if-needed
})

# window build (month_controller or a small HiringWindows helper):
func _hiring_accept_window(ev) -> Dictionary:
    return {
        "id": "hiring_onboard_%s" % ev["candidate_id"],
        "kind": "hiring_onboard_prompt",
        "title": "%s accepted -- provision + onboard now?" % ev["candidate"],
        "window": {
            "attention_cost": int(ev["onboard_attention"]),
            "handle_option": "provision_now",
            "ignore_option": "defer",
            "unignorable": false,
        },
        "candidate_id": ev["candidate_id"],
    }
```
Resolution routes through `window_resolver.resolve(...)` (`window_resolver.gd:60-127`):
`handle_reserve` -> pays the bundle from reserve and calls the shared onboard body for laptop
(+visa); `handle_cannibalize` -> pays from available/kills WIP; `ignore`/`defer` -> current
silent behavior (hire stays un-onboarded, surfaces in the tray). Mentoring is NOT in the window
-- it stays an optional later step so the skimped/attrition tension (ADR-0011,
`hiring_pipeline.gd:503-518`) survives.

Guard: the offer's accept/reject RNG roll happens in `_resolve_offer`
(`hiring_pipeline.gd:284`) BEFORE the window is built, so pausing does not move any draw.

### Step 4 -- Offer-time projection ("plan for it when you make the offer")

Files: `main_ui.gd` offer confirmation, optional `hiring_pipeline.gd` params earmark.

In the offer UI, show "If accepted, onboarding will cost ~N Attention" (from
`_hard_checklist_attention`) and surface the current `reserve_remaining()` so the player can bump
their reserve via the existing `MonthPlan.set_reserve` before ending the turn. Optionally persist
`earmark_onboarding_attention` on the offer job params (Section 5.2).

### Step 5 -- #801 nudge pointer + conference soft-hook (scoped per Section 4.2 / 9)

Wire the getting-started hint to point at the hiring entry point; add the minimal conference
presence-yield check only if Pip greenlights it (Decision 4).

---

## 8. Ladder + tests

### 8.1 Ladder version -- YES it bumps (C2 batched)

Per `BUILD_VS_LADDER_VERSION_SPLIT.md` Section 3.3 checklist, #789 answers "yes" to Q2 (changes
what happens on a fixed seed: the reserve-draw path and the accept-pause change the Attention
economy) and arguably Q4 (control-flow change around offer resolution). Section 3.1 lists
"effort economy (ADR-0011)" as a bump trigger. **Decision C2 (recommended in that doc,
`:450-471`): batch #789 into a single v0.13 gameplay epoch, do NOT give it its own epoch bump.**

CRITICAL DEPENDENCY TO FLAG: the ladder-version split itself is **still a DRAFT and UNBUILT** --
`ladder_version.txt` does not exist yet, `GameConfig.get_board_version()` does not exist, the
board key still reads `CURRENT_VERSION` (`BUILD_VS_LADDER_VERSION_SPLIT.md:1-9` status DRAFT).
So #789 cannot "bump the ladder" through machinery that is not there. Two paths (Pip decides,
Section 9 Decision 3):
- (a) Land the ladder split FIRST (its own PR, per that doc's appendix), then #789 bumps
  `ladder_version.txt`; or
- (b) If #789 ships before the split, it bumps `version.txt` to the v0.13 gameplay build, which
  today forks the board anyway (the current coupling) -- acceptable at the 48h/pre-launch mark
  but note it scatters cosmetic-patch testers per the split doc's whole rationale.

Recommend (a) if the split is close; otherwise (b) with a note to reconcile at the v0.13 cut.

### 8.2 Tests to add

Fast gate (`godot/tests/unit`, must keep `--min-tests 300` green,
`python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300`):

- Extend `test_hiring_data_model.gd` / `test_hiring_pipeline.gd`:
  - `test_accept_emits_onboard_prompt_event`: after an offer resolves to accept in `on_tick`,
    `last_events` contains an `offer_accepted` entry carrying `candidate_id` +
    `onboard_attention`.
  - `test_onboard_from_reserve_draws_reserve_first`: with reserve set, `onboard_step_from_reserve`
    decrements `reserve_used` (via `pay_from_reserve`) not `attention_spent`; falls back to
    available when reserve is short; fails cleanly when both are short.
  - `test_onboard_bundle_attention_matches_checklist`: `_hard_checklist_attention` = laptop +
    (visa iff `needs_visa`), excludes mentoring.
  - `test_defer_leaves_hire_unonboarded`: choosing defer/ignore keeps `onboarded == false` and
    the hire surfaces in the onboarding tray query.
  - `test_interview_resolution_event_shape`: `interview_done` event carries candidate +
    reveal_level (guards the Step 1 surfacing contract).
- `test_window_resolver.gd`: add a `hiring_onboard_prompt` window case exercising
  `handle_reserve` and `handle_cannibalize` for the bundle.
- Determinism: if the accept-prompt is proven RNG-neutral (Section 5.3), a targeted assertion in
  the simulation tier (`godot/tests/unit/simulation`, `--simulation`) that a fixed-seed run's RNG
  draw count is unchanged by enabling the prompt path. If any reserve-draw or prompt path is
  found to consume RNG, that is a red flag -- it must not. Run the slow tier only because this
  touches the resolution loop (`month_controller`), per CLAUDE.md guidance.

### 8.3 Non-negotiables (from CLAUDE.md + ADRs)

- Deterministic / replay-safe (ADR-0006): no new RNG draws in the stitch; the offer roll stays
  where it is (`hiring_pipeline.gd:284`).
- Keep `month_controller` (core) UI-free -- bubble hiring events up in the result dict; toast in
  `main_ui.gd` (Step 1 note).
- Scene nav (if any new screen): only via `SceneTransition` (CLAUDE.md). The prompt is a window,
  not a scene change, so this likely does not apply.
- Do not stage `.import`/`.uid` churn; stage only changed files.

---

## 9. Open decisions for Pip

1. **Prompt hardness (Section 3).** Accept-prompt as a HARD-PAUSE response window (issue says
   "PROMPTS"; reuses tested pause plumbing) vs a NON-BLOCKING toast + "onboard now" button
   (respects your rage-quit-friction / interruption-fatigue design principle)? Recommendation:
   window pipeline for reliability, but soften copy to feel like an opportunity not an
   interruption. Your call.
2. **Reserve-draw priority (Section 7 Step 2).** When onboarding from the prompt, draw from the
   crisp reserve FIRST then fall back to available, or make the player explicitly choose the
   source (as event windows do with handle_reserve vs handle_cannibalize)? Recommendation:
   explicit choice via the existing window options -- it teaches the reserve mechanic.
3. **Ladder sequencing (Section 8.1).** Land the build-vs-ladder split (currently DRAFT/unbuilt)
   BEFORE #789 so #789 cleanly bumps `ladder_version.txt` (path a), or ship #789 on a `version.txt`
   v0.13 bump and reconcile at the epoch cut (path b)? This is a real blocker: the ladder
   machinery #789 is "supposed" to bump does not exist yet.
4. **Conference attendance scope (Section 4.2).** ADR-0014 PARKED the attendance subgame. For
   #789, do the minimal soft presence-yield hook (lead author on staff + conference this month =
   full yield, else penalty), or DEFER conference alignment entirely to the ADR-0014
   socialization issue and ship #789 as interview-surfacing + onboarding-chain only?
   Recommendation: defer; keep #789 tight for the 48h tier.
5. **Mentoring in or out of the accept-prompt.** Recommendation: OUT (keep the slack-as-insurance
   / attrition tension, ADR-0011). Confirm.
6. **Worktree disposition.** Confirm the `art-archive` worktree is abandoned for hiring purposes
   (its hiring content is already on main; it is 28 commits stale). If you want its art-review
   tool, that is a separate cherry-pick.
