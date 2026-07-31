# [Gate 1: LAST POUR]

**When:** Wednesday, ~1200. Legacy name: G0.

The last mechanics merge of the week enters review. Anything not in review
by the pour does not ship this league, by construction.

Note what this gate does NOT claim: not that the work is merged, only that
it is in review. Merging continues after the pour; *starting* does not.

---

## Entry criteria

- The week's lanes have pushed per step (nothing lives only in an agent's
  working tree).
- The Clerk holds a merge/park table with one row per open PR.
- The day-log for Wednesday is open and being written to.

## Mechanical checks

```
gh pr list --state open --json number,title,labels,isDraft \
  --limit 100 > docs/rituals/_snapshots/pour_$(date +%F).json   # snapshot
gh pr list --state open --limit 100                             # eyeball
```

Snapshot path is a suggestion, not a rule; what matters is that the list is
captured to a file with a timestamp, so "what was open at the pour" is a
fact afterwards rather than a memory.

| # | Check | Mechanical or judgement | Runnable now? |
|---|---|---|---|
| 1 | Open-PR list snapshotted to a timestamped file | mechanical | yes |
| 2 | Every row in the snapshot carries MERGE or PARK | judgement (Commissioner) | yes |
| 3 | Count of rows unaccounted for is zero | mechanical (against 1 and 2) | yes |
| 4 | Nothing in the PARK column is labelled league-critical | mechanical (label read) | yes |

Check 4 is new. A parked league-critical item is a contradiction: parking
means next month, and league-critical means this league cannot open without
it. It surfaced implicitly this week when #1039's four fixes were admitted
past the freeze; better to catch the class at the pour.

## The incantation

> *"The pour is closed. <N> merged, <M> parked, none unaccounted, and
> nothing parked is league-critical. What is poured is poured. The month is
> what it is."*

## Per-line provenance

| Clause | Backed by | Kind |
|---|---|---|
| "The pour is closed" | check 1 -- a timestamped snapshot exists | mechanical |
| "<N> merged, <M> parked" | check 2 -- the merge/park table | judgement, counted |
| "none unaccounted" | check 3 -- rows minus (N+M) = 0 | mechanical |
| "nothing parked is league-critical" | check 4 -- label read on the park set | mechanical |
| "What is poured is poured. The month is what it is." | nothing -- this is the declaration itself, not a claim about the world | n/a |

The last sentence is deliberately left exactly as written in playbook v0.
It is the only line in the ceremony that is a *speech act* rather than an
assertion: saying it is what makes it true. It needs no check and must not
acquire one.

## When a line is FALSE

- **Rows unaccounted for.** Do not pour. Adjudicate the stragglers -- the
  decision is cheap (merge or park) and taking it late costs the whole
  week's predictability. Re-snapshot after, so the file matches the words.
- **A parked item is league-critical.** Two legal exits, both explicit:
  (a) re-classify it as not league-critical and record why, or (b) hold the
  pour open for that one lane and record the new pour time. Do not pour
  around it silently.
- **A lane is not pushed.** Push it first. An unpushed lane cannot be
  parked, because parking means it is a review input next block and an
  unpushed branch is not an input to anything.

Slipping the pour by an hour is cheap and legal. Pouring with an
inaccurate table is not: every later gate's "what is in the month" answer
descends from this snapshot.

## Not verifiable from here

Nothing. This is the only gate whose every check runs entirely against the
repository and GitHub, at the moment it is spoken. Treat that as the
standard the other five are measured against.
