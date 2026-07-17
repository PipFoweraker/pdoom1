# Asset generation pipeline (gpt-image-1.5)

Audit of the existing `tools/assets/` pipeline plus the no-spend foundation added
alongside it (palette extractor + first icon manifest). Nothing in this doc calls
an image API; the generation step is described, not run.

Read order: this file for the loop, `docs/art/palette.json` for the brand colours,
`tools/assets/manifests/icons_v1.json` for the first icon set.

## TL;DR loop

```
manifest (YAML native; JSON also parses)
    |
    v
tools/assets/generate_images.py  --file <manifest> [--dry-run] [--variants N] [--yes]
    |  (OpenAI Images API, model gpt-image-1.5; needs OPENAI_API_KEY)
    v
art_generated/<asset_type>/v1/<id>[_vN]_<size>.png     <-- master + downscaled widths
    |
    v
REVIEW  --  tools/assets/select_assets.py --gallery generated   (writes asset_gallery.html)
    |         [click variants -> copy "id:vN ..." commands]
    v
tools/assets/select_assets.py --select id:vN ...   (writes selected_variant into the manifest)
    |
    v
tools/assets/promote_assets.py --file <manifest> [--mark-promoted]
    |  (copies selected variant, strips the _vN suffix)
    v
godot/assets/icons/<category>/<id>_<size>.png
    |
    v
tools/assets/audit_icons.py   (checks godot/assets/icons vs godot/data/icon_mapping.json)
```

The nicer keyboard-driven `tools/art_review/build.py` viewer is a **separate track**
(pixellab sweep, not gpt-image output) -- see "Glue gaps" #1.

## What each script does

### `tools/assets/generate_images.py` -- the generator
- **Input format:** a **YAML** prompt file passed as `--file <path>`
  (`load_prompts` uses `yaml.safe_load`, lines 204-207; arg at line 380, load at
  line 438). Because JSON is a subset of YAML, `yaml.safe_load` also parses a JSON
  manifest, so `--file tools/assets/manifests/icons_v1.json` works unchanged
  (verified by a dry-run). Top-level keys the script reads: `asset_type`,
  `default_size`, `output_sizes`, `styles`, `themes`, `assets` (lines 441-445).
  Unknown keys (e.g. our `_meta`, `schema_version`) are ignored.
- **Per-asset fields:** `id`, `category`, `status`, `theme`, `prompt_tail`
  (plus optional `display_name`, `reference_images`, `generation_history`).
  The full prompt is assembled in `build_full_prompt` (lines 216-243) as
  `styles[theme.style_overrides...] + theme.color_bias + prompt_tail`.
- **Backend / model:** default backend `openai`, default model **gpt-image-1.5**
  (`DEFAULT_OPENAI_MODEL`, line 42; gpt-image-1 retires 2026-10-23). A dormant
  `--backend gemini` (Nano Banana Pro) path exists (lines 158-201) and is the
  only path that consumes `--reference-images` for style consistency.
- **API key:** `get_client()` (lines 122-129) constructs `OpenAI()`, which reads
  **`OPENAI_API_KEY` from the environment implicitly** -- there is no key CLI arg.
  `--dry-run` never constructs the client, so it needs no key (confirmed).
- **Size / quality:** the request passes only `model, prompt, size`
  (`_openai_generate_bytes`, line 154). `size` comes from the manifest's
  `default_size` (line 443). There is **no quality param and no
  `background="transparent"`** in the call -- see Glue gaps #2.
- **Where it writes:** `art_generated/<asset_type>/v1/` (line 451). It saves a
  master `<id>[_vN]_<masterwidth>.png` then downscales to each width in
  `output_sizes` (lines 286-318). Logs go to `art_generated/logs/` (lines 73-104).
- **Cost:** dry-run/confirm estimate only (`estimate_cost_per_image`, lines 56-62;
  ~$0.06 at 1024, ~$0.09 for landscape). Real spend is whatever the API charges.
- **Key CLI:** `--file` (required), `--dry-run`, `--status`, `--category`,
  `--ids`, `--limit`, `--variants N`, `--add-variant`, `--force`, `--yes/-y`,
  `--update-yaml`, `--backend`, `--model`, `--reference-images`.

### `tools/assets/select_assets.py` -- the reviewer/selector
- **Input:** same `--file <manifest>`; `--gallery <status>`, `--select id:vN ...`,
  `--list <status>`, or interactive (default).
- **Gallery:** `generate_gallery_html` (lines 69-324) scans
  `art_generated/<asset_type>/v1/` (with a `game_icons` fallback, lines 77-82),
  embeds each variant via a `file://` URL, and writes **`asset_gallery.html`** to
  the project root (line 507). You click variants; it emits `id:vN` commands.
- **Select:** `--select id:vN` sets `selected_variant` + `status: selected` on the
  asset and **saves the manifest via `yaml.dump`** (lines 603-607, save at 27-30).
- **Output:** an updated manifest (selection state) + `asset_gallery.html`.

### `tools/assets/promote_assets.py` -- the promoter
- **Input:** `--file <manifest>`, `--status` (default `selected`), `--category`,
  `--ids`, `--dest` (default **`godot/assets/icons`**, lines 133-136), `--dry-run`,
  `--mark-promoted`.
- **What it does:** for each matching asset, copies
  `art_generated/<asset_type>/v1/<id>_<selected>_<size>.png` (falling back to the
  no-variant name) into `<dest>/<category>/<id>_<size>.png` -- the `_vN` suffix is
  stripped for clean game paths (`promote_asset`, lines 33-96). `--mark-promoted`
  flips `status: promoted` and re-saves the manifest via `yaml.dump`.
- **Output:** PNGs under `godot/assets/icons/<category>/`.

### `tools/assets/audit_icons.py` -- the usage auditor
- **Input:** none but the tree. Scans `godot/assets/icons/**/*_64.png` (64px treated
  as canonical, line 30) and compares against
  `godot/data/icon_mapping.json` (line 23).
- **Output:** used / unused / missing / placeholder report;
  `--format json|markdown|summary` (line 251). This closes the loop -- it tells you
  which promoted icons are actually wired into the game and which mapping entries
  are still `PLACEHOLDER` (with a `suggested_prompt`).

### `tools/assets/extract_palette.py` -- brand palette extractor (added here)
- **Input:** `<image>` (positional) `--n <count>` (default 24),
  `--out-json`, `--out-html`. Pillow import is guarded -- if PIL is missing it
  prints `pip install pillow` and exits non-zero rather than crashing.
- **Method:** downscales the longest edge to 400px, runs PIL adaptive median-cut
  `quantize`, sorts the resulting palette by pixel frequency, and labels each
  colour with a best-guess role from its HSV coordinates (`role_guess`).
- **Output:** `docs/art/palette.json` (`[{hex, rgb, role_guess, weight_pct}]`) and
  `tools/art_review/palette_swatches.html` (standalone, inline styles, no external
  assets). Re-runnable: `python tools/assets/extract_palette.py <image> --n 24`.
- The hero (`godot/assets/dump_october_31_2025/hero-bg-2400w.webp`) is
  **dark-dominant** -- the palette skews to ink / deep-indigo / doom-purple,
  matching the "purple doom-end" art direction. No warm amber accent exists in the
  hero, so an accent colour (e.g. the review tool's `--amber #e8a33d`) has to be
  brought in by hand if a set needs one.

## The first manifest

`tools/assets/manifests/icons_v1.json` -- 6 icons grounded in `docs/art/palette.json`,
one coherent set (shared `global_icon_base` + `brand_palette` styles, one
`brand_doom` theme). IDs and intent:

| id | resource | direction |
|----|----------|-----------|
| `icon_doom` | doom | ROBOT-flavoured skull -- machined cranium, glowing sensor eyes, slotted grille instead of teeth (per `docs/art/reviews/2026-07-17-overnight-sweep.md`: old ones "too teethy / Heavy-Metal / too human") |
| `icon_compute` | compute | GPU / stacked rack-blades with cooling fins + power node -- explicitly off the literal microchip square |
| `icon_money` | money | banked credit-chip stack + upward funding arrow |
| `icon_reputation` | reputation | heraldic seal / shield with a centred star |
| `icon_papers` | papers | fanned research sheets in a bracket clip |
| `icon_governance` | governance | balance scale on a pillared plinth (oversight) |

Resource names (`money`, `compute`, `reputation`, `papers`, `governance`) verified
against `godot/scripts/core/game_state.gd` (lines 9-48). Prompts pin the specific
palette hexes (indigo `#181b3b`/`#2e2547`, doom-purple `#300e1c`/`#351b33`, ink
`#0e020c`, bone keyline `#ece0cf`) so the set reads as one system.

## Glue gaps (flagged, not yet fixed)

1. **Two review tools; only one sees generator output.**
   `select_assets.py --gallery` scans `art_generated/<asset_type>/v1/` and is the
   reviewer for gpt-image output. The newer keyboard-driven viewer
   `tools/art_review/build.py` does **not** read `art_generated/` -- it renders
   committed PNGs under `art_source/<image_root>/<batch.dir>/` per
   `tools/art_review/manifest.json` (build.py lines 277-288) plus the pixellab
   `sweep`/`reroll` dirs (lines 171-273). So the nice viewer is a pixellab track.
   **Bridge needed** to review gpt-image icons there: after generation, copy/rename
   `art_generated/game_icons/v1/*.png` into an `art_source/<batch>/` dir and add a
   `gallery` batch to `manifest.json`, or extend `build.py` to scan `art_generated/`.

2. **Transparent background is prompted but never requested.**
   The manifest prompts (and the older ui_icons prompts) ask for a transparent
   background, but `_openai_generate_bytes` (line 154) passes only
   `model/prompt/size` -- no `background="transparent"`. The `img.convert("RGBA")`
   at line 309 only adds an all-opaque alpha channel. Icons will come back with a
   baked background until `background="transparent"` is added to the
   `images.generate(...)` call.

3. **JSON manifest is a one-way convenience.**
   `generate_images.py` *reads* JSON fine (via `yaml.safe_load`). But
   `select_assets.py` and `promote_assets.py` *write* the manifest back with
   `yaml.dump` (select lines 27-30, promote lines 27-30) whenever you `--select`,
   `--update-yaml`, or `--mark-promoted`. Running those on `icons_v1.json` rewrites
   it in YAML syntax (still a valid file, wrong extension). Options: keep the JSON
   read-only and pass `--dry-run` style flows only, or `cp icons_v1.json
   icons_v1.yaml` before the select/promote stages and drive those off the YAML.

4. **API key is implicit.** `OpenAI()` (line 128) reads `OPENAI_API_KEY` from the
   environment; there is no CLI flag. `--dry-run` needs no key.

## No-spend verification done here
- `python -m py_compile tools/assets/extract_palette.py` -- passes.
- `extract_palette.py <hero> --n 24` -- wrote `palette.json` (24 colours) +
  `palette_swatches.html`.
- `icons_v1.json` parses as JSON **and** via `yaml.safe_load`.
- `generate_images.py --file icons_v1.json --dry-run` -- lists all 6 icons and
  builds their full prompts (no API call, no spend).
