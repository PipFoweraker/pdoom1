# Voice variant kit -- finding the professional-pdoom register

> Status: DRAFT for Pip, 2026-07-26. Purpose: answer the register question BY
> RECORDING, not by deciding upfront. One 30-minute session, one fixed
> passage, several registers, then a pick. Two-take rule throughout: this is
> a probe, not a studio day.

## The fixed passage (~85 words, ~34s at 2.5 w/s)

Read THIS, identically, in every register. It deliberately contains wry lines
("argue about at parties", "There is a cat.") and one earnest line ("I
genuinely think...") so registers differentiate audibly:

    There's a number AI researchers argue about at parties -- the
    probability that this all goes horribly wrong. I made it into a
    strategy game. You run a safety lab. Doom is a system, not a score.
    Every mitigation is a loan, and the ledger always collects. Your
    researchers have quirks. Some of them leak. There is a cat.
    I genuinely think games can help us reason about this risk.
    Play it, lose, and tell me what broke.

## The registers (record in this order)

| id | Register | One-line direction |
|----|----------|--------------------|
| a | deadpan-dark documentary | Flat, unhurried, let the dark lines sit; think narrator who has seen things. |
| b | earnest indie-dev | Warm, direct, slightly faster; you're telling a friend what you built and why it matters. |
| c | wry-but-warm educator | Half-smile audible; lands jokes without leaning on them; teacherly confidence. |
| d | free take | Whatever feels like YOU after a/b/c. Often the winner. |

Two takes per register, straight through, mistakes and all (flub -> repeat the
sentence -> keep going; never stop the recording). 8 takes total, ~15 min of
tape.

## Recording procedure (Audacity, once per session)

1. Same room, same mic position as you'll always use. Door closed, fan off.
2. Audacity: Project Rate 48000 Hz (bottom-left). Record 5s of room silence
   FIRST (this is your noise profile; keep it at the head of the session).
3. Record all 8 takes in one long track, saying "REGISTER A, TAKE ONE" etc.
   before each -- slate out loud, it makes splitting trivial.
4. Effect > Noise Reduction: Get Profile on the silence, apply defaults to
   the whole track. Once. Do not fiddle further.
5. Export per take: File > Export Audio, WAV 48kHz, into
   `G:/tmp/pdoom1-video-masters/voice-variants-2026-07/` named
   `a_1.wav, a_2.wav, b_1.wav ... d_2.wav`. Also export one MP3 per register
   (best take) for easy phone listening.
6. Stop at 30 minutes regardless of state. Incomplete beats overworked.

## Self-review rubric (next day, fresh ears, phone speaker)

Score each register 1-5 on:
- SUSTAINABLE: could I do 10 minutes of this without strain?
- IDENTITY: does this sound like the person who made THIS game?
- MEMORY: play best-takes to one friend, unlabelled; which line do they quote
  back an hour later, and from which register?
- CRINGE-PROOF: still fine on the third listen?

## Decision rule

Pick ONE dominant register (highest total; SUSTAINABLE breaks ties -- a
register you can't repeat weekly is a trap). Keep ONE accent register for
contrast moments (e.g. deadpan for doom lines inside an earnest video).
Write the pick as one line in ROLE_CREATIVE_DIRECTOR.md ("House register:
X, accent: Y") -- that line is the whole style guide for voice.

## Why this works [craft rationale]

Register chosen by audition beats register chosen by argument: the mouth
knows things the planner doesn't, the fixed passage isolates the variable
(same words, same mic, same day), and the friend-memory test measures the
only thing that matters downstream -- what listeners retain.
