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
