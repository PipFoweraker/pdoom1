# Music direction notes -- running log

Taste rulings, palette, and design principles from Pip's listening sessions.
Append-only per session; newest at the bottom of each section. ASCII only.

## Taste rulings (dated, from Pip's ear)

2026-07-17 -- green bed v0.1:
- Confirmed direction. Reads like Ray Lynch, "Rhythm in the Pews"
  (Deep Breakfast-era new-age minimalism). That lineage is a keeper for calm bands.

2026-07-17 -- green+blue v0.1:
- Seven layers is "kind of OK" -- treat as near the density ceiling for blue.
- Layer 5 (lydian ghost, F# music box) = most impactful. Keeper.
- Layer 6 (maj7 rub drone at b2, lpf 320) = inaudible. Moved to mids in v0.2.
- Layer 7 (glitch echo) = wanted LOUDER, should "impinge a little more".
- Blue texture reference: the friend's SFX -- "mechanically-acoustically warped,
  BIOS glitching out, screen refresh rate clashes on old CRT monitors".
  Direction yes, intensity no -- keep it tamer than that.
- Lower layers (bass + kick + drone) combined too busy. Spread via register,
  reverb, tone. (v0.2: drone up an octave, bass clipped shorter, kick down.)
- UX: toggling a layer block via comments was clumsy. v0.2 introduces a single
  `blue` 0..1 constant scaling all blue gains -- one number, one Ctrl+Enter.
  Doubles as a live prototype of the engine's band crossfade.

## Instrument palette (for real stems later)

Real performers Pip can call on locally:
- Taiko drums (massive ones). Cool rhythms on big drums confirmed possible.
- Atarigane / chan-chiki style small metal drums (hit on the inside, the
  timekeepers for taiko soloists).
- Shakuhachi players.
- Pipe flutes ("fool pipe flutes") alongside taiko.
- A standing double bass player who owes Pip a favour.
- DJs.

Synthesize or source locally:
- Sitar, zither.
- Wailers / ululating vocals ("ululaters from ululating country").

Standing lyrical conceit (from kickoff): formulae / numbers as lyrics, harmonised.

## Design principles

- Anti-Tarkov-generator rule: environmental doom noise (hums, crackles, beeps,
  bops amplifying each other) is welcome as doom rises, but must NOT be a
  constant fatiguing presence (ref: Tarkov base generator hum -- painful during
  inventory sorting). Instead: doom MUTATES if the player lingers in one turn
  for a long time; otherwise the score should convey a sensation of PROGRESS.
- "Techno will get you to the mountain, but prog house will let you climb it"
  -- progression/journey feel over static loop intensity.
- Zen moments: solo shakuhachi or flute passages. The game will have
  kung-fu-masters-death-staring-across-valleys standoffs -- tension, pauses,
  bluffs, checks of character. Drums propel emotion there; silence is a tool.
- Doom is a layer, not a repaint (kickoff). Blue v0.1/v0.2 A/B validated the
  additive approach by ear so far.

## 2026-07-17 autonomous batch (Pip at a dance) -- state + sync notes

SYNC WARNING before `git pull` in this worktree: the offthread agent landed its
own `tools/music/analyze_refs.py` on origin/main (#692). The local analyzer
(different implementation, has the meter-hint feature) was RENAMED to
`tools/music/analyze_refs_meter.py` to clear the path. Local untracked files
that origin also does NOT have (kickoff doc, patches/, notes, stem board,
profiles JSONs) are safe. Pull should now be clean.

Engine mapping confirmed (docs/audio/MUSIC_DROPIN_KIT.md + MUSIC_DESIGN.md,
read from origin/main + feat/adaptive-music):
- Per-tier stem groups BASE / PULSE / WEIRD (+ FIRE at M3/M4), stacked via
  AudioStreamSynchronized. Our Strudel layer split maps 1:1 --
  layers 1-3 = BASE, layer 4 = PULSE seed, blue layers = WEIRD, and the
  patch `blue`/`amber` dials = per-stem volume_db in-engine.
- Authoring targets: ogg 44.1k, ~-16 LUFS/stem, file boundary IS the loop,
  same tempo+key within a tier, ML/AI-safety pun names.
- Five tiers cosy/uneasy/spooky/eldritch/terminal from doom % bands
  (<15 / <52 / <80 / <92 / 92+). VICTORY slot is EMPTY (needs a track).

In-game placeholder tracks profiled (tools/music/profiles/): tempos cluster
117.5-129.2 bpm (a natural ~120 lane matching ADAPTIVE_BPM), keys scatter
(C, A#, A#, A, C, F#) -- no key discipline in the placeholder set; composed
stems should fix per-tier key relationships. All are the friend's DJ-session
ambient (STEM_CATALOGUE.md); "the original doom multi-track artist" of the
design model is Mick Gordon -- derivations in GORDON_DERIVATIONS.md.

New tools this batch:
- tools/music/stem_board.html -- LOCAL browser rig: drop stems, tag them
  BASE/PULSE/WEIRD/FIRE + tier, doom slider drives 4s tier crossfades like the
  engine, group dials, mix save/export. For auditioning friend recordings.
- tools/music/zoom_rhythm.py -- window rhythm extractor (awaiting a Drifting
  Houses leitmotif timestamp from Pip).
- patches/green_blue_amber_v0_1.js -- BOTH axes on the green bed (blue+amber
  dials); amber = shaker 16ths + 3+3+2 proto-taiko + offbeat bass 8ths.
- patches/zen_standoff_sketch_v0_1.js -- shakuhachi/ma standoff moment cue.

## Design principles (additions 2026-07-18, from Pip's v0.3 listening)

- Predictability scaffold for A/B: state a pattern plainly (hear a 4-count
  twice), THEN mutate it (3rd pass slightly, 5th more) -- because the listener
  can predict the progression, subtle changes become audible. Use this both as
  a composition device and as the protocol for playtesting variants on Pip.
  Non-predictable subtle change still allowed, but predictable frames are the
  A/B instrument. (Music-cognition backing: expectation -> salience; see David
  Huron, "Sweet Anticipation".)
- Payoff + loop-signal: v0.3's bar-13 payoff then bar-15 breath worked; Pip
  explicitly likes RECOGNIZING the loop restart coming. Same device as the
  Drifting Houses beat-7 pickup: the end-of-bar skip IS the loop announcement.
  Build "the turn is coming" cues into every looping bed.

## Emotional thesis (2026-07-18, Pip verbatim-adjacent -- the music's north star)

"We're all highly likely to die to an unsolved alignment problem... nearly all
pathways of even everyone trying their best is still likely to be insufficient.
But! We, us glorious, expendable, individual humans, with our love and care and
worries, will STILL wake up and STILL try and do the right thing EVEN in the
face of defeat, doom, and paperwork." Trailer vision: trudge...IMPACT loop,
work spreads as we zoom out, rivals compound faster than we can, 'Next!' --
step forward anyway. Not hiding the immensity; inviting the attempt anyway.
Dignity, not triumph. First sketch: patches/trailer_trudge_sketch_v0_1.js.

## Dramaturgy ruling: organic = human, synthetic = rival (2026-07-18)

Pip's organic-vs-"conjured from pure abstraction" production instinct is also
the game's cast list. HUMAN material: recorded/physical register, micro-timing,
missed steps, room air. THE RIVAL/DOOM material: the only place purely
synthetic, gridded, dry, quantized sound is allowed -- coldness as character.
Audible-exponential device: rival motif recurs at halving intervals
(gaps 8->4->2->1 bars) while the human dirge never accelerates.

## Compositional grammar: ritual-procedural form (2026-07-18)

Pip's shaman model: real rituals don't bar-count -- "the shaman hits the drums
UNTIL the spirits are summoned, then moves to the bones; on a nod and a big 3
everyone switches to rhythm 2". Sections gated by completion-of-process, with
audible handoff cues, human-coordinated switches. Discordance at transitions
reads as process-change, not error (PotDH does this).
Two scales of application:
- LONG-FORM tracks (trailer, defeat, victory, menu): through-composed, patient,
  material calls back to itself over minutes. PotDH's unhurried length is the
  model.
- IN-GAME adaptive beds: must stay seamless loops (engine constraint), BUT the
  long-form IS the doom-tier ladder itself -- THE PLAYER IS THE SHAMAN. Tier
  transitions are the ritual-station changes, triggered by events not bars;
  the engine's crossfade is the nod-and-big-3. The game performs the
  composition; each bed is one ritual station with a long internal arc.

## Chant language ruling (2026-07-18)

Pip's background: Gyuto monks (Tibetan), Krishna Das, chanting before
meditation groups; his practice mantras are short Sanskrit (2-20 lines).
Rulings:
- Chanting in NON-ENGLISH feels right to him (intention over literal meaning).
- Real sutras/mantras and his personal practice stay OUT of the game --
  respect line, his call, do not blur performance and practice.
- Direction: chant the MATH ITSELF as the sacred register. Greek letter names
  (theta, eta, nabla, sigma) are already phonetically liturgical and carry no
  borrowed tradition. Candidate forms to test on mic day:
  1. Greek-letter recitation of real formulae (e.g. "theta... eta... nabla
     theta... iota-ta..." -- the update rule as pure letter-litany);
  2. Latin machine-liturgy (gradiens descendit, error minor fit -- the
     40k Adeptus Mechanicus register, learn-from-not-copy);
  3. Pure vocables built from math phonemes (del, sig, eps, mu) -- MMoB-style
     texture, zero semantics.
- Recording setup: RODE desktop USB mic, quietest room, dry takes, stacked
  imperfect takes = the choir. Short phrases (his 2-20 line comfort zone),
  repeat-repeat-repeat-tail-variant delivery per the PotDH/whisper finding.

## Pip as vocalist (2026-07-18 -- big unlock)

Pip offers his own voice: deep, dramatic-speaking compliments, grew up doing
extensive Buddhist chanting, happy to "chant and atonally wail". Uses:
- MATH CHANTS: the formulae-as-lyrics conceit now has a performer. Sutra-style
  recitation of real formulae over drone beds; process MMoB-style (reverse,
  smear) for WEIRD-stem material.
- VOICEOVER: narrate/explain the game (separate workstream, same mic setup).
Chant slot reserved in patches/trudge_welcome_v0_1.js (drone tuned to D).

## Production philosophy ruling (2026-07-18, from Pip's "IT-nerd cultist" rant)

Target: "IT nerds making really INTERESTING cultist circles around the server
stands" -- not purely techno noises. Organic-first synthesis rule, three axes:
1. SOURCE: real recorded instruments (taiko, shakuhachi, upright bass, voice)
   or synthesis that faithfully models physical behaviour -- not raw preset
   oscillators. Modular synth allowed AS a physical, hands-on instrument.
2. PERFORMANCE: human micro-timing and dynamics; grid-perfect = placeholder
   only. In Strudel prototypes approximate with velocity patterns + degradeBy
   (missed steps read as manual/human).
3. SPACE: real room/air over dry digital.
Pip's phrasing: grit "from doing things manually as opposed to being conjured
from pure abstraction like a generated MIDI chord". Converges with Gordon
derivation D1 (build the P(Doom) instrument from acoustic sources).
ALL gm_* sounds in patches are explicitly placeholders under this rule.

## Cue feedback log (2026-07-18)

- drifting_seven_v0_1: "kinda boppy" -- too short a phrase; drone valued as
  the space things fill into; softened percussion edges good (pulse not hits).
  Lesson: LONG PHRASES (PotDH's phrase-length is core to its pull). Extend
  cells into multi-bar AAAB phrases + 16-bar layer arcs.
- New cue commissioned: DEFEAT/welcome-back = "papers-please trudge through
  snow", NO oompah/tuba. First draft: patches/trudge_welcome_v0_1.js. Maps to
  the kit's DEFEAT slot + terminal->defeat bridge gap.
- trudge_welcome_v0_1: LOVED ("I love the dirge... the little wibbly bit at
  the end"). Complexity/progression level confirmed right (left it looping
  voluntarily). Trailer sketches v0.1/v0.2 both landed on two listens.
- Trailer rulings (Pip, 2026-07-18): OPEN = weird-smear tease (corrupted dirge
  bars 1-2, snap to reality -- doom ruins OUR theme, no villain theme);
  BUTTON = lone footstep + breath after the silence. Overwhelm = rival goes
  continuous then impossibly fast (rave-BPM wall) while humans hold steady --
  outclassed, never faltering. Current: patches/trailer_trudge_sketch_v0_3.js.
- Anathem (Stephenson) added as endgame/story register: monastic overtones for
  time-loop/denouement/intro; the avout's math-liturgy is native ground for
  the math-chant conceit. See CASTING_SHEET.md "Mathic Order" row.
- Score cast list formalized in CASTING_SHEET.md (6 characters, timbre
  boundaries as story boundaries, rival never harmonizes).
- v0.3 feedback -> v0.4 rulings: intro compressed to 1 bar = SECOND HALF of an
  explosion (we exit the time portal with catastrophe behind us, land in
  safe-2017, trudge begins AGAIN -- the time-loop/"pervents" element enters
  the lore). Bar of true silence after. Recognition flicker mid-piece (quiet
  smear return = "I know this sound"). Ending: high-pitched fast arps read
  as jagged/annoying -- REPLACED with the MULTI-FRONT RATCHET: five distinct
  fronts (hardware clicks / software blips / wetware voices / infraware sub /
  society swarm) entering on successive B-bars, ALL tightening each 4-bar
  round on a shared schedule; final swell = detuned beating saw roar (mass,
  not treble). Principle: "disquieting without discomfort"; unnaturalness via
  beating/detune/accumulation, not jagged edges. "All the things are coming
  to get me, from every direction."
- Variation techniques demoed in patches/dirge_variations_v0_1.js (9 x 2-bar
  tour: canon/inversion/retrograde/mode-swap/augment/hurry/ornament/STOLEN --
  V8 "rival plays our theme" flagged as late-game dramatic device).

## Reference artist identified (2026-07-18)

"People of the Drifting Houses" = Master Musicians of Bukkake, Totem One
(2009), Seattle ritual-psych collective (Randall Dunn, Don McGreevy, Milky).
Name riffs on the Master Musicians of Jajouka (Moroccan trance lineage).
Vocals are deliberately processed/reversed chant -- Pip's "thought it was
Aramaic" reaction is the intended effect; treat the vocal register as TEXTURE
not lyrics. Ceremonial/collectivist aesthetic, masked live shows, Sun City
Girls orbit. Full lore links in session chat 2026-07-18.

## Local exploration pipeline (2026-07-18)

`python tools/music/explore_track.py "<any audio file>"` -- profiles mix,
Demucs-splits stems (local, gitignored), folds the drum-stem accent bar at the
detected meter, emits a Strudel seed, writes numbers-only reports to
tools/music/library/<slug>/ + INDEX.md (committable). Optional --whisper for
vocal transcription (hallucination-prone on processed vocals). This is the
"drag songs in, build the Pip-explored-musical-analysis library" tool.

## Fable tier-set v0.1 + jukebox (2026-07-18)

Pip commissioned Claude's OWN interpretation of the full soundtrack from
everything known (session taste rulings + repo constellation: Beacon/GCR
governance, situational-awareness tracker, Tasmania localism -- the author IS
the person in the trudge line; "defeat, doom, and paperwork" is his calendar).
Delivered: tools/music/jukebox.html -- local player with 6 embedded tracks
(M0 "Unit tests passing", M1 "Distribution shift", M2 "Proxy gaming",
M3 "Mesa optimizer", M4 "Treacherous turn", WIN "The off switch worked"),
per-track notes/tags saved to localStorage + JSON export for feeding back.
Tier design: M0-M2 share C/104bpm (one room souring: major -> stumble ->
dorian), M3-M4 shift to D dorian/96 (the trudge universe arrives), victory =
green cell pure at 76 (casting sheet rule 4 kept). M4 centerpiece = STOLEN
theme. Layer comments carry BASE/PULSE/WEIRD/FIRE tags for stem-slicing.
Iterate: Pip plays with game running, tags states, exports jukebox_notes.json.

## Drifting Houses leitmotif (Pip's hummed transcription, 2026-07-17)

Structure he hears: a 4-phrase AAAB loop -- 3 repeats of pattern A, then one
variant phrase B with a tail. "Weird, Pirates-of-the-Caribbean-like time
signature", a "skipping rhythm" that is "super addictive":

    A: dun-dundun-dun-DUN-dundun--DUN-dun   (x3)
    B: dunnnn-dun-dunnit-dunner, ner, ner, ner... (beat)

To reconcile against analyze_refs.py output (tempo, meter hint, onset grid)
before building the amber/catastrophe rhythmic vocabulary from it.

## Jukebox judgment round 1 (2026-07-18, raw export committed as jukebox_notes.json)

Tags: M0 like; M1 like + fits-state; M4 like + fits-state; WIN too-thin.
Per-track rulings -> tier-set v0.2 actions:

- M0: marimba "just a biiit too bright when contrasted with the plodding"
  -> lpf + gain dim (register kept). "Not certain the payoff actually pays
  off" -> bar-12 lift figure, louder two-bar resolve, low-third floor under
  the downbeat. Wants more material for a much-heard track -> arc extended
  16 -> 32 bars, kalimba lead (competence cast) sings the second half.
- M1: liked; variations-on-first-theme progression confirmed. Marimba fix
  inherited; otherwise untouched. Lead-inheritance into M1 deferred until
  stem-slicing (when BASE stems are literally shared).
- M2: "a little busy" -> hats and offbeat synth 8ths CUT, spine spread over
  two bars (long-phrase lesson again). NEW RULING (doom density): doom wants
  "density and weight and inevitability as it approaches"; its heralds "might
  sing out in every register" but doom's own imposition lives in DARKER AND
  MIDDLE TONES with increasing prominence. v0.2: low-mid spine doubling +
  drone floor; lydian ghost quieter and rarer. Target feel: aware and
  slightly threatened, not "directly ominoused-upon".
- M3: downward-tripping cell "really welcome and refreshing" -- kept. NEW
  RULING (discordance-as-intrusion): truly discordant material = small
  intrusions and event-based responses (miniboss/boss flavour), not constant
  audio assault; constant bed stays enjoyable-from-inside. NEW IDEA
  (game-design crossover, flag for mechanics discussion): not ONE but MANY
  RIVAL SOUNDS -- characterful rival identities, Civ-empire-theme analogy,
  possibly representations the rivals EVOLVE into. v0.2 implements the
  canonical recurrence-gap halving (8-4-2-1 across the arc) with two
  distinct rival voices as a many-rivals proof-of-concept.
- M4: loved as-is ("a good, tight little loop", Pokemon battle-trill
  lineage). CANONIZED: "if you told me that this little ditty stayed with us
  as a compositional element into the far future, I'd believe you." NEW
  DEVICE (tempo ratchet): the live-band move -- the *phwar*, the drummer
  kicks the tempo, the crowd realises they must dance FASTER. Demo track
  added (m4r, four rounds each ~6% faster). Trill ending: lean into the
  mortal-kombat-ey character deliberately. Ratchet is likely an event/boss
  device, not the looping bed (anti-Tarkov rule).
- WIN: too-thin; wants "more triumphant and harmonious", AND doubts we want
  a victory-victory flavour at all. Split A/B for the next round:
  WIN-A "fanfare cut" (earned cadence, full-voice competence family --
  cast-legal triumph; real BRASS is an OPEN CASTING QUESTION, no row owns it
  yet) vs WIN-B "quiet dawn" (respite bed + the pure green-cell quote,
  casting rule 4 -- victory as being allowed to stop). Pip picks.
- NEW CUE COMMISSIONED (from the WIN note): menu respite -- "a balming
  respite for when you get out to the main or settings menus", the
  duck-out-of-the-hecticness sensation. Draft: jukebox "Checkpoint saved"
  (60 bpm, no percussion, no weirdness). Fills the drop-in kit's
  second-menu-bed nice-to-have.

## Jukebox judgment round 2 (2026-07-18, raw export committed as jukebox_notes2.json)

Tags: m0 like, m1 like, menu like. Rulings -> tier-set v0.3 actions:

- M0: progression CONFIRMED ("I like this version! I like we have a
  progression"). NEW RULE (graceful exit): the payoff-to-breath cut felt
  abrupt -- layers must taper or ring out, never hard-cut ("needs to be
  handled more gracefully"). v0.3: payoff rings into the breath, soft
  kick+hat ghost lands bar 15. NEW EXPLORATION: slow-build variant
  commissioned ("shifting the pacing down a little as an alternate...
  feel around what the start of a slow-build feels like") -> new track
  m0s "first light" at 92, entrances stretched across 32 bars. Pip is
  now consciously directing pacing -- give him pacing dials.
- M1: unsettling-creep working; the kick "oomphs" drive it. ASK: develop
  "graduation and stepping elements... missing a little out in the bass
  register" -> v0.3 adds a sinking-floor bass voice (steps down a degree
  every 2 bars through the second half) + an every-4th-bar kick fill.
- M2: insidiousness landing -- "like I'm sowing very very long germinating
  seeds of my own destruction. The lengths of these can get verrrry long."
  NEW RULING (long germination): elements may evolve over VERY long spans.
  He heard it "metamorphose... creepier and slower over time" -- v0.3
  composes that in for real: 32-bar filter bloom on the dark doubling +
  a 16-bar swelling cello seed.
- M3: "hovering in my midranges and fuzzy around the edges of my hearing";
  intrusion beeps "jarring and disjointing in a way that's interesting";
  an emergent "jazzy patch" after minutes. Working as designed -- kept
  unchanged. Meta note: he has never listened to music designed with
  these flows/ebbs -- the adaptive-listening skill is building.
- M4: immersion metric hit ("listened a full loop or two longer than I
  intended"). NEW DEVICE (bassist catches the train): after ~3 clean
  rounds something comes "gunning in -- a bassist left behind the train,
  running to catch up, then the bassline gets pulled into the carriage and
  we all gain GRUNGE together" -- pre-hook ramp-up flavour. NEW TRAJECTORY:
  "low industrial Protomen-style GRRRRR growls... sections of this might
  end up getting a bit metal. Wild." CONVERGENCE: this independently
  arrives at the Mick Gordon lineage (GORDON_DERIVATIONS.md) -- doom-tier
  metal grown from our own material. OPEN CASTING QUESTION: when the
  HUMANS go metal, what timbre rule applies? (a slammed/crushed bass on
  human material strains casting rule 1 -- decide before real stems.)
  v0.3: new sketch track m4t; canon loop still untouched.
- m4r: liked a lot; the "on-again off-again persistent little throbbing
  hum underneath" is "a very good tech-ey kind of thing to lean into"
  (that is the beating-saw pair + sub interplay). Both "gentler paths and
  more intense paths out of these paths forming emergently" -- fork later.
- WIN VERDICT: fanfare cut RETIRED ("a little... soporific?"). Quiet dawn
  IS victory. Fix: the green-cell quote enters "comparatively harsh" ->
  softened (kalimba, half speed, filtered). NEW RULING (respite = A-team
  solidity): in respite states, total absence of stressor-stimulation BUT
  a reassuring holding pattern -- "someone in an intense situation but
  knows they're being looked after by professionals... you have the A team
  with you, we've got this -- structural solidity." Applies to victory bed
  AND menu register. His long-listen: "the ambient elements I end up with
  are beautiful" -- bed confirmed.
- MENU: "Transitioning to something like this is exceptional. The pace
  remains, so I can re-engage with the mainstream event when I want, but
  the attention-demands are diminished." Exactly the design goal --
  confirmed, untouched.

## Drifting Houses leitmotif -- decode continued

DECODED 2026-07-18 (Demucs drum-stem isolation + 53 s onset fold): the groove
is a 7-BEAT bar at ~129 bpm, grouped 3+2+2. Meter-hint contrast for 7 on the
isolated drums = 0.131, over 2x any other grouping -- strong signal. Accent
skeleton on the 8th grid: beats 1 and 2 square, LOUDEST hits on the &-of-3
and &-of-4 (the offbeat "skip"), near-even gallop through 5-6-7, beat 7
leaning as pickup into the next downbeat. Square -> trip -> gallop -> pickup.
Hearable reconstruction: patches/drifting_seven_v0_1.js. Pip's AAAB phrase
structure (3 repeats + variant tail) still to be located/verified -- needs a
timestamp or a bar-level self-similarity pass. This cell is the seed for the
amber/taiko catastrophe vocabulary (real taiko can play a 3+2+2 seven).
