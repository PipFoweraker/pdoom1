# SEED: The Rival + Narrative Pressure ("Developments") -- design seed

> **What this is.** A LOSSLESS capture of Pip's 2026-07-25 brain dump on (a) the
> rival antagonist system and (b) the narrative-pressure layer he wants to call
> **"Developments"** (rival-specific subtype: **"Sightings"**). This is a RAW
> DESIGN SEED, not decided canon. It exists so nothing is lost before it can be
> workshopped.
>
> **Feeds:** WS-3 mechanics workshop (issue #811, Wed 2026-07-30).
>
> **Voice tags** (same convention as `docs/copy/COPY_CORPUS.md`):
> `[PIP]` = verbatim quote from Pip; `[CLAUDE-note]` = agent inference /
> secretariat synthesis, reword or discard freely.

---

## 1. The Rival

**Default first action = start a lab.** [PIP]
> "our rival can take multiple important actions through the game, and their
> most likely action in the fully-designed game is to start a lab. Let's have
> them do that as the first action we'll have them take by default, but I want
> to very carefully leave room for the lab to do other things if we give the
> player other things to do as well"

**Rock-paper-scissors / Pokemon-style meta (visible, mentally-modellable
advantage).** [PIP]
> "if a rock-paper-scissors type meta emerges, just like in Pokemon, I want our
> rival to be able to pick the same thing as us and essentially get a visible
> baked-in advantage that the player can mentally model well because they're
> familiar with the trimvirate or polyvirate rules of the game and can feel it's
> mechanically 'fair' that, oh yes, Politics beats Money even if Money beats
> Technology and Technology would have made it easier to beat Politics if I'd
> have picked that"

**The flavour vignette (target feel, NOT the literal copy).** [PIP]
> "I picked Money and I went outside and saw my rival set up a shop over the
> road advertising Politics, bother"
> (Pip's own caveat: "although probably not that blunt and obvious lol")

**Three-act rival presence.** [PIP]
- **Early game:** "we feel them mostly as a procedural force in the early game
  as both players build a power base"
- **Midgame:** "we feel them indirectly in the midgame as perhaps envoys and
  things happen"
- **Late game:** "we confront them more directly in the late game as we get to
  outright conflict level mechanics as more and more power comes to bear and the
  stakes get higher"

**Representation:** rival stays abstract / in silhouette (Carmen Sandiego
framing, established 2026-07-24) -- hints, stickers, pamphlets, glimpses of
people going into meeting rooms; the player mostly infers the rival rather than
sees them.

---

## 2. Narrative Pressure -- "Developments" (umbrella) / "Sightings" (rival subtype)

Naming decided for now: **Developments** = the general narrative-pressure engine;
**Sightings** = the rival-specific skin of it.

**Booker's Seven Basic Plots as the structural reference.** [PIP]
> "I spent like 2 years reading Booker's The Seven Basic Plots and while I don't
> necessarily want to get too monomyth-y, you know how that has a bunch of
> archetypal elements that recur as motifs the same way a Rags to Riches or a
> Tragedy will have recognisable beats?"

**Why beats need to be presented as options (the flaw-recognition point).** [PIP]
> "We don't feel as sad unless the person has multiple chances to recognise and
> overcome their flaws, so they have to be presented with those options, yes?"

**Our beat archetypes (the game's equivalent of Start / Kind Stranger / lose-to-
the-Dragon-but-survive / training).** [PIP]
> "maybe it's each player gets, like a Cat Encounter, a Stroke of good Luck, an
> Ally, an Early Success, a Local Problem, an Office Crisis, and then something
> allows them to Step Up a bit, leading to early-midgame and we shift out of
> startup-era to office-era"

**Era shift drives the event pools.** [PIP]
> "this then signifies changes in the styles of events that the event pools can
> draw from, and so on -- these can be interleaved so it's a bit more subtle for
> players"

---

## 3. The design north star (the "thumb on the scale")

**Respond to the world, don't script it; add spookiness; make the player feel
they matter.** [PIP]
> "we don't want to control what happens, we want the narrative flow of the world
> to feel like it's responding to real world events (like the real world did!)
> but with the slight layer of spookiness and things filtering into the game
> world that makes us feel like the player is having a difference."

**Deliberate optimism bias vs a "perfectly representative sim."** [PIP]
> "this means that the player is likely to experience more success than will be
> like correct for a perfectly representative sim, because most things are
> rejected etc etc etc, so there will be some thumbs on the scales kind of baked
> in there"

**Narrative-progression payoff ranking (what feels better).** [PIP]
> "a game where the player basically becomes a respected junior researcher and
> then works as a small part of a larger and larger team is less payoff than a
> player who ends up managing a company or leading a team of researchers or
> running the world's only doom-reducing frontier lab are all giving us better
> narrative progression feelings."

---

## 4. Secretariat notes -- connections & open questions [CLAUDE-note]

**Structural synergies (why these aren't three separate systems):**
- **Shared surface:** the rival gets revealed on the SAME "go outside to find
  contacts / recruit" loop as the people & money cohesion spine (#833). Leaving
  the office is what both exposes the rival AND drives recruitment. One surface,
  two payoffs.
- **Era shift == "the world starts shooting back":** the startup-era -> office-era
  transition is the same seam as the existing DESIGN_PHILOSOPHY midgame line
  ("the midgame begins when the world starts shooting back"). "Developments" IS
  the midgame-interaction engine, not a separate feature.
- **The polyvirate needs a named axis set.** Pip's example uses **Politics /
  Money / Technology** (Politics beats Money, Money beats Technology, Technology
  beats Politics). Candidate triumvirate -- confirm at WS-3. This axis set would
  also want to be the rival's action space AND (maybe) the player's strategic
  posture, so the RPS is legible.

**Open questions for WS-3 (#811):**
1. Is the rival ONE persistent silhouette (a modelled agent with its own moves /
   doom contribution) or a faceless procedural force with narrative dressing?
   (Pip leans: procedural early -> indirect mid -> direct late, so likely it
   GRADUATES from force to agent as the game progresses.)
2. Do "Developments" carry mechanical teeth (change game state) from day one, or
   ship flavour-first and gain teeth later?
3. Is the Politics/Money/Technology triumvirate the real axis set, or a
   placeholder? Does the player pick a posture on the same axes the rival does?
4. How are the beat archetypes (Cat Encounter, Ally, Office Crisis, Step Up...)
   represented in data? A beat-tag on events + an era-gate on the event pool?
5. How is the "thumb on the scale" implemented without lying to the player -- an
   explicit acceptance-bias on world-event injection? Where does it live so it's
   tunable and honest?

**Related docs:** `docs/copy/COPY_CORPUS.md` (voice), `docs/game-design/DESIGN_PHILOSOPHY.md`
("world shoots back", "the sim never lies; characters do"), `docs/game-design/WORLD_AND_LORE.md`
(Antagonist_Lab, the Mogul/Hustler/Operator personas), `PEOPLE_AND_MONEY_COHESION.md` (#833, shared recruitment surface).

---

## Appendix: unrelated WS-3 flavour seeds captured in passing

Not rival-related; parked here so they reach the WS-3 agenda (#811). Migrate to
the workshop backlog when it's stood up.

**Office upkeep / janitor (the retired "Office Maintenance" money-sink, reborn as
flavour).** [PIP, 2026-07-25]
> "It was a proof of concept money sink about 1,300 commits ago. abandon
> mechanism, lightly hold onto mechanical idea. I am thinking here of little
> people walking around SimPark and reliably dropping trash that a little
> janitor would wander around and collect, but at a lower scale / probably only
> relevant once we get larger offices, maybe?"

Design note [CLAUDE]: the mechanical seed is *ambient upkeep that scales with
org size* -- an office-era (not startup-era) cost that emerges only once you have
a larger office/team, tying it to the startup->office era shift above. The
current `office_maintenance` action (pays $5000, does nothing) is being REMOVED
from the action board in v0.13.1; this note preserves the idea for a real
implementation later.
