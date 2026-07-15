# Salvage Report — pre-workshop-1 / legacy documentation archival

**Date:** 2026-07-16
**Branch:** `docs/legacy-archival`
**Purpose (Pip's words):** *"(a) to not accidentally cross-pollinate through poor hygiene
and (b) if done systematically will give me the confidence we've squeezed all the good
juice out of the old lemon in terms of ideas preserved in old docs and notes."*

This report is the lemon-squeezing record: every legacy doc archived in this PR was read
and its ideas cross-checked against **current canon** —
`docs/game-design/DESIGN_PHILOSOPHY.md`, the ADR series
(`docs/game-design/decisions/ADR-0001..0016`), `docs/game-design/WORKSHOP_2_BACKLOG.md`
(the DQ register), `docs/game-design/WORLD_AND_LORE.md`, `docs/game-design/WORKSHOP_2_BUILD_LANES.md`,
and `docs/balance/*`. An idea already reflected there is safely preserved; an idea NOT
reflected there is flagged below so Pip can decide whether to keep it.

Nothing was deleted. Every file was `git mv`-moved (history preserved). No archived doc's
content was edited.

## Headline

- **117 legacy `.md` files archived** into `docs/archive/` (5 buckets — see section 2).
- **6 uncaptured / partially-captured ideas flagged** for Pip's judgment (section 1). None
  are blocking; a surfaced idea Pip drops is fine — the goal was to avoid *silently* burying
  a good one.
- **Left in place (not archived):** 2 confirmed-live docs, 3 infra docs for Pip to verify,
  and a conservatively-held "uncertain" set (sections 3-5) — per the rule *when you can't
  tell if something is legacy or live, do not move it.*
- **2 hygiene findings** where a **live** doc contradicts current canon (section 6) — Pip
  action, not touched by this PR.

---

## 1. Uncaptured / partially-captured ideas (THE JUICE)

These are the salvage finds — ideas in archived docs that are **not**, or only **partly**,
reflected in current canon. All come from the pre-workshop-1 `game-design/` docs; the
session-log / bug-investigation / infra buckets yielded nothing (section 7).

| # | Source doc (now archived) | Idea not fully in canon | Verdict | Proposed destination |
|---|---|---|---|---|
| 1 | `ECONOMIC_CYCLES_IMPLEMENTATION.md` | **Typed funding-source cycle-sensitivity**: five named macro phases (BOOM / STABLE / CORRECTION / RECESSION / RECOVERY) and, more usefully, funding sources reacting *differently* to the cycle — **government grants counter-cyclical**, seed/angel least cycle-sensitive, VC most sensitive, corporate moderate. | PARTIALLY-CAPTURED | `WORKSHOP_2_BACKLOG.md` already registers "Market conditions (bull/bear funding cycles) — ADR-0013 extension" (~line 219) but *without* the source-typed / counter-cyclical structure. Extend that DQ, or fold into ADR-0013 (cost-of-debt engine already types counterparties). |
| 2 | `PERSONNEL_BALANCING_NOTES.md` | **Granular researcher-trait effect catalog**: `leak_prone` (-> doom leak), `media_savvy` (-> reputation on publish), `prima_donna` (anti-synergy when peers present), `team_player` (stacking, **uncapped — flagged exploit risk**), `safety_conscious`, `workaholic`, `burnout_prone`, `fast_learner`, `pessimist`. Trait *names* appear live (README lists team_player/media_savvy/leak_prone) but this doc's effect-values are pygame-era. Also poaching-cadence note: 4%/turn ≈ 48%/yr vs Pip's stated "less than once per year" target. | PARTIALLY-CAPTURED | `DQ-15` (researcher archetype roster, ADR-0011). Reconcile the trait catalog against the three seeded archetypes; carry the **team_player uncapped-stacking** caution and the **poaching cadence** mismatch into balance. |
| 3 | `TECHNICAL_FAILURE_CASCADES.md` | **Transparency / Investigation / Cover-up response trichotomy** with **"cover-up debt"** (a hidden liability that accrues and can later be *exposed* for severe consequences) + **near-miss system** (monitoring investment converts would-be failures into cheap learning) + failure->failure cascade domino. Cover-up-debt is philosophically aligned with the Liability Ledger ("every mitigation is a loan") and the honesty line ("the sim never lies; characters do"), but the specific *event-response* framework isn't in ADR-0012's HANDLE/DEFER/IGNORE taxonomy. | PARTIALLY-CAPTURED | Extend `ADR-0012` (event response taxonomy), or a new DQ "cover-up-debt / failure-cascade event genre" — sibling to WORLD_AND_LORE's "blackmail -> one event genre". Near-miss-via-monitoring is a clean SA/instrumentation tie-in (ADR-0004). |
| 4 | `FEATURES_v0.4.1.md` | **Moore's-law compute-price decay**: "compute costs decrease 2% per week." A time-based decline in compute cost isn't obviously in current canon. | UNCAPTURED (minor) | Propose new **DQ-27 · Compute economy / price decay** (or fold into balance). Low priority; flag so it isn't lost. |
| 5 | `PROGRESSION_SYSTEM_DESIGN.md` | **Data-driven progression architecture**: a `ProgressionTree` / `ProgressionNode` / composable `UnlockCondition` (AND/OR) system unifying action-unlocks, upgrades, milestone events. | ENGINEERING-REFERENCE (not game-design) | Not a game-design salvage — keep as an *engineering* reference for structuring unlocks in the Godot rewrite. No canon home needed; noted so the pattern is findable. |
| 6 | `LANDING_EXPERIENCE_ENHANCEMENTS.md` | **Onboarding UX**: condense the 17-screen tutorial to 5-7 information-dense screens; progressive disclosure (black screen -> reveal elements as introduced); prominent skip. | UX-BACKLOG (not game-design) | No game-design-canon home. Candidate for a UX/onboarding backlog item if/when tutorial work is scheduled. |

---

## 2. Archived (117 files, 5 buckets)

All under `docs/archive/`. Buckets and their salvage verdict:

| Bucket | Count | What it is | Salvage verdict |
|---|---|---|---|
| `game-design-pre-workshop1/` | 12 | pygame-era design/tuning analysis + the two EXECUTED Fable workshop transcripts (#1, #2) + `GAME_DESIGN_CANON.md` | See section 1 (finds #1-#6) + notes below |
| `dev-sessions-pre-workshop1/` | 51 | session handoffs, completion reports, phase plans, project-management + PM planning, cleanup, summaries, old DOCUMENTATION_INDEX, test_failure_analysis | Salvage-none (historical narrative) |
| `issues-and-investigations-legacy/` | 32 | closed bug investigations + archived/completed issue write-ups + bug-sweep plans | Salvage-none (closed bugs) |
| `technical-pygame-era/` | 18 | technical docs describing `src/*.py` / `ui.py` / `main.py` systems that no longer exist post-migration | Salvage-none (engineering, superseded) |
| `architecture-pygame-era/` | 4 | pygame-era architecture/refactoring planning (CI/CD, input overhaul, refactor priorities, UI refactor targets) | Salvage-none (engineering, superseded) |

### Notable per-file verdicts in `game-design-pre-workshop1/`

| File | Verdict | Note |
|---|---|---|
| `GAME_DESIGN_CANON.md` | FULLY-CAPTURED — **highest-stakes move** | Dated 2026-06-30, self-titled "single source of truth", Godot-code-verified. **Superseded** by `DESIGN_PHILOSOPHY.md` + the ADRs that workshop #1 produced 4 days later. Its distinctive content is already elsewhere: win/lose spine -> **ADR-0002** (which even cites this doc as "Related §2"); MIT AI Risk Repository harm-taxonomy commitment -> **WORKSHOP_2_BACKLOG line 152 / DQ-21**. Archiving it is *also* the point of the hygiene pass — the filename actively misleads now that it is no longer canon. It is a `[PIP]`-placeholder skeleton draft, not a finished doc. **Easily reversible** (one `git mv`) if Pip disagrees. See section 6 for the stale ADR-0002 cross-reference this creates. |
| `FABLE_SESSION_KICKOFF.md` (#1) | FULLY-CAPTURED | Marked EXECUTED; its output *is* ADR-0002..0008 + DESIGN_PHILOSOPHY/WORLD_AND_LORE. Self-flagged stale ("games no longer target 7-8 turns"). |
| `FABLE_SESSION_2_KICKOFF.md` (#2) | FULLY-CAPTURED | Marked EXECUTED 2026-07-12; output is ADR-0009..0014 + build lanes. |
| `DOOM_MECHANICS_ANALYSIS.md`, `DOOM_TUNING_HOTFIX_v0.7.4.md` | FULLY-CAPTURED / obsolete | pygame doom numbers (doom_rise=5 etc.), superseded by ADR-0015 nine-stream doom + `balance/DOOM_STREAMS_v1.md`. Numbers are dead (reference `src/core/turn_manager.py`). |
| `TURN_SEQUENCING_FIX.md` | FULLY-CAPTURED | pygame bugfix; its *design* insight (events precede action-commitment) survives in ADR-0009's two-decision-speeds + "a turn is a plan you watch collide with reality". |
| `ECONOMIC_CYCLES_IMPLEMENTATION.md`, `PERSONNEL_BALANCING_NOTES.md`, `TECHNICAL_FAILURE_CASCADES.md`, `FEATURES_v0.4.1.md`, `PROGRESSION_SYSTEM_DESIGN.md`, `LANDING_EXPERIENCE_ENHANCEMENTS.md` | PARTIAL / see section 1 | The six salvage finds above come from these. |

---

## 3. Live-but-stale — needs refresh (LEFT IN PLACE)

| File | Status |
|---|---|
| `docs/technical/TURN_SEQUENCE_REFERENCE.md` | **Left in place — live, but describes the turn sequence and would benefit from a refresh pass** against the current ADR-0009/0012 turn model. Not archived: it still functions as the go-to turn-order reference. Flagged for a content refresh, not archival. |

---

## 4. Pip-to-verify — infra docs left in place

Three infrastructure docs in `docs/technical/` that could be live-operational or stale. Held
in place (conservative — *when you can't tell, don't move it*). Pip to confirm whether each
still describes a functioning system:

- `docs/technical/HEALTH_MONITORING_INFRASTRUCTURE.md`
- `docs/technical/PIPELINE_IMPLEMENTATION_GUIDE.md`
- `docs/technical/SETUP_CROSS_REPO_TOKEN.md`

---

## 5. Left in place — confirmed-live + uncertain

- **Confirmed live (do not archive):**
  - `docs/issues/leaderboard-backend-issues.md` — active issue tracker for the leaderboard backend.
  - `docs/technical/TURN_SEQUENCE_REFERENCE.md` — see section 3.
- **Uncertain, held for Pip (recent / resolved-but-detailed / mixed live+legacy):**
  - `docs/game-design/FABLE_SESSION_3_KICKOFF.md` — workshop #3 clearly ran (DESIGN_PHILOSOPHY has extensive 2026-07-13 workshop-#3 entries) but this kickoff has **no EXECUTED banner** (unlike #1/#2). Left in place pending Pip marking it executed; then it can join #1/#2 in the archive.
  - `docs/game-design/DQ-21-INTERMEDIARY-SEMANTICS-STRAWMAN.md` — RESOLVED into ADR-0015 but holds detail beyond the ADR and is recent (2026-07-13); may still be a live ruling-record reference.
  - `docs/guides/**`, `docs/shared/**`, `docs/assets/**`, `docs/ui_changes_20251117/**`, and the 2025-11-27 root-`docs/*.md` ops-doc batch (CONTROLS, MUSIC_SYSTEM, TESTING_*, VERIFICATION_*, PRIVACY, STEAM_*, LEADERBOARD_*, etc.) — a **mix** of live Godot-era ops/reference docs (e.g. `THEME_SYSTEM.md`, `UI_POLISH_GUIDE.md` reference current `godot/` `.gd` files) and a few clearly-stale one-off completion logs (e.g. `guides/ASSET_INTEGRATION_GUIDE.md` "Oct 31 2025", `guides/COPILOT_INSTRUCTIONS_UPDATE_ANALYSIS.md`, `guides/UPDATED_COPILOT_INSTRUCTIONS_v0.10.1.md`). **Held entirely in place** rather than risk archiving a live ops doc; recommend a follow-up targeted sweep with Pip if he wants these split.

---

## 6. Hygiene findings — live docs contradicting canon (Pip action)

Not touched by this PR (editing live README / canon is out of scope), but surfaced because
they are exactly the cross-pollination this exercise targets:

1. **`README.md:27` still states the superseded win-condition** — "Survive 100 turns with
   P(Doom) at 0%". Both `GAME_DESIGN_CANON.md` and **ADR-0002** explicitly call this "the
   wrong game" (the real spine is survival / how-long-how-low, no turn limit). The same
   stale phrasing appears in `docs/STEAM_INTEGRATION_ROADMAP.md` (ACHIEVEMENT_100_TURNS
   framing). Recommend correcting README to the ADR-0002 spine.
2. **`docs/adr/0002-win-condition-survival-spine.md:12`** has `Related: docs/GAME_DESIGN_CANON.md §2`.
   Archiving GAME_DESIGN_CANON moves it to `docs/archive/game-design-pre-workshop1/GAME_DESIGN_CANON.md`,
   so that cross-reference path is now stale. Minor; Pip may update the ADR pointer or leave
   it as a historical reference. (Not edited here — ADR content is canon and immutable-by-convention.)

---

## 7. Salvage-none (confirmed)

The following buckets were read/skimmed and contain **no** design/mechanic/balance idea
missing from current canon — they are historical narrative or superseded engineering:

- `dev-sessions-pre-workshop1/` (51) — session handoffs, completion reports, phase/strategic
  plans, project-management, cleanup, summaries.
- `issues-and-investigations-legacy/` (32) — closed bug investigations, archived/completed
  issue write-ups, bug-sweep plans.
- `technical-pygame-era/` (18) + `architecture-pygame-era/` (4) — pygame-era system/architecture
  docs superseded by the Godot code.
- Pre-existing `docs/archive/` subtrees (`monolith-refactoring-2025-09/`,
  `root-docs-cleanup-2025-09-15/`, `session-handoffs-2025-09/`, `ui-fixes-and-improvements/`)
  — from an earlier 2025-09 cleanup; left as-is, no salvage.
