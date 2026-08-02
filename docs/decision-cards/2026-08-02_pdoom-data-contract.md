# Decision card -- what pdoom1 actually wants from pdoom-data

- **Date:** 2026-08-02
- **Trigger:** Pip's ruling in pdoom1#1097 / pdoom-data#55: pdoom-data#51 (rarity
  is a length threshold on a discarded field) and pdoom-data#52 (all_events.json
  has no producer) are NOT fixed unilaterally by pdoom-data. pdoom1 reviews the
  findings, decides what information it actually wants, pdoom-data draws that
  down. Direction of authority: pdoom1 -> pdoom-data.
- **Status:** PREP FOR PIP. Nothing here has been posted to pdoom-data. No code
  changed. Every claim below was verified against the pdoom1 tree on 2026-08-02;
  file:line refs are to that tree.

This card assumes no memory of the session that produced it.

---

## 1. Context: what the game consumes today, measured

`godot/data/historical_events.json` is a 1,194-record snapshot of pdoom-data's
`all_events.json`, imported ONCE at commit 88a71959 (2025-12-25, PR #503) and
never re-synced. `godot/autoload/event_service.gd` loads it at startup (an API
fetch of `https://api.pdoom.org/v1/events/timeline` is tried first and falls
back to the snapshot), transforms each record into a game event, and
`godot/scripts/core/events.gd:104-115` feeds them into the same trigger loop as
built-in events.

Corpus composition (counted from the shipped file): 1,129 `arxiv_*` + 37
`distill_*` + 28 hand-authored. 1,174 of 1,194 carry category
`technical_research_breakthrough`. All 1,129 arxiv records carry the IDENTICAL
impacts array (`research +15, papers +10, vibey_doom +3`) -- one distinct value
across the whole population.

### Field-by-field inventory (the actual contract, as implemented)

| pdoom-data field | Does pdoom1 read it? | What it does | Verdict |
|---|---|---|---|
| `id` | YES (required) | Event identity; `arxiv*` prefix also triggers flavour demotion (`event_service.gd:491-497`) | KEEP |
| `title` | YES (required) | Player-facing name | KEEP |
| `year` | YES | Trigger scheduling + start-year filter (`events.gd:111-113`; 54 pre-2017 records can never fire) | KEEP, prefer full `date` |
| `category` | YES | Picks the option template (`_generate_options`), flavour demotion, provenance fallback | KEEP, controlled vocab needed |
| `description` | YES | Player-facing text | KEEP, but see quality note below |
| `rarity` | YES | Selects trigger mode/probability/min_turn from pdoom1's OWN `rarity_curves.json` -- see section 2 | RETIRE from contract |
| `impacts[].variable/change` | YES | Mapped via pdoom1's `variable_mapping.json`; drives a `significance` scalar that scales auto-generated options; used directly only in the funding_catastrophe branch | MOVE to pdoom1 side (ADR-0015) |
| `impacts[].condition` | NO (never read; all 1,194 are null anyway) | -- | DROP |
| `safety_researcher_reaction`, `media_reaction` | YES | Flavour strings appended to option messages | OPTIONAL nice-to-have |
| `pdoom_impact` | Copied onto the game event, then read by NOTHING (zero consumers in `godot/scripts`) | Dead weight; also contradicts ADR-0015 by construction | DROP |
| `sources` | NO (game never reads it) | Provenance -- valuable in pdoom-data and on the website, not drawn by the game | KEEP upstream, not drawn |
| `tags` | NO | -- | KEEP upstream, not drawn |
| `source_id` | NO -- and DANGEROUS | In pdoom-data it is a hex row-hash (1,166 records). In pdoom1 `source_id` means "the named character who owns this information" (`event_tiers.gd:65-71`, feed provenance). Same key, incompatible semantics. Currently harmless only because `_transform_event` builds a fresh dict and does not copy it | RENAME upstream or never pass through |

### What the game NEEDS on an event and currently synthesizes by heuristic

The workshop-3-era delivery model (`godot/scripts/core/event_tiers.gd`,
ADR-0012, Balance `defaults.json`) classifies every event by:

- `delivery_tier`: ambient / feed / window -- only WINDOW demands a decision
- `event_class` (windows): un-snoozable / deferrable / standing / no-action
- `source_id`: named-character provenance for feed items
- `unignorable`, `expiry_turns`, `window{}`, `options`

None of this comes from pdoom-data. It is synthesized: "has options and type
popup -> window" (`event_tiers.gd:53`), "arxiv or technical_research_breakthrough
-> feed/flavour" (the #630 P0 fix, `event_service.gd:474-477`), everything else
defaults via Balance. These are GAME-BALANCE classifications; under the standing
principle already written in `variable_mapping.json` ("pdoom-data owns facts and
defaults; pdoom1 owns balance tuning") they belong on pdoom1's side and should
NOT be requested from pdoom-data.

---

## 2. Ruling prep: is "rarity" a concept pdoom1 wants at all?

**What rarity does in the shipped game, end to end:**

1. For 1,174 of 1,194 records (the arxiv/research deck), the P0 flood fix
   demotes the event to the FEED tier, `flavour` channel. Feed items are log
   lines; their effects are never applied and no decision opens
   (`month_controller.gd:189-210` routes feed items to `feed_log` only). So for
   98% of the corpus, rarity's ONLY effect is WHEN a mechanically inert flavour
   line appears.
2. For the ~20 hand-authored non-research events, rarity picks the trigger
   mode: legendary -> deterministic beat at the historical date, rare ->
   probabilistic window, common -> random-after-eligible
   (`event_service.gd:413-436` against `rarity_curves.json`).
3. The `_default_effects[rarity]` fallback (`event_service.gd:748-755`) is a
   DEAD PATH for this corpus: all 1,194 records have impacts arrays.

pdoom-data#51's measurement stands up against the shipped file: 1,076/1,194
"rare" because the source PDF exceeded 20,000 chars of since-discarded text;
37/37 distill "legendary" because they came from distill.pub. The field is
noise for the bulk population and unverifiable (no recorded rubric) for the 28
hand-authored records.

**The honest answer: pdoom1 does not want "rarity". It wants two orthogonal
things it already synthesizes locally:**

- *Does this demand a decision?* -- delivery_tier / event_class (ADR-0012).
  Balance classification, pdoom1-owned.
- *Is this a scheduled historical beat or ambient texture?* -- trigger mode.
  Under ADR-0005 ("a seed = RNG seed + event schedule") and ADR-0016 (monthly
  world-update packs drawn from pdoom-data), the pack AUTHOR decides which
  events become scheduled causes. A per-record frequency enum has no seat in
  that model.

A three-value enum derived from PDF length is measuring nothing, and the game
would lose nothing by never receiving it again.

**Sequencing guard (this is the trap #51 flagged as option (c)):** pdoom-data
must NOT nullify or delete `rarity` before pdoom1 stops reading it.
`event_service.gd:384` defaults missing rarity to "common", which would move
1,072 events from min_turn 20 / p=0.06 to min_turn 10 / p=0.12 per turn -- a
real feed-pacing change on the live build. Order: pdoom1 change lands first,
then the data change is a no-op by construction.

---

## 3. Ruling prep: should all_events.json exist, and who produces it?

pdoom-data#52's finding: the file has no reproducible producer (the 1,194-record
union was written by ad-hoc commits on 2025-12-24 and cannot be rebuilt), yet it
is the single file the website's daily sync reads and the source of pdoom1's
snapshot.

From pdoom1's seat:

- pdoom1 consumes a ONE-TIME copy, not a live feed. The game has zero build-time
  or run-time dependency on pdoom-data being able to regenerate the file today.
  (The API path would create a silent live dependency if `api.pdoom.org` ever
  starts serving -- see section 6.)
- The future draw-down is already ruled: ADR-0016 monthly world-update packs
  ("collect real world events ... author a world-update pack (ADR-0005 schedule
  entries, fed from the pdoom-data repositories)"). That is a CURATED MONTHLY
  DIFF in a pdoom1-specified schema -- not a re-pull of a 1,194-record bulk
  mirror.

So: yes, the file should exist and be reproducible -- but for pdoom-data's own
integrity and the website's sake, not because pdoom1 needs it. pdoom-data#52's
proposed `scripts/build/project_timeline_events.py --check` producer is the
right fix ON THEIR SIDE and pdoom1 endorses it without depending on it. What
pdoom1 asks for instead is the pack contract (section 4).

---

## 4. THE PRECISE ASK -- options for Pip

### Option A (recommended): facts-only contract; classification and balance stay in pdoom1

The drawn-down record, per event, becomes exactly:

    id            required, stable, namespaced (no bare row-hashes)
    title         required, player-facing quality
    date          required, YYYY-MM-DD (full date, not just year)
    category      required, from a short controlled vocabulary pdoom1 ratifies
    description   required, curated PROSE (not PDF extraction), length-capped
    sources       required upstream for provenance; game does not read it
    tags          optional
    reactions     optional (safety_researcher_reaction / media_reaction)

Explicitly REMOVED from the contract: `rarity`, `impacts`, `pdoom_impact`,
`source_id` (in its row-hash meaning), `impacts[].condition`.

- Rarity: retired per section 2. pdoom-data may keep any internal field it
  likes for the website badge; pdoom1 ignores it.
- Impacts: post-ADR-0015, effect vocabulary is the curated intermediary set
  (`global_alarm`, `global_panic`, `safety_absorption`, `frontier_capability`,
  `general_capability` -- see `godot/data/events/overrides/example.json`
  `_adr_0015` note), and doom writes from event content are already inert
  no-ops (`resource_accessor.gd:75-79`). Assigning intermediary magnitudes is
  an ADR-grade balance act. It cannot live in a facts repo. pdoom1 authors
  effects in its overrides / world-update packs.
- Delivery: bulk corpus stays as-is (the shipped snapshot already works as
  flavour-feed ambience); NEW material arrives as ADR-0016 monthly world-update
  packs in a schema pdoom1 publishes when the EE-6 pipeline lane builds it.

Trade-offs: pdoom1 takes on classifying the 28 hand-authored events itself
(one override file; trivial). pdoom-data's enrichment pipeline stops pretending
to produce game balance, which is a simplification for them, not a cost.
Website keeps whatever fields it wants -- but if rarity is retired their badge
and rare-first sort need a heads-up (#51 documents both).

### Option B: fix rarity upstream (real rubric or citation signal), keep the pull-everything contract

Trade-offs: preserves the current pipeline shape and the website badge gets a
real meaning. But the game demonstrably routes nothing of value on it (section
2), so this is effort spent making a slightly better version of a field the
consumer should not be reading -- and it leaves impacts/pdoom_impact encoding
ADR-0015-retired mechanics in the schema. Not recommended.

### Option C: freeze -- rule nothing until the ADR-0016 pack pipeline is built

Trade-offs: cheapest today; the snapshot keeps working. But it leaves
pdoom-data#55 with no drawn-down ask (the exact outcome Pip's ruling exists to
prevent), leaves the website's rarity problem unresolved, and leaves the
option-(c) nullification trap armed. Not recommended.

**Recommendation: A, phased.**

1. NOW (a ruling, not a build): adopt the Option A field list; declare rarity
   retired from the contract; state the sequencing guard (pdoom1 stops reading
   rarity before pdoom-data touches the field).
2. pdoom1 side, small change when scheduled: stop reading `rarity` in
   `event_service.gd` -- classify the ~20 window-grade hand-authored events via
   the existing overrides mechanism, and let the flavour deck pace off one
   config value instead of three fake tiers.
3. pdoom-data side (their #52 plan, endorsed as-is): invariants first, then the
   `all_events.json` producer. pdoom1 endorses, does not depend.
4. Contract v2 = the monthly world-update pack schema, published by pdoom1 when
   the ADR-0016 / EE-6 pipeline lane builds. That schema, not all_events.json,
   is the long-run interface.

### Who owns each side (all options)

- pdoom-data owns: facts, provenance, corpus integrity, reproducible exports.
- pdoom1 owns: the drawn schema (field list + vocabularies), all game-facing
  classification (tier/class/trigger), all effect magnitudes (intermediaries),
  all pacing (rarity_curves or its successor), and the overrides layer.
- The website draws its own contract separately; retiring rarity needs them in
  the loop before any data change (game is the authority; website is a peer
  consumer, not a constraint).

---

## 5. Defects found in pdoom1's own house (not pdoom-data's fault; file separately)

- **Time denomination mismatch:** `rarity_curves.json` says `turns_per_year:
  52`; the Clock says one turn = one workday (~260/yr, `clock.gd:13-15`); the
  code fallback says 12 (`event_service.gd:951`). Historical events therefore
  fire at compressed calendar positions -- "events trigger on their actual
  dates" (docs/data/HISTORICAL_DATA_INTEGRATION.md) is not currently true. Any
  contract language must not promise it.
- **54 pre-2017 records can never fire** (start-year filter, `events.gd:111`).
- **Dead pipeline docs:** `docs/data/HISTORICAL_DATA_INTEGRATION.md` and
  `scripts/sync_from_pdoom_data.sh` describe a `transformed/timeline_events`
  per-year sync into `godot/data/historical_timeline/` consumed by
  `timeline_loader.gd`. That loader has ZERO callers in the game, and only
  `2017.json` exists. Two documented pipelines, one real (the snapshot), one
  dead. The dead one should be marked or removed before it misleads the next
  contract discussion.
- **`pdoom_impact` is copied but never consumed** -- delete the copy or the
  field.

## 6. What could NOT be determined, and what would settle it

- **Whether `api.pdoom.org/v1/events/timeline` is live.** EventService tries it
  on every launch and will ingest WHATEVER it returns with no schema validation
  and no version pin (`event_service.gd:251-307`). If that endpoint ever starts
  serving, it silently replaces the shipped snapshot on players' machines --
  a determinism and league-integrity hazard bigger than anything in #51/#52.
  Settle by: one curl, then either stand the endpoint up under the v2 contract
  with a schema version, or delete the fetch path until it exists.
- **Whether players ever reach the 2020+ events.** Run-length telemetry/replays
  would say how much of the corpus is reachable at all; with the time-
  denomination bug unresolved the year->turn mapping is wrong anyway.
- **Whether Pip wants the arxiv flavour deck at all.** Mechanically it costs
  nothing now (feed-only, capped, demoted); its descriptions are extraction
  garbage (#51: 756 records literally "1 Introduction") but the feed renders
  only titles. Keeping it is a taste call, not a correctness one. If kept,
  a description-quality pass upstream is cosmetic, not urgent.
- **The website's actual field needs** -- out of scope here by design; they
  draw their own contract. Their rarity badge/sort is the one consumer a
  rarity retirement visibly changes.

## 7. Sources

- pdoom-data#51, #52, #55; pdoom1#1097 (the ruling), #630 (flood, CLOSED),
  #503/#442/#505 (the 2025-12-25 import)
- `godot/autoload/event_service.gd` (transform, rarity routing, API path)
- `godot/scripts/core/events.gd` (trigger loop), `event_tiers.gd` (tier/class),
  `month_controller.gd:189-210` (feed vs window dispatch),
  `resource_accessor.gd:75-79` (inert doom writes)
- `godot/data/historical_events.json`, `godot/data/events/balancing/
  rarity_curves.json`, `variable_mapping.json`, `godot/data/events/overrides/
  example.json`, `godot/data/balance/defaults.json`
- ADR-0005 (seed = RNG + schedule), ADR-0012 (event taxonomy), ADR-0015 (no
  printed doom deltas), ADR-0016 (league metabolism / monthly packs) in
  `docs/game-design/decisions/`
- Legacy (dead): `docs/data/HISTORICAL_DATA_INTEGRATION.md`,
  `scripts/sync_from_pdoom_data.sh`, `godot/scripts/data/timeline_loader.gd`
