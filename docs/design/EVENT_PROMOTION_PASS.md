# EVENT PROMOTION PASS -- ranked shortlist, ready to execute

- **Date:** 2026-08-04
- **Ask (Pip):** "a little half hour of promoting some events from different
  timelines will let us work on mechanics a bit and give players a touch more
  variety."
- **Status:** PROPOSAL. No data or code changed. Every mechanical claim below
  was verified against the tree on 2026-08-04; file:line refs are to that tree.
  Assumes the 2026-08-02 audit
  (`docs/decision-cards/2026-08-02_pdoom-data-contract.md`) -- its measured
  findings are used, not re-derived.
- **Deliverable shape:** one new override file
  (`godot/data/events/overrides/promotion_pass_2026_08.json`) plus one edit to
  `godot/data/events/balancing/rarity_curves.json`. Both are pdoom1-owned
  balance files per the contract card. Zero code changes required for the core
  pass; one small optional enabler PR is specified in section 4.

---

## 0. Execution order for the half hour

1. (5 min) **Re-time the corpus**: edit 3 numbers in `rarity_curves.json`
   (section 2). Without this step, 9 of the 13 core promotions never fire.
2. (20 min) **Write the override file**: copy the template in section 6, then
   copy-adapt the Tier A and Tier B entries from the table in section 5.
3. (5 min) **Sanity launch**: `godot --path godot`, new run, confirm the
   console prints the override count and that Tay/Maven windows appear by
   turn ~30. Ship on a release boundary, not mid-league-week (section 7).

---

## 1. BLOCKER FIRST: the time bug re-times this pass; it does not kill it

The contract card measured the mismatch: `rarity_curves.json` says
`turns_per_year: 52`, the Clock runs 1 turn = 1 workday (~260/yr,
`godot/scripts/core/clock.gd:15`), and the code fallback says 12
(`event_service.gd:864`, only used if the JSON is missing). What that means
concretely for firing turns, from `event_service.gd:311-349`:

    base_turn(year) = max(1, (year - 2017) * turns_per_year + 1)
    legendary  -> fires exactly at base_turn + legendary_month_offset (26)
    rare       -> eligible from ~base_turn, rolls 6% per turn
    common     -> eligible from max(10, base_turn), rolls 12% per turn

Measured run lengths: the 2026-07-05 exploit sweep found every policy run
terminated before turn 300 (`docs/qa/EXPLOIT_SWEEP_2026-07-05.md:31`);
Balance's endgame threshold is turn 200 (`godot/data/balance/defaults.json`
`events.endgame_turn`); observed deaths in specimens range turn 14 to 229. So
the playable band is roughly turns 1-250, thinning fast after ~200.

Under the CURRENT 52 turns/year, event years land at:

    year:   2017  2018  2019  2020  2021  2022  2023  2024  2025
    turn:     27    79   131   183   235   287   339   391   443
    (legendary firing turn; rare/common become eligible ~26 turns earlier)

Everything 2022+ is dead or near-dead -- and that is where almost all the good
hand-authored content sits (FTX, board crisis, alignment faking, blackmail: 25
of the 28 hand-authored records are 2022+ or pre-start). A promotion pass that
skips this step produces events nobody sees -- the #1027 signature failure.

**The fix is NOT "make it honest" (260 turns/year).** At calendar-true pacing a
run reaches mid-2018 before it ends; 95% of the corpus becomes unreachable
forever. The design-correct reading: the historical deck is a COMPRESSED ECHO
of the real timeline (the run already spans "2017-2025" of AI history inside
one fictional year), and `turns_per_year` is a pacing dial pdoom1 owns.

**Recommended: compress to 26 turns per year** so the full 2017-2025 arc fits
the observed run band:

    year:   2017  2018  2019  2020  2021  2022  2023  2024  2025
    turn:     14    40    66    92   118   144   170   196   222
    (legendary firing turn at offset 13; see diff in section 6)

2023-2025 beats land in the endgame minority of runs -- acceptable: rare
sightings are variety, and the endgame window budget doubles at turn 200
anyway (`defaults.json` `window_demand_budget_endgame`).

Side effects to accept knowingly:
- The 1,129-line arxiv flavour feed also compresses (each year-cohort's
  `min_turn` halves), so ambient feed density shifts earlier. Feed items are
  inert lines; this is pacing, not correctness.
- The calendar badge (July 2017 + turn) will disagree with an event's
  historical year MORE than it already does (5x -> 10x compression). The
  divergence exists today; do not promise "events fire on their dates"
  anywhere player-facing. `docs/data/HISTORICAL_DATA_INTEGRATION.md` already
  makes that false promise and the contract card already flags it for cleanup.
- Probability-roll consumption changes -> old replays diverge. Ship with a
  version bump (board key forks automatically); see section 7.

If the retime is skipped entirely, the pass degrades to the 2017-2020
candidates only (marked "works today" in section 5) -- it does not become
worthless, but the five best events stay invisible.

---

## 2. What a PROMOTED event is, mechanically (verified findings)

The pipeline: `EventService` loads `godot/data/historical_events.json`, deep-
merges any override keyed by record id (`event_service.gd:920-948`), then
`_transform_event` (line 259) builds the game event. `events.gd:104-115` feeds
it to the trigger loop; `month_controller.gd:189-210` routes fired events by
tier -- only WINDOW-tier events open a decision, throttled by the demand
budget (3/month, 6 after turn 200).

**F1. Two gates keep an event out of the window tier** (`event_service.gd:387,
404-410`): category `technical_research_breakthrough` OR id starting with
`arxiv`. Anything that passes both gates gets `type: popup` + generated
options and classifies as a window (`event_tiers.gd:53`). So "promotion" =
override the category (and, for arxiv records, the id -- see F4).

**F2. The 20 "real window events" are windows with BLANK personalities.**
`_generate_options` (line 482) picks an option template by category, and only
these categories have real templates:

    organization, organization_founding      -> collaborate / compete / observe
    research, paper, alignment_research      -> build upon (money+hours) / safety analysis / acknowledge
    policy, regulation, policy_event         -> support / critique / stay neutral
    incident, capability, capability_advance -> respond publicly / internal review / note concerns
    funding_catastrophe, funding             -> emergency fundraise / diversify / accept losses

`organizational_crisis` (6 records) and `institutional_decay` (7 records)
match NO template and fall to the bland default (engage / acknowledge) -- they
are already "flavour lines with extra steps". Promoting them is a one-word
category override into the right template. Only the 7 `funding_catastrophe`
records currently have a real decision.

**F3. Which raw fields an override can actually change.** `_transform_event`
builds a fresh dict; only these raw keys survive: `title`, `description`,
`category`, `rarity`, `year`, `impacts`, `significance`,
`safety_researcher_reaction`, `media_reaction`, `id` (`pdoom_impact` is
copied but read by nothing). Custom `options`, `delivery_tier`,
`event_class`, `unignorable`, `expiry_turns` in an override are silently
IGNORED -- they are not passed through. Consequences:
- You choose a decision by choosing a TEMPLATE (category), not by authoring
  options. Option text/costs are fixed per template; magnitudes scale.
- Staffing mechanics (hire / poach / loyalty_hit effects, `events.gd:336-358`)
  are unreachable from this pass -- no template uses them. An event like
  "safety team departures" can be promoted for its reputation/panic choice but
  cannot actually remove a researcher. Do not promise otherwise in copy.

**F4. The arxiv escape hatch: override the `id` too.** The override file is
keyed by the ORIGINAL record id; an `"id"` key inside the override replaces
the id before the flavour check runs (`_apply_overrides` merges scalars, then
`_is_flavour_event` reads the merged id). So
`"arxiv_f48be4c3fb9d9ad0": {"id": "gpt2_staged_release_2019", "category":
"policy_event", ...}` fully promotes an arxiv record. Works today; it is
undocumented behaviour, so a regression test or a passthrough (section 4) is
the durable version. Distill records only need the category override (their
ids do not start with "arxiv").

**F5. Timing dials that actually work.** `rarity` picks the trigger mode
(legendary = deterministic exact turn, scripted-bucket priority in the 2-per-
turn cap; rare = 6%/turn after eligibility; common = 12%/turn). NOTE:
`eligibility_end` is computed but NEVER checked -- `should_trigger`'s random
branch reads only `min_turn` + `probability` (`events.gd:173-190`). "Rare" is
just "common, later and slower"; there is no real window cutoff. Expected lag
after eligibility: ~8 turns (common), ~16 turns (rare). Use legendary for
story beats you want every run to see at a fixed point; rare/common for
variety that lands differently per seed.

**F6. Effect magnitudes: one scalar, two honest paths.** `significance` (1-10,
override directly -- simpler than faking an impacts array) scales every
template option: rep_effect = significance, doom_effect = 0.6x, money costs
2000x. The templates' literal `doom` effects are NOT the ADR-0015 dead path:
`execute_event_choice` routes literal doom into the doom engine's `panic`
stream (`events.gd:304-310`), which is real and attributable. But DO NOT add a
`doom` or `pdoom_impact` key in an override expecting a printed delta --
ADR-0015 retired that; the only doom influence is stream-routed. The `impacts`
array matters only for (a) auto-computing significance and (b) the
`funding_catastrophe` template, where the mapped `cash` impact (x1000) sets
the money hole and the fundraise recovery. Keep impacts for funding events;
use bare `significance` everywhere else.

**F7. ADR-0012 class: every promoted event is DEFERRABLE, like it or not.**
`event_class` is not passed through (F3), so all historical windows take the
Balance default `deferrable` (`defaults.json` `default_event_class`) -- DEFER
mints a ledger entry, IGNORE resolves via the zero-cost option
(`window_resolver.gd:45-58`; every template has one, so IGNORE is always
coherent). The per-event classes recommended in section 5 are aspirational
until the section 4 enabler lands. This is acceptable for v1: deferrable is
the taxonomy's safe middle, and the ledger carrying cost (ADR-0013) gives even
a deferred FTX event teeth.

**F8. One-shot, capped, budgeted.** Promoted events are `repeatable: false`
(once per run), share the 2-events-per-turn cap (#568, legendary/scripted
fire first), and windows beyond the 3/month demand budget downgrade to feed.
Promoting ~13 events spread over ~220 turns adds well under one window per
month on average -- no flood risk.

---

## 3. Corpus survey (counted from the shipped file)

1,194 records: 1,129 `arxiv_*` + 37 `distill_*` + 28 hand-authored.
Categories: 1,174 technical_research_breakthrough, 7 funding_catastrophe,
7 institutional_decay, 6 organizational_crisis.
Years: 2016:54 (blocked by start-year filter, `events.gd:111`), 2017:60,
2018:207, 2019:200, 2020:211, 2021:224, 2022:192, 2023:28, 2024:14, 2025:4.

Where the variety is, per run phase (turns under the proposed 26/yr retime):

- **Early (turns 1-40, "2016-2018"):** hand-authored fireable content today =
  Maven and Tesla ONLY (Tay is 2016-blocked). The teaching window of the run
  has almost no historical texture.
- **Middle (turns 40-100, "2019-2020"):** ZERO hand-authored events. 411
  records, all flavour-demoted research. This is the empty middle the pass
  should fill -- from arxiv/distill landmarks (GPT-2 release strategies,
  training-data extraction, Circuits).
- **Late (turns 100-160, "2021-2022"):** anthropic_exodus, FTX, crypto crash.
  The strongest funding shocks live here. Good.
- **Endgame (turns 160+, "2023-2025"):** board crisis, alignment faking,
  clawback, coordination breakdown, blackmail -- 20 records, only reachable
  after the retime, and only in long runs.

Notable corpus GAPS (do not go hunting; they are absent): no GPT-3 paper, no
scaling laws, no AlphaFold/AlphaGo, no Transformer paper, no ChatGPT-moment
record (`example.json` references `chatgpt_released` and `openai_founded`;
NEITHER id exists in the shipped file -- two of its three example overrides
are dead keys). Capability-landmark variety is ADR-0016 world-pack material,
out of scope for this half hour.

Also 4 sibling "AI caught scheming" records (sandbagging, alignment faking,
Apollo scheming, METR deception, all 2024). Promote ONE (alignment faking --
the famous one); promoting all four is the same window four times.

---

## 4. Optional enabler (small PR, NOT needed for the core pass)

Pass through optional classification keys in `_transform_event`
(`event_service.gd`, after line 380): if the raw/override record carries
`event_class`, `unignorable`, `expiry_turns`, or `delivery_tier`, copy them
onto the game event. ~8 lines + one unit test. This unlocks the ADR-0012
classes in section 5's last column and makes F4's id trick unnecessary for
future passes (an explicit `delivery_tier: "window"` beats an id rename).
Until it lands, every promoted event is a deferrable window (F7) -- fine.

---

## 5. THE RANKED LIST

Legend: firing turn is under the RECOMMENDED 26/yr retime (section 1);
"works today" = also reachable under the current 52/yr numbers. Class column
is the ADR-0012 target once the section 4 enabler lands; until then all are
deferrable. Every arxiv/distill promotion MUST override title+description --
the base descriptions are PDF-extraction garbage (contract card / #51).

### Tier A -- the five that carry the pass

**A1. `ftx_future_fund_collapse_2022` -- FTX Future Fund Collapse (2022)**
Override: `rarity: legendary` (keep category funding_catastrophe, keep
impacts). Fires turn ~144, every run.
Why: the best-authored record in the corpus wired to the best template, and
today it is a 6%/turn roll parked at turn 261+ -- most players have never
seen it. Choice: emergency fundraise (2 founder hours, recover half the hole,
reputation cost) vs diversify vs eat the loss. Mechanic: spiky-in/smooth-out
cash (ADR-0012's named core tension), month-plan hours, ledger carrying cost
on DEFER -- deferring an $80k funding hole and paying carrying cost on it is
exactly what the ADR-0013 engine is for. Class: deferrable (true fit).

**A2. `microsoft_tay_2016` -- Tay Chatbot Scandal**
Override: `year: 2017` (start-year filter blocks 2016; one-line `_reason`
documenting the echo), `category: incident`, `rarity: legendary`,
`significance: 4`. Fires turn ~14 -- works today (turn 27 under 52/yr).
Why: the early game currently teaches windows with zero historical texture;
Tay is a perfect low-stakes first incident (respond publicly / internal
review / note concerns) and its media_reaction line is already funny. Mechanic:
first contact with window verbs, reputation, panic stream, at stakes a turn-14
lab can afford. Class: un-snoozable (a news cycle does not wait) -- the
taxonomy's teaching example.

**A3. `arxiv_f48be4c3fb9d9ad0` -- "Release Strategies and the Social Impacts
of Language Models" = the GPT-2 staged-release debate (2019)**
Override: `id: gpt2_staged_release_2019`, `category: policy_event`,
`rarity: legendary`, `significance: 6`, new title ("GPT-2 and the Staged
Release Debate"), new description, reactions. Fires turn ~66 -- works today
(turn 131). Why: fills the empty middle with the era's defining publication-
norms fight, and the policy template (support staged release / critique /
stay neutral) maps onto a real community argument. Mechanic:
reputation-vs-research trade, thematically adjacent to the game's own paper
system. Class: standing (the debate stays open for a while, then moves on).

**A4. `openai_board_crisis_2023` -- Board Crisis and CEO Firing**
Override: `category: incident`, `rarity: legendary`, `significance: 8`.
Fires turn ~170 (endgame; unreachable at 52/yr -- turn 339).
Why: the strongest governance story in the corpus, currently rendered with
the blank default template AND unreachable. Choice: issue public response /
internal governance review / note concerns. Mechanic: endgame reputation and
panic swing when the window budget has doubled. Class: un-snoozable.

**A5. `anthropic_exodus_2021` -- Safety-Focused Lab Splits Off**
Override: `category: organization`, `rarity: legendary`, `significance: 6`.
Fires turn ~118 (turn 235 today: marginal).
Why: the ONLY viable record that exercises the organization template --
collaborate with the new safety lab / position as competitor / observe. The
compete option is the one generated choice that trades reputation away for
research velocity, and it lands mid-run where that trade is live. Mechanic:
org positioning, rival texture (ADR-0007 world flavour). Class: no-action
(watching a rival form is legitimately fine).

### Tier B -- strong, copy-adapt-repeat (8)

**B1. `google_project_maven_2018`** -- category `incident`, rarity `rare`,
significance 5. Eligible ~turn 27+, works today. Employee-revolt ethics story;
respond/review choice. Class: deferrable.
**B2. `arxiv_eaef206260f37f45` "Extracting Training Data from LLMs" (2020)**
-- id `training_data_extraction_2020`, category `incident`, rarity `rare`,
significance 5, rewrite title/desc. Eligible ~turn 79+. The mid-run security
incident. Class: deferrable.
**B3. `arxiv_ac6144846c25f722` "Deep RL from Human Preferences" (2017)** --
id `rlhf_origin_2017`, category `alignment_research`, rarity `rare`,
significance 5, rewrite. Eligible early; works today. Research template:
build-upon costs money+hours for research -- the first real invest-in-a-
result decision. Class: standing.
**B4. `arxiv_19f1abcbac7010a1` "Scalable agent alignment via reward
modeling" (2018)** -- id `reward_modeling_agenda_2018`, category
`alignment_research`, rarity `common`, significance 4, rewrite. Works today.
Class: standing.
**B5. `arxiv_eb20cd0d24a7d685` "Emergent Tool Use From Multi-Agent
Autocurricula" (2019)** -- id `emergent_tool_use_2019`, category
`capability_advance`, rarity `rare`, significance 5, rewrite (the OpenAI
hide-and-seek result). Eligible ~turn 53+. Capability-shock texture for the
empty middle. Class: no-action.
**B6. `distill_ed5ab808068ad61f` "Zoom In: An Introduction to Circuits"
(2020)** -- category `alignment_research`, rarity `legendary`, significance
5, rewrite desc (title is fine). Fires ~turn 92. The interpretability
milestone; safety-analysis option shines. Class: standing.
**B7. `cais_ftx_clawback_2023`** -- keep category, rarity `rare`,
significance 6. Eligible ~turn 157+. The delayed second bill from A1 -- a
funding shock that arrives AFTER you thought the crisis was over; the
diversify option finally pays off. Class: deferrable.
**B8. `anthropic_alignment_faking_2024`** -- category `incident`, rarity
`legendary`, significance 8. Fires ~turn 196. THE scheming beat (promote only
this one of the four siblings, section 3). Class: un-snoozable.

### Tier C -- bench (promote only if the file is going well) (8)

C1. `tesla_autopilot_incidents_2016_2024` (2018) -- incident, common, sig 5.
C2. `arxiv_7c7c5101e999d894` WebGPT (2021) -- capability_advance, common,
sig 4, rewrite.
C3. `arxiv_c356f4bb1fc1101d` TruthfulQA (2021) -- alignment_research,
common, sig 4, rewrite.
C4. `arxiv_5b9b42f6b9b6a092` Red Teaming LMs with LMs (2022) --
alignment_research, common, sig 4, rewrite.
C5. `international_coordination_breakdown_2025` -- policy_event, rare,
sig 7. Endgame-only sighting; the one institutional_decay record worth a
window (the other six are near-duplicates of each other with weaker copy).
C6. `claude_4_opus_blackmail_2025` -- incident, legendary, sig 9. Fires
~turn 222; a final-act jolt for long runs only.
C7. `distill_eb5c12bc89464f38` "AI Safety Needs Social Scientists" (2019) --
alignment_research, common, sig 3, rewrite.
C8. `openai_safety_team_departures_2024` -- incident, rare, sig 6. Staffing
THEME only -- it cannot remove a researcher (F3); keep copy honest.

### Deliberately NOT promoted

- The other 3 scheming siblings (sandbagging, Apollo, METR) -- same window
  thrice; keep as flavour.
- `uk_ai_safety_to_security_2025` / `us_aisi_to_caisi_2025` /
  `ai_summit_pivot_2023_2025` / `eu_ai_act_watering_down_2024` /
  `academic_safety_funding_cuts_2024` / `safety_researcher_brain_drain_2024`
  -- institutional_decay near-duplicates; C5 represents the theme. (The UK
  record's title also contains a non-ASCII arrow -- if it is ever promoted,
  override the title to ASCII.)
- `gartner_synthetic_data_prediction_2024`, `synthetic_data_scaling_2024`,
  remaining funding_catastrophe minors, the other 34 distill posts, and the
  arxiv bulk -- forecasts and papers with no decision attached are flavour
  lines, and flavour is the tier they are already in.

Spread check: 13 A+B promotions = 3 early / 4 middle / 3 late / 3 endgame;
templates exercised: funding x2, incident x4, policy x1, organization x1,
research x4, capability x1. Every template with a real decision gets play.

---

## 6. What to write, verbatim

### 6a. The retime (`godot/data/events/balancing/rarity_curves.json`)

Change three values in `year_trigger` (rest of the file untouched):

    "year_trigger": {
      "_description": "Settings for year-based event triggering",
      "turns_per_year": 26,
      "base_year": 2017,
      "base_month": 7,
      "legendary_month_offset": 13,
      "rare_spread_turns": 6
    }

(52 -> 26: one historical year = ~5 game weeks; offset and spread halve to
keep legendary at mid-year and rare windows proportionate. See section 1 for
what this does and does not promise.)

### 6b. The override file (`godot/data/events/overrides/promotion_pass_2026_08.json`)

ASCII only -- the no-emoji pre-commit gate scans `godot/data/**/*.json` and
BLOCKS any codepoint above U+007F. Full shape with the first three entries;
every further entry is copy-adapt of one of these three patterns:

    {
      "_description": "Event promotion pass 2026-08: promote historical records to window-tier decisions. See docs/design/EVENT_PROMOTION_PASS.md.",
      "_note": "Keyed by ORIGINAL record id. An 'id' key inside an entry renames the event (required to promote arxiv_* records past the flavour gate). category picks the option template; rarity picks the trigger mode; significance (1-10) scales option magnitudes. NEVER add doom/pdoom_impact keys (ADR-0015).",

      "ftx_future_fund_collapse_2022": {
        "_reason": "Pattern 1, already-window event: escalate to a deterministic story beat. Keeps funding_catastrophe template and its impacts (the cash impact sets the money hole).",
        "rarity": "legendary"
      },

      "microsoft_tay_2016": {
        "_reason": "Pattern 2, re-categorize + re-year. 2016 records cannot fire (start-year filter); year 2017 is a documented timeline echo. incident template = respond/review/note choice.",
        "year": 2017,
        "category": "incident",
        "rarity": "legendary",
        "significance": 4
      },

      "arxiv_f48be4c3fb9d9ad0": {
        "_reason": "Pattern 3, full arxiv promotion: new id escapes the arxiv flavour gate, new category escapes the research gate and picks the policy template, title/description replace PDF-extraction text.",
        "id": "gpt2_staged_release_2019",
        "category": "policy_event",
        "rarity": "legendary",
        "significance": 6,
        "title": "GPT-2 and the Staged Release Debate",
        "description": "OpenAI withholds its full language model, citing misuse potential, and releases it in stages. The field splits: responsible precedent, or reputational theater that broke publication norms? Everyone wants to know where your lab stands.",
        "safety_researcher_reaction": "Finally someone treats release itself as a safety decision",
        "media_reaction": "AI lab says its text generator is too dangerous to release"
      }
    }

Then repeat: Tier A4/A5 and B1/B7/B8/C-hand-authored use pattern 2 (category
+ rarity + significance); B2-B6 and C2-C4/C7 use pattern 3 (add `id`, `title`,
`description`). All the values are in the section 5 table.

---

## 7. Guardrails and sequencing

- **Ship on a release boundary, never mid-league-week.** Promoted random
  events and the retime change RNG consumption in the trigger loop; replays
  and board comparability fork. The version bump forks the board key by
  design (`version.txt` SSOT + `tools/sync_version.py`) -- that is the
  correct fork; a silent mid-week data change is not.
- **Do not touch `godot/data/historical_events.json`.** The pass needs zero
  edits there, and the file contains a pre-existing non-ASCII arrow that will
  trip the blocking no-emoji gate if the file is ever re-staged.
- Stage only the two files (`git add <path>`, never `-A`); commit in the
  foreground per CLAUDE.md.
- After landing, have an agent lane run the fast gate plus
  `tests/unit/test_events.gd` -- the pass touches data only, but
  `test_no_authored_event_content_writes_literal_doom` and the event-service
  transform tests are the relevant tripwires.
- `example.json` cleanup (2 of its 3 keys reference records that do not
  exist) can ride along or wait; it is inert either way.

---

## 8. What could not be determined

- **Median run length.** The turn-band evidence (sweep <300, endgame at 200,
  deaths 14-229, one stale doc saying "rarely past 100") brackets but does
  not pin the median; if most human runs die before turn ~120, the endgame
  promotions (A4, B7, B8, C5, C6) are rare-sighting content by construction.
  Run-length telemetry or a replay sample would settle it, and would also
  settle whether 26/yr should really be ~20/yr.
- **Whether Pip wants the alt-timeline year fiction stated anywhere player-
  facing** (e.g. feed items showing the historical year as provenance). The
  retime widens badge-vs-history divergence; a one-line UI treatment ("echo
  of 2019") is a taste call not taken here.
- **Window-budget contention in practice** -- promoted windows compete with
  hiring cards and core events for 3 slots/month; the math says no flood
  (section 2 F8), but only a playtest shows whether a legendary beat ever
  gets budget-downgraded to feed in a busy month. If A1 or A4 ever lands as
  a feed line, that is the section 4 passthrough's `delivery_tier` field
  earning its keep.
