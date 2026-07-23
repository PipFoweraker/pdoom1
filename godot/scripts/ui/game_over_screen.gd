extends Control
class_name GameOverScreen
## Game Over screen showing final stats and offering replay options

@onready var panel_container = $CenterContainer/PanelContainer
@onready var title_label = $CenterContainer/PanelContainer/MarginContainer/VBox/TitleLabel
@onready var subtitle_label = $CenterContainer/PanelContainer/MarginContainer/VBox/SubtitleLabel
@onready var stats_label = $CenterContainer/PanelContainer/MarginContainer/VBox/StatsLabel
@onready var copy_result_button = $CenterContainer/PanelContainer/MarginContainer/VBox/ButtonsHBox/CopyResultButton

var game_manager: Node
var final_turns: int = 0
var final_doom_integral: int = 0
# Issue #734: values captured for the "Copy result" share line (clipboard only, no network).
var final_doom: float = 0.0
var final_seed: String = ""
var baseline_turns: int = 0
var baseline_doom_integral: int = 0
var baseline_result: Dictionary = {}
var leaderboard_entry_uuid: String = ""
var game_start_time: float = 0.0
var sync_status_label: Label = null  # Tiny non-blocking remote-sync status blip
var attribution_label: RichTextLabel = null  # EE-8 cause-of-death chain, above the stats scroll
# Re-entrancy guard: the game-over signal fires on EVERY state update (incl. leftover
# day-ticks in a month playback), so show_game_over() can be called many times. The
# scoring side-effects (local save + remote POST + music) must run EXACTLY ONCE; later
# calls only keep the overlay visible.
var _game_over_shown: bool = false

func _ready():
	# Initially hidden
	visible = false

	# Delineate the end-game box with a solid panel + border so it reads clearly as an
	# overlay rather than blending into the dimmed game behind it (playtest: screen4).
	# Palette-sourced (#743): deep-aubergine dread ground + dimmed cozy-amber frame,
	# matching the menu_theme.tres modal register (pause/player-guide panels).
	if panel_container:
		var box := StyleBoxFlat.new()
		box.bg_color = Color(0.09, 0.04, 0.11, 0.98)
		box.set_border_width_all(3)
		box.border_color = Color(0.91, 0.64, 0.24, 0.8)
		box.set_corner_radius_all(10)
		box.set_content_margin_all(6)
		panel_container.add_theme_stylebox_override("panel", box)

	# Enable input processing for ENTER key
	set_process_input(true)

	# Connect URL click handler for AI safety links
	if stats_label:
		stats_label.meta_clicked.connect(_on_meta_clicked)

func _input(event: InputEvent):
	"""Handle keyboard shortcuts - ENTER to continue to leaderboard"""
	if not visible:
		return  # Only process input when visible

	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ENTER or event.keycode == KEY_SPACE:
			# Navigation goes through SceneTransition, which always defers the scene swap,
			# so it is safe to invoke directly from inside _input().
			get_viewport().set_input_as_handled()
			_continue_to_leaderboard()

func show_game_over(is_victory: bool, final_state: Dictionary):
	"""Display game over screen with final statistics.

	ISOLATION CONTRACT (fix/endgame-quit-score-post -- release blocker). This is the view
	layer at the defeat transition; the live remote leaderboard turned it into a place where
	a bug loses scores. The rules this method now enforces:
	  1. RE-ENTRANCY: the game-over signal fires on every state update (incl. leftover
	     day-ticks in a month playback), so run the scoring side-effects EXACTLY ONCE.
	  2. SCORE FIRST: persist + submit the score BEFORE any heavy/optional work, so a hang,
	     force-quit, or later error can't lose it. The submit was previously the LAST step,
	     after a multi-second synchronous baseline sim -- a force-quit during that freeze
	     meant the POST was never even dispatched (root cause of the live score loss).
	  3. NEVER BLOCK: read the baseline NON-BLOCKING (get_baseline_score() ran a ~4s
		 synchronous simulation on the main thread -> "Not Responding" at the defeat moment).
	  4. NEVER CRASH: music / save / submit are all failure-tolerant side-effects.
	"""
	# Rule 1 -- re-entrancy guard. Later calls only keep the overlay visible.
	if _game_over_shown:
		visible = true
		return
	_game_over_shown = true

	visible = true

	# Play appropriate end-game music (MusicManager already no-ops a missing/failed track).
	if is_victory:
		# Victory music not yet implemented, keep gameplay music
		pass
	else:
		MusicManager.play_context(MusicManager.MusicContext.DEFEAT)

	# ADR-0002: the engine is the scoring authority -- read the (turns, doom_integral)
	# tuple straight off final_state; no formula here.
	var st = GameState.score_tuple(final_state)
	final_turns = st[0]
	final_doom_integral = st[1]
	print("[GameOverScreen] Final score: %s" % GameState.format_score(final_turns, final_doom_integral))

	var game_seed = GameConfig.get_display_seed()

	# Issue #734: stash the seed + final doom so the "Copy result" button can build the
	# shareable one-liner after the async work below. final_turns is already set above.
	final_seed = game_seed
	final_doom = final_state.get("doom", 0.0)

	# Rule 3 -- baseline comparison (Issue #372), NON-BLOCKING. If the background sim isn't
	# ready yet we skip the comparison rather than freeze the defeat screen computing it.
	# baseline_turns == 0 is exactly what the stats block already treats as "no baseline".
	baseline_result = BaselineSimulator.get_baseline_score_if_ready(game_seed)
	baseline_turns = int(baseline_result.get("turns", 0))
	baseline_doom_integral = int(round(baseline_result.get("doom_integral", 0.0)))
	if baseline_turns > 0:
		print("[GameOverScreen] Baseline: %s" % GameState.format_score(baseline_turns, baseline_doom_integral))
	else:
		print("[GameOverScreen] Baseline not ready -- skipping comparison (defeat screen must not block).")

	# Rule 2 -- SCORE FIRST. Persist locally + fire the async remote POST immediately, before
	# the verification export and stats rendering below.
	_persist_and_submit_score(final_state, game_seed)

	# Verification export (decorative here -- a future dispute artifact). Cheap; kept AFTER
	# the durable save so nothing scoring-critical depends on it.
	VerificationTracker.stop_tracking()
	var final_hash = VerificationTracker.get_final_hash()
	var verification_data = VerificationTracker.export_for_submission(final_state)
	verification_data["turns_survived"] = final_turns  # ADR-0002 score tuple
	verification_data["doom_integral"] = final_doom_integral
	print("[GameOverScreen] Game ended - Verification hash: %s..." % final_hash.substr(0, 16))

	# Set title and colors based on outcome
	if is_victory:
		title_label.text = "VICTORY!"
		title_label.add_theme_color_override("font_color", Color(0.2, 1.0, 0.2))  # Green
		subtitle_label.text = "Humanity Survived the AI Revolution"
		subtitle_label.add_theme_color_override("font_color", Color(0.6, 1.0, 0.6))
	else:
		title_label.text = "DEFEAT"
		title_label.add_theme_color_override("font_color", Color(1.0, 0.2, 0.2))  # Red
		# P0 (playtest 2026-07-17): the subtitle used to hardcode "The AI Destroyed Humanity"
		# even when the run actually died of rep-collapse (doom was only 50). Title the defeat
		# by its ACTUAL death cause so the headline never lies about what killed you.
		subtitle_label.text = _get_defeat_title(final_state)
		subtitle_label.add_theme_color_override("font_color", Color(1.0, 0.6, 0.6))
		# EE-8: the turn-stamped causal chain (DeathAttribution), named + prominent, above
		# the stats scroll. Names the killer lab when the doom death was overhang-driven.
		_render_death_attribution()

	# Build statistics display
	var stats_text = "[center][b]FINAL STATISTICS[/b][/center]\n\n"

	# Final Score (prominent display)
	stats_text += "[center][color=gold]* FINAL SCORE *[/color][/center]\n"
	stats_text += "[center][b][color=yellow]%s[/color][/b][/center]\n" % GameState.format_score(final_turns, final_doom_integral)

	# Baseline comparison (Issue #372)
	if baseline_turns > 0:
		var comparison = BaselineSimulator.get_comparison_text(final_turns, final_doom_integral, baseline_turns, baseline_doom_integral)
		var comparison_color = comparison["color"].to_html(false)
		stats_text += "[center][color=%s]%s[/color][/center]\n" % [comparison_color, comparison["text"]]
		stats_text += "[center][color=gray](Baseline: %s with no actions)[/color][/center]\n\n" % GameState.format_score(baseline_turns, baseline_doom_integral)
	else:
		stats_text += "\n"

	# Game duration
	var turn = final_state.get("turn", 0)
	stats_text += "[color=cyan]* Turns Survived:[/color] [b]%d[/b]\n\n" % turn

	# Doom level
	var doom = final_state.get("doom", 0)
	var doom_color = _get_doom_display_color(doom)
	stats_text += "[color=cyan]* Final Doom:[/color] [color=%s][b]%.1f%%[/b][/color]\n" % [doom_color, doom]

	# Doom momentum
	var doom_momentum = final_state.get("doom_momentum", 0.0)
	if abs(doom_momentum) > 0.1:
		var momentum_text = "^ %.1f (Spiral)" % doom_momentum if doom_momentum > 0 else "v %.1f (Flywheel)" % abs(doom_momentum)
		var momentum_color = "red" if doom_momentum > 0 else "green"
		stats_text += "[color=cyan]  `- Momentum:[/color] [color=%s]%s[/color]\n" % [momentum_color, momentum_text]

	stats_text += "\n"

	# Resources accumulated
	stats_text += "[color=cyan]* Resources:[/color]\n"
	stats_text += "  [color=gold]Money:[/color] $%d\n" % final_state.get("money", 0)
	stats_text += "  [color=blue]Compute:[/color] %.1f\n" % final_state.get("compute", 0)
	stats_text += "  [color=purple]Research:[/color] %.1f\n" % final_state.get("research", 0)
	stats_text += "  [color=white]Papers:[/color] %d\n" % final_state.get("papers", 0)
	stats_text += "  [color=orange]Reputation:[/color] %.0f\n\n" % final_state.get("reputation", 0)

	# Team composition -- count via GameState.get_total_staff() (L0 #620: the legacy
	# field sum below missed the researchers[] roster, showing 0 employees mid-era).
	var safety = final_state.get("safety_researchers", 0)
	var capability = final_state.get("capability_researchers", 0)
	var compute_eng = final_state.get("compute_engineers", 0)
	var total_staff = safety + capability + compute_eng
	if GameManager.is_initialized and GameManager.state:
		total_staff = GameManager.state.get_total_staff()

	stats_text += "[color=cyan]* Team:[/color] [b]%d employees[/b]\n" % total_staff
	if total_staff > 0:
		stats_text += "  [color=green]Safety Researchers:[/color] %d\n" % safety
		stats_text += "  [color=red]Capability Researchers:[/color] %d\n" % capability
		stats_text += "  [color=blue]Compute Engineers:[/color] %d\n" % compute_eng

	# Upgrades purchased
	var upgrades = final_state.get("purchased_upgrades", [])
	if upgrades.size() > 0:
		stats_text += "\n[color=cyan]* Upgrades:[/color] [b]%d purchased[/b]\n" % upgrades.size()

	# L8 achievements (#619): recognition only, never score (ADR-0002 anti-sink).
	var achievements_node = get_node_or_null("/root/Achievements")
	if achievements_node and not achievements_node.unlocked_this_run.is_empty():
		stats_text += "\n[color=cyan]* Achievements this run:[/color]\n"
		for ach_id in achievements_node.unlocked_this_run:
			var ach_def = achievements_node.get_definition(ach_id)
			if not ach_def.is_empty():
				stats_text += "  [color=gold]* %s[/color] [color=gray]-- %s[/color]\n" % [ach_def["title"], ach_def["flavor"]]

	# Victory/defeat flavor text
	stats_text += "\n[center][color=gray]-------------------[/color][/center]\n"
	if is_victory:
		stats_text += "\n[center][color=lime]Your leadership guided humanity safely through\nthe development of transformative AI.[/color][/center]"
	else:
		var reason = _get_defeat_reason(final_state)
		stats_text += "\n[center][color=red]%s[/color][/center]" % reason
		var attribution = _get_ledger_attribution_text(final_state)
		if attribution != "":
			stats_text += "\n[center][color=orange]%s[/color][/center]" % attribution

	# AI Safety resources call to action (condensed to reduce vertical overflow)
	stats_text += "\n[center][color=gray]-------------------[/color][/center]\n"
	stats_text += "[center][color=cyan]Learn about real AI safety: [url=https://aisafety.info][color=dodger_blue]aisafety.info[/color][/url][/color][/center]\n"
	stats_text += "[center][color=gold][b]> Press ENTER for Leaderboard[/b][/color][/center]"

	stats_label.text = stats_text

func _persist_and_submit_score(final_state: Dictionary, game_seed: String) -> void:
	"""SCORE FIRST (isolation contract, rule 2): save the run's score to the LOCAL board and
	fire the async remote POST. Runs before the verification export + stats rendering so the
	score is durable the instant the defeat screen appears -- a later hang / force-quit /
	error cannot lose it. The remote POST is fire-and-forget on the LeaderboardSync autoload
	(lifecycle-independent from this screen) and internally bulletproof against network
	failure, so nothing here can crash or freeze the end-game."""
	var duration = Time.get_ticks_msec() / 1000.0 - game_start_time
	var entry = Leaderboard.ScoreEntry.new(
		final_turns,
		GameConfig.lab_name,
		final_state.get("turn", 0),
		"v" + GameConfig.CURRENT_VERSION,  # Game version from GameConfig
		duration,
		baseline_turns,  # Baseline turns for comparison (Issue #372); 0 when not ready
		final_doom_integral,  # ADR-0002 tiebreak
		baseline_doom_integral
	)

	# ---- local save (authoritative: the score must exist locally regardless of network) --
	# BOARD KEY: the ladder epoch (build-vs-ladder split) -- a cosmetic build bump
	# must land scores on the SAME board file. Entry.game_mode above keeps the build
	# string for provenance.
	var leaderboard = Leaderboard.new(game_seed, GameConfig.get_board_version())
	var result: Dictionary = leaderboard.add_score(entry)
	leaderboard_entry_uuid = entry.entry_uuid
	GameConfig.latest_leaderboard_entry = leaderboard_entry_uuid  # for leaderboard highlight
	print("[GameOverScreen] Score saved locally - Rank: %d" % int(result.get("rank", -1)))

	# ---- remote submit (async; failure just leaves the score local + queued for retry) ----
	_maybe_submit_remote(entry, game_seed)

func _maybe_submit_remote(entry, game_seed: String) -> void:
	"""Upload the just-saved score to the global board, if sync is on. Never blocks;
	shows a tiny status blip that resolves async via submit_completed."""
	if not LeaderboardSync.should_submit():
		return
	_ensure_sync_status_label()
	sync_status_label.visible = true
	sync_status_label.text = "Global leaderboard: submitting..."
	sync_status_label.add_theme_color_override("font_color", Color(0.7, 0.8, 0.9))
	if not LeaderboardSync.submit_completed.is_connected(_on_sync_submit_completed):
		LeaderboardSync.submit_completed.connect(_on_sync_submit_completed)
	# BOARD KEY: remote board is scoped by the ladder epoch too. BACKEND TASK (flagged,
	# not attempted here): api.pdoom1.com's score API must key by ladder_version and
	# alias the live v0.12.0 board to L1 -- see GameConfig.get_board_version() docs.
	LeaderboardSync.submit_score(entry, game_seed, GameConfig.get_board_version())

func _on_sync_submit_completed(success: bool, _added: bool, _rank: int, message: String) -> void:
	"""Resolve the status blip. Failure is silent-ish: score is already saved locally."""
	if not is_instance_valid(sync_status_label):
		return
	if message == "":
		message = "saved locally"
	sync_status_label.text = "Global leaderboard: %s" % message
	var col := Color(0.6, 1.0, 0.6) if success else Color(0.85, 0.8, 0.55)
	sync_status_label.add_theme_color_override("font_color", col)

func _ensure_sync_status_label() -> void:
	if is_instance_valid(sync_status_label):
		return
	sync_status_label = Label.new()
	sync_status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sync_status_label.add_theme_font_size_override("font_size", 12)
	var parent: Node = stats_label.get_parent() if stats_label else self
	parent.add_child(sync_status_label)

func _get_doom_display_color(doom: float) -> String:
	"""BBCode colour for the final-doom stat -- ThemeManager's doom ramp, stroke variant
	so it stays legible on the dark panel (L6 unification: was a divergent 30/60/80
	green/yellow/orange/red copy)."""
	return "#" + ThemeManager.get_doom_stroke_color(doom).to_html(false)

func _get_defeat_title(final_state: Dictionary) -> String:
	"""Short honest defeat headline, keyed to the ACTUAL death cause (P0 fix).
	Order mirrors GameState.check_win_lose(): doom >= 100, then reputation <= 0, then the
	bankruptcy fallback -- so the subtitle always names the counter that ended the run."""
	var doom = final_state.get("doom", 0)
	var reputation = final_state.get("reputation", 100)

	if doom >= 100.0:
		return "The AI Destroyed Humanity"
	elif reputation <= 0.0:
		return "You Lost All Credibility"
	elif final_state.get("money", 0) < 0:
		return "The Lab Went Bankrupt"
	else:
		return "The Experiment Ended"

func _get_defeat_reason(final_state: Dictionary) -> String:
	"""Generate defeat reason based on final state.
	Order mirrors GameState.check_win_lose(): doom >= 100, then reputation <= 0."""
	var doom = final_state.get("doom", 0)
	var reputation = final_state.get("reputation", 100)

	if doom >= 100.0:
		return "Doom reached 100%. The AI became\nunaligned and humanity was lost."
	elif reputation <= 0.0:
		return "Your lab lost all credibility --\nreputation hit zero and the doors closed."
	elif final_state.get("money", 0) < 0:
		return "Your organization went bankrupt before\nthe mission could be completed."
	else:
		return "The experiment ended prematurely."

func _fmt_money(amount: float) -> String:
	"""Money display -- routes through the ONE formatter (L0 #620: was a duplicate
	compact implementation; GameConfig.format_money is the canonical one)."""
	return GameConfig.format_money(amount)

## EE-8 (ADR-0012): render DeathAttribution's turn-stamped causal chain prominently above the
## stats scroll, so the defeat screen tells the player HOW they lost in concrete named causes.
## READ-ONLY: reads the finished GameManager.state, never mutates. No-op (hidden) when there is
## no live state or no attribution data (e.g. a bare test harness / empty cause_log).
func _render_death_attribution() -> void:
	var bbcode := _build_death_attribution_bbcode()
	if bbcode == "":
		return
	if not is_instance_valid(attribution_label):
		attribution_label = RichTextLabel.new()
		attribution_label.bbcode_enabled = true
		attribution_label.fit_content = true
		attribution_label.scroll_active = false
		var parent: Node = stats_label.get_parent() if stats_label else self
		parent.add_child(attribution_label)
		# Sit directly above the stats scroll (StatsLabel), below the subtitle.
		if stats_label:
			parent.move_child(attribution_label, stats_label.get_index())
	attribution_label.text = bbcode
	attribution_label.visible = true

## Build the cause-of-death BBCode from the live finished state. Empty when unavailable.
func _build_death_attribution_bbcode() -> String:
	if not (GameManager.is_initialized and GameManager.state):
		return ""
	var st = GameManager.state
	var result: Dictionary = DeathAttribution.classify(st)
	var chain: Array = result.get("chain", [])
	var surface := str(result.get("surface", ""))
	var dominant := ""
	if st.doom_system:
		dominant = st.doom_system.get_dominant_stream()
	var killer := overhang_killer_line(surface, dominant, st.frontier_capability, _rival_dicts(st))
	return build_attribution_bbcode(chain, killer)

## Serialize the live rival labs to dicts so the shared DoomBreakdown name-masking (which reads
## the save-shaped rival dicts) can resolve visibility identically on the defeat screen.
func _rival_dicts(st) -> Array:
	var out: Array = []
	if st and st.rival_labs is Array:
		for rival in st.rival_labs:
			out.append(rival.to_dict())
	return out

## When the run died of doom AND the overhang stream was the dominant contributor, name the top
## visible frontier holder as the killer. Deadpan bureaucratic register (achievements.gd tone).
## Empty string when the death was not overhang-driven or no frontier holder is identifiable.
static func overhang_killer_line(surface: String, dominant_stream: String, frontier_capability, rival_labs) -> String:
	if surface != "doom":
		return ""
	if dominant_stream != "overhang":
		return ""
	var leaders := DoomBreakdown.frontier_leaders(frontier_capability, rival_labs)
	if leaders.is_empty():
		return ""
	var top: Dictionary = leaders[0]
	if str(top.get("id", "")) == "player":
		return "Your own frontier outran your absorption. The paperwork was filed on time."
	return "%s's frontier outran your absorption. The paperwork was filed on time." % str(top.get("name", "an unknown actor"))

## Compose the cause-of-death panel BBCode from a causal chain + optional named-killer line.
## Empty string when there is nothing to show. Pure -- unit-tested.
static func build_attribution_bbcode(chain: Array, killer_line: String) -> String:
	var has_chain: bool = chain != null and not chain.is_empty()
	if not has_chain and killer_line == "":
		return ""
	var out := "[center][b]CAUSE OF DEATH[/b][/center]\n"
	if killer_line != "":
		out += "[center][color=orange]%s[/color][/center]\n" % killer_line
	if has_chain:
		out += "[color=gray]"
		for line in chain:
			out += "  " + str(line) + "\n"
		out += "[/color]"
	return out

func _get_ledger_attribution_text(final_state: Dictionary) -> String:
	"""Surface the ledger death_attribution already in state, so the player learns what
	killed them. Returns '' when there's no ledger attribution."""
	var ledger = final_state.get("ledger", {})
	var attribution = ledger.get("death_attribution", [])
	if attribution == null or attribution.is_empty():
		return ""
	var total := 0.0
	var counts := {}
	for entry in attribution:
		var src := str(entry.get("source", "debt"))
		total += float(entry.get("magnitude", 0.0))
		counts[src] = int(counts.get(src, 0)) + 1
	var parts := []
	for src in counts:
		parts.append("%d %s" % [counts[src], src])
	return "Your ledger came due: %s -- %s in bills you couldn't cover." % [", ".join(parts), _fmt_money(total)]

## Issue #734: build the single shareable result line. Pure + static so it can be unit-tested
## without instantiating the screen. ASCII only ("--" for the dash); clipboard only, no network.
static func format_share_line(months: int, doom: float, seed: String, version: String) -> String:
	return "I survived %d months at %d%% doom on seed %s -- P(Doom)1 v%s" % [months, int(round(doom)), seed, version]

func _on_copy_result_pressed() -> void:
	"""Copy a single shareable result line to the system clipboard (no network, no leaderboard)."""
	var line := format_share_line(final_turns, final_doom, final_seed, GameConfig.CURRENT_VERSION)
	DisplayServer.clipboard_set(line)
	print("[GameOverScreen] Copied result to clipboard: %s" % line)
	if is_instance_valid(copy_result_button):
		copy_result_button.text = "Copied to clipboard"

func _on_play_again_pressed():
	"""Restart the game"""
	print("[GameOverScreen] Play Again pressed")
	# Reload the main scene to restart
	SceneTransition.reload()

func _on_main_menu_pressed():
	"""Return to main menu"""
	print("[GameOverScreen] Main Menu pressed")
	SceneTransition.go_to("res://scenes/welcome.tscn")

func _on_meta_clicked(meta):
	"""Handle URL clicks in the stats label"""
	print("[GameOverScreen] Opening URL: %s" % meta)
	OS.shell_open(str(meta))

func _continue_to_leaderboard():
	"""Navigate to leaderboard screen to show saved score.

	Navigation goes through SceneTransition, which always defers the scene swap,
	so this is safe to reach from an _input handler or a Button `pressed` signal.
	"""
	print("[GameOverScreen] Transitioning to leaderboard")
	SceneTransition.go_to("res://scenes/leaderboard_screen.tscn")
