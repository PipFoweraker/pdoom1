// P(Doom)1 music -- "TRUDGE" defeat/welcome-back cue, v0.1
// Paste whole block at https://strudel.cc, Ctrl+Enter plays, Ctrl+. stops.
//
// Pip's brief 2026-07-18: when you die, the game welcomes you back with a
// soviet-era papers-please trudge-forward-in-the-snow feeling -- but NO
// oompah/tuba brass-band anything. Esoteric instrument set instead:
// taiko-adjacent low drums, upright-bass-ish plod, drone, shakuhachi ghost.
//
// Also answers "the seven-loop is boppy and too short": here the musical
// phrase is LONG. One cycle = one slow 4/4 bar at 63 bpm; the melody is an
// AAAB 4-bar phrase (the Drifting Houses lesson); layers arc over 16 bars
// (~61 s before the full shape repeats). Limping 3+3+2 footsteps, not a bop.
//
// Organic-grit pass: velocities vary, and degradeBy makes the walker
// occasionally MISS a step -- manual imperfection, not grid perfection.
// (GM sounds remain placeholders: final stems = real taiko/bass/voice.)
//
// CHANT SLOT: layer 7 is reserved -- this is where Pip's recorded math-chant
// vocal will sit, processed MMoB-style. The drone is tuned to D so chanting
// against this patch stays easy: hum a D, speak-chant on it.

setcpm(63/4)

stack(
  // 1) Snow-wind: soft noise wash (if "white" errors in your Strudel, delete)
  s("white")
    .attack(2).release(3).sustain(1)
    .lpf(400).gain(0.05).room(0.8),

  // 2) The valley drone: open fifth in D, always present
  note("[d2,a2]").sound("sawtooth")
    .lpf(240).gain(0.2).room(0.6).attack(1.5),

  // 3) Footsteps: limping 3+3+2 low drum, soft-edged, sometimes missing
  s("lt ~ ~ lt ~ ~ lt ~")
    .bank("RolandTR808")
    .velocity("1 0 0 0.6 0 0 0.75 0")
    .degradeBy(0.08)
    .gain(0.75).lpf(650).room(0.3),

  // 4) Upright plod: bass doubles the steps, drags slightly behind the drone
  note("d1 ~ ~ a1 ~ ~ d1 ~")
    .sound("gm_acoustic_bass")
    .clip(0.8).velocity("0.9 0 0 0.7 0 0 0.8 0")
    .gain(0.8).lpf(380),

  // 5) The dirge line: AAAB phrase, enters bar 5. Cello = organic placeholder.
  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D3:dorian")
    .sound("gm_cello")
    .clip(1.6).gain(0.5).room(0.5).pan(0.4)
    .mask("<0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1>"),

  // 6) Shakuhachi ghost: doubles the dirge an octave up, bars 11-16 only --
  //    the zen face appearing through the snow late in the arc
  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D4:dorian")
    .sound("gm_shakuhachi")
    .clip(1.4).gain(0.3).room(0.8).pan(0.65)
    .mask("<0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1>")

  // 7) CHANT SLOT (future): Pip's voice, low D recitation, reversed/smeared
  //    per Master Musicians treatment. Recorded, not synthesized.
)
