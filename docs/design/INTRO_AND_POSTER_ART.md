# Intro and poster art -- using the effects and posters we already own

- **Status:** DESIGN PROPOSAL for Pip. No code changed, no assets moved.
- **Date:** 2026-08-04
- **Ask (Pip):** "we have our swirly and whirly video effects we made up a
  while ago, this feels like some fleshing out of the intro and opportunities
  to use those poster scenes would be handy now." Plus playtest 2026-08-01:
  [5:05] "I want a visual, like a poster or a pop-up on the strategic moves
  unlocked"; [5:11] "it's just a black little screen, let's make that visually
  more interesting"; [3:49] a summary "pops up and blocks the screen" (so more
  visual must not mean more obstructive).
- **Governing rules:** ADR-0019 (pack = declared demand; every proposal below
  states its demand), ADR-0001 (a reveal should open a decision), house
  register (ASCII chrome, dark palette, amber accents, no emoji, ever).

---

## Part A -- What actually exists

Reportage first. I hunted the tree; here is what is real, with verdicts from
`tools/art_review/review_state.json` (2,713 entries) and Pip's notes quoted
where they exist.

### A1. The "swirly and whirly video effects"

**There are no video files.** Honest finding: the swirl Pip remembers is not
footage, it is a live procedural shader plus a capture harness that can RENDER
footage on demand. This is better than video for our purposes: zero megabytes,
resolution-independent, tintable to any palette at runtime.

| Thing | Where | State |
|---|---|---|
| The vortex shader | `godot/assets/shaders/time_portal.gdshader` | SHIPPED in the pack, used by NO player-facing flow |
| Technique doc | `godot/assets/shaders/README_shader_animation.md` | tween-a-shader-uniform pattern, written to outlive the portal |
| Live tuning harness | `godot/scenes/dev/portal_shader_demo.tscn` + `godot/scripts/dev/portal_shader_demo.gd` | dev-only; every dial is a slider |
| Unattended capture scene | `godot/scenes/dev/captures/portal_capture.tscn` + `godot/scripts/dev/captures/portal_capture.gd` | dev-only; Movie Maker auto-play |
| Capture runner | `tools/capture_cinematic.py` + `tools/README_capture.md` | deterministic mp4/gif shooter; `captures/` output dir is currently empty |

The shader header says it plainly: *"procedural time-travel PORTAL for the
#801 cold-open (UPGRADE layer)"*. It was built FOR the intro and never wired
in. It is a rotating radial vortex with concentric spiralling rings, a glowing
core, a CRT scanline overlay, and an `open_progress` uniform (tween 0 -> 1 and
it "pops into existence"). Three palettes are pre-matched to TerminalTheme:
doom-red (default), phosphor green, amber. Fourteen dials total (swirl_speed,
distortion, ring_count, glow_size, scanline_intensity, and so on) -- this is a
menu of tunables Pip can drive live in the demo scene.

Adjacent effects, smaller:

- **CRT frame overlays** -- `art_generated/crt_frame_overlay/v1/`: three
  designs (`crt_frame_bezel_heavy`, `crt_frame_curved_glass`,
  `crt_frame_vignette_light`) at 768 and 1536 px. All three verdict **keep**.
  Tiny files (the 1536 vignette is 56 KB).
- **Doom overlay pixel loops** -- `art_source/pixellab_2026-07-26_doom_overlays/`:
  9-frame animated loops in families `aura/` (glowdisc, smokering,
  spikysigil), `void/` (jaggedrift, tentacles, **vortex**), plus arc, embers,
  flame, wisp, states. **199 keep / 21 iterate** verdicts. Whole directory is
  926 KB. These are small office-scale FX sprites, not full-screen material,
  but the `void/vortex` loop is a second, pixel-art swirl if we ever want one
  inside the office render.
- `GlowButton.shader` exists twice (retired dump + `godot/assets/ui/buttons/glowcat/`) -- minor, noted for completeness.

### A2. The poster scenes

**endgame_concepts + endgame_concepts_gen2** (`art_generated/endgame_concepts*/v1/`)
-- 14-16 subjects x 2 variants x 4 sizes (512/768/1024/1536 PNG). **21 keeps**
across the two generations, including:

- `intro_bus_strangers_help` (gen2 v1, keep) -- literally named for the intro.
  Pip's note on the gen1 sibling: *"this was a good composition but more
  recent versions have better approaches to keeping the protagonist
  unidentified - shoot from the back, silhouettes for either gender only,
  hoods, hats"*.
- `remote_operators_room`, `orbital_datacenter_ring`,
  `field_ladder_three_rungs`, `chokehold_permit_counter`,
  `chokehold_water_and_gigawatts`, `attention_loud_vs_slow`,
  `attention_stack_buried_desk` (note: *"human too identifiable, otherwise,
  good, backgroundf weirdness good also"*), `economics_rung_shuttered_street`,
  `cheerful_propaganda_atrium`, `crux_drone_arms_race`,
  `pacification_delivery_suburb`, `runaway_delivery_loop`.
- A systemic note worth honouring in any new generation: *"we ssem toh ave
  massively overindexed on the bankers lamp as an art asset"*.

**hero_banners** (`art_generated/hero_banners/v1/`, 162 files) -- **19 keeps,
12 maybes**. The keeps that matter here:

- `fanfare_strategic_moves_v1` and `_v3` -- generated FOR the fanfare popup's
  empty image slot, reviewed keep, never wired. Also
  `round3_rerolls_banners/v1/fanfare_strategic_moves_r3_v1` (keep).
- `banner_title_hero_v2`, `banner_doom_rising_v2` (keep; r3 rerolls v1+v2 also
  keep), `hero_office_at_dusk` v1-v4 (all four keep), `hero_cat_and_terminal`
  v1-v3, `hero_desk_doom_window_v2`, `hero_doom_gradient_title` v1+v4,
  `hero_doom_ladder_split_v2`, `hero_server_doom_altar` v3+v4,
  `hero_whiteboard_war_room` v1+v3.
- Iterate notes that read as briefs: founder silhouettes *"too boviously male,
  too obviously signalling Operator"*; server-doom-altar operator should be
  *"androgynous... cool cloak with a collar or a hood"*.

**scene_art_wave2** (`art_generated/scene_art_wave2/v1/`, webp) -- **19 keeps**.
Three families:

- `event_crisis_v1/v2/v4`, `event_opportunity_v3`, `event_secret_v1/v3`,
  `event_board_v1` -- event-category art. **Eight of these are ALREADY PACKED**
  at `godot/assets/images/events/` (crisis v1+v3, opportunity v2+v4, secret
  v1+v3, board v2+v3) and **no code references them** -- textbook
  packed-but-undemanded (ADR-0019's fourth state), grandfathered. Note on
  opportunity v2 (iterate): *"Try making fihgures more androgynous and less
  obvious, otherwise, good"*.
- `office_*` six -- shipped at `godot/assets/images/backgrounds/`;
  `office_wide_dawn.webp` is the ONE image the current intro uses.
- `records_*` six -- shipped at `godot/assets/images/backgrounds/records/`.

**vignettes_2026-07-28** (`art_source/`, in git, 921x614 committed, 1536x1024
masters archived per ART_MASTERS_POLICY) -- 5 images against
`docs/game-design/SEED_VIGNETTE_SPECS.md` (30 specs; GTA-loading-screen
register; SILHOUETTE PRINCIPLE; KEYED vs GENERIC pools). Keeps:
`01_cat-in-the-alley` (flagship -- note: *"This will do for now but please
give me, like, 10 variants to choose from? Maybe some vesrions where the cat's
arrival is doom-portentous and some where it's saviour-portentous?"*),
`02_conference-departure`, `05_taxi-window-rain`. `04_conference-return`
carries a redo brief (*"seems too visible and obviously a man... luggage on
bed, overstuffed mailbox... what's in the fridge"*).

**env_scenes** -- thin: `env_bg_doom_abstract_v2` keep, two maybes, one
reroll; the `env_loading_*` families are unreviewed. **screen_backgrounds** --
the `bg_*` set is ALL reroll (*"All these seeem wildly incorrect"*) -- do not
design against them; the `tex_*` texture set has 10 keeps.

### A3. The current intro, second by second

Flow: boot -> `welcome_screen.gd` -> `config_confirmation.gd:91` -> (if
`GameConfig.should_show_intro()`) `cold_open_sequence.tscn` -> `main.tscn`.

`godot/scripts/ui/cold_open_sequence.gd` (#801), what a player sees:

```
0.0s   black (OPENING_BLACK_HOLD 0.5s)
0.5s   office_wide_dawn fades up behind, dimmed to 45%; green mono text
       pops in: "Doom is coming."                       (holds 3.0s)
~4.4s  "But... when am I? / What can I do?  What *day* is it?"  (4.0s)
~9.9s  "*checks pockets*  --  a primitive phone!"       (3.0s)
~14s   interactive phone slab: lock screen (07:03) -> any-4-digit keypad ->
       "Oh! how lucky!" -> home: BANK (real starting money) + MESSAGES
       (Mysterious Helpful Stranger hands over the SCOUTING choice)
       -> "Begin  >>" -> main, with the first-lever hint pulsing scouting
```

Click advances beats; hold-to-skip conviction ring (3s) is the only skip.
Total art on screen: ONE background image. The portal shader that was built
for this sequence's "UPGRADE layer" appears nowhere. The ending already obeys
ADR-0001: the last beat hands the player an active choice (scouting), not a
narrative line -- every proposal below preserves that handoff.

### A4. The popups

- `godot/scripts/ui/fanfare_popup.gd` (#578) -- CanvasLayer 128, 0.8-alpha
  black backdrop, 460 px card, **an image slot that already exists**
  (`_image`, 408 px wide, fit-width) and has never once received an image. The
  single call site (`main_ui.gd:1869`, `_show_strategic_unlock_fanfare`)
  passes `""` with the comment *"hero banner image slot -- [it] drops in here
  later"*. This is the "just a black little screen". The banner it is waiting
  for exists and is verdict-keep (`fanfare_strategic_moves_v1`).
- `godot/scripts/ui/event_dialog.gd` (#622) -- queue + modal presenter,
  forest-green panel, lettered choice buttons, NO image support at all.
  Issue #508 (open): per-option hero art on event popups. The presenter
  already distinguishes decision popups from single-option free "doors"
  (`is_navigation_popup`, playtest B2/B3).
- `godot/scripts/ui/conference_vignette.gd` -- an existing staged-reveal shell
  (ADR-0014) whose header explicitly plans for *"a tableau backdrop... layered
  in without touching the sim seam"*. Useful precedent: we already have a
  pattern for text-beats-over-art scenes.

---

## Part B -- The intro: five proposals

Shared constraints: the phone + scouting handoff stays (it is the decision the
reveal opens, per ADR-0001); hold-to-skip stays; all copy in the one tunable
block; green/amber mono over near-black; every image ships as a sized webp
derivative, never a master (ADR-0019 rule 4). Effort estimates assume the
existing beat driver is reused, not rewritten.

### B1. PORTAL STITCH (wire in the thing that was built for this)

The minimal upgrade: the portal shader becomes the connective tissue of the
EXISTING sequence, nothing else changes.

- Beat 0: black; the doom-red vortex opens behind "Doom is coming."
  (`open_progress` tweened 0 -> 1 over ~1.6s, dimmed so text reads).
- Beat 1-2: the swirl keeps spinning, slowly decaying (`swirl_speed` and
  `glow_strength` tweened down) as the questions land -- the time-jump is
  ending.
- Phone reveal: the vortex collapses (`open_progress` 1 -> 0), and as it dies
  the phone slab fades up -- palette handoff from doom-red swirl to the
  phone's CRT green. `office_wide_dawn` fades up only at "Begin >>", so dawn
  = arrival.
- Teaches: you time-travelled, arrival-in-a-body, before any word says so.
- Uses: `time_portal.gdshader` (shipped), `office_wide_dawn.webp` (shipped).
- Demand: **0 new assets, 0 new MB.**
- Effort: 4-8 h (tween choreography + dialing; the dials already have a live
  tuning harness).
- Risks: swirl behind text can fight legibility (mitigate: modulate the
  portal rect down to ~35% while text holds -- ~90% confident this reads
  fine, the demo scene proves it cheaply). Motion for motion's sake if
  overdone; keep swirl_speed low.

### B2. HELD FRAME (one poster, slow push)

A single held image with the existing text beats as lower-third captions.
`intro_bus_strangers_help` (gen2 v1, keep, named for this) fills the screen at
45% dim with a very slow scale 1.00 -> 1.06 over the whole ~14s (Ken Burns by
tween). Text beats unchanged. Phone rises out of it as now.

- Teaches: tone (ordinary world, unidentified protagonist -- the silhouette
  principle already reviewed into this image).
- Uses: 1 endgame_concepts_gen2 poster.
- Demand: **1 image at 1536x1024 -> webp derivative, ~0.3-0.4 MB.**
- Effort: 3-5 h. Lowest risk of anything here.
- Risks: it is the current intro with a better photo -- if Pip wants "fleshed
  out", this may under-deliver. Zero motion payoff from the shader ask.

### B3. FIVE POSTERS, ONE LINE EACH (silent poster sequence)

The SEED_VIGNETTE_SPECS register, used as the front door: 4-5 GENERIC-pool
posters crossfade, each holding ~3s with one caption line in the seed doc's
voice (mood only, no-lies rule -- none may claim a mechanic). Suggested pull,
all keeps: `05_taxi-window-rain` -> `02_conference-departure` ->
`intro_bus_strangers_help` -> `attention_stack_buried_desk_v2` (gen2) -> cut
to black -> "Doom is coming." -> phone. The endgame posters are NOT shown as
endgame here, just as world.

- NOT `01_cat-in-the-alley`: the spec marks it KEYED to the stray-cat event
  (*"do not put in the generic pool"*). Respect that.
- Teaches: the world's register and loneliness; that images in this game carry
  voice.
- Demand: **4-5 images at ~1280x854 webp, ~0.15-0.25 MB each => ~1 MB.**
- Effort: 6-10 h (crossfade driver is a small extension of the beat system;
  most of the cost is caption copy, which is Pip's voice anyway).
- Risks: lengthens the pre-interaction stretch (mitigate: click-to-advance
  already exists per beat); caption quality is load-bearing -- placeholder
  captions here would be worse than no posters.

### B4. BOOT SEQUENCE (diegetic CRT power-on)

The intro pretends the GAME is a machine being switched on in 2016. Black;
a single amber cursor blinks; ASCII boot log types itself ("PDOOM/1 BIOS",
memory check that counts up to the real starting money, "CLOCK SKEW DETECTED:
+9 YEARS" as the one joke); mid-boot the log corrupts and the portal shader
flashes open-and-shut (green palette, 1-2s) as the "time glitch"; boot
completes into the phone lock screen -- the phone IS the booted device.
`crt_frame_vignette_light` overlays the whole sequence so it all happens
inside glass.

- Teaches: the terminal register IS the game's skin; when-am-I as a machine
  symptom rather than a narrated question.
- Uses: shader + 1 CRT overlay (keep, 56 KB) + zero posters.
- Demand: **1 overlay image at 1536px, ~0.06 MB.** Effectively free.
- Effort: 8-12 h (typewriter/boot-log driver is new code; everything else
  exists).
- Risks: fake boot screens are a known trope -- charming or groan, taste call
  (playtest it; ~25% it reads as filler to a second-time viewer, which
  hold-to-skip already covers). Longer copy surface to keep in-register.

### B5. MID-CRISIS REWIND (start at the end)

Starts at the death the player is being sent back to prevent. Doom-red vortex
at full scream, one line: "It is 2026. P(Doom): 97%." Two endgame keeps flash
as ~1.5s stills inside the swirl (`orbital_datacenter_ring`,
`runaway_delivery_loop` -- late-game states the sim can actually reach). Then
`swirl_direction` flips to -1, `ring_count` and speed wind down -- the vortex
runs BACKWARDS -- posters strobe in reverse, and it collapses onto
`office_wide_dawn`: "It is 2016. You remember all of it." -> phone -> scouting.

- Teaches: the stakes, the time-travel premise, and that the endgame art the
  player will later meet is REAL foreshadowing -- when
  `orbital_datacenter_ring` shows up at a real ending, the intro pays off.
- Uses: shader (both spin directions -- a dial that exists) + 2-3 endgame
  posters + office_wide_dawn.
- Demand: **2-3 images at 1280x854 webp => ~0.5-0.7 MB.**
- Effort: 10-16 h (most choreography of the five; new copy; careful pacing so
  the loud open does not read as a different game).
- Risks: opening loud then going quiet is a tone gamble for a first
  impression (~30% it needs a second pacing pass after playtest); the "9 years
  early" framing must match whatever start-year canon says (current cold open
  deliberately keeps the year vague -- check before writing "2016" anywhere).

### Comparison

| # | Name | New assets | New MB | Effort | Character |
|---|---|---|---|---|---|
| B1 | Portal Stitch | 0 | 0 | 4-8 h | motion, uses the shader ask directly |
| B2 | Held Frame | 1 | ~0.4 | 3-5 h | cheapest, safest, least ambitious |
| B3 | Five Posters | 4-5 | ~1.0 | 6-10 h | voice-forward, caption-dependent |
| B4 | Boot Sequence | 1 | ~0.06 | 8-12 h | most diegetic, most new code |
| B5 | Mid-Crisis Rewind | 2-3 | ~0.6 | 10-16 h | biggest narrative swing |

These compose: B1 is a substrate for B3, B4, or B5 (all three assume the
portal exists as a stitchable element). B2 is the fallback if a league week
eats the calendar.

---

## Part C -- Event popups: art without obstruction

The [3:49] complaint rules here: art attaches INSIDE surfaces that already
interrupt; nothing new interrupts, and nothing gets bigger than it is today.

### C1. The fanfare, specifically (the "black little screen")

The fix is embarrassingly close: `fanfare_popup.gd` already has the image
slot, `_show_strategic_unlock_fanfare` already has the argument position, and
`fanfare_strategic_moves_v1` is already verdict-keep. Render a derivative at
~816 px wide (2x the 408 px slot for hidpi), drop the path into the call, done.
While in there: restyle the card border to the house register (amber 2px rule,
`[OK] Continue` button label) -- the current card is a gray-green one-off that
predates the theme work. Any FUTURE unlock fanfare declares one banner in the
same pool ("fanfare banners: 1 per unlock moment, 816px wide").

- Demand: **1 image, 816px webp, ~0.2 MB.** Effort: 1-2 h.

### C2. Event dialogs: CATEGORY header strips, not per-event posters

Issue #508 asks for per-option images; the sustainable version is a tier
below: a wide, shallow header strip (full card width x ~110-140 px tall,
cropped from the middle band of the image) at the top of the event panel,
selected by event CATEGORY -- crisis / opportunity / secret / board. The four
families exist as keeps in scene_art_wave2, and eight files are ALREADY IN THE
PACK at `godot/assets/images/events/` with zero references. Wiring them is not
new demand so much as finally writing the demand declaration for grandfathered
bytes (net new download: ~0; a cropped-strip re-derivative would actually
SHRINK them).

Mechanics: `event_dialog.gd` maps `event.category` (or a fallback keyword
match) -> one strip texture, drawn dimmed (~70%) behind an amber rule under
the title. Same card size, same button layout, no added clicks. Events without
a category get no strip -- absence is fine, magenta-cat placeholders are not
(ADR-0019 rule 5).

- The "doors" stay bare: `is_navigation_popup` events (single free option,
  e.g. month review) get NO art. A door is not a moment; decorating it
  re-inflates exactly what B2/B3 deflated.
- Per-OPTION icons (#508's literal ask) ride the existing 48 px icon system
  later, as a separate small demand ("event option icons: pool of ~12 at
  48px"); they are not part of this pass.
- Demand: **4 strips at ~1280x180 webp, ~0.05-0.08 MB each => ~0.3 MB** (and
  it retires ~2.5 MB of grandfathered full-size webp if the strips replace
  the eight unreferenced files). Effort: 4-6 h.

### C3. KEYED vignettes for flagship events only

The SEED_VIGNETTE_SPECS pattern (image BEFORE the choice panel) is reserved
for the 1-3 events the design has explicitly keyed -- the stray cat first
(`01_cat-in-the-alley`, the flagship Pip keyed and asked for 10 variants of).
Presentation: the vignette fades up full-screen for ~2.5s with its caption,
then RECEDES INTO the event dialog's header strip as the choices appear -- the
interruption is the event itself, which was already modal; the art borrows its
time rather than adding any. This is the show-piece answer to [5:05] without
making every event a show-piece.

- Demand: **1 image now (cat, 1280x854 webp ~0.25 MB); pool declared as
  "keyed event vignettes: 1 per KEYED spec that ships".** Effort: 5-8 h for
  the recede-into-header presenter, reusable for every later keyed event.

### C4. What deliberately does NOT get art

Month summaries, resolution reports, and anything else on the [3:49] list of
screen-blockers. The rule of thumb to write down: **art marks state changes
the player will remember (unlocks, keyed story beats, endings); chrome marks
everything else.** If a popup would be dismissed in under two seconds, it gets
chrome, not a poster.

---

## Part D -- What this costs the pack

Context: pack is 59 MB, `godot/assets` is 47 MB of it; #1109 records that a
blanket promotion of current keeps would add ~105 MB; ADR-0019 makes the pack
a function of declared demand and this document IS a demand declaration. All
figures are sized webp DERIVATIVES rendered from Library masters (ADR-0019
rule 4) -- masters never cross into `godot/`.

| Proposal | Assets demanded | Size each | Pack delta |
|---|---|---|---|
| B1 Portal Stitch | 0 (shader shipped) | -- | +0 MB |
| B2 Held Frame | 1 poster, 1536x1024 | ~0.4 MB | +0.4 MB |
| B3 Five Posters | 5 posters, 1280x854 | ~0.2 MB | +1.0 MB |
| B4 Boot Sequence | 1 CRT overlay, 1536px | ~0.06 MB | +0.1 MB |
| B5 Mid-Crisis Rewind | 3 posters, 1280x854 | ~0.2 MB | +0.6 MB |
| C1 Fanfare banner | 1 banner, 816px wide | ~0.2 MB | +0.2 MB |
| C2 Category strips | 4 strips, 1280x180 | ~0.07 MB | +0.3 MB (net ~-2 MB if the 8 grandfathered event webps are retired for the strips) |
| C3 Keyed vignette (cat) | 1 poster, 1280x854 | ~0.25 MB | +0.25 MB |

Worst-case everything-at-once: **~2.9 MB gross, roughly +1 MB net** against a
59 MB pack if C2 retires the unreferenced event images. Nothing here is a
40-poster animal; the largest single demand is five images. The demand-pool
declarations, in ADR-0019's shape:

```
intro posters:        pool, floor 1, ceiling 5, 1280x854 webp
fanfare banners:      pool, 1 per unlock moment, 816px wide webp
event header strips:  pool, 1 per event category (4), 1280x180 webp
keyed vignettes:      pool, 1 per shipped KEYED spec, 1280x854 webp
crt overlays:         pool, floor 1, 1536px png/webp
```

One cost that is not megabytes: every image that enters a pool inherits the
silhouette-principle review bar (three of Pip's notes above are exactly this),
so each pull is a taste check, not a copy.

---

## Part E -- What I would build first, and why

**First commit: C1, the fanfare banner.** One derivative, one path string,
one call-site edit; it closes the exact [5:05]/[5:11] playtest complaint with
an asset that was generated for that slot and reviewed keep. It is also the
cheapest possible live test of the ADR-0019 pull path: one pool, one entry,
one transform. If the demand-manifest tooling does not exist yet, this is the
right first entry to hand-write. 1-2 hours, +0.2 MB.

**First intro build: B1, Portal Stitch.** Three reasons ahead of the others:
it is the only proposal that spends the asset Pip actually named (the swirl),
it adds zero bytes to a pack that #1109 says is under pressure, and it is the
substrate the bigger intros (B3/B4/B5) would be built on anyway -- so nothing
is thrown away if Pip later escalates to Mid-Crisis Rewind. The risk profile
is the best of the five: the tuning harness already exists, so the "does the
swirl fight the text" question costs an afternoon in
`portal_shader_demo.tscn`, not a rebuild.

Then, in order of payoff-per-hour: C2 (category strips -- turns grandfathered
dead bytes into working art), C3 (the cat vignette -- the flagship), and B3 or
B5 as the ambition budget allows, with B3/B5 treated as an extension of the
B1 substrate rather than a competing intro.
