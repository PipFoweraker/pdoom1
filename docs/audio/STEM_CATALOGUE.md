# P(Doom)1 -- Stem + track catalogue

> Everything audio the project holds today, what it is good for, and the gaps the
> musicians need to fill. Track names are ML/AI-safety puns and are KEPT -- they are
> part of the game's voice. Durations measured from the imported streams (Godot) and
> wav headers (Python) on 2026-07-17.

## Music tracks (`godot/assets/audio/music/`)

All six full tracks are DJ-session ambient recorded by Pip; **Pip owns full rights**.
Source dump duplicates live in `sounds/musicdump/20_nov_2025/` (root of repo, not in
the Godot project) -- treat `godot/assets/audio/music/` as canonical.

| Track (pun intact) | The pun | Length | Vibe | Current use | Adaptive slot (placeholder) | Usability / coherence note |
|---|---|---|---|---|---|---|
| `PDoom1 Descent gradient.mp3` | gradient descent, inverted | 1:28 | calm, drifting, warm ambient | GAMEPLAY playlist | tier M0 `cosy` | Best fit for low-doom bed; loops acceptably for a non-authored loop (no hard tail) |
| `PDoom1 Local maxima.mp3` | stuck on a local maximum | 1:12 | ambient with more movement, mild tension | GAMEPLAY playlist | tier M1 `uneasy` | Reads slightly less settled than Descent gradient -- fits the first step up |
| `PDoom1 Power spike.mp3` | compute/power spike | 1:12 | pushier energy, more insistent | GAMEPLAY playlist | tier M2 `spooky`; also layered at -6 dB inside M4 | The most rhythmic of the set; the natural percussion-adjacent placeholder |
| `PDoom1 Undetected sandbagging.mp3` | model sandbagging evals, undetected | 1:05 | darker, undercurrent of wrongness | GAMEPLAY playlist | tier M3 `eldritch`; base of M4 `terminal` | Darkest gameplay track; carries high-doom until real eldritch stems exist |
| `PDOOMN ST1 (safe).mp3` | "(safe)" -- the label every unsafe thing has | 1:12 | neutral-warm menu ambience | MENU playlist | none | Fine as menu bed. Filename typo "PDOOMN" preserved on purpose (it is the shipped name) |
| `PDoom Out_of_distribution.mp3` | out-of-distribution input; also "you died" | 1:00 | unmoored, wrong-place feeling | DEFEAT | none (defeat stays non-adaptive) | Good conceptual fit for defeat; could later gain a terminal-tier reprise so death sounds related to terminal doom |
| `PDoom1 seleciton beeyoowee.wav` | selection blip ("beeyoowee") | 0.72 s | UI blip, not music | listed in MENU *music* playlist | none | **Miscatalogued**: a 0.72 s one-shot inside the menu MUSIC rotation -- it plays, ends instantly, and the playlist advances. Should move to SFX duty (typo "seleciton" also preserved in the filename) |

Coherence as a SET: all six sit in the same ambient DJ-session family, so tier
crossfades between them do not clash stylistically -- good placeholder property. None
were authored as loops or stems: no shared tempo grid, no separated percussion, no
intensity-matched variants. They demonstrate the adaptive plumbing; they cannot express
the axes (rhythm-vs-timbre) by themselves.

## SFX (`sounds/`, repo root -- NOT yet in the Godot project)

`godot/assets/audio/sfx/` currently holds only a `.gitkeep`. These files are not wired
into the game and their provenance is not documented in-repo -- **verify rights before
shipping any of them** (the all-caps names read like a downloaded pack; the lowercase
ones may be homemade).

| File | Length | Reads as | Adaptive-music relevance |
|---|---|---|---|
| `WARNINGBEEP.WAV` | 0.04 s | single warning tick | loopable tick could seed the M4 FIRE layer's alarm texture |
| `SUDDENDEATH.WAV` | 6.0 s | doom hit / death sting | candidate M3->M4 filler-clip sting (see MUSIC_DESIGN.md section 6) |
| `ROCKETPOWERUP.WAV` | 1.58 s | powerup arpeggio | one-shot SFX only |
| `ROCKETRELEASE.WAV` | 3.0 s | launch whoosh | one-shot SFX only |
| `blob.wav` | 1.73 s | soft squelch | UI/feedback SFX |
| `popup_close.wav` | 1.53 s | UI close (16 kHz mono -- lo-fi) | UI SFX; consider re-render at 44.1 kHz |
| `zabinga.wav` | 1.54 s | jingle/success hit | achievement/fanfare candidate |

## Gaps to fill (the ask to the musicians)

Per `MUSIC_DESIGN.md` section 4 -- in priority order:

1. **Per-tier stem groups** for the five tiers (BASE + PULSE + WEIRD, shared tempo/key
   within each tier, seamless loops). This is the core commission; everything above is
   placeholder for it.
2. **FIRE layer** (M3/M4 topper): alarm-adjacent, driving; the audio equivalent of the
   hero image's burning monitors.
3. **Victory music** -- the VICTORY context playlist is EMPTY today (the win screen is
   silent).
4. **Terminal->defeat bridge**: a defeat sting/reprise related to the M4 material so
   losing sounds like the music finished its sentence.
5. **Menu bed refresh** (optional): `PDOOMN ST1 (safe)` works; a second menu track
   would stop the single-track loop from wearing.
6. Naming: keep the pun register -- e.g. "Mesa optimizer", "Reward hacking",
   "Treacherous turn", "Sharp left turn" are unclaimed and on-theme.
