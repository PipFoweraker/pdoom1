extends Node
## LeaderboardSync -- client side of the settled PHP score API
## (docs/strategy/BACKEND_AND_DATA_ARCHITECTURE.md, server/leaderboard/score_api.php).
##
## Registered as an autoload singleton. Provides:
##   submit_score(entry, seed, version)          -> fire-and-forget POST, emits submit_completed
##   fetch_board(seed, version, limit, callback) -> async GET, invokes callback(ok, entries)
##
## DETERMINISM / REPLAY IS SACRED (ADR-0006). Everything here is a pure view/side-effect
## invoked ONLY from game-over + the leaderboard screen (both UI). It never touches the
## simulation, the seeded RNG, turn logic, or replay, and must never be called from any
## deterministic code path. It also never blocks and never crashes on network failure:
## all HTTP is async with a timeout; unreachable/unconfigured/malformed -> quiet no-op.
##
## No `class_name` on purpose: this is registered as the `LeaderboardSync` autoload, and a
## matching class_name would collide with the singleton. Callers use the autoload directly
## (LeaderboardSync.x); tests load the script and call the static helpers.

## Emitted when a submit_score POST resolves (or fails). Fire-and-forget: the caller
## may connect for a status blip but must not depend on it arriving.
##   success: reached the server AND it accepted the entry (HTTP 200, ok=true)
##   added:   the entry landed on the board (server "added"; false for a duplicate)
##   rank:    1-based rank on the board (0 if unknown)
##   message: short human-readable status for a non-blocking UI blip
signal submit_completed(success: bool, added: bool, rank: int, message: String)

const CONFIG_PATH := "res://data/leaderboard_config.json"
const ENDPOINT_FILE := "score_api.php"
const REQUEST_TIMEOUT_SEC := 8.0
const PLACEHOLDER_TOKEN := "CHANGE_ME_set_a_long_random_token"

# Durable outbox: every score we attempt to submit is written here FIRST, and removed only
# once the server acks it. If the app quits / crashes / loses network before the POST lands
# (the live release-blocker: a force-quit at the defeat freeze killed the in-flight POST and
# the score reached the server on ZERO occasions), the entry survives and is retried at the
# next launch. The server dedups by entry_uuid, so a resend of a landed score is a harmless
# no-op. This is what makes "the score actually lands even if the endpoint is slow/down".
const OUTBOX_PATH := "user://pending_scores.json"

# Loaded from CONFIG_PATH at _ready. Public so tests can set them directly.
var enabled: bool = false
var base_url: String = ""
var token: String = ""

func _ready() -> void:
	# ALWAYS process: an in-flight HTTPRequest must keep polling even if the SceneTree is
	# paused (pause menu, window resolver) -- otherwise a POST started at the defeat screen
	# could stall forever and never leave the machine.
	process_mode = Node.PROCESS_MODE_ALWAYS
	_load_config()
	# Retry anything left in the outbox from a previous session (prior crash / offline run).
	_flush_outbox()

func _load_config() -> void:
	if not FileAccess.file_exists(CONFIG_PATH):
		# Missing config -> stay disabled. Unconfigured builds never error.
		print("[LeaderboardSync] No config at %s; remote sync disabled." % CONFIG_PATH)
		return
	var file := FileAccess.open(CONFIG_PATH, FileAccess.READ)
	if file == null:
		return
	var text := file.get_as_text()
	file.close()
	var json := JSON.new()
	if json.parse(text) != OK or typeof(json.data) != TYPE_DICTIONARY:
		push_warning("[LeaderboardSync] Malformed config; remote sync disabled.")
		return
	var data: Dictionary = json.data
	enabled = bool(data.get("enabled", false))
	base_url = str(data.get("base_url", ""))
	token = str(data.get("token", ""))
	print("[LeaderboardSync] Config loaded. enabled=%s configured=%s" % [enabled, is_configured()])

## True when the config points somewhere plausible (non-empty url + token).
## Intentionally light: `enabled` is the real master switch and defaults false.
func is_configured() -> bool:
	return base_url.strip_edges() != "" and token.strip_edges() != ""

## Master gate for fetching the global board (read-only; not gated by the opt-out).
func can_fetch() -> bool:
	return enabled and is_configured()

## Gate for uploading a score: enabled + configured + the player has NOT opted out.
## The opt-out lives on GameConfig (default ON for alpha).
func should_submit() -> bool:
	if not (enabled and is_configured()):
		return false
	# Defensive: if GameConfig isn't present (isolated unit test), treat as opted-in.
	if typeof(GameConfig) == TYPE_OBJECT and "submit_scores_global" in GameConfig:
		return bool(GameConfig.submit_scores_global)
	return true

# --------------------------------------------------------------------------
# Pure helpers (no HTTP, no state) -- this is where the contract bugs hide,
# so these are unit-tested directly.
# --------------------------------------------------------------------------

## Full endpoint URL from the configured base. endpoint = base + "/score_api.php".
static func build_endpoint(p_base_url: String) -> String:
	var b := p_base_url.strip_edges()
	while b.ends_with("/"):
		b = b.substr(0, b.length() - 1)
	return "%s/%s" % [b, ENDPOINT_FILE]

## POST body = the ScoreEntry dict PLUS seed + version, per the frozen contract.
## entry_dict is exactly Leaderboard.ScoreEntry.to_dict(). Post build-vs-ladder
## split, the `version` param carries the LADDER EPOCH ("L1", via
## GameConfig.get_board_version()), not the build string -- the server buckets
## boards by whatever lands in this column, so no schema change is needed.
## BACKEND TASK (flagged, separate): api.pdoom1.com must alias the live v0.12.0
## board to L1 so the epoch cutover does not fork the existing board.
static func build_post_body(entry_dict: Dictionary, seed: String, version: String) -> Dictionary:
	var body := entry_dict.duplicate(true)
	body["seed"] = seed
	body["version"] = version
	return body

## GET url for a board: <base>/score_api.php?seed=&version=&limit=
## `version` is the board-scope value: the ladder epoch post-split (see build_post_body).
static func build_get_url(p_base_url: String, seed: String, version: String, limit: int) -> String:
	var n: int = max(1, limit)
	return "%s?seed=%s&version=%s&limit=%d" % [
		build_endpoint(p_base_url),
		seed.uri_encode(),
		version.uri_encode(),
		n,
	]

## Parse a POST response body -> { ok, added, rank, duplicate }.
## Any malformed/error body degrades to ok=false without throwing.
static func parse_submit_response(body: String) -> Dictionary:
	var out := {"ok": false, "added": false, "rank": 0, "duplicate": false}
	var json := JSON.new()
	if json.parse(body) != OK or typeof(json.data) != TYPE_DICTIONARY:
		return out
	var data: Dictionary = json.data
	out["ok"] = bool(data.get("ok", false))
	out["added"] = bool(data.get("added", false))
	out["rank"] = int(data.get("rank", 0))
	out["duplicate"] = bool(data.get("duplicate", false))
	return out

## Parse a GET response body -> { ok, entries }, where entries is an Array of
## Leaderboard.ScoreEntry objects (the exact shape leaderboard_screen renders).
## Malformed/error body -> { ok=false, entries=[] } with no throw.
static func parse_board_entries(body: String) -> Dictionary:
	var out := {"ok": false, "entries": []}
	var json := JSON.new()
	if json.parse(body) != OK or typeof(json.data) != TYPE_DICTIONARY:
		return out
	var data: Dictionary = json.data
	if not bool(data.get("ok", false)):
		return out
	var raw = data.get("entries", [])
	if typeof(raw) != TYPE_ARRAY:
		return out
	var entries: Array = []
	for item in raw:
		if typeof(item) == TYPE_DICTIONARY:
			entries.append(Leaderboard.ScoreEntry.from_dict(item))
	out["ok"] = true
	out["entries"] = entries
	return out

# --------------------------------------------------------------------------
# Async HTTP (fire-and-forget). Each call spins up its own HTTPRequest child so
# concurrent submit + fetch don't collide, and frees it on completion.
# --------------------------------------------------------------------------

## Fire-and-forget upload. No-op (emits an "off" status) when not submitting.
## Durability: the POST body is written to the outbox BEFORE dispatch and removed only on a
## server ack, so an app-exit / crash / offline window can't lose the score.
func submit_score(entry, seed: String, version: String) -> void:
	if not should_submit():
		# Disabled / unconfigured / opted-out -> pure no-op, no HTTP.
		submit_completed.emit(false, false, 0, "")
		return
	if entry == null or not entry.has_method("to_dict"):
		submit_completed.emit(false, false, 0, "")
		return

	var body := build_post_body(entry.to_dict(), seed, version)
	_outbox_add(body)  # persist FIRST -- survives a crash between here and the server ack

	_dispatch_post(body, func(ok: bool, added: bool, rank: int):
		if ok:
			_outbox_remove(str(body.get("entry_uuid", "")))  # landed -> drop from retry queue
		var msg := ""
		if ok:
			msg = "submitted (rank %d)" % rank if rank > 0 else "submitted"
		else:
			msg = "offline -- saved locally"
		submit_completed.emit(ok, added, rank, msg)
	)

## Shared POST dispatcher. on_done is called EXACTLY once with (ok, added, rank) whether the
## request succeeds, errors, or times out -- so callers never hang and never crash. Reused by
## submit_score and by the outbox flush.
func _dispatch_post(body: Dictionary, on_done: Callable) -> void:
	if base_url.strip_edges() == "":
		if on_done.is_valid():
			on_done.call(false, false, 0)
		return
	var url := build_endpoint(base_url)
	var headers := [
		"Content-Type: application/json",
		"X-PDoom-Token: %s" % token,
	]
	var payload := JSON.stringify(body)

	var http := _new_request()
	http.request_completed.connect(
		func(result: int, code: int, _headers: PackedStringArray, resp_body: PackedByteArray):
			var ok := false
			var added := false
			var rank := 0
			if result == HTTPRequest.RESULT_SUCCESS and code == 200:
				var parsed := parse_submit_response(resp_body.get_string_from_utf8())
				ok = parsed["ok"]
				added = parsed["added"]
				rank = parsed["rank"]
			if on_done.is_valid():
				on_done.call(ok, added, rank)
			http.queue_free()
	)
	var err := http.request(url, headers, HTTPClient.METHOD_POST, payload)
	if err != OK:
		http.queue_free()
		if on_done.is_valid():
			on_done.call(false, false, 0)

# --------------------------------------------------------------------------
# Durable outbox (user://pending_scores.json). All IO is fully guarded: a missing /
# malformed / unwritable file degrades to an empty queue and never throws.
# --------------------------------------------------------------------------

func _read_outbox() -> Array:
	if not FileAccess.file_exists(OUTBOX_PATH):
		return []
	var f := FileAccess.open(OUTBOX_PATH, FileAccess.READ)
	if f == null:
		return []
	var text := f.get_as_text()
	f.close()
	var json := JSON.new()
	if json.parse(text) != OK or typeof(json.data) != TYPE_ARRAY:
		return []
	return json.data

func _write_outbox(entries: Array) -> void:
	var f := FileAccess.open(OUTBOX_PATH, FileAccess.WRITE)
	if f == null:
		push_warning("[LeaderboardSync] Could not write outbox at %s" % OUTBOX_PATH)
		return
	f.store_string(JSON.stringify(entries))
	f.close()

func _outbox_add(body: Dictionary) -> void:
	var uuid := str(body.get("entry_uuid", ""))
	var entries := _read_outbox()
	# De-dupe by entry_uuid so retries don't pile up copies of the same score.
	for e in entries:
		if typeof(e) == TYPE_DICTIONARY and str(e.get("entry_uuid", "")) == uuid and uuid != "":
			return
	entries.append(body)
	_write_outbox(entries)

func _outbox_remove(uuid: String) -> void:
	if uuid == "":
		return
	var entries := _read_outbox()
	var kept: Array = []
	for e in entries:
		if typeof(e) == TYPE_DICTIONARY and str(e.get("entry_uuid", "")) == uuid:
			continue
		kept.append(e)
	if kept.size() != entries.size():
		_write_outbox(kept)

## Retry every queued score once. Called at launch. Each landed score drops itself from the
## queue on ack; failures stay for the next launch. Silent (no status blip): this is
## background catch-up, not a live submit.
func _flush_outbox() -> void:
	if not (enabled and is_configured()):
		return  # can't reach the server right now; keep the queue for later
	var entries := _read_outbox()
	if entries.is_empty():
		return
	print("[LeaderboardSync] Flushing %d queued score(s) from a previous session." % entries.size())
	for e in entries:
		if typeof(e) != TYPE_DICTIONARY:
			continue
		var body: Dictionary = e
		var uuid := str(body.get("entry_uuid", ""))
		_dispatch_post(body, func(ok: bool, _added: bool, _rank: int):
			if ok:
				_outbox_remove(uuid)
		)

## Async board fetch. Invokes callback(ok: bool, entries: Array[ScoreEntry]).
## On any failure -> callback(false, []) so callers fall back to local silently.
func fetch_board(seed: String, version: String, limit: int, callback: Callable) -> void:
	if not can_fetch():
		if callback.is_valid():
			callback.call(false, [])
		return

	var url := build_get_url(base_url, seed, version, limit)
	var http := _new_request()
	http.request_completed.connect(
		func(result: int, code: int, _headers: PackedStringArray, resp_body: PackedByteArray):
			var ok := false
			var entries: Array = []
			if result == HTTPRequest.RESULT_SUCCESS and code == 200:
				var parsed := parse_board_entries(resp_body.get_string_from_utf8())
				ok = parsed["ok"]
				entries = parsed["entries"]
			if callback.is_valid():
				callback.call(ok, entries)
			http.queue_free()
	)
	var err := http.request(url, [], HTTPClient.METHOD_GET)
	if err != OK:
		http.queue_free()
		if callback.is_valid():
			callback.call(false, [])

func _new_request() -> HTTPRequest:
	var http := HTTPRequest.new()
	http.timeout = REQUEST_TIMEOUT_SEC
	add_child(http)
	return http
