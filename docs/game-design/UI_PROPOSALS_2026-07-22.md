# PLAN / WATCH UI -- drift analysis + ranked enhancement proposals (2026-07-22)

> Deliverable for Pip's 2026-07-22 review of the built PLAN and WATCH screens.
> Compares the shipped UI against the original wireframes / design intent, ranks
> simple enhancements by effort, and assesses an in-game A/B layout switch for
> iteration. Read-mostly analysis; no code changed by this doc.

## Sources read (intent side)

- `docs/game-design/BUILD_BRIEF_PLAN_WATCH_UI.md` -- the *what to build* for both screens.
- `docs/game-design/WORKSHOP_2_BACKLOG.md` (Plan/Watch workshop beats 1-4, lines ~639-740).
- `docs/game-design/UI_PASS_NOTES_2026-07-20.md` -- Pip's own playthrough notes, incl. the
  `ABBBCCC` submenu sketch and the "buttons centre-aligned not left-bound" complaint.
- `docs/game-design/UI_MENU_CONSISTENCY_2026-07-20.md`, `docs/game-design/UI_ESCAPE_CONTRACT.md`,
  `docs/ui/UI_LAYOUT_GUIDE.md`, `godot/docs/design/UI_DECISIONS.md` + `UI_BACKLOG.md`.

## Sources read (built side)

- `godot/scenes/main.tscn` -- the real container tree. ContentArea is one shared HBox of three
  columns: `PlanScreen` (0.3) | `InstrumentColumn` (0.3) | `WatchScreen` (0.4).
- `godot/scenes/ui/plan_screen.tscn` + `plan_screen.gd` -- left column only (hint, actions
  scroll, upgrades scroll, command zone, reserve gauge built in code).
- `godot/scenes/ui/watch_screen.tscn` + `watch_screen.gd` -- right column (feed + filters).
- `godot/scripts/ui/instrument_panel.gd` (shared centre column: cat + doom + roster + queue strip).
- `godot/scripts/ui/screen_mode.gd` -- the mode controller (visibility-toggle, no reparent).
- `godot/scripts/ui/main_ui.gd` (3747 lines) -- `_populate_actions` icon loop (~1138-1280),
  `_populate_upgrades` (~1282).
- `godot/scripts/ui/doom_meter.gd` -- draws its own `%d%%` label (lines 64-75).
- `godot/scripts/ui/office_floor/office_floor.gd` -- the pure-view floor (min size 360x260).
- Branch `fable/office-floor-integration` -- mounts the floor under the WATCH feed
  (`watch_screen.gd`, floor sized `Vector2(0, 180)`, `SIZE_EXPAND_FILL` horizontal). This is
  where the WATCH office-floor in the screenshot comes from; it is NOT on `main` yet.

---

## 1. Drift table -- wireframe intent vs what got built

Verdict legend: **MATCH** (built as intended) / **PARTIAL** (seed present, not finished) /
**MISSING** (intent not built) / **DRIFT** (built differently than intent) / **BUG** (defect).

| # | Element | Wireframe intent (source) | Built now | Verdict |
|---|---------|---------------------------|-----------|---------|
| D1 | PLAN header attention budget | Depleting pips: allocated (filled) vs reserved (hollow) (BRIEF elem 1; ADR-0011) | `plan_screen.gd` `_build_reserve_gauge` renders exactly this pip strip | MATCH |
| D2 | **The committed queue / "month ahead"** | Each committed play shows a **gantt-style duration bar + ETA** ("lands ~M18"); list is **reorderable**; **queue order = execution priority** (BRIEF elem 2 + mechanic) | `InstrumentColumn/QueuePanel` is a thin HBox with a "No actions queued..." hint. No duration bars, no ETA, no reorder handle, no priority numbering | **MISSING** (headline drift) |
| D3 | The hand = action cards | **Card register along the BOTTOM**; baseline + situational cards; show MORE than 20 AP can play; greyed = unaffordable; each shows AP cost (BRIEF elem 4) | A **left-column vertical scroll of 70x70 icon tiles** (old RTS register). Affordability dimming present; cost-on-face and "more than you can play" honesty absent | DRIFT |
| D4 | Action grouping | Pip's `ABBBCCC` sketch: category icon (A) -> submenu of options (B) -> context window (C) on hover (UI_PASS_NOTES). Submenus expand from the clicked button (UI_DECISIONS #510) | Flat single `icon_stack` VBox, all categories concatenated, no grouping/headers. Submenus exist for hire/fundraise/publicity/travel only | PARTIAL |
| D5 | Icon column alignment/packing | Left-bound, tidy (UI_PASS_NOTES: "centre-aligned... rather than being left-bound") | Icons are `SIZE_SHRINK_CENTER` inside a ~0.3-width column -> floats centred with wide side margins; packs to top leaving dead space below | BUG/DRIFT |
| D6 | Upgrades list home | Not assigned a home in the two-screen model. Old `UI_LAYOUT_GUIDE` put upgrades in the RIGHT panel | Moved to the **bottom of the left PLAN column**, unframed, below the action hand + hiring buttons -> reads as "floating/orphaned" (matches screenshot) | DRIFT |
| D7 | Hiring buttons in the list | Pip: get rid of them (handled inside hiring) OR fold into the `ABBBCCC` submenu expansion (UI_PASS_NOTES) | Still present as standalone list rows, lengthening the vertical slice | DRIFT |
| D8 | Team panel (small, early) | Founder row + a few hires with assignment tags; collapsible seed for the Entity swimlane (BRIEF elem 5) | `EmployeeRosterZone` roster list present (centre column) | MATCH (seed) |
| D9 | Doom two-instrument display | **Rate** = live sparkline (wiggles) + **level** = grinding bar + names its own driver (BRIEF WATCH elem 3) | DoomMeter arc + sparkline present; "Doom this turn: Baseline +0.1" driver line present | MATCH |
| D10 | Doom percentage readout | One canonical percentage | **Two** percentages rendered: `NumericDoomLabel` ("27.2%", main.tscn) directly above DoomMeter, which *also* draws "%d%%" ("27%") at its own centre (`doom_meter.gd:64-75`) -> the collision in the screenshot | **BUG** |
| D11 | Cat / office scene placement | Ambient office + cat is a **WATCH** thing (beat 3: operator swivels to the floor in WATCH; PLAN stays abstract/board) | Cat sits in the shared `InstrumentColumn`, so it dominates the **PLAN** centre too, oversized | DRIFT |
| D12 | WATCH office floor | The employee-sprite fishbowl, centre-right, sprite state = readout of mechanical state (BRIEF WATCH elem 6) | Built well as a pure-view component; on `fable/office-floor-integration` it mounts **under** the feed in the 0.4 column at `Vector2(0,180)` -> squeezed "wide short strip", sprites tiny | PARTIAL (scale/space) |
| D13 | WATCH playback controls | Play/pause + speed + reserve remaining (BRIEF WATCH elem 1) | `screen_mode.build_watch_bar`: speed dial REAL, play/pause a disabled STUB, reserve readout present | PARTIAL (by design) |
| D14 | "WATCH -- tactics..." banner | Pip: don't permanently tell players the screen's purpose; fade it after first play (UI_PASS_NOTES) | Banner text is permanent in `screen_mode._refresh_banner` | DRIFT |
| D15 | Zone legibility during dev | Pip: left/right backgrounds should be **different colours** so borders are visible while building (UI_PASS_NOTES) | All three columns share the same ground; no per-zone tint | MISSING (dev aid) |
| D16 | Info/context strip colour | Pip: give the bottom hover-context window **its own colour** to zone the play area; stop it jumping on hover (UI_PASS_NOTES) | Single InfoBar, fixed 60px (anti-flicker) but same palette; jump reported when cost text widens | PARTIAL |

---

## 2. The lower-right "gantt / operations underway" verdict (asked specifically)

**Verdict: the gantt / committed-queue tracker was specified in the wireframes but was NOT
built. It is the single largest drift on the PLAN screen (row D2).**

What the brief called for, twice:
- PLAN elem 2 -- *"The committed queue ('The month ahead'): the plays you've committed, each
  with a gantt-style duration bar + ETA ('lands ~M18') -- the fishing-line made visual. Queue
  ORDER = execution priority ... the list is reorderable."*
- WATCH elem 4 -- *"In-flight queue: the committed plays executing in your committed order
  (1->2->3), with progress bars and completion ticks."*
- Workshop beat 2 praised the gantt-style duration bars as *"exceptional"* and named the
  reserve/allocation gauge + duration bars as *"the tension made legible."*

What exists instead: `InstrumentColumn/QueuePanel` -- a single-line `HBoxContainer` whose only
child is a grey `QueueHint` label ("No actions queued..."). No duration bars, no ETA text, no
per-item priority number, no reorder affordance, no progress/completion ticks in WATCH. The
"queue order = execution priority" **mechanic** may exist in the sim
(`month_plan.gd`/`month_controller.gd` were not audited for this doc), but it has **no UI
surface** -- the player cannot see or set the order.

Note this is also the exact thing Pip re-requested independently in UI_PASS_NOTES: *"have the
icons ... on the planned actions in sequence so the player has a better visual representation
of their priority ordering, like the build queue in Civ."* So the wireframe and the latest
playtest agree: build the queue-as-gantt. Sizing it into the lower-right is the natural home
(it is a WATCH-and-PLAN throughline; `instrument_panel.gd` already documents the queue as "the
throughline between the two screens").

---

## 3. Ranked enhancement proposals

Effort key: **T** = trivial (<~30 min, one file), **S** = small (a few hours), **M** = medium
(~1 day, structural). Tag: **[BUG]** defect fix / **[DESIGN]** intended-but-unbuilt or restyle.

### T -- trivial, do-first

- **P1 [BUG] Kill the double doom percentage (row D10).** Pick ONE readout. Cheapest: hide the
  DoomMeter's internal `draw_string` percentage (guard the `doom_text` block in
  `doom_meter.gd:64-75` behind an exported `show_percentage := false`) and keep the
  `NumericDoomLabel`; or the reverse. One-line effect. Removes the "27.2% over 27%" collision.
- **P2 [BUG] Left-bind the action icons (rows D5).** Change `icon_button.size_flags_horizontal`
  from `SIZE_SHRINK_CENTER` to `SIZE_SHRINK_BEGIN` (or fill) in `main_ui.gd:1222`, and set the
  `icon_stack` VBox `alignment` to begin. Directly answers "centre-aligned rather than
  left-bound." Confirms/limits the perceived vertical-gap by removing the horizontal float.
- **P3 [DESIGN] Dev-only per-zone background tint (row D15).** Add a faint distinct `ColorRect`
  (or panel bg) behind PlanScreen / InstrumentColumn / WatchScreen, gated on a debug flag.
  Pip explicitly wants this to see borders while building. Doubles as the confirmation tool for
  the icon-gap root cause (see note below P2).
- **P4 [DESIGN] Make the WATCH banner fade after first play (row D14).** Gate the permanent
  banner text in `screen_mode._refresh_banner` on a `GameConfig.seen_watch_intro` bool; collapse
  to a short tag once seen.

### S -- small

- **P5 [DESIGN] Frame + rehome the upgrades list (rows D6/D7).** Wrap `UpgradesLabel` +
  `UpgradesScroll` in a titled `PanelContainer` so it stops reading as orphaned, and drop the
  standalone hiring rows from the action list (handled inside the hiring submenu per Pip). Cheap
  version of the real fix; the structural version is P9.
- **P6 [DESIGN] Constrain the cat in PLAN (row D11).** Clamp the `OfficeCat` panel size in the
  shared `InstrumentColumn` so it stops dominating PLAN centre; longer term move the ambient
  cat/office read to WATCH per beat 3. (UI_LAYOUT_GUIDE has a "do not enlarge cat" rule -- so
  this is bringing it back into spec, not violating it.)
- **P7 [DESIGN] Office-floor sprite scale bump (row D12).** In `office_floor.gd`, scale the
  sprite draw/`EmployeeSprite` size up (the component was tuned for 360x260; it is now in a
  180px strip). Art-side lever Pip named ("scale of the art assets will need to be worked on").
  Pairs with P10 for the width.
- **P8 [DESIGN] Give the InfoBar/context strip its own colour + stop the hover jump (row D16).**
  Tint the InfoBar panel a distinct palette value; the fixed 60px already exists -- ensure the
  cost text renders within it without reflowing the strip above.

### M -- medium / structural

- **P9 [DESIGN] Grouped `ABBBCCC` action submenus (rows D3/D4).** Restructure `_populate_actions`
  so each *category* is one A-icon; clicking/hovering expands the B-list of that category's
  actions (reuse the existing #510 submenu-align machinery), with the C context window on hover.
  This is Pip's own sketch and it simultaneously fixes the sparse-column (fewer top-level icons),
  the hiring-row bloat, and the missing grouping. Biggest UX win on PLAN.
- **P10 [DESIGN] Build the committed-queue gantt / "operations underway" tracker (row D2 -- the
  headline gap).** Replace the one-line `QueuePanel` hint with a small vertical list: per
  committed play a row of `[priority #] [icon] [duration bar ---> ETA]`, reorderable (drag or
  up/down), reused in WATCH with a progress fill + completion tick. Surfaces the
  queue-order-as-priority mechanic. Start read-only (bars only), add reorder second.
- **P11 [DESIGN] WATCH: give the office floor more of the right side (row D12).** Restructure the
  WATCH column so the floor is not stacked *under* the full-height feed in a 0.4 strip. Options:
  (a) split WATCH into feed (left ~0.45) + floor (right ~0.55, taller); (b) let the floor span
  the InstrumentColumn+WatchScreen width in WATCH mode only. Answers "floorspace can take up a
  little more of the right hand side." Couples naturally with the A/B switch (P12) as one of the
  two layouts.

**Top-5 by impact-per-effort:** P1 (bug, T), P2 (bug, T), P10 (the missing gantt, M), P9
(grouped submenus, M), P7 (office-floor scale, S).

> Diagnostic note for the icon-gap (P2/P3): from the scene files the gaps are most plausibly
> horizontal (70px tiles `SHRINK_CENTER` in a wide column) plus top-packing dead-space below a
> short list -- NOT a large inter-item separation (`icon_stack` separation is 1). P3's per-zone
> tint will confirm this in one glance. If real inter-item gaps persist after P2, look for
> vertical `SIZE_EXPAND` leaking onto the buttons.

---

## 4. A/B display-mode switch -- feasibility + recommendation

**Idea:** a `GameConfig`-flagged layout switch (e.g. `ui_layout: "classic" | "proposed"`) so Pip
can flip arrangements in-game and iterate without rebuilds.

### Feasibility -- strongly feasible, and the codebase already does the hard part

`ScreenModeController` (`screen_mode.gd`) *already* implements exactly this pattern for
PLAN/WATCH: it does **not** reparent the widget tree (its own docstring: *"main_ui.gd is heavily
coupled to absolute node paths -- moving nodes would break it"*); it registers nodes and toggles
their `visible` + swaps a few container properties. An A/B layout switch is the same move applied
to layout properties instead of visibility. `GameConfig` already has the flag+persistence
mechanism (`show_rivals_feed`, `colorblind_mode` bools saved via `ConfigFile` in `save_config`).

### Scene-swap vs container-reflow -- reflow is much cheaper here

- **Scene-swap** (two full alternate `.tscn` layouts) is the WRONG mechanism: `main_ui.gd` is a
  3.7k-line monolith wired to fixed node paths and `.tscn` signal connections. A second scene
  means duplicating every `@onready`/path/signal or building an abstraction layer first --
  high cost, high regression risk.
- **Container-reflow** (one scene, flip container properties from a flag) is the cheap, proven
  path. The A/B differences are almost all container-property values:
  - column `size_flags_stretch_ratio` (e.g. PLAN 0.3/0.3/0.4 vs a proposed split),
  - upgrades parent (left column vs a framed sub-panel -- `reparent()` a single subtree),
  - office-floor host + size in WATCH (P11's two options are literally the A and B),
  - queue panel = one-line hint (A) vs gantt list (B, from P10).

### Recommended mechanism (build sketch)

1. Add `var ui_layout: String = "classic"` to `game_config.gd` + persist it in
   `save_config`/`load_config` (copy the `show_rivals_feed` lines).
2. Add a `func apply_layout(name: String)` on `MainUI` (or a small `LayoutController` sibling to
   `ScreenModeController`) that, given the flag, sets the handful of container properties above.
   Keep every A/B difference in this ONE function so the two arrangements are legible side by side
   and easy to tune.
3. Bind a debug key (there is prior art: `PageUp/PageDown` doom-nudge is debug-build-gated in
   `main_ui._debug_nudge_doom`) to cycle `ui_layout` and call `apply_layout` live. In-game flip,
   zero rebuild -- exactly the iteration loop asked for.
4. Ship "classic" = today's layout; "proposed" = P6+P9+P10+P11 assembled. Pip A/Bs, picks, then
   the loser is deleted (the switch is scaffolding, not a permanent feature).

**Recommendation: build the A/B switch as a container-reflow `LayoutController` driven by a
persisted `GameConfig.ui_layout` flag + a debug hotkey. Do it AFTER P1/P2 (free bug fixes) and
alongside P10/P11 (the two arrangements need a real "proposed" layout to be worth comparing).**
Effort: the switch harness itself is **S**; its value depends on P9/P10/P11 existing as the
"proposed" side, which are **M**.

---

## Open questions for Pip

1. Which doom percentage stays -- the decimal `NumericDoomLabel` (27.2%) or the meter's integer
   centre text (27%)? (P1 needs the call; I lean: keep the meter's integer, drop the label, so
   the number lives inside the gauge.)
2. Upgrades: fold into the action hand as an `ABBBCCC` category (P9), or keep as a separate
   framed panel (P5)? They are conceptually purchases, not month-plays -- a case for keeping
   them distinct.
3. Office floor: widen within WATCH only (P11a/b), or promote the whole ambient office+cat to a
   WATCH-dominant layout per beat 3 (bigger, ties to the "proposed" A/B side)?
4. Is the queue-order-as-priority mechanic actually wired in `month_controller`/`month_plan`
   already (so P10 is pure UI surfacing), or does the mechanic itself still need building?
   (Not audited in this pass.)
