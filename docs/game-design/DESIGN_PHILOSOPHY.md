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

- **2026-07-04** — First fill, from Fable workshop #1 (purpose, losing, ledger,
  legibility, restraint, flavor; four tensions logged). Session also produced
  ADR-0002–0008 and amendments to ADR-0001.
