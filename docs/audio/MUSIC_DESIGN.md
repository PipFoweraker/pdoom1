# P(Doom)1 -- Music design spec (adaptive doom-band music)

> Music is the AUDIO expression of the existing doom-intensity spec
> (`docs/art/PALETTE_AND_DOOM_INTENSITY.md`). Same two axes, same five bands, same
> "cozy competence sliding toward existential dread" arc. This document is the reference
> for the musicians composing stems and for anyone touching
> `godot/autoload/music_manager.gd`. Companion docs: `STEM_CATALOGUE.md` (what audio we
> own today), `TRACK_ANALYSIS.md` (the taste reference method).

## 1. The model in one paragraph

Mick-Gordon / DOOM-style adaptive music: a small set of MUSIC TIERS (moods), each built
from LAYERED STEMS that add/subtract as doom rises. The game's doom value (0-100) is
read -- never written -- by the music system, quantized to the canonical doom bands, and
mapped to a tier. Tier changes crossfade horizontally (mood shift); within a tier, stems
stack vertically (intensity texture). Players should be able to close their eyes and
know roughly where the doom meter sits.

## 2. Axes -> music mapping

The art spec defines two independent axes plus combined bands. Each gets a musical
dimension:

| Axis (art spec) | Visual expression | MUSICAL expression |
|---|---|---|
| A. Catastrophe (amber -> red -> fire) | glow sours, strobes, literal fire | RHYTHM: percussive density and drive. Cosy = sparse/ambient pulse; alarmed = insistent percussion; fire = a dedicated "things are on fire" layer (alarm-adjacent textures, driving low end) entering at high tiers only |
| B. Weirdness (green -> blue -> violet) | clean -> glitchy -> eldritch glow | TIMBRE: clean/tonal instruments -> detuned, bit-crushed, glitch-stuttered -> dissonant clusters, wrong-scale intervals, reversed/smeared textures |
| Doom bands (0-4) | which register the office renders in | WHICH LAYERS ARE LIVE + overall mood/key territory |

Discipline rule, borrowed from the art spec's lighting rule ("at most ONE ambient +
ONE weird glow source"): at most ONE rhythmic driver and ONE weird/timbral accent
prominent at a time. Do not stack every layer at full volume even at terminal doom --
terminal reads as oppressive SPACE plus the fire layer, not as maximum loudness.
Purple is expensive; so is dissonance. Reserve overt eldritch harmony for tiers 3-4.

## 3. Music tiers (the five bands, made audible)

The game's canonical thresholds live in `ThemeManager.DOOM_STATUS_BANDS` (7 UI bands).
Music collapses them onto the art spec's 5 doom-intensity bands:

| Music tier | Name | UI bands (doom %) | Mood target | Rhythm (axis A) | Timbre (axis B) |
|---|---|---|---|---|---|
| M0 | cosy | NOMINAL (<15) | warm competence, focus | soft pulse or none | clean, tonal, warm (amber) |
| M1 | uneasy | ELEVATED + HIGH (15-52) | something is off | pulse gains weight, occasional stumble | faint detune/flicker creeping in |
| M2 | spooky | SEVERE + EXTREME (52-80) | shadows lengthen | insistent percussion, darker low end | glitch artifacts, blue-arcing synth |
| M3 | eldritch | CATASTROPHIC (80-92) | it has gone wrong in a wrong way | percussion fractures/polyrhythm | dissonant, wrong-scale, violet |
| M4 | terminal | TERMINAL (92+) | apocalyptic; the end is audible | FIRE layer in; driving or collapsed | full eldritch smear + alarms |

Numbers come from `ThemeManager` at runtime -- the music system holds NO thresholds of
its own, only the band->tier table `MUSIC_TIER_BY_BAND = [0,1,1,2,2,3,4]`. If Pip
retunes the bands, music follows automatically.

## 4. Layer/stem model (what the musicians compose)

Each tier is a STEM GROUP played in sync. Target stems per tier (a tier may omit some):

| Stem slot | Carries | Axis | Notes |
|---|---|---|---|
| BASE | harmony/bed, the mood itself | bands | always on within its tier; must loop seamlessly |
| PULSE | percussion/rhythm | A (catastrophe) | density scales with tier; absent at M0 is fine |
| WEIRD | timbral accent (detune/glitch/dissonance) | B (weirdness) | the "one weird glow" -- keep it a single identifiable voice |
| FIRE | the things-are-on-fire topper | A, high end | ONLY M3/M4 (like purple in the palette: expensive) |

Composition constraints so stems can be swapped/stacked mechanically:
- Every stem in a tier: same tempo, same key (or deliberate fixed relationship), same
  length or integer multiple, seamless loop, no reverb tails crossing the loop point
  (bake tails into the loop musically or keep them short).
- Adjacent tiers should share tempo or have a planned tempo relationship (e.g. M0-M2 at
  one tempo, M3-M4 at another) so crossfades between tiers do not churn.
- Deliver as separate files (wav or ogg preferred; mp3 acceptable), loudness roughly
  matched (about -16 LUFS integrated per stem; final balance happens in-engine).
- Names stay in the ML/AI-safety pun family (see `STEM_CATALOGUE.md`).

## 5. Runtime architecture (what is built, Godot 4.5.1 native)

No FMOD/Wwise. Two native primitives, already implemented in
`godot/autoload/music_manager.gd`:

- **Horizontal (tier moods): `AudioStreamInteractive`** -- one clip per tier, named
  `cosy/uneasy/spooky/eldritch/terminal`, with an any-to-any crossfade transition
  (8 beats at a nominal 120 BPM = 4 s). Tier changes call
  `AudioStreamPlaybackInteractive.switch_to_clip()`.
- **Vertical (stems within a tier): `AudioStreamSynchronized`** -- each clip's stream is
  a synchronized group of that tier's stems with per-stem volume offsets. Today most
  tiers hold a single placeholder track; the `terminal` tier already layers two tracks
  to keep the synchronized path exercised.

Signal flow (read-only, view-layer):

```
GameManager.game_state_updated(state)          # existing broadcast, emitted per turn
  -> MusicManager._on_game_state_for_music     # reads state["doom"], nothing else
    -> ThemeManager.get_doom_band_index(doom)  # canonical band (0..6)
      -> MUSIC_TIER_BY_BAND[band]              # music tier (0..4)
        -> switch_to_clip(tier)                # native crossfade if tier changed
```

### Hard rules (ADR-0006: the replay string is the canonical run artifact)
- Audio is a PURE view-layer side-effect. `MusicManager` only LISTENS to
  `game_state_updated`; it never calls into game code, never touches the seeded RNG,
  the turn loop, replay, or any state that could perturb determinism.
- Never block or crash on missing audio: a missing stem is skipped, an empty tier
  inherits its neighbour's stream, a fully-empty build falls back to the legacy
  playlist, and no music at all is silence, not an error.
- `randi()` use for playlist shuffle is the GLOBAL RNG, not the seeded game RNG --
  keep it that way; never "fix" music shuffle by borrowing the game's RNG.

## 6. Transition rules

Current prototype: single any-to-any rule -- switch immediately, crossfade over 8 beats
(4 s), restart target clip from its start. Deliberately simple; placeholder tracks share
no tempo grid, so beat-aligned transitions would be false precision.

Target rules once composed stems exist (all native `AudioStreamInteractive` features):
- UP-tier (doom rose): transition at NEXT BEAT, short crossfade (1-2 bars). Rising dread
  should feel prompt -- the ratchet.
- DOWN-tier (doom fell -- rare, earned): transition at NEXT BAR or phrase end, long lazy
  crossfade. Relief arrives slower than fear.
- M3 -> M4 (terminal): consider a FILLER CLIP sting (a one-shot "it is happening"
  hit) via the native filler-clip transition option.
- Hysteresis: band quantization already gives dead zones; if doom oscillates across one
  boundary each turn and audibly churns, add a 1-turn dwell before down-transitions
  (do NOT add one for up-transitions; the ratchet must feel immediate).

## 7. Where composed tracks slot in

One place: `MUSIC_TIER_STEMS` in `godot/autoload/music_manager.gd` -- an array of five
stem lists, `{"path": ..., "volume_db": ...}` per stem. Replacing a placeholder track
with real per-tier stems is a data edit, no logic change. Contexts outside GAMEPLAY
(menu / victory / defeat) stay on the existing `music_library` playlists; a future
victory track and a composed defeat sting slot in there.

Menu music stays NON-adaptive on purpose: the menu has no doom.

## 8. Out of scope / anti-goals

- No AI-generated finished music (rights are murky; Pip values owning rights).
- No per-action stingers wired to game logic (would tempt writes into the turn loop;
  any future stinger hooks must also be listen-only).
- No rewrite of the audio bus layout; the Music bus (index 2) is the only one touched.
