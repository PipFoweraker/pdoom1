# Tone & Art Direction — cozy-grimdark + ambient state display

> **Status**: Direction capture — evolving. Reference for art-asset work.
> **Related**: `INTRO_CINEMATIC.md`, `TWO_ACT_STRUCTURE.md`, `RISK_SYSTEM.md`, #528 (Ledger)

## Thesis
**Cozy competence under existential dread.** A warm, lived-in office you enjoy running,
beneath a sky that is quietly bleeding. The aesthetic goal is to hold both at once without
either cancelling the other.

## The layer split (why cozy + doom coexist)
The games that pull this off (Papers Please, Two Point Hospital, Frostpunk, Spiritfarer) all
separate the two onto different layers, so they never compete for the same beat:
- **Cozy = the moment-to-moment loop.** Tactile, competent, warm, low-pressure — the office,
  the people, the rhythm of upkeep. Where the player lives second-to-second.
- **Dread = the meta layer.** The doom meter, the *hidden* risk pools, the clock toward the
  singularity. The trajectory, not the moment.

You are cozy in the *now* and terrified of the *trend*. The architecture already splits this
way: visible office/people management = cozy; hidden insight-gated risk pools (the redacted
Ledger, #528) = dread.

### The refinement: dread *bleeds* into the cozy layer atmospherically
Dread stays mostly cerebral (numbers/events/text), but it **leaks into the cozy visuals as
mood, not gore** — a red sun, heavier weather, a nervous cat. A beautiful, upgraded office
*under a bleeding sky* is the entire game in one frame: cozy and doom rendered simultaneously.
That dissonance is the thesis, not a bug.

## Visual register (rules)
- **Reference: Plants vs Zombies** visually — cute, readable, low-poly / 8-bit; a notch darker
  in content.
- **Bloodless lethality** — people get *lasered into crispy skeletons*, not chunked into gibs.
  Comedic death is the pressure-release valve. Keep gore *out* of the cute layer.
- **Readability first** — ambient/mood elements must be visually distinct from interactive ones
  (see Risks).

## Ambient Environment System (passive, diegetic, patch-in-able)
A non-interactive mood layer that reflects game state. **Not gameplay** — no clicking, no rush.

- **Environment as a second doom display.** The numeric meter is the *read* channel; the
  environment is the *felt* channel: sun reddens on high-doom days, weather intensifies, light
  cools. The player feels doom before reading it. (Natural tie to Insight/SA: low insight →
  you only feel the vibe; high insight → you read the numbers.)
- **Sims-like ambient life.** People wander the office as *decoration*, not tasks — like the
  background sim in management games. Makes the space feel alive and rewards investment; adds
  zero click-pressure (reinforces cozy).
- **Investment → visual richness (office tiers).** Office upgrades happen in *most* successful
  runs regardless of strategy, so visual progression is a near-universal reward — a high-value
  place to put art. **Everyone starts bare-bones** (even capabilities-flavoured / well-funded
  starts), and climbs a richness ladder as funding grows:
  `garage / warehouse / basement → bad office → swanky office → …`. The starting flavour (safety
  vs capabilities) tints the aesthetic but not the *tier* — you still begin humble. The office
  visibly warms (plants, mugs, posters, lighting) as you ascend.
- **Flagship indicator: the office cat.** Already seeded (`has_cat`, `OfficeCat` node in
  main_ui). Cheapest high-charm doom-barometer: content/playful when things are good, hiding /
  agitated when doom is high. Expand the partially-built feature into the lead mood-tell.

## Architecture for incremental patching
Make every effect a **read-only consumer of game state**, so it can be added/removed/A-B'd
without touching core logic:
- A single `AmbientController` (Node) subscribes to `game_manager.game_state_updated` (the dict
  already emitted each turn) and reads `doom`, office tier, etc.
- It pushes params to independent, self-contained effect nodes — e.g. `SkyTint`, `WeatherFX`,
  `OfficeCatMood`, `AmbientCrowd` — each exposing `apply_state(doom, office_tier, ...)`.
- Each effect is **toggleable via a config flag** → patch in one at a time, ship the ones
  playtesters like, disable the rest. None of them write game state.

## Priority (cheap-first, highest-charm-per-effort)
1. **Sky/sun tint by doom** — trivial, huge mood payoff.
2. **Office cat mood** — node exists; small state-machine.
3. **Office set-dressing by upgrade tier** — swaps/decorations, no animation.
4. **Weather intensity by doom** — moderate.
5. **Ambient wandering NPCs** — most expensive (pathing); do last, keep low-poly.

## Risks
- **Readability trap.** Ambient effects must NOT look interactive, or players click them and get
  confused. No hover/affordance on mood elements.
- **Perf/scope.** Wanderers + weather + dynamic light is real cost; keep each cheap and optional.
- **Mixed signal = intended.** Nicer office + redder sky simultaneously is the *theme*, not a
  contradiction — but make sure the *actionable* doom signal (meter) stays unambiguous.

## Existing-art audit (assessed 2026-06-27)
What's already in `godot/assets/` and what it tells us:
- **`dump_october_31_2025/`** ("main office doom chair scene", "vibes computer 1/2", "zoomed in
  doom cat") — **painterly, atmospheric, AI-generated concept art** (Midjourney-style): dark
  retro-computing dens, glowing CRTs, ember/fire light, occult-circuit symbology, colour-graded
  variants (**red = doom**, **teal/green = AI menace**, a CRT reading "AWAKEN"). This is
  **dread/horror register — NOT** the cozy cute-8-bit direction.
- **`cats/`** — the doom-cat motif is the most-developed asset line: mood-state SVGs
  (`happy / worried / concerned / distressed / corrupted`), generated doom-cat art, AND **real
  cat photos** (`web-arwen/luna/chucky/...` — likely community/backer cats). The "zoomed in doom
  cat" (calico + red gloom + code) is literally the cozy-grimdark thesis in one image.
- **Doom meter is already built** (`scripts/ui/doom_meter.gd` + `VISUAL_DOOM_METER.md`): a
  circular **"Doomsday Clock"** gauge (Bulletin-of-Atomic-Scientists), green→yellow→orange→red
  tiers, momentum arrows, pulse at ≥80%. Documented anchor phrase: **"early-2000s command-center
  aesthetic."**
- ~1180 action/UI icons exist (multi-resolution PNG sets) — UI iconography is well-covered.

### Three registers — reconcile, don't pick blindly
Auditing what's *documented* vs what was *said this session* surfaces THREE visual registers:
1. **Command-center retro-tech (the DOCUMENTED dominant).** The 536-line `UI_STYLE_GUIDE.md`
   (in the *older `pdoom1` repo*) + the icon pipeline define the established look: **"Early-2000s
   Command Center"** (Bloomberg / NATO C2 / Windows XP) × **StarCraft 2 / XCOM** × **"worn
   industrial."** Palette: graphite `#0E1318`, steel `#1C2730`, action-teal `#1EC3B3`, warn-amber
   `#F6A800`, danger-red `#B31217`; 5-stage doom overlays amber→deep-red. Generation color-bias:
   *"desaturated teal and olive."* ~3,700 existing images + the doom meter sit here. The devblog
   already calls the tone **"cozy-grimdark"** — operationalised as worn-industrial command-center,
   NOT cute-cartoon.
2. **Painterly atmospheric (Midjourney concept/mood).** The Oct-31 dump — doom dens, embers,
   red/teal grading. Concept / cinematic / high-doom mood, not in-game chrome.
3. **Cute low-poly / 8-bit (stated THIS session).** PvZ-ish, bloodless-comedic. A *new* lean that
   diverges from #1.

**Honest finding:** "cute 8-bit PvZ" is a pivot away from a large, documented body of
command-center work. Don't generate more art until this is settled. A reconciliation that keeps
everything (and maps onto the cozy/dread split):
- **UI / HUD chrome → command-center (#1).** Keep it; the doom meter already is = the *read*
  dread channel.
- **World / office / characters → cute low-poly (#3).** The cozy channel + the office tiers.
- **Cinematic / event / high-doom → painterly (#2).** Acute dread.
- **Doom-cat = hinge across all three.**
Games routinely run a HUD aesthetic distinct from a world aesthetic, so this holds.

**DECIDED (2026-06-27): adopt the three-layer synthesis** — command-center HUD (#1), cute
low-poly world/office/characters (#3), painterly cinematic/event/high-doom (#2), doom-cat as the
hinge across all three. New art is generated to the layer it belongs to.

### Where art lives (canonical map)
- **Asset GENERATION (methodology, source of truth): THIS repo `pdoom1-game/`** —
  `art_prompts/ui_icons.yaml` defs + `tools/assets/generate_images.py` (OpenAI `gpt-image-1`,
  YAML-driven, human-curated, ~$0.08/image). Staged in `art_generated/ui_icons/v{N}/` → promoted
  to `godot/assets/`.
- **Visual STYLE GUIDE (canonical): the *older* `pdoom1` repo** — `godot/UI_STYLE_GUIDE.md`
  (536 lines, most comprehensive). ⚠️ **Drift risk:** the canonical style guide lives in the old
  repo while active dev is here — consider migrating/copying it into `pdoom1-game` so worktrees
  inherit it (ties to the end-of-session "fold design into main" note).
- **Largest asset store:** `pdoom1` (~3,700 images, incl. `art_generated/`, `generated_icons/`).
- **Copies (NOT canonical):** `pdoom1-website` (~143 promo/web), `pdoom1-webclient` (~383 web UI).
  A `DESIGN_TOKEN_SYNC` GitHub Action treats `pdoom1` as canonical token source → website.
- `pdoom-data`: no art.

## Open decisions (Pip's calls)
- [x] **Register reconciliation** → three-layer synthesis adopted (2026-06-27).
- [x] Locate the older art-direction material → found (`pdoom1/godot/UI_STYLE_GUIDE.md` canonical
      style guide; `pdoom1-game` generation pipeline). Still TODO: migrate the style guide into
      this repo (drift risk).
- [ ] Doom→sky/weather mapping curve (linear vs threshold "bad day" spikes?).
- [ ] Cat mood states & thresholds.
- [ ] Whether ambient intensity is gated by Insight (felt-only at low insight).
