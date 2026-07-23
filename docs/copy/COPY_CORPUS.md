# P(Doom)1 -- Copy Corpus (RAW MATERIAL, not approved copy)

> **What this is.** A read-only archaeology pass that catalogs every piece of
> player-facing / public-facing COPY the project has produced across its
> iterations (pygame era -> Godot era), with provenance. Assembled 2026-07-23.
>
> **Purpose.** Give Pip a deck of his own prior thinking to write a Manifund
> funding application FROM, in his own words. **This is raw material. Nothing
> here is finished or approved copy.** No new taglines were written; entries are
> quoted verbatim from what already exists in the repo.
>
> **Voice tags used below:**
> - `[PIP]` -- first-person founder statement, a verbatim design-interview quote,
>   or a section explicitly marked "PIP:" / authored+committed by Pip. High
>   confidence this is Pip's own wording.
> - `[PIP-idea / Claude-prose]` -- the *thinking* is Pip's (distilled from his
>   design conversations / decisions) but the *sentences* were drafted by an
>   agent. Use the substance, rewrite the phrasing.
> - `[CLAUDE]` -- agent/assistant-generated doc prose (marketing tone, cheat-sheet
>   style, or an AI-drafted README/release note). Treat as inspiration only.
> - `[UNKNOWN]` -- can't reliably attribute.
>
> **Current game (the truth to check copy against):** Godot 4.5.1, pure GDScript,
> turn-based AI-safety strategy game. No Python runtime (the old pygame build and
> the Python<->Godot bridge are both retired). Version SSOT = `version.txt` =
> **0.11.0**. Survival/high-score framing: no turn limit, no expected victory
> (ADR-0002).

---

## 0. TL;DR -- the evolution of "what is P(Doom)1"

A short timeline of how the one-liner / description shifted (dates from git +
dated doc headers):

| Era | Approx date | Framing of "what it is" | Voice |
|-----|-------------|--------------------------|-------|
| Pre-semver prototypes v1-v3 | 2024 | "Bureaucracy Strategy Game"; basic resource-management prototype | [UNKNOWN] |
| pygame v0.2-v0.7 | Sep 2025 | "80s Retro Command Interface"; retro DOS-green bureaucracy sim | [CLAUDE] release notes |
| pygame v0.10.0 (last pygame) | Oct 2025 | "satirical strategy game... racing against well-funded opponents to solve the alignment problem before everyone dies"; "Unregulated AI poses an existential threat to humanity." | [CLAUDE/UNKNOWN] |
| Godot v0.10.1 (first Godot) | ~Oct-Nov 2025 | DELIBERATE copy shift: "satirical" -> "strategic simulation"; project.godot -> "AI Safety Lab Management Simulation" | [PIP-idea / Claude-prose] |
| Godot v0.11.0 (current) | 2026 | "Manage an AI safety lab racing to solve alignment before it's too late" + the "you can't win, you can only buy time" survival spine (ADR-0002) | [PIP / mixed] |
| Design-canon layer | 2026-06 / 07 | Deeper framing: "sandbox for a live research question", the open historical dataset as public good, "Bloomberg terminal for AI safety" | [PIP quotes + Claude prose] |

The single biggest deliberate change on record: the project consciously moved
**away from "satirical"** toward **"strategic simulation"** for "professional
tone for public presentation" (documented in `_website_export/docs/releases.md`).

---

## 1. TAGLINES / one-liners

| # | Text (verbatim) | Source | Date/Version | Voice | Current? |
|---|-----------------|--------|--------------|-------|----------|
| T1 | "Manage an AI safety lab racing to solve alignment before it's too late." | `README.md` line 3 (bold subtitle) | v0.11.0, README added 2025-07-30, last edit 2026-07-21 (Pip) | [PIP / mixed] | CURRENT |
| T2 | "Made with coffee and existential dread" | `README.md` line 63; `_website_export/docs/index.md` line 94 | 2025-2026, recurring | [PIP-flavored] | CURRENT (signature line) |
| T3 | "A satirical strategy game about managing an AI safety lab" | `_website_export/docs/index.md` frontmatter `description:` | v0.10.1 era, updated 2025-11-06 | [CLAUDE] | STALE (project deliberately dropped "satirical") |
| T4 | "A strategic simulation about managing an AI safety lab racing to solve alignment before it's too late." | `_website_export/docs/index.md` line 8 (bold) | 2025-11-06 | [PIP-idea / Claude-prose] | Mostly current (version stale) |
| T5 | "Unregulated AI poses an existential threat to humanity." | `archive/docs/README_OLD.md` (old root README) | v0.10.0, Oct 2025 | [CLAUDE/UNKNOWN] | SUPERSEDED (pygame-era README) |
| T6 | "AI Safety Lab Management Simulation - Strategic resource allocation and risk management" | `godot/project.godot` `config/description` | Godot era | [PIP-idea / Claude-prose] | CURRENT (ships in the build) |
| T7 | "P(Doom)" / subtitle "Bureaucracy Strategy Prototype" | `godot/scenes/welcome.tscn` (in-game main menu Title+Subtitle) | file added 2025-10-30, last 2026-07-21 | [PIP] | STALE-ish (says "Prototype"; "Bureaucracy" framing predates the "AI Safety" positioning) |
| T8 | "P(Doom): Bureaucracy Strategy Game" | `CHANGELOG.md` line 2 | changelog since 2025-08 | [UNKNOWN] | STALE subtitle |
| T9 | "A bootstrap strategy game about managing a scrappy AI safety lab with realistic funding constraints." | `_website_export/docs/player-guide.md` line 4; near-identical in `docs/PLAYERGUIDE.md` | v0.11.0 | [PIP-idea / Claude-prose] | CURRENT |

Uncommitted variant worth knowing about (exists only in a local worktree
`.claude/worktrees/ui-proposals/README.md`, NOT on main -- a proposed rewrite):
"You run an underfunded AI safety lab while better-resourced competitors race
toward AGI. There is no win screen -- alignment is not a thing you finish. What
you can do is buy time." -- [PIP-idea / Claude-prose], proposed, unshipped.

---

## 2. SHORT DESCRIPTIONS (1-2 sentences)

- **S1** [PIP / mixed] -- CURRENT. `README.md` line 19:
  > "You run an underfunded AI safety lab racing against well-resourced
  > competitors to solve the alignment problem. Make strategic decisions about
  > hiring, research priorities, and resource allocation. You can't stop
  > catastrophe -- you can only buy time; your choices determine how long you
  > hold P(Doom) back before a run ends."

- **S2** [PIP-idea / Claude-prose] -- CURRENT. `_website_export/docs/index.md`
  ("What is P(Doom)?" section):
  > "You manage a bootstrap AI safety lab with limited funds, racing against
  > well-funded competitors to solve the alignment problem. Make strategic
  > decisions about hiring, research, and resource allocation while P(Doom) rises
  > or falls based on your choices."

- **S3** [PIP] -- CURRENT. `docs/archive/game-design-pre-workshop1/GAME_DESIGN_CANON.md`
  section 1, explicitly marked "PIP:" (the one-paragraph pitch):
  > "You run an underfunded AI safety lab racing against well-resourced
  > competitors. Your choices about hiring, research priorities, and resource
  > allocation helps shape humanity's destiny."

- **S4** [PIP-idea / Claude-prose] -- CURRENT. `docs/PLAYERGUIDE.md` line 12
  (Strategic Challenge):
  > "Experience the real constraints of running an AI safety nonprofit - manage
  > weekly cash flow, make strategic funding decisions, and scale your team
  > efficiently while keeping doom levels low."

- **S5** [CLAUDE/UNKNOWN] -- SUPERSEDED. `archive/docs/README_OLD.md` (v0.10.0):
  > "In this satirical strategy game, you manage a bootstrap AI safety lab racing
  > against well-funded opponents to solve the alignment problem before everyone
  > dies. Experience the challenge of running a scrappy nonprofit in the
  > competitive AI safety space."

---

## 3. LONG DESCRIPTIONS / elevator pitch

- **L1** [PIP / mixed] -- CURRENT. `README.md` "About the Game" + Gameplay bullets.
  The load-bearing paragraph (line 27):
  > "You can't win -- you can only buy time. There's no turn limit and no victory
  > condition: every run ends in loss, and your score is how long you hold
  > P(Doom) back before it does. A good run beats your own previous best."

- **L2** [PIP] -- the canonical goal, marked "Goal (Pip, 2026-06-30)" in
  `docs/archive/game-design-pre-workshop1/GAME_DESIGN_CANON.md` section 2:
  > "Survive AGI -- and if possible ASI -- by keeping P(Doom) low for as long as
  > possible."

- **L3** [PIP / mixed] -- the win-condition framing prose, `docs/adr/0002-win-condition-survival-spine.md`
  (Decision section), deciders: Pip, 2026-06-30:
  > "P(Doom) is primarily a survival / high-score game. Doom trends upward (the
  > Doom Spiral / positive feedback). A run's achievement is how long and how low
  > the player holds P(Doom) -- a score, ranked on the weekly-seeded leaderboard.
  > Driving doom to 0 (ASI solved) is a real but rare apex victory for mastery
  > play, not the expected outcome."

- **L4** [CLAUDE/UNKNOWN] -- SUPERSEDED but historically interesting (the v0.10.0
  "positioning + value prop" block). `archive/docs/README_OLD.md`:
  > "Anonymous Competition: Deterministic lab names preserve privacy while
  > enabling rankings ... Strategic Gameplay: 12-13 turn games with meaningful
  > decision depth ... Bootstrap Economics: $100k starting funds with realistic
  > costs."

---

## 4. MISSION / VISION / POSITIONING (the AI-safety framing, public-good angle)

This is the richest seam for a funding application. Almost all of it is Pip's
thinking; the DESIGN_PHILOSOPHY quotes are verbatim Pip, the PRODUCT_STRATEGY
doc is Pip's strategy in Claude-drafted prose.

### 4a. What the game is *for* (all [PIP], verbatim from design interviews)

Source: `docs/game-design/DESIGN_PHILOSOPHY.md` (interview-extracted, quotes
preserved verbatim; dated inline). First filled 2026-07-04.

- **M1** (2026-07-04):
  > "The game is about the challenge facing real AI safety researchers,
  > grantmakers and philanthropists, wrapped in a game to communicate the
  > challenge while mitigating the actual despair."
  (Gloss, [CLAUDE]: "Not a persuasion piece -- a sandbox for a live research
  question ... let people stay in contact with the problem longer than despair
  normally permits.")

- **M2** (2026-07-04):
  > "the theoretical payoff is a few people learning a bit more about AI safety
  > as a side effect from playing an engagingly hard game, the same way young me
  > learned a bit about history by playing Civilization."

- **M3** (2026-07-04):
  > "my short or medium term time lines actually will likely come true in real
  > life and... AGI might be survivable but ASI won't be."

- **M4** (2026-07-12):
  > "people voluntarily adopting good actions will generate the space for better
  > actions to come about, and this is how small and middle power players can
  > affect things - norm and market setting"
  (Marked in the doc as "Pip's real-world theory of change ... never patched for
  freshness.")

- **M5** (2026-07-04, on audience/community):
  > "[patches] took this from 'a game 200 people might play, ever' to 'a game
  > where 30 nerds might enjoy playing this for long enough to form a community'
  > which actually seems better?"

- **M6** (2026-07-13, on the reality-tether):
  > "Otherwise I drift away from the guiding star of this having some utility as
  > something like a tool / scenario builder / argument fosterer."

### 4b. The public-good / open-dataset / two-products vision

Source: `docs/PRODUCT_STRATEGY_RATIONALE.md` (added+committed by Pip 2026-06-15;
"rationale distilled from design conversations"). Voice: [PIP-idea / Claude-prose]
-- the strategy is Pip's, sentences are agent-drafted.

- **V1 -- two products, one data backbone:**
  > "Design the data backbone for two products sharing it ... (1) the P(Doom)
  > consumer game with Steam revenue, and (2) an 'AI Safety Intelligence
  > Platform' -- a 'Bloomberg terminal for AI safety' as a B2B/research product
  > with subscription/API revenue. ... The game doubles as user research for the
  > platform."

- **V2 -- the open dataset as public good / NGO credibility:**
  > "The historical AI-safety event dataset lives in a standalone public repo ...
  > the data is non-controversial and broadly useful to researchers/journalists/
  > devs, so open-sourcing builds NGO academic credibility and invites
  > contributions/source-verification."

- **V3 -- fact/opinion firewall (the defensible public value prop):**
  > "The public B2B value prop becomes 'we track what actually happened, with
  > sources,' not 'we rate how good/bad people are' -- far more defensible and a
  > broader market."

- **V4 -- the moat is curation, not secrecy (Path of Exile model):**
  > "The real moat is three things competitors can't copy: (1) the ~350-source
  > curated data pipeline, (2) editorial judgment on which events matter, (3)
  > game-design sense for how events feel in play."
  Plus the funder-facing note:
  > "Secondary goal served by openness: proving to funders the NGO self-funding
  > effort is genuine, not a vanity mission."

- **V5 -- factual, never predictive (research-integrity positioning):**
  > "Visualizations stay strictly factual: correlation without causation,
  > patterns without predictions. ... The point is to help researchers ask
  > better questions, not answer them."

- **V6 -- the P(Doom) clock as a public risk meter (motivational flywheel):**
  > "pdoom-dashboard (the 'P(Doom) clock', a usdebtclock.org-style single-page
  > global AI-risk meter) ... so people can model and argue about the serious
  > metrics without being distracted by the cartoony, light-hearted game
  > elements."

- **V7 -- accumulation/evolution vision (league metabolism, [PIP] verbatim,
  DESIGN_PHILOSOPHY 2026-07-13):**
  > "I can run the game a month behind real time, update real world events into
  > the engine, balance patch, test, and deploy in a way that doesn't demand my
  > full-time attention."
  Gloss: "Reality becomes the map generator -- each league, another month of the
  real race enters the seed timeline."

- **In-game link (ships in the build):** `godot/scripts/ui/game_over_screen.gd`
  line 235 -- "Learn about real AI safety: aisafety.info". Main menu also has a
  "AI Safety Info" button -> https://aisafety.info/ (`welcome_screen.gd`).

---

## 5. VALUE PROPS (why it matters / who it's for)

- **P1** [PIP] design-test personas -- who plays / the fantasy. `docs/game-design/WORLD_AND_LORE.md`
  (2026-07-04):
  > "The Mogul -- builds the hundred-person lab; scale as strategy. The Hustler --
  > grows a we'll-do-it-faster, capabilities-endorsing venture and rides it;
  > money as strategy. The Operator -- skips to networking and politicking
  > straight into influence; favors as strategy."

- **P2** [PIP] the emotional value prop -- the three-ring meaning of a loss.
  DESIGN_PHILOSOPHY (2026-07-04):
  > "A good loss means you survived a few turns more than last time. A better
  > loss might be when you beat other people using a similar strategy in this
  > week's ladder. The best loss might be finding a new set of starting moves
  > that leads to everyone on the ladder adopting your early game for that meta
  > before a new balance patch."

- **P3** [CLAUDE] pygame-era feature value props (privacy-first framing), still
  partly true (deterministic, privacy-conscious). `archive/docs/README_OLD.md`:
  > "Privacy-First Design - Your data stays under your control. Deterministic
  > Gameplay - Reproducible games for competitive verification. Pseudonymous
  > Competition - Compete without compromising privacy."

- **P4** [PIP-idea / Claude-prose] contributor hook (community value). `README.md`:
  > "We immortalize our contributors in the game! Report bugs, suggest features,
  > or help with playtesting, and your cat can become an Office Cat in P(Doom)."

- **P5** [PIP-idea / Claude-prose] community-hub positioning (B2B-aware).
  `docs/PRODUCT_STRATEGY_RATIONALE.md`:
  > "The website (not Steam forums) is the PRIMARY community hub. ... keep a
  > professional look for B2B prospects -- Steam forums get too spicy around AI
  > topics."

---

## 6. "SNAPPY LITTLE JUDGMENTS" -- design-philosophy epigrams & characterful lines

These are the memorable turns of phrase. The `[PIP]` ones are verbatim quotes;
the `[CLAUDE-gloss]` ones are the interviewer's crystallizations of a Pip idea
(often the sharper single line, but not Pip's words -- rewrite before use).

### 6a. Pip's own phrasings [PIP]

- "you cannot win, only buy time, and you can't see what's killing you without
  paying" -- DESIGN_PHILOSOPHY (2026-07-04). (The load-bearing structural claim.)
- "like taking out a credit card to save the mortgage, then taking a job as a
  lobbyist to pay off the credit card, then lobbying to weaken financial
  regulation on AI firms which then leads to an increase in AI driven fraud which
  then funds Antagonist_Lab" -- DESIGN_PHILOSOPHY (2026-07-04).
- "these are the resources by which you get things done, given your tiny manual
  amount of hours per week (action points), you're going to hire costly humans
  who come with their own problems, bother." -- DESIGN_PHILOSOPHY (2026-07-04).
- "Doom Arrives With Your To-Do List Being Infinitely Long Still is a real
  possibility that I'm not shy of playing into." -- DESIGN_PHILOSOPHY (2026-07-12).
- "The simulation won't lie, but maybe our managers will give us rosy pictures of
  what's going on ... nobody wants to bring the boss bad news..." --
  DESIGN_PHILOSOPHY (2026-07-12).
- "I want my minions to bring me information! good minions!" -- DESIGN_PHILOSOPHY
  (2026-07-13).
- "the player is the heroic focus point of a lot of stuff (and blame when things
  go wrong!) that is nonetheless going to battle superhuman forces (some of them
  spooky) to save the world, the cat, and keep the receipts along the way" --
  DESIGN_PHILOSOPHY (2026-07-13).
- "with some time travelling foreknowledge of bitcoin prices, perhaps?" (the joke
  that became the time-loop framing) -- WORLD_AND_LORE (2026-07-04).
- "we're not saying or implying labs really do any of the truly weird stuff
  that's going to take place later in the game." -- WORLD_AND_LORE (2026-07-12,
  the event-horizon guardrail).
- "Admin is painful in this game, I want that to be part of the overhead." --
  DESIGN_PHILOSOPHY (2026-07-13).

### 6b. Interviewer crystallizations of Pip's ideas [CLAUDE-gloss]

(Sharp one-liners, but agent-authored -- these summarize Pip, they are not his
words. Great seeds; reword in his voice.)

- "Every mitigation is a loan." / "Skill is debt-portfolio selection."
- "The game must explain your death before it kills you." -- target loss-feeling:
  "tragedy ('I saw it coming'), never unexplained horror."
- "The sim never lies; characters do."
- "Author causes, never outcomes."
- "Staff are leverage, not simulation subjects."
- "The management grain coarsens as the org scales."
- "Idle staff don't exist; unmanaged staff do."
- "A turn is a plan you watch collide with reality."
- "The midgame begins when the world starts shooting back."
- "Attachment is built to be spent."
- "The admin view is not the game; the game is the fogged subset." (Simulate
  everything, gate only the view.)
- "The turn count is a badge, not a number."
- "Coarse hands, fine scoreboard."
- "Weirdness lives in cards, not the stack."

### 6c. Tone / flavor register [PIP + gloss]

- WORLD_AND_LORE tone north star (mix): "Dark comedy in flat CRT type over raw
  grief: 'HypNOTised: 2.1B' beats a casualty counter ... Papers, Please is the
  tonal north star: bureaucratic deadpan around enormous stakes."
- Diegetic time-loop line: "you've seen this world before." [CLAUDE-gloss of Pip's
  bitcoin joke]
- UI era vibe [CLAUDE, `godot/UI_STYLE_GUIDE.md`]: "Early 2000s Command Center -
  Bloomberg terminals, NATO C2 systems, Windows XP/Longhorn prototypes."
- README sign-off [PIP-flavored]: "Made with coffee and existential dread."

---

## 7. Pip's authentic voice -- lines only he wrote (seed for a future voice guide)

Pulled together from the verbatim `[PIP]` interview quotes. These are the
highest-confidence "his own words" and the best raw material for a funding
application written in his voice. All from `docs/game-design/DESIGN_PHILOSOPHY.md`
and `docs/game-design/WORLD_AND_LORE.md` (2026-07-04 to 2026-07-16), plus the
GAME_DESIGN_CANON "PIP:" pitch.

1. "The game is about the challenge facing real AI safety researchers,
   grantmakers and philanthropists, wrapped in a game to communicate the
   challenge while mitigating the actual despair."

2. "the theoretical payoff is a few people learning a bit more about AI safety as
   a side effect from playing an engagingly hard game, the same way young me
   learned a bit about history by playing Civilization."

3. "people voluntarily adopting good actions will generate the space for better
   actions to come about, and this is how small and middle power players can
   affect things - norm and market setting"

4. "A good loss means you survived a few turns more than last time. A better loss
   might be when you beat other people using a similar strategy in this week's
   ladder. The best loss might be finding a new set of starting moves that leads
   to everyone on the ladder adopting your early game for that meta before a new
   balance patch."

5. "my short or medium term time lines actually will likely come true in real
   life and... AGI might be survivable but ASI won't be."

6. "Survive AGI -- and if possible ASI -- by keeping P(Doom) low for as long as
   possible." (the canonical goal, GAME_DESIGN_CANON, "Goal (Pip, 2026-06-30)")

Characteristic voice markers: lowercase-casual asides, self-interrupting
qualifiers ("which actually seems better?"), Civ/Factorio/XCOM/PoE/Tarkov
analogies as load-bearing reasoning, the word "bother" for personnel pain, dry
gallows humor around catastrophe, and a genuine theory-of-change (norm/market
setting by small players) sitting under the jokes.

---

## 8. STALE / CONTRADICTORY public copy -- cleanup candidates

Flagged for Pip's README/positioning review. Ordered roughly by how public-facing
and how wrong.

1. **`godot/README.md` -- fully stale architecture (HIGH priority).** Still
   describes the retired Python bridge: "The game logic runs in Python via
   `shared_bridge/bridge_server.py`", "Python Version: 3.13+", "Godot UI
   (GDScript) <-> Python Bridge <-> Shared Game Logic", "Status: Phase 4 MVP -
   Minimal Functional UI". Last updated 2025-10-17. The current game is pure
   GDScript, no Python runtime. Directly contradicts root `CLAUDE.md`. Anyone
   landing on the godot/ folder reads a wrong mental model.

2. **`_website_export/docs/index.md` -- wrong win condition + stale version
   (HIGH, it's the website).** "Try to reach turn 100 with P(Doom) at 0%"
   CONTRADICTS ADR-0002 (no turn limit; survival/high-score; victory is rare).
   Also "Download v0.10.1", "Current Version: v0.10.1" (SSOT is 0.11.0), and
   frontmatter `description: "A satirical strategy game"` -- re-introduces the
   "satirical" word the project deliberately dropped.

3. **`godot/scenes/welcome.tscn` -- in-game menu subtitle (MEDIUM, ships in the
   build).** Title subtitle = "Bureaucracy Strategy Prototype". Two problems:
   "Prototype" undersells a shipping v0.11.0 game, and "Bureaucracy" is the older
   framing that predates the "AI Safety Strategy Game" public positioning. (Also
   contains literal emoji in button labels: trophy on "Leaderboard", link glyph
   on "AI Safety Info" -- note vs the repo's ASCII-in-source rule, though .tscn
   isn't ASCII-gated.)

4. **`CHANGELOG.md` line 2 -- old subtitle (LOW).** "All notable changes to
   P(Doom): Bureaucracy Strategy Game" -- same stale "Bureaucracy Strategy Game"
   subtitle.

5. **`godot/README_UI.md` -- contradicts the scene-nav MUST rule (MEDIUM, dev-
   facing).** Documents "Scene Transition Pattern: All navigation uses
   `get_tree().change_scene_to_file(...)`" -- this is exactly the pattern
   `CLAUDE.md` now forbids (must go through `SceneTransition` autoload; the
   direct call caused the v0.11.0 leaderboard segfault). Also credits a "Ported
   from Pygame" lineage and Python 3.13.

6. **Root `README.md` screenshot (LOW).** References
   `screenshots/pdoom_screenshot_20250918_104357.png` -- a 2025-09-18 capture,
   i.e. pygame-era UI, on the current Godot README. Verify it shows the Godot
   build before the funding push; likely a stale pygame screenshot.

7. **Version drift across surfaces (LOW-MEDIUM).** `version.txt`=0.11.0, root
   README="v0.11.0" (OK), website="v0.10.1" (stale). Whatever the funding app
   links to should be reconciled to one number.

8. **`archive/docs/README_OLD.md` and pygame-era release notes (NO ACTION --
   correctly archived).** These carry "satirical... before everyone dies" and
   "Unregulated AI poses an existential threat" copy. They're historical, live
   under `archive/`, and are fine where they are -- listed here only so the old
   framing isn't mistaken for current.

---

## Appendix: source files consulted

- `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md` (root)
- `godot/README.md`, `godot/README_UI.md`, `godot/project.godot`,
  `godot/scenes/welcome.tscn`, `godot/UI_STYLE_GUIDE.md`,
  `godot/scripts/ui/game_over_screen.gd`, `godot/scripts/ui/welcome_screen.gd`
- `docs/game-design/DESIGN_PHILOSOPHY.md`, `docs/game-design/WORLD_AND_LORE.md`
- `docs/PRODUCT_STRATEGY_RATIONALE.md`, `docs/adr/0002-win-condition-survival-spine.md`
- `docs/PLAYERGUIDE.md`,
  `docs/archive/game-design-pre-workshop1/GAME_DESIGN_CANON.md`
- `_website_export/docs/index.md`, `player-guide.md`, `releases.md`
- `archive/docs/README_OLD.md`, `archive/ARCHIVE_INDEX.md`,
  `docs/releases/RELEASE_NOTES_v0.2.0.md` / `v0.3.0` / `v0.7.0` / `v0.10.0`

Provenance dates from `git log --diff-filter=A` (file-add) and `git log -1`
(last-touch), cross-checked against dated headers inside the docs.
