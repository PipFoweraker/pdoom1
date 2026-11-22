extends GutTest
## #1281: a saved report is not a sent report.
##
## The panel wrote reports to `user://bug_reports` and told the player to email
## the file to team@pdoom1.com. Nobody does that. Measured on the dev machine
## after a fortnight of playtesting: that directory was **empty**. Not one report
## had ever been filed, let alone forwarded. The feature existed, was reachable
## by button and keybind, and produced nothing -- the same inert-mechanic shape
## as a lever that quotes a doom figure it never applies (#967).
##
## Pip, 2026-08-23: "I'm still terrified that I'm losing in-game comms... there
## aren't easy ways in game for players to give feedback and I want it like 50%
## easier and twice as obvious."
##
## Routing confirmed by Pip the same day: player -> public issue tracker -> LLM
## triage -> a summary the developer reads. NOT a raw personal inbox. The panel
## states this because a player who does not know where it goes does not send it.
##
## These pin the PURE helpers -- formatting and URL construction -- which is where
## the contract bugs hide. The button wiring is not unit-testable here; what is
## testable is that the text a player sends carries what a reader needs.

const REPORT := {
	"report_type": "bug",
	"title": "Compute engineers do not load into the sim",
	"description": "My employee screen says 2 engineers but they never appear.",
	"system_info": {
		"os_type": "Windows",
		"godot_version": "4.5.1",
		"game_version": "0.14.2",
		"timestamp": "2026-08-23T06:00:00Z",
	},
	"attachments": {"screenshot_included": false, "save_file_included": false},
	"attribution": null,
}


func _with(extra: Dictionary) -> Dictionary:
	var d := REPORT.duplicate(true)
	for k in extra:
		d[k] = extra[k]
	return d


# --- the report carries what a reader needs ----------------------------------

func test_transport_text_carries_title_and_description():
	var s := BugReporter.format_for_transport(REPORT)
	assert_true(s.contains("Compute engineers do not load"), "title missing: " + s)
	assert_true(s.contains("My employee screen says 2 engineers"), "description missing")


func test_transport_text_carries_versions_so_a_report_is_reproducible():
	var s := BugReporter.format_for_transport(REPORT)
	assert_true(s.contains("0.14.2"), "game version missing -- a report without it cannot be placed on a build")
	assert_true(s.contains("Windows"), "OS missing")


func test_report_type_is_named_in_words_not_an_enum_index():
	assert_true(BugReporter.format_for_transport(REPORT).contains("Bug"), "bug")
	assert_true(BugReporter.format_for_transport(_with({"report_type": "feature_request"}))
		.contains("Feature request"), "feature_request")
	assert_true(BugReporter.format_for_transport(_with({"report_type": "feedback"}))
		.contains("Feedback"), "feedback")


func test_optional_sections_appear_only_when_filled():
	var without := BugReporter.format_for_transport(REPORT)
	assert_false(without.contains("Steps to reproduce"), "empty section must not be emitted")
	var with_steps := BugReporter.format_for_transport(
		_with({"steps_to_reproduce": "Hire an engineer, then look at the sim."}))
	assert_true(with_steps.contains("Steps to reproduce"), "filled section must be emitted")
	assert_true(with_steps.contains("Hire an engineer"), "content missing")


# --- attachments must not be over-claimed -------------------------------------

func test_attachments_are_described_as_staying_on_the_players_machine():
	## The screenshot and save file are METADATA ONLY -- the files never travel.
	## Saying "screenshot attached" in text that gets pasted into an issue would
	## make a reader wait for an image that does not exist.
	var s := BugReporter.format_for_transport(
		_with({"attachments": {"screenshot_included": true, "save_file_included": true}}))
	assert_true(s.contains("not attached here"),
		"an attachment that did not travel must say so. Got: " + s)


func test_no_attachment_line_when_nothing_was_attached():
	assert_false(BugReporter.format_for_transport(REPORT).contains("not attached here"))


# --- attribution is opt-in and must never leak --------------------------------

func test_attribution_absent_by_default():
	assert_false(BugReporter.format_for_transport(REPORT).contains("reported by"),
		"a null attribution must produce no byline")


func test_attribution_included_when_the_player_gave_one():
	var s := BugReporter.format_for_transport(
		_with({"attribution": {"name": "Wanasai", "contact": null}}))
	assert_true(s.contains("reported by Wanasai"), "opt-in attribution should appear")


func test_contact_details_are_never_put_in_the_transport_text():
	## Contact info is for the developer's private copy, not for a block the player
	## is invited to paste into a PUBLIC issue tracker.
	var s := BugReporter.format_for_transport(
		_with({"attribution": {"name": "Wanasai", "contact": "wanasai@example.com"}}))
	assert_false(s.contains("example.com"),
		"contact details must not ride into public paste-able text. Got: " + s)


# --- the tracker URL ----------------------------------------------------------

func test_issue_url_points_at_the_real_repo():
	var u := BugReporter.github_issue_url(REPORT)
	assert_true(u.begins_with("https://github.com/PipFoweraker/pdoom1/issues/new"),
		"Got: " + u)


func test_issue_url_is_labelled_so_player_reports_can_be_found():
	assert_true(BugReporter.github_issue_url(REPORT).contains("labels=player-feedback"))


func test_issue_url_percent_encodes_the_body():
	var u := BugReporter.github_issue_url(REPORT)
	assert_false(u.contains(" "), "a raw space breaks the URL: " + u)
	assert_true(u.contains("title="), "title param missing")
	assert_true(u.contains("body="), "body param missing")


func test_untitled_report_still_produces_a_usable_url():
	## An empty title used to be possible; a blank issue title is worse than a
	## generic one because it cannot be scanned in a list.
	var u := BugReporter.github_issue_url(_with({"title": ""}))
	assert_true(u.contains("title="), "Got: " + u)
	assert_false(u.contains("title=&"), "title must not be empty: " + u)


func test_very_long_report_is_truncated_and_says_so():
	## GitHub truncates long query strings silently. Losing the tail without
	## telling anyone is the silent-failure class this repo keeps meeting.
	var long := ""
	for i in range(3000):
		long += "the description continues. "
	var u := BugReporter.github_issue_url(_with({"description": long}))
	assert_true(u.length() < 12000, "URL should be capped, got %d chars" % u.length())
	assert_true(u.uri_decode().contains("truncated"),
		"a truncated body must announce it")


# --- the routing promise ------------------------------------------------------

func test_routing_text_states_where_a_report_goes():
	var t := BugReporter.ROUTING_TEXT
	assert_true(t.length() > 0, "routing must be stated, not folklore")
	assert_true(t.to_lower().contains("triage"),
		"the player is promised triage before a human reads it. Got: " + t)


func test_routing_text_denies_the_personal_inbox():
	## Pip's confirmed shape: it goes to the tracker and is summarised, it does
	## NOT land in the developer's inbox. The player is told the second half too,
	## because that is the part that makes people willing to write.
	assert_true(BugReporter.ROUTING_TEXT.to_lower().contains("personal inbox"),
		"Got: " + BugReporter.ROUTING_TEXT)
