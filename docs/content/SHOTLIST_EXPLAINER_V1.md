# Shot list: "What is P(Doom)?" explainer V1

> Status: DRAFT, 2026-07-26. Companion to SCRIPT_EXPLAINER_V1.md.
> Capture = Godot Movie Maker mode, PROVEN on this machine today (see
> "Proven command + gotchas" below). Masters:
> `G:/tmp/pdoom1-video-masters/2026-07-explainer/shots/`.

## Proven command + gotchas (verified 2026-07-26, GTX 1070, Godot 4.5.1)

Working command (ran end-to-end, output verified):

    "C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe" --path "G:/Documents/Organising_Life/Code/pdoom1/godot" --write-movie "G:/tmp/pdoom1-video-masters/2026-07-explainer/shots/<shot>.avi" --fixed-fps 60 --resolution 1920x1080

Verified facts and gotchas:
- Output: MJPEG AVI, ~18 MB/s (~1.1 GB/min). The AVI 4GB cap means MAX ~3.5
  MINUTES PER SHOT -- fine for this list; never leave it running.
- **`--quit-after N` frames gives a CLEAN finalized file** (proof: 300 frames
  -> header reads exactly 300 frames / 60fps / 5.0s). Use it for static or
  scripted shots (N = seconds x 60). For interactive shots, quit via the
  window X button. NEVER Ctrl+C (corrupts duration metadata).
- Do NOT use --headless -- Movie Maker needs the rendering window; a game
  window appears and plays in slightly-slower-than-real-time. Input works;
  play deliberately.
- AUDIO: game audio IS recorded into the AVI at your current volume settings
  (session log showed Master 60% / Music 18%). For VO-led shots this is fine
  (assembly ducks or drops it); for the S6 office shot consider Settings ->
  music low so SFX/ambience survives as a bed.
- Expect first-run stderr class-cache noise if the checkout was freshly
  imported; harmless.

## Shots (capture 2-3x the VO line length; cut points need fat)

| Shot | Feeds line | Source / where | What to do | Capture len |
|------|-----------|----------------|------------|-------------|
| S1 | 1 HOOK | Real game: doom instrument close-up (main HUD) | Sit on the doom meter/streams readout mid-run; small mouse drift only, let the number breathe. Static-ish: `--quit-after 1800` (30s). | 30s |
| S2 | 2 PROMISE | Real game: title/menu -> new run | From welcome screen, start a run, land on the first month. Window-X quit. | 30s |
| S3 | 3 turn loop | Real game: early turns | Queue 2-3 actions (hire, fundraise, research), end month, watch resolution feed. The rhythm is the shot. | 45s |
| S4 | 4 doom system | Real game: doom instrument / streams breakdown | Open the streams/instrument view, hover items so rows highlight; one month tick so numbers move. | 30s |
| S5 | 5 ledger | Real game: ledger screen | Open ledger with 3+ entries incl. a promise; hover one so the counterparty/fuse reads; close. | 30s |
| S6 | 6 office+cat | OFFICE SANDBOX (legit stage): compare view | Populate the large floor (workers walking, cat wandering); 10s calm wide, then follow the cat. Music LOW first. | 45s |
| S7 | 7 rivals/endgame | Real game: an event popup + a game-over screen | Bank two mini-shots: (a) a juicy event dialog appearing; (b) a run's ending screen + leaderboard. Any lost run from S2-S5 play works. | 30s+20s |
| S8 | 8 BUTTON | Title card (no capture) | Built in assembly: logo/wordmark still + download URL + ">> tell me what broke". Uses hero logo art (core_resource_icons logo or wordmark when picked). | n/a |

Total tape ~4.5 min for ~80s of video -- correct ratio; resist capturing more.

## Session plan (one sitting, ~60-90 min)

1. Prep: sandbox worktree launched once to warm caches; masters dir created;
   music volume set for S6.
2. Capture order: S2 -> S3 -> S4 -> S5 -> S7 (one continuous run gives all
   five; keep playing until you lose, that loss IS S7b). Then S1 (static),
   then S6 (sandbox).
3. One retake max per shot. Gaps are assembly's problem, not capture's.
4. Rename files to shot ids immediately; a wrong-named master costs more
   later than 10 seconds now.
