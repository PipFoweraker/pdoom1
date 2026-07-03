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
  `scripts/generate_mechanics_docs.py`. §8 below only *points at* them.
- `[PIP]` = needs your words. `[CODE-VERIFIED 2026-06-30]` = checked against source, cite included.

---

## 1. What the game is (the one-paragraph pitch)
PIP:
You run an underfunded AI safety lab racing against well-resourced competitors. Your
choices about hiring, research priorities, and resource allocation helps shape humanity's destiny.

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

**Resolution (canonical) — survival spine, rare apex victory.** P(Doom) is *primarily a survival /
high-score game*: doom trends upward (the Doom Spiral), and a run's achievement is **how long and how
low the player holds it** — their score, ranked on the weekly-seeded leaderboard. Driving doom to 0
(ASI solved) is a *real but rare apex victory* for mastery play, not the expected outcome. Most runs
end in loss; by design the outcome is legible before doom reaches 100%, so the player may **concede
gracefully** — locking their score — rather than grind to the floor. Doom 100% is the hard floor:
total civilisational failure. *Open dial (Pip): is the apex victory reachable by skilled players, or
deliberately near-mythical? — this tunes the Safety-Flywheel-vs-Doom-Spiral balance.* Recorded in
`docs/adr/0002-win-condition-survival-spine.md`.

**Design rationale (Pip's notes):**
The game looks at two broad questions - what could we have done differently since the start of mainlining AI sfaety and now, and what will the outcomes predicted by the AI safety field be if they come to pass? My taking advantage of a time-travel based narrative structure, we can explore what our actions might do against a 'baseline' of p(Doom), a famously incalculable risk assessment that humanity is facing into with the pending arrival of AGI and, subsequently, ASI and beyond.

Through game mechanics yet to be fully articulated, high p(Doom) increases the frequency of things happening that lead to bad outcomes. We will default to using the MIT AI Risk repository's methods of classifying the taxonomies of real-world harms, and we will need to be sensitive about the in-game representations of harms. For example, catastrophic or existential levels of p(Doom) might trigger strongly negative in-game effects, like the nationalisation or militarisation of AI infrastructure, the deployment of autonomous or semi-autonomous weapons in conflict, governments and regulators ceding human control to AI corporations, fracturing of communications ecosystems, etc etc. ASI, in-game, will essentially include most of the mechanisms that foreclose on player agency and lead to any number of 'failure modes' that will result in the player losing out on access to critical resources (like money, reputation, and oxygen / biological substrate if they get Paperclipped)

I want to hold some possibility in the design space for players not to lose, but I also want to make the game so mechanistically difficult that really the majority of players won't be able to beat it without following exact steps or something. There is some ambiguity here in my mind that needs to be resolved. I note that p(Doom) doesn't kill the player unless it hits 100%; but the higher it gets, the more likely it is through various mechanics to keep increasing. 100% means we've arrived at an in-game factual representaiton of total civilizational failure, where all human agency has been ceded or all humans killed for whatever reason. The game may effectively be 'over' before then, and this can be recognised bythe player and gracefully ceded out when the writing is on the wall.


> ⚠️ Known code wrinkle to resolve separately: `godot/scripts/game_controller.gd:163` is a *second*
> win/lose implementation (loses on money/compute = 0, no doom-victory). `game_state.gd` is canonical;
> `game_controller.gd` needs reconciling or removing. Tracked as a code task, not a doc decision.

## 3. Core loop

- Turn-based, using Action Points to designate an intended plan or action taken by the player that will carry out inside the turn cycle. **3 Action Points per turn** (`docs/mechanics/README.md`; confirm against code) is the default amount; in-game decisions will vary the amount of action points available.
- Hire researchers from a candidate pool (Safety / Capabilities / Interpretability / Alignment). Train and upskill them over time. Manage their human elements so they don't burn out and keep being useful. Protect them from poaching and high paying capabilities jobs.
- Spend AP on research, fundraising, media, strategic actions.
- Resolve events and rival-lab actions; doom and reputation move; repeat.
The intended felt loop in the early game should be 'I'm making progress putting a team together'. The midgame loop should be 'How do I compete with these actors that have more resources than me / the more I explore the game state, the more ways it becomes clear I'm falling behind' and the end game state should be 'How do I manage these crises with all the challenges on my limited resources'.

## 4. Tone & aesthetic
[PIP: one or two sentences of canonical tone. Current artefacts to fold in / point at:]
- `godot/docs/design/TONE_AND_ART.md`
- `godot/docs/design/INTRO_CINEMATIC.md`
- README flavour: "Made with coffee and existential dread."
The game incorporates slightly more humorous and whimsical elements in its mechanics, particularly its story-based mechanics, than the raw numbers that the data repositories and other reference materials would indicate. Some elements of the UI will be retro / cozy / comfortable, but this is in deliberate juxtaposition with the thematic thrust of the game which is that *we are in a world that's going to get strange and bad and there's little we can do about it but feed the cat, stock up on biscuits and keep writing technical articles'.
There are some thematic matches with the 'laundry files' novels by Charles Stross - what do dedicated public servants do in the face of the end of the world?

## 5. Structure — the two-act model
Canonical structure lives in `godot/docs/design/TWO_ACT_STRUCTURE.md` (deterministic Act I /
probabilistic Act II, insight-gated "redacted" risk UI).
Pip: Act I is intended on taking place between the start of the game and the present-day, so about 2017-2026 in current design terms. It is designed to use pseudoRNG to befully deterministic based off either a custom or pre-seeded rotating weekly string, so players can compare their game runs against a standard baseline for scoring purposes.
Act II is mostly undeveloped but takes place when the game switches to a mostly historically affilicated 'This is what's happened + the player interventions on the timeline' mode to a more speculative 'We are now anticipating what the players in the game will do' mode. this is still underdeveloped in terms of mechanics. The idea behind this mode is where all the pressures of the increasing level of p(Doom) start to kick in, weird game effecst start taking place, and the gfame shifts in tone from researching things that are abstract to helping game stakeholders answer questions and deal with scenarios that have increasingly apocalyptic and catastrophic impacts.

## 6. Harms taxonomy & content sensitivity

Doom is not an abstract meter — at high levels it manifests as *represented real-world harms*. Two
commitments are canonical:

- **Taxonomy.** Classify in-game harms using the **MIT AI Risk Repository** taxonomies as the default
  scheme, so the game's harm categories map to a recognised external reference rather than ad-hoc
  invention. *(link: Pip to confirm the canonical URL before this leaves the repo.)*
- **Content sensitivity.** In-game depictions of catastrophic / existential harms (e.g. militarisation
  or nationalisation of AI infrastructure, autonomous weapons, loss of human oversight, communications
  collapse, substrate loss) are handled with deliberate care — systemic/structural framing, never
  gratuitous or targeted content.

Worked examples and the reasoning behind this section are in §2's *design rationale*.

## 7. Positioning & identity  `STATUS: ranking settled 2026-06-30; public copy still provisional`
**Ranking (resolved 2026-06-30).** The four identities are kept but *ranked* — the lower tiers serve
the primary, they don't compete with it.

1. **Primary — a downloadable single-player strategy game.** The spine; every other identity serves it.
2. **Secondary — a competitive platform** (leaderboards, weekly-seeded scoring) — an *adjunct to* the
   single-player experience, not a rival product.
3. **Tertiary — an educational tool** for AI-safety concepts, delivered *through* the mechanics
   themselves (tech tree, trade-off decisions, the in-game ecosystem), not bolted-on didactics.
4. **Quaternary — a data source** feeding the broader "AI Safety Intelligence Platform"
   (see `docs/PRODUCT_STRATEGY_RATIONALE.md`).

**Taglines** *(all untested; Pip gathering info before committing — options for selection, by register):*
- *Cozy-apocalyptic (most distinctive):* "Feed the cat. Stock up on biscuits. Hold back the apocalypse." · "Keep calm and lower P(Doom)."
- *Earnest strategy:* "Run the underfunded lab standing between humanity and P(Doom)." · "Race better-funded rivals to solve alignment — before the odds run out."
- *Survival-honest:* "You probably can't win. You can last. Lower P(Doom) for as long as you can."
- *Literary / hook:* "Bureaucracy at the end of the world." · "A strategy game about a famously incalculable risk."
- *Prior (README):* "Manage an AI safety lab racing to solve alignment before it's too late."

## 8. Canonical starting state & numbers (mirror of code — DO NOT hand-edit to disagree)
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

## 9. Relationship to other docs (what derives from this)
- `README.md` "About the Game" → derives from §1–2 (trim its win-condition + core-loop claims to match).
- `PLAYERGUIDE.md` → player-facing expression of §2–3 (currently mixes pygame-era economy; rewrite).
- `docs/mechanics/*` → auto-generated numeric detail (the only currently CI-enforced docs).
- `docs/game-design/*` (Python-era analysis docs) → archive; superseded by code + this canon.
- `docs/adr/*` → the *decisions* that produced this canon (win-condition, develop-retirement, migration).

## 10. Open questions for Pip
- [ ] §1 pitch — final wording?
- [ ] §2 — is "reach doom 0" framed as *winning* or as *a milestone you can lose after*? (affects UI/score copy) => Pip -  Getting doom to 0 is a victory condition that means that ASI is solved
- [ ] §6 — primary identity / spine, and ranking of the other three? The primary identity is a downloadable single-payer strategy game. The ssecondary identity is a competitive plaform with leaderboards, but this is an adjunct to the single player experience. The tertiary identity is that of an educational tool for AI safety concepts mostly by working them into the elements of the game itself like the tech tree, the trade-off decisions necessary in the ecosystem of the game. The quarternary (?) identity is that of the AI safety intelligence platform being fed into;
- [ ] §6 — which tagline(s) graduate from "untested" once you face the public? - Pip to claude - I havene't assembled information on these yet, pass for now or provide some options to me
- [ ] Naming: docs variously call it "AI Safety Strategy Game" (README) vs "Bureaucracy Strategy"
      (DEVELOPERGUIDE). Pick the canonical subtitle.  - PIP": AI Safety Strategy Game is the canonical choice. Bureaucracy can come up in 2-sentence copy.
