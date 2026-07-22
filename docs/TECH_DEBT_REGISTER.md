# Tech Debt Register — pre-rewrite audit (2026-07-12)

> **Provenance:** three parallel code audits (hardcoded-values census; duplication/dead-
> code sweep; monolith seam analysis) run at the close of Fable workshop #2, funded as a
> deliberate debt-reduction pass before the ADR-0009..0013 rewrite. Every item carries a
> **build lane** (see `docs/game-design/WORKSHOP_2_BUILD_LANES.md`) and a **phase**:
> BEFORE the rewrite (behavior-preserving), DURING (rewritten anyway), or **LET-DIE**
> (do not touch — the rewrite deletes it). Implementation sessions: fix items in your
> lane, log new debt here, never polish LET-DIE code.

## Live bugs (fix in L0)

1. **`log_exporter` is doubly dead.** It reads the never-initialized autoload
   `GameManager` (`project.godot:32`) while the real instance is the scene child
   (`main.tscn:35-36`, used by `main_ui.gd:77`, `employee_screen.gd:17`) — AND it
   references fields that don't exist on GameState: `research_progress` (real:
   `research`), `papers_published` (`papers`), `game_seed` (`game_seed_str`) at
   `log_exporter.gd:54-58`. Consolidate GameManager (#608), fix the field names.
2. **`take_loan` is defined twice** in `execute_action` (`actions.gd:636` and `:699`) —
   the second match arm is unreachable dead code.
3. **Replay schema gap:** producer never emits the `schedule` key
   (`verification_tracker.gd:232-242`) that the verifier reads
   (`replay_simulator.gd:28`). DQ-6 is a live code gap.
4. **Doom thresholds are mutually inconsistent across four copies:**
   `doom_system.gd:360-371` says 25/50/70/90; `doom_meter.gd:125-131` and
   `game_over_screen.gd:203-212` say 30/60/80; `main_ui.gd:474-477` warns at 70/80.
   Three different answers to "what counts as critical." Canonical:
   `theme_manager.gd:365-389` (data-driven bands) — route everything through it (L6).
5. **`pass` vs `pass_turn` twin ids** — two "do nothing" code paths that are NOT
   interchangeable (`actions.gd:242/491-497/506`, `main_ui.gd:522-535/3755+`;
   `get_action_by_id("pass_turn")` returns `{}`). Collapse to one id via a constant.

## No balance-config surface exists (→ L9)

Zero gameplay tunables are centralized. `game_config.gd` holds player settings only;
every price, rate, probability, cooldown, and doom coefficient is an inline literal
across `actions.gd` (~120+ literals), `events.gd` (~30 events × effect dicts +
cooldowns 15–80 turns), `ledger.gd` (interest/fuses/magnitudes), `turn_manager.gd`
(salary `/260`, productivity, AP grant), `game_state.gd` (starting resources, risk
tables), `doom_system.gd`, `rivals.gd`, `risk_pool.gd`, `researcher.gd`,
`conferences.gd`, `game_manager.gd` (difficulty AP). Three balancing JSONs
(`data/events/balancing/*.json`) exist but are **loaded by nothing** — wire or delete.

**Fix (L9): a `Balance` autoload** (Resource/JSON-backed, mirroring the proven
`scenario_loader` pattern) so sweeps swap a file instead of editing code. Migration
order (lowest-risk first):
1. The seam: `get_months_per_turn()` (`game_state.gd:383` — hardcodes 1.0, already
   consumed by risk pools) returns a Balance value; route salary `/260`
   (`turn_manager.gd:145-149`), `TURNS_PER_WEEK` (`game_state.gd:77`), and the week→turn
   `×5` conversions (`actions.gd:1063`, `paper_submissions.gd:190`) through the L0
   Clock, which reads Balance. The whole day→month flip becomes one number + calendar.
2. Time-coupled durations as calendar-time: ledger fuses, event
   `cooldown_turns`/`min_turn`/`trigger_turn`, conference weeks — resolved to turns via
   the Clock.
3. Dedupe UI thresholds into Balance/ThemeManager (kills the desync class).
4. Lift pure balance literals in batches by file, current values as defaults
   (behavior-neutral until a sweep varies them).
5. Wire `difficulty.json` as multipliers over Balance; activate or delete
   `rarity_curves.json`/`variable_mapping.json`.

Structural (fine to hardcode): win/loss comparisons (doom≥100, rep≤0), 0–100 clamps,
enums/phases, save keys, calendar shape.

## Data masquerading as code (→ L9)

- **`events.gd`: ~1,100 of 1,483 lines are dict literals** (`get_all_events` ~830 +
  `get_risk_events` ~275). Externalization is two-thirds done already — the scheduler
  merges three sources uniformly (`events.gd:874-896`: built-ins, scenario events,
  EventService JSON pipeline). Move built-ins to `data/events/core_events.json` +
  `risk_events.json`; the remaining ~300-line engine splits cleanly into scheduler
  (L1 rewrites it) vs condition-eval + effect-applier (stable).
- **`actions.gd`: definitions (101–500) are already pure dictionaries** grouped by
  domain → `data/actions/*.json` via a loader copied from `scenario_loader.gd`.
  `_apply_risk_contributions` (846–969) is a pure `action_id → {pool: weight}` table →
  `data/actions/risk_contributions.json`.
- Blocker in both: inline `GameConfig.format_money()` in option text → template as
  placeholders resolved at display time (historical events already do this).
- Payoff: L1 operates on ~600 lines of engine instead of 2,665 of engine-plus-data.
- Effect layer (DURING, with the cost-schema rewrite): replace the 340-line
  `execute_action` match with a registry (`action_id → Callable`, per-domain handler
  modules). The scattered refund-on-failure pattern
  (`state.add_resources(action["costs"])`) is the most AP-coupled piece — new shape:
  handlers signal success/failure, one caller owns spend/refund. All
  `VerificationTracker.record_rng_outcome` calls must survive any split (determinism).

## `main_ui.gd` decomposition (→ L10; 3,786 lines, all dialogs built imperatively)

Extraction precedent exists (`research_quality_selector.gd` et al — child script
mounted in `_ready`). Follow it; do not invent a new pattern.

- **Extract BEFORE the rewrite** (turn-model-independent):
  `event_dialog.gd` (:2975–3223 — **first**, L1's response windows reuse exactly this
  presenter), `ledger_screen.gd` (:1857–1985), `employee_panel.gd` (:3304–3582 — grows
  into the L2 assignment surface), `submenu_chrome.gd` (:1088–1195).
- **Extract DURING** (content survives, AP triggers die): hiring / fundraising /
  financing / publicity / strategic / travel / operations dialogs. Travel
  (:2359–2865, paper submission + conference attendance) is the richest — real domain
  UI, feeds L3.
- **LET-DIE — do not extract or polish:** command/queue/reserve-AP/commit-plan zone
  (:397–544 — this IS the AP plan model being replaced), queued-actions viz
  (:2866–2974), `_calculate_queued_costs`, the AP-affordability half of the action-bar
  builder (:909–928).
- Layering leaks to sever during extraction: direct state writes at `main_ui.gd:535`
  (`queued_actions.append`), `:1524-1526` (hire queue + candidate pool).

## Duplication kill-list

| What | Canonical | Divergent copies | Lane |
|---|---|---|---|
| Affordability | `GameState.can_afford` + `select_action` enforcement | 8× pre-checks in main_ui + a different inline loop at `:909-920` | L10 (mostly let-die) |
| Doom bands | `theme_manager.gd` band API (`get_doom_band_index` / `get_doom_band` / `get_doom_status_label`) | ~~doom_meter, game_over_screen, doom_system, main_ui~~ **DONE (L6, #617)** — all four routed through ThemeManager; values become Balance tunables in L9 | L6 [x] |
| Money format | `GameConfig.format_money` | `game_over_screen._fmt_money`, 2 dead `format_number`, ad-hoc `"$%.0f"` | L0 |
| Severance rule | engine should own | `employee_screen.gd:36-47` (game math in a screen) | L2 |
| Resource-name match | new shared `ResourceAccessor` | `events.gd` `evaluate_condition` + `execute_event_choice` + `event_service._map_variable` | L9 |
| Staff counts | `GameState.get_total_staff` | `game_over_screen.gd:169-172` inline | L0 |

## Dead code (delete in L0)

- `game_controller.gd` (244 lines, referenced by no scene; divergent win/lose + old
  5-arg ScoreEntry) — **confirms backlog EE-1**.
- `end_game_screen.gd` + `scenes/end_game_screen.tscn` (orphaned; live path is
  `game_over_screen.gd` via `main.tscn:456`).
- Dead stub `main_ui.gd:544-547`; commented block `doom_system.gd:382+`.

## Conventions going forward (clean-as-you-go, all lanes)

- **Ids:** constants registry for action/event ids — no new bare strings (the
  pass/pass_turn split is this failure mode).
- **Logging:** ErrorHandler or a debug-gated logger; no new raw `print()`. Burn-down:
  `game_manager.gd` 44, `main_ui.gd` 108 (engine core is already clean: 0–2 each).
- **Node access:** autoload identifier or `%UniqueName`; never `../../` relative paths
  (three styles currently coexist for the same node).
- **State writes:** UI never mutates `game_manager.state` directly.
- **Typing:** typed signatures in core scripts (game_manager.gd is the laggard).

## Change log

- **2026-07-12** — Register opened from the workshop-#2 closing audit (3 parallel
  auditors). Lanes L9/L10 created to hold the balance-surface and UI-decomposition
  work; L0 scope expanded with the live bugs above.
