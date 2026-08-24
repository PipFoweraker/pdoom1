# Funding p(Doom)1

> **RETIRED 2026-08-23.** The funder-facing architecture pitch that lived at this path
> advertised a $25K/$75K/$150K/$300K annual funding ladder that was never the ask being
> made, alongside claims about the build that were false -- most consequentially a "Web"
> shipping platform that does not exist. It is preserved, unedited apart from a header
> recording each false claim, at
> [`docs/archive/2026-08-23-architecture-funders/ARCHITECTURE_FUNDERS.md`](archive/2026-08-23-architecture-funders/ARCHITECTURE_FUNDERS.md).
>
> This page is a signpost, not a second ask. There is one ask.

## The ask

p(Doom)1 is funded through a single all-or-nothing campaign:

- **Minimum:** USD 14,500 -- below this, nothing is collected
- **Goal:** USD 48,000
- **Closes:** 2026-09-09
- **Page:** <https://manifund.org/projects/fund-development-of-pdoom1>

Progress figures move daily, so they are deliberately not typed here. Follow the link and
let it resolve.

## Where the money goes

The breakdown is **data, not prose**. It lives in
[`docs/copy/budget.json`](copy/budget.json) as seven line items, each carrying its own
provenance -- whether a figure is measured against logged spend, priced as Pip's own
labour, or openly awaiting a quote. Every published rendering of the budget is generated
from that file by [`tools/render_budget.py`](../tools/render_budget.py):

```bash
python tools/render_budget.py --check    # validates the columns and the declared gap
python tools/render_budget.py            # renders the published breakdown
```

The file also records what is **not** known -- including a $500 rounding gap between the
line-item column and the published minimum, which the renderer recomputes and refuses to
publish if the stated size disagrees. That gap is named rather than papered over.

## Anything written for funders must satisfy `budget.json`'s constraints

The `constraints` block in `docs/copy/budget.json` is binding on all outward-facing copy.
In short:

1. **Nobody has been hired, commissioned, approached, quoted or engaged.** Every figure is
   conditional; a single slip into past tense makes the copy a misrepresentation.
2. The game is free and **source-available** -- an interim licence, **not** an open-source
   one. A pledge funds the work, not a licence and not early access.
3. **Do not type the raised total or days remaining.** Link the page and let it resolve.
4. **Do not identify the project's first backer**, by name or by description.
5. **p(Doom)1 is not finished.** No copy may frame it as a launch, a 1.0, or a completed
   thing.

Read the block itself before writing; this summary is a convenience, and the file wins.

## What the build actually is, today

Verified against the repository on 2026-08-23. Correct these here rather than restating
them from memory elsewhere:

| | |
|---|---|
| Version | `version.txt` reads **0.14.3**; newest tag **v0.14.2** |
| Engine | Godot 4.5, GDScript |
| Shipping targets | **Windows, Linux, macOS.** There is **no web build and no mobile build** -- `godot/export_presets.cfg` defines exactly three presets |
| macOS signing | **Ad-hoc at best, not notarised** (`codesign/identity=""`, `notarization/notarization=0`). Do not promise Mac users a clean install without saying this |
| Scale | ~76,900 lines of GDScript across 301 files, excluding addons |
| Tests | ~1,644 `test_` functions across 166 test files |
| CI | 15 workflows. **None of them performs a Godot export** -- platform builds are not produced by CI from these presets |

## Developer-facing architecture

For how the game is actually built -- systems map, extension points, ADR series -- see
[`docs/ARCHITECTURE.md`](ARCHITECTURE.md). That is the live document; this one is only
about money.
