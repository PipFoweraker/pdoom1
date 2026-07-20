# Original placeholder audio (retired 2026-07-20)

The friend-made DJ-session tracks + UI blip that stood in for music before the
Fable composed tier-set (PR #710). Retired from the game when the composed
score was wired in; MOVED HERE rather than deleted (storage-is-cheap /
save-everything -- and these may be recycled or sampled later).

Kept OUT of `godot/` on purpose: Godot exports everything under the project
root into the shipped .pck, so live-but-unreferenced audio was build bloat.
Nothing here is referenced by any scene, script, or the MusicManager.

To recycle one: copy it back under `godot/assets/audio/music/`, let Godot
re-import (regenerates the .import sidecar), and register it in
`music_manager.gd`. See `docs/audio/MUSIC_DROPIN_KIT.md`.

Files (with their old in-game roles):
- PDoom1 Descent gradient.mp3   -- old M0 cosy tier
- PDoom1 Local maxima.mp3       -- old M1 uneasy tier
- PDoom1 Power spike.mp3        -- old M2 spooky tier (+ old M4 layer)
- PDoom1 Undetected sandbagging.mp3 -- old M3/M4 tier
- PDoom Out_of_distribution.mp3 -- old DEFEAT
- PDOOMN ST1 (safe).mp3         -- old MENU second track
- PDoom1 seleciton beeyoowee.wav -- 0.7s UI selection blip (miscatalogued in music)
