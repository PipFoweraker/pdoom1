extends GutTest
## Guards for the cold-open arrival (#801 core + #1112 B1 portal stitch / B2 held frame).
##
## The cold open is PURE PRESENTATION (its header states the contract). These tests pin
## the properties that keep it safe and shippable WITHOUT instantiating the scene:
##   1. every asset the sequence references actually ships in the pack;
##   2. the beat cues are machinery the driver knows, and the sequence still ends on
##      the interactive phone (the #811 handoff surface);
##   3. the LOCKED Pip-approved MHS copy is unchanged (edits must be deliberate);
##   4. static purity: no RNG draw, no direct scene change (SceneTransition only).

const SEQUENCE_SCRIPT_PATH: String = "res://scripts/ui/cold_open_sequence.gd"

var _seq: GDScript


func before_all() -> void:
	_seq = load(SEQUENCE_SCRIPT_PATH)


func test_every_referenced_arrival_asset_ships() -> void:
	# A silently-missing texture degrades to an invisible layer (the ResourceLoader.exists
	# guards in _build_ui), so a broken path would ship a black intro with no error.
	assert_true(ResourceLoader.exists(_seq.PORTAL_SHADER),
		"portal shader missing from the pack: %s" % _seq.PORTAL_SHADER)
	assert_true(ResourceLoader.exists(_seq.POSTER_ART),
		"held-frame poster missing from the pack: %s" % _seq.POSTER_ART)
	assert_true(ResourceLoader.exists(_seq.HERO_ART),
		"dawn-office hero art missing from the pack: %s" % _seq.HERO_ART)


func test_beat_cues_are_known_and_the_phone_still_ends_the_sequence() -> void:
	var known_cues: Array = ["", "portal_open", "world_resolves"]
	var phone_beats: int = 0
	for beat in _seq.BEATS:
		assert_true(str(beat.get("cue", "")) in known_cues,
			"unknown arrival cue (driver would silently no-op): %s" % str(beat))
		if str(beat.get("kind", "text")) == "phone":
			phone_beats += 1
	assert_eq(phone_beats, 1, "exactly one interactive phone beat")
	assert_eq(str(_seq.BEATS[-1].get("kind", "")), "phone",
		"the sequence must END on the phone -- the handoff opens a choice (#811, ADR-0001)")


func test_locked_mhs_message_is_unchanged() -> void:
	# Pip approved this string personally (#801 ruled copy). If this fails, someone edited
	# the LOCKED block; that must be a deliberate, Pip-signed change -- update both together.
	assert_eq(_seq.STRANGER_MESSAGE,
		"Hello past me! No, I can't tell you how it ends. You know nothing yet -- go and find out. Read something, show up somewhere, or be loud online. Scouting. -- MHS",
		"LOCKED copy drifted: cold_open_sequence.gd STRANGER_MESSAGE")
	assert_eq(_seq.HANDOFF_ACTION_ID, "scouting",
		"the handoff still points at scouting (also pinned in test_office_economy)")


func test_static_purity_no_rng_and_no_direct_scene_change() -> void:
	# The pure-presentation contract, checked against the SOURCE: the sequence draws no
	# RNG (the portal spin is TIME-driven in the shader) and navigates only through
	# SceneTransition (the v0.11.0 segfault rule; also enforced by check_scene_nav.py).
	# Call-shaped tokens (trailing paren) so the sequence's own header comments -- which
	# NAME change_scene_to_file while forbidding it -- do not trip the scan.
	var src: String = FileAccess.get_file_as_string(SEQUENCE_SCRIPT_PATH)
	assert_true(src.length() > 0, "could not read the sequence source for the purity scan")
	for banned in ["randi(", "randf(", "randi_range(", "randf_range(", "RandomNumberGenerator", "change_scene_to_file(", "change_scene_to_packed("]:
		assert_false(banned in src,
			"pure-presentation contract broken: '%s' appears in cold_open_sequence.gd" % banned)
