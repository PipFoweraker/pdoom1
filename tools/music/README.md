# tools/music -- reference-track analyzer

Turns the dev's beloved reference tracks into NUMBERS the music lab (Fable /
Strudel / SuperCollider) can compose against, so composed stems match the
pulse and structure of the north-star tracks (e.g. Master Musicians Of
Bukkake -- "People Of The Drifting Houses"). It is an offline analysis tool;
it does not touch the game or CI.

Companion docs:
- `docs/audio/REFERENCE_TRACKS.md` -- the aesthetic north stars + a prior
  hand-rolled DSP pass (ffmpeg + numpy). This tool is the repeatable,
  richer-featured successor.
- `docs/audio/MUSIC_DESIGN.md` / `docs/audio/STEM_CATALOGUE.md` -- what the
  numbers are FOR (the doom-band adaptive-music model + stem commission).
- `docs/audio/MUSIC_DROPIN_KIT.md` -- how a real stem replaces a placeholder.

## IMPORTANT: reference audio stays LOCAL, never committed

The reference tracks are personal and copyrighted. **Never commit the audio.**
Only the emitted JSON profiles are safe to keep -- extracted features (BPM,
chroma, section times) are facts and carry no rights baggage.

- Put your local copies in `tools/music/ref_local/` (singular "ref"; this is
  the dir Pip already uses -- gitignored).
- `.gitignore` already excludes `tools/music/ref_local/` (and the alternate
  `refs_local/` spelling) plus any `*.flac` / `*.mp3` / `*.wav` under
  `tools/music/` so personal audio cannot be staged by accident.
- If you analyze files from elsewhere on disk, that is fine too -- just do not
  copy them into the repo except under `ref_local/`.

## Install (local/dev only)

The analyzer needs **librosa** (which pulls in numpy / scipy / numba /
soundfile). It is intentionally **NOT** added to `requirements-dev.txt` --
librosa is heavy and this is a local-only tool, so keeping it out of the dev
requirements keeps CI installs light.

```
python -m pip install librosa
```

FLAC loads natively (soundfile); MP3 loads via `ffmpeg`, so **no format
conversion step is required** -- point the tool straight at your `.flac` /
`.mp3` files. (ffmpeg on PATH is the only non-pip prerequisite for MP3.) If
librosa is missing the script prints this same install line and exits
non-zero (no traceback).

Python 3.11 baseline (repo automation floor).

## Usage

```
python tools/music/analyze_refs.py path/to/track.mp3 [more.mp3 ...]
python tools/music/analyze_refs.py --help
```

One JSON profile per input is written to `tools/music/profiles/<trackname>.json`.
Useful flags: `--segments N` (target section count, default 8), `--env-buckets N`
(intensity-envelope resolution, default 32), `--sr HZ` (analysis rate, default
22050), `-o DIR` (output dir).

Batch the recommended set (assuming local copies live in `ref_local/`; FLAC and
MP3 both work directly):

```
python tools/music/analyze_refs.py tools/music/ref_local/*.flac tools/music/ref_local/*.mp3
```

## Recommended 5 reference tracks to analyze

Pulled from `docs/audio/REFERENCE_TRACKS.md` (the top-played, most
stylistically-relevant set):

1. **Master Musicians Of Bukkake -- People Of The Drifting Houses** (the most
   beloved; ritual pulse + large-scale build-and-release).
2. **Philip Glass -- Knee Play 5** (Einstein on the Beach; progressive
   minimalist patterns, and Knee Play 1 is literally sung numbers -- the
   formulae-as-lyrics ancestor).
3. **Braided Hair -- Speech feat. 1 Giant Leap** (the intro loops: additive
   loop-cell staircase = the vertical stem-stacking model).
4. **Dengue Fever -- Touch Me Not** (simple, distinct instrumental melody over
   a modal bed).
5. **The Staves -- Wisely and Slow** (close vocal harmony -- the reference for
   the title theme's harmonized formulae-as-lyrics).

(Nina Simone -- "Feeling Good" is a 6th brass-line reference; add it if you
want the progressive-brass data point.)

## What each profile contains

Per track, `<trackname>.json` holds:

- `tempo` -- estimated BPM + beat grid (`beat_times_sec`), plus `bpm_half` /
  `bpm_double` because BPM estimates alias to 2x/4x of the felt tempo (the
  `~84 BPM ritual heartbeat` vs `~104-112 pattern` lanes from REFERENCE_TRACKS.md).
- `key` -- Krumhansl-Schmuckler tonic + mode + top-4 candidates (a tonal
  CENTER, not a functional key; drone/modal material has no cadence to pin it).
- `tonal` -- normalized mean chroma (12 pitch classes) + the top pitch classes
  (spot the C/D modal-drone home: fifth + flat-7).
- `rhythm` -- onset count, onsets/sec density, and onset times.
- `intensity_envelope` -- time-bucketed arrays: `rms`, `rms_db_rel_peak` (the
  loudness ARC -- reveals ritual build-release), `onset_strength`,
  `onset_density`, `spectral_centroid_hz` (brightness proxy for the weirdness
  tilt budget).
- `sections` -- structural boundary times (agglomerative segmentation over
  chroma + MFCC).

## How the JSON feeds the composition loop

The profiles are compact, ASCII, and language-model-friendly. The intended
loop:

1. Analyze the 5 references -> `tools/music/profiles/*.json`.
2. Hand a profile (or several) to the composition agent (Fable) with the ask
   from `docs/audio/MUSIC_DESIGN.md` (per-tier BASE / PULSE / WEIRD / FIRE
   stems). The agent reads `tempo.bpm_half` for the heartbeat lane,
   `tonal.top_pitch_classes` for the drone center, `sections.boundary_times_sec`
   + `intensity_envelope.rms_db_rel_peak` for the build-release shape, and
   `rhythm.onset_density_per_sec` for how busy the PULSE stem should be.
3. The agent emits Strudel / SuperCollider patterns whose tempo/key/structure
   match the reference numbers.
4. Rendered stems drop into the game via `docs/audio/MUSIC_DROPIN_KIT.md`
   (the `MUSIC_TIER_STEMS` table in `godot/autoload/music_manager.gd`).

The profiles are just a starting seed -- the doom-tier LADDER supplies the
large-scale build; within-tier stems stay hypnotically flat (Glass-like), per
`docs/audio/REFERENCE_TRACKS.md`.
