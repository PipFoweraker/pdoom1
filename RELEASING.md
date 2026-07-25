# RELEASING -- P(Doom)1 release & branch protocol

**Status:** ACTIVE PROTOCOL (ratified 2026-07-25, issue #775). Hold to this.
Companion: `docs/RELEASE_NOMENCLATURE.md` (the clocks + version numbers);
`docs/adr/0001-retire-develop-branch.md` (why there is no `develop`).

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
exception, not a convenience.

## Version discipline

- `version.txt` on `release/v0.X` = the release version (e.g. `0.13.1`);
  `ladder_version.txt` is fixed for the epoch's life.
- On `main`, `version.txt` carries the in-development number; the epoch cut is
  what stamps the new minor + bumps the ladder (RELEASE_NOMENCLATURE.md).
- `python tools/sync_version.py --check` still gates both, on every branch.

## How CI ships it

`.github/workflows/enhanced-release.yml` triggers on **tag push** (+ manual
dispatch). So the release flow is: cherry-pick the fix onto `release/v0.X`, bump
`version.txt`, tag `v0.X.Y`, push the tag -> the workflow builds and publishes.
No branch-trigger plumbing needed.

## Worked example -- v0.13

- `release/v0.13` was cut from tag `v0.13.0` (the pristine epoch baseline -- it
  EXCLUDES the CARVE 1/2 `main_ui` refactors, which are v0.14 work living on
  `main`).
- The **v0.13.1** honesty pass (subtitle, dead-button removal, quirks CI fix,
  README refresh) meets criterion 4 (first-impression integrity) -> cherry-pick
  onto `release/v0.13`, bump to `0.13.1`, tag `v0.13.1`, build.
- CARVE 1/2, per-tick, people&money: they stay on `main` for the v0.14 epoch and
  never touch `release/v0.13`.
