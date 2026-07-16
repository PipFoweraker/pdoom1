# Sprite Generation Plan — PixelLab (for Pip review BEFORE we spend generations)

> Reviewable plan. Nothing generated until Pip approves. Integration seam already built
> (#656 merged): `OfficeFloor.set_sprite_frames(frames)` wants a Godot `SpriteFrames` with
> four clips named EXACTLY `idle`, `walking`, `working`, `stressed`.

## Design foundation (RULED 2026-07-16 — see WORKSHOP_2_BACKLOG "Character sprite system")

**Physical identity is DECOUPLED from ability.** (Pip's instinct, beats Fable's earlier
"recognizable archetype-characters" which would have leaked hire-as-scouting hidden-info,
drifted Stardew, and coded competence into body types.)
- **Physical appearance = IDENTITY:** distinct, DIVERSE (gender / race / body type /
  disability / visible eccentricity — strong representation, deliberately *uncorrelated*
  with ability so a body is never a stat tell). Gives floor-recognizability ("who is that").
- **Personality/ability = HIDDEN, revealed over time via accruing clothing/accessories.**
  The archetype shows as you scout them, not at first sight.
- **Procedural per-run assembly** = base body × revealed clothing × swappable hat × state
  anim → fresh cast each run (roguelike), not a fixed dating-sim roster.

## The layered character model
1. **Base bodies** (`create_character`): a diverse set of physical identities, ability-
   neutral. Start with ~4–6 for MVP; expand later.
2. **State animations** (`animate_character`, the 4 OfficeFloor clips):
   - `idle` — relaxed stand (2-frame OK)
   - `walking` — walk cycle (4-frame)
   - `working` — sitting/typing at desk, focused (4-frame) — custom text prompt
   - `stressed` — head-in-hands / slumped (4-frame) — **priority anim; must read as the
     dashboard alarm at 48px**
3. **Swappable hats** (`create_map_object` overlays): rep cosmetics (medium-fancy, very-tall
   "aren't-compensating", sports). Base head kept NEUTRAL so hats layer clean.
4. **Revealed-trait clothing** (later wave): overlays that accrue as you learn a hire.

## Style dials (Fable's surprise-me calls — Pip can override)
- Bodies: **desaturated COLOR** on the amber-CRT **monochrome** environment (workers pop).
- Density: **48px** bodies.
- Frames: 4-frame key anims (idle 2-frame acceptable).
- Register: Papers-Please / CRT pastiche (WORLD_AND_LORE tone).

## The cat (first-class doom instrument — "a lot of effort into our cats")
Multiple cat forms keyed to DOOM BANDS: normal-**singed** (low doom, the running gag) →
**spooky** (mid) → **weird/eldritch** (high). `create_map_object` per form; OfficeFloor/
WATCH swaps the form by doom band. Ambient doom-barometer (office-as-mirror).

## The founder (separate — NOT a floor worker)
Shadowed **Dr Claw / Gendo silhouette** in a chair, WATCH-screen operator. Customize
trappings (throne/robes) never the face (anonymity = inclusion). Generated later.

## PixelLab tool → asset mapping
- `create_character` → base bodies (diverse identities).
- `animate_character` → idle / walking + custom-text `working`, `stressed`.
- `create_map_object` → hats, cat forms, furniture (desks, water cooler, fridge).
- tilesets → the office floor.

## Godot import wiring
Per base body: build a `SpriteFrames` with the four clips (`idle/walking/working/stressed`),
load the exported frames, → `OfficeFloor.set_sprite_frames(frames)` (or set as default in
`employee_sprite.gd`). Hats/cat = separate overlay sprites the OfficeFloor composites.

## First move (before any batch)
Generate **ONE** base character with the four anims, import, put it on the floor replacing
a blob, and judge IN-ENGINE (pixels read differently at 48px in-context). Only batch the
rest once the style + the stressed pose land. Budget: Tier 1 = 2,000 img/mo; a full set is
~100–200 — plenty of headroom, but generate deliberately.

## Open for Pip
- Approve the layered model + style dials, or override.
- Pick / confirm the diverse base-body set (Fable will propose specifics on request).
- Confirm the test character (Fable nominates: pick a base whose silhouette + stressed
  pose stress-test the style hardest).
