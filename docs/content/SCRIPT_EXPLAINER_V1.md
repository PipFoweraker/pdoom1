# Script: "What is P(Doom)?" -- 60-90s explainer, V1

> Status: DRAFT for Pip taste-gate, 2026-07-26. Voiced-primary (Pip ruling:
> voice YES, face NO). Register: written neutral-wry so any register from the
> voice-variant session works without a rewrite. ~185 words VO ~= 72s spoken
> at 2.5 w/s; with breathing room and shot-led pauses lands 80-90s.
> Companion: SHOTLIST_EXPLAINER_V1.md (shots S1-S8), VOICE_VARIANT_KIT.md.

## VO script (line / est. seconds / shot)

| # | VO line | ~s | Shot |
|---|---------|----|------|
| 1 | HOOK: "There's a number AI researchers argue about at parties. It's the probability that this all goes horribly wrong. I made it into a strategy game." | 9 | S1 |
| 2 | PROMISE: "This is P(Doom). You run an AI safety lab -- and the game is about what that number does while you try to move it." | 8 | S2 |
| 3 | "It's turn-based. Every month you spend money, attention, and researchers you can't fully trust -- on research, on funding, on keeping the lights on." | 10 | S3 |
| 4 | "Doom isn't a score I hand you. It's a system: streams of risk flowing from labs, rivals, and hype -- and you can see the plumbing." | 9 | S4 |
| 5 | "Every mitigation is a loan. The ledger remembers what you promised, and it bills you when the fuse runs out." | 8 | S5 |
| 6 | "Meanwhile, your office is alive. Researchers have quirks. Some of them leak. There is a cat. The simulation never lies to you -- but the characters will." | 11 | S6 |
| 7 | "Rivals race ahead whether you're ready or not. Most runs end badly. The leaderboard ranks how long you kept the lights on -- and the world intact." | 10 | S7 |
| 8 | BUTTON: "It's free, it's in alpha, and it breaks in interesting ways. Link below. Play it, lose, and tell me what broke." | 8 | S8 |

Total VO ~73s. Do not add lines; if a beat must grow, another must shrink.

## Delivery notes (any register)

- Line 1 lands on "horribly wrong" -- tiny beat before "I made it into a
  strategy game."
- Line 6: "There is a cat." is its own sentence. Do not decorate it.
- Line 8: "tell me what broke" is the brand voice of the feedback culture --
  keep it plain, not jokey.

## Title / description (step 6-7 of the pipeline)

- Title: "I made a strategy game about P(Doom) | the AI safety game"
  (claims: "P(Doom)", "AI safety game" -- pending Pip's idea-space term pick).
- Description first 2 lines: "You run an AI safety lab. Doom is a system, not
  a score. Free alpha below -- play it, lose, tell me what broke."
  + download link + devblog link.

## Appendix: no-voice fallback (text cards)

Same shots, VO lines become 6 cards (merge 3+4, merge 6+7). Card text max 12
words each, ASCII chrome style:

1. "There's a number AI researchers argue about at parties."
2. "P(Doom): you run an AI safety lab."
3. "Turn-based. Money, attention, researchers you can't fully trust."
4. "Doom is a system, not a score. Every mitigation is a loan."
5. "Your office is alive. Researchers leak. There is a cat."
6. ">> Free alpha. Play it. Lose. Tell me what broke."

Cards burn in via assemble.sh (drawtext); music carries the pacing; each card
holds ~2.5s + shot runs underneath.
