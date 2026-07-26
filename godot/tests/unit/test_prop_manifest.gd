extends GutTest
## Guards the office prop manifest (data/office/props_manifest.json) and its loader
## (scripts/core/prop_catalogue.gd):
##   - manifest parses, carries a version, and every entry's art path resolves;
##   - every PNG under assets/office_floor/props/ HAS an entry (a new prop dropped in
##     without metadata fails here loudly instead of silently force-scaling forever);
##   - geometry is sane (anchor inside canvas, positive footprint/height);
##   - sockets are schema-only (shape validated IF ever populated);
##   - PropCatalogue fallback for unmanifested ids matches the legacy PROP_TARGET_H
##     behaviour (46 px at the 64 px display tile) so renderers degrade gracefully.

const MANIFEST_PATH := "res://data/office/props_manifest.json"
const PROPS_DIR := "res://assets/office_floor/props"
const MIN_PROPS := 3  # floor: the three props shipping today; raise as the set grows


func _load_manifest() -> Dictionary:
	var file := FileAccess.open(MANIFEST_PATH, FileAccess.READ)
	assert_not_null(file, "props_manifest.json must be readable")
	if file == null:
		return {}
	var json := JSON.new()
	assert_eq(json.parse(file.get_as_text()), OK, "props_manifest.json must be valid JSON")
	file.close()
	var data = json.data
	assert_true(data is Dictionary, "manifest root must be a JSON object")
	return data if data is Dictionary else {}


func test_manifest_parses_with_version_and_schema():
	var data := _load_manifest()
	assert_ne(String(data.get("_meta", {}).get("version", "")), "", "manifest carries _meta.version")
	assert_true(data.has("_schema"), "manifest documents its fields in a _schema block")
	var props: Dictionary = data.get("props", {})
	assert_true(
		props.size() >= MIN_PROPS,
		"expected at least %d prop entries, found %d" % [MIN_PROPS, props.size()]
	)


func test_every_entry_art_path_exists():
	var props: Dictionary = _load_manifest().get("props", {})
	for id in props:
		var path := String(props[id].get("art", ""))
		assert_ne(path, "", "prop '%s' has an art path" % id)
		assert_true(ResourceLoader.exists(path), "art for '%s' does not exist: %s" % [id, path])


func test_every_prop_png_has_an_entry():
	# Enumerate the real directory so a newly added PNG cannot ship unmanifested.
	var props: Dictionary = _load_manifest().get("props", {})
	var files := DirAccess.get_files_at(PROPS_DIR)
	assert_true(files.size() > 0, "props dir should enumerate (source tree): %s" % PROPS_DIR)
	var png_count := 0
	for f in files:
		if not f.ends_with(".png"):
			continue  # skip .import metadata files
		png_count += 1
		var id := f.get_basename()
		assert_true(props.has(id), "PNG '%s' has no manifest entry (id '%s')" % [f, id])
		if props.has(id):
			assert_eq(
				String(props[id].get("art", "")),
				PROPS_DIR + "/" + f,
				"entry '%s' art path should point at its own PNG" % id
			)
	assert_true(png_count >= MIN_PROPS, "expected at least %d PNGs in %s" % [MIN_PROPS, PROPS_DIR])


func test_geometry_sane():
	var props: Dictionary = _load_manifest().get("props", {})
	for id in props:
		var e: Dictionary = props[id]
		var canvas: Array = e.get("canvas_px", [])
		var subject: Array = e.get("subject_px", [])
		var anchor: Array = e.get("anchor_px", [])
		var foot: Array = e.get("footprint_tiles", [])
		assert_eq(canvas.size(), 2, "'%s' canvas_px is [w, h]" % id)
		assert_eq(subject.size(), 2, "'%s' subject_px is [w, h]" % id)
		assert_eq(anchor.size(), 2, "'%s' anchor_px is [x, y]" % id)
		assert_eq(foot.size(), 2, "'%s' footprint_tiles is [w, h]" % id)
		if canvas.size() != 2 or subject.size() != 2 or anchor.size() != 2 or foot.size() != 2:
			continue
		# Subject fits the canvas; anchor lies inside the canvas (y is the exclusive
		# bottom of the opaque bbox, so y == canvas h is legal for flush-bottom art).
		assert_true(
			float(subject[0]) <= float(canvas[0]) and float(subject[1]) <= float(canvas[1]),
			"'%s' subject exceeds canvas" % id
		)
		assert_between(float(anchor[0]), 0.0, float(canvas[0]), "'%s' anchor x inside canvas" % id)
		assert_between(float(anchor[1]), 1.0, float(canvas[1]), "'%s' anchor y inside canvas" % id)
		assert_true(
			int(foot[0]) > 0 and int(foot[1]) > 0, "'%s' footprint tiles positive" % id
		)
		assert_gt(float(e.get("height_tiles", 0.0)), 0.0, "'%s' height_tiles positive" % id)
		# style_tags restricted to the canonical quality-tier ladder (ruled 2026-07-26).
		var tags: Array = e.get("style_tags", [])
		assert_true(tags.size() > 0, "'%s' carries at least one style tag" % id)
		for t in tags:
			assert_true(
				t in ["scummy", "decent", "premium"],
				"'%s' style tag '%s' not on the scummy/decent/premium ladder" % [id, t]
			)


func test_sockets_schema_only():
	# Sockets are a schema placeholder until a paper-doll/cosmetics consumer exists.
	# Empty is expected today; if one is ever populated, its shape must match _schema.
	var props: Dictionary = _load_manifest().get("props", {})
	for id in props:
		var sockets = props[id].get("sockets", null)
		assert_true(sockets is Array, "'%s' sockets must be an array" % id)
		for s in sockets:
			assert_true(s is Dictionary, "'%s' socket entries are objects" % id)
			assert_true(s.has("name") and s.has("px") and s.has("layer"),
				"'%s' socket needs name/px/layer" % id)


func test_loader_known_entry():
	assert_true(PropCatalogue.has("water_cooler"), "water_cooler manifested")
	assert_true(PropCatalogue.size() >= MIN_PROPS, "catalogue floor")
	# height_px scales height_tiles by the tile size the caller renders at.
	assert_almost_eq(PropCatalogue.height_px("water_cooler", 32.0), 3.5 * 32.0, 0.001)
	assert_almost_eq(PropCatalogue.height_px("water_cooler", 64.0), 3.5 * 64.0, 0.001)
	assert_eq(PropCatalogue.footprint("water_cooler"), Vector2i(1, 1))
	var a := PropCatalogue.anchor("water_cooler")
	assert_almost_eq(a.x, 31.5, 0.001, "anchor x = bottom-centre of opaque bbox")
	assert_almost_eq(a.y, 114.0, 0.001, "anchor y = opaque bbox baseline")
	assert_eq(PropCatalogue.art_path("water_cooler"), PROPS_DIR + "/water_cooler.png")


func test_loader_fallback_matches_legacy_force_scale():
	var bogus := "__no_such_prop__"
	assert_false(PropCatalogue.has(bogus))
	assert_eq(PropCatalogue.get_entry(bogus), {}, "unmanifested id -> empty entry")
	# Legacy office_floor.gd behaviour: every prop force-scaled to 46 px at the 64 px
	# display tile. The fallback must reproduce that so renderers degrade gracefully.
	assert_almost_eq(PropCatalogue.height_px(bogus, 64.0), 46.0, 0.001)
	assert_almost_eq(PropCatalogue.height_px(bogus, 32.0), 23.0, 0.001)
	assert_eq(PropCatalogue.footprint(bogus), Vector2i(1, 1), "fallback footprint 1x1")
	assert_eq(PropCatalogue.anchor(bogus), PropCatalogue.ANCHOR_UNSET,
		"fallback anchor is the documented sentinel")
	assert_eq(PropCatalogue.style_tags(bogus).size(), 0)
	# The catalogue warns ONCE per unknown id (GUT tracks push_warning as an engine
	# error). This consumes exactly one matching warning -- if _warn_once ever broke
	# and warned per-call, the extra unhandled warnings would fail this test.
	assert_engine_error(
		"has no manifest entry",
		"unmanifested id warns once via push_warning"
	)


func test_approach_px_schema_and_water_cooler_slots():
	# v1.2: optional approach_px = list of [x, y] slot offsets from anchor_px
	# (source px). water_cooler populates left/right side slots (Pip 2026-07-26:
	# walkers were standing "slightly in front of the water cooler").
	var data := _load_manifest()
	assert_true(data.get("_schema", {}).has("approach_px"), "_schema documents approach_px")
	var props: Dictionary = data.get("props", {})
	for id in props:
		if not props[id].has("approach_px"):
			continue  # optional field -- absence is the documented fallback
		var ap = props[id]["approach_px"]
		assert_true(ap is Array, "'%s' approach_px is a list" % id)
		for slot in ap:
			assert_true(slot is Array and (slot as Array).size() == 2,
				"'%s' approach slot is an [x, y] pair" % id)
	var wc: Array = props.get("water_cooler", {}).get("approach_px", [])
	assert_eq(wc.size(), 2, "water_cooler declares two approach slots")
	if wc.size() == 2:
		assert_lt(float(wc[0][0]), 0.0, "first slot on the LEFT side")
		assert_gt(float(wc[1][0]), 0.0, "second slot on the RIGHT side")


func test_loader_approach_points():
	var pts := PropCatalogue.approach_points("water_cooler")
	assert_eq(pts.size(), 2, "loader surfaces both water_cooler slots")
	if pts.size() == 2:
		assert_true(pts[0] is Vector2 and pts[1] is Vector2, "slots come back as Vector2")
		assert_lt((pts[0] as Vector2).x, 0.0)
		assert_gt((pts[1] as Vector2).x, 0.0)
	# Manifested prop WITHOUT the optional field -> empty (fallback unchanged).
	assert_eq(PropCatalogue.approach_points("filing_cabinet").size(), 0,
		"props without approach_px report no slots")
	# Unmanifested id -> empty list + the standard warn-once.
	assert_eq(PropCatalogue.approach_points("__no_such_prop_ap__").size(), 0)
	assert_engine_error("has no manifest entry", "unmanifested id warns once")


func test_style_lookup_sorted_and_deterministic():
	var decent := PropCatalogue.style_ids("decent")
	assert_true(decent.size() > 0, "at least one decent-tagged prop")
	assert_true(decent.has("water_cooler"), "water_cooler serves the decent state")
	var sorted := decent.duplicate()
	sorted.sort()
	assert_eq(decent, sorted, "style_ids returns a sorted (deterministic) list")
	assert_eq(PropCatalogue.style_ids("__no_such_style__").size(), 0)
