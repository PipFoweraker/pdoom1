// P(Doom)1 music -- GREEN bed v0.3: development arc
// Paste whole block at https://strudel.cc, Ctrl+Enter plays, Ctrl+. stops.
//
// Response to Pip 2026-07-18: v0.1's spine was a static 1-bar up-down scale --
// "drilling into my ears", "childish". Real Glass develops by PROCESS: cells
// rotate/mutate, layers enter and leave on a schedule. And the zen sketch
// proved entrances-you-wait-for are the good stuff. So v0.3:
//   - 16-bar breathing arc: each layer has a mask() = which bars it sounds.
//     Layers stage in (bass -> spine -> counter -> hats -> kick), a sparkle
//     payoff arrives at bar 13, bar 15 is a composed breath, then it wraps.
//   - spine contour is leapier (arpeggio jumps, not a ladder) and iter(4)
//     rotates its starting note each bar -- never identical twice running.
//   - harmony is a 4-chord cycle over 8 bars (C Am F G in scale-degree
//     shifts) instead of the two-chord seesaw.
// One cycle = one bar; full arc = 16 bars ~ 37 s at 104 bpm.

setcpm(104/4)

stack(
  // 1) Spine v2: leaping contour, rotating start, rests on bar 15
  n("0 4 2 7 4 9 7 11".add("<0 -2 -4 -3>/2"))
    .scale("C4:major")
    .iter(4)
    .sound("gm_epiano1")
    .gain(0.72).room(0.35).pan(0.3)
    .mask("<1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 1>"),

  // 2) Counter-cell (6/bar shimmer): enters bar 3, steps out for the payoff
  n("2 4 7 9 7 4".add("<0 -2 -4 -3>/2"))
    .scale("C5:major")
    .sound("gm_marimba")
    .gain(0.38).room(0.5).pan(0.7)
    .mask("<0 0 1 1 1 1 1 1 1 1 1 1 0 0 1 1>"),

  // 3) Bass: the constant. Present from bar 1, carries the chord cycle.
  n("0 ~ 0 ~".add("<0 -2 -4 -3>/2"))
    .scale("C2:major")
    .sound("gm_acoustic_bass")
    .clip(0.6).gain(0.85).lpf(400),

  // 4a) Hats arrive bar 5...
  s("[~ hh]*4").bank("RolandTR808")
    .gain(0.22)
    .mask("<0 0 0 0 1 1 1 1 1 1 1 1 1 1 0 1>"),

  // 4b) ...kick arrives bar 7 (staged entrances, the zen lesson)
  s("bd ~ [~ bd] ~").bank("RolandTR808")
    .gain(0.32)
    .mask("<0 0 0 0 0 0 1 1 1 1 1 1 1 1 0 1>"),

  // 5) Sparkle payoff: bars 13-14 only -- the thing you waited for
  n("14 11 9 11")
    .scale("C5:major")
    .sound("gm_music_box")
    .gain(0.35).room(0.7).pan(0.6)
    .mask("<0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0>")
)
