# Glowing Cat UI Button Kit  --  Design Decisions (Web + Godot)

_Last updated: 2025-10-31_

## 1) Aesthetic & Theme
- **Era vibe:** early‑2000s command‑center dashboards (Windows XP/Longhorn prototypes, Bloomberg terminals, NATO C2) with subtle skeuomorph.
- **Material feel:** smoked glass + dark ABS plastic with anodized edge accents.
- **Mood:** calm, professional; can escalate toward ominous via overlays as ,        # LEFT DOUBLE QUOTATION
            '”': doom tier” rises.
- **Texture policy:** extremely light film grain; faint scanlines applied at **container level** (never per‑button).

## 2) Core Visual Language
- **Bevel:** top highlight + bottom shadow for a cautious 3D press effect.
- **Under‑glass glow:** soft outer neon ring + inner specular strip (curved band) to imply backlit hardware.
- **Edge discipline:** rounded corners; consistent ring thickness; no harsh halos.
- **Icon emphasis:** minimalist line icons; the ,        # LEFT DOUBLE QUOTATION
            '”': cat” icon is the hero motif for special/armed actions.

## 3) Color System (Design Tokens)
- **Base surface**
  - Graphite `#0E1318`
  - Steel `#1C2730`
  - Deep `#0F171D`
- **Accents**
  - Action Teal `#1EC3B3` (hover `#0FA5A0`)
  - Warn/Armed Amber `#F6A800` (press/red optional escalation)
- **Neutrals**
  - Off‑white text `#E9F2F2`
  - Chrome highlight line `#6B7C8C` (1 px, low opacity)

> **Doom‑tier overlays (optional, applied globally):**  
> Tier 0  ->  none | Tier 1  ->  `#F6A800 @ 6%` | Tier 2  ->  `#E9752E @ 10%` | Tier 3  ->  `#E24A3B @ 14%` | Tier 4  ->  `#B31217 @ 18%`

## 4) Typography & Iconography
- **Type:** Inter for labels (all‑caps, +0.06em tracking); techno display font (e.g., Michroma/Orbitron) allowed for headers.
- **Icon grid:** 20/24/32 px square cells; ~1.5 px stroke at 1x; rounded joins for neon continuity.
- **Signature icon:** `cat_icon.svg` (stroke‑based; scalable; uses `currentColor` for tinting).

## 5) Geometry, Sizes, and Spacing
- **Corner radius:** 12 px (standard); 999 px for pills/rounds.
- **Heights:** 48 px (standard) / 56 px (CTA); circular icon buttons 56 px.
- **Padding:** H 16 - 22 px; V 8 - 12 px; icon‑label gap 8 - 10 px.
- **Alignment:** label vertically centered; 1 px content drop on pressed state.

## 6) Button Types
- **Primary (Confirm/Commit):** teal fill + neon ring.
- **Secondary (Utility/Status):** dark fill; teal text/icon; softer ring.
- **Destructive/Armed:** amber (hover)  ->  red (pressed) if escalation desired.
- **Icon‑only (Round):** neon cat or system icon; 56 px circular.
- **Pill CTA:** maximum radius for high‑prominence ,        # LEFT DOUBLE QUOTATION
            '”': ESCALATE/ARM” actions.
- **Segmented/Toggle (optional extension):** shared border; active segment holds pressed bevel.

## 7) State Matrix
- **Default:** dark gradient `#22303A  ->  #172028`; 1 px top highlight (`#6B7C8C @ ~30%`); inner shadow.
- **Hover:** +3 - 6% brightness; slightly stronger glow ring.
- **Pressed/Active:** bevel inverted; gradient compressed `#0F1A20  ->  #0B1318`; content nudged +1 px.
- **Focused:** 1 px teal focus ring outside stroke; must be visible against maps.
- **Disabled:** desaturated, reduced contrast; maintain >=4.5:1 label contrast on dark.
- **Armed/Danger:** amber ring + cat icon; optional red press state at higher doom tier.

## 8) Micro‑FX Details
- **Specular strip:** top‑third gloss band, ~18% white fade, curved mask.
- **Edge neon ring:** 1 px crisp edge + soft outer bloom; no overblown halos.
- **Chromatic bleed (Tier >=3):** subtle 0.25 px horizontal R/G offset on extreme edges.
- **Noise/Scanlines:** added only to the panel/container, not the button texture.

## 9) Web Implementation Notes
- **Tech:** pure CSS + inline SVG; uses CSS variables for quick theming.
- **Effects mapping:**
  - `::before` = specular strip (screen blend‑like look)
  - `::after`  = edge neon ring (outer glow)
  - `filter: drop-shadow()` on SVG icon = inner neon
- **Accessibility:** focus ring always visible; hover/pressed deltas obvious at 110% scale.

## 10) Godot 4 Implementation Notes
- **Shader:** CanvasItem rounded‑rect SDF with bevel, glow ring, and gloss band.
- **Primary uniforms:**  
  - `base_color`  --  background plastic  
  - `edge_glow_color`  --  teal/amber/red tint  
  - `corner`  --  0..0.5 roundedness  
  - `glow`  --  ring intensity  
  - `gloss_height`  --  position of specular strip
- **Script (`GlowButton.gd`):** hover boosts glow; pressed nudges content 1 px; exported `colorway` (0 teal / 1 amber) + `glow_strength`.
- **Icons:** import `cat_icon.svg` as VectorTexture; size ~22 x 22; align left with 8 - 10 px gap.
- **Scaling:** prefer vector + shader over bitmap for crispness; if exporting textures, use 9‑slice with 10 px caps.

## 11) Export & QA Checklist
- Labels readable in disabled and armed states (>= 4.5:1 contrast).
- Hover/pressed states visibly distinct at 110% UI scale.
- Focus ring visible on busy maps and imagery.
- Corners remain crisp under 9‑slice or vector scaling.
- Doom overlay does not crush contrast on red/danger buttons.
- SVG strokes >= 1.5 px at target scale to avoid shimmer.

## 12) File & Versioning Convention
```
ui/buttons/glowcat/
  web/
    index.html
    glow_buttons.css
    cat_icon.svg
  godot/
    GlowButton.shader
    GlowButton.gd
```
- Semantic versioning: `v1.0.0` for this baseline; variants as `-pill`, `-round`, `-seg` if/when added.

---

### Rationale (short)
The kit balances recognisable early‑2000s enterprise aesthetics with modern readability and responsiveness. The neon‑under‑glass motif reads well at small sizes, remains performant (shader + vector), and provides a clean path for escalating tension via global overlays without redrawing assets.
