# Introducing RIVALS -- design options for issue #1088

Decision card for Pip. Source: recorded playtest 2026-08-01, timestamps
[3:58]-[4:27]; issue #1088. Design document only -- no code was changed.

His words, from the tape:

- [3:58] "Now, I've NEVER SEEN THESE RIVALS BEFORE, this is the FIRST TIME this
  information has appeared in the game"
- [4:02] "from a player experience, HOW DO I KNOW THAT I HAVE RIVALS?"
- [4:10] "How has the game INTRODUCED THIS CONCEPT to me?"
- [4:16] "How do I know what they're doing?"
- [4:27] "this is like a UI interaction storyline thing, so I think we can crack
  that out pretty quickly"

Verdict on [4:27], stated up front because he asked to be told rather than
agreed with: the INTRODUCTION is quick -- he is right about that half. The
[4:16] half ("how do I know what they're doing?") needs a continuing surface,
not a beat, and the third layer underneath both ("why do rivals matter to ME?")
has a hard ceiling no UI work can raise: in the current sim, rivals touch the
player only through the invisible-by-design overhang stream (ADR-0015) and one
decoupled poach flavour event. Full detail in Part C and the closing section.

---

## Part A -- the diagnosis: what a first-time player actually experiences

Traced through the code, in run order. The prior agent's finding is confirmed:
rival DATA is on screen early, but the CONCEPT is never taught, and the first
FRAMED appearance is the month review.

### The timeline

**t0 -- cold open.** `cold_open_sequence.gd`: portal, phone, passcode, Bank,
Messages. The Mysterious Helpful Stranger's entire message (line 56): "Hello
past me! I am expository filler (for now). You know nothing yet -- go and find
out. Read, show up somewhere, or be loud online. Scouting. -- MHS". Zero
mention of other labs. The handoff points at scouting (#811 item 1).

**t1 -- the first plan phase.** No surface names a rival. The nearest thing is
the strategic action "Corporate Espionage -- Slow down competitors (unethical,
risky)" (`data/actions/strategic.json:16-18`), which implies competitors exist
without naming any. Meanwhile the sim already holds three fully-simulated
rivals from turn 1 (`rivals.gd:153-180`): DeepSafety (KNOWN), CapabiliCorp
(KNOWN), StealthAI (RUMORED). Note: RUMORED counts as visible
(`is_visible_to_player()` is `visibility >= RUMORED`, rivals.gd:48-49), so ALL
THREE are player-visible from turn 1 -- the "two of three known" framing
understates it.

**t1-commit -- the first grey lines.** When the player commits the first plan,
`GameManager.end_month()` runs `turn_manager.execute_turn()`, whose
`_step_process_rival_turns()` (turn_manager.gd:636-661) appends ONE deadpan
headline per visible rival per month to the results, rendered grey-blue
(#9aa7b8) on the "rivals" channel: "CapabiliCorp pushes the frontier. The word
'safety' appears once, in the footer." These lines land MIXED IN with the
player's own action results ("Published 1 paper!...") at commit time. Three
unexplained proper nouns in a scrolling terminal feed, with no noun phrase
anywhere that says "these are rival labs and they are racing you."

**t1-playback -- the mute button before the concept.** The WATCH screen
carries a "Hide rival intel" filter toggle (main_ui.gd:136-138, 218-220,
1394-1423). So the first UI element that names the concept is a button for
TURNING IT OFF. A player can mute a channel they were never told existed.

**~t28 -- discovery, maybe.** `_step_check_rival_discovery()`
(turn_manager.gd:663-675) can fire the gold "[INTEL] there is another lab..."
line for StealthAI -- but only once reputation clears 45 (rivals.gd:174, 221-244),
typically well after the first review. The one felt reveal moment in the whole
system is gated behind the LEAST important rival.

**Month boundary -- the first framed appearance.** The month review
(`game_manager.gd:763-802`) renders `_build_rivals_review_section()`:

```
Rivals this month:
  DeepSafety (safety) -- capabilities flat
  CapabiliCorp (capabilities) -- capabilities flat
  StealthAI (rumored) (balanced) -- capabilities flat
```

Three named organisations with focus tags, presented as if the player already
knew them. This is the moment on the tape.

### Two code-level details that sharpen the complaint

**Detail 1 -- the first framed appearance is GUARANTEED information-free.**
`game_manager.gd:796`: the drift baseline is
`_rival_cap_snapshot.get(rid, rival.capability_progress)` -- when a rival has
no snapshot (always true at the first review), the previous value defaults to
the CURRENT value, so delta is 0 and every rival reads "capabilities flat"
regardless of what it actually did all month. The game's first framed statement
about rivals cannot ever say anything. (Fix is a rider on any option below:
seed the snapshot at game start, or suppress drift labels on first appearance
and print "now tracking" instead.)

**Detail 2 -- the player is never told WHY rivals matter, and mostly cannot
be.** Post-ADR-0015, rival capability feeds `frontier_capability`, which the
DoomSystem overhang stream converts to hazard (rivals.gd:6-9,
doom_system.gd overhang). That causal chain is deliberately unprinted (no
printed doom deltas). Legible attribution ("overhang: 60% CapabiliCorp") is
sketched as option 9 in RIVALS_SURFACING_OPTIONS_2026-07-20.md but unbuilt.
And `rivals.panic_per_capability_action` defaults to 0.0
(data/balance/defaults.json:141-142 block), so the one visible-world coupling
is currently zeroed. The honest summary: rivals presently affect the player
through exactly one invisible pipe.

### Where the first-time player first encounters "other labs exist and matter"

Honestly traced: as an UNFRAMED grey headline at first plan commit (exists,
does not register), then as the month review block (registers, but assumes
context that was never given). "Matter" is never encountered at all -- nothing
the player can see connects any rival to any number they care about, until the
death screen fails to name them either (surfacing option 10, unbuilt).

The design problem, precisely: data present, concept never taught, stakes
never shown. A grey one-liner among many is not an introduction, and a recap
cannot introduce -- a recap can only RESTATE.

---

## Part B -- seven options

Effort estimates assume the existing event/feed/window machinery; none of
these require new sim mechanics. "Teaches" is scored against three layers:
EXIST (there are rivals), MATTER (they affect my run), DOING (I can follow
their behaviour over time).

### B1. The Stranger's Second Text (advisor line)

**What the player sees, when:** one more MHS message, either as a final
cold-open beat or as a first-morning feed item on day 1:

```
MESSAGES -- Mysterious Helpful Stranger
  One more thing, past me. You are not the only lab that got
  funded this year. DeepSafety means well. CapabiliCorp does
  not. There is a third. Watch the feed. -- MHS
```

**Costs:** 1-2h (one string + one beat, machinery exists; #956 pattern).
**Risks:** cold-open beats get skipped (hold-to-skip exists,
cold_open_sequence.gd:591-599); a skipped intro is no intro. MHS copy is
Pip's to finalize, so the real cost is his writing pass. Continues the
"expository filler" placeholder tension.
**Teaches:** EXIST yes, MATTER weakly (asserted, not shown), DOING no --
though "watch the feed" at least points at the surface that already exists.
**Note:** this is the cheapest possible fix and a free rider on any other
option. It should probably happen regardless, but alone it is a sentence,
not an introduction.

### B2. First Contact (the Civ moment) -- RECOMMENDED FIRST BUILD

Pip's own philosophy names this beat: "[the Civ moment] settler -> city +
local barbarians -> deal with them -> meet either city-state or rival Civ --
this establishes early relationship" (DESIGN_PHILOSOPHY.md, early-game
section), and "Early contact compounds."

**What the player sees, when:** the FIRST time a visible rival takes an
action (first plan commit, month 1), that rival's headline is promoted -- once
per run -- from a grey feed line to a framed one-off INTEL window:

```
+--------------------------------------------------------------+
|  [INTEL] FIRST CONTACT                                       |
|                                                              |
|  CapabiliCorp closed a funding round this week. The press    |
|  release says 'responsibly.'                                 |
|                                                              |
|  You are not the only lab in this race. Their frontier work  |
|  raises the ceiling everyone falls from -- including you.    |
|  You cannot stop them. You can watch them, outlast them,     |
|  or ignore them.                                             |
|                                                              |
|  > Follow the race  (rival intel stays in your feed)         |
|  > I have work to do  (mute rival intel -- your call)        |
+--------------------------------------------------------------+
```

The two choices wire to the EXISTING "Hide rival intel" filter
(GameConfig.show_rivals_feed) -- the introduction IS the channel
subscription decision. This satisfies the ADR-0001 hard constraint (every
reveal must open a decision) and the philosophy ruling that muting a channel
is a legal, priced choice, without inventing any mechanism. After this
window, the grey feed lines and the review block are RESTATEMENTS of a
taught concept -- exactly what #1088 ask 2 requires.

**Costs:** 4-7h -- a one-off gate flag (save-carried), one event content
entry, wiring the choice to the existing toggle, a unit test on the
once-per-run gate.
**Risks:** consumes early acknowledgment budget -- either one of the 2-3
early window-demand slots (month_controller.gd:51-56) or it bypasses the
budget the way player-owned hiring prompts do; recommend bypass, since it
fires at plan commit, not during playback. Copy must stay deadpan; the
window frame makes tycoon-enthusiasm the failure mode.
**Teaches:** EXIST yes, MATTER yes (the one sentence of causal framing the
game currently never says, kept qualitative so ADR-0015 is untouched),
DOING partially (points at the feed as the ongoing surface).

### B3. Scouting Pays in Names (the authorship version)

The cold open already ends by handing the player scouting: "You know nothing
yet -- go and find out." B3 makes the first scouting action's RESULT complete
that sentence.

**What the player sees, when:** the first time any scouting action resolves
(scout_read / scout_meetups / scout_shitpost, data/actions/scouting.json),
its result message carries the reveal, provenance-matched to the verb:

```
  scout_read:    "You read for a week. Two names keep appearing:
                  DeepSafety, publishing carefully, and CapabiliCorp,
                  publishing fast. A third name appears once, then the
                  post is deleted."
  scout_meetups: "Half the room works at DeepSafety. The loud ones are
                  interviewing at CapabiliCorp."
  scout_shitpost:"Your post does numbers. Three CapabiliCorp recruiters
                  follow you before lunch."
```

**Costs:** 3-5h (three strings, a first-time flag, tests).
**Risks:** the player might not scout -- the nudge glows but does not force.
B3 therefore NEEDS a fallback (B2 or the month-review restatement) or some
players meet rivals cold anyway. Splitting the reveal across three verbs
triples the copy that must stay coherent.
**Teaches:** EXIST yes, and with AUTHORSHIP -- the player learns rivals
exist because they looked, the strongest possible framing per ADR-0004
(decision-flip: the reveal rewards the scouting choice and differentiates
the verbs). MATTER no. DOING no.
**Note:** pairs beautifully with B2: scouting gives the names EARLY and
warmly; first contact gives the stakes. If both land in month 1 they must
share copy so the second references the first.

### B4. The Front Page (diegetic press, reality-tethered)

**What the player sees, when:** the first WATCH tick of the run opens with a
single feed-tier block styled as a news front page -- the civilian-awareness
floor made concrete (philosophy: "the ambient floor is civilian awareness"),
and a home the league metabolism (ADR-0016) can refresh monthly:

```
  ------------------------------------------------------------
  THE REGISTER OF PROBABLE FUTURES        March 2017 -- 5 cents
  ------------------------------------------------------------
  MACHINES KEEP WINNING BOARD GAMES; INVESTORS KEEP NOTICING
  DeepSafety publishes 40-page alignment result; 14 people
  read it. CapabiliCorp raises again ('responsibly').
  Rumours persist of a third, quieter outfit. -- p.2: your lab
  is not mentioned anywhere.
  ------------------------------------------------------------
```

**Costs:** 4-6h as a styled feed block; 10-16h as its own dismissible
screen. Recommend the feed block.
**Risks:** a feed block can scroll past unread -- this is ambient
introduction, the softest tier (acknowledgment-scarcity says ambient < feed
< window, and an introduction arguably deserves the window tier once).
Pastiche copy is a new voice to maintain; must not drift from the deadpan
register. "-- p.2: your lab is not mentioned anywhere" is doing the actual
teaching (you are small, they are the story) and must survive editing.
**Teaches:** EXIST yes, MATTER weakly (mood, not mechanism), DOING no --
but as a RECURRING monthly front page it becomes a DOING surface and a
league-flavour asset. That upgrade is the real reason to pick B4.

### B5. The INTEL Card (persistent surface -- the A8 companion)

**What the player sees, when:** a small always-present card in the shared
instrument panel (both PLAN and WATCH, like doom/roster), from turn 1:

```
  +-- INTEL: THE RACE ----------------+
  | DeepSafety      safety    steady  |
  | CapabiliCorp    capabil.  rising  |
  | (rumour of a third)               |
  +-- feed: rival intel [on] ---------+
```

Qualitative drift labels only (capability_drift_label, rivals.gd:141-151) --
no numbers, consistent with ADR-0001 (sight is bought) and ADR-0015 (no
printed doom math). RUMORED renders as the rumour line, DISCOVERED upgrades
it, KNOWN completes it -- the card makes the existing visibility ladder
(rivals.gd:12-17) legible for the first time.

**Costs:** 6-10h (per MONTH_REVIEW_OPTIONS A8: contested panel real estate;
`_rival_cap_snapshot` needs a monthly owner rather than the review's
read-and-update).
**Risks:** A8's own warning stands: a panel does not INTRODUCE a concept --
B5 without a beat still fails [4:10]. Panel space is contested. A card
visible from turn 1 slightly pre-empts the fog; acceptable because the
roster is already visible-by-data from turn 1 (Part A).
**Teaches:** EXIST passively, MATTER no, DOING yes -- this is the ONLY
option on the list that answers [4:16] on an ongoing basis. It is the
second half of whatever first half is chosen.

### B6. The Poach (rival-initiated, forces acknowledgement)

**What the player sees, when:** month 2-4, the existing rival_poaching event
(core_events.json:260-292) recoupled to a NAMED lab chosen by aggression x
funding, upgraded from flavour text to a response window:

```
+--------------------------------------------------------------+
|  [!] CAPABILICORP MAKES AN OFFER                             |
|                                                              |
|  Dr Chen forwarded you the email, which was polite of her.   |
|  CapabiliCorp is offering double. She has not said yes.      |
|  She has not said no.                                        |
|                                                              |
|  > Counter-offer   ($30k/yr raise -- payroll rises)          |
|  > Let her decide  (loyalty roll; you keep the money)        |
+--------------------------------------------------------------+
```

**Costs:** 8-14h -- recoupling the event to the RivalLab object, the
counter-offer branch, calibration (#648: target ~1/year, current rate is
uncalibrated), tests.
**Risks:** the biggest option here in sim-touching surface -- this is the
one option that changes behaviour, not just presentation, so it needs the
balance sweep and cannot ride the "display-only" fast lane. Timing is
RNG-dependent, so it cannot be THE introduction (a player could reach month
4 unintroduced); it is the "rivals MATTER" hammer that lands after a
cheaper beat established existence. Early-window budget interaction.
**Teaches:** MATTER better than anything else on this list -- a rival
reaches into your roster and takes something, which is the only teacher
players never forget. EXIST redundantly, DOING no.

### B7. Hallway Contact (rivals as people, at the first conference)

The conference content is already seeded with exactly this texture:
"At a party in a rented warehouse someone from a rival lab is very friendly
and asks nothing at all about your work" (data/events/conferences.json:56).

**What the player sees, when:** attending the first conference (ADR-0014
presence machinery) guarantees one framed hallway beat naming a rival and
its disposition, personified:

```
  [CONFERENCE] A DeepSafety researcher buys you a coffee and
  apologises for their lab twice. Across the hall, the
  CapabiliCorp booth is hiring. It is a very large booth.
```

**Costs:** 6-10h, mostly content plus a first-conference gate.
**Risks:** conditional on the player attending a conference at all --
like B3, an opt-in surface cannot carry the whole introduction. Depends on
how much of the ADR-0014 presence loop is player-reachable in the current
build (verify before scoping).
**Teaches:** EXIST warmly, with provenance personified ("I want my minions
to bring me information!" generalised to the social layer) -- rivals become
people you met, which compounds (early-contact ruling). MATTER weakly,
DOING no.

### Riders that should ship with ANY choice (near-zero cost)

- **R1. Fix the flat-first-review baseline** (Part A detail 1): seed
  `_rival_cap_snapshot` at game start, or print "now tracking" on first
  appearance. 0.5-1h. Without this, whatever introduces rivals hands off to
  a review that immediately says nothing three times.
- **R2. The review only restates.** Gate `_build_rivals_review_section()` on
  "has the intro beat fired" once a beat exists (#1088 ask 2). 0.5h.
- **R3. Toggle honesty.** If B2's subscription choice lands, the WATCH
  toggle label and the choice should visibly be the same switch. 0.5h.

---

## Part C -- [4:16] is a different and larger question

"How do I know that I have rivals?" is a ONE-TIME teaching problem. "How do
I know what they're doing?" is an ONGOING legibility problem. One beat
cannot answer the second question, and a permanent surface cannot answer the
first. The mapping:

| Option | EXIST (one-time) | MATTER | DOING (ongoing) |
|---|---|---|---|
| B1 Stranger text | yes | asserted only | no |
| B2 First Contact | yes | yes (framed) | pointer only |
| B3 Scouting names | yes (authored) | no | no |
| B4 Front Page | yes (ambient) | mood only | yes IF recurring |
| B5 INTEL card | passive | no | YES -- the only real one |
| B6 The Poach | redundant | YES -- felt | no |
| B7 Hallway | yes (personified) | weak | no |

Options needing a CONTINUING surface rather than a single beat: B5 by
definition; B4 only pays for itself in its recurring form; everything else
is a beat and must hand off to something persistent or the player is
introduced and then re-blinded until the next month review.

The DOING column also has content the options list does not cover, already
scoped elsewhere and worth naming as the follow-on backlog:

1. **The existing feed lines become legible retroactively** once any intro
   beat lands -- the grey headlines stop being noise the moment the nouns
   mean something. Zero cost; this is why the intro pays off out of
   proportion to its hours.
2. **Month-review drift becomes real information** after rider R1.
3. **Overhang attribution by lab** (surfacing option 9) is the MATTER
   instrument: "overhang: 60% CapabiliCorp" in the paid doom-breakdown --
   consistent with ADR-0001 (resolution is earned) and ADR-0015 (level and
   band free, per-source detail bought).
4. **Name the killer lab on the death screen** (surfacing option 10): the
   retroactive teacher. Serves tragedy-not-horror (ADR-0004 lead-time
   clause) -- if a rival's frontier killed you, the game must say so.
5. **The ceiling: DQ-22.** The complete answer to "what are they doing?" is
   eventually "coming for you" -- the aggro-threshold midgame (litigation,
   funding cuts, hiring raids). That is a scheduled ADR workshop (the
   surfacing doc's own instruction: write the ADR first, do not let an
   agent freestyle it), not a crack-out. Until it lands, rivals are honest
   background dread, and the introduction copy should promise exactly that
   much and no more.

---

## Part D -- what NOT to do

**D1. The tutorial popup ("Rivals are other AI labs. They compete with
you...").** The obvious trap, and wrong three separate ways: it violates the
diegetic-onboarding thesis the cold open was built on (teach by doing inside
the fiction, one app at a time -- COLD_OPEN_SEQUENCE.md); it fails the
ADR-0001 hard constraint because prose that opens no decision is "a tax with
extra UI"; and it teaches a SCHEMA rather than an experience -- the player
who read the popup still has never seen a rival do anything. Prose about the
world belongs in the world's voice (MHS, the press, a hallway), never in the
game explaining its own rules from outside the fiction.

**D2. Full rival stats in the HUD from turn 1.** Tempting because the data
exists (get_rival_summary already formats funding/rep/safety/caps,
rivals.gd:302-310) and it "answers" both questions at once. Wrong because
fog is the game: spending-buys-sight (ADR-0001) makes rival detail a thing
you EARN through the visibility ladder, and dumping KNOWN-tier stats free
kills the discovery machinery (#474), the estimated-vs-real fields, and the
future Investigate verb (surfacing option 15) in one move. The restraint
rule applies too: a new always-on panel must prove it cannot be a read on
existing surfaces -- B5 passes that test only in its qualitative,
visibility-gated form.

**D3. Fixing it inside the month review.** Tempting because the review is
where the complaint was filmed. But a recap can only RESTATE; polishing the
rivals block (better drift labels, nicer layout) makes a better summary of a
concept that still was never taught. Pip already saw this himself -- the
fix "mostly does not live on this screen" (MONTH_REVIEW_OPTIONS A7). The
review work that IS worth doing is the riders (R1/R2), which make the
review a correct SECOND appearance.

**D4. A codex / lore screen ("LABS" tab with descriptions).** The
description fields exist (rivals.gd:160, 167, 175) and a reference screen
feels thorough. But reference material is pull-only -- the player who most
needs the introduction is precisely the one who does not know to pull; it
adds a surface (restraint rule) that answers neither EXIST-at-the-right-
moment nor DOING-over-time; and it invites lore-writing effort that the
roster may not survive (the naming pass to match WORLD_AND_LORE is still
owed -- surfacing doc section 1). If a codex ever exists, it is where an
introduction LINKS, never the introduction.

**D5. Three introductions.** Firing a separate framed beat per rival (and a
fourth for discovery) triples acknowledgment cost in the exact weeks the
window budget protects (2-3 demands early, month_controller.gd:51-56), and
the acknowledgment-scarcity ruling is explicit that decision demands are
what flood. One beat introduces the CONCEPT and names the cast; the
already-built [INTEL] discovery line remains the per-rival reveal for the
hidden third. Resist the completionist urge to make each lab its own event.

---

## Bottom line

- **Is it quick?** The half he pointed at, yes: B2 plus riders R1-R3 is a
  day, B1 rides along free, and his "UI interaction storyline thing"
  instinct is correct FOR THE INTRODUCTION. The [4:16] half is a second,
  medium job (B5, 6-10h, plus the Part C backlog items), and the "why they
  matter" floor is capped until DQ-22 gets its workshop -- no copy can
  honestly promise rivals that shoot back before the sim has them.
- **Build first:** B2 (First Contact) with riders R1-R3, because it is the
  only cheap option that teaches EXIST and MATTER in one diegetic beat,
  opens a real decision (the channel subscription -- ADR-0001 satisfied by
  wiring to an existing toggle), needs no sim changes, and does not depend
  on the player happening to scout or attend a conference.
- **Build second:** B5 (INTEL card), so [4:16] has a permanent answer and
  the month review can point instead of dump.
- **Hold in pocket:** B3 and B7 as content riders whenever scouting and
  conferences get their next pass (both are strings, not systems, once the
  first-time flags exist); B6 for after the #648 calibration; B4's
  recurring front page as a league-metabolism flavour asset.
