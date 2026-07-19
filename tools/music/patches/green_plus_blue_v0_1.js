// P(Doom)1 music -- GREEN bed + BLUE "acting up" layer, v0.1
// Paste whole block at https://strudel.cc, Ctrl+Enter plays, Ctrl+. stops.
//
// ARCHITECTURE TEST: layers 1-4 are green_bed_v0_1 UNCHANGED. Layers 5-7 are
// the weirdness-axis additive layer (green -> blue). Comment out 5-7 and you
// must get exactly the green bed back -- that's the "doom is a layer, not a
// repaint" claim, tested by ear. A/B it live: select layers 5-7, toggle
// comments (Ctrl+/), Ctrl+Enter.
//
// Taste anchor from Pip 2026-07-17: green v0.1 reads like Ray Lynch,
// "Rhythm in the Pews" -- that lineage (Lynch / Deep Breakfast era new age
// minimalism) is a confirmed direction for the calm bands.
//
// Blue design: weirdness != danger. No minor, no percussion change. Instead:
//   5) lydian ghost -- F# shimmer (raised 4th) the green scale doesn't own,
//      5 notes/bar so it phases 5-against-8 against the spine
//   6) maj7 rub drone -- low B under the C harmony, slow vibrato, barely there
//   7) glitch echo -- quiet copy of the spine that occasionally runs BACKWARDS

setcpm(104/4)

stack(
  // ---------- GREEN (unchanged from green_bed_v0_1) ----------
  // 1) The cell: 8 eighth-notes, C major arpeggio up-and-back. The spine.
  n("0 2 4 7 9 7 4 2".add("<0 -2>/2"))
    .scale("C4:major")
    .sound("gm_epiano1")
    .gain(0.8).room(0.35).pan(0.42),

  // 2) Counter-cell: 6 notes per bar -> phases against the 8s
  n("2 4 7 9 7 4".add("<0 -2>/2"))
    .scale("C5:major")
    .sound("gm_marimba")
    .gain(0.4).room(0.5).pan(0.6),

  // 3) Bass: root on the half-notes
  n("0 ~ 0 ~".add("<0 -2>/2"))
    .scale("C2:major")
    .sound("gm_acoustic_bass")
    .gain(0.9).lpf(400),

  // 4) Heartbeat percussion
  s("bd ~ [~ bd] ~, [~ hh]*4")
    .bank("RolandTR808")
    .gain(0.35),

  // ---------- BLUE additive layer (comment these out to return to green) ----------
  // 5) Lydian ghost: 5-per-bar cell in C lydian -- the F# doesn't belong here
  n("0 3 4 3 7")
    .scale("C5:lydian")
    .sound("gm_music_box")
    .gain(0.3).room(0.6).pan(0.75),

  // 6) Maj7 rub: low B drone under the C harmony, slow queasy vibrato
  note("<b2 b2 a2 b2>")
    .sound("sawtooth")
    .lpf(320).vib(1.5).vibmod(0.25)
    .gain(0.18).room(0.4),

  // 7) Glitch echo: quiet spine copy that sometimes plays in reverse
  n("0 2 4 7 9 7 4 2".add("<0 -2>/2"))
    .scale("C4:major")
    .sometimesBy(0.2, x => x.rev())
    .sound("triangle")
    .gain(0.22).room(0.5).pan(0.25).lpf(1200)
)
