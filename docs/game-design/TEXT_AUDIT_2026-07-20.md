# Player-facing text audit -- 2026-07-20

Scope: player-visible strings across `godot/scenes/**/*.tscn`, `godot/scripts/**/*.gd`,
and `godot/data/**/*.json`. Two categories: (1) TRAPS (confusing/wrong/placeholder/
dev-facing copy shown to players) and (2) HARDCODED-SHOULD-BE-VARIABLE (magic values
baked into display strings that can drift from the real source of truth).

Method note: many `.tscn` `text = "..."` values are **editor placeholders overwritten at
runtime** in `_ready()`/update loops (verified per file). Those are NOT traps -- a player
never sees them past the first frame.

Status legend: APPLIED = fixed in PR #715. All findings were triaged with Pip; his rulings
(2026-07-20) are folded in below.

---

## Category 1 -- TRAPS

### T1. Papers tooltip promised doom reduction that no longer happens  [APPLIED]
- `godot/scenes/main.tscn` Papers `tooltip_text` was
  `"Publications boost reputation (+5 each) and reduce doom (-3 each)."`
- The `+5 reputation each` half is correct (`turn_manager._step_publish_papers`). The
  `reduce doom (-3 each)` half was stale: `actions.gd:341` documents that paper doom
  reduction is now a stream "priced at 0 in v1" -- publishing currently reduces doom by 0.
- Pip's ruling: "say that publications boost reputation and may have further downstream
  impacts as their findings are adopted."
- Fix: tooltip is now built at runtime (`main_ui._apply_balance_tooltips`) as
  `"Publications boost reputation (+N each) and may have further downstream impact as their
  findings are adopted."` (N from Balance; see H2). The static scene text was updated to
  match so no stale "-3 doom" survives anywhere.

### T2. "Hire SR" dev/test button in the live control bar  [APPLIED -- removed]
- `main.tscn` node `TestActionButton` (`text = "Hire SR"`), a dev shortcut that at runtime
  hired a safety researcher directly (`main_ui._on_test_action_button_pressed`), bypassing
  the normal action flow.
- Pip's ruling: "Remove." Removed the node, its `pressed` connection, the `@onready` ref,
  the handler, and its enable/disable sites. Also simplified the now-dead
  `child.name != "TestActionButton"` guard in `_on_actions_available`.

### T3. "Init" control button -- vestigial  [APPLIED -- removed]
- `main.tscn` node `InitButton` (`text = "Init"`).
- Investigated per Pip: introduced in "Phase 4 MVP - Minimal functional UI" (commit
  c32dfd9) as the original start-the-game button. The game now **auto-boots** -- `_ready`
  calls the boot logic directly (`main_ui.gd:240`), and the button was auto-pressed then
  immediately disabled, so it did nothing a player could use. The `KEY_ESCAPE`-to-init path
  was guarded on `not init_button.disabled` (never true post-boot) -- dead code.
- Pip's ruling: "remove it unless you find otherwise warranted." Nothing warranted keeping
  it. Removed the node + connection + `@onready` ref + the dead ESC branch; renamed the
  handler `_on_init_button_pressed` -> `_boot_game` (kept -- it IS the boot logic, called
  from `_ready`). Stale comments in `test_game_start_actionable.gd` updated.

### T4. ">> INITIALIZE LAB" launch button -- off-theme  [APPLIED]
- `pregame_setup.tscn:285` and `config_confirmation.tscn:241` both read
  `text = ">> INITIALIZE LAB"` (all-caps + `>>` chevron, matches the earlier
  "INITIALISE LAB" flag).
- Pip's ruling: "Shift to launch lab for consistence." Both now read `"Launch Lab"`,
  matching `welcome.tscn:131`.

### T5. "What's New" fallback pointed players at a repo file  [APPLIED + ticket]
- `whats_new_modal.gd:202` fallback: "...Check the CHANGELOG.md file for the latest
  updates." `CHANGELOG.md` is a source-repo artifact players don't have in a packaged build.
- Pip's ruling: "Remove the reference to changelog. See if there is a better changelog on
  the pdoom-website. If not, put a ticket on that repo to make one."
- Checked: `pdoom1-website` has no player-facing changelog (only an archived
  `docs/archive/DASHBOARD_INTEGRATION_CHANGELOG.md`). Fallback now reads "Visit pdoom1.com
  for the latest updates." and filed **pdoom1-website#141** to create a real changelog page.

### T6. `send_delegation` "[Coming Soon]" description  [NOTE -- intentional, no action]
- `data/actions/travel.json:26`, carries `"is_stub": true`. Honest teaser for an unbuilt
  action, not a broken placeholder. Left as-is.

### Minor / observations (no fix)
- `main.tscn` ExplanationLabel "Buy time ... | Lose: P(Doom) = 100%" vs the tooltip's
  "league baseline" framing -- two framings of the loss condition on one widget. Design copy.
- `main.tscn` DateLabel static `"Week 1 | Mon Jul 3, 2017 | Day 1/5"` is stale vs the current
  `_format_turn_datetime` format but is overwritten every frame; editor-only.

---

## Category 2 -- HARDCODED-SHOULD-BE-VARIABLE

### H1. Starting-funding display hardcoded  [APPLIED]
- `config_confirmation.gd:52` was `GameConfig.format_money(245000)` (stale comment pointing
  at the wrong line). Now reads `Balance.num("starting_resources.money", 245000.0)` --
  the value `game_state.gd:217` actually boots with (`data/balance/defaults.json`).

### H2. Balance numbers baked into resource tooltips  [APPLIED]
- `main.tscn` tooltips hardcoded balance constants (compute-per-researcher, research-per-
  paper, reputation-per-paper, AP base + per-staff). `.tscn` tooltips can't call `Balance`,
  so these were drift-prone literals.
- Pip's ruling: "Change to balance literals, please." Done as a **single-source** wiring so
  the tooltip and the mechanic read the same keys:
  - Added Balance keys: `papers.research_per_paper` (100), `papers.reputation_per_paper` (5),
    `compute.per_researcher_per_turn` (1). (`action_points.per_staff` = 0.5 already existed.)
  - `turn_manager.gd` now reads those keys in `_step_publish_papers` and
    `_step_researcher_productivity` (defaults identical -> behaviour unchanged; verified by
    the simulation/determinism tier).
  - `main_ui._apply_balance_tooltips()` (called from `_ready`) builds the Compute / Research
    / Papers tooltips from the same `Balance.num(...)` values; the AP tooltip is rebuilt
    per-turn from `state.max_action_points` + `action_points.per_staff` (base is
    difficulty-dependent). Tooltips can no longer drift from the mechanic.

### H3. Version/date/seed statics in scenes  [NOTE -- managed or overwritten]
- `welcome.tscn "v0.11.0"` is stamped by `tools/sync_version.py` AND overwritten at runtime
  from `GameConfig.CURRENT_VERSION`. `whats_new_modal.tscn` / `config_confirmation.tscn`
  version/seed/funding statics are editor placeholders overwritten at runtime. Not
  player-visible; no drift risk.

---

## Summary (final)
- Traps found: 6 (T1-T6). Fixed: 5 (T1-T5, all per Pip's rulings); T6 is intentional.
- Hardcoded-should-be-variable: 3 groups (H1-H3). Fixed: 2 (H1 + H2 via new single-source
  Balance keys). H3 already managed/overwritten.
- Cross-repo follow-up: pdoom1-website#141 (create a player-facing changelog page).
- Behaviour: all mechanic changes are value-preserving (new Balance defaults == the old
  literals); fast gate (510 tests, 0 fail) + simulation tier (96 tests, 0 fail) green.
