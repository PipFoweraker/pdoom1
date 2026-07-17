# Researcher Quirks

*The hidden-but-true rider layer on researchers. Replaces the retired placeholder
"trait / perk" system.*

Status: implemented on `feat/hiring-phase-b-pipeline` (PR #664). Data:
`godot/data/researchers/quirks.json`. Loader: `godot/scripts/core/quirk_catalogue.gd`.
Model: `godot/scripts/core/researcher.gd` (`quirk`, `quirk_known`, `quirk_effect()`).

## What a quirk is

A **quirk** is a rare, thematically-grounded lab archetype riding on a researcher: a
philosophical stance, a working style, a political tic. Each carries a **small, legible
mechanical effect** and is **hidden but TRUE** -- it is real from the moment the researcher
is created; play only *reveals* it. The sim never lies (BUILD_BRIEF_HIRING_PIPELINE.md:
"Hidden info is TRUE-but-incomplete -- interviewing reveals, it does not fabricate"). A
leaker leaks from day one; you just do not yet know *who* or *why*.

Quirks sit alongside, but are distinct from, the five **appetites**
(compute / prestige / mentees / money / mission_purity, ADR-0011 sec.8). An appetite is a
0..1 negotiation hunger revealed by *interviewing*; a quirk is a discrete rider revealed by
an *exposure* (an incident, or simply time on the team) -- **never** by the interview ladder
(A2). A fully-interviewed hire can still be hiding a quirk.

Register is held to Papers-Please deadpan: **"bother," not HR gravity** (WORLD_AND_LORE.md).
Quirks are archetype-flavours, never portraits of real people (the event-horizon guardrail).

## The catalogue (14 quirks)

Valence key: `+` positive, `-` negative, `+/-` double-edged (the best ones cut both ways).

| # | id | name | v | one-line flavour | hidden effect (legible once revealed) | appetite | reveal |
|---|----|------|---|------------------|----------------------------------------|----------|--------|
| 1 | `secret_successionist` | Secret Successionist | - | Believes the machines should inherit the earth -- and is quietly at peace with it. | ships fast (+12% own productivity) but quietly discounts safety (+0.04 doom) | mission_purity | incident (an old commit's half-joke manifesto) |
| 2 | `doom_absolutist` | Doom Absolutist | +/- | P(doom) is 0.99 and they will cc the whole company to say so. | their diligence lowers doom (-0.06) but the moralizing drags the room (-3% team) | mission_purity | tenure (~8 turns) |
| 3 | `e_acc_sympathizer` | e/acc Sympathizer | - | Wants to feel the AGI. "Also helps safety, really." | burns compute, ships (+15% own) but pushes danger (+0.05 doom) | compute | incident (unsanctioned scaling run) |
| 4 | `open_science_zealot` | Open-Science Zealot | +/- | Information wants to be free; the NDA was a suggestion. | spreads knowledge (+2% team) but leaks on principle (3%/turn) | prestige | leak (a preprint legal never saw) |
| 5 | `secrecy_maximalist` | Secrecy Maximalist | +/- | Compartmentalizes everything, including from you. | heads-down focus (+5% own) but silos the team (-4% team) | mission_purity | tenure (~6 turns) |
| 6 | `empire_builder` | Empire Builder | +/- | Every problem is solved by hiring three more reports. | grows the team (+4% team) but drives everyone hard (+0.3 burnout/turn) | prestige | tenure (~7 turns) |
| 7 | `runs_hot` | Runs Hot | +/- | Ships twice the work and burns at twice the rate. | +20% own productivity, +2.0 burnout/turn | -- | tenure (~6 turns) |
| 8 | `lab_parent` | Lab Parent | + | The one who actually onboards the juniors nobody else will. | +6% productivity to the whole team | mentees | tenure (~5 turns) |
| 9 | `loose_lips` | Loose Lips | - | A delightful conversationalist with a poor sense of what was confidential. | 5%/turn chance to leak research | prestige | leak (a detail in a rival deck) |
| 10 | `sponge` | Sponge | + | Absorbs a whole subfield over a long weekend. | 2.5x skill-growth rate | mentees | tenure (~10 turns) |
| 11 | `cat_whisperer` | Cat Whisperer | + | The office cat is calmest at their desk -- a small mercy against the doom. | +3% team, -0.5 burnout/turn (cancels the base) | -- | tenure (~4 turns) |
| 12 | `glory_hound` | Glory Hound | - | First author or no author; co-authors are load-bearing furniture. | +10% own but demoralizes co-authors (-4% team) | prestige | incident (authorship dispute) |
| 13 | `quiet_quitter` | Quiet Quitter | - | Present, paid, and quietly checked out. | -15% own productivity, -1 loyalty/turn (flight risk) | money | tenure (~6 turns) |
| 14 | `true_believer` | True Believer | + | Would do this for free, and nearly does; recruiters bounce off. | -0.04 doom, +1 loyalty/turn (poach-resistant) | mission_purity | tenure (~8 turns) |

Deliberate spread: 4 positive, 5 negative, 5 double-edged. The two secrecy poles
(`open_science_zealot` vs `secrecy_maximalist`) and the three mission-purity registers
(`true_believer` / `doom_absolutist` / `secret_successionist`) map the doomer-vs-accelerationist
axis onto real hiring dilemmas.

## Effect channels

A quirk's effect is a small fixed set of keys the sim reads through
`Researcher.quirk_effect(key, default)`. No stat soup -- each quirk touches one or two:

| channel | default | where it hooks | sign meaning |
|---------|---------|----------------|--------------|
| `self_productivity_mult` | 1.0 | `get_effective_productivity()` | >1 faster, <1 slower |
| `burnout_per_turn_add` | 0.0 | `process_turn()` (on top of base 0.5) | + burns, - relieves |
| `doom_mod_add` | 0.0 | `get_doom_modifier()` | + raises doom, - lowers |
| `leak_chance` | 0.0 | `turn_manager` roster loop | per-turn leak probability |
| `team_productivity_add` | 0.0 | `turn_manager` team bonus | + lifts team, - drags it |
| `skill_growth_mult` | 1.0 | `process_turn()` skill roll | >1 grows faster |
| `loyalty_per_turn_add` | 0 | `process_turn()` loyalty drift | + retains, - flight-risk |

These are the **exact hook points the retired traits used**, so wiring quirks in was a swap,
not new sim surface. The effect is live even while the quirk is hidden -- the player observes
the *output* (a leak, a productivity dip) before learning the *cause*.

## Reveal mechanics

Quirks flip `quirk_known` (never fabricated -- the value pre-exists) via:

1. **Tenure fallback (deterministic, always present).** Every quirk carries
   `reveal.after_turns`; once `turns_employed` reaches it, `process_turn()` surfaces the
   quirk (`maybe_reveal_quirk_by_tenure()`). This guarantees no rider stays invisible
   forever, and is fully seed-reproducible (ADR-0006).
2. **Leak incident.** When a leak-risk quirk (`leak_chance > 0`) actually fires a leak,
   `turn_manager` calls `expose_quirk()` that turn -- the incident names the culprit.
3. **Exposure events.** `reveal.via = "incident"` quirks are tagged for the existing
   ADR-0003 exposure-event genre (`expose_quirk()`); the tenure fallback still guarantees
   eventual reveal until a bespoke event exists.

Interviewing (the reveal ladder) deliberately does **not** surface quirks (A2 contract,
`test_quirk_hidden_even_when_fully_interviewed`).

## Starters (the "starter pokemon")

The four turn-0 founders each get a **guaranteed hidden rider** (`game_state.gd
_assign_guaranteed_rider`): a coin-flip between a strong appetite and a **catalogue quirk**
(`QuirkCatalogue.pick_id`). Riders start hidden; the depth is latent for late-game drama.

## Determinism (ADR-0006)

- Assignment draws only from the seeded RNG. `QuirkCatalogue.pick_id()` indexes a **sorted**
  id list, so the pick is independent of JSON/Dictionary iteration order.
- In `generate_random`, the quirk draw reuses the same two hidden-RNG draws (chance +
  index) the old pool used, so the RNG stream is byte-identical downstream -- only the
  resulting id changes.
- `quirk` / `quirk_known` serialize in `to_dict`/`from_dict` and round-trip through JSON.
- Replay verification (`test_replay_verification`) is run-vs-replay, and both tiers pass.

## Legacy traits: retired vs kept-reframed

The old `POSITIVE_TRAITS` / `NEGATIVE_TRAITS` dicts, the `traits` array, `add_trait` /
`has_trait` / `get_trait_description`, and the dead `_assign_random_traits` assigner are
**removed**. Their effect hooks were repointed at the quirk channels above. Pip: "happy to
move away from the perk thinking ... very placeholdery and shallowly designed."

**Kept by reframing into a quirk** (the ones worth keeping):

| legacy trait | -> quirk | why kept |
|--------------|----------|----------|
| `workaholic` (+prod, +burnout) | `runs_hot` | the cleanest double-edged; classic |
| `team_player` (+team prod) | `lab_parent` | team-wide lift, now with a mentees tie-in |
| `leak_prone` (leaks) | `loose_lips` | anchors the secrecy/leaks theme |
| `fast_learner` (skill growth) | `sponge` | keeps the growth-over-time hook |
| `safety_conscious` (-doom) | folded into `true_believer` | doom-diligence, now with loyalty |

**Retired outright** (shallow / redundant / tied to other systems):
`prima_donna` (salary-threshold micro-penalty), `burnout_prone` (subsumed by `runs_hot` /
per-quirk burnout), `pessimist` (flat morale hit, no depth), `media_savvy` (paper-quality /
reputation bonus -- a press-facing quirk can re-add it later via a dedicated channel),
`road_warrior` (jet-lag-specific; the jet-lag system stands on its own).

## Follow-ups (not in this pass)

- Bespoke exposure *events* per `incident` quirk (currently tenure-fallback only).
- The placeholder staff-perks panels (`staff_perks_panel.gd`, `staff_perks_compact.gd`)
  are decoupled from the removed `traits` field and now show empty slots; a future pass can
  rebuild them on the quirk layer (or delete them).
- A press/reputation channel to re-home the retired `media_savvy` effect.
