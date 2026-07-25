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
| `height_tiles` | subject height / 32, rounded to nearest 0.25 (ties up) |
| `style_tags` | office-state families: `"scummy"` / `"decent"`; both = state-neutral art |
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

## Renderer integration -- explicit follow-up, NOT in this lane

`office_floor.gd` / `office_sandbox.gd` were being edited by another lane when
this shipped, so nothing consumes `PropCatalogue` yet. The follow-up, AFTER the
in-flight scale lane merges:

- Replace the `PROP_TARGET_H / src.y` force-scale with
  `PropCatalogue.height_px(id, tile_px) / subject_h` so each prop keeps its
  authored proportions.
- Anchor placement at `anchor_px` (subject feet) instead of texture
  bottom-centre -- kills the padding-dependent drift.
- Use `footprint_tiles` for placement/occupancy once props block walking.
- `PropCatalogue` fallback for unmanifested ids reproduces today's 46 px
  behaviour (and warns once), so integration cannot regress unknown assets.

## Sockets are schema-only

`sockets` defines the FUTURE attachment-point shape
(`{"name", "px": [x, y], "layer": "front"|"behind"}`) for the cosmetics sprite
category in `art_source/` (paper-doll layers, e.g. a poster taped to a server
rack). No consumer exists; keep every `sockets` array empty until one does --
the unit test validates the shape only if populated.
