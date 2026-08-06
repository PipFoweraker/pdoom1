# Navigation audit + the seven principles

Issue #602 asked for a PRINCIPLE, not four patches. This file is that principle, plus
the map it was derived from. It exists because #565, #567 and #575 are not three bugs --
they are three sightings of the same two generators, and the four issues had sat open
since 2026-07-22 precisely because each was treated as a one-off and the class was never
enumerated.

**Status:** audit performed 2026-08-04 against `origin/main` at `d0cf8e30`.
**Executable half:** `godot/tests/unit/test_navigation_principles.gd` and
`godot/tests/unit/test_dialog_key_routing.gd`. A future PR is checked against the
principles by those tests, not by re-reading this file -- that is deliberate, and is the
same anti-rot pattern as the generated `DQ_INDEX.md` (the stale `decisions/README.md` is
the failure mode being avoided).

---

## The two generators

Everything below reduces to these. If a new navigation defect does not, it is worth
writing down, because it is a third generator.

**G1 -- Two lists that must agree, with nothing forcing them to.**
The key a button ADVERTISED and the key the router ACCEPTED lived in six unrelated
arrays: `event_dialog.gd`, three entries in `submenu_controller.gd`'s `GRID_CONFIG` plus
a fourth in its financing builder, `travel_panel_controller.gd`, and
`MainUI._dialog_button_index_for_key`. Nothing tied them together, so they drifted, some
were truncated, and one panel advertised numbers while its siblings advertised letters.
#567 is one sighting. So is the blank `[] ` prefix on a 5th grid option that a working
but undiscoverable key still fired.

**G2 -- A key handled without asking who is listening.**
A global `_input` that reads a keycode before checking whether a text field has focus
eats the character the player is typing (#575's bug-report half). A hotkey that opens a
panel without asking whether that panel is already open cannot close it (#602's mirrored
toggles). A bind listed in the rebind screen that no handler ever names is the same
mistake inverted -- a listener that does not exist (`menu_research`, `cancel`,
`next_tab`/`prev_tab`, `action_1..9`).

---

## The seven principles

Stated so a PR can be checked against them.

### P1 -- Nothing is hotkey-only.
Every screen, panel or feature reachable by a hotkey is ALSO reachable by a visible
control. A hotkey is an accelerator for something the player can already see, never the
sole door.
*Sightings:*
- #565, Travel & Conferences reachable only by `T`. (Already fixed by the L9 data
  migration -- `travel` is a normal `is_submenu` entry in `data/actions/core.json` with no
  unlock gate -- but nothing was guarding it, so it could silently regress. Now guarded.)
- **The Settings screen, and with it the KEYBIND EDITOR, had NO door at all once a run was
  live.** `F10` was bound and consumed by nothing; the pause menu offered
  Resume/Resign/Save/MainMenu/Quit. A player who wanted to rebind a key had to abandon
  their run to reach the screen that rebinds keys. Fixed both ways: a visible
  "Settings & Keybindings" button on the pause menu, and `F10` actually wired.
- The Employee screen's `_on_employee_tab_button_pressed` is a dead `pass` and
  `tab_manager.gd`'s `E`-key path is commented out. The screen IS reachable (a code-built
  button, `main_ui.gd:300`), so this is dead code rather than a live defect -- left alone
  and recorded.
- `debug_overlay` (`F3`) has no visible affordance. ACCEPTED: a debug surface is not a
  player feature, so P1 does not bind it. Recorded so the next audit does not re-find it.
- `welcome_screen.gd:82` -- the "Load Game" button ships `visible = false` and
  `disabled = true` while `_on_load_game_pressed` still serves it. Not navigation; left
  for whoever owns save/load.

*Pinned by:* `test_every_hotkey_submenu_is_also_in_the_action_bar`,
`test_hotkey_submenus_are_not_hidden_from_the_action_bar`,
`test_travel_is_unlocked_from_the_first_turn`,
`test_settings_is_reachable_mid_run_by_a_visible_control`.
*Mechanical half:* both doors call ONE function (`MainUI._open_submenu`), so a panel
reached by key and a panel reached by click are the same panel in the same state.

### P2 -- A key that opens a panel closes it.
Menu hotkeys are TOGGLES. Pressing the key while its own panel is up closes that panel.
Pressing it while a DIFFERENT modal is up does nothing -- the key is still consumed, so a
hotkey can never stomp the panel the player is looking at, and an unanswered event dialog
stays unanswerable-away (#452).
Identity is read from the panel's own `submenu_id` meta, never from a remembered
"last opened" variable, so the toggle cannot desync from the scene tree.
*Sightings:* #602. `L` already behaved this way (#601); `H`/`F`/`P`/`T` did not. Neither
did `N` -- the bug-report form opened and could not be closed by the key that opened it,
while `BugReportPanel.toggle_panel()` had existed unused the whole time. All five are
mirrored now.
*Pinned by:* `test_menu_hotkeys_go_through_the_mirrored_toggle`,
`test_both_doors_into_a_submenu_share_one_function`,
`test_bug_reporter_key_is_mirrored_too`.

### P3 -- A choice key is legitimate only if the button it fires is on screen AND carries that key's label.
One table (`godot/scripts/ui/dialog_keys.gd`) is read by every dialog builder to RENDER
and by the router to ROUTE. The router is bounded by the LIVE button count, so a key that
names no on-screen choice returns "no choice" instead of an out-of-range index.
Letters (`Q W E R A S D F Z`) are the advertised scheme everywhere; `1`-`9` remain
accepted as an unadvertised alias so an old habit is not punished, but nothing renders
them (outside a dialog those digits already mean "action-bar slot", so advertising them
inside one double-books the key).
*Sighting:* #567, "Key index 3 out of range" on `R` at a three-option event.
*Pinned by:* `test_letter_past_button_count_is_not_a_choice` (reproduces the exact index
3), `test_label_and_keycode_round_trip`, `test_no_producer_keeps_its_own_key_label_list`.

### P4 -- No advertised key is inert, and no working key is unadvertised.
Every key the game answers to is EITHER a rebindable action in `KeybindManager.keybinds`
OR a documented entry in `KeybindManager.RESERVED_KEYS`. Never neither (a working key the
rebind screen cannot show), never both.
A bind whose action name no handler ever mentions is a lie the settings screen tells: the
player rebinds it and nothing changes, or presses it and nothing happens and concludes the
game is broken.
*Sightings, all found by this audit and none of them named in the four issues:*
`menu_research` (`R`) bound with no research submenu to open; `cancel` (`ESC`) bound while
every ESC handler matched a raw keycode; `next_tab`/`prev_tab` (`TAB`) bound and handled
nowhere; `action_1..action_9` bound while `MainUI` matched a raw `KEY_1..KEY_9` range;
`SPACE`, `ENTER`, `N` and `V` handled as raw keycodes.
*Pinned by:* `test_no_keybind_action_is_inert`,
`test_dynamic_bind_families_are_actually_dispatched`,
`test_core_gameplay_keys_are_rebindable_not_hardcoded`,
`test_menu_research_stays_deleted`, `test_esc_is_reserved_not_falsely_rebindable`.

### P5 -- ESC goes back exactly one level, and never quits from a nested screen.
- From a modal: closes STRICTLY the topmost modal (`ModalStack.handle_escape()`), never
  one buried beneath it. An unanswered event dialog SWALLOWS ESC rather than letting it
  fall through to the pause menu behind a still-visible dialog (#452).
- From a full-screen sub-view (the Employee screen): returns to the view that opened it.
  `MainUI._input` returns immediately when `not visible`, so ESC there cannot reach the
  pause menu -- the #602 symptom.
- Only at the top level, with no modal up, does ESC open the game menu.

ESC is RESERVED: not rebindable, because a rebind lets a player strand themselves in a
modal with no way out.

*Sighting fixed here:* the rebind screen itself was the worst offender. With a rebind
pending it CAPTURED whatever key you pressed -- **ESC included** -- so the one screen whose
job is keys was the one place you could destroy the universal back key. With nothing
pending its `_input` returned early, so ESC did nothing at all on a full screen whose only
exit was a Back button. ESC now cancels a pending rebind, or goes Back.
*Pinned by:* `test_keybind_screen_cannot_swallow_esc_as_a_binding`.

*Sightings NOT fixed here* (recorded so they are inherited, not rediscovered):
- `cold_open_sequence.gd` has no ESC handler; the only escape is hold-SPACE or the skip
  button. ESC is inert on a full-screen cinematic.
- `welcome_screen.gd` has no ESC handler. Defensible at the root scene -- there is no "back
  one level" from the front door -- but it means ESC is inert on one top-level scene.
- `leaderboard_screen.gd:724` -- ESC calls the back handler, which `queue_free()`s the node
  when it is not the current scene root. The same key either navigates or self-destructs
  depending on how the screen was mounted.
- `settings_menu.gd` -- ESC exits to `main.tscn` when a run is live and `welcome.tscn`
  otherwise. Intentional and correct (it is still "back one level"), noted because one key
  with two destinations is worth being deliberate about.

### P6 -- Typed text outranks every global shortcut.
When a `LineEdit`/`TextEdit` owns GUI focus, every global handler returns BEFORE reading
any key (`KeybindManager.is_text_input_focused()`, consulted by the autoload's own
`_input` and as the first gate in `MainUI._input`). Half-applying this is how #575
survived: one handler that checks and another that does not still eats the characters.
Dialog choice buttons use `FOCUS_NONE` on purpose, so this gate never blocks a choice key.
`TAB` is RESERVED for Godot's GUI focus traversal -- no game action may bind it, or the
player cannot move between the bug-report form's fields.
*Pinned by:* `test_text_focus_gate_precedes_every_shortcut_in_main_ui`, and the
pre-existing `test_keybind_focus_gate.gd`.

### P7 -- Scene changes go through `SceneTransition`.
`SceneTransition.go_to()` / `.reload()`, never `get_tree().change_scene_to_file()`. A
direct call from inside `_input()` segfaulted the v0.11.0 release build. Restated here so
the audit is complete; enforced by `tools/check_scene_nav.py`, documented in
`docs/LEADERBOARD_CRASH_DIAGNOSIS.md`.

---

## The map

### Key bindings after this pass -- `godot/autoload/keybind_manager.gd` is the ONE source

Issue #1011 notes three docs disagree with `keybind_manager.gd`. **The file is right and
the docs are wrong**, in every case checked here. Settled:

| Key | Action id | What it does |
|---|---|---|
| `SPACE` | `end_turn` | End turn (with warnings). Also advances a one-option navigation popup that opted in via `space_advances` (PR #1100). |
| `ENTER` | `commit_plan` | Commit plan. Deliberately inert inside every dialog -- no meta can change that (#1100). |
| `Z` | `undo_action` | Undo last queued action |
| `C` | `clear_queue` | Clear the action queue |
| `V` | `toggle_view` | Toggle PLAN / WATCH (was a hardcoded `KEY_V`; now rebindable) |
| `L` | `open_ledger` | Liability Ledger -- mirrored toggle |
| `H` | `menu_hire` | Hiring pipeline -- mirrored toggle |
| `F` | `menu_fundraise` | Fundraising -- mirrored toggle |
| `P` | `menu_publicity` | Publicity -- mirrored toggle |
| `T` | `menu_travel` | Travel & Conferences -- mirrored toggle |
| `1`-`9` | `action_1`..`action_9` | Action-bar slots (now read through the binds, so a rebind takes) |
| `N` | `bug_reporter` | Open the bug reporter. **Not backslash** -- `CONTRIBUTING.md:213` is stale. |
| `F10` | `settings` | Settings menu |
| `F3` | `debug_overlay` | Debug overlay (all builds -- NOT dev-gated) |
| `[` | `screenshot` | Screenshot |
| `]` | `admin_mode` | Admin mode |
| `F12` | `export_log` | Export game log |
| `\` | `dev_mode` | Dev-mode overlay (dev builds only) |
| `F6` | `flight_recorder` | Flight recorder (dev builds only) |
| `F7` | `ui_evolution_shot` | UI evolution capture (dev builds only) |

**Reserved, deliberately not rebindable** (`KeybindManager.RESERVED_KEYS`):

| Key | Why |
|---|---|
| `ESC` | Universal back/close (P5). A rebind could strand a player in a modal. |
| `TAB` / `Shift+TAB` | Godot GUI focus traversal (P6). Claiming it breaks form navigation. |
| `Q W E R A S D F Z`, `1`-`9` inside a dialog | Positional choice labels rendered onto the buttons (`DialogKeys`), not standalone actions. |

**Deleted this pass, with the reason left in-file:** `menu_research`, `cancel`,
`next_tab`, `prev_tab`. `KEYBINDS_CONFIG_VERSION` bumped 5 -> 6 so saved configs refresh.

### Modal choice keys

| Panel | Advertised | Router sees | Producer |
|---|---|---|---|
| Event dialog | `[Q] [W] [E] ...` | same | `event_dialog.gd` via `DialogKeys.prefix_for` |
| Grid submenus (fundraise / publicity / strategic / office / scouting / operations) | `Q W E ...` | same | `submenu_controller.gd` via `DialogKeys.label_for` |
| Financing list | `[Q] [W] ...` | same | `submenu_controller.gd` via `DialogKeys.prefix_for` |
| Travel & Conferences | `Q W E` (**was `1 2 3`**) | same | `travel_panel_controller.gd` |
| Hiring pipeline | `[Q] [W] ...` on each candidate's PRIMARY button (**was nothing at all**) | same | `hiring_panel_controller.gd` |
| Month review popup | `[SPACE]` | `dialog_key_advances()` opt-in | `event_dialog.gd` (#1100) |

The hiring panel keys ONE button per candidate card -- Interview while anything is left to
learn, otherwise Make Offer -- and registers it whether or not it is disabled, so the
key-to-card alignment does not shift when a candidate becomes unactionable. `MainUI`
refuses to fire a disabled button, so a dead key is silent rather than wrong.

### Screens, entrances, exits

`SceneTransition` for every scene change (P7). Sub-views and modals live inside
`main.tscn`.

| Screen / panel | Entrances | ESC | Visible exit |
|---|---|---|---|
| Welcome (`welcome.tscn`) | app launch | -- (top level) | menu buttons |
| Pregame setup | Welcome -> New Game | back to Welcome | Back button |
| Main game (`main.tscn` / `MainUI`) | Pregame -> Start | opens the pause menu (top level, P5) | -- |
| Pause menu | ESC at top level | closes itself | Resume button |
| Employee screen (sub-view) | visible access button in `MainUI` (`main_ui.gd:300`) | `TabManager._input` returns to the main view, NOT the game menu | Back button |
| Submenu panels (hire / fundraise / publicity / travel / strategic / office / scouting / operations / financing) | action-bar button AND mirrored hotkey (P1, P2) | `ModalStack.handle_escape()` closes topmost | `[X]` close affordance |
| Liability Ledger | `L` (mirrored) + visible control | closes topmost | `[X]` |
| Event dialog | fired by the sim | SWALLOWED (#452 -- must be answered) | choice buttons only |
| Month review popup | end of month | closes topmost | primary button, or `SPACE` (#1100) |
| Bug report panel | `N` + visible button | closes the panel | Cancel / Submit |
| Settings | `F10` (**newly wired**) + Welcome + **pause menu button (new)** | back one level; keeps a live run via `pending_resume` | Back button |
| Keybind screen | Settings menu entry | cancels a pending rebind, else back to Settings (**both new**) | Back button |
| Leaderboard | Welcome + game-over | back one level | Back button |
| Player guide | Welcome menu entry | closes | Close button |
| Dev-mode overlay | `\` (dev builds only) | closes | the toggle key |

---

## What this pass did NOT fix

Named so the next lane inherits a list, not a surprise.

- **`BuildInfo.DEV_BUILD` is a hand-flipped constant** (#1011 section 3). Backslash opens
  the full dev overlay in whatever build ships, and nothing verifies which. Out of scope
  here: a release-process gap, not a navigation one.
- **The keybind artifact** (#1011 section 2) -- emitting `keybinds.json` per release so
  the website derives instead of mirroring. This audit settles WHAT is true; emitting it
  is the follow-up. The stale doc references (`CONTRIBUTING.md:213` says backslash opens
  the bug reporter; it is `N`) are listed in #1011 and belong in a docs PR, not this one.
- **`ModalStack` is documented as the ONLY writer of `active_dialog`, and it is not.**
  `hiring_panel_controller.gd` and several sibling builders still assign
  `host.active_dialog` directly just before calling `_present_modal_dialog`, which reads
  those writes back. `main_ui.gd` acknowledges this ("that shape is preserved so ~10
  builders across four files stay untouched"). It works, but the bug class #877 was
  written to kill is only structurally impossible once the assignment is removed. That is
  a real refactor, deliberately not smuggled into a keyboard fix.
- **`MainUI._unhandled_input` duplicates the choice-key routing** already done in
  `_input`. It now reads the same shared table, so the two cannot disagree, but it is
  still a second dispatch site for one decision.
- **Multi-site dispatch generally.** ESC is handled in ten places (`main_ui.gd` twice,
  `pause_menu`, `tab_manager`, `modal_stack`, `esc_to_close`, `staff_perks_panel`,
  `fanfare_popup`, `bug_report_panel`, `flight_recorder`); submenus are registered in
  `ModalStack` AND separately given an `EscToClose` (`submenu_chrome.gd:75`), so two
  closers are deconflicted only by `set_input_as_handled` ordering. SPACE has seven
  handlers, ENTER seven. None of this is broken today -- each site guards on its own
  visibility -- but it is the substrate every future ESC bug will grow in, and P5 is only
  cheap to verify once `ModalStack.handle_escape()` is the sole in-game closer.
- **No raw scene changes exist.** The full sweep found `change_scene_to_file` only inside
  `scene_transition.gd` itself. P7 is currently clean.
