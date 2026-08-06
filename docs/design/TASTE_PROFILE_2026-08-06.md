# Taste profile -- what 151 slot decisions and 111 notes actually show

- **Status:** MEASURED (read-only; no art generated, no verdict or pick file
  modified)
- **Date:** 2026-08-06
- **Question, Pip's words:** "What have we learned about the finer expressions
  of my taste from the picks? That seems like useful metadata."
- **Inputs:** `tools/assets/demand/slot_picks.json` (136 contested slots + 15
  frame roles, resolved in one session on 2026-08-06) and
  `tools/art_review/review_state.json` (2,713 verdicts, 111 of them carrying a
  typed note). Both READ-ONLY here.
- **Re-run everything numeric below with:**
  `python tools/art_review/measure_taste.py`
  (that script is the authority for every number in this file; the doc is a
  reading of its output, not a separate calculation).

## Method, and what it can and cannot see

For each contested slot Pip chose one candidate and left the others as Library
assets no manifest entry names. **The rejections carry the signal.** A chosen
icon on its own says nothing -- icons are dark because icons are dark. A chosen
icon sitting next to the two near-identical siblings it beat isolates the one
difference that decided it.

So every statistic here is paired: *chosen minus the mean of the rejected,
within one slot*, counted across slots. n is the number of contested slots
where the comparison exists (136 unless stated). The test is a sign test; the
reported `p` is the two-sided exact binomial against 50/50, and each metric is
additionally checked against a **permutation null** -- 1,000 draws where the
winner in each slot is picked at random -- because slot sizes are uneven (61
two-candidate slots, 48 three, 18 four, 9 larger) and an uneven design can
manufacture a bias that is not taste. The permutation nulls all land at
0.49-0.52, so the design is clean and the sign test is readable at face value.

Three method choices that change the answer, stated because they do:

1. **Candidates are resampled to a common 128x128 canvas before measuring.**
   Without that control, a 32px source and a 512px source in the same slot get
   measured at different resolutions, and the downscaling itself moves contrast
   and gradient magnitude. Running `measure_taste.py --native` reproduces the
   uncontrolled version: detail density weakens from 71.3% to 59.6% and PNG
   bytes-per-pixel flips sign. The controlled numbers are the ones below.
2. **"Detail density" is the mean luminance-gradient magnitude on that canvas.
   It is a proxy and it is crude.** It rises with texture, grain, and edge
   count alike, and cannot separate "richly rendered" from "noisy". PNG
   bytes-per-pixel is reported alongside it as a second proxy that fails
   differently (it rises with dithering, falls with flat alpha) -- when the two
   agree, that is worth something; when they disagree, neither is trusted.
3. **The clustering is the weakest link and is inherited, not fixed here.** It
   is `slot_model.role_stem`'s filename heuristic, which merges cross-batch
   assets sharing a stem and fails to merge same-role assets with unrelated
   names. A cluster means "these definitely compete", never "nothing else
   competes".

## The tempo caveat -- read this before believing any of it

```
python -c "import json,datetime as D; \
p=json.load(open('tools/assets/demand/slot_picks.json'))['slots']; \
t=sorted(D.datetime.fromisoformat(v['decided_at'].replace('Z','+00:00')) for v in p.values()); \
g=[(t[i+1]-t[i]).total_seconds() for i in range(len(t)-1)]; \
print(len(t),'decisions', round((t[-1]-t[0]).total_seconds()/60,1),'min', \
'median gap',sorted(g)[len(g)//2],'s', 'gaps<5s:',sum(1 for x in g if x<5))"
```

**136 decisions in 10.4 minutes. Median gap between decisions: 1.7 seconds. 120
of 135 gaps are under five seconds.**

That is a snap-judgement pass, not a deliberation. Whatever decided these picks
had to be legible in about a second at thumbnail size. This is the single most
important framing in the document, and it predicts the result before the result
arrives: the dimensions that survive should be the ones visible instantly
(contrast, pop, brightness), and the dimensions that need looking should show
nothing (composition, palette, subject treatment). That is exactly what the
measurements show, which is either corroboration or the tempo explaining away
the whole analysis -- both readings are live. It does NOT mean the picks are
bad; a second is plenty to judge which of four icons reads.

## Signal 1 -- contrast, the strongest thing in the data (n=136, 74.3%, p<0.0001)

```
contrast (luminance sd)   n=136  chosen higher in 101 (74.3%)  mean delta +0.0119  p<0.0001
contrast (p95 - p05)      n=136  chosen higher in  96 (70.6%)  mean delta +0.0446  p<0.0001
```

Two different contrast definitions agree, the permutation null sits at
0.514 +/- 0.042, and the effect survives dropping the 22 size-ladder slots
(82/114 = 71.9%, p<0.0001). In 8-bit terms the chosen image has on average
+11/255 more spread between its 5th and 95th luminance percentiles than the
siblings it beat (pooled means, which understate it because of the trap
described under signal 3: 0.488 vs 0.454, i.e. +8.6/255).

It is not one destination carrying it: icons 87/113, textures 9/14, heroes 5/7,
events 2/2.

Largest positive examples (chosen minus mean rejected, luminance sd):
`team_building` +0.118, `icon_money` +0.067, `ui_settings_account` +0.061,
`icon_morale` +0.061, `button_cancel_normal` +0.060.
The counter-examples exist and are real: `icon_reputation` -0.064,
`ui_config_random` -0.037, `icon_acquire_startup` -0.029. 35 of 136 slots went
the other way. This is a tendency, not a law.

## Signal 2 -- detail density, busier wins (n=136, 71.3%, p<0.0001)

```
detail density (grad)     n=136  chosen higher in 97 (71.3%)  mean delta +0.0033  p<0.0001
PNG bytes/pixel           n=114  chosen higher in 73 (64.0%)  mean delta +0.0282  p=0.0035
```

The bytes-per-pixel line is the 114-slot subset with the size ladders removed,
because in ladder slots the file-size proxy measures resolution rather than
content. On that subset the two independent proxies agree, which is the reason
to believe the finding at all -- a gradient proxy alone would be one
measurement dressed up as two.

Contrast and detail are correlated but not the same axis: r = 0.50 across the
136 per-slot deltas; 85 slots moved up on both, 23 down on both, 28 disagreed.
So "he picks the punchier one" is closer to the truth than either metric alone,
and the residual 28 disagreements are where the two ideas come apart.

**This one is corroborated by his own words**, which matters more than the
pixels: `action_facility_upgrade_compute:v2` -- "a bit too simple, try with more
depth and texture and richness, decrease arrow size by 15%". And five separate
discard notes reading "blurry", "blurry?", "blurrrrry", "mostly discarded for
being blurry".

## Signal 3 -- brightness, weaker but real (n=136, 63.2%, p=0.0026)

```
luminance                 n=136  chosen higher in 86 (63.2%)  mean delta +0.0088  p=0.0026
```

**With a trap attached.** Compare the paired result to the unpaired one: pooled
across all 398 files, the chosen images are *fractionally darker* than the
rejected ones (mean 0.1963 vs 0.2016, i.e. -1.4/255). Both statements are true.
Within a slot he takes the brighter sibling; across the corpus the slots he
chose brighter siblings in happen to be darker slots. Anyone quoting a global
chosen-vs-rejected average of anything here will get the sign wrong. Only the
paired numbers mean something.

Again the notes say it in plain language, from the 2026-07-25 icon pass:

> "too dark, brighten, decrease grain slightly"
> -- `gen:game_icons:action_strategic_acquire_startup:v2`

> "Brighten, increase contrast, consider lighting some of the windows gently"
> -- `gen:game_icons:action_strategic_acquire_startup:v3`

> "Needs a bit more lightness and colour, slightly increase contrast around
> interior edge of hood"
> -- `gen:game_icons:action_strategic_sabotage:v1`

That is the measured signal being dictated back, months earlier, in his own
words. Contrast and brightness are the two things he asks for by name.

## NULL RESULTS -- the loud part

These are as actionable as the signals, and there are more of them than there
are signals.

```
saturation                n=136  chosen higher in 75 (55.1%)  p=0.26   perm p=0.16
off-centre distance       n=136  chosen higher in 72 (52.9%)  p=0.55   perm p=0.80
PNG bytes/pixel (all)     n=136  chosen higher in 75 (55.1%)  p=0.26   perm p=0.22
```

**Composition is the cleanest null in the dataset.** The distance of the
luminance-weighted "ink centroid" from frame centre is indistinguishable from
random at 52.9%, and drops to 48.2% when the size ladders are excluded. He did
not systematically prefer centred over offset subjects, or tight over loose
crops, in any way this measurement can detect. Caveat with teeth: a centroid is
a blunt composition metric -- it cannot see rule-of-thirds placement, horizon
height, or figure-ground relationship, so read this as "no gross framing
preference", not "composition does not matter to him". His notes DO discuss
composition ("this was a good composition but more recent versions have better
approaches...", "shoot from the back"), so the null is more likely a limit of
the metric plus the 1.7-second tempo than a real indifference.

**Saturation is a genuine null with the same brightness trap.** Paired: 55.1%,
nothing. Pooled: chosen images are *less* saturated by -7.4/255. Neither
direction is defensible. Note that this null contradicts what a reader might
expect from the CRT-terminal framing -- there is no measurable pull toward a
saturated amber-phosphor look in the picks. There is one note asking for the
opposite of restraint ("try increasing saturation slightly and emboldening
shield, otherwise, good", `action_research_robustness:v1`) and one asking for
restraint ("The yellow is a little unsubtle"). One each is not a preference.

**Palette / hue: weak at best, and it does not survive correction.** Splitting
saturation-weighted hue into 12 buckets and running the same paired test, three
buckets come up: yellow-green 90-120 deg (n=68, chosen-higher 32.4%, p=0.005),
green-cyan 150-180 (n=84, 34.5%, p=0.006), green 120-150 (n=70, 37.1%,
p=0.041), all in the direction of *avoiding* green, plus a non-significant lean
toward cyan 180-210 (n=87, 59.8%, p=0.086). Twelve tests were run; Bonferroni
puts the best of these at p=0.06. **Report this as: possible mild aversion to
yellow-green and green-cyan, not established.** It would need a purpose-built
A/B to confirm, and it is cheap to confirm -- vary hue deliberately in tomorrow's
run and the next pick pass answers it.

**Generation lineage: no preference, and this is expensive to not know.**

```
slots where variant numbers differ: 119
  chose highest vN:  40   (random expectation 47.3)
  chose lowest  vN:  50   (random expectation 48.2)
  chose middle  vN:  29
  binomial p, highest vs lowest: 0.34
```

Per-variant hit rates: v1 64/192 = 33.3%, v2 45/105 = 42.9%, v3 19/76 = 25.0%,
v4 8/25 = 32.0%. Every cell is near the 34% base rate. **Iterating a prompt to
v3 and v4 bought nothing measurable.** He did not prefer later variants, and he
did not prefer originals either -- the highest-variant count (40) is slightly
*below* the random expectation (47.3), which is the closest thing to a
direction, and it is not significant.

Two consequences worth taking seriously. First, the 2026-08-03 "highest variant
wins" default convention has no support in his actual behaviour -- as a
tie-breaker it is arbitrary, which is what it always claimed to be, but it
should not be described as tracking taste. Second, and this is the money
finding for spend: **a fourth variant of the same prompt is worth about as much
as a first. Breadth beats depth.**

**Frame roles are a null too (n=12 contested, higher contrast in 6).** The icon
contrast preference does not appear in the frame source picks at all. Small n,
so this is "no evidence", not "evidence of no". Per the re-parse note in the
picks file, the frame TREATMENTS (`whole` vs `nineslice`) are not usable as
taste data -- he picked `whole` where he meant `nineslice` and consented to the
inversion being re-parsed -- but the SOURCE picks stand, and this is what they
say.

## 22 of the 136 decisions contain no taste at all

```
python tools/art_review/measure_taste.py   # prints "excluding the 22 size-ladder slots"
```

In 22 slots the competitors are the SAME artwork at different resolutions
(`icon_dial_clock` at 32/48/64/128/256/512/1024, `gen_seal_paper` at
64/128/256/512, and so on). His picks there scatter -- 128px four times, 256px
three, 512px twelve, 768px once, 1024px twice -- with the only visible rule being that when
the choice is "tiny or 512" he takes 512, which is not taste, it is legibility.
These 22 should be re-derived mechanically from the demanded draw size rather
than treated as decisions, and the picker should not have shown them. That is a
tooling finding, not a taste finding, and it is worth a follow-up issue.

## Signal 4 (words, not pixels) -- the one thing he says over and over

Nine of the 111 notes are about **who the human figure is and whether they can
be identified**:

```
python -c "import json,re; d=json.load(open('tools/art_review/review_state.json')); \
print(sum(1 for v in d.values() if isinstance(v,dict) and v.get('note') and \
re.search(r'\b(male|men|man|androgyn|gender|identifiab|unidentified|silhouett|human face|persona)\b', v['note'], re.I)))"
```

The same sentence appears four times in a row, on `hero_founder_silhouette` v1
through v4:

> "silhouette too boviously male, too obviously signalling Operator"

And the constructive version, which is the most useful sentence in the entire
notes corpus because it is a specification rather than a complaint:

> "this was a good composition but more recent versions have better approaches
> to keeping the protagonist unidentified - shoot from the back, silhouettes
> for either gender only, hoods, hats"
> -- `gen:endgame_concepts:intro_bus_strangers_help:v1`

Supporting instances, verbatim:

> "Try making fihgures more androgynous and less obvious, otherwise, good"
> -- `scene_art_wave2/v1/event_opportunity_v2.webp`

> "andogynous operator please, otherwise, good, maybe give them a cape or cloak
> or be carrying equipment or san umbrella or protective gear or somesuch"
> -- `gen:hero_banners:hero_server_doom_altar:v2`

> "Having a human face makes it weird, see what happens if we give the figure
> (a) a mask, so it could be human or robot, (b) a copy of (a) but mybe make
> one of the arms or the person be ambiguouss or hinting at possibly being
> robotis as well, (c) have the figure still be fairly non-human but with more
> religious overtones as well as (d) a version of (c) but with more
> state-propoganda overtines"
> -- `gen:wanasai_calls:atrium_face_smiling:v1`

> "human too identifiable, otherwise, good, backgroundf weirdness good also"
> -- `gen:endgame_concepts:attention_stack_buried_desk:v2`

> "this operator seems too visible and obviously a man, maybe try making the
> scene more abstract, luggage on bed, overstuffed mailbox at an apartment door
> with packages buiding up outside, what's in the fridge, etc"
> -- `px:vignettes_2026-07-28/04_conference-return.png`

This is the strongest preference in the whole corpus and no pixel metric would
ever have found it. It is also the cheapest to act on: it is a prompt
constraint, not a style dial.

## Signal 5 (words) -- symbol choice, and the rejection of the obvious one

Seven notes reject a cliche symbol by name:

> "Not nuclear symbol. Experiment with new, geometric abstract represtation of
> doom escalation" -- `gen:game_icons:doom_bg_critical:v3`

> "Not a lock. try a more symbolic reprsentation in the abstract. Consider an
> alien culture's represetion of safe from boba principles."
> -- `gen:game_icons:doom_bg_safe:v1`

> "one red team one blue team, combat, not chess, can be engineers facing each
> other off" -- `gen:ui_icons:action_research_red_teaming:v2`

> "this si danerously close to a mtg symbol. think about better repersentaiton
> for emotinal burnout" -- `gen:ui_icons:employee_status_burned_out:v1`

> "Entirely rebase instructions for this, reading LLM, and branch out into
> several variats so we can move away from cliche"
> -- `gen:round3_rerolls:grant_proposal_r3:v1`

And the positive form -- when the symbol is fresh and specific he escalates hard:

> "This being on a lanyard is amazing. Strong positive note. COnsider us using
> this in other employee_role icons. Consider propogating this up into design
> documents. Amazing. A++" -- `gen:ui_icons:employee_role_security:v2`

> "There is something emerging with an emergent P from a doom meter filling up
> becoming the P in p(Doom) here that is strongly attractive, excellent. Keep
> and use this as a basis for more re-rolls as an avolutionary step."
> -- `gen:iconset_round2:gen_type_pdoom_us:v1`

> "DINg this bell is very good pickup, bureaucratic, I like it"
> -- `gen:game_icons:indicator_status_critical:v3`

The generator behind all three positives is the same: an unexpected but
*legible* object standing in for an abstract concept (a lanyard for a role, a
filling meter for a probability, a desk bell for bureaucratic alarm). The
generator behind all the rejections is the first symbol a stock-image search
would return. "Second-most-obvious symbol, rendered clearly" is a usable brief
line.

## Signal 6 (words) -- colour used to separate elements, not to set mood

Eight notes contain the word "colour". Almost none of them ask for a palette;
they ask for two things in one image to stop being the same colour:

> "Good, try a second colour for the camera."
> -- `gen:ui_icons:action_facility_security_upgrade:v1`

> "Make the arrow and bottom cog one colour and the upper cog a differnet
> colour to highlight difference" -- `gen:ui_icons:action_research_alignment:v1`

> "briefcase needs to be colour and visually distinct from foreground"
> -- `gen:action_icons_missing:lobby_government:v1`

> "needs more colour differentiation, ask or increase scope of style guide for
> assistance" -- `gen:ui_icons:ui_governance_oversight:v1` and `:v2`

This reconciles the saturation null with the contrast signal: he is not asking
for more colour, he is asking for more *separation*, which is the same request
as the contrast preference expressed in hue instead of luminance. Both are
"make the parts of the picture distinguishable at a glance", which is precisely
what a 1.7-second decision can see.

## The most useful thing he wrote

Not a taste statement -- a request for this document, written eleven days early,
inside a note on a security-camera icon:

> "Meta note: I think we want to craete some style design rules about, like
> primary and secondary clour groupings in our icons for a next-generation
> coherence pass because we keep getting things that are individually good,
> subtly with mayn upsides, but need coherence in direction. We can extract
> this from pulling detailed analysis of the little features of images I like
> and striving for collapsing into coherence from there. This is otherwise an
> excellent image."
> -- `gen:ui_icons:action_facility_security_upgrade:v1`, 2026-07-25

The stated problem is not quality, it is *coherence*: individually good, no
shared direction. That reframes the whole exercise. The measurement above found
what is already consistent (contrast, detail, brightness) and mostly found
absence everywhere else -- and absence of a shared direction is exactly the
complaint. The right response to this profile is not "generate more of what he
likes"; it is "pick a direction on the axes where he has no revealed
preference, apply it uniformly, and let him reject the direction rather than
individual images."

## One case where a written verdict lost to a slot pick

`icon_acquire_startup:v1` carries the note

> "This icon style is different and interesting, LLM, describe the prompts and
> so on to me that generated these?"

and then lost its slot to v2. Same shape for `doom_meter_frame:v3` -- "this
ouroborous like flavour is intersting, explore it more with a few other
variants?" -- which lost the frame role to v2. Enthusiasm in a verdict note is
about a DIRECTION worth exploring; it is not a vote for that file. Do not mine
`review_state.json` notes for pins.

The inverse also happened, and it is the cleanest positive datum in the corpus:
`gen_type_pdoom_us` had glowing notes on both v1 and v2, and v2 -- the one he
called "Exceptional" -- won the slot.

## GENERATION BRIEF FOR TOMORROW'S RUN

### Hold constant (revealed preference, n and p above)

1. **High internal contrast.** Aim for a p95-p05 luminance spread above ~0.50
   on the finished image (the chosen set averages 0.488 vs 0.454 rejected).
   If a prompt knob exists for "strong value structure / clear lights and
   darks", turn it up. Evidence: n=136, 74.3%, p<0.0001, plus his own
   "increase contrast" notes.
2. **Detailed over minimal.** Texture, grain, rendered depth. Evidence: n=136,
   71.3%, p<0.0001 on gradient density, corroborated by bytes/pixel on the
   clean subset (n=114, 64.0%, p=0.0035) and by "a bit too simple, try with
   more depth and texture and richness".
3. **Do not ship soft.** Five separate notes discard on "blurry" alone. Any
   upscale/denoise step that softens edges is fighting the two signals above.
4. **Human figures unidentifiable, and specifically not read-as-male.** Nine
   notes, one repeated verbatim four times. Use his own list: shot from the
   back, silhouette, hood, hat, mask, cloak, ambiguous-human-or-robot. This is
   a hard constraint, not a dial.
5. **Second-most-obvious symbol, rendered legibly.** No nuclear trefoil for
   doom, no padlock for safety, no chessboard for red-teaming, no MTG-shaped
   glyph for burnout. Concrete objects standing in for abstractions score
   highest with him (lanyard, desk bell, filling meter).
6. **Two-colour separation within each icon.** Foreground subject and its key
   sub-element in distinguishable hues. Four notes ask for exactly this. This
   is separation, not saturation.

### Vary widely (no revealed preference -- spend the variation budget here)

1. **Palette and saturation.** Paired saturation test: 55.1%, p=0.26. Nothing.
   Generate deliberately across amber / cyan / cool-blue / neutral families
   rather than assuming the CRT-amber house look wins -- the picks do not say
   it does. Include green variants specifically to settle the one weak hue
   result honestly rather than quietly designing around an uncorrected p=0.005.
2. **Composition -- centred vs offset, tight vs loose crop, negative space.**
   Off-centre distance: 52.9%, p=0.55, the cleanest null measured. Vary it
   freely; nothing here is being wasted.
3. **Subject treatment for scene art -- near vs far, lit vs silhouetted, warm
   vs cold key light.** Not measurable at n=7 heroes plus n=2 events. Treat as
   unknown and sample it.
4. **Prop and set vocabulary.** From the notes: "we ssem toh ave massively
   overindexed on the bankers lamp as an art asset. This probably meansd we
   need to generate a bunch more asset descriptions that *could* be in scenes
   so that llm's can chooose between different sets of objects". Write the
   object list before the prompts.

### Change how the budget is shaped

**Breadth, not depth.** v1/v2/v3/v4 win their slots at 33%/43%/25%/32% against
a 34% base rate -- iterating a prompt produced no measurable improvement across
119 slots. Prefer 4 *different* prompts at 1 variant each over 1 prompt at 4
variants, except where a note explicitly asks for evolution of a specific image
("Keep and use this as a basis for more re-rolls as an avolutionary step").

**Generate at the size the game draws, or close to it.** 22 of 136 "decisions"
were resolution ladders carrying no taste information, and the payload analysis
already showed 512px masters behind 70px tiles. Ladders cost money and produce
noise in the pick data.

**Expect to prune hard, and design the sheet for a one-second read.** He resolved
136 contested slots in 10.4 minutes at a 1.7-second median. Whatever cannot be
judged in a second at thumbnail size will not be judged; if a dimension genuinely
needs slow looking, it needs its own review sheet at full size, not a slot card.

### Confidence

**Moderate that this brief beats generating blind; low that it beats a
thoughtful art director's instinct.** The concrete case for it: the six
hold-constant items include four that come from his own written words rather
than from inference, and the two measured ones (contrast, detail) both clear
p<0.0001 with an honest permutation null and agree with what he typed months
earlier -- that convergence between the pixels and the prose is the main reason
to trust it. The lineage null alone should change tomorrow's spend shape, and
that is a bigger lever than any style dial.

The case against: the effect sizes are modest (about 9/255 of luminance spread),
35 of 136 slots went against the strongest signal, and the 1.7-second tempo
means this may be a profile of *what survives a fast glance* rather than of what
he actually values -- those are different things, and the second one is what a
game ships. The hue result is the one place where a careless reading of this
document could actively cost money by narrowing the palette on evidence that
does not survive multiple-comparison correction. **What would prove this brief
wrong:** hold contrast and detail high across tomorrow's run and the pick rate
on the next contested pass should rise above 34%; if it does not move, the
signals here were about the old batches' failure modes, not about taste.
