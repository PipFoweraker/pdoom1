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

**(2026-07-13, workshop #3)** *"i'm considering making the leagues and associated patches
that long as well - that means I can run the game a month behind real time, update real
world events into the engine, balance patch, test, and deploy in a way that doesn't
demand my full-time attention."*
→ **League metabolism: the game trails reality by one month** — RESOLVED same session
(ADR-0016). Reality becomes the map generator — each league, another month of the real
race enters the seed timeline. The two collisions ruled: 2017 run-start holds (fixed
history is the shared macro map; present-month jump-in parked as experiment), and
cadences decouple — monthly world-updates ("mild lore and sprint refresh") vs slower,
legible-event-grade balance patches, preserving the patch-as-heartbeat principle.

**(2026-07-13, workshop #3)** *"I feel like this is 75% of the way towards canon, I am
happy for it being baked fairly deeply into config. Otherwise I drift away from the
guiding star of this having some utility as something like a tool / scenario builder /
argument fosterer."*
→ **The reality-tether is what keeps the game an argument-fosterer.** League metabolism
ruled ~75%-canon, baked deep into config: without the tether, the game drifts from
scenario-builder toward pure fiction.

**(2026-07-13, workshop #3)** *"they could also share that seed with others, so really
the number is infinite, just one will be promoted by default. This also kind of implies
players can host mini-leagues by posting a baseline seed. Intersting [interesting]."*
→ **A league is just a promoted seed; anyone can host one.** League baseline = one seed
(possibly one seed with a few variants — the elegant home for a future present-month
mode). Community structure falls out of seed-sharing; no new infrastructure.

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

**(2026-07-13, workshop #3)** *"there are so many environmental forces that the player
can't really influence in any given game that the background of Doom is nearly always
going to be trending up, and only at the end of long chains of effort can the player's
impacts *directly or strongly* reduce Doom - in most measures, the player is going to be
needing to trade off increasingly sacred objects / values / projects to try and get
things over the line as Doom pushes higher."*
→ **Doom is a rate (~75% ruling), the background always climbing; direct reduction lives
only at the end of long chains, priced in sacred objects.** Tension-through-sacrifice
extended to the doom variable itself. A 2017 spawn starts lower and builds slower than
current balance — the steady build *is* the early grind.

**(2026-07-13, workshop #3)** *"in the early game, the rivals will be mostly
concentrating on developing their *own* positions, and then as a player starts to
threaten their interests … active attacks (litigation, funding cuts, reputational
attacks, scathing reviews of our works, psyops, aggressive hiring, leak seeking, etc)
will emerge as a sign we're entering what I'm starting to think of as the midgame."*
→ **The midgame begins when the world starts shooting back.** Aggro-threshold design
(XCOM:EU anti-grind, Factorio pollution/biters): rival attention keys to the *visibility
of the player's impacts*, not the calendar. Difficulty ratchet: the rival's compounding
headstart should stack up "frustrating, legible, and don't feel like the game is
cheating you *that* much." ADR-candidate — mechanism owed (DQ-22).

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

### On the early game (scouting and the populating board)

**(2026-07-13)** *"I was thinking about the early stage phases of games like Civ and
Factorio that provide replayability to even veteran players and a lot of it seems to come
down to scouting / information-gathering."*
→ **The early game's replayability engine is scouting.** What keeps veterans replaying an
opening isn't new content — it's re-gathering information about *this* seed. Aligns SA
(ADR-0001/0004) with the opening-as-commitment-device: the first moves are scouting moves.

**(2026-07-13)** *"[the pre-Godot version] was very hard and very punishing and kept
players in the dark and with a bad UI that they had to pay to unlock even slightly
unpunishing things like a scrolling event log … there was more emphasis on exploring and
trying to forge connections at the start."*
→ Pip's prior build already had the shape: **sight and even UI comfort were things you
paid for** (spending-buys-sight, ADR-0001), and the start was exploration-and-connection
heavy. The instinct to recover: front-load *forging connections*, not just spending.

**(2026-07-13)** *"I wonder if we can bring information to players more over time as …
researchers discover papers or add to situational awareness / highlight things to the
player's attention such that the 'game board' starts to get populated over time — maybe
actions like 'go read' or 'go to meetups' or 'shitpost online'."*
→ **The board populates over time.** Fog doesn't lift by a single purchase; it fills in as
staff and actions surface it — a live expression of simulate-everything/gate-the-view
(ADR-0004). "Go read / go to meetups / shitpost online" are scouting actions in different
SA channels (research/presence/media, ADR-0014).

**(2026-07-13)** *"[the Civ moment] settler → city + local barbarians → deal with them →
meet either city-state or rival Civ — this establishes early relationship … go explore and
try to find hires (the hiring process will take longer and feel more committed, I want to
get people attached to their hires like recruits in 2012 X-COM), and those hires then
bring you information if you yourself stop scouting as actively? things 'come across your
desk'."*
→ **Hiring is a scouting relationship, and delegation is how scouting scales.** Early hires
are found by exploring (slow, committed, emotionally sticky — the XCOM-recruit attachment
target); once hired, they *become* your scouts — information "comes across your desk"
when you stop scouting personally. This is ADR-0011's staff-as-SA-channels (Celine's-law
reporting) meeting ADR-0009's action durations: hiring takes real time and bills real
commitment. Candidate for a dedicated early-game/scouting beat next workshop.

**(2026-07-13, workshop #3)** *"I also like the early game of SC2 where you are trading
scouting for information vs the extra resources your workers could get leaving you blind
but better mined - that tension is interesting."*
→ **Scouting is priced in opportunity cost.** Every founder-hour spent looking is one not
spent mining. And [interviewer's sharpening, Pip to confirm] the SC2 citation carries a
second answer: SC2 maps are *known* — scouting there reads the opponent's build on a fixed
map, and the map pool rotates per season. P(Doom) scouting reads the **micro layer**
(actor postures, the hire pool, the local social scene) on a **known macro map** (real
history + this league's patch); league rotation is the freshness engine.

**(2026-07-13, workshop #3)** *"It might be that the players and entities in the game you
encounter you can start building relationships with sooner than if you encounter them
later - perhaps relevant?"*
→ **Early contact compounds.** Scouting's payoff is denominated in relationship-time
(typed compounding social capital, applied to the opening): meeting an actor at month 3
vs month 20 changes the whole integral of that relationship.

**(2026-07-13, workshop #3)** *"I don't mind factorio-mode for re-optimising known
openings - I figure players will start to evolve stable target goals as the game goes
through its phase shigts [shifts]."*
→ **Factorio-mode accepted at the macro grain.** Veteran freshness comes from meta churn
(leagues/patches) and micro-social variance, not per-seed world regeneration.
Scouting-as-every-run-content survives at the micro layer only.

**(2026-07-13, workshop #3)** *"Info was happening at me as spawn without me having opted
into that much information … If they were pieces of a board lighting up or moving around,
fine, but the acknowledgment-response requirement was too strong."*
→ **The scarce channel is acknowledgment, not information.** Ambient board mutation can
run at high rate without spam-feel; *decision demands* are what flood. Three intrusiveness
tiers: ambient change < readable feed < response window (ADR-0009/0012 machinery).
Subscribing to a channel (scouting is subscribing) is opting into its demands; the only
unsolicited demand floor is ADR-0004's lethality rule — the world may only shout uninvited
about what is becoming lethal.

**(2026-07-13, workshop #3)** *"I want my minions to bring me information! good minions!"*
→ **Provenance, personified.** The same fact lands differently from a named hire than from
a ticker. Wherever a character plausibly owns a piece of information, deliver it through
them.

**(2026-07-13, workshop #3)** *"Default civilian awareness for a WEIRD nation / mid-sized
city / moderately techy person of the civilizational meta at the time."*
→ **The ambient floor is civilian awareness.** Pre-scouting, the feed carries only what a
moderately techy 2017 civilian would passively absorb — a small floor of world-noise, not
silence. The quiet opening is intended; the floor exists for aliveness, not information.

**(2026-07-13, workshop #3)** *"Stumbling onto LessWrong feels like a significant unlock
of this part of the scouting tree."*
→ **Scouting actions v1, sketched:** *go read* — near-free internet browsing with
discovery unlocks (LessWrong as a significant one); *go to meetups* — effort-priced,
meet people at random; bigger meetups in other cities seed local first-connections
faster, building **regional influence**; *shitpost online* — low effort, low rep, high
variance networking. All deliberately capital-preserving: the things you do when
protecting cash flow in the very early game.

### On the hero and the office

**(2026-07-13, workshop #3)** *"we don't power up the player, we power up the office?"*
(context: *"the player is the heroic focus point of a lot of stuff (and blame when things
go wrong!) that is nonetheless going to battle superhuman forces (some of them spooky) to
save the world, the cat, and keep the receipts along the way"*)
→ **Progression lives in the org, not the hero's stats.** Character creation (starting
connections, founder background — surface owed, not yet designed) customizes the *start*;
the run grows the *office*. When staff scout, their lane preferences and skillsets filter
what's surfaced (*"If I assign a staff member to scout, their preference sets and
skillsets come into play, otherwise it's the player's, who we will generally expect to be
pretty strong"*); the founder is a strong generalist lens. Who you send determines what
you see — ADR-0004's channels-with-provenance, personified.

**(2026-07-13, workshop #3)** *"Do we tie them into making *decisions*, and everyone else
taking *actions*? Decisions imply draining something like mana or willpower, and this
implies poor decisions if you're cramming, although this is speculation."*
→ **The founder spends decisions; staff spend actions** (Pip's speculation flag
preserved on the willpower-drain/cramming-degradation half). Grain accepted: ~1
meaningful decision/day ≈ 5/week ≈ 20-and-a-bit/month, with **admin as painful
overhead** ("Admin is painful in this game, I want that to be part of the overhead").
**The founder currency is named `Attention`** (ruled 2026-07-13): Pip's own canon
already held "attention is the resource the UI must be honest about"; "I don't have the
attention for this" is the founder experience being modeled; and the game spawns in
2017 — the year of "Attention Is All You Need." The joke is load-bearing.

**(2026-07-13, workshop #3)** *"I suffer most when a 4-year hire walks in year 5, and
then 4 of her 6 team leaves as their morale craters the following few months when I can't
promote someone good in and have to gamble on an outside manager as an emergency hire."*
(and: *"tension through sacrifice"*)
→ **Attachment is built to be spent.** Slow committed hiring is the attachment generator
(XCOM-recruit target); every deepening — project leadership, promotion, years served —
raises the price of the loss vectors (departure cascades, forced loyalty-vs-performance
firings, spooky removals: abduction / brainwashed / wireheaded / cultist-ed; design
boundary: nobody grossly murdered). Cascades stay event/ledger riders, not a mood sim
(ADR-0011 register: "bother," escalating to tragedy only at the top end).

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

**(2026-07-13, workshop #3)** *"hardcoding doom counters into things seems really like a
legacy design philosophy and as we get sophisticated things should defer to, like, having
impacts on things that have impacts on doom so we move more towards downstream effects
rather than single source-destination number bumps."*
→ **No printed doom deltas** (ADR-0015 candidate): extends "author causes, never
outcomes" from designer discipline to *schema* discipline — actions and events touch
world state; only world state touches doom. Guard: indirection must never break
loss-legibility; the L6 attribution chain is the counterpart instrument (the
death-attribution artifact showed accounting breaks exactly where causality goes
indirect).

**(2026-07-13, workshop #3, #634 veto round)** *"the game notes strongly for debugging
and logging purposes any turn where Doom is not a positive rate AND a significant event
('sacred object' in design parlance…) is not happening (this allows for occasional
downward spikes in doom if a player pulls something impressive off)"*
→ **The doom floor is an instrument, not a clamp.** Doom rate may legally go negative;
what's enforced is *legibility of the fall* — any net-negative turn without a
sacred-object-grade cause gets loudly flagged in telemetry. Same falsifiable-invariant
pattern as the decision-flip rate: balance assumptions become alerts, never engine rules.

**(2026-07-13, workshop #3, #634 veto round)** *"we can have the satisfaction of watching
something like the *delta Doom* rise and fall in response to our observed outputs, and
then the actual, accumulated Doom can steadily grind upwards with much subtler gradients
over time, so the player has (or, better yet, can *earn*) tighter feedback loops."*
→ **Two instruments: the rate wiggles, the level grinds.** The delta-doom display gives
high-frequency agency feedback (waves and falls responding to your outputs); accumulated
doom keeps the structural dread (destined to rise). The tighter loop is *earned* —
instrumentation as progression (power-up-the-office; the pre-Godot paid-for event log's
direct descendant). Guard: ADR-0004's lead-time rule owns the free layer — the coarse
doom band and becoming-lethal warnings are never paywalled; what's earned is *resolution*
(stream decomposition, pulse forecasting), not survival-critical sight.

### On restraint (as little design as possible)

Demonstrated rather than stated this session — the folds:
- Four issues (loans, funding-with-strings, governance cascade, blackmail) → one Ledger.
- Three issues (Insight System, CRT viewports, opponent discovery) → one SA system.
- Geopolitics → schedule content, not a system. Management depth → ledger riders, not a
  sim. Influence → a ledger column, not a resource. Blackmail → one event genre.
- Working rule: a mechanic that needs a new player-facing currency or panel has to prove
  it can't be a read/write on existing ones first.

**(2026-07-13, workshop #3, #634 veto round)** *"I might be able to solve this at the
cards-level, not the stack-level, to use a M:TG analogy."*
→ **Weirdness lives in cards, not the stack.** Engine rules stay crisp (e.g. no standing
player lever governs `global_compute`); edge cases (an autocratic state cracking down on
PC-grade general compute) enter as content — events on the seed schedule. Same generator
as "geopolitics is content, not a system," now stated as a general division of labor.

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

- **2026-07-13 (workshop #3, beat 3 — #634 veto round)** — doom floor as instrument-not-
  clamp (unexplained falls logged, not prevented); "weirdness lives in cards, not the
  stack" (under restraint); doom function restructured toward named component streams
  (round-2 strawman on PR #634).
- **2026-07-13 (workshop #3, beat 2 — handover round)** — Doom-as-rate + sacred-objects
  reduction; aggro-threshold midgame ("the world starts shooting back", DQ-22); ambient
  floor = civilian awareness; scouting actions v1 sketch (LessWrong unlock); decisions
  (founder) vs actions (staff) + willpower speculation; league = promoted seed /
  mini-league hosting; reality-tether ~75% canon ("argument fosterer" guiding star).
- **2026-07-13 (workshop #3, beat 1)** — Scouting/early-game interview: SC2-mode scouting
  (known macro map, micro-layer variance), league-metabolism candidate (game trails
  reality by a month — UNRESOLVED), acknowledgment-scarcity spam rule, provenance
  personified, new "On the hero and the office" section ("power up the office",
  attachment-is-built-to-be-spent), no-printed-doom-deltas (ADR-0015 candidate).
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
