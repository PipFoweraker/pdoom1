# Workshop #2 Backlog — Parked Items Register

> **Purpose.** Every question or errand *parked* (not freelanced) during the workshop-#1
> build lanes lands here, so nothing evaporates and we clear it **in one fell swoop**.
> Three buckets:
> - **Design questions (DQ)** — need judgment; resolved *with Fable at workshop #2* (which
>   also wants first playtest data + a fresh kickoff doc; `FABLE_SESSION_KICKOFF.md` is
>   EXECUTED/stale).
> - **Deferred build lanes (BL)** — no design blocker, just queued implementation (mostly
>   the ledger's player-facing slice — the engine landed, the UI didn't).
> - **Engineering errands (EE)** — batched cleanup, no design judgment.
>
> Each item cites its source PR. Update status here as items resolve.
> Lanes captured: WS-A #550, WS-B #551, WS-0 #552, WS-C #554, WS-1 #555.

## Design questions — for Fable workshop #2

- **DQ-1 · Victory condition removal — RESOLVED** *(#550, ADR-0002)* — the doom≤0 victory
  branch is **removed**. Proven safe by the exploit sweep: with rival labs contributing
  scaling doom (#562), a clean safety run is now *finite* (dies of doom, no immortal runs),
  so removing the win no longer creates an immortal-run exploit. The game is now unwinnable
  by design (ADR-0002 thesis: you can only buy time).
- **DQ-2 · Baseline yardstick** *(#550)* — is the no-action baseline still the right
  reference under turns-survived scoring?
- **DQ-3 · Cross-version leaderboard UX** *(#550)* — `(seed, game_version)` boards show as
  separate `seed (version)` entries. Aggregate/filter by version, or leave split?
- **DQ-4 · Character-creation re-roll within a seed** *(#552)* — ruling applied: *same seed
  → same starting staff*. Whether a future char-creation screen lets you re-roll *within* a
  seed is deferred (not implemented, not precluded).
- **DQ-5 · Empty-seed determinism contract** *(#552)* — only explicitly-seeded games are
  deterministic (empty falls back to `Time`). Confirm interim contract; tighten later so
  every ranked game records a concrete seed?
- **DQ-6 · Schedule provenance in the replay artifact** *(#554)* — replay accepts a
  schedule, but the exported artifact doesn't yet *carry* it. Should the schedule travel
  with the run, or be recoverable from `(seed, version)` via a seed registry? (Ties to WS-B
  artifact format + EE-2.)
- **DQ-7 · Governance player-facing design** *(#555)* — `governance` added as an engine
  `float` (a ledger currency per ADR-0003), but its scale, starting value, how the player
  raises/spends it, and its UI are **undesigned**.
- **DQ-8 · Balance constants** *(#555, #562)* — ledger escalation rates
  (`DOOM_PER_UNPAID_1000`, interest, loan multiple) and rival doom pressure are
  **placeholders**. Rival magnitude softened `0.05 → 0.025` as a first step toward longer
  games; full tuning (game length, sink pricing) still open — a playtest-driven pass.
- **DQ-9 · Receivables / counterparty content** *(#555)* — the `Entry` model supports the
  receivable (favor/pledge) side, but content is unbuilt and **overlaps ADR-0007 alliances**
  (WS-3). Design together?
- **DQ-10 · Inward-SA / ledger visibility** *(#555)* — how much of the player's *own* ledger
  is visible is undecided; overlaps WS-2 SA and the inward-SA deferral (ADR-0008).

### Workshop #2 additions (2026-07-12, beat 1 / ADR-0009)

- **DQ-11 · Save/fork/divergence mechanics** — Pip open to them; legal under ADR-0006's
  verification law. Needs design: UX, ladder norms (not rules), interaction with
  seed-as-timeline fiction (a fork is *literally* a timeline fork — free flavor).
- **DQ-12 · Rival narrative presence** — playtest note: rival still "narratively
  invisible" despite mechanical doom pressure. Candidate home: response windows + month
  review screen (rival actions as events you *see*, not just doom drift).
- **DQ-13 · Doom nudge strength** — playtest note: "doom nudges overall probably a
  little strong." Folds into the DQ-8 balance pass, re-denominated at month grain.
- **DQ-14 · World-state progression display** — playtest note: "sense of progression
  over time doesn't feel very strong." Candidate home: month review screen (ADR-0009
  consequence) + era-keyed visual/UI shifts.
- **DQ-15 · Researcher archetype roster — SEEDED** *(ADR-0011)* — Pip authored three
  (people-pleaser interp, authoritarian governance pessimist, moral-crusader agent
  foundations), Fable drafted two for veto (capabilities-curious optimist, burned-out
  ex-frontier senior). Roster lives in WORLD_AND_LORE. Remaining: Pip's edit pass +
  appetite fills.
- **Promoted: conference/travel design** *(ADR-0010)* — now the mandatory middle of the
  research→adoption value chain, no longer flavor; design with DQ-9 receivables +
  ADR-0007 counterparties.
- **DQ-16 · Conference-attendance subgame** *(ADR-0014)* — Pip's flagged ambition
  ("that's how critical I think these are"). v1 ships attendance + yields only; revisit
  when playtests show conference turns feel thin.
- **DQ-17 · Achievement candidates register** *(build lane L8)* — observer-only,
  never writes back to sim/score. Seed set: year marks, first-time-X. Tag
  `[ACHIEVEMENT]` in future sessions and append here.
- **Navigation principle — PROVISIONAL, not ratified** — hub-and-spoke guidance in
  WORKSHOP_2_BUILD_LANES; rule it at workshop #3 with real screens in hand.
- *(Parked in ADR-0009 itself: variable/coarsening cadence; quarter grain — each with
  explicit revisit triggers.)*

> **2026-07-12 reconciliation:** BL-1..3 absorbed into build lane L4; BL-5 into L6;
> EE-2 **promoted** to lane L7 (6–8 hr runs require save/load); DQ-6 batches into L1's
> replay schema bump; DQ-8 gated behind EE-8. See `WORKSHOP_2_BUILD_LANES.md`.

## Playtest QA findings (2026-07-13, Pip — first play of the consolidated build)

**Positive:** delta chips (L6/EE-7) "really helped"; play loop "felt good" over a few
dozen turns; doom felt good on a hang-and-watch; achievements a "nice skeleton."

**Bugs filed:**
- **#630 · Event flood + text overflow** — turn 33 queued 28+ events (mostly paper
  decisions), click-through wall, dialogs overspill margins. Lead: paper decisions bypass
  `MAX_NEW_EVENTS_PER_TURN`. Present-build stopgap; structural fix already decided
  (ADR-0009/0012/0014 — the notification-spam thinking, this is its concrete instance).
- **#631 · Event outcome correctness** — flavor fires but effect unclear/broken (poaching:
  which researcher? does "let them go" no-op?). Needs flavor-vs-effect audit + outcome
  legibility. Pip wants a real QA/human-review process on event outcomes.
- **Save regression (fixed live)** — pause→Save hit "GameManager not found"
  (`pause_menu.gd` used the L0-deleted `../GameManager` scene node); fixed to the autoload.
  Uncommitted in Pip's tree; wants a pause→save→load smoke test (feeds #629).

**Design (future workshop):**
- **DQ-18 · Early game = scouting / the populating board** — Pip's coalescing theme
  (DESIGN_PHILOSOPHY "On the early game"): scouting as the veteran-replayability engine;
  board fills over time via staff/actions ("go read / meetups / shitpost online"); hiring
  as a slow, committed scouting relationship (XCOM-2012 recruit attachment); hires become
  your scouts ("comes across your desk"). Strong candidate for a dedicated beat. Connects
  ADR-0001/0004 (SA), ADR-0011 (staff-as-channels), ADR-0014 (presence/discovery).
- **DQ-17 ext · Achievements in-run visibility** — Pip wants them referenceable *during* a
  run, near a "character sheet" UI surface that doesn't exist yet (himself unsure); also
  "felt a little generic" → content pass owed. Overlaps DQ-14 (world-state progression
  display) + the wanted dashboard/character-sheet surface.

**No action (expected):** the top-left clock **"Week 8 | … | Day 3/5"** is a day-tick
hangover Pip correctly flagged — replaced by ADR-0009's month display when L1 (#612)
lands; current display honestly reflects the still-day-tick structure, so no fix before L1.

### Workshop #3 additions (2026-07-13, beat 1 — scouting/early game)

- **DQ-18 — EXECUTED** — the scouting beat ran as workshop #3's lead. Outputs:
  DESIGN_PHILOSOPHY "On the early game" extended + new "On the hero and the office"
  section; **ADR-0015** (no printed doom deltas) and **ADR-0016** (league metabolism)
  minted. Residue distributed to DQ-19/20/21 below and the #612 spec addendum.
- **DQ-19 · Character creation surface — PRIORITISED** *(de-parked by Pip 2026-07-13
  during issue triage: "prioritise de-parking all related issues, we should solve for
  them soon")* — attached question (Pip: "the right question"): does founder background
  **type the starting channels/connections** — ex-academic → research-sight affinity,
  ex-finance → doors/VC access, ex-journalist → media-sight? Moves ADR-0004's
  channel-investment build-identity axis partially to turn zero. Overlaps DQ-4 (re-roll
  within seed). Starting connections as a config lever. Absorbs #473/#514 (point
  allocation); dependency chain into ADR-0004 channel design. Candidate next workshop
  beat alongside DQ-23.
- **DQ-20 · Risk pools** — Pip's gloss, logged not designed: *"insurance/mutualisation -
  industry actors pooling exposure to AI incidents, and the pool itself becoming an actor
  with opinions about safety standards. Like how fire insurance invented building codes…
  the pool is a customer for safety work with actual pricing power."* ADR-0010 adjacency
  (adoption customer); mid-game unlock; candidate: governance-lane researchers can stand
  one up. Don't over-invest yet.
- **DQ-21 · Intermediary vocabulary v1 — RESOLVED (v1)** *(ADR-0015; PR #634, fully
  vetoed by Pip 2026-07-13 via sheet)* — Nine streams: `general_capability` (chronic
  floor), `frontier_capability` (per-actor map; player slice separately named for DQ-22
  aggro), overhang (`frontier − safety_absorption`), `global_compute` (uncontrollable
  ocean, no direct doom term), `dedicated_ai_compute` (governable fleet),
  `ambient_risk`, `global_panic` (additive), `global_alarm` (small stream AND
  damper-gate), plus scheduled pulses (ramp/spike/tail envelope on ADR-0005 entries);
  `political_pressure` gates dampers, owns no stream. Doom = accumulating rate;
  baselines dampable; streams clamp at 0 v1 (**LOUD revisit flag — Pip not settled**);
  trend invariant N=6 months (sustained decline without sacred-object cause = telemetry
  flag + exploit-sweep gate failure). Sacrifice emergent, not a gate (R2-Q8 revision).
  Cycles: no v1 machinery, prefer emergent (open). Forward intent: decompose
  `political_pressure` into component risk factors via real-world risk/harm taxonomies
  (**MIT AI Risk Repository** named as reference source) — feeds the pdoom-data /
  league pipeline.
- **DQ-23 · Damper economy** *(next workshop beat; from R2-Q4)* — minting systems,
  durations, stacking rules, per-stream caps. Pip's prep instruction: "prompt agent to
  find examples from real history to baseline with or against" — research errand:
  historical analogs of policy/institutional responses damping technology risks
  (candidates to check: Montreal Protocol, nuclear test bans, financial-stability
  accords), for damper magnitude/duration baselines.
- **Burnout outcome model — RULED (Pip 2026-07-13, resolves #635 DEFERRED)** — ignored
  burnout ("Push Through") is never toothless: outcome draws from {sudden quit,
  no-notice quit, short-notice extended leave → return with lasting loyalty + efficiency
  debuff}; recovery duration ≫ prevention cost (send-on-holiday). Implementation home:
  L2 effort economy (#613) — needs per-researcher efficiency debuffs with durations;
  interim event content may ship the loyalty-hit-only version. Interacts with DQ-22
  (loyalty hits raise poach vulnerability).
- **Dial-5 RATIFIED (Pip 2026-07-14)** — package **B+C+D** from
  `docs/balance/DIAL5_ATTENTION_SCARCITY_PROPOSALS.md`: demand rise via diegetic
  process steps + admin tax bought down by ops hires (B), era-scaling demand/cost (C),
  uninsured-handling premium (D). **A rejected** (fights the ~20-decisions canon).
  **E transformed**: cramming/fatigue expressed as *visible debuffs* on the unified
  status layer (see burnout ruling), never hidden roll degradation. Decimals set after
  the doom recalibration lands (sweep sequencing note).
- **DQ-24 · Attention-demand taxonomy + typed delegation** *(Pip 2026-07-14; feeds
  build lane L2 #613 spec)* — enumerate the ~4–6 demand skill-categories (candidates:
  ops/bookkeeping, people/HR, technical-infra/security, research direction,
  external/comms) and the hire-archetype matching ("can't delegate bookkeeping to a
  security engineer"); enumerate the process-step demand list (hiring pipeline steps,
  onboarding, research-strategy setting, progress check-ins); define aggregation rule
  (typed micro-demands roll up into manager-absorbed classes at scale — same object as
  the Celine's-law report). Guard: type demands, never the currency — Attention stays
  single and universal. Workshop beat alongside DQ-19/DQ-23.
- **DQ-22 · Aggro-threshold midgame** *(Pip 2026-07-13; ADR-candidate)* — rivals develop
  their own positions until the player's visible impact threatens their interests, then
  active attacks begin (litigation, funding cuts, rep attacks, scathing reviews, psyops,
  aggressive hiring, leak seeking) — "the sign we're entering the midgame." XCOM:EU
  anti-grind / Factorio pollution-biters pattern. Mechanism + threshold semantics owed;
  interacts with rival-headstart difficulty ratchet (compounding, legible, doesn't feel
  like cheating) and DQ-12 (rival narrative presence — the attacks ARE the presence).
- **L1 spec inputs from the handover round** *(feeds #612)* — window demand budget:
  **2–3/month at spawn → 5–6 in true endgame**; some events legally unignorable;
  unanswered windows auto-resolve as IGNORE **with a mild default rep penalty**
  (nonresponse annoys the offerer; flavor note: a "known to be busy" trait reduces it).
  Founder unit: **decisions**, ~20/month, admin as painful overhead; staff spend
  *actions* — separate currencies (ADR-0011 refined). Currency name RULED: **Attention**
  (2017 / "Attention Is All You Need" resonance; Pip 2026-07-13). Ambient feed floor: 2017 civilian
  awareness (WEIRD nation, mid-sized city, moderately techy). Ratcheting timeline
  ideation (how games play out era by era) — flagged by Pip as a future exercise.
- **EE-6 promotion note** — the schedule content pipeline is now ADR-0016's league
  pipeline: structured monthly world-diff format, LLM-drafted, Pip-approved, ≤1 day/week
  sustained. Product feature, not aspiration.
- **F3 risk overlay = the stream readout** *(Pip confirmed 2026-07-13)* — the "risk
  pools" that hover at zero in current playtests (#584 overlay) get their content from
  DQ-21's named doom streams; the overlay becomes the earned high-resolution doom
  instrument's home. No new surface. Balance gate: doom falls legal, *sustained* falls =
  failed-difficulty signal (exploit-sweep gate + telemetry, not an engine clamp).

### Triage captures (2026-07-13 — salvaged from 2025-issue close-out, Pip-flagged)

- **Observable threshold** *(#474)* — two-tier discovery model worth specifying in the
  scouting design: low observability → only big labs visible; high observability →
  small research groups/startups visible. Home: ADR-0014 discovery-by-presence /
  DQ-18 scouting choreography.
- **Paper-presentation delegation split** *(#411)* — self-present ≈1.5× vs delegate
  ≈1.0× reputation multiplier; park for DQ-16 (conference subgame revisit).
- **Series A/B/C staged equity progression** *(#395)* — stage-appropriate investor
  matching; revisit when the equity/capabilities-funding branch gets its mechanics
  review (ADR-0013 extension). **Market conditions** (bull/bear funding cycles) —
  distant-park, low priority, "most likely not-abandon, but not-get-to" (Pip).
- **Event-chain schema caution** *(#513)* — `event_chains.json`/`triggers.json` is seed
  data only; re-derive chain-management design from current intuitions (gauntlets,
  pulses, ADR-0012) before adopting any of it. Flag for L4 content wiring.
- **Ledger failure states TODO** *(#476)* — overdraft / tax-penalty / audit-problem
  failure states to be explicitly cross-referenced into ADR-0012's called-due cascade.
- *(Presentation-layer intents — robed cabal animations #222, insight-ladder copy #515 —
  captured in WORLD_AND_LORE.md.)*

## Playtest QA findings — round 2 (2026-07-13 evening, first play of the L1 month loop, PR #636 branch)

**Pip's reaction (verbatim):** *"That new version where things play out fast in front of
me is super cool. It makes the simulator element way more representative. This feels
like a huge shift… I feel like time in the game will progress way faster. Interestingly,
my doom was low and then partway through the second month it spiked up at the end and I
watched as I lost. It felt pretty wild! This will make video capture of the game much
more interesting."*
- **Evidence the playback delivers the intended register** — "I watched as I lost" is
  the tragedy target (ADR-0004 lead-time feeling), arriving via resolution spectacle.
- **Streaming/video-capture value noted** — the day-tick playback is inherently
  watchable; park as a marketing/community consideration.
- Month-2 doom-spike death = expected pre-rebalance behavior (old day-grain doom
  constants under the new structure); the L1 balance sweep (below) quantifies it.
- **Time-progression feel:** "way faster" — watch wall-clock-per-fiction-year against
  ADR-0009's 6–8 hr decent-run target once balance lands.

## Balance-instrument roadmap (Pip 2026-07-14, post-L1-merge)

- **EE-9 · Auto-player strategy scripting** — *"experiment with outlining strategies in
  more detail to the auto-player"*: evolve sweep policies from constant heuristics to
  scripted strategy outlines (plan-level + response-level policy pairs, per ADR-0009's
  exploit-finder rework note). Lets the sweep test *lines*, not just dispositions.
- **EE-10 · Opening-book miner** — *"brute-force random selection of the first ~20
  moves of the game, then adopt certain default behaviours so as to mine information
  about early game build stack order / variance / outcomes"*: randomize the opening
  prefix, standardize the continuation, and map opening-move → outcome distributions.
  Dev-side scouting of the opening meta (the ladder's "stable target goals" space);
  also measures per-seed micro-variance once the social layer lands.
- **Playtest deep-dive protocol** — a couple of comprehensively logged human
  run-throughs: replay artifact (ADR-0006 input-string) + periodic/auto screenshots +
  Pip's timestamped impressions, reviewed as a unit. ~~Candidate small build item~~
  **flight recorder SHIPPED** (F9, PR #639). Decision-flip logging (ADR-0004 §4:
  declared-intent-before-reveal vs action-after) belongs in this bundle.

### #638 review rulings (Pip 2026-07-14) + roadmap additions

- **EE-9 spec enriched (Pip):** policies as *reactive condition rules* ("do this with AP
  unless this condition is met, in which case do this" — e.g. fundraise by default, loan
  only when cash runs low); **solver-bots** in dev tooling to systematically probe one
  mechanic vs baselines (first target: desperation levers, Pip's open-Q1); use
  established game-balancing techniques (parameterized reactive policies, hill-climb /
  beam over opening prefixes, MCTS-lite where the tree is shallow) rather than naive
  random walk — random_walk retained only for initial theory-of-play mapping.
- **EE-11 · Variable-wired mechanics docs** *(Pip: "I don't understand [the ledger's]
  underlying mechanics well enough to explain it")* — wiki / player-guide / dev-guide
  explainers that are **wired to Balance variables** (generated or referencing
  defaults.json keys) so prose stays numerically accurate across patches. First
  customer: the Ledger explainer. Second: the doom pipeline post-migration.
- **Cadence audit (scope confession, Pip):** systematically hunt remaining per-tick
  interactions that bill at non-human-sense speeds ("things taking human times and
  efforts") — the #638 finding (rival doom, researcher doom, ledger fuses all billed
  per-tick) generalized into a standing sweep-rigor item. More such finds are
  *welcome*: rigor here buys future feature-adding without unexpected outcomes.
- **T9 floor target (Pip):** no standard-policy run dies < 6 months; early game nearly
  unlosable w.r.t. compounding debt. Fed into #638's final iteration.
- **DQ-25 · Desperation-lever revisit** — Pip wants the mechanic + flavor re-understood
  (ADR-0003's catch-up machinery); solver-bot data now in (EE-9, PR #642,
  `docs/balance/DESPERATION_SOLVER.md`, calibrated pre-stream-migration constants).
  **Finding: the lever is a trap that reads as help.** Firing it earlier/more is
  *monotonically worse* (baseline 14.0mo → lever-always 11.5), and it silently converts
  doom deaths into ledger deaths (1→12) — the visible −10 doom hides a compounding
  governance liability. Cross-validated three ways: solver monotone, `fundraise_first`
  (14.0) beats `loan_desperation_reactive` (13.0), and the opening-book miner flags
  `desperation_lever` as a top loser signal. This is ADR-0003 "every mitigation is a
  loan" proving itself. Design beat owed: is the reveal legible enough, or is it a
  *too-hidden* trap (honesty line)? Re-confirm numbers post-#643 (streams change
  ledger→doom conversion).
- **ADR-0015 migration status (PR #643, awaiting Pip review)** — doom is now a
  nine-stream accumulating rate; sweep feel preserved (do_nothing 14, T9 held, mortality
  PASS, ordering intact). **Structurally complete; one content tail remains:** event/
  action JSON (`data/events/*.json`) still carries inert/clobbered doom writes routed
  through two generic sinks (`add_resources`/`resource_accessor`) — per-event
  intermediary re-authoring is a **content lane** (the "event-intermediary content
  pass"), owed before the printed-delta ban is 100% true in data. Also: R2-Q9 hazard-
  stream ≥0 clamp shipped with a LOUD in-code revisit marker (Pip unsettled, DQ-21).
  **Post-merge todo:** regenerate EE-9/EE-10 balance docs (one command) on the stream
  base — their current numbers are pre-stream-migration.
- **DQ-26 · VC/equity depth revisit** *(Pip 2026-07-15, on approving #641)* — the L5
  instruments ship with equity dilution + board seats as inert standing terms (DQ-7
  stubs). Future work: (a) make VC investment *interesting* as a mechanic (what does a
  board seat DO — agenda pressure, window injections, exit pressure?); (b) build the
  measurement layer for equity and board seats (cap-table state, control thresholds);
  (c) Pip's framing: these are **set-at-config-or-accept-basics** knobs — fine-tunable
  as difficulty or scenario settings (ADR-0016 league/scenario surface), so the config
  schema should carry them even while the mechanics stay basic.
- **DQ-27 · Mortality guarantee — where is it ratified?** *(Pip 2026-07-16, from #645
  coherence check)* — the guarantee (no immortal runs, ADR-0002) is currently *emergent*
  from ledger compounding interest, asserted across ADR-0002/0003/0013, pinned in no
  single ADR. Pip's self-check: *"I can't tell if I am being philosophically shy or if I
  want to play the game a bit more and build out the middle and end games organically."*
  **Resolution (not shyness): the guarantee IS pinned — executably, in the exploit-sweep
  mortality assertion (0 immortal runs, max-months bound), not in prose.** An executable
  guarantee beats a prose one. Correct move: leave the mechanism *emergent and
  sweep-protected* until mid/late game is played-in, THEN write the single ratifying ADR
  choosing the mechanism deliberately rather than freezing an unfelt one. Deferral-for-
  evidence, not timidity. Trigger to write the ADR: mid/late-game feels designed, not
  accidental.
- **DQ-28 · Game "phases" as vocabulary + scenario-jump testing** *(Pip 2026-07-16)* —
  Pip: as the game lengthens and "its metabolism heats up and starts changing the nature
  of experiences the player's having," we'll want (a) an internal (later maybe
  player-facing) vocabulary of **phases** — early/scouting, mid/"world shoots back"
  (DQ-22 aggro threshold), late/attention-drowning; and (b) **test suites that jump to a
  phase** instead of replaying from turn 1 (as full-game sims get expensive — extends the
  tiered-pipeline discussion). **Fold: flight-recorder state snapshots (F9, #639) ARE
  scenario fixtures** — a saved mid/late state = a test seed; the capture tool and the
  test-fixture library are the same object. Connects DQ-22 (phase boundaries as the aggro
  threshold) + the deploy-vs-PR test-tier design.
- **DQ-29 · Cover-up debt** *(SALVAGED from pre-Godot TECHNICAL_FAILURE_CASCADES.md,
  Pip loves it 2026-07-16)* — a failure-response trichotomy: **Transparency / Investigate
  / Cover-up**, where covering up a technical failure mints a **delayed-exposure hidden
  liability** — a secret ledger entry that bites later via an exposure event. Beautiful
  reuse of existing machinery: ADR-0003 secret entries + ADR-0012 exposure events, zero
  new systems (Rams #10). On-theme (the "nobody wants to bring the boss bad news" honesty
  line, now a player *choice* with a priced downside). Interacts with the Celine's-law
  reporting (managers who cover up) and DQ-22 (a cover-up exposed mid-aggro is a cascade).
  Candidate: workshop beat + one event genre.
- **DQ-30 · Economic cycles** *(SALVAGED from ECONOMIC_CYCLES_IMPLEMENTATION.md, Pip
  loves it)* — typed funding-source **cycle-sensitivity** (government counter-cyclical,
  seed/VC most cyclical) + named macro phases (bull/bear/winter). Directly feeds DQ-28
  (game phases as vocabulary) and de-parks the market-conditions note (was #395-parked as
  "distant, low-priority") — the old lemon already had the phase model. Cycles as
  emergent-from-mechanism (Pip's R2-Q5 preference) rather than a hardcoded clock. Sits on
  ADR-0013 finance + the ADR-0016 league/world-update surface (real macro conditions
  injected monthly).
- **L5 finance construction AUTHORIZED (Pip):** loans over months+, player optionality
  among offered instruments (interest-rate intuitions from ADR-0013), "orchestrate the
  construction… in parallel with the other finance ideas" — build lane L5 (#616)
  launches after #638 merges.
- **Momentum:** dial-4 retune accepted as *interim*; momentum ruled a low-commitment
  SWITCH (Balance flag + weight); refresher explainer owed to Pip (memo box, #638).
- **Reputation reminder (Pip's open-Q5):** direction already ruled — reputation is
  TYPED per-audience/per-actor (ADR-0010; ADR-0011 interaction contract), not one
  score; relationships = per-actor reputation + contacts-as-receivables (ADR-0014 /
  DQ-9). Fundraise-first/loan-when-broke is the expected player pattern → EE-9 reactive
  policy should mirror it.

## Deferred build lanes — follow-up implementation (no design blocker)

> These are why WS-1's ledger is **engine + soak only** right now — it works and is
> mortality-proven, but a player can't yet interact with it. A "WS-1b" slice covers BL-1..4.

- **BL-1 · Ledger action/UI wiring** *(#555)* — content factories (loan, funding-with-
  strings, desperation payroll, staff rider) exist but aren't clickable actions in
  `actions.gd`/UI yet. **The ledger is not player-facing until this lands.**
- **BL-2 · Exposure trigger wiring** *(#555)* — `expose()` is built + tested but not fired
  by any WS-C scheduled cause or rival action (needs an `expose_liability` cause handler).
- **BL-3 · Staff-rider hire/departure wiring** *(#555)* — factory exists; hiring/departure
  don't yet create or flip-to-secret ledger entries.
- **BL-4 · Full-pipeline soak fidelity** *(#555)* — the mortality soak uses a controlled
  doom model in-test, not the full TurnManager rival/doom pipeline; a full-pipeline soak is
  a follow-up (does not weaken the current proof).
- **BL-5 · Action-taking vetting bots** *(#554)* — WS-C brackets seeds by event-choice
  policy only; greedy-safety / capability-rush action-taking bots are a seam.

## Engineering errands — batched cleanup pass

- **EE-7 · Loss-legibility UI pass** *(workshop #2 beat 3, ADR-0012)* — per-resource
  per-turn delta indicators near resource symbols; event-log improvement. Motivation:
  the one human ledger-death specimen was low-res ("I don't recall… the feeling that I
  was losing things badly"); future specimens need to be readable.
- **EE-8 · Sweep death attribution** *(ADR-0012)* — exploit-finder must attribute
  deaths to root-cause chains (default→rep→funding→doom is a *ledger* death); current
  "dies of doom" hides the cascade. Prerequisite to all ADR-0013 tuning.

- **EE-1 · Legacy `game_controller`/`end_game_screen` path** *(#550)* — constructs
  `ScoreEntry` with `doom_integral`=0 + unversioned board; appears superseded. Remove or
  wire to new scoring.
- **EE-2 · Save/load serialization** *(#552, #555)* — `triggered_events`/`event_cooldowns`
  (WS-0) and ledger entries (WS-1) aren't rebuilt by `from_dict`. Replay is unaffected
  (rebuilds from turn 0); a mid-game **save/load** would forget them. One save/load pass
  clears both.
- **EE-3 · Delete website composite formula** *(#550, cross-repo)* — `pdoom1-website/
  scripts/verification_logic.py` still holds the old formula; delete, not sync (ADR-0002).
- **EE-4 · Website static-JSON board wiring** *(#551, cross-repo)* — wire the exported
  replay artifact to the static-JSON board path. Postgres stays parked (ADR-0006).
- **EE-5 · Vetting envelope config source** *(#554)* — envelope thresholds are a passable
  dict (default provided); wiring to a JSON/league config file is a seam.
- **EE-6 · Schedule content pipeline** *(#554, content)* — ADR-0005 names `pdoom-data` as
  feedstock (real timeline → scheduled causes); mechanism exists, content pipeline unbuilt.

---
*Register opened 2026-07-05 (post WS-0). Last synced after WS-1 #555.*
