# Music reference tracks -- Pip's aesthetic north stars

> Captured 2026-07-17 so they persist beyond any chat. These are the emotional/structural
> references for P(Doom)1's music direction -- to brief musicians (and the generative-music
> experiments) on what the game should FEEL like. Not tracks to copy; tracks to learn from.
> Measured features appended below (local analysis of Pip's own library copies; features are
> facts and carry no rights baggage -- the audio itself stays out of the repo).

## The most beloved
**Master Musicians Of Bukkake -- People Of The Drifting Houses** (Totem One). Pip listens
2-3x/day, ~1.5 years.
- Delightful to try to dance or walk to.
- A **ritualistic** core, **bookended by the whole album's build-up and subsequent denouement**.
- Take-home for us: ritual pulse you can move to; large-scale build-and-release framing the piece.

## The stylistically-relevant top-played set
- **Braided Hair -- Speech feat. 1 Giant Leap** -- the *intro loops* specifically (looped cells).
- **Touch Me Not -- Dengue Fever** -- evocative, distinct, **simple instrumental melody**.
- **Feeling Good -- Nina Simone** -- "one of the best progressive brass lines of all time" (Pip).
- **Wisely and Slow -- The Staves** -- beautifully, interestingly **harmonised**. Pip: if the game
  ever has lyrics they will likely be a **pure transliteration of formulae / numbers**, harmonised
  like this. (Formulae-as-lyrics -- a strong, on-theme conceit for an AI-safety game.)
- **Philip Glass -- Knee Play 1, and *especially* Knee Play 5** (Einstein on the Beach). Pip's ~2nd
  favourite song ever. **"Philip Glassmaxxing"** -- progressive patterns + subtle orchestration.
  For us: slightly more **unsettling** versions of that minimalism.

## The synthesis (what these share -> our direction)
- **Progressive / minimalist patterns** (Glass), **cyclical, looped cells** (Braided Hair intro).
- **Ritual build-and-release** at large scale (Bukkake), you-can-move-to-it pulse.
- **Subtle orchestration + interesting harmony** (Staves, Glass, Nina's brass) over simple,
  distinct melodic material (Dengue Fever).
- **Formulae/numbers as lyrics**, harmonised -- the one lyrical idea, and it's thematically perfect.
- Tilt everything a little **unsettling** as doom rises (per the doom-intensity spec's weirdness axis).

Main theme lives in the title / main menu screen.

## Measured features (2026-07-17, hand-rolled DSP: ffmpeg + numpy)

Caveats: BPM values are dominant-periodicity estimates (can alias to 2x/4x of the felt
tempo -- Feeling Good's 215 is ~4x of a ~54 BPM ballad pulse); key guesses on drone/modal
material name a TONAL CENTER, not a functional key; centroid/loudness comparisons across
different masterings are rough. Good enough to set direction, not to transcribe.

| Track | Dur | BPM~ (conf) | Center (top chroma) | Bright (centroid) | Low<150Hz | Dyn p90-p10 | Loudness arc (8ths, dB rel peak) |
|---|---|---|---|---|---|---|---|
| MMOB -- People Of The Drifting Houses | 7.5 min | 83.4 (0.73) | D modal (D,A,C) | 1785 Hz | 10.6% | 11.4 dB | -11,-6,-5,-4,-3,-2,0,-11 |
| Braided Hair (full) | 4.1 min | 99.4 (0.67) | F-ish (C,D,A) | 2177 Hz | 14.9% | 13.7 dB | -15,-4,-2,-3,-1,-2,0,-13 |
| Braided Hair (intro 45 s) | -- | 99.4 (0.60) | (C,D,F) | 974 Hz | 25.6% | 17.9 dB | staircase: -20,-10,-9,-10,-4,-3,-2,0 |
| Dengue Fever -- Touch Me Not | 4.4 min | 66.3 (0.58) | D modal (D,A,C) | 1463 Hz | 22.3% | 10.2 dB | -5,-1,-2,-1,-1,-2,0,-12 |
| Nina Simone -- Feeling Good | 2.9 min | ~54 felt (alias 215) | D minor (D,G,A) | 1985 Hz | 3.3% | 25.1 dB | -22,-15,-3,-2,-4,-3,0,-14 |
| The Staves -- Wisely & Slow | 3.6 min | 123.0 (0.69) | Bb major (Bb,G,D) | 1586 Hz | 8.2% | 25.5 dB | -18,-14,-13,-8,-9,-7,0,-8 |
| Glass -- Knee Play 1 (1976) | 3.9 min | 103.4 (0.63) | C (C,D,G) | 1245 Hz | 24.0% | 5.5 dB | -9,-4,-3,-3,-2,0,0,-2 |
| Glass -- Knee Play 5 (1976) | 5.5 min | 112.3 (0.51) | C (C,A,G) | 1143 Hz | 33.4% | 4.9 dB | -4,-3,-3,-3,-3,-1,0,-7 |

### What the numbers confirm (measured, not vibes)
1. **The beloved track's shape is Pip's description, verbatim**: a six-segment monotonic
   climb (-11 dB -> 0) then a -11 dB denouement. Ritual build-and-release, measured.
2. **Braided Hair's intro is a loudness STAIRCASE** (-20 -> 0 in steps): additive loop-cell
   layering -- exactly the vertical stem-stacking model in MUSIC_DESIGN.md section 4.
3. **Glass sits nearly FLAT** (dyn ~5 dB): hypnosis inside a section, terraces between
   sections. Within-tier stems should behave like this; the TIER LADDER supplies the build.
4. **A shared modal center**: beloved + Dengue Fever both center D with A and C prominent
   (drone fifth + flat-7 -- mixolydian/dorian territory); Glass and the friend-made repo
   tracks center C with D/G prominent. A C/D modal-drone tonal home, avoiding functional
   leading-tone cadences, matches BOTH the taste profile and the existing game audio.
5. **Tempo lanes converge**: beloved 83 BPM; repo gameplay tracks' half-time equivalents
   ~81-92; Glass patterns ~103-112. Suggests a ~84 BPM "ritual heartbeat" lane for beds
   and a ~104-112 pattern lane for Glass-cell layers.
6. **Knee Play 1 is literally sung numbers** -- Pip's formulae-as-lyrics conceit has a
   direct ancestor in his second-favourite piece. The main theme can lean on this hard.

### Direction distilled (for the music lab and the musicians)
- Tonal home: C/D modal drone (fifth + flat-7), no functional cadences -- doom never resolves.
- Pulse: ~84 BPM ritual heartbeat you can walk/sway to; pattern layers may run ~104-112.
- Structure: flat hypnotic cells within a tier; the doom-tier ladder IS the large-scale
  build; defeat (Out_of_distribution) and victory serve as the denouement bookend.
- Arrivals: stems enter as Braided-Hair-style staircase events players can learn to await.
- Harmony/voices: simple distinct melodic cells; close vocal-style harmony reserved for the
  title theme; lyrics, if ever, are transliterated formulae/numbers (Knee-Play-1-maxxing).
- Unsettling tilt scales with the weirdness axis: detune/dissonance budget grows with tier.
