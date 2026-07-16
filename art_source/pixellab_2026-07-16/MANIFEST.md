# PixelLab generation run — 2026-07-16 (character/aesthetic exploration)

> First PixelLab session for P(Doom)1. Preserved in full — **including discards** — because
> (a) blog material, (b) discards are negative evidence for future tuning, (c) a stylistic
> reference set for any human artist we later bring in. Each entry: the exact prompt, params,
> and the verdict (Pip's read + Fable's notes). PixelLab character IDs are kept so any sprite
> can be re-animated or re-rolled later (characters persist in the PixelLab account by name;
> the hat was a map-object that auto-deletes there after 8h — the PNG here is the only copy).
>
> Files: `<NN>-<name>_<direction>.png` (48px sprite on a 68px canvas, 4 directions). Base
> character description held CONSTANT across the style tests (a Black woman, 30s, box braids,
> round glasses, business-casual) so only the *dials* vary — clean A/B evidence.

## The verdict (what we learned — the leading direction)
- **Un-desaturate → clearer read.** Pip LOVED V4 (full bright color) — "reads a lot clearer."
  The muted/desaturated palette read *drab*. Desaturation is reserved for grimy in-game
  *textures* in the "scummy phase", NOT the character palette.
- **Chibi / cartoon proportions → the chunky Zelda/Stardew feel** Pip wanted. Stylized/heroic
  went *leaner* = away from the direction.
- **Leading combo = V4/V5 lineage: full warm color + chibi-or-cartoon proportions + low-top-down.**
  Cozy-grim balance (C1/C2 tuned toward it). "Warm + legible + a little wry."
- **View:** low-top-down / side / high-top-down all work; **oblique is BROKEN** (BETA distorted
  the figure — see V6). Don't use oblique for characters.
- **Cast approach works:** same style, different diverse physical identities → distinct,
  representative, ability-uncorrelated (C3/C4/C5).
- **Cats** via `body_type=quadruped, template=cat` — come with their own anim set (idle, sitting,
  licking, running…). Cozy singed vs spooky doom-form both read.
- **Accessories** (the hat) via `create_map_object` — works for the swappable-cosmetic layer.
- **`create_character_state` bakes a cosmetic onto a base character consistently across ALL
  rotations** (linked via `group_id`) — validated by putting top hats on both cats (19/20).
  For TRUE in-game swappability we still want separate overlay sprites, but this is exactly
  how you'd bake fixed cosmetic *variants* of a character, and it Just Works.
- **Process:** PixelLab throttles concurrency — firing 8+ at once fails ~half with "heavy load."
  Keep batches to ~3–4 and pace.

## Inventory

### Style-dial tests (constant base character; only dials vary)
| # | file | id | proportions | color | view | verdict |
|---|---|---|---|---|---|---|
| 00 | original-default-muted | 0a159f6c | default | muted | low-top-down | baseline; "generic RPG villager" risk |
| 01 | V1-chibi-muted | dfe0aae2 | chibi | muted | low-top-down | Pip liked the Zelda/Stardew read |
| 02 | V2-cartoon-muted | 906ca143 | cartoon | muted | low-top-down | "chunky but less than chibi, OK" |
| 03 | V3-stylized-muted **DISCARD** | 9e84817a | stylized | muted | low-top-down | tall/lean "surprisingly OK" but glasses failed; wrong chunk direction |
| 04 | V4-fullcolor-default **LOVED** | d51fb474 | default | full bright | low-top-down | **Pip LOVED — "reads a lot clearer"** |
| 05 | V5-fullcolor-chibi **GOOD** | 01bb55c8 | chibi | full bright | low-top-down | **"step in the right direction" — cozy/grim** |
| 06 | V6-chunky-oblique **BROKEN** | 22a1672e | cartoon | full | oblique | oblique BETA distorted the figure — negative evidence |
| 07 | V7-cartoon-sideview | 52817353 | cartoon | muted | side | side view works |
| 08 | V8-fullcolor-chibi-hightopdown | e8b9edd2 | chibi | full | high-top-down | steeper angle, colorful |
| 09 | V9-heroic-fullcolor | 1c99a0f9 | heroic | full | low-top-down | heroic = taller/leaner build |

Style-test prompt (00–03, 06 muted): *"…muted desaturated color palette, retro 1990s corporate aesthetic"*.
Full-color (04,05,08,09): *"…bright cheerful colors, cartoony retro RPG style, pixel art"*. V6: *"…colorful cartoony retro RPG, chunky 16-bit pixel art"*.

### Cozy-grim refinement (the leading direction, tuned)
| # | file | id | prompt notes | verdict |
|---|---|---|---|---|
| 10 | C1-V4-cozywarm | c3a7795d | *"warm cozy color palette, cheerful but a little weary"* (default props) | strong warm+clear |
| 11 | C2-V5-cozygrim-chibi | 38e360ea | *"cozy muted-warm colors, wry tired expression"* (chibi) | cozy-grim chibi |

### Diverse cast (same style, different identities — representation, ability-uncorrelated)
| # | file | id | identity | verdict |
|---|---|---|---|---|
| 12 | C3-cast-burnedout-senior | 83c8e171 | tired older white man, bald, rumpled cardigan, coffee mug | **came out great** |
| 13 | C4-cast-eccentric-junior | e4612834 | nonbinary 20s, teal undercut, oversized hoodie (chibi) | expressive, colorful, distinct |
| 14 | C5-cast-south-asian-man | 6571b9b1 | South Asian man 40s, glasses, beard, heavyset | reads distinct |

### Cats (doom-barometer forms — "a lot of effort into our cats")
| # | file | id | form | verdict |
|---|---|---|---|---|
| 15 | Cat1-singed-tabby | 12458a84 | orange tabby, faintly singed (low-doom cozy gag) | adorable |
| 16 | Cat2-spooky-doom | 81ba732c | eerie black cat, glowing eyes, smoke (high-doom form) | distinctly creepier — good band contrast |

### Flavour
| # | file | id | thing | verdict |
|---|---|---|---|---|
| 17 | Operator-silhouette | f165e489 | shadowed suited figure (Dr Claw/Gendo operator), side view | silhouette worked |
| 18 | Hat-tall (map object) | efc3c3a2 | absurdly tall ornate top hat (impostor-satire cosmetic) | the gag lands; 48x88 |
| 19 | Cat1-tophat | bead2cfe | cozy tabby wearing a jaunty top hat (create_character_state) | delightful |
| 20 | Cat2-spooky-tophat | 03ed6f4f | spooky doom-cat wearing a formal top hat, glowing eyes | **the whole game in one sprite** |

## Next steps (when Pip returns / locks direction)
- Pick the final style combo (leading: full warm color + chibi/cartoon + low-top-down, cozy-grim tuned).
- Then per chosen base: generate the four OfficeFloor clips (`idle`/`walking`/`working`/`stressed`,
  stressed = the priority dashboard-alarm), export, build a `SpriteFrames`, wire to `OfficeFloor.set_sprite_frames`.
- Future: human-artist collaboration — this set is the stylistic reference/starting point.
