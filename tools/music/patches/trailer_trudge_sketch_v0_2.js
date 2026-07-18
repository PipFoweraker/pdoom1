// P(Doom)1 music -- TRAILER TRUDGE sketch v0.2: the overwhelm ending
// Paste whole block at https://strudel.cc, Ctrl+Enter plays, Ctrl+. stops.
// 42 bars, ~2:40 at 63 bpm. THROUGH-COMPOSED -- listen start to finish.
//
// v0.2 changes (Pip 2026-07-18): trailers end, loops don't -- sharper finish,
// obvious crescendo. The ending states the pitch in sound:
//   bars 33-36  rival goes CONTINUOUS -- 8 notes/bar, climbing
//   bars 37-39  rival goes IMPOSSIBLE -- 32 notes/bar (the 13-notes-a-second
//               rave-doof "no human dances this fast" wall), still climbing.
//               The humans DO NOT accelerate and DO NOT falter. We hold.
//   bar 40      IMPACT. Hard cut. Everything stops.
//   bar 41      silence. (Real silence -- even the wind stops.)
//   bar 42      the button: ONE soft footstep and one low breath-note.
//               "Next!" -- we step forward anyway. The thesis in one gesture.
//
// The overwhelm never ARRIVES -- it is only made inevitable. Per the ruling:
// artificial = clean/gridded/dry; human = organic/roomed/missing steps.

setcpm(63/4)

stack(
  // -- the snow --
  s("white").attack(2).release(3).sustain(1)
    .lpf(400).gain(0.05).room(0.8)
    .mask("<1!39 0!3>"),

  note("[d2,a2]").sound("sawtooth")
    .lpf(240).gain(0.2).room(0.6).attack(1.5)
    .mask("<1!39 0!3>"),

  // -- the line: steady the whole way. humans don't scale; humans hold. --
  s("lt ~ ~ lt ~ ~ lt ~").bank("RolandTR808")
    .velocity("1 0 0 0.6 0 0 0.75 0").degradeBy(0.08)
    .gain(0.75).lpf(650).room(0.3)
    .mask("<1!39 0!3>"),

  note("d1 ~ ~ a1 ~ ~ d1 ~").sound("gm_acoustic_bass")
    .clip(0.8).gain(0.8).lpf(380)
    .mask("<1!39 0!3>"),

  // -- the work: dirge, bars 9-39 --
  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D3:dorian").sound("gm_cello")
    .clip(1.6).gain(0.5).room(0.5).pan(0.4)
    .mask("<0!8 1!31 0!3>"),

  // -- work spreads: bars 17-39 --
  s("[~ hh]*4").bank("RolandTR808")
    .gain(0.15).mask("<0!16 1!23 0!3>"),

  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D4:dorian").sound("gm_shakuhachi")
    .clip(1.4).gain(0.28).room(0.8).pan(0.65)
    .mask("<0!16 1!23 0!3>"),

  // -- zoom out: bars 25-39 --
  s("lt*8").bank("RolandTR808")
    .velocity("0.5 0.3 0.4 0.3 0.5 0.3 0.4 0.35")
    .gain(0.4).lpf(800).mask("<0!24 1!15 0!3>"),

  note("[d5,a5]").sound("triangle")
    .attack(2).gain(0.1).room(0.9).mask("<0!24 1!15 0!3>"),

  // -- THE RIVAL, phase 1: discrete calls, gaps halving 8->4->2->1 --
  n("<~!16 [0 4 7] ~!7 [2 5 8] ~!3 [4 7 10] ~ [5 8 11] [7 10 12] ~!10>")
    .scale("D4:dorian")
    .sound("sawtooth").crush(6)
    .clip(0.5).gain(0.45).lpf(2500).pan(0.7),

  // -- phase 2 (bars 33-36): continuous, 8/bar, climbing each bar --
  n("0 4 7 11".fast(2).add("<12 14 16 17>"))
    .scale("D4:dorian")
    .sound("sawtooth").crush(6)
    .clip(0.6).gain(0.4).lpf(3000).pan(0.7)
    .mask("<0!32 1!4 0!6>"),

  // -- phase 3 (bars 37-39): impossible speed, the wall --
  n("0 4 7 11".fast(8).add("<19 21 24>"))
    .scale("D4:dorian")
    .sound("sawtooth").crush(7)
    .clip(0.8).gain(0.33).lpf(4500).pan("0.6 0.8")
    .mask("<0!36 1!3 0!3>"),

  // -- bar 40: IMPACT. bar 41: silence. --
  s("[lt,bd]").bank("RolandTR808")
    .gain(1.0).lpf(500).room(0.9)
    .mask("<0!39 1 0 0>"),

  // -- bar 42: the button. one footstep, one breath. "Next!" --
  s("lt ~ ~ ~ ~ ~ ~ ~").bank("RolandTR808")
    .velocity(0.5).gain(0.6).lpf(600).room(0.4)
    .mask("<0!41 1>"),

  note("d2 ~ ~ ~").sound("gm_cello")
    .clip(2).gain(0.35).room(0.7)
    .mask("<0!41 1>")
)
