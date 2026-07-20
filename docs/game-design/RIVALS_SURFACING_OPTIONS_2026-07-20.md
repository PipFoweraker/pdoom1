# Rivals / frontier labs: status + surfacing options -- 2026-07-20

> Status audit + lossless option list for making rival labs visible and
> consequential. Produced by an agent status-map pass; options tiered by effort
> for triage. Effort: T = under an hour, S = half-day, M = 1-3 days, L = week+.
> Core finding: the SIMULATION side of rivals is largely built; the PLAYER-FACING
> side is absent. Rendering already-paid simulation beats building new mechanics
> on value-per-effort almost everywhere below.

## 1. Status map (verified to file:line)

| Aspect | Status | Evidence |
|---|---|---|
| RivalLab data model | Built | rivals.gd:20-93 (progress, funding, aggression, visibility enum, discovery fields) |
| Roster | Built, hardcoded | rivals.gd:95-122 -- DeepSafety (KNOWN), CapabiliCorp (KNOWN), StealthAI (RUMORED, threshold 45). No data file |
| Discovery/visibility (#474) | Built but narrow | rivals.gd:124-144; only StealthAI is ever hidden; checked each turn (turn_manager.gd:511-517) |
| Per-turn rival actions | Built | rivals.gd:146-200; 1-3 actions/turn scaling with funding (turn_manager.gd:495-509) |
| Doom integration (ADR-0015) | Built | capability_progress feeds state.frontier_capability -> overhang stream (doom_system.gd:214-220); direct doom writes retired (pinned by test_doom_system.gd:117-123) |
| Panic from reckless rival moves | Wired but ZEROED | rivals.panic_per_capability_action defaults 0.0 (data/balance/defaults.json:109-110) -- code path exists, never fires |
| Poaching | Partial, decoupled | rival_poaching flavor event (core_events.json:266-292) removes researchers via generic text; NOT connected to any RivalLab object; rate uncalibrated (open #648: target ~1/year vs 0.06/turn) |
| Player -> rival actions | One lever | Corporate Espionage (strategic.json:15-20, actions.gd:577-598): 70% delays top rival, 30% backfires to panic+rep |
| Scheduled causes | Built + tested | seed_schedule.gd:40-52 rival_funding_wave / rival_aggression_shift (ADR-0005) |
| Save/load | Built | game_state.gd:869-873, 1166-1171 full round-trip |
| Player-facing UI | ABSENT | Only debug overlay + F3 readout. doom_breakdown.gd "rivals" label is dead post-ADR-0015 |
| Debug overlay | Stale/buggy | debug_overlay.gd:194-196 reads nonexistent fields (capabilities/money vs capability_progress/funding) |
| Tests | Thin, indirect | No test_rivals.gd; coverage via phase5/doom/seed-schedule tests; one stale comment in test_phase5_features.gd |

Design intent with zero code: DQ-22 aggro-threshold midgame (rivals targeting
the player: litigation, funding cuts, rep attacks, hiring raids); #474 Early
Discovery Rewards (collaboration, recruit-their-staff). The backlog's own DQ-12
line matches this audit: "rival still narratively invisible despite mechanical
doom pressure." WORLD_AND_LORE.md's Antagonist_Lab fiction does not match the
actual roster names (naming pass owed, flagged in-doc).

## 2. Option list (lossless, tiered by effort)

### Tier T -- trivial hygiene
| # | Idea | Effort | Payoff |
|---|---|---|---|
| 1 | Fix debug_overlay.gd:194-196 stale field names | T | Dev-only correctness |
| 2 | Un-zero rivals.panic_per_capability_action + balance sweep | T+sweep | Reckless rival moves finally feed the panic stream |
| 3 | Remove/repoint dead "rivals" label in doom_breakdown.gd | T | Hygiene |
| 4 | Fix stale doc-comment in test_phase5_features.gd | T | Stops misleading future agents |
| 5 | Roster naming pass to match lore (save-compat: ids serialized; fine mid-alpha) | S | Labs become memorable; flavor coherence |

### Tier S -- half-day each; this tier kills "narratively invisible"
| # | Idea | Effort | Payoff |
|---|---|---|---|
| 6 | Route rival actions into the player feed ("CapabiliCorp closes a $40M round"). process_rival_turn() already returns messages; currently discarded. Classify via event_tiers (feed-tier, not window-spam) | S | HIGHEST value/effort in this list. Directly closes DQ-12 |
| 7 | "Rivals this month" section in month review (uses get_rival_summary()) | S | Rivals enter the player's mental model at the reflect moment |
| 8 | Discovery reveal moment: StealthAI surfacing fires a visible event, not a silent flip | S | Makes built machinery felt once per run |
| 9 | Attribute overhang stream by lab in doom breakdown ("overhang: 60% CapabiliCorp"); per-rival slices already in state.frontier_capability | S-M | Ties rivals into the legibility thesis |
| 10 | Name the killer lab on the game-over screen when overhang got you | S | Serves "interested in how they lost"; pairs with wiring DeathAttribution.chain_summary() |

### Tier M -- 1-3 days each
| # | Idea | Effort | Payoff |
|---|---|---|---|
| 11 | Rivals/Intel panel: visibility-tiered lab list (rumored = name only, known = full). Pure UI; sim data exists. Design choice: standalone screen vs side panel | M | Anchor surface; prerequisite for acting on rivals |
| 12 | Capability-race chart: per-lab frontier capability vs your safety absorption over time. Check first whether per-turn history snapshots exist; may need recording | M | The thesis in one picture; screenshot-worthy (share-loop adjacent) |
| 13 | Data-driven roster -> godot/data/rivals.json | M | Scenarios/seeds vary the roster; matches data-over-hardcode convention |
| 14 | Poaching rework: attribute to an actual lab (aggression x funding), calibrate ~1/year (#648), counter-offer window | M | The one rival->player touch becomes legible and fair |
| 15 | "Investigate lab" action: RUMORED -> DISCOVERED -> KNOWN, reveals real vs estimated stats (estimated_* fields exist unused) | M | Revives 2/3-dead visibility machinery; gives the panel a verb |
| 16 | Lab logos/portraits via the pixellab pipeline | M | Visual identity; labs stop being text strings |
| 17 | Media-system headlines on rival milestones (media_story.gd/media_system.gd exist to hang this on) | M | World-texture; the race feels alive |

### Tier L -- week+; design pass BEFORE code
| # | Idea | Effort | Payoff |
|---|---|---|---|
| 18 | DQ-22 aggro-threshold midgame: rivals target YOU (litigation, funding interference, rep attacks, hiring raids) | L | Highest long-term payoff -- defines the midgame. Write the ADR first; do not let an agent freestyle it |
| 19 | #474 Early Discovery Rewards: collaboration offers, recruit-from-their-staff | L | Content depth; promised in the closed issue, never built |
| 20 | Rival lifecycle: collapse, merger, new entrants via seed schedule (ADR-0005 plumbing supports mutation) | L | Replayability; runs stop feeling roster-static |
| 21 | Coordination layer: safety pacts, mutual-slowdown with defection risk | L-XL | Thematically the heart of AI-safety strategy; workshop material |

## 3. Suggested sequence (if wanted)

6 -> 7 -> 9 -> 10 -> 11 -> 8 -> 14: roughly a week of lane-work that converts
the entire already-built simulation into a visible game before any new mechanic
is written. Item 18 is the one to SCHEDULE (ADR workshop), not start. Items 2
and 5 ride along free with whichever lane touches those files.
