# Office Cat Assets

This directory contains office cat images for the contributor recognition system.

## Directory Structure

```
cats/
|--- default/               # Default office cat (shipped with game)
|   |--- happy.png         # 0-20% doom level
|   |--- concerned.png     # 21-40% doom level
|   |--- worried.png       # 41-60% doom level
|   |--- distressed.png    # 61-80% doom level
|   `--- corrupted.png     # 81-100% doom level
`--- {contributor_uuid}/    # Contributor-specific cats (synced from pdoom-data)
    |--- happy.png
    |--- concerned.png
    |--- worried.png
    |--- distressed.png
    `--- corrupted.png
```

## Image Specifications

- **Format**: PNG with transparency
- **Size**: 256x256 pixels
- **Style**: Consistent with PDoom game art style
- **Doom Progression**: Each variant should visually "doom-ify" as the doom meter increases
  - `happy.png`: Clean, content office cat
  - `concerned.png`: Slightly worried expression
  - `worried.png`: More distressed, environmental corruption begins
  - `distressed.png`: Heavily corrupted environment, cat clearly stressed
  - `corrupted.png`: Full doom aesthetic (similar to Doom Guy's bloodied face at low health)

## Default Cat

The default cat images (in `default/`) are used when:
1. No contributors are loaded (empty contributors.json)
2. A contributor's images are missing or fail to load
3. The player hasn't unlocked any contributor cats yet (future feature)

## Contributor Cats

Contributor cats are synced from the **pdoom-data** repository:
- Source: `pdoom-data/cats/{contributor_uuid}/`
- Sync: Automated via CI/CD or manual sync script
- Processing: See `tools/process_contributor_cats.py` for image processing pipeline

### Adding Contributor Cats

1. Contributor submits photo via pdoom1-website form
2. Admin reviews and approves in Airtable CRM
3. Cat images are processed (manually or via AI tool):
   - Extract subject, remove background
   - Generate 5 doom variants
   - Ensure style consistency
4. Images uploaded to pdoom-data repository
5. Sync to pdoom1 via CI/CD
6. Contributor appears in next game release

## TODO

- [ ] Create default cat images (5 variants)
- [ ] Document cat art style guide
- [ ] Create image processing pipeline (see pdoom-data issue #22)
- [ ] Add example contributor cat directory

## Related Documentation

- `docs/CONTRIBUTOR_SYSTEM.md`: Full contributor recognition system docs
- `scripts/data/contributor_manager.gd`: Contributor manager implementation
- pdoom-data issue #22: Contributor sync pipeline
- pdoom1-website issue #70: Airtable CRM system
