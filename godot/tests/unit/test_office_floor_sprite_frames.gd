extends GutTest
## OfficeFloor art-loop wiring: the real pixellab.ai SpriteFrames resource must
## have the clips employee_sprite.gd expects -- the four state clips
## (idle/walking/working/stressed) plus the directional walk clips
## (walking_east/north/west) that _update_facing_visual() prefers when a worker
## faces a non-south direction -- each with the frame count pixellab generated,
## so Tier 1 renders the real animated worker instead of the placeholder blobs.
## South walking uses the base "walking" clip; the three siblings cover E/N/W.

const RealSpriteFrames := preload("res://assets/office_floor/artloop_char/office_worker.tres")

const EXPECTED_COUNTS := {
	"idle": 4,
	"walking": 6,
	"walking_east": 6,
	"walking_north": 6,
	"walking_west": 6,
	"working": 9,
	"stressed": 9,
}


func test_has_exactly_the_expected_clips():
	var names := RealSpriteFrames.get_animation_names()
	assert_eq(names.size(), EXPECTED_COUNTS.size(), "expected exactly %d animations" % EXPECTED_COUNTS.size())
	for clip in EXPECTED_COUNTS:
		assert_true(RealSpriteFrames.has_animation(clip), "missing clip: %s" % clip)


func test_each_clip_has_the_right_frame_count():
	for clip in EXPECTED_COUNTS:
		var expected: int = EXPECTED_COUNTS[clip]
		var actual := RealSpriteFrames.get_frame_count(clip)
		assert_eq(actual, expected, "%s frame count" % clip)


func test_all_clips_loop():
	for clip in EXPECTED_COUNTS:
		assert_true(RealSpriteFrames.get_animation_loop(clip), "%s should loop" % clip)


func test_all_frames_have_a_valid_texture():
	for clip in EXPECTED_COUNTS:
		var count: int = EXPECTED_COUNTS[clip]
		for i in range(count):
			var tex := RealSpriteFrames.get_frame_texture(clip, i)
			assert_not_null(tex, "%s frame %d texture" % [clip, i])
