# Pixellab size vanguard probe -- 2026-07-26

Feeds Pip's after-lunch sprite-scale review: does the accessory richness the
house wants (lanyard + ID badge, glasses, distinctive hat) survive at the
current size-48 standard, or does it need the size-64 canvas? THE SAME worker
description at three generation sizes so size is the only dial. Data-only
round: NOTHING here is wired into godot/.

Review sheet: `art_generated/size_probe_sheet.html` (regenerate with
`python tools/art_review/gen_size_probe_sheet.py`; images are embedded as data
URIs so the copy in the main checkout works before this art lands there).

## Generation settings (identical across sizes)

`create_character` standard mode, humanoid, low top-down, 8 directions,
single color black outline, high detail, basic shading. Stills only -- no
walks (probe, not production). Description (the accessory-richness test):

    office worker, medium-skin-tone man, distinctive mustard-amber knit
    beanie, round dark-rimmed glasses, muted olive button-up shirt over
    slate trousers, dark teal lanyard around neck with a small white ID
    badge clipped at the chest

## The ladder

| folder | gen size | canvas | pixellab id |
|---|---|---|---|
| size_48/ | 48 (house standard) | 68x68 | 31d5c001-5124-4d51-9d53-daea3d07b76d |
| size_64/ | 64 | 92x92 | d4d59ad0-4a61-4f8f-9e45-f127926820f9 |
| size_32/ | 32 (bottom rung) | 48x48 | a64f638f-fada-48e5-917f-2c2f4c59d325 |

Canvas note: the documented ~40% pad predicts 44/45 for size 32; the API
actually emitted a **48x48** canvas -- the pad rounds up at the small end.
size_32/metadata.json records the observed value.

Each folder: `rotations/{south,...}.png` (8 stills) + `metadata.json`
(generation params + id).

## Sheet display math (64px-tile floor)

"tiles tall" = subject px * display multiple / 64; tile art stays at face
value, only the sprite multiple varies.

| config | subject on screen | tiles tall |
|---|---|---|
| size-48 @ 2x | 96px | 1.50 |
| size-48 @ 3x | 144px | 2.25 |
| size-64 @ 2x | 128px | 2.00 |
| size-32 @ 4x | 128px | 2.00 |

## Generation cost (pixellab)

- Balance BEFORE round: **869 generations remaining** ($0.00 credits, Tier 1
  Pixel Apprentice, 2000 total).
- Balance AFTER round: **5952 remaining** -- NOT comparable: the subscription
  was upgraded to **Tier 3 Pixel Architect (7419 total)** mid-round, and a
  sibling agent lane was generating on the shared account concurrently
  (observed 869 -> 633 while all of this lane's jobs were failing).
- Attributable cost of THIS round: **3 generations** (3 billed standard-mode
  characters at 1 gen each). Seven "heavy load" failures across the round were
  NOT billed (consistent with the round-2 observation).
- Ops datapoint: the heavy-load failures correlated with the sibling lane
  saturating the shared account's concurrency -- serialized single jobs got
  through where 3-at-once batches failed twice. Failed job ids: fbf6c255,
  3a119eaa, 6b208c25 (batch 1), 3ca8b46a, 6089d501, 67e656f4 (batch 2),
  2dce7bd8 (solo, pre-upgrade).
