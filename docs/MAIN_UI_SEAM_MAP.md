# main_ui.gd -- Seam Map + Refactor Plan

**Status:** ACTIVE PLAN (2026-07-25). Steering artifact for the incremental
de-monolithing of `godot/scripts/ui/main_ui.gd` (~3k lines). WS-3 build lanes and
any agent touching `main_ui` MUST read this first and extract along these seams
rather than piling onto the monolith.

**Governing decision (Pip, 2026-07-25):** NOT a big-bang "sortie." One targeted
carve now (R4), a map for the rest, and incremental extraction distributed across
WS-3 lanes -- each seam pulled when the feature that touches it lands. Refactors
here are **non-forking** (internal structure, no gameplay/RNG/scoring change ->
build patch, not ladder epoch) but MUST be test-gated: fast gate (300+ tests)
green before AND after each carve. GDScript breaks silently.

---

## 1. The six responsibilities tangled in main_ui.gd

Grounded in the actual function inventory (2026-07-25). `main_ui.gd` conflates:

| Seam | Responsibility | Representative functions (current) | Why it hurts |
|---|---|---|---|
| **R1** | Layout / rendering | `_render_actions_grouped`, `_build_candidate_card`, `_build_onboarding_card`, `update_queued_actions_display` | View churn risks logic |
| **R2** | Input / hover | `_on_dynamic_action_pressed`, `_on_action_hover`, `_on_action_unhover`, `_trigger_action_by_index` | Input tangled with state reads |
| **R3** | Game-state reading | scattered `GameState`/`game_manager` reads inside render + handlers | No single read surface |
| **R4** | **Planning / attention / queue** | `_on_commit_plan_button_pressed`, `_on_clear_queue_button_pressed`, `_remove_queued_action`, `_calculate_queued_costs`, `update_queued_actions_display`, `_on_action_executed`, `_on_actions_available`, `_setup_plan_watch_scaffold` | **DOMAIN LOGIC in the UI -- the hotpatch-bleed** |
| **R5** | Submenu / dialog orchestration | `_show_hiring_submenu`, `_show_fundraising_submenu`, `_show_financing_submenu`, `_show_publicity_submenu`, `_show_strategic_submenu`, `_show_travel_submenu`, `_show_operations_submenu` + 7 matching `_on_*_option_selected` + `_decorate_active_submenu` / `_close_active_submenu` | **7 copy-pasted builders -- the single biggest line bloat** |
| **R6** | Event / result presentation -- **CARVED (CARVE 6 -> `event_result_presenter.gd`)** | `_hiring_action_result` (moved earlier w/ CARVE 3), `_on_action_executed` + `_on_achievement_unlocked` + `_on_error_occurred` (presentation) | Presentation mixed with mutation |

## 2. Target architecture

`main_ui.gd` becomes a **thin view**: it renders model state and emits *intents*;
it owns no domain logic. Two controllers absorb the domain seams:

```
  main_ui.gd (thin view)
    |  renders <- reads model
    |  emits intents ->
    |
    +-- PlanController        (R4: the plan/attention/queue model + ops)
    |     owns: queued actions, attention spend, cost calc, commit/clear
    |     wraps/uses existing MonthPlan + MonthController
    |
    +-- SubmenuController     (R5: one data-driven submenu component)
          owns: open/close, option list from data, option-selected -> intent
          replaces the 7 hand-rolled _show_*_submenu / _on_*_option_selected pairs
```

R1/R3/R6 stay in the view for now (they ARE view work); they get tidied opportunistically as lanes touch them. R2 input routes through the two controllers as intents.

## 3. Extraction order (and who triggers each)

**CARVE 1 -- R4 -> PlanController. DO NOW (quiet window). Priority.**
- Pull the queue/attention/cost/commit logic out of `main_ui` into a
  `PlanController` that wraps the existing `MonthPlan` / `MonthController`.
- `main_ui` keeps only: render the plan, wire buttons to `PlanController` calls.
- **Why first:** it is the actively-hotpatched seam AND the natural prerequisite
  for the per-tick resolution spike (`spike-resolve-time-spend`) -- per-tick IS a
  change to how the queue resolves, so the queue logic wants a clean home before
  per-tick lands on it. Do the carve, then per-tick sits on `PlanController`, not
  on the monolith.
- Test-gate: the queue/attention unit tests must stay green; add characterization
  tests for `_calculate_queued_costs` behaviour before moving it if coverage is thin.

**CARVE 2 -- R5 -> SubmenuController. HIGH-VALUE, LOW-RISK. Do when the first WS-3
lane needs a new submenu.**
- The 7 `_show_*_submenu` builders are ~near-identical: build a dialog, list
  options, decorate, wire `_on_*_option_selected`. Collapse to ONE data-driven
  `SubmenuController.open(submenu_id)` reading option lists from data/config.
- **Why high-value:** biggest single line reduction, pure UI pattern (low
  regression risk), and it stops the next submenu (people&money roster panel,
  Developments feed) from being an 8th copy-paste. Whichever WS-3 lane first adds
  a panel triggers this -- they build the generic component instead of copy #8.

**CARVE 6 -- R6 -> EventResultPresenter. DONE.**
- The event/result PRESENTATION (executed-action result, achievement unlock, engine
  error -> feed-log lines + the PLAN error toast) pulled out of `main_ui` into
  `godot/scripts/ui/event_result_presenter.gd` (RefCounted, holds a `host` ref back to
  the view, matching the CARVE 1-5 controller pattern). `main_ui` keeps thin signal
  shims (`_on_action_executed` / `_on_achievement_unlocked` / `_on_error_occurred`)
  that forward to the presenter, and still owns the feed MODEL (`log_message` +
  filters) the presenter writes through. `_hiring_action_result` was already moved with
  CARVE 3 (HiringPanelController), so R6's remaining target was the three signal
  handlers + the `_format_deltas` helper. Pure NON-FORKING move; fast gate green
  (647 tests, 0 fail) before and after. `main_ui.gd`: 1974 -> 1940 lines.

**CARVES 3+ -- R1/R2/R3 opportunistic.** No speculative extraction. Each WS-3
lane that touches rendering/input tidies its own patch toward the thin-view target
(boy-scout rule), guided by this map. Revisit for a formal pass only if a seam
proves painful again after WS-3.

## 4. Lane tagging (fill in at WS-3 scoping, #811)

| WS-3 lane / feature | Seam it naturally triggers |
|---|---|
| Per-tick resolution (spike-resolve-time-spend) | depends on CARVE 1 (R4) |
| People & money roster panel (#833) | triggers CARVE 2 (R5) |
| Developments / rival feed UI (SEED_RIVAL_AND_DEVELOPMENTS) | reuses CARVE 2 (R5) |
| Onboarding advisor / lever-pointer (#801) | opportunistic R1/R6 |

## 5. Non-negotiables

- **Non-forking.** No carve changes gameplay/RNG/scoring. Ladder stays put; these
  ship in build patches.
- **Test-gated.** `python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300`
  green before and after every carve. Touch simulation code -> also run `--simulation`.
- **Scene-nav rule still applies.** Any extracted controller changing scenes goes
  through `SceneTransition` (never `change_scene_to_file` from input/signals).
- **One carve per PR.** Keep each extraction reviewable; do not bundle R4 + R5.

**Related:** `docs/game-design/WORKSHOP_3_PREP.md` (WS-3 scoping), `spike-resolve-time-spend`
branch (per-tick prototype), `PEOPLE_AND_MONEY_COHESION.md` (#833), `docs/game-design/SEED_RIVAL_AND_DEVELOPMENTS.md`.
