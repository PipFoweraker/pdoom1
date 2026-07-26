extends GutTest
## Guards Anchor Sockets V2 (data/office/anchor_sockets.json + its consumer
## scripts/ui/office_floor/anchored_overlay.gd), issues #894 #900 #913:
##   - the JSON parses, carries _meta/_schema, and covers the promoted cat sets;
##   - every referenced clip dir EXISTS in art_source and holds the declared
##     frame range (art_source is git-tracked, so any full checkout has it);
##   - PIL-authored anchors land INSIDE the sprite's opaque subject bbox
##     (tolerance for glow anchors that sit just off the silhouette);
##   - AnchoredOverlay resolves the anchor position for a synthetic host,
##     follows a direction switch, and hides sockets absent from a clip
##     (butt exists only on rear-facing + butt-flash clips);
##   - the footfall pulse hook is deterministic (frame-index driven, no RNG).

const SOCKETS_PATH := "res://data/office/anchor_sockets.json"
const MIN_SETS := 3  # tabby / black / purple promoted sweep sets

var _art_missing_logged := false


func _load_doc() -> Dictionary:
	var f := FileAccess.open(SOCKETS_PATH, FileAccess.READ)
	assert_not_null(f, "anchor_sockets.json must be readable")
	if f == null:
		return {}
	var json := JSON.new()
	assert_eq(json.parse(f.get_as_text()), OK, "anchor_sockets.json must be valid JSON")
	f.close()
	return json.data if json.data is Dictionary else {}


func _repo_root() -> String:
	return (ProjectSettings.globalize_path("res://") + "/..").simplify_path()


## art_source ships in git; absent = partial checkout, skip file checks cleanly.
func _art_source_present() -> bool:
	return DirAccess.dir_exists_absolute(_repo_root() + "/art_source")


func test_doc_parses_with_meta_schema_and_promoted_sets():
	var doc := _load_doc()
	assert_ne(String(doc.get("_meta", {}).get("version", "")), "", "carries _meta.version")
	assert_true(doc.has("_schema"), "documents its fields in a _schema block")
	var sprites: Dictionary = doc.get("sprites", {})
	assert_true(sprites.size() >= MIN_SETS,
		"expected at least %d sprite sets, found %d" % [MIN_SETS, sprites.size()])
	for sid in sprites:
		var s: Dictionary = sprites[sid]
		assert_eq(Array(s.get("canvas_px", [])).size(), 2, "'%s' canvas_px is [w, h]" % sid)
		assert_true(s.get("clips", {}).size() > 0, "'%s' has clips" % sid)


func test_every_clip_has_feet_sockets_and_eyes():
	var sprites: Dictionary = _load_doc().get("sprites", {})
	for sid in sprites:
		var clips: Dictionary = sprites[sid].get("clips", {})
		for clip in clips:
			var e: Dictionary = clips[clip]
			var label := "%s/%s" % [sid, clip]
			assert_ne(String(e.get("source_dir", "")), "", "'%s' has source_dir" % label)
			assert_eq(Array(e.get("feet_px", [])).size(), 2, "'%s' feet_px is [x, y]" % label)
			assert_eq(Array(e.get("subject_px", [])).size(), 2, "'%s' subject_px is [w, h]" % label)
			assert_true(e.get("footfall_frames", null) is Array, "'%s' has footfall_frames" % label)
			var names: Array = []
			for sk in e.get("sockets", []):
				assert_true(sk is Dictionary and sk.has("name") and sk.has("px") and sk.has("layer"),
					"'%s' socket needs name/px/layer (unified socket shape)" % label)
				assert_eq(Array(sk.get("px", [])).size(), 2, "'%s' socket px is [x, y]" % label)
				assert_true(String(sk.get("layer", "")) in ["front", "behind"],
					"'%s' socket layer front|behind" % label)
				names.append(String(sk.get("name", "")))
			# Ruled anchor set: eyes on EVERY direction; spine_mid reserve everywhere.
			assert_true("eyes" in names, "'%s' carries an eyes anchor" % label)
			assert_true("spine_mid" in names, "'%s' carries the spine_mid reserve" % label)


func test_butt_only_on_rear_facing_and_butt_flash_clips():
	# Ruling: butt anchors exist on rear-facing walks + butt-flash splices ONLY.
	var sprites: Dictionary = _load_doc().get("sprites", {})
	for sid in sprites:
		var clips: Dictionary = sprites[sid].get("clips", {})
		for clip in clips:
			var has_butt := false
			for sk in clips[clip].get("sockets", []):
				if String(sk.get("name", "")) == "butt":
					has_butt = true
			var rear := String(clip).begins_with("walk_north")
			assert_eq(has_butt, rear,
				"'%s/%s': butt anchor exactly on rear-facing/butt-flash clips" % [sid, clip])


func test_referenced_clip_dirs_and_frames_exist():
	if not _art_source_present():
		pass_test("art_source absent (partial checkout) -- file checks skipped")
		return
	var root := _repo_root()
	var sprites: Dictionary = _load_doc().get("sprites", {})
	for sid in sprites:
		var clips: Dictionary = sprites[sid].get("clips", {})
		for clip in clips:
			var e: Dictionary = clips[clip]
			var label := "%s/%s" % [sid, clip]
			var d := (root + "/" + String(e.get("source_dir", ""))).simplify_path()
			assert_true(DirAccess.dir_exists_absolute(d), "'%s' source_dir exists: %s" % [label, d])
			var lo := 0
			var rng: Array = e.get("frames", [])
			if rng.size() == 2:
				lo = int(rng[0])
				# the declared range must exist in full
				assert_true(FileAccess.file_exists("%s/frame_%03d.png" % [d, int(rng[1])]),
					"'%s' declared last frame exists" % label)
			assert_true(FileAccess.file_exists("%s/frame_%03d.png" % [d, lo]),
				"'%s' first frame exists" % label)


func test_anchors_inside_subject_bbox_and_feet_match_measurement():
	if not _art_source_present():
		pass_test("art_source absent (partial checkout) -- pixel checks skipped")
		return
	var root := _repo_root()
	var sprites: Dictionary = _load_doc().get("sprites", {})
	for sid in sprites:
		var clips: Dictionary = sprites[sid].get("clips", {})
		for clip in clips:
			var e: Dictionary = clips[clip]
			var label := "%s/%s" % [sid, clip]
			var d := (root + "/" + String(e.get("source_dir", ""))).simplify_path()
			var lo := 0
			var rng: Array = e.get("frames", [])
			if rng.size() == 2:
				lo = int(rng[0])
			var img := Image.new()
			if img.load("%s/frame_%03d.png" % [d, lo]) != OK:
				fail_test("'%s' frame unreadable" % label)
				continue
			var bbox := img.get_used_rect()
			var feet: Array = e.get("feet_px", [0, 0])
			var feet_v := Vector2(float(feet[0]), float(feet[1]))
			# feet_px is averaged across frames; frame `lo` must agree within a few px.
			assert_almost_eq(feet_v.x, bbox.position.x + bbox.size.x * 0.5, 4.0,
				"'%s' feet x ~ bbox bottom-centre" % label)
			assert_almost_eq(feet_v.y, float(bbox.end.y), 4.0,
				"'%s' feet y ~ bbox baseline" % label)
			# PIL-authored anchors sit inside the subject bbox (small tolerance:
			# averaging across frames can put a static anchor just off frame 0's
			# silhouette).
			var tol := 4.0
			for sk in e.get("sockets", []):
				var off: Array = sk.get("px", [0, 0])
				var p := feet_v + Vector2(float(off[0]), float(off[1]))
				assert_between(p.x, bbox.position.x - tol, float(bbox.end.x) + tol,
					"'%s' socket '%s' x inside subject bbox" % [label, sk.get("name")])
				assert_between(p.y, bbox.position.y - tol, float(bbox.end.y) + tol,
					"'%s' socket '%s' y inside subject bbox" % [label, sk.get("name")])


func test_footfall_frames_within_clip_length():
	if not _art_source_present():
		pass_test("art_source absent (partial checkout) -- frame-count checks skipped")
		return
	var root := _repo_root()
	var sprites: Dictionary = _load_doc().get("sprites", {})
	for sid in sprites:
		var clips: Dictionary = sprites[sid].get("clips", {})
		for clip in clips:
			var e: Dictionary = clips[clip]
			var d := (root + "/" + String(e.get("source_dir", ""))).simplify_path()
			var lo := 0
			var hi := -1
			var rng: Array = e.get("frames", [])
			if rng.size() == 2:
				lo = int(rng[0])
				hi = int(rng[1])
			var n := 0
			var i := lo
			while FileAccess.file_exists("%s/frame_%03d.png" % [d, i]) and (hi < 0 or i <= hi):
				n += 1
				i += 1
			for ff in e.get("footfall_frames", []):
				assert_between(int(ff), 0, n - 1,
					"'%s/%s' footfall frame %d within %d-frame clip" % [sid, clip, int(ff), n])


# --- AnchoredOverlay static queries ------------------------------------------

func test_static_queries():
	assert_true(AnchoredOverlay.sprite_sets().size() >= MIN_SETS, "sets visible to the consumer")
	var sk := AnchoredOverlay.socket_of("cat_tabby_v1", "walk_east", "eyes")
	assert_false(sk.is_empty(), "tabby walk_east has an eyes socket")
	assert_eq(AnchoredOverlay.socket_of("cat_tabby_v1", "walk_east", "butt"), {},
		"no butt socket on a side walk -> empty dict")
	assert_eq(AnchoredOverlay.socket_of("__nope__", "walk_east", "eyes"), {},
		"unknown set -> empty dict")
	assert_eq(AnchoredOverlay.canvas_of("cat_tabby_v1"), Vector2(68, 68))


# --- AnchoredOverlay runtime behaviour (synthetic host, no art needed) --------

func _synthetic_host() -> AnimatedSprite2D:
	var img := Image.create(68, 68, false, Image.FORMAT_RGBA8)
	img.fill(Color(1, 1, 1, 1))
	var tex := ImageTexture.create_from_image(img)
	var sf := SpriteFrames.new()
	sf.rename_animation("default", "walk_east")
	sf.add_frame("walk_east", tex)
	sf.add_frame("walk_east", tex)
	sf.add_frame("walk_east", tex)
	for extra in ["walk_north", "walk_north_alt", "idle", "no_anchor_clip"]:
		sf.add_animation(extra)
		sf.add_frame(extra, tex)
	var host := AnimatedSprite2D.new()
	host.sprite_frames = sf
	host.play("walk_east")
	return host


func _expected_local(sid: String, clip: String, anchor: String) -> Vector2:
	var sk := AnchoredOverlay.socket_of(sid, clip, anchor)
	var off: Array = sk.get("px", [0, 0])
	return AnchoredOverlay.feet_of(sid, clip) + Vector2(float(off[0]), float(off[1])) \
		- AnchoredOverlay.canvas_of(sid) * 0.5


func test_overlay_positions_at_anchor_and_follows_direction_switch():
	var host := _synthetic_host()
	add_child_autofree(host)
	var ov := AnchoredOverlay.new()
	ov.attach(host, "cat_tabby_v1", "eyes", null, {"pulse": false})
	assert_eq(ov.get_parent(), host, "overlay reparents under the host")
	assert_true(ov.visible, "eyes socket exists on walk_east")
	assert_eq(ov.position, _expected_local("cat_tabby_v1", "walk_east", "eyes"),
		"positions at feet_px + socket px, centred-host corrected")
	# Direction switch: the host clip change re-resolves the anchor.
	host.play("walk_north")
	assert_true(ov.visible, "eyes anchor also exists on walk_north")
	assert_eq(ov.position, _expected_local("cat_tabby_v1", "walk_north", "eyes"),
		"anchor follows the direction switch")
	assert_eq(ov.z_index, -1, "rear-view eyes socket is layer 'behind' -> z below host")
	# A clip with no anchor data hides the overlay instead of guessing.
	host.play("no_anchor_clip")
	assert_false(ov.visible, "unknown clip -> overlay hidden")


func test_butt_overlay_appears_only_on_rear_clips():
	var host := _synthetic_host()
	add_child_autofree(host)
	var ov := AnchoredOverlay.new()
	ov.attach(host, "cat_tabby_v1", "butt", null, {"pulse": false})
	assert_false(ov.visible, "no butt on a side walk")
	host.play("walk_north")
	assert_true(ov.visible, "butt appears on the rear-facing walk")
	assert_eq(ov.position, _expected_local("cat_tabby_v1", "walk_north", "butt"))
	host.play("walk_north_alt")
	assert_true(ov.visible, "butt appears on the butt-flash splice")
	host.play("walk_east")
	assert_false(ov.visible, "butt hides again on a side walk")


func test_enabled_toggle_and_footfall_pulse_deterministic():
	var host := _synthetic_host()
	add_child_autofree(host)
	var ov := AnchoredOverlay.new()
	ov.attach(host, "cat_tabby_v1", "eyes", null,
		{"opacity": 0.5, "pulse": true, "pulse_strength": 0.5})
	assert_true(ov.visible)
	ov.set_enabled(false)
	assert_false(ov.visible, "master toggle hides the overlay")
	ov.set_enabled(true)
	assert_true(ov.visible, "and brings it back")
	# Footfall pulse: purely frame-index driven. walk_east footfalls come from
	# the JSON; drive the host to one and check the pulse bumps the modulate.
	# Pause the host + zero the pulse first: the auto-playing loop passes the
	# footfall frame on its own, which would inflate the baseline read.
	host.pause()
	var ffs: Array = AnchoredOverlay.footfalls_of("cat_tabby_v1", "walk_east")
	assert_true(ffs.size() > 0, "authored footfall frames exist for walk_east")
	ov._pulse = 0.0
	ov._apply_visual()
	var base_a := ov.modulate.a
	host.frame = int(ffs[0])
	ov._on_host_frame()
	assert_gt(ov.modulate.a, base_a, "paw-strike frame pulses the glow (deterministic)")
	# Non-footfall frame does NOT pulse from rest.
	var ov2 := AnchoredOverlay.new()
	ov2.attach(host, "cat_tabby_v1", "eyes", null,
		{"opacity": 0.5, "pulse": true, "pulse_strength": 0.5})
	var ffs_int: Array = []
	for ff in ffs:
		ffs_int.append(int(ff))
	var quiet := -1
	for i in range(3):
		if not (i in ffs_int):
			quiet = i
	if quiet >= 0:
		ov2._pulse = 0.0
		ov2._apply_visual()
		var a2 := ov2.modulate.a
		host.frame = quiet
		ov2._on_host_frame()
		assert_eq(ov2.modulate.a, a2, "non-footfall frame does not pulse")
