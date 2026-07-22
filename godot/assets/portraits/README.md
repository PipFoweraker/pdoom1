# Researcher portraits -- staged, unwired

Source: batch #649 gpt-image-1.5 portrait pilot
(`art_generated/researcher_portraits_pilot/`). Reviewed 2026-07-21
(`docs/art/reviews/BATCH_649_VERDICTS_2026-07-21.md`).

## Status

STAGED-BUT-UNWIRED. No UI slot references these yet. Do not assume any screen
loads them. They live here so a later hiring/roster UI can pick them up.

## What is here

The single most internally-consistent promoted set: the **CRT-dossier v2** run
(pole B, Papers-Please terminal-badge look), five archetypes, one coherent
style:

| file stem                         | archetype              | source variant                 |
| --------------------------------- | ---------------------- | ------------------------------ |
| dossier_people_pleaser            | People-Pleaser         | poleB_people_pleaser v2        |
| dossier_authoritarian_pessimist   | Authoritarian Pessimist| poleB_authoritarian_pessimist v2 |
| dossier_moral_crusader            | Moral Crusader         | poleB_moral_crusader v2        |
| dossier_capabilities_optimist     | Capabilities Optimist  | poleB_capabilities_optimist v2 |
| dossier_burned_out_senior         | Burned-Out Senior      | poleB_burned_out_senior v2     |

Sizes: 1024, 512, 256.

## Intended system (per-archetype variant pools)

Portraits are NOT a single fixed image per archetype. The intended design is
**per-archetype variant pools with random assignment**: each archetype owns a
pool of gender and appearance variants, and the game randomly assigns one per
run (hot-swappable). This is the representation mechanism and applies to all
archetypes over time.

The painterly keeps (including the People-Pleaser painterly male v1 / female v2
pair and the other painterly archetype keeps) remain in `art_generated/` as the
growing variant pool. Round-3 re-rolls deliberately add gender/ethnicity
variety per archetype. When the roster UI is built, wire it to select a random
variant from each archetype's pool rather than a fixed file.
