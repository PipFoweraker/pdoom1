# SEED: First-funding modes -- rearranged from what already exists

> Status: SEED (options for Pip to rule on, Wed 2026-07-29 W-3b). NOT ratified.
> Written 2026-07-27 as the design half of the EARLYGAME lane, against Pip's
> ruling: "first-funding modes I think we can rearrange from the existing
> fundraising mechanics, plus giving them one additional sub-layer of extension as
> we have done to employment (was generic, is now not, and employees have 1 level
> of complexity to them with several lateral mechanics)."
> Feeds #811 agenda item 1 ("first-funding modes -- each mode gets 3 of 4 finance
> options"). `[PIP]` = verbatim; `[INFERRED]` = Claude's read.

---

## 0. Resolving the "4 finance options" ambiguity

R3A_CRIB flagged this as a possible missing-doc gap: *"confirm the pool of 4
finance options is defined elsewhere (not found in the docs searched)."*

**It is defined -- in data, not docs.** `godot/data/actions/fundraising.json`
holds exactly four actions, and has since the L9 externalization (#621):

| id | name | what it actually does today |
|---|---|---|
| `fundraise_small` | Modest Funding Round | 1 AP + 2 rep -> $30k-60k. Always available. |
| `fundraise_big` | Major Funding Round | 2 AP + 8 rep -> $80k-150k. Wants standing. |
| `take_loan` | Business Loan | 1 AP -> $75k now, $90k debt. |
| `apply_grant` | Research Grant | 1 AP + 1 paper -> $50k-100k. Needs a publication. |

So "#811: each mode gets 3 of 4 finance options" reads exactly as written: THIS
quartet is the pool, and a first-funding mode REMOVES one door. That is the
"rearranged from the existing fundraising mechanics" Pip asked for -- no new
economy, no new instrument, a subtraction that makes each mode a shape.

(Distinct from `data/actions/financing.json` + `FinanceEngine`, which is the
ADR-0013 cost-of-debt LEDGER layer. The modes below gate the fundraising quartet;
the financing engine stays orthogonal and keeps its own org-type gates.)

---

## 1. The pattern being copied: generic -> specific + lateral complexity [PIP]

Pip's own analogy, applied literally:

| Employment (shipped) | Funding (proposed) |
|---|---|
| "Hire Staff" was one generic button | "Fundraising" is one generic submenu today |
| Now: distinct channels (Advertise / Connections) with different clocks and currencies | Now: a MODE chosen at org creation decides which three doors exist |
| Each employee carries ONE level of complexity (appetites, quirk, loyalty, onboarding) -- several LATERAL mechanics, not a deeper number | Each mode carries ONE named sub-layer -- a lateral mechanic, not a bigger number |

The load-bearing word is **lateral**. An employee is not a bigger number than the
old generic staff count; they are a different KIND of object with hooks. A funding
mode must be the same: not "more money" but "money with a different handle on it."

---

## 2. The three modes (Claude's proposal)

Three, not four. MaRo/Rams check: a fourth mode ("angel/patron") duplicates
grant-funded's shape without adding a distinct sub-layer, and three crisp options
beat four mushy ones. The fourth is listed in section 4 as a Pip call.

### Mode 1 -- BOOTSTRAPPED
*You are paying for this yourself, and it shows.*

| | |
|---|---|
| Doors OPEN | Modest Round, Business Loan, Research Grant |
| Door CLOSED | **Major Round** -- nobody is writing you a big cheque yet |
| Sub-layer | **Personal guarantee.** The loan carries a rider that bills YOU, not the org: a ledger entry in `governance` (or reputation) rather than money. Default on the org's loan and it is your name on it. |
| Why the sub-layer is lateral | It does not change the loan's size or rate. It changes WHO the counterparty can come after -- an existing `Ledger.Entry` with a different currency and counterparty, which the ledger already supports. |
| Early bite | Immediate: the biggest single cash lever is missing, so the tier-1 office choice is genuinely constrained (the co-working corner suddenly looks sensible). |

### Mode 2 -- GRANT-FUNDED
*Cheap in money, expensive in paperwork.*

| | |
|---|---|
| Doors OPEN | Modest Round, Major Round, Research Grant |
| Door CLOSED | **Business Loan** -- restricted funds cannot service debt |
| Sub-layer | **Reporting burden.** Each live grant creates a recurring TYPED ADMIN DEMAND at the month boundary -- absorbable by ops staff, exactly the pattern OFFICE_ECONOMY_PROPOSAL 2e proposes for rent-admin (ADR-0011 point 6). The grant money is good; the Attention it eats is the price. |
| Why the sub-layer is lateral | The demand is not a debuff and not a fee. It is a claim on the founder's Attention that STAFF CAN BUY BACK -- which is the game's core staff-buys-founder-time loop, reached from a new direction. |
| Early bite | Immediate and structural: no debt at all means no bridging. You cannot borrow your way out of a bad month; you plan or you starve. |

### Mode 3 -- VENTURE-BACKED
*Fast money, and someone is watching.*

| | |
|---|---|
| Doors OPEN | Modest Round, Major Round, Business Loan |
| Door CLOSED | **Research Grant** -- no publication record, and funders discount you |
| Sub-layer | **The board.** The `board_seat` rider (already minted by `FinanceEngine.accept_offer`, currently an inert standing ledger entry) becomes LIVE: periodically the board makes a demand -- a window event (ADR-0012) that constrains next month's action space until answered. |
| Why the sub-layer is lateral | It spends no resource. It removes options for a bounded time. That is a different KIND of cost from every other funding cost in the game, which is precisely the point. |
| Early bite | Immediate: fastest cash in the game, and the first board demand lands before you have staff to absorb it. |

### The subtraction table at a glance

| | Modest | Major | Loan | Grant |
|---|---|---|---|---|
| Bootstrapped | yes | -- | yes | yes |
| Grant-funded | yes | yes | -- | yes |
| Venture-backed | yes | yes | yes | -- |

Modest Round is the floor every mode shares (the "you can always scrape something
together" guarantee that keeps the opening nearly-unlosable). Each mode is
identified by the ONE door it lacks -- which is far more memorable than three
overlapping lists.

---

## 3. How a mode is chosen, and how it interacts with np/fp

- **When**: at org creation, alongside org_type (DQ-4 / DQ-19 char-org creation).
  Same screen, second question. It is a commitment, not a menu you revisit --
  same switching-costs philosophy as the office lease (#791).
- **Storage**: `GameState.funding_mode: String`, serialized like `org_type`.
  Read by whatever builds `get_fundraising_options()` -- i.e. the gate is ONE
  filter over the existing data-driven list, not a rewrite.
- **Interaction with org_type** (see SEED_NPFP_DIVERGENCE.md): the two forks are
  ORTHOGONAL but not all nine combinations are sane. [INFERRED]

| | nonprofit | for_profit |
|---|---|---|
| Bootstrapped | natural | natural |
| Grant-funded | natural (the archetype) | odd -- allow but price the grants worse |
| Venture-backed | incoherent -- **disallow** (a nonprofit cannot sell equity) | natural (the archetype) |

Ruling needed: disallow the incoherent cell outright at creation, or allow it and
let it be a hard mode? Claude's read: **disallow**, and say why on the creation
screen -- an illegal combination the player discovers 20 turns later is a trap,
and the creation screen is the cheapest place in the game to teach a rule.

---

## 4. Open questions for Pip

1. **Three modes or four?** A fourth candidate is PATRON/ANGEL (one wealthy
   believer: doors = Modest, Major, Grant; sub-layer = the patron is a single
   named counterparty whose opinion of you is a relationship, and who can withdraw
   entirely). It is the most flavourful and the most work -- it needs a persistent
   NPC relationship the game does not model yet.
2. **Is the closed door CLOSED, or unlockable?** Permanently absent is crisp.
   Unlockable-later ("publish 3 papers to open Research Grant") is the
   switching-costs philosophy applied to funding, and is more work. Claude leans
   crisp for v1, unlockable as the next epoch's extension.
3. **Which sub-layer ships first if only one does?** Claude's pick: the
   grant-funded REPORTING BURDEN, because it reuses the typed-admin-demand pattern
   the office lane already needs for rent, so the two lanes share one mechanic
   instead of inventing two.
4. **Does the mode feed FinanceEngine pricing?** It currently would not.
   Bootstrapped arguably should price debt worse (no institutional backing) --
   one more `org_factors`-shaped coefficient table if so.
5. **Bot/sweep policies**: the sweep needs a policy axis per mode
   ({bootstrap-lean, grant-lean, vc-lean}) before any of this can be balanced.
   Confirm that is in scope for whoever runs the next sweep.
