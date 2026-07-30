# UI placeholder audit -- scene-authored fake state (2026-07-30)

Audit of every `.tscn` under `godot/` for hardcoded `text = ` values that a
viewer would read as real runtime state. Triggered by a boot failure in which a
dead UI displayed `Week 1 | Mon Jul 3, 2017 | Day 1/5`, `Turn 1`, `58.5%` and
`Phase: Not Started` -- all scene literals, no runtime data behind any of them.
The tester reasonably concluded "gameplay bug" rather than "the game never
booted", and the real cause took a separate investigation.

READ-ONLY audit. Nothing in `godot/` was modified.

## Scope and counts

- 34 `.tscn` files under `godot/` (excluding `godot/addons/`, 22 files).
- 20 of those carry at least one `text = ` property; 224 assignments total.
- 14 carry none (`cold_open_sequence`, `conference_vignette`, `fanfare_popup`,
  the three `office_floor/*`, the two `dev/*`, the four `tests/manual/*`).

| Category  | Count | Meaning                                              |
|-----------|-------|------------------------------------------------------|
| DANGEROUS |    32 | reads as real runtime state                          |
| AMBIGUOUS |     9 | judgement calls, argued individually below           |
| HARMLESS  |   183 | genuinely static chrome: captions, headings, legends |

Of the 32 DANGEROUS, **30 are overwritten** by runtime code in normal
operation (debugging traps only, live when boot fails) and **2 are not**
(section "Live bugs").

## LIVE BUGS -- fake data reaching players

### 1. `godot/scenes/ui/watch_screen.tscn:25` -- never cleared

```
[node name="MessageLog" type="RichTextLabel" parent="MessageScroll"]
text = "[color=gray]Game not started...[/color]"
```

The feed writer is APPEND-only:

- `godot/scripts/ui/main_ui.gd:1359` -- `message_log.text += "\n" + line`

No code path clears it on boot. `grep -n 'message_log.text' godot --include=*.gd`
returns exactly two writes: the `+=` above, and `main_ui.gd:1384` inside
`_render_feed()`, which does a full rebuild (`message_log.text = text`) but only
runs when the player toggles a feed filter (`_on_feed_filter_changed` /
`_on_rivals_filter_changed`).

Consequence: in a normal run the first line of the player's message log
permanently reads `Game not started...`, above every real event line, until and
unless the player happens to flip a feed filter. Visible harm is modest (it
scrolls out of view) but it is literally false state shipped to players, and it
is the same string that helped the dead UI look alive. `_render_feed()` is also
the accidental "fix" -- which is why the bug survived: anyone who touched a
filter while testing saw it disappear.

Note the generalisable rule this exposes: **`+=` does not establish runtime
ownership of a node's text.** Only an unconditional `=` on a boot path does.

### 2. `godot/scenes/main.tscn:103` -- text never assigned, node hidden instead

```
[node name="TurnCountLabel" type="Label" parent="TabManager/MainUI/TopBar"]
text = "Turn 1"
```

`main_ui.gd:1060` does `turn_count_label.visible = false` (the date badge at
`TurnLabel` supersedes it; comment at `main_ui.gd:1057` explains the merge). The
`.text` is never written anywhere. So when the UI is alive the label is hidden,
and when boot fails the label is visible reading `Turn 1`. This is a pure
debugging trap with no live-player impact -- but it is the worst-behaved kind,
because the placeholder is only ever displayed in the failure case. The correct
fix is deleting the property (or the node), not sentinel-ing it.

## DANGEROUS -- overwritten in normal operation (30)

Format: `file:line` -- scene literal -> setter that overwrites it.

### `godot/scenes/main.tscn` (top bar / instruments / phase)

| Line | Scene literal                        | Overwritten at            |
|------|--------------------------------------|---------------------------|
|   96 | `Week 1 \| Mon Jul 3, 2017 \| Day 1/5` | `main_ui.gd:1059`       |
|  115 | `Money: $0`                          | `main_ui.gd:1061`         |
|  127 | `Compute: 0`                         | `main_ui.gd:1062`         |
|  139 | `Research: 0`                        | `main_ui.gd:1063`         |
|  151 | `Papers: 0`                          | `main_ui.gd:1064`         |
|  163 | `Rep: 0`                             | `main_ui.gd:1065`         |
|  176 | `AP: 0`                              | `main_ui.gd:1113`         |
|  240 | `58.5%`                              | `main_ui.gd:1129`         |
|  393 | `[color=white]Phase: Not Started[/color]` | `main_ui.gd:1305`    |

Two aggravating details in this block:

- The placeholders do not even match the runtime FORMAT. Runtime money is
  `GameConfig.format_money(...)` with no `Money: ` prefix; compute/research are
  bare `%.1f`; reputation is `* %.0f`. So the scene literals are not stale
  copies of real output -- they are a different, invented format, which means a
  reader cannot tell "dead UI" from "old build" either.
- `AP: 0` is stale vocabulary: the AP pool was retired when the attention
  economy merged, and `main_ui.gd:1117` now describes attention hours. The
  placeholder still teaches the dead noun.
- `240` (`58.5%`) is the worst single value in the tree: a specific,
  precision-carrying, plausibly-mid-game doom reading. Nothing about `58.5`
  says "not real".

### `godot/scenes/config_confirmation.tscn` (pre-launch settings review)

| Line | Scene literal                          | Overwritten at                |
|------|----------------------------------------|-------------------------------|
|   97 | `Researcher`                           | `config_confirmation.gd:35`   |
|  114 | `AI Safety Lab`                        | `config_confirmation.gd:38`   |
|  131 | `weekly-2025-w45 (Weekly Challenge)`   | `config_confirmation.gd:43,46`|
|  148 | `Standard (Regulatory)`                | `config_confirmation.gd:51,55`|
|  165 | `$245,000`                             | `config_confirmation.gd:61`   |

This whole screen exists to tell the player what they are about to launch. Every
value is a convincing fake of exactly the thing the screen promises to report.
`weekly-2025-w45` additionally names a week from a year the game no longer
starts in. Note that `97` and `114` collide with the runtime EMPTY-value
fallbacks (`... if GameConfig.player_name != "" else "Researcher"`), so those two
are the least harmful of the five -- the placeholder equals a legitimate runtime
output. Still DANGEROUS: indistinguishability is the defect.

### `godot/scenes/leaderboard_screen.tscn`

| Line | Scene literal      | Overwritten at                 |
|------|--------------------|--------------------------------|
|  180 | `Page 1 of 1`      | `leaderboard_screen.gd:583`    |
|  195 | `Total Games: 0`   | `leaderboard_screen.gd:592`    |
|  200 | `Avg Score: 0`     | `leaderboard_screen.gd:600`    |
|  205 | `Best Score: 0`    | `leaderboard_screen.gd:604`    |

Worth calling out: this script ALREADY implements the recommended convention for
its own empty state -- `leaderboard_screen.gd:606-607` write
`Avg Score: --` / `Best Score: --`. The scene literals disagree with the
script's own house style by asserting `0`.

### Volume readouts (6)

| File                       | Lines         | Lit.  | Overwritten at             |
|----------------------------|---------------|-------|----------------------------|
| `scenes/pause_menu.tscn`   | 102, 125, 148 | `80%` | `pause_menu.gd:25,28,31`   |
| `scenes/settings_menu.tscn`| 113, 136, 159 | `80%` | `settings_menu.gd:122,125,128` |

Milder: a wrong volume readout misleads about a setting, not about game state,
and `80%` is a plausible default. Classified DANGEROUS anyway because it is a
number presented as a current value with no marking, and because these six lines
are the cheapest possible demonstration of the convention.

### `godot/scenes/ui/staff_perks_panel.tscn`

| Line | Scene literal                     | Overwritten at                    |
|------|-----------------------------------|-----------------------------------|
|  192 | `[SAFE]`                          | `staff_perks_panel.gd:89,101`     |
|  211 | `DR. ELENA VANCE`                 | `staff_perks_panel.gd:84,99`      |
|  218 | `Safety Researcher \| Skill 7/10` | `staff_perks_panel.gd:85,100`     |

A fully-realised fake employee with a name, a specialisation and a skill number.
The irony: this same scene is the best in-repo EXEMPLAR of the right convention
-- lines 105 (`???`), 111 (`""`), 164 (`---`), 253 (`""`) are all correctly
self-announcing, and the script's no-selection state writes `NO RESEARCHER`,
`[---]`, `---`, plus `Researcher.HIDDEN_PLACEHOLDER` at
`staff_perks_panel.gd:149`. Whoever authored the dossier slots understood the
rule; whoever authored the centre preview panel did not.

### `godot/scenes/ui/whats_new_modal.tscn:85`

```
text = "Version 0.11.0 - Travel & Conferences"
```

Overwritten on all three code paths (`whats_new_modal.gd:122` normal, `:170`
show-all, `:199` fallback). Shipping version is `v0.13.1`, so the literal is a
stale wrong version number -- the specific failure mode where a reader trusts a
version string and debugs the wrong build.

### `godot/scenes/pregame_setup.tscn:219`

```
text = "The default P(Doom) experience"
```

Overwritten at `pregame_setup.gd:96` from the scenario JSON. Presents itself as
a description of the currently-selected scenario.

### `godot/scenes/ui/employee_screen.tscn:86`

```
text = "[color=green][OK] No warnings[/color]"
```

Overwritten at `employee_screen.gd:166` (real warnings) or `:168` (the genuine
all-clear, `[OK] No warnings - Team running smoothly!`). DANGEROUS because the
placeholder is a positive ASSERTION about state -- green, `[OK]`, "no warnings"
-- and a dead panel therefore claims the team is fine. Compare its sibling at
line 59 (`Loading...`), which asserts nothing; that one is AMBIGUOUS-safe.

## AMBIGUOUS (9) -- and the call made on each

`main.tscn:314` -- `No actions queued...`
: HARMLESS-by-design. Text is never written; `main_ui.gd:1866,1954` only
  toggle `.visible`. The string is true exactly when the node is shown, so it
  is a static empty-state caption, not a value.

`ui/game_over_screen.tscn:58` -- `Victory Message`
: Already self-announcing -- no reader mistakes "Victory Message" for a
  victory message. Overwritten at `game_over_screen.gd:139,147`. Compliant
  with the proposed convention in spirit.

`ui/game_over_screen.tscn:69` -- `Statistics will appear here`
: Same: names itself as a slot. Overwritten at `game_over_screen.gd:240`.

`ui/bug_report_panel.tscn:166` -- `Privacy notice will appear here`
: Same. Overwritten at `bug_report_panel.gd:48`.

`ui/bug_report_panel.tscn:174` -- `Confirmation message`
: Same, plus hidden by default (`bug_report_panel.gd:56,104`).

`ui/whats_new_modal.tscn:104` -- `Loading patch notes...`
: Honest transient state; overwritten at `whats_new_modal.gd:165,194,202`.

`ui/employee_screen.tscn:59` -- `[color=gray]Loading...[/color]`
: Honest transient state; overwritten at `employee_screen.gd:136`. Asserts
  nothing about the team, unlike its sibling at line 86.

`debug_overlay.tscn:132` -- `1.0s`
: A value, so technically DANGEROUS -- but it mirrors the sibling slider's
  authored `value = 1.0` in the same file (`RateSlider`), so scene and reality
  agree at boot. Overwritten at `debug_overlay.gd:332`. Dev-only surface.
  Called AMBIGUOUS, low priority.

`welcome.tscn:155` -- `v0.13.1`
: A value, and a version number at that -- but doubly defended: overwritten at
  `welcome_screen.gd:48` from `GameConfig.CURRENT_VERSION`, AND stamped in the
  scene by `tools/sync_version.py`, whose `--check` mode gates pre-commit and
  CI. Cannot go stale silently. Leave as-is; it is the one place a
  real-looking value in a scene is correct by construction.

## HARMLESS -- not touched

The remaining 183 are static chrome: button captions (`Launch Lab`, `Back`,
`END TURN (Space)`, `Add $50k Money`), section headings (`Audio Settings`,
`STAFF DOSSIER`, `KEY RESOURCES`), column headers (`Rank`, `Player`, `Turns`),
keybind legends (`[1-9]`, `[F5]`, `[Space/Enter]`), separators (`|`), product
strings (`P(Doom)`, `You can't win. You can only buy time.`), the player-guide
prose blocks, and `placeholder_text` on `LineEdit`/`TextEdit` (which is Godot's
purpose-built, visually-distinct empty-field hint and is correct usage).

## Side finding (out of scope, worth an issue)

Player-facing non-ASCII survives in `.tscn` text, which the house ASCII rule
forbids for docs/source but which `scripts/check_no_emoji.py` only blocks for
EMOJI in `.tscn`:

- `leaderboard_screen.tscn:175,185` -- `<-`/`->` written as U+2190/U+2192
- `main.tscn:270` -- middle dot U+00B7; `main.tscn:104` tooltip em-dash U+2014
- `player_guide.tscn:124-127,154-156` -- bullets U+2022

Not a placeholder problem; flagged because a sweep of scene text is the cheap
moment to fix it.

## Recommended convention

**Rule: a node whose text is owned by runtime code MUST be authored in the scene
as one of a closed set of ASCII sentinels, never as a specimen value.**

Allowed scene-authored values for runtime-owned text:

| Sentinel | Use |
|----------|-----|
| `""` (empty) | preferred where the empty node does not collapse layout |
| `--` | a value slot (numbers, money, percentages, dates, counts) |
| `[--]` | a bracketed-chrome value slot, matching `[M]` / `[OK]` / `[!]` |
| `???` | an unknown-identity slot (names, quirks, statuses) |
| `<Label>` | a named slot where sizing needs realistic width, e.g. `<doom>` |

Why this one, over the alternatives considered:

- **Chosen: sentinel set.** It fits the existing house idiom exactly -- the repo
  already ships `???`, `---`, `[---]`, `[???]`,
  `Researcher.HIDDEN_PLACEHOLDER` in `staff_perks_panel`, and `Avg Score: --` in
  `leaderboard_screen.gd`. So this is codifying an existing internal precedent,
  not importing a foreign one. Crucially it degrades LOUDLY: a boot-failed HUD
  reading `-- | -- | Phase: --` cannot be mistaken for turn 1.
- **Rejected as sole rule: empty-by-default.** Correct in principle and it is
  the strongest signal, but Godot editor layout work genuinely needs non-empty
  text to size containers (the top bar is an `HBoxContainer` of Labels; empty
  ones collapse and the separators bunch). `--` gives a stable minimum width.
  Keep `""` as the preferred option where layout tolerates it.
- **Rejected: `PLACEHOLDER` / `TODO` words.** Too long for HUD slots, wrecks
  layout worse than a real value, and reads as a bug rather than as a slot.
- **Rejected: naming convention (e.g. suffix runtime-owned nodes
  `*_Slot`).** Renaming nodes breaks every `$Path/To/Node` and `@onready` in the
  UI layer -- a large, risky, zero-runtime-benefit refactor. And it fixes
  nothing for the human staring at the screen, which was the actual failure.
- **Additional rule worth adopting regardless of enforcement: `+=` does not
  own text.** Any node written only via `+=` (the `watch_screen` live bug) must
  be authored empty and cleared explicitly on the boot path.

## Should it be mechanically enforced? Yes, but narrowly -- and it will not
## catch the case that hurt us

Two enforcement designs were evaluated against the actual tree, in the style of
`tools/check_scene_nav.py` (pre-commit on changed files, full-tree in CI).

### Design A -- value-shape gate (cheap, measurable)

Flag `text = "..."` in `.tscn` when, after preprocessing, the value contains a
digit. Preprocessing needed to be usable:

1. only `Label` / `RichTextLabel` nodes (skip `Button`, `CheckBox`,
   `OptionButton` -- captions like `Add $50k Money` are legitimate);
2. strip `#[0-9a-fA-F]{3,8}` colour hex and `[...]` bracket spans (BBCode tags,
   keybind chrome like `[F5]`, `[1-9]`);
3. skip values over ~40 chars and any multi-line value (prose, not readouts);
4. small literal allowlist for product names containing digits (`P(Doom)1`,
   `pdoom1`) and for `welcome.tscn`'s `sync_version.py`-stamped version node.

Measured on the current tree: 38 lines contain a digit at all. Raw, that is
23 true positives against 15 false positives -- a **39% FP rate**, which is
squarely in cries-wolf territory and would get bypassed within a week. With
rules 1-4 applied the count lands at roughly **24 true positives and 1 false
positive** (`debug_overlay.tscn:36` `Debug Overlay (F3)`), i.e. **~4%**, and that
one FP is a single allowlist entry away from zero. Ongoing FP rate on incremental
runs is lower still, since only new or changed lines are scanned.

The honest limitation is RECALL, not precision. Design A catches 24 of the 32
DANGEROUS findings. It structurally CANNOT catch the non-numeric ones:
`DR. ELENA VANCE`, `AI Safety Lab`, `Researcher`, `Standard (Regulatory)`,
`[SAFE]`, `Phase: Not Started`, `[OK] No warnings`,
`The default P(Doom) experience`, and -- most importantly --
`Game not started...`, the live bug. **A digit gate would not have prevented the
incident that prompted this audit.** Anyone selling it as the fix is overselling.

### Design B -- ownership cross-reference (precise, expensive, fragile)

Parse each `.tscn` for node paths; scan `.gd` for unconditional `=` writes to
each node's `.text`; flag any node that runtime writes but whose scene text is
not a sentinel. This directly encodes the actual invariant, and treating `+=`
as non-owning makes it the only design that flags the `watch_screen` live bug.

It is also the one that will rot. The real code reaches labels through layers of
indirection -- `main_ui.gd:35` is
`@onready var numeric_doom_label = instruments.numeric_doom_label`, itself
`$CoreZone/.../NumericDoomLabel` inside `instrument_panel.gd`; `main_ui.gd:28` is
`watch_screen.message_log`. Resolving that chain is real static analysis of
GDScript, and every miss is either a false positive (node written via an alias
the checker cannot follow) or a false negative. Estimated FP rate if built
naively: 20-40%, concentrated exactly on the interesting multi-hop cases.
Estimated effort: days, not hours, and it becomes a maintenance burden of its
own.

### Recommendation

1. **Fix the live bug first** (`watch_screen.tscn:25` + an explicit clear on the
   boot path in `main_ui.gd`), and delete `main.tscn:103`'s dead `text`.
2. **Convert the 30 remaining DANGEROUS lines to sentinels.** This is the whole
   payoff and it needs no tooling.
3. **Then add Design A** as `tools/check_scene_placeholders.py`, pre-commit on
   changed `.tscn` plus a CI full-tree pass. Order matters: added before the
   cleanup it fails on 30 pre-existing lines, and a gate that is red on arrival
   gets `--no-verify`-ed and then ignored forever.
4. **Do NOT build Design B.** Its precision is worse than its concept suggests
   and its cost is days. Encode the `+=`-is-not-ownership rule in this doc and in
   review instead.
5. The gate cannot annotate exceptions inline, because **Godot rewrites `.tscn`
   on save and drops comments** -- so the `# scene-nav-allow` trick used by
   `tools/check_scene_nav.py` does not transfer. The allowlist must be an
   external checked-in file (`tools/scene_placeholder_allowlist.txt`, entries of
   the form `path/to/scene.tscn:NodePath`). That is extra friction; it is also
   the reason to keep the gate narrow enough that the allowlist stays short.

Residual risk after all of the above: the ~8 non-numeric DANGEROUS patterns are
caught by convention and review only. Rough judgement -- the digit gate prevents
maybe 60-70% of future instances of this class, and roughly 0% of the specific
"plausible prose status line" variant that cost the debugging time. Worth doing
because it is cheap, not because it closes the hole.
