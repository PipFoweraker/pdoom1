// P(Doom)1 music -- TWO-AXIS prototype: green bed + BLUE (weird) + AMBER (catastrophe)
// Paste whole block at https://strudel.cc, Ctrl+Enter plays, Ctrl+. stops.
//
// This is the full doom-space in one patch. Two dials, matching the art spec axes:
//   blue  = weirdness   (timbre: detune/glitch/wrong notes)   -> WEIRD stem group
//   amber = catastrophe (rhythm: density/drive/urgency)       -> PULSE stem group
// green bed (layers 1-4) never changes. Try: (0,0) (1,0) (0,1) (1,1).
// (1,1) approximates tier M2 "spooky" territory.
//
// Amber vocabulary (kept separate from blue on purpose):
//   A1) shaker 16ths -- time starts insisting
//   A2) proto-taiko low drums in a 3+3+2 skipping cell -- the Drifting Houses
//       additive-rhythm lesson, and a placeholder for real taiko recordings
//   A3) bass urgency doubler -- offbeat 8ths under the original half-note bass

let blue  = 0   // weirdness 0..1
let amber = 1   // catastrophe 0..1

setcpm(104/4)

stack(
  // ---------- GREEN (stable core) ----------
  n("0 2 4 7 9 7 4 2".add("<0 -2>/2"))
    .scale("C4:major").sound("gm_epiano1")
    .gain(0.8).room(0.35).pan(0.3),

  n("2 4 7 9 7 4".add("<0 -2>/2"))
    .scale("C5:major").sound("gm_marimba")
    .gain(0.4).room(0.5).pan(0.7),

  n("0 ~ 0 ~".add("<0 -2>/2"))
    .scale("C2:major").sound("gm_acoustic_bass")
    .clip(0.6).gain(0.85).lpf(400),

  s("bd ~ [~ bd] ~, [~ hh]*4")
    .bank("RolandTR808").gain(0.3),

  // ---------- BLUE / weirdness ----------
  n("0 3 4 3 7").scale("C5:lydian")
    .sound("gm_music_box")
    .gain(0.3 * blue).room(0.6).pan(0.8),

  note("<b3 b3 a3 b3>").sound("sawtooth")
    .lpf(650).vib(1.5).vibmod(0.25)
    .gain(0.28 * blue).room(0.4),

  n("0 2 4 7 9 7 4 2".add("<0 -2>/2"))
    .scale("C4:major")
    .sometimesBy(0.25, x => x.rev())
    .sound("triangle").crush(8)
    .gain(0.38 * blue).room(0.45).pan(0.15).lpf(1800),

  // ---------- AMBER / catastrophe ----------
  // A1) shaker 16ths: urgency without loudness (accent on the beat)
  s("hh*16").bank("RolandTR808")
    .velocity("1 0.5 0.7 0.5".fast(4))     // accent pattern rides over...
    .gain(0.16 * amber),                   // ...one flat amber-scaled level

  // A2) proto-taiko: 3+3+2 skipping cell on low drums (real taiko later)
  s("[lt ~ ~ lt ~ ~ lt ~]")               // 8 slots, hits on 1,4,7 = 3+3+2
    .bank("RolandTR808")
    .gain(0.7 * amber).lpf(900).room(0.2),

  // A3) bass urgency doubler: offbeat 8ths under the green bass
  n("~ 0 ~ 0 ~ 0 ~ 0".add("<0 -2>/2"))
    .scale("C2:major").sound("gm_synth_bass_1")
    .clip(0.4).gain(0.5 * amber).lpf(500)
)
