<?php
/**
 * P(Doom)1 leaderboard API -- minimal, low-volume, flat-file JSON store.
 * Runs on plain Dreamhost shared PHP (no framework, no DB required).
 *
 * Endpoints (single file):
 *   GET  score_api.php?seed=<seed>&version=<ver>&limit=<n>
 *        -> { ok, seed, version, entries: [ top-n sorted ] }
 *   POST score_api.php   (JSON body, header X-PDoom-Token: <shared secret>)
 *        body = a score entry (see $ALLOWED_FIELDS); -> { ok, added, rank }
 *
 * Scoring order (ADR-0002): primary = score (turns survived) DESC,
 * tiebreak = doom_integral DESC. Boards are keyed by (seed, game_version).
 *
 * Storage: DATA_DIR/board_<seed>__<version>.json  (in-place write under flock).
 * The website repos can read those JSON files directly.
 *
 * DEPLOY: upload this file somewhere web-served (e.g. ~/pdoom1.com/api/),
 * set SHARED_TOKEN + DATA_DIR below (DATA_DIR should be OUTSIDE the web root
 * or protected, so the raw files aren't world-writable-guessable), then point
 * the game at the URL. See README.md.
 *
 * ---------------------------------------------------------------------------
 * ONE SUBMITTED NAME USED TO EMPTY THE BOARD (#1272, fixed 2026-08-24).
 *
 * The old code cut player_name with byte-wise substr($s, 0, 40) and then wrote
 * the board as `ftruncate($fp, 0); fwrite($fp, json_encode($entries));`.
 * json_encode() returns false on malformed UTF-8, and the truncate had already
 * happened, so the sequence was:
 *
 *   1. a name arrives whose byte 40 lands INSIDE a UTF-8 sequence
 *   2. substr() cuts it there, producing bytes that are not valid UTF-8
 *   3. ftruncate() empties the board file
 *   4. json_encode() returns false, and fwrite($fp, false) writes ""
 *   5. the response is still {"ok":true,"added":true,"rank":N}
 *
 * Measured against the deployed endpoint on a throwaway board 2026-08-10: a
 * 7-row board went to 0 rows while the API answered ok:true. Measured again
 * locally 2026-08-24: fwrite($fp, false) returns int(0), NOT false -- so even
 * `if (fwrite(...) === false)` would not have caught it. The write check below
 * compares against strlen() for that reason.
 *
 * Three rules now hold, and tests/test_score_api.php pins all three:
 *   - encode BEFORE truncating; an encode failure must leave the board alone
 *   - cut on a CODEPOINT boundary, never a byte boundary, and mark the cut
 *   - "I could not read/encode this board" is never rendered as "[]", because
 *     an empty board is indistinguishable from a quiet day
 * ---------------------------------------------------------------------------
 */

// ---- config ----------------------------------------------------------------
$SHARED_TOKEN = getenv('PDOOM_SCORE_TOKEN') ?: 'CHANGE_ME_set_a_long_random_token';
$DATA_DIR     = getenv('PDOOM_SCORE_DIR')   ?: (__DIR__ . '/data');
$MAX_ENTRIES  = 100;    // per board
$MAX_BODY     = 8192;   // bytes; reject anything larger

// Name budget, in BYTES, matching what the client fits to
// (Leaderboard.compose_board_name / fit_board_name in the pdoom1 game repo).
// Raising this is a coordinated change: the client fits to the same number, so
// bump both or the client keeps cutting early for no reason.
$MAX_NAME_BYTES = 40;
$CUT_MARKER     = '...';   // ASCII on purpose: house style, and 3 known bytes

$ALLOWED_FIELDS = [
    'score', 'doom_integral', 'player_name', 'operator_name', 'date',
    'level_reached', 'game_mode', 'duration_seconds', 'entry_uuid',
    'baseline_score', 'baseline_doom_integral',
];

// Fields that carry player-typed text and therefore get length-fitted.
$NAME_FIELDS = ['player_name', 'operator_name'];

// ---- helpers ---------------------------------------------------------------

function fail($code, $msg) {
    http_response_code($code);
    $body = json_encode(['ok' => false, 'error' => $msg]);
    // Even the error path must not emit an empty body -- an empty 200/500 is
    // exactly the silence this endpoint is being fixed for.
    if ($body === false) $body = '{"ok":false,"error":"error message could not be encoded"}';
    echo $body;
    exit;
}

/** Emit a success payload, or a loud error rather than PHP's silent "". */
function respond($payload) {
    $body = json_encode($payload);
    if ($body === false) fail(500, 'response encode failed: ' . json_last_error_msg());
    echo $body;
    exit;
}

/**
 * Is $s valid UTF-8?
 *
 * Deliberately NOT mb_check_encoding(): mbstring is not guaranteed on shared
 * hosting (and is absent from the stock Windows CLI build these tests run on).
 * preg_match('//u', ...) returns false with PREG_BAD_UTF8_ERROR on malformed
 * input using PCRE's own UTF-8 validator, which needs no extension beyond pcre.
 * Measured 2026-08-24 to agree with json_encode() on all nine probe cases
 * (lone continuation byte, lone 0xFF, truncated 2/3-byte sequences, overlong
 * encoding, surrogate half, and the three valid cases).
 */
function is_utf8($s) {
    return preg_match('//u', (string)$s) === 1;
}

/**
 * Fit $s into $max_bytes bytes WITHOUT ever splitting a UTF-8 codepoint.
 *
 * Returns the string unchanged when it already fits. Otherwise cuts to
 * ($max_bytes - strlen($marker)) bytes, walks the cut back until what remains
 * is valid UTF-8 (at most 3 steps, since no codepoint is longer than 4 bytes),
 * and appends $marker so the player can SEE that the name was shortened. The
 * old silent byte cut is why the live board still reads
 * "GRIM (Global Risk Intervention Mechanism" with the bracket eaten.
 *
 * Caller must have established that $s is valid UTF-8 to begin with.
 */
function fit_utf8($s, $max_bytes, $marker = '...') {
    $s = (string)$s;
    if (strlen($s) <= $max_bytes) return $s;

    if (strlen($marker) > $max_bytes) $marker = '';
    $budget = $max_bytes - strlen($marker);

    $cut = substr($s, 0, $budget);
    // Drop trailing bytes until the remainder is valid UTF-8 again. Uses the
    // same validator as the encode check, so the two cannot disagree.
    while ($cut !== '' && !is_utf8($cut)) {
        $cut = substr($cut, 0, -1);
    }
    return $cut . $marker;
}

function safe_key($s) {
    // keep boards keyed to a safe filename fragment
    $s = substr((string)$s, 0, 64);
    return preg_replace('/[^A-Za-z0-9._-]/', '_', $s);
}

function board_path($dir, $seed, $version) {
    $seed = safe_key($seed !== '' ? $seed : 'default');
    $ver  = safe_key($version !== '' ? $version : 'none');
    return "$dir/board_{$seed}__{$ver}.json";
}

/**
 * Read a board.
 *
 * Returns an array of entries, or NULL when the board exists but could not be
 * read or parsed. The null is the point: the old version returned [] for that
 * case, which renders "this file is damaged" as "nobody has played". A board
 * that does not exist yet, or is legitimately zero bytes, is genuinely empty
 * and still returns [].
 */
function load_board($path) {
    if (!is_file($path)) return [];
    $raw = file_get_contents($path);
    if ($raw === false) return null;
    if (trim($raw) === '') return [];
    $data = json_decode($raw, true);
    return is_array($data) ? $data : null;
}

// ADR-0002 order: score DESC, then doom_integral DESC
function cmp_entries($a, $b) {
    $as = (int)($a['score'] ?? 0); $bs = (int)($b['score'] ?? 0);
    if ($as !== $bs) return $bs - $as;
    return (int)($b['doom_integral'] ?? 0) - (int)($a['doom_integral'] ?? 0);
}

// Under the bare CLI SAPI this file is being INCLUDED by
// tests/test_score_api.php, which wants the helpers above and none of the
// request handling below. A real request never arrives under 'cli' -- Dreamhost
// serves PHP as cgi-fcgi/fpm, and the test harness's own end-to-end pass uses
// `php -S`, which reports 'cli-server'. So this cannot short-circuit production.
if (PHP_SAPI === 'cli') { return; }

// ---- request handling ------------------------------------------------------
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *'); // fine for public read-only scores
header('Access-Control-Allow-Headers: X-PDoom-Token, Content-Type');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

if (!is_dir($DATA_DIR)) { @mkdir($DATA_DIR, 0775, true); }
if (!is_dir($DATA_DIR)) fail(500, 'data dir missing');

// ---- GET: top-N ------------------------------------------------------------
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $seed    = (string)($_GET['seed']    ?? 'default');
    $version = (string)($_GET['version'] ?? 'none');
    // These are echoed straight back in the response. Unvalidated, a query
    // string carrying a stray byte (?seed=%FF) made json_encode() below return
    // false and PHP echo it as "" -- a 200 with a zero-byte body. Verified
    // against the deployed endpoint 2026-08-24; no token needed to trigger it.
    if (!is_utf8($seed) || !is_utf8($version)) fail(400, 'seed/version is not valid UTF-8');

    $limit   = max(1, min(100, (int)($_GET['limit'] ?? 20)));
    $entries = load_board(board_path($DATA_DIR, $seed, $version));
    if ($entries === null) fail(500, 'board unreadable; refusing to report it as empty');

    usort($entries, 'cmp_entries');
    respond([
        'ok' => true, 'seed' => $seed, 'version' => $version,
        'entries' => array_slice($entries, 0, $limit),
    ]);
}

// ---- POST: submit ----------------------------------------------------------
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $tok = $_SERVER['HTTP_X_PDOOM_TOKEN'] ?? '';
    if (!hash_equals($SHARED_TOKEN, $tok)) fail(403, 'bad token');

    $raw = file_get_contents('php://input', false, null, 0, $MAX_BODY + 1);
    if (strlen($raw) > $MAX_BODY) fail(413, 'body too large');
    $in = json_decode($raw, true);
    if (!is_array($in)) fail(400, 'bad json');

    $seed    = $in['seed']    ?? ($in['game_seed'] ?? 'default');
    $version = $in['version'] ?? ($in['game_version'] ?? ($in['game_mode'] ?? 'none'));

    // whitelist fields
    $entry = [];
    foreach ($GLOBALS['ALLOWED_FIELDS'] as $f) {
        if (array_key_exists($f, $in)) $entry[$f] = $in[$f];
    }
    if (!isset($entry['score'])) fail(400, 'missing score');
    $entry['score'] = (int)$entry['score'];
    $entry['doom_integral'] = (int)($entry['doom_integral'] ?? 0);

    // Same default as before (?? fires on absent OR null). An empty string is
    // left alone deliberately: rows with an empty name already sit on the live
    // (weekly-2026-w32, L4) board, and rewriting them here would be a separate
    // change smuggled into a data-loss fix.
    if (!isset($entry['player_name'])) $entry['player_name'] = 'Unknown Lab';
    // Fit every player-typed field on a codepoint boundary. json_decode() above
    // already guarantees valid UTF-8, so the is_utf8() guard is belt-and-braces
    // -- but a rejected submission is cheap and a wiped league is not.
    foreach ($GLOBALS['NAME_FIELDS'] as $f) {
        if (!array_key_exists($f, $entry)) continue;
        $entry[$f] = (string)$entry[$f];
        if (!is_utf8($entry[$f])) fail(400, "$f is not valid UTF-8");
        $entry[$f] = fit_utf8($entry[$f], $GLOBALS['MAX_NAME_BYTES'], $GLOBALS['CUT_MARKER']);
    }

    $path = board_path($DATA_DIR, $seed, $version);
    $fp = fopen($path, 'c+');
    if (!$fp) fail(500, 'cannot open board');
    flock($fp, LOCK_EX);
    $raw_existing = stream_get_contents($fp);
    $entries = json_decode($raw_existing, true);
    if (!is_array($entries)) {
        if (trim($raw_existing) !== '') {
            // Non-empty and unparseable. Carrying on with [] would make the
            // damage PERMANENT on the very next write, which is how a read
            // failure turns into data loss. Refuse instead.
            flock($fp, LOCK_UN); fclose($fp);
            fail(500, 'board unreadable; refusing to overwrite it');
        }
        $entries = [];
    }

    // de-dupe by entry_uuid (idempotent re-submits)
    $uuid = $entry['entry_uuid'] ?? '';
    if ($uuid !== '') {
        foreach ($entries as $e) {
            if (($e['entry_uuid'] ?? '') === $uuid) {
                usort($entries, 'cmp_entries');
                $rank = 0; foreach ($entries as $i => $e2) { if (($e2['entry_uuid'] ?? '') === $uuid) { $rank = $i + 1; break; } }
                flock($fp, LOCK_UN); fclose($fp);
                respond(['ok' => true, 'added' => false, 'duplicate' => true, 'rank' => $rank]);
            }
        }
    }

    $entries[] = $entry;
    usort($entries, 'cmp_entries');
    $entries = array_slice($entries, 0, $GLOBALS['MAX_ENTRIES']);
    $rank = 0; foreach ($entries as $i => $e) { if (($e['entry_uuid'] ?? '') === $uuid) { $rank = $i + 1; break; } }

    // ENCODE FIRST. Nothing above this line has touched the file, so a failure
    // here costs one submission instead of the whole league (#1272).
    $json = json_encode($entries);
    if ($json === false) {
        flock($fp, LOCK_UN); fclose($fp);
        fail(500, 'encode failed, board left intact: ' . json_last_error_msg());
    }

    ftruncate($fp, 0); rewind($fp);
    $written = fwrite($fp, $json);
    if ($written !== strlen($json)) {
        // Short write (disk full, quota). fwrite returns int|false, and it
        // returned int(0) rather than false in the original bug, so compare
        // lengths rather than checking === false. We still hold the lock and
        // the previous bytes are in memory: put them back.
        ftruncate($fp, 0); rewind($fp);
        fwrite($fp, $raw_existing);
        fflush($fp); flock($fp, LOCK_UN); fclose($fp);
        fail(500, 'short write, board restored to its previous contents');
    }
    fflush($fp); flock($fp, LOCK_UN); fclose($fp);

    respond([
        'ok' => true, 'added' => ($rank > 0), 'rank' => $rank,
        // What actually landed, so the client can tell the player when the
        // server shortened the name instead of leaving them to discover it on
        // the public board.
        'player_name' => $entry['player_name'],
    ]);
}

fail(405, 'method not allowed');
