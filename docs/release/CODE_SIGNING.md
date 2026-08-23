# Code signing and platform pre-compliance -- what to buy, what it costs, what only Pip can do

Written 2026-08-23 against a stated budget of **AUD $5,000** and a stated
outreach plan: *"tell 10 people today and 40 people tomorrow and email 100
people the day after that."*

Every figure below was verified against first-party or vendor sources on
2026-08-23, not recalled. Where a belief of mine turned out to be wrong, the
correction is kept in place rather than quietly edited out, because the wrong
version is the one most people still hold.

---

## 1. The finding that decides everything

Microsoft SmartScreen builds reputation on **two different objects**, and only
one of them survives a rebuild.

| object | how it grows | what a new build does to it |
|---|---|---|
| **file hash** | downloads + clean runs of that exact binary | **destroyed.** A new build is a new hash, starting from zero |
| **signing certificate** | downloads + clean runs across *every* file it signs | **inherited.** New builds start with the certificate's accumulated trust |

This project bumped **23 commits past its last tag in two days.** Unsigned, that
cadence is not merely unhelpful -- it is self-defeating. Every release resets
the only reputation it has, so the warning can never stop appearing no matter
how many people download it.

**Signing is the one purchase whose value compounds with build frequency
instead of being destroyed by it.** That is why it outranks everything else on
this page, and why the timing matters this week specifically.

### The expensive misconception, corrected

I believed, and would have advised, that an **EV certificate grants instant
SmartScreen trust**. That was true for years and it is **no longer true**.

> Since March 2024, Microsoft's Trusted Root Program update removed EV's
> distinct SmartScreen status. EV and OV certificates now build SmartScreen
> reputation equally, through download volume.

**Do not pay the EV premium expecting a bypass that no longer exists.** Buy on
validation speed, price, and whether the vendor will sell to an Australian
entity. EV is still worth considering for one reason only: some corporate IT
policies whitelist on EV specifically. That is a procurement argument, not a
SmartScreen argument.

---

## 2. The option that is closed to us, and why

**Azure Artifact Signing (formerly Azure Trusted Signing) -- USD $9.99/month.**

It is by a wide margin the cheapest and best-engineered option: no hardware
token, no shipping, HSM-backed, CI-friendly.

**It is not available to us.** As of April 2026 it is restricted to **US,
Canadian, EU or UK businesses**, and self-employed individuals must be located
in the **United States or Canada**.

Pip is Tasmanian and the entities are Australian. **This door is shut.** I am
recording it explicitly because it is the first thing any adviser will suggest,
and re-deriving that it does not apply wastes an hour each time.

*Re-check this before renewal.* Microsoft has stated an intention to widen
eligibility; a geography that excludes Australia today may not next year.

---

## 3. What to buy -- recommended order

### PRIORITY 1 -- Windows OV code signing certificate

**~USD $215-260/year.** OV, not EV, for the reason in section 1.

- Issuance: **1-3 business days** typical; some CAs same-day. Expedited
  validation is offered by several vendors for a fee.
- Since June 2023 the private key **must** live on FIPS 140-2 Level 2 hardware
  -- a physical USB token, or the CA's cloud HSM. **Prefer the cloud HSM
  option.** A physical token must be shipped to Tasmania and then physically
  present at every signing, which makes CI signing impossible and makes signing
  impossible while Pip is in Singapore 26 Aug - 1 Sep.
- Since **2026-02-23** the CA/Browser Forum caps code signing certificates at
  **459 days (~15 months).** Three-year plans still exist but require annual
  re-issuance. Budget for this as a recurring cost, not a one-off.

#### Buy the INDIVIDUAL variant, and do not wait for the entity decision

There are two validation levels and the cheaper one is also the faster one:

- **OV (Organisation Validation)** puts an entity name on the binary. It
  requires a verifiable legal entity, a phone number findable in public records,
  and a callback. **This is where new entities stall** -- an org too young to
  appear in a public directory cannot complete validation, and there is no way
  to hurry it.
- **IV (Individual Validation)** puts a verified *person's* name on the binary
  with **no business entity required**. Government photo ID, proof of address,
  and a callback. It is the lowest-cost path to Authenticode signing for a solo
  developer.

**Recommendation: buy IV as `Pip Foweraker`, now.** Four reasons:

1. **It is honest.** A solo developer's name on an indie AI-safety game is
   accurate, and to a donor doing five minutes of due diligence it reads better
   than a company they have never heard of.
2. **It unblocks immediately.** No ABN, no directory listing, no tax history,
   and no need to resolve which of three orgs owns this.
3. **The forfeited reputation is near zero TODAY.** Reputation starts from
   nothing either way. Switching publisher identity in a year costs a year of
   accrual; switching now costs nothing. The cost of this decision grows every
   week it is deferred, which is an argument for acting, not for waiting.
4. **A certificate purchase should not force an entity decision.** That
   decision has its own reasons and its own timeline.

**The one thing that is genuinely permanent:** the name on the certificate is
what every Windows user sees, and **SmartScreen reputation does not transfer
between publisher identities.** Signing as `Pip Foweraker` and later re-signing
as `Beacon GCR` restarts reputation from zero. That is a real cost, taken
knowingly, in exchange for starting today.

#### Cloud signing, not a hardware token -- this is not a preference

**SSL.com eSigner** (FIPS 140-2 Level 3 cloud HSM) or an equivalent cloud
service. A physical USB token:

- has to be shipped to Tasmania, adding days before anything can be signed;
- must be physically present at every signing, so **CI cannot sign at all** --
  hardware tokens cannot participate in cloud-hosted runners;
- makes signing impossible while Pip is in Singapore 26 Aug - 1 Sep.

A cloud HSM signs from GitHub Actions natively. Given a release cadence of
twenty-plus commits in two days, a signing step a human must be present for is
a signing step that will be skipped.

#### What to have ready before starting

- Government photo ID (passport or licence)
- Proof of address matching that ID
- A phone number that will be answered for the callback
- **The exact publisher name, spelled the way it should appear forever**

### PRIORITY 2 -- Windows SDK (free, do it today)

`signtool.exe` is **not installed on this machine** -- verified, `--status`
reports `signtool: NOT FOUND`. Nothing can be signed until it is. Free, and it
can be done before the certificate arrives.

### PRIORITY 3 -- Apple Developer Program

**USD $99/year.** Required for a Developer ID certificate, which is required
for notarization, which is what stops macOS refusing the app outright.
Notarization itself is free once enrolled.

- Enrolling as an **organisation** requires a free **D-U-N-S number** from Dun
  & Bradstreet, plus authority to sign for the entity. Australian applicants
  are sometimes asked for **notarised copies of registration documents**.
  D-U-N-S issuance is not instant -- start it before it is needed.
- Enrolling as an **individual** skips D-U-N-S entirely and is much faster.

**Recommendation: enrol as an individual now, migrate to the organisation
later.** The macOS build has never been verified to run at all (#1071), so
there is nothing to notarise this week; the value of enrolling now is that the
D-U-N-S clock and the organisation decision stop blocking anything later. This
is a small deliberate acceptance of a later migration, not an oversight.

### PRIORITY 4 -- Steam Direct

**USD $100 per title**, recouped once the title earns USD $1,000.

**Not urgent, and worth paying anyway.** Pip's own framing: *"not that I want
to launch on them"*. The value today is a **claimed Steam page**, which is a
credibility artifact a donor can look at in the five minutes they will spend.
It also parks the name.

Note the standing blocker: **the Steam framework breaks on non-mac checkouts
(#1071)** and GodotSteam binaries were silently missing from CI packages
(#917). Paying the fee does not fix either.

### Total

| item | cost (USD) | recurring |
|---|---|---|
| OV code signing certificate | 215-260 | annual |
| Windows SDK | 0 | -- |
| Apple Developer Program | 99 | annual |
| Steam Direct | 100 | per title, recoupable |
| **total** | **~415-460** | |

**Roughly 12% of the stated $5,000 budget.** Money is not the constraint here;
**validation lead time and entity choice are.**

---

## 4. What is already built and waiting

`tools/sign_release.py` exists and is tested against its three states. When the
certificate arrives, signing becomes **configuration, not code**:

```
setx PDOOM1_SIGN_SHA1 <thumbprint>
python tools/sign_release.py --require builds/windows_desktop/PDoom.exe
```

It refuses to lie in three specific ways, each killing a failure this project
has already met in another form:

1. **Unsigned is reported, never assumed fine.** No credentials exits 0 with an
   explicit `NOT SIGNED` verdict -- an unsigned dev build is legitimate.
   `--require` inverts it for releases, so a release cannot quietly ship
   unsigned the way v0.13.1's gdextension binaries quietly shipped missing.
2. **The signature is verified by a second invocation.** `signtool` can exit 0
   having produced a signature that does not verify, so the check re-reads the
   file rather than trusting the sign command's own exit code.
3. **Timestamping is mandatory.** Without an RFC-3161 timestamp, every
   signature stops validating when the certificate expires -- at most 459 days
   -- and every build already in donors' hands silently reverts to "unknown
   publisher" on a date nobody wrote down.

---

## 5. The free wins, which do not need a certificate

- **The application icon was empty.** `#732` was closed on 2026-07-20 with zero
  comments; it set the publisher metadata and never set the icon, so every
  build since has shipped the default Godot icon in the taskbar, in alt-tab,
  and **in the SmartScreen dialog itself**. Fixed: a 7-resolution `.ico` is now
  generated and both presets point at it. This is the cheapest credibility
  gain available and it cost nothing.
- **`FIRST-RUN.txt` ships in no archive** (#1017), so every install instruction
  lives on a page the downloader has already navigated away from.
- **A provable statement of what the game touches** (#1038) is the actual
  answer to five minutes of donor due diligence, and it is *true today* --
  it is simply undocumented.

---

## 6. Honest ceiling

**None of this proves the game is safe.** Issue #1038 states it correctly and
it is worth repeating where a donor can see it: you cannot prove the absence of
vulnerabilities, and claiming otherwise to a technical audience destroys the
credibility the exercise is meant to build.

What signing buys is narrower and still worth having: **it proves the binary
came from a named, validated publisher and has not been altered since.** That
is a chain of custody, not a safety certificate. Say that, and say it first.
