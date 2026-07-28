# Vignette VANGUARD -- generation manifest

Generated 2026-07-28. Vanguard = specs 01-05 of
`docs/game-design/SEED_VIGNETTE_SPECS.md` (the first 5, which include the
cat-silhouette flagship at spec 01). These are stand-in fade-in hero images
per the seed doc's framing -- an artist-onboarded sweep replaces them later.

Model: `gpt-image-1.5`, size `1536x1024`, b64_json response (same request
shape as `tools/art_review/gen_generative_pass.py`). Runner script was a
one-off in scratchpad (not committed; contained no key -- key loaded from
env var only).

Committed files are downscaled to 921x614 (LANCZOS resize + PNG optimize) to
stay under the repo's 1000KB add-large-file hook. Full-resolution
(1536x1024) masters are archived at
`G:/tmp/pdoom1-art-masters/vignettes_2026-07-28/` per
`docs/art/ART_MASTERS_POLICY.md`.

| Spec | File | Model | Committed size (921x614) | Master size (1536x1024) | Approx cost |
|---|---|---|---|---|---|
| 01 cat-in-the-alley [KEYED, flagship] | `01_cat-in-the-alley.png` | gpt-image-1.5 | 878 KB | 2911 KB | ~$0.09 |
| 02 conference-departure [KEYED] | `02_conference-departure.png` | gpt-image-1.5 | 887 KB | 2692 KB | ~$0.09 |
| 03 conference-floor [KEYED] | `03_conference-floor.png` | gpt-image-1.5 | 804 KB | 2678 KB | ~$0.09 |
| 04 conference-return [KEYED] | `04_conference-return.png` | gpt-image-1.5 | 943 KB | 2914 KB | ~$0.09 |
| 05 taxi-window-rain [GENERIC] | `05_taxi-window-rain.png` | gpt-image-1.5 | 770 KB | 2645 KB | ~$0.09 |

Total: 5/5 specs generated on first attempt, 0 retries, 0 skips.
Approx total spend: ~$0.45 USD (per `tools/assets/generate_images.py`
`estimate_cost_per_image` table for `1536x1024` at gpt-image-1.5 medium
quality; not a billed-invoice figure).

## Notes
- Spec 01's cat is generated per the SILHOUETTE PRINCIPLE in the seed doc:
  shape + two lamp-glints only, no breed/colour/face -- reviewed against the
  brief on generation, not re-touched.
- No caption text, logos, or UI chrome baked into any image (captions live
  in the seed doc / game data, not the art).
- These are stand-ins per the seed doc header; not final art.
