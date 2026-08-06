# Jam Session 2026-08-05 -- P(Doom)1 as raw material

One to two hours at a friend's place. A singer with a mic, a techno DJ
(maybe decks), Pip with laptop + RODE + USB + printouts. Core plan works
OFFLINE. This is play, not a work session -- anything captured is a bonus.

## PART A -- PACK LIST (do this in 5 minutes, before 12:00)

USB stick (about 60 MB total -- any stick works):
- [ ] `tools/music/captures/game/` -- all 15 .ogg tracks (19 MB). This is
      the whole score incl. variants; plays in anything.
- [ ] The five per-tier WAVs for the DJ (decks and DAWs prefer WAV):
      `tools/music/captures/capture_2026-07-18_jukebox_m0.wav` through
      `_m4.wav` (plus `_win.wav` and `_menu.wav` if space is free).
- [ ] The game build zip (0.13.2) in case their machine is faster or
      internet is absent. It is on your laptop already; copy it over.

Laptop (verify, do not assume):
- [ ] Audacity or OBS opens and records from the RODE. Do a 5-second
      test recording NOW and play it back. This is the whole capture rig.
- [ ] The repo is on the laptop, so `art_generated/full_gallery.html`
      works there without the USB (it needs the 3.8 GB of images next to
      it via relative paths -- do NOT try to fit it on the stick).
- [ ] Game runs from the laptop (you know it does; launch it once anyway).

Print (one sheet each, three copies of sheet 1):
- [ ] SHEET 1 -- "The score cheat sheet": track names + one-line vibe
      (M0 checkpoint_saved = calm/cosy, M1 distribution_shift = uneasy,
      M2 proxy_gaming = spooky, M3 mesa_optimizer = eldritch,
      M4 treacherous_turn = terminal; defeat = out_of_distribution_trudge,
      victory = the_off_switch_worked) AND the musical keys:
      **M0-M2 are in C at 104 BPM; M3-M4 are D dorian at 96 BPM.**
      The singer needs the key; the DJ needs the BPM. This one line is
      the highest-value thing on any printout.
- [ ] SHEET 2 -- 15 event headlines pulled from
      `godot/data/events/core_events.json` (e.g. "Funding Crisis",
      "AI Breakthrough!", "Rival Lab Poaching", "Media Scandal",
      "Critical System Failure", "A Stray Cat Appears!") plus 3 blank
      lines for ones you invent on the spot.
- [ ] SHEET 3 -- half a page of premise for the guests: "You run an AI
      safety lab in 2017. You cannot win. You can only buy time. The
      music gets worse as doom rises." That is all the lore they need.

Phone: charged; voice-recorder app works (backup room mic + photos).

## PART B -- ACTIVITIES (each survives the others flopping)

### 1. Sing the doom ladder (best fun-per-setup -- start here)
What: play the five tier beds in order, M0 -> M4, a few minutes each.
The singer improvises a vocal line over each tier; the challenge is that
her voice has to decay with the world -- warm over M0, wordless and wrong
by M4. DJ runs playback (from decks or just a laptop), loops the good
bars, nudges tempo/FX live. Pip records everything on the RODE and stays
out of the way except to say what each tier means in the fiction.
Why it works: it is a creative constraint plus a mic, which is fun for
musicians regardless of the game. The beds are composition-real but
GM-placeholder timbre, so a human voice instantly makes them better --
low bar, real payoff.
Needs: USB tracks, mic, speaker. 20-40 min.
Walk away with: candidate vocal stems. The music plan
(`tools/music/COMMISSION_LIST.md`) already expects tiers to grow into
multi-stem groups (BASE/PULSE/WEIRD/FIRE) -- a vocal take slots into
that design with zero code changes.

### 2. The lab voicemail / newsreader pack
What: sheet 2 goes on the table. Each person picks a persona -- panicked
newsreader, dead-eyed corporate PR, the lab's answering machine -- and
reads headlines in character. One take each, fast, no retakes unless
someone wants one. The stray cat headline exists specifically so this
gets silly.
Why it works: near-zero skill floor, nobody has to sing, laughing is the
success condition. Good opener if the room needs warming up, good filler
between other activities.
Needs: printout, mic. 10-15 min.
Walk away with: scratch VO for event popups, and a feel for whether
voiced events are even good for the game.

### 3. DJ seeds: hand over the beds
What: give the DJ the five WAVs and one sentence of brief: "M4 is the
end of the world; make the techno version." If decks are there, they
play with it live and the others react; if not, the USB goes home with
them. Do NOT expect a finished remix in an hour -- frame it as a seed.
Needs: USB, their gear. 15 min live, or zero and it pays off later.
Walk away with: possibly a live jam recording; realistically, a
collaborator who now has the stems and a reason to touch them.

### 4. Narrated playthrough: one player, two voices
What: someone who is NOT Pip plays a run on the laptop. The singer
voices the world (staff, rivals, the news); the DJ scores it live,
riding the tier tracks or their own sounds as doom climbs. Pip's only
job: explain nothing unless asked, and record.
Why it works: this is the one honest way to make guests play the alpha
-- they are performing, not test-driving. The game's arc (calm -> doom)
gives the performance a shape for free.
Needs: laptop, mic, 25-40 min. Do this second half, after activity 1 or
2 has loosened the room.
Walk away with: an audio document of how strangers narrate your game --
which is playtest data smuggled inside a party game -- plus possibly a
trailer-grade moment.

### 5. The lab anthem (stretch goal)
What: write and record a 60-90 second corporate anthem for the doomed
lab -- earnest, upbeat, HR-approved, while the world ends. Everyone
writes lines; singer leads; DJ builds a backing loop (steal M0's
chords, C at 104).
Needs: 30-45 min of remaining energy. Only start if the room is hot.
Walk away with: a possible credits / trailer gag track.

## PART C -- CAPTURE (lightweight, decided in advance)

- ONE rule: the RODE + Audacity/OBS records CONTINUOUSLY per activity.
  Hit record when an activity starts, stop when it ends, never between
  takes. No slating, no interruptions.
- Phone voice recorder runs as a backup room mic, started once, left on.
- File names on the spot: `jam_2026-08-05_<activity>_full.wav`. Nothing
  fancier; you will not do better under social pressure.
- Phone photos of any written lyrics / scribbled lines before leaving.
- Back home: copy everything to `tools/music/captures/jam_2026-08-05/`
  (new folder, sibling of `raw/`), and note keeper-takes in a short
  INDEX.md there, same pattern as `tools/music/library/INDEX.md`.
- Ask both friends ON THE DAY: "ok if anything good ends up in the
  game, credited?" Ten seconds now beats an awkward message later.

## PART D -- HONEST WARNINGS

- `tools/transcribe_recording.py` is NOT offline. It calls the OpenAI
  API (whisper-1); it needs internet and a key. Transcribe at home
  afterwards. Do not plan anything on the day around transcription.
- The art gallery is laptop-only: keyboard-driven review, relative
  paths into 3.8 GB of images. It will not work from the USB and is
  not phone-usable. Use it only as ambient wallpaper on a screen, not
  as an activity -- reviewing 9,500 images is YOUR fun, not theirs.
- Do not open with the game. Playing someone's alpha out of politeness
  is work; activity 4 is the only game-shaped thing on the list and it
  works because the guests perform rather than evaluate.
- Anthem (5) puts the singer on the spot hardest -- writing to order in
  front of people. Offer it, never push it. The doom ladder (1) is
  safer: improvisation over a bed has no wrong answers.
- Expecting a finished DJ remix in the room will fall flat; an hour is
  not enough. Seed-and-take-home is the honest frame.
- The beds are GM-placeholder timbre. Say so up front ("placeholder
  sounds, real composition") so the DJ critiques the right layer.
- If there is no internet and the build zip is not on the USB, there is
  no game download. The USB copy is the insurance.

## PART E -- IF THERE IS TIME FOR ONLY ONE THING

Sing the doom ladder (activity 1), with the score cheat sheet printed.
It needs only the USB tracks, a speaker, and the mic; it gives both
guests a real role in the first five minutes; it is fun even if nothing
is kept; and if anything IS kept, it is exactly the asset class the
music plan is already waiting for.
