# Smell pass, 2026-08-23 -- starting where we first sniffed

Pip: *"let's do a smell analysis, starting where we first sniffed something, and
then flare our nostrils a bit and see what the wind and some subtle rotations of
the head and slow openings of the jaw bring us."*

Every claim below is measured. The interesting result is not the list of smells
-- it is **how many dissolved when measured**, and where the ones that survived
turned out to live.

---

## 1. The first sniff: #608, and it is STALE

> *"main.tscn instances a scene-local GameManager, while a bareword GameManager
> autoload ALSO exists and is never populated ('[GameManager] ready' prints
> twice)."*

**Measured:** no scene instances a `GameManager` node at all. `grep` across every
`.tscn` returns nothing. There is exactly one, the autoload, registered at
`res://scripts/game_manager.gd`, with 24 files referencing it.

**The duplicate is gone.** #608's specific claim no longer describes the code.
The issue has sat 42 days describing a condition that was fixed somewhere along
the way and never closed -- which is its own small finding, and the same shape
as the shadow-debt scanner's quarry.

---

## 2. Flaring the nostrils: four smells that DISSOLVED

Recorded because a dissolved smell is a real result, and because three of the
four dissolved due to **my measurement being wrong**, not the code changing.

### 2a. Three autoloads with zero inbound references

`ScreenshotManager`, `LogExporter` and `Achievements` have **zero** dotted
references anywhere in the tree. That reads as dead code.

**It is not.** All three are signal-driven:

```
screenshot_manager.gd:18   KeybindManager.screenshot_requested.connect(...)
log_exporter.gd:13         KeybindManager.log_export_requested.connect(...)
achievements.gd:84         game_manager.game_state_updated.connect(...)
```

**Zero dotted references proves nothing when the wiring is signals.** The metric
was wrong for the shape, not the code wrong for the metric.

### 2b. `office_sandbox.gd` is 2,291 lines -- and that is fine

Nearly as large as the `main_ui.gd` monolith, and never named as one. ADR-0018
declares the office **render-only**, which a 2,291-line file invites suspicion
about.

**It touches game state on exactly ONE line.** 108 functions, one point of
contact. ADR-0018 is being honoured precisely. **Size without coupling is not a
smell** -- a 2,291-line pure renderer is healthier than a 900-line file with 200
state references.

### 2c. `settings_menu.gd` at 16.8% coupling density

Alarming for a settings screen -- until the metric is split. That figure counted
`GameConfig.` (which a settings menu *should* touch -- it edits config) together
with `state.` / `game_state.` (which it should not).

**Split apart, `settings_menu.gd` is 0.7%.** The first metric was misleading and
the refinement disproved it.

### 2d. UI-to-simulation layering, overall

| file | sim-coupling density |
|---|---:|
| `employee_screen.gd` | 4.3% |
| `main_ui.gd` | 3.6% |
| `queue_gantt.gd` | 3.5% |
| `hiring_panel_controller.gd` | 1.8% |
| `settings_menu.gd` | 0.7% |

**0.7% to 4.3% across the board.** The view layer is not reaching into the
simulation. ADR-0006's purity rule is holding without needing to be enforced.

---

## 3. Rotating the head: one real, and cosmetic

`godot/scripts/` root contains exactly **two** files:

```
scripts/game_manager.gd     1,447 lines -- the central orchestrator
scripts/leaderboard.gd
```

Every other core file lives in `scripts/core/`. **The single most important file
in the codebase is the one not filed with its siblings**, and `game_manager.gd`
carries the fourth-highest coupling density in the tree (21.8%).

Harmless today. It costs a beat of hesitation every time someone looks for it,
and it is the kind of thing that quietly justifies a second orchestrator
appearing somewhere else later.

---

## 4. Opening the jaw: the real smells are in the DATA, not the code

Structural metrics cannot see the defect class that actually caused a bug this
week. `Balance.num(key, fallback)` **silently returns the fallback for a key that
does not exist** -- which is how two invented keys survived review in #1276.

So: check the balance surface in **both** directions.

### 4a. One key read but never defined -- a live silent fallback

```
doom.streams.upgrade_cat_alarm      scripts/core/upgrades.gd:143
```

```gdscript
"cat_adoption":
    state.global_alarm += Balance.num("doom.streams.upgrade_cat_alarm", 5.0)
```

**All 30 sibling keys under `doom.streams` are defined. This one is not.**

Three consequences, none loud:

1. The cat's alarm effect **cannot be tuned from data**, which is the entire
   purpose of the Balance surface.
2. Anyone reading `defaults.json` to understand the doom model would conclude
   **the cat has no mechanical effect at all.**
3. If someone "fixed" it by adding a key with a different value, the game's
   behaviour would change silently and nothing would report it.

Small, real, and the cat is not a minor object in this game -- eight cat credit
forms were formally agreed.

### 4b. Thirteen keys defined but never read -- config that lies

13 of 273 leaf keys (4.8%) are unreachable from any code path:

```
doom.legacy_capability_per_researcher      <- named "legacy" in the data file
doom.legacy_safety_per_researcher          <-
doom.researcher.alignment_base
doom.researcher.capabilities_base
doom.researcher.interpretability_base
doom.researcher.safety_base
doom.unproductive_per_staff
financing.counterparty_factors.{foundation, government, philanthropist}
financing.org_factors.{academic, independent}
hiring.onboarding.mentoring_attention
```

Two clusters worth separating:

- **A superseded doom model, still sitting in the tunable surface.** The
  `doom.legacy_*` and `doom.researcher.*_base` keys read as an older
  per-researcher doom calculation. Anyone tuning doom would reasonably assume
  they are live. **They do nothing.**
- **Counterparties and org types no instrument uses.** `foundation`,
  `government`, `philanthropist`, `academic`, `independent` are priced in the
  data and unreachable from any instrument definition. Either speculative
  scaffolding or an instrument set that shrank without the data following.

---

## 5. The finding behind the findings

**Four of five structural smells dissolved. Both surviving smells are in the
data surface.**

That is not a coincidence, and the reason is mechanical:

- **The code is guarded.** 1,471 unit tests, a simulation tier, a class-cache
  check, a scene-navigation gate, a font-size ratchet, a no-emoji gate, an
  ASCII gate, an effect-key allowlist, a ladder-impact guard, three generated
  indexes with staleness checks.
- **The balance surface is guarded in neither direction.** Nothing fails when a
  key is read but undefined. Nothing fails when a key is defined but unread.
  `Balance.num` is *designed* to swallow the first case, and the second has no
  observer at all.

The defect class this repo has spent the weekend removing -- **a mechanism that
charges you and does nothing, quietly** -- has an exact analogue in its own
configuration, and it is the one surface with no gate pointed at it.

**A `check_balance_keys.py` in the shape of the existing guards would be about
forty lines**, and it would have caught both findings above plus the two
invented keys from #1276 before they reached review. It is not built here
because the ask was a smell pass, not a fix -- but it is the obvious next move
and the cheapest guard remaining.

---

## What was NOT looked at

Stated so the absence is not read as a clean bill:

- Cyclomatic complexity and function length -- no measurement taken.
- Duplication across files -- not measured.
- Test *quality*. 1,471 tests pass; whether any of them can actually fail was
  not checked, and a test that cannot fail is the loudest smell there is.
- `main_ui.gd` internals. It is 2,324 lines and the known monolith; this pass
  measured its coupling (3.6%, low) and nothing about its cohesion.
- Anything in `godot/scenes/` beyond the `GameManager` check.
