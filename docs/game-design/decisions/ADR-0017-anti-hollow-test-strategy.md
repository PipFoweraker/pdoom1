# ADR-0017 -- Anti-hollow test strategy (load-time smoke + property-based invariants)

- **Status:** ACCEPTED
- **Date:** 2026-07-17
- **Session:** test-strategy-uplift (feat/test-strategy-uplift)

## Context

Two real failures on 2026-07-17 share one root cause -- **tests that pass without
exercising the thing they claim to protect** (call it a "hollow" test):

1. **Hollow CI (fixed as #640).** The gate reported GREEN while running ZERO tests:
   a cold Godot class cache made GUT `quit(0)` before parsing a single test. Nobody
   noticed for a while. The suite's *pass* was uncorrelated with the code's health.

2. **The parse-error-that-broke-the-game** (fixed on `feat/hiring-phase-b-pipeline`,
   commit a2de3a7). A one-line GDScript parse error in `scripts/ui/main_ui.gd` made
   the ENTIRE script fail to load, so the game would not start -- yet **436 unit
   tests passed**, because the fast unit suite exercises core / GameManager logic and
   **never loads the UI script**. The thing that broke (script load) was never
   touched by any test, so no test could fail.

Back in January, Pip's housemate (an ML expert) gave three pieces of advice that
today vindicates:
- (a) some unit tests should be **property-based** (assert an invariant over a
  distribution of inputs, not one hand-picked case);
- (b) **write the tests before the code**;
- (c) **"let me see some of them fail."** A test you have never watched fail is
  untrustworthy -- you cannot distinguish it from a hollow one.

This ADR credits that advice and turns it into standing practice.

### What the pre-uplift suite can and cannot catch

CAN catch (well-covered):
- Core engine logic: resource math, turn loop, events, finance, ledger, doom.
- Engine determinism and replay soundness (ADR-0006): `tests/unit/simulation`
  re-simulates recorded input logs and checks the (turns, doom_integral, hash)
  reproduce. This tier is genuinely strong.
- Save/load snapshot fidelity for one hand-built mid-game state.

CANNOT catch (the gaps this ADR closes):
- **Load-time breakage of any script no test imports.** The whole `scripts/ui`
  surface (main_ui.gd, panels, screens) is loaded only when a *scene* is
  instantiated. The fast unit tests never instantiate scenes, so a parse error there
  is invisible. `run_godot_tests.py`'s `--quit` syntax check boots only the main
  menu scene (`welcome.tscn`); the import pass builds the class cache but its exit is
  only checked for cache *existence*, not per-script parse success. So a parse error
  off the welcome-boot path passes the entire gate.
- **Whole-space invariants.** Single-seed tests can pass while a different region of
  the seed space boots into an unplayable / game-over / NaN state.

### Where hollow tests can still hide

- Any assertion against a value the test itself constructs but the *product* never
  loads (the main_ui.gd class of bug).
- Tests with no floor on how much they exercised -- e.g. a directory-walking test
  that silently finds zero files still "passes." (Guarded here with `MIN_*` floors.)

## Decision

Adopt three standing practices, and add the tests that embody them:

1. **A "nothing is hollow at load time" smoke test** in the fast gate
   (`tests/unit/test_smoke_load_all.gd`). It `load()`s every project `.gd` under
   `scripts/` and `autoload/`, instantiates every `.tscn` under `scenes/`, asserts
   every declared autoload singleton is present, and instantiates the `main.tscn`
   chain specifically. A parse/load error turns the gate RED and names the file.
   This is the direct guard against failure #2. It is cheap (scripts are already
   imported; `instantiate()` does not enter the SceneTree, so `_ready()` side effects
   stay dormant), so it stays in the required fast gate.

2. **Property-based invariant tests** that assert over a *deterministically-generated
   distribution* of seeds, not one case:
   - `tests/unit/test_property_boot_invariants.gd` (fast): for any seed (64 generated
     + 8 awkward edge seeds), a fresh `GameState` boots to an ACTIONABLE state --
     alive, finite/sane resources, at least one affordable action.
   - `tests/unit/simulation/test_property_determinism.gd` (slow tier): over a seed
     distribution, (i) the engine is byte-identical across two runs of the same seed,
     (ii) a recorded replay reproduces the run's hash+score (ADR-0006, READ not
     weakened), (iii) save/load round-trips to a deep-equal state.

3. **Red-first discipline (write-the-test-before-the-code, item b + c).** Every new
   invariant test in this ADR was watched FAIL with its target bug present before
   being accepted -- see the counterfactual table. New behavioural tests should
   likewise be demonstrated to fail against the unfixed code, at least once, in the
   PR that introduces them.

### Counterfactual: which practice would have caught today's failures

| Failure | Caught by | How |
|---|---|---|
| #1 hollow CI (zero tests ran) | already fixed in #640 (JUnit floor + manifest); this ADR's `MIN_*` floors extend the same "silence is failure" principle into individual tests | a suite that runs nothing now fails; a walk that finds nothing now fails |
| #2 main_ui.gd parse error | smoke test `test_all_scripts_compile` | `load("res://scripts/ui/main_ui.gd")` returns null on parse error -> RED, naming the file |

Demonstrated (red-first proof, all reverted after observation):

| New test | Bug reintroduced | Result |
|---|---|---|
| `test_all_scripts_compile` | one-line parse error appended to `main_ui.gd` | RED. Critically, **419/420 other fast-gate tests still PASSED** -- reproducing "the game will not start yet the suite is green." Only the direct script-`load()` check caught it; scene-instantiation did NOT (a scene loads with a null script attached), which is why the smoke test loads every `.gd` directly rather than relying on instantiation. |
| boot-invariant sweep | `money = 0.0` in `GameState.reset()` | RED across the ENTIRE seed distribution ("positive money" failed for every sampled seed). |
| determinism property | `state.money += Time.get_ticks_usec() % 13` in `TurnManager.execute_turn()` | RED (byte-different final states between two runs of the same seed). |
| save/load property | drop `money` on restore (`restore_state`) | RED (round-trip deep-equal fails for the sampled seeds). |

## Beacons served / violated

- **Rams 6 (honest):** a green gate now means the boot surface actually loads --
  the signal stops lying, extending #640's honesty from "tests ran" to "the product
  loads."
- **Rams 10 (as little design as possible):** no new framework; reuses GUT, the
  existing determinism/replay infra, and the existing two-tier runner.
- Cost: a few seconds added to the fast gate (whole-tree load) and ~1-2 min to the
  already-slow, non-blocking simulation tier. Judged worth it against a class of bug
  that ships an unstartable game past a green gate.

## Interaction contract

- **Reads:** every `scripts/**.gd`, `autoload/**.gd`, `scenes/**.tscn`; the
  `[autoload]` list in `project.godot`; `BaselineSimulator`, `VerificationTracker`,
  `ReplaySimulator`, `SaveLoad`, `GameState`, `TurnManager`.
- **Writes:** nothing in the engine. Adds test files only; determinism/replay
  (ADR-0006) is READ and verified, never modified. (>=2 systems touched: satisfied.)

## Rejected alternatives

- **Rely on the runner's `--quit` syntax check / import pass.** Rejected: `--quit`
  boots only `welcome.tscn`; the import pass is checked for cache existence, not
  per-script parse success. Both were green while main_ui.gd was broken.
- **Instantiate scenes only (skip direct script loads).** Rejected empirically: a
  scene whose attached script fails to parse still instantiates (with a null script),
  so `main.tscn.instantiate()` did NOT go red on the injected parse error. Loading
  every `.gd` directly is the reliable catch; scene instantiation is a complementary
  bonus for structural breakage.
- **A separate full headless game boot as the smoke test.** Rejected as too slow /
  side-effecting (timers, audio, threads) for the required fast gate; the load +
  instantiate sweep gets the same parse-error coverage cheaply.
- **Put the property tests only in the fast gate.** Rejected: the determinism/replay
  properties run full games; they belong in the non-blocking simulation tier. Only
  the cheap boot-invariant property (construction only) is in the fast gate.

## Consequences / open questions

- The fast gate now fails if ANY project script fails to compile, even one no other
  test uses. This is the point.
- `MIN_SCRIPTS` / `MIN_SCENES` floors in the smoke test will need bumping as the tree
  grows; they are deliberately loose (guard against a hollow walk, not a tight
  census).
- Open: extend property coverage to save/load of adversarial mid-game states
  (currently a short deterministic horizon); consider a headless "play N turns via
  the real GameManager signal path" integration smoke to cover UI-to-engine wiring,
  which the load-time smoke does not exercise.
