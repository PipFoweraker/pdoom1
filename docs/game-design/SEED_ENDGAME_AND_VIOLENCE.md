# SEED: End-game, Failure Modes & the Arrival of Violence

> LOSSLESS capture of Pip's 2026-07-25 rapid brain dump (inspiration notes, taken
> fast to get them out of his head). RAW SEED, not decided canon. Feeds WS-3 (#811)
> and the late-game / future-epoch design. `[PIP]` = verbatim; `[CLAUDE-note]` =
> secretariat connection or tension, reword or discard freely.

## 1. End-game content from real failure-mode literature [PIP]
> "we can derive a lot of meaty end game content by failure modes outlined in
> yud's list of lethalities and the failure modes already sketched out by others
> in eg ai2027 and ai2040"

[CLAUDE-note] Extends the reality-tether / league-metabolism principle (ADR-0016,
"reality becomes the map generator") to the END-GAME: the doom-streams' terminal
textures get their content from real AI-safety failure-mode writing (Yudkowsky's
"AGI Ruin: A List of Lethalities"; the AI-2027 / AI-2040 scenario forecasts).
Guardrail to respect -- WORLD_AND_LORE's "we're not saying labs really do the truly
weird stuff": author the FEEL of the failure modes, not a claim they are happening.

## 2. Research as compute vs non-compute streams [PIP]
> "we can get a lot more value by streamlining research into compute and non
> compute heavy streams these have different payoff periods and downstream impacts"

[CLAUDE-note] A concrete axis for the workstream substrate WS-3 is scoping
(ADR-0011 / RESEARCH_IDEA_PAPER_PIPELINE_GAP.md): compute-heavy vs non-compute-heavy
research = two streams with different DURATIONS (ADR-0009) and different downstream
effects. Ties into the office/finance economy: compute = a purchasable, burnable
resource with lead time; non-compute = founder/researcher hours. Near-term mechanic
candidate.

## 3. Tech-tree robustness to fluid influence [PIP]
> "design of anything like a tech tree has to be robust to matching and argument
> about influence in a really fluid way"

[CLAUDE-note, INTERPRETATION -- confirm with Pip] Reads as: progression must NOT be a
rigid prereq tree; it must survive influence flowing and being contested fluidly.
Connects to the Politics / Money / Technology polyvirate (SEED_RIVAL_AND_DEVELOPMENTS):
capability/influence as a fluid web, not a locked tree. Design constraint: prefer a
fluid influence model over a classic tech tree.

## 4. Funny -> violent reputation-loss escalation [PIP]
> early reputation loss -- "you get beaten up at a party"
> late game reputation loss -- "helmeted government agents crash in through your
> conference room windows and black bag you into a helicopter"

[CLAUDE-note] A tonal escalation ladder for the "Developments" narrative-pressure
system (SEED_RIVAL_AND_DEVELOPMENTS): early beats are comedic/personal, late beats
turn violent/state-level. The drama of a reputation hit scales with game stage --
Papers-Please deadpan early, thriller late.

## 5. The arrival of violence = the end-game escalation signal [PIP]
> "we want the arrival of violence to kind of mechanistically signal incredibly
> hard to recover from end game states, because they will tend to increase
> escalation and player should be pretty outgunned unless they dive hard into
> military opti[ons]... right now it is overly simplistic and not consuming enough
> attention, we are under-pressured to spend enough each turn at this point.
> Luckily, now we have the fundamental elements of our game engine, these mechanics
> feel like they will be relatively emergent to both execute and explore / balance."

[CLAUDE-note] The load-bearing late-game idea, three parts:
- Violence = a near-terminal state MARKER: escalation ratchets, recovery is hard --
  a designed "point of no return" on the doom spiral (ADR-0002 survival spine).
- The player is OUTGUNNED unless they pre-invested in military depth -- military is
  an optional deep path, not a default.
- It FIXES a named flaw: the end-game currently consumes too little attention (the
  player is under-pressured to spend each turn). Violence/military is the mechanism
  that RAISES late-game attention demand (connects to the DIAL5 attention-scarcity
  work).

## Emergent tensions + open questions (secretariat) [CLAUDE-note]
- **THE sharp tension -- is "military" a legitimate strategy or a desperation-trap?**
  A safety-LAB pivoting to military power cuts against the thesis. Is diving into
  military a genuine winning branch, or another "every mitigation is a loan"
  desperation-lever (ADR-0003) that reads as help and isn't? Deciding the moral +
  strategic status of the military path is the biggest fork here.
- **Violence trigger:** what fires it -- rival aggro-threshold (DQ-22), a doom
  threshold, or player VISIBILITY (you got big enough to be a target)? The
  reputation ladder (item 4) points at visibility.
- **Compute vs non-compute:** two discrete streams or a spectrum? Concrete
  payoff-period + downstream-impact differences (near-term item).
- **Failure-mode dosage:** how much real-lethality texture before it becomes a
  persuasion piece (WORLD_AND_LORE guardrail).
- **End-game attention pressure:** the concrete fix for "not consuming enough
  attention" late -- more/costlier reactive windows, military upkeep, escalation
  demands?

**Related:** SEED_RIVAL_AND_DEVELOPMENTS.md, WORKSHOP_3_PREP.md, DESIGN_PHILOSOPHY.md
("the world shoots back", desperation-as-trap), ADR-0002 (survival spine), ADR-0011
(research/effort), RESEARCH_IDEA_PAPER_PIPELINE_GAP.md, ADR-0016 (league metabolism /
reality-tether), the DIAL5 attention-scarcity proposals.

---

## Wave 2 -- endgame stays emergent + the CROSSOVER beat (Pip, 2026-07-25)

**Endgame = multiple overlapping clusters, NOT fixed mechanisms.** [PIP]
> "I suspect there might be multiple likely end-game-state clusters that will emerge --
> I think we'll try not to get tied down in particular endgame mechanisms the same way
> we tried not to get tied down to rigid tech tree development -- I imagine a lot of
> clusters in probability space starting to overlap until something eventuates -- we'll see."

[CLAUDE-note] Same anti-rigidity stance as the fluid-influence progression model: don't
hardcode THE endgame; let several end-state clusters coexist and overlap until a run
resolves into one. The violence proposal (military-as-trap-or-path) is ONE such cluster,
not the whole endgame.

**CROSSOVER -- the historical -> forward-looking temporal switch (placeholder name).** [PIP]
> "The part of the game that will get purely predictive i.e. after CROSSOVER (placeholder
> until we find name for temporal switch from historical to forward-looking) -- at that
> point we want to lock in a probability set or something that's visible and then the
> players can battle out to end-game... a nice weird WARP or something around the
> now-moment in time, then everything has weirdly different names and the money's called
> Schmekels or something -- this has slipped us into an alternate timeline, and we can't
> rely on our knowledge of the past any more!"

[CLAUDE-note] A structural beat + tone shift, and it does DOUBLE duty:
- Until CROSSOVER the game runs on curated REAL history (reality-tether / ADR-0016,
  trailing reality by ~a month). At CROSSOVER (the game catches up to "now") it switches
  to purely SPECULATIVE / forward-looking: lock in a visible probability set; players
  battle to end-game on it. This is the clean handoff from deterministic-historical to
  speculative-forward -- and where a forward probability set (cf. #236 prediction-market
  doom) would live.
- The alternate-timeline reskin (renamed money "Schmekels", weird names, "can't rely on
  the past") is also the real-world-slander SOLVENT: post-CROSSOVER events are overtly
  fictional, not claims about real actors. A fun narrative rupture AND a legal/tone
  guardrail in one beat.
- Nominal target to reach CROSSOVER: ~1.0 [INFERRED from Pip's data-sharing pacing note].
