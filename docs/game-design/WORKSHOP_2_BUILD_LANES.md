# Workshop #2 → Build Lanes (implementation instructions)

> **How to use:** each lane below is a self-contained brief for a non-Fable
> implementation session (or a series of them). Lanes cite their ADRs — **the ADR is
> the authority; this doc is the work order.** Run lanes in dependency order; L6/L7/L8
> are parallel-safe from day one. Do not freelance design: anything not covered by a
> cited ADR goes to `WORKSHOP_2_BACKLOG.md` as a DQ, not into code.
>
> Produced by Fable workshop #2 (2026-07-12). ADR-0009..0014, DESIGN_PHILOSOPHY,
> WORLD_AND_LORE updated same session.

## The falsifiable claim (sweep gates)

The whole workshop asserts three measurable things. Bake them in as acceptance gates:

- **G1 (after L1+L4):** in a 20-seed × N-policy sweep, **no constant policy dominates**
  (safety-spam must not be the best line), and greedy policies produce **>0
  ledger-attributed deaths** (root-cause attribution per EE-8, not surface cause).
- **G2 (after L3):** publish-and-socialize policies **beat basement-spam** on median
  survival.
- **G3 (after L5):** a philanthropy-only opening is **viable but slow**; trade-heavy
  openings (equity/agenda/capabilities) are faster and bill later — distinct viable
  openings, none dominant.

## Lane order

```
L6 instrumentation ──┐            (start now, parallel)
L7 save/load ────────┤            (start now, parallel)
L8 achievements ─────┤            (start now, parallel, observer-only)
L1 turn engine ──────┼─► L2 effort economy ─► L3 adoption+conferences
                     └─► L4 events+ledger ──► L5 pricing engine
```

## L1 · Turn engine (ADR-0009) — CRITICAL PATH

- Month = the turn: plan phase (allocate staff/founder-hours, set reserve, queue
  strategic actions) → day-by-day resolution (speed control + auto-pause-on-window) →
  month review screen.
- **Guard rule: no routine decision on the day tick.** Days are physics and comedy.
- Response-window framework: event fires → window with costed menu
  [HANDLE-reserve / HANDLE-cannibalize / DEFER / IGNORE]. Menu semantics per ADR-0012
  (L4 wires the ledger side; L1 builds the window plumbing).
- Reserve: explicit at plan time, evaporates crisply at month end. Banking: delete.
- Strategic actions get durations (fundraising money lands later — ADR-0012).
- Re-denominate: salaries monthly; loans %/month placeholder until L5; event pacing
  per month.
- Replay artifact: schema bump — record `(event_id, window, choice, payment_source)`;
  batch the schedule-provenance fix (DQ-6) into the same version bump.
- Score internals unchanged (lexicographic days-survived · doom-integral); **display
  badge = exact death date** ("I made it to March 2034").
- Acceptance: deterministic replay round-trip including responses; constant-policy bots
  still run (re-baseline for G1).

## L2 · Effort economy (ADR-0011) — after L1

- Delete the global AP pool. Founder-hours menu: doors (stakeholder face-time),
  approvals (hires = "approve this salary," not paperwork), audits (skip-level),
  reserve.
- Per-person staff assignment to workstreams from a backlog; unassigned staff
  self-direct **within their lane** (cross-lane drift is rare + diagnostic).
- Workstreams: multi-month, produce artifacts; **milestone ticks** within a workstream
  (working papers, blog posts) yield partial rep/SA — spikes without added player
  judgment.
- Managers: absorb their team's interrupt classes; plan-screen compression (members
  housed under manager, expand-on-click; team report replaces per-member detail);
  Celine's-law report channel stub (fidelity < 1); agenda riders via existing ledger
  staff-rider factory.
- Ops/admin: reduce founder-price of routine actions; automate classes over time.
- Researcher model: lane × appetite × optional quirk-rider — roster in WORLD_AND_LORE
  (DQ-15); retention promises are ledger entries.

## L3 · Adoption, papers, conferences (ADR-0010 + ADR-0014) — after L2

- Safety research splits: internal hardening (own-lab doom, private) vs publishable
  agendas (world/rival doom, adoption-routed). Rival/world doom share must dominate the
  integral or teeth are cosmetic.
- Pipeline: research → paper → socialization → adoption (labs/governments) → doom
  bends. Unadopted world-facing research is a PDF.
- Reputation: per-person + per-org, **typed** (safety-rep vs finance-rep); typed
  attention events (safety success → grants/interviews; reckless success → accel VC).
- Conferences: seed-schedule entries, annual majors announced ~9 months out; exclusive
  gatherings gated by contacts/safety-rep. Founder attendance (founder-hours + travel
  cash) ≫ delegate (staff-month + travel cash). Yields: adoption acceleration, faster
  rep (esp. introductions), **contacts-as-receivables** (ledger receivables content —
  DQ-9), SA presence boost.
- Location minimal: `where` on events; HQ defaults American; overseas team basing =
  cheaper hires + downstream influence hooks (stub the hooks).

## L4 · Event taxonomy + ledger intake (ADR-0012) — after L1, parallel with L2

- Absorbs BL-1..3 (the DEFER menu IS the ledger's player-facing UI wiring).
- Event classes: **un-snoozable** (borders, emergencies, legal threats, story events —
  no DEFER), **deferrable** (mints ledger entry, carrying cost via L5 engine —
  placeholder rate until then), **standing offers** (open N turns → expire to
  no-engage, optional rep loss, NO ledger entry), **no-action-correct**.
- Called-due cascade: unpaid staff work damaged for a period → leave → work abandoned →
  severe rep penalty → credit lockout → funding starvation → rival pulls ahead → doom
  spike. The ledger never owns a death screen; the cascade must be legible (EE-7).
- The infinite to-do list is diegetic: overflow falls out of the foreground honestly.
- Event content schema: class, expiry N, response-expected flag, `where`, carrying-cost
  hook.

## L5 · Pricing engine (ADR-0013) — after L4; numbers gated on L6

- One engine for loans, defers, funding-with-strings:
  `cost = f(org_type [major], counterparty [major], typed_rep, purpose_hype,
  ledger_load [minor])`.
- Purpose-tagged fundraising (hype prices the purpose); **no internal earmarked
  budgets**.
- Instruments: equity (single dilution scalar v1), board seats (stub as
  "options-curtailed" flag until DQ-7 designs voting), agenda narrowing (constrains
  legal workstreams).
- Tuning target: philanthropy-only is starved-but-viable (G3).

## L6 · Instrumentation (EE-7, EE-8) — start immediately

- **EE-8 first:** root-cause death attribution in the exploit-finder (a doom death
  downstream of a default is a ledger death). Prerequisite to ALL tuning.
- Exploit-finder policy space: plan policy × response policy × assignment policy ×
  publish/socialize policy (absorbs BL-5).
- EE-7: per-resource per-turn delta indicators; event-log improvement (loss legibility).

## L7 · Save/load (EE-2, PROMOTED) — start immediately

- Full state round-trip including ledger entries, triggered_events/cooldowns, and (once
  L2 lands) workstreams. 6–8 hr runs are untestable without it; DQ-11 forking builds on
  it.

## L8 · Achievements skeleton — start anytime, small

- **Observer-only contract:** achievements are read-only listeners on run events; they
  never write back to sim or score (ADR-0002 anti-sink rule — pure recognition, no
  in-run reward).
- v1 set: year marks (survived 2022 / 2027 / 2032 / 2037), "first time X" local profile
  flags. "Fastest X this season" deferred until boards (EE-4).
- Capture convention: design sessions tag `[ACHIEVEMENT]` candidates as they come up;
  park them in WORKSHOP_2_BACKLOG.

## Provisional UI guidance (NOT an ADR — revisit at workshop #3 with real screens)

Hub-and-spoke default for implementers, adopted to prevent five freelance navigation
patterns during the rebuild: the plan screen is the hub; every screen reachable within
~1 action of it; ESC always steps toward the hub; response windows are the only modal
interrupts. Pip has not ratified this as doctrine — log friction against it rather than
inventing alternatives, and it gets ruled with real screens in hand.

## Old-backlog reconciliation

- BL-1..3 → absorbed into L4. BL-5 → absorbed into L6. EE-2 → promoted to L7.
- DQ-6 → batch into L1's schema bump. DQ-8 → gated behind L6 (EE-8), executed in L5+G1.
- DQ-2 (baseline yardstick) → re-baseline as part of G1.
- DQ-7 (governance) → still undesigned; L5 stubs board seats against it.
