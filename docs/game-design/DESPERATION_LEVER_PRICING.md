# The desperation lever is priced CRUDELY and on purpose

**Ruled by Pip, 2026-08-22:** *"we need to give the mechanical inertness a definite
fix-by date. And I'd rather have a bad thing in there now, unsubtle, rather than
no thing, and we can balance it later. players need to suffer."*

## What was wrong

`doom.streams.action_desperation_absorb` was **0.0**. Two player-reachable levers
read it:

| Lever | Where |
|---|---|
| `desperation_lever` quick action | `godot/scripts/core/actions.gd` |
| `desperation_payroll` financing offer | `godot/scripts/core/finance_engine.gd` |

Both plant a **secret, compounding governance liability** (`payroll_coinflip`,
severity 1200-2000, on a fuse). Both bought, numerically, **nothing**.

So the trap could never spring. A rational player never pulls a lever that costs a
compounding secret debt and delivers zero, which means the liability -- the
interesting half, the ADR-0003 teeth -- had no way to reach anybody. **An option
with a real cost and no benefit is not a hard choice; it is a dead button**
(the #595 shape).

Before this, `finance_engine` also *told* the player it delivered "-10 doom now"
and wrote to the inert sink that `turn_manager` clobbers every resolve (#967).
That lie is fixed separately; this file is about the number.

## The number, and why this one

**25.0 flat.** Anchored against the existing `doom.streams.*` pricing layer:

| Key | Value | Shape |
|---|---|---|
| `action_safety_absorb` | 4.0 | **x safety_researchers** |
| `action_audit_absorb` | 1.0 | flat |
| `action_desperation_absorb` | **25.0** | flat |

**Flat is the load-bearing choice, not the magnitude.** You reach for desperation
when you are weak and short-staffed -- which is exactly when a per-researcher
scale pays out least. A lever that works only for labs who do not need it is the
same dead button in a different costume.

25.0 is roughly six safety researchers' worth of one `safety_research` action. It
is meant to be a **visible gulp of relief** followed by a bill. It is NOT
calibrated: no sweep was run, and the 72-run L1 sweep that priced the rest of
`doom.streams` (`DOOM_STREAMS_v1.md`) did not cover it because it was zero.

**Expect it to be wrong.** It is deliberately unsubtle so that being wrong is
VISIBLE in play rather than invisible in a spreadsheet.

## The fix-by date

COMMITMENT: 2026-09-19 -- Balance the desperation lever: play or sweep the 25.0 flat `doom.streams.action_desperation_absorb` against the compounding `payroll_coinflip` liability it buys, and either calibrate it or record that 25.0 survived contact -- owner: pip -- kind: review -- note: priced crudely and deliberately on 2026-08-22 to replace a 0.0 that made both desperation levers dead buttons; the number is uncalibrated and expected to be wrong.

Dated **after v0.15 ships (Sep 4)** so the number gets real play in a real release,
and **before v0.16 (Oct 2)** so it cannot ride two epochs uncalibrated. Both dates
from `docs/ROADMAP.md`.

## What "players need to suffer" means here, mechanically

The suffering was never missing -- `payroll_coinflip` is a secret liability that
compounds on a fuse and surfaces through the ledger's exposure roll. What was
missing was a **reason to take it**, and therefore any path by which the suffering
reached a player.

Pricing the relief makes the trap live: the lever now genuinely helps, which is
what makes accepting the hidden debt a real decision rather than an obvious no.

## What would tell us 25.0 is wrong

- **Too high:** the lever becomes a routine doom-management tool and the ledger
  entry reads as a mild tax. Watch for runs that pull it every time it is offered.
- **Too low:** nobody pulls it and the liability still never lands -- the original
  defect at a different value. Watch for runs that never pull it.
- Either way the answer is a number, not an argument, and the date above is when
  somebody goes and gets it.
