# Gate audit -- 2026-08-24

Audit of every gate in `.github/workflows/` (16 workflows) and
`.pre-commit-config.yaml` (36 hooks), against four questions:

- **(a) WHAT does it test**, read from the code it executes, not from its name,
  its comments or its own docstring.
- **(b) CAN IT RETURN BOTH ANSWERS?** What input makes it red, what input makes
  it green. Where one of those cannot be constructed, that is the finding.
- **(c) DOES ANYTHING ACT ON THE RESULT?** A red that blocks nothing and
  notifies nobody is theatre.
- **(d) IS IT POINTED AT THE RIGHT INPUT?** A working check aimed at the wrong
  file is the failure a green suite hides.

Audited at `161240be`. This is an audit, not a fix: nothing here changes a gate.
Where a thing could not be determined it is written `UNKNOWN` with the command
that would settle it.

Every claim below is followed by the command that produced it. Commands were run
from the repo root on Windows (Git Bash) unless marked otherwise.

---

## 0. Three structural facts everything else rests on

These were measured first because most of the findings are consequences of them.

### 0.1 The default `GITHUB_TOKEN` in this repo is READ-ONLY

```bash
gh api repos/PipFoweraker/pdoom1/actions/permissions/workflow
# {"default_workflow_permissions":"read","can_approve_pull_request_reviews":false}
```

Any job without an explicit `permissions:` block that tries to create an issue,
post a comment, or push, gets HTTP 403 `Resource not accessible by integration`.
**10 of 16 workflows have no `permissions:` block:** `data-validation`,
`docs-sync`, `enhanced-cicd-pipeline`, `godot-tests` (job-level only, on one job
of six), `pre-release-checks`, `quality-checks`, `release-sync-monitor`,
`sync-dev-blog`, `sync-documentation`, `sync-game-version`.

```bash
grep -L '^permissions:' .github/workflows/*.yml
```

Splitting those ten by whether the missing block actually costs anything:

- **3 write nothing at all**, so it is free: `enhanced-cicd-pipeline`,
  `quality-checks`, `release-sync-monitor`.
- **3 write cross-repo with a PAT** (`CROSS_REPO_TOKEN` / `WEBSITE_SYNC_TOKEN`),
  so the default token is not the one being used: `sync-dev-blog`,
  `sync-documentation`, `sync-game-version`.
- **4 attempt a write with the default token and get 403**: `data-validation`
  (only on `if: failure()`, so not yet observed), `docs-sync` (F5),
  `godot-tests` (F17, masked), `pre-release-checks` (F6, loud).

### 0.2 The default shell is `bash -e` WITHOUT `pipefail`

Measured from this repo's own logs, not from documentation. A `run:` step with no
`shell:` key:

```bash
gh api "repos/PipFoweraker/pdoom1/actions/jobs/97322816968/logs" | grep -n "shell:"
# 152: shell: /usr/bin/bash -e {0}
```

A `run:` step that declares `shell: bash`:

```bash
gh api "repos/PipFoweraker/pdoom1/actions/jobs/97319351960/logs" | grep -n "shell:"
# 210: shell: /usr/bin/bash --noprofile --norc -e -o pipefail {0}
```

Two consequences, both demonstrated rather than argued. These two commands are
the whole demonstration; run them anywhere:

```bash
# (1) under -e, the line after a failing command is UNREACHABLE
bash -e -c 'python -c "import sys; sys.exit(3)" >/dev/null 2>&1; EXITCODE=$?; echo "REACHED, $EXITCODE"'
echo $?     # -> 3, and "REACHED" never printed

# (2) without pipefail, $? after a pipeline is the RIGHTMOST command
bash -e -c 'python -c "import sys; sys.exit(1)" | tee /dev/null; echo "after pipe = $?"'
# -> after pipe = 0
```

Every line that reads `$?` after a plain command in this estate is therefore
unreachable. There are seven, in two shapes:

- **Five `if [ $? ... ]` blocks**, all harmless. `-e` already failed the step; the
  dead block was only going to print a nicer message. They still mislead a reader
  into thinking a check exists. Listed in F20.
- **Two `VAR=$?` assignments.** `data-validation.yml:46` is harmless for the same
  reason. `enhanced-release.yml:54` is **not**, because the unreachable line was
  feeding a job output that four downstream jobs gate on. That is F2.

### 0.3 Only THREE status checks can block a merge, and admins bypass them

```bash
gh api repos/PipFoweraker/pdoom1/branches/main/protection \
  --jq '{required: .required_status_checks.contexts, strict: .required_status_checks.strict, enforce_admins: .enforce_admins.enabled}'
# {"required":["GDScript Syntax Check","Unit Tests","quality-checks"],"strict":false,"enforce_admins":false}
```

A real PR carries thirteen check contexts:

```bash
gh pr checks 1303
```

`GDScript Syntax Check`, `Integration Tests`, `Pipeline Summary`,
`Self-merge class eligibility`, `Sim Tier PR Status`, `Simulation Tests`,
`Stage 1: Basic Validation`, `Stage 2: Code Quality`,
`Stage 3: Integration Testing (3.11)`, `Test Summary`, `Unit Tests`,
`quality-checks`, `Quality Dashboard Update`.

**Three of thirteen can block anything.** The other ten answer (c) with "nothing"
before their content is even examined. And `enforce_admins: false` means the
admin-merge path CLAUDE.md documents for agent PRs walks past all three.

`strict: false` additionally means a branch need not be current with `main`, so a
green result can be about a tree that no longer exists.

---

## 1. Findings, ranked

Ranked by (c) first, then (b), per the brief: a gate nothing acts on is worse
than one that cannot fail, because it costs attention as well as buying nothing.

### F1. `enhanced-release` publishes the release BEFORE it verifies the release. MEASURED.

`verify-release-urls` declares `needs: [create-github-release]`. The v0.14.3
timeline:

```bash
gh api "repos/PipFoweraker/pdoom1/actions/runs/32690368004/jobs" \
  --jq '.jobs[] | [.name, .conclusion, .started_at, .completed_at] | @tsv'
```

| job | conclusion | started | completed |
|---|---|---|---|
| Create GitHub Release | success | 04:36:30 | **04:37:16** |
| Verify Release Download URLs | **failure** | 04:37:18 | 04:37:34 |

The release was public at 04:37:16. The 404 was detected 18 seconds later.
Nothing un-publishes it.

```bash
gh api "repos/PipFoweraker/pdoom1/actions/jobs/97323684446/logs" | grep -E '404|\[OK\]'
#   [OK] v0.14.3.windows      200
#   [OK] v0.14.3.linux        200
#   [!]  v0.14.3.mac          404 (Not Found)  .../PDoom-macOS-v0.14.3.zip
```

**A second, separate finding inside the same job.** The steps are sequential in
one job, so the failure of step 5 SKIPPED step 6:

```bash
gh api "repos/PipFoweraker/pdoom1/actions/runs/32690368004/jobs" \
  --jq '.jobs[] | select(.name=="Verify Release Download URLs") | .steps[] | "\(.number). \(.name) = \(.conclusion)"'
# 5. Verify this release's download URLs resolve = failure
# 6. Verify the unversioned platform aliases were published = skipped
# 7. Sweep committed feed index for rotted entries (report-only) = skipped
```

Step 6 is the check the workflow's own comment describes as the INDEPENDENT
second path -- the one that exists because #1068 hid behind a green feed check.
It did not run on the release that most needed it. Two independent assertions
were serialised into one job, so the first one's failure silenced the second.

- (a) Whether the URLs in the generated feed, and the three unversioned aliases,
  answer HTTP 200.
- (b) Both answers reachable, and both observed. Red: v0.14.3 (macOS export
  dropped). Green: v0.14.2.
- (c) **Nothing.** It turns the run red after publication. There is no
  un-publish, no issue, no revert.
- (d) Right input (the live URLs), wrong position in the graph.

### F2. A data-validation failure turns the whole release into a SILENT GREEN NO-OP. REASONED, not observed.

`enhanced-release.yml` lines 46-70:

```yaml
      - name: Run historical data validation
        id: validate
        continue-on-error: true
        run: |
          python scripts/validate_historical_data.py --verbose > validation_report.txt 2>&1
          VALIDATION_EXIT=$?
          ...
          echo "hash=$DATA_HASH" >> $GITHUB_OUTPUT
          if [ $VALIDATION_EXIT -eq 0 ]; then echo "status=success" >> $GITHUB_OUTPUT
          else echo "status=failed" >> $GITHUB_OUTPUT ; fi
          exit $VALIDATION_EXIT
```

Trace it against fact 0.2. If the python exits non-zero:

1. `bash -e` kills the step ON THAT LINE. `VALIDATION_EXIT=$?` never executes.
2. Therefore `hash=` and `status=` are **never written**. Both job outputs are
   empty strings, not `failed`.
3. `continue-on-error: true` masks the step failure; the job conclusion is
   `success`, so `failure()` in the next step is FALSE and
   **"Create triage issue on validation failure" never runs.**
4. `build-godot` gates on
   `if: needs.validate-data.outputs.validation_status == 'success' || inputs.skip_validation`.
   Empty string is not `success`; on a tag push `inputs` is null. **Skipped.**
5. Every downstream job `needs:` `build-godot`, so all skip. `notification` runs
   under `if: always()` and matches neither branch, printing nothing.
6. All jobs skipped plus one success = **run conclusion `success`**.

Net: a tag is pushed, `enhanced-release` goes green, no build happens, no release
is published, no issue is filed. The `status=failed` branch that was written to
handle exactly this is on a line that cannot be reached.

- (b) The red input exists (a malformed file under `godot/data/` or
  `shared/data/`); the gate answers it with green-and-silence.
- (c) The intended consumer (`build-godot`'s `if:`, the triage issue) is wired to
  a value that is never set.
- Evidence status: **not observed.** Validation has never failed in this workflow:
  `gh api ".../workflows/enhanced-release.yml/runs?per_page=100" --paginate --jq '.workflow_runs[].conclusion' | sort | uniq -c` gives 12 success / 9 failure, and
  every failure so far was downstream. The step semantics in 0.2 are measured;
  the composition is inferred.
- **Command that would settle it:** on a throwaway branch, break one JSON file
  under `godot/data/`, then
  `gh workflow run enhanced-release.yml -f version=v0.0.0-gateprobe -f prerelease=true`
  and read the run's conclusion and the `validate-data` job outputs.

### F3. Two ASCII gates cannot return red, and 120 files are currently non-compliant. MEASURED.

`quality-checks.yml` "ASCII Compliance Check" and
`enhanced-cicd-pipeline.yml` "ASCII Compliance Check" both run
`python scripts/intelligent_ascii_converter.py --dry-run`.

In `scripts/intelligent_ascii_converter.py`, `success = True` is set at line 634
and is only ever assigned `False` at line 651 -- inside the `if args.file:`
single-file branch. CI passes no `--file`, so it takes the `--directory` branch
(default `Path(".")`), where `success` is never touched. Line 697 returns
`0 if success else 1`.

Proven by running it (`bash scratchpad/gateaudit/ascii_probe.sh`):

```bash
python scripts/intelligent_ascii_converter.py --dry-run > /dev/null 2>&1; echo $?
# 0

# plant a violation and re-run
printf 'smart quote \xe2\x80\x9chello\xe2\x80\x9d em dash \xe2\x80\x94 arrow \xe2\x86\x92\n' > PROBE.md
python scripts/intelligent_ascii_converter.py --dry-run 2>&1 | grep PROBE.md
#   [FILE] SIMULATE PROBE.md: WOULD_UPDATE      <- it SEES it
python scripts/intelligent_ascii_converter.py --dry-run > /dev/null 2>&1; echo $?
# 0                                              <- and reports green
```

How much is currently hidden:

```bash
python scripts/intelligent_ascii_converter.py --dry-run 2>&1 | grep -c "WOULD_UPDATE"
# 120
```

**120 files in the tree today would be rewritten by the converter, and both gates
report green on all of them.** The script's own comment at line 588 says "the dry
run still reports every violation and returns non-zero, which is what CI
(`--dry-run`) gates on." The code does not do that. This is the case the brief
warned about: do not trust a gate's docstring about itself.

- (a) Nominally: non-ASCII characters anywhere in the tree. Actually: nothing.
- (b) **The red input does not exist.** Green for every input.
- (c) `quality-checks` IS a required context, so a red here would genuinely block
  a merge. It cannot go red.
- (d) Right input, broken verdict.

### F4. The other ASCII gate reports 2111 files and calls them warnings. MEASURED.

`quality-checks.yml` and `enhanced-cicd-pipeline.yml` both run:

```yaml
python scripts/enforce_standards.py --check-all || echo "WARNING  Standards check warnings (non-blocking during Godot migration)"
```

```bash
python scripts/enforce_standards.py --check-all; echo "EXIT: $?"
# [WARNING] Found 2111 files with Unicode content
# Summary: 0 errors, 5 warnings
# EXIT: 0
```

Two independent reasons this cannot go red: Unicode is classified as a warning so
the exit is 0, and the `|| echo` would swallow a non-zero anyway. Removing either
one alone changes nothing.

Combined with F3, the ASCII position is: **the only ASCII enforcement in this
repo that can fail is the two pre-commit hooks** (`enforce-standards --incremental`
and `no-emoji`), which run only on the committer's machine. See F14.

### F5. `docs-sync` has been red on every PR for nine months, for a permissions block. MEASURED.

```bash
gh api "repos/PipFoweraker/pdoom1/actions/workflows/docs-sync.yml/runs?per_page=100" \
  --paginate --jq '.workflow_runs[] | [.event,.conclusion] | @tsv' | sort | uniq -c
#      77 pull_request  failure
#      50 push          success
```

77 of 77. The `check-docs-sync` job passes every time; the `comment-pr` job 403s:

```bash
gh run view 32569928505 --log-failed
# ##[error]Unhandled error: HttpError: Resource not accessible by integration
# url: 'https://api.github.com/repos/PipFoweraker/pdoom1/issues/1271/comments'
# status: 403
```

The 50 push runs are green because their auto-commit step is always skipped
(`has_changes` is false). If the mechanics docs ever DID drift on `main`, that
step does `git push` with the same read-only token and would 403 too. The green
half of the record is green because it has never had to do anything.

- (a) `check-docs-sync`: whether `generate_mechanics_docs.py` output matches the
  committed docs. `comment-pr`: posts a preview comment.
- (b) The real check can return both answers. The comment job can only return
  red.
- (c) `docs-sync` is not a required context, so its red blocks nothing. It has
  cost nine months of a red X on PRs that meant nothing about the PR. This is the
  single most expensive item in the audit by the (c) criterion, because a
  permanent meaningless red teaches everyone to discount reds -- which is how a
  real one gets waved through.
- (d) Note the payload the 403 rejects contains `## [U+1F4DA] Documentation
  Preview`. See F10.

### F6. `pre-release-checks` fails into an empty room, and nothing downstream depends on it. MEASURED.

On the first v0.14.3 tag push:

```bash
gh api "repos/PipFoweraker/pdoom1/actions/runs/32689075022/jobs" \
  --jq '.jobs[] | .steps[] | "\(.number). \(.name) = \(.conclusion)"'
# 3. Check CHANGELOG updated = success
# 5. Release notes guard (structure + citations) = failure     <- a REAL catch
# 8. Post validation results = failure                          <- the 403
```

```bash
gh api "repos/PipFoweraker/pdoom1/actions/jobs/97319351960/logs" | grep -E "RN003|403|not accessible"
# [FAIL] RN003: CHANGELOG section [0.14.3]: cites #1225 but that issue is OPEN
# RELEASE NOTES CHECK FAILED: 7 fatal, 0 warning
# RequestError [HttpError]: Resource not accessible by integration ... status: 403
```

The gate found a genuine defect in 21 seconds and could not tell anyone. Its
lifetime record:

```bash
gh api ".../workflows/pre-release-checks.yml/runs?per_page=100" --paginate \
  --jq '.workflow_runs[].conclusion' | sort | uniq -c
#  16 failure
#   4 success
```

Red 16 times out of 20 and it has never stopped a release, because
`enhanced-release.yml` does not reference it in any way.

Per-step, this workflow is four assertions and one of them is real:

| step | (b) can it go red? | note |
|---|---|---|
| Check CHANGELOG updated | yes | unanchored -- see F13 |
| Release notes guard (structure + citations) | yes, and does | the one that works |
| Check version in project.godot | yes | duplicated in `release-reminder` and `quality-checks` |
| Check for uncommitted changes | **no** | see F12 |
| Post validation results | only red | 403, always |

One of those four is the ONLY thing in the estate asserting it. `enhanced-release`
does not fail when the CHANGELOG has no section for the tag -- its
`Extract changelog` step falls back to a stub body, and the release-body guard
passes the stub:

```bash
printf 'Release v9.9.9\n\nSee CHANGELOG.md for details.\n' > /tmp/stub.txt
python scripts/check_release_notes.py --body /tmp/stub.txt --tag v9.9.9 > /tmp/rn.txt 2>&1
echo $?     # 0
tail -3 /tmp/rn.txt   # [OK] release notes check passed (1 warning(s))
```

So a tag with no CHANGELOG section publishes a release body reading "See
CHANGELOG.md for details", and the only gate that objects is one nothing waits
for. (Exit code read from the command, not through a pipe -- `... | tail; echo $?`
reports `tail`'s status and would have returned the same 0 for the wrong reason.)

### F7. `release-ledger` disarmed itself the moment the thing it watches was fixed. MEASURED.

Merged 2026-08-24 to catch "a version was bumped and never tagged". It has run
twice and failed twice:

```bash
gh api ".../workflows/release-ledger.yml/runs?per_page=10" \
  --jq '.workflow_runs[] | [.event,.conclusion,.created_at] | @tsv'
# schedule  failure  2026-08-24T04:36:29Z
# push      failure  2026-08-24T04:08:10Z
```

```bash
gh api "repos/PipFoweraker/pdoom1/actions/runs/32690643064/jobs" \
  --jq '.jobs[] | .steps[] | "\(.number). \(.name) = \(.conclusion)"'
# 4. Prove the classifier can return both answers = failure
# 5. Check the ledger = skipped
# 6. Open or update the rolling issue = skipped
# 7. Fail if the ledger is not settled = skipped
```

```bash
gh api "repos/PipFoweraker/pdoom1/actions/jobs/97323554003/logs" | grep SELF-TEST
# [release_ledger] SELF-TEST FAIL: 0.14.3 should classify UNTAGGED -- if this now
# fails because the tag was pushed, replace this anchor with the next untagged
# version rather than deleting it
```

The self-test is anchored on the literal string `0.14.3` being untagged. v0.14.3
was tagged the same day. So the self-test fails permanently, and because it is
step 4 of 7 under `bash -e`, **the actual ledger check never runs.**

The self-test's own message predicted this and asked a human to re-anchor. This
is the docs-sync shape recurring on a one-day-old workflow: permanently red for a
reason unrelated to what it gates. Two workflows, nine months apart, same defect
class.

- (a) Whether every value `version.txt` has held is either tagged or declared in
  `docs/releases/UNTAGGED.md`.
- (b) The classifier can demonstrably return both answers -- that is what the
  self-test is for -- but the WORKFLOW currently returns only red, from step 4.
- (c) The rolling issue and the failing verdict are both `needs`-gated on
  `steps.check.outputs.status`, which is never set. Nothing is acted on.
- (d) Right input; the anchor is pointed at a moving target.

Credit where due: the `${PIPESTATUS[0]}` handling in this workflow (line 120) is
correct, and the exit-1-vs-exit-2 split is the right distinction. The wiring is
sound and the anchor is not.

### F8. `GDScript Syntax Check` is a required check that does not check GDScript syntax across the tree. MEASURED.

`godot-tests.yml` runs `godot --headless --path godot --quit 2>&1 | tee
godot_output.log` and greps the log. I built a minimal Godot 4.5.1 project and
ran the four relevant cases
(`bash scratchpad/gateaudit/probe.sh`):

| case | godot `--quit` exit | output | workflow grep verdict |
|---|---|---|---|
| everything clean | 0 | no errors | GREEN (correct) |
| syntax error in an **unreferenced** `.gd` | **0** | **nothing at all** | **GREEN (wrong)** |
| syntax error in an **autoload** | 0 | `SCRIPT ERROR: Parse Error: ...` + `ERROR: Failed to load script ... "Parse error".` | RED (correct) |
| undeclared identifier in an autoload (the stale-cache shape) | 0 | same two lines | RED (correct) |

Two things fall out.

**(i) `godot --quit` exits 0 in every case, including a broken autoload.**
CLAUDE.md's warning that "it did not crash proves nothing" is confirmed; the
grep is the entire verdict, which is the right design.

**(ii) A parse error in a script the boot path does not load produces NO OUTPUT.**
`--quit` compiles only what startup loads (autoloads, main scene). So the gate
named "GDScript Syntax Check" -- one of the three required contexts -- is blind
to a parse error in any script not on the boot path.

The tree-wide check does exist. It is inside the OTHER job:
`scripts/run_godot_tests.py` runs a compile-all walker
(`res://tools/syntax_walk.tscn`, line 446) with three independent conditions --
proof the walk ran, a manifest check that `walked == on_disk`, and the marker
grep -- and that runner is what "Unit Tests" invokes. So the thorough check is
downstream of the shallow one that shares its name:

```yaml
  unit-tests:
    needs: syntax-check
```

A separate, smaller point: the workflow's grep is `grep -E` (case sensitive) and
its pattern list carries `Parse error` (lowercase). Godot's `SCRIPT ERROR: Parse
Error:` line has a capital E and is NOT matched by it. The gate still goes red
because Godot prints a second line, `ERROR: Failed to load script ... with error
"Parse error".`, which matches twice over. `run_godot_tests.py` matches
case-insensitively and its comment at line 452 says why: "the CLI emits 'Parse
error' but runtime `load()` emits 'SCRIPT ERROR: Parse Error:' (different
capitalisation)." The workflow copy did not inherit that lesson. It works today
by redundancy, not by intent.

### F9. `Commit Message Check` has never read a commit message anyone wrote. MEASURED.

`quality-checks.yml`:

```bash
commit_msg=$(git log -1 --pretty=%B)
```

`actions/checkout` on a `pull_request` event checks out the merge ref, so
`git log -1` is the synthetic merge commit. From PR #1303's own run log:

```bash
gh api "repos/PipFoweraker/pdoom1/actions/jobs/97322584751/logs" | grep "Commit message:"
# Commit message: Merge e620e5b07ccb6a7b601a5373e203e3ff4e4f1e71 into b9f5526061a641e79a4716f5fe979f2f739b006f
```

- (a) Nominally: non-ASCII in the PR's commit messages. Actually: non-ASCII in a
  message GitHub generates, which is two SHAs and the word "Merge".
- (b) **The red input cannot be constructed through the intended route.** No
  commit message an author writes is ever examined.
- (c) It is inside the required `quality-checks` job, so a red WOULD block. It
  cannot go red.
- (d) **Wrong input.** This is the exact failure mode the brief names. The fix
  shape (do not fix here) is a range against `github.event.pull_request.base.sha`.

### F10. `check_no_emoji.py` is real, blocking, and cannot see `.github/`. MEASURED.

```bash
grep -n "^GODOT = " scripts/check_no_emoji.py
# GODOT = PROJECT_ROOT / "godot"
```

Everything outside `godot/` is invisible to it. Using the gate's own `is_emoji()`
predicate against `.github/`:

```bash
python - <<'PY'
import pathlib, sys
sys.path.insert(0, 'scripts')
from check_no_emoji import is_emoji
for p in sorted(pathlib.Path('.').glob('.github/**/*')):
    if not p.is_file(): continue
    try: t = p.read_text(encoding='utf-8')
    except Exception: continue
    hits = [c for c in t if is_emoji(ord(c))]
    if hits: print(p.as_posix(), len(hits), sorted({'U+%04X' % ord(c) for c in hits}))
PY
```

| file | count | codepoints |
|---|---|---|
| `.github/copilot-instructions.md` | 2 | U+26A0 U+FE0F |
| `.github/FUTURE_FEATURES_ISSUE.md` | 2 | U+2B50 |
| `.github/ISSUE_TEMPLATE/comprehensive_verification_tests.md` | 2 | U+23F3 |
| `.github/RELEASE_CHECKLIST.md` | 1 | U+2715 |
| `.github/workflows/docs-sync.yml` | 1 | U+1F4DA |
| `.github/workflows/enhanced-cicd-pipeline.yml` | 9 | U+1F3C1 U+1F3F7 U+1F4BE U+1F4C2 U+1F4E6 U+1F524 U+1F9EA U+26A1 |

**17 emoji codepoints in six files**, none of which any gate can see. Two of them
reach humans: the `docs-sync` one is in the PR comment body (F5), and
`.github/RELEASE_CHECKLIST.md` is read verbatim by `release-reminder.yml` and
pasted into a GitHub issue on every tag.

- (a) Non-ASCII in `godot/**/*.gd` and `godot/data/**/*.json`; emoji in
  `godot/**/*.tscn`.
- (b) Both answers reachable within its scope. It is a well-built gate.
- (c) Blocking pre-commit hook. But see F14: it runs nowhere else.
- (d) **Wrong scope.** The rule in CLAUDE.md says "Emoji are NEVER allowed
  anywhere"; the mechanism enforces it in one subtree.

### F11. `pre-release-checks` "Check for uncommitted changes" cannot fail. MEASURED by construction.

```bash
if [ -n "$(git status --porcelain)" ]; then ... exit 1; fi
```

It runs on a fresh `actions/checkout` and the only preceding steps are
`setup-python` and `check_release_notes.py`, which writes nothing:

```bash
grep -nE "open\(.*['\"]w|write_text|\.write\(|shutil|os.remove" scripts/check_release_notes.py
# (no output)
```

The working tree at that point is a clone. There is no input that makes this red.
The issue body the workflow files lists "Uncommitted changes" as a common cause
-- a cause it structurally cannot detect.

### F12. The CHANGELOG grep is unanchored, but it has never produced a false green. MEASURED -- and this CORRECTS the premise I was given.

The gate is `grep -q "$TAG_VERSION" CHANGELOG.md`, which matches the version
string anywhere in the file, including inside a bullet in an unrelated section.

I was told 6 of 25 real tags passed it with no section heading. **That does not
reproduce.** Replaying the gate against every tag
(`bash scratchpad/gateaudit/changelog_probe2.sh`):

```bash
for tag in $(git tag -l 'v*.*.*' | sort -V); do
  V="${tag#v}"; BODY=$(git show "$tag:CHANGELOG.md")
  printf '%s '  "$tag"
  printf '%s '  "$(printf '%s' "$BODY" | grep -q "$V" && echo GATE:PASS || echo GATE:FAIL)"
  printf '%s\n' "$(printf '%s' "$BODY" | grep -qE "^#{1,3} *\[?v?${V//./\\.}\]?" && echo HEADING:YES || echo HEADING:NO)"
done
```

Result over 26 tags carrying a CHANGELOG: **15 PASS, 11 FAIL, and 0 cases where
the gate passed without a section heading.** (My first pass reported 5 such cases;
that was my regex, which did not allow the leading `v` the headings actually use.
Corrected before reporting.)

So the finding is smaller and more precise than the premise: the unanchored grep
is a LATENT hole, not a realised one. It is trivially constructible --

```bash
# would make it green with no section for the version at all:
echo "- reverted the change from 0.99.0-rc1" >> CHANGELOG.md   # tag v0.99.0 now passes
```

-- and the anchored check already exists next door
(`scripts/check_release_notes.py --changelog-structure`, run in the very next
step). The grep is redundant with a stricter neighbour rather than dangerous on
its own.

Also worth stating: 11 of 26 tags would have FAILED this gate, and every one of
them shipped. That is a stronger statement about (c) than about (b).

### F13. Steps that can only ever return one answer. MEASURED by reading.

| workflow | step | why it cannot go red |
|---|---|---|
| quality-checks | Import Cleanup Check | two `echo`s, no command |
| quality-checks | Web Export System Check | two `echo`s, no command |
| quality-checks | CLI Interface Check | two `echo`s, no command |
| quality-checks | Development Standards Check | `\|\| echo` (F4) |
| quality-checks | ASCII Compliance Check | tool always returns 0 (F3) |
| quality-checks | Health Gate Check | `project_health --quick-check` has no `--ci-mode`, so its score-based `sys.exit` is unreachable; the second command is `\|\| echo` |
| enhanced-cicd | Import Structure Validation | three `echo`s |
| enhanced-cicd | Type Annotation Coverage | `echo "type_coverage=85"` above `# TODO: Implement type annotation coverage checker` |
| enhanced-cicd | Code Quality Metrics | consumes the 85; `>= 80` -> always `HIGH` |
| enhanced-cicd | Import Cleanup Check | two `echo`s |
| enhanced-cicd | Set validation status | `echo "passed=true"`, unconditional |
| enhanced-cicd | Run Test Suite | `\|\| echo "INFO: Some Python tests may fail"` |
| enhanced-cicd | Performance Benchmark | two `echo`s |
| enhanced-cicd | Memory Usage Check | two `echo`s |
| enhanced-cicd | ASCII Compliance Check | tool always returns 0 (F3) |
| enhanced-cicd | Version Consistency Check | both branches print PASSED |
| data-validation | Generate feeds (placeholder) | `echo` + writes a stub JSON |
| enhanced-release | Deploy to GitHub Pages | `echo` + `ls -la` + `# TODO: Add your deployment logic here` |
| pre-commit | style-guide-reminder | see below |

**19 steps.** Two near-misses that do NOT belong on that list, stated so the
count is honest: `quality-checks` "Documentation Check" and `enhanced-cicd`
"File Structure Validation" both assert that a handful of files exist
(`README.md`, `CHANGELOG.md`, `godot/project.godot`, `requirements.txt`). Those
CAN return red -- delete one of those files and they do. They are vacuous rather
than inert, which is a different and much milder complaint.

Verify the Health Gate claim:

```bash
python scripts/project_health.py --quick-check; echo "EXIT: $?"
# [SCAN] Linting Issues: 6299
# [QUICK] Quick Health Score: 50/100
# EXIT: 0
sed -n '711,721p' scripts/project_health.py     # the sys.exit block is inside `if args.ci_mode:`
```

A quick score of 50 would be `sys.exit(1)` under `--ci-mode`. The workflow does
not pass `--ci-mode`.

Verify the style-guide-reminder claim:

```bash
sed -n '150,158p' scripts/check_style_guide.py
#   if strict_mode:  return 1
#   else:            print("[WARNING] Proceeding with commit (warning only)"); return 0
grep -n "check_style_guide" .pre-commit-config.yaml
#   entry: python scripts/check_style_guide.py      <- no --strict
```

It cannot fail locally either. It is a print statement with a hook wrapper.

### F14. `Type Annotation Coverage` and the health score are built on constants. MEASURED.

Beyond the `echo "type_coverage=85"` already named, the same shape is inside the
health scorer that gates `enhanced-cicd` Stage 2:

```bash
sed -n '196,202p' scripts/project_health.py
#   def _check_import_cleanliness(self) -> Dict[str, int]:
#       return {'unused_imports': 0,   # TODO: Implement proper analysis
#               'circular_imports': 0, 'import_errors': 0}
```

And the two health numbers disagree wildly on the same tree:

```bash
python scripts/project_health.py --quick-check   # Quick Health Score: 50/100, Linting Issues: 6299
python scripts/project_health.py --ci-mode --output /tmp/hr.json
# Overall Health Score: 97/100
#    [GREEN] Code Quality: 100/100
```

The number that gates CI is 97 with Code Quality 100/100, on a tree the same
script separately scores 50 with 6299 lint issues. The `--ci-mode` thresholds are
60 (fail) and 80 (warn). A 97 has 37 points of headroom against a metric partly
made of hardcoded zeros.

### F15. 36 pre-commit hooks; `pre-commit run` appears in ZERO workflows. MEASURED.

```bash
grep -rn "pre-commit run" .github/workflows/     # no matches
grep -rn "pre-commit" .github/workflows/         # 2 matches, both in prose comments
```

The complete set of Python entrypoints CI actually invokes:

```bash
grep -rhoE "(scripts|tools)/[a-zA-Z_/]+\.py" .github/workflows/ | sort -u
```

`build_all_platforms`, `check_release_notes`, `check_site_release_freshness`,
`ci_health_integration`, `enforce_standards`, `generate_mechanics_docs`,
`generate_release_manifest`, `generate_release_metadata`, `health_tracker`,
`intelligent_ascii_converter`, `pre_build_validation`, `project_health`,
`run_godot_tests`, `sync_website_docs`, `validate_historical_data`,
`verify_release_urls`, `assets/check_provenance`, `build_release`,
`check_ladder_bump`, `check_refusal_classification`, `check_release_ledger`,
`check_scene_nav`, `check_self_merge_eligibility`, `sync_version`.

Cross-referenced against the hooks, **exactly five pre-commit hooks have an
independent blocking CI invocation**: `provenance-check`,
`refusal-classification-check`, `scene-nav-check`, `version-sync-check`, and
`changelog-structure-check` (tag-time only, via `pre-release-checks`). One more,
`enforce-standards`, has a CI invocation that cannot fail (F4).

**The remaining 30 hooks run on the committer's machine and nowhere else:**

| hook | what is unenforced in CI |
|---|---|
| `no-emoji` | the emoji rule (F10) |
| `font-size-ssot-check` | the 280-override ratchet |
| `balance-key-census` | the only gate on the balance surface, either direction |
| `trust-declaration-check` | `docs/TRUST.md` vs the source |
| `credential-check` | C2PA credentials on shipped PNGs |
| `dq-index-check` `adr-index-check` `tools-index-check` `action-taxonomy-index-check` `credits-json-check` `commitment-calendar-check` `rulings-index-check` `release-index-check` | eight generated indexes, the repo's whole anti-rot pattern |
| `review-js-parses` | the JS-in-Python gate from the 2026-08-14 dead-gallery day |
| `check-pyc-files` `check-pygame-dir` `style-guide-reminder` | -- |
| `class-cache-check` | correctly CI-exempt: CI always clones fresh, so it would watch the one place that is never wrong. Its DETECTOR is unit-tested in `quality-checks`, which is the right substitute. |
| upstream: `trailing-whitespace` `end-of-file-fixer` `check-yaml` `check-json` `check-added-large-files` `check-case-conflict` `check-merge-conflict` `detect-private-key` `mixed-line-ending` | -- |
| upstream: `black` `isort` `ruff` | no formatting or lint gate in CI at all |

`git commit --no-verify`, or a checkout where `pre-commit install` was never run,
bypasses all thirty. Nothing downstream re-asserts them. Note in particular that
`detect-private-key` and `check-added-large-files` are the two with irreversible
consequences, and both are local-only.

- (c) for this whole class: the consumer is one developer's local git hook. That
  is a real consumer -- these hooks do fire and do block -- but it is a consumer
  with an opt-out flag and no record.

### F16. Notifications and summaries that print FAILURE and exit 0. MEASURED by reading.

- `enhanced-release` job `notification`, `if: always()`. On the first v0.14.3 run
  (`create-github-release` = failure) it ran and printed
  `ERROR Release v0.14.3 failed!` into a log, job conclusion `success`. It sends
  nothing anywhere. `grep -n "TODO\|Discord\|Slack" .github/workflows/*.yml`
- `enhanced-cicd` job `pipeline-summary`, `if: always()`. Prints
  `ERROR PIPELINE FAILURE: Quality gates failed` and exits 0. It is one of the
  thirteen PR check contexts, and it is green while printing FAILURE.
- `enhanced-cicd` job `quality-dashboard`. Writes `quality_metrics.json` to a
  runner that is then destroyed -- no upload-artifact, no commit. Nothing can
  ever read it.
- `data-validation` job `publish-feeds`. Writes `provenance.json` with
  `"validation_passed": true` **hardcoded**, and writes it AFTER the
  `upload-artifact` step, so it is not in the artifact either.
- `sync-documentation` job `notify-completion`: three echoes, `if: always()`.

### F17. `godot-tests` posts a PR comment that has never posted, and reports success. MEASURED.

```bash
gh api "repos/PipFoweraker/pdoom1/actions/jobs/97322902062/logs" | grep -E "403|not accessible|Unhandled"
# RequestError [HttpError]: Resource not accessible by integration
# status: 403,
# ##[error]Unhandled error: HttpError: Resource not accessible by integration
```

And the API reports:

```bash
gh api "repos/PipFoweraker/pdoom1/actions/runs/32690282031/jobs" \
  --jq '.jobs[] | select(.name=="Test Summary") | .steps[] | "\(.name) = \(.conclusion)"'
# Post comment on PR = success
```

`continue-on-error: true` rewrites the step conclusion to `success`, so **even
the API lies about it.** The comment "Cosmetic; a transient GitHub API hiccup must
not fail the gate" describes a transient failure; this is a permanent one, and
the mask makes it undiscoverable without opening the log.

The clean contrast is in the same run: `sim-tier-pr-status` declares
`permissions: pull-requests: write` at job level and its comment posts fine
(`gh api ".../actions/jobs/97324178720/logs" | grep -c 403` -> 0). Same repo,
same run, same API call. The only difference is the permissions block.

### F18. `sync-documentation`'s repository selector does not select. MEASURED by reading.

```yaml
      - name: Skip if not targeting this repository
        if: github.event.inputs.target_repo != '' && github.event.inputs.target_repo != matrix.target.repo
        run: |
          echo "Skipping ${{ matrix.target.repo }} - not the target repository"
          exit 0
```

`exit 0` ends the STEP, not the job. Every subsequent step -- checkout of the
target repo, the sync, `git add .`, `git push` -- runs anyway. Dispatching with
`target_repo: pdoom1-website` still writes to `pdoom-data`.

Secondary: the commit step runs `git add .` inside a foreign repo, which is the
thing CLAUDE.md forbids in this one.

- (b) The step itself can return both answers; the JOB cannot honour either.
- (c) Nothing. 12 runs, all success, and the selector has never been obeyed.
- **UNKNOWN:** whether any of those 12 runs actually wrote to the wrong repo, or
  whether they all took the `sync_needed=false` path. Settle with
  `gh api ".../workflows/sync-documentation.yml/runs" --jq '.workflow_runs[].id'`
  then read each run's "Detect changed documentation" step output.

### F19. `sync-game-version` fired six times on one release with no concurrency group. MEASURED.

```bash
gh api "repos/PipFoweraker/pdoom1/actions/runs?per_page=100" \
  --jq '.workflow_runs[] | select(.head_branch=="v0.14.3") | [.name,.event,.run_started_at] | @tsv'
# Sync Game Versions to Website  release  2026-08-24T08:47:55Z
# Sync Game Versions to Website  release  2026-08-24T08:37:27Z
# Sync Game Versions to Website  release  2026-08-24T08:34:19Z
# Sync Game Versions to Website  release  2026-08-24T08:34:18Z
# Sync Game Versions to Website  release  2026-08-24T08:34:17Z
# Sync Game Versions to Website  release  2026-08-24T08:34:17Z
```

Four runs within two seconds. The `release: edited` trigger fires on every body
edit, and only two workflows in the estate declare `concurrency:`
(`live-site-release-freshness`, `self-merge-eligibility`):

```bash
grep -l '^concurrency:' .github/workflows/*.yml
```

Today each run is one idempotent `repository_dispatch`, so the herd is harmless.
The workflow's own comment records the hazard that makes it stop being harmless:
once pdoom1-website#289 lands, "a dispatch arriving mid-asset-upload makes the
website publish a version whose `platforms` are derived from an incomplete asset
list." Four dispatches racing makes that four chances instead of one.

### F20. Dead `if [ $? ... ]` blocks. MEASURED by reading, semantics proven in 0.2.

Five `if [ $? ... ]` blocks. All harmless -- `-e` already failed the step, the
block only changes the message -- but each one tells a reader that a check exists
which does not:

```bash
grep -rn 'if \[ \$? ' .github/workflows/
# data-validation.yml:142       (ajv)          harmless
# enhanced-cicd-pipeline.yml:65 (ascii)        harmless, and the tool returns 0 anyway (F3)
# enhanced-release.yml:153      (pre_build)    harmless
# quality-checks.yml:53         (ascii)        harmless, and the tool returns 0 anyway (F3)
# sync-dev-blog.yml:38          (blog index)   harmless
```

The two `VAR=$?` assignments are a separate shape:
`grep -rn '=\$?' .github/workflows/` gives `data-validation.yml:46` (harmless)
and `enhanced-release.yml:54`, which is F2.

---

## 2. The gates that work

Stated because an audit that only lists faults is not calibrated, and because
these are the shapes worth copying.

| gate | why it holds up |
|---|---|
| `enhanced-release` "Guard the release body against false delivery claims" | Runs on the exact bytes about to be published, positioned between assembly and publication. **Observed working:** it blocked the first v0.14.3 publish at 04:16:05 (`gh api ".../runs/32689075164/jobs"` -> `Create Release = skipped`). |
| `run_godot_tests.py` syntax walker | Three independent conditions: proof-the-walk-ran, a `walked == on_disk` manifest check, and the marker grep -- and it refuses to pass on silence. Case-insensitive because both capitalisations occur. |
| `run_godot_tests.py` three-outcome contract | exit 0 / 1 / 2, where 2 is DID NOT COMPLETE and never prints a test count. Refusing to report a measurement that does not exist is the rarest property in this estate. |
| `live-site-release-freshness` | Reads the live site with a cache-buster, not the repo; UNKNOWN (exit 2) stays green with a warning; `${PIPESTATUS[0]}`, correct; explicit `permissions:`; a `force_alarm` drill that exercises the real alarm path; a `resolve` job that closes the issue. 187 success / 3 failure. |
| `release-sync-monitor` | Repointed at `public/data/version.json` -- the file that is actually deployed. **Verified it really compares:** `gh api ".../actions/jobs/97342474757/logs"` shows `Latest published release: 0.14.3 / Website repo: 0.14.3 / IN SYNC`, i.e. real values, not a skipped strict check. |
| `self-merge-eligibility` | Self-test plus a hermetic unit suite, both blocking, before the real check. Author-controlled text passed via `env:`, never templated. `concurrency` with `cancel-in-progress`. Its only weakness is (c): not a required context. |
| `quality-checks` self-test steps | `check_refusal_classification --self-test`, `check_provenance --self-test`, `check_ladder_bump --self-test`, `tests.test_check_class_cache`, `tests.test_check_ladder_bump`, all blocking. This is the correct answer to "prove the gate can still fail", and it is why F7 is a wiring fault rather than a rotted classifier. |
| `godot-tests` simulation tier | Deliberately does NOT use `continue-on-error`, with the reasoning written down (#964): a real red X that blocks nothing beats a green tick hiding a failure. F17, four jobs away in the same file, is the counterexample that proves the point. |
| `data-validation` "Run schema validation" | Genuinely returns both answers -- 168 failures and 133 successes on real history. Weakness is (c) only: not a required context. |
| `sync-game-version` dispatch step | Checks the HTTP status and fails on anything but 204, and states its own honest limit in a comment: a 204 says the POST was received, not that anything subscribes. |

---

## 3. UNKNOWNs

Things this audit could not settle, with the command that would.

1. **Whether F2 happens as traced.** Not observed; validation has never failed in
   `enhanced-release`. Settle: break a JSON under `godot/data/` on a throwaway
   branch, `gh workflow run enhanced-release.yml -f version=v0.0.0-gateprobe -f prerelease=true`,
   read the run conclusion and the `validate-data` job outputs.
2. **Whether any `sync-documentation` run wrote to the wrong repo** (F18).
   Settle: for each id from
   `gh api ".../workflows/sync-documentation.yml/runs" --jq '.workflow_runs[].id'`,
   read the "Detect changed documentation" and "Commit and push changes" steps.
3. **Whether `docs-sync`'s auto-commit-to-main path would 403.** It has never
   executed (`has_changes` has always been false on push). Settle: on a branch,
   edit `docs/mechanics/` out of sync and dispatch the workflow, then read the
   "Auto-commit updated docs" step.
4. **Whether `dev-blog-automation` can complete at all.** 976 failures / 21
   successes; the file's own header says `create-dev-blog-entry` is missing its
   gitpython install. Not audited further because it is `workflow_dispatch`-only
   and the header says repair is #1009. Settle:
   `gh api ".../workflows/dev-blog-automation.yml/runs?per_page=5" --jq '.workflow_runs[].id'`
   and read the most recent failing job.
5. **Whether the 148 `quality-checks` failures were real catches or wiring.**
   Not sampled. Settle: `gh api ".../workflows/quality-checks.yml/runs?status=failure&per_page=20"`
   and tally the failing step names.
6. **Whether `strict: false` on branch protection has ever mattered** -- i.e.
   whether a PR merged green against a base it was stale against. Settle by
   comparing merge-base SHAs to `main` at merge time across recent PRs.

---

## 4. Summary count

| category | count |
|---|---|
| Workflows | 16 |
| Jobs | 41 |
| Pre-commit hooks | 36 |
| Status checks that can block a merge | **3** (and `enforce_admins: false`) |
| Workflows with no `permissions:` block, on a read-only default token | 10 |
| Workflows currently red for a reason unrelated to what they gate | 2 (`docs-sync`, `release-ledger`) |
| Steps identified that cannot return red | 19 |
| Pre-commit hooks with no CI enforcement | 30 of 36 |
| Files currently failing a gate that reports green | 120 (ASCII), 2111 (Unicode warnings), 17 emoji codepoints under `.github/` |

---

## Appendix: reproducing this audit

The probes are small and self-contained. They were run from a scratch directory,
not committed:

- `shell_semantics.sh` -- proves the `bash -e` / `pipefail` facts in section 0.2.
- `probe.sh` -- builds a minimal Godot 4.5.1 project and runs the four
  syntax-gate cases in F8. Requires `PDOOM1_GODOT` or the console binary; run
  with an isolated `APPDATA` per CLAUDE.md.
- `ascii_probe.sh` -- plants a violation and shows the ASCII gate stays green
  (F3).
- `changelog_probe2.sh` -- replays the CHANGELOG grep against every tag (F12).

Every other claim in this document is a single `gh api`, `grep` or `sed` command
quoted inline with its output.

RULING: 2026-08-24 -- a gate's verdict must be traced to a consumer before it is called a gate: a red that blocks no merge, gates no job, and reaches no human is theatre, and it costs attention as well as buying nothing -- flavour: ci-gates -- mechanism: this audit, and docs/deployment/RELEASE_FLOW_MAP_2026-08-24.md

RULING: 2026-08-24 -- a workflow that writes anything must declare `permissions:`, because this repo's default workflow token is read-only and a write attempt without one 403s into either a permanent meaningless red or, under continue-on-error, a green that hides it -- flavour: ci-gates -- mechanism: gh api repos/PipFoweraker/pdoom1/actions/permissions/workflow
