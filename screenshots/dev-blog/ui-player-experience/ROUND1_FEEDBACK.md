# 🖨️ QA / Eyeball Clipboard — UI lane

> **Ephemeral working doc — delete before PR** (like `PRIMER_UI.md`). Not committed game content.
> Running list of things for Pip to visually review / playtest, grouped by feature.
> Tick as you go. Anything that fails → note it under the item and I'll fix.

How to drive it: open the project in the Godot editor, run the game, and walk each item.
Binary: `Godot_v4.5-stable_win64.exe --path godot` (or just press Play in-editor).

**DEBUG (debug builds only):** `PageUp` / `PageDown` nudge doom ±10 and add a graph point — use it to
sweep the bushfire ramp and fill the sparkline fast.

---

## ⟳ ROUND 1 FIXES — re-eyeball these (2026-06-30)

From your screenshot feedback. Screenshots filed in `screenshots/dev-blog/ui-player-experience/`.

- [ ] **Submenus open to the RIGHT** of the clicked button now (not over the icon column), top-aligned — by click AND by keyboard (H/F/P/T). (screen2, screen3, line 16/17)
- [ ] **Submenu panels are near-opaque + bordered** — icons no longer show through. (screen5)
- [ ] **Close affordance tidied** — styled `✕`, `[ESC] close` now bottom-RIGHT (clear of "Pool: 3/6"). (screen5, line 22)
- [ ] **Sparkline**: dots on each point; the **line itself changes color** over time; taller; 24 points; bands much fainter (less rainbow). (screen6, line 47/59)
- [ ] **Ramp**: TERMINAL is now **saturated dark purple, not black**; upper half darker. (line 47)
- [ ] **Victory box** now has a solid border/panel. (screen4, line 57)

**Deferred to a design pass (NOT changed yet):** horseshoe gauge, doom-cluster reposition-down,
full "Doom Screen" + event markers, expand-panel axis/gridlines. See SESSION_NOTES.md.

---

## #510 — UI polish  ·  status: built, awaiting eyeball  ·  commit BEFORE #512

### Submenu alignment (Task 1)
- [review screen1, the submenu only opens partly to the right, also note my intended reponsitioning downward of the doom meter generally ] Click each left-panel action that opens a submenu (Hire, Fundraise, Publicity, Strategic, Travel, Operations). Submenu opens to the **right of the icon panel**, with its **top aligned to the button you clicked** (reads as expanding from that row).
- [see screen2, screen3, needs to move to the right, increase opacity by about 20% to make the differenentiation clearer. should feel more 'opens to the right', not 'opens on top of / slightly below' ] Open a submenu via the **bottom-most** action button — confirm it doesn't run off the bottom of the screen (it should clamp into view).
- [Opening by keyboard seems to open up in the top left, not showing the same behaviour as the buttons, so the positioning looks odd. The screens should open correspondingly to where they would if clicked by a button, even if interfaced with via the keyboard. ] Open via **keyboard** (H / F / P / T) — opens at default position (no clicked button to align to). Confirm it still looks right.

### Close affordance (Task 2)
- [Yes ] Each submenu shows a clickable **`[X]` top-right** and a dim **`[ESC] close`** hint bottom-left.
- [Yes] `[X]` click closes the submenu. **ESC** closes it too.
- [see screen5, the submenu hints don't visually collide but we can definitely improve the formatting and layout a bit, open to suggestions to improve readability etc for player ] On the smaller submenus (e.g. Hiring "Pool: 3/6" status line), check the bottom-left `[ESC] close` hint **doesn't visually collide** with centered footer text. ← most likely cosmetic snag
- [ Yes] Open an **event popup** → confirm it has **no** X / ESC-close (events must be completed — by design, #452).

### Event cost display (Task 3)
- [Yes ] Trigger an event with choices. Each option button shows an inline cost, e.g. `[Q] Emergency Intervention ($30,000, 2 AP)`.
- [Reads OK ] Money uses house format (`$30,000`, commas, not `$30k`). AP shows as `N AP`. Confirm that reads well / fits the button width (buttons are 500px).
- [Yes ] An option you **can't afford** still shows its cost and is greyed/disabled.

### Sub-dialogs (extension)
- [Yes ] Travel → **Submit Paper** dialog and **Attend Conference** dialog each show the `[X]` + `[ESC] close` affordance (in addition to their existing Cancel button — note if the X+Cancel redundancy bugs you).

**Decision notes for these:** `godot/docs/design/UI_DECISIONS.md`

---

## #512 — Doom trend graph  ·  Stage 1 of 3: bushfire color ramp  ·  status: built, awaiting eyeball

> To see the ramp across its range you need doom to climb — play a few turns into rising doom,
> or use any debug doom setter (ask me to add a temporary debug key if that's a hassle).

### Shared color ramp (gauge + labels + bars all changed)
- [I think the bar needs to be double the height it is currently just to start taking up a reasonable amount of screen real estate. I am less keen on the circular 'doom' gauge but, for now, can we consider modifying it so it looks like an inverted U or a horseshoe so the doom meter more clasically 'fills up' like a petrol meter or a gas meter moving from empty (mostly on the left prong) through halfway (vertical) and then descending on the right down towards the maximum point? we can do clever math to scale the 100%itude into a less than full circle.  ] The circular **doom gauge** now follows the bushfire ramp: **one** green (≤15%), then yellow → orange → red → dark crimson → **purple** (~87%) → near-black (terminal). Walk doom up and confirm the transitions read well.
- [Let's review this once we've increased the size of the bar and moved it down as per screen1 ] **Legibility at the deadly end** (the key thing): above ~85% the gauge arc + the numeric `%` should glow **ember-rose** (bright), NOT vanish into black. The near-black is reserved for the trend graph's *fill* (Stage 3). Confirm the gauge/number stay readable at 90–100%.
- [I reserve judgment ] **Numeric doom label** and **resource bars** recolor along the same ramp (and stay legible at the top end).
- [I reserve judgment ] **Colorblind mode** (toggle in settings): gauge status label now reads NOMINAL / ELEVATED / HIGH / SEVERE / EXTREME / CATASTROPHIC / TERMINAL across the range.
- [The current version is a little hard to differentiate. Also, I'm less sold on having all the colours be displayed at once because it creates a permanent gradient / rainbow, maybe we can experiment with having the line itself change colour as it maps over time and the visual of the line is reinforced with the colour? I think we can lean slightly more reavily into the darker colourset overall if we mentally include 'saturated but dark purple' as one step above red as a replacement for black. ] Overall vibe check: does "one green, then many shades of dead" land the bushfire-sign feeling you wanted? Note any stop you'd shift (thresholds + RGB are in `ThemeManager.DOOM_STOPS`, easy to tune).

## #512 — Doom trend graph  ·  Stages 2–3: data + sparkline widget  ·  status: built, awaiting eyeball

> Play several turns so doom moves and history accumulates (the graph needs ≥2 points to draw a line;
> with 1 point it shows only the faint zone bands — that's expected on turn 0/1).

### Always-on sparkline (under the gauge)

[general notes from playtesting session related to UI
victory screen vertical box could do with a border around it to make it easier to read as an overlay on the end game screen, right now we only dim the background a little but the edge of the box isn't very well delineated.
I need to go back to main to tweak the game's settings as it's difficult to make the game last longer than 9 turns without accidentally winning at the moment]
- [see screen6, screen6 could do with dots on the points of each doom calculation, let's extend the goom graph horizontally to allow for more time series to increase both our undersatnding of the trend over time. Perhaps we can make a note for future development for a Doom screen which we can populate more information into as the player gains situational awareness. ] A small **trend sparkline appears directly below the doom gauge** in the right column (number → gauge → spark → win/lose text).
- [ Y but as noted above in screen6 I would like to eperiment with adding more time points ot the series and also increasing the visual length of it so players can see what's happened. I am mindful of the UI for spotify where you can see a lot of events that influence the doom meter's progression (similarly to comments on a song in spotify) so you can see points of impact] As you end turns, the line **extends right** and tracks the doom number's ups/downs.
- [ Now that I've seen it in action over time, the background colour changing is nice. Preserve the option for us to see this played out as some kind of animation-over-time in the do-be-developed Doom Screen] Faint **horizontal zone bands** sit behind the line (green low → … → near-black high), Y pinned 0–100. The line is filled underneath and stroked in the ember-bright color (stays visible).
- [Yes but this isn't made obious elsewhere. Consider a note to add this in the tutorial or introduction.  ] Hovering shows the "Doom trend — click to expand" tooltip.

### Expand panel (click the sparkline)
- [Y ] Clicking the sparkline opens a **larger full-history panel** (centered), titled "DOOM TREND — FULL HISTORY".
- [ Y] It carries the same **`[X]` + `[ESC] close`** affordance from #510; both close it.
- [This would be better with notes on the time series or marks on the axes or gridlines or all 3 ] The full-history graph shows **all** turns (not just the last 12), so early game is visible.

### Data integrity
- [Not tested ] (If you have save/load) save mid-game, reload — the trend graph **retains its history** (it's in GameState, serialized).
- [Yes ] Start a **new game** — the graph **resets** and seeds a single starting point (~50%).

### Tunables if anything feels off
- Window length (always-on): `DoomTrendGraph.window_size` (default 12). Fill weight: `fill_alpha`. Band strength: alpha in `_draw()` (0.18). Graph height: `custom_minimum_size` set in `main_ui._ready()` (46px).
- Deferred by design (say if you want them): per-event markers on the panel, momentum overlay.

<!-- #529 review items appended as built. -->
