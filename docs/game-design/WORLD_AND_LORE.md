# P(Doom)1 — World & Lore (Body of Knowledge)

> **Status: living document.** Worldbuilding, flavor, naming, and narrative filling
> captured from design sessions (`[LORE]` tags) and iterated over time. Distinct from
> mechanics (`docs/mechanics/`) and decisions (`docs/game-design/decisions/`): this is
> the *fiction* the mechanics wear.

## The world

**The time-loop framing (2026-07-04).** Born from Pip's joke about hustling *"with some
time travelling foreknowledge of bitcoin prices, perhaps?"* — a player replaying a known
seed literally *is* someone with foreknowledge of this timeline. The roguelike loop
reframed as a time loop is the cheapest diegetic justification for seed-knowledge and
opening theory: **"you've seen this world before."** Costs one line of flavor text on
the seed-select screen. Seasons/seeds are *timelines*; the community's opening theory is
shared foreknowledge.

**End states (death epitaphs).** The post-mortem names *which* future got you, keyed to
the dominant doom vector: humans as slaves to whip-drones; humans hypnotised; humans
turned into computational storage biomass; the quieter ones (fraud collapse, overhang
foom). This is "the game explains your death" (ADR-0004) delivered as worldbuilding.

**Tone register.** Dark comedy in flat CRT type over raw grief: **"HypNOTised: 2.1B"**
beats a casualty counter — body-count realism risks tipping despair-mitigation into
despair. Papers, Please is the tonal north star: bureaucratic deadpan around enormous
stakes. Population figures, if shown, are *presentation* of the doom-integral
("doom-years averted"), never a separate mechanic (ADR-0002).

**The event-horizon guardrail (2026-07-12).** Pip: *"we're not saying or implying labs
*really* do any of the truly weird stuff that's going to take place later in the game."*
The fiction's claims about recognizably-real actors stop at the run's crossing of the
real-world event horizon; past it, the timeline is openly ours (seeds *are* timelines —
divergence is the premise, not a disclaimer). Player influence over other labs scales up
mostly post-horizon, so the norm-setting mechanic (ADR-0010) never reads as an
accusation about present-day labs. Researcher archetypes are likewise flavors, never
portraits of real people.

## The player's org / lab

**Who you are.** A founder whose only unscalable resource is their own hours — action
points are diegetically **the founder's personal week**. Everything else (money,
compute, headcount) scales; you don't. Hiring is buying leverage that arrives with its
own problems — the personnel register is mild exasperation (*"costly humans who come
with their own problems, bother"*), never HR-simulator gravity.

**Player archetypes (design-test personas, 2026-07-04).** Pip named three openings; use
them to test every major system (a system should be interesting to at least two):
- **The Mogul** — builds the hundred-person lab; scale as strategy.
- **The Hustler** — grows a we'll-do-it-faster, capabilities-endorsing venture and rides
  it; money as strategy.
- **The Operator** — skips to networking and politicking straight into influence;
  favors as strategy.

**Staff archetypes (design-test roster, 2026-07-12, DQ-15/ADR-0011).** Template: *lane /
unmanaged drift / appetite / quirk-rider*. Drift rule (held loosely, per Pip): **default
drift stays within-lane**; cross-lane or off-the-map drift is rare and *diagnostic* —
bad employee, bad manager, or something seriously awry. Drift isn't laziness, it's their
mission winning the backlog-ordering fight. Flavors, never portraits of real people
(event-horizon guardrail).

Pip's three (near-verbatim):
1. **The people-pleaser** — interpretability / drifts to building evals / needs
   financial stability for family / easily swayed. *Free mechanics:* rosiest
   Celine's-law reports on the org chart (a doom-legibility hazard inside payroll);
   cheap to retain with certainty; first to wobble in desperation payroll.
2. **The authoritarian pessimist** — governance / drifts to identifying and combating
   deepfakes / wants authoritarian policies, willing to trade off privacy / pessimistic.
   *Free mechanics:* your best door to government adoption (ADR-0010), with a
   letterhead-risk rider; typed attention splits (ministries vs civil society).
3. **The moral crusader** — agent foundations / drifts to lobbying for software moral
   rights / mission purity (the org must not do dual-use) / introverted coder. *Free
   mechanics:* adoption routing makes their unsocialized work stay a PDF — needs a
   champion; capabilities hires are a departure trigger.

Fable's two, drafted for Pip's edit/veto:
4. **The capabilities-curious optimist** — scaling-efficiency / drifts to capability
   gains that "also help safety, really" / wants compute + a magazine cover / genuine
   believer. The priced temptation (ADR-0010) with a face inside the org.
5. **The burned-out ex-frontier senior** — evals / drifts to quietly writing the
   tell-all memoir (a secret ledger entry with an exposure fuse, ADR-0003 reuse) /
   wants absolution / cynical.

### PROPOSED (Fable Lane 0, for Pip veto) — appetite fills

> **Strawman only — does not modify the archetype text above.** ADR-0011 §8 names the
> appetite menu (**compute, prestige/first-author, mentees, money, mission purity**) and the
> rule that *promises made to retain staff are ledger entries*. Below: 1–2 dominant appetites
> per archetype + one line of unmanaged-drift *behaviour* (what the backlog-ordering fight
> looks like when nobody steers). Register held to "bother," dark comedy, Papers-Please —
> personnel problems, not HR gravity. Pip: veto/re-pick appetites, they're deliberately
> arguable.

1. **The people-pleaser** — appetites: **money** (dominant — "financial stability for
   family" is a payroll promise, so a *ledger entry* you can't quietly drop) + **mentees**
   (secondary — being liked is the whole personality; adopts juniors, then advocates for
   them). *Unmanaged drift:* says yes to whoever asked most recently, so their week ends up
   shaped by the loudest colleague, not the plan — the interp mandate quietly becomes
   whatever evals task someone buttonholed them about at lunch. Cheap to retain, expensive
   to trust.

2. **The authoritarian pessimist** — appetites: **prestige/first-author** (dominant — wants
   to be *the* named authority whose framework the ministries cite) + **money** (secondary —
   reads power and budget as the same lever). *Unmanaged drift:* empire-builds toward the
   deepfake/surveillance beat because that's where the government meetings are, courting
   ministries on your letterhead without asking — great door, live rider (ADR-0010), one bad
   op-ed from becoming *your* PR problem.

3. **The moral crusader** — appetite: **mission purity** (dominant and near-total — the org
   must not touch dual-use, non-negotiable). *Unmanaged drift:* the agent-foundations work
   calcifies into a PDF nobody adopts while they spend the week lobbying for software moral
   rights; a capabilities hire anywhere in the org is a resignation trigger, and they'll cc
   the whole company on the way out. Bother, escalating.

4. **The capabilities-curious optimist** — appetites: **compute** (dominant — will burn the
   cluster budget on "just one more scaling run") + **prestige/first-author** (secondary —
   the magazine cover is a real motivator). *Unmanaged drift:* quietly reallocates
   `dedicated_ai_compute` (DQ-21 §1.4) toward flashy scaling results that "also help safety,
   really," publishes them loud, and nudges `frontier_capability` and `global_panic` up while
   genuinely believing they're helping. The priced temptation with a payroll number.

5. **The burned-out ex-frontier senior** — appetites: **prestige/first-author** (dominant,
   darkly — the tell-all memoir *is* an authorship move, absolution laundered as legacy) +
   **money** (secondary — the advance doesn't hurt). *Unmanaged drift:* low visible output
   while the secret memoir accretes as a ledger entry with an exposure fuse (ADR-0003);
   cynicism leaks into their evals work and their Celine's-law reports run sour rather than
   rosy — the pessimist's mirror-image reporting hazard.

## Rival labs & organizations

Rivals emerge from fog as *causes with trajectories*: a funding wave hits, a lab
accelerates, the doom instrumentation shifts — every spike has a discoverable origin
(ADR-0005). The adversary "adapts" like the Borg only in the sense that **your own
ledger is what it exploits**: the fraud your lobbying enabled funds Antagonist_Lab. Name
placeholder `Antagonist_Lab` is Pip's; a proper naming pass is owed.

## Situational Awareness, in-fiction

Sight has **provenance**, and provenance is where the conspiracy register lives:
redacted documents, cranks who are occasionally right, a source who might be a plant.
The weirdness is honest — real AI-race epistemics look like this — and the sim never
lies about itself; instruments can be fooled, but *how* they can be fooled is
knowable, and counter-intelligence is a thing you buy (ADR-0004). Channel flavors:
espionage (fast, dirty, corrodes your governance), alliance (slow, public, obligates
you), media (cheap, noisy), research (deep, narrow) — and **presence** (2026-07-12,
ADR-0014): you discover actors, alliances, and intentions by *being where they are* —
Pip: *"We discover other players in the game by encountering their units moving around
in the playing space"* — while news/newsletters are the cheaper, lower-fidelity
discovery. The hallway track is an intelligence channel.

The political register is the whip's office: *"there are critical votes coming up, and
people are wavering. have you got them?"* Pledges, favors, counterparty dread —
House of Cards, not Model UN.

## The endgame — 2037, a vignette (2026-07-12)

Pip's answer, verbatim, to "describe one late turn" (flagged by him as pure guess; kept
as the canonical *feel* target):

> *"I am negotiating to buy rents of entire data centres. I am dealing with stakeholders
> negotiating with global financial firms. I am being asked how people should cast votes
> on AI treaties. I am paying rent on hiring defensive drone swarms, losing reputation
> because my researchers are being mind-hacked by cultists, and the cat is permanently on
> fire. A manager is asking me to approve costs to evacuate the Berlin office to a bunker
> in Mongolia. Payroll is automated, I am notified when a currency collapses. I have 5
> delegates to send to 10 meetings."*

Design payload, unpacked:
- **The endgame scarcity is attention and representation, not money** — "5 delegates to
  10 meetings" is the late-game resource problem in one sentence.
- **Delegation silences mechanics**: payroll is *automated*; a currency collapse arrives
  as a *notification*, not a decision. What you've delegated stops asking.
- **Managers surface approvals, not tasks** (Berlin → Mongolia bunker: you rule on the
  cost, not the logistics).
- Escalation of counterparties: employees → team leads → global financial firms, treaty
  bodies, drone-swarm contractors.
- **The cat is permanently on fire** — the domestic running gag survives to the end of
  the world; tone anchor (the cats are already in `assets/cats/`).

## Naming & terminology

- **Doom-years averted** — the score tiebreaker; area under the survival curve
  ("the QALY of the apocalypse").
- **The badge is the date** (ADR-0009) — public score is the exact calendar day the run
  died ("I made it to March 2034"), replacing turn-count display; internals stay
  lexicographic days-survived · doom-integral. Years are the community's native
  timeline vocabulary — "I survived past 2027" is a boast and a joke simultaneously.
- **The Ledger** — payables and receivables; liabilities and favors (ADR-0003).
- **Seeds are timelines**; a seed = RNG + event schedule (ADR-0005).
- **Lead time** — what SA purchases actually buy (ADR-0004).
- Naming passes owed: rival labs, SA channels' in-fiction names, the governance stat's
  player-facing name, epitaph titles.

## Presentation-layer intents (captured from 2025-issue triage, 2026-07-13)

- **The robed cabal** (from #222, Pip: "strong yes to capture the 222 specific
  flavour"): alliance/governance votes presented with robed-council staging and
  **per-verdict character reactions as Civ II–IV-style simple few-frame animations**
  (pleased/displeased faces per vote outcome). Pip ties this explicitly to the
  downstream scene-asset-generation pipeline intent — few-frame reaction sprites are a
  cheap, generable asset class. Hardcoded vote cadences dropped (ADR-0007's scheduled
  causes own timing).
- **Insight-ladder copy** (from #515): the "Vague hints" → "Quantified" progression
  wording is kept as UI-string reference material for ADR-0004's channel-resolution
  display (the earned-instrumentation ladder's in-fiction voice).

## Change log

- **2026-07-13** — Workshop #3 triage: presentation-layer intents section (robed cabal
  + few-frame reaction animations, insight-ladder copy).
- **2026-07-12** — Workshop #2, beat 1: endgame-2037 vignette (attention/representation
  scarcity, delegation silences mechanics, burning cat); badge-is-the-date naming.
- **2026-07-04** — First fill, from Fable workshop #1: time-loop framing, epitaphs and
  tone register, founder-hours AP canon, Mogul/Hustler/Operator personas, provenance
  fiction, whip register, core terminology.
