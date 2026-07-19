# Fable music session -- kickoff brief

Paste-and-go context for a fresh Fable-model Claude Code session. Mission: compose
the adaptive "doom-band" music for P(Doom)1 -- Pip's own workshopped motifs. Foundation
now; a professional-dev friend patches real stems into the Godot engine later.

## Who's in the loop
Pip is the dev AND the musician. He listens iteratively through headphones and steers.
You propose patches; he judges by ear. He is the taste authority -- keep him in the loop,
don't run ahead. His old motifs are scaffold: supersede them, don't delete them.

## Aesthetic north stars (learn from, do NOT copy -- full detail in docs/audio/REFERENCE_TRACKS.md)
- Progressive / minimalist patterns (Philip Glass -- "Glassmaxxing"); tilt a little
  unsettling as doom rises.
- Cyclical, looped cells (Braided Hair intro).
- Ritual build-and-release at large scale (People Of The Drifting Houses); a pulse you
  can move to.
- Subtle orchestration + interesting harmony (The Staves, Glass, Nina's brass) over
  simple, distinct melodic material (Dengue Fever).
- One lyrical conceit: formulae / numbers as lyrics, harmonised. Thematically perfect for
  an AI-safety game.

## Reference tracks (in tools/music/ref_local/ -- for Pip's ears + numeric profiling)
- 01-04 People Of The Drifting Houses.mp3  -- ritual pulse, build/release
- 02-20 Knee55.mp3                          -- Philip Glass Knee Play 5, minimalism spine
- 03-09 Braided Hair.wav (.wma original)    -- looped-cell intro
- 04-01 Touch Me Not.flac                   -- Dengue Fever, simple distinct melody
- 05 Nina Simone - Feeling Good.mp3         -- the brass line
Analyzer: `python tools/music/analyze_refs.py tools/music/ref_local/*` (lands with the
music-kit PR) turns these into tempo/key/structure JSON = compositional seeds. Needs
`pip install librosa`; ffmpeg is already installed (decodes the mp3/wma). Profiles are an
enhancement, not a gate -- you can start composing from the descriptions + Pip's ears now.

## The system you're feeding
An adaptive "doom-band" music engine (PR #682). Doom has TWO axes:
- Catastrophe: amber -> red -> fire
- Weirdness: green (ok) -> blue (acting up) -> purple (eldritch)
Music shifts with doom state. Core cues stay stable; intensity is an ADDITIVE layer --
"doom is a layer, not a repaint" (glow/aura/colour-grade analogue in sound: extra
dissonance, detuning, density -- not a different song). The exact stem slots, the
doom-band -> cue mapping, and the required audio file format live in
docs/audio/MUSIC_DROPIN_KIT.md (lands with the kit). Produce stems that fit those slots so
the friend can drop them straight into Godot.

## Tooling approach
Strudel (browser, live-codeable, fastest to hear) and/or SuperCollider. Write a patch ->
Pip runs it -> listens -> steers. Prototype motifs per doom-band. The friend integrates
final stems into Godot later using the drop-in kit.

## First moves
1. Pick ONE doom-band to prototype -- suggest the calm early-game "green / ok" bed: a
   Glassy looped cell with a pulse you can move to.
2. Propose a first Strudel patch (small, hearable in seconds).
3. Pip listens, steers. Iterate.

## Constraints
ASCII only in repo files (enforce-standards hook). No emoji in source/docs.
