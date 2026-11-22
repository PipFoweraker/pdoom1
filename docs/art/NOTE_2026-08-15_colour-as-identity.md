# Note -- colour as identity: groupings, bindings, and multi-colour signatures

> **Status: captured intent, nothing ruled.** Dictated by Pip on the morning of
> 2026-08-15, in the same memo that produced
> `docs/game-design/DESIGN_2026-08-15_backlog-as-teacher.md`. Two unrelated
> subjects shared one recording; they are filed apart on purpose.
>
> Pip's words are quoted. Everything under **Proposal** is this seat's addition
> and is not his ruling. Nothing here changes
> `docs/art/PALETTE_AND_DOOM_INTENSITY.md`, which remains the live spec.

## The want, in Pip's words

The trigger was v0.14.1 reading as **"cohering"** on a play-through -- the
build where things stacking up first felt right -- and the thought went straight
to colour as the thing that could carry that coherence further.

> "something maybe like the boundaries or the bindings of the, or the groupings
> around icons might be able to subtly link to colors in a way that then cards
> can and subtly linked to colors."

> "maybe figuring out ways to collect sets of color patches so that things in
> the game have more than one color or more than one color and color combination
> representing their identities."

> "There's probably some math or some like color selection, the grouping theory
> that Wanasai and I can work through where we can come up with some numbers
> that we derive through a system that is like elegant and coherent."

Two things are being asked for at once, and they are separable:

1. **Colour as a binding across surfaces.** The chrome around an icon -- its
   boundary, its grouping frame -- carries a colour, and the card that belongs
   to the same family carries it too. The link is meant to be *subtle*: a
   quiet rhyme a player half-notices, not a legend to be read.
2. **Identity as a colour set, not a colour.** A thing in the game may be
   entitled to more than one colour, or to a *combination*, so identity is
   expressed as a small patch-set rather than a single swatch.

The second is the harder and more interesting claim, because it turns palette
work into a combinatorics problem: how many distinguishable multi-colour
signatures can be drawn from a shared set, under the constraint that the whole
thing still looks like one world.

## The named collaborator and the named method

Pip wants this worked through **with Wanasai, in person, when Wanasai is in
town** -- specifically the "grouping theory" and the derivation of the numbers,
so the palette comes out of a system rather than out of taste applied swatch by
swatch. Wanasai already appears in the art record as a source of direction
(`docs/art/NOTES_BRIEF.md`, the `wanasai_calls` prompt group).

He also floated capturing it:

> "here's something where I wanna like, do you wanna just get one slide down in
> front of a computer and just like record interviews with her opinions about
> this."

That is the same interview-extraction method that produced
`docs/game-design/DESIGN_PHILOSOPHY.md`, pointed at a second person. Worth
noting it is a *consent* question in a way the solo memos are not.

## Constraints this must not break

These are already ruled elsewhere and any colour-identity system inherits them:

- **"Doom is a layer, not a repaint"** (`PALETTE_AND_DOOM_INTENSITY.md`). If a
  thing's identity is a colour set, that set must survive doom escalation. Doom
  intensity may glow *around* an identity signature; it may not overwrite it,
  or the signature stops being an identity.
- **Two registers, one world** -- cozy office and dark dread are the same world
  at different doom levels. A signature scheme has to read in both.
- **No emoji, ASCII chrome** (issue #744). Colour cannot be offloaded onto
  pictographs; the bindings and grouping frames are what is available to carry
  it.
- Colour alone can never be the *only* channel for a gameplay-relevant
  distinction. Accessibility aside, the CRT-amber register compresses hue hard
  at high doom.

## Proposal -- what to bring to the session with Wanasai

Marked as this seat's suggestion, not Pip's.

- Bring the question in its combinatoric form: **how many identity classes do
  we actually need signatures for?** Count them from the game before choosing
  any maths. If the answer is nine, a scheme that generates ninety is the wrong
  scheme.
- Decide first whether a signature is **ordered** (primary + accent, where
  swapping the two makes a different identity) or **unordered** (a set). That
  single choice changes the available count by a factor and is cheaper to
  settle in conversation than in code.
- Bring `docs/art/palette.json` as evidence of what the existing hero art
  actually contains, not as a proposal. It is an extraction from an image, and
  its `role_guess` labels are guesses.
- Ask what the scheme does when a thing changes family mid-run. Identity that
  cannot migrate is a weaker system than one that can, and the answer
  constrains the maths.

## Open questions

- Does the icon-boundary treatment and the card treatment share one token, or
  are they two treatments that merely agree? A shared token is cheaper and
  harder to tune per-surface.
- Is the multi-colour signature a *player-facing* language (learnable, load-
  bearing for decisions) or purely a coherence device? Pip said "subtly",
  twice, which points at coherence -- but the two demand different amounts of
  contrast discipline, so it should be answered before the maths.
- Recording the Wanasai session: agreed in principle by Pip, not yet asked of
  Wanasai.

## Related

- `docs/art/PALETTE_AND_DOOM_INTENSITY.md` -- the live palette and doom-layer spec
- `docs/art/NOTES_BRIEF.md` -- prompt groups including `wanasai_calls`
- `docs/GODOT_UI_COLOR_IMPLEMENTATION.md`, `docs/UI_COLOR_SCHEME_RECOMMENDATIONS.md`
- `docs/game-design/DESIGN_2026-08-15_backlog-as-teacher.md` -- the other half of the same memo
