# UI architecture: what is top-level, what is nested, and the rule that decides

- **Status:** PROPOSED (design, no code) -- commissioned 2026-08-06 after Pip's
  "do we have an overall ui architecture sweep planned?" (post-#1130, and the
  voice memos in #1132)
- **Companion:** a fresh-eyes teardown is running in parallel; this is the
  structural half
- **Inputs read:** `godot/data/actions/*.json` (all 12 files),
  `action_bar_renderer.gd`, `submenu_controller.gd` (GRID_CONFIG),
  `docs/design/NAVIGATION_AUDIT.md` (PR #1120 branch, P1-P7),
  `UI_ESCAPE_CONTRACT.md`, ADR-0009, ADR-0012, issues #798 #1043 #1090 #1125
  #1132, PR #1130

## A correction to the commission's numbers, first

The brief says "64 actions ... risk_contributions 2". Measured directly:
`risk_contributions.json` contains ZERO actions -- it is a per-action risk-pool
contribution table (`_description` says so; its top-level keys are
`_description` and `contributions`). The real inventory is **62 entries**:

```
core 20 | financing 7 | hiring 7 | publicity 5 | fundraising 4
office 4 | strategic 4 | travel 4 | operations 3 | scouting 3 | command 1
```

Of those 62: **9 are already submenu DOORS** (`is_submenu: true` in core.json:
hire_staff, fundraise, publicity, operations, strategic, travel, financing,
office, scouting), **1 is a command** (`pass`, not a bar tile), **3 are hidden
from the bar** (interview_next, hire_best, office_maintenance), and the other
files are those doors' contents. So the architecture is not being invented --
a two-layer structure half-exists. What is missing is the RULE that says which
layer a thing belongs to, and anything enforcing it.

Two data defects found while counting, both invisible today:

- **`take_loan` is defined twice** -- once in `fundraising.json` (category
  `funding`) and once in `financing.json` (category `financing`). Whichever
  loads last wins silently. Same class as the `fundraise` mis-tag.
- **`grant_proposal` (strategic.json) and `apply_grant` (fundraising.json)**
  are near-duplicates: same risk-pool source (`diversified_funding`, -3.0
  financial_exposure), similar costs, two different menus. Two doors selling
  the same verb.

---

## Part A -- the rule

> **An action is TOP-LEVEL if and only if it is the single door to a system
> the player steers when composing an ordinary month's plan -- something that
> competes with the OTHER top-level tiles for this month's attention budget.
> Anything that competes only with its own siblings -- a variant, a step, or a
> target of a door's verb -- is NESTED behind that door.**

The operational test is **"what does this action compete with?"** You choose
BETWEEN fundraise-small and fundraise-big, but you choose fundraising ITSELF
against hiring, research, and publicity. The first choice is intra-door; the
second is the monthly plan. The menu tree should be the decision tree.

### Why this rule, from the game

ADR-0009 makes the turn a MONTH and the plan phase the place where the player
"allocates staff and founder hours, queues strategic actions, explicitly sets
reserve". The top of the Plan screen is therefore not a list of everything the
player CAN do -- it is the **vocabulary of the monthly plan**: one tile per
lever the player weighs every single month against `attention_per_month = 20`
(game_state.gd:81). A lever you weigh monthly must be one click away; a
variant you only reach after committing to a lever costs nothing by being one
click further, because by the time you want it you already know why you came.

This is also why Pip's cap-of-10 (#1132: "no more than 10 buttons along the
top ... including how many buttons we want to have unlocked in total, so we
can kind of lock ourselves into a UI width") is a GAME constraint wearing a UI
costume: if the rule ever produces an 11th door, the game has grown an 11th
steerable system, and that -- not the pixel width -- is the thing to
interrogate. The rule below produces **9 doors**, so the cap holds with one
slot spare for a future epoch (alliances/governance, ADR-0007 territory).

### The candidate axes, and why they lose to the competition test

- **Frequency of use** -- correlated but wrong on its own: fundraise_small is
  used constantly and still belongs nested (it competes with fundraise_big,
  not with hiring). Frequency promotes popular VARIANTS; the test promotes
  levers.
- **Economic enabler** -- fails both directions: loans are enablers and belong
  in a desperation drawer; team_building enables nothing and is still a
  monthly people-lever consideration.
- **Reversibility** -- orthogonal to reach. Office leases are the least
  reversible actions in the game and are correctly the most nested (you sign
  maybe three leases per run).
- **New player needs it in the first ten turns** -- necessary but not
  sufficient; onboarding is needed in turn 2 and is still a STEP of hiring
  (#1132 rules exactly this). The early-need axis is served by badges on
  doors (below), not by promotion.
- **Belongs to a phase** -- phase-bound actions do tend to nest (leases,
  desperation levers), but Strategic is phase-gated AND a door. Phase predicts
  nesting only via the competition test (phase-bound things rarely compete
  monthly), so use the test directly.

The competition test subsumes the useful residue of all five.

---

## Part B -- the 62 entries, sorted

### The nine doors (top level, fixed digit slots)

| Slot | Door | Hotkey | Members (count) | Unlock |
|---|---|---|---|---|
| 1 | Funding | F | fundraise_small, fundraise_big, apply_grant, take_loan (dedup), funding_strings, desperation_lever, staff_rider, seek_financing, accept_financing_offer, pay_bills (10) | turn 1 |
| 2 | People | H | 7 hire_* roles, advertise, use_connections, interview_next, hire_best, onboard_next, team_building (13) | turn 1 |
| 3 | Research | R | safety_research, capability_research, publish_paper, audit_safety (4) | turn 1 |
| 4 | Compute | -- | buy_compute (1 now; #798's submenu when it lands) | turn 1 |
| 5 | Publicity | P | network, media_campaign, lobby_government, release_warning, open_source_release (5) | turn 1 |
| 6 | Scouting | -- | scout_read, scout_meetups, scout_shitpost (3) | turn 1 |
| 7 | Travel | T | submit_paper, attend_conference, attend_conference_trip, send_delegation (4) | turn 1 |
| 8 | Operations | -- | order_supplies, audit_self_directed, tour_offices, 3x sign_lease_*, (office_maintenance stays retired) (7) | turn 1 |
| 9 | Strategic | -- | acquire_startup, sabotage_competitor, emergency_pivot, grant_proposal (4) | turn 10 + rep 30 |
| 0 | (reserved) | -- | future system, deliberately empty | -- |

Members: 52. Doors: 9 (the current 9 door records, with `financing` and
`office` retired as separate doors -- merged into Funding and Operations).
Command: `pass` stays a Plan-screen control, not a tile. 52 + 9 + 1 = 62.

Turn-1 top level: **8 tiles** (Strategic hidden until its unlock -- Action
Discovery behavior kept, slot 9 stays reserved so nothing renumbers when it
appears; the #1089 fanfare announces it). All-unlocked: **9**. Both under
Pip's 10.

What this changes versus today's 15-tile hand: the six loose core actions
(advertise, use_connections, onboard_next, team_building, audit_safety,
buy_compute-as-plain-tile) fold into doors; financing and office merge into
Funding and Operations. #1132's three named misplacements (use_connections,
onboarding, and the cap itself) fall out of the rule rather than being
patched.

### Where the rule produces results I distrust -- evidence about the rule

1. **Safety vs capability research is buried one level down.** This is the
   game's central thematic tension, and the rule files it as two variants of a
   Research door because they compete with each other, not with fundraising.
   The rule is optimizing reach-structure and is blind to thematic salience.
   Two mitigations, pick at the workshop: (a) the Research door's tile face
   shows the current allocation (a door with state, not a blank folder); (b)
   the door opens an ALLOCATION panel rather than a verb list -- which is
   where #1090 (research quality becomes project-level, per Pip's ruling) is
   heading anyway. I lean (b): the rule's "wrong" answer here is accidentally
   the right shape for where research is going. But this is the weakest
   corner of the sort and I flag it as such.
2. **Compute as a one-member door diverges from #798**, which asked for
   buy_compute "under one of the operations-style submenus". I am
   contradicting the issue deliberately: compute is a strategic input bought
   nearly every mid-game month (an enabler the player weighs against research
   and hiring), while operations is housekeeping; hiding an enabler behind
   housekeeping repeats the fundraise-below-the-fold mistake at one level
   deeper. #798 is ABSORBED rather than rejected: its real ask is "compute
   deserves a grouped submenu", and the Compute door is that submenu's home.
   If Pip reads #798 literally, folding Compute into Operations costs one
   line in the taxonomy map and drops the top level to 8 -- cheap either way.
3. **pay_bills under Funding smells wrong.** Paying bills is an obligation,
   not a funding strategy. The rule places it by competition ("how do I move
   money this month") but ADR-0013's direction (every mitigation is a loan;
   ledger cascade) suggests bills may belong to the Ledger surface or to
   automation, not to the action menu at all. Flagged for the workshop, left
   in Funding meanwhile.
4. **grant_proposal vs apply_grant** -- the duplicate named above. The rule
   cannot place one verb in two doors; the mechanics owner should merge them
   (or differentiate them for real). Until then grant_proposal stays in
   Strategic so the sort is honest about today's data.
5. **Travel is the weakest door.** Four phase-bound items; raw frequency says
   nest it. It keeps its door on ADR-0014's presence economy (conferences are
   a system, not a variant of publicity). If a real 10th system ever arrives,
   Travel folds into Publicity ("Presence") first. Named now so that future
   squeeze is a lookup, not a debate.
6. **onboard_next nests even though it is urgent in turn 2.** The rule is
   right (it is a step of hiring, #1132 agrees) but the urgency must not be
   lost: the People door carries a pending-count badge ("2 waiting") when
   onboarding or offers are outstanding. This is the pain/payoff heuristic --
   the game surfaces earned state instead of making the player rummage.

---

## Part C -- the grouping mechanism

**One mechanism: the modal submenu panel that already exists** (SubmenuChrome
frame + SubmenuController grid/sectioned-list), opened by tile click, by the
door's digit, or by the legacy letter hotkeys -- all three through the single
`MainUI._open_submenu` (P1's "both doors call ONE function"). No tabs, no
expanding trays, no second mechanism: every navigation defect in the audit
came from surfaces that each did keys their own way, and the grid/list panels
are the surface that PASSED. Merges reuse GRID_CONFIG entries (a merged panel
is "one panel, two sections", which the financing list builder already proves
out).

Judged against the principles:

- **P1 (nothing hotkey-only):** doors are visible tiles; digits and letters
  are accelerators. Holds.
- **P2 (a key that opens closes):** extended to digits -- pressing an open
  door's OWN digit closes it, same mirrored-toggle semantics as H/F/P/T/L,
  identity read from `submenu_id` meta as today. While a door panel is up,
  OTHER digits are consumed and do nothing (P2's existing "a hotkey can never
  stomp the panel the player is looking at").
- **P3 (choice keys render what they route):** inside a panel, members answer
  to the advertised letters `Q W E R A S D F Z` via `dialog_keys.gd`,
  unchanged. One deliberate change: the UNADVERTISED digit alias inside door
  panels is retired (digits now mean doors); it survives inside EVENT dialogs,
  which have no door digit to conflict with. `test_dialog_key_routing.gd`
  changes with this and must be watched fail first.
- **P5 (ESC exactly one level):** panel -> top; picker -> panel. Holds.
- **P6/P7:** untouched.

### The number-key problem (the hard part)

Nesting breaks a flat 1-9 mapping twice over: items move between levels, and
today's badges are INDEX-ordered, so every unlock renumbers everything after
it -- muscle memory is impossible even without nesting. The fix is the same
for both:

> **A digit is a NAME, not a position.** Each door owns one digit for the
> whole run (the table in Part B). Locked doors keep their slot empty;
> unlocks fill a reserved slot and renumber nothing. Members answer to
> letters. Every one of the 62 actions is at most two keystrokes:
> `digit, letter` (e.g. `1 Q` = small fundraise; `2 W` = second candidate's
> primary hiring step).

The cap-of-10 is what makes this POSSIBLE: 1-9 plus 0 is exactly ten names.
Pip's "lock ourselves into a UI width" is equally "lock ourselves into the
digit row". This grammar also survives the (already-live) `action_1..9`
rebindable binds -- they rebind door names now, which is strictly more useful
to rebind than positions.

**Depth invariant: two menus, then at most one picker.** No door may contain
a door. A member may end in a parameter picker (travel's destination
sub-dialog, a candidate card's confirm) but never a third menu of verbs.
Travel's current sub-dialog routing sits exactly at this line; the taxonomy
check pins it there.

Single-member doors (Compute until #798 lands) still open a panel rather than
firing directly -- consistency of the grammar over one saved keystroke; the
panel is also where the submenu's cost/gain context lives.

---

## Part D -- keeping the taxonomy honest

The `fundraise` mis-tag shipped because `category` was a sort key with no
checker: the failure was a rendering position, not a red test. The `take_loan`
duplicate is the same class, still live. Guard, in this repo's established
pattern (generated index + check that was watched fail, per DQ_INDEX /
ADR-0017):

1. **One placement SSOT:** a small `godot/data/actions/taxonomy.json` --
   door list, each door's fixed digit slot, hotkey letter, member categories
   and/or member files, unlock gate. The renderer's `category_order`,
   GRID_CONFIG's id list, and core.json's `is_submenu` flags all become
   things the checker RECONCILES against it, instead of four places that can
   drift (today placement lives in: the category field, category_order,
   GRID_CONFIG keys, and which file an action sits in).
2. **Generated index:** `scripts/generate_action_taxonomy.py` emits
   `docs/design/ACTION_TAXONOMY.md` (GENERATED, never hand-edit) -- the full
   door/member table with counts; pre-commit runs `--check` so a stale index
   blocks, exactly like `generate_dq_index.py`.
3. **GUT test `godot/tests/unit/test_action_taxonomy.gd`** asserting, against
   the REAL loaded action defs:
   - every action id is UNIQUE across all files (fails TODAY on take_loan --
     the red-first proof comes free);
   - every `category` is in the known set (fails on a re-introduced
     `fundraise: management` fixture);
   - every non-hidden action is a door or a member of EXACTLY one door --
     no orphans, no double-placement;
   - the all-unlocked door count is <= 10 and each door's slot digit is
     unique (Pip's cap, executable);
   - every `is_submenu` id has a builder (GRID_CONFIG entry or documented
     bespoke) -- pins the `push_warning("unknown submenu id")` hole shut;
   - depth: no member of a door is itself `is_submenu`.
4. **Geometry stays separate:** `test_action_visibility.gd` (from #1130)
   keeps owning "the hand fits above the fold at 1080p"; the taxonomy test
   owns structure. Two failure modes, two tests.

Cap enforcement ratchets: the check first lands asserting the MEASURED
current value (so it is green and true), then tightens per phase below --
never a threshold the tree does not actually meet, which is how checks go
hollow.

---

## Part E -- sequencing

- **Phase 0 -- measure (half a day). Lands first.** Taxonomy checker +
  generated index in REPORT-ONLY. It fails on take_loan immediately, which is
  the red-first proof and a real bug found. No player-visible change, no
  workshop needed.
- **Phase 1 -- the hiring fold (a day).** advertise, use_connections,
  onboard_next, team_building into the People door (the hiring panel already
  has the candidate-card pipeline; these join it). This is #1132's explicit
  ruling, so no new decision from Pip is required. Hand: 15 -> 11. Add the
  People-door pending badge.
- **Phase 2 -- merges + digit grammar (1-2 days).** Funding absorbs
  financing (sectioned list; F hotkey unchanged); Operations absorbs office
  (also kills #1132's shared-icon collision for free); fixed digit slots +
  digit-toggle-close; retire the digit alias inside door panels
  (test_dialog_key_routing updated, watched fail first). Checker flips to
  BLOCKING with cap <= 10 for doors; interim loose-action count asserted at
  its measured value. Hand: 8 turn-1 tiles + 3 loose research tiles +
  compute = 12 all-unlocked. Honest note: the cap is NOT met yet at
  all-unlocked after phase 2; the ratchet records 12.
- **Phase 3 -- the Research door (workshop FIRST, then ~2-3 days).** Folding
  safety/capability/publish/audit needs Pip's call on Part B item 1 (verb
  list vs allocation panel), and it is entangled with #1090's project-level
  quality ruling. Do not build ahead of that workshop -- it is the one place
  this design touches the game's thematic core. After it: all-unlocked = 9,
  cap check tightens to 10, done.
- **Phase 4 -- NOT this workstream.** #1043 (Plan screen's dead middle,
  persistent-across-screens columns) stays its own workshop; this
  architecture is an INPUT to it (a 1-row bar frees vertical space and the
  right-hand action-log idea from #1132 wants the middle), not a solution.

Total: about a week of build spread over phases, with exactly one decision
gate (phase 3) needing Pip in a room. Phases 0-2 are safe to run now and
deliver Pip's cap-10 instinct for the opening hand within two days.

---

## Part F -- what this does NOT solve

This design decides REACHABILITY STRUCTURE: what is one keystroke away, what
is two, and what enforces that. Open UI issues that look adjacent but have
different generators:

- **Instant resolution / no tempo (#1044) and "money disappears with no
  feedback" (#1132 item 5).** Generator: actions resolve in zero sim time,
  violating ADR-0009's duration rule. No menu tree fixes a missing action
  log or missing durations. The right-panel action log belongs to #1043's
  workshop.
- **Mouse-over jiggle (#1132 item 1).** Generator: per-component hover
  styling re-laying-out containers -- a regression of a previously solved
  problem, which per #1132 means the fix lived in a component instead of a
  shared rule. That shared rule (hover must never change a control's size)
  is a style-guide/theme_manager item, not taxonomy.
- **Month review "still needs some work" (#1132 item 6) and #1043's dead
  middle** -- screen-content design, deliberately left to their workshop.
- **F3 event injection permalocking a run (#1134) and the dev-vs-alpha tool
  boundary (#1112).** Generator: dev tools bypassing phase guards.
- **Research Quality dead text block (#1090)** -- adjacent (phase 3 is its
  natural landing), but its generator is a mechanics ruling not yet
  implemented, not menu structure.
- **Rivals unintroduced (#1088), fanfare-on-black (#1089), onboarding-by-
  silence (#1091)** -- presentation and mechanics-surfacing of EVENTS
  (ADR-0012 territory), not of the action menu. The fixed Strategic slot
  gives #1089's fanfare a stable target, nothing more.
- **Placeholder sentinels (#1031), stale AP nomenclature (#1037), non-ASCII
  in .tscn (#1035)** -- copy/content hygiene with their own checkers.
- **Local/Global toggle silent unpress (#1126), Duration column (#1062),
  play-again dead end (#1064), first-screen naming (#1063)** -- leaderboard
  and meta-screens, outside the Plan-screen action surface entirely.

And one boundary worth stating: this rule governs the ACTION hand. Upgrades,
the event feed, the ledger, and the top-bar instruments are separate surfaces
with their own (currently unwritten) rules; if the competition test earns its
keep here, the upgrades column is the next place to apply it, but that is a
claim to test, not a decision this document makes.
