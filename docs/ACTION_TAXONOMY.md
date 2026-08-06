# Action taxonomy (GENERATED -- do not hand-edit)

> Derived from `godot/data/actions/*.json`, `action_bar_renderer.gd`
> (`category_order`, `HIDDEN_FROM_ACTION_BAR_IDS`) and
> `submenu_controller.gd` (`GRID_CONFIG`) by
> `scripts/generate_action_taxonomy.py`. Regenerate with:
> `python scripts/generate_action_taxonomy.py`.
>
> Implements Part D of `docs/design/UI_ARCHITECTURE_2026-08-06.md`.
> The rule it serves: **an action is top-level iff it is the single door to a
> system the player steers when composing an ordinary month's plan.**
>
> **The violation gate is REPORT-ONLY.** Pre-commit runs `--check-stale`, which
> fails only if THIS FILE is out of date. `--check` additionally exits nonzero on
> the errors below and is deliberately NOT wired while a known violation is live:
> a gate that is red on arrival gets disabled within a week (#1117). Flip the hook
> to `--check` when the error list is empty.

## Counts

| Measure | Value |
|---|---|
| Action entries | 62 |
| Distinct action ids | 61 |
| Files scanned | 12 |
| Files carrying actions | 11 |
| Doors (`is_submenu`) | 9 (cap 10) |
| Loose top-level tiles | 9 |
| Hidden from the bar | 3 |
| Errors | 1 |
| Warnings | 6 |

- `risk_contributions.json` carries ZERO actions and is excluded from the count (it is a lookup table, not an action list). The commission's earlier inventory credited it with 2.

## Findings

### Errors (`--check` exits 1)

- DUPLICATE ID 'take_loan' defined in 2 files: financing.json (category financing), fundraising.json (category funding). The domain caches are separate, so BOTH are live at once and neither shadows the other loudly; which one a lookup returns depends on accessor order in GameActions.get_action_by_id. They DISAGREE on: category (financing.json="financing" vs fundraising.json="funding"); description (financing.json="+$50k now; a balloon repayment (~$60k) bills in 4 turns and compounds until paid." vs fundraising.json="Immediate funds via debt - creates future repayment obligation"); gains (financing.json=null vs fundraising.json={"debt": 90000, "money": 75000}); name (financing.json="Take Loan" vs fundraising.json="Business Loan"). Deduping is therefore not a merge -- pick the record that matches what execute_action actually does, and say so.

### Warnings (reported, never fatal)

- NAMESPACE CATEGORY -- door 'operations' is category 'management'; its operations.json members are operations, which the action bar has no group for. The door has to borrow a render category, so `category` means two different things at the two levels. Phase 2 workitem.
- NAMESPACE CATEGORY -- door 'travel' is category 'research'; its travel.json members are travel, which the action bar has no group for. The door has to borrow a render category, so `category` means two different things at the two levels. Phase 2 workitem.
- NAMESPACE CATEGORY -- door 'financing' is category 'influence'; its financing.json members are financing, which the action bar has no group for. The door has to borrow a render category, so `category` means two different things at the two levels. Phase 2 workitem.
- NAMESPACE CATEGORY -- door 'office' is category 'management'; its office.json members are office, which the action bar has no group for. The door has to borrow a render category, so `category` means two different things at the two levels. Phase 2 workitem.
- NAMESPACE CATEGORY -- door 'scouting' is category 'influence'; its scouting.json members are scouting, which the action bar has no group for. The door has to borrow a render category, so `category` means two different things at the two levels. Phase 2 workitem.
- LOOSE TOP-LEVEL ACTIONS -- 9 actions render as bare tiles alongside the 9 doors (advertise, audit_safety, buy_compute, capability_research, onboard_next, publish_paper, safety_research, team_building, use_connections). Under the Part A rule each competes only with its door's siblings; phase 1/2 of docs/design/UI_ARCHITECTURE_2026-08-06.md folds them.

## Every action

`Door (today)` is measured from the data: which submenu file the action lives
in, and which `is_submenu` action opens that file. `Door (proposed)` is
transcribed from Part B of the architecture doc and is **reference only** --
nothing here checks it, and the Research door is gated on a workshop.

| # | id | Name | File | Category | Placement | Door (today) | Door (proposed) |
|---|---|---|---|---|---|---|---|
| 1 | `pass` | Do Nothing | `command.json` | `command` | top-level | (top level) | (command) |
| 2 | `hire_staff` | Hire Staff | `core.json` | `hiring` | door | (is a door) | People |
| 3 | `buy_compute` | Purchase Compute | `core.json` | `resources` | top-level | (top level) | Compute |
| 4 | `safety_research` | Safety Research | `core.json` | `research` | top-level | (top level) | Research |
| 5 | `capability_research` | Capability Research | `core.json` | `research` | top-level | (top level) | Research |
| 6 | `publish_paper` | Publish Safety Paper | `core.json` | `research` | top-level | (top level) | Research |
| 7 | `fundraise` | Fundraising | `core.json` | `funding` | door | (is a door) | Funding |
| 8 | `publicity` | Publicity | `core.json` | `influence` | door | (is a door) | Publicity |
| 9 | `team_building` | Team Building | `core.json` | `management` | top-level | (top level) | People |
| 10 | `audit_safety` | Safety Audit | `core.json` | `research` | top-level | (top level) | Research |
| 11 | `operations` | Operations | `core.json` | `management` | door | (is a door) | Operations |
| 12 | `strategic` | Strategic | `core.json` | `strategic` | door | (is a door) | Strategic |
| 13 | `travel` | Travel & Conferences | `core.json` | `research` | door | (is a door) | Travel |
| 14 | `financing` | Financing | `core.json` | `influence` | door | (is a door) | Funding (merged) |
| 15 | `office` | Office | `core.json` | `management` | door | (is a door) | Operations (merged) |
| 16 | `scouting` | Scouting | `core.json` | `influence` | door | (is a door) | Scouting |
| 17 | `advertise` | Advertise a Role | `core.json` | `hiring` | top-level | (top level) | People |
| 18 | `use_connections` | Work Your Connections | `core.json` | `hiring` | top-level | (top level) | People |
| 19 | `interview_next` | Interview a Candidate | `core.json` | `hiring` | top-level (hidden) | (top level) | People |
| 20 | `hire_best` | Make an Offer | `core.json` | `hiring` | top-level (hidden) | (top level) | People |
| 21 | `onboard_next` | Onboard New Hires | `core.json` | `hiring` | top-level | (top level) | People |
| 22 | `take_loan` | Take Loan | `financing.json` | `financing` | member | financing | Funding |
| 23 | `funding_strings` | Funding (Strings) | `financing.json` | `financing` | member | financing | Funding |
| 24 | `desperation_lever` | Desperation Lever | `financing.json` | `financing` | member | financing | Funding |
| 25 | `staff_rider` | Contractor | `financing.json` | `financing` | member | financing | Funding |
| 26 | `seek_financing` | Seek Financing | `financing.json` | `financing` | member | financing | Funding |
| 27 | `accept_financing_offer` | Accept Offer | `financing.json` | `financing` | member | financing | Funding |
| 28 | `pay_bills` | Pay the Bill | `financing.json` | `financing` | member | financing | Funding |
| 29 | `fundraise_small` | Modest Funding Round | `fundraising.json` | `funding` | member | fundraise | Funding |
| 30 | `fundraise_big` | Major Funding Round | `fundraising.json` | `funding` | member | fundraise | Funding |
| 31 | `take_loan` | Business Loan | `fundraising.json` | `funding` | member | fundraise | Funding |
| 32 | `apply_grant` | Research Grant | `fundraising.json` | `funding` | member | fundraise | Funding |
| 33 | `hire_safety_researcher` | Safety Researcher | `hiring.json` | `hiring` | member | hire_staff | People |
| 34 | `hire_capability_researcher` | Capability Researcher | `hiring.json` | `hiring` | member | hire_staff | People |
| 35 | `hire_compute_engineer` | Compute Engineer | `hiring.json` | `hiring` | member | hire_staff | People |
| 36 | `hire_manager` | Manager | `hiring.json` | `hiring` | member | hire_staff | People |
| 37 | `hire_ethicist` | AI Ethicist | `hiring.json` | `hiring` | member | hire_staff | People |
| 38 | `hire_interpretability_researcher` | Interpretability Researcher | `hiring.json` | `hiring` | member | hire_staff | People |
| 39 | `hire_alignment_researcher` | Alignment Researcher | `hiring.json` | `hiring` | member | hire_staff | People |
| 40 | `tour_offices` | Tour Offices | `office.json` | `office` | member | office | Operations |
| 41 | `sign_lease_coworking_corner` | Sign: Co-working corner | `office.json` | `office` | member | office | Operations |
| 42 | `sign_lease_walkup_office` | Sign: Walk-up office | `office.json` | `office` | member | office | Operations |
| 43 | `sign_lease_university_annex` | Sign: University annex | `office.json` | `office` | member | office | Operations |
| 44 | `order_supplies` | Order Office Supplies | `operations.json` | `operations` | member | operations | Operations |
| 45 | `office_maintenance` | Office Maintenance | `operations.json` | `operations` | member (hidden) | operations | Operations |
| 46 | `audit_self_directed` | Audit Self-Directed Work | `operations.json` | `operations` | member | operations | Operations |
| 47 | `network` | Networking | `publicity.json` | `influence` | member | publicity | Publicity |
| 48 | `media_campaign` | Media Campaign | `publicity.json` | `influence` | member | publicity | Publicity |
| 49 | `lobby_government` | Lobby Government | `publicity.json` | `influence` | member | publicity | Publicity |
| 50 | `release_warning` | Public Warning | `publicity.json` | `influence` | member | publicity | Publicity |
| 51 | `open_source_release` | Open Source Tools | `publicity.json` | `influence` | member | publicity | Publicity |
| 52 | `scout_read` | Read the Literature | `scouting.json` | `scouting` | member | scouting | Scouting |
| 53 | `scout_meetups` | Go to Meetups | `scouting.json` | `scouting` | member | scouting | Scouting |
| 54 | `scout_shitpost` | Post Online | `scouting.json` | `scouting` | member | scouting | Scouting |
| 55 | `acquire_startup` | Acquire Startup | `strategic.json` | `strategic` | member | strategic | Strategic |
| 56 | `sabotage_competitor` | Corporate Espionage | `strategic.json` | `strategic` | member | strategic | Strategic |
| 57 | `emergency_pivot` | Emergency Pivot | `strategic.json` | `strategic` | member | strategic | Strategic |
| 58 | `grant_proposal` | Grant Proposal | `strategic.json` | `strategic` | member | strategic | Strategic |
| 59 | `submit_paper` | Submit Paper | `travel.json` | `travel` | member | travel | Travel |
| 60 | `attend_conference` | Attend Conference | `travel.json` | `travel` | member | travel | Travel |
| 61 | `attend_conference_trip` | Attend Conference (trip) | `travel.json` | `travel` | member | travel | Travel |
| 62 | `send_delegation` | Send Delegation | `travel.json` | `travel` | member | travel | Travel |

## Doors today

| Door id | Door category | Members file | Members | Member categories | Builder |
|---|---|---|---|---|---|
| `hire_staff` | `hiring` | `hiring.json` | 7 | `hiring` | bespoke |
| `fundraise` | `funding` | `fundraising.json` | 4 | `funding` | GRID_CONFIG |
| `publicity` | `influence` | `publicity.json` | 5 | `influence` | GRID_CONFIG |
| `operations` | `management` | `operations.json` | 3 | `operations` | GRID_CONFIG |
| `strategic` | `strategic` | `strategic.json` | 4 | `strategic` | GRID_CONFIG |
| `travel` | `research` | `travel.json` | 4 | `travel` | bespoke |
| `financing` | `influence` | `financing.json` | 7 | `financing` | bespoke |
| `office` | `management` | `office.json` | 4 | `office` | GRID_CONFIG |
| `scouting` | `influence` | `scouting.json` | 3 | `scouting` | GRID_CONFIG |

Action bar `category_order` (the render groups): `funding`, `hiring`, `resources`, `research`, `management`, `influence`, `strategic`, `other`.
