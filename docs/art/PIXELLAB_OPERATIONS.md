# PixelLab operations -- knowledge base for generation lanes

Read this BEFORE running any PixelLab generation lane. Companion docs:
`docs/art/SEED_ART_COST_MODEL.md` (unit costs incl. Pip-time downstream) and
`docs/art/ART_MASTERS_POLICY.md` (where outputs may live). Sources are tagged:

- MEASURED -- balance-bracketed deltas or logs in `art_source/*/MANIFEST.md`.
- SCHEMA -- read directly off the MCP tool schemas (authoritative API surface).
- UI (Pip 2026-07-26) -- Pip's paste from the PixelLab web UI for HIS account;
  not found in any public doc, treat as authoritative for this account.
- [verify] -- third-party reviews only; pixellab.ai/pricing is client-rendered
  and would not yield to fetch (tried direct + pure.md proxy, 2026-07-26).

## 1. Account facts

| Fact | Value | Source |
|---|---|---|
| Tier | **Tier 3 "Pixel Architect"** since 2026-07-26 (upgraded mid cat-sweep; rows below predate it) | get_balance MEASURED |
| Tier 3 pool | 7419 total this cycle; 5884 remaining after the cat-refinement lane | get_balance 2026-07-26 MEASURED |
| Tier 3 concurrency | **20 jobs confirmed** -- over-cap calls atomically rejected with "need N job slots but only M available (K/20 used)"; nothing partial, refire when free | MEASURED cat-refinement lane |
| Tier 3 queue latency | near zero this session (jobs returned in ~1-3 min even 15+ deep); the warm-ramp/priority-slot dance below did not bite | MEASURED cat-refinement lane |
| (pre-upgrade) Tier | Tier 1 "Pixel Apprentice" | get_balance 2026-07-26 |
| (pre-upgrade) Monthly generation pool | 2000/month | get_balance (`generations_total`) |
| (pre-upgrade) Standing (2026-07-26) | 625 remaining, 1375 used this cycle | get_balance MEASURED |
| Pay-as-you-go credits | $0.00 (subscription generations only) | get_balance MEASURED |
| Tier 1 price | $12/month; loyalty discount trends to $9/month | [verify -- third-party reviews] |
| Tier 1 max image size | 320x320 px | [verify -- flowtools review] |
| Tier 2 "Pixel Artisan" | $24/month, 400x400, priority queue, experimental features | [verify] |
| Tier 3 "Pixel Architect" | $50/month, highest priority, up to 20 concurrent jobs, teams | [verify] |
| Credit overflow pricing | basic tools 1 credit/request, some newer models 40 credits/request; $-per-credit rate NOT found | [verify] |
| Monthly pool for Tiers 2/3 | NOT found anywhere public | [verify] |

Always run `get_balance` at lane start and end; record both numbers in your
MANIFEST (the 2026-07-19 and 2026-07-26 manifests are the template). This is
the ONLY way per-operation costs get measured -- PixelLab does not itemize.

At $12 for 2000 generations, one generation ~= $0.006. Dollars are noise; the
real budgets are (a) the monthly generation pool and (b) wall-clock queue time.
Spend policy (Pip, 2026-07-26): generation spend is unconstrained to $100
AUD/day until 2026-08-15 -- rationing is the anti-pattern, queue time is the
real cost.

## 2. Concurrency and priority slots (UI, Pip 2026-07-26)

Facts from the account UI (none of this appears in public docs -- [verify]
against the UI if behaviour seems off):

- **Concurrent job limit: 8** for this account (Tier 1). Tier 3 advertises 20
  [verify].
- **Priority slots** = concurrent jobs that SKIP added queue time. Jobs beyond
  your slot count still run, but wait in queue first.
- **Earning:** run more jobs in parallel than your current slots, sustained for
  30 minutes (30-min average of jobs-over-slots >= 1) -> +1 slot.
- **Decay:** idle for 30 minutes -> -1 slot.
- Standing at time of paste: 0 slots, 6 jobs active (i.e. all 6 were queueing).

### Strategy consequence for agents

The mechanics reward sustained parallel bursts and punish trickling:

- **Batch your whole lane into one sustained burst.** Plan >= 30 min of
  continuous parallel work so the lane EARNS slots as it runs; the back half of
  a long batch runs faster than the front half.
- **Keep <= 8 jobs in flight** (hard limit), but do NOT fire 8 simultaneously
  from cold -- bursts of 8+ submissions fail ~half with "heavy load" (MEASURED
  2026-07-16). Ramp up: submit 3-4, then top the pool back up as jobs return.
  Heavy-load failures are NOT billed (MEASURED 2026-07-26) -- just refire.
- **Never trickle** (one job, wait, one job): you pay full queue time on every
  job and earn nothing.
- **Expect 0 slots at session start.** Slots decay between sessions (30 min
  idle each -1), so the first jobs of a day can queue for many minutes. That is
  normal, not a failure.
- **Polling etiquette:** jobs take ~2-5 min server-side (characters), ~100 s
  nominal for tilesets, ~30-90 s for objects/UI assets (SCHEMA), PLUS queue
  time at 0 slots. Poll with patient exponential backoff (e.g. 30 s -> 60 s ->
  120 s, cap ~5 min); do not tight-loop `get_*` calls. A job that has not
  returned after 10+ min at 0 slots is more likely queued than dead.

## 3. Per-operation cost table (generations)

Nominal = SCHEMA (tool descriptions). Measured = balance-bracketed deltas.

| Operation | Nominal (SCHEMA) | Measured | Notes |
|---|---|---|---|
| create_character, standard | 1 gen | 1 gen/character (2026-07-26, x5) | 4 or 8 dirs, ~2-5 min |
| create_character, v3 | 2-9 gens (scales with size) | -- | always 8 dirs; only mode taking reference_image_base64 |
| create_character, pro | 20-40 gens | -- | always 8 dirs; ignores style params |
| animate_character, template | 1 gen/direction | **~2.1 gens/direction** (17 gens for 8 dir-jobs, isolated 2026-07-26); cat-sweep lane later measured 1.0, but the cat-refinement lane (Tier 3, 2026-07-26) billed 141 vs 76 nominal with 30 template dirs the prime suspect -- NOT isolated | plan at 2/dir; next lane bracket one 8-dir group alone and settle this |
| animate_character, v3 custom | ceil(w*h*frames/65536)/dir; ~1/dir <= 96px, 128px ~2, 160px ~4, 256px ~8 | 1 gen/dir at 68x68 canvas (2026-07-26) | at house 68px canvas, v3 custom costs the SAME as template -- description control is free |
| animate_character, pro | 20-40 gens/direction | -- | frame count fixed by size; requires confirm_cost dance |
| create_character_state | ~20-40 gens/state (quoted by tool) | **21 gens for one state** (2026-07-26 pilot) | NOT a cheap pose source; 3-pose set ~60+ gens |
| create_map_object | -- | ~1 gen/prop (48 props in 96-gen batch, 2026-07-19) | ~15-30 s; results auto-delete after 8 h -- DOWNLOAD IMMEDIATELY |
| create_1_direction_object | 20-40 gens | ~8 gens/kept prop effective (~120 gens / ~13 props, 2026-07-23 overnight) | candidate-frames mode: <=42px -> 64 candidates, <=85 -> 16, <=170 -> 4, else 1; needs select_object_frames/dismiss_review |
| create_8_direction_object | 20-40 gens | -- | props only; do NOT use for characters (identity transfer unreliable -- use create_character v3 + reference) |
| animate_object, v3 | cheap (preferred) | -- | pro is 20-40/dir (160-320 for 8 dirs) -- avoid |
| create_topdown_tileset | -- | ~1-2 gens/tileset (2026-07-19 decomposition) | timeout-prone: budget 2x for refires |
| create_sidescroller_tileset | -- | -- | ~100 s nominal |
| create_isometric_tile | -- | -- | ~1-3 min |
| create_ui_asset | 20-40 gens | -- | ~30-90 s |

## 4. Size / canvas / view reference

### Canvas padding (characters) -- MEASURED

`create_character` pads the canvas ~40% beyond the requested sprite size to
leave room for animation:

- size 48 -> **68x68 canvas** (house standard; the promoted walkers)
- size 64 -> 92x92 canvas
- Default size is 48. Max 128 standard/pro; up to 256 in v3 (SCHEMA).

The 68x68 house canvas is deliberate: it keeps v3 custom animation at
1 gen/direction (the cost formula crosses to 2/dir around 128px).

### Size limits by tool (SCHEMA)

| Tool | Size range |
|---|---|
| create_character | 16-256 (standard/pro max 128; v3 max 256) |
| create_8_direction_object | 32-168 (pipeline rejects larger) |
| create_map_object | 32-400 basic; 192 max with inpainting |
| create_1_direction_object | 32-256 (candidate count depends on size) |
| create_topdown_tileset | tile 16/32; 64 requires mode=pro |
| create_sidescroller_tileset | tile 16/32 |
| create_isometric_tile | 16-64 (above 24 often better quality) |
| create_ui_asset | 192-688, aspect-gated (square <=512x512; 16:9 <=688x384; 4:3 <=600x448) |

### View enums -- reality check (SCHEMA + MEASURED)

`create_character` has exactly FOUR views; there is NO intermediate 3/4-side
between `low top-down` and `side`:

| view | angle | status |
|---|---|---|
| high top-down | ~35 deg from above | works |
| low top-down | ~20 deg, classic 3/4 RPG | **house standard** (humans/scene) |
| side | eye-level | works for E/W; N/S of small quadrupeds biped-izes (issue #912) -- use hybrid per-direction views |
| oblique | 3/4 oblique projection | BETA: max 128px, 4-dir, standard-mode only; **BROKEN for characters** (2026-07-16 V6 distortion) -- do not use |

Other tools differ: `create_map_object` / `create_8_direction_object` use
[low top-down, high top-down, side]; `create_1_direction_object` uses
[top-down, sidescroller]; tilesets use [low top-down, high top-down]. Check
the schema, do not assume the character enum carries over.

Quadrupeds: `body_type=quadruped` REQUIRES `template` (bear, cat, dog, horse,
lion). The `proportions` param is humanoid-only -- for quadrupeds, body shape
is steered by description language only (MEASURED: heft + kawaii probes,
2026-07-26).

## 5. Known failure modes

- **"heavy load" refires:** firing 8+ jobs simultaneously fails ~half. Failed
  jobs are NOT billed. Ramp submissions 3-4 at a time; refire failures.
- **oblique view for characters:** BROKEN (distorts figures). Negative
  evidence on file from 2026-07-16; not a candidate camera angle.
- **Blank-window prompt trap:** "clean/plain office window" collapses to a
  blank washed-out pane unless the prompt forces a dark sturdy frame + distant
  city skyline (2026-07-26 round2, rolls 1-4 vs 5+). Generalization: sparse
  "plain X" prompts under-constrain; anchor with concrete structural elements.
- **Tileset timeouts:** top-down tileset jobs time out server-side under load
  and need refires (2026-07-19: terrain-transition wall tilesets timed out
  twice). Budget 2x generations and wall-time for tileset lanes.
- **Map objects auto-delete after 8 hours.** Download every PNG in-lane;
  never plan to "come back tomorrow" for create_map_object output.
- **Side-view N/S quadruped walks go bipedal** (issue #912): eye-level fore/aft
  views of a ~34px quadruped hide the leg pairs and the model verticalizes.
  Prompt language ("all four paws on the ground") does NOT fix it. Fix: hybrid
  per-direction views (low top-down for N/S, side for E/W).
- **v3 action-prefix dedupe:** a new v3 animation whose action_description
  OPENS with the same phrase as an existing group on the same character +
  direction is rejected as "already queued or complete (nothing re-queued)"
  even when the rest of the description differs. Reword the opening words,
  not the tail. Rejections are unbilled (MEASURED 2026-07-26 refinement).
- **8-dir object tool for characters:** reference sprite loses the salience
  contest against placeholder characters; output resembles a generic
  character. Use `create_character(mode="v3", reference_image_base64=...)`.
- **White-flash matting under paws/feet (HOUSE PROMPT RULE, ruled
  2026-07-26):** walk frames can carry stray near-white background pixels
  under the body mid-stride. EVERY walk/action prompt for characters and
  cats carries clean-alpha language ("clean transparent background under
  paws/feet in every frame, no white halo"), and lanes verify with a PIL
  scan (near-white pixels in the lower third under the silhouette) before
  accepting; violations re-roll. Applies to workers AND cats.

## 5b. Skeleton keypoints (raw API, outside the MCP surface)

`POST /estimate-skeleton` (verified in the pixellab-python SDK source,
2026-07-26): one transparent-background character image in ->
`keypoints: [{x, y, label, z_index}]` out, over an 18-label set (NOSE,
NECK, L/R SHOULDER/ELBOW/ARM/HIP/KNEE/LEG, L/R EYE, L/R EAR). Powers the
anchor-track harvest for effect sockets (see
docs/art/ANCHORS_AND_EFFECTS_PRIMER.html section 5). Notes: bills in USD
API credits, NOT subscription generations (SDK usage type "usd"); label
set is humanoid-shaped -- no TAIL keypoint (tail tracks come from
annotation); what labels a quadruped/cat frame returns needs one live
probe before a bulk harvest; needs the PixelLab API key (raw HTTP, not
available through the MCP tools).

## 6. HOW LANES SHOULD RUN -- checklist

Before:
1. Read this doc + `docs/art/SEED_ART_COST_MODEL.md`.
2. `get_balance`; record the number in your MANIFEST draft.
3. Plan the WHOLE batch up front (every job you will fire), sized so the lane
   sustains >= 30 min of parallel work in one burst. If the batch is smaller
   than that, consider merging with another lane's queue rather than trickling.
4. Sanity-check per-op costs against Section 3 (plan template walks at
   ~2 gens/direction; treat character states and 1-dir candidate props as
   20-40 gen items).

During:
5. Ramp to 3-4 jobs in flight, top back up toward <= 8 as jobs return. Never
   exceed 8; never fire a cold burst of 8+.
6. Poll with exponential backoff (30 s -> 60 s -> 120 s, cap ~5 min). Queued
   != dead, especially at session start (0 slots).
7. Refire "heavy load" failures (unbilled). Refire timed-out tilesets.
8. Download every output PNG as jobs complete (8-hour auto-delete on map
   objects; do not batch downloads for later).
9. Isolate cost measurements when convenient: run one op type with nothing
   else in flight and bracket with `get_balance` (this is how the 2.1/dir and
   21-gen-state numbers were caught).

After:
10. `get_balance` again; write before/after + delta decomposition into the
    batch MANIFEST (`art_source/<batch>/MANIFEST.md`).
11. Record pixellab IDs (character/object/group) in the MANIFEST -- they are
    the only handle for re-animating or state-varianting later.
12. Update THIS doc if a measured number contradicts Section 3, and
    `SEED_ART_COST_MODEL.md` if a WEAKEST-number gap got filled.

## Open [verify] items

- Tier 1 price ($12/mo, loyalty to $9) and 320x320 size cap -- third-party only.
- Tier 2/3 monthly generation pools -- not published anywhere found.
- Credit overflow $-rate -- unknown; account has $0 credits so untested.
- Priority-slot earn/decay mechanics -- single-source (Pip's UI paste); no
  public doc describes them. Re-check the UI if queue behaviour changes.
- Monthly pool reset date for this account -- not exposed by get_balance.
