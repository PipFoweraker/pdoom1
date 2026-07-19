# Music session 1 -- from hummed leitmotif to a wired adaptive score

> Dev-history capture (2026-07-17/19, the Fable music session). How P(Doom)1
> went from "no composed music" to a five-tier adaptive score playing in-game,
> in one long human-AI listening loop. Working artifacts live in `tools/music/`;
> taste law in `tools/music/DIRECTION_NOTES.md`; raw judgment exports in
> `tools/music/jukebox_notes*.json`.

## The method: judgment rounds

The whole session ran on one loop: Claude composes Strudel patches (browser
live-coding, hearable in seconds) -> Pip listens on headphones and writes
unfiltered notes -> the notes are decoded into RULINGS (logged, append-only)
-> the rulings drive the next iteration. Pip is the taste authority; the
model is the instrument-builder and secretariat. Two full jukebox judgment
rounds happened in a single evening, and the second round's notes were
audibly more precise than the first -- the listening skill builds with the
score.

Design rulings that came out of ROUND 1: doom's weight lives in dark and
middle registers (its heralds may sing anywhere); harsh discordance is an
EVENT (miniboss flavour), not a bed; the tempo-ratchet (the live-band
*phwar*, everyone dances faster); victory might not be fanfare at all.
ROUND 2: layers must taper or ring out, never hard-cut; elements may
germinate over very long spans ("seeds of my own destruction"); respite
states need "A-team solidity" -- no stressors, but structural reassurance;
and M4 grew a metal trajectory ("the bassist catches the train... we all
gain GRUNGE together") that independently converged on the Mick Gordon
lineage the design docs had already flagged.

## The discoveries

- **The beloved reference decoded.** Pip's most-listened track ("People Of
  The Drifting Houses", Master Musicians of Bukkake) hides a 7-beat bar
  grouped 3+2+2 at ~129 bpm. Found by Demucs drum-stem isolation + folding
  53 s of onsets at candidate meters: contrast for 7 was double any other
  grouping. Pip had hummed the groove from memory first; the analysis
  matched his transcription. That cell now seeds the taiko/catastrophe
  rhythm vocabulary.
- **The score is a cast.** Six characters with hard timbre boundaries
  (CASTING_SHEET.md): humans are organic and micro-timed; the rivals are
  the ONLY purely synthetic voice and never harmonize with us; doom has no
  theme of its own -- it corrupts ours. Victory is the green cell allowed
  to play once, pure.
- **Pip is a performer.** Deep chanting background -> the math-chant
  conceit (Greek-letter litanies, Latin machine-liturgy, math-phoneme
  vocables) has a voice, with a hard respect line: real sutras and personal
  practice stay out of the game.

## The pipeline surprise: no OBS needed

The plan was OBS system-audio capture. The shipped result is better: a
Playwright script drives strudel.cc in a muted offscreen browser and records
the WebAudio graph itself (every connect() to the destination is duplicated
into a MediaRecorder tap). Captures are digitally clean, and the rig runs
happily while the machine is being used for a voice call -- nothing leaks in
either direction. One trap cost a full run: navigating to a strudel URL that
differs only in the #hash is a same-document navigation, so eleven takes
silently recorded the same patch. The tell was eleven identical volumedetect
readings; the fix verifies editor content per take.

Post-processing is exact rather than eyeballed: the WebAudio clock is
sample-accurate, so a 32-bar loop at 104 bpm is cut to precisely 73.846 s
from the onset-detected downbeat, the loop tail's reverb spill is baked into
the loop head with an equal-power crossfade (the file boundary IS the loop
point, per the drop-in kit), and everything lands at -16 LUFS ogg.

## Where it ended up

`music_manager.gd` now plays composed beds in all five adaptive tier slots
(C major at 104 souring through C dorian, then D dorian at 96 for the
endgame), the previously-silent VICTORY slot has "The off switch worked
(quiet dawn)", DEFEAT has the papers-please trudge Pip loved on first
listen, and the menu ducks into the "Checkpoint saved" respite cue. The
engine side (PR #682's AudioStreamInteractive tier crossfades) needed zero
code changes -- wiring the score was a data edit, as designed.

Still ahead: real stems from real players (COMMISSION_LIST.md -- taiko,
shakuhachi, upright bass, atarigane, Pip's voice), per-tier BASE/PULSE/
WEIRD/FIRE layer splits, the trailer long-form, and the metal question:
when the humans finally go loud, what instrument are they allowed to be?
