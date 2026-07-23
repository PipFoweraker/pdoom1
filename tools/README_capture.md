# Cinematic capture harness

Deterministically record P(Doom)1 scenes (the portal, the cold-open, future
doom-scroll trailers) into shareable **mp4 + gif** using Godot's built-in **Movie
Maker** mode plus **ffmpeg**. Same seed + same scene -> identical footage, so a
trailer can be re-shot each patch and diffed frame-for-frame.

Runner: `tools/capture_cinematic.py` (standard library + subprocess only).

## Prerequisites (run on a real desktop, NOT CI)

- **A real GPU + display session.** Movie Maker renders through the actual GPU
  pipeline; it produces NO frames headless (same wall the shader work hit). Run
  this on Pip's Windows box in a normal desktop session, not over a headless
  SSH/CI shell.
- **Godot 4.5.1.** Default path is `C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe`
  (per CLAUDE.md). Override with `--godot <path>` or the `GODOT_BIN` env var.
- **ffmpeg on PATH.** Install:
  - Windows: `winget install Gyan.FFmpeg`
  - Linux: `apt install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Verify with `ffmpeg -version`. (Or run with `--no-mp4 --no-gif` to keep only
    the raw AVI and post-process later.)

## Usage

```
python tools/capture_cinematic.py portal            # record the named 'portal' capture
python tools/capture_cinematic.py --dry-run portal  # print the exact commands, run nothing
python tools/capture_cinematic.py --help
```

Overrides (win over the registry defaults):

```
python tools/capture_cinematic.py portal --fps 30 --resolution 1280x720 --duration 6
python tools/capture_cinematic.py portal --frames 300 --out portal_teaser
python tools/capture_cinematic.py res://scenes/dev/captures/portal_capture.tscn  # ad-hoc scene
python tools/capture_cinematic.py portal --skip-godot   # re-encode an existing .avi only
```

## Where output lands

Everything goes to the repo-root **`captures/`** dir -- **outside `godot/` on
purpose**, so captured video is NEVER packed into the shipped `.pck` (build-hygiene
rule: Godot exports all of `godot/`). `captures/.gitignore` self-ignores the dir
(`*` + `!.gitignore`), so the large binaries never get committed. A run of
`portal` writes:

- `captures/portal.avi` -- raw Movie Maker output (MJPEG video + PCM audio).
- `captures/portal.mp4` -- h264 / yuv420p / `+faststart` (web + social friendly).
- `captures/portal.gif` -- two-pass palettegen/paletteuse (clean colours, small-ish).

The intermediate `*.palette.png` is deleted automatically.

## The pipeline (what --dry-run prints)

1. **Record** -- Godot Movie Maker:
   `godot --path godot --write-movie <abs>/captures/<name>.avi --fixed-fps <fps>
   --windowed --resolution <WxH> --quit-after <frames> <res://scene.tscn>`
   - `--write-movie` enables Movie Maker + writes the AVI (with audio).
   - `--fixed-fps` sets the deterministic fixed timestep AND the movie framerate.
   - `--quit-after <frames>` bounds the run with NO input; `frames = round(fps *
     duration)`. The capture scene ALSO self-quits as a standalone backstop.
   - `--windowed` forces windowed mode so `--resolution` is honoured (the project
     sets `window/size/mode=2` = maximized, which would otherwise win).
2. **mp4** -- `ffmpeg -i <avi> -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow
   -movflags +faststart -c:a aac ... <mp4>` (even dimensions enforced).
3. **gif** -- two ffmpeg passes: `palettegen=stats_mode=diff` then
   `paletteuse=dither=bayer` at `gif_fps` / `gif_width` from the registry.

## Audio

Movie Maker records the game audio -- including the **adaptive score** -- straight
into the AVI's PCM track, and the mp4 pass re-encodes it to AAC. The gif is silent
(gifs have no audio). If a scene plays music, expect it in `<name>.mp4`.

## Adding a new named capture

Edit the `CAPTURES` dict in `tools/capture_cinematic.py`. Each entry:

```python
"doom_scroll": {
    "scene": "res://scenes/dev/captures/doom_scroll_capture.tscn",
    "fps": 30,
    "resolution": (1080, 1920),   # keep BOTH even for h264/yuv420p
    "duration": 15.0,             # frames = fps * duration
    "gif_fps": 20,                # optional (default 24)
    "gif_width": 480,             # optional (default 540); height auto
},
```

For an **unattended** capture the scene must AUTO-PLAY with no clicks (like
`godot/scenes/dev/captures/portal_capture.tscn`, which auto-tweens the portal
`open_progress` reveal on `_ready`). An interactive scene (needs a button/keypad)
will just sit there. Build a dedicated auto-playing capture variant of it.

## Capturing the COLD-OPEN specifically

The cold-open (`res://scenes/cold_open_sequence.tscn`) is **show-once gated**
(`GameConfig.should_show_intro()` -> `last_seen_intro_version` vs `INTRO_VERSION`,
plus the `play_intros` master switch) AND **interactive** (it waits on a 4-digit
phone passcode), so it will not run unattended as-is. Two paths:

1. **Point the runner straight at the scene** to bypass the show-once gate:
   `python tools/capture_cinematic.py res://scenes/cold_open_sequence.tscn
   --resolution 1920x1080 --duration 30`. It still stops at the phone passcode
   beat (needs input) -- fine for capturing the opening text beats + portal.
2. **Reset the gate** if you want the real config -> cold-open entry flow: in the
   game, or by editing the user config at
   `%APPDATA%/Godot/app_userdata/P(Doom)/` -- set `play_intros = true` and clear
   `last_seen_intro_version` (`""`). Then the cold-open plays on next new game.
3. For a clean unattended trailer, add a dedicated auto-playing cold-open capture
   scene (auto-enters the passcode, auto-advances the beats) and register it, the
   same way `portal_capture.tscn` wraps the interactive portal demo.

## Deterministic re-shooting

Because the render is driven by `--fixed-fps` (fixed timestep) off a fixed scene
+ seed, two runs of the same capture on the same build produce byte-comparable
frames. Re-shoot a trailer each patch and it stays consistent; a visual diff
surfaces exactly what changed.

## KNOWN QUIRK -- capture height comes out 2x on Pip's dev machine (2026-07-23)

Measured on Pip's Windows box: the captured HEIGHT is **2x** the `--resolution`
height, while width is exact (requested `1080x1080` -> recorded `1080x2160`;
`1280x720` -> `1280x1440`; `800x600` -> `800x1200`). It reproduces across
different scenes (the portal demo too), so it is a **Godot-window / Windows
display-scaling interaction, NOT the harness** -- the runner passes
`--windowed --resolution WxH` faithfully (confirm with `--dry-run`). Godot really
creates a double-height WINDOW (the UI reflows into it -- it is not a stretch).

Likely cause: Windows Display Scaling (Settings -> Display -> Scale, likely 150-200%)
interacting with Godot 4.5 windowing. To resolve at the source, check that scale
and re-test at 100%. Until then, two workarounds:

- **Request half the target height:** `--resolution 1080x540` records `1080x1080`
  on this machine. (Do NOT bake this into the `CAPTURES` registry -- the registry
  states the TRUE intended size and would be wrong on a normal-DPI machine/CI.)
- **Let ffmpeg conform it:** re-encode/crop the AVI to the exact frame you want
  (`ffmpeg -i <avi> -vf "crop=..."` or `scale=W:H`). Cropping preserves geometry;
  scaling to a different aspect squishes -- crop for a round portal.

## Notes / gotchas

- ffmpeg may print `No JPEG data found in image` warnings once per frame while
  decoding the AVI. Observed harmless: Godot's MJPEG movie-writer emits a
  per-frame marker the video decoder skips; frames still decode and the mp4/gif
  come out correct (verified: portal `open_progress` reveal renders as an
  animated brightness ramp). If a decode ever produces black/empty output,
  re-record.
- GIFs of long, busy footage get large (an 8s 540px portal gif is ~40 MB). For
  sharing prefer the mp4; use short loops or a smaller `gif_width` / `gif_fps` /
  `--duration` for a lean gif.
- These scenes are **dev-only** (`godot/scenes/dev/captures/`, `godot/scripts/dev/
  captures/`) -- no game state, no RNG, not referenced by any shipped flow.
