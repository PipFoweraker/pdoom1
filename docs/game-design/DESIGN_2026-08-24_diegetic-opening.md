# The diegetic opening -- keys, browsing, the persistent office, and a second action class

> **Status: design document. Nothing ruled, nothing built, no code written.** Assembled
> 2026-08-24 for Pip from voice-memo atoms M24-002 .. M24-009 (memo `084241`), which are
> stored verbatim in `D:/Local_Code/coordination/tools/atoms/memo_rulings_2026-08-24.jsonl`
> and summarised in `D:/Local_Code/coordination/UNPACK_2026-08-24_morning-memos.md` section D.
> All nine atoms carry `"status": "open"`, `"owner": "pdoom1-seat"`. **Nothing from those
> memos has been filed as a pdoom1 issue yet** (checked: `gh issue list --search "M24"` and
> four other searches return zero).
>
> **Pip is the architect.** Every section below is options plus a recommendation, never a
> plan. Where this seat is uncertain the word is UNKNOWN and it says what would settle it.
>
> **Pip's own constraint, from M24-009, governs the whole document:**
>
> RULING: 2026-08-24 -- the diegetic-opening redesign (M24-002..009) must not be ladder- or epoch-breaking -- flavour: ladder-epochs -- mechanism: `tools/check_ladder_bump.py`
>
> Every proposal below carries an explicit ladder verdict against the rule in
> `docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md` section 3: *"the ladder version bumps
> if and only if two identical inputs (same seed, same player choices) could produce a
> different score, a different world trajectory, or a different RNG stream than the previous
> epoch."*

---

## Read this first: three vocabulary traps in this document

| Word | What it means here | Where it is fixed |
|---|---|---|
| **Instant** | Two different things. ADR-0009's *instant speed* already exists and means "a response window opened, spend your crisp reserve". M24-006's *instant* is a NEW player-initiated action class that "costs no attention". Section 3 keeps them apart. | ADR-0009 s3; M24-006 |
| **Interrupt** | Today: an event that fires mid-month and pauses playback (`MonthController` `Status.PAUSED_ON_WINDOW`). The world interrupts you. M24-006 also wants the player to act at that moment. | `godot/scripts/core/month_controller.gd:8` |
| **Office** | Three separate objects ship today: a static backdrop (`main.tscn:16`), a live animated floor with walking staff (`OfficeFloor`, WATCH only), and a sim-side lease economy (`Office`). "Persistent office" touches only the second. | section 1.4 |

---

## 1. What exists today

No proposals in this section. Everything here is a file, a line number, or a quote.

### 1.1 The cold open -- it exists, it is good, and it already does half of M24-002

**Files:** `godot/scripts/ui/cold_open_sequence.gd` (852 lines) and the near-empty scene
wrapper `godot/scenes/cold_open_sequence.tscn` -- the whole UI is built in code by
`_build_ui()` at `:192`.

**Trigger, one call site:** `godot/scripts/ui/config_confirmation.gd:86-93`

```gdscript
if GameConfig.should_show_intro():
    SceneTransition.go_to("res://scenes/cold_open_sequence.tscn")
else:
    SceneTransition.go_to("res://scenes/main.tscn")
```

Both New-Game routes funnel through that screen (`welcome_screen.gd:171-177` "Launch Lab";
`pregame_setup.gd:237` custom seed). Load Game (`welcome_screen.gd:179-185`) and the
settings resume path (`settings_menu.gd:432`) go straight to `main.tscn` and bypass it.

**Gate:** `GameConfig.should_show_intro()` (`godot/autoload/game_config.gd:780-786`) returns
`play_intros and last_seen_intro_version != INTRO_VERSION`. `INTRO_VERSION` is
`const INTRO_VERSION: String = "1"` (`game_config.gd:209`).

**The beats, verbatim from `cold_open_sequence.gd:44-49`:**

```gdscript
const BEATS: Array = [
    {"kind": "text", "text": "Doom is coming.", "duration": 3.0, "cue": "portal_open"},
    {"kind": "text", "text": "But... when am I?\nWhat can I do?  What *day* is it?", "duration": 4.0, "cue": "world_resolves"},
    {"kind": "text", "text": "*checks pockets*  --  a primitive phone!", "duration": 3.0},
    {"kind": "phone", "text": "", "duration": 0.0},
]
```

Then the phone: a 360x620 CRT-green slab, lock screen -> 4-digit keypad -> home.
**Any four digits unlock** and the success is phrased as fortune -- `PHONE_UNLOCK_LUCKY`
is `"Oh! how lucky!"` (`:59`), the "Editor's benevolent hand" principle from
`docs/game-design/COLD_OPEN_SEQUENCE.md:99-106`. Home shows BANK (one static
`Balance.num("starting_resources.money", 245000.0)` lookup, `:554`) and MESSAGES.

**The handoff already points at scouting.** `cold_open_sequence.gd:70-74`:

```gdscript
const STRANGER_MESSAGE: String = "Hello past me! No, I can't tell you how it ends. You know nothing yet -- go and find out. Read something, show up somewhere, or be loud online. Scouting. -- MHS"
const HANDOFF_ACTION_ID: String = "scouting"
const HANDOFF_HINT_TEXT: String = "Advisor: you do not know anything yet. Go and find out -- scouting (the glowing button)."
```

Correction worth recording: the `FRESH_EYES_TEARDOWN_2026-08-06.md` walkthrough quotes an
older string that called itself *"expository filler (for now)"*. That was replaced in
commit `78be0370` (#1136). **The shipped copy is the line above.**

**The arrival visuals already contain M24-002's imagery.** `cold_open_sequence.gd:23-31`
describes the #1112 build: the `time_portal.gdshader` vortex opens under "Doom is coming.",
then a held street frame resolves behind it --

```gdscript
const POSTER_ART: String = "res://assets/images/backgrounds/intro_bus_strangers_help.webp"
```

with the source comment at `:97-98`: *"the rainy street the traveler lands in ... it rhymes
with Pip's 2026-08-04 prior-beat sketch: teleport back, meet a bus."* **The strangers who
help you up are already on screen.** The keys are what is missing, not the scene.

**Purity contract, `cold_open_sequence.gd:11-16`:** *"PURE PRESENTATION. Reads no scoring
state, mutates no game state, draws no RNG, touches no seed -- it does NOT fork the
leaderboard ladder."* Enforced by a source scan in `godot/tests/unit/test_cold_open_intro.gd:55-65`
which bans `randi(`, `randf(`, `RandomNumberGenerator` and `change_scene_to_file(`.

**#1141 ("the cold open never fired") is a config-state report, not a code path.** No branch
unconditionally suppresses it. The two ways an install retires it permanently:
`mark_intro_seen()` fires on *every* exit including a skip (`:796`, saving immediately at
`game_config.gd:792`), and a completed hold-to-skip also flips `play_intros = false` and
persists it (`:791-793`), after which even an `INTRO_VERSION` bump stays suppressed. A
replay affordance now exists (`settings_menu.gd:348-356` -> `reset_intro_seen()`, landed in
`658963d7`). The issue is still OPEN and its own text says: *"Treat the cold open as
unverified, not as working."*

### 1.2 What a brand-new player sees at turn 1

`main.tscn` (418 lines). Top to bottom:

- **Backdrop** (`main.tscn:16, :38-49`) -- `office_wide_day.webp`, full rect,
  `modulate = Color(0.35,0.35,0.35,1)`, with a purple-black 25% scrim over it (`:51-59`).
  **The office is already the wallpaper. It is dimmed to a third and scrimmed.**
- **Top bar** (`:79-183`) -- eight readouts on one line: title, "Turn N - Wed 5 Jul 2017",
  Money, Compute, Research, Papers, Rep, and `APLabel` showing `"Attention: 20"` plus
  coloured `*` glyphs per staff member (`main_ui.gd:1172-1226`). The two-way founder-hour
  split (planning vs operating) surfaces only in the tooltip.
- **Mode banner** (runtime, `screen_mode.gd:187-200`) -- `"## PLAN - strategy - lay out the
  month, then COMMIT THE MONTH >"`. The teardown calls this *"the single best orientation
  device on the screen"*.
- **PLAN screen, left** -- an ATTENTION pip gauge built in code (`plan_screen.gd:63-107`),
  a getting-started hint, then the hand: ~15 icon tiles, 70x70, **icon-only, no names on
  the face** (`action_bar_renderer.gd:184-296`); then "Upgrades:" with prices; then a
  Command zone with "Do Nothing".
- **Instrument column, middle** (`main.tscn:198-310`) -- visible in BOTH modes: office cat
  (`:223`), numeric doom, doom meter, doom explanation, trend sparkline, per-source
  breakdown, Liability Ledger summary, Employees button, staff roster, and the Action Queue
  panel.
- **WATCH screen, right** -- **hidden in PLAN.** Holds the feed, two filter toggles ("Hide
  arxiv flood", "Hide rival intel"), and the office floor sprite strip
  (`watch_screen.gd:63-93`).
- **Bottom bar** (`:339-391`) -- Reserve Attention (disabled), Undo (Z), Clear (C),
  "COMMIT THE MONTH >", "Plan (Enter)", phase label, Bug Report (N).

**There is no tutorial system.** The complete onboarding machinery is four things: the
welcome overlay on the *menu* screen (`welcome_overlay.gd`, gated on `games_played == 0`),
a getting-started hint shown while `turn < 3` (`main_ui.gd:1266-1269`), the first-lever
nudge from the cold open (`main_ui.gd:1580-1603`, a looping alpha pulse on one named
button), and coming-soon gating in `action_bar_renderer.gd:73-83`.

### 1.3 The turn loop and where a decision can be taken

- **Two screens, whole subtrees toggled.** `ScreenModeController` (`godot/scripts/ui/screen_mode.gd`)
  does not reparent anything; it registers existing panels as `_plan_only` / `_watch_only`
  and flips visibility (`:10-15, :39-46`). `main_ui.gd:403-405` registers the entire
  `WatchScreen` -- **and therefore the office floor** -- as watch-only.
- **Day-tick playback with auto-pause.** `MonthController` (`godot/scripts/core/month_controller.gd`)
  advances ticks, routes events by tier, and *"PAUSES playback whenever a window demands a
  decision"* (`:1-8`). `is_paused()` at `:59`, `"paused_on_window"` at `:68` and `:114`,
  `_finish_paused_tick()` at `:362`, and the paused state **survives save/load** (`:400`).
- **Speed control ships; player-initiated pause does not.** `screen_mode.gd:37` --
  `const _SPEEDS := {"1x": 0.20, "2x": 0.10, "4x": 0.05}`. And `:98-104`:

  ```gdscript
  # Play/pause -- STUB (follow-up lane owns real pause; auto-pause on windows already works).
  var pause_stub := Button.new()
  pause_stub.text = "||"
  pause_stub.disabled = true
  ```

  **This matters directly for M24-006**, which says instants work *"because the sim can now
  be paused"*. Half true: the sim pauses **when the world says so**, never when the player
  says so.
- **The window menu.** `WindowResolver` (`godot/scripts/core/window_resolver.gd:1-17`)
  resolves `handle_reserve` / `handle_cannibalize` / `defer` / `ignore` / `auto_ignore`.
- **The reserve is the existing instant-speed currency.** `godot/scripts/core/month_plan.gd:15-16`:
  *"reserved -- explicitly set aside at plan time for response windows (instant speed); this
  is ADR-0009's CRISP reserve -- the gamble that makes windows interlock"*; `:44` names it
  *"instant-speed firefighting"*; `pay_from_reserve()` at `:339`. Unspent reserve
  **evaporates** at month end (`:18`).
- **Turn step order is replay-load-bearing.** `turn_manager.gd:27-28` and `:562-564`:
  *"STEP ORDER IS LOAD-BEARING: it defines the deterministic RNG stream that recorded
  replays re-simulate -- reordering steps invalidates every replay."*

### 1.4 The office, all three of it

**(a) Static backdrop.** `main.tscn:16` -- `office_wide_day.webp` at 35% modulate under a
scrim. Present in both modes, because it is behind the whole UI.

**(b) `OfficeFloor` -- the live animated room.** `godot/scripts/ui/office_floor/office_floor.gd`
(`class_name OfficeFloor`, ~780 lines) plus `employee_sprite.gd`, `employee_fsm.gd`,
`render_grid.gd`, `anchored_overlay.gd`, `worker_variant_pool.gd`. 4,793 lines across the
directory, backed by 16 unit-test files (#1229's count, verified). **Mounted only inside
WatchScreen** (`watch_screen.gd:63-81`, 260px tall, alpha 0.9, tier 1), driven every
`game_state_updated` from `main_ui.gd:1122-1125`. Purity contract at `watch_screen.gd:26-29`:
*"its wander uses a private cosmetic RNG, never the seeded sim stream."*

**(c) `Office` -- the sim-side lease economy.** `godot/scripts/core/office.gd` +
`godot/data/office/offices.json`. Tier-0 `bedroom`, `hire_cap: 2`; three tier-1 leases
(co-working corner / walk-up / university annex). The forcing function is the cap, not a
modal. **The render seam is already declared** -- `office.gd:26-28`:

> *"SIM/RENDER BOUNDARY (ADR-0018): floorplan.\* in offices.json is RENDER-ONLY. Nothing in
> this file (or any sim path) reads floorplan -- the sim reads hire_cap. floorplan() is
> exposed purely so office_floor.gd can size itself off the signed lease later."*

and `offices.json` `_sim_vs_render` says the same: *"floorplan.desk_slots is authored to
equal hire_cap as a courtesy to the render layer -- the sim reads hire_cap and must never
read desk_slots."* Every entry already carries `width_units`, `depth_units`, `desk_slots`,
`meeting_rooms`, `size_label`.

**(d) `office_sandbox.gd` -- the base-building toy that already exists.** v4.1, side-by-side
small/large compare view, prop placement on a first-class `RenderGrid`, posters, cats,
scummy/decent/premium quality tiers, promoted-asset loading from `art_source/`. Its own
header: *"This is the prototyping ground for the future runtime 'office reflects game
state' asset system ... It is a DEV TOOL and NEVER ships to players."* Reachable only by
opening `godot/scenes/ui/office_floor/office_sandbox.tscn` in the editor.

### 1.5 Scouting as it exists

`godot/data/actions/scouting.json` -- three stubs, each with a real deterministic effect:
`scout_read` ("Read the Literature", `attention: 1`, hour_type `approvals`), `scout_meetups`
(`attention: 1`, `money: 300`, `doors`), `scout_shitpost` ("Post Online", `attention: 1`,
`approvals`).

All three live **behind the `scouting` door** -- `core.json:144` is an `is_submenu` action.
`docs/ACTION_TAXONOMY.md` rows 52-54. So the cold open's glowing button opens a submenu; the
browsing action is two clicks from turn 1, not one.

SA itself is, per `docs/ARCHITECTURE.md`: *"designed; largely not built as a subsystem. No SA
purchase/screen-gating or decision-flip telemetry yet."*

### 1.6 What the record already decided, so we do not re-open it

| Question | Already answered | Where |
|---|---|---|
| Should the office persist across the mode switch? | **Yes.** Pip: *"losing it when you switch seems silly, it should be persistent while other things switch."* | `coordination/DESIGN_2026-08-10_calendar-and-persistent-stage.md` s3 |
| Can spatial facts feed gameplay? | **No.** *"No spatial fact will ever become a gameplay input."* Render-local cosmetic interactions are **outside the doctrine's scope** (rider b); click-to-command is legal **under the entity-ID invariant** and must always have a non-spatial path (rider c). | ADR-0018 |
| Is the office direction "now"? | **No.** *"Design thread, deliberately NOT work. Pip said 'not now' about this in the same breath as describing it."* Also: it is **top-down, not isometric**; going isometric is a renderer rewrite. | #1229 |
| Is there a second decision speed? | **Yes, since 2026-07-12.** *"Two decision speeds (MtG taxonomy, none of its machinery): plan speed ('sorcery') ... response windows ('instant')."* | ADR-0009 s3 |
| How do interrupts trade against the committed queue? | **Still open.** Variants A/B/C written and never ruled. | `coordination/DESIGN_2026-08-12_interrupt-resolution-variants.md` |
| Does the pack accept art because it is good? | **No.** *"The pack is a FUNCTION of declared demand, not an accumulation of past approvals."* | ADR-0019 |
| Is the phone the permanent HUD? | **Parked, explicitly.** *"Does the phone become the persistent HUD later, or stay an intro device? PARKED for a design workshop."* M24-002 is the answer to that parked question. | `COLD_OPEN_SEQUENCE.md:153-156` |

### 1.7 The stranded art, measured

Method (this seat's agent, over the current checkout): 503 image files under `godot/assets/`;
for each, resolve `uid://` from the sidecar and substring-search all 536 `.tscn/.gd/.tres/
.json/.cfg/.theme/.gdshader/.csv/.txt/.md` files under `godot/` for both the `res://` path
and the uid.

**151 of 503 image files under `godot/assets/` are referenced by nothing -- 9.9 MB.**
Widening the search to the whole repo rescues exactly one (`cats/simple/web-doom-cat.jpg`,
which appears in `credits.json`).

The richest seams, with paths:

| Cluster | Count | Bytes | Path |
|---|---:|---:|---|
| **CRT-dossier portraits** | 15 (5 characters x 256/512/1024) | 5.35 MB | `godot/assets/portraits/dossier_{authoritarian_pessimist,burned_out_senior,capabilities_optimist,moral_crusader,people_pleaser}_{256,512,1024}.png` |
| **Event popup art** | 8 (100% of dir) | 1.92 MB | `godot/assets/images/events/event_{board_v2,board_v3,crisis_v1,crisis_v3,opportunity_v2,opportunity_v4,secret_v1,secret_v3}.png` |
| **Records-room plates** | 5 of 6 | 1.18 MB | `godot/assets/images/backgrounds/records/records_{brass_plaques,crt_ranktable,stacks,trophy_terminal,vault}.webp` |
| **Two more office angles** | 2 | 0.33 MB | `godot/assets/images/backgrounds/office_lab_aisle.webp`, `office_mezzanine.webp` |
| **9-slice UI frame kit** | 10 (100% of dir) | 0.06 MB | `godot/assets/icons/frames/ui_frame_*.png`, `ui_separator_*.png` |
| **Button hover/disabled states** | 17 of 18 | 0.07 MB | `godot/assets/icons/buttons_{hover,disabled,normal}/` |
| **Employee status icons** | 6 of 8 | 0.04 MB | `godot/assets/icons/employee_status_{absent,active,burned_out,compromised,excellent,stressed}_64.png` |
| **Orphaned doom-cat SVGs** | 5 | 0.01 MB | `godot/assets/cats/default/{happy,concerned,worried,distressed,corrupted}.svg` |

`godot/assets/portraits/README.md` calls the dossier set *"The single most internally-consistent
promoted set: the CRT-dossier v2 run."* `patch_notes.json:216` already claims *"Staged dossier
portraits on candidate and employee cards"* -- **no scene or script loads them.**

`godot/assets/cats/README.md` self-documents its own orphan: *"`default/` ... is ORPHANED. Its
only consumer was `contributor_manager.gd`, deleted 2026-08-04 for having zero callers ...
They are kept under the ADR-0019 grandfathering rule for already-packed assets, not because
they are used."*

**Outside the pack:** `art_source/` is 148 MB / ~4,470 files, none of it packed. It holds the
whole desk/chair/monitor/plant/whiteboard prop corpus
(`art_source/pixellab_2026-07-16/props/`, `office_library/`, `pixellab_2026-07-19/props/`,
`pixellab_2026-07-17/reroll/objects/`), five finished narrative vignette plates
(`art_source/vignettes_2026-07-28/0{1..5}_*.png`, ~900 KB each, matching the KEYED specs in
`docs/game-design/SEED_VIGNETTE_SPECS.md`), and ~2,300 cat frames.
`docs/art/A4_COLLAPSE_2026-08-20.md` counts **2,687 approved-but-unpromoted assets, 51.5 MB.**

**#787 is CLOSED and did its job** (commit `0d038e11`, `.pck` 418 MB -> 59.1 MB). It removed
*size variants of icons whose `_64` was kept.* It did not touch icons whose `_64` is itself
unreferenced -- which is the 151-file residue above.

**Three structural blockers, none of them artistic:**

1. **No demand slot exists.** `tools/assets/demand/slot_picks.json` reads `"slots": {}` and
   `"frame_roles": {}`. Under ADR-0019 that is the only path into the pack.
2. **`props_manifest.json` gates every new office prop.** Only 3 props are manifested
   (`filing_cabinet`, `server_cluster`, `water_cooler`) and `test_prop_manifest.gd` fails
   loudly on an unmanifested PNG.
3. **`event_dialog.gd` cannot render a picture.** 497 lines, **zero** matches for
   `texture|sprite|image|.png|.svg|.jpg`; there is no `TextureRect` in the dialog at all
   (#1218 section E). This is why the stray cat has no art: *"There is no slot to promote
   art INTO ... the owner here is engineering, not art."*

### 1.8 Where the first ten turns are already known to be broken

Five open issues say the same thing from different angles. None needs re-opening.

- **#1210** (workshop request) -- *"A real first-time player, given the shipped build for 27
  minutes on 2026-08-10, could not work out what to do."* And the warning against reading the
  44 -> 87 score jump as progress: *"A surface that doubles when you stop hiding your own error
  messages is a surface that had a long way to come, not one that has arrived."* Its five
  interlocking items include *"Actions resolve instantly, so the early game has no rhythm
  (#1044) -- there is nothing for the confirmation to be a confirmation of."*
- **#1202** (early-game legibility) -- five findings, of which two land directly here:
  item 4 is *"the thing I probably want to do today is like shuffle the UI around such the
  simulation is in both screens"*, and item 5 is *"there's one choice at the start of the
  game ... Right now those choices are basically invisible ... you will start with slightly
  different decor"* -- **with the ladder constraint already attached**: *"it happens
  post-config, so we don't score fuck ourselves by having the actions taken during turn zero
  to live outside the scoring system in such a way that it bifurcates the ladder."*
  Measured, not felt: *"26 of the 33 `log_message()` call sites in `main_ui.gd` fire during
  PLAN"* -- and PLAN hides the feed. *"A player clicking an action they cannot afford sees
  nothing happen at all."*
- **#1223** (queue vs header) -- two of four items fixed, two open. The live one:
  *"what is the Action Queue once things take time?"* and *"Hiring is currently the only
  thing in the game that does take time, which is why it is the first system to break the
  widget."*
- **#1218** -- the attention-spent audit plus the no-art-slot finding above.
- **#1229** -- the office thread, marked not-now.

---

## 2. The nine atoms, one at a time

Each: what it means concretely, what it touches, what it replaces, ladder verdict.

**The verdict tool.** `tools/check_ladder_bump.py:137-167` treats **everything under
`godot/` as gameplay by default**, with an explicit cosmetic denylist:
`godot/{addons,assets,docs,scenes,scripts/debug,scripts/dev,scripts/ui,tests,theme,tools}/`
plus a handful of named files and the `.md`/`.uid`/`.import` suffixes. **`godot/data/` is
NOT on that list**, so any data edit needs either a bump or a stated
`Ladder-Impact: none -- <reason>` line. That is the practical shape of "does not fork" below:
it means the reason line is honest, not that the gate stays quiet.

---

### M24-002 -- keys replace the phone

> *"Strengthen the diegesis at game start: player is hit by a car (cars do not stop like they
> do in the future); the people who help them up introduce themselves; replace the
> mobile-phone introduction with KEYS -- 'all I've got on here, these keys' -- with an address
> on the keychain leading to the office doors. 'Give us a call if you need anything'
> establishes the starting contacts as a baseline."*

**Concretely.** The four-beat `BEATS` array and the three phone panels
(`_build_lock_panel` / `_build_keypad_panel` / `_build_home_panel`, `cold_open_sequence.gd:446-597`)
are replaced by: the poster frame that already ships (`intro_bus_strangers_help.webp`) held
longer and given two or three named strangers; a keys object that carries a fob with an
address; and an arrival at the office door instead of an arrival at a home screen.

**What it replaces, and what is lost.** The phone carried three jobs the keys must inherit or
drop:

| Phone job | Keys equivalent | Assessment |
|---|---|---|
| Bank readout ($245,000) | M24-004 -- discovered by clicking, not shown | Moves, does not vanish |
| MHS message = the advisor channel and the scouting handoff | *"Give us a call if you need anything"* -- the strangers become the advisor channel | **Better.** Provenance personified: *"Wherever a character plausibly owns a piece of information, deliver it through them."* (DESIGN_PHILOSOPHY, On the early game) |
| The passcode = the player's first act of agency | Unlocking the office door with the key | Direct swap, same shape, same "Oh! how lucky!" register |

**What it also does, which is the real argument for it.** `COLD_OPEN_SEQUENCE.md:153-156`
parked the question *"Does the phone become the persistent HUD later, or stay an intro
device?"* Keys answer it by deletion: a keychain is not a HUD, so the question stops being
owed. That is the restraint principle -- *"a mechanic that needs a new player-facing currency
or panel has to prove it can't be a read/write on existing ones first."*

**Art.** There is **no key art anywhere in the tree** -- zero files matching `*key*` in
`art_source/` or `godot/assets/`. The nearest substitutes are
`godot/assets/icons/main_navigation/ui_control_{lock,unlock}_64.png` (both stranded). This is
a genuine generation request, and under ADR-0019 clause 5 it should be *"surfaced loudly and
forward -- never a placeholder texture."*
Note the keys motif is already written elsewhere: `SEED_VIGNETTE_SPECS.md` spec 01 is
*"keys still in hand at frame edge"* and spec 12 is *"keys and one unsigned page on bare
concrete"*, and `art_source/vignettes_2026-07-28/01_cat-in-the-alley.png` is the rendered
plate for the first.

**Ladder verdict: DOES NOT FORK -- for the presentation. FORKS if the contacts become real.**

- The cold open is `godot/scripts/ui/` + `godot/scenes/` + `godot/assets/`, all three on the
  cosmetic denylist, and the file's own contract plus `test_cold_open_intro.gd:55-65` already
  prove it draws no RNG and writes no state.
- Bumping `INTRO_VERSION` to re-show the new intro is **explicitly** ladder-neutral:
  `BUILD_VS_LADDER` s4.2a lists `INTRO_VERSION` among the `game_config.gd` lines that *"[are]
  not evidence of gameplay change."*
- **The fork risk is one phrase.** *"establishes the starting contacts as a baseline"* -- if
  those contacts become sim-readable state (a relationship roster the hiring or networking
  path reads), that is a new starting condition on every seed, which is a different world
  trajectory from turn 1 for every existing replay. FORKS, unambiguously.

---

### M24-003 -- browsing is the first real action

> *"Player gets on the internet to understand what is happening -- this is the browsing
> action, and it moves situational awareness off zero. Search 'AI News', recognise founded
> orgs and recent events. Leads naturally into more player actions."*

**Concretely, this is two separable claims.**

**(a) Reachability.** Today `scout_read` is behind the `scouting` submenu door. Making
browsing "the first real action" could mean promoting it to a top-level tile. **The record
argues against that**: `docs/design/UI_ARCHITECTURE_2026-08-06.md` Part A rules that *"an
action is TOP-LEVEL if and only if it is the single door to a system the player steers when
composing an ordinary month's plan ... Anything that competes only with its own siblings ...
is NESTED"*, and explicitly kills the tempting axis: *"New player needs it in the first ten
turns -- necessary but not sufficient ... The early-need axis is served by badges on doors,
not by promotion."* `scout_read` competes with `scout_meetups` and `scout_shitpost`, so it
nests. **The reachability problem is not depth; it is that the scouting door is one of ~15
unlabelled 70x70 icon tiles, and #1202 item 2 records that the scouting actions have no icons
at all.**

**(b) Substance.** *"Search 'AI News', recognise founded orgs and recent events"* is a
different and much larger thing: a browsing surface that renders real 2017 world state and
lets the player recognise it. The dataset exists -- M24-018/019 record 1,194 timeline events,
*"989 (82%) of descriptions are under 60 characters"*. This is the scouting-as-replayability
engine from the philosophy: *"What keeps veterans replaying an opening isn't new content --
it's re-gathering information about this seed."*

**What it touches.** (a) `action_bar_renderer.gd`, `submenu_controller.gd`, icon assets, and
the cold-open handoff string (one const). (b) a new panel, plus whatever "SA off zero" means
mechanically -- and SA is *"designed; largely not built as a subsystem"* today.

**Ladder verdict: (a) DOES NOT FORK. (b) FORKS.**

- (a) is `godot/scripts/ui/` and `godot/assets/` only. Re-pointing `HANDOFF_ACTION_ID` is one
  string in a denylisted file. Reordering the action bar is view-side.
- (b) forks on two counts. `BUILD_VS_LADDER` s3.1: *"New content that changes the reachable
  game -- new actions/events/scenarios that can occur on existing seeds."* And mechanically:
  once a player queues an action that mutates state, event gating (`events.gd:173-190`)
  decides from those values whether a `randf()` is drawn, so the stream diverges from the
  first turn it is taken. **Note the asymmetry** -- old replays that never take the new action
  still verify, so the fork is forward-only. That does not exempt it; s3.1 #5 is a bump
  trigger on its own.
- **Changing `scout_read`'s existing effect to "move SA off zero" also FORKS**, because the
  same id now produces a different trajectory for the same input.

---

### M24-004 -- the bank account is discovered by clicking

> *"Bank account should be discovered by clicking 'check bank account' rather than popping up
> unprompted. Open question Pip left open: whether the player must check it or the number then
> tracks from there."*

**Concretely.** Today Money is a permanent top-bar readout (`main.tscn` top bar,
`main_ui.gd:1147-1151`) and the cold open shows the starting balance on the phone's BANK app.
The proposal makes the balance *unknown until looked at*.

**This is ADR-0001 (spending buys sight) turned inward.** The philosophy already has the
shape: *"sight and even UI comfort were things you paid for."* It is also the redaction motif
from `COLD_OPEN_SEQUENCE.md:113-115`, with its own guard rail: *"Redact NARRATIVE / LORE,
NEVER mechanical / lever info the player needs to decide ... Crisp levers, mysterious lore."*
**A hidden bank balance is a lever, not lore.** That is an argument that the check must be
one click, always available, never denied.

**Pip's own open question is exactly the fork line.** Read it as three options:

| Option | Behaviour | Ladder |
|---|---|---|
| **1. Reveal-once, then live** | Number hidden until first click; thereafter tracks normally | **Does not fork** -- UI visibility only, `godot/scripts/ui/` |
| **2. Stale-until-checked** | The readout shows the balance *as at the last check*, and drifts | **Does not fork** by itself (still a display), but see below |
| **3. Checking is priced** | "Check bank account" costs attention or a day | **FORKS** -- a new action with a cost changes the reachable game and the attention budget |

Option 2 has a trap worth naming: a display that can lie about the sim is exactly the
dual-source-of-truth failure class ADR-0018 cites as *"the structural precedent"* for the
2026-07-25 modal soft-locks. If the stale number is ever read by anything except the player's
eye, it stops being cosmetic.

**Ladder verdict: DOES NOT FORK for options 1 and 2. FORKS for option 3.**

---

### M24-005 -- the office is a persistent visual

> *"Office as persistent visual: start in a shitty office space; upgrades visibly change it --
> delivery person with a trolley, installation, then the office changes. Reinforces that some
> actions are trivial and cost no attention."*

**Concretely, three separable pieces.**

**(a) Make `OfficeFloor` visible in PLAN as well as WATCH.** Today `main_ui.gd:403` registers
the whole `WatchScreen` as watch-only, and the floor is a child of it
(`watch_screen.gd:63-81`). The change is to lift the floor out of `WatchScreen` into a region
registered as neither plan-only nor watch-only -- the same shelf the instrument column already
occupies. **Pip already ruled this** (`DESIGN_2026-08-10` s3), and #1202 item 4 names it as a
day's priority. The rationale in that doc is the one worth keeping: *"it gives every decision
a second place to land ... The sim stops being decoration and becomes the confirmation
channel."* That is the direct answer to #1210's *"there is nothing for the confirmation to be
a confirmation of."*

**The cost that document also names, and it is real:** *"OPEN -- what stays resident. The sim,
certainly. The calendar too? If both are permanent, the swappable region is small, and screen
budget becomes the real constraint on every subsequent panel."*

**(b) The delivery trolley.** An upgrade purchase triggers a render-local animation: a figure
walks in with a trolley, a prop appears, the room changes. **This is explicitly outside
ADR-0018's scope, not an exception to it** -- rider (b): *"Render-local cosmetic interactions
are unrestricted. Clicking a coffee pot and having it boil, a worker idling into a new pose,
ambient office flavor -- none of this touches the sim ... The doctrine governs the input -> sim
boundary."* The trigger is a sim event (an upgrade was bought); the animation reads it and
writes nothing back. Legal.

**(c) The prop art to make (b) visible.** Blocked by `props_manifest.json` -- three props are
manifested and `test_prop_manifest.gd` fails on a fourth without an entry. The corpus is
sitting in `art_source/pixellab_2026-07-16/props/` and `office_library/` (desk, chair,
monitor, pc, coffee, fridge, window, bookshelf, coat rack, couch, plant, server rack,
whiteboard -- each in clean/scummy variants). Under ADR-0019 the route is a demand entry
(*"office props: >=2 large pot plants at 96px"* is the shape the ADR gives), then a pull that
renders a derivative.

**Ladder verdict: DOES NOT FORK for all three, with one caveat.**

- (a) and (b) are `godot/scripts/ui/` and `godot/scenes/` -- denylisted, and `OfficeFloor`
  already carries a proven pure-view contract with a private cosmetic RNG.
- (c) adds files to `godot/assets/` (denylisted) and entries to
  `godot/data/office/props_manifest.json` (**not** denylisted). That data edit is genuinely
  non-behavioural, so it ships with `Ladder-Impact: none -- props_manifest is render metadata;
  no sim path reads it (ADR-0018)`.
- **Caveat, and it is the one to watch.** M24-005's last sentence -- *"Reinforces that some
  actions are trivial and cost no attention"* -- is M24-006 wearing an office costume. If the
  trolley animation is a *consequence* of a purchase, it is free and cosmetic. If clicking the
  trolley *is* the purchase, ADR-0018 rider (c) applies: legal, but the action must serialize
  as `(action, entity_id)` and there must be a non-spatial path to the same command.

---

### M24-006 -- two action classes

> *"Two action classes: planned actions, and instants/interrupts fired in response to events.
> Instants live in a different UI area (roughly where upgrades are now) and take effect on the
> day the decision is taken -- any time in the simulation, because the sim can now be paused.
> Pausing and speed control are what make this work."*

This is the largest structural claim in the memo and it gets **section 3** to itself.

Two factual corrections to carry into that section:

1. **Player-initiated pause does not exist.** `screen_mode.gd:98-104` is a `disabled = true`
   stub. Auto-pause on windows does exist (`month_controller.gd:8`, `is_paused()` at `:59`,
   and it survives save/load at `:400`). Speed control does exist (`_SPEEDS` at `:37`).
2. **The upgrades panel is inside `PlanScreen`** (`plan_screen.gd:12-14`), which is
   plan-only. *"Roughly where upgrades are now"* is currently a region that is invisible
   during exactly the phase an instant would be played in.

**Ladder verdict: see section 3. Short form -- a UI re-presentation of the existing window
menu does not fork; a genuine new action class does, without exception.**

---

### M24-007 -- stranded art gets a use, and an alpha sandbox

> *"Art assets are stranded. Find a use for everything there is a use for, and make it visible
> in-game that the player can cycle through them. During alpha, let players change the sim
> artificially, add and break assets, and possibly move things around in a base-building
> mode."*

**Name the tension first, because it is real.** ADR-0019 is the standing ruling that *"the
pack is a FUNCTION of declared demand, not an accumulation of past approvals"*, and its whole
purpose is to make *"packed but undemanded"* **unrepresentable**. *"Find a use for everything
there is a use for"* is supply-side reasoning; ADR-0019's arrow points the other way. Two
honest readings:

- **Reading 1 (compatible).** *"Make it visible in-game that the player can cycle through
  them"* **is a declared demand.** A gallery, a variant cycler, a decor pool -- these are
  pools with floors and sizes, exactly the shape ADR-0019 clause 3 asks for. The ADR is
  satisfied, not bent, because a real consumer names the pool.
- **Reading 2 (in tension).** If "find a use" means auditing the 2,687 approved-but-unpromoted
  assets and inventing consumers for them, that is the promote-then-justify loop the ADR was
  written to close after the 2026-08-03 incident (202 files, +228 MB, reverted before commit).

**Recommendation: adopt Reading 1 explicitly and say so, so the next agent does not read the
memo as an ADR-0019 override.**

**What is actually blocked, in order of value:**

| Stranded set | Blocker | The unblock |
|---|---|---|
| 15 dossier portraits, 5.35 MB | No consumer. `patch_notes.json:216` already *claims* they are on candidate cards. | A `TextureRect` on the hiring candidate card + employee roster row. The `_256` variants are the right size. |
| 8 event popup plates, 1.92 MB | `event_dialog.gd` has **no `TextureRect` at all**, and the event schema has no art field (#1218 E) | An art channel on the event popup: schema field + TextureRect + demand slot. **This is engineering, not art**, and it also unblocks the stray cat. |
| ~40 office props in `art_source/` | `props_manifest.json` + `test_prop_manifest.gd` | Manifest entries; then M24-005(b) has something to deliver on a trolley |
| 5 rendered vignette plates | No vignette presenter for KEYED specs; `conference_vignette.gd` is text-only ("option 1 from the design seed", the seed recommends option 2) | A backdrop slot on the existing vignette scene -- its header says it is *"deliberately structured so that upgrade is a re-skin"* |
| 5 records-room plates | No consumer | The leaderboard screen is the obvious one |

**Ladder verdict: DOES NOT FORK -- rendering art. FORKS -- "let alpha players change the
sim".**

- Art into `godot/assets/`, presenters in `godot/scripts/ui/`: denylisted. A demand-manifest
  entry and a `props_manifest.json` row are `godot/data/` edits that ship with a stated
  `Ladder-Impact: none` reason.
- *"Let players change the sim artificially, add and break assets"* is a dev tool pointed at a
  live run. **#1134 already records what that costs**: F3 event injection permalocking a run.
  The only safe shape is the one `GameConfig.is_ranked_run()` (`game_config.gd:597`) already
  establishes -- the rule lives in the only path that exists, and that function's own comment
  names the failure mode of the alternative: *"a second write site that forgets this check
  silently reopens the hole."* An unranked sandbox run that never posts a score does not fork.
  A ranked run that a dev tool touched is not a run.

---

### M24-008 -- give the base-building direction to Aileen

> *"Give the base-building/cozy-sim direction to Aileen, who is into base building and cozy
> sims, and ask what would make it better."*

**This is an action for Pip, not a design item.** The relevant fact for this document is
**what there is to show her, and it is more than expected.**

`office_sandbox.gd` v4.1 is already a base-building toy: side-by-side small/large office
compare (the default view on open), prop placement on a first-class `RenderGrid` with
footprint occupancy, poster compositing, cat walk cycles, scummy/decent/premium quality tiers,
promoted-asset loading. It runs today from `godot/scenes/ui/office_floor/office_sandbox.tscn`.
Its header says *"It is a DEV TOOL and NEVER ships to players"* -- that is a scoping note, not
a rule, and no ADR forbids shipping it as an unranked mode.

**What she cannot be shown, and it should be said up front so the feedback is useful:**
ADR-0018 forecloses the cozy-sim payoff loop. Placement earning a bonus is one of the two
named rot modes: *"Command availability conditioned on placement -- e.g. 'the coffee pot is
only usable if it has been placed in the kitchen.' Same failure: a spatial fact ... is gating
a sim action."* And #1229: *"An 'XCOM base view' in the sense of placing rooms to get effects
is ruled out today."* The doctrine has a **review clause dated 2027-07-27** and that review is
where a spatial model gets re-litigated. So the honest question for Aileen is: *what makes a
base-builder satisfying when arrangement is pure expression and never pays?* That is a sharper
question than "what would make it better", and it is answerable.

**Ladder verdict: DOES NOT FORK.** A sandbox mode that never instantiates `GameState`, never
starts `VerificationTracker`, and never reaches `game_over_screen.gd` has nothing to fork.
Reached from the main menu, it is `godot/scenes/` + `godot/scripts/ui/` only.

---

### M24-009 -- irregular floorplan, and the org form made visible

> *"Smaller irregular office floorplan to start, with a door and windows. Cosmetic differences
> between the for-profit and non-profit versions so decisions produce visual feedback.
> Constraint stated by Pip: should not be ladder- or epoch-breaking."*

**(a) Irregular floorplan.** `offices.json` already carries `floorplan.{size_label,
width_units, depth_units, desk_slots, meeting_rooms}` per tier and declares the whole block
render-only. "Irregular" means the render stops drawing a rectangle -- which needs either
richer floorplan data (a shape, door and window positions) or the renderer inventing it from
the existing units. `RenderGrid` (the ADR-0018 a(3)-lite amendment) is the approved
infrastructure for exactly this: *"a first-class integer grid type -- `Vector2i` col/row
addressing, footprint occupancy, snap -- is approved as render-layer infrastructure ... this
grid is explicitly not a pathfinding or simulation grid."*

**(b) For-profit / non-profit decor.** **`org_type` already exists as first-class state** --
`game_state.gd:205-208`:

```gdscript
# Org form (early-game choice, part of DQ-19 char/org creation): "nonprofit" | "for_profit".
var org_type: String = "nonprofit"
```

plus `game_config.gd:16`. So the render layer has something to key off today. Note the
architecture doc's older claim that *"typed reputation and org type aren't first-class
GameState fields yet"* is **stale on the org-type half**; the field is there and gates
instruments (`vc_equity` is for_profit-only).

This is #1202 item 5 verbatim -- *"there's one choice at the start of the game ... Right now
those choices are basically invisible ... you will start with slightly different decor"* --
and that issue already attaches the ladder constraint Pip restates here.

**Ladder verdict: DOES NOT FORK, with one line of care.**

- Reading `state.org_type` to pick a prop palette is a render-side read of sim-owned state:
  the ADR-0018 arrow pointing the right way (*"the sim owns counts and quantities; the render
  owns coordinates"*). Nothing flows back.
- Adding door/window/shape fields to `floorplan.*` in `godot/data/office/offices.json` is a
  `godot/data/` edit; it ships with `Ladder-Impact: none -- floorplan.* is render-only by
  `offices.json` `_sim_vs_render` and `office.gd:26-28`; the sim reads hire_cap`.
- **The forbidden version, stated so nobody drifts into it:** the moment desk count, door
  position or room shape is read by anything in `godot/scripts/core/`, it forks and it also
  breaks ADR-0018. `test_office_*` already pins that the sim reads `hire_cap`, never
  `desk_slots`.

---

## 3. Instants and interrupts -- the second action class

M24-006 is the only atom that proposes a new *rule*. Everything else proposes a new *picture*.

### 3.1 What the phrase collides with

**The game already has two decision speeds, and has since 2026-07-12.** ADR-0009 s3:

> *"Two decision speeds (MtG taxonomy, none of its machinery): Plan speed ('sorcery') -- only
> castable at the month boundary. Response windows ('instant') -- an event fires mid-month
> and, if a window opens, offers a costed menu: HANDLE from reserve (painless -- what
> insurance was for) - HANDLE by cannibalizing - DEFER - IGNORE."*

And DESIGN_PHILOSOPHY, On the turn: *"A turn is a plan you watch collide with reality. Two
decision speeds -- plan-time (sorcery) and interrupt-time (instant) -- over a resolution tick
(the day) that owns no routine decisions."*

**So the second class is not missing. What is missing is the player's ability to initiate at
that speed.** Today the world initiates and the player answers.

**"Costs no attention" is the part that fights the design.** Three standing rulings point the
other way:

1. **ADR-0011 point 1 and its T2 amendment.** *"No global AP pool. The pool illusion dies."*
   T2 (2026-07-28) *"deleted the AP pool outright -- no `action_points` field, no per-turn
   grant, no AP in any cost dict"*. A free action class is a second pool with a new name.
2. **ADR-0009 point 4.** *"Reserve is crisp. Unspent slack evaporates at month end. No banking
   ever. Overcommitting is a legal gamble."* Free instants let you overcommit and still
   answer, which removes the gamble.
3. **The restraint rule.** *"A mechanic that needs a new player-facing currency or panel has
   to prove it can't be a read/write on existing ones first."*

And the prior interrupt doc opened by boasting exactly this: *"`reserve` IS spare attention.
None of the variants below invents a resource."*

**This is a ruling Pip needs to make on purpose, not a detail.**

### 3.2 What the prior thinking already covered, so this does not duplicate it

`D:/Local_Code/coordination/DESIGN_2026-08-12_interrupt-resolution-variants.md` (304 lines,
seat AlsoBort). It answers a **different** question: *how does an incoming interrupt trade
against the already-committed queue?* Variants:

- **A -- day allocation.** Response quality decays with `a - d`; *"reserve has a shape, not
  just a size."* Most expensive by a distance, and *"it asks a new player to schedule before
  they understand what any of the actions do."*
- **B -- commit-order stack, unfinished LOST.** Nearly free to build; *"losing committed work
  outright is harsh, and it punishes the player who plans ambitiously -- which is the player
  you want."*
- **C -- commit-order stack, unfinished CARRIES.** Recommended: *"C, with reserve doing the
  graceful/degraded split."* `reserve >= cost` -> graceful; `reserve < cost` -> the choice;
  month ends unresolved -> carries, subject to expiry.

**Its two questions are still open and neither was ever ruled:** (1) A, B or C; (2) *"Does an
interrupt preempt the queue, or wait for the current action to finish?"* The document is
explicit: *"Not decided here on purpose ... with the standing instruction not to close one by
picking the convenient answer while building."*

What *was* ruled that evening, and **has shipped**, is the capacity side: the calendar and the
budget are different objects; attention stays 20; `godot/scripts/core/capacity.gd` is the
single derivation point, seed in the signature, returning a value **and a reason**. Its own
comment: *"The moment `value` stops equalling `modifiers.grant`, the ladder epoch must bump."*

**M24-006 is orthogonal to A/B/C.** A/B/C is about *the queue*. M24-006 is about *a second
hand of cards*. They interact, but answering one does not answer the other.

### 3.3 Three shapes for the instants tray

---

#### Shape 1 -- the tray is a re-presentation, not a new class

The instants panel shows the **currently open response window's** verbs (HANDLE from reserve /
HANDLE by cannibalizing / DEFER / IGNORE) as a persistent tray in the upgrades region instead
of a modal dialog. No new action ids, no new costs, no new sim surface.

| | |
|---|---|
| **Delivers** | The visual claim of M24-006 (a second UI area, a second class of thing), and the pause is already there because windows already pause |
| **Costs** | `godot/scripts/ui/` only. The tray must be registered as neither plan-only nor watch-only, which is the same lift M24-005(a) needs |
| **Does not deliver** | Player-initiated. Zero-cost. "Take effect on the day taken" -- that is already true of window responses |
| **Ladder** | **Does not fork.** Presentation of an existing menu |
| **Risk** | Pip may read it as not having built the thing he asked for. It is honest to say so up front |

---

#### Shape 2 -- instants are free because they are cosmetic

The tray holds render-local verbs that change nothing in the sim: open the delivery box, put
the kettle on, pet the cat, cycle a poster, move a plant. Free because free is true.

This is ADR-0018 rider (b) territory, which the ADR puts **outside its own scope**: *"a
render-local effect is input -> render only: no sim read, no sim write, nothing serialized,
nothing replayed. If an interaction never crosses into the sim, this ADR has nothing to say
about it."*

| | |
|---|---|
| **Delivers** | M24-005's own stated purpose exactly: *"Reinforces that some actions are trivial and cost no attention."* And M24-007's *"make it visible in-game that the player can cycle through them"* -- the cycler IS an instant |
| **Costs** | `godot/scripts/ui/`, `godot/assets/`, and a real pause button so the player can do it mid-month. Prop demand entries |
| **Does not deliver** | Any strategic weight. Nothing here changes a run |
| **Ladder** | **Does not fork, by construction.** This is the strongest verdict in the document |
| **Risk** | The tray teaches "instants are decoration". If Shape 3 later arrives, the player has learned the wrong lesson about that region of the screen |

---

#### Shape 3 -- a genuine second action class with sim effect

Real instants: named actions, playable at any paused tick, with real effects. The design work
is entirely in *what they cost*, because free-with-effect breaks the scarcity the game is
built on.

Four pricings, cheapest to build first:

| Pricing | Mechanism | Assessment |
|---|---|---|
| **Crisp reserve** | `MonthPlan.pay_from_reserve()` already exists (`month_plan.gd:339`) | **Reuses everything.** "Costs no attention" becomes true in the sense the player means -- it does not eat your PLAN -- and false in the sense the engine means. Preserves the reserve gamble. **This seat's pick** |
| **Money / an in-fiction resource** | Ordinary `costs` dict | Honest, but makes instants a cash lever, and cash is *"the game's most fungible resource"* (ADR-0012) |
| **A per-month instant budget** | New counter on `MonthPlan` | A new currency. Fails the restraint rule unless it proves it cannot be a read on the reserve |
| **Cooldown, no resource** | Timestamp per instant | Genuinely free, and genuinely a second pool -- the thing T2 deleted |

| | |
|---|---|
| **Delivers** | All of M24-006 |
| **Costs** | A real pause button; new action data; a new record type on `VerificationTracker` (the replay log entry shapes are `{"t","k":"a","id"}` and `{"t","k":"r","ev","ch"}` -- an instant played at tick 14 of turn 200 is neither); a resolution-order interaction with the unruled A/B/C question |
| **Ladder** | **FORKS. No version of this does not.** Three independent triggers from s3.1: new content reachable on existing seeds; new decision points in the recorded input stream; and state mutation at a new point in the turn, which shifts event gating and therefore the RNG stream |
| **Risk** | It lands on top of an unruled question (A/B/C) and an unbuilt one (#1223's *"what is the Action Queue once things take time?"*). Building it now builds it twice -- which is the exact reason #1223's own comment gives for not building queue tiles yet |

---

### 3.4 Recommendation

**Shape 2 now; Shape 1 folded into it; Shape 3 held for the next epoch cut.**

The argument, in order:

1. **Shape 2 is the only one Pip's own memo justifies.** M24-005's sentence *"Reinforces that
   some actions are trivial and cost no attention"* is a claim about *feel*, and cosmetic
   instants deliver that feel completely and truthfully. Free-because-cosmetic is the only
   free that does not cost the design something.
2. **Shape 1 is nearly zero marginal cost once Shape 2's tray exists** -- the same persistent
   region, one more thing rendered into it -- and it gives the tray a second population so it
   is not purely decorative.
3. **Shape 3 is blocked on two open questions and one missing button.** The A/B/C ruling, the
   #1223/#1044/#794 "what is the queue once things take time" design, and a real pause. Doing
   it before those is the double-build #1223 warns against.
4. **Shape 3 is the only one that forks**, and the constraint Pip set is that this work does
   not fork. Held for an epoch cut, it is fine; smuggled into a cosmetic release, it is the
   thing `check_ladder_bump.py` was armed to catch.

**Build the pause button regardless.** It is denylisted, cheap, unblocks Shape 2, makes the
speed dial coherent, and is the load-bearing prerequisite Pip's memo already assumes exists.

---

## 4. What cannot be done without forking the ladder

Plainly, and each with its trigger from `BUILD_VS_LADDER_VERSION_SPLIT.md` s3.1.

1. **Any instant with a real sim effect** (Shape 3, at any price). New content reachable on
   existing seeds; new entries in the recorded input stream; state mutation at a new point in
   the tick order.
2. **"Starting contacts" becoming sim state.** If M24-002's helpers seed a relationship roster
   the sim reads, every seed starts from a different position than it did last epoch.
3. **A browsing surface that moves SA off zero as a mechanic.** Either a new action, or a
   changed effect on `scout_read` -- both change what happens on a fixed seed.
4. **Changing any existing action's effect or cost** while keeping its id. Same input,
   different trajectory. This includes re-pricing `scout_read` to make browsing "the first
   real action" feel right.
5. **"Check bank account" costing anything.** A priced check is a new action competing for the
   attention budget.
6. **Anything sim-side reading the floorplan** -- desk slots, door position, room shape,
   adjacency. Forks the ladder *and* violates ADR-0018.
7. **Alpha players changing the sim inside a ranked run.** Not a fork so much as a
   counterfeit; the guard is `GameConfig.is_ranked_run()`, and #1134 records what happens
   without it.
8. **New or reordered event data.** Each qualifying `"random"` event consumes exactly one
   `randf()` in file order (`events.gd:185`), so event-content changes fork **every seed
   globally** -- not just runs that encounter them. Worth stating because M24-002/003 both
   want new narrative beats, and the temptation is to author them as events.
9. **A variable attention grant.** Already ruled and already commented in
   `capacity.gd`: *"The moment `value` stops equalling `modifiers.grant`, the ladder epoch must
   bump."* Flavour reasons are free; a different number is not.

**One asymmetry worth knowing.** Adding a new action *definition* to `godot/data/actions/*.json`
does not by itself change any existing run: `get_available_actions()` (`turn_manager.gd:907-918`)
and `is_action_unlocked()` (`actions.gd:89-128`) are pure and draw no RNG, and an unqueued
action never reaches `execute_action` or `record_action`. Old replays still verify. **This does
not exempt it** -- s3.1 #5 makes new reachable content a bump trigger on its own -- but it does
mean the fork is forward-only, which matters for sequencing an epoch cut.

---

## 5. Open questions for Pip

Each answerable in one line.

1. **Keys or phone -- is the phone deleted, or does it survive as the thing in your other
   pocket?** (`COLD_OPEN_SEQUENCE.md:153-156` parked "does the phone become the HUD"; keys
   answer it by deletion, but only if the phone actually goes.)
2. **Are the strangers' contacts flavour, or real?** Flavour is free; a starting relationship
   roster forks the ladder.
3. **M24-004, your own open question restated as a fork line: reveal-once (free),
   stale-until-checked (free, and a lying display), or priced (forks)?**
4. **Is browsing a promotion, or an icon?** The competition test says `scout_read` nests; the
   real problem may be that the scouting door is an unlabelled tile with no icon (#1202 item
   2).
5. **Do instants cost the crisp reserve, or nothing at all?** If nothing, T2's deletion of the
   AP pool is being partly reversed and that should be said out loud.
6. **Shape 1, 2 or 3 for the instants tray** (section 3.3), and if 3, held for an epoch cut or
   shipped now with a bump?
7. **A, B or C** from `DESIGN_2026-08-12`, still unruled, and does an interrupt preempt the
   queue or wait? Shape 3 cannot be designed around it.
8. **What stays resident on the persistent stage besides the office?** The 08-10 doc flags
   that if the calendar is also permanent, screen budget becomes the constraint on every panel
   built after it.
9. **Does the alpha sandbox ship as a main-menu entry, or stay editor-only for Aileen?** A
   menu entry is denylisted and cheap; it is also a surface that must never touch a ranked run.
10. **Is Reading 1 of M24-007 correct -- "find a use" means declaring demand pools, not
    inventing consumers for 2,687 assets?** If not, ADR-0019 needs an explicit amendment
    rather than a quiet exception.
11. **Does the event popup get an art channel?** It is the single unblock for the 8 stranded
    event plates, the stray cat (#1218 E), and every future KEYED vignette -- and it is
    engineering, not art.
12. **Do the 15 dossier portraits go on candidate cards now?** `patch_notes.json:216` already
    tells players they did.

---

## 6. The recommended slice

**One release. Nothing in it forks the ladder. Every item is on the cosmetic denylist or ships
with an honest `Ladder-Impact: none` line.**

The thesis of the slice: **give the office one job it does not have -- being the place where
your decisions land -- and give the player one free thing to do in it.** That is #1210's
missing confirmation channel and M24-005's stated purpose, and it is the smallest coherent
thing here that is worth playing.

| # | Item | Files | Why it is in the slice |
|---|---|---|---|
| 1 | **Lift `OfficeFloor` out of `WatchScreen`** into a region registered as neither plan-only nor watch-only | `main_ui.gd`, `watch_screen.gd`, `screen_mode.gd`, `main.tscn` | Already ruled by Pip (08-10 s3); named as a priority by #1202 item 4; it is the load-bearing change and everything else decorates it |
| 2 | **Build the real pause button** | `screen_mode.gd:98-104`, `game_manager.gd` playback loop | Prerequisite Pip's memo assumes exists; makes the speed dial coherent; unblocks item 4 |
| 3 | **Org-type decor**: `OfficeFloor` reads `state.org_type` and picks a prop/colour palette | `office_floor.gd`, `props_manifest.json`, prop art pulled from `art_source/` | #1202 item 5 verbatim; the ADR-0018 arrow pointing the right way; makes the one meaningful pregame choice visible for the first time |
| 4 | **A cosmetic instants tray** (Shape 2) in the upgrades region, persistent across both modes: 3-5 free render-local verbs, one of which cycles decor | `plan_screen.gd` or a new shared panel, `office_floor.gd` | Delivers M24-005's *"some actions are trivial and cost no attention"* truthfully; delivers M24-007's *"visible in-game that the player can cycle through them"*; gives item 2 a reason to exist |
| 5 | **Keys replace the phone** in the cold open, ending at the office door that item 1 then shows you | `cold_open_sequence.gd` (BEATS + the three phone panels), key art, `INTRO_VERSION` bump | The intro's last frame becomes the game's first frame. Requires new key art -- surface it as a generation request per ADR-0019 clause 5, never a placeholder |
| 6 | **Dossier portraits on candidate and employee cards** | hiring panel + roster row, `portraits/*_256.png` | 5.35 MB already in the pack; `patch_notes.json` already claims it; the highest value-per-line item in the whole document |

**Deliberately NOT in the slice, and why:**

- **Shape 3 instants** -- forks, and blocked on the unruled A/B/C question.
- **Browsing as a mechanic** (SA off zero, the AI News surface) -- forks, and it is a system,
  not a slice.
- **The event-popup art channel** -- right, valuable, unblocks a lot, but it is engineering in
  `event_dialog.gd` plus a schema field plus a demand slot, and it belongs with #1218 rather
  than with the opening.
- **Irregular floorplan geometry** -- wants `RenderGrid` work and floorplan data authoring;
  item 3 gets most of the visible payoff for a fraction of the cost.
- **The base-building alpha mode** -- it already runs as a dev toy. Show Aileen *that*, with
  the ADR-0018 constraint stated, before deciding whether it becomes a mode.

**One measurement to take before and after, so this is not judged on feel.** #1210's own
warning applies to this slice too: *"A surface that doubles when you stop hiding your own
error messages is a surface that had a long way to come, not one that has arrived."* The
question worth answering with the next unattended first-timer is #1210's first suggested
output: *"What must a player be able to do, and believe, by turn 10?"*

---

## Related

- `docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md` -- section 3 is the rule every verdict
  here is measured against; section 4.2a is the as-built gate
- `docs/game-design/decisions/ADR-0009-plan-months-two-speeds.md` -- the two decision speeds
- `docs/game-design/decisions/ADR-0011-effort-economy.md` -- Attention as the only founder
  currency; the crisp reserve
- `docs/game-design/decisions/ADR-0012-event-response-taxonomy.md` -- the four event classes
- `docs/game-design/decisions/ADR-0018-render-only-office-doctrine.md` -- the live constraint
  on everything office-shaped; riders (b) and (c) are the levers
- `docs/game-design/decisions/ADR-0019-pull-from-demand-asset-pipeline.md` -- the pack is a
  function of declared demand
- `docs/game-design/COLD_OPEN_SEQUENCE.md` -- the design the keys would replace
- `docs/game-design/DESIGN_PHILOSOPHY.md` -- On the turn, On the early game, On the hero and
  the office, On restraint
- `docs/design/UI_ARCHITECTURE_2026-08-06.md` -- Part A, the top-level rule
- `docs/design/FRESH_EYES_TEARDOWN_2026-08-06.md` -- the minute-by-minute walkthrough
- `D:/Local_Code/coordination/DESIGN_2026-08-10_calendar-and-persistent-stage.md` -- section 3,
  the persistent stage ruling
- `D:/Local_Code/coordination/DESIGN_2026-08-12_interrupt-resolution-variants.md` -- variants
  A/B/C, still unruled
- `D:/Local_Code/coordination/tools/atoms/memo_rulings_2026-08-24.jsonl` -- the source atoms
- Issues: #1210, #1202, #1223, #1218, #1141, #1229, #1044, #794, #1134
