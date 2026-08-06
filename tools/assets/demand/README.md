# tools/assets/demand/ -- the selection record

`slot_picks.json` answers ONE question, per slot: **which Library asset does
this slot pin?**

It does NOT answer "is this asset good" -- that is a verdict, it lives in
`tools/art_review/review_state.json`, and nothing in this directory reads or
writes it. The two are separate on purpose (ADR-0019, and
`docs/design/ASSET_PAYLOAD_ANALYSIS_2026-08-06.md` "The mechanism -- a word for
'good but not chosen'"):

| question | answers | unit | written | store |
|---|---|---|---|---|
| is this good? | taste | per ASSET | once, at review | `review_state.json` |
| is this THE one? | selection | per (asset, SLOT) PAIRING | every time a slot is re-picked | here |

**There is no "good but not chosen" label, and there must never be one.** An
asset Pip likes is a **Library** asset. An asset a demand entry names is
**chosen**. The nineteen up-arrows nobody picked are simply Library assets no
entry names -- the ABSENCE of a record, not a status to store. A stored
`chosen` flag would be a second write site that can silently disagree with the
manifest; that is exactly the shape that stranded 75% of the verdicts once.

## Round trip

```
python tools/art_review/build_slot_picker.py --open      # build + open the page
                                                          # pick; press E to export
python tools/art_review/apply_slot_picks.py <download>    # validate + merge to here
git diff tools/assets/demand/slot_picks.json              # THIS is the manifest diff
```

`apply_slot_picks.py --check` re-validates every recorded pick against a fresh
rebuild of the cluster model: the slot must still exist, the file must still be
a candidate for it, and the asset must still hold a `keep` verdict. Drift is
reported loudly and exits non-zero. Run it after any art batch lands.

## Entry shape

```json
"godot/assets/images/heroes/hero_office_at_dusk": {
  "status": "chosen",
  "source_file": "art_generated/hero_banners/v1/hero_office_at_dusk_v2_768.png",
  "source_asset": "gen:hero_banners:hero_office_at_dusk:v2",
  "note": "dusk v2 reads better at 408",
  "decided_at": "2026-08-06T10:00:00.000Z",
  "destination": "godot/assets/images/heroes",
  "draw_px": 408,
  "draw_why": "fanfare_popup.gd:107 custom_minimum_size Vector2(408, 0)"
}
```

`draw_px` / `draw_why` are the SIZE THE GAME DRAWS IT AT plus the consumer line
that sets it. They are carried here because ADR-0019 pt 4 makes promotion a
TRANSFORM, not a copy: the pull step needs the size, and the citation is what
stops the size from drifting into folklore. `draw_px: 0` means the source is
already at or below the drawn size -- nothing to shrink.

A frame role's answer has TWO parts and the record reflects that: `treatment`
(always) and `source_file` (only under `nineslice` / `whole`). Under
`styleboxflat` and `drop` no source image is used at all, so the picker does
not offer one and clears any source carried over from a previous treatment --
the record can never name a source nobody chose for the treatment that shipped.
`status` stays `""` while a role is half-answered, so a 9-slice role with no
source never reads as decided.

`status: "deferred"` is a real answer ("not yet") and keeps the slot in the
working set. Clearing a pick in the page and re-exporting REMOVES the entry
here -- reopening a decision is expected; taste sessions are not one-shot.

## What consumes this

Nothing yet. The demand manifest (ADR-0019 increment 1, mechanical) is the
intended consumer: each `chosen` entry becomes a manifest pin, and the pull
step renders the pinned Library master down to `draw_px` into
`godot/assets/**`. Until that lands, this file is a decision record and
absolutely nothing moves on disk.
