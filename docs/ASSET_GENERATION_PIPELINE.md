# Asset Generation Pipeline

Automated system for generating, reviewing, and promoting AI-generated game assets using OpenAI's gpt-image-1 model.

## Overview

The pipeline uses YAML files as the single source of truth for asset definitions, generation history, and selection status. Three Python tools handle the workflow:

```
art_prompts/*.yaml     -> generate_images.py -> art_generated/
                                                     |
                                              select_assets.py
                                                     |
                                              promote_assets.py -> godot/assets/
```

## Directory Structure

```
pdoom1/
  art_prompts/           # YAML asset definitions
    ui_icons.yaml        # Icon definitions with prompts
  art_generated/         # Generated images (not in git)
    ui_icons/v1/         # Output directory
      asset_v1_1024.png  # Master 1024x1024
      asset_v1_512.png   # Downscaled versions
      asset_v1_256.png
      asset_v1_128.png
      asset_v1_64.png
  tools/assets/
    generate_images.py   # Image generation
    select_assets.py     # Variant selection
    promote_assets.py    # Copy to game
  godot/assets/icons/    # Final game assets
```

## YAML Schema

```yaml
schema_version: '1.0'
asset_type: ui_icons
default_size: 1024x1024
output_sizes: [1024, 512, 256, 128, 64]

styles:
  global_icon_base: 'high-res 1024x1024 square game icon...'
  surface_tarkov: 'Tarkov-style worn metal...'

themes:
  base_corporate:
    style_overrides: [global_icon_base, surface_tarkov]
    color_bias: 'desaturated teal and olive tones'

assets:
  - id: ui_home_hq
    category: main_navigation
    display_name: HQ Overview
    status: pending          # pending -> generated -> selected -> promoted
    theme: base_corporate
    prompt_tail: 'three small monitors...'
    generation_history:
      - version: v1
        generated_at: '2025-11-17T04:49:52+00:00'
        model: gpt-image-1
        full_prompt_hash: 3d4f10fc1950
        file_path: art_generated/ui_icons/v1/ui_home_hq_v1_1024.png
        cost_usd: 0.08
    selected_variant: v1     # Set after selection
```

## Status Workflow

```
pending -> generated -> selected -> promoted
```

- **pending**: Asset defined, not yet generated
- **generated**: Images created, awaiting review
- **selected**: Variant chosen, ready for game
- **promoted**: Copied to godot/assets/

## Tools

### generate_images.py

Generates images from YAML definitions using OpenAI API.

```bash
# Set API key (one-time)
export OPENAI_API_KEY="sk-..."

# Dry-run to preview
python tools/assets/generate_images.py --file art_prompts/ui_icons.yaml --dry-run

# Generate all pending assets
python tools/assets/generate_images.py --file art_prompts/ui_icons.yaml --status pending --yes --update-yaml

# Generate multiple variants for comparison
python tools/assets/generate_images.py --file art_prompts/ui_icons.yaml --status pending --variants 3 --yes --update-yaml

# Add another variant to existing assets
python tools/assets/generate_images.py --file art_prompts/ui_icons.yaml --status generated --add-variant --yes --update-yaml

# Generate specific assets by ID
python tools/assets/generate_images.py --file art_prompts/ui_icons.yaml --ids ui_home_hq ui_alerts --yes

# Filter by category
python tools/assets/generate_images.py --file art_prompts/ui_icons.yaml --category main_navigation --yes

# Force regenerate (overwrites existing)
python tools/assets/generate_images.py --file art_prompts/ui_icons.yaml --force --yes
```

**Key Arguments:**
- `--file`: Path to YAML (required)
- `--status`: Filter by status (pending, generated, etc.)
- `--category`: Filter by category
- `--ids`: Specific asset IDs
- `--variants N`: Generate N variants per asset
- `--add-variant`: Add one more variant to existing assets
- `--limit N`: Maximum images to generate
- `--dry-run`: Preview without API calls
- `--force`: Regenerate even if files exist
- `--update-yaml`: Write metadata back to YAML
- `--yes`: Skip confirmation prompt

### select_assets.py

Interactive tool for reviewing and selecting variants.

```bash
# Interactive mode
python tools/assets/select_assets.py --file art_prompts/ui_icons.yaml

# Open visual gallery in browser
python tools/assets/select_assets.py --file art_prompts/ui_icons.yaml --gallery generated

# Quick select specific variants
python tools/assets/select_assets.py --file art_prompts/ui_icons.yaml --select ui_home_hq:v2 ui_alerts:v1

# List assets by status
python tools/assets/select_assets.py --file art_prompts/ui_icons.yaml --list generated
```

**Interactive Commands:**
- `list [status]` - List assets
- `show <id>` - Show asset details
- `select <id> <v#>` - Select variant
- `batch` - Batch select from input
- `gallery [status]` - Open HTML gallery
- `status` - Show progress
- `save` - Save changes
- `quit` - Exit

**HTML Gallery Workflow:**
1. Run `--gallery generated` to open browser
2. Click variants to select
3. Copy commands from bottom of page
4. Run the copied `--select` command

### promote_assets.py

Copies selected assets to game directory.

```bash
# Dry-run to preview
python tools/assets/promote_assets.py --file art_prompts/ui_icons.yaml --dry-run

# Promote all selected assets
python tools/assets/promote_assets.py --file art_prompts/ui_icons.yaml

# Promote and mark as promoted in YAML
python tools/assets/promote_assets.py --file art_prompts/ui_icons.yaml --mark-promoted

# Promote specific category
python tools/assets/promote_assets.py --file art_prompts/ui_icons.yaml --category main_navigation

# Custom destination
python tools/assets/promote_assets.py --file art_prompts/ui_icons.yaml --dest godot/assets/custom
```

## Complete Workflow Example

### 1. Define Assets

Edit `art_prompts/ui_icons.yaml` to add new assets:

```yaml
- id: ui_new_feature
  category: main_navigation
  display_name: New Feature
  status: pending
  theme: base_corporate
  prompt_tail: 'description of the icon...'
```

### 2. Generate Images

```bash
# Preview cost
python tools/assets/generate_images.py --file art_prompts/ui_icons.yaml --status pending --dry-run

# Generate with 3 variants for critical icons
python tools/assets/generate_images.py --file art_prompts/ui_icons.yaml --ids ui_new_feature --variants 3 --yes --update-yaml
```

### 3. Review and Select

```bash
# Open gallery to view variants
python tools/assets/select_assets.py --file art_prompts/ui_icons.yaml --gallery generated

# Select winner (from gallery copy)
python tools/assets/select_assets.py --file art_prompts/ui_icons.yaml --select ui_new_feature:v2
```

### 4. Promote to Game

```bash
# Preview
python tools/assets/promote_assets.py --file art_prompts/ui_icons.yaml --dry-run

# Copy to game
python tools/assets/promote_assets.py --file art_prompts/ui_icons.yaml --mark-promoted
```

## Cost Tracking

- **Per image**: $0.08 (gpt-image-1 at 1024x1024)
- Generation history tracks cost per variant
- Dry-run shows estimated cost before generation

Example costs:
- 10 assets x 1 variant = $0.80
- 10 assets x 3 variants = $2.40
- 91 assets x 1 variant = $7.28

## Prompt Engineering

Prompts are built from:
1. **Style base** - Global icon style (StarCraft 2 / XCOM feel)
2. **Surface style** - Texture treatment (Tarkov worn metal, clean corporate)
3. **Color bias** - Theme-specific colors
4. **Prompt tail** - Asset-specific description

Full prompt = `{styles} + {color_bias} + {prompt_tail}`

### Tips for Good Icons

- Describe a **single central symbol**
- Specify **plain dark background with vignette**
- Note **no text, no full scene**
- Include **color accents** (teal, cyan, red for warnings)
- Request **chunky silhouette that reads at 64x64**

## Batch Generation Scripts

For large batches, create shell scripts:

```bash
#!/bin/bash
# generate_batch.sh
export OPENAI_API_KEY="$(cat ~/.openai_key.txt)"

# Critical icons get 3 variants
python tools/assets/generate_images.py --file art_prompts/ui_icons.yaml \
  --category main_navigation --variants 3 --yes --update-yaml

# Others get 1 variant
python tools/assets/generate_images.py --file art_prompts/ui_icons.yaml \
  --status pending --yes --update-yaml
```

## Troubleshooting

### API Key Not Set
```
Error: The api_key client option must be set
```
Solution: `export OPENAI_API_KEY="sk-..."`

### File Already Exists
```
Skipping asset_v1 (already exists, use --force to regenerate)
```
Solution: Use `--force` flag to overwrite

### No Assets Match Filter
```
No assets match the specified filters
```
Solution: Check `--status` and `--category` values match YAML

## Asset Categories

Current categories in ui_icons.yaml:
- main_navigation (10)
- employee_roles (8)
- employee_status (8)
- buttons_normal (6)
- buttons_hover (6)
- buttons_disabled (6)
- resources (10)
- decorative_corners (4)
- decorative_dividers (2)
- decorative_frames (1)
- decorative_headers (1)
- risk_indicators (5)
- alert_indicators (4)
- actions_research (8)
- actions_facilities (6)
- actions_policies (6)

Total: 91 assets defined
