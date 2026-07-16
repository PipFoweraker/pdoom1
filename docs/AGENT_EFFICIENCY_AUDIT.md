# Agent-Efficiency Audit & Roadmap

**Purpose:** make the repo cheaper and smoother for future Claude/LLM agents to
load, navigate, and work in — fewer wasted tokens, fewer repeated mistakes.

**Philosophy: SLOW, ITERATIVE, LOW-RISK.** This is not a big-bang refactor plan.
Each item is scoped to be landed on its own, in its own PR, when convenient. Items
are ranked by **leverage-per-risk**. Each is tagged **[SAFE QUICK WIN]** (an agent
can just do it) or **[NEEDS PIP'S CALL]** (a judgement/architecture decision).

The two highest-value fixes (root `CLAUDE.md`, and the `.gitattributes` +
line-ending fix) are **already done** in the PR that introduced this file.

---

## Top findings, ranked by leverage-per-risk

### 1. No root `CLAUDE.md` — every agent re-derived conventions [DONE]
**Cost:** every fresh session re-discovered the import pass, the test tiers, the
`.import`/`.uid` staging trap, ASCII-only, branch-from-origin — hundreds of wasted
tokens and repeated mistakes per session. **Fix:** added root `CLAUDE.md` (a
scannable cheat-sheet). **Risk:** none. **Maintenance:** update in place when a
convention changes; keep it short (if it grows past ~2 screens it stops being read).

### 2. CRLF↔LF commit-hook fight [DONE]
**Root cause:** `core.autocrlf=true` (local + global) with **no `.gitattributes`**.
Git wrote CRLF into the working tree on checkout; Godot and the pre-commit
`mixed-line-ending --fix=lf` hook both want LF — so every doc commit tripped the
hook once (CRLF→LF rewrite + abort + re-add). **Fix:** added `.gitattributes` with
`* text=auto eol=lf` (+ explicit `binary` for assets). The index was already LF, so
this produced **zero mass-renormalization diff** (verified: `git status` stays
clean after adding it). **Risk:** minimal. **Not done (proposed for Pip):** a
deliberate one-shot `git add --renormalize .` to flush the mixed CRLF/LF working
trees across all worktrees — a large one-time diff. Only worth it if the churn
keeps recurring; the `.gitattributes` fix should prevent recurrence on its own, so
this is optional.

### 3. `.import` / `.uid` churn after every import pass [DOCUMENTED — no code change needed]
**Finding:** tracking is **correct** per Godot 4 convention — 1213 `.import` + 218
`.uid` files tracked; `godot/.godot/` and `godot/.import/` correctly ignored. The
churn (~1200 modified `.import`, stray `.uid`) is Godot **rewriting them during the
required `--import` pass**, not a gitignore bug. **Fix:** the staging rule is now in
`CLAUDE.md` — stage only changed files, never `git add -A`, discard churn with
`git checkout -- godot/`. **Risk:** none. **[NEEDS PIP'S CALL]** if the rewrite is
deterministic noise (same bytes re-touched), a local `git config` or a tiny
pre-commit guard could auto-drop unstaged `.import` churn — but that risks hiding
real import changes, so left as a documented discipline, not automation.

### 4. Whole-tree ASCII rescan on every commit [SAFE QUICK WIN — small]
**Cost:** `enforce-standards` runs with `pass_filenames: false` and `rglob`s the
entire tree (`*.py *.md *.txt *.json *.yaml *.yml *.toml *.cfg *.sh`) on **every
commit**, re-reading thousands of files even for a one-file doc change. Slow, and
it's the second half of the "every commit is slow" complaint. **Fix options (low
risk):** (a) let pre-commit pass the staged filenames (`pass_filenames: true`) and
have `enforce_standards.py --pre-commit` check only those; (b) add `godot/`,
`docs/archive/`, `web_export/`, `_website_export/` to its `exclude_dirs`. **Risk:**
low — but changes commit-gate semantics, so verify the ASCII gate still catches a
planted non-ASCII char before landing. **[NEEDS PIP'S CALL]** on whether the
per-commit scan should stay whole-tree (belt-and-suspenders) vs staged-only (fast).

### 5. `main_ui.gd` is a 3188-line monolith [NEEDS PIP'S CALL — already in flight]
**Cost:** the single biggest read-cost hotspot; any UI task loads 3k lines. **Note:**
a UI build lane (`feat/plan-watch-scaffold` / `feat/office-floor-sprites`) is
actively working this file — **do not touch it from an efficiency PR** (merge
conflict risk). **Recommendation:** once those lanes land, decompose by screen/panel
into `godot/scripts/ui/panels/` (it already imports many panel scripts). Slow,
deliberate, one panel at a time. Left entirely to Pip/UI-lane.

---

## Large-file inventory (read-cost hotspots)

Biggest GDScript files (excluding `addons/`), by line count. Files >~600 lines are
decomposition *candidates* — not mandates. Core-logic files are testable and mostly
cohesive; UI files are the better split targets.

| Lines | File | Note |
|------:|------|------|
| 3188 | `godot/scripts/ui/main_ui.gd` | monolith — **in flight, do not touch** |
| 1134 | `godot/scripts/core/game_state.gd` | central state; cohesive, high-traffic |
| 1024 | `godot/autoload/event_service.gd` | event dispatch singleton |
|  892 | `godot/scripts/game_manager.gd` | top-level orchestrator |
|  865 | `godot/scripts/core/actions.gd` | action catalog — data-extract candidate |
|  822 | `godot/scripts/core/turn_manager.gd` | turn sequencing |
|  698 | `godot/tests/unit/test_risk_system.gd` | large test file (fine) |
|  533 | `godot/scripts/core/doom_system.gd` | |
|  525 | `godot/scripts/core/events.gd` | |
|  521 | `godot/scripts/core/risk_pool.gd` | |
|  480 | `godot/scripts/ui/staff_perks_panel.gd` | UI split candidate |

**Recommendation:** treat only `main_ui.gd` (post-lane) and possibly `actions.gd`
(extract the action table into `godot/data/actions/`) as active candidates. The
core files at 800–1100 lines are coherent single-responsibility units — splitting
them would add cross-file navigation cost without clear benefit. **[NEEDS PIP'S CALL]**

---

## Module boundaries & navigability

- **Good:** `core/` (logic) vs `ui/` (presentation) vs `autoload/` (singletons) vs
  `data/` (JSON) is a clean, discoverable split. `data/`-driven balance/events means
  agents edit JSON, not code — keep leaning into this.
- **Minor friction:** two files live at `godot/scripts/` root (`game_manager.gd`,
  `leaderboard.gd`) outside the `core/ui/` split. **[SAFE QUICK WIN]** low value —
  could move under `core/`, but they're easy to find; skip unless touching them.
- **Naming:** mostly consistent `snake_case.gd`. No systemic rename needed.

## Class-cache SCRIPT-ERROR flood (#629 follow-on)

**Finding:** the first headless Godot invocation on a cold cache prints a wall of
`SCRIPT ERROR` / class-cache lines before the import completes — pure noise that
looks like failure and costs agent tokens/attention. `run_godot_tests.py` already
does the import pass first, so the fast gate is clean. **Recommendation [SAFE QUICK
WIN, small]:** document the noise (done — in `CLAUDE.md`), and optionally have the
runner suppress/summarize the first-pass stderr so logs an agent reads are shorter.
Do NOT suppress in CI (you'd hide real parse errors). Low priority.

## Test-tier clarity

**Finding:** the fast vs slow split is real and well-built (`run_godot_tests.py`
docstring + `godot-tests.yml` explain it), but a fresh agent doesn't read those
first. **Fix:** `CLAUDE.md` now states the fast-gate command and "don't wait on
`--simulation` for scoped changes." **Risk:** none. No further action needed.

## Doc sprawl [NEEDS PIP'S CALL — the biggest slow-burn opportunity]

**Cost:** **624 tracked `.md` files.** 57 loose `.md` at `docs/` root, 21 loose
`.md` at `godot/` root (e.g. `CAT_EVENT_COMPLETE.md`, `OPTION_A_..._COMPLETE.md`,
`PHASE_5_QUICK_REFERENCE.md` — status/handover notes that read like scratch).
`WORKSHOP_2_BACKLOG.md` alone is 708 lines. An agent searching docs pays a big
grep/scan tax and often hits stale or superseded files. **Recommendations (slow,
iterative):**
1. **[SAFE QUICK WIN]** move the 21 loose `godot/*.md` completion/handover notes
   into `godot/docs/` or `docs/archive/` — they clutter the code root an agent lists
   first. Verify nothing links them before moving.
2. **[NEEDS PIP'S CALL]** add a `docs/README.md` index (one line per live doc,
   grouped) so agents navigate by index instead of `ls`-ing 57 files. `ARCHITECTURE.md`
   already flags that some indexes (e.g. `decisions/README.md`) are stale — an index
   only helps if it's maintained.
3. **[NEEDS PIP'S CALL]** split/retire: several `*_COMPLETE.md`, `ISSUE_###_FIX_*.md`
   and duplicate ARCHITECTURE variants look like finished-work records — candidates
   for `docs/archive/` (already excluded from the ASCII hook).

## Dead / duplicate code spotted (read-only pass — verify before acting)

- **Two `ARCHITECTURE.md` variants** (`docs/ARCHITECTURE.md` dev map vs
  `docs/ARCHITECTURE_FUNDERS.md`) — intentional and cross-linked; not dead, but the
  funders one is noted as pre-L1/stale. Leave; maybe add a stale banner.
- **Two `TESTING_GUIDE.md`** (`docs/TESTING_GUIDE.md` and `godot/TESTING_GUIDE.md`) —
  likely overlapping/divergent. **[SAFE QUICK WIN]** consolidate to one canonical,
  link the other. Verify contents differ first.
- **Root-level shell/py one-offs** (`generate_batch_option_c.sh`,
  `test_output.png`/`test_openai_api.py`/`generate_icons.py` — the last three are
  already gitignored) — candidates to move under `tools/`. **[NEEDS PIP'S CALL]**
- No dead GDScript identified in this read-only pass; a proper unused-symbol sweep
  needs Godot tooling and is out of scope for a low-risk audit.

---

## Suggested order of attack (all optional, all independent)

1. Land this PR (CLAUDE.md + `.gitattributes` + this doc). **[DONE here]**
2. Scope `enforce-standards` to staged files or exclude `godot/`/exports (#4).
3. Move loose `godot/*.md` handover notes out of the code root (doc-sprawl #1).
4. Add a maintained `docs/README.md` index (doc-sprawl #2).
5. Consolidate the duplicate `TESTING_GUIDE.md`s.
6. (After UI lanes land) decompose `main_ui.gd` panel-by-panel.

Nothing here blocks anything else. Do them one at a time, verify the fast gate
after each, and keep blast radius small.
