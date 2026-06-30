<!--
status: accepted
date: 2026-06-26
deciders: Pip
-->

# ADR-0001: Retire the `develop` branch (trunk-based on `main`)

- **Status:** Accepted
- **Date:** 2026-06-26 (documented in `998d602`; retirement effective ~April 2026)
- **Deciders:** Pip

## Context

The project historically used a two-branch Git-flow model: feature work merged into `develop`, which
periodically merged into `main`. The last `develop` → `main` merge was `bf50f27` (2026-04-03,
"Develop merge: Risk system… (#523)").

For a solo maintainer working with AI coding agents, the two-branch model added ceremony without
payoff: it doubled the surface for CI configuration, created confusion about which branch was
authoritative, and several workflows fanned out triggers across both branches (and even a
"Nuclear: Reset Develop Branch" pipeline job).

## Decision

**Adopt a single-branch (trunk-based) model. `main` is the sole long-lived branch. All work happens on
short-lived `feature/*` and `fix/*` branches that target `main` via pull request.** The `develop`
branch is retired and should not be recreated.

This was implemented for CONTRIBUTING.md and `quality-checks.yml` in `998d602` (2026-06-26).

## Consequences

- Simpler mental model and CI surface; one source of truth.
- CI triggers should target `main` only. **Cleanup debt:** at decision time, several workflows and
  docs still referenced `develop` (`enhanced-cicd-pipeline.yml` jobs, `TESTING_STRATEGY.md`,
  `TESTING_QUALITY_GATES.md`, `DEVELOPERGUIDE.md`). These are tracked in the CI-consistency sweep.
- The `main` branch-protection model needs revisiting: a required *human* review is unsatisfiable for a
  solo maintainer (you cannot approve your own PR). Planned follow-up: switch the merge gate to
  **required status checks** once CI is trustworthy (separate ADR/decision when actioned).
- The "April 2026" retirement date is a reconstruction; the documentation lagged the practice by ~11
  weeks, which is itself part of the motivation for keeping ADRs.
