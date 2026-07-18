# Mick Gordon (DOOM 2016/Eternal) -- philosophy, and what P(Doom)1 derives from it

The music design spec (docs/audio/MUSIC_DESIGN.md section 1) names the model
"Mick-Gordon / DOOM-style adaptive music". This note goes one level deeper into
HOW Gordon worked and derives concrete rules for our stems.

Provenance warning: written from Claude's training knowledge of Gordon's GDC 2017
talk "DOOM: Behind the Music" and contemporaneous interviews. Claims are marked
by confidence. Primary source to verify against (and worth Pip's 60 minutes):
the GDC talk on YouTube -- search "GDC DOOM Behind the Music Mick Gordon".

## The principles (high confidence unless flagged)

1. "Change the process, change the sound." Gordon's core method: novel signal
   chains produce novel identity. The famous example: sine waves fed through
   chains of distortion/pedals ("the Doom instrument") rather than stock synth
   presets. The instrument IS the aesthetic.

2. Embrace the artifact. Aliasing, bitcrush, clipping -- normally engineering
   failures -- were promoted to musical material, matching the game's
   hell-meets-tech fiction. The damage is diegetic.

3. Intensity = register expansion, not just volume. Low-tuned 7/8/9-string
   guitars extend the spectrum DOWN as intensity rises [medium confidence on
   string counts; the register principle itself is solid]. Loudness is the
   cheapest and least interesting intensity axis.

4. Silence is structural. DOOM 2016 pulls music back hard in exploration so
   combat entrances LAND. The absence is composed, not incidental.

5. Rhythm can come from gating, not drumming. Rhythmic sidechain/gate chopping
   of sustained textures gives pulse without a drum kit [medium confidence as
   Gordon-specific; standard in his genre and audible in the scores].

6. Motif discipline. Legacy material (E1M1 etc.) appears sparingly, warped,
   as payoff -- not wallpaper.

## Derivations for P(Doom)1 stems

D1 (from 1): Build a "P(Doom) instrument". Our equivalent chain: friend-recorded
   ACOUSTIC sources (taiko, shakuhachi, double bass, voice) mangled through
   mechanical/degradation processing (tape wobble, CRT-refresh AM, bit reduction)
   for WEIRD and FIRE stems. The friend's "BIOS glitching" SFX already point
   here -- same chain family, tamer settings for music. Never stock preset pads
   for the weird layer: the weirdness should sound like OUR process.

D2 (from 2): The artifact ladder maps to the weirdness axis literally:
   green = clean signal, blue = process artifacts audible (crush(8), light AM),
   purple = the artifact eats the signal (crush(4), spectral smear, reverse).
   One knob family, three depths -- consistent with "doom is a layer".

D3 (from 3): Tier ladder expands register outward, not louder. Green lives in
   the mids (our bed already does). Each tier up adds spectrum: uneasy adds
   low 8ths, spooky adds sub + air hats, terminal = full-range oppression at
   MODERATE loudness (the kit's -16 LUFS discipline enforces this).

D4 (from 4): Confirms two Pip rules independently: the anti-Tarkov-generator
   rule (constant texture = fatigue; composed absence = attention) and the zen
   standoff moments (see patches/zen_standoff_sketch_v0_1.js). Also suggests:
   when doom TIER RISES, consider a half-beat of thinning right before the new
   layer enters -- the pullback that makes the entrance land.

D5 (from 5): PULSE stems do not require a drummer. A gated/chopped version of
   the tier's own BASE stem is a valid PULSE stem -- cheap to produce, perfectly
   key-coherent, and it makes catastrophe feel like the SAME room shaking
   rather than a drummer walking in. Real taiko then tops the high tiers where
   a human hitting something huge means something.

D6 (from 6): The green cell (the 8-note C major arpeggio Pip approved
   2026-07-17) is our E1M1. It should recur in every tier, progressively
   warped by the D2 ladder -- and maybe once, pure, at the moment of victory.

## Divergences (where we are NOT Gordon)

- Gordon scores POWER (you are the demon's problem). P(Doom)1 scores DREAD
  (you are losing control of the thing you built). Same layering machinery,
  inverted emotional polarity: his intensity empowers, ours encroaches.
- His palette is metal; ours is minimalism/new-age lineage (Glass, Ray Lynch)
  with acoustic-ritual percussion. We take the PROCESS philosophy, not the
  genre.
- Combat-loop music must slam in milliseconds; turn-based doom can afford
  4-second crossfades and slow ratchets. We can be patient in ways he could
  not.
