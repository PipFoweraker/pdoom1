# P(Doom)1 — Design Philosophy

> **Status: living document, interview-extracted.** This is Pip's design philosophy in
> Pip's words, drawn out over successive design sessions (Fable interviews). It is meant
> to be iterated, contradicted, and sharpened over time — not finalized. Each principle
> should preserve the original phrasing that produced it before any paraphrase.
>
> Capture rule: when a session surfaces a `[PHILOSOPHY]` moment, paste the raw quote here
> under the right heading, dated, before editing it into a principle.

## Provisional principles

### On what the game is *for*

**(2026-07-04)** *"The game is about the challenge facing real AI safety researchers,
grantmakers and philanthropists, wrapped in a game to communicate the challenge while
mitigating the actual despair."*
→ Not a persuasion piece — a **sandbox for a live research question** (there is no
consensus to persuade people toward). The wrapper's job is emotional load-bearing: let
people stay in contact with the problem longer than despair normally permits.

**(2026-07-04)** *"the theoretical payoff is a few people learning a bit more about AI
safety as a side effect from playing an engagingly hard game, the same way young me
learned a bit about history by playing Civilization."*
→ The game teaches by **incidental contact, not argument**. This deflates the "tool"
claim healthily: balance patches don't owe historiography corrections (Civ nerfs units
freely). The one place the stronger standard survives is **structure, not numbers**: the
shape "you cannot win, only buy time, and you can't see what's killing you without
paying" is the load-bearing claim, never to be patched for freshness.

**(2026-07-04)** *"my short or medium term time lines actually will likely come true in
real life and… AGI might be survivable but ASI won't be."*
→ This belief is already structurally encoded: every run ends, only duration varies.
The honest version of the game has **no victory, only time bought** (ADR-0002).

**(2026-07-04)** *"[patches] took this from 'a game 200 people might play, ever' to 'a
game where 30 nerds might enjoy playing this for long enough to form a community' which
actually seems better?"*
→ Target: **small durable community over large audience**, with the **patch as the
community's heartbeat** — patches don't need to be frequent, they need to be *legible
events* people argue about.

**(2026-07-12)** *"people voluntarily adopting good actions will generate the space for
better actions to come about, and this is how small and middle power players can affect
things - norm and market setting"*
→ Pip's real-world theory of change, now load-bearing structure (ADR-0010): doom bends
where work is **adopted**, not where it's written. This is the second structural claim
(after "you can't win, only buy time") that is never patched for freshness.

### On losing (the core emotional design)

**(2026-07-04)** *"the game's default value is that they'll lose, and lose repeatedly,
and beyond a certain curve, any additional turn you survive means you've done a lot of
extra things right earlier in the game."*
→ **Survival time is the score, and it must be skill-legible** — every extra turn
attributable to something the player did.

**(2026-07-04)** *"A good loss means you survived a few turns more than last time. A
better loss might be when you beat other people using a similar strategy in this week's
ladder. The best loss might be finding a new set of starting moves that leads to
everyone on the ladder adopting your early game for that meta before a new balance
patch."*
→ The meaning of a loss escalates through three rings: **personal → competitive →
cultural**. The best thing a player can do in this game is change how everyone else
plays it.

**(2026-07-04)** *"I think of the PoE leaderboards where so many players will only ever
get one character to level 80; that'll be their best character over many seasons,
whereas other players will level multiples to 99 in one season."*
→ **The turn count is a badge, not a number** — milestone semantics legible across the
community ("I got to turn 20"), requiring an exponentially hard ladder. Mechanism: the
Liability Ledger — your own accumulated debts are the difficulty curve (ADR-0003).

**(2026-07-12)** *"a well balanced ladder might have people overtaking each other by days
in a period where their decisions are locked in in months or quarters, which leads to
interesting paths on a ladder style race for increments."*
→ **Coarse hands, fine scoreboard.** Decisions lock at month grain; the score resolves at
day grain (the badge is the exact death date, ADR-0009). The gap between the two grains
is where ladder drama lives — photo-finishes between players who never had day-level
control.

**(2026-07-04)** *"only the vastness of the design space will be what stops a determined
player just brute-forcing their way to a high score… although I would laud the
initiative!"*
→ **Verification is the only law.** Anyone who submits a legal, replayable run is a
player — bots and brute-forcers included. Tool-assisted play is culture, not cheating
(ADR-0006).

### On tension and tradeoffs

**(2026-07-04)** *"like taking out a credit card to save the mortgage, then taking a job
as a lobbyist to pay off the credit card, then lobbying to weaken financial regulation
on AI firms which then leads to an increase in AI driven fraud which then funds
Antagonist_Lab"*
→ **Every mitigation is a loan.** The game's tension generator: trades that pay now and
bill later, sequenced (ADR-0003). Skill is debt-portfolio selection.

**(2026-07-12)** *"I want to leave options for the player to contribute towards
capabilities in a way that increases danger but allows them more resources, as well,
that's a good and useful temptation and also correctly acknowledges the dual-use element
of the technology we're exploring in the AI safety space."*
→ **The dual-use temptation is priced, not forbidden.** Capabilities work is a legal lane
that pays in money/compute/hype and bills in doom — the Situational-Awareness-essay arc
(awareness → personal reputation → someone funds your capabilities-heavy play) is the
canonical real-world generator. Deepest ledger entry in the game.

**(2026-07-04)** *"Much like the founding location in civ matters, I feel like players
will start to point themselves in strategic directions in their early decisions."*
→ **The opening is a commitment device** — early moves aim the run; balance work exists
to protect that aim's meaningfulness into mid/late game.

**(2026-07-04)** *"these are the resources by which you get things done, given your tiny
manual amount of hours per week (action points), you're going to hire costly humans who
come with their own problems, bother."*
→ **Staff are leverage, not simulation subjects.** Canon: AP are the founder's personal
hours — the one resource that never scales. Every hire converts money into action
bandwidth and arrives with a liability rider.

### On the turn (the core loop)

**(2026-07-12)** *"I suppose what I want is the feeling of making a little plan and then
having to make trade-offs against the perfect execution of that plan. And the scale of
those interventions and balancing it is what is going to drive the game's narrative
tension."*
→ **A turn is a plan you watch collide with reality.** Two decision speeds — plan-time
(sorcery) and interrupt-time (instant) — over a resolution tick (the day) that owns no
routine decisions. Guard rule: no mechanic may hang a decision on the day tick.

**(2026-07-12)** *"I suppose I want to feel in control, comfortable when I delegate, and
like the end results are a result of my selections as opposed to pure simulations
running?"*
→ Extends skill-legibility (ADR-0002) inward: **every period's outcome must trace to a
selection the player made** — a plan, a response, or a deliberate inaction. The sim
generates pressure, never authorship.

**(2026-07-12)** *"if players reserve a healthy amount of slack in their systems, they
will be able to weather unusual events, but maybe they will get away by being greedy and
overcommitting themselves."* and *"I don't think we can let players bank time."*
→ **Slack is insurance the player is allowed to gamble against.** Reserved capacity
answers events painlessly; overcommitting is a legal bet that sometimes pays. Unspent
time evaporates at reset — banking is dead; crisp commitment-loss over soft fallbacks.

**(2026-07-12)** *"as a CEO, I care about managing the first half dozen people or so.
Then I probably want team leaders to stop me making employee-level decisions. Then I
probably want divisions to manage the teams... A game that forces me to manage every
employee if we scale to 100 employees will become draining."*
→ **The management grain coarsens as the org scales** (Factorio's complexity-progression
*feeling*): people → team leads → divisions. Attention, switching costs, and the waste of
abandoning work are the intended mid/late-game challenge material, not more knobs.

**(2026-07-12)** *"the player's situational awareness (or they can opt to turn off e.g.
medium news to reduce notification or decision spam) impact the number of tactical events
they *get* to respond to, as opposed to simply finding out they've happened"*
→ Cashes out ADR-0004's "SA buys lead time" mechanically: **situational awareness
purchases response windows** — the difference between an event you could answer and one
you merely read about afterward. Muting a channel is a legal, priced choice, not a
settings toggle.

### On work and delegation (the effort economy)

**(2026-07-12)** *"I have never been around unassigned workers before, because there's
always been a backlog."*
→ **Idle staff don't exist; unmanaged staff do.** Work always happens — the question is
*whose ordering of the backlog wins*. Unmanaged researchers drive at their own agendas
(thematically honest: costly humans with their own problems). Management effort steers;
it never creates.

**(2026-07-12)** *"the main thing a team lead does is stop employees from annoying me
with employee things"* and *"Each new employee is kinda cutting down the time I need to
do other things, so I want someone to just take this routine stuff off my hands."*
→ **Staff buy back founder time.** Hires don't add to an AP pool (the pool illusion is
dead) — they reduce the founder-price of routine actions and *absorb interrupt classes*.
A team lead is an interrupt shield with an agenda rider. Denominate manager value in the
response-window economy (ADR-0009), not in output multipliers.

**(2026-07-12)** *"something about how information flows up (Robert Anton Wilson /
Celine's Law might play here in mechanically interesting ways)"*
→ Delegation costs sight: a manager's report is an **inward SA channel with fidelity
loss** (hierarchies produce rosy reports upward — Celine's law as mechanic, not mysticism:
report accuracy degrades with punishment-culture and manager incentives). Skip-level
audits are a founder-time spend to re-ground truth. Folds inward-SA (ADR-0008 deferral)
into existing SA machinery.

**(2026-07-12)** *"successes plus schmoozing in finance leads to better VC offers than
successes plus time at AI safety conferences, which would have in turn led to better
grant applications or higher quality safety applicants"*
→ **Social capital is typed and compounding — the founder currency buys doors, and doors
compound.** Extends "the opening is a commitment device": which rooms you spend founder
hours in locks strategic paths (Hustler vs Operator divergence is literally this).
Early hires are reputation seeds who attract their own juniors.

### On honesty and legibility

**(2026-07-04)** *"I am used to thinking about the game with universal powers as god
mode / admin, whereas the player mostly starts ignorant about the world the same way a
fresh spawn in Tarkov / fresh game of Civilization / entirely fresh run of some
Roguelike."*
→ The architectural sentence of workshop #1: the admin view is not the game; **the game
is the fogged subset.** Simulate everything, gate only the view (ADR-0004).

**(2026-07-04)** *"Ideally the late game will bring with it some forcing of
understanding onto the player as to how they're going to lose (modulo their efforts to
stop it?)"*
→ **The game must explain your death before it kills you.** Doom sources become legible
for free as they become lethal; SA purchases buy *lead time*, not exclusive truth
(ADR-0004). Target loss-feeling: tragedy ("I saw it coming"), never unexplained horror.

**(2026-07-04)** *"I think the doom's waves are emergent. We might lean our thumbs on
the scale at certain points… rival_lab could get a wave of funding at point X."*
→ **Author causes, never outcomes.** The designer's thumb touches inputs to the sim,
never the doom variable (ADR-0005).

**(2026-07-12)** *"Doom Arrives With Your To-Do List Being Infinitely Long Still is a
real possibility that I'm not shy of playing into."*
→ **Attention is the resource the UI must be honest about.** Standing offers expire,
deferred items fall out of visibility, the backlog outgrows the screen — modeled
straight, not hidden (ADR-0012). Losing track is a legal way to lose; the game shows
you an honest backlog, not a complete one.

**(2026-07-12)** *"we should start fundraising and then have the money come in *later*,
so if it goes badly, that means we then need even more emergency measures if the ledger
is coming due soon…. emphasise the spiky-in and smooth-out cash flow management
challenge element of the game."*
→ **Cash is spiky-in, smooth-out — and the most fungible resource.** Debt death must be
tragedy, and tragedy requires foreseeability, which requires lead time on money: the
duration rule (ADR-0009) re-derived independently from the loss-feeling requirement.
The ledger doesn't own a death screen; called-due defaults cascade legibly into the
deaths that exist (ADR-0012).

**(2026-07-12)** *"The simulation won't lie, but maybe our managers will give us rosy
pictures of what's going on. Undiscovered or late discovered errors and doom are a real
world problem because nobody wants to bring the boss bad news…"*
→ Sharpens ADR-0004's honesty line: **the sim never lies; characters do.** Instruments
can be fooled, managers can be scared — deception lives in provenance and personnel,
never in the engine's account of itself. Late-discovered doom via rosy reporting is a
real-world failure mode the game now mirrors (ADR-0011 Celine's-law channels).

### On restraint (as little design as possible)

Demonstrated rather than stated this session — the folds:
- Four issues (loans, funding-with-strings, governance cascade, blackmail) → one Ledger.
- Three issues (Insight System, CRT viewports, opponent discovery) → one SA system.
- Geopolitics → schedule content, not a system. Management depth → ledger riders, not a
  sim. Influence → a ledger column, not a resource. Blackmail → one event genre.
- Working rule: a mechanic that needs a new player-facing currency or panel has to prove
  it can't be a read/write on existing ones first.

### On flavor and theme

**(2026-07-04)** *"there are critical votes coming up, and people are wavering. have you
got them?"* (on the whips in House of Cards)
→ The emotional target for politics: **counterparty dread** — a pledge is not a vote
until cast. Fiction and mechanic are the same object here (ADR-0007).

Tone: the Papers, Please register — conspiracy weirdness lives in the *provenance* of
information (redacted docs, cranks occasionally right, sources who might be plants),
never in the sim lying about itself. Dark comedy over raw grief: "Hypnotised: 2.1B" in
flat CRT type, not casualty counters. Personnel problems read as "bother," not tragedy.

## Open tensions in my own philosophy

- **Despair mitigation vs horror of the unknown**: resolved *for now* by ring-fencing —
  horror inside the run, meaning outside it (loss-ladder, community). Watch it.
- **Teaching-tool fidelity vs patch freshness**: resolved by the structure/numbers line
  (structure never patched for freshness) and seasons-as-scenarios (patches explore the
  real disagreement space instead of nerfing reality). Fragile if season design gets lazy.
- **Founding-location weight vs fast replays**: the early game must carry strategic
  commitment AND be quick to re-play for experienced hands — Civ never solved this; we
  have to. Unresolved; owned by the pacing question (ADR-0008).
- **Wretched survivor vs good steward**: resolved in favor of the survivor
  (lexicographic turns, ADR-0002) — desperate turns at doom 97 pay full value, keeping
  the desperation content load-bearing rather than touristic.

## Change log

- **2026-07-12 (beat 3)** — Workshop #2, ledger bite: infinite-to-do-list honesty,
  spiky-in/smooth-out cash + tragedy-requires-lead-time (under honesty/legibility);
  norm-and-market-setting theory of change marked never-patch (under purpose).
- **2026-07-12 (beat 2)** — Workshop #2, effort allocation: added "On work and
  delegation" (backlog-never-empty, staff-buy-back-time, managers-as-interrupt-shields,
  Celine's-law reports, typed compounding social capital) + dual-use-temptation-is-priced
  under tension/tradeoffs; ladder "coarse hands, fine scoreboard" under losing.
- **2026-07-12** — Workshop #2, beat 1 (turn cadence): added "On the turn (the core
  loop)" — plan-vs-execution tension, selection-attribution, slack-as-gambleable
  insurance, coarsening management grain, SA-buys-response-windows.
- **2026-07-04** — First fill, from Fable workshop #1 (purpose, losing, ledger,
  legibility, restraint, flavor; four tensions logged). Session also produced
  ADR-0002–0008 and amendments to ADR-0001.
