# Build Brief — Hiring Pipeline + Typed Effort Economy (L2 content wave)

> Steering artifact for the hiring-pipeline build. Design is COMPLETE (ruled) — this maps it
> to phases. Design sources (do not re-litigate, cite): WORKSHOP_2_BACKLOG "Hiring pipeline
> RULED (barrage)" + "DQ-24 taxonomy RULED" + "Character sprite system"; ADR-0011 (effort
> economy), ADR-0009 (durations, no instant strategy), ADR-0004 (SA = pay-to-see; hiring IS
> scouting), ADR-0003 (ledger = promises/retention-debt). Attention is canonical (20/mo).
> DESIGN_CONTRIBUTIONS.md credits the interview-triage idea.

## Why this wave
It's what fills the Attention economy with *meaningful* things to spend on (playtest-4:
"not enough smaller actions demanding my time") and delivers the **fishing-line** feel (cast
effort out via a slow gated process; the reward comes back later). Hiring is also **scouting**
(pay Attention to see a candidate, or gamble blind). This is the "playable → engaging" jump.

## Core rules that hold across all phases
- **Deterministic** (seeded RNG; replay-safe, ADR-0006). Every outcome traces to a player
  selection (ADR-0002 skill-legibility).
- **Physical identity is DECOUPLED from ability** (sprites already carry identity;
  ability/personality is hidden data revealed over time).
- **Hidden info is TRUE-but-incomplete** — the sim never lies; interviewing *reveals*, it does
  not fabricate; rare quirks stay hidden until an exposure event (ADR-0003).
- **Type demands, never the currency** — Attention stays single/universal; the founder is a
  strong generalist; specialists absorb their category (DQ-24).
- **Phase-scaled** — Phase A/B are the Startup/Incubator feel (few people, founder-does-most);
  Phase C/D bring Entity-phase management complexity, gated to when the player graduates to it
  (never front-loaded — the Moral-Mazes misery is earned).

---

## Phase A — Hire/candidate data model + the candidate card  (BUILD FIRST)
The foundation everything else needs. Extend the researcher/staff model in `game_state.gd`:
- **Identity:** sprite/appearance ref (diverse, ability-uncorrelated), name.
- **Hidden ability layer:** true skill, **appetites** (compute / prestige-first-author /
  mentees / money / mission-purity — ADR-0011), rare **quirk** riders, loyalty-risk.
- **Reveal level:** how much of the card the player has uncovered (0 = uninterviewed →
  progressively revealed by interviews). Un-interviewed shows lane + rough seniority only.
- **Hire-state:** `candidate-in-pool` / `offered` / `employed` / `departed`.
- **Candidate-card UI:** shows revealed fields; hidden fields shown as `??? (interview to
  reveal)`. This is hire-as-scouting made visible (ADR-0004).
Acceptance: a candidate exists with hidden fields; interviewing (Phase B) can flip hidden→known.

## Phase B — The pipeline: source → interview → offer → onboard  (BUILD SECOND)
Each stage is an **Attention-gated, multi-turn (duration) action** (ADR-0009 — nothing
instant). The fishing-line.
- **Source (two channels, distinct pricing):** *Advertise* = money + time → candidates trickle
  into the pool over weeks (also spawns NPC awareness of you). *Connections* = spend social
  capital → fewer, faster, pre-vetted candidates; success scales with **relative-rep flattery**
  (your standing vs the target's desirability). (NPC pool can be lazily-realized — don't
  over-simulate.)
- **Interview** (Attention-gated, TRIAGE — can't screen a whole pool): reveals hidden card
  portions. Hiring blind = legal but more stays hidden (a scouting gamble).
- **Offer + negotiate** (no minigame): candidate has a hidden self-worth/$ range; the offer must
  land in it. A recruiter/lieutenant gives the read ("Rebecca thinks we can get James to Foo /
  Foo+ / Foo-"). **Appetites are the negotiation currency** — a prestige-hungry candidate takes
  less cash for a first-authorship *promise* (mints a ledger entry, ADR-0003); resentment from
  a lowball is a loyalty debt.
- **Onboard:** predictable **checklist** (laptop, mentoring — Attention costs before they're
  productive) + situational **events** (visa if foreign/remote). Skimping (skip mentoring) =
  early-attrition risk / productivity debuff (slack-as-insurance, slow and tempting).

## Phase C — Typed Attention demands + workstream assignment + admin
- **DQ-24 five demand categories**, each with an absorbing hire-role: Ops/Admin,
  People/Management, Technical-Infra/Security, Research-Direction, External/Social. Founder =
  universal generalist; specialists absorb their category (bookkeeping ≠ a security engineer).
- **Workstream assignment** (ADR-0011): assign staff per-person at plan speed to workstreams
  that run multi-month and produce artifacts. Unassigned staff self-direct (drift).
- **Admin overhead tax** (dial-5 B): ~part of the monthly Attention is pre-spent on admin;
  ops/admin hires buy it down. **Payroll is a demand** (granular failure — miss it and *some*
  staff whose timesheets weren't approved have issues, not an all-or-nothing wipe).

## Phase D — Individual-researcher problems + managers (Entity-phase)
- **Named, appetite-driven problems:** "Sage has a crisis" (an unfed-appetite → a problem
  event), NOT "an employee has a problem." Personified provenance + attachment.
- **Managers phase-change the problem-space** (Moral Mazes): unmanaged → distraction/drift
  problems; managed → middle-management pathology. Managers **aggregate** individual problems
  into a report (Celine's-law fidelity loss) — you stop seeing individual crises once a team has
  a lead; skip-level audits (founder Attention) re-ground truth.
- **Burnout model:** prevention cheap (send on holiday), recovery long (sudden quit / no-notice
  / extended leave → return with lasting loyalty+efficiency debuff). Feeds DQ-22 poach-vulnerability.

---

## Integration points (already built — wire into them)
- **Attention economy** (canonical) — the pipeline stages + demands spend it.
- **OfficeFloor sprites** — a new hire appears on the floor; state reads off it.
- **Plan screen** (plan/watch UI) — the candidate cards, the assignment UI, and the demand
  allocation live here (BUILD_BRIEF_PLAN_WATCH_UI: the team panel unfolds into the assignment
  board at Entity).
- **Ledger** — promises (first-authorship etc.), retention debts, exposure events.
- **Sweep harness** — extend bot policies to exercise the pipeline; the mortality/legibility
  contracts hold.

## Build order
1. **Phase A** (data model + candidate card) — foundation, Pip-review.
2. **Phase B** (the source→interview→offer→onboard pipeline) — the fishing-line, Pip-PLAYTEST
   (this is where the feel gets judged).
3. Then C (demands/assignment/admin), then D (problems/managers) as later waves.
Each phase: deterministic, keep the game playable, fast-gate + sweep green, Pip-review PR.
The DQ-24 taxonomy and the candidate-card info model are the two things worth a quick Pip
confirm at the top of the build.
