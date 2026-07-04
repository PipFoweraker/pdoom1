# Implementation Kickoff — Workshop #1 build plan

> **How to use:** open a fresh Claude Code session on **Opus** (`/model opus`; fast mode
> is fine — this is specified execution, not design). Point it at ONE workstream section
> below plus the ADRs that section names. Each section is written to be self-contained:
> the implementing session needs no transcript of the design workshop. Design questions
> that surface during implementation get *parked in the workstream's "questions for the
> next design session" list*, not answered ad hoc — mechanics decisions belong to Fable
> workshops with Pip.
>
> Source of truth: `docs/game-design/decisions/ADR-0001..0008`. If code and ADR
> conflict, the ADR wins; if the ADR is genuinely wrong, stop and flag.

## Sequencing (binding)

```
WS-A Scoring rewire      ──┐  (parallel-safe side lanes)
WS-B Replay artifact     ──┤
WS-C Seed schedules      ──┘
WS-1 Liability Ledger    ── first of the big three
WS-2 Situational Awareness ── second (uses WS-1's governance writes)
WS-3 Alliances           ── third, strictly after WS-1 + WS-2 (built FROM their parts)
```

WS-A/B/C touch existing systems and can proceed anytime. WS-1 → WS-2 → WS-3 is a hard
order: alliances are assembled from ledger + SA parts (ADR-0007), and **the vote screen
must not be built early because it is dramatic** — a vote UI without a working ledger is
theater.

---

## WS-A — Scoring rewire (ADR-0002)

Delete the composite formula everywhere; implement lexicographic scoring.

- Remove `calculate_final_score` composite (incl. victory bonus) from
  `godot/scripts/ui/game_over_screen.gd` and `_calculate_score` from
  `godot/scripts/core/baseline_simulator.gd`.
- Implement per-turn accrual **in engine core** (near `game_state.gd` / turn end): each
  survived turn, `doom_integral += 100 - doom`. Score = `(turns_survived,
  doom_integral)` compared lexicographically. Display "Turn 14 · 862".
- Post-mortem reveal only — no in-run score UI.
- `godot/scripts/leaderboard.gd`: key boards by `(seed, game_version)` (currently
  per-seed only).
- Cross-repo: `pdoom1-website/scripts/verification_logic.py` formula gets deleted, not
  synced (separate PR in that repo; flag, don't do, if session is scoped to pdoom1).
- Tests: update `test_scoring_formula.gd`; determinism tests must show identical
  `(turns, integral)` for identical seed+inputs.
- **Done when:** no formula exists outside engine core; headless replay reproduces the
  score; no stock (money/papers/staff) affects score.

## WS-B — Replay artifact (ADR-0006)

Make the input-string replay the canonical run artifact.

1. Wire `VerificationTracker.record_action` into the live action pipeline (currently
   tests-only) — every player action, event response included.
2. Serialize: seed + game_version + ordered action string, starting from the pygame-era
   compact format in `docs/technical/COMMAND_STRING_CONTROLLER.md` (adapt, don't
   worship).
3. Import-and-replay: load a string, re-simulate headless, compare final hash and
   `(turns, integral)`.
4. Submission: export artifact at game-over; wire to the static-JSON board path
   (`pdoom1-website` Netlify exports). Postgres server stays parked.
- **Done when:** a run played by hand exports a string that, replayed headless,
  reproduces hash and score; a tampered string fails.

## WS-C — Seed schedules + vetting (ADR-0005)

- Extend seed definition to **RNG seed + event schedule** (scheduled causes: e.g.
  `{turn: 9, cause: "rival_funding_wave", target: "lab_2", magnitude: ...}`). Causes act
  on sim inputs only — grep-able invariant: nothing in the schedule path writes `doom`
  directly.
- Vetting harness on `baseline_simulator.gd`: run candidate seeds headless (no-action
  baseline + 1-2 crude heuristic bots), reject seeds outside a playability envelope
  (dead-by-turn-N, or doom never threatens). Envelope constants are config, not code.
- Later (not this WS): pdoom-data feed for schedule content.
- **Done when:** two seeds with identical RNG but different schedules produce different,
  deterministic, replay-verifiable runs; the vetting tool classifies a batch of seeds.

## WS-1 — Liability Ledger (ADR-0003) — the flagship

Two-sided ledger; no new player-facing currency; reads/writes money, reputation,
governance, AP, doom only.

- Entry: source, currency, fuse, interest profile, `secret` flag, side
  (payable/receivable), counterparty (for receivables).
- Turn integration: fuses tick, interest compounds, due entries bill their currency.
  Compounding interest is the **mortality guarantee** (ADR-0002) — verify no immortal
  runs in headless soak tests.
- Content, first wave: loans (money now, service later); funding-with-strings
  (money now, obligation entry); desperation levers (the payroll-coinflip family —
  visible resource now, corrosive secret liability later); staff riders (hires create
  small liability entries; departures can convert them to secret ones).
- Exposure events: rival actions/scheduled causes can expose `secret` entries →
  reputation/governance damage or a blackmail *offer* (a new, worse entry — the chain
  continues).
- Heterogeneity check (design invariant): fuses vary, currencies vary, some entries
  repayable, some only transformable. A lean-ledger run must be viable at tempo cost.
- **Done when:** a headless bot that takes every desperation lever dies spectacularly of
  its own ledger; a lean bot survives fewer turns but cleanly; both runs' deaths are
  traceable to specific entries in the post-mortem.

## WS-2 — Situational Awareness (ADR-0004, amending ADR-0001)

- Per-source visibility flags on already-simulated state (simulate everything, gate the
  view). Generalize the existing discovered/undiscovered opponent mechanic.
- Channels with provenance: espionage / alliance / media / research — different costs,
  different slices, different side effects (espionage writes governance down; alliance
  creates ledger obligations — stub until WS-3; media cheap+noisy).
- Lead-time rule: as any doom source approaches lethality, it becomes visible free;
  purchases move the reveal earlier.
- CRT viewports: bought sight unlocks screens (the aesthetic IS the mechanic).
- Telemetry hook for the decision-flip acceptance test: log action-before/after-reveal
  so playtests can measure flip rate per SA feature.
- **Done when:** a no-SA run and max-SA run of the same seed show the same sim, different
  screens; every SA purchase names the decision it opens; flip-rate telemetry emits.

## WS-3 — Alliances (ADR-0007) — after WS-1 + WS-2 only

- Treaty object = mutual ledger entries (both sides) + mutual sight channel.
- Votes as scheduled causes; whip loop: spend money/reputation/favors to create pledge
  receivables; wavering computed from counterparty state (financial pressure, rival
  counter-offers) — never scripted; defection = exposure-in-reverse.
- No global influence stat — receivables are per-actor.
- **Done when:** a vote can be won by whipping, lost by a computed defection the player
  had (purchasable) lead time on, and every favor spent is visible in the ledger.

---

## Standing constraints (all workstreams)

- Pure GDScript; Python 3.11 floor for tooling; fresh worktrees need a Godot `--import`
  pass before GUT runs.
- Determinism is sacred: no unseeded RNG, no wall-clock in sim. Every feature must
  survive replay verification (WS-B).
- Rams #10 gate: if an implementation wants a new resource, panel, or parallel economy,
  stop and check the ADR — the design almost certainly folds it into an existing system.
- Park emergent design questions per-workstream for the next Fable session; don't
  freelance mechanics.

## Open design questions (owned by next Fable workshop, not by builders)

- Wall-clock pacing targets (median death / deep run) — after first playtests
  (ADR-0008).
- Governance stat's player-facing design (it's currently a name, not a system).
- Rival-lab naming pass; SA channel in-fiction names; epitaph set.
- Season/scenario design cadence once WS-C exists.
