<?php
/**
 * Tests for server/leaderboard/score_api.php -- issue #1272.
 *
 * There is no PHP test harness in this repo (everything else is GUT/GDScript
 * or pytest), and adding PHPUnit for one file would be more machinery than the
 * file itself. So this is a dependency-free script: no composer, no extensions
 * beyond pcre + json.
 *
 * RUN:
 *   php server/leaderboard/tests/test_score_api.php
 *
 * THREE OUTCOMES, not two (same convention as scripts/run_godot_tests.py):
 *   0 = measured pass
 *   1 = measured failure
 *   2 = DID NOT COMPLETE -- no measurement was taken, so do not report a result
 *
 * The 2 exists because of a real miss during development: the PRE-FIX
 * score_api.php has no CLI guard, so `require`-ing it ran the request dispatch
 * and called exit(), and this harness returned 0 having run a third of its
 * assertions. A green exit code for a suite that never finished is the same
 * manufactured-confidence defect the endpoint itself is being fixed for, so the
 * shutdown guard below refuses to let it happen again.
 *
 * PROVE IT CAN FAIL (a test that cannot return the other answer proves nothing):
 *   git show origin/main:server/leaderboard/score_api.php > /tmp/old_api.php
 *   PDOOM_SCORE_API=/tmp/old_api.php php server/leaderboard/tests/test_score_api.php
 * Group B goes red -- a 7-row board drops to 0 rows while the API answers
 * ok:true -- and the run then ends as DID NOT COMPLETE on the require.
 *
 * ORDER MATTERS. The end-to-end group runs BEFORE the file is included,
 * because including a pre-fix copy terminates this process. End-to-end needs
 * only the file on disk.
 *
 * Touches no live data and never talks to api.pdoom1.com.
 */

// ---- tiny harness ----------------------------------------------------------
$TESTS_RUN  = 0;
$FAILURES   = [];
$REACHED_END = false;

register_shutdown_function(function () {
    global $REACHED_END, $TESTS_RUN;
    if ($REACHED_END) return;
    printf("\n%s\n", str_repeat('-', 70));
    printf("DID NOT COMPLETE -- the harness stopped after %d assertions and NO RESULT\n", $TESTS_RUN);
    printf("(the most likely cause is the API file under test calling exit() on include,\n");
    printf(" which is what a pre-fix copy without the CLI-SAPI guard does)\n");
    exit(2);
});

function ok($cond, $what) {
    global $TESTS_RUN, $FAILURES;
    $TESTS_RUN++;
    if ($cond) {
        printf("  ok   %s\n", $what);
    } else {
        printf("  FAIL %s\n", $what);
        $FAILURES[] = $what;
    }
}

function eq($actual, $expected, $what) {
    $pass = ($actual === $expected);
    ok($pass, $what . ($pass ? '' : sprintf(
        "\n         expected: %s\n         actual:   %s",
        var_export($expected, true), var_export($actual, true))));
}

function group($name) { printf("\n== %s ==\n", $name); }

// ---- the strings that actually did this ------------------------------------
// Byte-for-byte the value still sitting on the live (weekly-2026-w32, L4)
// board, and the 41-byte submission it came from. Mirrors LIVE_AMPUTATED /
// LIVE_FULL_LAB in the game repo's
// godot/tests/unit/test_leaderboard_identity_fields.gd.
const LIVE_FULL_LAB  = 'GRIM (Global Risk Intervention Mechanism)';
const LIVE_AMPUTATED = 'GRIM (Global Risk Intervention Mechanism';

// A name whose byte 40 lands INSIDE a UTF-8 sequence. 'a' + 20 x e-acute
// (2 bytes each) = 41 bytes, so a byte cut at 40 splits the final e-acute.
// This is the exact shape that emptied a 7-row board on 2026-08-10.
function splitting_name() { return 'a' . str_repeat("\xC3\xA9", 20); }

// 20 x e-acute = 40 bytes, so the cut lands ON a boundary. Measured to be
// stored normally by the old code -- proof the trigger is the SPLIT, not
// merely being non-ASCII.
function on_boundary_name() { return str_repeat("\xC3\xA9", 20); }

/** What the OLD code did, reproduced so the defect is visible in the test. */
function old_style_cut($s) { return substr($s, 0, 40); }

$API_PATH = getenv('PDOOM_SCORE_API') ?: (dirname(__DIR__) . '/score_api.php');
if (!is_file($API_PATH)) {
    fwrite(STDERR, "cannot find score_api.php at $API_PATH\n");
    $REACHED_END = true;
    exit(2);
}
printf("score_api.php under test: %s\n", $API_PATH);
printf("php %s (%s)\n", PHP_VERSION, PHP_SAPI);

// ============================================================================
group('A. the defect is real, and it is the byte cut that causes it');
// ============================================================================

eq(strlen(LIVE_FULL_LAB), 41, 'the submitted lab name is 41 bytes');
eq(old_style_cut(LIVE_FULL_LAB), LIVE_AMPUTATED,
   'the old byte cut reproduces the live board value, bracket eaten');
ok(json_encode(old_style_cut(LIVE_FULL_LAB)) !== false,
   'that one still encodes -- pure ASCII, so it only LOOKS harmless');

eq(strlen(splitting_name()), 41, 'the splitting name is 41 bytes');
ok(json_encode(old_style_cut(splitting_name())) === false,
   'THE BUG: the old byte cut of a multibyte name cannot be json_encode()d');
eq(json_last_error(), JSON_ERROR_UTF8, 'and it fails specifically as malformed UTF-8');

eq(strlen(on_boundary_name()), 40, 'the on-boundary name is 40 bytes');
ok(json_encode(old_style_cut(on_boundary_name())) !== false,
   'a cut landing ON a codepoint boundary was always fine (the trigger is the split)');

// The step that made the old bug fatal rather than merely wrong.
$tmp = tempnam(sys_get_temp_dir(), 'p1272');
$fp = fopen($tmp, 'c+');
fwrite($fp, '[{"score":1},{"score":2},{"score":3}]');
ftruncate($fp, 0); rewind($fp);
$n = @fwrite($fp, json_encode(['name' => old_style_cut(splitting_name())]));
fflush($fp); fclose($fp);
eq($n, 0, 'fwrite($fp, false) reports 0 bytes written -- NOT false, so a === false check misses it');
eq(file_get_contents($tmp), '',
   'so truncate-then-encode leaves the board file empty: the whole league gone');
unlink($tmp);

// ============================================================================
group('B. end-to-end over real HTTP: one name must not empty the board');
// ============================================================================
// Runs BEFORE the require below, because including a pre-fix score_api.php
// terminates this process.

function free_port() {
    $sock = @stream_socket_server('tcp://127.0.0.1:0', $errno, $errstr);
    if (!$sock) return 0;
    $name = stream_socket_get_name($sock, false);
    fclose($sock);
    return (int)substr($name, strrpos($name, ':') + 1);
}

/** Raw HTTP over a socket: no curl extension needed, and we see the exact body length. */
function http_request($port, $method, $path, $headers = [], $body = null) {
    $fp = @fsockopen('127.0.0.1', $port, $errno, $errstr, 10);
    if (!$fp) return [0, '', 'connect failed: ' . $errstr];
    stream_set_timeout($fp, 15);

    $req = "$method $path HTTP/1.1\r\nHost: 127.0.0.1:$port\r\nConnection: close\r\n";
    foreach ($headers as $k => $v) $req .= "$k: $v\r\n";
    if ($body !== null) $req .= 'Content-Length: ' . strlen($body) . "\r\n";
    $req .= "\r\n";
    if ($body !== null) $req .= $body;

    fwrite($fp, $req);
    $raw = '';
    while (!feof($fp)) {
        $chunk = fread($fp, 8192);
        if ($chunk === false || $chunk === '') break;
        $raw .= $chunk;
    }
    fclose($fp);

    $split = strpos($raw, "\r\n\r\n");
    if ($split === false) return [0, '', 'no header/body split'];
    $head = substr($raw, 0, $split);
    $resp = substr($raw, $split + 4);
    $status = 0;
    if (preg_match('#^HTTP/1\.[01] (\d{3})#', $head, $m)) $status = (int)$m[1];
    return [$status, $resp, $head];
}

function submit($port, $token, $seed, $ver, $name, $score, $uuid) {
    $body = json_encode([
        'seed' => $seed, 'version' => $ver, 'score' => $score,
        'doom_integral' => $score * 10, 'player_name' => $name,
        'entry_uuid' => $uuid,
    ]);
    return http_request($port, 'POST', '/score_api.php',
        ['X-PDoom-Token' => $token, 'Content-Type' => 'application/json'], $body);
}

function board_entries($port, $seed, $ver) {
    list($st, $body,) = http_request($port, 'GET',
        "/score_api.php?seed=$seed&version=$ver&limit=100");
    $d = json_decode($body, true);
    return [$st, $body, (is_array($d) && isset($d['entries'])) ? $d['entries'] : null];
}

$TOKEN    = 'test-token-not-a-real-secret';
$e2e_root = sys_get_temp_dir() . '/p1272_root_' . getmypid();
$e2e_data = sys_get_temp_dir() . '/p1272_data_' . getmypid();
@mkdir($e2e_root, 0775, true);
@mkdir($e2e_data, 0775, true);
copy($API_PATH, $e2e_root . '/score_api.php');

$port  = free_port();
$proc  = null;
$pipes = [];
if ($port > 0) {
    $cmd = escapeshellarg(PHP_BINARY) . ' -S 127.0.0.1:' . $port . ' -t ' . escapeshellarg($e2e_root);
    $env = $_ENV;
    $env['PDOOM_SCORE_TOKEN'] = $TOKEN;
    $env['PDOOM_SCORE_DIR']   = $e2e_data;
    $env['PATH']       = getenv('PATH');
    $env['SystemRoot'] = getenv('SystemRoot');   // Windows needs this for sockets
    $proc = @proc_open($cmd, [0 => ['pipe','r'], 1 => ['pipe','w'], 2 => ['pipe','w']],
                       $pipes, $e2e_root, $env);
}

$up = false;
if (is_resource($proc)) {
    for ($i = 0; $i < 100; $i++) {
        $probe = @fsockopen('127.0.0.1', $port, $en, $es, 1);
        if ($probe) { fclose($probe); $up = true; break; }
        usleep(100000);
    }
}
ok($up, "the built-in php -S server came up on port $port");

if ($up) {
    $SEED = 'test-1272';
    $VER  = 'Ltest';

    // Seven honest rows, the size of the board that was actually destroyed.
    for ($i = 1; $i <= 7; $i++) {
        submit($port, $TOKEN, $SEED, $VER, "Lab Number $i", 100 - $i, "uuid-$i");
    }
    list(, , $before) = board_entries($port, $SEED, $VER);
    eq(is_array($before) ? count($before) : -1, 7,
       'seven rows are on the board before the dangerous submission');

    // The submission that used to empty it.
    list($pst, $pbody,) = submit($port, $TOKEN, $SEED, $VER, splitting_name(), 42, 'uuid-danger');
    ok($pst === 200, "the splitting-name POST is accepted (HTTP $pst)");

    list(, , $after) = board_entries($port, $SEED, $VER);
    $after_n = is_array($after) ? count($after) : -1;
    ok($after_n !== 0, 'THE REGRESSION: the board was NOT emptied by one submitted name');
    eq($after_n, 8, 'and it holds all seven originals plus the new row');

    $stored = null;
    foreach (($after ?: []) as $e) {
        if (($e['entry_uuid'] ?? '') === 'uuid-danger') $stored = $e['player_name'];
    }
    ok($stored !== null, 'the dangerous row is on the board, not silently dropped');
    if ($stored !== null) {
        ok(strlen($stored) <= 40, 'the stored name is within the 40-byte budget');
        ok(json_encode($stored) !== false, 'the stored name is valid UTF-8');
        ok(substr($stored, -3) === '...', 'the stored name carries a visible cut marker');
    }

    // The POST response tells the client what actually landed.
    $pd = json_decode($pbody, true);
    ok(isset($pd['player_name']), 'the POST response reports the stored player_name');

    // A second, unauthenticated trigger: a stray byte in the seed used to make
    // GET return HTTP 200 with a zero-byte body. Verified against the deployed
    // api.pdoom1.com on 2026-08-24.
    list($bst, $bbody,) = http_request($port, 'GET', '/score_api.php?seed=%FF&version=L4&limit=1');
    ok(strlen($bbody) > 0,
       "a bad-encoding seed returns a body, not an empty 200 (HTTP $bst, " . strlen($bbody) . ' bytes)');
    eq($bst, 400, 'and it is a 400, not a cheerful 200');

    // A board file that is already damaged must not be silently overwritten.
    $cs    = 'test-1272-corrupt';
    $cpath = $e2e_data . "/board_{$cs}__{$VER}.json";
    file_put_contents($cpath, 'CORRUPT NOT JSON');
    list($cst,,) = submit($port, $TOKEN, $cs, $VER, 'Someone', 50, 'uuid-c');
    eq($cst, 500, 'submitting onto an unreadable board is refused');
    eq(file_get_contents($cpath), 'CORRUPT NOT JSON',
       'and the damaged file is left as it was, not overwritten with one row');

    list($gst, $gbody,) = http_request($port, 'GET', "/score_api.php?seed=$cs&version=$VER&limit=5");
    eq($gst, 500, 'reading an unreadable board is an error, not a cheerful empty list');
    ok(strpos($gbody, '"entries":[]') === false,
       'an unreadable board is never rendered as "nobody has played"');
}

if (is_resource($proc)) {
    foreach ($pipes as $p) { if (is_resource($p)) fclose($p); }
    proc_terminate($proc);
    proc_close($proc);
}

// ============================================================================
group('C. helpers (score_api.php included under the CLI SAPI)');
// ============================================================================
// Anything below this line is unreachable against a pre-fix copy, which is why
// the shutdown guard reports DID NOT COMPLETE rather than a green exit.

require $API_PATH;

ok(function_exists('fit_utf8'), 'fit_utf8() exists');
ok(function_exists('is_utf8'), 'is_utf8() exists');
ok(function_exists('load_board'), 'load_board() exists');

// is_utf8() must agree with json_encode(), since json_encode() is the thing
// that actually blows up. If the two ever disagree, the fix has a hole.
$utf8_cases = [
    'ascii'             => 'abc',
    'valid 2-byte'      => "\xC3\xA9",
    'valid 4-byte'      => "\xF0\x9F\x92\xA9",
    'lone continuation' => "\xA9",
    'lone 0xFF'         => "\xFF",
    'truncated 2-byte'  => "abc\xC3",
    'truncated 3-byte'  => "abc\xE2\x82",
    'overlong'          => "\xC0\xAF",
    'surrogate half'    => "\xED\xA0\x80",
];
foreach ($utf8_cases as $label => $s) {
    eq(is_utf8($s), json_encode($s) !== false,
       "is_utf8() agrees with json_encode() on: $label");
}

// ============================================================================
group('D. fit_utf8() never splits a codepoint, and marks the cut');
// ============================================================================

eq(fit_utf8('short', 40, '...'), 'short', 'a name that fits is returned untouched');
eq(fit_utf8(on_boundary_name(), 40, '...'), on_boundary_name(),
   'a name of exactly 40 bytes is untouched (no gratuitous marker)');

$fitted = fit_utf8(splitting_name(), 40, '...');
ok(strlen($fitted) <= 40, 'the fitted splitting name is within the 40-byte budget');
ok(json_encode($fitted) !== false,
   'THE FIX: the fitted splitting name json_encode()s -- no wipe possible');
ok(substr($fitted, -3) === '...', 'and the cut is VISIBLE, not silent');

$fitted_lab = fit_utf8(LIVE_FULL_LAB, 40, '...');
ok($fitted_lab !== LIVE_AMPUTATED,
   'the real 41-byte lab name no longer reproduces the silently amputated live value');
// A 40-byte budget minus the 3-byte marker leaves 37 bytes of name.
eq($fitted_lab, 'GRIM (Global Risk Intervention Mechan...',
   'it now reads as truncated instead of as a typo');
eq(strlen($fitted_lab), 40, 'and it uses the full budget, marker included');

// The exhaustive form of "never splits a codepoint", across all four sequence
// widths and every budget.
$mixed = 'ab' . "\xC3\xA9" . "\xE2\x82\xAC" . "\xF0\x9F\x92\xA9" . str_repeat("\xC3\xA9\x41", 20);
$all_ok = true;
$bad_budget = -1;
for ($budget = 1; $budget <= strlen($mixed); $budget++) {
    $f = fit_utf8($mixed, $budget, '...');
    if (strlen($f) > $budget || json_encode($f) === false) {
        $all_ok = false; $bad_budget = $budget; break;
    }
}
ok($all_ok, 'fit_utf8() holds at EVERY budget from 1 to ' . strlen($mixed) .
            ' over mixed 1/2/3/4-byte codepoints' .
            ($all_ok ? '' : " (first failure at budget $bad_budget)"));

// ============================================================================
group('E. load_board() distinguishes "empty" from "unreadable"');
// ============================================================================

$dir = sys_get_temp_dir() . '/p1272_' . getmypid();
@mkdir($dir, 0775, true);

eq(load_board($dir . '/does_not_exist.json'), [],
   'a board that does not exist yet is genuinely empty');

file_put_contents($dir . '/empty.json', '');
eq(load_board($dir . '/empty.json'), [],
   'a zero-byte board is genuinely empty (this is what a past wipe leaves behind)');

file_put_contents($dir . '/corrupt.json', 'this is not json at all');
eq(load_board($dir . '/corrupt.json'), null,
   'an unparseable board returns null, NOT [] -- damaged is not the same as quiet');

file_put_contents($dir . '/good.json', '[{"score":5}]');
eq(load_board($dir . '/good.json'), [['score' => 5]], 'a good board loads');

// ---- cleanup ---------------------------------------------------------------
foreach ([$dir, $e2e_root, $e2e_data] as $d) {
    if (is_dir($d)) {
        foreach (glob($d . '/*') as $f) { @unlink($f); }
        @rmdir($d);
    }
}

// ---- report ----------------------------------------------------------------
printf("\n%s\n", str_repeat('-', 70));
printf("%d assertions, %d failed\n", $TESTS_RUN, count($FAILURES));
$REACHED_END = true;
if ($FAILURES) {
    foreach ($FAILURES as $f) printf("  FAILED: %s\n", $f);
    exit(1);
}
printf("PASS\n");
exit(0);
