
# Glowing Cat Buttons — Web & Godot Parity

This folder contains:
- `cat_icon.svg` — scalable cat icon (stroke-based).
- `index.html` & `glow_buttons.css` — a web demo mirroring the target look.
- `GlowButton.shader` — Godot CanvasItem shader for "under-glass nuclear" glow.
- `GlowButton.gd` — Godot script to turn a `Button` into a glowing button with hover/press behavior.

## Web
Open `index.html` in a browser. Adjust color variables in `glow_buttons.css`.

## Godot (4.x)
1. Copy `cat_icon.svg`, `GlowButton.shader`, and `GlowButton.gd` into your project (e.g., `res://ui/`).
2. In a scene, add a `Button`, set **Custom Minimum Size** to e.g. `Vector2(200, 56)`.
3. Assign `GlowButton.gd` as the script.
4. Create a `ShaderMaterial`, load `GlowButton.shader`, and set it on the Button's **material** (or let the script auto-create it).
5. Optional: put an `Icon` (TextureRect) as a child using `cat_icon.svg` (Godot imports SVG as VectorTexture). Align left, size 22×22.
6. Toggle `colorway` export (0 teal, 1 amber), tweak `glow_strength`.

Tip: For a pill button, set **Corner** uniform in shader close to `0.5` using a Material override.
