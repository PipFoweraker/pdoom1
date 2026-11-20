# RELEASING -- P(Doom)1 release & branch protocol

**Status:** ACTIVE PROTOCOL (ratified 2026-07-25, issue #775; made MECHANICAL
2026-10-26, issues #1269 and #1299). Hold to this -- and since 2026-10-26 the
release workflow holds you to it whether you remember or not.
Companion: `docs/RELEASE_NOMENCLATURE.md` (the clocks + version numbers);
`docs/adr/0001-retire-develop-branch.md` (why there is no `develop`).
Rulings: `docs/rulings/DECISIONS_2026-10-26_return.md` items 3 and 5.

## The model (one screen)

- **`main` is trunk.** All development velocity and every impulse lands on `main`
  via PR. `main` IS the stash -- there is NO `develop` branch (retired by
  ADR-0001; do not recreate it).
- **Each monthly epoch, cut a release branch.** At the epoch (1st Friday --
  see RELEASE_NOMENCLATURE.md), cut `release/v0.X` from the epoch commit and tag
  `v0.X.0`. That branch is the stable line for the whole month.
- **Ship from the release branch, never from churny `main`.** Builds and tags
  come off `release/v0.X`; `main` keeps absorbing the next epoch's work.
- **Hotpatches: `main` first, then cherry-pick.** A fix lands on `main`, then is
  cherry-picked to `release/v0.X` ONLY if it meets the hotpatch criteria below.
  Point releases (`v0.X.Y`) are tagged off the release branch.
- **The train runs forward only.** `main` -> next release cut. NEVER merge a
  release branch back into `main` (cherry-pick individual fixes if `main` needs
  them too).
- **Only Pip pushes release tags.** GitHub ruleset 21258734 restricts creating,
  deleting and moving `refs/tags/v*` to the Admin role, and Pip is the only
  admin (#1290). Agents prepare the branch and say "ready to tag"; they never tag.

## What is ENFORCED (and by what)

Every claim in this section is a gate that fails a run, not a convention.

| Rule | Enforced by | When |
|---|---|---|
| Only Pip creates / moves / deletes `v*` tags | ruleset 21258734 | on push of the tag |
| Tag name is `v<major>.<minor>.<patch>[-pre]` (RB001) | `tools/check_release_branch.py` | preflight job, before any build |
| `version.txt` at the tagged commit equals the tag minus `v` (RB002) | `tools/check_release_branch.py` | preflight |
| `release/v<major>.<minor>` exists **on origin** -- a local-only branch does not count (RB003) | `tools/check_release_branch.py` | preflight |
| The tagged commit is reachable from that branch (RB004) -- so `v0.14.5` must be on `release/v0.14` | `tools/check_release_branch.py` | preflight |
| A publish builds exactly the tagged commit (RB005) | `tools/check_release_branch.py --require-tag` | preflight |
| `CHANGELOG.md` has a `## [<version>]` section heading | preflight step `Check CHANGELOG updated` | preflight |
| CHANGELOG structure + this version's citations (RN001-RN005) | `scripts/check_release_notes.py` | preflight, and again on the assembled body before publish |
| `godot/project.godot` `config/version` equals the tag | preflight step `Check version in project.godot` | preflight |
| Tests + guards run on the release branch itself | `godot-tests.yml` and `guards.yml` trigger on push/PR to `release/**` | every push to a release branch |

**The preflight job is a blocking gate.** It is the first job of
`.github/workflows/enhanced-release.yml`, and `validate-data`, `build-godot`
and `create-github-release` all `needs:` it. If it goes red, nothing builds and
nothing publishes, and it files a `[!] Release preflight failed: <tag> -- NOT
published` issue. It has **no bypass input** -- not `skip_validation`, not
anything. The old standalone `pre-release-checks.yml` (which raced the release
and could not stop it -- v0.14.4 published while it was red, #1325) is gone;
its checks moved into preflight unchanged.

**The one emergency input that remains:** `skip_validation` on a manual
dispatch. It skips exactly one thing -- a failing historical-data validation
job (`scripts/validate_historical_data.py`) -- and it is loud: a `::warning::`
annotation naming who dispatched it, a job-summary banner, and
`validation_passed=false` in the published manifest. It does not skip preflight.

**Exit 2 means COULD NOT MEASURE.** The branch guard refuses to answer on a
shallow clone (an ancestor can look unreachable there); it exits 2 and the
release stops. The workflow checks out with `fetch-depth: 0`, so this should
only ever be seen locally.

## Hotpatch criteria (what may cherry-pick to a LIVE release)

A fix earns a hotpatch to `release/v0.X` only if it is one of:

1. **Crash / hang** -- the build crashes or locks up.
2. **Data-loss / corruption** -- saves, leaderboard, or replay integrity at risk.
3. **Blocking-UX** -- a player cannot progress (soft-lock, dead-end, unusable
   control).
4. **First-impression integrity** -- the shipped build visibly lies about itself
   on the opening screens (a stale "Prototype" subtitle; a button that charges
   money and does nothing). Launch-facing only.

Everything else -- new mechanics, refactors, polish, balance -- waits for the
next monthly epoch on `main`. **If in doubt, it waits.** A hotpatch is an
exception, not a convenience. (The criteria are judgement; the guards above do
not check them.)

## Version discipline

- `version.txt` on `release/v0.X` = the release version (e.g. `0.14.5`);
  `ladder_version.txt` is fixed for the epoch's life.
- On `main`, `version.txt` carries the in-development number; the epoch cut is
  what stamps the new minor + bumps the ladder (RELEASE_NOMENCLATURE.md).
- `python3 tools/sync_version.py --check` still gates both, on every branch.

## The commands

All of these assume a clean checkout and a fresh fetch. On the Windows machine
use `python` for `python3`.

### 1. Cut `release/v0.X` at the epoch (Pip, or an agent up to the push)

```bash
git fetch origin --tags
git switch -c release/v0.15 <epoch-commit-on-main>   # the commit whose version.txt reads 0.15.0
git push origin release/v0.15                         # CI: godot-tests + guards run on the branch
```

The epoch commit itself carries the `0.15.0` version stamp and the ladder bump
(made on `main` via PR as today). For a point-release line opened after the
fact, cut from the previous tag instead: `git switch -c release/v0.14 v0.14.4`.

### 2. Cherry-pick a hotpatch (fix already merged to `main`)

```bash
git switch release/v0.15 && git pull --ff-only
git cherry-pick -x <sha-on-main>       # -x records "(cherry picked from commit ...)"
git push origin release/v0.15          # or push a branch and open a PR against release/v0.15
```

Squash-merged PRs are one commit on `main`, so one SHA per fix. If a generated
index conflicts (`docs/rulings/RULINGS.md`, `docs/releases/RELEASE_HORIZON.md`,
...), do not hand-merge it: regenerate it on the release branch, `git add` it,
`git cherry-pick --continue`.

### 3. Bump the version on the release branch

```bash
echo 0.15.1 > version.txt
python3 tools/sync_version.py          # stamps game_config.gd / project.godot / export_presets.cfg / welcome.tscn
# add a '## [0.15.1]' section to CHANGELOG.md, and the in-game patch notes
python3 scripts/check_release_notes.py --changelog-structure
python3 scripts/check_release_notes.py --version 0.15.1
git add version.txt godot/autoload/game_config.gd godot/project.godot godot/export_presets.cfg godot/scenes/welcome.tscn CHANGELOG.md godot/data/patch_notes.json
git commit -m "release: 0.15.1"
git push origin release/v0.15
```

(Or prepare the bump as a PR on `main` and cherry-pick its squash commit, which
keeps `main`'s CHANGELOG in step.)

### 4. Dry-run the gate, then tag (tagging is Pip only)

```bash
# Dry run on GitHub: preflight only, builds and publishes nothing (preflight_only defaults to true)
gh workflow run enhanced-release.yml --ref release/v0.15 -f version=v0.15.1
# ...or the branch guard locally, against what origin has:
git fetch origin && python3 tools/check_release_branch.py --tag v0.15.1

# PIP ONLY -- the ruleset refuses anyone else:
git tag -a v0.15.1 -m "P(Doom) v0.15.1" origin/release/v0.15
GIT_TERMINAL_PROMPT=0 git push origin v0.15.1
```

The tag push starts `enhanced-release.yml`: preflight, then data validation,
builds, feeds, manifest, the release-body guard, publish, URL verification.

**If preflight is red after tagging:** nothing was published. Fix it on the
release branch and tag the next patch version (`v0.15.2`). Moving a published
tag is possible for an admin but is a last resort -- anyone who fetched it keeps
the old one.

**Re-running a publish by hand** (e.g. a flaky build after a green preflight):
dispatch ON the tag, so the guard can prove the build is the tagged commit:
`gh workflow run enhanced-release.yml --ref v0.15.1 -f version=v0.15.1 -f preflight_only=false`.
A publish dispatched from a branch is refused (RB005) when the tag points
elsewhere, and when the tag does not exist yet.

## Worked example -- v0.13 (historical, and NOT what happened)

This section used to describe `release/v0.13` being cut from `v0.13.0` and
`v0.13.1` being cherry-picked onto it. That was the intent. In fact no
`release/*` branch ever existed on origin, and v0.13.0 through v0.14.4 were all
tagged from `main` (#1269). It is kept as the record of why the guards above
exist: a protocol that has never been run is a hypothesis, and one enforced
only by prose was not followed once. The first release cut under the enforced
model is intended to be v0.14.5, on `release/v0.14` cut from `v0.14.4`.
