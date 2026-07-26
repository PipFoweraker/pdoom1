# Cat sweep -- full 8-direction batch, 2026-07-26 (issues #900 #913)

Execution of Pip's locked recipe (ruled 2026-07-26, "go cat sweep 8 dir now"):

- **east/west = SIDE view** with heft description language (the cat_b2 heft
  retry worked; its description style is reused verbatim as the template).
- **north/south = LOW TOP-DOWN** -- the empirically settled quadruped-correct
  answer. Side-view N/S is NEVER shipped (bipedal horror, issue #912; the
  evidence lives in `pixellab_2026-07-26_cat_b2/`).
- Every cat gets a **full 8-direction low-top-down walk baseline**.
- **Tabby only**: side-view DIAGONAL walks (NE/SE/NW/SW) as the
  mixing-boundary probe -- the sheet pairs side vs lowtd per diagonal so Pip
  can judge where the side<->lowtd handoff should sit.
- **Butt-flash (issue #913)**: tail-up rear walk loops for tabby (cat_b2
  reuse) and black; renderer should splice frames ~2-8, not loop all 9.

## Reuse discipline (nothing regenerated that existed)

| piece | source | note |
|---|---|---|
| tabby side heft char + E/W walk | cat_b2 `42976b8d` | 4 diagonal walks APPENDED to the existing walk group |
| tabby lowtd heft char + N/S walk + butt-flash | cat_b2 `3bd14ec5` | 6 remaining walk directions APPENDED to the existing group |
| black lowtd char | existing `cat_black` `28157d2a` (68x68, low top-down) | walk-less before this batch |
| eldritch lowtd char | existing `cat_eldritch_r2` `d13a61ca` | walk-less before this batch |
| purple lowtd char | existing `cat_purple_r2b` `c82bf943` | walk-less before this batch |

Each character folder carries its API `metadata.json` (original creation
prompt + params -- provenance for the reused cats; e.g. cat_purple_r2b's
original prompt confirms "glowing purple eyes", which the new side-heft
purple deviates from).

New characters (side-view heft trio): `create_character` mode `standard`,
`body_type=quadruped`, `template=cat`, 8 directions, size 48 (68x68 canvas),
view `side`, single color black outline, high detail, basic shading -- the
exact cat_b2 heft parameter set.

| subject | pixellab id | description prompt |
|---|---|---|
| cat_sweep_black_side_heft | 55bf4986-ac8e-4419-bce6-aeb6892e0c56 | stocky chunky fluffy black cat with amber orange eyes, dark charcoal fur, solid heavy body mass, thick barrel-shaped torso, broad chest, short sturdy legs, weighty stance, slightly grumpy expression, cozy pet cat, warm bright colors, cartoony retro RPG style, pixel art |
| cat_sweep_eldritch_side_heft | 66cbb621-871d-4de4-b364-ba449d57ef21 | stocky chunky jet black eldritch cat with glowing violet purple eyes, faint purple glow accents on face, pale lavender collar ruff, solid heavy body mass, thick barrel-shaped torso, broad chest, short sturdy legs, weighty stance, subtly unsettling otherworldly aura, dark fur, cartoony retro RPG style, pixel art |
| cat_sweep_purple_side_heft | dc619504-20f9-48ef-a5d6-5a5cd2022991 | stocky chunky cat with deep violet purple-black fur, purple sheen mottling on coat, bright purple collar, glowing purple eyes, solid heavy body mass, thick barrel-shaped torso, broad chest, short sturdy legs, weighty stance, cozy pet cat, cartoony retro RPG style, pixel art |

Known colour deviation: the purple side cat came back with orange-red eyes
where the lowtd base reads purple-eyed. Left as-is (1-gen reroll not spent);
flag on the sheet verdict if it matters.

## Animation jobs

All template jobs are `walk-8-frames` (8 frames/direction, 1 gen/direction);
v3 jobs are 9 frames (ref + 8), 1 gen/direction at the 68x68 canvas.

| clip | character | mode | directions | group id | notes |
|---|---|---|---|---|---|
| walk_side_diag_probe | tabby side `42976b8d` | template | NE, NW, SE, SW | 3469af36-d45d-4887-b2d9-b946b725771b | APPENDED to the cat_b2 E/W walk group -- one 6-dir side walk |
| walk (lowtd fill) | tabby lowtd `3bd14ec5` | template | E, W, NE, NW, SE, SW | 97c17fec-0aed-4925-9c31-38f1dc5835fb | APPENDED to the cat_b2 N/S group -- full 8-dir baseline |
| walk_8dir_lowtd | cat_black `28157d2a` | template | all 8 | 3e9b2572-1723-4502-b0c2-6be2793499e7 | template NORTH misfired face-on (see below) |
| walk_north_fix | cat_black `28157d2a` | v3, "black cat walking directly away from the viewer on all four legs, seen from behind, only the back of the head and ears and tail visible, no eyes visible, natural feline walking gait" | north | b85baa2b-9f75-4985-95a8-83b2f994d48e | the 1-gen surgical fix; USE THIS for black north |
| butt_flash_north | cat_black `28157d2a` | v3, same prompt as the cat_b2 tabby butt-flash | north | 6f84f1c1-09ab-4314-bd49-a0a2be66b988 | issue #913; splice frames ~2-8 |
| walk_8dir_lowtd | cat_eldritch_r2 `d13a61ca` | template | all 8 | ad93b80a-a39d-4a53-9fb3-c3ce22e50896 | north OK (back view) |
| walk_8dir_lowtd | cat_purple_r2b `c82bf943` | template | all 8 | 3cce4521-9ec5-4ae7-9985-ba85010c954f | north OK (back view) |
| walk_ew (+diag) | black side `55bf4986` | template | E, W + NE, NW, SE, SW | 84b921af-7ac6-4d4c-852b-73a918034ba2 | diagonals appended in the cap-lift expansion |
| walk_ew (+diag) | eldritch side `66cbb621` | template | E, W + NE, NW, SE, SW | 06fef615-656a-4e87-a1a7-5bd5e4d53806 | " |
| walk_ew (+diag) | purple side `dc619504` | template | E, W + NE, NW, SE, SW | f255ff34-f31e-43e7-acc3-c1ce1735c678 | " |
| butt_flash_north | cat_eldritch_r2 `d13a61ca` | v3, same prompt | north | b2288003-535a-4373-82a4-5cf48e45796c | cap-lift expansion |
| butt_flash_north | cat_purple_r2b `c82bf943` | v3, same prompt | north | 2d71119f-2f78-42b7-9f2d-335395cbd273 | cap-lift expansion |
| sitting (south) | all 4 lowtd cats | template `sitting` | south | ec3fcda9 (tabby) / f316f814 (black) / dbfebd9e (eldritch) / 2b4cf51d (purple) | cap-lift flourish |
| licking (south) | all 4 lowtd cats | template `licking` | south | 9cb49f6e (tabby) / b6c3140e (black) / 31de71e5 (eldritch) / 8502cd99 (purple) | cap-lift flourish |

## Cap-lift expansion (mid-batch policy change)

Pip lifted generation spend caps mid-batch ("spend freely, bias to more
options/extras; do not ration"). Additions on top of the original recipe:
butt-flash for ALL four cats (not just tabby+black), side-view diagonal
walks for ALL four cats (so a diagonal-mixing ruling applies to the whole
roster immediately), and sitting + licking south flourish clips per lowtd
cat (office cats spend most of their time not walking). Nothing was ever
cut for budget.

## Template-north misfire (cat_black only)

The `cat_black` template walk NORTH came back walking TOWARD the viewer
(amber eyes visible) despite a correct back-view north rotation -- the other
seven directions and both other lowtd cats were fine. Cost of fix: 1 gen via
v3 with grounded away-from-viewer language (the north rotation is the v3
reference frame, which keeps it back-facing). Both clips are kept in
`cat_black/animations/` (`walking/north` = the broken template evidence,
`walk_north_fix/north` = the usable clip); the sheet builder prefers the fix.

## Credits (cat lane -- isolated deltas)

| checkpoint | generations remaining | delta | what it bought |
|---|---|---|---|
| batch start | 898 | -- | -- |
| after 3 side creates + first 20 walk dirs | 875 | 23 | 1 gen per create, 1 gen per direction (template AND v3) at 68x68 -- re-confirms the cat_b2 cost model; the older "~2.1 gens/direction" planning figure is obsolete |
| cat lane total | -- | **45** | 3 creates + 42 animation directions (34 template walk dirs on new groups, 6 appended dirs, 1 butt-flash, 1 north fix) |

Animation gens/direction datapoint: **1.0 measured** (45 jobs, 45 gens),
both template and v3 custom, at the 68x68 house canvas.

Cap-lift expansion added ~22 more cat gens (2 butt-flash + 12 diagonal
dirs + 8 flourish clips) -> **cat lane ~67 gens total**. Nothing was ever
cut. Mid-expansion Pip upgraded the account to Tier 3 (pool 2000 -> 7419);
the plan-independent `generations_used` counter went 1102 -> 1394 across
the whole batch = **292 gens both lanes** (overlay lane table in
`../pixellab_2026-07-26_doom_overlays/MANIFEST.md`); 6025 remaining at
close.

## Files (637 PNGs, all 68x68)

Zip-native layout per character (`{char}/rotations/*.png`,
`{char}/animations/{group}/{direction}/frame_*.png`; template walks = 8
frames, v3 clips = 9 with frame_000 = rotation ref):

- `cat_b2_tabby_side_heft/` 56 -- 8 rot + walk_side_diag_probe 6 dirs x 8
  (E/W from cat_b2 + the 4 new diagonals, one group)
- `cat_b2_tabby_lowtd_heft/` 101 -- 8 rot + walk_ns_lowtd 8 dirs x 8 +
  butt_flash_north 9 + sitting 10 + licking 10
- `cat_black/` 110 -- 8 rot + walking 8 dirs x 8 + walk_north_fix 9 +
  butt_flash_north 9 + sitting 10 + licking 10
- `cat_eldritch_r2/`, `cat_purple_r2b/` 101 each -- 8 rot + walk 8 dirs x 8
  + butt_flash_north 9 + sitting 10 + licking 10
- `cat_sweep_{black,eldritch,purple}_side_heft/` 56 each -- 8 rot + walk
  6 dirs x 8 (E/W + 4 diagonals; the eldritch/purple zips emitted the
  merged group under a second name, deduplicated on land)

Tabby rotations + E/W + N/S + butt-flash frames overlap with
`pixellab_2026-07-26_cat_b2/` (same pixels, different layout) -- duplicated
here deliberately so the sweep folder is self-contained for the sheet
builder (the generations were NOT re-spent; layout is from the character
zip download).

## Comparison sheet

`art_generated/cat_sweep_sheet.html` (gitignored derived output; regenerate
with `python tools/art_review/build_cat_sweep_sheet.py`) -- built on the
shared `tools/art_review/review_style.py` house module: verdict chips +
hide-on-verdict, animated players per cat per direction-set on floor strips,
the tabby diagonal mixing-boundary section, butt-flash players + filmstrips.
