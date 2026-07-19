// P(Doom)1 music -- TRAILER TRUDGE sketch v0.3: smear open + overwhelm end
// Paste whole block at https://strudel.cc, Ctrl+Enter plays, Ctrl+. stops.
// 44 bars, ~2:47 at 63 bpm. THROUGH-COMPOSED -- listen start to finish.
//
// v0.3 (Pip's rulings 2026-07-18):
//   OPEN  = weird-smear tease (horror-trailer grammar): bars 1-2 are the
//           DIRGE ITSELF corrupted -- reversed, crushed, tritone air --
//           because doom has no theme, it only ruins ours. The audience
//           hears the ruined future first. A dry snap cuts to the present.
//   BUTTON = lone footstep + breath (kept from v0.2). We step forward anyway.
//
// Timeline: 1-2 smear | 3 the line begins | 11 dirge | 19 spread + rival
// calls (gaps 8-4-2-1) | 27 zoom out | 35 rival continuous | 39 rival
// impossible | 42 IMPACT | 43 silence | 44 one footstep. "Next!"

setcpm(63/4)

stack(
  // ---- BARS 1-2: the ruined future (dirge B-phrase, corrupted) ----
  n("[~ 0 ~ 3 [2 1] 0 ~ ~]")
    .scale("D3:dorian")
    .rev()
    .sound("sawtooth").crush(4)
    .vib(4).vibmod(0.5)
    .clip(1.8).lpf(900).gain(0.4).room(0.9)
    .mask("<1!2 0!42>"),

  note("[d3,gs3]")                       // tritone air: d against g# = wrong
    .sound("sawtooth")
    .lpf(500).vib(0.7).vibmod(0.3)
    .gain(0.14).room(0.9).attack(0.5)
    .mask("<1!2 0!42>"),

  // the snap: one dry rimshot at the end of bar 2 -- cut to reality
  s("~ ~ ~ ~ ~ ~ ~ rim").bank("RolandTR808")
    .gain(0.8).hpf(1500)
    .mask("<0 1 0!42>"),

  // ---- BARS 3-41: the present (v0.2 body, shifted) ----
  s("white").attack(2).release(3).sustain(1)
    .lpf(400).gain(0.05).room(0.8)
    .mask("<0!2 1!39 0!3>"),

  note("[d2,a2]").sound("sawtooth")
    .lpf(240).gain(0.2).room(0.6).attack(1.5)
    .mask("<0!2 1!39 0!3>"),

  s("lt ~ ~ lt ~ ~ lt ~").bank("RolandTR808")
    .velocity("1 0 0 0.6 0 0 0.75 0").degradeBy(0.08)
    .gain(0.75).lpf(650).room(0.3)
    .mask("<0!2 1!39 0!3>"),

  note("d1 ~ ~ a1 ~ ~ d1 ~").sound("gm_acoustic_bass")
    .clip(0.8).gain(0.8).lpf(380)
    .mask("<0!2 1!39 0!3>"),

  // dirge, bars 11-41 -- the same phrase the smear ruined, now whole
  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D3:dorian").sound("gm_cello")
    .clip(1.6).gain(0.5).room(0.5).pan(0.4)
    .mask("<0!10 1!31 0!3>"),

  // spread, bars 19-41
  s("[~ hh]*4").bank("RolandTR808")
    .gain(0.15).mask("<0!18 1!23 0!3>"),

  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D4:dorian").sound("gm_shakuhachi")
    .clip(1.4).gain(0.28).room(0.8).pan(0.65)
    .mask("<0!18 1!23 0!3>"),

  // zoom out, bars 27-41
  s("lt*8").bank("RolandTR808")
    .velocity("0.5 0.3 0.4 0.3 0.5 0.3 0.4 0.35")
    .gain(0.4).lpf(800).mask("<0!26 1!15 0!3>"),

  note("[d5,a5]").sound("triangle")
    .attack(2).gain(0.1).room(0.9).mask("<0!26 1!15 0!3>"),

  // THE RIVAL phase 1: discrete calls at bars 19, 27, 31, 33, 34
  n("<~!18 [0 4 7] ~!7 [2 5 8] ~!3 [4 7 10] ~ [5 8 11] [7 10 12] ~!10>")
    .scale("D4:dorian")
    .sound("sawtooth").crush(6)
    .clip(0.5).gain(0.45).lpf(2500).pan(0.7),

  // phase 2 (bars 35-38): continuous, climbing
  n("0 4 7 11".fast(2).add("<12 14 16 17>"))
    .scale("D4:dorian")
    .sound("sawtooth").crush(6)
    .clip(0.6).gain(0.4).lpf(3000).pan(0.7)
    .mask("<0!34 1!4 0!6>"),

  // phase 3 (bars 39-41): impossible speed
  n("0 4 7 11".fast(8).add("<19 21 24>"))
    .scale("D4:dorian")
    .sound("sawtooth").crush(7)
    .clip(0.8).gain(0.33).lpf(4500).pan("0.6 0.8")
    .mask("<0!38 1!3 0!3>"),

  // bar 42: IMPACT. bar 43: silence.
  s("[lt,bd]").bank("RolandTR808")
    .gain(1.0).lpf(500).room(0.9)
    .mask("<0!41 1 0 0>"),

  // bar 44: the button. one footstep, one breath. "Next!"
  s("lt ~ ~ ~ ~ ~ ~ ~").bank("RolandTR808")
    .velocity(0.5).gain(0.6).lpf(600).room(0.4)
    .mask("<0!43 1>"),

  note("d2 ~ ~ ~").sound("gm_cello")
    .clip(2).gain(0.35).room(0.7)
    .mask("<0!43 1>")
)
