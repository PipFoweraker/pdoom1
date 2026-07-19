// P(Doom)1 music -- "drifting seven" rhythm study v0.1
// Paste whole block at https://strudel.cc, Ctrl+Enter plays, Ctrl+. stops.
//
// THE DECODED DRIFTING HOUSES SKIP (from the Demucs-isolated drum stem,
// folded over 53 s of the stable groove, 2026-07-18):
//   7-beat bar at ~129 bpm, grouped 3+2+2. Accent skeleton on the 8th grid:
//     beats 1 and 2 land SQUARE (strong on-beats),
//     then the &-of-3 and &-of-4 are the LOUDEST hits (offbeat trip -- the
//     "skip"), then beats 5-6-7 run almost evenly (the gallop tail), with
//     beat 7 leaning hard as a pickup into the next bar's downbeat.
//   Square -> trip -> gallop -> pickup. That's the addictive cell.
//
// This patch is that skeleton on proto-taiko voices in D (the track's key),
// one 7-beat bar per cycle. Judge by ear against the real thing: solo drum
// stem lives at tools/music/ref_local/stems/htdemucs/.../drums.wav.

setcpm(129.2/7)   // one cycle = one 7-beat bar at 129.2 bpm

stack(
  // 1) The cell on the 14-slot (8th-note) grid, velocities from the fold
  s("lt ~ lt hh mt lt ~ lt mt mt mt mt lt hh")
    .bank("RolandTR808")
    .velocity("1 0.3 0.95 0.5 0.75 1 0.3 1 0.8 0.78 0.78 0.83 0.85 0.5")
    .gain(0.8).lpf(1200).room(0.25),

  // 2) Deep pickup on beat 7 -- the lean into the next bar
  s("~ ~ ~ ~ ~ ~ bd")
    .bank("RolandTR808")
    .gain(0.7).lpf(300),

  // 3) Bass marks the 3+2+2 group starts (beats 1, 4, 6)
  note("d2 ~ ~ a1 ~ d2 ~")
    .sound("gm_acoustic_bass")
    .clip(0.7).gain(0.8).lpf(450),

  // 4) Open-fifth drone so the rhythm has a room to live in
  note("[d2,a2]")
    .sound("sawtooth")
    .lpf(280).gain(0.16).room(0.6).attack(1)
)
