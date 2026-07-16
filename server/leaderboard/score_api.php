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
    $entry['player_name'] = substr((string)($entry['player_name'] ?? 'Unknown Lab'), 0, 40);

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

    ftruncate($fp, 0); rewind($fp);
    fwrite($fp, json_encode($entries));
    fflush($fp); flock($fp, LOCK_UN); fclose($fp);

    echo json_encode(['ok' => true, 'added' => ($rank > 0), 'rank' => $rank]);
    exit;
}

fail(405, 'method not allowed');
