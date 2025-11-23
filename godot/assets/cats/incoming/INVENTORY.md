# Cat Assets Inventory - Incoming Staging Area

**Created:** 2025-11-22
**Status:** Staged for processing into game assets

## Overview

This directory contains cat images staged for integration into the game's contributor recognition system. These are the original images before processing into the 5 doom-level variants (happy, concerned, worried, distressed, corrupted).

## Contributor Cats (8 total)

### 1. Arwen & Chuck (web-arwen-chuck.jpg)
- **Size:** 38KB
- **Custodian:** Matilda
- **Contributor ID:** TBD (needs contributors.json entry)
- **Status:** Ready for variant generation

### 2. Arwen (web-arwen.jpg)
- **Size:** 54KB
- **Custodian:** Matilda
- **Contributor ID:** TBD
- **Status:** Ready for variant generation

### 3. Chucky (web-chucky.jpg)
- **Size:** 68KB
- **Custodian:** Nicki T.
- **Contributor ID:** TBD
- **Status:** Ready for variant generation

### 4. Doom Cat (web-doom-cat.jpg)
- **Size:** 54KB
- **Custodian:** Office (default/mascot)
- **Contributor ID:** default
- **Status:** **Priority - Default game cat**

### 5. Luna (web-luna.jpg)
- **Size:** 74KB
- **Custodian:** Nicki T.
- **Contributor ID:** TBD
- **Status:** Ready for variant generation

### 6. Mando/Jiggly (web-mando.jpg)
- **Size:** 71KB
- **Custodian:** Nicki T.
- **Contributor ID:** TBD
- **Status:** Ready for variant generation

### 7. Missy (web-missy.jpg)
- **Size:** 64KB
- **Custodian:** Spicy
- **Contributor ID:** TBD
- **Status:** Ready for variant generation

### 8. Nigel (web-nigel.jpg)
- **Size:** 66KB
- **Custodian:** Nicki T.
- **Contributor ID:** TBD
- **Status:** Ready for variant generation

## Base Images (3 total)

### office_cat_base.png
- **Size:** 251 bytes
- **Purpose:** Placeholder/base image
- **Status:** Check if still needed

### pdoom1-office-cat-default.png
- **Size:** 3.8MB
- **Purpose:** Large default office cat image
- **Status:** Needs optimization/variant generation

### small-doom-cat.png
- **Size:** 109KB
- **Purpose:** Small doom cat variant
- **Status:** May be existing variant, needs review

## Next Steps

### 1. Create Default Cat Variants (Priority)
For `web-doom-cat.jpg` (the official office cat):
- [ ] Create 5 doom-level variants:
  - `godot/assets/cats/default/happy.png`
  - `godot/assets/cats/default/concerned.png`
  - `godot/assets/cats/default/worried.png`
  - `godot/assets/cats/default/distressed.png`
  - `godot/assets/cats/default/corrupted.png`

### 2. Create Contributor Cat Variants
For each contributor cat (Arwen, Chucky, Luna, etc.):
- [ ] Determine cat_image_base name (e.g., "arwen", "chucky", etc.)
- [ ] Generate 5 doom variants per cat
- [ ] Place in `godot/assets/cats/{cat_image_base}/`

### 3. Update contributors.json
- [ ] Add entries for each cat custodian
- [ ] Link cat_image_base to contributor ID
- [ ] Include metadata (contribution_types, cat_name, etc.)

### 4. Processing Pipeline
Consider creating automated tools for:
- Batch resizing to game-appropriate dimensions (256x256?)
- Applying visual filters for doom levels (color grading, effects)
- Converting JPEG → PNG for game use (transparency support)
- Quality/compression optimization

## Expected Game Asset Structure

```
godot/assets/cats/
├── default/
│   ├── happy.png
│   ├── concerned.png
│   ├── worried.png
│   ├── distressed.png
│   └── corrupted.png
├── arwen/
│   ├── happy.png
│   ├── concerned.png
│   ├── worried.png
│   ├── distressed.png
│   └── corrupted.png
├── chucky/
│   └── [5 variants]
├── luna/
│   └── [5 variants]
└── [etc...]
```

## Source Chain

1. **Origin:** Individual cat photos from contributors
2. **Website Repo:** `pdoom1-website/public/assets/dump/` (web-optimized JPEGs)
3. **This Repo:** `assets/images/assets/cats-gallery/` (synced from website)
4. **Staging:** `godot/assets/cats/incoming/` (this directory)
5. **Game Assets:** `godot/assets/cats/{cat_id}/` (processed variants)

## Related Files

- [godot/scripts/data/contributor_manager.gd](../../scripts/data/contributor_manager.gd) - Cat loading logic
- [godot/scripts/ui/office_cat.gd](../../scripts/ui/office_cat.gd) - Cat display system
- [godot/data/contributors.json](../../data/contributors.json) - Contributor metadata
- [assets/images/assets/cats-gallery/README.md](../../../../assets/images/assets/cats-gallery/README.md) - Source metadata

## Notes

- Current system expects PNG files with transparency support
- Doom variants determined by percentage: 0-20%, 21-40%, 41-60%, 61-80%, 81-100%
- ContributorManager handles fallback to default cat if contributor cat missing
- office_cat.gd updates cat display based on doom level changes each turn
