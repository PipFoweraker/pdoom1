# Architecture Decision Records (ADRs)

This directory holds **Architecture Decision Records** — short, dated, immutable notes capturing a
significant decision, *why* it was made, and its consequences. The format follows
[Michael Nygard's original ADR pattern](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

## Why we keep these

P(Doom)'s documentation has drifted over time because decisions were made but the *reasoning* lived
only in commit messages, chat, or someone's head — so later docs silently contradicted earlier ones.
ADRs fix the **time axis**: each decision is recorded once, dated, and never edited after acceptance.
If a decision is later reversed, we add a *new* ADR that supersedes the old one (and mark the old one
`Superseded`), rather than rewriting history.

## Conventions

- Filenames: `NNNN-short-kebab-title.md` (zero-padded, sequential).
- Each ADR has: **Status**, **Context**, **Decision**, **Consequences**.
- **Status** is one of `Proposed` → `Accepted` → `Superseded by ADR-NNNN` / `Deprecated`.
- Once `Accepted`, the Context/Decision are **not edited**. New information → new ADR.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-retire-develop-branch.md) | Retire the `develop` branch (trunk-based on `main`) | Accepted |
| [0002](0002-win-condition-survival-spine.md) | Win condition: survival spine with a rare apex victory | Accepted |
| [0003](0003-godot-migration.md) | Runtime: migrate from pygame/Python to Godot 4.5.1 / GDScript | Accepted |
