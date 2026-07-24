# People & Money Cohesion Spine

- **Status:** DESIGN DOC (paper spine, no code) -- WS-3/epoch material
- **Date:** 2026-07-24
- **Issue:** #833 ("design: 'people & money' cohesion spine")
- **Related:** #574 (payroll/accounting depth), #830 (hiring statefulness), #822
  (overbook teeth -- see the mismatch note in Section 6), #803 (conference
  scheduling substrate), ADR-0003 (Liability Ledger), ADR-0011 (effort economy),
  ADR-0012 (event-response taxonomy / spiky-in-smooth-out cash), DQ-19
  (character/org creation surface)

This is a DESIGN document: options, a recommendation per fork, and open
questions for Pip. It is not a spec to implement wholesale. Per #833's method:
forge the data-model CONNECTIONS on paper now, so future work builds against a
pinned shape, without shipping dead fields or forking mechanics ahead of a
balance sweep.

---

## 1. The cohesion thesis

Pip's framing (2026-07-24 design workshop, verbatim from #833): *"The
recruitment flow is an EPIC whose sub-steps are PER-CANDIDATE, never
standalone: advertise-a-ROLE (spawns candidates already APPLYING for that
role) -> interview [candidate] -> offer to [candidate] -> onboard -> the hire
holds a ROLE (title / manager / monthly SALARY). 'Everyone needs a job' ->
salary = a PAYROLL obligation -> lands in the ledger/finance -> surfaced in an
expanded Employee screen <-> budget/finance screen."*

The GOAL, in his words: *"COHESION -- a legible causal chain the player
intuits over many interactions ('hired for a role -> it costs salary -> cash
tightens -> manage the budget')."*

Why cohesion, not tidy data, is the prize: the individual pieces already
exist and mostly work. `Researcher` carries `current_salary`.
`turn_manager._step_pay_salaries()` already drains it from `state.money`
every turn. `Ledger` already models "every mitigation is a loan" (ADR-0003).
`employee_screen.gd` already lists researchers. None of these currently
**reference each other**. A player can watch cash drop every turn and never
connect it to the roster; can fire someone and never see the severance land
on a finance screen; can read "9 employees, unmanaged past 9" without any
visual tie to who manages whom. The mechanics are correct in isolation and
illegible as a system -- the opposite failure mode from a tidy-but-decorative
data model that no screen reads.

**Method inversion, explicit:** WORKSHOP_2 (ADR-0009..0014) spent its budget
*surfacing hidden abstractions* -- pulling implicit rules (instant-resolve
actions, global AP, opaque candidate quality) into visible, player-facing
mechanics. This spine does the opposite: the pieces are already surfaced and
separately legible; the work is *fusing* them into one causal chain the
player can narrate back. That reversal is why the method here is
"forge-on-paper, consume-on-demand" rather than "build the whole graph now."

## 2. The data model

### What exists today (grounded in `godot/scripts/core/researcher.gd`)

`Researcher` (a `Resource`, `class_name Researcher`) already carries, among
others:

| Field | Type | Notes |
|---|---|---|
| `researcher_name` | `String` | display name |
| `specialization` | `String` | `safety \| capabilities \| interpretability \| alignment` -- the research LANE |
| `skill_level` | `int` | 1-10 |
| `salary_expectation` | `float` | set at spawn from `SPECIALIZATIONS[spec]["base_cost"]` (annual) |
| `current_salary` | `float` | the negotiated annual figure; billed per-turn via `Clock.annual_to_per_turn()` |
| `candidate_id` | `String` | stable cross-reference handle (object identity does not survive the JSON save/load hop -- the existing comment in `researcher.gd` is explicit about this) |
| `hire_state` | `int` (enum `HireState`) | `CANDIDATE_IN_POOL \| OFFERED \| EMPLOYED \| DEPARTED` |
| `onboarded`, `laptop_done`, `visa_done`, `systems_done`, `meet_people_done`, `mentoring_done`, `mentoring_skipped` | `bool` | Phase-B onboarding checklist (#789) |
| `appearance_id` | `String` | sprite handle, deliberately uncorrelated with ability |
| `appetites` | `Dictionary` | the 5 ADR-0011 hungers, negotiation currency |
| `loyalty`, `loyalty_risk`, `burnout`, `turns_employed` | mixed | dynamic state |

Notice what is **absent**: no `role`/`job_title`, no `manager` reference, no
`applying_for_role`. `specialization` currently does double duty as "the
role" for research staff, but has no equivalent for the non-researcher
archetypes.

### The other half of the roster is scalar, not entity-backed

`godot/scripts/core/game_state.gd` carries `managers: int` and
`compute_engineers: int` as flat counters (plus legacy `safety_researchers` /
`capability_researchers` counters that pre-date the `Researcher` array).
Neither `managers` nor `compute_engineers` has a `Researcher` instance behind
it. `turn_manager._step_pay_salaries()` pays `managers` a flat
`Balance.num("salaries.manager_annual", 60000.0)` per head, multiplied by
`state.managers` -- but **does not pay `compute_engineers` at all** (the loop
only iterates `state.researchers` and adds a `state.managers` term; grep
confirms `compute_engineers` never appears in `_step_pay_salaries`). That is
a pre-existing gap this spine should either fix or explicitly declare
in-scope-later (see Section 8) -- not something to paper over by pretending
the current model is uniform.

### Fields to forge

**On `Researcher` (candidate + employed, same object across the lifecycle,
per the existing `HireState` transitions):**

- `applying_for_role: String = ""` -- the role a **pool candidate** is
  applying for. Set at spawn time by the (forking) targeted-advertise flow
  (Section 4). Distinct from `specialization`: `specialization` is the
  research LANE (what they publish in); `applying_for_role` is the ORG-CHART
  slot being filled (which may not even be a research role -- "Recruiting
  Lead," "Compute Engineer," "Manager"). For research hires the two will
  usually agree; that agreement should not be baked into the field, because
  the non-research archetypes need `applying_for_role`/`job_title` and have
  no `specialization` concept at all today.
- `job_title: String = ""` -- the **employed** role, copied from
  `applying_for_role` at `_accept_offer()` time (or set directly for a
  non-pipeline/legacy hire). Kept as a separate field from
  `applying_for_role` rather than reusing one field across both states,
  because a candidate can apply for one role and be offered a different one
  (a real recruiting pattern, and useful hook for a future "counter-offer"
  mechanic) -- collapsing them would silently forbid that.
- `manager_id: String = ""` -- the `candidate_id` of the `Researcher` who
  manages this person. Empty string means founder-managed (today's implicit
  default -- ADR-0011: "First 9 researchers work without a manager (founder
  manages them)"). Chosen as a `candidate_id` string reference rather than a
  live `Researcher` object reference for the same reason `candidate_id`
  itself exists: object references do not survive the JSON save/load hop,
  and a string handle round-trips trivially through `to_dict()`/`from_dict()`
  the way `candidate_id` already does.
- `current_salary` stays as-is. **No new salary field is needed** --
  `current_salary` already IS the payroll figure, already billed every turn.
  The forge here is *connective*, not additive: what is missing is not a
  number, it is the role/manager context that number should be displayed
  alongside.

**Role: data table, not a `Resource` class (recommendation).** `Researcher`
already has a precedent for this shape -- `SPECIALIZATIONS` is a `const
Dictionary` keyed by lane id, not a `class_name Specialization` object. Roles
should follow the same pattern: a `res://data/staff/roles.json` (or a
`ROLES` const, if it stays this small) keyed by `role_id`, carrying
`display_name`, `base_salary_annual`, `management_capacity` (for manager-type
roles), and whatever else a future consumer needs. This is cheaper to
extend, mirrors the existing house style (`Balance` tables, `SPECIALIZATIONS`
const), and defers the question of whether a role needs its own *mutable,
shared* state (a headcount cap that several employees draw down together)
until an actual consumer needs it. If that day comes, promoting the table
entries to a `class_name Role : Resource` is a mechanical migration, not a
rethink -- the field names carry over unchanged.

*(Alternative considered: `Role` as a first-class `Resource`, referenced by
id from `Researcher.job_title`. Rejected for v1 as premature -- it doubles
the object graph that must serialize/save-load-round-trip for a benefit
(shared mutable role state) nothing currently consumes. Revisit if a role
ever needs live state of its own, e.g. a capped number of "Recruiting Lead"
slots.)*

**On `GameState` (or a small `Payroll`/query module, not a stored field):**

- No new stored field. The "payroll obligation" is a **derived** number: sum
  `Clock.annual_to_per_turn(r.current_salary)` over `state.researchers`, plus
  the scalar `managers`/`compute_engineers` terms, exactly as
  `_step_pay_salaries()` already computes it. See Section 3 for why this
  should stay a read query rather than becoming a new mutable object.

### Relations, summarized

```
Researcher (candidate)
  .applying_for_role -> role_id           (job-interest, pool-side)

Researcher (employed)
  .job_title          -> role_id           (org-chart slot)
  .manager_id          -> candidate_id      (another Researcher, or "" = founder)
  .current_salary       -> float             (already exists; the payroll figure)

Role (data table, keyed by role_id)
  .display_name, .base_salary_annual, .management_capacity, ...

Payroll obligation (derived, not stored)
  = sum(Clock.annual_to_per_turn(r.current_salary) for r in state.researchers)
    + state.managers * Clock.annual_to_per_turn(Balance.num("salaries.manager_annual"))
    [+ compute_engineers, if Section 5's gap gets closed]
```

## 3. The flow, step by step

1. **Advertise a role.** Player picks a `role_id` (today: `HiringPipeline.
   advertise(state)` takes no role parameter at all; `_spawn_candidate()`
   draws a random lane from `SPEC_POOL`). Forging the field means: campaign
   creation carries the chosen `role_id` forward into the candidates it
   trickles in.
2. **Candidates spawn already applying.** At each month-boundary trickle
   (`_tick_campaigns()`), spawned candidates get `applying_for_role =
   role_id` (and, for research roles, `specialization` set from the role's
   lane) instead of the current uniform-random draw. The card can show the
   role immediately -- `REVEAL_UNINTERVIEWED` already exposes `specialization`
   at reveal level 0, so `applying_for_role` slots into the same reveal tier
   with zero change to the reveal ladder.
3. **Interview [candidate].** `launch_interview(state, candidate_id)` --
   already exists, already per-candidate (`jobs` array keys on
   `candidate_id`). #830's ask is UI legibility (explicit WHO, a card+fade-in
   popup), not a data change.
4. **Offer to [candidate].** `make_offer(state, candidate_id, cash,
   promises)` -- already exists, already per-candidate.
   `_accept_offer()` is the natural point to copy `applying_for_role ->
   job_title` and to resolve `manager_id` (default "" / founder-managed, or
   an explicit assignment step -- open question, Section 8).
5. **Onboard.** `onboard_step()` / the hard checklist -- unchanged.
6. **The hire holds a role.** Once `EMPLOYED`, the `Researcher` carries
   `job_title` + `manager_id` + `current_salary` together -- the "holds a
   role" triad from Pip's framing.
7. **Salary becomes a standing payroll obligation.** No new event fires here
   -- `current_salary` was already being billed every turn by
   `_step_pay_salaries()`. What changes is *legibility*: a
   `payroll_monthly_total(state)` query (Section 2) can now be computed
   per-role and per-manager, not just as one undifferentiated lump.
8. **Lands in ledger/finance.** `turn_manager._step_pay_salaries()` keeps
   draining cash directly from `state.money` every turn exactly as today
   (Section 4 explains why this should NOT be re-routed through
   `Ledger.Entry` objects). What's new is a read: the finance/budget screen
   pulls `payroll_monthly_total(state)` as a labeled line item, the same
   number the roster screen shows as "burn."
9. **Surfaced in an expanded Employee screen <-> budget/finance screen.**
   `employee_screen.gd` / `employee_panel.gd` currently render `researchers`
   and the scalar counts with zero cross-reference to `state.ledger` or any
   finance total. The forge here: both screens read the same
   `payroll_monthly_total()` / per-role breakdown, so a player who fires
   someone on the roster screen and then opens finance sees the burn number
   move -- the causal chain made visible, not narrated.

## 4. The forking split (critical)

This is the section meant to stop a near-ship build from smuggling a forking
mechanic in under cover of "just adding some fields."

### NON-FORKING / cheap -- safe for a near-ship build

- **New data fields**: `applying_for_role`, `job_title`, `manager_id` on
  `Researcher`. Adding fields with safe defaults (`""`) that nothing reads
  yet changes no behavior. `Researcher.to_dict()`/`from_dict()` already
  round-trip unknown-to-old-saves fields fine given the pattern used for
  every other Phase B field (`.get(key, default)`).
- **Interview / offer as per-candidate UI sub-steps** (#830's ask). The
  pipeline is *already* per-candidate under the hood
  (`jobs` keyed on `candidate_id`, `find_pool_candidate`/`find_employed`
  lookups). Surfacing that explicitly in the UI (card+info fade-in, ask WHO)
  is a UI right-size, not a mechanics change.
- **A read-only `payroll_monthly_total(state)` query** surfaced on both
  roster and finance screens. Pure aggregation over existing
  `current_salary` data; no new mutation path; nothing about the difficulty
  curve changes because nothing about *how much is billed or when* changes.
- **Role data table** (Section 2's recommendation). Adding entries to a
  `Balance`-style table changes nothing until something reads
  `applying_for_role`.

### FORKING / needs a balance sweep -- WS-3/epoch material, do not smuggle

- **`advertise()` taking a role param and SPAWNING candidates already
  interested in that role.** This changes what's reachable each campaign
  turn (today: uniform-random lane trickle; after: player-targeted pipeline
  supply). WORKSHOP_2's sweep explicitly tracks "assignment policies join
  the policy space" as a sweep target (ADR-0011) -- a targeted-advertise
  lever is a new axis in exactly that space, and the exploit-finder has not
  seen it. Per #833's own framing: *"changes the reachable game."*
- **Routing payroll through the Ledger as a recurring liability**, if that
  is ever decided (see Section 2's recommendation against it, and Section 8's
  open question). `Ledger.Entry` is architected as a one-shot: `fuse` counts
  down, `_bill()` fires once, `settled = true`, done -- the post-mortem
  trail (`death_attribution`) depends on entries being attributable,
  terminal events, not a recurring subscription. Making payroll bill through
  that machinery would need either a new "recurring" entry kind (a schema
  change to a determinism- and save/load-tested core system) or re-minting a
  fresh `Entry` every pay cycle (which pollutes `entries` with N-per-turn
  churn and complicates `outstanding()`/`secret_entries()` reads). Per #833:
  *"payroll DRAINING money = 'every hire is a standing loan' (ADR-0003)"* --
  that framing is already true of the *existing* direct-drain mechanism
  (hiring someone increases a standing monthly obligation, full stop); it
  does not require literally minting Ledger entries to be legible. Treat
  "wire payroll non-payment into the ledger's default/exposure cascade"
  (ADR-0012's *"unpaid staff work on for a period suffering damage -> leave
  -> ... -> doom spikes"*) as the actual forking mechanic worth a sweep --
  today nothing detects "can't make payroll" as a distinct event; `state.
  money` just goes negative and whatever downstream system reads negative
  cash reacts (or doesn't). Wiring a real payroll-default trigger is a
  mortality-curve change.
- **`manager_id` auto-assignment / enforcing "who's managed" per-researcher**
  instead of the current scalar `management_capacity = 9 + managers * 9`
  math (`turn_manager._step_researcher_productivity()`). Real manager
  graphs change who counts as unmanaged (and therefore who drifts per
  ADR-0011's "unassigned researchers self-direct per their agenda"), which
  is a productivity-curve change, not a data-model change.

## 5. Membership boundary -- who is a salaried employee?

Grounded in what the code currently does, not just what it should do:

- **The founder is NOT a salaried employee.** No `Researcher` instance
  backs the player; ADR-0011 draws this distinction explicitly ("founder
  hours... canon since ADR-0008" vs "staff effort is per-person"). The
  founder spends **Attention** (`state.month_plan`), never draws
  `current_salary`, and is not billed by `_step_pay_salaries()`. This
  boundary already holds structurally (there is no code path that could
  even attempt to pay the founder a salary) -- **recommend formalizing it as
  a rule, not just an accident of the current object graph**: membership in
  payroll requires an entity with a `job_title`/`manager_id`/`current_salary`
  triad; the founder, by design, will never have one.
- **Researchers (`state.researchers: Array[Researcher]`) are IN** -- salaried
  by construction, billed every turn already.
- **Managers (`state.managers: int`) are IN payroll but structurally
  orphaned.** They're billed a flat rate, but have no `candidate_id`, no
  `job_title`, no ability to be the target of another employee's
  `manager_id`. If `manager_id` is forged as a real reference field
  (Section 4's forking item), managers need to become real `Researcher` rows
  (`job_title = "manager"`) for the reference to have anything to point at
  -- this is a **migration**, not an additive field, and belongs with that
  forking item, not before it.
- **Compute engineers (`state.compute_engineers: int`) are a genuine open
  gap, not a design choice**: grep across `godot/scripts/core/` finds no
  salary deduction for them anywhere (`_step_pay_salaries()` only sums
  `state.researchers` + `state.managers`). Either this is intentional
  (compute engineers are cheap/automated by design -- plausible given the
  2037-vignette "payroll is automated" endpoint referenced in ADR-0011) or
  it's a bug nobody hit because nobody's stress-tested a compute-engineer-
  heavy build. Flagging rather than silently fixing (see Section 8).
- **Contractors / `staff_rider`**: `Ledger.staff_rider()` already exists --
  a flat one-off governance liability minted at hire (and re-flagged
  `secret` on a disgruntled departure). This is NOT a payroll mechanism; it
  is an orthogonal, already-shipped liability rider. Do not conflate "does
  this person have a `staff_rider` ledger entry" with "is this person a
  salaried employee" -- every pipeline hire gets one regardless of role, and
  it fires once, not monthly.
- **Advisors**: no representation in code today at all. Out of scope for
  this spine; flag as a future membership-boundary question if/when advisors
  are built (they plausibly should NOT draw a `current_salary` the way a
  hire does -- equity/reputation-denominated compensation is the more
  obvious real-world model, and mirrors `FinanceEngine`'s existing
  `equity`/`philanthropy` non-cash instruments).

**Recommended rule:** membership = "has a `Researcher` row with a non-empty
`job_title`." This makes the founder's exclusion structural (no row exists),
makes the manager-orphan problem visible as a to-do rather than a permanent
special case (promote managers to rows, or explicitly declare scalar
managers exempt from the new fields), and gives compute engineers an
unambiguous either/or to resolve (promote to rows and bill them, or
explicitly declare scalar-and-unbilled-by-design).

## 6. Sequencing

1. **Forge on paper (this doc).** No code lands from this doc directly.
2. **Code each field when its first CONSUMER lands**, validated by real use
   -- not ahead of it:
   - `job_title` / `manager_id` land with the roster UI pass (or the
     manager-graph forking item, whichever comes first) -- not before either
     has code that reads them.
   - `applying_for_role` lands with the targeted-advertise forking item
     (there's no reason to carry it on candidates before advertise can set
     it to anything but "").
   - `payroll_monthly_total()` lands with whichever of {roster screen,
     finance screen} gets touched first -- it's a pure function, cheap to
     add opportunistically.
3. **`advertise-role-spawn` as an epoch mechanic** (Section 4's forking
   item) -- ships with its own balance sweep, not bundled into the roster/
   finance UI pass.
4. **Payroll gets its own design pass + sweep** -- see #574 ("payroll
   depth... make paying payroll cost AP + occasional timesheet-chasing...
   accounting-software upgrade introduces/gates the Liability Ledger").
   Note #574's own framing: the accounting-software upgrade is pitched as
   *diegetically explaining* how the player "gets" the ledger view --
   which is a strong hint that "lands in ledger/finance" in #833's framing
   may mean *visibility*, gated behind an upgrade, rather than a literal
   `Ledger.Entry` per payroll cycle. Worth reconciling explicitly with Pip
   before committing to either shape (see Section 8).
5. **Per-tick resolution dependency, flagged with a discrepancy note.** The
   task brief that produced this doc named a dependency on "per-tick
   resolution (`PER_TICK_RESOLUTION_DESIGN.md` / #822)" for any day-bound
   scheduling. As of this writing: **no `PER_TICK_RESOLUTION_DESIGN.md` file
   exists in `docs/`**, and **issue #822 in the tracker is titled "feat
   (mechanic): overbook TEETH -- forcing-function instead of a flat
   reject,"** not per-tick resolution. Recording this rather than silently
   reconciling it: either the per-tick design doc/issue does not exist yet
   under that name, or the brief conflated it with a different issue.
   Whichever party is stale, any day-bound payroll scheduling (fortnightly
   vs monthly, Section 8) should confirm its actual dependency before
   committing to a cadence -- the existing `Clock.WORKDAYS_PER_YEAR = 260.0`
   / `annual_to_per_turn()` machinery already resolves salary per *turn*
   (not per calendar day), so a fortnightly-vs-monthly cadence question may
   be substantially independent of whatever the per-tick work turns out to
   be.

## 7. ADR/issue connections

- **ADR-0003 (Liability Ledger)** -- "every mitigation is a loan." The
  payroll-obligation framing in #833 borrows this language; Section 4
  argues the existing direct-drain mechanism already embodies the thesis
  without needing literal `Ledger.Entry` minting, and identifies the actual
  forking version (wiring payroll-default into the ledger's cascade).
- **ADR-0011 (effort economy)** -- founder hours vs staff lanes vs manager
  compression is the source of the membership boundary (Section 5) and the
  management-capacity math this spine must not silently change (Section 4).
  Also the source of "idle staff don't exist; unmanaged staff do," which
  bears on what `manager_id = ""` should mean if it's ever enforced beyond
  a display label.
- **ADR-0012 (event-response taxonomy)** -- "spiky-in, smooth-out" cash flow
  and the unpaid-staff cascade language ("unpaid staff work on for a period
  suffering damage -> leave -> ... -> doom spikes") is the closest existing
  text to a payroll-default mechanic, and it is currently **prose, not
  code** -- nothing implements that cascade today. This is the real
  substance behind "payroll lands in the ledger," and it is squarely a
  forking item (Section 4).
- **ADR-0003 vs #574** -- #574's "accounting-software upgrade gates the
  ledger" is a *visibility* gate, separate from whether payroll itself is
  ledger-modeled. These are two different design moves that #833's language
  could be read as either; flagged as an open question (Section 8).
- **DQ-19 (character/org creation surface)** -- `org_type` already exists on
  `GameState` (`"nonprofit"` default, read by `FinanceEngine.context_from_
  state()`); DQ-19 owns whatever surface lets the player set it. Relevant
  here only insofar as `org_type` could plausibly gate role availability or
  salary bands later (a nonprofit vs a lab vs a startup might have different
  `base_salary_annual` tables) -- flagged as a future hook, not proposed now.

## 8. Open questions for Pip

- **Membership boundary.** Section 5 recommends "has a `Researcher` row with
  a non-empty `job_title`." Does that match your intent for contractors
  (`staff_rider`) and future advisors, or should there be an explicit
  `employment_type` enum (`employee \| contractor \| advisor`) from the
  start rather than inferring it from which fields are populated?
- **Payroll cadence.** #833's brief says you lean **fortnightly**; the
  current code bills every TURN via `Clock.annual_to_per_turn()` (annual/260
  workdays), which is already much finer-grained than either fortnightly or
  monthly -- it's a smooth per-turn drain, not a discrete payday event. Does
  "fortnightly" mean you want a discrete payday EVENT (a feed message, a
  moment of legibility) laid over the existing smooth drain, or an actual
  change to the billing cadence (e.g., bill every 10 turns in a lump instead
  of smoothly)? These read very differently against ADR-0012's "spiky-in,
  smooth-out" framing -- a lump-sum fortnightly bill is spikier than what
  exists today, which may be exactly the point (a payday the player can see
  coming and dread) or may reintroduce the "turn-7 cash crash" class of bug
  the `/260` fix (#573, referenced in `turn_manager.gd`) was written to kill.
- **Does per-tick resolution gate the day-bound parts?** Section 6 flags
  that the named dependency (`PER_TICK_RESOLUTION_DESIGN.md` / #822) does
  not currently match anything in the tracker under that description. Worth
  a quick confirm of what the actual dependent work is before scheduling
  cadence work against it.
- **Role taxonomy: reuse hire archetypes, or a separate role list?** Today's
  closest thing to "archetypes" is `HiringPipeline.SPEC_POOL` (the 4 research
  lanes) plus the informal "recruiter" read (`_best_recruiter()` picks the
  most senior onboarded researcher, skill >= a threshold -- not a real role,
  just a runtime query). Should `role_id` values be 1:1 with
  `specialization` for research hires (role = lane) plus new entries for
  `manager`/`compute_engineer`/`ops`/`recruiter`? Or should roles be a fully
  separate taxonomy that research hires' `job_title` happens to echo their
  `specialization` for, but isn't required to (enabling e.g. a capabilities
  researcher who is *also* the recruiting lead)? Section 2 leans toward the
  latter (separate fields, usually-equal values) but this is a real design
  call, not just a data-modeling one.
- **Should `compute_engineers` get billed, or is unbilled-by-design
  correct?** Section 5's finding (grep confirms no salary path for them) is
  presented neutrally; closing it either way is a small, non-forking fix
  once decided, but it changes the payroll total, so it should be a
  deliberate choice rather than something quietly patched in passing.
- **Manager promotion migration.** If `manager_id` becomes a real reference
  field (a forking item, Section 4), do scalar `state.managers` get migrated
  to `Researcher` rows retroactively (with a save-compat concern for
  existing saves carrying a scalar count and no rows to promote), or does
  the game accept a transition period where scalar-count managers coexist
  with row-backed managers and `manager_id` can only point at the latter?
