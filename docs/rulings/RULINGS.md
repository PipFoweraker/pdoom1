# Rulings index (GENERATED -- do not hand-edit)

> Derived from `RULING:` declarations in tracked files by
> `scripts/generate_rulings.py`. Regenerate with
> `python scripts/generate_rulings.py`. The convention, and why it looks
> like this, is argued in `docs/rulings/RULINGS_CONVENTION.md`.

**59 ruling(s)** across **16 flavour(s)**. **244** prose ruling(s) not yet declared.

## One index, five sources

Consolidated 2026-08-21. The estate had five places rulings were recorded;
they are GENRES, not rivals, so the record is unified here while the sources
keep their form. An ADR is a full argument and a transcript is evidence --
flattening either into one line would delete what makes it worth having.

| kind | n | what it is | where |
|---|---:|---|---|
| `declaration` | 33 | a `RULING:` line written next to what it governs | anywhere |
| `adr` | 20 | a full architecture argument, summarised here | `docs/game-design/decisions/` |
| `session` | 3 | a transcript or workshop ruling set, pointed at | `docs/SPOKEN_*`, `*RULINGS*` |
| `card` | 3 | the input a ruling was made from | `docs/decision-cards/` |

## By flavour

Recall by flavour is the point: before ruling on something, look for the
flavour it belongs to and read what was already decided there.

### `architecture`

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-07-04 | ADR-0001 -- Situational Awareness as the primary sink ("spending buys sight") | -- none -- | `docs/game-design/decisions/ADR-0001-spending-buys-sight.md:1` |
| 2026-07-04 | ADR-0002 -- Scoring: turns survived, lexicographic doom-integral tiebreak, flows only | -- none -- | `docs/game-design/decisions/ADR-0002-scoring-turns-survived.md:1` |
| 2026-07-04 | ADR-0003 -- The Liability Ledger (two-sided): every mitigation is a loan | -- none -- | `docs/game-design/decisions/ADR-0003-liability-ledger.md:1` |
| 2026-07-04 | ADR-0004 -- SA amended: channels with provenance, lead-time semantics, decision-flip test | -- none -- | `docs/game-design/decisions/ADR-0004-sa-channels-lead-time.md:1` |
| 2026-07-04 | ADR-0005 -- Emergent doom waves: author causes, never outcomes; seed = RNG + schedule | -- none -- | `docs/game-design/decisions/ADR-0005-emergent-waves-seed-schedules.md:1` |
| 2026-07-04 | ADR-0006 -- The replay string is the canonical run artifact; backend wiring order | -- none -- | `docs/game-design/decisions/ADR-0006-replay-artifact-backend.md:1` |
| 2026-07-04 | ADR-0007 -- Alliances: the third client of Ledger + SA (treaty = shared liability + shared sight) | -- none -- | `docs/game-design/decisions/ADR-0007-alliances-third-client.md:1` |
| 2026-07-04 | ADR-0008 -- Deferrals, folds, and rejections (the negative space of workshop #1) | -- none -- | `docs/game-design/decisions/ADR-0008-deferrals-and-rejections.md:1` |
| 2026-07-12 | ADR-0009 -- Turn structure: plan-months, two decision speeds, day as resolution tick | -- none -- | `docs/game-design/decisions/ADR-0009-plan-months-two-speeds.md:1` |
| 2026-07-12 | ADR-0010 -- Adoption routing (soft-with-teeth): doom bends where work is adopted | -- none -- | `docs/game-design/decisions/ADR-0010-adoption-routing.md:1` |
| 2026-07-12 | ADR-0011 -- The effort economy: founder hours, staff lanes, manager compression | -- none -- | `docs/game-design/decisions/ADR-0011-effort-economy.md:1` |
| 2026-07-12 | ADR-0012 -- Event response taxonomy: un-snoozable, deferrable, expiring | -- none -- | `docs/game-design/decisions/ADR-0012-event-response-taxonomy.md:1` |
| 2026-07-12 | ADR-0013 -- Financing instruments & the cost-of-debt engine | -- none -- | `docs/game-design/decisions/ADR-0013-cost-of-debt-engine.md:1` |
| 2026-07-12 | ADR-0014 -- Conferences, presence, and minimal location | -- none -- | `docs/game-design/decisions/ADR-0014-conferences-presence-location.md:1` |
| 2026-07-13 | ADR-0015 -- No printed doom deltas: doom is computed from world state | -- none -- | `docs/game-design/decisions/ADR-0015-no-printed-doom-deltas.md:1` |
| 2026-07-13 | ADR-0016 -- League metabolism: the game trails reality by one month | -- none -- | `docs/game-design/decisions/ADR-0016-league-metabolism.md:1` |
| 2026-07-17 | ADR-0017 -- Anti-hollow test strategy (load-time smoke + property-based invariants) | -- none -- | `docs/game-design/decisions/ADR-0017-anti-hollow-test-strategy.md:1` |
| 2026-07-27 | ADR-0018 -- Render-only office doctrine: no spatial fact becomes a gameplay input | -- none -- | `docs/game-design/decisions/ADR-0018-render-only-office-doctrine.md:1` |
| 2026-08-03 | ADR-0019 -- Pull-from-demand asset pipeline: the pack is a function of declared demand | -- none -- | `docs/game-design/decisions/ADR-0019-pull-from-demand-asset-pipeline.md:1` |
| 2026-08-23 | ADR-0020 -- Machine actor identity: a bot acts under its own name, or the attribution record is fiction | -- none -- | `docs/game-design/decisions/ADR-0020-machine-actor-identity.md:1` |

### `art-provenance`

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-15 | Tier W (website disclosure) ships first and standalone; Tier G (in-game motifs and epoch marks) stays ruled-but-unbuilt | `docs/art/MOTIF_AND_WATERMARK_PROTOCOL.md` | `docs/rulings/LEDGER.md:12` |
| 2026-08-15 | an embedded CA-signed C2PA credential outranks every provenance heuristic; it becomes evidence tier S and resolves an asset out of the unknown set | `tools/assets/backfill_provenance.py credential_origin` | `docs/rulings/LEDGER.md:14` |
| 2026-08-19 | New-Bort is the working machine and hosts new archives and images; the generated masters are NOT transferred to it but coordinated on an external drive or the upstream system, so a verdict whose art is absent is the designed steady state and orphan keys are never pruned | `this reporting line, and tools/art_review/ORPHANS_2026-08-15.md A1/A2` | `tools/art_review/build_full_gallery.py:808` |
| 2026-08-19 | every asset record names its author as well as its origin, with a named agent only where a source already in the repo names one and `unattributed` everywhere else, never inferred | `backfill_provenance.py --apply-authors, and classify() stamping it on a full re-run` | `tools/assets/backfill_provenance.py:555` |
| 2026-08-19 | the provenance guard compares against the git blob, not the working tree, and runs in pre-commit and CI; a guard wired to nothing is a document | `.pre-commit-config.yaml provenance-check + quality-checks.yml, both running --self-test first` | `tools/assets/check_provenance.py:65` |

### `art-review-vocabulary` (only one so far)

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-15 | flaw:<thing> joins the harvest vocabulary as the negative counterpart to element:, because the sweeps are mostly negative and prose cannot be counted | `tools/art_review/serve_review.py HARVEST_DOC, emitted to docs/art/NOMENCLATURE.md` | `docs/rulings/LEDGER.md:13` |

### `ci-gates`

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-22 | a check that fails 100% of the time is not a check; chronic red trains the team to ignore red, so a permanently-failing gate must be either fixed or explicitly declared, never left standing | `the chronic-red census in guards.yml, which gates on this since 2026-08-29 (issue #1279)` | `.github/workflows/docs-sync.yml:134` |
| 2026-08-24 | a command's exit status must be read from the command, never through a pipe: $? after a pipeline is the RIGHTMOST command's status, so `tool | tee`, `tool | head` and `tool | tail` all discard the tool's verdict and report the wrapper's success | `this workflow, and live-site-release-freshness.yml` | `.github/workflows/release-ledger.yml:102` |
| 2026-08-24 | a gate's verdict must be traced to a consumer before it is called a gate: a red that blocks no merge, gates no job, and reaches no human is theatre, and it costs attention as well as buying nothing | `this audit, and docs/deployment/RELEASE_FLOW_MAP_2026-08-24.md` | `docs/deployment/GATE_AUDIT_2026-08-24.md:949` |
| 2026-08-24 | a workflow that writes anything must declare `permissions:`, because this repo's default workflow token is read-only and a write attempt without one 403s into either a permanent meaningless red or, under continue-on-error, a green that hides it | `gh api repos/PipFoweraker/pdoom1/actions/permissions/workflow` | `docs/deployment/GATE_AUDIT_2026-08-24.md:951` |
| 2026-08-24 | two workflows firing on the same event with no dependency between them are not parallel, they are racing to a verdict nobody joins: on the first v0.14.3 tag pre-release-checks found RN003 at t+21s and enhanced-release found the same defect at t+4m39s after a full three-platform build, so the cheap gate bought nothing | `docs/deployment/RELEASE_FLOW_MAP_2026-08-24.md` | `docs/deployment/RELEASE_FLOW_MAP_2026-08-24.md:568` |

### `estate-process`

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-15 | the ruling road is cross-repo from day one, federated: each repo scans itself and emits rulings.json, an aggregator reads them, nothing writes back | `scripts/generate_rulings.py` | `docs/rulings/LEDGER.md:10` |
| 2026-08-15 | naming a mechanism is OPTIONAL on a ruling, and the generated index reports which rulings have none | `scripts/generate_rulings.py` | `docs/rulings/LEDGER.md:11` |
| 2026-08-17 | published figures live in tooling, not prose: the line item is the atom and every rendering is a projection | `tools/render_budget.py --check` | `tools/render_budget.py:12` |

### `guard-doctrine`

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-24 | an environment no workflow references is either clutter or a lie, and which one depends entirely on what it is called; a safety-vocabulary name with no reference is a finding, any other name is reported and not gated | `tools/check_environments.py in .github/workflows/guards.yml` | `tools/check_environments.py:51` |
| 2026-08-24 | a guard wired only to pre-commit is not installed; every local hook must either run in a workflow or carry a declared waiver naming what covers it instead | `tools/check_guard_parity.py --check in .github/workflows/guards.yml` | `tools/check_guard_parity.py:47` |
| 2026-08-29 | a workflow red for three consecutive runs of the same trigger must be fixed or declared, because an undeclared chronic red makes every later red unreadable | `tools/check_chronic_red.py --check in .github/workflows/guards.yml` | `tools/check_chronic_red.py:47` |
| 2026-08-30 | a CI fossil must be removed entirely, never declared: a red that cannot clear trains the team to discount reds, and a declaration for one can never go stale, so the register of exceptions would grow forever | `tools/check_chronic_red.py --check fails on any fossil, so a new one must be purged or its trigger restored` | `docs/CI_FOSSILS_2026-08-30.md:27` |

### `ladder-epochs`

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-23 | ~~ladder debt is paid when it is incurred, not deferred to build time, so a fresh epoch never inherits a forked board key~~ (superseded by `pdoom1:2026-08-23:fa830705`) | `tools/check_ladder_bump.py --owed` | `tools/check_ladder_bump.py:38` |
| 2026-08-23 | ladder debt is DECLARED when incurred and PAID at the release that ships it; deferring is legal, forgetting is not, and the epoch must never fork on an ordinary gameplay PR | `tools/check_ladder_bump.py --owed, run at cut time` | `tools/check_ladder_bump.py:40` |
| 2026-08-24 | the diegetic-opening redesign (M24-002..009) must not be ladder- or epoch-breaking | ``tools/check_ladder_bump.py`` | `docs/game-design/DESIGN_2026-08-24_diegetic-opening.md:16` |

### `league-seeds`

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-24 | the featured seed names the ISO week the league opens in, so a league that slips is renamed to the week it actually runs and the slip is recorded in the log, never hidden in the label | `godot/autoload/game_config.gd get_weekly_seed` | `godot/autoload/game_config.gd:550` |
| 2026-08-24 | the featured seed names the ISO week the league opens in | `godot/tests/unit/test_iso_week_seed.gd` | `godot/tests/unit/test_iso_week_seed.gd:24` |

### `mechanical-inertness` (only one so far)

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-22 | a mechanic that charges the player and does nothing observable gets an unsubtle placeholder consequence NOW rather than waiting for a balanced one; players need to suffer, and balance comes later | `this test file, and the fix-by dates on the inertness issues` | `godot/tests/unit/test_ad_campaign_is_visible.gd:11` |

### `player-feedback` (only one so far)

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-23 | player feedback routes to the PUBLIC issue tracker and is triaged and summarised before the developer reads it; it never lands in a personal inbox, and the player is told this in the panel | `BugReporter.ROUTING_TEXT and its tests` | `godot/scripts/core/bug_reporter.gd:328` |

### `release-artifacts` (only one so far)

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-24 | a published release artifact states a platform shipped only by enumerating an asset that exists, never by a naming convention or a hardcoded list, and where presence cannot be observed it says UNKNOWN instead of advertising a URL | `generate_release_metadata.audit_advertised_platforms and generate_release_manifest.derive_platforms` | `scripts/generate_release_metadata.py:91` |

### `release-cadence`

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-24 | every value version.txt has ever held must have a matching git tag, or a declared exemption; a bump with no tag is a defect the machine reports, not a thing a human is expected to remember | `tools/check_release_ledger.py` | `tools/check_release_ledger.py:34` |
| 2026-08-24 | a minor version bump ALWAYS cuts the ladder, and the ladder MAY ALSO cut mid-version whenever gameplay forks; therefore ladder epochs >= minor versions, always, and the ladder epoch is NEVER forecastable | `tools/generate_release_horizon.py` | `tools/generate_release_horizon.py:37` |

### `releases` (only one so far)

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-24 | a release must be verified before it is published, not after: verify-release-urls runs downstream of create-github-release, so on v0.14.3 the macOS 404 was proven at 04:37:34 against a release that had been public since 04:37:16, and there is no un-publish | `.github/workflows/enhanced-release.yml, and docs/deployment/RELEASE_FLOW_MAP_2026-08-24.md` | `docs/deployment/RELEASE_FLOW_MAP_2026-08-24.md:566` |

### `session-record`

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-07-29 | WS3 ENDGAME RULINGS 2026-07-29 | -- none -- | `docs/game-design/WS3_ENDGAME_RULINGS_2026-07-29.md:1` |
| 2026-07-31 | SPOKEN COMMENTS 2026-07-31 league-night | -- none -- | `docs/SPOKEN_COMMENTS_2026-07-31_league-night.md:1` |
| 2026-08-01 | 2026-08-01 dev-powers-nomenclature | -- none -- | `docs/decision-cards/2026-08-01_dev-powers-nomenclature.html:1` |
| 2026-08-01 | 2026-08-01 seed-authority | -- none -- | `docs/decision-cards/2026-08-01_seed-authority.html:1` |
| 2026-08-02 | SPOKEN RULINGS 2026-08-02 playtest-and-cards | -- none -- | `docs/SPOKEN_RULINGS_2026-08-02_playtest-and-cards.md:1` |
| 2026-08-02 | 2026-08-02 pdoom-data-contract | -- none -- | `docs/decision-cards/2026-08-02_pdoom-data-contract.md:1` |

### `silent-failure`

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-23 | silent failures are a named defect class and the counter is instrumentation, never vigilance; a failure representable in its own success type must be made countable rather than watched for | `this register, and the census/aggregate/differential counters it names` | `docs/design/SILENT_FAILURE_REGISTER.md:116` |
| 2026-08-24 | a best-effort platform build that fails must be TRACKED, not merely warned about: the release still publishes for the platforms that built, and the absence becomes ONE rolling per-platform issue plus a machine-readable build-status.json field the website reads, so a download page says "build coming" with a link instead of advertising a URL that 404s or pointing at an older release | `scripts/check_platform_builds.py + scripts/report_missing_build_issue.py, run by the platform-build-status job below` | `.github/workflows/enhanced-release.yml:240` |
| 2026-08-24 | a player-facing surface must not collapse distinct failures into one reassuring sentence: each cause gets its own words, its own consequence and its own way for the player to report it | `this table and godot/tests/unit/test_whats_new_states.gd, which fails if any two rows share a body or a code` | `godot/scripts/ui/whats_new_modal.gd:87` |

### `ui-legibility` (only one so far)

| date | ruling | mechanism | source |
|---|---|---|---|
| 2026-08-17 | the game has ONE font-size lever (theme/base_theme.tres default_font_size, registered as the project theme) and a raw size override is a deviation that has to earn its line | `tools/check_font_sizes.py` | `tools/check_font_sizes.py:16` |

## Nothing will re-ask these

Rulings with no `mechanism:`. Pip's doctrine (2026-08-11): what forces a
question to be resolved later is a MECHANISM, not a document. This section
reports, it does not block -- naming a mechanism is optional by design, and
an empty list here is not a goal.

- `pdoom1:2026-07-04:12de8fc2` -- ADR-0001 -- Situational Awareness as the primary sink ("spending buys sight") (`docs/game-design/decisions/ADR-0001-spending-buys-sight.md:1`)
- `pdoom1:2026-07-04:ffa37090` -- ADR-0002 -- Scoring: turns survived, lexicographic doom-integral tiebreak, flows only (`docs/game-design/decisions/ADR-0002-scoring-turns-survived.md:1`)
- `pdoom1:2026-07-04:ffbe9dcc` -- ADR-0003 -- The Liability Ledger (two-sided): every mitigation is a loan (`docs/game-design/decisions/ADR-0003-liability-ledger.md:1`)
- `pdoom1:2026-07-04:7b17a204` -- ADR-0004 -- SA amended: channels with provenance, lead-time semantics, decision-flip test (`docs/game-design/decisions/ADR-0004-sa-channels-lead-time.md:1`)
- `pdoom1:2026-07-04:7530dbcd` -- ADR-0005 -- Emergent doom waves: author causes, never outcomes; seed = RNG + schedule (`docs/game-design/decisions/ADR-0005-emergent-waves-seed-schedules.md:1`)
- `pdoom1:2026-07-04:3f10ce2e` -- ADR-0006 -- The replay string is the canonical run artifact; backend wiring order (`docs/game-design/decisions/ADR-0006-replay-artifact-backend.md:1`)
- `pdoom1:2026-07-04:c3c13f7a` -- ADR-0007 -- Alliances: the third client of Ledger + SA (treaty = shared liability + shared sight) (`docs/game-design/decisions/ADR-0007-alliances-third-client.md:1`)
- `pdoom1:2026-07-04:d4bc649b` -- ADR-0008 -- Deferrals, folds, and rejections (the negative space of workshop #1) (`docs/game-design/decisions/ADR-0008-deferrals-and-rejections.md:1`)
- `pdoom1:2026-07-12:61fc328b` -- ADR-0009 -- Turn structure: plan-months, two decision speeds, day as resolution tick (`docs/game-design/decisions/ADR-0009-plan-months-two-speeds.md:1`)
- `pdoom1:2026-07-12:52b9ee21` -- ADR-0010 -- Adoption routing (soft-with-teeth): doom bends where work is adopted (`docs/game-design/decisions/ADR-0010-adoption-routing.md:1`)
- `pdoom1:2026-07-12:48b249fb` -- ADR-0011 -- The effort economy: founder hours, staff lanes, manager compression (`docs/game-design/decisions/ADR-0011-effort-economy.md:1`)
- `pdoom1:2026-07-12:2d44a688` -- ADR-0012 -- Event response taxonomy: un-snoozable, deferrable, expiring (`docs/game-design/decisions/ADR-0012-event-response-taxonomy.md:1`)
- `pdoom1:2026-07-12:881c9a5d` -- ADR-0013 -- Financing instruments & the cost-of-debt engine (`docs/game-design/decisions/ADR-0013-cost-of-debt-engine.md:1`)
- `pdoom1:2026-07-12:cc6e8c3e` -- ADR-0014 -- Conferences, presence, and minimal location (`docs/game-design/decisions/ADR-0014-conferences-presence-location.md:1`)
- `pdoom1:2026-07-13:e5650a4c` -- ADR-0015 -- No printed doom deltas: doom is computed from world state (`docs/game-design/decisions/ADR-0015-no-printed-doom-deltas.md:1`)
- `pdoom1:2026-07-13:914bdd09` -- ADR-0016 -- League metabolism: the game trails reality by one month (`docs/game-design/decisions/ADR-0016-league-metabolism.md:1`)
- `pdoom1:2026-07-17:09d2b5eb` -- ADR-0017 -- Anti-hollow test strategy (load-time smoke + property-based invariants) (`docs/game-design/decisions/ADR-0017-anti-hollow-test-strategy.md:1`)
- `pdoom1:2026-07-27:650d3819` -- ADR-0018 -- Render-only office doctrine: no spatial fact becomes a gameplay input (`docs/game-design/decisions/ADR-0018-render-only-office-doctrine.md:1`)
- `pdoom1:2026-07-29:6893faf0` -- WS3 ENDGAME RULINGS 2026-07-29 (`docs/game-design/WS3_ENDGAME_RULINGS_2026-07-29.md:1`)
- `pdoom1:2026-07-31:3ad565a5` -- SPOKEN COMMENTS 2026-07-31 league-night (`docs/SPOKEN_COMMENTS_2026-07-31_league-night.md:1`)
- `pdoom1:2026-08-01:e138b8ef` -- 2026-08-01 dev-powers-nomenclature (`docs/decision-cards/2026-08-01_dev-powers-nomenclature.html:1`)
- `pdoom1:2026-08-01:96a2a6f0` -- 2026-08-01 seed-authority (`docs/decision-cards/2026-08-01_seed-authority.html:1`)
- `pdoom1:2026-08-02:6c6d32f9` -- SPOKEN RULINGS 2026-08-02 playtest-and-cards (`docs/SPOKEN_RULINGS_2026-08-02_playtest-and-cards.md:1`)
- `pdoom1:2026-08-02:327d595d` -- 2026-08-02 pdoom-data-contract (`docs/decision-cards/2026-08-02_pdoom-data-contract.md:1`)
- `pdoom1:2026-08-03:fb9eeed6` -- ADR-0019 -- Pull-from-demand asset pipeline: the pack is a function of declared demand (`docs/game-design/decisions/ADR-0019-pull-from-demand-asset-pipeline.md:1`)
- `pdoom1:2026-08-23:278981bd` -- ADR-0020 -- Machine actor identity: a bot acts under its own name, or the attribution record is fiction (`docs/game-design/decisions/ADR-0020-machine-actor-identity.md:1`)

## UNDECLARED -- prose that reads like a ruling

Found by heuristic scan. These are a WORK LIST, not rulings: each needs a
`RULING:` line, or is a false positive to ignore. They are listed rather
than dropped because an index that silently omits looks complete when it
is not.

- `.github/workflows/guards.yml:3` -- # WHY THIS FILE EXISTS (issue #1265, ruled by Pip 2026-08-20)
- `CHANGELOG.md:303` -- was retimed to one-turn-one-month and the ruled promotions were applied (#1137),
- `CHANGELOG.md:334` -- and the ruled promotions applied (#1137), against Pip's rulings of 2026-08-04.
- `CHANGELOG.md:342` -- - **The last player-facing "AP" is gone**, and one number format is ruled across
- `CLAUDE.md:226` -- quarterly pins to v0.15; league/content cadence is MONTHLY (ruled 2026-07-21).
- `CLAUDE.md:254` -- `UNDECLARED`, never dropped. **Cross-repo by design** (ruled 2026-08-15):
- `art_source/pixellab_2026-07-26_cat_sweep/MANIFEST.md:3` -- Execution of Pip's locked recipe (ruled 2026-07-26, "go cat sweep 8 dir now"):
- `docs/CONTENT_DISTRIBUTION_SYSTEM.md:10` -- > **SUPERSEDED, not merely "outdated in spirit", as of 2026-08-13.** Pip ruled
- `docs/DEV_BLOG_DECISION_2026-08-21.md:155` -- Pip ruled **option A**: archive the pygame-era entries, keep the 2026-07-22 post.
- `docs/GLOSSARY.md:278` -- Naming (ruled 2026-07-29, Pip): gates are written name-first with a 1-6
- `docs/GLOSSARY.md:477` -- ## Observed inconsistency (flagged, not ruled)
- `docs/HANDOVER_2026-08-06_EVENING.md:43` -- He ruled on it Tuesday and it was never built. B1 and B2 refer to the proposals in
- `docs/HANDOVER_2026-08-24_pdoom1_seat.md:141` -- immediately with an offer to revert; he ruled keep. The changes were verified
- `docs/HANDOVER_2026-08-24_pdoom1_seat.md:45` -- ## 2. What was ruled today
- `docs/ISSUE_MINING_2026-08-06.md:191` -- having ruled. W3 ruled. Any survivor is now ordinary work with a known spec,
- `docs/ISSUE_MINING_2026-08-06.md:350` -- overlay and called it *"kind of cool"*, then correctly ruled it out of scope
- `docs/ISSUE_MINING_2026-08-06.md:357` -- UI work; Pip ruled decomposition deferred until the game is out. These are
- `docs/ISSUE_MINING_2026-08-06.md:412` -- touched); the #1037 identifier rename (its author already ruled "separate PR, or
- `docs/ISSUE_TRIAGE_2026-08-06.md:182` -- F3 event injection. Pip ruled the fix is to REMOVE the debug event-trigger, not
- `docs/ISSUE_TRIAGE_2026-08-06.md:73` -- historical patch notes and the dev overlay, both ruled legitimate by that
- `docs/LEADERBOARD_WEBSITE_INTEGRATION.md:217` -- Pip ruled on 2026-08-08 that the board should carry **both** an Operator (the
- `docs/LEDGER_ROW_PROTOCOL_2026-08-21.md:25` -- ## Amendment 1 -- ROLL, NOT BLESS-IN-PLACE (ruled 2026-07-31)
- `docs/LEDGER_ROW_PROTOCOL_2026-08-21.md:50` -- thing being ruled out.
- `docs/NUMBER_FORMATS.md:91` -- 1. **Behaviour** -- the formatters produce the formats ruled above, for the exact
- `docs/POSTMORTEM_2026-08-07_CAPTURE.md:330` -- Filed during the cycle as **#1165**, and ruled in `coordination#35` where
- `docs/POSTMORTEM_SATURDAY_ITEMS_2026-08-08.md:52` -- ### Ruled by Pip, 2026-08-08 ~01:00
- `docs/PRIVACY.md:5` -- > model ruled 2026-07-26: tier 1 identity data (leaderboard) = explicit
- `docs/PRIVACY_POSTURE.md:3` -- **Ruled by Pip 2026-07-26** (identity-consent ruling + approved ping-decoupling,
- `docs/SPOKEN_RULINGS_2026-08-02_playtest-and-cards.md:11` -- **The asks, crisply:** ship the alpha-tools wording as ruled (section 2); adopt the release manifest as the seed publication surface with `weekly-2026-w31` as canonical format (section 3); raise the f
- `docs/TRIUMVIRATE_METABOLIC_CYCLE.md:352` -- 3. **Telemetry privacy posture -- RULED 2026-07-25** (was: undecided).
- `docs/TRIUMVIRATE_METABOLIC_CYCLE.md:77` -- Direction discipline (already ruled, restated): pdoom1 never depends on
- `docs/archive/2026-07-25-reconcile/PHASE3_DEPLOY_RECON.md:149` -- date-correct weekly generator contradicts the ruled MONTHLY cadence anyway).
- `docs/archive/2026-07-25-reconcile/PHASE3_DEPLOY_RECON.md:25` -- MONTHLY league cadence ruled; each month = world-update pack + new baseline
- `docs/art/A4_COLLAPSE_2026-08-20.md:3` -- **2026-08-20, `pdoom1` seat on New-Bort.** Ruled by Pip: canonicalise on the write
- `docs/art/ART_MASTERS_POLICY.md:1` -- # Art masters policy (RULED 2026-07-22)
- `docs/art/ART_MASTERS_POLICY.md:12` -- RULED 2026-07-25). Chosen over MinIO-on-instance / external R2/B2 because it
- `docs/art/ENDGAME_CONCEPT_REVIEW_2026-07-29.md:29` -- > **PROVISIONAL -- ruled by Pip, 2026-07-29.** Treat A1-A10 as **guidelines on
- `docs/art/MOTIF_AND_WATERMARK_PROTOCOL.md:366` -- transport. Nothing to build until the schema is ruled.
- `docs/art/MOTIF_AND_WATERMARK_PROTOCOL.md:410` -- It changes no assets and can run before any of this is ruled on.
- `docs/art/NOTE_2026-08-15_colour-as-identity.md:3` -- > **Status: captured intent, nothing ruled.** Dictated by Pip on the morning of
- `docs/art/NOTE_2026-08-15_colour-as-identity.md:65` -- These are already ruled elsewhere and any colour-identity system inherits them:
- `docs/art/PROP_MANIFEST.md:32` -- | `style_tags` | office quality tiers this art serves, from the canonical ladder `"scummy"` / `"decent"` / `"premium"` (ruled 2026-07-26; `docs/game-design/SEED_ASSET_REGISTRY_AND_VERDICTS.md`). Tier-
- `docs/art/SPRITE_GENERATION_PLAN.md:7` -- ## Design foundation (RULED 2026-07-16 -- see WORKSHOP_2_BACKLOG "Character sprite system")
- `docs/art/audit_2026-08-13/PROVENANCE_COMPLETENESS.md:638` -- identical byte length is not ruled out.
- `docs/art/audit_2026-08-13/RETENTION_ANALYSIS.md:251` -- byte in the tree** -- the biggest files are precisely the ones nobody has ruled on.
- `docs/balance/DIAL5_ATTENTION_SCARCITY_PROPOSALS.md:101` -- - **C is orthogonal** -- a time multiplier that rides on top of whatever supply/demand shape you pick. Nearly free to ratify (direction already ruled), most gated on "wait for a month to complete" for
- `docs/balance/DIAL5_ATTENTION_SCARCITY_PROPOSALS.md:109` -- **One-sentence rationale:** Keep the ruled ~20-decisions/month canon intact but make roughly half of it spoken-for (admin overhead + priced doors/approvals/audits), so the reserve you hold back become
- `docs/balance/DIAL5_ATTENTION_SCARCITY_PROPOSALS.md:25` -- **Interactions.** Cleanest possible change (one constant). But it **collides with a ruled grain**: WORKSHOP_2_BACKLOG "L1 spec inputs" fixes the founder unit at *"decisions, ~20/month"*, and DESIGN_PH
- `docs/balance/DIAL5_ATTENTION_SCARCITY_PROPOSALS.md:60` -- **Cost of being wrong.** If the ramp is too steep, the endgame is unplayable regardless of office quality (founder drowns before delegation can catch up); too shallow and scarcity never arrives, leavi
- `docs/balance/L1_CALIBRATION_2026-07-14.md:136` -- - [ ]N `doom.momentum_enabled` -- **NEW -> 1.0** *(the ruled kill-switch: 0 = momentum contributes nothing)*
- `docs/calendar/COMMITMENTS.md:157` -- COMMITMENT: 2026-08-10 -- Book the half-day audit-mechanics workshop, target window opens -- owner: pip -- kind: task -- note: pdoom1#984, ruled 2026-07-27 18:11. Scheduled to precede the 2026-08-31 f
- `docs/calendar/github_snapshot.json:2237` -- "title": "Ladder eligibility must be visible BEFORE the run starts, not delivered at death (ruled by Pip 2026-08-07)",
- `docs/content/ROLE_CREATIVE_DIRECTOR.md:16` -- > pipeline pushes to, not the home of the process"*. Pip ruled **`pull`** on
- `docs/copy/MANIFUND_SUBMITTED_2026-07-29.md:181` -- Compatible with the ruled model (monthly Theme/Epoch, weekly Seed rotation
- `docs/copy/budget.json:134` -- "explanation": "RESOLVED. This entry previously read 'unknown and unasked' and warned that if a fee existed the rounding gap would be larger than $500. A fee exists. It is NOT absorbed into the gap: P
- `docs/decision-cards/2026-08-02_pdoom-data-contract.md:130` -- - The future draw-down is already ruled: ADR-0016 monthly world-update packs
- `docs/design/ASSET_PROVENANCE_SCOPE_2026-08-06.md:119` -- a very plausible guess. It is still a guess, and `coordination#32` already ruled
- `docs/design/PHASE_GUARD_AUDIT_2026-08-06.md:10` -- This is **not** about #1134. PR #1143 (retire the feature) is the ruled fix for the
- `docs/design/PHASE_GUARD_AUDIT_2026-08-06.md:109` -- All three are removed by **PR #1143**, which is the ruled fix. Nothing here duplicates that
- `docs/design/UPDATER_DESIGN.md:55` -- auto pck-swap patcher (unbuilt). Ruled 2026-07-23: hash-in-manifest over
- `docs/design/WORKSHOP_TRI_REPO_PREP_2026-08-06.md:552` -- | K8 | `coordination` | File **one issue per Block A item**, labelled `broadcast`, same day, per the agenda -- and note that A1 ruled without a transport (`pdoom1#1115`) is a specification, not a deli
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:106` -- 3. **League cadence RULED monthly (2026-07-21)** (backlog:405-408) -- recorded
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:110` -- model RULED** (backlog:171-177), **DQ-24 five demand categories RULED**
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:112` -- (backlog:723-730), **two-screen PLAN/WATCH model RULED** (backlog:686+),
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:113` -- **identity-decoupled-from-ability RULED** (backlog:789+) -- all live in
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:126` -- lower: three "open" DQs are ruled or resolved in backlog prose the generator
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:146` -- - DIAGNOSIS: ADR-0016 was ruled ~75% CANON ("otherwise I drift away from the
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:179` -- ### Tension 3 -- Board legitimacy: three half-closed holes on one ladder, plus a ruled-monthly league running weekly
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:18` -- > **Status: ANALYSIS ONLY.** Nothing here is ruled. Recommendations are marked
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:207` -- stays open. What is missing is one ruled POLICY ("who appears on a board,
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:222` -- sustained) is being spent at 4x the ruled cadence.
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:322` -- | DQ-16 (conference subgame) | Shape ruled (ADR-0014 amendment a), shell shipped (#979) | Mark SHELL-EXECUTED; the remaining "yields" half is not a design question -- it is Tension 2's build dependenc
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:341` -- midgame -- NOTE: the WS-3 endgame rulings already ruled its rung boundary
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:350` -- - **Re-scope:** DQ-10 (inward SA) -- the *mechanism* half is ruled and built
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:368` -- when a DQ gets ruled, write the keyword into the bold span (that IS the
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:464` -- - Whether #758 (portrait variant determinism, DQ-15 ext) was ever ruled.
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:74` -- | 0009 | Plan-months, two speeds, day tick | ACCEPTED | 07-12 | Plan-month layer live and compliant: `month_controller.gd:1-19` (day-tick playback, auto-pause-on-window, demand budget), no-banking res
- `docs/game-design/ADR_DQ_AUDIT_2026-08-03.md:83` -- | 0018 | Render-only office doctrine | **DRAFT** (formal confirm at R3a) | 07-27 | The confirm HAPPENED: R3a/R4 ruled it and #968 merged (`WS3A_DAYLOG_2026-07-27.md:404-412`, ballots 7-8); the a(3)-li
- `docs/game-design/BUILD_BRIEF_789_HIRING_STITCH.md:100` -- The stitch must not invent economy. It rides the ruled effort economy:
- `docs/game-design/BUILD_BRIEF_789_HIRING_STITCH.md:106` -- exactly the ruled model, not a new sink.
- `docs/game-design/BUILD_BRIEF_789_HIRING_STITCH.md:5` -- > decision points. Do not re-litigate ruled design -- cite it.
- `docs/game-design/BUILD_BRIEF_789_HIRING_STITCH.md:98` -- ## 2. Mapping onto ADR-0011's ruled substrate
- `docs/game-design/BUILD_BRIEF_HIRING_PIPELINE.md:5` -- > RULED (barrage)" + "DQ-24 taxonomy RULED" + "Character sprite system"; ADR-0011 (effort
- `docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md:6` -- - **Status:** DRAFT (for Pip review; recommend promoting to ADR-0018 once ruled)
- `docs/game-design/DESIGN_2026-08-15_backlog-as-teacher.md:131` -- The strongest existing support for this thesis is a rule that was ruled for
- `docs/game-design/DESIGN_2026-08-15_backlog-as-teacher.md:224` -- agrees with the ruled card-hand principle that the hand must show **more than
- `docs/game-design/DESIGN_2026-08-15_backlog-as-teacher.md:241` -- 5. **Items must be allowed to fall out of view.** Already ruled diegetic --
- `docs/game-design/DESIGN_2026-08-15_backlog-as-teacher.md:292` -- **Proposal (this seat, not ruled).** The cleanest way to hold all of this is a
- `docs/game-design/DESIGN_2026-08-15_backlog-as-teacher.md:3` -- > **Status: design thesis, captured. Not an ADR, nothing ruled.** Dictated by
- `docs/game-design/DESIGN_2026-08-15_causality-violation.md:395` -- with an icon. **His own earlier ruling says no.** On 2026-07-31 he ruled that
- `docs/game-design/DESIGN_2026-08-24_diegetic-opening.md:242` -- | How do interrupts trade against the committed queue? | **Still open.** Variants A/B/C written and never ruled. | `coordination/DESIGN_2026-08-12_interrupt-resolution-variants.md` |
- `docs/game-design/DESIGN_2026-08-24_diegetic-opening.md:3` -- > **Status: design document. Nothing ruled, nothing built, no code written.** Assembled
- `docs/game-design/DESIGN_2026-08-24_diegetic-opening.md:493` -- occupies. **Pip already ruled this** (`DESIGN_2026-08-10` s3), and #1202 item 4 names it as a
- `docs/game-design/DESIGN_2026-08-24_diegetic-opening.md:628` -- is ruled out today."* The doctrine has a **review clause dated 2027-07-27** and that review is
- `docs/game-design/DESIGN_2026-08-24_diegetic-opening.md:739` -- **Its two questions are still open and neither was ever ruled:** (1) A, B or C; (2) *"Does an
- `docs/game-design/DESIGN_2026-08-24_diegetic-opening.md:866` -- 9. **A variable attention grant.** Already ruled and already commented in
- `docs/game-design/DESIGN_2026-08-24_diegetic-opening.md:927` -- | 1 | **Lift `OfficeFloor` out of `WatchScreen`** into a region registered as neither plan-only nor watch-only | `main_ui.gd`, `watch_screen.gd`, `screen_mode.gd`, `main.tscn` | Already ruled by Pip (
- `docs/game-design/DESIGN_PHILOSOPHY.md:423` -- **The founder currency is named `Attention`** (ruled 2026-07-13): Pip's own canon
- `docs/game-design/DESIGN_PHILOSOPHY.md:56` -- race enters the seed timeline. The two collisions ruled: 2017 run-start holds (fixed
- `docs/game-design/DESPERATION_LEVER_PRICING.md:3` -- **Ruled by Pip, 2026-08-22:** *"we need to give the mechanical inertness a definite
- `docs/game-design/DQ-21-INTERMEDIARY-SEMANTICS-STRAWMAN.md:150` -- - **Enters doom via ([x] R2-Q2 ruled: gate-only, no stream of its own):** positive
- `docs/game-design/DQ-21-INTERMEDIARY-SEMANTICS-STRAWMAN.md:279` -- 3. **Trend-grade invariant ([x] R2-Q7 ruled, N=6):** doom rate MAY go negative on any turn;
- `docs/game-design/DQ-21-INTERMEDIARY-SEMANTICS-STRAWMAN.md:491` -- - [x] **Q-FN-3** Resolved via rounds 2+4: dampers can push the *rate* negative; sacred-object chains (?2b) are the discrete *level* reductions; the R2-Q7 trend-grade invariant (now ruled, N=6) polices
- `docs/game-design/ENDGAME_VIOLENCE_PROPOSAL.md:165` -- allocated by visibility/reputation/impact -- the same key as DQ-22's ruled
- `docs/game-design/ENDGAME_VIOLENCE_PROPOSAL.md:202` -- unignorable (already ruled: "some events legally unignorable" with default
- `docs/game-design/ENDGAME_VIOLENCE_PROPOSAL.md:252` -- mind-hacked, wireheaded -- **nobody grossly murdered on screen** (the ruled
- `docs/game-design/ENDGAME_VIOLENCE_PROPOSAL.md:254` -- (a)-(d) discipline is INFERRED operationalization of the ruled guardrail;
- `docs/game-design/ENDGAME_VIOLENCE_PROPOSAL.md:276` -- | 2 | midgame, DQ-22 aggro | adversarial | psyops, poach raids, leak-seeking (the ruled rival attack list) |
- `docs/game-design/LEAGUE_WEEK_PLAYBOOK.md:114` -- - No Jira this week (ruled 2026-07-28). The playbook and runsheet are the
- `docs/game-design/OFFICE_ECONOMY_PROPOSAL.md:92` -- already ruled ("as a CEO, I care about managing the first half dozen people or
- `docs/game-design/RESEARCH_IDEA_PAPER_PIPELINE_GAP.md:175` -- The gap coincides exactly with the ADR-0011 workstream substrate the team already ruled to
- `docs/game-design/RESEARCH_IDEA_PAPER_PIPELINE_GAP.md:190` -- ideas/lanes/workstreams are the ruled cure ("with ADR-0010, the constant policy is
- `docs/game-design/RESEARCH_IDEA_PAPER_PIPELINE_GAP.md:252` -- Build the ruled design. A `Workstream` object = { idea/topic, assigned researchers,
- `docs/game-design/RESEARCH_IDEA_PAPER_PIPELINE_GAP.md:287` -- re-litigate MODERATE -- it is already ruled (ADR-0011 ACCEPTED); it only needs scheduling.**
- `docs/game-design/RESEARCH_STREAMS_PROPOSAL.md:58` -- the workstream substrate is already ruled (ADR-0011); the influence stocks are
- `docs/game-design/RUNSHEET_2026-07-27_to_29.md:174` -- 4. **Early-game decisions scaffolding** -- data/action stubs for the ruled
- `docs/game-design/RUNSHEET_2026-07-27_to_29.md:177` -- 5. **Tile-grid addressing** -- implement the ruled addressing scheme in the
- `docs/game-design/RUNSHEET_2026-07-27_to_29.md:179` -- 6. **Office-view real-estate/camera** -- apply the ruled footprint/camera
- `docs/game-design/RUNSHEET_2026-07-27_to_29.md:74` -- | 8 | Tile-grid addressing | one addressing scheme ruled for the office view (Tuesday lanes build against it) |
- `docs/game-design/SEED_GOVERNANCE_BODIES_NAMES.md:4` -- > Nothing here is ruled. The structure half-page answers the "must boards be
- `docs/game-design/TENSION_AUDIT_2026-07-23.md:16` -- > **Status.** ANALYSIS ONLY. Nothing here is ruled. No GitHub labels were changed
- `docs/game-design/UPGRADES_ASSET_BRAINSTORM.md:4` -- > This is a BRAINSTORM, not ruled mechanics -- but it doubles as the art-generation target list.
- `docs/game-design/VISION_ACCUMULATION_AND_EVOLUTION.md:335` -- | Attribution | emergent-community structures (NOT pre-built -- ruled 2026-07-21, DQ-34) | capture the run DNA + strategy signature so first-discovery stays computable later (4.1, 4.3) |
- `docs/game-design/WORKSHOP_2_BACKLOG.md:219` -- *actions* -- separate currencies (ADR-0011 refined). Currency name RULED: **Attention**
- `docs/game-design/WORKSHOP_2_BACKLOG.md:405` -- - **League cadence RULED (Pip 2026-07-21):** leagues and content ops are **monthly**
- `docs/game-design/WORKSHOP_2_BACKLOG.md:449` -- rotation across keepers. Also RULED: board/council art must be menacing but VARIED
- `docs/game-design/WORKSHOP_2_BACKLOG.md:470` -- - **POSITIONING RULED (Pip 2026-07-22, via grant-framing review):** the player is NOT
- `docs/game-design/WORKSHOP_2_BACKLOG.md:484` -- - **Momentum:** dial-4 retune accepted as *interim*; momentum ruled a low-commitment
- `docs/game-design/WORKSHOP_2_BACKLOG.md:486` -- - **Reputation reminder (Pip's open-Q5):** direction already ruled -- reputation is
- `docs/game-design/WORKSHOP_2_BACKLOG.md:599` -- (dial-5 B + burnout ruling). Not new scope -- the concrete shape of what's already ruled.
- `docs/game-design/WORKSHOP_2_BACKLOG.md:682` -- - **Nomenclature ruled:** a "turn" = a planning phase (currently a month); see
- `docs/game-design/WORKSHOP_2_BUILD_LANES.md:178` -- inventing alternatives, and it gets ruled with real screens in hand.
- `docs/game-design/WORKSHOP_3_PREP.md:130` -- - **Re-designing anything already ruled.** The workstream substrate is RULED
- `docs/game-design/WORKSHOP_3_PREP.md:298` -- - Design already ruled directionally in that doc: advisor persona (Component 3)
- `docs/game-design/WORKSHOP_3_PREP.md:343` -- - **DQ-24** (attention-demand taxonomy) is already RULED (5 demand categories ->
- `docs/game-design/WORKSHOP_3_PREP.md:487` -- biggest design payoff but is already RULED (ADR-0011) -- it needs *scheduling
- `docs/game-design/WORKSHOP_3_PREP.md:491` -- - Theme C's MODERATE/AMBITIOUS workstream build (already ruled; schedule it,
- `docs/game-design/WORKSHOP_3_PREP.md:531` -- ADR-0011 already ruled it? Pip's call on whether MINIMAL-vs-MODERATE sequencing
- `docs/game-design/WORKSHOP_3_PREP.md:60` -- the DECISIONS, not the INTERFACE. For every mechanic ruled in, ask: does it add
- `docs/game-design/WORLD_AND_LORE.md:215` -- one frame. (Anonymity-preserving = inclusion; the silhouette does both jobs, as ruled.)
- `docs/game-design/WS3A_DAYLOG_2026-07-27.md:18` -- ## Pre-0900 breakfast art-review block (Pip ruled 0645: art review while
- `docs/game-design/WS3A_DAYLOG_2026-07-27.md:415` -- (Pip ruled 4-way ~1615, overriding the 2-way default, WITH a formal
- `docs/game-design/WS3_ENDGAME_RULINGS_2026-07-29.md:104` -- | 8 | Which epoch | See Section 4 -- options, not yet ruled. |
- `docs/game-design/WS3_ENDGAME_RULINGS_2026-07-29.md:303` -- - **Q8 epoch placement** -- options in the session response, not yet ruled.
- `docs/game-design/WS3_FINISH_OR_DROP.md:157` -- lane (still ruled, not v1); (c) name the AP->Attention migration endpoint --
- `docs/game-design/decisions/ADR-0011-effort-economy.md:110` -- **(c) FOUR-WAY founder hours ruled** (R4 ballot 4, ~1615), overriding the
- `docs/game-design/decisions/ADR-0014-conferences-presence-location.md:82` -- **(a) Rhythm-break placeholder shape RULED.** Pip's ruling on ADR-0014's
- `docs/game-design/decisions/ADR-0016-league-metabolism.md:81` -- - **Canon-ness ruled ~75%** -- bake deeply into config. Pip's reason: without the
- `docs/game-design/decisions/ADR-0018-render-only-office-doctrine.md:161` -- Camera2D enters consideration only when a ruled office tier exceeds one
- `docs/game-design/decisions/ADR-0019-pull-from-demand-asset-pipeline.md:193` -- magenta cat shipped deliberately, as policy. Auto-stripping is ruled OUT,
- `docs/game-design/decisions/ADR-0019-pull-from-demand-asset-pipeline.md:231` -- RULED by Pip, 2026-08-03, when this was raised as the one assumption the ADR
- `docs/playtest/PLAYTEST_EXTRACT_2026-07-31.md:6` -- - **Status:** EXTRACTED BY CLAUDE 2026-07-31, **not yet ruled on by Pip.** The
- `docs/qa/PLAYTEST_READINESS_2026-07-15.md:88` -- (button overlap, text clipping, theme glitches) are not ruled out by this check.
- `docs/release-body-v0.14.0-CORRECTED.md:35` -- and the ruled promotions applied (#1137), against Pip's rulings of 2026-08-04.
- `docs/release-body-v0.14.0-CORRECTED.md:4` -- was retimed to one-turn-one-month and the ruled promotions were applied (#1137),
- `docs/release-body-v0.14.0-CORRECTED.md:43` -- - **The last player-facing "AP" is gone**, and one number format is ruled across
- `docs/releases/RELEASE_LINKING_TO_0.20.md:111` -- Whichever is ruled, it should then be **mechanised**: derive the expected seed
- `docs/releases/RELEASE_LINKING_TO_0.20.md:175` -- Under the atomise protocol clause 3 (ruled 2026-08-24: *"do not build an atom
- `docs/rituals/records/GATE_RECORD_2026-08-24_v0.14.3.md:20` -- morning of 2026-08-24, during ISO week 35. Pip ruled that the seed names the ISO
- `docs/strategy/IP_AND_OPENNESS_PREMORTEM.md:443` -- except keeping the data backbone clean (already ruled).
- `docs/strategy/IP_AND_OPENNESS_PREMORTEM.md:87` -- community reads retraction as betrayal. Pip has already ruled against
- `godot/assets/images/events/README.md:26` -- **They are GRANDFATHERED. Pip ruled 2026-08-03 that already-packed assets stay
- `godot/autoload/game_config.gd:851` -- # ruled by Pip via PR #1096: "alpha-tools naming and wording settled") -----------------
- `godot/autoload/theme_manager.gd:161` -- # It is not restored here for a reason already ruled on: #1155 kept the
- `godot/data/asset_provenance.json:14` -- "_unknown_is_not_a_guess": "`unknown` means no record exists. It is never inferred from image dimensions. 1024x1024 and 1536x1024 are OpenAI output sizes, which makes 'these are gpt-image' a plausible
- `godot/data/asset_provenance.json:5132` -- "why": "Ruled by Pip 2026-08-15. A signed credential outranks every heuristic and is the only evidence that survives a file moving between repos. Applied narrowly because a full re-run would rewrite 2
- `godot/data/asset_provenance.json:5138` -- "why": "Ruled by Pip 2026-08-19 (D2). ADR-0019 has no provenance field and this manifest answered only WHAT made an asset, never WHO is owed credit for it. A human contributor is in prospect, which ma
- `godot/data/asset_provenance.json:5150` -- "why": "Ruled by Pip 2026-08-19 (D2). ADR-0019 has no provenance field and this manifest answered only WHAT made an asset, never WHO is owed credit for it. A human contributor is in prospect, which ma
- `godot/data/office/props_manifest.json:15` -- "style_tags": "office quality tiers this art serves, from the canonical ladder [\"scummy\", \"decent\", \"premium\"] (ruled 2026-07-26; see docs/game-design/SEED_ASSET_REGISTRY_AND_VERDICTS.md). Tag o
- `godot/data/patch_notes.json:143` -- "WHY THE BOARD FORKED: the historical event deck was retimed to one turn = one month, and the ruled event promotions were applied. Different events now fire on the same seed, so an L4 run is not compa
- `godot/scripts/core/build_info.gd:22` -- ## Alpha-tools era switch (#1079 fallout, ruled 2026-08-05). While this is true the ALPHA
- `godot/scripts/core/build_info.gd:94` -- ## doom"). That consequence was flagged when #1079 merged and never ruled on; this is the
- `godot/scripts/core/capacity.gd:5` -- ## Ruled 2026-08-12 (coordination/DESIGN_2026-08-12_interrupt-resolution-variants.md,
- `godot/scripts/core/game_state.gd:194` -- # ground-truth reported vs actual in a later lane (ruled 2026-07-27, review-by
- `godot/scripts/core/game_state.gd:38` -- ## COST ROUTING RULE -- ruled by Pip, 2026-07-27 (answers ADR-0010 R2 section 6
- `godot/scripts/core/month_plan.gd:11` -- ## nothing anywhere reads `action_points` (ADR-0011 amendment (a), ruled 2026-07-27 11:37).
- `godot/scripts/core/month_plan.gd:29` -- ## N2 used for typed reputation (ruled 2026-07-27). `attention_total`/`attention_spent`
- `godot/scripts/core/month_plan.gd:39` -- ## FOUNDER-HOUR KINDS (4-way, ADR-0011 point 2 / Ballot 4 ruled 2026-07-27, REVIEW-BY
- `godot/scripts/core/office.gd:58` -- ## menu size is: Pip ruled "3 offices to choose from", so the choice is fixed-width and
- `godot/scripts/core/prop_catalogue.gd:141` -- scummy/decent/premium (ruled 2026-07-26). Empty for unmanifested ids."""
- `godot/scripts/core/researcher.gd:150` -- # SEAM (ruled 2026-07-27, review-by 2026-08-31): AUDITS ground-truth reported vs actual.
- `godot/scripts/core/researcher.gd:190` -- # Ruled by Pip 2026-08-22 (#1247): "real STAFF, but they might not eg produce
- `godot/scripts/core/researcher.gd:61` -- # "Hiring pipeline RULED" (A1/A2/A3); appetites/quirks per ADR-0011 section 8; pay-to-see
- `godot/scripts/core/researcher.gd:69` -- # Hire lifecycle (WORKSHOP_2 "Hiring pipeline RULED"): pool -> offered -> employed ->
- `godot/scripts/core/turn_manager.gd:239` -- # #1247, ruled by Pip: real staff, but "they might not eg produce
- `godot/scripts/core/turn_manager.gd:313` -- SEAM (ruled 2026-07-27, review-by 2026-08-31): AUDITS ground-truth reported vs actual.
- `godot/scripts/debug/debug_overlay.gd:15` -- ## reproduced it repeatably in a release build and ruled the feature out rather than
- `godot/scripts/ui/cold_open_sequence.gd:43` -- # not copy: the strings are the ruled #801 copy, unchanged.
- `godot/scripts/ui/office_floor/office_floor.gd:493` -- ## (no tinting hacks -- ruled 2026-07-26). "" or "decent" = shipped default art.
- `godot/scripts/ui/office_floor/office_sandbox.gd:161` -- # (ruled 2026-07-26, see docs/game-design/SEED_ASSET_REGISTRY_AND_VERDICTS.md):
- `godot/scripts/ui/office_floor/office_sandbox.gd:175` -- # The tier whose art stands in when a tier-variant is missing (ruled 2026-07-26).
- `godot/tests/unit/simulation/test_events.gd:50` -- ## THE RATCHET WAS DELIBERATELY LOOSENED -- 2026-08-14, ruled by Pip, for content velocity.
- `godot/tests/unit/test_cold_open_intro.gd:46` -- # Pip approved this string personally (#801 ruled copy). If this fails, someone edited
- `godot/tests/unit/test_compute_engineers_are_staff.gd:12` -- ## Ruled by Pip 2026-08-22: "real STAFF, but they might not eg produce as much
- `godot/tests/unit/test_no_debug_event_injection.gd:9` -- ## the hard lock repeatably in a release build (2026-08-06) and ruled the feature out:
- `godot/tests/unit/test_number_format_policy.gd:2` -- ## Locks the number-format policy ruled in #1087 (docs/NUMBER_FORMATS.md).
- `godot/tests/unit/test_prop_manifest.gd:96` -- # style_tags restricted to the canonical quality-tier ladder (ruled 2026-07-26).
- `public/releases/releases.json:100` -- "tag_message": "P(Doom) v0.14.3 -- ladder epoch L6\n\nLadder L6. Featured seed weekly-2026-w35. Board key (weekly-2026-w35, L6).\n\nFORKING RELEASE, and the fork happened before this build. L6 was cut
- `public/releases/releases.json:209` -- "changelog": "Ladder epoch **L3 -> L4** -- this is a FORKING release. The historical event deck\nwas retimed to one-turn-one-month and the ruled promotions were applied (#1137),\nwhich changes which e
- `public/releases/v0.14.3.json:45` -- "tag_message": "P(Doom) v0.14.3 -- ladder epoch L6\n\nLadder L6. Featured seed weekly-2026-w35. Board key (weekly-2026-w35, L6).\n\nFORKING RELEASE, and the fork happened before this build. L6 was cut
- `scripts/generate_rulings.py:164` -- # CONSOLIDATION, ruled by Pip 2026-08-21.
- `scripts/generate_rulings.py:9` -- (`ruled by Pip`, `Pip ruled`, `ruled 2026-..`) scattered across .py docstrings,
- `tests/test_art_promotion_pipeline.py:480` -- """Pip ruled 2026-08-03: "Keep both, you pick naming variant."
- `tests/test_art_promotion_pipeline.py:74` -- second-pass fix routes where it was ruled to route."""
- `tools/art_review/CLEARANCE_SHEET_2026-08-15.md:273` -- | artq-017 | A | B T | "Avoid cockleg problems, this is very funny though" | **Already ruled by Pip.** The calibration for this sheet |
- `tools/art_review/CLEARANCE_SHEET_2026-08-15.md:325` -- Totals: **12 A** (including `artq-017`, already ruled, and `artq-014`, blocked
- `tools/art_review/ORPHANS_2026-08-15.md:65` -- **A4: RULED 2026-08-20 and DONE.** Canonicalise on the write path and collapse the
- `tools/art_review/apply_review.py:562` -- # its 07-21 reroll). Pip ruled both ship, so the older batch carries a
- `tools/art_review/apply_review.py:866` -- # Pip ruled 2026-08-03 that BOTH variants ship, so resolve collisions by
- `tools/art_review/build_cull_sheet.py:107` -- # A null clearance means "not yet ruled on", which is not consent.
- `tools/art_review/collapse_px_keys.py:4` -- ORPHANS A4. Ruled by Pip 2026-08-20: canonicalise on the write path AND collapse
- `tools/art_review/extract_pullquotes.py:227` -- # Per-platform clearance. null means "not yet ruled on"; a list
- `tools/art_review/extract_pullquotes.py:30` -- Verbatim is the default and the stored text is never edited. Pip ruled this
- `tools/art_review/qc_sprite_frames.py:4` -- Checks (per docs/art/PIXELLAB_OPERATIONS.md house rules, ruled 2026-07-26):
- `tools/art_review/serve_review.py:142` -- # estate has already ruled is just "abandoned" wearing a nicer word
- `tools/art_review/serve_review.py:181` -- "are different layers and must not be one letter apart. Ruled by Pip "
- `tools/art_review/serve_review.py:205` -- "to element: -- ruled by Pip 2026-08-15 because the sweeps are mostly "
- `tools/assets/backfill_provenance.py:147` -- `art_prompts/*.yaml` is the RULED source of truth per ART_MASTERS_POLICY:
- `tools/assets/backfill_provenance.py:38` -- ORIGIN VOCABULARY -- five values, ruled by Pip 2026-08-11
- `tools/assets/backfill_provenance.py:479` -- "Ruled by Pip 2026-08-15. A signed credential outranks every heuristic and "
- `tools/assets/backfill_provenance.py:558` -- # The five values ruled by Pip 2026-08-11, as a constant rather than a literal
- `tools/assets/backfill_provenance.py:673` -- "Ruled by Pip 2026-08-19 (D2). ADR-0019 has no provenance field and this "
- `tools/assets/backfill_provenance.py:851` -- "'these are gpt-image' a plausible guess; coordination#32 ruled that an "
- `tools/assets/check_credentials.py:30` -- permanently red over ~4,900 legacy files, and this estate has ruled on what
- `tools/assets/check_provenance.py:11` -- red, and this estate has already ruled on what that is worth:
- `tools/assets/check_provenance.py:4` -- Ruled by Pip 2026-08-11: the six unattributable assets are KEPT and recorded as
- `tools/assets/check_provenance.py:439` -- "_why": "Pinned unknown set. Ruled by Pip 2026-08-11: keep the "
- `tools/assets/check_provenance.py:60` -- this estate has already ruled carries no information.
- `tools/assets/manifests/new_subjects.json:115` -- "prompt_tail": "an almost perfectly flat-on frontal view of a wall of bureaucratic paperwork, shot square to the wall with minimal perspective so the picture plane and the wall plane are nearly parall
- `tools/assets/provenance_unknown_pin.json:2` -- "_why": "Pinned unknown set. Ruled by Pip 2026-08-11: keep the unattributable assets, record them honestly, and let a mechanism force the question later rather than a document.",
- `tools/check_chronic_red.py:250` -- Fossils count as failures as of 2026-08-30 (ruled by Pip; see
- `tools/check_chronic_red.py:484` -- # FOSSILS NOW FAIL (ruled by Pip 2026-08-30, docs/CI_FOSSILS_2026-08-30.md).
- `tools/check_chronic_red.py:579` -- print("  Ruled 2026-08-30: a fossil is REMOVED, never declared. A declaration for")
- `tools/check_guard_parity.py:6` -- WHY THIS EXISTS (issue #1265, ruled by Pip 2026-08-20)
- `tools/check_release_ledger.py:30` -- This is the ruled ``manufactured confidence`` shape (Pip, 2026-08-23 16:42):
- `tools/check_release_ledger.py:59` -- ``pdoom.releases/0.1``). Under the atomise protocol clause 3 (ruled by Pip,
- `tools/rule.py:153` -- description="Capture a ruling, after showing what was already ruled in its flavour."
- `tools/rule.py:159` -- ap.add_argument("--by", default="Pip", help="who ruled (default: Pip)")
- `tools/triage_undeclared_rulings.py:15` -- ruling, a doc explaining that something was ruled elsewhere, a tool's docstring
- `tools/triage_undeclared_rulings.py:21` -- ("ruled out", "ruled the day", "flagged, not ruled")
- `tools/triage_undeclared_rulings.py:52` -- (r"\bnot ruled\b|\bunruled\b|\bnothing ruled\b", "explicitly says it is NOT ruled"),
- `tools/triage_undeclared_rulings.py:58` -- (r"\bruled by \w+,?\s+\d{4}-\d{2}-\d{2}", "cites 'ruled by X, DATE'"),
- `tools/triage_undeclared_rulings.py:61` -- (r"\balready ruled\b|\bwas ruled\b|\bhas ruled\b|\bhe ruled\b|\bshe ruled\b", "past tense"),
- `user_privacy.json:2` -- "_comment": "Machine-readable privacy posture record. Canonical doc: docs/PRIVACY_POSTURE.md (two-tier model, ruled 2026-07-26). The Godot build persists LIVE player choices in user://config.cfg; this
