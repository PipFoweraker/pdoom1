# Office prop manifest

Per-asset metadata for office floor props, so props stop being force-scaled
identically. Pattern-matched on `godot/data/icon_mapping.json` (the repo's
registry convention: `_meta` version header + one keyed entry per asset).

- **Data:** `godot/data/office/props_manifest.json` (SSOT; `_schema` block inside
  documents every field)
- **Loader:** `godot/scripts/core/prop_catalogue.gd` (`PropCatalogue`, static/lazy
  like `quirk_catalogue.gd`)
- **Tests:** `godot/tests/unit/test_prop_manifest.gd`

## Why

The renderers (`office_floor.gd`, `office_sandbox.gd`) currently force-scale
EVERY prop to `PROP_TARGET_H = 46` display px, feet-anchored -- a water cooler and
a four-tile server cluster end up the same height. The manifest records what each
asset actually is (real canvas, opaque-subject bounds, feet anchor, tile
footprint, height) so a renderer can size and place each prop on its own terms.

## Fields (summary -- `_schema` in the JSON is authoritative)

| field | meaning |
|---|---|
| `art` | `res://` path to the PNG under `assets/office_floor/props/` |
| `canvas_px` | full PNG size `[w, h]` (includes transparent padding) |
| `subject_px` | opaque-subject (alpha bbox) size `[w, h]` |
| `anchor_px` | feet anchor in canvas coords: bottom-centre of the opaque bbox (x may be `.5`; y = exclusive bbox bottom, the baseline row) |
| `footprint_tiles` | floor tiles occupied `[w, h]` at the 32 px art-tile scale (floor art is 32 px, displayed at 64 px); depth is judgement -- front-view art has none |
| `approach_px` | v1.2, OPTIONAL: list of `[x, y]` approach-slot offsets from `anchor_px`, in source px (`+x` right, `+y` down = in front). Landmark destination resolution (`office_floor.gd` `approach_point_for`) prefers the first FREE slot, so walkers queue at a prop's sides instead of stacking in front of it (`water_cooler` populates left/right). Omit it and resolution falls back to the nearest-outside-footprint point unchanged |
| `height_tiles` | subject height / 32, rounded to nearest 0.25 (ties up) |
| `style_tags` | office quality tiers this art serves, from the canonical ladder `"scummy"` / `"decent"` / `"premium"` (ruled 2026-07-26; `docs/game-design/SEED_ASSET_REGISTRY_AND_VERDICTS.md`). Tier-variant art uses id convention `<base_id>_<tier>`; where a variant is missing, renderers show the decent art unchanged (no tinting) |
| `sockets` | ALWAYS `[]` for now -- schema placeholder, see below |
| `review` | `true` = a field needs Pip's ruling (see `notes`) |

## Adding a prop

1. Drop the PNG in `godot/assets/office_floor/props/` (transparent padding is
   fine -- the subject bbox is what matters).
2. Measure canvas + alpha bbox (python PIL: `Image.open(p).split()[3].getbbox()`
   gives `(left, top, right_excl, bottom_excl)`; subject = right-left x
   bottom-top; anchor = `((left+right)/2, bottom_excl)`).
3. Add the entry to `props_manifest.json` (id = file basename). Set `review: true`
   on anything you guessed (footprint depth, style family).
4. Run the fast gate -- `test_prop_manifest.gd` fails loudly if a PNG lacks an
   entry, an art path dangles, or geometry is out of bounds.

## Renderer integration -- DONE (2026-07-26, office-polish lane)

`office_floor.gd` and `office_sandbox.gd` now consume `PropCatalogue`:

- The `PROP_TARGET_H / src.y` force-scale is replaced with
  `PropCatalogue.height_px(id, tile_px) / subject_h` (tile_px = 64, the display
  tile), so each manifested prop keeps its authored proportions.
- Placement anchors at `anchor_px` (subject feet) instead of texture
  bottom-centre -- kills the padding-dependent drift. (`office_floor.gd`
  `_draw_prop`; sandbox sprites get `centered = false, offset = -anchor_px`.)
- The sandbox uses `footprint_tiles` for placement occupancy: a manifested prop
  marks its footprint cells so populate furniture will not overlap it.
- `approach_px` (v1.2, office pass 3) drives landmark-visit destinations:
  `OfficeFloor.approach_point_for()` hands a walker the first free slot
  (occupied = someone standing within 10 px of it, or navigating to it);
  props without the field keep the plain nearest-outside-footprint fallback.
- `style_tags` drive tier selection: `office_floor.set_office_style(tier)` picks
  a `<id>_<tier>` variant when manifested + tagged for the tier; otherwise the
  decent art draws unchanged. The sandbox prop pool filters manifested assets by
  `style_tags` (unmanifested promoted art still falls back to id-keyword
  inference).
- `PropCatalogue` fallback for unmanifested ids reproduces the legacy 46 px
  behaviour (and warns once), so integration cannot regress unknown assets. The
  sandbox additionally requires the loaded texture size to match `canvas_px`
  before trusting an entry (an off-resolution art_source master degrades to the
  legacy path).

NOTE: authored proportions are BIGGER than the old force-scale (a 3.5-tile
water cooler now renders 224 px at the 64 px display tile, vs 46 px before).
Entries carry `review: true` where the measured geometry needs Pip's ruling.

## Sockets are schema-only

`sockets` defines the FUTURE attachment-point shape
(`{"name", "px": [x, y], "layer": "front"|"behind"}`) for the cosmetics sprite
category in `art_source/` (paper-doll layers, e.g. a poster taped to a server
rack). No consumer exists; keep every `sockets` array empty until one does --
the unit test validates the shape only if populated.
