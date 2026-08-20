# Credits -- P(Doom)1

P(Doom)1 -- a turn-based AI-safety strategy game.

> **This file is the SOURCE OF TRUTH for the in-game credits screen.** It still
> lives at the repo root, outside `godot/`, so it is not itself bundled -- instead
> `scripts/generate_credits.py` derives `godot/data/credits.json` from it, and a
> pre-commit `--check` blocks a stale copy (same anti-rot pattern as
> `DQ_INDEX.md`). Edit THIS file; never hand-edit the JSON.
>
> Fields marked **[Pip to fill]** / **[Pip to confirm]** are placeholders only Pip
> can resolve. The generator DROPS any entry still carrying a placeholder, so an
> unresolved TODO can never reach a player's screen -- it just silently does not
> appear. Resolving one is what makes it ship.
>
> **EVERY SECTION HERE IS PLAYER-FACING.** Prose you write in a section body is
> rendered as a credits-screen note, not kept as a maintenance comment -- so
> ADR-0002 applies throughout (the Music section spells this out, and a test
> scans `godot/data/credits.json` for banned wording). Notes to yourself belong
> in the commit message or in "Notes for Pip" at the bottom, never in a section.
> **Diff `godot/data/credits.json` before committing** -- on 2026-08-20 an
> internal remark about this file having been wrong was one `generate` away from
> appearing on the credits screen, caught by reading that diff and by nothing
> else.

## Game

- **Design, direction, and development:** Pip Foweraker  *(adjust name form as preferred)*
- **Engine:** [Godot Engine](https://godotengine.org) 4.5.1 (MIT License)

## Cats

The office cat in your lab is a real cat. Eight were contributed by their people,
with permission, and `office_cat.gd` picks one at random per run -- so every one
of them reaches players.

Table columns are load-bearing: `Cat` is the display name, `Photo by` is the
credit line shown in game, `Asset` must match a key of `CAT_NAMES` in
`godot/scripts/ui/office_cat.gd` (a GUT test fails if the two rosters drift). A
`Photo by` cell still carrying a `[Pip to confirm ...]` marker renders the cat
WITHOUT a credit line rather than printing the marker.

| Cat | Photo by | Asset |
|---|---|---|
| Arwen | Matilda | web-arwen.jpg |
| Arwen & Chuck | Matilda | web-arwen-chuck.jpg |
| Chucky | Nicki T. | web-chucky.jpg |
| Doom Cat | Pip | web-doom-cat.jpg |
| Luna | Nicki T. | web-luna.jpg |
| Mando | Nicki T. | web-mando.jpg |
| Missy | Spicy | web-missy.jpg |
| Nigel | Nicki T. | web-nigel.jpg |

Credit names are the forms each contributor agreed to, settled with each of them
in the group chat where the photos were volunteered -- confirmed by Pip
2026-08-20, on his account of that conversation rather than a linkable artifact.
`art_source/cats_incoming/INVENTORY.md`'s "Custodian" field, still the only
record this repo holds, is therefore a transcription of an agreed credit line
and not internal metadata reused as one. Change the name HERE and the game picks
it up on the next generate.

## Music

**Original adaptive score** (the composed five-tier doom-band soundtrack + the
run-end and menu cues that ship today):

Wording note, not shipped: this section is PLAYER-FACING now, so it obeys ADR-0002
and must not name a "victory" cue -- `test_no_win_condition_copy.gd` scans
`godot/data/credits.json` and fails if it does.

- **Composition, direction, and taste authority:** Pip Foweraker -- the musician
  and director; every note judged by ear over the workshop sessions.
- **Composed with:** Claude (Anthropic's Claude Code, "Fable"), as the
  live-coding instrument and studio hand, under Pip's direction. The score was
  workshopped in Strudel patches and rendered to the game's audio beds.
- **Authoring tool:** [Strudel](https://strudel.cc) (live-codeable music in the browser).

**Original placeholder tracks** (the ambient beds that stood in during
development, now retired but preserved in `archive/audio/`):

- **Written and performed by:** **[Pip to fill -- friend's name / handle / "prefers anonymity"]**
  -- DJ-session ambient tracks, generously given to the project. Pip authored
  the (AI-safety pun) track titles; project holds full usage rights. With thanks
  for setting the sonic tone the composed score grew out of.

## Playtesting

- **[Pip to fill -- playtester name(s) / handle(s)]**

## Tools and third-party components

- [Godot Engine](https://godotengine.org) -- game engine (MIT)
- [GUT](https://github.com/bitwes/Gut) -- Godot unit test framework (dev/CI, MIT)
- [Strudel](https://strudel.cc) -- music authoring (composition sessions)
- Art pipeline & attributions: **[Pip / art lane to fill]**  *(pixellab, image-gen tooling, etc.)*

## Aesthetic gratitude

The score learned from, but did not copy, a set of north-star artists (Master
Musicians of Bukkake, Philip Glass, and others). They are inspirations only,
with no affiliation or endorsement.

The full lineage is documented in `docs/audio/REFERENCE_TRACKS.md`.

---

### Notes for Pip (resolve before any public/shipped credits use)

- [ ] Confirm your preferred credited name/handle (used "Pip Foweraker" above).
- [ ] Fill your friend's name/handle for the original tracks -- or "prefers
      anonymity" if that is their wish. Confirm the rights note in writing
      (the music brief says you hold full rights; STEM_CATALOGUE.md suggests
      capturing that as a saved message).
- [ ] Fill playtester acknowledgement(s).
- [ ] Decide how prominent the AI-collaboration credit should be -- the wording
      above is honest-and-plain; dial up or down to taste.
- [ ] Fill the art-pipeline attributions (owned by the art lane, not this session).
- [x] In-game credits screen: BUILT. Welcome menu -> `Credits`, generated from
      this file. Cats get the top section.
- [x] **Cats: RESOLVED 2026-08-20.** Each contributor's credit form was agreed
      with them in the group chat where the photos were volunteered -- confirmed
      by Pip. The "Custodian" field was therefore never merely internal
      metadata; it recorded a form each person had chosen. The eight rows above
      stand as shipped.
- [x] **Doom Cat: RESOLVED 2026-08-07.** Contributed by Pip. The inventory's
      "Office (default/mascot)" custodian field was internal metadata, not an
      absence of a contributor.
