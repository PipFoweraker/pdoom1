# Formats menu -- pick per video

> Status: DRAFT for Pip review, 2026-07-26. Effort estimates are Pip-hours
> (agent hours excluded), first-time vs once-templated. YouTube success/fail
> notes are craft heuristics, not measured facts. [heuristic]

## 1. The 60-90s explainer  << DO THIS FIRST

- What: "What is P(Doom)?" -- one video that says what the game is, shows it,
  and claims the core idea-space terms. Voiceover over captured footage.
- Script skeleton: HOOK ("I'm making a strategy game about the number AI
  researchers argue about at parties") -> PROMISE -> 3 beats: (1) you run an
  AI safety lab, turn by turn; (2) doom is a system, not a score -- show the
  meter and an event; (3) the world pushes back -- rivals/events/cat. ->
  BUTTON: download link.
- Capture needs: 5-8 shots, ~15-30s each: menu, early turns, an event popup,
  doom meter moving, office floor with cat, one ending screen.
- Effort (Pip): 4-6h first time, 2-3h templated. Most of it is capture play.
- Succeeds when [heuristic]: hook lands inside 10s; title carries the search
  terms; footage matches the sentence being spoken (shot discipline).
- Fails when [heuristic]: opens with logo/branding; tries to explain every
  mechanic; runs past 100s.
- Why first: cheapest per unit of idea-space claimed; becomes the channel's
  pinned "what is this" answer; every later video links back to it; the
  no-voice fallback variant still works if recording stalls.

## 2. One-mechanic explainer shorts (30-60s, repeatable)

- What: one short per mechanic: the Liability Ledger, doom streams, the cat,
  Attention, hiring, the league. Vertical-friendly framing from the start.
- Script skeleton: NAME the mechanic in sentence one -> show it doing its
  thing -> one design-reason sentence ("why: mitigation is a loan") -> button.
- Capture needs: 2-3 tight shots of that one system; sandbox stage often
  enough -- no full run needed.
- Effort (Pip): 1-2h each once the pipeline exists. Batch capture 3 at once.
- Succeeds when [heuristic]: single idea, loopable ending, legible UI at
  phone size (check capture at 1080x1920 or crop-safe center framing).
- Fails when [heuristic]: needs prior context; UI text unreadable small.
- Role: the steady cadence filler between bigger videos; each one claims a
  long-tail search phrase ("AI safety game ledger mechanic").

## 3. Devlog (3-6 min, monthly, rides the release train)

- What: "what changed and why" per monthly release -- design reasoning out
  loud, from the ADRs and devblog seeds. The community-building format.
- Script skeleton: this month's ONE headline change -> the design problem it
  solves (ADR reasoning, honestly, including what we rejected) -> show it ->
  what's next month -> button.
- Capture needs: mixed -- game footage + optionally editor/sandbox footage.
  Face optional; voice basically required (text-card devlogs read as
  changelogs, not devlogs).
- Effort (Pip): 3-5h per month. The script is half-written by the release
  notes + devblog seeds already.
- Succeeds when [heuristic]: cadence held (monthly, same week as release);
  personality and honest reasoning -- devlog audiences come for the designer's
  head, not polish.
- Fails when [heuristic]: irregular cadence; reading patch notes aloud;
  scope-creeping into a lecture.
- Note: this is the format most tied to Pip-the-person. Decide identity
  exposure before starting it.

## 4. Teaser trailer (45-75s, once, HOLD)

- What: the polished first-impression asset: pure captured footage + composed
  score (trailer_trudge exists) + title cards. No voiceover needed.
- Script skeleton: mood build (office, music) -> systems montage accelerating
  with the score -> doom spike -> title card -> release date/link.
- Capture needs: the best 12-20 shots the game can produce; wants round-2 art
  landed first; timing cut to the music (this is the one format where the
  ffmpeg-only path will hurt -- expect the Shotcut escape hatch).
- Effort (Pip): 10-20h spread over days, mostly gate-and-retake cycles.
- Succeeds when [heuristic]: every frame is the game at its best; music does
  the emotional work; under 75s.
- Fails when [heuristic]: shipped early as first impression with placeholder
  art -- a mediocre trailer anchors the game's perceived quality worse than
  no trailer.
- HOLD until: round-2 art landed + a store/download page worth pointing at.
  Steam page later would re-use it.

## Order of play

1. Explainer (this week -- it unblocks "telling people" with a link to send).
2. Two or three mechanic shorts (batch-captured, drip-published).
3. First devlog on the next release-train cycle.
4. Trailer after round-2 art + WS-3 mechanics settle.
