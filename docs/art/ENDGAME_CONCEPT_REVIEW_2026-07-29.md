# Endgame concept review -- 2026-07-29 (Pip + Wanasai, spoken)

- **Source:** 34-minute recorded review, transcript at
  `art_generated/audiodump/2026-07-29_21-22-07.transcript.md` (timestamped).
- **Status:** EXTRACTED BY CLAUDE, NOT YET SANITY-PASSED BY PIP. Every verdict
  below is my reading of an unlabelled two-speaker transcript. Correct anything
  wrong before this steers a regeneration.
- **Batch:** `art_generated/endgame_concepts/v1`, manifest
  `tools/assets/manifests/endgame_concepts.json`, 15 concepts x 2 variants.

> **PRIVACY -- do not move the raw transcript into a tracked path.** An
> Australian mobile number is spoken aloud mid-recording. `art_generated/` is
> gitignored, which is the only reason this is safe. Scrub before any reuse.

## Confidence key

- **[NAMED]** -- Pip said the concept's name aloud; mapping is certain.
- **[POSITION]** -- mapped by order of discussion against manifest order.
  Order matched perfectly wherever a name was spoken, so this is strong but
  not certain.
- **[?]** -- I could not resolve which variant was meant.

---

## PART A -- the general rules (the valuable part)

These were stated as rules, not as reactions to one image.

> **PROVISIONAL -- ruled by Pip, 2026-07-29.** Treat A1-A10 as **guidelines on
> probation, not settled law.** Some of these will turn out to be real
> constraints and some will turn out to be reactions to one bad image. Pip:
> *"some of the rules here might be more like guidelines and I don't want to
> over-commit future me without a generation of regens at least."*
>
> **Review trigger: after ONE full regeneration cycle run under these rules.**
> At that point, promote the ones that demonstrably improved output, demote the
> ones that just narrowed it, and kill any that produced worse art. Do not
> promote any of this into the style guide or an ADR before that cycle runs.
>
> A2 (no people) is the one most likely to be over-broad, because it is also
> the most sweeping -- it may prove to be "no *incidental* people" rather than
> "no people".

### A1. Mood must never come from the main light source

Stated three times, the clearest version:

> "there's probably a rule here that says something like, don't generate mood
> from lighting that wouldn't incidentally be used to generate mood. Like, if
> I'm going to have an emergency sign flashing, have it be emergency sign.
> Don't have the normal room lights be red or green, because I think it is
> unsubtle."

And the dial: **"we need to make your mood lighting like 75% more subtle."**

Corollary caught on the drone-fence image: if an emergency light IS the mood
source, every other light in frame must be a visibly different source.

### A2. No people in poster art, by default

The most consequential rule of the night:

> "my main concern is that by having people in the scene we break away from the
> peopleless... and particularly protagonist motif and by having other people
> in the scene it implies that the viewer should be responding to something
> rather than simply observing"

Explicit instruction, verbatim:

> "for all of the poster and meta art can we go back and look at the prompts
> and then regenerate versions of everything except with everything copied the
> same, except with no people in it... or if we are using people explicitly
> make them androgynous silhouettes, or if they have to be multiple people
> explicitly make them a reasonably varied group making reference to the first
> eight character sets of the employee class"

Reason given: default generator people are "interesting generic people" that
override his explicitly listed preferences. **This is a regen-everything
instruction, not a per-image note.**

### A3. Never show the hero / player character

Consistent with existing practice (the Dr. Claw model -- cosmetics only ever
show part of an arm or a shirt at the edge of frame). For the intro scene the
identity must be obscured through blocking and lighting so the viewer cannot
tell gender or anything else, with attention drawn instead to the people
stepping in to help.

### A4. Drone cockpits are an anti-pattern

> "any representation of a cockpit is an anti-pattern because directly
> manufactured drones don't have cockpits and so anything with a cockpit is we
> just want to like select against that while still having aircraft"

### A5. Objects must be legible, or they are noise

On unidentified shapes: *"Are they cars?... if I knew what these were... right
now, they're both just random boxy things."* Props earn their place by being
recognisable, ideally by also existing elsewhere in the game.

### A6. Props must be era-correct and match in-game assets

The banker's lamp: V2's lamp preferred "85% more" for being era-correct, and a
banker's lamp "is always green". If the in-game swanky-desk asset exists, the
concept art and the asset should agree down to the number of bars.

### A7. Palette anchored per weirdness level

Hash-value anchors per tier so colour stays consistent across images even when
composition and style do not -- e.g. a fixed indigo range for high-weirdness.

### A8. Avoid barbed wire

Reads "a little too concentration campy."

### A9. The correct term is POSTER ART

Pip corrected himself mid-session: he had been calling it the wrong thing while
generating. Worth propagating into the glossary and manifests.

### A10. The three flavours of weirdness

Pure/eldritch (spooky things from other dimensions), technology run amok
(drones), and environmental. Useful as a generation axis.

---

## PART B -- per-concept verdicts

### 1. field_ladder_three_rungs [NAMED]
**Lean V1, no hard verdict.** V1 preferred for sharpness -- "I like the
relatively sharper image of this one... I can see this as a thing and not just
like a smoke cloud." Blue in the other variant liked. The ring should be
"something more obvious" -- he mistook it for a lighting effect -- and one
variant is "too blurry". Composition called "a bit average"; wants the ring
off-centre or not fully in frame. The boxy objects are illegible (A5). The
red square lamp is wrong (A1). Overall he was impressed given the abstraction
of the brief.

### 2. same_desire_two_field_strengths [NAMED]
**STRONG NO ON BOTH.** Verbatim: *"this is just fucking terrible... the concept
probably feels right, but I hate the execution, I hate everything about it"*
and *"strong no on both same desire two strength fields."*

Failure modes worth keeping: the seated figures cannot physically sit that way,
which **breaks the uncanny valley rather than achieving it**; perspective is
off; the two halves have different lighting (funny, but wrong -- A1). He is
"not sold on this kind of framing anyway". If retried, generate as two images
and composite rather than asking one image to contain a diptych.

### 3. orbital_datacenter_ring [NAMED-BY-PIP, RESOLVED 2026-07-29]
**V1, extended.** "Death ships! Wow." Ruling: take **V1**, and have it
**extend further through the composition** -- that is, keep V1's read but give
it the quality Pip liked in the other variant, which "goes on for longer"
across the frame rather than resolving early.

Also wants **a tiny green dot for depth** -- explicitly the inverse of the
Dutch use of a small red square to open up a composition. No assigned use in
the game yet: "I don't know what I'm going to use that one for, but it's cool."

### 4. pacification_delivery_suburb [POSITION]
**Pass both, salvage the idea.** *"a pretty easy pass... I don't like either of
them. I'm just going to abandon that entirely."* Reads as a 1990s sci-fi
magazine foldout. Credit given that nothing is sexualised.

**The salvage is better than the image.** All robots facing one way implies a
camera and therefore a protagonist, which contradicts the whole game -- *"you're
a bureaucrat, it's about everyone else."* The proposed replacement concept is a
sorcerer's-apprentice runaway: you order one TV, twenty robots arrive with
twenty TVs; the next day, twenty fridges. Explicitly tied to the horror of an
unbounded `for` loop.

**RESOLVED 2026-07-29:** the *"I like this one... perspective going way off
into the distance"* line is **the start of the next concept, not a reprieve.**
So this concept is a clean pass on both variants, and the receding-depth praise
belongs to whatever came next on the sheet.

One loose end worth a glance during the contact-sheet pass: the content that
immediately follows (robots all facing one way, the twenty-deliveries salvage)
reads as delivery-adjacent, so the sorcerer's-apprentice idea may need
re-homing onto the correct concept id. The idea stands regardless of which
image it was attached to.

### 5. cheerful_propaganda_atrium [NAMED]
**Keep -- one of the night's winners.** *"I think this one with its hands is
actually really good"*, reminiscent of late-Soviet propaganda. The looming
figure works: *"looming is good, because he's just keeping an eye on the humans
voting."* Both reviewers liked the hands. The slides are "fucky".

Open disagreement, unresolved: Wanasai argued a **smiling** face beats a blank
one (a corporation proving everyone is happy would propagandise the voting
space); Pip leaned blank/no-face and found the smile creepier. **Resolution
agreed: generate with and without a face and compare.**

### 6. crux_drone_arms_race [POSITION]
**Positive, needs a clearer read.** "This one's good." The two fenced sides
must be far more delineated -- proposed blocking: *"robots, dude inspecting
them, fence, gap, fence, other robots"* -- so the red and green sides are
legible. Colouring needs restraint; this is where the 75%-subtler mood-lighting
note landed. Note this concept currently contains a person, so A2 applies.

### 7. chokehold_water_and_gigawatts [NAMED]
**Keep as a HYBRID.** Said plainly: *"chokehold water in gigawatts V2, we
like."* Then refined:

- **V1**: better composition; better pipe texture; the small central
  electricity is right because it reads as *possibly normal* electricity.
- **V2**: better overall colour; padlock overdone; far too much light low in
  frame; the pipe angle is wrong (V1's angle is right).
- **Target**: V1 composition and pipe + V2 colour set, with electricity cut to
  roughly what appears left of V2's padlock and moved to mid-frame.

The pipe drew the most enthusiasm of anything: an acrylic-like rendering rather
than photorealism, with "old school" crackle lighting.

### 8. chokehold_permit_counter [NAMED]
**Keep, rework.** Intent, in his words: civilisation choked by bureaucracy,
where only machines can comprehend the rules that infinite free lawyers
produce -- humans cannot get a permit through; the machine across the counter
can.

Changes: the human should be **slumped**, **smaller**, and **surrounded** by
paperwork; use a **wider-angle lens for foreshortening** so it reads
object -> human -> background rather than object, dead space, small human; add
**many stamps**, some visibly recently used; add folders and evidence of
things done in triplicate. Backgrounds of both are good; V1's colouring and its
mostly-complete facade catching light are liked; **V2's lamp wins** (A6).

### 9. attention_stack_buried_desk [NAMED]
**HARD PASS BOTH.** *"they're both like just veering towards cliche and I need
to figure out how to do weird a bit better."*

Worth recording: the generating agent nominated this as its single strongest
image. It was rejected outright. Agent taste is not Pip taste.

### 10. attention_loud_vs_slow [NAMED]
**V2, then regenerate without people.** V2 is *"definitely a stronger
character"*: figures at the corridor edges leave space that draws the eye
forward, versus V1 where they fill the frame. Purple in the walls liked in
both. V1's lights liked; V2's single circular light interesting, but if that is
the emergency source then every other light must differ (A1). Then A2 applies
to the whole image.

### 11. economics_rung_shuttered_street [NAMED]
**Strong V2.** *"I want to play Call of Duty on the one on the right"*, and
"the composition of the one on the right is like great -- strong thumbs up."
Defect: the chain-link fence fades into nothing and does not hang correctly.
V1 rejected for barbed wire (A8). Follow-up noted: "that needs to match reality
so do a reality scan."

### 12. remote_operators_room [NAMED]
**V1 tentatively; V2 rejected.** *"v2 they all look too much the same; v1 is
okay for now, but again see notes on representation"* -- i.e. blocked behind A2.

### 13. defeated_drone_coolant [NAMED]
**V2, strongly. "Extremely cool."** V2 fills the frame and reads bigger and
dominant; the spark implies *"there's still some life in it"*; the hole in the
screen above adds a sense of something having come out. This is the image that
produced rule **A4** -- recast with the no-cockpit constraint.

### 14. field_leaks_at_every_angle [NAMED]
**HARD PASS BOTH** -- *"both these are trying to do too many things at once."*
Salvage list: the floating silhouette figure is interesting and the floatingness
is good; runes on the right are better but **runes need more content**; the V2
tentacle works **because it is subtle and out of the way**; the eyes are too
obvious. His own estimate is that there is "probably not" anything worth
salvaging.

### 15. intro_bus_strangers_help [NAMED]
**Both good; V2 favoured; needs a real compositional solve.** The scene is the
time-traveller who has lost their memory, and the strangers who help are the
first contacts in the player's Network.

Hard constraint (A3): **the hero must never be identifiable.** Wanasai's read,
which drove this: both are over-bright, and **V1 is too specific** -- *"you can
see her pearl earrings"*, a tie and collar -- while V2 obscures more (a hat,
reads "a bit like a hobo") and its centre is more crisply defined. Pip: the
attention must land on the people stepping in to help, and the viewer must not
feel cheated of a focal figure. He named this "an interesting compositional
challenge that we'll leave for another night."

Also: the lamp is "really dated" and he would not specify a light source that
way.

---

## PART C -- process notes

**The two-variant method is validated.** *"if it just gave me this, it's like,
what do you like about it? And I'm like, ah -- when I can see this, I can see,
well, of these two, I like..."* Keep generating pairs.

**Naming the concept aloud worked; naming the VARIANT is the gap.** Pip named
12 of the 15 concepts out loud, which is the only reason this extraction was
possible at all -- "the three-rung ladder of weirdness", "chokehold water in
gigawatts V2", "attention loud verse slow" and so on map cleanly to manifest
ids. The three position-inferred entries are the ones he did not name.

The residual ambiguity is at the **variant** level, and it comes from pointing
at the screen out of habit -- Wanasai's, mostly, since she was reading over the
shoulder rather than driving. The coaching line, from the recording:

> "if you verbally differentiate between the angles on V1 and V2, the model
> will know which ones we're talking about. But when you're pointing, it can't
> see what you're pointing at."

Three verdicts are unresolvable for this reason. Cheap fix next session: say
"V1" or "V2" before each opinion, and both people say it.

**Concept art is direction-finding, not shipping art.** *"none of these are
going to survive me actually hiring a human... These all give us directions."*
Consistent with the public Manifund commitment.

---

## Tally

| Verdict | Concepts |
|---|---|
| **Keep / rework** | orbital_datacenter_ring (V1, extended), cheerful_propaganda_atrium, chokehold_water_and_gigawatts, chokehold_permit_counter, crux_drone_arms_race, defeated_drone_coolant (V2), economics_rung_shuttered_street (V2), attention_loud_vs_slow (V2), intro_bus_strangers_help (V2) |
| **Hard pass** | same_desire_two_field_strengths, attention_stack_buried_desk, field_leaks_at_every_angle, pacification_delivery_suburb (idea salvaged) |
| **Unresolved** | field_ladder_three_rungs (lean V1), remote_operators_room (V1, blocked on A2) |

Roughly half kept, half rejected -- which matches Pip's own summary before the
transcript was read: "half are magnificent, half are terrible."

## Next actions (proposed, not started)

1. Pip sanity-passes this file; correct anything misattributed.
2. Resolve the two remaining entries against the contact sheet
   (field_ladder variant; remote_operators once A2 is settled).
3. Fold A1-A10 into the manifest's shared style block **as PROVISIONAL**, so
   they apply by construction rather than by memory -- but do NOT copy them
   into the style guide or an ADR yet.
4. Regenerate the keepers under A1-A10, with **no people** as the default.
5. **Then review A1-A10 against the regen output** and decide which are rules
   and which were one-image reactions. That review is the gate on promoting any
   of this to settled doctrine.
6. Consider adding A9 (poster art vs hero art) to `docs/GLOSSARY.md` -- that one
   is a naming correction rather than a taste judgement, so it is safe to land
   early.
