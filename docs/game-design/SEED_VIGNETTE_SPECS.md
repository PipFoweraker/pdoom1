# SEED: Vignette specs V1 -- 30 fade-in hero images + one line

> SEED, not decided canon. DRAFT, 2026-07-27. Register target: GTA loading
> screen crossed with the death-screen voice recorded in
> `WS3A_DAYLOG_2026-07-27.md`'s "Milestone (1420)" -- self-deprecating,
> dark-comic, technically literate, never explains the joke.
> ALL 30 ARE STAND-INS. They exist so the fade-in shell can ship with content
> in it; an artist-onboarded sweep replaces the images later and probably half
> the captions with them.
>
> **NO-LIES RULE APPLIED:** every caption sets mood only. None claims an
> effect, a stat change, or a mechanic. If a caption reads like a tooltip,
> it failed and should be cut.
>
> **SILHOUETTE PRINCIPLE (Pip, the cat):** where content rotates or is
> seed-picked, the image must not commit -- silhouette, backlight, rear
> three-quarter, cropped-at-the-neck, obscured by rain/glass/blinds. An image
> that names a specific cat/rival/researcher locks a variable that the sim
> wants free.
>
> GENERIC = safe to fade in anywhere (mood filler, rotation pool).
> KEYED = only makes sense at its trigger; do not put in the generic pool.
>
> **Siblings (2026-07-27 R5 emit batch):** `SEED_CONFERENCE_RHYTHM_BREAK.md`
> (specs 02-04 + 29 are this seed's mini-scene beats), `SEED_GOVERNANCE_BODIES_NAMES.md`,
> `SEED_GOVERNANCE_NAMES_YESAND.md`. Day record: `WS3A_DAYLOG_2026-07-27.md`.

---

## 01 cat-in-the-alley  [KEYED]
TRIGGER: first stray-cat event fires (core_events "A Stray Cat Appears!"),
shown BEFORE the choice panel.
IMAGE BRIEF: Rear view from an office doorway at night, keys still in hand at
frame edge, wet alley beyond lit by one sodium lamp; a cat-shaped SILHOUETTE
low in the mouth of the alley, no breed, no colour, no face -- just the shape
and two lamp-glints where eyes would be.
CAPTION: "While locking up the office for the night, you notice you are being
evaluated."

## 02 conference-departure  [KEYED]
TRIGGER: attend-conference action confirmed, immediately before fade-out.
IMAGE BRIEF: Pre-dawn kerb outside the office, one wheeled bag, taxi indicator
smearing orange on wet asphalt, the office windows still lit behind -- someone
up there is not leaving.
CAPTION: "Four days away. The org will be fine. The org has never once been
fine."

## 03 conference-floor  [KEYED]
TRIGGER: conference mini-scene opens (tableau option 2 in the rhythm-break
seed).
IMAGE BRIEF: Wide expo hall from a mezzanine, banner text deliberately blurred
past legibility, lanyard crowd rendered as a low-contrast mass, one booth
lit much brighter than the rest.
CAPTION: "Everyone here is either solving it or selling it, and the badges do
not distinguish."

## 04 conference-return  [KEYED]
TRIGGER: fade-in on the turn the founder returns, above the "while you were
away" panel.
IMAGE BRIEF: Office at the exact moment of walking back in, bag still on the
shoulder, desk under a drift of printouts, a mug someone else left, blinds
striping the whole room.
CAPTION: "Nobody died. Several things got worse politely."

## 05 taxi-window-rain  [GENERIC]
TRIGGER: generic pool, any inter-scene transition; weight higher on
travel-flagged turns.
IMAGE BRIEF: Back seat of a taxi, camera over the passenger's shoulder from
behind so the face never resolves, city lights bokeh through rain-beaded
glass, meter glow the only sharp thing in frame.
CAPTION: "Somewhere between the airport and the office, the plan quietly
changed."

## 06 airport-gate-0540  [GENERIC]
TRIGGER: generic pool, transit slot.
IMAGE BRIEF: Empty departure gate before dawn, rows of identical seats, one
laptop open casting blue on an unoccupied chair, tarmac black beyond the
glass.
CAPTION: "You have read this slide deck eleven times. It has not improved."
NOTE: Deliberately no person in frame -- founder-identity-neutral.

## 07 shuttle-bus-industrial  [GENERIC]
TRIGGER: generic pool, transit slot; good for datacentre/compute-related
turns.
IMAGE BRIEF: Interior of a half-empty shuttle bus on a ring road at dusk,
seat-backs in the foreground, out the window a fenced low-rise building with
no signage and a great many air handlers.
CAPTION: "The tour guide called it a campus. There were no windows on the
second building."
FORESHADOW: drone taxonomy (unnamed) -- see spec 08 and 21.

## 08 airport-baggage-drone  [GENERIC]
TRIGGER: generic pool, transit slot. Deliberately unremarkable placement.
IMAGE BRIEF: Baggage hall, carousel empty, high wide shot; near the ceiling a
small four-rotor SILHOUETTE holding station, motion-blurred just enough to be
deniable, nobody in the frame looking at it.
CAPTION: "The airport has automated the part where someone watches you."
FORESHADOW: drone taxonomy, unnamed. Do NOT letter or brand the drone.

## 09 late-night-single-desk  [GENERIC]
TRIGGER: generic pool; weight up when the turn resolves late in a simulated
week or after several consecutive high-effort turns.
IMAGE BRIEF: Open-plan office with every light off except one desk lamp and
one monitor, chairs pushed in at every other desk, city dark through the far
window.
CAPTION: "The building's motion sensors gave up on you around eleven."

## 10 empty-desk-first-hire  [KEYED]
TRIGGER: first researcher hired, shown the turn BEFORE they start.
IMAGE BRIEF: A single new desk, still bare -- unopened monitor box, a chair
with the plastic on, a sticky note on the blank screen -- shot at eye level so
it dominates the frame.
CAPTION: "Tomorrow somebody sits here and this stops being your problem alone."

## 11 server-hum  [GENERIC]
TRIGGER: generic pool; weight up on compute-related turns.
IMAGE BRIEF: Narrow rack aisle, no people, status LEDs as the only colour,
faint haze of cold air, deep perspective so the aisle runs out of focus.
CAPTION: "It sounds like a held breath. It is doing exactly what you asked."

## 12 lease-signing  [KEYED]
TRIGGER: office upgrade / lease action confirmed.
IMAGE BRIEF: Empty commercial floor at handover, keys and one unsigned page on
bare concrete, afternoon light in long parallelograms, dust visible.
CAPTION: "Thirty-six months. Ask yourself what you think happens in thirty-six
months."

## 13 first-doom-spike  [KEYED]
TRIGGER: first significant doom increase of the run.
IMAGE BRIEF: Office window at night from inside; the room is fine, the reader
is fine, but the reflection in the glass shows the room slightly wrong --
one more chair than there should be.
CAPTION: "Nothing in the room changed. Your estimate of the room did."
NOTE: caption must not name a number or a direction of change.

## 14 the-breakthrough-3am  [KEYED]
TRIGGER: capability-breakthrough event fires.
IMAGE BRIEF: A whiteboard photographed from an angle so the writing is
unreadable, half-erased, one hand still holding the marker cropped at the
wrist, harsh overhead light.
CAPTION: "It works. Everyone in the room agrees it works. Nobody volunteers
why."

## 15 the-leak  [KEYED]
TRIGGER: research-leaked event fires.
IMAGE BRIEF: A phone face-up on a dark desk at night showing a wall of text
too small to read, the screen glow lighting nothing else in the room.
CAPTION: "Someone you fed has published your work in a font you did not
choose."

## 16 whistleblower-carpark  [KEYED]
TRIGGER: whistleblower-approaches event fires.
IMAGE BRIEF: Underground car park, one vehicle, two figures at extreme
distance rendered as SILHOUETTES with no identifying detail, concrete columns
receding, fluorescent tubes with one flickering.
CAPTION: "They picked the meeting spot. That is already most of the
conversation."

## 17 audit-boardroom  [KEYED]
TRIGGER: internal audit / security-vulnerability event fires.
IMAGE BRIEF: Long conference table, laptops closed, one open folder, chairs on
the far side occupied by figures cropped at the shoulders so no faces are
visible, blinds half shut.
CAPTION: "They have been very polite for forty minutes, which is how you know."

## 18 regulation-hearing  [KEYED]
TRIGGER: proposed-regulation event fires.
IMAGE BRIEF: Committee room from the witness's seat -- microphone huge in the
foreground, the bench beyond deliberately out of focus, water glass sweating.
CAPTION: "The people writing the rules would like a short answer, and there
isn't one."

## 19 media-scandal-doorstep  [KEYED]
TRIGGER: media-scandal event fires.
IMAGE BRIEF: The office entrance seen through a long lens from across the
street, two camera operators waiting, the glass door reflecting sky so the
lobby is invisible.
CAPTION: "The story ran at six. Nobody called for comment, which was the
comment."

## 20 burnout-kitchen  [KEYED]
TRIGGER: burnout-crisis event fires.
IMAGE BRIEF: Office kitchen after hours, sink stacked, twelve identical mugs,
one chair pulled out and turned away from the table, harsh strip light.
CAPTION: "Someone rinsed every mug and then went home at two in the afternoon."

## 21 delivery-hover  [GENERIC]
TRIGGER: generic pool; slightly favoured mid-to-late run.
IMAGE BRIEF: Suburban street at dusk from a first-floor window, a small
delivery aircraft SILHOUETTE descending toward a neighbour's lawn, the box
already lit by its own downlight, a curtain in the foreground half drawn.
CAPTION: "The neighbourhood has stopped looking up. That took about eight
months."
FORESHADOW: drone taxonomy, unnamed. Same lineage as 08; keep both anonymous.

## 22 rival-silhouette-hallway  [KEYED]
TRIGGER: rival-lab sighting / poaching event, or the conference mini-scene's
surprise beat (rhythm-break seed section 5).
IMAGE BRIEF: Hotel hallway, someone turning a corner at the far end -- a
SILHOUETTE with a lanyard, no face, no logo, no readable badge -- carpet
pattern running to a vanishing point.
CAPTION: "You recognise the walk. You are not going to bring it up."
NOTE: non-commitment is mandatory here; the rival roster rotates.

## 23 password-1234  [KEYED]
TRIGGER: competitor-security-breach event fires (the "1234" one).
IMAGE BRIEF: A monitor in a dark room, login prompt filling the frame, four
password dots, a sticky note beside the bezel with its writing turned away
from camera.
CAPTION: "Millions of records, and the only thing standing in front of them was
a joke you have told."

## 24 payroll-ledger-dawn  [KEYED]
TRIGGER: cash falls below a warning threshold / funding-crisis event fires.
IMAGE BRIEF: A desk at first light with a printed spreadsheet, a phone face
down, and a coffee gone cold with the surface skin visible; no screen in frame.
CAPTION: "You have done this arithmetic four times and it keeps arriving on
time."

## 25 league-week-opening  [KEYED]
TRIGGER: league/competitive week starts.
IMAGE BRIEF: A wall-mounted display in a dim office showing an abstract
league board, names deliberately illegible at this distance, one chair pulled
up close to it.
CAPTION: "Somewhere out there, a hundred other people are also convinced they
have the safe plan."

## 26 compute-handshake  [KEYED]
TRIGGER: compute-partnership event fires.
IMAGE BRIEF: Two hands mid-handshake cropped tight, both in unremarkable
sleeves, a glass wall behind reflecting a server hall's blue.
CAPTION: "Cheap compute, generous terms, and one clause you read twice and
signed anyway."

## 27 systems-failure-torchlight  [KEYED]
TRIGGER: critical-system-failure event fires.
IMAGE BRIEF: Rack aisle in emergency lighting, one torch beam, cable trays
overhead, everything else red-black.
CAPTION: "Redundant, they said, and they were right about the word."

## 28 the-cat-again  [KEYED -- REPLAY]
TRIGGER: any run AFTER the player has completed at least one run; fires the
first time the office is locked up in the new run, before any cat event.
IMAGE BRIEF: Same alley as spec 01, same lamp, same rain -- but the alley is
empty, and the composition leaves the exact spot where the silhouette stood
conspicuously vacant.
CAPTION: "Locking up. Nothing in the alley tonight. You check twice."
NOTE: only lands if 01 has been seen; the payload is the absence. Do NOT show
this on a first run.

## 29 the-same-conference-room  [KEYED -- REPLAY]
TRIGGER: second-or-later run, on the first conference departure of that run.
IMAGE BRIEF: The spec 03 expo hall, but from the floor rather than the
mezzanine, and one booth in the middle distance is unlit and unstaffed -- an
empty carpeted rectangle with a number on the floor.
CAPTION: "Booth 214 is empty this year. Last time you were here, it was not."
NOTE: no explanation offered, ever. If a later system fills 214, good; if not,
the ambiguity is the point.

## 30 the-quiet-morning  [GENERIC]
TRIGGER: generic pool, low weight; best as the calm before a heavy turn.
IMAGE BRIEF: Empty office at 7am, chairs square, monitors dark, one window
open, a single sheet of paper lifting slightly in the draught.
CAPTION: "For about nine minutes a day, this is just an office."

---

## Coverage check
- Cat: 01, 28. Conference cycle: 02, 03, 04 (+29 replay).
- Transit: 05 taxi, 06 airport, 07 shuttle, 08 airport-hall (4 minimum met).
- Drone foreshadow, unnamed: 08, 21 (+07 adjacent).
- Quiet office: 09 late night, 10 empty first-hire desk, 11 server hum, 30.
- Replay-only: 28, 29.
- GENERIC (rotation pool, 9): 05, 06, 07, 08, 09, 11, 21, 30 -- plus none
  others; everything else is KEYED to a named event or action.
- Event-space spread: funding 24, hiring 10, breakthrough 14, leak 15,
  whistleblower 16, audit 17, regulation 18, media 19, burnout 20, rival 22,
  breach 23, compute 26, infra failure 27, lease 12, doom 13, league 25.

## Known gaps / not written on purpose
- No caption references a stat, resource, or outcome (no-lies).
- No image names a specific person, cat, rival lab, or product.
- Pay-equity, interpersonal-conflict, and mental-health events (core_events)
  deliberately have NO vignette: a hero image over a human-harm event reads as
  aestheticising it. Handle those in text, or hand them to a writer.
