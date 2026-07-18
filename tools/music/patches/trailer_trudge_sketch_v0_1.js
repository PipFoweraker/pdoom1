// P(Doom)1 music -- TRAILER TRUDGE sketch v0.1 (the Factorio-zoom-out vision)
// Paste whole block at https://strudel.cc, Ctrl+Enter plays, Ctrl+. stops.
// 32-bar through-composed arc, ~2 minutes at 63 bpm. Let it run to the end.
//
// Pip's vision 2026-07-18: trudge... IMPACT (loop), the work spreading as we
// zoom out -- and the rivals growing FASTER than us, doom visible, inevitable,
// and we step forward in line anyway. "Next!"
//
// Structure (bars):
//   1-8    one person in line: steps, drone, plod
//   9-16   the dirge (AAAB) -- the player starts working
//   17-24  work spreads: hats + shakuhachi ghost + THE RIVAL's first call
//   25-32  zoom out: steps double, high air opens, rival recurs at HALVING
//          intervals -- gaps of 8, 4, 2, 1 bars = exponential growth made
//          audible. The dirge never speeds up. We trudge; it compounds.
//
// Dramaturgy rule (new): HUMAN voices = organic register (cello, shakuhachi,
// drums, bass -- placeholders for real players + Pip's chant). THE RIVAL is
// the only voice allowed to sound purely synthetic (clean saw, bitcrush,
// no room). The "generated MIDI chord" coldness is now a CHARACTER.

setcpm(63/4)

stack(
  // -- the snow (whole piece) --
  s("white").attack(2).release(3).sustain(1)
    .lpf(400).gain(0.05).room(0.8),

  note("[d2,a2]").sound("sawtooth")
    .lpf(240).gain(0.2).room(0.6).attack(1.5),

  // -- the line: footsteps + plod, never accelerating (humans don't scale) --
  s("lt ~ ~ lt ~ ~ lt ~").bank("RolandTR808")
    .velocity("1 0 0 0.6 0 0 0.75 0").degradeBy(0.08)
    .gain(0.75).lpf(650).room(0.3),

  note("d1 ~ ~ a1 ~ ~ d1 ~").sound("gm_acoustic_bass")
    .clip(0.8).gain(0.8).lpf(380),

  // -- the work: dirge enters bar 9 (AAAB, the wibbly tail intact) --
  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D3:dorian").sound("gm_cello")
    .clip(1.6).gain(0.5).room(0.5).pan(0.4)
    .mask("<0!8 1!24>"),

  // -- work spreads (bar 17): more hands, higher registers --
  s("[~ hh]*4").bank("RolandTR808")
    .gain(0.15).mask("<0!16 1!16>"),

  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D4:dorian").sound("gm_shakuhachi")
    .clip(1.4).gain(0.28).room(0.8).pan(0.65)
    .mask("<0!16 1!16>"),

  // -- zoom out (bar 25): the camera rises, the world is bigger than us --
  s("lt*8").bank("RolandTR808")
    .velocity("0.5 0.3 0.4 0.3 0.5 0.3 0.4 0.35")
    .gain(0.4).lpf(800).mask("<0!24 1!8>"),

  note("[d5,a5]").sound("triangle")
    .attack(2).gain(0.1).room(0.9).mask("<0!24 1!8>"),

  // -- THE RIVAL: rising synthetic call, recurrence gaps halving 8->4->2->1.
  //    Each return is higher. It does not breathe. It does not miss steps. --
  n("<~!16 [0 4 7] ~!7 [2 5 8] ~!3 [4 7 10] ~ [5 8 11] [7 10 12]>")
    .scale("D4:dorian")
    .sound("sawtooth").crush(6)
    .clip(0.5).gain(0.45).lpf(2500).pan(0.7)
)
