# Cat experiment B -- 2026-07-26 (issues #900 #912 #913)

Follow-up batch to the angle A/B (`art_source/pixellab_2026-07-26_cat_angle_ab/`).
Pip's A/B verdicts drove four probes:

1. **Heft retry** -- side E/W won but the A/B side cat read lanky vs the old
   low-top-down walker. Fix attempted via description language only.
2. **N/S candidates** -- the A/B side-view north/south walks were bipedal
   (issue #912, "bipedal horror", rejected for normal play). Two competing
   answers generated for the SAME tabby: (a) hybrid per-direction views (low
   top-down cat for N/S only -- renderer supports per-clip views); (b) side
   view retried ONCE with aggressively quadruped-grounded v3 descriptions.
3. **Butt-flash loop** -- occasional-use alternate "away" walk with tail-up
   rear visibility for the splice mechanic (issue #913; art only, the
   renderer splice is another lane).
4. **Kawaii probe** -- baby-schema proportions (bigger head ratio, larger
   eyes, rounder forms) via description, stills only. The API `proportions`
   param is humanoid-only, so description language is the only dial for
   quadrupeds.

## Generation parameters

Common: `create_character` mode `standard`, `body_type=quadruped`,
`template=cat`, 8 directions, size 48 (68x68 canvas -- house standard),
single color black outline, high detail, basic shading.

| subject | pixellab id | view | description prompt |
|---|---|---|---|
| tabby_side_heft | 42976b8d-6b3c-4fb0-ab9e-4acbb90abb43 | side | stocky chunky orange tabby cat with darker orange stripes, solid heavy body mass, thick barrel-shaped torso, broad chest, short sturdy legs, weighty stance, faintly singed fur, cream muzzle and paws, cozy pet cat, warm bright colors, cartoony retro RPG style, pixel art |
| tabby_lowtd_heft | 3bd14ec5-56d2-417e-ba15-293cec950089 | low top-down | (same heft description) |
| tabby_side_kawaii | a4f072ed-977d-4ea7-9a13-29f5b67523ab | side | adorable baby kitten-proportioned orange tabby cat, oversized round head much bigger than body, huge sparkling round eyes, tiny chubby rounded body, stubby little legs, darker orange stripes, cream muzzle and paws, kawaii cute, warm bright colors, cartoony retro RPG style, pixel art |

## Animation jobs

| clip | character | mode | directions | frames | group id | notes |
|---|---|---|---|---|---|---|
| walk_ew_heft | tabby_side_heft | template `walk-8-frames` | east, west | 8 | 3469af36-d45d-4887-b2d9-b946b725771b | heft retry; one-dial vs A/B side walk |
| walk_north_side_v3_grounded | tabby_side_heft | v3, "cat walking directly away from the viewer, all four paws on the ground, quadruped on all fours, tail raised, seen from behind at eye level, natural feline walking gait" | north | 9 (ref+8) | 4a8b9589-340f-4d04-8132-089793fb81f3 | the one-more-try side N/S |
| walk_south_side_v3_grounded | tabby_side_heft | v3, "cat walking directly toward the viewer on all four legs, all four paws on the ground, quadruped feline gait, seen from the front at eye level, head facing camera" | south | 9 (ref+8) | aca9289e-4332-4d18-901a-9b5b59dd1c3a | |
| walk_ns_lowtd | tabby_lowtd_heft | template `walk-8-frames` | north, south | 8 | 97c17fec-0aed-4925-9c31-38f1dc5835fb | hybrid candidate (a) |
| butt_flash_north | tabby_lowtd_heft | v3, "cat walking away from the viewer with its tail held straight up high in the air, rear end visible under the raised tail, all four paws on the ground, jaunty confident strut" | north | 9 (ref+8) | db7a3ffc-fbbc-4d32-b8be-39c4847b4b4a | issue #913 splice-in |

## Credits (isolated deltas)

| checkpoint | generations remaining | delta | what it bought |
|---|---|---|---|
| before | 928 (1072/2000 used) | -- | -- |
| after 3 character creates | 925 | 3 | 1 gen per standard create |
| after all 7 animation jobs | 918 | 7 | template walk = 1 gen/direction (4 dirs); v3 custom = 1 gen/direction at 68x68 (3 clips) |

**10 generations total**; $0.00 credits; Tier 1 subscription only. Cost-model
note: at the 68x68 house canvas, v3 custom animation is the SAME price as
template walk (1 gen/dir) -- description control is free at this size.

## Verdict-relevant notes (lane eyeball, pre-Pip)

| probe | read |
|---|---|
| heft E/W | WORKED. Visibly chunkier low-slung barrel body, short legs, weighty gait vs the lanky A/B side walker. Silhouette now closer in mass to the old low-top-down walker while keeping the side-view leg readability. |
| N/S (a) low top-down hybrid | WORKED. North reads as a proper quadruped cat from behind (striped back, haunches, tail flick); south walks toward camera tail-up, cute. Clean drop-in for the hybrid per-direction scheme. |
| N/S (b) side v3 grounded | STILL BIPEDAL-LEANING. Despite "all four paws on the ground" language the north walk verticalizes into a tall two-legged stride (tail improved, rump more feline than the A/B horror, but the columnar silhouette persists). South is better (face-on, front paws stepping) but still tall. Empirical answer: eye-level fore/aft views of a 34px quadruped hide the leg pairs and the model biped-izes -- the side view is structurally wrong for N/S. Closes the question: use the hybrid. |
| butt_flash | USABLE, splice-window quality. Frames 0-3 = normal rear walk (frame 2 shows the round rear + visible butt detail -- the joke lands); tail rises and holds straight up frames 4-8. As a raw 9-frame loop the tail pop-up reads abrupt; recommend the renderer splice frames ~2-8 (or hold 4-8) rather than looping all 9. |
| kawaii probe | STRONG DIFFERENTIATION. Head ratio and eye size clearly up, body rounder/chubbier with stubby legs; reads as a kitten/plush next to the heft adult at both 1x and 2x. Probably OVER the 15% brief (closer to chibi) -- if Pip wants a subtler dial, next probe should soften "oversized/much bigger than body" to "slightly larger". |

## Files (83 PNGs, all 68x68)

- `tabby_side_heft/rotations/{8 directions}.png` (8)
- `tabby_side_heft/walk_ew/walk_{east,west}_{0..7}.png` (16)
- `tabby_side_heft/walk_ns_v3/walk_{north,south}_{0..8}.png` (18; frame 0 = rotation ref)
- `tabby_lowtd_heft/rotations/{8 directions}.png` (8)
- `tabby_lowtd_heft/walk_ns/walk_{north,south}_{0..7}.png` (16)
- `tabby_lowtd_heft/butt_flash/butt_flash_north_{0..8}.png` (9; frame 0 = rotation ref)
- `tabby_side_kawaii/rotations/{8 directions}.png` (8)

## Comparison sheet

`art_generated/cat_b2_sheet.html` (gitignored derived output; regenerate with
`python tools/art_review/build_cat_b2_sheet.py`) -- heft retry vs lanky A/B
side cat vs old16 walker, all four N/S candidates animated side by side
(including the rejected bipedal reference), butt-flash player, kawaii vs adult
proportions, filmstrips, all on the office floor tile.

## References used on the sheet

- Old promoted walker: `art_source/pixellab_2026-07-16/cat_walk_cat1/` + `15-Cat1-singed-tabby_*.png`
- Lanky A/B side cat: `art_source/pixellab_2026-07-26_cat_angle_ab/cat1_tabby_side/` (incl. the rejected bipedal N/S walk, kept per issue #912)
