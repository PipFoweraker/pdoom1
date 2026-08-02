# ADR + DQ correctness-and-tension audit -- 2026-08-03

> **What this is.** The "correctness and contrasts pass between up and down the
> ADRs and DQs" Pip asked for twice (playtest [7:18]-[7:33], and the 2026-08-03
> brief: "a thorough revisit of every ADR and DQ, re-generating indexes for
> them, seeking tensions and areas of conflict, and also wanting to close /
> lock down some"). Successor to `TENSION_AUDIT_2026-07-23.md`; where that
> audit's findings are still live, this doc says so rather than re-deriving.
>
> **Method.** First-person read of all 18 design ADRs, the 4 runtime ADRs, the
> full `WORKSHOP_2_BACKLOG.md`, `DESIGN_PHILOSOPHY.md`, `WS3_FINISH_OR_DROP.md`,
> `WS3A_DAYLOG_2026-07-27.md`, `WS3_ENDGAME_RULINGS_2026-07-29.md`; three
> parallel code-verification passes (attention/AP economy; doom streams /
> schedules / league; leaderboard / issue cross-refs). Every load-bearing claim
> carries file:line. Claims I could not check are listed in Section 7 -- absence
> from that list means I looked.
>
> **Status: ANALYSIS ONLY.** Nothing here is ruled. Recommendations are marked
> as such; Pip rules. No game code was changed. `DQ_INDEX.md` was regenerated
> (result: byte-identical -- see Section 4).

Severity language: BLOCKING = stands between Pip and a named next step;
LANDMINE = latent, fires on a future refactor/patch; DRIFT = docs and reality
disagree but nothing is on fire yet.

---

## 1. Inventory -- the ADR layer

### 1.0 There are TWO ADR series, and their numbers collide

OBSERVATION: `docs/adr/` holds a 4-record engineering series (Nygard format,
own README + index); `docs/game-design/decisions/` holds the 18-record design
series. Both series contain an "ADR-0002", and the two ADR-0002s contradict
each other **on the game's central claim**:

- `docs/adr/0002-win-condition-survival-spine.md:39` (2026-06-30, Accepted):
  "Driving doom to **0 (ASI solved) is a real but rare apex victory** for
  mastery play".
- `docs/game-design/decisions/ADR-0002-scoring-turns-survived.md:21-22`
  (2026-07-04, ACCEPTED): "There is no victory condition."

The code follows the design series: DQ-1 is RESOLVED (victory branch removed,
`WORKSHOP_2_BACKLOG.md:18-22`), and `game_state.gd:765-782` only ever sets
`victory = false`. `docs/adr/0002` was never marked Superseded -- despite
`docs/adr/README.md:11-14` stating the series' own rule: "If a decision is
later reversed, we add a *new* ADR that supersedes the old one (and mark the
old one `Superseded`)".

DIAGNOSIS: this exact conflict was flagged as T3 in `TENSION_AUDIT_2026-07-23`
and is unfixed 11 days later -- though it IS now ticketed (#809, open: "remove
vestigial victory plumbing + reconcile runtime ADR-0002"). A good-faith
contributor reading `docs/adr/`
first (it is the more standard location) inherits a dead win condition. The
vestigial victory plumbing that audit found is also still present:
`turn_manager.gd:850-851` ("VICTORY! p(doom) reached 0!"),
`game_over_screen.gd:136-137`, `main_ui.gd:1188-1190`,
`debug_overlay.gd:212-213` -- all wired to a flag nothing sets true.

### 1.1 Design-series ADR inventory (docs/game-design/decisions/)

"Code truth" = spot-checked against the current tree this pass, not inherited.

| ADR | Title | Status in file | Date | Code truth |
|---|---|---|---|---|
| 0001 | Spending buys sight | ACCEPTED (as amended by 0004) | 07-04 | Direction intact, system mostly unbuilt. The live instance is hiring-as-scouting (interview reveal ladder, `hiring_pipeline.gd`); SA channels as a purchasable system do not exist yet. |
| 0002 | Scoring: turns survived, lexicographic | ACCEPTED | 07-04 | Scoring VERIFIED: `score_tuple()` = `[turn, round(doom_integral)]`, turns strictly first (`game_state.gd:1240-1254`); accrual `doom_integral += 100 - doom` (`:1228-1232`); single authority (both sort sites call the engine comparator, `leaderboard.gd:120`, `leaderboard_screen.gd:262`); no composite formula anywhere. Victory removal TRUE in the play loop (`game_state.gd:764-782`, only `victory = false`); vestigial "VICTORY!" strings remain (see 1.0; tracked as open #809). One un-written-back refinement: boards key by LADDER EPOCH, not `game_version` (`game_config.gd:567-579`) -- deliberate (build-vs-ladder split) but ADR-0002 point 5 was never amended. |
| 0003 | Liability Ledger | ACCEPTED (build first) | 07-04 | Engine built and mortality-proven; desperation lever solver-proven "a trap that reads as help" (DQ-25, backlog:308-319). Player-facing wiring (BL-1..4) not re-verified this pass. |
| 0004 | SA channels, lead time, decision-flip test | ACCEPTED | 07-04 | Delivery tiers exist (`event_tiers.gd:3-21`); decision-flip telemetry (the ADR's own acceptance instrument, section 4) has never been built -- the acceptance test for the flagship sink is unmeasured. |
| 0005 | Emergent waves; seed = RNG + schedule | ACCEPTED | 07-04 | **INERT (#1020).** Full class + per-turn hook exist (`seed_schedule.gd:21-32`, `turn_manager.gd:61-65`) but `game_manager.gd:80` constructs `GameState.new(game_seed)` with no schedule -- `event_schedule` is `[]` for every real run. Zero schedule data anywhere in `godot/data/`. `doom_pulses` is never written (`doom_system.gd:318-322` reads an always-empty array). Only tests pass a schedule (`test_seed_schedule.gd:47-71`). |
| 0006 | Replay string canonical | ACCEPTED | 07-04 | Determinism/replay tier real (ADR-0017 relies on it; `tests/unit/simulation` re-simulates recorded logs). Full wiring-order completion not re-verified this pass. |
| 0007 | Alliances, third client | ACCEPTED (build third) | 07-04 | Not started -- correctly, per its own sequencing (strictly after 0003/0004). Receivable slot exists unused (`ledger.gd:16,30`). No drift; just queued behind Tension 2. |
| 0008 | Deferrals and rejections | ACCEPTED | 07-04 | Record-keeping ADR; wall-clock open item partially closed by ADR-0009 (6-8 hr ruling). Inward-SA deferral has since been folded and BUILT (see 0011). |
| 0009 | Plan-months, two speeds, day tick | ACCEPTED | 07-12 | Plan-month layer live and compliant: `month_controller.gd:1-19` (day-tick playback, auto-pause-on-window, demand budget), no-banking reserve evaporation (`month_controller.gd:389-397`, `month_plan.gd:18`); sim tick = workday by design (`clock.gd:5-15`, per the 07-14 clarification). TWO gaps: (i) **the S6 badge never shipped** -- `get_turn_display()` implements "March 2034" (`game_state.gd:1208-1221`) but NO UI reads it except the dev overlay; the live HUD renders "Turn 14 -- Fri 21 Jul 2017" (`main_ui.gd:1863-1877`), a day-tick counter in the player's face. (ii) code says "turn" = workday while the ruled nomenclature says a turn is the planning phase; the game-over share line "I survived %d months" is fed by `final_turns` (`game_over_screen.gd:542-543`) -- suspected unit mismatch, not confirmed (Section 7). |
| 0010 | Adoption routing (soft-with-teeth) | ACCEPTED | 07-12 | **CONTRADICTED BY CODE.** Overhang = `max(frontier_capability over ALL actors incl rivals) - safety_absorption` (`doom_system.gd:266-271`), and `safety_absorption` is raised by private safety work -- so basement safety still offsets the rival-driven world hazard. That is the ADR's own REJECTED "status quo" alternative, re-denominated into streams (first verified in `WS3_FINISH_OR_DROP.md` sec 1; still true today). No adoption object exists. |
| 0011 | Effort economy | ACCEPTED + amendments (a)-(g) | 07-12/28 | Amendments TRUE in code: AP pool deleted (`game_state.gd:76-81`; guard test `test_founder_hours.gd:190-214`); cost key `attention`; difficulty scales the grant 24/20/16 (`defaults.json:154-156`, `game_manager.gd:986-994`); reserve untyped (`month_plan.gd:235-244`); staff_rider grants +2 OPERATING (`actions.gd:550-559`). TWO gaps: (i) the player-facing layer still teaches AP -- Tension 4; (ii) a 4-way KIND label layer (doors/approvals/audits/reserve) now exists in code (`month_plan.gd:66-90`, `kind_spent` :109) that amendment (e)'s "2-way floor" text does not record. Review timer 2026-08-31, workshop #984. |
| 0012 | Event response taxonomy | ACCEPTED | 07-12 | VERIFIED in code: the four classes are literal constants (`event_tiers.gd:28-31`); DEFER sold only on deferrable (`:86-87`); standing offers expire to no-engage (`:90-93`). Cleanest ADR-to-code match in the set. |
| 0013 | Financing / cost-of-debt engine | ACCEPTED (shape; numbers owed) | 07-12 | L5 instruments shipped with inert board seats / dilution (DQ-26, backlog:330-337). The later per-instrument interest-cadence ruling ("loan sharks charge on different schedules", backlog:666-671) is not in the ADR. One-engine unification not re-verified. |
| 0014 | Conferences, presence, location | ACCEPTED + amendments (a)-(c) | 07-12/27 | Rhythm-break shell BUILT (#979, merged, per amendment a). Yields correctly sequenced after 0010-v1 -- which is unbuilt, so the whole chain waits on Tension 2. Travel actions were `is_stub: true` at 07-25 (`WS3_FINISH_OR_DROP.md` sec 3); current stub visibility not re-verified. #980 (planner-mind vs operator-presence) status: see Section 7. |
| 0015 | No printed doom deltas | ACCEPTED | 07-13 | Structurally LANDED: nine streams implemented (`doom_system.gd:47-58`, `:262-306`), single doom authority (`turn_manager.gd:737`), authored events + actions clean and CI-guarded (`test_events.gd:107-128`). RESIDUE: 20 LIVE literal `effects.doom` fields in `risk_events.json`, routed via `add_event_doom` (`turn_manager.gd:790-796`), budgeted at `RISK_EVENTS_DOOM_BUDGET := 20` (`test_events.gd:51`, "MUST only ever go down") -- the budget sits at its ceiling, i.e. zero migration since the guard was written. The 07-27 "zero-priced no-op" finding (P4) IS fixed: action stream keys now priced (`defaults.json:96-108`). |
| 0016 | League metabolism | ACCEPTED (shape; pipeline owed) | 07-13 | **Mechanism does not exist.** No pack loader, no pack data, no `data/packs/`; `league_id` is a placeholder constant derived from the FICTION start month (`game_manager.gd:104-109`) so it is identical for every run; the featured seed is a hand-edited const keyed WEEKLY (`game_config.gd:472-488`, `FEATURED_SEED_OVERRIDE := "weekly-2026-w31"`) against the ADR's MONTHLY cycle. The first league shipped pack-free -- the repo's own gate ritual records "there was nothing to bless" (`docs/rituals/gate_3_pack_blessed.md:9-38`). |
| 0017 | Anti-hollow test strategy | ACCEPTED | 07-17 | Not re-run this pass (no test execution allowed -- other agents on the machine); no contrary evidence found. Guard-test pattern is visibly in use by newer code (`test_founder_hours.gd`, `test_events.gd`, `test_balance_key_coverage.gd`). |
| 0018 | Render-only office doctrine | **DRAFT** (formal confirm at R3a) | 07-27 | The confirm HAPPENED: R3a/R4 ruled it and #968 merged (`WS3A_DAYLOG_2026-07-27.md:404-412`, ballots 7-8); the a(3)-lite RenderGrid amendment is recorded in-file. The Status line is stale -- it should read ACCEPTED (review-by 2027-07-27). DRIFT. |

### 1.2 Rulings that never became ADRs (the write-back debt)

The repo's own governance rule, from the WS-3a daylog
(`WS3A_DAYLOG_2026-07-27.md:325-332`): "today's live ruling outranks any old
ADR BUT must be written back into the ADR layer the same day (amendment or
superseding ADR) or it becomes the accepted-but-unbuilt rot FINISH_OR_DROP
exists to kill."

Measured against that rule, these rulings are in debt:

1. **The WS-3 endgame rulings (2026-07-29)** -- `WS3_ENDGAME_RULINGS_2026-07-29.md:3-4`
   says "Promote to ADR at the emit block; this file is the lossless record
   until then." No ADR-0019 exists (the daylog itself noted "next free ADR is
   now 0019"). These are not small rulings: the doom-field reframe, the
   zero-decay escalation ratchet, the stealth-endgame requirement, the
   violence register, the actor want-graph. Five days of design memory living
   outside the decision layer.
2. **POSITIONING (2026-07-22)** -- "the player is NOT running a frontier lab"
   (backlog:470-479), with copy corrections OWED. `docs/ARCHITECTURE.md:24`
   still says "You run a frontier AI lab". Neither an ADR nor the copy sweep
   happened.
3. **League cadence RULED monthly (2026-07-21)** (backlog:405-408) -- recorded
   only as a backlog bullet; meanwhile the code and the live ceremony run
   weekly (Tension 3).
4. **Dial-5 package B+C+D RATIFIED** (backlog:178-184), **burnout outcome
   model RULED** (backlog:171-177), **DQ-24 five demand categories RULED**
   (backlog:194-206), **committed-queue order = execution priority**
   (backlog:723-730), **two-screen PLAN/WATCH model RULED** (backlog:686+),
   **identity-decoupled-from-ability RULED** (backlog:789+) -- all live in
   backlog prose only. Several are load-bearing for L2 build briefs.

RECOMMENDATION: batch-promote 1 and 2 (one ADR each); fold 3 into the Tension
3 ruling; leave 4 as backlog rulings but give them bold status markers the
index generator can see (Section 4).

### 1.3 DQ inventory

The DQ inventory IS `DQ_INDEX.md` -- generated, gate-checked, and verified
zero-drift this pass (Section 4) -- so this audit does not copy its table
(the anti-rot rule: never hand-copy what a generator owns). Headline: **38
DQs; the index reports 32 open, 6 terminal/advanced.** The honest count is
lower: three "open" DQs are ruled or resolved in backlog prose the generator
cannot see (DQ-24, DQ-27, DQ-16 -- Section 4 blind spot), one is absorbed
(DQ-13), and one is a standing process mislabeled as a question (DQ-8) --
see Section 3. Adjusted: ~27 genuinely open, of which 6 are blocked behind
Tensions 1-2 rather than undecided.

---

## 2. TENSIONS AND CONFLICTS (ranked by how much they block)

### Tension 1 -- The reality-tether has no wire (ADR-0005 + ADR-0016 are decisions with no mechanism)

- OBSERVATION: everything exists except the connection. Schedule class, cause
  handlers, per-turn hook, determinism tests: built (`seed_schedule.gd`,
  `turn_manager.gd:61-65`). Pack concept, seed pin, league_id stamp: built
  (`game_config.gd:472`, `game_manager.gd:104-109`). What does not exist: a
  loader (`game_manager.gd:80` passes no schedule) and any content (zero
  schedule keys in `godot/data/`). #1020 tracks it; the gate-3 ritual has
  already eaten the consequence once ("the pack gate dissolved on its first
  run... there was nothing to bless").
- DIAGNOSIS: ADR-0016 was ruled ~75% CANON ("otherwise I drift away from the
  guiding star", DESIGN_PHILOSOPHY.md:61-67) and its entire delivery vehicle
  is ADR-0005 schedule entries -- so the game's identity claim currently rests
  on an inert subsystem. This also silently blocks DQ-6 (schedule provenance
  in the replay -- nothing to carry), DQ-33 (pool snapshot versioning), and
  the "seasons as scenarios" promise of ADR-0005.
- BLOCKING. The v0.14 loader is already scoped (per gate_3 doc, Aug 7); what
  this audit adds: treat the loader as the UNBLOCKING KEYSTONE, not one item
  among many -- two ACCEPTED ADRs and two DQs are dead until it lands.

### Tension 2 -- ADR-0010's teeth are not in the sim; the rejected alternative shipped instead

- OBSERVATION: `doom_system.gd:266-271` computes overhang as
  `max(frontier over ALL actors) - safety_absorption`, and private safety
  research raises `safety_absorption`. So basement safety work offsets
  rival-driven hazard -- exactly the "status quo (direct doom reduction)"
  shape ADR-0010 lists under Rejected alternatives. No adoption object, roll,
  or credit exists anywhere in `godot/scripts` (verified 07-25 in
  WS3_FINISH_OR_DROP sec 1; overhang formula unchanged today).
- DIAGNOSIS: ADR-0010 is one of the two never-patch structural claims
  (DESIGN_PHILOSOPHY.md:43-48). While the absorption partition is missing,
  the sweep's dominant-line kill is not structural, and every system priced
  "as an adoption accelerant" (ADR-0014 yields, conference contacts, research
  depth) is priced against a mechanic that is not there. The R1 block on
  07-27 commissioned a 4-tier ladder for 0010 with "PICK AT R4 TODAY"
  (daylog:115-120); the R4 ballot record does not clearly show a rung was
  picked (ballot 5 reads "DERIVED"), and ADR-0010 carries no amendment.
  **Whether the 0010 rung pick actually happened is the single most valuable
  fact for Pip to confirm** (Section 7).
- BLOCKING -- the widest fan-out of any item here: ADR-0014 yields, ADR-0007,
  DQ-9, DQ-16-remainder, DQ-20 (risk pools are adoption customers), and the
  research-depth work all queue behind it.

### Tension 3 -- Board legitimacy: three half-closed holes on one ladder, plus a ruled-monthly league running weekly

- OBSERVATION (the #788 vs #1058 pair, verified against both records and code):
  these two rulings are NOT a flat contradiction -- they are two patterns for
  two different problems. #788 (OPEN, Pip's 2026-07-22 ruling): dev-assisted
  runs are **MARKED, never excluded** ("players should experiment a LOT with
  dev tools" -- badge + opt-in hide filter). PR #1058 (merged): difficulty is
  locked to Standard because Easy/Hard runs would post to the same
  `(seed, epoch)` board unmarked; and the same pattern already EXCLUDES
  scenario runs outright (`game_over_screen.gd:249-264` gates save AND submit
  on `GameConfig.is_ranked_run()`, `game_config.gd:581-598`). So the implicit
  policy is: *incomparable* runs are excluded, *assisted* runs are marked.
  Coherent -- but never stated as one policy, and half of it is fiction:
  - **#788's marking is UNIMPLEMENTED in both directions.** No
    `dev_mode_used` flag exists anywhere in `godot/` (grep: zero hits);
    `ScoreEntry` carries no dev field (`leaderboard.gd:14-49`);
    `leaderboard_sync.gd:136-140` adds none; the board screen has no hide
    filter (`leaderboard_screen.gd:339-374`). Today a dev-assisted score
    posts and ranks silently.
  - **#1058's lock closes one control, not the value.** The lock lives only
    on the pregame screen (`pregame_setup.gd:57-65`); `settings_menu.gd:162-165`
    still exposes an ENABLED difficulty dropdown writing the persisted value,
    and `game_manager.gd:968-997` still applies Easy/Hard modifiers from it.
    A start path that skips `pregame_setup._ready()` can run non-Standard
    onto the one ladder. Difficulty appears nowhere in the entry or key
    (verified: `leaderboard.gd`, `leaderboard_sync.gd`, `game_over_screen.gd`).
- DIAGNOSIS: this is the silent-wrongness class again -- each ruling looks
  closed (a merged PR, a written ruling) while the board-legitimacy surface
  stays open. What is missing is one ruled POLICY ("who appears on a board,
  how marked, what is excluded") that #788's badge, #1058's lock, and the
  scenario gate are all instances of. DQ-34 (disclosure tiers) is the same
  surface from the privacy side and should ride the same ruling.
- OBSERVATION (cadence half): ADR-0016 rules a MONTHLY league cycle, and the
  2026-07-21 ruling (backlog:405-408) says weekly output is only for "cheaply
  generated artifacts... never curation or balance patches." The
  implementation keys the featured seed WEEKLY (`game_config.gd:475-488`,
  fallback generator emits `weekly-YYYY-wNN`), the live ceremony is a weekly
  league day (`LEAGUE_WEEK_PLAYBOOK.md`, "league close Friday 2026-07-31"),
  and commit 84a9a492 rolls `weekly-2026-w31`.
- DIAGNOSIS: two readings reconcile it -- (a) the weekly seed IS the permitted
  cheap weekly artifact and the monthly cycle starts when packs exist; or
  (b) practice has quietly drifted to weekly leagues. The docs do not say
  which. Left unruled, the ADR-0016 ops-budget constraint (<= 1 day/week
  sustained) is being spent at 4x the ruled cadence.
- BLOCKING for leaderboard trust specifically; DRIFT otherwise.

### Tension 4 -- The ruling the UI never received: the game still teaches a currency that does not exist

- OBSERVATION: ADR-0011 amendment (d): AP deleted in code 2026-07-28, true
  (`game_state.gd:76-81`; no action/event/scenario prices in `action_points`,
  guard `test_founder_hours.gd:207-214`). The player-facing layer never got
  the memo:
  - `godot/scenes/main.tscn:176` -- tooltip "Action Points. Limits actions per
    turn. Base 3 + 0.5 per staff." (node still named `APLabel`; runtime
    overwrite at `main_ui.gd:1122-1126` masks it only after first HUD update).
  - `godot/data/actions/financing.json:37` -- "+2 action points now" while the
    effect grants +2 OPERATING hours (`actions.gd:550-559`).
  - `godot/scenes/player_guide.tscn:125,184` -- in-game guide teaches AP,
    reachable from the welcome screen (`welcome_screen.gd:188`).
  - `godot/data/historical_timeline/2017.json:108,148` -- "costs 2 AP".
  - `godot/autoload/keybind_manager.gd:72` -- "Commit Plan & Reserve AP".
  - `docs/PLAYERGUIDE.md:83-85,175,203,317-409` -- fully stale AP tutorial.
  Issue #1073 tracks part of this.
- DIAGNOSIS: this is the same failure class as the POSITIONING copy debt
  (`ARCHITECTURE.md:24`) and ADR-0014's "-N doom" fiction strings: **rulings
  change the sim; nobody owns sweeping the words.** The house pattern already
  exists for numbers (EE-11, "explainers wired to Balance variables") -- prose
  has no equivalent gate, so every mechanics epoch mints new ghost copy.
- BLOCKING for onboarding/teaching (a new player is taught a dead economy in
  the first minutes); trivially parallelizable fix.

### Tension 5 -- The decision layer itself is rotting: colliding series, stale statuses, unwritten supersessions

- OBSERVATION, four instances converging: (i) two ADR series with colliding
  numbers and a live contradiction on victory (Section 1.0); (ii)
  `decisions/README.md` hand-index missing ADR-0018 entirely and carrying
  pre-amendment statuses (last touched 07-25, `git log`); (iii) ADR-0018's
  own Status line still DRAFT after its confirm (Section 1.1); (iv) the WS-3
  endgame rulings unpromoted (Section 1.2). Issue #1018 tracks ADR
  supersession generally.
- DIAGNOSIS: the repo already solved this failure mode once -- the DQ index is
  GENERATED and gate-checked, and this pass proves the pattern works (index
  regenerated byte-identical while the hand-kept ADR README is stale in four
  ways). The ADR layer has no generator, so it rots at exactly the rate the
  DQ layer no longer can.
- LANDMINE with one live edge (the victory contradiction). Fix is cheap and
  mechanical: Section 5 proposes the generator.

### Secondary tensions (real, smaller, or already fenced)

- **T6. ADR-0015 residue.** 20 live printed doom deltas in `risk_events.json`
  at the guard budget's ceiling (`test_events.gd:51`); inert clobbered sinks
  documented in-code (`resource_accessor.gd:75-79`, `game_state.gd:629-638`).
  Fenced by CI, but the M-ticket (re-author 20 live fields = a balance change)
  has made zero progress since the guard landed. LANDMINE only if the clobber
  is refactored away; the guard test makes that loud. Ruling 5 of R1 already
  split S/M tickets -- the M half needs a home in an epoch.
- **T7. Research Quality: global toggle vs project-level ruling (#1090).**
  Verified: still a global Plan-screen stance (`main_ui.gd:245-249`,
  `research_quality_selector.gd`). Two corrections to the record: it does NOT
  apply literal doom deltas anymore -- it feeds risk pools
  (`game_state.gd:739-753`), whose triggered events are the T6 literals; so
  backlog:520's claim ("uses literal doom deltas -- dies in the ADR-0015
  event-intermediary content pass") is now wrong twice -- the mechanism moved,
  and the ADR-0015 pass did not kill the toggle. The real fix is the ADR-0011
  workstream MODERATE rung (quality/direction becomes per-workstream,
  `RESEARCH_IDEA_PAPER_PIPELINE_GAP.md:250-273`). DRIFT in the backlog text;
  the mechanic itself is fenced.
- **T8. ADR-0011 text lags its own code.** A 4-way kind-label layer
  (doors/approvals/audits/reserve) is live (`month_plan.gd:66-90`) on top of
  the 2-way families; amendment (e) still describes "2-way shipped as the
  floor." The 2026-08-31 review (#984) should rule on the 4-way question with
  the ADR text already accurate, or the review will re-litigate from a stale
  premise. DRIFT.
- **T9. ADR-0004's acceptance instrument was never built.** The decision-flip
  rate is the ADR's own falsification test ("kill any SA feature whose flip
  rate stays low") and nothing measures it. Every SA-adjacent build since is
  un-gated by the ADR's own criterion. DRIFT now; becomes BLOCKING the day an
  SA channel ships.
- **T10. Vestigial victory strings** (Section 1.0 list) -- LANDMINE, prior
  audit's ~15% estimate stands; unfixed.
- **T11. ADR-0009 nomenclature.** "The turn is a month" headline vs the later
  ruled "a turn is a planning phase" (DESIGN_PHILOSOPHY.md:428-434). One-line
  amendment. DRIFT.
- **T12. DQ-6 and DQ-33 are silently blocked by Tension 1** -- neither says so
  in the backlog. Cross-reference when the loader lands.

---

## 3. CLOSE / LOCK candidates (recommendations only -- Pip rules)

### Settled -- recommend LOCK (mark status, defend with a guard where cheap)

| Item | Why it is settled | Lock action |
|---|---|---|
| ADR-0002 (no victory) | Ruled, coded, sweep-proven (DQ-1) | Supersede `docs/adr/0002`; strip the four vestigial VICTORY branches; done. |
| ADR-0009 (month plan layer) | Ruled twice (headline + PR #636 clarification), live in code | Amend headline wording per T11; lock. |
| ADR-0012 (event taxonomy) | Verified 1:1 in `event_tiers.gd` | Lock as-is. Cleanest record in the set. |
| ADR-0017 (anti-hollow tests) | Standing practice, visibly propagating into new guard tests | Lock as-is. |
| ADR-0018 (render-only office) | Confirmed at R3a/R4, merged, amended | Flip Status DRAFT -> ACCEPTED (review-by 2027-07-27). |
| ADR-0011 amendments (a)-(g) | AP death verified structural in code | Add one amendment line recording the 4-way kind layer (T8); then the 08-31 review (#984) is the next touch. |
| DQ-24 (demand taxonomy) | RULED in backlog body (:194-206), built into hiring | Move "RULED" into the bold DQ span so the index shows it (Section 4). |
| DQ-27 (mortality guarantee) | Its own entry contains the resolution: executably pinned in the sweep, ratifying ADR deferred-for-evidence | Mark RESOLVED-PENDING-TRIGGER; the trigger ("mid/late game feels designed") is already written. |
| DQ-16 (conference subgame) | Shape ruled (ADR-0014 amendment a), shell shipped (#979) | Mark SHELL-EXECUTED; the remaining "yields" half is not a design question -- it is Tension 2's build dependency. |

### Quietly dead -- recommend marking so

| Item | Why it is dead | Action |
|---|---|---|
| DQ-13 (doom nudge strength) | Pre-stream-migration framing; "doom nudges" as printed deltas no longer exist (ADR-0015); the live question is stream pricing, owned by the sweep | Mark ABSORBED into DQ-8 / the balance lane. |
| DQ-8 as a *question* | It is a standing process (sweep-driven balance passes), not a decidable question; it will never "resolve" | Convert to a standing lane reference; stop counting it as an open DQ. |
| EE-1 (legacy game_controller path) | `godot/scripts/game_controller.gd` no longer exists (glob: no files) | Mark DONE in the backlog's EE section. |
| Issue #959 (Accept Your Fate) | Feature is on main (commit 8ed05128 cites #959/#1051) but the issue is still OPEN -- the known squash-merge-does-not-close gotcha (CLAUDE.md) | Verify shipped scope matches the ask, then close manually. |
| backlog:520's research-quality claim | Factually stale twice over (T7) | Correct the sentence when DQ statuses are next edited; #1090 is the live tracker. |

### Genuinely open -- keep, with sharpened framing

- **Blocked-behind-Tension-2 (do not workshop until 0010-v1 is picked/built):**
  DQ-9 (receivables content), DQ-20 (risk pools), DQ-16 remainder, ADR-0007.
- **Blocked-behind-Tension-1:** DQ-6 (provenance), DQ-33 (pool versioning).
- **Ready for a workshop now:** DQ-19 (character creation -- PRIORITISED since
  07-13, still unworkshopped; feeds ADR-0004 channels and DQ-4), DQ-22 (aggro
  midgame -- NOTE: the WS-3 endgame rulings already ruled its rung boundary
  (rivals own 0-2, violence era owns 3-4); promote that ruling first or the
  workshop re-derives it), DQ-23 (dampers), DQ-25 (desperation legibility --
  solver data is in), DQ-34 (disclosure tiers -- interacts with Tension 3's
  ruling and should ride it).
- **Standing registers, correctly open-ended:** DQ-17/17-ext (achievements),
  DQ-35/35-ext (cosmetics), DQ-31 (actor tags -- NOTE: the cheap headroom
  ("rivals.json ships with a tags field") never shipped; no rivals data file
  exists in `godot/data/`), DQ-30, DQ-29, DQ-32.
- **Re-scope:** DQ-10 (inward SA) -- the *mechanism* half is ruled and built
  (ADR-0011 audits; reported_vs_actual seam, PR #981); what remains is the
  narrower "how much of your own ledger do you SEE" UI question. Rename or
  split so the built half stops looking open.

---

## 4. Index regeneration

`python scripts/generate_dq_index.py --check` passed BEFORE regeneration and
the regenerated file is byte-identical: **the DQ index has zero drift.** The
generated-index pattern is doing its job.

One parse-contract blind spot found (not a bug, a convention gap): the
generator reads status keywords only inside the bold `**DQ-N ...**` span
(`generate_dq_index.py:38,61-75`). Rulings recorded in the entry BODY (DQ-24's
"RULED", DQ-27's in-entry resolution) are invisible to it, so the index
under-reports resolution. Two possible fixes; the cheap one is editorial:
when a DQ gets ruled, write the keyword into the bold span (that IS the
documented contract, per the script docstring). The generator itself needs no
change.

## 5. decisions/README.md: do not hand-fix -- generate it

The hand-kept `decisions/README.md` is the failure mode the DQ index was built
to kill (the script's own docstring cites it: "see the stale decisions/README.md
for the failure mode this avoids", `generate_dq_index.py:5-6`). Current
staleness: missing ADR-0018; statuses pre-amendment for 0011/0015/0018; last
real touch 07-25.

This is not a new idea -- it is ALIGNMENT: issue #1018 (open, "Philosophy
Quest: progressive supersession scan over the ADR set") already proposes
required frontmatter (`status`/`supersedes`/`superseded-by`), a GENERATED
`decisions/README.md` gated in pre-commit like `DQ_INDEX.md`, and a
collision-matrix scan; #1049 (open) asks for the correctness/staleness pass
with an implementation-status field the website can render. This audit is
effectively the first manual run of both. The proposal below is the minimal
generator that #1018's fuller scheme can grow from:

PROPOSAL -- `scripts/generate_adr_index.py`, same shape as the DQ generator:

- **Reads:** `docs/game-design/decisions/ADR-*.md` (excluding the template).
  Per file, parses:
  - the H1 (`# ADR-NNNN -- <title>`) for number + title;
  - the `- **Status:**` line (the template contract, `ADR-TEMPLATE.md:3`);
  - the `- **Date:**` line;
  - presence and dates of `## Amendment` headings -> an "amended YYYY-MM-DD"
    column, so post-hoc rulings are visible at the index without editing the
    status line;
  - first sentence of `## Context` or an optional explicit one-line summary.
- **Emits:** the index table + a totals line, ASCII-transliterated (reuse the
  DQ generator's `ASCII_MAP`).
- **Gate:** `--check` mode wired into pre-commit beside the DQ check, so an
  ADR edit without regeneration blocks the commit.
- **Side effect worth having:** the parser fails loudly on a missing Status
  line, which enforces template conformance on future ADRs for free.
- **Open call for Pip:** does it also read `docs/adr/`? Options: (a) second
  table in the same README naming it the engineering series; (b) rename that
  series (ENG-0001..) to end the number collision; (c) fold its 4 records
  into the design series with supersession notes. Any of these ends the
  two-ADR-0002s problem; (b) is the smallest.

This audit deliberately does NOT hand-edit the README -- the stale index is
Exhibit A for the generator and hand-fixing it would destroy the evidence
while re-committing to the failure pattern.

## 6. What this unlocks -- the decisions in front of Pip, ordered by unblock

D1. **Confirm or make the ADR-0010 rung pick** (Tension 2). If R4 already
    picked it, the cost is one amendment paragraph; if not, this is the
    highest-leverage open decision in the repo: 0014 yields, 0007, DQ-9,
    DQ-16-remainder, DQ-20, and research depth all unblock behind it, and the
    game's second structural claim becomes true in the sim.
D2. **Bless the schedule loader as the v0.14 keystone** (Tension 1). Already
    scoped for Aug 7; the decision is priority, not design. Unblocks
    ADR-0005, ADR-0016, DQ-6, DQ-33, and the first real pack.
D3. **One board-legitimacy ruling** (Tension 3): state the policy the three
    instances already imply (incomparable runs excluded; assisted runs
    marked), then fund its two missing halves -- implement #788's
    `dev_mode_used` badge, and close the difficulty VALUE (submission-side
    guard or key it) rather than one entry screen. Pin weekly-vs-monthly
    league cadence against ADR-0016 in the same sitting. DQ-34 rides this
    ruling.
D4. **Authorize the ghost-copy sweep** (Tension 4): one content lane kills the
    AP ghosts (#1073 list above) + the frontier-lab positioning copy. No
    design input needed beyond the go.
D5. **ADR hygiene batch** (Tension 5): supersede `docs/adr/0002` and finish
    #809; flip ADR-0018 to ACCEPTED; promote WS3 endgame rulings to ADR-0019
    and POSITIONING to ADR-0020 (or amendments); adopt
    `generate_adr_index.py` (de-parks the deferred #1018/#1049 pair at
    minimal cost); pick a fate for the `docs/adr/` series. Mostly clerical;
    a half-day lane.

The single decision that unblocks the most: **D1.** D2 unblocks two ADRs but
is already scheduled build; D1 is a genuinely open pick with the widest
downstream fan-out, and every week it stays open, systems get priced against
an adoption mechanic that does not exist.

## 7. What I could NOT verify (stated plainly)

- **Whether R4 (2026-07-27) actually picked an ADR-0010 rung.** The ballot
  record's "5 DERIVED" is ambiguous and ADR-0010 carries no amendment. If a
  LADDER_0010_R2 doc exists it is not in `docs/` (glob found no LADDER_* files
  -- possibly scratchpad-only, which would itself be a write-back gap).
- The suspected months/workdays unit mismatch in the game-over share line
  (`game_over_screen.gd:542-543`, "I survived %d months" fed by
  `final_turns` where a turn is a workday per `clock.gd:5-15`) -- flagged,
  not traced to the value's origin. Adjacent to open #1062 (Duration column
  meaningless when score is turns).
- ADR-0006 wiring-order completion (steps 2-4) beyond the existence of the
  replay/determinism test tier.
- BL-1..4 (ledger player-facing wiring) current state.
- ADR-0013's one-engine claim (loans and DEFER carrying costs actually priced
  by one code path).
- Whether #758 (portrait variant determinism, DQ-15 ext) was ever ruled.
- Whether the ADR-0014 travel stubs are still player-visible in the current
  build (verified true as of 07-25 only).
- ADR-0017's suite health (no test runs permitted this pass).
