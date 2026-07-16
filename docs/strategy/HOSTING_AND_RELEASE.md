# pdoom1 -- hosting + release strategy (spelling out the land)

> Written 2026-07-17 at Pip's request. Two linked questions: (1) how do we host the backend, and
> (2) when/how do we launch + apply for funding. Both are really "how does pdoom1 reach people with
> low friction." Prices are current (2026, see Sources). NOT financial/grants advice -- verify
> funder fit with someone who does grants.

## TL;DR
- **Today:** scores on a **PHP subdomain** on your existing shared hosting. ~15 min, ~$0 marginal,
  and it gets "download -> play -> score on the world board" working *today*. It is NOT throwaway --
  it's just the score store; a real backend later reads/migrates the same JSON.
- **This week or next:** stand up **one real backend box** (~$5-12/mo) as the home for all pdoom
  services (scores + pdoom-data APIs + a future web-client backend). This is the pivot insurance.
- **Release:** you are almost certainly **under-shipping**. Ship a public itch/web alpha soon and
  apply for a grant *with the alpha as proof* -- don't wait for polish.

---

## Part 1 -- Hosting

### The immediate need (scores today) -> subdomain PHP
Your shared hosting already serves PHP. Add `api.pdoom1.com` (or reuse a subdomain), upload
`score_api.php`, done. Cost: $0 marginal (you already pay for shared hosting). Effort: ~15 min.
This satisfies today's goal completely. Keep it even after a real backend exists, or migrate the
JSON up -- either way it's not wasted.

### The real question -> a dedicated backend box
You want to host pdoom-data datasets, serve the website game-data, and (you suspect) maybe a
web-only game client later. That wants a real always-on server. Options, cheapest-effort-first:

| option | cost/mo | effort | you manage | best for |
|---|---|---|---|---|
| **Shared PHP subdomain** | ~$0 (existing) | ~15 min | nothing | scores only; no long-running procs, no APIs at scale |
| **DreamHost VPS** (Passenger) | $10 intro -> ~$25 renew | low (same as CVTas) | little (managed-ish) | staying in the DreamHost family you know; Django like CVTas |
| **DreamCompute 2GB** (OpenStack VM) | ~$12 (pay-as-you-go, free bandwidth) | medium (you sysadmin) | OS + web server | a real VM inside DreamHost; free egress is nice |
| **Hetzner CX22 + Coolify** | ~EUR 4.59 (~$5) | medium initial, easy after | OS (Coolify eases it) | cheapest real box; stack many pdoom apps on one; best $/value |
| **Fly.io / Railway** | ~$5-25 (usage) | lowest DX | almost nothing | fastest deploys; Fly's edge = low latency for a web GAME client |

Notes:
- **DreamHost VPS renewal jumps ~134-220%** -- watch the intro-to-renewal cliff.
- **DreamCompute** is pay-as-you-go, capped at 600h/mo billing, free bandwidth -- clean model.
- **Hetzner + Coolify** is the value king if you're willing to `apt update` occasionally; Coolify
  gives you a Railway-like deploy UI on a $5 box and you can host scores + pdoom-data + more on it.
- **Fly.io** matters *specifically* if the web-client happens -- its edge network cuts latency for
  players worldwide; for a turn-based game that's a nice-to-have, not essential.

### The web-client pivot -- cheaper than it feels
Key fact: **Godot exports to HTML5/Web.** So a "web-only client" does NOT mean a rewrite or an
expensive server:
- The **client** (the game) is a static export -> host it **free** on itch.io, Cloudflare Pages,
  or GitHub Pages. Near-zero friction, near-zero cost.
- Only the **backend** (scores, pdoom-data, any future multiplayer) needs a paid server -- the same
  ~$5-12/mo box above.
So investing in one backend box now makes the pivot a matter of *exporting to web + pointing the
client at the existing API*, not a project. That's the cheap optionality you're sensing.

### Recommendation
1. **Today:** `score_api.php` on a shared subdomain. Unblocks the goal now.
2. **Soon (a half-day, not urgent):** stand up **Hetzner CX22 + Coolify** (~$5/mo, best value, hosts
   everything) OR **DreamCompute 2GB** (~$12/mo, stay in DreamHost). Migrate scores there, host the
   pdoom-data read APIs there. This is your "real backend."
3. **When web-client pressure comes:** export Godot to web, static-host it free, point at the backend.
   You'll be able to pivot in days, not weeks.
Recurring cost of being fully pivot-ready: **~$5-12/mo.** That's the whole bill.

---

## Part 2 -- Release thresholds + grants (the reticence)

### Blunt read: you are under-shipping, not over-shipping
You have a deterministic, replay-safe engine; deep, ADR-documented mechanics; a hiring pipeline; an
art pipeline; a test suite + honest CI; a leaderboard. **That is more than most indie games that
are already "released" in alpha.** Your instinct that you "should have shipped ages ago" is
probably correct. High-standards solo devs (especially detail-driven ones) systematically launch
too late -- the failure mode is invisibility, not embarrassment.

### The "shame-free MVP" bar (for a public alpha)
You clear it when: (a) a new player can play a full game start -> loss/win without a crash, (b) the
core loop is legible (you can tell what you're doing and why doom moves), (c) there's one hook to
return for (the leaderboard/score chase -- which is exactly what we're wiring today). You are at or
within days of this bar.

### The release ladder
1. **Private alpha (now):** today's downloadable build + world leaderboard, shared with your
   playtester + a handful of AI-safety folks. **You are here today.**
2. **Public alpha (next -- weeks, not months):** itch.io page, free, labelled "alpha." An itch/web
   build captures traffic with near-zero friction. THIS is where the "inferior-but-shipped web game
   got a massive audience" lesson pays off -- accessible + present beats polished + gated.
3. **Beta -> Steam "coming soon" page (wishlists start compounding early) -> 1.0.**

### On the traffic-capture instinct
Pre-chasing metrics *does* feel weird, and you're right to be wary of vanity metrics. But your
prospective collaborator's data point is real evidence: **a low-friction, present, "inferior" web
game out-reached better gated ones.** Capturable traffic is optionality, and optionality is cheap
to hold. The web export makes holding it nearly free. Take the lesson; don't let it distort the
game design.

### Grants -- you can apply NOW
A playable alpha + a crisp theory-of-impact (AI-safety literacy / making the strategic landscape of
AI risk legible + felt) is a *strong* application. You do not need polish; you need a working thing
and a clear "why this matters." Waiting has a real cost (no runway, no external validation, slower
iteration). Plausible funders to look at (VERIFY fit + current status with someone who does grants
-- this is not my expertise):
- **Manifund** (regranting; AI-safety-adjacent projects; fast, informal).
- **Survival & Flourishing Fund / SFF** (larger, AI-x-risk).
- **Long-Term Future Fund (EA Funds)** (AI safety, incl. comms/education).
- **AI-safety communications / field-building grants** (various; the "make AI risk legible" angle
  fits comms funders).
- Possibly **Astral Codex Ten grants** or similar small-grant rounds.
The move: draft a one-page "what it is / why it matters / what a grant buys (runway to X)" and send
it to 2-3 of these. Low cost, high EV. Get a grant-savvy person to sanity-check the framing.

### Bottom line
The risk here is **under-shipping**, full stop. You're closer to a legitimate public alpha than you
feel. Concretely, in order: (1) ship today's build to your private testers, (2) get scores syncing
this afternoon, (3) put an itch alpha up within a couple of weeks, (4) draft a one-page grant pitch
and send it while the alpha is live. Perfection is the enemy here; presence is the asset.

## Sources
- DreamCompute billing + instance sizes (512MB $4.50 / 2GB $12 / 8GB $48, pay-as-you-go, free bandwidth).
- DreamHost VPS pricing (intro $10-15 -> ~$25 renew).
- Hetzner (~EUR 4.59 for 2 vCPU/4GB) + Coolify; Fly.io / Railway / Render solo-dev pricing (2026 comparisons).
