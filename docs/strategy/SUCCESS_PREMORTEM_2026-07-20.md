# Success premortem -- 2026-07-20

> Frame: it is mid-2027 and the game went WELL. This doc works backward from that:
> which kinds of success would find us unprepared, what breaks first in each, and
> the cheapest thing we can lay down now so the success pays off instead of
> overwhelming. Companion piece to HOSTING_AND_RELEASE.md (2026-07-17), which
> covers the release ladder, backend hosting, and grants -- not restated here.
>
> Produced by a four-agent review pass on 2026-07-20. Companion reports:
> - docs/game-design/FRESH_EYES_UX_TEARDOWN_2026-07-20.md (naive-player walkthrough)
> - docs/game-design/VOICE_AND_LEGIBILITY_SCAN_2026-07-20.md (outside-critic scan)
> - docs/game-design/RIVALS_SURFACING_OPTIONS_2026-07-20.md (rivals status + options)
> - docs/strategy/PLAYER_DOCS_PIPELINE_2026-07-20.md (docs SSOT + website sync plan)

## 1. The core observation

The game itself scales technically: single-player, deterministic, static website,
tiny JSON score payloads on shared PHP hosting. Volume is not the risk. What does
NOT scale in every success scenario examined below:

1. **Trust** -- the leaderboard auth is one shared token inside the client build.
2. **Triage** -- bug intake and inbound messages have no funnel.
3. **Founder attention** -- every scenario's binding constraint is Pip-hours and
   Pip-response-latency, not servers.

Most of the preparations below are therefore attention-armor: decisions made cold
now so they do not have to be made hot later.

## 2. Success scenarios and what breaks

### S1. Organic spread (a friend shares it onward; a Discord / LW / HN post lands)
- Breaks first: SmartScreen "unknown publisher" wall (unsigned exe, default Godot
  icon, empty publisher metadata -- export_presets.cfg). Strangers do not push
  through the way friends do.
- Breaks second: stranded versions. Direct-download zips have no update check;
  a spreading population files bugs already fixed.
- Breaks third: the leaderboard token. One extracted token = a spammable world
  board with no rate limit, name filter, or wipe policy.
- Now-actions: export metadata + icon (15 min); a version-check ping against a
  static latest.json on pdoom1.com (S); leaderboard hardening minimums (S-M):
  rate limit per IP, name filter, per-version boards (already in the contract),
  a written "the board can be wiped/rolled" policy line on the site.

### S2. AI-safety community adoption (orgs want it for outreach; talk invites)
- Breaks: no canonical self-description. Others will paraphrase the game's thesis
  badly; correcting after the fact costs more than authoring first.
- Now-actions: an about/press page on pdoom1.com in Pip's own words -- one
  paragraph of what it is, 3-5 chosen screenshots, contact route (S). The voice
  scan's store-page list is the raw material.

### S3. Streamer / video pickup (one mid-size creator plays it on camera)
- Breaks: the first 10 minutes ARE the video. Every teardown item in the UX
  report (commit-button rejection, undefined vocabulary, debug Init button)
  happens on stream, unedited.
- Breaks second: no shareable moment. No copy-seed, no result card; the natural
  "chat, beat my run" loop has no affordance.
- Now-actions: the UX report's top-2 (commit always advances + first-run modal);
  a "copy result + seed" one-liner on the game-over screen (S).

### S4. A grant lands (Manifund / LTFF / SFF per HOSTING_AND_RELEASE.md)
- Breaks: money arriving before the receiving-entity decision is made; reporting
  obligations with no roadmap doc to point at.
- Now-actions: decide WHICH entity receives game money before applying (T,
  decision only); keep a current public roadmap page (the docs-pipeline issues
  give it a home).

### S5. Press / academic interest
- Same fracture as S2 (narrative control) plus: response latency reads as
  disinterest. Pre-written answers to the five obvious questions (why this game,
  is it hopeless, is AI writing your AI-doom game, what should players take away,
  what next) cost an hour now and remove live-response pressure later.

### S6. Collaborator influx (artists, musicians, translators, devs offer help)
- Breaks: unanswered PRs and offers damage relationships silently. The repo has
  agent-facing docs but no outsider-facing "how to help".
- Now-actions: a short CONTRIBUTING note stating honestly what helps now
  (playtests, feedback) and what is not being accepted yet (code PRs, art) and
  where to talk (see S7's channel decision) (S).

### S7. Any of the above: where do people gather?
- Breaks: if no channel is named, four half-dead channels self-select (itch
  comments + GitHub issues + a Discord someone else makes + email).
- Now-action: pick ONE channel now (T, decision only) and put its link in-game
  and on the site before spread happens, so the community forms where you are.

### S8. Praise influx (the personal one)
- The historical pattern named by Pip: bewilderment at praise, freeze, missed
  windows. Structural mitigations, all cold-decided:
  - An opportunity-acceptance policy written in advance (talks: yes/no/cap per
    month; collabs: route to email; press: point at the press page). Deciding
    the policy now means the hot moment only requires pattern-matching, not
    deciding.
  - Response templates for the three common inbounds (praise, bug, "can I
    help"). A sentence each. Honest, warm, finite.
  - Praise lands in an evidence file, not just in the feed -- doubles as grant
    application material.
  - The bug-reporter and channel funnels above are also THIS mitigation: they
    convert diffuse social pressure into bounded queues.

## 3. What scales / what does not (audit)

| Surface | Volume behavior | Trust/attention behavior |
|---|---|---|
| Game client | N/A (local) | Stale-version bug reports without update ping |
| Website (static, netlify) | Fine to very large N | Fine |
| Score API (shared PHP, JSON) | Fine for turn-based N in the thousands | BREAKS: shared client token, no rate limit, no moderation |
| Bug reporter | Currently local-save only | BREAKS both ways: silence at scale (current) or issue-spam (if naively auto-filed). Needs endpoint + digest. Release notes currently overpromise ("files a GitHub issue") -- fix the copy either way |
| GitHub issues | Fine | Attention sink if it becomes the de facto community channel -- see S7 |
| Founder attention | -- | The binding constraint everywhere. All of section 2 is armor for it |

## 4. Ranked now-action list (cheapest leverage first)

1. Export metadata + icon (T). UX teardown item 1.
2. Commit button always advances an empty month + 4-sentence first-run modal (S).
   The single biggest retention fix; prerequisite to ANY sharing scenario.
3. Wire DeathAttribution.chain_summary() into the game-over screen (S). The
   "interested in how they lost" experience is built and unrendered.
4. One community channel decided + linked (T decision).
5. Copy result + seed share button (S).
6. Version-check ping against static latest.json (S).
7. Leaderboard hardening minimums + honest board policy line (S-M).
8. Bug-reporter honest copy now (T); endpoint + digest funnel later (M).
9. About/press page + pre-written answers (S).
10. CONTRIBUTING note for outsiders (S).
11. Docs pipeline phases 0-4 (filed as GitHub issues; see PLAYER_DOCS_PIPELINE doc).
12. Rivals surfacing tier-S bundle (see RIVALS_SURFACING_OPTIONS doc) -- converts
    already-built simulation into perceived depth.
13. Voice pass: re-skin the generic HR/tycoon event text in the shipped data to
    match the achievements register (M, content work; see voice scan).
14. Receiving-entity decision for grant money (T decision, before applying).
15. Opportunity-acceptance policy + response templates + praise evidence file
    (T-S, personal ops).

## 5. What was deliberately NOT planned here

- Steam/wishlist mechanics, multiplayer, web build execution: covered or
  sequenced in HOSTING_AND_RELEASE.md.
- Full tutorial design: scoped in the docs-pipeline issues instead.
- DQ-22 rival midgame escalation: needs an ADR workshop, not a premortem line.
