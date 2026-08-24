# Dev tools index (GENERATED -- do not hand-edit)

> Derived from the tool files in `scripts/` and `tools/` by
> `scripts/generate_tools_index.py`. Regenerate with:
> `python scripts/generate_tools_index.py`. A pre-commit check fails
> commits that change the tooling without regenerating this file.
>
> Why generated: PR #1118 deleted three redundant GUT runners that had
> quietly carried the issue #640 silent-green bug for months -- invisible
> because nothing enumerated the tools. An index that is derived cannot
> rot the way the hand-kept `decisions/README.md` did.

The `Invoked by` column is DISCOVERED (by scanning `.pre-commit-config.yaml`,
`.github/workflows/*.yml`, `Makefile`, `tests/` and the other tools), never
copied from a tool's self-description. `tool:x.py` means another tool
references it; `test:x.py` means a Python test exercises it.

## Layers

Declared with a `Layer:` line in a tool's module docstring; `--` = undeclared.

- **GENERATE** -- derive an artifact from source; offer --check; gate in pre-commit
- **PROVE** -- assert a property and fail loudly
- **OBSERVE** -- report; never gate
- **SWEEP** -- find rot; never delete

## `scripts/`

| Tool | Layer | Purpose | Invoked by |
|---|---|---|---|
| ascii_compliance_fixer.py | -- | ASCII Compliance Fixer for P(Doom) Documentation | NONE FOUND |
| branch_manager.py | -- | Automated Branch Management System for P(Doom) | human (docstring usage) |
| build_all_platforms.py | -- | Build P(Doom) for all platforms (Windows, Linux, macOS). | ci:enhanced-release.yml; test:test_build_all_platforms.py; test:test_generate_release_metadata.py; tool:check_platform_builds.py; tool:generate_release_metadata.py |
| check_no_emoji.py | PROVE | Blocking no-emoji / ASCII enforcement for the Godot tree (issue #744). | pre-commit; ci:guards.yml |
| check_platform_builds.py | VERIFY (unrecognised) | Detect, per platform, whether a release's build artefacts actually EXIST. | ci:enhanced-release.yml; test:test_generate_release_metadata.py; test:test_platform_build_status.py; tool:generate_release_metadata.py |
| check_release_notes.py | -- | Guard against a release note that announces something we did not ship. | pre-commit; ci:enhanced-release.yml; ci:pre-release-checks.yml; test:test_release_notes_guard.py |
| check_site_release_freshness.py | -- | Is pdoom1.com advertising the release we actually published? | ci:live-site-release-freshness.yml |
| check_style_guide.py | -- | Style Guide Enforcement Check | pre-commit; tool:check_guard_parity.py |
| ci_health_integration.py | -- | CI/CD Health Integration - GitHub Actions Integration | ci:enhanced-cicd-pipeline.yml; ci:quality-checks.yml |
| cleanup_project.py | -- | Project Cleanup Automation Script | make |
| content_publisher.py | -- | P(Doom) Content Publisher - Multi-Platform Publishing System | human (docstring usage) |
| devblog_automation.py | -- | Dev Blog Automation System with Metadata | tool:content_publisher.py |
| enforce_standards.py | -- | P(Doom) Development Standards Enforcement Script | pre-commit; ci:enhanced-cicd-pipeline.yml; ci:quality-checks.yml; tool:generate_credits.py; tool:intelligent_ascii_converter.py; tool:pre_version_bump.py |
| find_duplicates.py | -- | Duplicate File Detector | human (docstring usage) |
| generate_action_taxonomy.py | GENERATE | Generate docs/ACTION_TAXONOMY.md and check the action taxonomy for rot. | pre-commit; ci:guards.yml; test:test_generate_action_taxonomy.py; tool:check_guard_parity.py |
| generate_adr_index.py | GENERATE | Generate docs/game-design/decisions/README.md from the ADR files themselves. | pre-commit; ci:guards.yml; tool:generate_action_taxonomy.py; tool:generate_tools_index.py |
| generate_commitment_calendar.py | GENERATE | Generate a subscribable .ics calendar + index from this repo's dated commitments. | pre-commit; ci:guards.yml; test:test_generate_commitment_calendar.py |
| generate_credits.py | GENERATE | Generate godot/data/credits.json from CREDITS.md. | pre-commit; ci:guards.yml; tool:backfill_provenance.py |
| generate_dq_index.py | GENERATE | Generate docs/game-design/DQ_INDEX.md from WORKSHOP_2_BACKLOG.md. | pre-commit; ci:guards.yml; tool:enforce_standards.py; tool:generate_credits.py; tool:generate_release_metadata.py; tool:intelligent_ascii_converter.py; tool:check_guard_parity.py |
| generate_mechanics_docs.py | GENERATE | Generate mechanics documentation from game code. | ci:docs-sync.yml |
| generate_release_manifest.py | GENERATE | Generate release_manifest.json -- the machine-readable release descriptor. | ci:enhanced-release.yml; test:test_generate_release_manifest.py; test:test_generate_release_metadata.py |
| generate_release_metadata.py | GENERATE | Generate release metadata for website integration. | pre-commit; ci:enhanced-release.yml; test:test_generate_release_manifest.py; test:test_generate_release_metadata.py; tool:generate_release_manifest.py |
| generate_rulings.py | GENERATE | Generate the rulings index + the cross-repo rulings.json from RULING: declarations. | pre-commit; ci:guards.yml; tool:generate_commitment_calendar.py; tool:check_credentials.py; tool:rule.py; tool:triage_undeclared_rulings.py |
| generate_tools_index.py | GENERATE | Generate docs/TOOLS.md -- the index of the dev tooling in scripts/ and tools/. | pre-commit; ci:guards.yml; test:test_generate_tools_index.py |
| health_automation.py | -- | Project Health Automation Suite - BLITZ MODE | human (docstring usage) |
| health_tracker.py | -- | Project Health History Tracker & Dev Blog Integration | ci:enhanced-cicd-pipeline.yml |
| intelligent_ascii_converter.py | -- | Intelligent ASCII Converter for P(Doom) Documentation | ci:enhanced-cicd-pipeline.yml; ci:quality-checks.yml; tool:enforce_standards.py; tool:pre_version_bump.py |
| issue_sync_bidirectional.py | -- | Bidirectional Issue Sync System for P(Doom) | human (docstring usage) |
| logging_system.py | -- | P(Doom) Centralized Logging System | NONE FOUND |
| monitor-sync.py | -- | Monitor the cross-repository documentation sync status | NONE FOUND |
| pre_build_validation.py | -- | Pre-Build Validation Script - Comprehensive Godot Project Testing | ci:enhanced-release.yml; tool:test_before_push.py |
| pre_version_bump.py | -- | Pre-Version Bump Quality Checks for P(Doom) | human (docstring usage) |
| project_health.py | -- | P(Doom) Project Health Dashboard - BLITZ MODE IMPLEMENTATION | make; ci:enhanced-cicd-pipeline.yml; ci:quality-checks.yml |
| repo-status.py | -- | P(Doom) Ecosystem Repository Status Dashboard | NONE FOUND |
| report_missing_build_issue.py | REPORT (unrecognised) | File / update ONE ROLLING tracking issue per platform whose build is missing. | ci:enhanced-release.yml; test:test_platform_build_status.py; tool:check_platform_builds.py |
| run_godot_tests.py | PROVE | Run Godot GUT (Godot Unit Test) tests from command line. | make; ci:godot-tests.yml; ci:guards.yml; test:test_find_dead_code.py; test:test_generate_tools_index.py; test:test_run_godot_tests_outcomes.py; tool:check_agent_env.py |
| setup-token.py | -- | GitHub Token Setup Helper for VS Code Users | NONE FOUND |
| sync_website_docs.py | -- | Sync documentation from pdoom1 repo to website export format. | ci:docs-sync.yml |
| test_before_push.py | -- | Test Before Push - Local Development Workflow | human (docstring usage) |
| todo_tracker.py | -- | TODO/FIXME/HACK Tracker | human (docstring usage) |
| token-setup-guide.py | -- | Quick GitHub Token Setup Guide for P(Doom) Cross-Repository Sync | NONE FOUND |
| validate_historical_data.py | -- | Historical Data Validation Script | make; ci:data-validation.yml; ci:enhanced-release.yml |
| verify_release_urls.py | -- | Verify release-feed download URLs actually resolve. | ci:enhanced-release.yml; test:test_generate_release_metadata.py; tool:generate_release_metadata.py |

## `tools/`

| Tool | Layer | Purpose | Invoked by |
|---|---|---|---|
| archive_masters.py | -- | Sync the local art-masters cache to off-site object storage (DreamObjects). | tool:slim_repo.py |
| build_release.py | PROVE | build_release.py -- export a P(Doom) build FROM A VERIFIED-CLEAN STATE. | ci:enhanced-release.yml; test:test_build_all_platforms.py; test:test_build_release_paths.py; tool:build_all_platforms.py; tool:check_agent_env.py; tool:find_dead_code.py |
| capture_cinematic.py | -- | Cinematic capture harness for P(Doom)1 -- deterministic scene footage -> mp4/gif. | test:test_find_dead_code.py; tool:find_dead_code.py |
| check_agent_env.py | PROVE | Guard: is CLAUDE.md still describing THIS machine? | make |
| check_balance_keys.py | PROVE | Census the Balance surface in BOTH directions, because nothing else does. | pre-commit; ci:guards.yml |
| check_class_cache.py | PROVE | check_class_cache.py -- catch a STALE global script class cache before it eats a playtest. | pre-commit; make; test:test_check_class_cache.py |
| check_environments.py | PROVE | Flag GitHub environments that no workflow references -- and say which are LIES. | ci:guards.yml |
| check_export_icons.py | -- | Every export preset's application/icon is a format that platform can decode. | pre-commit |
| check_font_sizes.py | PROVE | check_font_sizes.py -- count what the font-size SSOT still cannot reach. | pre-commit; ci:guards.yml |
| check_guard_parity.py | PROVE | Census every pre-commit hook against the workflows, and fail on a guard CI cannot see. | ci:guards.yml |
| check_ladder_bump.py | PROVE | Guard: did this diff need a ladder_version bump (or get one it did not need)? | ci:quality-checks.yml; test:test_check_ladder_bump.py; test:test_check_self_merge_eligibility.py; tool:sync_version.py |
| check_patch_notes.py | -- | check_patch_notes.py -- the shipped version must have patch notes to show. | pre-commit; test:test_check_patch_notes.py |
| check_refusal_classification.py | PROVE | check_refusal_classification.py -- every NEW player-facing refusal must say whether it | pre-commit; ci:quality-checks.yml |
| check_release_ledger.py | PROVE | Guard: has every version we bumped to actually been tagged and released? | ci:release-ledger.yml; tool:generate_commitment_calendar.py |
| check_review_js.py | -- | Syntax-check the JavaScript that serve_review.py serves to the browser. | pre-commit; ci:guards.yml |
| check_scene_nav.py | PROVE | check_scene_nav.py -- enforce the single-scene-navigation-chokepoint invariant. | pre-commit; ci:guards.yml; ci:quality-checks.yml; tool:enforce_standards.py; tool:check_guard_parity.py |
| check_self_merge_eligibility.py | PROVE | Guard: does this PR actually qualify for the self-merge class it claims? | ci:self-merge-eligibility.yml; test:test_check_self_merge_eligibility.py |
| cleanup-duplicate-issues.py | -- | Cleanup script for duplicate GitHub issues created by sync tool failure. | NONE FOUND |
| collect_ui_evolution.py | -- | UI evolution capture collector for P(Doom). | human (docstring usage) |
| commit.py | -- | Commit wrapper that absorbs the "hook reformatted a file then aborted" dance. | make; test:test_find_dead_code.py; tool:find_dead_code.py |
| find_dead_code.py | -- | find_dead_code.py -- report-only dead-path scanner for P(Doom)1. | test:test_find_dead_code.py; tool:generate_tools_index.py |
| generate_cat_placeholders.py | -- | Generate placeholder cat images for different doom levels. | tool:backfill_provenance.py |
| generate_release_horizon.py | -- | Generate the release horizon: which version ships when, on which seed, and | pre-commit; test:test_generate_release_horizon.py; tool:generate_commitment_calendar.py |
| generate_trust_declaration.py | -- | Generate docs/TRUST.md -- what the game reaches for, derived from the source. | pre-commit; ci:guards.yml |
| ingest_recordings.py | -- | Pull fresh OBS recordings into the repo's working area. | human (docstring usage) |
| phase2_setup.py | -- | Phase 2: Events System Setup | human (docstring usage) |
| phase3_setup.py | -- | Phase 3: Extract Features to Shared | human (docstring usage) |
| playtest_report.py | OBSERVE | Turn a recorded playtest into an evidenced bug list. | tool:ingest_recordings.py |
| print_doc.py | OBSERVE | Print a Markdown or HTML doc to paper with PREDICTABLE, LEGIBLE typography. | human (declared) |
| process_bug_reports.py | -- | Bug Report Processing Tool for P(Doom) | tool:collect_ui_evolution.py |
| release_timeline.py | -- | Mine GitHub timestamps for a release tag into a stage-gate timing table. | human (docstring usage) |
| render_budget.py | -- | Render the funding budget from data. Every published form, one source. | human (docstring usage) |
| reset_player_state.py | -- | Reset this machine's P(Doom) player state to a genuine first-launch experience. | test:test_reset_player_state_restore.py |
| rule.py | -- | Capture a ruling in one command, and show the precedent before you make it. | human (docstring usage) |
| scan_closed_issue_debt.py | PROVE | Find closed issues whose own acceptance criteria may never have been checked. | human (docstring usage) |
| sign_release.py | -- | Authenticode-sign a built Windows binary, or say clearly that it did not. | human (docstring usage) |
| slim_repo.py | -- | Reclaim git + .pck weight -- the slack mapped by the 2026-07-25 archival pass (#861). | human (docstring usage) |
| sync_version.py | PROVE | Stamp the canonical game version into every place that cannot self-read it. | pre-commit; ci:quality-checks.yml; tool:build_release.py; tool:check_ladder_bump.py |
| transcribe.py | OBSERVE | Transcribe a recording to timestamped text, offline, and optionally join it to the review log. | tool:serve_review.py |
| transcribe_recording.py | OBSERVE | Turn a recording into a transcript. | tool:playtest_report.py |
| triage_undeclared_rulings.py | OBSERVE | Sort the UNDECLARED prose-scan hits into real work, references, and noise. | human (docstring usage) |
| validate_assets.py | -- | validate_assets.py -- pre-release asset-import validation gate. | human (docstring usage) |
| velocity_report.py | OBSERVE | Reconstruct how much TIME a git history actually cost -- six ways, side by side. | human (declared) |
| write_build_stamp.py | -- | Write a build stamp that identifies exactly which commit a build came from. | tool:build_all_platforms.py; tool:build_release.py |

## `tools/art_review/`

| Tool | Layer | Purpose | Invoked by |
|---|---|---|---|
| analyze_verdicts.py | -- | Analyze art triage exports (verdict JSONs) for BOTH art libraries. | human (docstring usage) |
| apply_review.py | SWEEP | apply_review.py -- wire art-review verdicts into the P(Doom)1 asset pipeline. | test:test_art_promotion_pipeline.py; tool:build_full_gallery.py; tool:measure_taste.py; tool:serve_review.py; tool:slot_model.py |
| apply_slot_picks.py | -- | apply_slot_picks.py -- fold a slot_picker.html export into the TRACKED | test:test_slot_picker.py; tool:build_slot_picker.py |
| author_anchor_sockets.py | -- | Author godot/data/office/anchor_sockets.json -- Anchor Sockets V2 (#894 #900 #913). | tool:build_cat_sweep_sheet.py |
| build.py | -- | Build the P(Doom)1 style-review tool: a self-contained, single-file HTML page | test:test_find_dead_code.py; tool:select_assets.py |
| build_cat_angle_ab_sheet.py | -- | Build art_generated/cat_angle_ab.html -- the 2026-07-26 cat angle A/B sheet. | human (docstring usage) |
| build_cat_b2_sheet.py | -- | Build art_generated/cat_b2_sheet.html -- the 2026-07-26 cat experiment B sheet. | human (docstring usage) |
| build_cat_refinement_sheet.py | -- | Build art_generated/cat_refinement_sheet.html -- the cat refinement batch. | human (docstring usage) |
| build_cat_sweep_sheet.py | -- | Build art_generated/cat_sweep_sheet.html -- the full 8-direction cat sweep. | human (docstring usage) |
| build_cat_west_walk_picks.py | -- | build_cat_west_walk_picks -- 2026-07-27 cat_sweep_black_side_heft WEST walk pick sheet. | human (docstring usage) |
| build_cull_sheet.py | -- | Render a contact sheet of reviewed assets with their notes as captions. | human (docstring usage) |
| build_doom_strip_sheet.py | -- | Generate art_generated/doom_strip_sheet.html -- ADR-0015 doom-strip triage | human (docstring usage) |
| build_endgame_review.py | -- | Build a verdict-capturing review page for the endgame concept batch. | human (docstring usage) |
| build_full_gallery.py | OBSERVE | build_full_gallery.py -- ONE stateful gallery over ALL art on disk, in three | tool:apply_review.py; tool:run_art_night.py |
| build_generation_compare.py | -- | Side-by-side comparison of two generations of the same concept batch. | human (docstring usage) |
| build_morning_index.py | -- | One index page over every generated art batch on disk. | human (docstring usage) |
| build_prop_rebase_sheet.py | -- | build_prop_rebase_sheet -- prop re-base bulk batch + facing pilot (2026-07-27). | human (docstring usage) |
| build_slot_picker.py | -- | build_slot_picker.py -- the SLOT PICKER page. | tool:build_full_gallery.py |
| build_t6_diagonals_and_cats_sheet.py | -- | build_t6_diagonals_and_cats_sheet -- lane T6 review sheet, 2026-07-27. | human (docstring usage) |
| build_worker_rebase_sheet.py | -- | build_worker_rebase_sheet -- worker re-base at the 64px standard (2026-07-26). | human (docstring usage) |
| build_worker_round2_sheet.py | -- | build_worker_round2_sheet -- 2026-07-27 worker reroll + fresh worker (A+B). | human (docstring usage) |
| butt_dot_stamp.py | -- | Stamp the anatomical dot onto butt-flash frames (issue #913 follow-up). | tool:build_cat_refinement_sheet.py |
| collapse_px_keys.py | -- | One-shot: collapse the two `px:` key spellings onto one, per reviewer store. | human (docstring usage) |
| compare_reviewers.py | OBSERVE | Diff two reviewers' verdicts, honestly. | human (docstring usage) |
| export_picks.py | -- | export_picks.py -- turn the gallery review state into a picks file the | human (docstring usage) |
| extract_pullquotes.py | -- | Derive the pull-quote atoms from review_log.jsonl. | tool:build_cull_sheet.py |
| gen_contact_sheet.py | -- | Generate a self-contained pixellab contact-sheet / triage HTML. Local review tool. | tool:analyze_verdicts.py; tool:review_style.py |
| gen_generative_pass.py | -- | Generative (gpt-image) pass for the P(Doom)1 app-icon + settings-bg fast pass. | human (docstring usage) |
| gen_hero_gallery.py | -- | Generate art_generated/hero_gallery.html -- triage gallery for gpt-image-1 hero/banner/icon o... | tool:analyze_verdicts.py; tool:review_style.py |
| gen_icon_candidates.py | -- | Stopgap app-icon candidate generator for P(Doom)1 (no external API). | human (docstring usage) |
| gen_prop_grain_sheet.py | -- | gen_prop_grain_sheet -- prop NATIVE-GRAIN vanguard comparison sheet (issue #900/#925). | NONE FOUND |
| gen_quirk_icon_sheet.py | -- | Generate art_generated/quirk_icons_sheet.html -- quirk icon review sheet (issue #903). | human (docstring usage) |
| gen_settings_grounds.py | -- | Warm-register settings-screen background candidates for P(Doom)1 (no API). | human (docstring usage) |
| gen_size_probe_sheet.py | -- | gen_size_probe_sheet -- character size vanguard probe sheet (2026-07-26). | human (docstring usage) |
| measure_taste.py | -- | measure_taste.py -- what the slot picks say about taste, measured. | tool:shortlist_l3_heroes.py |
| merge_gallery_export.py | -- | merge_gallery_export.py -- fold a full_gallery.html export back into | tool:build_full_gallery.py; tool:notes_brief.py |
| notes_brief.py | -- | notes_brief.py -- turn the reviewer's notes into the brief for the next round. | tool:build_full_gallery.py |
| qc_sprite_frames.py | -- | qc_sprite_frames -- PIL QC gate for pixellab character batches. | tool:build_worker_rebase_sheet.py |
| rank_l3_picks.py | -- | rank_l3_picks.py -- choose which 'keep' verdicts get hero money. | NONE FOUND |
| revert_action.py | -- | Undo one batch action, restoring exactly what each asset was before it. | human (docstring usage) |
| review_style.py | -- | review_style -- ONE house style for all internal review/dev HTML tools. | tool:analyze_verdicts.py; tool:build_cat_angle_ab_sheet.py; tool:build_cat_refinement_sheet.py; tool:build_cat_sweep_sheet.py; tool:build_cat_west_walk_picks.py; tool:build_doom_strip_sheet.py; tool:build_prop_rebase_sheet.py; tool:build_slot_picker.py; tool:build_t6_diagonals_and_cats_sheet.py; tool:build_worker_rebase_sheet.py; tool:build_worker_round2_sheet.py; tool:gen_contact_sheet.py; tool:gen_hero_gallery.py; tool:gen_prop_grain_sheet.py; tool:gen_quirk_icon_sheet.py; tool:gen_size_probe_sheet.py |
| scan_text_leak.py | -- | Measure text leakage in a generated art batch, with OCR, and record the result. | tool:build_share_set.py |
| scan_white_flash.py | -- | Scan walk-clip frames for the "white flash under the cat" artifact. | tool:build_cat_refinement_sheet.py |
| serve_review.py | -- | Local art-review app for P(Doom)1 -- ONE place to review ALL the art. | test:test_harvest_pass.py; tool:build_full_gallery.py; tool:build_slot_picker.py; tool:revert_action.py; tool:scan_text_leak.py; tool:check_review_js.py |
| shortlist_l3_heroes.py | -- | shortlist_l3_heroes.py -- turn 140 flat hero candidates into an ordered shortlist. | human (docstring usage) |
| slot_model.py | -- | slot_model.py -- the ONE definition of "slot cluster" and "frame role". | test:test_slot_picker.py; tool:apply_slot_picks.py; tool:build_slot_picker.py; tool:measure_taste.py |
| text_leak_scan.py | -- | text_leak_scan.py -- measure how often generated art leaks legible text. | human (docstring usage) |

## `tools/assets/`

| Tool | Layer | Purpose | Invoked by |
|---|---|---|---|
| audit_icons.py | -- | Icon Asset Audit Tool | human (docstring usage) |
| backfill_provenance.py | -- | Backfill asset provenance for everything already packed into godot/assets/. | tool:check_provenance.py |
| build_review_gallery.py | -- | Rebuild tools/assets/review_generated.html from whatever PNGs are on disk under | human (docstring usage) |
| build_share_set.py | -- | Derive the ART SHARE SET from verdicts already applied -- no new review pass. | human (docstring usage) |
| check_credentials.py | PROVE | Guard: shipped images must not silently lose their C2PA content credential. | pre-commit; ci:guards.yml; test:test_check_credentials.py; tool:backfill_provenance.py; tool:check_guard_parity.py |
| check_provenance.py | -- | Guard: the provenance manifest and the pack must agree, and `unknown` must not grow. | pre-commit; ci:quality-checks.yml; tool:backfill_provenance.py |
| extract_palette.py | -- | Extract a brand palette from an image (default: the P(Doom)1 hero background). | human (docstring usage) |
| generate_images.py | -- | Generalized batch image generator for pdoom1 art assets. | test:test_check_credentials.py; tool:promote_assets.py |
| promote_assets.py | -- | Asset promotion tool for pdoom1. | NONE FOUND |
| render_latex_pdoom.py | -- | Local LaTeX-style typeset renders of the P(doom) logo studies. | NONE FOUND |
| run_art_night.py | GENERATE | run_art_night.py -- level-structured, budget-capped, resumable art run. | test:test_check_credentials.py |
| select_assets.py | -- | Interactive asset selection tool for pdoom1. | tool:promote_assets.py |

## `tools/music/`

| Tool | Layer | Purpose | Invoked by |
|---|---|---|---|
| analyze_refs.py | -- | Reference-track analyzer for P(Doom)1 adaptive-music composition. | human (docstring usage) |
| analyze_refs_meter.py | -- | Profile reference tracks into compositional seeds. | tool:explore_track.py |
| capture_takes.py | -- | Programmatic Strudel capture -- no OBS, no system audio. | human (docstring usage) |
| explore_track.py | -- | One-command track exploration: drop in any song, get a full analysis report. | human (docstring usage) |
| process_captures.py | -- | Turn raw strudel captures into game-ready looping ogg stems. | human (docstring usage) |
| zoom_rhythm.py | -- | Zoom into a time window of a track and extract its rhythm as notation. | human (docstring usage) |

## UNKNOWN -- no declaration, no usage hint, no discoverable caller

11 tool(s) that nothing declares, documents, or calls. Each one is either
a rot candidate or an undocumented dependency -- find out which (`tools/find_dead_code.py` lane).

- `scripts/ascii_compliance_fixer.py`
- `scripts/logging_system.py`
- `scripts/monitor-sync.py`
- `scripts/repo-status.py`
- `scripts/setup-token.py`
- `scripts/token-setup-guide.py`
- `tools/art_review/gen_prop_grain_sheet.py`
- `tools/art_review/rank_l3_picks.py`
- `tools/assets/promote_assets.py`
- `tools/assets/render_latex_pdoom.py`
- `tools/cleanup-duplicate-issues.py`

## Claim-vs-reality gaps

The tool's own docstring names an automated caller category that the scan
could not corroborate. Some are prose false-positives (a docstring merely
DISCUSSING CI); the rest are the hollow-runner shape -- read them.

- `scripts/health_automation.py` -- docstring mentions CI; no workflow calls it
- `scripts/logging_system.py` -- docstring mentions CI; no workflow calls it
- `tools/art_review/apply_review.py` -- docstring mentions pre-commit; no pre-commit hook calls it
- `tools/art_review/notes_brief.py` -- docstring mentions pre-commit; no pre-commit hook calls it
- `tools/art_review/scan_text_leak.py` -- docstring mentions CI; no workflow calls it
- `tools/assets/build_share_set.py` -- docstring mentions CI; no workflow calls it
- `tools/capture_cinematic.py` -- docstring mentions CI; no workflow calls it
- `tools/check_class_cache.py` -- docstring mentions CI; no workflow calls it
- `tools/check_export_icons.py` -- docstring mentions CI; no workflow calls it
- `tools/check_guard_parity.py` -- docstring mentions pre-commit; no pre-commit hook calls it
- `tools/check_release_ledger.py` -- docstring mentions pre-commit; no pre-commit hook calls it
- `tools/commit.py` -- docstring mentions pre-commit; no pre-commit hook calls it
- `tools/find_dead_code.py` -- docstring mentions pre-commit; no pre-commit hook calls it
- `tools/find_dead_code.py` -- docstring mentions CI; no workflow calls it
- `tools/music/analyze_refs.py` -- docstring mentions CI; no workflow calls it
- `tools/reset_player_state.py` -- docstring mentions CI; no workflow calls it
- `tools/write_build_stamp.py` -- docstring mentions CI; no workflow calls it

## Archived (`scripts/archive/` -- indexed by name only, excluded from caller scan)

- `scripts/archive/archive_completed_issues.py`
- `scripts/archive/ascii_cleanup_remnants.py`
- `scripts/archive/close_ui_issues.py`
- `scripts/archive/fix_deterministic_rng.py`
- `scripts/archive/fix_unicode_damage.py`
- `scripts/archive/nuclear_unicode_killer.py`

## Not indexed: HTML tools

27 `.html` tool(s) under `tools/` (browser-opened, no docstring to parse): `tools/art_review/doom_overlay_preview.html`, `tools/art_review/hero_gallery_template.html`, `tools/art_review/icon_pass_2026-07-21.html`, `tools/art_review/icon_pass_verdicts_2026-07-21.html`, `tools/art_review/palette.html`, `tools/art_review/palette_swatches.html`, `tools/art_review/scene_wave2_2026-07-21.html`, `tools/art_review/style_review.html`, `tools/assets/review_generated.html`, `tools/music/commission_sheets.html`, `tools/music/jukebox.html`, `tools/music/listening_room.html`, `tools/music/stem_board.html`, `tools/runsheet/CEREMONY-ALL-GATES-2026-07-31.html`, `tools/runsheet/SUNDAY-postmortem-2026-08-07.html`, `tools/runsheet/chronicle-2026-08-06_07.html`, `tools/runsheet/commitments-2026-08.html`, `tools/runsheet/copy-review-2026-08-09.html`, `tools/runsheet/fri-2026-07-31-EVENING-1620.html`, `tools/runsheet/fri-2026-07-31-GATES-1700.html`, `tools/runsheet/fri-2026-07-31-TO-MIDNIGHT-1733.html`, `tools/runsheet/fri-2026-07-31-league-day.html`, `tools/runsheet/playtest_card.html`, `tools/runsheet/wed-thu-2026-07-29.html`, `tools/social_composer.html`, `tools/ui_comparison.html`, `tools/ui_mockup/wireframe.html`.

Total: 152 active tools (11 GENERATE, 8 OBSERVE, 17 PROVE, 1 SWEEP, 115 undeclared); 11 in UNKNOWN; 6 archived.
