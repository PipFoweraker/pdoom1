# P(Doom)1 roadmap

> Single source of truth for where the game is headed. Kept deliberately thin
> so it cannot rot: everything volatile is LINKED (milestones, the DQ index),
> not copied. The quarterly pins are the only hand-maintained forecast and are
> revisited at each release. Predecessor roadmaps (pygame-era alpha/beta plan,
> the 2025 Steam integration doc) are archived -- their status claims no
> longer described the project.
>
> Capacity basis for all dates: a solo developer at roughly 1-2 focused
> effort-days per week (Friday/Saturday project days plus agent-assisted
> weekday increments). Pins are sized to that cadence, not to burst weeks.

## Now (committed) -- GitHub milestones

The live execution roadmap is the milestone pages; issues move, the milestone
reflects it. This file does not duplicate their contents.

- [v0.12 -- First Contact](https://github.com/PipFoweraker/pdoom1/milestone/12)
  (target: end Q3 2026). Public itch alpha readiness: first-contact UX fixes
  (SmartScreen metadata, commit-always-advances, first-launch help), onboarding
  phases 0-2, the share loop (copy result + seed), remote leaderboard enabled
  and hardened, monthly league v0.
- [v0.13 -- Rivals and News](https://github.com/PipFoweraker/pdoom1/milestone/13)
  (target: end Q4 2026). Rivals become a strategic surface: intel panel,
  capability-race display, poaching rework (#648), News channel v1 (DQ-32),
  the voice re-skin of generic event content, tutorial mode, and the DQ-22
  aggro-midgame ADR workshop.

## Quarterly pins to v0.15 (indicative beyond v0.13)

| Quarter | Version | Theme | Headline contents |
|---|---|---|---|
| Q3 2026 | v0.12 | First Contact | Public itch alpha live; onboarding; share loop; leaderboard on; monthly league v0; grant applications out |
| Q4 2026 | v0.13 | Rivals and News | Rival surfaces + News feedline; voice content pass; tutorial; DQ-22 designed |
| Q1 2027 | v0.14 | The World Shoots Back | DQ-22 aggro midgame built; player-facing Liability Ledger UI (#528); content-pool ladder v1 (DQ-33) + monthly world-diff metabolism (ADR-0016); damper economy beat (DQ-23) |
| Q2 2027 | v0.15 | Beta / Steam Coming Soon | Steam page + wishlists; press kit; character creation (DQ-19); balance calibration pass (DQ-8/13); phase vocabulary surfaced (DQ-28) |

Confidence: v0.12 committed, v0.13 planned, v0.14-v0.15 indicative pins --
they exist to be steered, and to make the shape of the ask legible to funders.

## Cadence ruling (2026-07-21)

League and content operations run on a MONTHLY cycle: balance/quality patches,
curated world-diffs, and pool updates are monthly artifacts (matching the
game's own month cadence and the sustainable ops budget of ADR-0016). Weekly
output is limited to cheaply generated artifacts (a challenge seed or simple
scenario), never curation or balance. Rollover validation
(pdoom1-website#126) applies to the monthly boundary.

## Next -- the release ladder

Private alpha (friends and family, v0.11 -- HERE) -> public itch.io alpha
(free, labelled alpha) -> Steam "coming soon" page while in beta -> 1.0.
Rationale and hosting details: docs/strategy/HOSTING_AND_RELEASE.md.

## Later -- the design horizon

Not listed here on purpose. The design question register is
[docs/game-design/DQ_INDEX.md](game-design/DQ_INDEX.md) (generated; 27 open),
sourced from WORKSHOP_2_BACKLOG.md. Design advances through workshop beats
(next candidates: DQ-19 + DQ-23; DQ-22 + DQ-31 + DQ-32 as one conversation).
Longer-horizon intents that have pins above: content-pool ladder (DQ-33),
league metabolism (ADR-0016). Jira adoption is deliberately deferred until
the project is funded and housed in an org, at which point it follows that
org's work management.

## Cross-repo

The website (pdoom1-website) carries the player-facing projection of this
roadmap (public/docs/roadmap.md, synced -- see issues #723/#724/#545) plus
the funding-ask surface (website issues #78-#87: donor page, budget, press
kit, metrics). The data lake (pdoom-data) feeds the content-pool ladder.
