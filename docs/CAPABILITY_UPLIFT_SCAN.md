# Capability Uplift Scan -- ranked opportunity map (2026-07-25)

> **Status:** exploratory strategic scan, opinionated, decisions-for-Pip.
> Produced by a capability-analysis lane; every load-bearing claim below was
> verified against the repo (file reads / greps / gh queries) on 2026-07-25.
> Where a claim is inferred rather than verified it is tagged [INFERRED].
>
> **Question answered:** where is the highest-LEVERAGE uplift to this
> project's engineering + design capabilities over the coming month --
> investments that COMPOUND (make future work cheaper, safer, faster),
> not features?

---

## 0. Ground truth (verified 2026-07-25)

The frame for "the coming month": **Workshop 3 is 2026-07-29** (4 days out),
the release train is MONTHLY (ROADMAP ruling 2026-07-21), and v0.13 league
prep is live. Whatever gets invested in now is amortized across the WS-3
build lanes and every monthly epoch after.

State of the board, as measured:

- **Monolith carve is ahead of its own paperwork.** CARVE 1-4 are merged
  (commits 55b217ba, b92295f2, 08436a57, 25460e56/86740469): PlanController,
  SubmenuController, HiringPanelController, TravelPanelController all exist in
  `godot/scripts/ui/`. `main_ui.gd` is **2,259 lines** (was 3,786 at the
  2026-07-12 audit). `TECH_DEBT_REGISTER.md` still says 3,786.
- **Balance externalization (L9) substantially landed.** `godot/autoload/balance.gd`
  exists; `godot/data/actions/*.json` (10 files incl. `risk_contributions.json`)
  and `godot/data/events/{core_events,risk_events}.json` exist; `events.gd` is
  down to 525 lines (register said 1,483), `actions.gd` to 876 (register said
  2,665). The register materially understates progress -- it is itself rotting.
- **ADR-0017 (anti-hollow) is landed but has named open ends.**
  `test_smoke_load_all.gd` and `test_property_boot_invariants.gd` exist in the
  fast gate; `test_property_determinism.gd` in the sim tier. The ADR's own
  "Consequences / open questions" section still owes: adversarial mid-game
  save/load property coverage, and a headless "play N turns via the real
  GameManager signal path" smoke (UI-to-engine WIRING is still untested; only
  load-time parse breakage is caught).
- **The simulation tier is still non-blocking.** `godot-tests.yml` line 128:
  `continue-on-error: true`, with an in-file comment "promote to required once
  it is stable in CI". The last 10 runs of the workflow on main are all
  `success` (gh run list, 2026-07-22..25).
- **The balance instrument fleet is manual-only and constants-stale.**
  `godot/tests/manual/` holds a genuinely unusual asset: `test_exploit_sweep.gd`
  (5 bot policies x 20 seeds through the REAL turn loop, death attribution),
  `test_desperation_solver.gd` (isolate-one-mechanic solver),
  `test_opening_book_miner.gd` (96 random openings x seeds -> opening meta),
  `test_policy_sweep.gd`, all through a shared `l1_month_driver.gd`. Every one
  is excluded from CI by design and invoked by hand; the newest reports in
  `docs/balance/` are dated 2026-07-13/14; the solver and miner headers carry
  the same CAVEAT: "constants = dials-1-4 calibration ... dial-5 Attention pass
  pending + a stream re-calibration owed. Re-run before ... locks anything in."
- **Zero scheduled automation exists.** `grep cron .github/workflows/*.yml`
  matches nothing. Nothing runs nightly; every instrument fires only when a
  human remembers.
- **ADR-0004 (self-describing data) is accepted, migration 0% started.**
  `grep -rn 'schema_type|"$schema"' godot/data/` returns zero hits. The
  stopgap (skip `quirks.json` in `validate_historical_data.py`) is in place.
- **CI workflow sprawl with one live hazard.** 11 workflows. Four are
  docs/blog-sync flavored (`docs-sync`, `sync-documentation`, `sync-dev-blog`,
  `dev-blog-automation`). `dev-blog-automation.yml` interpolates
  `${{ github.event.pull_request.title }}` and `...body }}` DIRECTLY into an
  inline Python heredoc (lines ~125-126) -- a PR title containing a quote
  breaks the job, and a crafted title/body is template-injection into code
  that runs with the repo token. Classic GH-Actions injection shape.
- **The telemetry loop is open.** #800: the in-game bug reporter writes to
  the player's local disk and the confirmation text lies about transmission.
  #799 (install ping / update check) is filed, hotpatch-tier. Meanwhile the
  engine already produces exactly the artifacts a balance pipeline wants:
  deterministic replays + death attribution (ADR-0006, `verification_tracker.gd`),
  and `leaderboard_sync.gd` already knows how to phone home.
- **Dev-mode A/B wants are multiplying as one-offs.** #848 (live icon
  swapper), #819 (queue-feedback A/B dev toggle), #778 (dual layout A/B,
  loser-must-die), #788 (dev-mode badge on leaderboard runs). Four separate
  hand-rolled experiment switches in flight, no shared harness.

---

## 1. The portfolio at a glance

| # | Opportunity | Type | Effort | Compounds with |
|---|---|---|---|---|
| 1 | Balance Observatory: schedule the sweep fleet | Foundational | 2-3 days | monthly league, WS-3 lanes, every balance PR |
| 2 | ADR-0004 execution + schema registry + generated content index | Foundational | 2-4 days spread | content scale-up, pdoom-data, L4 event content |
| 3 | Close the telemetry loop (#800 + #799 -> pdoom-data) | Foundational | 3-5 days, cross-repo | Observatory (#1), playtesting, league ops |
| 4 | Anti-hollow completion: promote sim tier + wiring smoke | Robustness | 1-2 days | every future carve and WS-3 lane |
| 5 | CI pruning + injection fix | Quick win | 0.5-1 day | CI trust, agent throughput |
| 6 | Monolith ratchet gate | Quick win | 0.5 day | carve trajectory becomes irreversible |
| 7 | Generated ADR index + debt census (anti-rot extension) | Quick win | 1 day | #826 architecture map, agent onboarding |
| 8 | DevExperiments harness (generalize #848/#819/#778) | Structural, smaller | 1-2 days | art pipeline, UX decisions, #788 |

Ranking logic: (leverage per effort) x (how soon the compounding starts).
Items 1-3 are the foundational bets; 4 is cheap robustness with a deadline
logic (do it before WS-3 lanes fan out); 5-8 are quick wins any idle lane can
take.

---

## 2. Foundational bets

### BET 1 -- The Balance Observatory (my highest-conviction bet)

**What:** promote the manual sweep fleet (`tests/manual/`) from episodic
instrument to standing regression detector. Concretely:

1. Teach `run_godot_tests.py` a `--sweep` mode that runs `test_exploit_sweep`
   (and optionally the miner at reduced N) headlessly and emits a
   machine-readable summary (JSON: per-policy median survival, outcome mix,
   root-cause death mix, dominant-strategy gap) alongside the human report.
2. A scheduled workflow (the repo's FIRST cron) runs it nightly or 3x/week on
   main, uploads the report artifact, and diffs headline metrics against the
   previous run. Drift beyond thresholds (e.g. any policy's median survival
   moves >20%, or a policy becomes dominant) opens/comments an issue.
3. The monthly league cut gets a required "balance sign-off" artifact: the
   sweep report generated AT the epoch commit, attached to the release.

**Leverage -- why this compounds:** the deterministic engine + bot-policy
harness is this repo's single most differentiated engineering asset, and it
is currently write-only memory: reports go stale the moment constants move
(the solver's own header says the 07-13 calibration is already owed a re-run).
WS-3 will move mechanics again within days. Every mechanics/balance PR
currently ships with ZERO meta-level feedback; with the observatory, every
merge to main gets a free "did the strategy space shift?" answer the next
morning. This is the same honesty upgrade CI got in #640 -- "green means
tests ran" -- applied to game balance: "shipped means the meta was measured."
It also converts the monthly league obligation (ADR-0016 metabolism) from a
recurring manual chore into an artifact the pipeline produces.

**Effort:** 2-3 days. The hard parts already exist (driver, policies, death
attribution, determinism). New work is a summary emitter, one workflow file,
and a diff script. Ubuntu CI already runs headless Godot for the sim tier,
so the runtime path is proven.

**Dependencies:** none hard. Runtime cost: the exploit sweep is minutes at
NUM_SEEDS=20; cap miner N for CI. Constants churn during WS-3 will make the
diffs noisy for a week -- that is signal, not noise, but set thresholds loose
initially.

**First step:** add the JSON summary emitter to `test_exploit_sweep.gd`
(write next to `REPORT_PATH`), then a `balance-observatory.yml` with
`schedule: cron` + `workflow_dispatch`, uploading both artifacts. Diffing can
land a week later; the dated artifact trail is valuable from day one.

### BET 2 -- Execute ADR-0004: schema registry + self-describing data + generated content index

**What:** the ADR is accepted (2026-07-25) but zero files self-declare.
Build the actual machinery:

1. `godot/data/schemas/` as the registry (researcher, quirk, event, action,
   scenario, balance-default schemas -- several already exist for researchers).
2. `schema_type` field added folder-by-folder, starting with `researchers/`
   (retiring the #807 stopgap), then `events/`, `actions/`.
3. `validate_historical_data.py` dispatches on the declaration, never on
   directory. A file with no declaration = logged skip (per ADR).
4. The DQ_INDEX anti-rot pattern applied to CONTENT: a generated
   `docs/CONTENT_INDEX.md` (counts, ids, types, sources) regenerated by a
   script with a pre-commit `--check`, so the content surface is browsable
   and cannot silently rot.

**Leverage:** Pip's stated scale target is hundreds-to-thousands of events
flowing from pdoom-data with "minimal drift, wrongness, and operator
insanity" (ADR-0004's own words). Every content batch that lands after the
registry exists is validated for free; every batch that lands before it is
future migration debt. WS-2 lane L4 still owes event-content classification
(ADR-0012 taxonomy) -- doing that classification pass ON TOP of self-declared,
schema-validated files is strictly cheaper than doing it first and migrating
after. The voice/content pass pinned for v0.13 ("Rivals and News") multiplies
this again.

**Effort:** 2-4 days spread across lanes (the ADR itself mandates incremental,
folder-by-folder migration -- respect that; no big bang).

**Dependencies:** none hard; coordinates with pdoom-data contract design
(BET 3) but does not wait on it.

**First step:** registry + dispatch in the validator + migrate
`researchers/` (removes the stopgap). One PR, fully green, sets the pattern.

### BET 3 -- Close the telemetry loop: run artifacts flow home

**What:** fix #800 (bug reporter transmits for real -- plausibly via the same
path `leaderboard_sync.gd` already uses), ship #799 (install ping + update
check, already hotpatch-tier), and -- the capability part -- attach the
ALREADY-GENERATED run artifact (seed, version, turns survived, death
attribution root-cause, replay hash) to what comes home, landing in
pdoom-data as the first real ingestion feed.

**Leverage:** design capability is currently bottlenecked on anecdote (one
playtester, playtest write-ups). The engine already computes exactly the
fields a balance analyst wants, per run, deterministically -- they just die on
the player's disk. Once real-player runs land in pdoom-data, BET 1's
observatory gets a second data source: bot-policy sweeps say what is
POSSIBLE, player telemetry says what is HAPPENING. The monthly league
(ADR-0016 world-diff metabolism) is designed to be steered by exactly this.
This is also the honest-signal fix: the bug reporter currently TELLS players
it transmitted (#800's words: "confirmation text lies") -- same class of
integrity bug as hollow CI, player-facing this time.

**Effort:** 3-5 days and CROSS-REPO (website/endpoint + pdoom-data landing
zone + client). The riskiest of the three bets; probability it slips past
the month if started late: ~60%. Start the endpoint conversation early even
if the client work waits.

**Dependencies:** website/API repo; privacy posture decision (anonymous-by-
default install ping is already the #799 framing; run telemetry should ride
the same consent).

**First step:** fix #800 alone (transmit + honest confirmation). It is
already ship:hotpatch-48h-adjacent, self-contained, and forces the endpoint
question that the rest of the loop needs answered anyway.

---

## 3. Robustness with a deadline: finish the anti-hollow program (BET 4)

**What:** three items, all cheap, all named in ADR-0017's own open-questions
list or in the workflow comments:

1. **Promote the simulation tier to blocking.** The workflow comment says
   "promote to required once it is stable"; the last 10 main runs are green.
   Audit the sim JOB's individual history first (continue-on-error hides its
   failures from the workflow conclusion -- the 10/10 green proves the
   workflow, not the job [INFERRED until audited]), then flip
   `continue-on-error: false` and wire it into Test Summary.
2. **The UI-to-engine wiring smoke.** ADR-0017 explicitly notes load-time
   smoke does NOT exercise signal wiring. Post-CARVE, the controllers
   (PlanController, SubmenuController, ...) are exactly the seam such a test
   wants: a headless "boot main scene, queue 3 actions via PlanController,
   commit, run 6 turns via GameManager signals, assert alive+sane" smoke.
3. **Characterization tests per extracted controller** as a standing rule for
   the remaining carves (R1/R3/R6 in `MAIN_UI_SEAM_MAP.md`): before a seam is
   pulled, its observable behavior gets pinned. Red-first per ADR-0017:
   watch each new test fail against a mutated target once.

**Why the deadline logic:** WS-3 lanes fan out within a week. Every lane
inherits whatever gate exists on day one. A wiring smoke added AFTER six
lanes are mid-flight protects nothing retroactively.

**Effort:** 1-2 days. **First step:** the sim-job audit + flip (item 1) is
under an hour of work once the history is pulled.

---

## 4. Quick wins (any idle lane; each self-contained)

### QW-5: CI pruning + the injection fix

`dev-blog-automation.yml` interpolates PR title/body straight into inline
Python. Fix pattern: pass them as `env:` values and read `os.environ` (the
standard GH-Actions injection mitigation), or -- my actual recommendation --
RETIRE the workflow: it is legacy-smelling (its `lines_changed` heuristic
`(item.deleted_file and 100) or len(str(item.diff).split('\n'))` is not
measuring anything real), and the repo has three OTHER docs/blog sync
workflows. One consolidation pass: keep `docs-sync` + `sync-dev-blog`
[verify which the website actually consumes], park the rest. Every retired
workflow is CI minutes, noise, and one fewer thing lying about the repo's
health. Effort: 0.5-1 day.

**First step:** the env-var fix is 10 minutes and closes the injection hole
even if the retirement debate takes longer.

### QW-6: The monolith ratchet

A pre-commit/CI check (mirror `check_scene_nav.py`'s shape) that fails if
`godot/scripts/ui/main_ui.gd` exceeds a stored line ceiling, updated DOWNWARD
only. Current: 2,259. The carve trajectory (3,786 -> 2,259 in two weeks) is
excellent; the ratchet makes backsliding impossible when WS-3 lanes are
tempted to "just add one handler" to the monolith instead of the seam map's
controllers. Generalize later to any file over ~800 lines if it earns its
keep. Effort: 0.5 day. **First step:** `tools/check_file_ratchet.py` +
`ratchet.json` + one pre-commit entry.

### QW-7: Generated ADR index + debt census (extend the anti-rot pattern)

Two documented rot sites: `decisions/README.md` (CLAUDE.md says "trust the
files, the index is stale") and `TECH_DEBT_REGISTER.md` (verified stale
above: cites 3,786-line main_ui and 1,483-line events.gd; reality 2,259 and
525 -- the register UNDERSTATES two weeks of real progress, which misleads
planning in the pessimistic direction). Fix per the established DQ_INDEX
pattern: `generate_adr_index.py` (status/date/title scraped from ADR
headers) with a pre-commit `--check`; plus a generated "census" appendix to
the register (line counts of named monoliths, `print()` counts, test counts)
so the measurable half of the register can never rot again. Feeds #826
(rendered architecture map) directly. Effort: 1 day.

### QW-8: DevExperiments harness

One registry autoload for named dev-mode experiment toggles (variant lists,
cycle/A-B, persisted choice, dev-overlay surfacing), then #848 (icon
swapper), #819 (queue-feedback A/B), #778 (layout A/B) become entries
instead of three hand-rolled switch mechanisms. Integrates with #788
(dev-mode badge on leaderboard) since "any experiment active" is now one
query. The art-review pipeline's gallery->in-game gut-check loop (#848's
stated purpose) gets its in-game half as a durable surface, not a one-off.
Effort: 1-2 days. **First step:** build the registry WITH #848 as its first
client -- do not build the harness speculatively.

---

## 5. What I would invest in, in order (the opinionated part)

If I were you, the month looks like this:

1. **Before WS-3 (this week):** BET 4 items 1-2 (sim-tier promotion + wiring
   smoke) and QW-6 (ratchet). Cheap, and they harden the floor every WS-3
   lane will stand on. QW-5's 10-minute injection fix same day.
2. **The week of WS-3:** BET 1, the Balance Observatory. WS-3 moves mechanics;
   the observatory is most valuable when installed BEFORE the churn so the
   drift trail captures it. This is my single highest-conviction bet: it
   turns the repo's most differentiated asset (deterministic engine + bot
   fleet) from a hand-cranked instrument into a standing capability, and the
   monthly league makes its output a recurring deliverable, not a curiosity.
   Probability it pays for itself within two epochs: ~85%.
3. **WS-3 build-lane weeks:** BET 2 folder-by-folder (each content-touching
   lane migrates the folder it touches -- the ADR already mandates exactly
   this shape), QW-7 and QW-8 as idle-lane filler.
4. **Started early, finished when cross-repo allows:** BET 3, beginning with
   the #800 honest-transmit fix now and the pdoom-data landing zone as the
   month's stretch goal.

What I deliberately did NOT rank highly: further speculative main_ui carving
(the seam map already correctly says opportunistic-only; the ratchet is the
cheap enforcement), new test-count growth for its own sake (72 fast-gate
files with a 300-test floor is healthy; the GAPS are wiring + sim promotion,
not volume), and any big-bang data migration (ADR-0004 explicitly forbids
it).

The common thread across all eight: this repo's proven best trick is turning
a one-time fix into a STANDING GUARANTEE (hollow CI -> JUnit floor; scene-nav
crash -> chokepoint + checker; DQ rot -> generated index + staleness gate;
emoji leak -> blocking gate). The month's leverage is applying that same
move to balance (observatory), content (schema registry), player evidence
(telemetry), and the monolith (ratchet).
