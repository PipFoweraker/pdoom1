// P(Doom)1 music -- TRAILER TRUDGE sketch v0.4: portal open + multi-front end
// Paste whole block at https://strudel.cc, Ctrl+Enter plays, Ctrl+. stops.
// 44 bars, ~2:47 at 63 bpm. THROUGH-COMPOSED -- listen start to finish.
//
// v0.4 (Pip's notes 2026-07-18):
//   OPEN compressed to ONE bar: we arrive out of the time portal catching the
//   SECOND HALF of the explosion behind us -- boom tail, roar dying, the
//   corrupted dirge screaming through it. Bar 2 is pure silence ("...oh!").
//   Bar 3: safe-2017. The trudge begins. (...again. Pervents walk on.)
//   RECOGNITION: one quiet smear flicker at bar 34 -- "I know this sound.
//   This is the doom coming for us."
//   ENDING rebuilt: the screech arps are GONE. Instead, five RATCHET FRONTS
//   enter one at a time on successive B-bars (the "wibbly tail" bars),
//   and every front already running keeps TIGHTENING each 4-bar round via a
//   shared schedule -- all of them, from every direction, each getting faster
//   than us:
//     bar 20  R1 HARDWARE  -- dry clicks, left, accelerating
//     bar 24  R2 SOFTWARE  -- the rival's blips, right, mid register
//     bar 28  R3 WETWARE   -- corrupted voices, bending upward
//     bar 32  R4 INFRAWARE -- sub pulse quickening underfoot
//     bar 36  R5 SOCIETY   -- swarm chatter, everywhere
//   bars 39-41: no treble scream -- a DETUNED LOW ROAR (two saws beating
//   against each other) swells instead: disquiet from beating and mass, not
//   jagged edges. IMPACT 42, silence 43, one footstep 44.

setcpm(63/4)

const TIGHT = "<1 1 1 1 1 1.25 1.5 1.75 2 2.5 3>/4"   // the shared ratchet
const CREEP = "<0 0 0 0 0 0 1 2 3 4 5>/4"             // pitch creep, in steps

stack(
  // ---- BAR 1: out of the portal, explosion tail behind us ----
  s("[bd,lt] ~ ~ ~").bank("RolandTR808")
    .gain(1.0).lpf(120).room(0.95)
    .mask("<1 0!43>"),

  s("white!4")
    .velocity("1 0.55 0.3 0.15")
    .lpf("4000 1400 600 250")
    .release(0.4).gain(0.5)
    .mask("<1 0!43>"),

  n("[~ 0 ~ 3 [2 1] 0 ~ ~]")
    .scale("D3:dorian").rev()
    .sound("sawtooth").shape(0.6).crush(4)
    .vib(6).vibmod(0.6)
    .clip(1.5).lpf(1600).gain(0.5).room(0.9)
    .mask("<1 0!43>"),
  // (bar 2 is silence on purpose. if .shape errors in your Strudel, delete it)

  // ---- BARS 3-41: the trudge (unchanged core) ----
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

  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D3:dorian").sound("gm_cello")
    .clip(1.6).gain(0.5).room(0.5).pan(0.4)
    .mask("<0!10 1!31 0!3>"),

  s("[~ hh]*4").bank("RolandTR808")
    .gain(0.15).mask("<0!18 1!23 0!3>"),

  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D4:dorian").sound("gm_shakuhachi")
    .clip(1.4).gain(0.28).room(0.8).pan(0.65)
    .mask("<0!18 1!23 0!3>"),

  s("lt*8").bank("RolandTR808")
    .velocity("0.5 0.3 0.4 0.3 0.5 0.3 0.4 0.35")
    .gain(0.4).lpf(800).mask("<0!26 1!15 0!3>"),

  note("[d5,a5]").sound("triangle")
    .attack(2).gain(0.1).room(0.9).mask("<0!26 1!15 0!3>"),

  // rival's discrete calls (kept -- these were fine): 19, 27, 31, 33, 34
  n("<~!18 [0 4 7] ~!7 [2 5 8] ~!3 [4 7 10] ~ [5 8 11] [7 10 12] ~!10>")
    .scale("D4:dorian")
    .sound("sawtooth").crush(6)
    .clip(0.5).gain(0.45).lpf(2200).pan(0.7),

  // ---- RECOGNITION FLICKER, bar 34: the smear, quiet, under the mix ----
  n("[~ 0 ~ 3 [2 1] 0 ~ ~]")
    .scale("D3:dorian").rev()
    .sound("sawtooth").crush(5)
    .vib(4).vibmod(0.4)
    .clip(1.2).lpf(900).gain(0.16).room(0.8)
    .mask("<0!33 1 0!10>"),

  // ---- THE FIVE FRONTS (each enters on a B-bar; all keep tightening) ----
  // R1 HARDWARE: dry clicks, hard left, accelerating
  s("rim*4").bank("RolandTR808")
    .fast(TIGHT)
    .gain(0.22).hpf(1200).pan(0.12)
    .mask("<0!19 1!22 0!3>"),

  // R2 SOFTWARE: the rival's blips, mid register, hard right
  n("0 4 7").scale("D5:dorian")
    .fast(TIGHT).add(CREEP)
    .sound("square").crush(8)
    .clip(0.3).gain(0.2).lpf(2400).pan(0.88)
    .mask("<0!23 1!18 0!3>"),

  // R3 WETWARE: corrupted voices bending upward
  n("<0 1 0 2>").scale("D4:dorian")
    .add(CREEP)
    .sound("gm_voice_oohs")
    .vib(3).vibmod(0.4)
    .gain(0.3).room(0.6).pan(0.35)
    .mask("<0!27 1!14 0!3>"),

  // R4 INFRAWARE: sub pulse quickening underfoot
  note("d1*2").sound("sine")
    .fast(TIGHT)
    .clip(0.5).gain(0.42).lpf(140)
    .mask("<0!31 1!10 0!3>"),

  // R5 SOCIETY: swarm chatter, everywhere at once
  n("0 2 4 7 9".fast(2)).scale("D5:dorian")
    .fast(TIGHT)
    .sound("gm_marimba")
    .clip(0.4).gain(0.16).room(0.4).pan("0.2 0.8")
    .mask("<0!35 1!6 0!3>"),

  // ---- bars 39-41: the roar (beating detuned saws, mass not treble) ----
  note("d1").sound("sawtooth")
    .lpf("<600 1000 1600>")
    .gain("<0.2 0.3 0.42>").attack(0.5)
    .mask("<0!38 1!3 0!3>"),

  note("d1").add(note(0.13)).sound("sawtooth")
    .lpf("<600 1000 1600>")
    .gain("<0.2 0.3 0.42>").attack(0.5)
    .mask("<0!38 1!3 0!3>"),

  // ---- IMPACT 42, silence 43, the button 44 ----
  s("[lt,bd]").bank("RolandTR808")
    .gain(1.0).lpf(500).room(0.9)
    .mask("<0!41 1 0 0>"),

  s("lt ~ ~ ~ ~ ~ ~ ~").bank("RolandTR808")
    .velocity(0.5).gain(0.6).lpf(600).room(0.4)
    .mask("<0!43 1>"),

  note("d2 ~ ~ ~").sound("gm_cello")
    .clip(2).gain(0.35).room(0.7)
    .mask("<0!43 1>")
)
