# pdoom1 -- spoken rulings, weekend of 2026-08-01/02

**07:30** | Sun 2026-08-02 | memo `pdoom1/2026-08-02/0730` | supersedes: none

## Front page

Pip worked a printed backlog on Sunday morning and recorded responses to five pdoom1 packs. Everything below is his ruling, transcribed on-device and extracted. **Not yet re-read by him** -- verify item labels against the original cards before acting, since ASR does not reliably distinguish A3/A8 style codes.

The decisions are settled and can be actioned immediately. The Saturday playtest (capture `2026-08-01_100453`, 12:43) is a large body of new design observation that mostly needs issues raised rather than answers given; it is section 5 and is the longest part.

**The asks, crisply:** ship the alpha-tools wording as ruled (section 2); adopt the release manifest as the seed publication surface with `weekly-2026-w31` as canonical format (section 3); raise the four missing infrastructure issues plus a cross-repo sync issue (section 3); build the month-review changes A1-A10 and B1-B5 with A6 deferred (section 4); produce mockups for three settings directions today, deferring the diegetic one until a designer is hired (section 4); and work section 5 into issues.

**Two standing requests that change how packs should be written.** First, ministerial-briefing format: a single front page carrying summary, key facts and the exact asks as one-line yes/no items, with the reasoning behind it. His words -- *"if the asks are at the front and I have the context, I can answer them and move on."* Second, **higher information density**: denser text, more paragraphs, fewer bullets and splitting mechanisms. *"I'm okay reading pretty dense blocks of text if that is the most effective way to deliver the information."* A slight preference, not an override.

---

## 1. Postmortem findings -- all agreed

Capture `2026-08-02_065031`. Pip agrees with the one-sentence version and with findings 1 through 11 without exception. Two annotations. On the morning playtest being "of a different game": he believes he switched to crisis mode on instinct at the start and that this was probably not correct, but holds that the assessment stands and *"the severity is the direction of the error -- it doesn't fail to prove the build was good, it appeared to prove it."* He explicitly endorses the sharper framing that the failure was the gap between a proxy and the thing itself: where proxies for truth can detach from truth, that gap is the risk. He also agrees the ceremony earned its keep despite being improvised, and is glad it was recorded.

Outstanding issue work he wants confirmed or raised: `#1060` is done; `#1062`, `#1063`, `#1064`, `#1065`, `#1066`, `#1061`, `#1057` remain. **Four things still need issues raised**: the macOS framework, `enhanced-release.yml`, `build_release.py`, and the unversioned Linux alias. Separately, an issue is needed spanning pdoom1 and pdoom1-website to work out the sync workflow, gating the dead steps to `workflow_dispatch`, plus updates to the ritual sheets.

## 2. Alpha tools -- ruled, with wording changes

Capture `2026-08-02_065316`, relating to `#1079`. The name **alpha tools** is agreed, as is the ruling and the observation that the mechanism already exists in the codebase.

Wording changes he wants: drop the two dashes so the toggle reads simply **alpha tools**. Extend the explanation beyond "using any of these takes the run off the leaderboard permanently" to cover what they are *for* -- changing how the game works, seeing how the game works, diagnosing whether something is broken, getting out of a trap, or otherwise messing about. At game over, change the wording to **"play without them to get your play on the board."** The first-use wording is agreed as drafted.

Card answers: name **alpha tools** [x]; effect on board **unranked and warned** [x] (recommended); sticky **yes, one-way per run** [x]; colour **reuse the not-ranked amber** [x] (recommended).

One naming note: he can remove sandbox mode as a scenario pack -- possibly renaming it something like *the good timeline*. Since scenarios are paused, he wants naming reconsidered generally, because "sandbox" may be a term wanted elsewhere.

## 3. Seed publication and format -- ruled

Capture `2026-08-02_065031`, decision card one. **Ask 1A: option B -- the release manifest.** He notes the manifest JSON is already an asset carrying featured seed plus ladder epoch, and that his written question of whether this is a downside or a control mechanism resolves as "mostly fine". He agrees the manifest's machine-readable formatting should be uplifted.

**Ask 1B: the canonical seed string is `weekly-2026-w31`** -- the game's current form. He additionally wants a short piece of thinking on **what the protocol is if the seed string format ever changes**: if new features require additional information in the string, how that folds into the ceremonies, using what was learned this week to anticipate the failure mode before it arrives.

Card two, what happens to a board when the seed rolls: **2A yes on both** -- archive as knowledge history (recommended) and publish past boards as history. He accepts building B now and holding it ready for when there is real season history. **2B** was, in his words, an accidentally written card, decided along with 2A; the three W30 entries are covered by that.

## 4. Month review and settings menus -- decision cards

Capture `2026-08-02_070454`, month review options from the 2026-08-01 playtest: **A1 yes, A2 yes, A3 yes, A6 deferred, A7 yes, A8 yes, A9 yes, A10 yes, B1 yes, B2 yes, B3 yes, B4 yes, B5 yes.** A6 is *"an uplift where I'm willing to put in the effort, but not now"* -- push it. B5 is a yes he wants validated by playing it, ideally as an A/B or a few iterations experienced as a player rather than decided on paper. He notes he has said yes to a great many things and expects pushback on effort: *"those are the decisions."*

Capture `2026-08-02_070851`, settings menu five directions. **Direction 1, operations board -- fine. Direction 2, diegetic -- capture the thinking but do not build it now**; he judges it the direction that suffers most from being done badly, and wants it done properly, likely a day or more of work, ideally after a designer is hired. **Direction 5, the first five minutes -- he likes this a lot.**

The substantive new idea: **put the common early settings on the escape/pause screen itself**, not behind escape-then-settings. His reasoning is that the first thing most players do is disable hints, change colour, and change music volume, so those should be both surfaced and made cheap to reach. He calls it a great pickup.

Given that, he wants **mockups today of three directions -- protocol tabs, config terminal, and operations board** -- asset-generated if needed, at good fidelity. Then **at least one round of iteration, probably two**, producing roughly nine options to narrow from. He is explicit that he intends to be deliberately iterative about art assets *"rather than just accepting the first acceptable copy of a wave that is presented to me."*

## 5. Saturday playtest -- new observations

Capture `2026-08-01_100453`, 12:43, played on the shipped build. Grouped by what they need.

**Defects.** The hiring screen conflates two currencies: it states a cost of *3 attention* while the money figure reads *3000 dollars*, and the Q and W option layouts are both poor. He calls this the first bug of the run. Minimising and restoring the window produces behaviour he flags as *"probably not expected"* -- worth reproducing. The player guide still reads badly, which is `#1073`.

**Confirmed fixed or good.** The version badge now reads v0.13.2 with no stray dev-build text. The feed no longer draws over the feed text. Achievement toasts appear top-right and work.

**Month review screen.** Unspent reserve evaporates with no banking, which he is happy with as a rule but not as a presentation -- the screen tells him a number he already knows rather than a story. What he wants instead is narrative: at the start of the month you planned to spend seventeen of twenty attention; these things came up requiring this much; you made this many trade-offs and this many sacrifices. The doom summary is good content but pops up blocking the screen. He asks for **ten ways to make the month review screen better**, proposed back to him for decision.

**Rivals.** They appeared for the first time with no introduction. His framing is a player-experience question rather than a bug: how does the player learn they have rivals, how did the game introduce the concept, and how do they know what rivals are doing? He believes the summary predates workshop 3 and needs rework as a UI-and-narrative piece, and thinks it can be cracked quickly.

**Planning screen layout.** The *begin planning* button is poor -- he asks for **five ways to make it better**. `Q` works as the key; spacebar might also serve; **not enter**, which should stay reserved for commit so nobody triggers it accidentally. The header text *"plan strategy, layout the month, commit the month"* is tutorial content: teach it once in the introduction, then it is wasted space. Reclaim that space to make the attention bar and its dots **twice as large**. The *watch* button needs stronger visual differentiation from its background, and so does *plan* on the loading screen. Research quality -- rushed, standard, thorough -- **does not belong in this UI at all**; he believes a decision was already made to set it at idea or research-project level rather than globally, and wants it moved to wherever the philosophically coherent version of the game puts it.

**Onboarding and staff.** If a hire is fast-tracked, onboarding reminders must surface: the player has to consciously choose whether and how each new staff member is onboarded, and **it must not default to silently not happening** -- at least once, they must make the choice. He wants this expressed as story rather than dialog: staff arriving through a door for the first time, which implies spawning a door and some arrival logic. He judges it an easy pickup.

**Art and events.** Installing a security system should visibly add security cameras to the lab. Generalising: **sweep every in-game event for references to assets, and use that sweep to generate another fifty to a hundred assets.** He also wants a large art review session scheduled -- he has spent money on generation and not yet seen the outputs, and thinks packaging that could ship quickly.

**Audio.** Change the default music away from the current opening theme -- he finds it too intense -- toward the slower, gentler theme heard in the settings menu or the end-game. Set **default volume to about 15%**. He wants another pass with the music tooling scheduled, and the intro reworked; blasting a new player with loud intense music is, in his judgement, off-putting.

**Settings menus generally.** *"It's not breaking but it's pretty amateur, and it seems like a pretty quick pickup."* He wants agents spun up to produce **five different sets of UI options for the settings menus**, presented for selection: *"I'm not actually constrained by effort here, I'm constrained by choice."* The mode he is asking for is a film director reviewing what a creative department brings -- flooded with options, saying yes, no, more of this.

**Process, not game.** He wants a correctness-and-contrast pass up and down the ADRs and DQs, expecting it to force out what the next steps are. He feels internal pressure to have a verbalised plan for the whole game, because newcomers cannot infer direction from the current state. The lever he wants is **an actively developed roadmap** functioning as the pre-FAQ: when someone says a thing is bad, the answer becomes *"it's on the roadmap"* plus a surprisingly detailed roadmap, eventually linked to Jira items so people can see when things are coming. He states plainly that solving the buttons-and-UI problem *"one hundred percent has to be part of the postmortem."*

Finally, on the office floor: he cannot perceive the floor-depth change and would need a side-by-side. He suggests reviving the UI preview or simulator tool to make such comparisons cheap, and has added it to his own postmortem list.
