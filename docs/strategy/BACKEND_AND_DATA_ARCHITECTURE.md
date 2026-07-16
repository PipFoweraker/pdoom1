# pdoom backend + data architecture -- settled decision

> Status: SETTLED (2026-07-17), open to revision. Written so the parallel repos
> (pdoom1-website, pdoom-data, pdoom1-webclient) can align to one shared plan --
> prompted by the pdoom1-website agent flagging **backend fragmentation across score paths**.
> Companion to `docs/strategy/HOSTING_AND_RELEASE.md` (the cost/benefit land-spelling).

## The decision, in one line
**One score/data backend, implemented in PHP, behind a frozen HTTP contract. No parallel score
paths.**

## Why (the fragmentation risk)
Multiple repos want game data (website, data, webclient). If each grows its own score endpoint /
language / shape, they drift and break. The fix is to settle **one implementation** and, more
importantly, **one contract** everything codes to.

## What is settled
1. **Implementation language: PHP.** The pdoom score/data API layer is PHP (`server/leaderboard/
   score_api.php` is the reference). Not Node, not a second Django service. (CVTas stays Django --
   it is a *separate app*, not the pdoom data layer. Don't conflate them.)
2. **The HTTP contract is frozen** (below). Hosting location may change; the contract may not,
   except by a versioned, announced change.
3. **One score path.** The game POSTs scores and GETs boards through this API only. The website
   READS the same data (either via the API's GET, or directly off the board JSON files on disk).
   There is no second score writer.

## The frozen contract (v1)
Base: `https://<host>/score_api.php` (host TBD -- shared subdomain now, a real box later).
- `GET ?seed=<s>&version=<v>&limit=<n>` -> `{ ok, seed, version, entries: [ ... ] }`
  entries sorted by `score` (turns) DESC, `doom_integral` DESC (ADR-0002).
- `POST` (JSON body; header `X-PDoom-Token: <shared secret>`) -> `{ ok, added, rank }`.
  Idempotent on `entry_uuid`.
- Board key: **(seed, game_version)** -- ADR-0002 #5. Balance patches rotate the meta; old scores
  never rank against a new version.
- Entry fields (whitelisted): score, doom_integral, player_name, date, level_reached, game_mode,
  duration_seconds, entry_uuid, baseline_score, baseline_doom_integral (+ seed, version).
- Storage: `board_<seed>__<version>.json` -- plain JSON the website can read directly.

Any consumer (website, webclient, dashboards) codes to THIS. Changes are versioned (`/v2/...`),
never silent.

## Data planes (keep these distinct)
| plane | what | owner | how others consume |
|---|---|---|---|
| **Scores** | leaderboard entries | the PHP score API (this doc) | GET the API, or read `board_*.json` |
| **pdoom-data** | the curated datasets (improving over time) | pdoom-data repo | its own read endpoint(s), also PHP, same host |
| **Website** | presentation | pdoom1-website repo | consumes both of the above read-only |
The website does not write scores; pdoom-data does not serve scores; the game writes only scores.

## Hosting (settled direction, not urgent)
- **Now:** `score_api.php` on a shared-hosting subdomain (`api.pdoom1.com` or similar). Gets
  scores flowing today. $0 marginal.
- **Soon:** one PHP-capable backend box (DreamCompute 2GB ~$12/mo, or Hetzner+Coolify ~$5/mo) as the
  home for the score API + pdoom-data read APIs. Same contract -> moving hosts changes nothing
  downstream.
- **Web-client pivot:** Godot exports to web; static-host the client free; it points at the same
  API. No new backend needed. (See HOSTING_AND_RELEASE.md.)

## What this asks of the parallel repos
- **pdoom1-website:** read scores via the GET contract or the board JSON; do NOT stand up a second
  score store. Agreed with your fragmentation concern -- this is the settle.
- **pdoom-data:** serve datasets as read APIs on the same PHP host; keep it separate from scores.
- **pdoom1-webclient:** when it exists, it is a Godot web export pointing at this same API.

## Open (for Pip + the agents)
- Final host + subdomain name.
- Whether pdoom-data read APIs live in the same PHP file/dir or a sibling.
- Anti-cheat beyond the shared-secret token (later: deterministic-replay validation -- the server
  re-simulates seed+action-log to verify a claimed score).

## Next stately-cleanup pass
Once blessed, fold this + HOSTING_AND_RELEASE into the main architecture docs (a proper ADR for the
backend) so it's discoverable next to the game-design ADRs.
