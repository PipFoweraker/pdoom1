# Number formats -- the ruling

**Status:** ACTIVE. **Ruled:** 2026-08-04 (issue #1087). **Enforced by:**
`godot/tests/unit/test_number_format_policy.gd` (fast gate).
**Implemented in:** `godot/autoload/game_config.gd` -- the ONLY place a player-facing
number is made.

## The defect this closes

From the recorded v0.13.2 playtest, [3:12], on one screen: *"months, years, and cents,
and billions"*. The turn-21 top bar carried four coexisting formats at once:

| Shown | Problem |
|---|---|
| `$197,207.69` | cents on a six-figure balance imply cent-grain decisions exist |
| `82.0 (-1.0)` | a one-decimal float implies fractional compute is meaningful |
| `* 70` | a bare int behind a star sigil that reads as a footnote marker |
| `money: 3000.0` | an internal dict key and a raw float, in a player-facing tooltip |

None of these was individually wrong. The absence of a policy was the defect:
**precision implies meaning it does not have**, and four grammars on one bar force the
player to re-learn how to read a number every time their eye moves.

## The policy

### 1. Money -- whole dollars, grouped, NEVER cents

`$197,208`. Rounded to the nearest dollar, not truncated (truncation understated the
balance: `$1,999.99` read as `$1,999`).

Rationale: no mechanic in the game trades below a dollar. A lab budget rendered to the
cent reads like a bank statement, not a strategy game -- it invites the player to look
for a decision that does not exist. If a mechanic ever DOES price in cents, this ruling
is what gets amended, in one place.

`GameConfig.format_money(amount)`

### 2. Resource scalars -- whole units, grouped

`82`, `3,400`. Compute, research, reputation, papers, staff, Attention.

Rationale: the engine carries these as floats because the simulation integrates them
continuously, but no player action is available at 0.1 grain. The decimal was engine
internals leaking through the view.

`GameConfig.format_scalar(value)`

### 3. Percentages -- one decimal (the deliberate exception)

`14.2%`. p(Doom) and other percent-denominated readouts.

Rationale: this is the one number whose fraction is load-bearing. Doom momentum is
visible at sub-point grain, and the meter, the trend sparkline and the warnings all
read against it. Dropping the decimal here would hide the signal the whole game is about.

`GameConfig.format_percent(value, decimals := 1)`

### 4. Deltas -- explicit sign, same base format

`+$1,200`, `-$238`, `+3`, `-1`. Always signed, including `+$0`, so a chip never reads as
an ambiguous bare number sitting beside a value.

A delta smaller than the display grain renders as **nothing**, not as `+0`: a rounding
artefact reads as a bug.

`GameConfig.format_money_delta(d)` / `GameConfig.format_scalar_delta(d)`

### 5. No internal dict may be dumped at a player

`money: 3000.0` was `"  %s: %s\n" % [resource, costs[resource]]` -- a debug string that
shipped. Cost and effect lines are built from the resource's player-facing NAME and its
policy-formatted amount:

`GameConfig.format_resource(key, value)` -> `Money $3,000`
`GameConfig.format_resource_delta(key, value)` -> `Reputation +5`

Unmapped internal keys are humanised (`safety_absorption` -> `Safety Absorption`) rather
than printed raw, so a new resource cannot silently leak a snake_case key.

### 6. The hard requirement

**A raw float must never reach the player.** `str(value)` and `"%s" % variant` on
anything read out of a state/cost/effect dict are how this class of bug ships. Route it
through one of the functions above.

## Enforcement

`godot/tests/unit/test_number_format_policy.gd` runs in the fast gate and holds two
kinds of guard:

1. **Behaviour** -- the formatters produce the formats ruled above, for the exact
   values from the playtest frame (`197207.69 -> $197,208`, `82.0 -> 82`,
   `format_resource("money", 3000.0) -> "Money $3,000"`).
2. **Source shape** -- a scan of `scripts/ui/**.gd` forbidding the bare `"  %s: %s\n"`
   dict-dump format string, with a meta-test proving the detector matches the line
   that actually shipped and does not match the fixed form. It is anchored to the
   whole string literal so an authored log line (`"[color=cyan]%s: %s[/color]"`,
   a label plus a message) does not false-positive.

Behaviour tests alone would not have caught this: the right function existed
(`format_money`) and the defect was code that did not call it.

## Not covered by this ruling

- **Dates and the turn counter** (`Turn 21 - Tue 1 Aug 2017`). The day-grain date beside
  a turn counter is a separate defect -- see #1041 ("Turn is counting days") and #1062.
- **Where a number sits on screen.** This is a format ruling only; no control moved.
