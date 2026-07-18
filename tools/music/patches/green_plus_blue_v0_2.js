// P(Doom)1 music -- GREEN bed + BLUE layer, v0.2
// Paste whole block at https://strudel.cc, Ctrl+Enter plays, Ctrl+. stops.
//
// Changes from v0.1, per Pip's ear (2026-07-17):
//   - ONE DIAL: the `blue` constant below fades the whole weirdness layer.
//     No more comment gymnastics -- type 0, 0.5, 1 and Ctrl+Enter.
//     This is also a live prototype of the engine's band crossfade.
//   - Glitch echo (winner-adjacent) rebalanced UP + gentle bitcrush for the
//     "BIOS glitching / CRT refresh clash" texture, kept well short of harsh.
//   - Maj7 rub was inaudible at b2 under lpf(320): moved up an octave into
//     the mids and opened the filter. Also fixes low-end congestion.
//   - Low end decongested: drone out of the bass register, bass notes
//     tightened with clip(), kick down a touch, wider stereo spread.
//   - Layer 5 lydian ghost confirmed strongest -- untouched.

let blue = 1   // 0 = pure green ... 1 = full "acting up". THE dial.

setcpm(104/4)

stack(
  // ---------- GREEN ----------
  // 1) Spine: 8th-note C major arpeggio cell
  n("0 2 4 7 9 7 4 2".add("<0 -2>/2"))
    .scale("C4:major")
    .sound("gm_epiano1")
    .gain(0.8).room(0.35).pan(0.3),

  // 2) Counter-cell, 6-per-bar shimmer
  n("2 4 7 9 7 4".add("<0 -2>/2"))
    .scale("C5:major")
    .sound("gm_marimba")
    .gain(0.4).room(0.5).pan(0.7),

  // 3) Bass, tightened (clip shortens each note -> less low-end wash)
  n("0 ~ 0 ~".add("<0 -2>/2"))
    .scale("C2:major")
    .sound("gm_acoustic_bass")
    .clip(0.6).gain(0.85).lpf(400),

  // 4) Heartbeat, slightly lighter than v0.1
  s("bd ~ [~ bd] ~, [~ hh]*4")
    .bank("RolandTR808")
    .gain(0.3),

  // ---------- BLUE (all gains scaled by the one dial) ----------
  // 5) Lydian ghost -- the keeper. F# shimmer, 5-against-8.
  n("0 3 4 3 7")
    .scale("C5:lydian")
    .sound("gm_music_box")
    .gain(0.3 * blue).room(0.6).pan(0.8),

  // 6) Maj7 rub, now in the mids where ears live
  note("<b3 b3 a3 b3>")
    .sound("sawtooth")
    .lpf(650).vib(1.5).vibmod(0.25)
    .gain(0.28 * blue).room(0.4),

  // 7) Glitch echo, louder + crushed: the loop misbehaving, CRT-flavoured
  n("0 2 4 7 9 7 4 2".add("<0 -2>/2"))
    .scale("C4:major")
    .sometimesBy(0.25, x => x.rev())
    .sound("triangle").crush(8)
    .gain(0.38 * blue).room(0.45).pan(0.15).lpf(1800)
)
