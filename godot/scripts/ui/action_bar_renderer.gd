class_name ActionBarRenderer
extends RefCounted
## CARVE 5 (docs/MAIN_UI_SEAM_MAP.md, seam R1): the ACTION-BAR RENDERING pulled out of the
## main_ui.gd monolith. This is the surface the player touches every turn, so the carve is
## strictly PURE-STRUCTURAL / NON-FORKING: every statement below is a VERBATIM move of the
## rendering that previously lived inline in main_ui (_on_actions_available flat renderer +
## _render_actions_grouped). No visual or gameplay change -- the on-screen bar is byte-identical.
## Ladder stays L2.
##
## What this owns (was inline in the view):
##   * render(actions)            -- the single entry point (was _on_actions_available's body):
##                                   filter locked/hidden ids, group by category, fire the
##                                   strategic-unlock fanfare, then dispatch to a LAYOUT builder.
##   * _render_flat(...)          -- the classic single-column icon-tile grid.
##   * _render_grouped(...)       -- the P9 "proposed" collapsible category sections (was
##                                   _render_actions_grouped).
##   * _build_action_tile(...)    -- builds ONE classic icon tile (look + affordability + wiring).
##   * _build_action_row(...)     -- builds ONE grouped list row.
##   * the render-only constants + new-unlock tracking state (moved verbatim from the view).
##
## VARIANT PLUG POINT (Pip, dev-mode display variants -- built LATER, not now):
##   render() computes the model (categories / order / colors / state) ONCE, then dispatches on
##   `host._ui_layout` to a LAYOUT builder. To add an alternate display variant:
##     1. add a branch in render()'s layout dispatch for the new layout key, calling a new
##        `_render_<variant>(categories, category_order, category_colors, current_state)`;
##     2. reuse or override the per-item builder (`_build_action_tile` / `_build_action_row`) --
##        those are the ONLY places a button's LOOK is decided, so a variant restyles tiles
##        without touching the grouping/affordability/wiring logic in the layout methods.
##   A dev-mode switcher just flips `host._ui_layout` and re-calls render() (the existing
##   _apply_ui_layout path already does exactly this). No new seam surgery required.
##
## What STAYS in the view (main_ui), on purpose -- these are NOT action-bar rendering:
##   * _on_dynamic_action_pressed  -- INPUT: routes queueing through PlanController and submenu
##     opens through SubmenuController (R2/R4/R5, already carved). The tiles/rows wire their
##     `pressed` signal to host._on_dynamic_action_pressed, unchanged.
##   * _on_action_hover / _on_action_unhover (+ _highlight_resources / _reset_resource_highlights)
##     -- the shared InfoBar + top-bar readout presentation. A display variant changes the GRID,
##     not the shared hover surface, so it is deliberately left in the view; tiles wire their
##     mouse signals to host._on_action_hover / host._on_action_unhover, unchanged.
##   * _get_action_by_id / _find_action_button -- thin GameActions / SubmenuChrome delegates
##     consumed by the input + submenu + first-lever-nudge code that stays in the view; the
##     render pass here never calls them, so moving them would only add a back-dependency.
##   * _populate_upgrades / _apply_first_lever_nudge / _show_strategic_unlock_fanfare -- upgrades
##     list, cold-open pulse, and the FanfarePopup (built on the view's tree). render() calls
##     these through host at the SAME points the pre-carve view did.

var host  # MainUI node (untyped: avoids a class_name coupling cycle main_ui <-> renderer)


# --- Render-only config + state (moved verbatim from main_ui) ------------------------------

# P9 proposed-layout category headers: each grouping renders with its accent colour PLUS a real
# navigation icon (was falling through IconLoader.get_action_icon(category_key) -> neon
# placeholder, since a category key is not an action id). Single source for the mapping; loads
# are guarded so a missing file degrades to no-icon, never a crash. (influence/other are
# stand-ins pending #795.)
const CATEGORY_HEADER_ICONS := {
	"hiring": "res://assets/icons/main_navigation/ui_staff_management_64.png",
	"resources": "res://assets/icons/main_navigation/ui_guide_resources_64.png",
	"research": "res://assets/icons/main_navigation/ui_research_tech_64.png",
	"funding": "res://assets/icons/main_navigation/ui_budget_finance_64.png",
	"management": "res://assets/icons/main_navigation/ui_governance_oversight_64.png",
	"influence": "res://assets/icons/main_navigation/ui_guide_objective_64.png",
	"strategic": "res://assets/icons/main_navigation/ui_guide_strategy_64.png",
	"other": "res://assets/icons/main_navigation/ui_guide_book_64.png",
}

# Right-size the promise (hiring rightsize pass): "advertise" currently spawns candidates with a
# RANDOM specialization -- it over-promises a targeted role. Real fix (spawn role-interested
# candidates) is a forking mechanic for a later patch, so grey the button out and label it
# coming-soon everywhere it renders (action bar + hiring submenu) instead of shipping a button
# that lies about what it does.
const COMING_SOON_ACTION_IDS := ["advertise"]
const COMING_SOON_TOOLTIP_SUFFIX := " -- COMING SOON (spawns a random specialization for now; targeted-role hiring is not available yet)"

# "Interview a Candidate" / "Make an Offer" were meant as per-candidate STEPS in the recruitment
# epic, never standalone generic verbs -- the target is chosen at random by the underlying
# no-target menu drivers (interview_next / hire_best), which reads as confusing from the action
# bar. The per-candidate hiring submenu binds Interview/Make Offer to a specific candidate, so
# hide the generic drivers from the action list. The ids stay wired in core.json / actions.gd --
# bots and tests still exercise interview_next/hire_best directly. office_maintenance (v0.13.1):
# charged $5000 and did nothing; taken OFF the board but kept replay-safe in operations.json.
const HIDDEN_FROM_ACTION_BAR_IDS := ["interview_next", "hire_best", "office_maintenance"]

var _seen_unlocked_actions: Dictionary = {}  # #578: action ids seen unlocked, to detect NEW unlocks for fanfare
var _actions_primed: bool = false  # skip fanfare on the very first action population (baseline)


func _init(host_ref) -> void:
	host = host_ref


# --- Single entry point (was main_ui._on_actions_available's body) -------------------------

func render(actions: Array) -> void:
	"""Populate action list with icon buttons in a grid layout. Filters locked/hidden ids, groups
	by category, fires the new-unlock fanfare, then dispatches to the active LAYOUT builder (see
	the VARIANT PLUG POINT note at the top of this file)."""
	print("[MainUI] Populating ", actions.size(), " actions as icon buttons")

	# Clear existing action buttons
	for child in host.actions_list.get_children():
		child.queue_free()

	# Get current state for affordability and unlock checking
	var current_state = host.game_manager.get_game_state()

	# Filter actions by unlock status (Issue #415: Action Discovery)
	var unlocked_count = 0
	var locked_count = 0

	# Group actions by category, filtering out locked actions
	var categories = {}
	var unlocked_ids := {}  # #578: track which ids are unlocked this pass (for new-unlock fanfares)
	for action in actions:
		# Right-size the promise: interview_next/hire_best are no-target menu drivers that pick a
		# candidate at random -- never show them as generic action-bar items, the per-candidate
		# hiring submenu is the correct path (see HIDDEN_FROM_ACTION_BAR_IDS).
		if HIDDEN_FROM_ACTION_BAR_IDS.has(action.get("id", "")):
			continue

		# Check if action is unlocked based on game state
		if not GameActions.is_action_unlocked(action, current_state):
			locked_count += 1
			continue  # Skip locked actions - they won't be shown

		unlocked_count += 1
		unlocked_ids[action.get("id", "")] = true
		var category = action.get("category", "other")
		if not categories.has(category):
			categories[category] = []
		categories[category].append(action)

	if locked_count > 0:
		print("[MainUI] Action Discovery: %d unlocked, %d locked (hidden)" % [unlocked_count, locked_count])

	# #578: momentous-unlock fanfare. When Strategic Moves first becomes available, fade a
	# Civ-style reveal up over the screen instead of the button just silently appearing. This is
	# the ONE wired proof trigger; the same FanfarePopup API can front other unlocks.
	if _actions_primed and unlocked_ids.has("strategic") and not _seen_unlocked_actions.has("strategic"):
		host._show_strategic_unlock_fanfare()
	for id in unlocked_ids:
		_seen_unlocked_actions[id] = true
	_actions_primed = true

	# Define category order. FUNDING LEADS (playtest 2026-08-05: 2 of 2 external players could
	# not find Fundraising): money is the enabling resource -- it buys hires, compute and
	# upgrades -- so the economic opener renders as tile 1 with keyboard badge [1]. The
	# cold-open first-lever nudge is unaffected (it pulses its target by action id, not index).
	var category_order = ["funding", "hiring", "resources", "research", "management", "influence", "strategic", "other"]

	# Define category colors
	var category_colors = {
		"hiring": ThemeManager.get_category_color("hiring"),
		"resources": ThemeManager.get_category_color("resources"),
		"research": ThemeManager.get_category_color("research"),
		"management": ThemeManager.get_category_color("management"),
		"influence": ThemeManager.get_category_color("influence"),
		"strategic": ThemeManager.get_category_color("strategic"),
		"funding": ThemeManager.get_category_color("funding"),
		"other": Color(0.8, 0.8, 0.8)
	}

	# P9 (proposed layout): render the hand GROUPED -- one collapsible category section per the
	# ABBBCCC sketch -- instead of the flat concatenated icon column. Classic falls through to the
	# untouched flat renderer below, so it stays pixel-identical.
	if host._ui_layout == "proposed":
		_render_grouped(categories, category_order, category_colors, current_state)
		host._populate_upgrades()
		return

	_render_flat(categories, category_order, category_colors, current_state)

	# Also populate upgrades
	host._populate_upgrades()

	# #801: re-apply the first-lever pulse each rebuild (buttons are recreated above, so a tween on
	# the old button would dangle). No-op unless the cold-open set the flag.
	host._apply_first_lever_nudge()


# --- LAYOUT: classic single-column icon grid (was inline in _on_actions_available) ---------

func _render_flat(categories: Dictionary, category_order: Array, category_colors: Dictionary, current_state: Dictionary) -> void:
	# WRAPPING icon grid (playtest 2026-08-05 / #1043 item 1). The old single VBox column put
	# ~15 70px tiles (~1,065px) inside a ~550px scroll viewport, with the scrollbar at the FAR
	# RIGHT of the panel, ~470px away from the 70px-wide tile column it scrolls -- an invisible
	# affordance, so 2 of 2 external players never found Fundraising (tile 10, below the fold).
	# An HFlowContainer wraps tiles across the panel's full width (~8 per row at 1080p): the
	# whole turn-1 hand sits above the fold and the dead width beside the column is reclaimed.
	# Keyboard badges keep index order (reading order: left-to-right, top-to-bottom).
	var icon_stack = HFlowContainer.new()
	icon_stack.add_theme_constant_override("h_separation", 2)
	icon_stack.add_theme_constant_override("v_separation", 2)
	host.actions_list.add_child(icon_stack)

	# Create icon buttons - single column layout
	var action_index = 0  # Track index for keyboard shortcuts

	for category_key in category_order:
		if not categories.has(category_key):
			continue

		var category_actions = categories[category_key]
		if category_actions.is_empty():
			continue

		# Create icon buttons for actions in this category
		for action in category_actions:
			var icon_button := _build_action_tile(action, category_key, category_colors, current_state, action_index)
			action_index += 1
			# Add to stack
			icon_stack.add_child(icon_button)


## The hover tooltip for one action tile/row. PLAIN TEXT ONLY -- Godot tooltips render BBCode
## literally, so the info bar's markup (main_ui._on_action_hover) must not be reused here.
##
## Why it carries the description. The hand is 13 uncaptioned pictograms, and the tooltip used to
## repeat only the tile's own name -- which tells a player nothing they cannot already see. Two
## external playtests in a week landed on the same wall: 2026-08-05, "2 of 2 external players
## could not find Fundraising" (see the FUNDING LEADS note in render()); 2026-08-10, Jason, asked
## whether it was apparent what he was meant to do -- "Not yet." The description already rides in
## the action dictionary, so this is a free caption.
func _tooltip_for(action_name: String, action: Dictionary, is_coming_soon: bool) -> String:
	var tip := action_name
	var description := String(action.get("description", "")).strip_edges()
	if description != "":
		tip += "\n" + description
	if is_coming_soon:
		tip += COMING_SOON_TOOLTIP_SUFFIX
	return tip


## VARIANT PLUG POINT: builds ONE classic icon tile. A display variant overrides this to restyle
## the tile without touching _render_flat's grouping/affordability logic. Verbatim from the
## pre-carve inline build.
func _build_action_tile(action: Dictionary, category_key, category_colors: Dictionary, current_state: Dictionary, action_index: int) -> Button:
	var action_id = action.get("id", "")
	var action_name = action.get("name", "Unknown")
	var action_cost = action.get("costs", {})
	var is_coming_soon: bool = COMING_SOON_ACTION_IDS.has(action_id)

	# Create icon-only button (square, fills width)
	var icon_button = Button.new()
	icon_button.custom_minimum_size = Vector2(70, 70)  # square icon tiles
	# #594: hug the 70px icon instead of ballooning across the wide left panel -- this reclaims
	# the empty padding around each icon (and stops expand_icon distorting them). P2/#768: bind to
	# the LEFT (was SHRINK_CENTER) so icons pack against the column edge instead of floating
	# centred with wide side margins (Pip's "white gaps" complaint).
	icon_button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	icon_button.focus_mode = Control.FOCUS_NONE

	# Get icon texture
	var icon_texture = IconLoader.get_action_icon(action_id)
	if icon_texture:
		icon_button.icon = icon_texture
		icon_button.expand_icon = true
		icon_button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER

	# Add keyboard shortcut number badge (prominent for discoverability), unless the button is
	# coming-soon -- badge that slot with "SOON" instead so the greyed-out state is visible without
	# hovering for the tooltip.
	if is_coming_soon:
		icon_button.text = "SOON"
		icon_button.add_theme_font_size_override("font_size", 10)
		icon_button.add_theme_color_override("font_color", Color(0.85, 0.85, 0.85, 1))
		icon_button.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
		icon_button.add_theme_constant_override("outline_size", 2)
	elif action_index < 9:
		icon_button.text = str(action_index + 1)
		icon_button.add_theme_font_size_override("font_size", 14)  # Increased from 9
		icon_button.add_theme_color_override("font_color", Color(1, 1, 1, 1))  # Full opacity
		icon_button.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
		icon_button.add_theme_constant_override("outline_size", 2)

	# Check if player can afford this action
	var can_afford = true
	var missing_resources = []

	for resource in action_cost.keys():
		var cost = action_cost[resource]
		var available = current_state.get(resource, 0)

		if available < cost:
			can_afford = false
			missing_resources.append("%s (need %s, have %s)" % [resource, cost, available])

	# Style based on affordability and category. Coming-soon always wins: it's disabled regardless
	# of whether the player could otherwise afford it.
	if is_coming_soon:
		icon_button.disabled = true
		icon_button.modulate = Color(0.35, 0.35, 0.35)  # Darker gray than plain unaffordable
	elif not can_afford:
		icon_button.disabled = true
		icon_button.modulate = Color(0.4, 0.4, 0.4)  # Dark gray for unaffordable
	else:
		# Apply category color tint
		var button_color = category_colors.get(category_key, Color(1.0, 1.0, 1.0))
		icon_button.modulate = Color(0.9, 0.9, 0.9).lerp(button_color, 0.4)

	icon_button.tooltip_text = _tooltip_for(action_name, action, is_coming_soon)

	# Tag with action_id so submenus can align to the button that opened them (#510)
	icon_button.set_meta("action_id", action_id)

	# Connect button press
	icon_button.pressed.connect(func(): host._on_dynamic_action_pressed(action_id, action_name))

	# Connect mouse hover for info bar
	icon_button.mouse_entered.connect(func(): host._on_action_hover(action, can_afford, missing_resources))
	icon_button.mouse_exited.connect(func(): host._on_action_unhover())

	return icon_button


# --- LAYOUT: P9 grouped collapsible sections (was _render_actions_grouped) ------------------

func _render_grouped(categories: Dictionary, category_order: Array, category_colors: Dictionary, current_state: Dictionary) -> void:
	"""P9 grouped hand (proposed layout only): each category is one A-header that expands/collapses
	a B-list of its actions -- Pip's ABBBCCC sketch as inline collapsible sections. Fewer top-level
	entries, real grouping, hiring folded into its own category (fixes D3/D4). The C context stays
	the shared InfoBar on hover. VIEW-only: same press/hover handlers as the flat renderer."""
	var stack := VBoxContainer.new()
	stack.add_theme_constant_override("separation", 3)
	stack.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	host.actions_list.add_child(stack)

	var display_names := {
		"hiring": "Hiring", "resources": "Resources", "research": "Research",
		"funding": "Funding", "management": "Management", "influence": "Influence",
		"strategic": "Strategic", "other": "Other",
	}

	for category_key in category_order:
		if not categories.has(category_key):
			continue
		var category_actions: Array = categories[category_key]
		if category_actions.is_empty():
			continue
		var accent: Color = category_colors.get(category_key, Color(0.8, 0.8, 0.8))
		var label_name: String = display_names.get(category_key, String(category_key).capitalize())

		# B-list built first so the header's toggle closure can capture it.
		var blist := VBoxContainer.new()
		blist.add_theme_constant_override("separation", 1)
		blist.size_flags_horizontal = Control.SIZE_EXPAND_FILL

		# A-header: category name + count, toggles the B-list open/closed.
		var header := Button.new()
		header.toggle_mode = true
		header.button_pressed = true
		header.focus_mode = Control.FOCUS_NONE
		header.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		header.alignment = HORIZONTAL_ALIGNMENT_LEFT
		# Category header icon: pull the mapped navigation icon (not IconLoader, which keys on
		# action ids and returned the neon placeholder for a category key). Guard the load so a
		# missing asset degrades to an icon-less (but still colour-coded) header, never a crash.
		var cat_icon_path: String = CATEGORY_HEADER_ICONS.get(category_key, "")
		if cat_icon_path != "" and ResourceLoader.exists(cat_icon_path):
			var cat_icon := load(cat_icon_path) as Texture2D
			if cat_icon:
				header.icon = cat_icon
		header.text = "v %s (%d)" % [label_name, category_actions.size()]
		header.add_theme_color_override("font_color", accent)
		header.tooltip_text = "Show / hide %s actions" % label_name
		header.toggled.connect(func(on: bool):
			blist.visible = on
			header.text = "%s %s (%d)" % ["v" if on else ">", label_name, category_actions.size()])
		stack.add_child(header)
		stack.add_child(blist)

		for action in category_actions:
			var row := _build_action_row(action, accent, current_state)
			blist.add_child(row)


## VARIANT PLUG POINT: builds ONE grouped list row. A display variant overrides this to restyle
## the row without touching _render_grouped's section/header/affordability logic. Verbatim from
## the pre-carve inline build.
func _build_action_row(action: Dictionary, accent: Color, current_state: Dictionary) -> Button:
	var action_id: String = action.get("id", "")
	var action_name: String = action.get("name", "Unknown")
	var action_cost: Dictionary = action.get("costs", {})
	var is_coming_soon: bool = COMING_SOON_ACTION_IDS.has(action_id)

	# Affordability -- same rule as the flat renderer.
	var can_afford := true
	var missing_resources := []
	for resource in action_cost.keys():
		var cost = action_cost[resource]
		var available = current_state.get(resource, 0)
		if available < cost:
			can_afford = false
			missing_resources.append("%s (need %s, have %s)" % [resource, cost, available])

	var row := Button.new()
	row.focus_mode = Control.FOCUS_NONE
	row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.alignment = HORIZONTAL_ALIGNMENT_LEFT
	row.clip_text = true
	row.text = ("  " + action_name + " [SOON]") if is_coming_soon else ("  " + action_name)
	var icon_texture := IconLoader.get_action_icon(action_id)
	if icon_texture:
		row.icon = icon_texture
	row.set_meta("action_id", action_id)  # submenu alignment (#510) + button lookup
	# Coming-soon always wins: disabled regardless of affordability (see FIRST_LEVER block in the
	# view for the "advertise" over-promise this right-sizes).
	if is_coming_soon:
		row.disabled = true
		row.modulate = Color(0.35, 0.35, 0.35)
	elif not can_afford:
		row.disabled = true
		row.modulate = Color(0.4, 0.4, 0.4)
	else:
		row.modulate = Color(0.9, 0.9, 0.9).lerp(accent, 0.4)
	row.tooltip_text = _tooltip_for(action_name, action, is_coming_soon)
	row.pressed.connect(func(): host._on_dynamic_action_pressed(action_id, action_name))
	row.mouse_entered.connect(func(): host._on_action_hover(action, can_afford, missing_resources))
	row.mouse_exited.connect(func(): host._on_action_unhover())
	return row
