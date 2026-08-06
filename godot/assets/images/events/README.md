# Event images -- PACKED BUT UNDEMANDED

**Audited 2026-08-04. Nothing in the codebase references any file in this
directory.**

Eight `.webp` files live here:

```
event_board_v2.webp        event_board_v3.webp
event_crisis_v1.webp       event_crisis_v3.webp
event_opportunity_v2.webp  event_opportunity_v4.webp
event_secret_v1.webp       event_secret_v3.webp
```

Evidence of zero demand: grepping `assets/images/events` across all `.gd`,
`.tscn` and `.json` under `godot/` returns nothing but the `.import` sidecars.
No scene, no script, no data file names them, by `res://` path or by `uid://`.

## Why they are still here

`export_filter="all_resources"` means Godot packs the ENTIRE `godot/` tree into
the `.pck` whether or not anything loads it -- so these ship in every build.
That is exactly the packed-but-undemanded state ADR-0019 (pull-from-demand asset
pipeline) exists to stop.

**They are GRANDFATHERED. Pip ruled 2026-08-03 that already-packed assets stay
until the ADR-0019 audit runs. Do not delete them as part of a dead-code
sweep.**

## What "audited" would mean

Either (a) a demand site appears -- an event presenter that actually loads a
themed image per event class -- or (b) the ADR-0019 audit rules them out and
they move to `art_source/` (outside `godot/`, so out of the `.pck`).

If you move them: `grep -rn` BOTH the `uid://` from each `.webp.import` AND the
`res://assets/images/events/...` path across `godot/` first. Godot resolves
assets by UID, so a blind move breaks references silently (issue #787).

## Related orphan

`godot/assets/cats/default/` (5 doom-variant SVGs) is in the same state: its only
consumer was `contributor_manager.gd`, deleted 2026-08-04. Also grandfathered.
Note `godot/assets/cats/simple/` is NOT orphaned -- `office_cat.gd` loads from it.
