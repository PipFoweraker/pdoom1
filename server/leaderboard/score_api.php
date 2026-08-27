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
 * Storage: DATA_DIR/board_<seed>__<version>.json  (atomic write + flock).
 * The website repos can read those JSON files directly.
 *
 * DEPLOY: upload this file somewhere web-served (e.g. ~/pdoom1.com/api/),
 * set SHARED_TOKEN + DATA_DIR below (DATA_DIR should be OUTSIDE the web root
 * or protected, so the raw files aren't world-writable-guessable), then point
 * the game at the URL. See README.md.
 */

// ---- config ----------------------------------------------------------------
$SHARED_TOKEN = getenv('PDOOM_SCORE_TOKEN') ?: 'CHANGE_ME_set_a_long_random_token';
$DATA_DIR     = getenv('PDOOM_SCORE_DIR')   ?: (__DIR__ . '/data');
$MAX_ENTRIES  = 100;    // per board
$MAX_BODY     = 8192;   // bytes; reject anything larger

// Longest stored player_name, in BYTES.
//
// MUST stay equal to Leaderboard.BOARD_NAME_MAX_BYTES in
// godot/scripts/leaderboard.gd; tools/check_board_name_budget.py fails the
// commit if the two drift, because the two disagreeing is precisely the bug
// this number was raised to fix.
//
// This was 40, and 40 was arbitrary. Nothing here needed it: a board is at most
// $MAX_ENTRIES rows of a few hundred bytes, and $MAX_BODY already caps a POST at
// 8192. But the game trusted it as an external law -- the client comment said
// this file "is in no repo here" -- and spent two issues dividing 40 between a
// lab name and an operator name, which is how the live weekly-2026-w33 board
// came to publish "Bureau of Catastrophe... -- Pip" with the "..." stored as
// data.
//
// The value is now the client's derived worst case: a 50-character lab plus
// " -- " plus a 30-character operator, at 4 bytes per UTF-8 codepoint. It is
// therefore never reached by a submission from the game, and the cut below is a
// backstop against anything that is not the game.
$MAX_NAME_BYTES = 324;

$ALLOWED_FIELDS = [
    'score', 'doom_integral', 'player_name', 'date', 'level_reached',
    'game_mode', 'duration_seconds', 'entry_uuid', 'baseline_score',
    'baseline_doom_integral',
];

// ---- helpers ---------------------------------------------------------------
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *'); // fine for public read-only scores
header('Access-Control-Allow-Headers: X-PDoom-Token, Content-Type');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');

function fail($code, $msg) {
    http_response_code($code);
    echo json_encode(['ok' => false, 'error' => $msg]);
    exit;
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
function load_board($path) {
    if (!is_file($path)) return [];
    $raw = file_get_contents($path);
    $data = json_decode($raw, true);
    return is_array($data) ? $data : [];
}
/**
 * Cut $s to at most $max BYTES without ever splitting a UTF-8 codepoint.
 *
 * WHY THIS IS NOT substr(). A byte-wise substr can end mid-codepoint and leave
 * a malformed string. json_encode() then returns FALSE on that string -- and
 * the POST handler below used to ftruncate(0) the board file BEFORE encoding,
 * so a single such submission wrote nothing and DESTROYED THE ENTIRE BOARD
 * while the response still said {"ok":true}. Measured 2026-08-10: a 7-row
 * throwaway board went to 0 rows, rank reported as 7.
 *
 * Two independent guards now stand between a name and that outcome: this
 * function (never emit a split codepoint) and the encode-before-truncate check
 * in the writer (never blank a board because encoding failed). Either alone
 * would have prevented it; a public board is worth both.
 *
 * No mbstring dependency on purpose -- this runs on whatever PHP Dreamhost
 * shared hosting happens to offer.
 */
function fit_name_bytes($s, $max) {
    $s = (string)$s;
    if (strlen($s) <= $max) return $s;
    $cut = substr($s, 0, $max);
    $len = strlen($cut);
    // Walk back over continuation bytes (10xxxxxx) to the lead byte of the
    // sequence the cut landed in.
    $j = $len;
    while ($j > 0 && (ord($cut[$j - 1]) & 0xC0) === 0x80) { $j--; }
    if ($j > 0) {
        $lead = ord($cut[$j - 1]);
        $need = 1;
        if      (($lead & 0x80) === 0x00) $need = 1;  // ASCII
        else if (($lead & 0xE0) === 0xC0) $need = 2;
        else if (($lead & 0xF0) === 0xE0) $need = 3;
        else if (($lead & 0xF8) === 0xF0) $need = 4;
        // Sequence incomplete inside the cut -> drop it whole.
        if (($len - ($j - 1)) < $need) return substr($cut, 0, $j - 1);
    }
    return $cut;
}

// ADR-0002 order: score DESC, then doom_integral DESC
function cmp_entries($a, $b) {
    $as = (int)($a['score'] ?? 0); $bs = (int)($b['score'] ?? 0);
    if ($as !== $bs) return $bs - $as;
    return (int)($b['doom_integral'] ?? 0) - (int)($a['doom_integral'] ?? 0);
}

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

if (!is_dir($DATA_DIR)) { @mkdir($DATA_DIR, 0775, true); }
if (!is_dir($DATA_DIR)) fail(500, 'data dir missing');

// ---- GET: top-N ------------------------------------------------------------
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $seed    = $_GET['seed']    ?? 'default';
    $version = $_GET['version'] ?? 'none';
    $limit   = max(1, min(100, (int)($_GET['limit'] ?? 20)));
    $entries = load_board(board_path($DATA_DIR, $seed, $version));
    usort($entries, 'cmp_entries');
    echo json_encode([
        'ok' => true, 'seed' => $seed, 'version' => $version,
        'entries' => array_slice($entries, 0, $limit),
    ]);
    exit;
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
    $entry['player_name'] = fit_name_bytes(
        $entry['player_name'] ?? 'Unknown Lab', $GLOBALS['MAX_NAME_BYTES']);

    $path = board_path($DATA_DIR, $seed, $version);
    $fp = fopen($path, 'c+');
    if (!$fp) fail(500, 'cannot open board');
    flock($fp, LOCK_EX);
    $raw_existing = stream_get_contents($fp);
    $entries = json_decode($raw_existing, true);
    if (!is_array($entries)) $entries = [];

    // de-dupe by entry_uuid (idempotent re-submits)
    $uuid = $entry['entry_uuid'] ?? '';
    if ($uuid !== '') {
        foreach ($entries as $e) {
            if (($e['entry_uuid'] ?? '') === $uuid) {
                usort($entries, 'cmp_entries');
                $rank = 0; foreach ($entries as $i => $e2) { if (($e2['entry_uuid'] ?? '') === $uuid) { $rank = $i + 1; break; } }
                flock($fp, LOCK_UN); fclose($fp);
                echo json_encode(['ok' => true, 'added' => false, 'duplicate' => true, 'rank' => $rank]);
                exit;
            }
        }
    }

    $entries[] = $entry;
    usort($entries, 'cmp_entries');
    $entries = array_slice($entries, 0, $GLOBALS['MAX_ENTRIES']);
    $rank = 0; foreach ($entries as $i => $e) { if (($e['entry_uuid'] ?? '') === $uuid) { $rank = $i + 1; break; } }

    // ENCODE BEFORE TRUNCATING. The old order was ftruncate(0) then
    // fwrite(json_encode(...)); json_encode() returns FALSE on malformed UTF-8
    // anywhere in the board, fwrite(false) writes the empty string, and the
    // whole board is gone -- with {"ok":true} on the way back. Measured on a
    // throwaway board 2026-08-10. If encoding fails now, the file on disk is
    // still untouched and the caller is told the truth.
    $json = json_encode($entries);
    if ($json === false) {
        flock($fp, LOCK_UN); fclose($fp);
        fail(500, 'refusing to write: board would be emptied (json_encode failed)');
    }

    ftruncate($fp, 0); rewind($fp);
    fwrite($fp, $json);
    fflush($fp); flock($fp, LOCK_UN); fclose($fp);

    echo json_encode(['ok' => true, 'added' => ($rank > 0), 'rank' => $rank]);
    exit;
}

fail(405, 'method not allowed');
