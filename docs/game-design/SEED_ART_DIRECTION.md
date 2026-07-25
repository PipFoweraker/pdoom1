# SEED: Art Direction

RAW SEED, not decided canon. Captures Pip's art-direction thinking 2026-07-25.
Feeds WS-3 (#811), the art-generation pipeline, and the asset-registry system
(see SEED_ASSET_REGISTRY_AND_VERDICTS.md). Status: SEED. [PIP] = Pip
verbatim/near-verbatim; [CLAUDE-note] = secretariat, reword/discard freely.

---

## 1. Iteration verbs: reroll intents

[PIP] As assets go through several iterations, the verdict vocabulary should
grow beyond the 5 tags to include reroll actions: "reject, re-roll with notes"
(regenerate with new guidance/notes attached) and "reject, re-roll with things
as they are" (same prompt, new seed -> variations).

[CLAUDE-note] These feed the generation pipeline directly:
- reroll-with-notes = new prompt guidance.
- reroll-as-is = re-run the SAME captured prompt with a new seed.

Provenance capture (prompt + params per generation) is the prerequisite.
Implication for the galleries: add these as first-class actions alongside
like/dislike/favour/disfavour/promote, with an attached notes field, exported
so a generation run can consume them.

---

## 2. Lock-base + colour-via-effects

[PIP] "the further we go with some design elements, the more I want to lock
some things down and then use transparencies or effects to deal with the
colouring."

[CLAUDE-note] As base forms/silhouettes settle, LOCK them and drive COLOUR
through transparency/shader effects (modulate, overlays, palette shaders)
rather than redrawing per colour variant. Same family as palette-swap; the
office sandbox already tints via `modulate`. This is both a coherence lever and
a draw-reduction lever (one locked base -> many colourways for near-free).

---

## 3. Deeper colour-palette selection

[PIP] Wants to go "a lot deeper into colour palette selection."

[CLAUDE-note] A dedicated palette-definition/selection step: define the game's
palette(s) as an explicit artifact, then apply via the lock-base+effects
approach from (2). Candidate future tool: a palette picker / palette-apply
preview.

---

## 3b. Oversight-gap tracking

[PIP] Libraries should also track assets that have had NO judgment rendered,
"so we can see if there are gaps in my oversight."

[CLAUDE-note] Untriaged = a first-class state; surface it in the galleries (an
"untriaged" filter) and the analyzer (untriaged report) -- being added to
analyze_verdicts.py.

---

## 4. THE FIDELITY SPLIT (the headline art-direction thesis)

[PIP] "massively up-detail, up-direct, and up-render some of our hero images to
see what the upper limits are, then decide how we go 'downscale realism to
increase coziness in game, hero images portray a slightly more hardcore vision,
this complements the humorous / narrative tension to some extent'."

[CLAUDE-note] Two deliberate fidelity PROFILES:
- HERO images = high-fidelity / hardcore / more realistic.
- IN-GAME art = downscaled / cozy.

The CONTRAST is intentional and serves the tone -- the hardcore hero vision
against the cozy playable game complements the humour + narrative tension.
Method: first run an up-render experiment on a few heroes to find the fidelity
CEILING, then set the two profiles' targets relative to it. This changes
generation: two target profiles, not one.

---

## 5. Generation strategy tie-in

[CLAUDE-note] Round-2 generation therefore has two tracks:

(a) IN-GAME library -- fill the analyzer's structural gaps (windows/tilesets)
at the cozy fidelity profile, coherence preamble, disfavour-as-negatives.

(b) HERO up-render experiment -- push select heroes to the ceiling to validate
the hardcore profile.

Provenance captured on both so keepers can be re-run coherently.

---

Related: SEED_ASSET_REGISTRY_AND_VERDICTS.md, tools/art_review/README.md,
WORKSHOP_3_PREP.md, the office sandbox.
