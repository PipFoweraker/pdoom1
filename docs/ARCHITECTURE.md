# P(Doom)1  --  Architecture & Onboarding Map

Reference documentation for developers. This maps the game's **systems to the code that
implements them and the ADRs that decided them**, so you can orient without reading all
sixteen decision records first. It is factual, not a design manifesto  --  for the *why*
behind the design, read [`DESIGN_PHILOSOPHY.md`](game-design/DESIGN_PHILOSOPHY.md) and the
[ADR set](game-design/decisions/) (`ADR-0001` ... `ADR-0016`).

> **Two docs share this name.** This is the **developer** architecture map. The older
> **funder/partner** pitch (audience "For Funders & Partners") now lives at
> [`ARCHITECTURE_FUNDERS.md`](ARCHITECTURE_FUNDERS.md)  --  note it predates the L1 wave and
> describes the retired momentum-doom model.

> **Status of this doc:** written against `origin/main` at the L1 wave
> (month engine #636, nine-stream doom #643, cost-of-debt finance #641, calibration #638,
> honest CI #640). Where a system is a stub or half-built, this doc says so  --  see
> [section 7 Known gaps](#7-known-gaps--active-fronts).

---

## 1. What the game is

P(Doom)1 is a **turn-based AI-safety strategy game** built in **Godot 4 / pure GDScript**
(no Python runtime; the old bridge is gone). You run a frontier AI lab: hire researchers,
raise money, publish, and steer the world's **p(doom)** while a compounding-liability
economy and rival labs try to end your run. There is **no victory condition**  --  you are
scored on **turns survived**, doom-integral as tiebreak (ADR-0002). Every run is
deterministic from a seed, and the input-replay is the canonical artifact (ADR-0006).

- **Design philosophy (the "why"):** [`docs/game-design/DESIGN_PHILOSOPHY.md`](game-design/DESIGN_PHILOSOPHY.md)
- **Decision log (the "what & why-not"):** [`docs/game-design/decisions/`](game-design/decisions/) -- one ADR per decision.
  > [!] The ADR index in [`decisions/README.md`](game-design/decisions/README.md) is
  > **stale** (lists only ADR-0001 as PROPOSED). The real set is ADR-0001...0016, nearly all
  > ACCEPTED. Trust the files, not the index.

---

## 2. The core loop

ADR-0009 is the spine. Its headline  --  *"the turn is a month"*  --  is a **decision cadence**,
**not** a re-grain of the simulation. Read this carefully, because the wording confuses
newcomers (it confused the L1 build; see the PR #636 clarification in the ADR):

- **`GameState.turn` still counts workday ticks** (1 turn = 1 workday). The day is the
  **resolution tick**.
- The **month** is a *plan layer on top* of the day tick. Routine decisions live at the
  month boundary; nothing routine hangs on a single day (the "guard rule").
- This is the **"layer, not re-grain"** principle. The sim substrate, RNG stream, and
  recorded replays are untouched by the month layer.

### The four phases and who owns them

| Phase | What happens | Owning file(s) |
|---|---|---|
| **Plan** | New month opens: a fresh **Attention** grant, last month's reserve **evaporates** (no banking), strategic actions are queued with durations. | [`month_plan.gd`](../godot/scripts/core/month_plan.gd) (`MonthPlan`), opened by [`clock.gd`](../godot/scripts/core/clock.gd) month helpers |
| **Day-tick resolution** | The month plays out day by day (visible date advance). Each tick runs the sim and routes fired events by delivery tier. | [`month_controller.gd`](../godot/scripts/core/month_controller.gd) (`MonthController`) driving [`turn_manager.gd`](../godot/scripts/core/turn_manager.gd) (`TurnManager`) |
| **Response window** | A `window`-tier event **pauses playback** and demands a costed decision (HANDLE / DEFER / IGNORE). Only windows interrupt. | [`window_resolver.gd`](../godot/scripts/core/window_resolver.gd) (`WindowResolver`), classified by [`event_tiers.gd`](../godot/scripts/core/event_tiers.gd) |
| **Month review** | Boundary reached  ->  review dialog  ->  next plan phase (boundary tick held **open** as the new plan turn). | [`game_manager.gd`](../godot/scripts/game_manager.gd) `_finish_month_playback()` / `end_month()` |

**Orchestration:** [`game_manager.gd`](../godot/scripts/game_manager.gd) (`GameManager`
autoload) is the top-level driver. The **End Turn** button routes to `end_month()`  ->
`_run_month_playback()` (async day ticks)  ->  auto-pause on windows  ->  review  ->  next plan.
The pre-L1 single-day `end_turn()` still exists but only behind the **dev-mode** overlay.

**Turn step order is load-bearing.** `TurnManager.start_turn()` and `execute_turn()` are
split into named `_step_*` functions whose order defines the deterministic RNG stream that
replays re-simulate. Reordering steps invalidates every recorded replay.

---

## 3. The systems map

Each system: what it does, the files, the deciding ADR(s), and honest status.

### Turn / clock (time authority)
Single source of truth for all turn <-> calendar math (dates, weekday, month boundaries,
salary denominators). One turn = one workday; `months_per_turn()` is fixed at 1.0 until a
variable-length system lands.
**Files:** [`clock.gd`](../godot/scripts/core/clock.gd) -- **ADR:** ADR-0009 (L0 #620).
**Status:** built.

### Doom  --  nine-stream accumulating rate (the flagship)
Doom is **not a printed number that events add to**. It is an **accumulating rate computed
each day tick** from a sum of **named streams**, each fed by a world-state **intermediary**
(ADR-0015 / DQ-21). `doom_rate = sum of streams`; `doom_level += rate` each tick (may fall).
No action or event writes doom directly  --  they write intermediaries (lab frontier
capability, safety absorption, global alarm/panic, ...); the doom function reads them.
**One authority writes `state.doom`: `DoomSystem`.** Ledger bills and risk shocks arrive as
**stream inputs** (`add_stream_input`), never as parallel writes to the level.

The streams (see [`DOOM_STREAMS_v1.md`](balance/DOOM_STREAMS_v1.md) for coefficients):
`baseline` (ambient risk), `overhang` (frontier - safety absorption; the acute hazard),
`diffusion` (chronic capability floor), `compute` (inert in v1), `panic` (social
accelerant), `alarm` (small standing *relief*, natively negative), plus routed inputs
`ledger` and `technical_debt`, a gated `momentum` modifier, and dynamic `pulse:*` streams.
Legibility is the point: every stream is named so death attribution can say which one
killed you.
**Files:** [`doom_system.gd`](../godot/scripts/core/doom_system.gd) (`DoomSystem`);
intermediary state lives on `GameState` (`frontier_capability`, `safety_absorption`,
`global_alarm`, `global_panic`, `general_capability`, `ambient_risk`,
`political_pressure`, `doom_dampers`, `doom_pulses`).
**ADR:** ADR-0015 (#643), DQ-21. **Status:** **built** (engine + calibrated, 72-run sweep).
*Partial:* scheduled pulses and typed dampers are engine hooks with **no content**;
founder-action  ->  intermediary influence priced at 0; **event-data doom writes not yet
re-authored** to intermediaries (the printed-delta ban isn't 100% true in data yet).

> **Naming note:** "nine-stream" is approximate  --  DQ-21 fixed **nine intermediary
> concepts**; the `doom_sources` dict carries nine keys but not all are intermediary-fed
> (ledger/tech-debt are routed inputs; momentum is a modifier; pulses are dynamic).

### Liability Ledger (every mitigation is a loan)
A two-sided ledger (payables / receivables) of trades that pay now and bill later.
**No new player-facing currency**  --  entries read/write only existing resources (money,
reputation, governance, doom, AP). Compounding interest on unpaid payables is the
**mortality guarantee** (ADR-0002): debt grows unbounded until a bill you can't cover ends
the run  --  and the death is attributable to specific entries. A defaulted money bill
converts its shortfall to **capped** doom + reputation damage (doom residual rolls forward
so the full teeth land over months). Secret entries can be **exposed**  ->  rep/governance
damage + a blackmail rider.
**Files:** [`ledger.gd`](../godot/scripts/core/ledger.gd) (`Ledger`, `Ledger.Entry`);
billed each turn by `TurnManager._step_ledger_tick_and_bill()`.
**ADR:** ADR-0003, ADR-0013 (pricing), ADR-0008 (staff riders).
**Status:** **engine built + soak-tested**, but **not player-facing**  --  no ledger
action/UI wiring yet (blocker BL-1). Exposure fires on a per-turn chance
(`check_exposures`), not yet from rival/scheduled causes (BL-2).

### Finance / cost-of-debt engine
**One pricing function for all liabilities** (loans, funding-with-strings, equity,
philanthropy, the desperation lever). Cost is a function of org type, counterparty, **typed
reputation** (safety-rep prices grants, finance-rep prices debt), hype, and current
leverage  --  all data-driven (`financing.*`). Generates 2 - 3 concurrent **standing offers**
with expiry; accepting applies cash now and mints the ledger entry carrying the offer's
**own quoted terms**. Boundary: this engine never touches doom (that's the doom-streams
lane's job).
**Files:** [`finance_engine.gd`](../godot/scripts/core/finance_engine.gd) (`FinanceEngine`,
stateless static utility); offers stashed transiently on `GameState.financing_offers`.
**ADR:** ADR-0013 (#641). **Status:** **built** (engine + instruments). *Partial:* typed
reputation and org type aren't first-class `GameState` fields yet (falls back to scalar
rep / nonprofit); equity dilution + board seats mint **inert standing riders** (DQ-7/DQ-26).

### Effort economy / Attention
The founder currency is **Attention** (~N decisions/month; admin as painful overhead), held
on `MonthPlan`. It splits into `available` (fund strategic work), `reserved` (crisp reserve
for response windows  --  **evaporates** monthly), and `spent`. Strategic actions carry
**durations** (nothing strategic resolves instantly). There is **no global AP pool** in the
target design  --  staff get a separate per-person budget.
**Files:** [`month_plan.gd`](../godot/scripts/core/month_plan.gd) (`MonthPlan`);
plan API on `GameManager` (`queue_strategic_action`, `set_attention_reserve`).
**ADR:** ADR-0011, ADR-0009. **Status:** **Attention layer built**; the **legacy
per-turn AP pool still co-exists** (`GameState.action_points`, `select_action`)  --  L1
introduced Attention *alongside* AP; **L2 (#613) deletes AP and migrates costs**. This dual
economy is the single most confusing live edge for a new dev (see section 7). The **staff effort
economy (L2) is not built**  --  only spec inputs exist.

### SA channels (situational awareness)
"Spending buys sight": simulate everything, gate only the *view*; SA is **channels with
provenance**, not a meter; the game must **explain your death before it kills you**
(lead-time), and features are judged by **decision-flip rate**.
**Files:** provenance seams exist  --  `EventTiers.source_id_of()` stamps a named owner on feed
items; death legibility lands via `DeathAttribution`. **ADR:** ADR-0001 (amended by
ADR-0004). **Status:** **designed; largely not built as a subsystem.** No SA
purchase/screen-gating or decision-flip telemetry yet.

### Event delivery tiers
Every event is classified into a **delivery tier**  --  `ambient` (board mutates, no notice),
`feed` (readable, no acknowledgment, carries provenance), or `window` (the **only** tier
that demands a decision). Windows also carry a **class** governing legal response verbs:
`un-snoozable`, `deferrable` (DEFER mints a ledger entry), `standing` (expires, mints
nothing), `no-action`. The structural fix for the event flood (#630) is a **demand budget**
(N windows/month may demand a decision) enforced in `MonthController`, not an information
budget.
**Files:** [`event_tiers.gd`](../godot/scripts/core/event_tiers.gd),
[`window_resolver.gd`](../godot/scripts/core/window_resolver.gd),
budget in [`month_controller.gd`](../godot/scripts/core/month_controller.gd);
raw events in [`events.gd`](../godot/scripts/core/events.gd) + `data/events/*.json`.
**ADR:** ADR-0012, ADR-0009. **Status:** **classification engine built**; **event-class
content wiring is L4, outstanding** (un-annotated legacy events degrade to sane defaults).

### Adoption / reputation routing
Doom bends only where work is **adopted**: research  ->  paper  ->  socialization  ->  adoption.
Your own lab's doom is basement-fixable (private); world/rival doom bends through adoption.
Reputation is **per-person and per-org**; attention is **typed** (safety vs accel VC).
**Files:** rival capability pipeline in [`rivals.gd`](../godot/scripts/core/rivals.gd)
(feeds the `overhang` stream); papers/conferences in
[`paper_submissions.gd`](../godot/scripts/core/paper_submissions.gd),
[`conferences.gd`](../godot/scripts/core/conferences.gd).
**ADR:** ADR-0010, ADR-0014 (conferences). **Status:** **partial**  --  rival -> frontier -> doom
routing is live; typed reputation and the publish-and-socialize path are **designed, not
built** (L3, after L2). Conferences ship as attendance+yields only (DQ-16).

### Scoring / replay
Score is the tuple **(turns_survived, doom_integral)** compared lexicographically  --  flows
only, never end-state stocks. The **engine is the sole scoring authority**; boards key on
`(seed, game_version)` (+ league id). The **input-replay is the canonical run artifact**
(anti-cheat / share / bug-repro); verification is a cheap hash chain + headless
re-simulation for disputes.
**Files:** score math in [`game_state.gd`](../godot/scripts/core/game_state.gd)
(`score_tuple` / `compare_score` / `doom_integral`); replay recording in
[`verification_tracker.gd`](../godot/autoload/verification_tracker.gd);
baseline in [`baseline_simulator.gd`](../godot/scripts/core/baseline_simulator.gd),
replay in [`replay_simulator.gd`](../godot/scripts/core/replay_simulator.gd).
**ADR:** ADR-0002, ADR-0006, ADR-0016 (league). **Status:** **scoring built**; **full
input-string replay/import path not yet wired** (the one component never built in either
era  --  ADR-0006 wiring order). League pipeline (ADR-0016) is designed, not built.

### Death attribution (loss legibility)
Read-only classifier that traces a finished run's **root cause**. The ledger never owns a
death screen  --  defaults cascade into doom/rep deaths through intermediate wreckage, so the
*surface* cause hides the chain. This reads `GameState.cause_log` (a turn-stamped
contributing-cause trail) and answers "ledger vs doom vs rep?" for balance accounting.
**Files:** [`death_attribution.gd`](../godot/scripts/core/death_attribution.gd);
trail written via `GameState.note_cause()` / `Ledger._note()`.
**ADR:** ADR-0012 (EE-8). **Status:** **built** (recording-only; never changes outcomes).

### Governance & risk pools (supporting)
`governance` is a real currency the ledger bills against, but its **player-facing design is
parked** (DQ-7)  --  a stub. `political_pressure` = `global_alarm - global_panic`, a
gate-only signal (no stream). The older hidden **risk pools** (research integrity,
capability overhang) still accumulate and trigger events.
**Files:** [`risk_pool.gd`](../godot/scripts/core/risk_pool.gd); governance on `GameState`.
**ADR:** ADR-0003 (governance), DQ-20 (risk pools). **Status:** **stubs / partial.**

---

## 4. Data-driven config

Gameplay numbers live in JSON, not code, via the **`Balance` autoload** (L9 #621).

- **Surface:** [`balance.gd`](../godot/autoload/balance.gd)  --  `Balance.num("path", fallback)`,
  `Balance.inum(...)`, `Balance.table(...)`. Dotted paths into
  [`data/balance/defaults.json`](../godot/data/balance/defaults.json). An optional
  `user://balance_overrides.json` **deep-merges on top**, so sweeps/tuning swap a file
  instead of editing code.
- **Top-level keys in `defaults.json`:** `starting_resources`, `attention`, `doom`
  (incl. `doom.streams.*`), `ledger`, `financing`, `salaries`, `action_points`, `rivals`,
  `risk`, `difficulty`, `events`, `papers`.
- **Contract:** every consumer passes its inline literal as the fallback, so a missing/broken
  file *should* degrade to shipped behavior. [!] **This contract is currently violated for
  `doom.streams.*`** -- see [S7](#7-known-gaps--active-fronts).
- **Other data dirs:** `data/actions/*.json` (10 files -- action definitions),
  `data/events/*.json` (8 files across `balancing/`, `extensions/`, `overrides/`),
  `data/scenarios/*.json` (bootstrap / crisis / sandbox).

**What's tunable without code:** starting resources, doom stream coefficients, ledger
escalation rates/fuses, financing rate curves & instruments, salaries, AP grants, rival
pressure, difficulty modifiers, event budgets  --  all of it.

---

## 5. Testing & CI

### Local
- **Fresh worktree gotcha (important):** a fresh checkout has no
  `global_script_class_cache`, so GUT/headless will `quit(0)` before running anything and
  spit misleading `class_name` parse errors. **Run an import pass first:**
  `godot --headless --path godot --import`.
- **Runners:** [`godot/tests/run_all_tests.ps1`](../godot/tests/run_all_tests.ps1) /
  `run_all_tests.sh` are the *old naive* path (no import pass, no count floor). The
  **authoritative** runner is `scripts/run_godot_tests.py`, which the CI drives.

### CI tiers (#640  --  the honest gate)
Workflow `.github/workflows/godot-tests.yml`. All gating delegates to
`scripts/run_godot_tests.py`, which **ignores GUT's exit code** and instead parses the
JUnit XML, hard-failing on: no/zero tests, `tests < --min-tests` floor, any failures, or a
**manifest cross-check** (every `test_*.gd` on disk must appear as a collected suite  --  #590).

| Job | Scope | Dir | Min tests | Blocking |
|---|---|---|---|---|
| `syntax-check` | import pass + parse-error grep |  --  |  --  | yes |
| **`unit-tests`** | fast gate | `tests/unit` (~36 files) | **300** | yes |
| `integration-tests` | UI stability | `tests/integration` (1) | 10 | yes |
| `simulation-tests` | slow sim suite | `tests/unit/simulation` (6) | 80 | **non-blocking** (visible, `continue-on-error`) |
| `test-summary` | required gate |  --  |  --  | fails unless the 3 above pass |
| manual sweeps | `tests/manual/` (`test_l1_month_sweep`, `test_exploit_sweep`) | run by hand |  --  |  --  |

The min-test floors are the concrete backstop against the old **"green while running zero
tests"** hollow gate. **Note:** the earlier warning that "CI is hollow until #629" is now
**resolved**  --  #640 (which closes #629/#590) is merged on this main; CI green can be trusted
again.

---

## 6. Where to look to change X

| I want to... | Go here |
|---|---|
| Change a gameplay number (money, doom rate, loan interest, salaries) | [`data/balance/defaults.json`](../godot/data/balance/defaults.json)  --  no code change |
| Tune doom stream weights / intermediary gains | `doom.streams.*` in `defaults.json`; mechanism in [`doom_system.gd`](../godot/scripts/core/doom_system.gd); rationale in [`DOOM_STREAMS_v1.md`](balance/DOOM_STREAMS_v1.md) |
| Add / edit an event | `data/events/*.json`; classify its tier/class via fields read by [`event_tiers.gd`](../godot/scripts/core/event_tiers.gd) |
| Add / edit an action | `data/actions/*.json`; execution in [`actions.gd`](../godot/scripts/core/actions.gd) |
| Add a finance instrument | `financing.instruments` in `defaults.json`; pricing in [`finance_engine.gd`](../godot/scripts/core/finance_engine.gd) |
| Adjust how doom is computed (structure, not numbers) | [`doom_system.gd`](../godot/scripts/core/doom_system.gd) `_compute_streams` / `_advance_intermediaries` |
| Change the turn/month loop | [`month_controller.gd`](../godot/scripts/core/month_controller.gd) + [`game_manager.gd`](../godot/scripts/game_manager.gd) `end_month`/`_run_month_playback` |
| Add a ledger liability type | factories in [`ledger.gd`](../godot/scripts/core/ledger.gd) |
| Change turn step order / add a sim step | `_step_*` in [`turn_manager.gd`](../godot/scripts/core/turn_manager.gd) -- **[!] order is replay-load-bearing** |
| Register new save/load state | `to_dict`/`from_dict` in [`game_state.gd`](../godot/scripts/core/game_state.gd) -- read the SERIALIZATION CONVENTION block first |
| Change scoring | `score_tuple`/`compare_score` in [`game_state.gd`](../godot/scripts/core/game_state.gd) |
| Navigate between scenes (menu/game/leaderboard) | `SceneTransition.go_to(path)` / `.reload()` in [`scene_transition.gd`](../godot/autoload/scene_transition.gd) -- **NEVER** `get_tree().change_scene_to_file()` directly (deferred-swap chokepoint; enforced by `tools/check_scene_nav.py`). Why: [`LEADERBOARD_CRASH_DIAGNOSIS.md`](LEADERBOARD_CRASH_DIAGNOSIS.md) |
| Cut a Windows build | `python tools/build_release.py` (nukes `.godot`, stamps the build, PROVES the pack is fresh) -- never a raw `godot --export` (stale-cache trap) |
| Bump the game version | edit `version.txt`, run `python tools/sync_version.py`; `--check` gates pre-commit + CI |

---

## 7. Known gaps / active fronts

Where a new dev will hit live edges. Pulled from the ADRs, code TODOs, and
[`WORKSHOP_2_BACKLOG.md`](game-design/WORKSHOP_2_BACKLOG.md) open DQs.

**Half-built / transitional:**
- **Dual currency (AP vs Attention).** L1 added Attention beside the legacy AP pool; both
  are live. `select_action` still spends AP; windows spend Attention. **L2 (#613) deletes
  AP.** Expect confusion until then.
- **Staff effort economy (L2, #613): not built.** Only spec inputs exist (burnout debuffs,
  typed delegation DQ-24).
- **Ledger not player-facing** (BL-1). Engine + soak only; no action/UI to view or pay bills
  from the plan screen yet. Exposure not fired by rival/scheduled causes (BL-2);
  hire/departure don't create/flip riders (BL-3).
- **Event-content tail (ADR-0015).** `data/events/*.json` still carry inert/clobbered doom
  writes; per-event re-authoring to intermediaries is owed before the printed-delta ban is
  100% true in data. (`GameState` has a temporary branch handling legacy event doom.)
- **Finance stubs:** equity dilution + board seats ship as inert standing riders (DQ-7 /
  DQ-26); typed reputation & org type aren't first-class state fields yet.
- **Adoption / papers / conferences (L3): not built.** Full input-string replay/import path
  (ADR-0006) and the league pipeline (ADR-0016) are designed, not built.
- **Governance / `political_pressure`: stubs** with no player-facing design (DQ-7).
- **Doom pulses & typed dampers:** engine hooks, no content.

**Coherence-check findings surfaced while drafting (for Pip):**
1. **Balance behavior-preservation contract violated for `doom.streams.*`.** `defaults.json`
   ships `cap_frontier_gain=60.0`, `safety_absorb_gain=8.0`, `W_frontier=3.9e-05`, but the
   **code fallbacks** in `doom_system.gd` are `0.9`, `1.15`, `0.000145`  --  a **~66x divergence**
   on `cap_frontier_gain`. `Balance.gd` documents "a missing or broken file degrades to
   exactly the shipped behavior," which is **false** for these keys. If `defaults.json` ever
   fails to load, doom dynamics change wildly rather than degrading gracefully. Either the
   fallbacks should match shipped values, or the contract wording should be scoped to
   pre-L9 keys only.
2. **Stale ADR index.** [`decisions/README.md`](game-design/decisions/README.md) lists only
   ADR-0001 (as PROPOSED) though there are 16 ADRs, nearly all ACCEPTED. Regenerate it.
3. **Two docs named ARCHITECTURE.md.** This dev map replaced a funder pitch at the same path
   (preserved as `ARCHITECTURE_FUNDERS.md`); ~18 files reference `ARCHITECTURE.md`. Pip to
   confirm the split and repoint any links that specifically wanted the funder content.
4. **"The turn is a month" headline vs mechanism.** ADR-0009's headline reads as a re-grain
   but the implementation is a plan layer over day ticks  --  self-noted in the ADR after it
   was misread during the L1 build. A junior dev *will* trip on `GameState.turn` counting
   workdays.
5. **Mortality guarantee has no single ratified source.** ADR-0002 requires unbounded
   growth; ADR-0003 names compounding interest as "the candidate"; ADR-0013 replaces the
   flat-25%/turn loans. The mechanism is real (ledger compounding), but it's asserted across
   three ADRs rather than pinned in one.

**Open design questions (live, from the backlog):** typed-attention demand taxonomy
(DQ-24, feeds L2), governance player-facing design (DQ-7), desperation-lever legibility
(DQ-25, "the lever is a trap"), VC/equity depth (DQ-26), damper economy (DQ-23), rival
narrative presence (DQ-12), character-creation surface (DQ-19). See
[`WORKSHOP_2_BACKLOG.md`](game-design/WORKSHOP_2_BACKLOG.md) for the full list.
