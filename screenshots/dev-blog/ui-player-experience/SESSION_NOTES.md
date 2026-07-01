# UI / Player-Experience lane — round 1 playtest feedback (2026-06-30)

Branch `feat/ui-player-experience`. First hands-on playtest of #510 (submenu/UI polish) and
#512 (doom trend graph + bushfire color ramp). Screenshots are Pip's; filenames describe the issue.

## Screenshots
| File | What it shows |
|---|---|
| `01-doom-meter-reposition-down.jpg` | Doom cluster sits high-center; Pip wants it moved down, sparkline bar too short |
| `02-submenu-needs-move-right.jpg` | Publicity submenu opens over/left of the icon column, not to its right |
| `03-submenu-overlays-bottom-ui.jpg` | Submenu bleeds over the bottom command bar; needs to move right |
| `04-victory-box-needs-border.jpg` | Victory panel has no border — blends into the dimmed game |
| `05-submenu-transparent-overlay.jpg` | Submenu panel is see-through; action icons show through it |
| `06-doom-graph-dots-and-wider.jpg` | 76% EXTREME crimson reads well; sparkline wants dots + more width/height |

## Addressed this session (built, awaiting re-eyeball)
- **Submenus open to the RIGHT** of the clicked action button (x = button right edge + gap), top-aligned.
- **Submenu panels near-opaque** + bordered (no more see-through over icons).
- **Keyboard-opened submenus align like clicks** (find the matching action button).
- **Close affordance tidied** — styled `✕` button, `[ESC] close` moved bottom-right (clear of centered footers).
- **Sparkline**: dots at each point, per-segment line color (the line carries the bushfire hue over time),
  taller (92px), more points (window 24), fainter zone bands (less permanent rainbow).
- **Bushfire ramp**: TERMINAL is now **saturated dark purple instead of black**; upper half leaned darker;
  legibility glow shifted magenta so the dark-purple hue survives on strokes.
- **Victory/game-over box**: solid panel + border so it reads as a delineated overlay.
- **Debug**: PageUp/PageDown nudge doom ±10 (debug builds only) to sweep the ramp + fill the graph fast.

## Deferred — design calls to workshop with Pip
- **Horseshoe / speedometer doom gauge** (replace the full circle with a <360° "gas gauge" fill).
- **Doom cluster reposition-down** (scene layout; Pip wants to review coupled with gauge + bar size).
- **Full "Doom Screen"** future feature: event/impact markers (Spotify-comments style), animation-over-time,
  richer situational-awareness info as the player unlocks insight.
- **Expand panel** wants axis labels / gridlines / time-series notes.
- Tutorial/intro note so the "click to expand" trend affordance is discoverable.

## Balance note (not this lane — Pip handles on `main`)
Game is too easy to win (~9 turns, accidental victory via safety-flywheel momentum to 0% doom).
Hard to exercise late-game UI states without the debug doom keys above.
