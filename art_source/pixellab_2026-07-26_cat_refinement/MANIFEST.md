# Cat refinement batch -- 2026-07-26 (issues #900 #912 #913 #923)

Execution of Pip's cat-sweep review rulings (2026-07-26, clip-level verdicts
folded in PR #935). Sources of truth: this MANIFEST + the per-character
`metadata.json` files (zip-native layout, same convention as
`../pixellab_2026-07-26_cat_sweep/`).

## Dispositions

| ruling | disposition |
|---|---|
| cat_purple ("large purple cat with white collary thing can go") | **RETIRED.** No regeneration. `cat_purple_r2b` (`c82bf943`) and `cat_sweep_purple_side_heft` (`dc619504`) stay in the sweep folder as archive; nothing purple in this batch. |
| white-flash walk clips | re-rolled via v3 with clean-alpha language; per-clip verification below |
| tabby lowtd north tail-spaz | re-rolled (`walk_north_tailfix`) |
| tabby lowtd south "sashaying a little hard" + could be 2-3px taller | re-rolled (`walk_south_calmtall`) |
| sitting/licking (ALL old versions disliked -- cramped motion) | REDONE at 16 frames v3 with explicit motion arcs, all surviving cats + new roster |
| butt punctuation ("without the little starfish") | prompt attempt + deterministic PIL stamp -- see below |
| new roster | stripey brown, kambu_placeholder (superseded later per issue #923), fat marmalade chonker |

## White-flash forensics (before re-rolling)

Pip: "weird little flashes of white under the cats as they walked". Frame
forensics (tools/art_review/scan_white_flash.py) found the artifact is
intermittent pale pixels in the under-body zone, three shapes:

| clip | scan of the OLD (disliked) clip |
|---|---|
| cat_sweep_black_side_heft walk west | pale shadow ellipse RGB ~(212,198,196) drawn in frames 1/4/7 only -- 96 temporal flash-px |
| cat_eldritch_r2 walk east | stuck near-white fleck at (41,36), present every frame + 3 flash-px |
| cat_eldritch_r2 walk west | intermittent fleck at (25,37) -- 1 flash-px |
| cat_b2_tabby_lowtd_heft walk east / west | cream belly-line flicker -- 145 flash-px each (liked south/north walks score 71/67 from moving cream paws, so treat scores comparatively) |
| cat_black walk NE/SE/SW/NW | **NO in-sprite white at all** (max in-sprite min(R,G,B) = 44 across all frames/pixels). Whatever flashed on the sheet there is not sprite matting -- most plausibly the light floor tile showing through the flickering leg gaps of a black cat. Re-rolled anyway per the ruling. |

## Re-roll verification (scan of the NEW clips + 4x contact-strip eyeball)

Scanner caveat re-confirmed: the temporal count is COMPARATIVE -- coats with
cream/white markings (tabby, kambu) score high from legitimately moving
bright anatomy; the eyeball decides. v3 clips carry frame_000 = the rotation
reference still, which is NOT part of the loop (splice 1-8) -- the blackside
reading below is entirely that reference frame.

| new clip | scan | eyeball verdict |
|---|---|---|
| blackside walk_west_cleanfix | 91 flash-px, ALL from frame_000 (the reference rotation carries a baked-in grey shadow ellipse at y=45-46); frames 1-8 = 0 | CLEAN in the loop window; the old mid-walk shadow flashes are gone |
| cat_black walk_diag_cleanfix NE/SE/SW/NW | 0 / 0 / 0 / 0 | CLEAN (the old diagonals also scanned 0 -- see counter-finding above -- but the re-rolls are darker-grounded and smoother) |
| eldritch walk_ew_cleanfix west | 0 | CLEAN |
| eldritch walk_ew_cleanfix east | 6 transient bib-edge px | old STUCK fleck gone; residual bib flicker judged borderline -> second roll |
| eldritch walk_east_cleanfix2 | 17 px (bib flicker moved, not removed) | collar-stability language did NOT beat roll 1; BOTH offered on the sheet, v1 recommended |
| tabby walk_ew_cleanfix east / west | 201 / 154 px | CLEAN to the eye -- cream chest/paw boundary moving naturally (attached anatomy, not stray flecks); visibly cleaner than the old belly-line flicker |
| tabby walk_north_tailfix | -- | tail holds ONE low relaxed curve, no frame-to-frame jumps |
| tabby walk_south_calmtall | -- | reads taller + calmer, modest sway; frame 3 has a 1-frame tongue-blep (kept -- flag if unwanted) |
| new roster walks (30 dirs) | all HITS at cream-paw-level counts; kambu stuck flecks = its own white patch edges | eyeballed: no shadow-blob class artifacts; kambu/marmalade bright pixels are coat markings |

## Butt punctuation (issue #913 follow-up)

Two paths, both landed for comparison:

1. **Prompt language** (`butt_flash_dotted` groups): v3 re-roll with "one
   single tiny dark dot marking the anus right below the tail base".
   Result (tabby, pixel-verified): the model DID render a 1px grey dot
   (152,152,148) at (34,39-41) tracking the body bob -- in 5 of the 6
   tail-up frames (frame 7 missed). So prompt language CAN hit ~1px at the
   68px canvas but is per-frame unreliable and low-contrast. The marmalade
   prompt roll drew a whole cream butt-patch with a pink dot (bolder than
   asked; on the sheet). VERDICT: prompt path = partial; deterministic
   stamp = the dependable path.
   API note: the v3 dedupe rejects a new animation whose action description
   shares its opening phrase with an existing group on the same character +
   direction ("already queued or complete (nothing re-queued)") -- reworded
   openings queue fine. Cost of discovery: 0 gens (rejections are free).
2. **Deterministic PIL stamp** (`tools/art_review/butt_dot_stamp.py`):
   rump-run anchor (lowest row whose longest opaque run >= 12 px), 2x1 dot
   at (run centre, rump_bottom - 2), stamped only over opaque pixels;
   contrast-aware shade (dark warm brown (43,26,23) on light/mid coats,
   muted pink-brown (98,62,58) on black fur so the dot reads). Flash window
   picked per clip by eyeball: tabby 4-8, black 3-8, eldritch 4-8, stripey
   1-8, kambu 1-8, marmalade 4-8. Verified on 8x zoom grids for all six.
   Output lands as `butt_flash_stamped` groups (existing cats stamped from
   the LIKED sweep clips; new cats from their `butt_flash_dotted` rolls).

## New roster (locked recipe: side-heft E/W + lowtd N/S + 8-dir lowtd baseline + butt-flash; REGULAR looks, standard eyes)

`create_character` mode `standard`, `body_type=quadruped`, `template=cat`,
8 dirs, size 48 (68x68 canvas), `single color black outline`, `high detail`,
`basic shading` -- the exact cat_b2 heft parameter set. Views: side (E/W
lane) + low top-down (everything else).

| subject | pixellab id | view | description prompt |
|---|---|---|---|
| cat_ref_stripey_side_heft | e27412ed-fbed-43ed-a86b-2bbc0fef1d55 | side | stocky chunky brown striped cat with bold dark chocolate brown stripes over a warm tan-brown coat, distinct brown tabby striping, solid heavy body mass, thick barrel-shaped torso, broad chest, short sturdy legs, weighty stance, cream muzzle and paws, cozy pet cat, warm bright colors, cartoony retro RPG style, pixel art |
| cat_ref_stripey_lowtd | c17642a3-552e-4e0c-9f38-7fe6dc57dd77 | low top-down | (same) |
| cat_ref_kambu_placeholder_side_heft | 5cc3c3a8-17e5-409d-bb51-42557d56d6c5 | side | stocky chunky cat with large irregular white blotches and patches over a dark grey coat, patchy piebald bicolor pattern, solid heavy body mass, thick barrel-shaped torso, broad chest, short sturdy legs, weighty stance, pink nose, cozy pet cat, warm bright colors, cartoony retro RPG style, pixel art |
| cat_ref_kambu_placeholder_lowtd | dfe42fba-11e6-4910-9ba1-e6035b5c6fba | low top-down | (same) |
| cat_ref_marmalade_side_heft | a4b9d8ae-df72-42c6-af58-00e96dddc4f9 | side | enormously fat marmalade orange cat, emphatically chonky and heavyset, very round wide body with a huge low-slung belly, broad jowly face with magnificent long white whiskers, rough scruffy alley tomcat look, deep orange marmalade fur with darker orange markings, short sturdy legs under a massive round body, weighty stance, cozy pet cat, warm bright colors, cartoony retro RPG style, pixel art |
| cat_ref_marmalade_lowtd | 9eb8ed03-a8db-43eb-9c57-f6870b432907 | low top-down | (same) |

kambu_placeholder note: the real Kambu spec arrives later via photos (issue
#923); this cat is a stand-in and will be superseded.

Body-range ruling applied: cats may span "skinny lankers and hefty chonkers";
the marmalade is prompted emphatically chonky (Scarface Claw archetype --
Hairy Maclary's nemesis: rough, heavyset, magnificent whiskers).

## Animation jobs

Existing characters (fix re-rolls; all v3, 68x68 canvas, walks 9f = ref+8,
flourishes 17f = ref+16):

| clip | character | directions | group id | prompt gist |
|---|---|---|---|---|
| walk_west_cleanfix | cat_sweep_black_side_heft `55bf4986` | W | 63cc88ab | clean-alpha walk (no white under paws/belly) |
| walk_diag_cleanfix | cat_black `28157d2a` | NE SE SW NW | 417977c8 | clean-alpha diagonal walk |
| walk_ew_cleanfix | cat_eldritch_r2 `d13a61ca` | E W | 82084332 | clean-alpha walk |
| walk_ew_cleanfix | cat_b2_tabby_lowtd_heft `3bd14ec5` | E W | 2084d2d6 | clean-alpha walk |
| walk_north_tailfix | tabby lowtd | N | 7473dafe | tail in one smooth continuous curve, no jumps |
| walk_south_calmtall | tabby lowtd | S | 1ddbeb01 | minimal hip sway, body carried slightly taller |
| sitting_v2 | tabby / black / eldritch | S | 392b0b45 / 42e5ad38 / dbd7c0ac | 16f motion arc: stand -> haunches lower -> settle -> weight shift -> tail wrap |
| licking_v2 | tabby / black / eldritch | S | 14f05d95 / 6b06f09d / e8e593a5 | 16f motion arc: head dip -> 3 tongue strokes -> pause -> resume |
| butt_flash_dotted | tabby lowtd | N | 950bccbc | tail-up strut + explicit tiny dark dot language |

New characters:

| clip | character | mode | directions | group id |
|---|---|---|---|---|
| walk_ew | stripey side | template walk-8-frames | E W | c086672c |
| walk_8dir_lowtd | stripey lowtd | template walk-8-frames | all 8 | d8759a43 |
| walk_ew | kambu side | template walk-8-frames | E W | bba1070a |
| walk_8dir_lowtd | kambu lowtd | template walk-8-frames | all 8 | ab7bee3a (fired 4+4, one group) |
| walk_ew | marmalade side | template walk-8-frames | E W | 792d05a0 |
| walk_8dir_lowtd | marmalade lowtd | template walk-8-frames | all 8 | f0c36d85 (fired 4+4, one group) |
| butt_flash_dotted | stripey / kambu / marmalade lowtd | v3 | N | ac47db78 / 9f5cb9e0 / 659eae83 |
| sitting_v2 | stripey / kambu / marmalade lowtd | v3 16f | S | 10900be2 / 72600815 / 8c6ced6b |
| licking_v2 | stripey / kambu / marmalade lowtd | v3 16f | S | 6f870d83 / 93c8a18a / c8ee4251 |

## Concurrency notes (Tier 3, first lane on the upgraded account)

- Tier 3 concurrent-job cap **20 confirmed**: an 8-direction template call
  is atomically rejected with "need 8 job slots but only N available
  (M/20 used)" -- clean rejection, nothing partial, refire when slots free.
  Splitting 8-dir groups into 4+4 via `animation_group_id` works well.
- Queue latency at Tier 3 was near zero this session (jobs returned in
  ~1-3 min even 15+ deep); the Tier-1 warm-ramp/priority-slot dance in
  PIXELLAB_OPERATIONS.md section 2 did not bite.

## Credits

| checkpoint | generations remaining | delta | what it bought |
|---|---|---|---|
| lane start | 6025 (1394 used) | -- | -- |
| mid-flight (after ~44 gens of nominal work fired) | 6000 | 25 | jobs bill on completion, not submission |
| lane end | 5884 (1535 used) | **141 total** | whole lane |

Nominal (tool-quoted) spend was 76: 6 creates + 12 v3 fix dirs (incl the
eldritch second roll) + 24 flourish gens (12 jobs x 2/dir at 16f) + 4
butt-flash + 30 template walk dirs. **Measured 141 -- a +65 gap the quotes
do not explain.** The nominal-vs-billed decomposition was not isolated
(jobs overlapped); prime suspect is template walk dirs billing ~2-3/dir on
this account tier (the pre-sweep "~2.1/dir" datapoint back from the dead)
rather than the 1.0 the cat-sweep lane measured. Next lane: bracket ONE
8-dir template group with get_balance and nothing else in flight, and
update PIXELLAB_OPERATIONS.md section 3 either way. At Tier 3 pool scale
(5884 remaining) the gap is noise for planning, but the cost model should
not silently drift.

Free discoveries (0 gens): slot-cap rejections and v3 action-prefix dedupe
rejections do not bill.

## Files (722 PNGs, all 68x68; fetched via download_batch.py)

Zip-native layout ({char}/rotations/, {char}/animations/{group}/{dir}/,
{char}/metadata.json). Existing characters carry ONLY the new refinement
groups -- their old clips stay in `../pixellab_2026-07-26_cat_sweep/`.
`butt_flash_stamped/` folders are LOCAL PIL derivatives (butt_dot_stamp.py),
not pixellab groups.

- `cat_b2_tabby_lowtd_heft/` 96 -- 8 rot + walk_ew_cleanfix 2x9 +
  walk_north_tailfix 9 + walk_south_calmtall 9 + butt_flash_dotted 9 +
  sitting_v2 17 + licking_v2 17 + butt_flash_stamped 9
- `cat_black/` 87 -- 8 rot + walk_diag_cleanfix 4x9 + sitting_v2 17 +
  licking_v2 17 + butt_flash_stamped 9
- `cat_eldritch_r2/` 78 -- 8 rot + walk_ew_cleanfix 2x9 +
  walk_east_cleanfix2 9 + sitting_v2 17 + licking_v2 17 +
  butt_flash_stamped 9
- `cat_sweep_black_side_heft/` 17 -- 8 rot + walk_west_cleanfix 9
- `cat_ref_{stripey,kambu_placeholder,marmalade}_side_heft/` 24 each --
  8 rot + walk_ew 2x8
- `cat_ref_{stripey,kambu_placeholder,marmalade}_lowtd/` 124 each --
  8 rot + walk_8dir_lowtd 8x8 + butt_flash_dotted 9 + sitting_v2 17 +
  licking_v2 17 + butt_flash_stamped 9

## Comparison sheet

`art_generated/cat_refinement_sheet.html` (gitignored derived output;
regenerate with `python tools/art_review/build_cat_refinement_sheet.py`) --
review_style house module (verdict chips, hide-on-verdict, collapsed
sections + completeness pills). Old-vs-new players for every fix; new roster
rotations + walks; butt punctuation players + filmstrips.
