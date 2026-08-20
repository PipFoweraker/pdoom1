# Guard audit, 2026-08-19: which gates actually run, and where

**Seat `pdoom1` on New-Bort. First run at `dbd568dc`; re-run and confirmed unchanged at `4bc6ec27`, after `e01a9a0f` added the second-reviewer tooling.** Read-only diagnosis. Nothing was
rewired; every remedy below is a proposal for Pip to rule on.

Prompted by a specific failure: `tools/assets/check_provenance.py` shipped
2026-08-11 as *"a mechanism, not a document"*, appeared in **no** pre-commit hook,
**no** workflow and **no** Makefile target, and one day later `ab85ed0b` (#1196)
landed a packed asset with no provenance entry -- the exact condition it was built
to catch. Nobody saw it for a week. `docs/TOOLS.md` already publishes a
"docstring mentions CI; no workflow calls it" list, which is how the class was
noticed. This audit widens that from docstring-claims to every guard.

**34 guard-shaped tools examined.** Reproduce with the script in the session
scratchpad, or by hand: for each tool, grep `.pre-commit-config.yaml`,
`.github/workflows/*.yml` and `Makefile` for its stem.

---

## The headline is not a list of unwired tools. It is a tier.

**15 guards run in pre-commit and nowhere else.** No workflow runs any of them,
and **no workflow invokes `make`**, so there is no indirect path either (verified:
the only `make` matches in `.github/workflows/` are the word "make" in prose).

That means the entire tier is inert on any machine where `pre-commit install` has
not been run -- and nothing anywhere verifies that it has been.

**This is not hypothetical. It was New-Bort until 2026-08-19.** `pre-commit` was
not installed at all; five commits went in through that hole today, and two of
them left generated indexes stale. Installing it and running one hook surfaced
both within a minute.

| pre-commit-only guard | what it protects | why the gap bites |
|---|---|---|
| `scripts/check_no_emoji.py` | ASCII-only rule, issue #744 | **CLAUDE.md calls this the "Blocking no-emoji gate"**, created *because* the older non-blocking Unicode check let a coffee emoji ship. The replacement for a non-blocking gate is itself absent from CI. |
| `tools/check_font_sizes.py` | the font-size SSOT **ratchet** (#1224) | Landed today. A ratchet's whole contract is "the count may fall, never rise" -- across contributors, which is precisely what a per-machine hook cannot enforce. |
| `tools/assets/check_credentials.py` | signed C2PA credentials on shipped images | Guards a loss its own docstring calls "invisible and irreversible"; ~1,600 masters were already destroyed this way before 2026-08-15. |
| `tools/assets/check_provenance.py` | the provenance manifest vs the pack | The tool that prompted this audit. PR #1239 puts it in CI, making it the only one of these four enforced in both places. |
| `scripts/generate_*.py` x9 (`rulings`, `commitment_calendar`, `tools_index`, `dq_index`, `adr_index`, `action_taxonomy`, `credits`) | generated-index staleness | Staleness is exactly what shipped twice today while the hook was absent. These are the anti-rot pattern; they rot silently without a runner. |
| `tools/check_review_js.py`, `tools/art_review/serve_review.py` | the embedded review JS parses | |
| `scripts/check_style_guide.py`, `tools/assets/build_share_set.py` | | |

## What CI does run

13 tools, of which **4 carry a `--self-test`** that proves the gate can still
fail: `check_ladder_bump`, `check_refusal_classification`,
`check_self_merge_eligibility`, and (via #1239) `check_provenance`.

## Second finding: 21 wired gates cannot prove they can fail

Per issue #640, this repo's own doctrine is that a green gate means something only
if it has been shown capable of returning the other answer. Most cannot:

`check_no_emoji`, `check_release_notes`, `check_site_release_freshness`,
`check_style_guide`, `check_class_cache`(\*), `check_font_sizes`,
`check_review_js`, `check_scene_nav`, `sync_version`, `build_release`,
`run_godot_tests`, `build_share_set`, and the nine `generate_*` index checks.

(\*) `check_class_cache` is the exception that proves the rule: CI cannot
reproduce a stale cache, so it runs `tests/test_check_class_cache.py` instead,
which asserts **both** answers against a synthetic tree. That is the pattern the
others lack, and it already exists in-tree as a worked example.

## Dismissed, having checked

- **The CRLF cry-wolf class does not extend beyond `check_provenance.py`.** The
  only other candidate that hashes filesystem bytes is `check_credentials.py`, and
  it is not exposed: `.png` resolves to `text: unset` in `.gitattributes`, so
  worktree equals blob for all four pinned files. Its pin also hashes the **C2PA
  box**, not the file (`51257B` is the box, not `office_scene.png`), and it has its
  own self-test. Guard exits 0. No action.
- **`tools/render_budget.py`** is the only fully inert tool, and it is a renderer,
  not a guard. Not a finding.

## Remedies -- for Pip, not adopted

**R1. Add the four substantive pre-commit-only guards to `quality-checks.yml`.**
Cheap and targeted: `check_no_emoji`, `check_font_sizes`, `check_credentials`,
plus the nine `generate_* --check` invocations, which cost seconds each.

**R2. One CI step running `pre-commit run --all-files`.** Structurally the better
answer -- it makes the two tiers the same tier by construction and can never drift
again. **Measured tonight, and it is NOT viable as-is: 231 seconds, exit 1, 154
failures**, almost all pre-existing whole-tree conditions (trailing whitespace,
missing final newlines, and 100+ `leaderboards/*.json` files that are not valid
JSON). A gate that is red on arrival carries no information, by this estate's own
rule. R2 only becomes available after a tree-wide cleanup that is its own decision.

**A warning attached to R2, learned the hard way tonight:** `pre-commit run
--all-files` includes the *auto-fixers*, and running it modified **1,046 files** in
the working tree. That is the whole-tree churn `CLAUDE.md` warns about, arriving
from a direction the warning does not name. Anyone evaluating R2 should run it in a
throwaway worktree, or expect to throw the tree away afterwards.

**R3. Self-tests for the highest-stakes gates that lack them**, modelled on
`tests/test_check_class_cache.py`: `check_no_emoji` and `check_font_sizes` first,
since both are blocking-by-intent and neither has ever been shown to fail.

**R4. The install itself.** Nothing detects a missing `pre-commit install`. A
`make doctor` target that reports it is the honest version -- a CI check cannot see
a contributor's git hooks, so this one genuinely cannot be mechanised the usual way
and should be documented rather than pretended.

**Recommendation: R1 now, R3 next, R2 only behind a cleanup decision.** R1 closes
the four named gaps for every contributor tonight; R2 is the right shape and is
currently blocked by a mess it did not create.

---

*Method note: the "hashes the working tree" heuristic in the audit script produced
one false positive (`check_credentials.py`), corrected above by reading the code.
Counts of tools come from the script; every claim about a specific tool in this
document was re-checked by hand against the file.*
