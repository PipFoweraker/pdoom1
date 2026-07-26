# Role: Creative Director (content/video), P(Doom)1

> Status: DRAFT for Pip review, 2026-07-26. Not committed anywhere yet.
>
> PROPOSED PERMANENT HOME: `pdoom1/docs/content/` (procedures live next to the
> game they capture; `pdoom1-website` is a publish TARGET the pipeline pushes to,
> not the home of the process). Tradeoff: if content ops later outgrows the game
> repo (multi-game, hires with no code access), lift the whole `docs/content/`
> dir into its own repo -- the docs are written to survive that move.

## 1. What the Creative Director DECIDES (cannot be proceduralized)

These are the calls only Pip (or a future hire he trusts) makes. Everything not
on this list should live in a procedure.

- **Taste gates.** Approve/reject each script, each final cut, each thumbnail.
  One pass, binary, with notes. (Same shape as the art triage verdicts --
  reuse that muscle.)
- **Voice of the project.** Register and tone: how dark, how earnest, how much
  AI-safety discourse vs pure game content. Set once as a style note, revisit
  quarterly, enforce via the taste gate.
- **What gets made next.** Pick from FORMATS_MENU.md; order the backlog.
- **Idea-space strategy.** Which search terms / niches we are claiming
  ("P(Doom)", "AI safety game", "AI doom simulator"...) -- titles and topics
  follow from this, procedurally.
- **Identity exposure.** How much Pip face/voice appears. This is a personal
  call with a real cost either way (see Open Questions).

## 2. What is PROCEDURAL (delegated to procedures + agents, later to a hire)

- Script drafting (from devblog seeds, game systems, ADRs) -> template in
  PROC_VIDEO_PIPELINE.md step 2. Agent drafts, Pip taste-gates.
- Capture -> Godot Movie Maker mode, fully scripted (step 3).
- Assembly -> ffmpeg scripts checked into the repo (step 5). Re-runnable:
  patch the script, re-render the video. This is the "iteration and patching"
  property Pip asked for -- a video becomes a build artifact, not a craft object.
- Upload/publish -> checklist (step 7). Metadata (title/description/tags)
  drafted procedurally from the script.
- Re-cuts (Instagram/Shorts) -> deferred; will be another ffmpeg script over
  the same source clips.

## 3. Minimal irreducible skill list for Pip

Honest list. Everything else is "run a script" or "review and say yes/no".

1. **Reading a script aloud into a microphone, twice.** (Voiceover delivery.
   Only real new skill. Gets better free with reps; procedure includes a
   warm-up + two-take rule so it never becomes a perfectionism sink.)
2. **Binary taste gates with one-line notes.** Already practiced (art triage).
3. **Playing the game on camera** -- i.e. playing deliberately and slightly
   slower than normal while Movie Maker mode records. No editing skill needed.
4. NOT required: video editing, motion graphics, thumbnail design tools,
   audio engineering. These are procedural or agent-drafted.

## 4. Maturity ladder

- **L0 (today):** Pip + agents. Agent drafts script + shot list; Pip records
  capture + voice; agent assembles via ffmpeg; Pip gates; Pip uploads.
  Everything logged in the repo.
- **L1 (steady state, solo):** One video per release-train cycle (monthly)
  plus opportunistic shorts. The pipeline docs are the SSOT; any agent can
  run any step except voice and gates.
- **L2 (first hire):** Hand the hire PROC_VIDEO_PIPELINE.md. They take
  capture, assembly-script authoring, upload, and re-cuts. Pip keeps section 1
  (decisions) only. Test of the docs: the hire should produce a publishable
  short in their first week without asking Pip a process question.
- **L3 (later):** Hire proposes formats and scripts; Pip is purely the gate.

## 5. Standing constraints

- ASCII-only in committed docs (repo rule).
- Music: use the in-repo composed score (godot/assets/audio/music/). Note for
  the first hire: confirm and record the license/ownership line for these
  tracks in this doc before any monetized upload. [confirm rights provenance]
- Every format has a NO-VOICE fallback variant (text cards + music) so a
  video is never blocked on recording energy.
- Nothing over 1MB goes in git except final thumbnails if needed; rendered
  videos live outside the repo (masters dir / YouTube itself is the archive).
  Capture scripts and ffmpeg scripts DO go in git -- they are the video.
