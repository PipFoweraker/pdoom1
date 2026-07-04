# ADR-0004 — SA amended: channels with provenance, lead-time semantics, decision-flip test

- **Status:** ACCEPTED — this amends and accepts ADR-0001; build second, after ADR-0003
- **Date:** 2026-07-04
- **Session:** Fable workshop #1

## Context

ADR-0001 proposed "spending buys sight" as the flagship sink. The workshop stress-tested
it against Pip's peak verb — *"triaging in a race against death"* — and against the
realization: *"I am used to thinking about the game with universal powers as god mode /
admin, whereas the player mostly starts ignorant about the world the same way a fresh
spawn in Tarkov / fresh game of Civilization / entirely fresh run of some Roguelike."*
The hypothesis survives, amended in four ways.

## Amendments

### 1. Simulate everything; gate only the view

The world-model always runs at full fidelity — every rival lab, every doom source,
computed every turn exactly as the admin-mode intuition imagines. SA purchases never add
simulation; they only remove blindfolds from state that already exists. The
discovered/undiscovered opponent mechanic already works this way; this generalizes it.
Implementation is therefore UI gating plus per-source visibility flags, not a subsystem.

### 2. SA is not a meter; it is channels with provenance

Espionage-sight, alliance-sight, media-sight, research-sight — each reveals overlapping
but non-identical slices of the same sim, each priced in a different currency, each with
side effects (espionage corrodes governance and burns alliance standing; alliance-sight
is slow, public, and obligates you via ledger entries; media-sight is cheap and noisy).
Channel investment is a **build-identity axis** — the run's founding-location choice.

### 3. Lead-time semantics: the game must explain your death before it kills you

From Pip: *"Ideally the late game will bring with it some forcing of understanding onto
the player as to how they're going to lose (modulo their efforts to stop it?)"* — so doom
sources become legible **for free as they become lethal**. What SA purchases buy is not
exclusive truth but **lead time**: everyone eventually sees the thing killing them;
paying means seeing it while you can still act. This resolves the deduction-vs-triage
tension: sight serves triage, not puzzle pleasure.

### 4. The acceptance test is decision-flip rate

ADR-0001's constraint ("every unit of sight must open a decision") was too weak for a
triage game. Sharpened: **the fraction of reveals that change the player's next action
or reorder their priorities.** A reveal that confirms the existing plan feels like a
tax; a reveal that flips the plan feels like the game. Instrument playtests (log
declared-intent-before-reveal vs action-after-reveal); kill any SA feature whose flip
rate stays low. This is a falsifiable design criterion — measure it, don't eyeball it.

## The honesty boundary (Papers, Please register)

Conspiracy-tinged weirdness lives in the **provenance of information, never in the sim
lying about itself**: redacted documents, cranks who are occasionally right, a source
who might be a plant — all on-theme, because real AI-race epistemics look like that.
Instruments may be *fallible* (rival info ops are thematically perfect), but the game
must be honest about *how* they can be fooled, and counter-intelligence is its own
purchase. Rams #6 applied one level up: honest about dishonesty.

## Beacons

As ADR-0001, plus: the lead-time rule protects against the one loss-feeling Pip did not
choose ("I still don't know what killed me" — horror), while preserving the one he did
(tragedy: "I saw it coming and couldn't stop it").
