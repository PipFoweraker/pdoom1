# ADR-0020 -- Machine actor identity: a bot acts under its own name, or the attribution record is fiction

- **Status:** PROPOSED -- built not released, per Pip's constraint. Design gates below are unanswered and BLOCK creation.
- **Date:** 2026-08-23
- **Summary:** Agent work is currently indistinguishable from Pip's in every repo's attribution record, because agents act through his credentials. This proposes a single machine actor with its own identity, its own audit trail, and permissions strictly narrower than Pip's -- and names the six questions that must be answered before one is created.
- **Session:** D4, approved 2026-08-23 via the coordination seat with the constraint *"actually create things without me, but then don't release them... if that raises interesting questions, give me design gates, ADR decisions and stuff."*

## Context

### The observation that earned this

Pip, reading a printed pack, 2026-08-23:

> *"every one of the 130 was filed by me not one by a bot account... if I can
> give a bot the same rights as me in my repos and it can differentiate from
> when things are fully run and then I can come in as a human and review it, we
> can see what my vs the bot interactions with the repos are, which I think is
> more honest."*

**The word doing the work is "honest".** This is not a permissions problem or a
throughput problem. It is an *evidence* problem.

### What the record currently claims, and why it is false

Every issue, PR, comment and commit produced by an agent in this estate is
attributed to `PipFoweraker`. The `Co-Authored-By` trailer on commits is the
only marker, and it:

- appears on **commits only** -- not on issues, comments, reviews, labels,
  merges, or closures;
- is **self-asserted** -- an agent that omitted it would be invisible, and
  nothing checks;
- is **not queryable** -- no view anywhere answers "what did the machines do
  last week".

So a reader of any repo's history sees one prolific human. On 2026-08-23 alone
that record absorbed roughly a dozen merges, four issue closures, two
cross-repo issues and several thousand lines of documentation, all stamped with
one person's name. **The attribution record is not a lie anyone told. It is a
lie the tooling tells by default**, and it is the same silent-failure shape
catalogued in `docs/design/SILENT_FAILURE_REGISTER.md`: the false state is the
*plausible* one, and nothing generates an event when it happens.

### Why this matters now rather than later

Three reasons converged this week:

1. **A hundred and fifty people are about to look.** Some will read the repo
   before running the binary -- #1038 exists because one already did.
2. **`docs/TRUST.md` now makes provable claims** about what the game touches.
   A trust artifact in a repo whose authorship record is fictional is a weaker
   artifact than it deserves to be.
3. **Certificates are being bought in a human's legal name.** Code signing
   asserts *a named person vouches for this binary*. That assertion should not
   quietly cover work no human read.

## Decision

**PROPOSED, not accepted. Nothing is created until the gates below are answered.**

### D1. One machine actor, not one per seat

A single identity, not `pdoom1-bot` / `website-bot` / `coordination-bot`.

Rationale: the question the record must answer is *"human or machine?"*, and
that is one bit. Which seat did it is already recoverable from the repo and the
branch name. Multiple bot identities multiply the credential surface, the audit
surfaces, and the number of things that can be silently misconfigured, to answer
a question nothing is asking.

### D2. A GitHub App, not a machine user

| | machine user (PAT) | GitHub App |
|---|---|---|
| shows as | a second human account | a distinctly-rendered bot |
| credential | long-lived token | short-lived, auto-expiring installation token |
| permissions | per-account, coarse | per-repo, per-scope, revocable |
| seat cost | may consume a paid seat | none |
| audit | mixed into user events | separate installation event log |

A machine user is a fake human, and the entire purpose here is to **stop the
record containing fake humans**. Adding a second one to fix the first is the
wrong shape.

### D3. Strictly narrower permissions than Pip's -- explicitly NOT "the same rights"

This departs from Pip's phrasing and the departure is deliberate.

**Grant:** open issues, open PRs, comment, push to non-default branches, add
labels.

**Withhold:** merge to `main`, close issues, force-push, administer branch
protection, publish releases, touch secrets, modify workflow files.

The reason is not distrust of an agent. It is that **the value of the record is
that the two identities can do different things.** If the bot can do everything
Pip can, "reviewed by a human" becomes unfalsifiable again -- a merge stamped
with his name would prove nothing, because the bot could have made it. The
separation is what converts a label into evidence.

There is a live example: three branch-protection bypasses happened on
2026-08-23, agent-driven, under Pip's admin rights. Under this ADR the agent
could not have performed them and would have had to ask.

### D4. A commit trailer is not attribution -- it is a courtesy

`Co-Authored-By` stays, because it is useful. It does not satisfy this ADR.
Attribution means **the actor field GitHub records**, which no trailer can
change.

### What is NOT decided here

- Whether the bot may act in repos beyond pdoom1. **Out of scope**; each repo
  admits it separately or not at all.
- Whether agents keep operating under Pip's credentials during any transition.
  They will, until the gates are answered.
- Anything about the bot's *name*. See the naming note below -- deliberately
  provisional.
- Whether this generalises to Beacon's or CVTas's repositories, which have
  different governance and, in beacon-internal's case, sensitive material.

## Design gates -- these BLOCK creation

Pip asked for gates rather than silent resolutions. Six, roughly in the order
they bite.

**GATE 1 -- Does the bot's output count as reviewed?**
If a bot opens a PR and Pip merges it, the record says a human reviewed it. Is
that true? Today a human merges agent PRs after reading a summary, sometimes
after reading the diff. **The honest record is only as good as the honesty of
that step**, and this ADR makes it *visible* without making it *true*. Naming
the risk: a bot identity could make review-theatre easier to perform, not
harder. That would be worse than the current state, which at least has no
ceremony to hide behind.

**GATE 2 -- Who is accountable for what the bot does?**
Legally and practically, Pip. The identity separation is evidentiary, not a
liability shield, and it must never be described as one. If a bot opens an issue
containing something defamatory or a PR containing someone's private data, the
answer to "who did this" is Pip, with an extra step.

**GATE 3 -- What happens to the existing 130?**
Backfill is impossible: GitHub authorship cannot be rewritten. So the record has
a **discontinuity** at the date the bot starts. Either that boundary is
documented, or every future analysis of "human vs machine over time" silently
reads the pre-boundary period as all-human. **An undocumented discontinuity is a
silent failure by this estate's own definition.**

**GATE 4 -- Does the bot get to close things?**
D3 says no, and it is the gate most likely to be argued. Closing is a judgement
that work is finished. #732 was closed with half its criteria undone *by a
human*; a machine closing issues would industrialise that failure. The counter-
argument -- that stale-issue hygiene is exactly the drudgery to delegate -- is
real. **Unresolved.**

**GATE 5 -- Is the bot one actor or a fleet?**
D1 says one. But if several agents run concurrently under one identity, their
work is mutually indistinguishable, and this ADR's whole premise is that
indistinguishable actors make a record fictional. **The premise may apply
recursively and D1 may be wrong.**

**GATE 6 -- What does the bot do when it is uncertain?**
A human who is unsure asks. A bot with issue-opening rights that is unsure will
open an issue -- and the cheapest possible action becomes the default response
to uncertainty. That is how a tracker acquires 200 open issues. **The failure
mode is not bad work; it is cheap work at volume.**

## Beacons served / violated

- **Rams #6 (honest):** the attribution record stops asserting that one person
  did work that a machine did. This is the beacon the whole ADR exists to serve.
- **Rams #10 (as little design as possible):** one identity, one bit of new
  information, no per-seat proliferation. The question "human or machine" is
  answered once.
- **Violated -- convenience:** every agent operation gains a credential
  boundary. Some things Pip does in one step become two. That cost is accepted
  because the separation is the product.

## Rejected alternatives

**Do nothing, rely on `Co-Authored-By`.** Rejected: covers commits only, is
self-asserted, is unqueryable, and is absent from every issue and comment. It
is a courtesy, and courtesies are not evidence.

**A machine user account.** Rejected under D2: it is a fake human, and the
problem is fake humans.

**Label agent work instead of separating identity.** Rejected: a label is
applied by the same actor doing the work, so it is self-assertion again --
sighting #9's shape, where `bump` and `none` were mechanically identical.

**Give the bot Pip's full rights, as originally phrased.** Rejected under D3,
with the reasoning stated there: identical capability makes "a human did this"
unfalsifiable, which destroys the evidence the exercise is meant to create.

## Consequences / open questions

- **A trust artifact gets stronger.** `TRUST.md` and a signed binary both say
  "a named party vouches for this". A queryable human/machine split makes that
  claim checkable rather than asserted.
- **Some agent work will be slower**, and a small amount will require Pip that
  does not require him today. That is the intended cost of Gate 1 being real.
- **This ADR could make things worse** if the identity split becomes a
  performance of review rather than review. Gate 1 is the one to keep watching,
  and it is not resolvable by tooling.
- **The naming is provisional on purpose.** Pip, 2026-08-23: *"we'll call it
  that until it's mature enough to decide if it wants to rename itself."* A name
  held in trust rather than assigned, which is the same stance as
  guardian-rather-than-owner. Candidates and reasoning are in the PR; the ADR
  deliberately does not fix one, because a name chosen inside a design document
  is harder to give back.
