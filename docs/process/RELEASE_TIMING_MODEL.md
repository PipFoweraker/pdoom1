# Release Timing Model -- the G..N stage-gate chain

Status: v1, first data row 2026-07-26 (v0.13.1). Owner: Pip.
Source: Pip's release-pipeline timing braindump (2026-07-26), variable names
preserved verbatim. Companion tool: `tools/release_timeline.py`; data file:
`docs/process/release_timings.csv`.

## Why this exists

Pip anchors release timing on personal commitments (Rektango Fridays 5:30PM):
the question is never "how long does a release take in the abstract" but "when
must each stage START so the league is visibly WORKING before the anchor". So
the model works BACKWARD from N, and every stage duration is a measured number
from real releases, not a guess. First-cycle numbers are expected to be bad --
that is the point; each release appends a row and the estimates tighten
(antifragility/iterability, below).

Architecture qualities the pipeline is held to (Pip's list): **legibility**,
**LOUD failures AND successes** (no silent either), **antifragility**,
**iterability**.

All timestamps in this doc are UTC. Pip local (Melbourne) is UTC+10 in July,
so 00:07Z = 10:07 local.

## The chain

```
  G --------> H --------> I --------> J --------> K --------> L --------> M --------> N
  last        last        human       build       upload      confirm     deploy +    watch the
  B-quality   A-quality   gate +      each OS     assets      across      public      league deploy
  submission  submission  checklist   variant                 repos       social      start
  cutoff      cutoff      go/nogo     (min J-K                            process     FUNCTIONING
                                      gap)
  artifact:   artifact:   artifact:   artifact:   artifact:   artifact:   artifact:   artifact:
  (none yet)  (none yet)  go/nogo     green       assets      sync run    post URL    league page
                          recorded    release     N>=expected GREEN at/   exists      shows fresh
                          + tag       workflow    w/ sizes    after                   activity
                          pushed      run         on release  publish
```

Working backward: N is the deadline; M must finish before N can be observed;
L before M (do not announce what has not synced); K before L; J before K;
I decides what enters J; H and G bound what I is allowed to consider.

## Variable definitions

| Var | Definition (Pip's words) | Loud-success artifact to check |
|---|---|---|
| G | last-submission cutoff for B-quality items | cutoff time recorded; anything after G waits for next train |
| H | last-submission cutoff for A-quality items | cutoff time recorded; H > G |
| I | human-architected gate + checklist; go/nogo on gated evidence in dev/SIT flows deciding patch scope | go/nogo written down (issue comment or checklist); tag pushed = "go" executed |
| J | building each OS variant (minimise the J-K gap via serialisation/parallelisation) | build workflow run green, or local build_release.py stamp-verified output per platform |
| K | uploading | `gh release view <tag>`: asset count >= expected, sizes plausible (~80-130 MB per platform zip) |
| L | confirmation across repos | sync-game-version run GREEN at-or-after publish; website shows the new version |
| M | deploy + public social-media process | post/announcement URL exists |
| N | watching the league deploy start functioning | league shows fresh activity on the new version's board-key |

## KEY STRUCTURAL FINDING: the J-K gap is solved by PATH SELECTION

The measured data shows the J-K gap problem Pip flagged is already solved --
not by optimising either stage, but by choosing which path runs them:

- **CI path (the norm): J+K together = ~5 minutes for ALL platforms.**
  v0.13.1 measured: tag pushed 00:03:15Z -> Enhanced Release workflow green
  00:07:49Z (4m34s), assets on the release at 00:07:26Z (tag 10:02 -> assets
  10:07 Pip-local). K_ci ~= 0 because CI uploads from datacenter pipes.
  CAVEAT: this holds only once PR #919's packaging completeness holds at the
  next tag -- at v0.13.1 the CI batch was MISSING the Windows and Linux zips
  (see measured table), which is exactly what #919 fixed after the fact.
- **Local path (the FALLBACK for CI-down days, not the norm):**
  J_local ~5 min/platform (`tools/build_release.py`, stamp-verified).
  K_local at the measured 42.5 KB/s uplink = ~37 min per 90 MB zip, ~2h for
  3 platforms serialized. The local math stays documented here because the
  fallback must remain executable, but a 2-hour K is never the plan.

Consequence for backward planning: on the CI path, J+K is a rounding error
and the schedule is dominated by I (human gate) and L (sync confirmation).
On the fallback path, add ~2h of upload and start that much earlier.

## Measured v0.13.1 -- the first data row

Verbatim output of `python tools/release_timeline.py v0.13.1`
(run 2026-07-26):

```
Release timeline for v0.13.1 (published 2026-07-26 00:07:25Z)
| Stage                         | Start (UTC)          | End (UTC)            | Duration | Notes                                                     |
|-------------------------------|----------------------|----------------------|----------|-----------------------------------------------------------|
| G last B-quality submission   | n/a                  | n/a                  | n/a      | unmeasured                                                |
| H last A-quality submission   | n/a                  | n/a                  | n/a      | unmeasured                                                |
| I gate (proxy: last PR merge) | 2026-07-25 12:23:46Z | 2026-07-26 00:03:15Z | 11h39m   | PR #887 -> tag push                                       |
| J+K CI build+upload           | 2026-07-26 00:03:15Z | 2026-07-26 00:07:49Z | 4m34s    | Enhanced Release with Validation & Feeds: success         |
| K assets (CI batch)           | 2026-07-26 00:07:26Z | 2026-07-26 00:07:26Z | 1s       | 7 assets within grace of publish                          |
| K late asset (local fallback) | 2026-07-26 00:07:25Z | 2026-07-26 02:04:40Z | 1h57m    | PDoom-Windows-v0.13.1.zip (90.7 MB) after publish         |
| K late asset (local fallback) | 2026-07-26 00:07:25Z | 2026-07-26 02:42:39Z | 2h35m    | PDoom-Linux-v0.13.1.zip (83.8 MB) after publish           |
| L cross-repo sync             | 2026-07-26 00:56:23Z | 2026-07-26 03:16:37Z | 3h09m    | 6 failed run(s) before green; green was a MANUAL dispatch |
| M deploy + social process     | n/a                  | n/a                  | n/a      | unmeasured                                                |
| N league observed working     | n/a                  | n/a                  | n/a      | unmeasured                                                |
```

Reading notes on this row:

- The 11h39m I-duration includes an overnight gap (PR #887 merged mid-day,
  tag pushed next morning) -- human latency, not process latency. The model
  keeps it anyway: backward planning has to schedule around sleep too.
- The CI batch (7 assets in 1s) contained the macOS zips and the feed/manifest
  JSON but NOT the Windows or Linux zips -- those arrived +1h57m and +2h35m
  after publish via the local fallback path. This is the packaging
  incompleteness PR #919 closed; the next tag is the test of whether the CI
  path now carries all platforms.
- G, H, M, N are unmeasured because no naturally-occurring artifact records
  them yet. Expected; they gain artifacts as the process matures (M gets a
  post URL, N gets a league observation; G/H need the cutoffs to be declared
  somewhere timestamped, e.g. an issue comment).

## L is where releases die silently: the canonical example

The model's loud-failure requirement is not theoretical. On v0.13.1 the
`sync-game-version` workflow (game version -> website) failed **6 times with
zero signal to anyone**, and the website sat on the old version for ~3h until
a human noticed and dispatched it manually (green at 03:16:37Z, +3h09m after
publish). Two independent silent mechanisms stacked:

1. **The `published` trigger never fired at all.** The release was published
   by the CI workflow using its own `GITHUB_TOKEN`, and GitHub suppresses
   workflow events caused by `GITHUB_TOKEN` actions (recursion guard). Zero
   runs, zero red X, zero anything -- the purest silent failure: absence of
   evidence presented as nothing-to-see.
2. **An injection bug killed every run that DID fire.** The workflow
   interpolates the release body directly into a bash assignment
   (`RELEASE_BODY="${{ ... }}"`); a body containing quotes/backticks (ours
   had a markdown table and inline code) breaks the shell script at the
   "Extract Version Information" step. The later `edited`-event runs
   (00:56Z x2, 01:05Z, 01:10Z, 02:42Z, and one more at 03:19Z after the
   manual green) all died this way -- red in the Actions tab, but nothing
   watches the Actions tab.

Design rule this produces: **a stage is not done when its job ran; a stage is
done when its ARTIFACT is checked**. Sync is done when a green run exists
at-or-after publish AND the website shows the version -- checked, not
assumed. `docs/process/RELEASE_CHECKLIST.md` section 7.5 now carries a
per-stage verification line for exactly this.

## Antifragility / iterability

- Every release appends one timing row:
  `python tools/release_timeline.py <tag> --append` writes to
  `docs/process/release_timings.csv` (skips if the tag is already recorded);
  commit the CSV with the release wrap-up.
- The script mines only naturally-occurring artifacts (tag ref, workflow
  runs, asset `created_at`, PR merges) -- no extra bookkeeping to forget.
- Each failure that reaches this doc becomes a named example and usually a
  new checkable artifact, so the pipeline gets stronger from being hit
  (v0.13.1 contributed: the silent-sync example, the packaging-completeness
  caveat, and two mining bugs fixed in the script itself).
- Quality mapping: legibility = this doc + the ASCII table; loud
  success/failure = per-stage artifacts in the checklist; antifragility =
  failures convert to checks; iterability = the CSV tightens estimates every
  cycle.

## Cross-links

- Issue #917 -- deploy: robust cross-OS releases (Windows/Linux/macOS); this
  model is its measurement layer.
- PR #919 -- complete release zip packaging (#917 increment 1); the CI-path
  claim above is conditional on it holding at the next tag.
- `docs/process/RELEASE_CHECKLIST.md` -- section 7.5 stage-gate verification.
- `docs/process/BRANCHING_STRATEGY.md`, `docs/ROADMAP.md` -- release-train
  cadence the anchors sit inside.
- Planning intent: durations here feed Pip's energy/time planning -- work
  backward from the anchor commitment through N..G with measured numbers.
