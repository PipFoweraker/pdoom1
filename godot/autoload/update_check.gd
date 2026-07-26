extends Node
## UpdateCheck -- the launch call: anonymous install ping + remote update check
## (issue #799: "one request, two jobs"; this is L2 of the update ladder in
## docs/game-design/DISTRIBUTION_AND_PATCHING.md -- an in-game update NOTICE,
## never an auto-downloader).
##
## Two jobs, fired once per session at boot, both fire-and-forget:
##   1. UPDATE CHECK -- GET the static version feed the website already publishes
##      (https://pdoom1.com/data/version.json). No identifiers attached, so per
##      #799 it does NOT sit behind the analytics opt-out. If the remote version
##      is numerically newer, `update_available` fires and the welcome screen
##      shows a quiet dismissible notice pointing at the releases page.
##   2. ANONYMOUS PING -- POST a Plausible event to analytics.pdoom1.com with a
##      random UUIDv4 install_id persisted to user://. NEVER derived from
##      hardware/username/anything about the machine (#799: a random UUID that
##      regenerates on reinstall is exactly right -- it counts installs, it is
##      not a device fingerprint). Gated behind the player's privacy opt-outs
##      (see should_send_ping). Issue #940's morning-briefing install metrics
##      consume this server-side; nothing else is collected.
##
## HARD RULES (from #799 + the v0.11.0 lessons):
##   - Never block startup or gameplay. Everything async, 3s hard timeout.
##   - Any failure (offline, timeout, malformed JSON, HTTP error) is a silent
##     no-op for the player. Loud in logs (one push_warning max per session),
##     silent on screen. The game must behave identically offline.
##   - Compare semver NUMERICALLY, never as strings ("0.9.0" > "0.11.0" is true
##     for strings and would tell every player they are ahead).
##   - Never auto-download. Notice + link; the player decides.
##   - Never retry the ping in a loop; a 202 means "accepted", not "stored".
##
## No `class_name` on purpose: registered as the `UpdateCheck` autoload; tests
## load the script directly and exercise the static helpers + response handler.

## Fired when the feed reports a version numerically newer than the local build
## AND the player has not dismissed the notice for that exact version.
signal update_available(remote_version: String)

## Canonical static version feed (auto-published by the website repo's workflow).
const VERSION_FEED_URL := "https://pdoom1.com/data/version.json"
## Where the notice sends the player. Latest release page; never a binary.
const UPDATE_PAGE_URL := "https://github.com/PipFoweraker/pdoom1/releases/latest"
## Plausible ingest endpoint (#799: verified live, returns 202, no auth).
const ANALYTICS_URL := "https://analytics.pdoom1.com/api/event"
## Hard cap on either request. An update check that can stall launch is worse
## than no update check.
const REQUEST_TIMEOUT_SEC := 3.0
## The ONLY thing the ping persists client-side: a random install id.
const INSTALL_ID_PATH := "user://install_id.txt"

## Patch-cadence notice sunset (#939). The welcome screen shows a "patching
## frequently right now" label ONLY while today < this date, so removal cannot
## be forgotten (loud-success pattern): the label self-retires on 2026-08-04.
## DELETE the label code (welcome_screen._setup_launch_notices) after that date.
const PATCH_CADENCE_SUNSET := "2026-08-04"

## Set when the feed reports a newer, non-dismissed version ("" otherwise).
## The welcome screen reads this on _ready in case the HTTP response landed
## before the scene did, then also listens for update_available.
var available_version: String = ""

var _launched := false
var _warned := false

func _ready() -> void:
	# Keep polling even if the tree pauses right after boot (same rationale as
	# LeaderboardSync: an in-flight HTTPRequest must not stall forever).
	process_mode = Node.PROCESS_MODE_ALWAYS
	if DisplayServer.get_name() == "headless":
		# CI / GUT / --import passes: never do real HTTP in headless runs.
		print("[UpdateCheck] Headless run; launch call skipped.")
		return
	# Deferred so boot never waits on us, not even for request setup.
	call_deferred("_start_launch_call")

## Fire both jobs. Once per session; safe to call again (no-op).
func _start_launch_call() -> void:
	if _launched:
		return
	_launched = true
	_dispatch_get(VERSION_FEED_URL, handle_check_response)
	if should_send_ping():
		_send_ping()
	else:
		print("[UpdateCheck] Launch ping disabled by privacy settings; not sent.")

# --------------------------------------------------------------------------
# Pure helpers (no HTTP, no state) -- unit-tested directly, the contract bugs
# live here (string-compare trap, v-prefix tolerance, malformed feeds).
# --------------------------------------------------------------------------

## Strip whitespace and an optional leading v/V: "v0.13.1" -> "0.13.1".
static func normalize_version(s: String) -> String:
	var t := s.strip_edges()
	if t.begins_with("v") or t.begins_with("V"):
		t = t.substr(1)
	return t

## Parse "0.13.1" / "v0.13.1" -> [0, 13, 1] (ints). Two-part "0.13" pads to
## [0, 13, 0]. Anything non-numeric (including ladder-epoch strings like "L1"
## or "2" alone -- the build-vs-ladder split means those are NOT build
## versions) -> [] so comparisons fail closed and no notice ever shows.
static func parse_version(s: String) -> Array:
	var t := normalize_version(s)
	if t == "":
		return []
	var parts := t.split(".")
	if parts.size() < 2 or parts.size() > 3:
		return []
	var out: Array = []
	for p in parts:
		if p == "":
			return []
		for c in p:
			if c < "0" or c > "9":
				return []
		out.append(int(p))
	while out.size() < 3:
		out.append(0)
	return out

## Numeric triple compare (#799: NEVER string compare -- "0.9.0" > "0.11.0" as
## strings). Malformed either side -> false (fail closed, no notice).
static func is_remote_newer(remote: String, local: String) -> bool:
	var r := parse_version(remote)
	var l := parse_version(local)
	if r.is_empty() or l.is_empty():
		return false
	for i in range(3):
		if r[i] != l[i]:
			return r[i] > l[i]
	return false

## Extract latest_release.version from the feed body. Any malformed shape -> "".
static func parse_version_feed(body: String) -> String:
	var json := JSON.new()
	if json.parse(body) != OK or typeof(json.data) != TYPE_DICTIONARY:
		return ""
	var latest = json.data.get("latest_release", {})
	if typeof(latest) != TYPE_DICTIONARY:
		return ""
	var version = latest.get("version", "")
	if typeof(version) != TYPE_STRING:
		return ""
	return String(version).strip_edges()

## Notice gate: remote must be numerically newer AND not the version the player
## already dismissed (#799: "don't re-nag every launch for the same version").
## v-prefix tolerated on every input.
static func should_show_notice(remote: String, local: String, dismissed: String) -> bool:
	if not is_remote_newer(remote, local):
		return false
	return normalize_version(remote) != normalize_version(dismissed)

## The EXACT Plausible event body from #799. Whitelist by construction: these
## four props are everything the ping ever carries. No hostname, no username,
## no locale, no hardware ids -- the privacy test asserts this stays true.
static func build_ping_body(install_id: String, version: String, os_name: String, first_launch: bool) -> Dictionary:
	return {
		"name": "Game Launch",
		"domain": "pdoom1.com",
		"url": "app://pdoom1/launch",
		"props": {
			"install_id": install_id,
			"version": version,
			"os": os_name,
			"first_launch": first_launch,
		},
	}

## Honest UA for both requests: game + version + platform, nothing else.
## Plausible drops requests with no User-Agent, so this must always be set on
## the ping; on the feed GET it doubles as a server-log signal (#940).
static func build_user_agent(version: String, os_name: String) -> String:
	return "pdoom1/%s (%s)" % [version, os_name]

## RFC-4122 UUIDv4 from Godot's CSPRNG-seeded RNG. Random by construction --
## never derived from the machine (#799 install_id rules).
static func generate_uuid_v4() -> String:
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	var hex := "0123456789abcdef"
	var out := ""
	for i in range(32):
		var nibble: int
		if i == 12:
			nibble = 4  # version nibble
		elif i == 16:
			nibble = 8 | (rng.randi() & 0x3)  # variant nibble: 8/9/a/b
		else:
			nibble = rng.randi() & 0xF
		out += hex[nibble]
		if i == 7 or i == 11 or i == 15 or i == 19:
			out += "-"
	return out

## Loose UUID shape check for the persisted install id (8-4-4-4-12 hex).
static func looks_like_uuid(s: String) -> bool:
	if s.length() != 36:
		return false
	for i in range(36):
		var c := s[i]
		if i == 8 or i == 13 or i == 18 or i == 23:
			if c != "-":
				return false
		elif not ((c >= "0" and c <= "9") or (c >= "a" and c <= "f") or (c >= "A" and c <= "F")):
			return false
	return true

## #939 sunset gate: show the "patching frequently" label only strictly BEFORE
## the sunset date. ISO YYYY-MM-DD compares correctly as strings; anything that
## does not look like an ISO date fails closed (label hidden).
static func is_patch_notice_active(today_iso: String, sunset_iso: String) -> bool:
	if not _looks_like_iso_date(today_iso) or not _looks_like_iso_date(sunset_iso):
		return false
	return today_iso < sunset_iso

static func _looks_like_iso_date(s: String) -> bool:
	if s.length() != 10 or s[4] != "-" or s[7] != "-":
		return false
	for i in range(10):
		if i == 4 or i == 7:
			continue
		if s[i] < "0" or s[i] > "9":
			return false
	return true

# --------------------------------------------------------------------------
# Gates + response handling (instance methods; GameConfig read defensively so
# tests can instance this script and drive them with stubbed values).
# --------------------------------------------------------------------------

## Privacy gate for the ping (the update-check GET is NOT gated: it carries no
## identifiers, per #799). TIER 2 of the two-tier model
## (docs/PRIVACY_POSTURE.md, ruled + approved by Pip 2026-07-26): the ping is
## identity-free (random install UUID only), so the leaderboard gate -- which
## now means IDENTITY consent specifically -- does NOT cover it. The ping
## honours exactly one thing: its own default-ON, honestly-labelled settings
## toggle (GameConfig.send_launch_ping).
func should_send_ping() -> bool:
	if typeof(GameConfig) != TYPE_OBJECT:
		return false
	if "send_launch_ping" in GameConfig:
		return bool(GameConfig.send_launch_ping)
	return true

## Feed-response handler (public so tests can call it with stubbed transport
## results -- no real HTTP in tests). Sets available_version + emits on a
## genuine newer version; every failure path is a logged no-op.
func handle_check_response(result: int, code: int, body: String) -> void:
	if result != HTTPRequest.RESULT_SUCCESS or code != 200:
		_warn_once("version feed unreachable (result=%d, http=%d) -- offline is fine, carrying on" % [result, code])
		return
	var remote := parse_version_feed(body)
	if remote == "":
		_warn_once("version feed malformed; ignoring")
		return
	var local := _local_version()
	if should_show_notice(remote, local, _dismissed_version()):
		available_version = normalize_version(remote)
		print("[UpdateCheck] Newer version available: v%s (local v%s)" % [available_version, local])
		update_available.emit(available_version)
	else:
		print("[UpdateCheck] Up to date (local v%s, feed %s)" % [local, remote])

## Player dismissed the welcome-screen notice: remember THIS version so it does
## not re-nag, but a future, even-newer release notices again.
func dismiss_current_notice() -> void:
	if available_version == "":
		return
	if typeof(GameConfig) == TYPE_OBJECT and "dismissed_update_version" in GameConfig:
		GameConfig.dismissed_update_version = available_version
		GameConfig.save_config()
	available_version = ""

func _local_version() -> String:
	if typeof(GameConfig) == TYPE_OBJECT:
		return GameConfig.CURRENT_VERSION
	return ""

func _dismissed_version() -> String:
	if typeof(GameConfig) == TYPE_OBJECT and "dismissed_update_version" in GameConfig:
		return str(GameConfig.dismissed_update_version)
	return ""

# --------------------------------------------------------------------------
# install_id persistence (user:// only; the whole client-side footprint).
# --------------------------------------------------------------------------

## Returns { "id": String, "first_launch": bool }. Missing/corrupt file ->
## fresh UUIDv4 (re-counting an install after wipe/reinstall is fine and
## expected per #799 -- do not try to make it survive).
func _load_or_create_install_id() -> Dictionary:
	if FileAccess.file_exists(INSTALL_ID_PATH):
		var f := FileAccess.open(INSTALL_ID_PATH, FileAccess.READ)
		if f != null:
			var id := f.get_as_text().strip_edges()
			f.close()
			if looks_like_uuid(id):
				return {"id": id, "first_launch": false}
	var fresh := generate_uuid_v4()
	var w := FileAccess.open(INSTALL_ID_PATH, FileAccess.WRITE)
	if w != null:
		w.store_string(fresh)
		w.close()
	# Unwritable user:// -> still ping with the fresh id; next launch simply
	# regenerates (over-counts one install; acceptable, never blocks).
	return {"id": fresh, "first_launch": true}

# --------------------------------------------------------------------------
# Async HTTP (fire-and-forget; one HTTPRequest child per call, freed on done).
# --------------------------------------------------------------------------

func _dispatch_get(url: String, on_done: Callable) -> void:
	var http := _new_request()
	http.request_completed.connect(
		func(result: int, code: int, _headers: PackedStringArray, resp_body: PackedByteArray):
			if on_done.is_valid():
				on_done.call(result, code, resp_body.get_string_from_utf8())
			http.queue_free()
	)
	var headers := ["User-Agent: %s" % build_user_agent(_local_version(), OS.get_name())]
	var err := http.request(url, headers, HTTPClient.METHOD_GET)
	if err != OK:
		http.queue_free()
		_warn_once("could not start version check (err=%d)" % err)

func _send_ping() -> void:
	var install := _load_or_create_install_id()
	var body := build_ping_body(
		str(install["id"]),
		_local_version(),
		OS.get_name(),
		bool(install["first_launch"])
	)
	var headers := [
		"Content-Type: application/json",
		"User-Agent: %s" % build_user_agent(_local_version(), OS.get_name()),
	]
	var http := _new_request()
	http.request_completed.connect(
		func(result: int, code: int, _headers: PackedStringArray, _resp: PackedByteArray):
			# 202 = "accepted", not "stored" (#799). Log and move on; NEVER retry.
			if result == HTTPRequest.RESULT_SUCCESS:
				print("[UpdateCheck] Launch ping sent (http=%d)." % code)
			else:
				print("[UpdateCheck] Launch ping did not land (result=%d); fine, no retry." % result)
			http.queue_free()
	)
	var err := http.request(ANALYTICS_URL, headers, HTTPClient.METHOD_POST, JSON.stringify(body))
	if err != OK:
		http.queue_free()

func _new_request() -> HTTPRequest:
	var http := HTTPRequest.new()
	http.timeout = REQUEST_TIMEOUT_SEC
	add_child(http)
	return http

## One push_warning per session max (loud in logs, silent to players); further
## failures downgrade to plain prints.
func _warn_once(msg: String) -> void:
	if _warned:
		print("[UpdateCheck] %s" % msg)
		return
	_warned = true
	push_warning("[UpdateCheck] %s" % msg)
