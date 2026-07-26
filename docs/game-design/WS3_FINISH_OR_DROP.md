# WS-3 finish-or-drop: the four unbuilt WS-2 ADRs

> Status: DECISION PREP for W-3a (Mon 2026-07-27) -- the opening RATIFY BLOCK
> of the three-day W-3 structure (Mon W-3a / Tue build day / Wed W-3b-W-4;
> restructured 2026-07-26, see `WORKSHOP_3_PREP.md` + the runsheet). Drafted
> 2026-07-25 by a research agent at Pip's request. Companion to
> `WORKSHOP_3_PREP.md` Section 2
> (Decision-for-Pip 2A/2B) -- this doc turns "finish or formally drop the unbuilt
> WS-2 ADRs" into five ratify-in-minutes questions.
>
> Every "built / not built" claim below was RE-VERIFIED against current
> origin/main by grepping `godot/scripts`, `godot/autoload`, `godot/data`,
> `godot/tests` on 2026-07-25 -- not inherited from the prep doc. File:line refs
> are to that tree. Judgements and sizes are marked [INFERRED] where they are
> design calls rather than code facts.
>
> Lane-number correction (verified via `gh`): L2 = #613 (effort economy),
> **L3 = #614 (adoption, papers, conferences -- ADR-0010 + ADR-0014)**,
> L4 = #615 (event taxonomy). `WORKSHOP_3_PREP.md` says "lane L3 (#615)" in two
> rows -- that mapping is wrong; all three lanes are OPEN.

---

## 0. The five decisions (the ratify block)

Pip: each row is one call. Defaults are the agent's recommendation; overriding
any of them is fine, but leaving a row undecided re-creates the rot this doc
exists to stop (accepted-but-unbuilt ADRs silently shaping new design).

| # | ADR | Recommendation (default) | The one-line question for Pip |
|---|-----|--------------------------|-------------------------------|
| 1 | 0010 adoption routing | **Downscope-then-finish** (v1 teeth in L3/#614) | Ratify the v1 downscope: partition `safety_absorption` to the player frontier only + adoption-credit -> typed dampers; park the counterparty model? |
| 2 | 0011 effort economy (remainder) | **Downscope-then-finish** (MINIMAL now, MODERATE = scheduled L2; defer manager-shields + founder-hour typing inside the lane) | Ratify MINIMAL as a fast-follow and MODERATE as the L2 milestone -- and explicitly sequence manager-shields/hour-typing BEHIND both? |
| 3 | 0014 conferences ADR-shape | **Downscope-then-finish, sequenced AFTER 0010-v1** (attendance+yields only; subgame stays parked) | Ratify: no conference build until adoption-v1 exists to accelerate; then only the attendance/delegate/contacts v1? |
| 4 | 0016 league metabolism | **Downscope-then-finish as ops**: define the pack format + run ONE manual league cycle; automate later | Which month runs the first real league cycle -- v0.13 epoch or public launch -- and is manual-pack-first ratified? |
| 5 | 0015 data-strip trap | **Schedule the strip as an S errand** (do not ratify "inert but present") | Approve a one-lane data errand: strip/re-author ~66 literal doom fields + fix the "-N doom" fiction strings? |

None of the four is recommended for **formally-drop**. Reasoning per ADR below;
the honest drop candidate was 0014, and even there the ADR's *shape* costs
nothing to keep while its build is explicitly sequenced behind 0010.
[INFERRED -- design judgement throughout the recommendation column.]

---

## 1. ADR-0010 -- Adoption routing (soft-with-teeth)

**Decided (2026-07-12):** world/rival doom -- the majority share -- bends ONLY
through research -> paper -> socialization -> adoption; your own lab's doom
contribution stays privately fixable. Purpose: kill the basement-safety-spam
dominant line *by construction*, and encode Pip's real theory of change
("norm and market setting" by small/middle powers).

**Verified state -- MOSTLY NOT BUILT, and the current stream shape actively
contradicts the ADR's core partition:**

- BUILT: the ADR-0015 stream engine gives adoption a clean landing site.
  `doom_system.gd:284-313` already supports **typed dampers** whose docstring
  names "adopted safety work" as a grantor (`:306`), and scheduled pulses --
  both wired, zero content. `add_stream_input()` (`:319-332`) is the
  single-authority intake.
- BUILT (adjacent): papers exist (two disconnected paths -- see ADR-0011 below);
  conferences exist in pre-ADR #468 shape; presenting a safety paper routes
  through `global_alarm` not printed doom (`actions.gd:840-842`).
- NOT BUILT: no adoption object, roll, credit, or pipeline anywhere in
  `godot/scripts` -- "adopt" greps to the office cat event and comments only.
  No per-person/per-org typed reputation (scalar `state.reputation` only).
- **CONTRADICTION (the key verified finding):** the overhang stream is
  `W_frontier * max(0, frontier_max - safety_absorption)` where `frontier_max`
  is the max over ALL actors *including rivals* (`doom_system.gd:259-263`), and
  `safety_absorption` is raised by your own private safety researchers
  (`doom_system.gd:211`, `actions.gd:324-329`). So basement safety work still
  directly offsets the rival-driven world hazard -- the exact reach ADR-0010
  exists to remove. The teeth are not merely missing; the current shape is the
  rejected "status quo" alternative, re-denominated into streams. Whether the
  line is currently *dominant* is a balance question for the sweep; the
  structural availability is a code fact.

**Effort to FINISH: L full / M downscoped.** Full = adoption counterparty model
(overlaps ADR-0007/DQ-9) + typed rep + socialization chain + sweep verification.
Downscoped v1 = (a) split absorption: own `safety_absorption` offsets only
`frontier_capability["player"]`; (b) published+socialized safety work accrues
an adoption credit that mints typed dampers on the world streams via the
existing `doom_dampers` hook; (c) sweep target: publish-and-socialize must beat
basement-spam. Rides the existing stream engine, no new engine system.
[INFERRED sizing]

**RECOMMENDATION: downscope-then-finish (v1 in L3/#614).** This is a thesis
pillar twice over: it is the structural kill for the sweep's dominant line
(no payoff tuning can substitute -- ADR-0010's own argument), and it is the
game's honesty claim (Rams #6: the mechanic IS Pip's theory of change).
Dropping it means re-accepting the degenerate line and deleting the
norm-setting thesis; that is not a scope cut, it is a different game.
The counterparty/typed-rep superstructure is the part that can wait.

**WS-3 must DECIDE:** ratify the v1 downscope above (absorption partition +
adoption-credit-to-dampers, counterparty model parked to the DQ-9/ADR-0007
beat), and name the sweep gate that proves the teeth. Secondary: does the
absorption partition ship in the same version bump as the ADR-0011 MINIMAL
(both fork the ladder -- batching them is one fork instead of two)? [INFERRED]

---

## 2. ADR-0011 -- Effort economy (the unbuilt remainder)

**Decided (2026-07-12):** delete the global AP pool; founder hours typed as
doors/approvals/audits/reserve; staff effort per-person, assigned at plan speed
to multi-month WORKSTREAMS from a backlog; managers as interrupt shields with a
Celine's-law reporting channel; researcher = lane x appetites x quirks, with
retention promises as ledger entries.

**Verified state -- PARTIAL; the substrate half is missing:**

- BUILT: lanes/appetites/quirks (`researcher.gd:66-110`, data-driven quirk
  catalogue); appetite-promises minted as ledger obligations
  (`hiring_pipeline.gd:319-344` -> `ledger.gd:127+`); the Attention currency
  with crisp evaporating reserve (`month_plan.gd` -- ADR-0009's L1 layer);
  burnout; the hiring pipeline + reveal ladder.
- NOT BUILT: **workstreams** -- zero code objects; the word appears only in
  comments marking the seam (`month_plan.gd:21` "the seam L2 workstreams
  extend", `game_state.gd:844`). **Founder-hour typing** -- `founder_hour`
  greps to nothing; Attention is a single untyped integer pool. **Manager
  shields** -- `state.managers` is a legacy int giving 9-per-manager capacity
  (`game_state.gd:97,658`, `turn_manager.gd:126`), no window absorption, no
  fidelity-lossy reporting channel. The **legacy AP pool still exists and is
  what actions actually spend** (`game_state.gd:41-42`, costs in
  `data/actions/*.json`) -- the two currencies coexist mid-migration.
- The research->paper substrate is fully diagnosed in
  `RESEARCH_IDEA_PAPER_PIPELINE_GAP.md` (re-verified): research is an
  undirected per-turn RNG drip into one fungible scalar
  (`turn_manager.gd:178-236`); a "paper" is either a counter increment
  (`turn_manager.gd:484-491`, `state.papers += research/100`) or a
  player-labelled `PaperSubmission` whose topic is a last-second dropdown
  decoupled from the work (`actions.gd:724-778`). No Idea object, no
  assignment verb. Links 2/4/5 of the promised chain are fiction.

**Effort to FINISH: L overall, cleanly laddered.** MINIMAL (per-researcher
`focus_topic` + topic-tagged accrual + idea-carrying papers) = **S**, days,
already scoped as the seam toward MODERATE. MODERATE (Workstream object +
assignment UI + agenda drift -- the real L2 build) = **L**, weeks, gated on the
plan-screen work (MAIN_UI_SEAM_MAP CARVE 1) and DQ-15 archetypes.
Manager-shields + founder-hour typing = **M each**, on top. [Sizing per the
gap doc, spot-checked against the code seams.]

**RECOMMENDATION: downscope-then-finish -- and do NOT re-litigate.** This is
the biggest single drag and the most load-bearing of the four: the fungible
scalar IS the diagnosed constant-policy exploit, and the workstream substrate
is what makes the appetite/promise/ledger loop *playable* (today nothing can
feed a first-author appetite because nothing is directable). It also carries
"the sim never lies; characters do" -- the Celine's-law manager channel is that
principle's canonical mechanic, which is an argument for keeping manager-shields
RULED even while sequencing them last. WS-3's job here is scheduling, not
design: the ladder already exists and MODERATE is already ACCEPTED.

**WS-3 must DECIDE:** (a) ratify MINIMAL as a fast-follow (own version bump --
it forks the ladder) and MODERATE as the L2/#613 milestone; (b) explicitly
sequence manager-shields and founder-hour typing BEHIND MODERATE inside the
lane (still ruled, not v1); (c) name the AP->Attention migration endpoint --
when does `action_points` die? Leaving two currencies indefinitely is the same
mid-migration rot this doc targets. [INFERRED on (c)]

---

## 3. ADR-0014 -- Conferences, presence, minimal location

**Decided (2026-07-12):** conferences are seed-timeline scheduled world events
(9-month announcements, invitation-gated smaller gatherings); founder
attendance >> delegate attendance (founder-hours + cash vs staff-month + cash);
conferences accelerate adoption and mint contacts-as-receivables; presence is
an SA channel; location minimal (`where` field, overseas basing later).

**Verified state -- NOT BUILT in ADR shape; only the pre-ADR #468 system:**

- EXISTS (pre-ADR): `conferences.gd` -- a hardcoded annual conference list with
  static month-of-year, travel-cost tables, and a per-conference
  `doom_reduction` field (`:37,55,119+`); `paper_submissions.gd` -- the
  submit/review/present lifecycle; `attend_conference_action`
  (`actions.gd:795-870`) with jet lag (#469). Presenting now routes through
  `global_alarm` rather than printed doom (`actions.gd:840-842`) -- though the
  player-facing message still says "-N doom" (`:847`), a Section-5 item.
- STUBBED: the actual travel actions the player would use are `is_stub: true`
  "[Coming Soon]" entries (`data/actions/travel.json:15-31` -- attend
  conference, send delegation). Only submit-paper is live.
- NOT BUILT: seed-timeline scheduling (the ADR-0005 pulse hook at
  `doom_system.gd:297-302` ships "no pulse content"); founder-vs-delegate
  distinction (no founder-hours to spend -- see ADR-0011); invitation gating;
  contacts-as-receivables (the Ledger has the RECEIVABLE side + counterparty
  field, `ledger.gd:16,30`, but nothing mints contacts); presence-as-SA.

**Effort to FINISH: L full / M downscoped.** The v1 the ADR itself scoped
(attendance + yields, subgame parked) needs: conferences as schedule entries,
two attendance verbs with real costs, adoption-accelerant multiplier, contact
minting into the existing receivable slot. Most of its dependencies are the
OTHER two lanes: founder-hours (0011) and an adoption pipeline to accelerate
(0010). [INFERRED sizing]

**RECOMMENDATION: downscope-then-finish, explicitly SEQUENCED AFTER 0010-v1.**
This is the weakest finish-now case of the four: conferences are an
*accelerant* on adoption, not the adoption roll itself (the ADR's own ruling)
-- so building them before adoption-v1 exists would be polishing the middle of
a chain whose end is missing. But formally dropping the ADR-shape would strand
ADR-0010 (socialization is its mandatory middle) and waste the already-built
#468 lifecycle underneath. The cheap, honest position: keep the ADR ACCEPTED,
gate its build on adoption-v1 landing, and hold the v1 scope line (no subgame,
no foreign law). If Pip wants a real drop candidate, the droppable piece is
the *invitation-gated exclusive event stream* -- defer to the DQ-22 rivals/
midgame workshop where it has a consumer. [INFERRED]

**WS-3 must DECIDE:** ratify "no conference build until adoption-v1 exists to
accelerate", and confirm the v1 scope (attendance + delegate + contacts
minting; subgame and invitation stream stay parked). Also: does the stubbed
"[Coming Soon]" travel UI stay visible in v0.13, or hide until the lane lands?
(Visible stubs are a fiction/mechanic gap of the kind #801 flagged.)

---

## 4. ADR-0016 -- League metabolism (monthly world-update packs)

**Decided (2026-07-13):** monthly cycle -- collect real-world events -> author a
world-update pack (ADR-0005 schedule entries, pdoom-data feedstock) -> frontier
advances one month -> new baseline seed -> league launches with notes. 2017
start holds; world-updates decoupled from balance patches; hard ops constraint
of <= 1 day/week founder effort.

**Verified state -- NOT BUILT as a metabolism; the engine-side seams DO exist
(more than the prep doc credits):**

- BUILT (seams): `DEFAULT_START_YEAR = 2017` (`game_state.gd:130`); every run
  artifact is stamped with a `league_id` (`verification_tracker.gd:65-91`,
  placeholder = start-month, `game_manager.gd:80-85`) beside the board/ladder
  version (`GameConfig.get_board_version()` -- the build-vs-ladder split that
  landed as version-split L1); a manual featured-league seed pin
  (`game_config.gd:400-406`, "the metabolic cycle rotates it at Pip's call");
  one year of world content exists as `data/historical_timeline/2017.json`.
- NOT BUILT: everything metabolic. No world-update-pack format, no authoring
  pipeline or tooling (zero hits for world-update/league in `tools/` and
  `scripts/`), no frontier-advance mechanism, no league-notes format, no
  rotation process. `historical_timeline/` contains exactly one file (2017).

**Effort to FINISH: engine S / ops M -- but the real cost is RECURRING.** The
engine barely needs anything (packs are ADR-0005 schedule entries; the pulse
hook is wired). The build is: define the pack format, write one pack, rotate
the seed pin, publish notes. The ADR's own risk register says it: the
sustainability constraint (1 day/week sustained) is the design input, and the
cadence "only pays if the game is public with real players pretty darn soon".
[INFERRED sizing]

**RECOMMENDATION: downscope-then-finish as OPS, manual-first.** Do not drop:
the reality-tether is ~75%-ruled canon and is the game's identity claim (the
third structural pillar candidate). But do not build automation for a league
with no public players either -- that is liveops decay in advance. The
downscope: (a) WS-3 ratifies the pack FORMAT (a schema + one worked example,
S); (b) the first real cycle runs MANUALLY (Pip + an agent draft, ~1-2 days),
pinned to a named month; (c) automation/tooling waits for evidence of monthly
engagement. The monthly release train (ROADMAP) already gives it a heartbeat
to ride.

**WS-3 must DECIDE:** the date question -- does the first real league cycle run
at the v0.13 epoch or at public launch? And ratify manual-pack-first. One
format constraint to ratify while deciding: **packs must be born clean of
printed doom** -- see Section 5; `2017.json` (the de-facto pack template)
currently carries literal doom fields, and a pack pipeline that inherits that
schema propagates the trap into every monthly drop.

---

## 5. The ADR-0015 data-strip trap (Decision 2B companion)

**What ADR-0015 decided:** no definition carries literal doom; effects write
intermediaries; `DoomSystem` is the single authority (LANDED as an engine --
`doom_system.gd:1-27`, #638).

**Verified residue -- bigger than the prep doc's "~40 fields":** literal
`"doom": N` effect fields in shipped content, inert ONLY because the resolve
path clobbers them:

- `data/events/core_events.json` -- 40
- `data/events/risk_events.json` -- 20 (not counted by the prep doc)
- `data/historical_timeline/2017.json` -- 4 (the ADR-0016 pack template!)
- `data/scenarios/crisis.json` -- 2 effect fields (start-config doom is fine)
- plus `data/events/balancing/variable_mapping.json` maps external pdoom-data
  variables ("stress", "vibey_doom", ...) onto the doom sink
  (`resource_accessor.gd:86-94`) -- the ingest path for ADR-0016 packs.

The clobber itself is explicit and commented: `resource_accessor.gd:73-77`
("event-content doom sink. Clobbered by doom resolution in the real loop
(inert no-op)") and `game_state.gd:381-382`. Any refactor that drops that
clobber silently resurrects printed doom with zero test failures [INFERRED --
no test asserts the clobber; worth one property test either way]. The fiction
layer also still SAYS printed doom: event messages ("-3 reputation, +2 doom" in
`risk_events.json:14`) and the conference message (`actions.gd:847` prints
"-N doom" while actually writing `global_alarm`).

**RECOMMENDATION: schedule the strip; do NOT ratify "inert but present".** The
errand is S (re-author ~66 effect fields onto intermediaries or delete them;
fix the message strings; add the guard test), it is content-only on the data
side, and two live workstreams make the latent trap ACTIVE: the ADR-0016 pack
format inherits `2017.json`'s schema, and any L4/#615 event-content lane will
copy existing events as templates. Cheap now, compounding later.

**WS-3 must DECIDE:** approve the S data-strip errand (and whether it rides the
L4 content lane or goes standalone), or explicitly ratify the inert state with
the guard test as the only protection.

---

## 6. Verification notes / corrections to the prep doc

For the record, where this pass diverges from `WORKSHOP_3_PREP.md` Section 2:

1. **Lane mapping:** L3 = #614 (adoption/papers/conferences), L4 = #615 (event
   taxonomy). The prep doc's "Lane L3 (#615)" is wrong in both rows it appears.
2. **ADR-0010:** prep says "MOSTLY NOT BUILT"; verified, plus sharper -- the
   current overhang math (`doom_system.gd:263`) lets private absorption offset
   the rival frontier, i.e. the rejected status-quo shape persists inside the
   new stream engine.
3. **ADR-0014:** prep says "only the pre-ADR #468 travel system exists";
   verified, plus: the player-facing attend/delegate actions are `is_stub`
   placeholders (`travel.json`), and the receivable slot for contacts already
   exists unused (`ledger.gd:16,30`).
4. **ADR-0015:** prep counts "~40 literal fields"; verified count is ~66
   effect fields across four content files, plus the external-variable mapping
   and two player-facing "-N doom" fiction strings.
5. **ADR-0016:** prep says "only the 2017 anchor"; undercounts -- league-id
   stamping, the board/ladder version split, and the manual seed pin all exist,
   which is exactly why the remaining work is ops/content, not engine.
