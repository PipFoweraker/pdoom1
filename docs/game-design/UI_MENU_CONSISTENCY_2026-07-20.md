# UI Menu Consistency Pass -- 2026-07-20

Directional coherence audit of every menu/screen against the established visual
direction: warm-grime base + heavy-outline heft + deeper shadow
(`docs/art/reviews/2026-07-17-overnight-sweep.md`), palette = dark
indigo/doom-purple grounds + hand-sourced warm amber accent
(`docs/art/palette.json`, `docs/art/PALETTE_AND_DOOM_INTENSITY.md`).
This was a COHERENCE pass, not a redesign: colors and one texture swap only;
no layout or node changes anywhere.

## The shared retone vocabulary (applied consistently)

The single biggest off-style pattern was a slate-blue button stylebox set
(bg `Color(0.2,0.3,0.5)`, border `Color(0.4,0.5,0.7)`, bright-blue focus fill)
copy-pasted across five menu scenes plus ice-blue (`0.6,0.8,1`) section-header
labels. Blue is semantically reserved in the palette doc for "computers acting
up" (Axis B), not menu chrome. Replaced everywhere with palette values:

| role | old | new | palette source |
|---|---|---|---|
| button normal bg | 0.2,0.3,0.5 slate blue | 0.18,0.145,0.278 (#2E2547) | doom-indigo (palette.json) |
| button normal border | 0.4,0.5,0.7 light blue | 0.09,0.04,0.11 (#170A1C) | deep aubergine = heavy dark outline (the sweep's "heavy-outline heft") |
| button hover bg | 0.3,0.5,0.8 | 0.231,0.192,0.349 (lightened indigo) | -- |
| button hover border | 0.7,0.8,1 | 0.91,0.64,0.24 (#E8A33D) | cozy amber -- accent appears on interaction |
| button pressed bg | 0.15,0.25,0.4 | 0.106,0.078,0.165 (#1B142A) | darker indigo |
| pressed/focus border | 0.9..1 white-blue | 0.965,0.659,0 (#F6A800) | amber UI token (glow_cat "the ONLY saturated accent") |
| focus bg | 0.4,0.6,1 bright blue FILL | same as normal bg + 3px amber border | keeps keyboard-nav visible without a loud fill |
| section-header labels | 0.6,0.8,1 / 0.4,0.8,1 ice blue | 0.91,0.64,0.24 cozy amber | amber CRT header register |
| screen titles | 0.86,0.94,1 ice white | 0.914,0.949,0.949 (#E9F2F2) | off-white text neutral |
| modal panel bg | bluish/neutral grays | #170A1C / #1B142A | dread grounds |
| modal panel border | 0.3-0.4,0.5-0.6,0.7-0.8 blue | 0.91,0.64,0.24 @ 0.8 alpha | amber frame on the active modal |

Rationale for border direction: the sweep ruling is heavy-OUTLINE heft, so
resting buttons get a near-black aubergine outline (dark outline around a
raised indigo fill) and amber only appears on hover/press/focus and on modal
frames. This keeps the "one saturated accent" lighting discipline.

## Menu-by-menu audit (ranked by visual impact)

### 1. Welcome / main menu (`godot/scenes/welcome.tscn`) -- WAS most off-style, RETONED
- Background: `tex_grid_circuit_trace_512` -- verified warm brown grime +
  verdigris traces; ON-style, kept.
- Overlay: WAS `tex_green_scanlines_512` at 0.15 alpha -- green reads
  Matrix-terminal and green is reserved for "computers OK" semantics.
  SWAPPED to `tex_amber_scanlines_512` (existing asset, same folder) -- the
  amber CRT glow is the brand accent. APPLIED.
- Buttons: full slate-blue set -> shared retone vocabulary. APPLIED.
- WhatsNewButton light-blue font trio -> amber trio. AISafetyButton blue trio
  -> teal `#1EC3B3` trio (palette "UI action" token; keeps the external-link
  differentiation without blue). APPLIED.
- Title/Subtitle plain white/gray: fine. Emoji glyphs in two button labels
  ("trophy", "link") render from system font -- style question, flagged below.

### 2. Pregame setup (`godot/scenes/pregame_setup.tscn`) -- RETONED
- Background `tex_bakelite_cracked_512` -- verified dark warm brown, very
  close to Warm panel #2B221A; the MOST on-style menu background. Kept.
- Amber scanline overlay already on-style. Kept.
- Slate-blue styleboxes + 4 ice-blue field labels -> shared retone. APPLIED.
- Note: LaunchButton deliberately uses the hover box as its normal state --
  after retone this gives the primary CTA a lighter fill + amber border at
  rest. Reads as intended emphasis; kept the pattern.

### 3. Settings (`godot/scenes/settings_menu.tscn`) -- RETONED
- Background `tex_painted_metal_panel_512` -- verified sage-green peeling
  paint; institutional-grime, green-leaning but within the grime family.
  Kept (borderline -- see flags).
- Gray dither overlay: neutral, kept.
- Slate-blue styleboxes + 6 ice-blue section headers + ice title -> shared
  retone. APPLIED.
- Sliders/OptionButtons/CheckButtons are default Godot theme (gray) -- see
  cross-cutting flag on a shared Theme resource.

### 4. Pause menu (`godot/scenes/pause_menu.tscn`) -- RETONED
- Panel was bluish-dark bg + 3px blue border -> deep aubergine bg (0.96 a) +
  dimmed amber border. Title + "Audio Settings" header retoned. APPLIED.
- Buttons are default-theme gray: flagged (shared Theme), not changed.

### 5. Player guide (`godot/scenes/player_guide.tscn`) -- RETONED
- Flat bluish-gray ColorRect background -> deep aubergine #170A1C; panel
  bluish-navy -> #1B142A + dimmed amber border; 4 blue section titles ->
  amber; back-button styleboxes -> shared retone. APPLIED.
- The RichTextLabel bodies use raw bbcode color names (green/red/cyan/
  purple/yellow/blue) as resource-name coding. Semantically load-bearing
  (matches researcher dot colors), so NOT touched -- flagged for a later
  pass to swap named colors for palette hexes.

### 6. What's New modal (`godot/scenes/ui/whats_new_modal.tscn`) -- RETONED
- Navy panel + steel-blue border + blue button + blue version label -> aubergine
  panel, amber frame, indigo/amber button, amber version line. APPLIED.

### 7. Bug report panel (`godot/scenes/ui/bug_report_panel.tscn`) -- RETONED
- Neutral-gray panel + blue border -> aubergine + dimmed amber frame. APPLIED.
- Form controls (LineEdit/TextEdit/OptionButton/CheckBox) default-theme; flagged.

### 8. Main in-game HUD (`godot/scenes/main.tscn` + runtime styling) -- LIGHT TOUCH
- Much of the in-game look is applied at runtime and is ALREADY on-doctrine:
  `scripts/ui/terminal_theme.gd` defines the amber-PLAN/green-WATCH CRT
  register (AMBER 1,0.72,0.2), `main_ui.gd` sets the TopBar title to
  TerminalTheme.AMBER. Scene-level stragglers unified to that register:
  - TurnLabel yellow (0.9,0.9,0.3) + yellow-bordered TurnCounter box ->
    TerminalTheme amber (1,0.72,0.2) + aubergine box bg. APPLIED.
  - Instrument "P(DOOM)" title (1,0.6,0) -> (1,0.72,0.2). APPLIED.
  - EndTurnButton cyan (0.2,0.9,0.9) -> teal token #1EC3B3. APPLIED.
- Left alone: doom number red, roster/queue hint grays (neutral), category
  colors from theme_manager (gameplay-legibility coding, not chrome).

### 9. Plan screen (`godot/scenes/ui/plan_screen.tscn`) -- LIGHT TOUCH
- CommandLabel violet (0.6,0.5,0.8) and PassButton lavender text (0.8,0.7,1):
  purple is doctrine-reserved for band 3+ eldritch; a resting menu label
  should not spend it. Retoned to TerminalTheme AMBER_DIM (0.66,0.48,0.16)
  and TEXT (0.82,0.86,0.78). APPLIED. (If the lavender was an intentional
  "weird command" joke, revert is one line -- noted for Pip.)
- Green tip hint kept (green = OK register).

### 10. Leaderboard (`godot/scenes/leaderboard_screen.tscn`) -- FLAGGED ONLY
- Background `tex_oxidized_copper_512` -- verified green verdigris circuit
  motif + cyan ISPF overlay: the most green/cyan-leaning menu ground. It IS
  grimy, but a warmer ground (bakelite/plywood) would match the register
  better. Subjective texture call -> needs Pip's eye.
- ALL buttons/panel are default Godot theme (no styleboxes at all) -- the
  screen looks unthemed next to the retoned menus. Fix belongs in a shared
  Theme resource (below), not another copy-paste set. No changes applied.
- Emoji trophies in the title label: style call, flagged.

### 11. Keybind screen (`godot/scenes/keybind_screen.tscn`) -- FLAGGED ONLY
- Zero styling: no background, default-theme buttons/dropdowns on the clear
  color. Reads as a debug screen. Needs the menu background+overlay pattern
  (suggest bakelite or concrete + amber scanlines) and the shared button set
  -- structural additions, so flagged rather than done.

### 12. Game over (`godot/scenes/ui/game_over_screen.tscn` + `.gd`) -- OK / minor
- Styled at runtime: dark panel (0.10,0.12,0.15,0.98) with a sage border,
  green title for wins / red for losses. Semantically sound (win/lose coding);
  panel tone is bluish-neutral rather than aubergine -- one-line candidate in
  `game_over_screen.gd:33-35` but it is script code, so left for Pip/next lane.

### 13. Staff perks panel + compact (`godot/scenes/ui/staff_perks_*.tscn`) -- DELIBERATE REGISTER, kept
- Coherent internal green-phosphor terminal identity (dark-green panels,
  green/blue/gold/purple tier coding). Green = "computers OK" fits doctrine;
  tier colors are information coding. Left untouched; if Pip wants these
  pulled toward aubergine-ground later it should be one deliberate re-skin.

### 14. Employee screen / watch screen / office cat / doom meter / fanfare / debug overlay -- OK
- Mostly default containers styled at runtime (employee_screen.gd,
  watch_screen.gd via TerminalTheme, doom_meter.gd draws via
  ThemeManager.DOOM_STOPS ramp -- the single doom source of truth). Debug
  overlay is developer chrome; intentionally unthemed. No changes.

### 15. Ledger + submenus (script-driven, no .tscn) -- OK / minor
- `submenu_chrome.gd` styles submenu panels (0.12,0.13,0.16,0.97 + gray-green
  border) -- near-neutral, mildly bluish; acceptable. The ledger has its own
  leather look (explicitly protected from chrome clobbering in
  `submenu_chrome.gd:37`). Script-side retones left for a code lane.

## Applied changes (complete list)

- `godot/scenes/welcome.tscn` -- overlay green->amber scanlines (line 5);
  4 styleboxes retoned (lines 7-53); WhatsNew font trio -> amber (214-216);
  AISafety font trio -> teal (227-229).
- `godot/scenes/settings_menu.tscn` -- 4 styleboxes (7-53); title (102);
  6 section headers (blue->amber, replace-all).
- `godot/scenes/pregame_setup.tscn` -- 4 styleboxes (7-53); title (114);
  4 field labels (blue->amber, replace-all).
- `godot/scenes/config_confirmation.tscn` -- 4 styleboxes (5-51); background
  ColorRect -> #170A1C (69); title (108); 5 row labels (blue->amber).
- `godot/scenes/player_guide.tscn` -- 3 button styleboxes + panel stylebox
  (5-51); background ColorRect -> #170A1C (69); title (101); 4 section
  titles (blue->amber).
- `godot/scenes/pause_menu.tscn` -- panel stylebox -> aubergine+amber (5-11);
  title (57); Audio header (75).
- `godot/scenes/ui/whats_new_modal.tscn` -- panel + button styleboxes (5-27);
  title (76); version label (83).
- `godot/scenes/ui/bug_report_panel.tscn` -- panel stylebox (5-11).
- `godot/scenes/main.tscn` -- TurnCounter stylebox (17-23); TurnLabel font
  (74); instrument P(DOOM) title (192); EndTurnButton font -> teal (365).
- `godot/scenes/ui/plan_screen.tscn` -- CommandLabel violet -> AMBER_DIM (51);
  PassButton lavender -> terminal text (58).

## Needs Pip's eye (NOT changed)

1. `godot/theme/welcome_theme.tres` -- unused (only referenced from
   `godot/docs/README.md`) AND malformed: Theme styles are written as inline
   dictionaries, which Godot does not parse into StyleBoxes. Recommend delete
   or rebuild as the real shared Theme (next item).
2. A real shared `Theme` resource. The same stylebox set now exists as five
   per-scene copies (was already true pre-pass); sliders, dropdowns,
   checkboxes, and the leaderboard/keybind/pause/game-over buttons all fall
   back to default gray. One `menu_theme.tres` applied at the root of each
   menu scene would kill the duplication and theme the stock controls.
   Structural, so not done in this pass.
3. Leaderboard background/overlay (verdigris+cyan) -- swap toward a warm
   ground, or embrace it as the "institutional records" room? Taste call.
4. Keybind screen -- needs the full menu treatment (background, overlay,
   buttons); additive work.
5. Emoji in labels (welcome "Leaderboard"/"AI Safety Info", leaderboard
   title, submenu close glyph) vs the ASCII-flavoured look elsewhere
   ("[M]", ">>", "[ESC] close").
6. Script-side stragglers for a code lane: `game_over_screen.gd:33-35` panel
   tone; `submenu_chrome.gd:26-28` submenu panel tone; player-guide bbcode
   named colors; `theme_manager.gd` `apply_button_style()` "Style Guide"
   STEEL_DARK/ELECTRIC_BLUE/NEON_MAGENTA block (predates the palette doc --
   any runtime-created button still gets electric blue + neon magenta; high
   leverage but touches game code, so left).
7. Settings background (sage peeling paint) -- kept, but it is the
   greenest-leaning of the kept grounds.
8. plan_screen "Do Nothing" lavender -- retoned to the amber register per the
   purple-is-expensive rule; revert `godot/scenes/ui/plan_screen.tscn:51,58`
   if the lavender was a deliberate gag.
