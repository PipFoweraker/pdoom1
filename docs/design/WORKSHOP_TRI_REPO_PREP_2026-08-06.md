# Tri-repo content workshop -- pdoom1's prep as CHAIR

- **Session:** 2026-08-06, 2h05 hard stop. Agenda: `coordination#30`. Proposal it
  discharges: `coordination#17`. Chair: `pdoom1`. Recorder: `coordination`.
- **Binding input, not re-litigated here:** `coordination#15` (section 5c status
  vocabulary; sister repos REFERENCE, do not COPY).
- **Prepared by:** pdoom1 seat, 2026-08-06. Everything below was measured against
  `origin/main` at `78be0370` plus the open PR branch
  `feat/event-retime-and-promotions` (`pdoom1#1137`), not recalled.
- **Protocol changed mid-prep:** `coordination#31` (posted 2026-08-06) gives each
  repo ONE VOTE and lets Pip cast 0-2, so three unanimous seats beat him 3-2.
  Phase 1 requires each seat to post an independent position BEFORE Pip's sealed
  positions are released. **Section 3 of this document is pdoom1's Phase 1
  ballot.** Sections 1 and 2 remain the evidence base; they were written before
  `#31` arrived and are unchanged by it.
- **This document does not answer A1 or A2 on Pip's behalf.** It prices each
  option in pdoom1, and then -- per `#31` -- casts pdoom1's own vote on the
  merits.

---

## 0. Executive summary -- four findings, three of which correct the agenda

1. **The agenda's A1 cost figure is wrong, and the retime is not why.** The
   claim that nulling `rarity` moves 1,072 events from `min_turn 20 / p=0.06` to
   `min_turn 10 / p=0.12` is wrong in the count, wrong in the `min_turn` values,
   and **inverted in direction** for the only records that move at all. It was
   already wrong before the retime, and the retime does not change it. Full
   working in section 1.
2. **`rarity` mechanically does far less than either repo believes.** After
   tracing the code, the entire behavioural content of the rare/common
   distinction is (a) `p=0.06` vs `p=0.12` and (b) a 9-turn later start for
   pre-2018-dated records. The "eligibility window" that gives `rare` its name
   is **written and never read**. Section 1.3.
3. **On A2, the two documents are not evenly matched, and the code has already
   voted.** `docs/copy/README.md` (pull) describes what is built. The push
   sentence in `docs/content/ROLE_CREATIVE_DIRECTOR.md` sits inside a
   `Status: DRAFT ... Not committed anywhere yet` header block and is an aside
   about where a doc should live. Section 2.1.
4. **Asset provenance is not recorded anywhere that survives to a published
   asset. Not partially -- not at all.** No `origin` field exists in ADR-0019,
   in `godot/assets/`, or in anything pdoom1 emits. The Manifund obligation is
   therefore **currently unmet, not at risk of becoming unmet**, 34 days out
   from 2026-09-09. Section 2.2.

---

# A1 -- DECISION CARD: what crosses the boundary from pdoom-data into pdoom1

**Read this cold. No session context assumed.**

## A1.0 Context

`pdoom-data` curates an AI-safety event corpus. `pdoom1` ships a frozen 1,194-record
snapshot of it at `godot/data/historical_events.json`, hand-committed once on
2025-12-25 (`88a71959`, PR #503) and **never re-synced**. `pdoom-data` has asked
three times what shape it should send. pdoom1 has not answered.

The chain of asks, in order:

| Where | Date | What it asked |
|---|---|---|
| `pdoom1#1052` Q2 | 2026-07-30 | what should a pdoom-data event carry? |
| `pdoom-data#55` | 2026-08-02 | ruled: "trigger a review in pdoom1, let pdoom1 decide" |
| `pdoom1#1102` | 2026-08-02 | that review, filed, **zero comments to date** |
| `pdoom-data#43` | open | the export-profile issue blocked on the answer |

`pdoom-data` is structurally forbidden from answering: its ADR-007 exists to stop
it picking pdoom1's mechanical vocabulary from outside pdoom1. `pdoom1-website`
must be in the room (its browse index sorts on `rarity`) and cannot vote.

**Sources, all readable without this document:**
`pdoom1#1102` (the measured inventory), `pdoom1#1052`, `pdoom1#1115`,
`pdoom-data#43` (options A/B/C), `pdoom-data#55`,
`docs/decision-cards/2026-08-02_pdoom-data-contract.md`,
`godot/autoload/event_service.gd`, `godot/scripts/core/events.gd`,
`godot/data/events/balancing/rarity_curves.json`.

## A1.1 The three sub-questions, as the agenda states them

1. Facts only, or facts **plus attributed editorial opinion**?
   (`pdoom-data#43` options A / B / C; that seat recommends B.)
2. If opinion: expressed in **pdoom-data's own taxonomy** with a mapping table on
   pdoom1's side, or directly in **pdoom1's DQ-21 intermediary names**?
3. Does pdoom1 want **`rarity`** at all -- keep, split, or null it?

## A1.2 THE RETIME ARITHMETIC CHECK -- the agenda's figure does not survive

The agenda states, as the reason no single repo can answer A1:

> nulling rarity moves **1,072 events** from `min_turn 20 / p=0.06` to
> `min_turn 10 / p=0.12`, a live gameplay change `pdoom-data` cannot make.

**Verdict: the figure is wrong on three counts, and the retime is not the cause.**
It was wrong before the retime. The retime leaves it exactly as wrong.

### (a) The count is 1,076, and 1,028 of those reach the pool

Measured over all 1,194 records in `godot/data/historical_events.json` on `main`:

| rarity | records | dated >= 2017 (reach the pool) |
|---|---|---|
| `rare` | **1,076** | **1,028** |
| `common` | 77 | 73 |
| `legendary` | 41 | 39 |

48 `rare` records are dated 2016 and are dropped by the start-year filter at
`godot/scripts/core/events.gd:111-113` (`if event_year < state.start_year: continue`;
`DEFAULT_START_YEAR = 2017`, `godot/scripts/core/game_state.gd:214`) before
`should_trigger` is ever called on them. They cost nothing either way.

Nearest measured figure to the agenda's 1,072 is **1,073** -- `rare` AND caught by
the flavour gate. Not 1,072. Whatever produced 1,072, it is not reproducible
against the shipped corpus.

### (b) `min_turn: 20` is dead config -- a rare event never uses it

`event_service.gd:335-342`, the `probabilistic_window` branch that every `rare`
record takes, **does not read `rarity_settings.min_turn` at all**:

```
"probabilistic_window":
    var spread = year_config.get("rare_spread_turns", 13)
    var window = rarity_settings.get("eligibility_window_turns", 26)
    trigger_turn = base_turn + spread
    eligibility_start = max(1, trigger_turn - window / 2)
    eligibility_end = trigger_turn + window / 2
```

and the event's shipped `min_turn` is then `eligibility_start`
(`event_service.gd:378`), i.e. a **year-derived** number, never 20. Only the
`common` branch (`:346`) reads the flat value, and even there as
`max(min_turn, base_turn)` -- so it is 10 only for records dated before 2018.

`rare.min_turn: 20` appears in `rarity_curves.json` and in the hardcoded fallback
at `event_service.gd:461`. It is read by nothing. Both sides of the agenda's
`min_turn` pair are fiction.

### (c) The direction is inverted for the only records that move

Computing `eligibility_start` for all 1,076 `rare` records as `rare` and again as
`common`, the delta distribution is:

| eligibility_start change if `rarity` is nulled | records |
|---|---|
| **no change** | **975** |
| **+9 turns (LATER, 1 -> 10)** | **101** |
| earlier | **0** |

Not one record becomes eligible sooner. 101 do so **later** -- the ones dated
2016-2017, whose `base_turn` is below `common`'s floor of 10. (Of those 101, 48
are the 2016 records already filtered out, so 53 actually move.)

The cause is arithmetic that holds in both timescales: `eligibility_start` for a
rare record is `base_turn + spread - window/2`, and `spread == window/2` in both
variants (13 == 26/2, and 3 == 6/2), so it collapses to `base_turn` -- the same
value `common` uses, except that `common` also floors it at 10.

### (d) The retime does not change any of this

`pdoom1#1137` is **OPEN, not merged** (branch `feat/event-retime-and-promotions`;
7 files). Its `rarity_curves.json` changes `turns_per_year` 52 -> 12,
`legendary_month_offset` 26 -> 6, `rare_spread_turns` 13 -> 3,
`rare.eligibility_window_turns` 26 -> 6, and adds the `timescale` /`timescales`
dial. It leaves `common.min_turn: 10`, `common.base_probability: 0.12`,
`rare.min_turn: 20` and `rare.base_probability: 0.06` **untouched**.

The delta table in (c) was computed under both `(52, 13, 26)` and `(12, 3, 6)`
and is **identical**: `{no change: 975, +9: 101}`.

**So: the agenda's figure is not stale-because-of-the-retime. It was never right.
Correcting it is worth more than the retime finding the workshop expected.**

### (e) What nulling `rarity` ACTUALLY costs -- the honest number

Three real effects, in descending size:

1. **RNG fork -> replay and ladder fork.** 53 in-pool records dated 2017 have
   their first probability roll deferred from turn 1 to turn 10. Every candidate
   consumes `rng.randf()` (`events.gd:185`) and records it in
   `VerificationTracker`. Moving when rolls happen forks the seeded stream, which
   forks replays and the leaderboard board key. **This is the only cost that is
   genuinely expensive**, and it is the same constraint `pdoom1#1137` already
   carries: land on a release boundary with a version bump so the board key forks
   by design.
2. **Feed volume doubles, and is then absorbed by a cap.** `p` goes 0.06 -> 0.12
   for 1,028 in-pool records, of which **1,025 are flavour-demoted to the feed
   tier** by `_is_flavour_event` (`event_service.gd:404-410`: any
   `technical_research_breakthrough` category or `arxiv*` id). At `p=0.06` that
   pool already produces roughly 60 candidates per turn against
   `events.max_new_events_per_turn: 2` (`godot/data/balance/defaults.json:6`) --
   an oversubscription of ~30x. Doubling it makes ~120 candidates for the same 2
   slots. **The player does not see twice as much; the player sees a different
   two.** Feed churn, not feed flooding.
3. **Decision surface: three records.** Only three `rare` records survive the
   flavour gate and can open a decision window:
   `ftx_future_fund_collapse_2022`, `openai_board_crisis_2023`,
   `international_coordination_breakdown_2025`. Those three go from 6%/turn to
   12%/turn from the same turn. That is the entire gameplay-visible consequence.

**Restated for the room:** the agenda frames `rarity` as a live gameplay lever
`pdoom-data` cannot touch. Measured, it is a replay-determinism lever with a
three-record gameplay tail. That should change how expensive "null it" feels.

### (f) Two defects found while checking, filed here for the record

- **`eligibility_end` is written and read by nothing.** `event_service.gd:366`
  writes it; `should_trigger`'s `"random"` branch (`events.gd:173-190`) checks
  only `min_turn` and `probability`. There is no window. A `rare` event rolls
  6%/turn **forever** once eligible. The `probabilistic_window` trigger mode is
  misnamed, and `pdoom1#1137`'s new `rare_eligibility_window_turns` dial position
  therefore tunes a value with no consumer.
- **`_get_rarity_settings`'s poison-key trap got wider.** `event_service.gd:446`
  tests `_rarity_curves.has(rarity)`, so any record whose `rarity` string
  collides with a top-level key of `rarity_curves.json` returns the wrong dict.
  On `main` the poison set is `{_description, _note, default_rarity, year_trigger}`;
  `pdoom1#1137` adds `_retime_2026_08`, `timescale`, `timescales`, taking it from
  4 to 7. No such record exists today. Also noted in `pdoom1#1102` and
  `pdoom1#1151`.

## A1.3 What `rarity` is actually worth keeping, if anything

Everything the rare/common distinction does today, exhaustively:

| Mechanism | Effect | Live? |
|---|---|---|
| `base_probability` | 0.06 vs 0.12 per turn | **yes** |
| `min_turn` floor of 10 | 9-turn later start, pre-2018 records only | **yes**, 101 records |
| `eligibility_window_turns` | bounded window | **no** -- `eligibility_end` unread |
| `cooldown_turns` (15 vs 8) | re-fire spacing | **no** -- all historical events are `repeatable: false`, short-circuited at `events.gd:146` |
| `legendary` -> deterministic | fires at an exact turn | **yes**, and unaffected by the rare/common question |

And the field's provenance, per `pdoom-data#51` cited in `pdoom1#1102`: `rarity`
is an exact `text_length > 20000` threshold on a field that is not carried into
the output. Correlation with the visible description length is `r = -0.0065`.
**It is a proxy for source-PDF length.**

Consequence worth saying out loud in the room: all 41 `legendary` records are in
the arxiv/flavour stream, so the tier meaning "always fires, key story beat" is
applied **exclusively** to records that are then demoted to a grey feed line. The
19 records that can open a window are 17 `common` and 3 `rare`. **Zero legendary.**
`pdoom1#1137` fixes this by hand for 24 promoted events via an override file; it
does not fix the field.

## A1.4 The options, priced

### Sub-question 1 -- facts only, or facts plus attributed opinion?

| Option | What pdoom-data sends | Cost in pdoom1 | Cost elsewhere |
|---|---|---|---|
| **A. Facts only** (`pdoom-data#43` A) | title, date, description, sources, provenance, attributed tags | pdoom1 supplies `category`, `impacts`, `rarity`, salience for every record. With 1,194 records that is a curation job pdoom1 has never done and has no tool for. | cleanest against pdoom-data's ADR-007 firewall |
| **B. Facts + attributed opinion** (`#43` B, **pdoom-data recommends**) | A, plus `category_suggestion_by_profile` and `salience_tier_by_profile`, each attributed | pdoom1 inherits or ignores per field. Needs a mapping table + a policy for "we disagree". Salience is the field `pdoom1#630` / `UI_FEATURES_STACK.md:39-44` has been asking for since the feed-flooding playtest. | pdoom-data already ships `salience_tier_by_profile` on its candidate feed (A 172 / B 687 / C 1717 / D 858) -- just not on `all_events.json` |
| **C. Full `event_v1`** | today's shape, incl. `impacts` / `rarity` / `pdoom_impact` | zero new work; keeps the status quo | requires pdoom-data to assert shaping fields -- the breach its `#34` exists to undo, and `pdoom_impact` is null in 1,187 of 1,194 records anyway |

**pdoom1's recommendation: B.** The reason is specific rather than diplomatic:
option A obliges pdoom1 to hand-classify 1,194 records to recover a decision
surface of 19, and option C keeps shipping `pdoom_impact` (null 1,187/1,194) and
`rarity` (a PDF-length proxy). B is the only option that delivers the one field
pdoom1 has independently asked for -- **salience** -- which is the principled fix
for the feed flooding that `_is_flavour_event` currently patches with a hardcoded
`arxiv*` prefix match.

### Sub-question 2 -- pdoom-data's taxonomy, or pdoom1's DQ-21 names?

DQ-21 is **resolved and live**. The accepted intermediaries are handled at
`godot/scripts/core/events.gd:315-337`: `global_alarm`, `global_panic`,
`safety_absorption`, `general_capability`, `frontier_capability`
(plus `political_pressure`, deliberately absent because `doom_system.gd:246`
reassigns it every tick, so an event write there would be an inert sink).

| Option | Cost in pdoom1 | Risk |
|---|---|---|
| **pdoom-data's taxonomy + mapping table on pdoom1's side** (pdoom-data's recommendation, its ADR-007) | one mapping file in `godot/data/events/balancing/`, maintained by pdoom1 | pdoom1's vocabulary stays pdoom1's to revise; renaming an intermediary touches one file here and zero packs in the wild |
| **pdoom1's DQ-21 names directly** | no mapping file | every exported pack already distributed silently means the wrong thing the day pdoom1 renames or splits an intermediary. No error, no failed parse -- numbers attached to a concept that no longer exists |

**pdoom1's recommendation: pdoom-data's taxonomy plus a mapping table here.**
Note the precedent already in the tree:
`godot/data/events/balancing/variable_mapping.json` is that mapping table,
already existing, and `pdoom1#1102` records that it currently maps
`vibey_doom` / `stress` / `burnout_risk` onto a literal `doom` key, which is
exactly what ADR-0015 outlaws and survives only via the panic-stream reroute at
`events.gd:290-310`. So the mechanism exists; it needs re-pointing at DQ-21
names, not inventing.

### Sub-question 3 -- keep, split, or null `rarity`?

| Option | pdoom1 files touched | Events affected | Replay / ladder |
|---|---|---|---|
| **Keep as-is** | none | none | none |
| **Null it** (pdoom-data stops sending; pdoom1 defaults everything to `common`) | `godot/data/historical_events.json` (or its successor), no code change -- `default_rarity: "common"` already exists at `rarity_curves.json` | 1,076 records reclassified; 1,028 in pool; 1,025 of those are feed tier; **3** are decision-window; 53 records' first roll moves turn 1 -> turn 10 | **FORKS both.** RNG stream changes. Needs a release boundary + version bump, same as `pdoom1#1137` |
| **Split** (replace `rarity` with a pdoom1-owned salience/tier field, sourced from pdoom-data's `salience_tier_by_profile`) | `event_service.gd` (`_get_rarity_settings`, `_is_flavour_event`), `rarity_curves.json`, the ingest schema | all 1,194 -- and it retires the hardcoded `arxiv*` flavour gate, which is the actual fix for `pdoom1#630` | **FORKS both**, and by more than nulling |

**pdoom1's recommendation: SPLIT, sequenced after `pdoom1#1137` lands.** Reasons,
in order of weight:
1. Nulling and splitting cost the same thing that actually matters (a board
   fork), so paying it twice would be the waste. Pick the end state.
2. `rarity` is a PDF-length proxy with `r = -0.0065` to anything visible. Keeping
   it means keeping a field that means nothing, on pdoom1's side, forever.
3. The field pdoom1 has independently asked for three times (`#630`,
   `UI_FEATURES_STACK.md:39-44`, `SESSION_STATUS_2026-07-17.md:36-37`) is
   salience, and pdoom-data already computes it.
4. **Sequencing matters:** `pdoom1#1137` is open and already forks the board once.
   Landing the split in the same release boundary makes it one fork, not two.

**The counter-argument the chair must put in the room:** `pdoom1-website` badges
`rarity` on 1,194 public pages and uses it as its browse index's secondary sort
key. Splitting changes what those pages say without a website decision. That is a
real cost, it belongs to a seat that cannot vote on A1, and the honest version is
that the website inherits whichever field replaces it -- so the ruling should
name the replacement field's values **in the same breath**, not defer them.

## A1.5 What A1 cannot deliver on its own

Even a perfect A1 ruling is undeliverable today: **there is no working sync path
from pdoom-data to pdoom1.** `scripts/sync_from_pdoom_data.sh` has been deleted
(`pdoom1#1115`) after evidence it never completed a run -- it read directories
that do not exist in pdoom-data and wrote directories that do not exist in
pdoom1. The 42-address redaction (`pdoom1#1106`, merged) had to be applied by
hand-copying a file.

**So A1's ruling is a specification with no transport.** That is B2's problem on
the agenda, and the chair should say so when A1 concludes rather than letting the
room believe the ruling ships anything.

---

# A2 -- DECISION CARD: push or pull, and what a published asset carries

**Read this cold. No session context assumed.**

## A2.0 Context

Two documents in `pdoom1` state opposite directions of flow between the game and
the website. Neither cites the other. Every image decision downstream waits on
which is authoritative. `pdoom1-website#249` is the blocked party and filed its
seat position on 2026-08-06.

Second, separate question riding on the same item: does a published asset carry
an `origin` field (`generated` / `human` / `photo`), and is the website
**required** to be able to say which? The agenda calls this the **Manifund
commitment** -- a truth obligation on the website created by an art decision in
the game (`pdoom1#1015`, `pdoom1-website#194`, deadline **2026-09-09**).

**Sources:** `docs/copy/README.md`, `docs/content/ROLE_CREATIVE_DIRECTOR.md`,
`docs/game-design/decisions/ADR-0019-pull-from-demand-asset-pipeline.md`,
`docs/art/ART_MASTERS_POLICY.md`, `pdoom1-website#249` (body + the seat comment),
`pdoom1#1113`, `pdoom1#900`.

## A2.1 Which document describes what the code does -- PULL, and it is not close

### The evidence, not the preference

**On the website side** (from the `pdoom1-website` seat's audit in `#249`,
re-derived against its `origin/main` at `e7637794`): three sync workflows exist,
`sync-pdoom1-docs.yml`, `sync-design-tokens.yml`, `sync-events.yml`. **All three
pull.** There is no image or asset sync in either direction, no push receiver, no
manifest format, no naming convention.

**On the pdoom1 side:** there is no emitter either. `ADR-0019` (ACCEPTED
2026-08-03 -- the most recent architectural word on the pipeline, and *after*
both contested documents) defines exactly three asset states:

| State | Where |
|---|---|
| Generated | `art_generated/` (gitignored) |
| Library | `art_source/` (<=1MB, in git) + masters archive |
| Packed | `godot/assets/` |

Its Interaction Contract "Writes" clause constrains all future writes to
`godot/assets/**`. **There is no publish or emit state in the accepted
architecture at all.** Every stage terminates inside `godot/`.

### The two documents are not of equal standing

- `docs/copy/README.md` opens with `**Status:** ACTIVE POLICY (2026-07-25).
  This is the interface contract between pdoom1 (this repo) and pdoom1-website.`
  Its clause 1 is explicit: *"Direction is one-way. `pdoom1-website` reads
  `pdoom1`. `pdoom1` never depends on `pdoom1-website`."* It names six canonical
  pull targets and a pull mechanism.
- `docs/content/ROLE_CREATIVE_DIRECTOR.md` opens (lines 3-9) with
  `> Status: DRAFT for Pip review, 2026-07-26. Not committed anywhere yet.` The
  push sentence is **line 6**, inside a bullet titled `PROPOSED PERMANENT HOME`,
  and reads in full: *"procedures live next to the game they capture;
  `pdoom1-website` is a publish TARGET the pipeline pushes to, not the home of
  the process"*. It is an aside justifying where a **document** should live, in a
  role description about **video content**, in a file whose own header says it is
  not committed anywhere.

**Finding: this is not two policies contradicting. It is one ACTIVE POLICY and one
parenthetical in a self-declared draft.** The agenda's framing ("two policy docs
written a day apart, neither citing the other") is accurate on the facts and
overstates the symmetry.

### If PULL wins, retire this exactly

- **File:** `docs/content/ROLE_CREATIVE_DIRECTOR.md`
- **Line 6**, the clause `pdoom1-website is a publish TARGET the pipeline pushes
  to, not the home of the process`.
- **Replacement:** keep the "procedures live next to the game they capture"
  rationale, which is unaffected, and replace the push clause with a citation:
  `see docs/copy/README.md clause 1 -- direction is one-way, the website reads
  the game`.
- **Also:** `docs/copy/README.md`'s Related section already flags
  `docs/CONTENT_DISTRIBUTION_SYSTEM.md` as an OUTDATED predecessor that proposed
  publishing *from* pdoom1. Same ruling retires it properly rather than leaving
  it "superseded in spirit".

### If PUSH wins, retire this exactly

- **File:** `docs/copy/README.md`
- **The `## The contract` section, clause 1** in full (the "Direction is one-way"
  paragraph), plus the `## Pull mechanism` section, which specifies the
  agent-manual pull as the mechanism.
- **Cost, stated honestly:** push arrives as a build -- receiver, auth, manifest
  format, and a gate -- on a side that has none of those, and it makes the
  website's correctness depend on the art pipeline's release discipline while
  that pipeline is the fastest-changing thing in either repo (ADR-0019 is three
  days old). Pull arrives as a fourth instance of a pattern already running green.

### The caveat the chair should not let pass

**"Pull" is proven for COPY and unproven for BINARY ASSETS.** The three green
workflows move markdown, tokens and JSON. Ruling pull does not make an image pull
exist -- it names who builds it. The concrete follow-on decision is
`pdoom1-website#249`'s ask 2: where published images live. Its options were
(a) committed to `public/`, (b) attached to a GitHub release -- the API the
website already trusts for version and platform facts, (c) a second public
bucket; website lean is **(b)**. **pdoom1 has no objection to (b)** and notes it
composes with ADR-0019: a release attachment is outside `godot/`, so it does not
enter the pack and does not touch the demand manifest.

## A2.2 Does a published asset carry `origin`? -- NOT RECORDED TODAY. AT ALL.

**This is the finding.** Stated plainly because the agenda treats it as an open
design question and it is not -- it is a measured absence.

What was checked, and what was found:

| Where provenance could live | Result |
|---|---|
| `ADR-0019` (the accepted pipeline architecture) | **no `origin`, no provenance field anywhere.** Its demand manifest is pools / floors / sizes. Manifest format and location are in its explicit "What is NOT decided here" list |
| `godot/assets/**` | **no manifest, no JSON, no metadata file of any kind.** `ASSETS_README.md` is a hand-written directory guide with recommended sizes |
| `art_source/pixellab_*/MANIFEST.md` | model, params, prompt suffix, generation date -- **as prose, per BATCH, in markdown.** Not machine-readable, not per-file, not carried forward |
| `tools/art_review/README.md:171-176` | promises "per-asset provenance (prompt, model, cost, hash)" -- but sourced from `art_generated/logs`, and `art_generated/` is **gitignored**. It is a review-tool display; it does not ship |
| `pdoom1#900` | lists "confirm the gpt-image/pixellab pipeline logs prompt+params (provenance)" as a **prereq still open** |
| anything pdoom1 emits for the website | there is nothing pdoom1 emits |

**So: no asset in `godot/assets/` carries `origin`, no artefact leaving pdoom1
carries it, and the batch-level generation metadata that does exist is stripped
by the time a file reaches the pack.** The `pdoom1-website` seat reached the same
conclusion independently on its own side: *"No asset this site serves carries
`origin` ... and none ever has."*

**Consequence for the Manifund commitment:** the obligation to be able to say
which images are AI-generated and which are human-made is **currently unmet, not
at risk of becoming unmet**, with the 2026-09-09 date 34 days away. That is a
statement of fact from the repo that owns the pipeline, and it is pdoom1's to put
on the record rather than the website's to discover.

**What Pip is actually deciding**, therefore, is not "should assets carry
`origin`" but: **is the requirement accepted, or does the copy change?** The
website seat has already stated the honest disjunction and it is correct -- if the
requirement is judged too expensive, the consequence is that the Manifund copy
changes, not that the question goes away.

### Cost in pdoom1 of accepting the requirement

| Increment | Files touched | Effort |
|---|---|---|
| Record `origin` at generation time | `tools/assets/*`, `tools/art_review/*`, the pixellab MANIFEST template | small -- the data exists in the generation logs already, it is just not persisted per-file |
| Carry it into the Library | `art_source/**` sidecar or index | small -- but 5,267 files exist with no record; backfill is "generated" for everything pixellab/gpt-image produced, and requires a judgement for anything else |
| Carry it into `godot/assets/` | the ADR-0019 pull step, which does not exist yet | **this is the natural place to build it.** ADR-0019 already says promotion is a TRANSFORM, not a copy, and a transform can write a sidecar. Adding provenance to a step not yet built is close to free; adding it to a step already built is a migration |
| Emit it for the website | the emitted manifest, which does not exist yet | the `#249` contract sketch already specifies the shape |

**Sequencing observation for the chair:** ADR-0019's pull step is **unbuilt**.
Deciding provenance NOW, before it is built, is the cheapest this decision will
ever be. Deciding it after is a migration across 5,267 Library files.

### The `pdoom1#1113` rider (5 of 30 min)

The four-piece interior art batch (jocular art personifying the three repos) is
the cheapest possible first exercise of an emit-for-non-game-surface path: it is
interior-only, nobody is harmed if the manifest shape is wrong, and it produces a
worked example instead of another design argument. `#1113`'s own constraints
already say to tag it at generation time rather than sorting it out later,
**precisely because of the Manifund commitment**. pdoom1's position: **"wait for
the contract" is a fine answer**, and so is "do it as the contract's first test".
Either is cheap. The one bad outcome is generating it untagged.

### Publish gate distinct from `promotable` (agenda A2 item 3)

`pdoom1#1107` established the sub-stage vocabulary `promotable / contested /
held / blocked`. Those gate entry to the **game's pack**. `publishable` would gate
entry to the **open web**. pdoom1's position: **they must be distinct, and pdoom1
does not want to own `publishable`.** The failure modes are asymmetric --
`promotable` wrong puts a weak sprite in a build (internal, recoverable, cheap);
`publishable` wrong puts a public claim on the indexed web (not retractable by
deleting a file). The website seat has offered to own it. pdoom1 should accept.

---

# `pdoom1#1106` -- in scope, or separate?

**Verdict: SEPARATE from A1/A2 as an item, but a hard dependency on A1's
deliverability, and already represented on the agenda under B2.**

Facts: `pdoom1#1106` is a **MERGED PR**, not an open question. It copied 42
records' redacted `description` fields from pdoom-data into
`godot/data/historical_events.json` (42 insertions, 42 deletions; 1,194 records
before and after; email-shaped strings 42 -> 0). It closed `pdoom1#1098`.

What survives it, and where each belongs:

| Residue | Belongs to |
|---|---|
| The redaction applies to HEAD only -- addresses remain in git history and in any distributed build | **NOT this workshop.** Legal/comms. Pip recorded the pdoom-data equivalent as LATER at `pdoom-data#55` A3 |
| There is no working sync path, so the next upstream correction will also fail to arrive silently | **B2 on the agenda**, and it is already named there: *"there is currently no path for any pdoom-data correction to reach pdoom1"*. Tracked as `pdoom1#1115` + `pdoom-data#52` |
| The redaction had to be applied as a hand file-copy | same as above |

**Recommendation to the chair:** do not add `#1106` to Block A. Cite it once,
during A1, as the worked proof that A1's ruling has no transport -- it is the only
correction that has ever crossed the boundary, and it crossed by hand.

---

# What pdoom1 OWES the other two seats vs what it is ASKING them for

## pdoom1 OWES

| # | To | What | Status |
|---|---|---|---|
| O1 | `pdoom-data` | **An answer to `pdoom1#1102`.** Filed 2026-08-02, zero comments, deferred three times. This is the whole of A1 | **owed, overdue.** Section A1 above is the priced version; the ruling is Pip's |
| O2 | `pdoom-data` | The three sub-answers in a form `pdoom-data#43` can build against: fact-vs-opinion, taxonomy-vs-DQ-21-names, `rarity` keep/split/null | owed at the session |
| O3 | `pdoom-data` | **A correction:** its `rarity` field has `r = -0.0065` correlation with anything pdoom1 uses it for, and 1,073 of the 1,076 `rare` records are demoted to a feed line before `rarity` ever matters. It has been computing a field for a consumer that discards it | **owed now**, independent of A1's outcome |
| O4 | `pdoom1-website` | **The push/pull ruling**, and the deliberate retirement of the losing lines (exact file + lines in A2.1). `#249` has been blocked on this since 2026-08-02 | owed at the session |
| O5 | `pdoom1-website` | **The provenance fact:** `origin` is not recorded anywhere in pdoom1, so the Manifund obligation is currently unmet. The website cannot discover this from its own repo | **owed now.** Filed in this document; relayed in the `coordination#30` comment |
| O6 | `pdoom1-website` | If `rarity` is split or nulled, the **replacement field and its values**, in the same ruling -- because the website badges `rarity` on 1,194 pages and sorts its browse index on it, and cannot vote on A1 | owed if A1 rules split/null |
| O7 | both | `pdoom1#1137`'s **ship constraint**: the retime forks RNG consumption, so replays and board comparability fork. It lands on a release boundary with a version bump. Any corpus change stacked on it should land in the same boundary | **owed now** |
| O8 | `coordination` | **The correction to the A1 cost figure** (section A1.2). The agenda's 1,072 / `min_turn 20 -> 10` / `p 0.06 -> 0.12` line does not reproduce | **owed now**, before the session, so the room does not rule against it |

## pdoom1 ASKS

| # | Of | What | Why pdoom1 cannot answer it |
|---|---|---|---|
| K1 | `pdoom-data` | Put **`salience_tier_by_profile` on `all_events.json`**, not only on the candidate feed. It is the principled fix for `pdoom1#630`, which `_is_flavour_event`'s hardcoded `arxiv*` prefix match currently patches | the field is computed in pdoom-data from data pdoom1 does not hold |
| K2 | `pdoom-data` | The four ADR-0012 event-content fields, or an explicit "no": **class, expiry N, response-expected flag, carrying-cost hook**. Everything currently defaults to `deferrable` | they are content properties of the source record |
| K3 | `pdoom-data` | A **named, existing artifact to pull**, with a JSON Schema and a version pdoom1 can pin (`pdoom-data#52`). `pdoom1#1115` lists the four things a re-sync needs: a named artifact, ingest validation, a diff/review step, a provenance stamp | pdoom1 cannot name a producer in another repo |
| K4 | `pdoom-data` | Confirmation of what happens to the **three variables pdoom1 silently drops as unmapped**: `ethics_risk` (16), `technical_debt` (12), `media_reputation` (4). They still count toward `significance` | they are pdoom-data's vocabulary |
| K5 | `pdoom1-website` | **Own `publishable`** as a gate distinct from pdoom1's `promotable` (`#1107`). pdoom1 should not own a flag whose failure mode is public and irreversible | the failure lands on the website's surface, under its prime directive |
| K6 | `pdoom1-website` | Confirm whether it wants **game art or web-native poster art**. Only 52 of 2,247 game images are hero-shaped and masters cap at 1536x1024 with no upscale path (`#249`). If the answer is web-native, ADR-0019's pull step is the wrong producer and this is a different build | it is a question about the website's surface |
| K7 | `pdoom1-website` | Where published images live -- `#249` ask 2, website lean (b) GitHub release attachment. **pdoom1 has no objection to (b)** and notes it composes with ADR-0019 | it is the website's transport |
| K8 | `coordination` | File **one issue per Block A item**, labelled `broadcast`, same day, per the agenda -- and note that A1 ruled without a transport (`pdoom1#1115`) is a specification, not a delivery. Under section 5c that is `blocked` on a named party, not `moving` | recording is coordination's instrument, per `#17` |

---

# 3. PHASE 1 BALLOT -- pdoom1's positions, posted before Pip's are unsealed

Filed as a comment on `coordination#31`. Reproduced here so the repo holds its own
ballot rather than only the recorder holding it.

## 3.0 Disclosure -- pdoom1 is the least independent seat and must say so

`coordination#31`: *"If you have already read his views elsewhere, say so in your
Phase 1 comment rather than pretending otherwise."*

**pdoom1 is the repo Pip works in every day. Its seat is structurally the least
independent of the three.** Two boundaries, stated separately:

**NOT seen, and not sought:** the 17:44 memo positions on A1/A2/A3/B2/B3, sealed
under SHA-256 `2d0bc4e0...c936ccd`. This seat did not look for them and does not
have them.

**Seen, and legitimately ours -- prior public rulings on pdoom1's own mechanics
that bear on A1/A2.** Every one of these is a merged issue or an accepted ADR in
this repo, but the other two seats may not carry them:

| Ruling | Where | Bears on |
|---|---|---|
| **One turn = ONE MONTH** | `#1125`, `#1111` | A1 sub-question 3, B2 -- it is the premise the whole retime rests on |
| **F4/F5 timing dials and F6 effect magnitudes DEFERRED**, because the current percentages and rarity values are *"hard coded in from ages ago"* and he wants to *"mentally scrap them"* | `#1125`, `#1111` | **A1 sub-question 3 directly.** This is Pip on the record about `rarity`, before the workshop |
| *"pdoom1-website pulls from pdoom1"*, with the website-to-pdoom-data contract expected to change later | `#1111`, "Cross-repo, routed separately" | **A2 sub-question 1 directly.** Discount pdoom1's A2 vote accordingly |
| The asset-pipeline ruling, verbatim, plus *"Yes things are grandfathered"* | `ADR-0019` (ACCEPTED 2026-08-03) | A2 sub-questions 2 and 4 |
| Interior art must be tagged at generation time *"rather than sorting it out later"*, because of the Manifund commitment | `#1113` | A2 sub-question 2 |
| *"pdoom1 decides what it wants, pdoom-data supplies that"* | `pdoom-data#55`, `coordination#9` | A1 framing |

**The honest reading:** on A2 sub-question 1 this seat is not independent. Pip has
already said "pdoom1-website pulls from pdoom1" in a public pdoom1 issue. The vote
below is cast anyway, on evidence that stands without him -- but the room should
apply the discount rather than count pdoom1's A2 as a third free convergence.

`pdoom1-website`'s disclosure is the same shape (`#21`, *"maybe some asset
promotion up to the website"*). So **two of three seats are compromised on A2 bit
1 in the same direction.** Coordination should say so in the post-mortem rather
than reading 3-0 as three independent derivations.

## 3.1 A chair's note on a procedural contradiction

`pdoom1-website` is right that `#30` ("`pdoom1-website` must be in the room and
**cannot vote**" on A1) and `#31` ("vote on everything") cannot both hold.

**pdoom1's chair view: count it.** Two reasons and one reassurance:
1. `#31` is the later protocol and explicitly supersedes how `#30` decides.
2. `#30`'s exclusion was written when A1 was framed as pdoom1-asks / pdoom-data-supplies.
   The website then produced the single most decision-relevant fact anyone brought
   to A1 -- that `rarity` is not an internal field but a public surface with five
   petition buttons on 2,197 pages, pointing game-balance requests at the wrong
   repo. A seat that finds that is not a spectator.
3. **It changes nothing.** All three seats voted B / own-taxonomy, and the website
   deferred `rarity` to pdoom1. Counting or binning the vote gives the same A1.

The recorder still has to rule it before Phase 3, because on a later item it may
not be free.

## 3.2 The ballot

Format: verdict, then the reason, then **the failure mode** -- what would have to
be true for this vote to be wrong. Positions without a stated failure mode are how
this repo shipped a hollow CI gate, a dead sync script, and a review tool that
reported 807 confident keeps of which 75% could not move.

### A1 bit 1 -- facts, or facts plus attributed opinion? **VOTE: B.**

Not as a midpoint. Option A obliges pdoom1 to hand-classify **1,194 records to
recover a decision surface of 19** (measured: 1,174 records are demoted to feed by
`_is_flavour_event`, and one of the remaining 20 is dropped by the start-year
filter). pdoom1 has no tool for that and no plan to build one. Option C keeps
shipping `pdoom_impact`, which is **null in 1,187 of 1,194 records**, and `rarity`,
which correlates `r = -0.0065` with anything visible.

B is also the only option that delivers **salience**, which pdoom1 has asked for
three times in its own documents (`#630`, `UI_FEATURES_STACK.md:39-44`,
`SESSION_STATUS_2026-07-17.md:36-37`) and which is the principled replacement for
the hardcoded `arxiv*` prefix match currently holding the feed together.

**Failure mode:** if pdoom1 ignores the attributed opinion in practice, B is A with
extra bytes. Test at 90 days: is any `*_by_profile` field read by
`event_service.gd`? If not, this vote was wrong.

### A1 bit 2 -- pdoom-data's taxonomy, or pdoom1's DQ-21 names? **VOTE: pdoom-data's taxonomy, mapping table on pdoom1's side.**

The mapping table **already exists**:
`godot/data/events/balancing/variable_mapping.json`. It currently maps
`vibey_doom` / `stress` / `burnout_risk` onto a literal `doom` key -- which
ADR-0015 outlaws and which survives only via the panic-stream reroute at
`events.gd:290-310`. So this is not a new layer to build; it is a broken layer to
re-point at the live DQ-21 names (`global_alarm`, `global_panic`,
`safety_absorption`, `general_capability`, `frontier_capability`, handled at
`events.gd:315-337`).

pdoom-data's ADR-007 argument is correct and favours pdoom1: encoding DQ-21 names
upstream means every pack already distributed silently means the wrong thing the
day pdoom1 renames an intermediary. Given that pdoom1 has renamed its vocabulary
twice this year, that is not hypothetical.

**Failure mode:** the mapping table is a hand-maintained index, which is this
repo's known rot shape (`decisions/README.md`). If it is not `--check`-gated in
pre-commit like `DQ_INDEX.md`, it rots. That gate is a condition of this vote, not
a nicety.

### A1 bit 3 -- `rarity`: keep, split, or null? **VOTE: SPLIT, landed in the same release boundary as `#1137`.**

Reasoning is in section A1.4 and rests on the corrected arithmetic in A1.2. The
short version: nulling and splitting cost the **same** thing that actually matters
-- a replay and ladder fork -- so paying it twice is the only real waste. Pick the
end state.

**pdoom1 owes the website the replacement in the same breath** (obligation O6),
so here it is concretely, as a proposal to be argued with:

- `salience_tier` (A / B / C / D), sourced from pdoom-data's existing
  `salience_tier_by_profile`. Fact-adjacent, attributed, already computed
  upstream. **This is what the website badges and sorts on.**
- `trigger_class` (`deterministic` / `probabilistic`), computed **inside pdoom1**
  from its override files, never supplied by pdoom-data. This is shaping and does
  not cross the boundary.

That split gives the website a stable public field with a defensible meaning and
gives pdoom1 the mechanical dial, and neither repo asserts the other's vocabulary.

**Failure mode:** if `salience_tier` turns out to be as uncorrelated with anything
as `rarity` was, pdoom1 has swapped one meaningless badge for another. The check is
cheap and should be a condition: correlate `salience_tier` against whether a record
survives the flavour gate, before adopting it. If `r` is near zero again, keep
`rarity` and say so.

### A2 bit 1 -- push or pull? **VOTE: PULL. Discounted, per section 3.0.**

Evidence in section A2.1. Summarised: three website transports exist and all three
pull; no image transport exists in either direction; ADR-0019 -- accepted three
days ago, *after* both contested documents -- defines three asset states and no
publish state at all. `docs/copy/README.md` is ACTIVE POLICY with a contract
section. The push sentence is line 6 of a file whose own header reads
`Status: DRAFT for Pip review, 2026-07-26. Not committed anywhere yet.`

**This is the vote to trust least on this ballot**, because Pip has already said it
in `#1111` and this seat read that. The evidence would carry it without him, which
is why it is cast; the room should still weight it as two seats, not three.

**Failure mode:** pull is proven for markdown, tokens and JSON. It is unproven for
binary assets, of which zero have ever crossed. A pull ruling that assumes the
transport will look like the other three is a guess. If the first image pull needs
auth, size budgets, or content addressing that the doc pulls never needed, this
vote decided a direction and left the hard part undesigned.

### A2 bit 2 -- does an asset carry `origin`, and is the website required to say which? **VOTE: YES to both.**

And pdoom1 puts the fact on the record rather than making the website discover it:
**`origin` is not recorded anywhere in pdoom1. Not partially. Not at all.** Not in
ADR-0019, not in `godot/assets/` (no manifest of any kind exists there), not in
anything pdoom1 emits. Batch-level generation metadata exists as prose in
`art_source/pixellab_*/MANIFEST.md` and is stripped before a file reaches the
pack. `#900` still lists "confirm the pipeline logs prompt+params" as an **open
prereq**.

**So the Manifund obligation is currently unmet, not at risk of becoming unmet**,
34 days from 2026-09-09. That is pdoom1's finding about pdoom1, and it was pdoom1's
to report.

The decision Pip actually faces is therefore not "should assets carry origin" but
**"is the requirement accepted, or does the copy change?"** pdoom1 votes accept,
and notes the sequencing that makes it cheap: **ADR-0019's pull step is UNBUILT.**
Its own text says promotion is a TRANSFORM, not a copy -- and a transform can write
a provenance sidecar for free. Deciding this before the step is built costs
approximately nothing; deciding it after is a migration across 5,267 Library files.

**Failure mode:** backfill. Every existing asset needs an `origin` value and the
honest one for most is `generated`, but "most" is not "all" and nobody has
checked. If backfill turns out to require per-file human judgement at 5,267-file
scale, this vote wrote a cheque the pipeline cannot cash before 09-09, and the
honest fallback is that the copy changes anyway -- just later and under more
pressure.

### A2 bit 3 -- publish gate distinct from `promotable`? **VOTE: YES, and `pdoom1-website` owns `publishable`.**

`#1107` gave pdoom1 `promotable / contested / held / blocked`. Those gate entry to
the **game's pack**. `publishable` gates entry to the **indexed web**. The failure
modes are asymmetric by an order of magnitude: a wrong `promotable` puts a weak
sprite in a build (internal, recoverable, cheap); a wrong `publishable` puts a
public claim on a cached and indexed surface that deleting the file does not
retract.

**pdoom1 does not want to own `publishable` and should not be given it.** The
website offered; accept the offer.

**Failure mode:** two gates that always agree are one gate with extra ceremony,
and ceremony decays. If nothing ever gets `promotable: true, publishable: false`,
the separation was theatre.

### A2 bit 4 -- web-native art through pdoom1's pipeline, or a separate media process? **VOTE: same pipeline, second demand target. Do NOT split the process yet.**

This is genuinely pdoom1's question and pdoom1 has a view. ADR-0019 already makes
the pack a function of **declared demand**, with demand expressed as pools, floors
and sizes. A website surface is another demand entry -- `og card: 1 at 1200x630`,
`hero: 1 at 2400px` -- pulling from the same taste-gated Library through the same
transform. Nothing about the ADR requires the destination to be `godot/assets/`;
that is just the only destination declared so far.

Splitting media generation into a separate process duplicates the Library, the
taste gate and the review tooling. **This estate's measured failure this week was
duplication**: `coordination#15` records the same rule being independently
re-derived by three agents, and five separate print implementations.
Deliberately building a sixth duplicate to solve a routing problem is the wrong
trade.

**Failure mode:** `pdoom1-website#249` measured that only 52 of 2,247 game images
are hero-shaped and that game masters cap at 1536x1024 with no upscale path. If
the website wants 2400px web-native poster art, the shared Library may not contain
anything it can use, and "same pipeline, second target" becomes a shared name over
two disjoint asset sets -- which is the duplication I just voted against, wearing
a single pipeline's badge. **This is the vote on the ballot I hold most weakly**,
and `pdoom1-website` should overrule it if K6 comes back "web-native".

### A3 -- is the event corpus in scope for Chinese localisation? **VOTE: NO, corpus out. And the agenda's premise for this item is wrong.**

pdoom1's own reason, independent of pdoom-data's (which is that 756 of 1,129 arXiv
descriptions are literally `"1 Introduction\n---------------"`): **1,174 of 1,194
records never reach a decision window.** Translating them buys grey feed lines in a
second language.

**Correction the room needs.** The agenda says: *"the player guide lives in
`pdoom1` but publishes through the website, so its translation has two owners."*
Checked, and it does not:

- The player guide is **static text inside a Godot scene**,
  `godot/scenes/player_guide.tscn` (+ `godot/scripts/ui/player_guide.gd`). It is
  not a document.
- It is **not** one of the six pull targets listed in `docs/copy/README.md`. The
  website does not publish it.
- It is also currently **wrong** -- `docs/design/FRESH_EYES_TEARDOWN_2026-08-06.md:281`
  records it as *"static scene text, apparently untouched"*, teaching retired
  controls and a stale win condition, partially repaired by `#1136` yesterday.

**So the guide has ONE owner, not two, and its real problem is that it is stale in
English.** A3's two-owner framing dissolves.

**Bigger correction:** the agenda frames A3 as corpus-versus-UI-strings, which
presumes pdoom1 can localise UI strings. **It cannot.** Measured: zero `tr()` calls
in `godot/scripts/`, no `.translation` files, no `locale/` directory, no
`internationalization` block in `project.godot`. **pdoom1 has no localisation layer
of any kind.** Every player-facing string is a literal in a scene or a script.

The real A3 question is therefore not "which content" but **"who builds the i18n
layer, and when"** -- and until that exists, both answers cost the same, namely
everything. pdoom1 votes corpus-out and asks that A3 be re-scoped rather than
answered.

**Failure mode:** if a partial corpus translation is wanted for marketing rather
than for play -- a Chinese-language landing page showing real events -- that is a
website surface, needs no i18n layer in the game, and my "corpus out" vote would
have blocked something cheap for the wrong reason.

### B1 -- one file or two projections? **VOTE: two projections, and the producer must stamp identity.**

Two projections, for the reason the agenda already states: the consumers want
nearly disjoint things. pdoom1 reads 9 of 13 fields; `sources` (present on all
1,194), `tags`, `impacts[].condition` (3,636 entries, all null) and `source_id`
are **never accessed anywhere in the tree** (`#1102`).

pdoom1's addition, which is a condition rather than a preference: **whatever the
producer emits must carry a source commit, a record count, and a generated-at
stamp.** `#1115` lists the four things a working re-sync needs and this is the one
that makes the other three checkable. Without it, "which corpus is this build
running" is unanswerable -- which is exactly the state pdoom1 is in today, holding
a snapshot from `88a71959` that it can only identify by archaeology.

**Failure mode:** two projections means two `--check` gates, and a gate nobody
watches is this repo's signature defect. If only one projection has a consumer
that fails loudly on drift, the other one rots quietly and we learn about it in
eight months, the way `sync_icons` was learned about.

### B2 -- promotion pass now, or wait for the producer? **VOTE: GO NOW. And the agenda's bind is not real.**

This is the item where pdoom1 bears the cost and the sister seats split
(`pdoom-data`: GO with a snapshot id; `pdoom1-website`: WAIT). pdoom1 votes GO, and
brings the fact that dissolves the disagreement.

**The agenda says:** *"pdoom1 is promoting events out of the same corpus
`pdoom-data#62` is refreshing ... Promote now and you promote against a snapshot
that cannot be refreshed without redoing the work."*

**Measured: the promotion pass does not edit the corpus.** `#1137` ships
`godot/data/events/overrides/promotion_pass_2026_08.json` -- 214 lines of
**deep-merge overrides keyed by original record id**, applied at load over an
untouched `historical_events.json`. The override README states the principle
explicitly: *"pdoom-data owns facts and defaults; pdoom1 owns balance tuning via
overrides. Never modify pdoom-data for game balance."*

So a corpus refresh does **not** invalidate the promotions. It invalidates only
overrides whose key **disappears** from the refreshed corpus -- and `#1137`
already ships a red test for exactly that
(`test_event_retime.gd`: *"asserts every override key in every override file
exists in the corpus"*), written because `example.json` shipped two dead keys for
months and nothing said so.

**The redo cost of promoting now is therefore not "the work", it is "the subset of
24 override keys pdoom-data renames or deletes", and it is already guarded by a
test that fails red.** That is a very different trade from the one the agenda put
in front of the website seat, and I suspect its WAIT vote would move if it had this.

pdoom1 also **accepts pdoom-data's condition** -- record the snapshot identity
(corpus commit sha + record count) alongside the promotion pass. It is cheap, it is
`#1115` item 4 anyway, and it converts "which promotions were made against stale
inputs" from a memory into a query.

**Failure mode:** if the refresh renames ids at scale rather than in ones and twos,
24 hand-authored overrides with rewritten titles and descriptions become 24
orphans, and the red test tells you *that* they broke without telling you what they
should now point at. Above roughly 8 of 24 broken keys, WAIT was the better call.

### B3 -- where does the shared vocabulary live? **VOTE: mint-site ownership, with `coordination` holding a GENERATED index of pointers -- not the definitions.**

Both sister seats are half right and the disagreement is resolvable.
`pdoom1-website` is right that coordination holds no vocabulary of its own and
would become a fourth variant. `pdoom-data` is right that a definition living in
one sister repo forces the other two to copy, and `coordination#15` says what a
copy becomes.

pdoom1 has the empirical resolution because it made both mistakes in the same
directory:

- `docs/game-design/decisions/README.md` -- a **hand-maintained index** of the
  ADRs. CLAUDE.md tells every agent in this repo, in writing, *"trust the files,
  the index is stale."*
- `docs/game-design/DQ_INDEX.md` -- a **generated index** of the same class of
  content, regenerated by `scripts/generate_dq_index.py`, with a `--check` that
  blocks a stale commit in pre-commit.

**Same repo. Same directory. One rotted, one cannot.** The difference is not where
it lives; it is whether it is derived and gated.

So: the definition lives where the term is **minted** (the website's test is the
right one -- *if you cannot name which repo changes behaviour when the definition
changes, the term is not yours*). Coordination holds **a generated index of which
term is minted where**, regenerated from the three repos, `--check`-gated, never
hand-edited. That is a registry that cannot drift, rather than a fourth glossary
that will.

**Failure mode:** a generated index needs a machine-readable source in each repo,
which is three new files and three gates that do not exist. If the estate will not
pay that, the honest fallback is coordination hand-holds it and everyone accepts
it will be stale -- and CLAUDE.md's *"trust the files, not the index"* line becomes
the estate's rule instead of one repo's scar.

## 3.3 The question that is not on the agenda

> *"how we metabolise things overall. Is there any philosophy that guides us on
> this?"*

Both sister seats answered with a rule about **who may write**:

- `pdoom-data`: *a repo publishes into a zone it owns; nobody writes into a zone
  they do not own* -- plus push-the-signal / pull-the-content.
- `pdoom1-website`: *every cross-repo transport is initiated by the consumer, reads
  a published artefact, and the consumer may never author a value in the
  producer's vocabulary* -- with a falsifier for takedowns.

Both are good and pdoom1 endorses both. **pdoom1's candidate is the missing half,
and it is not about direction at all.**

> **Direction is the cheap half. The binding rule is that a consumer must be able
> to state the IDENTITY of what it last consumed, and must fail loudly when it
> cannot. A transport that cannot report a bad state is indistinguishable from one
> that is not running.**

The evidence is that **pull did not save us**. Every cross-repo path in this estate
that broke, broke by *succeeding*:

| What broke | Direction | How it reported |
|---|---|---|
| `sync_from_pdoom_data.sh` | pull | never completed a run in its life; said nothing (`#1115`) |
| `sync_icons()` (website) | pull | reported **success** on every scheduled run for ~8 months while doing nothing |
| `historical_events.json` | pull, once, by hand | 42 un-redacted addresses sat in a shipped file because nobody could tell which corpus the build carried (`#1106`) |
| the CI test gate | n/a | reported **green** while running **zero tests** (`#640`, ADR-0017) |
| `apply_review.py` | n/a | reported 807 confident keeps, 75% of which could not move (ADR-0019) |

**Not one of those is a direction failure. Every one is an identity failure.**
Nothing travelled with the payload saying what it was, so nothing could say it was
wrong.

This unifies four agenda items into one missing artefact:

- **A1** cannot deliver because pdoom1 cannot name what it consumed (`#1115`).
- **A2 bit 2** is the same field at asset scale -- `origin` is the identity of an
  image.
- **B1** needs the producer to stamp a source commit and record count.
- **B2**'s resolution, which `pdoom-data` reached independently, is *record the
  snapshot id*.

Same missing thing, four costumes. **The estate's metabolism rule should be: the
payload carries its own provenance, or the consumer refuses it.** Absent field ->
error, never a default. That is the rule that would have caught all five failures
in the table; "pull" catches none of them.

Convergence note for the post-mortem: `pdoom-data` reached "record the snapshot id"
on B2 independently, from its own zone model. That is two seats arriving at
provenance-travels-with-payload from opposite directions, before Phase 2. Worth
more than either statement alone.

**Falsifier, so this is testable rather than pretty:** if a cross-repo transport
exists in this estate that carries no identity stamp and has nonetheless never
silently drifted, the rule is over-strong.
`.github/workflows/sync-design-tokens.yml` is the obvious candidate and pdoom1 has
not checked it. **Someone should, before this is adopted as anything.**

## 3.4 Voice

`#31` invites a voice and warns against performing one. pdoom1's is not chosen; it
is what the last month of this repo's issue log sounds like.

**This is the seat that ships, and then finds out it was wrong.** Not
occasionally -- as its characteristic mode. This week alone: a test gate that
reported green while running zero tests; a review tool confidently reporting 807
keeps of which three quarters could not move; a sync script that read directories
that did not exist and wrote directories that did not exist and never told anyone;
an example file teaching the override format that was wrong in two of its three
examples for months; a player guide teaching a game that no longer exists.

The pattern is not incompetence, it is that **everything here fails by looking
fine.** Which is why every vote above carries a failure mode: a position with no
stated way to be wrong is exactly the artefact this repo keeps discovering it
shipped.

And it is why pdoom1 spent its prep re-deriving the agenda's own numbers instead of
arguing with its conclusions. Three of the figures did not survive. **That is not a
criticism of the agenda -- it is the house specialty, applied to a friend.**

---

## Appendix -- how to reproduce the A1 numbers

Every count in section A1.2 comes from `godot/data/historical_events.json` on
`main` at `78be0370` (a JSON object keyed by event id, 1,194 entries) plus these
code sites:

- flavour gate: `godot/autoload/event_service.gd:404-410`
- rarity branch selection: `godot/autoload/event_service.gd:326-349`
- shipped `min_turn` = `eligibility_start`: `godot/autoload/event_service.gd:378`
- poison-key test: `godot/autoload/event_service.gd:446`
- start-year filter: `godot/scripts/core/events.gd:111-113`
- the only gates `should_trigger` applies to a `"random"` event:
  `godot/scripts/core/events.gd:173-190`
- per-turn cap: `godot/data/balance/defaults.json:6`
  (`events.max_new_events_per_turn: 2`)
- curve values: `godot/data/events/balancing/rarity_curves.json` (main) and the
  same path on branch `feat/event-retime-and-promotions` (`pdoom1#1137`)

`eligibility_start` for a rare record is
`max(1, (year-2017)*turns_per_year + 1 + rare_spread_turns - eligibility_window_turns/2)`;
for a common record it is `max(10, (year-2017)*turns_per_year + 1)`. Since
`rare_spread_turns == eligibility_window_turns/2` in both the 52/yr and the 12/yr
variants, the rare expression collapses to `base_turn` and the delta is entirely
the `common` floor of 10.
