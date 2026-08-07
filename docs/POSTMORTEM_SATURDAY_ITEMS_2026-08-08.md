# Saturday postmortem -- items logged live, awaiting Pip's context

Logged as they happen so the context is not reconstructed later. Pip supplies the
"why" on Saturday; this file supplies the "what", timestamped and evidenced.

---

## ITEM 1 -- Truncated lab names on the public leaderboard

**Logged 2026-08-08 ~01:05 AEST, at Pip's request.** His words:

> "Ahhhh truncated lab things eh? this is ironic. Please note it in the logs and
> I'll saturday postmortem the context as to why."

**PIP TO SUPPLY: why this is ironic.** He has context this seat does not, and he
has asked to provide it himself rather than have it guessed at. Do not fill this
in speculatively -- the whole point of logging it now is that the reason is his.

### The measured facts, so the context has something to attach to

The leaderboard's `player_name` column is populated from
`GameConfig.lab_name`, not `player_name` -- `game_over_screen.gd:280-282`:

```gdscript
var entry = Leaderboard.ScoreEntry.new(
    final_turns,
    GameConfig.lab_name,     # lands in the field named player_name
```

`GameConfig.player_name` exists (`DEFAULT_PLAYER_NAME := "Researcher"`, line 10),
is persisted (line 246), is loaded (line 309) and is settable (line 396). **PR
#1133 built an identity prompt and a lab-name generator, and the leaderboard reads
neither.**

The API then truncates with `substr` at approximately 40 characters. Pip's entry
is on the live `(weekly-2026-w32, L4)` board right now, reading:

```
GRIM (Global Risk Intervention Mechanism
```

Cut mid-word, closing bracket lost. The lab-name generator produces expanded
bacronyms precisely BECAUSE the expansion is the joke, and the expansion is the
part the truncation removes.

### Why it is on the Saturday list rather than fixed tonight

Pip: *"I'm not asking for it now it just feels silly."* He named the absurdity
rather than setting a deadline. The ruling he DID make is recorded below and is
being implemented within safe limits tonight.

### Ruled by Pip, 2026-08-08 ~01:00

> "can we submit both? I feel like this has been mentioned a lot this week.
> players will collide on lab names and player names are also cool because then a
> player can have different labs?"

**BOTH -- player name and lab name as separate values.** Reasoning: lab names
collide (a good generator makes names two people both pick), and **one player with
many labs is a supported thing the board should be able to express.** A single
conflated field destroys that permanently.

Constraints this creates, being worked now: the ~40-char server limit will not
hold two names, so either the client fits deliberately or the API changes -- and
an API change is `pdoom1-website` territory, routed through coordination, not
solved in this repo. The live board also already holds rows whose `player_name`
is a lab name, so adding a field is a migration, not an edit.

### The generalisation worth testing on Saturday

Three defects tonight share one shape: **a field whose name and contents
disagree.** `player_name` holding a lab name; `duration_seconds` reading 2.8-10s
for 147-turn runs because `game_start_time` is never set on the live path; and
`[Unreleased]` in `CHANGELOG.md` accumulating across five releases. In each case
every check passed, because a check compares a value to itself and none of them
compares a value to its own label.

Related, from the `pdoom1-website` seat the same night: the version sync writes
`data/current-game-version.json` while the site serves `public/data/version.json`
-- **a producer and a consumer with no overlapping filename.** That one never
worked at all, not once, and nothing on either side ever went red.
