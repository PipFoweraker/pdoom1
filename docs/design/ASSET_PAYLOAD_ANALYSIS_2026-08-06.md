# Asset payload analysis -- what promotion would actually ship, measured

- **Status:** MEASURED (read-only analysis; no art touched, no promote run)
- **Date:** 2026-08-06
- **Brief:** Pip's three observations on the post-review payload (variant
  redundancy, UI source material approved as icons, and "de-promote the
  non-chosen variants?") -- quantify each, then design the mechanism.
- **Method:** a scratchpad script drove `tools/art_review/apply_review.py`'s
  own asset resolution (import-only, no writes) over the 2,704-verdict
  `review_state.json`, so every number below uses the SAME promotable set the
  gate reports (1,206 assets, 200.4 MB, 0 blocked, 0 contested). Display-size
  numbers are real measurements: each file was decoded, LANCZOS-downscaled in
  memory to its consumer's draw size, re-encoded in its own format (PNG
  optimize / WEBP q85), and the encoded bytes counted. Nothing was written
  into the repo.

## Baseline

```
pack today:             59 MB (godot/assets = 47 MB of it)
promotable payload:     1,206 files, 200.4 MB
promote-as-is result:   ~259 MB pack (4.4x the current download)
```

Where the 200.4 MB sits, by destination (MB at display = saving 1 applied):

```
destination                          files      MB    MB at display (1x)
icons/generated                        484   139.5     3.4
textures/generated                      48    18.7    18.7  (native kept)
images/heroes                           23    15.0     3.8
portraits/generated                     19     8.9     2.2
images/backgrounds                      16     7.8     7.8  (native kept)
images/scenes                           13     3.5     3.5  (native kept)
images/vignettes                         3     2.6     2.6  (native kept)
images/events                            7     1.7     1.7  (native kept)
office_floor/props                     215     0.8     0.8  (game-scale)
ui/frames                               12     0.8     0.8  (native kept)
cats, doom_overlays, characters,
tilesets                               366     1.2     1.2  (game-scale)
```

Icons are 70% of the payload by themselves: 396 of the 484 icon files are
512x512 PNGs (134.3 MB of the 139.5).

## Saving 1 -- derivative sizing (promotion is a copy, should be a transform)

**200.4 MB -> 46.5 MB at 1x display size, 71.2 MB at 2x. Saves 129 to 154 MB
on its own.**

The display sizes are from consumer code, not guesses:

- Action-bar tiles are 70x70 (`action_bar_renderer.gd:227`,
  `custom_minimum_size = Vector2(70, 70)`, the #1130 sizing). A 512px master
  behind a 70px tile carries 53x the pixels drawn; the measured shrink for the
  484 icon files is 139.5 MB -> 3.4 MB.
- Portraits load at 256 (`portrait_library.gd`, `PORTRAIT_SIZE := 256`);
  card thumbnails draw at 48.
- The fanfare/hero image slot is 408 wide (`fanfare_popup.gd:107`).
- Backgrounds/scenes fill a 1920x1080 viewport (`project.godot`), and the
  sources are 1536 wide or less, so they were kept at NATIVE size -- no
  invented saving there. Events art was also kept native (it has zero
  consumers today; `godot/assets/images/events/README.md` documents that).

The 1x/2x range exists because `project.godot` sets
`window/stretch/mode="canvas_items"`: on a 4K display the canvas scales up and
a 70-logical-px tile draws at ~140 physical px. 1x is the floor (soft on 4K);
2x is crisp everywhere. The honest number is the range.

Two structural notes the measurement surfaced:

1. The copy step optimizes for the WRONG thing by design: `apply_review.py`
   promotes "the largest size that fits the 1MB git cap" (its own docstring,
   and `_largest_by_size(fits)` at line 326). Largest-committable is the
   opposite of size-the-game-draws. ADR-0019 pt 4 already rules the fix
   (promotion is a transform, never a copy); this measures what the ruling is
   worth: ~130-154 MB.
2. Copy-promotion does not even connect to the consumers' naming contracts.
   The 19 promotable portraits are 512px and 1024px files; `portrait_library.gd`
   constructs `"%s%s_%d.png"` with `PORTRAIT_SIZE = 256`, so every copied
   portrait would be packed AND invisible to the loader. Same class: promoted
   terminal textures land in `textures/generated/` while `theme_manager.gd:122-131`
   reads unversioned names from `textures/terminal/`. A transform step that
   renders the demanded name at the demanded size fixes both; a copy cannot.

## Saving 2 -- variant redundancy (many keeps, one slot)

**One-per-slot collapses 565 slot-competing files into 304 roles, dropping
261 alternates: 68.9 MB as-is (75.6 MB if measured against the whole payload
before saving 3 is carved out).**

Method: cluster promotable files by role -- filename stem with `_vN` markers,
trailing size tokens, and batch-date suffixes stripped, per destination.
Pool destinations were EXEMPTED from collapse (office_floor props/characters/
tilesets, cats, doom_overlays, portraits): their consumers read directories as
variety pools (`worker_variant_pool.gd`, `portrait_library.gd`), so
multiplicity there is demand, not redundancy (ADR-0019 pt 3).

Measured redundancy, worst offenders:

```
icons/generated       458 files -> 240 roles   (13 action icons kept x4 each;
                                                cat_doom_8bit x5; resource_*_small x3)
textures/generated     45 files ->  14 roles   (tex_paper_grain x4, tex_dark_panel x4,
                                                tex_terminal_void x4, ...)
images/heroes          23 files ->  14 roles   (hero_office_at_dusk x4 = 2.4 MB)
images/events           7 files ->   4 roles
```

Against actual game demand the redundancy is starker:

- The game references 146 distinct icon paths (grep over gd/tscn/json), and
  NOT ONE reference to `assets/icons/generated` exists -- all 484 promotable
  icon files would be packed-but-unreferenced on day one.
- The theme's 10 terminal-texture slots are ALREADY filled by shipped
  unversioned files; the 29 promotable `tex_*_vN` variants compete for slots
  that are occupied.
- Pip's "20 up arrows", verified: `ui_control_up` alone carries 9 verdicts
  across three batches (3 gen discards, 6 keeps in the held icon_hires set --
  two directories x three sizes) for what the game consumes as one glyph.

## Saving 3 -- UI source material approved as finished art

**41 files, 10.4 MB, collapsing to 15 roles. None of it should promote as
whole images.**

The set (curated by stem + category, then eyeballed):

```
game_icons: ui_frame_corner_{tl,tr,bl,br}, ui_frame_{top,bottom,left,right},
            doom_meter_frame            26 files, 9.2 MB, all 512x512
ui_frames:  frame_button, frame_panel_plain, frame_panel_ornate
            (x4 variants each)          12 files, 0.8 MB, all 512x512
crt_frame_overlay: bezel_heavy, curved_glass, vignette_light
            (1536x1024 full-screen)      3 files, 0.3 MB
```

These are exactly what Pip described: a 512px PICTURE of a corner, shipped to
draw a 12px corner. Right treatment, in order of preference:

1. **Hand-authored `StyleBoxFlat` first** where the frame is geometric
   (borders, plain panels): zero texture bytes, resolution-independent, theme
   lane (#743) territory.
2. **9-slice extraction** for the ones whose painted texture is the point:
   crop the good corner/edge regions out of the masters into ONE small atlas,
   consume via `StyleBoxTexture`/`NinePatchRect` with region rects.
   Replacement cost measured against comparable atlases: well under 0.3 MB
   for all 15 roles.
3. The three CRT bezels are the only members that plausibly ship whole (they
   ARE full-screen overlays); 0.3 MB total, decide in the theme lane.

The corner/edge files should be reclassified in review terms as Library
masters (source material), which is a taste-neutral move: nothing about their
keep verdicts was wrong; what is wrong is the assumption that keep implies
ship-as-is.

## Combined -- applied in sequence, no double counting

```
promotable payload as-is                         200.4 MB
  saving 3: frame/bezel source material out       -10.4 MB  -> 190.1
  saving 2: 261 alternates out (post-S3 set)      -68.9 MB  -> 121.2 (chosen 110.2 + pools 10.9)
  saving 1: transform chosen+pools to display    28.7 MB (1x) / 45.7 MB (2x)
  9-slice atlas replacing saving-3 material          +0.3 MB
INCOMING PAYLOAD                                 ~29 MB (1x) to ~46 MB (2x)

RESULTING PACK        59 + 29..46 =  ~88 MB to ~106 MB   (vs ~259 MB as-is)
```

The 4.4x download becomes ~1.5x-1.8x. Not counted, available later: WEBP
re-encoding the chosen PNG icons (roughly halves them again), and the
ADR-0019 audit worklist over the existing 47 MB already in the pack (the
events dir alone is documented packed-but-undemanded).

**The measurement I trust least: saving 2's role count (304).** The "slot" is
defined there by a filename-stem regex, not by the game -- cross-batch assets
that share a stem but differ in content merge falsely, and same-role assets
with unrelated names (e.g. `grant_proposal` vs `apply_grant`, a known
near-duplicate pair) fail to merge. It is defensible as a +/- 15% estimate of
role count, and the MB saving is dominated by the unambiguous x3/x4
same-stem clusters, but the true slot list can only come from the demand
manifest -- which is the point of the mechanism below. Second-least: the
408px hero target rests on a single consumer's min-width; if hero art gets a
full-screen use, its 11 MB saving shrinks to ~4 MB (bounded -- heroes are
15.0 MB total).

## The mechanism -- a word for "good but not chosen"

### The gap, stated precisely

A `keep` verdict currently conflates two judgements made at different times by
different processes: **"this is good"** (taste, judged per-asset, once, at
review) and **"this is THE one we use"** (selection, judged per-SLOT, against
competitors, revisable every patch). Twenty good up-arrows are twenty true
keeps and one slot. The verdict vocabulary has no word for the other nineteen,
so today they default to "promotable" -- which is how 200 MB of approvals
became a 260 MB pack.

### Three candidate designs, argued

**(a) A new verdict** (`keep` vs `chosen`, or Pip's "de-promote"). Rejected.
Chosen-ness is not a property of the asset alone -- it is a property of the
(asset, slot) pairing. A verdict is written once, per asset, by taste; a
selection changes when a DIFFERENT asset wins the slot, without this asset
changing at all. Encoding selection as a verdict means every re-pick rewrites
review history (`updated_at` would lie about when taste was exercised), and an
asset chosen for one slot but not another is unrepresentable.

**(b) A second axis stored alongside the verdict** (a `chosen` flag or tag in
`review_state.json`). Rejected on ADR-0019's own precedent. A stored flag is a
second write site that can disagree with the manifest the pull step reads --
and when they disagree, one of them lies silently. That is the exact shape of
the category->destination map that stranded 75% of verdicts (1,021 keeps, 202
movable), and of `is_ranked_run()`'s warning comment: a rule duplicated beside
the path "silently reopens the hole". The review week's lesson (silent
wrongness: every failure looked right) argues against ANY hand-maintained
mirror of a decision that lives elsewhere.

**(c) Selection is a consequence of the demand manifest, and "good but not
chosen" needs NO stored label.** Adopted. ADR-0019 already contains the
vocabulary: an asset Pip likes is **Library**; an asset a demand entry names
is **chosen**, and the pull step renders its derivative into the pack. The
other nineteen up-arrows are simply Library assets no manifest entry names --
which is not a status to record, it is the ABSENCE of a record. Pip's
"reserve-ify" instinct is right about the outcome and wrong about the
direction: nothing needs to be done TO the alternates; the manifest does
something to the winner. "De-promote" is then not an asset operation but a
manifest diff -- change which asset the entry pins, commit, and the next pull
swaps the derivative. Reviewable in git, reversible, and the asset itself is
untouched.

### The vocabulary, concretely

- **Library** -- admitted by taste (`keep`). The default, unlabeled state.
  This is what Pip's word "reserve" means; it requires no action.
- **Chosen / pinned** -- a demand-manifest entry names this Library asset for
  a slot: `slot: action_icon/audit_safety, source: gen:icons_v2:icon_audit_safety:v3,
  size: 70` (shape illustrative; the manifest format is ADR-0019's open
  question). Singular slots pin by name.
- **Pool-resolved** -- for pool entries (">=6 researcher portraits at 256"),
  the pull step selects deterministically from eligible Library assets and
  emits a generated SELECTION RECORD (pool -> chosen list) committed next to
  the manifest. Generated-never-hand-edited, the `DQ_INDEX` anti-rot pattern;
  Pip overrides a pool pick by pinning, not by editing the record.
- **Alternate** -- fine as DISPLAY language in the review app (a derived
  badge: "in Library, not named by any manifest entry"), computed from
  manifest + selection record at render time. Never stored on the asset.

One review-tool consequence (design only, not built here): the place where
Pip exercises slot taste is a slot-picker view -- "show me the 4 Library
candidates for `action_icon/audit_safety`, click one" -- and its write target
is the MANIFEST, not `review_state.json`. Verdicts stay append-mostly taste
history; the manifest stays the single selection authority.

### Edge cases checked against the design

- Asset wins two slots: manifest names it twice; fine, derivatives can differ
  per slot size.
- Winner later discarded on taste: verdict change removes Library
  eligibility; the audit's demanded-but-missing direction flags the orphaned
  pin loudly (ADR-0019 pt 6), rather than the pack silently keeping stale art.
- The 752 held keeps: unchanged; Hold reasons live in the promote tool today
  and become moot once pull-from-demand retires copy-promotion -- held assets
  are simply Library members nothing names.

## Sequencing -- what to do, in what order

1. **Write the demand manifest for what the game loads TODAY** (ADR-0019's
   own first increment). The 146 referenced icon paths, the 10 theme texture
   slots, backgrounds/scenes in use, and the pool declarations for the six
   directory-consumers. MECHANICAL -- it transcribes existing references; no
   taste required, no file moves.
2. **Build the two-direction audit** against it. MECHANICAL. Day-one output:
   the undemanded share of the existing 47 MB, and the #1092-class gap list.
3. **Build the transform step** (render pinned Library asset -> demanded size
   and name, the sizes from this analysis). MECHANICAL; retires
   copy-promotion when it lands. This is what converts saving 1 from a
   number in this doc into the shipped pack.
4. **Pip's slot picks** -- the taste pass this analysis cannot do: choose one
   winner per contested role. Bounded work: 135 multi-competitor clusters,
   dominated by the 13 action-icon x4 sets, 14 texture roles, 14 hero roles,
   4 event roles. Each pick is one manifest pin. (Default if he abstains:
   highest variant number, the 2026-08-03 contested-keeps convention --
   defensible, but it is a default, not a decision.)
5. **Frame/9-slice lane** -- part taste, part craft: for the 15 saving-3
   roles decide StyleBoxFlat vs 9-slice-extract per role (taste), then build
   the atlas and theme entries (mechanical, theme lane #743 adjacency).
6. **Only then** consider the existing-pack audit worklist (the grandfathered
   47 MB) as deliberate, reviewed deletions -- the #787 precedent.

Taste vs mechanical, compressed: Pip is needed for step 4 (slot winners),
half of step 5 (which frames deserve their texture), and nothing else; steps
1-3 are agent-lane work with this doc as the size spec.
