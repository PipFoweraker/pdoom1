# UI / UX Decisions Log

> **Status**: Living log — append decisions as they're made.
> **Purpose**: Capture *why* UI/UX calls were made, so later work doesn't relitigate or accidentally reverse them.
> **Related**: `TONE_AND_ART.md`, issue #510 (UI polish)

Each entry: the decision, the rationale, and what would justify revisiting it.

---

## Event option buttons show *costs*, not *benefits* (#510, 2026-06-30)

**Decision.** Event choice buttons display a compact inline **cost** summary only —
e.g. `[Q] Emergency Intervention ($30,000, 2 AP)`. Effects/benefits stay in the hover
tooltip, not on the button face.

**Rationale.**
- The button's job is a fast affordability read at decision time. Costs answer "can I
  even pick this?"; benefits answer "is it worth it?" — a slower, more deliberative
  question that the tooltip already serves.
- Benefit *effects* are multi-resource and often signed (some go up, some down). Rendered
  inline they bloat the label and bury the cost, defeating the quick-scan purpose.
- Costs are short and uniform (money + AP, occasionally one more resource), so they stay
  legible on a single line.

**Formatting.** Money via `GameConfig.format_money()` (house style, `$30,000` with commas —
*not* abbreviated `$30k`); action points as `N AP`; other resources as `N <Resource>`.
See `_format_cost_summary()` in `scripts/ui/main_ui.gd`.

**Revisit if.** Playtesting shows players repeatedly opening tooltips just to compare
benefits before choosing — that would be evidence the benefit info needs to be more
glanceable (e.g. a second dim line, or an icon row), at which point reconsider putting a
condensed benefit hint on the button.

---

## Submenus expand from the clicked action button (#510, 2026-06-30)

**Decision.** Action submenus (hire / fundraise / publicity / strategic / travel /
operations, plus the paper-submission and conference sub-dialogs) open anchored to the
**right of the left icon panel** and **vertically aligned to the button that opened them**,
so they read as expanding from that row. No slide/expand tween (kept static for now).

**Rationale.** StarCraft-2-style "pop-out" reduces the eye-travel between the action you
clicked and the menu that results. A tween was considered and deferred — alignment delivers
most of the readability win without input-timing risk.

**Revisit if.** The static jump feels abrupt in motion → add a short slide/fade tween in
`_align_submenu_to_button()`'s caller path.

---

## All submenus carry a close affordance; event dialogs do not (#510, 2026-06-30)

**Decision.** Every submenu gets a clickable `[X]` (top-right) and a dim `[ESC] close`
hint (bottom-left). **Event dialogs are deliberately excluded** — they must be completed
via a choice (no ESC/X close), preserving the no-soft-lock guarantee from #452.

**Rationale.** Submenus are exploratory and reversible; events are commitments. The
affordance makes the reversible case discoverable (both mouse and keyboard) without
weakening the commitment case.

---

## Doom Meter trend graph + bushfire color ramp (#512, 2026-06-30)

A stock-price-style trend graph for the doom meter, which dragged a shared color-system
redesign along with it.

**Data storage.** Doom history lives in `GameState` as `doom_history: Array[float]`,
appended once per turn at `turn_manager.gd` (right after `state.doom` is set), and
serialized in `to_dict()`/`from_dict()`. It is authoritative game state (like a price
series), so it survives save/load and any system can read it — not a UI-side ring buffer.

**Visual form.** An **always-on sparkline** sits with the doom gauge (last ~12 turns),
because the tone doc frames doom as *"terrified of the trend"* — the trend should be
permanently visible, not hidden. Clicking it expands a full-history panel (which reuses the
`_add_submenu_close_affordance()` helper from #510).

**Scale & style.** Y-axis **fixed 0–100** with **zone bands** (not auto-scale) — the point
is "how dead are you," an absolute read that auto-scaling would erase. **Area fill** under
the line (zone-colored), line stroked in the current doom-zone color. Window = 12 turns
(tunable). Event markers and a momentum overlay are **deferred** (event markers need
per-event turn data we don't yet store; momentum is already implicit in the line's slope).

**Bushfire color ramp (shared).** Replaces the two divergent doom-color functions
(`ThemeManager.get_doom_color` flat 30/60/85; `DoomMeter.get_doom_color` lerped 30/60/80)
with ONE smooth ramp in `ThemeManager`; `DoomMeter` is de-duped to call it. The ramp is
deliberately **asymmetric — one green safe zone, then six escalating stops** through yellow,
orange, red, dark crimson, purple, near-black, à la Australian bushfire danger signs
("only one green, then many subtle indicators of just how dead you are"). Anchor stops:

| Doom | Tier | RGB |
|---|---|---|
| 0–15 | NOMINAL | 0.30, 0.80, 0.35 |
| 30 | ELEVATED | 0.90, 0.80, 0.20 |
| 45 | HIGH | 0.95, 0.55, 0.15 |
| 60 | SEVERE | 0.90, 0.25, 0.20 |
| 74 | EXTREME | 0.60, 0.10, 0.13 |
| 87 | CATASTROPHIC | 0.45, 0.10, 0.52 |
| 96–100 | TERMINAL | 0.10, 0.05, 0.12 |

Applied to the **shared** `ThemeManager.get_doom_color`, so the gauge, numeric label, and
resource bars all inherit it (branch-isolated, so no clash with main-branch QA).

**Two known tensions to handle in the build:**
- *Legibility at the top end* — near-black line on a dark CRT background (#529) vanishes.
  Keep the **line stroke bright/desaturated** while only the **fill** goes near-black; same
  fix applies to the gauge arc. Solve now so #529 doesn't fight it.
- *Colorblind channel* — `DoomMeter`'s status labels (SAFE/CAUTION/DANGER/CRITICAL) must
  extend to the 7 tiers (NOMINAL…TERMINAL) so the non-color channel keeps pace.

**Revisit if.** Playtesters find the always-on sparkline too noisy → fall back to
expand-on-click only. If absolute 0–100 reads too flat at low doom → revisit auto-scale
for the *expanded panel only* (keep the always-on absolute).
