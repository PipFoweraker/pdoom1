# Upgrades system -- asset brainstorm (pre-mechanics-review)

> Pip asked: "are there suggestions on what we can do that would also require some assets?"
> This is a BRAINSTORM, not ruled mechanics -- but it doubles as the art-generation target list.
> The frame: an **upgrade** is a purchasable/earnable thing that (a) drops a new sprite into a
> reserved office slot (the office visibly grows + gets fancier -- see the wireframe upgrade slots),
> (b) has a mechanical hook, and (c) usually feeds an existing system/appetite. Most come in
> era-tiers (scummy startup -> decent -> conspicuously-fancy megacorp), which is free art mileage.

## Why this is a good fit
- The office-reflects-your-state mechanic already wants tiered props -- upgrades ARE that, made a
  player choice instead of automatic.
- Appetites (ADR-0011: compute / prestige-first-author / mentees / money / mission-purity) give
  each upgrade a "who loves this" hook -- a prestige-hungry hire is happier with the fancy espresso
  machine; a compute-hungry one wants the GPU wall.
- Burnout/morale, doom mitigation, and attention all give upgrades numeric effects.

## The list

### Comfort / morale (reduce burnout; feed money/comfort appetites)
| upgrade | mechanical hook | feeds | art asset | tiers |
|---|---|---|---|---|
| Cushions / beanbags | small burnout resistance | morale | beanbag, floor cushions | 1 |
| Break couch | rest spot; slow burnout recovery | morale | couch (HAVE) | S/D |
| Standing desks | tiny productivity, "we care" signal | morale/prestige | standing desk | D/M |
| Nap pod | strong burnout recovery | morale | sleek nap pod | M |
| Rug / soft-furnishing | ambient cosiness (low-doom register) | flavour | rug | S/D |
| Potted plants | ambient morale | morale | plant (HAVE) + variants | 1 |

### Kitchen / social (morale; the conspicuous-status axis)
| upgrade | hook | feeds | art asset | tiers |
|---|---|---|---|---|
| Coffee -> espresso -> full cafe bar | escalating morale + a status flex | morale/prestige | drip (HAVE) / espresso (HAVE) / **cafe bar** | S/D/M |
| Fridge | morale | fridge (HAVE) | S/D |
| Snack shelf / free food | morale, mild money drain | morale | snack shelf | D |
| Kitchen bench | enables the above | (host slot) | bench (re-rolling) | S/D |

### Compute (feed compute appetite; enable/scale research)
| upgrade | hook | feeds | art asset | tiers |
|---|---|---|---|---|
| Server rack -> cluster -> exotic | +compute capacity | compute | rack (HAVE) / cluster (re-rolling) / **quantum/exotic rig** | S/D/M |
| GPU wall | big compute, big power draw | compute | glowing GPU wall | M |
| Cooling / server cage | compute uptime; mild security | compute/security | AC unit, caged rack | D/M |

### Prestige / status (feed prestige appetite; reputation)
| upgrade | hook | feeds | art asset | tiers |
|---|---|---|---|---|
| Trophy / awards shelf | reputation, recruiting pull | prestige | trophy shelf, framed awards | D/M |
| Framed published papers | prestige for first-authors | prestige-first-author | framed-paper wall | D/M |
| Conspicuously fancy espresso | pure flex (Pip's example) | prestige | chrome espresso (HAVE) / **gold-plated** | M |
| Reception / lobby | reputation; visitor events | prestige | reception desk, logo wall | M |
| Branded wall art / logo | identity | flavour | logo sign | D/M |

### Research / productivity
| upgrade | hook | feeds | art asset | tiers |
|---|---|---|---|---|
| Whiteboards | +research legibility | mentees | whiteboard (HAVE) | 1 |
| Bookshelf / library | slow skill growth | mentees | bookshelf (HAVE) | S/D |
| Extra monitors | per-desk productivity | -- | monitor (HAVE) tiers | S/D/M |
| Meeting room / war room | unlocks team actions | -- | meeting table (re-rolling) | D/M |

### Security / safety (doom mitigation; DQ-24 tech-infra)
| upgrade | hook | feeds | art asset | tiers |
|---|---|---|---|---|
| Air-gap / red-team corner | doom reduction | mission-purity | isolated terminal | D/M |
| Monitoring wall | early-warning on incidents | security | wall of status screens | M |
| Server security cage | leak resistance (vs Loose Lips quirk) | security | caged rack | D/M |

### Ambient / doom-flavour (mostly signal, not stats)
| upgrade | hook | feeds | art asset | tiers |
|---|---|---|---|---|
| Cat furniture | the cat likes it (Cat Whisperer quirk) | flavour | bed (HAVE), box (HAVE) | 1 |
| Emergency lighting | reads at high doom | flavour | red strobe, exit sign | doom 2+ |
| The rune wall / shrine | eldritch flavour at high doom | flavour | glowing rune wall (Bayes runes) | doom 3+ |

## How it plugs into the art pipeline
- Everything marked HAVE is generated. Everything else is a **prompt for a future sweep** -- mostly
  clean objects (warm-grime-heft, palette-locked, era-tiered), which is exactly what the current
  pipeline does well.
- The doom-flavour items pull their glow hues from the doom-intensity spec (rune wall = violet/
  eldritch band; emergency lighting = red/catastrophe band).

## For Pip / the mechanics review
- Is an upgrade a one-off purchase, or does it occupy a limited slot count (forcing choices)?
- Do upgrades tie to appetites strongly enough to matter in hiring/retention? (I think yes -- it
  makes the office a retention tool.)
- Which come as era-tiers vs one-shot? (Compute/comfort/kitchen scale well; trophies are one-shot.)
