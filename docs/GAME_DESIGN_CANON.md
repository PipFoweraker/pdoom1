<!--
status: canonical-draft
applies-to-version: 0.11.0
last-verified: 2026-06-30
owner: Pip
note: SKELETON for Pip to fill. Sections marked [PIP] need your voice/thinking. Sections marked
      [CODE-VERIFIED] are mirrored from the shipping GDScript and must not be hand-edited to disagree
      with code — fix the code or the generator instead. This doc is the single source of truth for
      "what the game is" (goal, loop, positioning). For numbers, code wins; for vision, this doc wins.
-->

# P(Doom) — Game Design Canon

> **Purpose.** One place that answers "what is this game?" When another doc disagrees with this one on
> *vision/goal/positioning*, this doc wins (and the other doc is wrong — fix it). When another doc
> disagrees on a *number*, the **code** wins and both docs are fixed to match it.
> This replaces the scattered, era-split answers in `README.md`, `PLAYERGUIDE.md`, and `docs/game-design/*`.

## 0. How to use this doc
- **Canonical for:** the goal, the core loop framing, tone, two-act structure, and positioning.
- **Not the home of numbers:** balance numbers live in code and flow to `docs/mechanics/*` via
  `scripts/generate_mechanics_docs.py`. §7 below only *points at* them.
- `[PIP]` = needs your words. `[CODE-VERIFIED 2026-06-30]` = checked against source, cite included.

---

## 1. What the game is (the one-paragraph pitch)
[PIP: write the elevator pitch in your own voice. Starting clay from the current README, treat as
provisional: "You run an underfunded AI safety lab racing against well-resourced competitors. Your
choices about hiring, research priorities, and resource allocation determine whether P(Doom) reaches
0% or humanity faces extinction." — keep / cut / rewrite.]

## 2. The goal of the game (CANONICAL — this is the spine)
**Goal (Pip, 2026-06-30):** *Survive AGI — and if possible ASI — by keeping P(Doom) low for as long
as possible.*

`[CODE-VERIFIED 2026-06-30 — godot/scripts/core/game_state.gd:378 check_win_lose()]`
- **Victory:** `doom <= 0`
- **Defeat:** `doom >= 100` **OR** `reputation <= 0`
- **There is no turn limit and no "survive N turns" win condition in the shipping code.**

**Explicitly NOT the goal:** "Survive 100 turns with P(Doom) at 0%." That phrasing (currently in
README.md:27 and STEAM_INTEGRATION_ROADMAP) describes the wrong game. A "best score within N turns"
idea is welcome **as a leaderboard benchmark / achievement**, never as the win state. → see ADR on
win-condition, and the achievements backlog.

[PIP: expand the philosophical framing if you want — e.g. what "surviving ASI" means thematically,
whether reaching doom 0 is "winning" or just "not losing yet", the relationship to real-world P(Doom).]

> ⚠️ Known code wrinkle to resolve separately: `godot/scripts/game_controller.gd:163` is a *second*
> win/lose implementation (loses on money/compute = 0, no doom-victory). `game_state.gd` is canonical;
> `game_controller.gd` needs reconciling or removing. Tracked as a code task, not a doc decision.

## 3. Core loop
[PIP/CODE: confirm and flesh out. Known pieces:]
- Turn-based. **3 Action Points per turn** (`docs/mechanics/README.md`; confirm against code).
- Hire researchers from a candidate pool (Safety / Capabilities / Interpretability / Alignment).
- Spend AP on research, fundraising, media, strategic actions.
- Resolve events and rival-lab actions; doom and reputation move; repeat.
[PIP: what is the *intended felt loop* — the tension the player should feel each turn?]

## 4. Tone & aesthetic
[PIP: one or two sentences of canonical tone. Current artefacts to fold in / point at:]
- `godot/docs/design/TONE_AND_ART.md`
- `godot/docs/design/INTRO_CINEMATIC.md`
- README flavour: "Made with coffee and existential dread."
[PIP: reconcile the "cartoony/light-hearted game" vs "serious metrics" tension you noted in
PRODUCT_STRATEGY_RATIONALE — is the game deliberately tonally lighter than the data platform?]

## 5. Structure — the two-act model
Canonical structure lives in `godot/docs/design/TWO_ACT_STRUCTURE.md` (deterministic Act I /
probabilistic Act II, insight-gated "redacted" risk UI). [PIP: one-line summary here so this doc is
self-contained, then link out for detail.]

## 6. Positioning & identity  `STATUS: PROVISIONAL — do not treat as settled`
[PIP: this is the one you're still floating copy on. Do NOT let anything downstream harden this yet.]
Four identities currently coexist across docs with no stated spine:
1. A downloadable single-player strategy game (README)
2. An **educational tool** for AI-safety concepts (docs/ARCHITECTURE.md, funder-facing)
3. A **competitive platform** with leaderboards/tournaments (ALPHA_BETA_ROADMAP)
4. One half of a **two-product** vision feeding an "AI Safety Intelligence Platform" (PRODUCT_STRATEGY_RATIONALE)
[PIP: which is the *primary* identity / spine, and which are secondary? The others don't have to die —
they need ranking. Candidate taglines you've floated (mark each tested/untested):]
- "Manage an AI safety lab racing to solve alignment before it's too late." (README, untested)
- [PIP: others...]

## 7. Canonical starting state & numbers (mirror of code — DO NOT hand-edit to disagree)
`[CODE-VERIFIED — docs/SCENARIOS.md default scenario / game_state.gd]`

| Resource | Start value | Source |
|---|---|---|
| Money | 245,000 | SCENARIOS.md / funding.md (Issue #436) |
| Doom | 50 (range 0–100) | game_state.gd:14 |
| Compute | 100 | game_state.gd:10 |
| Reputation | 50 | mechanics/reputation.md |
| Action Points | 3 / turn | mechanics/README.md |
| Start year | 2017 | SCENARIOS.md |

→ **Action item (layer 2):** these should become *generated* into this table by
`scripts/generate_mechanics_docs.py` so they cannot drift. Until then, treat code as truth.

## 8. Relationship to other docs (what derives from this)
- `README.md` "About the Game" → derives from §1–2 (trim its win-condition + core-loop claims to match).
- `PLAYERGUIDE.md` → player-facing expression of §2–3 (currently mixes pygame-era economy; rewrite).
- `docs/mechanics/*` → auto-generated numeric detail (the only currently CI-enforced docs).
- `docs/game-design/*` (Python-era analysis docs) → archive; superseded by code + this canon.
- `docs/adr/*` → the *decisions* that produced this canon (win-condition, develop-retirement, migration).

## 9. Open questions for Pip
- [ ] §1 pitch — final wording?
- [ ] §2 — is "reach doom 0" framed as *winning* or as *a milestone you can lose after*? (affects UI/score copy)
- [ ] §6 — primary identity / spine, and ranking of the other three?
- [ ] §6 — which tagline(s) graduate from "untested" once you face the public?
- [ ] Naming: docs variously call it "AI Safety Strategy Game" (README) vs "Bureaucracy Strategy"
      (DEVELOPERGUIDE). Pick the canonical subtitle.
