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
- **DQ-19 · Character creation surface** — parked. Attached question (Pip: "the right
  question"): does founder background **type the starting channels/connections** —
  ex-academic → research-sight affinity, ex-finance → doors/VC access, ex-journalist →
  media-sight? Moves ADR-0004's channel-investment build-identity axis partially to turn
  zero. Overlaps DQ-4 (re-roll within seed). Starting connections as a config lever.
- **DQ-20 · Risk pools** — Pip's gloss, logged not designed: *"insurance/mutualisation -
  industry actors pooling exposure to AI incidents, and the pool itself becoming an actor
  with opinions about safety standards. Like how fire insurance invented building codes…
  the pool is a customer for safety work with actual pricing power."* ADR-0010 adjacency
  (adoption customer); mid-game unlock; candidate: governance-lane researchers can stand
  one up. Don't over-invest yet.
- **DQ-21 · Intermediary vocabulary v1 — SEEDED** *(ADR-0015; Pip 2026-07-13)* — Pip's
  list, verbatim: `general_capability` (diffusion + mass adoption), `frontier_capability`
  (plus per-actor variants), `global_compute`, `global_dedicated_AI_compute` (smaller,
  scarcer, more valuable, likely controlled early), `something_for_attitudes_of_
  political_pressures` (naming owed), `ambient_capability_-_risk_background_levels`,
  `global_alarm`, `global_panic`. Form: **rate, accumulating** (~75% ruling) —
  experienced as a rate while history ticks the level up; 2017 spawn starts lower,
  builds slower than current balance. Doom **can** go down, but only at the end of long
  effort chains, priced in sacred objects. Semantics pass owed (lane strawmans for Pip
  veto): alarm-vs-panic distinction, the compute pair's roles, political-attitudes name.
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
