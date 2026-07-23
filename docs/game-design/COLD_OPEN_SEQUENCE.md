# Cold-Open Sequence -- the time-loop framing (design + build direction)

> Extends ONBOARDING_STORY_DESIGN.md (#801). Creative direction from Pip
> 2026-07-23. This doc captures the SEQUENCE, the diegetic-onboarding thesis, the
> dials, and a phased build so it is not lost. Story copy is Pip's to finalize;
> back-story beats are deliberately fuzzed ([REDACTED-FUZZ]) to preserve mystery.

## Why this is more than a cutscene (the thesis)

1. **Diegetic onboarding via the phone.** Instead of a tutorial popup, the player
   picks up their character's phone, enters a passcode, and the phone reveals the
   game's UI ONE APP AT A TIME -- bank (money), messages (advisor / objectives).
   This directly answers the first playtester's "too much information at once": it
   reveals sequentially, it gives the player AGENCY in the intro (they DO
   something), and it gives the advisor a diegetic home (a text from a "Mysterious
   Helpful Stranger").
2. **The time-loop justifies the ladder.** The player is sent back in time to buy
   time against doom. Each run = a loop / a send-back; the leaderboard (everyone
   replaying the same seed) = everyone is a time-traveler comparing loops. This
   retro-justifies the roguelike-replay structure IN FICTION. Already seeded in
   lore: WORLD_AND_LORE's "with some time travelling foreknowledge of bitcoin
   prices, perhaps?" and the "you've seen this world before" line.

## The sequence (Pip's beats -- copy is placeholder / Pip's to finalize)

1. PORTAL opens (spinny effects) over black.
2. Segmented fade-up from black; elements "pop" into existence.
3. Back-story (Pip lays out): humanity reaches a final crisis in 20[REDACTED-FUZZ]
   and ... everyone dies? A last-ditch effort -- a mountain --
4. FLASHBACK: a massive scaling-out dolly-zoom / bewildering pullback over racks
   and racks of sizzling compute, all channeling their energy toward -> a TIME
   MACHINE.
5. Fade in: "Doom is coming!"
6. Disorientation: "But... when am I? What can I do? ... What *day* is it?"
7. "*checks pockets* -- a primitive phone!"
8. Passcode: "I wonder what my passcode is..." -> PLAYER ENTERS 4 DIGITS -> unlock.
9. Unlock reveals: BANK ACCOUNT (your money) + MESSAGES.
10. First message [advisor / first-lever nudge]: "Hello past me! I am expository
    filler (for now). Get to work! -- Mysterious Helpful Stranger" -> points at the
    first move (hire a researcher): the lever-legibility nudge from #801.

## Phasing -- crisp parts, brutal decisions

**SHIP-NOW CORE** (delivers ALL the onboarding value on modest art; non-score,
ladder-safe):
- Segmented fade-up from black + the cold-open text beats (Pip's, already liked).
- The phone: lock screen -> 4-digit passcode entry -> home with Bank + Messages.
- Bank shows starting funds; Messages shows the Stranger's first message = the
  first-lever nudge (wires to the button-glow in main_ui).

**UPGRADE LAYER** (delight polish; later "little patches" for the tester):
- The spinny PORTAL (procedural shader -- see dials).
- The dolly-zoom compute-racks -> time-machine cinematic (the expensive bit; a LITE
  stand-in is a static "racks -> machine" image with a scale + fade).
- Richer plot reveals / more messages / Pip's back-beats.

## Dials (creative knobs)

- **PORTAL:** recommend a PROCEDURAL SHADER (rotating radial UV distortion) over
  generated+rotated frames -- cheaper, crisper, infinitely tunable, fits the
  "spinny effects" and the flat-CRT aesthetic. Knobs: swirl speed + direction,
  ring count/thickness, radial distortion strength, glow size, colour (on-brand:
  CRT phosphor green/amber, or an ominous doom-red), optional scanline overlay. The
  only baseline image needed is the portal "mouth"/centre; the shader does the
  spin. (Generated frames stay an option for a painterly look -- more art cost,
  less tunable.)
- **FADE-UP / POP-IN:** staged Tween timeline. Knobs: segment timing, pop easing
  (overshoot/bounce vs linear), reveal order.
- **DOLLY-ZOOM (upgrade):** a true 2D dolly-zoom is hard; fake it with a scaling
  background + parallax layers, or a pre-rendered sequence. LITE = static image +
  scale/fade.
- **PHONE:** deliberately "primitive" / grungy early-smartphone. Knobs: case wear,
  cracked screen, era. Passcode keypad interaction. (SEED, not scoped now: the
  phone could grow into a persistent diegetic HUD -- messages = advisor/event feed,
  bank = finances. Big idea; defer.)
- **MESSAGE:** sender persona / name / tone / count; the Stranger is the advisor
  channel.

## Reusable techniques + aesthetic motifs (2026-07-23)

**Shader-as-animation-capability [Claude uplift, noted by Pip].** Choosing a
procedural shader for the portal is not a one-off -- the same technique (shader
uniforms driven by Tweens) becomes a general, cheap, tunable ANIMATION capability
reusable across the game over time, instead of hand-animating or re-generating
frames. Build the portal; keep the technique.

> BUILT 2026-07-23 (UPGRADE-layer portal, standalone -- cold-open core untouched):
> - Shader: `godot/assets/shaders/time_portal.gdshader` (rotating vortex; rings,
>   radial swirl distortion, glowing core, CRT scanlines; good with zero tuning).
> - Every dial is a uniform; `open_progress` (0..1) is the reveal -- Tween it 0->1
>   to "pop into existence" (1->0 to collapse). Colour presets in the header:
>   doom-red (default), CRT phosphor-green, amber.
> - Live tuning harness: `godot/scenes/dev/portal_shader_demo.tscn` (dev-only; a
>   slider per uniform + colour presets + a "Play open" button). Run with F6.
> - Full technique + the exact cold-open wiring hook (add a portal rect as the
>   first beat, Tween `shader_parameter/open_progress` 0->1):
>   `godot/assets/shaders/README_shader_animation.md`. Wiring left for Pip.

**The Editor's benevolent hand -- early-game gentle rigging [Pip].** Any-4-digits
unlocks -> phrase the success as "Oh! how lucky!". This is the subtle hand of the
Editor: doom is guaranteed long-term, but the OPENING has a few things predictably
go the player's way (a little) -- the passcode works, the cat turns up. Model: PoE,
where you know you won't die on the beach before your first support gem. Worth its
own principle home (relates to Pip's "no early loss < 6 turns" + "author causes,
never outcomes"): the early game is gently benevolent so the player is hooked before
difficulty bites. Keep it as fortune / being-looked-after, not "the game is easy".

**The Baroque-Cycle redaction motif [Pip idea + Claude tuning].** For spooling text
/ info reveals: a "*fzzZZt*" of denial -- overlay / obscure / de-crisp. Conceit from
Neal Stephenson's Baroque Cycle: teasing censorship ("went to dear with Mr D_____",
"the spring of the year 166-"). Cheap, builds delight + familiarity, on-brand with
the CRT-glitch look and the already-fuzzed crisis year. TUNING (Claude):
- Redact NARRATIVE / LORE, NEVER mechanical / lever info the player needs to decide.
  Fuzzing the story = delight; fuzzing the levers re-breaks the playtester's
  legibility complaint. Crisp levers, mysterious lore.
- Use it SELECTIVELY -- the tease lives in the selectivity. Redact everything and
  nothing is mysterious; it becomes noise.
- Give it a DIEGETIC redactor for meaning: the same "Editor" / "Mysterious Helpful
  Stranger" who gently guides you is also WITHHOLDING (future-you can't tell past-you
  too much without breaking the timeline?). The hand that helps is the hand that
  redacts -- this unifies the Editor's-hand and redaction motifs and seeds the
  plot-reveal-later.

**3-frame cross-fade animation -- ship-now-achievable [Pip].** Old-school RPG
expressiveness on the cheap: generate a few KEYFRAMES (variations of the hero image
via the existing gallery / pixellab / gpt-image workflow -- "this, but nudged ~10%
toward that perspective/mood"), then quick-cross-fade 3 frames. Reference: the Civ II
leaderhead anger animation (decline QE's lopsided tech trade -> the escalating
scowl). Target fidelity: ~Return to Zork. No real animation pipeline needed.

## Build sketch (for the VS Code agent)

- New scene `ColdOpenSequence.tscn`, entered via `SceneTransition` BEFORE
  `main.tscn` (hook: `config_confirmation` -> `increment_games_played` ->
  `SceneTransition.go_to(cold_open)` -> main), show-once via the
  `last_seen_intro_version` gate (see ONBOARDING_STORY_DESIGN.md).
- Beat-driver: an array of beats `{kind: text|portal|flashback|phone, payload,
  duration}`; a Tween sequence advances them; ESC/click skips.
- Phone: a Control with lock-screen -> keypad (4 digits) -> on-unlock, reveal Bank
  + Messages panels. RECOMMEND any-4-digits unlocks ("I wonder what my passcode
  is" is diegetic hand-waving) -- friendlier than a real code, no dead-end.
- Messages panel renders the Stranger message; its CTA wires to the first-lever
  glow in `main_ui` (the #801 nudge).
- Portal (upgrade): a `ShaderMaterial` on a `TextureRect`; the dials above become
  shader uniforms exposed for tuning.
- NON-SCORE: pure presentation; does not fork the ladder.

## Open decisions for Pip

1. Portal: procedural shader (rec) vs generated frames?
2. Passcode: any-4-digits unlocks (friendlier, rec) vs a real code to find/guess?
3. Does the phone become the persistent HUD later, or stay an intro device?
   PARKED for a design workshop [Claude original, hold + recycle per Pip]. If built,
   it is reusable (messages = advisor/event feed, bank = finances). Ship the MINIMUM
   (phone as intro device) now; do not over-invest in the phone UI until the
   workshop decides whether it becomes the diegetic HUD.
