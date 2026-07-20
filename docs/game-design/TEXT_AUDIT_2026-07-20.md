# Player-facing text audit -- 2026-07-20

Scope: player-visible strings across `godot/scenes/**/*.tscn`, `godot/scripts/**/*.gd`,
and `godot/data/**/*.json`. Two categories: (1) TRAPS (confusing/wrong/placeholder/
dev-facing copy shown to players) and (2) HARDCODED-SHOULD-BE-VARIABLE (magic values
baked into display strings that can drift from the real source of truth).

Method note: many `.tscn` `text = "..."` values are **editor placeholders overwritten at
runtime** in `_ready()`/update loops (verified per file). Those are NOT traps -- a player
never sees them past the first frame. They are called out only where the static value is
stale AND could flash, or where no runtime overwrite exists.

Ranked by player-confusion risk (highest first). Status: APPLIED = fixed in this PR,
FLAG = left for Pip (wording/design/behavioural judgment).

---

## Category 1 -- TRAPS

### T1. Papers tooltip promises doom reduction that no longer happens  [FLAG -- highest risk]
- `godot/scenes/main.tscn:128`
  `tooltip_text = "Publications boost reputation (+5 each) and reduce doom (-3 each)."`
- Half stale. The `+5 reputation each` half is CORRECT (`turn_manager.gd:487`,
  `_step_publish_papers`: `research >= 100 -> +1 paper, +5 reputation`). But the
  `reduce doom (-3 each)` half is WRONG: `actions.gd:341` documents the migration --
  "instead of a printed -3 doom ... Priced at 0 in v1 (a follow-up prices it)." Under the
  ADR-0015 stream model, publishing a paper currently reduces doom by **0**, not 3.
- Why it matters: the tooltip actively teaches a mechanic that does not exist; a player
  optimising "publish to cut doom" is being misled. Highest confusion risk of the set.
- Proposed fix: drop the `reduce doom (-3 each)` clause, or reword to reflect that papers
  feed a doom stream currently priced at 0. Needs Pip's design call on what papers should
  *say* they do (hence FLAG, not auto-edited -- I won't invent the number/voice).

### T2. "Hire SR" dev/test button in the live control bar  [FLAG]
- `godot/scenes/main.tscn:338` node `TestActionButton`, `text = "Hire SR"` (disabled in
  scene, ENABLED at runtime `main_ui.gd:837` once `turn >= 0`).
- `main_ui.gd:550` `_on_test_action_button_pressed()` -> directly
  `select_action("hire_safety_researcher")`, bypassing the normal action flow.
- The node name `TestActionButton` and the terse "Hire SR" label read as a developer test
  shortcut that leaked into the shipped UI. A player sees an unexplained "Hire SR" button
  sitting next to Undo/Clear/End Turn.
- Proposed fix: either remove the button (behavioural change) or relabel + document it as a
  real quick-action. Behavioural/design judgment -> FLAG.

### T3. "Init" control button -- ambiguous, dev-flavoured  [FLAG]
- `godot/scenes/main.tscn:332` node `InitButton`, `text = "Init"`.
- Pressed automatically on load (`main_ui.gd:240`) then disabled (`:838`), so a player
  mostly sees a greyed "Init". "Init" is dev shorthand; if it ever shows enabled (load
  path, `_on_init_button_pressed`) the label tells the player nothing. Cf. the earlier
  "INITIALISE LAB" off-theme flag.
- Proposed fix: relabel to something player-legible ("Start" / "Begin Run") or hide it.
  Wording call -> FLAG.

### T4. ">> INITIALIZE LAB" launch button -- off-theme / kerning  [FLAG]
- `godot/scenes/pregame_setup.tscn:285` and `godot/scenes/config_confirmation.tscn:241`
  `text = ">> INITIALIZE LAB"`.
- Matches the previously-flagged "INITIALISE LAB" trap (off-theme all-caps + `>>` ASCII
  chevron, awkward kerning). Two copies, so any reword must hit both.
- Proposed fix: settle a single launch verb ("Launch Lab" is already used on
  `welcome.tscn:131`) and reuse it for consistency. Voice call -> FLAG.

### T5. "What's New" fallback points players at a repo file  [FLAG -- low]
- `godot/scripts/ui/whats_new_modal.gd:202`
  `"...Check the CHANGELOG.md file for the latest updates."`
- Only shown when no patch-notes entry exists for the current version. `CHANGELOG.md` is a
  source-repo artifact players don't have in a packaged build; dev-facing wording leaking
  to players.
- Proposed fix: point at the in-game "What's New" / a website URL instead of a filename.
  Wording call -> FLAG.

### T6. `send_delegation` "[Coming Soon]" description  [NOTE -- intentional, no action]
- `godot/data/actions/travel.json:26` `"description": "[Coming Soon] Send researchers..."`,
  carries `"is_stub": true`. This is an honest teaser for an unbuilt action, not a broken
  placeholder. Left as-is; listed for completeness.

### Minor / observations (no fix proposed)
- `main.tscn:245` ExplanationLabel "Buy time ... | Lose: P(Doom) = 100%" vs the tooltip at
  `:249` introducing a "league baseline" win/lose condition -- two slightly different
  framings of the loss condition layered on the same widget. Design copy; note only.
- `main.tscn:153` AP tooltip "Base 3 + 0.5 per staff": the `0.5 per staff` is exact
  (`turn_manager.gd:83`) but "Base 3" is only true on Standard (Easy=4, Hard=2 per
  `balance/defaults.json:122-124`). Correct on the default difficulty; minor imprecision.
- `main.tscn:72` DateLabel static `"Week 1 | Mon Jul 3, 2017 | Day 1/5"` is stale relative
  to the current `_format_turn_datetime` format ("Turn N - Fri 21 Jul 2017") but is
  overwritten every frame (`main_ui.gd:744`); editor-only, no player impact.

---

## Category 2 -- HARDCODED-SHOULD-BE-VARIABLE

### H1. Starting-funding display hardcoded  [APPLIED]
- `godot/scripts/ui/config_confirmation.gd:52` (before):
  `funding_label.text = GameConfig.format_money(245000)  # from game_state.gd:5`
- The `245000` duplicated the real starting balance, which is data-driven via
  `Balance.num("starting_resources.money", 245000.0)` (`game_state.gd:217`;
  `data/balance/defaults.json:95`). If the balance is retuned, the confirmation screen would
  silently show the wrong starting funds. (The stale comment even pointed at the wrong line.)
- Fix APPLIED: now reads `Balance.num("starting_resources.money", 245000.0)`, the same value
  the game actually boots with.

### H2. Balance numbers baked into resource tooltips  [FLAG]
- `godot/scenes/main.tscn` tooltips hardcode balance constants:
  - `:104` "Each researcher uses 1 per turn" -- CORRECT today (`turn_manager.gd:165`, flat 1
    compute/researcher) but a literal that will drift if that flat rate is tuned.
  - `:116` "100 research = 1 auto-published paper" -- CORRECT today
    (`turn_manager.gd:481`) but the `100` threshold is a hardcoded literal.
  - `:128` "+5 each ... -3 each" -- see T1 (the -3 is already wrong).
  - `:153` "Base 3 + 0.5 per staff" -- difficulty-dependent base (see minor note).
- These are display literals with no live binding to `Balance`. `.tscn` tooltips can't call
  `Balance.num(...)`, so making them data-driven means moving tooltip assignment into
  `main_ui.gd` -- new plumbing, not a safe in-place swap. FLAG for a decision on whether the
  economy tooltips should be generated from balance data.

### H3. Version/date/seed statics in scenes  [NOTE -- managed or overwritten]
- `welcome.tscn:265 "v0.11.0"` -- managed by `tools/sync_version.py` (stamps `welcome.tscn`)
  AND overwritten at runtime from `GameConfig.CURRENT_VERSION` (`welcome_screen.gd:35`). Not
  a drift risk.
- `whats_new_modal.tscn:85 "Version 0.11.0 - Travel & Conferences"`,
  `config_confirmation.tscn:{177 seed, 211 $245,000}` -- all editor placeholders overwritten
  at runtime (`whats_new_modal.gd:122`, `config_confirmation.gd:36/52`). Not player-visible.
  Listed so a future editor doesn't mistake them for live copy.

---

## Summary
- Traps found: 6 (T1-T6); traps fixed: 0 (all require a wording/design/behavioural call;
  each flagged with a concrete recommendation).
- Hardcoded-should-be-variable found: 3 groups (H1-H3); fixed: 1 (H1, safe swap to the
  existing `Balance` source of truth). H2 needs new plumbing; H3 is already managed/overwritten.
- Highest player-confusion risk: **T1** (Papers tooltip claims a doom reduction the current
  code prices at 0), then **T2** (a "Hire SR" dev button live in the control bar).
