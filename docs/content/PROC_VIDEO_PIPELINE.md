# Procedure: one video, idea to published

> Status: DRAFT for Pip review, 2026-07-26 (rev 2, same day). Written so a
> non-technical hire can follow it. Each step says WHO (Pip / agent / anyone)
> and produces one artifact. Godot facts verified against the official docs
> AND the capture path was PROVEN end-to-end on Pip's machine 2026-07-26
> (see step 3). Pip rulings now baked in: VOICE YES (primary), FACE NO.

## Step 0 -- Voice register (once, before video #1)

Run VOICE_VARIANT_KIT.md: one 30-minute session, one fixed passage, four
registers, two takes each; pick a dominant register + one accent register
and write the pick into ROLE_CREATIVE_DIRECTOR.md. Every later video
inherits that one line.

## Step 1 -- Idea (WHO: Pip picks, anyone proposes)

- Pick a format from FORMATS_MENU.md and a topic.
- Topic sources, in preference order: devblog story seeds (docs/devblog/),
  a game mechanic that exists and demos well, a release-note highlight.
- Artifact: one line in the content backlog: format + topic + hook sentence.

## Step 2 -- Script (WHO: agent drafts, Pip gates)

- Agent drafts from the script template (below) + the topic's source material.
- Pip taste-gate: approve / redraft-with-notes. Do NOT wordsmith in the gate;
  notes only, agent redrafts.
- Script template (all formats):
  1. HOOK (first 5-10 s, one sentence, no logos, no "hi guys")
  2. PROMISE (what the viewer will understand by the end)
  3. 3-5 BEATS (each beat = one claim + one on-screen shot)
  4. BUTTON (last line: punchline or call-to-action, one only)
- Every line annotated with its SHOT (see step 3 shot-list).
- Artifact: `script.md` + `shotlist.md` in the video's working folder.

## Step 3 -- Capture (WHO: Pip plays; agent prepares)

Canonical capture = Godot Movie Maker mode (offline render: perfect frame
pacing and clean audio regardless of machine speed; the game stays playable
while recording, it just may not run at real-time speed -- expect input to
feel slower; play deliberately).

One-time setup (agent does, once, committed to repo):
- Project settings under Editor > Movie Writer: set FPS 60, Video Quality 0.9,
  and check Mix Rate is divisible by FPS (desync guard).
- Use the `movie` feature tag for capture-only overrides (e.g. resolution
  1920x1080 via Display > Window > Size overrides) so normal play is untouched.

Per-shot procedure (Pip) -- PROVEN command (ran clean 2026-07-26):
1. From a terminal:
   `"C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe" --path "G:/Documents/Organising_Life/Code/pdoom1/godot" --write-movie "G:/tmp/pdoom1-video-masters/<video>/<shot>.avi" --fixed-fps 60 --resolution 1920x1080`
2. Play the beat the shotlist describes. Slightly slower than natural.
3. Quit with the window X button (NEVER Ctrl+C -- it corrupts the AVI's
   duration metadata). For STATIC/scripted shots, append `--quit-after N`
   (N = seconds x 60) -- verified to finalize the file cleanly.
4. One retake max per shot at this stage; gaps are fixable in assembly.
5. Data-rate reality (measured): ~18 MB/s, ~1.1 GB/min, AVI 4GB cap =>
   max ~3.5 min per shot. Game audio records at current volume settings;
   set music LOW for ambience shots. Do NOT use --headless.

Notes:
- Output formats: `.avi` (MJPEG, fast, 4GB cap per file) for normal shots;
  `.png` sequence + wav for shots needing transparency (overlay effects).
  OGV also exists (editor builds only) but AVI is our default. [Both
  transcode to mp4 in assembly anyway.]
- The office sandbox (dev tool) is a legitimate capture stage for staged
  shots: spawn/populate/cat-walk/doom-glow scenes without playing a full run.
- Masters live OUTSIDE the repo: `G:/tmp/pdoom1-video-masters/<video>/`
  (same policy as art masters).

## Step 4 -- Voiceover (WHO: Pip)

Minimal tooling: Audacity (free). One-page procedure:
1. Same room, same mic position every time (consistency beats quality).
2. Read the whole script once as a warm-up. Do not record the warm-up.
3. Record TWO full takes, straight through, mistakes and all. Do not stop
   for errors -- just repeat the flubbed sentence and keep going.
4. Export each take as WAV (48000 Hz) into the video's masters folder.
5. Stop. Two takes is the rule. The assembler picks lines per-take.
- Fallback (no-voice day): skip; the format's text-card variant is used.

## Step 5 -- Assembly (WHO: agent writes script, anyone runs it)

DECISION: ffmpeg-scripted assembly, not a GUI editor.
- Why: fits the procedural philosophy (a video is re-renderable from a
  script; patching = edit script, re-run); zero new GUI skill for Pip; the
  assembly script IS the handover artifact; diffable in git.
- Cost (honest): fine timing feel is slower to iterate than dragging clips in
  a GUI; complex motion graphics are out of scope. Escape hatch: if a video
  needs human-feel cutting, Shotcut (free) is the named GUI -- but any video
  that needs it should probably be re-scoped first.
- Mechanics: per-video `assemble.sh` (committed) that: transcodes AVI masters
  to h264 mp4, trims clips to the shotlist's in/out points, concatenates,
  ducks music under voice, burns title cards from a text file, outputs
  `<video>_vN.mp4`. Music from godot/assets/audio/music/.
- Artifact: `assemble.sh` + rendered `_vN.mp4` in masters folder.
- Pip taste-gate on the render: approve / notes / re-render.

## Step 6 -- Thumbnail + title (WHO: agent drafts 2-3, Pip picks)

- Title follows the idea-space strategy: plain-language + the claimed term.
  Pattern: "<hook> | P(Doom) - the AI safety strategy game".
- Thumbnail: one game still (hero art or capture frame) + max 4 words of
  text. Agent produces 2-3 variants (existing gpt-image-1 pipeline or a
  capture frame + ImageMagick caption -- keep it scripted).
- Artifact: `thumb.png` 1280x720.

## Step 7 -- YouTube upload checklist (WHO: Pip now, hire later)

1. [ ] Upload `_vN.mp4`; title from step 6.
2. [ ] Description: 2 lines from the script's PROMISE + game download link +
       devblog link. First 2 lines matter (shown before the fold).
3. [ ] Tags: the claimed idea-space terms (keep a standing list in this doc).
4. [ ] Thumbnail from step 6. End screen: subscribe + one other video.
5. [ ] Visibility: Public. (Unlisted first ONLY if gate wasn't done on the
       final render.)
6. [ ] Log the URL in the content backlog line; done.

## Step 8 -- Instagram re-cut (DEFERRED)

- Not now. When activated: per-video `recut_vertical.sh` producing 9:16
  <60s cuts from the same masters. No new capture, no new voice.

## Working-folder convention

`G:/tmp/pdoom1-video-masters/<yyyy-mm>-<slug>/`
  script.md shotlist.md takes/ shots/ assemble.sh out/
Repo keeps: script.md, shotlist.md, assemble.sh (small, text, diffable).
Masters dir keeps: AVI/WAV/mp4 (big, binary).
