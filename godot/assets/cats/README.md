# Office Cat Assets

> **[!] Audited 2026-08-04 -- half of this directory is wired to nothing.**
>
> - `simple/` is **LIVE**: `godot/scripts/ui/office_cat.gd` picks a random photo
>   from it using a hardcoded `CAT_NAMES` dictionary.
> - `default/` (the 5 doom-variant SVGs described below) is **ORPHANED**. Its
>   only consumer was `godot/scripts/data/contributor_manager.gd`, deleted
>   2026-08-04 for having zero callers. Nothing loads these SVGs. They are kept
>   under the ADR-0019 grandfathering rule for already-packed assets, not because
>   they are used.
> - The doom-level variant system does not exist. `office_cat.gd`'s
>   `update_doom_level()` is an explicit no-op.
> - There is no contributor sync. `godot/data/contributors.json` (an empty stub)
>   was deleted 2026-08-04; the sync script that was meant to fill it never ran.
>   See issue #1115.
>
> **UPDATE 2026-08-06 -- recognition now EXISTS, by a different route.** The
> abandoned design (a synced `contributors.json` + a `ContributorManager`) is
> still dead and should not be revived as written. What replaced it:
> `CREDITS.md` at the repo root is the source of truth, `scripts/generate_credits.py`
> derives `godot/data/credits.json`, and `godot/scenes/credits_screen.tscn`
> (welcome menu -> Credits) renders every cat with its contributor. The in-run
> cat gained a hover tooltip naming the same person. `office_cat.gd` still owns
> `CAT_NAMES`; a GUT test (`tests/unit/test_credits_data.gd`) fails if that
> roster and the CREDITS.md table ever disagree. Doom variants remain unbuilt.

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

- `docs/CONTRIBUTOR_SYSTEM.md`: Full contributor recognition system docs (carries
  its own "half dead" header -- read that before trusting it)
- ~~`scripts/data/contributor_manager.gd`~~: **DELETED 2026-08-04** (zero callers;
  carried the #796 `FileAccess.file_exists()` export-blindness bug)
- `godot/scripts/ui/office_cat.gd`: what actually renders a cat today
- pdoom-data issue #22: Contributor sync pipeline
- pdoom1-website issue #70: Airtable CRM system
