extends Control
class_name GameOverScreen
## Game Over screen showing final stats and offering replay options

## PALETTE (Pip, v0.14.0 playtest: "old colour schemes"). This screen was written in
## Godot's named web primaries -- pure #00FFFF cyan, #FFFF00 yellow, #0000FF blue,
## #00FF00 lime -- which predate the command-center palette in UI_STYLE_GUIDE.md and
## belong to no theme the game currently ships. Three were also unreadable on this
## panel's Color(0.09, 0.04, 0.11) ground; the contrast ratios are in theme_manager.gd
## beside RESOURCE_COLORS and are pinned by test_game_over_is_readable.gd.
##
## Resource/staff hues live in ThemeManager (shared, const). The four below are local
## because they are this screen's own register and nothing else uses them.
const _C_LABEL := Color(0.42, 0.85, 0.82)      # section labels; was [color=cyan] #00FFFF
const _C_SCORE_LABEL := Color(0.95, 0.80, 0.35)  # "* FINAL SCORE *"; was [color=gold]
const _C_SCORE := Color(1.00, 0.93, 0.55)      # the number itself; was [color=yellow] #FFFF00
const _C_DIM := Color(0.62, 0.66, 0.72)        # parentheticals + rules; was [color=gray]
const _C_VICTORY := Color(0.50, 0.90, 0.55)    # was [color=lime] #00FF00
const _C_DEFEAT := Color(0.95, 0.45, 0.40)     # cause of death; was [color=red] #FF0000
const _C_LINK := Color(0.45, 0.72, 1.00)       # was [color=dodger_blue]

## Achievements printed in full before "(+N more)". See the achievements block below:
## this is the only cap standing between a good run and an unbounded panel.
const ACHIEVEMENT_LINE_CAP := 3

static func _hex(c: Color) -> String:
	"""BBCode needs an rrggbb string, and Color.to_html(false) is the only conversion
	used on this screen so a colour can never be spelled two ways."""
	return c.to_html(false)

# What the identity prompt is allowed to promise. The prompt collects an
# Operator name AND a Lab name, and BOTH are published: the remote board's
# frozen contract carries one string, and `ScoreEntry.to_wire_dict()` composes
# both names into it as `LAB -- OPERATOR` (see `Leaderboard.compose_board_name`,
# godot/scripts/leaderboard.gd:32 and :196). A separate `operator_name` key is
# not sent because the server drops unknown keys via $ALLOWED_FIELDS (measured
# 2026-08-10) -- that is a wire-shape detail, NOT a limit on what goes public.
# So the prompt must say both names go public, and it does.
const IDENTITY_PROMPT_BOARD_NOTE := "The global board shows both, as 'Lab -- Operator'. One Operator can run many labs, and lab names collide, so the Operator name is what tells two identical labs apart. Long names are shortened with '...' to fit the board."

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
	# ADR-0002: THERE IS NO VICTORY CONDITION. `GameState.victory` is initialised false and
	# is never assigned true anywhere in the engine (check_win_lose sets it false on both
	# death routes; test_game_state.test_check_win_lose_doom_zero_no_victory pins doom<=0 as
	# a non-ending). This branch is therefore unreachable, but it used to headline "VICTORY!
	# / Humanity Survived the AI Revolution" -- the third surface disagreeing with the menu's
	# "You can't win. You can only buy time." Copy is now consistent whichever way it goes;
	# deleting the branch outright is a code change for issue #809 to make, not a copy fix.
	if is_victory:
		title_label.text = "RUN ENDED"
		title_label.add_theme_color_override("font_color", Color(0.2, 1.0, 0.2))  # Green
		subtitle_label.text = "You bought humanity more time"
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

	# Build statistics display.
	#
	# A DEATH SCREEN IS A MOMENT, NOT A DOCUMENT (Pip's v0.14.0 playtest, 2026-08-07:
	# "really hard to read and still involves scrolling"). Measured on the failing
	# build at 1920x1080: 31 lines / 713px of content inside a 720x300 box, i.e. 14
	# lines visible and 413px unreachable without scrolling -- and the LAST line was
	# "> Press ENTER for Leaderboard", which is why he never found the board.
	#
	# So the ledger rows collapsed into single lines rather than one line per field.
	# The information is all still here; it just stopped costing a line each. The
	# navigation left the document entirely and became a real button (LeaderboardButton
	# in ButtonsHBox) -- a way OUT of a scrolling region must never live INSIDE it.
	#
	# "FINAL STATISTICS" is gone as a header: the panel already says GAME OVER in 48pt
	# with the cause of death under it, so the header was a label for a thing the
	# player is already looking at.
	var stats_text = ""

	# Final Score (prominent display)
	stats_text += "[center][color=%s]* FINAL SCORE *[/color][/center]\n" % _hex(_C_SCORE_LABEL)
	stats_text += "[center][b][color=%s]%s[/color][/b][/center]\n" % [_hex(_C_SCORE), GameState.format_score(final_turns, final_doom_integral)]

	# Baseline comparison (Issue #372)
	if baseline_turns > 0:
		var comparison = BaselineSimulator.get_comparison_text(final_turns, final_doom_integral, baseline_turns, baseline_doom_integral)
		var comparison_color = comparison["color"].to_html(false)
		stats_text += "[center][color=%s]%s[/color][/center]\n" % [comparison_color, comparison["text"]]
		# Was its own line ("(Baseline: X with no actions)"). Folded into the comparison
		# it qualifies -- a parenthetical does not need a line of its own on a screen
		# that had 413px of unreachable content.
		stats_text += "[center][color=%s](vs %s doing nothing)[/color][/center]\n" % [
			_hex(_C_DIM), GameState.format_score(baseline_turns, baseline_doom_integral)]
	stats_text += "\n"

	# Survival + doom on ONE row each, and momentum folded into the doom row rather
	# than hanging under it as a `- continuation.
	var turn = final_state.get("turn", 0)
	var doom = final_state.get("doom", 0)
	var doom_color = _get_doom_display_color(doom)
	stats_text += "[color=%s]* Survived:[/color] [b]%d months[/b]\n" % [_hex(_C_LABEL), turn]
	var doom_row := "[color=%s]* Final Doom:[/color] [color=%s][b]%.1f%%[/b][/color]" % [
		_hex(_C_LABEL), doom_color, doom]
	var doom_momentum = final_state.get("doom_momentum", 0.0)
	if abs(doom_momentum) > 0.1:
		var momentum_text = "^ %.1f Spiral" % doom_momentum if doom_momentum > 0 else "v %.1f Flywheel" % abs(doom_momentum)
		var momentum_color = _hex(ThemeManager.STAFF_COLORS["capability"]) if doom_momentum > 0 else _hex(ThemeManager.STAFF_COLORS["safety"])
		doom_row += "   [color=%s]%s[/color]" % [momentum_color, momentum_text]
	stats_text += doom_row + "\n\n"

	# Resources: was a header plus five indented rows plus a blank -- seven lines to
	# carry five numbers. Now one labelled row, pipe-separated. #1087's formatting
	# policy (GameConfig.format_money / format_scalar) is unchanged.
	var rc: Dictionary = ThemeManager.RESOURCE_COLORS
	stats_text += "[color=%s]* Resources:[/color] " % _hex(_C_LABEL)
	stats_text += "[color=%s]%s[/color] | " % [_hex(rc["money"]), GameConfig.format_money(final_state.get("money", 0))]
	stats_text += "[color=%s]%s compute[/color] | " % [_hex(rc["compute"]), GameConfig.format_scalar(final_state.get("compute", 0))]
	stats_text += "[color=%s]%s research[/color] | " % [_hex(rc["research"]), GameConfig.format_scalar(final_state.get("research", 0))]
	stats_text += "[color=%s]%s papers[/color] | " % [_hex(rc["papers"]), GameConfig.format_scalar(final_state.get("papers", 0))]
	stats_text += "[color=%s]%s rep[/color]\n" % [_hex(rc["reputation"]), GameConfig.format_scalar(final_state.get("reputation", 0))]

	# Team composition -- count via GameState.get_total_staff() (L0 #620: the legacy
	# field sum below missed the researchers[] roster, showing 0 employees mid-era).
	var safety = final_state.get("safety_researchers", 0)
	var capability = final_state.get("capability_researchers", 0)
	var compute_eng = final_state.get("compute_engineers", 0)
	var total_staff = safety + capability + compute_eng
	if GameManager.is_initialized and GameManager.state:
		total_staff = GameManager.state.get_total_staff()

	# Team: was a header plus three indented rows. Now one row, same three numbers,
	# still safety/capability colour-coded because that split is the game's argument.
	var sc: Dictionary = ThemeManager.STAFF_COLORS
	stats_text += "[color=%s]* Team:[/color] [b]%d[/b]" % [_hex(_C_LABEL), total_staff]
	if total_staff > 0:
		stats_text += " -- [color=%s]%d safety[/color] | [color=%s]%d capability[/color] | [color=%s]%d compute eng[/color]" % [
			_hex(sc["safety"]), safety, _hex(sc["capability"]), capability,
			_hex(sc["compute_eng"]), compute_eng]
	stats_text += "\n"

	# Upgrades purchased -- promoted onto the team row's block rather than its own
	# paragraph, since it is a single number.
	var upgrades = final_state.get("purchased_upgrades", [])
	if upgrades.size() > 0:
		stats_text += "[color=%s]* Upgrades:[/color] [b]%d purchased[/b]\n" % [_hex(_C_LABEL), upgrades.size()]

	# L8 achievements (#619): recognition only, never score (ADR-0002 anti-sink).
	#
	# CAPPED AT THREE. This block was the one unbounded region on the screen -- a good
	# run could unlock a dozen and each one printed a title AND a flavor line, so the
	# panel's height depended on how well the player did. A box that a test measured
	# against a 3-achievement fixture could still overflow for the player who earned
	# eight. Flavor text dropped: it is charm, and charm is what a moment sheds first.
	var achievements_node = get_node_or_null("/root/Achievements")
	if achievements_node and not achievements_node.unlocked_this_run.is_empty():
		var titles: Array = []
		for ach_id in achievements_node.unlocked_this_run:
			var ach_def = achievements_node.get_definition(ach_id)
			if not ach_def.is_empty():
				titles.append(str(ach_def["title"]))
		if not titles.is_empty():
			var shown: Array = titles.slice(0, ACHIEVEMENT_LINE_CAP)
			var line := ", ".join(shown)
			if titles.size() > ACHIEVEMENT_LINE_CAP:
				line += " (+%d more)" % (titles.size() - ACHIEVEMENT_LINE_CAP)
			stats_text += "[color=%s]* Achievements:[/color] [color=%s]%s[/color]\n" % [
				_hex(_C_LABEL), _hex(_C_SCORE_LABEL), line]

	# Victory/defeat flavor text. One separator, not two -- the second rule was
	# separating the flavor line from the link line, which nobody was confusing.
	stats_text += "\n[center][color=%s]-------------------[/color][/center]\n" % _hex(_C_DIM)
	if is_victory:
		stats_text += "[center][color=%s]Your lab held the line for %d months. That is the whole game: time bought, not a war won.[/color][/center]\n" % [_hex(_C_VICTORY), final_turns]
	else:
		var reason = _get_defeat_reason(final_state)
		stats_text += "[center][color=%s]%s[/color][/center]\n" % [_hex(_C_DEFEAT), reason]
		var attribution = _get_ledger_attribution_text(final_state)
		if attribution != "":
			stats_text += "[center][color=%s]%s[/color][/center]\n" % [_hex(rc["reputation"]), attribution]

	# AI Safety call to action. The "> Press ENTER for Leaderboard" line that used to
	# end this block is GONE -- it is LeaderboardButton in the button row now. ENTER
	# still works (see _input); it is simply no longer the ONLY advertised route, and
	# the advertisement is no longer buried at the bottom of a scroll.
	stats_text += "[center][color=%s]Learn about real AI safety: [url=https://aisafety.info][color=%s]aisafety.info[/color][/url][/color][/center]" % [
		_hex(_C_LABEL), _hex(_C_LINK)]

	stats_label.text = stats_text

func _persist_and_submit_score(final_state: Dictionary, game_seed: String) -> void:
	"""SCORE FIRST (isolation contract, rule 2): save the run's score to the LOCAL board and
	fire the async remote POST. Runs before the verification export + stats rendering so the
	score is durable the instant the defeat screen appears -- a later hang / force-quit /
	error cannot lose it. The remote POST is fire-and-forget on the LeaderboardSync autoload
	(lifecycle-independent from this screen) and internally bulletproof against network
	failure, so nothing here can crash or freeze the end-game."""
	# UNRANKED RUNS NEVER TOUCH THE BOARD (Pip's ruling, 2026-07-31). Scenario packs
	# rewrite the starting position -- Sandbox opens with $10,000,000 -- and scenario
	# is not part of the board key, so a scenario score is silently incomparable with
	# every Standard score sitting beside it. Same hole #1058 closed for difficulty.
	# Gated here rather than at the remote submit because the LOCAL board must stay
	# clean too: it is what the leaderboard screen renders and what the player reads
	# as "the board". The player was warned when they picked the scenario; this is the
	# second telling, and it is deliberately SHOWN rather than failing quietly -- a
	# score that just never appears is precisely this week's failure mode.
	if not GameConfig.is_ranked_run():
		_ensure_sync_status_label()
		sync_status_label.visible = true
		if GameConfig.alpha_tools_used:
			# Third telling (decision card 2026-08-01: warn at the toggle, at first
			# use, and again here) -- SHOWN, never silent (#1027).
			print("[GameOverScreen] Unranked run (Alpha Tools first used turn %d) - no local save, no remote submit" % GameConfig.alpha_tools_first_use_turn)
			sync_status_label.text = GameConfig.ALPHA_TOOLS_GAME_OVER_NOTICE
		else:
			print("[GameOverScreen] Unranked run (scenario '%s') - no local save, no remote submit" % GameConfig.scenario_id)
			sync_status_label.text = "NOT RANKED: scenario runs stay off the leaderboard. Play Standard Game for the board."
		sync_status_label.add_theme_color_override("font_color", Color(1.0, 0.75, 0.25))
		return
	var duration = Time.get_ticks_msec() / 1000.0 - game_start_time
	# BOTH identity values (Pip's ruling 2026-08-08). Until this, only the lab
	# was passed -- into a field then named `player_name` -- so #1133 could
	# collect an Operator name that no code path ever carried anywhere. A player
	# who typed their name saw it nowhere. The operator now reaches BOTH the local
	# board and the PUBLIC one: ScoreEntry.to_wire_dict() composes it into the
	# frozen `player_name` field as `LAB -- OPERATOR` (leaderboard.gd:196).
	var entry = Leaderboard.ScoreEntry.new(
		final_turns,
		GameConfig.lab_name,
		final_state.get("turn", 0),
		"v" + GameConfig.CURRENT_VERSION,  # Game version from GameConfig
		duration,
		baseline_turns,  # Baseline turns for comparison (Issue #372); 0 when not ready
		final_doom_integral,  # ADR-0002 tiebreak
		baseline_doom_integral,
		GameConfig.player_name  # the Operator -- the human, distinct from the lab
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
	"""Route the just-saved score through the IDENTITY-CONSENT flow (privacy ruling
	2026-07-26). The local save above is already durable and is never gated by any
	of this; consent covers only uploading player name + lab name + score."""
	# No sync configured -> nothing to consent to; stay silent (dev builds, forks).
	if not (LeaderboardSync.enabled and LeaderboardSync.is_configured()):
		return
	var flow: String = LeaderboardSync.consent_flow_state(
		GameConfig.leaderboard_consent_asked,
		GameConfig.submit_scores_global,
		_has_submittable_identity(),
		GameConfig.leaderboard_reminder_shown
	)
	# ONE-TIME default-identity gate (Pip 2026-08-06), LAYERED BEFORE the consent
	# flow resolves: when an upload is imminent ("submit"/"ask") and the player
	# still carries the unedited install defaults, offer one chance to claim a
	# name -- so the name is worth uploading BEFORE it is baked into a public row.
	# Never fires twice (persisted flag, set at show time); never fires for
	# "remind"/"silent" (anonymity and decline are legitimate, never nagged).
	# Consent itself (consent_flow_state above) is deliberately untouched.
	var identity_gate: String = LeaderboardSync.default_identity_prompt_state(
		flow, GameConfig.has_default_identity(), GameConfig.default_identity_prompt_shown
	)
	if identity_gate == "prompt":
		_show_default_identity_prompt(entry, game_seed, flow)
		return
	_continue_consent_flow(flow, entry, game_seed)

func _continue_consent_flow(flow: String, entry, game_seed: String) -> void:
	"""Resolve a consent_flow_state result. Split out of _maybe_submit_remote so
	the default-identity prompt can continue the SAME flow after it closes."""
	match flow:
		"submit":
			_do_remote_submit(entry, game_seed)
		"ask":
			_show_consent_prompt(entry, game_seed)
		"remind":
			_show_identity_reminder()
		_:
			# "silent" covers TWO different players and they need different screens
			# (Pip's v0.14.0 playtest, 2026-08-07: three ranked runs in a row showed
			# nothing at all, and read as a broken leaderboard).
			#   - REMEMBERED DECLINE: say where the score went and how to change it.
			#     The decline moment itself already renders this line; every run
			#     after it rendered a bare `pass`, so the one setting that explains
			#     the missing board became invisible from the only screen that
			#     depends on it. Shown, never silent (#1027).
			#   - ANONYMOUS + ALREADY NUDGED: also gets a standing line. See DEFECT 1
			#     below -- this branch used to be silent, and anonymous is the DEFAULT
			#     state of a fresh install.
			_show_local_only_notice()

func _show_local_only_notice() -> void:
	"""Standing (every-run) readout of why this score is not on the global board.

	DEFECT 1 (Pip's v0.14.0 playtest, 2026-08-07). game_config.gd:108-109 ships every
	fresh install with submit_scores_global=false and leaderboard_consent_asked=false,
	so the DEFAULT player is anonymous. consent_flow_state returns "remind" for them
	exactly ONCE and "silent" for the entire rest of the install's life. One easily
	missed line, then permanent absence from the board with no further signal -- and a
	legitimate not-yet-decided state rendered identically to a decided one.

	NOT A REVISION OF THE PRIVACY RULING (2026-07-26). Nobody is defaulted to opted-in,
	nothing is uploaded, and no flag is written here. This only says out loud what the
	current configuration already is.

	WHY A STANDING LINE RATHER THAN ANOTHER NUDGE, given a once-only nudge is what
	failed: this is a STATE READOUT, not a prompt. It is present on every game-over the
	way a mute icon is present whenever sound is off -- it never interrupts, never opens
	a dialog, never escalates its wording, and never asks for anything, so it cannot
	become a nag however many runs are played. Rejected: re-prompting every N runs (the
	nagging the remind-once ruling forbids); staying silent (the defect); a
	Settings-only indicator (invisible from the one screen where the player is asking
	"where did my score go?").

	Grey, not the amber that means NOT RANKED (#1060): the run IS ranked and the score
	IS on the local board. Only the upload is off. Borrowing amber here would overstate
	it."""
	_ensure_sync_status_label()
	sync_status_label.visible = true
	if GameConfig.leaderboard_consent_asked:
		# Remembered decline: the player made this choice; name where to unmake it.
		sync_status_label.text = "Global leaderboard: OFF -- score saved locally only (turn on in Settings)"
	else:
		# Never decided: anonymous by default. Say what is missing, not that they erred.
		sync_status_label.text = "Global leaderboard: OFF -- playing anonymously, score saved locally only (set a name and opt in via Settings)"
	sync_status_label.add_theme_color_override("font_color", Color(0.75, 0.75, 0.75))

func _has_submittable_identity() -> bool:
	"""A submission would be meaningful only with a non-empty player + lab name
	(the board displays them; consent is about sharing exactly these)."""
	return GameConfig.player_name.strip_edges() != "" and GameConfig.lab_name.strip_edges() != ""

func _do_remote_submit(entry, game_seed: String) -> void:
	"""Upload the just-saved score to the global board. Never blocks; shows a tiny
	status blip that resolves async via submit_completed."""
	if not LeaderboardSync.should_submit():
		return  # authoritative gate: enabled + configured + explicit identity consent
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

func _show_default_identity_prompt(entry, game_seed: String, flow: String) -> void:
	"""ONE-TIME (persisted flag, set at SHOW time -- the remind-once shape): the
	player is about to upload while still carrying the unedited install defaults
	("Researcher" / "AI Safety Lab"). One dialog, answerable in one click either
	way; the score is already saved locally (isolation contract rule 2), so
	nothing here can lose it. Keeping the default is a legitimate choice and is
	never asked about again. Either answer continues the consent flow unchanged."""
	GameConfig.default_identity_prompt_shown = true
	GameConfig.save_config()

	var dialog := ConfirmationDialog.new()
	dialog.title = "STILL THE DEFAULT NAME -- ONE-TIME ASK"
	# Custom content instead of dialog_text: the dialog needs editable fields, and
	# AcceptDialog lays out Control children in its content area only when its own
	# text label is unused.
	var vbox := VBoxContainer.new()
	vbox.custom_minimum_size = Vector2(460, 0)
	vbox.add_theme_constant_override("separation", 8)
	var info := Label.new()
	info.text = (
		"This score is headed for the global board under the install defaults.\n"
		+ "Every unedited copy of the game posts as exactly this name, so nobody\n"
		+ "can tell your run from anyone else's. Claim yours here, once:"
	)
	vbox.add_child(info)

	# HONESTY (2026-08-08): the prompt collects two values and the global board
	# carries only one of them today. Saying so is the whole point -- a prompt
	# that implies both appear publicly is lying to the player about what they
	# just typed.
	var board_note := Label.new()
	board_note.text = IDENTITY_PROMPT_BOARD_NOTE
	board_note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	board_note.add_theme_color_override("font_color", Color(0.72, 0.72, 0.72))
	vbox.add_child(board_note)

	var name_row := HBoxContainer.new()
	var name_label := Label.new()
	name_label.text = "Operator:"  # nomenclature ruling (#957): the player is the Operator
	name_label.custom_minimum_size = Vector2(80, 0)
	var name_edit := LineEdit.new()
	name_edit.text = GameConfig.player_name
	name_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	name_row.add_child(name_label)
	name_row.add_child(name_edit)
	vbox.add_child(name_row)

	var lab_row := HBoxContainer.new()
	var lab_label := Label.new()
	lab_label.text = "Lab:"
	lab_label.custom_minimum_size = Vector2(80, 0)
	var lab_edit := LineEdit.new()
	lab_edit.text = GameConfig.lab_name
	lab_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var reroll := Button.new()
	reroll.text = "Reroll"
	reroll.tooltip_text = "Roll a generated lab name until one fits"
	# UI-side RNG only -- never the seeded run RNG (ADR-0006).
	var reroll_rng := RandomNumberGenerator.new()
	reroll_rng.randomize()
	reroll.pressed.connect(func():
		lab_edit.text = LabNameGenerator.generate(reroll_rng)
	)
	lab_row.add_child(lab_label)
	lab_row.add_child(lab_edit)
	lab_row.add_child(reroll)
	vbox.add_child(lab_row)

	dialog.add_child(vbox)
	dialog.register_text_enter(name_edit)
	dialog.register_text_enter(lab_edit)
	dialog.ok_button_text = "[OK] Use this name"
	dialog.cancel_button_text = "Keep the default"
	dialog.confirmed.connect(func():
		_apply_identity_from_prompt(name_edit.text, lab_edit.text, entry, game_seed)
		_continue_consent_flow(flow, entry, game_seed)
	)
	# Cancel / ESC / close = keep the default, remembered; the flow continues so a
	# consented player's upload still happens -- the prompt must never cost a score.
	dialog.canceled.connect(func():
		_continue_consent_flow(flow, entry, game_seed)
	)
	add_child(dialog)
	dialog.popup_centered()

func _apply_identity_from_prompt(name_text: String, lab_text: String, entry, game_seed: String) -> void:
	"""Persist the claimed identity and retrofit it onto the CURRENT run's entry.
	An emptied field keeps its previous value -- the prompt can never strip
	identity below what the consent flow already deemed submittable."""
	var new_name := name_text.strip_edges()
	var new_lab := lab_text.strip_edges()
	if new_name != "":
		GameConfig.player_name = new_name
	if new_lab != "":
		GameConfig.lab_name = new_lab
	GameConfig.save_config()
	print("[GameOverScreen] Identity claimed at default-name prompt: %s -- %s"
		% [GameConfig.player_name, GameConfig.lab_name])
	# The claimed OPERATOR name is retrofitted too -- it is stored on the entry
	# and on the local board, and is the value waiting for the server to carry it.
	if entry != null and "operator_name" in entry and new_name != "":
		entry.operator_name = new_name
	if new_lab != "" and entry != null and "lab_name" in entry:
		entry.lab_name = new_lab
		# The LOCAL row was saved before the dialog (rule 2: durable first), under
		# the old default -- rename it in place so the player can recognise their
		# run on their own board too. Name-only; rank order untouched.
		var board = Leaderboard.new(game_seed, GameConfig.get_board_version())
		board.rename_entry(entry.entry_uuid, new_lab)
		board.free()

func _show_consent_prompt(entry, game_seed: String) -> void:
	"""FIRST-TIME identity opt-in (privacy ruling 2026-07-26): the player must click
	once to confirm that submitting PLAYER NAME + LAB NAME + score to the global
	board is OK. Either answer is remembered (never re-asked) and reversible any
	time in Settings; ESC / cancel = remembered 'keep local only'."""
	var dialog := ConfirmationDialog.new()
	dialog.title = "GLOBAL LEADERBOARD -- ONE-TIME CHOICE"
	dialog.dialog_text = (
		"Submit your scores to the global leaderboard?\n\n"
		+ "This shares publicly, for this and future runs:\n"
		+ "  player name: %s\n" % GameConfig.player_name
		+ "  lab name:    %s\n" % GameConfig.lab_name
		+ "  your score\n\n"
		+ "Nothing else is sent. Change any time in Settings."
	)
	dialog.ok_button_text = "[OK] Submit my runs"
	dialog.cancel_button_text = "Keep local only"
	dialog.confirmed.connect(func():
		_record_consent_choice(true)
		_do_remote_submit(entry, game_seed)
	)
	dialog.canceled.connect(func():
		_record_consent_choice(false)
		_ensure_sync_status_label()
		sync_status_label.visible = true
		sync_status_label.text = "Global leaderboard: local only (change in Settings)"
		sync_status_label.add_theme_color_override("font_color", Color(0.75, 0.75, 0.75))
	)
	add_child(dialog)
	dialog.popup_centered()

func _record_consent_choice(opted_in: bool) -> void:
	"""Persist the explicit identity choice IMMEDIATELY (a crash later must not
	lose it or cause a re-ask)."""
	GameConfig.leaderboard_consent_asked = true
	GameConfig.submit_scores_global = opted_in
	GameConfig.save_config()
	print("[GameOverScreen] Leaderboard identity consent recorded: %s"
		% ("opted in" if opted_in else "local only"))

func _show_identity_reminder() -> void:
	"""ONE gracious nudge, ever (persisted flag): an anonymous player (empty
	name/lab) reached submission without having opted in. Friendly label, no
	dialog, never blocks replays, never repeated on later playthroughs."""
	GameConfig.leaderboard_reminder_shown = true
	GameConfig.save_config()
	_ensure_sync_status_label()
	sync_status_label.visible = true
	sync_status_label.text = "[i] Playing anonymously -- set a name + opt in via Settings to join the global leaderboard"
	sync_status_label.add_theme_color_override("font_color", Color(0.7, 0.75, 0.8))

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
	"""Build the leaderboard status line WHERE A HUMAN WILL SEE IT.

	DEFECT 3 (Pip's v0.14.0 playtest, 2026-08-07). This label was 12pt and appended to
	the END of the panel VBox -- i.e. below the three 50px buttons, the last line in the
	panel. Measured on the failing build:
	    text="Global leaderboard: submitted (rank 1)" rect=(600,1217) 720x17
	A SUCCESSFUL submission was visually indistinguishable from nothing happening, which
	is how a working leaderboard reads as a broken one. The submitting was never the
	problem; the reporting was.

	Two changes, both about noticeability rather than wording: 16pt instead of 12, and
	inserted directly ABOVE the button row (below the stats scroll) instead of after it,
	so it sits inside the block the player is already reading rather than trailing off
	the bottom. Kept in the same VBox so no layout/anchoring assumptions change.

	NOT PROVEN BY ANY TEST: that it is legible against the panel art at this size. That
	needs Pip on a real build -- the tests only pin that the size and position which
	demonstrably failed are gone."""
	if is_instance_valid(sync_status_label):
		return
	sync_status_label = Label.new()
	sync_status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sync_status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	sync_status_label.add_theme_font_size_override("font_size", 16)
	var parent: Node = stats_label.get_parent() if stats_label else self
	parent.add_child(sync_status_label)
	# Move it above the button row. Falls back to append (the old behaviour) if the
	# scene tree ever loses ButtonsHBox, so a rename cannot crash the defeat screen.
	for i in range(parent.get_child_count()):
		if parent.get_child(i).name == "ButtonsHBox":
			parent.move_child(sync_status_label, i)
			return

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
		out += "[center][color=%s]%s[/color][/center]\n" % [
			_hex(ThemeManager.RESOURCE_COLORS["reputation"]), killer_line]
	if has_chain:
		out += "[color=%s]" % _hex(_C_DIM)
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

func _on_leaderboard_pressed() -> void:
	"""The board, reachable by clicking a thing that says 'Leaderboard'.

	Until now the ONLY advertised route was the string "> Press ENTER for Leaderboard",
	which was the 31st and last line of a RichTextLabel showing 14 lines -- so on a
	1920x1080 screen the instruction was 413px below the bottom of its own box. Pip
	played v0.14.0 and never found the leaderboard. The keyboard shortcut worked the
	whole time; nothing told him about it.

	ENTER/SPACE still work (_input). This is the same call, given a surface."""
	print("[GameOverScreen] Leaderboard button pressed")
	_continue_to_leaderboard()

func _on_play_again_pressed():
	"""Restart the game.

	VERIFIED (scene-reentry run-killer family audit, sibling of #979): this looks like it
	reloads the GAME-OVER SCREEN, not the game, but it doesn't -- GameOverScreen is never its
	own current_scene. It only ever lives as a child of TabManager inside main.tscn
	(godot/scenes/main.tscn, node "GameOverScreen"; see also test_endgame_score_isolation.gd /
	test_game_over_remote_isolation.gd, which instantiate it standalone for isolated testing,
	never as the live tree root). So get_tree().current_scene at this point IS main.tscn, and
	SceneTransition.reload() reloads main.tscn -- re-running main_ui._boot_game(), whose
	fresh-start branch calls GameManager.start_new_game("", true) (force=true: a real reset,
	not a reentry bug). Play Again works correctly."""
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
