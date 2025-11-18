---
title: Building an AI Asset Generation Pipeline
date: 2025-11-18
categories: ["feature", "tools", "ai", "art"]
contributors: ["Pip", "Claude"]
---

## Building an AI-Powered Asset Generation Pipeline

Today marks a significant milestone: we've generated, reviewed, and selected 91 custom game icons through a fully automated pipeline using OpenAI's gpt-image-1 model. The total cost? Around $12 for 145 images. Here's how we built it.

### The Problem

PDoom needs a cohesive visual identity - StarCraft 2 meets XCOM, with a worn industrial aesthetic. Hand-drawing 91 icons would take weeks. Commissioning them would cost thousands. We needed a middle path: AI-generated assets with human curation.

### Architecture: YAML as Single Source of Truth

The core insight was treating a YAML file as the canonical database for everything:

```yaml
assets:
  - id: ui_home_hq
    category: main_navigation
    status: pending  # -> generated -> selected -> promoted
    theme: base_corporate
    prompt_tail: 'three small monitors displaying graphs...'
    generation_history:
      - version: v1
        generated_at: '2025-11-17T04:49:52+00:00'
        model: gpt-image-1
        cost_usd: 0.08
    selected_variant: v1
```

This design means we can track generation history, costs, prompt hashes (for cache invalidation), and selection state all in one place. Three Python tools operate on this file:

1. **generate_images.py** - Calls OpenAI API, saves images, updates YAML
2. **select_assets.py** - Interactive CLI + HTML gallery for variant selection
3. **promote_assets.py** - Copies selected variants to Godot assets directory

### Prompt Engineering: Composable Styles

Rather than writing 91 separate prompts, we built a composable system:

```yaml
styles:
  global_icon_base: 'high-res 1024x1024 square game icon...'
  surface_tarkov: 'Tarkov-style worn metal, scratched paint...'

themes:
  base_corporate:
    style_overrides: [global_icon_base, surface_tarkov]
    color_bias: 'desaturated teal and olive tones'
```

Each asset only needs a `prompt_tail` describing its specific content. The full prompt is assembled at generation time: `{styles} + {color_bias} + {prompt_tail}`. This ensures visual consistency while allowing per-icon customization.

### The Variant Problem

Initial generation gave us one variant per asset - but AI image generation is stochastic. Sometimes v1 is perfect; sometimes it's unusable. We needed options.

The solution: a `--variants N` flag to generate multiple versions, plus `--add-variant` to add another variant to existing assets. This led to an interesting file naming challenge.

Original single-variant assets were saved as `asset_128.png`. Multi-variant assets use `asset_v1_128.png`, `asset_v2_128.png`. When we added v2 variants to single-variant assets, the gallery couldn't find the v1 images - it was looking for `asset_v1_128.png` but the file was `asset_128.png`.

The fix: fallback logic in both the gallery generator and promotion tool. Check for the variant-suffixed filename first, fall back to the non-suffixed version. A small bug that taught us about the importance of consistent naming conventions from the start.

### The Selection Interface

Reviewing 145 images in a terminal would be miserable. We built an HTML gallery generator that:

- Groups assets by category
- Shows 128px thumbnails of each variant
- Highlights the currently selected variant
- Generates a copy-paste command with all selections

The workflow: run `--gallery generated`, click through variants in the browser, copy the generated `--select` command, paste it in terminal. Human judgment for selection, automation for everything else.

### Cost Management

At $0.08 per 1024x1024 image, costs add up. Every command shows estimated cost before execution:

```
Estimated cost: $4.32 (54 images: 1 new variant per asset)
```

We generated strategically: 3 variants for critical navigation icons, 2 for buttons and resources, 1 for decorative elements. The batch script encoded this prioritization, spending more on assets that appear constantly and less on rarely-seen elements.

### Lessons Learned

**Start with consistent conventions.** The variant suffix inconsistency cost us debugging time. Design the file naming scheme before generating anything.

**YAML is surprisingly good for this.** It's human-readable, git-diffable, and easy to hand-edit when needed. A database would be overkill.

**Generation is cheap; curation is expensive.** The $12 in API costs was trivial. The hours spent selecting variants was the real investment. Good tooling (the HTML gallery) made this bearable.

**Prompt engineering compounds.** Getting the base style right meant every asset benefited. We iterated on `global_icon_base` until we got that worn industrial look, then it applied to all 91 assets automatically.

### What's Next

With 91 selected assets ready to promote into Godot, the next step is integrating them into the actual UI. The pipeline infrastructure means we can easily generate more assets as the game expands - new research types, new employee roles, new resources.

The tools are in `tools/`, the YAML in `art_prompts/`, and everything's documented in `docs/ASSET_GENERATION_PIPELINE.md`. Clone the repo, set your `OPENAI_API_KEY`, and you're off.

Total investment: ~$12 in API costs, ~6 hours of development and curation time. Result: 91 cohesive game icons with full version history and a reusable pipeline for future assets.

Not bad for a day's work.
