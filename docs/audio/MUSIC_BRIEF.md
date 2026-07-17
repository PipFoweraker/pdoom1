# P(Doom)1 -- music brief (for a bounded Fable run)

> Scoped brief for a ~3-hour parallel run (Fable or fresh session). Goal: a music DESIGN + a
> working adaptive-music PROTOTYPE + a stem catalogue -- NOT finished composed tracks (those come
> from Pip's musician friends / owned stems later). Tightly scoped on purpose: audio is isolated,
> so this should NOT sprawl into dozens of subagents.

## The vision (Pip's, sharpened)
Mick-Gordon / DOOM-style **adaptive music**: layered stems that add/subtract and modulate to
**ratchet tension**, with enough creative space that players don't get bored. The key insight:
**music is the AUDIO expression of the existing doom-intensity spec** (`docs/art/PALETTE_AND_DOOM_INTENSITY.md`).
Reuse that architecture -- do not invent a new intensity model.
- **Catastrophe axis** (amber->red->fire) -> rhythmic/percussive intensity + a "things are on fire"
  layer entering at high tiers.
- **Weirdness axis** (green=ok -> blue=acting-up -> violet=eldritch) -> timbre: clean/tonal ->
  detuned/glitchy -> dissonant/eldritch.
- **Doom bands** (cosy -> uneasy -> spooky -> eldritch -> terminal) -> which layers are live and
  the overall mood, cozy-competence sliding toward existential dread.

## What already exists (build ON this, don't replace wholesale)
- **`godot/autoload/music_manager.gd`** -- context-based crossfade (MENU / GAMEPLAY / VICTORY /
  DEFEAT), 2-player crossfade, MUSIC_BUS_INDEX 2. The upgrade is making GAMEPLAY doom-band-adaptive.
- **Tracks** in `godot/assets/audio/music/` (DJ-session ambient, Pip owns full rights; names are
  ML/AI-safety puns worth preserving): `Descent gradient`, `Local maxima`, `Power spike`,
  `Undetected sandbagging` (gameplay), `Out_of_distribution` (defeat), `PDOOMN ST1 (safe)` +
  `selection beeyoowee` (menu).
- **SFX** in `sounds/` (blob, warningbeep, suddendeath, rocket*, zabinga, popup_close).
- **Godot 4.5.1** ships `AudioStreamInteractive` (clip-based adaptive music with transition rules)
  and `AudioStreamPlaylist`/`AudioStreamSynchronized` -- native adaptive music, no FMOD/Wwise needed.

## Deliverables (all four; keep each tight)
1. **Music-design spec** (`docs/audio/MUSIC_DESIGN.md`) -- the axes->music mapping above, the
   layer/stem model, how doom band selects layers, transition rules, where composed tracks will
   slot in. The reference the musicians will read.
2. **Working adaptive prototype** (Godot) -- extend `music_manager.gd` (or an adaptive sub-system)
   using `AudioStreamInteractive`/`Synchronized`, driven by a READ-ONLY doom-band signal, using the
   existing tracks as PLACEHOLDER layers/clips. It must audibly shift with doom in-game. Placeholder
   audio is fine -- the point is the plumbing.
3. **Stem + track catalogue** (`docs/audio/STEM_CATALOGUE.md`) -- every existing track + SFX: name
   (preserve the puns!), length, vibe, rights (Pip owns the DJ stems), and a usability/coherence
   note + gaps to fill. This is the "keep the track names + assess what we have" ask.
4. **Beloved-track analysis** (`docs/audio/TRACK_ANALYSIS.md`) -- Pip has a track he listens to
   2-3x/day; he'll supply the name/link separately. Produce the ANALYSIS METHOD + a template
   (tempo/key/instrumentation/structure/production/*why it grips* -> actionable direction in plain
   language for a low-literacy owner). If the track name is provided in the run, fill it in.

## Hard constraints
- **Determinism / replay is sacred (ADR-0006).** Audio is a PURE view-layer side-effect. The music
  system may only READ a doom-band value; it must NEVER write game state, touch the seeded RNG, the
  turn loop, or replay. Hook it where other view code reads doom.
- **Never block/crash on missing audio.** Degrade gracefully.
- **Verify:** fast gate `python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300` -> 0
  failures; simulation/determinism tier -> 0 failures (prove audio didn't touch determinism).
- **Scope discipline:** this is ONE focused pass. Do not spawn a fleet. Do not attempt to compose
  finished music (out of scope -- that's the human musicians / owned stems). Placeholder + system + spec.
- Branch `feat/adaptive-music`, PR (do not merge). Stage only what you changed; no .import/.uid/settings churn.

## Not in scope (say so if tempted)
Composing/generating actual finished tracks; AI-music-gen (rights are murky and Pip values owning
rights); rewriting the whole audio bus setup.
