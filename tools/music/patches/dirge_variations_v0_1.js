// P(Doom)1 music -- DIRGE VARIATIONS sampler v0.1b (parse fix: no string
// concatenation -- Strudel patternifies every "quoted" literal, so patterns
// must each be ONE literal string)
// Paste whole block at https://strudel.cc, Ctrl+Enter plays, Ctrl+. stops.
//
// The SAME dirge (A phrase + wibbly-tail B phrase) through 9 transforms,
// 2 bars each, looping 18-bar tour over constant drone + footsteps.
// Note which numbers you like; keepers get folded into real cues.
//
//   bars  1-2   V0 THEME     the dirge as you know it
//   bars  3-4   V1 CANON     it chases its own echo (off by a half-beat)
//   bars  5-6   V2 INVERTED  mirror image -- every rise becomes a fall
//   bars  7-8   V3 BACKWARD  retrograde (the time-loop variation)
//   bars  9-10  V4 HOPEFUL   same shape in D major -- the picardy trudge
//   bars 11-12  V5 STRETCHED augmentation: half speed, twice the weight
//   bars 13-14  V6 HURRIED   double speed + displaced off the beat, anxious
//   bars 15-16  V7 ORNATE    grace notes -- the shakuhachi's telling of it
//   bars 17-18  V8 STOLEN    the RIVAL plays our theme, quantized, crushed

setcpm(63/4)

stack(
  // constant context: drone + footsteps
  note("[d2,a2]").sound("sawtooth")
    .lpf(240).gain(0.18).room(0.6).attack(1.5),

  s("lt ~ ~ lt ~ ~ lt ~").bank("RolandTR808")
    .velocity("1 0 0 0.6 0 0 0.75 0").degradeBy(0.08)
    .gain(0.6).lpf(650).room(0.3),

  // V0 THEME
  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D3:dorian").sound("gm_cello")
    .clip(1.6).gain(0.5).room(0.5)
    .mask("<1 1 0!16>"),

  // V1 CANON: leader + half-beat echo at lower volume
  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D3:dorian").sound("gm_cello")
    .off(0.0625, x => x.gain(0.5).pan(0.7))
    .clip(1.4).gain(0.45).room(0.5)
    .mask("<0!2 1 1 0!14>"),

  // V2 INVERTED: mirrored around the home note
  n("<[~ 0 ~ ~ -2 ~ -1 ~] [~ 0 ~ -3 [-2 -1] 0 ~ ~]>")
    .scale("D3:dorian").sound("gm_cello")
    .clip(1.6).gain(0.5).room(0.5)
    .mask("<0!4 1 1 0!12>"),

  // V3 BACKWARD: retrograde -- for the time-loop scenes
  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>").rev()
    .scale("D3:dorian").sound("gm_cello")
    .clip(1.6).gain(0.5).room(0.5)
    .mask("<0!6 1 1 0!10>"),

  // V4 HOPEFUL: same degrees, D major -- competence weather
  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D3:major").sound("gm_cello")
    .clip(1.6).gain(0.5).room(0.5)
    .mask("<0!8 1 1 0!8>"),

  // V5 STRETCHED: augmentation, one phrase across two bars
  n("[~ 0 ~ ~ 2 ~ 1 ~]").slow(2)
    .scale("D3:dorian").sound("gm_cello")
    .clip(2).gain(0.5).room(0.6)
    .mask("<0!10 1 1 0!6>"),

  // V6 HURRIED: diminution + displacement -- running late, off balance
  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>").fast(2).late(0.125)
    .scale("D3:dorian").sound("gm_cello")
    .clip(0.9).gain(0.45).room(0.4)
    .mask("<0!12 1 1 0!4>"),

  // V7 ORNATE: grace-noted telling, breathy voice
  n("<[~ 0 ~ [1 0] 2 ~ [2 1] ~] [~ 0 [1 0] 3 [2 1] 0 ~ ~]>")
    .scale("D4:dorian").sound("gm_shakuhachi")
    .clip(1.3).gain(0.45).room(0.7)
    .mask("<0!14 1 1 0!2>"),

  // V8 STOLEN: the rival has learned our song. gridded, dry, no room.
  n("<[~ 0 ~ ~ 2 ~ 1 ~] [~ 0 ~ 3 [2 1] 0 ~ ~]>")
    .scale("D4:dorian")
    .sound("square").crush(7)
    .clip(0.5).gain(0.4).pan(0.75)
    .mask("<0!16 1 1>")
)
