# SEED: Art sweep unit-cost model

Status: SEED (2026-07-26). Feeds issue #900 (pre-WS-3 art ramp) and WS-3
planning. Purpose: put a unit cost -- dollars/credits, generation wall-time,
Pip triage time, integration time -- on each asset type so future sweeps can
be budgeted instead of guessed. Numbers are tagged MEASURED (from logs,
manifests, or the live PixelLab balance) or ESTIMATE (derivation shown).
See LIMITS at the bottom before quoting anything downstream.

## Current PixelLab balance (MEASURED, get_balance 2026-07-26)

- Credits: $0.00 (nothing on pay-as-you-go)
- Subscription: Tier 1 "Pixel Apprentice", active
- Generations: 964 remaining of 2000/month (1036 used this cycle)
- Subscription price: ~$12/month, loyalty discount trends to ~$9/month
  [verify -- third-party review + search results, not read off a
  first-party pricing page; pixellab.ai/pricing did not render for fetch]

At $12 for a 2000-generation pool, one generation ~= $0.006. PixelLab
dollars are therefore noise; the real PixelLab budget is the MONTHLY
GENERATION POOL, plus Pip-hours downstream.

## Measured generation anchors (where every number below comes from)

| Anchor | Source | Numbers |
|---|---|---|
| 2026-07-19 volume batch | `art_source/pixellab_2026-07-19/MANIFEST.md` | 96 generations -> 48 props + 5 tilesets + 10 8-dir characters (133 PNGs); balance 1591 -> 1495 (MEASURED) |
| 2026-07-21 reroll sweep | `art_source/pixellab_2026-07-21-rerolls/MANIFEST.md` | 65 jobs / 120 PNGs; ~150 generations by balance interpolation 1495 -> ~1344 (ESTIMATE -- endpoint interpolated) |
| 2026-07-23 overnight props | `art_source/pixellab_overnight_2026-07-23/MANIFEST.md` | ~120 generations -> ~13 props (~16 objects) via 128px 1-dir candidate-frames mode; balance ended 1224 remaining (MEASURED, self-reported in manifest) |
| 2026-07-23..26 sandbox work | balance delta 1224 -> 964 | ~260 generations, incl. cat walk animations for sandbox v3 (MEASURED delta, undecomposed) |
| gpt-image-1 icon runs | `art_generated/logs/generation_icons_v1_*.log`, `_v2_*.log` | $0.06/image (v1, 1024px) and $0.24/image (v2, 24 images for $5.76) (MEASURED -- pipeline logs cost per run) |
| gpt-image-1 hero/scene runs | `generation_hero_banners_*.log`, `generation_env_scenes_*.log` | $0.36/image (9 images for $3.24, twice) (MEASURED) |
| gpt-image-1 July 2026 total | all `art_generated/logs/*.log` July runs | $15.78 for 62 images logged; Nov 2025 batches add ~$3.76 for 27 (MEASURED). Known anchor "~91 icons for ~$12" is consistent with the v1/v2 price mix. |
| gpt-image-1 wall-time | icons v1 log timestamps | ~16-19 s/image, sequential (MEASURED) |
| Triage volume | `art_source/pixellab_verdicts.json` (651), `art_source/hero_verdicts.json` (378) | 1029 verdicts recorded via contact-sheet / art-review tool (MEASURED count; no timestamps stored) |

## Unit-cost table

Generation wall-time for PixelLab is AGENT-paced, not Pip-paced: PixelLab
throttles to ~3-4 concurrent jobs ("heavy load" failures above that,
per the 07-16 and 07-19 manifests), each job takes roughly 1-5 minutes
server-side [estimate], and an agent babysits retries. So "wall-time"
below is elapsed clock in an unattended/agent session, near-zero Pip time.

| Asset type | Credits or dollars | Generation wall-time | Pip triage | Integration (Pip or agent+Pip review) |
|---|---|---|---|---|
| 8-dir character (create_character, 64px) | ~4 gens ~= $0.02 (ESTIMATE: 96-gen batch decomposes as 48 props x1 + 10 chars x4 + 5 tilesets x1.6) | minutes/job; a 10-char batch fits in an evening run | ~1-2 min (8 rotations, one gestalt call) ESTIMATE | 30-60 min first time (SpriteFrames + wiring); ~15 min once tooled ESTIMATE |
| 4-dir walk cycle (animate_character) | ~4-8 gens ~= $0.02-0.05 ESTIMATE -- WEAKEST NUMBER: no manifest isolates an animation; frames/request scale with sprite size per PixelLab docs [verify] | minutes/job | ~1-2 min ESTIMATE | 30-60 min per character (frame import + SpriteFrames anims) ESTIMATE |
| Top-down tileset (create_topdown_tileset, 32px Wang) | ~1-2 gens ~= $0.01 (ESTIMATE from 07-19 decomposition; server timeouts forced refires twice, so budget 2x) | minutes, but timeout-prone -- budget retries | ~2-5 min (must check seams, not just look) ESTIMATE | 1-2 h first time (Godot TileSet + Wang autotile from the .json metadata); less after first ESTIMATE |
| Prop, 1-roll mode (create_map_object) | ~1 gen ~= $0.006 (MEASURED: 48 props inside the 96-gen batch) | minutes/job; 48 props = one paced evening | ~0.5-1 min ESTIMATE | 5-10 min via office sandbox placement ESTIMATE |
| Prop, candidate-frames mode (create_1_direction_object, 128px) | ~8 gens ~= $0.05 (MEASURED-ish: ~120 gens / ~13 props, overnight manifest) | overnight batch | +1-2 min (must also pick a candidate frame) ESTIMATE | same as prop above |
| gpt-image-1 icon | $0.06 (v1 quality) to $0.24 (v2 quality) MEASURED | ~20 s/image sequential; 16 icons ~= 6 min | ~0.5-1 min ESTIMATE | mapping entry + wiring: ~5 min/icon amortized in a batch (PR #797 scale) ESTIMATE |
| Hero banner / env scene (gpt-image-1, large) | $0.36 MEASURED | ~30 s/image ESTIMATE | ~1-2 min (hero = brand surface, slower call) ESTIMATE | varies wildly: welcome-screen swap ~15 min; new surface ~hours ESTIMATE |

Triage rate, overall: 1029 verdicts exist. The contact-sheet workflow is
bulk shift-click, so most assets get ~1-2 s and hard calls get ~30 s.
ESTIMATE: 10-20 Pip-minutes per 100 assets triaged, i.e. a 300-asset
sweep is a 30-60 min coffee session. No timestamps were recorded in the
verdict JSONs, so this is calibrated only against "it was done in
sessions, not days" -- treat as +/-2x.

## Worked example: a round-2 sweep

6 x 8-dir characters + 4 x 4-dir walk cycles + 2 x tilesets + 16 x icons:

- PixelLab: 6x4 + 4x6 + 2x2 = ~52 generations ~= 5% of the monthly pool,
  ~$0.31 of subscription value. Pool remaining today (964) covers ~18 such
  sweeps' generation cost -- generations are NOT the bottleneck at this size.
- gpt-image-1: 16 icons x $0.06-0.24 = $1.00-3.85, call it ~$2.
- Generation wall-clock: one unattended evening/overnight agent run for the
  PixelLab jobs (throttle-paced), ~10 min for the icons.
- Pip triage: ~150-250 output images (rotations + candidates) -> ~30-45 min.
- Integration: 6 chars ~2-3 h + 4 walk cycles ~2-4 h + 2 tilesets ~2-4 h
  + 16 icons ~1-1.5 h = ~7-12 h, spread over agent lanes with Pip review.

Headline: dollars ~$2-4 total. Generations ~52 of 2000. Pip-hours dominate
completely: ~0.5-0.75 h triage + several hours of integration review.
The cost model says: generate generously, triage cheaply, and budget the
real spend -- integration lanes -- explicitly in WS-3 planning.

## LIMITS (read before quoting)

MEASURED and safe to quote:
- Current balance (964/2000 gens, $0 credits), 96-gens-for-133-PNGs batch,
  ~120-gens-overnight-props batch, gpt-image-1 per-image dollars and log
  totals, verdict counts (651 + 378).

ESTIMATE with stated derivation (quote with the tag):
- Per-type PixelLab generation costs (decomposed from batch totals, not
  per-job receipts -- PixelLab does not itemize in anything we store).
- The 07-21 reroll ~150 gens (balance interpolation).
- All triage minutes (no timestamps in verdict JSONs) and all integration
  hours (recalled from this week's sandbox/wiring sessions, not clocked).

WEAKEST numbers:
1. Walk-cycle/animation generation cost -- nothing in the manifests isolates
   one; the 07-23..26 ~260-gen delta mixes animations with sandbox rerolls.
   Fix: on the next animation job, note the balance before/after.
2. Subscription price ($12/mo, loyalty to $9) -- third-party sources only
   [verify against the PixelLab account page].
3. Integration hours -- +/-2x at least; they dominate the total, so they are
   the number most worth actually clocking in round 2.

Cheap fixes for round 2 (also serves issue #900's provenance prereq):
record get_balance before/after each batch in the MANIFEST (the 07-19
manifest already did this -- make it the template), and have the review
tool timestamp verdicts so triage rate becomes measured.
