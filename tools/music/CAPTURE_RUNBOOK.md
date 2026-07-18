# Capture runbook -- render the session's patches to audio before PC reset

Goal: WAV/MP3 archives of every current patch iteration, so the early versions
survive as audio references even if the patches or Strudel drift.

## Setup (once, ~3 minutes)

1. Open OBS (installed at C:/Program Files/obs-studio).
2. In a Scene, add Source -> "Audio Output Capture" (Desktop Audio). Remove or
   mute any Mic source.
3. Settings -> Output -> Recording: path = anywhere convenient
   (e.g. Desktop/captures), format mkv or mp4 is fine -- we extract audio after.
4. Open https://strudel.cc in the browser. Set system volume to a fixed,
   non-clipping level and DO NOT touch it between takes (consistent gain).

## Per-take loop

1. Paste the patch into strudel.cc (from tools/music/patches/ or the jukebox's
   "Copy patch" button).
2. Start OBS recording. Wait 1 second of silence (trim handle).
3. Ctrl+Enter to play. Record for the take length below. Ctrl+. to stop.
4. Stop OBS recording. Rename the file to the take name below.

## Take list (name -> what to capture)

| Take name | Patch | Capture length |
|---|---|---|
| m0_green_v0_3 | green_bed_v0_3.js | 2 arcs ~ 1:15 |
| green_blue_v0_2_tour | green_plus_blue_v0_2.js | blue=1 for ~40s, then live-edit blue=0.5 ~30s, blue=0 ~30s |
| green_blue_amber_tour | green_blue_amber_v0_1.js | ~30s each at (0,0) (1,0) (0,1) (1,1) |
| zen_standoff_v0_1 | zen_standoff_sketch_v0_1.js | 16 cycles ~ 1:05 |
| drifting_seven_v0_1 | drifting_seven_v0_1.js | 16 bars ~ 0:55 |
| trudge_welcome_v0_1 | trudge_welcome_v0_1.js | 2 arcs ~ 2:05 |
| trailer_v0_4 | trailer_trudge_sketch_v0_4.js | ONE full pass ~ 2:50 + 3s tail |
| dirge_variations_v0_1 | dirge_variations_v0_1.js | 2 tours ~ 2:20 |
| jukebox_m1 | jukebox: Distribution shift | ~ 1:15 |
| jukebox_m2 | jukebox: Proxy gaming | ~ 1:15 |
| jukebox_m3 | jukebox: Mesa optimizer | ~ 1:25 |
| jukebox_m4 | jukebox: Treacherous turn | ~ 1:25 |
| jukebox_win | jukebox: The off switch worked | ~ 1:45 |

(m0 doubles as jukebox M0 -- same patch.)

## Extract audio afterwards (one command per file, ffmpeg is installed)

In the folder with the OBS recordings (PowerShell):

    foreach ($f in Get-ChildItem *.mkv,*.mp4) {
      ffmpeg -y -i $f.FullName -vn -acodec pcm_s16le `
        ("{0}.wav" -f $f.BaseName)
    }

Then copy the .wav files into tools/music/captures/ in the repo and commit
them (commit-generated-assets-by-default policy). Optional space-saver mp3s:

    foreach ($f in Get-ChildItem *.wav) {
      ffmpeg -y -i $f.FullName -b:a 192k ("{0}.mp3" -f $f.BaseName)
    }

## Naming convention

    capture_2026-07-18_<take name>.wav

These are ITERATION ARCHIVES, not shippable stems (GM placeholder sounds,
un-mastered). Shippable stems come later from real recordings per
COMMISSION_LIST.md.
