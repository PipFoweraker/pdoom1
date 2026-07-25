# IP / Openness / Monetization / Data-sharing Premortem -- 2026-07-25

> **Status: decisions-FOR-Pip strategy doc. PROPOSED, not ratified.**
>
> **THIS IS NOT LEGAL ADVICE AND NOT TAX/ENTITY ADVICE.** The author is an
> LLM agent, not a lawyer, not a registered tax agent, not an IP attorney in
> any jurisdiction. Every place below where a real license text gets adopted,
> a trademark gets filed, an entity receives grant money, or IP gets assigned
> between entities is flagged `[LAWYER]` -- those are the points where a real
> professional signs off before anything is executed. This doc's job is to
> get the STRATEGY decisions made cold so the professional conversation is
> short and cheap.
>
> Frame (matching SUCCESS_PREMORTEM_2026-07-20.md): it is mid-2027. The game
> found its "30 nerds who play long enough to form a community"
> (DESIGN_PHILOSOPHY target) and maybe a few hundred more. Which IP/openness
> choices made in 2026 turned out to be the expensive ones? Pip's explicit
> steer: worry about the MIDDLE ground, not the tails. Nobody is litigating a
> viral hit; nobody cares about a dead repo. The middle -- mild success, real
> community, a trickle of money, other people building on the work -- is
> where ambiguous licensing and reflexive posturing actually cost.

Grounding (decided things this doc builds ON, not re-decides):

- `docs/PRODUCT_STRATEGY_RATIONALE.md` -- two products, one data backbone;
  the fact/opinion firewall; "the moat is curation, not secret formulas";
  the Path of Exile model; open dataset as NGO credibility.
- `docs/copy/README.md` -- the repo-split SOURCE/PUBLISHER contract.
- `docs/TRIUMVIRATE_METABOLIC_CYCLE.md` -- the 3-repo metabolism (revised in
  this same PR to carry the data-openness ruling in section 6 below).
- `docs/CAPABILITY_UPLIFT_SCAN.md` -- BET 3 (telemetry loop), the Balance
  Observatory.
- `docs/game-design/DESIGN_PHILOSOPHY.md` -- small durable community over
  large audience; patch-as-heartbeat.
- `docs/strategy/SUCCESS_PREMORTEM_2026-07-20.md` -- the attention-armor
  frame; founder-hours as the binding constraint.

---

## 0. Ground truth (verified 2026-07-25)

Checked against the repo and GitHub the day of writing:

1. **The repo is PUBLIC and carries NO license.** `gh repo view` returns
   `"license": null, "visibility": "PUBLIC"`. There is no LICENSE file at
   the repo root (`git ls-files | grep -i licen` finds only
   `godot/addons/godotsteam/license.md` and `godot/addons/gut/LICENSE.md`
   -- third-party addons' own MIT texts).
2. **README.md line 59 claims otherwise:** "**Built with Godot 4.5.1** |
   **Open Source (MIT License)**". A public statement of MIT with no MIT
   text anywhere is the worst of both worlds: it may function as a license
   grant people reasonably relied on `[LAWYER -- whether a README badge
   constitutes a grant is exactly a lawyer question]`, while giving none of
   MIT's actual terms (attribution requirement, warranty disclaimer). This
   is the single most urgent item in this doc -- see section 3.4.
3. `CONTRIBUTING.md` says nothing about licensing of contributions. Every
   outside PR merged so far has ambiguous IP status `[LAWYER]`. At current
   contributor volume (approximately zero external) this is cheap to fix
   and expensive to fix later.
4. The Manifund application draft exists (`docs/copy/MANIFUND_DRAFT.md`);
   Pip's stated likely path is taking Manifund money INTO his for-profit
   company for IP protection + control, with a possible later pivot to a
   fully-nonprofit model (section 9).
5. The strategy doc already rules the big shape: "open the historical
   events data ... keep the game-mechanics integration as the protected
   layer. The ONE thing to actually prevent is a wholesale clone of the
   entire game if it goes viral on Steam."

## 1. The premortem: five ways mid-2027 goes wrong in the middle

- **F1 -- License-vacuum drift.** The public repo keeps accumulating value
  with no license. In 2027 someone forks it, or builds a mod, or reuses the
  event data, and asks "am I allowed?". Any answer given then is improvised
  under social pressure, and the README's MIT badge means the permissive
  interpretation has already been promised. Retracting a promise costs more
  community trust than never making it (the surface-then-retract trap,
  section 4.2, applies to licenses too).
- **F2 -- The sticker-seller.** Someone sells P(Doom) merch / reskins the
  game on itch with the name and logo. Financial damage at Pip's scale:
  tens of dollars. Emotional damage: the exact "ripped off while I did the
  labour" feeling Pip named. The cheap pre-commitment (trademark posture,
  section 3.5) is what makes 2027-Pip shrug instead of seethe.
- **F3 -- Surface-then-retract on data.** Gameplay telemetry gets
  auto-published during dev because the pipeline made it easy; balance
  changes daily so the data is instantly stale and misleading; the tiny
  playerbase means rows are fingerprintable; when it gets pulled, the
  community reads retraction as betrayal. Pip has already ruled against
  this (section 6) -- the premortem's job is to keep the ruling from being
  eroded by pipeline convenience.
- **F4 -- Reflexive greed on a success spike.** A good month (streamer
  pickup, HN post) triggers "lock it all down / charge for everything"
  moves that burn the small durable community the whole design philosophy
  optimizes for. Antidote: the written covenant in section 8.2, adopted
  cold, now.
- **F5 -- Entity-shape lock-in.** Manifund money lands in the for-profit,
  IP ownership is never written down, and the later nonprofit pivot
  requires untangling who owns what with money already spent `[LAWYER]`.
  Cheap now-action in section 9.

Everything below is organized as decisions that close off these failures.

---

## 2. Decision 1 -- Licensing: four separate levers, not one

The load-bearing insight: "the license" is not one decision. CODE, ART and
ASSETS, DATA, and TRADEMARK are four independent levers with different
default legal regimes, different threats, and different costs to Pip. Most
indie licensing pain comes from pulling one lever and assuming it covered
all four.

### 2.1 The lever map

| Lever | What it covers here | Default if silent | Real threat at Pip's scale | Cheapest effective posture |
|---|---|---|---|---|
| CODE | GDScript engine + sim core, Python tooling | All rights reserved (but README badge muddies) `[LAWYER]` | Wholesale Steam clone (strategy doc's ONE thing) | License the ENGINE permissively-or-copyleft, keep it separable from the shipped GAME (open-core split, 2.2) |
| ART / ASSETS | pixellab sprites, generated icons, music, tilesets | All rights reserved | Reskin-clone shipping YOUR art | Do NOT open-license; "all rights reserved, mod-use permitted" written policy |
| DATA | pdoom-data facts; godot/data balance JSON | Facts largely uncopyrightable in US; database rights differ by jurisdiction (EU sui generis; AU follows copyright-in-compilation case law) `[LAWYER]` | None worth money; the WIN is people using it | CC-BY 4.0 (or ODC-BY) on pdoom-data; balance JSON rides the code license |
| TRADEMARK | "P(Doom)1" name, logo | Unregistered marks get thin passing-off protection only `[LAWYER]` | The sticker-seller; a confusing clone using the NAME | The one lever worth actual money (2.4) |

### 2.2 Code options, priced at Pip's scale (few $k/yr ceiling)

- **Permissive (MIT/Apache-2.0).** Buys: maximum "build things off my
  labour" (Pip's stated want (c)); zero friction for community tools.
  Costs: a Steam clone is fully legal, including of the shipped game, if
  the whole repo is MIT -- this is the one outcome the strategy doc says to
  prevent. Verdict: right for the ENGINE, wrong for the whole repo.
- **Copyleft (GPLv3/AGPL).** Buys: clones must open their source (most
  commercial cloners just walk away); community forks stay open. Costs:
  approximately nothing at this scale -- the "GPL scares business" concern
  is a big-company problem. Key evidence that copyleft does not kill
  indie revenue: **Mindustry** (GPLv3, source free on GitHub, sells on
  Steam) and **Shattered Pixel Dungeon** (GPLv3, sells on Google
  Play/Steam) both sustain exactly the few-$k-to-modest-living band by
  charging for CONVENIENCE (builds, updates, workshop, leaderboards) while
  the source sits open [confidence: high, well-known projects; verify
  current terms before citing publicly].
- **Open-core split.** Engine/sim (deterministic core, the genuinely
  reusable thing) under an open license; game-layer (content integration,
  balance opinion, art) under a restrictive one. Buys: want (c) served
  precisely where Pip wants to serve it; the anti-clone layer is the layer
  the strategy doc already calls the moat. Costs: a repo-boundary
  discipline tax (the triumvirate split already practices this muscle).
- **Source-available (BSL-style: "converts to open license after N years",
  or PolyForm Noncommercial).** Buys: readable + moddable now, no
  commercial clones, automatic future openness. Costs: NOT open source by
  OSI definition -- the README badge would still be a lie; some community
  goodwill discount; more exotic license = more explaining. Verdict: a
  reasonable MODERATE posture for the game-layer specifically.
- **Dual-license.** Irrelevant at this scale -- dual-licensing pays when
  businesses want to buy out of copyleft; no such buyer exists here.

### 2.3 The three postures

- **MINIMAL (do this week, near-zero cost):** Delete or amend the README
  MIT badge to match reality; add a root `LICENSE.md` that says, honestly:
  "Source-available for reading, learning, and modding. No license is
  granted yet to redistribute the game or ship derivative games; a real
  license split (engine vs game vs assets vs data) is planned -- see
  docs/strategy/IP_AND_OPENNESS_PREMORTEM.md." Plus one CONTRIBUTING.md
  line: contributions are licensed to the project under the project's
  eventual license `[LAWYER for exact wording -- this is a lightweight
  inbound-license clause, not a CLA]`. This closes F1 without committing
  to anything.
- **MODERATE (decide by ~v1.0):** Execute the open-core split. Engine/sim
  core -> MIT or GPLv3 (Pip's taste: MIT maximizes want (c), GPL maximizes
  anti-clone; at this scale my recommendation is **GPLv3 for the engine**
  -- it still lets everyone build and mod, and it is the cheapest real
  anti-wholesale-clone device that requires zero enforcement budget
  [INFERRED from the Mindustry/SPD precedent]). Game content + art: all
  rights reserved with a short written MOD POLICY ("mods, tools,
  datamining, videos: yes, encouraged; redistributing the game or assets:
  no"). pdoom-data: CC-BY 4.0 (section 7). `[LAWYER before any license
  text ships]`
- **AMBITIOUS (only if the platform/B2B leg materializes):** Formal IP
  assignment into the entity, registered trademarks in AU + US, per-repo
  license audit, partner data-feed contracts. Not worth starting until a
  B2B conversation is real.

### 2.4 Trademark -- the cheapest real protection against sticker-sellers

Copyright does nothing against someone selling "P(Doom) stickers" with a
self-drawn logo; trademark is the lever built for exactly that. Mechanics,
priced [figures from memory, verify current fees before filing]:

- AU: IP Australia registration runs roughly AU$250-400 per class
  (TM Headstart pre-check slightly more). Relevant classes: 9 (downloadable
  games), 41 (entertainment services), maybe 16/25 (printed matter/apparel)
  if merch is real.
- US: USPTO TEAS roughly US$250-350 per class.
- An UNREGISTERED mark still gets passing-off / consumer-protection
  protection in AU and common-law trademark in the US -- weaker, but not
  nothing, and it costs $0 `[LAWYER]`.

Posture recommendation: **do not file yet.** At few-$k/yr scale, the
registered mark buys a cease-and-desist letterhead for a threat that
costs tens of dollars. Instead: (a) date-stamped evidence of use (the
site, releases, this repo's history -- already exists), (b) a one-line
public brand policy ("the name and logo are not open; ask first"), and
(c) a pre-decided tripwire: **file in AU the month merch revenue or a
confusing clone actually appears** -- filing after a specific threat
materializes is only mildly worse than filing before, and infinitely
better than deciding under emotional load. The failure F2 is mostly an
EMOTIONAL injury; the covenant to consult section 8.2 before reacting is
the true mitigation. `[LAWYER before filing or sending anything that
smells like a legal threat]`

---

## 3. Decision 2 -- The Path of Exile model, examined before adopted

The strategy doc already names "the Path of Exile model: make core
mechanics discoverable but not trivially cloneable, and let players build
solver tools." Worth unpacking what GGG actually did, what it bought and
cost them, and what transfers to a solo dev at 1/100,000th the scale.
[All game-industry claims below are from general knowledge, not fresh
research; confidence tags inline; verify before quoting publicly.]

### 3.1 What GGG actually does [confidence: high on shape, medium on details]

- Ships a client whose data files (GGPK) the community datamines within
  hours of every patch; GGG has never seriously fought this.
- Publishes OFFICIAL APIs for trade and ladders -- the SOCIAL data -- while
  keeping drop weights and internal numbers unpublished.
- **Path of Building**, the build-solver the strategy doc alludes to, was
  built by a community member (Openarl), later maintained as the
  open-source PoB Community fork. GGG neither built nor blessed it
  initially; they simply did not kill it. It became infrastructure that
  sells the game (theorycrafting IS the endgame for many players).
- The costs, in the observable record: recurring community rage cycles
  when hidden numbers are discovered to be worse than assumed (loot/drop
  controversies where GGG eventually disclosed hidden mechanics under
  pressure [confidence: medium on specifics]); developer harassment during
  nerf cycles; a playerbase that now treats every undisclosed number as
  presumptively hostile. Once a community norm of disclosure exists,
  each NON-disclosure is read as concealment.

### 3.2 The surface-then-retract trap (the transferable warning)

The pattern that transfers directly: **information you publish becomes an
entitlement; withdrawing it costs more trust than never publishing it.**
GGG-scale example: publish a stat, later hide it, community assumes the
worst. Pip-scale example: auto-publish run telemetry during dev, pull it
when fingerprinting or misreading becomes a problem, and the 30-nerd
community -- whose whole culture is data-argumentation -- reads it as the
project going closed. This is the strongest argument FOR the section 6
ruling: do not start publishing until the publishing posture can be
permanent.

### 3.3 Other comparables, one line each of what transfers

- **Factorio (Wube):** closed source, but a STABLE modding API + mod
  portal + relentlessly transparent dev blog (FFF). Lesson: openness of
  PROCESS and INTERFACES substitutes almost fully for openness of source.
  The patch-as-heartbeat principle is already FFF-shaped.
- **RimWorld (Ludeon):** closed source; mods work by runtime patching;
  EULA simply permits it. Lesson: a one-paragraph written mod policy is
  enough legal scaffolding for a thriving mod scene.
- **Minecraft (Mojang):** shipped obfuscated, community deobfuscated
  anyway for a decade, Mojang eventually published official mappings.
  Lesson: obfuscation against a motivated community only decides WHO
  makes the tools, not WHETHER.
- **Dwarf Fortress (Bay 12):** closed source, free for 16 years, then the
  Steam release monetized CONVENIENCE + PRESENTATION on top of the same
  free game. Lesson: the moat was always the accumulated labour and
  curation -- nobody clones DF because nobody can clone the 20 years.
  This is the strongest version of Pip's own "moat is curation" thesis.
- **Mindustry / Shattered Pixel Dungeon:** fully GPL, still get paid
  (section 2.2). Lesson: at indie scale, people pay for convenience and
  to support the author, not for exclusion.
- **id Software (Doom/Quake):** GPL'd engines years after release; the
  source releases created source ports, longevity, and goodwill without
  cannibalizing anything. Lesson for the AMBITIOUS tier: time-delayed
  openness is a proven move (BSL is the contractual version of it).

### 3.4 The extracted strategy for P(Doom)1

1. Treat dataminers as the community-tools wing, never as adversaries
   (they arrive within days of any real community forming; the design
   already assumes this).
2. Publish INTERFACES deliberately (run-artifact schema, replay format,
   ladder API) -- that is where a PoB-analogue would grow from -- while
   never promising to publish internal NUMBERS on a schedule.
3. Never publish a number you are not prepared to publish forever.
4. Openness of process (dev blog, patch notes, design docs -- all already
   public in this repo) is the Factorio move and is already being made;
   count it as openness spend before adding data-openness spend.

---

## 4. Decision 3 -- Easter eggs and dev-tool posture in an open build

### 4.1 What is actually hideable in a Godot client: approximately nothing

Honest technical baseline: Godot packs the entire `godot/` tree into the
`.pck` (already a known trap, CLAUDE.md), and community tooling (gdsdecomp
/ Godot RE Tools) reconstructs a near-complete project -- including
GDScript close to source form -- from any shipped build [confidence: high].
PCK encryption exists but the key must live in the binary, so it is
extractable by anyone determined; it raises the effort floor from "minutes"
to "an afternoon", once, for one person who then posts the result. The
strategy doc's posture already accepts this ("fully expects and welcomes
the community reverse-engineering balance"). So the design question is
never "can hardcore players be stopped" -- they cannot -- it is "what
keeps surprises alive for REGULAR players after the hardcore have
datamined everything."

### 4.2 The toolkit, ranked by what actually survives datamining

1. **Not-yet-shipped content (the only true secrecy).** Content delivered
   in a later patch cannot be datamined from the current build. The
   monthly Epoch train is a NATURAL late-delivery channel: an easter egg
   that ships IN the epoch patch it activates in is secret right up to
   patch day. Cost: zero new infrastructure. This should carry most of
   the load.
2. **Server-delivered payloads.** A tiny remote blob (the leaderboard
   phone-home path already exists) fetched at a date/condition. True
   secrecy until served, then instantly public. Worth it only for a
   marquee surprise; adds an availability dependency to an otherwise
   offline game -- use sparingly, never for anything load-bearing.
3. **Hash commitments (the fun one for this audience).** Ship a SHA-256
   of the secret content now; ship the content later. Dataminers find
   the hash, KNOW something is coming, cannot know what -- which converts
   datamining energy into anticipation instead of spoilers, and proves
   non-retcon when revealed. Extremely cheap; on-brand for an
   AI-safety-nerd audience.
4. **Seed/condition-gated experiential content.** Content whose data is
   visible but whose MEANING only lands in play (a specific seed's event
   confluence, an ending variant conditional on a rare state). Dataminers
   publish "there is a secret ending"; regular players still get the
   experience fresh. This is spoiler-RESISTANT design rather than
   secrecy, and it is the only kind that survives a wiki.
5. **Mild obfuscation of dev tools.** Shipping dev/debug tooling
   compiled-out or flag-gated (the existing dev-mode pattern) keeps
   regular players from stumbling into the machinery; assume hardcore
   players will find and even use it -- that is free QA, not a breach.

### 4.3 The posture in one line

Secrecy budget goes to TIMING (late delivery via the Epoch train +
occasional server blob + hash teasers); surprise budget goes to DESIGN
(experiential, seed-gated content that a wiki spoiler cannot actually
spoil); zero budget goes to fighting dataminers.

---

## 5. Decision 4 -- Data openness: the ruling and its seeds

Pip's live steer, now written down (and folded into
`docs/TRIUMVIRATE_METABOLIC_CYCLE.md` as "Data-openness posture"):

1. **No auto-publishing of gameplay metadata while in dev.** Three
   reasons, each sufficient: balance changes daily so published data is
   instantly stale and misleads; the playerbase is small enough that run
   rows (seed + version + events_fired) are FINGERPRINTABLE (already
   flagged as Risk 3 in the metabolic-cycle doc); and the
   surface-then-retract trap (3.2) -- publishing now creates an
   entitlement that dev-phase reality cannot honor.
2. **The downward flow (pdoom-data -> game) runs at full speed** -- the
   world-update packs are unaffected; that data is already public facts.
3. **The return leg carries only confirmations + error-correction for
   now:** bug reports (#800 honest-transmit), install ping (#799),
   crash/error artifacts, "pack event X displayed wrongly" corrections.
   Run summaries still flow home under the same consent -- but into a
   PRIVATE lake, not the public one.
4. **pdoom1 accumulates the private lake slowly.** Broad publishing of
   aggregate play data is DEFERRED to ~1.0, when the sim has real
   strategic depth and the numbers mean something durable.
5. **The meta-display / ladder-analytics layer is HOPED to emerge from
   the community** (the PoB pattern: the best solver was built by a
   player), not pushed from the center.

### Seeds to lay now (enable later openness without committing to it)

- **Stabilize and document the run-artifact SCHEMA** (the fields already
  exist deterministically: seed, version, turns, outcome, death
  attribution, replay hash -- ADR-0006). A community tool needs the
  INTERFACE, not Pip's data.
- **Version every payload** so a future published corpus can exclude
  pre-1.0 noise cleanly.
- **Write the consent line NOW to permit later aggregate publication**
  ("anonymized run data may be published in aggregate form in future") so
  ~1.0 publishing does not require re-consent from years of players
  `[LAWYER for the actual privacy-policy wording; AU Privacy Act
  applicability at this scale is exactly a verify-with-professional item]`.
- **Local export:** let a player dump their OWN runs to a file. Voluntary
  player sharing (players posting their runs to a community tool) gets a
  PoB-pattern ecosystem started without Pip publishing anything --
  openness by player choice is immune to the retract trap.
- **Keep the private lake tidy from day one** (schema-validated on
  arrival) so the ~1.0 publishing decision is a switch, not a cleanup
  project.

---

## 6. Decision 5 -- What to give away most easily

Candidates, per the task and the strategy doc: pdoom-data (the curated
public dataset) and/or the engine.

- **pdoom-data: give it away NOW, fully.** It is already public-by-design
  (NGO credibility, research value, the fact/opinion firewall makes it
  safe). Recommended license: **CC-BY 4.0** (attribution keeps the
  curation labour visible -- the one currency that matters at this scale)
  or ODC-BY if a data-specific text is preferred. Note: bare facts are
  largely uncopyrightable in the US and AU protection of compilations is
  case-law-dependent, so the license here mostly functions as a NORM
  statement, not a wall -- which is fine, norms are what this community
  runs on `[LAWYER if the B2B data-feed product ever charges for the same
  data]`. CC0 is the maximally-generous alternative; rejected here only
  because attribution is the mechanism by which the dataset builds the
  NGO's name.
- **The engine: second, and later.** The deterministic sim core is the
  genuinely reusable artifact for want (c) ("let people make their own
  games off my labour"). Give it away at the MODERATE tier (section 2.3)
  under GPLv3 -- open enough for anyone to build on, copyleft enough that
  a wholesale commercial clone must open its own source. Timing: after
  the open-core repo split exists; giving away the engine today means
  giving away the whole repo, art and balance opinion included, which is
  the one thing the strategy doc rules out.
- **Never in the giveaway pile:** the art/assets, the balance-shaping
  opinion layer, the name/logo, and the private telemetry lake.

Recommendation in one line: **data first (now, CC-BY), engine second (at
the repo split, GPLv3), art/name never** -- generosity concentrated
exactly where the strategy doc says the moat is not.

---

## 7. Worked dollars at Pip's scale + the anti-greed guardrail

### 7.1 The honest numbers [all illustrative, order-of-magnitude]

- Steam at the target community size: 300-1,000 sales x US$10 x ~65%
  after Valve/VAT = roughly **US$2k-6.5k, mostly one-time** -- squarely
  Pip's own "few $k/year at most".
- Merch: at 30-300 engaged players, stickers/shirts are
  **tens-to-hundreds of dollars a year**. A rogue sticker-seller
  therefore costs single-digit dollars of displaced revenue; the injury
  is dignity, not money -- which is why the mitigation (2.4) is a
  pre-decided tripwire + covenant, not upfront legal spend.
- B2B platform leg: $0 until it isn't; ignore in all 2026 decisions
  except keeping the data backbone clean (already ruled).
- Against the FATFire frame: the ENTIRE realistic game revenue is noise
  relative to the established ceiling. The money's real function, per
  Pip: **a success funds the OTHER art/creative projects in the
  business.** That framing is itself the anti-greed device -- the game
  never needs to be squeezed, because it was never the retirement plan.

### 7.2 The "don't get reflexively greedy" guardrail, made mechanical

Failure F4 is a decision made HOT. The fix is the same attention-armor
move as the success premortem: decide cold, write it down, and make
future-Pip's job "follow the written policy" instead of "resist
temptation." Proposed covenant (adopt by merging; amend only by PR, never
in the week of a success spike):

1. No license on any already-shipped version ever gets more restrictive
   retroactively. (Relicensing FORWARD is allowed; clawing back is not.)
2. Anything published (data, schema, API) stays published; see 3.2.
3. Community tools, mods, videos, datamining: always permitted, never
   monetized against.
4. Any monetization change (price, DLC, merch, data products) waits a
   **two-week cooling period** from the triggering event, and gets checked
   against this doc first.
5. The game's revenue purpose is fixed: fund the other creative work.
   Any plan that only makes sense if the game becomes the main income is
   out of scope by definition.

---

## 8. The entity question (Manifund -> for-profit, possible nonprofit pivot)

`[LAWYER + ACCOUNTANT -- this whole section is flags, not advice. Grant
money into a for-profit, IP assignment between entities, and any later
for-profit -> nonprofit conversion have real tax and charity-law
consequences in AU that an LLM must not be the last word on.]`

The premortem risk (F5) is not the choice itself -- taking Manifund money
into the for-profit for IP protection + control is a coherent, common
choice -- it is the UNDOCUMENTED state: money in one entity, IP created
across personal/company boundaries, and a pivot later that has to
archaeologize who owns what.

Cheap now-actions that keep BOTH doors open:

1. **Write down, today, which entity owns what** (one page: code
   copyright, art, the name, the domains, the data curation). Unwritten
   IP ownership defaults are jurisdiction- and employment-status-
   dependent and messy `[LAWYER]`.
2. **Keep the grant's purpose paper-trail clean** (what the Manifund
   money is FOR, spent from a separable account) -- this is what makes a
   later nonprofit pivot auditable instead of forensic
   `[ACCOUNTANT/registered tax agent -- explicitly out of scope for this
   doc]`.
3. **Prefer licenses over transfers while undecided:** if the nonprofit
   pivot is live-possible, the for-profit LICENSING the IP (to itself, to
   a future NGO) is more reversible than assigning it `[LAWYER]`.
4. Note the alignment: the section 2.3 MODERATE posture (open engine +
   open data, reserved game layer) reads WELL in either entity shape --
   open artifacts are exactly what an NGO wants to point at, and the
   reserved game layer is exactly what a for-profit wants to hold. The
   licensing strategy does not force the entity decision. [INFERRED]

---

## 9. Decision summary for Pip

| # | Decision | MINIMAL (now) | MODERATE (by ~1.0) | Flag |
|---|---|---|---|---|
| 1 | Code license | Fix README/LICENSE contradiction with honest source-available placeholder + CONTRIBUTING line | Open-core split: engine GPLv3, game layer reserved + written mod policy | `[LAWYER]` before any text ships |
| 2 | Trademark | $0: brand-policy line + evidence of use + written tripwire | File AU class 9/41 the month merch or a confusing clone is real | `[LAWYER]` before filing/threatening |
| 3 | PoE model | Publish interfaces not numbers; never publish what can't stay published | Stable run-artifact schema + ladder API as the community-tool substrate | -- |
| 4 | Easter eggs | Epoch-train late delivery + seed-gated experiential design | Hash commitments; rare server blob for marquee moments | -- |
| 5 | Data openness | Ruling adopted: confirmations/error-correction up only; private lake; consent line written for future aggregate publishing | ~1.0: publish aggregates; hope the PoB-pattern tool emerges | `[LAWYER]` privacy wording |
| 6 | Giveaways | pdoom-data -> CC-BY 4.0 now | Engine -> GPLv3 at repo split; art/name never | `[LAWYER]` if B2B charges for same data |
| 7 | Anti-greed | Adopt the section 7.2 covenant by merging this doc | Re-read it during any success spike, before acting | -- |
| 8 | Entity | One-page IP ownership inventory; clean grant paper-trail | License-don't-assign while the nonprofit door is open | `[LAWYER + ACCOUNTANT]` -- the load-bearing flag of this doc |

**The single most important professional-boundary flag:** the Manifund
money -> for-profit -> possible nonprofit pivot chain (section 8). License
files can be fixed with a PR; entity and grant-money structure, done
wrong, is the one item here that compounds into real legal/tax cost and
cannot be repaired by editing a file. Get a lawyer and a registered tax
agent on that one before the money moves.

---

*Drafted 2026-07-25 by a strategy lane. Repo-state claims (public
visibility, null license, README line 59, CONTRIBUTING silence) verified
same day via gh + git. Game-industry comparables are from general
knowledge with inline confidence tags -- verify before quoting publicly.
PROPOSED; Pip amends and ratifies by merge.*
