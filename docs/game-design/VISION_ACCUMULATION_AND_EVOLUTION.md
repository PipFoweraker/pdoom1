# P(Doom)1 -- Vision: Accumulation and Evolution

> **Status: living / evolving vision document.** This captures Pip's north-star
> framing for what P(Doom)1's data *becomes* over time, then bolts architectural
> structure onto it. Like `DESIGN_PHILOSOPHY.md`, it preserves the original phrasing
> before any paraphrase, and it is meant to be iterated, contradicted, and sharpened.
> It deliberately separates **the dream** (aspirational, unbuilt) from **buildable next
> hooks** (small, concrete, do-now). It does **not** propose changing the frozen score
> contract (ADR-0002) -- everything here is additive.

---

## 1. The vision, in Pip's words

The core attraction, verbatim:

> "trying to get people to think about the cumulative effects of their actions, over
> time, and how we can try to network those to build towards good futures as we avoid
> AI doom."

The premise this rides on:

> "We live in an era where capabilities are advancing very rapidly, and things
> accumulate. Like high scores. Like runs on pdoom1."

The ask -- the thing the architecture exists to make possible:

> "if we architect cleverly, can we start to think of ways to aggregate and assimilate
> data for what's submitted to the game so that, over time, we can do things like really
> cool visualisations of evolutions of the game, deep score runs, show the discovery and
> adaptations of strategies as *players* explore the game and find ways to break it."

The motif -- the game is a thing that builds itself, and says so:

> "'This thing keeps building and building itself' is both a motif of the game and also
> something that I'd like to see start to articulate in how the game expresses the story
> of its own development."

Pip notes this has already been happening in the repo's own history: the change-log
shows the design "evolving from simple principles into increasingly articulated
philosophies has been emergent in the game."

The image to hold in mind when we imagine the eventual visualizations:

> "a histogram of a tree of life and then a Cambrian explosion kind of thing ... from
> the abstract to the replete within the space of things like code, histograms, series,
> and the evolution of forking channels that we'll explore through many player runs."

**One-sentence compression:** every run is a data point in a growing population; the
population, visualized over time, tells the story of both the strategy-space *and* the
game's own development -- and we should architect now so that story can be told later.

---

## 2. Architectural synthesis (the coordinator's structure)

This section is the interpretation layer: how the vision above maps onto systems that
already exist in the repo, and what small additions let the substrate start accreting.

### 2.1 Run telemetry as the substrate (not a scoreboard)

The leaderboard is **the first instance of a run-telemetry system**, not a mere
high-score table. The distinction matters: a scoreboard stores an *outcome* (turns
survived); a telemetry substrate stores the *run* -- enough of its shape that later
analysis can reconstruct populations, lineages, and divergences.

The substrate already half-exists. Each run is deterministically fingerprinted by
`VerificationTracker` (`godot/autoload/verification_tracker.gd`):

- A **chained SHA-256 hash** updated after every action, event, event-response, response
  window, RNG outcome, and turn-end. `start_tracking()` seeds it from the seed + game
  version; every subsequent record folds the previous hash plus the new datum. Same
  seed + same inputs -> same 64-char hex hash. That hash is the run's **DNA**: a compact,
  tamper-evident identity.
- An **ordered replay log** (`replay_log`) -- the canonical run artifact per ADR-0006.
  Entries record player inputs in execution order: actions (`k:"a"`), event responses
  (`k:"r"`), and response windows (`k:"w"` -- carrying the payment source:
  reserve / cannibalize / defer / ignore). The hash is demoted to a cheap fingerprint;
  the replay log is what a verifier *re-simulates* to prove a run is legal.
- The artifact also carries `seed`, `game_version`, the `event_schedule` (ADR-0005: the
  schedule is part of seed identity), and the `league` (ADR-0016). Format tag:
  `pdoom1-replay-v1`.

So the run's *shape* is already computed client-side. The gap is that today it does not
all travel to, and accumulate on, the server as a queryable population.

### 2.2 The enrichment path (additive, contract-safe)

Today a leaderboard submission carries a **thin** slice. From
`server/leaderboard/score_api.php` (`$ALLOWED_FIELDS`) and the frozen contract
(ADR-0002 / `docs/strategy/BACKEND_AND_DATA_ARCHITECTURE.md`):

```
score, doom_integral, player_name, date, level_reached, game_mode,
duration_seconds, entry_uuid, baseline_score, baseline_doom_integral   (+ seed, version)
```

That is the *ranking* payload -- turns survived (score) and the doom-integral tiebreak,
plus provenance. **It must stay backward-compatible.** ADR-0002 froze the scoring
semantics ("flows only, never stocks"; boards keyed by `(seed, game_version)`) and
`BACKEND_AND_DATA_ARCHITECTURE.md` froze the HTTP contract ("Changes are versioned
(`/v2/...`), never silent"). None of the vision requires touching either.

**The enrichment is a separate telemetry channel, or optional additive fields.** To let
the evolution visualizations exist, a submission could OPTIONALLY carry the run's SHAPE:

- the ordered action / input sequence (`replay_log` already produces it -- ADR-0006's
  `pdoom1-replay-v1` artifact is exactly this);
- a derived **strategy signature** -- a compact summary of the run's posture (e.g. the
  action-class histogram, the opening N moves, the branch points where the run diverged
  from the do-nothing baseline);
- the run **DNA** (the verification hash) as the stable join key.

Accumulate those across the player population and the leaderboard dataset stops being a
list of scores and becomes a **strategy-space population** -- the raw material for every
visualization below.

Design guard rails, restated so no later agent breaks them:

- **Score contract stays frozen.** Enrichment is a new optional field set or a sibling
  telemetry table/endpoint on the same PHP host (`BACKEND_AND_DATA_ARCHITECTURE.md`
  keeps score-plane and data-plane distinct; the score writer stays the sole score
  writer). Ranking never reads enrichment fields.
- **Additive-only, degrade-gracefully.** Just as `record_window_response` bumped the
  replay schema with a new `k:"w"` key that the v1 simulator ignores, enrichment must be
  ignorable by anything that does not understand it. Pre-enrichment artifacts stay valid.
- **Verification remains the only law** (DESIGN_PHILOSOPHY, "On losing"). Enrichment is
  descriptive, never authoritative for ranking; a run is legal iff it re-simulates.

### 2.3 The visualizations it unlocks (future work -- named, not built)

These are **the dream**, listed so the substrate is built toward them, not as committed
features. All of them fall out of an accumulated population of run-shapes:

- **Strategy-fingerprint histograms.** Bin runs by strategy signature; watch the
  distribution of how people are playing a given `(seed, version, league)`. Pip's "tree
  of life ... histogram" image, made literal.
- **A tree / forking-channels view of strategy divergence.** Cluster runs by shared
  opening / shared branch points; render how strategies fork across the player
  population as the meta explores the seed. Pip's "evolution of forking channels that
  we'll explore through many player runs" -- and his "Cambrian explosion" once a league
  opens and strategies radiate.
- **"Deep run" replays.** Because the replay artifact re-simulates deterministically
  (ADR-0006), any standout run can be replayed / scrubbed / annotated -- a spectatable
  object, chess-PGN-style. "deep score runs."
- **Exploit-discovery detection over time.** Watch the population for the moment players
  "find ways to break it" -- a strategy signature that suddenly dominates, or a run that
  trips the doom-floor instrument (DESIGN_PHILOSOPHY: sustained doom decline is a balance
  bug, not a rules violation). This is the strategy-space telling the dev where the
  engine misbehaves -- the exploit-finder as a *population* instrument, not a single
  headless sweep. (Note the philosophy line: an exploit is engine misbehaviour, distinct
  from a clever legal line that just out-thinks the current patch.)

### 2.4 The self-referential motif (the game tells its own developmental story)

Pip's motif -- "This thing keeps building and building itself" -- has two faces, and the
architecture should serve both:

1. **The player-facing accumulation:** runs pile up, leagues rotate (ADR-0016 -- the game
   trails reality by a month; each league another slice of the real race enters the seed
   timeline), strategies radiate. The dataset visibly grows.
2. **The dev-facing accumulation:** the repo's own change-history is the *same shape* of
   story. `DESIGN_PHILOSOPHY.md` literally documents "simple principles branching into
   increasingly articulated philosophies" -- a fold-log where four issues collapse into
   one Ledger, three into one SA system, and a single "you cannot win, only buy time"
   axiom grows sixteen-plus ADRs. The ADR sequence *is* a phylogenetic tree of design
   decisions.

The vision is to make these two legible **as one phenomenon**. The accumulating run-data
and the accumulating design-history are both instances of "increasingly articulated
philosophies emerging from simple principles" -- one in strategy-space, one in
design-space. A mature version of this doc (or a tool it points to) could render both on
the same footing: the ADR tree beside the strategy tree, development-time beside
play-time.

**Sibling data substrate (cross-link).** The strategy-space population is not the only
accreting dataset in the ecosystem. `pdoom-data` (the curated event corpus) is the
sibling data plane: its **A/B/C/D importance tiers** -- A(1166 arXiv, in-game) / B(3966)
/ C(1375) / D(42), per `docs/SESSION_STATUS_2026-07-17.md` and pdoom-data #25 -- are the
salience layer that feeds the game's event schedule and, via league metabolism, its
month-by-month advance. `BACKEND_AND_DATA_ARCHITECTURE.md` keeps the planes distinct
(scores vs pdoom-data vs website presentation), all on one frozen-contract PHP host. The
"forking channels ... explored through many player runs" and the "improving over time"
curated corpus are the two halves of the self-building whole: **the world-data grows
(pdoom-data), and the play-data grows (run telemetry), and the game is the join.**

### 2.5 "Keep everything" is a design constraint

Pip does **not** want this data cleaned up or discarded. That is a first-class
architectural constraint, not an afterthought: the whole value proposition is
*longitudinal* -- you cannot visualize an evolution you threw away. Retention beats
tidiness. Store raw artifacts append-only; derive summaries downstream; never prune the
source. (Storage is cheap; a `pdoom1-replay-v1` artifact is a small JSON blob, and even
the full input log is tiny next to its analytical value.)

---

## 3. Near-term hooks (buildable now, small, concrete)

The point of naming these: the substrate should **accrete before the visualizations
exist**, so that when someone builds a viz there is already a corpus to render. None of
these touches the frozen score contract; all are additive and low-ceremony.

1. **Persist the run DNA with every submission.** Add the `verification_hash`
   (already computed, already in `export_for_submission`) as an optional field on the
   telemetry channel, keyed to the same `entry_uuid`. This is the stable join key for
   every future analysis -- the cheapest possible first accretion. (One field; ignorable
   by the ranking path.)

2. **Persist the compact input log (`replay_log`) alongside the score.** The
   `pdoom1-replay-v1` artifact already travels in `export_for_submission()["replay"]`;
   land it server-side into a sibling telemetry store (NOT the ranking row -- keep it off
   the frozen contract). This alone unlocks deep-run replays and every shape-derived
   analysis later, because the run can be re-simulated from it. Append-only; keep all of
   it (per section 2.5).

3. **Emit a compact strategy signature at game-over.** A small derived summary -- e.g.
   action-class histogram + first-N opening moves + count of response-window payment
   choices by type (`reserve`/`cannibalize`/`defer`/`ignore`, already recorded on
   `k:"w"`). Cheap to compute from `replay_log`, cheap to store, and it is what
   fingerprint-histograms and forking-channel clustering read first -- before anyone
   writes a re-simulator-backed pipeline.

4. **Stamp the accretion context on every telemetry record.** Carry `seed`,
   `game_version`, and `league` (all already in the replay artifact) on the telemetry
   record too, so the population is sliceable by league/version from day one. Leagues
   rotate the meta (ADR-0016); without this stamp a cross-league evolution view is
   impossible to reconstruct after the fact.

Optional / slightly-larger fifth hook, flagged as such:

5. **A sibling read endpoint for the telemetry store**, on the same PHP host as the
   score API, behind its own versioned contract -- so a future local HTML tool (Pip's
   preferred build target) can pull the population and render the first histogram. This
   is the seam where "the dream" starts becoming buildable; it is not needed to *start
   accreting* (hooks 1-4 do that), only to start *visualizing*.

**Sequencing note:** hooks 1-4 are pure capture -- they make the corpus grow even with
zero viz code written, which is the whole point ("keep everything" only pays off if
capture precedes analysis). Hook 5 is the first step of the read/viz side and can wait
until there is a corpus worth looking at.

---

## 4. Dream vs buildable -- the honest separation

| | The dream (unbuilt) | Buildable next hook (now) |
|---|---|---|
| Substrate | strategy-space population across all runs | persist hash + replay log + signature per run (section 3.1-3.3) |
| View | tree-of-life / Cambrian-explosion strategy viz | sibling read endpoint + one local histogram tool (3.5) |
| Self-reference | ADR-tree beside strategy-tree, one render | (not yet -- needs the corpus first) |
| Exploit story | population-level exploit-discovery detection | capture the payment-choice + signature data that would reveal it (3.3) |

The dream is aspirational and explicitly *not committed*. The hooks are the small,
safe, do-now moves that keep the dream *reachable* -- so that "if we architect cleverly"
(Pip) is answered by architecture that has already started, quietly, with each submitted
run.

---

## 5. Cross-links

- `docs/game-design/DESIGN_PHILOSOPHY.md` -- the "why"; source of "verification is the
  only law", the loss-ladder (personal -> competitive -> cultural), the doom-floor
  instrument, and the "power up the office" / two-instrument doctrine this doc extends to
  telemetry.
- `docs/game-design/decisions/ADR-0002-scoring-turns-survived.md` -- the **frozen** score
  semantics (lexicographic turns; flows-only; boards keyed by `(seed, game_version)`).
  Never broken by anything here.
- `docs/game-design/decisions/ADR-0005-emergent-waves-seed-schedules.md` -- the event
  schedule as part of seed identity (travels in the artifact).
- `docs/game-design/decisions/ADR-0006-replay-artifact-backend.md` -- the input-string
  replay as the canonical run artifact (anti-cheat + share + bug-repro); the basis for
  deep-run replays and shape analysis.
- `docs/game-design/decisions/ADR-0016-league-metabolism.md` -- leagues (the game trails
  reality by a month); the rotation axis every evolution view slices on.
- `godot/autoload/verification_tracker.gd` -- where the run DNA (hash) and the replay
  artifact are produced.
- `server/leaderboard/score_api.php` -- the frozen-contract score endpoint
  (`$ALLOWED_FIELDS`); enrichment is a sibling channel, not a change to this.
- `docs/strategy/BACKEND_AND_DATA_ARCHITECTURE.md` -- one PHP backend, frozen HTTP
  contract, distinct data planes (scores / pdoom-data / website).
- `pdoom-data` repo -- the sibling data substrate (A/B/C/D importance tiers; the curated
  world corpus that grows over time), per `docs/SESSION_STATUS_2026-07-17.md`.

---

## Change log

- **2026-07-20** -- First fill. Captured Pip's accumulation/evolution vision verbatim
  (core attraction, "things accumulate ... like runs on pdoom1", the aggregate-and-
  visualize ask, the self-building motif, the tree-of-life / Cambrian-explosion image).
  Added the coordinator's architectural structure: run-telemetry-as-substrate, the
  contract-safe enrichment path, the visualizations it unlocks, the self-referential
  motif tying run-data to the ADR/change-history, and four-plus concrete near-term
  capture hooks. Explicitly does not touch the frozen score contract (ADR-0002).
