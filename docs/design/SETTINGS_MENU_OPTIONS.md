# Settings Menu: Five Directions

Requested by Pip in the 2026-08-01 playtest recording [12:14]-[12:39]:
"give me like five different sets of UI options for all of the settings
menus, then let me pick through them... I'm not constrained by effort,
I'm constrained by CHOICE."

This is a menu of directions, not a recommendation. Pick, mix, or reject.
No game code was touched. Verified against the shipped 0.13.2 frame
(`art_generated/audiodump/frames_2026-07-31_18-09-46/f019_153s.jpg`),
`godot/scenes/settings_menu.tscn`, `godot/scripts/ui/settings_menu.gd`,
`godot/autoload/game_config.gd`, `godot/UI_STYLE_GUIDE.md`.

---

## 0. What the code actually says (read this first -- it changes the problem)

The screenshot problem is NOT missing content. It is a layout bug hiding
content that already shipped.

1. **Every section already exists.** The .tscn contains Audio (3 sliders),
   Graphics (quality + fullscreen), Gameplay (difficulty + 4 code-injected
   toggles: leaderboard consent, launch ping, story intros, hints), UI
   (theme + experimental layout A/B), Accessibility (colorblind), and a
   Keyboard Shortcuts reference grid.
2. **Why you only see three sliders:** in `settings_menu.tscn`, both
   `Scroll` (the settings viewport) and the empty `Spacer` below it have
   `size_flags_vertical = 3` (expand). They split the leftover height
   50/50, so ~200px of scroll window shows the content while an equally
   tall EMPTY spacer sits under it. "Graphics Settings" is the last header
   that fits above the fold; everything else scrolls inside the tiny
   window. The whole menu is hostage to one flag on one node.
3. **The root VBox is hard-sized 800x600, centered.** On a 1080p+ window
   the rest of the screen is raw tiling texture. This is the second half
   of the empty-space problem.
4. **Graphics Quality is a placebo.** `GameConfig.apply_graphics_settings()`
   only applies fullscreen; quality is a literal `# TODO`. The dropdown
   saves a number that changes nothing.
5. **"Research Intensity" (difficulty) in Settings undermines #1058.**
   Pregame locks difficulty to Standard for the league; the Settings
   dropdown still freely writes `GameConfig.difficulty`. Pregame re-locks
   it on entry so the damage is limited, but the row is at best dead UI
   and at worst a confusing lock bypass. Every proposal below drops it
   from Settings (difficulty is a per-run choice, made at pregame).
6. **The Keyboard Shortcuts grid is static text and appears stale.** It
   advertises `[F5] Quick save` / `[F9] Quick load`; no `KEY_F5` binding
   exists anywhere in `godot/scripts`, and the only `KEY_F9` handler is a
   debug-build-only UI-layout flip in `main_ui.gd` [verify in a build].
   Meanwhile a real Keybindings screen (`keybind_screen.tscn`, with
   profiles and rebinding) exists as a SEPARATE top-level menu entry.
   Silent wrongness of exactly the flavour league week taught us to fear.
7. **Apply is a trap.** Every control applies live via
   `set_setting(..., false)`; the Apply button only does `save_config()`.
   Back without Apply = settings work for this session, then silently
   revert on next launch. Standard player mental model ("it changed, so
   it's saved") loses data here.
8. **Settings with NO reachable UI anywhere:** `baseline_mode` (Auto /
   Eager / Blind baseline computation -- read by GameManager, set nowhere).
9. **Settings with UI only OUTSIDE the settings menu:** `show_rivals_feed`
   (WATCH-screen filter button only), theme also persists in ThemeManager's
   own cfg file, keybindings (own screen).
10. Not settings, despite living in config: `dismissed_update_version`,
    `welcome_seen`, `last_seen_*`, `games_played`, `leaderboard_reminder_shown`
    -- state flags. No proposal exposes them (except as a "reset onboarding"
    action, noted where relevant).

### The true player-facing inventory (from `game_config.gd` + ThemeManager)

| Setting              | Backing field           | Today's UI                  |
|----------------------|-------------------------|-----------------------------|
| Master volume        | master_volume           | settings (visible)          |
| SFX volume           | sfx_volume              | settings (visible)          |
| Music volume         | music_volume            | settings (visible)          |
| Fullscreen           | fullscreen              | settings (below fold)       |
| Graphics quality     | graphics_quality        | settings (below fold, NO-OP)|
| Colorblind mode      | colorblind_mode         | settings (below fold)       |
| Visual theme         | ThemeManager            | settings (below fold)       |
| Story intros         | play_intros             | settings (injected, fold)   |
| Gameplay hints       | show_hints              | settings (injected, fold)   |
| Rival intel feed     | show_rivals_feed        | WATCH screen only           |
| UI layout A/B        | ui_layout               | settings (injected, fold)   |
| Leaderboard identity | submit_scores_global    | settings (injected, fold)   |
| Launch ping (anon)   | send_launch_ping        | settings (injected, fold)   |
| Baseline mode        | baseline_mode           | NONE                        |
| Keybindings          | keybind profiles        | separate screen             |

Shared assumptions in all five directions:
- Difficulty row removed from Settings (per-run, pregame owns it).
- Quality dropdown either wired or labelled "(not yet wired)" -- never
  silently fake.
- Apply button dies: changes save on change (or on exit). One honest rule.
- `show_rivals_feed` gains a Settings row (it is a persisted preference;
  players will look for it here).
- ASCII chrome per house style; amber stays in its existing menu-chrome
  register (headers, hover/focus) -- no new third meaning for amber.
- Keybindings reachable FROM settings (one link), whatever else happens.

---

## Direction 1: OPERATIONS BOARD

**Thesis:** A settings screen is an instrument cluster -- every control
visible at once, zero navigation, and density IS the aesthetic (the style
guide's Bloomberg-terminal / NATO-C2 register, finally applied to the one
screen that never got it).

### Wireframe (1080p; single screen, no scrolling)

```
+------------------------------------------------------------------------------+
|  LAB OPERATIONS // SETTINGS                                v0.13.2  board L3 |
|  changes apply immediately and are saved -- there is no Apply button         |
+------------------------+---------------------------+-------------------------+
|  AUDIO                 |  OPERATIONS               |  DISCLOSURE             |
|                        |                           |                         |
|  Master   50%          |  Story intros      [ON ]  |  Global leaderboard     |
|  [========-------]     |  Gameplay hints    [ON ]  |  submits player + lab   |
|                        |  Rival intel feed  [ON ]  |  name publicly          |
|  Effects  50%          |                           |            [OFF] opt-in |
|  [========-------]     |  INTERFACE                |                         |
|                        |                           |  Anonymous launch ping  |
|  Music    13%          |  Theme     < Default   >  |  installs count only    |
|  [==-------------]     |  UI layout A/B     [OFF]  |            [ON ]        |
|                        |  (experimental; next run) |                         |
|  DISPLAY               |                           +-------------------------+
|                        |  ACCESS                   |  CONTROLS               |
|  Fullscreen    [OFF]   |                           |                         |
|  Quality  < Medium >   |  Colorblind mode   [OFF]  |  >> KEYBINDINGS         |
|  (quality not wired    |  patterns + symbols       |  edit all bindings and  |
|   yet -- no effect)    |  alongside colors         |  profiles               |
+------------------------+---------------------------+-------------------------+
|  [ESC] back      [K] keybindings      [R] reset to defaults      saved 3s ago|
+------------------------------------------------------------------------------+
```

### Grouping and why
Three columns by QUESTION the player is asking, not by engine subsystem:
- Col 1 "my machine" (audio, display) -- the things you touch in minute one.
- Col 2 "my game" (operations = what the game shows you; interface; access).
- Col 3 "my data + my hands" (privacy gets its OWN header at last --
  identity consent buried under "Gameplay" is how consent gets missed --
  plus the keybindings jump-off).

### Empty space / empty Graphics section
Solved by construction: the board fills the frame edge-to-edge; the
texture only survives as thin gutters between panels. Nothing scrolls, so
nothing can hide below a fold. The Graphics section stops being empty
because everything is always on screen.

### Trade-offs
- Worst at growth: at ~20+ settings the board must shrink fonts or go to
  a fourth column; this design bets the settings count stays modest.
- Dense screens intimidate the players who only came to turn music down.
- Needs real layout work (three balanced columns responsive to window
  size), not just flag fixes.
- Effort: ~8-12h (new .tscn layout, kill Apply, add rivals row, status
  strip, remove difficulty row; logic mostly reused).

### Who it is for
The league grinder and the tinkerer -- players who visit settings often,
know what they want, and resent clicks. Also the game's own brand: this
is the direction that makes Settings look like the rest of P(Doom) wants
to look.

---

## Direction 2: PROTOCOL TABS

**Thesis:** Players arrive pre-trained by every PC game of the last 15
years; the fastest settings UI is the one they have already used a
thousand times -- a left rail of categories, one roomy page at a time.

### Wireframe

```
+------------------------------------------------------------------------------+
|  SETTINGS                                                    [ESC] back      |
+----------------+-------------------------------------------------------------+
|                |                                                             |
|  > AUDIO       |   AUDIO                                                     |
|    DISPLAY     |                                                             |
|    GAMEPLAY    |   Master volume                                     50%     |
|    INTERFACE   |   [===============--------------]                           |
|    PRIVACY     |   everything the game plays                                 |
|    CONTROLS    |                                                             |
|                |   Sound effects                                     50%     |
|                |   [===============--------------]                           |
|                |   clicks, alerts, event stingers                            |
|                |                                                             |
|                |   Music                                             13%     |
|                |   [====-------------------------]                           |
|                |   adaptive score; ducks under alerts                        |
|                |                                                             |
|                |                                                             |
|                |                                                             |
+----------------+-------------------------------------------------------------+
|  changes save automatically                          [R] reset this page     |
+------------------------------------------------------------------------------+
```

Tab contents: AUDIO (3 sliders) / DISPLAY (fullscreen, quality, theme) /
GAMEPLAY (intros, hints, rival feed) / INTERFACE (UI layout A/B; future
UI scale) / PRIVACY (leaderboard identity consent with its full honest
sentence, launch ping) / CONTROLS (embeds or links the keybind screen --
the existing static shortcuts grid is deleted, ending the F5/F9 drift).

### Grouping and why
One category per rail entry, 2-4 items per page. The rail IS the table of
contents: a player scanning for "where do I turn off score submission"
reads six words and knows. PRIVACY as a first-class tab is the point --
it is the group players go hunting for angriest, and today it is invisible
inside "Gameplay".

### Empty space / empty Graphics section
Each page holds few items, so pages are designed AROUND whitespace: every
row gets a one-line caption (the caption text is already written -- it
lives in code comments and tooltips today). Remaining space is honest
panel, not accidental void. No section can be empty because a tab with no
content does not get a rail entry.

### Trade-offs
- Slowest to a specific setting if you guessed the wrong tab (is theme
  DISPLAY or INTERFACE? -- needs one judgment call and a cross-link).
- Six navigation clicks to audit everything; bad for the "check all my
  privacy toggles" sweep.
- Most total surface to build: rail + page container + 6 pages.
- Effort: ~10-14h (rail component, per-page scenes or a data-driven page
  builder, captions, embed/link keybinds).

### Who it is for
The general Steam player and the first-week player -- least learning
required, most familiar shape. Also the direction that scales best if the
settings count doubles.

---

## Direction 3: THE LAB FLOOR (diegetic)

**Thesis:** This IS a laboratory -- settings should read as equipment on
the wall, and configuring the game should feel like walking the lab:
audio is the intercom mixer, display is the monitor cart, privacy is a
compliance clipboard you actually sign.

### Wireframe

```
+------------------------------------------------------------------------------+
|  BACK OFFICE // FACILITIES PANEL                              [ESC] leave    |
+------------------------------------------------------------------------------+
|                                                                              |
|  +----------------------+   +----------------------+   +------------------+  |
|  | INTERCOM MIXER       |   | MONITOR CART         |   | COMPLIANCE       |  |
|  |  MASTER  SFX  MUSIC  |   |  +----------------+  |   | CLIPBOARD        |  |
|  |   |       |     |    |   |  | quality: MED   |  |   |                  |  |
|  |  [=]     [=]    |    |   |  | (lamp: unlit - |  |   | Disclosure form  |  |
|  |   |       |    [=]   |   |  |  not wired)    |  |   | 27-B:            |  |
|  |   |       |     |    |   |  +----------------+  |   |                  |  |
|  |  50%     50%   13%   |   |  FULLSCREEN [ off ]  |   | [ ] publish lab  |  |
|  +----------------------+   |  THEME  < Default >  |   |     scores under |  |
|                             +----------------------+   |     our name     |  |
|  +----------------------+   +----------------------+   | [x] anonymous    |  |
|  | ADVISOR WHITEBOARD   |   | KEYBOARD TRAY        |   |     headcount    |  |
|  |  intros: PLAY        |   |                      |   |     ping         |  |
|  |  hints:  SHOW        |   |  >> pull out tray    |   |                  |  |
|  |  rival intel: PIPE   |   |  (keybindings)       |   |    sign: [OK]    |  |
|  |  layout: CLASSIC     |   |                      |   +------------------+  |
|  +----------------------+   +----------------------+                         |
|                                                                              |
|  every switch is live -- the lab remembers                                   |
+------------------------------------------------------------------------------+
```

Each panel is a distinct styled PanelContainer "object": the mixer gets
vertical fader sliders, the clipboard gets a paper-toned panel with
checkbox rows and a "sign" button (which IS the consent click the privacy
ruling wants to be explicit), the monitor cart's quality lamp is honestly
unlit until quality is wired. Same GameConfig calls underneath.

### Grouping and why
Grouping by OBJECT, and objects map 1:1 to the player's mental categories:
sound gear = audio, screen gear = display, paperwork = privacy (making
identity consent feel like signing a form is more honest, not less, than
a bare toggle), whiteboard = the advisor-flavored gameplay assists,
tray = controls. The fiction does the information architecture.

### Empty space / empty Graphics section
The empty texture becomes the WALL the equipment hangs on -- the first
direction where the painted-metal background is a feature. Panels are
sized to content; there is no fold and no section headers to run empty
(an object with one control is just a small object).

### Trade-offs
- Highest art + bespoke-layout cost, and each NEW setting needs a home in
  the fiction (where does "UI scale" live on a lab bench?). Growth is
  awkward.
- Discoverability depends on the metaphor landing; a player who does not
  read "clipboard = privacy" hunts longer than in any other direction.
- Accessibility: vertical faders and novel controls need real focus-order
  and keyboard-nav work to stay compliant with the style guide.
- Risk it reads as cute rather than institutional if the art misses.
- Effort: ~20-30h including simple placeholder art; more with generated
  panel art (the gpt-image-1 pipeline can produce the five object plates
  cheaply, but integration/iteration time dominates).

### Who it is for
The immersion player and the streamer -- the person who screenshots the
settings menu. This is the direction that turns the game's weakest screen
into a marketing asset. It is also the only one that makes the privacy
consent MORE legible by theming it.

---

## Direction 4: CONFIG TERMINAL

**Thesis:** The config file is the UI. Render `user://config.cfg` sections
directly as an editable terminal document -- zero possible drift between
what is shown and what is stored, and the ASCII register stops being
chrome and becomes the whole screen.

### Wireframe

```
+------------------------------------------------------------------------------+
| pdoom1 lab console -- configuration editor                        rev 0.13.2 |
| /user/config.cfg   LIVE   writes on change   [/] filter   [ESC] exit         |
+------------------------------------------------------------------------------+
|                                                                              |
|  [audio]                                                                     |
|  > master_volume   = 50        # <- -> adjust, hold for fast                 |
|    sfx_volume      = 50                                                      |
|    music_volume    = 13                                                      |
|                                                                              |
|  [graphics]                                                                  |
|    fullscreen      = false     # [ENTER] toggle                              |
|    quality         = medium    # ! not wired yet -- has no effect            |
|                                                                              |
|  [interface]                                                                 |
|    theme           = default   # default | retro | high_contrast             |
|    show_rivals_feed= true                                                    |
|    show_hints      = true                                                    |
|    ui_layout       = classic   # experimental A/B; applies next run          |
|                                                                              |
|  [privacy]                                                                   |
|    submit_scores_global = false  # shares player + lab name publicly         |
|    send_launch_ping     = true   # anonymous install count only              |
|                                                                              |
|  [controls]                                                                  |
|    keybindings     -> open keybind editor                                    |
+------------------------------------------------------------------------------+
| 14 keys   3 sections hidden by filter: (none)              all changes saved |
+------------------------------------------------------------------------------+
```

Up/down moves the `>` cursor; left/right adjusts values in place; `/`
type-to-filter jumps to any key by substring ("colo" -> colorblind_mode).
Comment column carries the honest captions. Mouse still works (click row,
click value to cycle) so it is not keyboard-gated.

### Grouping and why
Grouping = the ACTUAL cfg sections already defined in
`GameConfig.save_config()` (audio/graphics/interface/accessibility/
privacy/leaderboard...), lightly merged for display. The file is the
single source of truth; the screen is a view of it. A new setting added
to GameConfig appears here by adding one descriptor line to a table --
this is the anti-rot pattern (generated index, not hand-maintained copy),
the same reasoning as DQ_INDEX.
Search is the real grouping: with type-to-filter, taxonomy arguments
(is theme display or interface?) stop mattering.

### Empty space / empty Graphics section
A terminal is fullscreen by nature; the document fills the frame over a
dark scanline field (the existing `tex_green_grid`/`tex_amber_scanlines`
assets finally used as intended). No fold: 14 keys fit one screen at
terminal density; if they ever do not, terminal scrolling with a visible
`-- more --` line is native to the fiction instead of a lying scrollbar.

### Trade-offs
- Least approachable for players who do not read config files; snake_case
  keys on screen will feel like developer UI to some (mitigable with a
  friendly-label column, at the cost of the purity).
- Sliders-as-numbers lose the analog feel for volume; needs a live
  preview tick to compensate.
- Novel control = real keyboard/focus implementation work, and it must
  not regress accessibility (large-text mode at terminal density needs
  checking).
- Effort: ~12-16h (data-driven row descriptor table, cursor + filter
  logic, one screen; no per-section scenes).

### Who it is for
The game's core demographic bullseye -- the AI-safety-curious, terminal
native player -- and Pip's own aesthetic. Also the cheapest direction to
keep TRUE forever (one descriptor per setting; the UI cannot silently
disagree with the config file, which is the exact failure class of the
stale F5/F9 grid).

---

## Direction 5: THE FIRST FIVE MINUTES

**Thesis:** Nearly every settings visit in a player's first hour is one of
five intents -- too loud, music off, fullscreen, hints off, colorblind.
Serve those in five seconds on one small card; put everything else behind
exactly one clearly labelled door.

### Wireframe (front card)

```
+------------------------------------------------------------------------------+
|                                                                              |
|                       +------------------------------+                       |
|                       |  SETTINGS                    |                       |
|                       |                              |                       |
|                       |  Volume    [==========----]  |                       |
|                       |  Music     [===-----------]  |                       |
|                       |                              |                       |
|                       |  Fullscreen          [OFF]   |                       |
|                       |  Gameplay hints      [ON ]   |                       |
|                       |  Colorblind mode     [OFF]   |                       |
|                       |                              |                       |
|                       |  ---------------------------- |                      |
|                       |                              |                       |
|                       |  >> ALL PROTOCOLS            |                       |
|                       |     sound detail, display,   |                       |
|                       |     privacy, intros, feed,   |                       |
|                       |     experiments              |                       |
|                       |                              |                       |
|                       |  >> KEYBINDINGS              |                       |
|                       |                              |                       |
|                       |  [ESC] back    auto-saved    |                       |
|                       +------------------------------+                       |
|                                                                              |
+------------------------------------------------------------------------------+
```

"Volume" is master; SFX/music split lives in ALL PROTOCOLS (music gets a
front-card slider because Pip's own playtest note -- music downtuned to
20 as "too loud/intense" -- says players reach for it early). ALL
PROTOCOLS opens the complete flat ledger: every remaining setting in one
scrolling list with section headers and captions (essentially today's
screen done properly), including the privacy pair with their full honest
sentences.

### Grouping and why
Grouping by FREQUENCY OF NEED, not by topic. The front card is a bet on
usage statistics, not a taxonomy: five controls, zero scanning cost. The
back page can afford to be a plain dense list because only deliberate
players open it -- and deliberate players are exactly who a flat
everything-visible list serves best (audit-friendly for privacy sweeps).

### Empty space / empty Graphics section
Embraced instead of fought: a deliberately small centered card reads as
composed (the welcome screen already proves a narrow centered column
works on this texture -- this direction makes Settings rhyme with the
game's strongest screen). The back page fills tall; no header can sit
empty because the ledger only renders rows that exist.

### Trade-offs
- Two hops to anything advanced; the player hunting "stop submitting my
  scores" must open ALL PROTOCOLS first (mitigated by naming privacy in
  the door's caption, as wireframed).
- The front-card picks are a guess; if the guess is wrong for a player,
  this is strictly worse than one flat screen.
- Two surfaces to maintain instead of one.
- Effort: ~6-10h (front card is trivial; the ledger is today's scene
  with the layout bug fixed, captions added, difficulty removed, Apply
  killed).

### Who it is for
The new player and the drive-by adjuster -- the person mid-frustration
who wants the music quieter NOW. Best onboarding feel of the five; also
the least work after Direction 1's bug-fix floor, because it reuses the
existing scene as its back page.

---

## Spread check (why these five are actually different)

| Direction        | Organizing principle    | Density | Nav depth | Fiction |
|------------------|-------------------------|---------|-----------|---------|
| Operations Board | player's question       | high    | 0         | medium  |
| Protocol Tabs    | category convention     | medium  | 1         | low     |
| Lab Floor        | diegetic object         | medium  | 0         | high    |
| Config Terminal  | the config file itself  | high    | 0 +search | high    |
| First Five Min.  | frequency of need       | low->hi | 0 or 1    | low     |

Axes covered: everything-visible vs progressive disclosure; taxonomy vs
frequency vs fiction vs file-truth; mouse-first vs keyboard-first;
whitespace-as-composition vs density-as-composition.

---

## If you only do one thing

Remove the expand flag from `Spacer` in `settings_menu.tscn` (or delete
the node) so `Scroll` takes all leftover height, and widen the root VBox
beyond its hard-coded 800x600. That is a two-line .tscn change, ~0.5h
including a visual check, and it un-hides SIX already-shipped sections --
fullscreen, quality, theme, colorblind, intros, hints, privacy toggles,
the works. The menu Pip thinks is missing was built; it is standing
behind a spacer.

Second and third cheapest wins, independent of direction, in order:
1. Delete the static Keyboard Shortcuts grid (stale F5/F9 claims) and
   replace with one `>> KEYBINDINGS` link to the real screen (~0.5h).
2. Kill the Apply button; save on change or on exit, and say so on
   screen ("changes save automatically") (~1h). Silent revert-on-restart
   is the current behavior for anyone who presses Back without Apply.
3. Remove the Research Intensity row (contradicts the #1058 league lock)
   and either wire graphics quality or label it not-yet-wired (~1h).

Do all four and today's screen stops being amateur before any direction
is even chosen; the five directions above are then a choice about what
Settings should BECOME, not a rescue.
