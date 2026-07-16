# Art Production Plan -- road to a coherent visual style

> Front-loaded planning for the big art sweep. Written 2026-07-16 for a next-morning
> selection sweep. The style is LOCKED; what remains is breadth + coherence.

## The thesis (my view on what's left)

We are past style exploration. The winning direction is settled and validated on
two rounds of review:

**Locked style = warm-grime-heft, view-locked.** Warm cozy lived-in palette with
soft grime + bold heavy black outline + deep-contrast shadows, cartoony retro RPG,
at a fixed low-top-down camera (symmetrical / straight-on / centered). Round-2
scored 6/8 "excellent" on this, so it holds across varied shapes.

That changes what the sweep IS. Tomorrow is **not** an A/B of styles -- it is a
**selection sweep**: roll each prompt 3-4 times (pixellab varies per roll), then
pick the best composition within a close range. Pure quality selection, your eye
doing subtle picks. That is exactly the "picking-within-close-ranges" you described,
and it front-loads cleanly because the prompt list can be written now.

**Coherence is not "more assets" -- it is consistency across a complete-enough set.**
The five levers that make a pile of sprites read as one world:
1. **One camera pitch** (low-top-down) on everything. Non-negotiable; mixing pitches is what broke round-1 desks.
2. **One light direction** (specify it in every prompt -- pixellab drifts otherwise; this was the round-1/2 "perspective slightly wrong" note on the water cooler + server rack).
3. **Era-tiers** for anything the office upgrades: scummy (startup) -> decent (funded) -> sleek (megacorp). This is the office-reflects-your-state mechanic, and it multiplies prop counts by ~3.
4. **Consistent palette + outline weight** (the heft) so a desk and a fridge sit together.
5. **Common scale + floor footprint** so relative sizes read true and y-sort depth works.

**What "coherent enough to ship" means:** you can dress a believable office at each
phase (startup / funded / megacorp), populate it with a varied cast, and let the cat
+ window signal doom -- all in one visual language. That is the P0 set below. Everything
else (P1/P2) deepens the world but is not load-bearing for coherence.

## Scope + budget

~64 distinct prompts across all categories. At 3-4 rolls each that is **~190-250
generations**. Budget remaining is ~1,900 (Tier-1, 2,000/mo), so the entire sweep
fits comfortably in one morning with room to re-roll. Pacing is the only limit:
pixellab throttles at ~4-5 concurrent, so a full sweep is a paced background loop,
not one big fire.

Priority tiers: **P0** = needed for a coherent office at all three phases (do first);
**P1** = fills the world; **P2** = polish / nice-to-have.

---

## The tables

Legend: **tiers** = how many era/quality variants (S=scummy, D=decent, M=megacorp);
**rolls** = re-rolls per prompt for the selection sweep; **have** = already generated.

### A. Character bodies (P0/P1)
Diverse identities, ability-uncorrelated, warm-grime-heft. Bodies are cheap to roll;
**animation is the expensive step** (each kept body needs idle + walk x4 dirs + work +
stressed = ~7 clips). So: sweep BODIES now (2 rolls each, pick faces), animate only the KEPT ones.

| asset | priority | rolls | notes |
|---|---|---|---|
| Base floor worker (re-style) | P0 | 2 | existing 0a6a27ed is the OLD style; regen in warm-grime-heft to standardize |
| Cast: burned-out senior | P0 | 2 | taster generating now |
| Cast: eccentric junior | P0 | 2 | taster generating now |
| Cast: South-Asian researcher | P0 | 2 | taster generating now |
| Cast: +4 more identities | P1 | 2 | e.g. young Black woman, older woman lead, wheelchair user, visibly-eccentric genius -- ability-uncorrelated |
| Founder silhouette (Dr Claw) | P1 | 3 | NOT a floor worker; WATCH-screen operator, customizable throne/robes |

Roster target ~8 bodies for roguelike variety. ~8 body prompts, animate the ~6-8 keepers after picking.

### B. Character cosmetics / reveal layer (P1/P2)
The hidden-info reveal -- accessories accrue as you scout a hire. Overlay sprites (swappable) vs baked states TBD.

| asset | priority | rolls | notes |
|---|---|---|---|
| Hat: medium / tall / sports (x3) | P1 | 2 | impostor-satire cosmetics; tall hat already exists |
| Lab coat overlay | P1 | 2 | reveal-trait clothing |
| Security badge / lanyard | P2 | 2 | |
| Headphones (heads-down) | P2 | 2 | ties to Secrecy Maximalist / Runs Hot quirks |
| Coffee mug / laptop-bag held items | P1 | 2 | held-item states (create_character_state trick) |

### C. Cats -- doom-barometer forms (P0/P1)
Keyed to doom bands. Both existing forms now walk in 4 directions.

| asset | priority | rolls | notes |
|---|---|---|---|
| Singed tabby (low doom) | have | -- | +walk x4 done |
| Spooky black (mid doom) | have | -- | +walk x4 done |
| Eldritch / high-doom form | P0 | 3 | the "weird" band -- more forms, smoke, wrong angles |
| Purple end-state form | P1 | 3 | "what comes after red" doom-end |
| Cat furniture: bed / litter (have) | have | -- | scummy/decent tiers optional (P2) |

### D. Props -- desk & workstation (P0, tiers x3)
The core of the floor. Era-tiers are the upgrade mechanic.

| asset | priority | tiers | rolls | notes |
|---|---|---|---|---|
| Desk | have S/D | +M | 3 | add megacorp tier |
| Office chair | have (re-rolled) | +D/+M | 3 | starting chair now older/cheaper; add decent + sleek |
| Monitor | have S/D | +M | 4 | WEAK subject -- roll more; must read as powered/glowing |
| PC tower | have S/D | +M | 3 | |
| Keyboard + peripherals | P1 | S/D | 2 | small desk-dressing |

### E. Props -- compute / research (P0/P1)
The compute-hunger + research-culture flavour.

| asset | priority | tiers | rolls | notes |
|---|---|---|---|---|
| Server rack | have | +M cluster | 3 | mega tier = a glowing compute cluster (compute appetite) |
| Whiteboard w/ equations | have | -- | 2 | scored "Good!"; maybe 1-2 equation variants |
| Research poster / diagram wall | P1 | -- | 2 | |
| Book / paper stacks | P2 | -- | 2 | desk-dressing |

### F. Props -- kitchen / social (P1)
Morale corner.

| asset | priority | tiers | rolls | notes |
|---|---|---|---|---|
| Fridge | have S/D | -- | -- | done |
| Coffee machine | have S/D | -- | -- | done |
| Water cooler | have | -- | 2 | "extremely good", minor perspective re-roll |
| Kitchen counter / bench | P1 | S/D | 3 | requested earlier, not yet made |
| Microwave | P2 | -- | 2 | |
| Break couch | have | +tiers | -- | "excellent" |

### G. Props -- misc office (P1/P2)

| asset | priority | tiers | rolls | notes |
|---|---|---|---|---|
| Bookshelf | have (re-rolled metal) | -- | -- | office/laminate version pulled |
| Filing cabinet | P1 | S/D | 2 | |
| Printer / copier | P1 | S/D | 2 | |
| Trash can / recycling | P1 | -- | 2 | |
| Coat rack | have | -- | 2 | "excellent"; minor neaten re-roll |
| Desk lamp | P2 | -- | 2 | |
| Wall clock | P2 | -- | 2 | |
| Rug | P2 | S/D | 2 | |
| Potted plants (variants) | have | +2 | 2 | "excellent"; a couple more species |
| Meeting table | P1 | S/D | 3 | Entity-phase |
| Reception desk | P2 | D/M | 2 | Entity-phase |

### H. Environment -- the room (P0, BLOCKED on a decision)
Gated on: prop-only-on-a-background NOW vs top-down tileset LATER. Needed for a real room.

| asset | priority | tiers | rolls | notes |
|---|---|---|---|---|
| Floor tile (carpet / lino / concrete) | P0 | 3 | 3 | if tileset route |
| Wall segment | P0 | S/D | 3 | |
| Door | P0 | S/D | 2 | |
| Window (have S/D) | have | -- | -- | done as props |
| Window weather layers | P1 | 4 | 3 | clear / overcast / storm / doomy-red-purple -- the weather-portal idea |

### I. UI / iconography (P1)
Much exists (91 gpt-image-1 icons). Gaps:

| asset | priority | rolls | notes |
|---|---|---|---|
| Resource icons (money/doom/attention/compute/reputation) | P1 | 2 | consistency pass in the pixel style |
| Candidate-card frame | P1 | 2 | ties to the pool UI build |
| Doom meter / band art | P2 | 2 | |

### J. Effects / motifs (P1/P2)

| asset | priority | rolls | notes |
|---|---|---|---|
| Doom glow (red -> purple) | P1 | 2 | the negative-value + doom-end signal |
| Bayes-rune glow set | P2 | 3 | endgame motif; Bayes-in-Bayer-dither pun; readable P(A\|B) needs hand-authoring |
| Compute glow | P2 | 2 | |
| Selection outline | -- | -- | SHADER (engine), not art -- no generation needed |

---

## Sweep methodology (tomorrow, turnkey)

1. **The prompt list is pre-written** in `tools/art_review/sweep_prompts.json` (P0 core to start). Each entry: key, category, description, size, rolls.
2. I run a paced generator over it (~4 concurrent), pulling each roll into `art_source/pixellab_<date>/sweep/`.
3. `build.py` renders them into the review tool as **gallery batches, grouped by asset with the 3-4 rolls side by side** -- so you pick within close ranges.
4. You mark keep/re-roll + notes, Export, paste back. Keepers get committed; re-rolls get re-queued.
5. Kept bodies + cats then go to the animation step (idle/walk x4/work/stress).

Front-loading payoff: because prompts + tool + pull/build pipeline all exist, the
morning is just **generate -> pick -> commit**, no setup.

## Open decisions that gate art (need your call)

1. **The room:** prop-only-on-a-flat-background now, or commit to a top-down tileset? This gates floor/wall/door (section H). Leaning prop-only now, tileset as its own wave.
2. **Re-style the existing floor worker + already-animated assets** into warm-grime-heft? Standardizing on the new style means the current base worker (old style) should be regenerated. Cost: re-animate. Recommend yes, batched.
3. **Cosmetic reveal layer:** swappable overlay sprites vs baked `create_character_state` variants. Affects how section B is generated.

## Rough totals

| bucket | distinct prompts | ~generations (x3-4) |
|---|---|---|
| P0 (coherent MVP) | ~26 | ~90 |
| P1 (fills world) | ~24 | ~85 |
| P2 (polish) | ~14 | ~45 |
| **total** | **~64** | **~220** |

Comfortably one morning's sweep against a ~1,900 budget.
