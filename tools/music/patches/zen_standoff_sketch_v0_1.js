// P(Doom)1 music -- ZEN STANDOFF sketch v0.1
// Paste whole block at https://strudel.cc, Ctrl+Enter plays, Ctrl+. stops.
//
// For the kung-fu-masters-death-staring-across-the-valley moments: tension,
// pauses, bluffs, checks of character. Not a doom tier -- a MOMENT cue that
// could interrupt any tier (engine-wise: a future context like VICTORY/DEFEAT,
// or a filler-clip sting family).
//
// Vocabulary: solo shakuhachi phrases with real silence between them, a barely
// moving drone, one taiko strike + atarigane tick keeping ma (negative space).
// Slow: at 60 BPM one cycle is a 4-second breath.
//
// The shakuhachi phrases land on D minor pentatonic (close to hirajoshi feel
// without leaving Strudel's stock scales). Real shakuhachi player later --
// this sketch just frames the SPACE the player will fill.

setcpm(60/4)

stack(
  // 1) Breath drone: barely moving, the valley itself
  note("<d2 d2 d2 c2>")
    .sound("sawtooth")
    .lpf(220).gain(0.25).room(0.7).attack(1.5).release(2),

  // 2) Solo flute phrases -- one per 2 cycles, mostly air. The soloist.
  n("<[0 ~ ~ ~] [~ ~ ~ ~] [2 3 ~ 2] [~ ~ ~ ~] [4 ~ 3 ~] [~ ~ ~ ~] [2 0 ~ ~] [~ ~ ~ ~]>")
    .scale("D4:minPent")
    .sound("gm_shakuhachi")
    .gain(0.75).room(0.8).attack(0.15).release(0.8)
    .sometimesBy(0.3, x => x.add(note(12)).gain(0.5)),   // occasional high answer

  // 3) One taiko strike, every 4th cycle -- a heartbeat you WAIT for
  s("<lt ~ ~ ~>")
    .bank("RolandTR808")
    .gain(0.9).lpf(600).room(0.5),

  // 4) Atarigane tick: the timekeeper, tiny and dry
  s("<~ rim ~ rim>")
    .bank("RolandTR808")
    .gain(0.3).hpf(2000)
)
