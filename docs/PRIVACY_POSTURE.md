# Privacy Posture -- the two-tier consent model (SSOT)

**Ruled by Pip 2026-07-26** (identity-consent ruling + approved ping-decoupling,
PR #942). This file is the canonical statement of what the shipped game sends,
under what consent, and why. If code and this file disagree, one of them is a
bug -- fix whichever is wrong and keep this file current (anti-policy-rot
instruction, Pip 2026-07-26).

Related: [`PRIVACY.md`](PRIVACY.md) (player-facing policy, older and broader),
repo-root `user_privacy.json` (machine-readable posture record + legacy
Python-era values), issues #799 (launch call) / #940 (metrics stubs).

## The two tiers

The model separates two DIFFERENT consent classes. The rationale: sharing
**who you are** (identity) and being **counted anonymously** are not the same
decision, so they get different defaults and different gates. Leaderboard
opt-in does NOT gate the ping, and ping opt-out does NOT touch the
leaderboard.

### Tier 1 -- identity-carrying data (explicit opt-in)

**What:** player name + lab name + score, submitted to the global leaderboard.

**HOW the two names are published (measured, PR #1176, 2026-08-10).** Both names
are public, and they travel as ONE composed string inside the frozen wire field
`player_name`, formatted `LAB -- OPERATOR` (e.g. `GRIM -- Pip`). There is no
separate operator field on the server: an unknown extra key is accepted with
HTTP 200 and then silently dropped by the API's `$ALLOWED_FIELDS` whitelist, so
composition is the only route by which a player's own name reaches a public
board. Consequences worth stating in a privacy document:

- The Operator name is rendered publicly, verbatim, beside the lab name. It is
  NOT a local-only value.
- The composed string is fitted CLIENT-SIDE to the board's measured 40-byte
  budget and marked with `...` when cut, so a long name is published truncated
  rather than amputated by the server.
- A run with no Operator name submits the lab alone, byte-identical to the
  pre-#1176 shape. Legacy rows are never back-filled with a fabricated operator.

**Consent:** EXPLICIT opt-in at the point of first submission -- the first time
a run reaches score submission, a one-time prompt asks the player to confirm
(game-over screen, `ConfirmationDialog`). Flipping the Settings toggle counts
as the same explicit choice. Until that click happens, nothing
identity-carrying leaves the machine.

**Rules:**
- Both answers are remembered locally (`user://config.cfg`:
  `leaderboard/consent_asked` + `leaderboard/submit_scores_global`) and
  changeable any time in Settings ("Submit scores to global leaderboard
  (shares player + lab name)").
- A player with EMPTY name/lab who reaches submission un-opted-in gets ONE
  gracious reminder ever (persisted `leaderboard/reminder_shown`); later
  playthroughs stay silent. No hounding.
- Declining never affects local play: local scores always save and display
  regardless of consent state.
- Viewing the global board is read-only and un-gated.

**Code:** `godot/autoload/leaderboard_sync.gd` (`should_submit`,
`consent_flow_state`), `godot/scripts/ui/game_over_screen.gd` (prompt +
reminder), `godot/scripts/ui/settings_menu.gd`,
`godot/autoload/game_config.gd`, and `godot/scripts/leaderboard.gd`
(`ScoreEntry.to_wire_dict` + `Leaderboard.compose_board_name` -- this is the
file that decides the exact shape of what leaves the machine, so a change there
is a change to this posture).

### Tier 2 -- anonymous telemetry (default ON, honest opt-out)

**What:** one launch ping per session to `analytics.pdoom1.com/api/event`
(#799): a random UUIDv4 install id + game version + OS name + first-launch
flag. Nothing else, ever.

**Rules:**
- The install id is random, persisted only to `user://install_id.txt`, and
  NEVER derived from hardware, MAC, username, or anything about the machine.
  Reinstall regenerates it; that is by design (it counts installs, it is not a
  device fingerprint).
- Default ON, with an honestly-labelled Settings toggle: "Anonymous launch
  ping (counts installs; no personal data)" (`privacy/send_launch_ping`).
- The payload is a whitelist pinned by a regression test
  (`godot/tests/unit/test_update_check.gd`,
  `test_ping_body_carries_nothing_else`): adding ANY field forces the privacy
  conversation first.
- No PII, no machine ids, no retries, no client-side state beyond the install
  id and normal config.
- The update CHECK (GET of the public static version feed) carries no
  identifiers at all and sits behind no toggle.

**Code:** `godot/autoload/update_check.gd` (`should_send_ping`,
`build_ping_body`).

## Decoupling ruling (2026-07-26, approved by Pip)

Historically the ping was AND-gated with the leaderboard opt-out. Under the
identity-consent model the leaderboard gate means IDENTITY consent
specifically, and the ping carries no identity -- so the ping now honours only
its own toggle. Pip approved this interpretation explicitly ("approve your
subtle correction to privacy processing").

## Migration note

Pre-ruling configs persisted `submit_scores_global=true` (the old default-ON
alpha posture) without any explicit click. `consent_asked` defaults false, so
those players get the one-time prompt at their next game over, and the
Settings toggle displays OFF until a real choice is made.
