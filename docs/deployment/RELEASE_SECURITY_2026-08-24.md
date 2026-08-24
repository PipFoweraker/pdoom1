# Release security: what protects a public build with Pip's name on it

> **This is a PROPOSAL. Nothing in it has been applied.** No repository
> setting, ruleset, environment, secret or permission was created, changed or
> deleted while writing it. Section 7 lists the exact commands and UI steps;
> they have NOT been run. Settings changes are Pip's.

**Measured:** 2026-08-24, against `PipFoweraker/pdoom1` at `28f8cd94`.
Every claim in section 1 is followed by the command that produces it and the
raw answer. Re-run them; they are cheap and they are the whole point.

---

## 0. The headline finding is that the headline finding was already stale

This document was commissioned from a measurement taken earlier on 2026-08-24
which read: *"one ruleset, `Default no-ruin rules`, target branch, enforcement
DISABLED; no tag protection; therefore anyone with push access can create a
`v*.*.*` tag and publish a public release."*

Re-running the commands found a **second ruleset that did not exist when that
measurement was taken**:

```
$ gh api repos/PipFoweraker/pdoom1/rulesets --jq '.[] | "\(.name) | enforcement=\(.enforcement) | target=\(.target) | created=\(.created_at)"'
Default no-ruin rules | enforcement=disabled | target=branch | created=2025-08-20T19:54:01.556+10:00
Release tags: v* created by admins only, never moved, never deleted | enforcement=active | target=tag | created=2026-08-24T11:17:43.875+10:00
```

So the primary hole this document was asked to propose a fix for **is closed**,
by an active tag ruleset created at 11:17 AEST today. Section 5 Option A is
therefore no longer a proposal; it is a thing to verify and to finish.

**The methodological point is worth more than the finding.** One of the three
briefed commands was:

```
$ gh api repos/PipFoweraker/pdoom1/tags/protection
{"message": "Not Found", ..., "status": "404"}
```

That 404 reproduces exactly. But it is **uninformative about tag protection**.
`/tags/protection` is the *legacy tag-protection-rules* API, a separate and
deprecated system that rulesets superseded; a repository with a fully active
tag ruleset still answers 404 there, which is precisely what this repository is
doing right now. The command was read as evidence of absence when it can only
ever return 404-or-legacy-rules and knows nothing about rulesets.

That is the same failure the CLAIM_AUDIT rule in `CLAUDE.md` names: *"a
published command must be shown capable of returning the other answer."* This
one cannot. It should not be cited again except alongside the rulesets call.

---

## 1. The current state, with the command for each claim

### 1.1 What IS protected

**`main` has real branch protection, and more of it than the brief suggested.**

```
$ gh api repos/PipFoweraker/pdoom1/branches/main/protection
```

Raw answer, reformatted for reading (no fields omitted from the ones below):

| field | value |
|---|---|
| `required_pull_request_reviews.required_approving_review_count` | `1` |
| `required_pull_request_reviews.dismiss_stale_reviews` | `true` |
| `required_pull_request_reviews.require_last_push_approval` | `true` |
| `required_status_checks.contexts` | `GDScript Syntax Check`, `Unit Tests`, `quality-checks` |
| `required_status_checks.strict` | `false` |
| `required_linear_history.enabled` | `true` |
| `allow_force_pushes.enabled` | `false` |
| `allow_deletions.enabled` | `false` |
| `required_conversation_resolution.enabled` | `true` |
| `required_signatures.enabled` | **`false`** |
| `enforce_admins.enabled` | **`false`** |

That is a genuinely well-configured branch. `main` cannot be force-pushed,
cannot be deleted, cannot be merged without one approval and three green
checks, and stale approvals are dismissed. The two `false` rows are the
interesting ones and they are covered in 1.2.

**Release tags are now restricted.**

```
$ gh api repos/PipFoweraker/pdoom1/rulesets/21258734
{"id":21258734,
 "name":"Release tags: v* created by admins only, never moved, never deleted",
 "target":"tag","enforcement":"active",
 "conditions":{"ref_name":{"exclude":[],"include":["refs/tags/v*"]}},
 "rules":[{"type":"creation"},{"type":"deletion"},{"type":"non_fast_forward"}],
 "bypass_actors":[{"actor_id":5,"actor_type":"RepositoryRole","bypass_mode":"always"}],
 "current_user_can_bypass":"always"}
```

Three rules on `refs/tags/v*`: creation blocked, deletion blocked, non-fast-forward
(i.e. moving an existing tag) blocked. One bypass actor, repository role `5`.
GitHub's built-in repository role IDs run read/triage/write/maintain/admin as
1..5, so `5` is Admin -- corroborated by the ruleset's own name, "created by
admins only" [role-ID mapping inferred from GitHub's documented ordering, not
measured; confirm in the ruleset UI, which prints the role name].

**Actions cannot escalate their own token by default.**

```
$ gh api repos/PipFoweraker/pdoom1/actions/permissions/workflow
{"default_workflow_permissions":"read","can_approve_pull_request_reviews":false}
```

Default `GITHUB_TOKEN` is read-only and workflows cannot approve PRs. Each
workflow that needs more asks for it explicitly in a `permissions:` block --
`enhanced-release.yml` declares `contents: write` and `issues: write`, and
nothing else in the tree asks for more than `contents: write` +
`pull-requests: write`.

**No deploy keys.**

```
$ gh api repos/PipFoweraker/pdoom1/keys
[]
```

**There is no `pull_request_target` anywhere.** Covered in full in section 3.

### 1.2 What is NOT protected

**`enforce_admins` is `false`.** From the table above. Every rule in 1.1 --
the review requirement, the status checks, the linear history -- is advisory
for Pip. He can push straight to `main`. This is a deliberate and defensible
choice for a solo maintainer running agent lanes; it is listed here because it
means "protected branch" describes the repo's exposure to *other people*, not
to a mistake or a stolen token of Pip's.

**`required_signatures` is `false`.** Commits on `main` are not required to be
GPG/SSH-signed, so a commit's author line is a claim, not a proof.

**The `Default no-ruin rules` ruleset is disabled and always has been.**

```
$ gh api repos/PipFoweraker/pdoom1/rulesets/7544281
{"id":7544281,"name":"Default no-ruin rules","target":"branch",
 "enforcement":"disabled",
 "conditions":{"ref_name":{"include":["~DEFAULT_BRANCH"]}},
 "rules":[{"type":"deletion"},{"type":"non_fast_forward"}],
 "bypass_actors":[],
 "created_at":"2025-08-20T19:54:01.556+10:00",
 "updated_at":"2025-08-20T19:54:16.724+10:00"}
```

Created and last touched within sixteen seconds of each other in August 2025
and never enforced since. Both of its rules -- no deletion, no non-fast-forward
on the default branch -- are in fact delivered by the branch-protection entry
in 1.1, so **disabling it costs nothing and it protects nothing**. Its only
live effect is on a reader: a ruleset list that shows a confidently-named
"no-ruin" entry reads as protection until you look at the `enforcement` field.
That is the same manufactured-confidence shape as `check_class_cache`'s
`godot --headless --quit` exiting 0 through a total cascade. **Recommendation:
delete it** (section 5), so the ruleset list contains only things that are
true.

**Any `workflow_dispatch` on `enhanced-release.yml` is open to write access.**
The tag ruleset gates *tag creation*. It does not gate the workflow's other
trigger:

```
$ sed -n '3,22p' .github/workflows/enhanced-release.yml
on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:
    inputs:
      version: ...
      prerelease: ...
      skip_validation:
        description: 'Skip validation (emergency only!)'
```

Running a `workflow_dispatch` requires write access to the repository, not
admin. Section 2 works out what that is worth to an attacker, and it is less
than it first looks -- but it is not nothing, and `skip_validation` is sitting
right there in the input list.

**No action is SHA-pinned, and third-party actions are unrestricted.**

```
$ gh api repos/PipFoweraker/pdoom1/actions/permissions
{"enabled":true,"allowed_actions":"all","sha_pinning_required":false}

$ grep -rho "uses: [^ ]*@[0-9a-f]\{40\}" .github/workflows/*.yml | wc -l
0
```

93 `uses:` references across 16 workflows, zero pinned to a commit SHA. Two of
them are outside the `actions/` namespace and both sit in the release path:
`chickensoft-games/setup-godot@v1` (5 uses) and
`softprops/action-gh-release@v1` (1 use, and it is the step that publishes).
`@v1` is a mutable tag: whoever controls that repository controls what runs
inside a job holding `contents: write`.

**Five repository secrets have no consumer in this repo.**

```
$ gh api repos/PipFoweraker/pdoom1/actions/secrets --jq '.secrets[].name'
CROSS_REPO_TOKEN
DH_HOST
DH_PATH
DH_PORT
DH_SSH_KEY
DH_USER
WEBSITE_SYNC_TOKEN

$ grep -rn "DH_" .github/workflows/
(no output)
```

The five `DH_*` secrets -- a DreamHost host, path, port, user and **SSH private
key** -- are referenced by nothing in `.github/workflows/`. They were added
2025-09-14. A secret with no consumer is pure liability: it cannot break
anything by being deleted, and it can be read by any workflow that gains the
ability to read secrets.

### 1.3 Who has push access

```
$ gh api repos/PipFoweraker/pdoom1/collaborators --jq '.[] | "\(.login) | \(.role_name) | admin=\(.permissions.admin) push=\(.permissions.push)"'
PipFoweraker | admin | admin=true push=true
tegabeta | write | admin=false push=true
stevenhobartwork-create | write | admin=false push=true
```

Three collaborators, not one. This did not 403; it is a measured answer.
Two accounts hold `write` and neither holds `admin`. The repository is public
(`"visibility":"public"`, `"private":false`) and is not a fork.

### 1.4 What the release path actually does

`gh api repos/PipFoweraker/pdoom1/actions/workflows/enhanced-release.yml/runs`
shows every release run to date was `event: push`, `actor: PipFoweraker`, on
head_branch `v0.14.2` / `v0.14.1` / `v0.14.0` / `v0.13.2` ... -- i.e. the
tag-push path, always by Pip. No `workflow_dispatch` run has ever been used to
cut a release.

One correction to the brief's framing, because it matters for how a player
reads the page: the releases are **not** published under Pip's personal
account. `gh api repos/PipFoweraker/pdoom1/releases --jq '.[0:3][] | {tag_name,
author: .author.login}'` returns `github-actions[bot]` for v0.14.2, v0.14.1 and
v0.14.0. The author byline is the bot. What carries Pip's name is the
repository, the URL, the project, and the email he sent -- which is the part
that actually does the persuading, so the blast radius in section 2 is
unchanged. It is just not literally his username on the release.

---

## 2. Threat model

No melodrama. This is a solo-maintained indie game with a playtest list, not a
package with ten million weekly downloads. The point of writing the model down
is to size the response, and the honest size is "small, cheap, and worth doing
because the asset being protected is trust, which does not have a rollback."

### 2.1 The actors

**Pip.** Admin. Bypasses the tag ruleset (`current_user_can_bypass: "always"`)
and, with `enforce_admins: false`, bypasses branch protection too. **Nothing in
this repository constrains Pip, or anything acting as Pip.** That includes his
`gh` session on this machine and any agent using it.

**`tegabeta` and `stevenhobartwork-create`.** Write, not admin. Since 11:17
today they can no longer create, move, or delete a `v*` tag. They can still:
open PRs; merge a PR that has one approval and green checks; push directly to
any non-`main` branch; push a tag that does *not* match `v*` (harmless -- the
release workflow only listens on `v*.*.*`); and run `workflow_dispatch` on
`enhanced-release.yml`.

**The public.** Read-only. Can fork and open PRs. On a `pull_request` event
from a fork, GitHub gives the job a read-only `GITHUB_TOKEN` and **withholds
repository secrets**, and this repo has no `pull_request_target` to undo that
(section 3). A fork PR is not a route to the release pipeline.

**Whoever controls `softprops/action-gh-release@v1` and
`chickensoft-games/setup-godot@v1`.** Not Pip. Mutable tags, unpinned, running
in a job that holds `contents: write` and, via `secrets: inherit` on the
`sync-website-version` reusable-workflow call, `CROSS_REPO_TOKEN`. This is the
one actor in the list who is neither a person Pip chose nor a person he can
revoke [general mechanism; no specific compromise of either action is claimed
or was checked -- verify supply-chain advisories yourself before quoting this].

### 2.2 What a compromise buys, per actor

**A stolen `write` collaborator token.** Cannot create a `v*` tag any more.
Can `workflow_dispatch` `enhanced-release.yml`. Two sub-cases, and they differ:

- *With a version input naming a tag that already exists* (`v0.14.2`): the
  workflow builds from that tag's tree and `softprops/action-gh-release` updates
  the existing release -- new assets on a release players already trust. This is
  the live residual hole.
- *With a version input naming a new tag*: `action-gh-release` must create the
  tag, and it acts as `github-actions[bot]`, which holds no repository role and
  is not in the ruleset's bypass list. **Prediction: the tag ruleset blocks it
  and the publish step fails.** [NOT tested -- testing it means pushing a tag,
  which this document is not permitted to do. Pip can confirm cheaply by
  dispatching with a junk version like `v0.0.1-rulesettest` on a quiet day and
  reading whether the Create Release step errors.] If that prediction is right,
  the ruleset also silently broke the emergency `workflow_dispatch` release
  path for everyone including Pip -- worth knowing *before* the night it is
  needed. If it is wrong, this sub-case is a full unrestricted publish path and
  Option B in section 4 stops being optional.

**A stolen admin (Pip) token, or an agent misfiring with his `gh` auth.** Full
publish, no gate, immediately. Also full force-push of `main`. The tag ruleset
does not slow this down by one second. This is, realistically, the dominant
risk in the model: there is far more machinery on this box acting as Pip than
there are third parties with write access.

**A compromised third-party action.** Runs inside the build. Can replace the
binaries with anything before they are hashed -- note the manifest hashes the
artifacts the build produced, so a tampered build produces a manifest that
faithfully attests the tampered file (section 3.2). Can exfiltrate
`CROSS_REPO_TOKEN` from the inherited-secrets job.

### 2.3 Blast radius

The output is Windows, macOS and Linux zips on a public releases page under
`github.com/PipFoweraker/pdoom1`, linked from pdoom1.com, downloaded by people
Pip personally emailed and asked to run. The builds are **unsigned**, so the
existing player instruction is already *"Windows will warn you; click through
it"* -- a population trained, by necessity, to dismiss the one OS-level
warning that would otherwise catch a malicious substitute.

Recovery is asymmetric. Yanking a release takes minutes; the download that
already happened is on the player's disk forever, and the email that vouched
for it was sent by a person, not a bot. The asset at risk is not the code. It
is the sentence "Pip sent me this, it's fine."

Probability of any of this being exercised, over the next twelve months, on a
project of this profile: low. My estimate is under 2% for a targeted attack and
under 5% for an incidental one (dependency compromise, credential leak from an
unrelated breach). The reason to act is not the probability; it is that the
mitigations cost between zero and one evening, and the loss is not the kind you
can patch.

---

## 3. Supply-chain check: `pull_request_target` and untrusted-code-with-secrets

**Asked for explicitly, and the finding is clean. Recording it as such.**

```
$ grep -rn "pull_request_target" .github/
(no output)

$ grep -rn "workflow_run" .github/workflows/
(no output)

$ grep -rn "issue_comment:" .github/workflows/
(no output)
```

Zero occurrences of all three across 16 workflow files. The classic public-repo
hole -- `pull_request_target` checking out `github.event.pull_request.head.sha`
and then running it with secrets in scope -- **is not present in this repo**.

The stronger version of the check is whether any workflow that touches
untrusted code can reach a real secret. Four workflows reference a secret other
than `GITHUB_TOKEN`:

| workflow | secret | trigger |
|---|---|---|
| `release-sync-monitor.yml` | `CROSS_REPO_TOKEN` | `schedule`, `workflow_dispatch` |
| `sync-dev-blog.yml` | `WEBSITE_SYNC_TOKEN` | `push` to `main` (paths), `workflow_dispatch` |
| `sync-documentation.yml` | `CROSS_REPO_TOKEN` | `push` to `main` (paths), `workflow_dispatch` |
| `sync-game-version.yml` | `CROSS_REPO_TOKEN` | `release: [published, edited]`, `workflow_call` |

Not one of them is triggered by `pull_request`. Every trigger in that column is
post-merge or privileged. The seven workflows that *do* run on `pull_request`
(`data-validation`, `dev-blog-automation`, `docs-sync`,
`enhanced-cicd-pipeline`, `godot-tests`, `quality-checks`,
`self-merge-eligibility`) reference no secret beyond `GITHUB_TOKEN`, which for
a fork PR is read-only. **The untrusted-code and the secrets are cleanly
separated.**

One good pattern worth naming so it does not get refactored away: in
`enhanced-release.yml`'s `actions/github-script` step, the user-influenced tag
name is passed as an environment variable and read via `process.env`, with the
reason written next to it --

```
        env:
          # SECURITY: user-influenced (dispatch input / tag name) -- must not
          # be templated into the script text; read via process.env as data
          RELEASE_VERSION: ${{ github.event.inputs.version || github.ref_name }}
```

That is the correct defence against script injection through `${{ }}`
interpolation, and somebody already knew it. The same file does still splice
`${{ github.sha }}`, `${{ github.run_id }}` and `${{ github.repository }}`
directly into `run:` blocks, but those are GitHub-controlled values, not
attacker-controlled, so they are not the same class of problem.

**Residual, minor:** `deploy-feeds` in `enhanced-release.yml` is a stub whose
deployment step is `# TODO: Add your deployment logic here` followed by an
`ls`. It does nothing and holds nothing. Worth deleting or finishing rather
than leaving a job named "Deploy Feeds to Website" that deploys nothing --
manufactured confidence again, same as the disabled ruleset.

---

## 4. The integrity chain that already exists, and is good

There is more of this than the brief credited, and it is well argued in its own
files. This section says what each link proves and -- more usefully -- what it
does not, because two of the links are routinely described as doing a job they
do not do.

### 4.1 Source -> pack: `tools/build_release.py`'s freshness marker

Before each export, `build_release.py` deletes `godot/.godot` and drops a
uniquely-named file `buildstamp<uuid4hex>.gd` into `godot/`. After the export it
streams the `.pck` (descending into the zip for the macOS `.app.zip`) looking
for that filename, via `find_marker()`; a miss is a hard `fail()`. The docstring
explains why the *filename* and not a string literal: GDScript packs as
binary-tokenized `.gdc`, so literals do not survive as grep-able text, but
resource paths survive in the pack file table.

**This proves the pack was built from the current working tree** -- that no
stale `.godot/exported/` cache was served. That is the trap that burned about
twelve cycles in v0.11.0, and it is genuinely solved.

**It is not an integrity control and should never be cited as one.** The token
is generated locally, checked locally, and deleted. It is never published, never
in the manifest, and a tamperer downstream is entirely unaffected by it. It
answers *"did my source reach the pack?"*, never *"did this pack reach the
player unaltered?"*

Since #1069, CI exports route through this same builder
(`scripts/build_all_platforms.py` -> `tools/build_release.py`, one preset at a
time, sequentially; `enhanced-release.yml` names the step "Build all platforms
(via tools/build_release.py, freshness-proven)"). Note that
`docs/design/UPDATER_DESIGN.md` lines 179-182 still describe the pre-#1069 state
("CI builds bypass `build_release.py`'s freshness proof") as current. That is
stale doc, corrected by the code; do not repeat it.

### 4.2 Pack -> zip -> published hash: `release_manifest.json`

`scripts/generate_release_manifest.py` emits a manifest carrying `version`,
`build_date`, `commit_hash`, `ladder_version`, `league_seed`, `assets`,
`data_batch_hash`, `engine`, `validation_passed`, `workflow_run`, and a
`provenance` block of `{repository, ref, actor, event}`. `assets` is a list of
`{name, size, sha256}`, hashed by `sha256_file()` streaming 1 MiB chunks. It is
unit-tested (`tests/test_generate_release_manifest.py`), including a test that
the digest is of file *bytes* rather than of the filename -- a sabotage that was
deliberately tried against the suite.

**What it proves: the zip you hold is byte-for-byte the zip that was uploaded.**
That is exactly what the player-facing notice claims and no more, and the
wording is scrupulous about it:

> A matching hash means the file is byte-for-byte what was published here.

**What it does not prove: who made it.** A hash is a checksum, not a signature.
It detects corruption and in-transit alteration; it cannot distinguish "the
build Pip cut" from "a build somebody else published to this same page", because
in the second case the manifest is regenerated over the substituted zip and
matches perfectly. **The manifest attests whatever was in `build-artifacts/`.**

Three specific limits worth writing down:

- **Coverage is `*.zip` only.** `collect_assets()` does `rglob("*.zip")`. The
  interior `PDoom.exe`, `PDoom.pck` and the `.app` bundle contents are not
  separately hashed; the distribution container is the anchor. Fine as a
  design, but it means once a player extracts the zip, nothing in the release
  can re-verify the extracted files.
- **A hash-free manifest still exits 0.** With no `--assets-dir`,
  `collect_assets()` returns `[]` and `main()` prints
  `"[manifest] WARNING: no assets hashed (no --assets-dir?); manifest carries no
  integrity anchors"` -- a warning, not a failure. This is the one place in an
  otherwise fail-loud tool where the integrity anchor can silently vanish while
  the release publishes green. It is the same shape as the disabled ruleset and
  the stub `deploy-feeds` job: a thing that looks present and is empty. Worth
  turning into a non-zero exit.
- **The `provenance` block is self-asserted metadata inside an unsigned JSON
  file.** It records `actor` faithfully, which makes it useful *forensically* --
  a release published by a stolen token records that account. It is worthless as
  a *control*: anyone who can write the file can write the field.

The separate "Manifest Hash" printed into the release body is echo, not anchor:
there is no independent published source a reader could compare it against.

### 4.3 Publisher identity: the gap, and the tooling already waiting

There is **no signature anywhere in this chain**. Confirmed by search across the
tree: no `SHA256SUMS` sidecar, no `cosign`, no `sigstore`, no SLSA, no
`actions/attest-build-provenance`, no `attestations: write`, no GPG, no
minisign, no public key in the client. `docs/design/UPDATER_DESIGN.md` names the
position precisely and it is the correct name for it:

> **Trust chain today** is rung 2 of the 2026-07-23 ruling: HTTPS to
> github.com plus control of the repo.

So the trust root today is: *TLS to github.com, plus the assumption that only
the right people control the repository.* Every measurement in section 1 is a
measurement of that second clause. **That is why repository settings are a
release-integrity question and not merely a hygiene question** -- with no
signature, repo control is the whole of the chain of custody.

The tooling to close it exists and predates this document by one day.
`tools/sign_release.py` (added in #1282, 2026-08-23) wraps `signtool` with three
rules that each kill a named silent failure: unsigned is *reported* not assumed
fine (`--require` makes it fatal); a signature is re-verified from outside the
signing tool after signing, because `signtool` can exit 0 having produced a
signature that does not verify; and timestamping is mandatory, because an
untimestamped signature silently becomes "unknown publisher" on a date nobody
wrote down. Credentials come from environment variables only, never a repo file.

Two honest corrections to how that tool has been described:

- `docs/release/CODE_SIGNING.md` says it "is tested against its three states."
  **There is no automated test file** -- no `tests/test_sign_release.py`, and
  `grep -rln "sign_release" tests/` is empty. The #1282 commit message is
  accurate where the doc is not: "All three states verified: `--status`,
  unsigned-exit-0, `--require`-exit-1", i.e. hand-run once. Describe it as
  hand-verified.
- **It is wired into nothing.** `grep -rn "sign_release"` matches only inside
  the file itself: not `enhanced-release.yml`, not `build_all_platforms.py`,
  not `build_release.py`, not pre-commit.

`docs/release/CODE_SIGNING.md` (2026-08-23) already contains the purchasing
analysis and it is better than anything this document would reconstruct. Its
conclusions, which section 5 takes as given rather than re-deriving: an OV or IV
Authenticode certificate at **USD 215-260/year**; **EV buys no SmartScreen
bypass any more** (EV and OV have built reputation identically since March 2024,
a belief the doc corrects in public and leaves visible); **Azure Artifact
Signing at USD 9.99/month is closed to us** because it is restricted to US,
Canadian, EU or UK businesses; a **cloud HSM rather than a USB token**, because
a hardware token must be physically present at every signing and therefore CI
cannot sign at all; and the whole Windows+macOS+Steam bundle at roughly USD
415-460, about 12% of the stated AUD 5,000 budget -- *"Money is not the
constraint here; validation lead time and entity choice are."*

And the ceiling, which belongs in any conversation about this and is already
written:

> **None of this proves the game is safe.** ... What signing buys is narrower
> and still worth having: **it proves the binary came from a named, validated
> publisher and has not been altered since.** That is a chain of custody, not a
> safety certificate.

### 4.4 The fourth link, which is unusual and worth keeping

`docs/TRUST.md` is generated by `tools/generate_trust_declaration.py` and gated
by the `trust-declaration-check` pre-commit hook, so it cannot go stale silently
-- the reasoning being that *"a stale trust page is WORSE than none: an absent
declaration is honest, a stale one is a false declaration to exactly the
audience least able to check it."* It enumerates every host, file and process
reach the source makes, with file:line citations, and states its own ceiling
first. It also names precisely the gap this document is about:

> It describes the **source**, not the binary you downloaded. What ties
> those together is the sha256 in each release's `release_manifest.json`
> and, once it exists, the Authenticode signature.

### 4.5 Nothing verifies at download time, and that is deliberate

`godot/autoload/update_check.gd` fetches `release_manifest.json` but reads only
`version`, `ladder_version`, `highlights` and `download_page` -- it never touches
`assets`, `size` or `sha256`, because it never downloads a binary
(`## - Never auto-download. Notice + link; the player decides.`). Its one live
security control is a URL allowlist, not a hash check: `download_page` reaches
`OS.shell_open`, so only `https://github.com/PipFoweraker/pdoom1/` is ever
opened and anything else falls back to a constant. That is the right control
for what it does.

Hash verification is specified for R2 (auto-apply) and not built, per the
2026-07-23 ruling that cryptographic signatures land with auto-execution
because *"auto-execution is when the RCE risk bites"*. So today's chain ends at
a human running `Get-FileHash` by hand, which approximately nobody does.

**Net:** the chain proves *the file was not altered in transit* and *the pack
was built from the tagged source*. It does not prove *who built it*. Closing
that is signing, and signing is blocked on a purchased certificate, not on code.

---

## 5. Options, with honest costs

Ordered by what they defend. Read the "does NOT prevent" rows; they are the
reason none of these is a complete answer on its own.

### Option A -- Tag ruleset restricting creation of `v*`

**Status: ALREADY APPLIED, today at 11:17 AEST.** See section 0. This is no
longer a decision; it is a thing to verify and finish.

- **Money:** zero.
- **Friction for Pip:** zero in the normal path. `current_user_can_bypass` is
  `"always"`; his tag pushes work exactly as before. This is the rare control
  that costs the maintainer nothing.
- **Prevents:** a `write` collaborator, or a stolen `write` token, creating,
  moving or deleting a `v*` tag. Also prevents accidental tag deletion and
  history-rewriting a shipped tag -- which is the quieter win, because a moved
  release tag makes every published hash a lie about a different tree.
- **Does NOT prevent:** anything done as Pip, or by an agent holding his `gh`
  auth -- which section 2.2 argues is the dominant risk here. Does not prevent
  a `workflow_dispatch`-triggered publish. Does not prevent a compromised
  third-party action inside the build.
- **Unfinished business, and it is time-sensitive:** the prediction in 2.2 that
  the ruleset now *blocks* `action-gh-release` from creating a tag that does not
  yet exist, because it publishes as `github-actions[bot]`, which holds no
  repository role and is not a bypass actor. If that is right, the emergency
  `workflow_dispatch` release path is broken and will be discovered on the night
  it is needed. **Untested here on purpose** -- testing it means pushing a tag.
  Section 7.1 gives the cheap check.

### Option B -- A GitHub Environment with required reviewers on `create-github-release`

Create an environment (say `release`), list Pip as a required reviewer, and add
`environment: release` to the `create-github-release` job. A tag push then runs
validation, the three-platform build and the manifest as normal, and **stops**
before publishing, waiting for a human to click Approve.

- **Money:** zero. Deployment protection rules are free on public repositories,
  and this repo is public.
- **Friction:** one approval per release, forever. In wall-clock terms that is
  perhaps 30-60 seconds plus a context switch to a browser and a notification to
  notice. The honest cost is not the click; it is the **new silent-stall failure
  mode**. A run waiting for approval and a run that failed look nearly identical
  from a phone at 23:00 on a league night, and "the release is just sitting
  there" is a category of confusion this repo has paid for before in other
  forms. Add roughly 5-15 minutes to the median hotpatch, and a small but real
  chance of a release that nobody publishes until morning.
- **Prevents:** *any* publication without a human approving -- including via
  `workflow_dispatch`, including from a stolen `write` token, including a
  mistaken agent that pushed a tag. It is the only option here that gates
  **publication** rather than **the trigger**, which is why it survives paths
  Option A does not.
- **Does NOT prevent:** a compromised admin session, which can approve its own
  deployment (see the caveat below). Does not prevent a compromised third-party
  action -- the malicious build has already happened by the time the gate is
  reached, and approving it is approving a binary you have not inspected. Does
  nothing at all for a downloader's ability to verify authenticity.
- **Caveat that decides whether this works for a solo maintainer:** GitHub has a
  "Prevent self-review" option on environments; with it off (the default, as I
  understand it) the person who triggered the run *can* approve it. If that were
  not so, a one-person project could never release. **[VERIFY in the UI before
  relying on it -- if self-approval is blocked, this option is unusable here and
  the variant below is the only form of it worth having.]**

**Variant B2, which I think is strictly better for this project: publish as a
draft.** Set `draft: true` on the `softprops/action-gh-release` step and click
"Publish release" by hand. Same pause, same human decision, and three
advantages: it is a **code change** (so it goes through the branch protection
and review that already exist, rather than being an invisible settings change);
the assets exist and are downloadable-by-Pip before any player can see them, so
the pause is *useful* rather than merely obstructive; and there is no new
environment machinery to forget about.

One real cost of B2: the `verify-release-urls` job (issue #963) checks that
advertised asset URLs answer 200, and a draft release's assets are not publicly
reachable. That guard would need reordering or teaching about drafts, or it will
go red on every release. **[Predicted from the job's stated purpose -- confirm
by reading `verify-release-urls` before committing to B2.]**

### Option C -- Code signing

- **Money:** USD 215-260/year for the Windows certificate, per
  `docs/release/CODE_SIGNING.md`; USD 99/year more if macOS notarization
  follows. Not the binding constraint. **Validation lead time and the choice of
  publisher name are**, and the publisher-name decision compounds: SmartScreen
  reputation does not transfer between identities, so switching from
  `Pip Foweraker` to an entity later costs a year of accrued reputation.
- **Friction:** a signing step in the release job; annual renewal; and -- the
  part that belongs in *this* document specifically -- **a cloud-HSM signing
  credential in GitHub Actions is a new, high-value secret living inside exactly
  the pipeline this document is about.** Signing does not just add a control; it
  raises the payoff of compromising the release workflow, because a compromised
  pipeline would then produce *validly signed* malware. That is an argument for
  doing the cheap pipeline hardening in 5.4 *alongside* signing, not an argument
  against signing.
- **Prevents:** substitution of the binary after it leaves the build -- a
  mirror, a re-upload, a replaced release asset, a file forwarded by a third
  party. And, less obviously but more importantly: it removes the SmartScreen
  warning over time, which **un-trains the click-through habit the current
  notice is forced to teach**. Right now the release body instructs players to
  dismiss the one OS-level warning that would catch a malicious substitute.
  Every release deepens that training. Signing is the only item in this document
  that reverses it, and on this project's cadence -- "23 commits past its last
  tag in two days" -- that compounding matters more than the tamper-detection
  does.
- **Does NOT prevent:** a compromised build producing a correctly-signed
  malicious binary. Signing proves origin, not goodness. Nor does it help
  immediately: OV/IV reputation accrues over releases; there is no instant
  bypass to buy since March 2024.

### 5.4 Cheap extras found while measuring (not in the brief)

These are not really "options"; they are three chores with no downside, and
together they cost less than an hour.

- **Delete the five `DH_*` secrets.** Zero references in any workflow (1.2).
  One of them is an SSH private key. Cost: zero. Prevents: that key being
  readable by any future workflow, or by a compromised action.
- **Delete the `Default no-ruin rules` ruleset.** Disabled since 2025, and both
  its rules are already delivered by branch protection (1.2). Cost: zero.
  Prevents nothing operationally -- it removes a false signal, which is worth
  doing for the same reason `self-merge-eligibility.yml` was written -- its
  header records the precedent: the `class:guard` / `class:docs` labels
  *"promised eligibility and checked nothing -- the same defect that retired
  ship:hotpatch-48h the same day (a label asserting a property no mechanism
  enforces)"*. A disabled ruleset with a reassuring name is that same defect
  wearing a different hat.
- **SHA-pin the two non-`actions/` third-party actions.**
  `softprops/action-gh-release@v1` and `chickensoft-games/setup-godot@v1` are
  mutable tags running in the job that publishes, holding `contents: write`, in
  a call tree that inherits `CROSS_REPO_TOKEN`. Cost: a few minutes now, plus
  remembering to bump (or a Dependabot `github-actions` ecosystem entry, which
  handles it and is itself free). Prevents: a mutable-tag hijack of the one
  actor in section 2.1 that Pip neither chose nor can revoke. Note the tradeoff
  honestly: pinning `@v1` to its current SHA **freezes you on an old major** --
  `action-gh-release` is at v3.0.2 and `setup-godot` at v2.4.1 today, so pinning
  v1 locks in a two-major-versions-behind release publisher. Pinning the current
  v1 SHA is the safe, boring move; upgrading first is better but can only really
  be validated by cutting a release.
- **Make a hash-free manifest fatal.** Section 4.2: with no `--assets-dir` the
  manifest publishes with zero integrity anchors and exits 0. A one-line change
  in `generate_release_manifest.py` (and a test) turns the only silent
  degradation in that tool into a loud one.

---

## 6. Recommendation

**Do 5.4 first, this week.** Three deletions and two pins. They cost nothing,
they add zero recurring friction, and the SHA-pinning is the only item in this
document that addresses the one attacker Pip cannot revoke. Nothing here needs
a decision; it is just work.

**Then verify Option A's side effect (7.1) before you need it.** The tag
ruleset is a good control that arrived free, but it plausibly broke the
emergency `workflow_dispatch` path as a side effect, and the cost of finding
that out on the night of a hotpatch is much larger than the ninety seconds of
checking now.

**Push Option C, and push it on the SmartScreen argument rather than the
tampering argument.** The tampering case is real but low-probability. The
argument that actually justifies USD 260/year is that the current release notice
*has to* teach players to click through the warning, and that training gets
worse with every release at this cadence. `sign_release.py` is written and the
purchasing analysis is done; the remaining work is a purchase, a decision about
the publisher name, and about twenty lines to wire the tool into
`build_all_platforms.py`. If the certificate lands, do the 5.4 pinning first --
signing a pipeline you have not hardened means a compromised pipeline emits
validly signed malware.

**The one I would not bother with is Option B, the environment with required
reviewers.** The reasoning, since it is the one thing here that a reasonable
person would disagree with:

1. It taxes the path that is actually used. All eight releases in this
   repository's history were `event: push`, `actor: PipFoweraker` -- the tag-push
   path, always by Pip. Option B adds a permanent click to every one of them.
2. Its unique coverage over Option A is thin. Option A already stopped the
   `write`-collaborator tag path at zero friction. What is left is the
   `workflow_dispatch` republish, which is narrow and which two much cheaper
   moves also close: deleting the `workflow_dispatch` trigger, or accepting it.
3. **It does not cover the threat that actually dominates the model.** A stolen
   admin session can approve its own deployment, so the gate that costs Pip a
   click every release does not stop the attacker most likely to matter.
4. It introduces a failure mode -- a release sitting unpublished, indistinguishable
   from a failed one -- into the exact scenario (late-night hotpatch) where the
   cost of confusion is highest.

If the "wait, do I really want to publish this" pause is wanted -- and there is
a genuine argument for it against *agent* error rather than attacker action --
take **variant B2, the draft release**. It buys the same pause, it is a reviewed
code change rather than an invisible setting, and the pause is spent doing
something useful (looking at the artifacts) instead of clicking through a
modal. It is also trivially reversible: one line back to `draft: false`.

---

## 7. How to apply each -- NONE OF THESE HAVE BEEN RUN

**Read this line before pasting anything below.** No command in this section was
executed while writing this document. They are written from the API and UI
documentation and from the measured current state in section 1; they have not
been tested against this repository, and several are destructive. Check each one
before running it. Where a command deletes something, the "put it back" form is
given alongside.

### 7.1 Verify Option A's side effect on `workflow_dispatch` (do this first, it is read-mostly)

Look at the ruleset in the UI, which prints the bypass role by name rather than
by the numeric `5` that section 1.1 had to infer:

    https://github.com/PipFoweraker/pdoom1/rules/21258734

To test whether `github-actions[bot]` can still create a tag through
`action-gh-release`, dispatch the release workflow with a throwaway version on a
quiet day and read whether the "Create Release" step errors:

    gh workflow run enhanced-release.yml -R PipFoweraker/pdoom1 -f version=v0.0.1-rulesettest -f prerelease=true

Then watch it, and delete the release and tag afterwards if it succeeded:

    gh run watch -R PipFoweraker/pdoom1
    gh release delete v0.0.1-rulesettest -R PipFoweraker/pdoom1 --yes --cleanup-tag

Note that the deletion itself will be blocked by the ruleset's `deletion` rule
unless run as an admin -- which is a second thing this test usefully proves.
This burns a full three-platform build (about ten minutes of CI), so pick a
moment when nothing else is queued.

If the step fails on tag creation, the fix is to add the GitHub Actions
integration as a bypass actor in the ruleset UI (Rulesets -> the tag ruleset ->
Bypass list -> Add bypass -> Integrations -> GitHub Actions), which restores the
dispatch path while keeping human non-admins blocked.

### 7.2 The cheap extras (5.4)

Delete the five unused secrets:

    gh secret delete DH_HOST  -R PipFoweraker/pdoom1
    gh secret delete DH_PATH  -R PipFoweraker/pdoom1
    gh secret delete DH_PORT  -R PipFoweraker/pdoom1
    gh secret delete DH_SSH_KEY -R PipFoweraker/pdoom1
    gh secret delete DH_USER  -R PipFoweraker/pdoom1

Irreversible: the values are write-only and cannot be read back before deleting.
If any is still wanted, it must be re-created from its original source (a
DreamHost SSH key, which would in any case be better rotated than restored).
Re-check for consumers across the whole estate first, not just this repo --
these were plausibly for a website deploy that lives in `pdoom1-website`:

    gh api repos/PipFoweraker/pdoom1/actions/secrets --jq '.secrets[].name'
    grep -rn "DH_" .github/workflows/

Delete the dead ruleset (verify it is the disabled branch one, then delete):

    gh api repos/PipFoweraker/pdoom1/rulesets/7544281 --jq '{name,target,enforcement}'
    gh api -X DELETE repos/PipFoweraker/pdoom1/rulesets/7544281

Reversible: recreate via Settings -> Rules -> Rulesets -> New ruleset, target
Branch, `~DEFAULT_BRANCH`, rules "Restrict deletions" and "Block force pushes".
Both are already enforced by branch protection, so there is nothing to restore
in practice.

SHA-pin the two third-party actions. The SHAs below were resolved on 2026-08-24
and are the current tips of those `v1` tags; re-resolve before using, since a
tag can move:

    gh api repos/softprops/action-gh-release/commits/v1 --jq .sha
    de2c0eb89ae2a093876385947365aca7b0e5f844

    gh api repos/chickensoft-games/setup-godot/commits/v1 --jq .sha
    1dc3741f474fcf64a3b302d5fdd263010c200866

Then, as a normal PR against `.github/workflows/`:

    uses: softprops/action-gh-release@de2c0eb89ae2a093876385947365aca7b0e5f844  # v1
    uses: chickensoft-games/setup-godot@1dc3741f474fcf64a3b302d5fdd263010c200866  # v1

Keep the trailing `# v1` comment: without it the next reader cannot tell what
version they are on, and Dependabot uses it to write a readable bump PR.
Optionally add `.github/dependabot.yml` with the `github-actions` ecosystem so
the pins get maintained rather than quietly rotting -- pinning without a bump
mechanism trades a hijack risk for a stale-dependency risk, and the whole point
of this repo's anti-rot pattern is not to accept that trade silently.

Make a hash-free manifest fatal -- a code change in
`scripts/generate_release_manifest.py`, in the branch where `collect_assets()`
returned an empty list: turn the existing
`"[manifest] WARNING: no assets hashed ..."` print into a non-zero exit, and add
a case to `tests/test_generate_release_manifest.py`. Normal PR.

### 7.3 Option B -- environment with required reviewers (NOT recommended; see section 6)

UI is the reliable path, because the reviewers field is awkward over the API:

1. Settings -> Environments -> New environment -> name it `release`.
2. Tick **Required reviewers**, add `PipFoweraker`, Save protection rules.
3. Check whether **Prevent self-review** is present and leave it UNTICKED, or
   the sole maintainer cannot approve his own releases.
4. In `.github/workflows/enhanced-release.yml`, add to the
   `create-github-release` job, at the same indentation as `runs-on`:

        environment: release

Step 4 is a normal PR. Steps 1-3 are settings and are Pip's alone.

To reverse: delete the environment (Settings -> Environments -> ... -> Delete)
and revert the one-line workflow change.

The API equivalent of steps 1-2, if preferred -- write the body to a file first
rather than composing it inline, per the house rule about shell heredocs
mangling content:

    gh api -X PUT repos/PipFoweraker/pdoom1/environments/release --input env-release.json

where `env-release.json` contains:

    {"wait_timer": 0,
     "prevent_self_review": false,
     "reviewers": [{"type": "User", "id": 77564415}],
     "deployment_branch_policy": null}

(`77564415` is Pip's user id, from the collaborators call in section 1.3.)

### 7.4 Variant B2 -- draft release (the form of B worth considering)

One line in `.github/workflows/enhanced-release.yml`, in the `Create Release`
step:

    draft: true

Then publish by hand from the releases page. Before merging this, read the
`verify-release-urls` job and decide what happens to it -- a draft release's
assets are not publicly reachable, so that guard likely needs to move after
manual publication or learn to skip on drafts. Normal PR; no settings change;
reverting is the same one line.

### 7.5 Option C -- code signing

No commands here, because the blocker is a purchase and a decision, not a
command. The sequence, per `docs/release/CODE_SIGNING.md`:

1. Decide the publisher name -- `Pip Foweraker` (IV, no entity needed, unblocks
   immediately) versus an entity. This decision is more expensive to defer than
   to make: SmartScreen reputation does not transfer between identities, so a
   later switch discards whatever has accrued.
2. Buy an OV or IV certificate with **cloud HSM** key storage, not a USB token.
   A token cannot sign from a hosted runner at all.
3. Set `PDOOM1_SIGN_SHA1` (or `PDOOM1_SIGN_PFX` / `PDOOM1_SIGN_PFX_PASS`) as
   repository secrets, and wire `tools/sign_release.py --require` into
   `scripts/build_all_platforms.py` after the Windows export and before
   packaging -- so the manifest hashes the *signed* zip, not the unsigned one.
   Getting that order wrong makes every published hash wrong.
4. Write `tests/test_sign_release.py`, so the claim in
   `docs/release/CODE_SIGNING.md` that the tool "is tested against its three
   states" becomes true rather than nearly-true.
5. Do 7.2's SHA-pinning first. See section 5, Option C, on why a signing
   credential raises the value of the pipeline it lives in.

---

## Appendix: every command used to produce this document

Copy-paste as a block; all are read-only.

    gh api repos/PipFoweraker/pdoom1/rulesets
    gh api repos/PipFoweraker/pdoom1/rulesets/7544281
    gh api repos/PipFoweraker/pdoom1/rulesets/21258734
    gh api repos/PipFoweraker/pdoom1/tags/protection
    gh api repos/PipFoweraker/pdoom1/branches/main/protection
    gh api repos/PipFoweraker/pdoom1/collaborators
    gh api repos/PipFoweraker/pdoom1 --jq '{visibility,private,fork,default_branch}'
    gh api repos/PipFoweraker/pdoom1/actions/permissions
    gh api repos/PipFoweraker/pdoom1/actions/permissions/workflow
    gh api repos/PipFoweraker/pdoom1/environments
    gh api repos/PipFoweraker/pdoom1/actions/secrets
    gh api repos/PipFoweraker/pdoom1/keys
    gh api repos/PipFoweraker/pdoom1/releases --jq '.[0:3][] | {tag_name, author: .author.login}'
    gh api "repos/PipFoweraker/pdoom1/actions/workflows/enhanced-release.yml/runs?per_page=5" \
      --jq '.workflow_runs[] | {event, actor: .actor.login, head_branch, conclusion}'
    grep -rn "pull_request_target" .github/
    grep -rn "workflow_run" .github/workflows/
    grep -rn "issue_comment:" .github/workflows/
    grep -rn "secrets\." .github/workflows/
    grep -rn "DH_" .github/workflows/
    grep -rho "uses: [^ ]*@[0-9a-f]\{40\}" .github/workflows/*.yml | wc -l

Anything in this document not reachable from one of those, or from a named file
path, is marked with a bracketed hedge. There are five such hedges: the
repository-role ID mapping (1.1), the two `action-gh-release` behavioural
predictions (2.2 and 5, Option B2's `verify-release-urls` interaction), the
GitHub self-review default (5, Option B), and the general third-party-action
compromise mechanism (2.1), which is a mechanism and not a claim about either
named action.
