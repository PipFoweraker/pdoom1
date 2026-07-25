# The Triumvirate Metabolic Cycle -- pdoom-data -> pdoom1 -> pdoom1-website

**Status: PROPOSED (2026-07-25). NOT ratified.** This is a decisions-FOR-Pip
proposal for how the three repos turn over as one metabolism across the next
three Epoch months (Aug-Oct 2026). It lands in `pdoom1` because pdoom1 is the
design/philosophy hub; the other two repos are invited to confirm or amend
their leg via cross-repo issues (see "Ratification plan" below). Nothing here
imposes work on pdoom-data or pdoom1-website unilaterally.

Grounding (decided things this doc builds ON, not re-decides):

- `docs/copy/README.md` -- the SOURCE/PUBLISHER contract (pdoom1 = source,
  website pulls; agent-manual until volume justifies automation).
- `docs/ROADMAP.md` "Cross-repo" -- the roadmap -> website upward-comms
  protocol (website re-projects on material change; signal = commit + a
  cross-repo issue for big re-casts, e.g. pdoom1-website#164).
- `docs/RELEASE_NOMENCLATURE.md` -- the monthly Theme/Epoch/Seed clock
  (Epoch = first Friday; minor + ladder bump together; Seeds weekly).
- `docs/PRODUCT_STRATEGY_RATIONALE.md` -- two products, one data backbone;
  the fact/opinion firewall ("fact: data. opinion: game."); pdoom-data as
  the public data lake; the "Bloomberg terminal" B2B angle.
- `docs/game-design/DESIGN_PHILOSOPHY.md` (reality-tether, ~75% canon:
  "Reality becomes the map generator") + ADR-0016 (league metabolism: the
  game trails reality by one month; monthly world-update packs; <=1
  day/week founder ops budget) + `docs/adr/0004-self-describing-data.md`
  (files declare their schema; tooling dispatches on the declaration).
- `docs/CAPABILITY_UPLIFT_SCAN.md` BET 3 -- "close the telemetry loop":
  run artifacts flowing home, landing in pdoom-data as the first real
  ingestion feed. This proposal folds that in as the RETURN leg.

---

## 1. The cycle in one paragraph

The triumvirate is a metabolism: **pdoom-data** crawls and curates real
AI-safety events (the public, fact-only data lake); **pdoom1** ingests a
curated monthly pack and balance-shapes it into in-game content (opinion
layer: weights, doom modifiers, event framing -- all of which stay HERE);
**pdoom1-website** pulls the voice seam + roadmap + release notes and
publishes the outward presentation. The RETURN leg closes the loop:
anonymized run artifacts (seed, version, turns survived, death attribution,
which events fired) flow home from players to pdoom-data, so next month's
curation is steered by what actually happened in play. One full turn of the
cycle = one Epoch month. Reality becomes the map generator; play becomes
the curation signal.

## 2. The cycle diagram

```
                 HOP A: World-Update Pack (facts only)
      +--------------------------------------------------------+
      |                                                        v
+-----------+                                            +-----------+
| pdoom-data|                                            |  pdoom1   |
| data lake |                                            | the game  |
| crawl +   |                                            | balance-  |
| curate    |                                            | shaping   |
+-----------+                                            +-----------+
      ^                                                        |
      |                                                        | HOP B:
      | RETURN LEG: Run Artifact feed                          | voice seam +
      | (anonymized telemetry,                                 | roadmap +
      |  event-in-play signals)                                | release notes
      |                                                        v
      |                                                  +-----------+
      +--------------------------------------------------|  pdoom1-  |
                       (website relays player-submitted  |  website  |
                        telemetry to the landing zone    | publisher |
                        [INFERRED -- endpoint TBD])      +-----------+
```

Direction discipline (already ruled, restated): pdoom1 never depends on
pdoom1-website (copy/README contract). This proposal adds the analogous
rules for the other two boundaries: pdoom-data never depends on pdoom1
(facts don't know about the game), and the return leg carries only
anonymized artifacts, never source-of-truth data (the lake's facts are
curated from reality, not from the game).

## 3. The three contracts (one per boundary)

Each hop gets a NAMED contract, owned by the DOWNSTREAM repo's need but
DOCUMENTED in the upstream repo (the producer publishes its interface;
consumers pull). All three are pull-based, matching the existing seam.

### Contract 1 -- the World-Update Pack (pdoom-data -> pdoom1)

**What crosses:** a curated monthly pack of real AI-safety events for the
month the game's frontier is about to absorb (game trails reality by ~1
month, ADR-0016). Shape [PROPOSED]:

- One JSON file per monthly pack (e.g. `packs/2026-08.json` in pdoom-data),
  self-describing per ADR-0004 (`schema_type: "world_update_pack"`).
- Each entry: event id, date, title, factual description, entities,
  sources (urls), confidence -- **facts only**. This is the fact/opinion
  firewall at the boundary: NO game_impacts, NO doom modifiers, NO
  weights in pdoom-data. (pdoom-data's current `CROSS_REPO_INTEGRATION.md`
  sample schema embeds `game_impacts` -- that predates the firewall ruling
  and needs cleanup on the pdoom-data side; flagged in Risks.)
- pdoom1 ingests the pack and does ALL balance-shaping locally: mapping
  facts to ADR-0005 schedule entries / event-pool additions, assigning
  weights and doom-stream contributions, voice-skinning descriptions.
  The shaped output lives in `godot/data/` and is versioned with the Epoch.

**Pull mechanism:** agent-manual. A pdoom1 lane reads the pack from the
pdoom-data repo, shapes it, opens a PR. No sync script yet (same posture
as the voice seam -- automate when volume justifies).

**Schema authority [PROPOSED]:** pdoom-data owns the FACT schema (what an
event IS); pdoom1 owns the SHAPING schema (what an event DOES in-game).
Two schemas, one id namespace -- shaped events carry the pack event id as
provenance, so any in-game event traces to its sources.

### Contract 2 -- the Publication Pull (pdoom1 -> pdoom1-website)

**Already largely decided** -- this leg mostly restates the existing
contracts and adds the monthly rhythm:

- The **voice seam** (`docs/copy/README.md`): six canonical source files,
  website pulls and collates. Unchanged.
- The **roadmap protocol** (`docs/ROADMAP.md` "Cross-repo"): website
  re-projects on material change; big re-casts get a cross-repo issue.
  Unchanged.
- **NEW, monthly [PROPOSED]:** each Epoch ships with (a) release notes /
  patch notes (already produced: `godot/data/patch_notes.json` + the
  release page) and (b) **league notes** (the ADR-0016 "league launches
  fresh with notes" artifact -- format owed, see Risks). The website pulls
  both within a few days of the Epoch Friday and publishes the monthly
  "world turned over" post: new Theme, new ladder, what changed, what real
  events entered the world.
- **Doom-clock feed: explicitly OUT of this hop.** Per
  PRODUCT_STRATEGY_RATIONALE, the P(Doom) clock (pdoom-dashboard) ties to
  pdoom-data, NOT the game, so serious-metrics arguments stay uncontaminated
  by the cartoony game. If the website ever surfaces a clock, it reads
  pdoom-data's serveable layer directly [INFERRED -- pdoom-data has a
  `serveable/` dir that looks built for exactly this; confirm with Pip].

### Contract 3 -- the Run Artifact feed (pdoom1 -> pdoom-data, the RETURN leg)

**What crosses:** the capability scan's BET 3, made a standing organ.
The engine already computes, per run, deterministically: seed, version,
ladder, turns survived, death-attribution root cause, replay hash
(ADR-0006). Today those die on the player's disk. [PROPOSED]:

- **Payload v0:** the run summary only (no full replays yet) --
  `{seed, ladder_version, game_version, turns_survived, outcome,
  death_root_cause, events_fired[], replay_hash}` -- anonymous by default,
  riding the same consent posture as the #799 install ping.
- **Transport:** the same phone-home path `leaderboard_sync.gd` already
  uses [INFERRED -- endpoint design is exactly the open question the scan
  says to start early]. Landing zone: a `telemetry/` (or `runs/`) inlet in
  pdoom-data, schema-validated on arrival, SEPARATE from the fact lake
  (`raw/` vs curated facts -- run data is evidence about the GAME, not
  about reality; it must never leak into the fact layer).
- **What it feeds:** the monthly curation. "Which events fired and how
  runs ended" tells next month's pack author which content is load-bearing,
  stale, or never-seen. Bot sweeps say what is POSSIBLE; telemetry says
  what is HAPPENING (scan's framing). Together they are the league's
  steering signal.

**Privacy note:** anonymized, aggregate-oriented, opt-in-visible. The
firewall applies here too -- run telemetry is game-opinion data and is
never presented as AI-safety fact.

## 4. The monthly beat (Aug-Oct 2026, on the Epoch clock)

The cycle turns once per league month. Within a month [PROPOSED]:

| When (rel. to Epoch Friday) | Action | Actor |
|---|---|---|
| E-7 (prev. Friday) | Pack draft opened in pdoom-data (LLM-drafted, per ADR-0016 ops model) | pdoom-data lane |
| E-2 (Wednesday) | Pack FROZEN; Pip editorial approval (the curation moat is his judgment) | Pip |
| E-2..E-0 | pdoom1 pulls pack, balance-shapes, PR, fast gate green | pdoom1 lane |
| E (first Friday) | Epoch ships: minor+ladder bump, new baseline seed, league notes | pdoom1 (existing train) |
| E+1..E+4 | Website pulls release notes + league notes + any voice-seam changes; publishes the monthly post | pdoom1-website lane |
| continuous | Run artifacts trickle home (once Contract 3 is live) | players -> pdoom-data |
| E-9 (approx) | Telemetry digest of the CLOSING month summarized for the next pack draft | pdoom-data lane |

Who pulls what: every arrow is a PULL by the downstream repo (pdoom1 pulls
the pack; website pulls the copy; pdoom-data receives pushed telemetry but
PULLS nothing from the game repo). Signals are commits + cross-repo issues,
same as the roadmap protocol.

### The three months, concretely

The ramp is deliberate: the cycle does not pretend to be fully alive in
August. Per the roadmap, v0.16 (Oct 2) is ALREADY pinned as "wider event
pool from pdoom-data" -- so October is the first FULL turn, and Aug/Sep
build the organs. Confidence: Aug is grounded; Sep ~70%; Oct is direction
[INFERRED from roadmap provisional status].

**August (v0.14 "Per-tick & People" prov., ships Aug 7, L3):**

- pdoom-data: WAKE THE REPO (dormant since 2026-06-27). Confirm/define the
  fact schema + `world_update_pack` schema; clean the firewall breach in
  its sample data/docs (`game_impacts` out of the lake); draft a PILOT
  pack (2026-07 real events, small -- 5-15 events) as a dry run. No
  gameplay dependency this month.
- pdoom1: v0.14 ships on its own content (no pack dependency). Side lane:
  ADR-0004 schema-registry work proceeds (scan BET 2), which is the
  ingestion machinery the pack lands on. Start the telemetry endpoint
  conversation (#800 honest-transmit fix is the opener).
- pdoom1-website: pulls v0.14 release notes; publishes the monthly post.
  Confirms its leg of this proposal (cross-repo issue, below).

**September (v0.15, ships Sep 4, L4 -- public-alpha hardening month):**

- pdoom-data: first REAL pack (August's events), Pip-approved on the E-2
  beat. Stand up the telemetry landing zone (schema + inlet dir), even if
  nothing flows yet.
- pdoom1: consume the pilot/September pack into the event pool as a
  low-stakes trial (a handful of shaped events, clearly provenance-tagged).
  v0.15 is the hardening month (leaderboard, install ping #799, bug
  reporter #800) -- exactly the infrastructure the return leg rides. If
  #799/#800 land, run-summary telemetry v0 goes live behind the same
  consent.
- pdoom1-website: monthly post now includes "real events that entered the
  world" as a section -- the outward face of the reality-tether.

**October (v0.16 "Sightings" prov., ships Oct 2, L5 -- first full turn):**

- pdoom-data: September pack drafted WITH the first telemetry digest
  (if v0 flowed) -- the loop's first closed turn. Pack now the roadmap's
  promised "wider event pool" feedstock.
- pdoom1: v0.16 ships with the pdoom-data-fed pool expansion (roadmap
  commitment). Frontier advances; league notes name the real events.
- pdoom1-website: full-cycle monthly post: new Theme + new world events +
  (if presentable) first aggregate play stats. By now the post has a
  stable template -- candidate for the copy corpus.

## 5. Manual-first vs automatable

Per the standing principle (copy/README: "agent-manual, for now... until
content volume justifies automation") and ADR-0016's <=1 day/week ops
budget:

**Manual (agent-drafted, Pip-approved) for all of Aug-Oct:**

- Pack curation and approval (the editorial judgment IS the moat --
  PRODUCT_STRATEGY_RATIONALE; do not automate the taste).
- Balance-shaping of pack events in pdoom1.
- Website pulls and the monthly post.
- Telemetry DIGESTS (a human/agent reads the data and writes the summary).

**Automated from day one (because it cannot be manual by nature):**

- The telemetry transport itself (client -> endpoint -> landing zone).
  Players will not hand-mail JSON.
- Schema validation on pack PRs in pdoom-data (validate.yml already
  scaffolded there [INFERRED from repo listing]; keep it).

**Automate LATER, when volume justifies (explicitly not now):**

- Pack -> shaped-events transform assist (the ADR-0004 registry makes this
  cheap when wanted).
- Website pull sync job.
- Telemetry auto-aggregation dashboards (the scan's Balance Observatory
  pattern applied to player data).

## 6. Ratification plan (careful, iterative, no unilateral moves)

Modeled on the roadmap -> website signal that already worked
(pdoom1-website#164):

1. **This doc lands in pdoom1 as PROPOSED** (this PR). Pip reviews/amends.
   Merging it here ratifies ONLY pdoom1's own leg-shape intentions.
2. **Two cross-repo issues** (filed AFTER Pip merges, not before):
   - pdoom-data: "Confirm your leg of the triumvirate metabolic cycle" --
     links this doc; asks: fact-schema + pack-schema ownership, firewall
     cleanup, pilot pack in Aug, telemetry landing zone in Sep. pdoom-data
     answers with ITS OWN doc/issue-plan; disagreements come back as
     comments on this doc.
   - pdoom1-website: same shape -- monthly post beat, league-notes pull,
     doom-clock question. Website already carries #164's re-projection
     habit; this extends it to a monthly rhythm.
3. **Status ladder for this doc:** PROPOSED -> AGREED-PER-LEG (each leg's
   confirming issue linked here as it lands) -> ACTIVE (all three legs
   confirmed; status header flips). Amendments repeat the same loop --
   change proposed here, legs confirm.
4. **Monthly retro line item:** each Epoch's league-notes prep includes a
   one-line "did the cycle turn? what jammed?" note. Three jams in a row =
   revisit this doc, not push harder.

## 7. Risks / open questions (for Pip)

1. **pdoom-data is dormant and doc-stale.** Last push 2026-06-27; its
   CROSS_REPO_INTEGRATION.md is python-bridge-era and its sample event
   schema embeds `game_impacts` INSIDE the lake -- a fact/opinion firewall
   breach the strategy doc already flagged ("sample data that blurs this
   fact/opinion line should be cleaned up"). Waking the repo + cleanup is
   real August work. Estimate: 1-2 days. Risk if skipped: the pack
   contract gets built on a schema that leaks opinion into the public
   lake -- the exact reputational exposure the firewall exists to prevent.
2. **Ops budget honesty.** ADR-0016's own consequence note: solo liveops
   decay is the real sustainability risk. This proposal adds pack curation
   + monthly post + telemetry digest to the monthly train. My estimate:
   ~1 day/month once the organs exist, but ~2-3 days/month during the
   Aug-Sep ramp. If that breaches the <=1 day/week envelope alongside
   feature work, the ramp stretches (Oct full-turn slips to Nov) --
   probability of exactly that slip: ~40% [INFERRED from the scan's ~60%
   slip estimate on BET 3 alone].
3. **Telemetry privacy posture is undecided.** Anonymous-by-default is
   the #799 framing; run telemetry proposed to ride the same consent. But
   `events_fired[]` + seed + version is fingerprint-adjacent for a tiny
   playerbase. Needs a ruling before Contract 3 goes live: what fields,
   what retention, where stated to players.
4. **League-notes format is still owed** (ADR-0016 open question). Hop B's
   monthly post depends on it. Cheap to settle: one template, first used
   at the v0.15 or v0.16 Epoch.
5. **Doom-clock ownership.** This doc routes the clock to
   pdoom-data-direct (per PRODUCT_STRATEGY_RATIONALE's separate-dashboard
   reasoning), NOT through pdoom1. If Pip wants the website to surface a
   clock sooner, that is a pdoom-data <-> website contract, a FOURTH edge
   outside this cycle -- fine, but name it separately so the triumvirate
   diagram stays honest.
6. **Engagement dependency (named in ADR-0016).** The cycle only pays if
   real players are on the league "pretty darn soon" -- and the
   public-alpha channel decision (ROADMAP, 2026-07-21) is still open.
   The return leg is worthless without players; the Aug-Oct ramp assumes
   First Contact lands roughly on its Sep 29 target.
7. **Schema authority split (Contract 1) needs pdoom-data's assent.**
   "pdoom-data owns fact schema, pdoom1 owns shaping schema, shared id
   namespace" is my proposal [INFERRED as the natural firewall-preserving
   split]; pdoom-data's confirming issue should explicitly accept or
   counter it.
8. **Which repo hosts the telemetry endpoint?** The scan says
   "website/endpoint + pdoom-data landing zone + client" -- three moving
   parts across all three repos. The website relaying to pdoom-data keeps
   the game repo out of ops [INFERRED]; but Pip may prefer the leaderboard
   server host it since that path already exists. Decide with the #800 fix.

---

*Proposal drafted 2026-07-25 by a design lane; grounded in the docs listed
at top; repo-state claims (pdoom-data contents/dormancy, roadmap pins,
issue states) verified same day via gh. PROPOSED, not ratified -- Pip and
the two sibling repos iterate from here.*
