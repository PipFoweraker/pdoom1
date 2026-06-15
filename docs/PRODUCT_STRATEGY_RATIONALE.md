# pdoom — Product & Design Rationale

> **What this is.** The *strategic and philosophical reasoning* behind the pdoom ecosystem's architecture — the "why" that sits behind the structural decisions documented elsewhere. The mechanics themselves are documented in the existing tree (`ARCHITECTURE.md`, `BACKEND_PRIVACY_ARCHITECTURE.md`, `CONTENT_DISTRIBUTION_SYSTEM.md`, `CONTRIBUTOR_SYSTEM.md`, `EXTERNAL_REPOS_IMPLEMENTATION_PLAN.md`, `UI_DESIGN_VISION.md`, the `shared/` and `project-management/` ecosystem docs). This doc captures the rationale distilled from design conversations so the reasoning isn't lost. Add to `DOCUMENTATION_INDEX.md` if useful.

---

## The fact/opinion firewall — "fact: data. opinion: game."

`pdoom-data` holds ONLY factual events ("Sam Altman departed CEO role at OpenAI on 2023-11-17, sources [urls], confidence 0.95"). ALL interpretive/opinion analysis — poaching scores, reputation impacts, game classifications, doom modifiers — lives ONLY in `pdoom1` (the game/dev space). **This is a reputational-damage firewall:** it prevents accidentally publishing judgments like "we think researcher X is worth N safety points," which could cause real-world drama since the project judges real people's work. The public B2B value prop becomes "we track what actually happened, with sources," not "we rate how good/bad people are" — far more defensible and a broader market. *(Watch: sample data that blurs this fact/opinion line should be cleaned up to respect the barrier.)*

## IP-protection philosophy — moat is curation, not secret formulas

The IP strategy is deliberately NOT about hiding game-balance formulas. Pip fully expects and welcomes the community reverse-engineering balance (the **Path of Exile model**: make core mechanics discoverable but not trivially cloneable, and let players build solver tools). The real moat is three things competitors can't copy: **(1) the ~350-source curated data pipeline, (2) editorial judgment on which events matter, (3) game-design sense for how events feel in play.** The ONE thing to actually prevent is a wholesale clone of the entire game if it goes viral on Steam. So: open the historical events data (builds community trust + research value), keep the game-mechanics integration as the protected layer. Secondary goal served by openness: proving to funders the NGO self-funding effort is genuine, not a vanity mission.

## Open-data strategy — why the dataset is a separate public repo

The historical AI-safety event dataset lives in a standalone public repo (`pdoom-datasets` / `pdoom-data`), not inside the game repo, for two reasons: **(1)** the data is non-controversial and broadly useful to researchers/journalists/devs, so open-sourcing builds NGO academic credibility and invites contributions/source-verification; **(2)** it decouples licensing/visibility from the game code, so `pdoom1` itself can later be turned private when commercialised on Steam (revenue funding the NGO) **without** also hiding the dataset. (GitHub privacy is per-repository, not per-folder — the only way to expose some content publicly while keeping the rest private is to split repos.)

## Two products, one data backbone (design the backbone NOW)

Design the data backbone for **two products sharing it**, not retrofit later: (1) the **P(Doom) consumer game** with Steam revenue, and (2) an **"AI Safety Intelligence Platform"** — a "Bloomberg terminal for AI safety" as a B2B/research product with subscription/API revenue. The platform is entirely event-stream focused (not network/relationship focused). The game doubles as user research for the platform: players surface which events feel important and which framings resonate. So the data model should be "structured intelligence with multiple presentation layers" (one `intelligence_item` with facts/entities/timeline/confidence/impact_vectors, exposing a private "game" layer and public "research_dash"/"api" layers) rather than "events for game mechanics."

## Intelligence-platform presentation principle — factual, never predictive

Visualizations stay strictly factual: **correlation without causation, patterns without predictions.** Approved safe types: timeline clustering ("15 events across 6 orgs in Nov 2023"), entity-movement networks (person moved Org X → Org Y, as connections not quality judgments), source-diversity indicators ("reported by 8 sources" vs single-source), and geographic/funding-flow maps. The point is to help researchers ask better questions, not answer them. Implication: capture relationships and source metadata richly *internally* even though `pdoom-data` only exposes facts.

## Community hub = the website, NOT Steam

The website (not Steam forums) is the PRIMARY community hub. **Rationale:** Pip wants to control moderation/tone given the audience ("all sorts of oddbods"), avoid Steam's gamer-skewed demographics, and keep a professional look for B2B prospects — Steam forums get too spicy around AI topics. Engagement is a hybrid funnel: wide mouth (open public submissions via the website, low barrier, always thank/attribute submitters); middle (a curated trusted community on a forum with faster responses); deep (private bulk data feeds from partner orgs). Design distinct submission workflows keyed by source-trust level (community `needs_review`, forum-trusted `fast_track`, partner `auto_ingest`).

## Why the dashboard is a separate, deliberately un-monetized project

`pdoom-dashboard` (the "P(Doom) clock", a usdebtclock.org-style single-page global AI-risk meter) is kept as its own repo/site, separate from the game, so **people can model and argue about the serious metrics without being distracted by the cartoony, light-hearted game elements.** It ties to `pdoom-data` (not the game), with only soft brand tie-ins. Explicitly NOT an audience/monetization play: it's a "buy domain, park, iterate slowly, no public launch, add things for fun" side project whose real purpose is a **positive feedback loop motivating Pip to keep feeding data into `pdoom-data`** ("yay, I can add another button!"). Worth respecting that motivational function when deciding how much process to wrap around it.

## Asset sourcing follows licensing, not just aesthetics

When sourcing visual inspiration for the game's bureaucratic Win9x aesthetic, Pip prefers government/research-institution projects (e.g. CSIRO/Data61) over generic personal projects **specifically because their work is typically Creative Commons or otherwise open-licensed** — so it can be integrated directly and credited via attribution, rather than only used as loose "influence." Licensing clarity for reuse is the deciding factor, not aesthetics alone. (Always confirm the actual LICENSE file before integrating any component kit — e.g. ui95's MIT license was inferred, not verified.)
