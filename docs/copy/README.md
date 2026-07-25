# docs/copy/ -- the Voice Seam (SOURCE, not published copy)

**Status:** ACTIVE POLICY (2026-07-25). This is the interface contract between
`pdoom1` (this repo) and `pdoom1-website`. Edit it as policy, not as notes --
its diff history is part of the record.

---

## What this folder is

The canonical SOURCE of P(Doom)1's voice, positioning, and copy raw material.

- **`pdoom1` (this repo) = SOURCE.** It owns MECHANICS, DESIGN, and PHILOSOPHY,
  and the *raw* voice/positioning material derived from them. Nothing in this
  repo is final, approved, or published copy.
- **`pdoom1-website` = PUBLISHER.** It PULLS the canonical source files below,
  EDITS/COLLATES them into finished posts, and PUBLISHES to the website /
  LinkedIn / LessWrong / other channels. Final, approved copy lives THERE.

## The contract (both repos' agents read this)

1. **Direction is one-way.** `pdoom1-website` reads `pdoom1`. `pdoom1` never
   depends on `pdoom1-website`. If you are an agent in `pdoom1` reaching into
   the website repo for content, stop -- you have the direction backwards.
2. **Commentary originates here only when the mechanics/design demand it.** A
   design decision, a philosophy shift, a new mechanic's framing -- those are
   born here because they are downstream of the game. The *finished words* that
   sell/explain them live in `pdoom1-website`.
3. **Nothing here is published copy.** Treat everything in the voice seam as raw
   material with provenance, not as approved marketing. Voice tags (`[PIP]` /
   `[PIP-idea / Claude-prose]` / `[CLAUDE]`) mark confidence and authorship.

## Canonical source files (the "voice seam" pdoom1-website pulls)

- `docs/copy/COPY_CORPUS.md` -- catalogued raw copy, taglines, provenance, voice
  tags. The primary pull target.
- `docs/game-design/DESIGN_PHILOSOPHY.md` -- the "why", verbatim Pip quotes.
- `docs/PRODUCT_STRATEGY_RATIONALE.md` -- two-products / open-dataset strategy,
  the B2B/public-good framing.
- `docs/game-design/WORLD_AND_LORE.md` -- personas (Mogul/Hustler/Operator),
  tone north star, Antagonist_Lab.

These four are the seam. If a fifth source becomes load-bearing for public
copy, add it here so the website agent knows it is fair game.

## Pull mechanism

**Agent-manual, for now.** The `pdoom1-website` agent reads these files directly
from the `pdoom1` repo (clone/fetch) and hand-collates. No sync script, no
submodule -- deliberately, until content volume justifies automation. When it
does, this section is where the automated pull (submodule / sync job) gets
specified.

## Related

- `docs/CONTENT_DISTRIBUTION_SYSTEM.md` -- OUTDATED predecessor (proposed
  publishing *from* pdoom1). Superseded in spirit by this contract; flagged for
  Pip's revision during doc uplift. Retained for diff history.
