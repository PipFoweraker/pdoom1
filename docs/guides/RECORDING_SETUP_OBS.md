# Recording setup: the spare office, a RODE mic, and OBS

A beginner's guide written to be finished in **one to two hours**, in priority
order, so you can stop at any point and still have most of the benefit.

Scope: capturing good AUDIO for three different jobs from one room --
(1) talking-over-images sessions, (2) voiceover, (3) chanting, drums and
creative samples. Those three want different settings, and knowing that is
most of the skill.

Written 2026-07-30 after the first session produced a 218 MB file containing a
blank 4K video track and 12 MB of speech. That is the specific mistake this
guide prevents.

---

## The 20% that gets 80%, ranked

Do them in this order. Each one is worth more than everything below it.

1. **Get the mic close.** Roughly a hand-span from your mouth, slightly off to
   one side. This single thing beats every piece of software processing and
   every blanket in the room, because it changes the ratio of you to
   everything-else at the source.
2. **Kill the reflections behind and beside the mic, not the whole room.**
3. **Set the gain so peaks land around -12 dBFS.** Never let it touch 0.
4. **Record mono at 48 kHz.** Not stereo. One mic makes one channel.
5. **Stop OBS from recording a video track you do not want.**
6. Only then think about filters, and use fewer than you expect.

If you run out of time, stop after 4. You will already be at "clearly good".

---

## PART 1 -- The room (30-40 minutes)

You have a spare office, plenty of sheets, and low street noise. That is a
genuinely good starting hand.

### What you are actually fixing

You are **not** soundproofing. Soundproofing means stopping outside noise
getting in, it requires mass and construction, and you cannot do it with
bedding. Do not try.

You are **treating** -- stopping your own voice bouncing off hard surfaces and
arriving back at the mic a few milliseconds later. That late arrival is what
makes a recording sound like it was made in a room instead of in front of your
face. It is also the thing that is nearly impossible to remove afterwards, which
is why it is worth an hour now.

### The layout that works

- **Do not sit in the middle of the room, and do not face a bare wall
  head-on.** Both make strong, even reflections.
- **Face into the treated side.** Your voice goes forward, hits absorption,
  and does not come back.
- **Get the mic away from hard parallel surfaces.** Aim for at least a metre
  from any wall, and off-centre so the two side walls are at different
  distances -- unequal distances break up the reflection pattern.
- **Never put the mic directly in front of a hard desk surface** angled up at
  your face. The desk becomes a mirror. If the desk is hard, put a folded
  towel or sheet on it under the mic.

### Where the sheets go

Priority order. Two sheets in the right places beat six in the wrong ones.

1. **Behind the mic, facing you.** This catches the reflection of your own
   voice coming back off the wall you are facing. Highest value spot.
2. **Behind your head.** Catches what goes past you and returns.
3. **Either side, roughly level with your head**, forming a loose triangle.
4. **Under the mic** if the desk is hard.
5. Floor, if it is hard boards -- a rug is worth more than another sheet.

Thicker and looser beats thin and taut. **Hang them with folds and gathers, not
stretched flat** -- a rippled surface absorbs more than a smooth one, and the
air gap behind a hanging sheet does real work. Bedding, a duvet or a thick
blanket outperforms a single sheet substantially. A duvet on a clothes-drying
rack behind the mic is the classic cheap solution and it genuinely works.

### The test that tells you if it worked

Stand where you will record and **clap once, sharply.** Listen to the tail.

- A short dry *tok* with no ring: done, stop working.
- A noticeable *tock-ck* ring, or a sound like a small tiled room: add
  absorption behind the mic and behind your head, then clap again.

Do this before and after. It takes ten seconds and it is the only feedback loop
you need for the room.

### Then hunt the constant noises

Sit still for a full minute with your eyes closed and list what you hear. The
usual offenders, all free to fix:

- Computer fans -- put the recording laptop as far away as the cable allows,
  and behind you, not between you and the mic.
- Fridge, air conditioning, a heater -- turn them off for the take. Write a
  note so you remember to turn them back on.
- Phone on a hard surface -- vibrate mode against wood is loud. Put it on a
  sheet or in another room.
- Fluorescent tubes and some LED drivers hum. If one does, use a different
  lamp.

**Hardware for capture genuinely does not matter much.** Any laptop that can
run OBS is fine for audio, because audio is trivially cheap to encode compared
to video. Use whichever machine is quietest and most convenient.

---

## PART 2 -- The mic (15 minutes)

### First: which RODE do you have?

This determines everything, and there are only two answers:

- **USB** (NT-USB, NT-USB Mini, PodMic USB, Podcaster, VideoMic NTG via USB):
  it plugs into the laptop directly and appears as an input device. Nothing
  else needed.
- **XLR** (PodMic, NT1, NT1-A, Procaster, most of the studio range): it needs an
  audio interface or a mixer between mic and laptop. If you do not have one,
  that is the one purchase this setup actually requires.

If unsure, look at the cable end. USB is obvious; XLR is a round three-pin
connector.

### Placement and technique

- **A hand-span from your mouth**, about 15 cm. Closer is boomier, further
  brings the room back in.
- **Speak across the mic, not straight into it.** Angle it so your breath
  passes the side of the capsule rather than hitting it. This alone removes
  most plosive thumps on P and B sounds.
- **Know which side is the front.** Most cardioid mics take sound from the
  front and reject the back. RODE end-address mics (PodMic, Procaster) take it
  from the *end*; side-address mics (NT1) take it from the *side* with the
  badge. Pointing the wrong face at yourself is the single most common beginner
  mistake and sounds thin and distant.
- **Do not touch the desk while recording.** Every tap travels up the stand
  into the capsule. A boom arm or a shock mount fixes it; so does simply not
  drumming your fingers.
- **A pop filter helps.** So does a folded sheet of paper clipped a few
  centimetres in front, if you do not have one.

### Gain, which is the setting that matters

Set input level so **normal speech peaks around -12 dBFS**, with the loudest
moments no higher than -6.

Why not louder: digital audio has a hard ceiling at 0. Hitting it clips, which
is permanent, unfixable distortion. Quiet-but-clean can be raised later at no
cost. Loud-and-clipped is broken forever.

For **chanting or drums, aim lower** -- peaks around -18 dBFS. Percussive
transients are far louder than they feel, and a drum hit that sounds moderate
can be 15 dB above your speaking voice.

---

## PART 3 -- OBS (30-45 minutes)

OBS is a video tool. Audio-only recording is slightly off its main path, which
is exactly why last night's file was 218 MB of blank 4K video. Two routes below:
one certain, one cleaner.

### Step 1 -- Audio settings

**Settings -> Audio**

- Sample Rate: **48 kHz**
- Channels: **Mono**
- Mic/Auxiliary Audio: select your RODE explicitly. Do not leave it on
  "Default", which silently follows Windows and will one day pick the webcam.
- Set every device you are not using to "Disabled" so nothing unexpected gets
  mixed in.

Mono matters more than it looks: one mic recorded as stereo gives two identical
channels, doubling file size and adding nothing.

### Step 2 -- Kill the pointless video

**The certain route (do this one):**
**Settings -> Video** and set both Base and Output resolution to something
tiny -- **160x90** -- and FPS to **10**. You still get a video track, but it
becomes a rounding error instead of 96% of the file. This works in every OBS
version and cannot be got wrong.

**The cleaner route (try it, fall back if confusing):**
**Settings -> Output -> Output Mode: Advanced -> Recording tab**, set
**Type: Custom Output (FFmpeg)**, then choose an audio-only container --
`flac`, `mp3` or `m4a` -- and check the option to encode **audio only**. This
produces a genuine audio file with no video track at all. The exact wording
moves between OBS versions, so if you cannot find the audio-only checkbox
within five minutes, use the tiny-canvas route and move on. Nothing downstream
cares.

### Step 3 -- Recording output

**Settings -> Output -> Recording**

- Recording Path: a folder you will actually find again.
- Recording Format: **mkv** if you stay on the video route -- it survives a
  crash, where a half-written mp4 does not. Remux to mp4 afterwards from the
  File menu if anything needs it.
- Audio Bitrate: **160 kbps or higher** for archival talking. For music and
  chanting you want **FLAC** (lossless) via the Custom Output route.
- Audio Track: 1 is fine to start.

### Step 4 -- Filename formatting so files sort themselves

**Settings -> Advanced -> Recording -> Filename Formatting:**

```
%CCYY-%MM-%DD_%hh-%mm-%ss
```

That is what produced yesterday's tidy `2026-07-29_21-22-07` names. Keep it.

### Step 5 -- One hotkey, then stop fiddling

**Settings -> Hotkeys -> Start Recording / Stop Recording.** Bind both to
something you will not hit accidentally. Being able to start without looking at
the screen is worth more than any filter.

### Step 6 -- Watch the meter, not the waveform

The audio mixer panel shows a level meter. Green is fine, yellow is fine, **red
means you are clipping and must turn the gain down.** Adjust at the mic or
interface first; only use OBS's fader if the hardware is already at minimum.

---

## PART 4 -- Filters, and why you want fewer than you think

Add filters by right-clicking the mic in the Audio Mixer -> Filters.

**Order matters.** OBS applies them top to bottom, and this order is the
conventional one:

1. Noise Suppression
2. Noise Gate
3. Compressor
4. Limiter

### For talking (voiceover, review sessions)

- **Noise Suppression: RNNoise.** One click, no settings, removes steady
  background hiss and fan noise convincingly. The Speex option is lighter on
  CPU and worse.
- **Limiter** at about **-3 dB**, as a seatbelt against one loud laugh
  clipping the take.
- That is genuinely enough. Add a **Compressor** only if your volume swings
  wildly between leaning in and sitting back, and if you do, start gentle:
  ratio 2:1 or 3:1, threshold around -18 dB.
- **Noise Gate: think twice.** A gate mutes below a threshold, which sounds
  clean in isolation and chops the ends off quiet words in practice. With a
  treated room and a close mic you do not need it.

### For chanting, drums and samples -- USE NO FILTERS

This is the important part, and it is the opposite of the above.

- **No noise suppression.** RNNoise is trained on speech and will treat sung
  tone, sustained vowels and cymbal-like content as noise to be removed. It
  will audibly mangle chanting.
- **No gate.** It cuts the decay tail off every drum hit and the end of every
  held note. Tails are the character of a percussion sample.
- **No compressor.** Dynamics are the performance.
- **Limiter only**, purely as protection, set high at about -1 dB.
- Record **FLAC** if you can, and leave **more headroom** (peaks -18 dBFS).

Capture clean and flat, decide later. Processing you have applied at capture
cannot be undone; processing you skipped can always be added.

### Do this with two Profiles, not by remembering

OBS **Profile** stores settings; **Scene Collection** stores sources and their
filters.

- Profile **"Spoken"** -- mono, 160 kbps, RNNoise + Limiter.
- Profile **"Raw Capture"** -- mono or stereo, FLAC, Limiter only, lower gain.

`Profile -> Duplicate` after you have one working, then change the few things
that differ. Switching profiles takes two seconds and removes the entire class
of mistake where you record a drum take through a noise gate.

---

## PART 5 -- The ten-minute test loop

Before any real session:

1. Record 30 seconds: speak normally, then loudly, then say a sentence full of
   P and B words ("pack a big purple box"), then sit silently for five seconds.
2. Stop. **Listen on headphones.** Not laptop speakers -- they hide
   everything that matters.
3. Check four things:
   - Does the silence sound *quiet*, or is there hiss and hum?
   - Do the P and B words thump? Angle the mic further off-axis.
   - Did the loud part clip? Lower the gain.
   - Does it sound like a room? More absorption behind the mic.
4. Fix one thing. Repeat.

Three passes of this will get you further than any amount of reading, including
this document.

---

## PART 6 -- Straight into a transcript

The repo already has the tool:

```
python tools/transcribe_recording.py path/to/recording.mkv
```

It strips the video, downmixes to 16 kHz mono, splits into ten-minute chunks,
transcribes each, and writes both a plain `.transcript.txt` and a timestamped
`.transcript.md`. Roughly US$0.006 per minute -- about 20 cents for half an hour.
It accepts video or audio, so it does not care which OBS route you chose.

**It does not separate speakers.** There is no diarization in the API, so a
two-person conversation comes back as one voice. Two habits fix most of the
resulting ambiguity:

- **Say the file or concept name aloud** before discussing it. You did this
  last night for 12 of 15 concepts and it is the only reason the feedback could
  be extracted at all.
- **Say "V1" or "V2" out loud**, and get anyone else in the room to do the
  same. Every unresolvable verdict in last night's session came from someone
  pointing at the screen.

### Privacy, learned the hard way

Last night's recording contains a mobile phone number, spoken aloud in passing.
`art_generated/` is gitignored, which is the only reason that is harmless.

**Never move a raw recording or transcript into a tracked path without reading
it first.** If a session needs to be shared, scrub it.

---

## Appendix -- if you only have twenty minutes

1. Hang a duvet on a rack behind the mic, facing you.
2. Mic a hand-span away, angled across your mouth, badge or end pointing at you.
3. OBS: Audio -> 48 kHz, Mono, RODE selected explicitly.
4. OBS: Video -> 160x90 at 10 fps.
5. Mic filters: RNNoise, then Limiter at -3 dB. Nothing else.
6. Clap once. If it rings, add another blanket.
7. Record 30 seconds and listen on headphones.

That is a genuinely good spoken-word setup. Everything above it is refinement.
