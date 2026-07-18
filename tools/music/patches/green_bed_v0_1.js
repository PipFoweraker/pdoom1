// P(Doom)1 music -- GREEN band ("ok") bed, v0.1
// Paste the whole block into https://strudel.cc then Ctrl+Enter to play.
// Ctrl+. (period) stops. Edit numbers and Ctrl+Enter again -- it hot-swaps live.
//
// Design intent: Glass-style looped cell (pure C major arpeggio), a slower
// counter-cell at 6-per-bar over the 8-per-bar spine (3-against-4 shimmer,
// the Braided Hair trick), harmony breathing C <-> Am every 2 bars, and a
// soft heartbeat pulse underneath. Nothing dissonant -- doom layers come later.

setcpm(104/4)  // 104 BPM, one cycle = one 4/4 bar

stack(
  // 1) The cell: 8 eighth-notes, C major arpeggio up-and-back. The spine.
  n("0 2 4 7 9 7 4 2".add("<0 -2>/2"))   // <0 -2>/2 = C bar-pair, then Am bar-pair
    .scale("C4:major")
    .sound("gm_epiano1")
    .gain(0.8).room(0.35).pan(0.42),

  // 2) Counter-cell: same material, 6 notes per bar -> phases against the 8s
  n("2 4 7 9 7 4".add("<0 -2>/2"))
    .scale("C5:major")
    .sound("gm_marimba")
    .gain(0.4).room(0.5).pan(0.6),

  // 3) Bass: root on the half-notes, the thing you nod to
  n("0 ~ 0 ~".add("<0 -2>/2"))
    .scale("C2:major")
    .sound("gm_acoustic_bass")
    .gain(0.9).lpf(400),

  // 4) Heartbeat percussion, well under the band
  s("bd ~ [~ bd] ~, [~ hh]*4")
    .bank("RolandTR808")
    .gain(0.35)
)
