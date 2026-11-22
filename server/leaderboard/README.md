# P(Doom)1 leaderboard server (Dreamhost, minimal)

A single PHP file, no framework, no DB required -- built for low volume + simple text up/down.
Storage is flat JSON files keyed by `(seed, game_version)` (ADR-0002), which the pdoom website
repos can read directly.

## How hard is this? (Pip's question)
Low. It's ~one file + two config lines + an upload. No server process to run -- Dreamhost shared
hosting serves PHP on request. No DB unless you want one later.

## Deploy (5 minutes)
1. Pick a location under a web-served dir on the pdoom1 domain, e.g. `~/pdoom1.com/api/`.
2. Upload `score_api.php` there (SFTP / Dreamhost file manager).
3. Set two things (env vars via `.htaccess` `SetEnv`, or edit the two `getenv(...) ?:` defaults at
   the top of the file):
   - `PDOOM_SCORE_TOKEN` -- a long random string. The game sends it as header `X-PDoom-Token` on
     POST so randoms can't spam the board. (Read/GET is public.)
   - `PDOOM_SCORE_DIR` -- a writable data dir, ideally OUTSIDE the web root (e.g.
     `~/pdoom1-scoredata/`) so raw board files aren't directly fetchable. Default is `./data`.
4. Test:
   - `curl "https://pdoom1.com/api/score_api.php?seed=default&version=v0.11.0"` -> `{"ok":true,...}`
   - POST test:
     ```
     curl -X POST -H "X-PDoom-Token: YOURTOKEN" -H "Content-Type: application/json" \
       -d '{"seed":"default","version":"v0.11.0","score":42,"doom_integral":1000,"player_name":"Test Lab","entry_uuid":"abc-123"}' \
       https://pdoom1.com/api/score_api.php
     ```
5. Hand Claude the URL + token; the Godot client gets wired to it (an HTTPRequest).

## Tests -- run these before you upload anything

    php server/leaderboard/tests/test_score_api.php

Dependency-free: no composer, no PHPUnit, only the `pcre` + `json` extensions
that every PHP build has. It boots PHP's built-in `php -S` over a COPY of the
API in a temp docroot with a temp data dir, so it drives real HTTP and touches
neither live data nor api.pdoom1.com.

**Three outcomes, not two** (same convention as `scripts/run_godot_tests.py`):
`0` = measured pass, `1` = measured failure, `2` = **DID NOT COMPLETE**. Exit 2
means no measurement was taken -- do not report a suite result from that run.

To see the suite return the other answer (a test that cannot fail proves
nothing):

    git show <pre-1272-rev>:server/leaderboard/score_api.php > /tmp/old_api.php
    PDOOM_SCORE_API=/tmp/old_api.php php server/leaderboard/tests/test_score_api.php

Group B goes red: a 7-row board drops to **0 rows** while the API answers
`{"ok":true,"added":true,"rank":8}`.

## DEPLOY IS MANUAL, AND NOTHING IN THIS REPO CHECKS IT

There is no deploy path from this repo to api.pdoom1.com. Editing this file and
merging changes NOTHING that a player touches -- the fix ships only when someone
uploads it. Verify a deploy landed with a GET, not with a green CI run:

    curl "https://api.pdoom1.com/score_api.php?seed=%FF&version=L4&limit=1"

Pre-#1272 that returns **HTTP 200 with a zero-byte body** (measured 2026-08-24).
Once the fix is deployed it returns HTTP 400 with a JSON error. That one request
distinguishes the deployed version from the repo version without a POST and
without touching any board.

## API
- `GET  ?seed=&version=&limit=` -> `{ ok, seed, version, entries: [...] }` (top-N, score DESC, doom_integral tiebreak).
- `POST` (JSON body, `X-PDoom-Token` header) -> `{ ok, added, rank }`. Idempotent on `entry_uuid`.

Accepted body fields (whitelisted): score, doom_integral, player_name, operator_name, date,
level_reached, game_mode, duration_seconds, entry_uuid, baseline_score, baseline_doom_integral,
plus seed + version. `player_name` and `operator_name` are fitted to 40 BYTES on a codepoint
boundary, with a visible `...` when shortened; the POST response echoes the stored `player_name`.
An unknown key is still accepted and dropped.

## Website integration
The board files are plain JSON (`board_<seed>__<version>.json`). The pdoom website can read them
directly off disk / via a read-only PHP include, no game API needed.

## Anti-cheat (staged)
- v1 (now): shared-secret token on POST. Good enough at low volume + not fussed about it.
- v2 (later): the engine is deterministic with replay -- submit `(seed, action_log)` and have the
  server re-simulate to VALIDATE the claimed score. Strong, but a separate build.
