# Workshop 3 -- Three-Day Structure (Mon 2026-07-27 .. Wed 2026-07-29) + Prep Pack

> Status: RUNNING ORDER for the W-3 block (issue #811), RESTRUCTURED 2026-07-26
> evening at Pip's call: the single Wed 07-29 workshop becomes a THREE-DAY
> structure (table below). The blow-by-blow schedule lives in
> `RUNSHEET_2026-07-27_to_29.md`. Blocks R0-R5 are the agenda, now
> RE-PARTITIONED across Monday and Wednesday by one gating rule (an item is
> Monday iff its ruling gates Tuesday's build fan-out). Sections 0-6 further
> down are the original prep pack (2026-07-23) that fed this agenda --
> BACKGROUND, partially superseded; read the reconciliation note at the head of
> the appendix before trusting a detail there.

## The three days (pinned 2026-07-26 evening, anniversary-driven)

Pip's first GitHub issue on this project was 2025-07-30. Thu 2026-07-30 is the
one-year anniversary, and W-4 lands on its eve -- the restructure exists so the
anniversary week SHOWS what a year produced: decide Monday, build Tuesday,
review + plan the next epoch Wednesday.

| Day | Name | What happens |
|---|---|---|
| **Mon 2026-07-27** | **W-3a** | The RATIFY block (`WS3_FINISH_OR_DROP.md`'s 5 questions) + build-gating decisions ONLY: early-game decisions design, effort-economy scheduling (#613 keystone), tile-grid addressing ruling, office-view real-estate/camera ruling. ~5 focused hours AROUND Pip's day-job CEO chunks. |
| **Tue 2026-07-28** | **BUILD DAY** | Fable orchestrates the implementation fan-out of Monday's rulings + the in-flight art re-base. Pip mostly ignores it: CEO chunks + drive-by approvals only (the proven 27-PR co-orchestration mode). |
| **Wed 2026-07-29** | **W-3b / W-4** | Colour architecture circle-back, interior-decorating math + office-fullness, league/content cadence + Friday league prep, REVIEW of Tuesday's builds, next-epoch planning. |

Standing constraints (baked into the runsheet): 3x 2-hour day-job CEO chunks
across Mon+Tue, exact times TBD by Pip -- schedules show them as MOVABLE
placeholders, with workshop time as morning + late-afternoon blocks, hard
stops, and a movable middle. 30-min feed-triage slots Mon+Tue+Wed (Manifund
launched + 20 contacts messaged Sunday night -- inbound expected). Energy
discipline: Sunday was enormous; hard stops, no heroics. Fri 2026-07-31 17:30
Rektango remains the weekly anchor.

## The frame -- this is a CONVERGENCE workshop, not an exploration

WS-1 and WS-2 were divergent: generate options. WS-3 is different. The design
proposals commissioned this week ARE the divergence, done async and off the clock:

- `WS3_FINISH_OR_DROP.md`
- `RESEARCH_STREAMS_PROPOSAL.md`
- `OFFICE_ECONOMY_PROPOSAL.md`
- `ENDGAME_VIOLENCE_PROPOSAL.md`
- `CAPABILITY_UPLIFT_SCAN.md`
- `OLD_ISSUE_TRIAGE.md`
- (plus Pip's two raw captures: `SEED_RIVAL_AND_DEVELOPMENTS.md`, `SEED_ENDGAME_AND_VIOLENCE.md`)

So WS-3's job is NOT to hunt for more ideas. It is to CARVE the meat already on the
table into build-ready lanes. The meat is decided in the room; the exploring already
happened in the proposals.

**The one discipline that makes it converge:** every agenda item exits with a RULING
-- ship / kill / defer -- never "let's think more". A genuine can't-decide is
DEFERRED with what is needed to unblock it (pendingness marked, not pretended-
resolved -- the no-lies standard applied to the workshop itself). If a block starts
going exploratory again, that is the signal a proposal did not give enough to decide;
capture THAT gap and defer, do not re-open divergence mid-workshop.

**The standing lens (carried from the Theme A ruling, 2026-07-23):** "crisp parts,
brutal decisions" (the Factorio / MaRo / Rams thesis). The game's hardness lives in
the DECISIONS, not the INTERFACE. For every mechanic ruled in, ask: does it add
INTERFACE complexity (reject / simplify) or DECISION complexity (the only kind that
earns its keep)? Claude runs this as a standing MaRo-Rosewater / Rams check across
every block.

## Running order -- Monday 2026-07-27 (W-3a): ratify + build-gating decisions

Gating rule: an item sits on Monday IFF its ruling gates Tuesday's build
fan-out. ~4.5h of blocks, fitted around the CEO chunks (see the runsheet).

| Block | ~Time | What happens | Exit artifact |
|---|---|---|---|
| **R0 -- Frame** | 20m | State the win condition for the three days: by Wednesday close every candidate mechanic is a scoped, Epoch-tagged build lane OR explicitly killed/deferred with a reason -- nothing leaves in "exploratory" status. Monday's narrower bar: every build-gating item exits with a RULING so Tuesday can fan out. | the decision queue |
| **R1 -- Finish-or-drop the inheritance (THE RATIFY BLOCK)** | 45m | Walk `WS3_FINISH_OR_DROP.md`'s five ratify-in-minutes questions against the WS-2 ADR status table (Appendix Section 2). Each unbuilt/half-built WS-2 decision (0010 adoption, 0011 workstreams, 0014 conference-shape, 0016 league pipeline) + the ADR-0015 data-strip trap: ship / kill / defer. Clear the deck before adding new meat. | kill-list + keep-list |
| **R2 -- The substrate + effort-economy scheduling** | 60m | `RESEARCH_STREAMS_PROPOSAL.md` (= the ADR-0011 L2 workstream substrate). Lock or reject the compute / non-compute stream model + the polyvirate axis set. Then the #613 keystone scheduling call: MINIMAL-now vs MODERATE-when, and when the legacy AP pool dies. FOUNDATIONAL: the rival RPS and the endgame both hang off the axes, so protect this timebox above all others. | ADR: research substrate + axes; #613 schedule |
| **R3a -- Office economy + spatial rulings** | 45m | `OFFICE_ECONOMY_PROPOSAL.md` (near-term money loop / upkeep; the office-era cost) PLUS the two spatial calls that gate the office-view build lanes: the **tile-grid addressing ruling** and the **office-view real-estate/camera ruling** (sandbox v3 prototypes are the demo input). Also the early-game decisions design from #811 item 1 (offices 1-of-3, np/fp depth, first-funding modes, scouting actions, onboarding->scouting handoff) -- Pip's content calls. | rulings Tuesday builds against |
| **R4 -- Scope + prioritise into lanes** | 45m | Every Monday keep/build ruling -> a lane: size (S/M/L), dependencies, Epoch target (v0.14 vs v0.15), which carve-seam it lands on (the monolith is now carved to ~1940 lines; the controllers exist). This emits Tuesday's build queue; the roadmap epoch-assignments deferred as "pending WS-3" get their first real fill here, finished Wednesday. | Tuesday's lane manifest |
| **R5 -- Emit + commit** | 30m | Fable fans out overnight: one build-brief agent per locked lane -> `BUILD_BRIEF_*` docs; Monday's ADRs drafted; DQ index regenerated (`scripts/generate_dq_index.py`); all committed so Tuesday starts from briefs, not memory. | stack of build-ready briefs |

## Tuesday 2026-07-28 -- BUILD DAY (not a workshop)

No agenda blocks. Fable runs the fan-out of Monday's rulings + the standing
art re-base lanes; Pip does CEO chunks + drive-by approvals only. The runsheet
carries the anticipated build queues.

## Running order -- Wednesday 2026-07-29 (W-3b / W-4): react, colour, cadence, next epoch

| Block | ~Time | What happens | Exit artifact |
|---|---|---|---|
| **W0 -- Review Tuesday's builds** | 60m | Merge/park call per lane PR; anything half-done gets an explicit in-flight status, not silence. | merged lanes + park-list |
| **R3b -- Endgame + violence (+ cat doom-oracle)** | 60m | `ENDGAME_VIOLENCE_PROPOSAL.md` (the far tent-pole). The sharp ruling: is military a genuine winning branch or another desperation-trap? And what fires "violence arrives"? Plus #811 item 3: the cat as a higher-resolution doom instrument (earn resolution, no printed deltas; rival-steal modifier stays HELD per Pip's T6 ruling). | rulings + endgame/violence ADR |
| **W1 -- Colour architecture circle-back** | 45m | The deferred colour ruling, with the sandbox v3 doom-glow + overlay-compositing prototypes as the demo input. | colour architecture ruling |
| **W2 -- Interior-decorating math + office-fullness** | 45m | How furniture/decoration accrues, what "full" means for an office tier, how fullness reads on screen -- downstream of Monday's tile-grid + real-estate rulings and Tuesday's office-view lanes. | decorating/fullness model |
| **W3 -- League/content cadence + Friday league prep** | 45m | Ratify `RELEASE_AND_LEAGUE_CYCLE.html` (two-cadence model + two-league idea, #811 item 4); the ADR-0016 first-cycle date question lands here; prep the Fri 07-31 league target (seed rotation + notes). | cadence ratification + Friday plan |
| **W4 -- Next-epoch planning + emit** | 60m | Finish the lane manifest + roadmap epoch assignments (v0.14 "Per-tick & People", Fri 08-07); WORKSHOP_2_BACKLOG parked-items updated; remaining ADRs written; DQ index regenerated; all committed. The anniversary beat: one year from issue #1 (2025-07-30) -- name what the year produced. | lane manifest + roadmap epochs |

Two cross-cutting threads, not their own blocks:
- **`CAPABILITY_UPLIFT_SCAN.md`** is the FEASIBILITY lens -- keep it open through R2-R4
  and gut-check every "build" ruling against what the engine can actually carry near-term.
- **`OLD_ISSUE_TRIAGE.md`** is housekeeping -- its consolidate/close calls fold into R1
  (drop) and R5 (commit); it does not need floor time.

## Idealised outputs (the things that feed build lanes)

1. **Decisions ledger** -- every mechanic: ship / kill / defer + reason. ADRs for the
   big three (substrate, economy, endgame/violence). Confirm the ADR numbering before
   assigning the range (see the workshop-numbering note in the appendix).
2. **Lane manifest** -- scoped, prioritised, Epoch-tagged, dependency-graphed. The
   single source build agents execute from.
3. **Build briefs** -- one per greenlit lane, agent-executable (`BUILD_BRIEF_*`).
4. **Updated roadmap** -- real epoch assignments filled in (closes the "pending WS-3"
   gap in ROADMAP.md).

## Fable orchestration pattern

Per the orchestration lessons (push-per-step, narrow fan-out, tier the model): Fable
does NOT pre-spawn a fleet. It runs the agenda WITH Pip and spins ONE scoped agent at
each convergence point -- an ADR-drafter when a decision locks (R2-R3), then the only
real fan-out at R5 (build-brief-per-lane), which is safe because by then the targets
are decided, not speculative. The inversion from WS-1/2: the fan-out moves from the
FRONT (explore) to the BACK (emit), because the exploring already happened in the
proposals.

## What is explicitly OUT of WS-3 (so it stays convergent)

- **Onboarding / legibility build (old Theme A).** It is presentation-tier and
  hotpatch-safe (advisor persona + lever-pointer, #801 / ONBOARDING_STORY_DESIGN.md).
  It does not need a workshop block -- it runs as hotpatch execution. Its LENS (crisp
  interface, brutal decisions) survives as the standing check above. Pull it into a
  block only if Pip wants to re-open it.
- **Re-designing anything already ruled.** The workstream substrate is RULED
  (ADR-0011); R2 SCOPES and SCHEDULES it, it does not re-litigate it.
- **DQ-22 rival aggro deep-build**, if R3's endgame work does not naturally reach it
  -- it can stay a later beat rather than being forced into this day.
- **New scope stacked on unbuilt ADR-0010/0014/0016** -- R1 is finish-or-drop only.

## Pip's pre-read leanings (2026-07-25, banked before the workshop)

Captured after Pip read the six proposals. These are LEANINGS to enter the room with,
not rulings (no-lies: priors, not decisions) -- except the polyvirate, which Pip locked.

- **Polyvirate: LOCKED.** Not a triumvirate. [PIP] "polyvirate for definite" -- a fixed
  small race-set (StarCraft-style) would invite an all-in-on-one-race imbalance; more
  axes keeps it harder to map / min-max.
- **Military branch (R3 endgame): build-for-both.** [PIP] "both / neither / a third,
  more subtle thing, but build for both of these." -> engineer the substrate so the
  military path's moral valence (genuine branch vs desperation-trap vs subtle third) is
  a TUNABLE, not a hardcode. Do not resolve the morality in code; keep it a dial.
- **Research streams (R2 substrate): the centre of gravity.** [PIP] "where the meat of
  our economic sinks are ... the best possible version we can design will override
  convenience or speed ... care, consideration, and deliberate iteration, so let's get
  it built and in." Pre-committing ~40 of 100 effort-units across the whole body of work
  to this. Implication: R2 gets the deliberate-iteration treatment, not a fast MVP.
- **Build ~90% of the proposals, mostly as they emergently unfold.** [PIP] Little math
  needed to kill the vestigial old-engine translation + early action-point systems;
  framing the game as DECISIONS + ATTENTION (not AP) is the individuating move -- [PIP]
  "not sure how many other bureaucracy simulators play to this point."
- **Inject weird.** [PIP] looking forward to drawing on his esoteric + colourful literary
  background -- the CROSSOVER / Schmekels / alternate-timeline register
  (SEED_ENDGAME_AND_VIOLENCE) is the licensed home for it.

---

# Appendix -- original prep pack (2026-07-23), partially superseded

## Reconciliation -- what changed since this pack was drafted

The prep pack below is preserved for its analysis (especially the Section 2 WS-2
ADR-status table, which is the R1 ammunition). But several of its OPEN QUESTIONS are
now RESOLVED -- do not treat them as live:

- **"v0.12 vs v0.13 anchor" / "which milestone does WS-3 serve" (Section 5 headline):
  RESOLVED.** The quarterly model was retired for monthly Themes; v0.13.1 is live;
  WS-3 is a deep-mechanics workshop feeding the v0.14+ Epochs, not a milestone-anchor
  choice. See ROADMAP.md + RELEASE_NOMENCLATURE.md.
- **"No WS-3 mechanics session is scheduled" / "the Friday unknown" (Section 5):
  RESOLVED.** WS-3 is scheduled Wed 2026-07-29 (issue #811), separate from the old
  Friday #758 slot.
- **"Office economy proposal does not exist" (Theme B gate, Sections 3b/5/6):
  RESOLVED.** `OFFICE_ECONOMY_PROPOSAL.md` now exists -- it is R3's input.
- **"Build-vs-ladder version split must land first" (Theme D / Section 3d): SHIPPED.**
  build version vs ladder version (L2) is live; board key is (seed, ladder_version).
- **main_ui monolith:** CARVES 1-6 have landed (PlanController, SubmenuController,
  HiringPanelController, TravelPanelController, ActionBarRenderer, EventResultPresenter);
  main_ui.gd is ~1940 lines. New WS-3 UI lands on these controllers, not the monolith
  (see MAIN_UI_SEAM_MAP.md).
- **Workshop numbering** (Section 6) is still worth confirming before the ADR range is
  assigned -- carried forward as an R0/R5 checklist item.

The A/B/C/D "candidate themes" framing in Section 4 is SUPERSEDED by the proposals and
the R0-R6 running order above; it remains as the reasoning trail that produced them
(Theme C -> RESEARCH_STREAMS, Theme B -> OFFICE_ECONOMY, Theme A -> the standing lens,
Theme D -> the shipped version split).

---

## 0. Steering docs added since drafting (WS-3 lanes MUST read)

Added 2026-07-25 after the prep pack. Any WS-3 build lane reads these before
starting so refactors and new UI land along agreed seams, not on the monolith:

- **`docs/MAIN_UI_SEAM_MAP.md`** -- the incremental de-monolithing plan for
  `main_ui.gd`. CARVE 1 (R4 planning/attention/queue -> `PlanController`) is
  slated for the quiet pre-WS-3 window and is the prerequisite for the per-tick
  spike. CARVE 2 (the 7 copy-pasted submenus -> one data-driven
  `SubmenuController`) triggers the first time a lane adds a panel -- build the
  generic component, do NOT copy-paste an 8th submenu. All carves are non-forking
  and test-gated.
- **`docs/game-design/SEED_RIVAL_AND_DEVELOPMENTS.md`** -- captured design seed for
  the rival system + narrative-pressure layer ("Developments" umbrella,
  "Sightings" rival subtype). Feeds the DQ-22 rivals cluster (Theme E / the
  midgame lane). Note the structural synergy: the rival is revealed on the same
  "go outside to recruit" surface as the people & money spine (#833).
- **`docs/adr/0004-self-describing-data.md`** -- data files declare their own
  schema; tooling never infers schema from directory. Relevant to any lane adding
  new data files (events/actions): self-declare the type.

---

## 1. Purpose + how these workshops work

Pip runs periodic **mechanics-design workshops**. Each produces a batch of ADRs
(Architecture Decision Records) in `docs/game-design/decisions/`, which later
agents/build-lanes implement. The pattern so far:

- **Workshop 1 (WS-1)** -> ADR-0001 .. ADR-0008. The load-bearing spine:
  spending-buys-sight (0001), scoring = turns-survived / flows-only (0002),
  liability ledger (0003), SA channels + lead time (0004), emergent waves /
  seed schedules (0005), replay-artifact backend (0006), alliances / third
  client (0007), deferrals + rejections (0008).
- **Workshop 2 (WS-2)** -- EXECUTED 2026-07-12; ADR-0009 .. ADR-0016 merged via
  PR #611 (per repo memory). Plan-months / two speeds (0009), adoption routing
  (0010), effort economy (0011), event-response taxonomy (0012), cost-of-debt
  engine (0013), conferences / presence (0014), no-printed-doom-deltas (0015),
  league metabolism (0016). ADR-0017 (anti-hollow test strategy) was added
  later (2026-07-22, out of a testing workshop, not WS-2 mechanics).

Convention worth preserving in WS-3: WS-2 also produced a **parked-items
register** (`WORKSHOP_2_BACKLOG.md`) and a **generated DQ index**
(`DQ_INDEX.md`, regenerated by `scripts/generate_dq_index.py`; never
hand-edited). WS-3 should feed the same two artifacts.

Naming caution: `DESIGN_PHILOSOPHY.md` carries a `(2026-07-13, workshop #3)`
quote tag on the league-metabolism principle. That tag appears to refer to a
Fable *interview* session numbered 3, NOT the mechanics WS-3 being scoped here.
Confirm the numbering with Pip so the ADR batch is labelled consistently.
[INFERRED]

---

## 2. Status of prior decisions (WS-2 ADRs: landed vs decided-but-unbuilt)

Verified by grepping `godot/scripts/`, `godot/autoload/`, `godot/data/`,
`godot/tests/`. "LANDED" = a working system in core; a data stub / comment /
test-only reference does not count.

| ADR | Decided | Status in code | Drag on WS-3? |
|---|---|---|---|
| 0009 plan-months / two speeds | Turn=month; evaporating reserve; response windows; durations | **LANDED** -- `month_plan.gd`, `month_controller.gd` | No |
| 0010 adoption routing | World/rival doom bends only via research->paper->socialization->adoption | **MOSTLY NOT BUILT** -- own-lab `safety_absorption` exists in `doom_system.gd`; no adoption pipeline ("adopt" only in comments). Lane L3 (#614) open | YES -- a thesis pillar unbuilt |
| 0011 effort economy | Delete global AP; typed founder hours; workstreams; managers; researcher lanes x appetites x quirks | **PARTIAL** -- lanes/appetites/quirks + appetite-promises-as-ledger landed; founder-hour typing, **workstreams**, manager-shields NOT built. Lane L2 (#613) open | YES -- biggest single drag |
| 0012 event-response taxonomy | 4 classes; DEFER mints ledger | **MECHANISM LANDED** (`event_tiers.gd`, `window_resolver.gd`); event **content** unclassified (only defaults in `balance/defaults.json`). Lane L4 (#614) owes content | Partial (content only) |
| 0013 cost-of-debt engine | One pricing engine for all liabilities | **LANDED** -- `finance_engine.gd` (`price()`, `generate_offers()`, `accept_offer()`); caveat: typed rep / org_type not first-class state yet (prices off scalar reputation) | No (inputs stubbed) |
| 0014 conferences / presence / location | Founder-vs-delegate; contacts-as-receivables; presence=SA channel; seed-timeline scheduling | **NOT BUILT (ADR shape)** -- only the pre-ADR #468 travel system (`conferences.gd`, `paper_submissions.gd`) exists. Lane L3 (#614) open | YES |
| 0015 no printed doom deltas | No definition carries literal doom; computed each tick; single authority | **ENGINE LANDED** (`doom_system.gd` streams + single authority #638); data migration INCOMPLETE -- `data/events/core_events.json` still ships ~40 literal `"doom": N` fields, inert only because clobbered at resolve | Partial (latent trap) |
| 0016 league metabolism | Monthly world-update packs; game trails reality by 1 month; 2017 start | **NOT BUILT** -- only the 2017 anchor (`DEFAULT_START_YEAR = 2017`); no world-update-pack pipeline. Largely ops/content, not engine | YES (ops/content) |
| 0017 anti-hollow test strategy | Load-time smoke + property invariants | **LANDED** -- `test_smoke_load_all.gd`, `test_property_boot_invariants.gd`, `test_property_determinism.gd` | No |

**Decision-for-Pip 2A:** Four WS-2 decisions are still largely unbuilt (0010
adoption, 0011 workstreams, 0014 conference-ADR-shape, 0016 league pipeline).
These are DRAG: WS-3 should not stack new design on top of them. For each,
WS-3's first job is *finish, or formally drop/downscope*, not add.

**Correction (2026-07-27, R5 emit):** the table above originally read "Lane
L3 (#615)" in both the 0010 and 0014 rows. Verified mapping per
`WS3_FINISH_OR_DROP.md`: **L3 = #614** (adoption/papers/conferences --
ADR-0010 + ADR-0014), **L4 = #615** (event taxonomy). Both rows fixed above.

**Decision-for-Pip 2B (latent trap):** ADR-0015's data strip is unfinished --
the fiction still says "-3 doom" and 40 literal fields survive as inert
no-ops. Any refactor that drops the resolve-clobber silently resurrects printed
doom. Fold the data-strip into a WS-3 cleanup errand or ratify the current
"inert but present" state explicitly.

---

## 3. Accumulated design questions since WS-2 (grouped)

Sources woven in: first external playtest (Rick M), the newer design docs, and
the open DQ register. Issue numbers verified via `gh`.

### 3a. Early-game legibility / onboarding-as-mechanic
- **#801** (playtest #1): "lots of information ... not a lot of direction ...
  trial and error just to find out what I'm meant to do. I love the concept."
  Diagnosed in `ONBOARDING_STORY_DESIGN.md` as TWO gaps: (1) cold-open overload
  / no narrative frame; (2) **no LEVER legibility** -- player knows the goal
  (doom->0) but not which action moves the needle. Onboarding's real job =
  teach the `action -> effect` mapping, not re-explain the objective.
- Design already ruled directionally in that doc: advisor persona (Component 3)
  that speaks the cold-open AND a first-turn lever pointer while the named
  button glows; NOT a forced tutorial. Explicitly PRESENTATION-only -> does not
  fork the ladder -> hotpatch-safe.
- **#802** (playtest #1): music repetition fatigue over a long sitting ("start
  to break my mind"), but "actually digging the music" earlier -- so it needs a
  mute/skip controller + track variety + doom-decoupled rotation. Audio-only,
  non-score. Minor mechanically; include only as an onboarding/UX-comfort note.
- Adjacent DQs: **DQ-18** (early game = scouting / populating the board,
  EXECUTED), **DQ-19** (character-creation surface, PRIORITISED -- does founder
  background type starting channels? ex-academic->research-sight, etc.).

### 3b. Office economy / floor-space / early progression
- **#791**: force a small early **lease** decision with starting money;
  bedroom/basement start HARD-CAPS hires; lease unlocks more hires + capability;
  rent falls due periodically as a predictable AP/cash sink. Progression thesis:
  "first unlocks small-now, bigger-over-time; switching costs."
- **#793**: office-floor render bugs (all staff same sprite, oversized) -- art,
  not mechanics, but signals the office-as-place surface is live in the UI.
- NOTE: the prompt referenced an `OFFICE_LAYER_PROPOSAL.md`. **No such file
  exists** in `docs/game-design/` (verified). The office-economy design is
  currently carried only by issue #791 + scattered notes -- i.e. it is a
  candidate WS-3 topic precisely because it is NOT yet written up. [VERIFIED
  ABSENT]
- Ties into ADR-0011: rent/hire-cap are the concrete early face of the effort/
  finance economy.

### 3c. Hiring depth / stitch + research-idea -> paper pipeline (the ADR-0011 L2 gap)
- **#789**: hiring stitch -- onboarding sub-actions (laptop/mentoring) as
  AP-sink PROMPTS on offer-accept; interview = schedule -> happen with a
  notification. Data (`researcher.gd` laptop_done/visa_done/mentoring_done)
  exists; needs surfacing as costed actions. Gameplay change -> forks ladder.
- **`RESEARCH_IDEA_PAPER_PIPELINE_GAP.md`** (2026-07-22 analysis, ~95%
  confident, verified in code): the promised chain onboard -> **direct at a
  specific idea** -> devote time -> **accrue with specificity** -> **paper
  carrying that idea** is FICTION for links 2/4/5. Today research is a single
  fungible scalar dripped by an undirected per-turn RNG roll; there is no Idea
  object; a "paper" is either a bare counter (`state.papers += research/100`) or
  a player-labelled wrapper whose topic is a last-second dropdown decoupled from
  the work. This IS the ADR-0011 "workstream substrate" (ruled, unbuilt).
  - Options the doc scopes: MINIMAL (per-researcher `focus_topic` + topic-tagged
    accrual + idea-carrying papers; days-scale, fast-follow) -> MODERATE (full
    `Workstream` object + assignment UI + agenda drift; the L2 build, weeks) ->
    AMBITIOUS (Idea lifecycle idea->hypothesis->result->paper). Its
    recommendation: MINIMAL now, MODERATE as the scheduled L2.
- **DQ-24** (attention-demand taxonomy) is already RULED (5 demand categories ->
  absorbing hire-roles; founder = universal generalist). This is the hiring
  build's demand-model -- ready for a build brief, awaiting the L2 substrate.
- **Burnout outcome model** RULED (implementation home = L2). **DQ-15**
  researcher archetype roster still SEEDED (Pip owes 3-5 archetypes) -- a
  dependency for agenda-driven flavour.

### 3d. Meta / ladder integrity + versioning
- **`DISTRIBUTION_AND_PATCHING.md`** (2026-07-22): the **build-vs-ladder version
  split**. Today the board key is `(seed, full game_version)`, so EVERY patch
  forks the leaderboard -- a UI-only pck splits the board and scatters testers.
  Required: a **build version** (bumps every patch) SEPARATE from a **ladder
  version** (bumps only on gameplay/scoring change); the patch manifest declares
  per-patch whether it forks the ladder. Doc says this must land BEFORE the
  first gameplay hotpatch.
- **#799** (priority:high, hotpatch-48h): anonymous install ping + remote update
  check ("one request, two jobs"); the L2 update-notice from the same doc.
- **`DEPRECATED_SAVE_LOAD.md`** + **DQ-11**: single-slot save/load HIDDEN
  2026-07-21. Open design question Pip raised: make save-scum an INTENTIONAL
  mechanic ("Orb of Regret" / branch-rewind) vs enforce one-uninterrupted-run
  per seed for ladder integrity. A branch mechanic must solve the
  verification-chain restore or mark resumed runs practice-only.
- **DQ-34** (leaderboard disclosure tiers: score vs reconstructable play),
  **#788** (mark dev-mode runs with a visible badge, not exclusion),
  **#763** (nomenclature/pacing: strategic-options unlock at MONTH grain --
  turns-vs-days scoring nomenclature). All feed a coherent meta-integrity theme.

### 3e. Midgame: rivals aggro-threshold (already earmarked for v0.13)
- **DQ-22** (aggro-threshold midgame): rivals develop their own positions until
  the player's visible impact threatens their interests, then active attacks
  begin (litigation, funding cuts, rep attacks, poaching, leak-seeking) -- "the
  sign we're entering the midgame." Backlog tags it an ADR-candidate; **milestone
  "Rivals & News" explicitly schedules a "DQ-22 ADR workshop"**
  (verified via `gh api milestones`). **DQ-12** (rival narrative presence --
  rival still "narratively invisible") is its companion.
- This is the one cluster the roadmap has ALREADY assigned its own workshop. So
  the live question is whether WS-3 == the DQ-22 workshop, or WS-3 is an earlier
  (v0.12) workshop and DQ-22 stays a later v0.13 one.

### 3f. Also-parked, lower priority (name only)
DQ-9 receivables/counterparty (overlaps ADR-0007 alliances, tagged WS-3),
DQ-20 risk pools (insurance/mutualisation as an actor), DQ-23 damper economy
("next workshop beat"; needs a real-history baselining errand), DQ-2 baseline
yardstick, DQ-13 doom-nudge strength (folds into a DQ-8 balance pass).

---

## 4. Candidate Workshop-3 themes

Four coherent groupings. They are NOT all one workshop -- WS-3 should pick 1-2
(see Section 5).

### Theme A -- Early-game legibility + onboarding-as-mechanic
- **Core tension:** teach the `action -> effect` mapping and give first-turn
  direction WITHOUT a forced tutorial / leash. Onboarding as a diegetic advisor
  MECHANIC, not a dismissible popup.
- **Scope:** small-to-medium; mostly presentation (hotpatch-safe), but touches
  the first-5-turns feel. Ratify the advisor-persona + lever-pointer design;
  decide the first lever to teach; decide character-creation surface (DQ-19).
- **Absorbs:** #801, `ONBOARDING_STORY_DESIGN.md`, DQ-18, DQ-19, #802 (as a UX
  comfort note), #722/#721 (tutorial mode / contextual hints).
- **Serves:** milestone "First Contact" (the live playtest pain). This is
  the most time-urgent because it is what the one real tester hit first.
- **BACKBONE LENS -- Design-Philosophy + Crisp/Clarity pass (Pip ruling, 2026-07-23):**
  run WS-3 through one thesis -- **"crisp parts, brutal decisions"** (the Factorio
  model: a ruthlessly clear interface over bottomless optimization). The game's
  suffer-hardness lives in the DECISIONS (the right move is hard, the downstream is
  genuinely uncertain, doom is unforgiving), NOT in the INTERFACE (which must be
  legible enough that a slow, deliberate player -- the "dad archetype", not the
  play-fast Young Gun -- always understands their options and what just happened).
  Rick's "not enough direction" is an INTERFACE failure; the suffer-core is a
  DECISION feature; fixing the first does not soften the second. Assess every
  proposed mechanic against MaRo (Rosewater -- "easy to learn, hard to master";
  New World Order clarity; lenticular design) and Rams ("less, but better"): does
  it add INTERFACE complexity (reject / simplify) or DECISION complexity (the only
  kind that earns its keep)? This is a CROSS-CUTTING lens for all four themes,
  housed in A because legibility is where it bites first. Claude to act as the
  standing MaRo/Rams check across WS-3. Companion principle: sell FORESIGHT as a
  purchased/progressive capability (buy interpretability -> see one hop further
  downstream) rather than a free consequence-oracle HUD -- keeps the interface
  clean while making insight EARNED, and is thematically on-point (AI safety = the
  science of foreseeing consequences).

### Theme B -- Office economy + floor-space progression
- **Core tension:** make early unlocks "small-now, bigger-over-time" with
  switching costs; a forced early LEASE decision; hire caps as a spatial/economic
  constraint that gives the early game shape.
- **Scope:** medium; a genuine gameplay change (forks the ladder). Needs a
  written proposal FIRST (none exists -- see 3b). Couples to ADR-0011 finance/
  effort economy (rent as ledger liability + AP sink).
- **Absorbs:** #791, #793 (art side-effect), DQ-8 balance constants (rent/cap
  magnitudes), part of the Dial-5 attention-scarcity package.
- **Serves:** v0.12/v0.13 progression feel. Risk: thin without the L2 economy
  under it (Theme C).

### Theme C -- Depth: hiring stitch + research -> paper pipeline (the ADR-0011 L2 substrate)
- **Core tension:** the promised "direct a person at an idea, watch it sharpen,
  publish that idea" loop is fiction (verified). The workstream substrate is
  RULED (ADR-0011) but unbuilt; the fungible research scalar is also the
  diagnosed constant-policy exploit. WS-3's job here is to *finish scoping and
  schedule*, not re-litigate.
- **Scope:** large. The doc offers a clean MINIMAL (days) -> MODERATE (weeks) ->
  AMBITIOUS ladder. WS-3 could ratify MINIMAL-now + MODERATE-scheduled and pin
  the DQ-24 demand-model + DQ-15 archetypes into the build brief.
- **Absorbs:** #789, `RESEARCH_IDEA_PAPER_PIPELINE_GAP.md`, DQ-24 (ruled),
  DQ-15, burnout model, build lanes L2/#613 and part of L3/#615.
- **Serves:** the thesis directly (kills the constant-policy exploit; wires the
  promise/appetite/ledger loop). Highest design payoff, highest build cost.

### Theme D -- Meta / ladder integrity + versioning
- **Core tension:** patch cadence vs ladder forking. Which changes fork the
  board? Is save/rewind a designed mechanic or an exploit? How much play is
  disclosed on the leaderboard?
- **Scope:** medium; mostly architecture + norms, some of it must land BEFORE
  the first gameplay hotpatch (build-vs-ladder split). Several pieces are
  decisions, not builds.
- **Absorbs:** build-vs-ladder split (`DISTRIBUTION_AND_PATCHING.md`), #799,
  `DEPRECATED_SAVE_LOAD.md` / DQ-11 (Orb-of-Regret vs one-run), DQ-34, #788,
  #763 (turns-vs-days nomenclature at month grain).
- **Serves:** the launch/liveops spine (v0.12 First Contact + the monthly-league
  cadence). Time-sensitive because the split gates the first balance hotpatch.

(Theme E -- DQ-22 rivals aggro-threshold -- exists and is coherent, but the
roadmap already earmarks it as the v0.13 workshop. Treat it as "WS-4 / the
scheduled DQ-22 workshop" unless Pip pulls it forward.)

---

## 5. Decisions for Pip (to scope WS-3)

**THE single scoping decision (do this first):**
> **Which milestone does WS-3 serve -- "First Contact" or v0.13 "Rivals
> and News"?** Everything else falls out of this. If v0.12: run Themes A + D
> (legibility + meta-integrity), both cheap, both time-urgent, both feed the
> live tester + launch. If v0.13: WS-3 becomes the DQ-22 rivals workshop the
> roadmap already names, and A/D drop to hotpatch execution without a workshop.

Supporting decisions:

1. **Run how many themes?** Recommendation [INFERRED]: WS-3 = **Theme A + Theme
   D** (legibility + meta-integrity). Rationale: they are the two clusters tied
   to the live playtest and the imminent friends-and-family launch, both are
   mostly presentation/architecture (low build risk), and D's build-vs-ladder
   split is a hard prerequisite for the first gameplay hotpatch. Theme C is the
   biggest design payoff but is already RULED (ADR-0011) -- it needs *scheduling
   and a build brief*, arguably not a fresh workshop.

2. **What is explicitly OUT of WS-3?**
   - Theme C's MODERATE/AMBITIOUS workstream build (already ruled; schedule it,
     don't re-design it).
   - DQ-22 rivals midgame (belongs to the v0.13 workshop unless pulled forward).
   - DQ-20 risk pools, DQ-23 damper economy, DQ-9 receivables content -- park to
     a later beat (DQ-23 still owes its real-history baselining errand).
   - New scope on top of unbuilt ADR-0010/0014/0016 -- finish-or-drop only.

3. **Finish-or-drop pass on unbuilt WS-2 ADRs** (Section 2): decide, per ADR
   (0010 adoption, 0011 workstreams, 0014 conference-shape, 0016 league
   pipeline), whether it is still committed or formally downscoped. Unbuilt-but-
   still-"accepted" ADRs are the main rot risk going into WS-3.

4. **Theme B gate:** if Office economy is in scope, someone must WRITE the
   proposal first (no `OFFICE_LAYER_PROPOSAL.md` exists). Otherwise WS-3 has
   nothing to workshop against for B.

**The Friday unknown (asked for explicitly):**
There IS a session on **Friday 2026-07-24** -- issue **#758** "Session agenda:
Friday 2026-07-24 (decisions + conversations queue)". BUT it is **not framed as
a mechanics-design / ADR-producing workshop.** Its contents are art/creative
(doom-colour spec, fonts/wordmark, portrait system), distribution-channel and
art-masters decisions, rival-roster NAMING, leaderboard-enable, a build
playtest, release-notes voice, and a grant deadline. So: **no Workshop-3
mechanics session is currently scheduled** -- not on Friday, not elsewhere on the
roadmap (the only earmarked mechanics workshop is the v0.13 DQ-22 one).
**Decision-for-Pip:** is WS-3 meant to run AT the Friday #758 slot (in which
case its mechanics agenda needs to be added to #758), or is WS-3 a separate
session to be scheduled? This is genuinely unresolved in the repo. [VERIFIED --
#758 read in full]

---

## 6. Open questions / unknowns

- **Workshop numbering.** Is this "Workshop 3" the next mechanics ADR batch, or
  does the `(2026-07-13, workshop #3)` Fable-interview tag already claim the
  number? Confirm labelling before the ADR range is assigned. [INFERRED
  collision]
- **v0.12 vs v0.13 anchor** (the Section 5 headline) -- unresolved in the repo.
- **Is Theme C a workshop at all,** or a build-brief-and-schedule item since
  ADR-0011 already ruled it? Pip's call on whether MINIMAL-vs-MODERATE sequencing
  needs a workshop or just a go/no-go.
- **Save/rewind identity** (DQ-11): Orb-of-Regret branch mechanic vs one-run
  discipline is a genuine fork with leaderboard-integrity consequences; not yet
  chosen.
- **ADR-0015 data strip:** ratify "inert literal doom fields stay" vs schedule
  the migration. Latent-trap risk if left implicit.
- **Office economy proposal** does not exist yet -- Theme B cannot be workshopped
  until it is written.
- **DQ-15 archetype roster** (Pip owes 3-5) blocks the agenda-driven flavour in
  Theme C; not a WS-3 blocker but a dependency to name.
- Milestone due dates in `gh` are stale/contradictory (several 2025 `due_on`
  values on open milestones); do not treat them as live scheduling. The live
  "Now" is v0.12 First Contact (created 2026-07-20, due 2026-09-29). [VERIFIED]
</content>
</invoke>
