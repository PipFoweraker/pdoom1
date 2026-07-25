# Perk flavour harvest (dead 15-perk system -> quirk catalogue)

Status: SEED (WS-3 content review input -- nothing here is auto-adopted)

## What this is

The tiered perk system in `staff_perks_panel.gd` (TIER_1/2/3_PERKS, 15 perks,
25 effect keys) was DEAD code: `_is_perk_equipped` always returned false, zero
sim consumers, and the backing trait system was retired in favour of the
data-driven quirk catalogue (`godot/data/researchers/quirks.json`, see
`RESEARCHER_QUIRKS.md`). The `feat/quirk-skeleton` branch deletes the perk
definitions and rebuilds the staff ID card on the quirk layer.

This document harvests the perks' FLAVOUR before deletion, so nothing written
is lost. Each perk maps to one of three verdicts:

- **COVERED** -- an existing quirk already expresses the idea; drop the perk.
- **SEED** -- the idea is worth a NEW quirk; a draft JSON stub is inline.
  Stubs marked `(new channel)` need an effect channel the sim does not read
  yet -- adopting them is a WS-3 decision, not a copy-paste.
- **DROP** -- shallow, redundant, or dependent on a system that does not exist.

Effect channels the sim reads today (via `Researcher.quirk_effect()`):
`self_productivity_mult`, `burnout_per_turn_add`, `doom_mod_add`,
`leak_chance`, `team_productivity_add`, `skill_growth_mult`,
`loyalty_per_turn_add`. See `RESEARCHER_QUIRKS.md` "Effect channels".

## Tier 1 (Foundation)

| perk | intended effects | verdict | mapping |
|------|------------------|---------|---------|
| Methodical | +10% research quality, -15% error rate | SEED | stub `checklist_devotee` below |
| Fast Learner | +50% skill growth | COVERED | `sponge` (skill_growth_mult 2.5 -- strictly stronger) |
| Team Player | +10% team productivity | COVERED | `lab_parent` (team_productivity_add 0.06) |
| Night Owl | +25% crunch bonus, +10% burnout rate | COVERED | `runs_hot` is the same trade at higher stakes; no crunch mechanic exists to hook the conditional part |
| Safety First | -10% doom (safety spec only) | COVERED | `true_believer` (doom_mod_add -0.04, plus loyalty); ruled in RESEARCHER_QUIRKS.md ("safety_conscious folded into true_believer") |

```json
"checklist_devotee": {
  "name": "Checklist Devotee",
  "flavour": "Slower, but nothing ships broken. The postmortem doc is always already written.",
  "valence": "double_edged",
  "appetite": "mission_purity",
  "effects": { "self_productivity_mult": 0.92, "research_quality_add": 0.10 },
  "reveal": { "via": "tenure", "after_turns": 5, "hint": "Their PRs are the only ones that never get reverted." },
  "_note": "research_quality_add is a NEW channel; could hook state research-quality mode (#500) instead of a bespoke channel."
}
```

## Tier 2 (Specialization)

| perk | intended effects | verdict | mapping |
|------|------------------|---------|---------|
| Deep Focus | +20% output, -15% multitask | SEED | stub `monotasker` below (expressible with today's channels) |
| Mentor | +30% mentee skill growth | SEED | stub `socratic` below; pairs with the `mentees` appetite |
| Publisher | +20% paper quality, +2 rep/publish | SEED | stub `press_darling` below; re-homes retired `media_savvy` (RESEARCHER_QUIRKS.md follow-up already asks for a press/reputation channel) |
| Networker | +25% conference bonus, +15% poach resistance | SEED | stub `rolodex` below |
| Resilient | +30% burnout recovery, +25% jet-lag reduction | SEED | stub `teflon` below (fully expressible today) |

```json
"monotasker": {
  "name": "Monotasker",
  "flavour": "One tab open. One problem. Do not schedule them into a second meeting.",
  "valence": "double_edged",
  "appetite": "compute",
  "effects": { "self_productivity_mult": 1.15, "team_productivity_add": -0.02 },
  "reveal": { "via": "tenure", "after_turns": 6, "hint": "They have declined every recurring invite for a month." }
},
"socratic": {
  "name": "Socratic",
  "flavour": "Answers every question with a better question. The juniors level up anyway.",
  "valence": "positive",
  "appetite": "mentees",
  "effects": { "mentee_skill_growth_mult": 1.5 },
  "reveal": { "via": "tenure", "after_turns": 7, "hint": "The intern just solved something the seniors could not." },
  "_note": "mentee_skill_growth_mult is a NEW channel: multiplies the skill roll of LOWER-skill roster-mates, not self. Distinct from lab_parent (flat team output)."
},
"press_darling": {
  "name": "Press Darling",
  "flavour": "Gives good quote. Journalists have their personal number; legal wishes they did not.",
  "valence": "double_edged",
  "appetite": "prestige",
  "effects": { "paper_reputation_add": 1.0, "leak_chance": 0.01 },
  "reveal": { "via": "incident", "after_turns": 8, "hint": "A profile piece runs with a suspiciously flattering photo." },
  "_note": "paper_reputation_add is a NEW channel (+rep per published paper); the small leak_chance keeps the double edge honest."
},
"rolodex": {
  "name": "Rolodex",
  "flavour": "Knows everyone. Which also means everyone knows them.",
  "valence": "double_edged",
  "appetite": "prestige",
  "effects": { "loyalty_per_turn_add": 1, "hiring_connections_bonus": 0.15 },
  "reveal": { "via": "tenure", "after_turns": 6, "hint": "Your best lead this quarter came 'through a friend'." },
  "_note": "hiring_connections_bonus is a NEW channel (boost hiring.connections success). The original poach-resistance reading maps to loyalty_per_turn_add, live today."
},
"teflon": {
  "name": "Teflon",
  "flavour": "Deadlines, red-eyes, layoff rumours -- nothing sticks.",
  "valence": "positive",
  "appetite": "",
  "effects": { "burnout_per_turn_add": -1.0 },
  "reveal": { "via": "tenure", "after_turns": 5, "hint": "Everyone else is fraying; they brought pastries." },
  "_note": "Expressible today. Jet-lag reduction dropped (jet-lag system stands on its own, same ruling as retired road_warrior)."
}
```

## Tier 3 (Mastery)

| perk | intended effects | verdict | mapping |
|------|------------------|---------|---------|
| Visionary | +15% breakthrough chance, special projects | DROP | depends on breakthrough/special-project systems that do not exist; revisit if a breakthrough mechanic lands |
| Leader | +15% lab productivity, +10 morale | COVERED | `lab_parent` / `empire_builder` own team-wide lift; no morale stat exists. WS-3 may want a stronger-tier team quirk instead |
| Specialist | +40% specialization bonus | DROP | specialization bonuses live in `Researcher.SPECIALIZATIONS`; a flat multiplier on top is stat soup with no story |
| Polymath | works any specialization, +20% versatility | DROP (note) | respec/multi-lane assignment is an L2 assignment-surface question, not a quirk |
| Sage | -10% lab doom, +20% event mitigation | COVERED | `doom_absolutist` / `true_believer` carry doom-lowering dispositions (doom_mod_add, now routed lab-wide via the DoomSystem quirk stream); event mitigation is the alignment lane's passive |

## Disposal record

- Perk definitions deleted from `staff_perks_panel.gd` on `feat/quirk-skeleton`
  (the ID card now renders quirk/appetite/loyalty/tenure).
- `staff_perks_compact.gd` / `.tscn` were orphaned (no references outside
  themselves) and are deleted on the same branch.
- Icon slots for quirks on the employee surfaces are tracked by issue #903.
