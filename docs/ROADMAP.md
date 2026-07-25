# P(Doom)1 roadmap

> Single source of truth for where the game is headed. Kept deliberately thin
> so it cannot rot: everything volatile is LINKED (milestones, the DQ index),
> not copied. The Monthly Themes table is the only hand-maintained forecast and
> is revisited at each release. Predecessor roadmaps (pygame-era alpha/beta plan,
> the 2025 Steam integration doc) are archived -- their status claims no
> longer described the project.
>
> Capacity basis for all dates: a solo developer at roughly 1-2 focused
> effort-days per week (Friday/Saturday project days plus agent-assisted
> weekday increments). Pins are sized to that cadence, not to burst weeks.

> **Nomenclature (2026-07-25):** precise definitions of Theme / Epoch / Seed and
> the version numbers live in [`RELEASE_NOMENCLATURE.md`](RELEASE_NOMENCLATURE.md).
> Ruling (**ADOPTED 2026-07-25**): the game evolves on a **MONTHLY** rhythm --
> each month is a named Theme = a minor-version bump = a forking Epoch. Quarterly
> planning is retired (it slowed the real ~feature-a-week pace). The old quarterly
> table is re-cast into the **Monthly Themes** table below; only the two Big
> Milestones (First Contact, Rivals & News) survive as coarse multi-month
> groupings. Rendered view: [`ROADMAP_RECAST_PROPOSAL.html`](ROADMAP_RECAST_PROPOSAL.html).

## Now (committed) -- GitHub milestones

The live execution roadmap is the milestone pages; issues move, the milestone
reflects it. This file does not duplicate their contents.

- [First Contact](https://github.com/PipFoweraker/pdoom1/milestone/12)
  (target: end Q3 2026). Public alpha readiness: first-contact UX fixes
  (SmartScreen metadata, commit-always-advances, first-launch help), onboarding
  phases 0-2, the share loop (copy result + seed), remote leaderboard enabled
  and hardened, monthly league v0.
- [Rivals & News](https://github.com/PipFoweraker/pdoom1/milestone/13)
  (target: end Q4 2026). Rivals become a strategic surface: intel panel,
  capability-race display, poaching rework (#648), News channel v1 (DQ-32),
  the voice re-skin of generic event content, tutorial mode, and the DQ-22
  aggro-midgame ADR workshop.

## Monthly Themes (the release spine)

Each month is a named Theme = a minor-version bump = a forking Epoch (first
Friday; see RELEASE_NOMENCLATURE.md). Theme names beyond v0.13 are PROVISIONAL.

| Version | Ships | Ladder | Theme | Headline |
|---|---|---|---|---|
| v0.13 | Jul 24 | L2 | Launch epoch (shipped) | hiring pipeline, onboarding cold-open, office visuals, league live, legibility + stability, v0.13.1 honesty pass |
| v0.14 | Aug 7 | L3 | Per-tick & People (prov.) | per-tick resolution + people & money cohesion (roles / salary / manager / payroll) |
| v0.15 | Sep 4 | L4 | (unnamed) | onboarding-as-mechanic + public-alpha hardening (leaderboard, install ping, bug reporter, test builds) |
| v0.16 | Oct 2 | L5 | Sightings (prov.) | rivals begin -- Developments / procedural presence; wider event pool from pdoom-data |
| v0.17 | Nov 6 | L6 | The World Shoots Back (prov.) | News feedline + rival midgame pressure (poaching, litigation, funding attacks); DQ-22 aggro built |
| v0.18 | Dec 4 | L7 | (unnamed) | rival direct confrontation + News v1 + voice re-skin of event content |

Further out (unscheduled, folded from the retired quarterly pins): player-facing
Liability Ledger UI (#528); content-pool ladder v1 (DQ-33) + monthly world-diff
metabolism (ADR-0016); damper economy (DQ-23); then the Beta / Steam "coming
soon" beat -- Steam page + wishlists, press kit, character creation (DQ-19),
balance calibration (DQ-8/13), phase vocabulary (DQ-28).

Confidence: v0.14-v0.15 grounded in existing design; v0.16+ is direction to
steer, not commitment (WS-3 will reshape). The two Big Milestones (First Contact,
Rivals & News) are the coarse groupings that make the shape legible to funders.

## Cadence ruling (2026-07-21)

League and content operations run on a MONTHLY cycle: balance/quality patches,
curated world-diffs, and pool updates are monthly artifacts (matching the
game's own month cadence and the sustainable ops budget of ADR-0016). Weekly
output is limited to cheaply generated artifacts (a challenge seed or simple
scenario), never curation or balance. Rollover validation
(pdoom1-website#126) applies to the monthly boundary.

RELEASES ride the same train: whatever is merged and green ships as a point
release each league month (one per monthly Theme), with notes, alongside the
world-update. The two Big Milestones (First Contact, Rivals & News) complete
ACROSS several monthly Themes -- they are named arcs, not the release cadence.

## Decision owed: public-alpha distribution channel (2026-07-21)

The channel for the public alpha is NOT yet decided; earlier references to
itch.io were a recommendation that leaked into public copy, now retracted.
Options on the table: (a) website direct download -- pdoom1.com stays the
hub, works today; (b) itch.io page -- free hosting including HTML5 web
builds plus platform discovery, at the cost of one more outward surface;
(c) self-hosted web build -- Godot web export on own hosting (needs
COOP/COEP headers for threading; small but real ops work).
docs/strategy/HOSTING_AND_RELEASE.md argues for (b); Pip's instinct is
website -> Steam with web-pivot optionality held in reserve. Decide before
the public alpha ships (the First Contact milestone). The Themes above are
channel-neutral.

## Next -- the release ladder

Private alpha (friends and family, v0.13 -- HERE) -> public alpha (free;
channel per the open decision above) -> Steam "coming soon" page while in
beta -> 1.0. Rationale and hosting details:
docs/strategy/HOSTING_AND_RELEASE.md.

## Later -- the design horizon

Not listed here on purpose. The design question register is
[docs/game-design/DQ_INDEX.md](game-design/DQ_INDEX.md) (generated; 32 open),
sourced from WORKSHOP_2_BACKLOG.md. Design advances through workshop beats
(next candidates: DQ-19 + DQ-23; DQ-22 + DQ-31 + DQ-32 as one conversation).
Longer-horizon intents listed above: content-pool ladder (DQ-33),
league metabolism (ADR-0016). Jira adoption is deliberately deferred until
the project is funded and housed in an org, at which point it follows that
org's work management.

## Cross-repo

The website (pdoom1-website) carries the player-facing / funder-facing projection
of this roadmap plus the funding-ask surface (website issues #78-#87: donor page,
budget, press kit, metrics). The data lake (pdoom-data) feeds the content-pool ladder.

**Upward-comms protocol (roadmap -> website).** Per the source/publisher contract
(`docs/copy/README.md`): `pdoom1` is SOURCE, `pdoom1-website` PULLS. This
`ROADMAP.md` is the canonical roadmap; the website's `public/docs/roadmap.md` is a
PROJECTION it derives (audience-shaped, funder-legible), never the source of truth.
When the roadmap changes materially, the pdoom1-website agent PULLS this file +
`RELEASE_NOMENCLATURE.md` and re-projects. The signal is the roadmap commit; for a
big re-cast, a cross-repo issue is filed in pdoom1-website. Prior sync threads:
#723 / #724 / #545.
