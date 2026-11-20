extends GutTest
## A reaction nobody was asked for must read as empty, never as the text "null".
##
## pdoom-data made safety_researcher_reaction and media_reaction nullable
## because they had been carrying invented text: 1,166 of its 1,194 events drew
## from a five-element list by random.choice, so one sentence stood as what
## safety researchers thought about hundreds of separate papers. Null now means
## nobody was asked. See pdoom-data#96.
##
## The incompatibility is narrow and easy to miss. pdoom-data KEEPS THE KEY and
## sets the value to null, so nothing raises and every `has()` guard still
## passes. `raw.get(key, "")` looks safe and is not: a default fires only on a
## MISSING key, so a present key holding null hands back the null, and
## _format_reaction is typed String.


func test_null_value_reads_as_empty():
	var raw := {"safety_researcher_reaction": null}
	assert_eq(EventService._reaction_text(raw, "safety_researcher_reaction"), "",
		"a present key holding null must read as the empty string")


func test_missing_key_reads_as_empty():
	assert_eq(EventService._reaction_text({}, "media_reaction"), "",
		"an absent key reads as empty, exactly as before")


func test_real_text_passes_through():
	var raw := {"media_reaction": "Wide coverage followed."}
	assert_eq(EventService._reaction_text(raw, "media_reaction"),
		"Wide coverage followed.",
		"a real reaction is returned unchanged")


func test_the_old_idiom_would_have_returned_null():
	## The reason this fix exists, asserted rather than described. If this ever
	## starts returning "" then Dictionary.get semantics changed and the guard
	## in _reaction_text can be reconsidered. Until then it is load-bearing.
	var raw := {"safety_researcher_reaction": null}
	assert_null(raw.get("safety_researcher_reaction", ""),
		"Dictionary.get returns the stored null, NOT the default, when the key exists")


func test_empty_reaction_formats_to_nothing():
	assert_eq(EventService._format_reaction(""), "",
		"an empty reaction contributes no flavour text and no quotation marks")


func test_present_reaction_is_quoted():
	assert_eq(EventService._format_reaction("They were alarmed."),
		" \"They were alarmed.\"",
		"a real reaction is still quoted")


func test_null_reaction_is_not_copied_into_the_game_event():
	## A key promising a sentence must not be present holding null. The same
	## rule pdoom_impact already followed three lines below it.
	var raw := {
		"id": "test:null_reactions",
		"title": "A Thing Happened",
		"safety_researcher_reaction": null,
		"media_reaction": null,
	}
	var game_event: Dictionary = EventService._transform_event(raw)
	assert_false(game_event.has("safety_researcher_reaction"),
		"a null safety reaction is omitted rather than copied through")
	assert_false(game_event.has("media_reaction"),
		"and so is a null media reaction")
