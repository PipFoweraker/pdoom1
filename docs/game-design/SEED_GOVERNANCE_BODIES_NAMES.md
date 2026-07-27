# SEED: Governance bodies -- tier structure + name pools (V1 draft)

> **SEED-grade.** Drafted 2026-07-27 evening for Pip's Wednesday reaction.
> Nothing here is ruled. The structure half-page answers the "must boards be
> external?" question; the three pools are RAW STOCK for a second creative
> pass (orchestrator hybridizes). Range over polish -- weird ones are kept
> deliberately.
>
> Read against: `godot/data/bodies.json` (3 placeholder bodies, schema
> id/name/focus/weight/description), `rivals.gd` roster
> (DeepSafety/CapabiliCorp/StealthAI), `RESEARCH_STREAMS_PROPOSAL.md` s2e
> (three influence stocks; gates are threshold expressions over Politics /
> Money / Technology), WS3A daylog Milestone 1420 framing bank
> (bureaucracy-simulator intro, CoD death screen, ALL HAIL HYPNODRONE) and
> R4 ballot 4 (4-way founder hours: doors / approvals / audits / reserve).
>
> **Siblings (2026-07-27 R5 emit batch):** `SEED_GOVERNANCE_NAMES_YESAND.md`
> (the Fable yes-and pass over this doc), `SEED_CONFERENCE_RHYTHM_BREAK.md`,
> `SEED_VIGNETTE_SPECS.md`. Day record: `WS3A_DAYLOG_2026-07-27.md`.

---

## PART 1 -- STRUCTURE: do bodies have tiers?

**Short answer: no, they must not all be external.** The current roster is
all-external because it was minted as the adoption counterparty to the rival
labs -- an outward-facing readership. But the game's best joke is the
self-audit, and that joke needs a body INSIDE the building. Proposal: bodies
carry a `tier` field, and tier is a maturity/severity ladder that the player
climbs by being noticed.

    tier: internal -> state -> international
    (a fourth, `civil`, is parked below -- press/forums/community, the
    body that has no power and all the reach. Flag for Pip: in or out?)

### INTERNAL -- your own safety board. Exists turn 1. You appoint it.

- **Grants:** internal legitimacy -- a signed-off safety case is a
  prerequisite some STATE bodies later ask to see. Cheap adoption (weight
  low, ~0.1) but always available. Also grants *cover*: a bad outcome with a
  board sign-off costs less reputation than one without.
- **Demands:** founder hours. The internal board is the natural
  **destination of the AUDIT hour type** (R4 ballot 4) -- audits report TO
  someone, and this is who. Unaudited optimistic self-reports flow up to a
  board that then certifies them. That is the whole irony in one arrow.
- **Capture dial:** the board has an `independence` scalar the player
  affects by who they appoint and how they respond to findings. Captured
  board = cheap sign-off, zero external credibility (STATE bodies discount
  its attestations). Honest board = expensive (it says no) and its
  attestations carry weight upward. This is the internal-vs-external
  exchange rate, and it should be legible.
- **Escalation trigger:** none -- it is the day-1 tier. But it can COLLAPSE
  (mass resignation event) when capture and doom both run high, which is a
  loud, cheap, thematic failure state.

### STATE / NATIONAL -- arrives with VISIBILITY.

- **Trigger:** reputation / media attention crossing a threshold, not
  capability. You get regulated when people notice you, which is the true
  and slightly unfair mechanic.
- **Grants:** Politics influence, funding doors (grants, procurement),
  legal safe harbour. A pickup here is durable -- matches the s2e
  "non-compute -> Politics, slow but durable" pump.
- **Demands:** disclosure (reveals your internals to rivals -- information
  leakage as a real cost), compliance hours, and *attendance*: hearings
  consume founder days and interact with the travel/exposed-while-
  travelling ruling.
- **Escalation:** state bodies gain teeth as doom rises. Same body, harder
  asks -- a consultation invitation at low doom becomes a compulsory
  notice at high doom. Escalating an existing named body beats spawning new
  ones; the player learns the name and then learns to fear it.

### INTERNATIONAL -- arrives with CAPABILITY ESCALATION.

- **Trigger:** frontier capability (yours or the leader's) crossing a
  threshold. Doom-driven, not fame-driven -- you can be obscure and still
  summoned, if the frontier moves.
- **Grants:** the only bodies that can act on RIVALS. Adoption here is the
  high-weight prize (0.5+) and the only lever that slows CapabiliCorp
  without you outspending it.
- **Demands:** slow, procedural, and multi-turn -- an international process
  is a commitment, not a transaction. Also *coordination*: they demand
  things that only work if rivals comply too, so their asks can fail through
  no fault of yours (the defection texture).
- **Escalation:** they arrive late and resolve slowly, so the design job is
  making the player feel they should have started the process ten turns ago.

### Cross-tier notes

- **Vertical pressure:** an internal board's attestation is INPUT to state
  bodies; a state body's finding is input to international ones. That gives
  the tiers a pipeline rather than three parallel scoreboards.
- **The self-audit irony, stated plainly:** the player appoints the body
  that judges the player, funds it from the same pool it audits, and staffs
  it with hours stolen from research. Every honest choice there is a
  capability sacrifice. That is the game.
- **Schema hooks (data-only, additive, no reader change needed):**
  `tier` ("internal"|"state"|"international"), `unlock` (threshold
  expression, same shape as s2e gates), `independence` (0..1, internal
  only), `teeth` (scales with doom).
- **Roster shape suggestion:** 1-2 internal, 3-4 state, 2-3 international.
  Names below are sorted loosely so a hybridizer can pull per tier.

---

## PART 2 -- POOL 1: STRAIGHT (a policy wonk nods)

Real-world plausible. Boring on purpose -- these are the load-bearing names
that make the satire in Pool 3 land by contrast.

1. Interim Frontier Model Standards Board -- the current placeholder, sharpened
2. Office of Compute Accountability
3. National AI Safety Institute
4. Frontier Systems Evaluation Directorate
5. Model Evaluation and Assurance Council
6. Bureau of Algorithmic Standards
7. Joint Committee on Emerging Technology Risk
8. International Compute Verification Regime
9. Advanced Systems Licensing Authority
10. Standing Panel on Model Deployment
11. Compute Allocation Registry
12. Office of the Technology Ombudsman
13. Interagency Working Group on Model Provenance
14. Frontier Capability Reporting Scheme
15. Global Partnership on Advanced AI -- deliberately toothless-sounding
16. Independent Evaluations Consortium
17. Council of National AI Regulators
18. Directorate-General for Digital Risk
19. Select Committee on Autonomous Systems
20. Model Incident Reporting Authority
21. Treaty Secretariat on Compute Thresholds
22. Chief Scientist's Advisory Panel on AI
23. Statutory Review of Frontier Model Regulation
24. Office of Emerging Technology Assurance
25. Multilateral Compute Verification Task Force
26. Public Inquiry into Automated Decision Systems
27. Standards Harmonisation Sub-Committee (AI)
28. National Critical Systems Inspectorate

---

## PART 3 -- POOL 2: IN-HOUSE / IN-WORLD

Names a lab self-mints, plus the nicknames staff actually use. Register
matched to DeepSafety / CapabiliCorp / StealthAI: compound, earnest,
slightly too on-the-nose. Nicknames included because in-fiction shorthand is
where the humanity is.

1. Internal Safety Board -- the day-1 default; deliberately plain
2. Responsible Scaling Committee
3. Model Release Board
4. Deployment Readiness Review
5. Capability Threshold Committee
6. Publication Review Board -- decides what you're allowed to publish
7. Dual-Use Screening Panel
8. Ethics and Societal Impacts Committee
9. Office of the Chief Safety Officer
10. Independent Safety Oversight Trust -- "independent"; you fund it
11. Standing Red Team Panel
12. Incident Review Board
13. Charter Compliance Office
14. Preparedness Council
15. Model Welfare Working Group -- earnest, easily mocked, possibly right
16. Internal Whistleblower Ombudsman
17. Scaling Policy Custodian -- one person, enormous authority, no budget
18. The Long Table -- staff nickname for the exec safety review
19. The Sunday Group -- meets when something has gone wrong
20. The Kill Switch Committee -- what staff call the shutdown authority
21. Safety Advisory Group (SAG) -- the acronym is the joke internally
22. Founders' Conscience Committee -- what the board was called before legal
23. Alignment Assurance Function
24. Pre-Deployment Sign-Off Chain
25. The Tuesday Standup That Became Governance
26. Voluntary Commitments Working Group
27. Research Norms Committee
28. Internal Frontier Council -- the one that meets without the founder

---

## PART 4 -- POOL 3: THE PDOOM REGISTER

Wry, Australian-inflected, deflates authority while telling the truth.
Rule applied: it must still be a name a real committee could have landed on.
Acronyms that spell something unfortunate are the workhorse. The "mob" /
"You Beaut" moves are used SPARINGLY (three total) so they stay funny.

**Unfortunate acronyms (a committee that lost a bet):**

1. Panel on Alignment, Nomenclature, Interpretability and Compute (PANIC)
2. Directorate for Oversight of Optimisation Methods (DOOM) -- almost too good
3. Standing Committee on Advanced Model Safety (SCAMS)
4. Bureau of Legitimate Oversight, Assurance and Transparency (BLOAT)
5. Office for Oversight of Predictive Systems (OOPS)
6. Committee on Oversight, Verification, Escalation and Response (COVER)
7. Secretariat for Harmonised Auditing, Metrics and Evaluation (SHAME)
8. Council for Risk Assessment, Systems and Harm (CRASH)
9. National Office for Prudent Escalation (NOPE)
10. Working Group on Harm, Ethics and Emerging Deployment (WHEED)
11. Federal Unit for Beneficial and Aligned Research (FUBAR) -- maybe too much
12. Bureau of Unified Model Provenance (BUMP)
13. Joint Oversight of Kinetic Escalation (JOKE)
14. Framework for Escalating Assessment of Risk (FEAR)
15. Office of Model Governance (OMG) -- nobody noticed for two years

**Truth-telling by over-honest naming:**

16. Select Committee on Things We Cannot Un-Invent
17. Royal Commission into Things That Have Already Happened
18. Interim Interim Standards Board -- second "interim" added by amendment
19. The Register of Compute We Know About
20. Multi-Stakeholder Roundtable on Everyone Being Very Reasonable
21. Office of the Inspector-General of Vibes
22. National Frontier Model Safety Framework Implementation Steering Group
23. Standing Committee on the Committee -- terms of reference under review
24. Voluntary Code of Conduct Monitoring Arrangement (Non-Binding)
25. Advisory Body with No Statutory Power (Est. 2027)
26. The Not-Yet-Legislated Register
27. Coalition of the Willing to Sign Something
28. Department of Prime Minister and Cabinet (AI Taskforce) -- three people, one inbox

**Australian deflation (used sparingly -- these three only):**

29. The Compute Mob -- what everyone calls the Registry; nobody says its real name
30. You Beaut National Model Register -- named during a funding announcement
31. Bureau of Model Meteorology -- forecasts doom like weather, with a percentage

**Wildcards / possibly too weird (kept deliberately):**

32. eDoom Commissioner -- eSafety's cousin; can order takedowns of models
33. The Ethics Guy -- internal tier; a body of one, on a fixed-term contract
34. Australian Frontier Model Authority (Interim) (Provisional)
35. Committee of Blokes Who Know a Bit About Servers -- state tier, rural
36. Office of the HypnoDrone Registrar -- late-game only; ALL HAIL
37. Section 12 Notice Issuing Unit -- named after the paperwork, not the job
38. Tribunal of Last Resort (Waiting List: 14 Months)

---

## Notes for the second pass

- **Hybridization seams:** Pool 1 gives the noun-stack, Pool 3 gives the
  acronym; the strongest names usually come from a Pool 1 body wearing a
  Pool 3 nickname (e.g. formal name "Global Compute Registry", player-facing
  feed calls it "the Compute Mob"). That argues for a `nickname` field in
  bodies.json -- formal name in the roster UI, nickname in the feed.
- **Register discipline:** if every body is a joke, none of them are. My
  suggested mix is roughly 60% Pool 1 / 25% Pool 2 / 15% Pool 3 in the
  shipped roster, with Pool 3 concentrated in the DESCRIPTION line rather
  than the name (the existing three placeholders already do this well --
  "Counts the chips. Declines to say what it does with the numbers.").
- **Existing three:** all read as STATE tier. If tiers land, they stay
  where they are and we add internal + international around them rather
  than reworking.
- **Open question for Pip:** does the CIVIL tier (press / forums / the
  comment thread the death screen links to) exist as a body, or is that the
  media system's job? Overlap risk is real.
