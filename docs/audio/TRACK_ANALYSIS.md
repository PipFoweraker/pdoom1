# P(Doom)1 -- Beloved-track analysis (method + template)

> Pip has a track he listens to 2-3x/day. That track is the project's TASTE REFERENCE:
> decoding *why it grips* gives the musicians a concrete target instead of vibe-words.
> The track name/link arrives separately; this file is the METHOD and the fill-in
> TEMPLATE. Nothing below assumes a specific track. Written for a low-music-literacy
> owner: every step says exactly what to do and needs no theory.

## Method: five listening passes (about 30-40 minutes total)

Do the passes in order, one focus each. Use headphones. Write timestamps as `m:ss`.

### Pass 1 -- Structure map (what happens when)
Listen once with a notepad. Every time the track *changes* (something enters, drops
out, gets louder, mood shifts), write the timestamp and one plain phrase:
"1:12 drums drop out", "2:40 gets huge". No vocabulary needed. You now have the
track's shape -- this is the single most useful artifact for the musicians.

### Pass 2 -- Pulse and speed (tempo)
- Tap along with the beat on a tap-tempo site (search "tap tempo", tap 20+ times) ->
  BPM number.
- Cross-check by searching "<track name> BPM key" (Tunebat/SongData list most tracks).
- Note WHERE the pulse lives: kick drum? bassline? a repeating synth? And whether it
  ever stops.

### Pass 3 -- Key and harmony (the mood machinery)
- Get the key from the same lookup sites (do not derive it by ear).
- Answer in plain words: does it feel resolved or endlessly suspended? Does it loop a
  short chord cycle (count: does the "home" feeling come back every 2/4/8 bars)?
  Bright or dark? Does the mood shift mid-track or stay in one weather?

### Pass 4 -- Instrumentation and texture (who is speaking)
List every distinct voice you can pick out (name them functionally: "deep bass",
"shimmery pad", "clicky percussion", "human voice"). For each: when is it present
(reuse Pass 1 timestamps), and is it clean or dirty/distorted/detuned?
Optional: open the file in Spek (free spectrogram) -- a dense bottom = bass-heavy,
striped top = bright percussion. Screenshot it into this doc.

### Pass 5 -- Production feel + the grip (the actual question)
- Space: does it sound like a small room, a cathedral, or headphone-internal?
- Dynamics: does it breathe (quiet/loud waves) or hold one intensity?
- Then the core: at which exact timestamps do you feel the pull? What JUST happened
  at each of those moments (check the Pass 1 map)? The grip almost always lives in a
  repeatable trick: a tension that only half-resolves, a texture change right when the
  loop would get boring, an entrance you wait for. Name the trick in your own words.
- Honesty check: is the grip musical, or is it associative (memory/person/game it is
  tied to)? Associative grip is real but does not transfer to a commission -- say so.

## Translating findings -> direction the musicians can use

| If the analysis found... | Then the ask is... |
|---|---|
| Grip lives at entrances/drop-outs | "Stems must create arrival moments: build layer entrances players can wait for" (maps to tier up-transitions, MUSIC_DESIGN.md sec 6) |
| Endless-suspension harmony, never resolves | "Keep tier beds harmonically open -- avoid full cadences; doom never resolves" |
| One dirty voice over a clean bed | "One WEIRD stem over a clean BASE" -- confirms the one-weird-glow rule (sec 2) |
| Slow breathing dynamics | "Long-form volume waves inside each loop so a 2-min stay in one tier does not flatline" |
| Tempo X, pulse carried by Y | "Tier tempo lanes near X BPM; put the pulse in the PULSE stem on instrument-type Y" |
| Grip is associative, not musical | Do NOT ask musicians to clone the track; extract only tempo/texture facts |

## Template (fill in when the track arrives)

```
TRACK: <name -- artist>              LINK: <url>
LISTEN COUNT / CONTEXT: <when/why Pip plays it>

PASS 1 -- STRUCTURE MAP
  0:00  <...>
  <m:ss>  <...>
  Overall shape in one sentence: <...>

PASS 2 -- TEMPO
  BPM (tapped): <...>   BPM (lookup): <...>
  Pulse carried by: <...>   Pulse ever stops?: <...>

PASS 3 -- KEY / HARMONY
  Key (lookup): <...>
  Resolved or suspended: <...>   Chord-cycle length (bars): <...>
  Mood weather: <bright/dark/shifting -- describe>

PASS 4 -- VOICES
  <voice> -- present <m:ss>-<m:ss> -- clean/dirty: <...>
  <voice> -- ...
  Spectrogram notes (optional): <...>

PASS 5 -- PRODUCTION + GRIP
  Space: <...>   Dynamics: <...>
  Grip moments: <m:ss> because <what just happened>
                <m:ss> because <...>
  The trick, in my words: <...>
  Musical or associative?: <...>

DIRECTION FOR THE MUSICIANS (3-5 bullets, plain language,
use the translation table above):
  - <...>
  - <...>
```
