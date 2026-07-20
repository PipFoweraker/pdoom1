# Voice and legibility scan (outside-critic pass) -- 2026-07-20

> An uninvested outside read of the whole game surface, classifying elements:
> common/legible (carries newcomers) vs load-bearing weird (distinctly ours,
> amplify) vs confusing-weird (weird without payoff -- translate or cut) vs
> generic filler (adds nothing). Structural headline: THE DISTINCTIVE VOICE
> LIVES ALMOST ENTIRELY IN SURFACES PLAYERS DO NOT SEE (achievements strings,
> researcher quirks, design docs) while the shipped player-facing text (events,
> actions) is mostly generic management-sim filler, and the flagship identity
> systems (Ledger player-facing UI, doom legibility payoff) are engine-built
> but not yet rendered. Ship bucket-2 voice into the actual events, re-skin or
> delete bucket-4, and the playable game becomes what the docs promise.

## 1. Common / legible -- keep, they carry newcomers
- Tycoon verb set: hire researchers, raise money, publish, buy compute.
- Doomsday-Clock-style doom gauge (doom_meter.gd) -- universally read.
- Choose-your-consequence event popups with explicit deltas (Reigns/CK format).
- Seed leaderboard + turns-survived score (roguelike ladder framing).
- Crisis staples (PR campaign, raises, counter-offer) -- legible if generic.
- The office cat.

## 2. Load-bearing weird -- distinctly ours, amplify
- No victory condition; only time bought (ADR-0002; score = turns survived,
  doom-integral tiebreak). Genuinely unusual; the thesis.
- The achievements register -- best-written words in the repo, e.g. "Still
  Here: 2027 -- ... You are a footnote with staff."; "Peer Reviewed --
  Reviewer 2 had concerns. Humanity gains a PDF."; "White Knuckles -- Doom
  passed 90. You filed the paperwork anyway." (autoload/achievements.gd:30-49)
- Liability Ledger: every mitigation is a loan, compounding interest, secret
  entries carry a blackmail rider. Real mechanical identity -- NOT yet
  player-facing.
- Attention as founder currency ("Attention Is All You Need" pun, played
  straight); reserve evaporates monthly, no banking.
- Death attribution: "the game must explain your death before it kills you" --
  wired into defeat subtitle; the full chain not yet rendered (see UX teardown).
- Researcher quirks: insider AI-safety-culture texture (Secret Successionist,
  e/acc Sympathizer, Doom Absolutist) (data/researchers/quirks.json).
- Cozy-grimdark: warm office under a quietly bleeding sky; cat hides at high
  doom (TONE_AND_ART.md).
- Meta-honesty framing: sandbox for a live research question; teaching by
  incidental contact; made by an AI-safety person partly with AI agents.

## 3. Confusing-weird -- translate or cut
- Dual economy: legacy action_points coexisting with Attention; events still
  say "costs 1 AP". Half-finished migration reading as incoherence (L2/#613
  deletes AP).
- "The turn is a month" vs turn = workday tick: over-theorized nomenclature
  relative to player-perceived payoff.
- "No printed doom deltas" philosophy while shipped events print doom deltas
  everywhere -- confusion in both directions until data is re-authored.
- "Nine-stream doom" that is not nine streams -- dev-facing precision-anxiety.
- Game-over jargon without gloss: momentum "Spiral"/"Flywheel" (Flywheel for
  FALLING doom is counter-intuitive at the moment it appears).

## 4. Generic filler -- re-skin or delete
- The HR/workplace event suite (Interpersonal Conflict, Pay Equity Concerns,
  Equipment Gone Missing, Workplace Complaint...) -- flat rep deltas, no
  AI-safety specificity; reads like a purchased event pack.
- Bare 4X-tycoon strategic actions (Corporate Espionage, Acquire Startup) --
  zero voice.
- Exclamation-mark tycoon copy fighting the dread tone ("AI Breakthrough! ...
  unexpected AI capability advancement!").
- Stock incidents (Media Scandal, Critical System Failure, Budget Overrun).

## 5. Top first-session perplexities
1. "I always lose" -- load-bearing; needs a framing beat or it reads broken.
2. The flagship system is invisible (Ledger engine-built, no UI) -- the
   biggest gap: first sessions meet bucket 4, not bucket 2.
3. AP vs Attention vs turn-vs-month -- incidental jank, not designed weird.
4. Doom will not go down and you cannot tell why -- intentional model,
   mis-delivered until breakdown/attribution renders.
5. Tonal whiplash between earnest HR events and deadpan achievements.

## 6. Marketing: sell vs hide
Sell: "You cannot win. You can only last longer."; achievements deadpan as
literal screenshots; bleeding-sky-over-cozy-office key art + the cat; the
Ledger framed as loans-with-blackmail-riders; researcher quirks gif;
Attention-Is-All-You-Need; "the game explains your death before it kills you."
Hide: AP/Attention dual economy; turn/month nomenclature; printed-delta
contradiction; the HR event pack; do not trailer the Ledger UI until it exists.

## 7. Honest audience paragraph
The real audience is an intersection, not a union: AI-safety/rationalist
culture fluency AND taste for punishing legibly-fair loss-ladder games AND
bureaucratic-deadpan-over-catastrophe humour (Papers Please, Cultist Simulator,
Frostpunk). The in-group texture is a draw inside that intersection and noise
outside it -- a trade already explicitly chosen. The honest risk is not the
weirdness; it is that the distinctive weirdness currently lives in docs,
achievement strings, and stubs while the playable surface is disproportionately
generic filler.

Key files: voice that works: godot/autoload/achievements.gd,
godot/data/researchers/quirks.json. Voice missing: godot/data/events/
core_events.json, godot/data/actions/strategic.json. Thesis + gaps:
docs/game-design/DESIGN_PHILOSOPHY.md, docs/ARCHITECTURE.md section 3,
godot/docs/design/TONE_AND_ART.md.
