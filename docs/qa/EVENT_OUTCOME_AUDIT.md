# Event Outcome Audit — flavor text vs mechanical effect (#631 follow-up)

**Scope:** every player-visible event outcome in the externalized event data —
all 25 core events / 74 choice outcomes (`godot/data/events/core_events.json`)
and all 30 risk events (`godot/data/events/risk_events.json`). Historical events
(`EventService`) are covered by construction: the transformer only ever emits
scalar keys (`reputation`, `doom`, `research`, `money` — `autoload/event_service.gd`),
all of which the apply path handles.

**Bug class being killed:** an event's flavor text claims something happens, but
the mechanical effect silently does nothing or mismatches the text. Root cause in
both apply paths: **unknown effect keys are silently dropped** —
`ResourceAccessor.add()` returns `false` and the `match` falls through
(`events.gd execute_event_choice`), and `state.add_resources()` ignores keys it
doesn't recognize (`turn_manager._step_process_risk_pools`). Unknown *cost* keys
are likewise silently free (`can_afford`/`spend_resources`).

**Verdicts:** `OK` = effect matches the text (or text claims nothing mechanical).
`NO-OP` = text claims an effect that never happened. `MISMATCH` = effect exists
but doesn't match the text. `AMBIGUOUS` = target/intent unclear. `DEFERRED` =
needs Pip's design ruling; not guessed at.

**Totals: 104 outcomes checked — 98 OK / 2 NO-OP (both fixed) / 2 MISMATCH (both fixed) / 2 AMBIGUOUS (1 fixed in #633, 1 DEFERRED).**

## Core events (`core_events.json`) — applied via `GameEvents.execute_event_choice`

| Event | Choice | Flavor claim | Actual effect | Verdict | Fix status |
|---|---|---|---|---|---|
| funding_crisis | emergency_fundraise | +$75k emergency funding | money +75000 (1 AP) | OK | — |
| funding_crisis | sell_assets | +$120k, -10 research | money +120000, research -10 (2 AP) | OK | — |
| funding_crisis | accept | "Continuing with limited funds" | none | OK (flavor-only, claims nothing) | — |
| talent_recruitment | hire_immediately | +1 safety researcher, -3 doom | real Researcher hired (named note), doom -3 | OK | — |
| talent_recruitment | hire_discounted | +1 safety researcher, -2 doom | real Researcher hired (named note), doom -2 | OK | — |
| talent_recruitment | decline | declined offer | none | OK (flavor-only) | — |
| ai_breakthrough | publish_open | +5 doom, +10 rep, +20 research | matches | OK | — |
| ai_breakthrough | keep_proprietary | +2 doom, +30 research | matches | OK | — |
| ai_breakthrough | safety_review | +1 doom, +15 research, +5 rep | matches (1 AP, $20k) | OK | — |
| funding_windfall | accept_donation | +$150k, +5 rep | matches | OK | — |
| funding_windfall | decline_donation | +3 rep | matches | OK | — |
| compute_deal | accept_deal | +100 compute, -2 rep | matches | OK | — |
| compute_deal | negotiate | +150 compute, -5 rep | compute +150, rep 5 paid as cost (can_afford checks rep) | OK | — |
| compute_deal | decline_deal | declined | none | OK (flavor-only) | — |
| employee_burnout | emergency_intervention | "prevented resignations", +8 rep, -5 doom | rep +8, doom -5 ($30k, 2 AP) | OK (retention = nobody leaves) | — |
| employee_burnout | team_retreat | +5 rep, -2 doom | matches ($30k) | OK | — |
| employee_burnout | salary_raise | "improved retention", +8 rep | rep +8 ($50k) | OK | — |
| employee_burnout | ignore_burnout ("Push Through") | event setup: "several researchers are **considering** leaving"; outcome message claims only "+3 doom" | doom +3, nobody leaves | **AMBIGUOUS** | **DEFERRED** — Q for Pip: should Push Through actually cost a researcher (e.g. least-loyal leaves, or a loyalty hit), or is "retained under strain, +3 doom" the intent? (#633 noted "arguably intended") |
| rival_poaching | counter_offer | $80k "retained researchers" | money -80000, nobody leaves | OK (paying to keep everyone) | — |
| rival_poaching | let_go | "Lost researcher, +$20k saved" | was silent NO-OP (`safety_researchers: -1` fell through) | **NO-OP** | **FIXED in PR #633** — least-loyal safety researcher actually removed + named |
| media_scandal | pr_campaign | +10 rep | matches ($40k) | OK | — |
| media_scandal | ignore_media | -8 rep | matches | OK | — |
| government_regulation | support_regulation | -10 doom, +15 rep | matches ($50k, 1 AP) | OK | — |
| government_regulation | oppose_regulation | +5 doom, -5 rep | matches | OK | — |
| government_regulation | stay_neutral | +2 doom | matches | OK | — |
| technical_failure | emergency_repair | +30 compute | matches ($60k) | OK | — |
| technical_failure | basic_fix | "limping along", -20 compute | compute -20 ($20k) | OK (text matches; paying to still lose compute is odd but stated) | — |
| stray_cat | adopt_cat | cat adopted, -1 doom | has_cat flag set, doom -1 ($500) | OK | — |
| stray_cat | feed_and_release | cat wanders off | none ($100) | OK (flavor-only) | — |
| stray_cat | shoo_away | +1 doom | matches | OK | — |
| workplace_conflict | mediate_personally | +3 rep, -1 doom | matches (1 AP) | OK | — |
| workplace_conflict | hire_mediator | +5 rep | matches ($15k) | OK | — |
| workplace_conflict | ignore_conflict | -3 rep, +2 doom | matches | OK | — |
| harassment_complaint | thorough_investigation | +8 rep | matches (2 AP, $25k) | OK | — |
| harassment_complaint | quick_resolution | +3 rep | matches ($40k) | OK | — |
| harassment_complaint | minimize_issue | -10 rep, +3 doom | matches | OK | — |
| salary_dispute | salary_audit | +10 rep, -2 doom | matches ($60k) | OK | — |
| salary_dispute | explain_structure | +2 rep | matches (1 AP) | OK | — |
| salary_dispute | ignore_concerns | -5 rep, +1 doom | matches | OK | — |
| mental_health_crisis | full_support | +8 rep, -3 doom | matches ($30k) | OK (leave is narrative; no claim of staffing change) | — |
| mental_health_crisis | partial_leave | +3 rep | matches | OK | — |
| mental_health_crisis | deny_leave | -8 rep, +5 doom | matches | OK | — |
| office_theft | security_upgrade | +5 rep, +10 compute | matches ($35k) | OK | — |
| office_theft | team_meeting | +2 rep | matches (1 AP) | OK | — |
| office_theft | ignore_theft | -15 compute, -3 rep | matches | OK | — |
| policy_violation | formal_discipline | +5 rep | matches (1 AP) | OK (no claim the violator leaves) | — |
| policy_violation | verbal_warning | -2 rep | matches | OK | — |
| policy_violation | sweep_under_rug | -6 rep, +2 doom | matches | OK | — |
| research_leak | investigate_leak | +3 doom, +5 rep | matches (2 AP, $30k) | OK (leaker "addressed", no firing claimed) | — |
| research_leak | publish_immediately | +1 paper, +8 rep, +5 doom | matches (1 AP) | OK | — |
| research_leak | accept_leak | +8 doom, -3 rep | matches | OK | — |
| competitor_intel | use_intel | -5 doom, -8 rep | matches ($20k) | OK | — |
| competitor_intel | report_intel | +10 rep, -3 doom | matches (1 AP) | OK | — |
| competitor_intel | refuse_intel | +3 rep | matches | OK | — |
| whistleblower_approach | full_support | -15 doom, +20 rep | matches (2 AP, $50k) | OK | — |
| whistleblower_approach | anonymous_support | -8 doom, +5 rep | matches ($25k) | OK | — |
| whistleblower_approach | hire_whistleblower | +1 safety researcher, -3 doom | real Researcher hired (named note), doom -3 ($60k, 1 AP) | OK | — |
| whistleblower_approach | decline_involvement | -5 rep | matches | OK | — |
| employee_whistleblower | address_concerns | +8 rep, -2 doom | matches (1 AP) | OK | — |
| employee_whistleblower | private_resolution | +3 rep | matches ($30k) | OK | — |
| employee_whistleblower | suppress_concerns | -15 rep, +5 doom | matches | OK (concerned employee stays; no departure claimed) | — |
| plant_source_opportunity | plant_source | "-15 reputation **if discovered**" | rep -15 applied unconditionally, immediately | **MISMATCH** (text implies a conditional the mechanics don't have) | **FIXED this PR** — message reworded to unconditional ("word of your methods spreads"). Alt design (actual discovery roll) available if preferred |
| plant_source_opportunity | legitimate_partnership | -5 doom, +8 rep | matches (1 AP, $40k) | OK | — |
| plant_source_opportunity | decline_espionage | +2 rep | matches | OK | — |
| competitor_password_breach | public_security_audit | +15 rep, -3 doom | matches ($40k, 1 AP) | OK | — |
| competitor_password_breach | offer_help | +10 rep | matches ($25k) | OK | — |
| competitor_password_breach | stay_silent | -5 rep, +2 doom | matches | OK | — |
| competitor_password_breach | exploit_weakness | +$50k, -10 rep, +3 doom | matches (1 AP) | OK | — |
| your_security_audit | full_security_overhaul | +8 rep, -5 doom | matches ($60k, 2 AP) | OK | — |
| your_security_audit | patch_critical | +3 rep, -2 doom | matches ($20k) | OK | — |
| your_security_audit | defer_security | +5 doom | matches | OK | — |
| researcher_poached | match_offer | researcher stays, +2 rep | rep +2 ($50k), nobody leaves | OK | — |
| researcher_poached | counter_promotion | promoted, +3 rep | rep +3 (1 AP, $30k) | OK | — |
| researcher_poached | let_them_go | "Researcher departed", +3 doom | pre-#633: RANDOM researcher removed, unnamed | **AMBIGUOUS** (which researcher?) | **FIXED in PR #633** — deterministic least-loyal target (loyalty = poaching resistance), departure named in log |

## Risk events (`risk_events.json`) — applied via `turn_manager._step_process_risk_pools`

All 30 outcomes are forced (no player choice). Scalar effects here apply via
`state.add_resources` — a *different* path from `execute_event_choice`, with its
own silent-drop failure mode (now also handles `lose_researcher`, this PR).

| Event | Flavor claim | Actual effect | Verdict | Fix status |
|---|---|---|---|---|
| risk_capability_minor_1 (Alignment Tax Debate) | -3 rep, +2 doom | matches | OK | — |
| risk_capability_minor_2 (Capability Gap Concerns) | -5 research, +3 doom | matches | OK | — |
| risk_capability_moderate_1 (Unexpected Capability Jump) | +8 doom, +5 rep | matches | OK | — |
| risk_capability_severe_1 (Near-Miss Incident) | +12 doom, -10 rep, -$30k | matches | OK | — |
| risk_capability_catastrophic_1 (RSI Scare) | +20 doom, -20 rep, -50 compute | matches | OK | — |
| risk_integrity_minor_1 (Replication Failure) | -5 rep, -1 paper retracted | matches (papers -1) | OK | — |
| risk_integrity_minor_2 (Peer Review Criticism) | -10 research, -2 rep | matches | OK | — |
| risk_integrity_moderate_1 (Data Quality Concerns) | -20 research, -8 rep, +3 doom | matches | OK | — |
| risk_integrity_severe_1 (Retraction Notice) | -2 papers, -15 rep, +5 doom | matches | OK | — |
| risk_integrity_catastrophic_1 (Whistleblower Exposé) | "former employee goes public", -30 rep, +10 doom, -$50k | matches (a *former* employee — no current-staff removal claimed) | OK | — |
| risk_regulatory_minor_1 (Compliance Inquiry) | -$10k, -2 rep | matches | OK | — |
| risk_regulatory_minor_2 (Policy Consultation) | -$5k, +3 rep | matches | OK | — |
| risk_regulatory_moderate_1 (Formal Investigation) | -$40k, -10 rep, +3 doom | matches | OK | — |
| risk_regulatory_severe_1 (Congressional Hearing) | -$60k, -5 rep, +5 doom | matches | OK | — |
| risk_regulatory_catastrophic_1 (Moratorium Proposal) | "-30 compute **frozen**" | compute permanently removed, never returned | **MISMATCH** (text implies temporary; effect permanent) | **FIXED this PR** — message reworded ("frozen" dropped); a real freeze/thaw mechanic would be a design change |
| risk_public_minor_1 (Social Media Backlash) | -5 rep | matches | OK | — |
| risk_public_minor_2 (Documentary Mention) | -3 rep, +$10k donations | matches | OK | — |
| risk_public_moderate_1 (Viral AI Panic) | +5 doom, -8 rep, -$20k | matches | OK | — |
| risk_public_severe_1 (Tech Backlash Movement) | -15 rep, -$40k, +8 doom | matches | OK | — |
| risk_public_catastrophic_1 (Protest Blockade) | +12 doom, -25 research, -$50k | matches | OK | — |
| risk_insider_minor_1 (Morale Issues) | -8 research, -2 rep | matches | OK | — |
| risk_insider_minor_2 (Internal Conflict) | -5 research, -$5k | matches | OK | — |
| risk_insider_moderate_1 (Key Resignation) | "**Senior researcher quits**", -15 research, -5 rep, +3 doom | pre-fix: scalars only — **nobody actually left** | **NO-OP** (staffing) | **FIXED this PR** — `lose_researcher: 1` added; least-loyal researcher removed via `GameEvents.remove_researchers` and **named** in the risk log line ("resigned") |
| risk_insider_severe_1 (Data Leak) | insider leaked data; -20 rep, +8 doom, -20 research | matches (leaker not identified in fiction; no removal claimed) | OK | — |
| risk_insider_catastrophic_1 (Sabotage Discovered) | sabotage found; -40 research, +15 doom, -25 rep, -$30k | matches (saboteur's fate not claimed) | OK | — |
| risk_financial_minor_1 (Budget Overrun) | -$15k | matches | OK | — |
| risk_financial_minor_2 (Invoice Dispute) | -$8k, -1 rep | matches | OK | — |
| risk_financial_moderate_1 (Funding Delay) | -$30k, +3 doom | matches | OK | — |
| risk_financial_severe_1 (Budget Shortfall) | -$50k, +6 doom | matches | OK | — |
| risk_financial_catastrophic_1 (Runway Crisis) | +20 doom, -$80k, -15 rep | matches | OK | — |

## DEFERRED — needs Pip's ruling

1. **employee_burnout / "Push Through"** — should ignoring burnout actually cost
   a researcher (least-loyal leaves, or a loyalty penalty that raises future
   poach vulnerability), or is "+3 doom, everyone grudgingly stays" the intended
   retention-under-strain outcome? The setup text says researchers are
   "considering leaving"; the outcome message claims only doom, so this is
   text-consistent but arguably toothless. (#633 flagged the same question.)

## How the class stays dead (regression armor, this PR)

- `test_events.gd::test_all_core_event_effect_keys_are_handled` — every effect
  key in `core_events.json` must be in the vocabulary `execute_event_choice`
  actually applies; an unhandled key now fails the suite instead of shipping as
  a silent no-op.
- `test_events.gd::test_all_core_event_cost_keys_are_payable` — same for cost
  keys (`can_afford` silently ignores unknown costs = free lunch).
- `test_risk_system.gd::test_property_all_risk_events_have_valid_effects` —
  whitelist corrected to what `_step_process_risk_pools` actually handles
  (`stationery` removed — it was allowed but unhandled; `lose_researcher` and
  `technical_debt` added).
- `test_turn_manager.gd::test_insider_threat_key_resignation_removes_a_researcher`
  (+ empty-roster safety case) — outcome assertion driving the real risk-pool
  path via a guaranteed threshold trigger.
- `test_events.gd::test_remove_researchers_*` (3 tests) — the shared staffing-loss
  helper: least-loyal-first, spec filter, safe empty no-op, named notes.
- Existing #633 poaching regression tests continue to cover the
  `execute_event_choice` staffing arms.

**Residual limitation:** the key-whitelist tests prove every key is *handled*,
not that the magnitude/direction matches the prose. The prose-vs-effect check in
this document was done by human-readable audit (this table); keeping messages
and effects adjacent in the JSON is the practical guard. A stronger invariant
(parse the "(+N x)" claims out of message strings and diff against effects) is
possible; not built here to keep scope bounded.
