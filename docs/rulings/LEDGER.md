# Ruling ledger -- rulings with no code to live next to yet

Hand-appended. One `RULING:` line per entry, newest at the bottom. The
convention is argued in `RULINGS_CONVENTION.md`; the generated index is
`RULINGS.md`.

A ruling belongs HERE only when it has no natural home. If it governs a file,
write the line next to that file instead -- it is more use where it bites.

RULING: 2026-08-15 -- the ruling road is cross-repo from day one, federated: each repo scans itself and emits rulings.json, an aggregator reads them, nothing writes back -- flavour: estate-process -- mechanism: scripts/generate_rulings.py
RULING: 2026-08-15 -- naming a mechanism is OPTIONAL on a ruling, and the generated index reports which rulings have none -- flavour: estate-process -- mechanism: scripts/generate_rulings.py
RULING: 2026-08-15 -- Tier W (website disclosure) ships first and standalone; Tier G (in-game motifs and epoch marks) stays ruled-but-unbuilt -- flavour: art-provenance -- mechanism: docs/art/MOTIF_AND_WATERMARK_PROTOCOL.md
RULING: 2026-08-15 -- flaw:<thing> joins the harvest vocabulary as the negative counterpart to element:, because the sweeps are mostly negative and prose cannot be counted -- flavour: art-review-vocabulary -- mechanism: tools/art_review/serve_review.py HARVEST_DOC, emitted to docs/art/NOMENCLATURE.md
RULING: 2026-08-15 -- an embedded CA-signed C2PA credential outranks every provenance heuristic; it becomes evidence tier S and resolves an asset out of the unknown set -- flavour: art-provenance -- mechanism: tools/assets/backfill_provenance.py credential_origin
