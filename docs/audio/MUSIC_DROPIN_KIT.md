# P(Doom)1 -- Adaptive-music drop-in kit (for the audio developer)

> **Who this is for:** a professional audio developer new to this repo who wants
> to replace the placeholder music with real composed stems. It documents the
> ACTUAL audio interface the game implements, cited to code (`file:line`), plus a
> step-by-step for swapping a placeholder for a real stem and an honest list of
> what still needs building.
>
> **Provenance / important:** the adaptive interface described here lives in
> **PR #682 / branch `feat/adaptive-music`** (`godot/autoload/music_manager.gd`).
> As of this writing that branch is **not yet merged to `main`** -- `main` still
> carries the older playlist-only `music_manager.gd`. All `file:line` citations
> below are against the `feat/adaptive-music` version. Check that branch out (or
> wait for it to land) before wiring real audio. Design rationale lives in
> `docs/audio/MUSIC_DESIGN.md`; the placeholder audit in
> `docs/audio/STEM_CATALOGUE.md`; the taste target in
> `docs/audio/REFERENCE_TRACKS.md`.

Engine: Godot 4.5.1, pure GDScript. The whole music system is one autoload node,
`MusicManager` (`godot/autoload/music_manager.gd`), registered in
`godot/project.godot` under `[autoload]` as
`MusicManager="*res://autoload/music_manager.gd"`. No FMOD/Wwise; two native
primitives only (`AudioStreamInteractive` + `AudioStreamSynchronized`).

---

## 1. Stem / slot inventory

The adaptive system exposes **5 tier slots** (one clip per doom-intensity band).
Each slot is a list of stems `{"path", "volume_db"}` in the constant
`MUSIC_TIER_STEMS` (`music_manager.gd:38`). Tier names come from
`MUSIC_TIER_NAMES = ["cosy","uneasy","spooky","eldritch","terminal"]`
(`music_manager.gd:26`).

| Tier | Slot name | Selected when doom band is... | Stems today (placeholder) | Volume |
|---|---|---|---|---|
| M0 | `cosy` | NOMINAL (<15% doom) | `PDoom1 Descent gradient.mp3` | 0 dB |
| M1 | `uneasy` | ELEVATED + HIGH (15-52%) | `PDoom1 Local maxima.mp3` | 0 dB |
| M2 | `spooky` | SEVERE + EXTREME (52-80%) | `PDoom1 Power spike.mp3` | 0 dB |
| M3 | `eldritch` | CATASTROPHIC (80-92%) | `PDoom1 Undetected sandbagging.mp3` | 0 dB |
| M4 | `terminal` | TERMINAL (92%+) | `PDoom1 Undetected sandbagging.mp3` **+** `PDoom1 Power spike.mp3` (layered) | 0 dB / -6 dB |

All stem paths are under `res://assets/audio/music/` (repo dir
`godot/assets/audio/music/`).

**Real vs placeholder:** **0 of 5 slots have real composed stems.** All are FULL
owned tracks standing in for per-tier stems (see the comment at
`music_manager.gd:34-37`). Only **4 distinct audio files** back the 5 slots --
M4 `terminal` reuses M3's and M2's tracks layered together, deliberately, to
keep the `AudioStreamSynchronized` (multi-stem) code path exercised
(`music_manager.gd:44-51`). None of the target layered stems (BASE / PULSE /
WEIRD / FIRE from `MUSIC_DESIGN.md` section 4) exist yet: every current "stem"
is a whole track, not a separable layer.

Non-adaptive contexts (unchanged, NOT doom-driven) live in `music_library`
(`music_manager.gd:62`): MENU playlist (2 tracks), VICTORY (**empty**), DEFEAT
(1 track, `PDoom Out_of_distribution.mp3`). Menu stays non-adaptive on purpose
(the menu has no doom).

---

## 2. Doom-band -> cue mapping

Two art-spec axes (`docs/art/PALETTE_AND_DOOM_INTENSITY.md`) map to two musical
dimensions (per `MUSIC_DESIGN.md` section 2): **Catastrophe (amber->red->fire)
-> RHYTHM/percussive density**, **Weirdness (green->blue->violet) ->
TIMBRE/detune-dissonance**. But the RUNTIME selector is single-valued: the game's
doom % (0-100) is quantized to a doom band, then to a tier.

The music system holds **no thresholds of its own** -- it calls
`ThemeManager.get_doom_band_index(doom)` for the canonical band (0..6), then
indexes `MUSIC_TIER_BY_BAND = [0,1,1,2,2,3,4]` (`music_manager.gd:30`) to get the
tier (0..4). Retuning the doom bands in `ThemeManager` moves the music
automatically.

Signal path (read-only view layer; ADR-0006):

```
GameManager.game_state_updated(state)              # per-turn broadcast (existing)
  -> MusicManager._on_game_state_for_music(state)  # reads state["doom"] only   (:137)
    -> set_doom_level(doom%)                        # (:367)
      -> music_tier_for_doom(doom%)                 # ThemeManager band -> tier  (:356)
        -> _switch_adaptive_tier(tier)              # (:406)
          -> AudioStreamPlaybackInteractive.switch_to_clip(tier)   # native crossfade
```

Transition rule (the crossfade): a **single any-to-any** transition added at
`music_manager.gd:481-485`:
`CLIP_ANY -> CLIP_ANY`, `TRANSITION_FROM_TIME_IMMEDIATE`,
`TRANSITION_TO_TIME_START`, `FADE_CROSS`, over `ADAPTIVE_FADE_BEATS` (8) beats.
With the stamped `ADAPTIVE_BPM = 120` (`music_manager.gd:52-53`), 8 beats = **a
4-second cross-fade**, target clip restarted from its start. Tier only switches
when the computed tier actually changes (`set_doom_level` early-returns
otherwise, `:369-370`). Band quantization gives natural hysteresis (dead zones);
no beat-alignment is attempted because the placeholder tracks share no tempo
grid (see `MUSIC_DESIGN.md` section 6 for the intended up/down/hysteresis rules
once real stems exist).

| Trigger | From | To | What happens |
|---|---|---|---|
| doom rises/falls into a new band | any tier | new tier | `switch_to_clip`, 4 s FADE_CROSS, target restarts at 0 |
| doom moves within same band | tier N | tier N | no-op (early return) |
| entering GAMEPLAY context | -- | tier for current doom | adaptive stream starts at `initial_clip = current tier` (`:398`) |
| MENU / VICTORY / DEFEAT | -- | -- | non-adaptive `music_library` playlist, NOT doom-driven |

Debug hook: `debug_force_tier(tier)` (`music_manager.gd:377`) forces a tier
directly for manual testing.

---

## 3. File format + conventions

**Directory (canonical):** `godot/assets/audio/music/` (`res://assets/audio/music/`).
SFX go in `godot/assets/audio/sfx/` (today just a `.gitkeep`).

**Formats Godot 4.5 accepts here:**
- **`.ogg` (Vorbis)** -- `AudioStreamOggVorbis`. **Preferred for looping music
  stems**: compressed, and the runtime loop/BPM stamping applies to it.
- **`.mp3`** -- `AudioStreamMP3`. What every current placeholder uses. Also
  gets runtime loop/BPM stamping. (ffmpeg-free; Godot decodes natively.)
- **`.wav`** -- `AudioStreamWAV`. Fine for short one-shots/SFX; for looping
  music it must carry **import-set loop points** (the runtime stamping does NOT
  apply to WAV -- see below).

**Loop + BPM handling (important, this is done at runtime):** `_prepare_stem`
(`music_manager.gd:492-497`) `duplicate()`s each loaded stream (so tweaks never
leak into the shared resource cache the playlist also uses) and, **for MP3/Ogg
only**, sets `stream.loop = true` and `stream.bpm = 120`. So today a whole
placeholder track is force-looped end-to-end (no authored loop point -> it wraps
at the file boundary, acceptable only because these beds have no hard tail). For
**WAV**, the code does NOT set loop -- it relies on the `.import` loop settings
(`edit/loop_mode` in the `.wav.import`), else the clip goes silent at its end and
the `finished` signal restarts it (`:266-272`, `music_manager.gd:498-503`).

**Import metadata:** the per-asset `.import` file is committed alongside each
audio file (Godot 4 convention -- see repo `CLAUDE.md`). Current MP3 imports have
`loop=false, bpm=0` (runtime overrides both). WAV import defaults show
`force/max_rate_hz=44100`, `edit/loop_mode=0`.

**Recommended authoring conventions for real stems:**
- Deliver **`.ogg` (or `.wav`)**, 44.1 kHz, stereo (mono acceptable for a mix
  layer). Match loudness roughly to about -16 LUFS integrated per stem; final
  balance is per-stem `volume_db` in-engine.
- **Seamless loop:** author the loop so head meets tail with no click and no
  reverb tail crossing the loop point (bake tails into the loop). The engine
  will still hard-loop MP3/Ogg, so the FILE boundary must BE the loop point.
- **Within a tier:** all stems share tempo, key (or a fixed relationship), and
  length (or integer multiple), so `AudioStreamSynchronized` stacks them cleanly.
- **Naming:** keep the ML/AI-safety pun register (e.g. "Mesa optimizer", "Reward
  hacking"); the game's voice depends on it (`STEM_CATALOGUE.md`). Existing
  filename typos ("PDOOMN", "seleciton") are shipped names -- preserve them.

---

## 4. How to replace a placeholder with a real stem

Aimed at a developer new to this repo. Assumes the `feat/adaptive-music` branch
(#682) is checked out.

1. **Drop the file in.** Copy your rendered stem (e.g. `bed_cosy.ogg`) into
   `godot/assets/audio/music/`. Use `.ogg` or `.wav`.
2. **Let Godot import it.** Open the project in the editor
   (`godot --path godot`, or `make run`), or run a headless import pass
   (`godot --headless --path godot --import`). Godot writes a
   `bed_cosy.ogg.import` (and maybe a `.uid`) next to the file. **Commit the
   audio file AND its `.import`/`.uid`** -- they are tracked on purpose. Do NOT
   `git add -A` (it stages ~1200 unrelated `.import` churn); `git add` only your
   file and its sidecars.
3. **(Optional) set a loop point for WAV.** If you shipped a `.wav` whose loop is
   not the whole file, select it in the editor's Import dock, set
   `Loop Mode = Forward` with begin/end sample points, and Reimport. MP3/Ogg are
   force-looped whole-file at runtime, so no editor step is needed there -- the
   file must itself be one seamless loop.
4. **Register it in `MUSIC_TIER_STEMS`** (`godot/autoload/music_manager.gd:38`).
   Replace the placeholder path for the relevant tier. Example -- swap the cosy
   bed and add a second synchronized layer:
   ```gdscript
   const MUSIC_TIER_STEMS := [
       [   # M0 cosy -- now a 2-stem synchronized group (BASE + PULSE)
           {"path": "res://assets/audio/music/bed_cosy.ogg",   "volume_db": 0.0},
           {"path": "res://assets/audio/music/pulse_cosy.ogg", "volume_db": -3.0},
       ],
       # ... M1..M4 unchanged
   ]
   ```
   Multiple stems in one tier are auto-wrapped in an `AudioStreamSynchronized`
   with per-stem `volume_db` (`music_manager.gd:461-475`); a single stem is used
   directly. No other code changes -- this is a **data edit**.
5. **Test in-engine.** Start a game session (GAMEPLAY context builds the adaptive
   stream, `music_manager.gd:384`). To move tiers without playing to high doom,
   call `MusicManager.debug_force_tier(0..4)` from a dev overlay / remote debugger.
   Watch the console: the manager logs `Adaptive stem missing, skipping`,
   `Adaptive stream built: N tiers`, and `Doom X% -> music tier N (name)`.
6. **Run the unit tests** (they cover the wiring, not the audio content):
   `python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300`.
   `godot/tests/unit/test_adaptive_music.gd` asserts tier mapping, clip-per-tier,
   and listen-only signal wiring. A malformed path just degrades (see section 5),
   so also confirm your file actually loads via the console log.

**Loop/transition behaviour to expect:** within a tier the stem(s) loop
indefinitely (whole-file for MP3/Ogg). When doom crosses a band boundary the
engine cross-fades to the new tier's clip over ~4 s and restarts that clip from
0. Missing/failed stems never crash -- they degrade.

---

## 5. Gaps / TODO -- what EXISTS vs what the audio dev must still build

**What is ready (plumbing, done):**
- The full doom-band -> tier -> clip pipeline, read-only and determinism-safe
  (ADR-0006). Adding real stems is a pure data edit in one constant.
- `AudioStreamInteractive` (horizontal tier crossfades) AND
  `AudioStreamSynchronized` (vertical multi-stem stacking) are both wired and
  exercised (terminal tier layers two stems today).
- Graceful degradation everywhere: a missing stem is skipped
  (`music_manager.gd:441-449`); an empty tier inherits a neighbour's stream
  (`:466-472`); a fully-empty build falls back to the legacy playlist
  (`:463-465`); no audio == silence, not an error.
- Per-stem `volume_db`, runtime loop/BPM stamping for MP3/Ogg, 4 s crossfade.

**What is still stubbed / missing (the commission):**
1. **No real stems exist -- all 5 slots are placeholders (4 distinct full
   tracks).** The core ask: per-tier **BASE / PULSE / WEIRD** stem groups (and a
   **FIRE** topper for M3/M4), sharing tempo+key within each tier, authored as
   seamless loops. Today no tier expresses the rhythm-vs-timbre axes -- they are
   just five whole ambient tracks. (`STEM_CATALOGUE.md` "Gaps to fill".)
2. **Loop points are not authored.** MP3/Ogg are force-looped whole-file at
   runtime; there are no seamless loop points and no shared tempo grid, so the
   stamped 120 BPM is nominal and beat-aligned transitions are false precision.
   Real stems must be authored so the file boundary IS a clean loop.
3. **VICTORY music is empty** (`music_library` VICTORY = `[]`,
   `music_manager.gd:73`) -- the win screen is silent. Needs a track.
4. **Transition polish not built:** only a single any-to-any 4 s crossfade
   exists. The intended up-tier(prompt)/down-tier(lazy) asymmetry, M3->M4 filler
   sting, and down-transition hysteresis (`MUSIC_DESIGN.md` section 6) are not
   implemented yet.
5. **Minor:** `PDoom1 seleciton beeyoowee.wav` (0.72 s UI blip) is miscatalogued
   in the MENU *music* rotation; SFX in `sounds/` (repo root) are not wired and
   their rights are unverified. A terminal->defeat bridge and a second menu bed
   are nice-to-haves. (`STEM_CATALOGUE.md`.)

Bottom line for the audio dev: **the engine is ready; the music is not.** Your
job is composing the per-tier layered stems (and victory/defeat cues); wiring
them is dropping files in `godot/assets/audio/music/` and editing the one
`MUSIC_TIER_STEMS` table.
